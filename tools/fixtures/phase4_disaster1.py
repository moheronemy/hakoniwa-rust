#!/usr/bin/env python3
"""phase4-disaster1*: doIslandProcess の地震・重税・食料不足・津波・怪獣の出現の突き合わせ用データ。

phase4-disaster1 (rand 1/32 と 0.5):
  島 1: 地ならし 7 回 (地震の確率が 8 倍) と観測衛星 -450 (地震・津波の確率が上がる。
        負の値なので人工衛星の維持は動かない)。rand 1/32 で地震と津波が起きる
  島 2: おまもり 2 つ (etc8 の 2 番目) と観測衛星 -450。地震と津波をおまもりで防ぐ。
        重税 (eisei1 = 70) で暴動が起きる
  島 3: 食料不足。宇宙ステーション (eis7) の住民がいなくなる。地ならし 6 回だけで
        rand 1/32 の地震が起きる (5 回なら起きない)
phase4-disaster1-mon (rand 0): 政策 s04 = 50 で地震・津波・隕石・噴火を、気象衛星 50 で
  台風を止め、怪獣だけが現れるようにする。人口でレベル 4・3・2 の怪獣を出す
phase4-disaster1-mon2 (rand 0): レベル 1 の怪獣、人口が足りない島、町の無い島

山 (鉱山) で仕事を十分に作り、失業者の移民が起きないようにしてある。

    python3 -I tools/fixtures/phase4_disaster1.py
    RANDS="03125 50" tools/perl-harness/run-harness.sh phase4-disaster1 \\
        estimate,income,commands,eachhex,process,estimate
    for f in phase4-disaster1-mon phase4-disaster1-mon2; do
        RANDS=0 tools/perl-harness/run-harness.sh $f estimate,income,commands,eachhex,process,estimate
    done
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, Fixture  # noqa: E402

PREPARE2 = COMMAND["Prepare2"]


def put(f, island_id, cells, fill=("Sea", 0)):
    """cells は {(x, y): (地形名, 値)}。残りは fill"""
    cells.setdefault((5, 9), MEXT)
    flat = [fill] * 144
    for (x, y), c in cells.items():
        flat[y * 12 + x] = c
    f.map(island_id, flat)


def row(cells, y, items, x0=0):
    for i, c in enumerate(items):
        cells[(x0 + i, y)] = c


def policy(**s):
    """etc5 ($s00..$s30)"""
    v = [1] + [0] * 30  # 先頭が 0 だと estimate が数値の 0 とみなして消す
    for k, val in s.items():
        v[int(k[1:])] = val
    return ",".join(str(x) for x in v)


MINES = [("Mountain", 2000)] * 3
# 文部科学省 (大学 77)。これが無いと estimate が政策 (etc5) を消す
MEXT = ("College", 77)

# ---------------------------------------------------------------------------
f = Fixture("phase4-disaster1")
# 島 1: 地震と津波
a = {}
row(a, 1, [("Plains", 0)] * 7, 2)
row(a, 2, [("Town", 150), ("Town", 50), ("Foodim", 100), ("Foodim", 500), ("Procity", 100),
           ("Procity", 200), ("Haribote", 0), ("Park", 0), ("Minato", 10), ("Onsen", 10)], 1)
row(a, 3, [("Kyujo", 0), ("Kyujokai", 0), ("Factory", 30), ("Bigtown", 150), ("Bettown", 150),
           ("Skycity", 150), ("Shuto", 150), ("Rizort", 20), ("Kajino", 20), ("BigRizort", 20)], 1)
row(a, 4, [("HTFactory", 20), ("SHTF", 20), ("Newtown", 150), ("Newtown", 50), ("Farmchi", 30),
           ("Farmpic", 500), ("Farmcow", 40), ("Farm", 10), ("EneAt", 100), ("Train", 0)], 1)
row(a, 5, [("Fune", 1), ("Nursery", 10), ("Mine", 5)] + MINES + [("Forest", 10), ("Seki", 0),
           ("College", 0), ("Zoo", 0)], 1)
row(a, 6, [("Umishuto", 150), ("Conden", 0), ("Defence", 0), ("Base", 0), ("Kura", 0),
           ("Umicity", 150)], 1)
put(f, 1, a)
f.commands(1, [(PREPARE2, 0, x, 1, 0) for x in range(2, 9)])
f.main(1, money=50000, food=50000, eis2=-450)
f.ips(1, etc5=policy(s06=2))

# 島 2: おまもりと暴動
b = {}
row(b, 1, [("Farm", 10), ("College", 0), ("Yakusho", 0), ("Factory", 30), ("SHTF", 20),
           ("HTFactory", 20), ("Nursery", 10), ("EneAt", 100), ("EneFw", 100), ("Base", 0)], 1)
row(b, 2, [("Park", 0), ("Kyujo", 0), ("Zoo", 0), ("House", 0), ("Train", 0), ("Kura", 0),
           ("Kuraf", 0), ("Defence", 0), ("Town", 50), ("Minato", 10)], 1)
row(b, 3, [("Foodim", 100), ("Procity", 100), ("Farmchi", 30), ("Farmpic", 30), ("Farmcow", 30),
           ("Plains", 0)] + MINES, 1)
row(b, 4, [("Sbase", 0), ("Seacity", 50), ("Umiamu", 10), ("Frocity", 50), ("Forest", 10)], 1)
put(f, 2, b)
f.main(2, money=50000, food=50000, eis2=-450, eisei1=70)
f.ips(2, etc5=policy(s06=2), etc8="0,2,0,0,0,0,0")

# 島 3: 食料不足と宇宙ステーション
c = {}
row(c, 1, [("Farm", 1), ("Foodim", 1), ("Foodka", 0), ("Farmchi", 30), ("Farmpic", 30),
           ("Farmcow", 30), ("College", 0), ("Yakusho", 0), ("Factory", 30), ("HTFactory", 20)], 1)
row(c, 2, [("SHTF", 20), ("Nursery", 1), ("Base", 0), ("Mine", 5), ("Kura", 0), ("Kuraf", 0),
           ("Defence", 0), ("Town", 50), ("Plains", 0), ("Forest", 10)], 1)
row(c, 3, MINES, 1)
row(c, 4, [("Plains", 0)] * 6, 1)
put(f, 3, c)
f.commands(3, [(PREPARE2, 0, x, 4, 0) for x in range(1, 7)])
f.main(3, money=50000, food=-90000, eis7=1050)
f.ips(3, etc5=policy(s06=2))
for i in (1, 2):
    f.main(i, eis1=0, eis3=0, eis4=0, eis5=0, eis6=0, eis7=0)
f.main(3, eis1=0, eis2=0, eis3=0, eis4=0, eis5=0, eis6=0)
f.save()


# ---------------------------------------------------------------------------
def quiet(f, island_id):
    """rand 0 で怪獣以外の災害が起きないようにする"""
    f.main(island_id, money=50000, food=90000, eisei1=0, eis1=50,
           **{f"eis{i}": 0 for i in range(2, 8)})
    f.ips(island_id, etc5=policy(s04=50, s06=2))


def towns(cells, kind, value, n, y0=1):
    for i in range(n):
        cells[(1 + i % 10, y0 + i // 10)] = (kind, value)


f = Fixture("phase4-disaster1-mon")
# 島 1: 人口 10000 以上 (レベル 4)。都市 (町) は rand 0 の火災で壊滅するので、輝ける都市にする
a = {}
towns(a, "Bettown", 200, 51)
row(a, 7, MINES * 2, 1)
put(f, 1, a)
# 島 2: 人口 9000 以上 (レベル 3)。最初に見つかる町は大都市
b = {}
towns(b, "Bigtown", 200, 46)
row(b, 7, MINES * 2, 1)
put(f, 2, b)
# 島 3: 人口 7500 以上 (レベル 2)
c = {}
towns(c, "Newtown", 200, 38)
row(c, 7, MINES * 2, 1)
put(f, 3, c)
for i in (1, 2, 3):
    quiet(f, i)
f.save()

f = Fixture("phase4-disaster1-mon2")
# 島 1: 人口 5000 以上 (レベル 1)。いろいろな町
a = {}
towns(a, "Town", 200, 20)
row(a, 4, [("Rizort", 200), ("Kajino", 200), ("BigRizort", 200), ("Bettown", 200),
           ("Skycity", 200), ("Umicity", 200)], 1)
row(a, 7, MINES * 2, 1)
put(f, 1, a)
# 島 2: 人口が足りない (4000)。火災で壊滅しない大都市
b = {}
towns(b, "Bigtown", 200, 20)
row(b, 7, MINES * 2, 1)
put(f, 2, b)
# 島 3: 人口はあるが、怪獣の現れる町が無い (海上都市・首都だけ)
c = {}
towns(c, "Seacity", 200, 30)
row(c, 7, MINES * 2, 1)
put(f, 3, c)
for i in (1, 2, 3):
    quiet(f, i)
f.save()
