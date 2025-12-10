#!/usr/bin/env powershell
# Enterprise Tools Detection Module
# Detects Omnissa Horizon Client, RSA Authenticator, and other enterprise applications

param()

$detectedTools = @()

# ============================================================================
# Omnissa Horizon Client Detection
# ============================================================================

function Detect-OmnissaHorizonClient {
    $tools = @()
    
    # Check Program Files for Omnissa/VMware Horizon
    $horizonPaths = @(
        "${env:ProgramFiles}\Omnissa\Horizon Client",
        "${env:ProgramFiles(x86)}\Omnissa\Horizon Client",
        "${env:ProgramFiles}\VMware\Horizon\Client",
        "${env:ProgramFiles(x86)}\VMware\Horizon\Client",
        "${env:ProgramFiles}\VMware\VMware Blast\Client",
        "${env:ProgramFiles}\Omnissa"
    )
    
    foreach ($path in $horizonPaths) {
        if (Test-Path $path) {
            # Look for horizon executable
            $exePath = Get-ChildItem -Path $path -Filter "*horizon*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            
            if ($null -eq $exePath) {
                $exePath = Get-ChildItem -Path $path -Filter "*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            }
            
            if ($exePath) {
                try {
                    $version = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($exePath.FullName).FileVersion
                    
                    $tools += @{
                        Name = "Omnissa Horizon Client"
                        Version = if ($version) { $version } else { "Installed" }
                        Path = $exePath.FullName
                        Type = "Enterprise"
                    }
                    break
                } catch {
                    continue
                }
            }
        }
    }
    
    # Check Registry for version info
    if ($null -eq $tools -or $tools.Count -eq 0) {
        $regPaths = @(
            "HKLM:\SOFTWARE\Omnissa\Horizon Client",
            "HKLM:\SOFTWARE\VMware\Horizon",
            "HKCU:\Software\Omnissa\Horizon Client",
            "HKCU:\Software\VMware\Horizon"
        )
        
        foreach ($regPath in $regPaths) {
            if (Test-Path $regPath) {
                $regItem = Get-Item -Path $regPath -ErrorAction SilentlyContinue
                if ($null -ne $regItem) {
                    $tools += @{
                        Name = "Omnissa Horizon Client"
                        Version = "Installed"
                        Path = "Registry Entry"
                        Type = "Enterprise"
                    }
                    break
                }
            }
        }
    }
    
    return $tools
}

# ============================================================================
# RSA Authenticator Detection
# ============================================================================

function Detect-RSAAuthenticator {
    $tools = @()
    
    # Check Program Files
    $rsaPaths = @(
        "${env:ProgramFiles}\RSA\Authenticator",
        "${env:ProgramFiles(x86)}\RSA\Authenticator",
        "${env:ProgramFiles}\RSA\SecurID",
        "${env:ProgramFiles(x86)}\RSA\SecurID",
        "${env:ProgramFiles}\RSA\Authentication Manager",
        "${env:ProgramFiles(x86)}\RSA\Authentication Manager",
        "${env:LOCALAPPDATA}\RSA\Authenticator"
    )
    
    foreach ($path in $rsaPaths) {
        if (Test-Path $path) {
            # Look for RSA authenticator executable
            $exePaths = @(
                "$path\RSAAuthenticator.exe",
                "$path\Authenticator.exe",
                "$path\ctf.exe",
                "$path\SecurID.exe",
                "$path\ctfmon.exe"
            )
            
            foreach ($exePath in $exePaths) {
                if (Test-Path $exePath) {
                    try {
                        $version = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($exePath).FileVersion
                        
                        $tools += @{
                            Name = "RSA Authenticator"
                            Version = if ($version) { $version } else { "Installed" }
                            Path = $exePath
                            Type = "Enterprise"
                        }
                        break
                    } catch {
                        continue
                    }
                }
            }
            
            if ($tools.Count -gt 0) {
                break
            }
        }
    }
    
    # Check AppData for RSA Authenticator
    if ($null -eq $tools -or $tools.Count -eq 0) {
        $appDataPath = "${env:APPDATA}\RSA\Authenticator"
        if (Test-Path $appDataPath) {
            $tools += @{
                Name = "RSA Authenticator"
                Version = "Installed"
                Path = $appDataPath
                Type = "Enterprise"
            }
        }
    }
    
    # Check Registry
    if ($null -eq $tools -or $tools.Count -eq 0) {
        $regPaths = @(
            "HKLM:\SOFTWARE\RSA\Authenticator",
            "HKLM:\SOFTWARE\Wow6432Node\RSA\Authenticator",
            "HKCU:\Software\RSA\Authenticator",
            "HKCU:\Software\RSA\SecurID"
        )
        
        foreach ($regPath in $regPaths) {
            if (Test-Path $regPath) {
                $regItem = Get-Item -Path $regPath -ErrorAction SilentlyContinue
                if ($null -ne $regItem) {
                    $tools += @{
                        Name = "RSA Authenticator"
                        Version = "Installed"
                        Path = "Registry Entry"
                        Type = "Enterprise"
                    }
                    break
                }
            }
        }
    }
    
    return $tools
}

# ============================================================================
# Execute Detection
# ============================================================================

$horizonTools = Detect-OmnissaHorizonClient
if ($horizonTools) {
    $detectedTools += $horizonTools
}

$rsaTools = Detect-RSAAuthenticator
if ($rsaTools) {
    $detectedTools += $rsaTools
}

# Return detected tools (modular script handles JSON conversion)
return $detectedTools
