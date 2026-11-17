# -*- coding: utf-8 -*-
"""12강 「원무 업무마다 남는 기록」 → 「업무는 HIS에서, 통계는 CDW에서」 (2026-11-17).

업무 → 표 · 열 표를 HIS · CDW 비교 표(4줄)로 바꾸고 아래에 회색 두 문장. 학습 목표 ① 도 맞춤.
옛 표의 업무 · 표 이름은 새 표 첫 줄에 남김. 지금 글이 다르면 멈춤.
사용: python3 tools/w12_his_cdw.py <덱.pptx> <결과.pptx>
"""
import sys
from slidekit import A, P, Deck, add_box, set_title, table_fill, texts

OLD_TITLE, NEW_TITLE = "원무 업무마다 남는 기록", "업무는 HIS에서, 통계는 CDW에서"
GOAL = ("12주차 학습 목표", "① 원무 업무마다 남는 기록을 말할 수 있다", "① CDW가 왜 필요한지 말할 수 있다")
HEADER = ["구분", "병원정보시스템 (HIS · EMR)", "CDW"]
ROWS = [["하는 일", "접수 · 입원 수속 · 퇴원 수납 · 보험 청구", "입원 · 병동일보 · 진료비 표로 통계"],
        ["기록", "실시간으로 먼저 남음", "하루 한 번 옮겨 온 사본 (11강 ETL)"],
        ["무거운 통계를 돌리면", "진료 중인 시스템이 느려짐", "진료에 영향 없음"],
        ["자료 구조", "업무를 하기 좋게 짜여 있음", "여러 자료를 모아 분석하기 좋게 정리"]]
NOTE = ["병동일보 같은 정해진 보고서는 HIS 메뉴로도 나옵니다.", "메뉴에 없는 질문은 CDW에서 SQL로 셉니다."]


def main(src, out):
    d = Deck(src)
    t = d.tree(d.find(OLD_TITLE))
    assert "남는 기록 (가상 병원 CDW)" in texts(t), "298번 표가 예상과 다름"
    set_title(t, NEW_TITLE)
    frame = t.find(f".//{P}graphicFrame")
    x, w = int(frame.find(f"{P}xfrm/{A}off").get("x")), int(frame.find(f"{P}xfrm/{A}ext").get("cx"))
    widths = [2500000, 4800000, 4500000]
    assert sum(widths) == w, (sum(widths), w)                # 표 너비는 그대로
    bottom = table_fill(t, HEADER, ROWS, widths=widths, row_h=560000, sz=1800)
    add_box(t, x, bottom + 250000, w, 700000, NOTE, fill=None, line=None, sz=1800, color="7F7F7F",
            geom="rect", align="l", anchor="t", inset=0, name="Note")

    g = d.tree(d.find(GOAL[0]))
    runs = [r for r in g.iter(A + "t") if r.text == GOAL[1]]
    assert len(runs) == 1, (GOAL[1], len(runs))
    runs[0].text = GOAL[2]
    d.save(out)
    print(f"12강 「{NEW_TITLE}」 + 목표 ① → {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
