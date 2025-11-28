# Release Instructions for W-Rebuild - Windows Workspace Configuration Backup & Restore Tool

## Creating a Release

### 1. Prepare the Release

```cmd
# Ensure you're on the main branch
git checkout main

# Pull latest changes
git pull origin main

# Update version numbers in:
# - version_info.txt
# - README.md
# - src/ui/main.py (if version displayed)
```

### 2. Build the Executable

```cmd
# Run the build script
build_exe.bat

# Test the executable
dist\W-Rebuild\W-Rebuild.exe
```

### 3. Create Release Package

```cmd
# The build script creates a 'release' folder
# Compress it to ZIP
powershell Compress-Archive -Path release\* -DestinationPath W-Rebuild-v1.0.0-Windows.zip
```

### 4. Create GitHub Release

1. Go to GitHub repository
2. Click "Releases" → "Draft a new release"
3. Create a new tag: `v1.0.0`
4. Release title: `W-Rebuild v1.0.0`
5. Description:

```markdown
## W-Rebuild v1.0.0 - Windows Workspace Configuration Backup & Restore Tool

Complete solution for backing up and restoring your entire Windows workspace configuration including tools, settings, connections, and extensions.

### Features
- ✅ Detect 40+ development tools and configurations
- ✅ Comprehensive backup to local or OneDrive
- ✅ Automatic tool installation via winget
- ✅ Configuration restoration with version migration
- ✅ Extension/plugin restoration
- ✅ Automatic shortcut creation
- ✅ Responsive modern UI

### Installation
1. Download `W-Rebuild-v1.0.0-Windows.zip`
2. Extract to a folder
3. Run `W-Rebuild.exe`

### Supported Tools
- IDEs: VS Code, JetBrains, Sublime Text, Notepad++
- Databases: SQL Developer, DBeaver, MySQL Workbench
- Development: Git, Node.js, Python, Docker
- Terminal: Windows Terminal, MobaXterm, PuTTY
- And 30+ more tools...

### System Requirements
- Windows 10/11
- Administrator privileges (for some installations)

### What's New
- Initial release
- Full backup and restore functionality
- SQL Developer preference migration
- Universal shortcut creation

### Known Issues
- Windows UAC prompts required for some installers
- SQL Developer preferences require restart to apply

### Download
⬇️ [W-Rebuild-v1.0.0-Windows.zip](link-to-file)
```

6. Upload the ZIP file: `W-Rebuild-v1.0.0-Windows.zip`
7. Check "Set as the latest release"
8. Click "Publish release"

### 5. Update Repository

```cmd
# Add release notes
git add RELEASE.md

# Commit
git commit -m "Release v1.0.0"

# Push
git push origin main

# Create and push tag
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

## Initial Repository Setup

If this is your first time pushing to GitHub:

```cmd
# Initialize git repository
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit - W-Rebuild: Windows Workspace Configuration Backup & Restore Tool v1.0"

# Add remote repository
git remote add origin https://github.com/alibaba40core/W-Rebuild.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Release Checklist

- [ ] Update version numbers in all files
- [ ] Test executable on clean Windows machine
- [ ] Update README.md with latest features
- [ ] Build executable with `build_exe.bat`
- [ ] Test backup functionality
- [ ] Test restore functionality
- [ ] Test tool installation
- [ ] Create ZIP package
- [ ] Create GitHub release
- [ ] Upload ZIP to GitHub
- [ ] Update documentation
- [ ] Announce release

## Future Releases

For subsequent releases:

1. Update version number: `v1.0.0` → `v1.1.0` or `v2.0.0`
2. Update CHANGELOG.md with new features/fixes
3. Follow the same build and release process

## Download Statistics

After release, monitor:
- GitHub release download count
- Issue reports
- Feature requests

## Version Numbering

- **Major** (v2.0.0): Breaking changes, major new features
- **Minor** (v1.1.0): New features, non-breaking changes
- **Patch** (v1.0.1): Bug fixes, minor improvements
