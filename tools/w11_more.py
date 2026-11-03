# -*- coding: utf-8 -*-
"""11강: CDW 설명 강화 + 가상 병원 CDW 소개 (2026-11-03 강사 요청: 11강부터 aact_mini 대신 가상 병원 DB)

- 새 슬라이드 3장 (덱 안의 슬라이드 모양 복제)
    'CDW로 무엇을 하나 — 병원에서 쓰는 예'   ('운영 DB와 CDW' 뒤, 'CDW에서 자주 보는 표' 모양)
    'CDW가 없으면, 있으면'                   (그 뒤, 'CDW를 쓰는 방법' 두 칸 모양)
    '가상 병원 CDW — 12강부터 쓰는 실습 DB'   ('수업에서 쓰는 가상 CDW 표' 뒤, 표 모양)
- '수업에서 쓰는 가상 CDW 표' → 제목 · 부제: 핵심 네 표가 이제 실제로 있는 실습 DB
- '요청서를 SQL 조건으로 옮기기': 가상 병원 CDW 에서 실제로 실행한 숫자 (data/hospital_mini.duckdb 에서 계산해 넣음)
- 강의 정리 '다음 시간': 12강 새 제목
사용: python3 tools/w11_more.py <덱.pptx> <결과.pptx>
"""
import os, sys
import duckdb
from slidekit import A, Deck, texts, shape, set_para, set_title, replace_text, table_fill, move_y
from w10_tx_more import fill

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEXT12 = "  12강. 원무 데이터로 보는 병원 운영 — 과제 2 공개"

h = duckdb.connect(os.path.join(ROOT, "data", "hospital_mini.duckdb"), read_only=True)
REQ = """SELECT COUNT(DISTINCT 입원.입원ID) AS 퇴원건, COUNT(DISTINCT 입원.환자ID) AS 환자수
FROM 입원 JOIN 환자 ON 입원.환자ID = 환자.환자ID JOIN 진단 ON 진단.입원ID = 입원.입원ID
WHERE 입원.퇴원일 BETWEEN '2024-01-01' AND '2024-12-31' AND 진단.진단코드 LIKE 'E11%' AND 진단.주진단여부 = 'Y'
  AND 입원.입원일 - 환자.생년월일 >= 19 * 365 AND 입원.퇴원형태 NOT IN ('사망', '전원')"""
N_DIS, N_PT = h.execute(REQ).fetchone()
assert (N_DIS, N_PT) == (331, 326), (N_DIS, N_PT)
BEDS = h.execute("SELECT SUM(병상수) FROM 병동").fetchone()[0]
assert BEDS == 226
COUNTS = dict(h.execute("""SELECT '환자', COUNT(*) FROM 환자 UNION ALL SELECT '입원', COUNT(*) FROM 입원 UNION ALL
  SELECT '낙상', COUNT(*) FROM 낙상""").fetchall())

USES = [  # 누가 · 무엇을 보나 · CDW 에서 꺼내는 자료 · 이 수업에서
    ("간호부", "낙상 · 욕창 발생률, 근무조별 인력", "낙상 보고 · 재원 환자 수 · 근무표", "13강 · 과제 2"),
    ("QI · 적정성평가", "30일 재입원율, 평가 지표 충족률", "입원 · 퇴원 · 진단", "13강"),
    ("원무 · 경영", "평균 재원일수, 병상 가동률, 진료비", "입퇴원 · 병상 · 진료비", "12강"),
    ("연구자", "연구 대상자 선별, 변수 추출", "진단 · 검사 · 처방", "13강"),
    ("감염관리", "병원감염 발생, 격리 병상 사용", "검사(배양) · 입원 · 병상", "—"),
]
TABLES = [  # 표 · 한 행 · 주요 열 · 쓰는 곳
    ("환자", "환자 1명", "환자ID (글자 7자리) · 성별 · 생년월일 · 사망일", "12 · 13강 · 과제 2"),
    ("입원", "입원 1건", "병동 · 진료과 · 입원일 · 퇴원일 · 퇴원형태 · 계획입원", "12 · 13강 · 과제 2"),
    ("진단", "진단 1건", "진단코드 (KCD) · 주진단여부", "11 · 13강"),
    ("검사", "검사 1건", "검사일 · 검사명 · 결과값", "13강"),
    ("병동", "병동 1곳", "구분 · 주진료과 · 병상수", "12강"),
    ("병동일보", "병동 × 날짜", "재원환자수 · 입원환자수 · 퇴원환자수", "12 · 13강 · 과제 2"),
    ("근무", "병동 × 날짜 × 근무조", "근무조 (D · E · N) · 간호사수", "13강"),
    ("진료비", "입원 × 항목", "항목 · 금액 · 급여구분", "12강"),
    ("낙상", "낙상 1건", "발생일 · 근무조 · 손상정도", "과제 2"),
]


def uses_slide(t):
    set_title(t, "CDW로 무엇을 하나 — 병원에서 쓰는 예")
    set_para(shape(t, "TextBox 4"), "같은 CDW 자료로 부서마다 다른 질문에 답합니다")
    bottom = table_fill(t, ["누가", "무엇을 보나", "CDW에서 꺼내는 자료", "이 수업에서"], [list(r) for r in USES],
                        widths=[2200000, 4000000, 3700000, 1900000], row_h=560000, sz=1800)
    set_para(shape(t, "TextBox 6"), "12강부터는 가상 병원 CDW 로 이 일들을 직접 해 봅니다.")
    move_y(t, "TextBox 6", bottom + 250000)


def before_after(t):
    set_title(t, "CDW가 없으면, 있으면")
    set_para(shape(t, "TextBox 4"), "같은 질문에 답하는 데 걸리는 시간이 다릅니다")
    set_para(shape(t, "TextBox 5"), "예) “작년에 우리 병동 낙상은 몇 건이고, 어느 근무조에 많았나?”")
    set_para(shape(t, "Panel Head 7"), "CDW가 없으면 — 차트를 한 장씩")
    fill(shape(t, "TextBox 8"), [(0, ["환자 명단을 받아 EMR 화면을 한 명씩 열어 봄"]),
                                 (1, ["보고서 · 간호기록에서 날짜와 근무조를 옮겨 적음"]),
                                 (2, ["몇 주가 걸리고, 사람마다 세는 기준이 달라짐"])])
    set_para(shape(t, "Panel Head 10"), "CDW가 있으면 — 조건으로 한 번에")
    fill(shape(t, "TextBox 11"), [(0, ["기간 · 병동 · 사건 종류를 조건으로 적어 한 번에 추출"]),
                                  (1, ["다음 달에도 같은 조건으로 다시 뽑을 수 있음"]),
                                  (2, ["숫자가 이상하면 어느 조건 때문인지 바로 확인"])])
    fill(shape(t, "TextBox 12"), [(0, ["CDW는 ‘자료를 찾는 일’을 줄이고 ‘자료를 읽는 일’에 시간을 쓰게 해 줍니다."]),
                                  (1, ["그래서 데이터 사전 · 요청서로 조건을 정확히 적는 힘이 중요합니다 (3 · 4절)."])])


def db_slide(t):
    set_title(t, "가상 병원 CDW — 12강부터 쓰는 실습 DB")
    set_para(shape(t, "TextBox 4"), f"2024년 · 병동 6곳 · 병상 {BEDS}개 · 환자 {COUNTS['환자']:,}명 · 입원 {COUNTS['입원']:,}건")
    bottom = table_fill(t, ["표", "한 행", "주요 열", "쓰는 곳"], [list(r) for r in TABLES],
                        widths=[1500000, 2400000, 5600000, 2300000], row_h=430000, sz=1500, head_sz=1700)
    set_para(shape(t, "TextBox 6"), "수업용 가상 자료입니다 (실제 병원 자료 아님). 열 이름은 앞 장 그림과 같습니다.")
    move_y(t, "TextBox 6", bottom + 200000)


def main(src, out):
    d = Deck(src)
    s11 = d.find("11강. CDW 구조와 분석 업무 흐름")
    s11_end = d.find("11주차 강의 정리")
    L11 = d.between(s11, s11_end)
    assert not any("CDW로 무엇을 하나 — 병원에서 쓰는 예" in texts(d.tree(s)) for s in L11), "이미 고침"

    # 새 슬라이드 3장
    t, rel = d.clone(d.find("CDW에서 자주 보는 표", within=L11)); uses_slide(t)
    a = d.insert_after(d.find("운영 DB와 CDW", within=L11), t, rel)
    t, rel = d.clone(d.find("CDW를 쓰는 방법", within=L11)); before_after(t)
    d.insert_after(a, t, rel)
    s291 = d.find("수업에서 쓰는 가상 CDW 표", within=L11)
    t, rel = d.clone(d.find("CDW에서 자주 보는 표", within=L11)); db_slide(t)
    d.insert_after(s291, t, rel)

    # 고침
    t = d.tree(s291)
    set_title(t, "가상 병원 CDW — 핵심 네 표")
    set_para(shape(t, "TextBox 4"), "12강부터 실습 · 과제 2 에서 실제로 쓰는 표입니다 (가상 자료)")
    replace_text(t, "· JOIN하면 행이 늘어남 → 12강 오류 2", "· JOIN하면 행이 늘어남 → 12강에서 직접 확인")
    t = d.tree(d.find("요청서를 SQL 조건으로 옮기기", within=L11))
    set_para(shape(t, "TextBox 4"), "앞 장 요청서의 한 줄 한 줄이 WHERE의 한 줄이 됩니다 (가상 병원 CDW)")
    set_para(shape(t, "Tag"), f"가상 병원 CDW 에서 그대로 실행하면 → 퇴원 {N_DIS}건 · 환자 {N_PT}명 (12강부터 직접 실행)")
    t = d.tree(s11_end)
    runs = list(shape(t, "Next 5").iter(A + "r"))
    assert len(runs) == 2 and runs[0].findtext(A + "t") == "다음 시간", [r.findtext(A + "t") for r in runs]
    runs[1].find(A + "t").text = NEXT12
    d.save(out)
    print(f"11강: 새 슬라이드 3장 · 고친 슬라이드 3장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
