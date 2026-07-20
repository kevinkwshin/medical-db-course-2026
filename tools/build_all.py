# -*- coding: utf-8 -*-
"""전체 빌드 단일 진입점: 슬라이드 → 통합본 병합 → 문서 → 노트북 → 검증
실행: cd tools && python3 build_all.py
(데이터 재생성은 의도적으로 제외 — 결과가 바뀌므로 mini_emr/generate_mini_emr.py를 직접 실행)
"""
import glob
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SLIDES = os.path.abspath(os.path.join(BASE, "..", "slides"))


def sh(desc, args, cwd=BASE):
    print(f"== {desc}")
    subprocess.run(args, cwd=cwd, check=True)


if __name__ == "__main__":
    py = sys.executable
    sh("슬라이드 13개 덱", [py, "build_slides.py"])

    from build_slides import ALL_WEEKS               # 병합 목록은 한 곳에서만 정의
    parts = [os.path.join(SLIDES, f"week{w:02d}.pdf") for w in ALL_WEEKS]
    sh("통합본 병합", ["pdfunite", *parts, os.path.join(SLIDES, "전체_통합본.pdf")])

    sh("명세서·강의계획서", [py, "build_docs.py"])
    sh("노트북·SQL 스크립트", [py, "build_notebooks.py"])

    removed = 0
    for p in (glob.glob(os.path.join(SLIDES, "*.html"))
              + glob.glob(os.path.join(BASE, "..", "*.html"))
              + glob.glob(os.path.join(BASE, "..", "mini_emr", "*.html"))):
        os.remove(p); removed += 1
    print(f"== 빌드 부산물 정리 ({removed}개 html)")

    sh("자동 검증", [py, "run_checks.py"])
    print("\n빌드 완료 — git add/commit/push로 배포하세요.")
