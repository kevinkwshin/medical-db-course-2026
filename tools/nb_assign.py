# -*- coding: utf-8 -*-
"""과제 노트북 공용: 질환 목록과 준비 셀."""
MESH = ["Diabetes Mellitus, Type 2", "Hypertension", "Asthma", "Breast Neoplasms", "Depressive Disorder",
        "Stroke", "Heart Failure", "Pulmonary Disease, Chronic Obstructive", "Renal Insufficiency, Chronic",
        "Alzheimer Disease", "Obesity", "COVID-19", "Osteoarthritis", "Sepsis", "Pneumonia"]

SETUP = r'''# ── 0. 준비: 이 셀을 먼저 실행하세요 (Shift+Enter) ───────────────────────────
import os, sys, urllib.request, hashlib
DB  = "aact_mini.duckdb"
URL = "https://raw.githubusercontent.com/kevinkwshin/medical-db-course-2026/main/data/aact_mini.duckdb.gz"

for cand in [DB, os.path.join("..", "data", DB), os.path.join("data", DB)]:
    if os.path.exists(cand):
        DB = cand; break
else:
    print("데이터 파일을 내려받습니다 (약 50MB, 1분 내외) ...")
    import gzip, shutil
    urllib.request.urlretrieve(URL, DB + ".gz")
    with gzip.open(DB + ".gz", "rb") as f_in, open(DB, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(DB + ".gz")

if "google.colab" in sys.modules:
    import subprocess; subprocess.run([sys.executable, "-m", "pip", "install", "-q", "duckdb", "jupysql", "duckdb-engine"])

import duckdb, pandas as pd
pd.set_option("display.max_colwidth", 60)
%load_ext sql
%config SqlMagic.autopandas = True
%config SqlMagic.displaylimit = 30
%config SqlMagic.feedback = 0
conn = duckdb.connect(DB, read_only=True)
%sql conn --alias aact

# ── 학번과 이름을 입력하세요 ────────────────────────────────────────────────
학번 = "20260000"     # ← 본인 학번으로 바꾸세요
이름 = "홍길동"        # ← 본인 이름으로 바꾸세요

MESH = ["Diabetes Mellitus, Type 2", "Hypertension", "Asthma", "Breast Neoplasms", "Depressive Disorder",
        "Stroke", "Heart Failure", "Pulmonary Disease, Chronic Obstructive", "Renal Insufficiency, Chronic",
        "Alzheimer Disease", "Obesity", "COVID-19", "Osteoarthritis", "Sepsis", "Pneumonia"]
MY_MESH = MESH[int(hashlib.md5(str(학번).encode()).hexdigest(), 16) % len(MESH)]
print(f"{이름}({학번}) 님의 배정 질환:  {MY_MESH}")
print("→ 아래 문항에서 '배정 질환' 이라고 나오면 이 값을 쓰세요.")

def _sig(df):
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
    a = ANSWERS[name]
    exp = a["by_mesh"].get(MY_MESH) if a.get("by_mesh") else a
    if not isinstance(df, pd.DataFrame):
        print(f"❌ {name}  결과가 표가 아닙니다. %%sql 셀을 먼저 실행한 뒤 바로 다음 셀에서 check 하세요."); return
    if _sig(df) == exp["sig"]:
        print(f"✅ {name} 정답!  (행 {len(df)}개)")
    else:
        msg = f"❌ {name} 아직 다릅니다.  기대 행 수 {exp['rows']}개, 현재 {len(df)}개."
        if a.get("hint"): msg += "  힌트: " + a["hint"]
        print(msg)

def 제출확인():
    done = [k for k in ANSWERS if k.startswith("Q")]
    print(f"문항 {len(done)}개.  모든 셀을 실행한 뒤 파일을 저장해 제출하세요.")
    print(f"제출자: {이름} ({학번}) / 배정 질환: {MY_MESH}")
'''


