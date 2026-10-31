---
name: social-video-kit
description: Global Scope social-media kit for explainer videos. Use whenever the user uploads or names a video and asks to insert/replace the logo, or to generate an Instagram cover photo, a caption ("capcha"), or a YouTube Short thumbnail. Instagram covers are ALWAYS 1:1 (1080×1080); YouTube Short thumbnails are ALWAYS 9:16 (1080×1920).
---

# Global Scope social video kit

House rules for every video request from this user. Follow them without asking again.

## Fixed output formats (user's standing preference)

| Deliverable | Size | File name |
|---|---|---|
| Instagram cover photo | **1:1, 1080×1080 PNG** | `<slug>-cover-1x1.png` |
| YouTube Short thumbnail | **9:16, 1080×1920 PNG** | `<slug>-yt-short-thumbnail.png` |
| Caption ("capcha" = social caption) | text file | `<slug>-caption.txt` |
| Final video: logo swapped **+ 1 s cover intro** | same as source (720×1280 MP4) | `<slug>-globalscope.mp4` |

**Every video gets its 1:1 cover as a 1-second intro** (step 5): always make the cover first, then add it. A "cover" always means the Instagram cover: make the 1:1 one. When they ask for a "thumbnail" or "YT Short", make the 9:16 one. When they ask for both, make both. Never switch sizes unless the user asks for a different size in that request.

## Inbox workflow: process videos one by one

The user keeps new videos in `C:\Users\Dell\OneDrive\Documents\Projects\Media\Inbox` on their Windows PC. Claude can't reach that PC, so `sync-media.ps1` (repo root, run by the user) pushes those videos to `inbox/` on branch `ccr-bae6bdbf-qv17eb`. It also pulls everything in `media/`, including the tracker, back into their `Media` folder.

**Local mode (Claude Code running on the user's Windows PC, in a clone of this repo).** Check with `Test-Path "C:\Users\Dell\OneDrive\Documents\Projects\Media\Inbox"`. If it is there, skip the sync script:
- Take videos straight from `Media\Inbox` (oldest first, one at a time), and move each original to `Media\Inbox\Uploaded` once its video is finished.
- Write the deliverables to `media/<slug>/` in the repo (commit and push: all files are stored on GitHub) **and** copy that folder to `Media\<slug>\`. Copy `media/video-tracker.xlsx` to `Media\` after each rebuild.
- Use `python` instead of `python3`. The tools come from `setup-windows.ps1` (run once): Git, Python, Node.js, FFmpeg, Pillow, openpyxl, Playwright + Chromium, and the Inter / JetBrains Mono fonts. If a tool is missing, ask the user to run that script.
- Paths with spaces need quoting in PowerShell.

**Excel batch mode (the user's main workflow).** The user keeps a posts list `builddatacentres_posts.xlsx` and a folder `video_files` with the videos, both in `C:\Users\Dell\OneDrive\Documents\Projects\Media` (or next to each other wherever the user points). The **last column** of each row holds that post's video file name in `video_files`. The other columns hold the post details (title, description, hashtags…); read the header row to see which is which.
- Process **every row, one video at a time**, in sheet order. Skip rows whose last cell is empty, and report any file name that isn't found in `video_files`.
- For each video, make **its own folder** next to `video_files`, named with a **short topic slug** in lowercase kebab-case describing the subject (e.g. `ai-power-200mw`, `data-centre-go-live`, `inside-a-rack`). **Never** name it after the video file (the user rejected `Video_by_builddatacentres_N`). Use the same slug for the files inside, and record the source file name and Excel row in `media/videos.json` so the tracker maps them. Put all of that video's deliverables in it: the final video (logo + 1 s cover intro), the 1:1 cover, the 9:16 thumbnail and the caption. Write the caption from that row's own title and description, keeping the user's wording, CTA question and hashtags, and adding the Global Scope CTA.
- Don't edit `builddatacentres_posts.xlsx` itself. Progress goes into the tracker (`video-tracker.xlsx`, rebuilt after each video). Also copy each folder to `media/<slug>/` in the repo, then commit and push.
- If a folder for a video already exists with all four deliverables, skip that video (so a re-run continues where it stopped).

When the user says "process the inbox" (or similar), or uploads videos in chat:
1. `git fetch origin ccr-bae6bdbf-qv17eb` and work on that branch, so new inbox files are present.
2. List `inbox/*.mp4|mov|m4v`, oldest first. Process **one video at a time, fully**, before starting the next: steps 1–6 below, then deliver its files.
3. Title and caption source: a same-name `.txt` next to the video, if present, holds the title on its first line and the user's post description after it; otherwise use the file name. Slug: a short kebab-case form of the topic (e.g. `cdu-cooling`).
4. Finish each video: copy its deliverables to `media/<slug>/`, `git rm` the video (and its `.txt`) from `inbox/` (the user keeps the original on their PC in `Inbox\Uploaded`), add an entry to `media/videos.json` (slug, title, source file name, received, completed, video, intro: true, notes), run `python3 .claude/skills/social-video-kit/scripts/tracker.py` to rebuild `media/video-tracker.xlsx`, then commit and push. Only then start the next video.
5. After the last one, tell the user to run `sync-media.ps1` to download everything, and summarise each video in one line.

## Video tracker (Excel)

`media/video-tracker.xlsx` is rebuilt by `scripts/tracker.py` from `media/videos.json` and the files in each `media/<slug>/` folder. The Yes/No columns reflect which files exist, Status is a formula (Done when all five deliverables exist), and videos waiting in `inbox/` show as "In inbox". Never hand-edit the xlsx: change `videos.json` or the files, then re-run the script. Rebuild it whenever any video's files change.

## Where things go

- Work in the session scratchpad: one folder per video.
- **All files are stored on GitHub** (the user's standing instruction): deliver every file with SendUserFile, then copy it to `media/<slug>/` in this repo, commit, and push to the session's branch. When a video is updated, replace the file in place under the same name; git keeps the history. Give the GitHub link `https://github.com/globalscopeqa/globalscope/tree/<branch>/media/<slug>`, because the scratchpad is deleted when the session ends.
- Brand assets: logo `globalscope-logo.png` (repo root, black text on transparent, needs a white backing). Website: globalscope.qa. Brand red `#e0004d`, cyan accent `#3fd8ff`, amber `#ffb547`. Fonts: Inter (headlines) and JetBrains Mono (tags), both installed.

## 1. Insert or replace the logo in a video

The user's explainer videos (720×1280, ~60 s) carry a round white badge in the bottom-right corner. Its position varies slightly per video. The user has confirmed these videos are theirs. If a video carries some other brand's logo, ask whether they own it before replacing.

```sh
python3 -I .claude/skills/social-video-kit/scripts/swap-logo.py <in.mp4> <out.mp4> --logo globalscope-logo.png
```

The script finds the badge (centre and radius) automatically, covers it with a matching white-ringed Global Scope badge for the whole video, copies the audio unchanged, and writes `<out>-check.png` (crops from 5 moments). **Read the check image** and confirm no part of the old logo shows before delivering. If detection fails, or the video has no badge, pass `--center X Y --radius R` explicitly (default spot for a new badge: `--center 636 1191 --radius 86`).

## 2. Pick background frames

```sh
for t in 5 15 25 35 45 55; do ffmpeg -v error -y -ss $t -i video.mp4 -frames:v 1 bg_$t.png; done
ffmpeg -v error -y -i bg_5.png -i bg_15.png -i bg_25.png -i bg_35.png -i bg_45.png -i bg_55.png -filter_complex "hstack=6,scale=1440:-1" sheet.jpg
```

Read the sheet and pick a sharp, dramatic frame with one clear subject (a glowing chip, a hero equipment shot). Avoid blurry transition frames and frames whose built-in labels would collide with the headline. The videos burn in their own subtitles at about y 950–1000 of the 1280-px frame, and the progress diagram and badge sit below that. Crop above y ≈ 930 so they don't leak in.

## 3. Instagram cover photo: 1:1, 1080×1080

```sh
node .claude/skills/social-video-kit/scripts/render-image.js cover <config.json> <out.png>
```

Config (see `examples/cdu-cover.json`):
- `bg`: absolute path of the frame. `sy`: top of the 720×720 square crop; keep `sy + 720 ≤ 930`.
- `tag` (e.g. "DATA CENTRE 101"); headline `lines` (two white, one cyan glowing line); `sub` (one line); `steps` (the path row along the bottom) plus `highlight` (the step to fill).

Layout: tag at top left, round logo badge at top right, headline on the upper half, red rule, subtitle, step row at the bottom, globalscope.qa footer.

## 4. YouTube Short thumbnail: 9:16, 1080×1920

```sh
node .claude/skills/social-video-kit/scripts/render-image.js thumb <config.json> <out.png>
```

Config (see `examples/cdu-thumb.json`):
- `bg`, `zoom` (≈1.42), `sx`, `sy`: crop window of `720/zoom` × `720/zoom·16/9` px; keep its bottom above y ≈ 930.
- `y`: top of the headline block. Keep the headline inside the middle square (y 420–1500) so it survives square crops.
- `tag` with `tagBg`/`tagFg`; two `lines` (the hook: 2–4 heavy words, the second one large and glowing); `sub` pill; "60-SECOND EXPLAINER" footer.

The hook should be short and curiosity-driven, not the full title: "FROM GRID / TO GPU", "HOW AI CHIPS / STAY COOL". Use amber for power/energy topics and cyan for cooling/network topics.

## 5. Add the 1:1 cover as a 1-second intro (always)

```sh
python3 -I .claude/skills/social-video-kit/scripts/add-cover-intro.py <slug>-logo.mp4 <slug>-cover-1x1.png <slug>-globalscope.mp4
```

This prepends a 1-second intro. The square cover sits centred at full width on a blurred, darkened copy of itself that fills the 9:16 frame. The intro is added before the footage, so nothing is hidden, and the original audio starts in sync after it, with silence under the intro. `--seconds N` changes the length, but only when the user asks. Verify by grabbing a frame at 0.5 s and checking the video is exactly 1 s longer than the source. For an audio-sync check, decode the audio to raw PCM rather than using `-ss`, because seek-based volume checks are imprecise.

## 6. Caption ("capcha")

Write `<slug>-caption.txt` with three sections:
1. **INSTAGRAM / TIKTOK / FACEBOOK**: hook question with emojis, a numbered 1️⃣–7️⃣ walk-through of the stages shown in the video, a one-line takeaway, a CTA ("Planning …? DM us or visit globalscope.qa"), and 10–14 hashtags including #Qatar #Doha #GlobalScope.
2. **LINKEDIN**: professional; an opening hook, → bullet stages, why it matters, "At Global Scope we … across Qatar since 2009", a CTA, and 5 hashtags.
3. **YOUTUBE SHORTS TITLE**: `<Question>? (<Topic> in 60s) #shorts`.

Base the stages on what the video actually shows (read frames and on-screen labels). Don't claim services Global Scope may not offer; keep it to "help organisations plan/integrate/manage".

## 7. Always verify before delivering

Read every PNG you render (and the swap-logo check image). Look for text collisions, leaked video subtitles, clipped labels, and the old logo showing. Fix and re-render before sending.
