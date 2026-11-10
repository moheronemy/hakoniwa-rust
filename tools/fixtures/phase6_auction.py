#!/usr/bin/env python3
"""phase6-auction-*: ハコオクの順位・賞品と出品の入れ替え (turnMain 857〜903 行、934〜1116 行) を
ターン全体で突き合わせるためのデータ。

ケース (tests/fixtures/cgi/turn-auction-*.json) で時刻を 1 ターン後にすると、Perl 版は turnMain を
まるごと実行する。hakojima.dat のターン数は「進む前」の値 (ターン杯のターン 100 なら 99)。

- phase6-auction-normal: ターン 51。出品の状態 (3 番目) が 1 進んで 15 になる / 15 で止まる / "007" は 8
- phase6-auction-late: ターン 75 (ターン杯の残り 25 ターンの最初)。5% の締め切り
- phase6-auction-prize: ターン 100。順位 (同点あり)、1 位の連続記録、賞金。1 枠目が 100 兆円で
  売れて新しい品物になり、2 枠目は売れたが少なくてお休み、3 枠目は前回お休み
- phase6-auction-cap: ターン 100。1 位の連続記録が上限 (5) で止まる。1 枠目は前回お休みなので
  売れなくても新しい品物になる
- phase6-auction-many: 32 島。2・3 枠目も乱数で品物を選ぶ (お休みにならない)
- phase6-auction-rest: 32 島。21 島が休み中 (auc6 が 1、estimate ごとに数えて $oyasumiritu = 63)
  で、2・3 枠目は乱数でお休みになる (3 枠目は 750 < 63 * 12.5 で境目の近く)
- phase6-auction-rest9: 32 島。9 島が休み中 ($oyasumiritu = 27)。2 枠目は 750 < 68 + 27 * 25 に
  ならず品物を選ぶ (境目の近く)
- phase6-auction-sold: 32 島。3 枠とも境目の額 (90・120・60 兆円) で売れて新しい品物になる
- phase6-auction-mid: 29 島。2 枠目は乱数で品物を選び、3 枠目は島が 30 未満なのでお休み
- phase6-auction-few: 20 島。2 枠目は島が 20 未満ではないので品物を選ぶ

    python3 -I tools/fixtures/phase6_auction.py
    for c in crates/hakoniwa-core/tests/fixtures/cgi/turn-auction-*.json; do
        timeout 300 python3 -I tools/perl-harness/run_cgi.py $c
    done
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

IDS = (3, 1, 2)  # hakojima.dat の並び


def make(name, turn, lots, islands=None, extra=0, every=None, rest=0):
    """lots: 出品 3 枠の文字列。islands: 島 ID → auction.dat / hakojima.dat の値。
    extra: 島 1 を複製して足す島の数。every: 全島に入れる auction.dat の値。
    rest: 先頭からこの数の島を休み中 (auc6 = 1,0,0) にする"""
    f = Fixture(name)
    f.turn(turn)
    lines = f._lines("auction.dat")
    for i, lot in enumerate(lots):
        lines[i] = lot.encode()
    f._write("auction.dat", lines)
    ids = list(IDS) + (f.add_islands(extra) if extra else [])
    for k, iid in enumerate(ids):
        f.main(iid, money=200000, food=50000)
        if every:
            f.auction(iid, **every)
        if k < rest:
            f.auction(iid, auc6="1,0,0")
    for iid, spec in (islands or {}).items():
        f.main(iid, **spec.get("main", {}))
        f.auction(iid, **spec.get("auction", {}))
    f.save()


make("phase6-auction-normal", 50, ["5,0,14,4,0", "22,3,15,6,2", "12,2500,007,7,3"], {
    3: {"auction": {"auc0": "1,0,9,0,2", "auc4": "2,3,1", "auc1": 4}},
    1: {"auction": {"auc0": "1,0,20,0,1", "auc4": "1,0,0"}},
})

make("phase6-auction-late", 74, ["5,0,3,4,0", "22,3,15,6,2", "12,2500,14,7,3"])

make("phase6-auction-prize", 99, ["17,2,2,100,0", "12,5,2,4,0", "29,0,15,0,0"], {
    3: {"auction": {"auc0": "1,0,9,0,0", "auc4": "3,2,1", "auc1": 100,
                    "auc9": "200,0,2000000,0,0"}},
    1: {"auction": {"auc0": "1,0,20,0,7", "auc4": "2,4,1", "auc2": 4}},
    2: {"auction": {"auc0": "1,0,20,0,0", "auc4": "0,1,0"}},
})

make("phase6-auction-cap", 99, ["29,0,15,0,0", "5,0,7,3,0", "29,0,15,0,0"], {
    3: {"auction": {"auc0": "1,0,5,0,3", "auc4": "1,6,0"}},
    1: {"auction": {"auc0": "1,0,4,0,1", "auc4": "7,2,2"}},
    2: {"auction": {"auc0": "1,0,30,0,2", "auc4": "1,6,0"}},
})

make("phase6-auction-many", 99, ["5,0,3,4,0", "29,0,15,0,0", "29,0,15,0,0"], {
    1: {"auction": {"auc0": "1,0,50,0,0", "auc4": "0,0,0"}},
}, extra=29)

make("phase6-auction-rest", 99, ["5,0,3,4,0", "29,0,15,0,0", "29,0,15,0,0"],
     extra=29, rest=21)

make("phase6-auction-rest9", 99, ["5,0,3,4,0", "29,0,15,0,0", "29,0,15,0,0"],
     extra=29, rest=9)

make("phase6-auction-sold", 99, ["17,2,2,90,0", "12,5,2,120,0", "27,3,2,60,0"], {
    3: {"auction": {"auc1": 90}},
    1: {"auction": {"auc2": 120}},
    2: {"auction": {"auc3": 60}},
}, extra=29, every={"auc9": "200,0,2000000,0,0"})

make("phase6-auction-mid", 99, ["5,0,3,4,0", "29,0,15,0,0", "29,0,15,0,0"], extra=26)

make("phase6-auction-few", 99, ["5,0,3,4,0", "29,0,15,0,0", "29,0,15,0,0"], extra=17)
