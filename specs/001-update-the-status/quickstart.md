# Quickstart: PCB Manufacturing Readiness

**Feature**: PCB device status management and manufacturing file preparation
**Date**: 2025-09-23
**Purpose**: End-to-end integration test scenarios for validating the PCB manufacturing workflow

## Prerequisites

### Required Setup
- ✅ Next.js application running locally
- ✅ Supabase database with PCB schema migrated
- ✅ Supabase Storage bucket `pcb-files` configured
- ✅ Test user authenticated with organization access
- ✅ Sample PCB files available for upload

### Test Data
```
test-files/
├── sample-gerber.zip        # Valid Gerber package
├── sample-bom.csv          # Valid Bill of Materials
├── sample-cpl.csv          # Valid Component Placement List
├── sample-schematic.pdf    # Technical documentation
├── invalid-file.txt        # Invalid file for error testing
└── oversized-file.zip      # >200MB file for size limit testing
```

## Core User Journey Tests

### Test 1: Create New Device
**Goal**: Verify device creation and initial status

**Steps**:
1. Navigate to `/devices` page
2. Click "Create New Device" button
3. Fill form:
   - Name: "ESP32 Smart Switch v2"
   - Description: "Updated IoT switch with WiFi connectivity"
   - Version: "2.0.0"
4. Click "Create Device"

**Expected Results**:
- ✅ Device created with status `DRAFT`
- ✅ Redirect to device detail page `/devices/{id}`
- ✅ Device appears in devices list
- ✅ Status history shows initial creation entry
- ✅ Files section shows empty state with upload prompt

**Test Data**:
```json
{
  "name": "ESP32 Smart Switch v2",
  "description": "Updated IoT switch with WiFi connectivity",
  "version": "2.0.0"
}
```

### Test 2: Upload Required Files
**Goal**: Verify file upload and validation

**Steps**:
1. On device detail page, click "Upload Files"
2. Upload `sample-gerber.zip` as type `gerber_zip`
3. Upload `sample-bom.csv` as type `bom_csv`
4. Upload `sample-cpl.csv` as type `cpl_csv`
5. Upload `sample-schematic.pdf` as type `schematic_pdf`

**Expected Results**:
- ✅ All files upload successfully with progress indicators
- ✅ File metadata extracted and displayed
- ✅ Total file count and size updated
- ✅ Files appear in device files list with correct types
- ✅ Device validation status updates (ready for review)

**Validation Checks**:
- Gerber ZIP contains required layers
- BOM has valid component data
- CPL has valid placement coordinates
- File sizes within limits

### Test 3: Status Progression Workflow
**Goal**: Verify status transitions and validation

**Steps**:
1. From `DRAFT` status, click "Submit for Review"
2. Verify status changes to `REVIEW`
3. Click "Approve for Manufacturing"
4. Verify status changes to `READY_FOR_MANUFACTURING`
5. Generate manufacturing package
6. Update status to `SUBMITTED`

**Expected Results**:
- ✅ Each status transition validates requirements
- ✅ Status history tracks all changes with timestamps
- ✅ UI updates to reflect current status
- ✅ Available actions change based on status
- ✅ Validation prevents invalid transitions

**Status Flow Validation**:
```
DRAFT → REVIEW (requires files)
REVIEW → READY_FOR_MANUFACTURING (requires approval)
READY_FOR_MANUFACTURING → SUBMITTED (requires package)
```

### Test 4: Manufacturing Package Generation
**Goal**: Verify package creation and download

**Steps**:
1. With device in `READY_FOR_MANUFACTURING` status
2. Click "Generate Manufacturing Package"
3. Configure package options:
   - Include all file types
   - Set 7-day expiry
   - Name: "ESP32_SmartSwitch_v2_Manufacturing"
4. Generate package
5. Download generated ZIP file

**Expected Results**:
- ✅ Package generation succeeds
- ✅ ZIP contains all uploaded files
- ✅ Package metadata stored correctly
- ✅ Download URL works and requires authentication
- ✅ Package includes manufacturing checklist
- ✅ File integrity verified with checksums

**Package Contents Validation**:
```
ESP32_SmartSwitch_v2_Manufacturing.zip
├── Gerber/
│   └── [extracted gerber files]
├── BOM/
│   └── ESP32_IoT_Switch_BOM.csv
├── Assembly/
│   └── ESP32_IoT_Switch_CPL.csv
├── Documentation/
│   └── sample-schematic.pdf
└── MANUFACTURING_README.txt
```

### Test 5: File Version Management
**Goal**: Verify file versioning and updates

**Steps**:
1. Upload new version of BOM file
2. Verify version increment
3. Download previous version
4. Update device version to "2.1.0"
5. Generate new package with updated version

**Expected Results**:
- ✅ File version increments automatically
- ✅ Previous versions remain accessible
- ✅ Device version updates correctly
- ✅ New package reflects updated version
- ✅ Version history maintained

### Test 6: Manufacturer Sharing Workflow
**Goal**: Verify external manufacturer access

**Steps**:
1. Generate manufacturing package with 24-hour expiry
2. Copy shareable download link
3. Access link in incognito browser (unauthenticated)
4. Verify package downloads without login
5. Wait for expiry and verify link becomes invalid

**Expected Results**:
- ✅ Temporary download URL generated
- ✅ Unauthenticated download works within expiry
- ✅ Link expires correctly after time limit
- ✅ Expired links return 410 Gone status
- ✅ Download includes manufacturer instructions

## Error Handling Tests

### Test 7: File Upload Validation
**Goal**: Verify error handling for invalid files

**Steps**:
1. Attempt to upload `invalid-file.txt` as `gerber_zip`
2. Attempt to upload `oversized-file.zip` (>200MB)
3. Upload BOM with missing required columns
4. Upload Gerber ZIP with no layer files

**Expected Results**:
- ✅ Invalid file type rejected with clear error
- ✅ Oversized file rejected with size limit message
- ✅ Invalid BOM structure detected and rejected
- ✅ Incomplete Gerber package validation fails
- ✅ User gets actionable error messages

### Test 8: Status Transition Validation
**Goal**: Verify invalid status changes are prevented

**Steps**:
1. Try to change from `DRAFT` to `READY_FOR_MANUFACTURING` (skip review)
2. Try to change from `SUBMITTED` back to `DRAFT`
3. Try to delete device in `IN_PRODUCTION` status
4. Try to upload files when status is `SUBMITTED`

**Expected Results**:
- ✅ Invalid status transitions blocked
- ✅ Clear error messages explain requirements
- ✅ Deletion prevented for active manufacturing
- ✅ File modifications blocked after submission

### Test 9: Permission and Access Control
**Goal**: Verify security and access controls

**Steps**:
1. Create device in Organization A
2. Switch to user from Organization B
3. Attempt to access Organization A's device
4. Attempt to download Organization A's files

**Expected Results**:
- ✅ Cross-organization access denied (404/403)
- ✅ File downloads respect organization boundaries
- ✅ Device lists filtered by organization
- ✅ Manufacturing packages not accessible across orgs

## Performance Tests

### Test 10: Large File Upload
**Goal**: Verify performance with realistic file sizes

**Steps**:
1. Upload 50MB Gerber ZIP file
2. Monitor upload progress
3. Verify metadata extraction completes
4. Generate package with large files

**Expected Results**:
- ✅ Upload completes within 30 seconds
- ✅ Progress indicator shows accurate progress
- ✅ Metadata extraction completes within 10 seconds
- ✅ Package generation completes within 15 seconds

### Test 11: Concurrent Operations
**Goal**: Verify system handles multiple simultaneous users

**Steps**:
1. Multiple users upload files simultaneously
2. Multiple package generations in parallel
3. Concurrent status updates on different devices

**Expected Results**:
- ✅ No file corruption or conflicts
- ✅ All operations complete successfully
- ✅ Database consistency maintained
- ✅ Response times remain reasonable

## Integration Test Scenarios

### Test 12: Complete Manufacturing Workflow
**Goal**: End-to-end integration test

**Steps**:
1. User creates device
2. Hardware engineer uploads all files
3. Project manager reviews and approves
4. System generates manufacturing package
5. External manufacturer downloads package
6. Status progresses through production
7. Device marked as completed

**Expected Results**:
- ✅ Complete workflow executes without errors
- ✅ All status transitions logged
- ✅ Files remain accessible throughout lifecycle
- ✅ Audit trail captures all actions
- ✅ Final package contains all required files

### Test 13: Real-time Updates
**Goal**: Verify real-time status synchronization

**Steps**:
1. Open device page in two browser tabs
2. Update status in first tab
3. Verify second tab updates automatically
4. Upload file in first tab
5. Verify file appears in second tab

**Expected Results**:
- ✅ Status changes appear in real-time
- ✅ File uploads trigger UI updates
- ✅ No page refresh required
- ✅ WebSocket connections stable

## Test Data Cleanup

### Cleanup Steps
1. Delete all test devices
2. Remove uploaded test files from storage
3. Clear generated manufacturing packages
4. Reset database to clean state

**Automated Cleanup Script**:
```bash
# Run after all tests complete
npm run test:cleanup
```

## Success Criteria

**All tests must pass** to consider the PCB Manufacturing Readiness feature complete:

- ✅ Device CRUD operations work correctly
- ✅ File upload and validation functions properly
- ✅ Status workflow enforces business rules
- ✅ Manufacturing package generation works
- ✅ Access controls prevent unauthorized access
- ✅ Error handling provides clear user feedback
- ✅ Performance meets defined targets
- ✅ Real-time updates function correctly

**Definition of Done**:
- All quickstart scenarios execute successfully
- Error handling covers edge cases
- Performance targets met
- Security controls verified
- Documentation complete and accurate