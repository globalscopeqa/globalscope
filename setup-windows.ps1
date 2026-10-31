# One-time setup so Claude Code can run the social-video-kit locally on this Windows PC.
# Run from the repo folder in PowerShell:  powershell -ExecutionPolicy Bypass -File setup-windows.ps1
# Installs: Git, Python, Node.js, FFmpeg (via winget), Pillow + openpyxl, Playwright + Chromium,
# and the Inter + JetBrains Mono fonts. It also creates Media\Inbox. Safe to re-run.

param([string]$Media = "C:\Users\Dell\OneDrive\Documents\Projects\Media")
$ErrorActionPreference = "Stop"
$repo = $PSScriptRoot
$scripts = Join-Path $repo ".claude\skills\social-video-kit\scripts"

Write-Host "1/5 Tools (Git, Python, Node.js, FFmpeg)" -ForegroundColor Cyan
foreach ($id in "Git.Git", "Python.Python.3.12", "OpenJS.NodeJS.LTS", "Gyan.FFmpeg") {
  winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements | Out-Null
}
# pick up PATH changes from the installs without reopening the terminal
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "2/5 Python packages" -ForegroundColor Cyan
python -m pip install --quiet --upgrade pillow openpyxl

Write-Host "3/5 Playwright + Chromium (for covers and thumbnails)" -ForegroundColor Cyan
Push-Location $scripts
npm install --silent --no-save playwright
npx playwright install chromium
Pop-Location

Write-Host "4/5 Fonts (Inter, JetBrains Mono)" -ForegroundColor Cyan
$tmp = Join-Path $env:TEMP "gs-fonts"; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$zips = @{
  "inter.zip" = "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"
  "jbmono.zip" = "https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip"
}
$fontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"; New-Item -ItemType Directory -Force -Path $fontDir | Out-Null
$reg = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
foreach ($z in $zips.Keys) {
  $zip = Join-Path $tmp $z
  Invoke-WebRequest $zips[$z] -OutFile $zip
  Expand-Archive -Force $zip (Join-Path $tmp ($z -replace ".zip", ""))
}
Get-ChildItem $tmp -Recurse -Include "Inter-*.ttf", "JetBrainsMono-*.ttf" | Where-Object { $_.FullName -notmatch "variable|Variable|webfonts|NL" } | ForEach-Object {
  $dest = Join-Path $fontDir $_.Name
  Copy-Item -Force $_.FullName $dest
  New-ItemProperty -Path $reg -Name ($_.BaseName + " (TrueType)") -Value $dest -PropertyType String -Force | Out-Null
}

Write-Host "5/5 Media folders" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path (Join-Path $Media "Inbox"), (Join-Path $Media "Inbox\Uploaded") | Out-Null

Write-Host "`nChecks:" -ForegroundColor Cyan
ffmpeg -version | Select-Object -First 1
python -c "import PIL, openpyxl; print('Pillow', PIL.__version__, '/ openpyxl', openpyxl.__version__)"
node -e "require('$($scripts -replace '\\','/')/node_modules/playwright'); console.log('Playwright OK')"
Write-Host "`nDone. Open this folder in Claude Code and say: process the inbox" -ForegroundColor Green
