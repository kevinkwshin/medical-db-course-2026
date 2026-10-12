# -*- coding: utf-8 -*-
"""슬라이드 안의 SQL 문장을 실제 실습 DB에 EXPLAIN 으로 걸어 문법/컬럼 오류를 찾습니다."""
import re, zipfile, duckdb
import xml.etree.ElementTree as ET

DECK = "데이터베이스관리_수정본_개편_최종_v2.pptx"
NSP = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
NSR = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
z = zipfile.ZipFile(DECK)
_rm = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))}
order = [_rm[s.get(NSR + "id")].split("/")[-1]
         for s in ET.fromstring(z.read("ppt/presentation.xml")).find(NSP + "sldIdLst")]
def parts(n):
    return "ppt/slides/" + order[n - 1]

con = duckdb.connect("data/aact_mini.duckdb", read_only=True)
KW = ("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "WITH")
bad, checked = [], 0
for n in range(53, len(order) + 1):
    x = z.read(parts(n)).decode()
    for m in re.finditer(r'<p:sp>.*?</p:sp>', x, re.S):
        b = m.group(0)
        lines = []
        for p in re.findall(r'<a:p>.*?</a:p>', b, re.S):
            t = "".join(re.findall(r'<a:t>([^<]*)</a:t>', p))
            lines.append(t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&"))
        s = "\n".join(lines).strip()
        if not s.upper().startswith(KW) or ";" not in s:
            continue
        s = s.split(";")[0] + ";"
        if "…" in s or "..." in s or "⋯" in s or "?" in s or "___" in s:
            continue
        if s.upper().startswith(("CREATE", "INSERT", "UPDATE", "DELETE", "GRANT")):
            continue    # 읽기 전용 DB 에서는 실행할 수 없는 문장
        checked += 1
        try:
            con.execute("EXPLAIN " + s)
        except Exception as e:
            bad.append((n, s[:110].replace("\n", " ⏎ "), str(e).split("\n")[0][:110]))
print(f"검사한 SQL: {checked}개,  오류: {len(bad)}개")
for n, s, e in bad:
    print(f"\n슬라이드 {n}\n   {s}\n   → {e}")
