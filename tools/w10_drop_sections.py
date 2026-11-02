# -*- coding: utf-8 -*-
"""10강에서 1절(데이터를 바꾼다는 것)과 5절(안전하게 배우기)을 지우고, 남은 절 번호 · 오늘의 순서를 1~4로 (2026-11-02 강사 요청).
사용: python3 tools/w10_drop_sections.py <덱.pptx> <결과.pptx>"""
import sys, re, zipfile, posixpath
from lxml import etree
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
DROP_TITLES = ["1. 데이터를 바꾼다는 것", "조회와 수정은 다릅니다", "5. 안전하게 배우기",
               "안전하게 연습하는 세 가지 순서", "분석자는 원본을 함부로 바꾸지 않습니다"]
DROP_ITEMS = ("데이터를 바꾼다는 것", "안전하게 배우기")
RETITLE = {"2. INSERT · UPDATE · DELETE": "1. INSERT · UPDATE · DELETE", "3. 트랜잭션": "2. 트랜잭션",
           "4. COMMIT과 ROLLBACK": "3. COMMIT과 ROLLBACK", "6. 정리": "4. 정리"}


def paras(el):
    return ["".join(x.text or "" for x in p.iter(A + "t")) for p in el.iter(A + "p")]


def main(src, out):
    z = zipfile.ZipFile(src)
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    prels = etree.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    ct = etree.fromstring(z.read("[Content_Types].xml"))
    rid2rel = {r.get("Id"): r for r in prels}
    lst = pres.find(P + "sldIdLst")
    sids = list(lst)
    paths = ["ppt/" + rid2rel[s.get(R + "id")].get("Target") for s in sids]
    tx = [paras(etree.fromstring(z.read(p))) for p in paths]
    s10 = [i for i, x in enumerate(tx) if "10강. 안전한 데이터 수정과 트랜잭션" in x][0]
    e10 = [i for i, x in enumerate(tx) if "11강. CDW 구조와 분석 업무 흐름" in x][0]
    drop, remove_parts, repl = [], set(), {}
    for i in range(s10, e10):
        title = tx[i][0] if tx[i] else ""
        if any(t in tx[i][:2] for t in DROP_TITLES):
            drop.append(i)
    assert len(drop) == 5, [tx[i][:1] for i in drop]
    for i in drop:
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
    # 남은 10강 슬라이드: 절 제목 번호 · 오늘의 순서
    for i in range(s10, e10):
        if i in drop:
            continue
        t = etree.fromstring(z.read(paths[i])); changed = False
        for x in t.iter(A + "t"):
            if x.text in RETITLE:
                x.text = RETITLE[x.text]; changed = True
        nos = [s for s in t.iter(P + "sp") if re.match(r"(Step|Sec) No \d+$", s.find(f"{P}nvSpPr/{P}cNvPr").get("name"))]
        if nos:
            items = [s for s in t.iter(P + "sp") if re.match(r"(Step|Sec) \d+$", s.find(f"{P}nvSpPr/{P}cNvPr").get("name"))]
            y = lambda s: int(s.find(f".//{A}off").get("y"))
            nos.sort(key=y); items.sort(key=y)
            assert len(nos) == len(items) == 6
            slots = [y(s) for s in nos]
            keep = []
            for no, it in zip(nos, items):
                if "".join(paras(it)).startswith(DROP_ITEMS):
                    no.getparent().remove(no); it.getparent().remove(it)
                else:
                    keep.append((no, it))
            assert len(keep) == 4
            for k, (no, it) in enumerate(keep):
                no.find(f".//{A}off").set("y", str(slots[k])); it.find(f".//{A}off").set("y", str(slots[k]))
                [x for x in no.iter(A + "t")][0].text = str(k + 1)
            changed = True
        if changed:
            repl[paths[i]] = etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True)
    repl["ppt/presentation.xml"] = etree.tostring(pres, xml_declaration=True, encoding="UTF-8", standalone=True)
    repl["ppt/_rels/presentation.xml.rels"] = etree.tostring(prels, xml_declaration=True, encoding="UTF-8", standalone=True)
    repl["[Content_Types].xml"] = etree.tostring(ct, xml_declaration=True, encoding="UTF-8", standalone=True)
    app = z.read("docProps/app.xml").decode(); m = re.search(r"<Slides>(\d+)</Slides>", app)
    if m:
        repl["docProps/app.xml"] = app.replace(m.group(0), f"<Slides>{int(m.group(1)) - len(drop)}</Slides>").encode()
    with zipfile.ZipFile(out, "w") as zo:
        for info in z.infolist():
            if info.filename in remove_parts:
                continue
            zo.writestr(info, repl.get(info.filename, z.read(info.filename)))
    print("지운 슬라이드", len(drop), "· 고친 슬라이드", len([k for k in repl if k.startswith("ppt/slides/")]))


if __name__ == "__main__":
    main(*sys.argv[1:3])
