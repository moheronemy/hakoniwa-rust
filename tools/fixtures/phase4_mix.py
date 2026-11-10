#!/usr/bin/env python3
"""phase4-mix-*: 全地形・全種類の計画・政策・人工衛星を混ぜた島で、島全体の処理
(doIslandProcess / doIslandunemployed) まで含めたターンを通しで突き合わせる。

phase3_mix と同じ作り方に、政策 (etc5、文部科学省つき)、人工衛星、怪獣派遣の状態を足す。
Perl 版は乱数の固定値が小さいと終わらない道筋がある (隕石のくり返しは random(2) == 0 の
あいだ続く) ので、rand は 1/2 以上に固定する。

    python3 -I tools/fixtures/phase4_mix.py
    RANDS="50 75 96875" tools/perl-harness/run-harness.sh phase4-mix-1 \\
        estimate,income,commands,eachhex,process,estimate,income,commands,eachhex,process,estimate
"""
import contextlib
import io
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

# phase2_mix / phase3_mix は読み込むと自分の fixture を作り直す (同じ内容になる)。出力は捨てる
with contextlib.redirect_stdout(io.StringIO()):
    from phase2_mix import island_map  # noqa: E402
    from phase3_mix import commands  # noqa: E402


def policy(rng):
    """etc5 ($s00..$s30)。先頭が 0 だと estimate が消すので 1 以上"""
    v = [rng.randrange(1, 4)] + [rng.choice([0, 0, 1, 3, 8, 20, 60]) for _ in range(30)]
    return ",".join(str(x) for x in v)


for seed in range(1, 7):
    rng = random.Random(4000 + seed)
    f = Fixture(f"phase4-mix-{seed}")
    for island_id in (1, 2, 3):
        cells = island_map(rng, 0.25)
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
        f.commands(island_id, commands(rng, 20))
    f.save()



# phase4-policy-1..4: 島全体の処理だけを回す (STEPS=process)。doEachHex を通さないので
# 文部科学省 (大学 77) が島役所に戻らず、政策の調整・維持費・食料と資金のあふれの上限
# (s12b) が最後の estimate のあとも残る
for seed in range(1, 5):
    rng = random.Random(4100 + seed)
    f = Fixture(f"phase4-policy-{seed}")
    for island_id in (1, 2, 3):
        cells = island_map(rng, 0.25)
        cells[rng.randrange(len(cells))] = ("College", 77)
        f.map(island_id, cells)
        f.main(island_id, money=rng.randrange(500000, 9000000), food=rng.randrange(50000, 900000),
               pts=rng.randrange(1000, 80000), eis1=rng.randrange(0, 5), eis5=rng.randrange(0, 60))
        f.ips(island_id, etc5=policy(rng),
              etc8=",".join(str(rng.randrange(0, 3)) for _ in range(7)))
    f.save()
