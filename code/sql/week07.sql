-- ============================================================
-- 7주차 — DDL — 테이블 설계와 생성
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 코호트 테이블 생성
CREATE TABLE IF NOT EXISTS my_cohort (
  subject_id   TEXT PRIMARY KEY,
  patient_id   TEXT NOT NULL REFERENCES patient(patient_id),
  index_date   DATE NOT NULL,
  age_at_index INTEGER CHECK (age_at_index BETWEEN 0 AND 120),
  sex          TEXT NOT NULL CHECK (sex IN ('M','F')),
  dm_flag      INTEGER NOT NULL DEFAULT 0 CHECK (dm_flag IN (0,1))
);

-- 생성 확인
SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1;

-- CHECK 위반 실험: SpO2 250%는 입력 자체가 거부된다 (일부러 에러를 내는 데모 — 주석을 풀면 실행이 중단됩니다)
-- CREATE TABLE IF NOT EXISTS vital_demo (visit_id TEXT, spo2 INTEGER CHECK (spo2 BETWEEN 0 AND 100));
--     INSERT INTO vital_demo VALUES ('V0001', 250);

-- 컬럼 추가 후 테이블 정리 — 이 셀을 두 번 실행하면 duplicate column 에러 (이미 있는 컬럼은 재추가 불가 — reset_db() 후 재실행)
ALTER TABLE my_cohort ADD COLUMN htn_flag INTEGER DEFAULT 0;
DROP TABLE IF EXISTS vital_demo;

-- [연습 Q1] '수술(operation)' 테이블을 설계해 CREATE 하라 — 수술ID(PK), 내원ID(FK), 수술명(NOT NULL), 수술일, 집도의ID(FK)
-- 여기에 SQL을 작성하세요

-- [연습 Q2] operation에 마취종류 컬럼을 ALTER로 추가해 보라 — CHECK 제약까지 걸려면 왜 어려운지 겪어보기
-- 여기에 SQL을 작성하세요

-- [연습 Q3] 자기 연구 주제의 코호트 테이블을 컬럼 6개 이상으로 설계하라 (과제 제출용)
-- 여기에 SQL을 작성하세요

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. 수술 테이블
CREATE TABLE operation (
  op_id TEXT PRIMARY KEY,
  visit_id TEXT NOT NULL REFERENCES visit(visit_id),
  op_name TEXT NOT NULL,
  op_date DATE,
  surgeon_id TEXT REFERENCES staff(staff_id)
);

-- A2. 마취종류 추가
-- SQLite의 ALTER는 CHECK 추가를 지원하지 않음 → 테이블 재생성 필요.
-- 교훈: 제약조건은 처음 설계할 때 넣는 것이 훨씬 싸다.
ALTER TABLE operation ADD COLUMN anesthesia TEXT;
