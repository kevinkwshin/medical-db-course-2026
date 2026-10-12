# -*- coding: utf-8 -*-
"""5강. 관계형 데이터베이스 (원본 78~87번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)

SPAN = (78, 87)
TITLE = "5강. 관계형 데이터베이스"

AGENDA = [("관계형 데이터베이스", "왜 표로 저장하는가"),
          ("테이블의 구성과 특성", "속성 · 튜플 · 지켜야 할 5가지"),
          ("키(Key)", "기본키 · 외래키"),
          ("무결성 제약조건", "잘못된 값을 막는 규칙"),
          ("데이터 타입과 NULL", "값의 종류와 빈 값"),
          ("정리", "용어와 요약")]


def _key_preview(ids):
    """키 5종 미리보기 — 옛 슬라이드 아래 빈 공간을 채웁니다."""
    rows = [["후보키", "행을 유일하게 구분할 수 있는 열(들)"],
            ["기본키", "후보키 중 대표로 고른 것 (NULL · 중복 불가)"],
            ["대체키", "기본키로 뽑히지 않은 나머지 후보키"],
            ["슈퍼키", "유일성만 만족하면 되는 키 (최소성은 따지지 않음)"],
            ["외래키", "다른 표의 기본키를 가리키는 열"]]
    s, h = table(ids, X0 + 1400000, 2900000, [2400000, 7200000],
                 [["종류", "한 줄 설명"]] + rows, sz=1900, row_h=480000, header_h=460000,
                 col_algn=["ctr", "l"])
    s += textbox(ids, X0, 2900000 + h + 350000, W0, 500000,
                 para("다섯 가지를 차례로 살펴봅니다.", sz=2300, b=True, algn="ctr", lnSpc=115))
    return s


def terms_table_slide():
    return table_slide("관계형 데이터베이스의 용어", "같은 것을 부르는 이름이 여러 개입니다",
        ["수학 · 이론에서", "데이터베이스에서", "엑셀에서", "뜻"],
        [["릴레이션 (Relation)", "테이블 (Table)", "시트 · 표", "행과 열로 이루어진 자료"],
         ["튜플 (Tuple)", "행 (Row) · 레코드", "한 줄", "환자 한 명, 임상시험 한 건"],
         ["속성 (Attribute)", "열 (Column) · 필드", "한 칸(세로)", "환자명, 나이처럼 기록하는 항목"],
         ["도메인 (Domain)", "데이터 타입 · 값의 범위", "셀 서식", "그 열에 들어갈 수 있는 값의 범위"],
         ["차수 (Degree)", "열의 개수", "열 수", "속성이 몇 개인가"],
         ["카디널리티", "행의 개수", "행 수", "튜플이 몇 개인가"]],
        [3100000, 3100000, 2000000, 4300000], sz=1800, row_h=520000, y=1600000,
        col_algn=["ctr", "ctr", "ctr", "l"],
        note="교재와 시험에서는 릴레이션 · 튜플 · 속성이라는 말을 씁니다. 실무에서는 테이블 · 행 · 열이라고 부릅니다.",
        note_style="footnote")


def aact_rows_cols_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("studies 테이블의 한 조각입니다. 행과 열이 각각 무엇을 뜻하는지 봅시다.", sz=2200, lnSpc=115))
        t, h = table(ids, X0 + 700000, 2150000, [1950000, 3300000, 1650000, 1500000, 2100000],
            [["nct_id", "brief_title", "start_date", "enrollment", "phase"],
             ["NCT04280705", "Adaptive COVID-19 Treatment Trial", "2020-02-21", "1062", "PHASE3"],
             ["NCT04368728", "Safety, Tolerability … Vaccine", "2020-04-29", "44047", "PHASE2/PHASE3"],
             ["NCT04470427", "Efficacy, Safety … mRNA-1273", "2020-07-27", "30420", "PHASE3"]],
            sz=1700, row_h=520000, col_algn=["ctr", "l", "ctr", "ctr", "ctr"])
        s += t
        y = 2150000 + h
        s += textbox(ids, X0 + 700000, y + 200000, 5000000, 500000,
                     para("↑ 열(column) = **속성** : 기록하는 항목", sz=2000, b=True, color=BLUE, lnSpc=110), autofit=False)
        s += textbox(ids, X0 - 150000, 3050000, 1000000, 500000,
                     para("행(튜플)", sz=1800, b=True, algn="ctr", color=RED, lnSpc=100), autofit=False)
        s += connector(ids, X0 + 730000, 3280000, X0 + 900000, 3280000, color=RED, lw=19050)
        s += textbox(ids, X0, 5000000, W0, 1600000,
            para("**한 행(튜플) = 임상시험 1건**입니다. 이 표의 차수(속성 수)는 5, 카디널리티(행 수)는 3입니다.", sz=2200, lnSpc=125) +
            para("분석을 시작할 때 “이 표의 한 행이 무엇인가”를 먼저 말로 확인하는 습관이 중요합니다.", sz=2200, lnSpc=125, color="1F3763") +
            para("실제 studies 테이블은 행이 **37,509개** 있습니다. (수업용 aact_mini 기준)", sz=2200, b=True, lnSpc=125, color="1F3763"))
        return s
    return free("속성과 튜플 — AACT로 보기", b, subtitle="행은 무엇이고 열은 무엇인가")


def atomic_violation_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("특성 ④ **원자성**: 한 칸에는 더 이상 쪼갤 수 없는 값 하나만 들어가야 합니다.", sz=2300, lnSpc=115))
        t1, h1 = table(ids, X0, 2100000, [1400000, 1700000, 2900000],
            [["환자ID", "환자명", "복용약"], ["P001", "김OO", "메트포민, 아스피린"], ["P002", "이OO", "리시노프릴"]],
            sz=1800, row_h=520000, algn="ctr")
        s += t1
        s += textbox(ids, X0, 2100000 + h1 + 150000, 6000000, 900000,
            para("한 칸에 약이 두 개 → 원자성 위반", sz=2000, b=True, color=RED, lnSpc=115) +
            para("“아스피린을 먹는 환자”를 세기 어렵고, 약이 늘면 칸을 계속 늘려야 합니다.", sz=1900, lnSpc=115, color=GRAY))
        s += arrow_right(ids, 6350000, 2700000, 600000, 700000)
        t2, h2 = table(ids, 7300000, 2100000, [1400000, 1700000, 2400000],
            [["환자ID", "환자명", "복용약"], ["P001", "김OO", "메트포민"], ["P001", "김OO", "아스피린"], ["P002", "이OO", "리시노프릴"]],
            sz=1800, row_h=520000, algn="ctr")
        s += t2
        s += textbox(ids, 7300000, 2100000 + h2 + 150000, 5800000, 900000,
            para("약 하나당 한 행으로 나눔 → 원자성 지킴", sz=2000, b=True, color="2C5F2D", lnSpc=115) +
            para("이렇게 나누는 작업을 **제1정규화**라고 합니다 (6주차).", sz=1900, lnSpc=115, color=GRAY))
        s += textbox(ids, X0, 5900000, W0, 700000,
            para("실제 병원 데이터에서 “약품명, 진단명을 쉼표로 이어 붙인 칸”은 아주 흔한 문제입니다. 12주차에서 다시 봅니다.",
                 sz=2300, b=True, algn="ctr", lnSpc=115))
        return s
    return free("테이블의 특성 — 원자성 위반 예", b, subtitle="한 칸에 값이 여러 개면 무엇이 곤란할까")


def hospital_keys_slide():
    def b(ids):
        s = ""
        t1, h1 = table(ids, X0, 1600000, [1500000, 1800000, 2300000, 1800000],
            [["환자ID", "환자명", "주민번호", "연락처"],
             ["P001", "김OO", "480315-1******", "010-1111-2222"],
             ["P002", "이OO", "660722-2******", "010-3333-4444"]],
            sz=1800, row_h=480000, algn="ctr")
        s += t1
        s += textbox(ids, X0, 1600000 + h1 + 60000, 7000000, 330000,
                     para("<환자> 테이블", sz=1900, b=True, color=GRAY, lnSpc=100), autofit=False)
        t2, h2 = table(ids, X0, 3500000, [1500000, 1500000, 1800000, 2600000],
            [["진료ID", "환자ID", "진료일", "진단명"],
             ["V1001", "P001", "2026-03-11", "제2형 당뇨병"],
             ["V1002", "P001", "2026-04-02", "고혈압"],
             ["V1003", "P002", "2026-04-02", "천식"]],
            sz=1800, row_h=480000, algn="ctr")
        s += t2
        s += textbox(ids, X0, 3500000 + h2 + 60000, 7000000, 330000,
                     para("<진료> 테이블", sz=1900, b=True, color=GRAY, lnSpc=100), autofit=False)
        s += textbox(ids, 8400000, 1600000, 4700000, 4300000,
            para("**환자 테이블**", sz=2200, lnSpc=125) +
            para("후보키: 환자ID, 주민번호", sz=1900, lvl=1, lnSpc=120) +
            para("기본키: **환자ID**", sz=1900, lvl=1, lnSpc=120) +
            para("대체키: 주민번호 (개인정보)", sz=1900, lvl=1, lnSpc=120) +
            para("**진료 테이블**", sz=2200, lnSpc=125, spcBef=16) +
            para("기본키: **진료ID**", sz=1900, lvl=1, lnSpc=120) +
            para("외래키: **환자ID**", sz=1900, lvl=1, lnSpc=120) +
            para("같은 환자가 여러 번 진료 → 1 : N", sz=1900, lvl=1, lnSpc=120), autofit=False)
        s += textbox(ids, X0, 6250000, W0, 600000,
            para("기본키는 **변하지 않고, 비어 있지 않고, 중복되지 않는** 열로 고릅니다.", sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("병원 테이블에서 키 찾기", b, subtitle="환자 · 진료 테이블로 연습")


def integrity_violation_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("규칙을 어기면 DBMS가 **입력 자체를 거부**합니다. 그래서 잘못된 데이터가 쌓이지 않습니다.", sz=2200, lnSpc=115))
        rows = [["개체 무결성", "기본키는 비어 있거나\n중복될 수 없다", "환자ID 없이 환자 등록\n이미 있는 환자ID로 다시 등록", "INSERT 거부"],
                ["참조 무결성", "외래키는 참조하는 테이블에\n있는 값이어야 한다", "환자 테이블에 없는 P999로\n진료 기록 입력", "INSERT 거부"],
                ["도메인 무결성", "값은 정해진 타입과 범위\n안에 있어야 한다", "나이 칸에 ‘스물셋’\n수축기혈압에 -20", "타입 오류 · CHECK 위반"]]
        t, h = table(ids, X0, 2150000, [2300000, 3400000, 4400000, 2400000],
                     [["종류", "규칙", "어기는 예 (병원)", "결과"]] + rows,
                     sz=1900, row_h=1000000, header_h=520000, col_algn=["ctr", "l", "l", "ctr"])
        s += t
        s += textbox(ids, X0, 2150000 + h + 350000, W0, 900000,
            para("참조 무결성 때문에 **환자를 지우면 그 환자의 진료 기록은 어떻게 될까요?**", sz=2300, b=True, lnSpc=120) +
            para("보통은 삭제를 막거나(RESTRICT), 함께 지우거나(CASCADE) 규칙을 정해 둡니다. 10주차 삭제에서 다시 봅니다.",
                 sz=2100, lnSpc=120, color="1F3763"))
        return s
    return free("무결성 제약조건 3가지", b, subtitle="잘못된 값이 들어오지 못하게 막는 규칙")


def datatype_slide():
    return table_slide("데이터 타입", "열마다 어떤 값이 들어갈 수 있는지 정합니다",
        ["타입", "무엇을 담나", "예", "할 수 있는 일"],
        [["CHAR(n)", "길이가 고정된 문자", "'P001'", "비교 · 정렬 (계산 불가)"],
         ["VARCHAR(n)", "길이가 변하는 문자", "'김OO', 'PHASE3'", "비교 · 정렬 · 일부 검색"],
         ["INTEGER", "정수", "1062", "합계 · 평균 · 크기 비교"],
         ["NUMERIC / DECIMAL", "소수점 있는 수", "36.5, 127.4", "합계 · 평균 (반올림 정확)"],
         ["DATE", "날짜", "2026-03-11", "기간 계산 · 크기 비교"],
         ["TIMESTAMP", "날짜 + 시간", "2026-03-11 09:20", "시간 차이 계산"],
         ["BOOLEAN", "참 / 거짓", "true, false", "조건 판단"]],
        [2700000, 2700000, 3200000, 3900000], sz=1800, row_h=480000, y=1600000,
        col_algn=["l", "l", "l", "l"], col_font={0: "Courier New", 2: "Courier New"},
        note="타입을 잘못 정하면 계산이 막히거나 정렬이 이상해집니다. 다음 슬라이드에서 실제 예를 봅니다.",
        note_style="footnote")


def datatype_problem_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("AACT에는 “숫자처럼 보이지만 문자인 열”이 있습니다.", sz=2300, lnSpc=115))
        t, h = table(ids, X0, 2100000, [3600000, 2000000, 2600000, 4300000],
            [["열", "타입", "값의 예", "생기는 문제"],
             ["eligibilities.minimum_age", "VARCHAR", "'18 Years'", "18 이상 조건을 크기로 비교할 수 없음"],
             ["studies.phase", "VARCHAR", "'PHASE2/PHASE3'", "‘2상’으로 셀 때 어디에 넣을지 애매"],
             ["studies.enrollment", "INTEGER", "188,814,085", "입력 오류가 평균을 크게 왜곡"],
             ["studies.start_date", "DATE", "2020-02-21", "(정상) 기간 계산 가능"]],
            sz=1800, row_h=620000, header_h=500000, col_algn=["l", "ctr", "l", "l"],
            col_font={0: "Courier New", 2: "Courier New"})
        s += t
        y = 2100000 + h + 300000
        s += panel(ids, X0, y, 6000000, 1900000, "문자라서 생기는 일", [
            "'18 Years' > '8 Years' → 거짓",
            "- 글자 순서로 비교하기 때문",
            "- 나이 조건을 걸 수 없음"], fill="FBE5E5", line="C00000")
        s += panel(ids, 7300000, y, 6000000, 1900000, "그래서 AACT가 준비해 둔 열", [
            "minimum_age_num = 18 (INTEGER)",
            "- 숫자라서 크기 비교 가능",
            "- 단위는 minimum_age_unit 열에 따로 들어 있음"], fill="E2EFDA", line="2C5F2D", sz=1800)
        return s
    return free("데이터 타입 — 실제로 생기는 문제", b, subtitle="타입이 다르면 할 수 있는 계산이 다릅니다")


def null_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 600000,
            para("NULL은 **값이 없다 · 모른다 · 해당 없다**는 표시입니다. 0이나 빈칸(' ')과 다릅니다.", sz=2400, b=True, lnSpc=120))
        t, h = table(ids, X0, 2100000, [2600000, 3000000, 3400000, 3500000],
            [["검사결과 칸", "뜻", "평균을 내면", "병원에서는"],
             ["0", "검사해서 0이 나옴", "0이 포함되어 평균이 내려감", "실제 측정값"],
             ["NULL", "검사를 안 했거나 결과가 없음", "계산에서 **빠짐**", "미검사 · 기록 누락"],
             ["' ' (빈 문자)", "빈 글자가 들어 있음", "숫자가 아니라 오류", "잘못 입력된 값"]],
            sz=1900, row_h=620000, header_h=500000, col_algn=["ctr", "l", "l", "l"])
        s += t
        y = 2100000 + h + 350000
        s += panel(ids, X0, y, 6000000, 1900000, "NULL 확인은 IS NULL 로", [
            "WHERE 결과 = NULL   → 항상 거짓 (0행)",
            "WHERE 결과 IS NULL  → 올바름",
            "- NULL 은 ‘같다/다르다’로 비교할 수 없음"], fill="FFF2CC", line="BF9000", sz=1800)
        s += panel(ids, 7300000, y, 6000000, 1900000, "집계에서 NULL 은 빠집니다", [
            "COUNT(*) = 모든 행",
            "COUNT(결과) = 결과가 있는 행만",
            "- AVG, SUM 도 NULL 은 제외하고 계산"], fill="DEEAF6", line="1F497D", sz=1800)
        return s
    return free("NULL — 값이 없다는 표시", b, subtitle="0과 NULL은 다릅니다")



def relation_link_slide():
    """왜 ‘관계형’인가 — 표와 표를 잇는 부분. 5주차 1번 구간이 표 이야기만으로 끝나지 않게."""
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("표를 따로 두고 **필요할 때 이어서** 보기 때문에 ‘관계형’이라고 부릅니다.", sz=2300, lnSpc=115))
        y0, ew, gap = 2150000, 2700000, 900000
        e1, h1 = entity_box(ids, X0 + 900000, y0, ew, "환자",
                            ["환자ID", "환자명", "생년월일"], sz=1600, head_h=360000, row_h=290000)
        e2, h2 = entity_box(ids, X0 + 900000 + ew + gap, y0, ew, "진료",
                            ["진료ID", "환자ID", "진료일", "진단명"], sz=1600, head_h=360000, row_h=290000)
        s += e1 + e2
        mid = y0 + h1 // 2
        s += label_line(ids, X0 + 900000 + ew, mid, X0 + 900000 + ew + gap, mid, label="1 : N", sz=1700)
        s += textbox(ids, 8600000, y0, 4400000, 2000000,
            para("**한 표에 다 넣지 않는 이유**", sz=2200, lnSpc=125) +
            para("환자 정보를 진료 건마다 반복해 적지 않아도 됨", sz=1900, lvl=1, lnSpc=120) +
            para("환자명이 바뀌면 환자 표 한 곳만 고치면 됨", sz=1900, lvl=1, lnSpc=120) +
            para("진료 기록이 없는 환자도 등록할 수 있음", sz=1900, lvl=1, lnSpc=120), autofit=False)
        s += textbox(ids, X0, 4600000, W0, 900000,
            para("두 표를 잇는 열이 **외래키**입니다 (오늘 3번에서). 실제로 이어 붙이는 명령이 **JOIN** 입니다 (8주차).",
                 sz=2200, lnSpc=125, color="1F3763") +
            para("환자 한 명에 진료가 여러 건이므로 **1 : N** 관계입니다. 관계를 그리는 법은 6주차에서 봅니다.",
                 sz=2200, lnSpc=125, color="1F3763"))
        s += textbox(ids, X0, 6250000, W0, 500000,
            para("표를 나누어 두고 필요할 때 잇는 것 — 이것이 관계형 데이터베이스의 핵심입니다.",
                 sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("표와 표를 잇는 것이 ‘관계형’입니다", b, subtitle="표 하나로 끝나지 않습니다")


def pk_choice_slide():
    return table_slide("기본키를 무엇으로 고를까", "병원에서 실제로 따져 보는 네 가지",
        ["후보", "변하지 않는가", "비어 있지 않은가", "중복되지 않는가", "개인정보가 아닌가"],
        [["환자번호(원내 부여)", "○", "○", "○", "○"],
         ["주민등록번호", "○", "△ (외국인 등)", "○", "✕ 민감정보"],
         ["이름 + 생년월일", "△ (개명)", "○", "✕ 동명이인", "✕"],
         ["휴대전화번호", "✕", "△", "△", "✕"]],
        [3400000, 2000000, 2300000, 2200000, 2400000], sz=1800, row_h=560000, y=1750000,
        col_algn=["l", "ctr", "ctr", "ctr", "ctr"],
        note="그래서 병원은 대부분 **원내 환자번호**를 기본키로 씁니다. 주민번호는 대체키로 두거나 아예 보관하지 않습니다.")


def constraint_ddl_slide():
    return sql_example("제약조건을 실제로 걸어 보기", "지금까지 배운 규칙을 표 만들 때 적어 둡니다",
        "환자 표를 만들면서 규칙도 같이 걸어 주세요",
        ["CREATE TABLE 환자 (",
         "  환자ID   CHAR(8)     PRIMARY KEY,",
         "  환자명   VARCHAR(20) NOT NULL,",
         "  생년월일 DATE        NOT NULL,",
         "  성별     CHAR(1)     CHECK (성별 IN ('M','F')),",
         "  연락처   VARCHAR(20) UNIQUE",
         ");"],
        sz=1600, request_label="요청",
        note="PRIMARY KEY = 개체 무결성, CHECK = 도메인 무결성, 다른 표를 가리키는 FOREIGN KEY = 참조 무결성입니다.\n규칙을 표에 적어 두면 잘못된 값이 애초에 들어오지 못합니다. (3주차 CREATE TABLE)")


def null_rules_slide():
    return table_slide("NULL을 만나면 생기는 세 가지", "빈 값은 보통 값처럼 다뤄지지 않습니다",
        ["무엇을 할 때", "NULL은 어떻게 되나", "그래서 이렇게 씁니다"],
        [["비교할 때", "나이 = NULL 은 참도 거짓도 아님 → 한 행도 안 나옴", "나이 IS NULL / IS NOT NULL"],
         ["계산할 때", "NULL + 1 은 1이 아니라 NULL", "COALESCE(값, 0) 으로 채울지 먼저 정한다"],
         ["집계할 때", "AVG · SUM 은 NULL을 빼고 계산 → 분모가 조용히 줄어듦", "COUNT(*) 와 COUNT(열)을 같이 본다"]],
        [2400000, 5200000, 4200000], sz=1900, row_h=760000, y=1750000,
        col_algn=["ctr", "l", "l"],
        note="세 가지 모두 7 · 8주차 SQL에서 바로 만납니다. 지금은 “빈 값은 다르게 움직인다”만 기억하면 됩니다.")


def build(c):
    c.remove_tiny_pics(80, 150000)          # 'o' 를 그림으로 넣어 둔 것을 글자로 바꿉니다
    c.retitle(80, title="테이블의 구성요소", replacements=[
        ("<a:t>릴레이션(Relati</a:t>", "<a:t>릴레이션(Relation)</a:t>"), ("<a:t>n)</a:t>", "<a:t></a:t>"),
        ("<a:t>레코드(Rec</a:t>", "<a:t>레코드(Record)</a:t>"), ("<a:t>rd)</a:t>", "<a:t></a:t>"),
        ('<a:off x="9294129" y="1276957"/><a:ext cx="3089528" cy="252061"/>',
         '<a:off x="9294129" y="1276957"/><a:ext cx="3700000" cy="252061"/>'),
        ('<a:off x="9294129" y="5301248"/><a:ext cx="1537186" cy="252061"/>',
         '<a:off x="9294129" y="5301248"/><a:ext cx="1900000" cy="252061"/>')])
    c.retitle(81, title="테이블이 지켜야 할 5가지")
    c.retitle(82, title="키(Key)란 무엇인가")
    c.add_subtitle(82, "행 하나를 정확히 찾아내는 열")
    c.remove_shapes_below(82, 2350000)        # 옛 'Key의 종류' 상자 제거
    c.append_shapes(82, _key_preview)
    c.retitle(83, title="후보키 (Candidate Key)")
    c.add_subtitle(83, "행을 유일하게 구분할 수 있는 열(들)")
    c.add_subtitle(84, "후보키 중 대표로 고른 하나", w=4500000)
    c.retitle(84, title="기본키 (Primary Key)", replacements=[
        ("<a:t>‘학번’은 또는</a:t>", "<a:t>‘학번’ 또는</a:t>"),
        ("<a:t>값</a:t>", "<a:t>값들은</a:t>"), ("<a:t>들은</a:t>", "<a:t></a:t>")])
    c.add_subtitle(85, "기본키로 뽑히지 않은 나머지, 그리고 넓게 잡은 키")
    c.retitle(85, title="대체키와 슈퍼키", replacements=[
        ("만족하시만", "만족하지만"),
        ("최소성은 만족시키지 못하는 키", "최소성은 따지지 않는 키")])
    c.retitle(86, title="외래키 (Foreign Key)")
    c.add_subtitle(86, "다른 표의 기본키를 가리키는 열")
    c.append_shapes(86, lambda ids: textbox(ids, X0, 6350000, W0, 500000,
        para("외래키는 **8주차 JOIN에서 두 표를 잇는 열**이 됩니다.", sz=2300, b=True, algn="ctr", lnSpc=115)))
    c.retitle(87, title="키의 포함 관계", subtitle_contains="슈퍼키", new_subtitle="슈퍼키 ⊃ 후보키 ⊃ 기본키")
    c.append_shapes(87, lambda ids: textbox(ids, 948807, Y_SUB, 12000000, 354344,
        para("슈퍼키 ⊃ 후보키 ⊃ 기본키", sz=2200, b=True, color=GREEN, lnSpc=100), autofit=False)
        + textbox(ids, X0, 6250000, W0, 600000,
        para("기본키는 후보키 중 하나이고, 후보키는 모두 슈퍼키입니다.", sz=2400, b=True, algn="ctr", lnSpc=115)))

    # --- 도입
    c.add(cover(5, "관계형 데이터베이스",
                ["테이블 · 속성 · 튜플", "후보키 · 기본키 · 외래키", "무결성 · 데이터 타입 · NULL"],
                "2026. 10. 13."))
    c.add(content("지난시간 리뷰", [
        ("**데이터베이스 시스템** = DB + DBMS + 스키마 + 사용자 + 언어", dict(lvl=1, marL=457200, indent=-457200)),
        ("**스키마** = 틀,  **인스턴스** = 지금 들어 있는 값", dict(lvl=1, marL=457200, indent=-457200)),
        ("**3단계 스키마** = 외부(화면) · 개념(전체 설계도) · 내부(저장 방법)", dict(lvl=1, marL=457200, indent=-457200)),
        ("**사상**이 세 단계를 이어 주기 때문에 **데이터 독립성**이 생김", dict(lvl=1, marL=457200, indent=-457200)),
        ("**데이터 사전** = 테이블 · 열 · 타입 · 키를 설명하는 정보", dict(lvl=1, marL=457200, indent=-457200)),
        ("오늘은 그 중 **개념 스키마**를 실제로 어떻게 만드는지 봅니다.", dict(b=True, algn="ctr", color=BLUE, spcBef=24)),
    ]))
    c.add(objectives_slide(5,
        ["관계형 데이터베이스의 용어(테이블 · 속성 · 튜플)를 말할 수 있다",
         "어떤 열을 기본키로 골라야 하는지 판단할 수 있다",
         "외래키와 참조 무결성이 무엇을 막아 주는지 설명할 수 있다",
         "데이터 타입과 NULL 때문에 생기는 문제를 알아볼 수 있다"],
        AGENDA, subtitle="데이터를 표로 저장할 때 지켜야 하는 것들",
        date_note="오늘 배우는 키와 무결성은 8주차 JOIN, 12주차 오류 점검의 바탕이 됩니다"))

    # --- 1. 관계형 데이터베이스
    c.add(section_slide(1, AGENDA, lead="데이터를 왜 하필 ‘표’로 저장할까요?"))
    c.add(two_panel_slide("왜 표(table)로 저장하는가", "엑셀과 무엇이 다를까요",
        "같은 환자 명단을 엑셀과 관계형 데이터베이스에 각각 넣었다고 해 봅시다.",
        ("엑셀 파일", ["누구나 아무 칸에나 입력 가능",
                     "- 나이 칸에 ‘스물셋’을 넣어도 막지 않음",
                     "- 같은 환자를 두 번 넣어도 모름",
                     "- 파일이 여러 개로 복사되어 값이 서로 달라짐",
                     "- 여러 명이 동시에 고치기 어려움"], *RED_PANEL),
        ("관계형 데이터베이스", ["열마다 **타입과 규칙**이 정해져 있음",
                            "- 나이 칸에는 숫자만 들어감",
                            "- 기본키로 중복 등록을 막음",
                            "- 한 곳에 모아 두고 여러 명이 동시에 사용",
                            "- 표와 표를 **관계**로 연결"], *GREEN_PANEL),
        note=["**관계형 데이터베이스** = 데이터를 표(테이블)로 저장하고, 표와 표를 관계로 연결하는 방식",
              "1970년 코드(Codd) 박사가 제안한 뒤 지금까지 가장 널리 쓰입니다. (2주차 발전과정 복습)"],
        y=2300000, h=2900000))
    c.add(terms_table_slide())
    c.add(relation_link_slide())

    # --- 2. 테이블의 구성과 특성
    c.add(section_slide(2, AGENDA, lead="표 하나를 제대로 들여다봅니다"))
    c.keep(80)
    c.add(aact_rows_cols_slide())
    c.keep(81)
    c.add(atomic_violation_slide())
    c.add(checkpoint_slide(
        ["**테이블** = 행(튜플)과 열(속성)로 이루어진 표",
         "한 행이 무엇을 뜻하는지 먼저 말로 확인한다",
         "한 칸에는 **값 하나만** (원자성), 같은 행이 **중복되지 않게**"],
        question="한 환자에게 주민번호와 환자ID가 둘 다 있습니다. 무엇을 기본키로 할까요?",
        answer="둘 다 후보키입니다. 개인정보인 주민번호 대신 환자ID를 기본키로 쓰고, 주민번호는 대체키가 됩니다."))

    # --- 3. 키
    c.add(section_slide(3, AGENDA, lead="수많은 행 중에서 하나를 정확히 찾아내는 방법"))
    c.keep(82)
    c.keep(83)
    c.keep(84)
    c.keep(85)
    c.keep(86)
    c.keep(87)
    c.add(hospital_keys_slide())
    c.add(pk_choice_slide())
    c.add(sql_example("AACT에서 기본키 확인하기", "정말 중복이 없는지 SQL로 확인할 수 있습니다",
        "studies의 nct_id가 기본키가 맞는지 확인해 줘",
        ["SELECT COUNT(*) AS 행수,", "       COUNT(DISTINCT nct_id) AS 등록번호수", "FROM studies;"],
        result=[["행수", "등록번호수"], ["37509", "37509"]], result_w=[3000000, 3000000],
        sz=2000, request_label="확인하고 싶은 것",
        note="두 값이 같으면 중복이 없다는 뜻입니다. COUNT · DISTINCT · AS 는 8주차에 배웁니다. 지금은 “세어 본다”는 뜻만 알면 됩니다."))
    c.add(quiz("키(Key)", "다음 중 기본키(Primary Key)로 가장 적절한 것은?",
               ["환자명 — 같은 이름의 환자가 있을 수 있다", "환자ID — 병원이 부여하고 중복되지 않는다",
                "연락처 — 바뀔 수 있고 비어 있을 수 있다", "진단명 — 여러 환자가 같은 값을 가진다"],
               answer=1, note="기본키는 유일하고, 비어 있지 않고, 잘 바뀌지 않는 값이어야 합니다."))

    # --- 4. 무결성
    c.add(section_slide(4, AGENDA, lead="데이터가 처음부터 잘못 들어오지 않게 하는 규칙"))
    c.add(integrity_violation_slide())
    c.add(constraint_ddl_slide())
    c.add(two_panel_slide("참조 무결성이 지켜 주는 것", "외래키가 없다면 어떤 일이 생길까요",
        "진료 기록에 환자 테이블에 없는 환자ID(P999)를 입력하려고 합니다.",
        ("규칙이 없다면", ["P999 진료 기록이 그대로 저장됨",
                       "- 나중에 환자 정보를 못 찾음 = 미아 데이터",
                       "- 환자별 통계에서 이 진료가 빠짐",
                       "- 원인을 찾기 어려움 (언제 들어왔는지 모름)"], *RED_PANEL),
        ("외래키가 있다면", ["INSERT 가 즉시 거부됨",
                        "- 오타를 그 자리에서 발견",
                        "- 두 테이블의 값이 항상 맞물림",
                        "- JOIN 했을 때 행이 사라지지 않음 (8주차)"], *GREEN_PANEL),
        note=["**참조 무결성** = 외래키 값은 반드시 참조하는 테이블에 있어야 한다는 규칙",
              "실무에서는 속도 때문에 외래키를 걸지 않은 CDW도 있습니다. 그런 곳에서는 분석자가 직접 확인해야 합니다."],
        y=2300000, h=2700000))
    c.add(checkpoint_slide(
        ["**기본키** = 행 하나를 유일하게 찾아내는 열 (NULL 불가, 중복 불가)",
         "**외래키** = 다른 테이블의 기본키를 가리키는 열, 테이블을 연결",
         "**무결성 제약조건** = 개체 · 참조 · 도메인. 잘못된 값을 처음부터 막음"],
        question="진료 테이블의 환자ID는 어떤 키일까요?",
        answer="외래키입니다. 환자 테이블의 기본키(환자ID)를 가리킵니다."))

    # --- 5. 데이터 타입과 NULL
    c.add(section_slide(5, AGENDA, lead="칸 안에 들어가는 값의 종류"))
    c.add(datatype_slide())
    c.add(datatype_problem_slide())
    c.add(null_slide())
    c.add(null_rules_slide())
    c.add(quiz("무결성과 NULL", "다음 중 옳지 않은 설명은?",
               ["기본키에는 NULL을 넣을 수 없다", "NULL과 0은 같은 뜻이다",
                "외래키 값은 참조하는 테이블에 있어야 한다", "평균(AVG)을 구할 때 NULL인 행은 빠진다"],
               answer=1, note="NULL은 ‘값이 없다 · 모른다’는 표시이고, 0은 측정된 값입니다."))

    # --- 6. 정리
    c.add(section_slide(6, AGENDA, lead="오늘 나온 용어와 핵심을 다시 짚습니다"))
    c.add(terms_slide(5, [
        ["릴레이션 · 테이블", "Relation · Table", "행과 열로 이루어진 표"],
        ["튜플 · 행", "Tuple · Row", "표의 한 줄. 환자 한 명, 임상시험 한 건"],
        ["속성 · 열", "Attribute · Column", "기록하는 항목. 환자명, 나이"],
        ["도메인", "Domain", "그 열에 들어갈 수 있는 값의 범위"],
        ["후보키", "Candidate Key", "행을 유일하게 구분할 수 있는 열(들)"],
        ["기본키", "Primary Key", "후보키 중 대표로 고른 것. NULL · 중복 불가"],
        ["대체키", "Alternate Key", "기본키로 뽑히지 않은 나머지 후보키"],
        ["외래키", "Foreign Key", "다른 테이블의 기본키를 가리키는 열"],
        ["무결성 제약조건", "Integrity Constraint", "잘못된 값이 들어오지 못하게 막는 규칙"],
        ["NULL", "—", "값이 없거나 모른다는 표시. 0과 다름"],
    ]))
    c.add(summary(5, [
        "**관계형 데이터베이스** = 데이터를 표로 저장하고 관계로 연결",
        "**기본키**로 행 하나를 찾고, **외래키**로 표와 표를 잇는다",
        "**무결성 제약조건**과 **데이터 타입**이 잘못된 값을 처음부터 막아 준다",
    ], sz=2800, lnSpc=170, next_week="6강. 모델링과 정규화 — 표를 어떻게 나눌지 설계하는 방법"))
