-- Supabase Storage Setup for PCB Files
-- Created: 2025-09-23
-- Feature: PCB Manufacturing Readiness

-- Create storage bucket for PCB files
INSERT INTO storage.buckets (id, name, public)
VALUES ('pcb-files', 'pcb-files', false);

-- Create storage bucket for manufacturing packages
INSERT INTO storage.buckets (id, name, public)
VALUES ('pcb-packages', 'pcb-packages', false);

-- Storage policies for PCB files bucket

-- Policy: Users can view files for devices in their organization
CREATE POLICY "Users can view PCB files in their organization" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'pcb-files' AND
    auth.uid() IS NOT NULL AND
    -- Extract organization_id from path: organization_id/device_id/filename
    (storage.foldername(name))[1]::uuid IN (
      SELECT organization_id::text
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Policy: Users can upload files to devices in their organization
CREATE POLICY "Users can upload PCB files to their organization devices" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'pcb-files' AND
    auth.uid() IS NOT NULL AND
    -- Extract organization_id from path: organization_id/device_id/filename
    (storage.foldername(name))[1]::uuid IN (
      SELECT organization_id::text
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Policy: Users can update files for devices in their organization
CREATE POLICY "Users can update PCB files in their organization" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'pcb-files' AND
    auth.uid() IS NOT NULL AND
    -- Extract organization_id from path
    (storage.foldername(name))[1]::uuid IN (
      SELECT organization_id::text
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Policy: Users can delete files from devices in their organization (only if device allows)
CREATE POLICY "Users can delete PCB files in their organization" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'pcb-files' AND
    auth.uid() IS NOT NULL AND
    -- Extract device_id from path and check device status
    (storage.foldername(name))[2]::uuid IN (
      SELECT d.id
      FROM devices d
      JOIN user_organizations uo ON d.organization_id = uo.organization_id
      WHERE uo.user_id = auth.uid()
      AND d.status IN ('draft', 'review')
    )
  );

-- Storage policies for manufacturing packages bucket

-- Policy: Users can view packages for devices in their organization
CREATE POLICY "Users can view manufacturing packages in their organization" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'pcb-packages' AND (
      -- Authenticated users in the organization
      (auth.uid() IS NOT NULL AND
       (storage.foldername(name))[1]::uuid IN (
         SELECT organization_id::text
         FROM user_organizations
         WHERE user_id = auth.uid()
       )) OR
      -- Public access for non-expired packages (external manufacturers)
      (name IN (
        SELECT package_path
        FROM manufacturing_packages
        WHERE expiry_date IS NULL OR expiry_date > NOW()
      ))
    )
  );

-- Policy: Users can upload packages for devices in their organization
CREATE POLICY "Users can upload manufacturing packages to their organization" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'pcb-packages' AND
    auth.uid() IS NOT NULL AND
    -- Extract organization_id from path: organization_id/device_id/package_name
    (storage.foldername(name))[1]::uuid IN (
      SELECT organization_id::text
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Policy: Users can update packages for devices in their organization
CREATE POLICY "Users can update manufacturing packages in their organization" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'pcb-packages' AND
    auth.uid() IS NOT NULL AND
    -- Extract organization_id from path
    (storage.foldername(name))[1]::uuid IN (
      SELECT organization_id::text
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Policy: Users can delete packages from devices in their organization
CREATE POLICY "Users can delete manufacturing packages in their organization" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'pcb-packages' AND
    auth.uid() IS NOT NULL AND
    -- Extract organization_id from path
    (storage.foldername(name))[1]::uuid IN (
      SELECT organization_id::text
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Helper function to generate storage paths
CREATE OR REPLACE FUNCTION generate_pcb_file_path(
  org_id UUID,
  device_id UUID,
  filename TEXT,
  version INTEGER DEFAULT 1
)
RETURNS TEXT AS $$
BEGIN
  RETURN org_id::text || '/' || device_id::text || '/v' || version::text || '/' || filename;
END;
$$ LANGUAGE plpgsql;

-- Helper function to generate package paths
CREATE OR REPLACE FUNCTION generate_package_path(
  org_id UUID,
  device_id UUID,
  package_name TEXT
)
RETURNS TEXT AS $$
BEGIN
  RETURN org_id::text || '/' || device_id::text || '/packages/' || package_name || '.zip';
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup expired packages
CREATE OR REPLACE FUNCTION cleanup_expired_packages()
RETURNS INTEGER AS $$
DECLARE
  expired_count INTEGER := 0;
  expired_package RECORD;
BEGIN
  -- Find expired packages
  FOR expired_package IN
    SELECT id, package_path
    FROM manufacturing_packages
    WHERE expiry_date IS NOT NULL AND expiry_date < NOW()
  LOOP
    -- Delete from storage
    DELETE FROM storage.objects
    WHERE bucket_id = 'pcb-packages' AND name = expired_package.package_path;

    -- Delete from database
    DELETE FROM manufacturing_packages WHERE id = expired_package.id;

    expired_count := expired_count + 1;
  END LOOP;

  RETURN expired_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to calculate storage usage for an organization
CREATE OR REPLACE FUNCTION get_organization_storage_usage(org_id UUID)
RETURNS TABLE(
  total_files BIGINT,
  total_size BIGINT,
  pcb_files_count BIGINT,
  pcb_files_size BIGINT,
  packages_count BIGINT,
  packages_size BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COALESCE(pcb.file_count, 0) + COALESCE(pkg.package_count, 0) as total_files,
    COALESCE(pcb.total_size, 0) + COALESCE(pkg.total_size, 0) as total_size,
    COALESCE(pcb.file_count, 0) as pcb_files_count,
    COALESCE(pcb.total_size, 0) as pcb_files_size,
    COALESCE(pkg.package_count, 0) as packages_count,
    COALESCE(pkg.total_size, 0) as packages_size
  FROM (
    -- PCB files stats
    SELECT
      COUNT(*) as file_count,
      SUM(file_size) as total_size
    FROM device_files df
    JOIN devices d ON df.device_id = d.id
    WHERE d.organization_id = org_id
  ) pcb
  CROSS JOIN (
    -- Package stats
    SELECT
      COUNT(*) as package_count,
      SUM(total_size) as total_size
    FROM manufacturing_packages mp
    JOIN devices d ON mp.device_id = d.id
    WHERE d.organization_id = org_id
  ) pkg;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically delete storage objects when device files are deleted
CREATE OR REPLACE FUNCTION delete_device_file_storage()
RETURNS TRIGGER AS $$
BEGIN
  -- Delete the file from storage
  DELETE FROM storage.objects
  WHERE bucket_id = 'pcb-files' AND name = OLD.file_path;

  RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER delete_device_file_storage_trigger
  AFTER DELETE ON device_files
  FOR EACH ROW
  EXECUTE FUNCTION delete_device_file_storage();

-- Trigger to automatically delete storage objects when packages are deleted
CREATE OR REPLACE FUNCTION delete_package_storage()
RETURNS TRIGGER AS $$
BEGIN
  -- Delete the package from storage
  DELETE FROM storage.objects
  WHERE bucket_id = 'pcb-packages' AND name = OLD.package_path;

  RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER delete_package_storage_trigger
  AFTER DELETE ON manufacturing_packages
  FOR EACH ROW
  EXECUTE FUNCTION delete_package_storage();

-- Comments for documentation
COMMENT ON FUNCTION generate_pcb_file_path(UUID, UUID, TEXT, INTEGER) IS
  'Generates standardized storage path for PCB files: org_id/device_id/v{version}/filename';

COMMENT ON FUNCTION generate_package_path(UUID, UUID, TEXT) IS
  'Generates standardized storage path for manufacturing packages: org_id/device_id/packages/package_name.zip';

COMMENT ON FUNCTION cleanup_expired_packages() IS
  'Removes expired manufacturing packages from both storage and database';

COMMENT ON FUNCTION get_organization_storage_usage(UUID) IS
  'Returns storage usage statistics for an organization';

-- Example storage paths:
-- PCB files: pcb-files/550e8400-e29b-41d4-a716-446655440000/123e4567-e89b-12d3-a456-426614174000/v1/gerber_files.zip
-- Packages: pcb-packages/550e8400-e29b-41d4-a716-446655440000/123e4567-e89b-12d3-a456-426614174000/packages/ESP32_SmartSwitch_v2_Manufacturing.zip