# -*- coding: utf-8 -*-
"""10강 트랜잭션 보충 2장 (2026-11-03): 'ROLLBACK 해 보기' 뒤에 9강 '2단계 — 값 살펴보기' 모양으로 추가.

  ① 한 덩어리로 되돌리기 — BEGIN 뒤 UPDATE + DELETE 를 ROLLBACK 하나로 함께 취소
  ② BEGIN 없이 바꾸면 — 바로 확정되어 ROLLBACK 이 안 됨 (no transaction is active)
- 숫자는 노트북 10 과 같은 SQL 로 aact_mini 에서 나온 값 (tools/build_nb_w10.py 가 assert)
사용: python3 tools/w10_tx_slides.py <덱.pptx> <결과.pptx>
"""
import sys, re, zipfile
from lxml import etree
from w10_slides import P, R, PR, CT, SLIDE_T, SLIDE_CT, ORIG, HEAD, texts, build

GONE = "(지워짐)"
NEW = [
    dict(title="한 덩어리로 되돌리기 — 두 변경을 함께 취소",
         question="BEGIN 뒤에 바꾸기와 지우기를 둘 다 했다면?",
         sql_lines=["BEGIN;", "UPDATE studies_copy SET overall_status = 'COMPLETED'",
                    "WHERE nct_id = 'NCT00623389';   -- ① 바꾸기", "DELETE FROM studies_copy",
                    "WHERE overall_status = 'WITHDRAWN';   -- ② 지우기", "ROLLBACK;   -- ①② 함께 취소"],
         hl_lines={0, 5}, label="결과 (overall_status)", header=["nct_id", "ROLLBACK 전", "ROLLBACK 뒤"],
         rows=[[r[0], "COMPLETED" if r[0] == "NCT00623389" else (GONE if r[1] == "WITHDRAWN" else r[1]), r[1]] for r in ORIG],
         hl_rows=set(), widths=[1500000, 1500000, 1724400],
         notes=[("ROLLBACK 전", "1행 바뀌고 3행 지워져 2행만 남음"),
                ("ROLLBACK 뒤", "두 변경이 함께 취소되어 처음 5행 그대로")]),
    dict(title="BEGIN 없이 바꾸면 — 바로 확정",
         question="BEGIN 없이 UPDATE 하고 ROLLBACK 하면?",
         sql_lines=["UPDATE studies_copy", "SET overall_status = 'COMPLETED';   -- BEGIN 없음",
                    "ROLLBACK;   -- 오류", "SELECT * FROM studies_copy ORDER BY nct_id;"],
         hl_lines={2}, label="결과 — 되돌아가지 않음", header=HEAD,
         rows=[[r[0], "COMPLETED", r[2]] for r in ORIG], hl_rows=set(), widths=[1600000, 1650000, 1474400],
         notes=[("오류", "cannot rollback - no transaction is active (되돌릴 트랜잭션이 없음)"),
                ("자동 확정", "BEGIN 없이 실행한 문장은 바로 확정됨. 되돌리려면 먼저 BEGIN")]),
]


def main(src, out):
    z = zipfile.ZipFile(src)
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    prels = etree.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    ct = etree.fromstring(z.read("[Content_Types].xml"))
    rid2t = {r.get("Id"): r.get("Target") for r in prels}
    sids = list(pres.find(P + "sldIdLst"))
    paths = ["ppt/" + rid2t[s.get(R + "id")] for s in sids]
    tx = [texts(etree.fromstring(z.read(p))) for p in paths]

    def find(line):
        m = [i for i, x in enumerate(tx) if line in x]
        assert len(m) == 1, (line, m)
        return m[0]

    assert not any(NEW[0]["title"] in x for x in tx), "이미 추가됨"
    i_tmpl = find("2단계 — 값 살펴보기")
    anchor = sids[find("ROLLBACK 해 보기 — 실수를 되돌리기")]
    template = etree.fromstring(z.read(paths[i_tmpl]))
    tmpl_rels = z.read(paths[i_tmpl].replace("slides/", "slides/_rels/") + ".rels")
    assert b"notesSlide" not in tmpl_rels
    nums = [int(m.group(1)) for n in z.namelist() for m in [re.match(r"ppt/slides/slide(\d+)\.xml$", n)] if m]
    max_id = max(int(s.get("id")) for s in sids)
    max_rid = max(int(r.get("Id")[3:]) for r in prels if r.get("Id").startswith("rId"))
    add, repl = {}, {}
    for k, spec in enumerate(NEW, 1):
        n = max(nums) + k
        part = f"ppt/slides/slide{n}.xml"
        add[part] = etree.tostring(build(template, **spec), xml_declaration=True, encoding="UTF-8", standalone=True)
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
        repl["docProps/app.xml"] = app.replace(m.group(0), f"<Slides>{int(m.group(1)) + len(NEW)}</Slides>").encode()
    with zipfile.ZipFile(out, "w") as zo:
        for info in z.infolist():
            zo.writestr(info, repl.get(info.filename, z.read(info.filename)))
        for name, data in add.items():
            zo.writestr(zipfile.ZipInfo(name), data, compress_type=zipfile.ZIP_DEFLATED)
    print(f"10강 트랜잭션: 새 슬라이드 {len(NEW)}장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
