# -*- coding: utf-8 -*-
"""주차별 Colab 노트북(.ipynb) + SQL 스크립트(.sql) 생성기
실행: python3 build_notebooks.py  →  ../code/weekNN_*.ipynb, ../code/sql/weekNN.sql
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(BASE, "..", "code")
SQLD = os.path.join(CODE, "sql")

# mini_emr.sqlite 배포 주소 — 학기 중 데이터가 바뀌지 않도록 git 태그에 고정
# (데이터를 변경하면: 새 태그 생성·push → DATA_TAG 갱신 → 노트북 재생성)
DATA_TAG = "data-v1"
DB_URL = (f"https://raw.githubusercontent.com/kevinkwshin/medical-db-course-2026/"
          f"{DATA_TAG}/mini_emr/mini_emr.sqlite")

SETUP_MD = """# {week}주차 — {title}
**의료진을 위한 데이터베이스** · 미니 EMR 실습 노트북

사용법: 위에서부터 순서대로 셀을 실행하세요 (`Shift+Enter`).
`q("SELECT ...")` 안의 SQL만 바꿔가며 실험하면 됩니다.
어떤 셀이 오류로 막히거나 데이터가 엉켰다면, 아무 셀에서 `reset_db()`를 실행하면 처음 상태로 돌아갑니다."""

SETUP_CODE = """# [준비] 미니 EMR 데이터베이스 내려받기 + 도우미 정의 — 이 셀을 가장 먼저 실행!
import os, shutil, sqlite3, urllib.request
import pandas as pd

DB_URL = "{db_url}"
DB_PATH = "mini_emr.sqlite"
WORK_PATH = {work_path}   # 실습에 사용할 파일

con = None

def reset_db():
    \"\"\"DB를 원본 상태로 되돌리고 다시 연결 (막히면 언제든 호출)\"\"\"
    global con
    if con is not None:
        con.close()
    try:
        urllib.request.urlretrieve(DB_URL, DB_PATH)
    except Exception as e:
        if not os.path.exists(DB_PATH):
            raise RuntimeError(
                "DB 다운로드 실패 — 왼쪽 파일 탭에 mini_emr.sqlite를 업로드한 뒤 이 셀을 다시 실행하세요."
            ) from e
        print("다운로드 실패 — 업로드되어 있는 파일을 사용합니다.")
    if WORK_PATH != DB_PATH:
        shutil.copyfile(DB_PATH, WORK_PATH)   # 원본 보존, 실습은 사본에서
    con = sqlite3.connect(WORK_PATH)
    con.execute("PRAGMA foreign_keys = ON")   # SQLite는 기본으로 꺼져 있음 — 반드시 켠다
    assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1

def q(sql):
    \"\"\"조회(SELECT) 실행 → 결과를 표로 반환\"\"\"
    return pd.read_sql_query(sql, con)

def run(sql):
    \"\"\"데이터/구조를 바꾸는 SQL(INSERT/UPDATE/DELETE/CREATE 등) 실행.
    여러 문장을 순서대로 실행하고 즉시 커밋합니다 — 트랜잭션(BEGIN/ROLLBACK) 실습은
    8주차처럼 con.cursor()를 직접 사용하세요.\"\"\"
    con.executescript(sql); con.commit(); print("실행 완료")

reset_db()
q("SELECT name AS 테이블 FROM sqlite_master WHERE type='table' ORDER BY 1")"""


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def py(code):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": code.splitlines(keepends=True)}


def sql_cell(comment, sql):
    return py(f"# {comment}\nq(\"\"\"\n{sql.strip()}\n\"\"\")")


def run_cell(comment, sql):
    return py(f"# {comment}\nrun(\"\"\"\n{sql.strip()}\n\"\"\")")


def exercise(no, question, hint=None, kind="q"):
    """kind='q'는 조회 문제, kind='run'은 DDL/DML 문제(결과셋이 없으므로 run 사용)"""
    h = f"\n# 힌트: {hint}" if hint else ""
    return py(f"# [연습 Q{no}] {question}{h}\n{kind}(\"\"\"\n-- 여기에 SQL을 작성하세요\n\n\"\"\")")


# ======================================================================
# 주차별 콘텐츠: (week, slug, title, cells, answers)
# answers: [(번호, 질문, SQL)] — 노트북 끝 '정답' 섹션과 .sql 파일에 수록
# ======================================================================
WEEKS = []

WEEKS.append((3, "select1", "SELECT ① 조회의 기본기", [
    md("## 1. SELECT — 전부, 혹은 골라서"),
    sql_cell("환자 테이블 전체 (LIMIT으로 자르기)", "SELECT * FROM patient LIMIT 5"),
    sql_cell("특정 컬럼만", "SELECT patient_id, birth_date FROM patient LIMIT 5"),
    sql_cell("별칭(AS)", "SELECT patient_id AS 환자번호, blood_type AS 혈액형 FROM patient LIMIT 5"),
    md("## 2. DISTINCT — 값의 종류 탐색"),
    sql_cell("우리 병원의 진료과 목록", "SELECT DISTINCT department FROM visit ORDER BY 1"),
    sql_cell("의료진 직종 목록", "SELECT DISTINCT role FROM staff"),
    md("## 3. ORDER BY · LIMIT"),
    sql_cell("나이 많은 순 (생년월일 오름차순)", "SELECT patient_id, birth_date, sex FROM patient ORDER BY birth_date ASC LIMIT 10"),
    sql_cell("가장 최근 내원 5건", "SELECT visit_id, patient_id, visit_date, department\nFROM visit ORDER BY visit_date DESC LIMIT 5"),
    md("## 연습문제 — 먼저 직접 풀어보세요"),
    exercise(1, "검사(lab) 테이블에는 어떤 검사 종류들이 있는가?", "DISTINCT"),
    exercise(2, "처방에서 약품명과 용량만, 약품명 가나다순으로", "ORDER BY"),
    exercise(3, "가장 어린 환자 3명의 ID와 생년월일은?", "birth_date DESC + LIMIT"),
    exercise(4, "영상(imaging) 테이블의 촬영종류 목록은?"),
], [
    (1, "검사 종류", "SELECT DISTINCT test_name FROM lab ORDER BY 1;"),
    (2, "약품명·용량 가나다순", "SELECT drug_name, dose FROM prescription ORDER BY drug_name;"),
    (3, "가장 어린 환자 3명", "SELECT patient_id, birth_date FROM patient ORDER BY birth_date DESC LIMIT 3;"),
    (4, "촬영종류 목록", "SELECT DISTINCT modality FROM imaging;"),
]))

WEEKS.append((4, "where", "SELECT ② WHERE 조건", [
    md("## 1. 비교 연산과 날짜"),
    sql_cell("여성 환자", "SELECT patient_id, sex, birth_date FROM patient WHERE sex = 'F' LIMIT 8"),
    sql_cell("1950년 이전 출생", "SELECT patient_id, birth_date FROM patient\nWHERE birth_date < '1950-01-01' ORDER BY birth_date"),
    md("## 2. AND / OR / IN / BETWEEN"),
    sql_cell("65세 이상 여성 — 나이 조건을 출생연도 조건으로 (2026년 기준 65세 이상 = 1961년 이전 출생)",
             "SELECT patient_id, sex, birth_date\nFROM patient\nWHERE sex = 'F'\n  AND birth_date <= '1961-12-31'\nORDER BY birth_date"),
    sql_cell("응급 또는 입원 (IN)", "SELECT visit_id, visit_date, visit_type FROM visit\nWHERE visit_type IN ('응급','입원') ORDER BY visit_date DESC LIMIT 8"),
    sql_cell("2024년 내원 (BETWEEN)", "SELECT visit_id, visit_date, department FROM visit\nWHERE visit_date BETWEEN '2024-01-01' AND '2024-12-31'"),
    md("## 3. LIKE — 코드 패턴"),
    sql_cell("순환기계(I코드) 진단 전체", "SELECT dx_id, kcd_code, dx_name FROM diagnosis\nWHERE kcd_code LIKE 'I%' ORDER BY kcd_code LIMIT 10"),
    sql_cell("당뇨(E11) 패밀리", "SELECT DISTINCT kcd_code, dx_name FROM diagnosis WHERE kcd_code LIKE 'E11%'"),
    md("## 4. IS NULL"),
    sql_cell("퇴원일이 없는 내원 (외래·응급 귀가)", "SELECT visit_id, visit_type, visit_date, discharge_date\nFROM visit WHERE discharge_date IS NULL LIMIT 8"),
    md("⚠️ `discharge_date = NULL` 로 바꿔 실행해 보세요 — **아무 행도 안 나옵니다.** NULL은 `IS NULL`로만."),
    md("## 연습문제"),
    exercise(1, "남성이면서 O+ 혈액형인 환자는?"),
    exercise(2, "2023년 이후 신경과 내원을 최신순으로"),
    exercise(3, "호흡기계(J코드) 진단을 모두 찾아라", "LIKE 'J%'"),
    exercise(4, "투약일수가 30~90일인 처방은?", "BETWEEN"),
    exercise(5, "정상 상한(ref_high)이 기록되지 않은 검사가 있는가?", "IS NULL"),
], [
    (1, "남성 O+", "SELECT * FROM patient WHERE sex = 'M' AND blood_type = 'O+';"),
    (2, "2023년 이후 신경과", "SELECT * FROM visit WHERE department = '신경과' AND visit_date >= '2023-01-01' ORDER BY visit_date DESC;"),
    (3, "J코드 진단", "SELECT * FROM diagnosis WHERE kcd_code LIKE 'J%';"),
    (4, "30~90일 처방", "SELECT * FROM prescription WHERE duration_days BETWEEN 30 AND 90;"),
    (5, "ref_high 없는 검사", "SELECT * FROM lab WHERE ref_high IS NULL;  -- 이 데이터셋에서는 0행이 정답"),
]))

WEEKS.append((5, "calc_agg", "SELECT ③ 계산·CASE·집계", [
    md("## 1. 산술식 — 재원일수"),
    sql_cell("입원별 재원일수(LOS)",
             "SELECT visit_id, visit_date, discharge_date,\n       julianday(discharge_date) - julianday(visit_date) AS los\nFROM visit WHERE visit_type = '입원' ORDER BY los DESC LIMIT 8"),
    sql_cell("나이 계산 — substr(연도 자르기) + CAST(숫자 변환), 연 나이 근사",
             "SELECT patient_id, birth_date,\n       2026 - CAST(substr(birth_date,1,4) AS INT) AS age\nFROM patient ORDER BY age DESC LIMIT 5"),
    md("## 2. CASE — 측정치 구간 분류"),
    sql_cell("혈압 측정치 3구간 (측정 1회의 구간 분류 — 진단 아님, 경계값은 예시)",
             "SELECT visit_id, sbp, dbp,\n  CASE WHEN sbp >= 140 OR dbp >= 90 THEN '고혈압 범위'\n       WHEN sbp >= 120 THEN '주의 범위'\n       ELSE '정상 범위' END AS bp_range\nFROM vital ORDER BY sbp DESC LIMIT 10"),
    md("## 3. 집계함수"),
    sql_cell("입원 요약: 건수·평균·최장",
             "SELECT COUNT(*) AS 입원건수,\n       ROUND(AVG(julianday(discharge_date) - julianday(visit_date)), 1) AS 평균재원일,\n       MAX(julianday(discharge_date) - julianday(visit_date)) AS 최장재원일\nFROM visit WHERE visit_type = '입원'"),
    sql_cell("정상범위 벗어난 검사 비율 (CASE×SUM 패턴) — 분모는 결과값이 있는 검사만",
             "SELECT COUNT(*) AS 전체검사,\n  COUNT(result_value) AS 판정가능검사,\n  SUM(CASE WHEN result_value > ref_high OR result_value < ref_low THEN 1 ELSE 0 END) AS 이상건수,\n  ROUND(100.0 * SUM(CASE WHEN result_value > ref_high OR result_value < ref_low THEN 1 ELSE 0 END) / COUNT(result_value), 1) AS 이상비율\nFROM lab"),
    md("분모를 `COUNT(*)`로 두면 결과값이 NULL이라 판정 불가능한 검사까지 '정상'처럼 분모에 들어갑니다. 이 데이터셋의 정상범위(ref_low/ref_high)는 모두 채워져 있어 `COUNT(result_value)`면 충분합니다."),
    sql_cell("COUNT(*) vs COUNT(컬럼) — NULL의 조용한 제외",
             "SELECT COUNT(*) AS 전체행수, COUNT(result_value) AS 값있는행수,\n       COUNT(*) - COUNT(result_value) AS 결측행수\nFROM lab"),
    md("## 연습문제"),
    exercise(1, "처방의 평균 투약일수는?"),
    exercise(2, "맥박을 서맥(<60)·정상·빈맥(>100)으로 분류해 보라", "CASE"),
    exercise(3, "HbA1c 검사의 최솟값·최댓값·평균은?", "WHERE test_name='HbA1c'"),
    exercise(4, "HbA1c가 7.0 이상인 검사 건수의 비율은?", "CASE×SUM, 100.0"),
    exercise(5, "입원 재원일수가 14일을 넘는 내원은 몇 건인가?"),
], [
    (1, "평균 투약일수", "SELECT ROUND(AVG(duration_days),1) FROM prescription;"),
    (2, "맥박 분류", "SELECT visit_id, pulse, CASE WHEN pulse < 60 THEN '서맥' WHEN pulse > 100 THEN '빈맥' ELSE '정상' END AS grade FROM vital;"),
    (3, "HbA1c 요약", "SELECT MIN(result_value), MAX(result_value), ROUND(AVG(result_value),1) FROM lab WHERE test_name='HbA1c';"),
    (4, "HbA1c≥7.0 비율", "SELECT ROUND(100.0*SUM(CASE WHEN result_value>=7.0 THEN 1 ELSE 0 END)/COUNT(*),1) FROM lab WHERE test_name='HbA1c';"),
    (5, "14일 초과 입원", "SELECT COUNT(*) FROM visit WHERE visit_type='입원' AND julianday(discharge_date)-julianday(visit_date) > 14;"),
]))

WEEKS.append((6, "groupby", "SELECT ④ GROUP BY·HAVING", [
    md("## 1. GROUP BY"),
    sql_cell("진료과별 내원 건수와 환자 수 — 둘의 차이에 주목!",
             "SELECT department, COUNT(*) AS 내원건수,\n       COUNT(DISTINCT patient_id) AS 환자수\nFROM visit GROUP BY department ORDER BY 내원건수 DESC"),
    sql_cell("내원유형별 평균 재원일수",
             "SELECT visit_type, COUNT(*) AS 건수,\n       ROUND(AVG(julianday(discharge_date) - julianday(visit_date)), 1) AS 평균재원일\nFROM visit GROUP BY visit_type"),
    sql_cell("월별 내원 추이 (2025년)",
             "SELECT strftime('%Y-%m', visit_date) AS 월, COUNT(*) AS 내원건수\nFROM visit WHERE visit_date >= '2025-01-01'\nGROUP BY strftime('%Y-%m', visit_date) ORDER BY 월"),
    md("## 2. HAVING"),
    sql_cell("10건 이상 처방된 약물",
             "SELECT drug_name, COUNT(*) AS 처방건수\nFROM prescription GROUP BY drug_name\nHAVING COUNT(*) >= 10 ORDER BY 처방건수 DESC"),
    md("## 3. Table 1 맛보기"),
    sql_cell("성별 × 연령군 분포",
             "SELECT sex,\n  CASE WHEN 2026 - CAST(substr(birth_date,1,4) AS INT) >= 65\n       THEN '65세 이상' ELSE '65세 미만' END AS 연령군,\n  COUNT(*) AS 명수\nFROM patient GROUP BY sex, 연령군 ORDER BY sex, 연령군"),
    md("## 연습문제"),
    exercise(1, "KCD 코드별 진단 건수를 많은 순으로"),
    exercise(2, "검사 종류별 평균 결과값과 검사 건수는?"),
    exercise(3, "5회 이상 내원한 환자의 ID와 내원 횟수는?", "GROUP BY patient_id + HAVING"),
    exercise(4, "혈액형별 환자 수 분포는?"),
    exercise(5, "연도별 입원 건수 추이는?", "strftime('%Y', …)"),
], [
    (1, "KCD별 진단 건수", "SELECT kcd_code, dx_name, COUNT(*) AS n FROM diagnosis GROUP BY kcd_code, dx_name ORDER BY n DESC;"),
    (2, "검사별 평균", "-- COUNT(*)와 COUNT(result_value)를 함께 — 평균의 분모는 후자다\nSELECT test_name, ROUND(AVG(result_value),2) AS 평균,\n       COUNT(*) AS 전체건수, COUNT(result_value) AS 값있는건수\nFROM lab GROUP BY test_name;"),
    (3, "5회 이상 내원", "SELECT patient_id, COUNT(*) AS n FROM visit GROUP BY patient_id HAVING COUNT(*) >= 5 ORDER BY n DESC;"),
    (4, "혈액형 분포", "SELECT blood_type, COUNT(*) FROM patient GROUP BY blood_type ORDER BY 2 DESC;"),
    (5, "연도별 입원", "SELECT strftime('%Y', visit_date) AS 연도, COUNT(*) FROM visit WHERE visit_type='입원' GROUP BY 연도 ORDER BY 연도;"),
]))

WEEKS.append((7, "ddl", "DDL — 테이블 설계와 생성", [
    md("## 1. CREATE TABLE — 제약조건과 함께\n이 노트북은 **사본 DB**(`mini_emr_practice.sqlite`)에서 실습합니다 — 자유롭게 만들었다 지워도 됩니다. 막히면 `reset_db()`."),
    run_cell("코호트 테이블 생성",
             "CREATE TABLE IF NOT EXISTS my_cohort (\n  subject_id   TEXT PRIMARY KEY,\n  patient_id   TEXT NOT NULL REFERENCES patient(patient_id),\n  index_date   DATE NOT NULL,\n  age_at_index INTEGER CHECK (age_at_index BETWEEN 0 AND 120),\n  sex          TEXT NOT NULL CHECK (sex IN ('M','F')),\n  dm_flag      INTEGER NOT NULL DEFAULT 0 CHECK (dm_flag IN (0,1))\n);"),
    sql_cell("생성 확인", "SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1"),
    md("## 2. 제약조건이 일하는 순간 — 아래 셀은 **일부러 에러**가 납니다"),
    py("# CHECK 위반 실험: SpO2 250%는 입력 자체가 거부된다\ntry:\n    run(\"\"\"\n    CREATE TABLE IF NOT EXISTS vital_demo (visit_id TEXT, spo2 INTEGER CHECK (spo2 BETWEEN 0 AND 100));\n    INSERT INTO vital_demo VALUES ('V0001', 250);\n    \"\"\")\nexcept Exception as e:\n    print('거부됨 →', e)"),
    md("## 3. ALTER / DROP"),
    run_cell("컬럼 추가 후 테이블 정리 — 이 셀을 두 번 실행하면 duplicate column 에러 (이미 있는 컬럼은 재추가 불가 — reset_db() 후 재실행)",
             "ALTER TABLE my_cohort ADD COLUMN htn_flag INTEGER DEFAULT 0;\nDROP TABLE IF EXISTS vital_demo;"),
    md("## 연습문제\nDDL 문제는 결과 표가 없으므로 `q()`가 아닌 `run()` 안에 작성합니다."),
    exercise(1, "'수술(operation)' 테이블을 설계해 CREATE 하라 — 수술ID(PK), 내원ID(FK), 수술명(NOT NULL), 수술일, 집도의ID(FK)", kind="run"),
    exercise(2, "operation에 마취종류 컬럼을 ALTER로 추가해 보라 — CHECK 제약까지 걸려면 왜 어려운지 겪어보기", kind="run"),
    exercise(3, "자기 연구 주제의 코호트 테이블을 컬럼 6개 이상으로 설계하라 (과제 제출용)", kind="run"),
], [
    (1, "수술 테이블", "CREATE TABLE operation (\n  op_id TEXT PRIMARY KEY,\n  visit_id TEXT NOT NULL REFERENCES visit(visit_id),\n  op_name TEXT NOT NULL,\n  op_date DATE,\n  surgeon_id TEXT REFERENCES staff(staff_id)\n);"),
    (2, "마취종류 추가", "-- SQLite의 ALTER는 CHECK 추가를 지원하지 않음 → 테이블 재생성 필요.\n-- 교훈: 제약조건은 처음 설계할 때 넣는 것이 훨씬 싸다.\nALTER TABLE operation ADD COLUMN anesthesia TEXT;"),
]))

WEEKS.append((8, "dml", "DML — 입력·수정·삭제와 트랜잭션", [
    md("## 1. INSERT\n이 노트북은 **사본 DB**에서 실습합니다. 아래 셀을 두 번 실행하면 PK 중복 에러가 납니다 — 기본키가 정상 동작하는 것입니다. `reset_db()` 후 다시 실행하세요."),
    run_cell("가상 환자 P051 등록 (재실행 시 PK 중복 에러 = 정상)",
             "INSERT INTO patient (patient_id, sex, birth_date, blood_type)\nVALUES ('P051', 'F', '1988-03-15', 'A+');"),
    sql_cell("확인", "SELECT * FROM patient WHERE patient_id = 'P051'"),
    py("# FK가 실제로 켜져 있는지 확인 — 존재하지 않는 내원(V9999)에 처방을 넣어 본다\ntry:\n    run(\"\"\"\n    INSERT INTO prescription (rx_id, visit_id, drug_code, drug_name, dose, duration_days)\n    VALUES ('R9999', 'V9999', 'MET500', '메트포르민', '500mg', 30);\n    \"\"\")\nexcept Exception as e:\n    print('거부됨 →', e)   # FOREIGN KEY constraint failed — 참조 무결성(2주차)"),
    md("## 2. UPDATE — WHERE 확인 습관"),
    sql_cell("① 먼저 SELECT로 대상 확인", "SELECT lab_id, test_name, result_value FROM lab WHERE lab_id = 'L0044'"),
    run_cell("② 그 다음 UPDATE", "UPDATE lab SET result_value = 176 WHERE lab_id = 'L0044';"),
    sql_cell("③ 결과 재확인", "SELECT lab_id, test_name, result_value FROM lab WHERE lab_id = 'L0044'"),
    md("## 3. 트랜잭션 — 없던 일로 만들기"),
    py("# BEGIN → UPDATE → ROLLBACK: WHERE 절이 없는 UPDATE의 영향을 확인하고 되돌린다\ncur = con.cursor()\ncur.execute(\"BEGIN\")\ncur.execute(\"UPDATE lab SET result_value = 0\")\nprint('UPDATE 직후:', cur.execute(\"SELECT COUNT(*) FROM lab WHERE result_value = 0\").fetchone())\ncon.rollback()\nprint('롤백 후   :', cur.execute(\"SELECT COUNT(*) FROM lab WHERE result_value = 0\").fetchone())"),
    md("## 4. soft delete + 감사로그 패턴"),
    run_cell("감사로그 테이블과 정정 이력 남기기 (재실행하면 이력이 한 건씩 쌓임 — reset_db()로 초기화)",
             "CREATE TABLE IF NOT EXISTS lab_audit (\n  audit_id INTEGER PRIMARY KEY,\n  lab_id TEXT, old_value REAL, new_value REAL,\n  changed_by TEXT, changed_at DATETIME, reason TEXT\n);\nINSERT INTO lab_audit (lab_id, old_value, new_value, changed_by, changed_at, reason)\nVALUES ('L0044', 167, 176, 'S001', '2026-04-02 09:30', '재검 결과 반영');"),
    sql_cell("감사로그 확인", "SELECT * FROM lab_audit"),
    md("## 연습문제\nQ1·Q2·Q4는 데이터를 바꾸는 문제이므로 `run()` 안에, 결과 확인은 별도 `q()` 셀에서 하세요."),
    exercise(1, "P051의 외래 내원 한 건을 visit에 INSERT 하라 (visit_id는 'V0101' 등 새 값)", kind="run"),
    exercise(2, "P051의 혈액형을 B+로 정정하라 — 먼저 q()로 SELECT 확인 후, 이 셀에서 UPDATE", kind="run"),
    exercise(3, "WHERE 없는 UPDATE를 실행해 피해 규모를 q()로 확인한 뒤, reset_db()로 복구하라", kind="run"),
    exercise(4, "lab_audit에 '단위 오입력 정정' 이력을 한 건 더 남겨 보라", kind="run"),
], [
    (1, "P051 내원", "INSERT INTO visit (visit_id, patient_id, visit_date, department, visit_type)\nVALUES ('V0101', 'P051', '2026-04-01', '가정의학과', '외래');"),
    (2, "혈액형 정정", "SELECT * FROM patient WHERE patient_id='P051';\nUPDATE patient SET blood_type='B+' WHERE patient_id='P051';\nSELECT * FROM patient WHERE patient_id='P051';"),
]))

WEEKS.append((11, "join", "JOIN — 테이블 연결", [
    md("## 1. INNER JOIN"),
    sql_cell("내원 + 환자 정보",
             "SELECT v.visit_id, v.visit_date, v.department, p.sex, p.birth_date\nFROM visit v\nJOIN patient p ON v.patient_id = p.patient_id\nLIMIT 8"),
    sql_cell("3테이블: 내원 + 환자 + 담당의",
             "SELECT v.visit_id, v.visit_date, p.sex AS 환자성별, s.role, s.department AS 소속과\nFROM visit v\nJOIN patient p ON v.patient_id = p.patient_id\nJOIN staff s ON v.attending_id = s.staff_id\nWHERE v.visit_type = '입원' ORDER BY v.visit_date DESC LIMIT 8"),
    md("## 2. 대표 질문 — 당뇨 환자들의 HbA1c (한 단계씩)"),
    sql_cell("① 같은 내원 안에서: 당뇨 진단이 붙은 그 내원의 HbA1c",
             "SELECT d.kcd_code, l.test_name, l.result_value, l.collected_at\nFROM diagnosis d\nJOIN lab l ON l.visit_id = d.visit_id\nWHERE d.kcd_code LIKE 'E11%' AND l.test_name = 'HbA1c'\nORDER BY l.collected_at"),
    md("①은 진단과 검사가 **같은 내원**에 있을 때만 잡습니다. 다른 내원의 검사까지 보려면 visit을 한 번 더 통과해 '같은 환자의 모든 내원'으로 확장합니다."),
    sql_cell("② 환자 단위로 확장: 당뇨(E11) 환자의 모든 HbA1c 결과",
             "SELECT DISTINCT v.patient_id, l.result_value AS hba1c, l.collected_at\nFROM diagnosis d\nJOIN visit v  ON d.visit_id = v.visit_id\nJOIN visit v2 ON v2.patient_id = v.patient_id\nJOIN lab l    ON l.visit_id = v2.visit_id\nWHERE d.kcd_code LIKE 'E11%' AND l.test_name = 'HbA1c'\nORDER BY v.patient_id, l.collected_at"),
    md("## 3. LEFT JOIN — 없는 사람이 보인다"),
    sql_cell("당뇨 환자 전원 + HbA1c 검사 건수·최근 검사시각 (NULL = 미검사)",
             "SELECT dm.patient_id,\n       COUNT(l.lab_id) AS 검사건수,\n       MAX(l.collected_at) AS 최근검사시각\nFROM (SELECT DISTINCT v.patient_id\n      FROM diagnosis d JOIN visit v ON d.visit_id = v.visit_id\n      WHERE d.kcd_code LIKE 'E11%') dm\nLEFT JOIN visit v2 ON v2.patient_id = dm.patient_id\nLEFT JOIN lab l ON l.visit_id = v2.visit_id AND l.test_name = 'HbA1c'\nGROUP BY dm.patient_id"),
    md("주의: `GROUP BY` 후에 집계함수 없이 `l.result_value` 같은 일반 컬럼을 SELECT하면 SQLite는 **임의의 한 행 값**을 돌려줍니다 — 최신값도 최대값도 아닙니다. 반드시 COUNT/MAX 등 집계함수로 의도를 명시하세요."),
    sql_cell("HbA1c를 한 번도 안 받은 당뇨 환자",
             "SELECT DISTINCT v.patient_id\nFROM diagnosis d JOIN visit v ON d.visit_id = v.visit_id\nWHERE d.kcd_code LIKE 'E11%'\n  AND v.patient_id NOT IN (\n    SELECT v2.patient_id FROM lab l\n    JOIN visit v2 ON l.visit_id = v2.visit_id\n    WHERE l.test_name = 'HbA1c')"),
    md("이 NOT IN은 하위 명단에 NULL이 없어 안전하게 동작합니다 — NULL이 섞이면 어떻게 되는지는 **다음 주(서브쿼리)의 핵심 주제**입니다."),
    md("## 연습문제"),
    exercise(1, "각 진단(dx_name)에 해당 환자의 성별을 붙여 출력하라", "diagnosis→visit→patient"),
    exercise(2, "뇌 MRI를 찍은 내원의 환자ID·촬영일·판독문을 출력하라", "imaging + visit"),
    exercise(3, "영상 검사를 한 번도 안 받은 환자는 몇 명인가?", "LEFT JOIN … IS NULL 또는 NOT IN"),
    exercise(4, "폐렴(J18) 내원에서 나간 약물 목록을 만들라", "diagnosis + prescription, 내원 기준"),
], [
    (1, "진단+성별", "SELECT d.dx_name, p.sex FROM diagnosis d\nJOIN visit v ON d.visit_id = v.visit_id\nJOIN patient p ON v.patient_id = p.patient_id;"),
    (2, "뇌 MRI", "SELECT v.patient_id, i.taken_date, i.report FROM imaging i\nJOIN visit v ON i.visit_id = v.visit_id\nWHERE i.modality = 'MRI' AND i.body_part = '뇌';"),
    (3, "영상 없는 환자 수", "-- 하위 명단에 NULL이 없어 NOT IN이 안전 (NULL 위험은 12주차에서)\nSELECT COUNT(*) FROM patient p\nWHERE p.patient_id NOT IN (\n  SELECT v.patient_id FROM imaging i JOIN visit v ON i.visit_id = v.visit_id);"),
    (4, "폐렴 약물", "SELECT DISTINCT rx.drug_name FROM diagnosis d\nJOIN prescription rx ON rx.visit_id = d.visit_id\nWHERE d.kcd_code LIKE 'J18%';"),
]))

WEEKS.append((12, "subquery", "서브쿼리", [
    md("## 1. 스칼라 서브쿼리"),
    sql_cell("평균보다 오래 입원한 환자",
             "SELECT visit_id, patient_id,\n       julianday(discharge_date) - julianday(visit_date) AS los\nFROM visit\nWHERE visit_type = '입원'\n  AND julianday(discharge_date) - julianday(visit_date) >\n      (SELECT AVG(julianday(discharge_date) - julianday(visit_date))\n       FROM visit WHERE visit_type = '입원')\nORDER BY los DESC"),
    md("## 2. IN 서브쿼리"),
    sql_cell("I63 진단 이력자의 인적 정보",
             "SELECT patient_id, sex, birth_date FROM patient\nWHERE patient_id IN (\n  SELECT v.patient_id FROM visit v\n  JOIN diagnosis d ON v.visit_id = d.visit_id\n  WHERE d.kcd_code LIKE 'I63%')"),
    md("## 3. EXISTS / NOT EXISTS"),
    sql_cell("항생제를 한 번도 처방받지 않은 환자 수",
             "SELECT COUNT(*) AS 무항생제환자수\nFROM patient p\nWHERE NOT EXISTS (\n  SELECT 1 FROM visit v\n  JOIN prescription rx ON rx.visit_id = v.visit_id\n  WHERE v.patient_id = p.patient_id\n    AND rx.drug_code IN ('CTX2','AMC625','LVX500'))"),
    sql_cell("항생제 노출군과 약물",
             "SELECT DISTINCT v.patient_id, rx.drug_name\nFROM visit v JOIN prescription rx ON rx.visit_id = v.visit_id\nWHERE rx.drug_code IN ('CTX2','AMC625','LVX500')\nORDER BY v.patient_id"),
    md("## 연습문제"),
    exercise(1, "평균 투약일수보다 길게 처방된 약물 행은?", "스칼라 서브쿼리"),
    exercise(2, "폐렴(J18) 진단 이력이 있는 환자의 성별·생년월일은?", "IN"),
    exercise(3, "검사(lab)를 한 번도 받지 않은 환자 수는?", "NOT EXISTS"),
    exercise(4, "자기 진료과 평균보다 재원이 길었던 입원 건은?", "상관 서브쿼리 (도전)"),
    exercise(5, "Q3를 NOT IN으로도 써 보고, NULL이 끼면 어떻게 되는지 설명해 보라"),
], [
    (1, "평균 초과 투약", "SELECT * FROM prescription\nWHERE duration_days > (SELECT AVG(duration_days) FROM prescription);"),
    (2, "폐렴 이력자", "SELECT patient_id, sex, birth_date FROM patient\nWHERE patient_id IN (SELECT v.patient_id FROM visit v\n  JOIN diagnosis d ON d.visit_id = v.visit_id WHERE d.kcd_code LIKE 'J18%');"),
    (3, "검사 무이력", "SELECT COUNT(*) FROM patient p WHERE NOT EXISTS (\n  SELECT 1 FROM visit v JOIN lab l ON l.visit_id = v.visit_id\n  WHERE v.patient_id = p.patient_id);"),
    (4, "진료과 평균 초과 재원", "-- 별칭(los)은 표준 SQL의 WHERE에서 쓸 수 없어 식을 반복한다\nSELECT v.visit_id, v.department,\n  julianday(v.discharge_date)-julianday(v.visit_date) AS los\nFROM visit v WHERE v.visit_type='입원'\n  AND julianday(v.discharge_date)-julianday(v.visit_date)\n      > (SELECT AVG(julianday(v2.discharge_date)-julianday(v2.visit_date))\n         FROM visit v2 WHERE v2.visit_type='입원' AND v2.department = v.department);"),
]))

WEEKS.append((13, "cohort", "실전 — 코호트 추출과 Table 1", [
    md("## 연구 질문\n**\"2020년 1월 1일 이후 처음으로 뇌경색(I63)을 진단받은 환자\"** 코호트를 만들고 Table 1까지 완성한다."),
    md("## 1단계 — 후보군: I63 이력자 전체와 첫 진단일"),
    sql_cell("첫 진단일 (washout 적용 전 — 10명)",
             "SELECT v.patient_id, MIN(v.visit_date) AS first_dx_date\nFROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id\nWHERE d.kcd_code LIKE 'I63%'\nGROUP BY v.patient_id ORDER BY first_dx_date"),
    md("## 2단계 — 신규 환자 제한: 관찰된 '첫' 진단이 2020년 이후\n엄밀한 washout은 index date 이전 일정 기간(look-back)의 이력 부재를 확인하는 것입니다. 이 데이터셋은 관찰이 2019년부터 시작되므로, `MIN(진단일) >= '2020-01-01'`은 **약 1년의 look-back**에 해당하는 간이 조건입니다 — 정의서에는 이런 한계를 명시해야 합니다."),
    sql_cell("index date 확정 (8명 — P029·P030은 2019년 진단력으로 제외)",
             "SELECT v.patient_id, MIN(v.visit_date) AS index_date\nFROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id\nWHERE d.kcd_code LIKE 'I63%'\nGROUP BY v.patient_id\nHAVING MIN(v.visit_date) >= '2020-01-01'\nORDER BY index_date"),
    md("## 3단계 — WITH(CTE)로 특성 붙이기\n나이는 연도 차이(연 나이) 근사입니다 — 생일 미도래 환자는 1세 크게 계산될 수 있습니다."),
    sql_cell("코호트 + 성별 + index 시점 나이(연 나이 근사)",
             "WITH stroke_cohort AS (\n  SELECT v.patient_id, MIN(v.visit_date) AS index_date\n  FROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id\n  WHERE d.kcd_code LIKE 'I63%'\n  GROUP BY v.patient_id\n  HAVING MIN(v.visit_date) >= '2020-01-01')\nSELECT c.patient_id, c.index_date, p.sex,\n       CAST(substr(c.index_date,1,4) AS INT)\n         - CAST(substr(p.birth_date,1,4) AS INT) AS age_at_index\nFROM stroke_cohort c JOIN patient p ON p.patient_id = c.patient_id"),
    md("## 4단계 — 기저 동반질환 플래그 (EXISTS)\n기저(baseline) 동반질환이므로 **index date 이전(당일 포함)** 이력만 세야 합니다 — 시간 조건이 없으면 뇌경색 이후에 생긴 고혈압까지 '기저'로 잘못 집계됩니다. 아래는 이 강의의 조작적 정의(operational definition)이며, 실제 연구에서는 look-back 기간까지 명시합니다."),
    sql_cell("고혈압(I10) 기저 동반 여부 — index date 이전 이력만",
             "WITH stroke_cohort AS (\n  SELECT v.patient_id, MIN(v.visit_date) AS index_date\n  FROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id\n  WHERE d.kcd_code LIKE 'I63%'\n  GROUP BY v.patient_id\n  HAVING MIN(v.visit_date) >= '2020-01-01')\nSELECT c.patient_id, c.index_date,\n  CASE WHEN EXISTS (\n    SELECT 1 FROM visit v2 JOIN diagnosis d2 ON d2.visit_id = v2.visit_id\n    WHERE v2.patient_id = c.patient_id\n      AND d2.kcd_code LIKE 'I10%'\n      AND v2.visit_date <= c.index_date)\n  THEN 1 ELSE 0 END AS htn_baseline\nFROM stroke_cohort c"),
    md("## 5단계 — Table 1"),
    sql_cell("성별·평균나이 요약",
             "WITH stroke_cohort AS (\n  SELECT v.patient_id, MIN(v.visit_date) AS index_date\n  FROM visit v JOIN diagnosis d ON d.visit_id = v.visit_id\n  WHERE d.kcd_code LIKE 'I63%'\n  GROUP BY v.patient_id\n  HAVING MIN(v.visit_date) >= '2020-01-01')\nSELECT p.sex AS 성별, COUNT(*) AS 명수,\n  ROUND(AVG(CAST(substr(c.index_date,1,4) AS INT)\n    - CAST(substr(p.birth_date,1,4) AS INT)), 1) AS 평균나이\nFROM stroke_cohort c JOIN patient p ON p.patient_id = c.patient_id\nGROUP BY p.sex"),
    md("## 프로젝트 스타터 — 이 뼈대를 복사해 조별 주제로 바꾸세요"),
    py("# [프로젝트 템플릿]\nCOHORT_SQL = \"\"\"\nWITH my_cohort AS (\n  -- ① 포함 기준: 코드/기간을 조별 주제로 교체\n  SELECT v.patient_id, MIN(v.visit_date) AS index_date\n  FROM visit v JOIN diagnosis d ON d.visit_id = v.visit_id\n  WHERE d.kcd_code LIKE '__%'          -- ← 여기\n  GROUP BY v.patient_id\n  HAVING MIN(v.visit_date) >= '2020-01-01'  -- ← washout 기준\n)\nSELECT c.*, p.sex FROM my_cohort c\nJOIN patient p ON p.patient_id = c.patient_id\n\"\"\"\n# q(COHORT_SQL)  # 주석을 풀어 실행"),
], [
    (0, "프로젝트 체크리스트",
     "-- ① 포함 기준(코드·기간)과 제외 기준을 정의서에 먼저 글로 쓴다\n-- ② 단계마다 대상자 수를 주석으로 남긴다 (attrition)\n-- ③ Table 1 변수는 성별·연령 + 조별 선택 2개 이상"),
]))

WEEKS.append((14, "pitfall", "함정·보안·비정형", [
    md("## 함정 ① 단위 불일치"),
    sql_cell("혈당을 낮은 값부터 — 이 7.8은 저혈당인가?",
             "SELECT lab_id, test_name, result_value, unit\nFROM lab WHERE test_name = 'Glucose'\nORDER BY result_value LIMIT 5"),
    sql_cell("단위 감사 쿼리 — 분석 전 사전 점검",
             "SELECT test_name, unit, COUNT(*) AS 건수,\n       MIN(result_value) AS 최소, MAX(result_value) AS 최대\nFROM lab GROUP BY test_name, unit ORDER BY test_name"),
    md("## 함정 ② 분모 — '검사받은 사람만'의 평균"),
    sql_cell("당뇨 환자 수 vs 그중 HbA1c 검사자 수",
             "SELECT\n  (SELECT COUNT(DISTINCT v.patient_id) FROM visit v\n   JOIN diagnosis d ON d.visit_id = v.visit_id\n   WHERE d.kcd_code LIKE 'E11%') AS 당뇨환자수,\n  (SELECT COUNT(DISTINCT v.patient_id) FROM visit v\n   JOIN lab l ON l.visit_id = v.visit_id\n   WHERE l.test_name = 'HbA1c'\n     AND v.patient_id IN (\n       SELECT v2.patient_id FROM visit v2\n       JOIN diagnosis d2 ON d2.visit_id = v2.visit_id\n       WHERE d2.kcd_code LIKE 'E11%')) AS 당뇨환자중검사자수"),
    md("## 함정 ③ 비정형 텍스트의 한계"),
    sql_cell("판독문 LIKE 검색 — '경색'이 들어간 보고서",
             "SELECT img_id, modality, body_part, report\nFROM imaging WHERE report LIKE '%경색%'"),
    md("⚠️ \"급성 경색 **소견 없음**\" 같은 부정 표현도 걸립니다 — 텍스트의 의미는 LIKE가 이해하지 못합니다."),
    md("## 연습문제"),
    exercise(1, "mmol/L로 입력된 혈당을 mg/dL로 환산하면 얼마인가? (×18) — SELECT로 환산값을 계산해 보라"),
    exercise(2, "채혈시각(collected_at)의 시(hour) 분포를 구하라 — 오후 채혈이 섞여 있는가?", "strftime('%H', collected_at)"),
    exercise(3, "각 검사(test_name)의 결측(result_value IS NULL) 건수를 세어 보라"),
    exercise(4, "판독문에 '없음'이 포함된 영상 보고서를 찾아, LIKE 검색의 함정을 확인하라"),
], [
    (1, "단위 환산", "-- ×18은 포도당에만 유효한 환산 — 검사명 조건을 반드시 함께\nSELECT lab_id, result_value AS mmol, ROUND(result_value * 18, 0) AS mgdl\nFROM lab WHERE test_name = 'Glucose' AND unit = 'mmol/L';"),
    (2, "채혈 시각 분포", "SELECT strftime('%H', collected_at) AS 시, COUNT(*) FROM lab GROUP BY 시 ORDER BY 시;"),
    (3, "검사별 결측", "SELECT test_name, SUM(CASE WHEN result_value IS NULL THEN 1 ELSE 0 END) AS 결측 FROM lab GROUP BY test_name;"),
    (4, "부정 표현", "SELECT img_id, report FROM imaging WHERE report LIKE '%없음%';"),
]))


# ======================================================================
PRACTICE_WEEKS = {7, 8}   # 데이터를 의도적으로 변경하는 주차 — 사본 DB에서 실습


def build_notebook(week, slug, title, cells, answers):
    work = '"mini_emr_practice.sqlite"' if week in PRACTICE_WEEKS else "DB_PATH"
    setup = SETUP_CODE.format(db_url=DB_URL, work_path=work)
    nb_cells = [md(SETUP_MD.format(week=week, title=title)), py(setup)]
    nb_cells += cells
    if answers:
        nb_cells.append(md("---\n## 정답 및 해설\n먼저 스스로 푼 다음에 열어 보세요."))
        for no, qq, sql in answers:
            head = f"**A{no}. {qq}**" if no else f"**{qq}**"
            nb_cells.append(md(f"{head}\n```sql\n{sql}\n```"))
    nb = {"cells": nb_cells,
          "metadata": {"colab": {"provenance": []},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 0}
    path = os.path.join(CODE, f"week{week:02d}_{slug}.ipynb")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    return path


def build_sql(week, slug, title, cells, answers):
    lines = [f"-- {'='*60}", f"-- {week}주차 — {title}",
             "-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)",
             f"-- {'='*60}", ""]
    for c in cells:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if 'q("""' in src:
            head = src.split("\n")[0].lstrip("# ")
            body = src.split('q("""')[1].split('""")')[0].strip()
            lines += [f"-- {head}", body if body.endswith(";") else body + ";", ""]
        elif 'run("""' in src:
            head = src.split("\n")[0].lstrip("# ")
            body = src.split('run("""')[1].split('""")')[0].strip()
            if "try:" in src:   # 의도적 에러 데모는 주석으로 수록
                body = "\n".join("-- " + l for l in body.split("\n"))
                head += " (일부러 에러를 내는 데모 — 주석을 풀면 실행이 중단됩니다)"
            lines += [f"-- {head}", body, ""]
    if answers:
        lines += ["-- " + "-" * 50, "-- 연습문제 정답", "-- " + "-" * 50, ""]
        for no, qq, sql in answers:
            lines += [f"-- A{no}. {qq}" if no else f"-- {qq}", sql, ""]
    path = os.path.join(SQLD, f"week{week:02d}.sql")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


if __name__ == "__main__":
    os.makedirs(SQLD, exist_ok=True)
    for week, slug, title, cells, answers in WEEKS:
        nb = build_notebook(week, slug, title, cells, answers)
        sq = build_sql(week, slug, title, cells, answers)
        print(f"  week{week:02d}: {os.path.basename(nb)}, sql/{os.path.basename(sq)}")
