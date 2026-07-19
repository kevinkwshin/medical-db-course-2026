# -*- coding: utf-8 -*-
"""7주차 — DDL: CREATE / ALTER / DROP"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, code)

WEEK = 7
TITLE = "DDL — 테이블 설계와 생성"

slides = [
    cover(7, "CREATE · ALTER · DROP<br>테이블 설계 = 연구 데이터셋 설계",
          ["데이터 타입 — 검사값은 왜 REAL인가",
           "CREATE TABLE과 제약조건 (NOT NULL · UNIQUE · CHECK · FK)",
           "ALTER · DROP — 구조 변경과 삭제",
           "실습: 내 연구용 코호트 테이블 설계"],
          question="내 연구의 증례기록지(CRF)를 테이블로 옮긴다면?"),

    table_slide("데이터 타입 — 값의 성질을 먼저 정한다",
        ["타입", "담는 것", "미니 EMR에서", "타입을 잘못 고르면"],
        [["INTEGER", "정수", "투약일수, 혈압, 맥박", "—"],
         ["REAL", "소수", "검사 결과값, 체온", "TEXT로 넣으면 <b>평균·비교가 문자 기준</b>으로 왜곡"],
         ["TEXT", "문자열", "진단명, 판독문, ID", "숫자를 TEXT로: '9' &gt; '10' 이 참이 되는 사고"],
         ["DATE / DATETIME", "날짜·시각", "내원일, 채혈시각", "형식 제각각이면 기간 필터 전멸 (14주차)"]],
        note="검사값을 REAL로 선언하는 순간 '결과값엔 숫자만'이라는 <b>규칙이 구조에 새겨집니다</b>. "
             "타입은 첫 번째 데이터 검증 장치입니다.",
        tag="타입"),

    code("CREATE TABLE — 미니 EMR의 실제 진단 테이블",
         """CREATE TABLE diagnosis (
  dx_id      TEXT PRIMARY KEY,              -- 진단ID
  visit_id   TEXT NOT NULL
             REFERENCES visit(visit_id),    -- 어느 내원의 진단인가
  kcd_code   TEXT NOT NULL,                 -- 상병코드는 필수
  dx_name    TEXT NOT NULL,
  is_primary INTEGER NOT NULL
             CHECK (is_primary IN (0,1))    -- 주진단 여부는 0/1만
);""",
         note="지금까지 조회해 온 diagnosis 테이블의 실제 정의문입니다. "
              "구조(컬럼·타입) + 규칙(제약조건)을 한 번에 선언합니다.",
         tag="DDL"),

    table_slide("제약조건 — 입력 사고를 구조로 막는다",
        ["제약조건", "규칙", "병원에서의 의미"],
        [["<b>PRIMARY KEY</b>", "NULL 불가 + 중복 불가", "모든 기록엔 유일한 신원"],
         ["<b>NOT NULL</b>", "빈 값 금지", "상병코드 없는 진단은 접수 자체가 안 되게"],
         ["<b>UNIQUE</b>", "중복 금지 (SQLite에서는 NULL 여러 개 허용 — DBMS마다 다름)", "같은 장비 시리얼번호 이중 등록 방지"],
         ["<b>CHECK</b>", "조건을 만족하는 값만", "성별은 M/F만, SpO2는 0~100만"],
         ["<b>FOREIGN KEY</b>", "NULL이 아니면 부모에 존재하는 값만", "없는 환자·없는 내원에 기록 못 달게 (2주차)"]],
        note="<b>제약조건(constraint)</b>: 컬럼·테이블에 선언하는 입력 규칙. 위반하면 "
             "'constraint failed' 에러와 함께 <b>문장 전체가 거부</b>되어 부분 입력이 남지 않습니다."),

    qsql("CHECK가 일하는 순간: SpO2에 250을 입력해 본다면?",
         "CREATE TABLE vital_demo (\n  visit_id TEXT,\n  spo2 INTEGER CHECK (spo2 BETWEEN 0 AND 100)\n);\nINSERT INTO vital_demo VALUES ('V0001', 250);",
         result=False,
         title="제약조건 위반 실험",
         note="실행 결과: <span class='danger'>CHECK constraint failed</span>. "
              "'산소포화도 250%'는 입력되는 순간 거부됩니다. 5주차에 MIN/MAX로 이상값을 '사후에' 찾았다면, "
              "CHECK는 <b>사전에</b> 차단합니다 — 둘 다 필요합니다."),

    code("ALTER TABLE — 운영 중인 구조 고치기",
         """-- 흡연 여부 컬럼 추가 (연구 변수 추가)
ALTER TABLE patient ADD COLUMN smoking TEXT;

-- 컬럼 이름 변경
ALTER TABLE patient RENAME COLUMN smoking TO smoking_status;

-- 테이블 삭제 (구조와 데이터 모두 소멸!)
DROP TABLE vital_demo;""",
         note="DROP은 되돌릴 수 없습니다. 참조하는 자식 테이블이 있으면 삭제가 거부되는 것도 "
              "참조 무결성의 보호막입니다. <b>운영 DB에서 DROP은 결재 문서와 함께 움직이는 명령</b>입니다.",
         tag="DDL"),

    two_col("테이블 설계 = 연구 설계다",
        """<h3>증례기록지(CRF)의 항목이…</h3>
        <ul><li>대상자번호 → <span class="mono">subject_id TEXT PRIMARY KEY</span></li>
        <li>등록일 → <span class="mono">enroll_date DATE NOT NULL</span></li>
        <li>흡연 여부 → <span class="mono">smoking TEXT CHECK(...)</span></li>
        <li>기저 HbA1c → <span class="mono">baseline_a1c REAL</span></li></ul>""",
        """<h3>설계 때 답해야 할 질문</h3>
        <ul><li>이 값이 <b>없어도 되는가?</b> → NOT NULL 여부</li>
        <li>허용되는 값의 <b>범위·목록</b>은? → CHECK</li>
        <li>무엇으로 행을 <b>특정</b>하나? → PK</li>
        <li>기존 데이터와 <b>어떻게 연결</b>되나? → FK</li></ul>""",
        note="<b>CRF(Case Report Form, 증례기록지)</b>: 연구 대상자별 수집 항목을 정의한 표준 양식. "
             "CRF의 각 항목이 컬럼으로, 허용값 규칙이 제약조건으로 번역됩니다.",
        tag="연구 설계"),

    code("실습 — 내 연구용 코호트 테이블을 직접 설계한다",
         """CREATE TABLE my_cohort (
  subject_id   TEXT PRIMARY KEY,
  patient_id   TEXT NOT NULL
               REFERENCES patient(patient_id),
  index_date   DATE NOT NULL,        -- 코호트 진입일
  age_at_index INTEGER
               CHECK (age_at_index BETWEEN 0 AND 120),
  sex          TEXT NOT NULL CHECK (sex IN ('M','F')),
  dm_flag      INTEGER NOT NULL DEFAULT 0
               CHECK (dm_flag IN (0,1))  -- 당뇨 동반 여부
);""",
         note="13주차 코호트 실습에서 이 테이블에 실제 데이터를 채워 넣습니다. "
              "오늘의 과제: 각자 관심 주제로 컬럼 6개 이상의 코호트 테이블을 설계해 오세요 — "
              "<b>각 제약조건마다 '왜'를 한 줄씩</b> 달아서.",
         tag="실습"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["DDL (Data Definition Language)", "구조를 정의하는 SQL — CREATE·ALTER·DROP"],
         ["데이터 타입", "컬럼이 담을 값의 종류 — INTEGER·REAL·TEXT·DATE"],
         ["제약조건(constraint)", "입력 규칙 — 위반한 문장은 통째로 거부됨"],
         ["CHECK", "허용 값의 조건을 직접 지정 (예: spo2 BETWEEN 0 AND 100)"],
         ["DEFAULT", "값을 생략했을 때 자동으로 들어가는 기본값"],
         ["REFERENCES", "외래키 선언 — 참조할 부모 테이블(컬럼)을 지정"],
         ["CRF(증례기록지)", "연구 수집 항목을 정의한 표준 양식 — 스키마 설계의 원본"]],
        small=True, tag="용어"),

    closing(7,
            ["타입 선택이 첫 번째 검증: <b>검사값은 REAL, 날짜는 통일된 DATE</b>",
             "제약조건 5총사(PK · NOT NULL · UNIQUE · CHECK · FK) = <b>입력 사고의 사전 차단</b>",
             "DROP은 비가역 — 참조 무결성이 실수를 한 번은 막아준다",
             "<b>CRF → 스키마</b> 번역 능력이 곧 연구 데이터 품질"],
            homework="'내 연구 코호트 테이블' CREATE TABLE 문 제출 (제약조건 사유 주석 포함)",
            next_week="INSERT·UPDATE·DELETE — 그리고 의무기록은 왜 진짜로 지우지 않는가"),
]
