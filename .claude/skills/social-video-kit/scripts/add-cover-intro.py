#!/usr/bin/env python3
"""Prepend the 1:1 cover to a vertical video as a 1-second intro.

usage: add-cover-intro.py IN.mp4 COVER.png OUT.mp4 [--seconds 1]
The square cover is centred, full width, on a blurred and darkened copy of itself
that fills the frame; the original audio starts after the intro (silence under it).
"""
import argparse, json, subprocess


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-of", "json", path])
    return json.loads(out)["streams"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("cover"); ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=1.0)
    a = ap.parse_args()
    streams = probe(a.src)
    v = next(s for s in streams if s["codec_type"] == "video")
    au = next((s for s in streams if s["codec_type"] == "audio"), None)
    W, H = int(v["width"]), int(v["height"])
    num, den = map(int, v["r_frame_rate"].split("/"))
    fps = num / den
    d = a.seconds

    intro = (f"[1:v]loop=loop=-1:size=1:start=0,trim=duration={d},setpts=PTS-STARTPTS,split[c1][c2];"
             f"[c1]scale={H}:{H},crop={W}:{H},boxblur=30:2,eq=brightness=-0.25[bg];"
             f"[c2]scale={W}:{W}[fg];"
             f"[bg][fg]overlay=0:({H}-{W})/2,fps={fps},format=yuv420p,setsar=1[iv];"
             f"[0:v]fps={fps},format=yuv420p,setsar=1[mv];")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", a.src, "-loop", "1", "-i", a.cover]
    if au:
        rate = au.get("sample_rate", "44100")
        layout = au.get("channel_layout") or ("stereo" if int(au.get("channels", 2)) == 2 else "mono")
        cmd += ["-f", "lavfi", "-t", str(d), "-i", f"anullsrc=r={rate}:cl={layout}"]
        fc = intro + f"[0:a]aformat=sample_rates={rate}:channel_layouts={layout}[ma];[iv][2:a][mv][ma]concat=n=2:v=1:a=1[v][a]"
        maps = ["-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
    else:
        fc = intro + "[iv][mv]concat=n=2:v=1:a=0[v]"
        maps = ["-map", "[v]"]
    # cap at the input's video bitrate so the file stays about the size of the source
    br = int(v.get("bit_rate") or 0) or 8_000_000
    cmd += ["-filter_complex", fc, *maps, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-maxrate", str(int(br * 1.1)), "-bufsize", str(br * 2), "-movflags", "+faststart", a.out]
    subprocess.check_call(cmd)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
