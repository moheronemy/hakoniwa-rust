#!/usr/bin/env python3
"""phase2-train: doEachHex の線路 (普通電車 10〜19、貨物列車 20〜29) の突き合わせ用データ。
線路と、分岐の無い地形・移植済みの地形 (町・コンデンサ) だけを置く。

rand を 0 に固定すると `random(100)` は 0 なので電車は 1 つ目の方向へ、
0.5 に固定すると 50 なので 2 方向の値は 2 つ目、3 方向の値は 3 つ目の方向へ進む
(3 方向の値の 2 つ目は固定した乱数では選ばれない)。

    python3 -I tools/fixtures/phase2_train.py
    tools/perl-harness/run-harness.sh phase2-train estimate,eachhex,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import SIZE, Fixture  # noqa: E402

# 値の 1 の位ごとの方向 (dx, dy, 位置調整, 進める線路の値)。train.rs の ROUTES と同じ
E1 = [1, 2, 3, 6, 8]
E = [0, 1, 2, 3, 6, 8]
W1 = [1, 4, 5, 7, 9]
W = [0, 1, 4, 5, 7, 9]
NE = [5, 7, 8]
SE = [4, 7]
NW = [3, 6, 9]
SW = [2, 6]
ROUTES = [
    [(1, 0, "dec", E1), (-1, 0, "dec", W1)],
    [(1, 0, "dec", E), (-1, 0, "dec", W)],
    [(1, -1, "dec", NE), (-1, 0, "dec", W)],
    [(1, 1, "dec", SE), (-1, 0, "dec", W)],
    [(1, 0, "dec", E), (-1, -1, "inc", NW)],
    [(1, 0, "dec", E), (-1, 1, "inc", SW)],
    [(1, -1, "dec", NE), (1, 1, "dec", SE), (-1, 0, "dec", W)],
    [(-1, -1, "inc", NW), (-1, 1, "inc", SW), (1, 0, "dec", E)],
    [(-1, 0, "dec", W), (-1, 1, "inc", SW)],
    [(1, 0, "dec", E), (1, 1, "dec", SE)],
]


def route(lv):
    if lv == 19:
        return [(0, 0, "dec", E)] + ROUTES[9][1:]
    return ROUTES[lv % 10]


def target(x, y, step):
    dx, dy, adj, _ = step
    sx, sy = x + dx, y + dy
    if adj == "dec" and sy % 2 == 0 and y % 2 == 1:
        sx -= 1
    if adj == "inc" and sy % 2 == 1 and y % 2 == 0:
        sx += 1
    return sx, sy


def inside(x, y):
    return 0 <= x < SIZE and 0 <= y < SIZE


class Map:
    def __init__(self):
        self.cells = {}

    def put(self, x, y, kind, value):
        assert inside(x, y), (x, y)
        assert (x, y) not in self.cells, (x, y, self.cells[(x, y)], kind, value)
        self.cells[(x, y)] = (kind, value)

    def train(self, x, y, lv, pick=0, targets=None):
        """電車を置き、行き先に進める線路を置く。pick で進める値のどれを使うか選ぶ。
        targets を渡すと、方向ごとにその (地形, 値) を置く (None なら何も置かない)"""
        self.put(x, y, "Train", lv)
        for i, step in enumerate(route(lv)):
            sx, sy = target(x, y, step)
            if (sx, sy) == (x, y) or not inside(sx, sy):
                continue
            if targets is not None:
                if targets[i] is not None:
                    self.put(sx, sy, *targets[i])
            else:
                allowed = step[3]
                self.put(sx, sy, "Train", allowed[(pick + i) % len(allowed)])

    def flat(self):
        return [self.cells.get((x, y), ("Sea", 0)) for y in range(SIZE) for x in range(SIZE)]


BLOCKS = [(x, y) for y in (1, 4, 7, 10) for x in (1, 5, 9)]

f = Fixture("phase2-train")

# 島 1: 普通電車 10〜19、貨物列車 20〜21。行き先はどの方向も進める線路
m = Map()
for (x, y), lv in zip(BLOCKS, range(10, 22)):
    m.train(x, y, lv, pick=lv)
# 値 19 の 1 つ目の方向は自分のマス。右隣に進める線路があっても進まない
m.put(2, 10, "Train", 1)
m.put(11, 0, "Town", 120)
m.put(3, 0, "Conden3", 3000)
m.put(7, 0, "Conden3", 3000)
f.map(1, m.flat())
f.main(1, money=500000, food=50000)

# 島 2: 貨物列車 22〜29 と、進めない電車 (行き先が違う値の線路・別の電車・線路でない)
m = Map()
for (x, y), lv in zip(BLOCKS, range(22, 30)):
    m.train(x, y, lv, pick=lv + 3)
# 進めない: 行き先の値が条件に無い / 別の電車 / 町や平地
m.train(5, 10, 10, targets=[("Train", 0), ("Train", 4)])
m.train(9, 10, 23, targets=[("Train", 11), ("Plains", 0)])
m.train(1, 10, 17, targets=[("Town", 30), ("Train", 3), ("Train", 9)])
# 電車の走っていない線路 (何もしない)
for i, v in enumerate(range(0, 10)):
    if (i, 0) not in m.cells:
        m.put(i, 0, "Train", v)
m.put(11, 11, "Town", 150)
m.put(11, 0, "Conden3", 3000)
f.map(2, m.flat())
f.main(2, money=500000, food=50000)

# 島 3: 島の外に出る電車 (next で災害判定を飛ばす)、行の位置調整で島の中に収まる電車、
# 電力不足で止まる (消える) 電車
m = Map()
m.train(11, 1, 10, targets=[None, ("Train", 1)])   # rand 0: x=12
m.train(0, 4, 20, targets=[("Train", 1), None])    # rand 0.5: x=-1
m.train(5, 0, 12, targets=[None, ("Train", 0)])    # rand 0: y=-1
m.train(5, 11, 13, targets=[None, ("Train", 9)])   # rand 0: y=12
m.train(0, 6, 24, targets=[("Train", 0), ("Train", 3)])   # rand 0.5: (-1,5) が (0,5) に
m.train(0, 8, 25, targets=[("Train", 2), ("Train", 6)])   # rand 0.5: (-1,9) が (0,9) に
m.train(0, 11, 15)                                 # rand 0.5: y=12
m.train(11, 6, 27)                                 # rand 0.5: x=12
m.train(11, 9, 16)                                 # rand 0: (12,8) が (11,8) に
m.train(11, 3, 29)                                 # rand 0.5: (12,4)
# 電力不足: 島の中ほどに電車を並べる (後の電車ほど電力が足りなくなる)
m.train(4, 3, 11, pick=1)
m.train(7, 3, 21, pick=2)
m.train(4, 6, 14, pick=0)
m.train(7, 6, 24, pick=3)
m.train(4, 9, 18, pick=1)
m.train(7, 9, 28, pick=0)
m.put(3, 11, "Town", 100)
m.put(9, 0, "Conden2", 150)
f.map(3, m.flat())
f.main(3, money=500000, food=50000)
f.save()
