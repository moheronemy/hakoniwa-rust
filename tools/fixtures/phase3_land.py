#!/usr/bin/env python3
"""phase3-land: doCommand の整地・埋め立て・港町・造船・関所・掘削・温泉・伐採・採掘場の突き合わせ用データ。

島 1 は整地・地ならし・埋め立て・港町開発・関所建設、島 2 は掘削 (油田探しと地形ごとの掘削)、
島 3 は温泉掘削・採掘場整備 (繰り返し)・伐採・造船。失敗する計画 (ターンを使わない) は
成功する計画の前にまとめて置き、`commands` の 1 段階で 1 つずつ成功する計画が進むようにしてある。
陸地に囲まれた浅瀬 (周りの海が 4 以下) と島の縁の浅瀬の両方を予定地にする。

    python3 -I tools/fixtures/phase3_land.py
    RANDS="0 50 03125 0078125" tools/perl-harness/run-harness.sh phase3-land \
        "estimate,income$(printf ',commands%.0s' $(seq 13)),estimate"

rand 0 では埋蔵金・金塊・卵がすべて出る。0.5 では温泉が見つかる/油田が見つからない分岐、
1/32 では温泉掘削の卵、1/128 では温泉掘削の卵と埋蔵金・採掘場の金塊を通る。
温泉掘削の古代遺跡は random(1000) を 2 回続けて引いて 1 回目が 50 以上・2 回目が 50 未満の
ときだけなので、rand を固定したこの突き合わせでは通らない。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, Fixture  # noqa: E402

LEGEND = {
    ".": ("Sea", 0),
    "s": ("Sea", 1),
    "P": ("Plains", 0),
    "p": ("Plains2", 0),
    "W": ("Waste", 0),
    "T": ("Town", 30),
    "F": ("Forest", 10),
    "M": ("Mountain", 0),
    "m": ("Mountain", 50),
    "G": ("Gold", 190),
    "g": ("Gold", 3),
    "I": ("Ice", 0),
    "O": ("Oil", 0),
    "H": ("Minato", 10),
    "e": ("Monument", 80),
    "j": ("Monument", 75),
    "S": ("Monument", 26),
    "J": ("Monument", 27),
    "o": ("Onsen", 20),
}
SEA = ["............"] * 12

f = Fixture("phase3-land")
f.grid(1, [
    "............",
    ".s.ssss.....",
    ".sPPWpTTs...",
    ".sTTPTTTs...",
    ".sejTTTOs...",
    ".sTTsTsTO...",
    ".sT....TO...",
    ".sTTTTTTs...",
    "..ssssss....",
] + SEA[:3], LEGEND)
f.grid(2, [
    "............",
    "..ssssss....",
    ".sMMggIIs...",
    ".sTTTTSJs...",
    ".sTTOTTTs...",
    "..ssssss....",
] + SEA[:6], LEGEND)
f.grid(3, [
    "............",
    "..ssssss....",
    ".sMmMMFFs...",
    ".sGTSJoFs...",
    ".sTTHTTHs...",
    "..s.sOss....",
] + SEA[:6], LEGEND)

for i in (1, 2, 3):
    f.main(i, money=3000000, food=50000)


def c(name, x, y, arg=0, target=0):
    return (COMMAND[name], target, x, y, arg)


# 島 1: 各行が commands の 1 段階 (最後の計画だけが 1 を返す)
f.commands(1, [
    c("Prepare", 0, 0), c("Prepare2", 2, 2), c("Prepare2", 2, 4), c("Prepare", 3, 4),
    c("Reclaim", 6, 2), c("Reclaim", 10, 10), c("Reclaim3", 10, 10), c("Reclaim2", 10, 10),
    c("Reclaim", 4, 5),
    c("Reclaim", 1, 3),
    c("Reclaim", 4, 2),
    c("Reclaim3", 8, 2),
    c("Reclaim3", 7, 4),
    c("Reclaim", 8, 5),
    c("Minato", 6, 2), c("Minato", 10, 10), c("Minato", 6, 5),
    c("Minato", 1, 5),
    c("Minato", 8, 6),
    c("Seki", 6, 2), c("Seki", 11, 11), c("Seki", 4, 6),
    c("Seki", 1, 6),
])
# 島 2: 掘削。最後は資金を超える投資額 (資金がすべて使われる)
f.commands(2, [
    c("Destroy", 4, 4), c("Destroy", 10, 10),
    c("Destroy", 10, 9, 75),
    c("Destroy", 2, 2),
    c("Destroy3", 3, 2),
    c("Destroy", 4, 2),
    c("Destroy3", 5, 2),
    c("Destroy", 6, 2),
    c("Destroy3", 7, 2),
    c("Destroy3", 2, 3),
    c("Destroy", 1, 2),
    c("Destroy", 3, 3),
    c("Destroy", 10, 8, 99999),
    c("Destroy", 9, 9),
])
# 島 3: 温泉・採掘場 (3 回繰り返し)・伐採・造船
f.commands(3, [
    c("Onsen", 3, 3), c("Onsen", 3, 2),
    c("Onsen", 2, 2),
    c("Onsen", 4, 2, 81),
    c("Onsen", 5, 2, 400),
    c("SellTree", 10, 10), c("SellTree", 6, 2), c("SellTree", 7, 2), c("Mountain", 10, 10),
    c("Mountain", 3, 2, 3),
    c("Mountain", 2, 3),
    c("Fune", 3, 3), c("Fune", 10, 10), c("Fune", 5, 5), c("Fune", 8, 3, 77),
    c("Fune", 8, 4),
    c("Fune", 8, 5, 3),
    c("Fune", 4, 5, 50),
    c("Fune", 7, 5, 11),
])
f.save()
