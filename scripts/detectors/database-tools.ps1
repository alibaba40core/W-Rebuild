# Database Tools Detector (MongoDB, MySQL, PostgreSQL clients)

$ErrorActionPreference = "SilentlyContinue"

# MongoDB Compass
$compassPaths = @(
    "$env:LOCALAPPDATA\MongoDBCompass\MongoDBCompass.exe",
    "$env:ProgramFiles\MongoDB\Compass\MongoDBCompass.exe"
)
foreach ($path in $compassPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        if (-not $version) { $version = (Get-Item $path).VersionInfo.ProductVersion }
        
        [PSCustomObject]@{
            Name = "MongoDB Compass"
            Version = $version
            Path = $path
            Type = "Database Tool"
        }
        break
    }
}

# MySQL Workbench
$mysqlPatterns = @(
    "$env:ProgramFiles\MySQL\MySQL Workbench*\MySQLWorkbench.exe"
)
foreach ($pattern in $mysqlPatterns) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $version = $found.VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "MySQL Workbench"
            Version = $version
            Path = $found.FullName
            Type = "Database Tool"
        }
        break
    }
}

# pgAdmin
$pgAdminPatterns = @(
    "$env:ProgramFiles\pgAdmin*\runtime\pgAdmin4.exe"
)
foreach ($pattern in $pgAdminPatterns) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $version = $found.VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "pgAdmin"
            Version = $version
            Path = $found.FullName
            Type = "Database Tool"
        }
        break
    }
}

# DBeaver
$dbeaverPaths = @(
    "$env:ProgramFiles\DBeaver\dbeaver.exe",
    "$env:LOCALAPPDATA\DBeaver\dbeaver.exe"
)
foreach ($path in $dbeaverPaths) {
    if (Test-Path $path) {
        $version = (Get-Item $path).VersionInfo.FileVersion
        
        [PSCustomObject]@{
            Name = "DBeaver"
            Version = $version
            Path = $path
            Type = "Database Tool"
        }
        break
    }
}
