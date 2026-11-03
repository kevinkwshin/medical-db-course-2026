# -*- coding: utf-8 -*-
"""11강: 도입부에 CDW 이름 풀이 슬라이드 · '수업에서 쓰는 가상 CDW 표' 안내 글 고침 (2026-11-03 강사 요청).

- 새 슬라이드 'CDW — Clinical Data Warehouse' ('1. CDW란 무엇인가' 구분 슬라이드 바로 뒤, 11강 '여기까지 정리' 모양 복제)
    Clinical (임상) · Data (데이터) · Warehouse (창고) 로 이름을 풀고, 한 줄 정의 + 1강 병원 정보 시스템과 연결
- '수업에서 쓰는 가상 CDW 표' 부제: 10강은 이제 이 표를 쓰지 않음 (studies_copy) → NOTE_290
사용: python3 tools/w11_revise.py <덱.pptx> <결과.pptx>
"""
import sys, re, zipfile
from lxml import etree
from w10_slides import P, R, PR, CT, SLIDE_T, SLIDE_CT, texts, sp, set_run
from w10_tx_more import fill

OLD_290 = "10 · 12 · 13강의 개념 예시는 이 네 표를 씁니다 (실습 DB에는 없음)"
NOTE_290 = "12 · 13강의 병원 예시는 이 네 표를 씁니다 (실습 DB에는 없음)"


def cdw_intro(t):              # 11강 '여기까지 정리' 복제
    set_run(t, "여기까지 정리", "CDW — Clinical Data Warehouse")
    set_run(t, "다음으로 넘어가기 전에", "임상데이터웨어하우스 — 이름부터 풀어 봅니다")
    fill(sp(t, "TextBox 5"), [(0, ["① ", "Clinical (임상)", "   진료 현장에서 생긴"]),
                              (0, ["② ", "Data (데이터)", "   진료 기록 · 처방 · 검사 결과 · 영상 · 수납 기록을"]),
                              (0, ["③ ", "Warehouse (창고)", "   분석 · 연구용으로 한곳에 모아 둔 곳"])], sz=2400)
    fill(sp(t, "TextBox 7"), [(0, ["한 줄로", "  CDW = 진료 데이터를 분석 · 연구용으로 모아 둔 데이터베이스"]),
                              (1, ["1강에서 본 병원 정보 시스템(EMR · OCS · LIS · PACS) 가운데 분석 · 연구를 맡는 곳입니다."])])


def main(src, out):
    z = zipfile.ZipFile(src)
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    prels = etree.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    ct = etree.fromstring(z.read("[Content_Types].xml"))
    rid2t = {r.get("Id"): r.get("Target") for r in prels}
    sids = list(pres.find(P + "sldIdLst"))
    paths = ["ppt/" + rid2t[s.get(R + "id")] for s in sids]
    tx = [texts(etree.fromstring(z.read(p))) for p in paths]

    def find(line, also=None):
        m = [i for i, x in enumerate(tx) if line in x and (also is None or also in x)]
        assert len(m) == 1, (line, m)
        return m[0]

    assert not any("CDW — Clinical Data Warehouse" in x for x in tx), "이미 추가됨"
    i_sec = find("1. CDW란 무엇인가")
    i_tmpl = find("여기까지 정리", "① CDW = 분석용으로 따로 모아 둔 읽기 전용 복사본")
    i_290 = find("수업에서 쓰는 가상 CDW 표")
    dump = lambda t: etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True)
    t = etree.fromstring(z.read(paths[i_290]))
    set_run(t, OLD_290, NOTE_290)
    repl = {paths[i_290]: dump(t)}

    t = etree.fromstring(z.read(paths[i_tmpl])); cdw_intro(t)
    rels = z.read(paths[i_tmpl].replace("slides/", "slides/_rels/") + ".rels")
    assert b"notesSlide" not in rels
    nums = [int(m.group(1)) for n in z.namelist() for m in [re.match(r"ppt/slides/slide(\d+)\.xml$", n)] if m]
    n = max(nums) + 1
    part = f"ppt/slides/slide{n}.xml"
    rid = f"rId{max(int(r.get('Id')[3:]) for r in prels if r.get('Id').startswith('rId')) + 1}"
    rel = etree.SubElement(prels, PR + "Relationship")
    rel.set("Id", rid); rel.set("Type", SLIDE_T); rel.set("Target", f"slides/slide{n}.xml")
    sid = etree.Element(P + "sldId"); sid.set("id", str(max(int(s.get("id")) for s in sids) + 1)); sid.set(R + "id", rid)
    sids[i_sec].addnext(sid)
    ov = etree.SubElement(ct, CT + "Override"); ov.set("PartName", f"/{part}"); ov.set("ContentType", SLIDE_CT)
    repl["ppt/presentation.xml"] = dump(pres)
    repl["ppt/_rels/presentation.xml.rels"] = dump(prels)
    repl["[Content_Types].xml"] = dump(ct)
    app = z.read("docProps/app.xml").decode()
    m = re.search(r"<Slides>(\d+)</Slides>", app)
    if m:
        repl["docProps/app.xml"] = app.replace(m.group(0), f"<Slides>{int(m.group(1)) + 1}</Slides>").encode()
    with zipfile.ZipFile(out, "w") as zo:
        for info in z.infolist():
            zo.writestr(info, repl.get(info.filename, z.read(info.filename)))
        zo.writestr(zipfile.ZipInfo(part), dump(t), compress_type=zipfile.ZIP_DEFLATED)
        zo.writestr(zipfile.ZipInfo(f"ppt/slides/_rels/slide{n}.xml.rels"), rels, compress_type=zipfile.ZIP_DEFLATED)
    print(f"11강: CDW 이름 풀이 1장 추가 · 가상 CDW 표 안내 글 고침 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
