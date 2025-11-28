# API Tools Detector (Postman, Mockoon, Insomnia)

$ErrorActionPreference = "SilentlyContinue"

# Postman
$postmanPath = "$env:LOCALAPPDATA\Postman\Postman.exe"
if (Test-Path $postmanPath) {
    $version = (Get-Item $postmanPath).VersionInfo.FileVersion
    
    [PSCustomObject]@{
        Name = "Postman"
        Version = $version
        Path = $postmanPath
        Type = "API Tool"
    }
}

# Mockoon
$mockoonPaths = @(
    "$env:LOCALAPPDATA\Programs\mockoon\Mockoon.exe",
    "$env:LOCALAPPDATA\mockoon\Mockoon.exe"
)
foreach ($path in $mockoonPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        if (-not $version) { $version = (Get-Item $path).VersionInfo.ProductVersion }
        
        [PSCustomObject]@{
            Name = "Mockoon"
            Version = $version
            Path = $path
            Type = "API Tool"
        }
        break
    }
}

# Insomnia
$insomniaPaths = @(
    "$env:LOCALAPPDATA\insomnia\Insomnia.exe",
    "$env:LOCALAPPDATA\Programs\Insomnia\Insomnia.exe"
)
foreach ($path in $insomniaPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Insomnia"
            Version = $version
            Path = $path
            Type = "API Tool"
        }
        break
    }
}
