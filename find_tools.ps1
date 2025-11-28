# Quick tool finder - helps locate SQL Developer and Mockoon
Write-Host "Searching for SQL Developer and Mockoon..." -ForegroundColor Cyan
Write-Host ""

# Search for SQL Developer
Write-Host "=== SQL Developer Search ===" -ForegroundColor Yellow
$sqlDevLocations = @(
    "C:\",
    "D:\",
    "$env:ProgramFiles",
    "$env:ProgramFiles (x86)",
    "$env:USERPROFILE",
    "$env:LOCALAPPDATA"
)

foreach ($location in $sqlDevLocations) {
    if (Test-Path $location) {
        Write-Host "Searching $location..." -ForegroundColor Gray
        $found = Get-ChildItem -Path $location -Filter "sqldeveloper.exe" -Recurse -Depth 4 -ErrorAction SilentlyContinue
        foreach ($file in $found) {
            Write-Host "  FOUND: $($file.FullName)" -ForegroundColor Green
        }
    }
}

# Search for Mockoon
Write-Host ""
Write-Host "=== Mockoon Search ===" -ForegroundColor Yellow
$mockoonLocations = @(
    "$env:LOCALAPPDATA",
    "$env:ProgramFiles",
    "$env:APPDATA"
)

foreach ($location in $mockoonLocations) {
    if (Test-Path $location) {
        Write-Host "Searching $location..." -ForegroundColor Gray
        $found = Get-ChildItem -Path $location -Filter "*mockoon*.exe" -Recurse -Depth 4 -ErrorAction SilentlyContinue
        foreach ($file in $found) {
            Write-Host "  FOUND: $($file.FullName)" -ForegroundColor Green
        }
    }
}

# Check Registry
Write-Host ""
Write-Host "=== Registry Check ===" -ForegroundColor Yellow
$regPaths = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

foreach ($regPath in $regPaths) {
    $apps = Get-ItemProperty $regPath -ErrorAction SilentlyContinue | 
            Where-Object { $_.DisplayName -like "*SQL Developer*" -or $_.DisplayName -like "*Mockoon*" }
    foreach ($app in $apps) {
        Write-Host "Found in registry: $($app.DisplayName)" -ForegroundColor Green
        Write-Host "  Install Location: $($app.InstallLocation)" -ForegroundColor Gray
        Write-Host "  Version: $($app.DisplayVersion)" -ForegroundColor Gray
        if ($app.DisplayIcon) {
            Write-Host "  Icon: $($app.DisplayIcon)" -ForegroundColor Gray
        }
        Write-Host ""
    }
}

Write-Host "Search complete!" -ForegroundColor Cyan
