# Browser Detection Module
# Detects installed web browsers

$ErrorActionPreference = "SilentlyContinue"

function Add-DetectedBrowser {
    param(
        [string]$Name,
        [string]$Version,
        [string]$Path
    )
    
    return [PSCustomObject]@{
        Name = $Name
        Version = $Version
        Path = $Path
        Type = "Browser"
    }
}

$detectedBrowsers = @()

# Check Google Chrome
$chromePaths = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            $detectedBrowsers += Add-DetectedBrowser -Name "Google Chrome" -Version $version -Path $path
            break
        } catch {}
    }
}

# Check Microsoft Edge
$edgePaths = @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)
foreach ($path in $edgePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            $detectedBrowsers += Add-DetectedBrowser -Name "Microsoft Edge" -Version $version -Path $path
            break
        } catch {}
    }
}

# Check Mozilla Firefox
$firefoxPaths = @(
    "$env:ProgramFiles\Mozilla Firefox\firefox.exe",
    "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe"
)
foreach ($path in $firefoxPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            $detectedBrowsers += Add-DetectedBrowser -Name "Mozilla Firefox" -Version $version -Path $path
            break
        } catch {}
    }
}

# Check Brave Browser
$bravePaths = @(
    "$env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe",
    "${env:ProgramFiles(x86)}\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe"
)
foreach ($path in $bravePaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            $detectedBrowsers += Add-DetectedBrowser -Name "Brave Browser" -Version $version -Path $path
            break
        } catch {}
    }
}

# Check Opera Browser
$operaPaths = @(
    "$env:LOCALAPPDATA\Programs\Opera\opera.exe",
    "$env:ProgramFiles\Opera\opera.exe",
    "${env:ProgramFiles(x86)}\Opera\opera.exe"
)
foreach ($path in $operaPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            $detectedBrowsers += Add-DetectedBrowser -Name "Opera" -Version $version -Path $path
            break
        } catch {}
    }
}

# Check Vivaldi Browser
$vivaldiPaths = @(
    "$env:LOCALAPPDATA\Vivaldi\Application\vivaldi.exe",
    "$env:ProgramFiles\Vivaldi\Application\vivaldi.exe",
    "${env:ProgramFiles(x86)}\Vivaldi\Application\vivaldi.exe"
)
foreach ($path in $vivaldiPaths) {
    if (Test-Path $path) {
        try {
            $version = (Get-Item $path).VersionInfo.FileVersion
            $detectedBrowsers += Add-DetectedBrowser -Name "Vivaldi" -Version $version -Path $path
            break
        } catch {}
    }
}

# Return detected browsers
return $detectedBrowsers
