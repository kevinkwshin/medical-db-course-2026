-- ============================================================
-- 12주차 — 서브쿼리
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 평균보다 오래 입원한 환자
SELECT visit_id, patient_id,
       julianday(discharge_date) - julianday(visit_date) AS los
FROM visit
WHERE visit_type = '입원'
  AND julianday(discharge_date) - julianday(visit_date) >
      (SELECT AVG(julianday(discharge_date) - julianday(visit_date))
       FROM visit WHERE visit_type = '입원')
ORDER BY los DESC;

-- I63 진단 이력자의 인적 정보
SELECT patient_id, sex, birth_date FROM patient
WHERE patient_id IN (
  SELECT v.patient_id FROM visit v
  JOIN diagnosis d ON v.visit_id = d.visit_id
  WHERE d.kcd_code LIKE 'I63%');

-- 항생제를 한 번도 처방받지 않은 환자 수
SELECT COUNT(*) AS 무항생제환자수
FROM patient p
WHERE NOT EXISTS (
  SELECT 1 FROM visit v
  JOIN prescription rx ON rx.visit_id = v.visit_id
  WHERE v.patient_id = p.patient_id
    AND rx.drug_code IN ('CTX2','AMC625','LVX500'));

-- 항생제 노출군과 약물
SELECT DISTINCT v.patient_id, rx.drug_name
FROM visit v JOIN prescription rx ON rx.visit_id = v.visit_id
WHERE rx.drug_code IN ('CTX2','AMC625','LVX500')
ORDER BY v.patient_id;

-- [연습 Q1] 평균 투약일수보다 길게 처방된 약물 행은?
-- 여기에 SQL을 작성하세요;

-- [연습 Q2] 폐렴(J18) 진단 이력이 있는 환자의 성별·생년월일은?
-- 여기에 SQL을 작성하세요;

-- [연습 Q3] 검사(lab)를 한 번도 받지 않은 환자 수는?
-- 여기에 SQL을 작성하세요;

-- [연습 Q4] 자기 진료과 평균보다 재원이 길었던 입원 건은?
-- 여기에 SQL을 작성하세요;

-- [연습 Q5] Q3를 NOT IN으로도 써 보고, NULL이 끼면 어떻게 되는지 설명해 보라
-- 여기에 SQL을 작성하세요;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. 평균 초과 투약
SELECT * FROM prescription
WHERE duration_days > (SELECT AVG(duration_days) FROM prescription);

-- A2. 폐렴 이력자
SELECT patient_id, sex, birth_date FROM patient
WHERE patient_id IN (SELECT v.patient_id FROM visit v
  JOIN diagnosis d ON d.visit_id = v.visit_id WHERE d.kcd_code LIKE 'J18%');

-- A3. 검사 무이력
SELECT COUNT(*) FROM patient p WHERE NOT EXISTS (
  SELECT 1 FROM visit v JOIN lab l ON l.visit_id = v.visit_id
  WHERE v.patient_id = p.patient_id);

-- A4. 진료과 평균 초과 재원
-- 별칭(los)은 표준 SQL의 WHERE에서 쓸 수 없어 식을 반복한다
SELECT v.visit_id, v.department,
  julianday(v.discharge_date)-julianday(v.visit_date) AS los
FROM visit v WHERE v.visit_type='입원'
  AND julianday(v.discharge_date)-julianday(v.visit_date)
      > (SELECT AVG(julianday(v2.discharge_date)-julianday(v2.visit_date))
         FROM visit v2 WHERE v2.visit_type='입원' AND v2.department = v.department);
