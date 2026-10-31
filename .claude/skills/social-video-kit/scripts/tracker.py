#!/usr/bin/env python3
"""Rebuild media/video-tracker.xlsx from media/videos.json, the files in media/<slug>/ and inbox/.

usage: tracker.py [REPO_ROOT]
Deliverable columns are Yes/No from what actually exists on disk; Status is an Excel formula.
Videos still waiting in inbox/ are listed as "In inbox".
"""
import glob, json, os, subprocess, sys
from urllib.parse import quote
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "../../../.."))
BRANCH = "ccr-bae6bdbf-qv17eb"
GH = f"https://github.com/globalscopeqa/globalscope/tree/{BRANCH}"
FONT = "Arial"


def duration(path):
    try:
        return round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])), 1)
    except Exception:
        return None


def has(folder, pattern):
    return "Yes" if glob.glob(os.path.join(folder, pattern)) else "No"


reg = sorted(json.load(open(os.path.join(ROOT, "media/videos.json"))), key=lambda v: v.get("num", 9999))
rows = []
for v in reg:
    folder = v.get("folder", v["slug"])
    d = os.path.join(ROOT, "media", folder)
    vid = os.path.join(d, v["video"])
    rows.append([v.get("num", ""), folder, v["title"], v["source"], v["received"], v.get("completed", ""),
                 duration(vid) if os.path.exists(vid) else None,
                 "Yes" if os.path.exists(vid) else "No",
                 "Yes" if v.get("intro") else "No",
                 has(d, "*cover-1x1.png"), has(d, "*yt-short-thumbnail*.png"), has(d, "*caption*.txt"),
                 v.get("notes", ""), f"{GH}/media/{quote(folder)}"])
known = {os.path.basename(v["source"]) for v in reg}
for f in sorted(glob.glob(os.path.join(ROOT, "inbox", "*.mp4")), key=os.path.getmtime):
    if os.path.basename(f) in known:
        continue
    rows.append(["", "", os.path.splitext(os.path.basename(f))[0], os.path.basename(f), "", "", duration(f),
                 "No", "No", "No", "No", "No", "Waiting in inbox", f"{GH}/inbox"])

wb = Workbook()
ws = wb.active; ws.title = "Videos"
head = ["Excel #", "Folder", "Title", "Source file", "Received", "Completed", "Duration (s)", "Video + logo",
        "1 s cover intro", "Cover 1:1 (Instagram)", "YT Short thumbnail 9:16", "Caption", "Status", "Notes", "GitHub folder"]
ws.append(head)
thin = Side(style="thin", color="D0D5DD")
for c in ws[1]:
    c.font = Font(name=FONT, bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F2A44")
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for i, r in enumerate(rows, start=2):
    num, slug, title, src, rec, done, dur, logo, intro, cover, thumb, cap, notes, link = r
    ws.append([f"{num:03d}" if num != "" else "", slug, title, src, rec, done, dur, logo, intro, cover, thumb, cap,
               f'=IF(COUNTIF(H{i}:L{i},"Yes")=5,"Done",IF(B{i}="","In inbox","In progress"))', notes, "Open folder"])
    ws.cell(i, 15).hyperlink = link; ws.cell(i, 15).font = Font(name=FONT, color="0563C1", underline="single")
    for c in ws[i]:
        if c.column != 15: c.font = Font(name=FONT)
        c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        c.alignment = Alignment(vertical="top", wrap_text=c.column in (3, 4, 14),
                                horizontal="center" if 5 <= c.column <= 13 or c.column == 1 else "left")
    ws.cell(i, 7).number_format = "0.0"
last = max(2, len(rows) + 1)
green, amber, grey = PatternFill("solid", fgColor="D1FADF"), PatternFill("solid", fgColor="FEF0C7"), PatternFill("solid", fgColor="EAECF0")
ws.conditional_formatting.add(f"H2:L{last}", FormulaRule(formula=['H2="Yes"'], fill=green))
ws.conditional_formatting.add(f"H2:L{last}", FormulaRule(formula=['H2="No"'], fill=amber))
ws.conditional_formatting.add(f"M2:M{last}", FormulaRule(formula=['M2="Done"'], fill=green, font=Font(name=FONT, bold=True, color="067647")))
ws.conditional_formatting.add(f"M2:M{last}", FormulaRule(formula=['M2="In progress"'], fill=amber, font=Font(name=FONT, bold=True)))
ws.conditional_formatting.add(f"M2:M{last}", FormulaRule(formula=['M2="In inbox"'], fill=grey, font=Font(name=FONT, bold=True)))
dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"H2:L{last}")
for col, w in zip("ABCDEFGHIJKLMNO", [8, 30, 46, 40, 12, 12, 11, 11, 11, 13, 14, 10, 13, 40, 14]):
    ws.column_dimensions[col].width = w
ws.row_dimensions[1].height = 32
ws.freeze_panes = "C2"; ws.auto_filter.ref = f"A1:O{last}"

s = wb.create_sheet("Summary")
s["A1"] = "Global Scope video pipeline"; s["A1"].font = Font(name=FONT, bold=True, size=14)
items = [("Total videos", f'=COUNTA(Videos!C2:C{last})'), ("Done", f'=COUNTIF(Videos!M2:M{last},"Done")'),
         ("In progress", f'=COUNTIF(Videos!M2:M{last},"In progress")'), ("Waiting in inbox", f'=COUNTIF(Videos!M2:M{last},"In inbox")'),
         ("Total runtime (s)", f'=SUM(Videos!G2:G{last})')]
for k, (label, f) in enumerate(items, start=3):
    s.cell(k, 1, label).font = Font(name=FONT, bold=True); s.cell(k, 2, f).font = Font(name=FONT)
s["A10"] = "How this file works"; s["A10"].font = Font(name=FONT, bold=True)
notes = ["Rebuilt automatically by Claude after each video is processed; edits made here are overwritten.",
         "Yes/No columns reflect which files exist in the video's GitHub folder.",
         "Status is a formula: Done when all five deliverables are Yes.",
         "New videos: put them in Media\\Inbox on your PC and run sync-media.ps1; they appear here as 'In inbox'."]
for k, n in enumerate(notes, start=11):
    s.cell(k, 1, n).font = Font(name=FONT)
s.column_dimensions["A"].width = 26; s.column_dimensions["B"].width = 14

out = os.path.join(ROOT, "media/video-tracker.xlsx"); wb.save(out); print("wrote", out, f"({len(rows)} rows)")
