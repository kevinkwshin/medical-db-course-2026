-- ============================================================
-- 3주차 — SELECT ① 조회의 기본기
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 환자 테이블 전체 (LIMIT으로 자르기)
SELECT * FROM patient LIMIT 5;

-- 특정 컬럼만
SELECT patient_id, birth_date FROM patient LIMIT 5;

-- 별칭(AS)
SELECT patient_id AS 환자번호, blood_type AS 혈액형 FROM patient LIMIT 5;

-- 우리 병원의 진료과 목록
SELECT DISTINCT department FROM visit ORDER BY 1;

-- 의료진 직종 목록
SELECT DISTINCT role FROM staff;

-- 나이 많은 순 (생년월일 오름차순)
SELECT patient_id, birth_date, sex FROM patient ORDER BY birth_date ASC LIMIT 10;

-- 가장 최근 내원 5건
SELECT visit_id, patient_id, visit_date, department
FROM visit ORDER BY visit_date DESC LIMIT 5;

-- [연습 Q1] 검사(lab) 테이블에는 어떤 검사 종류들이 있는가?
-- 여기에 SQL을 작성하세요;

-- [연습 Q2] 처방에서 약품명과 용량만, 약품명 가나다순으로
-- 여기에 SQL을 작성하세요;

-- [연습 Q3] 가장 어린 환자 3명의 ID와 생년월일은?
-- 여기에 SQL을 작성하세요;

-- [연습 Q4] 영상(imaging) 테이블의 촬영종류 목록은?
-- 여기에 SQL을 작성하세요;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. 검사 종류
SELECT DISTINCT test_name FROM lab ORDER BY 1;

-- A2. 약품명·용량 가나다순
SELECT drug_name, dose FROM prescription ORDER BY drug_name;

-- A3. 가장 어린 환자 3명
SELECT patient_id, birth_date FROM patient ORDER BY birth_date DESC LIMIT 3;

-- A4. 촬영종류 목록
SELECT DISTINCT modality FROM imaging;
