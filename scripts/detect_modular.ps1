# W-Rebuild Modular Detection Script
# Dynamically loads and executes all detector modules
# Returns JSON output for Python to parse

$ErrorActionPreference = "SilentlyContinue"
$detectedTools = @()

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$detectorsDir = Join-Path $scriptDir "detectors"

# Check if detectors directory exists
if (Test-Path $detectorsDir) {
    # Get all PowerShell detector scripts
    $detectorScripts = Get-ChildItem -Path $detectorsDir -Filter "*.ps1" | Sort-Object Name
    
    # Execute each detector script
    foreach ($detector in $detectorScripts) {
        try {
            # Execute detector script and capture output
            $results = & $detector.FullName
            
            # Add results to main collection
            if ($results) {
                foreach ($result in $results) {
                    if ($result -and $result.Name) {
                        $detectedTools += $result
                    }
                }
            }
        } catch {
            # Silently continue if a detector fails
            continue
        }
    }
}

# Output as JSON
try {
    if ($detectedTools.Count -eq 0) {
        Write-Output "[]"
    } elseif ($detectedTools.Count -eq 1) {
        # Single tool - wrap in array
        Write-Output "[$($detectedTools | ConvertTo-Json -Depth 3 -Compress)]"
    } else {
        # Multiple tools
        Write-Output ($detectedTools | ConvertTo-Json -Depth 3 -Compress)
    }
} catch {
    Write-Output "[]"
}
