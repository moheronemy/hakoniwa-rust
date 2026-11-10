#!/usr/bin/env python3
"""phase2-sea: doEachHex の海上都市・船舶の突き合わせ用データ。

船 (値 0〜19 のすべて) と海上都市を、海・移動できない地形 (荒地・山・ハリボテ)・
島の端の近くに置く。rand 0 では船はすべて老朽化で沈み (沈んだ海が移動する)、
rand 0.5 では沈まずに収入・漁獲を得て (x, y+1) の方へ動く。
島は 3, 1, 2 の順に処理されるので、島 3 の船が付けた移動済みの印 (@funeMove) で
島 1・島 2 の同じ位置の船が動かなくなる。

    python3 -I tools/fixtures/phase2_sea.py
    tools/perl-harness/run-harness.sh phase2-sea estimate,eachhex,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

LEGEND = {
    ".": ("Sea", 0),
    "T": ("Town", 150),
    "N": ("Mountain", 10),
    "W": ("Waste", 0),
    "H": ("Haribote", 0),
    "p": ("Frocity", 50),
    "q": ("Frocity", 99),
    "r": ("Frocity", 150),
    "s": ("Frocity", 5),
    "u": ("Frocity", 1),
    "w": ("Frocity", 25),
    "x": ("Frocity", 60),
}
# 船: "0"〜"9" が値 0〜9、"a"〜"j" が値 10〜19
for v in range(20):
    LEGEND["0123456789abcdefghij"[v]] = ("Fune", v)

f = Fixture("phase2-sea")
# 島 1: すべての船、海上都市 (成長・移動・移動できない)、島の端
f.grid(1, [
    "............",
    "0123456789ab",
    "............",
    "...........W",
    ".cdefghij.1.",
    "..........N.",
    "............",
    "..p..q..r...",
    "...........H",
    "...........x",
    "..........H.",
    "........TT..",
], LEGEND)
f.main(1, money=500000, food=30000)

# 島 2: 食料不足で海上都市が縮む・平地になる。人口 0 の豪華客船
f.grid(2, [
    "............",
    ".s..u..w..x.",
    "............",
    "...1...4...8",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(2, money=400000, food=-50)

# 島 3 (最初に処理する): ここの船の移動済みの印が島 1・島 2 の船に効く
f.grid(3, [
    "...5........",
    "............",
    "...2........",
    "............",
    "..TTT.......",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(3, money=600000, food=20000)
f.save()
