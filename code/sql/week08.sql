-- ============================================================
-- 8주차 — DML — 입력·수정·삭제와 트랜잭션
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 가상 환자 P051 등록
INSERT INTO patient (patient_id, sex, birth_date, blood_type)
VALUES ('P051', 'F', '1988-03-15', 'A+');

-- 확인
SELECT * FROM patient WHERE patient_id = 'P051';

-- ① 먼저 SELECT로 대상 확인
SELECT lab_id, test_name, result_value FROM lab WHERE lab_id = 'L0044';

-- ② 그 다음 UPDATE
UPDATE lab SET result_value = 176 WHERE lab_id = 'L0044';

-- ③ 결과 재확인
SELECT lab_id, test_name, result_value FROM lab WHERE lab_id = 'L0044';

-- 감사로그 테이블과 정정 이력 남기기
CREATE TABLE IF NOT EXISTS lab_audit (
  audit_id INTEGER PRIMARY KEY,
  lab_id TEXT, old_value REAL, new_value REAL,
  changed_by TEXT, changed_at DATETIME, reason TEXT
);
INSERT INTO lab_audit (lab_id, old_value, new_value, changed_by, changed_at, reason)
VALUES ('L0044', 167, 176, 'S001', '2026-04-02 09:30', '재검 결과 반영');

-- 감사로그 확인
SELECT * FROM lab_audit;

-- [연습 Q1] P051의 외래 내원 한 건을 visit에 INSERT 하라 (visit_id는 'V0101' 등 새 값)
-- 여기에 SQL을 작성하세요;

-- [연습 Q2] P051의 혈액형을 B+로 정정하라 (SELECT → UPDATE → SELECT 3단계로)
-- 여기에 SQL을 작성하세요;

-- [연습 Q3] (사본이니 안심하고) WHERE 없는 UPDATE를 실행해 피해 규모를 확인한 뒤, 데이터를 다시 내려받아 복구하라
-- 여기에 SQL을 작성하세요;

-- [연습 Q4] lab_audit에 '단위 오입력 정정' 이력을 한 건 더 남겨 보라
-- 여기에 SQL을 작성하세요;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. P051 내원
INSERT INTO visit (visit_id, patient_id, visit_date, department, visit_type)
VALUES ('V0101', 'P051', '2026-04-01', '가정의학과', '외래');

-- A2. 혈액형 정정
SELECT * FROM patient WHERE patient_id='P051';
UPDATE patient SET blood_type='B+' WHERE patient_id='P051';
SELECT * FROM patient WHERE patient_id='P051';
