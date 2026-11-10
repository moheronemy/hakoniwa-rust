#!/usr/bin/env python3
"""phase2-stadium*: 多目的スタジアム (Hakoniwa Cup) の突き合わせ用データ。

Hakoniwa Cup の段階はターン数 % 100 で決まるので、ターンを変えた fixture を複数作る。
島の並び (処理順) は ID 3, 1, 2。チームは eisei4
(攻撃,守備,キーパー,勝,分,負,通算勝,通算分,通算負,優勝回数,段階)。
rand 0 では試合は 0−0 (予選は引き分け、決勝トーナメントはくじで自島の勝ち)、
rand 0.5 では random(n) = int(n/2) なので能力の差で勝敗が決まる。

    python3 -I tools/fixtures/phase2_stadium.py
    for f in phase2-stadium phase2-stadium-reset phase2-stadium-r2 phase2-stadium-r4 \\
             phase2-stadium-qf phase2-stadium-sf phase2-stadium-final phase2-stadium-end \\
             phase2-stadium-52; do
        tools/perl-harness/run-harness.sh $f estimate,eachhex,estimate
    done
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

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

# 町に囲まれたスタジアム (町 9 → 収入あり)、発電所あり
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
# 同じ町並みで発電所なし (消費 > 供給なので収入が 1/5)
MAP_TOWNS_NOPOWER = [r.replace("f", ".") for r in MAP_TOWNS]
# 周りに町の無いスタジアム (収入が 0 以下になる)、発電所なし (消費 > 供給)
MAP_LONELY = [
    "............",
    ".WWW........",
    ".WKW....tt..",
    ".WWN....tt..",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
]
# スタジアム 2 つ (kyu > 1 なので収入なし)
MAP_TWO = [
    "............",
    "..TTTT......",
    "..TKKT......",
    "..TTTT......",
    "....P.......",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
]


def build(name, turn, teams, maps, auc9=None, money=None):
    """teams / maps / auc9 / money は 島 ID → 値"""
    f = Fixture(name)
    path = f.dir / "hakojima.dat"
    lines = path.read_bytes().split(b"\n")
    lines[0] = str(turn).encode()
    path.write_bytes(b"\n".join(lines))
    for island_id in (3, 1, 2):
        f.grid(island_id, maps[island_id], LEGEND)
        f.main(island_id, eisei4=teams[island_id], money=(money or {}).get(island_id, 500000),
               mountain=10)
        if auc9 and island_id in auc9:
            f.auction(island_id, auc9=auc9[island_id])
    f.save()


# 予選第１戦 (ターン 105)。島 3 は島 1 より弱い (rand 0.5 で負け)。島 2 は相手がいない
build("phase2-stadium", 105, {
    3: "20,20,20,0,0,0,3,1,2,0,1",
    1: "60,60,60,1,0,0,4,0,0,1,1",
    2: "5,5,5,0,0,0,0,0,0,0,1",
}, {3: MAP_TOWNS, 1: MAP_LONELY, 2: MAP_TWO}, auc9={1: "5,1,45000,2,1", 3: "x,y"})

# 開幕 (ターン 200): 成績を消して参加。島 3 はスタジアム 2 つ (stsankahantei が 2 になる)
build("phase2-stadium-reset", 200, {
    3: "20,20,20,3,1,0,3,1,2,0,9",
    1: "60,60,60,1,0,0,4,0,0,1,14",
    2: "5,5,5,0,0,0,0,0,0,0,11",
}, {3: MAP_TWO, 1: MAP_LONELY, 2: MAP_TOWNS_NOPOWER})

# ターン 111: 第１戦の不戦勝のあと第２戦。rand 0.5 で島 3 が勝ち、島 1 の能力が負の数になる
# (以後 島 1 の eisei4 は形式に合わず、ほかの島の値が入る)
build("phase2-stadium-r2", 111, {
    3: "10,0,0,0,0,0,0,0,0,0,1",
    1: "300,0,0,1,0,0,1,0,0,0,2",
    2: "7,7,7,0,0,0,0,0,0,0,1",
}, {3: MAP_TOWNS, 1: MAP_LONELY, 2: MAP_TWO}, auc9={3: "1,0,9000,0,0"})

# ターン 131: 第３戦の不戦勝のあと第４戦 (島 3 が強い)
build("phase2-stadium-r4", 131, {
    3: "90,40,40,2,0,0,2,0,0,0,3",
    1: "30,30,30,2,1,0,2,1,0,0,4",
    2: "7,7,7,0,0,0,0,0,0,0,2",
}, {3: MAP_TOWNS, 1: MAP_LONELY, 2: MAP_TWO})

# ターン 146: 敗退 (段階 < 6 → 11)、準々決勝、準々決勝の不戦勝。rand 0 で勝つ島 3 の auc9 は
# 形式に合わず、相手の eisei4 のマッチの $1..$5 が使われる
build("phase2-stadium-qf", 146, {
    3: "40,40,40,3,0,1,3,0,1,0,6",
    1: "50,50,50,3,1,0,3,1,0,0,6",
    2: "30,30,30,1,0,3,1,0,3,0,5",
}, {3: MAP_TOWNS, 1: MAP_TWO, 2: MAP_LONELY}, auc9={3: "x,y"})

# ターン 149: 準決勝 (島 3 が強い)、島 2 は試合数の上限で試合できず不戦勝
build("phase2-stadium-sf", 149, {
    3: "60,60,60,4,0,0,4,0,0,0,7",
    1: "40,40,40,4,0,0,4,0,0,0,7",
    2: "30,30,30,4,0,0,4,0,0,0,7",
}, {3: MAP_TOWNS, 1: MAP_LONELY, 2: MAP_TWO})

# ターン 150: 決勝 (rand 0.5 で島 3 が負け、rand 0 でくじで島 3 が勝ち)
build("phase2-stadium-final", 150, {
    3: "30,30,30,5,0,0,5,0,0,0,8",
    1: "60,60,60,5,0,0,5,0,0,2,8",
    2: "30,30,30,4,0,0,4,0,0,0,13",
}, {3: MAP_TOWNS, 1: MAP_LONELY, 2: MAP_TWO}, auc9={1: "3,0,30000,0,0"})

# ターン 151: 決勝の不戦勝 (とりあえずの優勝)、敗退したチームの能力上昇
build("phase2-stadium-end", 151, {
    3: "30,30,30,5,1,0,5,1,0,0,8",
    1: "60,60,60,5,0,0,5,0,0,2,14",
    2: "30,30,30,1,0,3,1,0,3,0,11",
}, {3: MAP_TOWNS, 1: MAP_LONELY, 2: MAP_TWO})

# ターン 152: 優勝 (9) 以外は 10 になって能力上昇
build("phase2-stadium-52", 152, {
    3: "30,30,30,6,1,0,6,1,0,1,9",
    1: "60,60,60,5,0,1,5,0,1,2,14",
    2: "30,30,30,1,0,3,1,0,3,0,12",
}, {3: MAP_TOWNS, 1: MAP_LONELY, 2: MAP_TWO})
