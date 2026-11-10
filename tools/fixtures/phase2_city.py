#!/usr/bin/env python3
"""phase2-city / phase2-city2: doEachHex の都市系 (防災都市・ニュータウン・現代都市・
海底新都市・輝ける都市・空中都市・海都市・首都・海底首都・温泉街) の突き合わせ用データ。
この系統の地形と、分岐の無い地形・移植済みの地形だけを置く。

    python3 -I tools/fixtures/phase2_city.py
    tools/perl-harness/run-harness.sh phase2-city estimate,eachhex,estimate
    tools/perl-harness/run-harness.sh phase2-city2 estimate,eachhex,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

# 町が密集した島 (ニュータウン → 現代都市、現代都市 → 首都)。
# 町は火災で焼けないよう値を 30 以下にしておく
DENSE = {
    ".": ("Sea", 0),
    "T": ("Town", 20),
    "N": ("Newtown", 299),
    "n": ("Newtown", 50),
    "m": ("Newtown", 100),
    "B": ("Bigtown", 199),
    "b": ("Bigtown", 499),
    "E": ("House", 0),
    "R": ("Procity", 50),
    "Q": ("Procity", 99),
    "q": ("Procity", 150),
    "Z": ("Procity", 200),
    "s": ("Seatown", 249),
    "S": ("Seatown", 399),
    "W": ("Waste", 0),
}

# 食料不足で縮む
SHRINK = {
    ".": ("Sea", 0),
    "T": ("Town", 100),
    "r": ("Procity", 1),
    "R": ("Procity", 10),
    "n": ("Newtown", 1),
    "N": ("Newtown", 10),
    "b": ("Bigtown", 1),
    "B": ("Bigtown", 10),
    "s": ("Seatown", 1),
    "S": ("Seatown", 10),
    "e": ("Bettown", 1),
    "E": ("Bettown", 10),
    "X": ("Bettown", 1500),
    "k": ("Skycity", 1),
    "K": ("Skycity", 10),
    "u": ("Umicity", 1),
    "U": ("Umicity", 10),
    "h": ("Shuto", 1),
    "H": ("Umishuto", 10),
    "o": ("Onsen", 1),
    "O": ("Onsen", 10),
}

# 成長と上限
GROW = {
    ".": ("Sea", 0),
    "T": ("Town", 100),
    "M": ("Mountain", 0),
    "h": ("Shuto", 749),
    "H": ("Umishuto", 100),
    "Y": ("Shuto", 100),
    "e": ("Bettown", 500),
    "f": ("Bettown", 999),
    "g": ("Bettown", 1000),
    "i": ("Bettown", 1999),
    "k": ("Skycity", 100),
    "K": ("Skycity", 2249),
    "u": ("Umicity", 100),
    "U": ("Umicity", 2499),
    "o": ("Onsen", 30),
    "O": ("Onsen", 49),
    "P": ("Onsen", 100),
    "N": ("Newtown", 299),
    "B": ("Bigtown", 199),
    "E": ("House", 0),
}

f = Fixture("phase2-city")
# 島 1: 密集地。家が隣に無い現代都市は首都にならない。家が隣の現代都市が首都になり (2 つ目はもう
# 首都にならない)、ニュータウンが現代都市になる。
# 防災都市の成長
f.grid(1, [
    "............",
    ".TTTTTTTTTT.",
    ".TTTTTTTTTT.",
    ".TTNTbTTnTT.",
    ".TTTTTTTTTT.",
    ".TEBTBETTTT.",
    ".TTTTTTTTTT.",
    ".TTbTmTTBET.",
    ".TTTTTTTTTT.",
    "............",
    ".R.Q.q.Z....",
    "............",
], DENSE)
f.main(1, money=500000, food=50000)

# 島 2: 食料不足。どの都市も縮み、値が尽きると平地・海・荒地に戻る (首都は 2 つ)
f.grid(2, [
    "............",
    ".r.R.n.N.b..",
    "............",
    ".B.s.S.e.E..",
    "............",
    ".k.K.u.U.h..",
    "............",
    ".H.o.O.X.T..",
    "............",
    "..TTT.......",
    "............",
    "............",
], SHRINK)
f.main(2, money=400000, food=-50)

# 島 3: 首都が 1 つ。輝ける都市 (首都の隣・2 つ並び・孤立)、空中都市、海都市、温泉街、首都の成長
f.grid(3, [
    "............",
    ".eh.........",
    "............",
    ".fg....i....",
    "............",
    ".k.K.u.U....",
    "............",
    ".o.O.P......",
    "..TTT.......",
    "..TTTM......",
    "............",
    "............",
], GROW)
f.main(3, money=300000, food=20000)
f.save()

f = Fixture("phase2-city2")
# 島 1: 密集地の海底新都市が海底首都になる
f.grid(1, [
    "............",
    ".TTTTTTTTTT.",
    ".TTTTTTTTTT.",
    ".TTTTTTTTTT.",
    ".TTTTsETTTT.",
    ".TTTTTTTTTT.",
    ".TTTTTTTTTT.",
    ".TTTTTTTTTT.",
    "............",
    "..S.........",
    "............",
    "............",
], DENSE)
f.main(1, money=500000, food=50000)

# 島 2: 首都が 2 つ (先に処理した方が開発予定地になる)
f.grid(2, [
    "............",
    ".Y.H........",
    "............",
    ".e.f.g......",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], GROW)
f.main(2, money=400000, food=20000)

# 島 3: 首都が無い (輝ける都市は成長しない)。密集していないニュータウン・現代都市
f.grid(3, [
    "............",
    ".e.fg.......",
    "............",
    ".N..BE......",
    "..TTT.......",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], GROW)
f.main(3, money=300000, food=20000)
f.save()

AX = [0, 1, 1, 1, 0, -1, 0, 1, 2, 2, 2, 1, 0, -1, -1, -2, -1, -1, 0]
AY = [0, -1, 0, 1, 1, 0, -1, -2, -1, 0, 1, 2, 2, 2, 1, 0, -1, -2, -2]


def around(x, y, i):
    sx, sy = x + AX[i], y + AY[i]
    if sy % 2 == 0 and y % 2 == 1:
        sx -= 1
    return sx, sy


def block(center, kind, others):
    """center の周囲 2 ヘックスを町 (値 20、火災で焼けない) で埋め、中心を kind、
    others ({i: (地形名, 値)}、i は @ax/@ay の番号) を置いた cells"""
    x, y = center
    cells = {around(x, y, i): ("Town", 20) for i in range(19)}
    cells[(x, y)] = kind
    for i, v in others.items():
        cells[around(x, y, i)] = v
    return cells


# phase2-city3: 町の数のしきい値ちょうど (ニュータウン > 17、首都 > 16)、上限を超えた値
f = Fixture("phase2-city3")
sea = ("Sea", 0)
# 島 1: 町が 18 (自分を含む。現代都市になる) と 17 (ならない) のニュータウン
f.map(1, [])
f.cells(1, block((2, 3), ("Newtown", 299), {7: sea}))
f.cells(1, block((8, 8), ("Newtown", 299), {7: sea, 11: sea}))
f.cells(1, {(5, 10): ("Shuto", 4095)})
# 島 2: 町が 17 (自分を含む) で家が 1 つの現代都市 (首都になる)
f.map(2, [])
f.cells(2, block((5, 5), ("Bigtown", 199), {2: ("House", 0), 7: sea}))
# 島 3: 町が 16 で家が 1 つの現代都市 (ならない)。上限を超えた値、森に守られた温泉街
f.map(3, [])
f.cells(3, block((3, 3), ("Bigtown", 199), {2: ("House", 0), 7: sea, 11: sea}))
f.cells(3, {
    (9, 1): ("Newtown", 350), (9, 3): ("Bigtown", 600), (9, 5): ("Seatown", 450),
    (9, 7): ("Bettown", 2100), (9, 9): ("Skycity", 3100), (11, 9): ("Umicity", 3100),
    (1, 9): ("Onsen", 30), (2, 9): ("Forest", 10), (1, 10): ("Onsen", 120),
    (0, 7): ("Procity", 250),
})
for i in (1, 2, 3):
    f.main(i, money=400000, food=20000)
f.save()
