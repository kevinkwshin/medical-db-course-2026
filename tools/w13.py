# -*- coding: utf-8 -*-
"""13강. CDW 실무 사례 (원본 155~162번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)
from w9 import stepwise_slide

SPAN = (155, 162)
TITLE = "13강. CDW 실무 사례"

AGENDA = [("요청서 읽기", "무엇을 물어보는가"),
          ("코호트 정의", "대상 · 기준일 · 제외"),
          ("단계별 추출", "조건을 하나씩"),
          ("검산표", "숫자를 믿을 수 있게"),
          ("결과 해석", "무엇을 말할 수 있는가"),
          ("정리", "과제 2 제출")]


def request_slide():
    def b(ids):
        s = ""
        rows = [["연구 질문", "제2형 당뇨병 임상시험 중 결과가 게시된 비율은 얼마인가?"],
                ["대상 (포함)", "2015~2024년 시작, MeSH 'Diabetes Mellitus, Type 2'"],
                ["제외", "상태가 WITHDRAWN(철회)인 시험"],
                ["기준", "완료(COMPLETED)된 시험을 분모로"],
                ["필요 변수", "등록번호, 시작일, 상태, 결과게시일, 국가"],
                ["결과 형태", "전체 집계표 1개 + 국가별 표 1개"],
                ["승인", "공개 데이터이므로 IRB 해당 없음 (수업용)"]]
        t, h = table(ids, X0, 1520000, [2800000, 9000000],
                     [["항목", "내용"]] + rows, sz=2000, row_h=520000, header_h=480000,
                     col_algn=["ctr", "l"])
        s += t
        s += textbox(ids, X0, 1520000 + h + 300000, W0, 1300000,
            para("**이 요청서만으로 SQL을 쓸 수 있을까요?** 아직 부족한 것이 있습니다.", sz=2400, b=True, lnSpc=125) +
            para("“결과가 게시된” 이 무엇을 뜻하는지(결과게시일이 있으면?), 한 시험에 질환이 여러 개일 때 어떻게 셀지가 빠져 있습니다.",
                 sz=2200, lnSpc=125, color="1F3763"))
        return s
    return free("요청서 읽기", b, subtitle="오늘 함께 풀어 볼 요청")


def cohort_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("요청서를 **SQL로 옮길 수 있는 형태**로 다시 적습니다.", sz=2300, lnSpc=115))
        rows = [["세는 단위", "임상시험 1건 (nct_id 기준, 중복 제거)"],
                ["대상 기간", "start_date 2015-01-01 ~ 2024-12-31  (실습 DB가 이 기간만 담고 있습니다)"],
                ["포함 조건", "browse_conditions.mesh_term = 'Diabetes Mellitus, Type 2'"],
                ["제외 조건", "overall_status = 'WITHDRAWN'"],
                ["분모", "overall_status = 'COMPLETED' 인 시험 수"],
                ["분자", "위 중 results_first_posted_date IS NOT NULL 인 시험 수"],
                ["주의", "질환이 여러 개 붙을 수 있으므로 COUNT(DISTINCT nct_id)"]]
        t, h = table(ids, X0, 2050000, [2600000, 9200000],
                     [["항목", "SQL로 옮긴 정의"]] + rows, sz=1900, row_h=520000, header_h=500000,
                     col_algn=["ctr", "l"], col_font={1: "Malgun Gothic"})
        s += t
        s += textbox(ids, X0, min(2050000 + h + 300000, 6500000), W0, 700000,
            para("이렇게 적어 두면 **누가 해도 같은 숫자**가 나오고, 나중에 방법을 설명할 수 있습니다.",
                 sz=2400, b=True, algn="ctr", lnSpc=118))
        return s
    return free("코호트 정의", b, subtitle="요청서를 SQL 조건으로 바꾸기")


def verify_table_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("단계마다 건수를 적어 두면 **어디에서 얼마나 줄었는지** 설명할 수 있습니다.", sz=2300, lnSpc=115))
        rows = [["① 전체 시험", "조건 없음", "37,509", "—"],
                ["② 제2형 당뇨 대상", "mesh_term 조건", "1,353", "-36,156"],
                ["③ 철회 제외", "WITHDRAWN 제외", "1,316", "-37"],
                ["④ 완료된 것만 (분모)", "COMPLETED", "817", "-499"],
                ["⑤ 결과 게시 (분자)", "결과게시일 있음", "191", "-626"],
                ["⑥ 비율", "⑤ / ④", "23.4 %", "—"]]
        t, h = table(ids, X0, 2100000, [3400000, 3200000, 2400000, 2400000],
                     [["단계", "적용한 조건", "건수", "변화"]] + rows,
                     sz=2000, row_h=560000, header_h=520000, col_algn=["l", "l", "ctr", "ctr"])
        s += t
        s += textbox(ids, X0, 2100000 + h + 280000, W0, 1200000,
            para("**④에서 499건이 빠졌습니다.** 아직 진행 중이거나 상태가 UNKNOWN인 시험들입니다.", sz=2200, lnSpc=125) +
            para("이 표가 있으면 “왜 1,353건이 아니라 817건이 분모인가?”라는 질문에 바로 답할 수 있습니다.",
                 sz=2200, b=True, lnSpc=125, color="1F3763"))
        return s
    return free("검산표", b, subtitle="단계별 건수를 기록합니다")


def interpret_slide():
    def b(ids):
        s = panel(ids, X0, 1500000, 6000000, 2600000, "말할 수 있는 것", [
            "이 데이터 안에서, 정해진 조건으로",
            "- 완료된 제2형 당뇨 시험 817건 중",
            "- 191건(23.4%)에 결과가 게시되어 있다",
            "- 자료: AACT 2026년 9월 스냅샷(그 시점의 자료를 그대로 떠 둔 것)",
            "- 2015~2024년 시작 시험 표본 (수업용 aact_mini)"], fill="E2EFDA", line="2C5F2D", sz=1800)
        s += panel(ids, 7300000, 1500000, 6000000, 2600000, "말할 수 없는 것", [
            "“게시율이 낮으니 연구 질이 나쁘다”",
            "- 게시 의무 대상이 아닌 시험이 섞임",
            "“전 세계 당뇨 연구의 현황이다”",
            "- 수업용으로 추린 표본이고 등록된 시험만 포함",
            "“최근에 나빠지고 있다” — 추세 분석 필요"], fill="FBE5E5", line="C00000", sz=1800)
        s += textbox(ids, X0, 4350000, W0, 2000000,
            para("**결과를 쓸 때 함께 적는 것**", sz=2400, lnSpc=130) +
            para("자료 출처와 기준일 · 추출일", sz=2100, lvl=1, lnSpc=125) +
            para("포함 · 제외 기준과 각 단계의 건수 (검산표)", sz=2100, lvl=1, lnSpc=125) +
            para("결측값과 이상값을 어떻게 처리했는지", sz=2100, lvl=1, lnSpc=125) +
            para("이 분석으로 말할 수 없는 것 (한계)", sz=2100, lvl=1, lnSpc=125))
        return s
    return free("결과 해석", b, subtitle="숫자가 말해 주는 것과 말해 주지 않는 것")


def hospital_case_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("같은 절차를 병원 자료에 적용하면 이렇게 됩니다.", sz=2300, lnSpc=115))
        rows = [["① 질문", "2024년 퇴원 환자의 30일 내 재입원율"],
                ["② 세는 단위", "퇴원 건 1건 = 1행 (같은 환자의 여러 퇴원은 각각)"],
                ["③ 기준일", "퇴원일"],
                ["④ 분모", "2024년 퇴원 건 중 사망 · 전원 제외"],
                ["⑤ 분자", "퇴원일 +1일 ~ +30일 사이에 다시 입원한 건 (계획 재입원 제외)"],
                ["⑥ 검산", "분모 건수, 환자 수, 제외된 건수, 중복 입원 처리 방식"],
                ["⑦ 해석", "진료과별 차이는 중증도 보정 없이는 비교 불가"]]
        t, h = table(ids, X0, 2050000, [2400000, 9400000],
                     [["단계", "내용"]] + rows, sz=2000, row_h=530000, header_h=500000,
                     col_algn=["ctr", "l"])
        s += t
        s += textbox(ids, X0, 2050000 + h + 350000, W0, 900000,
            para("어려운 부분은 SQL이 아니라 ②③④⑤의 **기준을 정하는 일**입니다.", sz=2400, b=True, algn="ctr", lnSpc=118) +
            para("이 기준은 반드시 요청자와 합의하고 문서로 남깁니다.", sz=2200, algn="ctr", lnSpc=118, color="1F3763"))
        return s
    return free("병원 사례 — 30일 재입원율", b, subtitle="같은 절차를 병원 자료에")


def build(c):

    # --- 도입
    c.add(cover(13, "CDW 실무 사례",
                ["요청서에서 코호트 정의까지", "단계별 추출과 검산표", "결과 해석과 과제 2 제출"],
                "2026. 12. 8."))
    c.add(content("지난시간 리뷰", [
        ("**세는 단위**와 **JOIN 후 행 수**를 항상 확인한다", dict(lvl=1, marL=457200, indent=-457200)),
        ("**타입 · 표기 · 빈 값**이 결과를 조용히 바꾼다", dict(lvl=1, marL=457200, indent=-457200)),
        ("**기준일 이전 자료만** 쓰고 처리 방법을 기록한다", dict(lvl=1, marL=457200, indent=-457200)),
        ("오늘은 이 모든 것을 **요청 하나에 한꺼번에** 적용해 봅니다.", dict(b=True, algn="ctr", color=BLUE, spcBef=24)),
    ]))
    c.add(objectives_slide(13,
        ["요청서를 읽고 부족한 부분을 되물을 수 있다",
         "코호트 정의를 SQL 조건으로 옮길 수 있다",
         "검산표를 만들어 단계별 건수를 설명할 수 있다",
         "결과로 말할 수 있는 것과 없는 것을 구분할 수 있다"],
        AGENDA, subtitle="요청 하나를 처음부터 끝까지",
        date_note="과제 2(20점)는 오늘 수업 후 1주일 이내에 제출합니다"))

    # --- 1. 요청서 읽기
    c.add(section_slide(1, AGENDA, lead="요청서를 받으면 먼저 무엇을 확인할까요?"))
    c.add(request_slide())
    c.add(content("요청자에게 되물어야 할 것", [
        ("① **세는 단위가 무엇인가요?**", dict()),
        ("시험 건수인가, 환자 수인가, 기관 수인가", dict(lvl=1, sz=2200)),
        ("② **‘결과가 게시된’의 기준은 무엇인가요?**", dict()),
        ("결과게시일이 있으면 되는가, 특정 항목이 다 있어야 하는가", dict(lvl=1, sz=2200)),
        ("③ **제외할 대상이 더 있나요?**", dict()),
        ("철회 외에 진행 중인 시험은 어떻게 할지", dict(lvl=1, sz=2200)),
        ("④ **결과를 언제까지, 어떤 형태로 드릴까요?**", dict()),
        ("집계표만인지, 원자료도 필요한지 (원자료는 승인 범위 확인)", dict(lvl=1, sz=2200)),
        ("되묻는 것은 일을 늦추는 것이 아니라 **다시 하지 않기 위한 것**입니다.",
         dict(b=True, algn="ctr", color=BLUE, spcBef=16)),
    ], subtitle="바로 SQL을 쓰지 않습니다"))

    # --- 2. 코호트 정의
    c.add(section_slide(2, AGENDA, lead="요청서를 SQL 조건으로 바꿉니다"))
    c.add(cohort_slide())
    c.add(table_slide("코호트 정의에 꼭 적는 세 가지", "이 세 가지가 있어야 남이 같은 결과를 냅니다",
        ["항목", "무엇을 정하나", "이번 사례에서는"],
        [["진입 사건", "어떤 일이 있었던 대상을 뽑나", "제2형 당뇨를 대상으로 등록된 임상시험"],
         ["기준일", "각 대상의 출발점을 언제로 잡나", "시험 시작일(start_date)"],
         ["관찰 기간", "기준일 앞뒤로 얼마를 보나", "2015년 ~ 2024년에 시작한 시험"]],
        [2600000, 4200000, 5000000], sz=1900, row_h=700000, y=1750000,
        col_algn=["ctr", "l", "l"],
        note="이 세 가지를 적어 두면 여섯 달 뒤에도 같은 숫자를 다시 만들 수 있습니다."))

    # --- 3. 단계별 추출
    c.add(section_slide(3, AGENDA, lead="조건을 하나씩 더하며 건수를 기록합니다"))
    c.add(stepwise_slide(1, "1단계 — 대상 시험", "먼저 대상을 고릅니다",
        "제2형 당뇨병 시험은 몇 건인가?",
        ["SELECT COUNT(DISTINCT nct_id) AS 시험수",
         "FROM browse_conditions",
         "WHERE mesh_term = 'Diabetes Mellitus, Type 2';"],
        [["시험수"], ["1,353"]], [3200000],
        "전체 37,509건 중 1,353건입니다. 검산표 ②에 기록합니다.",
        progress=[("① 전체", "37,509", True), ("② 대상 질환", "1,353", True), ("③ 철회 제외", "—", False), ("④ 완료(분모)", "—", False), ("⑤ 결과(분자)", "—", False)]))
    c.add(stepwise_slide(2, "2단계 — 제외 조건 적용", "철회된 시험을 뺍니다",
        "철회(WITHDRAWN)를 뺀 대상은?",
        ["SELECT COUNT(DISTINCT s.nct_id) AS 시험수",
         "FROM studies AS s",
         "JOIN browse_conditions AS b ON s.nct_id = b.nct_id",
         "WHERE b.mesh_term = 'Diabetes Mellitus, Type 2'",
         "  AND s.overall_status <> 'WITHDRAWN';"],
        [["시험수"], ["1,316"]], [3200000],
        "37건이 빠졌습니다. 얼마나 빠졌는지 기록해 두는 것이 중요합니다.", sz=1800,
        progress=[("① 전체", "37,509", True), ("② 대상 질환", "1,353", True), ("③ 철회 제외", "1,316", True), ("④ 완료(분모)", "—", False), ("⑤ 결과(분자)", "—", False)]))
    c.add(stepwise_slide(3, "3단계 — 분모와 분자", "완료된 것 중 결과가 있는 것",
        "완료된 시험 중 결과가 게시된 비율은?",
        ["SELECT COUNT(DISTINCT s.nct_id) AS 분모,",
         "       COUNT(DISTINCT CASE WHEN s.results_first_posted_date",
         "             IS NOT NULL THEN s.nct_id END) AS 분자",
         "FROM studies AS s",
         "JOIN browse_conditions AS b ON s.nct_id = b.nct_id",
         "WHERE b.mesh_term = 'Diabetes Mellitus, Type 2'",
         "  AND s.overall_status = 'COMPLETED';"],
        [["분모", "분자"], ["817", "191"]], [2400000, 2400000],
        "191 ÷ 817 = 23.4%. 분모와 분자를 한 번에 세면 조건이 어긋나지 않습니다.", sz=1700,
        progress=[("① 전체", "37,509", True), ("② 대상 질환", "1,353", True), ("③ 철회 제외", "1,316", True), ("④ 완료(분모)", "817", True), ("⑤ 결과(분자)", "191", True)]))
    c.add(sql_example("4단계 — 국가별로 나누기", "요청서의 두 번째 표를 만듭니다",
        "국가별로도 나누어 보여 주세요",
        ["SELECT co.name AS 국가,", "       COUNT(DISTINCT s.nct_id) AS 완료시험",
         "FROM studies AS s",
         "JOIN browse_conditions AS b ON s.nct_id = b.nct_id",
         "JOIN countries AS co ON s.nct_id = co.nct_id",
         "WHERE b.mesh_term = 'Diabetes Mellitus, Type 2'",
         "  AND s.overall_status = 'COMPLETED'",
         "  AND co.removed = false",
         "GROUP BY co.name",
         "ORDER BY 완료시험 DESC;"],
        sz=1600, request_label="추가 요청",
        result=[["국가", "완료시험"], ["United States", "248"], ["China", "81"], ["Germany", "55"]],
        result_w=[3400000, 2600000],
        note="표를 하나 더 연결했지만 COUNT(DISTINCT nct_id)를 써서 시험 단위를 유지했습니다."))

    # --- 4. 검산표
    c.add(section_slide(4, AGENDA, lead="숫자를 설명할 수 있게 만듭니다"))
    c.add(verify_table_slide())
    c.add(checkpoint_slide(
        ["요청서를 **SQL 조건**으로 옮겨 적은 뒤 시작한다",
         "조건을 하나씩 더하며 **단계별 건수**를 기록한다",
         "**검산표**가 있으면 “왜 이 숫자인가”에 바로 답할 수 있다"],
        question="1,353건에서 817건으로 줄었습니다. 무엇을 설명해야 할까요?",
        answer="철회 37건 제외, 완료되지 않은 499건 제외. 각 단계의 건수를 표로 보여 줍니다."))

    # --- 5. 결과 해석
    c.add(section_slide(5, AGENDA, lead="숫자에 무엇을 붙여서 전달할까요?"))
    c.add(interpret_slide())
    c.add(hospital_case_slide())

    c.add(table_slide("결과표를 내보내기 전에", "표 한 칸이 사람을 특정할 수 있습니다",
        ["이런 표는", "무엇이 문제인가", "이렇게 고칩니다"],
        [["칸의 값이 아주 작을 때", "‘해당 환자 2명’ 같은 칸은 누구인지 좁혀짐", "구간을 넓게 묶거나 ‘5명 미만’으로 표기"],
         ["칸을 너무 잘게 나눌 때", "연령 × 성별 × 지역까지 나누면 한 명만 남는 칸이 생김", "나누는 기준의 수를 줄임"],
         ["합계에서 역산될 때", "전체에서 다른 칸을 빼면 가려 둔 칸이 드러남", "관련된 칸을 함께 가림"]],
        [3200000, 4600000, 4200000], sz=1800, row_h=720000, y=1750000,
        col_algn=["ctr", "l", "l"],
        note="기관마다 기준이 다릅니다. 내보내기 전에 담당 부서의 기준을 확인하세요.",
        note_style="footnote"))

    # --- 6. 정리
    c.add(section_slide(6, AGENDA, lead="과제 2 제출 안내와 오늘의 핵심입니다"))
    c.add(terms_slide(13, [
        ["분석 요청서", "Data Request Form", "무엇을 · 누구를 · 언제 · 어떻게 셀지 적은 문서"],
        ["코호트", "Cohort", "같은 조건으로 묶어 분석 대상으로 삼은 집단"],
        ["진입 사건", "Entry Event", "코호트에 들어오는 계기가 되는 사건"],
        ["기준일", "Index Date", "각 대상의 분석 출발점이 되는 날짜"],
        ["관찰 기간", "Observation Period", "기준일 앞뒤로 자료를 보는 기간"],
        ["제외 조건", "Exclusion Criteria", "대상에서 빼는 조건 (철회 · 중복 등)"],
        ["검산표", "—", "단계마다 건수와 변화량을 적어 둔 표"],
        ["분모 · 분자", "Denominator · Numerator", "비율을 만들 때 아래와 위에 오는 수"],
        ["소수 셀", "Small Cell", "사람 수가 아주 적어 개인이 드러날 수 있는 칸"],
    ]))
    c.add(content("과제 2 제출 안내", [
        ("**제출물**: 노트북 파일 하나 (과제2.ipynb)", dict()),
        ("단계별 SQL과 결과가 모두 실행된 상태", dict(lvl=1, sz=2200)),
        ("검산표 (단계별 건수)", dict(lvl=1, sz=2200)),
        ("찾아낸 오류와 수정 방법 설명", dict(lvl=1, sz=2200)),
        ("결과 해석 1쪽 — 말할 수 있는 것과 없는 것", dict(lvl=1, sz=2200)),
        ("**마감**: 13주차(오늘) 수업 후 1주일 이내, LMS 제출", dict(spcBef=14)),
        ("**도움이 되는 자료**: 12주차 오류 체크리스트, 오늘의 검산표 양식, 7~9주차 실습 노트북",
         dict(b=True, color=BLUE, spcBef=14)),
    ], subtitle="20점 · 노트북 파일 하나"))
    c.add(content("과제 2를 할 때 자주 막히는 부분", [
        ("**① 어디부터 하나요**", dict()),
        ("오류 고치기(E1~E6)는 12주차 내용으로 풀 수 있습니다. 단계별 추출과 검산표는 오늘 배운 순서대로.", dict(lvl=1, sz=2000)),
        ("**② 숫자가 정답과 다릅니다**", dict(spcBef=8)),
        ("배정된 질환이 사람마다 다릅니다. 숫자가 달라도 정상이니 줄어드는 모양만 확인하세요.", dict(lvl=1, sz=2000)),
        ("**③ 오류를 못 찾겠습니다**", dict(spcBef=8)),
        ("12주차 체크리스트를 위에서부터 대 보세요. 세는 단위 · JOIN 후 행 수 · NULL · 표기 · 기준일 순.", dict(lvl=1, sz=2000)),
        ("**④ 해석을 어떻게 쓰나요**", dict(spcBef=8)),
        ("오늘 ‘결과 해석’ 슬라이드의 두 칸을 그대로 따라 쓰면 됩니다.", dict(lvl=1, sz=2000)),
    ], subtitle="과제 1 때와 같은 방식으로 도와드립니다"))
    c.add(summary(13, [
        "요청서를 **SQL 조건으로 옮겨 적은 뒤** 추출을 시작한다",
        "**검산표**로 단계별 건수를 남겨 숫자를 설명할 수 있게 한다",
        "결과에는 **기준 · 처리 방법 · 한계**를 함께 적는다",
    ], sz=2800, lnSpc=170, next_week="14강. 빅데이터와 의료데이터 표준 — OMOP CDM과 데이터 품질"))
