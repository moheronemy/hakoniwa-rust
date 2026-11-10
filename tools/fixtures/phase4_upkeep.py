#!/usr/bin/env python3
"""phase4-upkeep: doIslandProcess の人工衛星・宇宙ステーション・天空城の維持の突き合わせ用データ。

rand を 0.75 / 0.96875 に固定すると、ほかの段階 (災害・暴動・怪獣・移民) は Perl 版でも
何も起きない。食料は減らさない (食料不足のときの宇宙ステーションの処理は別の段階)。

    python3 -I tools/fixtures/phase4_upkeep.py
    RANDS="75 96875" tools/perl-harness/run-harness.sh phase4-upkeep \\
        estimate,income,commands,eachhex,process,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture, monster  # noqa: E402

LEGEND = {
    ".": ("Sea", 0),
    "p": ("Plains", 0),
    "B": ("Base", 200),
    "r": ("Monument", 17),  # ロケット
    "h": ("House", 11),  # 天空城
    "E": ("EneAt", 900),  # 原子力発電所
    "1": ("Monster", monster(1, 1)),  # 体力 1 (イレギュラーで倒れる)
    "9": ("Monster", monster(2, 9)),  # 体力 9 (倒れない)
}

f = Fixture("phase4-upkeep")
# 島 1: 衛星 1〜5 (1 のものは崩壊)、イレギュラーが 2 体を攻撃、ロケットがあり宇宙ステーションは耐久 0 で崩壊
f.grid(1, [
    "............",
    ".1..9.......",
    "............",
    "...pppppp...",
    "...pBBBBp...",
    "...pBBBBp...",
    "...pBBBrp...",
    "...pppppp...",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(1, money=500000, food=90000, eis1=1, eis2=5, eis3=1, eis4=3, eis5=1, eis6=50,
       eis7=500 * 100 + 0)
# msexe (eisei5 の 6 番目) で rena を上げ、ダメージ int(rena / 1000) を 3 にする
f.main(1, eisei5="0,0,0,0,0,1700,0")
# 島 2: イレギュラー (eis6 = 5) が 1 体を攻撃して 0 未満になり崩壊、ロケットが無く宇宙ステーションの
# 人がいなくなる。天空城が電力の余りで怪獣 2 体を消し飛ばす
f.grid(2, [
    "............",
    ".9..1.......",
    "............",
    "...pppppp...",
    "...phpEpp...",
    "...pppppp...",
    "............",
    "............",
    "......9.....",
    "............",
    "............",
    "............",
], LEGEND)
f.main(2, money=300000, food=90000, eis1=0, eis2=0, eis3=0, eis4=0, eis5=0, eis6=5,
       eis7=300 * 100 + 50)
f.main(2, eisei5="0,0,0,0,0,2500,0")
# 島 3: 宇宙ステーションの人口が多く (ロケット 1 では足りない)、天空城はあるが電力が無い
f.grid(3, [
    "............",
    ".9..........",
    "............",
    "...pppppp...",
    "...phpprp...",
    "...pppppp...",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(3, money=800000, food=90000, eis1=7, eis2=0, eis3=0, eis4=0, eis5=0, eis6=0,
       eis7=20000 * 100 + 40)
f.save()

# phase4-upkeep-2: ロケットが足りて宇宙ステーションが資金を払い、そのまま続く
f = Fixture("phase4-upkeep-2")
for island_id in (1, 2, 3):
    f.grid(island_id, [
        "............",
        "............",
        "............",
        "...pppppp...",
        "...pprppp...",
        "...pppppp...",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
    ], LEGEND)
    f.main(island_id, money=400000, food=90000,
           **{f"eis{i}": 0 for i in range(1, 7)}, eis7=(1000 * island_id) * 100 + 30)
f.save()
