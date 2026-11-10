#!/usr/bin/env python3
"""phase3-ops-*: doCommand の人工衛星・ハコオク出品・エサ・輸出・援助・電力援助・誘致活動の
突き合わせ用データ。

- phase3-ops-eisei: 人工衛星打ち上げ (数量ごと、ロケット・技術・資金の不足、失敗)、
  人工衛星修復 (宇宙ステーションの上限)、誘致活動 (繰り返し)
- phase3-ops-att:   衛星破壊砲・衛星レーザー (イレギュラー / 軍事衛星、消耗と崩壊、
  援助射撃の許可、目標なし、人口不足)、電力不足、出品枠 3 だけ空いているハコオク
- phase3-ops-aid:   ハコオク出品 (出品権利なし、枠 1・2、枠なし、マッチ失敗)、エサ、
  食料輸出、資金・食料援助 (存在しない島 = 先頭の島)、電力援助 (コンデンサへの充電)、
  衛星レーザー (目標なし、目標の島の人口不足)
- phase3-ops-edge:  技術・宇宙ステーション・衛星の値がちょうど境目のとき
- phase3-ops-rates: 衛星破壊砲の命中率 (rand を命中率ちょうどの値に固定する)
- phase3-ops-lzr:   衛星レーザーが当たる地形の種類、衛星の値が 1 のとき

期待値の作り方 (STEPS は estimate,income,commands × N,estimate):

    python3 -I tools/fixtures/phase3_ops.py
    RANDS="0 50 96875 03125" tools/perl-harness/run-harness.sh phase3-ops-eisei $STEPS
    (phase3-ops-att, -edge も同じ。N = 12、-lzr は N = 17)
    RANDS="0 50 96875 03125 40625" tools/perl-harness/run-harness.sh phase3-ops-aid $STEPS
    RANDS="0 50 96875 03125 203125 3046875 40625 6015625 703125 8046875 90625 9921875" \\
        tools/perl-harness/run-harness.sh phase3-ops-rates $STEPS   (N = 8)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, Fixture, monster  # noqa: E402

C = COMMAND


def base_map(f, island_id, extra, towns=6, plants=2):
    """町 (人口) と原子力発電所 (電力) を置き、extra の座標を上書きする"""
    cells = {}
    for i in range(towns):
        cells[(i, 11)] = ("Town", 200)
    for i in range(plants):
        cells[(i, 10)] = ("EneAt", 4000)
    cells.update(extra)
    f.map(island_id, [])
    f.cells(island_id, cells)


def rockets(n):
    """ロケット (記念碑 17) を n 個"""
    return {(i, 9): ("Monument", 17) for i in range(n)}


def auction_lots(f, lots):
    lines = (f.dir / "auction.dat").read_bytes().split(b"\n")
    lines[0:3] = [s.encode() for s in lots]
    (f.dir / "auction.dat").write_bytes(b"\n".join(lines))


# ---- 人工衛星打ち上げ・修復・誘致活動 --------------------------------------------
f = Fixture("phase3-ops-eisei")
auction_lots(f, ["1,0,0,0,0", "2,0,0,0,0", "3,0,0,0,0"])
# 島 3: 技術もロケットも十分。数量ごとに打ち上げる (rand 0.96875 だと 99 と 6 は失敗)
base_map(f, 3, rockets(10))
f.main(3, money=9000000, food=100000, eis7=0)
f.main(3, eisei5="0,0,0,0,0,6000,0")  # 軍事技術 (rena) は estimate で msexe から
f.commands(3, [
    (C["Eisei"], 0, 0, 0, 99), (C["Eiseimente"], 0, 0, 0, 99),
    (C["Eisei"], 0, 0, 0, 6), (C["Eisei"], 0, 0, 0, 5),
    (C["Eisei"], 0, 0, 0, 4), (C["Eisei"], 0, 0, 0, 3), (C["Eisei"], 0, 0, 0, 2),
    (C["Eisei"], 0, 0, 0, 0), (C["Eisei"], 0, 0, 0, 7),
])
# 島 1: 技術が低いので失敗しやすい打ち上げ、ロケット不足・資金不足、打ち上げと修復
base_map(f, 1, rockets(3))
f.main(1, money=900000, food=100000, eis1=0, eis2=0, eis4=0, eis5=3, eis7=5080)
f.main(1, eisei5="0,0,0,0,0,250,0")
f.commands(1, [
    (C["Eisei"], 0, 0, 0, 3), (C["Eisei"], 0, 0, 0, 4), (C["Eisei"], 0, 0, 0, 5),
    (C["Eisei"], 0, 0, 0, 99), (C["Eisei"], 0, 0, 0, 2), (C["Eisei"], 0, 0, 0, 1),
    (C["Eiseimente"], 0, 0, 0, 0), (C["Eiseimente"], 0, 0, 0, 2),
    (C["Eiseimente"], 0, 0, 0, 4), (C["Eiseimente"], 0, 0, 0, 6),
    (C["Eiseimente"], 0, 0, 0, 99), (C["Eiseimente"], 0, 0, 0, 99),
    (C["Eiseimente"], 0, 0, 0, 5), (C["Eiseimente"], 0, 0, 0, 3),
])
# 島 2: 宇宙ステーションの技術不足、イレギュラーの打ち上げ、誘致活動の繰り返し
base_map(f, 2, rockets(10))
f.main(2, money=9000000, food=100000, eis7=0)
f.main(2, eisei5="0,0,0,0,0,4000,0")
f.commands(2, [
    (C["Eisei"], 0, 0, 0, 99), (C["Eisei"], 0, 0, 0, 6),
    (C["Eiseimente"], 0, 0, 0, 99),
    (C["Propaganda"], 0, 0, 0, 3), (C["Propaganda"], 0, 0, 0, 1),
    (C["Propaganda"], 0, 0, 0, 0),
])
f.save()

# ---- 衛星破壊砲・衛星レーザー -----------------------------------------------------
f = Fixture("phase3-ops-att")
# 枠 1 はマッチに失敗 ($1 は auc6 の 1)、枠 2 は 7、枠 3 が空いている
auction_lots(f, ["29x", "7,0,0,0,0", "29,0,0,0,0"])
TARGET3 = {
    (0, 0): ("Oil", 0), (1, 0): ("Onsen", 30), (2, 0): ("Farm", 10),
    (3, 0): ("Mountain", 0), (4, 0): ("Fune", 1), (5, 0): ("Ice", 0),
    (6, 0): ("Forest", 50), (7, 0): ("Factory", 30), (8, 0): ("Sbase", 20),
    (9, 0): ("Nursery", 10),
}
base_map(f, 3, TARGET3)
# 島 3: イレギュラー 65、軍事衛星 40。目標は島 1
f.main(3, money=9000000, food=100000, eis1=100, eis2=100, eis3=100, eis4=40, eis5=100,
       eis6=65, eis7=1234)
f.ips(3, etc7="2,0,1")
f.auction(3, auc6="1,0,0")
f.commands(3, [
    (C["EiseiAtt"], 99, 0, 0, 1),        # 目標の島が無い
    (C["EiseiAtt"], 2, 0, 0, 1),         # 援助射撃の許可が無い
    (C["EiseiAtt"], 1, 0, 0, 0),         # イレギュラーで気象衛星
    (C["EiseiAtt"], 1, 0, 0, 2),         # 目標に観測衛星が無い
    (C["EiseiLzr"], 1, 0, 0, 0),         # イレギュラーでレーザー (海底都市)
    (C["EiseiAtt"], 1, 0, 0, 6),         # イレギュラーでイレギュラー、崩壊
    (C["EiseiAtt"], 1, 0, 0, 99),        # 軍事衛星で宇宙ステーション
    (C["EiseiLzr"], 1, 2, 0, 0),         # 軍事衛星でレーザー (町)、崩壊
    (C["EiseiAtt"], 1, 0, 0, 4),         # 衛星が無い
    (C["EiseiLzr"], 1, 1, 0, 0),         # 衛星が無い
    (C["Auction"], 0, 6, 0, 20),         # 枠 3 に出品
])
TARGET1 = {
    (0, 0): ("Seacity", 10), (1, 0): ("Fune", 3), (2, 0): ("Town", 100),
    (3, 0): ("Onsen", 10), (4, 0): ("Frocity", 3), (5, 0): ("Gold", 1),
    (6, 0): ("Umiamu", 1), (7, 0): ("Nursery", 1),
}
base_map(f, 1, {**TARGET1, **rockets(1)})
# 島 1: 軍事衛星だけ。目標は島 3
f.main(1, money=9000000, food=100000, eis1=100, eis2=0, eis3=0, eis4=200, eis5=0, eis6=100,
       eis7=5099)
f.ips(1, etc7="2,0,3")
f.auction(1, auc6="1,0,0")
f.commands(1, [
    (C["Eisei"], 0, 0, 0, 1),            # 軍事技術が足りない
    (C["EiseiAtt"], 3, 0, 0, 2), (C["EiseiAtt"], 3, 0, 0, 4), (C["EiseiAtt"], 3, 0, 0, 5),
    (C["EiseiAtt"], 3, 0, 0, 7), (C["EiseiAtt"], 3, 0, 0, 6), (C["EiseiAtt"], 3, 0, 0, 99),
    (C["EiseiLzr"], 2, 0, 0, 0),         # 援助射撃の許可が無い
    (C["EiseiLzr"], 3, 1, 0, 0),         # 温泉
    (C["EiseiLzr"], 3, 3, 0, 0),         # 山 (暖かくなる)
    (C["EiseiLzr"], 3, 6, 0, 0),         # 森 (荒地、記念碑は自分の島に)
    (C["EiseiLzr"], 3, 4, 0, 0),         # 船 (海になる)
    (C["EiseiLzr"], 3, 0, 0, 0),         # 油田 (海になる)
    (C["Auction"], 0, 2, 0, 5),          # 枠が無い
])
# 島 2: 人口が少なく電力も無い。イレギュラーで島 3 を撃つ
base_map(f, 2, {}, towns=1, plants=0)
f.main(2, money=9000000, food=100000, eis6=200)
f.owner(2, rena=30000)
f.ips(2, etc7="2,0,3")
f.commands(2, [
    (C["Eisei"], 0, 0, 0, 1),            # 電力不足
    (C["Eiseimente"], 0, 0, 0, 1),       # 電力不足
    (C["EiseiLzr"], 3, 0, 0, 0),         # 自島の人口が少ない
    (C["EiseiAtt"], 3, 0, 0, 3), (C["EiseiAtt"], 3, 0, 0, 5), (C["EiseiAtt"], 3, 0, 0, 1),
    (C["EiseiAtt"], 3, 0, 0, 99), (C["EiseiAtt"], 3, 0, 0, 2),
])
f.save()

# ---- ハコオク出品・エサ・輸出・援助・電力援助 -----------------------------------------
f = Fixture("phase3-ops-aid")
# 枠 3 はマッチに失敗し、直前に成功した枠 2 の値を使う
auction_lots(f, ["29,0,0,0,0", "29,1,2,3,4", "5x"])
base_map(f, 3, {(0, 0): ("Farm", 20)})
f.main(3, money=9000000, food=3000, eis4=50)
f.auction(3, auc6="1,0,0")
f.ips(3, etc7="2,0,2")
f.commands(3, [
    (C["EiseiLzr"], 99, 0, 0, 0),        # 目標の島が無い
    (C["EiseiLzr"], 2, 0, 0, 0),         # 目標の島の人口が少ない
    (C["Sell"], 0, 0, 0, 0),             # 100 輸出
    (C["Food"], 1, 0, 0, 99),            # 食料が足りるだけ援助
    (C["Sell"], 0, 0, 0, 5),             # 食料が無い
    (C["Money"], 99, 0, 0, 2),           # 存在しない島 = 先頭の島 (自分)
    (C["Auction"], 0, 0, 0, 30),         # 枠 1
    (C["Auction"], 0, 0, 0, 30),         # 出品権利が無い
    (C["EneGive"], 2, 0, 0, 4),          # 島 2 のコンデンサへ少しずつ電力援助
    (C["EneGive"], 2, 0, 0, 12),
    (C["EneGive"], 2, 0, 0, 1),
    (C["Givefood"], 0, 0, 0, 0),         # 食料不足
])
ISLAND1 = {
    (0, 0): ("Monster", monster(3, 5)), (1, 0): ("Monster", monster(5, 12)),
    (2, 0): ("College", 4), (3, 0): ("College", 96), (4, 0): ("College", 5),
    (5, 0): ("College", 97), (6, 0): ("College", 98),
}
base_map(f, 1, ISLAND1)
f.main(1, money=5000, food=500000, eisei5="15,1,2,3,4,5,6")
f.auction(1, auc6="1,0,0")
f.commands(1, [
    (C["Givefood"], 0, 4, 0, 0),         # 地形が違う
    (C["Auction"], 0, 1, 11, 7),         # 枠 2
    (C["Givefood"], 0, 0, 0, 2),         # 怪獣 (体力 5)、繰り返し
    (C["Givefood"], 0, 1, 0, 0),         # 怪獣 (体力 12)
    (C["Givefood"], 0, 3, 0, 1),         # 大学 96 (マスコットの体力は 15 まで)
    (C["Givefood"], 0, 2, 0, 0),         # 大学 4
    (C["Givefood"], 0, 5, 0, 0),         # 大学 97
    (C["Givefood"], 0, 6, 0, 0),         # 大学 98
    (C["Money"], 3, 0, 0, 0),            # 数量 0 は 1
    (C["Money"], 3, 0, 0, 99),           # 資金が足りるだけ援助
    (C["EneGive"], 2, 0, 0, 60),         # たくさん電力援助
])
# 島 2: 人口が少なく発電所も無い (電力の不足分はコンデンサから引かれる)
ISLAND2 = {
    (0, 0): ("Conden", 1500), (1, 0): ("Conden3", 4000), (2, 0): ("Conden2", 3000),
    (3, 0): ("Conden", 0), (4, 0): ("Conden", 0), (5, 0): ("Conden3", 0),
    (6, 0): ("Conden2", 0),
}
base_map(f, 2, ISLAND2, towns=1, plants=0)
f.main(2, money=9000000, food=100000)
f.auction(2, auc6="1,0,0")
f.commands(2, [
    (C["Money"], 3, 0, 0, 1),            # 自島の人口が少ない
    (C["Auction"], 0, 0, 11, 1),         # 枠が無い (枠 3 は枠 2 の値)
    (C["Propaganda"], 0, 0, 0, 2),
])
f.save()

# ---- 境目の値 (技術・宇宙ステーション・衛星の値が 1) ------------------------------
f = Fixture("phase3-ops-edge")
auction_lots(f, ["1,0,0,0,0", "2,0,0,0,0", "3,0,0,0,0"])
# 島 3: 技術 26 (rand 0.96875 で random(100) = 96 = 70 + 26)、観測衛星 1、宇宙ステーション 5074
base_map(f, 3, rockets(1))
f.main(3, money=9000000, food=100000, eis1=0, eis2=1, eis7=5074)
f.main(3, eisei5="0,0,0,0,0,26,0")
f.commands(3, [
    (C["Eisei"], 0, 0, 0, 1), (C["Eiseimente"], 0, 0, 0, 2), (C["Eiseimente"], 0, 0, 0, 99),
])
# 島 1: 技術ちょうど 5000、宇宙ステーション 1
base_map(f, 1, rockets(10))
f.main(1, money=9000000, food=100000, eis7=1)
f.main(1, eisei5="0,0,0,0,0,5000,0")
f.commands(1, [(C["Eiseimente"], 0, 0, 0, 99), (C["Eisei"], 0, 0, 0, 99)])
# 島 2: 技術 6687 (rand 0.96875 で random(10000) = 9687 = 3000 + 6687)
base_map(f, 2, rockets(10))
f.main(2, money=9000000, food=100000, eis7=0)
f.main(2, eisei5="0,0,0,0,0,6687,0")
f.commands(2, [(C["Eisei"], 0, 0, 0, 99)])
f.save()

# ---- 衛星破壊砲の命中率 (rand をいろいろな値に固定して試す) -------------------------
f = Fixture("phase3-ops-rates")
auction_lots(f, ["1,0,0,0,0", "2,0,0,0,0", "3,0,0,0,0"])
# 島 3: イレギュラーで島 1 の衛星を順に撃ち、最後に宇宙ステーション (1005) を撃つ
base_map(f, 3, {})
f.main(3, money=9000000, food=100000, eis1=100, eis2=100, eis3=100, eis4=100, eis5=100,
       eis6=250, eis7=0)
f.ips(3, etc7="2,0,1")
f.commands(3, [(C["EiseiAtt"], 1, 0, 0, a) for a in (1, 2, 3, 4, 5, 6, 99)])
# 島 1: イレギュラー 31 で島 2 の宇宙ステーション (1) を撃ち (残り 1 で崩壊しない)、
# 残り 1 のイレギュラーで観測衛星を撃つ (軍事衛星もあるがイレギュラーを使う)
base_map(f, 1, {})
f.main(1, money=9000000, food=100000, eis1=100, eis2=100, eis3=100, eis4=100, eis5=100,
       eis6=31, eis7=1005)
f.ips(1, etc7="2,0,2")
f.commands(1, [(C["EiseiAtt"], 2, 0, 0, 99), (C["EiseiAtt"], 2, 0, 0, 2)])
# 島 2: 軍事衛星 181 で島 3 の衛星を順に撃つ (6 回で残り 1)
base_map(f, 2, {})
f.main(2, money=9000000, food=100000, eis2=100, eis4=181, eis6=0, eis7=1)
f.ips(2, etc7="2,0,3")
f.commands(2, [(C["EiseiAtt"], 3, 0, 0, a) for a in (1, 2, 3, 4, 5, 6)] +
           [(C["EiseiAtt"], 3, 0, 0, 1)])
f.save()

# ---- 衛星レーザーが当たる地形 ---------------------------------------------------
f = Fixture("phase3-ops-lzr")
auction_lots(f, ["1,0,0,0,0", "2,0,0,0,0", "3,0,0,0,0"])
KINDS = [("Sea", 0), ("Waste", 0), ("Mountain", 0), ("Gold", 1), ("Seacity", 10),
         ("Seatown", 10), ("Umishuto", 10), ("Umiamu", 1), ("Sbase", 20), ("Oil", 0),
         ("Nursery", 10), ("Frocity", 3), ("Ice", 0), ("Fune", 1), ("Onsen", 10),
         ("Forest", 50)]
# 島 3: イレギュラー 76 (5 ずつ減り、15 発で 1、16 発目で崩壊) で島 1 の 16 種類の地形を撃つ
base_map(f, 3, {})
f.main(3, money=9000000, food=100000, eis4=0, eis6=76)
f.ips(3, etc7="2,0,1")
f.commands(3, [(C["EiseiLzr"], 99, 0, 0, 0)] +
           [(C["EiseiLzr"], 1, i % 12, 1 + i // 12, 0) for i in range(len(KINDS))])
base_map(f, 1, {(i % 12, 1 + i // 12): k for i, k in enumerate(KINDS)})
# 島 1: 軍事衛星 11 (10 ずつ減り、1 発目で残り 1、2 発目で崩壊) で島 3 の町を撃つ
f.main(1, money=9000000, food=100000, eis4=11, eis6=0)
f.ips(1, etc7="2,0,3")
f.commands(1, [(C["EiseiLzr"], 3, i, 11, 0) for i in range(4)])
base_map(f, 2, {})
f.main(2, money=9000000, food=100000)
f.save()
