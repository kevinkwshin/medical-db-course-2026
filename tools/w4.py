# -*- coding: utf-8 -*-
"""4강. 데이터베이스 시스템 (원본 53~77번 자리를 대체, 32장)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)
from w4_parts import (conceptual_schema_slide, internal_schema_slide, mapping_slide,
                      independence_why_slide, data_dictionary_slide, three_level_hospital_slide)

SPAN = (53, 77)
TITLE = "4강. 데이터베이스 시스템"


def hospital_systems_slide():
    def b(ids):
        s = ""
        systems = [("EMR", "전자의무기록"), ("OCS", "처방전달"), ("LIS", "검사정보"), ("PACS", "의료영상"), ("원무 · 보험", "수납 · 청구")]
        w, gap, y, h = 2200000, 250000, 1800000, 950000
        for i, (a, bb) in enumerate(systems):
            x = X0 + i * (w + gap)
            s += box(ids, x, y, w, h, [f"**{a}**", bb], sz=2000, fill="DEEAF6", line="1F497D")
            s += arrow_down(ids, x + w // 2 - 250000, y + h + 120000, 500000, 420000)
        wide = 5 * w + 4 * gap
        s += box(ids, X0, 3350000, wide, 850000, ["**각 시스템의 운영 데이터베이스** (진료 · 처방 · 검사 · 영상 · 수납 데이터)"],
                 sz=2200, fill="FFF2CC", line="BF9000")
        s += arrow_down(ids, X0 + wide // 2 - 250000, 4320000, 500000, 420000)
        s += box(ids, X0, 4850000, wide, 900000, ["**CDW (임상데이터웨어하우스)** = 분석 · 연구용으로 모아 둔 데이터베이스 (11주차)"],
                 sz=2200, fill="E2EFDA", line="2C5F2D")
        s += textbox(ids, X0, 6100000, W0, 700000,
            para("병원의 모든 화면 뒤에는 데이터베이스가 있습니다. 그 전체를 **데이터베이스 시스템**이라고 부릅니다.",
                 sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("병원 정보시스템과 데이터베이스", b, subtitle="우리가 쓰는 시스템 하나하나가 데이터베이스 위에서 움직입니다")


def component_tree():
    def b(ids):
        s = ""
        c1x, c1w, c2x, c2w, c3x, c3w = X0, 2600000, 4300000, 3000000, 8300000, 2500000
        h2, h3, gap3 = 600000, 360000, 60000
        lvl2 = [("데이터베이스", 1550000, []), ("DBMS", 2250000, []),
                ("스키마", None, ["외부 스키마", "개념 스키마", "내부 스키마"]),
                ("데이터베이스 사용자", None, ["일반 사용자", "응용 프로그래머", "SQL 사용자", "데이터베이스 관리자(DBA)"]),
                ("데이터베이스 언어", None, ["DDL (정의)", "DML (조작)", "DCL (제어)"])]
        y3, centers = 2950000, []
        for name, y2, kids in lvl2:
            if kids:
                ys = [y3 + i * (h3 + gap3) for i in range(len(kids))]
                cy = (ys[0] + ys[-1] + h3) // 2
                y2 = cy - h2 // 2
                for k, yk in zip(kids, ys):
                    s += box(ids, c3x, yk, c3w, h3, [k], sz=1600, fill="F2F2F2", line="7F7F7F", geom="rect", lnSpc=100)
                    s += connector(ids, c2x + c2w, cy, c3x, yk + h3 // 2, color="7F7F7F", lw=12700, arrow=False)
                y3 = ys[-1] + h3 + 220000
            else:
                cy = y2 + h2 // 2
            s += box(ids, c2x, y2, c2w, h2, [f"**{name}**"], sz=2000, fill="DEEAF6", line="1F497D", geom="rect", lnSpc=100)
            centers.append(cy)
        root = (centers[0] + centers[-1]) // 2
        s += box(ids, c1x, root - 400000, c1w, 800000, ["**데이터베이스 시스템**", "(DBS)"],
                 sz=2000, fill="1F497D", line="1F497D", geom="rect", color="FFFFFF", lnSpc=100)
        for cy in centers:
            s += connector(ids, c1x + c1w, root, c2x, cy, color="1F497D", lw=15875, arrow=False)
        return s
    return free("데이터베이스 시스템의 구성", b, subtitle="오늘 배울 다섯 가지를 한 그림으로")


def dbms_inside_slide():
    def b(ids):
        s = step_row(ids, X0, 1650000, W0, 1000000,
                     [("사용자", "SQL 요청"), ("질의 처리기", "요청을 해석"), ("저장 데이터 관리자", "데이터를 찾아옴"), ("데이터베이스", "실제 저장")], sz=1900)
        rows = [["질의 처리기\n(Query Processor)", "SQL 문장을 해석하고, 어떻게 찾을지 계획을 세움", "원무 접수 창구"],
                ["저장 데이터 관리자\n(Storage Manager)", "디스크에서 실제 데이터를 찾아 가져오고 저장함", "의무기록실 담당자"],
                ["트랜잭션 관리자", "여러 사람이 동시에 써도 데이터가 어긋나지 않게 함", "전체를 조율하는 관리자"]]
        t, h = table(ids, X0, 3150000, [3300000, 5900000, 3200000], [["구성", "하는 일", "병원에 비유하면"]] + rows,
                     sz=1900, row_h=760000, header_h=500000, col_algn=["ctr", "l", "ctr"])
        s += t
        s += textbox(ids, X0, 3150000 + h + 350000, W0, 700000,
            para("우리가 SQL 한 줄을 실행하면 이 세 부분이 순서대로 움직입니다. 트랜잭션은 10주차에서 자세히 다룹니다.",
                 sz=2200, b=True, algn="ctr", lnSpc=115))
        return s
    return free("DBMS 안에서는 무슨 일이 일어날까", b, subtitle="SQL 한 줄이 처리되는 과정")


def schema_instance_hospital():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, 5900000, 4500000,
            para("① **스키마(Schema)**", sz=2600, lnSpc=140) +
            para("데이터베이스의 구조: 어떤 테이블에 어떤 열이 있고, 각 열의 타입은 무엇인지", sz=2200, lvl=1, lnSpc=130) +
            para("설계할 때 정해지고, 그 뒤에는 거의 바뀌지 않음", sz=2200, lvl=1, lnSpc=130) +
            para("② **인스턴스(Instance)**", sz=2600, lnSpc=140, spcBef=12) +
            para("어느 시점에 실제로 저장되어 있는 값", sz=2200, lvl=1, lnSpc=130) +
            para("환자가 등록되고 진료가 쌓일 때마다 계속 바뀜", sz=2200, lvl=1, lnSpc=130))
        xr = 7300000
        s += textbox(ids, xr, 1500000, 5800000, 400000, para("**스키마** = 틀 (거의 변하지 않음)", sz=2200, color=BLUE, lnSpc=100), autofit=False)
        t1, _ = table(ids, xr, 1950000, [1200000, 1700000, 900000, 2000000],
                      [["환자ID", "환자명", "나이", "연락처"], ["CHAR(10)", "VARCHAR(20)", "INT", "CHAR(13)"]],
                      sz=1600, row_h=450000, algn="ctr", col_font={i: "Courier New" for i in range(4)})
        s += t1
        s += textbox(ids, xr, 3450000, 5800000, 400000, para("**인스턴스** = 지금 들어 있는 값 (자주 변함)", sz=2200, color=BLUE, lnSpc=100), autofit=False)
        t2, _ = table(ids, xr, 3900000, [1200000, 1700000, 900000, 2000000],
                      [["환자ID", "환자명", "나이", "연락처"], ["P001", "김OO", "72", "010-XXXX-XXXX"],
                       ["P002", "이OO", "58", "010-XXXX-XXXX"], ["P003", "박OO", "65", "010-XXXX-XXXX"]],
                      sz=1800, row_h=450000, algn="ctr")
        s += t2
        s += textbox(ids, X0, 6250000, W0, 650000,
            para("같은 틀(스키마)에 환자가 한 명 등록될 때마다 행(인스턴스)이 하나 늘어납니다.", sz=2400, b=True, algn="ctr", lnSpc=120) +
            para("CHAR · VARCHAR = 글자, INT = 숫자. 값의 종류를 정해 두는 것이며 5주차에서 자세히 봅니다.",
                 sz=1700, algn="ctr", lnSpc=110, color=GRAY))
        return s
    return free("스키마와 인스턴스", b, subtitle="스키마 = 틀,  인스턴스 = 틀 안에 들어 있는 현재 값")


def schema_instance_aact():
    def b(ids):
        s = textbox(ids, X0, 1550000, 6000000, 400000, para("**스키마** = 틀 (거의 변하지 않음)", sz=2200, color=BLUE, lnSpc=100), autofit=False)
        t1, h1 = table(ids, X0, 2000000, [2100000, 1700000, 2200000],
                       [["열 이름", "데이터 타입", "뜻"], ["nct_id", "VARCHAR", "임상시험 등록번호"],
                        ["brief_title", "VARCHAR", "시험 제목"], ["start_date", "DATE", "시작일"],
                        ["enrollment", "INTEGER", "등록 인원"], ["phase", "VARCHAR", "임상 단계"]],
                       sz=1800, row_h=450000, col_algn=["l", "ctr", "l"], col_font={0: "Courier New", 1: "Courier New"})
        s += t1
        xr = 7150000
        s += textbox(ids, xr, 1550000, 6000000, 400000, para("**인스턴스** = 지금 들어 있는 값 (계속 바뀜)", sz=2200, color=BLUE, lnSpc=100), autofit=False)
        t2, h2 = table(ids, xr, 2000000, [1500000, 2000000, 1250000, 1250000],
                       [["nct_id", "brief_title", "start_date", "enrollment"],
                        ["NCT04280705", "Adaptive COVID-19 Treatment Trial", "2020-02-21", "1062"],
                        ["NCT04368728", "Safety, Tolerability … of RNA Vaccine", "2020-04-29", "44047"],
                        ["NCT04470427", "Efficacy, Safety … of mRNA-1273", "2020-07-27", "30420"]],
                       sz=1500, row_h=675000, col_algn=["ctr", "l", "ctr", "ctr"])
        s += t2
        y_cap = 2000000 + max(h1, h2) + 150000
        s += textbox(ids, X0, y_cap, 6000000, 400000, para("스키마: 열 이름과 타입만 정해져 있음", sz=1800, lnSpc=100, color=GRAY), autofit=False)
        s += textbox(ids, xr, y_cap, 6000000, 400000, para("인스턴스: 임상시험 1건 = 1행 (값은 예시)", sz=1800, lnSpc=100, color=GRAY), autofit=False)
        s += textbox(ids, X0, 6100000, W0, 500000,
            para("같은 틀(스키마)에 새 임상시험이 등록될 때마다 행(인스턴스)이 늘어납니다.", sz=2400, b=True, algn="ctr", lnSpc=120))
        return s
    return free("스키마와 인스턴스 — AACT로 보기", b, subtitle="7주차부터 쓸 studies 테이블로 보면")


def user_cards():
    items = [("일반 사용자", "End User", "F2F2F2", "프로그램 화면을 통해 데이터를 조회 · 입력. SQL을 몰라도 사용 가능", "병원: 의사 · 간호사 · 원무팀 (EMR 화면)"),
             ("응용 프로그래머", "Application Programmer", "FFF2CC", "화면과 기능을 만드는 프로그램을 개발. 프로그램 안에서 SQL을 작성", "병원: EMR · OCS 개발자"),
             ("SQL 사용자", "SQL User", "DEEAF6", "SQL을 직접 작성해 데이터를 검색하고 통계를 냄. 읽기 권한 중심", "병원: 연구자 · QI 담당자 · 분석 담당  ← 이 수업의 목표"),
             ("데이터베이스 관리자", "DBA", "E2EFDA", "설계 · 계정과 권한 · 백업 · 성능 · 장애 복구 등 데이터베이스 전체를 책임", "병원: 의료정보팀 DB 관리자")]
    def b(ids):
        s, y, h, gap = "", 1500000, 1120000, 130000
        for name, en, fill, desc, hosp in items:
            s += shape(ids, "roundRect", X0, y, W0, h, fill=None, line="BFBFBF", lw=9525, name="Card")
            s += box(ids, X0 + 120000, y + 160000, 2700000, h - 320000, [f"**{name}**", en], sz=1800, fill=fill, line=None, geom="rect")
            s += textbox(ids, X0 + 3000000, y + 90000, W0 - 3200000, h - 150000,
                         para(desc, sz=2000, lnSpc=120) + para(hosp, sz=2000, lnSpc=120, color="1F3763"),
                         autofit=False, anchor="ctr")
            y += h + gap
        s += textbox(ids, X0, 6350000, W0, 500000,
            para("이 수업의 목표 = SQL 사용자로서 필요한 데이터를 직접 조회하고 검산하는 것", sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("데이터베이스 사용자 네 가지", b, subtitle="누가 데이터베이스를 어떻게 쓰는가")


def independence_table():
    def fig(ids, y_end):
        s, y, w, h = "", y_end + 350000, 2200000, 520000
        xs = [X0 + 700000, X0 + 4900000, X0 + 9100000]
        for x, name, fill in zip(xs, ["외부 스키마", "개념 스키마", "내부 스키마"], ["DEEAF6", "FFF2CC", "E2EFDA"]):
            s += box(ids, x, y, w, h, [f"**{name}**"], sz=1800, fill=fill, line="7F7F7F", geom="rect", lnSpc=100)
        s += connector(ids, xs[0] + w, y + h // 2, xs[1], y + h // 2, color="1F497D", lw=15875, arrow=False)
        s += connector(ids, xs[1] + w, y + h // 2, xs[2], y + h // 2, color="1F497D", lw=15875, arrow=False)
        s += textbox(ids, xs[0] + w, y - 420000, xs[1] - xs[0] - w, 400000,
                     para("논리적 독립성", sz=1800, b=True, algn="ctr", color=BLUE, lnSpc=100), autofit=False)
        s += textbox(ids, xs[1] + w, y - 420000, xs[2] - xs[1] - w, 400000,
                     para("물리적 독립성", sz=1800, b=True, algn="ctr", color=RED, lnSpc=100), autofit=False)
        return s
    return table_slide("논리적 독립성과 물리적 독립성", "무엇이 바뀌어도 무엇은 그대로인가",
        ["구분", "무엇이 바뀌어도", "무엇은 그대로", "병원 예"],
        [["논리적 독립성", "개념 스키마", "외부 스키마\n(사용자 화면)", "환자 테이블에 ‘알레르기’ 열을 추가해도\n원무팀 화면은 그대로"],
         ["물리적 독립성", "내부 스키마", "개념 스키마\n(테이블 구조)", "서버 디스크를 바꾸거나 인덱스를 추가해도\n테이블 구조는 그대로"]],
        [2300000, 2300000, 2600000, 5200000], sz=2000, row_h=880000, y=1600000,
        col_algn=["ctr", "ctr", "ctr", "l"], extra=fig,
        note="기억법: 외부 ↔ 개념 = 논리적,  개념 ↔ 내부 = 물리적", note_style="footnote")


AGENDA = [("데이터베이스 시스템", "구성 요소 5가지"), ("스키마와 인스턴스", "틀과 값"),
          ("3단계 스키마", "외부 · 개념 · 내부"), ("사상과 데이터 독립성", "구조가 바뀌어도"),
          ("데이터 사전", "분석의 출발점"), ("데이터베이스 사용자", "누가 어떻게 쓰는가")]


def build(c):
    # 기존 슬라이드 손보기
    c.remove_offslide(62)
    c.retitle(55, title="스키마 미리 보기")
    c.append_shapes(55, lambda ids: textbox(ids, 563032, 5150000, 4600000, 900000,
        para("오른쪽 그림: **AACT 데이터베이스의 스키마** (테이블과 테이블 사이의 관계).\n오늘 배우는 ‘스키마’의 실제 예입니다.",
             sz=2000, lnSpc=120, color="1F3763")))
    c.retitle(56, replacements=[('sz="2000"', 'sz="2400"'), ('sz="1050"', 'sz="1200"'),
        ('<a:off x="8944980" y="3872842"/><a:ext cx="1490980" cy="428625"/>', '<a:off x="8690000" y="3872842"/><a:ext cx="2000000" cy="428625"/>'),
        ('<a:off x="8707237" y="4709519"/><a:ext cx="1990725" cy="428625"/>', '<a:off x="8450000" y="4709519"/><a:ext cx="2500000" cy="428625"/>'),
        ('<a:off x="10135352" y="3286484"/><a:ext cx="427990" cy="186690"/>', '<a:off x="10000000" y="3266484"/><a:ext cx="700000" cy="260000"/>')])
    c.retitle(74, title="3단계 스키마 (전체 구조)")

    # --- 도입
    c.add(cover(4, "데이터베이스 시스템",
                ["데이터베이스 시스템의 구성 요소", "스키마 · 3단계 구조 · 데이터 독립성", "데이터 사전과 데이터베이스 사용자"],
                "2026. 9. 29."))
    c.add(content("지난시간 리뷰", [
        ("**DBMS의 주요 기능**: 저장 · 검색 · 추가/수정/삭제 · 여러 사용자 지원 · 보안 · 무결성", dict(lvl=1, marL=457200, indent=-457200)),
        ("**SQL의 3가지 종류**", dict(lvl=1, marL=457200, indent=-457200)),
        ("DDL = 구조를 만든다 (CREATE, ALTER, DROP)", dict(lvl=2, sz=2400)),
        ("DML = 데이터를 다룬다 (SELECT, INSERT, UPDATE, DELETE)", dict(lvl=2, sz=2400)),
        ("DCL = 접근 권한을 관리한다 (GRANT, REVOKE)", dict(lvl=2, sz=2400)),
        ("평소에는 **EMR 프로그램**이 의료진의 요청을 SQL로 바꾸어 DBMS에 전달", dict(lvl=1, marL=457200, indent=-457200)),
        ("연구 · 통계를 위해서는 **직접 SQL**로 데이터베이스에서 조회", dict(lvl=1, marL=457200, indent=-457200)),
        ("먼저 지난주에 나온 질문부터 보겠습니다.", dict(b=True, algn="ctr", color=BLUE, spcBef=18)),
    ]))

    # --- 지난주 질문: SQL 호환성 (병원 DB 교체 사례)
    c.add(two_panel_slide(
        "지난주 질문 — SQL도 제품마다 다른가요?",
        "병원 데이터베이스를 바꿨을 때 생기는 일",
        "새 제품으로 바꾼 뒤 통계 쿼리에서 오류가 나, 한 달간 손으로 통계를 냈습니다.",
        ("왜 이런 일이 생기나",
         ["SQL에 표준은 있지만 제품마다 조금씩 다릅니다",
          "- 표준에 없는 기능을 따로 만들어 씀",
          "- 같은 일을 적는 법이 다름",
          "- 예전 문법은 새 제품에서 안 됨",
          "- 자료형 이름도 다름"], *RED_PANEL),
        ("옮길 때 덜 고생하려면",
         ["표준 문법(JOIN · CASE · COALESCE)을 먼저 씁니다",
          "- 제품 고유 함수는 한곳에 모아 관리",
          "- 바꾸기 전에 쓰던 쿼리와 그때의 건수를 적어 둠",
          "- 바꾼 뒤 같은 숫자가 나오는지 대조",
          "- 손으로 적기 전에 담당 부서에 변환을 요청"], *GREEN_PANEL),
        note=["**SELECT · FROM · WHERE · GROUP BY · JOIN 같은 뼈대는 거의 모든 제품에서 같습니다.**",
              "“그럼 이건 어느 층의 오류인가?” — 오늘 4번 구간(사상과 데이터 독립성)에서 다시 답합니다."],
        y=2250000, h=2300000))
    c.add(table_slide("같은 일, 제품마다 다른 문장", "자주 부딪히는 다섯 가지",
        ["하려는 일", "Oracle", "SQL Server", "PostgreSQL · MySQL"],
        [["상위 5행만 보기", "ROWNUM <= 5", "TOP 5", "LIMIT 5"],
         ["빈 값 대신 0 넣기", "NVL(값, 0)", "ISNULL(값, 0)", "COALESCE(값, 0)"],
         ["오늘 날짜", "SYSDATE", "GETDATE()", "CURRENT_DATE"],
         ["글자 잇기", "성 || 이름", "성 + 이름", "CONCAT(성, 이름)"],
         ["문자 자료형", "VARCHAR2(20)", "VARCHAR(20)", "VARCHAR(20)"]],
        [2700000, 2600000, 2600000, 3300000], sz=1800, row_h=560000, y=1700000,
        col_algn=["l", "l", "l", "l"], col_font={1: "Courier New", 2: "Courier New", 3: "Courier New"},
        note="COALESCE 는 세 제품 모두에서 됩니다. 표준을 쓰면 옮길 때 고칠 일이 줄어듭니다."))
    c.keep(55)
    c.add(objectives_slide(4,
        ["데이터베이스 시스템이 무엇으로 이루어지는지 말할 수 있다",
         "스키마와 인스턴스를 구분할 수 있다",
         "3단계 스키마와 사상이 데이터 독립성을 어떻게 만드는지 설명할 수 있다",
         "데이터 사전을 보고 분석을 시작할 수 있다"],
        AGENDA,
        subtitle="데이터베이스 시스템의 구성 요소를 하나씩 살펴봅니다",
        date_note="실습 데이터: AACT (임상시험 등록 데이터) — 7주차부터 직접 조회합니다"))

    # --- 1. 데이터베이스 시스템
    c.add(section_slide(1, AGENDA, lead="병원 정보시스템은 무엇으로 이루어져 있을까요?"))
    c.add(hospital_systems_slide())
    c.add_subtitle(56, "다섯 가지를 묶어 부르는 이름")
    c.keep(56)
    c.add(table_slide("구성 요소를 병원에 대응해 보면", "무엇이 무엇에 해당할까요?",
        ["구성 요소", "뜻", "병원에서는"],
        [["데이터베이스", "실제 데이터가 저장된 곳", "환자 · 진료 · 처방 · 검사 데이터"],
         ["DBMS", "데이터베이스를 관리하는 프로그램", "Oracle, MS SQL Server, PostgreSQL 등"],
         ["스키마", "데이터베이스의 구조 (설계도)", "환자 테이블에 어떤 열이 있는지"],
         ["사용자", "데이터를 이용하는 사람", "의사 · 간호사 · 원무팀 · 연구자 · 의료정보팀"],
         ["데이터베이스 언어", "DBMS에게 요청하는 언어", "SQL (대부분 EMR 프로그램이 대신 작성)"]],
        [2500000, 4500000, 5300000], col_algn=["ctr", "l", "l"], row_h=620000,
        note="이 다섯 가지를 오늘 하나씩 살펴봅니다."))
    c.add(component_tree())
    c.add(dbms_inside_slide())

    # --- 2. 스키마와 인스턴스
    c.add(section_slide(2, AGENDA, lead="‘틀’과 ‘그 안에 들어 있는 값’을 나누어 봅니다"))
    c.add(schema_instance_hospital())
    c.add(schema_instance_aact())
    c.add(quiz("스키마와 인스턴스", "다음 중 스키마(schema)에 해당하는 것은?",
               ["P001 / 김OO / 72 / 010-XXXX-XXXX", "환자(환자ID, 환자명, 나이, 연락처)", "SELECT * FROM 환자;", "의료정보팀 DB 관리자"],
               answer=1, note="스키마는 데이터가 들어갈 틀(구조)이고, ①은 인스턴스(실제 값)입니다."))

    # --- 3. 3단계 스키마
    c.add(section_slide(3, AGENDA, lead="하나의 데이터베이스를 세 가지 관점에서 봅니다"))
    c.add(content("3단계 스키마", [
        ("① 의사는 **진료 화면**에서 환자명, 진단명, 처방약을 봅니다.", dict()),
        ("② 원무팀은 **수납 화면**에서 환자명, 진료비, 검사내역을 봅니다.", dict()),
        ("③ 연구자는 **이름 없는 연구용 ID**로 진단과 검사결과만 봅니다.", dict()),
        ("④ 그런데 서버에는 **하나의 데이터베이스**만 있습니다.", dict()),
        ("→ 사용자가 보는 모습, 병원 전체의 설계도, 실제 저장 방법을 나누어 생각하면 관리가 쉬워집니다.", dict(color="1F3763", spcBef=18)),
        ("{{외부 스키마 · 개념 스키마 · 내부 스키마}}", dict(b=True, algn="ctr", sz=3200, spcBef=18)),
    ], subtitle="하나의 데이터베이스를 세 가지 관점에서 봅니다"))
    c.add(three_level_hospital_slide())
    c.keep(74)
    c.add(table_slide("외부 스키마 (사용자 관점)", "같은 데이터베이스라도 사용자마다 보이는 부분이 다릅니다",
        ["사용자", "화면에서 보는 항목", "보지 못하는 항목"],
        [["의사", "환자명, 진단명, 처방약", "진료비, 수납 내역"],
         ["원무팀", "환자명, 진료비, 검사내역", "진단명 상세"],
         ["연구자", "연구용 ID, 진단코드, 검사결과", "이름, 연락처 (개인정보)"]],
        [2200000, 5300000, 4700000], col_algn=["ctr", "l", "l"], sz=2200, row_h=760000, y=1800000,
        note="외부 스키마 = 서브 스키마 = 뷰(View).  사용자마다 필요한 부분만 보여 줍니다."))
    c.add(sql_example("외부 스키마 만들기 — 뷰(View)", "연구자용 화면은 이렇게 만듭니다",
        "연구자에게는 환자명과 연락처를 빼고 보여 주세요",
        ["CREATE VIEW 연구용_환자 AS", "SELECT 환자ID, 나이", "FROM 환자;", "", "GRANT SELECT", "ON 연구용_환자", "TO researcher;"],
        sz=2000, request_label="연구 부서의 요청",
        note="원본 환자 테이블(개념 스키마)은 그대로 두고, 필요한 부분만 보여 주는 뷰를 만듭니다.\nCREATE VIEW · GRANT 문법은 7주차부터 직접 써 봅니다. 지금은 ‘필요한 부분만 보여 준다’는 뜻만 보면 됩니다."))
    c.add(conceptual_schema_slide())
    c.add(internal_schema_slide())
    c.add(table_slide("3단계 스키마 정리", "한 줄로 기억하기",
        ["구분", "쉽게 말하면", "관점", "병원 예"],
        [["외부 스키마", "내가 보는 화면", "사용자", "의사의 진료 화면, 원무팀의 수납 화면"],
         ["개념 스키마", "병원 전체 설계도", "조직 전체", "환자 · 진료 · 처방 테이블과 그 관계"],
         ["내부 스키마", "실제 저장 방법", "저장장치", "파일 위치, 인덱스, 압축 방식"]],
        [2300000, 2700000, 1900000, 5300000], col_algn=["ctr", "ctr", "ctr", "l"], sz=2200, row_h=800000, y=1800000,
        note="외부 스키마는 여러 개, 개념 스키마와 내부 스키마는 각각 하나"))

    # --- 4. 사상과 데이터 독립성
    c.add(checkpoint_slide(
        ["데이터베이스 시스템 = 데이터베이스 + DBMS + 스키마 + 사용자 + 언어",
         "스키마 = 데이터가 들어갈 틀, 인스턴스 = 지금 그 틀에 들어 있는 값",
         "외부 스키마는 사용자마다, 개념 스키마와 내부 스키마는 하나씩"],
        question="의사 화면과 원무팀 화면이 서로 다른 것은 어느 스키마 때문일까요?",
        answer="외부 스키마 — 같은 데이터베이스를 사용자마다 필요한 부분만 보여 줍니다."))
    c.add(section_slide(4, AGENDA, lead="구조가 바뀌어도 화면은 그대로인 이유"))
    c.add(mapping_slide())
    c.add(independence_why_slide())
    c.add(independence_table())
    c.add(quiz("사상과 데이터 독립성", "개념 스키마가 바뀌어도 사용자 화면(외부 스키마)이 영향을 받지 않는 성질은?",
               ["물리적 독립성", "논리적 독립성", "참조 무결성", "데이터 종속성"], answer=1,
               note="외부 ↔ 개념 = 논리적 독립성, 개념 ↔ 내부 = 물리적 독립성.  이 연결을 담당하는 규칙이 사상(Mapping)입니다."))

    c.add(table_slide("제품을 바꾸는 것은 어느 층의 변화일까", "오늘 첫 질문으로 돌아가 봅니다",
        ["층", "제품을 바꾸면 무슨 일이", "데이터 독립성이 지켜 주나"],
        [["외부 스키마\n(쿼리 · 뷰 · 리포트)", "제품마다 적는 법이 달라 가장 먼저 깨집니다", "아니요"],
         ["개념 스키마\n(어떤 표에 어떤 열)", "표와 열은 그대로지만 자료형 이름과\n제약조건 문법을 다시 적어야 합니다", "아니요"],
         ["내부 스키마\n(파일 · 인덱스)", "통째로 새로 만듭니다 (보통 담당 부서가 처리)", "아니요"]],
        [3000000, 6200000, 2600000], sz=1900, row_h=760000, y=1700000,
        col_algn=["ctr", "l", "ctr"],
        note="데이터 독립성은 **같은 DBMS 안에서** 한 층이 바뀔 때 다른 층을 지켜 주는 장치입니다. "
             "제품 자체를 바꾸는 것은 세 층을 받치던 바닥이 바뀌는 일이라 지켜 주지 못합니다."))
    c.add(two_panel_slide("그래도 살아남는 쿼리가 있습니다", "무엇이 깨지고 무엇이 남는가",
        "개념 스키마가 같으면 표준 문법으로 쓴 쿼리는 그대로 돕니다.",
        ("깨지는 것 — 제품 고유 문법",
         ["상위 N행: ROWNUM · TOP · LIMIT",
          "- 빈 값 대체: NVL · ISNULL · IFNULL",
          "- 오늘 날짜: SYSDATE · GETDATE()",
          "- 자료형 이름: VARCHAR2 · VARCHAR"], *RED_PANEL),
        ("남는 것 — 표준에 가까운 문법",
         ["SELECT · FROM · WHERE · GROUP BY · HAVING",
          "- JOIN … ON, ORDER BY",
          "- CASE WHEN … THEN … END",
          "- COALESCE(값, 대체값)"], *GREEN_PANEL),
        note=["**그래서 옮길 때 고생을 줄이려면, 개념 스키마를 먼저 옮기고 표준 문법으로 쓴 쿼리부터 돌려 봅니다.**",
              "제품 고유 함수를 쓴 쿼리만 따로 모아 두면 무엇을 고쳐야 하는지 한눈에 보입니다."],
        y=2300000, h=2200000))

    # --- 5. 데이터 사전
    c.add(section_slide(5, AGENDA, lead="분석을 시작할 때 가장 먼저 보는 자료"))
    c.add(data_dictionary_slide())
    c.add(table_slide("데이터 사전 읽기 ① AACT", "먼저 확인할 것: 테이블 이름, 한 행이 뜻하는 것, 연결 키",
        ["테이블", "한 행이 뜻하는 것", "연결 키"],
        [["studies", "임상시험 1건", "nct_id (기본키)"],
         ["conditions", "임상시험 1건의 대상 질환 1개", "nct_id"],
         ["interventions", "임상시험 1건의 중재(약물 · 시술) 1개", "nct_id"],
         ["sponsors", "임상시험 1건의 스폰서 1곳", "nct_id"],
         ["facilities", "임상시험 1건이 진행되는 기관 1곳", "nct_id"],
         ["eligibilities", "임상시험 1건의 선정 · 제외 기준", "nct_id"]],
        [2700000, 5600000, 2900000], sz=2200, row_h=560000, y=1650000,
        col_algn=["l", "l", "ctr"], col_font={0: "Courier New"},
        note="한 임상시험에 질환 · 기관이 여러 개 → studies 1행에 여러 행이 연결됨 (8주차 JOIN)", note_style="footnote"))
    c.add(table_slide("데이터 사전 읽기 ② AACT", "열 이름과 데이터 타입도 데이터 사전에 있습니다",
        ["테이블.열", "데이터 타입", "값의 예", "주의할 점"],
        [["studies.nct_id", "VARCHAR", "NCT04280705", "문자, 계산 불가"],
         ["studies.start_date", "DATE", "2020-02-21", "날짜 계산 가능"],
         ["studies.enrollment", "INTEGER", "1062", "합계 · 평균 가능"],
         ["studies.phase", "VARCHAR", "PHASE2/PHASE3", "두 단계가 한 값에 들어 있음"],
         ["eligibilities.minimum_age", "VARCHAR", "18 Years", "숫자가 아님, 비교 불가"],
         ["calculated_values.minimum_age_num", "INTEGER", "18", "숫자로 바꿔 둔 열"]],
        [4900000, 1700000, 2500000, 3200000], sz=1800, row_h=580000, y=1650000,
        col_algn=["l", "ctr", "ctr", "l"], col_font={0: "Courier New", 2: "Courier New"},
        note="같은 정보라도 타입이 다르면 할 수 있는 계산이 다릅니다 (5주차 데이터 타입, 12주차 오류).", note_style="footnote"))
    c.add(sql_example("데이터 사전 읽기 ③ SQL로 확인", "데이터 사전은 SQL로도 조회할 수 있습니다",
        "studies 테이블에 어떤 열이 있는지 알려줘",
        ["SELECT column_name, data_type", "FROM information_schema.columns", "WHERE table_name = 'studies';"],
        note="DuckDB = 이 수업 실습에서 쓰는 가벼운 데이터베이스입니다 (7주차부터). DESCRIBE studies; 명령으로도 볼 수 있습니다.",
        result=[["column_name", "data_type"], ["nct_id", "VARCHAR"], ["start_date", "DATE"],
                ["enrollment", "INTEGER"], ["phase", "VARCHAR"], ["…", "…"]],
        result_w=[3300000, 2700000], request_label="자연어 요청"))

    # --- 6. 사용자 · 마무리
    c.add(checkpoint_slide(
        ["사상(Mapping) = 스키마와 스키마를 이어 주는 규칙",
         "논리적 독립성 = 개념 스키마가 바뀌어도 사용자 화면은 그대로",
         "데이터 사전 = 테이블 이름 · 한 행의 뜻 · 열과 타입을 적어 둔 자료"],
        question="AACT의 studies 테이블은 한 행이 무엇을 뜻할까요?",
        answer="임상시험 1건입니다. 한 행이 무엇인지 먼저 정해야 세는 단위가 어긋나지 않습니다."))
    c.add(section_slide(6, AGENDA, lead="누가 데이터베이스를 어떻게 쓰는지 살펴봅니다"))
    c.add(user_cards())
    c.add(quiz("데이터베이스 사용자", "연구를 위해 SQL로 직접 환자 데이터를 조회하고 통계를 내는 사람은?",
               ["일반 사용자", "응용 프로그래머", "SQL 사용자", "데이터베이스 관리자 (DBA)"], answer=2,
               note="EMR 화면만 쓰면 일반 사용자, SQL을 직접 쓰면 SQL 사용자"))
    c.add(table_slide("데이터베이스 시스템 (참고사항)", "DBMS마다 데이터 사전을 보는 명령이 조금씩 다릅니다",
        ["DBMS", "테이블 목록 보기", "열 정보 보기"],
        [["PostgreSQL (AACT)", "\\dt", "\\d studies"],
         ["DuckDB (실습 환경)", "SHOW TABLES;", "DESCRIBE studies;"],
         ["Oracle", "SELECT table_name\nFROM user_tables;", "DESC studies"],
         ["MS SQL Server", "SELECT name\nFROM sys.tables;", "sp_help 'studies'"],
         ["표준 SQL (Oracle 제외)", "SELECT table_name\nFROM information_schema.tables;",
          "SELECT column_name, data_type\nFROM information_schema.columns\nWHERE table_name = 'studies';"]],
        [2700000, 4400000, 4700000], sz=1800, row_h=560000, y=1650000, col_algn=["ctr", "l", "l"],
        col_font={1: "Courier New", 2: "Courier New"},
        note="명령은 달라도 ‘데이터 사전을 먼저 본다’는 순서는 같습니다.", note_style="footnote"))
    c.add(terms_slide(4, [
        ["데이터베이스 시스템", "Database System", "데이터베이스 · DBMS · 스키마 · 사용자 · 언어를 묶어 부르는 말"],
        ["스키마", "Schema", "데이터가 들어갈 틀. 어떤 테이블에 어떤 열이 있는지"],
        ["인스턴스", "Instance", "지금 그 틀에 들어 있는 실제 값"],
        ["외부 스키마", "External Schema", "사용자마다 보이는 부분. 뷰(View)로 만듭니다"],
        ["개념 스키마", "Conceptual Schema", "조직 전체의 설계도. 데이터베이스마다 하나"],
        ["내부 스키마", "Internal Schema", "저장장치에 실제로 저장하는 방법"],
        ["사상", "Mapping", "스키마와 스키마를 이어 주는 규칙"],
        ["데이터 독립성", "Data Independence", "한쪽이 바뀌어도 다른 쪽이 영향을 받지 않는 성질"],
        ["데이터 사전", "Data Dictionary", "테이블과 열의 뜻 · 타입을 적어 둔 자료"],
        ["메타데이터", "Metadata", "데이터를 설명하는 데이터"],
    ]))
    c.add(summary(4, [
        "**데이터베이스 시스템** = DB + DBMS + 스키마 + 사용자 + 언어",
        "**스키마** = 틀,  **인스턴스** = 지금 들어 있는 값",
        "**3단계 스키마**와 **사상** 덕분에 **데이터 독립성**이 생긴다",
        "**데이터 사전**은 분석을 시작할 때 가장 먼저 보는 자료다",
    ], sz=2700, lnSpc=165, next_week="5강. 관계형 데이터베이스 — 테이블 · 키 · 무결성"))
