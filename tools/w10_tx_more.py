# -*- coding: utf-8 -*-
"""10강 트랜잭션 설명 보강 + 3장 명령어 강조 (2026-11-03).

- 2. 트랜잭션: '트랜잭션 (Transaction)' 뒤에 2장
    병원 프로그램 속 트랜잭션 ('트랜잭션 (Transaction)' 모양 복제: 전동 = 한 덩어리, [저장] = COMMIT · [취소] = ROLLBACK)
    트랜잭션이 지켜 주는 4가지 ('여기까지 정리' 모양 복제: ACID 를 쉬운 말로)
- 3. COMMIT과 ROLLBACK: 그 장에서 새로 나온 명령어(BEGIN · COMMIT · ROLLBACK)를 9강처럼 노란 강조 + 굵게
    COMMIT과 ROLLBACK 의 BEGIN; · ROLLBACK 해 보기 의 BEGIN; · 주석 앞 공백은 강조에서 뺌
    COMMIT 해 보기 1장 추가 ('ROLLBACK 해 보기' 뒤, 9강 '2단계 — 값 살펴보기' 모양): 확정한 뒤에는 ROLLBACK 이 안 됨
- 숫자는 노트북 10 과 같은 SQL 로 aact_mini 에서 나온 값 (tools/build_nb_w10.py 가 assert)
사용: python3 tools/w10_tx_more.py <덱.pptx> <결과.pptx>
"""
import sys, re, copy, zipfile
from lxml import etree
from w10_slides import A, P, R, PR, CT, SLIDE_T, SLIDE_CT, ORIG, HEAD, texts, sp, set_run, build

HL = "FFF2CC"


def fill(s, spec, sz=None):
    """도형 s 의 문단을 spec = [(본 문단 번호, [런별 글])] 로 바꿈. 본 문단의 런 서식을 앞에서부터 씀"""
    body = s.find(P + "txBody")
    ps = body.findall(A + "p")
    out = []
    for idx, runs in spec:
        p_ = copy.deepcopy(ps[idx])
        rs = p_.findall(A + "r")
        assert len(runs) <= len(rs), (idx, runs)
        for r, txt in zip(rs, runs):
            r.find(A + "t").text = txt
        for r in rs[len(runs):]:
            p_.remove(r)
        if sz:
            for pr in p_.iter(A + "rPr", A + "endParaRPr"):
                pr.set("sz", str(sz))
        out.append(p_)
    for p_ in ps:
        body.remove(p_)
    for p_ in out:
        body.append(p_)


def emph(r):
    """9강 SQL 강조와 같게: 굵게 + 노란 배경"""
    pr = r.find(A + "rPr")
    pr.set("b", "1")
    if pr.find(A + "highlight") is None:
        h = etree.Element(A + "highlight")
        etree.SubElement(h, A + "srgbClr").set("val", HL)
        anchor = pr.find(A + "latin")
        (anchor.addprevious(h) if anchor is not None else pr.append(h))


def emph_para(s, first):
    m = [p_ for p_ in s.iter(A + "p") if "".join(x.text or "" for x in p_.iter(A + "t")) == first]
    assert len(m) == 1, (first, len(m))
    for r in m[0].findall(A + "r"):
        emph(r)


def unhl_gap(s):
    """강조된 런 끝의 공백(주석 앞)을 다음 보통 런으로 옮김"""
    for p_ in s.iter(A + "p"):
        rs = p_.findall(A + "r")
        for a, b in zip(rs, rs[1:]):
            hl = lambda r: r.find(A + "rPr").find(A + "highlight") is not None
            ta = a.find(A + "t")
            if hl(a) and not hl(b) and ta.text != ta.text.rstrip():
                gap = ta.text[len(ta.text.rstrip()):]
                ta.text = ta.text.rstrip()
                b.find(A + "t").text = gap + b.find(A + "t").text


# ---------------------------------------------------------------- 2. 트랜잭션 — 새 2장
def hospital(t):               # '트랜잭션 (Transaction)' 복제
    set_run(t, "트랜잭션 (Transaction)", "병원 프로그램 속 트랜잭션")
    fill(sp(t, "TextBox 5"), [(0, ["EMR ", "", "[저장] 을 한 번 누르면 = 트랜잭션 하나", "."])])
    fill(sp(t, "TextBox 7"), [(0, ["전동 (병동 이동, 한 덩어리)"])])
    fill(sp(t, "Step 8"), [(0, ["① 전 병상을 ‘빈 병상’으로 바꾼다"])])
    fill(sp(t, "Step 9"), [(0, ["② 새 병상을 ‘사용 중’으로 바꾼다"])])
    fill(sp(t, "Step 10"), [(0, ["③ 환자의 병동 기록을 바꾼다"])])
    fill(sp(t, "TextBox 11"), [(0, ["[저장] 을 누르면"]), (2, ["①②③ 이 ", "함께 확정", "  (COMMIT)"]),
                               (3, ["[취소] 하거나 저장 중 오류가 나면"]), (4, ["①②③ 이 ", "모두 없던 일로", "  (ROLLBACK)"])])
    fill(sp(t, "TextBox 12"), [(0, ["사용자는 BEGIN · COMMIT 을 ", "직접 쓰지 않습니다", "."]),
                               (1, ["프로그램이 [저장] · [취소] 버튼 뒤에서 대신 묶어 줍니다", "."])])


def acid(t):                   # '여기까지 정리' 복제
    set_run(t, "여기까지 정리", "트랜잭션이 지켜 주는 4가지")
    set_run(t, "다음으로 넘어가기 전에", "DBMS 가 알아서 지켜 줍니다")
    fill(sp(t, "TextBox 5"), [(0, ["① ", "전부 아니면 전무", "  입원 수속 3가지가 다 되거나, 하나도 안 되거나"]),
                              (0, ["② ", "규칙 지키기", "  NOT NULL · CHECK 같은 규칙을 어기는 변경은 확정되지 않음"]),
                              (0, ["③ ", "서로 섞이지 않기", "  두 사람이 같은 병상을 동시에 배정해도 한 명만 됨"]),
                              (0, ["④ ", "확정하면 남기", "  COMMIT 한 뒤에는 정전이 나도 그대로"])], sz=2200)
    fill(sp(t, "TextBox 7"), [(0, ["이름으로는  ACID  — 원자성 · 일관성 · 고립성 · 지속성"]),
                              (1, ["외울 필요는 없습니다. 5강의 ‘한 칸에 값 하나(원자성)’와는 이름만 같고 뜻이 다릅니다", "."])])


# ---------------------------------------------------------------- 3. COMMIT과 ROLLBACK — 강조 · COMMIT 해 보기
def commit_slide(t):           # COMMIT과 ROLLBACK
    emph_para(sp(t, "TextBox 7"), "BEGIN;")


def rollback_slide(t):         # ROLLBACK 해 보기
    emph_para(sp(t, "SQL"), "BEGIN;")


COMMIT_TRY = dict(title="COMMIT 해 보기 — 확정하면 끝",
                  question="BEGIN 뒤에 바꾸고 COMMIT 한 다음 ROLLBACK 하면?",
                  sql_lines=["BEGIN;", "UPDATE studies_copy SET overall_status = 'COMPLETED'",
                             "WHERE nct_id = 'NCT00623389';", "COMMIT;   -- 확정",
                             "ROLLBACK;   -- 오류", "SELECT * FROM studies_copy ORDER BY nct_id;"],
                  hl_lines={0, 3}, label="결과 — 확정된 그대로", header=HEAD,
                  rows=[list(r) for r in ORIG[:3]] + [["NCT00623389", "COMPLETED", "10"]] + [list(ORIG[4])], hl_rows={3},
                  widths=[1600000, 1650000, 1474400],
                  notes=[("COMMIT 뒤", "NCT00623389 가 COMPLETED 로 확정됨"),
                         ("ROLLBACK", "확정한 뒤라 되돌릴 것이 없음 (no transaction is active)")])


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

    assert not any("병원 프로그램 속 트랜잭션" in x for x in tx), "이미 추가됨"
    i_tx = find("트랜잭션 (Transaction)")
    i_sum = find("여기까지 정리", "② WHERE는 수정·삭제할 대상을 정한다")
    i_commit = find("COMMIT과 ROLLBACK", "확정하거나 되돌리거나")
    i_rb = find("ROLLBACK 해 보기 — 실수를 되돌리기")
    i_tmpl = find("2단계 — 값 살펴보기")
    load = lambda i: etree.fromstring(z.read(paths[i]))
    dump = lambda t: etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True)
    rels_of = lambda i: z.read(paths[i].replace("slides/", "slides/_rels/") + ".rels")

    repl = {}
    for i, fn in ((i_commit, commit_slide), (i_rb, rollback_slide)):
        t = load(i); fn(t); repl[paths[i]] = dump(t)
    for title in ("한 덩어리로 되돌리기 — 두 변경을 함께 취소", "BEGIN 없이 바꾸면 — 바로 확정"):
        i = find(title); t = load(i); unhl_gap(sp(t, "SQL")); repl[paths[i]] = dump(t)

    new = []                   # (앞 슬라이드 sldId, 슬라이드 xml, rels)
    for fn, i_src in ((hospital, i_tx), (acid, i_sum)):
        t = load(i_src); fn(t); new.append((i_tx, t, rels_of(i_src)))
    new.append((i_rb, build(load(i_tmpl), **COMMIT_TRY), rels_of(i_tmpl)))
    for _, _, rl in new:
        assert b"notesSlide" not in rl

    nums = [int(m.group(1)) for n in z.namelist() for m in [re.match(r"ppt/slides/slide(\d+)\.xml$", n)] if m]
    max_id = max(int(s.get("id")) for s in sids)
    max_rid = max(int(r.get("Id")[3:]) for r in prels if r.get("Id").startswith("rId"))
    last = {}
    add = {}
    for k, (i_after, t, rl) in enumerate(new, 1):
        n = max(nums) + k
        part = f"ppt/slides/slide{n}.xml"
        add[part] = dump(t)
        add[f"ppt/slides/_rels/slide{n}.xml.rels"] = rl
        rid = f"rId{max_rid + k}"
        rel = etree.SubElement(prels, PR + "Relationship")
        rel.set("Id", rid); rel.set("Type", SLIDE_T); rel.set("Target", f"slides/slide{n}.xml")
        sid = etree.Element(P + "sldId"); sid.set("id", str(max_id + k)); sid.set(R + "id", rid)
        last.get(i_after, sids[i_after]).addnext(sid); last[i_after] = sid
        ov = etree.SubElement(ct, CT + "Override"); ov.set("PartName", f"/{part}"); ov.set("ContentType", SLIDE_CT)
    repl["ppt/presentation.xml"] = dump(pres)
    repl["ppt/_rels/presentation.xml.rels"] = dump(prels)
    repl["[Content_Types].xml"] = dump(ct)
    app = z.read("docProps/app.xml").decode()
    m = re.search(r"<Slides>(\d+)</Slides>", app)
    if m:
        repl["docProps/app.xml"] = app.replace(m.group(0), f"<Slides>{int(m.group(1)) + len(new)}</Slides>").encode()
    with zipfile.ZipFile(out, "w") as zo:
        for info in z.infolist():
            zo.writestr(info, repl.get(info.filename, z.read(info.filename)))
        for name, data in add.items():
            zo.writestr(zipfile.ZipInfo(name), data, compress_type=zipfile.ZIP_DEFLATED)
    print(f"10강: 강조 · 공백 4장 고침, 새 슬라이드 {len(new)}장 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
