# Portable & Script-Based Tools Detector
# Detects tools that run via batch files, shell scripts, or jar files

$ErrorActionPreference = "SilentlyContinue"

# Common portable tool patterns
$portablePatterns = @(
    # Eclipse (often portable)
    @{
        Patterns = @(
            "$env:USERPROFILE\eclipse\eclipse.exe",
            "$env:USERPROFILE\Downloads\eclipse\eclipse.exe",
            "C:\eclipse\eclipse.exe",
            "D:\eclipse\eclipse.exe"
        )
        Name = "Eclipse IDE (Portable)"
        Type = "IDE"
    },
    # NetBeans (portable)
    @{
        Patterns = @(
            "$env:USERPROFILE\netbeans\bin\netbeans64.exe",
            "$env:USERPROFILE\netbeans\bin\netbeans.exe",
            "C:\netbeans\bin\netbeans64.exe"
        )
        Name = "NetBeans IDE (Portable)"
        Type = "IDE"
    },
    # Tomcat (batch file)
    @{
        Patterns = @(
            "$env:USERPROFILE\apache-tomcat*\bin\startup.bat",
            "C:\apache-tomcat*\bin\startup.bat",
            "C:\tomcat*\bin\startup.bat"
        )
        Name = "Apache Tomcat"
        Type = "Server"
    },
    # WildFly/JBoss (batch file)
    @{
        Patterns = @(
            "$env:USERPROFILE\wildfly*\bin\standalone.bat",
            "C:\wildfly*\bin\standalone.bat",
            "C:\jboss*\bin\standalone.bat"
        )
        Name = "WildFly/JBoss"
        Type = "Server"
    }
)

foreach ($tool in $portablePatterns) {
    $found = $false
    foreach ($pattern in $tool.Patterns) {
        $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($matches) {
            $version = "Unknown"
            
            # Try to get version from file
            if ($matches.Extension -eq ".exe") {
                $version = $matches.VersionInfo.FileVersion
                if (-not $version) { $version = $matches.VersionInfo.ProductVersion }
            }
            
            # Try to extract version from path
            if ($version -eq "Unknown" -and $matches.FullName -match '(\d+\.\d+(?:\.\d+)?)') {
                $version = $matches[1]
            }
            
            [PSCustomObject]@{
                Name = $tool.Name
                Version = $version
                Path = $matches.FullName
                Type = $tool.Type
            }
            $found = $true
            break
        }
    }
    if ($found) { break }
}

# Check for JAR-based tools with launcher scripts
$jarTools = @(
    # Burp Suite
    @{
        Patterns = @(
            "$env:USERPROFILE\BurpSuite*\*.jar",
            "$env:USERPROFILE\Downloads\burp*.jar"
        )
        Name = "Burp Suite"
        Type = "Security Tool"
    },
    # JMeter
    @{
        Patterns = @(
            "$env:USERPROFILE\apache-jmeter*\bin\jmeter.bat",
            "C:\apache-jmeter*\bin\jmeter.bat"
        )
        Name = "Apache JMeter"
        Type = "Testing Tool"
    }
)

foreach ($tool in $jarTools) {
    foreach ($pattern in $tool.Patterns) {
        $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($matches) {
            $version = "Unknown"
            
            # Try to extract version from filename or path
            if ($matches.Name -match '(\d+\.\d+(?:\.\d+)?)') {
                $version = $matches[1]
            } elseif ($matches.Directory.Name -match '(\d+\.\d+(?:\.\d+)?)') {
                $version = $matches[1]
            }
            
            [PSCustomObject]@{
                Name = $tool.Name
                Version = $version
                Path = $matches.FullName
                Type = $tool.Type
            }
            break
        }
    }
}
