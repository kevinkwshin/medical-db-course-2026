# -*- coding: utf-8 -*-
"""12강에 '수술시간' 예제 3장 추가 — 2026-11-16 강사 요청 ("어떤 의료진의 수술시간이 길더라" 같은 통계, 12주차만 고침).

가상 병원 CDW 의 수술 표 (tools/build_hospital_mini.py 가 2026-11-16 에 추가, 다른 9개 표는 그대로).
3절 '재원일수' 끝('평균 옆에 최댓값도 — 긴 재원 확인' 뒤)에 9강 '2단계 — 값 살펴보기' 모양으로 3장:
  ① 수술시간 — 종료시각 − 시작시각   DATEDIFF('minute', 시작시각, 종료시각) = 분
  ② 집도의별 평균 수술시간            전체로 보면 위 · 대장 절제술을 맡는 의사A · B 가 가장 김
  ③ 같은 수술끼리 비교               복강경 담낭절제술만 보면 의사C 가 20분 넘게 김
고치는 글 (한 줄씩): 학습 목표 부제 · ③ / 오늘의 순서 3번(학습 목표 + 구분 6장) / 3절 구분 제목 · 부제
                    / 3절 '여기까지 정리' ④ / 12주차 강의 정리 넷째 줄
강사가 손으로 고친 덱이라 슬라이드는 글로 찾고, 바꿀 글은 지금 글과 똑같은지 확인한 뒤 바꿈.
12주차 노트북(tools/build_nb_w12.py)이 여기 SQL 을 그대로 씀
사용: python3 tools/w12_surgery.py <덱.pptx> <결과.pptx>
"""
import os, sys, re, copy
import duckdb
import w10_slides
from w10_slides import build
from slidekit import A, P, Deck, texts, shape, set_para, set_title, KW_SQL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = duckdb.connect(os.path.join(ROOT, "data", "hospital_mini.duckdb"), read_only=True)
rows = lambda q: h.execute(q).fetchall()
M = "DATEDIFF('minute', 시작시각, 종료시각)"

# ---------------------------------------------------------------- 숫자 (가상 병원 CDW 수술 표)
N_OP = rows("SELECT COUNT(*) FROM 수술")[0][0]
Q_OP1 = ["SELECT 집도의, 시작시각, 종료시각,", "       DATEDIFF('minute', 시작시각, 종료시각)", "         AS 수술시간",
         "FROM 수술", "ORDER BY 수술ID", "LIMIT 3;"]
R_OP1 = rows(" ".join(Q_OP1))
Q_OP2 = ["SELECT 집도의, COUNT(*) AS 건수,", "       ROUND(AVG(DATEDIFF('minute',", "             시작시각, 종료시각)), 1) AS 평균",
         "FROM 수술", "GROUP BY 집도의", "ORDER BY 평균 DESC;"]
R_OP2 = rows(" ".join(Q_OP2))
LAP = "복강경 담낭절제술"
Q_OP3 = Q_OP2[:4] + [f"WHERE 수술명 = '{LAP}'"] + Q_OP2[4:]
R_OP3 = rows(" ".join(Q_OP3))
assert len({r[2] for r in R_OP2}) == len(R_OP2) and len({r[2] for r in R_OP3}) == len(R_OP3), "평균에 동점 — 순서가 하나로 정해지지 않음"
assert {r[0] for r in R_OP2[:2]} == {"의사A", "의사B"}, R_OP2          # 전체로는 위 · 대장 절제술을 맡는 A · B 가 가장 김
SLOW = R_OP3[0][0]
OTHERS = [r[2] for r in R_OP3[1:]]
assert SLOW == "의사C" and R_OP3[0][2] - max(OTHERS) >= 15, R_OP3      # 같은 수술에서는 C 가 가장 김
assert [r[0] for r in R_OP2].index(SLOW) >= 4, R_OP2                  # 전체로 보면 C 는 아래쪽
SLOW_MED = rows(f"SELECT MEDIAN({M}) FROM 수술 WHERE 수술명 = '{LAP}' AND 집도의 = '{SLOW}'")[0][0]
LONG_OPS = rows(f"SELECT 수술명, ROUND(AVG({M})) FROM 수술 WHERE 수술명 IN ('위절제술', '대장절제술') GROUP BY 1 ORDER BY 1")
assert all(m >= 180 for _, m in LONG_OPS), LONG_OPS
assert rows(f"SELECT COUNT(*) FROM 수술 WHERE {M} <= 0")[0][0] == 0           # 자정을 넘긴 수술 없음 (시각끼리 빼도 됨)
fmt = lambda v: f"{v:,}" if isinstance(v, int) else str(v)

SQL_SLIDES = {
    "op1": dict(title="수술시간 — 종료시각 − 시작시각", question="수술 표에서 수술마다 걸린 시간(분)은?",
                sql_lines=Q_OP1, hl_lines={1, 2}, label="결과", header=["집도의", "시작시각", "종료시각", "수술시간"],
                rows=[[a, str(b), str(c), fmt(dd)] for a, b, c, dd in R_OP1], hl_rows=set(),
                widths=[1050000, 1250000, 1250000, 1174400],
                notes=[("한 행 = 수술 1건", f"집도의 · 수술명 · 수술일 · 시작 · 종료 시각 (외과 · 정형외과 {N_OP:,}건)"),
                       ("시각 빼기", "DATEDIFF('minute', 시작, 종료) = 걸린 분. 재원일수(날짜 빼기)와 같은 생각")]),
    "op2": dict(title="집도의별 평균 수술시간", question="집도의별로 수술 1건에 평균 몇 분?",
                sql_lines=Q_OP2, hl_lines={1, 2}, label="결과 (분)", header=["집도의", "건수", "평균"],
                rows=[[a, fmt(b), str(c)] for a, b, c in R_OP2], hl_rows={0, 1}, widths=[1574800, 1574800, 1574800],
                notes=[("확인", f"{R_OP2[0][0]} · {R_OP2[1][0]} 가 가장 길게 나옴 ({R_OP2[1][2]:.0f}~{R_OP2[0][2]:.0f}분)"),
                       ("그런데", "의사A · B 는 위 · 대장 절제술(평균 3시간 넘음)을 주로 맡음. 수술 종류가 섞인 평균으로는 비교할 수 없음")]),
    "op3": dict(title="같은 수술끼리 비교 — 복강경 담낭절제술", question=f"{LAP}만 보면 집도의별 평균은?",
                sql_lines=Q_OP3, hl_lines={4}, label="결과 (분)", header=["집도의", "건수", "평균"],
                rows=[[a, fmt(b), str(c)] for a, b, c in R_OP3], hl_rows={0}, widths=[1574800, 1574800, 1574800],
                notes=[("확인", f"같은 수술에서는 {SLOW} 가 {R_OP3[0][2]:.0f}분 — 다른 집도의({min(OTHERS):.0f}~{max(OTHERS):.0f}분)보다 20분 넘게 김. 중앙값도 {SLOW_MED:.0f}분"),
                       ("해석", "길다고 곧 잘못은 아님 — 환자 상태 · 수련의 참여 같은 이유를 함께 확인")]),
}

# 바꿀 글 (지금 글 → 새 글). 지금 글이 다르면 멈춤 — 강사가 이미 고친 곳은 건드리지 않음
SEC3 = ("재원일수", "퇴원일 − 입원일", "재원일수와 수술시간", "날짜 · 시각 빼기")
GOAL3 = ("③ 재원일수 · 병상 가동률을 구한다", "③ 재원일수 · 수술시간 · 가동률을 구한다")          # 한 줄에 들어가게
GOAL_SUB = ("입원 · 퇴원 · 병상 · 진료비 숫자 만들기", "입원 · 퇴원 · 수술 · 병상 · 진료비 숫자 만들기")
SUM4 = ["④ ", "수술시간", " = 종료시각 − 시작시각 (분). 같은 수술끼리 비교한다"]
END4 = ["수술시간", "은 시각을 빼서 구하고, 같은 수술끼리 비교한다"]


def add_para(s, src_idx, runs):
    """도형 s 의 src_idx 번째 문단을 복제해 맨 뒤에 붙이고 런 글을 runs 로 (런 수가 같아야 함)"""
    ps = s.findall(f"{P}txBody/{A}p")
    p_ = copy.deepcopy(ps[src_idx])
    rs = p_.findall(A + "r")
    assert len(rs) == len(runs), ([r.findtext(A + "t") for r in rs], runs)
    for r, txt in zip(rs, runs):
        r.find(A + "t").text = txt
    ps[-1].addnext(p_)


def main(src, out):
    d = Deck(src)
    KW = re.compile(KW_SQL.pattern.replace(r"\b(", r"\b(DATEDIFF|", 1))
    w10_slides.KW = KW                                # SELECT · AVG · ROUND · DATEDIFF … 파란 글자
    s12 = d.find("12강. SQL로 병원 통계 분석")
    e12 = d.find("12주차 강의 정리")
    L = d.between(s12, e12)
    F = lambda line, also=None: d.find(line, also, within=L)
    assert not any("수술시간" in "".join(texts(d.tree(s))) for s in L), "12강에 이미 수술시간 슬라이드가 있음"
    tmpl = d.find("2단계 — 값 살펴보기")
    assert b"notesSlide" not in d.rels(tmpl)

    # ---- 3절 끝에 3장
    a = F("평균 옆에 최댓값도 — 긴 재원 확인")
    for key in ("op1", "op2", "op3"):
        a = d.insert_after(a, build(d.tree(tmpl), **SQL_SLIDES[key]), d.rels(tmpl))
    assert "여기까지 정리" in texts(d.tree(d.slides()[d.index(a) + 1])), "3장 뒤가 3절 '여기까지 정리' 가 아님"

    # ---- 오늘의 순서 3번 (학습 목표 1장 + 구분 6장): 런 2개 '재원일수' · '  퇴원일 − 입원일'
    done = 0
    for s in L:
        for sp in d.tree(s).iter(P + "sp"):
            tx = texts(sp)
            if len(tx) == 1 and re.fullmatch(rf"{SEC3[0]}\s+{SEC3[1]}", tx[0]):
                rs = sp.findall(f".//{A}r")
                assert len(rs) == 2 and rs[0].findtext(A + "t") == SEC3[0], [r.findtext(A + "t") for r in rs]
                gap = rs[1].findtext(A + "t")[: -len(SEC3[1])]
                rs[0].find(A + "t").text, rs[1].find(A + "t").text = SEC3[2], gap + SEC3[3]
                done += 1
    assert done == 7, f"오늘의 순서 3번이 {done}곳 (학습 목표 1 + 구분 6 이어야 함)"

    # ---- 3절 구분 제목 · 부제
    t = d.tree(F("3. 재원일수"))
    assert texts(shape(t, "TextBox 4")) == [SEC3[1]]
    set_title(t, f"3. {SEC3[2]}")
    set_para(shape(t, "TextBox 4"), SEC3[3])

    # ---- 학습 목표 부제 · ③
    t = d.tree(F("12주차 학습 목표"))
    assert texts(shape(t, "TextBox 4")) == [GOAL_SUB[0]]
    set_para(shape(t, "TextBox 4"), GOAL_SUB[1])
    goals = shape(t, "TextBox 6")
    i = texts(goals).index(GOAL3[0])
    set_para(goals, GOAL3[1], i)

    # ---- 3절 '여기까지 정리' 에 ④ · 강의 정리 넷째 줄
    t = d.tree(F("여기까지 정리", "③ 평균과 함께 중앙값 · 최댓값을 본다"))
    box = shape(t, "TextBox 5")
    assert len(texts(box)) == 3, texts(box)
    add_para(box, 2, SUM4)
    for nm in ("Q 6", "TextBox 7"):                    # 넷째 줄만큼 '잠깐 생각해 봅시다' 상자를 내림
        off = shape(t, nm).find(f".//{A}off")
        off.set("y", str(int(off.get("y")) + 300000))
    t = d.tree(e12)
    box = shape(t, "TextBox 4")
    assert len(texts(box)) == 3, texts(box)
    add_para(box, 1, END4)

    d.save(out)
    print(f"12강: 수술시간 3장 추가 · 글 {done + 5}곳 고침 → {out}")
    for k in SQL_SLIDES:
        print(f"  {SQL_SLIDES[k]['title']}: {[tuple(r) for r in SQL_SLIDES[k]['rows']]}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
