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

- 전체 빌드+검증: `cd tools && python3 build_all.py` (개별: `build_slides.py NN`, `build_docs.py`, `build_notebooks.py`)
- 데이터 변경 시: `mini_emr/generate_mini_emr.py` 수정·실행 → 새 데이터 태그(`data-v2` 등) push → `build_notebooks.py`의 `DATA_TAG` 갱신 → 전체 재빌드. 노트북은 태그 고정 주소에서 데이터를 받으므로 **학기 중 main이 바뀌어도 수강생 환경은 불변**
- 검증: `tools/run_checks.py` — 데이터 시나리오·재현성·노트북 전체 셀 실행·슬라이드 SQL을 확인하며, push 시 GitHub Actions에서도 자동 실행
- PDF 빌드에만 macOS + Brave Browser 필요 (검증·노트북 생성은 python3 + pandas면 충분)

명세서 3쪽(교수자용)은 학생 배포본에서 제외. 모든 환자 데이터는 가상입니다.
