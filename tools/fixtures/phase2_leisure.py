#!/usr/bin/env python3
"""phase2-leisure: doEachHex のリゾート地・臨海リゾートホテル・カジノ・動物園・野球場・
海あみゅ・腐海・枯死海の突き合わせ用データ。分岐の無い地形と、移植済みの地形だけを置く。

    python3 -I tools/fixtures/phase2_leisure.py
    tools/perl-harness/run-harness.sh phase2-leisure estimate,eachhex,estimate

rand 0 のとき観光先は島 1 (配列の 2 番目)、rand 0.5 のときは島 3 (先頭)。
島 1 は人口が多く電力が足りている。島 3 と島 2 は発電所が無い (消費 > 供給)。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

LEGEND = {
    ".": ("Sea", 0),
    "T": ("Town", 200),
    "t": ("Town", 100),
    "N": ("Mountain", 50),
    "f": ("EneFw", 500),
    "P": ("Plains", 0),
    "W": ("Waste", 0),
    "H": ("Haribote", 0),
    "B": ("Base", 500),
    "r": ("Rizort", 50),
    "R": ("Rizort", 450),
    "q": ("Rizort", 5),
    "1": ("Rizort", 1),
    "k": ("Kajino", 1500),
    "j": ("Kajino", 50),
    "m": ("Kajino", 300),
    "J": ("Kajino", 2100),
    "g": ("BigRizort", 300),
    "G": ("BigRizort", 1000),
    "o": ("BigRizort", 5),
    "Y": ("Kyujo", 1),
    "U": ("Umiamu", 1),
    "Z": ("Zoo", 50),
    "x": ("RottenSea", 5),
    "X": ("RottenSea", 19),
    "a": ("RottenSea", 4000),
    "b": ("RottenSea", 1001),
    "c": ("RottenSea", 751),
    "d": ("RottenSea", 501),
    "e": ("RottenSea", 251),
    "h": ("RottenSea", 126),
    "i": ("RottenSea", 20),
}


def zoo(**counts):
    """動物園の動物の数 (etc6)。zoo(z0=3, z13=1) のように書く"""
    z = [0] * 31
    for k, v in counts.items():
        z[int(k[1:])] = v
    return ",".join(str(v) for v in z)


f = Fixture("phase2-leisure")
# 島 1: 人口が多い (観光先)。電力は足りている。腐海 (rand 0 で胞子の疫病) と枯死海
f.grid(1, [
    "TTTTTTTTTT..",
    "TTTTTTTTTT..",
    "TTTTTTTTTT..",
    "TTTTTTTTTT..",
    "TYrRq1JGk...",
    ".U.NfffB.Z..",
    "............",
    "..ab.cd.....",
    "..eh.i......",
    "..H...ii....",
    ".WxX.xWi....",
    "..P.........",
], LEGEND)
f.main(1, money=500000, mountain=50, eis1=0, prize="0,0,")
f.ips(1, etc6=zoo(z1=2))

# 島 3: 人口は中くらい、電力不足。野球場が 2 つ (収益なし)、動物園 (レナが多い)
f.grid(3, [
    "............",
    ".TTTTT......",
    ".rkjgGq.....",
    ".YYW.U......",
    "..Z.........",
    "............",
    "............",
    "............",
    "........B...",
    "............",
    "............",
    "............",
], LEGEND)
f.main(3, money=500000, prize="0,0,")
f.ips(3, etc6=zoo(z0=1, z15=1))

# 島 2: 人口が少ない、電力不足。動物園 2 つ (怪獣の入荷と脱走)、怪獣に襲われるホテルとカジノ
f.grid(2, [
    "............",
    "...W...W....",
    "..ZgtrZo....",
    "..m.U.......",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(2, money=500000, prize="0,8192,")
f.ips(2, etc6=zoo(z0=3, z13=1, z15=2))
f.save()
