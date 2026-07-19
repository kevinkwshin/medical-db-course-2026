# 의료진을 위한 데이터베이스 — 강의 패키지

> **수강생이신가요?** → [실습안내.md](실습안내.md)를 보세요. 이 문서는 교수자·관리용입니다.

15주 SQL 실습형 강의의 전체 자료 세트입니다. 학기 내내 **미니 EMR**(가상 환자 50명, 8개 테이블) 하나만 사용하며, 모든 슬라이드의 SQL 예제는 실제 데이터에 실행한 결과가 그대로 실려 있습니다.

## 구성

```
강의계획서.pdf              15주 시라버스 (A4 1장)
slides/
  week01.pdf ~ week14.pdf   주차별 강의 슬라이드 (16:9, 총 144장, 9·15주차 제외)
  전체_통합본.pdf            13개 덱 합본
mini_emr/
  mini_emr.sqlite           실습 데이터베이스
  csv/                      테이블별 CSV (8개)
  ERD.png                   관계도
  데이터셋_명세서.pdf         학생 배포용 명세 2쪽 + 교수자용 노트 1쪽
  generate_mini_emr.py      데이터 생성 스크립트 (seed 고정 — 재실행해도 동일)
code/
  weekNN_*.ipynb            주차별 Colab 실습 노트북 (예제 + 연습문제 + 정답)
  sql/weekNN.sql            같은 내용의 순수 SQL 스크립트
tools/                      슬라이드·문서·노트북 빌드 시스템 (수정 후 재생성용)
```

## 배포

- 저장소: `github.com/kevinkwshin/medical-db-course-2026` — 노트북의 `DB_URL`과 `실습안내.md`의 Colab 링크가 이 주소로 설정되어 있음
- 학생에게는 `실습안내.md` 링크 하나만 공지하면 됨
- `데이터셋_명세서.pdf`의 3쪽(교수자용 노트)은 학생 배포본에서 제외
- `데이터베이스개론특강 복사본.pdf`(외부 저작물)는 저장소에 올리지 않음 (.gitignore 처리됨)

## 자료 수정 방법

- 슬라이드 내용: `tools/weeks/weekNN.py` 편집 → `cd tools && python3 build_slides.py NN`
- 데이터 시나리오: `mini_emr/generate_mini_emr.py` 편집 후 재실행 → 슬라이드 전체 재빌드 (결과 테이블이 자동 갱신됨)
- 명세서·계획서: `tools/build_docs.py` → `python3 build_docs.py`
- 빌드에는 macOS + Brave Browser(HTML→PDF 변환용)가 필요합니다.

모든 환자 데이터는 인공 생성된 가상 정보입니다.
