#!/usr/bin/env python3
"""size-*: 地図の大きさ ($HislandSize) を 12 以外にした島で、ターンを通しで突き合わせる。

Perl 版との突き合わせは 12 × 12 でしかしていなかったので、大規模化 (docs/SCALING.md) に向けて
大きな地図でも同じ結果になることを確かめる。作り方は phase4_mix と同じ (全地形・全種類の計画・
政策) で、地図の大きさと計画の座標の範囲だけが違う。島の数は 3 (legacy-turn3 のまま)。

    python3 -I tools/fixtures/scale_size.py
    RANDS="50 75 96875" tools/perl-harness/run-harness.sh size-128-1 \\
        estimate,income,commands,eachhex,process,estimate
"""
import contextlib
import io
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, LAND, Fixture  # noqa: E402

# phase2_mix / phase3_mix / phase4_mix は読み込むと自分の fixture を作り直す (同じ内容になる)。出力は捨てる
with contextlib.redirect_stdout(io.StringIO()):
    from phase2_mix import value  # noqa: E402
    from phase3_mix import KINDS  # noqa: E402
    from phase4_mix import policy  # noqa: E402


def island_map(rng, size, sea_ratio):
    names = [n for n in LAND if n != "Sea"]
    cells = []
    for _ in range(size * size):
        name = "Sea" if rng.random() < sea_ratio else rng.choice(names)
        cells.append((name, value(rng, name)))
    return cells


def commands(rng, size, n):
    """phase3_mix.commands と同じ。座標は地図全体から選ぶ"""
    out = []
    for _ in range(n):
        kind = COMMAND[rng.choice(KINDS)]
        out.append((kind, rng.choice([1, 2, 3, 3, 99]), rng.randrange(size), rng.randrange(size),
                    rng.choice([0, 1, 1, 2, 3, 5, 9])))
    return out


# (名前, 地図の大きさ, 海の割合)。13 は 12 のすぐ上 (端の判定)、32 は中くらい、128 は目標の大きさ
CASES = [
    ("size-13-1", 13, 0.25),
    ("size-32-1", 32, 0.25),
    ("size-128-1", 128, 0.25),
    ("size-128-2", 128, 0.6),
]

for n, (name, size, sea) in enumerate(CASES):
    rng = random.Random(8000 + n)
    f = Fixture(name, size=size)
    for island_id in (1, 2, 3):
        cells = island_map(rng, size, sea)
        # 文部科学省 (大学 77) が無いと estimate が政策を消す
        cells[rng.randrange(len(cells))] = ("College", 77)
        f.map(island_id, cells)
        f.main(island_id, money=rng.randrange(20000, 1500000), food=rng.randrange(0, 120000),
               pts=rng.randrange(1000, 80000),
               eis1=rng.randrange(0, 5), eis2=rng.randrange(0, 5), eis3=rng.randrange(0, 5),
               eis4=rng.randrange(0, 5), eis5=rng.randrange(0, 60), eis6=rng.randrange(0, 40),
               eis7=rng.choice([0, 0, 150050, 2000099]))
        f.ips(island_id, etc5=policy(rng),
              etc8=",".join(str(rng.randrange(0, 3)) for _ in range(7)))
        f.commands(island_id, commands(rng, size, 20))
    f.save()
