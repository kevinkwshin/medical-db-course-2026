# -*- coding: utf-8 -*-
"""6강. 모델링과 정규화 (원본 88~107번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)

SPAN = (88, 107)
TITLE = "6강. 모델링과 정규화"

AGENDA = [("데이터 모델링", "현실을 표로 옮기는 과정"),
          ("ERD", "개체 · 속성 · 관계 그리기"),
          ("이상현상", "표를 안 나누면 생기는 문제"),
          ("정규화", "1NF · 2NF · 3NF"),
          ("반정규화", "실무에서는 다시 합치기도"),
          ("정리", "용어와 요약")]

# 정규화 실습에 계속 쓰는 병원 예
RAW_HEAD = ["진료ID", "환자ID", "환자명", "담당의ID", "담당의명", "진단명", "검사항목"]
RAW_ROWS = [["V1001", "P001", "김OO", "D01", "박OO", "제2형 당뇨병", "혈당, 당화혈색소"],
            ["V1002", "P002", "이OO", "D02", "최OO", "고혈압", "혈압"],
            ["V1003", "P001", "김OO", "D01", "박OO", "고혈압", "혈압, 심전도"]]


def hospital_erd_slide():
    def b(ids):
        s = ""
        y0, ew, gap = 1800000, 2100000, 700000
        xs = X0 + 200000
        e1, h1 = entity_box(ids, xs, y0, ew, "환자", ["환자ID", "환자명", "생년월일", "성별"])
        e2, h2 = entity_box(ids, xs + ew + gap, y0, ew, "진료", ["진료ID", "환자ID", "진료일", "진단명"])
        e3, h3 = entity_box(ids, xs + 2 * (ew + gap), y0, ew, "처방", ["처방ID", "진료ID", "약품명", "용량"])
        e4, h4 = entity_box(ids, xs + ew + gap, y0 + h2 + 700000, ew, "검사", ["검사ID", "진료ID", "검사명", "결과값"])
        s += e1 + e2 + e3 + e4
        mid = y0 + h1 // 2
        s += label_line(ids, xs + ew, mid, xs + ew + gap, mid, label="1 : N")
        s += label_line(ids, xs + 2 * ew + gap, mid, xs + 2 * (ew + gap), mid, label="1 : N")
        s += label_line(ids, xs + ew + gap + ew // 2, y0 + h2, xs + ew + gap + ew // 2, y0 + h2 + 700000, label="1 : N")
        s += textbox(ids, 9000000, 1800000, 4300000, 3400000,
            para("**읽는 방법**", sz=2300, lnSpc=130) +
            para("환자 1명 → 진료 여러 건", sz=2000, lvl=1, lnSpc=125) +
            para("진료 1건 → 처방 여러 건", sz=2000, lvl=1, lnSpc=125) +
            para("진료 1건 → 검사 여러 건", sz=2000, lvl=1, lnSpc=125) +
            para("**연결하는 열**", sz=2300, lnSpc=130, spcBef=16) +
            para("진료의 환자ID = 외래키", sz=2000, lvl=1, lnSpc=125) +
            para("처방 · 검사의 진료ID = 외래키", sz=2000, lvl=1, lnSpc=125), autofit=False)
        s += textbox(ids, X0, 6200000, W0, 600000,
            para("이 그림 한 장이 병원 데이터베이스의 **개념 스키마**이자 **ERD**입니다. (4주차 복습)",
                 sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("병원 ERD 읽기", b, subtitle="화살표가 아니라 ‘몇 대 몇’을 먼저 봅니다")


def erd_symbol_slide():
    return table_slide("ERD 기호 읽는 법", "선 끝 모양만 알면 그림이 읽힙니다",
        ["선 끝 모양", "뜻", "병원 예"],
        [["세로줄 하나  |", "반드시 하나", "진료 한 건은 환자 한 명에게만 속한다"],
         ["세 갈래  (까마귀발)", "여럿", "환자 한 명에게 진료가 여러 건 있다"],
         ["동그라미  O", "없을 수도 있다", "아직 진료를 한 번도 안 받은 환자도 있다"],
         ["동그라미 + 세 갈래", "없거나 여럿", "검사를 하나도 안 한 진료도 있다"]],
        [3000000, 2600000, 6000000], sz=2000, row_h=680000, y=1750000,
        col_algn=["ctr", "ctr", "l"],
        note="표기법마다 모양은 조금씩 다릅니다. ‘하나인가 여럿인가’만 먼저 보면 됩니다.")


def mn_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, 6600000, 700000,
            para("환자 한 명이 검사 여러 개를 받고,\n같은 검사를 여러 환자가 받습니다 = **M : N**", sz=2200, lnSpc=118))
        y0, ew = 2450000, 2000000
        e1, h1 = entity_box(ids, X0, y0, ew, "환자", ["환자ID", "환자명"], sz=1500)
        e2, h2 = entity_box(ids, X0 + ew + 1000000, y0, ew, "검사항목", ["검사코드", "검사명"], sz=1500)
        s += e1 + e2
        s += label_line(ids, X0 + ew, y0 + h1 // 2, X0 + ew + 1000000, y0 + h1 // 2, label="M : N")
        s += textbox(ids, X0, y0 + max(h1, h2) + 200000, 5200000, 600000,
            para("M : N 은 표로 그대로 만들 수 없습니다.", sz=2000, b=True, color=RED, lnSpc=115), autofit=False)
        s += arrow_right(ids, 6150000, y0 + 400000, 650000, 750000)
        xr, ew2 = 7200000, 1700000
        xr2 = SLIDE_W - 250000 - ew2
        e3, h3 = entity_box(ids, xr, y0 - 100000, ew2, "환자", ["환자ID", "환자명"], sz=1500)
        e4, h4 = entity_box(ids, xr2, y0 - 100000, ew2, "검사항목", ["검사코드", "검사명"], sz=1500)
        xm = (xr + xr2 + ew2) // 2 - 950000
        e5, h5 = entity_box(ids, xm, y0 + 1500000, 1900000, "검사기록",
                            ["검사ID", "환자ID", "검사코드", "결과값"], sz=1500)
        s += e3 + e4 + e5
        s += label_line(ids, xr + ew2 // 2, y0 - 100000 + h3, xm + 500000, y0 + 1500000, label="1 : N")
        s += label_line(ids, xr2 + ew2 // 2, y0 - 100000 + h4, xm + 1400000, y0 + 1500000, label="1 : N")
        s += textbox(ids, xr, y0 + 1500000 + h5 + 160000, 6100000, 500000,
            para("가운데에 표를 하나 더 두면 1 : N 두 개가 됩니다.", sz=2000, b=True, color="2C5F2D", lnSpc=115), autofit=False)
        s += textbox(ids, X0, 6250000, W0, 600000,
            para("AACT의 conditions · facilities 테이블도 이렇게 가운데에서 연결해 주는 표입니다.",
                 sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("M : N 관계 풀기", b, subtitle="표 하나를 더 만들어 1 : N 두 개로 바꿉니다")


def anomaly_hospital_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("진료 · 환자 · 의사 · 검사를 **한 표에 다 넣으면** 어떤 일이 생길까요?", sz=2300, lnSpc=115))
        t, h = table(ids, X0, 2050000, [1300000, 1300000, 1300000, 1500000, 1500000, 2500000, 2800000],
                     [RAW_HEAD] + RAW_ROWS, sz=1600, row_h=480000, header_h=460000, algn="ctr")
        s += t
        y = 2050000 + h + 350000
        for i, (name, desc, fill, line) in enumerate([
                ("삽입 이상", "아직 진료를 한 적이 없는 새 의사(D03)를 등록하려면\n진료 기록이 없어 넣을 곳이 없다", *RED_PANEL),
                ("삭제 이상", "V1002 진료를 지우면\n의사 D02의 정보까지 함께 사라진다", *RED_PANEL),
                ("갱신 이상", "담당의명이 바뀌면 그 의사가 나오는\n모든 행을 빠짐없이 고쳐야 한다", *RED_PANEL)]):
            x = X0 + i * (4100000 + 100000)
            s += panel(ids, x, y, 4100000, 1650000, name, desc.split("\n"), fill=fill, line=line, sz=1800)
        s += textbox(ids, X0, y + 1800000, W0, 600000,
            para("이런 문제를 **이상현상(Anomaly)**이라 하고, 표를 나누어 해결하는 것이 **정규화**입니다.",
                 sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("이상현상 — 병원 예", b, subtitle="한 표에 모든 것을 담으면 생기는 세 가지 문제")


def nf1_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("**제1정규형**: 모든 칸에 값이 하나씩만 들어 있어야 한다 (원자성)", sz=2300, lnSpc=115))
        t1, h1 = table(ids, X0, 2100000, [1200000, 1200000, 2000000, 2000000],
            [["진료ID", "환자ID", "진단명", "검사항목"],
             ["V1001", "P001", "제2형 당뇨병", "혈당, 당화혈색소"],
             ["V1003", "P001", "고혈압", "혈압, 심전도"]], sz=1700, row_h=500000, algn="ctr")
        s += t1
        s += textbox(ids, X0, 2100000 + h1 + 150000, 6000000, 700000,
            para("검사항목 칸에 값이 두 개", sz=2000, b=True, color=RED, lnSpc=115) +
            para("“혈압 검사를 받은 진료 건수”를 셀 수 없습니다.", sz=1900, lnSpc=115, color=GRAY), autofit=False)
        s += arrow_right(ids, 7250000, 2800000, 500000, 700000)
        t2, h2 = table(ids, 7950000, 2100000, [1100000, 1100000, 1800000, 1500000],
            [["진료ID", "환자ID", "진단명", "검사항목"],
             ["V1001", "P001", "제2형 당뇨병", "혈당"],
             ["V1001", "P001", "제2형 당뇨병", "당화혈색소"],
             ["V1003", "P001", "고혈압", "혈압"],
             ["V1003", "P001", "고혈압", "심전도"]], sz=1700, row_h=500000, algn="ctr")
        s += t2
        s += textbox(ids, 7950000, 2100000 + h2 + 150000, 5300000, 700000,
            para("검사 하나당 한 행 → 제1정규형", sz=2000, b=True, color="2C5F2D", lnSpc=115) +
            para("이제 기본키는 (진료ID + 검사항목) 두 열의 조합입니다.", sz=1900, lnSpc=115, color=GRAY), autofit=False)
        s += textbox(ids, X0, 6250000, W0, 600000,
            para("EMR에서 내려받은 자료의 “쉼표로 이어 붙은 칸”이 바로 이 문제입니다. (12주차)",
                 sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("제1정규화 — 한 칸에 값 하나", b, subtitle="병원 예로 직접 해 보기")


def nf23_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 900000,
            para("**제2정규형**: 기본키의 **일부**에만 딸린 열을 떼어낸다 (부분 종속 제거)", sz=2200, lnSpc=120) +
            para("**제3정규형**: 기본키가 아닌 열에 딸린 열을 떼어낸다 (이행 종속 제거)", sz=2200, lnSpc=120))
        y = 2350000
        s += panel(ids, X0, y, 6000000, 2000000, "2정규화 — 부분 종속", [
            "기본키 = (진료ID + 검사항목)",
            "- 환자ID · 진단명은 진료ID만으로 정해짐",
            "- 검사항목과는 상관없음 → 따로 뗀다",
            "→ <진료> 와 <진료검사> 로 분리"], fill="FFF2CC", line="BF9000", sz=1800)
        s += panel(ids, 7300000, y, 6000000, 2000000, "3정규화 — 이행 종속", [
            "진료ID → 담당의ID → 담당의명",
            "- 담당의명은 기본키가 아닌 담당의ID에 딸림",
            "- 의사 정보가 진료마다 반복됨 → 따로 뗀다",
            "→ <의사> 테이블로 분리"], fill="DEEAF6", line="1F497D", sz=1800)
        s += textbox(ids, X0, y + 2200000, W0, 1300000,
            para("나눌 때 규칙: **딸린 열은 떼어 가고, 기준이 되는 열은 남겨서 연결 고리(외래키)로 쓴다**", sz=2300, b=True, lnSpc=120) +
            para("담당의ID는 진료 테이블에 남아 의사 테이블을 가리킵니다.", sz=2100, lnSpc=120, color="1F3763"))
        return s
    return free("제2 · 제3정규화", b, subtitle="딸려 있는 열을 떼어낸다")


def nf_result_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("앞의 한 표가 네 개로 나뉘었습니다. 필요할 때는 **JOIN**으로 다시 붙입니다 (8주차).", sz=2200, lnSpc=115))
        ew, gap, y0 = 2500000, 700000, 2050000
        xs = [X0 + 250000 + i * (ew + gap) for i in range(4)]
        hs = []
        for (name, attrs), x in zip([("환자", ["환자ID", "환자명", "생년월일"]),
                                     ("의사", ["담당의ID", "담당의명", "진료과"]),
                                     ("진료", ["진료ID", "환자ID", "담당의ID", "진단명"]),
                                     ("진료검사", ["진료ID", "검사항목", "결과값"])], xs):
            e, h = entity_box(ids, x, y0, ew, name, attrs, sz=1800, row_h=330000)
            s += e; hs.append(h)
        s += textbox(ids, xs[2], y0 + hs[2] + 120000, ew + 400000, 400000,
                     para("환자ID · 담당의ID = 외래키", sz=1600, b=True, color=RED, lnSpc=100), autofit=False)
        s += textbox(ids, xs[3], y0 + hs[3] + 120000, ew, 400000,
                     para("기본키 = 진료ID + 검사항목", sz=1500, b=True, color=RED, lnSpc=100), autofit=False)
        s += textbox(ids, X0, 4350000, W0, 1900000,
            para("**좋아진 점**", sz=2300, lnSpc=130) +
            para("환자명 · 담당의명이 한 곳에만 있어 고칠 때 한 번만 고치면 됨 (갱신 이상 해결)", sz=2000, lvl=1, lnSpc=125) +
            para("진료 기록이 없어도 의사를 등록할 수 있음 (삽입 이상 해결)", sz=2000, lvl=1, lnSpc=125) +
            para("진료를 지워도 의사 정보는 남음 (삭제 이상 해결)", sz=2000, lvl=1, lnSpc=125) +
            para("**대신 생기는 일**: 환자명까지 보려면 표를 연결(JOIN)해야 합니다.", sz=2100, lnSpc=125, color="1F3763", spcBef=12))
        return s
    return free("정규화 결과", b, subtitle="하나였던 표가 네 개로")


def denorm_cdw_slide():
    return two_panel_slide("CDW는 왜 넓은 표를 쓸까", "분석용 데이터베이스의 선택",
        "병원 운영 데이터베이스(EMR)와 분석용 데이터베이스(CDW)는 목적이 다릅니다.",
        ("운영 DB (EMR) — 정규화", ["입력과 수정이 계속 일어남",
                               "- 중복을 없애 잘못된 값을 막는 것이 우선",
                               "- 표가 잘게 나뉘어 있음",
                               "- 한 화면을 그리려면 여러 표를 연결"], "DEEAF6", "1F497D"),
        ("분석용 DB (CDW) — 반정규화", ["조회와 집계가 대부분, 수정은 거의 없음",
                                  "- 속도와 편의가 우선",
                                  "- 자주 쓰는 열을 미리 합쳐 둔 넓은 표",
                                  "- JOIN을 적게 해도 됨"], "E2EFDA", "2C5F2D"),
        note=["**반정규화** = 성능을 위해 일부러 중복을 허용하고 표를 합치는 것",
              "그래서 CDW에서는 같은 값이 여러 곳에 있을 수 있고, 어느 쪽이 최신인지 확인이 필요합니다. (11 · 12주차)"],
        y=2300000, h=2700000)



def _nf_overview(ids):
    rows = [["단계", "무엇을 없애나", "이 과목에서"],
            ["제1정규화", "한 칸에 값이 여러 개 들어간 것", "다룹니다"],
            ["제2정규화", "기본키의 일부에만 딸린 열", "다룹니다"],
            ["제3정규화", "일반 열에 딸려 있는 열", "다룹니다"],
            ["BCNF 이후", "드물게 남는 종속", "참고로만 봅니다"]]
    s, h = table(ids, X0 + 1100000, 2250000, [2500000, 5200000, 2600000], rows,
                 sz=1900, row_h=470000, header_h=450000, col_algn=["ctr", "l", "ctr"])
    s += textbox(ids, X0, 2250000 + h + 400000, W0, 500000,
                 para("앞 단계를 마쳐야 다음 단계로 넘어갑니다.", sz=2300, b=True, algn="ctr", lnSpc=115))
    return s

def build(c):
    c.set_layout(89, 2)
    c.retitle(89, title="데이터 모델링이란",
              replacements=[('<a:off x="648228" y="4001"/>', '<a:off x="806418" y="314526"/>'),
                            ('<a:off x="828830" y="1687293"/>', '<a:off x="828830" y="1830000"/>'),
                            ('<a:off x="1269162" y="1423092"/>', '<a:off x="1269162" y="1566000"/>'),
                            ('<a:off x="1239327" y="1948727"/>', '<a:off x="1239327" y="2091000"/>')])
    c.retitle(90, title="데이터베이스 설계 3단계", title_ext=(9000000, 558154))
    c.retitle(91, title="설계 3단계 — 한 그림으로", title_ext=(9000000, 558154))
    c.remove_tiny_pics(92, 250000)
    c.retitle(92, title="E-R 다이어그램 (ERD)", title_ext=(5600000, 558154), replacements=[
        ('<a:off x="3810999" y="451805"/><a:ext cx="3265822" cy="321382"/>',
         '<a:off x="8300000" y="430000"/><a:ext cx="4200000" cy="321382"/>'),
        ('<a:t>Entity-Relati</a:t>', '<a:t>Entity-Relationship</a:t>'),
        ('<a:t>nship</a:t>', '<a:t></a:t>'), ('\uf8ff', 'o'),
        ('<a:t>  </a:t>', '<a:t></a:t>'),
        ('<a:t>시각적</a:t>', '<a:t>시각적으로</a:t>'),
        ('<a:t>\t</a:t>', '<a:t></a:t>'), ('<a:t>로</a:t>', '<a:t></a:t>'),
        ('<a:off x="1242363" y="5599294"/><a:ext cx="5389324" cy="256480"/>',
         '<a:off x="1242363" y="5599294"/><a:ext cx="6300000" cy="256480"/>')])
    c.remove_tiny_pics(93, 250000)
    c.retitle(93, title="ERD 표기법", title_ext=(4200000, 558154), replacements=[
        ('<a:off x="3810999" y="451805"/><a:ext cx="3265822" cy="321382"/>',
         '<a:off x="8300000" y="430000"/><a:ext cx="4200000" cy="321382"/>'),
        ('<a:t>Entity-Relati</a:t>', '<a:t>Entity-Relationship</a:t>'),
        ('<a:t>nship</a:t>', '<a:t></a:t>'), ('\uf8ff', 'o'),
        ('<a:t>  </a:t>', '<a:t></a:t>')])
    c.retitle(94, title="개체와 속성", replacements=[
        ("<a:t>구분</a:t>", "<a:t>구분할</a:t>"), ("<a:t>할 수</a:t>", "<a:t>수</a:t>"),
        ("<a:t>로</a:t>", "<a:t>으로</a:t>")])
    c.retitle(95, title="관계와 차수 (1:1, 1:N, M:N)", replacements=[
        ("<a:t>1:M,</a:t>", "<a:t>1:N,</a:t>"), ("<a:t>[1:M</a:t>", "<a:t>[1:N</a:t>")])
    c.edit_shape_at(95, 4930986, 2354824, text="학과코드", ext=(900000, 252061))
    c.remove_tiny_pics(96, 250000)       # 낱글자 대신 넣어 둔 그림 (글자로 적습니다)
    c.retitle(96, title="ERD 연습 — 학생과 수강신청서", title_ext=(9500000, 558154), replacements=[
        ("<a:t>※</a:t>", "<a:t></a:t>"), ("<a:t>122회</a:t>", "<a:t></a:t>"),
        ("<a:t>정보관리기술사</a:t>", "<a:t></a:t>"), ("<a:t>기출</a:t>", "<a:t></a:t>"),
        ("<a:t>로</a:t>", "<a:t>으로</a:t>"),
        ("<a:t>\t</a:t>", "<a:t></a:t>"), ("<a:t>M</a:t>", "<a:t>N</a:t>"),
        ('<a:off x="541017" y="1215693"/><a:ext cx="7768891" cy="321382"/>',
         '<a:off x="541017" y="1215693"/><a:ext cx="8600000" cy="321382"/>')])
    c.retitle(98, title="이상현상 (Anomaly)")
    c.retitle(99, title="함수적 종속")
    c.append_shapes(99, lambda ids: textbox(ids, X0, 6050000, W0, 900000,
        para("**쉽게 말하면**  환자번호를 알면 환자명이 저절로 정해집니다. 이것을 **환자번호 → 환자명** 이라고 씁니다.",
             sz=2200, lnSpc=125, color="1F3763") +
        para("왼쪽이 **결정자**, 오른쪽이 **종속자**입니다. 거꾸로는 성립하지 않습니다.",
             sz=2200, lnSpc=125, color="1F3763")))
    # 제목 바로 아래에 단계 도형이 붙어 있어 부제를 넣을 자리가 없습니다 → 제목에 담습니다
    for n, t in [(100, "정규화의 단계 — 제1정규화부터 차례로"),
                 (101, "제1정규화 — 한 칸에 값이 여러 개인 경우"),
                 (102, "제2 · 제3정규화 — 부분 종속과 이행 종속 제거"),
                 (103, "BCNF — 시험 범위 밖, 참고로만 봅니다")]:
        c.set_layout(n, 2)              # 레이아웃5의 장식 사각형이 겹쳐 보여 레이아웃2로
        c.edit_shape_at(n, 648228, 235465, text=t, off=(806418, 314526), ext=(11500000, 541687))
        c.append_shapes(n, deco)
    c.append_shapes(100, _nf_overview)      # 단계 그림만 있어 비어 있던 자리를 채웁니다
    c.retitle(107, title="반정규화", replacements=[("<a:t>존재</a:t>", "<a:t>있음</a:t>")])
    c.append_shapes(107, lambda ids: textbox(ids, 948807, Y_SUB, 12000000, 354344,
        para("일부러 다시 합치는 경우", sz=2200, b=True, color=GREEN, lnSpc=100), autofit=False))

    # --- 도입
    c.add(cover(6, "모델링과 정규화",
                ["데이터 모델링과 ERD", "이상현상과 함수적 종속", "제1 · 제2 · 제3정규화, 반정규화"],
                "2026. 10. 20."))
    c.add(content("지난시간 리뷰", [
        ("**관계형 데이터베이스** = 데이터를 표로 저장하고 관계로 연결", dict(lvl=1, marL=457200, indent=-457200)),
        ("**기본키** = 행을 유일하게 찾는 열,  **외래키** = 다른 표를 가리키는 열", dict(lvl=1, marL=457200, indent=-457200)),
        ("**무결성 제약조건** = 개체 · 참조 · 도메인", dict(lvl=1, marL=457200, indent=-457200)),
        ("테이블의 특성 중 **원자성**: 한 칸에는 값 하나만", dict(lvl=1, marL=457200, indent=-457200)),
        ("그런데 **표를 어떻게 나눌지**는 누가 정할까요?", dict(b=True, algn="ctr", color=BLUE, spcBef=24)),
        ("오늘 배우는 모델링과 정규화가 그 방법입니다.", dict(b=True, algn="ctr", color=BLUE)),
    ]))
    c.add(objectives_slide(6,
        ["ERD를 보고 어떤 표가 어떻게 연결되는지 읽을 수 있다",
         "한 표에 다 담으면 생기는 이상현상 세 가지를 설명할 수 있다",
         "제1 · 제2 · 제3정규화가 무엇을 떼어내는지 말할 수 있다",
         "CDW가 왜 넓은 표를 쓰는지 설명할 수 있다"],
        AGENDA, subtitle="현실의 정보를 어떤 표로 나눌지 정하는 방법",
        date_note="오늘 나누는 연습이 8주차 JOIN과 11주차 CDW 구조 이해의 바탕이 됩니다"))

    # --- 1. 데이터 모델링
    c.add(section_slide(1, AGENDA, lead="현실에 있는 정보를 어떻게 표로 옮길까요?"))
    c.keep(89); c.keep(90); c.keep(91)

    # --- 2. ERD
    c.add(section_slide(2, AGENDA, lead="설계도를 그리는 약속된 표기법"))
    c.keep(92); c.keep(93); c.keep(94); c.keep(95)
    c.add(hospital_erd_slide())
    c.add(erd_symbol_slide())
    c.add(mn_slide())
    c.keep(96)
    c.add(checkpoint_slide(
        ["**모델링** = 현실의 정보를 표와 관계로 옮기는 과정",
         "**ERD** = 개체(표) · 속성(열) · 관계(몇 대 몇)를 그린 설계도",
         "**M : N** 관계는 가운데 표를 하나 더 두어 1 : N 두 개로 푼다"],
        question="환자와 진료는 몇 대 몇 관계일까요?",
        answer="1 : N 입니다. 환자 한 명이 진료를 여러 번 받기 때문입니다."))

    # --- 3. 이상현상
    c.add(section_slide(3, AGENDA, lead="표를 나누지 않으면 무슨 일이 생기는지 먼저 봅니다"))
    c.keep(98)
    c.add(anomaly_hospital_slide())
    c.keep(99)

    # --- 4. 정규화
    c.add(section_slide(4, AGENDA, lead="이상현상을 없애기 위해 표를 단계적으로 나눕니다"))
    c.keep(100); c.keep(101)
    c.add(nf1_slide())
    c.keep(102)
    c.add(nf23_slide())
    c.add(nf_result_slide())
    c.keep(103)
    c.add(checkpoint_slide(
        ["**1정규화** = 한 칸에 값 하나 (원자성)",
         "**2정규화** = 기본키의 일부에만 딸린 열을 분리 (부분 종속)",
         "**3정규화** = 기본키가 아닌 열에 딸린 열을 분리 (이행 종속)"],
        question="담당의ID → 담당의명 은 어떤 종속일까요?",
        answer="이행 종속입니다. 담당의명이 기본키가 아닌 담당의ID에 딸려 있어 3정규화 대상입니다."))

    # --- 5. 반정규화
    c.add(section_slide(5, AGENDA, lead="정규화가 항상 정답은 아닙니다"))
    c.keep(107)
    c.add(denorm_cdw_slide())
    c.add(quiz("정규화", "다음 중 제3정규화로 해결하는 문제는?",
               ["한 칸에 값이 여러 개 들어 있다", "기본키의 일부에만 딸린 열이 있다",
                "기본키가 아닌 열에 딸린 열이 있다", "표가 너무 많이 나뉘어 조회가 느리다"],
               answer=2, note="① 1정규화, ② 2정규화, ➃ 반정규화로 다룹니다."))

    # --- 6. 정리
    c.add(section_slide(6, AGENDA, lead="오늘 나온 용어와 핵심을 다시 짚습니다"))
    c.add(terms_slide(6, [
        ["모델링", "Data Modeling", "현실의 정보를 표와 관계로 옮기는 과정"],
        ["개체", "Entity", "표로 만들 대상. 환자, 진료, 의사"],
        ["속성", "Attribute", "개체가 가지는 항목. 환자명, 진료일"],
        ["관계", "Relationship", "개체 사이의 연결. 1:1, 1:N, M:N"],
        ["ERD", "E-R Diagram", "개체 · 속성 · 관계를 그린 설계도"],
        ["이상현상", "Anomaly", "표를 안 나눠서 생기는 삽입 · 삭제 · 갱신 문제"],
        ["함수적 종속", "Functional Dependency", "한 열의 값이 정해지면 다른 열이 따라 정해지는 관계"],
        ["정규화", "Normalization", "이상현상을 없애려고 표를 나누는 작업"],
        ["반정규화", "Denormalization", "성능을 위해 일부러 합치고 중복을 허용하는 작업"],
    ]))
    c.add(summary(6, [
        "**ERD**로 개체 · 속성 · 관계를 그린 뒤 표로 옮긴다",
        "**정규화** = 딸린 열을 떼어 표를 나누는 것 (1NF · 2NF · 3NF)",
        "**CDW는 반정규화**된 넓은 표라서 중복을 확인해야 한다",
    ], sz=2800, lnSpc=170, next_week="7강. SQL (1) — SELECT · FROM · WHERE, 실습 시작"))
