# -*- coding: utf-8 -*-
"""aact_mini 데이터 구성도(ERD) — data/aact_mini_erd.png

슬라이드 6주차(133~136)의 IE 표기법을 따릅니다:  || 반드시 하나 · |< 하나 이상 · O< 없거나 여럿.
숫자(행 수, 시험 1건당 평균 행 수, 행이 없는 시험 수)는 DB에서 다시 계산합니다.

    python3 tools/build_erd.py        # SVG 를 만들고 macOS QuickLook 으로 PNG 변환
"""
import os, subprocess, shutil, tempfile
import duckdb

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "data", "aact_mini.duckdb")
OUT_PNG = os.path.join(ROOT, "data", "aact_mini_erd.png")

BLUE, NAVY, GRAY, LINE = "#0070C0", "#1F3763", "#7F7F7F", "#404040"
PK_BG, FK_BG = "#FFC000", "#9DC3E6"
SANS = "Apple SD Gothic Neo, Malgun Gothic, Noto Sans KR, sans-serif"
MONO = "Menlo, Consolas, monospace"

W, H = 1600, 900
ROW, HEAD = 30, 58

STUDIES_COLS = ["brief_title", "study_type", "overall_status", "phase", "start_date",
                "enrollment", "results_first_posted_date"]
# (표, 한 행의 뜻, 주요 열, 쪽, 순서)
CHILDREN = [
    ("eligibilities", "선정 · 제외 기준", ["gender", "minimum_age"], "L", 0),
    ("sponsors", "스폰서 1곳", ["agency_class", "lead_or_collaborator"], "L", 1),
    ("conditions", "대상 질환 1개 (자유 입력)", ["name"], "L", 2),
    ("browse_conditions", "표준 질환명(MeSH) 1개", ["mesh_term"], "R", 0),
    ("countries", "참여 국가 1곳", ["name", "removed"], "R", 1),
    ("facilities", "수행 기관 1곳", ["name", "country"], "R", 2),
]


def stats(con):
    n = con.execute("SELECT COUNT(*) FROM studies").fetchone()[0]
    out = {"studies": {"rows": n}}
    for t, *_ in CHILDREN:
        rows, = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()
        zero, = con.execute(f"SELECT COUNT(*) FROM studies s WHERE NOT EXISTS "
                            f"(SELECT 1 FROM {t} x WHERE x.nct_id = s.nct_id)").fetchone()
        mx, = con.execute(f"SELECT MAX(c) FROM (SELECT COUNT(*) c FROM {t} GROUP BY nct_id)").fetchone()
        orphan, = con.execute(f"SELECT COUNT(*) FROM {t} x WHERE NOT EXISTS "
                              f"(SELECT 1 FROM studies s WHERE s.nct_id = x.nct_id)").fetchone()
        assert orphan == 0, f"{t}: studies 에 없는 nct_id {orphan}건"
        out[t] = {"rows": rows, "avg": rows / n, "zero": zero, "max": mx}
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=15, color=NAVY, weight="normal", family=SANS, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}" dominant-baseline="middle">{esc(s)}</text>')


def badge(x, y, label, bg):
    return (f'<rect x="{x}" y="{y - 10}" width="30" height="20" rx="4" fill="{bg}"/>'
            + text(x + 15, y + 1, label, size=12, color="#000000", weight="bold", anchor="middle"))


def table_box(x, y, w, name, sub, rows, foot=None):
    """rows: [(badge or None, column, note)]  →  (svg, y of the nct_id row centre, height)"""
    h = HEAD + ROW * len(rows) + (26 if foot else 8)
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FFFFFF" stroke="{BLUE}" stroke-width="2"/>',
         f'<path d="M{x},{y + 8} a8,8 0 0 1 8,-8 h{w - 16} a8,8 0 0 1 8,8 v{HEAD - 8} h{-w} z" fill="{BLUE}"/>',
         text(x + 14, y + 21, name, size=19, color="#FFFFFF", weight="bold", family=MONO),
         text(x + 14, y + 44, sub, size=14, color="#FFFFFF")]
    nct_y = None
    for i, (b, col, note) in enumerate(rows):
        cy = y + HEAD + ROW * i + ROW / 2 + 2
        if i:
            s.append(f'<line x1="{x + 8}" y1="{cy - ROW / 2}" x2="{x + w - 8}" y2="{cy - ROW / 2}" stroke="#D9D9D9"/>')
        if b:
            s.append(badge(x + 12, cy, b, PK_BG if b == "PK" else FK_BG))
        s.append(text(x + 50, cy, col, size=15, family=MONO, weight="bold" if b else "normal"))
        if note:
            s.append(text(x + w - 12, cy, note, size=13, color=GRAY, anchor="end"))
        if col == "nct_id":
            nct_y = cy
    if foot:
        s.append(text(x + 14, y + h - 15, foot, size=13, color=GRAY))
    return "\n".join(s), nct_y, h


def mark_one(x, y, d):
    """|| 반드시 하나 (x: 상자 끝, d: 선이 나가는 방향 +1/-1)"""
    return "".join(f'<line x1="{x + d * k}" y1="{y - 9}" x2="{x + d * k}" y2="{y + 9}" stroke="{LINE}" stroke-width="2"/>'
                   for k in (12, 19))


def mark_many(x, y, d, zero):
    """까마귀발 + (O 없을 수도 있다 | | 하나 이상)"""
    s = [f'<line x1="{x + d * 16}" y1="{y}" x2="{x}" y2="{y + dy}" stroke="{LINE}" stroke-width="2"/>' for dy in (-10, 0, 10)]
    if zero:
        s.append(f'<circle cx="{x + d * 25}" cy="{y}" r="6" fill="#FFFFFF" stroke="{LINE}" stroke-width="2"/>')
    else:
        s.append(f'<line x1="{x + d * 23}" y1="{y - 9}" x2="{x + d * 23}" y2="{y + 9}" stroke="{LINE}" stroke-width="2"/>')
    return "".join(s)


def build_svg(st):
    n = st["studies"]["rows"]
    # QuickLook 은 SVG 를 정사각형으로 렌더링하므로, 정사각형 캔버스 가운데에 그린 뒤 잘라 냅니다
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}" viewBox="0 0 {W} {W}">',
             f'<rect width="{W}" height="{W}" fill="#FFFFFF"/>',
             f'<g transform="translate(0,{(W - H) / 2})">',
             text(W / 2, 34, "aact_mini 데이터 구성 (ERD)", size=28, weight="bold", anchor="middle"),
             text(W / 2, 66, "모든 표는 nct_id(임상시험 등록번호)로 studies 와 연결됩니다. 선 끝 모양은 6주차 IE 표기법입니다.",
                  size=16, color=GRAY, anchor="middle")]
    # studies (가운데)
    sx, sw = 590, 420
    rows = [("PK", "nct_id", "임상시험 등록번호")] + [(None, c, "") for c in STUDIES_COLS]
    svg, _, sh = table_box(sx, 0, sw, "studies", f"임상시험 1건  ·  {n:,}행", rows)
    sy = 110 + (760 - sh) / 2
    svg, s_nct, sh = table_box(sx, sy, sw, "studies", f"임상시험 1건  ·  {n:,}행", rows)
    parts.append(svg)

    cw, top, gap = 380, 110, 30
    heights = {}
    for t, sub, cols, side, k in CHILDREN:
        rows = [("PK", "id", ""), ("FK", "nct_id", "→ studies")] + [(None, c, "") for c in cols]
        heights[(side, k)] = HEAD + ROW * len(rows) + 26
    ys = {}
    for side in "LR":
        y = top
        for k in range(3):
            ys[(side, k)] = y
            y += heights[(side, k)] + gap
    for t, sub, cols, side, k in CHILDREN:
        s = st[t]
        x = 70 if side == "L" else W - 70 - cw
        rows = [("PK", "id", ""), ("FK", "nct_id", "→ studies")] + [(None, c, "") for c in cols]
        one_to_one = s["max"] == 1 and s["zero"] == 0
        foot = (f"시험 1건당 1행 (1:1)" if one_to_one else
                f"시험 1건당 평균 {s['avg']:.1f}행" + (f"  ·  행이 없는 시험 {s['zero']:,}건" if s["zero"] else ""))
        svg, cy, _ = table_box(x, ys[(side, k)], cw, t, f"{sub}  ·  {s['rows']:,}행", rows, foot)
        parts.append(svg)
        # 선: 자식 표의 nct_id 줄 높이에서 studies 상자 옆면까지 수평선
        if side == "L":
            x1, x2, d_child, d_parent = x + cw, sx, +1, -1
        else:
            x1, x2, d_child, d_parent = x, sx + sw, -1, +1
        y_line = min(max(cy, sy + 20), sy + sh - 20)
        if abs(y_line - cy) < 1:
            parts.append(f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="{LINE}" stroke-width="2"/>')
        else:
            xm = (x1 + x2) / 2
            parts.append(f'<polyline points="{x1},{cy} {xm},{cy} {xm},{y_line} {x2},{y_line}" fill="none" stroke="{LINE}" stroke-width="2"/>')
        parts.append(mark_one(x2, y_line, d_parent))
        if one_to_one:
            parts.append(mark_one(x1, cy, d_child))
        else:
            parts.append(mark_many(x1, cy, d_child, zero=s["zero"] > 0))

    # 범례
    ly = H - 70
    parts.append(f'<rect x="70" y="{ly - 30}" width="{W - 140}" height="62" rx="8" fill="#F2F2F2"/>')
    lx = 100
    parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 50}" y2="{ly}" stroke="{LINE}" stroke-width="2"/>' + mark_one(lx + 50, ly, -1))
    parts.append(text(lx + 62, ly, "반드시 하나", size=15))
    lx = 300
    parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 50}" y2="{ly}" stroke="{LINE}" stroke-width="2"/>' + mark_many(lx + 50, ly, -1, zero=False))
    parts.append(text(lx + 62, ly, "하나 이상", size=15))
    lx = 490
    parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 50}" y2="{ly}" stroke="{LINE}" stroke-width="2"/>' + mark_many(lx + 50, ly, -1, zero=True))
    parts.append(text(lx + 62, ly, "없거나 여럿 → INNER JOIN 하면 빠지는 시험이 생김", size=15))
    parts.append(badge(1000, ly, "PK", PK_BG) + text(1040, ly, "기본키", size=15))
    parts.append(badge(1140, ly, "FK", FK_BG) + text(1180, ly, "외래키 (studies.nct_id 를 가리킴)", size=15))
    parts.append("</g></svg>")
    return "\n".join(parts)


def svg_to_png(svg, out_png, scale=1.5):
    """macOS QuickLook 으로 SVG → PNG (추가 설치 없이). 정사각형으로 렌더링한 뒤 가운데 내용만 잘라 냅니다."""
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "aact_mini_erd.svg")
    open(src, "w", encoding="utf-8").write(svg)
    size = int(W * scale)
    subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", tmp, src], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["sips", "--cropToHeightWidth", str(int(H * scale)), str(size), src + ".png"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.move(src + ".png", out_png)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    con = duckdb.connect(DB, read_only=True)
    st = stats(con)
    svg = build_svg(st)
    svg_to_png(svg, OUT_PNG)
    print("saved:", OUT_PNG)
    for t, *_ in CHILDREN:
        print(f"  {t:18s} {st[t]}")
