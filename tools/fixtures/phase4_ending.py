#!/usr/bin/env python3
"""phase4-ending: doIslandProcess の最後 (政策・あふれ・寄付・繁栄賞) の突き合わせ用データ。

rand を 0.75 / 0.96875 に固定すると、ほかの段階 (災害・暴動・怪獣・維持・移民) は
Perl 版でも何も起きないので、最後の段階だけを比べられる。

    python3 -I tools/fixtures/phase4_ending.py
    RANDS="75 96875" tools/perl-harness/run-harness.sh phase4-ending \\
        estimate,income,commands,eachhex,process,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

f = Fixture("phase4-ending")
# 島 1: 文部科学省で政策を保ち、町で人口 30 万を超え、神殿・神社がある。食料があふれる
f.map(1, [("College", 77), ("Monument", 26), ("Monument", 27)] + [("Town", 100)] * 32
      + [("Plains", 0)] * 10)
f.main(1, money=900000, food=200000)
# s01..s12 をばらばらにして、すべての調整を通す
f.ips(1, etc5=",".join(str(v) for v in [1, 5, 1, 2, 9, 3, 30, 4, 30, 6, 70, 1, 9] + [2] * 18))
# 島 2: 資金があふれ、大使館 (島 1 と存在しない島 99) に寄付する
f.map(2, [("Taishi", 1), ("Taishi", 99), ("Taishi", 3)] + [("Town", 50)] * 10 + [("Plains", 0)] * 5)
f.main(2, money=1300000, food=500)
# 島 3: 繁栄賞はもう 1 つ持っていて、次 (50 万人) を受賞する
f.map(3, [("Town", 200)] * 26 + [("Plains", 0)] * 6)
f.main(3, money=400000, food=90000, prize="1,0,")
# 人工衛星は置かない (維持の段階が動かないように)
for island_id in (1, 2, 3):
    f.main(island_id, **{f"eis{i}": 0 for i in range(1, 8)})
f.save()
