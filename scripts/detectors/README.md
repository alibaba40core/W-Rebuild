# W-Rebuild Modular Detection System

## 📁 Directory Structure

```
scripts/
├── detect_modular.ps1          # Main orchestrator - loads all detectors
├── detect.ps1                  # Legacy monolithic script (backup)
└── detectors/                  # Individual detector modules
    ├── jetbrains.ps1           # All JetBrains IDEs
    ├── vscode.ps1              # Visual Studio Code
    ├── sqldeveloper.ps1        # Oracle SQL Developer
    ├── python.ps1              # Python runtime
    ├── java.ps1                # Java JDK/JRE
    ├── nodejs.ps1              # Node.js
    ├── git.ps1                 # Git
    ├── docker.ps1              # Docker Desktop
    ├── database-tools.ps1      # MongoDB, MySQL, PostgreSQL clients
    └── api-tools.ps1           # Postman, Mockoon, Insomnia
```

## ✨ How It Works

1. **Main Script** (`detect_modular.ps1`):
   - Automatically discovers all `.ps1` files in `detectors/` folder
   - Executes each detector script
   - Collects all results
   - Returns unified JSON output

2. **Individual Detectors**:
   - Each detector is a standalone PowerShell script
   - Returns an array of PSCustomObject with properties:
     - `Name` - Tool name
     - `Version` - Version string
     - `Path` - Full path to executable
     - `Type` - Category (IDE, Editor, Runtime, Tool, etc.)

## 🚀 Adding a New Tool Detector

### Method 1: Create New Detector File

1. Create a new `.ps1` file in `scripts/detectors/` folder
2. Name it descriptively (e.g., `sublime-text.ps1`, `postman.ps1`)
3. Follow this template:

```powershell
# Tool Name Detector
# Brief description of what this detects

$ErrorActionPreference = "SilentlyContinue"

# Detection logic here
$toolPath = "$env:ProgramFiles\ToolName\tool.exe"

if (Test-Path $toolPath) {
    $version = (Get-Item $toolPath).VersionInfo.FileVersion
    
    # Return PSCustomObject
    [PSCustomObject]@{
        Name = "Tool Name"
        Version = $version
        Path = $toolPath
        Type = "IDE"  # or "Editor", "Runtime", "Tool", "Database Tool", etc.
    }
}
```

4. **That's it!** The tool will automatically be detected on next scan.

### Method 2: Add to Existing Group Detector

If the tool fits into an existing category:
- Add to `database-tools.ps1` for database clients
- Add to `api-tools.ps1` for API testing tools
- Add to `jetbrains.ps1` for JetBrains products

## 📝 Example: Adding Sublime Text

Create `scripts/detectors/sublime-text.ps1`:

```powershell
# Sublime Text Editor Detector

$ErrorActionPreference = "SilentlyContinue"

$sublimePaths = @(
    "$env:ProgramFiles\Sublime Text\sublime_text.exe",
    "$env:ProgramFiles\Sublime Text 3\sublime_text.exe",
    "$env:ProgramFiles\Sublime Text 4\sublime_text.exe"
)

foreach ($path in $sublimePaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Sublime Text"
            Version = $version
            Path = $path
            Type = "Editor"
        }
        break
    }
}
```

Save the file and restart W-Rebuild - Sublime Text will now be detected!

## 🎯 Detection Patterns

### Common Patterns:

1. **Direct Path Check**:
```powershell
if (Test-Path "$env:ProgramFiles\Tool\tool.exe") {
    # ... detect
}
```

2. **PATH Environment Check**:
```powershell
$toolPath = (Get-Command tool -ErrorAction SilentlyContinue).Source
if ($toolPath) {
    # ... detect
}
```

3. **Wildcard Pattern Search**:
```powershell
$found = Get-ChildItem -Path "$env:ProgramFiles\Tool*\bin\tool.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($found) {
    # ... detect
}
```

4. **Registry Check**:
```powershell
$app = Get-ItemProperty "HKLM:\SOFTWARE\Tool" -ErrorAction SilentlyContinue
if ($app.InstallPath) {
    # ... detect
}
```

5. **AppData Config Detection** (for portable tools):
```powershell
$configPath = "$env:APPDATA\ToolName"
if (Test-Path $configPath) {
    # ... detect
}
```

## 🔧 Tool Types

Use these standard types for consistency:
- `IDE` - Integrated Development Environments
- `Editor` - Text/Code Editors
- `Runtime` - Language runtimes (Python, Java, Node.js)
- `Tool` - General development tools (Git, Docker)
- `Database Tool` - Database clients and managers
- `API Tool` - API testing and development tools
- `Build Tool` - Maven, Gradle, etc.
- `Communication` - Slack, Teams, Zoom

## ✅ Benefits of Modular System

1. **Easy to Add New Tools**: Just drop a new `.ps1` file in `detectors/` folder
2. **Easy to Maintain**: Each tool has its own isolated script
3. **Easy to Debug**: Test individual detectors separately
4. **Easy to Share**: Users can share custom detector scripts
5. **No Code Changes**: No need to modify main script
6. **Automatic Discovery**: New detectors are picked up automatically

## 🧪 Testing a Detector

Test individual detector scripts:
```powershell
# Test a specific detector
powershell -ExecutionPolicy Bypass -File scripts/detectors/vscode.ps1 | ConvertFrom-Json

# Test all detectors
powershell -ExecutionPolicy Bypass -File scripts/detect_modular.ps1 | ConvertFrom-Json
```

## 📦 Sharing Detectors

To share a detector with others:
1. Copy the `.ps1` file from `scripts/detectors/`
2. Share it with another user
3. They drop it in their `scripts/detectors/` folder
4. Tool is automatically detected!

## 🎨 Advanced: Multi-Tool Detectors

You can detect multiple related tools in one script:

```powershell
# JetBrains Family Detector
$jetbrainsTools = @("IntelliJ", "PyCharm", "WebStorm")

foreach ($tool in $jetbrainsTools) {
    # Detection logic
    [PSCustomObject]@{
        Name = $tool
        Version = $version
        Path = $path
        Type = "IDE"
    }
}
```

---

**💡 Pro Tip**: Look at existing detector scripts in the `detectors/` folder for real examples and patterns!
