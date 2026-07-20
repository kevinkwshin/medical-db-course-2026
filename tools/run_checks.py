# -*- coding: utf-8 -*-
"""자동 검증 (CI에서도 실행 — Brave 불필요, python3 + pandas만 필요)

1. 데이터셋: 무결성 + 주차별 실습 시나리오 + 슬라이드 노트에 인용된 수치
2. 생성 스크립트 재현성: 재생성 결과가 커밋된 DB와 완전 동일한가
3. 노트북 end-to-end: 준비 셀부터 모든 코드 셀을 실제로 실행 (다운로드는 로컬 파일로 대체)
4. 슬라이드 SQL: 13개 주차 모듈 임포트 (qsql이 실제 DB에 실행됨)

실행: cd tools && python3 run_checks.py   (모두 통과하면 exit 0)
"""
import glob
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.abspath(os.path.join(BASE, "..", "mini_emr", "mini_emr.sqlite"))
GEN = os.path.abspath(os.path.join(BASE, "..", "mini_emr", "generate_mini_emr.py"))
FAILS = []


def check(name, ok, detail=""):
    print(f"  [{'OK ' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def fresh_con():
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    shutil.copy(DB, tmp.name)
    con = sqlite3.connect(tmp.name)
    con.execute("PRAGMA foreign_keys = ON")
    return con, tmp.name


# ================================================== 1. 데이터셋 + 인용 수치
def check_dataset():
    print("1. 데이터셋 시나리오 · 슬라이드 인용 수치")
    con, path = fresh_con()
    q = lambda sql: con.execute(sql).fetchall()
    one = lambda sql: q(sql)[0][0]

    check("무결성", one("PRAGMA integrity_check") == "ok")
    check("FK 위반 없음", len(q("PRAGMA foreign_key_check")) == 0)
    check("환자 50명", one("SELECT COUNT(*) FROM patient") == 50)

    no_a1c = sorted(r[0] for r in q(
        """SELECT DISTINCT v.patient_id FROM visit v JOIN diagnosis d ON v.visit_id=d.visit_id
           WHERE d.kcd_code LIKE 'E11%' AND v.patient_id NOT IN (
             SELECT v2.patient_id FROM visit v2 JOIN lab l ON v2.visit_id=l.visit_id
             WHERE l.test_name='HbA1c')"""))
    check("11주차: HbA1c 미검사 당뇨환자 = P007·P013", no_a1c == ["P007", "P013"], str(no_a1c))

    cohort = sorted(r[0] for r in q(
        """SELECT v.patient_id FROM visit v JOIN diagnosis d ON v.visit_id=d.visit_id
           WHERE d.kcd_code LIKE 'I63%' GROUP BY v.patient_id
           HAVING MIN(v.visit_date) >= '2020-01-01'"""))
    check("13주차: 신규 I63 코호트 = P021~P028",
          cohort == [f"P{i:03d}" for i in range(21, 29)], str(cohort))

    # ---- 슬라이드 노트에 하드코딩된 수치 (데이터 변경 시 여기서 걸린다)
    avg_los = one("""SELECT ROUND(AVG(julianday(discharge_date)-julianday(visit_date)),1)
                     FROM visit WHERE visit_type='입원'""")
    check("노트 인용: 평균 재원 11.7일", avg_los == 11.7, str(avg_los))
    check("노트 인용: 최장 재원 35일 (P039)",
          one("""SELECT MAX(julianday(discharge_date)-julianday(visit_date)) FROM visit""") == 35)
    no_abx = one("""SELECT COUNT(*) FROM patient p WHERE NOT EXISTS (
                      SELECT 1 FROM visit v JOIN prescription rx ON rx.visit_id=v.visit_id
                      WHERE v.patient_id=p.patient_id
                        AND rx.drug_code IN ('CTX2','AMC625','LVX500'))""")
    check("노트 인용: 항생제 무노출 41명", no_abx == 41, str(no_abx))
    check("노트 인용: 당뇨 8명 / HbA1c 검사자 6명",
          one("""SELECT COUNT(DISTINCT v.patient_id) FROM visit v
                 JOIN diagnosis d ON d.visit_id=v.visit_id WHERE d.kcd_code LIKE 'E11%'""") == 8
          and one("""SELECT COUNT(DISTINCT v.patient_id) FROM visit v
                     JOIN lab l ON l.visit_id=v.visit_id WHERE l.test_name='HbA1c'""") == 6)
    check("노트 인용: HbA1c 평균 7.6",
          one("SELECT ROUND(AVG(result_value),1) FROM lab WHERE test_name='HbA1c'") == 7.6)
    check("노트 인용: P010 HbA1c 최고 9.5 · 3회 연속 7.0 초과",
          [r[0] for r in q("""SELECT result_value FROM lab l JOIN visit v ON v.visit_id=l.visit_id
             WHERE v.patient_id='P010' AND l.test_name='HbA1c' ORDER BY collected_at""")]
          == [8.6, 9.5, 7.6])
    check("함정: mmol/L 1건(7.8) · 결과 NULL 1건",
          one("SELECT COUNT(*) FROM lab WHERE unit='mmol/L' AND result_value=7.8") == 1
          and one("SELECT COUNT(*) FROM lab WHERE result_value IS NULL") == 1)
    htn = one("""WITH sc AS (SELECT v.patient_id, MIN(v.visit_date) idx FROM visit v
                   JOIN diagnosis d ON v.visit_id=d.visit_id WHERE d.kcd_code LIKE 'I63%'
                   GROUP BY v.patient_id HAVING MIN(v.visit_date)>='2020-01-01')
                 SELECT SUM(CASE WHEN EXISTS (SELECT 1 FROM visit v2
                   JOIN diagnosis d2 ON d2.visit_id=v2.visit_id
                   WHERE v2.patient_id=sc.patient_id AND d2.kcd_code LIKE 'I10%'
                     AND v2.visit_date<=sc.idx) THEN 1 ELSE 0 END) FROM sc""")
    check("13주차: 기저 고혈압 5/8명", htn == 5, str(htn))

    try:
        con.execute("INSERT INTO prescription VALUES ('RX_T','V9999','X','x','1',1)")
        check("FK 강제 동작", False, "잘못된 참조가 차단되지 않음")
    except sqlite3.IntegrityError:
        check("FK 강제 동작", True)
    con.close()
    os.unlink(path)


# ================================================== 2. 생성 스크립트 재현성
def check_regen():
    print("2. 생성 스크립트 재현성 (재생성 == 커밋본)")
    with tempfile.TemporaryDirectory() as td:
        shutil.copy(GEN, td)
        r = subprocess.run([sys.executable, os.path.join(td, os.path.basename(GEN))],
                           capture_output=True)
        if r.returncode != 0:
            check("재생성 실행", False, r.stderr.decode(errors="replace")[:120])
            return
        a, b = sqlite3.connect(DB), sqlite3.connect(os.path.join(td, "mini_emr.sqlite"))
        tables = [t[0] for t in a.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        same = all(a.execute(f"SELECT * FROM {t}").fetchall()
                   == b.execute(f"SELECT * FROM {t}").fetchall() for t in tables)
        check("전체 테이블 내용 동일", same,
              "커밋된 DB가 생성 스크립트 출력과 다름 — 직접 수정되었거나 스크립트 변경 후 미재생성")
        a.close(); b.close()


# ================================================== 3. 노트북 end-to-end
def check_notebooks():
    print("3. 노트북 end-to-end (준비 셀 포함 전체 코드 셀 실행)")
    orig_retrieve = urllib.request.urlretrieve
    urllib.request.urlretrieve = lambda url, path: shutil.copy(DB, path)  # 네트워크 차단
    cwd = os.getcwd()
    try:
        for f in sorted(glob.glob(os.path.join(BASE, "..", "code", "*.ipynb"))):
            name, ok, err = os.path.basename(f), True, ""
            nb = json.load(open(f, encoding="utf-8"))
            with tempfile.TemporaryDirectory() as td:
                os.chdir(td)
                ns = {}
                for i, c in enumerate(nb["cells"]):
                    if c["cell_type"] != "code":
                        continue
                    src = "".join(c["source"])
                    if "여기에 SQL을 작성하세요" in src:
                        continue                     # 연습 빈칸
                    try:
                        exec(compile(src, f"{name}:cell{i}", "exec"), ns)
                    except Exception as e:
                        ok, err = False, f"cell{i}: {type(e).__name__}: {e}"
                        break
                os.chdir(cwd)
            check(name, ok, err)
    finally:
        urllib.request.urlretrieve = orig_retrieve
        os.chdir(cwd)


# ================================================== 4. 슬라이드 SQL
def check_slides():
    print("4. 슬라이드 SQL (qsql 재실행)")
    sys.path.insert(0, BASE)
    sys.path.insert(0, os.path.join(BASE, "weeks"))
    import importlib
    for w in [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]:
        try:
            mod = importlib.import_module(f"week{w:02d}")
            check(f"week{w:02d} ({len(mod.slides)}슬라이드)", True)
        except Exception as e:
            check(f"week{w:02d}", False, str(e))


if __name__ == "__main__":
    check_dataset()
    check_regen()
    check_notebooks()
    check_slides()
    print(f"\n결과: {'전체 통과' if not FAILS else f'{len(FAILS)}건 실패 — {FAILS}'}")
    sys.exit(1 if FAILS else 0)
