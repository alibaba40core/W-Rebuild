# Text Editors Detector (Notepad++, Sublime Text, Atom, etc.)

$ErrorActionPreference = "SilentlyContinue"

# Notepad++
$notepadPaths = @(
    "$env:ProgramFiles\Notepad++\notepad++.exe",
    "$env:ProgramFiles (x86)\Notepad++\notepad++.exe"
)
foreach ($path in $notepadPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Notepad++"
            Version = $version
            Path = $path
            Type = "Editor"
        }
        break
    }
}

# Sublime Text
$sublimePaths = @(
    "$env:ProgramFiles\Sublime Text\sublime_text.exe",
    "$env:ProgramFiles\Sublime Text 3\sublime_text.exe",
    "$env:ProgramFiles\Sublime Text 4\sublime_text.exe"
)
foreach ($path in $sublimePaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Sublime Text"
            Version = $version
            Path = $path
            Type = "Editor"
        }
        break
    }
}

# Atom
$atomPath = "$env:LOCALAPPDATA\atom\atom.exe"
if (Test-Path $atomPath) {
    $version = (Get-Item $atomPath).VersionInfo.FileVersion
    
    [PSCustomObject]@{
        Name = "Atom"
        Version = $version
        Path = $atomPath
        Type = "Editor"
    }
}

# Vim (GVim for Windows)
$vimPaths = @(
    "$env:ProgramFiles\Vim\*\gvim.exe",
    "$env:ProgramFiles (x86)\Vim\*\gvim.exe"
)
foreach ($pattern in $vimPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $version = $found.VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "Vim (GVim)"
            Version = $version
            Path = $found.FullName
            Type = "Editor"
        }
        break
    }
}
