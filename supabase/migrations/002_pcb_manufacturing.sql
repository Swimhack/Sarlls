-- PCB Manufacturing Tables Migration
-- Created: 2025-09-23
-- Feature: PCB Manufacturing Readiness

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE device_status AS ENUM (
  'draft',
  'review',
  'ready_for_manufacturing',
  'submitted',
  'in_production',
  'completed',
  'cancelled'
);

CREATE TYPE file_type AS ENUM (
  'gerber_zip',
  'bom_csv',
  'cpl_csv',
  'schematic_pdf',
  'technical_spec',
  'assembly_drawing',
  'test_procedure',
  'other'
);

-- Devices table
CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  description TEXT,
  version VARCHAR(20) NOT NULL,
  status device_status NOT NULL DEFAULT 'draft',
  board_dimensions JSONB,
  layer_count INTEGER CHECK (layer_count > 0 AND layer_count <= 32),
  component_count INTEGER CHECK (component_count >= 0),
  created_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID NOT NULL, -- References organizations table (assumed to exist)
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Constraints
  CONSTRAINT devices_name_org_unique UNIQUE (name, organization_id),
  CONSTRAINT devices_version_format CHECK (version ~ '^\d+\.\d+\.\d+$')
);

-- Device files table
CREATE TABLE device_files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  file_name VARCHAR(255) NOT NULL,
  file_type file_type NOT NULL,
  file_size BIGINT NOT NULL CHECK (file_size > 0),
  file_path TEXT NOT NULL, -- Supabase Storage path
  content_hash VARCHAR(64) NOT NULL, -- SHA-256 hash
  metadata JSONB,
  uploaded_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),

  -- Constraints
  CONSTRAINT device_files_unique_name_version UNIQUE (device_id, file_name, version)
);

-- Status history for audit trail
CREATE TABLE status_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  previous_status device_status,
  new_status device_status NOT NULL,
  changed_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  notes TEXT,
  metadata JSONB
);

-- Manufacturing packages
CREATE TABLE manufacturing_packages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  package_name VARCHAR(255) NOT NULL,
  package_path TEXT NOT NULL, -- Supabase Storage path
  file_count INTEGER NOT NULL CHECK (file_count > 0),
  total_size BIGINT NOT NULL CHECK (total_size > 0),
  checksum VARCHAR(64) NOT NULL, -- Package integrity check
  generated_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expiry_date TIMESTAMP WITH TIME ZONE
);

-- Manufacturers table (for future enhancement)
CREATE TABLE manufacturers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  contact_email VARCHAR(255) NOT NULL,
  contact_phone VARCHAR(50),
  website TEXT,
  capabilities TEXT[], -- Array of capabilities
  lead_time_days INTEGER CHECK (lead_time_days > 0),
  quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
  notes TEXT,
  added_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID NOT NULL, -- References organizations table
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Constraints
  CONSTRAINT manufacturers_name_org_unique UNIQUE (name, organization_id)
);

-- Indexes for performance
CREATE INDEX idx_devices_organization_id ON devices(organization_id);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_created_by ON devices(created_by);
CREATE INDEX idx_devices_created_at ON devices(created_at DESC);

CREATE INDEX idx_device_files_device_id ON device_files(device_id);
CREATE INDEX idx_device_files_type ON device_files(file_type);
CREATE INDEX idx_device_files_uploaded_at ON device_files(uploaded_at DESC);

CREATE INDEX idx_status_history_device_id ON status_history(device_id);
CREATE INDEX idx_status_history_changed_at ON status_history(changed_at DESC);

CREATE INDEX idx_manufacturing_packages_device_id ON manufacturing_packages(device_id);
CREATE INDEX idx_manufacturing_packages_generated_at ON manufacturing_packages(generated_at DESC);

CREATE INDEX idx_manufacturers_organization_id ON manufacturers(organization_id);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_devices_updated_at
  BEFORE UPDATE ON devices
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_manufacturers_updated_at
  BEFORE UPDATE ON manufacturers
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically create status history entries
CREATE OR REPLACE FUNCTION create_status_history()
RETURNS TRIGGER AS $$
BEGIN
  -- Only create history entry if status actually changed
  IF OLD.status IS DISTINCT FROM NEW.status THEN
    INSERT INTO status_history (
      device_id,
      previous_status,
      new_status,
      changed_by,
      notes
    ) VALUES (
      NEW.id,
      OLD.status,
      NEW.status,
      NEW.created_by, -- This would need to be updated to track actual user making change
      'Status updated automatically'
    );
  END IF;

  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER device_status_history_trigger
  AFTER UPDATE ON devices
  FOR EACH ROW
  EXECUTE FUNCTION create_status_history();

-- Comments for documentation
COMMENT ON TABLE devices IS 'PCB devices being prepared for manufacturing';
COMMENT ON TABLE device_files IS 'Files associated with PCB devices (Gerber, BOM, CPL, etc.)';
COMMENT ON TABLE status_history IS 'Audit trail for device status changes';
COMMENT ON TABLE manufacturing_packages IS 'Generated packages for manufacturer submission';
COMMENT ON TABLE manufacturers IS 'Manufacturing partners and their capabilities';

COMMENT ON COLUMN devices.board_dimensions IS 'JSON object with width, height, thickness in mm';
COMMENT ON COLUMN devices.layer_count IS 'Number of PCB layers (1-32)';
COMMENT ON COLUMN devices.component_count IS 'Total number of components from BOM';
COMMENT ON COLUMN device_files.metadata IS 'File-specific metadata (layer count, component count, etc.)';
COMMENT ON COLUMN device_files.content_hash IS 'SHA-256 hash for file integrity and deduplication';
COMMENT ON COLUMN manufacturing_packages.checksum IS 'Checksum for package integrity verification';