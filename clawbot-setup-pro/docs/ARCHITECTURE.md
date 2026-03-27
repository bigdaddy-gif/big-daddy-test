# ClawBot Setup Pro — Architecture (v0.1)

## Overview
Three components:
1) **Mobile app (Flutter)**: UX, account, pairing, progress, support.
2) **Desktop helper (Windows/macOS)**: performs installs/config + troubleshooting.
3) **Backend API**: auth, entitlements, devices, step orchestration, logs.

Mobile never installs dependencies directly; it controls + monitors the desktop helper.

## Recommended Tech Stack
### Mobile
- Flutter
- State: Riverpod/Bloc
- Auth: magic link + JWT

### Desktop Helper
Option A (recommended for speed): **Electron + Node**
- Pros: cross-platform UI, strong packaging ecosystem
- Can shell out to installers, manage files, run checks

Option B (leaner binary): **Go** (CLI + tray)
- Pros: single binary, easier signing
- UI is more work

MVP recommendation: **Go CLI + minimal tray** OR **Electron** depending on how much UI we want.

### Backend
- Node (NestJS/Fastify) or Python (FastAPI)
- Postgres
- Object storage for diagnostics (S3 compatible)

## Core API Objects
- User
- Entitlement (paid setup)
- Device (desktop helper)
- SetupSession
- Step (catalog)
- StepRun (per session)
- LogEvent
- DiagnosticBundle

## Pairing
- Mobile requests pairing code from backend.
- Desktop helper sends pairing code + device fingerprint.
- Backend issues device token.
- Device uses token for subsequent job polling / websocket.

## Orchestration Model
- Backend stores a **step plan** (template → ordered steps)
- Desktop helper executes steps and reports results.
- Steps must be idempotent and resumable.

## Security
- Device token scoped to one user.
- Secrets stored locally (DPAPI/Keychain).
- Logs redacted on device before upload.

## Packaging
- Windows: MSIX or NSIS installer.
- macOS: signed + notarized pkg.

## Later
- Screen sharing / remote assist
- Linux support
- Plugin system for new templates
