# W-Rebuild - Windows Workspace Configuration Backup & Restore Tool

**Complete Windows workspace configuration backup and restore solution** - Save your entire development environment (tools, settings, connections, extensions) and restore it on any Windows machine in minutes.

## 🚀 Features

### Detection
- **40+ Tools Supported**: Automatically detects installed development tools, IDEs, databases, and utilities
- **Smart Detection**: Finds tools in standard locations (Program Files, AppData, PATH)
- **Configuration Discovery**: Locates config files, settings, extensions, and plugins

### Backup
- **Comprehensive Backup**: Saves all tool configurations, settings, and preferences
- **Extension Support**: Backs up VS Code, JetBrains, Sublime Text extensions/plugins
- **Database Connections**: Saves SQL Developer, DBeaver, MySQL Workbench connections
- **Registry Entries**: Exports relevant registry keys
- **Environment Variables**: Backs up selected environment variables
- **OneDrive Integration**: Optionally save to OneDrive for cloud backup

### Restoration
- **Automatic Installation**: Installs missing tools via winget, direct download, or chocolatey
- **Smart Detection**: Skips already-installed tools
- **Configuration Restore**: Restores all backed-up settings and preferences
- **Version Migration**: Automatically migrates settings between tool versions (e.g., SQL Developer 24.3.0 → 24.3.1)
- **Extension Installation**: Restores all extensions and plugins
- **Shortcut Creation**: Automatically creates Desktop and Start Menu shortcuts
- **Staged Feedback**: Real-time progress updates during installation and restoration

## 📦 Installation

### Option 1: Download Executable (Recommended)
1. Download the latest release from [GitHub Releases](https://github.com/alibaba40core/W-Rebuild/releases)
2. Extract the ZIP file to your Windows machine
3. Run `W-Rebuild.exe`

### Option 2: Run from Source
```cmd
# Clone the repository
git clone https://github.com/alibaba40core/W-Rebuild.git
cd W-Rebuild

# Install dependencies
pip install -r requirements.txt

# Run the application
python src\ui\main.py
```

## 🛠️ Usage

### 1. Detection
- Launch W-Rebuild
- Click "Detect Tools" to scan your system
- Review the list of detected tools and configurations
- Optionally save detection results

### 2. Backup
- Click "Backup" after detection
- Select backup location (local folder or OneDrive)
- Choose which tools to backup
- Wait for backup to complete
- Backup manifest saved for restoration

### 3. Restore
- Launch W-Rebuild on new/clean machine
- Click "Restore"
- Select a backup folder (scans for manifest files)
- Review the backup contents in the HTML preview
- Click "Restore Selected Tools"
- Tool will:
  - Install missing tools automatically
  - Restore all configurations
  - Migrate settings between versions if needed
  - Create shortcuts
  - Install extensions/plugins

## 🔧 Supported Tools

### IDEs & Editors
- Visual Studio Code
- Visual Studio Code Insiders
- JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.)
- Sublime Text
- Notepad++
- Atom

### Database Tools
- Oracle SQL Developer (with connection & preference migration)
- DBeaver
- MySQL Workbench
- pgAdmin
- Azure Data Studio
- SQL Server Management Studio (SSMS)

### Development Tools
- Git
- Node.js
- Python
- Java (JDK)
- Docker Desktop
- Postman
- Insomnia
- Mockoon

### Terminal & SSH
- Windows Terminal
- MobaXterm
- PuTTY
- WinSCP

### Browsers
- Google Chrome
- Microsoft Edge
- Firefox
- Brave

### Communication
- Slack
- Microsoft Teams
- Discord
- Zoom

### Utilities
- 7-Zip
- WinRAR
- Notepad++
- PowerShell 7
- And many more...

## 🏗️ Building from Source

### Build Executable
```cmd
# Run the build script
build_exe.bat

# Output will be in:
# - dist\W-Rebuild\W-Rebuild.exe (executable)
# - release\ (distribution package)
```

### Manual Build
```cmd
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller W-Rebuild.spec --clean

# Executable location
dist\W-Rebuild\W-Rebuild.exe
```

## 📁 Project Structure

```
W-Rebuild/
├── src/
│   ├── cli/              # Command-line interface modules
│   │   ├── backup_cli.py
│   │   ├── detect_cli.py
│   │   └── restore_cli.py
│   ├── core/             # Core functionality
│   │   ├── backup.py     # Backup logic
│   │   ├── detector.py   # Tool detection
│   │   ├── restore.py    # Restoration logic
│   │   └── utils.py      # Utility functions
│   └── ui/               # GUI (PySide6)
│       ├── main.py       # Main window
│       └── components/   # UI components
├── docs/                 # Documentation
├── scripts/              # PowerShell scripts
├── requirements.txt      # Python dependencies
├── W-Rebuild.spec        # PyInstaller spec file
├── build_exe.bat         # Build script
└── README.md
```

## 🔒 Privacy & Security

- **Local Processing**: All detection and backup happens locally
- **No Data Collection**: No telemetry or analytics
- **Secure Storage**: Passwords in configs are preserved as-is from tool exports
- **OneDrive Optional**: Cloud backup is optional, local backup is default

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Windows UAC prompts cannot be fully bypassed for some installers
- Some tools require manual installation if not available via winget
- SQL Developer preferences require restart to apply

## 📞 Support

For issues and feature requests, please use [GitHub Issues](https://github.com/alibaba40core/W-Rebuild/issues).

## 🙏 Acknowledgments

- Built with PySide6 (Qt for Python)
- Uses winget for Windows tool installation
- Inspired by the need to quickly migrate complete Windows workspaces across machines

---

**Version**: 1.0.0  
**Last Updated**: November 2025
