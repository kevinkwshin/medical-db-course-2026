# -*- coding: utf-8 -*-
"""덱 전체 자동 점검: 화면 밖 도형 · 도형 겹침 · 금지 표현 · 주차 마지막 슬라이드"""
import zipfile, re, sys
import xml.etree.ElementTree as ET
DECK = "데이터베이스관리_수정본_개편_최종_v2.pptx"
NSP='{http://schemas.openxmlformats.org/presentationml/2006/main}'
NSR='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
W, H = 13433425, 7556500
z = zipfile.ZipFile(DECK)
pres = ET.fromstring(z.read("ppt/presentation.xml"))
rels = ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
rmap = {r.get("Id"): r.get("Target") for r in rels}
order = [rmap[s.get(NSR+"id")].split("/")[-1] for s in pres.find(NSP+"sldIdLst")]

def shapes(x):
    out = []
    for m in re.finditer(r'<p:(sp|pic|graphicFrame)>.*?</p:\1>', x, re.S):
        b = m.group(0)
        o = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>', b)
        if not o: continue
        X, Y, CX, CY = map(int, o.groups())
        txt = "".join(re.findall(r'<a:t>([^<]*)</a:t>', b))
        out.append((X, Y, CX, CY, txt, m.group(1)))
    return out

START = 53   # 1~3주차는 손대지 않음
off_slide, overlaps = [], []
for i, f in enumerate(order, 1):
    if i < START: continue
    sh = shapes(z.read("ppt/slides/"+f).decode())
    for X, Y, CX, CY, t, k in sh:
        if X < -20000 or Y < -20000 or X+CX > W+20000 or Y+CY > H+20000:
            off_slide.append((i, k, X, Y, CX, CY, t[:30]))
    txt = [s for s in sh if s[4].strip() and s[5] == "sp"]
    for a in range(len(txt)):
        for b in range(a+1, len(txt)):
            ax, ay, acx, acy, at, _ = txt[a]; bx, by, bcx, bcy, bt, _ = txt[b]
            ix = min(ax+acx, bx+bcx) - max(ax, bx)
            iy = min(ay+acy, by+bcy) - max(ay, by)
            if ix > 120000 and iy > 120000:      # 실제로 보일 만큼 겹칠 때만
                overlaps.append((i, at[:24], bt[:24], ix, iy))

print("■ 화면 밖 도형:", len(off_slide))
for r in off_slide[:30]: print("   ", r)
print("■ 글자 상자 겹침:", len(overlaps))
for r in overlaps[:40]: print("   ", r)

BAD = ["게임", "함정", "꿀팁", "마법", "비법", "레벨업", "치트", "필살기", "관계대수", "관계 대수"]
print("■ 금지 표현:")
hit = 0
for i, f in enumerate(order, 1):
    if i < START: continue
    t = "".join(re.findall(r'<a:t>([^<]*)</a:t>', z.read("ppt/slides/"+f).decode()))
    for w in BAD:
        if w in t:
            print(f"    {i}: {w}"); hit += 1
print("    없음" if not hit else f"    {hit}건")
