# -*- coding: utf-8 -*-
"""10강. 안전한 데이터 수정과 트랜잭션 (원본 134~141번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)

SPAN = (134, 141)
TITLE = "10강. 안전한 데이터 수정과 트랜잭션"

AGENDA = [("데이터를 바꾼다는 것", "조회와 무엇이 다른가"),
          ("INSERT · UPDATE · DELETE", "세 가지 문장"),
          ("트랜잭션", "한 덩어리로 묶기"),
          ("COMMIT과 ROLLBACK", "확정과 되돌리기"),
          ("안전한 수정 절차", "실무에서 지키는 순서"),
          ("정리", "용어와 요약")]


def read_vs_write_slide():
    return two_panel_slide("조회와 수정은 다릅니다", "되돌릴 수 있는가",
        "지금까지 배운 SELECT는 데이터를 **읽기만** 했습니다.",
        ("조회 (SELECT)", ["데이터를 읽기만 함",
                        "- 잘못 써도 데이터는 그대로",
                        "- 다시 실행하면 됨",
                        "- 연구자 · 분석자에게 주는 기본 권한"], "DEEAF6", "1F497D"),
        ("수정 (INSERT · UPDATE · DELETE)", ["데이터가 실제로 바뀜",
                                          "- 조건을 잘못 쓰면 전체가 바뀜",
                                          "- 확정 후에는 되돌리기 어려움",
                                          "- 권한이 따로 필요 (3주차 GRANT)"], *RED_PANEL),
        note=["병원에서 분석자는 보통 **읽기 권한만** 받습니다. 원천 데이터는 수정하지 않습니다.",
              "그래도 문법을 알아야 하는 이유: 데이터가 어떻게 바뀌는지 알아야 결과를 해석할 수 있기 때문입니다."],
        y=2300000, h=2700000)


def dml_slide():
    def b(ids):
        blocks = [("INSERT", "새 행을 추가", ["INSERT INTO 환자", "  (환자ID, 환자명, 생년월일)",
                                        "VALUES ('P100', '김OO', '1958-03-11');"], "DEEAF6", "1F497D"),
                  ("UPDATE", "기존 값을 바꿈", ["UPDATE 환자", "SET 연락처 = '010-9999-8888'",
                                          "WHERE 환자ID = 'P100';"], "FFF2CC", "BF9000"),
                  ("DELETE", "행을 지움", ["DELETE FROM 환자", "WHERE 환자ID = 'P100';"], "FBE5E5", "C00000")]
        s, y = "", 1600000
        for kw, what, sql, fill, line in blocks:
            h = 340000 * len(sql) + 500000
            s += shape(ids, "rect", X0, y, 2400000, h, fill=fill, line=line,
                       text_xml=para(f"**{kw}**", sz=2400, algn="ctr", font="Courier New", lnSpc=100) +
                                para(what, sz=1800, algn="ctr", lnSpc=110), name="KW")
            s += shape(ids, "roundRect", X0 + 2600000, y, 9500000, h, fill="F6F8FA", line="7F7F7F", name="SQL")
            s += textbox(ids, X0 + 2850000, y + 150000, 9000000, h - 200000,
                         "".join(para(l, sz=2000, lnSpc=110, sql=True) for l in sql), autofit=False)
            y += h + 200000
        s += textbox(ids, X0, y + 150000, W0, 700000,
            para("**UPDATE와 DELETE에는 WHERE가 거의 반드시 필요합니다.** 빠뜨리면 모든 행이 대상이 됩니다.",
                 sz=2400, b=True, algn="ctr", color=RED, lnSpc=115))
        return s
    return free("INSERT · UPDATE · DELETE", b, subtitle="추가 · 수정 · 삭제의 기본 모양")


def where_accident_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("실무에서 가장 유명한 사고입니다. 오류가 나지 않고 **조용히 전부 바뀝니다.**", sz=2300, lnSpc=115))
        y = 2100000
        s += shape(ids, "rect", X0, y, 6000000, 480000, fill="C00000", line="C00000",
                   text_xml=para("WHERE를 빠뜨리면", sz=2100, algn="ctr", color="FFFFFF", lnSpc=100), name="Bad Head")
        s += shape(ids, "roundRect", X0, y + 480000, 6000000, 2150000, fill="FBE5E5", line="C00000", name="Bad")
        s += textbox(ids, X0 + 250000, y + 600000, 5600000, 2000000,
            "".join(para(l, sz=2000, lnSpc=110, sql=True) for l in
                    ["UPDATE 환자", "SET 진료과 = '내과';", "-- WHERE 가 없습니다"]), autofit=False)
        s += textbox(ids, X0, y + 2760000, 6000000, 700000,
            para("→ **모든 환자**의 진료과가 내과로 바뀝니다.\n5만 명이면 5만 행이 한 번에 바뀝니다.",
                 sz=2000, lnSpc=120, color="C00000"))
        s += shape(ids, "rect", 7300000, y, 6000000, 480000, fill="2C5F2D", line="2C5F2D",
                   text_xml=para("이렇게 확인하고 씁니다", sz=2100, algn="ctr", color="FFFFFF", lnSpc=100), name="Good Head")
        s += shape(ids, "roundRect", 7300000, y + 480000, 6000000, 2150000, fill="E2EFDA", line="2C5F2D", name="Good")
        s += textbox(ids, 7550000, y + 600000, 5600000, 2000000,
            "".join(para(l, sz=2000, lnSpc=110, sql=True) for l in
                    ["SELECT COUNT(*) FROM 환자", "WHERE 진료과 = '외과';", "", "UPDATE 환자", "SET 진료과 = '내과'", "WHERE 진료과 = '외과';"]), autofit=False)
        s += textbox(ids, 7300000, y + 2760000, 6000000, 700000,
            para("→ **바꿀 조건을 WHERE에 적고**, 같은 조건으로\n먼저 세어 본 뒤 수정합니다.",
                 sz=2000, lnSpc=120, color="2C5F2D"))
        s += textbox(ids, X0, 5800000, W0, 1300000,
            para("병원 사례: 처방 코드 일괄 정정 작업에서 WHERE를 빠뜨려 **수개월치 처방이 한 값으로 덮여 쓰인** 사고가 있었습니다.",
                 sz=2200, lnSpc=125) +
            para("그래서 운영 데이터베이스 수정은 **혼자 하지 않고, 백업을 확인한 뒤, 승인 절차를 거쳐** 진행합니다.",
                 sz=2200, b=True, lnSpc=125, color="1F3763"))
        return s
    return free("WHERE를 빠뜨리면", b, subtitle="오류가 나지 않아서 더 위험합니다")


def transaction_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 600000,
            para("**트랜잭션** = 여러 개의 수정을 **하나의 덩어리**로 묶은 것. 전부 되거나, 전부 안 되거나.",
                 sz=2400, b=True, lnSpc=120))
        y0 = 2200000
        s += shape(ids, "roundRect", X0 + 300000, y0, 5600000, 2500000, fill="F6F8FA", line="1F497D", lw=15875, name="Tx")
        s += textbox(ids, X0 + 300000, y0 + 130000, 5600000, 400000,
                     para("입원 수속 (한 덩어리)", sz=2200, b=True, algn="ctr", color=BLUE, lnSpc=100), autofit=False)
        steps = ["① 입원 기록을 만든다", "② 병상을 ‘사용 중’으로 바꾼다", "③ 수납 내역을 만든다"]
        yy = y0 + 650000
        for st in steps:
            s += shape(ids, "rect", X0 + 600000, yy, 5000000, 480000, fill="DEEAF6", line="1F497D",
                       text_xml=para(st, sz=2000, lnSpc=100, marL=200000), name="Step")
            yy += 580000
        s += textbox(ids, 6800000, y0 + 250000, 6400000, 2450000,
            para("**②에서 오류가 나면?**", sz=2300, lnSpc=125) +
            para("입원 기록은 있는데 병상은 비어 있는 상태", sz=2000, lvl=1, lnSpc=120) +
            para("데이터가 **서로 맞지 않게** 됩니다", sz=2000, lvl=1, lnSpc=120, color=RED) +
            para("**그래서 묶습니다**", sz=2300, lnSpc=125, spcBef=12) +
            para("하나라도 실패하면 **전부 없던 일로** 되돌립니다", sz=2000, lvl=1, lnSpc=120, color="2C5F2D"),
            autofit=False)
        s += textbox(ids, X0, 5300000, W0, 1400000,
            para("**ACID** — 트랜잭션이 지켜 주는 네 가지 (용어만 기억하면 됩니다)", sz=2300, b=True, lnSpc=125) +
            para("원자성(전부 또는 전무) · 일관성(규칙 유지) · 고립성(서로 방해 안 함) · 지속성(확정되면 남음)",
                 sz=2200, lnSpc=125, color="1F3763"))
        return s
    return free("트랜잭션 (Transaction)", b, subtitle="입원 수속을 예로")


def commit_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("수정한 뒤 **확인하고 확정**하거나, **되돌립니다.**", sz=2300, lnSpc=115))
        s += shape(ids, "roundRect", X0, 2050000, 6200000, 2600000, fill="F6F8FA", line="7F7F7F", name="SQL")
        s += textbox(ids, X0 + 250000, 2200000, 5800000, 2400000,
            "".join(para(l, sz=2000, lnSpc=115, sql=True) for l in
                    ["BEGIN;", "", "UPDATE 환자", "SET 연락처 = '010-9999-8888'", "WHERE 환자ID = 'P100';",
                     "", "SELECT * FROM 환자 WHERE 환자ID = 'P100';"]), autofit=False)
        s += panel(ids, 6900000, 2050000, 6400000, 1200000, "결과가 맞으면  COMMIT;", [
            "바뀐 내용을 확정합니다. 이제 되돌릴 수 없습니다."], fill="E2EFDA", line="2C5F2D", sz=1900)
        s += panel(ids, 6900000, 3450000, 6400000, 1200000, "이상하면  ROLLBACK;", [
            "BEGIN 이후의 모든 변경을 없던 일로 되돌립니다."], fill="FBE5E5", line="C00000", sz=1900)
        s += textbox(ids, X0, 5100000, W0, 1400000,
            para("**중요**: COMMIT 하기 전에는 다른 사람에게 이 변경이 보이지 않습니다 (고립성).", sz=2200, lnSpc=125) +
            para("일부 도구는 자동으로 COMMIT 됩니다(auto-commit). 수정 작업 전에 **어떤 설정인지 반드시 확인**하세요.",
                 sz=2200, b=True, lnSpc=125, color=RED))
        return s
    return free("COMMIT과 ROLLBACK", b, subtitle="확정하거나 되돌리거나")


def safe_procedure_slide():
    def b(ids):
        steps = [("① 환경 확인", "운영 데이터베이스인가, 연습용 복사본인가"),
                 ("② 백업 확인", "언제 백업되었는지, 복구에 얼마나 걸리는지"),
                 ("③ SELECT 먼저", "같은 WHERE로 조회해 바뀔 행 수를 확인"),
                 ("④ BEGIN 후 수정", "트랜잭션 안에서 UPDATE · DELETE 실행"),
                 ("⑤ 결과 확인", "바뀐 행 수와 실제 값을 다시 조회"),
                 ("⑥ COMMIT / ROLLBACK", "맞으면 확정, 이상하면 되돌리기")]
        s, y, h, gap = "", 1550000, 700000, 110000
        for t, d in steps:
            s += shape(ids, "rect", X0 + 500000, y, 3400000, h, fill="DEEAF6", line="1F497D",
                       text_xml=para(f"**{t}**", sz=2100, algn="ctr", lnSpc=100), name="Step")
            s += shape(ids, "rect", X0 + 3900000, y, 7800000, h, fill="FFFFFF", line="7F7F7F",
                       text_xml=para(d, sz=2000, lnSpc=100, marL=250000), name="Desc")
            y += h + gap
        s += textbox(ids, X0, y + 200000, W0, 600000,
            para("이 순서를 지키면 사고의 대부분을 막을 수 있습니다.", sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("안전한 수정 절차", b, subtitle="실무에서 지키는 여섯 단계")


def build(c):

    # --- 도입
    c.add(cover(10, "안전한 데이터 수정과 트랜잭션",
                ["INSERT · UPDATE · DELETE", "트랜잭션과 ACID", "COMMIT · ROLLBACK과 안전 절차"],
                "2026. 11. 17."))
    c.add(content("지난시간 리뷰", [
        ("분석 질문을 **대상 · 기간 · 조건 · 세는 단위**로 나누어 적는다", dict(lvl=1, marL=457200, indent=-457200)),
        ("조건을 하나씩 더하며 **건수 변화**를 확인한다", dict(lvl=1, marL=457200, indent=-457200)),
        ("**검산 다섯 가지**로 결과를 점검한 뒤 숫자를 쓴다", dict(lvl=1, marL=457200, indent=-457200)),
        ("지금까지는 데이터를 **읽기만** 했습니다.", dict(spcBef=18)),
        ("오늘은 데이터를 **바꾸는 방법**과, 바꿀 때 지켜야 할 것을 배웁니다.",
         dict(b=True, algn="ctr", color=BLUE, spcBef=12)),
    ]))
    c.add(objectives_slide(10,
        ["INSERT · UPDATE · DELETE의 기본 모양을 읽고 쓸 수 있다",
         "WHERE를 빠뜨렸을 때 무슨 일이 생기는지 설명할 수 있다",
         "트랜잭션이 왜 필요한지 병원 예로 설명할 수 있다",
         "안전한 수정 절차 여섯 단계를 말할 수 있다"],
        AGENDA, subtitle="데이터를 바꿀 때 지켜야 하는 것들",
        date_note="분석자는 보통 읽기 권한만 받지만, 무슨 일이 일어나는지는 알아야 합니다"))

    # --- 1. 데이터를 바꾼다는 것
    c.add(section_slide(1, AGENDA, lead="읽는 것과 바꾸는 것은 무게가 다릅니다"))
    c.add(read_vs_write_slide())

    # --- 2. DML
    c.add(section_slide(2, AGENDA, lead="추가 · 수정 · 삭제의 세 가지 문장"))
    c.add(dml_slide())
    c.add(where_accident_slide())
    c.add(table_slide("수정할 때 확인할 것", "문장별로 특히 주의할 점",
        ["문장", "확인할 것", "안 지키면"],
        [["INSERT", "기본키 중복, 필수 열 누락, 타입 맞음", "개체 무결성 위반으로 거부"],
         ["UPDATE", "WHERE 조건, 바뀔 행 수, 바꿀 값의 타입", "의도하지 않은 행까지 변경"],
         ["DELETE", "WHERE 조건, 이 행을 참조하는 다른 표", "참조 무결성 위반 또는 연쇄 삭제"]],
        [2200000, 5600000, 4400000], sz=2000, row_h=720000, y=1750000,
        col_algn=["ctr", "l", "l"],
        note="5주차의 무결성 제약조건이 여기서 실제로 작동합니다."))
    c.add(checkpoint_slide(
        ["**INSERT · UPDATE · DELETE** 로 데이터를 바꾼다",
         "UPDATE · DELETE 에는 **WHERE가 거의 반드시** 필요하다",
         "수정 전에 **같은 WHERE로 SELECT** 해서 행 수를 확인한다"],
        question="UPDATE 문에서 WHERE를 빠뜨리면 어떻게 될까요?",
        answer="오류 없이 모든 행이 바뀝니다. 그래서 가장 위험한 실수입니다."))

    # --- 3. 트랜잭션
    c.add(section_slide(3, AGENDA, lead="여러 수정을 한 덩어리로 묶습니다"))
    c.add(transaction_slide())
    c.add(two_panel_slide("트랜잭션이 없으면", "병원에서 실제로 곤란해지는 경우",
        "수혈 기록과 혈액 재고를 각각 따로 수정한다고 해 봅시다.",
        ("중간에 실패하면", ["수혈 기록은 남았는데 재고는 그대로",
                        "- 재고 수량이 실제와 어긋남",
                        "- 어느 쪽이 맞는지 알 수 없음",
                        "- 나중에 사람이 찾아서 고쳐야 함"], *RED_PANEL),
        ("트랜잭션으로 묶으면", ["둘 다 되거나, 둘 다 안 되거나",
                          "- 중간 상태가 남지 않음",
                          "- 실패하면 자동으로 되돌아감",
                          "- 데이터가 항상 맞물려 있음"], *GREEN_PANEL),
        note=["계좌 이체, 재고 관리, 예약 시스템이 모두 같은 이유로 트랜잭션을 씁니다.",
              "**여러 표를 함께 바꿀 때는 반드시 트랜잭션으로 묶습니다.**"],
        y=2300000, h=2700000))

    # --- 4. COMMIT과 ROLLBACK
    c.add(section_slide(4, AGENDA, lead="확정하거나 되돌리거나"))
    c.add(commit_slide())

    # --- 5. 안전한 수정 절차
    c.add(section_slide(5, AGENDA, lead="순서를 지키면 사고를 막습니다"))
    c.add(safe_procedure_slide())
    c.add(content("분석자가 실제로 지키는 규칙", [
        ("① **원천 데이터는 건드리지 않는다**", dict()),
        ("EMR · CDW의 원본 테이블은 읽기 전용으로 사용", dict(lvl=1, sz=2200)),
        ("② **분석용 결과는 따로 만든다**", dict()),
        ("새 표를 만들거나 파일로 내보내서 작업", dict(lvl=1, sz=2200)),
        ("③ **수정이 필요하면 담당 부서에 요청한다**", dict()),
        ("의료정보팀 · DBA를 통해 절차대로 진행", dict(lvl=1, sz=2200)),
        ("④ **연습은 복사본에서 한다**", dict()),
        ("수업에서도 원본이 아닌 연습용 복사본으로만 시연합니다", dict(lvl=1, sz=2200)),
        ("“읽기 권한만 있는 것”은 불편이 아니라 **보호 장치**입니다.",
         dict(b=True, algn="ctr", color=BLUE, spcBef=16)),
    ], subtitle="권한과 절차가 우리를 지켜 줍니다"))

    c.add(sql_example("뷰(View)로 자주 쓰는 조회를 저장하기", "긴 조건을 이름 하나로 줄여 둡니다",
        "이 조건을 매번 다시 쓰지 않게 해 주세요",
        ["CREATE VIEW 제2형당뇨_시험 AS",
         "SELECT DISTINCT s.nct_id, s.brief_title,",
         "                s.overall_status, s.start_date",
         "FROM studies AS s",
         "JOIN browse_conditions AS b",
         "  ON s.nct_id = b.nct_id",
         "WHERE b.mesh_term = 'Diabetes Mellitus, Type 2';",
         "",
         "SELECT COUNT(*) FROM 제2형당뇨_시험;"],
        sz=1600,
        result=[["count"], ["1,353"]], result_w=[6000000], request_label="요청",
        note="뷰는 표를 새로 만드는 것이 아니라 조회 방법에 이름을 붙이는 것입니다. 원본은 그대로 남습니다. (4주차 외부 스키마)"))
    c.add(table_slide("뷰를 실무에서 쓰는 이유", "같은 조건을 여러 사람이 쓸 때",
        ["이유", "무엇이 좋아지나"],
        [["정의를 한 곳에", "코호트 조건이 바뀌면 뷰만 고치면 됩니다"],
         ["같은 숫자를 공유", "여러 사람이 같은 정의로 세게 됩니다"],
         ["필요한 열만 보여 주기", "이름 · 연락처를 뺀 뷰로 권한을 제한할 수 있습니다"],
         ["긴 SQL을 줄이기", "매번 JOIN과 조건을 다시 적지 않아도 됩니다"]],
        [3600000, 7600000], sz=2000, row_h=680000, y=1750000,
        col_algn=["ctr", "l"],
        note="분석자에게는 대개 뷰를 만들 권한이 없습니다. 필요하면 데이터 담당 부서에 요청합니다.",
        note_style="footnote"))

    # --- 6. 정리
    c.add(section_slide(6, AGENDA, lead="오늘 나온 용어와 핵심을 다시 짚습니다"))
    c.add(terms_slide(10, [
        ["뷰", "View", "조회 방법에 이름을 붙여 둔 것. 원본 표는 그대로"],
        ["INSERT", "—", "새 행을 추가하는 문장"],
        ["UPDATE", "—", "기존 행의 값을 바꾸는 문장"],
        ["DELETE", "—", "행을 지우는 문장"],
        ["트랜잭션", "Transaction", "여러 수정을 하나로 묶은 처리 단위"],
        ["ACID", "—", "원자성 · 일관성 · 고립성 · 지속성"],
        ["COMMIT", "—", "변경을 확정하는 명령"],
        ["ROLLBACK", "—", "변경을 없던 일로 되돌리는 명령"],
        ["자동 커밋", "Auto-commit", "실행하자마자 확정되는 설정. 수정 전 확인 필요"],
    ]))
    c.add(summary(10, [
        "**UPDATE · DELETE 에는 WHERE**. 빠뜨리면 모든 행이 바뀐다",
        "**같은 WHERE로 SELECT 먼저** 해서 바뀔 행 수를 확인한다",
        "여러 수정은 **트랜잭션으로 묶고**, 확인 후 COMMIT 또는 ROLLBACK",
    ], sz=2800, lnSpc=170, next_week="11강. CDW 구조와 분석 업무 흐름 — 병원에서 데이터를 받는 과정"))
