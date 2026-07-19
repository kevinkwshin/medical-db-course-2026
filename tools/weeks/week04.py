# -*- coding: utf-8 -*-
"""4주차 — SELECT ②: WHERE 조건으로 골라내기"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing)

WEEK = 4
TITLE = "SELECT ② — WHERE 조건"

slides = [
    cover(4, "SELECT ②<br>WHERE — 조건으로 골라내기",
          ["비교 연산자와 날짜 조건",
           "AND / OR / NOT — 조건 조합하기",
           "BETWEEN · IN · LIKE — 범위, 목록, 패턴",
           "IS NULL — 비어 있음을 묻는 법"],
          question="65세 이상 여성 환자는 몇 명인가?"),

    qsql("여성 환자만 보여줘",
         "SELECT patient_id, sex, birth_date\nFROM patient\nWHERE sex = 'F';",
         max_rows=6,
         title="WHERE — 행을 거르는 조건문",
         note="문자값은 <b>작은따옴표</b> 'F'. WHERE는 조건이 참인 행만 통과시킵니다. "
              "비교 연산자: <span class='mono'>= != &gt; &lt; &gt;= &lt;=</span>"),

    qsql("1950년 이전에 태어난 환자는?",
         "SELECT patient_id, birth_date\nFROM patient\nWHERE birth_date < '1950-01-01'\nORDER BY birth_date;",
         max_rows=6,
         title="날짜 조건 — 문자열처럼 비교한다",
         note="날짜를 'YYYY-MM-DD' 형식으로 저장하면 문자열 비교가 곧 시간 순서가 됩니다. "
              "<b>형식 통일이 무너지면</b>(01/12/2024 vs 2024-12-01) 이 비교 전체가 무너집니다 — 14주차 주제."),

    qsql("65세 이상 여성 환자는? (2026년 기준 연 나이)",
         "SELECT patient_id, sex, birth_date,\n       2026 - CAST(substr(birth_date,1,4) AS INT) AS age\nFROM patient\nWHERE sex = 'F'\n  AND 2026 - CAST(substr(birth_date,1,4) AS INT) >= 65;",
         max_rows=6,
         title="AND — 두 조건 모두 만족",
         tag="대표 질문",
         note="substr으로 출생연도를 잘라 연 나이를 계산했습니다(간단하지만 생일 미도래를 무시하는 '연 나이'라는 한계 있음). "
              "연구에서는 <b>어느 시점의 나이인가</b>(index date 기준)가 늘 쟁점입니다 — 13주차에서 다시."),

    qsql("응급 또는 입원으로 온 내원은?",
         "SELECT visit_id, visit_date,\n       department, visit_type\nFROM visit\nWHERE visit_type = '응급'\n   OR visit_type = '입원'\nORDER BY visit_date DESC;",
         max_rows=6,
         title="OR — 둘 중 하나라도",
         note="AND와 OR을 섞을 때는 <b>괄호</b>로 의도를 명시하세요: "
              "<span class='mono'>WHERE (A OR B) AND C</span> 와 <span class='mono'>WHERE A OR (B AND C)</span>는 "
              "완전히 다른 환자군입니다."),

    qsql("같은 질문, 더 깔끔하게 — IN",
         "SELECT visit_id, visit_date,\n       department, visit_type\nFROM visit\nWHERE visit_type IN ('응급', '입원')\nORDER BY visit_date DESC;",
         max_rows=6,
         title="IN — 목록 안에 있는가",
         note="OR을 여러 번 쓰는 대신 IN (값1, 값2, …). 진단코드 목록, 약물 목록을 다룰 때 "
              "필수 도구가 됩니다. 반대는 <span class='mono'>NOT IN</span>."),

    qsql("2024년에 발생한 내원만 보려면?",
         "SELECT visit_id, visit_date, department\nFROM visit\nWHERE visit_date BETWEEN '2024-01-01'\n                     AND '2024-12-31'\nORDER BY visit_date;",
         max_rows=6,
         title="BETWEEN — 범위 조건 (양 끝 포함)",
         note="'2024-12-31' 내원도 포함됩니다(양끝 포함) — 연구 기간 정의의 기본 문형."),

    qsql("순환기계 질환(KCD I코드) 진단을 모두 찾아라",
         "SELECT dx_id, kcd_code, dx_name\nFROM diagnosis\nWHERE kcd_code LIKE 'I%'\nORDER BY kcd_code;",
         max_rows=7,
         title="LIKE — 패턴으로 찾기",
         tag="대표 질문",
         note="<span class='mono'>%</span>는 '아무 글자 여러 개', <span class='mono'>_</span>는 '아무 글자 한 개'. "
              "KCD는 알파벳 첫 글자가 질환 대분류라서 <b>LIKE 'I%' = 순환기계 전체</b>가 됩니다. "
              "코드 체계를 알면 LIKE 한 줄이 강력한 필터가 됩니다."),

    qsql("당뇨(E11) 계열 진단만 — 더 구체적인 패턴",
         "SELECT DISTINCT kcd_code, dx_name\nFROM diagnosis\nWHERE kcd_code LIKE 'E11%';",
         title="LIKE 연습 — 코드 패밀리 찾기",
         note="E11.0, E11.9처럼 소수점 세분류가 붙어도 'E11%'가 전부 잡습니다. "
              "연구 정의서에서 '당뇨병: E11.x'라고 쓰는 것이 이 패턴입니다."),

    qsql("아직 퇴원일이 기록되지 않은 입원 vs 외래·응급 — NULL 구분하기",
         "SELECT visit_id, visit_type,\n       visit_date, discharge_date\nFROM visit\nWHERE discharge_date IS NULL\nORDER BY visit_type;",
         max_rows=6,
         title="IS NULL — 비어 있음을 묻는 유일한 방법",
         note="<span class='danger'>discharge_date = NULL 은 아무 행도 찾지 못합니다</span> — NULL은 '='로 비교 불가(2주차). "
              "반드시 <span class='mono'>IS NULL / IS NOT NULL</span>. 이 데이터에서 퇴원일 NULL은 "
              "외래·응급 귀가라는 <b>구조적 의미</b>입니다."),

    html_slide("연습문제 — 조건을 조합해 보세요",
        """<ul class="big">
        <li><b>Q1.</b> 남성이면서 O+ 혈액형인 환자는?</li>
        <li><b>Q2.</b> 2023년 이후 신경과 내원을 최신순으로</li>
        <li><b>Q3.</b> 호흡기계(J코드) 진단을 모두 찾아라 <span class="desc">힌트: LIKE</span></li>
        <li><b>Q4.</b> 투약일수가 30일 이상 90일 이하인 처방은? <span class="desc">힌트: BETWEEN</span></li>
        <li><b>Q5.</b> 정상 상한(ref_high)이 기록되지 않은 검사가 있는가? <span class="desc">힌트: IS NULL</span></li>
        </ul>""",
        tag="실습"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["조건식(술어, predicate)", "WHERE 뒤에서 행마다 참/거짓으로 판정되는 식"],
         ["논리 연산자", "AND(모두 만족) · OR(하나라도) · NOT(부정) — 섞을 땐 괄호로 우선순위 명시"],
         ["BETWEEN A AND B", "범위 조건 — 양쪽 끝 값 포함"],
         ["IN (목록)", "목록의 값 중 하나와 일치 — 코드 목록 필터의 기본"],
         ["LIKE / 와일드카드", "패턴 검색 — %(아무 글자 여러 개), _(아무 글자 한 개)"],
         ["IS NULL / IS NOT NULL", "값 없음/있음 검사 — '=NULL'은 아무 행도 찾지 못함"],
         ["연 나이", "올해 − 출생연도 (생일 미도래 무시) — 만 나이와 다르므로 논문엔 정의 명시"],
         ["KCD", "한국표준질병·사인분류 — WHO ICD 기반 국내 진단코드 체계, 현재 8차 개정(KCD-8)"]],
        small=True, tag="용어"),

    closing(4,
            ["WHERE = 행 필터. 비교 연산자 + <b>AND/OR(괄호로 명시)</b>로 조건을 쌓는다",
             "IN(목록) · BETWEEN(범위, 양끝 포함) · LIKE(패턴) — <b>연구 정의서의 3대 문형</b>",
             "KCD 코드 체계 × LIKE = 질환군 필터 (<span class='mono'>LIKE 'I%'</span> → 순환기계)",
             "NULL은 <span class='mono'>IS NULL</span>로만 — <b>=NULL은 조용히 실패한다</b>"],
            homework="Colab 4주차 Q1~Q5 + '내 연구 관심 질환의 KCD 패턴' 한 줄 찾아오기",
            next_week="계산과 집계 — 재원일수 구하기, CASE로 혈압 분류하기, COUNT/AVG"),
]
