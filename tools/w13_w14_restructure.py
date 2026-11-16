# -*- coding: utf-8 -*-
"""13 · 14강 개편 (2026-11-17, 강사 결정)

- 지금 13강 '의료 질 · 간호 지표 만들기'는 없앰. 「의료 질 지표 — 분자와 분모」 1장은 이미 12강으로 옮김 (A안).
  내용 18장은 지우고, 틀(표지 · 리뷰 · 학습 목표 · 구분 6 · 여기까지 정리 2 · 용어 정리 · 강의 정리)은 새 14강의 뼈대로 다시 씀.
- 지금 14강 '병원 데이터를 맞추는 법 — 표준과 품질' → 13강 (11/24). 지난시간 리뷰 = 12강, 과제 2 슬라이드 2장을 옮겨 옴,
  '같은 서랍' 절에 Epic 2장 (같은 서랍을 만드는 두 가지 길 · 미국 Epic).
- 새 14강 '빅데이터와 AI 시대의 DBMS' (12/1, 실습 없음, 깊지 않게): 병원 밖 데이터 · 디지털 바이오마커 → 데이터 레이크
  → 큰 데이터 다루기 → 표가 아닌 데이터 → API와 AI → 정리 (+ 기말고사 미리 안내를 옮겨 옴). 15강은 그 뒤.
- 15강: 지난시간 리뷰(14강) · 시험 범위 표 · 총복습 ④. 1강 강의 계획표 11~14주차 · 과제 2 줄.
숫자 · 사례는 웹에서 확인한 것 (출처는 슬라이드 아래 회색 줄). 사용: python3 tools/w13_w14_restructure.py <덱.pptx> <결과.pptx>
"""
import os, sys, re, copy
import duckdb
from w10_tx_more import fill
from w12_new import agenda, summary_slide, pair
from w14_easy import clone, blank, credit, X0, X1, BLUE_F, BLUE_L, GREEN_F, GREEN_L, RED_F, RED_L, YEL_F, YEL_L, GREY_F, B
from slidekit import (A, P, Deck, texts, shape, set_para, set_title, replace_text, table_fill, move_y, add_box, add_arrow,
                      set_fill, KW_SQL)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = duckdb.connect(os.path.join(ROOT, "data", "hospital_mini.duckdb"), read_only=True)
N_FALL, N_FALL_ADM = h.execute("SELECT COUNT(*), COUNT(DISTINCT 입원ID) FROM 낙상").fetchone()
assert (N_FALL, N_FALL_ADM) == (165, 136), (N_FALL, N_FALL_ADM)

TITLE13 = "13강. 병원 데이터를 맞추는 법 — 표준과 품질"
TITLE14 = "14강. 빅데이터와 AI 시대의 DBMS"
AG14 = [("병원 밖 데이터", "디지털 바이오마커"), ("데이터 레이크", "먼저 담고 나중에 정리"), ("큰 데이터 다루기", "열 저장 · 분산 · 클라우드"),
        ("표가 아닌 데이터", "NoSQL · FHIR"), ("API와 AI", "데이터를 나누고 쓰는 방법"), ("정리", "용어 · 기말고사 안내")]


def sp_with(t, text):
    m = [s for s in t.iter(P + "sp") if text in texts(s)]
    assert len(m) == 1, (text, len(m))
    return m[0]


def drop(t, name):
    s = shape(t, name)
    s.getparent().remove(s)


def mono(s):
    """코드 상자: 영문은 Courier New (한글은 맑은 고딕 그대로)"""
    for la in s.iter(A + "latin"):
        la.set("typeface", "Courier New")


def second_run(L, d, first, old, new):
    """오늘의 순서 칸 (런 2개 '제목' · '  설명') 중 설명이 old 인 것을 new 로. 바꾼 개수를 돌려줌"""
    n = 0
    for s in L:
        for p_ in d.tree(s).iter(A + "p"):
            rs = p_.findall(A + "r")
            if len(rs) == 2 and rs[0].findtext(A + "t") == first and rs[1].findtext(A + "t").strip() == old:
                t2 = rs[1].find(A + "t"); t2.text = t2.text[: len(t2.text) - len(t2.text.lstrip())] + new
                n += 1
    return n


def cell(t, r, c):
    return t.find(f".//{A}tbl").findall(A + "tr")[r].findall(A + "tc")[c]


def set_cell(t, r, c, text):
    rs = list(cell(t, r, c).iter(A + "r"))
    assert rs, (r, c)
    rs[0].find(A + "t").text = text
    for x in rs[1:]:
        x.getparent().remove(x)


def table_rows(t):
    return [["".join(x.text or "" for x in tc.iter(A + "t")) for tc in tr.findall(A + "tc")] for tr in t.find(f".//{A}tbl").findall(A + "tr")]


# ---------------------------------------------------------------- 새 슬라이드 (복제한 틀에 글 · 도형)
def tab_slide(d, tmpl, title, sub, header, rows, widths, bottom, sz=1500, row_h=None, note=None):
    t, rel = clone(d, tmpl)
    set_title(t, title); set_para(shape(t, "TextBox 4"), sub)
    y = table_fill(t, header, rows, widths=widths, sz=sz, head_sz=sz + 100, row_h=row_h)
    set_para(shape(t, "TextBox 6"), bottom)
    move_y(t, "TextBox 6", y + 200000)
    if note:
        credit(t, note, X0, y + 900000, X1 - X0)
    return t, rel


def two_slide(d, tmpl, title, sub, lead, left, right, bottom, colors=None):
    t, rel = clone(d, tmpl)
    set_title(t, title); set_para(shape(t, "TextBox 4"), sub); set_para(shape(t, "TextBox 5"), lead)
    for head, box, (h_txt, items) in (("Panel Head 7", "TextBox 8", left), ("Panel Head 10", "TextBox 11", right)):
        set_para(shape(t, head), h_txt)
        fill(shape(t, box), [(0, [x]) for x in items])
    fill(shape(t, "TextBox 12"), [(0, [x]) for x in bottom])
    if colors:
        (lf, ll), (rf, rl) = colors
        set_fill(shape(t, "Panel Head 7"), ll, ll); set_fill(shape(t, "Panel 6"), lf, ll)
        set_fill(shape(t, "Panel Head 10"), rl, rl); set_fill(shape(t, "Panel 9"), rf, rl)
    return t, rel


def outside(t):
    """병원 밖에서 쌓이는 데이터: 병원 안 · 밖 세 칸씩 → 합치면 · 먼저 할 일"""
    hw = (X1 - X0 - 600000) // 2
    for k, (head, items, f, l) in enumerate((("병원 안", ["EMR · 진료기록 · 처방", "영상 · 검사 결과", "간호기록 · 원무 자료"], BLUE_F, BLUE_L),
                                             ("병원 밖", ["스마트워치 — 맥박 · 수면 · 심전도", "연속혈당측정기 · 가정 혈압계", "건강 앱 기록 · 유전체 검사"], GREEN_F, GREEN_L))):
        x = X0 + k * (hw + 600000)
        add_box(t, x, 1450000, hw, 550000, [head], fill=l, line=l, sz=1900, color="FFFFFF", bold=True, name="Head")
        for i, it in enumerate(items):
            add_box(t, x, 2100000 + i * 680000, hw, 580000, [it], fill=f, line=l, sz=1700, color="262626", name="Item")
        add_arrow(t, x + hw // 2 - 300000, 4200000, 600000, 400000, "down")
    add_box(t, X0, 4700000, X1 - X0, 750000, [[("합치면  ", B), ("진료와 진료 사이의 변화까지 볼 수 있습니다", {})]],
            fill=YEL_F, line=YEL_L, sz=1800, name="Result")
    add_box(t, X0, 5650000, X1 - X0, 750000,
            [[("먼저 할 일  ", {"b": True, "color": RED_L}), ("기기마다 정확도 · 형식이 다르고 환자 동의가 필요합니다 (13강 같은 말 · 같은 서식)", {})]],
            fill=GREY_F, line="BFBFBF", sz=1600, name="Caution")


def distributed(t):
    """나눠서 처리하기: 큰 데이터 → 컴퓨터 세 대 → 합치기, 분산 · 클라우드, 병원에서는"""
    add_box(t, X0, 1700000, 3000000, 1300000, [[("아주 큰 데이터", B)], [("예: 전국 청구 · 영상 자료", {"sz": 1400})]],
            fill=GREY_F, line="BFBFBF", sz=1800, name="Big")
    add_arrow(t, X0 + 3100000, 2150000, 600000, 400000)
    for i, txt in enumerate(["컴퓨터 1 — 1~4월 계산", "컴퓨터 2 — 5~8월 계산", "컴퓨터 3 — 9~12월 계산"]):
        add_box(t, X0 + 3800000, 1620000 + i * 520000, 3400000, 440000, [txt], fill=BLUE_F, line=BLUE_L, sz=1500, name="Node")
    add_arrow(t, X0 + 7300000, 2150000, 600000, 400000)
    add_box(t, X0 + 8000000, 1700000, X1 - X0 - 8000000, 1300000, [[("합치기", B)], [("월별 건수를 더해 1년 결과", {"sz": 1400})]],
            fill=YEL_F, line=YEL_L, sz=1800, name="Merge")
    hw = (X1 - X0 - 400000) // 2
    add_box(t, X0, 3450000, hw, 1650000, [[("분산 처리", {"b": True, "color": BLUE_L, "sz": 1900})], "여러 컴퓨터가 나눠 계산하고 결과를 합침",
                                          "예: Hadoop · Spark"], fill=BLUE_F, line=BLUE_L, sz=1600, name="Dist")
    add_box(t, X0 + hw + 400000, 3450000, hw, 1650000, [[("클라우드", {"b": True, "color": GREEN_L, "sz": 1900})],
                                                         "서버를 사 두지 않고 필요할 때 빌려 씀", "작게 시작해서 필요할 때 크게"],
            fill=GREEN_F, line=GREEN_L, sz=1600, name="Cloud")
    add_box(t, X0, 5400000, X1 - X0, 800000,
            [[("병원에서는  ", B), ("개인정보 때문에 데이터를 어디에 두는지(병원 안 · 밖)와 망 분리를 먼저 따집니다", {})]],
            fill=YEL_F, line=YEL_L, sz=1600, name="Note")


FHIR_JSON = ['{', '  "resourceType": "Observation",', '  "status": "final",', '  "code": {"text": "당화혈색소 (LOINC 4548-4)"},',
             '  "subject": {"reference": "Patient/0010019"},', '  "effectiveDateTime": "2024-03-05",',
             '  "valueQuantity": {"value": 7.2, "unit": "%"}', '}']


def fhir(t):
    code = add_box(t, X0, 1500000, 7000000, 3300000, FHIR_JSON, fill="F2F2F2", line="BFBFBF", sz=1600, color="262626",
                   align="l", anchor="t", geom="rect", name="Code")
    mono(code)
    add_box(t, X0 + 7300000, 1500000, X1 - X0 - 7300000, 3300000,
            [[("resourceType", B), ("  무엇에 대한 문서 (검사 결과)", {})], [("code", B), ("  어떤 검사 (표준 코드 LOINC)", {})],
             [("subject", B), ("  누구 (환자)", {})], [("value", B), ("  결과 값과 단위", {})]],
            fill=BLUE_F, line=BLUE_L, sz=1700, align="l", name="Explain")
    add_box(t, X0, 5100000, X1 - X0, 1200000, ["병원이 달라도 같은 모양의 문서로 주고받습니다.",
                                              "기업 · 앱이 쓰는 API도 대부분 이런 JSON 문서를 주고받습니다."],
            fill=YEL_F, line=YEL_L, sz=1700, name="Note")


def users(t):
    """병원 데이터를 쓰는 사람: 직원(EMR) → 연구자(CDW) → 기업 · 앱(API)"""
    w, g = 3600000, (X1 - X0 - 3 * 3600000) // 2
    cols = [("병원 직원", "EMR", "진료 기록을 쓰고 봄", "(11강 운영 DB)", BLUE_L),
            ("연구자", "CDW", "승인받아 가명 자료를 SQL로 분석", "(11 · 12강)", GREEN_L),
            ("기업 · 앱", "API", "정해진 항목만 프로그램이 꺼내 감", "(환자 동의 · 계약 범위 안에서)", "7030A0")]
    for k, (who, sysname, what, ref, col) in enumerate(cols):
        x = X0 + k * (w + g)
        add_box(t, x, 1600000, w, 600000, [who], fill=col, line=col, sz=1900, color="FFFFFF", bold=True, name="Who")
        add_box(t, x, 2300000, w, 650000, [sysname], fill="F2F2F2", line=col, sz=2200, color=col, bold=True, name="System")
        add_box(t, x, 3050000, w, 1450000, [what, [(ref, {"sz": 1400, "color": "7F7F7F"})]], fill="FFFFFF", line=col, sz=1600, name="What")
        if k < 2:
            add_arrow(t, x + w + (g - 500000) // 2, 2420000, 500000, 400000)
    add_box(t, X0, 4900000, X1 - X0, 1000000,
            [[("API  ", B), ("정해진 창구로 정해진 항목만 꺼내 주는 약속 — 뷰 · 권한(GRANT)과 같은 생각입니다 (3 · 4강)", {})]],
            fill=YEL_F, line=YEL_L, sz=1700, name="Note")


def main(src, out):
    d = Deck(src)
    S = d.slides
    c13, e13 = d.find("13강. 의료 질 · 간호 지표 만들기"), d.find("13주차 강의 정리")
    c14, e14 = d.find("14강. 병원 데이터를 맞추는 법 — 표준과 품질"), d.find("14주차 강의 정리")
    c15 = d.find("15강. 기말고사")
    L13, L14 = d.between(c13, e13), d.between(c14, e14)
    assert S().index(e13) + 1 == S().index(c14) and S().index(e14) + 1 == S().index(c15)
    F13 = lambda line, also=None: d.find(line, also, within=L13)
    F14 = lambda line, also=None: d.find(line, also, within=L14)

    # ---- 틀 (지우기 전에 찾아 둠)
    T_TAB, T_TWO, T_BLANK = d.find("의료 질 지표 — 분자와 분모"), F14("데이터 웨어하우스와 데이터 레이크"), F14("맞추는 세 가지 방법 — 같은 말 · 같은 서식 · 같은 서랍")
    T_PAIR = d.find("JOIN 함정 — 재원일수가 6배로")
    review13, goals13 = F13("지난시간 리뷰"), F13("13주차 학습 목표")
    divs13 = [F13(x) for x in ("1. 의료 질 지표", "2. 지표 정의서", "3. 30일 재입원율", "4. 간호 업무량", "5. 검산표와 해석", "6. 정리")]
    sums13 = [s for s in L13 if "여기까지 정리" in texts(d.tree(s))]
    assert len(sums13) == 3
    terms13 = F13("13주차 용어 정리")
    a2 = [F13("과제 2 제출 안내"), F13("과제 2를 할 때 자주 막히는 부분")]
    keep = {c13, review13, goals13, *divs13, sums13[0], sums13[1], terms13, e13, *a2}
    gone = [s for s in L13 if s not in keep]
    assert len(gone) == 18, len(gone)
    exam, lake = F14("기말고사 미리 안내"), T_TWO

    # ---- 새 14강 내용 슬라이드 (만들어서 일단 13강 표지 뒤에 넣고, 마지막에 순서대로 옮김)
    new = {}

    def put(key, t_rel):
        new[key] = d.insert_after(c13, *t_rel)

    t, rel = blank(d, T_BLANK, "병원 밖에서 쌓이는 데이터", "진료와 진료 사이의 자료까지")
    outside(t); put("out", (t, rel))
    put("dbm", tab_slide(d, T_TAB, "디지털 바이오마커 — 기기로 재는 건강 지표", "디지털 기기로 잰 객관적 · 정량적 건강 지표",
                         ["기기", "재는 것", "어디에 쓰나"],
                         [["스마트워치", "맥박 · 심전도 · 수면 · 걸음", "심방세동 의심 알림 (Apple Heart Study, 약 41만 명)"],
                          ["연속혈당측정기", "몇 분마다 혈당", "당뇨 환자의 혈당 변동 관리"],
                          ["스마트폰", "걸음 속도 · 움직임 · 말소리", "낙상 위험 · 우울 · 파킨슨병 연구"],
                          ["가정 혈압계 · 체중계", "혈압 · 체중", "고혈압 · 심부전 원격 관리"]],
                         [2600000, 3800000, 5400000], "진료실에서 가끔 재던 것을 생활 속에서 매일 잴 수 있게 되었습니다.", sz=1600,
                         row_h=560000, note="Apple Heart Study: NEJM 2019"))
    put("xmod", tab_slide(d, T_TAB, "이미 찍은 영상 · 신호에서 다른 검사를 읽는 AI", "크로스모달리티 — 다른 검사의 값을 AI로 추정",
                          ["이미 있는 자료", "AI가 추정하는 것", "원래 하던 검사", "근거"],
                          [["흉부 X-ray", "골밀도 · 골다공증", "골밀도 검사 (DXA)", "J Bone Miner Res 2021 · Radiology 2024"],
                           ["심전도", "심장 수축 기능 저하", "심장초음파", "Nat Med 2019 · 2023 FDA 허가"],
                           ["안저(망막) 사진", "나이 · 혈압 · 심혈관 위험", "혈압 측정 · 위험 점수", "Nat Biomed Eng 2018"],
                           ["복부 CT", "근육 · 내장지방 · 골밀도 → 심혈관 사건", "따로 하는 검사들", "Lancet Digit Health 2020"]],
                          [2200000, 3700000, 2500000, 3400000],
                          "AI 학습 = X-ray와 같은 시기의 DXA 결과를 환자번호 · 날짜로 잇기 (12강 JOIN)",
                          sz=1500, row_h=600000, note="한계: 오경보(특이도) · 집단에 따라 다른 성능 · 다른 병원에서의 검증"))
    put("swamp", tab_slide(d, T_TAB, "레이크가 늪이 되지 않으려면", "일단 다 담으면, 나중에 아무도 못 찾을 수 있습니다",
                           ["할 일", "내용"],
                           [["이름표 붙이기", "무슨 자료인지 · 언제 · 어디서 왔는지 적어 둠 (데이터 사전)"],
                            ["품질 점검", "빠진 값 · 이상한 값을 정기적으로 확인 (13강 품질)"],
                            ["권한 · 가명처리", "누가 무엇을 볼 수 있는지 정하고, 개인정보는 가림"],
                            ["자주 쓰는 것은 웨어하우스로", "많이 쓰는 자료는 정리해서 CDW · 데이터 마트로 옮김"]],
                           [3400000, 8400000], "정리 없이 쌓기만 한 레이크를 ‘데이터 늪(swamp)’이라고 부릅니다.", sz=1600, row_h=600000))
    put("rowcol", two_slide(d, T_TWO, "행으로 저장, 열로 저장", "같은 표도 쓰임에 따라 저장 방식이 다릅니다",
                            "디스크에 적는 순서가 다를 뿐, SQL은 똑같이 씁니다.",
                            ("행 저장 — 운영 DB (EMR)", ["환자 한 명의 기록을 한 줄로 붙여 저장", "한 사람의 기록을 한꺼번에 읽고 쓰기 좋음",
                                                      "진료 화면 · 처방 입력에 알맞음", "많은 행의 한 열만 볼 때는 느림"]),
                            ("열 저장 — 분석 DB (CDW)", ["같은 열의 값끼리 모아 저장", "한 열을 많이 읽는 집계에 빠름 (예: 재원일수 평균)",
                                                      "한 사람 기록을 고칠 때는 불편", "예: 수업에서 쓴 DuckDB"]),
                            ["11강에서 EMR과 CDW를 따로 두는 이유 중 하나입니다.", "데이터가 커질수록 저장 방식이 속도를 크게 바꿉니다."]))
    t, rel = blank(d, T_BLANK, "나눠서 처리하기 — 분산과 클라우드", "한 대로 안 되면 여러 대가 나눠서")
    distributed(t); put("dist", (t, rel))
    put("nosql", tab_slide(d, T_TAB, "표가 아닌 데이터 — NoSQL", "표에 담기 어려운 자료를 위한 데이터베이스",
                           ["종류", "담는 모양", "병원 예"],
                           [["문서형", "한 건을 통째로 JSON 문서로", "진료 기록 한 건 · FHIR 자료"],
                            ["키-값", "이름표 하나에 값 하나", "로그인 정보 · 화면 설정 · 임시 저장"],
                            ["그래프", "점과 선 (관계)", "약 · 질환 · 환자의 관계, 약물 상호작용"],
                            ["시계열", "시간 순서대로 쌓이는 값", "생체신호 · 웨어러블 · 장비 기록"]],
                           [2000000, 3800000, 6000000],
                           "NoSQL은 SQL을 대신하지 않습니다. 표에 담기 어려운 자료를 함께 담는 도구입니다.", sz=1600, row_h=560000))
    t, rel = blank(d, T_BLANK, "FHIR — 진료 정보를 JSON 문서로", "13강 ‘같은 서식’ — 병원이 달라도 같은 모양의 문서")
    fhir(t); put("fhir", (t, rel))
    t, rel = blank(d, T_BLANK, "병원 데이터를 쓰는 사람이 넓어진다", "직원 → 연구자 → 기업 · 앱")
    users(t); put("users", (t, rel))
    put("api", two_slide(d, T_TWO, "API로 나눌 때 — 장점과 걱정", "같은 데이터가 더 많은 곳에서 쓰입니다",
                         "보건 분야에서는 두 쪽을 함께 봐야 합니다.",
                         ("장점", ["신약 · AI 진단 기기 개발이 빨라짐", "환자가 앱으로 내 기록을 모아 봄", "여러 기관 자료로 더 큰 연구",
                                   "중복 검사 · 서류가 줄어듦"]),
                         ("걱정", ["다시 누구인지 알아낼 위험 (재식별)", "환자가 모르는 사이에 쓰일 수 있음 (동의)",
                                   "기업의 이익으로만 쓰일 수 있음", "해킹 · 유출 사고"]),
                         ["지킬 것: 가명처리 · 꼭 필요한 항목만 · 누가 무엇을 꺼내 갔는지 기록 (13강 가명정보)"],
                         colors=((GREEN_F, GREEN_L), (RED_F, RED_L))))
    t, rel = clone(d, T_PAIR)
    pair(t, "AI가 만든 SQL도 검산합니다", "‘낙상이 있었던 입원은 몇 건?’을 AI에게 물었더니 SQL을 만들어 주었습니다.",
         ["SELECT COUNT(*) AS 입원건수", "FROM 낙상;"], f"{N_FALL}", "낙상 행을 셌습니다. 한 입원에서 두 번 넘어지면 2건이 됩니다.",
         ["SELECT COUNT(DISTINCT 입원ID)", "       AS 입원건수", "FROM 낙상;"], f"{N_FALL_ADM}", "입원 단위로 셉니다.",
         "AI가 만든 SQL도 세는 단위 · 조건을 확인하고 검산합니다 (9강 검산 · 12강).")
    set_para(shape(t, "BadHead 5"), "AI가 만든 SQL"); set_para(shape(t, "GoodHead 9"), "검산하고 고친 SQL")
    put("aisql", (t, rel))

    # ---- Epic 2장 (13강 '같은 서랍', OMOP CDM 주요 테이블 뒤)
    omop = F14("OMOP CDM 주요 테이블")
    t, rel = two_slide(d, T_TWO, "같은 서랍을 만드는 두 가지 길", "처음부터 같게 쓰거나, 나중에 맞추거나",
                       "여러 병원 자료를 같은 서랍에 넣는 길은 두 가지입니다.",
                       ("처음부터 같은 EMR — 예: 미국 Epic", ["여러 병원이 같은 회사의 EMR을 씀", "표 구조 · 코드 · 화면이 비슷함",
                                                       "병원끼리 주고받기 · 모으기가 쉬움", "회사 하나에 기대게 됨 (비용 · 바꾸기 어려움)"]),
                       ("나중에 공통 모델로 — 예: OMOP CDM", ["병원마다 EMR은 그대로 씀", "CDW 자료를 공통 서랍으로 옮겨 담음 (매핑)",
                                                       "어느 EMR을 쓰든 참여할 수 있음", "옮겨 담는 데 품이 들고 빠지는 자료가 생김"]),
                       ["한국 대형병원은 대부분 자체 EMR을 써서, 두 번째 길(표준 코드 · 공통 모델)이 더 중요합니다."],
                       colors=((BLUE_F, BLUE_L), (GREEN_F, GREEN_L)))
    ep1 = d.insert_after(omop, t, rel)
    t, rel = tab_slide(d, T_TAB, "미국 Epic — 같은 EMR을 쓰는 병원들", "한 회사의 EMR이 사실상의 표준이 된 예", ["항목", "내용"],
                       [["얼마나 쓰나", "미국 급성기 병원의 43.7% (병상 기준 56.9%) — 2025년 기준"],
                        ["주고받기", "Epic 병원끼리 진료 기록 교환 (Care Everywhere), 2023년 국가 교환망(TEFCA)에도 연결"],
                        ["모아서 연구", "Cosmos — 약 3억 명의 가명 기록을 모은 연구용 DB"],
                        ["DB 구조", "운영 DB → 밤마다 → 분석 DB(SQL) → 웨어하우스 — 11강의 EMR → CDW와 같음"],
                        ["한계", "병원마다 설정이 달라 데이터가 완전히 같지는 않음 · 회사 하나에 기댐"]],
                       [2400000, 9400000], "같은 EMR을 써도 표준 코드와 품질 점검은 여전히 필요합니다.", sz=1600, row_h=600000,
                       note="출처: KLAS US Acute Care EHR Market Share 2026 (2025년 기준) · Epic · ONC (2023)")
    d.insert_after(ep1, t, rel)

    # ---- 13강 (지금 14강): 번호 · 날짜 · 리뷰 · 과제 2 · 순서 6번
    t = d.tree(c14)
    replace_text(t, "14강. 병원 데이터를 맞추는 법 — 표준과 품질", TITLE13); replace_text(t, "2026. 12. 1.", "2026. 11. 24.")
    goals14 = F14("14주차 학습 목표")
    t = d.tree(goals14); set_title(t, "13주차 학습 목표")
    set_para(shape(t, "TextBox 20"), "과제 2(20점) 제출 기한은 2026-12-08(화)입니다")
    set_title(d.tree(F14("14주차 용어 정리")), "13주차 용어 정리")
    set_title(d.tree(e14), "13주차 강의 정리")
    t = d.tree(F14("지난시간 리뷰"))
    fill(shape(t, "TextBox 4"), [(1, ["입원 건수와 환자 수", "는 다르다 — 세는 단위와 날짜 기준"]),
                                 (1, ["재원일수 · 수술시간", "은 날짜 · 시각을 빼서 구한다"]),
                                 (0, ["지표 = ", "분자 ÷ 분모", " (예: 낙상률 = 낙상 건수 ÷ 재원일수 × 1,000)"]),
                                 (3, ["지금까지는 ", "우리 병원 한 곳", "의 데이터를 다뤘습니다."]),
                                 (4, ["오늘은 여러 병원의 데이터를 맞추는 법을 봅니다."])])
    assert second_run(L14, d, "정리", "용어와 요약", "용어 · 과제 2 제출") == 7          # 학습 목표 1 + 구분 6
    set_para(shape(d.tree(F14("6. 정리")), "TextBox 4"), "용어 · 과제 2 제출")
    for s in a2:                                                            # 과제 2 두 장: 13주차 강의 정리 바로 앞
        d.lst.remove(s); e14.addprevious(s)

    # ---- 새 14강 (지금 13강의 틀)
    t = d.tree(c13)
    fill(sp_with(t, "지표 정의서 — 분모 · 분자 · 기준일"), [(0, ["병원 밖 데이터와 디지털 바이오마커"]), (1, ["데이터 레이크와 큰 데이터"]),
                                                     (2, ["API와 AI 시대의 데이터베이스"])])
    replace_text(t, "13강. 의료 질 · 간호 지표 만들기", TITLE14); replace_text(t, "2026. 11. 24.", "2026. 12. 1.")
    t = d.tree(review13)
    fill(shape(t, "TextBox 4"), [(1, ["병원마다 다르게 적는 기록", "을 같은 말 · 같은 서식 · 같은 서랍으로 맞춘다"]),
                                 (1, ["같은 EMR(Epic)", "을 쓰거나 공통 모델(OMOP CDM)로 옮겨 담는다"]),
                                 (1, ["품질 점검 · 가명처리", " 뒤에 분석한다"]),
                                 (3, ["오늘은 병원 밖까지 넓어지는 데이터와, 그 데이터를 다루는 방법을 봅니다."])])
    t = d.tree(goals13)
    set_title(t, "14주차 학습 목표"); set_para(shape(t, "TextBox 4"), "병원 데이터가 커지고 넓어질 때")
    fill(shape(t, "TextBox 6"), [(0, ["① 디지털 바이오마커를 예로 든다"]), (1, ["② 데이터 레이크와 CDW의 차이를 말한다"]),
                                 (2, ["③ 큰 데이터를 저장 · 처리하는 방법을 안다"]), (3, ["④ API · AI로 데이터를 쓸 때 지킬 것을 안다"])])
    agenda(t, "Step", AG14, "  ")
    set_para(shape(t, "TextBox 20"), "다음 주는 기말고사입니다. 오늘 마지막에 시험 형식과 범위를 안내합니다")
    for k, s in enumerate(divs13):
        t = d.tree(s)
        set_title(t, f"{k + 1}. {AG14[k][0]}"); set_para(shape(t, "TextBox 4"), AG14[k][1]); agenda(t, "Sec", AG14, "   ")
    summary_slide(d.tree(sums13[0]), [("① ", "병원 밖 데이터", "(웨어러블 · 앱)도 진료 기록과 합친다"),
                                      ("② ", "디지털 바이오마커", " = 기기로 잰 지표, X-ray로 골밀도를 추정하기도"),
                                      ("③ ", "데이터 레이크", "는 먼저 담고 나중에 정리, CDW는 정리해 담음")],
                  ("잠깐 생각해 봅시다", "  스마트워치 심박 자료를 CDW에 바로 넣으면 될까요?",
                   "기기마다 정확도와 형식이 달라서, 같은 말 · 같은 서식(13강)과 품질 확인이 먼저입니다."))
    summary_slide(d.tree(sums13[1]), [("① ", "운영 DB는 행 저장", ", 분석 DB는 열 저장이 알맞다"),
                                      ("② ", "아주 큰 데이터", "는 여러 컴퓨터가 나눠 처리하고, 클라우드를 빌려 쓰기도"),
                                      ("③ ", "표가 아닌 데이터", "는 NoSQL에, 병원 사이 교환은 FHIR(JSON)로")],
                  ("잠깐 생각해 봅시다", "  NoSQL이 있으면 SQL은 필요 없을까요?",
                   "아닙니다. 대부분의 분석은 여전히 표와 SQL로 합니다. NoSQL은 표에 담기 어려운 자료를 함께 담는 도구입니다."))
    t = d.tree(terms13)
    set_title(t, "14주차 용어 정리")
    table_fill(t, ["용어", "영어", "뜻 (한 줄)"],
               [["디지털 바이오마커", "Digital Biomarker", "디지털 기기로 잰 객관적 건강 지표"],
                ["환자 생성 건강 데이터", "PGHD", "웨어러블 · 앱 등 병원 밖에서 환자가 만든 건강 데이터"],
                ["데이터 레이크", "Data Lake", "형태 그대로 먼저 담고 쓸 때 정리하는 저장소"],
                ["데이터 웨어하우스", "Data Warehouse", "정리한 뒤 담는 분석용 저장소 (CDW)"],
                ["열 저장", "Columnar Storage", "같은 열의 값끼리 모아 저장 — 집계가 빠름"],
                ["분산 처리", "Distributed Processing", "여러 컴퓨터가 나눠 계산하고 합침"],
                ["NoSQL", "Not only SQL", "표가 아닌 모양(JSON · 그래프)으로 담는 DB"],
                ["API", "Application Programming Interface", "정해진 항목만 꺼내 주는 프로그램 창구"]])
    t = d.tree(e13)
    set_title(t, "14주차 강의 정리")
    fill(shape(t, "TextBox 4"), [(1, ["병원 밖 데이터 · 디지털 바이오마커", "도 표준 · 품질이 먼저다"]),
                                 (0, ["데이터 레이크는 먼저 담고, ", "CDW", "는 정리해 담는다"]),
                                 (0, ["운영은 ", "행 저장", ", 분석은 열 저장이 알맞다"]),
                                 (0, ["API · AI로 넓게 써도 ", "가명처리 · 검산", "은 그대로 지킨다"])])
    drop(t, "Next 5")
    d.tree(lake).attrib.pop("show", None)

    # ---- 지우고 새 14강을 13강 뒤 · 15강 앞에 순서대로
    for s in gone:
        d.delete(s)
    order = [c13, review13, goals13, divs13[0], new["out"], new["dbm"], new["xmod"], divs13[1], lake, new["swamp"], sums13[0],
             divs13[2], new["rowcol"], new["dist"], divs13[3], new["nosql"], new["fhir"], sums13[1],
             divs13[4], new["users"], new["api"], new["aisql"], divs13[5], terms13, exam, e13]
    anchor = e14
    for s in order:
        d.lst.remove(s); anchor.addnext(s); anchor = s
    assert d.slides().index(anchor) + 1 == d.slides().index(c15)

    # ---- 15강: 리뷰 · 시험 범위 · 총복습 ④
    L15 = d.slides()[d.slides().index(c15):]
    F15 = lambda line, also=None: d.find(line, also, within=L15)
    t = d.tree(F15("지난시간 리뷰"))
    fill(shape(t, "TextBox 4"), [(0, ["병원 밖 데이터와 ", "디지털 바이오마커", "까지 합쳐 분석한다"]),
                                 (0, ["데이터 레이크는 먼저 담고, ", "CDW", "는 정리해 담는다"]),
                                 (0, ["API · AI로 넓게 써도 ", "가명처리 · 검산", "은 그대로 지킨다"]),
                                 (3, ["오늘은 시험 안내와 함께 한 학기 내용을 한 번에 정리합니다."])])
    t = d.tree(F15("시험 범위"))
    rows = table_rows(t)
    assert rows[7][0] == "11 · 12 · 13" and rows[8][0] == "14", rows
    table_fill(t, rows[0], rows[1:7] + [
        ["11 · 12", "CDW · 병원 통계", "CDW 구조, 한 행의 단위, 재원일수 · 수술시간 · 가동률, 지표(분자 ÷ 분모), JOIN 함정"],
        ["13", "병원 데이터 표준", "병원마다 다른 기록, 용어 · 교환 · 구조 표준, 매핑 · OMOP CDM · Epic, 품질 · 가명정보"],
        ["14", "빅데이터와 AI", "병원 밖 데이터 · 디지털 바이오마커, 데이터 레이크, 행 · 열 저장, 분산, NoSQL · FHIR, API · AI"]],
        sz=1300, head_sz=1400)
    move_y(t, "TextBox 6", 6550000)                                     # 줄이 늘어 두 줄 칸이 생겨도 겹치지 않게
    assert second_run(L15, d, "총복습 ④", "CDW와 병원 지표", "11~14주차 병원 데이터") == 6
    set_para(shape(d.tree(F15("5. 총복습 ④")), "TextBox 4"), "11~14주차 병원 데이터")
    t = d.tree(F15("총복습 ④ — CDW와 병원 지표"))
    set_title(t, "총복습 ④ — 11~14주차 병원 데이터")
    table_fill(t, ["개념", "한 줄 정의", "자주 나오는 구분"],
               [["CDW", "분석 · 연구용으로 모아 둔 읽기 전용 복사본", "운영 DB는 진료용, CDW는 분석용"],
                ["ETL", "원천에서 뽑아 정리해 CDW에 넣는 작업", "보통 하루 정도 시차"],
                ["한 행의 단위", "표의 한 행이 무엇을 뜻하는가", "환자 / 입원 / 진료비 항목"],
                ["재원일수 · 수술시간", "퇴원일 − 입원일 · 종료시각 − 시작시각", "재원 중이면 퇴원일 NULL, 같은 수술끼리 비교"],
                ["지표", "분자 ÷ 분모", "낙상률 = 낙상 건수 ÷ 재원일수 × 1,000"],
                ["분류와 용어", "KCD는 통계 · 청구용 분류, SNOMED CT는 임상용 용어", "KCD E11 ↔ SNOMED CT 44054006"],
                ["OMOP CDM", "여러 기관의 데이터를 같은 구조로 맞춘 모델", "같은 EMR(Epic)을 쓰는 길과 다름"],
                ["데이터 레이크", "형태 그대로 먼저 담고 쓸 때 정리", "CDW(웨어하우스)는 정리한 뒤 담음"],
                ["가명정보", "추가 정보 없이는 개인을 알아볼 수 없게 처리", "가명 / 익명의 차이"]])

    # ---- 1강 강의 계획표 (2장): 11~14주차 · 과제 2
    plans = [s for s in d.slides() if "과제 2: 12~13주차 CDW 실무 과제, 단일 제출물 20점" in texts(d.tree(s))]
    assert len(plans) == 2, len(plans)
    for s in plans:
        t = d.tree(s)
        rows = table_rows(t)
        assert [r[1] for r in rows[11:15]] == ["CDW 구조와 분석 업무 흐름", "의료데이터에서 자주 생기는 오류", "CDW 실무 사례", "빅데이터와 의료데이터 표준"], rows
        for r, txt in zip(range(11, 15), ["EMR과 CDW의 데이터 구조", "SQL로 병원 통계 분석", "병원 데이터 표준과 품질", "빅데이터와 AI 시대의 DBMS"]):
            set_cell(t, r, 1, txt)
        src_r = list(cell(t, 13, 2).iter(A + "r"))                      # '과제' · '2' 두 런
        assert "".join(r.findtext(A + "t") for r in src_r) == "과제2", [r.findtext(A + "t") for r in src_r]
        p12 = cell(t, 12, 2).find(f"{A}txBody/{A}p")
        assert p12.find(A + "r") is None
        end = p12.find(A + "endParaRPr")
        for r in src_r:
            (end.addprevious if end is not None else p12.append)(copy.deepcopy(r))
            r.getparent().remove(r)
        m = [p_ for p_ in t.iter(A + "p") if "".join(x.text or "" for x in p_.iter(A + "t")) == "과제 2: 12~13주차 CDW 실무 과제, 단일 제출물 20점"]
        assert len(m) == 1
        rs = m[0].findall(A + "r")                                       # '과제' ' 2' 는 굵게 그대로, 뒤만 바꿈
        assert [r.findtext(A + "t") for r in rs[2:5]] == [": 12~13주차 CDW ", "실무", " "], [r.findtext(A + "t") for r in rs]
        rs[2].find(A + "t").text = ": 8~12주차 병원 SQL "
        m[0].remove(rs[3]); m[0].remove(rs[4])

    d.save(out)
    print(f"지운 슬라이드 {len(gone)} · 새 14강 {len(order)}장 (새로 만든 {len(new)}) · Epic 2장 · 13강 {len(d.between(c14, e14))}장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
