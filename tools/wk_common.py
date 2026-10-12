# -*- coding: utf-8 -*-
"""주차별 빌드 공용 도구 — 기존 슬라이드 손보기(retitle 등)와 자주 쓰는 레이아웃."""
import os, re
from deckgen import *


class Ctx:
    """한 주차를 만드는 동안의 상태: 덱, 작업 폴더, 원본 순서, 만들어진 슬라이드 목록."""

    def __init__(self, deck, work, old):
        self.d, self.work, self.old = deck, work, old
        self.W = []

    # ---- 원본 슬라이드 참조/편집
    def O(self, n):
        return self.old[n - 1]

    def read(self, t):
        return open(os.path.join(self.work, "ppt", t), encoding="utf-8").read()

    def write(self, t, x):
        open(os.path.join(self.work, "ppt", t), "w", encoding="utf-8").write(x)

    def retitle(self, n, title=None, subtitle_contains=None, new_subtitle=None, replacements=(), title_ext=None):
        t = self.O(n)
        x = self.read(t)
        if title_ext:                       # 제목 상자가 좁아 글자가 접힐 때 넓혀 줍니다
            def widen(m):
                sp = m.group(0)
                if 'type="title"' not in sp:
                    return sp
                return re.sub(r'<a:ext cx="\d+" cy="\d+"/>',
                              f'<a:ext cx="{int(title_ext[0])}" cy="{int(title_ext[1])}"/>', sp, count=1)
            x = re.sub(r"<p:sp>.*?</p:sp>", widen, x, flags=re.S)
        for m in reversed(list(re.finditer(r"<p:sp>.*?</p:sp>", x, re.S))):
            sp = m.group(0)
            texts = "".join(re.findall(r"<a:t>([^<]*)</a:t>", sp))
            if title and 'type="title"' in sp:
                x = x[:m.start()] + _replace_paras(sp, title) + x[m.end():]
            elif subtitle_contains and new_subtitle and subtitle_contains in texts:
                x = x[:m.start()] + _replace_paras(sp, new_subtitle) + x[m.end():]
        for a, b in replacements:
            x = x.replace(a, b)
        self.write(t, x)

    def append_shapes(self, n, builder):
        t = self.O(n)
        x = self.read(t)
        ids = Ids(); ids.n = max(int(v) for v in re.findall(r'<p:cNvPr id="(\d+)"', x)) + 1
        self.write(t, x.replace("</p:spTree>", builder(ids) + "</p:spTree>", 1))

    def remove_offslide(self, n):
        t = self.O(n)
        x = self.read(t); cnt = [0]
        def drop(m):
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/><a:ext cx="(\d+)" cy="(\d+)"', m.group(0))
            if off:
                X, Y, Wd, H = map(int, off.groups())
                if X < 0 or X + Wd > SLIDE_W + 20000:
                    cnt[0] += 1; return ""
            return m.group(0)
        self.write(t, re.sub(r"<p:(sp|pic|graphicFrame)>.*?</p:\1>", drop, x, flags=re.S))
        return cnt[0]

    def edit_shape_at(self, n, x0, y0, text=None, ext=None, off=None, subtitle=None):
        """좌표로 도형을 찾아 글자와 크기를 바꿉니다 (제목 자리표시자가 아닌 옛 제목 상자용)."""
        t = self.O(n)
        x = self.read(t)
        pat = f'<a:off x="{x0}" y="{y0}"/>'
        m = None
        for mm in re.finditer(r"<p:sp>.*?</p:sp>", x, re.S):
            if pat in mm.group(0):
                m = mm
                break
        if m is None:
            raise ValueError(f"슬라이드 {n} 에서 ({x0}, {y0}) 위치의 도형을 찾지 못했습니다.")
        sp = m.group(0)
        if off:
            sp = sp.replace(pat, f'<a:off x="{int(off[0])}" y="{int(off[1])}"/>', 1)
        if ext:
            sp = re.sub(r'<a:ext cx="\d+" cy="\d+"/>', f'<a:ext cx="{int(ext[0])}" cy="{int(ext[1])}"/>', sp, count=1)
        if text is not None:
            sp = _replace_paras(sp, text)
        x = x[:m.start()] + sp + x[m.end():]
        self.write(t, x)
        if subtitle:
            self.append_shapes(n, lambda ids: deco(ids) + textbox(ids, 948807, Y_SUB, 12000000, 354344,
                para(subtitle, sz=2200, b=True, color=GREEN, lnSpc=100), autofit=False))

    def add_title(self, n, text, subtitle=None):
        """제목 자리표시자가 없는 옛 슬라이드에 제목(+부제)을 덧붙입니다."""
        def builder(ids):
            x = textbox(ids, X0, 314526, 11955336, 541687,
                        para(text, sz=3520, b=True, lnSpc=100), autofit=False)
            if subtitle:
                x += textbox(ids, 948807, Y_SUB, 12000000, 354344,
                             para(subtitle, sz=2200, b=True, color=GREEN, lnSpc=100), autofit=False)
            return x
        self.append_shapes(n, builder)

    def add_subtitle(self, n, text, w=12000000):
        """부제가 없는 슬라이드에 표준 위치 · 표준 서식의 초록 부제를 붙입니다."""
        self.append_shapes(n, lambda ids: textbox(ids, 948807, Y_SUB, w, 354344,
            para(text, sz=2200, b=True, color=GREEN, lnSpc=100), autofit=False))

    def remove_tiny_pics(self, n, max_cx=400000):
        """낱글자 대신 넣어 둔 아주 작은 그림을 지웁니다 (글자로 바꿔 적은 뒤)."""
        t = self.O(n)
        x = self.read(t); cnt = [0]
        def drop(m):
            e = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', m.group(0))
            if e and int(e.group(1)) <= max_cx and int(e.group(2)) <= max_cx:
                cnt[0] += 1; return ""
            return m.group(0)
        self.write(t, re.sub(r"<p:pic>.*?</p:pic>", drop, x, flags=re.S))
        return cnt[0]

    def replace_in_shape(self, n, contains, pairs):
        """특정 글자가 들어 있는 도형 안에서만 치환합니다 (같은 낱말이 여러 곳에 있을 때)."""
        t = self.O(n)
        x = self.read(t); done = [False]
        def fix(m):
            sp = m.group(0)
            if done[0] or contains not in "".join(re.findall(r"<a:t>([^<]*)</a:t>", sp)):
                return sp
            for a, b in pairs:
                sp = sp.replace(a, b)
            done[0] = True
            return sp
        self.write(t, re.sub(r"<p:sp>.*?</p:sp>", fix, x, flags=re.S))
        if not done[0]:
            raise ValueError("슬라이드 %d 에서 '%s' 도형을 찾지 못했습니다." % (n, contains))

    def set_layout(self, n, k):
        """슬라이드가 쓰는 레이아웃을 slideLayout{k} 로 바꿉니다 (레이아웃 장식 중복 제거용)."""
        t = self.O(n)                      # 예: "slides/slide100.xml"
        rp = os.path.join(self.work, "ppt", os.path.dirname(t), "_rels",
                          os.path.basename(t) + ".rels")
        r = open(rp, encoding="utf-8").read()
        r = re.sub(r'(Target="\.\./slideLayouts/slideLayout)\d+(\.xml")', r"\g<1>%d\g<2>" % k, r)
        open(rp, "w", encoding="utf-8").write(r)

    def remove_shapes_below(self, n, y_min):
        """세로 위치가 y_min 이상인 도형을 제거합니다."""
        t = self.O(n)
        x = self.read(t); cnt = [0]
        def drop(m):
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', m.group(0))
            if off and int(off.group(2)) >= y_min:
                cnt[0] += 1; return ""
            return m.group(0)
        self.write(t, re.sub(r"<p:(sp|pic|graphicFrame)>.*?</p:\1>", drop, x, flags=re.S))
        return cnt[0]

    def remove_shapes_right_of(self, n, x_min):
        """가로 위치가 x_min 이상인 도형을 제거합니다 (복사 후 남은 잔여 요소 정리용)."""
        t = self.O(n)
        x = self.read(t); cnt = [0]
        def drop(m):
            off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', m.group(0))
            if off and int(off.group(1)) >= x_min:
                cnt[0] += 1; return ""
            return m.group(0)
        self.write(t, re.sub(r"<p:(sp|pic|graphicFrame)>.*?</p:\1>", drop, x, flags=re.S))
        return cnt[0]

    # ---- 슬라이드 추가
    def add(self, xml):
        self.W.append(self.d.add_slide(xml))
        return self.W[-1]

    def keep(self, n):
        self.W.append(self.O(n))
        return self.W[-1]


def _replace_paras(sp_xml, new_text):
    rpr = re.search(r"<a:rPr\b[^>]*/>|<a:rPr\b[^>]*>.*?</a:rPr>", sp_xml, re.S)
    rpr = re.sub(r'\s(err|dirty)="[^"]*"', "", rpr.group(0)) if rpr else '<a:rPr lang="ko-KR" altLang="en-US"/>'
    ppr = re.search(r"<a:pPr\b[^>]*/>|<a:pPr\b[^>]*>.*?</a:pPr>", sp_xml, re.S)
    ppr = ppr.group(0) if ppr else ""
    new_p = f"<a:p>{ppr}<a:r>{rpr}<a:t>{esc(new_text)}</a:t></a:r></a:p>"
    return re.sub(r"(<a:lstStyle/>|</a:lstStyle>)(.*?)(</p:txBody>)",
                  lambda m: m.group(1) + new_p + m.group(3), sp_xml, count=1, flags=re.S)


# ---------------------------------------------------------------- 자주 쓰는 레이아웃
def table_slide(title, subtitle, cols, rows, widths, note=None, sz=2000, row_h=560000, y=1750000,
                col_algn=None, bold_first_col=True, col_font=None, header_h=None,
                note_style="takeaway", extra=None):
    """가운데 정렬 표 + (선택) 아래 도식 + 한 줄 요약."""
    def b(ids):
        x = (SLIDE_W - sum(widths)) // 2
        s, h = table(ids, x, y, widths, [cols] + rows, sz=sz, row_h=row_h, col_algn=col_algn,
                     bold_first_col=bold_first_col, col_font=col_font,
                     header_h=header_h or min(520000, row_h if isinstance(row_h, int) else 520000))
        y_end = y + h
        if extra:
            s += extra(ids, y_end); y_end += 1400000
        if note:
            if note_style == "takeaway":
                s += textbox(ids, X0, min(y_end + 300000, 6620000), W0, 600000,
                             para(note, sz=2400, b=True, algn="ctr", lnSpc=120))
            else:
                s += textbox(ids, X0, min(y_end + 250000, 6700000), W0, 600000,
                             para(note, sz=2000, lnSpc=120, color="1F3763"))
        return s
    return free(title, b, subtitle=subtitle)


def objectives_slide(week, goals, agenda, subtitle, date_note=None):
    """N주차 학습 목표 + 오늘의 순서."""
    def b(ids):
        s = textbox(ids, X0, 1450000, 5900000, 400000,
                    para("**오늘 끝나면 할 수 있어야 하는 것**", sz=2400, color=BLUE, lnSpc=100), autofit=False)
        ps = "".join(para(f"{m} {g}", sz=2200, lnSpc=145, marL=520000, indent=-520000)
                     for m, g in zip(["①", "②", "③", "④", "⑤"], goals))
        s += textbox(ids, X0, 1950000, 5900000, 3600000, ps, autofit=False)
        xr = 7150000
        s += textbox(ids, xr, 1450000, 5600000, 400000,
                     para("**오늘의 순서**", sz=2400, color=BLUE, lnSpc=100), autofit=False)
        y, h, gap = 1950000, 560000, 120000
        for i, (name, sub) in enumerate(agenda, 1):
            s += shape(ids, "rect", xr, y, 620000, h, fill="1F497D", line="1F497D",
                       text_xml=para(f"**{i}**", sz=2000, algn="ctr", color="FFFFFF", lnSpc=100), name="Step No")
            s += shape(ids, "rect", xr + 620000, y, 4980000, h, fill="F2F2F2", line="BFBFBF",
                       text_xml=para(f"**{name}**  {sub}", sz=1800, lnSpc=100, marL=180000), name="Step")
            y += h + gap
        if date_note:
            s += textbox(ids, X0, 6350000, W0, 500000,
                         para(date_note, sz=2200, b=True, algn="ctr", color="1F3763", lnSpc=110))
        return s
    return free(f"{week}주차 학습 목표", b, subtitle=subtitle)


def two_panel_slide(title, subtitle, lead, left, right, note=None, y=2350000, h=2600000):
    """상황 한 줄 + 좌우 비교 패널 + 마무리 문장. left/right = (제목, [줄들], 채움색, 선색)"""
    def b(ids):
        s = ""
        if lead:
            s += textbox(ids, X0, Y_BODY_SUB, W0, 700000, para(lead, sz=2600, b=True, lnSpc=120))
        hh = max(panel_height(6000000, left[1], h), panel_height(6000000, right[1], h))
        s += panel(ids, X0, y, 6000000, hh, left[0], left[1], fill=left[2], line=left[3])
        s += panel(ids, 7300000, y, 6000000, hh, right[0], right[1], fill=right[2], line=right[3])
        if note:
            ps = "".join(para(t, sz=2200, lnSpc=125, color=("1F3763" if i else None), b=bool(i))
                         for i, t in enumerate(note if isinstance(note, (list, tuple)) else [note]))
            s += textbox(ids, X0, min(y + hh + 300000, 6100000), W0, 1300000, ps)
        return s
    return free(title, b, subtitle=subtitle)


RED_PANEL = ("FBE5E5", "C00000")
GREEN_PANEL = ("E2EFDA", "2C5F2D")
BLUE_PANEL = ("DEEAF6", "1F497D")
YELLOW_PANEL = ("FFF2CC", "BF9000")

# ---------------------------------------------------------------- 항해 장치 (섹션 구분 · 중간 정리 · 용어표)
def section_slide(no, agenda, lead=None):
    """섹션 구분: 오늘의 순서를 다시 띄우고 지금 구간만 강조합니다. no는 1부터."""
    def b(ids):
        s = ""
        y, h, gap = 1900000, 620000, 150000
        for i, (name, sub) in enumerate(agenda, 1):
            on = (i == no)
            s += shape(ids, "rect", X0 + 900000, y, 720000, h,
                       fill=("1F497D" if on else "F2F2F2"), line=("1F497D" if on else "BFBFBF"),
                       text_xml=para(f"**{i}**", sz=2200, algn="ctr", color=("FFFFFF" if on else "7F7F7F"), lnSpc=100),
                       name="Sec No")
            s += shape(ids, "rect", X0 + 1620000, y, 9200000, h,
                       fill=("DEEAF6" if on else "FFFFFF"), line=("1F497D" if on else "BFBFBF"),
                       text_xml=para(f"**{name}**   {sub}", sz=(2200 if on else 1900), lnSpc=100,
                                     color=(None if on else "7F7F7F"), marL=220000),
                       name="Sec")
            y += h + gap
        if lead:
            s += textbox(ids, X0, y + 250000, W0, 600000, para(lead, sz=2400, b=True, algn="ctr", color="1F3763", lnSpc=115))
        return s
    name, sub = agenda[no - 1]
    return free(f"{no}. {name}", b, subtitle=sub)


def checkpoint_slide(points, question=None, answer=None, title="여기까지 정리"):
    """구간이 끝날 때 숨 고르는 슬라이드: 핵심 3가지 + 회상 질문 1개."""
    def b(ids):
        ps = "".join(para(f"{m} {t}", sz=2600, lnSpc=150, marL=560000, indent=-560000)
                     for m, t in zip(["①", "②", "③", "④"], points))
        s = textbox(ids, X0, 1600000, W0, 2800000, ps)
        if question:
            y = 1600000 + 700000 * len(points) + 400000
            # 글자 수에 맞춰 상자 높이를 잡습니다 (한 줄에 약 42자)
            lines = max(1, (len(question) + 12) // 42 + 1) + (max(1, (len(answer or "") + 8) // 46 + 1) if answer else 0)
            qh = 420000 + 380000 * lines
            s += shape(ids, "roundRect", X0, y, W0, qh, fill="FFF2CC", line="BF9000", lw=12700, name="Q")
            qs = para(f"**잠깐 생각해 봅시다**  {question}", sz=2400, lnSpc=120, marL=250000)
            if answer:
                qs += para(answer, sz=2100, lnSpc=120, color="1F3763", marL=250000)
            s += textbox(ids, X0 + 150000, y + 190000, W0 - 300000, qh - 250000, qs, autofit=False)
        return s
    return free(title, b, subtitle="다음으로 넘어가기 전에")


def terms_slide(week, rows, note=None):
    """이번 주에 나온 용어만 모은 표 (비전공자용)."""
    n = len(rows)
    return table_slide(f"{week}주차 용어 정리", "이번 시간에 새로 나온 말",
        ["용어", "영어", "뜻 (한 줄)"], rows, [2800000, 2900000, 6100000],
        sz=1900, row_h=max(430000, min(620000, 3900000 // max(n, 1))), y=1600000,
        col_algn=["ctr", "ctr", "l"], note=note, note_style="footnote")
