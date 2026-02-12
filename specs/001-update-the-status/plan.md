
# Implementation Plan: PCB Manufacturing Readiness

**Branch**: `001-update-the-status` | **Date**: 2025-09-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-update-the-status/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Primary requirement: Create a system to track PCB device manufacturing status and generate complete specification files for manufacturer submission. The system must manage device status updates, validate specification completeness, and export files in industry-standard formats (Gerber, BOM, CPL).

## Technical Context
**Language/Version**: TypeScript/JavaScript (Node.js 18+) - web application for file management
**Primary Dependencies**: Next.js 14, React, Tailwind CSS, Supabase (existing stack)
**Storage**: Supabase PostgreSQL + Supabase Storage for PCB files
**Testing**: Jest, React Testing Library, Cypress for E2E
**Target Platform**: Web application (cross-platform browser support)
**Project Type**: web - extends existing Next.js contract comparison application
**Performance Goals**: <2s file generation, <5s large file uploads, real-time status updates
**Constraints**: Must integrate with existing auth system, maintain file security, support multiple file formats
**Scale/Scope**: 10-100 concurrent users, 100MB+ file uploads, version history tracking

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**✅ PASS** - No constitutional constraints defined (constitution.md is template). Project extends existing codebase following established patterns:
- Uses existing Next.js/TypeScript stack
- Leverages existing Supabase infrastructure
- Follows existing auth patterns
- No new architectural complexity introduced

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 2 (Web application) - Extends existing Next.js app structure with new PCB management features

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Database migration tasks for new PCB tables
- API endpoint implementation from devices-api.yaml contract
- UI components for device management workflow
- File upload and processing services
- Status management and validation logic
- Manufacturing package generation functionality

**Specific Task Categories**:
1. **Setup Tasks**: Database schema migration, Supabase policies
2. **Model Tasks [P]**: Device, DeviceFile, StatusHistory, ManufacturingPackage entities
3. **Service Tasks [P]**: File processing, status validation, package generation
4. **API Tasks**: Device CRUD, file upload, status updates, package download endpoints
5. **UI Tasks [P]**: Device list, device detail, file upload, status management components
6. **Integration Tasks**: Real-time updates, file validation, package ZIP creation
7. **Test Tasks [P]**: Contract tests, integration tests from quickstart scenarios

**Ordering Strategy**:
- TDD order: Contract tests → API implementation → UI integration
- Dependency order: Database → Models → Services → APIs → UI
- Mark [P] for parallel execution (independent files/components)
- Sequential for shared files (API routes, database schema)

**Parallel Execution Groups**:
- [P] Model classes (independent entities)
- [P] Service modules (file processing, validation)
- [P] UI components (device forms, file lists)
- [P] Contract test files (one per endpoint)

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - ✅ 2025-09-23
- [x] Phase 1: Design complete (/plan command) - ✅ 2025-09-23
- [x] Phase 2: Task planning complete (/plan command - describe approach only) - ✅ 2025-09-23
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS - No constraints defined
- [x] Post-Design Constitution Check: PASS - Extends existing patterns
- [x] All NEEDS CLARIFICATION resolved - Research phase addressed unknowns
- [x] Complexity deviations documented - No deviations required

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
