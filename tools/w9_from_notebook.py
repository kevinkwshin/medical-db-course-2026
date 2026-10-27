# -*- coding: utf-8 -*-
"""9강 슬라이드를 9주차 노트북(notebooks/09_실습_질문을SQL로.ipynb)에 맞춥니다 (2026-10-27 강사 결정).

노트북이 기준입니다. 노트북을 만든 10/20 9강 슬라이드(백업 덱)를 가져와, 노트북에서 지운 설명을
슬라이드에서도 지우고 바뀐 SQL · 문구를 노트북과 같게 고친 뒤, 지금 덱의 9강 자리(같은 슬라이드 파일 이름)에
덮어씁니다. '같은 질문, 다른 답' 슬라이드는 빠지므로 28장 → 27장 (지금 덱의 9강도 27장).

사용: python3 tools/w9_from_notebook.py <지금 덱.pptx> <10/20 백업 덱.pptx> <결과.pptx>
- 편집마다 정확히 한 곳에만 맞는지 확인합니다 (안 맞으면 멈춤).
- 9강 슬라이드 파일(slideN.xml · rels)만 바꾸고, 다른 파일은 그대로 같은 순서 · 압축으로 씁니다.
"""
import sys, zipfile
from lxml import etree

NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P, A, R = "{%s}" % NS_P, "{%s}" % NS_A, "{%s}" % NS_R


def slide_paths(z):
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    rels = etree.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rels}
    out = []
    for s in pres.find(P + "sldIdLst"):
        t = rid2t[s.get(R + "id")]
        out.append(t[1:] if t.startswith("/") else "ppt/" + t)
    return out


def paras(t):
    return ["".join(x.text or "" for x in p.iter(A + "t")) for p in t.iter(A + "p")]


def week9(z, paths):
    """[9강 표지, 10강 표지) 범위 — 문단 전체가 표지 제목과 같은 슬라이드로 찾음"""
    ps = [paras(etree.fromstring(z.read(p))) for p in paths]
    s = [i for i, x in enumerate(ps) if "9강. 의료데이터 SQL 실습" in x]
    e = [i for i, x in enumerate(ps) if "10강. 안전한 데이터 수정과 트랜잭션" in x]
    assert len(s) == 1 and len(e) == 1 and s[0] < e[0], (s, e)
    return s[0], e[0]


# ---------------------------------------------------------------- 편집 도구 (모두 정확히 한 곳만)
def shapes(t):
    return list(t.iter(P + "sp"))


def sp_text(sp):
    return "\n".join(paras(sp)).strip()


def del_shape(t, text=None, startswith=None):
    m = [sp for sp in shapes(t) if (text is not None and sp_text(sp) == text)
         or (startswith is not None and sp_text(sp).startswith(startswith))]
    assert len(m) == 1, ("del_shape", text or startswith, len(m))
    m[0].getparent().remove(m[0])
    return m[0]


def del_para(t, startswith):
    m = [p for p in t.iter(A + "p") if "".join(x.text or "" for x in p.iter(A + "t")).startswith(startswith)]
    assert len(m) == 1, ("del_para", startswith, len(m))
    body = m[0].getparent()
    body.remove(m[0])
    if not body.findall(A + "p"):                 # 문단이 하나도 없으면 도형째 지움
        sp = body.getparent()
        sp.getparent().remove(sp)


def rep(t, old, new):
    """한 run(a:t) 안의 글자를 바꿈"""
    m = [x for x in t.iter(A + "t") if x.text and old in x.text]
    assert len(m) == 1 and m[0].text.count(old) == 1, ("rep", old, len(m))
    m[0].text = m[0].text.replace(old, new)


def set_run(t, old, new):
    """run 글자 전체가 old 와 같은 곳을 new 로"""
    m = [x for x in t.iter(A + "t") if x.text == old]
    assert len(m) == 1, ("set_run", old, len(m))
    m[0].text = new


def drop_run(t, text):
    m = [x for x in t.iter(A + "t") if x.text == text]
    assert len(m) == 1, ("drop_run", text, len(m))
    r = m[0].getparent()
    r.getparent().remove(r)


def set_para(t, old, new):
    """문단 글자 전체가 old 인 곳을 new 한 run 으로 (첫 run 의 글꼴 유지)"""
    m = [p for p in t.iter(A + "p") if "".join(x.text or "" for x in p.iter(A + "t")) == old]
    assert len(m) == 1, ("set_para", old, len(m))
    runs = m[0].findall(A + "r")
    runs[0].find(A + "t").text = new
    for r in runs[1:]:
        m[0].remove(r)


def move_y(t, startswith_or_name, y):
    m = [sp for sp in shapes(t) if sp.find(f"{P}nvSpPr/{P}cNvPr").get("name") == startswith_or_name
         or sp_text(sp).startswith(startswith_or_name)]
    assert len(m) == 1, ("move_y", startswith_or_name, len(m))
    m[0].find(f".//{A}off").set("y", str(y))


def agenda(t):
    """오늘의 순서 3번: '병원 SQL 사례  실제로 이렇게 씁니다' → '병원에서 활용하는 SQL 예제' (노트북 3절 제목)"""
    set_run(t, "병원 SQL 사례", "병원에서 활용하는 SQL 예제")
    m = [x for x in t.iter(A + "t") if x.text and x.text.strip() == "실제로 이렇게 씁니다"
         and x.getparent().getparent().find(A + "r") is not x.getparent()]   # 같은 문단의 둘째 run
    assert len(m) == 1, ("agenda", len(m))
    r = m[0].getparent()
    r.getparent().remove(r)


# ---------------------------------------------------------------- 10/20 9강 (표지 0번 기준 순서) → 노트북에 맞춘 편집
def edit(i, t):
    """i: 10/20 9강 안에서의 순서 (0 = 표지). 노트북과 같게 고침. None 을 돌려주면 그 슬라이드를 뺌"""
    if i == 5:                                     # 같은 질문, 다른 답 — 노트북에서 지움
        assert "같은 질문, 다른 답" in paras(t)
        return None
    if i == 2:                                     # 학습 목표 · 오늘의 순서
        agenda(t)
        del_shape(t, "과제 1 (20점) — 7 · 8주차 범위, 9주차 수업 후 1주일 이내 LMS 제출")
    if i in (3, 8, 18, 21, 23, 25):                # 절 구분 슬라이드의 순서 목록
        agenda(t)
    if i == 25:                                    # 6절 구분의 2번 항목만 옛 부제로 남아 있던 것을 다른 슬라이드와 같게
        rep(t, "질환별 임상시험 현황", "데이터 파악부터 보고까지")
    if i == 4:                                     # 다섯 단계 절차: 마지막 줄 → 노트북 문장 ('같은 질문, 다른 답'에서 옮겨 온 줄)
        set_para(t, "SQL을 먼저 쓰지 말고, ①②③을 말이나 글로 먼저 적는 것이 가장 빠릅니다.",
                 "분석을 요청받으면 먼저 네 가지를 되묻습니다: 대상 · 기간 · 조건 · 세는 단위.")
    if i == 7:                                     # 서브쿼리와 JOIN
        del_shape(t, "같은 답이 나오지만 쓰임이 다릅니다")
    if i == 9:                                     # 0단계
        del_shape(t, "분석 전에 어떤 표 · 열이 있고, 한 행이 무엇인지 확인합니다")
        set_run(t, "SHOW TABLES", "SELECT * FROM (SHOW TABLES)")     # 노트북처럼 감싸서 결과가 보이게
        set_run(t, "DESCRIBE", "SELECT * FROM (DESCRIBE")
        set_run(t, " studies;", " studies);")
        rep(t, "1쌍입니다 (7강 ERD).", "1쌍입니다.")
    if i == 10:                                    # 1단계
        del_shape(t, "질문에 맞는 대상이 몇 건인지 먼저 셉니다")
        rep(t, " 이 자료에서는 둘이 같습니다 (1,353 = 1,353).", "")
        del_para(t, "대상  제2형 당뇨병 시험 1,353건")
    if i == 11:                                    # 2단계
        del_shape(t, "쓸 열마다 빈 값과 값의 종류를 확인합니다")
        rep(t, "등록 인원은 빈 값 0건, 단계는 빈 값 242건. 단계의 글자 'NA'는 DISTINCT phase로 확인합니다.",
            "등록 인원은 빈 값이 없습니다. 단계는 빈 값이 242건이고, 글자 'NA' 도 값으로 들어 있습니다.")
        del_para(t, "DuckDB  SUMMARIZE")
    if i == 12:                                    # 3단계 — 빼는 SQL(AND enrollment IS NOT NULL)을 보이게
        del_shape(t, "2단계에서 찾은 빈 값을 분석에서 빼고, 뺀 건수를 기록합니다")
        set_para(t, "-- 분석에서는 WHERE enrollment IS NOT NULL 을 붙입니다",
                 "-- 빼기: WHERE 끝에 AND enrollment IS NOT NULL")
        rep(t, " (12강 오류 8)", "")
        rep(t, "‘등록 인원 빈 값 0건 제외’를 보고서에 적습니다. 7단계에서 다시 씁니다.", "뺀 건수를 보고서에 적습니다.")
    if i == 13:                                    # 4단계
        del_shape(t, "뒤의 분석에 쓸 열만 골라, 한 행 = 시험 1건인 표로 저장합니다")
        set_run(t, "CREATE TEMP TABLE", "CREATE OR REPLACE TEMP TABLE")
        rep(t, "IN(서브쿼리)로도 만들 수 있지만, ", "")
    if i == 14:                                    # 5단계
        del_shape(t, "분석표 하나로 논문 ‘표 1’의 기술통계를 한 번에 냅니다")
    if i == 15:                                    # 6단계
        del_shape(t, "분석표에서 분모와 분자를 정하고, 하위 집단끼리 비교합니다")
        del_para(t, "100.0을 곱하면")
        rep(t, " CASE WHEN은 8강에서 배웠습니다.", "")
        rep(t, "판단합니다 → 7단계에서 내보내기", "판단합니다.")
    if i == 16:                                    # 7단계
        del_shape(t, "숫자와 함께 ‘어떻게 정리했는지’를 적어야 결과를 믿을 수 있습니다")
    if i == 17:                                    # 여기까지 정리 → 잠깐 생각해 봅시다 (노트북과 같게)
        drop_run(t, "잠깐 생각해 봅시다")              # 제목과 겹치는 앞 글자 (제목을 바꾸기 전에 지움)
        set_run(t, "여기까지 정리", "잠깐 생각해 봅시다")
        del_shape(t, "다음으로 넘어가기 전에")
        del_shape(t, startswith="① 준비:")
        rep(t, "  4단계 분석표의 행 수가", "4단계 분석표의 행 수가")
        move_y(t, "Q 6", 1600000)
        move_y(t, "4단계 분석표의 행 수가", 1790000)
    if i == 18:                                    # 3절 구분: 병원 SQL 사례 → 병원에서 활용하는 SQL 예제
        set_run(t, "3. 병원 SQL 사례", "3. 병원에서 활용하는 SQL 예제")
        del_shape(t, "실제로 이렇게 씁니다")
    if i == 19:                                    # 병원에서 SQL을 쓰는 일
        del_shape(t, "실제로 이런 숫자를 SQL로 뽑습니다")
        drop_run(t, "코호트 = 같은 조건으로 묶어 분석 대상으로 삼은 집단 (13주차에서 자세히).")
    if i == 20:                                    # 사례 — 30일 재입원율
        del_shape(t, "QI 지표를 SQL로 만들면")
        del_shape(t, startswith="어려운 부분은 SQL 문법이 아니라")
    if i == 22:                                    # 검산
        del_shape(t, "다섯 가지만 확인하면 대부분 걸러집니다")
        del_shape(t, "결과를 보고서에 쓰기 전에 반드시 확인하는 다섯 가지입니다.")
        del_shape(t, startswith="숫자가 틀리는 것보다")
    return t


def main(cur, bak, out):
    zc, zb = zipfile.ZipFile(cur), zipfile.ZipFile(bak)
    pc, pb = slide_paths(zc), slide_paths(zb)
    cs, ce = week9(zc, pc)
    bs, be = week9(zb, pb)
    assert (be - bs) == 28, be - bs
    new = []
    for i, path in enumerate(pb[bs:be]):
        t = edit(i, etree.fromstring(zb.read(path)))
        if t is not None:
            rels = zb.read(path.replace("slides/", "slides/_rels/") + ".rels")
            assert b"notesSlide" not in rels and b"image" not in rels, path
            new.append((etree.tostring(t, xml_declaration=True, encoding="UTF-8", standalone=True), rels))
    targets = pc[cs:ce]
    assert len(new) == len(targets) == 27, (len(new), len(targets))
    repl = {}
    for (xml, rels), path in zip(new, targets):
        old_rels = zc.read(path.replace("slides/", "slides/_rels/") + ".rels")
        assert b"notesSlide" not in old_rels, path       # 지금 9강에는 노트가 없음 (있으면 따로 처리해야 함)
        repl[path] = xml
        repl[path.replace("slides/", "slides/_rels/") + ".rels"] = rels
    with zipfile.ZipFile(out, "w") as zo:
        for info in zc.infolist():
            data = repl.get(info.filename, zc.read(info.filename))
            zo.writestr(info, data)
    print(f"9강: 지금 덱 {cs + 1}~{ce} 번 슬라이드 {len(targets)}장을 노트북 기준 9강 {len(new)}장으로 바꿈 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
