# Docker Desktop Detector

$ErrorActionPreference = "SilentlyContinue"

$dockerPath = "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerPath) {
    $version = (Get-Item $dockerPath).VersionInfo.FileVersion
    
    [PSCustomObject]@{
        Name = "Docker Desktop"
        Version = $version
        Path = $dockerPath
        Type = "Tool"
    }
}
