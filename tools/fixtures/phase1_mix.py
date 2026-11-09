#!/usr/bin/env python3
"""phase1-mix: estimate / income / doCommand (資金繰り・放棄) の突き合わせ用データ。

島 1 と 2 にほぼすべての地形と特殊な記念碑・大学・家・電車の値を置き、
estimate が読む複合値もいくつか設定する。計画は、移植済みの処理 (費用不足で
飛ばされる計画、資金繰り、放棄) しか通らないように選んである。

    python3 -I tools/fixtures/phase1_mix.py
    tools/perl-harness/run-phase1.sh
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture, monster  # noqa: E402

ISLAND1 = [
    ("Town", 120), ("Procity", 50), ("Onsen", 30), ("Shuto", 200), ("Minato", 40),
    ("Farm", 30), ("Foodim", 100), ("Foodim", 600), ("Foodka", 2), ("Farmchi", 250),
    ("Farmpic", 170), ("Farmcow", 99), ("Factory", 40), ("HTFactory", 60), ("Park", 20),
    ("SHTF", 30), ("OWNF", 1234), ("Mountain", 25), ("Gold", 10), ("Forest", 77),
    ("Newtown", 150), ("Bigtown", 333), ("Bettown", 500), ("Skycity", 600), ("Rizort", 80),
    ("Kajino", 90), ("BigRizort", 70), ("Base", 35), ("Defence", 0), ("Haribote", 0),
    ("Mine", 3), ("Kyujo", 0), ("Kyujokai", 0), ("Zoo", 0), ("Seki", 0),
    ("RottenSea", 5), ("RottenSea", 30), ("Sunahama", 0), ("House", 3), ("Yakusho", 0),
    ("Kura", 1234), ("Kura", 99), ("Kuraf", 10), ("Taishi", 2), ("Taishi", 99),
    ("Train", 5), ("Train", 12), ("Train", 25), ("Monument", 26), ("Monument", 27),
    ("Monument", 73), ("Monument", 86), ("Monument", 87), ("Monument", 17), ("Monument", 93),
    ("College", 77), ("College", 0), ("College", 1), ("College", 2), ("College", 3),
    ("College", 5), ("College", 6), ("College", 7), ("College", 8), ("College", 95),
    ("Plains2", 0), ("Waste", 0), ("Plains", 0), ("Monster", monster(11, 3)),
    ("Monster", monster(21, 2)), ("Monster", monster(23, 9)), ("EneAt", 300), ("EneBo", 150),
    ("EneFw", 200), ("EneCs", 400), ("EneWt", 100), ("EneSo", 120), ("EneWd", 90),
    ("Conden", 500), ("Conden3", 800), ("Conden4", 99),
    # 海のもの
    ("Oil", 0), ("Sbase", 20), ("Fune", 1), ("Fune", 5), ("Fune", 3), ("Nursery", 12),
    ("Umiamu", 44), ("Seacity", 66), ("Frocity", 77), ("Umicity", 300), ("Umishuto", 55),
    ("Seatown", 400), ("Ice", 0),
]

ISLAND2 = [
    ("Town", 10), ("House", 0), ("Monument", 74), ("Monument", 75), ("Monument", 76),
    ("Monument", 77), ("Monument", 78), ("Monument", 79), ("Monument", 84), ("Monument", 96),
    ("Monument", 97), ("Monument", 98), ("Monument", 99), ("Monument", 100), ("Monument", 101),
    ("Monument", 26), ("Monument", 27), ("Monument", 86), ("Monument", 87), ("Monument", 93),
    ("Shuto", 30), ("College", 4), ("College", 96), ("College", 97), ("College", 98),
    ("College", 99), ("College", 78), ("College", 79), ("College", 80),
    ("Monster", monster(28, 1)), ("Monster", monster(30, 4)), ("Monster", monster(13, 7)),
    ("Conden", 100), ("Conden2", 3000), ("Conden3", 50), ("Conden4", 99), ("EneAt", 4000),
    ("EneFw", 100), ("Oil", 0), ("Gold", 3), ("Train", 19), ("Train", 29),
    ("Kyujokai", 0), ("Zoo", 0),
]



f = Fixture("phase1-mix")
f.map(1, ISLAND1, fill=("Sea", 1))
f.map(2, ISLAND2, fill=("Sea", 1))
# income の 3 つの分岐を通るように:
# 島 1 は農業だけで手一杯、島 2 はハイテク企業・改で働き口が足りる (補助金が増える)、
# 島 3 (元の地図のまま) はミサイル基地の電力消費で電力不足になる
f.cells(2, {(11, 11): ("SHTF", 30)})
f.cells(3, {(0, 0): ("Base", 4000)})

f.main(1, money=5000000, food=123456, pts=60000, eis1=3, eis2=7,
       eisei4="5,6,7,2,1,0,4,3,2,1,0")
f.main(2, money=9000000, pts=70000, eis7=1234, eisei2=-5, eisei5="10,20,30,40,5,6,7")
f.ips(1, etc5=",".join(str(i) for i in [1, 2, 30, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] + [1] * 18),
      etc8="1,2,3,4,5,6,7")
f.ips(2, etc6=",".join(str(i % 4) for i in range(31)), etc8="0,1,0,0,0,0,0")
f.auction(1, auc0="1,2,3,4,5", auc6="1,0,0", auc9="1,2,30000,4,5")
f.owner(1, rena=300, totoyoso2=555)

# 計画: 島 3 は資金・食料の不足で飛ばされる計画のあとに資金繰り、
# 島 1 は放棄、島 2 は連続資金繰りがあと 1 回で自動放棄
COM = {"Monument": 18, "Givefood": 100, "Zoo": 121, "Giveup": 46}
f.commands(3, [(COM["Monument"], 0, 3, 3, 1), (COM["Givefood"], 0, 0, 0, 0), (COM["Zoo"], 0, 4, 4, 0)])
f.commands(1, [(COM["Giveup"], 0, 0, 0, 0)])
f.main(2, absent=23)
f.save()
