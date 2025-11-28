# Minimal detection test
Write-Host "Starting minimal detection test" -ForegroundColor Green

$tools = @()

# Test 1: Check Python
Write-Host "`nTest 1: Checking for Python..." -ForegroundColor Yellow
try {
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pythonPath) {
        $version = & python --version 2>&1
        Write-Host "Found Python: $pythonPath" -ForegroundColor Cyan
        Write-Host "Version output: $version" -ForegroundColor Cyan
        
        $tools += [PSCustomObject]@{
            Name = "Python"
            Version = $version -replace "Python ", ""
            Path = $pythonPath
            Type = "Runtime"
        }
    } else {
        Write-Host "Python not found in PATH" -ForegroundColor Red
    }
} catch {
    Write-Host "Error checking Python: $_" -ForegroundColor Red
}

# Test 2: Check VS Code
Write-Host "`nTest 2: Checking for VS Code..." -ForegroundColor Yellow
$vscodePath = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"
Write-Host "Checking path: $vscodePath" -ForegroundColor Cyan
if (Test-Path $vscodePath) {
    Write-Host "VS Code found!" -ForegroundColor Cyan
    $version = (Get-Item $vscodePath).VersionInfo.FileVersion
    Write-Host "Version: $version" -ForegroundColor Cyan
    
    $tools += [PSCustomObject]@{
        Name = "Visual Studio Code"
        Version = $version
        Path = $vscodePath
        Type = "Editor"
    }
} else {
    Write-Host "VS Code not found at $vscodePath" -ForegroundColor Red
    # Try alternate location
    $altPath = "$env:ProgramFiles\Microsoft VS Code\Code.exe"
    Write-Host "Checking alternate path: $altPath" -ForegroundColor Cyan
    if (Test-Path $altPath) {
        Write-Host "VS Code found at alternate location!" -ForegroundColor Cyan
        $version = (Get-Item $altPath).VersionInfo.FileVersion
        $tools += [PSCustomObject]@{
            Name = "Visual Studio Code"
            Version = $version
            Path = $altPath
            Type = "Editor"
        }
    }
}

# Output results
Write-Host "`n`nResults:" -ForegroundColor Green
Write-Host "Found $($tools.Count) tool(s)" -ForegroundColor Green

if ($tools.Count -gt 0) {
    Write-Host "`nJSON Output:" -ForegroundColor Yellow
    $json = $tools | ConvertTo-Json -Depth 3 -Compress
    Write-Host $json
    
    # Also output to stdout without Write-Host for capture
    $tools | ConvertTo-Json -Depth 3 -Compress
} else {
    Write-Host "No tools detected!" -ForegroundColor Red
    Write-Output "[]"
}
