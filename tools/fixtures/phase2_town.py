#!/usr/bin/env python3
"""phase2-town: doEachHex の共通部分 (町・港町・海底都市・平地、火災、漏電、不景気、
人口の増減) の突き合わせ用データ。分岐の無い地形 (工場・ハリボテ・大使館など) と
この部分で移植した地形だけを置く。

    python3 -I tools/fixtures/phase2_town.py
    tools/perl-harness/run-harness.sh phase2-town estimate,eachhex,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

LEGEND = {
    ".": ("Sea", 0),
    "T": ("Town", 199),
    "t": ("Town", 150),
    "m": ("Town", 50),
    "v": ("Town", 5),
    "1": ("Town", 1),
    "M": ("Minato", 40),
    "S": ("Seacity", 60),
    "s": ("Seacity", 3),
    "P": ("Plains", 0),
    "W": ("Waste", 0),
    "H": ("Haribote", 0),
    "F": ("Factory", 30),
    "K": ("Kuraf", 10),
    "A": ("Taishi", 2),
    "N": ("Mountain", 10),
    "2": ("Conden2", 500),
    "3": ("Conden3", 800),
    "f": ("EneFw", 300),
    "I": ("Foodim", 100),
}

f = Fixture("phase2-town")
# 島 1: 町の密集地 (現代都市化の判定)、火災の起きる地形、コンデンサ、遺伝子組換え食物
f.grid(1, [
    "............",
    ".PPvMm......",
    ".PttttP.S...",
    "PtttTttP....",
    ".ttTTTttP...",
    "PtttTttP.S..",
    ".PttttPW....",
    "..PPvPWHFK..",
    "..AmmP.N.23.",
    "...mF..I....",
    "..f.......2.",
    "............",
], LEGEND)
f.main(1, money=800000)

# 島 2: 食料不足で町が縮む (村は平地に、海底都市は海に戻る)
f.grid(2, [
    "............",
    ".vvSm.......",
    ".v1M..s.....",
    "..S..PPP....",
    ".....P1P....",
    ".....PPP....",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(2, money=300000, food=-50)

# 島 3: 資金が多いと不景気で doEachHex を飛ばす (rand 0 のとき)
f.grid(3, [
    "............",
    "..PPmm......",
    "..PtTtF.....",
    "..mtAtH.....",
    "..PttPK.....",
    "...MM.......",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(3, money=2000000)
f.save()
