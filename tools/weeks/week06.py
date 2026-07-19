# -*- coding: utf-8 -*-
"""6주차 — SELECT ④: GROUP BY / HAVING"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, versus)

WEEK = 6
TITLE = "SELECT ④ — GROUP BY · HAVING"

slides = [
    cover(6, "SELECT ④<br>GROUP BY — 묶어서 요약하기",
          ["GROUP BY — 그룹별 집계의 원리",
           "진료과별 · 유형별 · 월별로 세기",
           "HAVING — 그룹에 거는 조건",
           "Table 1 맛보기 — 논문 첫 표의 정체"],
          question="진료과별 환자 수는 각각 몇 명인가?"),

    html_slide("GROUP BY의 원리 — 나눠 담고, 각각 요약",
        """<div class="cols" style="grid-template-columns:1fr 1fr">
        <div><h3>GROUP BY가 하는 일</h3>
        <p style="font-size:21px; line-height:1.9">
        ① 지정한 컬럼의 값이 같은 행끼리 <b>바구니에 나눠 담고</b><br>
        ② 바구니마다 집계함수를 <b>한 번씩</b> 적용<br>
        ③ 바구니 수만큼의 행을 반환</p></div>
        <div class="side"><h3>철칙 하나</h3>
        <p style="font-size:20px">SELECT에는 <b>① GROUP BY에 쓴 컬럼</b>과
        <b>② 집계함수</b>만 올 수 있습니다.</p>
        <p style="font-size:19px; color:#64748b">그룹당 한 행으로 접히는데, 그룹 안에서 값이 제각각인
        일반 컬럼은 '어느 값을 보여줄지' 정할 수 없기 때문.</p></div></div>""",
        tag="원리"),

    qsql("진료과별 내원 건수와 환자 수는?",
         "SELECT department,\n       COUNT(*) AS 내원건수,\n       COUNT(DISTINCT patient_id) AS 환자수\nFROM visit\nGROUP BY department\nORDER BY 내원건수 DESC;",
         title="GROUP BY 첫 실전",
         tag="대표 질문",
         note="<b>내원건수 ≠ 환자수</b>에 주목 — 만성질환 외래는 같은 환자가 반복 방문합니다. "
              "<span class='mono'>COUNT(DISTINCT patient_id)</span>가 '사람 수'입니다. "
              "행 단위(내원)와 사람 단위를 혼동하면 유병률이 뻥튀기됩니다."),

    qsql("내원 유형(외래/입원/응급)별로 평균 재원일수까지",
         "SELECT visit_type,\n       COUNT(*) AS 건수,\n       ROUND(AVG(julianday(discharge_date)\n         - julianday(visit_date)), 1)\n         AS 평균재원일\nFROM visit\nGROUP BY visit_type;",
         title="그룹별 다중 집계",
         note="외래·응급의 평균재원일은 NULL — discharge_date가 없으니 AVG가 계산할 대상이 없습니다. "
              "지난주의 'NULL은 조용히 빠진다'가 그룹별로도 그대로 적용."),

    qsql("월별 내원 추이 — 시간 축으로 묶기",
         "SELECT strftime('%Y-%m', visit_date) AS 월,\n       COUNT(*) AS 내원건수\nFROM visit\nWHERE visit_date >= '2025-01-01'\nGROUP BY strftime('%Y-%m', visit_date)\nORDER BY 월;",
         max_rows=7,
         title="날짜 함수 × GROUP BY",
         note="<span class='mono'>strftime('%Y-%m', …)</span>으로 '연-월'만 뽑아 묶으면 월별 통계. "
              "감염병 유행 곡선, 계절성 분석이 전부 이 문형입니다."),

    qsql("10건 이상 처방된 약물만 보여줘",
         "SELECT drug_name,\n       COUNT(*) AS 처방건수\nFROM prescription\nGROUP BY drug_name\nHAVING COUNT(*) >= 10\nORDER BY 처방건수 DESC;",
         title="HAVING — 그룹에 거는 조건",
         tag="대표 질문",
         note="WHERE는 <b>행</b>을 거르고(집계 전), HAVING은 <b>그룹</b>을 거릅니다(집계 후). "
              "'처방건수 10건 이상'은 집계가 끝나야 알 수 있으니 HAVING 자리입니다."),

    versus("WHERE vs HAVING — 언제 어느 쪽?",
           "WHERE (집계 전, 행 필터)", [
               "\"2024년 내원 중에서\" — 원본 행 조건",
               "집계함수를 <b>쓸 수 없다</b>",
               "먼저 실행되어 계산량을 줄인다"],
           "HAVING (집계 후, 그룹 필터)", [
               "\"환자 수가 5명 이상인 진료과만\" — 요약값 조건",
               "집계함수를 <b>쓰기 위한</b> 자리",
               "GROUP BY 다음에 실행된다"],
           note="실행 순서: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY. "
                "\"2024년(WHERE) 내원 기준으로, 내원이 10건 이상인(HAVING) 진료과\"처럼 둘을 함께 쓰는 게 보통입니다."),

    qsql("성별 × 연령대 분포 — Table 1의 첫 줄 만들기",
         "SELECT sex,\n  CASE WHEN 2026 - CAST(substr(birth_date,1,4) AS INT) >= 65\n       THEN '65세 이상' ELSE '65세 미만'\n  END AS 연령군,\n  COUNT(*) AS 명수\nFROM patient\nGROUP BY sex, 연령군\nORDER BY sex, 연령군;",
         title="다중 컬럼 GROUP BY — Table 1 맛보기",
         tag="Table 1",
         note="논문의 Table 1(연구대상자 특성표)은 결국 <b>CASE로 범주를 만들고 GROUP BY로 세는 것</b>의 반복입니다. "
              "13주차에 코호트 전용 Table 1을 완성합니다."),

    qsql("진료과별로 '고혈압(sbp≥140) 측정 비율'까지 — 종합 연습",
         "SELECT v.department,\n       COUNT(*) AS 측정수,\n       ROUND(100.0 * SUM(CASE WHEN t.sbp >= 140\n         THEN 1 ELSE 0 END) / COUNT(*), 1)\n         AS 고혈압비율\nFROM vital t, visit v\nWHERE t.visit_id = v.visit_id\nGROUP BY v.department\nORDER BY 고혈압비율 DESC;",
         title="지난 3주의 총결산 — 필터 × CASE × 집계 × 그룹",
         note="<span class='mono'>FROM vital t, visit v</span> + WHERE 연결은 <b>암시적 조인</b> — "
              "11주차에 배울 <span class='mono'>JOIN … ON</span>과 동작이 같습니다. "
              "WHERE·CASE·SUM·GROUP BY가 한 쿼리에 모두 들어간 형태로, 중간고사 최고 난도 수준입니다."),

    html_slide("연습문제",
        """<ul class="big">
        <li><b>Q1.</b> KCD 코드별 진단 건수를 많은 순으로</li>
        <li><b>Q2.</b> 검사 종류별 평균 결과값과 검사 건수는?</li>
        <li><b>Q3.</b> 5회 이상 내원한 환자의 ID와 내원 횟수는? <span class="desc">힌트: GROUP BY patient_id + HAVING</span></li>
        <li><b>Q4.</b> 혈액형별 환자 수 분포는?</li>
        <li><b>Q5.</b> 연도별 입원 건수 추이는? <span class="desc">힌트: strftime('%Y', …)</span></li>
        </ul>
        <div class="note"><b>중간고사 안내</b>: 9주차 시험 범위는 1~8주차 전체. SELECT 4부작(3~6주차)이 배점의 중심입니다.</div>""",
        tag="실습"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["GROUP BY", "지정 컬럼의 값이 같은 행끼리 묶어 그룹당 한 행으로 요약"],
         ["HAVING", "집계가 끝난 그룹에 거는 조건 (WHERE는 집계 전 행에)"],
         ["COUNT(DISTINCT x)", "중복을 빼고 센 개수 — '내원 수'가 아닌 '사람 수'를 셀 때"],
         ["strftime()", "날짜에서 원하는 부분을 추출하는 SQLite 함수 — '%Y-%m'이면 연-월"],
         ["실행 순서", "FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY"],
         ["암시적 조인", "FROM a, b + WHERE 연결 — JOIN…ON(11주차)과 같은 동작의 옛 문법"],
         ["Table 1", "연구대상자 기저 특성표 — CASE로 범주를 만들고 GROUP BY로 세면 완성"]],
        small=True, tag="용어"),

    closing(6,
            ["GROUP BY = 같은 값끼리 담아 <b>그룹당 한 행</b>으로 요약",
             "<b>내원 수 ≠ 환자 수</b> — '사람 수'는 COUNT(DISTINCT patient_id)로 센다",
             "WHERE는 행(집계 전), HAVING은 그룹(집계 후) — 실행 순서가 근거",
             "CASE로 범주 만들고 GROUP BY로 세면 그것이 <b>Table 1</b>"],
            homework="Colab 6주차 Q1~Q5",
            next_week="CREATE TABLE — 이번엔 우리가 테이블을 만든다: 연구 데이터셋 설계"),
]
