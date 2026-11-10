#!/usr/bin/env python3
"""phase6-cup*: Hakoniwa Cup のうち turnMain が行う部分 (シードと開催の記録) の突き合わせ用データ。

ターン全体を Perl 版と比べる (tests/fixtures/cgi/turn-cup-*.json、full_turn_tests.rs)。
島の並び (処理順) は ID 3, 1, 2。チームは eisei4
(攻撃,守備,キーパー,勝,分,負,通算勝,通算分,通算負,優勝回数,段階)。

    python3 -I tools/fixtures/phase6_cup.py
    for c in turn-cup-41 turn-cup-41-none turn-cup-00 turn-cup-00-none; do
        python3 -I tools/perl-harness/run_cgi.py crates/hakoniwa-core/tests/fixtures/cgi/$c.json
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
    "P": ("Plains", 0),
    "N": ("Mountain", 10),
}

MAP_STADIUM = [
    "............",
    "............",
    "...TTT......",
    "..TTKT......",
    "...TTT......",
    "....P.......",
    "...N........",
    "............",
    "............",
    "............",
    "............",
    "............",
]
MAP_PLAIN = [r.replace("K", "T") for r in MAP_STADIUM]


def build(name, turn, teams, maps):
    f = Fixture(name)
    f.turn(turn)
    for island_id in (3, 1, 2):
        f.grid(island_id, maps[island_id], LEGEND)
        f.main(island_id, eisei4=teams[island_id], money=500000, mountain=10)
    f.save()


# ターン 141 (シード)。勝ち点は 島 3: 9、島 1: 9 (段階 0 なので進めない)、島 2: 12 (段階 4)。
# 並べ替えで島 2 が先頭、島 3 と 島 1 は同点で元の順。島 3 の攻撃は "020" (そのまま書き戻す)
build("phase6-cup-41", 140, {
    3: "020,20,20,3,0,1,3,0,1,0,5",
    1: "30,30,30,3,0,1,3,0,1,0,0",
    2: "40,40,40,4,0,0,4,0,0,1,4",
}, {3: MAP_STADIUM, 1: MAP_STADIUM, 2: MAP_STADIUM})

# ターン 141、スタジアムのある島が無い (進出島は空)
build("phase6-cup-41-none", 140, {
    3: "20,20,20,3,0,1,3,0,1,0,5",
    1: "30,30,30,3,0,1,3,0,1,0,0",
    2: "40,40,40,4,0,0,4,0,0,1,4",
}, {3: MAP_PLAIN, 1: MAP_PLAIN, 2: MAP_PLAIN})

# ターン 200 (開催)。スタジアムのある島 2 つ (参加数は 2 − 1 = 1 と記録される)
build("phase6-cup-00", 199, {
    3: "20,20,20,3,0,1,3,0,1,0,12",
    1: "30,30,30,3,0,1,3,0,1,0,9",
    2: "40,40,40,4,0,0,4,0,0,1,4",
}, {3: MAP_STADIUM, 1: MAP_PLAIN, 2: MAP_STADIUM})

# ターン 200、スタジアムのある島が無い (参加数 −1)
build("phase6-cup-00-none", 199, {
    3: "20,20,20,3,0,1,3,0,1,0,12",
    1: "30,30,30,3,0,1,3,0,1,0,9",
    2: "40,40,40,4,0,0,4,0,0,1,4",
}, {3: MAP_PLAIN, 1: MAP_PLAIN, 2: MAP_PLAIN})
