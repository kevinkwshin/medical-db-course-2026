# -*- coding: utf-8 -*-
"""자동 검증: 데이터셋 시나리오 + 노트북 예제 셀 + 슬라이드 SQL 실행 가능성
실행: cd tools && python3 run_checks.py   (모두 통과하면 exit 0)
"""
import glob
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "..", "mini_emr", "mini_emr.sqlite")
FAILS = []


def check(name, ok, detail=""):
    mark = "OK " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def fresh_con():
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    tmp.close()
    shutil.copy(DB, tmp.name)
    con = sqlite3.connect(tmp.name)
    con.execute("PRAGMA foreign_keys = ON")
    return con, tmp.name


# ------------------------------------------------ 1. 데이터셋 시나리오
def check_dataset():
    print("1. 데이터셋 시나리오 (주차별 실습 성립 조건)")
    con, path = fresh_con()
    q = lambda sql: con.execute(sql).fetchall()
    check("무결성", q("PRAGMA integrity_check")[0][0] == "ok")
    check("환자 50명", q("SELECT COUNT(*) FROM patient")[0][0] == 50)
    check("FK 위반 없음", len(q("PRAGMA foreign_key_check")) == 0)
    no_a1c = sorted(r[0] for r in q(
        """SELECT DISTINCT v.patient_id FROM visit v JOIN diagnosis d ON v.visit_id=d.visit_id
           WHERE d.kcd_code LIKE 'E11%' AND v.patient_id NOT IN (
             SELECT v2.patient_id FROM visit v2 JOIN lab l ON v2.visit_id=l.visit_id
             WHERE l.test_name='HbA1c')"""))
    check("11주차: HbA1c 미검사 당뇨환자 = P007·P013", no_a1c == ["P007", "P013"], str(no_a1c))
    cohort = q("""SELECT v.patient_id FROM visit v JOIN diagnosis d ON v.visit_id=d.visit_id
                  WHERE d.kcd_code LIKE 'I63%' GROUP BY v.patient_id
                  HAVING MIN(v.visit_date) >= '2020-01-01'""")
    check("13주차: 신규 I63 코호트 8명", len(cohort) == 8, str(len(cohort)))
    check("14주차: mmol/L 함정 1건",
          q("SELECT COUNT(*) FROM lab WHERE unit='mmol/L'")[0][0] == 1)
    check("14주차: 결과값 NULL 1건",
          q("SELECT COUNT(*) FROM lab WHERE result_value IS NULL")[0][0] == 1)
    # FK가 실제로 동작하는지 (2·8주차 실습의 전제)
    try:
        con.execute("INSERT INTO prescription VALUES ('RX_T','V9999','X','x','1',1)")
        check("FK 강제 동작 (잘못된 참조 거부)", False, "차단되지 않음!")
    except sqlite3.IntegrityError:
        check("FK 강제 동작 (잘못된 참조 거부)", True)
    con.close()
    os.unlink(path)


# ------------------------------------------------ 2. 노트북 예제 셀 실행
def check_notebooks():
    print("2. 노트북 예제 셀 (q/run 블록을 순서대로 실행)")
    for f in sorted(glob.glob(os.path.join(BASE, "..", "code", "*.ipynb"))):
        con, path = fresh_con()
        name, ok, err = os.path.basename(f), True, ""
        nb = json.load(open(f, encoding="utf-8"))
        for c in nb["cells"]:
            if c["cell_type"] != "code":
                continue
            src = "".join(c["source"])
            if "[연습" in src or "def reset_db" in src:
                continue                     # 연습 빈칸·준비 셀은 제외
            for m in re.finditer(r'(?:q|run)\("""(.*?)"""\)', src, re.S):
                sql = m.group(1).strip()
                try:
                    con.executescript(sql)
                except Exception as e:
                    if "try:" in src:        # 의도된 에러 데모
                        continue
                    ok, err = False, f"{e} :: {sql[:60]}"
                    break
        check(name, ok, err)
        con.close()
        os.unlink(path)


# ------------------------------------------------ 3. 슬라이드 SQL
def check_slides():
    print("3. 슬라이드 SQL (qsql 슬라이드 재실행)")
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
    check_notebooks()
    check_slides()
    print(f"\n결과: {'전체 통과' if not FAILS else f'{len(FAILS)}건 실패 — {FAILS}'}")
    sys.exit(1 if FAILS else 0)
