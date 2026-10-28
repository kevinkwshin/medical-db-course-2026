# -*- coding: utf-8 -*-
"""수업용 셀 번호 — 실행하는 코드 셀마다 [1번], [2번] … 을 붙입니다 (빌드가 끝난 뒤 실행).

    python3 tools/number_cells.py            # notebooks/*.ipynb 와 notebooks/instructor/*.ipynb

- 준비 셀(#@title)  → 제목 앞:      #@title [1번] ▶ 준비 셀 …
- %%sql 셀          → 첫 주석 줄:   -- [12번] 완료된 시험만   (주석이 없으면 한 줄 추가)
- 한 줄짜리 셀      → 줄 끝:        check("Q1", _)   # [13번]
- 그 밖의 코드 셀   → 맨 위 한 줄:  # [14번]
번호는 주석이라 실행 · 채점에 영향이 없습니다 (check() 는 [n번] 을 건너뛰고 -- Q1 이름표를 읽음).
다시 실행해도 번호가 겹치지 않도록 기존 번호를 지운 뒤 새로 붙입니다.
"""
import glob, os, re
import nbformat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL = re.compile(r"\[\d+번\] ?")


def _strip(src):
    lines = src.split("\n")
    lines = [l for l in lines if not re.fullmatch(r"(#|--) \[\d+번\]", l.strip())]     # 따로 넣은 번호 줄
    lines = [re.sub(r"\s+# \[\d+번\]$", "", l) for l in lines]                           # 줄 끝 번호
    lines = [LABEL.sub("", l, count=1) if l.startswith(("#@title", "-- ")) else l for l in lines]
    return "\n".join(lines)


def _label(src, n):
    tag = f"[{n}번]"
    lines = src.split("\n")
    if lines[0].startswith("#@title "):
        lines[0] = "#@title " + tag + " " + lines[0][len("#@title "):]
    elif lines[0].startswith("%%sql"):
        if len(lines) > 1 and lines[1].lstrip().startswith("--"):
            lines[1] = "-- " + tag + " " + lines[1].lstrip()[2:].lstrip()
        else:
            lines.insert(1, "-- " + tag)
    elif len(lines) == 1:
        lines[0] = lines[0] + "   # " + tag
    else:
        lines.insert(0, "# " + tag)
    return "\n".join(lines)


def number(path):
    nb = nbformat.read(path, as_version=4)
    n = 0
    for c in nb.cells:
        if c.cell_type != "code":
            continue
        n += 1
        c.source = _label(_strip(c.source), n)
    nbformat.write(nb, path)
    return n


if __name__ == "__main__":
    paths = sorted(glob.glob(os.path.join(ROOT, "notebooks", "*.ipynb")) +
                   glob.glob(os.path.join(ROOT, "notebooks", "instructor", "*.ipynb")))
    paths = [p for p in paths if not os.path.basename(p).startswith("과제")]   # 과제에는 셀 번호 없음 (강사 요청 2026-10-28)
    for p in paths:
        print(f"{number(p):4d} cells  {os.path.relpath(p, ROOT)}")
