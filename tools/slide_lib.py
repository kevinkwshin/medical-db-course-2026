# -*- coding: utf-8 -*-
"""
16:9 강의 슬라이드 렌더러 (HTML → Brave headless → PDF)
- qsql(): SQL을 실제 mini_emr.sqlite에 실행하여 결과 테이블을 슬라이드에 자동 삽입
"""
import html
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "..", "mini_emr", "mini_emr.sqlite")
BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

COURSE = "의료진을 위한 데이터베이스"

# ------------------------------------------------------------------ SQL 하이라이트
_KW = r"""SELECT FROM WHERE GROUP BY HAVING ORDER LIMIT AS DISTINCT AND OR NOT IN IS NULL
LIKE BETWEEN CASE WHEN THEN ELSE END COUNT SUM AVG MIN MAX ROUND JOIN INNER LEFT ON
CREATE TABLE ALTER DROP ADD COLUMN INSERT INTO VALUES UPDATE SET DELETE PRIMARY KEY
FOREIGN REFERENCES UNIQUE CHECK DEFAULT INTEGER TEXT REAL DATE DATETIME EXISTS
COMMIT ROLLBACK BEGIN TRANSACTION VIEW WITH UNION ALL ASC DESC GRANT REVOKE TO
julianday strftime substr CAST COALESCE""".split()
_KW_RE = re.compile(r"\b(" + "|".join(sorted(_KW, key=len, reverse=True)) + r")\b")


def hl_sql(sql):
    out, pos = [], 0
    token_re = re.compile(r"('([^']*)')|(--[^\n]*)|(\b\d+(\.\d+)?\b)")
    for m in token_re.finditer(sql):
        seg = sql[pos:m.start()]
        out.append(_KW_RE.sub(r'<span class="kw">\1</span>', html.escape(seg)))
        t = m.group(0)
        cls = "str" if t.startswith("'") else ("com" if t.startswith("--") else "num")
        out.append(f'<span class="{cls}">{html.escape(t)}</span>')
        pos = m.end()
    out.append(_KW_RE.sub(r'<span class="kw">\1</span>', html.escape(sql[pos:])))
    return "".join(out)


# ------------------------------------------------------------------ SQL 실행
def run_sql(sql, max_rows=8, db=None):
    """(headers, rows(표시용), total_rows) 반환. 여러 문장이면 마지막 SELECT 결과."""
    src = db or DB
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    shutil.copy(src, tmp.name)          # 원본 보호: DML/DDL도 사본 위에서 실행
    con = sqlite3.connect(tmp.name)
    try:
        cur = con.cursor()
        stmts = [s.strip() for s in sql.split(";") if s.strip()]
        headers, rows = [], []
        for s in stmts:
            cur.execute(s)
            if cur.description:
                headers = [c[0] for c in cur.description]
                rows = cur.fetchall()
        total = len(rows)
        disp = []
        for r in rows[:max_rows]:
            disp.append(["∅" if v is None else
                         (f"{v:g}" if isinstance(v, float) else str(v)) for v in r])
        return headers, disp, total
    finally:
        con.close()
        os.unlink(tmp.name)


def result_table(headers, rows, total, max_rows=8):
    if not headers:
        return '<div class="resnote">실행 완료 (반환된 행 없음)</div>'
    th = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    trs = ""
    for r in rows:
        tds = "".join(f"<td>{html.escape(c)}</td>" for c in r)
        trs += f"<tr>{tds}</tr>"
    more = (f'<div class="resnote">… 총 {total}행 중 {len(rows)}행 표시</div>'
            if total > len(rows) else
            f'<div class="resnote">총 {total}행</div>')
    return f'<table class="res"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>{more}'


# ------------------------------------------------------------------ 슬라이드 생성자
def cover(week, title, topics, question=None, course=COURSE):
    tp = "".join(f"<li>{t}</li>" for t in topics)
    q = (f'<div class="cover-q"><span>이번 주 대표 질문</span>{question}</div>'
         if question else "")
    return {"cls": "cover", "html": f"""
      <div class="cover-week">{week}주차</div>
      <h1 class="cover-title">{title}</h1>
      <ul class="cover-topics">{tp}</ul>
      {q}
      <div class="cover-course">{course}</div>"""}


def bullets(title, items, note=None, tag=None, sub=None):
    lis = ""
    for it in items:
        if isinstance(it, (tuple, list)):
            lis += f'<li><b>{it[0]}</b><span class="desc">{it[1]}</span></li>'
        else:
            lis += f"<li>{it}</li>"
    n = f'<div class="note">{note}</div>' if note else ""
    s = f'<div class="subtitle">{sub}</div>' if sub else ""
    return {"cls": "content", "title": title, "tag": tag,
            "html": f'{s}<ul class="big">{lis}</ul>{n}'}


def _sql_font(sql):
    """줄 수·최장 줄 길이에 따라 코드 폰트 자동 축소"""
    lines = sql.strip().split("\n")
    n, w = len(lines), max(len(l) for l in lines)
    if n > 19 or w > 60:
        return "font-size:14.5px; line-height:1.5;"
    if n > 15 or w > 52:
        return "font-size:16.5px; line-height:1.55;"
    if n > 12 or w > 46:
        return "font-size:18px;"
    return ""


def qsql(question, sql, note=None, max_rows=8, title=None, tag=None,
         result=True, db=None, caption=None):
    """임상 질문 → SQL → 실제 실행 결과 3단 슬라이드"""
    res_html = ""
    if result:
        h, r, t = run_sql(sql, max_rows=max_rows, db=db)
        res_html = f'<div class="res-wrap">{result_table(h, r, t, max_rows)}</div>'
    cap = f'<div class="note">{note}</div>' if note else ""
    q = f'<div class="clinq"><span class="clinq-label">임상 질문</span><p>{question}</p></div>'
    body = f"""{q}
      <div class="qsql-cols">
        <pre class="sql" style="{_sql_font(sql)}">{hl_sql(sql.strip())}</pre>
        {res_html}
      </div>{cap}"""
    return {"cls": "content", "title": title or "질문을 SQL로 번역하기",
            "tag": tag, "html": body}


def code(title, sql, note=None, tag=None, right_html=None, lang_sql=True):
    body_code = hl_sql(sql.strip()) if lang_sql else html.escape(sql.strip())
    n = f'<div class="note">{note}</div>' if note else ""
    fs = _sql_font(sql)
    if right_html:
        body = (f'<div class="qsql-cols"><pre class="sql" style="{fs}">{body_code}</pre>'
                f'<div class="side">{right_html}</div></div>{n}')
    else:
        body = f'<pre class="sql solo" style="{fs}">{body_code}</pre>{n}'
    return {"cls": "content", "title": title, "tag": tag, "html": body}


def two_col(title, left, right, note=None, tag=None, ratio=(1, 1)):
    n = f'<div class="note">{note}</div>' if note else ""
    return {"cls": "content", "title": title, "tag": tag,
            "html": f'<div class="cols" style="grid-template-columns:{ratio[0]}fr {ratio[1]}fr">'
                    f'<div>{left}</div><div>{right}</div></div>{n}'}


def table_slide(title, headers, rows, note=None, tag=None, small=False):
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    n = f'<div class="note">{note}</div>' if note else ""
    k = "info small" if small else "info"
    return {"cls": "content", "title": title, "tag": tag,
            "html": f'<table class="{k}"><thead><tr>{th}</tr></thead>'
                    f'<tbody>{trs}</tbody></table>{n}'}


def img_slide(title, img_path, note=None, tag=None, h=520):
    n = f'<div class="note">{note}</div>' if note else ""
    return {"cls": "content", "title": title, "tag": tag,
            "html": f'<div class="imgwrap"><img src="{img_path}" style="max-height:{h}px"></div>{n}'}


def html_slide(title, body, tag=None):
    return {"cls": "content", "title": title, "tag": tag, "html": body}


def closing(week, points, next_week=None, homework=None):
    lis = "".join(f"<li>{p}</li>" for p in points)
    nw = (f'<div class="nextweek"><b>다음 주</b> {next_week}</div>' if next_week else "")
    hw = (f'<div class="nextweek hw"><b>과제</b> {homework}</div>' if homework else "")
    return {"cls": "content", "title": f"{week}주차 정리",
            "html": f'<ul class="big">{lis}</ul>{hw}{nw}'}


# 개념 비교 카드 (두 개념 대비)
def versus(title, a_head, a_items, b_head, b_items, note=None, tag=None):
    def card(head, items, color):
        lis = "".join(f"<li>{i}</li>" for i in items)
        return (f'<div class="vs-card {color}"><div class="vs-head">{head}</div>'
                f'<ul>{lis}</ul></div>')
    n = f'<div class="note">{note}</div>' if note else ""
    return {"cls": "content", "title": title, "tag": tag,
            "html": f'<div class="vs">{card(a_head, a_items, "blue")}'
                    f'{card(b_head, b_items, "teal")}</div>{n}'}


# ------------------------------------------------------------------ 렌더링
CSS = """
* { margin:0; box-sizing:border-box; }
:root {
  --navy:#1e3a5f; --navy2:#16304f; --teal:#0e7490; --amber:#b45309;
  --ink:#0f172a; --sub:#475569; --line:#e2e8f0; --bg:#ffffff;
}
body { font-family:"Apple SD Gothic Neo","AppleGothic",sans-serif; }
.slide { width:1280px; height:720px; position:relative; background:var(--bg);
         overflow:hidden; page-break-after:always; display:flex; flex-direction:column; }

/* ---------- 표지 ---------- */
.slide.cover { background:linear-gradient(135deg,#0f2138 0%,#1e3a5f 70%,#24466e 100%);
               color:#fff; padding:70px 90px; justify-content:center; }
.cover-week { font-size:26px; font-weight:700; color:#7dd3fc; letter-spacing:2px; }
.cover-title { font-size:58px; font-weight:800; margin:14px 0 34px; line-height:1.25; }
.cover-topics { list-style:none; font-size:24px; color:#cbd5e1; line-height:1.9; }
.cover-topics li::before { content:"▪"; color:#38bdf8; margin-right:12px; }
.cover-q { margin-top:38px; background:rgba(56,189,248,.12); border-left:5px solid #38bdf8;
           padding:16px 24px; font-size:24px; border-radius:0 10px 10px 0; }
.cover-q span { display:block; font-size:15px; color:#7dd3fc; font-weight:700; margin-bottom:6px; }
.cover-course { position:absolute; bottom:44px; left:90px; font-size:17px; color:#64748b; }

/* ---------- 본문 공통 ---------- */
.slide.content { padding:0; }
.slide-head { background:var(--navy); color:#fff; padding:22px 56px 20px;
              display:flex; align-items:center; }
.slide-head h2 { font-size:33px; font-weight:800; }
.slide-head .tag { margin-left:auto; font-size:15px; font-weight:700; color:#93c5fd;
                   border:1.5px solid #3b5f8a; padding:4px 14px; border-radius:99px; }
.slide-body { flex:1; padding:30px 56px 20px; display:flex; flex-direction:column; gap:14px; }
.slide-foot { padding:0 56px 18px; display:flex; font-size:13.5px; color:#94a3b8; }
.slide-foot .pg { margin-left:auto; }
.subtitle { font-size:20px; color:var(--sub); margin-bottom:4px; }

ul.big { list-style:none; font-size:24.5px; line-height:1.62; color:var(--ink);
         display:flex; flex-direction:column; gap:17px; margin-top:6px; }
ul.big > li { padding-left:30px; position:relative; }
ul.big > li::before { content:""; position:absolute; left:2px; top:14px; width:11px; height:11px;
                      border-radius:3px; background:var(--teal); }
ul.big b { color:var(--navy); font-weight:800; }
ul.big .desc { display:block; font-size:19.5px; color:var(--sub); margin-top:3px; }

.note { margin-top:auto; background:#fffbeb; border-left:5px solid #f59e0b; color:#78350f;
        font-size:18.5px; padding:13px 20px; border-radius:0 8px 8px 0; line-height:1.5; }

/* ---------- 임상 질문 + SQL ---------- */
.clinq { background:#ecfeff; border:1.5px solid #a5f3fc; border-left:6px solid var(--teal);
         border-radius:0 10px 10px 0; padding:13px 22px; }
.clinq-label { font-size:14px; font-weight:800; color:var(--teal); display:block; }
.clinq p { font-size:25px; font-weight:700; color:var(--ink); margin-top:2px; }
.qsql-cols { display:grid; grid-template-columns:1.05fr 1fr; gap:22px; flex:1; min-height:0; }
pre.sql { background:#0b1526; color:#dbeafe; border-radius:12px; padding:22px 26px;
          font-family:"SF Mono",Menlo,Consolas,monospace; font-size:19.5px; line-height:1.62;
          overflow:hidden; white-space:pre-wrap; align-self:start; max-height:100%; width:100%; }
pre.sql.solo { font-size:21px; }
.kw { color:#7dd3fc; font-weight:700; } .str { color:#fbbf24; }
.num { color:#f9a8d4; } .com { color:#64748b; font-style:italic; }

.res-wrap { overflow:hidden; }
table.res { border-collapse:collapse; font-size:16.5px; width:100%;
            box-shadow:0 1px 5px rgba(15,23,42,.09); border-radius:8px; overflow:hidden; }
table.res th { background:var(--navy); color:#fff; padding:8px 12px; font-size:14.5px;
               text-align:left; font-family:Menlo,monospace; font-weight:600; }
table.res td { padding:7px 12px; border-bottom:1px solid var(--line); color:var(--ink); }
table.res tr:nth-child(even) td { background:#f8fafc; }
.resnote { font-size:14px; color:#94a3b8; margin-top:7px; }

/* ---------- 정보 테이블 / 2단 / 비교카드 ---------- */
table.info { border-collapse:collapse; width:100%; font-size:20px; }
table.info th { background:var(--navy); color:#fff; padding:11px 16px; text-align:left; font-size:18px; }
table.info td { padding:10px 16px; border-bottom:1px solid var(--line); color:var(--ink); line-height:1.45; }
table.info tr:nth-child(even) td { background:#f8fafc; }
table.info.small { font-size:16.5px; }
table.info.small th { font-size:15px; padding:8px 13px; }
table.info.small td { padding:7px 13px; }

.cols { display:grid; gap:26px; flex:1; min-height:0; }
.cols h3, .side h3 { font-size:21px; color:var(--navy); margin-bottom:10px; font-weight:800; }
.cols p, .side p { font-size:19px; color:var(--ink); line-height:1.6; margin-bottom:8px; }
.cols ul, .side ul { font-size:19px; color:var(--ink); line-height:1.7; padding-left:22px; }
.side { align-self:start; }

.vs { display:grid; grid-template-columns:1fr 1fr; gap:26px; flex:1; align-items:start; }
.vs-card { border-radius:14px; padding:24px 28px; height:100%; }
.vs-card.blue { background:#eff6ff; border:1.5px solid #bfdbfe; }
.vs-card.teal { background:#f0fdfa; border:1.5px solid #99f6e4; }
.vs-head { font-size:24px; font-weight:800; margin-bottom:14px; }
.vs-card.blue .vs-head { color:#1d4ed8; } .vs-card.teal .vs-head { color:#0f766e; }
.vs-card ul { list-style:none; font-size:20.5px; line-height:1.6; display:flex;
              flex-direction:column; gap:11px; color:var(--ink); }
.vs-card li::before { content:"•"; margin-right:10px; color:#94a3b8; }

.imgwrap { flex:1; display:flex; align-items:center; justify-content:center; min-height:0; }
.imgwrap img { max-width:100%; object-fit:contain; border-radius:8px; }

.nextweek { background:#eff6ff; border-left:5px solid #3b82f6; color:#1e3a8a;
            font-size:20px; padding:13px 20px; border-radius:0 8px 8px 0; margin-top:10px; }
.nextweek.hw { background:#f0fdf4; border-color:#22c55e; color:#14532d; }
.nextweek b { margin-right:12px; }

/* 작은 유틸 */
.pill { display:inline-block; background:#e0f2fe; color:#075985; font-weight:700;
        border-radius:99px; padding:2px 12px; font-size:15px; margin-right:6px; }
.mono { font-family:Menlo,monospace; font-size:.92em; background:#f1f5f9;
        padding:1px 7px; border-radius:5px; color:#0f172a; }
.danger { color:#b91c1c; font-weight:700; }
.okay { color:#047857; font-weight:700; }
"""


def render_deck(week, week_title, slides, out_pdf):
    pages = []
    n = len(slides)
    for i, s in enumerate(slides, 1):
        if s["cls"] == "cover":
            pages.append(f'<div class="slide cover">{s["html"]}</div>')
            continue
        tag = f'<span class="tag">{s["tag"]}</span>' if s.get("tag") else ""
        pages.append(f"""
        <div class="slide content">
          <div class="slide-head"><h2>{s["title"]}</h2>{tag}</div>
          <div class="slide-body">{s["html"]}</div>
          <div class="slide-foot"><span>{COURSE} · {week}주차 {week_title}</span>
            <span class="pg">{i} / {n}</span></div>
        </div>""")
    doc = (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
           f'<style>@page {{ size:1280px 720px; margin:0; }}{CSS}</style></head>'
           f'<body>{"".join(pages)}</body></html>')
    html_path = out_pdf.replace(".pdf", ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    subprocess.run([BRAVE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", html_path],
                   check=True, capture_output=True)
    return out_pdf
