# Backup Specification

## Overview
W-Rebuild backup system creates comprehensive backups of tool configurations, settings, and environment variables to OneDrive for easy restoration after system formatting.

## Backup Location
```
C:\Users\<username>\OneDrive - AMDOCS\Backup Folders\W-Rebuild\
```
If OneDrive - AMDOCS is not available, falls back to:
- `OneDrive\Backup Folders\W-Rebuild\`
- `Documents\Backup Folders\W-Rebuild\` (if OneDrive not available)

## Backup Structure

Each backup creates a timestamped folder:
```
W-Rebuild/
├── backup_20250123_143022/
│   ├── manifest.json              # Backup metadata
│   ├── environment_variables.json # Selected environment variables
│   ├── vscode/
│   │   ├── settings.json
│   │   ├── keybindings.json
│   │   ├── snippets/
│   │   └── extensions.txt
│   ├── git/
│   │   ├── .gitconfig
│   │   └── .gitignore_global
│   ├── intellij/
│   │   └── config/
│   └── ...
```

## Manifest File Format

`manifest.json` contains:
```json
{
  "backup_name": "backup_20250123_143022",
  "timestamp": "20250123_143022",
  "datetime": "2025-01-23T14:30:22.123456",
  "tools": [
    {
      "name": "Visual Studio Code",
      "version": "1.85.0",
      "path": "C:\\Users\\...\\Code.exe",
      "backed_up_items": [
        {
          "description": "User Settings",
          "source": "C:\\Users\\...\\settings.json",
          "destination": "...\\vscode\\settings.json",
          "type": "file",
          "size_bytes": 2048
        }
      ]
    }
  ],
  "environment_variables": [
    {
      "name": "JAVA_HOME",
      "value": "C:\\Program Files\\Java\\jdk-17"
    }
  ],
  "backup_location": "C:\\Users\\...\\OneDrive - AMDOCS\\Backup Folders\\W-Rebuild\\backup_20250123_143022"
}
```

## Supported Tools & Backup Items

### Visual Studio Code
- `settings.json` - User settings
- `keybindings.json` - Custom keybindings
- `snippets/` - User code snippets
- `extensions.txt` - List of installed extensions

### JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.)
- `config/` - IDE configuration folder
- Settings, keymaps, color schemes, etc.

### Git
- `.gitconfig` - Git configuration
- `.gitignore_global` - Global gitignore rules

### Notepad++
- `config.xml` - Configuration
- `shortcuts.xml` - Keyboard shortcuts

### SQL Developer
- Full configuration folder including connections (passwords excluded)

### Postman
- Collections and settings

### Windows Terminal
- `settings.json` - Terminal configuration

## Backup Process

1. **User Selection**: User selects tools and environment variables from UI
2. **Confirmation**: System shows confirmation dialog with backup location
3. **Background Thread**: Backup runs in background to avoid UI blocking
4. **File Operations**:
   - Create timestamped backup folder
   - Copy configuration files for each tool
   - Export extension lists (VS Code, etc.)
   - Save environment variables to JSON
   - Generate manifest.json
5. **Completion**: Show success dialog with backup summary and option to open folder

## Backup Features

### Smart Path Resolution
- Expands environment variables (e.g., `%APPDATA%`)
- Handles wildcards in paths (e.g., `.PyCharm*`)
- Finds first matching folder for versioned paths

### Extension Handling
- VS Code: Exports extension list via `code --list-extensions`
- Can be restored using `code --install-extension <extension-id>`

### Error Handling
- Continues backup even if individual items fail
- Reports success/failure/skipped items in summary
- Detailed error messages in manifest

### Size Optimization
- Backs up configuration only, not cache or temporary files
- Skips large binary files when possible
- Focuses on human-editable settings

## Security Considerations

- Does **not** backup passwords or sensitive credentials
- SSH private keys are excluded (only public keys backed up)
- Database connection passwords are not included
- API tokens should be reviewed before backup

## Usage

### Creating a Backup
1. Click "Scan System" to detect tools
2. Select tools and environment variables to backup
3. Click "💾 Create Backup" button
4. Confirm backup location
5. Wait for completion (progress shown in status bar)
6. Option to open backup folder

### Backup Results
- **Success**: Tools backed up completely
- **Failed**: Items that encountered errors
- **Skipped**: Tools without backup configuration

## Future Enhancements (Step 3 - Restore)
- Restore configurations from backup
- Reinstall tools if missing
- Apply environment variables
- Install extensions automatically
- Selective restore (choose specific tools)

## Adding New Tool Support

To add backup support for a new tool, update `src/core/backup.py`:

```python
"Tool Name": {
    "name": "toolname",
    "paths": [
        {
            "source": r"%APPDATA%\ToolName\config.json",
            "type": "file",
            "description": "Configuration"
        }
    ]
}
```

## Technical Details

- **Language**: Python 3.x
- **UI Framework**: PySide6
- **File Operations**: shutil, pathlib
- **Threading**: QThread for background operations
- **Data Format**: JSON for manifest and environment variables
- **PowerShell**: Optional system-level operations via `scripts/backup.ps1`

## Error Recovery

If backup fails:
1. Check OneDrive connectivity
2. Verify write permissions to backup folder
3. Ensure sufficient disk space
4. Review detailed error in backup summary
5. Try backing up tools individually

## Best Practices

1. **Regular Backups**: Create backups before major system changes
2. **Verify**: Open backup folder to verify files
3. **Test Restore**: Periodically test restoration process
4. **Clean Old Backups**: Remove outdated backups to save space
5. **Document Custom Settings**: Add notes for custom configurations
