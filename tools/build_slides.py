# -*- coding: utf-8 -*-
"""주차별 슬라이드 PDF 일괄 빌드: python3 build_slides.py [주차번호 ...]"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "weeks"))
from slide_lib import render_deck  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "..", "slides")
ALL_WEEKS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]


def build(week_no):
    mod = importlib.import_module(f"week{week_no:02d}")
    out_pdf = os.path.join(OUT, f"week{week_no:02d}.pdf")
    render_deck(week_no, mod.TITLE, mod.slides, out_pdf)
    print(f"  week{week_no:02d}: {len(mod.slides)} slides → {out_pdf}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    targets = [int(a) for a in sys.argv[1:]] or ALL_WEEKS
    for w in targets:
        build(w)
