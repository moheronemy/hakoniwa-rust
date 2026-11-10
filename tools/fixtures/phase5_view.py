#!/usr/bin/env python3
"""phase5-view-*: 観光画面・開発画面に出る地図と島の情報を Perl 版と突き合わせるための島。

- phase5-view-1: landString が区別する地形と値の範囲をすべて並べた地図 (3 島に分けて置く)、
  情報欄の分岐 (収入見込み・家・衛星・家畜・電力不足・へそくり・政策など) を島ごとに変える
- phase5-view-2, 3: 全地形を混ぜた乱数の地図 (phase2_mix と同じ作り方) と、別の情報の値。
  ターン数を変えて (4, 5) 怪獣の硬化中の画像も確かめる

    python3 -I tools/fixtures/phase5_view.py
    python3 -I tools/perl-harness/run_cgi.py crates/hakoniwa-core/tests/fixtures/cgi/view-1.json
"""
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import LAND, SIZE, Fixture, monster  # noqa: E402

# phase2_mix.py と同じ作り方 (読み込むと phase2-mix-* を作り直すので写してある)
COLLEGE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 77, 78, 79, 80, 95, 96, 97, 98, 99]
MONSTER_KINDS = [k for k in range(31) if k != 19]


def value(rng, name):
    if name == "Monster":
        return monster(rng.choice(MONSTER_KINDS), rng.randrange(1, 16))
    if name == "Monument":
        return rng.randrange(0, 102)
    if name == "College":
        return rng.choice(COLLEGE)
    if name == "Fune":
        return rng.randrange(0, 20)
    if name == "Train":
        return rng.randrange(0, 30)
    if name == "House":
        return rng.randrange(0, 12)
    if name == "Conden4":
        return rng.choice([2, 3, 99])
    if name == "Defence":
        return rng.choice([0, 1, 77])
    if name == "Sea":
        return rng.choice([0, 0, 0, 1])
    if name == "RottenSea":
        return rng.randrange(0, 40)
    if name == "Kura":
        return rng.randrange(0, 1000)
    if name == "Taishi":
        return rng.choice([1, 2, 3, 99])
    if name == "OWNF":
        return rng.randrange(0, 4000)
    if name in ("Skycity", "Umicity", "Bettown", "Shuto", "Umishuto", "Kajino", "BigRizort"):
        return rng.randrange(1, 4000)
    return rng.randrange(0, 600)


def island_map(rng, sea_ratio):
    names = [n for n in LAND if n != "Sea"]
    cells = []
    for _ in range(144):
        name = "Sea" if rng.random() < sea_ratio else rng.choice(names)
        cells.append((name, value(rng, name)))
    return cells


def cells(*groups):
    out = []
    for name, values in groups:
        out += [(LAND[name], v) if isinstance(name, str) else (name, v) for v in values]
    assert len(out) <= SIZE * SIZE, len(out)
    return out + [(0, 0)] * (SIZE * SIZE - len(out))


def set_turn(f, turn):
    lines = f._lines("hakojima.dat")
    lines[0] = str(turn).encode()
    f._write("hakojima.dat", lines)


ISLAND1 = cells(
    ("Sea", [0, 1, 5]), ("Waste", [0, 1, 2]), ("Plains", [0]), ("Plains2", [0]),
    ("Yakusho", [0]), ("Kura", [0, 523, 999, 4095]), ("Kuraf", [0, 57, 999]),
    ("Forest", [0, 37]), ("House", list(range(13))),
    ("Train", [0, 1, 9, 10, 11, 19, 20, 21, 29, 30, 40]), ("Taishi", [0, 1, 2, 3, 99]),
    ("Town", [0, 29, 30, 99, 100, 500]),
    ("Procity", [0, 109, 110, 129, 130, 159, 160, 199, 200]),
    ("College", list(range(10)) + [50, 77, 78, 79, 80, 94, 95, 96, 97, 98, 99]),
    ("Kyujokai", [0]), ("Zoo", [3]), ("Farm", [0, 25]),
    ("EneAt", [100]), ("EneFw", [101]), ("EneWt", [102]), ("EneBo", [103]), ("EneWd", [104]),
    ("EneCs", [105]), ("EneSo", [106]), ("Conden", [10]), ("Conden2", [20]), ("Conden3", [30]),
    ("Conden4", [0, 1, 2, 3, 4, 99]),
)

# Foodka 4 / Conden4 5 は前のマスで最後に決めた名前 ($n) を引き継ぐ (先頭は情報欄の家の名前)
ISLAND2 = cells(
    ("Foodka", [4]), ("Foodim", [0, 479, 480]), ("Foodka", [0, 1, 2, 3, 5]),
    ("Farmchi", [10]), ("Farmpic", [10]), ("Farmcow", [10]), ("Factory", [30]),
    ("HTFactory", [40]), ("SHTF", [50]), ("OWNF", [0, 1234, 2999, 3999, 999]), ("Conden4", [5]),
    ("Base", [0, 20, 60, 120, 200, 500]), ("Sbase", [0, 50, 100, 200]), ("Seacity", [300]),
    ("Frocity", [300]), ("Minato", [200]), ("Onsen", [100]), ("Sunahama", [0]),
    ("Defence", [0, 1, 77]), ("Haribote", [0]), ("Nursery", [30]), ("Mine", [1, 5]),
    ("Ice", [0, 1]), ("Oil", [0]), ("Gold", [20]), ("Mountain", [0, 5]),
    ("Monument", [0, 1, 50, 102, 103, 4095]), ("Fune", [0, 10, 19, 20]), ("Park", [30]),
    ("Kyujo", [0]), ("Umiamu", [40]), ("Seki", [0]), ("RottenSea", [0, 20, 21, 35]),
    ("Newtown", [150]), ("Bigtown", [300]), ("Rizort", [100]), ("Kajino", [200]),
    ("BigRizort", [300]), ("Shuto", [500]), ("Umishuto", [500]), ("Bettown", [1000]),
    ("Skycity", [1500]), ("Umicity", [1500]), ("Seatown", [400]), (71, [0]), (80, [5]),
    (255, [4095]),
)

ISLAND3 = cells(
    ("Monster", [monster(k, (k * 7) % 16) for k in range(32)]),
    ("Forest", [100]), ("Base", [30]), ("Mine", [3]), ("Haribote", [1]),
)

# 開発画面に出る計画の印: 31 未満、70〜79、100〜130 だけ。同じマスに 2 つ、範囲外の座標も
COMMANDS = [
    (1, 1, 0, 0, 0), (2, 1, 0, 0, 0), (30, 1, 1, 0, 0), (31, 2, 2, 0, 0), (41, 1, 3, 0, 0),
    (70, 1, 4, 0, 0), (79, 1, 5, 0, 0), (80, 2, 6, 0, 0), (100, 1, 7, 0, 0), (122, 1, 8, 0, 0),
    (125, 1, 9, 0, 0), (130, 1, 10, 0, 0), (131, 1, 11, 0, 0), (69, 1, 0, 1, 0),
    (12, 1, 12, 3, 0), (13, 1, 11, 11, 0), (0, 1, 1, 1, 0),
]


def info1(f):
    # 島 1: 職場が余る (資金の見込み)、家 Lv1、衛星すべて、家畜、電力不足、へそくり、政策あり
    f.main(1, pop=12000, farm=50, factory="40,30,1,2,0,0,0,0,0,0", mountain=20, money=123456,
           food=4567, area=88, pts=16000, eis1=10, eis2=20, eis3=30, eis4=40, eis5=50, eis6=60,
           eis7=123456, monsterlive=2, monsterlivetype=5, eisei1=5,
           eisei3="100,150,0,5,80", eisei4="11,22,33,4,1,2,40,10,20,3,15",
           eisei5="100,20,30,40,5,600,0", eisei6="1,1,1,1,1,1,1,1,1,1,1,1")
    f.owner(1, rena=95, tare=3, zipro=0, leje=7, fore=330, totoyoso2="ミヤコ")
    f.ips(1, etc5="1,10,5,11,25,12,30,13,35,14,60,15,70" + ",0" * 18,
          etc6="1,2,0,0,0,0,0,0,3" + ",0" * 21 + ",1",
          etc8="0,0,0,0,0,0,0", etc9="0,3,4,2,5,2,6")
    f.auction(1, auc9="12,5,30000,0,0")
    f.commands(1, COMMANDS)
    # 島 2: 農業だけで手一杯、家なし、衛星なし、失業率が負、政策なし
    f.main(2, pop=300, farm=100, factory="0,0,1,0,0,0,0,0,0,0", mountain=0, money=499,
           food=0, area=5, pts=0, eis1=0, eis2=0, eis3=0, eis4=0, eis5=0, eis6=0, eis7=0,
           monsterlive=0, monsterlivetype=0, eisei1=0, eisei3="50,10,0,0,50",
           eisei4="0,0,0,0,0,0,0,0,0,0,0", eisei5="0,0,0,0,0,0,0",
           eisei6="0,0,0,0,0,0,0,0,0,0,0,0")
    f.owner(2, rena=0, tare=0, zipro=0, leje=0)
    f.ips(2, etc5="0" + ",9" * 30, etc9="0,1,2,3,4,5,6")
    f.auction(2, auc9="0,0,0,0,0")
    f.commands(2, [(70, 2, 0, 0, 0), (1, 2, 5, 5, 0)])
    # 島 3: ハイテク職場が余る (補助金の見込み)、家 Lv11 (天空城)、怪獣 31 匹分の出現中の種類
    f.main(3, pop=40000, farm=10, factory="5,5000,0,0,0,0,0,0,0,0", mountain=3, money=2500,
           pts=60000, eis1=0, eis2=0, eis3=0, eis4=0, eis5=0, eis6=0, eis7=99,
           monsterlive=31, monsterlivetype=2**31 - 1, eisei1=12,
           eisei3="900,30,0,0,900", eisei4="5,5,5,1,0,0,1,0,0,0,14",
           eisei6="1,1,1,1,1,1,1,1,1,2,1,1")
    f.owner(3, rena=1234, tare=0, zipro=4, leje=0)
    f.ips(3, etc8="0,1,0,0,0,0,0")
    f.auction(3, auc9="1,1,0,0,0")


f = Fixture("phase5-view-1")
f._set_map(1, ISLAND1)
f._set_map(2, ISLAND2)
f._set_map(3, ISLAND3)
info1(f)
f.save()


def info2(f, rng, turn):
    set_turn(f, turn)
    for island_id in (1, 2, 3):
        f.map(island_id, island_map(rng, 0.2))
    # 家 Lv10 (魔塔)、資金が推定 500 未満
    f.main(1, pop=5000, farm=20, factory="10,10,0,0,0,0,0,0,0,0", mountain=10, money=12,
           pts=56000, eisei1=3, eis7=1, monsterlive=1, monsterlivetype=2**30,
           eisei4="1,2,3,4,5,6,7,8,9,1," + str(turn + 3),
           eisei6="1,1,1,1,1,1,1,1,1,1,1,1")
    f.owner(1, rena=-35)
    f.ips(1, etc8="0,1,0,0,0,0,0", etc5="3,1,2,3,4,5,6,7,8,9,10,11,12" + ",0" * 18)
    # 家 Lv9 (石がない)、失業率ちょうど 0
    f.main(2, pop=1000, farm=40, factory="30,20,2,0,0,0,0,0,0,0", mountain=10, money=1500,
           pts=55001, eisei1=1, eis1=1, monsterlive=0,
           eisei4="1,1,1,0,0,0,0,0,0,0," + str(turn + 6))
    # 家 Lv4、職場ちょうどで余りなし
    f.main(3, pop=1100, farm=10, factory="0,100,0,0,0,0,0,0,0,0", mountain=0, money=500,
           pts=30001, eisei1=100, eis6=1, eisei4="0,0,0,0,0,0,0,0,0,0," + str(turn + 9))
    f.auction(3, auc9="3,4,99999,6,7")


rng = random.Random(51)
f = Fixture("phase5-view-2")
info2(f, rng, 4)
f.commands(1, [(c, 1, rng.randrange(12), rng.randrange(12), 0)
               for c in rng.sample(range(0, 132), 40)])
f.save()

rng = random.Random(52)
f = Fixture("phase5-view-3")
info2(f, rng, 5)
# 島 3: 複合値が壊れている (負の数で正規表現が一致しない)。Perl 版は直前に一致した $1.. を使う:
# 情報欄では eisei3 → auc9 の値、etc5 → prize の値。地図では観光者は 0、開発画面は
# tempOwner が読んだハコオクの 3 枠目の値
BAD = "9,-9"
f.main(3, prize="5,7,12,", eisei3=BAD, eisei4=BAD, eisei5=BAD, eisei6=BAD)
f.ips(3, etc5=BAD, etc6=BAD, etc8=BAD, etc9=BAD)
f.auction(3, auc6=BAD)
f.cells(3, {(0, 0): ("College", 4), (1, 0): ("College", 7), (2, 0): ("Kyujokai", 0),
            (3, 0): ("Zoo", 1), (4, 0): ("College", 77), (5, 0): ("Conden4", 99)})
f.save()
