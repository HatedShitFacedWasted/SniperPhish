$zip = "C:\Users\RUDEB\Downloads\adb.zip"
$dest = "C:\adb"

# Remove old if exists
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }

# Extract
Expand-Archive -Path $zip -DestinationPath $dest -Force

# Check
$adbExe = Join-Path $dest 'platform-tools\adb.exe'
if (Test-Path $adbExe) {
    Write-Host "ADB installed: $adbExe"
    & $adbExe version
} else {
    Write-Host "Extract failed"
    Get-ChildItem $dest -ErrorAction SilentlyContinue
}
