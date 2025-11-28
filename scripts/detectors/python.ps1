# Python Runtime Detector

$ErrorActionPreference = "SilentlyContinue"

$pythonPaths = @()
$pathDirs = $env:PATH -split ";"

# Check PATH
foreach ($dir in $pathDirs) {
    $pythonExe = Join-Path $dir "python.exe"
    if (Test-Path $pythonExe) {
        $pythonPaths += $pythonExe
    }
}

# Check common locations
$commonPaths = @(
    "$env:LOCALAPPDATA\Programs\Python\*\python.exe",
    "$env:ProgramFiles\Python*\python.exe"
)

foreach ($pattern in $commonPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($item in $found) {
        $pythonPaths += $item.FullName
    }
}

# Get unique installations
$uniquePythons = $pythonPaths | Select-Object -Unique

foreach ($pythonPath in $uniquePythons) {
    $versionOutput = & $pythonPath --version 2>&1
    if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
        $version = $matches[1]
        
        [PSCustomObject]@{
            Name = "Python"
            Version = $version
            Path = $pythonPath
            Type = "Runtime"
        }
    }
}
