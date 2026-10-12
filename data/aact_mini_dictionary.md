# aact_mini 데이터 사전

- 원본: AACT (Aggregate Analysis of ClinicalTrials.gov), 추출일 2026-09-19
- 표본: 2015~2024년 시작 임상시험 37,509건 (전체 약 8% + 과제 배정 질환 약 30%)
- 모든 테이블은 nct_id 로 studies 와 연결됩니다.

## studies  (37,509 rows)

임상시험 1건 = 1행. 모든 테이블의 기준 (기본키 nct_id)

| 열 | 타입 | 설명 |
|---|---|---|
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| brief_title | VARCHAR | 시험 제목(짧은) |
| official_title | VARCHAR | 공식 제목 |
| acronym | VARCHAR |  |
| study_type | VARCHAR | INTERVENTIONAL / OBSERVATIONAL 등 |
| overall_status | VARCHAR | 진행 상태 (COMPLETED, RECRUITING, …) |
| last_known_status | VARCHAR |  |
| why_stopped | VARCHAR | 중단 사유 (중단된 경우만) |
| phase | VARCHAR | 임상 단계 (PHASE1, PHASE2/PHASE3, NA …) |
| enrollment | BIGINT | 등록 인원(명) |
| enrollment_type | VARCHAR | ACTUAL(실제) / ESTIMATED(예상) |
| source | VARCHAR | 등록 기관명 |
| source_class | VARCHAR |  |
| number_of_arms | BIGINT |  |
| number_of_groups | BIGINT |  |
| start_date | DATE | 시작일 (DATE) |
| start_date_type | VARCHAR |  |
| start_month_year | VARCHAR | 시작 연월 (문자열) |
| primary_completion_date | DATE | 일차 결과 수집 종료일 |
| primary_completion_date_type | VARCHAR |  |
| completion_date | DATE | 종료일 |
| completion_date_type | VARCHAR |  |
| study_first_submitted_date | DATE |  |
| study_first_posted_date | DATE |  |
| results_first_posted_date | DATE | 결과 최초 게시일 (없으면 NULL) |
| last_update_posted_date | DATE |  |
| has_dmc | BOOLEAN |  |
| is_fda_regulated_drug | BOOLEAN |  |
| is_fda_regulated_device | BOOLEAN |  |
| plan_to_share_ipd | VARCHAR |  |

## brief_summaries  (37,509 rows)

임상시험 요약문 (1건당 1행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| description | VARCHAR |  |

## conditions  (73,173 rows)

연구자가 입력한 대상 질환 이름 (자유 텍스트, 1건당 여러 행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| name | VARCHAR |  |
| downcase_name | VARCHAR |  |

## browse_conditions  (309,124 rows)

MeSH 표준 용어로 정리된 대상 질환 (1건당 여러 행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| mesh_term | VARCHAR | MeSH 표준 용어 |
| downcase_mesh_term | VARCHAR |  |
| mesh_type | VARCHAR | mesh-list / mesh-ancestor |

## interventions  (63,093 rows)

중재(약물 · 시술 · 행동요법 등) (1건당 여러 행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| intervention_type | VARCHAR | DRUG, DEVICE, BEHAVIORAL … |
| name | VARCHAR |  |
| description | VARCHAR |  |

## browse_interventions  (134,385 rows)

MeSH 표준 용어로 정리된 중재 (1건당 여러 행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| mesh_term | VARCHAR | MeSH 표준 용어 |
| downcase_mesh_term | VARCHAR |  |
| mesh_type | VARCHAR | mesh-list / mesh-ancestor |

## sponsors  (62,783 rows)

스폰서 · 협력기관 (1건당 여러 행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| agency_class | VARCHAR | INDUSTRY, NIH, OTHER … |
| lead_or_collaborator | VARCHAR | lead(주관) / collaborator(협력) |
| name | VARCHAR |  |

## facilities  (208,690 rows)

시험 수행 기관 (1건당 여러 행, 다국가 시험은 수백 행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| status | VARCHAR |  |
| name | VARCHAR |  |
| city | VARCHAR |  |
| state | VARCHAR |  |
| zip | VARCHAR |  |
| country | VARCHAR | 국가명 |

## countries  (50,410 rows)

시험 수행 국가 (1건당 여러 행, removed = 제외된 국가 표시)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| name | VARCHAR |  |
| removed | BOOLEAN | TRUE면 등록 후 제외된 국가 |

## eligibilities  (37,509 rows)

선정 · 제외 기준 (1건당 1행, 나이는 문자열 '18 Years')

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| sampling_method | VARCHAR |  |
| gender | VARCHAR | ALL / FEMALE / MALE |
| minimum_age | VARCHAR | 최소 연령 (문자열, 예 '18 Years') |
| maximum_age | VARCHAR | 최대 연령 (문자열, 'N/A' 포함) |
| healthy_volunteers | BOOLEAN | 건강한 지원자 허용 여부 |
| population | VARCHAR |  |
| criteria | VARCHAR | 선정 · 제외 기준 원문 (1500자까지) |
| gender_based | BOOLEAN |  |
| adult | BOOLEAN |  |
| child | BOOLEAN |  |
| older_adult | BOOLEAN |  |

## calculated_values  (37,509 rows)

AACT가 계산해 둔 값 (1건당 1행, 나이의 숫자형 minimum_age_num 등)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| number_of_facilities | BIGINT | 기관 수 |
| registered_in_calendar_year | BIGINT |  |
| actual_duration | BIGINT | 실제 기간(월) |
| were_results_reported | BOOLEAN | 결과 보고 여부 |
| months_to_report_results | BIGINT |  |
| has_us_facility | BOOLEAN |  |
| has_single_facility | BOOLEAN |  |
| minimum_age_num | BIGINT | 최소 연령 숫자 |
| maximum_age_num | BIGINT |  |
| minimum_age_unit | VARCHAR | 최소 연령 단위 (Years, Months …) |
| maximum_age_unit | VARCHAR |  |
| number_of_primary_outcomes_to_measure | BIGINT |  |
| number_of_secondary_outcomes_to_measure | BIGINT |  |

## designs  (37,499 rows)

연구 설계 (배정 · 눈가림 · 목적 등, 1건당 1행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| allocation | VARCHAR | RANDOMIZED / NON_RANDOMIZED / NA |
| intervention_model | VARCHAR |  |
| observational_model | VARCHAR |  |
| primary_purpose | VARCHAR | TREATMENT, PREVENTION … |
| time_perspective | VARCHAR |  |
| masking | VARCHAR | NONE, SINGLE, DOUBLE … |
| subject_masked | BOOLEAN |  |
| caregiver_masked | BOOLEAN |  |
| investigator_masked | BOOLEAN |  |
| outcomes_assessor_masked | BOOLEAN |  |

## design_outcomes  (274,043 rows)

계획된 결과변수 (primary/secondary, 1건당 여러 행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| outcome_type | VARCHAR | primary / secondary / other |
| measure | VARCHAR | 결과변수 이름 |
| time_frame | VARCHAR | 측정 시점 |
| population | VARCHAR |  |

## keywords  (90,972 rows)

연구자가 입력한 키워드 (1건당 여러 행)

| 열 | 타입 | 설명 |
|---|---|---|
| id | BIGINT |  |
| nct_id | VARCHAR | ClinicalTrials.gov 등록번호 (NCT + 8자리) |
| name | VARCHAR |  |
| downcase_name | VARCHAR |  |
