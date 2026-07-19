-- ============================================================
-- 13주차 — 실전 — 코호트 추출과 Table 1
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 첫 진단일 (washout 적용 전 — 10명)
SELECT v.patient_id, MIN(v.visit_date) AS first_dx_date
FROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id
WHERE d.kcd_code LIKE 'I63%'
GROUP BY v.patient_id ORDER BY first_dx_date;

-- index date 확정 (8명)
SELECT v.patient_id, MIN(v.visit_date) AS index_date
FROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id
WHERE d.kcd_code LIKE 'I63%'
GROUP BY v.patient_id
HAVING MIN(v.visit_date) >= '2020-01-01'
ORDER BY index_date;

-- 코호트 + 성별 + index 시점 나이
WITH stroke_cohort AS (
  SELECT v.patient_id, MIN(v.visit_date) AS index_date
  FROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id
  WHERE d.kcd_code LIKE 'I63%'
  GROUP BY v.patient_id
  HAVING MIN(v.visit_date) >= '2020-01-01')
SELECT c.patient_id, c.index_date, p.sex,
       CAST(substr(c.index_date,1,4) AS INT)
         - CAST(substr(p.birth_date,1,4) AS INT) AS age_at_index
FROM stroke_cohort c JOIN patient p ON p.patient_id = c.patient_id;

-- 고혈압(I10) 동반 여부
WITH stroke_cohort AS (
  SELECT v.patient_id, MIN(v.visit_date) AS index_date
  FROM visit v JOIN diagnosis d ON v.visit_id = d.visit_id
  WHERE d.kcd_code LIKE 'I63%'
  GROUP BY v.patient_id
  HAVING MIN(v.visit_date) >= '2020-01-01')
SELECT c.patient_id, c.index_date,
  CASE WHEN EXISTS (
    SELECT 1 FROM visit v2 JOIN diagnosis d2 ON d2.visit_id = v2.visit_id
    WHERE v2.patient_id = c.patient_id AND d2.kcd_code LIKE 'I10%')
  THEN 1 ELSE 0 END AS htn_comorbid
FROM stroke_cohort c;

-- 성별·평균나이 요약
WITH stroke_cohort AS (
  SELECT v.patient_id, MIN(v.visit_date) AS index_date
  FROM visit v JOIN diagnosis d ON d.visit_id = v.visit_id
  WHERE d.kcd_code LIKE 'I63%'
  GROUP BY v.patient_id
  HAVING MIN(v.visit_date) >= '2020-01-01')
SELECT p.sex AS 성별, COUNT(*) AS 명수,
  ROUND(AVG(CAST(substr(c.index_date,1,4) AS INT)
    - CAST(substr(p.birth_date,1,4) AS INT)), 1) AS 평균나이
FROM stroke_cohort c JOIN patient p ON p.patient_id = c.patient_id
GROUP BY p.sex;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- 프로젝트 체크리스트
-- ① 포함 기준(코드·기간)과 제외 기준을 정의서에 먼저 글로 쓴다
-- ② 단계마다 대상자 수를 주석으로 남긴다 (attrition)
-- ③ Table 1 변수는 성별·연령 + 조별 선택 2개 이상
