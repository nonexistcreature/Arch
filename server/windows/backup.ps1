# Arkhaven hourly backup (Windows host): zips the world into C:\Arkhaven\backups, keeps 24 hourly + 7 daily copies
# (fewer if the drive gets below 15 GB free).
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$world = Join-Path $Dir "server\world"
if (-not (Test-Path $world)) { exit }
$stamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$dest = Join-Path $Dir "backups\world_$stamp.zip"
# Copy first so files locked by the running server don't break the archive.
$tmp = Join-Path $env:TEMP "arkhaven_backup"
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
robocopy $world $tmp /E /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
Compress-Archive -Path "$tmp\*" -DestinationPath $dest -Force
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
# Retention: everything from the last 24 h, plus the newest backup of each of the last 7 days.
$all = Get-ChildItem (Join-Path $Dir "backups") -Filter "world_*.zip" | Sort-Object LastWriteTime -Descending
$keep = @{}
$all | Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-24) } | ForEach-Object { $keep[$_.FullName] = $true }
$all | Group-Object { $_.LastWriteTime.Date } | Select-Object -First 7 | ForEach-Object { $keep[$_.Group[0].FullName] = $true }
$all | Where-Object { -not $keep[$_.FullName] } | Remove-Item -Force
# Disk guard: a pre-generated world is gigabytes; keep at least 15 GB free on the drive by dropping the
# oldest backups first, but never the newest 3.
$drive = (Get-Item $Dir).PSDrive
$left = Get-ChildItem (Join-Path $Dir "backups") -Filter "world_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 3
foreach ($old in ($left | Sort-Object LastWriteTime)) {
  if ((Get-PSDrive $drive.Name).Free -ge 15GB) { break }
  Remove-Item $old.FullName -Force
}
