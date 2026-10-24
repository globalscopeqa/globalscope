# From ISP to Laptop: vertical explainer video

A 63-second 720×1280 explainer video (`globalscope-isp-to-laptop.mp4`) for Reels, Shorts and TikTok.
It follows the internet's path from the provider's fibre to a user's laptop:
ISP fibre and demarc, router and firewall, core switch, access layer and PoE, Wi-Fi, device.

## Rebuild

```sh
python3 -m venv venv && ./venv/bin/pip install edge-tts
./venv/bin/python tts.py .     # narration s0..s6.mp3 + words.json (voice: en-GB-RyanNeural)
python3 timeline.py            # timeline.json + voice.wav
# ambient pad + mix → mix.wav (see ffmpeg commands in commit history / session)
node render.js "$PWD" "$PWD/globalscope-isp-to-laptop.mp4"   # Playwright renders render.html frame by frame
```

Edit the narration in `tts.py` (`SCENES`) and the visuals in `render.html` (`SCENES`, `TITLES`).
