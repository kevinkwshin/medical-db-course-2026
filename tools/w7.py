# -*- coding: utf-8 -*-
"""7강. SQL (1) — 조회 기초 (원본 108~114번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)

SPAN = (108, 114)
TITLE = "7강. SQL (1)"

AGENDA = [("실습 환경", "Colab과 aact_mini"),
          ("SELECT · FROM", "필요한 열 고르기"),
          ("WHERE", "필요한 행 고르기"),
          ("정렬과 중복 제거", "ORDER BY · DISTINCT"),
          ("자주 하는 실수", "오류 메시지 읽기"),
          ("정리", "용어와 요약")]


def env_slide():
    def b(ids):
        s = step_row(ids, X0, 1600000, W0, 1100000,
                     [("① 노트북 열기", "Colab 링크 클릭"), ("② 준비 셀 실행", "데이터 자동 연결"),
                      ("③ SQL 작성", "%%sql 셀에 입력"), ("④ 결과 확인", "표로 바로 출력")], sz=1900)
        s += panel(ids, X0, 3050000, 6000000, 2500000, "무엇을 설치하나요", [
            "아무것도 설치하지 않습니다",
            "- Google 계정으로 Colab 접속",
            "- 준비 셀이 데이터 파일을 받아 연결",
            "- 실습은 웹 브라우저에서만 진행",
            "- 집 컴퓨터에서도 같은 링크로 가능"], fill="DEEAF6", line="1F497D", sz=1800)
        s += panel(ids, 7300000, 3050000, 6000000, 2500000, "무엇을 쓰나요", [
            "DuckDB — 파일 하나로 된 관계형 DBMS",
            "- 문법은 PostgreSQL과 거의 같음",
            "- 실무에서 쓰는 SQL 그대로 연습",
            "jupysql — 노트북에서 SQL을 쓰는 도구",
            "- %%sql 로 시작하는 칸에 SQL만 입력"], fill="E2EFDA", line="2C5F2D", sz=1800)
        s += textbox(ids, X0, 5750000, W0, 900000,
            para("데이터는 **읽기 전용**으로 엽니다. 실수로 지우거나 바꿀 수 없습니다.", sz=2300, b=True, algn="ctr", lnSpc=115) +
            para("(데이터를 바꾸는 명령은 10주차에서 다룹니다.)", sz=2100, algn="ctr", lnSpc=115, color="1F3763"))
        return s
    return free("실습 환경", b, subtitle="설치 없이 웹 브라우저에서 SQL을 씁니다")


def data_slide():
    return table_slide("실습 데이터 — aact_mini", "임상시험 등록 자료에서 추린 수업용 데이터베이스",
        ["테이블", "한 행이 뜻하는 것", "행 수", "오늘 쓰는 열"],
        [["studies", "임상시험 1건", "37,509", "nct_id, brief_title, start_date,\noverall_status, phase, enrollment"],
         ["conditions", "대상 질환 1개", "73,173", "nct_id, name"],
         ["eligibilities", "선정 · 제외 기준", "37,509", "nct_id, gender, minimum_age"],
         ["sponsors", "스폰서 1곳", "62,783", "nct_id, agency_class, name"],
         ["facilities", "수행 기관 1곳", "208,690", "nct_id, name, country"],
         ["browse_conditions", "표준 질환명 1개", "309,124", "nct_id, mesh_term"],
         ["countries", "참여 국가 1곳", "50,410", "nct_id, name, removed"]],
        [2600000, 3200000, 1600000, 5200000], sz=1700, row_h=560000, y=1620000,
        col_algn=["l", "l", "ctr", "l"], col_font={0: "Courier New", 3: "Courier New"},
        note="오늘은 studies 한 표만 씁니다. 여러 표를 연결하는 것은 8주차 JOIN에서 배웁니다.",
        note_style="footnote")


def clause_slide():
    def b(ids):
        s = ""
        rows = [("SELECT", "무엇을 볼지 (열)", "nct_id, brief_title", "DEEAF6"),
                ("FROM", "어디에서 (테이블)", "studies", "FFF2CC"),
                ("WHERE", "어떤 행만 (조건)", "phase = 'PHASE3'", "E2EFDA"),
                ("ORDER BY", "어떤 순서로 (정렬)", "start_date DESC", "F2F2F2"),
                ("LIMIT", "몇 줄만 (개수)", "10", "F2F2F2")]
        y, h, gap = 1700000, 780000, 130000
        for i, (kw, what, ex, fill) in enumerate(rows):
            s += shape(ids, "rect", X0, y, 2600000, h, fill=fill, line="7F7F7F",
                       text_xml=para(f"**{kw}**", sz=2400, algn="ctr", color=BLUE, font="Courier New", lnSpc=100), name="KW")
            s += shape(ids, "rect", X0 + 2600000, y, 3600000, h, fill="FFFFFF", line="7F7F7F",
                       text_xml=para(what, sz=2100, lnSpc=100, marL=200000), name="What")
            s += shape(ids, "rect", X0 + 6200000, y, 4200000, h, fill="FFFFFF", line="7F7F7F",
                       text_xml=para(ex, sz=1900, lnSpc=100, marL=200000, font="Courier New"), name="Ex")
            y += h + gap
        s += textbox(ids, 11300000, 1750000, 2000000, 4300000,
            para("**순서가\n정해져\n있습니다**", sz=2200, b=True, algn="ctr", color=RED, lnSpc=125) +
            para("바꿔 쓰면\n문법 오류", sz=2000, algn="ctr", lnSpc=125, color=GRAY, spcBef=14), autofit=False)
        s += textbox(ids, X0, 6300000, W0, 600000,
            para("SELECT → FROM → WHERE → ORDER BY → LIMIT", sz=2600, b=True, algn="ctr", color=BLUE, lnSpc=110))
        return s
    return free("SQL 문장의 구조", b, subtitle="다섯 부분을 순서대로 적습니다")


def mistake_slide(no, title_txt, bad_sql, bad_why, good_sql, good_why, danger=False, lesson=None):
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para(("**오류가 나지 않아 더 위험합니다.**" if danger else "실행하면 오류 메시지가 나옵니다."),
                 sz=2200, b=danger, color=(RED if danger else "1F3763"), lnSpc=115))
        y = 2150000
        s += shape(ids, "rect", X0, y, 6000000, 480000, fill="C00000", line="C00000",
                   text_xml=para("이렇게 쓰면", sz=2100, algn="ctr", color="FFFFFF", lnSpc=100), name="Bad Head")
        bh = 380000 * len(bad_sql) + 300000
        s += shape(ids, "roundRect", X0, y + 480000, 6000000, bh, fill="FBE5E5", line="C00000", name="Bad")
        s += textbox(ids, X0 + 200000, y + 620000, 5600000, bh - 200000,
                     "".join(para(l, sz=2000, lnSpc=110, sql=True) for l in bad_sql), autofit=False)
        s += textbox(ids, X0, y + 480000 + bh + 150000, 6000000, 900000,
                     para(bad_why, sz=2000, lnSpc=120, color="C00000"))
        s += shape(ids, "rect", 7300000, y, 6000000, 480000, fill="2C5F2D", line="2C5F2D",
                   text_xml=para("이렇게 고칩니다", sz=2100, algn="ctr", color="FFFFFF", lnSpc=100), name="Good Head")
        gh = 380000 * len(good_sql) + 300000
        s += shape(ids, "roundRect", 7300000, y + 480000, 6000000, gh, fill="E2EFDA", line="2C5F2D", name="Good")
        s += textbox(ids, 7500000, y + 620000, 5600000, gh - 200000,
                     "".join(para(l, sz=2000, lnSpc=110, sql=True) for l in good_sql), autofit=False)
        s += textbox(ids, 7300000, y + 480000 + gh + 150000, 6000000, 900000,
                     para(good_why, sz=2000, lnSpc=120, color="2C5F2D"))
        if lesson:
            s += textbox(ids, X0, 6250000, W0, 600000,
                         para(lesson, sz=2300, b=True, algn="ctr", lnSpc=115))
        return s
    return free(f"자주 하는 실수 {no} — {title_txt}", b, subtitle=None)


def build(c):
    # --- 도입
    c.add(cover(7, "SQL (1) 조회 기초",
                ["SELECT · FROM · WHERE", "비교 · IN · BETWEEN · LIKE · IS NULL", "ORDER BY · DISTINCT · LIMIT"],
                "2026. 10. 27."))
    c.add(content("지난시간 리뷰", [
        ("**ERD**로 개체 · 속성 · 관계를 그리고 표로 옮긴다", dict(lvl=1, marL=457200, indent=-457200)),
        ("**정규화** = 이상현상을 없애려고 딸린 열을 떼어 표를 나누는 것", dict(lvl=1, marL=457200, indent=-457200)),
        ("**기본키**로 행을 찾고, **외래키**로 표를 연결한다 (5주차)", dict(lvl=1, marL=457200, indent=-457200)),
        ("이제 만들어진 표에서 **원하는 데이터를 꺼내는 방법**을 배웁니다.", dict(b=True, algn="ctr", color=BLUE, spcBef=24)),
        ("오늘부터 4주 동안 SQL을 직접 씁니다.", dict(b=True, algn="ctr", color=BLUE)),
    ]))
    c.add(objectives_slide(7,
        ["실습 환경에서 SQL을 실행하고 결과를 볼 수 있다",
         "SELECT · FROM으로 필요한 열만 조회할 수 있다",
         "WHERE로 조건에 맞는 행만 고를 수 있다",
         "오류 메시지를 읽고 잘못된 부분을 고칠 수 있다"],
        AGENDA, subtitle="데이터베이스에서 원하는 데이터를 꺼내는 방법",
        date_note="과제 1 (20점) — 7 · 8주차 범위, 9주차 수업 후 1주일 이내 LMS 제출"))

    # --- 1. 실습 환경
    c.add(section_slide(1, AGENDA, lead="먼저 실습 준비부터 합니다"))
    c.add(content("우리가 SQL을 직접 쓰는 이유", [
        ("① 평소 진료에서는 **EMR 프로그램**이 SQL을 대신 만들어 줍니다.", dict()),
        ("화면의 버튼을 누르면 정해진 조회만 됩니다.", dict(lvl=1, sz=2200)),
        ("② 그런데 연구 · 통계는 **매번 조건이 다릅니다.**", dict()),
        ("“작년에 65세 이상 당뇨 환자 중 재입원한 사람” 같은 질문", dict(lvl=1, sz=2200)),
        ("③ 이런 질문은 화면에 버튼이 없습니다. **직접 SQL로 물어봐야** 합니다.", dict()),
        ("논문 · 적정성평가 · QI 보고서의 숫자가 대부분 이렇게 나옵니다.", dict(lvl=1, sz=2200)),
        ("SQL은 국제 표준이라 한 번 배우면 Oracle · MS SQL · PostgreSQL에서 거의 그대로 씁니다.",
         dict(b=True, algn="ctr", color=BLUE, spcBef=20)),
    ], subtitle="버튼으로 안 되는 질문에 답하기 위해"))
    c.add(env_slide())
    c.add(data_slide())

    # --- 2. SELECT · FROM
    c.add(section_slide(2, AGENDA, lead="어떤 열을 볼지 고릅니다"))
    c.add(clause_slide())
    c.add(sql_example("SELECT · FROM", "가장 기본이 되는 두 줄",
        "임상시험의 등록번호와 제목을 보여 줘",
        ["SELECT nct_id, brief_title", "FROM studies", "LIMIT 3;"],
        result=[["nct_id", "brief_title"],
                ["NCT00455039", "INST 0514C- Biologic Correlative …"],
                ["NCT00589043", "Computed Tomography Laser Mammo…"],
                ["NCT00593164", "Clinical Study of the LRS Thermo…"]],
        result_w=[2100000, 3900000], request_label="자연어 요청",
        note="LIMIT 3 은 앞에서 3줄만 보라는 뜻입니다. 큰 표를 처음 볼 때 꼭 붙입니다."))
    c.add(sql_example("전체 열 보기와 개수 세기", "별표(*)는 모든 열, COUNT(*)는 행 수",
        "이 표에 행이 몇 개나 있어?",
        ["SELECT COUNT(*) AS 시험수", "FROM studies;"],
        result=[["시험수"], ["37509"]], result_w=[6000000], request_label="자연어 요청",
        note="SELECT * FROM studies; 는 모든 열을 봅니다. 열이 30개가 넘으므로 필요한 열만 적는 편이 읽기 쉽습니다."))
    c.add(sql_example("AS — 결과 열 이름 바꾸기", "보고서에 그대로 쓸 수 있게 이름을 붙입니다",
        "등록번호와 등록인원을 한글 이름으로 보여 줘",
        ["SELECT nct_id AS 등록번호,", "       enrollment AS 등록인원", "FROM studies", "LIMIT 3;"],
        result=[["등록번호", "등록인원"], ["NCT00455039", "0"], ["NCT00589043", "600"], ["NCT00593164", "0"]],
        result_w=[3000000, 3000000], request_label="자연어 요청",
        note="AS 는 생략할 수 있지만, 적어 두면 나중에 읽기 훨씬 좋습니다."))

    # --- 3. WHERE
    c.add(section_slide(3, AGENDA, lead="필요한 행만 남깁니다"))
    c.add(table_slide("WHERE 조건에 쓰는 기호", "조건은 이 여섯 가지 모양이면 거의 다 됩니다",
        ["종류", "쓰는 법", "예", "뜻"],
        [["비교", "= , <> , > , >= , < , <=\n(<> 는 ‘같지 않다’)", "enrollment >= 1000", "등록인원 1000명 이상"],
         ["여러 조건", "AND , OR , NOT", "A AND B", "두 조건을 모두 만족"],
         ["목록", "IN (값1, 값2)", "phase IN ('PHASE3','PHASE4')", "여러 값 중 하나"],
         ["범위", "BETWEEN a AND b", "start_date BETWEEN '2024-01-01'\nAND '2024-12-31'", "양 끝을 포함한 범위"],
         ["글자", "LIKE '%글자%'", "brief_title LIKE '%Nurs%'", "그 글자가 들어간 것"],
         ["빈 값", "IS NULL / IS NOT NULL", "results_first_posted_date IS NULL", "값이 없는 / 있는 행"]],
        [1500000, 3700000, 4500000, 2800000], sz=1700, row_h=560000, y=1620000,
        col_algn=["ctr", "l", "l", "l"], col_font={1: "Courier New", 2: "Courier New"},
        note="문자와 날짜는 반드시 '작은따옴표'로 감쌉니다. 숫자는 따옴표 없이 씁니다.",
        note_style="footnote"))
    c.add(sql_example("WHERE — 조건 하나", "완료된 시험만 보기",
        "완료(COMPLETED)된 시험이 몇 건이야?",
        ["SELECT COUNT(*) AS 완료시험", "FROM studies", "WHERE overall_status = 'COMPLETED';"],
        result=[["완료시험"], ["19622"]], result_w=[6000000], request_label="자연어 요청",
        note="전체 37,509건 중 19,622건입니다. 문자 값 'COMPLETED' 는 작은따옴표로 감쌉니다."))
    c.add(sql_example("WHERE — 조건 두 개 (AND)", "조건을 하나씩 더해 갑니다",
        "2024년에 시작한 3상 시험을 보여 줘",
        ["SELECT nct_id, start_date, phase", "FROM studies",
         "WHERE start_date BETWEEN '2024-01-01'",
         "                    AND '2024-12-31'",
         "  AND phase = 'PHASE3'", "ORDER BY start_date DESC", "LIMIT 3;"],
        sz=2000,
        result=[["nct_id", "start_date", "phase"],
                ["NCT05911061", "2024-12-30", "PHASE3"],
                ["NCT06716970", "2024-12-30", "PHASE3"],
                ["NCT06702878", "2024-12-27", "PHASE3"]],
        result_w=[2200000, 2000000, 1800000], request_label="자연어 요청",
        note="조건을 하나씩 추가하면서 건수가 어떻게 줄어드는지 확인하는 습관이 중요합니다."))
    c.add(sql_example("IN · BETWEEN · LIKE", "값의 목록 · 범위 · 글자 찾기",
        "제목에 Nurs 가 들어간 시험은 몇 건이야?",
        ["SELECT COUNT(*) AS 간호관련", "FROM studies", "WHERE brief_title LIKE '%Nurs%';"],
        result=[["간호관련"], ["187"]], result_w=[6000000], request_label="자연어 요청",
        note="% 는 아무 글자가 몇 개든 온다는 뜻입니다. LIKE 는 대소문자를 구분하므로 ILIKE 도 함께 기억하세요."))
    c.add(sql_example("IS NULL — 값이 없는 행 찾기", "5주차의 NULL이 여기서 쓰입니다",
        "완료됐는데 결과가 게시되지 않은 시험은?",
        ["SELECT COUNT(*) AS 결과없음", "FROM studies", "WHERE overall_status = 'COMPLETED'",
         "  AND results_first_posted_date IS NULL;"],
        sz=2000, result=[["결과없음"], ["16098"]], result_w=[6000000], request_label="자연어 요청",
        note="완료된 19,622건 중 16,098건(82%)에 결과가 없습니다. = NULL 로 쓰면 오류 없이 0이 나오니 주의하세요."))
    c.add(checkpoint_slide(
        ["**SELECT · FROM** = 어떤 열을, 어느 표에서",
         "**WHERE** = 어떤 행만. 문자 · 날짜는 '작은따옴표'",
         "**IS NULL** 로 빈 값을 찾는다 (= NULL 은 안 됨)"],
        question="2024년에 시작한 시험만 보려면 어떤 절을 쓸까요?",
        answer="WHERE start_date >= '2024-01-01' AND start_date <= '2024-12-31' 또는 BETWEEN 을 씁니다."))

    # --- 4. 정렬과 중복 제거
    c.add(section_slide(4, AGENDA, lead="결과를 보기 좋게 정리합니다"))
    c.add(sql_example("ORDER BY — 정렬", "큰 값부터, 또는 최근 순으로",
        "등록인원이 가장 많은 시험 3건을 보여 줘",
        ["SELECT nct_id, enrollment", "FROM studies", "ORDER BY enrollment DESC", "LIMIT 3;"],
        result=[["nct_id", "enrollment"], ["NCT05697705", "188,814,085"],
                ["NCT05222750", "41,200,246"], ["NCT05853536", "13,977,257"]],
        result_w=[3000000, 3000000], request_label="자연어 요청",
        note="1억 8천만 명은 실제 등록 인원일 수 없습니다. 정렬은 이런 이상한 값을 찾는 데도 씁니다. (12주차)"))
    c.add(sql_example("DISTINCT — 값의 종류 보기", "이 열에 어떤 값들이 있는지 먼저 확인합니다",
        "진행 상태에 어떤 값들이 있어?",
        ["SELECT DISTINCT overall_status", "FROM studies", "ORDER BY overall_status;"],
        result=[["overall_status"], ["ACTIVE_NOT_RECRUITING"], ["COMPLETED"], ["ENROLLING_BY_INVITATION"],
                ["NOT_YET_RECRUITING"], ["RECRUITING"], ["…  (모두 9가지)"]],
        result_w=[6000000], request_label="자연어 요청",
        note="WHERE 조건을 쓰기 전에 DISTINCT 로 값의 종류를 먼저 보면 오타와 빈 결과를 막을 수 있습니다."))

    # --- 5. 자주 하는 실수
    c.add(section_slide(5, AGENDA, lead="오류는 잘못이 아니라 안내문입니다"))
    c.add(mistake_slide(1, "= NULL", ["WHERE results_first_posted_date = NULL"],
        "오류가 나지 않고 결과가 0행으로 나옵니다.\nNULL은 ‘같다/다르다’로 비교할 수 없기 때문입니다.",
        ["WHERE results_first_posted_date IS NULL"],
        "IS NULL 을 씁니다. 반대는 IS NOT NULL 입니다.", danger=True,
        lesson="결과가 0행이면 “없다”가 아니라 “조건이 틀렸다”를 먼저 의심하세요."))
    c.add(mistake_slide(2, "작은따옴표 빠뜨림", ["WHERE overall_status = COMPLETED"],
        "Referenced column \"COMPLETED\" not found\nCOMPLETED 를 열 이름으로 읽습니다.",
        ["WHERE overall_status = 'COMPLETED'"],
        "문자 값은 '작은따옴표'로 감쌉니다. 큰따옴표는 열 이름을 뜻합니다.",
        lesson="오류 메시지의 Candidate bindings 목록이 비슷한 열 이름을 알려 줍니다."))
    c.add(mistake_slide(3, "절의 순서를 바꿈", ["SELECT nct_id", "FROM studies", "LIMIT 5", "ORDER BY start_date"],
        "Parser Error: syntax error at or near \"ORDER\"\n순서가 정해져 있습니다.",
        ["SELECT nct_id", "FROM studies", "ORDER BY start_date", "LIMIT 5"],
        "SELECT → FROM → WHERE → ORDER BY → LIMIT 순서를 지킵니다.",
        lesson="절의 순서는 외우는 것이 아니라 “무엇을 · 어디서 · 어떤 행만 · 어떤 순서로 · 몇 줄”로 읽으면 됩니다."))
    c.add(mistake_slide(4, "대소문자", ["WHERE brief_title LIKE '%covid%'"],
        "6건만 나옵니다.\n대소문자를 가리지 않고 세면 2,125건입니다.",
        ["WHERE brief_title ILIKE '%covid%'"],
        "ILIKE 는 대소문자를 구분하지 않습니다. UPPER() 를 써도 됩니다.", danger=True,
        lesson="조건을 쓰기 전에 DISTINCT 로 실제 값의 모양을 먼저 확인하세요."))
    c.add(content("오류 메시지 읽는 법", [
        ("① 붉은 글씨가 길게 나와도 **전부 읽지 않아도 됩니다.**", dict()),
        ("② `Original error message from DB driver:` **아래 한 줄**이 진짜 원인입니다.", dict()),
        ("③ 자주 보는 세 가지", dict()),
        ("Referenced column \"…\" not found  → 열 이름 오타 또는 따옴표 누락", dict(lvl=1, sz=2100, font="Courier New")),
        ("Parser Error: syntax error near \"…\"  → 절의 순서나 쉼표 문제", dict(lvl=1, sz=2100, font="Courier New")),
        ("Conversion Error / Cannot compare  → 타입이 맞지 않음 (5주차)", dict(lvl=1, sz=2100, font="Courier New")),
        ("④ 오류가 **안 나는데 결과가 이상한 경우**가 가장 위험합니다. 건수를 항상 확인하세요.",
         dict(b=True, color=RED, spcBef=18)),
    ], subtitle="어디를 봐야 하는지만 알면 됩니다"))

    # --- 6. 정리
    c.add(section_slide(6, AGENDA, lead="오늘 나온 용어와 핵심을 다시 짚습니다"))
    c.add(content("오늘의 실습과 과제 안내", [
        ("**오늘 실습**: 노트북 `07_실습_SQL기초.ipynb`", dict()),
        ("따라 하기 → 자주 하는 실수 → 직접 해보기 8문항", dict(lvl=1, sz=2200)),
        ("각 문항 아래 `check(\"Q1\", _)` 를 실행하면 정답 여부가 바로 표시됩니다", dict(lvl=1, sz=2200)),
        ("점수는 없습니다. 끝까지 해 보는 것이 목표입니다.", dict(lvl=1, sz=2200)),
        ("**과제 1 (20점) — 7 · 8주차 범위, 9주차 수업 후 1주일 이내 LMS 제출**", dict(spcBef=16)),
        ("오늘 배운 SELECT · WHERE 와 8주차의 집계 · JOIN 이 범위입니다", dict(lvl=1, sz=2200)),
        ("학번에 따라 분석할 질환이 다르게 배정됩니다", dict(lvl=1, sz=2200)),
        ("노트북 파일 하나를 제출합니다", dict(lvl=1, sz=2200)),
    ], subtitle="실습 노트북과 과제 1"))
    c.add(terms_slide(7, [
        ["SELECT", "—", "어떤 열을 볼지 정하는 절"],
        ["FROM", "—", "어느 테이블에서 가져올지 정하는 절"],
        ["WHERE", "—", "조건에 맞는 행만 남기는 절"],
        ["ORDER BY", "—", "결과를 정렬하는 절. DESC는 내림차순"],
        ["LIMIT", "—", "앞에서 몇 줄만 보는 절"],
        ["DISTINCT", "—", "중복을 없애고 값의 종류만 보기"],
        ["AS", "별칭 Alias", "결과 열에 다른 이름을 붙이기"],
        ["LIKE · ILIKE", "—", "글자 패턴 찾기. ILIKE는 대소문자 무시"],
        ["IS NULL", "—", "값이 비어 있는 행 찾기"],
    ], note="이 아홉 가지로 오늘 배운 조회가 전부 됩니다."))
    c.add(summary(7, [
        "**SELECT → FROM → WHERE → ORDER BY → LIMIT** 순서로 적는다",
        "문자 · 날짜는 '작은따옴표', 빈 값은 **IS NULL** 로 찾는다",
        "조건을 하나씩 더하며 **건수가 어떻게 변하는지** 확인한다",
    ], sz=2800, lnSpc=170, next_week="8강. SQL (2) — 집계(COUNT · AVG)와 GROUP BY, 그리고 JOIN"))
