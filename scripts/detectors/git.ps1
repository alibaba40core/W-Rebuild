# Git Detector

$ErrorActionPreference = "SilentlyContinue"

$gitPath = (Get-Command git -ErrorAction SilentlyContinue).Source
if ($gitPath) {
    $versionOutput = & git --version
    if ($versionOutput -match "git version (\d+\.\d+\.\d+)") {
        $version = $matches[1]
        
        [PSCustomObject]@{
            Name = "Git"
            Version = $version
            Path = $gitPath
            Type = "Tool"
        }
    }
}
