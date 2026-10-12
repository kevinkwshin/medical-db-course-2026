# -*- coding: utf-8 -*-
"""Slide generator that reproduces the visual conventions of weeks 1-3 of
데이터베이스관리_수정본_개편_최종.pptx and registers new slides into an unpacked package.

Conventions copied from the deck:
  - slide size 13433425 x 7556500 EMU (14.69in x 8.26in), layout "Title and Content" (slideLayout2)
  - small ACB8CA square top-left on content slides, title placeholder inherits layout (35.2pt bold Malgun Gothic)
  - body text 28pt Malgun Gothic, blue 0432FF for keywords / SQL keywords, red FF0000 for data types
  - ①②③ typed literally; sub-bullets "•" (Arial) with marL 457200 / indent -457200 (as on 정리 slides)
  - SQL example: request text (quoted) -> right arrow -> rounded box (bg1 lumMod 95%, black line) with SQL
  - tables use tableStyleId {5940675A-B579-460E-94D1-54222C63F5DA}
"""
import os, re, shutil, zipfile
from xml.sax.saxutils import escape

SLIDE_W, SLIDE_H = 13433425, 7556500
FONT = "Malgun Gothic"
BLUE, RED, BLACK, GRAY = "0432FF", "FF0000", "000000", "7F7F7F"
GOLD = "BF9000"
NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')

SQL_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "GROUP BY", "HAVING", "ORDER BY", "LIMIT", "DISTINCT",
    "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "JOIN", "ON", "AS", "AND", "OR", "NOT",
    "IN", "BETWEEN", "ILIKE", "LIKE", "IS NULL", "IS NOT NULL", "NULL", "UPPER", "LOWER", "ROUND", "MEDIAN", "COUNT", "SUM", "AVG", "MIN", "MAX",
    "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM", "CREATE TABLE", "ALTER TABLE", "DROP TABLE",
    "PRIMARY KEY", "FOREIGN KEY", "REFERENCES", "NOT NULL", "UNIQUE", "CHECK", "DEFAULT",
    "GRANT", "REVOKE", "TO", "BEGIN", "COMMIT", "ROLLBACK", "WITH", "CASE", "WHEN", "THEN", "ELSE", "END",
    "CAST", "DESC", "ASC", "EXISTS", "UNION", "ALL", "TRY_CAST", "COALESCE",
]
SQL_TYPES = ["INTEGER", "INT", "VARCHAR", "CHAR", "TEXT", "DATE", "TIMESTAMP", "BOOLEAN", "NUMERIC", "DECIMAL", "FLOAT", "BIGINT"]


def esc(t):
    return escape(t, {'"': "&quot;"})


# ---------------------------------------------------------------- runs / paragraphs
def rpr(sz=2800, b=False, color=None, font=FONT, i=False, u=False, lang="ko-KR"):
    attrs = f'lang="{lang}" altLang="en-US" sz="{sz}"'
    if b: attrs += ' b="1"'
    if i: attrs += ' i="1"'
    if u: attrs += ' u="sng"'
    attrs += ' dirty="0"'
    inner = ""
    if color:
        inner += f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
    if font:
        inner += f'<a:latin typeface="{font}"/><a:ea typeface="{font}"/><a:cs typeface="{font}"/>'
    return f"<a:rPr {attrs}>{inner}</a:rPr>" if inner else f"<a:rPr {attrs}/>"


_TOK = re.compile(r"(\*\*.+?\*\*|\{\{.+?\}\}|\[\[.+?\]\]|__.+?__)", re.S)


def runs(text, sz=2800, b=False, color=None, font=FONT, i=False):
    """Inline markup: **bold**, {{blue}}, [[red]], __underline__. Newlines inside text -> <a:br/>."""
    out = []
    for tok in _TOK.split(text):
        if not tok:
            continue
        tb, tc, tu = b, color, False
        if tok.startswith("**"):
            tok, tb = tok[2:-2], True
        elif tok.startswith("{{"):
            tok, tc = tok[2:-2], BLUE
        elif tok.startswith("[["):
            tok, tc = tok[2:-2], RED
        elif tok.startswith("__"):
            tok, tu = tok[2:-2], True
        parts = tok.split("\n")
        for k, part in enumerate(parts):
            if k > 0:
                out.append(f"<a:br>{rpr(sz, tb, tc, font, i, tu)}</a:br>")
            if part != "":
                out.append(f"<a:r>{rpr(sz, tb, tc, font, i, tu)}<a:t>{esc(part)}</a:t></a:r>")
    return "".join(out)


def para(text="", sz=2800, lvl=0, b=False, color=None, lnSpc=150, spcBef=None, algn=None,
         bullet=None, marL=None, indent=None, font=FONT, i=False, sql=False):
    """One paragraph. lvl 0: plain; lvl 1: '•' bullet; lvl 2: '-' bullet (deeper indent).
    bullet=False forces no bullet; bullet='①' etc. is typed literally by the caller instead."""
    if marL is None:
        marL = {0: 0, 1: 914400, 2: 1371600, 3: 1828800}[lvl]
    if indent is None:
        indent = {0: 0, 1: -457200, 2: -342900, 3: -342900}[lvl]
    ppr = f'<a:pPr marL="{marL}" indent="{indent}"'
    if algn:
        ppr += f' algn="{algn}"'
    ppr += ">"
    ppr += f'<a:lnSpc><a:spcPct val="{int(lnSpc * 1000)}"/></a:lnSpc>'
    if spcBef is not None:
        ppr += f'<a:spcBef><a:spcPts val="{int(spcBef * 100)}"/></a:spcBef>'
    if bullet is None:
        bullet = {0: False, 1: "•", 2: "-", 3: "·"}[lvl]
    if bullet:
        ppr += f'<a:buFont typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/><a:buChar char="{esc(bullet)}"/>'
    else:
        ppr += "<a:buNone/>"
    ppr += "</a:pPr>"
    body = sql_runs(text, sz) if sql else runs(text, sz, b, color, font, i)
    return f"<a:p>{ppr}{body}<a:endParaRPr lang=\"ko-KR\" altLang=\"en-US\" sz=\"{sz}\" dirty=\"0\"/></a:p>"


def sql_runs(line, sz=2400, font=FONT):
    """Highlight SQL keywords blue and data types red, like slides 41-49. Manual markup still honored."""
    if _TOK.search(line):
        return runs(line, sz, font=font)
    kw = sorted(SQL_KEYWORDS, key=len, reverse=True)
    ty = sorted(SQL_TYPES, key=len, reverse=True)
    pat = re.compile(r"(?<![A-Za-z_])(" + "|".join(re.escape(k) for k in kw) + r")(?![A-Za-z_])"
                     r"|(?<![A-Za-z_(])(" + "|".join(re.escape(t) for t in ty) + r")(?![A-Za-z_])")
    out, pos = [], 0
    # do not highlight inside quotes
    quoted = [(m.start(), m.end()) for m in re.finditer(r"'[^']*'", line)]
    def in_q(p):
        return any(a <= p < b for a, b in quoted)
    for m in pat.finditer(line):
        if in_q(m.start()):
            continue
        if m.start() > pos:
            out.append(f"<a:r>{rpr(sz, font=font, lang='en-US')}<a:t>{esc(line[pos:m.start()])}</a:t></a:r>")
        color = BLUE if m.group(1) else RED
        out.append(f"<a:r>{rpr(sz, color=color, font=font, lang='en-US')}<a:t>{esc(m.group(0))}</a:t></a:r>")
        pos = m.end()
    if pos < len(line):
        out.append(f"<a:r>{rpr(sz, font=font, lang='en-US')}<a:t>{esc(line[pos:])}</a:t></a:r>")
    if not out:
        out.append(f"<a:r>{rpr(sz, font=font, lang='en-US')}<a:t> </a:t></a:r>")
    return "".join(out)


# ---------------------------------------------------------------- shapes
class Ids:
    def __init__(self):
        self.n = 1
    def next(self):
        self.n += 1
        return self.n


def deco(ids):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids.next()}" name="object 3"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="277453" y="347141"/><a:ext cx="285579" cy="408427"/></a:xfrm>'
            '<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="l" t="t" r="r" b="b"/><a:pathLst><a:path w="227329" h="325119">'
            '<a:moveTo><a:pt x="227075" y="324611"/></a:moveTo><a:lnTo><a:pt x="227075" y="0"/></a:lnTo><a:lnTo><a:pt x="0" y="0"/></a:lnTo>'
            '<a:lnTo><a:pt x="0" y="324611"/></a:lnTo><a:lnTo><a:pt x="227075" y="324611"/></a:lnTo><a:close/></a:path></a:pathLst></a:custGeom>'
            '<a:solidFill><a:srgbClr val="ACB8CA"/></a:solidFill></p:spPr>'
            '<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0"/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>')


def title_ph(ids, text):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids.next()}" name="Title 16"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr/>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p>{runs(text, sz=3520, b=True)}<a:endParaRPr lang="ko-KR" dirty="0"/></a:p></p:txBody></p:sp>')


def textbox(ids, x, y, w, h, paras_xml, autofit=True, fill=None, line=None, anchor=None,
            insets=None, geom="rect", name="TextBox", shadow=False):
    body = '<a:bodyPr wrap="square"'
    if insets:
        body += f' lIns="{insets[0]}" tIns="{insets[1]}" rIns="{insets[2]}" bIns="{insets[3]}"'
    if anchor:
        body += f' anchor="{anchor}"'
    body += ">"
    if autofit:
        body += "<a:spAutoFit/>"
    body += "</a:bodyPr>"
    sppr = f'<a:xfrm><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm><a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>'
    if fill == "bg1_95":
        sppr += '<a:solidFill><a:schemeClr val="bg1"><a:lumMod val="95000"/></a:schemeClr></a:solidFill>'
    elif fill:
        sppr += f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    else:
        sppr += "<a:noFill/>"
    if line:
        sppr += f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
    else:
        sppr += "<a:ln><a:noFill/></a:ln>"
    if shadow:
        sppr += '<a:effectLst><a:outerShdw blurRad="50800" dist="38100" dir="2700000" algn="tl" rotWithShape="0"><a:prstClr val="black"><a:alpha val="40000"/></a:prstClr></a:outerShdw></a:effectLst>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids.next()}" name="{name} {ids.n}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f"<p:spPr>{sppr}</p:spPr><p:txBody>{body}<a:lstStyle/>{paras_xml}</p:txBody></p:sp>")


def shape(ids, geom, x, y, w, h, fill=None, line=BLACK, text_xml=None, lw=12700, name="Shape", dash=None):
    sppr = f'<a:xfrm><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm><a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>'
    if fill == "bg1_95":
        sppr += '<a:solidFill><a:schemeClr val="bg1"><a:lumMod val="95000"/></a:schemeClr></a:solidFill>'
    elif fill:
        sppr += f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    else:
        sppr += "<a:noFill/>"
    if line:
        sppr += f'<a:ln w="{lw}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>'
        if dash:
            sppr += f'<a:prstDash val="{dash}"/>'
        sppr += "</a:ln>"
    else:
        sppr += "<a:ln><a:noFill/></a:ln>"
    tx = text_xml or '<a:p><a:pPr algn="ctr"/><a:endParaRPr lang="ko-KR"/></a:p>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids.next()}" name="{name} {ids.n}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr>{sppr}</p:spPr><p:txBody><a:bodyPr rtlCol="0" anchor="ctr" lIns="45720" rIns="45720"/><a:lstStyle/>{tx}</p:txBody></p:sp>')


def arrow_right(ids, x, y, w=681644, h=867931):
    return shape(ids, "rightArrow", x, y, w, h, fill=None, line="1F497D", lw=19050, name="Right Arrow")


def arrow_down(ids, x, y, w=600000, h=520000):
    return shape(ids, "downArrow", x, y, w, h, fill=None, line="1F497D", lw=19050, name="Down Arrow")


def box(ids, x, y, w, h, lines, sz=2400, fill="bg1_95", line=BLACK, algn=None, anchor="ctr", b=False, color=None, geom="roundRect", lnSpc=120):
    """Rounded box with centered text lines (list of str)."""
    ps = "".join(para(l, sz=sz, algn=algn or "ctr", lnSpc=lnSpc, b=b, color=color) for l in lines)
    return shape(ids, geom, x, y, w, h, fill=fill, line=line, text_xml=ps, name="Rounded Rectangle")


def sql_box(ids, x, y, w, lines, sz=2400, h=None, pad=180000):
    """Rounded bg1_95 box + SQL text with keyword highlighting. Returns (xml, height)."""
    n = sum(_wrapped_lines(seg, sz, w - 2 * pad, mono=True)
            for l in lines for seg in str(l).split("\n"))
    line_h = (sz / 100) * 12700 * 1.25  # hundredths of pt -> EMU, with line factor
    if h is None:
        h = int(n * line_h + 2 * pad)
    ps = "".join(para(l, sz=sz, lnSpc=100, sql=True) for l in lines)
    xml = shape(ids, "roundRect", x, y, w, h, fill="bg1_95", line=BLACK, name="Rounded Rectangle")
    xml += textbox(ids, x + pad, y + pad // 2, w - 2 * pad, h - pad, ps, autofit=False, name="SQL")
    return xml, h


TABLE_HEADER_FILL = "0070C0"   # header row fill used on the deck's own tables (slide 8/12)
TABLE_BODY_COLOR = "1F3763"    # body text color used across weeks 1-3
TABLE_BORDER = "7F7F7F"


def table(ids, x, y, col_w, rows, sz=1800, row_h=370840, header=True, algn="l", bold_first_col=False, col_algn=None, col_font=None,
          header_fill=TABLE_HEADER_FILL, header_color="FFFFFF", body_color=TABLE_BODY_COLOR, border=TABLE_BORDER, band=None, header_h=None):
    """Table styled like the deck's own tables: blue header row with white bold text, thin gray borders,
    left-aligned body text (override per column with col_algn, e.g. ["ctr","l","l"]).
    rows: list of lists of str (first row = header when header=True). Markup allowed. col_font: {col_index: typeface}."""
    grid = "".join(f'<a:gridCol w="{int(w)}"/>' for w in col_w)
    trs = []
    line_h = (sz / 100) * 12700 * 1.2
    heights = []
    for ri, row in enumerate(rows):
        is_h = header and ri == 0
        base = (header_h if (is_h and header_h) else (row_h[ri] if isinstance(row_h, (list, tuple)) else row_h))
        n_lines = max(str(c).count("\n") + 1 for c in row) if row else 1
        rh = int(max(base, n_lines * line_h + 2 * 36000 + 60000))
        heights.append(rh)
        tcs = []
        for ci, cell in enumerate(row):
            a = "ctr" if is_h else (col_algn[ci] if col_algn else algn)
            b = is_h or (bold_first_col and ci == 0)
            f = FONT if is_h else (col_font or {}).get(ci, FONT)
            color = header_color if is_h else body_color
            ps = "".join(para(line, sz=sz, algn=a, lnSpc=100, b=b, font=f, color=color) for line in str(cell).split("\n")) or para("", sz=sz)
            tcpr = '<a:tcPr marL="91440" marR="91440" marT="36000" marB="36000" anchor="ctr">'
            for side in ("lnL", "lnR", "lnT", "lnB"):
                tcpr += f'<a:{side} w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill><a:prstDash val="solid"/></a:{side}>'
            fill = header_fill if is_h else (band if (band and ri % 2 == 0) else None)
            if fill:
                tcpr += f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
            tcpr += "</a:tcPr>"
            tcs.append(f"<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>{ps}</a:txBody>{tcpr}</a:tc>")
        trs.append(f'<a:tr h="{rh}">{"".join(tcs)}</a:tr>')
    h = sum(heights)
    return (f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{ids.next()}" name="Table {ids.n}"/><p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
            f'<p:xfrm><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(sum(col_w))}" cy="{h}"/></p:xfrm>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table"><a:tbl>'
            f'<a:tblPr firstRow="{1 if header else 0}" bandRow="1"><a:tableStyleId>{{5940675A-B579-460E-94D1-54222C63F5DA}}</a:tableStyleId></a:tblPr>'
            f"<a:tblGrid>{grid}</a:tblGrid>{''.join(trs)}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>"), h


def picture(ids, rid, x, y, w, h, name="Picture"):
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{ids.next()}" name="{name} {ids.n}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')


def connector(ids, x1, y1, x2, y2, color="1F497D", lw=19050, arrow=True, dash=None, geom="straightConnector1"):
    x, y = min(x1, x2), min(y1, y2)
    w, h = abs(x2 - x1), abs(y2 - y1)
    flipH = ' flipH="1"' if x2 < x1 else ""
    flipV = ' flipV="1"' if y2 < y1 else ""
    ln = f'<a:ln w="{lw}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
    if dash:
        ln += f'<a:prstDash val="{dash}"/>'
    if arrow:
        ln += '<a:tailEnd type="triangle"/>'
    ln += "</a:ln>"
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{ids.next()}" name="Connector {ids.n}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
            f'<p:spPr><a:xfrm{flipH}{flipV}><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(w)}" cy="{int(h)}"/></a:xfrm><a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>{ln}</p:spPr></p:cxnSp>')


# ---------------------------------------------------------------- slide wrappers
def slide_xml(shapes_xml):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:sld {NS} showMasterSp="0"><p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            f"{shapes_xml}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>")


X0 = 806418          # left content edge (matches title placeholder)
W0 = 12498102        # body text width used on slides 42-51
Y_BODY = 911719      # body top used on slides 42-51
Y_SUB = 940003       # subtitle top used on slides 37/39/57 (green 22pt bold)
GREEN = "375622"
Y_BODY_SUB = 1500000  # body top when a subtitle is present
Y_BODY_PLAIN = 1441440  # body top without subtitle (slide 51)


def subtitle_box(ids, text):
    """Green 22pt bold one-liner under the title, as on the instructor's slides 37/39/57."""
    return textbox(ids, 948807, Y_SUB, 12000000, 354344, para(text, sz=2200, b=True, color=GREEN, lnSpc=100), autofit=False)


def cover(week, title, topics, date, name="신기원"):
    """표지: mirrors slide 33. topics: 3 short lines."""
    ids = Ids()
    s = ""
    tp = "".join(
        f'<a:p><a:pPr marL="189052" indent="-173098"><a:lnSpc><a:spcPct val="150000"/></a:lnSpc><a:spcBef><a:spcPts val="126"/></a:spcBef>'
        f'<a:buFont typeface="Cambria Math"/><a:buChar char="∙"/><a:tabLst><a:tab pos="189052" algn="l"/></a:tabLst></a:pPr>{runs(t, 2800)}</a:p>'
        for t in topics)
    s += (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids.next()}" name="object 9"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
          '<p:spPr><a:xfrm><a:off x="4329685" y="2823012"/><a:ext cx="6753181" cy="1910475"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
          f'<p:txBody><a:bodyPr vert="horz" wrap="square" lIns="0" tIns="15954" rIns="0" bIns="0"><a:spAutoFit/></a:bodyPr><a:lstStyle/>{tp}</p:txBody></p:sp>')
    s += (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids.next()}" name="Title 6"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
          '<p:spPr><a:xfrm><a:off x="1007507" y="1546102"/><a:ext cx="11418411" cy="738664"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
          '<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0"><a:spAutoFit/></a:bodyPr>'
          f'<a:lstStyle><a:lvl1pPr><a:buNone/><a:defRPr sz="3078" b="0" i="0"><a:solidFill><a:srgbClr val="{GOLD}"/></a:solidFill><a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:defRPr></a:lvl1pPr></a:lstStyle>'
          f'<a:p><a:pPr algn="ctr"><a:buNone/></a:pPr>{runs(f"{week}강. {title}", 4800, b=True, color=BLACK)}</a:p></p:txBody></p:sp>')
    s += (f'<p:sp><p:nvSpPr><p:cNvPr id="{ids.next()}" name="object 9"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
          '<p:spPr><a:xfrm><a:off x="5149213" y="5922051"/><a:ext cx="3134998" cy="827999"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
          '<p:txBody><a:bodyPr vert="horz" wrap="square" lIns="0" tIns="15954" rIns="0" bIns="0"><a:spAutoFit/></a:bodyPr><a:lstStyle/>'
          f'<a:p><a:pPr marL="15954" algn="ctr"><a:spcBef><a:spcPts val="126"/></a:spcBef><a:buNone/></a:pPr>{runs(date, 2638, color=BLACK)}<a:br>{rpr(2638)}</a:br>{runs(name, 2638, color=BLACK)}</a:p></p:txBody></p:sp>')
    return slide_xml(s)


def content(title, paras, subtitle=None, y=None, w=W0, x=X0, extra="", lnSpc=150):
    """Title + body text. paras: list of (text, kwargs) or str. Sub-bullets via kwargs lvl=1/2."""
    ids = Ids()
    s = deco(ids) + title_ph(ids, title)
    yy = y if y is not None else Y_BODY_PLAIN
    ps = ""
    if subtitle:
        s += subtitle_box(ids, subtitle)
        yy = y if y is not None else Y_BODY_SUB
    for p in paras:
        if isinstance(p, str):
            ps += para(p, lnSpc=lnSpc)
        else:
            t, kw = p
            ps += para(t, **{**dict(lnSpc=lnSpc), **kw})
    s += textbox(ids, x, yy, w, 5000000, ps)
    s += extra(ids) if callable(extra) else extra
    return slide_xml(s)


def summary(week, bullets, title=None, sz=2800, lnSpc=150, next_week=None):
    """N주차 강의 정리 (mirrors slide 51)."""
    ids = Ids()
    s = deco(ids) + title_ph(ids, title or f"{week}주차 강의 정리")
    ps = ""
    for b in bullets:
        if isinstance(b, str):
            ps += para(b, sz=sz, lvl=1, lnSpc=lnSpc, marL=457200, indent=-457200)
        else:
            t, kw = b
            ps += para(t, **{**dict(sz=sz, lvl=1, lnSpc=lnSpc, marL=457200, indent=-457200), **kw})
    s += textbox(ids, X0, 1441440, 11812947, 4300000 if next_week else 4546373, ps)
    if next_week:
        s += shape(ids, "roundRect", X0, 5850000, W0, 900000, fill="F2F2F2", line="1F497D", lw=12700,
                   text_xml=para(f"**다음 시간**  {next_week}", sz=2200, algn="ctr", lnSpc=110), name="Next")
    return slide_xml(s)


def quiz(title, question, options, answer=None, note=None):
    """확인 문제 (mirrors slide 31): options as separate lines, correct one outlined in blue."""
    ids = Ids()
    s = deco(ids) + title_ph(ids, title)
    s += textbox(ids, 954125, 1391488, 11000000, 500000, para(question, sz=2400, lnSpc=120))
    marks = ["①", "②", "③", "④", "⑤"]
    x, top, pitch, hh = 1382712, 2280000, 720000, 620000
    for i, o in enumerate(options):
        s += textbox(ids, x, top + i * pitch, 11000000, hh, para(f"{marks[i]} {o}", sz=2600, lnSpc=100), autofit=False, anchor="ctr")
    if answer is not None:
        txt = f"{marks[answer]} {options[answer]}"
        width = sum(330000 if ord(ch) > 0x2E80 else 180000 for ch in txt) + 320000
        s += shape(ids, "rect", x, top + answer * pitch, min(width, 11000000), hh, fill=None, line=BLUE, lw=19050, name="Answer Box")
        if note:
            nrow = _wrapped_lines(f"왜 그럴까요  {note}", 2200, 10500000)
            nh = max(900000, int(nrow * 2200 / 100 * 12700 * 1.18 + 340000))
            s += shape(ids, "roundRect", x, top + len(options) * pitch + 260000, 11000000, nh,
                       fill="F6F8FA", line="BFBFBF", lw=9525, name="Note")
            s += textbox(ids, x + 250000, top + len(options) * pitch + 420000, 10500000, nh - 280000,
                         para(f"**왜 그럴까요**  {note}", sz=2200, lnSpc=118, color="1F3763"), autofit=False)
    return slide_xml(s)


def sql_example(title, subtitle, request, sql_lines, note=None, result=None, result_w=None, sz=2400, request_label=None):
    """Mirrors slide 41: quoted request -> arrow -> SQL box; optional result table underneath."""
    ids = Ids()
    s = deco(ids) + title_ph(ids, title)
    if subtitle:
        s += subtitle_box(ids, subtitle)
    top = 2150000
    box_x, box_w = 6650000, 6000000
    # request (left): bold label above, regular quoted request (mirrors slide 41)
    req_ps = ""
    if request_label:
        req_ps += para(request_label, sz=2800, b=True, lnSpc=120)
    req_ps += para(f"“{request}”", sz=2400, lnSpc=130)
    s += textbox(ids, X0, top - 450000, 4800000, 1200000, req_ps)
    s += textbox(ids, box_x, top - 450000, 2000000, 400000, para("SQL", sz=2800, b=True, lnSpc=100), autofit=False)
    # arrow
    s += arrow_right(ids, 5750000, top + 150000)
    # sql box (right)
    xml, h = sql_box(ids, box_x, top, box_w, sql_lines, sz=sz)
    s += xml
    y_next = top + h + 250000
    if result:
        cols = result[0]
        if result_w:
            k = box_w / sum(result_w)
            widths = [int(w * k) for w in result_w]
        else:
            widths = [box_w // len(cols)] * len(cols)
        need = 360000 * len(result) + 200000
        if y_next + need > 6100000:          # SQL 상자가 길면 결과표를 왼쪽 빈 자리에 둡니다
            lw = [int(w * 5400000 / sum(widths)) for w in widths]
            txml, th = table(ids, X0, top + 1100000, lw, result, sz=1800, row_h=360000, algn="ctr")
            s += txml
            y_next = max(y_next, top + 1100000 + th + 200000)
        else:
            txml, th = table(ids, box_x, y_next, widths, result, sz=1800, row_h=360000, algn="ctr")
            s += txml
            y_next += th + 200000
    if note:
        ny = min(max(y_next, 6200000), SLIDE_H - 780000)   # 슬라이드 아래로 넘치지 않게
        s += textbox(ids, X0, ny, W0, 600000, para(note, sz=2200, lnSpc=120, color="1F3763"))
    return slide_xml(s)


def free(title, builder, subtitle=None):
    """Arbitrary layout: builder(ids) -> shapes xml string."""
    ids = Ids()
    s = deco(ids) + title_ph(ids, title)
    if subtitle:
        s += subtitle_box(ids, subtitle)
    s += builder(ids)
    return slide_xml(s)


# ---------------------------------------------------------------- package
class Deck:
    """Operates on an unpacked pptx directory."""

    def __init__(self, root):
        self.root = root
        self.pres_path = os.path.join(root, "ppt", "presentation.xml")
        self.rels_path = os.path.join(root, "ppt", "_rels", "presentation.xml.rels")
        self.ct_path = os.path.join(root, "[Content_Types].xml")
        self.pres = open(self.pres_path, encoding="utf-8").read()
        self.rels = open(self.rels_path, encoding="utf-8").read()
        self.ct = open(self.ct_path, encoding="utf-8").read()
        self.new_files = []

    # ---- introspection
    def rel_map(self):
        return {m.group(1): m.group(2) for m in re.finditer(r'<Relationship Id="([^"]+)"[^>]*Target="([^"]+)"', self.rels)}

    def order(self):
        """Current slide order as list of 'slides/slideN.xml' targets."""
        rm = self.rel_map()
        return [rm[m.group(1)] for m in re.finditer(r'<p:sldId [^>]*r:id="([^"]+)"', self.pres)]

    def max_slide_num(self):
        nums = [int(m.group(1)) for m in re.finditer(r"slide(\d+)\.xml", " ".join(os.listdir(os.path.join(self.root, "ppt", "slides"))))]
        return max(nums)

    def _next_rid(self):
        ids = [int(m.group(1)) for m in re.finditer(r'Id="rId(\d+)"', self.rels)]
        return f"rId{max(ids) + 1}"

    def _next_sld_id(self):
        ids = [int(m.group(1)) for m in re.finditer(r'<p:sldId id="(\d+)"', self.pres)]
        return max(ids + [255]) + 1

    # ---- creation
    def add_slide(self, xml, layout="slideLayout2.xml", media=None):
        """Write a new slide part; returns target 'slides/slideN.xml'. media: list of (rid, relpath-to-media) already copied."""
        n = self.max_slide_num() + 1
        target = f"slides/slide{n}.xml"
        with open(os.path.join(self.root, "ppt", target), "w", encoding="utf-8") as f:
            f.write(xml)
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/{layout}"/>')
        for rid, mpath in (media or []):
            rels += f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{mpath}"/>'
        rels += "</Relationships>"
        with open(os.path.join(self.root, "ppt", "slides", "_rels", f"slide{n}.xml.rels"), "w", encoding="utf-8") as f:
            f.write(rels)
        if f'PartName="/ppt/{target}"' not in self.ct:
            self.ct = self.ct.replace("</Types>", f'<Override PartName="/ppt/{target}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>')
        self.new_files.append(target)
        return target

    def add_media(self, src_path):
        """Copy an image into ppt/media, return relative target for slide rels ('../media/imageN.ext')."""
        mdir = os.path.join(self.root, "ppt", "media")
        ext = os.path.splitext(src_path)[1].lower()
        nums = [int(m.group(1)) for m in re.finditer(r"image(\d+)\.", " ".join(os.listdir(mdir)))]
        name = f"image{max(nums + [0]) + 1}{ext}"
        shutil.copy(src_path, os.path.join(mdir, name))
        default = {".png": "png", ".jpeg": "jpeg", ".jpg": "jpeg", ".svg": "svg", ".gif": "gif"}[ext]
        if f'Extension="{ext[1:]}"' not in self.ct:
            mime = {"png": "image/png", "jpeg": "image/jpeg", "svg": "image/svg+xml", "gif": "image/gif"}[default]
            self.ct = self.ct.replace("<Override", f'<Default Extension="{ext[1:]}" ContentType="{mime}"/><Override', 1)
        return f"../media/{name}"

    # ---- ordering
    def set_order(self, targets):
        """Rewrite sldIdLst to exactly this list of 'slides/slideN.xml' targets (existing or new)."""
        rm = self.rel_map()
        inv = {v: k for k, v in rm.items()}
        sld_ids = {rm[m.group(2)]: m.group(1) for m in re.finditer(r'<p:sldId id="(\d+)" r:id="([^"]+)"', self.pres)}
        entries = []
        next_id = self._next_sld_id()
        for t in targets:
            if t not in inv:
                rid = self._next_rid()
                self.rels = self.rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="{t}"/></Relationships>')
                inv[t] = rid
            sid = sld_ids.get(t)
            if sid is None:
                sid = str(next_id); next_id += 1
            entries.append(f'<p:sldId id="{sid}" r:id="{inv[t]}"/>')
        self.pres = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", "<p:sldIdLst>" + "".join(entries) + "</p:sldIdLst>", self.pres, flags=re.S)
        # drop relationships of slides no longer listed
        keep = set(targets)
        def drop(m):
            return "" if (m.group(2).startswith("slides/") and m.group(2) not in keep) else m.group(0)
        self.rels = re.sub(r'<Relationship Id="([^"]+)" Type="[^"]*/slide" Target="([^"]+)"/>', drop, self.rels)

    def edit_slide(self, target, replacements):
        """Plain string replacements inside an existing slide XML (for small text fixes)."""
        p = os.path.join(self.root, "ppt", target)
        x = open(p, encoding="utf-8").read()
        for old, new in replacements:
            if old not in x:
                raise ValueError(f"'{old}' not found in {target}")
            x = x.replace(old, new)
        open(p, "w", encoding="utf-8").write(x)

    def save_meta(self):
        open(self.pres_path, "w", encoding="utf-8").write(self.pres)
        open(self.rels_path, "w", encoding="utf-8").write(self.rels)
        open(self.ct_path, "w", encoding="utf-8").write(self.ct)

    def zip(self, out_pptx):
        self.save_meta()
        if os.path.exists(out_pptx):
            os.remove(out_pptx)
        with zipfile.ZipFile(out_pptx, "w", zipfile.ZIP_DEFLATED) as z:
            # [Content_Types].xml first
            z.write(self.ct_path, "[Content_Types].xml")
            for dp, dn, fn in os.walk(self.root):
                for f in fn:
                    full = os.path.join(dp, f)
                    arc = os.path.relpath(full, self.root)
                    if arc == "[Content_Types].xml" or f == ".DS_Store":
                        continue
                    z.write(full, arc)
        return out_pptx

# ---------------------------------------------------------------- figure parts
def entity_box(ids, x, y, w, name, attrs, key_idx=(0,), fill="DEEAF6", line="1F497D", sz=1500, head_h=380000, row_h=300000):
    """테이블(개체) 상자: 파란 머리행 + 속성 목록. 반환: (xml, height)"""
    s = shape(ids, "rect", x, y, w, head_h, fill=fill, line=line, lw=12700,
              text_xml=para(f"**{name}**", sz=sz + 200, algn="ctr", lnSpc=100), name="Entity Head")
    h = head_h + row_h * len(attrs)
    s += shape(ids, "rect", x, y + head_h, w, row_h * len(attrs), fill="FFFFFF", line=line, lw=12700, name="Entity Body")
    ps = ""
    for i, a in enumerate(attrs):
        ps += para(("__" + a + "__") if i in key_idx else a, sz=sz, lnSpc=100, marL=140000)
    s += textbox(ids, x, y + head_h + 40000, w, row_h * len(attrs), ps, autofit=False)
    return s, h


def label_line(ids, x1, y1, x2, y2, label=None, sz=1400, color="1F497D", lw=15875, dash=None):
    """두 상자를 잇는 선 + 가운데 라벨 (예: 1 : N)"""
    s = connector(ids, x1, y1, x2, y2, color=color, lw=lw, arrow=False, dash=dash)
    if label:
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        s += textbox(ids, mx - 380000, my - 330000, 760000, 320000,
                     para(label, sz=sz, b=True, algn="ctr", color=color, lnSpc=100), autofit=False)
    return s


def _wrapped_lines(text, sz, width, mono=False):
    """글자 폭을 어림해 몇 줄로 접히는지 셉니다 (한글 1글자 = 글꼴 크기, 영문·숫자 = 그 절반)."""
    unit = (sz / 100) * 12700
    used, rows = 0.0, 1
    for ch in text.replace("**", ""):
        cw = unit if ord(ch) > 0x2E80 else unit * (0.62 if mono else 0.55)
        if used + cw > width:
            rows += 1; used = 0.0
        used += cw
    return rows


def panel_height(w, lines, h=0, sz=1900):
    """패널이 글을 다 담으려면 얼마나 높아야 하는지 (panel 과 같은 계산)."""
    line_h = (sz / 100) * 12700 * 1.25
    n_rows = sum(_wrapped_lines(ln[2:] if ln.startswith("- ") else ln, sz,
                                w - 300000 - (300000 if ln.startswith("- ") else 120000)) for ln in lines)
    return max(h, int(480000 + 200000 + n_rows * line_h + 260000))


def panel(ids, x, y, w, h, title, lines, fill="F2F2F2", line="7F7F7F", title_fill=None, sz=1900, title_sz=2000):
    """제목 띠 + 본문 줄이 있는 비교 패널. 글이 많으면 상자를 자동으로 늘립니다."""
    th = 480000
    h = panel_height(w, lines, h, sz)
    s = shape(ids, "roundRect", x, y, w, h, fill=fill, line=line, lw=12700, name="Panel")
    s += shape(ids, "rect", x + 90000, y + 90000, w - 180000, th, fill=title_fill or line, line=None,
               text_xml=para(f"**{title}**", sz=title_sz, algn="ctr", color="FFFFFF", lnSpc=100), name="Panel Head")
    ps = "".join(para(t, sz=sz, lnSpc=125, lvl=(0 if not t.startswith("- ") else 1),
                      bullet=("•" if t.startswith("- ") else False),
                      marL=(300000 if t.startswith("- ") else 120000), indent=(-250000 if t.startswith("- ") else 0))
                 for t in [ln[2:] if ln.startswith("- ") else ln for ln in lines])
    s += textbox(ids, x + 150000, y + th + 200000, w - 300000, h - th - 300000, ps, autofit=False)
    return s


def step_row(ids, x, y, w, h, items, fill="DEEAF6", line="1F497D", sz=1800, gap=None, arrow=True):
    """가로로 늘어놓은 단계 상자 + 화살표. items: [(굵은글씨, 설명)] 또는 [문자열]"""
    n = len(items)
    gap = gap if gap is not None else 400000
    bw = (w - gap * (n - 1)) // n
    s = ""
    for i, it in enumerate(items):
        bx = x + i * (bw + gap)
        lines = [f"**{it[0]}**", it[1]] if isinstance(it, (tuple, list)) else [f"**{it}**"]
        s += box(ids, bx, y, bw, h, lines, sz=sz, fill=fill, line=line, geom="rect", lnSpc=110)
        if arrow and i < n - 1:
            s += arrow_right(ids, bx + bw + gap // 2 - 170000, y + h // 2 - 170000, 340000, 340000)
    return s
