# -*- coding: utf-8 -*-
"""12강. 의료데이터에서 자주 생기는 오류 (원본 149~154번 자리를 대체)"""
from deckgen import *
from wk_common import (table_slide, objectives_slide, two_panel_slide, section_slide,
                       checkpoint_slide, terms_slide, RED_PANEL, GREEN_PANEL)

SPAN = (149, 154)
TITLE = "12강. 의료데이터에서 자주 생기는 오류"

AGENDA = [("세는 단위와 JOIN", "건수가 부풀거나 줄어든다"),
          ("값의 타입과 형식", "숫자처럼 보이지만 문자"),
          ("빈 값과 코드", "NULL · 대소문자 · 표기 불일치"),
          ("시간", "기준일 이후 정보가 섞인다"),
          ("점검 체크리스트", "오류를 찾는 SQL"),
          ("정리", "과제 2와 요약")]


def error_slide(no, title_txt, situation, bad_sql, bad_result, bad_why, good_sql, good_result, good_why, lesson, sz=1900):
    """오류 사례 한 장: 병원 상황 → 잘못된 SQL/결과 → 올바른 SQL/결과 → 한 줄 교훈"""
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
                    para(f"**상황**  {situation}", sz=2200, lnSpc=115))
        y = 2050000
        hh = int(len(bad_sql) * (sz / 100) * 12700 * 1.2 + 300000)
        gh = int(len(good_sql) * (sz / 100) * 12700 * 1.2 + 300000)
        box_h = max(hh, gh)
        s += shape(ids, "rect", X0, y, 6000000, 440000, fill="C00000", line="C00000",
                   text_xml=para("이렇게 하면", sz=2000, algn="ctr", color="FFFFFF", lnSpc=100), name="BadHead")
        s += shape(ids, "roundRect", X0, y + 440000, 6000000, box_h, fill="FBE5E5", line="C00000", name="Bad")
        s += textbox(ids, X0 + 200000, y + 570000, 5600000, box_h - 150000,
                     "".join(para(l, sz=sz, lnSpc=110, sql=True) for l in bad_sql), autofit=False)
        s += textbox(ids, X0, y + 440000 + box_h + 120000, 6000000, 900000,
                     para(f"**결과** {bad_result}", sz=2000, lnSpc=118, color="C00000") +
                     para(bad_why, sz=1900, lnSpc=118, color=GRAY))
        s += shape(ids, "rect", 7300000, y, 6000000, 440000, fill="2C5F2D", line="2C5F2D",
                   text_xml=para("이렇게 고칩니다", sz=2000, algn="ctr", color="FFFFFF", lnSpc=100), name="GoodHead")
        s += shape(ids, "roundRect", 7300000, y + 440000, 6000000, box_h, fill="E2EFDA", line="2C5F2D", name="Good")
        s += textbox(ids, 7500000, y + 570000, 5600000, box_h - 150000,
                     "".join(para(l, sz=sz, lnSpc=110, sql=True) for l in good_sql), autofit=False)
        s += textbox(ids, 7300000, y + 440000 + box_h + 120000, 6000000, 900000,
                     para(f"**결과** {good_result}", sz=2000, lnSpc=118, color="2C5F2D") +
                     para(good_why, sz=1900, lnSpc=118, color=GRAY))
        s += textbox(ids, X0, 6250000, W0, 600000,
                     para(lesson, sz=2300, b=True, algn="ctr", lnSpc=115))
        return s
    return free(f"오류 {no} — {title_txt}", b, subtitle=None)


def checklist_slide():
    return table_slide("오류 점검 체크리스트", "결과를 내보내기 전에 이 표를 훑습니다",
        ["무엇을", "어떻게 확인하나", "이상하면"],
        [["세는 단위", "COUNT(*) 와 COUNT(DISTINCT 키) 비교", "DISTINCT 를 쓰거나 먼저 집계"],
         ["JOIN 후 행 수", "JOIN 전후의 행 수 비교", "1:N 관계 확인, 필요한 단위로 집계"],
         ["분모", "LEFT JOIN 으로 다시 세기", "INNER JOIN 을 LEFT JOIN 으로"],
         ["값의 타입", "DESCRIBE 로 타입 확인", "숫자형 열을 쓰거나 CAST"],
         ["빈 값", "COUNT(*) 와 COUNT(열) 비교", "NULL 처리 규칙을 정하고 기록"],
         ["표기 불일치", "DISTINCT 로 값의 종류 보기", "표준 코드 열을 사용"],
         ["이상값", "MIN · MAX · 상위 10건 보기", "원인 확인 후 제외 기준 문서화"],
         ["기준일", "기준일 이후 자료가 섞였는지", "날짜 조건을 다시 확인"]],
        [2400000, 5400000, 4400000], sz=1900, row_h=470000, y=1580000,
        col_algn=["ctr", "l", "l"],
        note="9주차 검산 다섯 가지를 실제 오류 유형에 맞춰 넓힌 것입니다.")


def finder_sql_slide():
    def b(ids):
        s = textbox(ids, X0, Y_BODY_SUB, W0, 500000,
            para("새 데이터를 받으면 **가장 먼저 돌려 보는 네 가지 조회**입니다.", sz=2300, lnSpc=115))
        items = [("① 한 행의 단위 확인", ["SELECT COUNT(*), COUNT(DISTINCT 키)", "FROM 표;"]),
                 ("② 값의 종류 확인", ["SELECT 열, COUNT(*)", "FROM 표 GROUP BY 열", "ORDER BY 2 DESC;   -- 2 = 두 번째 열"]),
                 ("③ 빈 값 비율 확인", ["SELECT COUNT(*) AS 전체,", "       COUNT(열) AS 값있음 FROM 표;"]),
                 ("④ 이상값 확인", ["SELECT MIN(열), MAX(열), AVG(열)", "FROM 표;"])]
        y, h = 1950000, 1150000
        for i, (t, sql) in enumerate(items):
            x = X0 + (i % 2) * 6500000
            yy = y + (i // 2) * (h + 350000)
            s += shape(ids, "rect", x, yy, 6000000, 420000, fill="1F497D", line="1F497D",
                       text_xml=para(f"**{t}**", sz=2000, algn="ctr", color="FFFFFF", lnSpc=100), name="Head")
            s += shape(ids, "roundRect", x, yy + 420000, 6000000, h - 420000, fill="F6F8FA", line="7F7F7F", name="SQL")
            s += textbox(ids, x + 200000, yy + 540000, 5600000, h - 480000,
                         "".join(para(l, sz=1800, lnSpc=110, sql=True) for l in sql), autofit=False)
        s += textbox(ids, X0, 5250000, W0, 1300000,
            para("이 네 가지를 먼저 돌리면 대부분의 오류를 **분석 시작 전에** 발견합니다.", sz=2400, b=True, algn="ctr", lnSpc=118) +
            para("결과를 메모해 두면 나중에 “왜 이 숫자가 나왔는지” 설명할 수 있습니다.", sz=2200, algn="ctr", lnSpc=118, color="1F3763"))
        return s
    return free("오류를 찾는 SQL 네 가지", b, subtitle="데이터를 처음 받았을 때")


def assignment2_slide():
    def b(ids):
        s = panel(ids, X0, 1550000, 6000000, 2600000, "과제 2 — 무엇을 하나요", [
            "연구자 요청서 1건을 받아 코호트를 추출합니다",
            "- 배정된 질환의 임상시험을 대상으로",
            "- 조건을 단계별로 적용하고 건수를 기록",
            "- 심어 둔 오류 6가지를 찾아 수정",
            "- 검산표와 해석 1쪽을 작성"], fill="DEEAF6", line="1F497D", sz=1900)
        s += panel(ids, 7300000, 1550000, 6000000, 2600000, "배점 (20점)", [
            "단계별 SQL 8점",
            "검산표 4점",
            "오류 발견과 수정 설명 5점",
            "결과 해석 3점",
            "제출: 노트북 파일 하나 (과제2.ipynb)"], fill="E2EFDA", line="2C5F2D", sz=1900)
        s += textbox(ids, X0, 4400000, W0, 2000000,
            para("**일정**", sz=2400, lnSpc=130) +
            para("오늘(12주차) 과제 2 공개 — 오류 점검 방법을 배웠으니 바로 시작할 수 있습니다", sz=2100, lvl=1, lnSpc=125) +
            para("13주차 수업에서 사례를 함께 풀고 질문을 받습니다", sz=2100, lvl=1, lnSpc=125) +
            para("13주차 수업 후 1주일 이내 제출", sz=2100, lvl=1, lnSpc=125) +
            para("데이터에 숨어 있는 오류를 **찾아내는 것**이 이번 과제의 핵심입니다.",
                 sz=2300, b=True, algn="ctr", color=BLUE, lnSpc=120, spcBef=14))
        return s
    return free("과제 2 안내", b, subtitle="20점 · 노트북 파일 하나 · 13주차 수업 후 제출")


def build(c):
    # --- 도입
    c.add(cover(12, "의료데이터에서 자주 생기는 오류",
                ["세는 단위와 JOIN", "타입 · 형식 · 빈 값 · 코드", "기준일과 점검 체크리스트"],
                "2026. 12. 1."))
    c.add(content("지난시간 리뷰", [
        ("**CDW** = 분석용 읽기 전용 복사본, 보통 하루 정도 시차", dict(lvl=1, marL=457200, indent=-457200)),
        ("분석 전에 **데이터 사전**과 **요청서**로 단위 · 대상 · 기준일을 정한다", dict(lvl=1, marL=457200, indent=-457200)),
        ("**승인 범위 안에서** 최소한의 항목만 조회한다", dict(lvl=1, marL=457200, indent=-457200)),
        ("절차를 지켜도 **숫자가 틀릴 수 있습니다.**", dict(spcBef=18)),
        ("오늘은 실제로 자주 생기는 오류 12가지를 사례로 봅니다.", dict(b=True, algn="ctr", color=BLUE, spcBef=12)),
    ]))
    c.add(objectives_slide(12,
        ["건수가 부풀거나 줄어드는 원인을 찾아낼 수 있다",
         "타입과 형식 때문에 생기는 오류를 알아볼 수 있다",
         "NULL과 표기 불일치를 확인하고 처리할 수 있다",
         "점검 체크리스트로 결과를 스스로 검증할 수 있다"],
        AGENDA, subtitle="오류는 문법이 아니라 데이터에서 나옵니다",
        date_note="오늘 과제 2(20점)를 공개합니다. 13주차 수업 후 1주일 이내 제출입니다"))

    # --- 1. 세는 단위와 JOIN
    c.add(section_slide(1, AGENDA, lead="가장 흔하고, 가장 눈에 안 띄는 오류입니다"))
    c.add(error_slide(1, "세는 단위를 잘못 잡음",
        "“한국에서 진행된 임상시험이 몇 건인가요?”",
        ["SELECT COUNT(*) AS 시험수", "FROM facilities", "WHERE country = 'South Korea';"],
        "4,098", "한 시험이 여러 기관에서 진행되어 기관 기록의 행 수를 센 것입니다.",
        ["SELECT COUNT(DISTINCT nct_id) AS 시험수", "FROM facilities", "WHERE country = 'South Korea';"],
        "1,182", "시험 단위로 중복을 없앴습니다.",
        "병원에서도 같습니다. 환자 수인지, 방문 건수인지, 처방 건수인지 먼저 정하세요. 표의 한 행이 무엇인지부터 확인합니다."))
    c.add(error_slide(2, "JOIN 뒤 행이 늘어남",
        "질환 정보를 붙였더니 건수가 10배가 되었습니다.",
        ["SELECT COUNT(*) AS 시험수", "FROM studies AS s", "JOIN browse_conditions AS b",
         "  ON s.nct_id = b.nct_id;"],
        "309,124", "한 시험에 질환이 평균 10개 붙어 행이 늘어났습니다.",
        ["SELECT COUNT(DISTINCT s.nct_id) AS 시험수", "FROM studies AS s", "JOIN browse_conditions AS b",
         "  ON s.nct_id = b.nct_id;"],
        "31,634", "시험 단위를 유지했습니다.",
        "JOIN 전후의 행 수를 항상 비교하세요. 1 : N 이면 반드시 늘어납니다."))
    c.add(error_slide(3, "INNER JOIN으로 분모가 줄어듦",
        "“전체 시험 중 한국이 참여한 비율”을 구하려고 합니다.",
        ["SELECT COUNT(DISTINCT s.nct_id) AS 분모", "FROM studies AS s", "JOIN facilities AS f",
         "  ON s.nct_id = f.nct_id;"],
        "34,810", "기관 정보가 없는 2,699건이 조용히 빠졌습니다.",
        ["SELECT COUNT(DISTINCT s.nct_id) AS 분모", "FROM studies AS s", "LEFT JOIN facilities AS f",
         "  ON s.nct_id = f.nct_id;"],
        "37,509", "전체를 분모로 유지했습니다.",
        "비율을 구할 때는 분모가 줄지 않았는지 LEFT JOIN 으로 확인하세요."))
    c.add(checkpoint_slide(
        ["**COUNT(*)** 는 행을, **COUNT(DISTINCT 키)** 는 대상을 센다",
         "**JOIN 뒤에는 행 수가 변한다.** 전후를 비교한다",
         "비율의 **분모**는 LEFT JOIN 으로 다시 확인한다"],
        question="한 시험이 여러 기관에서 진행될 때 COUNT(*)는 무엇을 셀까요?",
        answer="기관 기록의 행 수를 셉니다. 시험 수를 세려면 COUNT(DISTINCT nct_id)가 필요합니다."))

    # --- 2. 값의 타입과 형식
    c.add(section_slide(2, AGENDA, lead="숫자처럼 보이지만 문자인 값들"))
    c.add(error_slide(4, "문자로 저장된 숫자",
        "“최소 연령 60세 이상인 시험”을 찾으려고 합니다.",
        ["SELECT COUNT(*)", "FROM eligibilities", "WHERE minimum_age >= '60 Years';"],
        "998", "글자 순서로 비교했습니다. '9 Years' 가 '60 Years' 보다 크게 나옵니다.",
        ["SELECT COUNT(*)", "FROM calculated_values", "WHERE minimum_age_num >= 60",
         "  AND minimum_age_unit = 'year';"],
        "1,036", "숫자형 열을 사용했습니다.",
        "병원 예: 혈압 '120/80', 검사결과 '<0.5' 처럼 기호가 섞인 값은 모두 문자입니다."))
    c.add(error_slide(5, "문자로 저장된 날짜",
        "날짜가 문자로 저장된 표에서 기간을 비교합니다.",
        ["SELECT '2024-9-1' < '2024-10-1';"],
        "false", "글자로 비교하면 '9' 가 '1' 보다 큽니다. 9월이 10월보다 뒤로 정렬됩니다.",
        ["SELECT DATE '2024-09-01'", "     < DATE '2024-10-01';"],
        "true", "날짜형으로 바꾸면 제대로 비교됩니다.",
        "자릿수를 맞춘 'YYYY-MM-DD' 형식이거나 DATE 타입이어야 안전합니다."))
    c.add(error_slide(6, "정수 나눗셈으로 0이 나옴",
        "191 / 817 의 비율을 퍼센트로 구합니다.",
        ["SELECT 191 / 817 * 100 AS 비율;", "", "-- PostgreSQL · SQL Server · SQLite"],
        "0", "정수끼리 나누면 소수점이 잘려 0이 되고, 거기에 100을 곱해도 0입니다.",
        ["SELECT ROUND(100.0 * 191 / 817, 1)", "       AS 비율;"],
        "23.4", "100.0 처럼 소수를 섞으면 소수 계산이 됩니다.",
        "비율에는 100.0 을 곱하거나 CAST 를 씁니다. CAST = 값의 종류를 바꾸는 것(문자 → 숫자)."))
    c.add(error_slide(7, "엑셀에서 앞자리 0이 사라짐",
        "환자번호 '0012345' 를 엑셀로 열었다가 다시 저장했습니다.",
        ["-- 엑셀이 숫자로 인식", "0012345  →  12345", "", "SELECT * FROM 환자",
         "WHERE 환자ID = '0012345';"],
        "0행", "앞의 0이 사라져 원본과 맞지 않습니다.",
        ["-- CSV를 열 때 해당 열을", "-- ‘텍스트’로 지정하거나", "-- 데이터베이스에서 직접 조회", "",
         "SELECT * FROM 환자", "WHERE 환자ID = '0012345';"],
        "정상", "엑셀을 거치지 않는 것이 가장 안전합니다.",
        "환자번호 · 진료과 코드 · 우편번호처럼 0으로 시작하는 값은 반드시 문자로 다룹니다.", sz=1800))

    # --- 3. 빈 값과 코드
    c.add(section_slide(3, AGENDA, lead="비어 있는 값과 제각각인 표기"))
    c.add(error_slide(8, "NULL을 0으로 바꿈",
        "검사 결과가 없는 환자를 0으로 채워 평균을 냈습니다.",
        ["SELECT AVG(COALESCE(검사값, 0))", "FROM 검사;"],
        "실제보다 낮음", "검사를 안 한 사람이 ‘0점’으로 계산됩니다.",
        ["SELECT COUNT(*) AS 전체,", "       COUNT(검사값) AS 값있음,", "       AVG(검사값) AS 평균",
         "FROM 검사;"],
        "정확", "빈 값의 개수를 먼저 확인하고, 평균에서는 제외합니다.",
        "NULL을 어떻게 처리했는지 **결과 보고서에 반드시 적습니다.**"))
    c.add(two_panel_slide("빠진 값 자체가 정보입니다", "왜 비어 있는지 먼저 물어봅니다",
        "의료 데이터의 결측은 아무 이유 없이 생기지 않습니다.",
        ("검사값이 없다는 것은",
         ["검사를 할 필요가 없을 만큼 안정적이었다",
          "- 너무 위급해서 검사할 겨를이 없었다",
          "- 다른 병원에서 받아 우리 기록에 없다",
          "- 시스템을 바꾸면서 옮겨지지 않았다"], *RED_PANEL),
        ("그래서 이렇게 합니다",
         ["전체 건수와 값이 있는 건수를 **항상 함께** 보고합니다",
          "- 빠진 비율이 큰 열은 결론의 근거로 쓰지 않음",
          "- 왜 비어 있는지 담당 부서에 확인",
          "- 0으로 채울지는 계산이 아니라 임상으로 판단"], *GREEN_PANEL),
        note=["**빠진 값을 0으로 채우는 것은 계산 문제가 아니라 해석 문제입니다.**",
              "채우기 전에 “이 빈칸이 무엇을 뜻하는가”를 먼저 물어보세요."],
        y=2250000, h=2300000))
    c.add(error_slide(9, "대소문자와 공백",
        "임상 단계를 'Phase 3' 으로 찾았습니다.",
        ["SELECT COUNT(*)", "FROM studies", "WHERE phase = 'Phase 3';"],
        "0", "실제 값은 'PHASE3' 입니다. 표기가 다르면 하나도 안 나옵니다.",
        ["SELECT DISTINCT phase", "FROM studies;", "", "-- 값을 먼저 보고 조건 작성"],
        "PHASE3 등 9종", "DISTINCT 로 실제 값을 먼저 확인합니다.",
        "값이 0행이면 “없다”가 아니라 “조건이 틀렸다”를 먼저 의심하세요."))
    c.add(error_slide(10, "같은 질환, 다른 표기",
        "“제2형 당뇨병” 시험을 연구자 입력 값으로 찾았습니다.",
        ["SELECT COUNT(DISTINCT nct_id)", "FROM conditions", "WHERE name = 'Diabetes Mellitus, Type 2';"],
        "541", "자유 입력이라 표기가 35가지로 갈라져 있습니다.",
        ["SELECT COUNT(DISTINCT nct_id)", "FROM browse_conditions", "WHERE mesh_term = 'Diabetes Mellitus, Type 2';"],
        "1,353", "MeSH 표준 용어 열을 사용했습니다.",
        "병원 예: 진단명 자유 입력 대신 **KCD 코드**를 쓰는 이유가 바로 이것입니다."))
    c.add(two_panel_slide("오류 11 — 청구 자료를 진료 기록으로 읽음",
        "같은 환자 자료라도 만들어진 목적이 다릅니다",
        "청구(EDI) 자료로 유병률을 세었더니 실제보다 훨씬 크게 나왔습니다.",
        ("청구 자료를 그대로 믿으면",
         ["청구 자료는 비용을 청구한 기록입니다",
          "- 확진이 아닌 의심(R/O) 상병이 섞임",
          "- 주상병 기준이 임상 중증도와 다름",
          "- 비급여 · 미청구 항목은 아예 없음",
          "- 같은 상병이 방문마다 반복해 붙음"], *RED_PANEL),
        ("이렇게 확인합니다",
         ["상병의 구분(주 · 부, 의심 여부)을 함께 봅니다",
          "- 몇 번 이상 청구된 경우만 셀지 미리 정함",
          "- 중요한 지표는 진료 기록(EMR)과 맞춰 봄",
          "- 세는 규칙을 문서로 남김"], *GREEN_PANEL),
        note=["**청구 자료로 센 유병률은 실제보다 크게 나오기 쉽습니다.**",
              "숫자를 낼 때 “어떤 자료로, 어떤 규칙으로 세었는지”를 함께 적어 주세요."],
        y=2250000, h=2300000))
    c.add(checkpoint_slide(
        ["**NULL을 0으로 바꾸지 않는다.** 처리 방법을 기록한다",
         "결과가 0행이면 **조건의 표기**를 먼저 의심한다",
         "자유 입력 대신 **표준 코드 열**을 사용한다"],
        question="검사 결과 칸이 비어 있습니다. 0으로 채워도 될까요?",
        answer="안 됩니다. ‘검사를 안 했다’와 ‘0이 나왔다’는 다른 뜻입니다."))

    # --- 4. 시간
    c.add(section_slide(4, AGENDA, lead="시간 순서를 어기면 결과가 지나치게 좋아집니다"))
    c.add(error_slide(12, "기준일 이후 정보가 섞임",
        "“입원 시점에 재입원을 예측”하는데 퇴원 후 검사를 넣었습니다.",
        ["-- 기준일(입원일) 이후 자료까지 사용", "SELECT …", "FROM 입원 adm JOIN 검사 lab",
         "  ON adm.환자ID = lab.환자ID;"],
        "예측 정확도가 비현실적으로 높음", "미래의 정보가 섞였습니다 (정보 누출).",
        ["SELECT …", "FROM 입원 adm JOIN 검사 lab", "  ON adm.환자ID = lab.환자ID",
         "WHERE lab.검사일 <= adm.입원일;"],
        "현실적인 값", "기준일 이전 자료만 사용했습니다.",
        "변수마다 “이 값을 기준일에 알 수 있었는가?”를 확인하세요.", sz=1800))
    c.add(table_slide("기준일(Index Date) 정하기", "대상자마다 분석의 출발점을 하나로 정합니다",
        ["분석 질문", "기준일", "기준일 이전만 써야 하는 것"],
        [["30일 재입원율", "퇴원일", "입원 중 검사 · 진단 · 처방"],
         ["수술 후 합병증", "수술일", "수술 전 검사 · 기저질환"],
         ["약물 효과 비교", "첫 처방일", "처방 전 진단 · 검사"],
         ["신규 진단 발생률", "코호트 등록일", "등록 전 병력"]],
        [3200000, 2800000, 5800000], sz=2000, row_h=620000, y=1750000,
        col_algn=["l", "ctr", "l"],
        note="기준일을 정하지 않으면 사람마다 다른 기간의 자료를 쓰게 됩니다."))

    c.add(table_slide("코드가 바뀌면 추세가 끊깁니다", "몇 년치를 한 번에 볼 때 꼭 확인할 것",
        ["무엇이 바뀌나", "무슨 일이 생기나", "어떻게 확인하나"],
        [["질병분류(KCD) 개정", "코드가 새로 생기거나 없어져\n연도별 건수가 갑자기 뜀", "데이터 사전에서 코드의\n적용 기간을 확인"],
         ["약제 · 수가 코드 변경", "같은 약이 다른 코드로 기록됨", "성분명이나 표준코드로 묶어서 셈"],
         ["원내 코드 정비", "부서가 코드를 다시 매긴\n시점부터 값이 달라짐", "담당 부서에 변경 이력을 요청"]],
        [3200000, 4200000, 4200000], sz=1800, row_h=800000, y=1750000,
        col_algn=["ctr", "l", "l"],
        note="제9차 한국표준질병 · 사인분류(KCD-9)는 2026년 1월 1일부터 시행되었습니다.",
        note_style="takeaway"))
    # --- 5. 점검 체크리스트
    c.add(section_slide(5, AGENDA, lead="결과를 내보내기 전에 훑는 표"))
    c.add(checklist_slide())
    c.add(finder_sql_slide())

    # --- 6. 정리
    c.add(section_slide(6, AGENDA, lead="과제 2 안내와 오늘의 핵심입니다"))
    c.add(terms_slide(12, [
        ["세는 단위", "Granularity", "결과의 한 행이 무엇을 뜻하는가"],
        ["행 부풀림", "Fan-out", "1 : N 관계를 JOIN해 한 건이 여러 행이 되는 것"],
        ["정보 누출", "Data Leakage", "기준일 이후의 정보가 분석에 섞여 들어가는 것"],
        ["결측", "Missing", "값이 비어 있는 것. 비어 있는 이유 자체가 정보"],
        ["표기 불일치", "—", "같은 뜻을 다른 글자 · 코드로 적어 둔 상태"],
        ["형 변환", "CAST", "문자로 저장된 숫자 · 날짜를 계산할 수 있는 형으로 바꾸기"],
        ["청구 자료", "EDI", "진료비를 청구한 기록. 진료 기록과는 목적이 다름"],
        ["검산표", "—", "단계마다 건수와 변화량을 적어 둔 표"],
    ]))
    c.add(assignment2_slide())
    c.add(summary(12, [
        "**세는 단위**와 **JOIN 후 행 수**를 항상 확인한다",
        "**타입 · 표기 · 빈 값**이 결과를 조용히 바꾼다",
        "**기준일 이전 자료만** 쓰고, 처리 방법을 보고서에 기록한다",
    ], sz=2800, lnSpc=170, next_week="13강. CDW 실무 사례 — 코호트 추출을 처음부터 끝까지, 과제 2 제출"))
