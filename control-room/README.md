# SafeSwitch Control Room

Local-only dashboard for observing and managing the Sarlls / SafeSwitch project.

## What It Does

- Scans the real `production/` PCB, manufacturing, and firmware files.
- Tracks Rev2 ordering gates and human-recorded workflow statuses.
- Runs approved local actions only.
- Stores workflow and activity data in a local SQLite database.

## Security Model

- Binds to `127.0.0.1` only.
- Rejects non-local origins.
- Does not accept arbitrary shell commands from the browser.
- Requires explicit confirmation before file-changing actions.
- Physical and manufacturer checks must be recorded by a human.

## Install

```powershell
cd control-room
npm.cmd install
```

## Run

```powershell
cd control-room
npm.cmd run dev
```

- Client: `http://127.0.0.1:4173`
- API: `http://127.0.0.1:4174`

Production mode:

```powershell
npm.cmd start
```

## Test

```powershell
npm.cmd test
npm.cmd run build
```

The test suite covers:

- readiness rules
- real artifact scanners
- API behavior
- file-change confirmation gates

## Action Catalog

- `run-all-checks`
- `run-drc`
- `compile-production-firmware`
- `compile-test-firmware`
- `run-android-tests`
- `regenerate-rev2`

The regeneration action requires confirmation before it can run.

## Database

Workflow records, activity history, and action runs are stored in:

```text
.control-room/control-room.db
```

The `.control-room/` directory is ignored by Git.

## Backup And Restore

Back up the entire `.control-room/` directory to preserve state.

Restore by copying `.control-room/control-room.db` back into the same path.

## Current Project Boundary

This dashboard can validate software artifacts and record human review steps.
It cannot verify physical hardware, vehicle behavior, or manufacturer review on its own.
