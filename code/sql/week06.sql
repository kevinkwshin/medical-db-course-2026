-- ============================================================
-- 6주차 — SELECT ④ GROUP BY·HAVING
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 진료과별 내원 건수와 환자 수 — 둘의 차이에 주목!
SELECT department, COUNT(*) AS 내원건수,
       COUNT(DISTINCT patient_id) AS 환자수
FROM visit GROUP BY department ORDER BY 내원건수 DESC;

-- 내원유형별 평균 재원일수
SELECT visit_type, COUNT(*) AS 건수,
       ROUND(AVG(julianday(discharge_date) - julianday(visit_date)), 1) AS 평균재원일
FROM visit GROUP BY visit_type;

-- 월별 내원 추이 (2025년)
SELECT strftime('%Y-%m', visit_date) AS 월, COUNT(*) AS 내원건수
FROM visit WHERE visit_date >= '2025-01-01'
GROUP BY strftime('%Y-%m', visit_date) ORDER BY 월;

-- 10건 이상 처방된 약물
SELECT drug_name, COUNT(*) AS 처방건수
FROM prescription GROUP BY drug_name
HAVING COUNT(*) >= 10 ORDER BY 처방건수 DESC;

-- 성별 × 연령군 분포
SELECT sex,
  CASE WHEN 2026 - CAST(substr(birth_date,1,4) AS INT) >= 65
       THEN '65세 이상' ELSE '65세 미만' END AS 연령군,
  COUNT(*) AS 명수
FROM patient GROUP BY sex, 연령군 ORDER BY sex, 연령군;

-- [연습 Q1] KCD 코드별 진단 건수를 많은 순으로
-- 여기에 SQL을 작성하세요;

-- [연습 Q2] 검사 종류별 평균 결과값과 검사 건수는?
-- 여기에 SQL을 작성하세요;

-- [연습 Q3] 5회 이상 내원한 환자의 ID와 내원 횟수는?
-- 여기에 SQL을 작성하세요;

-- [연습 Q4] 혈액형별 환자 수 분포는?
-- 여기에 SQL을 작성하세요;

-- [연습 Q5] 연도별 입원 건수 추이는?
-- 여기에 SQL을 작성하세요;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. KCD별 진단 건수
SELECT kcd_code, dx_name, COUNT(*) AS n FROM diagnosis GROUP BY kcd_code, dx_name ORDER BY n DESC;

-- A2. 검사별 평균
-- COUNT(*)와 COUNT(result_value)를 함께 — 평균의 분모는 후자다
SELECT test_name, ROUND(AVG(result_value),2) AS 평균,
       COUNT(*) AS 전체건수, COUNT(result_value) AS 값있는건수
FROM lab GROUP BY test_name;

-- A3. 5회 이상 내원
SELECT patient_id, COUNT(*) AS n FROM visit GROUP BY patient_id HAVING COUNT(*) >= 5 ORDER BY n DESC;

-- A4. 혈액형 분포
SELECT blood_type, COUNT(*) FROM patient GROUP BY blood_type ORDER BY 2 DESC;

-- A5. 연도별 입원
SELECT strftime('%Y', visit_date) AS 연도, COUNT(*) FROM visit WHERE visit_type='입원' GROUP BY 연도 ORDER BY 연도;
