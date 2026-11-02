# -*- coding: utf-8 -*-
"""10강 슬라이드: 예시를 aact_mini studies_copy 5행으로 바꾸고, 9강처럼 '질문 · SQL · 결과 표 · 확인' 슬라이드 추가 (2026-11-02).

- 글 고침: 'INSERT · UPDATE · DELETE'(개요) · 'WHERE는 바꿀 대상을 정합니다' · '여기까지 정리' · 'COMMIT과 ROLLBACK'
  의 환자 예시 → studies_copy 예시
- 추가: 9강 '2단계 — 값 살펴보기' 슬라이드 모양을 복제해 5장
    연습용 표 만들기 (참고 '연습용 사본 만들기' 뒤) · INSERT · UPDATE · DELETE (개요 뒤) · ROLLBACK 해 보기 (COMMIT과 ROLLBACK 뒤)
- 숫자는 노트북 10 과 같은 SQL 로 aact_mini 에서 나온 값 (tools/build_nb_w10.py 가 assert)
사용: python3 tools/w10_slides.py <덱.pptx> <결과.pptx>
"""
import sys, re, copy, zipfile
from lxml import etree

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PR = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
A16 = "{http://schemas.microsoft.com/office/drawing/2014/main}"
SLIDE_T = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
KW = re.compile(r"\b(CREATE TEMP TABLE|INSERT INTO|DELETE FROM|GROUP BY|ORDER BY|SELECT|FROM|WHERE|VALUES|UPDATE|SET|LIMIT|"
                r"COUNT|BEGIN|ROLLBACK|COMMIT|AS)\b")

ORIG = [("NCT00455039", "WITHDRAWN", "0"), ("NCT00589043", "UNKNOWN", "600"), ("NCT00593164", "WITHDRAWN", "0"),
        ("NCT00623389", "RECRUITING", "10"), ("NCT00756288", "WITHDRAWN", "0")]
HEAD = ["nct_id", "overall_status", "enrollment"]


def texts(el):
    return ["".join(x.text or "" for x in p.iter(A + "t")) for p in el.iter(A + "p")]


def sp(t, name):
    m = [s for s in t.iter(P + "sp") if s.find(f"{P}nvSpPr/{P}cNvPr").get("name") == name]
    assert len(m) == 1, name
    return m[0]


def set_run(t, old, new, shape=None):
    root = sp(t, shape) if shape else t
    m = [x for x in root.iter(A + "t") if x.text == old]
    assert len(m) == 1, (old, len(m))
    m[0].text = new


# ---------------------------------------------------------------- 1) 있는 슬라이드의 환자 예시 → studies_copy
def edit_overview(t):          # INSERT · UPDATE · DELETE (개요)
    set_run(t, " 환자", " studies_copy", "TextBox 7")
    set_run(t, "  (환자ID, 환자명, 생년월일)", "  (nct_id, overall_status, enrollment)", "TextBox 7")
    set_run(t, " ('P100', '김OO', '1958-03-11');", " ('NCT99999999', 'RECRUITING', 50);", "TextBox 7")
    set_run(t, " 환자", " studies_copy", "TextBox 10")
    set_run(t, " 연락처 = '010-9999-8888'", " overall_status = 'COMPLETED'", "TextBox 10")
    set_run(t, " 환자ID = 'P100';", " nct_id = 'NCT00623389';", "TextBox 10")
    set_run(t, " 환자", " studies_copy", "TextBox 13")
    set_run(t, " 환자ID = 'P100';", " overall_status = 'WITHDRAWN';", "TextBox 13")


def edit_where(t):             # WHERE는 바꿀 대상을 정합니다
    set_run(t, " 환자", " studies_copy", "TextBox 8")
    set_run(t, " 진료과 = '내과';", " overall_status = 'COMPLETED';", "TextBox 8")
    set_run(t, "모든 환자의 진료과가 내과로 바뀝니다", "5개 시험이 모두 COMPLETED 로 바뀝니다")
    tb = sp(t, "TextBox 12")
    for x in [x for x in tb.iter(A + "t") if x.text == " 환자"]:
        x.text = " studies_copy"
    for x in [x for x in tb.iter(A + "t") if x.text == " 진료과 = '외과';"]:
        x.text = " overall_status = 'WITHDRAWN';"
    set_run(t, " 진료과 = '내과'", " overall_status = 'TERMINATED'", "TextBox 12")
    set_run(t, "조건에 맞는 환자만 바뀝니다", "조건에 맞는 3개 시험만 바뀝니다")
    set_run(t, "예시의 환자 표는 설명을 위한 가상 표입니다", "studies_copy 는 studies 5행 사본입니다")


def edit_summary(t):           # 여기까지 정리
    set_run(t, "예시로 확인하기  환자 한 명의 연락처만 바꾸려면", "예시로 확인하기  시험 한 건의 상태만 바꾸려면")
    set_run(t, "로 그 환자를 지정합니다", "로 그 시험(nct_id)을 지정합니다")


def edit_commit(t):            # COMMIT과 ROLLBACK
    tb = sp(t, "TextBox 7")
    upd = [p for p in tb.iter(A + "p") if "".join(x.text or "" for x in p.iter(A + "t")).startswith("UPDATE")]
    assert len(upd) == 1 and [r.findtext(A + "t") for r in upd[0].findall(A + "r")] == ["UPDATE", " ", "환자"]
    upd[0].findall(A + "r")[2].find(A + "t").text = "studies_copy"
    set_run(t, "연락처 ", "overall_status ", "TextBox 7")
    set_run(t, "= '010-9999-8888'", "= 'COMPLETED'", "TextBox 7")
    tb = sp(t, "TextBox 7")
    last = [p for p in tb.iter(A + "p") if "".join(x.text or "" for x in p.iter(A + "t")).startswith("WHERE")]
    assert len(last) == 1
    rs = last[0].findall(A + "r")
    assert [r.findtext(A + "t") for r in rs] == ["WHERE", " ", "환자", "ID = 'P100';"]
    rs[2].find(A + "t").text = "nct_id"
    rs[3].find(A + "t").text = " = 'NCT00623389';"


# ---------------------------------------------------------------- 2) 9강 2단계 슬라이드를 본으로 새 슬라이드
def run_with(rpr, text):
    r = etree.Element(A + "r")
    r.append(copy.deepcopy(rpr))
    etree.SubElement(r, A + "t").text = text
    return r


def build(template, title, question, sql_lines, hl_lines, label, header, rows, hl_rows, widths, notes):
    t = copy.deepcopy(template)
    set_run(t, "2단계 — 값 살펴보기", title)
    sp(t, "Q").findall(f".//{A}r")[1].find(A + "t").text = "  " + question
    sqlsp = sp(t, "SQL")
    body = sqlsp.find(P + "txBody")
    ps = body.findall(A + "p")
    rp = {}
    for p_ in ps:
        for r in p_.findall(A + "r"):
            txt, pr = r.findtext(A + "t"), r.find(A + "rPr")
            hl = pr.find(A + "highlight") is not None
            if txt == "FROM" and not hl: rp["kw"] = pr
            if txt == " studies" and not hl: rp["n"] = pr
            if txt == "GROUP BY" and hl: rp["kw_hl"] = pr
            if txt == " phase" and hl: rp["n_hl"] = pr
    assert set(rp) == {"kw", "n", "kw_hl", "n_hl"}, rp.keys()
    ptemplate = ps[3]
    for p_ in ps:
        body.remove(p_)
    for i, line in enumerate(sql_lines):
        p_ = copy.deepcopy(ptemplate)
        for r in p_.findall(A + "r"):
            p_.remove(r)
        end = p_.find(A + "endParaRPr")
        hl = i in hl_lines
        pos, pieces = 0, []
        code, cmt = (line.split("--", 1)[0], "--" + line.split("--", 1)[1]) if "--" in line else (line, "")
        for m in KW.finditer(code):
            if m.start() > pos:
                pieces.append((code[pos:m.start()], False))
            pieces.append((m.group(0), True))
            pos = m.end()
        if pos < len(code):
            pieces.append((code[pos:], False))
        if cmt:
            pieces.append((cmt, False))
        if not pieces:
            pieces = [(" ", False)]
        for txt, kw in pieces:
            r = run_with(rp[("kw" if kw else "n") + ("_hl" if hl and not (cmt and txt == cmt) else "")], txt)
            (end.addprevious(r) if end is not None else p_.append(r))
        body.append(p_)
    ext = sqlsp.find(f".//{A}ext")
    ext.set("cy", str(330000 * len(sql_lines) + 250000))
    sql_bottom = int(sqlsp.find(f".//{A}off").get("y")) + int(ext.get("cy"))
    [x for x in sp(t, "Res lab").iter(A + "t")][0].text = label
    tbl = t.find(f".//{A}tbl")
    frame = tbl.getparent().getparent().getparent()
    trs = tbl.findall(A + "tr")
    head_t, plain_t, hl_t = trs[0], trs[1], trs[-1]
    grid = tbl.find(A + "tblGrid")
    cols = grid.findall(A + "gridCol")
    for c in cols:
        grid.remove(c)
    for w in widths:
        c = copy.deepcopy(cols[0]); c.set("w", str(w)); grid.append(c)
    for tr in trs:
        tbl.remove(tr)

    def make(tmpl, vals):
        tr = copy.deepcopy(tmpl)
        tcs = tr.findall(A + "tc")
        keep = [tcs[0]] + [tcs[-1]] * (len(vals) - 1)
        for tc in tcs:
            tr.remove(tc)
        ext_ = tr.find(A + "extLst")
        for tc_t, v in zip(keep, vals):
            tc = copy.deepcopy(tc_t)
            ts = list(tc.iter(A + "t"))
            ts[0].text = v
            for extra in ts[1:]:
                extra.getparent().getparent().remove(extra.getparent())
            (ext_.addprevious(tc) if ext_ is not None else tr.append(tc))
        return tr

    tbl.append(make(head_t, header))
    for i, row in enumerate(rows):
        tbl.append(make(hl_t if i in hl_rows else plain_t, row))
    for k, el in enumerate(grid.iter(A16 + "colId")):
        el.set("val", str(20000 + k))
    for k, el in enumerate(tbl.iter(A16 + "rowId")):
        el.set("val", str(10000 + k))
    total = int(head_t.get("h")) + sum(int((hl_t if i in hl_rows else plain_t).get("h")) for i in range(len(rows)))
    frame.find(f"{P}xfrm/{A}ext").set("cy", str(total))
    frame.find(f"{P}xfrm/{A}ext").set("cx", str(sum(widths)))
    tbl_bottom = int(frame.find(f"{P}xfrm/{A}off").get("y")) + total
    chk = sp(t, "Chk")
    cb = chk.find(P + "txBody")
    cps = cb.findall(A + "p")
    p0 = cps[0]
    for p_ in cps:
        cb.remove(p_)
    for lab_txt, body_txt in notes:
        p_ = copy.deepcopy(p0)
        rs = p_.findall(A + "r")
        rs[0].find(A + "t").text = lab_txt
        rs[1].find(A + "t").text = "  " + body_txt
        for r in rs[2:]:
            p_.remove(r)
        cb.append(p_)
    chk.find(f".//{A}off").set("y", str(max(sql_bottom, tbl_bottom) + 152400))
    chk.find(f".//{A}ext").set("cy", str(330000 * len(notes) + 150000))
    return t


W3 = [1600000, 1650000, 1474400]
NEW = {
    "make": dict(title="연습용 표 만들기 — studies 에서 5행만",
                 question="원본(studies)은 그대로 두고, 연습하는 테이블 만들기",
                 sql_lines=["CREATE TEMP TABLE studies_copy AS", "SELECT nct_id, overall_status, enrollment",
                            "FROM studies", "ORDER BY nct_id LIMIT 5;"], hl_lines={0},
                 label="결과 (SELECT * FROM studies_copy ORDER BY nct_id)", header=HEAD, rows=[list(r) for r in ORIG], hl_rows=set(), widths=W3,
                 notes=[("원본", "studies 는 그대로 (읽기 전용)"),
                        ("사본", "studies_copy 는 노트북을 닫으면 사라짐. 다음 장부터 매번 이 5행에서 시작")]),
    "insert": dict(title="INSERT — 새 행 추가하기",
                   question="studies_copy 에 새 시험 한 건을 넣으면?",
                   sql_lines=["INSERT INTO studies_copy", "  (nct_id, overall_status, enrollment)", "VALUES ('NCT99999999', 'RECRUITING', 50);", "SELECT * FROM studies_copy ORDER BY nct_id;"],
                   hl_lines={0, 1, 2}, label="결과", header=HEAD,
                   rows=[list(r) for r in ORIG] + [["NCT99999999", "RECRUITING", "50"]], hl_rows={5}, widths=W3,
                   notes=[("확인", "5행 → 6행. 맨 아래에 새 행이 생김"),
                          ("VALUES", "열 순서(nct_id, overall_status, enrollment)대로 값을 적음")]),
    "update": dict(title="UPDATE — 값 바꾸기",
                   question="NCT00623389 시험의 상태만 COMPLETED 로 바꾸면?",
                   sql_lines=["UPDATE studies_copy", "SET overall_status = 'COMPLETED'", "WHERE nct_id = 'NCT00623389';",
                              "SELECT * FROM studies_copy ORDER BY nct_id;"], hl_lines={1, 2}, label="결과", header=HEAD,
                   rows=[list(r) for r in ORIG[:3]] + [["NCT00623389", "COMPLETED", "10"]] + [list(ORIG[4])], hl_rows={3},
                   widths=W3,
                   notes=[("확인", "WHERE 에 맞는 1행만 바뀜 (RECRUITING → COMPLETED)"),
                          ("SET", "바꿀 열과 새 값, WHERE 는 바꿀 행")]),
    "delete": dict(title="DELETE — 행 지우기",
                   question="철회된(WITHDRAWN) 시험을 지우면?",
                   sql_lines=["DELETE FROM studies_copy", "WHERE overall_status = 'WITHDRAWN';", "SELECT * FROM studies_copy ORDER BY nct_id;"],
                   hl_lines={0, 1}, label="결과", header=HEAD, rows=[list(ORIG[1]), list(ORIG[3])], hl_rows=set(), widths=W3,
                   notes=[("확인", "WITHDRAWN 3행이 지워지고 2행이 남음"),
                          ("먼저 세기", "지우기 전에 같은 WHERE 로 SELECT COUNT(*) 를 하면 3")]),
    "rollback": dict(title="ROLLBACK 해 보기 — 실수를 되돌리기",
                     question="BEGIN 뒤에 WHERE 없는 UPDATE 를 했다면?",
                     sql_lines=["BEGIN;", "UPDATE studies_copy", "SET overall_status = 'COMPLETED';   -- WHERE 없음",
                                "SELECT * FROM studies_copy ORDER BY nct_id;   -- ① 모두 COMPLETED", "ROLLBACK;",
                                "SELECT * FROM studies_copy ORDER BY nct_id;   -- ② 처음대로"], hl_lines={4},
                     label="결과 (overall_status)", header=["nct_id", "① UPDATE 뒤", "② ROLLBACK 뒤"],
                     rows=[[r[0], "COMPLETED", r[1]] for r in ORIG], hl_rows=set(), widths=[1500000, 1500000, 1724400],
                     notes=[("① UPDATE 뒤", "WHERE 를 빠뜨려 5행 모두 COMPLETED"),
                            ("② ROLLBACK 뒤", "BEGIN 이후의 변경이 없던 일이 됨. COMMIT 한 뒤에는 되돌릴 수 없음")]),
}


def main(src, out):
    z = zipfile.ZipFile(src)
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    prels = etree.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    ct = etree.fromstring(z.read("[Content_Types].xml"))
    rid2t = {r.get("Id"): r.get("Target") for r in prels}
    sids = list(pres.find(P + "sldIdLst"))
    paths = ["ppt/" + rid2t[s.get(R + "id")] for s in sids]
    tx = [texts(etree.fromstring(z.read(p))) for p in paths]

    def find(first_line, also=None):
        m = [i for i, x in enumerate(tx) if first_line in x and (also is None or also in x)]
        assert len(m) == 1, (first_line, m)
        return m[0]

    assert not any("INSERT — 새 행 추가하기" in x for x in tx), "이미 추가됨"
    i_tmpl = find("2단계 — 값 살펴보기")
    i_copy = find("(참고) 연습용 사본 만들기")
    i_over = find("INSERT · UPDATE · DELETE", "새 행을 추가")
    i_where = find("WHERE는 바꿀 대상을 정합니다")
    i_sum = find("다음으로 넘어가기 전에", "① INSERT는 추가, UPDATE는 변경, DELETE는 삭제")
    i_commit = find("COMMIT과 ROLLBACK", "확정하거나 되돌리거나")
    repl = {}
    for i, fn in ((i_over, edit_overview), (i_where, edit_where), (i_sum, edit_summary), (i_commit, edit_commit)):
        t = etree.fromstring(z.read(paths[i])); fn(t)
        repl[paths[i]] = etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True)
    template = etree.fromstring(z.read(paths[i_tmpl]))
    tmpl_rels = z.read(paths[i_tmpl].replace("slides/", "slides/_rels/") + ".rels")
    nums = [int(m.group(1)) for n in z.namelist() for m in [re.match(r"ppt/slides/slide(\d+)\.xml$", n)] if m]
    max_id = max(int(s.get("id")) for s in sids)
    max_rid = max(int(r.get("Id")[3:]) for r in prels if r.get("Id").startswith("rId"))
    plan = [(sids[i_copy], ["make"]), (sids[i_over], ["insert", "update", "delete"]), (sids[i_commit], ["rollback"])]
    add, k = {}, 0
    for anchor, keys in plan:
        for key in keys:
            k += 1
            n = max(nums) + k
            part = f"ppt/slides/slide{n}.xml"
            add[part] = etree.tostring(build(template, **NEW[key]), xml_declaration=True, encoding="UTF-8", standalone=True)
            add[f"ppt/slides/_rels/slide{n}.xml.rels"] = tmpl_rels
            rid = f"rId{max_rid + k}"
            rel = etree.SubElement(prels, PR + "Relationship")
            rel.set("Id", rid); rel.set("Type", SLIDE_T); rel.set("Target", f"slides/slide{n}.xml")
            sid = etree.Element(P + "sldId"); sid.set("id", str(max_id + k)); sid.set(R + "id", rid)
            anchor.addnext(sid); anchor = sid
            ov = etree.SubElement(ct, CT + "Override"); ov.set("PartName", f"/{part}"); ov.set("ContentType", SLIDE_CT)
    repl["ppt/presentation.xml"] = etree.tostring(pres, xml_declaration=True, encoding="UTF-8", standalone=True)
    repl["ppt/_rels/presentation.xml.rels"] = etree.tostring(prels, xml_declaration=True, encoding="UTF-8", standalone=True)
    repl["[Content_Types].xml"] = etree.tostring(ct, xml_declaration=True, encoding="UTF-8", standalone=True)
    app = z.read("docProps/app.xml").decode()
    m = re.search(r"<Slides>(\d+)</Slides>", app)
    if m:
        repl["docProps/app.xml"] = app.replace(m.group(0), f"<Slides>{int(m.group(1)) + k}</Slides>").encode()
    with zipfile.ZipFile(out, "w") as zo:
        for info in z.infolist():
            zo.writestr(info, repl.get(info.filename, z.read(info.filename)))
        for name, data in add.items():
            zo.writestr(zipfile.ZipInfo(name), data, compress_type=zipfile.ZIP_DEFLATED)
    print(f"10강: 글 고침 4장 · 새 슬라이드 {k}장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
