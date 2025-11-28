# Anaconda & Conda Detector

$ErrorActionPreference = "SilentlyContinue"

# Check for Anaconda/Miniconda installations
$condaPaths = @(
    "$env:USERPROFILE\Anaconda3\Scripts\conda.exe",
    "$env:USERPROFILE\Miniconda3\Scripts\conda.exe",
    "$env:ProgramData\Anaconda3\Scripts\conda.exe",
    "$env:ProgramData\Miniconda3\Scripts\conda.exe",
    "C:\Anaconda3\Scripts\conda.exe",
    "C:\Miniconda3\Scripts\conda.exe"
)

foreach ($condaPath in $condaPaths) {
    if (Test-Path $condaPath) {
        $versionOutput = & $condaPath --version 2>&1
        if ($versionOutput -match "conda (\d+\.\d+\.\d+)") {
            $version = $matches[1]
            $name = if ($condaPath -match "Miniconda") { "Miniconda" } else { "Anaconda" }
            
            [PSCustomObject]@{
                Name = $name
                Version = $version
                Path = $condaPath
                Type = "Environment"
            }
            break
        }
    }
}

# Check for conda in PATH (any conda installation)
$condaInPath = (Get-Command conda -ErrorAction SilentlyContinue).Source
if ($condaInPath -and -not (Test-Path "$env:USERPROFILE\Anaconda3\Scripts\conda.exe")) {
    $versionOutput = & conda --version 2>&1
    if ($versionOutput -match "conda (\d+\.\d+\.\d+)") {
        $version = $matches[1]
        
        [PSCustomObject]@{
            Name = "Conda (PATH)"
            Version = $version
            Path = $condaInPath
            Type = "Environment"
        }
    }
}
