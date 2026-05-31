$user = $env:USERPROFILE
$folders = @('Downloads','Documents','Videos','Pictures','Music','Desktop')
$results = @()
foreach ($f in $folders) {
    $p = Join-Path $user $f
    if (Test-Path $p) {
        $s = (Get-ChildItem $p -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $results += [PSCustomObject]@{
            Path = $p
            Folder = $f
            SizeGB = [math]::Round($s/1GB,2)
        }
    }
}
$results | Sort-Object SizeGB -Descending | Format-Table -AutoSize
