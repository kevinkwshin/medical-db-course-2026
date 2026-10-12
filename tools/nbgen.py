# -*- coding: utf-8 -*-
"""nbgen.py — 실습/과제 노트북을 코드로 만들고(nbformat) 실제로 실행해 검증(nbclient)하는 도구.

노트북 공통 구조
  0. 준비 셀(Colab 에서는 코드가 접혀 보임): 데이터 다운로드 → jupysql → DuckDB 연결 → 채점 함수
  1. %%sql 셀: 학생은 SQL만 입력. 문항 셀의 첫 줄 주석(-- Q1)이 문항 이름표
  2. check("Q1", _) : 직전 %%sql 결과(_)를 정답 지문과 비교해 ✅/❌ 와 이유를 표시

채점 지문(GRADER_CORE)은 빌더와 노트북이 같은 코드를 씁니다. 값을 문자열로 바꿀 때
정수로 떨어지는 소수(1947.0)는 정수로, Decimal 은 소수로, 날짜는 YYYY-MM-DD 로 맞춥니다.
"""
import os, sys, json, shutil, hashlib, zlib, base64
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

DB_NAME = "aact_mini.duckdb"
DATA_URL = "https://raw.githubusercontent.com/kevinkwshin/medical-db-course-2026/main/data/aact_mini.duckdb.gz"
KERNEL = "py39"

# 과제 배정 질환 15개. 슬라이드 예제에 숫자가 나오는 질환(제2형 당뇨병 · 뇌졸중 · 고혈압 · 천식)은
# 2026-10-12 에 빼고, 슬라이드 · 노트북에 나오지 않는 질환으로 바꿨습니다.
MESH = ["Lung Neoplasms", "Parkinson Disease", "Atrial Fibrillation", "Breast Neoplasms", "Depressive Disorder",
        "Coronary Artery Disease", "Heart Failure", "Pulmonary Disease, Chronic Obstructive", "Renal Insufficiency, Chronic",
        "Alzheimer Disease", "Obesity", "COVID-19", "Osteoarthritis", "Sepsis", "Pneumonia"]

TABLES_IMG_URL = "https://raw.githubusercontent.com/kevinkwshin/medical-db-course-2026/main/data/aact_mini_tables.png"   # 7주차 슬라이드 "aact_mini 표 구조 한눈에 보기"

# 데이터 구성 표 (그림 tools/build_erd.py 와 같은 7개 표, 슬라이드 172)
# (표, 한 행의 뜻, 기본키, 외래키, studies 와의 관계)
DATA_TABLES = [
    ("studies", "임상시험 1건", "nct_id", "—", "기준이 되는 표"),
    ("eligibilities", "선정 · 제외 기준", "id", "`nct_id` → studies", "1 : 1 (시험마다 1행)"),
    ("sponsors", "스폰서 1곳", "id", "`nct_id` → studies", "1 : N (하나 이상)"),
    ("conditions", "대상 질환 1개 (연구자가 적은 이름)", "id", "`nct_id` → studies", "1 : N (하나 이상)"),
    ("browse_conditions", "표준 질환명(MeSH) 1개", "id", "`nct_id` → studies", "1 : N (없을 수도 있음)"),
    ("countries", "참여 국가 1곳", "id", "`nct_id` → studies", "1 : N (없을 수도 있음)"),
    ("facilities", "수행 기관 1곳", "id", "`nct_id` → studies", "1 : N (없을 수도 있음)"),
]
DATA_COLS = {
    "studies": "brief_title, study_type, overall_status, phase, start_date, enrollment, results_first_posted_date",
    "eligibilities": "gender, minimum_age (글자)",
    "sponsors": "agency_class, lead_or_collaborator, name",
    "conditions": "name (자유 입력이라 표기가 제각각)",
    "browse_conditions": "mesh_term",
    "countries": "name, removed (TRUE 면 등록 후 빠진 국가)",
    "facilities": "name, country",
}

# ---------------------------------------------------------------- 채점 지문 (빌더 · 노트북 공용)
GRADER_CORE = r'''
import hashlib as _hl, math as _math, decimal as _dec, datetime as _dt
import re as _re, zlib as _zlib, base64 as _b64, json as _json

def _load_answers(blob):
    """자동 확인용 지문(정답 결과표의 해시 · 행 수 · 열 이름 · 힌트)을 풉니다. 정답 SQL 은 들어 있지 않습니다."""
    return _json.loads(_zlib.decompress(_b64.b64decode(blob)).decode())

def _v(v):
    """값 하나를 비교용 문자열로: 빈 값 → '', 1947.0 → '1947', 날짜 → 'YYYY-MM-DD'"""
    try:
        if v is None or (not isinstance(v, (str, bytes)) and _pd.isna(v)):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(v, _dec.Decimal):
        v = float(v)
    if isinstance(v, (bool, _np.bool_)):
        return str(bool(v))
    if isinstance(v, (int, _np.integer)):
        return str(int(v))
    if isinstance(v, (float, _np.floating)):
        v = round(float(v), 4)
        return str(int(v)) if v.is_integer() else repr(v)
    if isinstance(v, (_pd.Timestamp, _dt.datetime)):
        if v.hour == 0 and v.minute == 0 and v.second == 0 and v.microsecond == 0:
            return v.strftime("%Y-%m-%d")
        return v.isoformat()
    if isinstance(v, _dt.date):
        return v.isoformat()
    return str(v)

def _sigs(df):
    """결과표의 지문: 열 이름(소문자), 행 수, 행 순서 무시 지문(sig), 행 순서 포함 지문(osig)"""
    cols = [str(c).strip().lower() for c in df.columns]
    rows = ["\x1f".join(_v(x) for x in r) for r in df.itertuples(index=False, name=None)]
    head = "\x1e".join(cols)
    h = lambda rs: _hl.md5((head + "\x1d" + "\x1e".join(rs)).encode()).hexdigest()[:12]
    return {"sig": h(sorted(rows)), "osig": h(rows), "rows": len(rows), "cols": cols}
'''

# ---------------------------------------------------------------- 노트북 안에서만 쓰는 함수
RUNTIME = r'''
_LAST = {"tag": None, "error": False, "sql": ""}
_TRIES, _RESULT = {}, {}

def _after_cell(result):
    info = getattr(result, "info", None)
    src = (getattr(info, "raw_cell", "") or "").lstrip()
    if not src.startswith("%%sql"):
        return
    tag = None
    for line in src.split("\n")[1:]:
        s = line.strip()
        if s.startswith("--"):
            parts = s[2:].split()
            tag = parts[0] if parts and not parts[0].startswith("[") else None
            break
        if s:
            break
    body = "\n".join(l.split("--")[0] for l in src.split("\n")[1:])
    _LAST.update(tag=tag, error=not result.success, sql=body)

for _cb in list(get_ipython().events.callbacks["post_run_cell"]):
    if getattr(_cb, "__name__", "") == "_after_cell":
        get_ipython().events.unregister("post_run_cell", _cb)
get_ipython().events.register("post_run_cell", _after_cell)

def _expected(name):
    a = ANSWERS[name]
    if "by_mesh" in a:
        if not globals().get("MY_MESH"):
            return None
        return dict(a["by_mesh"][MY_MESH], hint=a.get("hint", ""), ordered=a.get("ordered", False))
    return a

def _miss(name, why, exp):
    """틀렸을 때: 기록하고, 두 번째부터 힌트를 붙여 출력"""
    _RESULT[name] = False
    _TRIES[name] = _TRIES.get(name, 0) + 1
    msg = f"❌ {name}  {why}"
    hint = (exp or ANSWERS.get(name, {})).get("hint")
    if hint:
        msg += ("\n   💡 힌트: " + hint) if _TRIES[name] >= 2 else "\n   (한 번 더 다르면 힌트가 나옵니다)"
    print(msg)

def check(name, df=None):
    """바로 위 %%sql 셀의 결과를 확인합니다.  예) check("Q1", _)"""
    if name not in ANSWERS:
        print(f"알 수 없는 문항 이름입니다: {name}"); return
    if _LAST["tag"] and _LAST["tag"] != name:
        print(f"⚠️ 방금 실행한 SQL 셀은 {_LAST['tag']} 입니다. {name} 의 %%sql 셀을 먼저 실행한 뒤 이 셀을 실행하세요."); return
    exp = _expected(name)
    if exp is None:
        print("⚠️ 학번이 입력되지 않아 배정 질환이 없습니다. 맨 위 학번 셀과 준비 셀을 다시 실행하세요."); return
    if _LAST["sql"] and not _re.search(r"\bFROM\b", _LAST["sql"], _re.I):
        return _miss(name, "FROM 이 없는 SQL 입니다. 숫자를 직접 적지 말고, 표에서 꺼내 세는 SQL 을 쓰세요.", exp)
    if _LAST["error"]:
        return _miss(name, "바로 위 SQL 셀에서 오류가 났습니다. 붉은 글씨 중 'Error:' 가 들어간 줄을 읽고 SQL을 고친 뒤 다시 실행하세요.", exp)
    if not isinstance(df, _pd.DataFrame):
        return _miss(name, f"결과가 표가 아닙니다. %%sql 셀을 실행한 뒤, 바로 다음 셀에서 check('{name}', _) 를 실행하세요.", exp)
    got = _sigs(df)
    if got["sig"] == exp["sig"] and (not exp.get("ordered") or got["osig"] == exp["osig"]):
        _RESULT[name] = True
        print(f"✅ {name} 정답!  (행 {got['rows']}개)"); return
    zero = "값의 철자 · 대소문자 · 따옴표(예: 'COMPLETED')와, 빈 값을 = 나 <> 로 비교하지 않았는지(IS NULL) 확인하세요."
    if got["sig"] == exp["sig"]:
        why = "값은 맞지만 행의 순서가 다릅니다. 정렬(ORDER BY · DESC)을 확인하세요."
    elif got["cols"] != exp["cols"]:
        if len(got["cols"]) != len(exp["cols"]):
            why = f"열 개수가 다릅니다 (기대 {len(exp['cols'])}개: {', '.join(exp['cols'])} / 현재 {len(got['cols'])}개)."
        elif sorted(got["cols"]) == sorted(exp["cols"]):
            why = f"열의 순서가 다릅니다. 문항에 적힌 순서대로 적으세요: {', '.join(exp['cols'])}"
        else:
            why = f"열 이름이 다릅니다. 기대: {', '.join(exp['cols'])}  /  현재: {', '.join(got['cols'])}  (AS 로 이름을 맞추세요)"
    elif got["rows"] == 0 and exp["rows"] > 0:
        why = "결과가 0행입니다. " + zero
    elif got["rows"] == 1 and len(df.columns) and all(_v(x) in ("0", "") for x in df.iloc[0]):
        why = "결과가 0 이거나 비어 있습니다. 조건에 맞는 행이 없다는 뜻입니다. " + zero
    elif got["rows"] != exp["rows"]:
        why = f"행 수가 다릅니다 (기대 {exp['rows']}행, 현재 {got['rows']}행). 조건과 LIMIT 을 확인하세요."
    elif exp.get("ordered"):
        why = "행 수는 맞지만 값이나 순서가 다릅니다. 조건과 정렬(ORDER BY · DESC)을 확인하세요."
    else:
        why = "행 수는 맞지만 값이 다릅니다. 조건이나 계산식을 확인하세요."
    _miss(name, why, exp)

def 진행확인():
    """지금까지 확인한 문항의 결과를 한눈에 봅니다. 선택 문항은 개수에서 뺍니다."""
    names = list(ANSWERS)
    core = [n for n in names if not ANSWERS[n].get("optional")]
    ok = [n for n in core if _RESULT.get(n) is True]
    print(f"정답 {len(ok)} / {len(core)} 문항")
    for n in names:
        mark = {True: "✅", False: "❌"}.get(_RESULT.get(n), "·  (아직 check 안 함)")
        print(f"  {n:>4}  {mark}" + ("   (선택)" if ANSWERS[n].get("optional") else ""))
'''

SETUP_HEAD = r'''#@title ▶ 준비 셀 — 실행만 하세요 (Shift+Enter). 코드는 몰라도 됩니다. { display-mode: "form" }
import os, sys, urllib.request
import numpy as _np, pandas as _pd
DB  = "aact_mini.duckdb"
URL = "__URL__"

# 로컬(수업 폴더)에서 열었을 때는 ../data/ 의 파일을 사용
for cand in [DB, os.path.join("..", "data", DB), os.path.join("data", DB)]:
    if os.path.exists(cand):
        DB = cand
        break
else:
    print("데이터 파일을 내려받습니다 (약 50MB, 1분 내외) ...")
    import gzip, shutil
    urllib.request.urlretrieve(URL, DB + ".gz")
    with gzip.open(DB + ".gz", "rb") as f_in, open(DB, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(DB + ".gz")

if "google.colab" in sys.modules:           # Colab 에서만 설치 (수업에서 검증한 버전)
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "duckdb==1.4.5", "jupysql==0.11.1", "duckdb-engine==0.17.0"])

import duckdb
_pd.set_option("display.max_colwidth", 60)
%load_ext sql
%config SqlMagic.autopandas = True
%config SqlMagic.displaylimit = 30
%config SqlMagic.feedback = 0
%xmode Minimal
try:                                         # jupysql 의 영어 안내문(If using snippets ...)을 숨김
    import sql.error_handler as _eh
    _eh.CTE_MSG, _eh.ORIGINAL_ERROR = "", ""
except Exception:
    pass
conn = duckdb.connect(DB, read_only=True)
conn.execute("SET python_enable_replacements = false")   # 빈칸 ___ 을 파이썬 변수로 읽지 않게
%sql conn --alias aact
'''.replace("__URL__", DATA_URL)

IDENTITY_SRC = r'''#@title ✏️ 학번과 이름을 입력한 뒤 이 셀을 실행하세요 { display-mode: "form" }
학번 = ""  #@param {type:"string"}
이름 = ""  #@param {type:"string"}
'''

ASSIGN_SRC = r'''
MESH = __MESH__
학번, 이름 = str(globals().get("학번", "")).strip(), str(globals().get("이름", "")).strip()
if not 학번 or 학번 == "20260000":
    MY_MESH = None
    print("⚠️ 학번이 비어 있습니다. 맨 위 셀에 학번과 이름을 입력하고, 그 셀과 이 준비 셀을 다시 실행하세요.")
else:
    MY_MESH = MESH[int(_hl.md5(학번.encode()).hexdigest(), 16) % len(MESH)]
    print(f"연결 완료.  {이름}({학번}) 님의 배정 질환:  {MY_MESH}")
    print("→ SQL 의 '{{MY_MESH}}' 자리에 이 질환이 자동으로 들어갑니다. 질환 이름을 직접 적지 않아도 됩니다.")

def 제출확인():
    """제출 전에 실행: 문항별 결과와 제출 방법을 보여 줍니다."""
    print(f"제출자: {이름 or '(이름 없음)'} ({학번 or '학번 없음'})  /  배정 질환: {MY_MESH}")
    진행확인()
    print("\n제출 방법: ① 메뉴 런타임 → 모두 실행 (못 고친 문항에서 멈추면 그 아래 셀을 누르고 런타임 → 이후 셀 실행)")
    print("           ② 위 결과 확인  ③ 파일 → 다운로드 → .ipynb 다운로드")
    print(f"           ④ 파일 이름을 __KIND___{학번 or '학번'}_{이름 or '이름'}.ipynb 로 바꿔 LMS 에 제출")
'''


def setup_source(assignment=False, kind=""):
    src = SETUP_HEAD + GRADER_CORE + RUNTIME
    if assignment:
        src += ASSIGN_SRC.replace("__MESH__", json.dumps(MESH, ensure_ascii=False)).replace("__KIND__", kind)
    else:
        src += '\nprint("연결 완료:", DB)\n'
    return src


# 빌더 쪽에서도 똑같은 지문 함수를 씁니다
import numpy as _np, pandas as _pd
_g = {"_np": _np, "_pd": _pd}
exec(GRADER_CORE, _g)
sigs = _g["_sigs"]


def sig(df):
    return sigs(df)["sig"]


def offline_ok(entry, df):
    got = sigs(df)
    return got["sig"] == entry["sig"] and (not entry.get("ordered") or got["osig"] == entry["osig"])


def mesh_sql(m):
    """SQL 문자열 안에 넣을 수 있게 작은따옴표를 두 번 씁니다."""
    return m.replace("'", "''")


def id_for_mesh(mesh):
    """배정 질환이 mesh 가 되는 테스트용 학번을 찾습니다."""
    i = 20260001
    while True:
        if MESH[int(hashlib.md5(str(i).encode()).hexdigest(), 16) % len(MESH)] == mesh:
            return str(i)
        i += 1


class NB:
    """notebook builder.  assignment=True 이면 학번 셀 · 배정 질환 · 제출확인() 이 들어갑니다."""

    def __init__(self, title, intro_md=None, assignment=False, kind=""):
        self.cells, self.answers = [], {}
        self.assignment, self.kind = assignment, kind
        self.must_fail, self.must_pass = [], []
        self.md(f"# {title}")
        if intro_md:
            self.md(intro_md)

    # ---- 셀 만들기
    def md(self, text):
        self.cells.append(new_markdown_cell(text.strip("\n")))

    def code(self, src):
        self.cells.append(new_code_cell(src.strip("\n")))

    def sql(self, query, comment=None):
        head = "%%sql\n"
        if comment:
            head += "".join(f"-- {line}\n" for line in comment.split("\n"))
        self.cells.append(new_code_cell(head + query.strip("\n")))

    def sql_blank(self, name, template, comment=None):
        """학생이 채우는 SQL 셀(첫 줄 주석 = 문항 이름) + check 셀"""
        head = f"%%sql\n-- {name}\n"
        if comment and comment.strip() != name:
            head += "".join(f"-- {line}\n" for line in comment.split("\n"))
        self.cells.append(new_code_cell(head + template.strip("\n")))
        self.cells.append(new_code_cell(f'check("{name}", _)'))

    def setup(self, note=None):
        self.md("""
## 0. 시작하기 전에

- **Colab 에서 열었다면 먼저 메뉴의 `파일 → Drive에 사본 저장`** 을 누르세요. 그래야 작성한 내용이 남습니다.
- 셀 실행: 셀 왼쪽의 ▶ 단추 또는 `Shift + Enter`. **위에서부터 차례로** 실행합니다.
- `%%sql` 로 시작하는 셀에는 SQL만 적습니다. `%%sql` 바로 아래의 `-- Q1` 같은 줄은 지우지 마세요 (문항 이름표입니다).
- 오류가 나면 붉은 글씨 중 **`Error:` 가 들어간 줄**만 읽으면 됩니다. 연결이 이상하면 `런타임 → 런타임 다시 시작` 후 준비 셀부터 다시 실행하세요.
""" + ("- ✏️ 로 시작하는 칸의 첫 줄은 채점 이름표입니다. 지우지 말고 그 아래 줄에 적으세요.\n" if self.assignment else "")
  + (("\n" + note.strip("\n")) if note else ""))
        if self.assignment:
            self.code(IDENTITY_SRC)
        self.code(setup_source(self.assignment, self.kind))
        self.code('#@title 자동 확인 도우미 — 정답 SQL 은 들어 있지 않습니다 (수정하지 마세요) { display-mode: "form" }\n'
                  'ANSWERS = _load_answers("__ANSWERS__")')

    def tables_figure(self, note=None):
        """7주차 슬라이드 'aact_mini 표 구조 한눈에 보기' 그림 (data/aact_mini_tables.png)"""
        self.md(f"![aact_mini 표 구조 한눈에 보기]({TABLES_IMG_URL})" + (("\n\n" + note.strip()) if note else ""))

    def data_overview(self, cols=None, intro=None):
        """데이터 구성(ERD 그림 + 표 · 기본키 · 외래키 설명 + 1:N 확인 SQL). 그림은 tools/build_erd.py 로 만듭니다."""
        c = dict(DATA_COLS, **(cols or {}))
        rows = "\n".join(f"| `{t}` | {mean} | `{pk}` | {fk} | {rel} | {c[t]} |" for t, mean, pk, fk, rel in DATA_TABLES)
        self.md(f"""
## 데이터 구성 — 어떤 표가 있고, 어떻게 연결되나

{intro or "문제를 풀기 전에 표들의 관계를 먼저 봅니다. 열이 어느 표에 있는지, 표를 어떻게 연결하는지 막히면 이 그림으로 돌아오세요."}

![aact_mini 표 구조 한눈에 보기]({TABLES_IMG_URL})

| 표 | 한 행이 뜻하는 것 | 기본키 (PK) | 외래키 (FK) | studies 와의 관계 | 주로 쓰는 열 |
|---|---|---|---|---|---|
{rows}

**읽는 법** (5 · 6주차)

1. **기본키** — 한 행을 하나로 찾는 열입니다. `studies` 는 `nct_id`(임상시험 등록번호), 나머지 표는 `id` 입니다.
2. **외래키** — 다른 표의 `nct_id` 는 `studies.nct_id` 를 가리킵니다. 그래서 표를 연결(JOIN)할 때는 늘 `ON s.nct_id = 다른표.nct_id` 로 잇습니다.
3. **1 : N** — 시험 1건에 국가 · 기관 · 질환이 여러 개면 그 표에는 행이 여러 개입니다. 연결하면 시험 1건이 여러 행이 되므로, 시험 수는 `COUNT(DISTINCT s.nct_id)` 로 셉니다. 또 `browse_conditions` · `countries` · `facilities` 에는 행이 하나도 없는 시험도 있어서, INNER JOIN 하면 그 시험이 빠집니다.
""")
        self.sql("""SELECT s.nct_id, s.overall_status, c.name AS 국가
FROM studies AS s
JOIN countries AS c ON s.nct_id = c.nct_id
WHERE s.nct_id = 'NCT01795521'""", comment="확인: studies 에서는 1행인 시험이 countries 와 연결하면 국가 수만큼 여러 행이 됩니다")

    # ---- 정답 등록
    def register(self, name, df, hint="", ordered=False, optional=False):
        """optional=True: 선택 문항 — 진행확인()에서 (선택)으로 표시하고 개수에서 뺍니다"""
        s = sigs(df)
        self.answers[name] = {**s, "hint": hint, "ordered": ordered, "optional": optional}

    def register_mesh(self, name, qf, ref, hint="", ordered=False, optional=False):
        """배정 질환마다 답이 다른 문항: qf(mesh_sql 이 적용된 질환명) → SQL ('{{MY_MESH}}' 문자열도 가능)"""
        by = {m: sigs(ref(_sql_for(qf, m))) for m in MESH}
        self.answers[name] = {"by_mesh": by, "hint": hint, "ordered": ordered, "optional": optional}

    def expect_fail(self, name, sql_or_fn, why=""):
        """틀린 SQL 이 ❌ 가 되는지 빌드 때 확인 (질환별 문항은 15개 질환 모두)"""
        self.must_fail.append((name, sql_or_fn, why))

    def expect_pass(self, name, sql_or_fn, why=""):
        """다르게 썼지만 맞는 SQL 이 ✅ 가 되는지 빌드 때 확인"""
        self.must_pass.append((name, sql_or_fn, why))

    def save(self, path):
        nb = new_notebook(cells=self.cells)
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nb.metadata["language_info"] = {"name": "python"}
        nb.metadata["colab"] = {"provenance": [], "toc_visible": True}
        for c in nb.cells:
            if c.cell_type == "code" and '_load_answers("__ANSWERS__")' in c.source:
                blob = base64.b64encode(zlib.compress(json.dumps(self.answers, ensure_ascii=False).encode(), 9)).decode()
                c.source = c.source.replace("__ANSWERS__", blob)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        nbformat.write(nb, path)
        return path


def execute(path, cwd, kernel=KERNEL, timeout=600, prelude=None):
    """노트북을 실제로 실행합니다. prelude 가 있으면 첫 코드 셀 앞에 끼워 실행합니다(학번 지정 등)."""
    from nbclient import NotebookClient
    nb = nbformat.read(path, as_version=4)
    idx = None
    if prelude:
        idx = next(i for i, c in enumerate(nb.cells) if c.cell_type == "code") + 1   # 학번 셀 바로 뒤
        nb.cells.insert(idx, new_code_cell(prelude))
    client = NotebookClient(nb, timeout=timeout, kernel_name=kernel, resources={"metadata": {"path": cwd}}, allow_errors=True)
    client.execute()
    if idx is not None:
        del nb.cells[idx]
    errors = []
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        for o in c.get("outputs", []):
            if o.get("output_type") == "error":
                errors.append((i, o.get("ename"), (o.get("evalue") or "")[:200]))
            # jupysql 은 Parser · Catalog 오류를 error 가 아니라 stderr 글로 내보냅니다
            elif (o.get("output_type") == "stream" and o.get("name") == "stderr" and c.source.startswith("%%sql")
                  and "Error:" in o.get("text", "")):
                line = next((l for l in o["text"].splitlines() if "Error:" in l), "")
                errors.append((i, "stderr", line[:200]))
    return nb, errors


def strip_outputs(path):
    nb = nbformat.read(path, as_version=4)
    for c in nb.cells:
        if c.cell_type == "code":
            c.outputs = []
            c.execution_count = None
    nbformat.write(nb, path)


def _check_lines(nb):
    return [o["text"].strip() for c in nb.cells if c.cell_type == "code" and c.source.startswith("check(")
            for o in c.get("outputs", []) if o.get("output_type") == "stream"]


def _intended(src):
    """학생용 실행본에서 오류가 나도 되는 셀: 오류 예시, 빈칸, 과제의 '고칠 SQL'"""
    return any(k in src for k in ("[오류 예시]", "___", "배정질환을_여기에", "[고칠 SQL]", "[순서 맞추기]"))


def _sql_for(q, m):
    """정답/변형 SQL 을 질환 m 에 맞게: 함수면 호출, 문자열이면 '{{MY_MESH}}' 를 질환명으로 바꿈"""
    if callable(q):
        return q(mesh_sql(m or ""))
    return q.replace("{{MY_MESH}}", mesh_sql(m or "")) if m else q


def _fill(nb, fixes, mesh):
    for c in nb.cells:
        if c.cell_type == "code" and c.source.startswith("%%sql\n-- "):
            name = c.source.split("\n")[1][3:].split()[0]
            if name in fixes:
                q = fixes[name]
                q = q(mesh_sql(mesh)) if callable(q) else q      # 문자열은 '{{MY_MESH}}' 그대로 (노트북이 채움)
                c.source = f"%%sql\n-- {name} (정답)\n" + q.strip("\n")


def build_and_verify(nb, con, student_name, fixes, executed_copy=True, all_mesh=True):
    """학생용 저장 → (실행결과본) → 정답본 실행 · 모든 check ✅ 확인 → 틀린/맞는 변형 확인.

    fixes: {문항: 정답 SQL 또는 fn(질환명)}.  과제는 all_mesh=True 이면 15개 질환 모두 실행해 봅니다.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "notebooks")
    inst = os.path.join(out_dir, "instructor")
    os.makedirs(inst, exist_ok=True)
    student = os.path.join(out_dir, student_name + ".ipynb")
    nb.save(student)
    missing = set(nb.answers) - set(fixes)
    assert not missing, f"정답 SQL 이 없는 문항: {missing}"
    ref = lambda q: con.execute(q).df()

    # 1) 오프라인 확인 (빠름): 정답 SQL 은 ✅, 틀린 SQL 은 ❌, 다르게 쓴 맞는 SQL 은 ✅
    def entries(name):
        a = nb.answers[name]
        if "by_mesh" in a:
            return [(m, dict(a["by_mesh"][m], ordered=a.get("ordered"))) for m in MESH]
        return [(None, a)]
    problems = []
    checks = [("answer", n, q, "") for n, q in fixes.items()]
    checks += [("fail", n, q, w) for n, q, w in nb.must_fail] + [("pass", n, q, w) for n, q, w in nb.must_pass]
    for kind, name, q, why in checks:
        for m, entry in entries(name):
            ok = offline_ok(entry, ref(_sql_for(q, m)))
            if (kind == "fail" and ok) or (kind != "fail" and not ok):
                problems.append(f"{kind}:{name}:{m or ''} {why}".strip())
    print(f"offline: {len(checks)} SQL 확인, 문제 {len(problems)}건", problems[:10] if problems else "")
    assert not problems, "변형 SQL 검증 실패: " + "; ".join(problems)

    # 2) 학생용 그대로 실행 (실행결과본) — 의도한 오류 셀 외에 오류가 없어야 함
    if executed_copy:
        pre = f'학번 = "{id_for_mesh(MESH[0])}"; 이름 = "테스트"' if nb.assignment else None
        nbr, errors = execute(student, cwd=out_dir, prelude=pre)
        unexpected = [e for e in errors if not _intended(nbr.cells[e[0]].source)]
        print("student run: cells", len(nbr.cells), "| intended errors", len(errors) - len(unexpected), "| unexpected", unexpected)
        assert not unexpected, "학생용 노트북 실행 중 예상하지 못한 오류"
        nbformat.write(nbr, os.path.join(inst, student_name + "_실행결과.ipynb"))

    # 3) 정답본: 빈칸을 정답으로 채워 실행, 모든 check 가 ✅ (과제는 질환별로)
    targets = (MESH if all_mesh else MESH[:1]) if nb.assignment else [None]
    ans_path = os.path.join(inst, student_name + "_정답.ipynb")
    first = None
    for m in targets:
        nbs = nbformat.read(student, as_version=4)
        _fill(nbs, fixes, m or "")
        nbformat.write(nbs, ans_path)
        pre = f'학번 = "{id_for_mesh(m)}"; 이름 = "정답"' if m else None
        nbr, errors = execute(ans_path, cwd=out_dir, prelude=pre)
        unexpected = [e for e in errors if not _intended(nbr.cells[e[0]].source)]
        oks = _check_lines(nbr)
        bad = [t for t in oks if not t.startswith("✅")]
        print(f"answer run [{m or '-'}]: checks {len(oks)} | not ✅ {len(bad)} | unexpected errors {unexpected}")
        assert len(oks) == len(nb.answers), f"check 결과 수({len(oks)})와 문항 수({len(nb.answers)})가 다름"
        assert not unexpected and not bad, f"정답 노트북 검증 실패 [{m}]: {bad[:3]}"
        first = first or nbr
    nbformat.write(first, ans_path)          # 첫 번째(대표) 질환 실행본을 교수자용으로 저장
    strip_outputs(student)
    print("saved:", student, "|", ans_path)
    return student
