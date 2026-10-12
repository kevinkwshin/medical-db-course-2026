# -*- coding: utf-8 -*-
"""nbgen.py — 실습/과제 노트북을 코드로 만들고(nbformat) 실제로 실행해 검증(nbclient)하는 도구.

노트북 공통 구조
  0. 준비 셀: 데이터 파일 확인/다운로드 → jupysql 로드 → DuckDB 연결  (Colab, 로컬 모두 동작)
  1. %%sql 셀: 학생은 SQL만 입력
  2. check("문항", _) : 직전 %%sql 결과(_)를 정답 해시와 비교해 O/X 표시
"""
import os, sys, hashlib, json
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

DB_NAME = "aact_mini.duckdb"

SETUP_SRC = r'''# ── 0. 준비: 이 셀은 그대로 실행만 하세요 (Shift+Enter) ─────────────────────────
import os, sys, urllib.request
DB  = "aact_mini.duckdb"
URL = "https://raw.githubusercontent.com/kevinkwshin/medical-db-course-2026/main/data/aact_mini.duckdb.gz"

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
    print("완료:", DB)

if "google.colab" in sys.modules:           # Colab 에서만 설치
    import subprocess; subprocess.run([sys.executable, "-m", "pip", "install", "-q", "duckdb", "jupysql", "duckdb-engine"])

import duckdb, pandas as pd, hashlib
pd.set_option("display.max_colwidth", 60)
%load_ext sql
%config SqlMagic.autopandas = True
%config SqlMagic.displaylimit = 30
%config SqlMagic.feedback = 0
conn = duckdb.connect(DB, read_only=True)
%sql conn --alias aact
print("연결 완료:", DB)

def _sig(df):
    """결과표의 내용 지문: 열 이름 소문자화, 소수 4자리 반올림, 행 정렬 후 해시"""
    d = df.copy()
    d.columns = [str(c).lower() for c in d.columns]
    for c in d.columns:
        if pd.api.types.is_float_dtype(d[c]):
            d[c] = d[c].round(4)
    d = d.astype(str).sort_values(by=list(d.columns)).reset_index(drop=True)
    return hashlib.md5(d.to_csv(index=False).encode()).hexdigest()[:12]

def check(name, df):
    """직전 %%sql 결과를 _ 로 넘겨 확인합니다.  예) check("Q1", _)"""
    if name not in ANSWERS:
        print("알 수 없는 문항:", name); return
    if not isinstance(df, pd.DataFrame):
        print("❌ 결과가 표가 아닙니다. %%sql 셀을 먼저 실행한 뒤, 바로 다음 셀에서 check('%s', _) 를 실행하세요." % name); return
    exp = ANSWERS[name]
    if _sig(df) == exp["sig"]:
        print(f"✅ {name} 정답!  (행 {len(df)}개)")
    else:
        hint = exp.get("hint", "")
        rows = exp.get("rows")
        msg = f"❌ {name} 아직 다릅니다."
        if rows is not None:
            msg += f"  기대 행 수 {rows}개, 현재 {len(df)}개."
        if hint:
            msg += "  힌트: " + hint
        print(msg)
'''


class NB:
    def __init__(self, title, intro_md=None):
        self.cells = []
        self.answers = {}
        self.md(f"# {title}")
        if intro_md:
            self.md(intro_md)

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
        """학생이 채우는 SQL 셀 + check 셀"""
        head = "%%sql\n"
        if comment:
            head += "".join(f"-- {line}\n" for line in comment.split("\n"))
        self.cells.append(new_code_cell(head + template.strip("\n")))
        self.cells.append(new_code_cell(f'check("{name}", _)'))

    def setup(self):
        self.md("## 0. 준비\n아래 셀을 실행하면 데이터가 연결됩니다. 오류가 나면 런타임을 다시 시작한 뒤 한 번 더 실행하세요.")
        self.code(SETUP_SRC)
        self.code("ANSWERS = __ANSWERS__")

    def register(self, name, df, hint="", rows=None):
        self.answers[name] = {"sig": sig(df), "hint": hint, "rows": len(df) if rows is None else rows}

    def save(self, path):
        nb = new_notebook(cells=self.cells)
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nb.metadata["language_info"] = {"name": "python"}
        for c in nb.cells:
            if c.cell_type == "code" and c.source.startswith("ANSWERS = __ANSWERS__"):
                c.source = "ANSWERS = " + json.dumps(self.answers, ensure_ascii=False, indent=1)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        nbformat.write(nb, path)
        return path


def sig(df):
    import pandas as pd, hashlib
    d = df.copy()
    d.columns = [str(c).lower() for c in d.columns]
    for c in d.columns:
        if pd.api.types.is_float_dtype(d[c]):
            d[c] = d[c].round(4)
    d = d.astype(str).sort_values(by=list(d.columns)).reset_index(drop=True)
    return hashlib.md5(d.to_csv(index=False).encode()).hexdigest()[:12]


def execute(path, cwd, kernel="py39", timeout=600):
    """노트북을 실제로 실행해 오류가 없는지 확인하고 실행된 사본(*_run.ipynb)을 남깁니다."""
    from nbclient import NotebookClient
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(nb, timeout=timeout, kernel_name=kernel, resources={"metadata": {"path": cwd}}, allow_errors=True)
    client.execute()
    errors = []
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        for o in c.get("outputs", []):
            if o.get("output_type") == "error":
                errors.append((i, o.get("ename"), (o.get("evalue") or "")[:200]))
    out = path.replace(".ipynb", "_run.ipynb")
    nbformat.write(nb, out)
    return errors, out


def strip_outputs(path):
    nb = nbformat.read(path, as_version=4)
    for c in nb.cells:
        if c.cell_type == "code":
            c.outputs = []
            c.execution_count = None
    nbformat.write(nb, path)
