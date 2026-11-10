#!/usr/bin/env python3
"""phase4-migrate-*: 失業者の移民 (doIslandunemployed) とリゾートに飽きられた観光者の移住の突き合わせ用データ。

rand を小さく固定すると移民・移住が起きる (ほかの段階は 1/32 以下でも何も起きない)。
    rand 1/64 (015625): 失業者の移民と、リゾート飽きられの 1 つ目の分岐 (リゾートのある島へ)
    rand 1/32 (03125):  失業者の移民と、リゾート飽きられの 2 つ目の分岐 (町へ帰る)
    rand 0.5:           どれも起きない

島は hakojima.dat の並び (島 3, 1, 2) の順に処理され、rand を小さく固定すると
移民先を探す順番は 2 番目 (島 1)、3 番目 (島 2)、1 番目 (島 3) になる。

    python3 -I tools/fixtures/phase4_migrate.py
    RANDS="015625 03125 50" tools/perl-harness/run-harness.sh phase4-migrate-1 \\
        estimate,income,commands,eachhex,process,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402


def etc5(s06):
    # 先頭が 0 だと estimate が `$etc5 == 0` とみなして全部 0 にする
    return ",".join(["1"] + ["0"] * 5 + [str(s06)] + ["0"] * 24)


def quiet(f):
    # 人工衛星・天気は置かず、食料は足りるようにする (維持・災害の段階が動かないように)
    for island_id in (1, 2, 3):
        f.main(island_id, food=90000, eisei1=0, **{f"eis{i}": 0 for i in range(1, 8)})


# 1: 移民先が見つかる。島 1 は仕事が余っていて、リゾートがある
f = Fixture("phase4-migrate-1")
# 島 3: 人口が多く仕事が無い (失業者)。リゾートもある
f.map(3, [("Town", 200)] * 20 + [("Rizort", 300), ("Rizort", 2), ("Kajino", 100)]
      + [("Minato", 150), ("Bigtown", 200), ("Plains", 0)] + [("Plains", 0)] * 10)
f.ips(3, etc5=etc5(0))
# 島 1: 農場が多い (仕事が余る)。値が上限を超えたリゾートもある
# (政策の値は文部科学省が無いと 0 になる)
f.map(1, [("Farm", 50)] * 10 + [("Rizort", 400), ("Rizort", 340), ("BigRizort", 790),
                                 ("Kajino", 1990), ("Town", 20), ("Newtown", 30), ("College", 77)]
      + [("Plains", 0)] * 20)
f.ips(1, etc5=etc5(10))
# 島 2: 人口が多く仕事が無い。リゾートがあり、政策の値が島 1 より大きい
# (人口が島 1 より少なく、移住先が見つからない)
f.map(2, [("Town", 250)] * 6 + [("Rizort", 200), ("Onsen", 100), ("Seacity", 100),
                                ("College", 77)] + [("Plains", 0)] * 6)
f.ips(2, etc5=etc5(20))
quiet(f)
f.save()

# 2: 移民先に関所がある
f = Fixture("phase4-migrate-2")
f.map(3, [("Town", 200)] * 8 + [("Rizort", 300), ("Kajino", 100)] + [("Plains", 0)] * 10)
f.ips(3, etc5=etc5(0))
# 島 1: 左上が平地 (関所で人数が 0 でも値 0 の町になる)。関所が 2 つ
f.map(1, [("Plains", 0)] + [("Farm", 50)] * 5 + [("Seki", 0), ("Rizort", 100), ("Seki", 0),
                                                ("Town", 20)] + [("Plains", 0)] * 20)
f.ips(1, etc5=etc5(0))
f.map(2, [("Town", 250)] * 6 + [("Rizort", 200)] + [("Plains", 0)] * 6)
f.ips(2, etc5=etc5(0))
quiet(f)
f.save()

# 3: どの島も仕事が足りない (移民先が無い)。島 3 は暴動、島 1 はデモ行進
f = Fixture("phase4-migrate-3")
f.map(3, [("Town", 200)] * 8 + [("Farm", 5), ("Factory", 10), ("Park", 1), ("Base", 0),
                                ("Defence", 0), ("Mine", 1)] + [("Plains", 0)] * 6)
f.map(1, [("Town", 200)] * 6 + [("Plains", 0)] * 6)
f.map(2, [("Town", 150)] * 6 + [("Farm", 2), ("College", 0)] + [("Plains", 0)] * 6)
for island_id in (1, 2, 3):
    f.ips(island_id, etc5=etc5(0))
quiet(f)
f.save()
