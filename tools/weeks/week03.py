# -*- coding: utf-8 -*-
"""3주차 — SELECT ①: 조회의 기본기"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, code)

WEEK = 3
TITLE = "SELECT ① — 조회의 기본기"

slides = [
    cover(3, "SELECT ①<br>데이터 꺼내기의 기본기",
          ["SELECT · FROM — 무엇을, 어디서",
           "컬럼 고르기와 별칭(AS)",
           "DISTINCT — 중복 없이 보기",
           "ORDER BY · LIMIT — 정렬하고 자르기"],
          question="우리 병원엔 어떤 진료과가 있나?"),

    html_slide("SQL 문장의 기본 골격",
        """<div class="cols" style="grid-template-columns:1.1fr 1fr">
        <div><pre class="sql" style="font-size:23px">SELECT 컬럼1, 컬럼2   -- 무엇을
FROM 테이블           -- 어디서
ORDER BY 컬럼        -- 어떤 순서로
LIMIT 숫자;          -- 몇 개만</pre></div>
        <div class="side">
        <ul><li>영어 문장처럼 읽힌다: <b>"visit에서 내원일과 진료과를 골라줘"</b></li>
        <li>대소문자 구분 없음 (관례상 예약어는 대문자)</li>
        <li>문장 끝에는 세미콜론 <span class="mono">;</span></li>
        <li><span class="mono">--</span> 뒤는 주석 — 실행되지 않는 메모</li></ul>
        </div></div>""",
        tag="문법"),

    qsql("환자 테이블 전체를 보여줘",
         "SELECT *\nFROM patient;",
         max_rows=6,
         title="SELECT * — 일단 전부 꺼내기",
         note="<span class='mono'>*</span>는 '모든 컬럼'. 탐색 단계가 지나면 <b>필요한 컬럼만 지정</b>하고, "
              "대용량 테이블은 조건이나 LIMIT 없이 조회하지 않는 것이 관례입니다."),

    qsql("환자의 ID와 생년월일만 보고 싶다",
         "SELECT patient_id, birth_date\nFROM patient;",
         max_rows=6,
         title="컬럼 골라 꺼내기",
         note="필요한 컬럼만 명시하는 습관 = 개인정보 최소 수집의 습관. "
              "연구에 혈액형이 필요 없다면 꺼내지 않는 것이 원칙입니다."),

    qsql("컬럼 이름을 읽기 좋게 바꿔서 보여줘",
         "SELECT patient_id AS 환자번호,\n       birth_date AS 생년월일,\n       blood_type AS 혈액형\nFROM patient;",
         max_rows=5,
         title="별칭(AS) — 보고서용 이름 붙이기",
         note="AS는 <b>표시 이름만</b> 바꿉니다. 원본 테이블은 그대로 — SELECT는 데이터를 절대 바꾸지 않는, "
              "안전한 '읽기 전용' 명령입니다."),

    qsql("우리 병원엔 어떤 진료과가 있나?",
         "SELECT DISTINCT department\nFROM visit;",
         title="DISTINCT — 중복 없이 목록 보기",
         tag="대표 질문",
         note="visit 100행에는 진료과가 반복 등장하지만, DISTINCT가 중복을 걷어내고 "
              "<b>종류만</b> 보여줍니다. \"우리 데이터에 어떤 값들이 들어있지?\"를 묻는 탐색의 첫 도구."),

    qsql("의료진은 어떤 직종으로 구성되어 있나?",
         "SELECT DISTINCT role\nFROM staff;",
         title="DISTINCT 연습 — staff 테이블",
         note="새 데이터셋을 받으면 가장 먼저 할 일: 주요 범주형 컬럼마다 DISTINCT로 "
              "<b>값의 종류</b>를 훑어보기. 오타·코드 혼용이 여기서 발견됩니다."),

    qsql("환자를 나이 많은 순서로 정렬해줘",
         "SELECT patient_id, birth_date, sex\nFROM patient\nORDER BY birth_date ASC;",
         max_rows=6,
         title="ORDER BY — 정렬",
         note="생년월일 <b>오름차순(ASC)</b> = 나이 <b>많은</b> 순. 헷갈리기 쉬운 지점입니다. "
              "내림차순은 <span class='mono'>DESC</span>. ASC는 기본값이라 생략 가능."),

    qsql("가장 최근 내원 5건은?",
         "SELECT visit_id, patient_id,\n       visit_date, department\nFROM visit\nORDER BY visit_date DESC\nLIMIT 5;",
         max_rows=5,
         title="ORDER BY + LIMIT — 최신순 상위 N개",
         note="<b>정렬 없이 LIMIT만 쓰면</b> '아무 5건'이 나옵니다 — 행에는 순서가 없으니까요(2주차). "
              "'최근 5건'은 반드시 ORDER BY와 세트."),

    qsql("정렬 기준이 두 개라면? — 진료과별로 묶고, 그 안에서 최신순",
         "SELECT department, visit_date, visit_id\nFROM visit\nORDER BY department ASC,\n         visit_date DESC\nLIMIT 8;",
         max_rows=8,
         title="다중 정렬",
         note="쉼표 순서가 곧 우선순위입니다."),

    html_slide("연습문제 — 직접 번역해 보세요",
        """<ul class="big">
        <li><b>Q1.</b> 검사(lab) 테이블에는 어떤 검사 종류들이 있는가? <span class="desc">힌트: DISTINCT</span></li>
        <li><b>Q2.</b> 처방(prescription)에서 약품명과 용량만, 약품명 가나다순으로 <span class="desc">힌트: ORDER BY</span></li>
        <li><b>Q3.</b> 가장 어린 환자 3명의 ID와 생년월일은? <span class="desc">힌트: birth_date DESC + LIMIT</span></li>
        <li><b>Q4.</b> 영상(imaging) 테이블의 촬영종류 목록은?</li>
        </ul>
        <div class="note">정답 쿼리는 이번 주 Colab 노트북 마지막 '정답 및 해설' 섹션에 있습니다.</div>""",
        tag="실습"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["예약어(keyword)", "SELECT·FROM처럼 SQL이 미리 정해둔 단어 — 관례상 대문자로 표기"],
         ["절(clause)", "SELECT 절, FROM 절처럼 문장을 구성하는 블록 단위"],
         ["별칭(alias)", "AS로 붙이는 표시용 이름 — 원본 데이터는 바뀌지 않음"],
         ["DISTINCT", "결과에서 중복 행을 제거 — 값의 종류를 볼 때"],
         ["ASC / DESC", "오름차순(작→큰, 기본값) / 내림차순(큰→작)"],
         ["LIMIT", "반환할 행 수를 제한 — 큰 테이블 탐색의 안전장치"],
         ["주석(comment)", "'--' 뒤의 실행되지 않는 메모 — 쿼리의 의도를 기록"]],
        small=True, tag="용어"),

    closing(3,
            ["<span class='mono'>SELECT 컬럼 FROM 테이블</span> — \"무엇을, 어디서\"가 모든 조회의 뼈대",
             "AS로 보고서용 이름, DISTINCT로 <b>값의 종류 탐색</b>",
             "ORDER BY 없는 LIMIT은 '아무거나 N개' — <b>최신순·상위권은 반드시 정렬과 세트</b>",
             "SELECT는 데이터를 변경하지 않는다 — 단, 대용량 조회의 실행 비용은 별개 문제"],
            homework="Colab 노트북 3주차 연습문제 Q1~Q4 제출",
            next_week="WHERE — 조건으로 골라내기 (\"65세 이상 여성 환자는?\", \"I로 시작하는 진단은?\")"),
]
