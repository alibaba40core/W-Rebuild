# Node.js Detector

$ErrorActionPreference = "SilentlyContinue"

$nodePath = (Get-Command node -ErrorAction SilentlyContinue).Source
if ($nodePath) {
    $version = & node --version
    $version = $version -replace "v", ""
    
    [PSCustomObject]@{
        Name = "Node.js"
        Version = $version
        Path = $nodePath
        Type = "Runtime"
    }
}
