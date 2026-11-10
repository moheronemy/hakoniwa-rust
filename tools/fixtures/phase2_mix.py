#!/usr/bin/env python3
"""phase2-mix-*: 全地形を混ぜた島で doEachHex 全体を突き合わせる (系統をまたぐ相互作用)。

島の地図は乱数 (シード固定) で作る。地形ごとに、Perl 版でありうる値の範囲から選ぶ。

    python3 -I tools/fixtures/phase2_mix.py
    tools/perl-harness/run-harness.sh phase2-mix-1 estimate,income,commands,eachhex,estimate,eachhex,estimate
    (phase2-mix-2 .. も同じ)

Perl 版は rand() を 0 に固定すると、魔術師アールヴ (怪獣 19) の隕石のループが終わらない。
そのためアールヴは置かない。
"""
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import LAND, Fixture, monster  # noqa: E402

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


for seed in range(1, 5):
    rng = random.Random(seed)
    f = Fixture(f"phase2-mix-{seed}")
    for island_id in (1, 2, 3):
        f.map(island_id, island_map(rng, 0.3))
        f.main(island_id, money=rng.randrange(1000, 900000), food=rng.randrange(-100, 50000),
               eis1=rng.randrange(0, 5), eis5=rng.randrange(0, 60), eis7=rng.randrange(0, 2000))
    f.save()

# 複合値が壊れている (負の数を含む) 島: 正規表現が一致しないときの $1.. の扱いを全体で確かめる
for seed in (5, 6):
    rng = random.Random(seed)
    f = Fixture(f"phase2-mix-{seed}")
    for island_id in (1, 2, 3):
        f.map(island_id, island_map(rng, 0.3))
        f.main(island_id, money=rng.randrange(1000, 900000), food=rng.randrange(-100, 50000),
               eisei4=f"{rng.randrange(0, 300)},-{rng.randrange(1, 50)},5,1,0,0,2,1,0,0,0",
               eisei5=f"{rng.randrange(1, 15)},-3,4,5,0,0,0")
        f.ips(island_id, etc6=",".join(str(rng.randrange(-2, 5)) for _ in range(31)),
              etc8=f"1,-{rng.randrange(1, 9)},0,0,0,0,0")
        f.auction(island_id, auc9=f"-5,{rng.randrange(0, 9)},100,0,0", auc6="1,-1,0")
    f.save()
