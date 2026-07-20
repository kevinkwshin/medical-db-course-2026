# -*- coding: utf-8 -*-
"""A4 문서 생성: 미니 EMR 데이터셋 명세서 + 강의계획서 (HTML → Brave → PDF)"""
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

CSS = """
* { margin:0; box-sizing:border-box; }
@page { size:A4; margin:0; }
body { font-family:"Apple SD Gothic Neo","AppleGothic",sans-serif; color:#0f172a; }
.page { width:210mm; min-height:297mm; padding:16mm 17mm; page-break-after:always; position:relative; }
h1 { font-size:23px; color:#1e3a5f; border-bottom:3px solid #1e3a5f; padding-bottom:8px; margin-bottom:4px; }
.sub { color:#64748b; font-size:11.5px; margin-bottom:14px; }
h2 { font-size:14.5px; color:#1e3a5f; margin:10px 0 5px; }
p, li { font-size:11px; line-height:1.55; }
ul { padding-left:16px; margin-bottom:6px; }
table { border-collapse:collapse; width:100%; font-size:10px; margin-bottom:8px; }
th { background:#1e3a5f; color:#fff; padding:4.5px 7px; text-align:left; font-size:9.5px; }
td { padding:3.2px 7px; border-bottom:0.5px solid #e2e8f0; line-height:1.35; }
tr:nth-child(even) td { background:#f8fafc; }
.mono { font-family:Menlo,monospace; font-size:.95em; color:#0f172a; }
.tbl-name { font-family:Menlo,monospace; font-weight:700; color:#1e3a5f; }
.pk { background:#fbbf24; color:#7c2d12; font-size:8px; font-weight:800; border-radius:3px; padding:0 3px; }
.fk { background:#bfdbfe; color:#1e40af; font-size:8px; font-weight:800; border-radius:3px; padding:0 3px; }
.note { background:#fffbeb; border-left:3px solid #f59e0b; padding:7px 10px; font-size:10.5px;
        color:#78350f; margin:8px 0; line-height:1.5; }
.foot { position:absolute; bottom:8mm; left:17mm; right:17mm; display:flex;
        font-size:9px; color:#94a3b8; border-top:0.5px solid #e2e8f0; padding-top:4px; }
.foot span:last-child { margin-left:auto; }
.instructor { background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:10px 12px; margin-top:10px; }
.instructor h2 { color:#b91c1c; margin-top:0; }
.wk { font-weight:700; color:#1e3a5f; white-space:nowrap; }
"""


def render(html_body, out_pdf):
    doc = (f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style>'
           f'</head><body>{html_body}</body></html>')
    html_path = out_pdf.replace(".pdf", ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    subprocess.run([BRAVE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", html_path], check=True, capture_output=True)
    print("→", out_pdf)


def t(headers, rows):
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"


# ============================================================= 명세서
def spec():
    col = ["컬럼", "타입", "설명"]
    p1 = f"""
<div class="page">
<h1>미니 EMR 데이터셋 명세서</h1>
<div class="sub">의료진을 위한 데이터베이스 · 한 학기 공용 실습 데이터 · 파일: <span class="mono">mini_emr.sqlite</span> (CSV 8개 동본)</div>

<p><b>개요</b> — 가상 환자 <b>50명</b>, 내원 <b>100건</b>으로 구성된 축소형 전자의무기록입니다.
실제 병원 데이터의 구조(환자 1 : 내원 N : 진료기록 N)를 그대로 따르되, A4 한 장에 파악되는 크기로 만들었습니다.
<b>모든 데이터는 인공적으로 생성된 가상 정보이며 실존 인물과 무관합니다.</b> 환자 이름·주민번호가 없는 것은
가명처리된 연구용 데이터셋의 형태를 본뜬 것입니다(14주차 주제).</p>

<h2>patient — 환자 (50행)</h2>
{t(col, [["<span class='mono'>patient_id</span> <span class='pk'>PK</span>", "TEXT", "환자ID (P001~P050)"],
["<span class='mono'>sex</span>", "TEXT", "성별 M/F (CHECK 제약)"],
["<span class='mono'>birth_date</span>", "DATE", "생년월일 (YYYY-MM-DD)"],
["<span class='mono'>blood_type</span>", "TEXT", "혈액형 (ABO/Rh, 예: A+)"]])}

<h2>visit — 내원 (100행)</h2>
{t(col, [["<span class='mono'>visit_id</span> <span class='pk'>PK</span>", "TEXT", "내원ID (V0001~)"],
["<span class='mono'>patient_id</span> <span class='fk'>FK</span>", "TEXT", "환자ID → patient"],
["<span class='mono'>visit_date</span>", "DATE", "내원일"],
["<span class='mono'>department</span>", "TEXT", "진료과 (내과·신경과·외과·정형외과·응급의학과·가정의학과·소아청소년과)"],
["<span class='mono'>visit_type</span>", "TEXT", "외래 / 입원 / 응급 (CHECK 제약)"],
["<span class='mono'>discharge_date</span>", "DATE", "퇴원일 — 외래·응급 귀가는 NULL"],
["<span class='mono'>attending_id</span> <span class='fk'>FK</span>", "TEXT", "담당의 → staff"]])}

<h2>diagnosis — 진단 (140행)</h2>
{t(col, [["<span class='mono'>dx_id</span> <span class='pk'>PK</span>", "TEXT", "진단ID"],
["<span class='mono'>visit_id</span> <span class='fk'>FK</span>", "TEXT", "내원ID → visit"],
["<span class='mono'>kcd_code</span>", "TEXT", "KCD-8 상병코드 (예: I63.9)"],
["<span class='mono'>dx_name</span>", "TEXT", "진단명"],
["<span class='mono'>is_primary</span>", "INTEGER", "주진단 여부 (1=주진단, 0=부진단)"]])}

<h2>prescription — 처방 (154행)</h2>
{t(col, [["<span class='mono'>rx_id</span> <span class='pk'>PK</span>", "TEXT", "처방ID"],
["<span class='mono'>visit_id</span> <span class='fk'>FK</span>", "TEXT", "내원ID → visit"],
["<span class='mono'>drug_code</span>", "TEXT", "약품코드 (예: MET500)"],
["<span class='mono'>drug_name</span>", "TEXT", "약품명 (예: 메트포르민)"],
["<span class='mono'>dose</span>", "TEXT", "용량 (예: 500mg)"],
["<span class='mono'>duration_days</span>", "INTEGER", "투약일수"]])}
<div class="foot"><span>미니 EMR 명세서 · 의료진을 위한 데이터베이스</span><span>1 / 3</span></div>
</div>"""

    p2 = f"""
<div class="page">
<h2 style="margin-top:0">lab — 검체 검사 (93행)</h2>
{t(col, [["<span class='mono'>lab_id</span> <span class='pk'>PK</span>", "TEXT", "검사ID"],
["<span class='mono'>visit_id</span> <span class='fk'>FK</span>", "TEXT", "내원ID → visit"],
["<span class='mono'>test_name</span>", "TEXT", "검사명 (HbA1c·Glucose·Creatinine·Hemoglobin·LDL·CRP)"],
["<span class='mono'>result_value</span>", "REAL", "결과값 — <b>NULL은 '결과 미산출'</b>(검체 용혈 등)"],
["<span class='mono'>unit</span>", "TEXT", "단위 (%·mg/dL·g/dL·mg/L …)"],
["<span class='mono'>ref_low / ref_high</span>", "REAL", "정상 참고범위 하한/상한 (교육용 단일 범위 — 실제는 성별·연령·기관별로 다름)"],
["<span class='mono'>collected_at</span>", "DATETIME", "채혈 시각"]])}

<h2>vital — 활력징후 (149행) — 복합 PK (visit_id, measured_at)</h2>
{t(col, [["<span class='mono'>visit_id</span> <span class='pk'>PK</span> <span class='fk'>FK</span>", "TEXT", "내원ID → visit"],
["<span class='mono'>measured_at</span> <span class='pk'>PK</span>", "DATETIME", "측정 시각 (같은 내원에서 반복 측정)"],
["<span class='mono'>sbp / dbp</span>", "INTEGER", "수축기/이완기 혈압 (mmHg)"],
["<span class='mono'>pulse</span>", "INTEGER", "맥박 (회/분)"],
["<span class='mono'>temp</span>", "REAL", "체온 (℃)"],
["<span class='mono'>spo2</span>", "INTEGER", "산소포화도 (%)"]])}

<h2>staff — 의료진 (21행)</h2>
{t(col, [["<span class='mono'>staff_id</span> <span class='pk'>PK</span>", "TEXT", "직원ID"],
["<span class='mono'>role</span>", "TEXT", "직종 (의사·간호사·약사·임상병리사·방사선사)"],
["<span class='mono'>department</span>", "TEXT", "소속 진료과/부서"]])}

<h2>imaging — 영상 검사 (21행)</h2>
{t(col, [["<span class='mono'>img_id</span> <span class='pk'>PK</span>", "TEXT", "검사ID"],
["<span class='mono'>visit_id</span> <span class='fk'>FK</span>", "TEXT", "내원ID → visit"],
["<span class='mono'>modality</span>", "TEXT", "촬영 종류 (CXR·CT·MRI·X-ray)"],
["<span class='mono'>body_part</span>", "TEXT", "부위 (흉부·뇌·복부·고관절)"],
["<span class='mono'>taken_date</span>", "DATE", "촬영일"],
["<span class='mono'>report</span>", "TEXT", "판독문 (비정형 자유 텍스트)"]])}

<h2>주요 코드표</h2>
{t(["KCD", "진단명"], [["I10", "본태성 고혈압"], ["I20.9 / I48 / I63.9", "협심증 / 심방세동 / 뇌경색증"],
["E11.9 / E78.5", "2형 당뇨병 / 고지혈증"], ["J18.9 / J45.9", "폐렴 / 천식"],
["K29.7 / K80.2", "위염 / 담낭결석"], ["N18.3 / M17.9 / A09.9 / S72.0", "만성콩팥병 / 무릎관절증 / 감염성장염 / 대퇴골 경부 골절"]])}
{t(["약품코드", "약품명 (분류)"], [["MET500 / AML5 / ATV20", "메트포르민(혈당강하) / 암로디핀(혈압강하) / 아토르바스타틴(지질강하)"],
["ASA100 / CLO75 / PPI20 / ACE500", "아스피린 / 클로피도그렐(항혈소판) / 에스오메프라졸 / 아세트아미노펜"],
["CTX2 / AMC625 / LVX500", "세프트리악손 / 아목시실린-클라불란산 / 레보플록사신 (<b>항생제</b>)"]])}
<div class="foot"><span>미니 EMR 명세서 · 의료진을 위한 데이터베이스</span><span>2 / 3</span></div>
</div>"""

    p3 = f"""
<div class="page">
<div class="note" style="margin-top:0">사용법 — Colab: 노트북 첫 셀 실행으로 자동 준비 · 개인 PC: DB Browser for SQLite(무료)로
<span class="mono">mini_emr.sqlite</span> 열기 · 재생성: <span class="mono">python3 generate_mini_emr.py</span> (seed 고정, 항상 동일 데이터)</div>
<div class="instructor">
<h2>교수자용 노트 — 학생 배포본에서는 이 페이지를 제외하세요</h2>
<p>데이터에는 주차별 실습이 성립하도록 다음 시나리오가 <b>의도적으로 심겨</b> 있습니다.</p>
{t(["주차", "심어둔 시나리오", "확인 방법"], [
["4주", "65세 이상 여성 14명 존재", "WHERE sex='F' AND 연나이≥65"],
["5주", "혈압이 정상·주의·고혈압 3구간에 고루 분포 / 35일 장기입원(P039) 1건", "CASE 분류, MAX(재원일수)"],
["6주", "암로디핀 46건 등 10건 이상 처방 약물 5종", "GROUP BY drug_name HAVING"],
["11주", "당뇨(E11) 진단자 8명 중 <b>P007·P013은 HbA1c 검사 이력 없음</b>", "LEFT JOIN → NULL 2명"],
["12주", "항생제(CTX2·AMC625·LVX500) 무노출 환자 41명 / 평균 재원 11.7일 초과 입원 존재", "NOT EXISTS, 스칼라 서브쿼리"],
["13주", "2020년 이후 첫 I63 신규 8명(P021~P028) — <b>P029·P030은 2019년 진단력</b>으로 washout 제외 대상", "HAVING MIN(visit_date)"],
["14주", "혈당 1건이 mmol/L 단위(L0092, 7.8) / 결과값 NULL 1건(L0093) / 오후 채혈 혼입 / 판독문 내 부정 표현", "GROUP BY unit 등 감사 쿼리"],
])}
<p style="margin-top:6px"><b>생성 스크립트</b>: <span class="mono">mini_emr/generate_mini_emr.py</span> —
seed 고정(20260301)이라 언제 실행해도 동일한 데이터가 나옵니다. 시나리오를 바꾸고 싶으면 스크립트 상단의
환자 배정 딕셔너리를 수정한 뒤 재실행하고, 검증 쿼리(각 주차 대표 질문)를 다시 돌려 확인하세요.</p>
<p style="margin-top:4px"><b>배포</b>: 저장소는 <span class="mono">github.com/kevinkwshin/medical-db-course-2026</span> —
push 후 학생에게는 실습안내.md 링크만 공지하면 됩니다. 노트북의 DB_URL도 이 저장소를 가리킵니다.</p>
</div>
<div class="foot"><span>미니 EMR 명세서 · 교수자용</span><span>3 / 3</span></div>
</div>"""
    render(p1 + p2 + p3, os.path.join(BASE, "..", "mini_emr", "데이터셋_명세서.pdf"))


# ============================================================= 강의계획서
def syllabus():
    rows = [
        ["1", "데이터베이스 개론 — 의료데이터의 세계", "데이터vs정보(혈압 120/80) · 정형/비정형 · EMR·LIS·PACS·CDW 지도 · 미니 EMR 소개", "첫 SQL 데모"],
        ["2", "관계형 DB의 기본 구조", "테이블 구성 · 1:N 계층 · PK/FK·대리키 · NULL의 의미", "키 찾기"],
        ["3", "SELECT ①", "SELECT·FROM · 별칭 · DISTINCT · ORDER BY · LIMIT", "\"어떤 진료과가 있나?\""],
        ["4", "SELECT ② WHERE", "비교·논리연산 · BETWEEN·IN·LIKE · IS NULL · 날짜 조건", "\"65세 이상 여성은?\" \"I코드 진단은?\""],
        ["5", "SELECT ③ 계산·집계", "산술식(재원일수) · CASE(혈압 분류) · COUNT/AVG/MIN/MAX · NULL과 집계", "\"평균 재원일수는?\" \"검사 이상 비율은?\""],
        ["6", "SELECT ④ GROUP BY", "그룹 집계 · HAVING · WHERE vs HAVING · Table 1 맛보기", "\"진료과별 환자 수는?\" \"10건 이상 약물은?\""],
        ["7", "DDL — 테이블 설계", "데이터 타입 · CREATE TABLE · 제약조건 5종 · ALTER/DROP · 설계=연구설계", "내 코호트 테이블 설계"],
        ["8", "DML — 입력·수정·삭제", "INSERT/UPDATE/DELETE · soft delete와 감사로그 · 트랜잭션과 ACID", "\"오입력 검사값 정정은 어떻게?\""],
        ["9", "중간고사", "1~8주차 전 범위 (SELECT 4부작 중심)", "—"],
        ["10", "모델링과 정규화", "ERD · 이상현상을 임상 사고로 · 1NF~3NF · 반정규화 · OMOP CDM", "\"왜 처방엔 환자 이름이 없나?\""],
        ["11", "JOIN", "INNER/LEFT · 3+테이블 조인 · LEFT JOIN으로 결측 환자 찾기", "\"당뇨 환자의 HbA1c를 보려면?\""],
        ["12", "서브쿼리", "스칼라 · IN · EXISTS/NOT EXISTS · NOT IN의 NULL 함정", "\"평균보다 오래 입원한 환자는?\" \"항생제 무노출자는?\""],
        ["13", "실전 — 코호트 추출", "포함·제외 기준 · index date · washout · WITH(CTE) · Table 1 · VIEW", "\"2020년 이후 첫 뇌졸중 환자를 뽑아보자\""],
        ["14", "함정·보안·비정형", "단위·시각·코드 함정 · 결측과 분모 · 가명처리·IRB · PACS와 AI 데이터셋", "\"이 결과를 믿어도 되나?\""],
        ["15", "조별 프로젝트 발표", "코호트 정의서 + 추출 쿼리 + Table 1", "—"],
    ]
    trs = "".join(f"<tr><td class='wk'>{r[0]}</td><td><b>{r[1]}</b></td><td>{r[2]}</td><td>{r[3]}</td></tr>" for r in rows)
    body = f"""
<div class="page">
<h1>강의계획서 — 의료진을 위한 데이터베이스</h1>
<div class="sub">15주 · SQL 실습 중심 · 실습환경: Google Colab + SQLite (설치 불필요)</div>

<h2>수업 개요</h2>
<p>임상 질문을 SQL로 번역하는 능력을 기른다. 학기 내내 <b>단 하나의 데이터셋(미니 EMR: 가상 환자 50명·8개 테이블)</b>만 사용하며,
실습 슬라이드는 "한국어 임상 질문 → SQL → 실제 결과"의 3단 구조로 진행된다. 최종 목표는 연구 질문에서
<b>코호트 정의서 → 추출 쿼리 → Table 1</b>까지 스스로 완성하는 것.</p>

<h2>학습 목표</h2>
<ul>
<li>미니 EMR에서 SELECT·WHERE·GROUP BY·JOIN·서브쿼리로 임상 질문에 답한다</li>
<li>연구용 테이블을 제약조건과 함께 설계(CREATE)하고, 안전하게 수정(트랜잭션)한다</li>
<li>포함·제외 기준과 index date를 정의하여 연구 코호트와 Table 1을 추출한다</li>
<li>단위 불일치·결측·코드 문제를 점검하고, 가명처리·IRB 등 데이터 윤리 원칙을 설명한다</li>
</ul>

<h2>주차별 계획</h2>
<table>
<thead><tr><th style="width:5%">주</th><th style="width:20%">주제</th><th style="width:47%">내용</th><th>대표 질문 / 실습</th></tr></thead>
<tbody>{trs}</tbody>
</table>

<h2>평가</h2>
<p>출석 10% · 주차별 실습과제 20% · 중간고사 30% · 조별 프로젝트 40%
(프로젝트 배점: 포함·제외 기준의 임상적 타당성 40 / 쿼리 정확성 30 / Table 1 해석 20 / 발표 10)</p>

<h2>교재·자료</h2>
<p>주차별 강의 슬라이드(PDF), Colab 실습 노트북, 미니 EMR 데이터셋 및 명세서 — 모두 수업 저장소에서 배포.
참고: 「누구나 쉽게 이해하는 데이터베이스」 등 데이터베이스 개론서.</p>
<div class="foot"><span>의료진을 위한 데이터베이스 · 강의계획서</span><span>1 / 1</span></div>
</div>"""
    render(body, os.path.join(BASE, "..", "강의계획서.pdf"))


if __name__ == "__main__":
    spec()
    syllabus()
