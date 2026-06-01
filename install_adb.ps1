# Search for ADB on the system
$paths = @(
    'C:\Program Files\Android\Android Studio',
    'C:\Program Files (x86)\Android\Android Studio',
    'C:\Users\RUDEB\AppData\Local\Android\Sdk\platform-tools',
    'C:\Users\RUDEB\AppData\Local\Android',
    'C:\adb',
    'D:\adb'
)

$found = $false
foreach ($p in $paths) {
    $adbPath = Join-Path $p 'adb.exe'
    if (Test-Path $adbPath) {
        Write-Host "Found ADB: $adbPath"
        $found = $true
    } elseif (Test-Path $p) {
        Write-Host "Directory exists: $p"
    }
}

if (-not $found) {
    Write-Host "ADB not found. Downloading platform-tools..."
    $url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    $zip = "$env:TEMP\platform-tools.zip"
    $dest = "C:\adb"
    
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $dest -Force
    Remove-Item $zip
    
    $adbExe = Join-Path $dest 'platform-tools\adb.exe'
    if (Test-Path $adbExe) {
        Write-Host "ADB installed to: $adbExe"
        # Add to PATH for this session
        $env:PATH += ";$dest\platform-tools"
        Write-Host "Added to PATH"
    } else {
        Write-Host "Failed to install ADB"
    }
}
