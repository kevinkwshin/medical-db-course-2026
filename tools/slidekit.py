# -*- coding: utf-8 -*-
"""slidekit — 손으로 고친 v2 덱을 안전하게 고치는 도구 (2026-11-03, 11~13강 재구성용).

Deck(src) 로 열고 → find() 로 슬라이드를 찾고 → tree() 로 고치거나 clone() · insert_after() · delete() → save(out).
  - 슬라이드는 제목 · 문단 글로 찾습니다 (덱이 손으로 바뀌어도 번호에 기대지 않음). 찾는 글은 꼭 한 장에만 있어야 함
  - 새 슬라이드 = 덱 안의 비슷한 슬라이드를 복제해 글만 바꿈 (모양 · 글꼴 · 색은 원래 덱 그대로)
  - 표 채우기 table_fill(): 머리글 행 · 첫 본문 행 서식을 본으로 행 수 · 열 수를 바꿈 (colId · rowId 는 새로 매김)
w10_slides.build() (9강 '2단계 — 값 살펴보기' 모양의 질문 · SQL · 결과 표 · 확인) 와 함께 씁니다.
"""
import re, copy, zipfile, posixpath
from lxml import etree

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PR = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
A16 = "{http://schemas.microsoft.com/office/drawing/2014/main}"
SLIDE_T = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"


def texts(el):
    return ["".join(x.text or "" for x in p.iter(A + "t")) for p in el.iter(A + "p")]


def dump(t):
    return etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True)


def shape(t, name):
    m = [s for s in t.iter(P + "sp") if s.find(f"{P}nvSpPr/{P}cNvPr").get("name") == name]
    assert len(m) == 1, (name, len(m))
    return m[0]


def set_para(s, text, i=0):
    """도형 s 의 i 번째 문단 글을 text 로 (첫 런 서식을 씀, 나머지 런은 지움)"""
    p_ = s.findall(f"{P}txBody/{A}p")[i]
    rs = p_.findall(A + "r")
    assert rs, ("런이 없는 문단", texts(s))
    rs[0].find(A + "t").text = text
    for r in rs[1:]:
        p_.remove(r)


def set_title(t, text):
    set_para(shape(t, "Title 16"), text)


def replace_text(t, old, new):
    """슬라이드 안에서 런 하나의 글이 old 와 똑같으면 new 로 (꼭 한 곳)"""
    m = [x for x in t.iter(A + "t") if x.text == old]
    assert len(m) == 1, (old, len(m))
    m[0].text = new


def table_fill(t, header, rows, widths=None, row_h=None, sz=None, head_sz=None, name=None):
    """슬라이드의 표를 header · rows 로 다시 채움. 값에 '\\n' 이 있으면 문단을 나눔"""
    frames = [g for g in t.iter(P + "graphicFrame") if g.find(f".//{A}tbl") is not None
              and (name is None or g.find(f".//{P}cNvPr").get("name") == name)]
    assert len(frames) == 1, len(frames)
    frame = frames[0]
    tbl = frame.find(f".//{A}tbl")
    trs = tbl.findall(A + "tr")
    head_t, body_t = trs[0], trs[1]
    grid = tbl.find(A + "tblGrid")
    cols = grid.findall(A + "gridCol")
    n = len(header)
    total = sum(int(c.get("w")) for c in cols)
    if widths is None:
        widths = [int(c.get("w")) for c in cols] if len(cols) == n else [total // n] * n
    assert len(widths) == n
    for c in cols:
        grid.remove(c)
    for w in widths:
        c = copy.deepcopy(cols[0]); c.set("w", str(w)); grid.append(c)
    for tr in trs:
        tbl.remove(tr)

    def make(tmpl, vals, size):
        tr = copy.deepcopy(tmpl)
        tcs = tr.findall(A + "tc")
        for tc in tcs:
            tr.remove(tc)
        ext = tr.find(A + "extLst")
        for k, v in enumerate(vals):
            tc = copy.deepcopy(tcs[min(k, len(tcs) - 1)])
            body = tc.find(A + "txBody")
            ps = body.findall(A + "p")
            p0 = ps[0]
            for p_ in ps:
                body.remove(p_)
            for line in str(v).split("\n"):
                p_ = copy.deepcopy(p0)
                rs = p_.findall(A + "r")
                assert rs, "빈 칸 본"
                rs[0].find(A + "t").text = line
                for r in rs[1:]:
                    p_.remove(r)
                if size:
                    for pr in p_.iter(A + "rPr", A + "endParaRPr"):
                        pr.set("sz", str(size))
                body.append(p_)
            (ext.addprevious(tc) if ext is not None else tr.append(tc))
        if row_h:
            tr.set("h", str(row_h))
        return tr

    tbl.append(make(head_t, header, head_sz or sz))
    for r in rows:
        assert len(r) == n, r
        tbl.append(make(body_t, r, sz))
    for k, el in enumerate(grid.iter(A16 + "colId")):
        el.set("val", str(30000 + k))
    for k, el in enumerate(tbl.iter(A16 + "rowId")):
        el.set("val", str(40000 + k))
    h = sum(int(tr.get("h")) for tr in tbl.findall(A + "tr"))
    frame.find(f"{P}xfrm/{A}ext").set("cy", str(h))
    frame.find(f"{P}xfrm/{A}ext").set("cx", str(sum(widths)))
    return int(frame.find(f"{P}xfrm/{A}off").get("y")) + h        # 표 아래 끝 y


KW_SQL = re.compile(r"\b(IS NOT NULL|IS NULL|LEFT JOIN|GROUP BY|ORDER BY|SELECT|FROM|WHERE|JOIN|AND|OR|ON|AS|COUNT|DISTINCT|"
                    r"CASE|WHEN|THEN|ELSE|END|CAST|VARCHAR|BETWEEN|DATE|DESC|LIMIT|SUM|AVG|ROUND|MIN|MAX|"
                    r"INSERT INTO|VALUES|UPDATE|SET|DELETE FROM|IN|NOT)\b")
GREY = "7F7F7F"


def sql_paras(tb, lines, sz, kw=KW_SQL):
    """SQL 글 상자의 문단을 lines 로 다시 만듦: 키워드 = 본의 파란 런, 나머지 = 본의 보통 런, '--' 주석 = 회색"""
    body = tb.find(P + "txBody")
    ps = body.findall(A + "p")
    runs = [r for p_ in ps for r in p_.findall(A + "r")]
    def blue(r):                                   # 덱의 SQL 키워드 색 (0432FF)
        c = r.find(f"{A}rPr/{A}solidFill/{A}srgbClr")
        return c is not None and c.get("val") == "0432FF"
    kwpr = next(r.find(A + "rPr") for r in runs if blue(r))
    nm = next(r.find(A + "rPr") for r in runs if not blue(r))
    cm = copy.deepcopy(nm)
    f = etree.Element(A + "solidFill"); etree.SubElement(f, A + "srgbClr").set("val", GREY)
    cm.insert(0, f)
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
        for m in kw.finditer(code):
            if m.start() > pos:
                pieces.append((code[pos:m.start()], nm))
            pieces.append((m.group(0), kwpr)); pos = m.end()
        if pos < len(code):
            pieces.append((code[pos:], nm))
        if cmt:
            pieces.append((cmt, cm))
        if not pieces:
            pieces = [(" ", nm)]
        for txt, pr in pieces:
            r = etree.Element(A + "r"); r.append(copy.deepcopy(pr)); etree.SubElement(r, A + "t").text = txt
            r.find(A + "rPr").set("sz", str(sz))
            (end.addprevious(r) if end is not None else p_.append(r))
        if end is not None:
            end.set("sz", str(sz))
        body.append(p_)


def move_y(t, name, y):
    shape(t, name).find(f".//{A}off").set("y", str(int(y)))


class Deck:
    def __init__(self, src):
        self.z = zipfile.ZipFile(src)
        self.pres = etree.fromstring(self.z.read("ppt/presentation.xml"))
        self.prels = etree.fromstring(self.z.read("ppt/_rels/presentation.xml.rels"))
        self.ct = etree.fromstring(self.z.read("[Content_Types].xml"))
        self.lst = self.pres.find(P + "sldIdLst")
        self.rid2rel = {r.get("Id"): r for r in self.prels}
        self.trees, self.add, self.removed = {}, {}, set()
        names = self.z.namelist()
        self.num = max(int(m.group(1)) for n in names for m in [re.match(r"ppt/slides/slide(\d+)\.xml$", n)] if m)
        self.sid = max(int(s.get("id")) for s in self.lst)
        self.rid = max(int(r.get("Id")[3:]) for r in self.prels if r.get("Id").startswith("rId"))

    def path(self, sid):
        return "ppt/" + self.rid2rel[sid.get(R + "id")].get("Target")

    def slides(self):
        return list(self.lst)

    def tree(self, sid):
        p = self.path(sid)
        if p not in self.trees:
            self.trees[p] = etree.fromstring(self.z.read(p))
        return self.trees[p]

    def rels(self, sid):
        p = self.path(sid)
        relp = p.replace("slides/", "slides/_rels/") + ".rels"
        return self.add[relp] if relp in self.add else self.z.read(relp)

    def find(self, line, also=None, within=None):
        pool = within if within is not None else self.slides()
        m = [s for s in pool if line in texts(self.tree(s)) and (also is None or also in texts(self.tree(s)))]
        assert len(m) == 1, (line, len(m))
        return m[0]

    def index(self, sid):
        return self.slides().index(sid)

    def between(self, first, last):
        """first ~ last 사이 슬라이드 (둘 다 포함)"""
        s = self.slides()
        return s[s.index(first): s.index(last) + 1]

    def clone(self, sid):
        rel = self.rels(sid)
        assert b"notesSlide" not in rel, "노트가 있는 슬라이드는 복제하지 않음"
        return copy.deepcopy(self.tree(sid)), rel

    def insert_after(self, anchor, t, rel):
        self.num += 1; self.sid += 1; self.rid += 1
        part = f"ppt/slides/slide{self.num}.xml"
        self.trees[part] = t
        self.add[f"ppt/slides/_rels/slide{self.num}.xml.rels"] = rel
        r = etree.SubElement(self.prels, PR + "Relationship")
        r.set("Id", f"rId{self.rid}"); r.set("Type", SLIDE_T); r.set("Target", f"slides/slide{self.num}.xml")
        self.rid2rel[f"rId{self.rid}"] = r
        s = etree.Element(P + "sldId"); s.set("id", str(self.sid)); s.set(R + "id", f"rId{self.rid}")
        anchor.addnext(s)
        ov = etree.SubElement(self.ct, CT + "Override"); ov.set("PartName", f"/{part}"); ov.set("ContentType", SLIDE_CT)
        return s

    def delete(self, sid):
        p = self.path(sid)
        relp = p.replace("slides/", "slides/_rels/") + ".rels"
        for r in etree.fromstring(self.rels(sid)):
            if r.get("Type").endswith("/notesSlide"):
                np_ = posixpath.normpath(posixpath.join("ppt/slides", r.get("Target")))
                self.removed |= {np_, np_.replace("notesSlides/", "notesSlides/_rels/") + ".rels"}
        self.removed |= {p, relp}
        self.trees.pop(p, None); self.add.pop(relp, None)
        self.lst.remove(sid)
        self.prels.remove(self.rid2rel.pop(sid.get(R + "id")))
        for ov in list(self.ct):
            if ov.get("PartName", "").lstrip("/") in self.removed:
                self.ct.remove(ov)

    def save(self, out):
        repl = {p: dump(t) for p, t in self.trees.items()}
        repl["ppt/presentation.xml"] = dump(self.pres)
        repl["ppt/_rels/presentation.xml.rels"] = dump(self.prels)
        repl["[Content_Types].xml"] = dump(self.ct)
        app = self.z.read("docProps/app.xml").decode()
        m = re.search(r"<Slides>(\d+)</Slides>", app)
        if m:
            repl["docProps/app.xml"] = app.replace(m.group(0), f"<Slides>{len(self.lst)}</Slides>").encode()
        old = set(self.z.namelist())
        with zipfile.ZipFile(out, "w") as zo:
            for info in self.z.infolist():
                if info.filename in self.removed:
                    continue
                zo.writestr(info, repl.get(info.filename, self.z.read(info.filename)))
            for name, data in list(repl.items()) + list(self.add.items()):
                if name not in old and name not in self.removed:
                    zo.writestr(zipfile.ZipInfo(name), data, compress_type=zipfile.ZIP_DEFLATED)
