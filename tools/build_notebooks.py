# -*- coding: utf-8 -*-
"""주차별 Colab 노트북(.ipynb) + SQL 스크립트(.sql) 생성기
실행: python3 build_notebooks.py  →  ../code/weekNN_*.ipynb, ../code/sql/weekNN.sql
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(BASE, "..", "code")
SQLD = os.path.join(CODE, "sql")

# mini_emr.sqlite 배포 주소 (GitHub raw)
DB_URL = "https://raw.githubusercontent.com/kevinkwshin/medical-db-course-2026/main/mini_emr/mini_emr.sqlite"

SETUP_MD = """# {week}주차 — {title}
**의료진을 위한 데이터베이스** · 미니 EMR 실습 노트북

사용법: 위에서부터 순서대로 셀을 실행하세요 (`Shift+Enter`).
`q("SELECT ...")` 안의 SQL만 바꿔가며 실험하면 됩니다. 원본은 언제든 다시 내려받을 수 있으니 마음껏 실험하세요."""

SETUP_CODE = f"""# [준비] 미니 EMR 데이터베이스 내려받기 + 조회 도우미 정의 — 이 셀을 가장 먼저 실행!
import os, urllib.request, sqlite3
import pandas as pd

DB_URL = "{DB_URL}"   # 강의자 공지 주소
if not os.path.exists("mini_emr.sqlite"):
    try:
        urllib.request.urlretrieve(DB_URL, "mini_emr.sqlite")
        print("mini_emr.sqlite 다운로드 완료")
    except Exception as e:
        print("자동 다운로드 실패 — 왼쪽 파일 탭에서 mini_emr.sqlite를 직접 업로드하세요.", e)

con = sqlite3.connect("mini_emr.sqlite")

def q(sql):
    \"\"\"SQL을 실행하고 결과를 표로 반환\"\"\"
    return pd.read_sql_query(sql, con)

def run(sql):
    \"\"\"결과를 반환하지 않는 SQL(INSERT/UPDATE/CREATE 등) 실행\"\"\"
    con.executescript(sql); con.commit(); print("실행 완료")

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


def exercise(no, question, hint=None):
    h = f"\n# 힌트: {hint}" if hint else ""
    return py(f"# [연습 Q{no}] {question}{h}\nq(\"\"\"\n-- 여기에 SQL을 작성하세요\n\n\"\"\")")


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
    sql_cell("65세 이상 여성 (2026년 기준 연 나이)",
             "SELECT patient_id, sex, birth_date,\n       2026 - CAST(substr(birth_date,1,4) AS INT) AS age\nFROM patient\nWHERE sex = 'F'\n  AND 2026 - CAST(substr(birth_date,1,4) AS INT) >= 65"),
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
    (5, "ref_high 없는 검사", "SELECT * FROM lab WHERE ref_high IS NULL;  -- 이 데이터셋에는 0행 — '없다'도 답이다"),
]))

WEEKS.append((5, "calc_agg", "SELECT ③ 계산·CASE·집계", [
    md("## 1. 산술식 — 재원일수"),
    sql_cell("입원별 재원일수(LOS)",
             "SELECT visit_id, visit_date, discharge_date,\n       julianday(discharge_date) - julianday(visit_date) AS los\nFROM visit WHERE visit_type = '입원' ORDER BY los DESC LIMIT 8"),
    md("## 2. CASE — 혈압 분류"),
    sql_cell("정상/주의/고혈압",
             "SELECT visit_id, sbp, dbp,\n  CASE WHEN sbp >= 140 OR dbp >= 90 THEN '고혈압'\n       WHEN sbp >= 120 THEN '주의'\n       ELSE '정상' END AS bp_grade\nFROM vital ORDER BY sbp DESC LIMIT 10"),
    md("## 3. 집계함수"),
    sql_cell("입원 요약: 건수·평균·최장",
             "SELECT COUNT(*) AS 입원건수,\n       ROUND(AVG(julianday(discharge_date) - julianday(visit_date)), 1) AS 평균재원일,\n       MAX(julianday(discharge_date) - julianday(visit_date)) AS 최장재원일\nFROM visit WHERE visit_type = '입원'"),
    sql_cell("정상범위 벗어난 검사 비율 (CASE×SUM 패턴)",
             "SELECT COUNT(*) AS 전체검사,\n  SUM(CASE WHEN result_value > ref_high OR result_value < ref_low THEN 1 ELSE 0 END) AS 이상건수,\n  ROUND(100.0 * SUM(CASE WHEN result_value > ref_high OR result_value < ref_low THEN 1 ELSE 0 END) / COUNT(*), 1) AS 이상비율\nFROM lab"),
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
    (2, "검사별 평균", "SELECT test_name, ROUND(AVG(result_value),2) AS 평균, COUNT(*) AS 건수 FROM lab GROUP BY test_name;"),
    (3, "5회 이상 내원", "SELECT patient_id, COUNT(*) AS n FROM visit GROUP BY patient_id HAVING COUNT(*) >= 5 ORDER BY n DESC;"),
    (4, "혈액형 분포", "SELECT blood_type, COUNT(*) FROM patient GROUP BY blood_type ORDER BY 2 DESC;"),
    (5, "연도별 입원", "SELECT strftime('%Y', visit_date) AS 연도, COUNT(*) FROM visit WHERE visit_type='입원' GROUP BY 연도 ORDER BY 연도;"),
]))

WEEKS.append((7, "ddl", "DDL — 테이블 설계와 생성", [
    md("## 1. CREATE TABLE — 제약조건과 함께\n(이 노트북에서는 실습용 사본 위에서 자유롭게 만들었다 지워도 됩니다)"),
    run_cell("코호트 테이블 생성",
             "CREATE TABLE IF NOT EXISTS my_cohort (\n  subject_id   TEXT PRIMARY KEY,\n  patient_id   TEXT NOT NULL REFERENCES patient(patient_id),\n  index_date   DATE NOT NULL,\n  age_at_index INTEGER CHECK (age_at_index BETWEEN 0 AND 120),\n  sex          TEXT NOT NULL CHECK (sex IN ('M','F')),\n  dm_flag      INTEGER NOT NULL DEFAULT 0 CHECK (dm_flag IN (0,1))\n);"),
    sql_cell("생성 확인", "SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1"),
    md("## 2. 제약조건이 일하는 순간 — 아래 셀은 **일부러 에러**가 납니다"),
    py("# CHECK 위반 실험: SpO2 250%는 입력 자체가 거부된다\ntry:\n    run(\"\"\"\n    CREATE TABLE IF NOT EXISTS vital_demo (visit_id TEXT, spo2 INTEGER CHECK (spo2 BETWEEN 0 AND 100));\n    INSERT INTO vital_demo VALUES ('V0001', 250);\n    \"\"\")\nexcept Exception as e:\n    print('거부됨 →', e)"),
    md("## 3. ALTER / DROP"),
    run_cell("컬럼 추가 후 테이블 정리",
             "ALTER TABLE my_cohort ADD COLUMN htn_flag INTEGER DEFAULT 0;\nDROP TABLE IF EXISTS vital_demo;"),
    md("## 연습문제"),
    exercise(1, "'수술(operation)' 테이블을 설계해 CREATE 하라 — 수술ID(PK), 내원ID(FK), 수술명(NOT NULL), 수술일, 집도의ID(FK)", "run() 사용"),
    exercise(2, "operation에 마취종류 컬럼을 ALTER로 추가하고, CHECK로 ('전신','부위','국소')만 허용해 보라 — SQLite에서 기존 테이블에 CHECK 추가가 왜 어려운지 겪어보기"),
    exercise(3, "자기 연구 주제의 코호트 테이블을 컬럼 6개 이상으로 설계하라 (과제 제출용)"),
], [
    (1, "수술 테이블", "CREATE TABLE operation (\n  op_id TEXT PRIMARY KEY,\n  visit_id TEXT NOT NULL REFERENCES visit(visit_id),\n  op_name TEXT NOT NULL,\n  op_date DATE,\n  surgeon_id TEXT REFERENCES staff(staff_id)\n);"),
    (2, "마취종류 추가", "-- SQLite의 ALTER는 CHECK 추가를 지원하지 않음 → 테이블 재생성 필요.\n-- 교훈: 제약조건은 처음 설계할 때 넣는 것이 훨씬 싸다.\nALTER TABLE operation ADD COLUMN anesthesia TEXT;"),
]))

WEEKS.append((8, "dml", "DML — 입력·수정·삭제와 트랜잭션", [
    md("## 1. INSERT"),
    run_cell("가상 환자 P051 등록",
             "INSERT INTO patient (patient_id, sex, birth_date, blood_type)\nVALUES ('P051', 'F', '1988-03-15', 'A+');"),
    sql_cell("확인", "SELECT * FROM patient WHERE patient_id = 'P051'"),
    md("## 2. UPDATE — WHERE 확인 습관"),
    sql_cell("① 먼저 SELECT로 대상 확인", "SELECT lab_id, test_name, result_value FROM lab WHERE lab_id = 'L0044'"),
    run_cell("② 그 다음 UPDATE", "UPDATE lab SET result_value = 176 WHERE lab_id = 'L0044';"),
    sql_cell("③ 결과 재확인", "SELECT lab_id, test_name, result_value FROM lab WHERE lab_id = 'L0044'"),
    md("## 3. 트랜잭션 — 없던 일로 만들기"),
    py("# BEGIN → UPDATE → ROLLBACK 실습\ncur = con.cursor()\ncur.execute(\"BEGIN\")\ncur.execute(\"UPDATE lab SET result_value = 0\")   # 끔찍한 실수!\nprint('실수 직후:', cur.execute(\"SELECT COUNT(*) FROM lab WHERE result_value = 0\").fetchone())\ncon.rollback()                                      # 되돌리기\nprint('롤백 후  :', cur.execute(\"SELECT COUNT(*) FROM lab WHERE result_value = 0\").fetchone())"),
    md("## 4. soft delete + 감사로그 패턴"),
    run_cell("감사로그 테이블과 정정 이력 남기기",
             "CREATE TABLE IF NOT EXISTS lab_audit (\n  audit_id INTEGER PRIMARY KEY,\n  lab_id TEXT, old_value REAL, new_value REAL,\n  changed_by TEXT, changed_at DATETIME, reason TEXT\n);\nINSERT INTO lab_audit (lab_id, old_value, new_value, changed_by, changed_at, reason)\nVALUES ('L0044', 167, 176, 'S001', '2026-04-02 09:30', '재검 결과 반영');"),
    sql_cell("감사로그 확인", "SELECT * FROM lab_audit"),
    md("## 연습문제"),
    exercise(1, "P051의 외래 내원 한 건을 visit에 INSERT 하라 (visit_id는 'V0101' 등 새 값)"),
    exercise(2, "P051의 혈액형을 B+로 정정하라 (SELECT → UPDATE → SELECT 3단계로)"),
    exercise(3, "(사본이니 안심하고) WHERE 없는 UPDATE를 실행해 피해 규모를 확인한 뒤, 데이터를 다시 내려받아 복구하라"),
    exercise(4, "lab_audit에 '단위 오입력 정정' 이력을 한 건 더 남겨 보라"),
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
    md("## 2. 대표 질문 — 당뇨 환자들의 HbA1c"),
    sql_cell("당뇨(E11) 환자의 모든 HbA1c 결과",
             "SELECT DISTINCT v.patient_id, l.result_value AS hba1c, l.collected_at\nFROM diagnosis d\nJOIN visit v  ON d.visit_id = v.visit_id\nJOIN visit v2 ON v2.patient_id = v.patient_id\nJOIN lab l    ON l.visit_id = v2.visit_id\nWHERE d.kcd_code LIKE 'E11%' AND l.test_name = 'HbA1c'\nORDER BY v.patient_id, l.collected_at"),
    md("## 3. LEFT JOIN — 없는 사람이 보인다"),
    sql_cell("당뇨 환자 전원 + HbA1c 여부 (NULL = 미검사)",
             "SELECT dm.patient_id, l.result_value AS hba1c\nFROM (SELECT DISTINCT v.patient_id\n      FROM diagnosis d JOIN visit v ON d.visit_id = v.visit_id\n      WHERE d.kcd_code LIKE 'E11%') dm\nLEFT JOIN visit v2 ON v2.patient_id = dm.patient_id\nLEFT JOIN lab l ON l.visit_id = v2.visit_id AND l.test_name = 'HbA1c'\nGROUP BY dm.patient_id"),
    sql_cell("HbA1c를 한 번도 안 받은 당뇨 환자",
             "SELECT DISTINCT v.patient_id\nFROM diagnosis d JOIN visit v ON d.visit_id = v.visit_id\nWHERE d.kcd_code LIKE 'E11%'\n  AND v.patient_id NOT IN (\n    SELECT v2.patient_id FROM lab l\n    JOIN visit v2 ON l.visit_id = v2.visit_id\n    WHERE l.test_name = 'HbA1c')"),
    md("## 연습문제"),
    exercise(1, "각 진단(dx_name)에 해당 환자의 성별을 붙여 출력하라", "diagnosis→visit→patient"),
    exercise(2, "뇌 MRI를 찍은 내원의 환자ID·촬영일·판독문을 출력하라", "imaging + visit"),
    exercise(3, "영상 검사를 한 번도 안 받은 환자는 몇 명인가?", "LEFT JOIN … IS NULL 또는 NOT IN"),
    exercise(4, "폐렴(J18) 내원에서 나간 약물 목록을 만들라", "diagnosis + prescription, 내원 기준"),
], [
    (1, "진단+성별", "SELECT d.dx_name, p.sex FROM diagnosis d\nJOIN visit v ON d.visit_id = v.visit_id\nJOIN patient p ON v.patient_id = p.patient_id;"),
    (2, "뇌 MRI", "SELECT v.patient_id, i.taken_date, i.report FROM imaging i\nJOIN visit v ON i.visit_id = v.visit_id\nWHERE i.modality = 'MRI' AND i.body_part = '뇌';"),
    (3, "영상 없는 환자 수", "SELECT COUNT(*) FROM patient p\nWHERE p.patient_id NOT IN (\n  SELECT v.patient_id FROM imaging i JOIN visit v ON i.visit_id = v.visit_id);"),
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
    (4, "진료과 평균 초과 재원", "SELECT v.visit_id, v.department,\n  julianday(v.discharge_date)-julianday(v.visit_date) AS los\nFROM visit v WHERE v.visit_type='입원'\n  AND los > (SELECT AVG(julianday(v2.discharge_date)-julianday(v2.visit_date))\n             FROM visit v2 WHERE v2.visit_type='입원' AND v2.department = v.department);"),
]))

WEEKS.append((13, "cohort", "실전 — 코호트 추출과 Table 1", [
    md("## 연구 질문\n**\"2020년 1월 1일 이후 처음으로 뇌경색(I63)을 진단받은 환자\"** 코호트를 만들고 Table 1까지 완성한다."),
    md("## 1단계 — 후보군: I63 이력자 전체와 첫 진단일"),
    sql_cell("첫 진단일 (washout 적용 전 — 10명)",
             "SELECT v.patient_id, MIN(v.visit_date) AS first_dx_date\nFROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id\nWHERE d.kcd_code LIKE 'I63%'\nGROUP BY v.patient_id ORDER BY first_dx_date"),
    md("## 2단계 — washout: '첫' 진단이 2020년 이후인 신규 환자만"),
    sql_cell("index date 확정 (8명)",
             "SELECT v.patient_id, MIN(v.visit_date) AS index_date\nFROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id\nWHERE d.kcd_code LIKE 'I63%'\nGROUP BY v.patient_id\nHAVING MIN(v.visit_date) >= '2020-01-01'\nORDER BY index_date"),
    md("## 3단계 — WITH(CTE)로 특성 붙이기"),
    sql_cell("코호트 + 성별 + index 시점 나이",
             "WITH stroke_cohort AS (\n  SELECT v.patient_id, MIN(v.visit_date) AS index_date\n  FROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id\n  WHERE d.kcd_code LIKE 'I63%'\n  GROUP BY v.patient_id\n  HAVING MIN(v.visit_date) >= '2020-01-01')\nSELECT c.patient_id, c.index_date, p.sex,\n       CAST(substr(c.index_date,1,4) AS INT)\n         - CAST(substr(p.birth_date,1,4) AS INT) AS age_at_index\nFROM stroke_cohort c JOIN patient p ON p.patient_id = c.patient_id"),
    md("## 4단계 — 동반질환 플래그 (EXISTS)"),
    sql_cell("고혈압(I10) 동반 여부",
             "WITH stroke_cohort AS (\n  SELECT v.patient_id, MIN(v.visit_date) AS index_date\n  FROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id\n  WHERE d.kcd_code LIKE 'I63%'\n  GROUP BY v.patient_id\n  HAVING MIN(v.visit_date) >= '2020-01-01')\nSELECT c.patient_id, c.index_date,\n  CASE WHEN EXISTS (\n    SELECT 1 FROM visit v2 JOIN diagnosis d2 ON d2.visit_id = v2.visit_id\n    WHERE v2.patient_id = c.patient_id AND d2.kcd_code LIKE 'I10%')\n  THEN 1 ELSE 0 END AS htn_comorbid\nFROM stroke_cohort c"),
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
    sql_cell("단위 감사 쿼리 — 분석 전 30초 습관",
             "SELECT test_name, unit, COUNT(*) AS 건수,\n       MIN(result_value) AS 최소, MAX(result_value) AS 최대\nFROM lab GROUP BY test_name, unit ORDER BY test_name"),
    md("## 함정 ② 분모 — '검사받은 사람만'의 평균"),
    sql_cell("당뇨 환자 수 vs HbA1c 검사자 수",
             "SELECT\n  (SELECT COUNT(DISTINCT v.patient_id) FROM visit v\n   JOIN diagnosis d ON d.visit_id = v.visit_id\n   WHERE d.kcd_code LIKE 'E11%') AS 당뇨환자수,\n  (SELECT COUNT(DISTINCT v.patient_id) FROM visit v\n   JOIN lab l ON l.visit_id = v.visit_id\n   WHERE l.test_name = 'HbA1c') AS 검사받은환자수"),
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
    (1, "단위 환산", "SELECT lab_id, result_value AS mmol, ROUND(result_value * 18, 0) AS mgdl\nFROM lab WHERE unit = 'mmol/L';"),
    (2, "채혈 시각 분포", "SELECT strftime('%H', collected_at) AS 시, COUNT(*) FROM lab GROUP BY 시 ORDER BY 시;"),
    (3, "검사별 결측", "SELECT test_name, SUM(CASE WHEN result_value IS NULL THEN 1 ELSE 0 END) AS 결측 FROM lab GROUP BY test_name;"),
    (4, "부정 표현", "SELECT img_id, report FROM imaging WHERE report LIKE '%없음%';"),
]))


# ======================================================================
def build_notebook(week, slug, title, cells, answers):
    nb_cells = [md(SETUP_MD.format(week=week, title=title)), py(SETUP_CODE)]
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
