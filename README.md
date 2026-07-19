# 의료진을 위한 데이터베이스

15주 SQL 실습형 강의 자료. 학기 내내 미니 EMR(가상 환자 50명, 8개 테이블) 하나로 실습하며, 슬라이드의 모든 SQL 결과는 실제 데이터를 실행한 것입니다.

수강생은 [실습안내.md](실습안내.md)를 보면 됩니다.

## 구성

| 경로 | 내용 |
|---|---|
| `강의계획서.pdf` | 15주 시라버스 |
| `slides/` | 주차별 강의 슬라이드 + 통합본 |
| `mini_emr/` | 실습 DB(sqlite·CSV), ERD, 명세서, 생성 스크립트 |
| `code/` | Colab 노트북, SQL 스크립트 |
| `tools/` | 자료 빌드 스크립트 |

## 수정 방법

- 슬라이드: `tools/weeks/weekNN.py` 수정 → `cd tools && python3 build_slides.py NN`
- 데이터: `mini_emr/generate_mini_emr.py` 수정·실행 → 슬라이드 재빌드(결과 자동 갱신)
- 노트북·문서: `tools/build_notebooks.py`, `tools/build_docs.py`
- 빌드에는 macOS + Brave Browser 필요. 수정 후 `git push`

명세서 3쪽(교수자용)은 학생 배포본에서 제외. 모든 환자 데이터는 가상입니다.
