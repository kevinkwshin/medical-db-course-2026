# -*- coding: utf-8 -*-
"""build_hospital_mini.py — 11강부터 쓰는 가상 병원 CDW (data/hospital_mini.duckdb) 를 만듭니다 (2026-11-03 강사 결정).

실제 병원 자료가 아닙니다. 고정한 난수(SEED)로 만든 가상 자료라 몇 번을 다시 만들어도 같은 숫자가 나옵니다.
  - 병동 6곳, 2024년 1년 (2023년에 입원해 2024년에도 재원한 입원 포함)
  - 하루씩 병상 수 안에서 입원 · 퇴원을 흉내 냄 → 병동일보(자정 재원 환자 수)는 입원 표와 정확히 맞음
  - 재입원: 자택 퇴원 뒤 30일 안 비계획 재입원 · 항암 등 계획 재입원 · 30일 뒤 재입원
  - 낙상: 재원일 · 병동 · 나이에 따라 발생, 밤 근무에 많게

표 (한 행의 단위)
  환자      환자 1명       환자ID(글자 7자리, 앞자리 0) · 성별(M/F) · 생년월일 · 사망일
  입원      입원 1건       입원ID · 환자ID · 병동 · 진료과 · 입원일 · 퇴원일(재원 중이면 NULL) · 입원경로 · 퇴원형태 · 계획입원 · 보험유형
  진단      진단 1건       진단ID · 입원ID · 진단코드(KCD) · 주진단여부
  병동      병동 1곳       병동 · 구분 · 주진료과 · 병상수
  병동일보  병동 × 날짜     병동 · 날짜 · 재원환자수(자정 기준) · 입원환자수 · 퇴원환자수
  근무      병동 × 날짜 × 근무조   병동 · 근무일 · 근무조(D/E/N) · 간호사수
  진료비    입원 × 항목     진료비ID · 입원ID · 항목 · 금액(원) · 급여구분
  낙상      낙상 1건       낙상ID · 입원ID · 발생일 · 근무조 · 손상정도
  검사      검사 1건       검사ID · 환자ID · 검사일 · 검사명 · 결과값 (3% NULL, 일부는 퇴원 뒤 외래 검사)

일부러 넣은 실제 병원 자료의 모습 (12 · 13강 · 과제 2 에서 씀)
  - 환자ID 는 '0012345' 처럼 앞자리 0 이 있는 글자 (엑셀에서 숫자로 바뀌면 0 이 사라짐)
  - 2024-12-31 에 아직 재원 중인 입원은 퇴원일 · 퇴원형태가 NULL
  - 당일 입퇴원(퇴원일 = 입원일, 재원일수 0)이 있음
  - 2023년에 입원해 2024년까지 재원한 입원이 있음 (입원일 < 2024-01-01)

실행: cd /Users/kevin/Code/DBMS && python3 tools/build_hospital_mini.py
결과: data/hospital_mini.duckdb · data/hospital_mini.duckdb.gz · data/hospital_mini_dictionary.md
"""
import os, gzip, shutil, datetime as dt
import numpy as np
import pandas as pd
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "hospital_mini.duckdb")
DICT = os.path.join(ROOT, "data", "hospital_mini_dictionary.md")
SEED = 20241231
rng = np.random.default_rng(SEED)

SIM_START, Y0, Y1 = dt.date(2023, 10, 1), dt.date(2024, 1, 1), dt.date(2024, 12, 31)
DAYS = (Y1 - SIM_START).days + 1

# 병동: 병상수 · 주진료과 · 평균 재원일수(중앙값) · 응급 입원 비율 · 나이 평균 · 여성 비율 · 사망 · 전원 · 낙상 배수 · 간호사(D/E/N)
WARDS = {
    "51병동": dict(구분="내과계", 진료과=["호흡기내과"], beds=42, los=7.0, er=.55, age=70, female=.42, death=.05, transfer=.06, fall=1.1, rn=(7, 6, 4)),
    "52병동": dict(구분="내과계", 진료과=["순환기내과", "내분비내과"], beds=40, los=6.0, er=.45, age=68, female=.46, death=.03, transfer=.05, fall=1.0, rn=(7, 6, 4)),
    "61병동": dict(구분="외과계", 진료과=["외과"], beds=38, los=5.0, er=.35, age=60, female=.48, death=.01, transfer=.03, fall=.7, rn=(7, 6, 4)),
    "62병동": dict(구분="외과계", 진료과=["정형외과"], beds=40, los=9.0, er=.30, age=67, female=.60, death=.005, transfer=.15, fall=1.4, rn=(7, 6, 4)),
    "71병동": dict(구분="내과계", 진료과=["신경과"], beds=36, los=10.0, er=.50, age=72, female=.50, death=.03, transfer=.12, fall=1.8, rn=(6, 5, 4)),
    "72병동": dict(구분="내과계", 진료과=["종양내과"], beds=30, los=4.0, er=.10, age=62, female=.45, death=.06, transfer=.02, fall=.8, rn=(5, 4, 3)),
}
OCC = 0.80                                   # 새 환자 입원 수를 정하는 값 (재입원까지 더해 병상 가동률 약 85%)
# 주진단 (KCD, 병동별) · 함께 붙는 부진단
MAIN_DX = {
    "51병동": [("J18.9", .35), ("J44.1", .20), ("A41.9", .15), ("J96.0", .10), ("C34.9", .10), ("J15.9", .10)],
    "52병동": [("I50.9", .30), ("I21.9", .15), ("I48.9", .15), ("E11.6", .20), ("N39.0", .10), ("I10", .10)],
    "61병동": [("K80.2", .25), ("K35.8", .20), ("C16.9", .15), ("C18.9", .15), ("K56.6", .15), ("K40.9", .10)],
    "62병동": [("S72.0", .25), ("M17.1", .25), ("M48.0", .20), ("S82.8", .15), ("M16.1", .15)],
    "71병동": [("I63.9", .45), ("I61.9", .15), ("G40.9", .15), ("G20", .10), ("F03", .15)],
    "72병동": [("C34.9", .25), ("C16.9", .20), ("C50.9", .20), ("C22.0", .15), ("C18.9", .20)],
}
SUB_DX = [("I10", .40), ("E11.9", .25), ("E78.5", .20), ("N18.3", .10), ("F03", .08), ("I48.9", .07)]
SURGICAL = {"61병동": (1_500_000, 6_000_000), "62병동": (2_500_000, 9_000_000)}


def pick(pairs):
    codes, p = zip(*pairs)
    p = np.array(p) / sum(p)
    return codes[rng.choice(len(codes), p=p)]


# ---------------------------------------------------------------- 환자 · 입원 (하루씩 흉내)
patients = {}            # 환자ID → dict(성별, 생년월일)
next_pid = [10001]        # 7자리 글자로 저장 → '0010001' 처럼 앞자리 0


def new_patient(w, day):
    pid = f"{next_pid[0] + int(rng.integers(0, 37)):07d}"
    while pid in patients:
        pid = f"{int(pid) + 1:07d}"
    next_pid[0] = int(pid) + 1
    age = int(np.clip(rng.normal(WARDS[w]["age"], 14), 19, 99))
    born = day - dt.timedelta(days=age * 365 + int(rng.integers(0, 365)))
    patients[pid] = dict(성별="F" if rng.random() < WARDS[w]["female"] else "M", 생년월일=born)
    return pid


def age_at(pid, day):
    b = patients[pid]["생년월일"]
    return day.year - b.year - ((day.month, day.day) < (b.month, b.day))


adm, scheduled = [], {}   # scheduled[day] = [(pid, ward, planned)]
current = {w: [] for w in WARDS}   # 재원 중인 입원 index


def los_for(w, er):
    m = WARDS[w]["los"] * (1.15 if er else 1.0)
    los = int(round(rng.lognormal(np.log(m), 0.55)))
    if rng.random() < 0.02:
        los = 0                                   # 당일 입퇴원 (경과 관찰 등)
    return int(min(los, 90))


def admit(pid, w, day, planned):
    er = (not planned) and rng.random() < WARDS[w]["er"]
    los = los_for(w, er)
    if w == "72병동" and planned:
        los = int(rng.integers(2, 5))             # 계획 항암 입원은 짧게
    dx = pick(MAIN_DX[w])
    insurance = ("자동차보험" if dx.startswith("S") and rng.random() < .25 else
                 "산재보험" if dx.startswith("S") and rng.random() < .05 else
                 "의료급여" if rng.random() < .08 else "건강보험")
    a = dict(환자ID=pid, 병동=w, 진료과=WARDS[w]["진료과"][int(rng.integers(0, len(WARDS[w]["진료과"])))],
             입원일=day, 퇴원예정=day + dt.timedelta(days=los), 입원경로="응급" if er else "외래",
             계획입원="Y" if planned else "N", 보험유형=insurance, 주진단=dx)
    adm.append(a)
    current[w].append(len(adm) - 1)


def schedule(day, item):
    scheduled.setdefault(day, []).append(item)


for k in range(DAYS):
    day = SIM_START + dt.timedelta(days=k)
    # ① 퇴원 (당일 입퇴원은 아래 입원 뒤에 처리)
    for w in WARDS:
        stay = []
        for i in current[w]:
            a = adm[i]
            if a["퇴원예정"] <= day and a["입원일"] < day:
                a["퇴원일"] = a["퇴원예정"]
                ag = age_at(a["환자ID"], day)
                pd_ = WARDS[w]["death"] * (1.6 if ag >= 80 else 1.0)
                r = rng.random()
                a["퇴원형태"] = "사망" if r < pd_ else "전원" if r < pd_ + WARDS[w]["transfer"] else "자택"
                if a["퇴원형태"] == "자택":       # 재입원 예약
                    hi = a["주진단"] in ("I50.9", "J44.1", "A41.9", "J18.9") or ag >= 80
                    r2 = rng.random()
                    if r2 < (0.11 if hi else 0.05):
                        schedule(day + dt.timedelta(days=int(rng.integers(1, 31))), (a["환자ID"], w, False))
                    elif r2 < (0.11 if hi else 0.05) + 0.07:
                        schedule(day + dt.timedelta(days=int(rng.integers(31, 120))), (a["환자ID"], w, False))
                    if a["주진단"].startswith("C") and rng.random() < (0.45 if w == "72병동" else 0.08):
                        schedule(day + dt.timedelta(days=int(rng.integers(14, 29))), (a["환자ID"], "72병동" if w == "72병동" else w, True))
            else:
                stay.append(i)
        current[w] = stay
    # ② 예약된 재입원 → 같은 병동, 자리가 없으면 자리 있는 병동
    for pid, w, planned in scheduled.pop(day, []):
        if any(adm[i]["환자ID"] == pid for ww in WARDS for i in current[ww]):
            continue                                # 이미 재원 중
        target = w if len(current[w]) < WARDS[w]["beds"] else next((x for x in WARDS if len(current[x]) < WARDS[x]["beds"]), None)
        if target:
            admit(pid, target, day, planned)
    # ③ 새 환자 입원 (평일이 많고 주말은 적게)
    for w, c in WARDS.items():
        lam = OCC * c["beds"] / (c["los"] * 1.23) * (0.6 if day.weekday() >= 5 else 1.16)   # 1.23 = 평균 재원일수 / 중앙값
        n = min(int(rng.poisson(lam)), max(0, c["beds"] - len(current[w])))
        for _ in range(n):
            admit(new_patient(w, day), w, day, False)
    # ④ 당일 입퇴원
    for w in WARDS:
        stay = []
        for i in current[w]:
            a = adm[i]
            if a["퇴원예정"] == day == a["입원일"]:
                a["퇴원일"], a["퇴원형태"] = day, "자택"
            else:
                stay.append(i)
        current[w] = stay

A = pd.DataFrame(adm)
A["퇴원일"] = A.get("퇴원일")
A.loc[A["퇴원일"].notna() & (pd.to_datetime(A["퇴원일"]) > pd.Timestamp(Y1)), ["퇴원일", "퇴원형태"]] = None
keep = (pd.to_datetime(A["입원일"]) <= pd.Timestamp(Y1)) & (A["퇴원일"].isna() | (pd.to_datetime(A["퇴원일"]) >= pd.Timestamp(Y0)))
A = A[keep].sort_values(["입원일", "병동", "환자ID"]).reset_index(drop=True)
A.insert(0, "입원ID", range(240001, 240001 + len(A)))
pids = sorted(A["환자ID"].unique())

# ---------------------------------------------------------------- 병동일보 (자정 기준 재원 · 그날 입원 · 퇴원) · 근무
days24 = pd.date_range(Y0, Y1).date
adm_d = pd.to_datetime(A["입원일"]).dt.date
dis_d = pd.to_datetime(A["퇴원일"]).dt.date
rows, duty = [], []
for w, c in WARDS.items():
    m = A["병동"] == w
    for d in days24:
        census = int(((adm_d <= d) & (dis_d.isna() | (dis_d > d)) & m).sum())
        rows.append(dict(병동=w, 날짜=d, 재원환자수=census, 입원환자수=int(((adm_d == d) & m).sum()),
                         퇴원환자수=int(((dis_d == d) & m).sum())))
        weekend = d.weekday() >= 5
        for s, base in zip("DEN", c["rn"]):
            n = base - (1 if weekend and s == "D" else 0) + int(rng.choice([-1, 0, 0, 0, 1]))
            duty.append(dict(병동=w, 근무일=d, 근무조=s, 간호사수=max(n, 2)))
CEN = pd.DataFrame(rows); DUTY = pd.DataFrame(duty)
assert (CEN.groupby("병동")["재원환자수"].max() <= pd.Series({w: c["beds"] for w, c in WARDS.items()})).all(), "병상 수 초과"

# ---------------------------------------------------------------- 진단
dx_rows = []
for r in A.itertuples():
    dx_rows.append((r.입원ID, r.주진단, "Y"))
    ag = age_at(r.환자ID, r.입원일)
    for code, p in SUB_DX:
        if code != r.주진단 and rng.random() < p * (1.3 if ag >= 70 else 0.8):
            dx_rows.append((r.입원ID, code, "N"))
DX = pd.DataFrame(dx_rows, columns=["입원ID", "진단코드", "주진단여부"])
DX.insert(0, "진단ID", range(1, len(DX) + 1))

# ---------------------------------------------------------------- 진료비 (입원 × 항목, 원 단위)
cost = []
for r in A.itertuples():
    end = r.퇴원일 if pd.notna(r.퇴원일) else Y1
    days = max((end - r.입원일).days, 1)
    items = [("입원료", days * int(rng.normal(68_000, 4_000)), "급여"),
             ("식대", days * int(rng.normal(15_000, 1_500)), "급여"),
             ("검사료", int(150_000 + days * rng.normal(30_000, 8_000)), "급여"),
             ("약제비", int(days * rng.normal(45_000, 15_000) * (2.5 if r.병동 == "72병동" else 1)), "급여")]
    if rng.random() < 0.55:
        items.append(("영상진단료", int(rng.integers(1, 4)) * int(rng.normal(130_000, 30_000)), "급여"))
    if r.병동 in SURGICAL and r.주진단[0] in "KCSM" and rng.random() < 0.75:
        lo, hi = SURGICAL[r.병동]
        items.append(("처치·수술료", int(rng.uniform(lo, hi)), "급여"))
        items.append(("재료대", int(rng.uniform(200_000, 1_500_000)), "급여" if rng.random() < .7 else "비급여"))
    else:
        items.append(("처치·수술료", int(rng.uniform(20_000, 300_000)), "급여"))
    if rng.random() < 0.22:
        items.append(("상급병실료", days * int(rng.normal(90_000, 15_000)), "비급여"))
    if rng.random() < 0.15:
        items.append(("비급여 검사료", int(rng.uniform(80_000, 600_000)), "비급여"))
    for it, amt, kind in items:
        cost.append((r.입원ID, it, int(round(max(amt, 1000), -2)), kind))
COST = pd.DataFrame(cost, columns=["입원ID", "항목", "금액", "급여구분"])
COST.insert(0, "진료비ID", range(1, len(COST) + 1))

# ---------------------------------------------------------------- 낙상 (재원일마다 · 밤에 많게)
BASE = 1.55 / 1000                            # 재원 1일당
falls = []
for r in A.itertuples():
    end = (r.퇴원일 - dt.timedelta(days=1)) if pd.notna(r.퇴원일) else Y1
    start = max(r.입원일, Y0)
    if end < start:
        continue
    nights = (end - start).days + 1
    ag = age_at(r.환자ID, start)
    mult = WARDS[r.병동]["fall"] * (1.7 if ag >= 75 else 1.2 if ag >= 65 else 0.6)
    n = int(rng.poisson(BASE * mult * nights))
    if n and nights > 2 and rng.random() < 0.15:      # 한 번 넘어진 환자는 다시 넘어지기 쉬움 (재낙상)
        n += 1
    for _ in range(n):
        d = start + dt.timedelta(days=int(rng.integers(0, nights)))
        shift = "DEN"[rng.choice(3, p=[.25, .30, .45])]
        harm = ["없음", "경증", "중등도 이상"][rng.choice(3, p=[.62, .30, .08])]
        falls.append((r.입원ID, d, shift, harm))
FALL = pd.DataFrame(falls, columns=["입원ID", "발생일", "근무조", "손상정도"]).sort_values(["발생일", "입원ID"]).reset_index(drop=True)
FALL.insert(0, "낙상ID", range(1, len(FALL) + 1))

# ---------------------------------------------------------------- 환자 (사망일 = 병원에서 사망한 퇴원일)
died = A[A["퇴원형태"] == "사망"].groupby("환자ID")["퇴원일"].max()
PT = pd.DataFrame([dict(환자ID=p, 성별=patients[p]["성별"], 생년월일=patients[p]["생년월일"], 사망일=died.get(p)) for p in pids])

# ---------------------------------------------------------------- 검사 (환자 단위 · 재원 중 + 일부는 퇴원 뒤 외래 추적) — 따로 둔 난수
rng2 = np.random.default_rng(SEED + 1)        # 앞의 표들이 바뀌지 않게
LAB = {"알부민": (3.6, 0.5, 1), "헤모글로빈": (11.8, 1.8, 1), "크레아티닌": (1.1, 0.6, 2), "당화혈색소": (7.4, 1.2, 1)}
labs = []
dm = set(DX[DX["진단코드"].str.startswith("E11")]["입원ID"])
for r in A.itertuples():
    end = r.퇴원일 if pd.notna(r.퇴원일) else Y1
    span = max((end - r.입원일).days, 0)
    for name, (mu, sd, nd) in LAB.items():
        if name == "당화혈색소" and r.입원ID not in dm:
            continue
        if name != "당화혈색소" and rng2.random() < 0.25:
            continue
        d = r.입원일 + dt.timedelta(days=int(rng2.integers(0, span + 1)))
        if d < Y0:
            continue
        val = round(max(float(rng2.normal(mu, sd)), 0.1), nd)
        labs.append((r.환자ID, d, name, None if rng2.random() < 0.03 else val))      # 3% 는 결과값 없음 (검체 불량 등)
    if pd.notna(r.퇴원일) and rng2.random() < 0.12:                                   # 퇴원 뒤 외래 추적 검사
        d = r.퇴원일 + dt.timedelta(days=int(rng2.integers(7, 60)))
        if d <= Y1:
            labs.append((r.환자ID, d, "알부민", round(float(rng2.normal(3.8, 0.4)), 1)))
LABS = pd.DataFrame(labs, columns=["환자ID", "검사일", "검사명", "결과값"]).sort_values(["검사일", "환자ID", "검사명"]).reset_index(drop=True)
LABS.insert(0, "검사ID", range(1, len(LABS) + 1))

ADM = A[["입원ID", "환자ID", "병동", "진료과", "입원일", "퇴원일", "입원경로", "퇴원형태", "계획입원", "보험유형"]]
WARD = pd.DataFrame([dict(병동=w, 구분=c["구분"], 주진료과=" · ".join(c["진료과"]), 병상수=c["beds"]) for w, c in WARDS.items()])

# ---------------------------------------------------------------- DuckDB 로 저장 (타입을 분명히)
if os.path.exists(OUT):
    os.remove(OUT)
con = duckdb.connect(OUT)
DDL = {
    "환자": "환자ID VARCHAR PRIMARY KEY, 성별 VARCHAR, 생년월일 DATE, 사망일 DATE",
    "병동": "병동 VARCHAR PRIMARY KEY, 구분 VARCHAR, 주진료과 VARCHAR, 병상수 INTEGER",
    "입원": "입원ID INTEGER PRIMARY KEY, 환자ID VARCHAR REFERENCES 환자(환자ID), 병동 VARCHAR REFERENCES 병동(병동), 진료과 VARCHAR, "
            "입원일 DATE, 퇴원일 DATE, 입원경로 VARCHAR, 퇴원형태 VARCHAR, 계획입원 VARCHAR, 보험유형 VARCHAR",
    "진단": "진단ID INTEGER PRIMARY KEY, 입원ID INTEGER REFERENCES 입원(입원ID), 진단코드 VARCHAR, 주진단여부 VARCHAR",
    "병동일보": "병동 VARCHAR REFERENCES 병동(병동), 날짜 DATE, 재원환자수 INTEGER, 입원환자수 INTEGER, 퇴원환자수 INTEGER, PRIMARY KEY (병동, 날짜)",
    "근무": "병동 VARCHAR REFERENCES 병동(병동), 근무일 DATE, 근무조 VARCHAR, 간호사수 INTEGER, PRIMARY KEY (병동, 근무일, 근무조)",
    "진료비": "진료비ID INTEGER PRIMARY KEY, 입원ID INTEGER REFERENCES 입원(입원ID), 항목 VARCHAR, 금액 INTEGER, 급여구분 VARCHAR",
    "낙상": "낙상ID INTEGER PRIMARY KEY, 입원ID INTEGER REFERENCES 입원(입원ID), 발생일 DATE, 근무조 VARCHAR, 손상정도 VARCHAR",
    "검사": "검사ID INTEGER PRIMARY KEY, 환자ID VARCHAR REFERENCES 환자(환자ID), 검사일 DATE, 검사명 VARCHAR, 결과값 DOUBLE",
}
FRAMES = {"환자": PT, "병동": WARD, "입원": ADM, "진단": DX, "병동일보": CEN, "근무": DUTY, "진료비": COST, "낙상": FALL, "검사": LABS}
DATES = {"생년월일", "사망일", "입원일", "퇴원일", "날짜", "근무일", "발생일", "검사일"}
for t, ddl in DDL.items():
    con.execute(f"CREATE TABLE {t} ({ddl})")
    df = FRAMES[t].copy()
    for col in DATES & set(df.columns):
        df[col] = pd.to_datetime(df[col])
    con.register("df_", df)
    con.execute(f"INSERT INTO {t} SELECT * FROM df_")
    con.unregister("df_")

# ---------------------------------------------------------------- 확인: 병동일보 = 입원 표에서 센 재원 · 재원일수 합
chk = con.execute("""
SELECT (SELECT SUM(재원환자수) FROM 병동일보),
       (SELECT SUM(DATEDIFF('day', GREATEST(입원일, DATE '2024-01-01'), COALESCE(퇴원일, DATE '2025-01-01'))) FROM 입원)""").fetchone()
assert chk[0] == chk[1], chk
con.close()
with open(OUT, "rb") as f_in, gzip.open(OUT + ".gz", "wb", compresslevel=9) as f_out:
    shutil.copyfileobj(f_in, f_out)

# ---------------------------------------------------------------- 데이터 사전
DESC = {
    "환자": ("환자 1명", {"환자ID": "환자번호 (글자 7자리, 앞자리 0 있음 — 엑셀에서 숫자로 바뀌면 0 이 사라짐)", "성별": "M · F",
                       "생년월일": "", "사망일": "병원에서 사망한 날 (그 밖에는 NULL)"}),
    "병동": ("병동 1곳", {"병동": "병동 이름", "구분": "내과계 · 외과계", "주진료과": "", "병상수": "허가 병상 수"}),
    "입원": ("입원 1건 (같은 환자가 여러 번 입원하면 여러 행)", {"입원ID": "", "환자ID": "→ 환자", "병동": "→ 병동", "진료과": "",
             "입원일": "2023년 입원 중 2024년까지 재원한 입원도 들어 있음", "퇴원일": "2024-12-31 에 재원 중이면 NULL",
             "입원경로": "외래 · 응급", "퇴원형태": "자택 · 전원 · 사망 (재원 중이면 NULL)", "계획입원": "Y = 미리 계획한 입원 (예: 항암)",
             "보험유형": "건강보험 · 의료급여 · 자동차보험 · 산재보험"}),
    "진단": ("진단 1건 (입원 1건에 여러 개)", {"진단ID": "", "입원ID": "→ 입원", "진단코드": "KCD (예: E11.9, I63.9)", "주진단여부": "Y = 주진단 (입원 1건에 1개)"}),
    "병동일보": ("병동 × 날짜 (2024년 매일)", {"병동": "→ 병동", "날짜": "", "재원환자수": "그날 자정에 병동에 있던 환자 수", "입원환자수": "그날 입원한 환자 수", "퇴원환자수": "그날 퇴원한 환자 수"}),
    "근무": ("병동 × 날짜 × 근무조", {"병동": "→ 병동", "근무일": "", "근무조": "D 낮 · E 초번 · N 밤", "간호사수": "그 근무조의 간호사 수"}),
    "진료비": ("입원 × 진료비 항목", {"진료비ID": "", "입원ID": "→ 입원", "항목": "입원료 · 식대 · 검사료 · 약제비 · 영상진단료 · 처치·수술료 · 재료대 · 상급병실료 · 비급여 검사료",
              "금액": "원", "급여구분": "급여 · 비급여"}),
    "낙상": ("낙상 1건", {"낙상ID": "", "입원ID": "→ 입원", "발생일": "", "근무조": "D 낮 · E 초번 · N 밤", "손상정도": "없음 · 경증 · 중등도 이상"}),
    "검사": ("검사 1건 (환자 1명에 여러 건)", {"검사ID": "", "환자ID": "→ 환자", "검사일": "재원 중 검사 + 일부는 퇴원 뒤 외래 추적 검사",
            "검사명": "알부민 · 헤모글로빈 · 크레아티닌 · 당화혈색소", "결과값": "검체 불량 등으로 결과가 없으면 NULL"}),
}
con = duckdb.connect(OUT, read_only=True)
out = ["# 가상 병원 CDW (hospital_mini) 데이터 사전", "",
       "**실제 병원 자료가 아닙니다.** 수업용으로 만든 가상 자료입니다 (`tools/build_hospital_mini.py`, 고정 난수). "
       "기간: 2024-01-01 ~ 2024-12-31 (자료 기준일 2024-12-31). 병동 6곳.", ""]
for t, (unit, cols) in DESC.items():
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    out += [f"## {t} — 한 행 = {unit} · {n:,}행", "", "| 열 | 타입 | 설명 |", "|---|---|---|"]
    for name, typ in con.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}' ORDER BY ordinal_position").fetchall():
        out.append(f"| `{name}` | {typ} | {cols.get(name, '')} |")
    out.append("")
open(DICT, "w", encoding="utf-8").write("\n".join(out))
print("saved:", OUT, f"({os.path.getsize(OUT) / 1e6:.1f} MB, gz {os.path.getsize(OUT + '.gz') / 1e6:.1f} MB)")
for t in DDL:
    print(f"  {t}: {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:,}행")
