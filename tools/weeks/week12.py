# -*- coding: utf-8 -*-
"""12주차 — 서브쿼리: 스칼라/IN/EXISTS/NOT EXISTS"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, versus)

WEEK = 12
TITLE = "서브쿼리 — 쿼리 속의 쿼리"

slides = [
    cover(12, "서브쿼리<br>두 단계 질문을 한 문장으로",
          ["스칼라 서브쿼리 — \"평균보다 오래 입원한\"",
           "IN 서브쿼리 — 명단으로 거르기",
           "EXISTS / NOT EXISTS — \"~한 적이 있는가/없는가\"",
           "NOT IN의 NULL 함정"],
          question="항생제를 한 번도 처방받지 않은 환자는?"),

    html_slide("서브쿼리 — 두 단계 질문을 한 문장으로",
        """<div class="cols" style="grid-template-columns:1fr 1fr">
        <div><h3>임상 질문의 실제 구조</h3>
        <p style="font-size:21px; line-height:1.85">
        "평균보다 오래 입원한 환자는?"<br>
        = ① <b>먼저</b> 평균 재원일수를 구하고<br>
        &nbsp;&nbsp;&nbsp;② 그 값보다 큰 행을 찾아라</p></div>
        <div class="side"><h3>SQL의 대응</h3>
        <p style="font-size:20px">괄호 안의 쿼리(①)가 <b>논리적으로 먼저 평가</b>되어 값·명단이 되고,
        바깥 쿼리(②)가 그 결과를 조건으로 사용합니다. (실제 실행 순서는 DBMS가 최적화)</p>
        <p style="font-size:19px;color:#64748b">서브쿼리가 놓이는 자리: WHERE(오늘의 중심),
        FROM(지난주 이미 사용), SELECT</p></div></div>""",
        tag="개념"),

    qsql("평균 재원일수보다 오래 입원한 환자는?",
         "SELECT visit_id, patient_id,\n       julianday(discharge_date)\n         - julianday(visit_date) AS los\nFROM visit\nWHERE visit_type = '입원'\n  AND julianday(discharge_date)\n        - julianday(visit_date) >\n      (SELECT AVG(julianday(discharge_date)\n                - julianday(visit_date))\n       FROM visit\n       WHERE visit_type = '입원')\nORDER BY los DESC;",
         max_rows=6,
         title="스칼라 서브쿼리 — 값 하나를 조건에 꽂기",
         tag="대표 질문",
         note="괄호 안이 논리적으로 먼저 평가되어 평균(11.7일)이 되고 → 바깥 쿼리가 그보다 긴 입원만 필터. "
              "35일 입원한 P039(대퇴골 골절)가 선두입니다. <b>기준값을 데이터가 스스로 정하므로</b> "
              "평균이 바뀌어도 쿼리를 수정할 필요가 없습니다."),

    qsql("뇌경색(I63) 진단을 받은 적 있는 환자의 인적 정보",
         "SELECT patient_id, sex, birth_date\nFROM patient\nWHERE patient_id IN (\n    SELECT v.patient_id\n    FROM visit v\n    JOIN diagnosis d\n      ON v.visit_id = d.visit_id\n    WHERE d.kcd_code LIKE 'I63%');",
         max_rows=6,
         title="IN 서브쿼리 — 명단을 만들어 거르기",
         note="안쪽 쿼리가 'I63 진단 이력자 명단'을 만들고, 바깥 쿼리가 그 명단에 든 환자만 통과. "
              "<b>\"~한 적이 있는 환자군\"</b>은 코호트 정의의 기본 문형입니다(다음 주 주인공)."),

    qsql("항생제를 한 번도 처방받지 않은 환자는 몇 명인가?",
         "SELECT COUNT(*) AS 무항생제환자수\nFROM patient p\nWHERE NOT EXISTS (\n    SELECT 1\n    FROM visit v\n    JOIN prescription rx\n      ON rx.visit_id = v.visit_id\n    WHERE v.patient_id = p.patient_id\n      AND rx.drug_code IN\n          ('CTX2','AMC625','LVX500'));",
         title="NOT EXISTS — \"~한 적이 전혀 없다\"",
         tag="대표 질문",
         note="EXISTS는 '한 건이라도 있는가', NOT EXISTS는 '한 건도 없는가'를 묻습니다. "
              "안쪽의 <span class='mono'>v.patient_id = p.patient_id</span>처럼 바깥 행과 연결된 형태를 "
              "<b>상관 서브쿼리</b>라 부릅니다 — 환자 한 명 한 명에 대해 질문을 반복하는 그림."),

    qsql("반대로: 항생제 노출 이력이 있는 환자와 그 약물",
         "SELECT DISTINCT v.patient_id,\n       rx.drug_name\nFROM visit v\nJOIN prescription rx\n  ON rx.visit_id = v.visit_id\nWHERE rx.drug_code IN\n      ('CTX2','AMC625','LVX500')\nORDER BY v.patient_id;",
         max_rows=6,
         title="EXISTS의 짝 — 노출군 정의",
         note="약물 노출군 vs 비노출군 — 약물역학 연구의 두 팔이 "
              "EXISTS / NOT EXISTS 한 쌍으로 정의됩니다."),

    html_slide("NOT IN의 함정 — NULL이 끼면 전부 사라진다",
        """<div class="cols" style="grid-template-columns:1.05fr 1fr">
        <div><pre class="sql" style="font-size:18.5px">-- 위험한 형태
SELECT * FROM patient
WHERE patient_id NOT IN
  (SELECT patient_id FROM some_list);
-- some_list의 patient_id에 NULL이
-- 하나라도 있으면 → 결과 0행!</pre></div>
        <div class="side"><h3>왜?</h3>
        <ul><li><span class="mono">x NOT IN (a, b, NULL)</span>은 <span class="mono">x≠a AND x≠b AND x≠NULL</span></li>
        <li>NULL과의 비교는 참도 거짓도 아닌 <b>'모름'</b> → 전체가 '모름' → 아무도 통과 못 함</li>
        <li>에러도 없이 <b>조용히 0행</b> — 최악의 실패 유형</li></ul>
        <h3 style="margin-top:12px">처방</h3>
        <ul><li>결측 가능성이 있으면 <b>NOT EXISTS를 기본기로</b></li></ul></div></div>""",
        tag="함정"),

    versus("서브쿼리 vs JOIN — 언제 무엇을",
           "서브쿼리가 자연스러운 질문", [
               "\"평균/최댓값 <b>기준</b>으로\" — 스칼라",
               "\"~인 적 있는/없는 <b>사람</b>\" — EXISTS류",
               "결과에 상대 테이블 컬럼이 <b>필요 없을 때</b>"],
           "JOIN이 자연스러운 질문", [
               "양쪽 테이블의 컬럼을 <b>나란히 출력</b>해야 할 때",
               "\"진단명과 검사값을 한 줄에\"",
               "여러 테이블의 속성을 조합한 계산"],
           note="둘은 상당 부분 서로 변환 가능하며, DBMS가 내부적으로 같은 실행계획으로 바꾸기도 합니다 — "
                "SQLite에서는 <span class='mono'>EXPLAIN QUERY PLAN</span>을 쿼리 앞에 붙이면 실행 방식을 확인할 수 있습니다."),

    html_slide("연습문제",
        """<ul class="big">
        <li><b>Q1.</b> 평균 투약일수보다 길게 처방된 약물 행은? <span class="desc">스칼라 서브쿼리</span></li>
        <li><b>Q2.</b> 폐렴(J18) 진단 이력이 있는 환자의 성별·생년월일은? <span class="desc">IN</span></li>
        <li><b>Q3.</b> 검사(lab)를 한 번도 받지 않은 환자 수는? <span class="desc">NOT EXISTS</span></li>
        <li><b>Q4.</b> 자기 진료과 평균보다 재원이 길었던 입원 건은? <span class="desc">도전: 상관 서브쿼리</span></li>
        <li><b>Q5.</b> Q3를 NOT IN으로도 써 보고, 어떤 상황에서 위험해지는지 한 줄로 설명하라</li>
        </ul>""",
        tag="실습"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["서브쿼리(subquery)", "괄호 안에서 논리적으로 먼저 평가되는 내부 쿼리"],
         ["스칼라 서브쿼리", "값 하나를 반환하는 서브쿼리 — 비교 기준으로 사용"],
         ["상관 서브쿼리", "바깥 쿼리의 행을 참조하며 행마다 다시 평가되는 서브쿼리"],
         ["EXISTS / NOT EXISTS", "조건에 맞는 행이 하나라도 있는가 / 전혀 없는가"],
         ["IN / NOT IN", "명단 포함 / 미포함 — NOT IN은 명단에 NULL이 있으면 0행"],
         ["노출군 / 비노출군", "약물 등 연구 요인에 노출된 집단 / 노출되지 않은 대조 집단"]],
        small=True, tag="용어"),

    closing(12,
            ["서브쿼리 = <b>두 단계 질문의 한 문장화</b> — 안쪽이 먼저, 바깥이 나중",
             "스칼라(값 하나) · IN(명단) · <b>EXISTS/NOT EXISTS(이력 유무)</b>",
             "\"~한 적 없는 환자\"는 NOT EXISTS — <b>NOT IN은 NULL이 섞이면 조용히 0행</b>이 된다",
             "노출군/비노출군 정의 = EXISTS 한 쌍 — 약물역학의 문법"],
            homework="Colab 12주차 Q1~Q5",
            next_week="종합 실전 — 연구 질문에서 코호트 추출, 그리고 Table 1까지 한 번에"),
]
