#!/usr/bin/env python3
"""phase3-mix-*: 全地形を混ぜた島に全種類の計画をランダムに入れ、ターンを通しで突き合わせる。

計画の種類・対象の島・座標・数量はシード固定の乱数で選ぶ。
Perl 版が乱数の固定値によっては終わらなくなる道筋 (動物園建設のくり返し、
魔術師アールヴ = 怪獣 19 の隕石) は使わない。島の放棄も入れない (島が消えて残りを試せない)。

    python3 -I tools/fixtures/phase3_mix.py
    RANDS="0 03125 50 96875" tools/perl-harness/run-harness.sh phase3-mix-1 \\
        estimate,income,commands,eachhex,estimate,income,commands,eachhex,estimate
"""
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, Fixture  # noqa: E402
from phase2_mix import island_map  # noqa: E402

SKIP = {"Zoo", "Giveup", "Ijiri", "DoNothing"} | {k for k in COMMAND if k.startswith("Auto")}
KINDS = sorted(k for k in COMMAND if k not in SKIP)


def commands(rng, n=12):
    out = []
    for _ in range(n):
        kind = COMMAND[rng.choice(KINDS)]
        out.append((kind, rng.choice([1, 2, 3, 3, 99]), rng.randrange(12), rng.randrange(12),
                    rng.choice([0, 1, 1, 2, 3, 5, 9])))
    return out


for seed in range(1, 5):
    rng = random.Random(1000 + seed)
    f = Fixture(f"phase3-mix-{seed}")
    for island_id in (1, 2, 3):
        f.map(island_id, island_map(rng, 0.3))
        f.main(island_id, money=rng.randrange(20000, 1200000), food=rng.randrange(0, 80000),
               pts=rng.randrange(1000, 80000), eis1=rng.randrange(0, 5), eis5=rng.randrange(0, 60),
               eis7=rng.randrange(0, 2000))
        f.commands(island_id, commands(rng))
    f.save()


# phase3-mix-5..8: 計画を 30 件入れ、1 ターンに計画の実行を 3 回ずつ、3 ターン分回す
#   STEPS=estimate,income,commands,commands,commands,eachhex,estimate (を 3 回)
for seed in range(5, 9):
    rng = random.Random(1000 + seed)
    f = Fixture(f"phase3-mix-{seed}")
    for island_id in (1, 2, 3):
        f.map(island_id, island_map(rng, 0.2))
        f.main(island_id, money=rng.randrange(300000, 1200000), food=rng.randrange(20000, 80000),
               pts=rng.randrange(1000, 80000), eis1=rng.randrange(0, 5), eis5=rng.randrange(0, 60),
               eis7=rng.randrange(0, 2000))
        f.commands(island_id, commands(rng, 30))
    f.save()
