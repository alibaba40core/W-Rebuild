# Java (JDK/JRE) Detector

$ErrorActionPreference = "SilentlyContinue"

$javaPaths = @()
$pathDirs = $env:PATH -split ";"

# Check JAVA_HOME
if ($env:JAVA_HOME -and (Test-Path "$env:JAVA_HOME\bin\java.exe")) {
    $javaPaths += "$env:JAVA_HOME\bin\java.exe"
}

# Check PATH
foreach ($dir in $pathDirs) {
    $javaExe = Join-Path $dir "java.exe"
    if (Test-Path $javaExe) {
        $javaPaths += $javaExe
    }
}

# Check common locations
$commonJavaPaths = @(
    "$env:ProgramFiles\Java\*\bin\java.exe",
    "$env:ProgramFiles\Eclipse Adoptium\*\bin\java.exe",
    "$env:ProgramFiles\Microsoft\*\bin\java.exe",
    "$env:ProgramFiles\Amazon Corretto\*\bin\java.exe"
)

foreach ($pattern in $commonJavaPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($item in $found) {
        $javaPaths += $item.FullName
    }
}

$uniqueJavas = $javaPaths | Select-Object -Unique

foreach ($javaPath in $uniqueJavas) {
    $versionOutput = & $javaPath -version 2>&1
    if ($versionOutput -match 'version "(.+?)"' -or $versionOutput -match 'openjdk version "(.+?)"') {
        $version = $matches[1]
        $javaHome = Split-Path -Parent (Split-Path -Parent $javaPath)
        $isJDK = Test-Path (Join-Path $javaHome "bin\javac.exe")
        $name = if ($isJDK) { "Java JDK" } else { "Java JRE" }
        
        [PSCustomObject]@{
            Name = $name
            Version = $version
            Path = $javaPath
            Type = "Runtime"
        }
    }
}
