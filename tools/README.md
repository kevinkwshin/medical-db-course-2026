# tools — 강의자료 · 실습 · 과제 생성 도구

## 슬라이드

| 파일 | 역할 |
|---|---|
| `deckgen.py` | 1~3주차 양식을 재현하는 슬라이드 생성기 (표지 · 개념 · SQL 예제 · 표 · 확인 문제 · 정리 · 도식 부품) |
| `wk_common.py` | 주차 공용 도구. `Ctx`(기존 슬라이드 제목 수정 등), 표 슬라이드, 학습목표, 좌우 비교, 섹션 구분, 중간 정리, 용어표 |
| `w4.py` … `w15.py` | 주차별 내용. 각 모듈은 `SPAN`(원본에서 대체할 구간)과 `build(c)` 를 가짐 |
| `w4_parts.py` | 4주차 전용 도식 (미니 ERD · 인덱스 비교 · 사상 · 데이터 사전) |
| `build_deck.py` | 원본에서 시작해 준비된 주차만 교체해 `..._v2.pptx` 생성 |
| `qa_render.py` | PowerPoint로 PDF 내보내기 → PNG → 9장씩 묶은 확인용 시트 (`render/`) |
| `pdf2png.js` | macOS 내장 JXA로 PDF → PNG (LibreOffice 불필요) |
| `office39/` | pptx 구조 검증 (Python 3.9용으로 수정) |
| `qa_scan.py` | 화면 밖 도형 · 글자 상자 겹침 · 금지 표현 자동 점검 (4주차 이후만) |
| `qa_sql.py` | 슬라이드 안의 SQL 을 실습 DB 에 EXPLAIN 으로 걸어 문법 · 컬럼 오류 확인 |

```bash
python3 tools/build_deck.py                 # 준비된 주차 전부 다시 빌드
python3 tools/build_deck.py 5 6             # 특정 주차만
python3 tools/office39/validate.py "데이터베이스관리_수정본_개편_최종_v2.pptx" --original "데이터베이스관리_수정본_개편_최종.pptx"
python3 tools/qa_render.py "데이터베이스관리_수정본_개편_최종_v2.pptx" w5 85 119      # 5주차 렌더링
python3 tools/qa_scan.py                    # 도형 위치 · 겹침 · 표현 점검
python3 tools/qa_sql.py                     # 슬라이드 SQL 문법 점검
```

`qa_sql.py` 는 조회문만 검사합니다. 병원 예시용 가상 테이블(환자 · 검사 · 표)만 "없는 테이블" 로 보고되며 정상입니다.

주차별 슬라이드 수는 `build_deck.py` 실행 결과에 표시됩니다 (현재 총 397장, 4~15주차 345장).

새 주차를 고치려면 해당 `wN.py` 만 수정한 뒤 `build_deck.py` 를 다시 실행하면 됩니다.
**주의**: `build_deck.py 8` 처럼 주차를 지정하면 그 주차만 교체된 덱이 만들어집니다. 배포용 파일을 만들 때는 인자 없이 실행하세요.
원본 `데이터베이스관리_수정본_개편_최종.pptx` 는 건드리지 않습니다.

## 데이터

| 파일 | 역할 |
|---|---|
| `build_aact_mini.py` | AACT → `data/aact_mini.duckdb` + 데이터 사전. `--snapshot data/<Flat Text Files zip>` 또는 `data/.aact_env` 계정 접속 |

```bash
python3 tools/build_aact_mini.py --snapshot data/<받은파일>.zip
```

필요한 14개 테이블만 풀고 빌드 후 자동 삭제합니다. 결과는 약 114MB, 임상시험 37,509건.

## 실습 · 과제 노트북

| 파일 | 역할 |
|---|---|
| `nbgen.py` | 노트북 생성기. 준비 셀(데이터 다운로드 → jupysql → DuckDB), `%%sql` 셀, `check("Q1", _)`, nbclient 실행 검증 |
| `nb_assign.py` | 과제 공용: 질환 목록 15개와 학번 기반 배정 준비 셀 |
| `build_nb_w7.py` · `build_nb_w8.py` | 7 · 8주차 실습 노트북 |
| `build_nb_a1.py` · `build_nb_a2.py` | 과제 1 · 과제 2 |
| `number_cells.py` | 수업용 셀 번호 `[1번]`, `[2번]` … 를 코드 셀에 붙임. **모든 빌드가 끝난 뒤 마지막에 실행** |

각 빌드는 **정답본을 실제로 실행해 모든 `check` 가 ✅ 인지 확인**한 뒤에만 저장합니다.
학생용은 출력이 지워진 상태, 교수자용(`notebooks/instructor/`)은 실행 결과가 포함된 상태입니다.

**데이터 배포**: 노트북은 GitHub 저장소의 `data/aact_mini.duckdb.gz` 를 내려받아 압축을 풉니다.
DB를 다시 만들었다면 `gzip -9 -k -f data/aact_mini.duckdb` 로 압축본을 갱신해 커밋하세요.

## 참고

PowerPoint 내보내기는 `~/Library/Containers/com.microsoft.Powerpoint/Data/tmp` 에
`POSIX file` 객체로 저장해야 파일이 생성됩니다 (다른 경로는 조용히 실패).
