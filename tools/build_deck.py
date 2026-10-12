# -*- coding: utf-8 -*-
"""전체 덱 빌드 — 원본에서 시작해 주차 모듈(w4, w5, …)이 담당하는 구간만 교체합니다.

    python3 tools/build_deck.py            # 준비된 주차를 모두 다시 빌드
    python3 tools/build_deck.py 4 5        # 특정 주차만 (나머지 주차는 원본 유지)
"""
import importlib, os, re, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from deckgen import Deck
from wk_common import Ctx

SRC = os.path.join(ROOT, "데이터베이스관리_수정본_개편_최종.pptx")
OUT = os.path.join(ROOT, "데이터베이스관리_수정본_개편_최종_v2.pptx")
WORK = os.path.join(HERE, "_work")

ALL_WEEKS = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]



TITLE_OFF = '<a:off x="806418" y="314526"/>'      # 1~3주차에서 쓰는 표준 제목 위치
TITLE_START = 53                                   # 4주차 첫 슬라이드 (그 앞은 손대지 않음)


def normalize_titles(work, final):
    """4주차 이후 모든 슬라이드의 제목을 같은 위치 · 같은 글자색 · 같은 크기로 맞춥니다.

    원본에서 가져온 슬라이드는 제목이 조금 위 · 왼쪽(648228, 235465)에 있고
    남색(001F5F)이 직접 지정되어 있어, 생성한 슬라이드와 나란히 놓으면 눈에 띕니다.
    """
    fixed = []
    for i, name in enumerate(final, 1):
        if i < TITLE_START:
            continue
        path = os.path.join(work, "ppt", name if name.startswith("slides/") else "slides/" + name)
        x = open(path, encoding="utf-8").read()
        m = next((m for m in re.finditer(r"<p:sp>.*?</p:sp>", x, re.S)
                  if 'type="title"' in m.group(0)), None)
        if m is None:
            continue
        sp = before = m.group(0)
        sp = re.sub(r'<a:off x="-?\d+" y="-?\d+"/>', TITLE_OFF, sp, count=1)
        sp = re.sub(r'<a:solidFill><a:srgbClr val="001F5F"/></a:solidFill>', "", sp)
        sp = sp.replace('sz="3517"', 'sz="3520"')
        if sp != before:
            open(path, "w", encoding="utf-8").write(x[:m.start()] + sp + x[m.end():])
            fixed.append(i)
    if fixed:
        print(f"  제목 서식 통일: {len(fixed)}장 {fixed}")


def available_weeks():
    return [w for w in ALL_WEEKS if os.path.exists(os.path.join(HERE, f"w{w}.py"))]


def main():
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or available_weeks()
    mods = []
    for w in want:
        try:
            mods.append((w, importlib.import_module(f"w{w}")))
        except ModuleNotFoundError:
            sys.exit(f"w{w}.py 가 없습니다.")
    mods.sort(key=lambda m: m[1].SPAN[0])

    shutil.rmtree(WORK, ignore_errors=True)
    zipfile.ZipFile(SRC).extractall(WORK)
    d = Deck(WORK)
    old = d.order()
    c = Ctx(d, WORK, old)

    final, cursor, spans = [], 0, []
    for w, mod in mods:
        start, end = mod.SPAN                     # 원본 1-indexed 구간
        final += old[cursor:start - 1]            # 손대지 않는 앞 구간
        c.W = []
        mod.build(c)
        spans.append((w, len(final) + 1, len(final) + len(c.W)))
        final += c.W
        print(f"  {w}주차: {len(c.W):3d}장   (덱에서 {spans[-1][1]}~{spans[-1][2]}번)")
        cursor = end
    final += old[cursor:]

    normalize_titles(WORK, final)
    d.set_order(final)
    d.save_meta()
    env = {**os.environ, "PYTHONPATH": os.path.join(HERE, "pkg")}
    r = subprocess.run([sys.executable, os.path.join(HERE, "office39", "clean39.py"), WORK],
                       capture_output=True, text=True, env=env)
    if r.returncode:
        print("clean 경고:", r.stderr[-300:])
    Deck(WORK).zip(OUT)
    print(f"완료: {OUT}  (총 {len(Deck(WORK).order())}장)")
    shutil.rmtree(WORK, ignore_errors=True)
    return spans


if __name__ == "__main__":
    main()
