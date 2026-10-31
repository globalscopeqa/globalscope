#!/usr/bin/env python3
"""Replace the round bottom-right badge of a 720x1280 explainer video with the Global Scope badge.

usage: swap-logo.py IN.mp4 OUT.mp4 --logo globalscope-logo.png [--center X Y --radius R]
Writes OUT-check.png with crops from 5 moments for visual verification.
"""
import argparse, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw


def frame(video, t, path):
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", path])
    return Image.open(path).convert("RGB")


def detect(im):
    """Find the white circle in the bottom-right corner: the longest vertical white run gives centre y and radius."""
    im = im.convert("L")
    W, H = im.size
    best = None
    for x in range(int(W * 0.7), W - 4, 2):
        ys = [y for y in range(int(H * 0.8), H) if im.getpixel((x, y)) > 235]
        if ys and (best is None or ys[-1] - ys[0] > best[1]):
            best = (x, ys[-1] - ys[0], ys[0], ys[-1])
    if not best or best[1] < 80:
        return None
    cy = (best[2] + best[3]) // 2
    xs = [x for x in range(int(W * 0.6), W) if im.getpixel((x, cy)) > 235]
    cx = (xs[0] + xs[-1]) // 2
    r = max(best[1], xs[-1] - xs[0]) // 2
    return cx, cy, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--logo", required=True)
    ap.add_argument("--center", nargs=2, type=int)
    ap.add_argument("--radius", type=int)
    a = ap.parse_args()
    tmp = tempfile.mkdtemp()
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.src]))
    W, H = frame(a.src, 1, f"{tmp}/w.png").size

    if a.center:
        cx, cy = a.center; r = a.radius or 86
    else:
        found = [detect(frame(a.src, t, f"{tmp}/d.png")) for t in (1, dur * 0.4, dur * 0.8)]
        found = [f for f in found if f]
        if not found:
            sys.exit("No badge found; pass --center X Y --radius R")
        cx = sorted(f[0] for f in found)[len(found) // 2]
        cy = sorted(f[1] for f in found)[len(found) // 2]
        r = sorted(f[2] for f in found)[len(found) // 2]
    print(f"badge centre=({cx},{cy}) radius={r}")

    # overlay: grey ring + white disc slightly larger than the detected badge, logo centred
    K = 4
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    for R, col in ((r + 7, (205, 210, 218, 255)), (r + 2, (255, 255, 255, 255))):
        d.ellipse([(cx - R) * K, (cy - R) * K, (cx + R) * K, (cy + R) * K], fill=col)
    ov = big.resize((W, H), Image.LANCZOS)
    logo = Image.open(a.logo).convert("RGBA")
    lw = int(r * 1.66); lh = round(lw * logo.height / logo.width)
    ov.alpha_composite(logo.resize((lw, lh), Image.LANCZOS), (cx - lw // 2, cy - lh // 2))
    ov.save(f"{tmp}/badge.png")

    # keep the file about the size of the source: high quality, but capped at the source's video bitrate
    br = int(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=bit_rate",
                                      "-of", "csv=p=0", a.src]).strip() or 0) or 8_000_000
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-i", f"{tmp}/badge.png",
                           "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
                           "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-maxrate", str(int(br * 1.1)), "-bufsize", str(br * 2),
                           "-c:a", "copy", "-movflags", "+faststart", a.out])

    # verification sheet
    S = 2 * r + 60; x0 = max(0, min(W - S, cx - S // 2)); y0 = max(0, min(H - S, cy - S // 2))
    crops = [frame(a.out, t, f"{tmp}/c{i}.png").convert("RGB").crop((x0, y0, x0 + S, y0 + S))
             for i, t in enumerate((0.5, dur * 0.25, dur * 0.5, dur * 0.75, dur - 0.5))]
    sheet = Image.new("RGB", (S * len(crops), S))
    for i, c in enumerate(crops): sheet.paste(c, (i * S, 0))
    check = os.path.splitext(a.out)[0] + "-check.png"
    sheet.save(check); print("check image:", check)


if __name__ == "__main__":
    main()
