# W-Rebuild Backup PowerShell Script
# Handles system-level backup operations

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath,
    
    [Parameter(Mandatory=$false)]
    [string]$ToolName,
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigPath
)

$ErrorActionPreference = "Stop"

function Backup-RegistryKey {
    param(
        [string]$KeyPath,
        [string]$DestPath
    )
    
    try {
        if (Test-Path $KeyPath) {
            $regFile = Join-Path $DestPath "registry_export.reg"
            reg export $KeyPath $regFile /y | Out-Null
            
            if (Test-Path $regFile) {
                return @{
                    Success = $true
                    Path = $regFile
                }
            }
        }
        
        return @{
            Success = $false
            Error = "Registry key not found"
        }
    }
    catch {
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Backup-WindowsTerminalSettings {
    param([string]$DestPath)
    
    $terminalPackages = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "Microsoft.WindowsTerminal_*" -ErrorAction SilentlyContinue
    
    foreach ($package in $terminalPackages) {
        $settingsPath = Join-Path $package.FullName "LocalState\settings.json"
        
        if (Test-Path $settingsPath) {
            $destFile = Join-Path $DestPath "settings.json"
            Copy-Item $settingsPath $destFile -Force
            
            return @{
                Success = $true
                Path = $destFile
            }
        }
    }
    
    return @{
        Success = $false
        Error = "Windows Terminal settings not found"
    }
}

function Backup-SSHKeys {
    param([string]$DestPath)
    
    $sshPath = "$env:USERPROFILE\.ssh"
    
    if (Test-Path $sshPath) {
        $destSSH = Join-Path $DestPath "ssh"
        
        # Only backup public keys and config, not private keys (security)
        $itemsToCopy = @("*.pub", "config", "known_hosts")
        
        New-Item -ItemType Directory -Path $destSSH -Force | Out-Null
        
        foreach ($pattern in $itemsToCopy) {
            $files = Get-ChildItem $sshPath -Filter $pattern -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                Copy-Item $file.FullName (Join-Path $destSSH $file.Name) -Force
            }
        }
        
        return @{
            Success = $true
            Path = $destSSH
        }
    }
    
    return @{
        Success = $false
        Error = "SSH directory not found"
    }
}

function Backup-PowerShellProfile {
    param([string]$DestPath)
    
    $profiles = @(
        $PROFILE.CurrentUserAllHosts,
        $PROFILE.CurrentUserCurrentHost
    )
    
    $backedUp = @()
    
    foreach ($profilePath in $profiles) {
        if (Test-Path $profilePath) {
            $fileName = Split-Path $profilePath -Leaf
            $destFile = Join-Path $DestPath $fileName
            Copy-Item $profilePath $destFile -Force
            $backedUp += $destFile
        }
    }
    
    if ($backedUp.Count -gt 0) {
        return @{
            Success = $true
            Paths = $backedUp
        }
    }
    
    return @{
        Success = $false
        Error = "No PowerShell profiles found"
    }
}

function Backup-ChromiumBrowserData {
    param(
        [string]$BrowserName,
        [string]$BrowserPath,
        [string]$DestPath
    )
    
    $userDataPath = "$env:LOCALAPPDATA\$BrowserPath\User Data"
    
    if (Test-Path $userDataPath) {
        $destBrowser = Join-Path $DestPath $BrowserName
        New-Item -ItemType Directory -Path $destBrowser -Force | Out-Null
        
        # Backup bookmarks and preferences (not cache or history for space)
        $itemsToCopy = @("Bookmarks", "Preferences", "Local State")
        
        foreach ($item in $itemsToCopy) {
            $sourcePath = Join-Path $userDataPath "Default\$item"
            if (Test-Path $sourcePath) {
                Copy-Item $sourcePath (Join-Path $destBrowser $item) -Force
            }
        }
        
        return @{
            Success = $true
            Path = $destBrowser
        }
    }
    
    return @{
        Success = $false
        Error = "$BrowserName data not found"
    }
}

# Main execution
try {
    # Ensure backup path exists
    if (-not (Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    }
    
    $result = @{
        Success = $true
        BackupPath = $BackupPath
        Items = @()
    }
    
    # Tool-specific backup operations
    switch ($ToolName) {
        "WindowsTerminal" {
            $terminalBackup = Backup-WindowsTerminalSettings -DestPath $BackupPath
            $result.Items += $terminalBackup
        }
        "SSH" {
            $sshBackup = Backup-SSHKeys -DestPath $BackupPath
            $result.Items += $sshBackup
        }
        "PowerShell" {
            $psBackup = Backup-PowerShellProfile -DestPath $BackupPath
            $result.Items += $psBackup
        }
        "Chrome" {
            $chromeBackup = Backup-ChromiumBrowserData -BrowserName "Chrome" -BrowserPath "Google\Chrome" -DestPath $BackupPath
            $result.Items += $chromeBackup
        }
        "Edge" {
            $edgeBackup = Backup-ChromiumBrowserData -BrowserName "Edge" -BrowserPath "Microsoft\Edge" -DestPath $BackupPath
            $result.Items += $edgeBackup
        }
    }
    
    # Output result as JSON
    $result | ConvertTo-Json -Depth 10
}
catch {
    @{
        Success = $false
        Error = $_.Exception.Message
    } | ConvertTo-Json
}
