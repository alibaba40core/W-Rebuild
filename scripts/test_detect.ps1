# Quick test of detection
Write-Host "Testing detection script..."
Write-Host "Python version:"
python --version

Write-Host "`nChecking for Python in PATH:"
where.exe python

Write-Host "`nChecking for VS Code:"
$vscodePath = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"
if (Test-Path $vscodePath) {
    Write-Host "VS Code found at: $vscodePath"
    $version = (Get-Item $vscodePath).VersionInfo.FileVersion
    Write-Host "Version: $version"
} else {
    Write-Host "VS Code not found at $vscodePath"
}

Write-Host "`nRunning full detection script..."
& "$PSScriptRoot\detect.ps1"
