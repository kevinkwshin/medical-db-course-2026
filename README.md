# 데이터베이스 관리 — 실습 자료 (2026)

보건대학원 「데이터베이스 관리」 수업의 실습 노트북과 데이터입니다.
ClinicalTrials.gov 임상시험 등록 자료(AACT)에서 2015~2024년 시작 시험 37,509건을 추린 수업용 DB(`aact_mini`)를 사용합니다.

## 바로 실행 (Google Colab)

아래 배지를 누르면 Colab에서 노트북이 열립니다. **준비 셀**을 실행하면 데이터(약 50MB)를 자동으로 내려받습니다. 과제는 맨 위 칸에 학번과 이름을 먼저 입력합니다.

| 주차 | 구분 | 내용 | Colab |
|---|---|---|---|
| 7주차 | 실습 | SQL (1) 조회 기초 — SELECT · WHERE · ORDER BY | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/07_실습_SQL기초.ipynb) |
| 8주차 | 실습 | SQL (2) 집계 · GROUP BY · JOIN | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/08_실습_집계와JOIN.ipynb) |
| 9주차 | 실습 | 질문을 SQL로 바꾸기 · 서브쿼리 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/09_실습_질문을SQL로.ipynb) |
| 9주차 | **과제 1** | 일반적인 SQL 사용법 — 잘못된 SQL 12개 고치기 (조회 · 집계 · JOIN) · 해석 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/과제1.ipynb) |
| 10주차 | 실습 | 데이터 수정 · 트랜잭션 · 뷰 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/10_실습_데이터수정.ipynb) |
| 12주차 | 실습 | 데이터에서 나오는 오류 찾기 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/12_실습_오류찾기.ipynb) |
| 13주차 | **과제 2** | 당뇨병 임상시험 분석 — 변수 찾기 → 표 연결 → 통계 (잘못된 SQL 6개 고치기) · 결과표 · 해석 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/과제2.ipynb) |

> 작성한 내용을 저장하려면 Colab 메뉴 **파일 → Drive에 사본 저장** 을 먼저 눌러 주세요.

## 데이터 구성

모든 표는 `nct_id`(임상시험 등록번호)로 `studies` 와 연결됩니다. `studies` 의 기본키는 `nct_id`, 나머지 표의 기본키는 `id` 이고, 각 표의 `nct_id` 는 `studies.nct_id` 를 가리키는 외래키입니다.

![aact_mini 데이터 구성 (ERD)](data/aact_mini_erd.png)

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `notebooks/` | 학생용 실습 · 과제 노트북 |
| `data/aact_mini.duckdb.gz` | 수업용 DB (압축본, 노트북이 자동으로 풀어 사용) |
| `data/aact_mini_dictionary.md` | 데이터 사전 (테이블 · 컬럼 설명) |
| `data/aact_mini_erd.png` | 데이터 구성도 (`tools/build_erd.py` 로 생성) |
| `tools/` | 슬라이드 · 노트북 생성 도구 (교수자용) |

## 내 컴퓨터에서 실행

```bash
pip install "duckdb==1.4.5" "jupysql==0.11.1" "duckdb-engine==0.17.0" pandas
gunzip -k data/aact_mini.duckdb.gz
jupyter notebook notebooks/
```

## 데이터 출처 — AACT 와 aact_mini

**AACT (Aggregate Analysis of ClinicalTrials.gov)** 는 Clinical Trials Transformation Initiative(CTTI)가 ClinicalTrials.gov 등록 자료 전체를 관계형 데이터베이스로 정리해 매일 공개하는 자료입니다.

| 항목 | 링크 |
|---|---|
| AACT 홈페이지 | <https://aact.ctti-clinicaltrials.org/> |
| 내려받기 (무료 회원가입 후 로그인) | <https://aact.ctti-clinicaltrials.org/snapshots> → **Flat Text Files** (파이프 `\|` 로 구분한 텍스트 파일 묶음, zip) |

### aact_mini 를 만든 과정

| 단계 | 한 일 |
|---|---|
| ① 내려받기 | 2026년 9월 AACT 스냅샷의 Flat Text Files(zip 약 2.5GB, 표 49개)를 받았습니다. 자료 기준일은 2026년 9월 중순입니다(가장 최근 결과 게시일 2026-09-17). |
| ② 표 고르기 | 수업에 쓰는 **14개 표**만 꺼냈습니다: `studies`, `brief_summaries`, `conditions`, `browse_conditions`, `interventions`, `browse_interventions`, `sponsors`, `facilities`, `countries`, `eligibilities`, `calculated_values`, `designs`, `design_outcomes`, `keywords` |
| ③ 시험 고르기 | **2015-01-01 ~ 2024-12-31 에 시작한 시험** 중 일부만 뽑았습니다. 등록번호(`nct_id`)의 해시값으로 약 8% 를 골라, 다시 만들어도 같은 시험이 뽑힙니다. 자주 쓰는 15개 질환(제2형 당뇨병 등)은 시험 수가 넉넉하도록 약 30% 를 뽑았습니다. → **37,509건** |
| ④ 줄이기 | 14개 표에서 뽑힌 시험의 행만 남겨 DuckDB 파일 하나(`aact_mini.duckdb`, 114MB)로 저장하고, 데이터 사전(`aact_mini_dictionary.md`)을 함께 만들었습니다. 원본의 형식(빈칸 = NULL, 참/거짓 `t`/`f`, 긴 글의 줄바꿈 `~`)은 이때 정리했습니다. |
| ⑤ 배포 | gzip 으로 압축(48MB)해 이 저장소에 올렸습니다. 노트북의 준비 셀이 자동으로 받아 압축을 풉니다. |

다시 만들 때 (교수자용):

```bash
python3 tools/build_aact_mini.py --snapshot data/<내려받은_파일>.zip
```

> aact_mini 는 **표본**이므로 건수 · 비율이 ClinicalTrials.gov 전체와 다릅니다. 수업에서 나오는 숫자는 이 표본 기준입니다.
