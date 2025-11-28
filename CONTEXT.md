# W-Rebuild — Project Context File (For AI & Human Developers)

This file contains the authoritative architecture of the W-Rebuild automation tool.  
All AI coding agents (Cursor, Copilot, ChatGPT, etc.) must treat this as the ground truth.

**If ANY code, folder, or module structure changes, the agent must update CONTEXT.md to keep the project consistent.**

---

## 📘 Project Overview

W-Rebuild is a desktop automation tool for Windows that:

- ✅ Detects installed tools/software (Step 1 - Complete)
- ✅ Lets users choose what to back up (Step 2 - Complete)
- ✅ Saves settings/config files to OneDrive (Step 2 - Complete)
- ⚙️ Scans and selects backups for restoration (Step 3 Phase 1 - Complete)
- ⏳ Restores tools, configs, extensions, and workspace preferences (Step 3 Phase 2 - In Progress)
- Provides a clean PySide6 desktop interface
- Uses Python for logic
- Uses PowerShell for system-level automation

The system works with Windows 10/11 and future versions, and operates without admin rights whenever possible.

**Current Status:** Step 3 Phase 1 Complete - Restore UI with backup discovery and selection

---

## 📁 Final, Approved, Locked Project Structure

```text
W-Rebuild/
├── CONTEXT.md
├── venv/
├── requirements.txt
├── src/
│   ├── ui/
│   │   ├── main.py
│   │   ├── windows/
│   │   ├── components/
│   │   └── resources/
│   │
│   ├── core/
│   │   ├── detector.py
│   │   ├── backup.py
│   │   ├── restore.py
│   │   └── utils.py
│   │
│   └── cli/
│       ├── detect_cli.py
│       ├── backup_cli.py
│       └── restore_cli.py
│
├── scripts/
│   ├── detect.ps1
│   ├── backup.ps1
│   └── restore.ps1
│
└── docs/
    ├── ARCHITECTURE.md
    ├── DETECTOR_SPEC.md
    ├── BACKUP_SPEC.md
    └── RESTORE_SPEC.md
```

---

## 🔧 Component Roles

### 1. UI Layer (PySide6) — `src/ui/`

Local desktop app. No web server.

**Responsible for:**

- Application windows
- User interactions
- Tool selection
- Backup/restore dashboard

**Should not perform system logic directly.**  
**Must call functions from `src/core/`.**

### 2. Core Logic — `src/core/`

**Contains:**

- `detector.py` → Detect installed apps
- `backup.py` → Pack settings + configs
- `restore.py` → Reinstall apps & restore settings
- `utils.py` → Registry, FS operations, system utilities

**This is the heart of the project.**

### 3. CLI Tools — `src/cli/`

Optional.

**Allows:**

- Terminal power users
- CI execution
- Testing logic without UI

### 4. PowerShell Scripts — `/scripts/`

**Used for interacting with:**

- Windows registry
- Installed program list
- Environment variables
- AppData & user profiles
- System utilities (winget, choco, etc.)

**Python calls these scripts through subprocess when required.**

### 5. Documentation — `/docs/`

Every component must have a clear specification.

---

## 🤖 AI Coding Agent Rules

Any LLM/AI agent MUST follow these rules:

1. **MUST NOT change directory structure without updating CONTEXT.md.**
   - If a new file/folder is added → update CONTEXT.md.
   - If one is removed/renamed → update CONTEXT.md.

2. **MUST NOT introduce frontend frameworks (Angular/React/etc).**
   - UI is strictly PySide6 desktop application.

3. **MUST keep logic clean:**
   - `src/core`: business logic
   - `src/ui`: presentation layer
   - `scripts`: system-level operations

4. **Avoid unnecessary AI features.**
   - Only add AI where explicitly needed for decision-making.

5. **Backup formats must remain human-readable (JSON/YAML).**

---

## 🎯 Ready For Use

This CONTEXT.md is now stable, complete, and can be used as reference for:

- Cursor AI agent
- GitHub Copilot
- ChatGPT
- Any future coding assistant
