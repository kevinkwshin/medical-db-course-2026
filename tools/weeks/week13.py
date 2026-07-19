# -*- coding: utf-8 -*-
"""13주차 — 임상연구 코호트 추출 실전"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, code)

WEEK = 13
TITLE = "실전 — 코호트 추출과 Table 1"

slides = [
    cover(13, "임상연구 코호트 추출 실전<br>연구 질문에서 Table 1까지",
          ["연구 질문 → 포함·제외 기준 → 쿼리",
           "Index date와 washout — '첫 진단'의 정의",
           "단계별 코호트 조립 (WITH 구문)",
           "Table 1 자동 생성"],
          question="2020년 이후 '첫' 뇌졸중 진단 환자를 뽑아보자"),

    html_slide("연구 질문을 데이터 언어로 번역하기",
        """<table class="info">
        <thead><tr><th style="width:24%">연구 용어</th><th style="width:42%">뜻</th><th>SQL 대응물</th></tr></thead>
        <tbody>
        <tr><td><b>포함 기준</b></td><td>어떤 환자를 코호트에 넣나</td><td>WHERE + JOIN (진단코드, 기간)</td></tr>
        <tr><td><b>제외 기준</b></td><td>누구를 빼나</td><td>NOT EXISTS / NOT IN</td></tr>
        <tr><td><b>Index date</b></td><td>각 환자의 '시계 0시' — 추적 시작일</td><td>MIN(visit_date) 등으로 정의</td></tr>
        <tr><td><b>Washout</b></td><td>과거 일정 기간 질환 이력이 없어야 '신규'로 인정</td><td>HAVING MIN(…) ≥ 기준일</td></tr>
        <tr><td><b>Table 1</b></td><td>코호트의 기저 특성 요약표</td><td>CASE × GROUP BY (6주차)</td></tr>
        </tbody></table>
        <div class="note">오늘의 연구 질문: <b>\"2020년 1월 1일 이후 처음으로 뇌경색(I63)을 진단받은 성인 환자\"</b>의
        코호트를 만들고 기저 특성을 요약한다.</div>""",
        tag="설계"),

    qsql("1단계 — I63 진단 이력이 있는 환자와 첫 진단일",
         "SELECT v.patient_id,\n       MIN(v.visit_date) AS first_dx_date\nFROM visit v\nJOIN diagnosis d\n  ON v.visit_id = d.visit_id\nWHERE d.kcd_code LIKE 'I63%'\nGROUP BY v.patient_id\nORDER BY first_dx_date;",
         max_rows=10,
         title="후보군 전체 훑기",
         note="10명이 잡힙니다. 그런데 P029·P030의 첫 진단은 <b>2019년</b> — "
              "이들은 2020년 이후 기준으로는 '신규 발생'이 아니라 '기존 환자'입니다. "
              "여기서 washout이 등장합니다."),

    qsql("2단계 — washout 적용: '첫' 진단이 2020년 이후인 환자만",
         "SELECT v.patient_id,\n       MIN(v.visit_date) AS index_date\nFROM visit v\nJOIN diagnosis d\n  ON v.visit_id = d.visit_id\nWHERE d.kcd_code LIKE 'I63%'\nGROUP BY v.patient_id\nHAVING MIN(v.visit_date) >= '2020-01-01'\nORDER BY index_date;",
         max_rows=8,
         title="Index date 확정",
         tag="대표 질문",
         note="<b>HAVING MIN(visit_date) ≥ '2020-01-01'</b> — '가장 이른 진단'이 기준일 이후여야 신규. "
              "P029·P030이 제외되어 8명이 남았습니다. 각 환자의 첫 진단일이 곧 <b>index date</b>가 됩니다."),

    code("3단계 — WITH로 단계를 이름 붙여 조립하기",
         """WITH stroke_cohort AS (          -- ① 신규 I63 코호트
  SELECT v.patient_id,
         MIN(v.visit_date) AS index_date
  FROM visit v
  JOIN diagnosis d ON v.visit_id = d.visit_id
  WHERE d.kcd_code LIKE 'I63%'
  GROUP BY v.patient_id
  HAVING MIN(v.visit_date) >= '2020-01-01'
)
SELECT c.patient_id, c.index_date,       -- ② 특성 붙이기
       p.sex,
       CAST(substr(c.index_date,1,4) AS INT)
         - CAST(substr(p.birth_date,1,4) AS INT)
         AS age_at_index
FROM stroke_cohort c
JOIN patient p ON p.patient_id = c.patient_id;""",
         note="<b>WITH(공통 테이블 표현식, CTE)</b>: 서브쿼리에 이름을 붙여 단계를 쌓는 문법. "
              "정의서의 순서(포함→제외→특성)가 코드 구조에 그대로 보입니다 — 논문 Methods와 코드가 1:1 대응.",
         tag="CTE"),

    qsql("4단계 — 기저 변수 추가: 고혈압(I10) 동반 여부 플래그",
         "WITH stroke_cohort AS (\n  SELECT v.patient_id,\n         MIN(v.visit_date) AS index_date\n  FROM visit v\n  JOIN diagnosis d ON v.visit_id = d.visit_id\n  WHERE d.kcd_code LIKE 'I63%'\n  GROUP BY v.patient_id\n  HAVING MIN(v.visit_date) >= '2020-01-01')\nSELECT c.patient_id, c.index_date,\n  CASE WHEN EXISTS (\n    SELECT 1 FROM visit v2\n    JOIN diagnosis d2\n      ON d2.visit_id = v2.visit_id\n    WHERE v2.patient_id = c.patient_id\n      AND d2.kcd_code LIKE 'I10%')\n  THEN 1 ELSE 0 END AS htn_comorbid\nFROM stroke_cohort c;",
         max_rows=8,
         title="동반질환 플래그 — EXISTS의 재등장",
         note="EXISTS가 동반질환 플래그 제조기로 재등장 — 같은 패턴으로 어떤 기저 변수든 만들 수 있고, "
              "<span class='mono'>WHERE NOT EXISTS(…)</span>로 바꾸면 제외 기준이 됩니다."),

    qsql("5단계 — Table 1: 코호트 기저 특성 요약",
         "WITH stroke_cohort AS (\n  SELECT v.patient_id,\n         MIN(v.visit_date) AS index_date\n  FROM visit v\n  JOIN diagnosis d ON d.visit_id = v.visit_id\n  WHERE d.kcd_code LIKE 'I63%'\n  GROUP BY v.patient_id\n  HAVING MIN(v.visit_date) >= '2020-01-01')\nSELECT p.sex AS 성별,\n  COUNT(*) AS 명수,\n  ROUND(AVG(CAST(substr(c.index_date,1,4) AS INT)\n    - CAST(substr(p.birth_date,1,4) AS INT)), 1)\n    AS 평균나이\nFROM stroke_cohort c\nJOIN patient p ON p.patient_id = c.patient_id\nGROUP BY p.sex;",
         title="Table 1 생성",
         tag="Table 1",
         note="논문 Table 1의 뼈대가 완성됐습니다. 나머지 변수(동반질환율, 약물 노출률)도 "
              "같은 GROUP BY에 CASE 플래그를 추가하면 됩니다 — 6·12주차 기술의 총합."),

    code("보너스 — 자주 쓰는 코호트는 VIEW로 저장",
         """CREATE VIEW v_stroke_cohort AS
SELECT v.patient_id,
       MIN(v.visit_date) AS index_date
FROM visit v
JOIN diagnosis d ON d.visit_id = v.visit_id
WHERE d.kcd_code LIKE 'I63%'
GROUP BY v.patient_id
HAVING MIN(v.visit_date) >= '2020-01-01';

-- 이후로는 테이블처럼:
SELECT * FROM v_stroke_cohort;""",
         note="VIEW는 <b>저장된 쿼리</b>(가상 테이블)입니다. 정의를 한 곳에 두면 공동연구자 모두가 "
              "같은 코호트 정의를 쓰게 됩니다 — '나만의 엑셀 사본' 문제(1주차)의 정반대.",
         tag="VIEW"),

    html_slide("조별 프로젝트 안내 — 코호트 정의서 · 추출 쿼리 · Table 1",
        """<div class="cols" style="grid-template-columns:1fr 1fr">
        <div><h3>제출물 (15주차 발표)</h3>
        <ul><li><b>① 코호트 정의서</b> 1쪽 — 연구 질문, 포함·제외 기준, index date 정의</li>
        <li><b>② 추출 쿼리</b> — WITH 단계 구조, 단계별 대상자 수 주석</li>
        <li><b>③ Table 1</b> — 성별·연령 + 조별 선택 변수 2개 이상</li></ul></div>
        <div class="side"><h3>평가 기준</h3>
        <ul><li>포함·제외 기준의 <b>임상적 타당성 (40%)</b></li>
        <li>기준 → 쿼리의 <b>정확한 번역 (30%)</b></li>
        <li>Table 1 해석과 한계 논의 (20%)</li>
        <li>발표 명료성 (10%)</li></ul>
        <p style="font-size:17px;color:#64748b"><b>attrition</b>(단계별 대상자 수 감소 흐름):
        포함 → washout → 제외 각 단계의 n을 쿼리 주석으로 남기면 심사와 재현이 쉬워집니다.</p></div></div>""",
        tag="프로젝트"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["포함 / 제외 기준", "코호트에 넣을 조건 / 뺄 조건 — 정의서에 글로 먼저 쓴다"],
         ["index date", "환자별 추적 시작일(시계의 0시) — 나이·노출 계산의 기준 시점"],
         ["washout", "과거 일정 기간 이력이 없어야 '신규 발생'으로 인정하는 규칙"],
         ["CTE (WITH 구문)", "서브쿼리에 이름을 붙여 단계로 쌓는 문법 — Common Table Expression"],
         ["VIEW", "저장된 쿼리 — 테이블처럼 조회되는 가상 테이블, 정의 공유용"],
         ["attrition", "단계별 대상자 수 감소 흐름 — 각 단계의 n을 기록"],
         ["Table 1", "코호트의 기저 특성 요약표 — CASE 플래그 × GROUP BY로 생성"]],
        small=True, tag="용어"),

    closing(13,
            ["코호트 추출 = <b>포함(JOIN·WHERE) → washout(HAVING MIN) → 제외(NOT EXISTS) → 특성(CASE·EXISTS)</b>",
             "Index date가 모든 시간 계산의 원점 — '언제 기준의 나이·노출인가'를 항상 명시",
             "<b>WITH(CTE)</b>로 정의서의 단계를 코드 구조로 — Methods와 1:1 대응",
             "공유할 정의는 <b>VIEW</b>로 — 연구진 전원이 같은 코호트를 본다"],
            homework="조별 프로젝트 착수 — 다음 주까지 연구 질문·포함 기준 초안",
            next_week="이 결과를 믿어도 되나 — 의료데이터의 함정, 가명처리와 IRB, RDB 밖의 데이터"),
]
