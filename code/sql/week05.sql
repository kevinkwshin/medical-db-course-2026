-- ============================================================
-- 5주차 — SELECT ③ 계산·CASE·집계
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 입원별 재원일수(LOS)
SELECT visit_id, visit_date, discharge_date,
       julianday(discharge_date) - julianday(visit_date) AS los
FROM visit WHERE visit_type = '입원' ORDER BY los DESC LIMIT 8;

-- 나이 계산 — substr(연도 자르기) + CAST(숫자 변환), 연 나이 근사
SELECT patient_id, birth_date,
       2026 - CAST(substr(birth_date,1,4) AS INT) AS age
FROM patient ORDER BY age DESC LIMIT 5;

-- 혈압 측정치 3구간 (측정 1회의 구간 분류 — 진단 아님, 경계값은 예시)
SELECT visit_id, sbp, dbp,
  CASE WHEN sbp >= 140 OR dbp >= 90 THEN '고혈압 범위'
       WHEN sbp >= 120 THEN '주의 범위'
       ELSE '정상 범위' END AS bp_range
FROM vital ORDER BY sbp DESC LIMIT 10;

-- 입원 요약: 건수·평균·최장
SELECT COUNT(*) AS 입원건수,
       ROUND(AVG(julianday(discharge_date) - julianday(visit_date)), 1) AS 평균재원일,
       MAX(julianday(discharge_date) - julianday(visit_date)) AS 최장재원일
FROM visit WHERE visit_type = '입원';

-- 정상범위 벗어난 검사 비율 (CASE×SUM 패턴) — 분모는 결과값이 있는 검사만
SELECT COUNT(*) AS 전체검사,
  COUNT(result_value) AS 판정가능검사,
  SUM(CASE WHEN result_value > ref_high OR result_value < ref_low THEN 1 ELSE 0 END) AS 이상건수,
  ROUND(100.0 * SUM(CASE WHEN result_value > ref_high OR result_value < ref_low THEN 1 ELSE 0 END) / COUNT(result_value), 1) AS 이상비율
FROM lab;

-- COUNT(*) vs COUNT(컬럼) — NULL의 조용한 제외
SELECT COUNT(*) AS 전체행수, COUNT(result_value) AS 값있는행수,
       COUNT(*) - COUNT(result_value) AS 결측행수
FROM lab;

-- [연습 Q1] 처방의 평균 투약일수는?
-- 여기에 SQL을 작성하세요;

-- [연습 Q2] 맥박을 서맥(<60)·정상·빈맥(>100)으로 분류해 보라
-- 여기에 SQL을 작성하세요;

-- [연습 Q3] HbA1c 검사의 최솟값·최댓값·평균은?
-- 여기에 SQL을 작성하세요;

-- [연습 Q4] HbA1c가 7.0 이상인 검사 건수의 비율은?
-- 여기에 SQL을 작성하세요;

-- [연습 Q5] 입원 재원일수가 14일을 넘는 내원은 몇 건인가?
-- 여기에 SQL을 작성하세요;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. 평균 투약일수
SELECT ROUND(AVG(duration_days),1) FROM prescription;

-- A2. 맥박 분류
SELECT visit_id, pulse, CASE WHEN pulse < 60 THEN '서맥' WHEN pulse > 100 THEN '빈맥' ELSE '정상' END AS grade FROM vital;

-- A3. HbA1c 요약
SELECT MIN(result_value), MAX(result_value), ROUND(AVG(result_value),1) FROM lab WHERE test_name='HbA1c';

-- A4. HbA1c≥7.0 비율
SELECT ROUND(100.0*SUM(CASE WHEN result_value>=7.0 THEN 1 ELSE 0 END)/COUNT(*),1) FROM lab WHERE test_name='HbA1c';

-- A5. 14일 초과 입원
SELECT COUNT(*) FROM visit WHERE visit_type='입원' AND julianday(discharge_date)-julianday(visit_date) > 14;
