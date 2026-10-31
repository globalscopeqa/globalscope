# Global Scope media sync: run on your PC in PowerShell.
#   1. Uploads builddatacentres_posts.xlsx and every video in <Media>\video_files (plus anything in <Media>\Inbox)
#      to GitHub inbox/, in batches of ~400 MB, for Claude to process one by one.
#      Already-uploaded videos are remembered in <Media>\.uploaded.txt and never sent twice. Your files are not moved.
#   2. Downloads everything finished (one folder per video + video-tracker.xlsx) into <Media>.
#
# Usage:  powershell -ExecutionPolicy Bypass -File sync-media.ps1
# Needs Git for Windows (https://git-scm.com/download/win); the first push asks you to sign in to GitHub.

param(
  [string]$Media = "C:\Users\Dell\OneDrive\Documents\Projects\Media",
  [string]$Branch = "ccr-bae6bdbf-qv17eb",
  [long]$BatchBytes = 400MB
)
$ErrorActionPreference = "Stop"
$repo = Join-Path $env:USERPROFILE ".gs-media-sync"
$log = Join-Path $Media ".uploaded.txt"
$done = @{}; if (Test-Path $log) { Get-Content $log | ForEach-Object { $done[$_] = $true } }

# 1. latest copy of the repo (this folder is only a sync mirror, so resetting it is safe)
if (Test-Path (Join-Path $repo ".git")) {
  git -C $repo fetch origin $Branch
  git -C $repo checkout -q $Branch
  git -C $repo reset -q --hard "origin/$Branch"
} else {
  git clone --branch $Branch --single-branch https://github.com/globalscopeqa/globalscope.git $repo
}
$dest = Join-Path $repo "inbox"; New-Item -ItemType Directory -Force -Path $dest | Out-Null

function Push-Batch($files, $msg) {
  git -C $repo add inbox
  git -C $repo commit -q -m $msg
  git -C $repo push -q origin $Branch
  if ($LASTEXITCODE -ne 0) { throw "Push failed; nothing was marked as uploaded. Re-run the script." }
  $files | ForEach-Object { Add-Content $log $_ }
}

# 2a. the posts spreadsheet (always re-sent so Claude has your latest edits)
$xlsx = Join-Path $Media "builddatacentres_posts.xlsx"
if (Test-Path $xlsx) {
  Copy-Item -Force $xlsx $dest
  git -C $repo add inbox
  git -C $repo diff --cached --quiet
  if ($LASTEXITCODE -ne 0) { git -C $repo commit -q -m "Update builddatacentres_posts.xlsx"; git -C $repo push -q origin $Branch; Write-Host "Uploaded builddatacentres_posts.xlsx" }
} else { Write-Warning "builddatacentres_posts.xlsx not found in $Media" }

# 2b. videos, in batches
$videos = @()
foreach ($dir in (Join-Path $Media "video_files"), (Join-Path $Media "Inbox")) {
  if (Test-Path $dir) { $videos += Get-ChildItem -Path $dir -File | Where-Object { $_.Extension -in ".mp4", ".mov", ".m4v" } }
}
$todo = $videos | Where-Object { -not $done.ContainsKey($_.Name) } | Sort-Object Name
$batch = @(); $size = 0; $sent = 0
foreach ($v in $todo) {
  if ($v.Length -gt 95MB) { Write-Warning "$($v.Name) is over 95 MB; GitHub can't take it. Compress it first."; continue }
  Copy-Item -Force $v.FullName $dest
  $batch += $v.Name; $size += $v.Length
  if ($size -ge $BatchBytes) {
    Push-Batch $batch "Add $($batch.Count) video(s) to inbox"; $sent += $batch.Count
    Write-Host ("Uploaded {0} of {1} videos..." -f $sent, $todo.Count)
    $batch = @(); $size = 0
  }
}
if ($batch.Count -gt 0) { Push-Batch $batch "Add $($batch.Count) video(s) to inbox"; $sent += $batch.Count }
if ($sent -gt 0) { Write-Host "Uploaded $sent new video(s). Tell Claude: the videos are uploaded." -ForegroundColor Green }
else { Write-Host "No new videos to upload." }

# 3. download finished work (robocopy exit codes below 8 mean success)
robocopy (Join-Path $repo "media") $Media /E /NFL /NDL /NJH /NJS | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Download failed (robocopy code $LASTEXITCODE)" }
Write-Host "Finished folders are in $Media (see video-tracker.xlsx)." -ForegroundColor Green
