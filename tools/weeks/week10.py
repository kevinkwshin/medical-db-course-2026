# -*- coding: utf-8 -*-
"""10주차 — 데이터 모델링과 정규화 (3NF까지) + OMOP CDM"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, versus, code)

WEEK = 10
TITLE = "모델링과 정규화"

slides = [
    cover(10, "데이터 모델링과 정규화<br>왜 처방 테이블엔 환자 이름이 없을까",
          ["ERD — 개체 · 속성 · 관계 그리기",
           "이상현상(Anomaly)을 임상 사고로 이해하기",
           "정규화 1NF → 2NF → 3NF",
           "표준 모델 맛보기: OMOP CDM"],
          question="왜 처방 테이블에는 환자 이름이 없을까?"),

    bullets("모델링 — 현실을 테이블로 옮기는 3단계",
            [("개념적 설계", "현실을 개체(Entity)·관계(Relationship)로 추상화 → ERD. \"환자가 내원하고, 내원마다 진단이 달린다\""),
             ("논리적 설계", "ERD를 테이블·PK·FK로 변환 — 우리가 6주간 쓴 미니 EMR 스키마가 이 산출물"),
             ("물리적 설계", "저장 방식·인덱스(조회 가속용 색인)·용량 계획 (DBA의 영역, 이 수업에선 개념만)")],
            note="<b>개체(entity)</b>: 데이터로 관리할 대상(환자·내원·진단) · "
                 "<b>관계(relationship)</b>: 개체 사이의 연결(1:1, 1:N, M:N) · "
                 "미니 EMR의 스키마는 이 3단계 중 논리적 설계의 산출물입니다."),

    html_slide("ERD 그리기 — 환자·내원·진단 관계 (IE 표기법)",
        """<div class="cols" style="grid-template-columns:1.2fr 1fr">
        <div style="text-align:center; padding-top:20px">
        <svg width="620" height="300" viewBox="0 0 620 300">
        <rect x="10" y="100" width="150" height="80" rx="8" fill="#eff6ff" stroke="#1e3a5f" stroke-width="2"/>
        <text x="85" y="130" text-anchor="middle" font-size="18" font-weight="700" fill="#1e3a5f">환자</text>
        <text x="85" y="158" text-anchor="middle" font-size="13" fill="#475569">patient_id (PK)</text>
        <rect x="235" y="100" width="150" height="80" rx="8" fill="#eff6ff" stroke="#1e3a5f" stroke-width="2"/>
        <text x="310" y="130" text-anchor="middle" font-size="18" font-weight="700" fill="#1e3a5f">내원</text>
        <text x="310" y="158" text-anchor="middle" font-size="13" fill="#475569">visit_id (PK)</text>
        <rect x="460" y="20" width="150" height="70" rx="8" fill="#f0fdfa" stroke="#0e7490" stroke-width="2"/>
        <text x="535" y="50" text-anchor="middle" font-size="17" font-weight="700" fill="#0e7490">진단</text>
        <rect x="460" y="190" width="150" height="70" rx="8" fill="#f0fdfa" stroke="#0e7490" stroke-width="2"/>
        <text x="535" y="220" text-anchor="middle" font-size="17" font-weight="700" fill="#0e7490">처방</text>
        <line x1="160" y1="140" x2="235" y2="140" stroke="#475569" stroke-width="2"/>
        <text x="172" y="130" font-size="13" fill="#475569">1</text><text x="215" y="130" font-size="13" fill="#475569">N</text>
        <line x1="385" y1="130" x2="460" y2="60" stroke="#475569" stroke-width="2"/>
        <line x1="385" y1="150" x2="460" y2="220" stroke="#475569" stroke-width="2"/>
        <text x="395" y="115" font-size="13" fill="#475569">1</text><text x="440" y="70" font-size="13" fill="#475569">N</text>
        <text x="395" y="175" font-size="13" fill="#475569">1</text><text x="440" y="215" font-size="13" fill="#475569">N</text>
        </svg></div>
        <div class="side"><h3>읽는 법</h3>
        <ul><li>사각형 = <b>개체</b>(테이블이 될 후보)</li>
        <li>선 + 1/N = <b>관계와 참여 수</b></li>
        <li>환자 1명 — 내원 N번 (1:N)</li>
        <li>M:N 관계는 <b>중간 테이블</b>로 풀어낸다 (예: 처방 = 내원과 약물의 M:N을 푼 테이블)</li></ul></div></div>""",
        tag="ERD"),

    html_slide("만약 전부 한 테이블이었다면 — '통합 진료기록' 가상 사례",
        """<table class="info small">
        <thead><tr><th>내원ID</th><th>환자이름</th><th>전화번호</th><th>진료과</th><th>진단명</th><th>약품명</th></tr></thead>
        <tbody>
        <tr><td>V001</td><td>김철수</td><td>010-1111-2222</td><td>내과</td><td>고혈압</td><td>암로디핀</td></tr>
        <tr><td>V002</td><td>김철수</td><td>010-1111-2222</td><td>내과</td><td>고혈압, 당뇨</td><td>암로디핀, 메트포르민</td></tr>
        <tr><td>V003</td><td>김철수</td><td><span class="danger">010-9999-8888</span></td><td>내과</td><td>고혈압</td><td>암로디핀</td></tr>
        <tr><td>V004</td><td>박영희</td><td>010-3333-4444</td><td>산부인과</td><td>정기검진</td><td>—</td></tr>
        </tbody></table>
        <div class="note">보이시나요? ① V002 한 칸에 진단 두 개(원자성 위반) ② 김철수의 전화번호가 <b>행마다 복사</b>되다가
        V003만 변경되어 어느 게 진짜인지 모름 ③ 박영희 행을 지우면 <b>산부인과가 있었다는 사실</b>도 함께 사라짐</div>""",
        tag="문제 상황"),

    table_slide("이상현상(Anomaly) — 임상 사고의 언어로",
        ["이상현상", "정의", "임상 시나리오"],
        [["<b>갱신 이상</b>", "중복된 값 중 일부만 수정되어 불일치 발생",
          "개명·전화번호 변경이 100개 행 중 97개만 반영 → 연락 두절, 검사 결과 통보 실패"],
         ["<b>삽입 이상</b>", "불필요한 정보 없이는 입력 자체가 불가",
          "아직 내원 안 한 신규 환자를 등록하려면 가짜 내원 기록이 필요"],
         ["<b>삭제 이상</b>", "행을 지우면 무관한 정보까지 소실",
          "마지막 환자 기록 삭제 시 그 진료과 정보 자체가 사라짐"]],
        note="원인은 하나 — <b>서로 다른 주제(환자 신상 / 내원 / 진단)가 한 테이블에 동거</b>하기 때문. "
             "해법이 정규화입니다."),

    html_slide("정규화 1NF → 2NF → 3NF (이 수업은 여기까지)",
        """<table class="info">
        <thead><tr><th style="width:14%">단계</th><th style="width:40%">규칙</th><th>위반 사례 → 교정</th></tr></thead>
        <tbody>
        <tr><td><b>1NF</b></td><td>한 칸엔 하나의 값(원자성)</td>
        <td>진단명 칸의 "고혈압, 당뇨" → 진단을 <b>행으로 분리</b> (그래서 diagnosis가 별도 테이블)</td></tr>
        <tr><td><b>2NF</b></td><td>복합키의 <b>일부</b>에만 매달린 속성 분리</td>
        <td>(내원ID, 약품코드) 키인 처방 테이블 안의 '약품명' — 약품코드에만 종속 → 약품 마스터로 분리</td></tr>
        <tr><td><b>3NF</b></td><td>키가 아닌 속성끼리의 종속 분리</td>
        <td>내원 테이블 안의 '담당의 전화번호' — 담당의ID에 종속 → staff 테이블로 분리</td></tr>
        </tbody></table>
        <div class="note">이 수업에서는 <b>3NF까지</b> 다룹니다 — 실무·연구 데이터 설계도 대개 이 수준을 사용합니다.
        BCNF·4NF·5NF는 이론 과목의 영역으로 남겨둡니다.</div>""",
        tag="정규화"),

    qsql("\"왜 처방 테이블에 환자 이름이 없을까?\" — 정규화의 답",
         "SELECT p.rx_id, p.drug_name,\n       v.patient_id, v.visit_date\nFROM prescription p, visit v\nWHERE p.visit_id = v.visit_id\nLIMIT 5;",
         max_rows=5,
         title="분리하되, 연결한다",
         tag="대표 질문",
         note="처방에는 환자 정보가 <b>없어도 됩니다</b> — visit_id만 있으면 환자까지 거슬러 올라갈 수 있으니까. "
              "환자 정보는 patient <b>한 곳에만</b> 존재 → 개명해도 한 행만 고치면 끝. "
              "같은 사실을 여러 곳에 적지 않는 것 — 정규화의 기본 원칙입니다."),

    versus("정규화 vs 반정규화 — 목적이 다르면 모양도 다르다",
           "정규화된 운영 DB (EMR)", [
               "중복 최소, 무결성 최우선",
               "입력·수정이 잦은 <b>진료 현장용</b>",
               "질문 하나에 JOIN 여러 번은 감수"],
           "반정규화된 분석 테이블 (연구용)", [
               "분석 편의를 위해 <b>의도적으로 중복 허용</b>",
               "환자·진단·검사를 한 판에 펼친 '플랫 테이블'",
               "CDW·연구 데이터셋이 보통 이 모양"],
           note="13주차에 여러분이 만들 코호트 테이블이 바로 반정규화된 분석 테이블입니다 — "
                "원본은 정규형으로 지키고, <b>분석본은 목적에 맞게 펼친다</b>."),

    html_slide("표준 모델 한 장 — OMOP CDM",
        """<div class="cols" style="grid-template-columns:1fr 1fr">
        <div><h3>OMOP CDM이란</h3>
        <ul><li>전 세계 병원이 각자의 EMR을 <b>같은 구조</b>로 변환하는 공통 데이터 모델</li>
        <li>person, visit_occurrence, condition_occurrence, drug_exposure, measurement …</li>
        <li>구조가 같으면 <b>분석 코드를 병원 간 공유</b> 가능 → 다기관 연구의 기반</li></ul></div>
        <div class="side"><h3>익숙하지 않나요?</h3>
        <ul><li>person ≈ patient</li>
        <li>visit_occurrence ≈ visit</li>
        <li>condition_occurrence ≈ diagnosis</li>
        <li>drug_exposure ≈ prescription</li>
        <li>measurement ≈ lab·vital</li></ul>
        <p style="margin-top:8px">미니 EMR은 OMOP의 <b>축소 모형</b>으로 설계되었습니다.</p></div></div>
        <div class="note">공식 명칭: <b>OMOP Common Data Model</b> — OHDSI(Observational Health Data
        Sciences and Informatics, 국제 관찰형 보건데이터 컨소시엄)의 표준. 국내 여러 대형병원도 변환에
        참여하고 있으며, 공개 문서(ohdsi.org)에서 전체 테이블 정의를 볼 수 있습니다.</div>""",
        tag="OMOP CDM"),

    html_slide("연습문제 — 손으로 그리는 과제",
        """<ul class="big">
        <li><b>Q1.</b> '수술(operation)' 기록을 미니 EMR에 추가한다면 — 개체·속성·관계를 ERD로 그려보라
          <span class="desc">어느 테이블과 1:N인가? 집도의는 어떻게 연결하나?</span></li>
        <li><b>Q2.</b> 위 가상 '통합 진료기록' 테이블을 3NF까지 분해해 보라 (테이블 이름과 PK·FK 명시)</li>
        <li><b>Q3.</b> 우리 prescription 테이블에서 (drug_code, drug_name)이 함께 있는 것은
          몇 정규형 관점에서 논쟁거리인가? 실무적으로 왜 남겨두었을까? <span class="desc">힌트: 2NF, 반정규화</span></li>
        </ul>""",
        tag="실습"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["개체(entity) / 관계(relationship)", "관리 대상(환자·내원) / 개체 간 연결(1:1 · 1:N · M:N)"],
         ["ERD", "개체·속성·관계를 그린 설계도 — Entity-Relationship Diagram"],
         ["이상현상(anomaly)", "중복 탓에 생기는 갱신·삽입·삭제 사고"],
         ["함수적 종속", "A가 정해지면 B가 유일하게 정해지는 관계 (A → B)"],
         ["정규화 / 정규형(NF)", "중복을 제거하는 분해 절차 / 그 단계 (1NF~3NF)"],
         ["반정규화", "분석 편의를 위해 의도적으로 중복을 되살리는 설계"],
         ["플랫 테이블", "여러 테이블을 한 판에 펼친 분석용 넓은 테이블"],
         ["OMOP CDM", "병원 간 공통 연구용 데이터 모델 (OHDSI 표준)"]],
        small=True, tag="용어"),

    closing(10,
            ["모델링 3단계: <b>개념적 설계(ERD) → 논리적 설계(테이블·키) → 물리적 설계(저장·인덱스)</b>",
             "이상현상 = 중복의 대가 — 갱신 누락, 유령 입력, 정보 소실",
             "정규화의 원칙: <b>같은 사실을 여러 곳에 적지 않는다</b>. 이 수업 범위는 3NF까지",
             "운영은 정규형, 분석은 반정규형 — <b>OMOP CDM</b>이 두 세계를 잇는 표준"],
            homework="Q1~Q3 (ERD는 손그림 사진 제출 가능)",
            next_week="JOIN — 테이블을 정식으로 연결한다 (\"당뇨 환자들의 HbA1c를 보려면?\")"),
]
