import asyncio, json, sys, edge_tts
SCENES = [
 "Your laptop loads a web page in milliseconds. But how does the internet actually reach your desk?",
 "It begins outside the building. Your provider's fibre arrives as pulses of light, landing at the demarcation point, where their network ends and yours begins.",
 "Next comes the edge router and firewall. Every packet is inspected, filtered and routed here, so threats are blocked before they ever reach a user.",
 "Clean traffic flows into the core switch, the backbone of the network, moving data between floors and servers at ten gigabits or more.",
 "Structured cabling carries it to access switches on every floor, which also power phones, cameras and access points over the same cable.",
 "The access point turns that signal back into radio waves, and your laptop joins securely over Wi-Fi.",
 "From ISP to laptop, every hop is designed, secured and managed. That's what we build at Global Scope.",
]
async def main(out):
    words, t_off = [], 0.0
    audio = bytearray(); scenes = []
    for i, text in enumerate(SCENES):
        c = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="+4%", boundary="WordBoundary")
        chunk = bytearray(); sw = []
        async for m in c.stream():
            if m["type"] == "audio": chunk += m["data"]
            elif m["type"] == "WordBoundary":
                sw.append({"w": m["text"], "s": m["offset"]/1e7, "d": m["duration"]/1e7, "scene": i})
        open(f"{out}/s{i}.mp3","wb").write(chunk)
        words.append(sw)
    json.dump({"scenes": SCENES, "words": words}, open(f"{out}/words.json","w"), indent=1)
asyncio.run(main(sys.argv[1]))
