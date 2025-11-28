# JetBrains Tools Detector
# Detects all JetBrains IDEs using JetBrains Toolbox and direct installations

$ErrorActionPreference = "SilentlyContinue"

# JetBrains Toolbox installations
$toolboxBase = "$env:LOCALAPPDATA\JetBrains\Toolbox\apps"
if (Test-Path $toolboxBase) {
    $jetBrainsApps = @{
        "IDEA-U" = "IntelliJ IDEA Ultimate"
        "IDEA-C" = "IntelliJ IDEA Community"
        "PyCharm-P" = "PyCharm Professional"
        "PyCharm-C" = "PyCharm Community"
        "WebStorm" = "WebStorm"
        "PhpStorm" = "PhpStorm"
        "Rider" = "Rider"
        "CLion" = "CLion"
        "GoLand" = "GoLand"
        "DataGrip" = "DataGrip"
        "RubyMine" = "RubyMine"
        "AppCode" = "AppCode"
        "RustRover" = "RustRover"
    }
    
    foreach ($appKey in $jetBrainsApps.Keys) {
        $appPath = Join-Path $toolboxBase $appKey
        if (Test-Path $appPath) {
            # Find latest version
            $versions = Get-ChildItem -Path $appPath -Directory | Sort-Object Name -Descending
            foreach ($ver in $versions) {
                $exeName = $appKey.ToLower() -replace '-.*', ''
                if ($appKey -eq "IDEA-U" -or $appKey -eq "IDEA-C") { $exeName = "idea64" }
                if ($appKey -eq "PyCharm-P" -or $appKey -eq "PyCharm-C") { $exeName = "pycharm64" }
                
                $exePath = Get-ChildItem -Path $ver.FullName -Filter "$exeName*.exe" -Recurse -Depth 2 -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($exePath) {
                    [PSCustomObject]@{
                        Name = $jetBrainsApps[$appKey]
                        Version = $ver.Name
                        Path = $exePath.FullName
                        Type = "IDE"
                    }
                    break
                }
            }
        }
    }
}

# Direct installations
$directPaths = @(
    @{Pattern = "$env:ProgramFiles\JetBrains\IntelliJ IDEA*\bin\idea64.exe"; Name = "IntelliJ IDEA"},
    @{Pattern = "$env:ProgramFiles\JetBrains\PyCharm*\bin\pycharm64.exe"; Name = "PyCharm"},
    @{Pattern = "$env:ProgramFiles\JetBrains\WebStorm*\bin\webstorm64.exe"; Name = "WebStorm"},
    @{Pattern = "$env:ProgramFiles\JetBrains\PhpStorm*\bin\phpstorm64.exe"; Name = "PhpStorm"},
    @{Pattern = "$env:ProgramFiles\JetBrains\Rider*\bin\rider64.exe"; Name = "Rider"},
    @{Pattern = "$env:ProgramFiles\JetBrains\CLion*\bin\clion64.exe"; Name = "CLion"},
    @{Pattern = "$env:ProgramFiles\JetBrains\GoLand*\bin\goland64.exe"; Name = "GoLand"},
    @{Pattern = "$env:ProgramFiles\JetBrains\DataGrip*\bin\datagrip64.exe"; Name = "DataGrip"},
    @{Pattern = "$env:ProgramFiles\JetBrains\RubyMine*\bin\rubymine64.exe"; Name = "RubyMine"}
)

foreach ($tool in $directPaths) {
    $found = Get-ChildItem -Path $tool.Pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $version = $found.VersionInfo.FileVersion
        if (-not $version) { $version = "Unknown" }
        
        [PSCustomObject]@{
            Name = $tool.Name
            Version = $version
            Path = $found.FullName
            Type = "IDE"
        }
    }
}
