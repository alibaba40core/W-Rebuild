# Restore Specification - Step 3 Phase 1

## Overview

The Restore feature allows users to restore tool configurations, settings, and environment variables from previously created backups. This document describes Phase 1 implementation: **Backup Detection and Selection**.

## Current Implementation Status

### ✅ Phase 1 Complete: Backup Detection & Selection
- Scan for available backups in OneDrive folder
- List all backups with metadata (date, tools count, env vars count)
- Select backup (auto-selects most recent)
- Display detailed backup contents
- UI ready for restoration

### ⏳ Phase 2 Coming Next: Actual Restoration
- Tool configuration restoration
- Registry key import
- Environment variable restoration
- Extension/plugin installation
- Validation and verification

---

## Phase 1 Features

### Backup Discovery

**Location**: Same as backup creation
```
C:\Users\<username>\OneDrive - AMDOCS\Backup Folders\W-Rebuild\
```

**Scanned Items**:
- All folders starting with `backup_`
- Each folder must contain `manifest.json`
- Sorted by timestamp (newest first)

### Backup Metadata Display

For each backup, displays:
- **Backup Name**: `backup_YYYYMMDD_HHMMSS`
- **Date/Time**: Human-readable timestamp
- **Tools Count**: Number of backed-up tools
- **Environment Variables Count**: Number of backed-up variables

### Backup Details View

When a backup is selected, shows:
```
📦 Backup: backup_20250124_143022
🕐 Created: 2025-01-24T14:30:22
📁 Location: C:\Users\...\backup_20250124_143022

🔧 Tools (5):
  • Visual Studio Code v1.85.0
    - 4 item(s) backed up
  • Git v2.43.0
    - 3 item(s) backed up
  ...

🌍 Environment Variables (12):
  • PATH
  • JAVA_HOME
  • PYTHON_HOME
  ...
```

### Selection Mechanism

1. **Auto-select Most Recent**: By default, the newest backup is selected
2. **Manual Selection**: User can click any row to select different backup
3. **Radio Button**: Only one backup can be selected at a time
4. **Enable Restore Button**: Button enabled only when backup is selected

---

## Technical Architecture

### Core Module: `src/core/restore.py`

**Class**: `RestoreManager`

**Key Methods**:

```python
list_available_backups() -> List[Dict]
    # Returns list of all backups with metadata
    # Sorted by timestamp (newest first)

get_most_recent_backup() -> Optional[Dict]
    # Returns the most recent backup
    # None if no backups found

load_backup_details(backup_path: str) -> Optional[Dict]
    # Loads detailed info from manifest.json
    # Parses tools and environment variables

get_backup_summary(backup_path: str) -> str
    # Generates human-readable summary
    # Used for display in UI

restore_backup(backup_path, selected_tools, selected_env_vars) -> Dict
    # PLACEHOLDER for Phase 2
    # Will handle actual restoration
```

### UI Integration: `src/ui/main.py`

**New Tab**: "♻️ Restore"

**Components**:
1. **Scan for Backups Button**: Triggers backup discovery
2. **Backups Table**: Shows all available backups
3. **Backup Details Text**: Displays selected backup contents
4. **Restore Button**: Initiates restoration (placeholder in Phase 1)

**Event Handlers**:
```python
scan_for_backups()
    # Scans backup folder
    # Populates table
    # Auto-selects most recent

on_backup_selected()
    # Updates radio buttons
    # Shows backup details
    # Enables restore button

show_backup_details(backup)
    # Formats and displays backup summary

restore_selected_backup()
    # Shows preview dialog (Phase 1)
    # Will perform restoration (Phase 2)
```

---

## Data Flow

### Backup Discovery Flow
```
User clicks "Scan for Backups"
    ↓
RestoreManager.list_available_backups()
    ↓
Scans: C:\Users\...\OneDrive\...\W-Rebuild\
    ↓
For each backup_* folder:
    - Read manifest.json
    - Extract metadata
    - Add to list
    ↓
Sort by timestamp (newest first)
    ↓
Return to UI
    ↓
Populate table
    ↓
Auto-select first row (most recent)
    ↓
Display details
```

### Backup Selection Flow
```
User clicks on backup row
    ↓
on_backup_selected() triggered
    ↓
Update radio buttons (single selection)
    ↓
Get selected backup metadata
    ↓
RestoreManager.get_backup_summary(backup_path)
    ↓
Load manifest.json
    ↓
Format summary with tools & env vars
    ↓
Display in text area
    ↓
Enable "Restore" button
```

### Restore Preview Flow (Phase 1)
```
User clicks "Restore Selected Backup"
    ↓
Show confirmation dialog
    ↓
Display:
    - Backup name
    - Tools count
    - Env vars count
    - Phase 2 notice
    ↓
User confirms
    ↓
Show preview dialog:
    - What will be restored
    - Next phase notice
```

---

## Manifest.json Structure

The restore system reads from backup manifest files:

```json
{
    "backup_name": "backup_20250124_143022",
    "timestamp": "20250124_143022",
    "datetime": "2025-01-24T14:30:22.123456",
    "backup_location": "C:\\Users\\...\\backup_20250124_143022",
    "tools": [
        {
            "name": "Visual Studio Code",
            "version": "1.85.0",
            "path": "C:\\Program Files\\Microsoft VS Code\\Code.exe",
            "backed_up_items": [
                {
                    "description": "Complete User Configuration",
                    "source": "C:\\Users\\...\\AppData\\Roaming\\Code\\User",
                    "destination": "..\\vscode\\User",
                    "type": "folder",
                    "size_bytes": 12345
                },
                {
                    "description": "Registry Settings",
                    "source": "HKEY_CURRENT_USER\\Software\\Classes\\*\\shell\\VSCode",
                    "destination": "..\\vscode\\HKCU_Software_Classes_shell_VSCode.reg",
                    "type": "registry",
                    "size_bytes": 1024
                }
            ]
        }
    ],
    "environment_variables": [
        {
            "name": "JAVA_HOME",
            "value": "C:\\Program Files\\Java\\jdk-21"
        }
    ]
}
```

---

## User Experience

### Step-by-Step Workflow

1. **Open W-Rebuild Application**
   - Launch from command line or desktop shortcut

2. **Navigate to Restore Tab**
   - Click "♻️ Restore" tab

3. **Scan for Backups**
   - Click "🔍 Scan for Backups" button
   - Wait for scan to complete
   - See list of available backups

4. **Select Backup**
   - Most recent backup auto-selected
   - Or click any row to select different backup
   - View backup details on right side

5. **Review Contents**
   - Read list of tools that will be restored
   - Check environment variables included
   - Verify backup date and completeness

6. **Initiate Restore** (Preview in Phase 1)
   - Click "♻️ Restore Selected Backup" button
   - Confirm restoration
   - See preview of what will happen in Phase 2

---

## Error Handling

### No Backups Found
- Display message: "No backups found in: [path]"
- Suggest creating a backup first
- Provide link to Backup tab

### Corrupted Manifest
- Skip invalid backup folder
- Continue scanning other backups
- Log warning message

### Scan Failure
- Show error dialog with details
- Suggest checking OneDrive connection
- Retry option available

---

## Phase 2 Preview

### What's Coming Next

**Restoration Features**:
1. ✅ Tool Configuration Restoration
   - Copy backed-up files to original locations
   - Handle wildcards and version-specific paths
   - Preserve file permissions and timestamps

2. ✅ Registry Key Import
   - Import .reg files using `reg import`
   - Handle HKCU vs HKLM keys
   - Validate registry operations

3. ✅ Environment Variable Restoration
   - Update PATH with backed-up entries
   - Set user environment variables
   - Prompt for system variables (admin required)

4. ✅ Extension/Plugin Installation
   - VS Code: Install extensions from list
   - JetBrains: Plugin marketplace installation
   - Validate extension compatibility

5. ✅ Post-Restore Validation
   - Verify restored files exist
   - Check registry keys imported
   - Test environment variables set

6. ✅ Progress Reporting
   - Real-time progress indicators
   - Detailed success/failure reports
   - Rollback capability on errors

---

## Limitations (Phase 1)

- ❌ No actual file restoration
- ❌ No registry import
- ❌ No environment variable changes
- ❌ No tool installation
- ❌ No extension installation
- ✅ Only backup discovery and preview

---

## Testing Checklist

### Manual Testing

- [ ] Scan for backups shows all backup folders
- [ ] Most recent backup auto-selected
- [ ] Backup details display correctly
- [ ] Tool list shows all backed-up tools
- [ ] Environment variables list accurate
- [ ] Selection change updates details
- [ ] Restore button disabled with no selection
- [ ] Restore button enabled when backup selected
- [ ] Preview dialog shows correct information
- [ ] No backups message when folder empty

### Edge Cases

- [ ] Empty backup folder
- [ ] Corrupted manifest.json
- [ ] Missing manifest.json
- [ ] OneDrive not available
- [ ] Backup folder permissions denied
- [ ] Multiple backups with same timestamp
- [ ] Very old backup format compatibility

---

## Next Steps: Phase 2 Implementation

### Priority Order

1. **File Restoration** (High)
   - Copy configuration files back
   - Handle AppData folders
   - Restore user profiles

2. **Registry Import** (High)
   - Import .reg files
   - Validate registry changes
   - Handle errors gracefully

3. **Environment Variables** (Medium)
   - Set user variables
   - Update PATH
   - Handle system variables

4. **Extension Installation** (Medium)
   - VS Code extensions
   - JetBrains plugins
   - Browser extensions

5. **Tool Installation** (Future)
   - Download installers
   - Silent installation
   - Configuration post-install

---

## API Reference

### RestoreManager Class

```python
class RestoreManager:
    def __init__(self)
    def list_available_backups(self) -> List[Dict]
    def get_most_recent_backup(self) -> Optional[Dict]
    def load_backup_details(self, backup_path: str) -> Optional[Dict]
    def get_backup_summary(self, backup_path: str) -> str
    def restore_backup(self, backup_path: str, 
                      selected_tools: List[str],
                      selected_env_vars: List[str]) -> Dict
```

### Return Formats

**list_available_backups()**:
```python
[
    {
        "backup_name": "backup_20250124_143022",
        "backup_path": "C:\\...\\backup_20250124_143022",
        "timestamp": "20250124_143022",
        "datetime": "2025-01-24T14:30:22",
        "tools_count": 5,
        "env_vars_count": 12,
        "manifest": {...}  # Full manifest object
    }
]
```

**load_backup_details()**:
```python
{
    "backup_name": "backup_20250124_143022",
    "timestamp": "20250124_143022",
    "datetime": "2025-01-24T14:30:22",
    "backup_location": "C:\\...\\backup_20250124_143022",
    "tools": [...],  # Parsed tool list
    "environment_variables": [...],
    "tools_count": 5,
    "env_vars_count": 12
}
```

---

## Conclusion

Phase 1 of Step 3 (Restore) provides the foundation for restoration by implementing backup discovery, selection, and preview. Users can now browse their backups and understand what will be restored. Phase 2 will implement the actual restoration logic to complete the W-Rebuild workflow.
