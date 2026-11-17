# -*- coding: utf-8 -*-
"""12강 학습 목표 ① · ② 와 「원무 업무와 남는 자료」 낱말 (2026-11-17).

'남는 자료' → '남는 기록' (다음 장 「입원 표의 한 행 — 환자 한 명의 입원 기록」과 같은 말),
'나눠 센다' → '구분해 산정한다'. 런 하나의 글 전체가 같을 때만 바꾸고, 다르면 멈춤.
사용: python3 tools/w12_goal_words.py <덱.pptx> <결과.pptx>
"""
import sys
from slidekit import A, Deck

GOAL, DESK = "12주차 학습 목표", "원무 업무와 남는 자료"
EDITS = [
    (GOAL, "① 원무 업무와 남는 자료를 말할 수 있다", "① 원무 업무마다 남는 기록을 말할 수 있다"),
    (GOAL, "② 입원 건수와 환자 수를 나눠 센다", "② 입원 건수와 환자 수를 구분해 산정한다"),
    (DESK, "원무 업무와 남는 자료", "원무 업무마다 남는 기록"),
    (DESK, "남는 자료 (가상 병원 CDW)", "남는 기록 (가상 병원 CDW)"),
]


def main(src, out):
    d = Deck(src)
    slides = {k: d.find(k) for k in (GOAL, DESK)}       # 제목이 바뀌기 전에 찾아 둠
    for key, old, new in EDITS:
        runs = [t for t in d.tree(slides[key]).iter(A + "t") if t.text == old]
        assert len(runs) == 1, (key, old, len(runs))
        runs[0].text = new
    d.save(out)
    print(f"12강 낱말 {len(EDITS)}곳 → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
