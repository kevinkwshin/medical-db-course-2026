-- ============================================================
-- 14주차 — 함정·보안·비정형
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 혈당을 낮은 값부터 — 이 7.8은 저혈당인가?
SELECT lab_id, test_name, result_value, unit
FROM lab WHERE test_name = 'Glucose'
ORDER BY result_value LIMIT 5;

-- 단위 감사 쿼리 — 분석 전 사전 점검
SELECT test_name, unit, COUNT(*) AS 건수,
       MIN(result_value) AS 최소, MAX(result_value) AS 최대
FROM lab GROUP BY test_name, unit ORDER BY test_name;

-- 당뇨 환자 수 vs 그중 HbA1c 검사자 수
SELECT
  (SELECT COUNT(DISTINCT v.patient_id) FROM visit v
   JOIN diagnosis d ON d.visit_id = v.visit_id
   WHERE d.kcd_code LIKE 'E11%') AS 당뇨환자수,
  (SELECT COUNT(DISTINCT v.patient_id) FROM visit v
   JOIN lab l ON l.visit_id = v.visit_id
   WHERE l.test_name = 'HbA1c'
     AND v.patient_id IN (
       SELECT v2.patient_id FROM visit v2
       JOIN diagnosis d2 ON d2.visit_id = v2.visit_id
       WHERE d2.kcd_code LIKE 'E11%')) AS 당뇨환자중검사자수;

-- 판독문 LIKE 검색 — '경색'이 들어간 보고서
SELECT img_id, modality, body_part, report
FROM imaging WHERE report LIKE '%경색%';

-- [연습 Q1] mmol/L로 입력된 혈당을 mg/dL로 환산하면 얼마인가? (×18) — SELECT로 환산값을 계산해 보라
-- 여기에 SQL을 작성하세요;

-- [연습 Q2] 채혈시각(collected_at)의 시(hour) 분포를 구하라 — 오후 채혈이 섞여 있는가?
-- 여기에 SQL을 작성하세요;

-- [연습 Q3] 각 검사(test_name)의 결측(result_value IS NULL) 건수를 세어 보라
-- 여기에 SQL을 작성하세요;

-- [연습 Q4] 판독문에 '없음'이 포함된 영상 보고서를 찾아, LIKE 검색의 함정을 확인하라
-- 여기에 SQL을 작성하세요;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. 단위 환산
-- ×18은 포도당에만 유효한 환산 — 검사명 조건을 반드시 함께
SELECT lab_id, result_value AS mmol, ROUND(result_value * 18, 0) AS mgdl
FROM lab WHERE test_name = 'Glucose' AND unit = 'mmol/L';

-- A2. 채혈 시각 분포
SELECT strftime('%H', collected_at) AS 시, COUNT(*) FROM lab GROUP BY 시 ORDER BY 시;

-- A3. 검사별 결측
SELECT test_name, SUM(CASE WHEN result_value IS NULL THEN 1 ELSE 0 END) AS 결측 FROM lab GROUP BY test_name;

-- A4. 부정 표현
SELECT img_id, report FROM imaging WHERE report LIKE '%없음%';
