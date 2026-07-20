-- ============================================================
-- 11주차 — JOIN — 테이블 연결
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 내원 + 환자 정보
SELECT v.visit_id, v.visit_date, v.department, p.sex, p.birth_date
FROM visit v
JOIN patient p ON v.patient_id = p.patient_id
LIMIT 8;

-- 3테이블: 내원 + 환자 + 담당의
SELECT v.visit_id, v.visit_date, p.sex AS 환자성별, s.role, s.department AS 소속과
FROM visit v
JOIN patient p ON v.patient_id = p.patient_id
JOIN staff s ON v.attending_id = s.staff_id
WHERE v.visit_type = '입원' ORDER BY v.visit_date DESC LIMIT 8;

-- ① 같은 내원 안에서: 당뇨 진단이 붙은 그 내원의 HbA1c
SELECT d.kcd_code, l.test_name, l.result_value, l.collected_at
FROM diagnosis d
JOIN lab l ON l.visit_id = d.visit_id
WHERE d.kcd_code LIKE 'E11%' AND l.test_name = 'HbA1c'
ORDER BY l.collected_at;

-- ② 환자 단위로 확장: 당뇨(E11) 환자의 모든 HbA1c 결과
SELECT DISTINCT v.patient_id, l.result_value AS hba1c, l.collected_at
FROM diagnosis d
JOIN visit v  ON d.visit_id = v.visit_id
JOIN visit v2 ON v2.patient_id = v.patient_id
JOIN lab l    ON l.visit_id = v2.visit_id
WHERE d.kcd_code LIKE 'E11%' AND l.test_name = 'HbA1c'
ORDER BY v.patient_id, l.collected_at;

-- 당뇨 환자 전원 + HbA1c 검사 건수·최근 검사시각 (NULL = 미검사)
SELECT dm.patient_id,
       COUNT(l.lab_id) AS 검사건수,
       MAX(l.collected_at) AS 최근검사시각
FROM (SELECT DISTINCT v.patient_id
      FROM diagnosis d JOIN visit v ON d.visit_id = v.visit_id
      WHERE d.kcd_code LIKE 'E11%') dm
LEFT JOIN visit v2 ON v2.patient_id = dm.patient_id
LEFT JOIN lab l ON l.visit_id = v2.visit_id AND l.test_name = 'HbA1c'
GROUP BY dm.patient_id;

-- HbA1c를 한 번도 안 받은 당뇨 환자
SELECT DISTINCT v.patient_id
FROM diagnosis d JOIN visit v ON d.visit_id = v.visit_id
WHERE d.kcd_code LIKE 'E11%'
  AND v.patient_id NOT IN (
    SELECT v2.patient_id FROM lab l
    JOIN visit v2 ON l.visit_id = v2.visit_id
    WHERE l.test_name = 'HbA1c');

-- [연습 Q1] 각 진단(dx_name)에 해당 환자의 성별을 붙여 출력하라
-- 여기에 SQL을 작성하세요;

-- [연습 Q2] 뇌 MRI를 찍은 내원의 환자ID·촬영일·판독문을 출력하라
-- 여기에 SQL을 작성하세요;

-- [연습 Q3] 영상 검사를 한 번도 안 받은 환자는 몇 명인가?
-- 여기에 SQL을 작성하세요;

-- [연습 Q4] 폐렴(J18) 내원에서 나간 약물 목록을 만들라
-- 여기에 SQL을 작성하세요;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. 진단+성별
SELECT d.dx_name, p.sex FROM diagnosis d
JOIN visit v ON d.visit_id = v.visit_id
JOIN patient p ON v.patient_id = p.patient_id;

-- A2. 뇌 MRI
SELECT v.patient_id, i.taken_date, i.report FROM imaging i
JOIN visit v ON i.visit_id = v.visit_id
WHERE i.modality = 'MRI' AND i.body_part = '뇌';

-- A3. 영상 없는 환자 수
-- 하위 명단에 NULL이 없어 NOT IN이 안전 (NULL 위험은 12주차에서)
SELECT COUNT(*) FROM patient p
WHERE p.patient_id NOT IN (
  SELECT v.patient_id FROM imaging i JOIN visit v ON i.visit_id = v.visit_id);

-- A4. 폐렴 약물
SELECT DISTINCT rx.drug_name FROM diagnosis d
JOIN prescription rx ON rx.visit_id = d.visit_id
WHERE d.kcd_code LIKE 'J18%';
