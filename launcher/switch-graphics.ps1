# Arkhaven graphics preset switcher. Patches only preset-owned settings.
$ErrorActionPreference = 'Stop'
$app = Split-Path -Parent $MyInvocation.MyCommand.Path
$mc = Join-Path $app 'instances\Arkhaven\.minecraft'
Add-Type -AssemblyName System.Windows.Forms
$ru = (Get-Culture).TwoLetterISOLanguageName -eq 'ru'
$names = if ($ru) { @('Быстро (без шейдеров)', 'Сбалансировано', 'Красиво', 'Максимум') } else { @('Fast (no shaders)', 'Balanced', 'Beautiful', 'Ultra') }
$ids = @('fast', 'balanced', 'beautiful', 'ultra')
$form = New-Object Windows.Forms.Form
$form.Text = if ($ru) { 'Arkhaven — графика' } else { 'Arkhaven — graphics' }
$form.Size = New-Object Drawing.Size(360, 260); $form.StartPosition = 'CenterScreen'; $form.FormBorderStyle = 'FixedDialog'
$form.Icon = New-Object Drawing.Icon (Join-Path $app 'arkhaven.ico')
$cur = if (Test-Path (Join-Path $app 'preset.txt')) { (Get-Content (Join-Path $app 'preset.txt') -Raw).Trim() } else { 'beautiful' }
$radios = @()
for ($i = 0; $i -lt 4; $i++) {
  $r = New-Object Windows.Forms.RadioButton
  $r.Text = $names[$i]; $r.Location = New-Object Drawing.Point(24, (20 + 34 * $i)); $r.Size = New-Object Drawing.Size(300, 28)
  $r.Checked = ($ids[$i] -eq $cur); $form.Controls.Add($r); $radios += $r
}
$ok = New-Object Windows.Forms.Button
$ok.Text = 'OK'; $ok.Location = New-Object Drawing.Point(130, 170); $ok.DialogResult = 'OK'; $form.AcceptButton = $ok; $form.Controls.Add($ok)
if ($form.ShowDialog() -ne 'OK') { exit }
$id = $ids[[array]::IndexOf(($radios | ForEach-Object { $_.Checked }), $true)]
$src = Join-Path $app "presets\$id"
New-Item -ItemType Directory -Force (Join-Path $mc 'config') | Out-Null
Copy-Item (Join-Path $src 'config\iris.properties') (Join-Path $mc 'config\iris.properties') -Force
$java = (Join-Path $app 'java\bin\javaw.exe') -replace '\', '/'
(Get-Content (Join-Path $src 'instance.cfg') -Encoding UTF8) -replace '@JAVA@', $java | Set-Content (Join-Path $app 'instances\Arkhaven\instance.cfg') -Encoding UTF8
$opt = Join-Path $mc 'options.txt'
$preset = @{}; Get-Content (Join-Path $src 'options.txt') -Encoding UTF8 | ForEach-Object { $k, $v = $_ -split ':', 2; $preset[$k] = $v }
$keys = @('renderDistance', 'simulationDistance', 'graphicsMode', 'maxFps')
if (Test-Path $opt) {
  $lines = Get-Content $opt -Encoding UTF8 | ForEach-Object { $k = ($_ -split ':', 2)[0]; if ($keys -contains $k) { "${k}:$($preset[$k])" } else { $_ } }
  $lines | Set-Content $opt -Encoding UTF8
} else { Copy-Item (Join-Path $src 'options.txt') $opt }
Set-Content (Join-Path $app 'preset.txt') $id
[Windows.Forms.MessageBox]::Show($(if ($ru) { "Готово: $($names[[array]::IndexOf($ids, $id)])" } else { "Done: $($names[[array]::IndexOf($ids, $id)])" }), 'Arkhaven') | Out-Null
