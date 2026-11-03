# -*- coding: utf-8 -*-
"""11~13강: 9강과 겹치는 13강 단계별 추출을 줄이고 실무 SQL 두 장을 넣고, 과제 2 새 구성을 반영 (2026-11-03 강사 요청).

- 13강 단계별 추출 1~3단계(3장) → 한 장 '단계별 추출 — 9강 방식 그대로'
    (3단계 슬라이드를 고쳐 씀: 조건 줄마다 ②③④⑤ 주석, 아래 '여기까지의 건수' 그대로. 1 · 2단계 슬라이드는 지움)
- 13강 새 슬라이드 2장 (9강 '2단계 — 값 살펴보기' 모양)
    관찰 기간을 SQL로 — BETWEEN            ('코호트 정의에 꼭 적는 세 가지' 뒤)
    작은 칸 가리기 — CASE WHEN 으로 '5 미만'  ('결과표를 내보내기 전에' 뒤)
- 13강 '4단계 — 국가별로 나누기' → '국가별로 나누기', 강의 정리에 작은 칸 가리기
- 과제 2 새 구성 (요청서 1건 = 제2형 당뇨병 3상 시험의 결과 게시율, tools/build_nb_a2.py):
    12강 '과제 2 안내' · 13강 '과제 2 제출 안내' · '과제 2를 할 때 자주 막히는 부분',
    제출 기한 2026-12-08(화) (README · 노트북과 같게: 12강 · 13강 학습 목표 아래 줄)
- 11강 '결과를 전달하는 형태': 작은 칸 예 '3명 이하' → '5명 미만' (13강 '결과표를 내보내기 전에'와 같은 기준)
- 슬라이드의 숫자는 aact_mini 에서 다시 계산해 assert
사용: python3 tools/w13_revise.py <덱.pptx> <결과.pptx>
"""
import os, sys, re, copy, zipfile, posixpath
from lxml import etree
import duckdb
import w10_slides
from w10_slides import A, P, R, PR, CT, SLIDE_T, SLIDE_CT, texts, sp, set_run, run_with, build
from w10_tx_more import fill

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DM = "Diabetes Mellitus, Type 2"
KW13 = re.compile(r"\b(IS NOT NULL|IS NULL|LEFT JOIN|GROUP BY|ORDER BY|SELECT|FROM|WHERE|JOIN|AND|ON|AS|COUNT|DISTINCT|"
                  r"CASE|WHEN|THEN|ELSE|END|CAST|VARCHAR|BETWEEN|DATE|DESC|LIMIT)\b")
GREY = "7F7F7F"

# ---------------------------------------------------------------- 숫자 (aact_mini)
con = duckdb.connect(os.path.join(ROOT, "data", "aact_mini.duckdb"), read_only=True)
one = lambda q: con.execute(q).fetchone()[0]
J = f"FROM studies JOIN browse_conditions ON studies.nct_id = browse_conditions.nct_id WHERE mesh_term = '{DM}'"
N_ALL, N_DM = one("SELECT COUNT(*) FROM studies"), one(f"SELECT COUNT(DISTINCT studies.nct_id) {J}")
N_NOTW = one(f"SELECT COUNT(DISTINCT studies.nct_id) {J} AND overall_status <> 'WITHDRAWN'")
N_DEN = one(f"SELECT COUNT(DISTINCT studies.nct_id) {J} AND overall_status <> 'WITHDRAWN' AND overall_status = 'COMPLETED'")
N_NUM = one(f"SELECT COUNT(DISTINCT studies.nct_id) {J} AND overall_status = 'COMPLETED' AND results_first_posted_date IS NOT NULL")
assert (N_ALL, N_DM, N_NOTW, N_DEN, N_NUM) == (37509, 1353, 1316, 817, 191), "13강 검산표 숫자와 다름"
assert round(100.0 * N_NUM / N_DEN, 1) == 23.4
PERIOD = [("2015-01-01", "2024-12-31", "  (요청서)"), ("2020-01-01", "2024-12-31", ""), ("2024-01-01", "2024-12-31", "")]
PERIOD_N = [one(f"SELECT COUNT(DISTINCT studies.nct_id) {J} AND start_date BETWEEN DATE '{a}' AND DATE '{b}'") for a, b, _ in PERIOD]
assert PERIOD_N == [1353, 736, 171], PERIOD_N
SMALL = f"""SELECT countries.name AS 국가,
       CASE WHEN COUNT(DISTINCT studies.nct_id) < 5 THEN '5 미만'
            ELSE CAST(COUNT(DISTINCT studies.nct_id) AS VARCHAR)
       END AS 완료시험
FROM studies
JOIN browse_conditions ON studies.nct_id = browse_conditions.nct_id
JOIN countries ON studies.nct_id = countries.nct_id
WHERE mesh_term = '{DM}' AND overall_status = 'COMPLETED' AND removed = false
GROUP BY countries.name
ORDER BY COUNT(DISTINCT studies.nct_id) DESC, 국가"""
small = con.execute(SMALL).fetchall()
assert small[:3] == [("United States", "248"), ("China", "81"), ("Germany", "55")], small[:3]
assert small[-2:] == [("North Macedonia", "5 미만"), ("Syria", "5 미만")], small[-2:]
N_CTRY, N_LT5 = len(small), sum(v == "5 미만" for _, v in small)
assert (N_CTRY, N_LT5) == (87, 38), (N_CTRY, N_LT5)
try:                                        # CAST 를 빼면 오류 (슬라이드에 적는 말)
    con.execute(SMALL.replace("CAST(COUNT(DISTINCT studies.nct_id) AS VARCHAR)", "COUNT(DISTINCT studies.nct_id)")).fetchall()
    raise AssertionError("CAST 없이도 오류가 나지 않음")
except duckdb.Error as e:
    assert "Could not convert string '5 미만'" in str(e), e
fmt = lambda n: f"{n:,}"

# ---------------------------------------------------------------- 새 슬라이드 2장 (9강 '2단계 — 값 살펴보기' 모양)
PERIOD_SLIDE = dict(
    title="관찰 기간을 SQL로 — BETWEEN",
    question="요청서의 관찰 기간(2015~2024년 시작)을 WHERE 한 줄로 옮기면?",
    sql_lines=["SELECT COUNT(DISTINCT studies.nct_id) AS 시험수", "FROM studies", "JOIN browse_conditions",
               "  ON studies.nct_id = browse_conditions.nct_id", f"WHERE mesh_term = '{DM}'",
               "  AND start_date BETWEEN DATE '2015-01-01'", "                     AND DATE '2024-12-31';   -- 관찰 기간"],
    hl_lines={5, 6}, label="결과 — 두 날짜만 바꿔 실행", header=["관찰 기간 (start_date)", "시험수"],
    rows=[[f"{a} ~ {b}{note}", fmt(n)] for (a, b, note), n in zip(PERIOD, PERIOD_N)], hl_rows={0},
    widths=[3600000, 1124400],
    notes=[("기준일 · 관찰 기간", "기준일 = 시험 시작일(start_date), 관찰 기간 = BETWEEN 의 두 날짜 (양 끝 포함, 7강)"),
           ("날짜", "DATE '2015-01-01' 처럼 적어 날짜로 비교 (12강 오류 5)"),
           ("확인", "실습 DB는 2015~2024년 시작 시험만 있어 요청서 기간이면 1,353 그대로. 기간을 좁히면 줄어듦")])
SMALL_SLIDE = dict(
    title="작은 칸 가리기 — CASE WHEN 으로 ‘5 미만’",
    question="국가별 표에서 5건 미만인 칸을 가려서 내보내려면?",
    sql_lines=["SELECT countries.name AS 국가,",
               "       CASE WHEN COUNT(DISTINCT studies.nct_id) < 5 THEN '5 미만'",
               "            ELSE CAST(COUNT(DISTINCT studies.nct_id) AS VARCHAR)",
               "       END AS 완료시험",
               "-- FROM · JOIN · WHERE · GROUP BY 는 「국가별로 나누기」와 같음",
               "ORDER BY COUNT(DISTINCT studies.nct_id) DESC, 국가;   -- 숫자로 정렬"],
    hl_lines={1, 2, 3}, label=f"결과 ({N_CTRY}개국 중 일부)", header=["국가", "완료시험"],
    rows=[list(r) for r in small[:3]] + [["…", "…"]] + [list(r) for r in small[-2:]], hl_rows={4, 5},
    widths=[3000000, 1724400],
    notes=[("CASE WHEN", "5건 미만이면 '5 미만', 아니면 숫자를 글자로 바꿔(CAST) 한 열에 씀"),
           ("CAST 를 빼면", "숫자 열에 글자를 넣을 수 없어 오류 (Could not convert string '5 미만')"),
           ("확인", f"{N_CTRY}개국 중 {N_LT5}개국이 ‘5 미만’. 병원 자료에서는 환자 수 칸에 같은 방법을 씀")])


# ---------------------------------------------------------------- 3단계 슬라이드 → '단계별 추출 — 9강 방식 그대로'
MERGED_SQL = ["SELECT COUNT(DISTINCT studies.nct_id) AS 분모,",
              "       COUNT(DISTINCT CASE WHEN results_first_posted_date",
              "       IS NOT NULL THEN studies.nct_id END) AS 분자   -- ⑤",
              "FROM studies", "JOIN browse_conditions", "  ON studies.nct_id = browse_conditions.nct_id",
              f"WHERE mesh_term = '{DM}'   -- ②",
              "  AND overall_status <> 'WITHDRAWN'   -- ③",
              "  AND overall_status = 'COMPLETED';   -- ④"]


def sql_paras(tb, lines, sz):
    """SQL 글 상자의 문단을 lines 로 다시 만듦: 키워드 = 본의 파란 런, 나머지 = 본의 보통 런, 주석 = 회색"""
    body = tb.find(P + "txBody")
    ps = body.findall(A + "p")
    runs = [r for p_ in ps for r in p_.findall(A + "r")]
    blue = lambda r: r.find(f"{A}rPr/{A}solidFill") is not None
    kw = next(r.find(A + "rPr") for r in runs if blue(r))
    nm = next(r.find(A + "rPr") for r in runs if not blue(r))
    cm = copy.deepcopy(nm)
    fill_ = etree.Element(A + "solidFill"); etree.SubElement(fill_, A + "srgbClr").set("val", GREY)
    cm.insert(0, fill_)
    ptmpl = ps[0]
    for p_ in ps:
        body.remove(p_)
    for line in lines:
        p_ = copy.deepcopy(ptmpl)
        for r in p_.findall(A + "r"):
            p_.remove(r)
        end = p_.find(A + "endParaRPr")
        code, cmt = (line.split("--", 1)[0], "--" + line.split("--", 1)[1]) if "--" in line else (line, "")
        if cmt:
            cmt, code = code[len(code.rstrip()):] + cmt, code.rstrip()
        pos, pieces = 0, []
        for m in KW13.finditer(code):
            if m.start() > pos:
                pieces.append((code[pos:m.start()], nm))
            pieces.append((m.group(0), kw)); pos = m.end()
        if pos < len(code):
            pieces.append((code[pos:], nm))
        if cmt:
            pieces.append((cmt, cm))
        for txt, pr in pieces:
            r = run_with(pr, txt)
            r.find(A + "rPr").set("sz", str(sz))
            (end.addprevious(r) if end is not None else p_.append(r))
        if end is not None:
            end.set("sz", str(sz))
        body.append(p_)


def merged(t):
    set_run(t, "3단계 — 분모와 분자", "단계별 추출 — 9강 방식 그대로")
    set_run(t, "완료된 것 중 결과가 있는 것", "조건을 한 줄씩 더하며 건수를 적습니다", "TextBox 4")
    set_run(t, "  완료된 시험 중 결과가 게시된 비율은?", "  완료된 제2형 당뇨병 시험 중 결과가 게시된 비율은?", "TextBox 5")
    tb, box = sp(t, "TextBox 7"), sp(t, "SQL 6")
    sql_paras(tb, MERGED_SQL, 1600)
    line_h = 280000
    tb.find(f".//{A}ext").set("cy", str(line_h * len(MERGED_SQL)))
    box_h = line_h * len(MERGED_SQL) + 300000
    box.find(f".//{A}ext").set("cy", str(box_h))
    chk = sp(t, "TextBox 9")
    y_chk = int(box.find(f".//{A}off").get("y")) + box_h + 80000
    assert y_chk + int(chk.find(f".//{A}ext").get("cy")) < int(sp(t, "TextBox 10").find(f".//{A}off").get("y")), "확인 줄이 '여기까지의 건수'와 겹침"
    chk.find(f".//{A}off").set("y", str(y_chk))
    set_run(t, "  191 ÷ 817 = 23.4%. COMPLETED만 남기면 ③ 철회도 빠집니다.",
            f"  한 줄 더할 때마다 실행해 아래에 적습니다. ⑤ ÷ ④ = {N_NUM} ÷ {N_DEN} = 23.4%", "TextBox 9")
    flow = " ".join(texts(t))
    for v in (fmt(N_ALL), fmt(N_DM), fmt(N_NOTW), str(N_DEN), str(N_NUM)):
        assert v in flow, v


# ---------------------------------------------------------------- 글 고침
def e_300(t):        # 11강 결과를 전달하는 형태
    set_run(t, "소수 인원 칸은 재식별 위험 (예: 3명 이하)", "소수 인원 칸은 재식별 위험 (예: 5명 미만)")


def e_310(t):        # 12강 학습 목표
    set_run(t, "오늘 과제 2(20점)를 공개합니다. 13주차 수업 후 1주일 이내 제출입니다",
            "오늘 과제 2(20점)를 공개합니다. 제출 기한은 2026-12-08(화)입니다", "TextBox 20")


def e_337(t):        # 12강 과제 2 안내
    set_run(t, "20점 · 노트북 파일 하나 · 13주차 수업 후 제출", "20점 · 노트북 파일 하나 · 2026-12-08(화)까지", "TextBox 4")
    fill(sp(t, "TextBox 7"), [(0, ["연구자 요청서 1건을 받아 코호트를 추출합니다"]),
                              (1, ["제2형 당뇨병 3상 시험의 결과 게시율"]),
                              (2, ["조건을 한 줄씩 더하며 건수를 기록 (S1~S4)"]),
                              (3, ["작은 칸 가리기 (S5) · 동료 SQL 점검 (E1~E3)"]),
                              (4, ["검산표를 INSERT · UPDATE 로 만들고 해석 쓰기"])])
    fill(sp(t, "TextBox 10"), [(0, ["단계별 SQL 8점 · 작은 칸 가리기 2점"]), (1, ["동료 SQL 점검 3점"]),
                               (2, ["검산표 (INSERT · UPDATE) 4점"]), (3, ["결과 해석 3점"]),
                               (4, ["제출: 노트북 파일 하나 (과제2.ipynb)"])])
    fill(sp(t, "TextBox 11"), [(0, ["일정"]),
                               (1, ["오늘(12주차) 과제 2 공개 — 단계별 추출(9주차 방식) · 동료 SQL 점검(오늘)은 바로 시작할 수 있습니다"]),
                               (2, ["작은 칸 가리기와 해석은 13주차 수업에서 함께 보고 질문을 받습니다"]),
                               (3, ["2026-12-08(화)까지 LMS 에 제출"]),
                               (4, ["요청서 한 건을 SQL 로 옮겨, 숫자를 설명할 수 있게 만드는 것이 이번 과제의 핵심입니다."])])


def e_341(t):        # 13강 학습 목표
    set_run(t, "과제 2(20점)는 오늘 수업 후 1주일 이내에 제출합니다", "과제 2(20점) 제출 기한은 2026-12-08(화)입니다", "TextBox 20")


def e_352(t):        # 국가별로 나누기 (단계 번호 없앰: 1~3단계를 한 장으로 합쳤으므로)
    set_run(t, "4단계 — 국가별로 나누기", "국가별로 나누기")


def e_363(t):        # 13강 과제 2 제출 안내
    fill(sp(t, "TextBox 5"), [(0, ["제출물", ": 노트북 파일 하나 (과제2.ipynb)"]),
                              (1, ["S1~S5 · E1~E3 · T1~T2 가 모두 ✅ 인 상태로 저장"]),
                              (2, ["검산표 — INSERT · UPDATE 로 직접 만든 표"]),
                              (3, ["결과 해석 3~5문장 — 말할 수 있는 것과 없는 것"]),
                              (5, ["마감", ": 2026-12-08(화), LMS 제출"]),
                              (6, ["도움이 되는 자료: 9 · 10 · 12주차 실습 노트북, 오늘의 검산표 양식"])])


def e_364(t):        # 13강 과제 2를 할 때 자주 막히는 부분
    fill(sp(t, "TextBox 5"), [(0, ["① 어디부터 하나요"]),
                              (1, ["S1~S4 는 오늘 배운 순서대로 한 줄씩, S5 는 ‘작은 칸 가리기’, E1~E3 은 12주차 체크리스트, T1 · T2 는 10주차 INSERT · UPDATE 로."]),
                              (2, ["② 숫자가 정답과 다릅니다"]),
                              (3, ["검산표에서 건수가 어느 단계부터 달라졌는지 찾고, 그 단계의 조건을 확인하세요."]),
                              (4, ["③ 동료 SQL 의 어디가 틀렸는지 모르겠습니다"]),
                              (5, ["오류 없이 숫자만 틀립니다. 12주차 체크리스트를 위에서부터 대 보세요 — 세는 단위 · 빈 값(NULL) · 표기 순."]),
                              (6, ["④ 해석을 어떻게 쓰나요"]),
                              (7, ["오늘 ‘결과 해석’ 슬라이드의 두 칸을 그대로 따라 쓰면 됩니다."])])


def e_365(t):        # 13강 강의 정리
    set_run(t, "를 함께 적는다", "를 적고, 작은 칸은 가려서 내보낸다", "TextBox 4")


def main(src, out):
    z = zipfile.ZipFile(src)
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    prels = etree.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    ct = etree.fromstring(z.read("[Content_Types].xml"))
    rid2rel = {r.get("Id"): r for r in prels}
    lst = pres.find(P + "sldIdLst")
    sids = list(lst)
    paths = ["ppt/" + rid2rel[s.get(R + "id")].get("Target") for s in sids]
    tx = [texts(etree.fromstring(z.read(p))) for p in paths]

    def find(line, also=None):
        m = [i for i, x in enumerate(tx) if line in x and (also is None or also in x)]
        assert len(m) == 1, (line, m)
        return m[0]

    assert not any("단계별 추출 — 9강 방식 그대로" in x for x in tx), "이미 고침"
    s11, s14 = find("11강. CDW 구조와 분석 업무 흐름"), find("14강. 빅데이터와 의료데이터 표준")
    i_tmpl = find("2단계 — 값 살펴보기")
    i_def3 = find("코호트 정의에 꼭 적는 세 가지")
    i_s1, i_s2, i_s3 = find("1단계 — 대상 시험"), find("2단계 — 제외 조건 적용"), find("3단계 — 분모와 분자")
    i_small = find("결과표를 내보내기 전에")
    edits = [(find("결과를 전달하는 형태"), e_300), (find("12주차 학습 목표"), e_310), (find("과제 2 안내"), e_337),
             (find("13주차 학습 목표"), e_341), (i_s3, merged), (find("4단계 — 국가별로 나누기"), e_352),
             (find("과제 2 제출 안내"), e_363), (find("과제 2를 할 때 자주 막히는 부분"), e_364), (find("13주차 강의 정리"), e_365)]
    for i, _ in edits + [(i_def3, None), (i_s1, None), (i_s2, None), (i_small, None)]:
        assert s11 < i < s14, ("11~13강 밖", i)
    dump = lambda t: etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True)
    repl = {}
    for i, fn in edits:
        t = etree.fromstring(z.read(paths[i])); fn(t); repl[paths[i]] = dump(t)

    # 새 슬라이드 2장
    w10_slides.KW = KW13                        # 13강 슬라이드처럼 JOIN · ON · AND · CASE … 도 파란 글자
    template = etree.fromstring(z.read(paths[i_tmpl]))
    tmpl_rels = z.read(paths[i_tmpl].replace("slides/", "slides/_rels/") + ".rels")
    assert b"notesSlide" not in tmpl_rels
    nums = [int(m.group(1)) for n in z.namelist() for m in [re.match(r"ppt/slides/slide(\d+)\.xml$", n)] if m]
    max_id = max(int(s.get("id")) for s in sids)
    max_rid = max(int(r.get("Id")[3:]) for r in prels if r.get("Id").startswith("rId"))
    add = {}
    for k, (anchor, spec) in enumerate([(sids[i_def3], PERIOD_SLIDE), (sids[i_small], SMALL_SLIDE)], 1):
        n = max(nums) + k
        part = f"ppt/slides/slide{n}.xml"
        add[part] = dump(build(template, **spec))
        add[f"ppt/slides/_rels/slide{n}.xml.rels"] = tmpl_rels
        rid = f"rId{max_rid + k}"
        rel = etree.SubElement(prels, PR + "Relationship")
        rel.set("Id", rid); rel.set("Type", SLIDE_T); rel.set("Target", f"slides/slide{n}.xml")
        sid = etree.Element(P + "sldId"); sid.set("id", str(max_id + k)); sid.set(R + "id", rid)
        anchor.addnext(sid)
        ov = etree.SubElement(ct, CT + "Override"); ov.set("PartName", f"/{part}"); ov.set("ContentType", SLIDE_CT)

    # 1 · 2단계 슬라이드 지움 (3단계 슬라이드가 한 장으로 대신함)
    remove_parts = set()
    for i in (i_s1, i_s2):
        s = sids[i]; rel = rid2rel[s.get(R + "id")]
        lst.remove(s); prels.remove(rel)
        part = paths[i]; relp = part.replace("slides/", "slides/_rels/") + ".rels"
        remove_parts |= {part, relp}
        for r in etree.fromstring(z.read(relp)):
            if r.get("Type").endswith("/notesSlide"):
                np_ = posixpath.normpath(posixpath.join("ppt/slides", r.get("Target")))
                remove_parts |= {np_, np_.replace("notesSlides/", "notesSlides/_rels/") + ".rels"}
    for ov in list(ct):
        if ov.get("PartName", "").lstrip("/") in remove_parts:
            ct.remove(ov)

    repl["ppt/presentation.xml"] = dump(pres)
    repl["ppt/_rels/presentation.xml.rels"] = dump(prels)
    repl["[Content_Types].xml"] = dump(ct)
    app = z.read("docProps/app.xml").decode()
    m = re.search(r"<Slides>(\d+)</Slides>", app)
    if m:
        repl["docProps/app.xml"] = app.replace(m.group(0), f"<Slides>{int(m.group(1)) + 2 - 2}</Slides>").encode()
    with zipfile.ZipFile(out, "w") as zo:
        for info in z.infolist():
            if info.filename in remove_parts:
                continue
            zo.writestr(info, repl.get(info.filename, z.read(info.filename)))
        for name, data in add.items():
            zo.writestr(zipfile.ZipInfo(name), data, compress_type=zipfile.ZIP_DEFLATED)
    print(f"11~13강: 글 고침 {len(edits)}장 · 새 슬라이드 2장 · 지운 슬라이드 2장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
