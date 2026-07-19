# -*- coding: utf-8 -*-
"""
미니 EMR 데이터셋 생성기
========================
의료 데이터베이스 강의(15주)용 교육 데이터셋.
환자 50명 / 8개 테이블. seed 고정으로 언제 실행해도 같은 데이터가 나옵니다.

실행:  python3 generate_mini_emr.py
출력:  mini_emr.sqlite, csv/*.csv

※ 모든 데이터는 가상이며, 실제 환자와 무관합니다.
※ 주차별 실습 문제가 성립하도록 아래 시나리오가 의도적으로 심겨 있습니다.
   - 당뇨(E11) 진단 환자 중 HbA1c 검사가 없는 환자 존재    → 11주차 LEFT JOIN
   - 항생제를 한 번도 처방받지 않은 환자 존재               → 12주차 NOT EXISTS
   - 평균 재원일수보다 훨씬 긴 입원 존재                    → 12주차 서브쿼리
   - 2020년 이후 '첫' 뇌경색(I63) 진단 환자 (일부는 2020 이전 진단력 보유) → 13주차 코호트
   - 혈당 1건이 mmol/L 단위로 입력됨 (나머지는 mg/dL)       → 14주차 단위 함정
   - 검사 결과값이 NULL인 행 존재 ("검체 용혈로 결과 없음")   → 2·14주차 NULL 의미
"""

import csv
import os
import random
import sqlite3
from datetime import date, datetime, timedelta

random.seed(20260301)
BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- 참조 코드표
DEPTS = ["내과", "신경과", "외과", "정형외과", "응급의학과", "가정의학과", "소아청소년과"]

KCD = {
    "I10":   "본태성 고혈압",
    "I20.9": "협심증",
    "I48":   "심방세동",
    "I63.9": "뇌경색증",
    "E11.9": "2형 당뇨병",
    "E78.5": "고지혈증",
    "J18.9": "폐렴",
    "J45.9": "천식",
    "K29.7": "위염",
    "K80.2": "담낭결석",
    "N18.3": "만성 콩팥병(3기)",
    "M17.9": "무릎관절증",
    "A09.9": "감염성 장염",
    "S72.0": "대퇴골 경부 골절",
}

# (약품코드, 약품명, 용량, 항생제여부)
DRUGS = [
    ("MET500", "메트포르민",        "500mg",  False),
    ("AML5",   "암로디핀",          "5mg",    False),
    ("ATV20",  "아토르바스타틴",    "20mg",   False),
    ("ASA100", "아스피린",          "100mg",  False),
    ("CLO75",  "클로피도그렐",      "75mg",   False),
    ("PPI20",  "에스오메프라졸",    "20mg",   False),
    ("ACE500", "아세트아미노펜",    "500mg",  False),
    ("CTX2",   "세프트리악손 주사", "2g",     True),
    ("AMC625", "아목시실린/클라불란산", "625mg", True),
    ("LVX500", "레보플록사신",      "500mg",  True),
]

# (검사명, 단위, 정상하한, 정상상한, 소수자리)
LABS = [
    ("HbA1c",      "%",     4.0,  5.6,  1),
    ("Glucose",    "mg/dL", 70,   99,   0),
    ("Creatinine", "mg/dL", 0.6,  1.2,  2),
    ("Hemoglobin", "g/dL",  12.0, 16.0, 1),
    ("LDL",        "mg/dL", 0,    130,  0),
    ("CRP",        "mg/L",  0.0,  5.0,  1),
]

IMG_REPORTS = {
    ("CXR", "흉부"): [
        "양측 폐야에 활동성 병변 없음. 심비대 소견 없음.",
        "우하엽에 경계 불명확한 침윤 음영 관찰됨. 폐렴 의심. 임상 소견과 대조 바람.",
        "좌측 늑골횡격막각 둔화 소견. 소량의 흉수 의심.",
    ],
    ("MRI", "뇌"): [
        "좌측 중대뇌동맥 영역에 급성 뇌경색 소견. 출혈성 변화는 관찰되지 않음.",
        "우측 기저핵 부위에 급성 경색 병변. 확산강조영상에서 고신호 강도.",
        "미만성 소혈관 허혈성 변화 외 급성 병변 없음.",
    ],
    ("CT", "복부"): [
        "담낭 내 다발성 결석 관찰됨. 담낭벽 비후 동반. 급성 담낭염 의심.",
        "특이 소견 없음.",
    ],
    ("X-ray", "고관절"): [
        "우측 대퇴골 경부에 전위성 골절 관찰됨.",
    ],
}


def d(y, m, dd):
    return date(y, m, dd)


def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


# ---------------------------------------------------------------- 1. patient
# 성별·연령 분포: 고령 만성질환군 + 중년 + 청년 + 소아 1명
patients = []          # (patient_id, sex, birth_date, blood_type)
blood_types = ["A+", "A+", "B+", "O+", "O+", "AB+", "A-", "O-"]

birth_pool = (
    [random.randint(1938, 1955) for _ in range(16)]    # 70세 이상 고령군
    + [random.randint(1956, 1970) for _ in range(16)]  # 5·60대
    + [random.randint(1971, 1990) for _ in range(12)]  # 3·40대
    + [random.randint(1991, 2002) for _ in range(5)]   # 20대
    + [2014]                                           # 소아 1명 (P050)
)
for i, by in enumerate(birth_pool, start=1):
    pid = f"P{i:03d}"
    sex = random.choice(["M", "F"])
    bd = d(by, random.randint(1, 12), random.randint(1, 28))
    patients.append((pid, sex, bd.isoformat(), random.choice(blood_types)))

# 4주차 실습("65세 이상 여성")이 반드시 성립하도록 고령군 일부를 여성으로 고정
for idx in (0, 2, 5, 8, 11):
    p = patients[idx]
    patients[idx] = (p[0], "F", p[1] if False else p[2], p[3]) if False else (p[0], "F", p[2], p[3])

# ---------------------------------------------------------------- 2. staff
staff = []             # (staff_id, role, department)
sid = 0
for dept in DEPTS:
    for _ in range(2):
        sid += 1
        staff.append((f"S{sid:03d}", "의사", dept))
for dept in ["내과", "신경과", "외과", "응급의학과"]:
    sid += 1
    staff.append((f"S{sid:03d}", "간호사", dept))
staff += [
    (f"S{sid+1:03d}", "약사", "약제부"),
    (f"S{sid+2:03d}", "임상병리사", "진단검사의학과"),
    (f"S{sid+3:03d}", "방사선사", "영상의학과"),
]
doctors_by_dept = {}
for s in staff:
    if s[1] == "의사":
        doctors_by_dept.setdefault(s[2], []).append(s[0])

# ---------------------------------------------------------------- 3. visits & clinical records
visits, diagnoses, prescriptions, labs, vitals, imagings = [], [], [], [], [], []
_v = _dx = _rx = _lab = _img = 0


def add_visit(pid, vdate, dept, vtype, los=None):
    """los: 입원 시 재원일수"""
    global _v
    _v += 1
    vid = f"V{_v:04d}"
    disch = (vdate + timedelta(days=los)).isoformat() if los else None
    visits.append((vid, pid, vdate.isoformat(), dept,
                   vtype, disch, random.choice(doctors_by_dept[dept])))
    return vid, vdate


def add_dx(vid, code, primary=1):
    global _dx
    _dx += 1
    diagnoses.append((f"D{_dx:04d}", vid, code, KCD[code], primary))


def add_rx(vid, code, days=None):
    global _rx
    _rx += 1
    drug = next(x for x in DRUGS if x[0] == code)
    prescriptions.append((f"R{_rx:04d}", vid, drug[0], drug[1], drug[2],
                          days or random.choice([7, 14, 28, 30, 90])))


def add_lab(vid, vdate, name, value, unit=None, hour=None):
    global _lab
    _lab += 1
    spec = next(x for x in LABS if x[0] == name)
    t = datetime(vdate.year, vdate.month, vdate.day,
                 hour if hour is not None else random.choice([6, 7, 9, 10, 14, 16]),
                 random.randint(0, 59))
    labs.append((f"L{_lab:04d}", vid, name,
                 value, unit or spec[1], spec[2], spec[3], t.isoformat(sep=" ")))


def add_vitals(vid, vdate, n, sbp_base):
    for k in range(n):
        t = datetime(vdate.year, vdate.month, vdate.day, 8, 0) + timedelta(hours=8 * k)
        sbp = sbp_base + random.randint(-8, 8)
        vitals.append((vid, t.isoformat(sep=" "), sbp,
                       sbp - random.randint(35, 50),
                       random.randint(58, 105),
                       round(random.uniform(36.2, 37.2), 1),
                       random.randint(94, 100)))


def add_img(vid, vdate, modality, part, report=None):
    global _img
    _img += 1
    rep = report or random.choice(IMG_REPORTS[(modality, part)])
    imagings.append((f"IMG{_img:03d}", vid, modality, part, vdate.isoformat(), rep))


def lab_val(name, abnormal=False):
    lo, hi, nd = next((x[2], x[3], x[4]) for x in LABS if x[0] == name)
    v = random.uniform(hi * 1.05, hi * 1.6) if abnormal else random.uniform(lo, hi)
    return round(v, nd) if nd else int(round(v))


# ---- 시나리오 A: 만성질환 외래 추적군 (고혈압/당뇨/고지혈) -------------------
# P001~P020 중심. 당뇨 환자에게 HbA1c를 넣되, P007·P013은 '일부러' 뺀다(LEFT JOIN 소재).
chronic = {
    "P001": ["I10", "E11.9"], "P002": ["I10"],          "P003": ["E11.9", "E78.5"],
    "P004": ["I10", "E78.5"], "P005": ["E11.9"],        "P006": ["I10"],
    "P007": ["E11.9"],        "P008": ["I10", "I48"],   "P009": ["E78.5"],
    "P010": ["I10", "E11.9", "N18.3"],                  "P011": ["I10"],
    "P012": ["E11.9"],        "P013": ["E11.9", "I10"], "P014": ["I20.9", "I10"],
    "P015": ["J45.9"],        "P016": ["I10"],          "P017": ["E78.5", "I10"],
    "P018": ["K29.7"],        "P019": ["I10", "E78.5"], "P020": ["E11.9", "I10"],
}
NO_HBA1C = {"P007", "P013"}          # 당뇨인데 HbA1c 없음 → 11주차
HIGH_BP = {"P002", "P006", "P008", "P011", "P016"}   # CASE 분류용 고혈압군

for pid, codes in chronic.items():
    dept = "가정의학과" if pid in ("P009", "P015", "P018") else "내과"
    n_visit = random.choice([2, 3, 3, 4])
    for k in range(n_visit):
        vdate = rand_date(d(2023, 1, 2), d(2025, 11, 30))
        vid, vdate = add_visit(pid, vdate, dept, "외래")
        for j, c in enumerate(codes):
            add_dx(vid, c, primary=1 if j == 0 else 0)
        # 처방
        if "I10" in codes:
            add_rx(vid, "AML5", 30)
        if "E11.9" in codes:
            add_rx(vid, "MET500", 30)
        if "E78.5" in codes:
            add_rx(vid, "ATV20", 30)
        if "I48" in codes or "I20.9" in codes:
            add_rx(vid, "ASA100", 30)
        if "K29.7" in codes:
            add_rx(vid, "PPI20", 14)
        # 검사 (아침 공복 채혈)
        if "E11.9" in codes and pid not in NO_HBA1C:
            add_lab(vid, vdate, "HbA1c", round(random.uniform(6.5, 9.8), 1), hour=7)
        if "E11.9" in codes:
            add_lab(vid, vdate, "Glucose", random.randint(110, 220), hour=7)
        if "E78.5" in codes:
            add_lab(vid, vdate, "LDL", random.randint(115, 190), hour=7)
        if "N18.3" in codes:
            add_lab(vid, vdate, "Creatinine", round(random.uniform(1.4, 2.6), 2), hour=7)
        add_vitals(vid, vdate, 1, sbp_base=158 if pid in HIGH_BP else random.choice([112, 122, 132]))

# ---- 시나리오 B: 뇌경색(I63) 코호트 -----------------------------------------
# 13주차 실습: "2020-01-01 이후 '첫' I63 진단" 코호트.
#   신규 발생(2020 이후 첫 진단): P021~P028  → 코호트 포함 대상 8명
#   과거력 보유(2019년에 이미 I63): P029, P030 → washout에서 제외되어야 함
stroke_new = [f"P{i:03d}" for i in range(21, 29)]
stroke_old = ["P029", "P030"]

for pid in stroke_old:
    vdate = rand_date(d(2019, 2, 1), d(2019, 11, 30))
    vid, vdate = add_visit(pid, vdate, "신경과", "입원", los=random.randint(7, 14))
    add_dx(vid, "I63.9")
    add_rx(vid, "ASA100", 90)
    add_img(vid, vdate, "MRI", "뇌")
    add_vitals(vid, vdate, 3, sbp_base=150)

for pid in stroke_new + stroke_old:
    # 2020 이후 (신규군은 첫 진단, 과거력군은 재발/추적)
    vdate = rand_date(d(2020, 3, 1), d(2025, 6, 30))
    vid, vdate = add_visit(pid, vdate, "신경과", "입원", los=random.randint(5, 21))
    add_dx(vid, "I63.9")
    if random.random() < 0.6:
        add_dx(vid, "I10", primary=0)
        add_rx(vid, "AML5", 30)
    add_rx(vid, "CLO75", 90)
    add_rx(vid, "ATV20", 90)
    add_img(vid, vdate, "MRI", "뇌")
    add_lab(vid, vdate, "LDL", random.randint(120, 185), hour=6)
    add_vitals(vid, vdate, 4, sbp_base=152)
    # 퇴원 후 외래 추적
    f_date = vdate + timedelta(days=random.randint(30, 90))
    if f_date <= d(2025, 12, 20):
        fvid, f_date = add_visit(pid, f_date, "신경과", "외래")
        add_dx(fvid, "I63.9")
        add_rx(fvid, "CLO75", 90)

# ---- 시나리오 C: 급성기 입원 (폐렴/담낭염/골절) — 항생제 사용군 ---------------
# 폐렴 입원: 항생제 + CXR + CRP. P031~P036
for pid in [f"P{i:03d}" for i in range(31, 37)]:
    vdate = rand_date(d(2021, 1, 5), d(2025, 10, 31))
    los = random.randint(5, 12)
    vid, vdate = add_visit(pid, vdate, "내과", "입원", los=los)
    add_dx(vid, "J18.9")
    add_rx(vid, "CTX2", los)
    add_rx(vid, "ACE500", 5)
    add_lab(vid, vdate, "CRP", round(random.uniform(40, 180), 1), hour=6)
    add_lab(vid, vdate, "Hemoglobin", lab_val("Hemoglobin"), hour=6)
    add_img(vid, vdate, "CXR", "흉부",
            "우하엽에 경계 불명확한 침윤 음영 관찰됨. 폐렴 의심. 임상 소견과 대조 바람.")
    add_vitals(vid, vdate, 3, sbp_base=118)

# 담낭결석 수술 입원: P037, P038
for pid in ("P037", "P038"):
    vdate = rand_date(d(2022, 3, 1), d(2025, 8, 31))
    vid, vdate = add_visit(pid, vdate, "외과", "입원", los=random.randint(4, 7))
    add_dx(vid, "K80.2")
    add_rx(vid, "CTX2", 3)
    add_rx(vid, "ACE500", 5)
    add_img(vid, vdate, "CT", "복부",
            "담낭 내 다발성 결석 관찰됨. 담낭벽 비후 동반. 급성 담낭염 의심.")
    add_vitals(vid, vdate, 2, sbp_base=125)

# 대퇴골 골절 장기입원: P039 — '평균보다 훨씬 긴 재원'(12주차 서브쿼리 소재)
vid, vdate = add_visit("P039", d(2024, 1, 15), "정형외과", "입원", los=35)
add_dx(vid, "S72.0")
add_rx(vid, "CTX2", 5)
add_rx(vid, "ACE500", 14)
add_img(vid, vdate, "X-ray", "고관절")
add_lab(vid, vdate, "Hemoglobin", 9.8, hour=6)   # 수술 후 빈혈
add_vitals(vid, vdate, 5, sbp_base=128)

# ---- 시나리오 D: 응급실 내원 -------------------------------------------------
# 장염/천식발작 등 경증: P040~P046 (항생제 없이 귀가 → NOT EXISTS 소재 겸용)
for pid in [f"P{i:03d}" for i in range(40, 47)]:
    vdate = rand_date(d(2022, 1, 1), d(2025, 12, 15))
    vid, vdate = add_visit(pid, vdate, "응급의학과", "응급")
    code = random.choice(["A09.9", "J45.9", "K29.7"])
    add_dx(vid, code)
    add_rx(vid, "ACE500", 3)
    if code == "K29.7":
        add_rx(vid, "PPI20", 7)
    add_vitals(vid, vdate, 2, sbp_base=random.choice([110, 118, 126]))

# 소아 응급: P050
vid, vdate = add_visit("P050", d(2025, 5, 5), "소아청소년과", "응급")
add_dx(vid, "A09.9")
add_rx(vid, "ACE500", 3)
add_vitals(vid, vdate, 1, sbp_base=100)

# ---- 시나리오 E: 건강검진성 외래 (P047~P049) — 검사만 있고 처방 없음 ----------
for pid in ("P047", "P048", "P049"):
    vdate = rand_date(d(2024, 1, 10), d(2025, 11, 30))
    vid, vdate = add_visit(pid, vdate, "가정의학과", "외래")
    add_dx(vid, "K29.7" if pid == "P048" else "E78.5")
    add_lab(vid, vdate, "Glucose", random.randint(82, 118), hour=7)
    add_lab(vid, vdate, "LDL", random.randint(95, 175), hour=7)
    add_lab(vid, vdate, "Hemoglobin", lab_val("Hemoglobin"), hour=7)
    add_vitals(vid, vdate, 1, sbp_base=random.choice([108, 118, 135]))

# ---- 14주차용 함정 데이터 -----------------------------------------------------
# (1) 혈당 단위 불일치: 1건만 mmol/L (140.4 mg/dL에 해당하는 7.8)
trap_vid = visits[10][0]
trap_date = date.fromisoformat(visits[10][2])
add_lab(trap_vid, trap_date, "Glucose", 7.8, unit="mmol/L", hour=14)
# (2) 결과값 NULL: 검체 용혈로 재채혈 필요 — "검사를 했는데 결과가 없음"
add_lab(visits[20][0], date.fromisoformat(visits[20][2]), "Creatinine", None, hour=15)

# ---------------------------------------------------------------- 저장
SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE patient (                    -- 환자 (가명화: 이름·주민번호 없음)
  patient_id  TEXT PRIMARY KEY,           -- 환자ID (P001~)
  sex         TEXT NOT NULL CHECK (sex IN ('M','F')),
  birth_date  DATE NOT NULL,              -- 생년월일
  blood_type  TEXT                        -- 혈액형 (ABO/Rh)
);

CREATE TABLE staff (                      -- 의료진
  staff_id    TEXT PRIMARY KEY,
  role        TEXT NOT NULL,              -- 직종 (의사/간호사/약사/…)
  department  TEXT NOT NULL               -- 소속 진료과/부서
);

CREATE TABLE visit (                      -- 내원
  visit_id       TEXT PRIMARY KEY,        -- 내원ID (V0001~)
  patient_id     TEXT NOT NULL REFERENCES patient(patient_id),
  visit_date     DATE NOT NULL,           -- 내원일
  department     TEXT NOT NULL,           -- 진료과
  visit_type     TEXT NOT NULL CHECK (visit_type IN ('외래','입원','응급')),
  discharge_date DATE,                    -- 퇴원일 (외래/응급 귀가는 NULL)
  attending_id   TEXT REFERENCES staff(staff_id)  -- 담당의
);

CREATE TABLE diagnosis (                  -- 진단
  dx_id      TEXT PRIMARY KEY,
  visit_id   TEXT NOT NULL REFERENCES visit(visit_id),
  kcd_code   TEXT NOT NULL,               -- KCD-8 상병코드
  dx_name    TEXT NOT NULL,               -- 진단명
  is_primary INTEGER NOT NULL CHECK (is_primary IN (0,1))  -- 주진단 여부
);

CREATE TABLE prescription (               -- 처방
  rx_id         TEXT PRIMARY KEY,
  visit_id      TEXT NOT NULL REFERENCES visit(visit_id),
  drug_code     TEXT NOT NULL,
  drug_name     TEXT NOT NULL,
  dose          TEXT NOT NULL,            -- 용량
  duration_days INTEGER NOT NULL          -- 투약일수
);

CREATE TABLE lab (                        -- 검체 검사
  lab_id       TEXT PRIMARY KEY,
  visit_id     TEXT NOT NULL REFERENCES visit(visit_id),
  test_name    TEXT NOT NULL,             -- 검사명
  result_value REAL,                      -- 결과값 (NULL = 결과 미산출)
  unit         TEXT,                      -- 단위
  ref_low      REAL,                      -- 정상 하한
  ref_high     REAL,                      -- 정상 상한
  collected_at DATETIME                   -- 채혈 시각
);

CREATE TABLE vital (                      -- 활력징후
  visit_id    TEXT NOT NULL REFERENCES visit(visit_id),
  measured_at DATETIME NOT NULL,          -- 측정 시각
  sbp         INTEGER,                    -- 수축기혈압
  dbp         INTEGER,                    -- 이완기혈압
  pulse       INTEGER,                    -- 맥박
  temp        REAL,                       -- 체온
  spo2        INTEGER,                    -- 산소포화도
  PRIMARY KEY (visit_id, measured_at)
);

CREATE TABLE imaging (                    -- 영상 검사
  img_id     TEXT PRIMARY KEY,
  visit_id   TEXT NOT NULL REFERENCES visit(visit_id),
  modality   TEXT NOT NULL,               -- 촬영 종류 (CXR/CT/MRI/X-ray)
  body_part  TEXT NOT NULL,               -- 부위
  taken_date DATE NOT NULL,               -- 촬영일
  report     TEXT                         -- 판독문 (비정형 텍스트)
);
"""

TABLES = {
    "patient":      (["patient_id", "sex", "birth_date", "blood_type"], patients),
    "staff":        (["staff_id", "role", "department"], staff),
    "visit":        (["visit_id", "patient_id", "visit_date", "department",
                      "visit_type", "discharge_date", "attending_id"], visits),
    "diagnosis":    (["dx_id", "visit_id", "kcd_code", "dx_name", "is_primary"], diagnoses),
    "prescription": (["rx_id", "visit_id", "drug_code", "drug_name", "dose",
                      "duration_days"], prescriptions),
    "lab":          (["lab_id", "visit_id", "test_name", "result_value", "unit",
                      "ref_low", "ref_high", "collected_at"], labs),
    "vital":        (["visit_id", "measured_at", "sbp", "dbp", "pulse", "temp",
                      "spo2"], vitals),
    "imaging":      (["img_id", "visit_id", "modality", "body_part", "taken_date",
                      "report"], imagings),
}


def main():
    db_path = os.path.join(BASE, "mini_emr.sqlite")
    csv_dir = os.path.join(BASE, "csv")
    os.makedirs(csv_dir, exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    for name, (cols, rows) in TABLES.items():
        ph = ",".join("?" * len(cols))
        con.executemany(f"INSERT INTO {name} ({','.join(cols)}) VALUES ({ph})", rows)
        with open(os.path.join(csv_dir, f"{name}.csv"), "w", newline="",
                  encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
    con.commit()

    print("=== 미니 EMR 생성 완료 ===")
    for name in TABLES:
        n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"  {name:13s}: {n:4d} rows")
    con.close()


if __name__ == "__main__":
    main()
