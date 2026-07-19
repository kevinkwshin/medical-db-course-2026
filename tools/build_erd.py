# -*- coding: utf-8 -*-
"""미니 EMR ERD 이미지 생성 (HTML → Brave 스크린샷 → PNG)"""
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(BASE, "_erd.html")
OUT_PNG = os.path.join(BASE, "..", "mini_emr", "ERD.png")
BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

# (테이블명, 한글명, x, y, [(컬럼, 라벨, 표식)])  표식: PK/FK/''
TABLES = [
    ("patient", "환자", 70, 260, [
        ("patient_id", "환자ID", "PK"),
        ("sex", "성별", ""),
        ("birth_date", "생년월일", ""),
        ("blood_type", "혈액형", ""),
    ]),
    ("staff", "의료진", 70, 640, [
        ("staff_id", "직원ID", "PK"),
        ("role", "직종", ""),
        ("department", "진료과", ""),
    ]),
    ("visit", "내원", 560, 380, [
        ("visit_id", "내원ID", "PK"),
        ("patient_id", "환자ID", "FK"),
        ("visit_date", "내원일", ""),
        ("department", "진료과", ""),
        ("visit_type", "내원유형(외래/입원/응급)", ""),
        ("discharge_date", "퇴원일", ""),
        ("attending_id", "담당의ID", "FK"),
    ]),
    ("diagnosis", "진단", 1170, 40, [
        ("dx_id", "진단ID", "PK"),
        ("visit_id", "내원ID", "FK"),
        ("kcd_code", "KCD코드", ""),
        ("dx_name", "진단명", ""),
        ("is_primary", "주진단여부", ""),
    ]),
    ("prescription", "처방", 1170, 260, [
        ("rx_id", "처방ID", "PK"),
        ("visit_id", "내원ID", "FK"),
        ("drug_code", "약품코드", ""),
        ("drug_name", "약품명", ""),
        ("dose", "용량", ""),
        ("duration_days", "투약일수", ""),
    ]),
    ("lab", "검사", 1170, 510, [
        ("lab_id", "검사ID", "PK"),
        ("visit_id", "내원ID", "FK"),
        ("test_name", "검사명", ""),
        ("result_value", "결과값", ""),
        ("unit", "단위", ""),
        ("ref_low / ref_high", "정상 하한/상한", ""),
        ("collected_at", "채혈시각", ""),
    ]),
    ("vital", "활력징후", 1170, 800, [
        ("visit_id", "내원ID", "PK,FK"),
        ("measured_at", "측정시각", "PK"),
        ("sbp / dbp", "수축기/이완기 혈압", ""),
        ("pulse", "맥박", ""),
        ("temp", "체온", ""),
        ("spo2", "산소포화도", ""),
    ]),
    ("imaging", "영상", 560, 800, [
        ("img_id", "검사ID", "PK"),
        ("visit_id", "내원ID", "FK"),
        ("modality", "촬영종류", ""),
        ("body_part", "부위", ""),
        ("taken_date", "촬영일", ""),
        ("report", "판독문", ""),
    ]),
]

W_BOX = 330
ROW_H = 27
HEAD_H = 40

# 관계선: (부모테이블, 자식테이블) — 1:N
RELS = [
    ("patient", "visit"),
    ("staff", "visit"),
    ("visit", "diagnosis"),
    ("visit", "prescription"),
    ("visit", "lab"),
    ("visit", "vital"),
    ("visit", "imaging"),
]


def box_h(cols):
    return HEAD_H + ROW_H * len(cols) + 8


def anchor(name, side):
    t = next(t for t in TABLES if t[0] == name)
    x, y, h = t[2], t[3], box_h(t[4])
    if side == "right":
        return x + W_BOX, y + h / 2
    if side == "left":
        return x, y + h / 2
    if side == "top":
        return x + W_BOX / 2, y
    return x + W_BOX / 2, y + h  # bottom


def main():
    boxes, lines = [], []
    for name, kor, x, y, cols in TABLES:
        rows = ""
        for c, label, mark in cols:
            badge = ""
            if "PK" in mark:
                badge += '<span class="pk">PK</span>'
            if "FK" in mark:
                badge += '<span class="fk">FK</span>'
            rows += (f'<div class="row"><span class="cn">{c}</span>'
                     f'<span class="badges">{badge}</span>'
                     f'<span class="cl">{label}</span></div>')
        boxes.append(
            f'<div class="tbl" style="left:{x}px;top:{y}px;width:{W_BOX}px">'
            f'<div class="head">{name} <span class="kor">{kor}</span></div>{rows}</div>')

    for parent, child in RELS:
        if parent == "visit" and child == "imaging":
            x1, y1 = anchor(parent, "bottom")
            x2, y2 = anchor(child, "top")
            path = f"M{x1},{y1} C{x1},{(y1+y2)/2} {x2},{(y1+y2)/2} {x2},{y2}"
        elif parent == "visit" or child == "visit":
            p_side = "right"
            c_side = "left"
            x1, y1 = anchor(parent, p_side)
            x2, y2 = anchor(child, c_side)
            mx = (x1 + x2) / 2
            path = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"
        lines.append(f'<path d="{path}" class="rel"/>')
        # 1 : N 라벨
        lines.append(f'<text x="{x1+14}" y="{y1-8}" class="card">1</text>')
        lines.append(f'<text x="{x2-20}" y="{y2-8}" class="card">N</text>')

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
* {{ margin:0; box-sizing:border-box; font-family:"Apple SD Gothic Neo","AppleGothic",sans-serif; }}
body {{ width:1580px; height:1120px; background:#f8fafc; position:relative; }}
h1 {{ position:absolute; left:70px; top:40px; font-size:30px; color:#0f172a; }}
h1 small {{ font-size:16px; color:#64748b; font-weight:500; margin-left:14px; }}
.tbl {{ position:absolute; background:#fff; border:1.5px solid #cbd5e1; border-radius:10px;
       box-shadow:0 2px 8px rgba(15,23,42,.07); overflow:hidden; z-index:2; }}
.head {{ background:#1e3a5f; color:#fff; font-weight:700; font-size:17px;
        padding:9px 14px; height:{HEAD_H}px; }}
.head .kor {{ font-weight:500; font-size:14px; color:#93c5fd; margin-left:8px; }}
.row {{ display:flex; align-items:center; height:{ROW_H}px; padding:0 14px;
       font-size:13.5px; border-top:1px solid #f1f5f9; }}
.cn {{ color:#0f172a; font-family:"SF Mono",Menlo,monospace; font-size:12.5px; }}
.badges {{ margin-left:7px; }}
.pk,.fk {{ font-size:9.5px; font-weight:800; border-radius:4px; padding:1px 4px; margin-right:3px; }}
.pk {{ background:#fbbf24; color:#7c2d12; }}
.fk {{ background:#bfdbfe; color:#1e40af; }}
.cl {{ margin-left:auto; color:#64748b; font-size:12px; }}
svg {{ position:absolute; inset:0; z-index:1; }}
.rel {{ fill:none; stroke:#94a3b8; stroke-width:2; }}
.card {{ font-size:15px; font-weight:800; fill:#475569; }}
.note {{ position:absolute; left:70px; top:1050px; color:#94a3b8; font-size:13px; }}
</style></head><body>
<h1>미니 EMR — ERD <small>8개 테이블 · 환자 50명 · 내원 100건 (모든 데이터는 가상)</small></h1>
<svg width="1580" height="1120">{''.join(lines)}</svg>
{''.join(boxes)}
<div class="note">중심 구조: 환자(patient) 1 ─ N 내원(visit) 1 ─ N 진료기록(진단·처방·검사·활력징후·영상)</div>
</body></html>"""

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    subprocess.run([BRAVE, "--headless", "--disable-gpu",
                    "--window-size=1580,1120", "--hide-scrollbars",
                    f"--screenshot={os.path.abspath(OUT_PNG)}", OUT_HTML],
                   check=True, capture_output=True)
    print("ERD →", os.path.abspath(OUT_PNG))


if __name__ == "__main__":
    main()
