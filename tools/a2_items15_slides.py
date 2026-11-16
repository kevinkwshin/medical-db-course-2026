# -*- coding: utf-8 -*-
"""과제 2 슬라이드 글 — 15문항 · 20점(1점 10 + 2점 5)으로 바꾼 것에 맞춤 (2026-11-16, a2_duty_slides.py 다음에 실행).

12강 「과제 2 안내」 · 13강 「과제 2 제출 안내」 · 「과제 2를 할 때 자주 막히는 부분」. 런 하나 안의 글만 바꾸고, 지금 글이 다르면 멈춤.
사용: python3 tools/a2_items15_slides.py <덱.pptx> <결과.pptx>
"""
import sys
from slidekit import A, Deck, shape

GUIDE, SUBMIT, STUCK = "과제 2 안내", "과제 2 제출 안내", "과제 2를 할 때 자주 막히는 부분"
EDITS = [
    (GUIDE, "TextBox 4", "20점 · 10문항 × 2점", "20점 · 15문항"),
    (GUIDE, "TextBox 7", "낙상률 (S1~S3)", "낙상률 (S1~S5)"),
    (GUIDE, "TextBox 7", "간호사 근무시간 · 근무조별 초과근무 (S4 · S5)", "간호사 근무시간 · 초과근무 (S6~S8)"),
    (GUIDE, "TextBox 7", "(E1~E3)", "(E1~E4)"),
    (GUIDE, "TextBox 7", "검산표 INSERT · UPDATE (T1 · T2)", "검산표 UPDATE · INSERT · DELETE (T1~T3)"),
    (GUIDE, "TextBox 10", "S1~S5 단계별 SQL  각 2점 (10점)", "S1~S8 단계별 SQL  10점 (S6 · S7 2점)"),
    (GUIDE, "TextBox 10", "E1~E3 동료 SQL 점검  각 2점 (6점)", "E1~E4 동료 SQL 점검  7점 (E3 1점)"),
    (GUIDE, "TextBox 10", "T1 · T2 검산표  각 2점 (4점)", "T1~T3 검산표  각 1점 (3점)"),
    (SUBMIT, "TextBox 4", "20점 · 10문항 × 2점", "20점 · 15문항"),
    (SUBMIT, "TextBox 5", "S1~S5 · E1~E3 · T1 · T2 — 10문항이", "S1~S8 · E1~E4 · T1~T3 — 15문항이"),
    (SUBMIT, "TextBox 5", "문항마다 2점, 합계 20점", "문항마다 1점 또는 2점, 합계 20점"),
    (STUCK, "TextBox 5", "S4 · S5 는 12주차 수술시간과 같은 DATEDIFF, E 는 12주차, T 는 10주차 UPDATE · INSERT 로.",
     "S4 · S5 는 8 · 9주차 HAVING · IN, S6~S8 은 12주차 수술시간과 같은 DATEDIFF, E 는 11 · 12주차, T 는 10주차 UPDATE · INSERT · DELETE 로."),
    (STUCK, "TextBox 5", "시간 단위(분 · 시간) · 날짜 계산(일 수)", "JOIN 뒤 행 수 · 시간 단위(분 · 시간) · 날짜 계산(일 수)"),
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
