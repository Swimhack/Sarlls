# Data Model: PCB Manufacturing Readiness

**Feature**: PCB device status management and manufacturing file preparation
**Date**: 2025-09-23

## Core Entities

### Device
**Purpose**: Represents a PCB/hardware device being prepared for manufacturing

```typescript
interface Device {
  id: string;                    // UUID primary key
  name: string;                  // User-friendly device name
  description?: string;          // Optional device description
  version: string;               // Semantic version (1.0.0, 1.1.0, etc.)
  status: DeviceStatus;          // Current manufacturing status
  board_dimensions?: {           // Extracted from Gerber files
    width: number;               // mm
    height: number;              // mm
    thickness: number;           // mm
  };
  layer_count?: number;          // PCB layer count
  component_count?: number;      // Total components from BOM
  created_by: string;            // User ID (foreign key)
  organization_id: string;       // Organization ID (foreign key)
  created_at: timestamp;
  updated_at: timestamp;
}
```

### DeviceStatus
**Purpose**: Enumerated status values with validation rules

```typescript
enum DeviceStatus {
  DRAFT = 'draft',               // Initial creation, files can be modified
  REVIEW = 'review',             // Ready for team review
  READY_FOR_MANUFACTURING = 'ready_for_manufacturing',  // All files validated
  SUBMITTED = 'submitted',       // Sent to manufacturer
  IN_PRODUCTION = 'in_production',  // Manufacturing in progress
  COMPLETED = 'completed',       // Manufacturing finished
  CANCELLED = 'cancelled'        // Project cancelled
}
```

**Status Transition Rules**:
- `DRAFT` → `REVIEW` (when all required files uploaded)
- `REVIEW` → `READY_FOR_MANUFACTURING` (after validation passes)
- `REVIEW` → `DRAFT` (if changes needed)
- `READY_FOR_MANUFACTURING` → `SUBMITTED` (when sent to manufacturer)
- `SUBMITTED` → `IN_PRODUCTION` (manufacturer confirms start)
- `IN_PRODUCTION` → `COMPLETED` (manufacturing finished)
- Any status → `CANCELLED` (project termination)

### DeviceFile
**Purpose**: Tracks individual files associated with a device

```typescript
interface DeviceFile {
  id: string;                    // UUID primary key
  device_id: string;             // Foreign key to Device
  file_name: string;             // Original filename
  file_type: FileType;           // Categorized file type
  file_size: number;             // Bytes
  file_path: string;             // Supabase Storage path
  content_hash: string;          // SHA-256 for deduplication
  metadata?: FileMetadata;       // Extracted file-specific data
  uploaded_by: string;           // User ID
  uploaded_at: timestamp;
  version: number;               // File version (incremental)
}
```

### FileType
**Purpose**: Categorizes manufacturing files by purpose

```typescript
enum FileType {
  GERBER_ZIP = 'gerber_zip',     // Complete Gerber package
  BOM_CSV = 'bom_csv',           // Bill of Materials
  CPL_CSV = 'cpl_csv',           // Component Placement List
  SCHEMATIC_PDF = 'schematic_pdf',  // Schematic documentation
  TECHNICAL_SPEC = 'technical_spec', // Technical specifications
  ASSEMBLY_DRAWING = 'assembly_drawing', // Assembly instructions
  TEST_PROCEDURE = 'test_procedure',     // Testing documentation
  OTHER = 'other'                // Miscellaneous files
}
```

### FileMetadata
**Purpose**: Type-specific metadata extracted from files

```typescript
interface FileMetadata {
  // For Gerber ZIP files
  gerber?: {
    layer_count: number;
    board_outline: boolean;       // Has board outline layer
    drill_files: number;          // Number of drill files
    fabrication_notes?: string;
  };

  // For BOM CSV files
  bom?: {
    component_count: number;
    unique_parts: number;
    estimated_cost?: number;      // USD
    missing_parts: string[];      // Parts without availability
  };

  // For CPL CSV files
  cpl?: {
    placement_count: number;
    top_side_components: number;
    bottom_side_components: number;
    rotation_format: string;      // degrees or radians
  };
}
```

### StatusHistory
**Purpose**: Audit trail for device status changes

```typescript
interface StatusHistory {
  id: string;                    // UUID primary key
  device_id: string;             // Foreign key to Device
  previous_status: DeviceStatus;
  new_status: DeviceStatus;
  changed_by: string;            // User ID
  changed_at: timestamp;
  notes?: string;                // Optional change reason
  metadata?: {                   // Status-specific data
    manufacturer_id?: string;    // When status = SUBMITTED
    quote_id?: string;           // Manufacturing quote reference
    delivery_date?: string;      // Expected completion
  };
}
```

### ManufacturingPackage
**Purpose**: Generated packages for manufacturer submission

```typescript
interface ManufacturingPackage {
  id: string;                    // UUID primary key
  device_id: string;             // Foreign key to Device
  package_name: string;          // Generated package filename
  package_path: string;          // Supabase Storage path
  file_count: number;            // Number of files included
  total_size: number;            // Total package size in bytes
  checksum: string;              // Package integrity check
  generated_by: string;          // User ID
  generated_at: timestamp;
  expiry_date?: timestamp;       // For temporary manufacturer access
}
```

### Manufacturer
**Purpose**: External manufacturing partners

```typescript
interface Manufacturer {
  id: string;                    // UUID primary key
  name: string;                  // Company name
  contact_email: string;
  contact_phone?: string;
  website?: string;
  capabilities: string[];        // e.g., ["2-layer", "4-layer", "SMT", "THT"]
  lead_time_days: number;        // Typical lead time
  quality_rating?: number;       // 1-5 star rating
  notes?: string;
  added_by: string;              // User ID
  organization_id: string;       // Organization scope
  created_at: timestamp;
  updated_at: timestamp;
}
```

## Relationships

### Primary Relationships
- **Device** ↔ **DeviceFile** (1:many) - A device has multiple files
- **Device** ↔ **StatusHistory** (1:many) - A device has status change history
- **Device** ↔ **ManufacturingPackage** (1:many) - A device can have multiple packages
- **Device** → **User** (many:1) - A device is created by a user
- **Device** → **Organization** (many:1) - A device belongs to an organization

### Secondary Relationships
- **StatusHistory** → **User** (many:1) - Status changes are made by users
- **DeviceFile** → **User** (many:1) - Files are uploaded by users
- **ManufacturingPackage** → **User** (many:1) - Packages are generated by users
- **Manufacturer** → **Organization** (many:1) - Manufacturers are scoped to organizations

## Validation Rules

### Device Validation
- **Name**: Required, 1-100 characters, unique within organization
- **Version**: Required, semantic version format (x.y.z)
- **Status**: Must follow valid transition rules
- **Board dimensions**: If present, all values > 0
- **Layer count**: If present, 1-32 layers
- **Component count**: If present, >= 0

### File Validation
- **File size**: Maximum 200MB per file
- **File types**: Must match allowed extensions per FileType
- **Gerber ZIP**: Must contain minimum required layers
- **BOM CSV**: Must have required columns (RefDes, Value, Package)
- **CPL CSV**: Must have required columns (RefDes, X, Y, Rotation)

### Status Transition Validation
- **DRAFT → REVIEW**: Must have at least Gerber + BOM files
- **REVIEW → READY**: All files must pass validation
- **READY → SUBMITTED**: Manufacturing package must be generated
- **Backwards transitions**: Only allowed before SUBMITTED status

## Database Schema (Supabase)

### Table Structure
```sql
-- Extends existing user/organization tables
CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  description TEXT,
  version VARCHAR(20) NOT NULL,
  status device_status NOT NULL DEFAULT 'draft',
  board_dimensions JSONB,
  layer_count INTEGER,
  component_count INTEGER,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(name, organization_id)
);

CREATE TYPE device_status AS ENUM (
  'draft', 'review', 'ready_for_manufacturing',
  'submitted', 'in_production', 'completed', 'cancelled'
);

CREATE TYPE file_type AS ENUM (
  'gerber_zip', 'bom_csv', 'cpl_csv', 'schematic_pdf',
  'technical_spec', 'assembly_drawing', 'test_procedure', 'other'
);

-- Additional tables follow similar pattern...
```

### Row Level Security (RLS)
```sql
-- Device access control
CREATE POLICY "Users can view devices in their organization" ON devices
  FOR SELECT USING (organization_id IN (
    SELECT organization_id FROM user_organizations WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can create devices in their organization" ON devices
  FOR INSERT WITH CHECK (
    organization_id IN (
      SELECT organization_id FROM user_organizations WHERE user_id = auth.uid()
    ) AND created_by = auth.uid()
  );

-- File access control follows similar pattern...
```

## Integration Points

### Existing Schema Integration
- Uses existing `auth.users` table for user references
- Uses existing `organizations` table for data isolation
- Uses existing `user_organizations` junction table for permissions
- Follows existing RLS policy patterns

### Storage Integration
- Files stored in Supabase Storage bucket: `pcb-files`
- Organized by device: `pcb-files/{organization_id}/{device_id}/{version}/`
- Manufacturing packages: `pcb-packages/{organization_id}/{device_id}/`
- Public URLs with signed access for manufacturer sharing

This data model provides the foundation for all PCB manufacturing workflow requirements while integrating seamlessly with the existing contract comparison application.