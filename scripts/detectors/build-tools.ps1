# Build Tools Detector (Maven, Gradle, Ant, etc.)

$ErrorActionPreference = "SilentlyContinue"

# Maven
$mvnPath = (Get-Command mvn -ErrorAction SilentlyContinue).Source
if ($mvnPath) {
    $versionOutput = & mvn --version 2>&1
    if ($versionOutput -match "Apache Maven (\d+\.\d+\.\d+)") {
        $version = $matches[1]
        
        [PSCustomObject]@{
            Name = "Apache Maven"
            Version = $version
            Path = $mvnPath
            Type = "Build Tool"
        }
    }
}

# Gradle
$gradlePath = (Get-Command gradle -ErrorAction SilentlyContinue).Source
if ($gradlePath) {
    $versionOutput = & gradle --version 2>&1
    if ($versionOutput -match "Gradle (\d+\.\d+(?:\.\d+)?)") {
        $version = $matches[1]
        
        [PSCustomObject]@{
            Name = "Gradle"
            Version = $version
            Path = $gradlePath
            Type = "Build Tool"
        }
    }
}

# Ant
$antPath = (Get-Command ant -ErrorAction SilentlyContinue).Source
if ($antPath) {
    $versionOutput = & ant -version 2>&1
    if ($versionOutput -match "Apache Ant\(TM\) version (\d+\.\d+\.\d+)") {
        $version = $matches[1]
        
        [PSCustomObject]@{
            Name = "Apache Ant"
            Version = $version
            Path = $antPath
            Type = "Build Tool"
        }
    }
}

# CMake
$cmakePath = (Get-Command cmake -ErrorAction SilentlyContinue).Source
if ($cmakePath) {
    $versionOutput = & cmake --version 2>&1
    if ($versionOutput -match "cmake version (\d+\.\d+\.\d+)") {
        $version = $matches[1]
        
        [PSCustomObject]@{
            Name = "CMake"
            Version = $version
            Path = $cmakePath
            Type = "Build Tool"
        }
    }
}

# Make (GNU Make)
$makePath = (Get-Command make -ErrorAction SilentlyContinue).Source
if ($makePath) {
    $versionOutput = & make --version 2>&1
    if ($versionOutput -match "GNU Make (\d+\.\d+)") {
        $version = $matches[1]
        
        [PSCustomObject]@{
            Name = "GNU Make"
            Version = $version
            Path = $makePath
            Type = "Build Tool"
        }
    }
}
