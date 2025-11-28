# W-Rebuild Backup User Guide

## Quick Start

### 1. Launch W-Rebuild
```bash
cd C:\personal-sanbox\W-Rebuild
python src\ui\main.py
```

### 2. Detect Your Tools
- Click **"🔍 Scan System"** button
- Wait for detection to complete
- View detected tools in the table

### 3. Select What to Backup

#### Tools Tab
- ✓ Check tools you want to backup
- Use **"✓ Select All"** to select all tools
- Use **"✗ Deselect All"** to clear selection

#### Environment Variables Tab
- Switch to **"🌍 Environment Variables"** tab
- Search for specific variables using search box
- ✓ Check variables you want to backup
- Common variables to backup: `PATH`, `JAVA_HOME`, `PYTHON_HOME`, etc.

### 4. Review Your Selection
Look at the **Backup Summary** bar at the bottom:
```
🔧 3 Tools | VS Code, Git, PyCharm | 🌍 5 Variables | PATH, JAVA_HOME +3 more | [💾 Create Backup]
```

### 5. Create Backup
1. Click **"💾 Create Backup"** button
2. Review the confirmation dialog showing:
   - Number of tools to backup
   - Number of environment variables
   - Backup location
3. Click **"Yes"** to proceed
4. Wait for backup to complete (progress shown in status bar)

### 6. Backup Complete!
- Success dialog shows:
  - ✓ Backup created successfully
  - Timestamp
  - Backup folder location
  - Summary of what was backed up
- Click **"Yes"** to open the backup folder

## Backup Location

Your backups are saved to:
```
C:\Users\<YourUsername>\OneDrive - AMDOCS\Backup Folders\W-Rebuild\
```

Each backup creates a timestamped folder like:
```
backup_20250123_143022/
```

## What Gets Backed Up?

### Visual Studio Code
- ✓ User settings (`settings.json`)
- ✓ Keybindings (`keybindings.json`)
- ✓ Code snippets
- ✓ List of installed extensions

### JetBrains IDEs
- ✓ IDE configuration
- ✓ Keymaps
- ✓ Color schemes
- ✓ Plugins list

### Git
- ✓ `.gitconfig` (user name, email, aliases)
- ✓ `.gitignore_global`

### Other Tools
- SQL Developer: Configuration and connections
- Postman: Collections and settings
- Notepad++: Configuration and shortcuts
- Windows Terminal: Settings

### Environment Variables
- ✓ Variable name
- ✓ Variable value

## Understanding the Backup

### Manifest File
Each backup includes `manifest.json` that lists:
- When the backup was created
- What tools were backed up
- What files were copied
- Tool versions
- Environment variables

### Environment Variables File
`environment_variables.json` contains all selected variables with their values.

## Tips & Best Practices

### ✅ Do
- Create backups regularly
- Backup before major system changes
- Verify backup folder after creation
- Keep multiple backup versions
- Review what tools are selected

### ❌ Don't
- Don't manually edit backup files
- Don't backup sensitive passwords (they're excluded automatically)
- Don't delete backups immediately after creation

## Troubleshooting

### No Tools Detected
- Make sure tools are installed
- Try scanning again
- Check if tools are in standard locations

### Backup Failed
- Check OneDrive is connected
- Verify disk space available
- Check write permissions to OneDrive folder
- Review error message in dialog

### OneDrive Not Available
- App falls back to Documents folder
- You can manually move backups to OneDrive later

### Missing Configuration Files
- Some tools may not have config files yet (newly installed)
- This is normal and won't cause errors
- Only existing files are backed up

## Viewing Your Backups

Open the backup folder to see:
```
📁 backup_20250123_143022/
    📄 manifest.json              ← Backup metadata
    📄 environment_variables.json ← Your env variables
    📁 vscode/                    ← VS Code settings
    📁 git/                       ← Git configuration
    📁 intellij/                  ← IntelliJ settings
    ...
```

## What's NOT Backed Up

For security and size reasons, we DON'T backup:
- ❌ Passwords
- ❌ Private SSH keys
- ❌ API tokens/secrets
- ❌ Cache files
- ❌ Temporary files
- ❌ Large binary files

## Next Steps

After backing up:
1. ✅ Verify backup folder exists
2. ✅ Check manifest.json for completeness
3. ✅ Test opening a few config files
4. ✅ Keep backup safe in OneDrive

**Ready to format your system? Your tools and settings are safely backed up!**

---

## Need Help?

- Check `docs/BACKUP_SPEC.md` for technical details
- Review backup summary in success dialog
- Open manifest.json to see what was backed up
- Check status bar for progress messages

**Note**: Step 3 (Restore) is coming soon! You'll be able to restore your tools and settings after formatting.
