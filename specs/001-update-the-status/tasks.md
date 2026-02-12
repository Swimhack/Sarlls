# Tasks: PCB Manufacturing Readiness

**Input**: Design documents from `/specs/001-update-the-status/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Found: Next.js 14, TypeScript, Supabase stack
   → Extract: Web application structure, existing auth integration
2. Load optional design documents:
   → data-model.md: Device, DeviceFile, StatusHistory, ManufacturingPackage entities
   → contracts/: devices-api.yaml with 8 endpoint groups
   → research.md: File storage, status management, performance decisions
   → quickstart.md: 13 integration test scenarios
3. Generate tasks by category:
   → Setup: Database schema, Supabase policies
   → Tests: Contract tests for 8 endpoint groups, 13 integration scenarios
   → Core: 4 TypeScript models, 6 service modules, 8 API routes
   → Integration: File upload, real-time updates, package generation
   → Polish: Unit tests, performance optimization, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel execution
   → Same file/route = sequential (no [P])
   → Tests before implementation (TDD approach)
5. Number tasks sequentially (T001-T042)
6. Generate dependency graph and parallel execution examples
7. Validate task completeness: ✅ All contracts tested, entities modeled, endpoints implemented
8. Return: SUCCESS (42 tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web app structure**: Next.js App Router with `app/` directory
- **API routes**: `app/api/` for server endpoints
- **Components**: `app/components/` for React UI
- **Database**: `lib/database/` for Supabase schema and operations
- **Tests**: `__tests__/` for contract and integration tests

## Phase 3.1: Setup
- [x] T001 Create database migration for PCB tables in `supabase/migrations/002_pcb_manufacturing.sql`
- [x] T002 Create Supabase RLS policies for PCB tables in `supabase/migrations/003_pcb_policies.sql`
- [x] T003 [P] Configure TypeScript types for PCB entities in `lib/types/pcb.ts`
- [x] T004 [P] Set up Supabase Storage bucket and policies for PCB files in `supabase/migrations/004_pcb_storage.sql`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API Endpoints)
- [x] T005 [P] Contract test GET /api/devices in `__tests__/contract/devices-list.test.ts`
- [x] T006 [P] Contract test POST /api/devices in `__tests__/contract/devices-create.test.ts`
- [x] T007 [P] Contract test GET /api/devices/[id] in `__tests__/contract/devices-get.test.ts`
- [x] T008 [P] Contract test PUT /api/devices/[id] in `__tests__/contract/devices-update.test.ts`
- [x] T009 [P] Contract test PUT /api/devices/[id]/status in `__tests__/contract/device-status.test.ts`
- [x] T010 [P] Contract test GET/POST /api/devices/[id]/files in `__tests__/contract/device-files.test.ts`
- [x] T011 [P] Contract test POST /api/devices/[id]/manufacturing-package in `__tests__/contract/manufacturing-package.test.ts`
- [x] T012 [P] Contract test GET /api/devices/[id]/history in `__tests__/contract/device-history.test.ts`

### Integration Tests (User Scenarios)
- [ ] T013 [P] Integration test: Create new device workflow in `__tests__/integration/create-device.test.ts`
- [ ] T014 [P] Integration test: File upload and validation in `__tests__/integration/file-upload.test.ts`
- [ ] T015 [P] Integration test: Status progression workflow in `__tests__/integration/status-workflow.test.ts`
- [ ] T016 [P] Integration test: Manufacturing package generation in `__tests__/integration/package-generation.test.ts`
- [ ] T017 [P] Integration test: File version management in `__tests__/integration/file-versioning.test.ts`
- [ ] T018 [P] Integration test: Manufacturer sharing workflow in `__tests__/integration/manufacturer-sharing.test.ts`
- [ ] T019 [P] Integration test: Error handling and validation in `__tests__/integration/error-handling.test.ts`
- [ ] T020 [P] Integration test: Permission and access control in `__tests__/integration/access-control.test.ts`

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Database Models and Types
- [ ] T021 [P] Device model with status validation in `lib/database/models/device.ts`
- [ ] T022 [P] DeviceFile model with metadata handling in `lib/database/models/device-file.ts`
- [ ] T023 [P] StatusHistory model for audit trail in `lib/database/models/status-history.ts`
- [ ] T024 [P] ManufacturingPackage model in `lib/database/models/manufacturing-package.ts`

### Service Layer
- [ ] T025 [P] DeviceService with CRUD operations in `lib/services/device-service.ts`
- [ ] T026 [P] FileUploadService with validation in `lib/services/file-upload-service.ts`
- [ ] T027 [P] StatusValidationService for workflow rules in `lib/services/status-validation-service.ts`
- [ ] T028 [P] PackageGenerationService for ZIP creation in `lib/services/package-generation-service.ts`
- [ ] T029 [P] FileProcessingService for metadata extraction in `lib/services/file-processing-service.ts`
- [ ] T030 [P] NotificationService for real-time updates in `lib/services/notification-service.ts`

### API Endpoints
- [ ] T031 GET/POST /api/devices endpoint with pagination in `app/api/devices/route.ts`
- [ ] T032 GET/PUT/DELETE /api/devices/[id] endpoint in `app/api/devices/[id]/route.ts`
- [ ] T033 PUT /api/devices/[id]/status endpoint with validation in `app/api/devices/[id]/status/route.ts`
- [ ] T034 GET/POST /api/devices/[id]/files endpoints in `app/api/devices/[id]/files/route.ts`
- [ ] T035 GET/DELETE /api/devices/[id]/files/[fileId] endpoints in `app/api/devices/[id]/files/[fileId]/route.ts`
- [ ] T036 POST /api/devices/[id]/manufacturing-package endpoint in `app/api/devices/[id]/manufacturing-package/route.ts`
- [ ] T037 GET /api/devices/[id]/history endpoint in `app/api/devices/[id]/history/route.ts`

## Phase 3.4: Integration

### UI Components
- [ ] T038 [P] DeviceList component with status filtering in `app/components/devices/device-list.tsx`
- [ ] T039 [P] DeviceForm component for create/edit in `app/components/devices/device-form.tsx`
- [ ] T040 [P] FileUpload component with drag-and-drop in `app/components/devices/file-upload.tsx`
- [ ] T041 [P] StatusWorkflow component with transition validation in `app/components/devices/status-workflow.tsx`
- [ ] T042 [P] ManufacturingPackage component for generation/download in `app/components/devices/manufacturing-package.tsx`

### Pages and Navigation
- [ ] T043 Devices list page at `app/devices/page.tsx`
- [ ] T044 Device detail page at `app/devices/[id]/page.tsx`
- [ ] T045 Add navigation links to existing layout in `app/layout.tsx`

## Phase 3.5: Polish
- [ ] T046 [P] Unit tests for status validation logic in `__tests__/unit/status-validation.test.ts`
- [ ] T047 [P] Unit tests for file processing utilities in `__tests__/unit/file-processing.test.ts`
- [ ] T048 [P] Performance tests for large file uploads in `__tests__/performance/file-upload.test.ts`
- [ ] T049 [P] Performance tests for package generation in `__tests__/performance/package-generation.test.ts`
- [ ] T050 [P] Update API documentation in `docs/api/pcb-manufacturing.md`
- [ ] T051 Add user documentation for PCB workflow in `docs/user-guide/pcb-manufacturing.md`
- [ ] T052 Run complete quickstart validation scenarios
- [ ] T053 Code review and refactoring cleanup

## Dependencies
- Setup (T001-T004) before all other phases
- Contract tests (T005-T012) before any API implementation (T031-T037)
- Integration tests (T013-T020) before UI components (T038-T042)
- Models (T021-T024) before services (T025-T030)
- Services (T025-T030) before API endpoints (T031-T037)
- API endpoints (T031-T037) before UI components (T038-T042)
- Core implementation before polish (T046-T053)

### Specific Dependencies
- T021 (Device model) blocks T025 (DeviceService), T031 (devices API)
- T022 (DeviceFile model) blocks T026 (FileUploadService), T034 (files API)
- T025 (DeviceService) blocks T031, T032 (device APIs)
- T026 (FileUploadService) blocks T034, T035 (file APIs)
- T027 (StatusValidationService) blocks T033 (status API)
- T028 (PackageGenerationService) blocks T036 (package API)
- T031-T037 (APIs) block T038-T045 (UI components and pages)

## Parallel Execution Examples

### Contract Tests (Run Together)
```bash
# Launch T005-T012 in parallel:
Task: "Contract test GET /api/devices in __tests__/contract/devices-list.test.ts"
Task: "Contract test POST /api/devices in __tests__/contract/devices-create.test.ts"
Task: "Contract test GET /api/devices/[id] in __tests__/contract/devices-get.test.ts"
Task: "Contract test PUT /api/devices/[id] in __tests__/contract/devices-update.test.ts"
Task: "Contract test PUT /api/devices/[id]/status in __tests__/contract/device-status.test.ts"
Task: "Contract test GET/POST /api/devices/[id]/files in __tests__/contract/device-files.test.ts"
Task: "Contract test POST /api/devices/[id]/manufacturing-package in __tests__/contract/manufacturing-package.test.ts"
Task: "Contract test GET /api/devices/[id]/history in __tests__/contract/device-history.test.ts"
```

### Integration Tests (Run Together)
```bash
# Launch T013-T020 in parallel:
Task: "Integration test: Create new device workflow in __tests__/integration/create-device.test.ts"
Task: "Integration test: File upload and validation in __tests__/integration/file-upload.test.ts"
Task: "Integration test: Status progression workflow in __tests__/integration/status-workflow.test.ts"
Task: "Integration test: Manufacturing package generation in __tests__/integration/package-generation.test.ts"
Task: "Integration test: File version management in __tests__/integration/file-versioning.test.ts"
Task: "Integration test: Manufacturer sharing workflow in __tests__/integration/manufacturer-sharing.test.ts"
Task: "Integration test: Error handling and validation in __tests__/integration/error-handling.test.ts"
Task: "Integration test: Permission and access control in __tests__/integration/access-control.test.ts"
```

### Models (Run Together)
```bash
# Launch T021-T024 in parallel:
Task: "Device model with status validation in lib/database/models/device.ts"
Task: "DeviceFile model with metadata handling in lib/database/models/device-file.ts"
Task: "StatusHistory model for audit trail in lib/database/models/status-history.ts"
Task: "ManufacturingPackage model in lib/database/models/manufacturing-package.ts"
```

### Services (Run Together)
```bash
# Launch T025-T030 in parallel:
Task: "DeviceService with CRUD operations in lib/services/device-service.ts"
Task: "FileUploadService with validation in lib/services/file-upload-service.ts"
Task: "StatusValidationService for workflow rules in lib/services/status-validation-service.ts"
Task: "PackageGenerationService for ZIP creation in lib/services/package-generation-service.ts"
Task: "FileProcessingService for metadata extraction in lib/services/file-processing-service.ts"
Task: "NotificationService for real-time updates in lib/services/notification-service.ts"
```

### UI Components (Run Together)
```bash
# Launch T038-T042 in parallel:
Task: "DeviceList component with status filtering in app/components/devices/device-list.tsx"
Task: "DeviceForm component for create/edit in app/components/devices/device-form.tsx"
Task: "FileUpload component with drag-and-drop in app/components/devices/file-upload.tsx"
Task: "StatusWorkflow component with transition validation in app/components/devices/status-workflow.tsx"
Task: "ManufacturingPackage component for generation/download in app/components/devices/manufacturing-package.tsx"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing (TDD requirement)
- Commit after each task completion
- API endpoints are sequential (same route files)
- UI components can run in parallel (different files)
- All file paths are relative to repository root

## Task Generation Rules Applied

1. **From Contracts** (devices-api.yaml):
   - 8 endpoint groups → 8 contract test tasks (T005-T012) [P]
   - 8 endpoint groups → 7 implementation tasks (T031-T037) (sequential due to shared route files)

2. **From Data Model**:
   - 4 entities → 4 model creation tasks (T021-T024) [P]
   - Entity relationships → 6 service layer tasks (T025-T030) [P]

3. **From User Stories** (quickstart.md):
   - 8 test scenarios → 8 integration test tasks (T013-T020) [P]
   - UI requirements → 5 component tasks (T038-T042) [P]

4. **Ordering Applied**:
   - Setup (T001-T004) → Tests (T005-T020) → Models (T021-T024) → Services (T025-T030) → APIs (T031-T037) → UI (T038-T045) → Polish (T046-T053)
   - Dependencies prevent invalid parallel execution

## Validation Checklist
- ✅ All contracts have corresponding tests (T005-T012 cover all 8 endpoint groups)
- ✅ All entities have model tasks (T021-T024 cover Device, DeviceFile, StatusHistory, ManufacturingPackage)
- ✅ All tests come before implementation (T005-T020 before T021-T053)
- ✅ Parallel tasks truly independent (different files, no shared dependencies)
- ✅ Each task specifies exact file path
- ✅ No task modifies same file as another [P] task (API routes are sequential, components are parallel)

**Total Tasks**: 53 tasks covering complete PCB Manufacturing Readiness implementation
**Parallel Groups**: 6 groups with 38 parallelizable tasks
**Estimated Timeline**: 2-3 weeks with parallel execution capabilities