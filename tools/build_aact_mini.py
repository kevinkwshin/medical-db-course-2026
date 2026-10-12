# -*- coding: utf-8 -*-
"""
build_aact_mini.py — AACT(ClinicalTrials.gov) PostgreSQL에서 수업용 소형 데이터베이스(data/aact_mini.duckdb)를 만듭니다.

준비
  1) https://aact.ctti-clinicaltrials.org 에서 무료 계정 생성 (교수자 1회)
  2) data/.aact_env 파일에 두 줄 작성 (이 파일은 공유/배포하지 않음)
        AACT_USER=아이디
        AACT_PASSWORD=비밀번호
  3) 두 방법 중 하나
     (A) 스냅샷: AACT Download 페이지에서 "Flat Text Files"(파이프 구분 텍스트 zip)를 받아 data/ 에 두고
         python3 tools/build_aact_mini.py --snapshot data/<받은파일>.zip     (zip 또는 풀어 둔 폴더)
         → 필요한 14개 테이블 파일만 풀고, 빌드 후 자동 삭제 (--keep-extracted 로 유지)
     (B) 직접 접속: data/.aact_env 에 계정을 적고
         python3 tools/build_aact_mini.py
     python3 tools/build_aact_mini.py --dry-run  # 실행될 SQL만 출력
     * "PostgreSQL Database Dump"는 PostgreSQL 서버에 복원해야 하므로 사용하지 않습니다.

결과
  data/aact_mini.duckdb          학생 배포용 (Colab에서 duckdb로 바로 열림)
  data/aact_mini_dictionary.md   데이터 사전 (테이블 · 행 수 · 열 · 타입 · 설명)

참고: Flat Text Files 는 파이프(|) 구분, 헤더 1줄, 큰따옴표 인용, NULL=빈칸, 불리언 t/f, 긴 글의 줄바꿈은 '~' 로 저장됨
  (스크립트가 criteria/description 의 '~' 를 줄바꿈으로 되돌립니다)

표본 규칙 (서버 쪽에서 필터링되어 전송량이 작음)
  - 2015-01-01 ~ 2024-12-31 시작(start_date) 임상시험 중
  - 전체의 약 8% (nct_id 해시 기반, 재현 가능) + 과제 배정 질환(ASSIGNED_MESH)은 약 30%
"""
import os, sys, re, time, datetime, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ENV_FILE = os.path.join(DATA, ".aact_env")
OUT_DB = os.path.join(DATA, "aact_mini.duckdb")
OUT_DICT = os.path.join(DATA, "aact_mini_dictionary.md")
DRY = "--dry-run" in sys.argv

# 과제에서 학번별로 배정할 질환 (MeSH term, browse_conditions.mesh_term 기준)
ASSIGNED_MESH = [
    "Diabetes Mellitus, Type 2", "Hypertension", "Asthma", "Breast Neoplasms", "Depressive Disorder",
    "Stroke", "Heart Failure", "Pulmonary Disease, Chronic Obstructive", "Renal Insufficiency, Chronic",
    "Alzheimer Disease", "Obesity", "COVID-19", "Osteoarthritis", "Sepsis", "Pneumonia",
]

def sql_list(items):
    return ", ".join("'" + i.replace("'", "''") + "'" for i in items)

SAMPLE_SQL = f"""
    SELECT s.nct_id
    FROM ctgov.studies s
    WHERE s.start_date >= DATE '2015-01-01' AND s.start_date < DATE '2025-01-01'
      AND ( abs(hashtext(s.nct_id)) % 100 < 8
            OR ( abs(hashtext(s.nct_id)) % 100 < 30
                 AND s.nct_id IN (SELECT bc.nct_id FROM ctgov.browse_conditions bc
                                  WHERE bc.mesh_term IN ({sql_list(ASSIGNED_MESH)})) ) )
"""

# 테이블별로 가져올 열 (AACT ctgov 스키마). '*'는 전체.
TABLES = {
    "studies": """nct_id, brief_title, official_title, acronym, study_type, overall_status, last_known_status, why_stopped,
                  phase, enrollment, enrollment_type, source, source_class, number_of_arms, number_of_groups,
                  start_date, start_date_type, start_month_year, primary_completion_date, primary_completion_date_type,
                  completion_date, completion_date_type, study_first_submitted_date, study_first_posted_date,
                  results_first_posted_date, last_update_posted_date, has_dmc, is_fda_regulated_drug, is_fda_regulated_device,
                  plan_to_share_ipd""",
    "brief_summaries": "id, nct_id, replace(description, '~', chr(10)) AS description",
    "conditions": "id, nct_id, name, downcase_name",
    "browse_conditions": "id, nct_id, mesh_term, downcase_mesh_term, mesh_type",
    "interventions": "id, nct_id, intervention_type, name, replace(description, '~', chr(10)) AS description",
    "browse_interventions": "id, nct_id, mesh_term, downcase_mesh_term, mesh_type",
    "sponsors": "id, nct_id, agency_class, lead_or_collaborator, name",
    "facilities": "id, nct_id, status, name, city, state, zip, country",
    "countries": "id, nct_id, name, removed",
    "eligibilities": """id, nct_id, sampling_method, gender, minimum_age, maximum_age, healthy_volunteers, population,
                        replace(left(criteria, 1500), '~', chr(10)) AS criteria, gender_based, adult, child, older_adult""",
    "calculated_values": """id, nct_id, number_of_facilities, registered_in_calendar_year, actual_duration,
                            were_results_reported, months_to_report_results, has_us_facility, has_single_facility,
                            minimum_age_num, maximum_age_num, minimum_age_unit, maximum_age_unit,
                            number_of_primary_outcomes_to_measure, number_of_secondary_outcomes_to_measure""",
    "designs": """id, nct_id, allocation, intervention_model, observational_model, primary_purpose, time_perspective,
                  masking, subject_masked, caregiver_masked, investigator_masked, outcomes_assessor_masked""",
    "design_outcomes": "id, nct_id, outcome_type, measure, time_frame, population",
    "keywords": "id, nct_id, name, downcase_name",
}

# 데이터 사전에 넣을 한국어 설명 (없는 열은 빈칸으로 남김)
DESC_TABLE = {
    "studies": "임상시험 1건 = 1행. 모든 테이블의 기준 (기본키 nct_id)",
    "brief_summaries": "임상시험 요약문 (1건당 1행)",
    "conditions": "연구자가 입력한 대상 질환 이름 (자유 텍스트, 1건당 여러 행)",
    "browse_conditions": "MeSH 표준 용어로 정리된 대상 질환 (1건당 여러 행)",
    "interventions": "중재(약물 · 시술 · 행동요법 등) (1건당 여러 행)",
    "browse_interventions": "MeSH 표준 용어로 정리된 중재 (1건당 여러 행)",
    "sponsors": "스폰서 · 협력기관 (1건당 여러 행)",
    "facilities": "시험 수행 기관 (1건당 여러 행, 다국가 시험은 수백 행)",
    "countries": "시험 수행 국가 (1건당 여러 행, removed = 제외된 국가 표시)",
    "eligibilities": "선정 · 제외 기준 (1건당 1행, 나이는 문자열 '18 Years')",
    "calculated_values": "AACT가 계산해 둔 값 (1건당 1행, 나이의 숫자형 minimum_age_num 등)",
    "designs": "연구 설계 (배정 · 눈가림 · 목적 등, 1건당 1행)",
    "design_outcomes": "계획된 결과변수 (primary/secondary, 1건당 여러 행)",
    "keywords": "연구자가 입력한 키워드 (1건당 여러 행)",
}
DESC_COL = {
    "nct_id": "ClinicalTrials.gov 등록번호 (NCT + 8자리)", "brief_title": "시험 제목(짧은)", "official_title": "공식 제목",
    "study_type": "INTERVENTIONAL / OBSERVATIONAL 등", "overall_status": "진행 상태 (COMPLETED, RECRUITING, …)",
    "why_stopped": "중단 사유 (중단된 경우만)", "phase": "임상 단계 (PHASE1, PHASE2/PHASE3, NA …)",
    "enrollment": "등록 인원(명)", "enrollment_type": "ACTUAL(실제) / ESTIMATED(예상)", "source": "등록 기관명",
    "start_date": "시작일 (DATE)", "start_month_year": "시작 연월 (문자열)", "completion_date": "종료일",
    "primary_completion_date": "일차 결과 수집 종료일", "results_first_posted_date": "결과 최초 게시일 (없으면 NULL)",
    "mesh_term": "MeSH 표준 용어", "mesh_type": "mesh-list / mesh-ancestor", "intervention_type": "DRUG, DEVICE, BEHAVIORAL …",
    "agency_class": "INDUSTRY, NIH, OTHER …", "lead_or_collaborator": "lead(주관) / collaborator(협력)",
    "country": "국가명", "removed": "TRUE면 등록 후 제외된 국가", "gender": "ALL / FEMALE / MALE",
    "minimum_age": "최소 연령 (문자열, 예 '18 Years')", "maximum_age": "최대 연령 (문자열, 'N/A' 포함)",
    "healthy_volunteers": "건강한 지원자 허용 여부", "criteria": "선정 · 제외 기준 원문 (1500자까지)",
    "minimum_age_num": "최소 연령 숫자", "minimum_age_unit": "최소 연령 단위 (Years, Months …)",
    "number_of_facilities": "기관 수", "were_results_reported": "결과 보고 여부", "actual_duration": "실제 기간(월)",
    "allocation": "RANDOMIZED / NON_RANDOMIZED / NA", "masking": "NONE, SINGLE, DOUBLE …", "primary_purpose": "TREATMENT, PREVENTION …",
    "outcome_type": "primary / secondary / other", "measure": "결과변수 이름", "time_frame": "측정 시점",
}


def load_env():
    env = dict(os.environ)
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env.get("AACT_USER"), env.get("AACT_PASSWORD")


def snapshot_arg():
    if "--snapshot" in sys.argv:
        i = sys.argv.index("--snapshot")
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        sys.exit("--snapshot 뒤에 zip 파일 또는 폴더 경로를 적어 주세요.")
    return None


def find_txt(root, table):
    """스냅샷 폴더 안에서 <table>.txt 를 재귀적으로 찾습니다."""
    for dp, dn, fn in os.walk(root):
        if f"{table}.txt" in fn:
            return os.path.join(dp, f"{table}.txt")
    return None


def extract_needed(zip_path, folder):
    """zip 안에서 필요한 14개 테이블의 .txt 만 골라 풉니다 (전체를 풀면 수 GB가 더 필요)."""
    import zipfile
    os.makedirs(folder, exist_ok=True)
    wanted = {f"{t}.txt" for t in TABLES}
    found = set()
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            base = os.path.basename(info.filename)
            if base in wanted and not info.is_dir():
                target = os.path.join(folder, base)
                if not os.path.exists(target) or os.path.getsize(target) != info.file_size:
                    print(f"  extracting {base} ({info.file_size / 1e6:,.0f} MB)")
                    with z.open(info) as src, open(target, "wb") as dst:
                        shutil.copyfileobj(src, dst, 1024 * 1024)
                found.add(base)
    missing = wanted - found
    if missing:
        sys.exit(f"zip 안에 다음 파일이 없습니다: {sorted(missing)}  (Flat Text Files 스냅샷이 맞는지 확인)")


def build_from_snapshot(con, snap):
    extracted = None
    if os.path.isfile(snap) and snap.lower().endswith(".zip"):
        extracted = os.path.join(DATA, "aact_snapshot")
        print("extracting needed tables from", snap)
        extract_needed(snap, extracted)
        snap = extracted
    if not os.path.isdir(snap):
        sys.exit(f"스냅샷 경로를 찾을 수 없습니다: {snap}")
    csv_opts = "delim='|', header=true, quote='\"', escape='\"', nullstr='', sample_size=-1, ignore_errors=true"
    t0 = time.time()
    # 원본 파일을 뷰로 연결
    for t in TABLES:
        path = find_txt(snap, t)
        if path is None:
            sys.exit(f"스냅샷에 {t}.txt 가 없습니다.")
        con.execute(f"CREATE VIEW raw_{t} AS SELECT * FROM read_csv('{path}', {csv_opts})")
    # 표본 선택 (DuckDB hash 기반, 재현 가능)
    con.execute(f"""
        CREATE TABLE sample AS
        SELECT s.nct_id FROM raw_studies s
        WHERE s.start_date >= DATE '2015-01-01' AND s.start_date < DATE '2025-01-01'
          AND ( hash(s.nct_id) % 100 < 8
                OR ( hash(s.nct_id) % 100 < 30
                     AND s.nct_id IN (SELECT nct_id FROM raw_browse_conditions
                                      WHERE mesh_term IN ({sql_list(ASSIGNED_MESH)})) ) )
    """)
    print(f"sample: {con.execute('SELECT count(*) FROM sample').fetchone()[0]:,} studies  ({time.time() - t0:.0f}s)")
    for t, cols in TABLES.items():
        con.execute(f"CREATE TABLE {t} AS SELECT {cols} FROM raw_{t} WHERE nct_id IN (SELECT nct_id FROM sample)")
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"{t:22s} {n:>9,d} rows   ({time.time() - t0:6.0f}s)")
    for t in TABLES:
        con.execute(f"DROP VIEW raw_{t}")
    con.execute("DROP TABLE sample")
    if extracted and "--keep-extracted" not in sys.argv:
        shutil.rmtree(extracted, ignore_errors=True)
        print("removed extracted files (use --keep-extracted to keep them)")


def main():
    import duckdb
    os.makedirs(DATA, exist_ok=True)
    snap = snapshot_arg()
    user, pw = load_env()
    if not DRY and snap is None and not (user and pw):
        sys.exit(f"AACT 계정 정보가 없습니다. {ENV_FILE} 에 AACT_USER / AACT_PASSWORD 를 적거나, --snapshot <zip> 을 사용해 주세요.")
    if DRY:
        print("-- SAMPLE --", SAMPLE_SQL)
        for t, cols in TABLES.items():
            flat = re.sub(r"\s+", " ", cols)
            print(f"-- {t}\nSELECT {flat} FROM ctgov.{t} WHERE nct_id IN (<SAMPLE>)\n")
        return
    if os.path.exists(OUT_DB):
        os.remove(OUT_DB)
    con = duckdb.connect(OUT_DB)
    if snap is not None:
        build_from_snapshot(con, snap)
    else:
        con.execute("INSTALL postgres; LOAD postgres;")
        dsn = f"host=aact-db.ctti-clinicaltrials.org port=5432 dbname=aact user={user} password={pw} sslmode=require"
        con.execute(f"ATTACH '{dsn}' AS pg (TYPE postgres, READ_ONLY)")
        t0 = time.time()
        for t, cols in TABLES.items():
            q = f"SELECT {cols} FROM ctgov.{t} WHERE nct_id IN ({SAMPLE_SQL})"
            con.execute(f"CREATE TABLE {t} AS SELECT * FROM postgres_query('pg', $q${q}$q$)")
            n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            print(f"{t:22s} {n:>9,d} rows   ({time.time() - t0:6.0f}s)")
        con.execute("DETACH pg")
    # 표본 정보
    n_st = con.execute("SELECT count(*) FROM studies").fetchone()[0]
    con.execute("CHECKPOINT")
    write_dictionary(con, n_st)
    con.close()
    print("done:", OUT_DB, f"{os.path.getsize(OUT_DB) / 1e6:.0f} MB")


def write_dictionary(con, n_st):
    lines = [f"# aact_mini 데이터 사전", "",
             f"- 원본: AACT (Aggregate Analysis of ClinicalTrials.gov), 추출일 {datetime.date.today()}",
             f"- 표본: 2015~2024년 시작 임상시험 {n_st:,}건 (전체 약 8% + 과제 배정 질환 약 30%)",
             f"- 모든 테이블은 nct_id 로 studies 와 연결됩니다.", ""]
    for t in TABLES:
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        lines += [f"## {t}  ({n:,} rows)", "", DESC_TABLE.get(t, ""), "", "| 열 | 타입 | 설명 |", "|---|---|---|"]
        for name, typ in con.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}' ORDER BY ordinal_position").fetchall():
            lines.append(f"| {name} | {typ} | {DESC_COL.get(name, '')} |")
        lines.append("")
    open(OUT_DICT, "w", encoding="utf-8").write("\n".join(lines))
    print("dictionary:", OUT_DICT)


if __name__ == "__main__":
    main()
