# Quick SQL Developer finder
Write-Host "Quick SQL Developer Search..." -ForegroundColor Cyan

# Check Start Menu shortcuts
Write-Host "`n=== Checking Start Menu Shortcuts ===" -ForegroundColor Yellow
$startMenuPaths = @(
    "$env:ProgramData\Microsoft\Windows\Start Menu\Programs",
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
)

foreach ($path in $startMenuPaths) {
    if (Test-Path $path) {
        $shortcuts = Get-ChildItem -Path $path -Filter "*SQL*Developer*.lnk" -Recurse -ErrorAction SilentlyContinue
        foreach ($shortcut in $shortcuts) {
            Write-Host "Found shortcut: $($shortcut.FullName)" -ForegroundColor Green
            
            # Read shortcut target
            $shell = New-Object -ComObject WScript.Shell
            $target = $shell.CreateShortcut($shortcut.FullName).TargetPath
            if ($target) {
                Write-Host "  Target: $target" -ForegroundColor Cyan
            }
        }
    }
}

# Check if it's running
Write-Host "`n=== Checking if SQL Developer is running ===" -ForegroundColor Yellow
$running = Get-Process -Name "*sqldeveloper*" -ErrorAction SilentlyContinue
if ($running) {
    foreach ($proc in $running) {
        Write-Host "SQL Developer is running!" -ForegroundColor Green
        Write-Host "  Path: $($proc.Path)" -ForegroundColor Cyan
    }
} else {
    Write-Host "SQL Developer is not currently running" -ForegroundColor Gray
}

# Quick check of most common locations
Write-Host "`n=== Quick Check Common Locations ===" -ForegroundColor Yellow
$quickPaths = @(
    "C:\Oracle\sqldeveloper",
    "C:\sqldeveloper",
    "$env:USERPROFILE\Oracle\sqldeveloper",
    "$env:USERPROFILE\sqldeveloper",
    "$env:ProgramFiles\Oracle\sqldeveloper",
    "C:\Program Files\Oracle\sqldeveloper",
    "C:\app"
)

foreach ($path in $quickPaths) {
    if (Test-Path $path) {
        Write-Host "EXISTS: $path" -ForegroundColor Green
        $exe = Get-ChildItem -Path $path -Filter "sqldeveloper.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($exe) {
            Write-Host "  EXE: $($exe.FullName)" -ForegroundColor Cyan
        }
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan
