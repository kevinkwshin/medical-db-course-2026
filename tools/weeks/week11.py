# -*- coding: utf-8 -*-
"""11주차 — JOIN: INNER/LEFT, 3+ 테이블, 결측 찾기"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, versus)

WEEK = 11
TITLE = "JOIN — 테이블 연결하기"

slides = [
    cover(11, "JOIN<br>여러 테이블을 연결해 조회하기",
          ["INNER JOIN — 짝이 있는 것만",
           "3개 이상 테이블 연결하기",
           "LEFT JOIN — 짝이 없어도 남긴다",
           "LEFT JOIN으로 '검사를 안 받은 환자' 찾기"],
          question="당뇨 환자들의 HbA1c 결과를 보려면?"),

    html_slide("왜 JOIN이 필요한가",
        """<div class="cols" style="grid-template-columns:1fr 1fr">
        <div><h3>10주차에 우리는</h3>
        <ul><li>중복을 없애려 테이블을 <b>분리</b>했다</li>
        <li>환자 정보는 patient에만, 진단은 diagnosis에만</li></ul>
        <h3 style="margin-top:16px">그 대가</h3>
        <ul><li>\"당뇨 환자의 검사 결과\" 같은 질문은 이제 <b>여러 테이블에 걸쳐</b> 있다</li></ul></div>
        <div class="side"><h3>JOIN이 하는 일</h3>
        <p style="font-size:20px">여러 테이블의 관련 행을 <b>공통 키</b>를 기준으로,
        <b>조회 시점에</b> 조합해 하나의 결과로 만든다.</p>
        <p style="font-size:19px; color:#64748b">저장은 나눠서(무결성), 조회는 붙여서(편의) —
        관계형 DB의 핵심 원리입니다.</p></div></div>""",
        tag="개념"),

    qsql("내원 기록에 환자의 성별·생년월일을 붙여줘",
         "SELECT v.visit_id, v.visit_date,\n       v.department,\n       p.sex, p.birth_date\nFROM visit v\nJOIN patient p\n  ON v.patient_id = p.patient_id\nLIMIT 6;",
         max_rows=6,
         title="INNER JOIN 기본형",
         note="<span class='mono'>ON</span>이 연결 조건(어떤 열쇠로 잇는가), "
              "<span class='mono'>v, p</span>는 테이블 별칭. "
              "같은 이름의 컬럼이 양쪽에 있으니 <b>어느 테이블의 컬럼인지 항상 명시</b>하는 습관을."),

    qsql("당뇨(E11) 환자들의 HbA1c 결과를 보려면? — 4개 테이블 연결",
         "SELECT DISTINCT v.patient_id,\n       l.result_value AS hba1c,\n       l.collected_at\nFROM diagnosis d\nJOIN visit v  ON d.visit_id = v.visit_id\nJOIN visit v2 ON v2.patient_id = v.patient_id\nJOIN lab l    ON l.visit_id = v2.visit_id\nWHERE d.kcd_code LIKE 'E11%'\n  AND l.test_name = 'HbA1c'\nORDER BY v.patient_id, l.collected_at;",
         max_rows=6,
         title="다중 JOIN — 대표 질문 풀기",
         tag="대표 질문",
         note="진단은 이번 내원에, 검사는 다른 내원에 있을 수 있어 visit을 두 번 통과했습니다"
              "(같은 환자의 모든 내원으로 확장). JOIN은 체인처럼 이어 붙이면 됩니다 — "
              "<b>ERD를 보며 열쇠의 경로를 따라가는 것</b>이 요령."),

    versus("INNER JOIN vs LEFT JOIN — 짝이 없는 행의 운명",
           "INNER JOIN", [
               "양쪽 모두에 짝이 있는 행만 생존",
               "\"진단도 있고 검사도 있는\" 환자만",
               "짝 없는 행은 <b>조용히 사라진다</b> — 눈치채지 못하면 위험"],
           "LEFT JOIN", [
               "왼쪽 테이블의 행은 <b>전부 생존</b>",
               "오른쪽에 짝이 없으면 그 자리는 NULL",
               "\"안 받은 사람\"이 NULL로 <b>보이게 된다</b>"],
           note="연구 관점 번역: INNER는 '둘 다 있는 사람 분석', LEFT는 '<b>없는 사람이 누구인지</b>까지 분석'. "
                "결측을 다루는 순간 LEFT JOIN이 기본값이 됩니다."),

    qsql("당뇨 환자 전원 명단에 HbA1c 검사 여부를 표시하라",
         "SELECT dm.patient_id,\n       l.result_value AS hba1c\nFROM (SELECT DISTINCT v.patient_id\n      FROM diagnosis d\n      JOIN visit v ON d.visit_id = v.visit_id\n      WHERE d.kcd_code LIKE 'E11%') dm\nLEFT JOIN visit v2 ON v2.patient_id = dm.patient_id\nLEFT JOIN lab l ON l.visit_id = v2.visit_id\n              AND l.test_name = 'HbA1c'\nGROUP BY dm.patient_id;",
         max_rows=9,
         title="LEFT JOIN 실전 — 전원 유지하며 붙이기",
         note="hba1c가 <b>∅(NULL)인 환자가 보입니다</b> — INNER JOIN이었다면 명단에서 통째로 사라졌을 "
              "사람들. \"검사를 안 받았다\"는 사실은 LEFT JOIN이어야만 화면에 나타납니다."),

    qsql("그래서, HbA1c 검사를 한 번도 안 받은 당뇨 환자는 누구인가?",
         "SELECT DISTINCT v.patient_id\nFROM diagnosis d\nJOIN visit v ON d.visit_id = v.visit_id\nWHERE d.kcd_code LIKE 'E11%'\n  AND v.patient_id NOT IN (\n    SELECT v2.patient_id\n    FROM lab l\n    JOIN visit v2 ON l.visit_id = v2.visit_id\n    WHERE l.test_name = 'HbA1c');",
         title="결측 환자 찾기 — 질 지표의 원형",
         tag="대표 질문",
         note="P007, P013 — 당뇨 진단은 있는데 당화혈색소 추적이 없는 환자입니다. "
              "이 쿼리가 <b>진료 질 지표(당뇨 환자 HbA1c 검사율)</b>와 "
              "<b>결측 파악</b>의 원형입니다. 다음 주에 NOT EXISTS로 다시 씁니다."),

    qsql("진료과별 담당의(staff) 정보까지 — 3테이블 기본 연습",
         "SELECT v.visit_id, v.visit_date,\n       p.sex AS 환자성별,\n       s.role, s.department AS 소속과\nFROM visit v\nJOIN patient p ON v.patient_id = p.patient_id\nJOIN staff s   ON v.attending_id = s.staff_id\nWHERE v.visit_type = '입원'\nORDER BY v.visit_date DESC;",
         max_rows=6,
         title="3테이블 JOIN — 환자 + 내원 + 의료진",
         note="연결 경로: visit→patient는 patient_id로, visit→staff는 attending_id로 — <b>한 번에 한 열쇠씩</b>. "
              "ON 조건을 빠뜨리면 모든 행의 조합(<b>카티전 곱</b>)이 생겨 결과가 폭발하니 주의."),

    html_slide("연습문제",
        """<ul class="big">
        <li><b>Q1.</b> 각 진단(dx_name)에 해당 환자의 성별을 붙여 출력하라 <span class="desc">diagnosis + visit + patient</span></li>
        <li><b>Q2.</b> 뇌 MRI를 찍은 내원의 환자ID·촬영일·판독문을 출력하라 <span class="desc">imaging + visit</span></li>
        <li><b>Q3.</b> 영상 검사를 한 번도 안 받은 환자는 몇 명인가? <span class="desc">힌트: LEFT JOIN … IS NULL 또는 NOT IN</span></li>
        <li><b>Q4.</b> 처방과 진단을 내원 기준으로 연결해 '폐렴(J18) 내원에서 나간 약물' 목록을 만들라</li>
        </ul>""",
        tag="실습"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["JOIN", "두 테이블을 공통 키로 이어 붙이는 연산"],
         ["ON 절", "어떤 컬럼끼리 연결할지 지정 — 빠지면 모든 조합(카티전 곱) 발생"],
         ["INNER JOIN", "양쪽 모두에 짝이 있는 행만 남김 (기본 JOIN)"],
         ["LEFT JOIN", "왼쪽 테이블은 전부 유지 — 짝 없는 자리는 NULL"],
         ["테이블 별칭", "FROM visit v 의 v — 긴 조인문을 짧고 명확하게"],
         ["카티전 곱(Cartesian product)", "조건 없는 결합 — 100행 × 100행 = 10,000행"],
         ["∅ (결과 표의 표시)", "이 슬라이드 결과 화면에서 NULL을 나타내는 기호"]],
        small=True, tag="용어"),

    closing(11,
            ["JOIN = 정규화로 나눈 테이블을 <b>열쇠(키)로 조회 시점에 재조립</b>",
             "다중 JOIN은 ERD 위의 <b>열쇠 경로 따라가기</b> — 한 번에 한 연결",
             "INNER는 짝 없는 행을 조용히 버린다 — <b>결측 연구엔 LEFT JOIN</b>",
             "\"검사 안 받은 당뇨 환자\" 쿼리 = 질 지표·결측 분석의 원형"],
            homework="Colab 11주차 Q1~Q4",
            next_week="서브쿼리 — 쿼리 속의 쿼리 (\"평균보다 오래 입원한 환자는?\", \"항생제를 한 번도 안 받은 환자는?\")"),
]
