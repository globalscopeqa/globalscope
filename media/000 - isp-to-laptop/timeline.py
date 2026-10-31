import json, subprocess
d = json.load(open("words.json"))
LEAD, GAP, TAIL = 0.4, 0.45, 3.2
t = LEAD; scenes = []; words = []
for i in range(7):
    dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"s{i}.mp3"]))
    scenes.append({"start": t, "dur": dur})
    for w in d["words"][i]: words.append({"w": w["w"], "s": t + w["s"], "e": t + w["s"] + w["d"], "scene": i})
    t += dur + GAP
total = t - GAP + TAIL
json.dump({"scenes": scenes, "words": words, "total": total}, open("timeline.json","w"))
# concat narration with delays
inp = []; flt = []
for i, s in enumerate(scenes):
    inp += ["-i", f"s{i}.mp3"]; ms = int(s["start"]*1000)
    flt.append(f"[{i}:a]adelay={ms}|{ms},aresample=44100[a{i}]")
flt.append("".join(f"[a{i}]" for i in range(7)) + f"amix=inputs=7:normalize=0,apad=whole_dur={total}[v]")
subprocess.check_call(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(flt),"-map","[v]","-ac","2","voice.wav"])
print(total)
