# -*- coding: utf-8 -*-
"""1주차 — 데이터베이스 개론: 의료데이터의 세계"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, img_slide,
                       html_slide, closing, versus, code)

WEEK = 1
TITLE = "데이터베이스 개론 — 의료데이터의 세계"

slides = [
    cover(1, "데이터베이스 개론<br>의료데이터의 세계",
          ["데이터와 정보 — 혈압 수치는 언제 '진단'이 되는가",
           "정형 · 반정형 · 비정형 의료데이터",
           "병원 정보시스템 지도: EMR · LIS · PACS · CDW",
           "한 학기 동안 함께할 데이터셋: 미니 EMR"],
          question="혈압 120/80은 데이터인가, 정보인가?"),

    html_slide("이 수업이 끝나면 할 수 있는 것",
        """<ul class="big">
        <li><b>임상 질문을 SQL로 번역한다</b>
          <span class="desc">"당뇨 환자 중 HbA1c 검사를 안 받은 사람은?" → 컴퓨터가 알아듣는 문장으로</span></li>
        <li><b>연구용 코호트를 직접 추출한다</b>
          <span class="desc">포함·제외 기준을 SQL로 구현하고, 기초 특성표(Table 1)까지 산출한다</span></li>
        <li><b>의료데이터의 함정을 알아본다</b>
          <span class="desc">단위 불일치, 결측, 코드 버전 — "이 결과를 믿어도 되나?"에 답하기</span></li>
        </ul>
        <table class="info small" style="margin-top:auto">
        <thead><tr><th style="width:22%">용어</th><th>뜻</th></tr></thead>
        <tbody>
        <tr><td><b>SQL</b></td><td>Structured Query Language — 관계형 데이터베이스에 질문을 던지는 국제 표준 언어</td></tr>
        <tr><td><b>쿼리(query)</b></td><td>데이터베이스에 보내는 질의 한 건. "쿼리를 짠다" = 질문을 SQL 문장으로 쓴다</td></tr>
        <tr><td><b>코호트(cohort)</b></td><td>공통 기준(진단·기간 등)으로 정의한 연구 대상 환자 집단</td></tr>
        <tr><td><b>Table 1</b></td><td>논문의 첫 표 — 연구대상자의 기저 특성(성별·나이·동반질환) 요약</td></tr>
        </tbody></table>"""),

    versus("데이터 vs 정보 — 같은 숫자, 다른 무게",
           "데이터 (Data)", [
               "관찰·측정·기록된 값",
               "<span class='mono'>SBP 128, DBP 84</span> — 혈압계가 찍은 숫자",
               "해석 기준은 별도로 적용된다",
               "예: 검사 결과값, 내원 기록, 투약 기록"],
           "정보 (Information)", [
               "목적에 따라 데이터를 <b>가공·해석</b>한 것",
               "\"고혈압전단계\"(대한고혈압학회 2022 기준) — 기준이 붙은 판단",
               "의사결정의 근거가 된다",
               "예: 진료과별 평균 재원일수, 당화혈색소 조절률"],
           note="이 수업에서 사용하는 실용적 구분입니다. 같은 128/84라도 <b>어떤 분류 기준을 적용하느냐</b>에 "
                "따라 범주가 달라집니다 — 기준과 맥락이 붙어야 데이터가 정보가 됩니다."),

    html_slide("데이터 → 정보 → 의사결정: 병원에서의 실제 흐름",
        """<table class="info">
        <thead><tr><th style="width:18%">단계</th><th>예시</th><th style="width:34%">누가/무엇이 하나</th></tr></thead>
        <tbody>
        <tr><td><b>데이터</b></td><td>P010 환자의 HbA1c = 9.5%</td><td>검사장비 → LIS 저장</td></tr>
        <tr><td><b>정보</b></td><td>"최근 3회 연속 목표치 초과" (목표치 7.0%는 예시 — 실제 목표는 환자별로 다름)</td><td>SQL 질의로 추세 집계</td></tr>
        <tr><td><b>지식</b></td><td>"추가 임상 평가가 필요한 환자군에 해당"</td><td>임상 지식 + 가이드라인</td></tr>
        <tr><td><b>결정</b></td><td>치료 조정 여부 판단 — 다른 임상 정보와 함께 의료진이 결정</td><td>의료진</td></tr>
        </tbody></table>
        <div class="note">이 수업에서 배우는 SQL은 <b>2단계(데이터→정보)</b>를 담당합니다.
        LIS(검사정보시스템) 등 각 시스템 용어는 다음 슬라이드에서 정리합니다.</div>"""),

    table_slide("의료데이터의 세 가지 유형",
        ["구분", "특징", "병원에서의 예", "저장되는 곳"],
        [["<b>정형</b><br>(Structured)", "행·열 구조, 값의 형식이 고정",
          "진단코드, 처방, 검사수치, 활력징후", "관계형 DB (이 수업의 주인공)"],
         ["<b>반정형</b><br>(Semi-structured)", "구조를 설명하는 태그 포함",
          "HL7·FHIR(의료정보 교환 표준 규격)의 JSON·XML 메시지", "문서형 DB, 파일 + 메타데이터"],
         ["<b>비정형</b><br>(Unstructured)", "고정된 구조 없음",
          "경과기록 자유서술, 영상 판독문, X-ray·MRI 영상, 심전도 파형", "PACS, 전용 저장소"]],
        note="영상·파형·자유서술 기록처럼 관계형 테이블만으로 다루기 어려운 데이터가 병원에는 많습니다 — "
             "14주차에 다시 다룹니다."),

    html_slide("병원 정보시스템 지도 — 데이터는 왜 흩어져 있나",
        """<div class="cols" style="grid-template-columns:1.2fr 1fr">
        <div><table class="info small">
        <thead><tr><th>시스템</th><th>담는 것</th></tr></thead><tbody>
        <tr><td><b>EMR</b> (전자의무기록)</td><td>진료기록, 진단, 경과기록</td></tr>
        <tr><td><b>OCS</b> (처방전달)</td><td>처방·오더의 발행과 전달</td></tr>
        <tr><td><b>LIS</b> (검사정보)</td><td>검체검사 결과, 정도관리</td></tr>
        <tr><td><b>PACS</b> (영상저장전송)</td><td>X-ray·CT·MRI 이미지와 판독문</td></tr>
        <tr><td><b>CDW</b> (임상데이터웨어하우스)</td><td>위 시스템들을 연구·분석용으로 통합</td></tr>
        </tbody></table></div>
        <div class="side"><h3>흩어져 있는 이유</h3>
        <ul><li>시스템마다 <b>목적이 다르다</b> — 진료용 vs 검사용 vs 영상용</li>
        <li>도입 시기·업체가 달라 <b>구조도 다르다</b></li>
        <li>많은 기관이 연구·분석용으로 <b>CDW나 별도 데이터마트</b>에 통합한다</li>
        <li>이 수업의 미니 EMR은 이런 <b>분석용 통합 데이터셋</b>처럼 사용합니다</li></ul></div></div>"""),

    two_col("파일(엑셀)로 환자 명단을 관리하면 생기는 일",
        """<h3>연구 데이터 관리에서 흔히 발생하는 일</h3>
        <ul>
        <li><span class="mono">환자명단_최종.xlsx</span></li>
        <li><span class="mono">환자명단_최종_수정.xlsx</span></li>
        <li><span class="mono">환자명단_최종_수정_진짜최종.xlsx</span></li>
        <li>세 파일의 환자 수가 <span class="danger">전부 다르다</span></li>
        <li>전화번호를 고쳤는데 <b>한 파일만</b> 고쳐졌다</li></ul>""",
        """<h3>이것이 '파일 시스템의 한계'</h3>
        <ul>
        <li><b>중복</b> — 같은 데이터가 여러 곳에 복사됨</li>
        <li><b>불일치</b> — 하나만 수정되어 버전이 갈라짐</li>
        <li><b>종속</b> — 파일 구조가 바뀌면 쓰던 수식·코드가 깨짐</li>
        <li><b>동시성</b> — 두 사람이 같이 열면 한 명의 수정이 사라짐</li></ul>""",
        note="DBMS(데이터베이스 관리 시스템)는 중복·불일치·동시 접근 문제를 <b>통제하는 기능을 제공</b>합니다 — "
             "데이터를 한 곳에 두고, 여러 사람이 동시에, 규칙을 지키며 쓰도록."),

    bullets("DBMS가 해주는 일 — 병원 버전",
            [("구조화된 저장", "환자·내원·처방을 정해진 틀(테이블)에 — 적절한 설계와 결합하면 중복 최소화"),
             ("규칙(제약조건) 강제", "존재하지 않는 환자ID로는 처방을 입력할 수 없게"),
             ("동시 접근 제어", "외래 3진료실과 병동이 동시에 기록해도 안전하게"),
             ("보안과 이력", "권한 없는 접근 차단, 누가 언제 봤는지 기록")],
            tag="DBMS",
            note="관계형 DBMS는 1970년 제안(E. F. Codd) 이후 표준으로 자리잡았고, "
                 "병원의 핵심 임상·원무 데이터는 여전히 <b>관계형 DB</b> 중심입니다."),

    html_slide("미니 EMR — 핵심 구조 먼저",
        """<div style="flex:1; display:flex; align-items:center; justify-content:center">
        <svg width="1050" height="470" viewBox="0 0 1050 470">
        <rect x="20" y="170" width="230" height="110" rx="12" fill="#eff6ff" stroke="#1e3a5f" stroke-width="2.5"/>
        <text x="135" y="218" text-anchor="middle" font-size="30" font-weight="800" fill="#1e3a5f">환자</text>
        <text x="135" y="252" text-anchor="middle" font-size="17" fill="#475569">patient · 50명</text>
        <rect x="410" y="170" width="230" height="110" rx="12" fill="#eff6ff" stroke="#1e3a5f" stroke-width="2.5"/>
        <text x="525" y="218" text-anchor="middle" font-size="30" font-weight="800" fill="#1e3a5f">내원</text>
        <text x="525" y="252" text-anchor="middle" font-size="17" fill="#475569">visit · 100건</text>
        <line x1="250" y1="225" x2="410" y2="225" stroke="#475569" stroke-width="2.5"/>
        <text x="268" y="212" font-size="20" font-weight="700" fill="#475569">1</text>
        <text x="382" y="212" font-size="20" font-weight="700" fill="#475569">N</text>
        <g font-size="22" font-weight="700" fill="#0e7490">
        <rect x="810" y="20" width="220" height="70" rx="10" fill="#f0fdfa" stroke="#0e7490" stroke-width="2"/>
        <text x="920" y="63" text-anchor="middle">진단 diagnosis</text>
        <rect x="810" y="115" width="220" height="70" rx="10" fill="#f0fdfa" stroke="#0e7490" stroke-width="2"/>
        <text x="920" y="158" text-anchor="middle">처방 prescription</text>
        <rect x="810" y="210" width="220" height="70" rx="10" fill="#f0fdfa" stroke="#0e7490" stroke-width="2"/>
        <text x="920" y="253" text-anchor="middle">검사 lab</text>
        <rect x="810" y="305" width="220" height="70" rx="10" fill="#f0fdfa" stroke="#0e7490" stroke-width="2"/>
        <text x="920" y="348" text-anchor="middle">활력징후 vital</text>
        <rect x="810" y="400" width="220" height="70" rx="10" fill="#f0fdfa" stroke="#0e7490" stroke-width="2"/>
        <text x="920" y="443" text-anchor="middle">영상 imaging</text>
        </g>
        <g stroke="#94a3b8" stroke-width="2" fill="none">
        <path d="M640,210 C730,180 730,70 810,55"/>
        <path d="M640,220 C730,205 730,150 810,150"/>
        <path d="M640,230 C730,235 730,245 810,245"/>
        <path d="M640,245 C730,280 730,335 810,340"/>
        <path d="M640,255 C730,320 730,430 810,435"/>
        </g>
        <text x="655" y="200" font-size="19" font-weight="700" fill="#475569">1</text>
        <text x="785" y="250" font-size="19" font-weight="700" fill="#475569">N</text>
        </svg></div>
        <div class="note">구조는 이 한 문장이 전부입니다: <b>환자 1명이 여러 번 내원하고, 내원마다 진료기록(진단·처방·검사·활력징후·영상)이 달린다.</b>
        모든 진료기록은 내원ID로, 모든 내원은 환자ID로 연결됩니다.</div>""",
        tag="미니 EMR"),

    img_slide("미니 EMR — 전체 ERD (컬럼 수준)", "../mini_emr/ERD.png",
              note="컬럼 수준 세부는 배포된 <b>데이터셋 명세서(A4)</b>에 있습니다 — 외울 필요 없이 "
                   "매주 옆에 두고 참조하면 됩니다. <b>모든 데이터는 가상입니다.</b>",
              tag="미니 EMR"),

    table_slide("미니 EMR 8개 테이블 요약",
        ["테이블", "내용", "행 수", "주요 컬럼"],
        [["<span class='mono'>patient</span> 환자", "성별·생년월일·혈액형 (이름 없음 — 가명화)", "50",
          "patient_id"],
         ["<span class='mono'>visit</span> 내원", "내원일·진료과·유형(외래/입원/응급)·퇴원일", "100", "visit_id, patient_id"],
         ["<span class='mono'>diagnosis</span> 진단", "KCD코드·진단명·주진단여부", "140", "visit_id, kcd_code"],
         ["<span class='mono'>prescription</span> 처방", "약품명·용량·투약일수", "154", "visit_id, drug_code"],
         ["<span class='mono'>lab</span> 검사", "검사명·결과값·단위·정상범위·채혈시각", "93", "visit_id, test_name"],
         ["<span class='mono'>vital</span> 활력징후", "혈압·맥박·체온·SpO2·측정시각", "149", "visit_id, measured_at"],
         ["<span class='mono'>staff</span> 의료진", "직종·진료과", "21", "staff_id"],
         ["<span class='mono'>imaging</span> 영상", "촬영종류·부위·판독문", "21", "visit_id, modality"]],
        small=True),

    qsql("미리보기: 우리 데이터셋의 환자 5명을 꺼내 봅시다",
         "SELECT *\nFROM patient\nLIMIT 5;",
         title="오늘의 첫 SQL — 실행해보기",
         tag="실습 미리보기",
         max_rows=5,
         note="<span class='mono'>SELECT</span>(무엇을 꺼낼지) · <span class='mono'>FROM</span>(어느 테이블에서) · "
              "<span class='mono'>LIMIT</span>(몇 행까지) — 정확한 문법은 3주차부터 다룹니다. "
              "실습 환경은 브라우저(Colab)에서 링크 클릭만으로 열립니다."),

    bullets("실습 환경 — 설치 0",
            [("Google Colab 노트북", "매주 링크 제공 → 클릭 → 바로 실행. 노트북·태블릿 모두 가능"),
             ("SQLite", "서버 없이 파일 하나로 동작하는 경량 관계형 DBMS — 기본 조회 문법은 다른 관계형 DBMS와 유사하나 세부 문법은 제품마다 다름"),
             ("mini_emr.sqlite 다운로드", "개인 PC에서는 DB Browser for SQLite(무료)로도 열람 가능")],
            note="준비물: 구글 계정 하나면 충분합니다. 다음 주부터 매 수업 노트북을 함께 엽니다."),

    closing(1,
            ["데이터는 측정값, 정보는 <b>기준·맥락이 붙은 판단</b> — SQL은 그 변환 도구",
             "병원 데이터는 EMR·LIS·PACS 등에 <b>흩어져</b> 있고, 연구는 CDW에서 시작된다",
             "파일 관리의 중복·불일치 문제를 해결하는 것이 <b>DBMS</b>",
             "실습은 <b>미니 EMR 하나로</b> 15주 전체 진행 — 8개 테이블 구조는 명세서(A4 배포물) 참조"],
            next_week="관계형 데이터베이스의 기본 구조 — 테이블과 키(Key), 그리고 NULL의 의미"),
]
