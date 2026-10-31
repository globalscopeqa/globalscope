# Global Scope media sync: run on your PC in PowerShell.
#   1. Uploads new videos from  <Media>\Inbox  to GitHub (inbox/), for Claude to process one by one.
#   2. Downloads everything finished (media/: videos, covers, thumbnails, captions, video-tracker.xlsx) into <Media>.
#
# Usage:  powershell -ExecutionPolicy Bypass -File sync-media.ps1
# Optional: put a .txt with the same name next to a video (e.g. myvideo.mp4 + myvideo.txt) holding its
# title on the first line and your post description below; Claude uses it for the caption.
# Needs Git for Windows (https://git-scm.com/download/win); the first push asks you to sign in to GitHub.

param(
  [string]$Media = "C:\Users\Dell\OneDrive\Documents\Projects\Media",
  [string]$Branch = "ccr-bae6bdbf-qv17eb"
)
$ErrorActionPreference = "Stop"
$repo = Join-Path $env:USERPROFILE ".gs-media-sync"
$inbox = Join-Path $Media "Inbox"
$uploaded = Join-Path $inbox "Uploaded"
New-Item -ItemType Directory -Force -Path $inbox, $uploaded | Out-Null

# 1. get the latest copy of the repo (this folder is only a sync mirror, so it is safe to reset)
if (Test-Path (Join-Path $repo ".git")) {
  git -C $repo fetch origin $Branch
  git -C $repo checkout -q $Branch
  git -C $repo reset -q --hard "origin/$Branch"
} else {
  git clone --branch $Branch --single-branch https://github.com/globalscopeqa/globalscope.git $repo
}

# 2. upload new videos (GitHub rejects files over 100 MB)
$videos = Get-ChildItem -Path $inbox -File | Where-Object { $_.Extension -in ".mp4", ".mov", ".m4v" }
$sent = @()
foreach ($v in $videos) {
  if ($v.Length -gt 95MB) { Write-Warning "$($v.Name) is over 95 MB; GitHub can't take it. Compress it or send it in chat."; continue }
  New-Item -ItemType Directory -Force -Path (Join-Path $repo "inbox") | Out-Null
  Copy-Item $v.FullName (Join-Path $repo "inbox")
  $txt = [IO.Path]::ChangeExtension($v.FullName, ".txt")
  if (Test-Path $txt) { Copy-Item $txt (Join-Path $repo "inbox") }
  $sent += $v
}
if ($sent.Count -gt 0) {
  git -C $repo add inbox
  git -C $repo commit -q -m "Add $($sent.Count) video(s) to inbox"
  git -C $repo push -q origin $Branch
  foreach ($v in $sent) {
    Move-Item -Force $v.FullName $uploaded
    $txt = [IO.Path]::ChangeExtension($v.FullName, ".txt")
    if (Test-Path $txt) { Move-Item -Force $txt $uploaded }
  }
  Write-Host "Uploaded $($sent.Count) video(s). Ask Claude to 'process the inbox'." -ForegroundColor Green
} else {
  Write-Host "No new videos in $inbox."
}

# 3. download finished work (robocopy exit codes below 8 mean success)
robocopy (Join-Path $repo "media") $Media /E /NFL /NDL /NJH /NJS | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Download failed (robocopy code $LASTEXITCODE)" }
Write-Host "Finished files are in $Media (see video-tracker.xlsx)." -ForegroundColor Green
