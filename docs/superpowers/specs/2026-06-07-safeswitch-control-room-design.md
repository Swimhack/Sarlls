# SafeSwitch Control Room Design

**Date:** 2026-06-07  
**Status:** Approved for implementation  
**Deployment:** Local-first browser application  
**Primary user:** Non-technical project owner  
**Control level:** Full approved project actions

## Purpose

Build a local full-stack project control room that observes and manages the
entire SafeSwitch IoT switch project from one owner-friendly interface.

The control room must read real project artifacts, run approved engineering
actions, manage human-required workflows, preserve activity history, and make
project readiness understandable without requiring technical knowledge.

The system must never claim that a physical hardware test passed unless a human
recorded the result or connected hardware provided verifiable evidence.

## Product Principles

1. Plain English first; technical details available on demand.
2. Show one clear next action at the top of the dashboard.
3. Calculate readiness from explicit gates, not invented percentages.
4. Run real local project actions through a strict allowlist.
5. Preserve a timestamped history of checks, changes, and decisions.
6. Never hide failures or report unverified physical work as complete.
7. Require confirmation before actions that modify project files.

## Primary Experience

The default interface is the approved **Mission Control** layout.

The first screen must immediately answer:

1. Where is the project now?
2. What must happen next?
3. What is blocking progress?
4. What can the user do immediately?

### Primary Navigation

- Mission Control
- Rev2 Ordering
- Hardware
- Firmware
- Mobile App
- Automotive System
- Files & Documents
- Activity History
- Settings

### Mission Control Content

- Current product phase in plain English
- Current controller-board phase
- One prominent next required action
- Blocking issues and their impact
- Readiness gates grouped by workstream
- Recent action results
- Large action buttons:
  - Run all checks
  - Prepare Rev2 order
  - View manufacturing files
  - Compile firmware
  - Run Android tests
  - Record progress

Technical logs and detailed metrics are collapsed by default.

## Full-Stack Architecture

### Web Application

A React-based local browser application provides the owner interface and
technical detail views.

Responsibilities:

- Render project status and readiness
- Guide owner workflows
- Trigger approved backend actions
- Display action progress and results
- Manage checklists, notes, evidence, and records
- Show activity history

### Local API Service

A local backend runs inside the Sarlls workspace and exposes a private API to
the web application.

Responsibilities:

- Scan the project workspace
- Parse project artifacts
- Run allowlisted commands
- Stream or poll action status
- Persist project-management data
- Protect file-changing actions with confirmation
- Reject destructive or unknown commands

The service binds to localhost only. Authentication is unnecessary for the
initial local-only version because it is not exposed to a network.

### Local Database

Use a local SQLite database stored in an ignored application-data directory
inside the workspace.

Persist:

- Workflow checklist state
- Human test results
- Notes
- Manufacturer responses
- Component confirmations
- DFM review records
- Order details
- Evidence-file references
- Action runs and output summaries
- Activity history
- Application settings

Generated engineering artifacts remain in their existing project directories
and are referenced rather than duplicated in the database.

### Project Scanner

The scanner reads real workspace artifacts and converts them into structured
status:

- `PROJECT_STATUS.md`
- `REV2_ORDER_HANDOFF.md`
- `production/drc_report.json`
- Rev2 Gerber ZIP contents
- BOM and CPL
- Firmware source and latest compile results
- Android Gradle results
- Hardware bring-up logs
- Automotive integration documentation
- Git status

The scanner must tolerate missing or malformed files and report the impact in
plain English.

### Action Runner

Actions are predefined in code. The API does not accept arbitrary shell
commands.

Initial allowlisted actions:

- Run production DRC gate
- Validate BOM and CPL
- Validate Rev2 Gerber ZIP contents
- Run all non-mutating checks
- Compile production firmware
- Compile hardware-test firmware with `huge_app`
- Run Android Gradle tests
- Regenerate Rev2 PCB/manufacturing files with confirmation
- Open or reveal authoritative project files

Prohibited actions:

- Destructive Git operations
- Recursive deletion
- Arbitrary shell execution supplied by the browser
- Automatic approval of physical tests
- Automatic ordering or payment

## Workstreams

### Rev2 Ordering

Manage:

- Internal release validation
- USB-C manufacturer review
- SW1 confirmation
- SW2 confirmation
- J2 confirmation
- Fabrication preview review
- Assembly preview review
- DFM report review
- Substitution approvals
- Quote and order details
- Delivery and tracking details

Rev2 is **Ready to Order** only when:

- DRC gate has zero blocking findings
- BOM/CPL validation passes
- Gerber ZIP validation passes
- USB-C manufacturing approval is recorded
- SW1, SW2, and J2 confirmations are recorded
- DFM and preview review is recorded
- No unresolved manufacturer warning remains

### PCB Health

Display and run:

- DRC result
- Blocking-finding count
- Approved USB-C edge exceptions
- Warning count
- BOM line-item count
- CPL placement count
- Gerber ZIP file count and required-file status
- Authoritative release-file paths
- Manufacturing regeneration action

Regeneration requires explicit confirmation and creates before/after activity
records.

### Firmware

Display and run:

- Production WiFi firmware compile
- Hardware-test firmware compile using `huge_app`
- Program-size and memory results
- Compile history
- Firmware source-file links
- Physical flashing instructions

Firmware compilation does not imply that firmware has been flashed to a board.

### Mobile App

Display and run:

- Android build/test action
- Latest Gradle result
- Test-source availability
- App-to-ESP32 integration readiness
- Integration tasks and notes

The dashboard must state clearly that the current Android app is a UI prototype
until real ESP32 communication is implemented and verified.

### Hardware Bring-Up

Provide guided workflows for Rev1 and Rev2:

- Visual inspection
- USB cable insertion
- USB enumeration
- Firmware flashing
- 5V rail test
- 3.3V rail test
- WiFi test
- Serial test
- Relay test
- LED test
- J2 low-risk load test

Each physical step supports:

- Not started, passed, failed, blocked, or skipped state
- Notes
- Evidence-file reference
- Date
- Person recording result

### Automotive System

Track:

- Protected 12V input design
- External contactor selection
- Contactor-control wiring
- Bench supply testing
- Battery simulation testing
- Fault and disconnect testing
- Vehicle-safety review
- Controlled vehicle test

The product cannot become **Ready for Vehicle Test** until:

- Controller hardware passes bring-up
- App-to-device control passes
- Protected 12V power passes
- Contactor operation passes
- Bench-safety tests pass
- No unresolved safety blocker remains

### Files & Documents

Show authoritative files grouped by purpose:

- Manufacturing
- Firmware
- Mobile app
- Hardware bring-up
- Automotive system
- Project status

The UI must distinguish authoritative files from legacy or deprecated files.

### Activity History

Record:

- Action started
- Action completed
- Action failed
- Checklist state changed
- Note added
- Manufacturer response recorded
- Order data changed
- File-changing action confirmed

Each record contains timestamp, event type, summary, outcome, and optional
technical output reference.

## Status and Completion Model

Progress is derived from named gates. Percentages may only be shown as a visual
summary of completed required gates and must always be accompanied by the
underlying gate list.

Primary product states:

- Engineering prototype
- Controller pre-fabrication
- Controller ready to order
- Controller ordered
- Controller bring-up
- Controller validated
- Automotive integration
- Bench validated
- Ready for controlled vehicle test

State transitions occur only when their defined gates pass.

## Error Handling

Every failed software action must show:

- Plain-English failure summary
- Project impact
- Recommended recovery step
- Expandable technical output

Additional requirements:

- An action cannot run twice simultaneously.
- Long-running actions expose progress and cancellation when technically safe.
- Cancelling an action records a cancelled result.
- Backend restarts must not mark interrupted actions as passed.
- Missing files produce a clear blocked or degraded status.
- File-changing actions require a confirmation dialog naming affected files.

## UI and Interaction Design

### Visual Direction

- Dark charcoal and deep green Mission Control interface
- High-contrast readable text
- Green for verified pass
- Amber for waiting or human action required
- Red for blocking failures
- Restrained use of cards
- One strong next-action region
- Large, explicit action buttons
- Minimal technical terminology in default views

### Responsive Behavior

- Desktop is the primary environment.
- Tablet layouts preserve all management workflows.
- Mobile layouts support status review, checklist updates, and notes.
- File-changing or long-running engineering actions may require desktop.

### Accessibility

- Keyboard-accessible controls
- Visible focus states
- Semantic headings and labels
- Color is never the only status signal
- Reduced-motion support
- Sufficient contrast

## Testing Strategy

### Unit Tests

Cover:

- DRC report parsing
- BOM parsing and validation
- CPL parsing and validation
- Gerber ZIP validation
- Firmware output parsing
- Gradle output parsing
- Gate and readiness calculations
- Status transitions
- Action allowlist enforcement
- File-change confirmation rules
- Database repositories
- Missing/malformed artifact handling

### API Integration Tests

Cover:

- Project summary endpoint
- Workstream status endpoints
- Checklist updates
- Notes and evidence records
- Action start/status/cancel flows
- Concurrent-action rejection
- Action failure persistence
- File-changing confirmation enforcement
- Activity-history creation

### Browser Workflow Tests

Cover:

- Mission Control loads real project status
- Run-all-checks workflow
- Rev2 ordering checklist workflow
- Manufacturer response recording
- Failed action and recovery display
- Firmware compile workflow
- Android test workflow
- Physical-test manual recording
- Files and documents navigation
- Activity-history review

### Completion Criteria

Implementation is complete when:

- Every visible control has a real behavior
- All predefined software actions run through the backend
- Human-required workflows persist correctly
- No UI reports unverified physical work as passed
- Unit and API integration suites pass
- Core browser workflows pass
- The production build succeeds
- The rendered desktop and mobile UI have been visually reviewed

Physical hardware tests and external manufacturer approvals remain external
project work. The control room is complete when it accurately manages and
reports those workflows, not when those external tasks themselves are finished.

## Implementation Boundaries

Included:

- Local full-stack control room
- Real project observation
- Real allowlisted actions
- Persistent management workflows
- Comprehensive automated tests

Excluded from the initial implementation:

- Cloud hosting
- Multi-user authentication
- Remote network access
- Automatic manufacturer ordering or payment
- Automatic control of unconnected physical hardware
- Replacing the existing Android mobile app
