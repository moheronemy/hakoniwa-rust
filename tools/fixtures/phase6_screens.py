#!/usr/bin/env python3
"""phase6-screens*: ハコオクの入札・toto の予想・首都名・アンケート・援助射撃の申請 (hako-map.cgi の
auctionMain / totoMain / totosMain / changeAnkeito / msMain / ms2Main) の突き合わせ用データ。

ハコオクの出品: 1 枠目は最高額 5 (島 2 がトップ)、2 枠目は落札済み (状態 15)、3 枠目は最高額 0。
アンケートの票は 1,2,3,4,5。
島 1: 資金 50000、利益 (pika) 0、auc9 の先頭 3 (入札できる額が 3 兆円増える)。未投票。
島 2: 資金 500、利益 100、auc1 = 5 (1 枠目のトップ)。投票済み (anflag 2)。島 3 へ援助射撃を申請中
      (etc7 = 1,3,3)。首都名 (totoyoso2) は 555。
島 3: 資金 30000、利益 0、auc9 が正規表現に合わない "5,x" (直前のマッチの値が使われる)。
      島 1 へ援助射撃を申請中 (etc7 = 1,5,1)。

ターン数だけを変えたものも作る (toto の受付期間とハコオクの落札判定の境目):
phase6-screens (3), phase6-screens-t25, -t26, -t49, -t50, -t76, -t89, -t90。

    python3 -I tools/fixtures/phase6_screens.py
    python3 -I tools/perl-harness/run_cgi.py crates/hakoniwa-core/tests/fixtures/cgi/<case>.json
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import POS, Fixture  # noqa: E402


def set_lines(f, file, values):
    """file の行を {行番号: 値} で書き換える"""
    lines = (f.dir / file).read_bytes().split(b"\n")
    for i, v in values.items():
        lines[i] = str(v).encode("euc_jp")
    (f.dir / file).write_bytes(b"\n".join(lines))


for turn in [3, 25, 26, 49, 50, 76, 89, 90]:
    f = Fixture("phase6-screens" if turn == 3 else f"phase6-screens-t{turn}")
    # ターン数 (hakojima.dat 1 行目)
    set_lines(f, "hakojima.dat", {0: turn})
    # ハコオクの出品 3 枠 (品番,値,状態,最高額,最高額の島)
    set_lines(f, "auction.dat", {0: "16,0,2,5,0", 1: "12,0,15,8,0", 2: "7,0,2,0,0"})
    # アンケートの票 (an.dat 先頭 5 行) と各島の投票フラグ (その後に島ごと 1 行)
    votes = {i: i + 1 for i in range(5)}
    votes.update({5 + POS[1]: 1, 5 + POS[2]: 2, 5 + POS[3]: 1})
    set_lines(f, "an.dat", votes)

    f.main(1, money=50000)
    f.owner(1, pika=0, totoyoso2=0)
    f.auction(1, auc1=0, auc2=0, auc3=0, auc9="3,0,0,0,0")
    f.ips(1, etc7="0,0,0")

    f.main(2, money=500)
    f.owner(2, pika=100, totoyoso2=555)
    f.auction(2, auc1=5, auc2=0, auc3=0, auc9="0,0,0,0,0")
    f.ips(2, etc7="1,3,3")

    f.main(3, money=30000)
    f.owner(3, pika=0, totoyoso2=0)
    f.auction(3, auc1=0, auc2=0, auc3=0, auc9="5,x")
    f.ips(3, etc7="1,5,1")
    f.save()
