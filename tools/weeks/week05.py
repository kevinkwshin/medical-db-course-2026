# -*- coding: utf-8 -*-
"""5주차 — SELECT ③: 계산, CASE, 집계함수"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing)

WEEK = 5
TITLE = "SELECT ③ — 계산 · CASE · 집계"

slides = [
    cover(5, "SELECT ③<br>계산하고, 분류하고, 요약하기",
          ["산술식 — 재원일수 계산",
           "CASE — 혈압을 정상 · 주의 · 고혈압으로",
           "집계함수 — COUNT · AVG · MIN · MAX",
           "NULL이 집계를 어떻게 왜곡하는가"],
          question="우리 병원의 평균 재원일수는 며칠인가?"),

    qsql("입원 환자들은 며칠씩 입원했나? — 재원일수 계산",
         "SELECT visit_id, visit_date, discharge_date,\n       julianday(discharge_date)\n         - julianday(visit_date) AS los\nFROM visit\nWHERE visit_type = '입원'\nORDER BY los DESC;",
         max_rows=6,
         title="산술식 — 컬럼으로 계산하기",
         note="SELECT 안에서 사칙연산이 가능합니다. SQLite에서 날짜 간격은 "
              "<span class='mono'>julianday()</span> 차이로 구합니다(일 단위). "
              "LOS(Length of Stay, 재원일수)는 병원 운영·연구의 기본 지표."),

    qsql("검사 결과가 정상 상한을 몇 배나 초과했나?",
         "SELECT test_name, result_value, ref_high,\n       ROUND(result_value / ref_high, 2)\n         AS ratio\nFROM lab\nWHERE test_name = 'CRP'\nORDER BY ratio DESC;",
         max_rows=5,
         title="산술식 + ROUND — 비율 계산",
         note="CRP가 정상 상한(5)의 최대 30배가 넘는 환자들 — 폐렴 입원군입니다. "
              "ROUND(값, 자릿수)로 소수점 정리."),

    html_slide("CASE — SQL의 조건 분기",
        """<div class="cols" style="grid-template-columns:1.1fr 1fr">
        <div><pre class="sql" style="font-size:21px">CASE
  WHEN 조건1 THEN 결과1
  WHEN 조건2 THEN 결과2
  ELSE 나머지결과
END</pre></div>
        <div class="side"><h3>임상에서 늘 하는 일</h3>
        <ul><li>수치 → <b>범주</b>: 혈압 → 정상/주의/고혈압</li>
        <li>나이 → 연령대: 65세 기준 고령 여부</li>
        <li>검사값 → 정상/이상 플래그</li>
        <li>즉, <b>가이드라인의 분류표를 코드로</b> 옮기는 문법</li></ul></div></div>""",
        tag="문법"),

    qsql("활력징후의 혈압을 정상 · 주의 · 고혈압으로 분류하라",
         "SELECT visit_id, sbp, dbp,\n  CASE\n    WHEN sbp >= 140 OR dbp >= 90  THEN '고혈압'\n    WHEN sbp >= 120               THEN '주의'\n    ELSE '정상'\n  END AS bp_grade\nFROM vital\nORDER BY sbp DESC;",
         max_rows=6,
         title="CASE 실전 — 혈압 분류",
         tag="대표 질문",
         note="WHEN은 <b>위에서부터 차례로</b> 평가되고 먼저 맞은 조건에서 멈춥니다 — "
              "분류 기준의 순서가 곧 로직입니다. 분류 기준(140/90)을 바꾸면 "
              "연구 결과도 바뀝니다: 기준 명시가 왜 중요한지 보이는 대목."),

    qsql("우리 병원 전체 요약: 내원 건수, 평균 재원일수, 최장 입원",
         "SELECT COUNT(*) AS 입원건수,\n       ROUND(AVG(julianday(discharge_date)\n         - julianday(visit_date)), 1) AS 평균재원일,\n       MAX(julianday(discharge_date)\n         - julianday(visit_date)) AS 최장재원일\nFROM visit\nWHERE visit_type = '입원';",
         title="집계함수 — 여러 행을 하나의 숫자로",
         note="COUNT·SUM·AVG·MIN·MAX. 집계함수가 등장하면 결과는 <b>요약된 한 행</b>이 됩니다. "
              "최장 35일 입원(대퇴골 골절 환자)이 평균을 끌어올리고 있죠 — 평균만 보면 놓치는 것들."),

    qsql("검사 결과 중 정상범위를 벗어난 비율은 몇 %인가?",
         "SELECT COUNT(*) AS 전체검사,\n  COUNT(result_value) AS 판정가능,\n  SUM(CASE WHEN result_value > ref_high\n            OR result_value < ref_low\n           THEN 1 ELSE 0 END) AS 이상건수,\n  ROUND(100.0 * SUM(CASE WHEN result_value > ref_high\n            OR result_value < ref_low\n           THEN 1 ELSE 0 END)\n    / COUNT(result_value), 1) AS 이상비율\nFROM lab;",
         title="CASE × 집계 — 비율 구하기",
         tag="대표 질문",
         note="<b>CASE로 1/0 플래그를 만들고 SUM으로 세는</b> 패턴 — 유병률, 달성률, 이상률 계산의 기본 조합. "
              "분모는 COUNT(*)가 아니라 <b>판정 가능한 검사(COUNT(result_value))</b> — 결과값 NULL을 "
              "분모에 넣으면 결측이 '정상'처럼 계산됩니다. 100.0의 .0이 없으면 정수 나눗셈이 되어 0이 나옵니다."),

    qsql("COUNT(*) vs COUNT(컬럼) — NULL이 끼어들면?",
         "SELECT COUNT(*) AS 전체행수,\n       COUNT(result_value) AS 값있는행수,\n       COUNT(*) - COUNT(result_value)\n         AS 결측행수\nFROM lab;",
         title="NULL과 집계 — 조용한 왜곡",
         note="<span class='mono'>COUNT(*)</span>는 행 수, <span class='mono'>COUNT(컬럼)</span>은 "
              "<b>NULL을 제외한</b> 값의 수. AVG도 NULL을 빼고 평균합니다 — "
              "결측이 많은 검사의 '평균'은 <b>검사받은 사람들만의 평균</b>임을 항상 기억하세요."),

    qsql("체온과 산소포화도의 분포 감 잡기",
         "SELECT MIN(temp) AS 최저체온,\n       MAX(temp) AS 최고체온,\n       ROUND(AVG(temp), 1) AS 평균체온,\n       MIN(spo2) AS 최저SpO2\nFROM vital;",
         title="MIN/MAX — 데이터 범위 점검",
         note="새 데이터를 받으면 MIN/MAX부터: 체온 3.6℃, SpO2 250% 같은 <b>불가능한 값</b>이 "
              "여기서 걸립니다. 오늘 데이터는 깨끗하지만, 14주차에 지저분한 사례를 만납니다."),

    html_slide("연습문제",
        """<ul class="big">
        <li><b>Q1.</b> 처방의 평균 투약일수는?</li>
        <li><b>Q2.</b> 맥박을 서맥(&lt;60) · 정상 · 빈맥(&gt;100)으로 분류해 보라 <span class="desc">힌트: CASE</span></li>
        <li><b>Q3.</b> HbA1c 검사의 최솟값·최댓값·평균은? <span class="desc">WHERE test_name='HbA1c'</span></li>
        <li><b>Q4.</b> HbA1c가 7.0 이상인 검사 건수의 비율은? <span class="desc">힌트: CASE×SUM 패턴</span></li>
        <li><b>Q5.</b> 입원 재원일수가 14일을 넘는 내원은 몇 건인가?</li>
        </ul>""",
        tag="실습"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["산술식", "SELECT 안의 사칙연산 — 컬럼끼리 계산해 새 값을 만든다"],
         ["집계함수(aggregate)", "여러 행을 값 하나로 요약 — COUNT·SUM·AVG·MIN·MAX"],
         ["CASE 식", "SQL의 조건 분기 — WHEN을 위에서부터 평가, 먼저 맞으면 멈춤"],
         ["플래그(flag)", "CASE로 만든 1/0 표시값 — SUM하면 개수, 평균 내면 비율"],
         ["LOS (Length of Stay)", "재원일수 — 퇴원일과 내원일의 차이"],
         ["julianday()", "날짜를 일 단위 숫자로 바꾸는 SQLite 함수 — 날짜 간격 계산용"],
         ["결측(missing)", "값이 없는 상태 — AVG·COUNT(컬럼)는 NULL을 빼고 계산"]],
        small=True, tag="용어"),

    closing(5,
            ["SELECT 안에서 계산 가능 — 재원일수 = <span class='mono'>julianday()</span> 차이",
             "CASE = 가이드라인 분류표의 코드화. <b>WHEN의 순서가 로직</b>",
             "<b>CASE(1/0) × SUM ÷ COUNT</b> — 임상 비율 지표의 기본 패턴 (100.0 잊지 말기)",
             "AVG·COUNT는 NULL을 조용히 제외한다 — <b>'누구의 평균인가'를 항상 물을 것</b>"],
            homework="Colab 5주차 Q1~Q5",
            next_week="GROUP BY — 진료과별, 연령대별로 묶어 세기. Table 1의 원형"),
]
