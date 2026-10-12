# -*- coding: utf-8 -*-
"""8강. SQL (2) — 집계와 JOIN (원본 115~127번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)
from w7 import mistake_slide

SPAN = (115, 127)
TITLE = "8강. SQL (2)"

AGENDA = [("집계 함수", "COUNT · SUM · AVG · MEDIAN"),
          ("GROUP BY", "묶어서 세기"),
          ("HAVING과 실행 순서", "집계 결과에 조건"),
          ("JOIN", "두 표를 연결하기"),
          ("자주 하는 실수", "행 수를 꼭 확인"),
          ("정리", "용어와 요약")]


def count_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("COUNT는 세 가지 모양이 있고, **결과가 서로 다릅니다.**", sz=2300, lnSpc=115))
        rows = [["COUNT(*)", "모든 행", "37,509", "NULL도 포함해서 셈"],
                ["COUNT(열)", "그 열에 값이 있는 행", "4,352", "NULL은 세지 않음"],
                ["COUNT(DISTINCT 열)", "서로 다른 값의 개수", "9", "중복을 뺀 종류 수"]]
        t, h = table(ids, X0, 2100000, [3300000, 3400000, 2200000, 3600000],
                     [["쓰는 법", "무엇을 세나", "studies에서", "주의"]] + rows,
                     sz=1900, row_h=700000, header_h=520000, col_algn=["l", "l", "ctr", "l"],
                     col_font={0: "Courier New"})
        s += t
        y = 2100000 + h + 300000
        s += shape(ids, "roundRect", X0, y, W0, 1750000, fill="F6F8FA", line="7F7F7F", name="SQL")
        s += textbox(ids, X0 + 300000, y + 220000, W0 - 600000, 1450000,
            "".join(para(l, sz=2000, lnSpc=110, sql=True) for l in
                    ["SELECT COUNT(*) AS 전체행,",
                     "       COUNT(results_first_posted_date) AS 결과있음,",
                     "       COUNT(DISTINCT overall_status) AS 상태종류",
                     "FROM studies;"]), autofit=False)
        s += textbox(ids, X0, y + 1950000, W0, 600000,
            para("‘몇 건인가’를 물을 때는 **무엇을 세는지** 먼저 말로 정하세요.", sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("COUNT — 세 가지 모양", b, subtitle="COUNT(*) · COUNT(열) · COUNT(DISTINCT 열)")


def avg_median_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("중재 연구(INTERVENTIONAL) 27,916건의 등록 인원을 봅시다.", sz=2300, lnSpc=115))
        t, h = table(ids, X0 + 1200000, 2100000, [2600000, 2400000, 2400000, 2400000],
                     [["", "평균 (AVG)", "중앙값 (MEDIAN)", "최대 (MAX)"],
                      ["전체", "1,279", "60", "12,317,546"],
                      ["1만 명 이하만", "196", "60", "10,000"]],
                     sz=1900, row_h=560000, header_h=520000, algn="ctr", bold_first_col=True)
        s += t
        y = 2100000 + h + 350000
        s += panel(ids, X0, y, 6000000, 2100000, "평균이 왜 이렇게 클까", [
            "1,200만 명짜리 입력 오류가 하나 섞여 있음",
            "- 값 하나 때문에 평균이 중앙값의 20배가 됨",
            "- 중앙값은 60명으로 거의 변하지 않음"], fill="FBE5E5", line="C00000", sz=1800)
        s += panel(ids, 7300000, y, 6000000, 2100000, "병원 통계에서도 같은 일", [
            "재원일수 · 진료비 · 검사 수치",
            "- 한쪽으로 치우친 값이 대부분",
            "- 평균과 중앙값을 **함께** 보고",
            "- 이상한 값은 원인을 확인한 뒤 판단"], fill="E2EFDA", line="2C5F2D", sz=1800)
        return s
    return free("평균과 중앙값", b, subtitle="평균 하나만 보면 안 되는 이유")


def exec_order_slide():
    def b(ids):
        rows = [("SELECT", "⑤", "보여줄 열과 집계를 계산"),
                ("FROM", "①", "테이블을 가져옴"),
                ("WHERE", "②", "행을 걸러냄 (묶기 전)"),
                ("GROUP BY", "③", "같은 값끼리 묶음"),
                ("HAVING", "④", "묶은 그룹을 걸러냄"),
                ("ORDER BY", "⑥", "정렬"),
                ("LIMIT", "⑦", "앞에서 몇 줄만")]
        s = ""
        y, h, gap = 1620000, 560000, 70000
        for kw, order, what in rows:
            s += shape(ids, "rect", X0 + 600000, y, 2800000, h, fill="DEEAF6", line="1F497D",
                       text_xml=para(f"**{kw}**", sz=2200, algn="ctr", color=BLUE, font="Courier New", lnSpc=100), name="KW")
            s += shape(ids, "rect", X0 + 3400000, y, 900000, h, fill="FFF2CC", line="BF9000",
                       text_xml=para(f"**{order}**", sz=2400, algn="ctr", lnSpc=100), name="Ord")
            s += shape(ids, "rect", X0 + 4300000, y, 5500000, h, fill="FFFFFF", line="7F7F7F",
                       text_xml=para(what, sz=2000, lnSpc=100, marL=220000), name="What")
            y += h + gap
        s += textbox(ids, X0 + 10000000, 1620000, 2500000, 4000000,
            para("**적는 순서**와\n**실행 순서**가\n다릅니다", sz=2200, b=True, algn="ctr", color=RED, lnSpc=125) +
            para("그래서\nWHERE 에는\n집계 함수를\n쓸 수 없습니다", sz=2000, algn="ctr", lnSpc=125, color=GRAY, spcBef=16), autofit=False)
        s += textbox(ids, X0, 6350000, W0, 600000,
            para("집계에 대한 조건은 WHERE가 아니라 **HAVING**에 씁니다.", sz=2400, b=True, algn="ctr", lnSpc=115))
        return s
    return free("적는 순서와 실행 순서", b, subtitle="노란 숫자가 실제로 처리되는 차례")


def join_why_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("studies 표에는 **국가 정보가 없습니다.** 국가는 countries 표에 따로 있습니다.", sz=2300, lnSpc=115))
        y0 = 2150000
        e1, h1 = entity_box(ids, X0 + 600000, y0, 3000000, "studies", ["nct_id", "brief_title", "phase"], sz=1700)
        e2, h2 = entity_box(ids, X0 + 600000 + 3000000 + 2200000, y0, 3000000, "countries",
                            ["id", "nct_id", "name", "removed"], key_idx=(0,), sz=1700)
        s += e1 + e2
        s += label_line(ids, X0 + 3600000, y0 + h1 // 2, X0 + 5800000, y0 + h1 // 2, sz=1600)
        s += textbox(ids, X0 + 3700000, y0 + h1 // 2 - 470000, 2100000, 380000,
                     para("nct_id 로 연결", sz=1600, b=True, algn="ctr", color=GRAY, lnSpc=100), autofit=False)
        s += textbox(ids, 9600000, y0, 3700000, 1800000,
            para("**공통으로 가진 열**", sz=2200, lnSpc=125) +
            para("두 표 모두 nct_id 를 가지고 있음", sz=1900, lvl=1, lnSpc=120) +
            para("이 열로 같은 시험끼리 맞춰 붙임", sz=1900, lvl=1, lnSpc=120), autofit=False)
        s += textbox(ids, X0, 4100000, W0, 420000,
            para("**두 표를 잇는 조건은 ON 절에 적습니다**", sz=2200, lnSpc=110, color="1F3763"), autofit=False)
        s += shape(ids, "roundRect", X0, 4550000, W0, 1300000, fill="F6F8FA", line="7F7F7F", name="SQL")
        s += textbox(ids, X0 + 300000, 4700000, W0 - 600000, 1100000,
            "".join(para(l, sz=2000, lnSpc=110, sql=True) for l in
                    ["SELECT s.nct_id, s.brief_title, c.name AS 국가",
                     "FROM studies AS s",
                     "JOIN countries AS c ON s.nct_id = c.nct_id"]), autofit=False)
        s += textbox(ids, X0, 6100000, W0, 600000,
            para("표 이름을 s · c 처럼 짧게 붙여 두면(별칭) 어느 표의 열인지 분명해집니다.",
                 sz=2300, b=True, algn="ctr", lnSpc=115))
        return s
    return free("JOIN이 필요한 이유", b, subtitle="한 표에 없는 정보를 다른 표에서 가져오기")


def join_kind_slide():
    return two_panel_slide("JOIN의 두 가지", "양쪽에 다 있는 것만 vs 왼쪽은 모두",
        "studies 37,509건 중 2,699건은 기관(facilities) 정보가 없습니다.",
        ("JOIN (= INNER JOIN)", ["양쪽에 모두 있는 행만 남김",
                               "- 기관 정보가 없는 시험은 빠짐",
                               "- 결과: 34,810건",
                               "- 분모가 줄어드는 것을 모를 수 있음"], *RED_PANEL),
        ("LEFT JOIN", ["왼쪽(studies)은 모두 남김",
                       "- 오른쪽에 없으면 NULL로 채움",
                       "- 결과: 37,509건 그대로",
                       "- 전체를 분모로 유지할 때 사용"], *GREEN_PANEL),
        note=["“전체 시험 중 몇 %”를 구할 때 INNER JOIN을 쓰면 **분모가 조용히 줄어듭니다.**",
              "12주차에서 가장 자주 나오는 오류입니다."],
        y=2300000, h=2700000)



def clause_order_exercise_slide():
    """절 순서를 직접 맞춰 보는 연습. 적는 순서가 왜 중요한지 손으로 확인합니다."""
    PIECES = [("가", "LIMIT 5"),
              ("나", "GROUP BY phase"),
              ("다", "SELECT phase, COUNT(*) AS 건수"),
              ("라", "ORDER BY 건수 DESC"),
              ("마", "FROM studies"),
              ("바", "WHERE start_date >= '2024-01-01'")]
    ANSWER = ["다", "마", "바", "나", "라", "가"]

    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, 7000000, 700000,
            para("**“2024년에 시작한 시험을 임상 단계별로 세고, 많은 순으로 위에서 5줄만 보고 싶다.”**", sz=2200, lnSpc=120) +
            para("아래 여섯 조각을 올바른 순서로 놓아 보세요.", sz=2200, lnSpc=120, color=GRAY))
        y, h, gap = 2400000, 520000, 110000
        for i, (mark, code) in enumerate(PIECES):
            yy = y + i * (h + gap)
            s += shape(ids, "rect", X0, yy, 620000, h, fill="FFF2CC", line="BF9000",
                       text_xml=para(f"**{mark}**", sz=2000, algn="ctr", lnSpc=100), name="Mark")
            s += shape(ids, "rect", X0 + 620000, yy, 6200000, h, fill="FFFFFF", line="BFBFBF",
                       text_xml=para(code, sz=1800, lnSpc=100, marL=200000, sql=True), name="Piece")
        s += textbox(ids, 8000000, y - 470000, 5000000, 420000,
                     para("**정답**", sz=2200, color=BLUE, lnSpc=100), autofit=False)
        s += shape(ids, "roundRect", 8000000, y, 5000000, 3400000, fill="F6F8FA", line="1F497D", lw=12700,
                   name="Answer")
        ay = y + 260000
        for i, mark in enumerate(ANSWER):
            w = dict(PIECES)[mark].split()
            kw = " ".join(w[:2]) if w[0] in ("GROUP", "ORDER") else w[0]
            s += textbox(ids, 8200000, ay + i * 520000, 4600000, 470000,
                         para(f"**{i + 1}.  {mark}**   {kw}", sz=1900, lnSpc=100), autofit=False)
        s += textbox(ids, X0, 6280000, W0, 900000,
            para("**적는 순서**  SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT",
                 sz=2300, b=True, algn="ctr", lnSpc=120, color=BLUE) +
            para("순서를 바꿔 적으면 **문법 오류**가 납니다. 외우기보다 이 줄을 옆에 적어 두고 쓰세요.",
                 sz=2100, algn="ctr", lnSpc=120))
        return s
    return free("절 순서 맞추기 — 직접 해 보기", b, subtitle="흩어진 조각을 올바른 순서로")


def build(c):
    c.retitle(117, title="SELECT 문의 절", title_ext=(9500000, 541687), subtitle_contains="데이터를 조회할 때",
              new_subtitle="여섯 개의 절을 순서대로 적습니다")
    c.retitle(127, title="절의 실행 순서 (참고)", title_ext=(9500000, 541687),
              subtitle_contains="데이터를 조회할 때",
              new_subtitle="컴퓨터 안에서는 이런 차례로 계산됩니다")

    # --- 도입
    c.add(cover(8, "SQL (2) 집계와 JOIN",
                ["COUNT · SUM · AVG · MEDIAN", "GROUP BY 와 HAVING", "INNER JOIN 과 LEFT JOIN"],
                "2026. 11. 3."))
    c.add(content("지난시간 리뷰", [
        ("**SELECT → FROM → WHERE → ORDER BY → LIMIT** 순서로 적는다", dict(lvl=1, marL=457200, indent=-457200)),
        ("문자 · 날짜는 '작은따옴표', 빈 값은 **IS NULL**", dict(lvl=1, marL=457200, indent=-457200)),
        ("**DISTINCT** 로 값의 종류를 먼저 확인한다", dict(lvl=1, marL=457200, indent=-457200)),
        ("지금까지는 **행을 그대로** 봤습니다.", dict(spcBef=18)),
        ("오늘은 **여러 행을 하나의 숫자로 묶고**, **여러 표를 연결**합니다.", dict(b=True, algn="ctr", color=BLUE, spcBef=12)),
    ]))
    c.add(objectives_slide(8,
        ["COUNT의 세 가지 모양을 구분해서 쓸 수 있다",
         "GROUP BY로 묶어서 집계하고 HAVING으로 거를 수 있다",
         "CASE WHEN으로 구간을 나누어 세고, COALESCE로 빈 값을 드러낼 수 있다",
         "두 표를 JOIN으로 연결하고, 행 수가 변하는 것을 확인할 수 있다"],
        AGENDA, subtitle="여러 행을 묶고, 여러 표를 연결합니다",
        date_note="과제 1 (20점) — 7 · 8주차 범위, 9주차 수업 후 1주일 이내 LMS 제출"))

    # --- 1. 집계 함수
    c.add(section_slide(1, AGENDA, lead="여러 행을 하나의 숫자로 만듭니다"))
    c.add(table_slide("집계 함수", "다섯 개면 대부분의 통계가 됩니다",
        ["함수", "무엇을 구하나", "예", "NULL은"],
        [["COUNT", "개수", "COUNT(*)", "COUNT(*)는 포함, COUNT(열)은 제외"],
         ["SUM", "합계", "SUM(enrollment)", "제외하고 더함"],
         ["AVG", "평균", "AVG(enrollment)", "제외하고 나눔"],
         ["MIN / MAX", "가장 작은 / 큰 값", "MAX(start_date)", "제외"],
         ["MEDIAN", "중앙값", "MEDIAN(enrollment)", "제외"]],
        [1900000, 2800000, 3600000, 4400000], sz=1900, row_h=560000, y=1650000,
        col_algn=["ctr", "l", "l", "l"], col_font={0: "Courier New", 2: "Courier New"},
        note="집계 함수는 NULL을 빼고 계산합니다. 그래서 ‘빠진 값’이 많으면 결과가 달라집니다.",
        note_style="footnote"))
    c.add(count_slide())
    c.add(avg_median_slide())
    c.add(sql_example("비율 구하기", "퍼센트는 100.0 을 곱해서 계산합니다",
        "완료된 시험 중 결과가 게시된 비율은?",
        ["SELECT ROUND(100.0", "         * COUNT(results_first_posted_date)", "         / COUNT(*), 1) AS 결과게시율",
         "FROM studies", "WHERE overall_status = 'COMPLETED';"],
        sz=1900, result=[["결과게시율"], ["18.0"]], result_w=[6000000], request_label="자연어 요청",
        note="100 이 아니라 100.0 을 곱하는 이유: 정수끼리 나누면 소수점이 잘려 0이 나옵니다. (12주차 오류)"))
    c.add(sql_example("빈 값도 드러내기 — COALESCE", "NULL 은 이름을 붙여야 보입니다",
        "임상 단계별 건수를 보여 줘. 안 적힌 것도 같이.",
        ["SELECT COALESCE(phase, '미기재') AS 단계,", "       COUNT(*) AS 건수", "FROM studies",
         "GROUP BY 단계", "ORDER BY 건수 DESC;"],
        sz=1900,
        result=[["단계", "건수"], ["NA", "16,695"], ["미기재", "9,602"], ["PHASE2", "3,274"],
                ["PHASE1", "2,417"], ["…", "…"]],
        result_w=[3000000, 3000000], request_label="자연어 요청",
        note="phase 에는 빈 값(NULL) 9,602건과 글자 ‘NA’ 16,695건이 따로 있습니다. 둘은 다른 값입니다."))

    # --- 2. GROUP BY
    c.add(section_slide(2, AGENDA, lead="같은 값끼리 묶어서 셉니다"))
    c.add(sql_example("GROUP BY — 묶어서 세기", "결과 한 행 = 그룹 하나",
        "연구 유형별로 몇 건씩 있어?",
        ["SELECT study_type, COUNT(*) AS 건수,", "       MEDIAN(enrollment) AS 중앙값",
         "FROM studies", "GROUP BY study_type", "ORDER BY 건수 DESC;"],
        sz=1900,
        result=[["study_type", "건수", "중앙값"],
                ["INTERVENTIONAL", "27916", "60"], ["OBSERVATIONAL", "9593", "140"]],
        result_w=[2800000, 1600000, 1600000], request_label="자연어 요청",
        note="묶는 열(study_type)은 SELECT에도 적어야 결과를 읽을 수 있습니다."))
    c.add(sql_example("GROUP BY — 연도별 추이", "날짜에서 연도만 뽑아 묶습니다",
        "연도별로 시작한 시험이 몇 건이야?",
        ["SELECT YEAR(start_date) AS 시작연도,", "       COUNT(*) AS 건수", "FROM studies",
         "GROUP BY 시작연도", "ORDER BY 시작연도;"],
        sz=1900,
        result=[["시작연도", "건수"], ["2015", "2742"], ["2016", "2979"], ["2017", "3040"], ["2018", "3290"], ["…", "…"]],
        result_w=[3000000, 3000000], request_label="자연어 요청",
        note="YEAR(날짜) = 날짜에서 연도만 꺼내는 함수. 월은 MONTH(날짜), 연월은 strftime(날짜, '%Y-%m') 입니다."))
    c.add(sql_example("두 열로 묶기 — 교차표 만들기", "GROUP BY 에 열을 더 적으면 됩니다",
        "최근 2년, 연도별 · 연구 유형별 건수는?",
        ["SELECT YEAR(start_date) AS 연도,", "       study_type AS 유형,", "       COUNT(*) AS 건수",
         "FROM studies", "WHERE start_date >= '2023-01-01'", "GROUP BY 연도, 유형",
         "ORDER BY 연도, 유형;"],
        sz=1800,
        result=[["연도", "유형", "건수"], ["2023", "INTERVENTIONAL", "3,295"],
                ["2023", "OBSERVATIONAL", "1,124"], ["2024", "INTERVENTIONAL", "3,381"],
                ["2024", "OBSERVATIONAL", "1,049"]],
        result_w=[1300000, 3300000, 1400000], request_label="자연어 요청",
        note="묶는 열을 여러 개 적으면 결과 한 행은 ‘연도 + 유형’ 조합 하나가 됩니다."))
    c.add(sql_example("CASE WHEN — 조건에 따라 나누어 세기", "엑셀의 IF 와 같은 일을 합니다",
        "등록 인원을 소 · 중 · 대규모로 나누어 세어 줘",
        ["SELECT CASE WHEN enrollment < 50",
         "            THEN '소규모'",
         "            WHEN enrollment < 500",
         "            THEN '중규모'",
         "            ELSE '대규모'",
         "       END AS 규모,",
         "       COUNT(*) AS 건수",
         "FROM studies",
         "WHERE enrollment IS NOT NULL",
         "GROUP BY 규모;"],
        sz=1700,
        result=[["규모", "건수"], ["중규모", "18,968"], ["소규모", "14,003"], ["대규모", "4,536"]],
        result_w=[3000000, 3000000], request_label="자연어 요청",
        note="위에서부터 차례로 맞는 조건을 찾고, 맞으면 거기서 멈춥니다. 어디에도 안 맞으면 ELSE."))
    c.add(table_slide("CASE WHEN 을 병원에서 쓰는 곳", "구간으로 나누기와 조건부로 세기",
        ["하려는 일", "이렇게 적습니다"],
        [["나이를 연령대로 묶기", "CASE WHEN 나이 < 40 THEN '39세 이하'\n     WHEN 나이 < 65 THEN '40~64세'\n     ELSE '65세 이상' END"],
         ["검사값을 정상 · 이상으로", "CASE WHEN 수치 BETWEEN 하한 AND 상한 THEN '정상'\n     ELSE '이상' END"],
         ["조건에 맞는 것만 세기", "COUNT(CASE WHEN 재입원 = 'Y' THEN 1 END)"],
         ["분모와 분자를 한 번에", "COUNT(*) AS 분모,\nCOUNT(CASE WHEN 충족 = 'Y' THEN 1 END) AS 분자"]],
        [3600000, 7600000], sz=1800, row_h=880000, y=1700000,
        col_algn=["l", "l"], col_font={1: "Courier New"},
        note="지표 충족률처럼 분모와 분자를 한 번에 세면 조건이 어긋나지 않습니다. (9주차 · 13주차에서 다시 씁니다)",
        note_style="footnote"))

    # --- 3. HAVING과 실행 순서
    c.add(section_slide(3, AGENDA, lead="묶은 뒤의 결과에 조건을 겁니다"))
    c.add(table_slide("SELECT 문의 절", "여섯 개의 절이 각각 하는 일",
        ["절", "하는 일", "예"],
        [["SELECT", "볼 열과 집계를 고른다", "SELECT phase, COUNT(*)"],
         ["FROM", "어느 표에서 가져올지 정한다", "FROM studies"],
         ["WHERE", "행을 걸러낸다 (묶기 전)", "WHERE enrollment >= 100"],
         ["GROUP BY", "같은 값끼리 묶는다", "GROUP BY phase"],
         ["HAVING", "묶은 결과를 걸러낸다", "HAVING COUNT(*) >= 10"],
         ["ORDER BY", "정렬한다", "ORDER BY COUNT(*) DESC"]],
        [2200000, 4600000, 5300000], sz=2000, row_h=620000, y=1700000,
        col_algn=["l", "l", "l"], col_font={0: "Courier New", 2: "Courier New"},
        note="적는 순서는 이 차례지만, 실제로 처리되는 순서는 다릅니다. 다음 장에서 봅니다."))
    c.add(exec_order_slide())
    c.add(clause_order_exercise_slide())
    c.add(sql_example("HAVING — 집계 결과에 조건", "WHERE는 묶기 전, HAVING은 묶은 뒤",
        "시험이 2000건 이상인 국가만 보여 줘",
        ["SELECT name AS 국가,", "       COUNT(DISTINCT nct_id) AS 시험수", "FROM countries",
         "WHERE removed = false", "GROUP BY name", "HAVING COUNT(DISTINCT nct_id) >= 2000",
         "ORDER BY 시험수 DESC;"],
        sz=1900,
        result=[["국가", "시험수"], ["United States", "10843"], ["China", "3977"], ["France", "2775"]],
        result_w=[3400000, 2600000], request_label="자연어 요청",
        note="WHERE removed = false 는 묶기 전에 제외된 국가 행을 빼는 조건입니다."))
    c.add(checkpoint_slide(
        ["**COUNT(*)** 와 **COUNT(DISTINCT 열)** 은 다르다",
         "치우친 값은 **평균과 중앙값을 함께** 본다",
         "**WHERE는 묶기 전**, **HAVING은 묶은 뒤** 조건"],
        question="“국가별 시험 수가 1000건 이상인 곳”은 어디에 조건을 쓸까요?",
        answer="HAVING 입니다. 묶어서 센 결과(COUNT)에 대한 조건이기 때문입니다."))

    # --- 4. JOIN
    c.add(section_slide(4, AGENDA, lead="정규화로 나눈 표를 다시 붙입니다"))
    c.add(join_why_slide())
    c.add(sql_example("JOIN — 두 표 연결하기", "질환별 시험 수 구하기",
        "뇌졸중 · 고혈압 · 천식은 각각 시험이 몇 건이야?",
        ["SELECT b.mesh_term AS 질환,",
         "       COUNT(DISTINCT s.nct_id) AS 시험수",
         "FROM studies AS s",
         "JOIN browse_conditions AS b ON s.nct_id = b.nct_id",
         "WHERE b.mesh_term IN ('Stroke', 'Hypertension', 'Asthma')",
         "GROUP BY b.mesh_term", "ORDER BY 시험수 DESC;"],
        sz=1700,
        result=[["질환", "시험수"], ["Stroke", "1674"], ["Hypertension", "946"], ["Asthma", "563"]],
        result_w=[3400000, 2600000], request_label="자연어 요청",
        note="질환 이름은 conditions(연구자 입력)가 아니라 browse_conditions 를 씁니다.\nMeSH = 의학 주제어 표준 목록. 같은 질환을 한 이름으로 부르기 위한 것입니다 (14주차 표준 용어)."))
    c.add(join_kind_slide())
    c.add(sql_example("JOIN 뒤에는 행 수를 확인", "한 시험에 질환이 여러 개 붙어 있습니다",
        "JOIN하면 행이 몇 개가 되지?",
        ["SELECT COUNT(*) AS JOIN후_행수,", "       COUNT(DISTINCT s.nct_id) AS 시험수",
         "FROM studies AS s", "JOIN browse_conditions AS b", "  ON s.nct_id = b.nct_id;"],
        sz=1900,
        result=[["JOIN후_행수", "시험수"], ["309,124", "31,634"]], result_w=[3000000, 3000000],
        request_label="자연어 요청",
        note="행이 약 10배로 늘었습니다. 이 상태에서 COUNT(*)를 세면 시험 수가 아니라 (시험 × 질환) 쌍의 수입니다."))

    # --- 5. 자주 하는 실수
    c.add(section_slide(5, AGENDA, lead="오류가 안 나는 실수가 더 위험합니다"))
    c.add(mistake_slide(1, "GROUP BY에 없는 열",
        ["SELECT phase, overall_status,", "       COUNT(*)", "FROM studies", "GROUP BY phase"],
        "Binder Error: column \"overall_status\" must appear\nin the GROUP BY clause",
        ["SELECT phase, overall_status,", "       COUNT(*)", "FROM studies", "GROUP BY phase, overall_status"],
        "묶는 열이 아니면 집계 함수로 감싸거나 GROUP BY에 넣습니다."))
    c.add(mistake_slide(2, "WHERE에 집계 함수",
        ["SELECT phase, COUNT(*)", "FROM studies", "WHERE COUNT(*) > 1000", "GROUP BY phase"],
        "Binder Error: aggregate function ... not allowed in WHERE\nWHERE는 묶기 전이라 COUNT를 모릅니다.",
        ["SELECT phase, COUNT(*)", "FROM studies", "GROUP BY phase", "HAVING COUNT(*) > 1000"],
        "집계에 대한 조건은 HAVING에 씁니다."))
    c.add(mistake_slide(3, "JOIN 뒤 COUNT(*)를 시험 수로 착각",
        ["SELECT COUNT(*) AS 한국시험수", "FROM studies AS s", "JOIN facilities AS f", "  ON s.nct_id = f.nct_id",
         "WHERE f.country = 'South Korea'"],
        "결과 4,098 — 오류는 없지만 이것은 기관 수입니다.\n한 시험이 여러 기관에서 진행되기 때문입니다.",
        ["SELECT COUNT(DISTINCT s.nct_id)", "         AS 한국시험수", "FROM studies AS s", "JOIN facilities AS f",
         "  ON s.nct_id = f.nct_id", "WHERE f.country = 'South Korea'"],
        "결과 1,182 — 실제 시험 수입니다. COUNT(DISTINCT 키)를 씁니다.", danger=True))
    c.add(content("집계와 JOIN을 쓸 때의 확인 습관", [
        ("① **무엇을 세는지 말로 정한다**", dict()),
        ("“시험 건수”인가 “기관 수”인가 “질환 쌍의 수”인가", dict(lvl=1, sz=2200)),
        ("② **JOIN 전후의 행 수를 비교한다**", dict()),
        ("COUNT(*) 와 COUNT(DISTINCT 키) 를 같이 본다", dict(lvl=1, sz=2200)),
        ("③ **분모가 줄지 않았는지 본다**", dict()),
        ("INNER JOIN 때문에 빠진 행이 있는지 LEFT JOIN으로 확인", dict(lvl=1, sz=2200)),
        ("④ **평균은 중앙값과 함께 본다**", dict()),
        ("극단값 하나가 결과를 바꿀 수 있다", dict(lvl=1, sz=2200)),
    ], subtitle="이 네 가지만 지켜도 대부분의 오류를 막습니다"))

    # --- 6. 정리
    c.add(section_slide(6, AGENDA, lead="오늘 나온 용어와 핵심을 다시 짚습니다"))
    c.add(content("오늘의 실습과 과제 안내", [
        ("**오늘 실습**: 노트북 `08_실습_집계와JOIN.ipynb`", dict()),
        ("집계 함수 → GROUP BY → COALESCE · CASE WHEN → HAVING → JOIN 순서로 따라 합니다", dict(lvl=1, sz=2200)),
        ("마지막 ‘자주 하는 실수’ 다섯 가지는 오류 메시지를 직접 보는 것이 목적입니다", dict(lvl=1, sz=2200)),
        ("점수는 없습니다. 7주차 노트북과 같은 방식으로 진행합니다.", dict(lvl=1, sz=2200)),
        ("**과제 1 (20점) — 7 · 8주차 범위, 9주차 수업 후 1주일 이내 LMS 제출**", dict(spcBef=16)),
        ("오늘까지 배운 SELECT · WHERE · 집계 · GROUP BY · JOIN 이 범위입니다", dict(lvl=1, sz=2200)),
        ("다음 주에 문항을 함께 훑고 막히는 부분을 먼저 풀어 봅니다", dict(lvl=1, sz=2200)),
    ], subtitle="실습 노트북과 과제 1"))
    c.add(terms_slide(8, [
        ["집계 함수", "Aggregate Function", "여러 행을 하나의 값으로 만드는 함수"],
        ["COUNT(*)", "—", "모든 행의 수 (NULL 포함)"],
        ["COUNT(DISTINCT 열)", "—", "서로 다른 값의 개수"],
        ["MEDIAN", "—", "중앙값. 가운데 값이라 극단값에 덜 흔들림"],
        ["GROUP BY", "—", "같은 값끼리 묶는 절. 결과 1행 = 그룹 1개"],
        ["CASE WHEN", "—", "조건에 따라 다른 값을 내놓기. 엑셀의 IF와 같음"],
        ["COALESCE", "—", "빈 값(NULL)을 정해 둔 값으로 바꾸기"],
        ["HAVING", "—", "묶은 뒤의 그룹에 조건을 거는 절"],
        ["JOIN", "INNER JOIN", "양쪽에 모두 있는 행만 연결"],
        ["LEFT JOIN", "—", "왼쪽 표는 모두 남기고 연결"],
        ["ON", "—", "두 표를 어떤 열로 맞출지 적는 부분"],
        ["별칭", "Alias", "표나 열에 짧은 이름 붙이기 (AS)"],
    ]))
    c.add(summary(8, [
        "**GROUP BY** 결과의 한 행이 무엇인지 말로 확인한다",
        "**WHERE는 묶기 전, HAVING은 묶은 뒤** 조건이다",
        "**CASE WHEN**으로 구간을 나누고, **COALESCE**로 빈 값에 이름을 붙인다",
        "**JOIN 뒤에는 행 수가 변한다.** COUNT(DISTINCT 키)로 확인한다",
    ], sz=2600, lnSpc=155, next_week="9강. 의료데이터 SQL 종합실습 — 분석 질문을 SQL로 바꾸기, 과제 1 제출"))
