# ClawBot Setup Pro — PRD (v0.1)

## 1) Product Summary
**ClawBot Setup Pro** is a mobile companion app (iOS + Android) plus a desktop helper (Windows + macOS) that guides users through a complete OpenClaw/Claw Bot installation and configuration.

Goal: a user can pay, pair their computer, and end up with a **working bot** that can execute tasks without errors, with **remote monitoring** and optional **expert assistance**.

## 2) Target Users
- Non-technical but motivated creators/operators who want a working automation bot quickly.
- Small businesses who want a “concierge setup” without hiring a full-time engineer.

## 3) Success Definition
A setup is “successful” when:
- Claw Bot runs on the target machine.
- Default/specified tasks execute without errors.
- Bot is linked to the user account for remote monitoring (status, logs, health).
- A diagnostic report is generated and stored with the account.

## 4) Platforms (v1)
- **Mobile:** iOS, Android
- **Desktop Helper:** Windows 11+, macOS 13+
- **Later:** Linux, Chromebook

## 5) Business Model
- **External checkout** (Stripe/PayPal). After purchase, features unlock in the app.
- Core offer: **$1,000 per setup** (can evolve into tiers).
- Optional add-ons: priority scheduling, custom integrations, ongoing monitoring.

## 6) Product Scope (MVP)
### 6.1 Mobile App (Flutter recommended)
**Core capabilities**
- Auth: email + magic link (or OAuth) + device management
- Purchase verification: after external checkout, account is marked “active setup entitlement”
- Pairing flow: show a **QR code / pairing code** for the desktop helper
- Wizard: choose device type (Windows/macOS), choose bot goals/use case templates
- Live progress view: steps, logs, errors, retry
- “Request Expert Help”: upload diagnostic bundle, open support chat/ticket

**Out of scope (MVP)**
- Running installation directly from mobile (not feasible due to OS sandboxing)
- Full remote desktop control (screen sharing) — consider later

### 6.2 Desktop Helper (Agent)
**Core capabilities**
- Pairing: user enters code or scans QR from mobile
- Detect prerequisites: git, Python, Node (if needed), permissions, ports, firewall
- Install dependencies and Claw Bot repo (or user-provided repo URL)
- Configure:
  - env vars, config files, tokens
  - recommended default settings based on selected template
- Start/stop bot
- Collect diagnostics:
  - versions, logs, config snapshot (redacted), health checks
- Error remediation:
  - common fixes (PATH, venv recreation, pip conflicts, permissions)

**Security requirements**
- Explicit user approval on first pairing
- Signed binaries (later); for MVP, notarization for macOS and standard installer signing for Windows
- Redaction of secrets in logs; secure local secret storage (Keychain/DPAPI)

### 6.3 Backend
**Core capabilities**
- Accounts + auth tokens
- Device registry (desktop helpers)
- Job orchestration:
  - desktop helper polls/receives “run step” instructions
  - step results + logs streamed back
- Support system:
  - store diagnostic bundles
  - support notes/status

## 7) Key User Flows
### 7.1 Purchase → Pair → Setup
1. User installs mobile app
2. User signs up
3. User completes external checkout
4. App unlocks “Start Setup”
5. App shows pairing QR/code
6. User installs desktop helper on target machine
7. Desktop helper pairs → shows “Connected”
8. User selects template and clicks “Begin Setup”
9. Helper executes steps, app shows progress
10. Bot runs successfully; app shows “Setup Complete” + monitoring dashboard

### 7.2 Troubleshoot
- Error occurs → helper classifies error → auto-fix attempt
- If unresolved: offer “Guided mode” instructions + “Request Expert Help”

## 8) Templates (Examples)
- “Basic local assistant”
- “Home automation”
- “Content workflow”
- “Customer support triage”

## 9) Non-Functional Requirements
- Reliability: resumable steps; idempotent installs
- Observability: structured logs, step timing
- Privacy: minimize data collection; user controls diagnostic uploads

## 10) MVP Milestones
1. Architecture + repo scaffolds
2. Pairing + device registration
3. Step runner on desktop helper
4. Minimal wizard + progress UI
5. Diagnostic bundle + support request
6. Packaging: Windows installer + macOS pkg/notarization (initial)

## 11) Open Questions
- Exact Claw Bot repo URL and required runtime stack (Python/Node/etc.)
- Where does the bot “link to account” live today (OpenClaw gateway?)
- Support workflow: Zendesk/Intercom/email?
