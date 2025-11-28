# Visual Studio Code Detector

$ErrorActionPreference = "SilentlyContinue"

$vscodePaths = @(
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
    "$env:ProgramFiles\Microsoft VS Code\Code.exe"
)

foreach ($path in $vscodePaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Visual Studio Code"
            Version = $version
            Path = $path
            Type = "Editor"
        }
        break
    }
}

# VS Code Insiders
$insidersPath = "$env:LOCALAPPDATA\Programs\Microsoft VS Code Insiders\Code - Insiders.exe"
if (Test-Path $insidersPath) {
    $version = (Get-Item $insidersPath).VersionInfo.FileVersion
    
    [PSCustomObject]@{
        Name = "Visual Studio Code Insiders"
        Version = $version
        Path = $insidersPath
        Type = "Editor"
    }
}
