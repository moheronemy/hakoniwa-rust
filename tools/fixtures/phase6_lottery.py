#!/usr/bin/env python3
"""phase6-lottery-*: toto・Hakoniwa Cup toto・Numbers3・Numbers4 をターン全体で突き合わせるデータ。

予想は eis8 に書く (`(toto@...)`、`(hc@W.L)`、`(n3@N)`、`(n4@N)`)。島の並び (ファイル上) は
ID 3, 1, 2 なので、Numbers の配当先 ($HidToNumber、読み込んだときの位置) は 3→0, 1→1, 2→2。

- phase6-lottery-100: ターン 100 (toto + Numbers3)。島 3 は海だけで無人島になり、島数カットで
  切り捨てられる (ポイント順は 1, 2, 3)。toto の正解は [1, 2, 3, 0, ...] (切り捨てた島 3 の ID も
  正解に入る)。島 1 は 8 点、島 2 は 6 点 (7 点がいないので 8 点の率は 20 + 8)。Numbers3 は
  rand 0.75 で 749。島 1 と島 2 が的中し、島 1 の配当は位置 1 (島 2) へ、島 2 の配当は
  位置 2 (切り捨てた島 3) へ行く
- phase6-lottery-200: ターン 200 (toto + Numbers3)。島 1 は toto の購入費用が足りない (8 点の予想)。
  島 3 と島 2 が 7 点 (6 点がいないので 7 点の率は 8 + 2 を 2 島で分ける)。Numbers3 は島 2 が当たる
- ターン杯のターンのハコオクの賞金 (islandSortac4 の 1 位) は、どちらのケースも島 2 に行く
- phase6-lottery-150 / -150b: ターン 150 (Hakoniwa Cup の決勝 + Numbers4)。phase2-stadium-final と
  同じチーム (-150b は島 3 と島 1 を入れ替え)。rand 0.5 で -150 は島 1 が優勝 ([1, 3])、
  -150b は島 3 が優勝 ([3, 1])。
  島 2 の auc9 は形に合わず、turnMain の $auction3 のマッチの値が入る

    python3 -I tools/fixtures/phase6_lottery.py
    for c in turn-lottery-100 turn-lottery-200 turn-lottery-150 turn-lottery-150b; do
        python3 -I tools/perl-harness/run_cgi.py crates/hakoniwa-core/tests/fixtures/cgi/$c.json
    done
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

# phase2_stadium.py と同じ地図 (読み込むと phase2-stadium-* を作り直すので写してある)
LEGEND = {
    ".": ("Sea", 0),
    "K": ("Kyujokai", 0),
    "T": ("Town", 100),
    "t": ("Town", 20),
    "M": ("Minato", 40),
    "P": ("Plains", 0),
    "W": ("Waste", 0),
    "N": ("Mountain", 10),
    "f": ("EneFw", 300),
}
MAP_TOWNS = [
    "............",
    "............",
    "...TTT......",
    "..TTKTM.....",
    "...TTT......",
    "....P.......",
    "..fN........",
    "............",
    "............",
    "............",
    "............",
    "............",
]
MAP_LONELY = [
    "............",
    ".WWW........",
    ".WKW....tt..",
    ".WWN....tt..",
] + ["............"] * 8
MAP_TWO = [
    "............",
    "..TTTT......",
    "..TKKT......",
    "..TTTT......",
    "....P.......",
] + ["............"] * 7

# 島 3 を無人島にする海だけの地図
MAP_SEA = ["............"] * 12

# ターン 100
f = Fixture("phase6-lottery-100")
f.turn(99)
f.grid(3, MAP_SEA, LEGEND)
f.main(3, eis8="(toto@1.2.3.0.0.0.0.0)(n3@749)")
f.main(1, eis8="(toto@1.2.3.0.0.0.0.0)(n3@749)")
f.main(2, eis8="x(n3@)(toto@1.9.9.0.0.0.0.0)(n3@0749)")
f.save()

# ターン 200
f = Fixture("phase6-lottery-200")
f.turn(199)
f.main(3, eis8="(toto@3.1.2.0.0.0.0.9)(n3@748)")
f.main(1, money=0, eis8="(n3@1)(toto@3.1.2.0.0.0.0.0)")
f.main(2, eis8="(toto@3.1.5.0.0.0.0.0)(n3@749)")
f.save()


def stadium(name, eis8, money, swap=False):
    f = Fixture(name)
    f.turn(149)
    teams = {
        3: "30,30,30,5,0,0,5,0,0,0,8",
        1: "60,60,60,5,0,0,5,0,0,2,8",
        2: "30,30,30,4,0,0,4,0,0,0,13",
    }
    if swap:
        teams[3], teams[1] = teams[1], teams[3]
    maps = {3: MAP_TOWNS, 1: MAP_LONELY, 2: MAP_TWO}
    for island_id in (3, 1, 2):
        f.grid(island_id, maps[island_id], LEGEND)
        f.main(island_id, eisei4=teams[island_id], money=money[island_id], mountain=10,
               eis8=eis8[island_id])
    f.auction(1, auc9="3,0,30000,0,0")
    f.auction(2, auc9="x,y")
    f.save()


# rand 0.5: 島 1 が優勝、島 3 が準優勝。Numbers4 は 4999
stadium("phase6-lottery-150", {
    3: "(hc@1.3)(n4@4999)",
    1: "(hc@1.3)(n4@4999)",
    2: "(hc@1.2)(n4@04999)",
}, {3: 5000, 1: 500000, 2: 500000})

# 島 3 と島 1 のチームを入れ替える: 島 3 が優勝、島 1 が準優勝。1 点の的中がいないので
# 2 点の率は 10 + 3。Numbers4 は 4999 で誰も当たらず、島 2 は購入費用が足りない
stadium("phase6-lottery-150b", {
    3: "(hc@3.1)(n4@0)",
    1: "(hc@1.3)(n4@1)",
    2: "(hc@3.1)(n4@0)",
}, {3: 500000, 1: 500000, 2: 10}, swap=True)
