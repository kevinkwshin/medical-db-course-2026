# -*- coding: utf-8 -*-
"""9강. 의료데이터 SQL 종합실습 (원본 128~133번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)

SPAN = (128, 133)
TITLE = "9강. 의료데이터 SQL 종합실습"

AGENDA = [("질문을 SQL로 바꾸기", "다섯 단계 절차"),
          ("종합 예제", "질환별 임상시험 현황"),
          ("병원 SQL 사례", "실제로 이렇게 씁니다"),
          ("검산", "결과를 믿기 전에"),
          ("과제 1", "제출 안내"),
          ("정리", "요약")]


def procedure_slide():
    def b(ids):
        steps = [("① 질문을 한 문장으로", "“무엇을, 어떤 대상에서, 몇 개” 를 분명히 적는다"),
                 ("② 세는 단위를 정한다", "시험 건수? 환자 수? 기관 수? — 결과의 한 행이 무엇인가"),
                 ("③ 필요한 표와 연결 키", "어느 표에 있는 값인가, 무엇으로 연결하는가"),
                 ("④ 조건을 하나씩 더한다", "한 번에 다 쓰지 않고 건수 변화를 보며 추가"),
                 ("⑤ 검산한다", "건수 · 분모 · 중복을 확인한 뒤 결과를 쓴다")]
        s, y, h, gap = "", 1560000, 830000, 110000
        for i, (t, d) in enumerate(steps):
            s += shape(ids, "rect", X0 + 500000, y, 3600000, h,
                       fill=("DEEAF6" if i < 4 else "FFF2CC"), line=("1F497D" if i < 4 else "BF9000"),
                       text_xml=para(f"**{t}**", sz=2100, algn="ctr", lnSpc=105), name="Step")
            s += shape(ids, "rect", X0 + 4100000, y, 7800000, h, fill="FFFFFF", line="7F7F7F",
                       text_xml=para(d, sz=2000, lnSpc=105, marL=250000), name="Desc")
            y += h + gap
        s += textbox(ids, X0, 6360000, W0, 500000,
            para("SQL을 먼저 쓰지 말고, ①②③을 **말이나 글로 먼저** 적는 것이 가장 빠릅니다.",
                 sz=2300, b=True, algn="ctr", lnSpc=115))
        return s
    return free("분석 질문을 SQL로 바꾸는 절차", b, subtitle="다섯 단계를 순서대로")


def stepwise_slide(no, title_txt, sub, question, sql_lines, result, result_w, check_txt, sz=1900, progress=None):
    """단계별 SQL 한 장: 질문 → SQL + 결과 → 확인 → (선택) 아래에 지금까지의 건수 띠"""
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
                    para(f"**질문**  {question}", sz=2300, lnSpc=115))
        n = len(sql_lines)
        hh = int(n * (sz / 100) * 12700 * 1.25 + 360000)
        s += shape(ids, "roundRect", X0, 2100000, 7300000, hh, fill="F6F8FA", line="7F7F7F", name="SQL")
        s += textbox(ids, X0 + 250000, 2250000, 6900000, hh - 200000,
                     "".join(para(l, sz=sz, lnSpc=110, sql=True) for l in sql_lines), autofit=False)
        t, th = table(ids, 8200000, 2100000, result_w, result, sz=1700, row_h=420000, algn="ctr")
        s += t
        y = max(2100000 + hh, 2100000 + th) + 350000
        ch = 340000 * (1 + str(check_txt).count("\n")) + 180000
        s += textbox(ids, X0, y, W0, ch,
                     para(f"**확인**  {check_txt}", sz=2200, lnSpc=120, color="1F3763"))
        if progress:
            py = max(5900000, y + ch + 400000)
            s += textbox(ids, X0, py - 420000, W0, 380000,
                         para("여기까지의 건수", sz=1800, b=True, color=GRAY, lnSpc=100), autofit=False)
            bw, gap = 2100000, 420000
            for i, (label, val, done) in enumerate(progress):
                x = X0 + i * (bw + gap)
                s += box(ids, x, py, bw, 700000, [f"**{label}**", val], sz=1700,
                         fill=("DEEAF6" if done else "F2F2F2"), line=("1F497D" if done else "BFBFBF"),
                         geom="rect", lnSpc=110, color=(None if done else GRAY))
                if i < len(progress) - 1:
                    s += arrow_right(ids, x + bw + gap // 2 - 150000, py + 180000, 300000, 320000)
        return s
    return free(title_txt, b, subtitle=sub)


def hospital_cases_slide():
    return table_slide("병원에서 SQL을 쓰는 일", "실제로 이런 숫자를 SQL로 뽑습니다",
        ["누가", "무엇을", "어떤 SQL이 쓰이나"],
        [["QI · 적정성평가 담당", "지표별 대상자 수와 충족률", "조건으로 대상자 선별 → 분모 · 분자 각각 COUNT"],
         ["감염관리팀", "월별 감염 발생 건수, 재원일수", "GROUP BY 월 · 병동, 날짜 차이 계산"],
         ["간호부", "간호 인력 대비 환자 수, 낙상 건수", "GROUP BY 병동 · 근무조, COUNT와 비율"],
         ["연구자", "연구 대상자 선별, 변수 추출", "여러 표를 JOIN하여 코호트 추출"],
         ["원무 · 경영", "진료과별 실적, 수납 현황", "GROUP BY 진료과 · 기간, SUM과 AVG"]],
        [2800000, 3800000, 5600000], sz=1900, row_h=640000, y=1650000,
        col_algn=["ctr", "l", "l"],
        note="공통점: **대상을 고르고(WHERE) → 묶어서 세고(GROUP BY) → 검산한다**. 오늘 배운 그대로입니다.\n코호트 = 같은 조건으로 묶어 분석 대상으로 삼은 집단 (13주차에서 자세히).")


def verify_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("결과를 보고서에 쓰기 전에 **반드시 확인하는 다섯 가지**입니다.", sz=2300, lnSpc=115))
        rows = [["① 전체 건수", "조건 없이 센 값과 비교했을 때 말이 되는가", "COUNT(*) FROM studies"],
                ["② 세는 단위", "시험 수인가, 행 수인가", "COUNT(*) 인가 COUNT(DISTINCT nct_id) 인가"],
                ["③ 분모", "JOIN 때문에 대상이 줄지 않았는가", "LEFT JOIN 으로 다시 세기"],
                ["④ 빠진 값", "NULL이 많은 열을 조건에 썼는가", "COUNT(열) 로 값 있는 행 세기"],
                ["⑤ 이상한 값", "최소 · 최대가 상식적인가", "MIN(), MAX() 로 확인"]]
        t, h = table(ids, X0, 2100000, [2300000, 5200000, 5000000],
                     [["확인할 것", "무엇을 보는가", "어떻게"]] + rows,
                     sz=1900, row_h=620000, header_h=520000, col_algn=["ctr", "l", "l"],
                     col_font={2: "Courier New"})
        s += t
        s += textbox(ids, X0, 2100000 + h + 400000, W0, 900000,
            para("숫자가 틀리는 것보다 **틀린 줄 모르는 것**이 더 위험합니다.", sz=2400, b=True, algn="ctr", lnSpc=115) +
            para("12주차에서 이 다섯 가지를 오류 사례와 함께 다시 봅니다.", sz=2200, algn="ctr", lnSpc=115, color="1F3763"))
        return s
    return free("검산 — 결과를 믿기 전에", b, subtitle="다섯 가지만 확인하면 대부분 걸러집니다")


def assignment_slide():
    def b(ids):
        s = panel(ids, X0, 1550000, 6000000, 2500000, "무엇을 제출하나요", [
            "노트북 파일 하나 (과제1.ipynb)",
            "- 모든 셀을 실행한 상태로 저장",
            "- 학번 · 이름을 첫 셀에 기입",
            "- 마지막 해석 문항은 직접 작성",
            "제출: LMS,  마감: 9주차 수업 후 1주일 이내"], fill="DEEAF6", line="1F497D", sz=1900)
        s += panel(ids, 7300000, 1550000, 6000000, 2500000, "어떻게 채점하나요", [
            "자동 확인 12점",
            "- check(\"Q1\", _) 가 ✅ 이면 정답",
            "결과 해석 5점",
            "- 숫자가 뜻하는 바를 문장으로",
            "실행 완료 · 형식 3점"], fill="E2EFDA", line="2C5F2D", sz=1900)
        rows = [["① 조회 기초", "6문항", "SELECT · WHERE · ORDER BY 의 빈칸 채우기 (7주차)"],
                ["② 집계와 GROUP BY", "3문항", "COUNT · AVG · GROUP BY 의 빈칸 채우기 (8주차)"],
                ["③ 배정 질환 분석", "3문항", "JOIN 으로 두 표를 연결해 세기"],
                ["④ 결과 해석", "2문항", "숫자가 뜻하는 바를 문장으로"]]
        t, h = table(ids, X0, 4150000, [3000000, 1600000, 7000000],
                     [["문항 유형", "개수", "내용"]] + rows,
                     sz=1800, row_h=420000, header_h=440000, col_algn=["l", "ctr", "l"])
        s += t
        s += textbox(ids, X0, 4150000 + h + 200000, W0, 600000,
            para("학번 끝자리에 따라 **분석할 질환이 다르게 배정**됩니다. 결과 숫자도 사람마다 다릅니다.",
                 sz=2300, b=True, algn="ctr", lnSpc=115))
        return s
    return free("과제 1 안내", b, subtitle="20점 · 노트북 파일 하나 · 9주차 수업 후 1주일 이내")


def build(c):
    # --- 도입
    c.add(cover(9, "의료데이터 SQL 종합실습",
                ["분석 질문을 SQL로 바꾸기", "질환별 임상시험 현황 구하기", "검산과 과제 1 제출"],
                "2026. 11. 10."))
    c.add(content("지난시간 리뷰", [
        ("**집계 함수**: COUNT · SUM · AVG · MEDIAN", dict(lvl=1, marL=457200, indent=-457200)),
        ("**GROUP BY** 로 묶고, **HAVING** 으로 그룹을 거른다", dict(lvl=1, marL=457200, indent=-457200)),
        ("**JOIN** 으로 표를 연결하고, 뒤에는 **행 수를 확인**한다", dict(lvl=1, marL=457200, indent=-457200)),
        ("지금까지는 문법을 하나씩 배웠습니다.", dict(spcBef=18)),
        ("오늘은 **질문 하나를 끝까지** 풀어 봅니다.", dict(b=True, algn="ctr", color=BLUE, spcBef=12)),
    ]))
    c.add(objectives_slide(9,
        ["분석 질문을 다섯 단계로 나누어 SQL로 바꿀 수 있다",
         "서브쿼리로 대상을 먼저 뽑고 그 안에서 셀 수 있다",
         "조건을 하나씩 더하며 결과를 확인할 수 있다",
         "검산 다섯 가지로 결과를 스스로 점검할 수 있다",
         "과제 1을 제출할 수 있다"],
        AGENDA, subtitle="질문 하나를 처음부터 끝까지 풀어 봅니다",
        date_note="과제 1 (20점) — 7 · 8주차 범위, 9주차 수업 후 1주일 이내 LMS 제출"))

    # --- 1. 절차
    c.add(section_slide(1, AGENDA, lead="SQL을 쓰기 전에 무엇을 먼저 할까요?"))
    c.add(procedure_slide())
    c.add(two_panel_slide("같은 질문, 다른 답", "세는 단위를 정하지 않으면 생기는 일",
        "“당뇨 임상시험이 몇 건인가요?” — 이 질문만으로는 SQL을 쓸 수 없습니다.",
        ("이렇게 물으면 — 모호함", ["당뇨 시험이 몇 건인가요?",
                       "- 제2형만? 제1형도?",
                       "- 진행 중인 것만? 완료된 것도?",
                       "- 어느 나라? 어느 기간?",
                       "→ 사람마다 다른 숫자가 나옴"], *RED_PANEL),
        ("이렇게 물으면 — 분명함", ["2015~2024년에 시작한",
                       "- MeSH 용어가 'Diabetes Mellitus, Type 2' 인",
                       "- 중재 연구 중 완료된 것이",
                       "- 몇 **건**인가요?",
                       "→ 누가 해도 같은 숫자"], *GREEN_PANEL),
        note=["연구자 · 부서에서 분석을 요청받으면 **먼저 이 네 가지를 되묻습니다.**",
              "대상 · 기간 · 조건 · 세는 단위. 11주차 요청서에서 다시 봅니다."],
        y=2300000, h=2900000))

    c.add(sql_example("서브쿼리 — 대상을 먼저 뽑고, 그 안에서 세기", "괄호 안이 먼저 계산됩니다",
        "제2형 당뇨 대상 시험이 몇 건이야?",
        ["SELECT COUNT(DISTINCT nct_id) AS 시험수",
         "FROM studies",
         "WHERE nct_id IN (",
         "    SELECT nct_id",
         "    FROM browse_conditions",
         "    WHERE mesh_term =",
         "          'Diabetes Mellitus, Type 2'",
         ");"],
        sz=1700,
        result=[["시험수"], ["1,353"]], result_w=[6000000], request_label="자연어 요청",
        note="괄호 안에서 ‘대상자 목록’을 먼저 만들고, 바깥에서 그 목록에 드는 것만 셉니다."))
    c.add(table_slide("서브쿼리와 JOIN — 언제 무엇을", "같은 답이 나오지만 쓰임이 다릅니다",
        ["", "서브쿼리 (IN)", "JOIN"],
        [["무엇을 하나", "대상 목록을 만들어 걸러냄", "두 표를 옆으로 이어 붙임"],
         ["행 수가 늘어나나", "늘지 않음 (원래 표 그대로)", "1 : N 이면 늘어남"],
         ["언제 쓰나", "‘이 조건에 맞는 대상만’ 고를 때", "다른 표의 **열을 함께 보여줄** 때"],
         ["이번 사례에서는", "대상 시험 고르기", "상태 · 국가를 함께 보기"]],
        [2800000, 4600000, 4200000], sz=1900, row_h=640000, y=1750000,
        col_algn=["ctr", "l", "l"],
        note="대상을 고르기만 할 때는 서브쿼리가 안전합니다. 행 수가 변하지 않기 때문입니다."))

    # --- 2. 종합 예제
    c.add(section_slide(2, AGENDA, lead="제2형 당뇨병 임상시험 현황을 구해 봅니다"))
    c.add(stepwise_slide(1, "1단계 — 대상 고르기", "먼저 대상이 몇 건인지 셉니다",
        "제2형 당뇨병을 대상으로 한 임상시험은 몇 건인가?",
        ["SELECT COUNT(DISTINCT nct_id) AS 시험수",
         "FROM browse_conditions",
         "WHERE mesh_term = 'Diabetes Mellitus, Type 2';"],
        [["시험수"], ["1,353"]], [3200000],
        "COUNT(DISTINCT nct_id) 를 쓴 이유는? 한 시험에 질환이 여러 개 붙어 있을 수 있기 때문입니다.",
        progress=[("전체", "37,509", True), ("대상 질환", "1,353", True), ("상태별", "—", False), ("비율", "—", False), ("한국", "—", False)]))
    c.add(stepwise_slide(2, "2단계 — 진행 상태별로 나누기", "studies와 연결해 상태를 가져옵니다",
        "그 시험들은 지금 어떤 상태인가?",
        ["SELECT s.overall_status AS 상태,",
         "       COUNT(DISTINCT s.nct_id) AS 시험수",
         "FROM studies AS s",
         "JOIN browse_conditions AS b",
         "  ON s.nct_id = b.nct_id",
         "WHERE b.mesh_term = 'Diabetes Mellitus, Type 2'",
         "GROUP BY s.overall_status",
         "ORDER BY 시험수 DESC;"],
        [["상태", "시험수"], ["COMPLETED", "817"], ["UNKNOWN", "243"],
         ["RECRUITING", "98"], ["ACTIVE_NOT_RECRUITING", "74"], ["…", "…"]],
        [3000000, 1600000],
        "합계가 1,353인지 확인합니다. 맞으면 JOIN에서 빠진 시험이 없다는 뜻입니다.", sz=1800,
        progress=[("전체", "37,509", True), ("대상 질환", "1,353", True), ("상태별", "9종", True), ("비율", "—", False), ("한국", "—", False)]))
    c.add(stepwise_slide(3, "3단계 — 비율 구하기", "분모와 분자를 각각 정합니다",
        "완료된 시험 중 결과가 게시된 비율은?",
        ["SELECT COUNT(DISTINCT s.nct_id) AS 완료시험,",
         "       COUNT(DISTINCT CASE WHEN s.results_first_posted_date",
         "             IS NOT NULL THEN s.nct_id END) AS 결과게시",
         "FROM studies AS s",
         "JOIN browse_conditions AS b ON s.nct_id = b.nct_id",
         "WHERE b.mesh_term = 'Diabetes Mellitus, Type 2'",
         "  AND s.overall_status = 'COMPLETED';"],
        [["완료시험", "결과게시"], ["817", "191"]], [2400000, 2400000],
        "CASE WHEN 조건 THEN 값 END 은 “조건에 맞을 때만 값을 남긴다”는 뜻입니다.\n191 ÷ 817 = 23.4%", sz=1700,
        progress=[("전체", "37,509", True), ("대상 질환", "1,353", True), ("상태별", "9종", True), ("비율", "23.4%", True), ("한국", "—", False)]))
    c.add(stepwise_slide(4, "4단계 — 우리나라 참여 확인", "표를 하나 더 연결합니다",
        "그 중 한국에서 진행된 시험은 몇 건인가?",
        ["SELECT COUNT(DISTINCT s.nct_id) AS 한국참여",
         "FROM studies AS s",
         "JOIN browse_conditions AS b ON s.nct_id = b.nct_id",
         "JOIN countries AS co ON s.nct_id = co.nct_id",
         "WHERE b.mesh_term = 'Diabetes Mellitus, Type 2'",
         "  AND co.name = 'South Korea'",
         "  AND co.removed = false;"],
        [["한국참여"], ["76"]], [3200000],
        "표를 두 개 연결했지만 COUNT(DISTINCT nct_id) 를 썼으므로 시험 수가 유지됩니다.", sz=1800,
        progress=[("전체", "37,509", True), ("대상 질환", "1,353", True), ("상태별", "9종", True), ("비율", "23.4%", True), ("한국", "76", True)]))
    c.add(checkpoint_slide(
        ["질문을 **대상 · 기간 · 조건 · 단위**로 나누어 적는다",
         "조건을 **한 번에 하나씩** 더하며 건수를 확인한다",
         "표를 연결할 때마다 **COUNT(DISTINCT 키)** 로 단위를 지킨다"],
        question="1단계에서 1,353건이었는데 2단계 합계가 1,340건이면 무엇을 의심해야 할까요?",
        answer="JOIN에서 studies에 없는 시험이 빠졌을 수 있습니다. LEFT JOIN으로 다시 확인합니다."))

    # --- 3. 병원 사례
    c.add(section_slide(3, AGENDA, lead="병원에서는 이런 숫자를 SQL로 뽑습니다"))
    c.add(hospital_cases_slide())
    c.add(two_panel_slide("사례 — 30일 재입원율", "QI 지표를 SQL로 만들면",
        "“지난달 퇴원 환자 중 30일 안에 다시 입원한 비율”을 구한다고 해 봅시다.",
        ("분모 — 대상 퇴원", ["지난달에 퇴원한 입원 건",
                         "- 사망 · 전원은 제외",
                         "- 같은 환자가 여러 번이면 각각 셈",
                         "→ COUNT(*) FROM 입원 WHERE …"], "DEEAF6", "1F497D"),
        ("분자 — 재입원", ["그 퇴원일로부터 30일 이내",
                       "- 계획된 재입원은 제외",
                       "- 같은 환자의 다음 입원을 찾아 연결",
                       "→ 퇴원 기록과 입원 기록을 JOIN"], "E2EFDA", "2C5F2D"),
        note=["어려운 부분은 SQL 문법이 아니라 **제외 기준을 정하는 일**입니다.",
              "13주차에서 기준일(index date)을 정하는 방법과 함께 자세히 다룹니다."],
        y=2300000, h=2700000))

    # --- 4. 검산
    c.add(section_slide(4, AGENDA, lead="숫자를 내보내기 전에 스스로 점검합니다"))
    c.add(verify_slide())

    # --- 5. 과제 1
    c.add(section_slide(5, AGENDA, lead="오늘 배운 것을 과제로 확인합니다"))
    c.add(assignment_slide())
    c.add(content("과제 1을 할 때 자주 막히는 부분", [
        ("① **데이터 파일이 안 열려요**", dict()),
        ("준비 셀을 다시 실행하세요. 런타임 → 런타임 다시 시작 후 처음부터 실행", dict(lvl=1, sz=2200)),
        ("② **check가 계속 ❌ 로 나와요**", dict()),
        ("열 이름과 순서를 문항에 적힌 대로 맞추세요. AS 이름도 채점에 들어갑니다", dict(lvl=1, sz=2200)),
        ("③ **결과가 0행이에요**", dict()),
        ("문자 값의 대소문자와 따옴표를 확인하세요. DISTINCT로 실제 값을 먼저 보세요", dict(lvl=1, sz=2200)),
        ("④ **숫자가 예시와 달라요**", dict()),
        ("학번에 따라 질환이 다르게 배정되므로 정상입니다", dict(lvl=1, sz=2200)),
        ("막히면 노트북의 ‘자주 하는 실수’ 부분과 7 · 8주차 실습 노트북을 다시 보세요.",
         dict(b=True, algn="ctr", color=BLUE, spcBef=16)),
    ], subtitle="미리 알아 두면 좋은 네 가지"))

    # --- 6. 정리
    c.add(section_slide(6, AGENDA, lead="오늘 배운 절차를 한 번에 정리합니다"))
    c.add(terms_slide(9, [
        ["세는 단위", "Granularity", "결과의 한 행이 무엇인지 (환자 · 방문 · 시험)"],
        ["질문의 네 요소", "—", "대상 · 기간 · 조건 · 세는 단위. SQL로 옮기기 전에 적는다"],
        ["단계별 추출", "—", "조건을 하나씩 더하며 건수 변화를 기록하는 방법"],
        ["서브쿼리", "Subquery", "괄호 안이 먼저 계산되는 SQL. 대상을 고를 때 씀"],
        ["검산", "Sanity Check", "숫자를 내보내기 전에 스스로 확인하는 절차"],
        ["분모 · 분자", "Denominator · Numerator", "비율을 만들 때 아래와 위에 오는 수"],
        ["이상값", "Outlier", "혼자 크게 튀어 평균을 끌어당기는 값"],
    ]))
    c.add(summary(9, [
        "질문을 **대상 · 기간 · 조건 · 세는 단위**로 나누어 적은 뒤 SQL을 쓴다",
        "대상만 고를 때는 **서브쿼리**, 다른 표의 열까지 볼 때는 **JOIN**",
        "조건을 **하나씩** 더하며 건수가 어떻게 변하는지 본다",
        "**검산 다섯 가지**를 확인한 뒤에 숫자를 내보낸다",
    ], sz=2800, lnSpc=170, next_week="10강. 안전한 데이터 수정과 트랜잭션 — INSERT · UPDATE · DELETE"))
