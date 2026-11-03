# -*- coding: utf-8 -*-
"""14강을 쉽게: '병원 데이터를 맞추는 법 — 표준과 품질' (2026-11-03, 강사: "내용은 많은데 무슨 소리인지 모르겠다").

이야기: 병원마다 같은 것을 다르게 적는다 → 청구(돈)에 쓰는 코드만 비교적 맞다 → 맞추는 세 가지 방법(같은 말 · 같은 서식 · 같은 서랍)
→ 같은 말(용어 표준) → 같은 서랍(매핑 · OMOP CDM) → 그래도 안 맞는 이유와 먼저 물어볼 것 → 품질 · 가명정보 → 정리
- 새 슬라이드 6장 (도형으로 그린 도표. 웹 이미지 출처는 tools/assets/SOURCES.md)
    같은 것을 병원마다 다르게 적습니다 · 맞춰져 있는 것과 아닌 것 · 맞추는 세 가지 방법
    매핑 — 번역표 (+ 로제타석 사진, CC BY-SA 4.0) · OMOP CDM — 공통 서랍장 (+ OHDSI CDM v5.4 그림, Apache 2.0) · 그래도 잘 안 맞는 이유
- 줄임: 표준 용어 표 6줄 → 4줄, KCD vs SNOMED CT 6줄 → 4줄, SNOMED CT 구조 (개념 · 용어 · 관계 → 쉬운 설명 한 칸, 연표는 두 줄), 용어 정리 10 → 7
- 숨김 7장 (지우지 않음): 웨어하우스 · 레이크 (→ 정형 · 비정형 장에 한 줄), 세 가지 축, 국내 도입 연표, OMOP 표 그림 (→ 실제 그림 장),
  concept_ancestor SQL, 오류 점검 체크리스트, 빠진 값
- 13강 '다음 시간' · 15강 지난시간 리뷰 · 시험 범위 14주차 칸
w14_fix.py 다음에 실행. 사용: python3 tools/w14_easy.py <덱.pptx> <결과.pptx>
"""
import os, sys, copy
from w10_tx_more import fill
from w12_new import agenda, summary_slide
from w14_fix import RANGE
from slidekit import (A, P, Deck, texts, shape, set_para, set_title, replace_text, table_fill, move_y, add_box, add_arrow,
                      set_fill, remove_shapes, hide)

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_ROSETTA = os.path.join(HERE, "assets", "rosetta_stone.jpg")      # 683 × 800
IMG_OMOP = os.path.join(HERE, "assets", "omop_cdm54.png")           # 2200 × 1335
TITLE14 = "14강. 병원 데이터를 맞추는 법 — 표준과 품질"
AG = [("왜 숫자가 다를까", "병원마다 다른 기록"), ("맞추는 세 가지 방법", "말 · 서식 · 서랍"), ("같은 말", "용어 표준"),
      ("같은 서랍", "매핑과 OMOP CDM"), ("품질과 가명정보", "믿을 수 있는 데이터"), ("정리", "용어와 요약")]
X0, X1 = 806418, 13006418                    # 본문 왼쪽 · 오른쪽 끝
BLUE_F, BLUE_L = "DEEAF6", "1F497D"          # 덱의 파란 칸 (11강 'CDW를 쓰는 방법')
GREEN_F, GREEN_L, RED_F, RED_L = "E2EFDA", "2C5F2D", "FBE5E5", "C00000"
YEL_F, YEL_L, GREY_F = "FFF2CC", "BF9000", "F2F2F2"
B = {"b": True}


def clone(d, sid):
    t, rel = d.clone(sid)
    t.attrib.pop("show", None)               # 숨긴 장을 복제해도 새 장은 보이게
    return t, rel


def blank(d, tmpl, title, sub):
    """제목 · 부제만 남긴 장 ('세 가지 축' 복제)"""
    t, rel = clone(d, tmpl)
    remove_shapes(t, {"object 3", "Title 16", "TextBox 4"})
    set_title(t, title); set_para(shape(t, "TextBox 4"), sub)
    return t, rel


def credit(t, text, x, y, cx, align="r"):
    add_box(t, x, y, cx, 280000, [text], fill=None, line=None, sz=1000, color="7F7F7F", geom="rect", align=align, inset=0, name="Credit")


def seed_empty_cells(t):
    """런이 없는 표 칸에 같은 행의 런을 빈 글로 넣음 (table_fill 은 칸마다 런이 있어야 함)"""
    for tr in t.iter(A + "tr"):
        donor = next(tr.iter(A + "r"), None)
        for tc in tr.findall(A + "tc"):
            p0 = tc.find(f"{A}txBody/{A}p")
            if donor is not None and p0 is not None and p0.find(A + "r") is None:
                r = copy.deepcopy(donor); r.find(A + "t").text = ""
                end = p0.find(A + "endParaRPr")
                end.addprevious(r) if end is not None else p0.append(r)


# ---------------------------------------------------------------- 새 슬라이드
def same_thing(t):
    """같은 것을 병원마다 다르게 적습니다: 세 병원 × 기록 네 가지 (원내 코드 · 표 이름은 예시)"""
    rows = [("진단 코드", ["E11.9", "E11.9", "E11.9"], True),
            ("당화혈색소 검사", ["L2301 · HbA1c", "BC0457 · A1C", "LAB88 · 당화혈색소"], False),
            ("낙상 위험 평가", ["Morse 척도 45점", "Hendrich II 5점", "‘위험 높음’ (서술)"], False),
            ("CDW 표 · 열 이름", ["DIAG.DX_CD", "TB_DGNS.ICD_CD", "진단.진단코드"], False)]
    lw, gap = 1900000, 120000
    x0 = X0 + lw + gap
    cw = (X1 - x0 - 2 * gap) // 3
    for k, h in enumerate(["A병원", "B병원", "C병원"]):
        add_box(t, x0 + k * (cw + gap), 1480000, cw, 520000, [h], fill=BLUE_L, line=BLUE_L, sz=1900, color="FFFFFF", bold=True, name="Hospital")
    for i, (label, vals, same) in enumerate(rows):
        y = 2100000 + i * 850000
        add_box(t, X0, y, lw, 740000, [label], fill=GREY_F, line="BFBFBF", sz=1600, bold=True, color="262626", name="Row")
        for k, v in enumerate(vals):
            add_box(t, x0 + k * (cw + gap), y, cw, 740000, [v], fill=GREEN_F if same else RED_F, line=GREEN_L if same else RED_L,
                    sz=1700, color=GREEN_L if same else "7F0000", bold=same, name="Cell")
    add_box(t, X0, 5620000, X1 - X0, 900000,
            [[("초록  ", {"b": True, "color": GREEN_L}), ("청구에 쓰는 진단 코드는 병원끼리 같습니다", {})],
             [("빨강  ", {"b": True, "color": RED_L}), ("검사 코드 · 간호 평가 도구 · 표 이름은 병원마다 다릅니다", {})]],
            fill=YEL_F, line=YEL_L, sz=1600, align="l", name="Legend")


def aligned(t):
    """맞춰져 있는 것과 아닌 것 ('CDW를 쓰는 방법' 두 칸 복제)"""
    set_title(t, "맞춰져 있는 것과 아닌 것")
    set_para(shape(t, "TextBox 4"), "기준은 ‘청구(돈)에 쓰이는가’입니다")
    set_para(shape(t, "TextBox 5"), "청구에 쓰는 코드는 나라가 정해 두어서 병원끼리 같습니다.")
    set_para(shape(t, "Panel Head 7"), "비교적 맞춰져 있음 — 청구에 쓰임")
    fill(shape(t, "TextBox 8"), [(0, ["진단 — KCD (한국표준질병사인분류)"]), (1, ["행위 · 수가 — 건강보험 EDI 코드"]), (2, ["약 — 건강보험 약제 코드"])])
    set_para(shape(t, "Panel Head 10"), "병원마다 제각각 — 청구와 상관없음")
    fill(shape(t, "TextBox 11"), [(0, ["검사 결과 — 원내 검사 코드 · 이름"]), (1, ["간호기록 — 서식 · 평가 도구 · 서술"]), (2, ["CDW — 표 이름 · 열 이름"])])
    fill(shape(t, "TextBox 12"), [(0, ["그래서 여러 병원 자료를 합치려면 맞추는 일이 따로 필요합니다."]),
                                  (1, ["다음 절에서 맞추는 세 가지 방법(같은 말 · 같은 서식 · 같은 서랍)을 봅니다."])])
    set_fill(shape(t, "Panel Head 7"), GREEN_L, GREEN_L); set_fill(shape(t, "Panel 6"), GREEN_F, GREEN_L)
    set_fill(shape(t, "Panel Head 10"), RED_L, RED_L); set_fill(shape(t, "Panel 9"), RED_F, RED_L)


def three_ways(t):
    """맞추는 세 가지 방법: 세 병원 → 말 · 서식 · 서랍 → 같은 SQL"""
    cx = (X0 + X1) // 2
    w, gap = 1700000, 350000
    hx = cx - (3 * w + 2 * gap) // 2
    for k, h in enumerate(["A병원", "B병원", "C병원"]):
        add_box(t, hx + k * (w + gap), 1450000, w, 460000, [h], fill=BLUE_F, line=BLUE_L, sz=1600, bold=True, color=BLUE_L, name="Hospital")
    add_arrow(t, cx - 300000, 1990000, 600000, 420000, "down")
    cols = [("① 같은 말 — 용어 표준", "1F497D", "같은 것을 같은 코드로 부르기", "예: KCD · LOINC · SNOMED CT", "모두 같은 사전을 쓴다"),
            ("② 같은 서식 — 교환 표준", "7030A0", "병원끼리 같은 양식으로 주고받기", "예: HL7 FHIR · 건강정보 고속도로", "같은 진료의뢰서 양식"),
            ("③ 같은 서랍 — 구조 표준", "2C5F2D", "표 모양까지 똑같이 맞추기", "예: OMOP CDM", "같은 서랍장에 넣는다")]
    cg = 250000
    cw = (X1 - X0 - 2 * cg) // 3
    for k, (head, col, what, ex, like) in enumerate(cols):
        x = X0 + k * (cw + cg)
        add_box(t, x, 2500000, cw, 560000, [head], fill=col, line=col, sz=1800, color="FFFFFF", bold=True, name="Head")
        add_box(t, x, 3060000, cw, 2150000, [what, "", ex, "", [("비유  ", {"b": True, "color": col}), (like, B)]],
                fill="F7F7F7", line="BFBFBF", sz=1600, name="Body")
    add_arrow(t, cx - 300000, 5300000, 600000, 400000, "down")
    add_box(t, cx - 4500000, 5780000, 9000000, 680000, [[("결과  ", B), ("같은 SQL로 여러 병원을 같은 기준으로 셀 수 있습니다", {})]],
            fill=YEL_F, line=YEL_L, sz=1800, name="Result")


def mapping(d, sid):
    """매핑 — 번역표: 병원마다 다른 검사 이름 → LOINC 하나, 번역표에 없는 코드는 빠짐 (+ 로제타석)"""
    t = d.tree(sid)
    src = [("A병원", "HbA1c", 1500000), ("B병원", "A1C", 2250000), ("C병원", "당화혈색소", 3000000), ("D병원", "새 검사코드 N-07", 4000000)]
    for i, (h, name, y) in enumerate(src):
        add_box(t, X0, y, 2700000, 620000, [[(h + "  ", B), (name, {})]], fill=BLUE_F, line=BLUE_L, sz=1600, name="Source")
        add_arrow(t, X0 + 2780000, y + 130000, 800000, 360000, "right", fill="8EA9DB" if i < 3 else "E69C9C")
    sx = X0 + 3660000
    add_box(t, sx, 1500000, 3300000, 2120000, [[("표준 코드", B)], "LOINC 4548-4", "당화혈색소"],
            fill=GREEN_F, line=GREEN_L, sz=1900, color="1E4620", name="Standard")
    add_box(t, sx, 4000000, 3300000, 620000, [[("번역표에 없음 → 분석에서 빠짐", {"b": True, "color": RED_L})]],
            fill=RED_F, line=RED_L, sz=1600, name="Missing")
    add_box(t, X0, 4950000, sx + 3300000 - X0, 1100000,
            [[("번역표(매핑)", B), ("는 사람이 만듭니다.", {})], "그래서 병원마다 조금씩 다르고, 번역표에 없는 코드는 빠집니다."],
            fill=YEL_F, line=YEL_L, sz=1700, align="l", name="Note")
    rx = 8500000
    rw = X1 - rx
    pw = 2800000; ph = pw * 800 // 683
    d.add_picture(sid, IMG_ROSETTA, rx + (rw - pw) // 2, 1450000, pw, ph, name="Rosetta Stone", descr="로제타석 (Hans Hillewaert, CC BY-SA 4.0)")
    add_box(t, rx, 1450000 + ph + 80000, rw, 1300000,
            [[("로제타석", B), (" — 같은 글을 세 가지 글자로 새긴 돌", {})], "이 돌 덕분에 옛 이집트 글자를 읽어 냈습니다.",
             "매핑도 이처럼 병원마다 다른 ‘글자’를", "하나로 읽게 해 주는 번역표입니다."],
            fill=None, line=None, sz=1400, anchor="t", geom="rect", name="Caption")
    credit(t, "사진: Hans Hillewaert, CC BY-SA 4.0, Wikimedia Commons", rx, 1450000 + ph + 1420000, rw, align="ctr")


def omop_picture(d, sid):
    """OMOP CDM — 실제 표 구성도 + 설명 세 칸"""
    t = d.tree(sid)
    pw = 8400000; ph = pw * 1335 // 2200
    d.add_picture(sid, IMG_OMOP, X0, 1450000, pw, ph, name="OMOP CDM", descr="OMOP CDM v5.4 표 구성도 (OHDSI, Apache License 2.0)")
    credit(t, "그림: OHDSI CommonDataModel v5.4 (Apache License 2.0)", X0, 1450000 + ph + 50000, pw, align="l")
    x = X0 + pw + 220000
    notes = [("① 파란 칸 — 진료 기록", "환자 · 방문 · 진단 · 약 · 검사 (Person · Visit · Condition · Drug · Measurement)", BLUE_F, "2E75B6"),
             ("② 주황 칸 — 표준 용어 사전", "코드의 뜻은 모두 Concept 표에. 매핑한 표준 코드가 여기에 있습니다", "FBE4D5", "C55A11"),
             ("③ 짜임은 배운 그대로", "기본키 · 외래키 · JOIN. 같은 SQL을 병원마다 돌리고 결과만 모읍니다 (환자 자료는 병원 밖으로 안 나감)", GREY_F, "7F7F7F")]
    for i, (head, body, f, l) in enumerate(notes):
        add_box(t, x, 1450000 + i * 1740000, X1 - x, 1620000, [[(head, B)], body], fill=f, line=l, sz=1500, align="l", name="Callout")


def still_hard(t):
    """그래도 잘 안 맞는 이유 ('여기까지 정리' 복제)"""
    summary_slide(t, [("① ", "원내 코드 · 자유 입력", "이 아직 많다 — 특히 검사 · 간호기록"),
                      ("② ", "번역표(매핑)", "는 사람이 만들어 병원마다 다르고, 빠지는 코드가 생긴다"),
                      ("③ ", "돈 · 사람 · 시간", "이 드는 일이라 병원마다 진척이 다르다")], ("", "", ""))
    fill(shape(t, "TextBox 7"), [(0, ["여러 병원 자료를 받으면 먼저 물어볼 것", ""]), (1, ["· 어떤 표준 코드로 맞췄나?"]),
                                 (1, ["· 번역표에 없어 빠진 것은 몇 %인가?"]), (1, ["· 단위 · 평가 도구 · 기준일은 같은가?"])])
    set_title(t, "그래도 잘 안 맞는 이유")
    set_para(shape(t, "TextBox 4"), "표준이 있어도 현실은 다릅니다")


def main(src, out):
    d = Deck(src)
    s14 = d.find("14강. 빅데이터와 의료데이터 표준")
    e14 = d.find("14주차 강의 정리")
    s15 = d.find("15강. 기말고사")
    L = d.between(s14, e14)
    F = lambda line, also=None: d.find(line, also, within=L)
    rv, goal = F("지난시간 리뷰"), F("14주차 학습 목표")
    divs = [F("1. 의료데이터의 형태"), F("2. 표준 용어"), F("3. SNOMED CT"), F("4. 공통 데이터 모델"), F("5. 품질과 가명정보"), F("6. 정리")]
    kinds, lake = F("의료데이터의 형태"), F("데이터 웨어하우스와 데이터 레이크")
    std, nostd, kcd_sn = F("의료데이터 표준 용어"), F("표준 코드가 없으면"), F("분류와 용어 — KCD와 SNOMED CT")
    recode, axes = F("코드가 바뀌면 추세가 끊깁니다"), F("표준에는 세 가지 축이 있습니다")
    sn_tree, korea = F("SNOMED CT의 구조 — 개념 · 용어 · 관계"), F("국내 SNOMED CT 도입 현황")
    omop, omop_t, omop_sql = F("공통 데이터 모델 — OMOP CDM"), F("OMOP CDM 주요 테이블"), F("OMOP CDM에서 SNOMED CT가 쓰이는 방식")
    qual, checklist, sql4, missing = F("데이터 품질 점검"), F("오류 점검 체크리스트"), F("오류를 찾는 SQL 네 가지"), F("빠진 값 자체가 정보입니다")
    pseudo, summ, public = F("가명정보와 안전한 분석"), F("여기까지 정리"), F("병원 CDW 계정이 없다면")
    terms, exam = F("14주차 용어 정리"), F("기말고사 미리 안내")

    # ---- 새 슬라이드 (숨기기 전에 복제)
    new = lambda t, rel: d.insert_after(e14, t, rel)
    t, rel = blank(d, axes, "같은 것을 병원마다 다르게 적습니다", "같은 당뇨병 환자를 세 병원이 기록하면"); same_thing(t); n_same = new(t, rel)
    t, rel = clone(d, d.find("CDW를 쓰는 방법")); aligned(t); n_aligned = new(t, rel)
    t, rel = blank(d, axes, "맞추는 세 가지 방법 — 같은 말 · 같은 서식 · 같은 서랍", "여러 병원의 자료를 합칠 때 필요한 세 가지")
    three_ways(t); n_three = new(t, rel)
    t, rel = blank(d, axes, "매핑 — 병원 코드를 표준 코드로 바꾸는 번역표", "같은 검사를 병원마다 다르게 부르면")
    n_map = new(t, rel); mapping(d, n_map)
    t, rel = blank(d, axes, "OMOP CDM — 여러 병원의 공통 서랍장", "공통 데이터 모델 — 여러 병원이 같은 표 모양으로 자료를 담기로 한 약속")
    n_omop = new(t, rel); omop_picture(d, n_omop)
    t, rel = clone(d, d.find("여기까지 정리", "① CDW = 분석용으로 따로 모아 둔 읽기 전용 복사본")); still_hard(t); n_hard = new(t, rel)

    # ---- 표지 · 리뷰 · 학습 목표 · 구분
    for s in d.tree(s14).iter(P + "sp"):
        tx = texts(s)
        if tx and tx[0] == "14강. 빅데이터와 의료데이터 표준":
            set_para(s, TITLE14)
            for pr in s.iter(A + "rPr"):
                pr.set("sz", "4000")             # 48pt 이면 두 줄로 넘침
        elif tx[:3] == ["분류(KCD)와 용어(SNOMED CT)", "SNOMED CT와 OMOP 공통 데이터 모델", "데이터 품질과 가명정보"]:
            fill(s, [(0, ["왜 병원마다 숫자가 다를까"]), (1, ["같은 말 · 같은 서식 · 같은 서랍"]), (2, ["품질 점검과 가명정보"])])
    set_para(shape(d.tree(rv), "TextBox 4"), "오늘은 여러 병원의 데이터를 맞추는 법을 봅니다.", i=4)
    t = d.tree(goal)
    set_para(shape(t, "TextBox 4"), "여러 병원의 데이터를 같은 기준으로")
    fill(shape(t, "TextBox 6"), [(0, ["① 병원마다 데이터가 다른 이유를 말한다"]), (1, ["② 맞추는 세 가지 방법을 구분한다"]),
                                 (2, ["③ 매핑과 OMOP CDM이 하는 일을 말한다"]), (3, ["④ 품질 점검과 가명정보를 설명한다"])])
    agenda(t, "Step", AG, "  ")
    for k, s in enumerate(divs):
        t = d.tree(s)
        set_title(t, f"{k + 1}. {AG[k][0]}"); set_para(shape(t, "TextBox 4"), AG[k][1]); agenda(t, "Sec", AG, "   ")

    # ---- 1절 · 3절: 있던 슬라이드를 쉽게
    t = d.tree(kinds)
    set_title(t, "기록의 모양 — 정형 · 비정형")
    replace_text(t, "경과기록 문장, 영상, 음성", "간호기록 문장, 영상, 음성")
    fill(shape(t, "TextBox 6"), [(0, ["병원 데이터의 대부분은 비정형이라, 분석하려면 먼저 표(정형)로 바꿔야 합니다."]),
                                 (0, ["정리한 표는 데이터 웨어하우스(병원 CDW)에, 원본 그대로는 데이터 레이크에 모읍니다."])])
    shape(t, "TextBox 6").find(f".//{A}ext").set("cy", "1000000")
    t = d.tree(nostd)
    replace_text(t, "다기관 비교가 바로 가능", "같은 기준으로 셀 수 있음")
    set_para(shape(t, "TextBox 12"), "그럼 어떤 표준 코드가 있고, 병원끼리 정말 맞을까요? 다음 장에서 봅니다.", i=1)
    t = d.tree(std)
    set_para(shape(t, "TextBox 4"), "무엇을 어떤 코드로 부르나 — 그리고 병원끼리 정말 맞나")
    y = table_fill(t, ["무엇", "표준 코드", "예", "병원끼리 잘 맞나"],
                   [["진단", "KCD (한국표준질병사인분류)", "E11  제2형 당뇨병", "잘 맞음 — 청구에 꼭 씀"],
                    ["약 · 행위", "건강보험 EDI 코드", "약 · 처치마다 청구 번호", "잘 맞음 — 청구에 꼭 씀"],
                    ["검사 결과", "LOINC", "4548-4  당화혈색소", "잘 안 맞음 — 원내 코드가 많음"],
                    ["임상 기록 전반", "SNOMED CT", "44054006  제2형 당뇨병", "이제 시작 — 2020년부터 국내 무료"]],
                   widths=[1900000, 3300000, 3200000, 3800000], row_h=640000, sz=1700)
    set_para(shape(t, "TextBox 6"), "표준이 있어도 그 코드로 적어야 맞습니다. 지금 잘 맞는 것은 청구용 코드뿐입니다.")
    move_y(t, "TextBox 6", y + 350000)
    t = d.tree(kcd_sn)
    seed_empty_cells(t)
    y = table_fill(t, ["", "KCD (분류)", "SNOMED CT (용어)"],
                   [["쉽게 말하면", "큰 칸 — 한 칸에 하나씩 넣어 센다", "자세한 사전 — 낱말끼리 위아래로 이어짐"],
                    ["목적", "몇 명인가 (통계 · 청구)", "무엇이 있었나 (임상 기록)"],
                    ["예", "E11  제2형 당뇨병", "44054006  Type 2 diabetes mellitus"],
                    ["청구에 쓰나", "씀", "쓰지 않음 (청구는 KCD로)"]], row_h=700000, sz=1800)
    set_para(shape(t, "TextBox 12"), "그래서 코드끼리 잇는 번역표(매핑)가 필요합니다. 4절에서 봅니다.", i=1)
    move_y(t, "TextBox 12", y + 300000)
    t = d.tree(sn_tree)
    set_title(t, "SNOMED CT — 낱말이 위아래로 이어진 사전")
    set_para(shape(t, "TextBox 4"), "‘~의 한 종류(is a)’로 이어져 있어, 위 낱말 하나로 아래 낱말까지 모두 찾습니다")
    remove_shapes(t, {el.find(f".//{P}cNvPr").get("name") for el in t.find(f"{P}cSld/{P}spTree")
                      if el.find(f".//{P}cNvPr") is not None} - {"Part 0", "Part 1", "Part 2"})
    add_box(t, 7239000, 1498600, 5600700, 3886200,
            [[("쉽게 말하면", B)], "", "· 번호 하나 = 뜻 하나 (어느 병원에서나 같은 뜻)", "", "· 국내 의료기관은 2020년부터 무료로 사용", "",
             "· 2026년 한국판 배포 — 한글 동의어 약 6만 개", "", "· 아직은 연구 · 진료정보 교류에 주로 씀 (청구는 KCD)"],
            fill=BLUE_F, line=BLUE_L, sz=1600, align="l", name="Easy")
    fill(shape(t, "Bottom"), [(0, ["왜 중요한가  ", "‘당뇨병’ 하나를 고르면 제2형 · 합병증 동반까지 함께 잡혀, 병원마다 같은 기준으로 환자를 고릅니다."]),
                              (1, ["KCD는 한 칸에 하나만 넣는 분류라 이런 ‘족보’가 없습니다."])])

    # ---- 4절 · 5절 · 6절
    t = d.tree(omop_t)
    set_para(shape(t, "TextBox 4"), "우리 가상 병원 CDW의 표와 대응해 보면")
    table_fill(t, ["OMOP 테이블", "한 행이 뜻하는 것", "가상 병원 CDW로 치면"],
               [["PERSON", "환자 1명", "환자"], ["VISIT_OCCURRENCE", "방문(외래 · 입원) 1건", "입원"],
                ["CONDITION_OCCURRENCE", "진단 1건", "진단"], ["DRUG_EXPOSURE", "약물 노출 1건", "처방 (우리 DB에는 없음)"],
                ["MEASUREMENT", "검사 · 측정 1건", "검사"], ["CONCEPT", "표준 코드 1개", "코드 마스터 (우리 DB에는 없음)"]])
    set_para(shape(d.tree(qual), "TextBox 6"), "바로 뒤의 ‘오류를 찾는 SQL 네 가지’로 분석 전에 데이터 전체를 한 번 훑어봅니다.")
    set_para(shape(d.tree(sql4), "TextBox 5"), "새 데이터를 받으면 가장 먼저 돌려 보는 네 가지 조회입니다.")     # 두 줄째가 아래 칸에 가려졌음
    t = d.tree(summ)
    fill(shape(t, "TextBox 5"), [(2, ["① ", "병원마다", " 같은 것을 다르게 적는다 — 청구에 쓰는 코드만 비교적 맞다"]),
                                 (2, ["② ", "맞추는 방법", "은 같은 말(용어) · 같은 서식(교환) · 같은 서랍(OMOP CDM)"]),
                                 (2, ["③ ", "여러 병원 자료", "는 어떻게 맞췄는지부터 묻고, 품질을 점검한다"])])
    fill(shape(t, "TextBox 7"), [(0, ["잠깐 생각해 봅시다", "  다른 병원의 낙상률이 우리 병원의 두 배라면?"]),
                                 (1, ["먼저 평가 도구 · 기록 기준 · 분모(재원일수)가 같은지 봅니다. 진짜 차이인지는 그다음입니다."])])
    table_fill(d.tree(terms), ["용어", "영어", "뜻 (한 줄)"],
               [["용어 표준", "Terminology", "같은 것을 같은 코드로 부르는 약속 (KCD · LOINC · SNOMED CT)"],
                ["교환 표준", "HL7 FHIR", "병원끼리 같은 양식으로 주고받는 약속"],
                ["OMOP CDM", "Common Data Model", "표 모양까지 똑같이 맞춘 공통 데이터 모델 (구조 표준)"],
                ["매핑", "Mapping", "병원 코드를 표준 코드로 바꾸는 번역표"],
                ["SNOMED CT", "Clinical Terms", "낱말이 위아래로 이어진 임상 용어 사전"],
                ["데이터 품질", "Data Quality", "완전성 · 유효성 · 일관성 · 유일성 · 시의성"],
                ["가명정보", "Pseudonymized", "추가 정보 없이는 누구인지 알 수 없게 처리한 정보"]],
               widths=[2200000, 2600000, 7000000], row_h=560000, sz=1600)
    wrap = [(1, ["병원마다 같은 것을 다르게 적는다 — ", "청구용 코드", "만 비교적 맞다"]),
            (1, ["맞추는 방법은 ", "같은 말 · 같은 서식 · 같은 서랍", " (용어 · 교환 · OMOP CDM)"]),
            (2, ["여러 병원 자료는 ", "어떻게 맞췄는지", "부터 묻고, ", "품질 · 가명처리", "를 확인한다"])]
    fill(shape(d.tree(e14), "TextBox 4"), wrap)
    for s in (lake, axes, korea, omop, omop_sql, checklist, missing):
        hide(d.tree(s))

    # ---- 순서
    order = [s14, rv, goal,
             divs[0], n_same, kinds, n_aligned, lake,
             divs[1], n_three, axes,
             divs[2], nostd, std, kcd_sn, sn_tree, recode, korea,
             divs[3], n_map, n_omop, omop, omop_t, n_hard, omop_sql,
             divs[4], qual, sql4, checklist, missing, pseudo, summ, public,
             divs[5], terms, exam, e14]
    block = d.slides()[d.index(s14): d.index(s15)]
    assert len(order) == len(set(order)) == len(block) and set(order) == set(block), (len(order), len(set(order)), len(block))
    prev = d.slides()[d.index(s14) - 1]
    for s in order:
        d.lst.remove(s)
    for s in order:
        prev.addnext(s); prev = s

    # ---- 13강 '다음 시간' · 15강 리뷰 · 시험 범위
    runs = list(shape(d.tree(d.find("13주차 강의 정리")), "Next 5").iter(A + "r"))
    assert runs[0].findtext(A + "t") == "다음 시간"
    runs[1].find(A + "t").text = "  " + TITLE14
    L15 = d.slides()[d.index(s15):]
    tb = shape(d.tree(d.find("지난시간 리뷰", within=L15)), "TextBox 4")
    fill(tb, wrap + [(3, [texts(tb)[3]])])
    rng = [list(r) for r in RANGE]
    assert rng[-1][0] == "14"
    rng[-1] = ["14", "병원 데이터 표준", "병원마다 다른 기록, 용어 · 교환 · 구조 표준, 매핑 · OMOP CDM, 품질, 가명정보"]
    table_fill(d.tree(d.find("시험 범위", within=L15)), ["주차", "주제", "꼭 알아야 할 것"], rng)
    d.save(out)
    print(f"14강: 새 6장 · 숨김 7장 · 보이는 장 {sum(d.tree(s).get('show') != '0' for s in order)}장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
