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
| 9주차 | **과제 1** | 잘못된 SQL 고치기 (오류 메시지가 나는 실수 12문항) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/과제1.ipynb) |
| 10주차 | 실습 | 표 만들기 · 데이터 수정 · 트랜잭션 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/10_실습_데이터수정.ipynb) |
| 12주차 | 실습 | 데이터에서 나오는 오류 찾기 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/12_실습_오류찾기.ipynb) |
| 13주차 | **과제 2** | 잘못된 SQL 고치기 (결과가 틀리는 실수 6단계) · 검산표 · 해석 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kevinkwshin/medical-db-course-2026/blob/main/notebooks/과제2.ipynb) |

> 작성한 내용을 저장하려면 Colab 메뉴 **파일 → Drive에 사본 저장** 을 먼저 눌러 주세요.

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `notebooks/` | 학생용 실습 · 과제 노트북 |
| `data/aact_mini.duckdb.gz` | 수업용 DB (압축본, 노트북이 자동으로 풀어 사용) |
| `data/aact_mini_dictionary.md` | 데이터 사전 (테이블 · 컬럼 설명) |
| `tools/` | 슬라이드 · 노트북 생성 도구 (교수자용) |

## 내 컴퓨터에서 실행

```bash
pip install "duckdb==1.4.5" "jupysql==0.11.1" "duckdb-engine==0.17.0" pandas
gunzip -k data/aact_mini.duckdb.gz
jupyter notebook notebooks/
```

## 데이터 출처

[AACT (Aggregate Analysis of ClinicalTrials.gov)](https://aact.ctti-clinicaltrials.org/) — Clinical Trials Transformation Initiative
