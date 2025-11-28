# SQL Developer Detector - Portable & Installed versions

$ErrorActionPreference = "SilentlyContinue"

$sqlDevFound = $false
$sqlDevVersion = "Unknown"
$sqlDevPath = ""

# Method 1: Check AppData for config
$sqlDevConfigPath = "$env:APPDATA\SQL Developer"
if (Test-Path $sqlDevConfigPath) {
    $prefsFiles = Get-ChildItem -Path $sqlDevConfigPath -Filter "product-preferences.xml" -Recurse -ErrorAction SilentlyContinue
    foreach ($prefsFile in $prefsFiles) {
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
    }
    
    if (-not $sqlDevFound) {
        $versionDirs = Get-ChildItem -Path $sqlDevConfigPath -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d+\.\d+' }
        if ($versionDirs) {
            $latestVersion = $versionDirs | Sort-Object Name -Descending | Select-Object -First 1
            $sqlDevVersion = $latestVersion.Name
        }
    }
}

# Method 2: Common portable locations
if (-not $sqlDevFound) {
    $searchPaths = @(
        "$env:USERPROFILE\sqldeveloper\sqldeveloper.exe",
        "$env:USERPROFILE\Downloads\sqldeveloper\sqldeveloper.exe",
        "C:\sqldeveloper\sqldeveloper.exe",
        "D:\sqldeveloper\sqldeveloper.exe",
        "$env:ProgramFiles\Oracle\sqldeveloper\sqldeveloper.exe"
    )
    
    foreach ($path in $searchPaths) {
        if (Test-Path $path) {
            $sqlDevPath = $path
            $sqlDevFound = $true
            break
        }
    }
}

# Method 2.5: Check for batch/cmd files (portable installations)
if (-not $sqlDevFound) {
    $batchLocations = @(
        "$env:USERPROFILE\sqldeveloper\sqldeveloper.bat",
        "$env:USERPROFILE\sqldeveloper\sqldeveloper.cmd",
        "$env:USERPROFILE\Downloads\sqldeveloper\sqldeveloper.bat",
        "C:\sqldeveloper\sqldeveloper.bat",
        "D:\sqldeveloper\sqldeveloper.bat"
    )
    
    foreach ($batch in $batchLocations) {
        if (Test-Path $batch) {
            # Use batch file as the path
            $sqlDevPath = $batch
            $sqlDevFound = $true
            
            # Try to find exe nearby for better version info
            $batchDir = Split-Path $batch
            $exeFile = Get-ChildItem -Path $batchDir -Filter "sqldeveloper.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($exeFile) {
                $sqlDevPath = $exeFile.FullName
            }
            break
        }
    }
}

# Get version from product.conf
if ($sqlDevFound -and $sqlDevPath) {
    $confPath = Join-Path (Split-Path $sqlDevPath) "product.conf"
    if (Test-Path $confPath) {
        $conf = Get-Content $confPath -ErrorAction SilentlyContinue | Where-Object { $_ -match "SetVersion" }
        if ($conf -match "SetVersion\s+(.+)") {
            $sqlDevVersion = $matches[1].Trim()
        }
    }
    
    [PSCustomObject]@{
        Name = "Oracle SQL Developer"
        Version = $sqlDevVersion
        Path = $sqlDevPath
        Type = "Database Tool"
    }
} elseif (Test-Path $sqlDevConfigPath) {
    [PSCustomObject]@{
        Name = "Oracle SQL Developer (Config Only)"
        Version = $sqlDevVersion
        Path = $sqlDevConfigPath
        Type = "Database Tool"
    }
}
