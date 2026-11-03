# -*- coding: utf-8 -*-
"""12강 새 구성: '원무 데이터로 보는 병원 운영' — 가상 병원 CDW (data/hospital_mini.duckdb), 2026-11-03 강사 결정.

7~9강과 겹치던 'CDW 분석 오류 12가지(aact)' 를 원무 주제로 바꿈. 오류는 원무 예시 속에서 나옴.
  1. 원무 업무와 데이터   표: 원무 업무 → 남는 자료 · SQL: 환자 한 명의 입원 기록 (1 : N, 퇴원일 NULL)
  2. 입원과 퇴원 세기     입원 건수 vs 환자 수 · '2024년' 세 가지 기준 · 재원 중(IS NULL) · 정리
  3. 재원일수             퇴원일 − 입원일 · 병동별 평균 · 긴 재원(최댓값) · 정리
  4. 병상 가동률          병동일보 · 병동별 가동률
  5. 진료비와 청구        입원 1건의 항목 · 진료과별 건당 진료비 · 급여/비급여 · JOIN 함정(재원일수 6배)
                          · 청구 자료 ≠ 진료 기록 · 환자번호 앞자리 0 · 정리
  6. 정리                 용어 정리 · 과제 2 안내(10문항 × 2점, 설명 문항 없음) · 강의 정리
옮기는 슬라이드 (병원 개념 슬라이드는 버리지 않음)
  13강: '기준일(Index Date) 정하기' · '오류 12 — 기준일 이후 정보' ('코호트 정의에 꼭 적는 세 가지' 뒤, 13강 스크립트가 다시 다듬음)
  14강: '오류 점검 체크리스트' · '오류를 찾는 SQL 네 가지' · '빠진 값 자체가 정보입니다' ('데이터 품질 점검' 뒤),
        '코드가 바뀌면 추세가 끊깁니다' ('분류와 용어 — KCD와 SNOMED CT' 뒤)
지우는 슬라이드: aact 로 재현한 오류 1 · 3 · 4 · 5 · 6 · 8 · 9 · 10
슬라이드의 숫자는 모두 가상 병원 CDW 에서 계산 (같은 SQL 이 12주차 노트북에도 들어감)
사용: python3 tools/w12_new.py <덱.pptx> <결과.pptx>
"""
import os, sys, re, copy
import duckdb
import w10_slides
from w10_slides import build
from w10_tx_more import fill
from slidekit import A, P, Deck, texts, shape, set_para, set_title, replace_text, table_fill, move_y, sql_paras, KW_SQL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = duckdb.connect(os.path.join(ROOT, "data", "hospital_mini.duckdb"), read_only=True)
rows = lambda q: h.execute(q).fetchall()
fmt = lambda v: f"{v:,}" if isinstance(v, int) else ("NULL" if v is None else str(v))
TITLE12 = "12강. 원무 데이터로 보는 병원 운영"
NEXT13 = "  13강. 의료 질 · 간호 지표 만들기"
AG = [("원무 업무와 데이터", "접수에서 청구까지"), ("입원과 퇴원 세기", "건수와 환자 수"), ("재원일수", "퇴원일 − 입원일"),
      ("병상 가동률", "병동일보로 구하기"), ("진료비와 청구", "급여 · 비급여"), ("정리", "과제 2와 요약")]

# ---------------------------------------------------------------- 숫자 (가상 병원 CDW)
PID = rows("""SELECT 환자ID FROM 입원 GROUP BY 1 HAVING COUNT(*) = 3 AND SUM(CASE WHEN 퇴원일 IS NULL THEN 1 ELSE 0 END) = 1
               AND MIN(퇴원일 - 입원일) > 0 ORDER BY 1 LIMIT 1""")[0][0]
assert PID == "0139420", PID
Q_ONE = ["SELECT 입원ID, 병동, 입원일, 퇴원일", "FROM 입원", f"WHERE 환자ID = '{PID}'", "ORDER BY 입원일;"]
R_ONE = rows(" ".join(Q_ONE))
Q_CNT = ["SELECT COUNT(*) AS 입원건수,", "       COUNT(DISTINCT 환자ID) AS 환자수", "FROM 입원;"]
R_CNT = rows(" ".join(Q_CNT))
Q_3WAY = ["SELECT COUNT(CASE WHEN YEAR(입원일) = 2024", "                  THEN 1 END) AS 입원기준,",
          "       COUNT(CASE WHEN YEAR(퇴원일) = 2024", "                  THEN 1 END) AS 퇴원기준,",
          "       COUNT(*) AS 재원기준", "FROM 입원;"]
R_3WAY = rows(" ".join(Q_3WAY))
N_CARRY, N_STAY = rows("SELECT SUM(CASE WHEN 입원일 < DATE '2024-01-01' THEN 1 ELSE 0 END), SUM(CASE WHEN 퇴원일 IS NULL THEN 1 ELSE 0 END) FROM 입원")[0]
Q_STAY = ["SELECT 병동, COUNT(*) AS 재원중", "FROM 입원", "WHERE 퇴원일 IS NULL", "GROUP BY 병동", "ORDER BY 병동;"]
R_STAY = rows(" ".join(Q_STAY))
assert rows("SELECT COUNT(*) FROM 입원 WHERE 퇴원일 = NULL")[0][0] == 0 and sum(n for _, n in R_STAY) == N_STAY
Q_LOS1 = ["SELECT 입원ID, 입원일, 퇴원일,", "       퇴원일 - 입원일 AS 재원일수", "FROM 입원", f"WHERE 환자ID = '{PID}'", "ORDER BY 입원일;"]
R_LOS1 = rows(" ".join(Q_LOS1))
Q_ALOS = ["SELECT 병동, COUNT(*) AS 퇴원건수,", "       ROUND(AVG(퇴원일 - 입원일), 1) AS 평균재원일수", "FROM 입원",
          "WHERE 퇴원일 BETWEEN '2024-01-01' AND '2024-12-31'", "GROUP BY 병동", "ORDER BY 병동;"]
R_ALOS = rows(" ".join(Q_ALOS))
ALL_AVG, ALL_MED, ALL_MAX, N_SAME = rows("""SELECT ROUND(AVG(퇴원일 - 입원일), 1), MEDIAN(퇴원일 - 입원일), MAX(퇴원일 - 입원일),
    SUM(CASE WHEN 퇴원일 = 입원일 THEN 1 ELSE 0 END) FROM 입원 WHERE 퇴원일 IS NOT NULL""")[0]
Q_LONG = ["SELECT 입원ID, 병동, 퇴원일 - 입원일 AS 재원일수", "FROM 입원", "WHERE 퇴원일 IS NOT NULL",
          "ORDER BY 재원일수 DESC, 입원ID", "LIMIT 5;"]
R_LONG = rows(" ".join(Q_LONG))
Q_DAILY = ["SELECT 날짜, 재원환자수,", "       입원환자수 AS 입원, 퇴원환자수 AS 퇴원", "FROM 병동일보", "WHERE 병동 = '51병동'", "ORDER BY 날짜", "LIMIT 3;"]
R_DAILY = rows(" ".join(Q_DAILY))
Q_OCC = ["SELECT 병동일보.병동, 병상수,", "       SUM(재원환자수) AS 재원일수,", "       ROUND(100.0 * SUM(재원환자수)", "             / (병상수 * 366), 1) AS 가동률",
         "FROM 병동일보", "JOIN 병동 ON 병동일보.병동 = 병동.병동", "GROUP BY 병동일보.병동, 병상수", "ORDER BY 병동일보.병동;"]
R_OCC = rows(" ".join(Q_OCC))
OCC_ALL = rows("SELECT ROUND(100.0 * SUM(재원환자수) / (SELECT SUM(병상수) * 366 FROM 병동), 1) FROM 병동일보")[0][0]
AID = rows("""SELECT MIN(입원.입원ID) FROM 입원 JOIN 진료비 ON 입원.입원ID = 진료비.입원ID
              WHERE 병동 = '62병동' AND 퇴원일 IS NOT NULL AND 입원일 >= DATE '2024-01-01'
              GROUP BY 입원.입원ID HAVING COUNT(*) = 7 AND SUM(CASE WHEN 급여구분 = '비급여' THEN 1 ELSE 0 END) = 1
              ORDER BY 1 LIMIT 1""")[0][0]
Q_COST1 = ["SELECT 항목, 금액, 급여구분", "FROM 진료비", f"WHERE 입원ID = {AID}", "ORDER BY 진료비ID;"]
R_COST1 = rows(" ".join(Q_COST1))
Q_DEPT = ["SELECT 진료과,", "       COUNT(DISTINCT 진료비.입원ID) AS 입원건수,", "       ROUND(SUM(금액) / COUNT(DISTINCT 진료비.입원ID)",
          "             / 10000) AS 건당진료비", "FROM 진료비", "JOIN 입원 ON 진료비.입원ID = 입원.입원ID", "GROUP BY 진료과",
          "ORDER BY 건당진료비 DESC;"]
R_DEPT = rows(" ".join(Q_DEPT))
Q_PAY = ["SELECT 급여구분, SUM(금액) AS 금액,", "       ROUND(100.0 * SUM(금액)", "             / (SELECT SUM(금액) FROM 진료비), 1) AS 비율",
         "FROM 진료비", "GROUP BY 급여구분", "ORDER BY 급여구분;"]
R_PAY = rows(" ".join(Q_PAY))
TOP_NONPAY = rows("SELECT 항목 FROM 진료비 WHERE 급여구분 = '비급여' GROUP BY 항목 ORDER BY SUM(금액) DESC LIMIT 1")[0][0]
BAD_FAN = ["SELECT SUM(퇴원일 - 입원일) AS 재원일수", "FROM 입원", "JOIN 진료비", "  ON 입원.입원ID = 진료비.입원ID", "WHERE 퇴원일 IS NOT NULL;"]
GOOD_FAN = ["SELECT SUM(퇴원일 - 입원일) AS 재원일수", "FROM 입원", "WHERE 퇴원일 IS NOT NULL;"]
N_BAD, N_GOOD = rows(" ".join(BAD_FAN))[0][0], rows(" ".join(GOOD_FAN))[0][0]
assert N_BAD > 5 * N_GOOD, (N_BAD, N_GOOD)
ZERO_ID = rows("SELECT MIN(환자ID) FROM 환자")[0][0]
LOST = str(int(ZERO_ID))
assert ZERO_ID.startswith("00") and rows(f"SELECT COUNT(*) FROM 환자 WHERE 환자ID = '{LOST}'")[0][0] == 0
assert rows(f"SELECT COUNT(*) FROM 환자 WHERE 환자ID = '{ZERO_ID}'")[0][0] == 1
assert (R_CNT[0], R_3WAY[0], N_STAY, OCC_ALL) == ((10030, 7970), (9840, 9825, 10030), 205, 85.0), (R_CNT, R_3WAY, N_STAY, OCC_ALL)


def money(v):
    return f"{int(v):,}"


SQL_SLIDES = {
    "one": dict(title="입원 표의 한 행 — 환자 한 명의 입원 기록", question=f"환자 '{PID}' 의 입원 기록을 보면?",
                sql_lines=Q_ONE, hl_lines={2}, label="결과", header=["입원ID", "병동", "입원일", "퇴원일"],
                rows=[[str(a), b, str(c), fmt(d)] for a, b, c, d in R_ONE], hl_rows={len(R_ONE) - 1},
                widths=[1150000, 1100000, 1250000, 1224400],
                notes=[("한 행 = 입원 1건", f"같은 환자가 {len(R_ONE)}번 입원해 {len(R_ONE)}행 (환자 1명 : 입원 여러 건)"),
                       ("퇴원일 NULL", "12월 31일에도 아직 재원 중 — 퇴원형태도 비어 있음")]),
    "cnt": dict(title="입원 건수와 환자 수", question="2024년 자료에 입원은 몇 건, 환자는 몇 명?",
                sql_lines=Q_CNT, hl_lines={1}, label="결과", header=["입원건수", "환자수"],
                rows=[[fmt(R_CNT[0][0]), fmt(R_CNT[0][1])]], hl_rows=set(), widths=[2362200, 2362200],
                notes=[("세는 단위", "같은 환자의 재입원이 여러 행 → 입원 건수 ≠ 환자 수 (8강 COUNT(DISTINCT))"),
                       ("요청서", "‘환자 수’인지 ‘입원 건수’인지 먼저 정합니다 (11강)")]),
    "3way": dict(title="‘2024년 환자’는 세 가지로 읽힙니다", question="‘2024년 입원 환자’를 입원일 · 퇴원일 · 재원 기준으로 세면?",
                 sql_lines=Q_3WAY, hl_lines=set(), label="결과", header=["입원기준", "퇴원기준", "재원기준"],
                 rows=[[fmt(v) for v in R_3WAY[0]]], hl_rows=set(), widths=[1574800, 1574800, 1574800],
                 notes=[("입원기준", f"2024년에 입원한 건 — 2023년에 입원한 {N_CARRY}건이 빠짐"),
                        ("퇴원기준", f"2024년에 퇴원한 건 — 연말에 재원 중인 {N_STAY}건이 빠짐"),
                        ("요청서", "기준을 적지 않으면 같은 질문에 서로 다른 숫자가 나옵니다")]),
    "stay": dict(title="재원 중 환자 — 퇴원일이 비어 있음", question="12월 31일에 아직 재원 중인 환자는 병동별로 몇 명?",
                 sql_lines=Q_STAY, hl_lines={2}, label="결과", header=["병동", "재원중"],
                 rows=[[a, fmt(b)] for a, b in R_STAY], hl_rows=set(), widths=[2362200, 2362200],
                 notes=[("IS NULL", "WHERE 퇴원일 = NULL 로 쓰면 0건 (7강 자주 하는 실수 1)"),
                        ("확인", f"합계 {N_STAY}명. 재원일수 · 퇴원형태도 아직 비어 있음")]),
    "los1": dict(title="재원일수 — 퇴원일 − 입원일", question=f"환자 '{PID}' 의 입원마다 재원일수는?",
                 sql_lines=Q_LOS1, hl_lines={1}, label="결과", header=["입원ID", "입원일", "퇴원일", "재원일수"],
                 rows=[[str(a), str(b), fmt(c), fmt(dd)] for a, b, c, dd in R_LOS1], hl_rows=set(),
                 widths=[1150000, 1250000, 1250000, 1074400],
                 notes=[("날짜 빼기", f"날짜끼리 빼면 일 수. 당일 입퇴원은 0일 ({N_SAME}건) — 병원에 따라 1일로 세기도 하므로 기준을 적어 둠"),
                        ("NULL", "퇴원일이 없으면 재원일수도 NULL — 평균에서 저절로 빠짐")]),
    "alos": dict(title="병동별 평균 재원일수", question="2024년에 퇴원한 입원의 병동별 평균 재원일수는?",
                 sql_lines=Q_ALOS, hl_lines={1}, label="결과", header=["병동", "퇴원건수", "평균재원일수"],
                 rows=[[a, fmt(b), str(c)] for a, b, c in R_ALOS], hl_rows=set(), widths=[1574800, 1574800, 1574800],
                 notes=[("확인", f"전체 {ALL_AVG}일. 병동마다 다름 (가장 짧은 {min(R_ALOS, key=lambda r: r[2])[0]} {min(r[2] for r in R_ALOS)}일 ~ 가장 긴 {max(R_ALOS, key=lambda r: r[2])[0]} {max(r[2] for r in R_ALOS)}일)"),
                        ("기준", f"퇴원 기준 — 재원 중 {N_STAY}건은 빠짐")]),
    "long": dict(title="평균 옆에 최댓값도 — 긴 재원 확인", question="재원일수가 가장 긴 입원 5건은?",
                 sql_lines=Q_LONG, hl_lines={3}, label="결과", header=["입원ID", "병동", "재원일수"],
                 rows=[[str(a), b, fmt(c)] for a, b, c in R_LONG], hl_rows=set(), widths=[1574800, 1574800, 1574800],
                 notes=[("확인", f"평균 {ALL_AVG}일 · 중앙값 {int(ALL_MED)}일인데 가장 긴 입원은 {ALL_MAX}일. 긴 재원이 평균을 끌어올림"),
                        ("이상하면", "입력 오류인지 실제로 긴 입원인지 원무 담당과 확인 (8강 중앙값)")]),
    "daily": dict(title="병동일보 — 매일 자정의 재원 환자 수", question="51병동의 1월 1~3일 병동일보는?",
                  sql_lines=Q_DAILY, hl_lines=set(), label="결과", header=["날짜", "재원환자수", "입원", "퇴원"],
                  rows=[[str(a), fmt(b), fmt(c), fmt(dd)] for a, b, c, dd in R_DAILY], hl_rows=set(),
                  widths=[1350000, 1374400, 1000000, 1000000],
                  notes=[("한 행 = 병동 × 날짜", "재원환자수 = 그날 자정에 병동에 있던 환자 수"),
                         ("검산", "재원환자수를 1년치 더하면 = 재원일수 합 (재원 1일 = 자정 1번)")]),
    "occ": dict(title="병상 가동률", question="병동별 병상 가동률(%)은?",
                sql_lines=Q_OCC, hl_lines={2, 3}, label="결과", header=["병동", "병상수", "재원일수", "가동률"],
                rows=[[a, fmt(b), fmt(c), str(dd)] for a, b, c, dd in R_OCC], hl_rows=set(),
                widths=[1250000, 1050000, 1324400, 1100000],
                notes=[("가동률", "재원일수 ÷ (병상 수 × 날짜 수) × 100. 2024년은 366일"),
                       ("확인", f"전체 {OCC_ALL}%. 가장 높은 곳은 {max(R_OCC, key=lambda r: r[3])[0]} {max(r[3] for r in R_OCC)}%")]),
    "cost1": dict(title="진료비 — 입원 1건에 여러 항목", question=f"62병동 입원 1건(입원ID {AID})의 진료비는?",
                  sql_lines=Q_COST1, hl_lines=set(), label="결과", header=["항목", "금액", "급여구분"],
                  rows=[[a, money(b), c] for a, b, c in R_COST1], hl_rows={i for i, r in enumerate(R_COST1) if r[2] == "비급여"},
                  widths=[1724400, 1600000, 1400000],
                  notes=[("한 행 = 입원 × 항목", f"입원 1건에 진료비 {len(R_COST1)}행 (1 : N)"),
                         ("급여구분", "급여 = 건강보험 청구 대상, 비급여 = 환자가 모두 부담")]),
    "dept": dict(title="진료과별 입원 1건당 진료비", question="진료과별로 입원 1건에 평균 얼마?",
                 sql_lines=Q_DEPT, hl_lines={1, 2, 3}, label="결과 (만 원)", header=["진료과", "입원건수", "건당진료비"],
                 rows=[[a, fmt(b), fmt(int(c))] for a, b, c in R_DEPT], hl_rows=set(), widths=[1724400, 1400000, 1600000],
                 notes=[("나누는 수", "금액은 SUM, 건수는 COUNT(DISTINCT 입원ID) — 진료비 행 수로 나누면 안 됨"),
                        ("확인", f"수술이 많은 {R_DEPT[0][0]} {int(R_DEPT[0][2])}만 원 · {R_DEPT[1][0]} {int(R_DEPT[1][2])}만 원")]),
    "pay": dict(title="급여와 비급여", question="전체 진료비 중 비급여는 몇 %?",
                sql_lines=Q_PAY, hl_lines={1, 2}, label="결과 (원)", header=["급여구분", "금액", "비율"],
                rows=[[a, money(b), str(c)] for a, b, c in R_PAY], hl_rows=set(), widths=[1400000, 2224400, 1100000],
                notes=[("비급여", f"{TOP_NONPAY}가 가장 큼 (상급병실료 · 재료대 · 비급여 검사료)"),
                       ("청구", "급여 부분만 건강보험에 청구 — 청구 자료에는 비급여가 없음")]),
}

SUMMARY = {   # 여기까지 정리: 세 줄 (①②③ 런 3개) + 생각해 볼 질문 · 답
    2: ([("① ", "입원 표의 한 행", " = 입원 1건. 환자 수는 COUNT(DISTINCT 환자ID)"),
         ("② ", "‘2024년’", " 은 입원 · 퇴원 · 재원 기준마다 숫자가 다르다"),
         ("③ ", "재원 중", " 인 입원은 퇴원일이 NULL (IS NULL 로 찾음)")],
        ("잠깐 생각해 봅시다", "  “우리 병동 작년 환자 수”를 요청받으면 무엇을 되물을까요?",
         "환자 수인지 입원 건수인지, 어느 날짜 기준인지 — 11강 요청서의 ‘세는 단위 · 기준일’입니다.")),
    3: ([("① ", "재원일수", " = 퇴원일 − 입원일 (당일 입퇴원은 0일)"),
         ("② ", "평균 재원일수", " 는 퇴원한 입원으로 구한다"),
         ("③ ", "평균과 함께", " 중앙값 · 최댓값을 본다")],
        ("잠깐 생각해 봅시다", f"  재원 중인 {N_STAY}건은 왜 평균에서 빠지나요?",
         "아직 퇴원하지 않아 재원일수가 정해지지 않았기 때문입니다. 넣으려면 기준일까지의 재원일수로 따로 셉니다.")),
    5: ([("① ", "진료비", " 는 입원 1건에 여러 행 — 합계는 SUM, 건수는 COUNT(DISTINCT)"),
         ("② ", "JOIN 전에", " 한 행의 단위를 확인 (1 : N 이면 합계가 부풀어남)"),
         ("③ ", "청구 자료 ≠ 진료 기록", ", 환자번호는 글자로 다룬다")],
        ("잠깐 생각해 봅시다", "  비급여 비율을 청구 자료로 구할 수 있을까요?",
         "없습니다. 청구 자료에는 건강보험에 청구한 급여 항목만 있기 때문입니다.")),
}

TERMS = [("재원일수", "Length of Stay", "퇴원일 − 입원일 (당일 입퇴원은 0일)"),
         ("평균 재원일수", "ALOS", "퇴원한 입원의 재원일수 평균"),
         ("병상 가동률", "Bed Occupancy", "재원일수 ÷ (병상 수 × 날짜 수) × 100"),
         ("병동일보", "—", "병동 × 날짜별 재원 · 입원 · 퇴원 환자 수"),
         ("재원 중", "—", "기준일에 아직 퇴원하지 않음 (퇴원일 NULL)"),
         ("급여 · 비급여", "—", "건강보험 청구 대상인지 아닌지"),
         ("청구 자료", "EDI", "진료비를 청구한 기록. 진료 기록과 목적이 다름"),
         ("행 부풀림", "Fan-out", "1 : N 을 JOIN 해 합계가 커지는 것")]


def agenda(t, prefix, items, gap):
    """구분 · 학습 목표 슬라이드의 오늘의 순서 6칸 (런 2개: 제목 · 설명)"""
    names = sorted([s.find(f"{P}nvSpPr/{P}cNvPr").get("name") for s in t.iter(P + "sp")
                    if re.match(rf"{prefix} \d+$", s.find(f"{P}nvSpPr/{P}cNvPr").get("name"))], key=lambda n: int(n.split()[1]))
    assert len(names) == 6, names
    for nm, (a, b) in zip(names, items):
        fill(shape(t, nm), [(0, [a, gap + b])])


def pair(t, title, situation, bad, bad_res, bad_note, good, good_res, good_note, bottom, sz=1600):
    """'이렇게 하면 · 이렇게 고칩니다' 두 칸 슬라이드 (12강 오류 슬라이드 모양)"""
    set_title(t, title)
    fill(shape(t, "TextBox 4"), [(0, ["상황", "  " + situation])])
    for box, tb, res, lines, r, note in (("Bad 6", "TextBox 7", "TextBox 8", bad, bad_res, bad_note),
                                        ("Good 10", "TextBox 11", "TextBox 12", good, good_res, good_note)):
        sql_paras(shape(t, tb), lines, sz)
        hgt = 300000 * len(lines) + 100000
        shape(t, tb).find(f".//{A}ext").set("cy", str(hgt))
        shape(t, box).find(f".//{A}ext").set("cy", str(hgt + 150000))
        y = int(shape(t, box).find(f".//{A}off").get("y")) + hgt + 150000 + 120000
        move_y(t, res, y)
        fill(shape(t, res), [(0, ["결과", " " + r]), (1, [note])])
    fill(shape(t, "TextBox 13"), [(0, [bottom])])


def summary_slide(t, lines, box):
    set_title(t, "여기까지 정리")
    fill(shape(t, "TextBox 5"), [(0, list(x)) for x in lines])
    fill(shape(t, "TextBox 7"), [(0, [box[0], box[1]]), (1, [box[2]])])


def main(src, out):
    d = Deck(src)
    w10_slides.KW = KW_SQL                        # JOIN · ON · AND · CASE … 도 파란 글자
    s12 = d.find("12강. CDW 분석에서 자주 생기는 오류")
    e12 = d.find("12주차 강의 정리")
    L = d.between(s12, e12)
    F = lambda line, also=None: d.find(line, also, within=L)
    tmpl_sql = d.find("2단계 — 값 살펴보기")
    tmpl_tab = d.find("CDW에서 자주 보는 표")
    tmpl_sum = d.find("여기까지 정리", "① CDW = 분석용으로 따로 모아 둔 읽기 전용 복사본")

    def new_sql(anchor, key):
        t = build(d.tree(tmpl_sql), **SQL_SLIDES[key])
        return d.insert_after(anchor, t, d.rels(tmpl_sql))

    def new_sum(anchor, sec):
        t, rel = d.clone(tmpl_sum); summary_slide(t, *SUMMARY[sec])
        return d.insert_after(anchor, t, rel)

    # ---- 표지 · 리뷰 · 학습 목표
    t = d.tree(s12)
    for s in t.iter(P + "sp"):
        tx = texts(s)
        if tx and tx[0] == "12강. CDW 분석에서 자주 생기는 오류":
            set_para(s, TITLE12)
        elif tx[:3] == ["세는 단위와 JOIN", "타입 · 형식 · 빈 값 · 코드", "기준일과 점검 체크리스트"]:
            fill(s, [(0, ["원무 업무와 데이터"]), (1, ["재원일수와 병상 가동률"]), (2, ["진료비와 청구"])])
    t = d.tree(F("지난시간 리뷰"))
    fill(shape(t, "TextBox 4"), [(0, ["CDW", " = 분석용 읽기 전용 복사본, 보통 하루 정도 시차"]),
                                 (1, ["분석 전에 ", "데이터 사전", "과 ", "요청서", "로 단위 · 대상 · 기준일을 정한다"]),
                                 (2, ["승인 범위 안에서", " 최소한의 항목만 조회한다"]),
                                 (3, ["오늘부터는 ", "가상 병원 CDW 로 직접 숫자를 만듭니다."]),
                                 (4, ["첫 주제는 원무 — 입원 · 퇴원 · 병상 · 진료비입니다."])])
    t = d.tree(F("12주차 학습 목표"))
    set_para(shape(t, "TextBox 4"), "입원 · 퇴원 · 병상 · 진료비 숫자 만들기")
    fill(shape(t, "TextBox 6"), [(0, ["① 원무 업무와 남는 자료를 말할 수 있다"]),
                                 (1, ["② 입원 건수와 환자 수를 나눠 센다"]),
                                 (2, ["③ 재원일수 · 병상 가동률을 구한다"]),
                                 (3, ["④ 진료비를 집계하고 JOIN 함정을 피한다"])])
    agenda(t, "Step", AG, "  ")

    # ---- 구분 슬라이드 6장 (이름 · 부제 · 오늘의 순서)
    divs = [F("1. 세는 단위와 JOIN"), F("2. 값의 타입과 형식"), F("3. 빈 값과 코드"), F("4. 시간"), F("5. 점검 체크리스트"), F("6. 정리")]
    for k, s in enumerate(divs):
        t = d.tree(s)
        set_title(t, f"{k + 1}. {AG[k][0]}")
        set_para(shape(t, "TextBox 4"), AG[k][1])
        agenda(t, "Sec", AG, "   ")

    # ---- 옮길 슬라이드 · 지울 슬라이드 (지우기 전에 찾아 둠)
    e2, e7, e11 = F("오류 2 — JOIN 뒤 행이 늘어남"), F("오류 7 — 엑셀에서 앞자리 0이 사라짐"), F("오류 11 — 청구 자료를 진료 기록으로 읽음")
    to13 = [F("기준일(Index Date) 정하기"), F("오류 12 — 기준일 이후 정보가 섞임")]
    to14q = [F("오류 점검 체크리스트"), F("오류를 찾는 SQL 네 가지"), F("빠진 값 자체가 정보입니다")]
    to14c = F("코드가 바뀌면 추세가 끊깁니다")
    drop = [F(x) for x in ("오류 1 — 세는 단위를 잘못 잡음", "오류 3 — INNER JOIN으로 분모가 줄어듦", "오류 4 — 문자로 저장된 숫자",
                           "오류 5 — 문자로 저장된 날짜", "오류 6 — 정수 나눗셈으로 0이 나옴", "오류 8 — NULL을 0으로 바꿈",
                           "오류 9 — 대소문자와 공백", "오류 10 — 같은 질환, 다른 표기")]

    # ---- 1절: 원무 업무 표 · 한 환자의 입원 기록
    t, rel = d.clone(tmpl_tab)
    set_title(t, "원무 업무와 남는 자료")
    set_para(shape(t, "TextBox 4"), "언제 들어와 언제 나갔고, 얼마였나")
    bottom = table_fill(t, ["원무 업무", "무슨 일을 하나", "남는 자료 (가상 병원 CDW)"],
                        [["접수 · 입원 결정", "환자 등록, 보험 확인", "환자 · 입원.보험유형"],
                         ["입원 수속 · 병상 배정", "병동 · 진료과 정하기", "입원.병동 · 입원.진료과 · 병동"],
                         ["재원 관리", "매일 자정 재원 환자 수 집계", "병동일보"],
                         ["퇴원 수속 · 수납", "퇴원일 · 퇴원형태, 진료비 계산", "입원.퇴원일 · 진료비"],
                         ["보험 청구 · 심사", "급여 항목을 건강보험에 청구", "진료비.급여구분"]],
                        widths=[2700000, 4300000, 4800000], row_h=560000, sz=1800)
    set_para(shape(t, "TextBox 6"), "오늘은 이 자료로 입원 · 재원 · 병상 · 진료비 숫자를 직접 만듭니다.")
    move_y(t, "TextBox 6", bottom + 250000)
    a = d.insert_after(divs[0], t, rel)
    new_sql(a, "one")
    # ---- 2절
    a = new_sql(divs[1], "cnt"); a = new_sql(a, "3way"); a = new_sql(a, "stay"); new_sum(a, 2)
    # ---- 3절
    a = new_sql(divs[2], "los1"); a = new_sql(a, "alos"); a = new_sql(a, "long"); new_sum(a, 3)
    # ---- 4절
    a = new_sql(divs[3], "daily"); new_sql(a, "occ")
    # ---- 5절: 진료비 3장 → JOIN 함정 · 청구 자료 · 앞자리 0 (있던 슬라이드를 옮겨 고침) → 정리
    a = new_sql(divs[4], "cost1"); a = new_sql(a, "dept"); a = new_sql(a, "pay")
    for s in (e2, e11, e7):
        d.lst.remove(s); a.addnext(s); a = s
    new_sum(a, 5)
    pair(d.tree(e2), "JOIN 함정 — 재원일수가 6배로", "진료비를 붙인 표로 재원일수를 더했더니 6배가 되었습니다.",
         BAD_FAN, fmt(N_BAD), "입원 1건에 진료비가 여러 행이라 재원일수가 여러 번 더해졌습니다.",
         GOOD_FAN, fmt(N_GOOD), "재원일수는 입원 표에서만 더합니다.",
         "JOIN 전에 ‘한 행의 단위’를 확인하세요. 입원 1건 : 진료비 여러 행(1 : N)이면 합계가 부풀어납니다.")
    set_title(d.tree(e11), "청구 자료를 진료 기록으로 읽으면")
    t = d.tree(e7)
    set_title(t, "환자번호 앞자리 0 — 엑셀로 옮길 때")
    fill(shape(t, "TextBox 4"), [(0, ["상황", f"  환자번호 '{ZERO_ID}' 를 엑셀로 열었다가 다시 저장했습니다."])])
    sz7 = int(next(shape(t, "TextBox 7").iter(A + "rPr")).get("sz"))
    sql_paras(shape(t, "TextBox 7"), ["-- 엑셀이 숫자로 인식", f"{ZERO_ID}  →  {LOST}", " ", "SELECT * FROM 환자", f"WHERE 환자ID = '{LOST}';"], sz7)
    fill(shape(t, "TextBox 8"), [(0, ["결과", " 0행"]), (1, ["엑셀에서 앞의 0 이 사라진 번호로 찾았습니다."])])
    sql_paras(shape(t, "TextBox 11"), ["-- CSV를 열 때 해당 열을", "-- ‘텍스트’로 지정하거나", "-- 데이터베이스에서 직접 조회", " ",
                                       "SELECT * FROM 환자", f"WHERE 환자ID = '{ZERO_ID}';"], sz7)
    fill(shape(t, "TextBox 12"), [(0, ["결과", " 1행"]), (1, ["환자번호는 글자(텍스트)로 다룹니다."])])
    set_para(shape(t, "Concept tag"), "가상 병원 CDW 에서 실행")

    # ---- 6절: 용어 · 과제 2 안내 · 강의 정리
    t = d.tree(F("12주차 용어 정리"))
    table_fill(t, ["용어", "영어", "뜻 (한 줄)"], [list(x) for x in TERMS])
    t = d.tree(F("과제 2 안내"))
    set_para(shape(t, "TextBox 4"), "20점 · 10문항 × 2점 · 2026-12-08(화)까지")
    fill(shape(t, "TextBox 7"), [(0, ["가상 병원 CDW 로 낙상 발생률 구하기"]),
                                 (1, ["낙상 건수 · 재원일수 · 낙상률 (S1~S3)"]),
                                 (2, ["근무조별 낙상 · 낙상 입원의 재원일수 (S4 · S5)"]),
                                 (3, ["틀린 동료 SQL 고치기 (E1~E3)"]),
                                 (4, ["검산표 INSERT · UPDATE (T1 · T2)"])])
    fill(shape(t, "TextBox 10"), [(0, ["S1~S5 단계별 SQL  각 2점 (10점)"]), (1, ["E1~E3 동료 SQL 점검  각 2점 (6점)"]),
                                  (2, ["T1 · T2 검산표  각 2점 (4점)"]), (3, ["모두 SQL 문항 — ✅ 가 나오면 점수"]),
                                  (4, ["제출: 노트북 파일 하나 (과제2.ipynb)"])])
    fill(shape(t, "TextBox 11"), [(0, ["일정"]),
                                  (1, ["오늘(12주차) 과제 2 공개 — 오늘 배운 재원일수 · JOIN 으로 바로 시작할 수 있습니다"]),
                                  (2, ["범위는 12주차까지 — 13주차 수업 시간에도 질문을 받습니다"]),
                                  (3, ["2026-12-08(화)까지 LMS 에 제출"]),
                                  (4, ["값이 필요한 문항은 바로 위 조회 셀에서 값을 확인할 수 있습니다."])])
    t = d.tree(e12)
    fill(shape(t, "TextBox 4"), [(0, ["입원 건수", "와 ", "환자 수", "는 다르다. 세는 단위와 날짜 기준을 먼저 정한다"]),
                                 (1, ["재원일수 · 병상 가동률", "은 퇴원일과 병동일보로 구한다"]),
                                 (2, ["JOIN 전에 한 행의 단위", "를 확인한다. 1 : N 이면 합계가 부풀어난다"])])
    runs = list(shape(t, "Next 5").iter(A + "r"))
    assert runs[0].findtext(A + "t") == "다음 시간", [r.findtext(A + "t") for r in runs]
    runs[1].find(A + "t").text = NEXT13

    # ---- 13 · 14강으로 옮기기, 지우기
    anchor = d.find("코호트 정의에 꼭 적는 세 가지")
    for s in to13:
        d.lst.remove(s); anchor.addnext(s); anchor = s
    anchor = d.find("데이터 품질 점검")
    for s in to14q:
        d.lst.remove(s); anchor.addnext(s); anchor = s
    s = to14c; d.lst.remove(s); d.find("분류와 용어 — KCD와 SNOMED CT").addnext(s)
    t = d.tree(d.find("표준 코드가 없으면"))
    set_para(shape(t, "TextBox 4"), "같은 질환을 병원마다 다르게 적으면")
    for s in drop:
        d.delete(s)
    d.save(out)
    print(f"12강: 새로 {len(SQL_SLIDES) + 4}장 · 옮김 {len(to13) + len(to14q) + 1}장 · 지움 {len(drop)}장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
