$folders = @('Program Files','Program Files (x86)','Windows','Users','ProgramData')
$results = @()
foreach ($f in $folders) {
    $p = Join-Path 'C:\' $f
    if (Test-Path $p) {
        $size = (Get-ChildItem $p -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $results += [PSCustomObject]@{
            Folder = $f
            SizeGB = [math]::Round($size/1GB,2)
        }
    }
}
$results | Sort-Object SizeGB -Descending | Format-Table -AutoSize
