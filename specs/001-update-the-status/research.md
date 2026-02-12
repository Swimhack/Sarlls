# Research: PCB Manufacturing Readiness

**Feature**: PCB device status management and manufacturing file preparation
**Date**: 2025-09-23

## Technology Stack Decisions

### File Storage & Management
**Decision**: Supabase Storage with organized bucket structure
**Rationale**:
- Already integrated in existing application
- Provides secure file access with RLS policies
- Supports large file uploads (required for Gerber ZIP files)
- Built-in versioning capabilities
**Alternatives considered**:
- AWS S3 (requires new integration)
- Local file system (not scalable)
- Google Drive API (less secure)

### PCB File Format Support
**Decision**: Support multiple formats with ZIP packaging
**Rationale**:
- Industry standard: Gerber files (RS-274X) with drill files
- Component data: BOM (CSV), CPL (CSV) for pick-and-place
- Documentation: PDF technical specifications
- Packaging: ZIP files for manufacturer submission
**Alternatives considered**:
- Single format only (limits manufacturer compatibility)
- Direct CAD file support (complex, format-specific)

### Status Management System
**Decision**: Enum-based status with validation rules
**Rationale**:
- Clear workflow states: Draft → Review → Ready → Submitted → In Production → Complete
- Validation prevents invalid transitions (e.g., skip Review phase)
- Audit trail for status changes
**Alternatives considered**:
- Free-text status (error-prone)
- Boolean flags (not scalable)
- External workflow engine (over-engineering)

### Database Schema Strategy
**Decision**: Extend existing Supabase schema with PCB-specific tables
**Rationale**:
- Leverage existing user/organization structure
- RLS policies maintain data isolation
- Consistent with contract comparison patterns
**Alternatives considered**:
- Separate database (complexity)
- NoSQL approach (less structured)

## Integration Patterns

### Authentication & Authorization
**Decision**: Use existing Supabase Auth with role-based permissions
**Rationale**:
- Hardware engineers need full device management access
- Project managers need status update permissions
- External manufacturers need read-only access to submitted files
**Implementation**: Extend existing RLS policies for PCB tables

### File Upload Workflow
**Decision**: Multi-step upload with validation
**Rationale**:
- Step 1: Validate file types and sizes
- Step 2: Extract metadata (layer count, board dimensions)
- Step 3: Generate thumbnails/previews where possible
- Step 4: Store with organized naming convention
**Pattern**: Similar to existing contract upload flow

### Version Control Strategy
**Decision**: Semantic versioning for device specifications
**Rationale**:
- Major.Minor.Patch format (1.0.0, 1.1.0, 2.0.0)
- Major: Breaking changes requiring new manufacturing setup
- Minor: Component updates, layout improvements
- Patch: Documentation fixes, metadata updates

## Performance Considerations

### Large File Handling
**Decision**: Chunked uploads with progress tracking
**Rationale**:
- Gerber ZIP files can be 50-100MB+
- Component libraries add significant size
- User experience requires progress feedback
**Implementation**: Use Supabase resumable uploads

### Metadata Extraction
**Decision**: Server-side processing with background jobs
**Rationale**:
- ZIP file analysis can be CPU intensive
- Board dimension calculation requires geometry processing
- Component counting for BOM validation
**Pattern**: Similar to contract analysis pipeline

## Security & Compliance

### File Access Control
**Decision**: Signed URLs with time-limited access
**Rationale**:
- Manufacturers need temporary access to files
- Internal teams need permanent access
- Version control prevents unauthorized modifications
**Implementation**: Supabase Storage policies with JWT tokens

### Data Retention
**Decision**: Configurable retention with legal hold
**Rationale**:
- Manufacturing files may be needed for years (warranty, compliance)
- Legal requirements vary by industry/geography
- Cost optimization for old versions
**Implementation**: Lifecycle policies with archive tiers

## API Design Patterns

### REST Endpoints
**Decision**: RESTful API following existing patterns
**Rationale**:
- Consistent with contract comparison endpoints
- Easy integration with frontend components
- Standard HTTP status codes and error handling

**Endpoints planned**:
- `GET /api/devices` - List devices
- `POST /api/devices` - Create device
- `PUT /api/devices/{id}/status` - Update status
- `GET /api/devices/{id}/files` - List device files
- `POST /api/devices/{id}/files` - Upload files
- `GET /api/devices/{id}/manufacturing-package` - Generate submission package

### Real-time Updates
**Decision**: Supabase real-time subscriptions for status changes
**Rationale**:
- Teams need immediate status notifications
- Progress tracking during file uploads
- Collaborative editing scenarios
**Implementation**: WebSocket subscriptions on device status table

## Testing Strategy

### File Processing Tests
**Decision**: Mock file system with sample PCB files
**Rationale**:
- Test file validation logic
- Verify metadata extraction
- Ensure proper error handling
**Test data**: Sample Gerber, BOM, CPL files for different board types

### Integration Tests
**Decision**: End-to-end workflow testing
**Rationale**:
- Complete device creation to manufacturing submission flow
- Status transition validation
- File packaging verification
**Tools**: Cypress for browser automation, Jest for API testing

## Research Summary

All technical unknowns resolved with decisions that extend existing application patterns:
- ✅ File storage strategy defined
- ✅ PCB format support clarified
- ✅ Status management approach established
- ✅ Integration patterns identified
- ✅ Performance considerations addressed
- ✅ Security model defined

**Ready for Phase 1**: Design data model and API contracts