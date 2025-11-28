# W-Rebuild - Quick Start Guide

## Step 1: Detection Feature ✓ COMPLETED

### What's Built

The application now has a fully functional detection system that scans your Windows system for installed development tools and software.

### Features Implemented

1. **PowerShell Detection Script** (`scripts/detect.ps1`)
   - Scans Windows registry and common installation paths
   - Detects: VS Code, Python, Java, Anaconda/Miniconda, Node.js, Git, Docker, SQL Developer, IntelliJ IDEA, PyCharm, Postman
   - Returns structured JSON data

2. **Core Detector Module** (`src/core/detector.py`)
   - Python wrapper around PowerShell script
   - Clean API for tool detection
   - Caching system for performance
   - Type-based filtering

3. **Modern PySide6 UI** (`src/ui/main.py`)
   - Clean, professional desktop interface
   - Real-time system scanning
   - Results displayed in sortable table with:
     - Tool Name
     - Version
     - Type (IDE, Runtime, Tool, etc.)
     - Installation Path
   - Background threading (UI doesn't freeze during scan)
   - Progress indicators
   - Status messages

### How to Use

1. **Launch the Application**
   ```cmd
   cd c:\personal-sanbox\W-Rebuild
   python src\ui\main.py
   ```

2. **Scan Your System**
   - Click the "🔍 Scan System" button
   - Wait for detection to complete (usually 5-15 seconds)
   - View results in the table

3. **Review Detected Tools**
   - Each row shows a detected tool
   - Click on rows to see full installation paths
   - Use the information to plan backups

### Currently Detects

- **Editors**: Visual Studio Code
- **IDEs**: IntelliJ IDEA, PyCharm
- **Runtimes**: Python (all versions), Java (JDK/JRE), Node.js
- **Environments**: Anaconda, Miniconda
- **Tools**: Git, Docker Desktop, Postman, Oracle SQL Developer

### Project Structure Maintained

```
W-Rebuild/
├── src/
│   ├── ui/
│   │   └── main.py          ✓ Main application window
│   └── core/
│       └── detector.py      ✓ Detection logic
├── scripts/
│   └── detect.ps1           ✓ PowerShell scanner
├── requirements.txt         ✓ All dependencies listed
└── CONTEXT.md              ✓ Architecture maintained
```

### Next Steps for Future Development

**Step 2: Backup Feature**
- Select which tools to backup
- Export configurations to OneDrive
- Save VS Code extensions, settings
- Backup Python virtual environments
- Export IDE settings

**Step 3: Restore Feature**
- Re-install selected tools
- Restore configurations
- Apply saved settings
- Reinstall extensions

### Technical Notes

- UI built with PySide6 (native desktop app)
- PowerShell handles Windows-specific operations
- Core logic separated from UI (maintainable architecture)
- Background threading prevents UI freezing
- JSON-based data exchange between PowerShell and Python

### Dependencies Installed

- PySide6 6.10.1 (UI framework)
- psutil 7.1.3 (system utilities)
- PyYAML 6.0.3 (config file support)

---

**Status**: Step 1 Complete ✓  
**Ready for**: Step 2 Development (Backup Features)
