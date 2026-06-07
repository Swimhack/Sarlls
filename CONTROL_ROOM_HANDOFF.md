# SafeSwitch Control Room Handoff

## Current State

- A local-first control-room app now exists under `control-room/`.
- The app builds with Vite and TypeScript.
- The local API is implemented on `127.0.0.1:4174`.
- Mission Control, Rev2 ordering, workstreams, files, activity, and settings pages are present.
- The server scans the real `production/` artifacts and derives readiness from those files plus stored workflow records.

## Verified So Far

- `npm.cmd test` passes in `control-room/`.
- `npm.cmd run build` passes in `control-room/`.
- Real artifact checks are wired to:
  - `production/drc_report.json`
  - `production/ESP32_Simple_IoT_BOM.csv`
  - `production/ESP32_Simple_IoT_CPL.csv`
  - `production/Sarlls_IoT_Switch_Rev2_JLCPCB.zip`

## Remaining Work

1. Add broader browser/UI test coverage.
2. Finish the remaining control-room plan items, especially the Playwright workflow checks.
3. Write `control-room/README.md` with install, run, and backup instructions.
4. Update project status docs only after final verification.

## Guardrails

- Do not revert unrelated user changes anywhere in the repo.
- Keep the control-room app local-only.
- Do not allow arbitrary shell commands from the browser UI.
- Treat physical board, car, and manufacturer checks as human-recorded data only.

## Useful Commands

```powershell
cd control-room
npm.cmd test
npm.cmd run build
```
