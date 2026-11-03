# -*- coding: utf-8 -*-
"""11강 뒷부분을 SQL로 (2026-11-03, 강사: "프로세스는 별로 궁금하지 않아 … SQL에 관련된 것을 쉽게").

절차 슬라이드 대신 새 DB를 SQL로 둘러보고 표를 잇는 두 절:
  4. CDW를 SQL로 둘러보기   CDW를 쓰는 방법(화면 vs SQL) · SHOW TABLES · DESCRIBE 입원 · SELECT * FROM 환자 LIMIT 3
  5. 표 잇기               표를 잇는 열 (환자ID · 입원ID · 병동, 1 : N 도표) · 입원 JOIN 환자
- 숨김 5장 (지우지 않음): 분석 업무 흐름 · 결과를 전달하는 형태 · 무엇에 쓰느냐에 따라 절차가 다릅니다 · 가명정보로 분석하는 차례 · 지켜야 할 것
- 제목 '11강. CDW 구조와 SQL로 둘러보기' — 표지 · 학습 목표 · 구분 · 강의 정리
- 12강 제목 '12강. SQL로 병원 통계 분석' (강사가 정함) — 표지 · 12강 리뷰 · 13강 지표 표 · 15강 시험 범위
결과 표의 숫자는 가상 병원 CDW 에서 바로 계산. w14_easy.py 다음에 실행. 사용: python3 tools/w11_sql.py <덱.pptx> <결과.pptx>
"""
import os, sys, re
import duckdb
import w10_slides
from w10_slides import build
from w10_tx_more import fill
from w12_new import agenda
from w14_easy import clone, blank, X0, X1, B, YEL_F, YEL_L
from slidekit import A, P, Deck, texts, shape, set_para, set_title, replace_text, add_box, add_arrow, hide, KW_SQL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = duckdb.connect(os.path.join(ROOT, "data", "hospital_mini.duckdb"), read_only=True)
rows = lambda q: h.execute(q).fetchall()
val = lambda v: "NULL" if v is None else str(v)
TITLE11 = "11강. CDW 구조와 SQL로 둘러보기"
TITLE12 = "12강. SQL로 병원 통계 분석"
AG = [("CDW란 무엇인가", "운영 DB와 무엇이 다른가"), ("CDW의 구조", "원천 · ETL · 분석용 표"), ("데이터 사전과 요청서", "분석 전에 읽는 문서"),
      ("CDW를 SQL로 둘러보기", "표 · 열 · 값 보기"), ("표 잇기", "키와 JOIN"), ("정리", "강의 요약")]
KW = re.compile(KW_SQL.pattern.replace(r"\b(", r"\b(SHOW TABLES|DESCRIBE|", 1))

Q_SHOW = ["SELECT * FROM (SHOW TABLES);"]
R_SHOW = rows(Q_SHOW[0])
Q_DESC = ["SELECT * FROM (DESCRIBE 입원);"]
R_DESC = rows(Q_DESC[0])
Q_PEEK = ["SELECT *", "FROM 환자", "LIMIT 3;"]
R_PEEK = rows(" ".join(Q_PEEK))
PID = rows("SELECT 환자ID FROM 입원 GROUP BY 1 HAVING COUNT(*) = 2 AND COUNT(퇴원일) = 2 ORDER BY 1 LIMIT 1")[0][0]
Q_JOIN = ["SELECT 입원.입원ID, 입원.병동,", "       환자.성별, 환자.생년월일", "FROM 입원", "JOIN 환자", "  ON 입원.환자ID = 환자.환자ID",
          f"WHERE 입원.환자ID = '{PID}'", "ORDER BY 입원.입원ID;"]
R_JOIN = rows(" ".join(Q_JOIN))
assert len(R_SHOW) == 9 and len(R_DESC) == 10 and len(R_JOIN) == 2 and R_DESC[0][3] == "PRI"

SQL_SLIDES = [
    dict(title="어떤 표가 있나 — SHOW TABLES", question="가상 병원 CDW 에는 어떤 표가 있나?",
         sql_lines=Q_SHOW, hl_lines={0}, label="결과", header=["name"], rows=[[r[0]] for r in R_SHOW], hl_rows=set(),
         widths=[2400000],
         notes=[("표 9개", " · ".join(r[0] for r in R_SHOW)), ("같은 SQL", "9강 0단계에서 aact 표를 볼 때 쓴 것과 같습니다")]),
    dict(title="열 이름과 타입 — DESCRIBE", question="입원 표에는 어떤 열이 있고, 타입은 무엇인가?",
         sql_lines=Q_DESC, hl_lines={0}, label="결과 (열 6개 중 3개)", header=["column_name", "column_type", "key"],
         rows=[[r[0], r[1], val(r[3]) if r[3] else ""] for r in R_DESC], hl_rows={0}, widths=[1900000, 1600000, 1200000],
         notes=[("키", "입원ID 는 PRI = 기본키. 입원 1건에 번호 하나"), ("타입", "환자ID 는 VARCHAR(글자), 입원일 · 퇴원일은 DATE(날짜)")]),
    dict(title="몇 줄 먼저 보기 — LIMIT", question="환자 표의 실제 값은 어떤 모양인가?",
         sql_lines=Q_PEEK, hl_lines={2}, label="결과", header=["환자ID", "성별", "생년월일", "사망일"],
         rows=[[val(v) for v in r] for r in R_PEEK], hl_rows=set(), widths=[1250000, 900000, 1300000, 1274400],
         notes=[("환자ID", f"'{R_PEEK[0][0]}' 처럼 앞자리 0 이 있는 글자"), ("사망일", "비어 있으면 NULL — 값이 없다는 뜻")]),
]
JOIN_SLIDE = dict(title="두 표 잇기 — 입원에 환자 정보 붙이기", question=f"환자 '{PID}' 의 입원마다 성별 · 생년월일을 붙이면?",
                  sql_lines=Q_JOIN, hl_lines={3, 4}, label="결과", header=["입원ID", "병동", "성별", "생년월일"],
                  rows=[[val(v) for v in r] for r in R_JOIN], hl_rows=set(), widths=[1150000, 1100000, 900000, 1574400],
                  notes=[("ON", "두 표에 모두 있는 환자ID 로 잇기 (입원.환자ID = 환자.환자ID)"),
                         ("1 : N", f"환자 1명의 성별 · 생년월일이 입원 {len(R_JOIN)}건마다 붙음")])


def keys_slide(t):
    """표를 잇는 열 — 잇는 열 · 1 쪽 표 · N 쪽 표 (가상 병원 CDW 9개 표)"""
    keys = [("환자ID", "1F497D", "DEEAF6", "환자", "환자 1명", ["입원", "검사"]),
            ("입원ID", "2C5F2D", "E2EFDA", "입원", "입원 1건", ["진단", "진료비", "낙상"]),
            ("병동", "C55A11", "FBE4D5", "병동", "병동 1곳", ["입원", "병동일보", "근무"])]
    kw, ox, ow, ax, aw, mx, gap = 1900000, X0 + 2150000, 2400000, X0 + 4700000, 1000000, X0 + 5900000, 120000
    for x, w, head in ((X0, kw, "잇는 열"), (ox, ow, "1 쪽 (한 번)"), (mx, X1 - mx, "N 쪽 (여러 번)")):
        add_box(t, x, 1480000, w, 380000, [head], fill=None, line=None, sz=1400, bold=True, color="595959", geom="rect", name="Head")
    for i, (key, col, light, one, one_sub, many) in enumerate(keys):
        y = 1950000 + i * 1300000
        add_box(t, X0, y, kw, 1050000, [key], fill=col, line=col, sz=2000, color="FFFFFF", bold=True, name="Key")
        add_box(t, ox, y, ow, 1050000, [[(one, B)], one_sub], fill=light, line=col, sz=1800, name="One")
        add_box(t, ax, y + 60000, aw, 320000, ["1 : N"], fill=None, line=None, sz=1400, bold=True, color=col, geom="rect", name="Card")
        add_arrow(t, ax, y + 400000, aw, 380000, "right", fill=col)
        mw = (X1 - mx - (len(many) - 1) * gap) // len(many)
        for k, m in enumerate(many):
            add_box(t, mx + k * (mw + gap), y, mw, 1050000, [m], fill=light, line=col, sz=1800, bold=True, name="Many")
    add_box(t, X0, 5950000, X1 - X0, 700000,
            [[("JOIN", B), ("은 잇는 열의 값이 같은 행끼리 붙입니다. 1 쪽 표의 값은 N 쪽 행마다 반복해서 붙습니다.", {})]],
            fill=YEL_F, line=YEL_L, sz=1600, align="l", name="Note")


def main(src, out):
    d = Deck(src)
    w10_slides.KW = KW
    s11 = d.find("11강. CDW 구조와 분석 업무 흐름")
    e11 = d.find("11주차 강의 정리")
    s12 = d.find("12강. 원무 데이터로 보는 병원 운영")
    L = d.between(s11, e11)
    F = lambda line, also=None: d.find(line, also, within=L)
    rv, goal = F("지난시간 리뷰"), F("11주차 학습 목표")
    divs = [F("1. CDW란 무엇인가"), F("2. CDW의 구조"), F("3. 데이터 사전과 요청서"), F("4. 분석 업무 흐름"), F("5. 지켜야 할 것"), F("6. 정리")]
    s1 = [F("CDW — Clinical Data Warehouse"), F("운영 DB와 CDW"), F("CDW로 무엇을 하나 — 병원에서 쓰는 예")]
    s2 = [F("CDW가 만들어지는 과정"), F("CDW에서 자주 보는 표"), F("가상 병원 CDW — 핵심 네 표"), F("가상 병원 CDW — 12강부터 쓰는 실습 DB"),
          F("CDW를 쓸 때 늘 확인하는 두 가지")]
    s3 = [F("데이터 사전에서 확인할 것"), F("분석 요청서"), F("요청서를 SQL 조건으로 옮기기")]
    how = F("CDW를 쓰는 방법")
    flow, deliver = F("분석 업무 흐름"), F("결과를 전달하는 형태")
    purpose, pseudo, rules = F("무엇에 쓰느냐에 따라 절차가 다릅니다"), F("가명정보로 분석하는 차례"), F("지켜야 할 것")
    tmpl_sql = d.find("2단계 — 값 살펴보기")
    assert b"notesSlide" not in d.rels(tmpl_sql)

    # ---- 새 슬라이드 (숨기기 전에 복제)
    new_sql = lambda spec: d.insert_after(e11, build(d.tree(tmpl_sql), **spec), d.rels(tmpl_sql))
    n_show, n_desc, n_peek = [new_sql(s) for s in SQL_SLIDES]
    t, rel = blank(d, flow, "표를 잇는 열 — 환자ID · 입원ID · 병동", "같은 열이 있는 표끼리 JOIN으로 잇습니다")
    keys_slide(t); n_keys = d.insert_after(e11, t, rel)
    n_join = new_sql(JOIN_SLIDE)

    # ---- 표지 · 학습 목표 · 구분 · 강의 정리
    for s in d.tree(s11).iter(P + "sp"):
        tx = texts(s)
        if tx and tx[0] == "11강. CDW 구조와 분석 업무 흐름":
            set_para(s, TITLE11)
        elif tx[:3] == ["운영 DB와 CDW의 차이", "데이터 사전과 분석 요청서", "요청부터 결과 전달까지"]:
            fill(s, [(0, [tx[0]]), (1, [tx[1]]), (2, ["SQL로 둘러보기와 표 잇기"])])
    t = d.tree(goal)
    set_para(shape(t, "TextBox 4"), "CDW를 알고, 새 DB를 SQL로 둘러보기")
    fill(shape(t, "TextBox 6"), [(0, ["① 운영 DB와 CDW의 차이를 설명할 수 있다"]), (1, ["② 데이터 사전과 요청서를 읽을 수 있다"]),
                                 (2, ["③ 새 DB를 SQL로 둘러볼 수 있다"]), (3, ["④ 키로 두 표를 JOIN 할 수 있다"])])
    agenda(t, "Step", AG, "  ")
    set_para(shape(t, "TextBox 20"), "다음 시간부터 이 가상 병원 CDW로 병원 통계를 직접 냅니다")
    for k, s in enumerate(divs):
        t = d.tree(s)
        set_title(t, f"{k + 1}. {AG[k][0]}"); set_para(shape(t, "TextBox 4"), AG[k][1]); agenda(t, "Sec", AG, "   ")
    tb = shape(d.tree(e11), "TextBox 4")
    old = [[r.findtext(A + "t") for r in p_.findall(A + "r")] for p_ in tb.findall(f"{P}txBody/{A}p")]
    assert old[2][0] == "승인 범위 안에서", old
    fill(tb, [(0, old[0]), (1, old[1]), (1, ["새 DB는 ", "SHOW TABLES · DESCRIBE · LIMIT", "으로 먼저 둘러본다"]),
              (1, ["표는 ", "키(환자ID · 입원ID · 병동)", "로 잇는다 — JOIN … ON"])])
    for s in (flow, deliver, purpose, pseudo, rules):
        hide(d.tree(s))

    # ---- 순서
    order = [s11, rv, goal, divs[0], *s1, divs[1], *s2, divs[2], *s3,
             divs[3], how, n_show, n_desc, n_peek, flow, deliver,
             divs[4], n_keys, n_join, purpose, pseudo, rules,
             divs[5], e11]
    block = d.slides()[d.index(s11): d.index(s12)]
    assert len(order) == len(set(order)) == len(block) and set(order) == set(block), (len(order), len(set(order)), len(block))
    prev = d.slides()[d.index(s11) - 1]
    for s in order:
        d.lst.remove(s)
    for s in order:
        prev.addnext(s); prev = s

    # ---- 12강 제목 · 12강 리뷰 · 13강 지표 표 · 15강 시험 범위
    for s in d.tree(s12).iter(P + "sp"):
        if texts(s)[:1] == ["12강. 원무 데이터로 보는 병원 운영"]:
            set_para(s, TITLE12)
    rv12 = d.find("지난시간 리뷰", within=d.slides()[d.index(s12): d.index(s12) + 3])
    tb = shape(d.tree(rv12), "TextBox 4")
    old = [[r.findtext(A + "t") for r in p_.findall(A + "r")] for p_ in tb.findall(f"{P}txBody/{A}p")]
    assert old[2][0] == "승인 범위 안에서" and old[4][0].startswith("첫 주제는 원무"), old
    fill(tb, [(0, old[0]), (1, old[1]), (1, ["새 DB는 ", "SHOW TABLES · DESCRIBE", "로 둘러보고, 키로 JOIN한다"]), (3, old[3]),
              (4, ["입원 건수 · 재원일수 · 병상 가동률 · 진료비를 SQL로 셉니다."])])
    replace_text(d.tree(d.find("의료 질 지표 — 분자와 분모")), "원무 (12강)", "원무팀 (12강)")
    s15 = d.find("15강. 기말고사")
    replace_text(d.tree(d.find("시험 범위", within=d.slides()[d.index(s15):])), "CDW · 원무 · 질 지표", "CDW · 병원 통계 · 질 지표")
    d.save(out)
    vis = sum(d.tree(s).get("show") != "0" for s in order)
    print(f"11강: 새 5장 · 숨김 5장 · 보이는 장 {vis}장 · 12강 제목 '{TITLE12}' → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
