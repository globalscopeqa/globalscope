# Video inbox

New videos waiting for Claude. They arrive here from `sync-media.ps1` on the user's PC (`Media\Inbox`).
Claude processes them one at a time, oldest first, with the `social-video-kit` skill. Finished files go to
`media/<slug>/`, the video is removed from this folder, and `media/video-tracker.xlsx` is rebuilt.
