# -*- coding: utf-8 -*-
"""14주차 — 의료데이터의 함정, 개인정보보호, RDB 밖의 데이터"""
from slide_lib import (cover, bullets, qsql, two_col, table_slide, html_slide,
                       closing, versus)

WEEK = 14
TITLE = "함정 · 보안 · RDB 밖의 세계"

slides = [
    cover(14, "이 결과를 믿어도 되나?<br>의료데이터의 함정과 책임",
          ["단위 불일치 · 측정시각 · 코드 버전 — 3대 함정",
           "결측이 유병률을 왜곡하는 방식",
           "개인정보보호법 · 가명처리 · IRB",
           "영상·파형·판독문 — RDB 밖의 데이터"],
          question="내가 뽑은 이 숫자를 논문에 실어도 되는가?"),

    qsql("함정 ① 단위 불일치 — 우리 혈당 데이터에 숨어 있던 것",
         "SELECT lab_id, test_name,\n       result_value, unit\nFROM lab\nWHERE test_name = 'Glucose'\nORDER BY result_value\nLIMIT 5;",
         max_rows=5,
         title="이 7.8은 저혈당인가?",
         tag="함정 1",
         note="7.8 mmol/L = 약 140 mg/dL — <b>단위가 다르면 같은 숫자가 정반대 의미</b>가 됩니다. "
              "단위 확인 없이 AVG를 돌리면 평균이 통째로 왜곡됩니다. "
              "실무 수칙: 수치 분석 전 <span class='mono'>GROUP BY unit</span>으로 단위 분포부터."),

    qsql("함정 ① 대응 — 단위 감사 쿼리",
         "SELECT test_name, unit,\n       COUNT(*) AS 건수,\n       MIN(result_value) AS 최소,\n       MAX(result_value) AS 최대\nFROM lab\nGROUP BY test_name, unit\nORDER BY test_name;",
         max_rows=8,
         title="분석 전 30초 감사(audit) 습관",
         note="Glucose에 단위가 <b>두 종류</b>인 것이 즉시 드러납니다. "
              "새 데이터셋을 받으면 ①단위 분포 ②MIN/MAX ③결측 수 — 3종 감사부터 실행합니다."),

    two_col("함정 ② 시각의 여러 얼굴 — 어느 시간이 '진짜'인가",
        """<h3>같은 검사 하나에도</h3>
        <ul><li><b>처방 시각</b> — 의사가 오더 낸 때</li>
        <li><b>채혈 시각</b> (collected_at) — 검체가 몸에서 나온 때</li>
        <li><b>결과보고 시각</b> — 수치가 확정된 때</li>
        <li>기록 시각 — 시스템에 입력된 때</li></ul>""",
        """<h3>왜 중요한가</h3>
        <ul><li>공복혈당 연구인데 <b>오후 채혈</b>이 섞이면? — 우리 데이터의 함정 검사(14시 채혈)처럼</li>
        <li>'입원 후 48시간 내 항생제'는 <b>어느 시각 기준</b>인가에 따라 결과가 달라진다</li>
        <li>논문 Methods에 시각 정의를 <b>명시</b>해야 재현 가능</li></ul>""",
        note="임상적으로 의미 있는 시각은 대부분 <b>검체 채취·측정 시각</b>입니다 — 기록 시각과 몇 시간씩 어긋날 수 있습니다.",
        tag="함정 2"),

    bullets("함정 ③ 코드는 살아 움직인다",
            [("코드 버전 변경", "KCD는 주기적으로 개정 — 같은 질환의 코드가 시기별로 다를 수 있다"),
             ("코딩 관행의 변화", "특정 진단의 '유행'은 질병 증가가 아니라 수가·지침 변화일 수 있다"),
             ("주진단 vs 부진단", "is_primary를 무시하고 세면 '입원 사유'와 '동반 상병'이 뒤섞인다"),
             ("매핑 테이블의 필요", "다기관 연구는 코드 → 표준 개념(OMOP) 매핑이 절반의 일")],
            tag="함정 3",
            note="진단코드 기반 연구의 고전적 경고: <b>\"코드가 늘어난 것인가, 병이 늘어난 것인가?\"</b>"),

    qsql("결측의 왜곡 — '검사받은 사람만'의 평균이라는 것",
         "SELECT\n  (SELECT COUNT(DISTINCT v.patient_id)\n   FROM visit v JOIN diagnosis d\n     ON d.visit_id = v.visit_id\n   WHERE d.kcd_code LIKE 'E11%') AS 당뇨환자수,\n  (SELECT COUNT(DISTINCT v.patient_id)\n   FROM visit v JOIN lab l\n     ON l.visit_id = v.visit_id\n   WHERE l.test_name = 'HbA1c'\n     AND v.patient_id IN (\n       SELECT v2.patient_id\n       FROM visit v2 JOIN diagnosis d2\n         ON d2.visit_id = v2.visit_id\n       WHERE d2.kcd_code LIKE 'E11%'))\n    AS 당뇨환자중검사자수;",
         title="분모가 다르면 결론이 다르다",
         note="당뇨 환자 8명 중 HbA1c 검사자는 6명 — '평균 HbA1c 7.6%'는 <b>검사받은 6명의</b> 평균입니다. "
              "검사를 안 받은 2명(P007·P013)이 조절 양호자인지 추적 탈락자인지에 따라 해석이 뒤집힙니다. "
              "11주차 LEFT JOIN이 이 분모를 지키는 도구였습니다."),

    html_slide("개인정보보호 — 연구자가 알아야 할 최소한",
        """<table class="info">
        <thead><tr><th style="width:22%">구분</th><th style="width:42%">내용</th><th>예</th></tr></thead>
        <tbody>
        <tr><td><b>익명정보</b></td><td>누구인지 복원 불가능 — 개보법 적용 제외</td><td>통계표, 완전 집계값</td></tr>
        <tr><td><b>가명정보</b></td><td>추가 정보 없이는 특정 불가하게 처리<br>과학적 연구 등 목적에 한해 활용 근거 마련(개보법 §28-2 — 요건·예외는 기관 지침 확인)</td><td>P001처럼 ID 치환, 생년월일 → 연령대</td></tr>
        <tr><td><b>민감정보</b></td><td>건강정보는 민감정보 — 원칙적 처리 제한, 별도 보호</td><td>진단명, 검사결과</td></tr>
        <tr><td><b>IRB</b></td><td>인간대상연구는 기관생명윤리위원회 심의 — 후향적 DB 연구도 예외 아님</td><td>심의면제 여부도 IRB가 판단</td></tr>
        </tbody></table>
        <div class="note">미니 EMR에 이름·주민번호가 <b>처음부터 없었던</b> 이유 — 이 데이터셋 자체가 가명처리의 모형입니다.
        표의 내용은 개인정보보호법·생명윤리법의 <b>2026-07 기준 교육용 요약</b>이며, 실제 연구 전에는 소속기관
        IRB·개인정보보호 담당자와 상의하세요.</div>""",
        tag="법·윤리"),

    bullets("접근 권한 — 최소 권한의 원칙 (DCL 한 장)",
            [("GRANT / REVOKE", "<span class='mono'>GRANT SELECT ON lab TO 연구자;</span> — 필요한 테이블에, 필요한 동작만"),
             ("역할 기반(RBAC)", "'연구자' 역할에 조회 권한만 — 개인이 아닌 역할에 권한을 부여"),
             ("감사 추적", "누가 언제 무엇을 조회했는지 로그 — 8주차 감사로그의 조회 버전"),
             ("연구자의 현실", "연구자용 CDW 계정은 대부분 SELECT 전용 — 최소 권한 원칙의 적용 결과")],
            note="유출 사고의 다수는 해킹이 아니라 <b>과도한 권한 + 부주의</b>에서 시작됩니다."),

    qsql("RDB 밖의 데이터 — 판독문은 왜 '검색'이 어려운가",
         "SELECT img_id, modality, body_part,\n       report\nFROM imaging\nWHERE report LIKE '%경색%';",
         max_rows=4,
         title="비정형 텍스트의 한계",
         tag="비정형",
         note="LIKE 검색은 되지만 — \"급성 경색 <b>소견 없음</b>\"도 '%경색%'에 걸립니다. "
              "부정 표현, 동의어, 오타… 텍스트의 의미는 LIKE로 잡히지 않습니다. "
              "그래서 판독문 연구는 NLP(자연어처리)의 영역으로 넘어갑니다."),

    html_slide("영상 · 파형 · 텍스트 — RDB 밖의 저장소",
        """<div class="cols" style="grid-template-columns:1fr 1fr">
        <div><h3>RDB에 안 넣는 이유</h3>
        <ul><li>MRI 한 검사 수백 MB — RDB 내부 저장(BLOB)도 가능하지만 운영·백업·전송 부담이 커진다</li>
        <li>행·열 구조가 무의미한 픽셀·파형 데이터</li>
        <li>그래서 <b>RDB에는 메타데이터</b>(우리 imaging 테이블), 실제 파일은 PACS·전용 저장소에 두는 구조가 일반적</li></ul></div>
        <div class="side"><h3>AI 학습 데이터셋의 구조</h3>
        <ul><li>영상 파일 (PACS) + <b>레이블</b> (RDB에서 추출한 진단·판독)</li>
        <li>\"폐렴 X-ray 분류\"의 <b>후보 레이블</b>은 imaging×diagnosis 조합에서 출발 — 시점 정렬·레이블 정의·품질관리는 별도 작업</li>
        <li>SQL은 이 중 <b>코호트·레이블 후보 추출</b>에 쓰이는 도구다</li></ul></div></div>
        <div class="note">NoSQL·데이터레이크는 이 비정형 세계의 저장 기술입니다 — 관계형이 끝이 아니라, 관계형이 <b>중심축</b>인 생태계.</div>""",
        tag="생태계"),

    html_slide("최종 점검 리스트 — \"이 결과를 믿어도 되나?\"",
        """<ul class="big">
        <li><b>단위</b> — 같은 검사에 단위가 하나인가? (GROUP BY unit)</li>
        <li><b>분모</b> — 이 평균·비율은 <b>누구의</b> 평균·비율인가? (결측·LEFT JOIN)</li>
        <li><b>시각</b> — 어느 시각 기준인가? (채혈 vs 기록)</li>
        <li><b>단위 수준</b> — 내원 수를 환자 수로 착각하지 않았나? (COUNT DISTINCT)</li>
        <li><b>코드</b> — 정의한 코드 패턴이 임상적으로 타당한가? (주진단 여부 포함)</li>
        <li><b>권한·윤리</b> — 이 데이터를 이 목적으로 써도 되는가? (가명처리·IRB)</li>
        </ul>
        <div class="note">프로젝트 발표(15주차)에서 이 6개 항목으로 서로의 결과를 교차 검증합니다 — 각 항목의 점검 쿼리는 이번 주 노트북에 있습니다.</div>""",
        tag="체크리스트"),

    table_slide("이번 주 용어 정리",
        ["용어", "뜻"],
        [["가명정보", "추가 정보 없이는 누구인지 특정 불가하게 처리한 정보 — 연구 목적 활용 근거(개보법 §28-2)"],
         ["익명정보", "복원 자체가 불가능한 정보 — 개인정보보호법 적용 제외"],
         ["민감정보", "건강정보 등 법이 특별히 보호하는 정보 — 원칙적 처리 제한"],
         ["IRB", "기관생명윤리위원회 — 인간대상연구(후향적 DB 연구 포함) 심의 기구"],
         ["RBAC", "역할 기반 접근 제어 — 개인이 아닌 역할(연구자 등)에 권한 부여"],
         ["감사 쿼리(audit query)", "분석 전 단위·범위·결측을 점검하는 사전 검증 쿼리"],
         ["NLP (자연어처리)", "판독문 등 텍스트의 의미를 다루는 기술 — LIKE 검색의 한계 너머"],
         ["DCL (Data Control Language)", "권한을 다루는 SQL — GRANT(부여)·REVOKE(회수)"],
         ["NoSQL", "테이블·SQL 구조를 따르지 않는 DB 총칭 — 문서형·키값형 등, 비정형 대용량에 강점"],
         ["데이터레이크(data lake)", "원시 데이터를 형식 그대로 쌓아두는 대용량 저장소 — 영상·로그·텍스트까지"]],
        small=True, tag="용어"),

    closing(14,
            ["3대 함정: <b>단위 · 시각 · 코드</b> — 분석 전 30초 감사 쿼리가 논문을 지킨다",
             "평균·비율 앞에서 항상: <b>\"분모가 누구인가?\"</b>",
             "건강정보는 민감정보 — <b>가명처리 + IRB + 최소 권한</b>이 연구의 입장권",
             "영상·텍스트는 RDB 밖에 있지만, <b>코호트·레이블 후보 추출에는 SQL</b>이 쓰인다"],
            homework="프로젝트 최종 점검 — 위 체크리스트 6항목을 자기 결과에 적용해 볼 것",
            next_week="15주차 조별 프로젝트 발표 — 코호트 정의서 · 추출 쿼리 · Table 1"),
]
