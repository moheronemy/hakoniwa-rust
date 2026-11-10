#!/usr/bin/env python3
"""phase3-magic*: doCommand の魔術師派遣 (HcomMagic) の突き合わせ用データ。

魔術師を出す島には魔法の記念碑 (74〜79) と魔法学校 (大学 7)、原子力発電所を置き、
estimate が etc9 (`$co7, $magicf, ...`) を計算するようにする。天空城砲撃には家 11 (h11)。
1 回の commands で島ごとに「1 を返す計画」が 1 つしか実行されないので、
道筋ごとに 4 つのデータに分けてある。

    python3 -I tools/fixtures/phase3_magic.py
    for n in phase3-magic phase3-magic-2 phase3-magic-3 phase3-magic-4; do
      RANDS="0 03125 50 96875" tools/perl-harness/run-harness.sh $n \
        estimate,income,commands,commands,commands,estimate
    done
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, SIZE, Fixture, monster  # noqa: E402

MAGIC = COMMAND["Magic"]


def caster(cells, ene_cells, magic=3, college7=True, h11=False, zoo=()):
    """魔術師を出す島の設備 (下の方の行) を cells に足す"""
    row = []
    for m in (74, 75, 76, 77, 78, 79):
        row += [("Monument", m)] * magic
    if college7:
        row.append(("College", 7))
    if h11:
        row.append(("House", 11))
    row += [("Zoo", v) for v in zoo]
    row += [("EneAt", v) for v in ene_cells]
    for i, c in enumerate(row):
        cells[(i % SIZE, SIZE - 1 - i // SIZE)] = c
    return cells


def put(f, island_id, cells, fill=("Sea", 1)):
    flat = []
    for y in range(SIZE):
        for x in range(SIZE):
            flat.append(cells.get((x, y), fill))
    f.map(island_id, flat)


def cmds(*rows):
    return [(MAGIC, t, x, y, a) if k is None else (k, t, x, y, a) for k, t, x, y, a in rows]


def m(target, x, y, arg):
    return (None, target, x, y, arg)


ZOO_ETC6 = ",".join(["1"] * 3 + ["0"] * 28)  # 動物 3 匹

# ---------------------------------------------------------------------------
# 1: 自分の島の怪獣への攻撃 (next で次の計画へ)、動物園飼育係の捕獲、他の島の平地
f = Fixture("phase3-magic")
c1 = {
    (0, 0): ("Monster", monster(1, 2)),   # 炎で倒れる
    (1, 0): ("Monster", monster(2, 9)),   # 氷では倒れない
    (2, 0): ("Monster", monster(3, 5)),   # 地で倒れる (山になる)
    (3, 0): ("Monster", monster(4, 2)),   # 風 (rand 0 では 0 ダメージ)
    (4, 0): ("Monster", monster(5, 3)),   # 光
    (5, 0): ("Monster", monster(6, 7)),   # 闇 (確率で撃破)
    (6, 0): ("Plains", 0),
    (7, 0): ("Monster", monster(7, 1)),   # 捕獲できる
    (8, 0): ("Monster", monster(7, 2)),   # 捕獲できるが動物園が一杯
    (0, 2): ("Town", 50),
}
# 捕獲の上限 (rena + co4 * 1000 + co99 * 1000) を上げる大学
c1.update({(x, 3): ("College", 4) for x in range(8)})
put(f, 1, caster(c1, [4000] * 30, zoo=[3]))
f.ips(1, etc6=ZOO_ETC6)
f.main(1, money=3000000, prize="0,%d," % (1 << 7))
f.owner(1, rena=5000)
f.commands(1, cmds(
    m(99, 0, 0, 0),    # 目標の島が無い
    m(1, 12, 0, 0),    # 範囲外 (next)
    m(1, 0, 0, 0), m(1, 1, 0, 1), m(1, 2, 0, 2), m(1, 3, 0, 3), m(1, 4, 0, 4), m(1, 5, 0, 5),
    m(1, 6, 0, 8),     # 怪獣でない (arg 8 は 0 になる)
    m(1, 7, 0, 7),     # 捕獲
    m(1, 8, 0, 7),     # 動物園が一杯
))

c2 = {(0, 2): ("Town", 50)}
put(f, 2, caster(c2, [4000] * 30, h11=True))
f.main(2, money=3000000)
f.commands(2, cmds(m(3, 0, 0, 0), m(3, 1, 0, 1), m(3, 2, 0, 6)))

c3 = {(x, 0): ("Plains", 0) for x in range(8)}
c3[(0, 2)] = ("Town", 50)
c3[(0, 11)] = ("Base", 4000)  # 電力不足
put(f, 3, c3)
f.main(3, money=3000000)
f.commands(3, cmds(m(1, 0, 0, 0)))
f.save()

# ---------------------------------------------------------------------------
# 2: 電力の足りない攻撃、捕獲の電力不足・失敗、天空城 (自分の島では何もしない)、
#    魔法学校が無い島、平地 (地・風・光)
f = Fixture("phase3-magic-2")
c1 = {
    (0, 0): ("Monster", monster(2, 5)),
    (1, 0): ("Monster", monster(25, 5)),
    (2, 0): ("Monster", monster(2, 5)),
    (3, 0): ("Monster", monster(3, 5)),
    (0, 2): ("Town", 20),
}
put(f, 1, caster(c1, [3000, 3000], h11=True, zoo=[5]))
f.ips(1, etc6=ZOO_ETC6)
f.main(1, money=3000000, prize="0,%d,7,9," % (1 << 25 | 1 << 3))
f.owner(1, rena=100)
f.commands(1, cmds(
    m(1, 0, 0, 1),     # 氷: 電力が足りない
    m(1, 1, 0, 7),     # 捕獲: 電力が足りない (0 を返す)
    m(1, 2, 0, 7),     # 捕獲: 退治したことが無い怪獣
    m(1, 3, 0, 6),     # 天空城: 自分の島では何もしない
))

c2 = {(0, 2): ("Town", 50)}
put(f, 2, caster(c2, [4000] * 30, magic=4))
f.main(2, money=3000000)
f.commands(2, cmds(m(3, 0, 0, 2), m(3, 1, 1, 3), m(3, 2, 0, 4)))

c3 = {(x, 0): ("Plains", 0) for x in range(8)}
c3[(1, 1)] = ("Plains", 0)
c3[(0, 2)] = ("Town", 50)
put(f, 3, caster(c3, [4000] * 5, college7=False))
f.main(3, money=3000000)
f.commands(3, cmds(m(1, 0, 0, 0)))
f.save()

# ---------------------------------------------------------------------------
# 3: 腐海 (炎・光・闇・天空城) と他の島の怪獣 (炎・氷)
f = Fixture("phase3-magic-3")
rotten = {}
for y in range(1, 9):
    for x in range(SIZE):
        if (x + y) % 3 != 0:
            rotten[(x, y)] = ("RottenSea", 5 + x)
rotten[(0, 0)] = ("Monster", monster(9, 3))
rotten[(1, 0)] = ("Monster", monster(10, 9))
rotten[(2, 0)] = ("Monster", monster(11, 4))
rotten[(5, 0)] = ("Town", 50)

c1 = {(0, 2): ("Town", 50), (0, 0): ("Monster", monster(3, 3)), (1, 0): ("Plains", 0)}
put(f, 1, caster(c1, [4000] * 30, h11=True))
f.main(1, money=3000000)
# 天空城は島 2 の腐海を吹き飛ばす (島 3 の腐海は島 2 の魔術師に残す)
f.commands(1, cmds(m(2, 3, 3, 6), m(3, 0, 0, 0), m(3, 1, 0, 1)))

c2 = {(x, y): ("RottenSea", 20) for x in range(SIZE) for y in range(1, 5)}
c2[(0, 5)] = ("Town", 50)
put(f, 2, caster(c2, [4000] * 30, magic=5))
f.main(2, money=3000000)
f.commands(2, cmds(m(3, 5, 5, 0), m(3, 2, 2, 4), m(3, 2, 3, 5)))

# 島 3 も魔術師を出す: 他の島の怪獣と平地に飼育係 (何もしない・平地は費用だけ)
put(f, 3, caster(rotten, [4000] * 10))
f.main(3, money=3000000)
f.commands(3, cmds(m(1, 0, 0, 7), m(1, 1, 0, 7), m(1, 0, 0, 2)))
f.save()

# ---------------------------------------------------------------------------
# 4: 他の島の怪獣 (地・風・光・闇・天空城・飼育係)、電力切れで止まる腐海、
#    腐海に氷 (何もしない)、動物園の無い島の飼育係、電力の足りない平地
f = Fixture("phase3-magic-4")
t = {}
for y in range(2, 7):
    for x in range(SIZE):
        t[(x, y)] = ("RottenSea", 3)
for x in range(7):
    t[(x, 0)] = ("Monster", monster(12 + x, 2 + x))
t[(8, 0)] = ("Plains", 0)
t[(9, 0)] = ("Town", 50)

c1 = {
    (0, 1): ("Monster", monster(4, 4)),
    (1, 1): ("Monster", monster(5, 5)),
    (3, 1): ("Monster", monster(8, 3)),
    (0, 6): ("Town", 50),
}
put(f, 1, caster(c1, [4000] * 30))
f.main(1, money=3000000)
f.commands(1, cmds(m(3, 0, 0, 2), m(3, 1, 0, 3), m(3, 2, 0, 4)))

# 電力の少ない島: 平地は電力不足、腐海は途中で止まる
c2 = {(0, 1): ("Town", 50)}
put(f, 2, caster(c2, [1000, 900], magic=2))
f.main(2, money=3000000)
f.commands(2, cmds(m(3, 8, 0, 0), m(3, 6, 4, 1), m(3, 5, 4, 0)))

f.main(3, money=3000000)
# 島 3: 闇・天空城で島 1 の怪獣を攻撃、動物園の無い自分の島で飼育係 (何もしない)
t[(10, 0)] = ("Monster", monster(2, 2))
put(f, 3, caster(t, [4000] * 30, h11=True))
f.commands(3, cmds(m(1, 0, 1, 5), m(1, 1, 1, 6), m(3, 10, 0, 7)))
f.save()
