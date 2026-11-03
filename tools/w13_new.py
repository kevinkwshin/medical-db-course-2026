# -*- coding: utf-8 -*-
"""13강 새 구성: '의료 질 · 간호 지표 만들기' — 가상 병원 CDW (data/hospital_mini.duckdb), 2026-11-03 강사 결정.

9강과 같은 aact 당뇨 코호트로 단계별 추출을 다시 하던 구성을, 병원의 질 · 간호 지표로 바꿈 (요청서 · 기준일 · 검산표 · 작은 칸 · 해석은 유지).
  1. 의료 질 지표       표: 지표마다 분자 · 분모
  2. 지표 정의서        지표 정의서(30일 재입원율) · 되물을 것 · SQL 조건으로 · 꼭 적는 세 가지 · 기준일 정하기 · 기준일 이후 정보
  3. 30일 재입원율      1단계 분모(사망 · 전원 제외) · 2단계 관찰 기간 · 3단계 분자(입원 표를 두 번, LEFT JOIN) · 4단계 병동별 · 정리
  4. 간호 업무량        근무표 · 근무조별 간호사 1인당 환자 수(두 열로 JOIN) · 병동별 밤 근무 · 정리
  5. 검산표와 해석      검산표 · 결과표를 내보내기 전에 · 작은 칸 가리기(사망 퇴원) · 결과 해석 · 정리
  6. 정리               용어 · 과제 2 제출 안내(10문항 × 2점) · 자주 막히는 부분 · 강의 정리
  + 14강 '지난시간 리뷰' 를 새 13강 정리에 맞춤
지우는 슬라이드: aact 사례(관찰 기간 BETWEEN · 단계별 추출 · 국가별 · 작은 칸) · '병원 사례 — 30일 재입원율'(지표 정의서와 겹침)
w12_new.py 를 먼저 실행한 덱에 씀 ('기준일 정하기' · '기준일 이후 정보' 가 13강에 와 있어야 함)
사용: python3 tools/w13_new.py <덱.pptx> <결과.pptx>
"""
import os, sys, re
import duckdb
import w10_slides
from w10_slides import build
from w10_tx_more import fill
from slidekit import A, P, Deck, texts, shape, set_para, set_title, table_fill, move_y, sql_paras, KW_SQL
from w12_new import agenda, summary_slide

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = duckdb.connect(os.path.join(ROOT, "data", "hospital_mini.duckdb"), read_only=True)
rows = lambda q: h.execute(q).fetchall()
fmt = lambda v: f"{v:,}" if isinstance(v, int) else str(v)
TITLE13 = "13강. 의료 질 · 간호 지표 만들기"
AG = [("의료 질 지표", "무엇을 재는가"), ("지표 정의서", "분모 · 분자 · 기준일"), ("30일 재입원율", "단계별로 구하기"),
      ("간호 업무량", "간호사 1인당 환자 수"), ("검산표와 해석", "숫자를 믿을 수 있게"), ("정리", "과제 2 제출")]

# ---------------------------------------------------------------- 숫자
D1 = ["SELECT COUNT(*) AS 퇴원건수", "FROM 입원", "WHERE 퇴원일 BETWEEN '2024-01-01' AND '2024-12-31'", "  AND 퇴원형태 NOT IN ('사망', '전원');"]
D2 = ["SELECT COUNT(*) AS 퇴원건수", "FROM 입원", "WHERE 퇴원일 BETWEEN '2024-01-01' AND '2024-12-01'", "  AND 퇴원형태 NOT IN ('사망', '전원');"]
N_ALL = rows("SELECT COUNT(*) FROM 입원 WHERE 퇴원일 BETWEEN '2024-01-01' AND '2024-12-31'")[0][0]
N_D1, N_D2 = rows(" ".join(D1))[0][0], rows(" ".join(D2))[0][0]
RE_SQL = ["SELECT COUNT(DISTINCT 퇴원.입원ID) AS 분모,",
          "       COUNT(DISTINCT CASE WHEN 다음입원.입원ID IS NOT NULL",
          "                 THEN 퇴원.입원ID END) AS 분자",
          "FROM 입원 AS 퇴원",
          "LEFT JOIN 입원 AS 다음입원",
          "  ON 다음입원.환자ID = 퇴원.환자ID",
          "  AND 다음입원.입원일 BETWEEN 퇴원.퇴원일 + 1",
          "                       AND 퇴원.퇴원일 + 30",
          "  AND 다음입원.계획입원 = 'N'",
          "WHERE 퇴원.퇴원일 BETWEEN '2024-01-01' AND '2024-12-01'",
          "  AND 퇴원.퇴원형태 NOT IN ('사망', '전원');"]
DEN, NUM = rows(" ".join(RE_SQL))[0]
RATE = round(100.0 * NUM / DEN, 1)
NUM_PLAN = rows(" ".join(RE_SQL).replace("  AND 다음입원.계획입원 = 'N'", ""))[0][1]
DEN_INNER = rows(" ".join(RE_SQL).replace("LEFT JOIN", "JOIN"))[0][0]
assert (N_ALL, N_D1, N_D2, DEN, NUM, RATE) == (9825, 8887, 8137, 8137, 582, 7.2), (N_ALL, N_D1, N_D2, DEN, NUM, RATE)
WARD_SQL = ["SELECT 퇴원.병동,", "       COUNT(DISTINCT 퇴원.입원ID) AS 분모,", "       COUNT(DISTINCT CASE WHEN 다음입원.입원ID IS NOT NULL",
            "                 THEN 퇴원.입원ID END) AS 분자", "-- FROM · LEFT JOIN · WHERE 는 3단계와 같음", "GROUP BY 퇴원.병동", "ORDER BY 퇴원.병동;"]
WARD_RUN = " ".join(RE_SQL[:3]).replace("SELECT ", "SELECT 퇴원.병동, ") + " " + " ".join(RE_SQL[3:]).rstrip(";") + " GROUP BY 퇴원.병동 ORDER BY 퇴원.병동"
R_WARD = rows(WARD_RUN)
WRATE = {w: round(100.0 * n / d_, 1) for w, d_, n in R_WARD}
hi_w = max(WRATE, key=WRATE.get); lo_w = min(WRATE, key=WRATE.get)
DUTY1 = ["SELECT 근무조, 간호사수", "FROM 근무", "WHERE 병동 = '51병동'", "  AND 근무일 = '2024-01-01'", "ORDER BY 근무조;"]
R_DUTY1 = rows(" ".join(DUTY1))
CEN1 = rows("SELECT 재원환자수 FROM 병동일보 WHERE 병동 = '51병동' AND 날짜 = DATE '2024-01-01'")[0][0]
SHIFT = ["SELECT 근무조,", "       ROUND(SUM(재원환자수) * 1.0 / SUM(간호사수), 1)", "         AS 간호사1인당", "FROM 근무", "JOIN 병동일보",
         "  ON 근무.병동 = 병동일보.병동", " AND 근무.근무일 = 병동일보.날짜", "GROUP BY 근무조", "ORDER BY 근무조;"]
R_SHIFT = rows(" ".join(SHIFT))
AVG_RATIO = dict(rows("SELECT 근무조, ROUND(AVG(재원환자수 * 1.0 / 간호사수), 1) FROM 근무 JOIN 병동일보 ON 근무.병동 = 병동일보.병동 AND 근무.근무일 = 병동일보.날짜 GROUP BY 1"))
NIGHT = ["SELECT 근무.병동,", "       ROUND(SUM(재원환자수) * 1.0 / SUM(간호사수), 1)", "         AS 간호사1인당", "FROM 근무", "JOIN 병동일보",
         "  ON 근무.병동 = 병동일보.병동", " AND 근무.근무일 = 병동일보.날짜", "WHERE 근무조 = 'N'", "GROUP BY 근무.병동", "ORDER BY 근무.병동;"]
R_NIGHT = rows(" ".join(NIGHT))
SMALL = ["SELECT 병동, 보험유형,", "       CASE WHEN COUNT(*) < 5 THEN '5 미만'", "            ELSE CAST(COUNT(*) AS VARCHAR)",
         "       END AS 사망퇴원", "FROM 입원", "WHERE 퇴원형태 = '사망'", "GROUP BY 병동, 보험유형", "ORDER BY 병동, 보험유형;"]
R_SMALL = rows(" ".join(SMALL))
N_LT5 = sum(v == "5 미만" for *_, v in R_SMALL)
SHOW = [r for r in R_SMALL if r[0] in ("61병동", "62병동", "71병동")]
assert N_LT5 >= 2 and any(v == "5 미만" for *_, v in SHOW)

SQL_SLIDES = {
    "d1": dict(title="1단계 — 분모: 2024년 퇴원 건", question="2024년에 퇴원한 입원 중 사망 · 전원을 빼면 몇 건?",
               sql_lines=D1, hl_lines={3}, label="결과", header=["퇴원건수"], rows=[[fmt(N_D1)]], hl_rows=set(), widths=[4724400],
               notes=[("제외", f"2024년 퇴원 {N_ALL:,}건 중 사망 · 전원 {N_ALL - N_D1:,}건을 뺌 — 집으로 퇴원한 건만 재입원을 지켜봄"),
                      ("세는 단위", "퇴원 건 (같은 환자의 여러 퇴원은 각각 셈)")]),
    "d2": dict(title="2단계 — 관찰 기간이 다 찬 퇴원만", question="퇴원 뒤 30일을 다 지켜볼 수 있는 퇴원은 몇 건?",
               sql_lines=D2, hl_lines={2}, label="결과", header=["퇴원건수"], rows=[[fmt(N_D2)]], hl_rows=set(), widths=[4724400],
               notes=[("관찰 기간", "자료 기준일이 2024-12-31 이라 12월 2일 이후 퇴원은 30일을 다 볼 수 없음"),
                      ("확인", f"{N_D1 - N_D2:,}건이 빠짐. 빼지 않으면 재입원을 못 본 퇴원이 섞여 재입원율이 낮게 나옴")]),
    "ward": dict(title="4단계 — 병동별 재입원율", question="병동별로 나누면 30일 재입원율은?",
                 sql_lines=WARD_SQL, hl_lines={0, 5}, label="결과", header=["병동", "분모", "분자"],
                 rows=[[w, fmt(d_), fmt(n)] for w, d_, n in R_WARD], hl_rows=set(), widths=[1574800, 1574800, 1574800],
                 notes=[("재입원율", f"가장 높은 {hi_w} {WRATE[hi_w]}% ~ 가장 낮은 {lo_w} {WRATE[lo_w]}% (전체 {RATE}%)"),
                        ("조심", "병동마다 환자의 나이 · 질환이 달라 그대로 비교하면 안 됨 (5절 해석)")]),
    "duty1": dict(title="근무표 — 근무조마다 간호사 수", question="51병동 1월 1일 근무표는?",
                  sql_lines=DUTY1, hl_lines=set(), label="결과", header=["근무조", "간호사수"],
                  rows=[[s, fmt(n)] for s, n in R_DUTY1], hl_rows={2}, widths=[2362200, 2362200],
                  notes=[("한 행 = 병동 × 날짜 × 근무조", "D 낮 · E 초번 · N 밤"),
                         ("그날 재원 " + str(CEN1) + "명", f"밤에는 간호사 1명이 {CEN1} ÷ {R_DUTY1[2][1]} = {CEN1 / R_DUTY1[2][1]:.0f}명을 맡음")]),
    "shift": dict(title="근무조별 간호사 1인당 환자 수", question="1년 동안 근무조별로 간호사 1명이 맡은 환자는 몇 명?",
                  sql_lines=SHIFT, hl_lines={5, 6}, label="결과", header=["근무조", "간호사1인당"],
                  rows=[[s, str(v)] for s, v in R_SHIFT], hl_rows=set(), widths=[2362200, 2362200],
                  notes=[("두 열로 JOIN", "병동과 날짜가 모두 같아야 같은 날 같은 병동 (ON … AND …)"),
                         ("확인", f"밤(N) {dict(R_SHIFT)['N']}명 — 낮(D) {dict(R_SHIFT)['D']}명보다 많음. 밤 근무의 부담")]),
    "night": dict(title="병동별 밤 근무 간호사 1인당 환자 수", question="밤 근무(N)만 보면 병동마다 얼마나 다른가?",
                  sql_lines=NIGHT, hl_lines={7}, label="결과", header=["병동", "간호사1인당"],
                  rows=[[w, str(v)] for w, v in R_NIGHT], hl_rows=set(), widths=[2362200, 2362200],
                  notes=[("확인", f"{min(R_NIGHT, key=lambda r: r[1])[0]} {min(r[1] for r in R_NIGHT)}명 ~ {max(R_NIGHT, key=lambda r: r[1])[0]} {max(r[1] for r in R_NIGHT)}명"),
                         ("함께 볼 때", "과제 2 의 낙상률과 나란히 볼 수 있지만, 함께 높다고 원인이라고 할 수는 없음")]),
    "small": dict(title="작은 칸 가리기 — 사망 퇴원 표", question="병동 × 보험유형별 사망 퇴원 건수를 내보내려면?",
                  sql_lines=SMALL, hl_lines={1, 2, 3}, label=f"결과 ({len(R_SMALL)}행 중 일부)", header=["병동", "보험유형", "사망퇴원"],
                  rows=[list(r) for r in SHOW], hl_rows={i for i, r in enumerate(SHOW) if r[2] == "5 미만"},
                  widths=[1424400, 1800000, 1500000],
                  notes=[("CASE WHEN", "5건 미만이면 '5 미만', 아니면 숫자를 글자로 바꿔(CAST) 한 열에 씀"),
                         ("왜", f"사망처럼 민감한 칸은 몇 명만 있어도 누구인지 좁혀짐 — {len(R_SMALL)}칸 중 {N_LT5}칸을 가림")]),
}

SUMMARY = {
    3: ([("① ", "분모", " = 2024년 퇴원 건 (사망 · 전원 제외, 관찰 기간이 다 찬 것만)"),
         ("② ", "분자", " = 퇴원 +1~30일 안의 비계획 재입원 (입원 표를 두 번, LEFT JOIN)"),
         ("③ ", "정의가 숫자를 바꾼다", f" — 계획입원까지 넣으면 {NUM_PLAN:,}건 ({round(100.0 * NUM_PLAN / DEN, 1)}%)")],
        ("잠깐 생각해 봅시다", f"  {hi_w} 재입원율이 가장 높습니다. 진료가 나쁘다고 할 수 있을까요?",
         "아닙니다. 나이가 많고 폐렴 · 만성 질환 환자가 많은 병동은 원래 재입원이 잦습니다 (위험 보정이 필요).")),
    4: ([("① ", "근무 표의 한 행", " = 병동 × 날짜 × 근무조"),
         ("② ", "간호사 1인당 환자 수", " = 재원 환자 ÷ 간호사 (두 열로 JOIN)"),
         ("③ ", "밤 근무", "의 부담이 가장 크다")],
        ("잠깐 생각해 봅시다", "  ‘날마다 나눈 값의 평균’으로 구해도 같을까요?",
         f"조금 다릅니다 (밤 {dict(R_SHIFT)['N']} → {AVG_RATIO['N']}명). 어떤 방법으로 셌는지 지표 정의서에 적어 둡니다.")),
    5: ([("① ", "검산표", " 로 단계마다 건수와 빠진 이유를 남긴다"),
         ("② ", "작은 칸", " 은 가려서 내보낸다 (CASE WHEN · CAST)"),
         ("③ ", "말할 수 있는 것과 없는 것", " 을 나눠 쓴다")],
        ("잠깐 생각해 봅시다", f"  {N_D1:,}건에서 {N_D2:,}건으로 줄었습니다. 무엇을 설명해야 할까요?",
         f"12월 2일 이후 퇴원 {N_D1 - N_D2:,}건은 30일을 다 볼 수 없어 뺐다는 것. 검산표에 그 이유를 적어 둡니다.")),
}

INDICATORS = [("30일 재입원율", "30일 안에 비계획 재입원한 퇴원 건", "퇴원 건 (사망 · 전원 제외)", "QI · 적정성평가"),
              ("낙상 발생률", "낙상 건수", "재원일수 ÷ 1,000", "간호부 · 환자안전 (과제 2)"),
              ("욕창 발생률", "새로 생긴 욕창 건수", "재원일수 ÷ 1,000", "간호부"),
              ("간호사 1인당 환자 수", "재원 환자 수", "근무 간호사 수", "간호부 · 인력 배치"),
              ("병상 가동률", "재원일수", "병상 수 × 날짜 수", "원무 (12강)")]
TERMS = [("지표", "Indicator", "분자 ÷ 분모로 만든 숫자 (질 · 업무량)"),
         ("지표 정의서", "—", "분모 · 분자 · 제외 · 기준일 · 관찰 기간을 적은 문서"),
         ("기준일", "Index Date", "대상마다 분석의 출발점이 되는 날짜"),
         ("관찰 기간", "Observation Period", "기준일 뒤로 결과를 지켜보는 기간"),
         ("비계획 재입원", "Unplanned Readmission", "미리 계획하지 않은 재입원"),
         ("간호사 1인당 환자 수", "Nurse-to-Patient Ratio", "재원 환자 수 ÷ 근무 간호사 수"),
         ("검산표", "—", "단계마다 건수와 변화량을 적어 둔 표"),
         ("소수 셀", "Small Cell", "사람 수가 아주 적어 개인이 드러날 수 있는 칸")]


def main(src, out):
    d = Deck(src)
    w10_slides.KW = KW_SQL
    s13 = d.find("13강. CDW 실무 사례")
    e13 = d.find("13주차 강의 정리")
    L = d.between(s13, e13)
    F = lambda line, also=None: d.find(line, also, within=L)
    tmpl_sql = d.find("2단계 — 값 살펴보기")
    tmpl_tab = d.find("CDW에서 자주 보는 표")
    tmpl_sum = d.find("여기까지 정리", "① CDW = 분석용으로 따로 모아 둔 읽기 전용 복사본")

    def new_sql(key):
        return d.insert_after(e13, build(d.tree(tmpl_sql), **SQL_SLIDES[key]), d.rels(tmpl_sql))

    def new_sum(sec):
        t, rel = d.clone(tmpl_sum); summary_slide(t, *SUMMARY[sec])
        return d.insert_after(e13, t, rel)

    # ---- 표지 · 리뷰 · 학습 목표
    t = d.tree(s13)
    for s in t.iter(P + "sp"):
        tx = texts(s)
        if tx and tx[0] == "13강. CDW 실무 사례":
            set_para(s, TITLE13)
        elif tx[:3] == ["요청서에서 코호트 정의까지", "단계별 추출과 검산표", "결과 해석과 과제 2 제출"]:
            fill(s, [(0, ["지표 정의서 — 분모 · 분자 · 기준일"]), (1, ["30일 재입원율과 간호사 1인당 환자 수"]), (2, ["검산표 · 작은 칸 · 결과 해석"])])
    rv = F("지난시간 리뷰")
    fill(shape(d.tree(rv), "TextBox 4"), [(0, ["입원 건수", "와 ", "환자 수", "는 다르다 — 세는 단위와 날짜 기준"]),
                                          (1, ["재원일수 · 병상 가동률", "은 퇴원일과 병동일보로"]),
                                          (2, ["JOIN 전에 한 행의 단위", "를 확인한다 (1 : N)"]),
                                          (3, ["오늘은 이 숫자들로 의료 질 · 간호 지표를 만듭니다."])])
    t = d.tree(F("13주차 학습 목표"))
    set_para(shape(t, "TextBox 4"), "지표를 정의하고, 계산하고, 내보내기")
    fill(shape(t, "TextBox 6"), [(0, ["① 지표를 분모 · 분자 · 기준일로 정의한다"]), (1, ["② 30일 재입원율을 단계별로 구한다"]),
                                 (2, ["③ 근무조별 간호사 1인당 환자 수를 구한다"]), (3, ["④ 검산표 · 작은 칸 · 해석으로 내보낸다"])])
    agenda(t, "Step", AG, "  ")
    divs = [F("1. 요청서 읽기"), F("2. 코호트 정의"), F("3. 단계별 추출"), F("4. 검산표"), F("5. 결과 해석"), F("6. 정리")]
    for k, s in enumerate(divs):
        t = d.tree(s)
        set_title(t, f"{k + 1}. {AG[k][0]}")
        set_para(shape(t, "TextBox 4"), AG[k][1])
        agenda(t, "Sec", AG, "   ")

    # ---- 있던 슬라이드 고치기
    req, ask, cdef, three = F("요청서 읽기"), F("요청자에게 되물어야 할 것"), F("코호트 정의", "요청서를 SQL 조건으로 바꾸기"), F("코호트 정의에 꼭 적는 세 가지")
    idx, leak, chk, summ = F("기준일(Index Date) 정하기"), F("오류 12 — 기준일 이후 정보가 섞임"), F("검산표", "단계별 건수를 기록합니다"), F("여기까지 정리")
    sqlpage, interp, export = F("30일 재입원율을 SQL로"), F("결과 해석"), F("결과표를 내보내기 전에")
    terms, sub, stuck = F("13주차 용어 정리"), F("과제 2 제출 안내"), F("과제 2를 할 때 자주 막히는 부분")
    drop = [F("관찰 기간을 SQL로 — BETWEEN"), F("단계별 추출 — 9강 방식 그대로"), F("국가별로 나누기"), F("병원 사례 — 30일 재입원율"),
            F("작은 칸 가리기 — CASE WHEN 으로 ‘5 미만’")]

    t = d.tree(req)
    set_title(t, "지표 정의서 — 30일 재입원율"); set_para(shape(t, "TextBox 4"), "오늘 함께 만들어 볼 지표")
    table_fill(t, ["항목", "내용"], [["지표 이름", "30일 비계획 재입원율"],
                                     ["질문", "2024년에 퇴원한 환자 중 30일 안에 다시 입원한 비율은?"],
                                     ["분모", "2024년 퇴원 건 중 사망 · 전원 제외"],
                                     ["분자", "퇴원 다음 날부터 30일 안에 계획하지 않은 재입원이 있는 퇴원 건"],
                                     ["세는 단위", "퇴원 건 1건 (같은 환자의 여러 퇴원은 각각)"],
                                     ["기준일 · 관찰 기간", "퇴원일 · 퇴원 다음 날 ~ 30일"],
                                     ["결과 형태", "전체 재입원율 1개 + 병동별 표 (작은 칸은 가림)"]])
    fill(shape(t, "TextBox 6"), [(0, ["이 정의서만으로 SQL을 쓸 수 있을까요? 아직 정하지 않은 것이 있습니다."]),
                                 (1, ["계획입원(항암 등)을 넣을지, 12월 퇴원처럼 30일을 다 못 본 퇴원을 어떻게 할지가 빠져 있습니다."])])
    t = d.tree(ask)
    fill(shape(t, "TextBox 5"), [(0, ["① ", "세는 단위가 무엇인가요?"]), (1, ["환자 수인가, 퇴원 건수인가 (한 환자가 여러 번 퇴원)"]),
                                 (2, ["① ", "‘재입원’의 기준은 무엇인가요?"]), (3, ["계획한 입원(항암 · 단계 수술)도 넣는가, 같은 병원만 보는가"]),
                                 (4, ["① ", "제외할 대상이 더 있나요?"]), (5, ["사망 · 전원 퇴원은 재입원을 지켜볼 수 없음"]),
                                 (6, ["① ", "관찰 기간이 모자란 퇴원은 어떻게 할까요?"]), (7, ["12월 퇴원은 자료 기준일까지 30일이 안 됨"]),
                                 (8, ["되묻는 것은 일을 늦추는 것이 아니라 다시 하지 않기 위한 것입니다."])])
    rs = [p for p in shape(t, "TextBox 5").findall(f"{P}txBody/{A}p")]
    for k, p_ in zip((0, 2, 4, 6), "①②③④"):
        rs[k].findall(A + "r")[0].find(A + "t").text = p_ + " "
    t = d.tree(cdef)
    set_title(t, "지표 정의서를 SQL 조건으로"); set_para(shape(t, "TextBox 4"), "한 줄 한 줄이 WHERE · ON 의 한 줄이 됩니다")
    fill(shape(t, "TextBox 5"), [(0, ["정의서를 ", "SQL로 옮길 수 있는 형태", "로 다시 적습니다."])])
    table_fill(t, ["항목", "SQL로 옮긴 정의"], [["세는 단위", "퇴원 건 1건 (COUNT(DISTINCT 퇴원.입원ID))"],
                                              ["대상 기간", "퇴원.퇴원일 BETWEEN '2024-01-01' AND '2024-12-01'"],
                                              ["제외", "퇴원.퇴원형태 NOT IN ('사망', '전원')"],
                                              ["분자", "다음입원.입원일 BETWEEN 퇴원.퇴원일 + 1 AND 퇴원.퇴원일 + 30"],
                                              ["비계획만", "다음입원.계획입원 = 'N'"],
                                              ["주의", "같은 환자의 다음 입원을 찾으려고 입원 표를 두 번 씀 (퇴원 · 다음입원)"]])
    fill(shape(t, "TextBox 7"), [(0, ["이렇게 적어 두면 누가 해도 같은 숫자가 나오고, 나중에 방법을 설명할 수 있습니다."])])
    t = d.tree(three)
    set_title(t, "지표 정의서에 꼭 적는 세 가지")
    table_fill(t, ["항목", "무엇을 정하나", "30일 재입원율에서는"], [["진입 사건", "어떤 일이 있었던 대상을 뽑나", "2024년 1~11월 퇴원 (사망 · 전원 제외)"],
                                                              ["기준일", "각 대상의 출발점을 언제로 잡나", "퇴원일"],
                                                              ["관찰 기간", "기준일 뒤로 얼마를 보나", "퇴원 다음 날 ~ 30일"]])
    t = d.tree(leak)
    set_title(t, "기준일 이후 정보가 섞이면")
    set_para(shape(t, "Concept tag"), "가상 병원 CDW")
    t = d.tree(sqlpage)
    set_title(t, "3단계 — 분자: 30일 안 비계획 재입원")
    sz = int(next(shape(t, "SQL").iter(A + "rPr")).get("sz"))
    sql_paras(shape(t, "SQL"), RE_SQL, sz)
    fill(shape(t, "Map"), [(0, ["SQL 과 지표 정의서"]), (1, ["기준일"]), (2, ["WHERE의 퇴원일 = 각 퇴원 건의 출발점"]),
                           (3, ["분모"]), (4, ["1~2단계와 같음 (사망 · 전원 제외, 12월 1일까지)"]),
                           (5, ["분자"]), (6, ["퇴원 +1~30일 안에 계획하지 않은 다음 입원이 있는 건"]),
                           (7, ["왜 LEFT JOIN"]), (8, [f"재입원이 없는 퇴원도 분모에 남아야 함 (JOIN 이면 분모가 {DEN_INNER:,}건으로 줄어듦)"]),
                           (9, ["왜 별명"]), (10, ["같은 입원 표를 두 번 쓰므로 역할 이름(퇴원 · 다음입원)이 필요"])])
    fill(shape(t, "Bottom"), [(0, ["결과", f"  분모 {DEN:,} · 분자 {NUM:,} → 재입원율 {RATE}%. 계획입원까지 넣으면 {NUM_PLAN:,}건 — 정의가 숫자를 바꿉니다."])])
    set_para(shape(t, "Tag"), "가상 병원 CDW 에서 실행 (11강 「가상 병원 CDW — 핵심 네 표」)")
    t = d.tree(chk)
    fill(shape(t, "TextBox 5"), [(0, ["단계마다 건수를 적어 두면 ", "어디에서 얼마나 줄었는지", " 설명할 수 있습니다."])])
    table_fill(t, ["단계", "적용한 조건", "건수", "변화"], [["① 2024년 퇴원", "퇴원일이 2024년", fmt(N_ALL), "—"],
                                                     ["② 사망 · 전원 제외", "퇴원형태", fmt(N_D1), f"-{N_ALL - N_D1:,}"],
                                                     ["③ 관찰 기간이 다 참 (분모)", "퇴원일 ≤ 12월 1일", fmt(N_D2), f"-{N_D1 - N_D2:,}"],
                                                     ["④ 30일 안 비계획 재입원 (분자)", "다음 입원 +1~30일 · 계획입원 N", fmt(NUM), "—"],
                                                     ["⑤ 재입원율", "④ ÷ ③", f"{RATE} %", "—"]])
    fill(shape(t, "TextBox 7"), [(0, [f"③에서 {N_D1 - N_D2:,}건이 빠졌습니다.", " 12월 2일 이후 퇴원이라 30일을 다 볼 수 없는 퇴원입니다."]),
                                 (1, [f"이 표가 있으면 “왜 {N_ALL:,}건이 아니라 {N_D2:,}건이 분모인가?”에 바로 답할 수 있습니다."])])
    t = d.tree(interp)
    fill(shape(t, "TextBox 7"), [(0, ["이 가상 병원 자료 안에서, 정해진 정의로"]), (1, [f"2024년 1~11월 퇴원 {N_D2:,}건 중"]),
                                 (2, [f"{NUM:,}건({RATE}%)이 30일 안에 비계획 재입원"]), (3, ["자료: 가상 병원 CDW (수업용, 2024년)"]),
                                 (4, ["자료 기준일 2024-12-31"])])
    fill(shape(t, "TextBox 10"), [(0, [f"“{hi_w}가 진료를 못 한다”"]), (1, ["나이 · 질환(중증도)을 보정하지 않음"]),
                                  (2, ["“다른 병원 재입원까지 센 숫자다”"]), (3, ["우리 병원 기록만 있음"]),
                                  (4, ["“간호사가 적어서 재입원이 많다”"])])
    summary_slide(d.tree(summ), *SUMMARY[5])
    t = d.tree(terms)
    table_fill(t, ["용어", "영어", "뜻 (한 줄)"], [list(x) for x in TERMS])
    t = d.tree(sub)
    set_para(shape(t, "TextBox 4"), "20점 · 10문항 × 2점 · 노트북 파일 하나")
    fill(shape(t, "TextBox 5"), [(0, ["제출물", ": 노트북 파일 하나 (과제2.ipynb)"]),
                                 (1, ["S1~S5 · E1~E3 · T1 · T2 — 10문항이 모두 ✅ 인 상태로 저장"]),
                                 (2, ["문항마다 2점, 합계 20점 (모두 SQL 문항, 설명 쓰기 없음)"]),
                                 (3, ["값이나 열 이름이 필요한 문항은 바로 위 조회 셀부터 실행"]),
                                 (4, ["마감", ": 2026-12-08(화), LMS 제출"]),
                                 (5, ["도움이 되는 자료: 10 · 12주차 실습 노트북, 오늘의 검산표"])])
    t = d.tree(stuck)
    fill(shape(t, "TextBox 5"), [(0, ["① 어디부터 하나요"]),
                                 (1, ["S1~S3 은 분자 → 분모 → 낙상률 순서로, S4 · S5 는 GROUP BY · 재원일수(12주차), E 는 12주차, T 는 10주차 UPDATE · INSERT 로."]),
                                 (2, ["② 숫자가 정답과 다릅니다"]),
                                 (3, ["검산표에서 건수가 어느 단계부터 달라졌는지 찾고, 그 단계의 조건을 확인하세요."]),
                                 (4, ["③ 동료 SQL 의 어디가 틀렸는지 모르겠습니다"]),
                                 (5, ["오류 없이 숫자만 틀립니다. 세는 단위(중복) · 날짜 계산(일 수) · 값의 띄어쓰기를 차례로 확인하세요."]),
                                 (6, ["④ 열 이름이나 값을 모르겠습니다"]),
                                 (7, ["문항 바로 위 조회 셀(DESCRIBE · DISTINCT)을 먼저 실행해 확인합니다."])])
    t = d.tree(e13)
    fill(shape(t, "TextBox 4"), [(0, ["지표는 ", "지표 정의서", "(분모 · 분자 · 제외 · 기준일)부터 적는다"]),
                                 (1, ["검산표", "로 단계마다 건수를 남겨 숫자를 설명한다"]),
                                 (2, ["결과에는 ", "기준 · 한계", "를 적고, 작은 칸은 가려서 내보낸다"])])

    # ---- 새 슬라이드 (13강 끝에 만들고 아래에서 순서를 다시 맞춤)
    t, rel = d.clone(tmpl_tab)
    set_title(t, "의료 질 지표 — 분자와 분모"); set_para(shape(t, "TextBox 4"), "지표 = 분자 ÷ 분모")
    bottom = table_fill(t, ["지표", "분자", "분모", "어디서 쓰나"], [list(x) for x in INDICATORS],
                        widths=[2500000, 3300000, 2900000, 3100000], row_h=560000, sz=1700)
    set_para(shape(t, "TextBox 6"), "분자 · 분모를 정확히 적는 것이 지표 만들기의 거의 전부입니다.")
    move_y(t, "TextBox 6", bottom + 250000)
    ind = d.insert_after(e13, t, rel)
    n = {k: new_sql(k) for k in SQL_SLIDES}
    sm3, sm4 = new_sum(3), new_sum(4)
    for s in drop:
        d.delete(s)

    order = [s13, rv, F("지표를 정의하고, 계산하고, 내보내기") if False else d.find("13주차 학습 목표"),
             divs[0], ind,
             divs[1], req, ask, cdef, three, idx, leak,
             divs[2], n["d1"], n["d2"], sqlpage, n["ward"], sm3,
             divs[3], n["duty1"], n["shift"], n["night"], sm4,
             divs[4], chk, export, n["small"], interp, summ,
             divs[5], terms, sub, stuck, e13]
    block = [s for s in d.slides()[d.index(s13):] if s in set(order)]
    assert len(order) == len(set(order)) and set(order) == set(block), (len(order), len(block))
    prev = d.slides()[d.index(s13) - 1]
    for s in order:
        d.lst.remove(s)
    for s in order:
        prev.addnext(s); prev = s

    # ---- 14강 지난시간 리뷰 (= 새 13강 정리)
    s14, e14 = d.find("14강. 빅데이터와 의료데이터 표준"), d.find("14주차 강의 정리")
    t = d.tree(d.find("지난시간 리뷰", within=d.between(s14, e14)))
    fill(shape(t, "TextBox 4"), [(0, ["지표는 ", "지표 정의서", "부터 적는다 (분모 · 분자 · 기준일)"]),
                                 (1, ["검산표", "로 단계별 건수를 남긴다"]),
                                 (2, ["결과에는 ", "기준 · 한계", "를 적고 작은 칸은 가린다"]),
                                 (3, ["지금까지는 ", "우리 병원 한 곳", "의 데이터를 다뤘습니다."]),
                                 (4, ["오늘은 여러 병원 · 여러 종류의 데이터를 어떻게 맞추는지 봅니다."])])
    d.save(out)
    print(f"13강: 새로 {len(SQL_SLIDES) + 3}장 · 지움 {len(drop)}장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
