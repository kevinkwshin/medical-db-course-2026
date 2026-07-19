# -*- coding: utf-8 -*-
"""2주차 — 관계형 데이터베이스: 테이블, 키, 무결성, NULL"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, versus, code)

WEEK = 2
TITLE = "관계형 데이터베이스의 기본 구조"

slides = [
    cover(2, "관계형 데이터베이스의 기본 구조<br>테이블 · 키 · 무결성 · NULL",
          ["테이블의 해부학: 튜플, 속성, 도메인",
           "환자ID → 내원ID → 처방ID — 계층 구조와 1:N 관계",
           "기본키(PK)와 외래키(FK), 그리고 주민번호 이야기",
           "NULL — \"검사를 안 했다\"와 \"결과가 없다\"는 다르다"],
          question="주민등록번호를 환자 테이블의 기본키로 쓰면 왜 안 될까?"),

    html_slide("테이블의 구성 요소 — patient 테이블로 보기",
        """<div class="cols" style="grid-template-columns:1.15fr 1fr">
        <div><table class="info small">
        <thead><tr><th>patient_id</th><th>sex</th><th>birth_date</th><th>blood_type</th></tr></thead>
        <tbody><tr><td>P001</td><td>F</td><td>1947-04-12</td><td>B+</td></tr>
        <tr><td>P002</td><td>F</td><td>1942-01-04</td><td>O+</td></tr>
        <tr><td>P003</td><td>F</td><td>1942-12-27</td><td>A+</td></tr>
        <tr style="color:#94a3b8"><td colspan="4">… (총 50행)</td></tr></tbody></table></div>
        <div class="side">
        <p><span class="pill">속성 Attribute</span> 세로 열. 컬럼·필드라고도 부름 → 이 테이블은 4개 (<b>디그리</b> = 4)</p>
        <p><span class="pill">튜플 Tuple</span> 가로 행. 레코드라고도 부름 → 환자 한 명 = 한 행 (<b>카디널리티</b> = 50)</p>
        <p><span class="pill">도메인 Domain</span> 속성이 가질 수 있는 값의 범위 → sex는 {'M','F'}, blood_type은 8가지</p>
        </div></div>""",
        tag="용어"),

    bullets("관계형 테이블의 규칙 4가지 — 병원 기록으로 이해하기",
            [("튜플의 유일성", "이론적 관계 모델은 중복 튜플을 허용하지 않는다 — 실제 SQL 테이블에서는 PK·UNIQUE 제약으로 관리"),
             ("행 순서는 무의미", "먼저 등록한 환자가 '위'에 있을 이유가 없다 — 순서는 조회할 때 정한다(ORDER BY)"),
             ("속성의 원자성", "한 칸에는 하나의 값 — '고혈압, 당뇨'를 한 칸에 넣는 순간 문제가 시작된다(10주차)"),
             ("속성명의 고유성", "한 테이블 안에 같은 이름의 컬럼은 없다")],
            note="세 번째 규칙(원자성)을 어긴 실제 사례를 10주차 정규화에서 해부합니다."),

    html_slide("병원 데이터의 계층: 환자 → 내원 → 진료기록",
        """<div class="cols" style="grid-template-columns:1fr 1fr">
        <div>
        <p style="font-size:22px; line-height:2.1">
        <b>환자 1명</b> (P010)<br>
        &nbsp;&nbsp;└ <b>내원 여러 번</b> (V0031, V0032, V0033…)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ 내원마다 <b>진단 여러 개</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ 내원마다 <b>처방 여러 건</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└ 내원마다 <b>검사 여러 건</b></p></div>
        <div class="side"><h3>1 : N 관계</h3>
        <ul><li>환자 1 : 내원 N</li>
        <li>내원 1 : 진단 N / 처방 N / 검사 N / 활력징후 N</li>
        <li>그래서 테이블을 <b>분리</b>해서 저장하고, 필요할 때 <b>연결(JOIN, 11주차)</b>한다</li>
        <li>연결의 열쇠가 바로 <b>키(Key)</b></li></ul></div></div>""",
        tag="구조"),

    table_slide("키(Key)의 종류 — 미니 EMR에서 찾아보기",
        ["종류", "정의", "patient 테이블에서", "visit 테이블에서"],
        [["<b>후보키</b>", "행을 유일하게 구분하는 최소 속성(조합)", "patient_id", "visit_id"],
         ["<b>기본키(PK)</b>", "후보키 중 대표로 선택된 키<br>NULL 불가 · 중복 불가", "patient_id", "visit_id"],
         ["<b>외래키(FK)</b>", "다른 테이블의 PK를 참조하는 키", "—", "patient_id (→ patient)<br>attending_id (→ staff)"],
         ["<b>복합키</b>", "두 개 이상 속성을 합쳐야 유일해지는 키", "—", "vital: (visit_id, measured_at)"]],
        note="활력징후(vital)는 왜 복합키일까요? — 같은 내원에서 혈압을 <b>여러 번</b> 재기 때문에, "
             "'어느 내원의 몇 시 측정'까지 합쳐야 한 행이 특정됩니다 (이 교육용 데이터셋 기준 — "
             "실무에서는 동시각 재측정 등을 고려해 대리키를 두기도 합니다)."),

    two_col("주민등록번호를 PK로 쓰면 안 되는 이유",
        """<h3>기술적 이유</h3>
        <ul><li>바뀔 수 있다 — 정정·변경 사례 존재. PK가 바뀌면 <b>참조하는 모든 테이블</b>이 흔들린다</li>
        <li>없을 수 있다 — 신생아, 외국인 환자, 응급 무명 환자</li>
        <li>의미를 담고 있다 — 생년월일·성별이 노출되는 '스마트 키'는 위험하다</li></ul>""",
        """<h3>법적·윤리적 이유</h3>
        <ul><li>개인정보보호법상 <b>고유식별정보</b> — 원칙적 처리 제한, 암호화 의무</li>
        <li>유출 시 피해가 영구적 — 번호를 바꿔줄 수 없다</li>
        <li>연구용 데이터는 <b>가명처리</b>가 기본(14주차)</li></ul>""",
        note="그래서 병원은 업무상 의미가 없는 내부 식별자(등록번호, 우리 데이터의 P001…)를 PK로 씁니다 — "
             "<b>대리키(surrogate key)</b>. 법령 관련 내용은 개인정보보호법(2026-07 기준)의 교육용 요약이며, "
             "실제 적용은 기관 지침을 확인하세요.",
        tag="핵심"),

    qsql("외래키가 지켜주는 것: 존재하지 않는 내원(V9999)에 처방을 넣으면?",
         "INSERT INTO prescription\n  (rx_id, visit_id, drug_code,\n   drug_name, dose, duration_days)\nVALUES\n  ('R9999', 'V9999', 'MET500',\n   '메트포르민', '500mg', 30);",
         result=False,
         title="참조 무결성 — 잘못된 참조 입력의 차단",
         note="실행 결과: <span class='danger'>FOREIGN KEY constraint failed</span> — visit 테이블에 없는 "
              "V9999를 참조할 수 없습니다. <b>참조 무결성</b>: NULL이 아닌 외래키 값은 부모 테이블에 존재해야 한다. "
              "기록에 없는 내원으로 처방이 입력되는 일을 DBMS가 차단합니다."),

    versus("개체 무결성 vs 참조 무결성",
           "개체 무결성 (PK의 규칙)", [
               "기본키는 <b>NULL 불가</b>, <b>중복 불가</b>",
               "환자ID 없는 환자, 같은 ID의 두 환자는 존재할 수 없다",
               "각 행은 기본키로 식별 가능해야 한다"],
           "참조 무결성 (FK의 규칙)", [
               "NULL이 아닌 외래키 값은 <b>부모에 존재</b>해야 한다",
               "없는 환자에게 내원 기록을 달 수 없다",
               "참조값은 정의된 참조 규칙을 만족해야 한다"],
           note="<b>무결성(integrity)</b>: 데이터가 정해진 규칙을 위반한 상태로 존재하지 못하게 하는 성질. "
                "DBMS가 입력·수정 시점마다 자동 검사하며, 위반한 문장은 통째로 거부됩니다."),

    html_slide("NULL — 병원 데이터에서 가장 오해받는 값",
        """<table class="info">
        <thead><tr><th style="width:26%">기록</th><th style="width:30%">의미</th><th>NULL인가?</th></tr></thead>
        <tbody>
        <tr><td>Glucose = <b>0</b></td><td>혈당이 0 (사실상 불가능한 측정값)</td><td><span class="danger">아니오 — 0은 값이다</span></td></tr>
        <tr><td>Glucose = <b>NULL</b></td><td>결과가 없다 (용혈로 재검 필요 등)</td><td><span class="okay">예 — '모름/없음'</span></td></tr>
        <tr><td>Glucose 행 자체가 <b>없음</b></td><td>검사를 아예 하지 않았다</td><td>NULL도 아니고 행이 없음</td></tr>
        <tr><td>discharge_date = <b>NULL</b></td><td>외래·응급 귀가 (입원이 아니었음)</td><td>구조적으로 해당 없음</td></tr>
        </tbody></table>
        <div class="note"><b>"검사를 안 했다" ≠ "정상이었다"</b>. 연구에서 이 둘을 섞으면 유병률·이상률이 왜곡됩니다.
        NULL은 = 로 비교할 수 없고 <span class="mono">IS NULL</span>로만 물을 수 있습니다(4주차).</div>""",
        tag="NULL"),

    qsql("미니 EMR에 실제로 있는 NULL: 결과값이 비어 있는 검사를 찾아라",
         "SELECT lab_id, test_name,\n       result_value, unit,\n       collected_at\nFROM lab\nWHERE result_value IS NULL;",
         title="NULL 만나보기 — 우리 데이터의 실제 사례",
         note="L0093: 채혈은 했으나(collected_at 존재) 결과가 없습니다 — 검체 용혈로 재채혈이 필요했던 상황. "
              "이 행을 지워버리면 '검사를 시도했다'는 사실 자체가 사라집니다."),

    bullets("스키마 — 구조를 먼저 약속한다",
            [("스키마(Schema)", "테이블·컬럼·타입·제약조건의 설계도. 데이터보다 먼저 정의된다"),
             ("외부/개념/내부의 3계층", "사용자가 보는 화면 ↔ 병원 전체의 논리 구조 ↔ 디스크 저장 방식"),
             ("데이터 독립성", "저장 방식이 바뀌어도(디스크→클라우드) 쿼리는 그대로 — 계층 분리의 힘")],
            note="7주차에 여러분이 직접 스키마를 정의(CREATE TABLE)합니다. "
                 "그때 오늘 배운 PK·FK·NULL 규칙이 전부 문법으로 다시 등장합니다."),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["릴레이션(relation)", "테이블의 정식 명칭 — 행(튜플)과 열(속성)의 2차원 구조"],
         ["기본키(PK, Primary Key)", "행을 유일하게 특정하는 대표 키 — NULL·중복 불가"],
         ["외래키(FK, Foreign Key)", "다른 테이블의 PK를 참조하는 컬럼 — 테이블 간 연결고리"],
         ["복합키", "두 개 이상 컬럼을 합쳐야 유일해지는 키 (예: vital의 내원ID+측정시각)"],
         ["대리키(surrogate key)", "의미 없는 내부 번호로 만든 PK (P001…) — 주민번호 대신 쓰는 이유"],
         ["개체 무결성 / 참조 무결성", "PK의 규칙(신원 확실) / FK의 규칙(연결 끊김 없음)"],
         ["NULL", "값이 없음(모름) — 0도, 빈칸도 아니며 =로 비교 불가"],
         ["스키마(schema)", "테이블·컬럼·타입·제약조건의 설계도"]],
        small=True, tag="용어"),

    closing(2,
            ["테이블 = 튜플(행) × 속성(열), 병원 데이터는 <b>환자 1 : 내원 N</b>의 계층",
             "PK는 행의 신원(NULL·중복 불가), FK는 테이블 간 연결 — 두 무결성이 장부를 지킨다",
             "주민번호는 PK로 쓰지 않는다 — <b>바뀌고, 없을 수 있고, 위험하다</b> → 의미 없는 대리키",
             "NULL은 0도 빈칸도 아니다 — <b>\"안 했다\"와 \"정상\"을 구분</b>하는 것이 의료데이터 해석의 기본"],
            next_week="SQL 시작 — SELECT로 데이터 꺼내기 (\"우리 병원엔 어떤 진료과가 있나?\")"),
]
