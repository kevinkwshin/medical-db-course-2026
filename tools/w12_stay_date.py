# -*- coding: utf-8 -*-
"""12강 「재원 중 환자 — 퇴원일이 비어 있음」: 질문에 '자료 마지막 날' + 아래에 날짜 한 줄 (2026-11-17).

SQL(WHERE 퇴원일 IS NULL)은 그대로. 자료가 2024-12-31까지라 '퇴원일이 비어 있음 = 그날 재원 중'이고,
다른 날은 병동일보로 센다는 것을 적음. 지금 글이 다르면 멈춤.
사용: python3 tools/w12_stay_date.py <덱.pptx> <결과.pptx>
"""
import copy
import sys
from slidekit import A, P, Deck, shape

TITLE = "재원 중 환자 — 퇴원일이 비어 있음"
Q_OLD = "  12월 31일에 아직 재원 중인 환자는 병동별로 몇 명?"
Q_NEW = "  자료 마지막 날(12월 31일) 현재 재원 중인 환자는 병동별로 몇 명?"
DATE_LINE = ("날짜", "  자료가 12월 31일까지라 ‘비어 있음 = 그날 재원’. 다른 날은 병동일보로 (4절)")


def main(src, out):
    d = Deck(src)
    t = d.tree(d.find(TITLE))
    q = [r for r in shape(t, "Q").iter(A + "t") if r.text == Q_OLD]
    assert len(q) == 1, len(q)
    q[0].text = Q_NEW

    p_ = shape(t, "Chk").find(f"{P}txBody/{A}p")       # 'IS NULL …' <br> '확인 …' 한 문단
    rs, brs = p_.findall(A + "r"), p_.findall(A + "br")
    assert len(rs) == 4 and len(brs) == 1 and [r.find(A + "t").text for r in rs][::2] == ["IS NULL", "확인"]
    br, lab, txt = (copy.deepcopy(x) for x in (brs[0], rs[2], rs[3]))
    lab.find(A + "t").text, txt.find(A + "t").text = DATE_LINE
    end = p_.find(A + "endParaRPr")
    for x in (br, lab, txt):
        end.addprevious(x)
    d.save(out)
    print(f"12강 「{TITLE}」 질문 + 날짜 한 줄 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
