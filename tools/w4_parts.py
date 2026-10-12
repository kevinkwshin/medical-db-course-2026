# -*- coding: utf-8 -*-
"""4주차에서 쓰는 도식 슬라이드 빌더 모음 (build_week4.py 에서 import)."""
from deckgen import *


# ---------------------------------------------------------------- 학습 목표
def objectives_slide(week, goals, agenda, date_note=None):
    def b(ids):
        s = textbox(ids, X0, 1450000, 5900000, 400000,
                    para("**오늘 끝나면 할 수 있어야 하는 것**", sz=2400, color=BLUE, lnSpc=100), autofit=False)
        ps = "".join(para(f"{m} {g}", sz=2200, lnSpc=145, marL=520000, indent=-520000)
                     for m, g in zip(["①", "②", "③", "④", "⑤"], goals))
        s += textbox(ids, X0, 1950000, 5900000, 3600000, ps, autofit=False)
        xr = 7150000
        s += textbox(ids, xr, 1450000, 5600000, 400000,
                     para("**오늘의 순서**", sz=2400, color=BLUE, lnSpc=100), autofit=False)
        y, h, gap = 1950000, 560000, 120000
        for i, (name, sub) in enumerate(agenda, 1):
            s += shape(ids, "rect", xr, y, 620000, h, fill="1F497D", line="1F497D",
                       text_xml=para(f"**{i}**", sz=2000, algn="ctr", color="FFFFFF", lnSpc=100), name="Step No")
            s += shape(ids, "rect", xr + 620000, y, 4980000, h, fill="F2F2F2", line="BFBFBF",
                       text_xml=para(f"**{name}**  {sub}", sz=1800, lnSpc=100, marL=180000), name="Step")
            y += h + gap
        if date_note:
            s += textbox(ids, X0, 6350000, W0, 500000, para(date_note, sz=2200, b=True, algn="ctr", color="1F3763", lnSpc=110))
        return s
    return free(f"{week}주차 학습 목표", b, subtitle="데이터베이스 시스템의 구성 요소를 하나씩 살펴봅니다")


# ---------------------------------------------------------------- 개념 스키마 + 미니 ERD
def conceptual_schema_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, 5500000, 4200000,
            para("① **어떤 테이블이 있는가**", sz=2400, lnSpc=140) +
            para("환자, 의사, 진료, 처방, 검사", sz=2000, lvl=1, lnSpc=120) +
            para("② **테이블마다 어떤 열이 있는가**", sz=2400, lnSpc=140) +
            para("진료(진료ID, 환자ID, 진료일, 진단명)", sz=2000, lvl=1, lnSpc=120) +
            para("③ **테이블 사이의 관계**", sz=2400, lnSpc=140) +
            para("환자 한 명에게 진료가 여러 건 (1 : N)", sz=2000, lvl=1, lnSpc=120) +
            para("④ **지켜야 할 규칙과 권한**", sz=2400, lnSpc=140) +
            para("진료의 환자ID는 환자 테이블에 있는 값이어야 함", sz=2000, lvl=1, lnSpc=120))
        # mini ERD (right)
        xr, y0, ew, gap = 6650000, 1700000, 1800000, 570000
        e1, h1 = entity_box(ids, xr, y0, ew, "환자", ["환자ID", "환자명", "생년월일", "성별"])
        e2, h2 = entity_box(ids, xr + ew + gap, y0, ew, "진료", ["진료ID", "환자ID", "진료일", "진단명"], key_idx=(0,))
        e3, h3 = entity_box(ids, xr + 2 * (ew + gap), y0, ew, "처방", ["처방ID", "진료ID", "약품명", "용량"], key_idx=(0,))
        s += e1 + e2 + e3
        mid = y0 + h1 // 2
        s += label_line(ids, xr + ew, mid, xr + ew + gap, mid, label="1 : N")
        s += label_line(ids, xr + 2 * ew + gap, mid, xr + 2 * (ew + gap), mid, label="1 : N")
        s += textbox(ids, xr, y0 + max(h1, h2, h3) + 250000, 6500000, 900000,
            para("밑줄 = 기본키.  진료의 환자ID처럼 다른 테이블을 가리키는 열이 **외래키**입니다 (5주차).", sz=1900, lnSpc=120, color="1F3763") +
            para("이 그림 전체가 병원 데이터베이스의 **개념 스키마**입니다.", sz=1900, b=True, lnSpc=120, color="1F3763"))
        return s
    return free("개념 스키마 (조직 전체의 관점)", b, subtitle="병원 전체의 테이블과 관계를 한 장으로 그린 설계도")


# ---------------------------------------------------------------- 내부 스키마 + 인덱스
def internal_schema_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 1800000,
            para("① **파일의 위치와 이름, 저장 형식**", sz=2400, lnSpc=140) +
            para("② **인덱스(Index)**: 빠르게 찾기 위한 색인", sz=2400, lnSpc=140) +
            para("③ **압축, 분할 저장** 등 성능을 위한 방법", sz=2400, lnSpc=140))
        y = 3450000
        s += panel(ids, X0, y, 6000000, 2200000, "인덱스가 없으면", [
            "환자번호 P0500 을 찾으려면",
            "- 1번 차트부터 순서대로 전부 확인",
            "- 차트가 많을수록 오래 걸림"], fill="FBE5E5", line="C00000")
        s += panel(ids, 7300000, y, 6000000, 2200000, "인덱스가 있으면", [
            "색인표에서 P0500 의 위치를 먼저 찾고",
            "- 해당 위치의 차트만 꺼냄",
            "- 차트가 많아도 빠름"], fill="E2EFDA", line="2C5F2D")
        s += textbox(ids, X0, 5900000, W0, 900000,
            para("→ 의료진 · 연구자가 직접 다룰 일은 거의 없고, **DBA**(DB 관리자)가 관리합니다.", sz=2200, lnSpc=125, color="1F3763") +
            para("→ 저장 방법이 바뀌어도 화면과 SQL은 그대로여야 합니다 = {{데이터 독립성}}", sz=2200, lnSpc=125, color="1F3763"))
        return s
    return free("내부 스키마 (저장장치의 관점)", b, subtitle="데이터가 디스크에 실제로 어떻게 저장되는지")


# ---------------------------------------------------------------- 사상(Mapping)
def mapping_slide():
    def b(ids):
        s = ""
        w, h = 4000000, 800000
        xs, ys = X0 + 200000, [1550000, 3050000, 4550000]
        names = [("외부 스키마", "의사 화면 · 원무팀 화면", "DEEAF6", "1F497D"),
                 ("개념 스키마", "환자 · 진료 · 처방 테이블", "FFF2CC", "BF9000"),
                 ("내부 스키마", "디스크의 파일 · 인덱스", "E2EFDA", "2C5F2D")]
        for y, (n, sub, fill, line) in zip(ys, names):
            s += box(ids, xs, y, w, h, [f"**{n}**", sub], sz=2000, fill=fill, line=line, geom="rect", lnSpc=110)
        # mapping arrows between layers
        for i, (lbl, desc) in enumerate([("외부 / 개념 사상", "화면의 항목 ↔ 테이블의 열을 이어 줌"),
                                         ("개념 / 내부 사상", "테이블 ↔ 실제 저장 위치를 이어 줌")]):
            ytop = ys[i] + h
            s += label_line(ids, xs + w // 2, ytop, xs + w // 2, ys[i + 1], color="C00000", lw=19050)
            s += textbox(ids, xs + w + 500000, ytop + 130000, 7800000, 700000,
                         para(f"**{lbl}**", sz=2400, color="C00000", lnSpc=110) +
                         para(desc, sz=2200, lnSpc=110), autofit=False)
        s += textbox(ids, X0, 5700000, W0, 1300000,
            para("예) 의사 화면의 ‘진단명’ 칸 = 진료 테이블의 **진단명** 열  ← 이 연결이 **외부 / 개념 사상**", sz=2100, lnSpc=125) +
            para("테이블 구조가 바뀌어도 **사상만 고치면** 화면은 그대로입니다. 그래서 데이터 독립성이 가능합니다.", sz=2100, b=True, lnSpc=125, color="1F3763"))
        return s
    return free("사상 (Mapping)", b, subtitle="세 단계를 이어 주는 연결 규칙")


# ---------------------------------------------------------------- 데이터 독립성 (비교)
def independence_why_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 700000,
            para("상황: 환자 테이블에 **‘알레르기’ 열을 하나 추가**한다면?", sz=2600, b=True, lnSpc=120))
        y = 2350000
        s += panel(ids, X0, y, 6000000, 2600000, "파일 시스템이라면", [
            "환자정보.xlsx 의 열이 바뀜",
            "- 그 파일을 읽던 프로그램을 모두 수정",
            "- 수정이 늦은 곳에서는 오류 발생",
            "- 데이터와 프로그램이 묶여 있음 = 종속성"], fill="FBE5E5", line="C00000")
        s += panel(ids, 7300000, y, 6000000, 2600000, "데이터베이스라면", [
            "환자 테이블에 열이 하나 늘어남",
            "- 원무팀 화면은 그대로 (그 열을 쓰지 않음)",
            "- 필요한 화면만 사상을 조정",
            "- 데이터와 프로그램이 분리됨 = 독립성"], fill="E2EFDA", line="2C5F2D")
        s += textbox(ids, X0, 5350000, W0, 1300000,
            para("**데이터 독립성** = 데이터의 구조가 바뀌어도 응용 프로그램(EMR 화면)은 바꾸지 않아도 되는 성질", sz=2200, lnSpc=125) +
            para("3단계 스키마와 사상으로 나누어 두었기 때문에 가능합니다.", sz=2200, lnSpc=125, color="1F3763"))
        return s
    return free("데이터 독립성이 왜 필요한가", b, subtitle="구조가 바뀌어도 화면은 그대로인 이유")


# ---------------------------------------------------------------- 데이터 사전 + 도식
def data_dictionary_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, 6000000, 4200000,
            para("① **메타데이터**: 데이터를 설명하는 데이터", sz=2400, lnSpc=140) +
            para("CT 영상에 붙어 있는 촬영일 · 장비 · 환자번호 (DICOM 헤더)", sz=2000, lvl=1, lnSpc=120) +
            para("테이블 이름, 열 이름, 데이터 타입, 키, 권한", sz=2000, lvl=1, lnSpc=120) +
            para("② **데이터 사전**: 메타데이터를 모아 둔 곳", sz=2400, lnSpc=140) +
            para("DBMS가 자동으로 만들고 관리", sz=2000, lvl=1, lnSpc=120) +
            para("{{시스템 카탈로그}}라고도 함", sz=2000, lvl=1, lnSpc=120) +
            para("③ **왜 중요한가**", sz=2400, lnSpc=140) +
            para("분석을 시작할 때 가장 먼저 봐야 하는 자료", sz=2000, lvl=1, lnSpc=120))
        xr = 6900000
        s += shape(ids, "roundRect", xr, 1550000, 6300000, 3350000, fill="FFFFFF", line="1F497D", lw=15875, name="DB Frame")
        s += textbox(ids, xr, 1650000, 6300000, 400000, para("**데이터베이스**", sz=2200, algn="ctr", color="1F497D", lnSpc=100), autofit=False)
        s += box(ids, xr + 300000, 2200000, 5700000, 1100000,
                 ["**실제 데이터 (인스턴스)**", "환자 · 진료 · 처방 · 검사 행"], sz=1900, fill="F2F2F2", line="7F7F7F", geom="rect", lnSpc=110)
        s += box(ids, xr + 300000, 3500000, 5700000, 1200000,
                 ["**데이터 사전 (메타데이터)**", "테이블 · 열 · 타입 · 키 · 제약조건 · 권한"], sz=1900, fill="FFF2CC", line="BF9000", geom="rect", lnSpc=110)
        s += textbox(ids, xr, 5050000, 6300000, 1200000,
            para("사용자가 SQL을 실행하면 DBMS는", sz=1900, lnSpc=115) +
            para("**데이터 사전을 먼저 확인**한 뒤 실제 데이터를 찾습니다.", sz=1900, b=True, lnSpc=115, color="1F3763"), autofit=False)
        return s
    return free("데이터 사전과 메타데이터", b, subtitle="테이블과 열에 대한 설명은 어디에 있을까?")


# ---------------------------------------------------------------- 3단계 스키마 (병원 예) — 층별로 다시 그림
def three_level_hospital_slide():
    """같은 병원 데이터를 세 층으로 나누어 본 그림.

    외부 스키마는 사용자마다 여러 개라서 카드를 따로 두고,
    개념 · 내부 스키마는 각각 하나뿐이라서 큰 상자 하나로 묶습니다.
    """
    LX, LW = X0, 2350000                      # 왼쪽 층 이름 칸
    CX, CW, GAP = 3400000, 2950000, 250000    # 오른쪽 예시 카드
    OUTX, OUTW = CX - 150000, 3 * CW + 2 * GAP + 300000   # 하나로 묶는 큰 상자
    def cx(i):
        return CX + i * (CW + GAP)

    def band_label(ids, y, h, name, sub, fill, line):
        return shape(ids, "roundRect", LX, y, LW, h, fill=fill, line=line, lw=19050,
                     text_xml=para(f"**{name}**", sz=2200, algn="ctr", lnSpc=105) +
                              para(sub, sz=1600, algn="ctr", lnSpc=105, color=GRAY),
                     name="Level")

    def gap_row(ids, y, label, why):
        s = arrow_down(ids, LX + LW // 2 - 300000, y, 600000, 380000)
        s += textbox(ids, CX, y, 9400000, 380000,
                     para(f"**{label}**  {why}", sz=2000, color="1F3763", lnSpc=105), autofit=False)
        return s

    def b(ids):
        # ── 1층: 외부 스키마 — 사용자마다 하나씩, 그래서 카드가 여러 개
        y1, h1 = 1520000, 1230000
        s = band_label(ids, y1, h1, "외부 스키마", "사용자마다 · 여러 개", "DEEAF6", "1F497D")
        for i, (who, cols) in enumerate([("의사 화면", ["환자명", "진단명", "처방약"]),
                                         ("원무팀 화면", ["환자명", "진료비", "검사내역"]),
                                         ("연구자 화면", ["연구용ID", "진단코드", "검사결과"])]):
            e, _ = entity_box(ids, cx(i), y1, CW, who, cols, key_idx=(),
                              fill="DEEAF6", line="1F497D", sz=1600, head_h=360000, row_h=290000)
            s += e
        s += gap_row(ids, 2800000, "논리적 독립성", "— 가운데 층이 바뀌어도 위의 화면은 그대로입니다")

        # ── 2층: 개념 스키마 — 병원 전체에 하나뿐이라 큰 상자 하나로
        yo2, ho2, y2 = 3250000, 1740000, 3400000
        s += band_label(ids, yo2, ho2, "개념 스키마", "조직 전체 · 하나", "FFF2CC", "BF9000")
        s += shape(ids, "roundRect", OUTX, yo2, OUTW, ho2, fill="FFFBF0", line="BF9000", lw=19050,
                   name="Conceptual")
        for i, (name, attrs) in enumerate([("환자", ["환자ID", "환자명", "생년월일", "성별"]),
                                           ("진료", ["진료ID", "환자ID (외래키)", "진료일", "진단명"]),
                                           ("처방", ["처방ID", "진료ID (외래키)", "약품명", "용량"])]):
            e, _ = entity_box(ids, cx(i), y2, CW, name, attrs,
                              fill="FFF2CC", line="BF9000", sz=1600, head_h=360000, row_h=270000)
            s += e
        s += gap_row(ids, 5060000, "물리적 독립성", "— 저장 방법이 바뀌어도 위의 표 구조는 그대로입니다")

        # ── 3층: 내부 스키마 — 이것도 하나뿐이라 큰 상자 하나로
        yo3, ho3, y3, h3 = 5500000, 1250000, 5650000, 950000
        s += band_label(ids, yo3, ho3, "내부 스키마", "저장장치 · 하나", "E2EFDA", "2C5F2D")
        s += shape(ids, "roundRect", OUTX, yo3, OUTW, ho3, fill="F4FAF0", line="2C5F2D", lw=19050,
                   name="Internal")
        for i, lines in enumerate([["**파일 위치와 이름**", "어느 디스크의 어느 파일에"],
                                   ["**인덱스**", "빨리 찾기 위한 색인"],
                                   ["**저장 형식**", "환자ID CHAR(4Byte), 압축"]]):
            s += box(ids, cx(i), y3, CW, h3, lines, sz=1700,
                     fill="E2EFDA", line="2C5F2D", lnSpc=125)

        s += textbox(ids, X0, 6850000, W0, 650000,
                     para("세 층으로 나누어 두었기 때문에, 한 층이 바뀌어도 다른 층은 그대로입니다.",
                          sz=2300, b=True, algn="ctr", lnSpc=115) +
                     para("외래키 = 다른 표를 가리키는 열 (5주차에서 자세히)",
                          sz=1700, algn="ctr", lnSpc=110, color=GRAY))
        return s
    return free("3단계 스키마 (병원 예)", b, subtitle="같은 데이터를 사용자 · 조직 전체 · 저장장치의 관점에서 봅니다")
