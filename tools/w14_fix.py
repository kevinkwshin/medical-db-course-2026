# -*- coding: utf-8 -*-
"""14 · 15강: 12 · 13강 새 구성(원무 · 질 지표, 가상 병원 CDW)에 맞춰 글 고침 (2026-11-03). w13_new.py 다음에 실행.
- 14강 '데이터 품질 점검' 아래 줄: 12주차 오류 → 바로 뒤로 옮겨 온 '오류 점검 체크리스트'
- 14강 '병원 CDW 계정이 없다면': AACT (이 수업 실습) → AACT (7~10주차 실습)
- 15강 '기말고사 안내' 과제 2 주차 · '시험 범위' 11~13주차 칸 · '총복습 ③ 보충' 아래 줄 · '총복습 ④' 제목 · 표 · 오늘의 순서
사용: python3 tools/w14_fix.py <덱.pptx> <결과.pptx>
"""
import sys
from w10_tx_more import fill
from slidekit import A, P, Deck, texts, shape, set_para, set_title, table_fill, replace_text

RANGE = [("1 · 2 · 3", "데이터베이스와 DBMS", "데이터/정보, DBMS의 기능과 장단점, DDL · DML · DCL"),
         ("4", "데이터베이스 시스템", "스키마와 인스턴스, 3단계 스키마, 사상, 데이터 독립성, 데이터 사전"),
         ("5", "관계형 데이터베이스", "테이블 · 속성 · 튜플, 기본키 · 외래키, 무결성 3종, 타입과 NULL"),
         ("6", "모델링과 정규화", "ERD 읽기, 이상현상 3종, 1NF · 2NF · 3NF, 반정규화"),
         ("7 · 8 · 9", "SQL", "SELECT · WHERE · GROUP BY · HAVING · JOIN, 실행 순서, 집계, CASE WHEN · COALESCE, 서브쿼리"),
         ("10", "수정과 트랜잭션", "INSERT · UPDATE · DELETE, WHERE 누락, 트랜잭션, COMMIT · ROLLBACK"),
         ("11 · 12 · 13", "CDW · 원무 · 질 지표", "CDW 구조, 한 행의 단위, 재원일수 · 병상 가동률, 지표 정의서 · 30일 재입원율, 검산표 · 작은 칸"),
         ("14", "빅데이터와 표준", "정형/비정형, 용어 · 교환 · 구조 표준, OMOP CDM, 품질, 가명정보")]
REVIEW4 = [("CDW", "분석 · 연구용으로 모아 둔 읽기 전용 복사본", "운영 DB는 진료용, CDW는 분석용"),
           ("ETL", "원천에서 뽑아 정리해 CDW에 넣는 작업", "보통 하루 정도 시차"),
           ("한 행의 단위", "표의 한 행이 무엇을 뜻하는가", "환자 / 입원 / 진료비 항목"),
           ("재원일수 · 가동률", "퇴원일 − 입원일 · 재원일수 ÷ (병상 × 날짜)", "재원 중이면 퇴원일 NULL"),
           ("지표 정의서", "분모 · 분자 · 제외 · 기준일 · 관찰 기간", "30일 재입원율: 기준일 = 퇴원일"),
           ("검산표", "단계별 건수를 기록한 표", "어디에서 얼마나 줄었는지 설명"),
           ("분류와 용어", "KCD는 통계 · 청구용 분류, SNOMED CT는 임상용 용어", "KCD E11 ↔ SNOMED CT 44054006"),
           ("OMOP CDM", "여러 기관의 데이터를 같은 구조로 맞춘 모델", "PERSON · VISIT · CONDITION …"),
           ("가명정보", "추가 정보 없이는 개인을 알아볼 수 없게 처리", "가명 / 익명의 차이")]


def main(src, out):
    d = Deck(src)
    s14 = d.find("14강. 빅데이터와 의료데이터 표준")
    L = d.slides()[d.index(s14):]
    F = lambda line, also=None: d.find(line, also, within=L)
    t = d.tree(F("데이터 품질 점검"))
    set_para(shape(t, "TextBox 6"), "바로 뒤의 ‘오류 점검 체크리스트’를 데이터 전체에 대해 먼저 해 두는 것입니다.")
    replace_text(d.tree(F("병원 CDW 계정이 없다면")), "AACT (이 수업 실습)", "AACT (7~10주차 실습)")
    replace_text(d.tree(F("기말고사 안내")), "과제 2 (13주차) 20%", "과제 2 (12주차 공개) 20%")
    table_fill(d.tree(F("시험 범위")), ["주차", "주제", "꼭 알아야 할 것"], [list(r) for r in RANGE])
    set_para(shape(d.tree(F("총복습 ③ 보충 — 자주 틀리는 SQL")), "TextBox 6"), "12주차 JOIN 함정 · 재원 중(NULL) 사례와 함께 보면 시험 준비가 됩니다.")
    t = d.tree(F("총복습 ④ — CDW와 오류"))
    set_title(t, "총복습 ④ — CDW와 병원 지표")
    table_fill(t, ["개념", "한 줄 정의", "자주 나오는 구분"], [list(r) for r in REVIEW4])
    n = 0
    for s in d.slides()[d.index(F("15강. 기말고사")) if any("15강. 기말고사" in texts(d.tree(x)) for x in L) else d.index(s14):]:
        for x in d.tree(s).iter(A + "t"):
            if x.text and x.text.strip() == "CDW와 오류":
                x.text = x.text.replace("CDW와 오류", "CDW와 병원 지표"); n += 1
    assert n >= 1, "15강 오늘의 순서에 'CDW와 오류' 가 없음"
    d.save(out)
    print(f"14 · 15강: 글 고침 (오늘의 순서 {n}곳) → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
