# -*- coding: utf-8 -*-
"""과제 2 슬라이드 글 — S4 · S5 · E1 을 근무시간 문항으로 바꾼 것에 맞춤 (2026-11-16).

12강 「과제 2 안내」 2줄 · 13강 「과제 2를 할 때 자주 막히는 부분」 2줄. 런 하나 안의 글만 바꾸고, 지금 글이 다르면 멈춤.
사용: python3 tools/a2_duty_slides.py <덱.pptx> <결과.pptx>
"""
import sys
from slidekit import A, Deck, shape

EDITS = [
    ("과제 2 안내", "TextBox 7", "낙상 발생률 구하기", "낙상 발생률 · 초과근무 구하기"),
    ("과제 2 안내", "TextBox 7", "근무조별 낙상 · 낙상 입원의 재원일수", "간호사 근무시간 · 근무조별 초과근무"),
    ("과제 2를 할 때 자주 막히는 부분", "TextBox 5", "S4 · S5 는 GROUP BY · 재원일수(12주차)", "S4 · S5 는 12주차 수술시간과 같은 DATEDIFF"),
    ("과제 2를 할 때 자주 막히는 부분", "TextBox 5", "세는 단위(중복)", "시간 단위(분 · 시간)"),
]


def main(src, out):
    d = Deck(src)
    for title, box, old, new in EDITS:
        runs = [t for t in shape(d.tree(d.find(title)), box).iter(A + "t") if old in (t.text or "")]
        assert len(runs) == 1, (title, old, len(runs))
        runs[0].text = runs[0].text.replace(old, new)
    d.save(out)
    print(f"과제 2 슬라이드 글 {len(EDITS)}곳 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
