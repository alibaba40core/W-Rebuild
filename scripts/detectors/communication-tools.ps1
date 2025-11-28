# Communication Tools Detector (Slack, Teams, Zoom, Discord, etc.)

$ErrorActionPreference = "SilentlyContinue"

# Slack
$slackPath = "$env:LOCALAPPDATA\slack\slack.exe"
if (Test-Path $slackPath) {
    $version = (Get-Item $slackPath).VersionInfo.FileVersion
    
    [PSCustomObject]@{
        Name = "Slack"
        Version = $version
        Path = $slackPath
        Type = "Communication"
    }
}

# Microsoft Teams
$teamsPaths = @(
    "$env:LOCALAPPDATA\Microsoft\Teams\current\Teams.exe",
    "$env:ProgramFiles\Microsoft\Teams\current\Teams.exe",
    "$env:LOCALAPPDATA\Programs\Microsoft Teams\Teams.exe"
)
foreach ($path in $teamsPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Microsoft Teams"
            Version = $version
            Path = $path
            Type = "Communication"
        }
        break
    }
}

# Zoom
$zoomPath = "$env:APPDATA\Zoom\bin\Zoom.exe"
if (Test-Path $zoomPath) {
    $version = (Get-Item $zoomPath).VersionInfo.FileVersion
    
    [PSCustomObject]@{
        Name = "Zoom"
        Version = $version
        Path = $zoomPath
        Type = "Communication"
    }
}

# Discord
$discordPath = "$env:LOCALAPPDATA\Discord\app-*\Discord.exe"
$found = Get-ChildItem -Path $discordPath -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
if ($found) {
    $version = $found.Directory.Name -replace "app-", ""
    
    [PSCustomObject]@{
        Name = "Discord"
        Version = $version
        Path = $found.FullName
        Type = "Communication"
    }
}

# Skype
$skypePaths = @(
    "$env:LOCALAPPDATA\Microsoft\Skype for Desktop\Skype.exe",
    "$env:ProgramFiles\Microsoft\Skype for Desktop\Skype.exe",
    "$env:ProgramFiles (x86)\Microsoft\Skype for Desktop\Skype.exe"
)
foreach ($path in $skypePaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Skype"
            Version = $version
            Path = $path
            Type = "Communication"
        }
        break
    }
}
