# W-Rebuild Detection Script
# Scans Windows system for installed development tools and software
# Returns JSON output for Python to parse

$ErrorActionPreference = "SilentlyContinue"
$detectedTools = @()

# Function to add detected tool
function Add-DetectedTool {
    param(
        [string]$Name,
        [string]$Version,
        [string]$Path,
        [string]$Type
    )
    
    $script:detectedTools += [PSCustomObject]@{
        Name = $Name
        Version = $Version
        Path = $Path
        Type = $Type
    }
}

# Check Visual Studio Code
$vscodePaths = @(
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
    "$env:ProgramFiles\Microsoft VS Code\Code.exe"
)
foreach ($path in $vscodePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Visual Studio Code" -Version $version -Path $path -Type "Editor"
            break
        } catch {}
    }
}

# Check Python installations
$pythonPaths = @()
# Check PATH environment
$pathDirs = $env:PATH -split ";"
foreach ($dir in $pathDirs) {
    $pythonExe = Join-Path $dir "python.exe"
    if (Test-Path $pythonExe) {
        $pythonPaths += $pythonExe
    }
}
# Check common installation locations
$commonPythonPaths = @(
    "$env:LOCALAPPDATA\Programs\Python",
    "$env:ProgramFiles\Python*",
    "$env:USERPROFILE\AppData\Local\Programs\Python"
)
foreach ($pattern in $commonPythonPaths) {
    $found = Get-ChildItem -Path $pattern -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue
    foreach ($item in $found) {
        $pythonPaths += $item.FullName
    }
}

# Get unique Python installations and their versions
$uniquePythons = $pythonPaths | Select-Object -Unique
foreach ($pythonPath in $uniquePythons) {
    try {
        $versionOutput = & $pythonPath --version 2>&1
        if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
            $version = $matches[1]
            Add-DetectedTool -Name "Python" -Version $version -Path $pythonPath -Type "Runtime"
        }
    } catch {}
}

# Check Anaconda/Miniconda
$condaPaths = @(
    "$env:USERPROFILE\Anaconda3\Scripts\conda.exe",
    "$env:USERPROFILE\Miniconda3\Scripts\conda.exe",
    "$env:ProgramData\Anaconda3\Scripts\conda.exe",
    "$env:ProgramData\Miniconda3\Scripts\conda.exe"
)
foreach ($condaPath in $condaPaths) {
    if (Test-Path $condaPath) {
        try {
            $versionOutput = & $condaPath --version 2>&1
            if ($versionOutput -match "conda (\d+\.\d+\.\d+)") {
                $version = $matches[1]
                $name = if ($condaPath -match "Miniconda") { "Miniconda" } else { "Anaconda" }
                Add-DetectedTool -Name $name -Version $version -Path $condaPath -Type "Environment"
                break
            }
        } catch {}
    }
}

# Check Java (JDK/JRE) - Enhanced
$javaPaths = @()
# Check JAVA_HOME
if ($env:JAVA_HOME -and (Test-Path "$env:JAVA_HOME\bin\java.exe")) {
    $javaPaths += "$env:JAVA_HOME\bin\java.exe"
}
# Check PATH
foreach ($dir in $pathDirs) {
    $javaExe = Join-Path $dir "java.exe"
    if (Test-Path $javaExe) {
        $javaPaths += $javaExe
    }
}
# Check common locations - more comprehensive
$commonJavaPaths = @(
    "$env:ProgramFiles\Java\*\bin\java.exe",
    "$env:ProgramFiles\Java\*\jre\bin\java.exe",
    "$env:ProgramFiles (x86)\Java\*\bin\java.exe",
    "$env:ProgramFiles\Eclipse Adoptium\*\bin\java.exe",
    "$env:ProgramFiles\Microsoft\*\bin\java.exe",
    "$env:ProgramFiles\Amazon Corretto\*\bin\java.exe",
    "$env:ProgramFiles\Zulu\*\bin\java.exe",
    "C:\Java\*\bin\java.exe"
)
foreach ($pattern in $commonJavaPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($item in $found) {
        $javaPaths += $item.FullName
    }
}

$uniqueJavas = $javaPaths | Select-Object -Unique
foreach ($javaPath in $uniqueJavas) {
    try {
        $versionOutput = & $javaPath -version 2>&1
        if ($versionOutput -match 'version "(.+?)"' -or $versionOutput -match 'openjdk version "(.+?)"') {
            $version = $matches[1]
            # Determine if it's JDK or JRE
            $javaHome = Split-Path -Parent (Split-Path -Parent $javaPath)
            $isJDK = Test-Path (Join-Path $javaHome "bin\javac.exe")
            $name = if ($isJDK) { "Java JDK" } else { "Java JRE" }
            Add-DetectedTool -Name $name -Version $version -Path $javaPath -Type "Runtime"
        }
    } catch {}
}

# Check Node.js
$nodePath = (Get-Command node -ErrorAction SilentlyContinue).Source
if ($nodePath) {
    try {
        $version = & node --version
        $version = $version -replace "v", ""
        Add-DetectedTool -Name "Node.js" -Version $version -Path $nodePath -Type "Runtime"
    } catch {}
}

# Check Git
$gitPath = (Get-Command git -ErrorAction SilentlyContinue).Source
if ($gitPath) {
    try {
        $versionOutput = & git --version
        if ($versionOutput -match "git version (\d+\.\d+\.\d+)") {
            $version = $matches[1]
            Add-DetectedTool -Name "Git" -Version $version -Path $gitPath -Type "Tool"
        }
    } catch {}
}

# Check Docker Desktop
$dockerPath = "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerPath) {
    try {
        $version = (Get-Item $dockerPath).VersionInfo.FileVersion
        Add-DetectedTool -Name "Docker Desktop" -Version $version -Path $dockerPath -Type "Tool"
    } catch {}
}

# Check SQL Developer (Oracle) - Enhanced with Portable Detection
$sqlDevFound = $false
$sqlDevVersion = "Unknown"
$sqlDevPath = ""

# Method 1: Check AppData for SQL Developer config (indicates it's been used)
$sqlDevConfigPath = "$env:APPDATA\SQL Developer"
if (Test-Path $sqlDevConfigPath) {
    # SQL Developer config exists, now find the actual installation
    # Check product-preferences.xml for IDE path
    $prefsFiles = Get-ChildItem -Path $sqlDevConfigPath -Filter "product-preferences.xml" -Recurse -ErrorAction SilentlyContinue
    foreach ($prefsFile in $prefsFiles) {
        try {
            $content = Get-Content $prefsFile.FullName -Raw -ErrorAction SilentlyContinue
            if ($content -match 'ide\.main\.dir.*?value="([^"]+)"') {
                $idePath = $matches[1]
                if (Test-Path $idePath) {
                    $sqlDevExe = Get-ChildItem -Path $idePath -Filter "sqldeveloper.exe" -Recurse -Depth 3 -ErrorAction SilentlyContinue | Select-Object -First 1
                    if ($sqlDevExe) {
                        $sqlDevPath = $sqlDevExe.FullName
                        $sqlDevFound = $true
                        break
                    }
                }
            }
        } catch {}
    }
    
    # If not found via prefs, try to get version from config
    if (-not $sqlDevFound) {
        $versionDirs = Get-ChildItem -Path $sqlDevConfigPath -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d+\.\d+' }
        if ($versionDirs) {
            $latestVersion = $versionDirs | Sort-Object Name -Descending | Select-Object -First 1
            $sqlDevVersion = $latestVersion.Name
        }
    }
}

# Method 2: Search common portable locations
if (-not $sqlDevFound) {
    $sqlDevPaths = @(
        "$env:USERPROFILE\sqldeveloper\sqldeveloper.exe",
        "$env:USERPROFILE\Downloads\sqldeveloper\sqldeveloper.exe",
        "$env:USERPROFILE\Desktop\sqldeveloper\sqldeveloper.exe",
        "$env:USERPROFILE\Documents\sqldeveloper\sqldeveloper.exe",
        "C:\sqldeveloper\sqldeveloper.exe",
        "D:\sqldeveloper\sqldeveloper.exe",
        "C:\Oracle\sqldeveloper\sqldeveloper.exe",
        "D:\Oracle\sqldeveloper\sqldeveloper.exe",
        "$env:ProgramFiles\Oracle\sqldeveloper\sqldeveloper.exe",
        "$env:ProgramFiles (x86)\Oracle\sqldeveloper\sqldeveloper.exe"
    )
    
    foreach ($path in $sqlDevPaths) {
        if (Test-Path $path) {
            $sqlDevPath = $path
            $sqlDevFound = $true
            break
        }
    }
}

# Method 3: Check for batch files that launch SQL Developer
if (-not $sqlDevFound) {
    $batchLocations = @(
        "$env:USERPROFILE\sqldeveloper\sqldeveloper.cmd",
        "$env:USERPROFILE\sqldeveloper\sqldeveloper.bat",
        "C:\sqldeveloper\sqldeveloper.cmd",
        "D:\sqldeveloper\sqldeveloper.cmd"
    )
    
    foreach ($batch in $batchLocations) {
        if (Test-Path $batch) {
            # Found batch file, try to locate the actual exe nearby
            $batchDir = Split-Path $batch
            $exeFile = Get-ChildItem -Path $batchDir -Filter "sqldeveloper.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($exeFile) {
                $sqlDevPath = $exeFile.FullName
                $sqlDevFound = $true
                break
            } else {
                # Use batch file itself as the path
                $sqlDevPath = $batch
                $sqlDevFound = $true
                break
            }
        }
    }
}

# Method 4: Wildcard search in common parent directories
if (-not $sqlDevFound) {
    $searchPaths = @(
        "$env:USERPROFILE\*sqldeveloper*\sqldeveloper.exe",
        "C:\*sqldeveloper*\sqldeveloper.exe",
        "D:\*sqldeveloper*\sqldeveloper.exe"
    )
    
    foreach ($pattern in $searchPaths) {
        $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $sqlDevPath = $found.FullName
            $sqlDevFound = $true
            break
        }
    }
}

# Method 5: Registry check
if (-not $sqlDevFound) {
    $regPaths = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    foreach ($regPath in $regPaths) {
        $apps = Get-ItemProperty $regPath -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "*SQL Developer*" }
        foreach ($app in $apps) {
            if ($app.InstallLocation) {
                $exePath = Get-ChildItem -Path $app.InstallLocation -Filter "sqldeveloper.exe" -Recurse -Depth 3 -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($exePath) {
                    $sqlDevPath = $exePath.FullName
                    $sqlDevVersion = $app.DisplayVersion
                    $sqlDevFound = $true
                    break
                }
            }
        }
    }
}

# Get version from product.conf if found
if ($sqlDevFound -and $sqlDevPath) {
    $confPath = Join-Path (Split-Path $sqlDevPath) "product.conf"
    if (Test-Path $confPath) {
        $conf = Get-Content $confPath -ErrorAction SilentlyContinue | Where-Object { $_ -match "SetVersion" }
        if ($conf -match "SetVersion\s+(.+)") {
            $sqlDevVersion = $matches[1].Trim()
        }
    }
    
    Add-DetectedTool -Name "Oracle SQL Developer" -Version $sqlDevVersion -Path $sqlDevPath -Type "Database Tool"
} elseif (Test-Path $sqlDevConfigPath) {
    # Config exists but couldn't find executable - report it anyway
    Add-DetectedTool -Name "Oracle SQL Developer (Config Only)" -Version $sqlDevVersion -Path $sqlDevConfigPath -Type "Database Tool"
}

# Check IntelliJ IDEA
$intellijPaths = @(
    "$env:ProgramFiles\JetBrains\IntelliJ IDEA*\bin\idea64.exe",
    "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\IDEA-U\*\bin\idea64.exe"
)
foreach ($pattern in $intellijPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        try {
            $version = $found.VersionInfo.FileVersion
            Add-DetectedTool -Name "IntelliJ IDEA" -Version $version -Path $found.FullName -Type "IDE"
            break
        } catch {}
    }
}

# Check PyCharm
$pycharmPaths = @(
    "$env:ProgramFiles\JetBrains\PyCharm*\bin\pycharm64.exe",
    "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\PyCharm-P\*\bin\pycharm64.exe"
)
foreach ($pattern in $pycharmPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        try {
            $version = $found.VersionInfo.FileVersion
            Add-DetectedTool -Name "PyCharm" -Version $version -Path $found.FullName -Type "IDE"
            break
        } catch {}
    }
}

# Check Postman
$postmanPath = "$env:LOCALAPPDATA\Postman\Postman.exe"
if (Test-Path $postmanPath) {
    try {
        $version = (Get-Item $postmanPath).VersionInfo.FileVersion
        Add-DetectedTool -Name "Postman" -Version $version -Path $postmanPath -Type "Tool"
    } catch {}
}

# Check Mockoon (API Mocking Tool)
$mockoonPaths = @(
    "$env:LOCALAPPDATA\Programs\mockoon\Mockoon.exe",
    "$env:LOCALAPPDATA\mockoon\Mockoon.exe",
    "$env:ProgramFiles\Mockoon\Mockoon.exe",
    "$env:APPDATA\mockoon\Mockoon.exe"
)
foreach ($path in $mockoonPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            if (-not $version) { $version = (Get-Item $path).VersionInfo.ProductVersion }
            Add-DetectedTool -Name "Mockoon" -Version $version -Path $path -Type "API Tool"
            break
        } catch {}
    }
}

# Check Insomnia (REST Client)
$insomniaPaths = @(
    "$env:LOCALAPPDATA\insomnia\Insomnia.exe",
    "$env:LOCALAPPDATA\Programs\Insomnia\Insomnia.exe"
)
foreach ($path in $insomniaPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Insomnia" -Version $version -Path $path -Type "API Tool"
            break
        } catch {}
    }
}

# Check MongoDB Compass
$compassPaths = @(
    "$env:LOCALAPPDATA\MongoDBCompass\MongoDBCompass.exe",
    "$env:ProgramFiles\MongoDB\Compass\MongoDBCompass.exe"
)
foreach ($path in $compassPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            if (-not $version) { $version = (Get-Item $path).VersionInfo.ProductVersion }
            Add-DetectedTool -Name "MongoDB Compass" -Version $version -Path $path -Type "Database Tool"
            break
        } catch {}
    }
}

# Check Robo 3T / Studio 3T
$robo3tPaths = @(
    "$env:ProgramFiles\3T\Robo 3T\robo3t.exe",
    "$env:ProgramFiles\Studio 3T\Studio-3T.exe",
    "$env:ProgramFiles (x86)\3T\Robo 3T\robo3t.exe"
)
foreach ($path in $robo3tPaths) {
    if (Test-Path $path) {
        try {
            $toolName = if ($path -match "Studio 3T") { "Studio 3T" } else { "Robo 3T" }
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name $toolName -Version $version -Path $path -Type "Database Tool"
            break
        } catch {}
    }
}

# Check DBeaver
$dbeaverPaths = @(
    "$env:ProgramFiles\DBeaver\dbeaver.exe",
    "$env:LOCALAPPDATA\DBeaver\dbeaver.exe"
)
foreach ($path in $dbeaverPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "DBeaver" -Version $version -Path $path -Type "Database Tool"
            break
        } catch {}
    }
}

# Check MySQL Workbench
$mysqlPaths = @(
    "$env:ProgramFiles\MySQL\MySQL Workbench*\MySQLWorkbench.exe",
    "$env:ProgramFiles (x86)\MySQL\MySQL Workbench*\MySQLWorkbench.exe"
)
foreach ($pattern in $mysqlPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        try {
            $version = $found.VersionInfo.FileVersion
            Add-DetectedTool -Name "MySQL Workbench" -Version $version -Path $found.FullName -Type "Database Tool"
            break
        } catch {}
    }
}

# Check pgAdmin (PostgreSQL)
$pgAdminPaths = @(
    "$env:ProgramFiles\pgAdmin*\runtime\pgAdmin4.exe",
    "$env:ProgramFiles (x86)\pgAdmin*\runtime\pgAdmin4.exe"
)
foreach ($pattern in $pgAdminPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        try {
            $version = $found.VersionInfo.FileVersion
            Add-DetectedTool -Name "pgAdmin" -Version $version -Path $found.FullName -Type "Database Tool"
            break
        } catch {}
    }
}

# Check Maven
$mvnPath = (Get-Command mvn -ErrorAction SilentlyContinue).Source
if ($mvnPath) {
    try {
        $versionOutput = & mvn --version 2>&1
        if ($versionOutput -match "Apache Maven (\d+\.\d+\.\d+)") {
            $version = $matches[1]
            Add-DetectedTool -Name "Apache Maven" -Version $version -Path $mvnPath -Type "Build Tool"
        }
    } catch {}
}

# Check Gradle
$gradlePath = (Get-Command gradle -ErrorAction SilentlyContinue).Source
if ($gradlePath) {
    try {
        $versionOutput = & gradle --version 2>&1
        if ($versionOutput -match "Gradle (\d+\.\d+(?:\.\d+)?)") {
            $version = $matches[1]
            Add-DetectedTool -Name "Gradle" -Version $version -Path $gradlePath -Type "Build Tool"
        }
    } catch {}
}

# Check Eclipse IDE
$eclipsePaths = @(
    "$env:ProgramFiles\Eclipse\eclipse.exe",
    "$env:ProgramFiles (x86)\Eclipse\eclipse.exe",
    "C:\Eclipse\eclipse.exe"
)
foreach ($path in $eclipsePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            if (-not $version) { $version = "Unknown" }
            Add-DetectedTool -Name "Eclipse IDE" -Version $version -Path $path -Type "IDE"
            break
        } catch {}
    }
}

# Check NetBeans
$netbeansPaths = @(
    "$env:ProgramFiles\NetBeans*\bin\netbeans64.exe",
    "$env:ProgramFiles (x86)\NetBeans*\bin\netbeans.exe"
)
foreach ($pattern in $netbeansPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        try {
            $version = $found.VersionInfo.FileVersion
            Add-DetectedTool -Name "NetBeans IDE" -Version $version -Path $found.FullName -Type "IDE"
            break
        } catch {}
    }
}

# Check Sublime Text
$sublimePaths = @(
    "$env:ProgramFiles\Sublime Text\sublime_text.exe",
    "$env:ProgramFiles\Sublime Text 3\sublime_text.exe",
    "$env:ProgramFiles\Sublime Text 4\sublime_text.exe"
)
foreach ($path in $sublimePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Sublime Text" -Version $version -Path $path -Type "Editor"
            break
        } catch {}
    }
}

# Check Notepad++
$notepadPath = "$env:ProgramFiles\Notepad++\notepad++.exe"
if (Test-Path $notepadPath) {
    try {
        $version = (Get-Item $notepadPath).VersionInfo.FileVersion
        Add-DetectedTool -Name "Notepad++" -Version $version -Path $notepadPath -Type "Editor"
    } catch {}
} else {
    $notepadPath = "$env:ProgramFiles (x86)\Notepad++\notepad++.exe"
    if (Test-Path $notepadPath) {
        try {
            $version = (Get-Item $notepadPath).VersionInfo.FileVersion
            Add-DetectedTool -Name "Notepad++" -Version $version -Path $notepadPath -Type "Editor"
        } catch {}
    }
}

# Check Android Studio
$androidStudioPaths = @(
    "$env:ProgramFiles\Android\Android Studio\bin\studio64.exe",
    "$env:LOCALAPPDATA\Programs\Android Studio\bin\studio64.exe"
)
foreach ($path in $androidStudioPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Android Studio" -Version $version -Path $path -Type "IDE"
            break
        } catch {}
    }
}

# Check Slack
$slackPath = "$env:LOCALAPPDATA\slack\slack.exe"
if (Test-Path $slackPath) {
    try {
        $version = (Get-Item $slackPath).VersionInfo.FileVersion
        Add-DetectedTool -Name "Slack" -Version $version -Path $slackPath -Type "Communication"
    } catch {}
}

# Check Microsoft Teams
$teamsPaths = @(
    "$env:LOCALAPPDATA\Microsoft\Teams\current\Teams.exe",
    "$env:ProgramFiles\Microsoft\Teams\current\Teams.exe"
)
foreach ($path in $teamsPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Microsoft Teams" -Version $version -Path $path -Type "Communication"
            break
        } catch {}
    }
}

# Check Zoom
$zoomPath = "$env:APPDATA\Zoom\bin\Zoom.exe"
if (Test-Path $zoomPath) {
    try {
        $version = (Get-Item $zoomPath).VersionInfo.FileVersion
        Add-DetectedTool -Name "Zoom" -Version $version -Path $zoomPath -Type "Communication"
    } catch {}
}

# Check Browsers
# Google Chrome
$chromePaths = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Google Chrome" -Version $version -Path $path -Type "Browser"
            break
        } catch {}
    }
}

# Microsoft Edge
$edgePaths = @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe"
)
foreach ($path in $edgePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Microsoft Edge" -Version $version -Path $path -Type "Browser"
            break
        } catch {}
    }
}

# Mozilla Firefox
$firefoxPaths = @(
    "$env:ProgramFiles\Mozilla Firefox\firefox.exe",
    "$env:ProgramFiles(x86)\Mozilla Firefox\firefox.exe"
)
foreach ($path in $firefoxPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Mozilla Firefox" -Version $version -Path $path -Type "Browser"
            break
        } catch {}
    }
}

# Brave Browser
$bravePaths = @(
    "$env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$env:ProgramFiles(x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe"
)
foreach ($path in $bravePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Brave Browser" -Version $version -Path $path -Type "Browser"
            break
        } catch {}
    }
}

# Opera Browser
$operaPaths = @(
    "$env:LOCALAPPDATA\Programs\Opera\opera.exe",
    "$env:ProgramFiles\Opera\opera.exe"
)
foreach ($path in $operaPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            Add-DetectedTool -Name "Opera" -Version $version -Path $path -Type "Browser"
            break
        } catch {}
    }
}

# Generic Registry Scanner for Development Tools
# This catches tools we might have missed
$devToolKeywords = @(
    "SQL Developer", "Mockoon", "Studio 3T", "Compass", "DataGrip",
    "Redis", "Elasticsearch", "Kibana", "Grafana", "TablePlus",
    "HeidiSQL", "SQLyog", "Navicat", "DbVisualizer", "RazorSQL",
    "Azure Data Studio", "SSMS", "SQL Server Management"
)

$regPaths = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$foundTools = @{}  # Track found tools to avoid duplicates

foreach ($regPath in $regPaths) {
    $allApps = Get-ItemProperty $regPath -ErrorAction SilentlyContinue
    foreach ($app in $allApps) {
        if ($app.DisplayName) {
            foreach ($keyword in $devToolKeywords) {
                if ($app.DisplayName -like "*$keyword*" -and -not $foundTools.ContainsKey($app.DisplayName)) {
                    # Try to find the executable
                    $exePath = $null
                    
                    # Method 1: Check InstallLocation
                    if ($app.InstallLocation -and (Test-Path $app.InstallLocation)) {
                        $exeFiles = Get-ChildItem -Path $app.InstallLocation -Filter "*.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue |
                                    Where-Object { $_.Name -notmatch 'unins|uninst|setup|install|update' } |
                                    Select-Object -First 1
                        if ($exeFiles) {
                            $exePath = $exeFiles.FullName
                        }
                    }
                    
                    # Method 2: Check DisplayIcon
                    if (-not $exePath -and $app.DisplayIcon) {
                        $iconPath = $app.DisplayIcon -replace '",\d+$', '' -replace '^"', ''
                        if ((Test-Path $iconPath) -and $iconPath -match '\.exe$') {
                            $exePath = $iconPath
                        }
                    }
                    
                    if ($exePath) {
                        # Check if we already detected this tool
                        $alreadyDetected = $detectedTools | Where-Object { $_.Path -eq $exePath }
                        if (-not $alreadyDetected) {
                            $version = if ($app.DisplayVersion) { $app.DisplayVersion } else { "Unknown" }
                            Add-DetectedTool -Name $app.DisplayName -Version $version -Path $exePath -Type "Tool"
                            $foundTools[$app.DisplayName] = $true
                        }
                    }
                    break
                }
            }
        }
    }
}

# Output as JSON
try {
    if ($detectedTools.Count -eq 0) {
        Write-Output "[]"
    } elseif ($detectedTools.Count -eq 1) {
        # Single tool - wrap in array
        Write-Output "[$($detectedTools | ConvertTo-Json -Depth 3 -Compress)]"
    } else {
        # Multiple tools
        Write-Output ($detectedTools | ConvertTo-Json -Depth 3 -Compress)
    }
} catch {
    Write-Output "[]"
}
