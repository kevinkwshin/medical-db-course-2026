# -*- coding: utf-8 -*-
"""15강. 기말고사와 총정리 (원본 169~174번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)

SPAN = (169, 174)
TITLE = "15강. 기말고사"

AGENDA = [("시험 안내", "범위 · 문항 · 평가"),
          ("총복습 ①", "데이터베이스와 DBMS"),
          ("총복습 ②", "관계형 모델과 설계"),
          ("총복습 ③", "SQL"),
          ("총복습 ④", "CDW와 오류"),
          ("마무리", "수업을 마치며")]


def exam_info_slide():
    def b(ids):
        s = panel(ids, X0, 1550000, 6000000, 2500000, "시험 방식", [
            "날짜: 15주차 수업 시간",
            "형식: 지필 (SQL 문장을 손으로 작성)",
            "시간: 60분",
            "참고자료: 없음 (용어표는 문제지에 제공)",
            "배점: 100점 → 최종 성적의 40%"], fill="DEEAF6", line="1F497D", sz=1900)
        s += panel(ids, 7300000, 1550000, 6000000, 2500000, "최종 평가 구성", [
            "기말고사 40%",
            "과제 1 (9주차) 20%",
            "과제 2 (13주차) 20%",
            "출석 20%",
            "중간고사는 실시하지 않습니다"], fill="E2EFDA", line="2C5F2D", sz=1900)
        rows = [["개념 이해", "용어의 뜻과 구분", "30점", "단답 · 선택 · 짧은 서술"],
                ["SQL 읽기", "주어진 SQL이 무엇을 구하는지", "25점", "결과 단위 · 조건 설명"],
                ["SQL 쓰기", "질문을 SQL로 작성", "25점", "SELECT · WHERE · GROUP BY · JOIN"],
                ["오류 찾기", "잘못된 SQL이나 해석 고치기", "20점", "무엇이 왜 틀렸는지 설명"]]
        t, h = table(ids, X0, 4300000, [2400000, 4200000, 1400000, 4400000],
                     [["영역", "무엇을 묻나", "배점", "문항 형태"]] + rows,
                     sz=1900, row_h=470000, header_h=470000, col_algn=["ctr", "l", "ctr", "l"])
        s += t
        return s
    return free("기말고사 안내", b, subtitle="시험 방식과 배점")


def scope_slide():
    return table_slide("시험 범위", "주차별로 꼭 알아야 할 것",
        ["주차", "주제", "꼭 알아야 할 것"],
        [["1 · 2 · 3", "데이터베이스와 DBMS", "데이터/정보, DBMS의 기능과 장단점, DDL · DML · DCL"],
         ["4", "데이터베이스 시스템", "스키마와 인스턴스, 3단계 스키마, 사상, 데이터 독립성, 데이터 사전"],
         ["5", "관계형 데이터베이스", "테이블 · 속성 · 튜플, 기본키 · 외래키, 무결성 3종, 타입과 NULL"],
         ["6", "모델링과 정규화", "ERD 읽기, 이상현상 3종, 1NF · 2NF · 3NF, 반정규화"],
         ["7 · 8 · 9", "SQL", "SELECT · WHERE · GROUP BY · HAVING · JOIN, 실행 순서,\n집계, CASE WHEN · COALESCE, 서브쿼리"],
         ["10", "수정과 트랜잭션", "INSERT · UPDATE · DELETE, WHERE 누락, 트랜잭션, COMMIT · ROLLBACK"],
         ["11 · 12 · 13", "CDW와 오류", "CDW 구조, 목적에 따른 절차, 한 행의 단위, 오류 유형,\n검산표, 코호트 정의 3요소"],
         ["14", "빅데이터와 표준", "정형/비정형, 용어 · 교환 · 구조 표준, OMOP CDM, 품질, 가명정보"]],
        [1800000, 3000000, 7400000], sz=1700, row_h=440000, y=1480000,
        col_algn=["ctr", "l", "l"],
        note="각 주차의 ‘강의 정리’ 슬라이드와 ‘용어 정리’ 표가 가장 좋은 복습 자료입니다.")


def review1_slide():
    return table_slide("총복습 ① — 데이터베이스와 DBMS", "1~4주차 핵심",
        ["개념", "한 줄 정의", "자주 나오는 구분"],
        [["데이터베이스", "공유하여 사용하려고 통합 저장한 운영 데이터의 집합", "데이터 / 정보 / 지식"],
         ["DBMS", "데이터베이스를 만들고 관리하는 프로그램", "파일시스템과의 차이 (중복 · 종속성)"],
         ["데이터베이스 언어", "DDL(정의) · DML(조작) · DCL(제어)", "CREATE / SELECT / GRANT"],
         ["스키마 · 인스턴스", "틀(구조) / 지금 들어 있는 값", "거의 안 변함 / 계속 변함"],
         ["3단계 스키마", "외부(화면) · 개념(전체) · 내부(저장)", "외부는 여러 개, 나머지는 하나"],
         ["사상 (Mapping)", "세 단계를 이어 주는 대응 규칙", "외부/개념, 개념/내부"],
         ["데이터 독립성", "구조가 바뀌어도 프로그램은 그대로", "논리적(외부↔개념) / 물리적(개념↔내부)"],
         ["데이터 사전", "테이블 · 열 · 타입 · 키를 설명한 메타데이터", "= 시스템 카탈로그"]],
        [2400000, 5000000, 4800000], sz=1800, row_h=500000, y=1580000,
        col_algn=["ctr", "l", "l"])


def review2_slide():
    return table_slide("총복습 ② — 관계형 모델과 설계", "5~6주차 핵심",
        ["개념", "한 줄 정의", "자주 나오는 구분"],
        [["테이블 구성", "행(튜플) × 열(속성)", "차수 = 열 수, 카디널리티 = 행 수"],
         ["후보키 · 기본키", "행을 유일하게 찾는 열 / 그중 대표", "기본키는 NULL · 중복 불가"],
         ["대체키 · 슈퍼키", "기본키가 아닌 후보키 / 유일성만 만족", "슈퍼키는 최소성 불만족"],
         ["외래키", "다른 표의 기본키를 가리키는 열", "참조 무결성"],
         ["무결성 3종", "개체 · 참조 · 도메인", "기본키 / 외래키 / 타입 · 범위"],
         ["이상현상", "삽입 · 삭제 · 갱신 이상", "표를 안 나눠서 생김"],
         ["정규화", "1NF 원자값 · 2NF 부분종속 · 3NF 이행종속", "무엇을 떼어내는가"],
         ["반정규화", "성능을 위해 일부러 합치고 중복 허용", "CDW가 대표적"]],
        [2400000, 5000000, 4800000], sz=1800, row_h=500000, y=1580000,
        col_algn=["ctr", "l", "l"])


def review3_slide():
    def b(ids):
        s = ""
        rows = [("SELECT", "⑤", "무엇을 볼지 · 집계 계산"),
                ("FROM", "①", "어느 표에서"),
                ("WHERE", "②", "어떤 행만 (묶기 전)"),
                ("GROUP BY", "③", "같은 값끼리 묶기"),
                ("HAVING", "④", "묶은 그룹에 조건"),
                ("ORDER BY", "⑥", "정렬"),
                ("LIMIT", "⑦", "앞에서 몇 줄")]
        y, h, gap = 1600000, 540000, 70000
        for kw, o, what in rows:
            s += shape(ids, "rect", X0, y, 2500000, h, fill="DEEAF6", line="1F497D",
                       text_xml=para(f"**{kw}**", sz=2000, algn="ctr", color=BLUE, font="Courier New", lnSpc=100), name="KW")
            s += shape(ids, "rect", X0 + 2500000, y, 800000, h, fill="FFF2CC", line="BF9000",
                       text_xml=para(f"**{o}**", sz=2000, algn="ctr", lnSpc=100), name="O")
            s += shape(ids, "rect", X0 + 3300000, y, 3400000, h, fill="FFFFFF", line="7F7F7F",
                       text_xml=para(what, sz=1800, lnSpc=100, marL=180000), name="W")
            y += h + gap
        s += textbox(ids, 8000000, 1600000, 5300000, 4400000,
            para("**꼭 기억할 것**", sz=2300, lnSpc=130) +
            para("COUNT(*) ≠ COUNT(열) ≠ COUNT(DISTINCT 열)", sz=1900, lvl=1, lnSpc=124) +
            para("WHERE는 묶기 전, HAVING은 묶은 뒤", sz=1900, lvl=1, lnSpc=124) +
            para("문자 · 날짜는 '작은따옴표'", sz=1900, lvl=1, lnSpc=124) +
            para("빈 값은 = NULL 이 아니라 IS NULL", sz=1900, lvl=1, lnSpc=124) +
            para("JOIN은 ON에 연결 키, 뒤에 행 수 확인", sz=1900, lvl=1, lnSpc=124) +
            para("INNER JOIN은 양쪽 다 있는 행만, LEFT JOIN은 왼쪽 모두", sz=1900, lvl=1, lnSpc=124) +
            para("비율은 100.0 을 곱해서 계산", sz=1900, lvl=1, lnSpc=124) +
            para("CASE WHEN = 조건에 따라 나누기, COALESCE = 빈 값 바꾸기", sz=1900, lvl=1, lnSpc=124) +
            para("대상만 고를 때는 서브쿼리, 열까지 볼 때는 JOIN", sz=1900, lvl=1, lnSpc=124) +
            para("UPDATE · DELETE에는 WHERE", sz=1900, lvl=1, lnSpc=124), autofit=False)
        return s
    return free("총복습 ③ — SQL", b, subtitle="7~10주차 핵심")


def review4_slide():
    return table_slide("총복습 ④ — CDW와 오류", "11~14주차 핵심",
        ["개념", "한 줄 정의", "자주 나오는 구분"],
        [["CDW", "분석 · 연구용으로 모아 둔 읽기 전용 복사본", "운영 DB는 진료용, CDW는 분석용"],
         ["ETL", "원천에서 뽑아 정리해 CDW에 넣는 작업", "보통 하루 정도 시차"],
         ["한 행의 단위", "표의 한 행이 무엇을 뜻하는가", "환자 / 방문 / 처방"],
         ["기준일", "대상자마다 분석의 출발점이 되는 날짜", "기준일 이후 자료는 쓰지 않음"],
         ["검산표", "단계별 건수를 기록한 표", "어디에서 얼마나 줄었는지 설명"],
         ["표준 코드", "같은 것을 같은 코드로 부르기", "KCD · LOINC · SNOMED · ATC"],
         ["OMOP CDM", "여러 기관의 데이터를 같은 구조로 맞춘 모델", "PERSON · VISIT · CONDITION …"],
         ["가명정보", "추가 정보 없이는 개인을 알아볼 수 없게 처리", "가명 / 익명의 차이"]],
        [2400000, 5000000, 4800000], sz=1800, row_h=500000, y=1580000,
        col_algn=["ctr", "l", "l"])


def exam_tip_slide():
    def b(ids):
        s = panel(ids, X0, 1550000, 6000000, 2400000, "SQL 문제를 풀 때", [
            "① 질문이 무엇을 세는지 먼저 적는다",
            "② FROM · JOIN에 쓸 표와 연결 키를 찾는다",
            "③ WHERE 조건(날짜 · 코드)을 적는다",
            "④ 묶어야 하면 GROUP BY, 집계 조건은 HAVING",
            "⑤ 마지막에 절의 순서를 확인한다"], fill="DEEAF6", line="1F497D", sz=1900)
        s += panel(ids, 7300000, 1550000, 6000000, 2400000, "오류 문제를 풀 때", [
            "① JOIN 뒤 행 수가 늘었는가",
            "② INNER JOIN으로 분모가 줄었는가",
            "③ 기준일 이후 정보가 들어갔는가",
            "④ NULL을 0으로 바꾸었는가",
            "⑤ 표기 · 타입이 맞는가"], fill="E2EFDA", line="2C5F2D", sz=1900)
        s += textbox(ids, X0, 4250000, W0, 2200000,
            para("**부분 점수가 있습니다**", sz=2400, lnSpc=130) +
            para("SQL이 완전하지 않아도 맞는 절 · 조건에는 점수를 드립니다", sz=2100, lvl=1, lnSpc=125) +
            para("오류 문제는 “무엇이 틀렸는지”와 “왜 틀렸는지”를 함께 쓰면 만점", sz=2100, lvl=1, lnSpc=125) +
            para("서술형은 길게 쓰기보다 **용어를 정확히** 쓰는 것이 중요합니다", sz=2100, lvl=1, lnSpc=125) +
            para("각 주차의 ‘강의 정리’와 ‘용어 정리’ 슬라이드를 중심으로 복습하세요.",
                 sz=2200, b=True, algn="ctr", color=BLUE, lnSpc=125, spcBef=12))
        return s
    return free("시험 준비 요령", b, subtitle="문제 유형별로")


def closing_slide():
    def b(ids):
        s = textbox(ids, X0, 1450000, W0, 800000,
            para("이 수업에서 가장 중요한 것 세 가지", sz=3000, b=True, algn="ctr", color=BLUE, lnSpc=120))
        items = [("데이터의 구조를 먼저 본다",
                  "표가 무엇을 담고 있고, 한 행이 무엇을 뜻하는지 확인하는 것이 분석의 시작입니다."),
                 ("SQL은 질문을 옮기는 언어다",
                  "문법을 외우는 것보다 질문을 대상 · 기간 · 조건 · 단위로 나누는 연습이 중요합니다."),
                 ("숫자는 검산한 뒤에 쓴다",
                  "건수와 분모를 확인하고, 어떻게 구했는지 설명할 수 있어야 그 숫자를 쓸 수 있습니다.")]
        y = 2500000
        for i, (t, d) in enumerate(items, 1):
            s += shape(ids, "rect", X0 + 300000, y, 900000, 1100000, fill="1F497D", line="1F497D",
                       text_xml=para(f"**{i}**", sz=3200, algn="ctr", color="FFFFFF", lnSpc=100), name="No")
            s += shape(ids, "rect", X0 + 1200000, y, 10800000, 1100000, fill="F6F8FA", line="BFBFBF",
                       text_xml=para(f"**{t}**", sz=2400, lnSpc=110, marL=280000) +
                                para(d, sz=2000, lnSpc=115, marL=280000, color="1F3763"), name="Item")
            y += 1250000
        s += textbox(ids, X0, 6350000, W0, 600000,
            para("한 학기 동안 수고 많으셨습니다.", sz=2600, b=True, algn="ctr", lnSpc=115))
        return s
    return free("수업을 마치며", b, subtitle="현장에 돌아가서 기억할 것")


def build(c):
    # --- 도입
    c.add(cover(15, "기말고사와 총정리",
                ["시험 범위와 문항 유형", "1~14주차 총복습", "수업 마무리"],
                "2026. 12. 22."))
    c.add(content("지난시간 리뷰", [
        ("**표준 용어**와 **공통 데이터 모델**이 다기관 비교와 재사용을 가능하게 한다", dict(lvl=1, marL=457200, indent=-457200)),
        ("구조가 달라져도 **기본키 · 외래키 · JOIN** 은 그대로 쓰인다", dict(lvl=1, marL=457200, indent=-457200)),
        ("분석 전에 **품질을 점검**하고 **가명처리와 승인 범위**를 지킨다", dict(lvl=1, marL=457200, indent=-457200)),
        ("오늘은 시험 안내와 함께 한 학기 내용을 한 번에 정리합니다.",
         dict(b=True, algn="ctr", color=BLUE, spcBef=24)),
    ]))

    # --- 1. 시험 안내
    c.add(section_slide(1, AGENDA, lead="먼저 시험 방식과 범위를 안내합니다"))
    c.add(exam_info_slide())
    c.add(scope_slide())
    c.add(exam_tip_slide())

    # --- 2~5. 총복습
    c.add(section_slide(2, AGENDA, lead="1~4주차: 데이터베이스가 무엇인지"))
    c.add(review1_slide())
    c.add(section_slide(3, AGENDA, lead="5~6주차: 표를 어떻게 만들고 나누는지"))
    c.add(review2_slide())
    c.add(section_slide(4, AGENDA, lead="7~10주차: 데이터를 꺼내고 바꾸는 방법"))
    c.add(review3_slide())
    c.add(table_slide("총복습 ③ 보충 — 자주 틀리는 SQL", "시험에 자주 나오는 형태",
        ["이렇게 쓰면", "무엇이 문제", "이렇게 고칩니다"],
        [["WHERE 결과 = NULL", "오류 없이 0행", "WHERE 결과 IS NULL"],
         ["WHERE COUNT(*) > 10", "WHERE는 묶기 전", "HAVING COUNT(*) > 10"],
         ["SELECT a, COUNT(*) GROUP BY b", "a가 묶는 열이 아님", "GROUP BY a, b"],
         ["LIMIT 5 ORDER BY x", "절의 순서 오류", "ORDER BY x LIMIT 5"],
         ["JOIN 뒤 COUNT(*)", "행 수 ≠ 대상 수", "COUNT(DISTINCT 키)"],
         ["100 * a / b", "정수 나눗셈으로 잘림", "100.0 * a / b"],
         ["AVG(값)  (빈 값 많음)", "NULL은 빼고 평균", "COUNT(*)와 COUNT(값)을 같이 본다"]],
        [4900000, 3000000, 4300000], sz=1800, row_h=500000, y=1650000,
        col_algn=["l", "l", "l"], col_font={0: "Courier New", 2: "Courier New"},
        note="12주차 오류 사례와 함께 보면 시험 준비가 됩니다."))
    c.add(section_slide(5, AGENDA, lead="11~14주차: 실무에서 데이터를 다루는 법"))
    c.add(review4_slide())

    # --- 6. 마무리
    c.add(section_slide(6, AGENDA, lead="한 학기 동안 배운 것을 정리합니다"))
    c.add(closing_slide())
