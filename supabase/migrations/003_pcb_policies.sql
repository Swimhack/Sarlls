-- Row Level Security Policies for PCB Manufacturing
-- Created: 2025-09-23
-- Feature: PCB Manufacturing Readiness

-- Enable RLS on all PCB tables
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE manufacturing_packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE manufacturers ENABLE ROW LEVEL SECURITY;

-- Devices table policies
-- Assuming organizations table exists and user_organizations junction table exists
-- Users can view devices in their organization
CREATE POLICY "Users can view devices in their organization" ON devices
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Users can create devices in their organization
CREATE POLICY "Users can create devices in their organization" ON devices
  FOR INSERT WITH CHECK (
    organization_id IN (
      SELECT organization_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    ) AND created_by = auth.uid()
  );

-- Users can update devices in their organization
CREATE POLICY "Users can update devices in their organization" ON devices
  FOR UPDATE USING (
    organization_id IN (
      SELECT organization_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Users can delete devices in their organization (only if status allows)
CREATE POLICY "Users can delete devices in their organization" ON devices
  FOR DELETE USING (
    organization_id IN (
      SELECT organization_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    ) AND status IN ('draft', 'cancelled')
  );

-- Device files table policies
-- Users can view files for devices in their organization
CREATE POLICY "Users can view device files in their organization" ON device_files
  FOR SELECT USING (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    )
  );

-- Users can upload files to devices in their organization
CREATE POLICY "Users can upload files to devices in their organization" ON device_files
  FOR INSERT WITH CHECK (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    ) AND uploaded_by = auth.uid()
  );

-- Users can update file metadata for devices in their organization
CREATE POLICY "Users can update device files in their organization" ON device_files
  FOR UPDATE USING (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    )
  );

-- Users can delete files from devices in their organization (only if device status allows)
CREATE POLICY "Users can delete device files in their organization" ON device_files
  FOR DELETE USING (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      ) AND status IN ('draft', 'review')
    )
  );

-- Status history table policies
-- Users can view status history for devices in their organization
CREATE POLICY "Users can view status history in their organization" ON status_history
  FOR SELECT USING (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    )
  );

-- Status history entries are created automatically via triggers
-- Users can insert manual status history entries
CREATE POLICY "Users can create status history entries" ON status_history
  FOR INSERT WITH CHECK (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    ) AND changed_by = auth.uid()
  );

-- Manufacturing packages table policies
-- Users can view packages for devices in their organization
CREATE POLICY "Users can view manufacturing packages in their organization" ON manufacturing_packages
  FOR SELECT USING (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    )
  );

-- Users can create packages for devices in their organization
CREATE POLICY "Users can create manufacturing packages in their organization" ON manufacturing_packages
  FOR INSERT WITH CHECK (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    ) AND generated_by = auth.uid()
  );

-- Users can update package metadata in their organization
CREATE POLICY "Users can update manufacturing packages in their organization" ON manufacturing_packages
  FOR UPDATE USING (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    )
  );

-- Users can delete packages from devices in their organization
CREATE POLICY "Users can delete manufacturing packages in their organization" ON manufacturing_packages
  FOR DELETE USING (
    device_id IN (
      SELECT id FROM devices
      WHERE organization_id IN (
        SELECT organization_id
        FROM user_organizations
        WHERE user_id = auth.uid()
      )
    )
  );

-- Manufacturers table policies
-- Users can view manufacturers in their organization
CREATE POLICY "Users can view manufacturers in their organization" ON manufacturers
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Users can create manufacturers in their organization
CREATE POLICY "Users can create manufacturers in their organization" ON manufacturers
  FOR INSERT WITH CHECK (
    organization_id IN (
      SELECT organization_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    ) AND added_by = auth.uid()
  );

-- Users can update manufacturers in their organization
CREATE POLICY "Users can update manufacturers in their organization" ON manufacturers
  FOR UPDATE USING (
    organization_id IN (
      SELECT organization_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Users can delete manufacturers in their organization
CREATE POLICY "Users can delete manufacturers in their organization" ON manufacturers
  FOR DELETE USING (
    organization_id IN (
      SELECT organization_id
      FROM user_organizations
      WHERE user_id = auth.uid()
    )
  );

-- Public policies for temporary manufacturer access
-- (These would be used for sharing manufacturing packages with external manufacturers)

-- Function to check if a manufacturing package is publicly accessible (not expired)
CREATE OR REPLACE FUNCTION is_package_publicly_accessible(package_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM manufacturing_packages
    WHERE id = package_id
    AND (expiry_date IS NULL OR expiry_date > NOW())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Policy for public package downloads (for external manufacturers)
CREATE POLICY "Public access to non-expired manufacturing packages" ON manufacturing_packages
  FOR SELECT USING (
    is_package_publicly_accessible(id)
  );

-- Comments for documentation
COMMENT ON POLICY "Users can view devices in their organization" ON devices IS
  'Users can view devices that belong to organizations they are members of';

COMMENT ON POLICY "Users can view device files in their organization" ON device_files IS
  'Users can view files for devices in their organization only';

COMMENT ON POLICY "Users can delete device files in their organization" ON device_files IS
  'Users can only delete files if the device is in draft or review status';

COMMENT ON POLICY "Public access to non-expired manufacturing packages" ON manufacturing_packages IS
  'Allows external manufacturers to download packages before expiry date';

COMMENT ON FUNCTION is_package_publicly_accessible(UUID) IS
  'Checks if a manufacturing package can be accessed by external users (not expired)';