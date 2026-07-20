-- ============================================================
-- 4주차 — SELECT ② WHERE 조건
-- 의료진을 위한 데이터베이스 · 미니 EMR (mini_emr.sqlite)
-- ============================================================

-- 여성 환자
SELECT patient_id, sex, birth_date FROM patient WHERE sex = 'F' LIMIT 8;

-- 1950년 이전 출생
SELECT patient_id, birth_date FROM patient
WHERE birth_date < '1950-01-01' ORDER BY birth_date;

-- 65세 이상 여성 — 나이 조건을 출생연도 조건으로 (2026년 기준 65세 이상 = 1961년 이전 출생)
SELECT patient_id, sex, birth_date
FROM patient
WHERE sex = 'F'
  AND birth_date <= '1961-12-31'
ORDER BY birth_date;

-- 응급 또는 입원 (IN)
SELECT visit_id, visit_date, visit_type FROM visit
WHERE visit_type IN ('응급','입원') ORDER BY visit_date DESC LIMIT 8;

-- 2024년 내원 (BETWEEN)
SELECT visit_id, visit_date, department FROM visit
WHERE visit_date BETWEEN '2024-01-01' AND '2024-12-31';

-- 순환기계(I코드) 진단 전체
SELECT dx_id, kcd_code, dx_name FROM diagnosis
WHERE kcd_code LIKE 'I%' ORDER BY kcd_code LIMIT 10;

-- 당뇨(E11) 패밀리
SELECT DISTINCT kcd_code, dx_name FROM diagnosis WHERE kcd_code LIKE 'E11%';

-- 퇴원일이 없는 내원 (외래·응급 귀가)
SELECT visit_id, visit_type, visit_date, discharge_date
FROM visit WHERE discharge_date IS NULL LIMIT 8;

-- [연습 Q1] 남성이면서 O+ 혈액형인 환자는?
-- 여기에 SQL을 작성하세요;

-- [연습 Q2] 2023년 이후 신경과 내원을 최신순으로
-- 여기에 SQL을 작성하세요;

-- [연습 Q3] 호흡기계(J코드) 진단을 모두 찾아라
-- 여기에 SQL을 작성하세요;

-- [연습 Q4] 투약일수가 30~90일인 처방은?
-- 여기에 SQL을 작성하세요;

-- [연습 Q5] 정상 상한(ref_high)이 기록되지 않은 검사가 있는가?
-- 여기에 SQL을 작성하세요;

-- --------------------------------------------------
-- 연습문제 정답
-- --------------------------------------------------

-- A1. 남성 O+
SELECT * FROM patient WHERE sex = 'M' AND blood_type = 'O+';

-- A2. 2023년 이후 신경과
SELECT * FROM visit WHERE department = '신경과' AND visit_date >= '2023-01-01' ORDER BY visit_date DESC;

-- A3. J코드 진단
SELECT * FROM diagnosis WHERE kcd_code LIKE 'J%';

-- A4. 30~90일 처방
SELECT * FROM prescription WHERE duration_days BETWEEN 30 AND 90;

-- A5. ref_high 없는 검사
SELECT * FROM lab WHERE ref_high IS NULL;  -- 이 데이터셋에서는 0행이 정답
