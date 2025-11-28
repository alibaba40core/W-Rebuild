# Terminal & SSH Tools Detector (MobaXterm, PuTTY, Windows Terminal, etc.)

$ErrorActionPreference = "SilentlyContinue"

# MobaXterm
$mobaxPaths = @(
    "$env:ProgramFiles\Mobatek\MobaXterm\MobaXterm.exe",
    "$env:ProgramFiles (x86)\Mobatek\MobaXterm\MobaXterm.exe",
    "$env:LOCALAPPDATA\Programs\MobaXterm\MobaXterm.exe",
    "$env:USERPROFILE\MobaXterm\MobaXterm.exe",
    "$env:USERPROFILE\Desktop\MobaXterm*.exe",
    "$env:USERPROFILE\Downloads\MobaXterm*.exe",
    "C:\MobaXterm*.exe"
)

$mobaxFound = $false
foreach ($pattern in $mobaxPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $version = $found.VersionInfo.FileVersion
        if (-not $version) { $version = $found.VersionInfo.ProductVersion }
        if (-not $version) { 
            # Try to extract from filename
            if ($found.Name -match 'v?(\d+\.\d+)') {
                $version = $matches[1]
            } else {
                $version = "Portable"
            }
        }
        
        [PSCustomObject]@{
            Name = "MobaXterm"
            Version = $version
            Path = $found.FullName
            Type = "Terminal"
        }
        $mobaxFound = $true
        break
    }
}

# Check for MobaXterm INI files (indicates portable usage)
if (-not $mobaxFound) {
    $iniLocations = @(
        "$env:USERPROFILE\MobaXterm.ini",
        "$env:USERPROFILE\Desktop\MobaXterm.ini",
        "$env:USERPROFILE\Documents\MobaXterm.ini"
    )
    
    foreach ($ini in $iniLocations) {
        if (Test-Path $ini) {
            $iniDir = Split-Path $ini
            $exeFile = Get-ChildItem -Path $iniDir -Filter "MobaXterm*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($exeFile) {
                [PSCustomObject]@{
                    Name = "MobaXterm"
                    Version = "Portable"
                    Path = $exeFile.FullName
                    Type = "Terminal"
                }
                $mobaxFound = $true
                break
            }
        }
    }
}

# PuTTY
$puttyPaths = @(
    "$env:ProgramFiles\PuTTY\putty.exe",
    "$env:ProgramFiles (x86)\PuTTY\putty.exe",
    "$env:LOCALAPPDATA\Programs\PuTTY\putty.exe"
)
foreach ($path in $puttyPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        if (-not $version) { $version = (Get-Item $path).VersionInfo.ProductVersion }
        
        [PSCustomObject]@{
            Name = "PuTTY"
            Version = $version
            Path = $path
            Type = "Terminal"
        }
        break
    }
}

# Check if PuTTY is in PATH
$puttyInPath = (Get-Command putty -ErrorAction SilentlyContinue).Source
if ($puttyInPath -and -not (Test-Path "$env:ProgramFiles\PuTTY\putty.exe")) {
    $version = (Get-Item $puttyInPath).VersionInfo.FileVersion
    
    [PSCustomObject]@{
        Name = "PuTTY"
        Version = $version
        Path = $puttyInPath
        Type = "Terminal"
    }
}

# Cmder
$cmderPaths = @(
    "$env:ProgramFiles\cmder\Cmder.exe",
    "$env:LOCALAPPDATA\cmder\Cmder.exe",
    "$env:USERPROFILE\cmder\Cmder.exe",
    "C:\cmder\Cmder.exe"
)
foreach ($path in $cmderPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        if (-not $version) { $version = "Unknown" }
        
        [PSCustomObject]@{
            Name = "Cmder"
            Version = $version
            Path = $path
            Type = "Terminal"
        }
        break
    }
}

# WinSCP
$winscpPaths = @(
    "$env:ProgramFiles\WinSCP\WinSCP.exe",
    "$env:ProgramFiles (x86)\WinSCP\WinSCP.exe"
)
foreach ($path in $winscpPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "WinSCP"
            Version = $version
            Path = $path
            Type = "Terminal"
        }
        break
    }
}

# Bitvise SSH Client
$bitvisePaths = @(
    "$env:ProgramFiles\Bitvise SSH Client\BvSsh.exe",
    "$env:ProgramFiles (x86)\Bitvise SSH Client\BvSsh.exe"
)
foreach ($path in $bitvisePaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Bitvise SSH Client"
            Version = $version
            Path = $path
            Type = "Terminal"
        }
        break
    }
}

# SecureCRT
$securecrtPaths = @(
    "$env:ProgramFiles\VanDyke Software\SecureCRT\SecureCRT.exe",
    "$env:ProgramFiles (x86)\VanDyke Software\SecureCRT\SecureCRT.exe"
)
foreach ($path in $securecrtPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "SecureCRT"
            Version = $version
            Path = $path
            Type = "Terminal"
        }
        break
    }
}
