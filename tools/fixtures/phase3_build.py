#!/usr/bin/env python3
"""phase3-build*: doCommand の建設系 (植林〜防衛施設) の突き合わせ用データ。

    python3 -I tools/fixtures/phase3_build.py
    STEPS=estimate,income,$(printf 'commands,%.0s' $(seq 34))estimate
    RANDS="0 03125 50 96875" tools/perl-harness/run-harness.sh phase3-build-1 $STEPS
    RANDS="0 03125 50 96875" tools/perl-harness/run-harness.sh phase3-build-2 $STEPS
    RANDS="0 03125" tools/perl-harness/run-harness.sh phase3-build-zoo $STEPS
    RANDS="0 03125" tools/perl-harness/run-harness.sh phase3-build-zoo2 commands,commands,commands

島 1 と 2 は同じ地図 (人口が多く電力が足りている、文部科学省・首都がある)、
島 3 は発電所が無く資金も少ない。計画は 0 を返すもの (失敗・ターンを使わないもの) を
間に挟みながら並べてあり、commands 1 回で 1 ターン分 (1 を返すまで) 進む。

phase3-build-zoo は動物園の新設 (入荷ループ) を通す。入荷ループは random(5) が 0 に
なるまで回るので、rand 0.5 では Perl 版が止まらない。rand 0 と 1/32 だけで動かす。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, SIZE, Fixture  # noqa: E402


def base_map(cells, fill=("Plains", 0)):
    """外周を海、内側を fill にして cells {(x, y): (地形, 値)} を置いた地図 (行優先)"""
    flat = []
    for y in range(SIZE):
        for x in range(SIZE):
            if (x, y) in cells:
                flat.append(cells[(x, y)])
            elif x in (0, SIZE - 1) or y in (0, SIZE - 1):
                flat.append(("Sea", 0))
            else:
                flat.append(fill)
    return flat


RICH = {
    (1, 1): ("Town", 200), (2, 1): ("Town", 200), (3, 1): ("Town", 200),
    (5, 2): ("Shuto", 100),
    (6, 2): ("College", 77), (6, 3): ("College", 80), (4, 2): ("College", 79),
    (10, 1): ("EneAt", 1490), (10, 2): ("EneSo", 1000), (10, 3): ("EneAt", 1000),
    (1, 3): ("College", 4), (2, 3): ("College", 98), (3, 3): ("College", 96),
    (4, 3): ("College", 97), (1, 4): ("College", 6), (2, 4): ("College", 95),
    (7, 3): ("Farmchi", 50), (10, 4): ("Kura", 100),
    (2, 5): ("Town", 150), (7, 5): ("Park", 90), (8, 5): ("Ice", 0), (9, 5): ("Zoo", 10),
    (7, 6): ("Train", 0), (8, 6): ("Train", 0), (9, 6): ("Train", 0),
    (10, 6): ("Sea", 0), (11, 6): ("Zoo", 10),
    (2, 7): ("Town", 150), (3, 7): ("Kura", 195), (5, 7): ("Kuraf", 255),
    (6, 7): ("Kuraf", 2395), (7, 7): ("Kura", 150), (8, 7): ("Kuraf", 305),
    (9, 7): ("Nursery", 98), (0, 3): ("Sea", 1),
    (5, 8): ("Farm", 49), (7, 8): ("Umiamu", 990), (8, 8): ("Monument", 10),
    (1, 9): ("Mountain", 0), (4, 9): ("Foodim", 100), (10, 9): ("Forest", 5),
    (2, 10): ("Foodim", 495), (4, 10): ("Factory", 95), (6, 10): ("Defence", 0),
    (9, 10): ("Forest", 5),
    (1, 2): ("Base", 0),
    # 上限に近い発電所 (と、その条件になる周りの地形)
    (10, 5): ("EneFw", 480), (8, 1): ("Mountain", 0), (9, 1): ("EneWt", 240),
    (8, 2): ("EneWd", 140), (7, 1): ("Foodim", 30), (7, 2): ("EneBo", 1990),
    (9, 2): ("EneCs", 3900),
}

POOR = {
    (1, 1): ("Town", 100), (2, 1): ("Town", 100),
    (2, 2): ("Forest", 10), (3, 3): ("College", 6), (9, 9): ("Zoo", 10),
}


def etc5(costseisaku_each, s10=20):
    """政策 (etc5)。s0 = 1 で値引きあり、s1..s30 は costseisaku_each、s10 は大学の種類の数"""
    s = [1] + [costseisaku_each] * 30
    s[10] = s10
    s[12] = 0
    return ",".join(str(v) for v in s)


def zoo(**counts):
    z = [0] * 31
    for k, v in counts.items():
        z[int(k[1:])] = v
    return ",".join(str(v) for v in z)


def c(name, x, y, arg=0, target=0):
    return (COMMAND[name], target, x, y, arg)


def setup(name, rich2=None, rich1=None):
    f = Fixture(name)
    f.map(1, base_map(rich1 if rich1 is not None else RICH))
    f.map(2, base_map(rich2 if rich2 is not None else RICH))
    f.map(3, base_map(POOR))
    for i in (1, 2):
        f.main(i, money=6000000, food=900000, eis7=1, absent=0)
    f.main(3, money=120000, food=30000, eis7=0, absent=0)
    # 島 1: costseisaku = 29 * 1 + 20 = 49 (> 35)。島 2: 29 * 4 + 20 = 136 (> 110)
    f.ips(1, etc5=etc5(1), etc6=zoo(z5=2, z3=1, z30=1), etc9="0,0,0,3,0,3,0")
    f.ips(2, etc5=etc5(4), etc9="0,0,0,2,0,3,0")
    f.ips(3, etc5=etc5(0, 0))
    return f


# ---------------------------------------------------------------- phase3-build-1
f = setup("phase3-build-1")
f.commands(1, [
    c("Plant", 3, 5),
    c("Plant", 2, 2),
    c("Base", 1, 5),
    c("Haribote", 2, 5),
    c("Monbuy", 4, 5, 2),              # rand 31/32 で種類 12 -> 農場整備が先頭に入る
    c("Monbuyt", 5, 5),
    c("Zoo", 9, 5, 5),                 # 隣の平地に逃がす (0)
    c("Zoo", 11, 6, 3),                # 周りが海 -> 町に現れる (0)
    c("Zoo", 9, 5, 40),                # 30 番はいない (0)
    c("Park", 6, 5, 1),
    c("Park", 7, 5, 3),                # 2 回戻る
    c("Park", 8, 5),
    c("Zoo", 1, 6),                    # 動物園がある島の新設 (入荷しない)
    c("Mine", 2, 6, 0),
    c("Mine", 3, 6, 12),
    c("Conden", 4, 6, 0),
    c("Conden", 5, 6, 5),
    c("Train", 6, 6, 3),
    c("Train", 7, 6, 1),
    c("Train", 8, 6, 2),
    c("Train", 9, 6, 15),
    c("Train", 6, 6, 1),               # 電車 3 の上 -> 不適当 (0)
    c("Plant", 1, 2),                  # 基地の上 -> 不適当 (0)
    c("Monument", 7, 10, 5),
    c("Monument", 8, 10, 92),
    c("Monument", 3, 9, 69),
    c("Monument", 2, 9, 75),
    c("Monument", 8, 8, 5, target=99),  # 目標が無い (0)
    c("Monument", 8, 8, 5, target=3),   # 目標の人口が少ない (0)
    c("Monument", 8, 8, 5, target=1),   # 発射 (自分の島を攻撃、資金 0)
])
f.commands(2, [
    c("Yakusho", 6, 1),
    c("Yakusho", 6, 2),
    c("Yakusho", 6, 2),
    c("Yakusho", 6, 2),
    c("Yakusho", 6, 2),
    c("Yakusho", 4, 2),
    c("Yakusho", 6, 3),
    c("Yakusho", 2, 2),                # 首都が隣に無い (0)
    c("College", 1, 3),                # 4 -> 96 (0)
    c("College", 2, 3),                # 98 -> 97 (0)
    c("College", 3, 3),                # 96 -> 4 (0)
    c("College", 4, 3),                # 97 -> 98 (0)
    c("College", 2, 4),                # 95 -> 6 (0)
    c("College", 1, 4, 3),             # 6 -> 95、文部科学省で 2 に
    c("College", 3, 4, 4),             # 新設 -> 3 (co4 があるので eisei5 はそのまま)
    c("College", 7, 4, 9),             # 新設 (数量が多すぎる)
    c("Farmcpc", 7, 3, 2),             # 売る (0)
    c("Farmcpc", 8, 3, 2),
    c("Farmcpc", 9, 3, 3),
    c("Farmcpc", 9, 4, 7),
    c("Kura", 1, 7, 0),
    c("Kura", 2, 7, 5),
    c("Kura", 3, 7, 7),
    c("Kura2", 7, 7, 20),              # (0)
    c("Kura2", 8, 7, 0),               # (0)
    c("Kura2", 8, 7, 15),              # (0)
    c("Kura2", 10, 4, 3),              # (0)
    c("Kura2", 1, 1, 1),               # 町 -> 不適当 (0)
    c("Kura2", 5, 5, 1),               # 平地 -> 不適当 (0)
    c("Yoyaku", 4, 8),                 # (0)
    c("Yoyaku", 5, 9),                 # (0)
    c("Kuraf", 4, 7, 0),
    c("Kuraf", 5, 7, 12),
    c("Kuraf", 6, 7, 9),
    c("EneNF", 8, 9),                  # 失敗 (島 2 は magica != magicl) -> 広域被害 (0)
])
f.commands(3, [
    c("Base", 3, 2),
    c("Park", 3, 2),
    c("Zoo", 3, 2),
    c("Zoo", 9, 9, 1),
    c("Train", 3, 2),
    c("Kyujo", 3, 2),
    c("Rizort", 3, 2),
    c("Umiamu", 0, 4),
    c("Dbase", 3, 2),
    c("Plant", 2, 2),                  # 森 -> 不適当
    c("Yakusho", 3, 2),                # 首都が無い
    c("College", 3, 3),                # 資金不足
    c("EneCs", 3, 2),                  # 衛星が無い
    c("Conden", 4, 4, 2),              # 資金で 1 に
    c("Kura", 5, 5, 9),                # 資金で減る
    c("Kuraf", 6, 6, 5),               # 食料で減る
    c("Mine", 7, 7, 3),
    c("EneNF", 5, 5),                  # 失敗 -> 広域被害 (0)
    c("Newtown", 7, 2),
])
f.save()

# ---------------------------------------------------------------- phase3-build-2
rich2 = dict(RICH)
for xy in ((1, 3), (2, 3), (3, 3), (4, 3)):
    rich2[xy] = ("Plains", 0)          # co4 = 0 にする (大学 4 で eisei5 を書く)
# 島 1 は魔法の石 (記念碑 75 と 79) で etc9 の magica = magicl = 1 になり、核融合が成功する
rich1 = dict(RICH)
rich1[(4, 1)] = ("Monument", 75)
rich1[(5, 1)] = ("Monument", 79)
f = setup("phase3-build-2", rich2, rich1)
f.commands(1, [
    c("Nursery", 9, 7, 1),
    c("Nursery", 0, 3, 2),             # 浅瀬 -> 養殖場、1 回戻る
    c("Nursery", 10, 7),               # 平地 -> 不適当 (0)
    c("Nursery", 0, 4),                # 海 -> 不適当 (0)
    c("Umiamu", 0, 4),
    c("Umiamu", 7, 8, 2),
    c("Umiamu", 9, 8),                 # 平地 -> 不適当 (0)
    c("Kyujo", 1, 8),
    c("Newtown", 2, 8),
    c("Rizort", 3, 8),
    c("Farm", 5, 8, 1),
    c("Farm", 6, 8, 3),
    c("EneAt", 10, 1),
    c("EneAt", 6, 6),
    c("EneFw", 5, 9),                  # 海が無い (0)
    c("EneWt", 5, 9),                  # 山が無い (0)
    c("EneBo", 5, 9),
    c("EneWt", 2, 9),
    c("EneWt", 2, 9),
    c("EneWd", 3, 9),
    c("EneWd", 3, 9),
    c("EneWd", 10, 10),                # 平地が無い (0)
    c("EneBo", 10, 10),                # 食物研究所が無い (0)
    c("EneFw", 10, 8),
    c("EneFw", 10, 8),
    c("EneCs", 6, 9),
    c("EneCs", 6, 9),
    c("EneSo", 7, 9),
    c("EneSo", 10, 2),
    c("EneNF", 8, 9),                  # 成功
    c("EneBo", 5, 9),
    c("EneFw", 10, 5),
    c("EneWt", 9, 1),
    c("EneWd", 8, 2),
    c("EneBo", 7, 2),
    c("EneCs", 9, 2),
    c("Yakusho", 6, 2),                # costseisaku 49: 77 -> 78
    c("Yakusho", 6, 2),                # 78 -> 77
])
f.commands(2, [
    c("Foodim", 1, 10),
    c("Foodim", 2, 10),
    c("Factory", 3, 10, 2),
    c("Factory", 4, 10),
    c("Dbase", 5, 10),
    c("Dbase", 6, 10),
    c("College", 3, 4, 4),             # co4 = 0 -> eisei5 を書く
    c("College", 7, 4, 0),
    c("Farm", 1, 3, 2),
    c("Park", 7, 5, 0),
    c("Zoo", 9, 5, 3),                 # 3 番は 0 匹 (0)
    c("College", 9, 8, 6),             # 数量 6 は文部科学省で選べない (s10b = 5)
    c("Monument", 2, 2, 70),           # 70 番は無い -> 0
    c("Conden", 8, 4, 2),
    c("Mine", 9, 4, 10),
    c("Farmcpc", 6, 4, 4),             # 4 -> 1
    c("Monument", 8, 8, 1, target=1),  # 発射
    c("Plant", 4, 4),                  # 資金不足
])
f.commands(3, [
    c("Haribote", 3, 2),
    c("Mine", 4, 2, 1),
    c("Farmcpc", 5, 2, 3),
    c("Monbuy", 6, 2, 3),
    c("Monbuyt", 7, 2),
])
f.save()

# ---------------------------------------------------------------- phase3-build-zoo
POWERED = dict(POOR)
POWERED[(10, 1)] = ("EneAt", 1490)
POWERED[(10, 2)] = ("EneSo", 1000)
nozoo = dict(POWERED)
del nozoo[(9, 9)]
f = Fixture("phase3-build-zoo")
f.map(1, base_map(nozoo))
f.map(2, base_map(nozoo))
f.map(3, base_map(POWERED))
for i in (1, 2, 3):
    f.main(i, money=3000000, food=100000, absent=0)
f.main(2, eis7=0)
f.ips(1, etc5=etc5(1), etc6=zoo(z1=1, z4=2))
f.ips(2, etc5=etc5(1))
f.ips(3, etc5=etc5(2), etc6=zoo(z4=2))
# 動物園が無い島の新設 (入荷ループ)
f.commands(1, [c("Zoo", 4, 4), c("Zoo", 4, 4)])
# 衛星が無い (0)、核融合は文部科学省が無いので失敗して広域被害 (0)
f.commands(2, [c("EneCs", 4, 4), c("EneNF", 8, 8), c("Zoo", 3, 6)])
# 動物園の上: 4 番を逃がす、7 番はいない (0)、動物園がある島の新設
f.commands(3, [c("Zoo", 9, 9, 4), c("Zoo", 9, 9, 7), c("Zoo", 5, 5)])
f.save()

# ---------------------------------------------------------------- phase3-build-zoo2
# estimate を通さずに計画だけを実行する (estimate は etc6 を書き直すので、壊れた etc6 が
# doCommand まで届かない)。etc6 のマッチに失敗すると、直前に成功したマッチ
# (費用の計算での etc5 のマッチ) の $1.. が動物の数になる
f = Fixture("phase3-build-zoo2")
f.map(1, base_map(nozoo))
f.map(2, base_map(nozoo))
f.map(3, base_map(POWERED))
for i in (1, 2, 3):
    f.main(i, money=3000000, food=100000, absent=0)
f.ips(1, etc5=etc5(1), etc6="1,2,3")
# etc5 も壊れているときは $1.. が未定義になり、etc6 に空欄が残る。estimate が毎ターン
# etc6 を数値で書き直すので実際のターンでは起きない。移植版は 0 として扱うので試さない
f.ips(2, etc5="bad", etc6=zoo(z2=1))
f.ips(3, etc5=etc5(2), etc6="x")
f.commands(1, [c("Zoo", 4, 4)])
f.commands(2, [c("Zoo", 4, 4)])
f.commands(3, [c("Zoo", 9, 9, 2), c("Zoo", 9, 9, 3), c("Zoo", 5, 5)])
f.save()
