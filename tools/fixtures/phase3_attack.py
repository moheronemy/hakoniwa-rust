#!/usr/bin/env python3
"""phase3-attack*: doCommand のミサイル・動物派遣・大使派遣の突き合わせ用データ。

rand が固定されるので、1 回の計画のミサイルはすべて同じマスに落ちる。
rand 0 なら計画の座標そのもの、rand 0.5 なら誤差 19 の弾は (x+2, y)、誤差 7 の弾
(PP・核) は (x+1, y+1) (y が偶数のとき)、SPP は (x, y)。そこで目標のマスは
(x, y), (x+2, y), (x+1, y+1) の 3 つを同じ地形にしてある (y は偶数)。

島 1 は島 2 の大使館を持つ (同盟)、島 3 は etc7 で島 2 を撃つ許可を持つ、島 2 は自分の島を撃つ。

    python3 -I tools/fixtures/phase3_attack.py
    for f in phase3-attack phase3-attack-lr phase3-attack-ld phase3-attack-guard \
             phase3-attack-mon phase3-attack-mon6 phase3-attack-boat phase3-attack-send \
             phase3-attack-defhex; do
        RANDS="0 50 03125 96875" tools/perl-harness/run-harness.sh $f \
            estimate,income,commands,commands,commands,commands,commands,commands,commands,commands,commands,commands,estimate
    done
    # 地形隆起弾の記念碑 (rand(1000) < 22) を 20 以上 22 未満で確かめる
    RANDS=021484375 tools/perl-harness/run-harness.sh phase3-attack-lr (同じ STEPS)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, Fixture, monster  # noqa: E402

NM = COMMAND["MissileNM"]
PP = COMMAND["MissilePP"]
SPP = COMMAND["MissileSPP"]
ST = COMMAND["MissileST"]
SS = COMMAND["MissileSS"]
LR = COMMAND["MissileLR"]
LD = COMMAND["MissileLD"]
SEND = COMMAND["SendMonster"]
TAISHI = COMMAND["Taishi"]


def mon(kind, hp):
    return ("Monster", monster(kind, hp))


def put(f, island_id, cells, fill=("Sea", 0)):
    """cells は {(x, y): (地形名, 値)}。残りは fill"""
    flat = [fill] * 144
    for (x, y), c in cells.items():
        flat[y * 12 + x] = c
    f.map(island_id, flat)


def spot(cells, x, y, c):
    """(x, y), (x+2, y), (x+1, y+1) を同じ地形にする"""
    for p in [(x, y), (x + 2, y), (x + 1, y + 1)]:
        cells[p] = c


def home(cells, row=11, bases=(("Base", 4000),), extra=()):
    """撃つ側の設備: 町 3 つ (人口 600)、原子力発電所 2 つ、基地を row の行に置く"""
    row_cells = [("Town", 200)] * 3 + [("EneAt", 4000)] * 2 + list(bases) + list(extra)
    for x, c in enumerate(row_cells):
        cells[(x, row)] = c


def set_turn(f, turn):
    lines = f._lines("hakojima.dat")
    lines[0] = str(turn).encode()
    f._write("hakojima.dat", lines)


MONEY = 900000

# ---------------------------------------------------------------------------
# phase3-attack: 通常系のミサイル (NM / PP / SPP / ST) と地形ごとの結果、難民と平和賞
f = Fixture("phase3-attack")
t = {}
spot(t, 0, 0, ("Town", 1700))
spot(t, 3, 0, ("Waste", 0))
spot(t, 6, 0, ("RottenSea", 5))
spot(t, 9, 0, ("Oil", 0))
spot(t, 0, 2, ("Fune", 1))
spot(t, 3, 2, ("Frocity", 10))
spot(t, 6, 2, ("Nursery", 5))
spot(t, 9, 2, ("Ice", 0))
spot(t, 0, 4, ("Onsen", 10))
spot(t, 3, 4, ("Forest", 10))
spot(t, 6, 4, ("Mountain", 0))
spot(t, 9, 4, ("Sea", 0))
spot(t, 0, 6, ("Sea", 1))
spot(t, 3, 6, ("Sbase", 10))
spot(t, 6, 6, ("Monument", 25))
spot(t, 9, 6, ("Minato", 100))
spot(t, 0, 8, ("Newtown", 300))
spot(t, 3, 8, ("Bigtown", 400))
spot(t, 6, 8, ("Seacity", 10))
spot(t, 9, 8, ("Gold", 0))
spot(t, 0, 10, ("Haribote", 0))
spot(t, 3, 10, ("Factory", 30))
spot(t, 6, 10, ("Plains", 0))
spot(t, 9, 10, ("Farm", 10))
# 島 2 の町・発電所・基地 (自分の島を撃つ)
for p, c in {(0, 1): ("Town", 200), (2, 1): ("Town", 200), (3, 1): ("Town", 200),
             (5, 1): ("EneAt", 4000), (6, 1): ("EneAt", 4000), (11, 11): ("Base", 4000)}.items():
    t[p] = c
put(f, 2, t)

# 島 1: 同盟 (島 2 の大使館)、難民の受け入れ先 (町・平地)、神殿・神社
a = {}
home(a, row=11, bases=(("Base", 4000), ("Base", 4000)),
     extra=(("Taishi", 2), ("Monument", 26), ("Monument", 27)))
for x in range(12):
    a[(x, 0)] = ("Plains", 0)
for x in range(6):
    a[(x, 1)] = ("Town", 180)
put(f, 1, a)

# 島 3: etc7 で島 2 を撃つ許可
b = {}
home(b, row=11)
put(f, 3, b)
f.ips(3, etc7="2,5,2")
for i in (1, 2, 3):
    f.main(i, money=MONEY)
f.commands(1, [
    (NM, 2, 0, 0, 1),
    (ST, 2, 6, 0, 2),
    (NM, 2, 0, 2, 1),
    (PP, 2, 3, 4, 1),
    (NM, 2, 6, 6, 3),
    (ST, 2, 9, 6, 1),
    (NM, 2, 0, 8, 1),
    (SPP, 2, 9, 10, 1),
])
f.commands(3, [
    (NM, 2, 3, 0, 2),
    (NM, 2, 9, 0, 1),
    (NM, 2, 3, 2, 1),
    (NM, 2, 6, 2, 1),
    (NM, 2, 9, 2, 1),
    (NM, 2, 0, 4, 1),
    (NM, 2, 6, 4, 0),
    (NM, 2, 3, 8, 1),
])
f.commands(2, [
    (NM, 2, 9, 4, 1),
    (NM, 2, 0, 6, 1),
    (NM, 2, 3, 6, 1),
    (SPP, 2, 6, 8, 1),
    (NM, 2, 9, 8, 1),
    (NM, 2, 0, 10, 1),
    (PP, 2, 3, 10, 2),
    (PP, 2, 6, 10, 1),
])
f.save()


SPOTS = [(x, y) for y in (0, 2, 4, 6, 8) for x in (0, 3, 6, 9)]
TARGET_HOME = {(0, 1): ("Town", 200), (2, 1): ("Town", 200), (3, 1): ("Town", 200),
               (5, 1): ("EneAt", 4000), (6, 1): ("EneAt", 4000), (11, 11): ("Base", 4000)}


def spots_fixture(name, kind, lands, attackers_fill=("Plains", 0), extra_target=None):
    """島 2 の SPOTS に lands を置き、島 1・3・2 が順に 1 つずつ kind で撃つ"""
    f = Fixture(name)
    t = dict()
    for (x, y), c in zip(SPOTS, lands):
        spot(t, x, y, c)
    t.update(TARGET_HOME)
    if extra_target:
        t.update(extra_target)
    put(f, 2, t)
    a = {}
    home(a, row=11, extra=(("Taishi", 2),))
    put(f, 1, a, fill=attackers_fill)
    b = {}
    home(b, row=11)
    put(f, 3, b, fill=attackers_fill)
    f.ips(3, etc7="2,5,2")
    for i in (1, 2, 3):
        f.main(i, money=MONEY)
    cmds = {1: [], 3: [], 2: []}
    order = [1, 3, 2]
    for n, ((x, y), _) in enumerate(zip(SPOTS, lands)):
        cmds[order[n % 3]].append((kind, 2, x, y, 1))
    return f, cmds


# ---------------------------------------------------------------------------
# phase3-attack-lr: 地形隆起弾 (海底基地などに当たると撃った島の同じ座標が浅瀬になる)
LR_LANDS = [
    ("Mountain", 0), ("Gold", 0), ("Sbase", 10), ("Seacity", 10), ("Umishuto", 10),
    ("Seatown", 10), ("Oil", 0), ("Fune", 1), ("Frocity", 10), ("Umiamu", 10),
    ("RottenSea", 5), ("Sea", 1), ("Sea", 0), ("Ice", 0), ("Ice", 1), mon(1, 3),
    ("Plains", 0),
]
# 浅瀬 (11 番目の場所) の計画の座標だけ深い海にする (浅瀬にするのは計画の座標のまわり)
f, cmds = spots_fixture("phase3-attack-lr", LR, LR_LANDS,
                        extra_target={SPOTS[LR_LANDS.index(("Sea", 1))]: ("Sea", 0)})
for i, c in cmds.items():
    f.commands(i, c)
f.save()

# ---------------------------------------------------------------------------
# phase3-attack-ld: 陸地破壊弾と核 (核は最後に撃つ)
LD_LANDS = [
    ("Mountain", 0), ("Onsen", 10), ("Gold", 0), ("Sbase", 10), ("Fune", 1),
    ("Frocity", 10), ("Umiamu", 10), ("Seatown", 10), ("Umishuto", 10), ("Seacity", 10),
    mon(1, 3), ("RottenSea", 5), ("Sea", 1), ("Ice", 0), ("Town", 159), ("Sea", 0),
    ("Oil", 0), ("Minato", 100), ("Newtown", 50), ("Bigtown", 60),
]
# 核の着弾点 (6, 10) と (7, 11)、(0, 10) と (1, 11) のまわり
SS_AREA = {(4, 10): ("Town", 50), (5, 10): mon(1, 3), (6, 10): ("Town", 100),
           (7, 10): ("Forest", 10), (8, 10): ("Town", 100), (9, 10): ("Oil", 0),
           (10, 10): ("Waste", 0), (5, 9): ("Factory", 10), (6, 9): ("Sea", 1),
           (7, 11): ("Town", 100), (8, 11): ("Farm", 10), (0, 10): ("Town", 100),
           (1, 10): ("Ice", 0), (0, 9): mon(2, 2), (1, 11): ("Plains", 0)}
f, cmds = spots_fixture("phase3-attack-ld", LD, LD_LANDS, extra_target=SS_AREA)
cmds[1].append((SS, 2, 6, 10, 1))
cmds[3].append((SS, 2, 0, 10, 2))
cmds[2].append((SS, 2, 9, 9, 1))
for i, c in cmds.items():
    f.commands(i, c)
f.save()

# ---------------------------------------------------------------------------
# phase3-attack-guard: 防衛施設・防衛衛星・怪獣 23・島主の家 10、許可・人口の判定、不発弾、資金切れ
f = Fixture("phase3-attack-guard")
t = {}
spot(t, 0, 0, ("Defence", 0))
spot(t, 6, 0, ("Procity", 100))
spot(t, 0, 4, ("House", 3))
spot(t, 6, 4, ("Plains", 0))
t[(7, 4)] = ("Shuto", 100)
spot(t, 0, 8, ("Procity", 200))
spot(t, 6, 8, ("Forest", 10))
for x in range(4):
    t[(x, 11)] = ("Town", 200)
t[(4, 11)] = ("EneAt", 4000)
for x in range(5, 12):
    t[(x, 11)] = ("Base", 0)
for x in range(8, 12):
    t[(x, 10)] = ("Plains", 0)
put(f, 2, t)
f.ips(2, etc7="2,0,1")

a = {}
home(a, row=11, extra=(("Taishi", 2), ("House", 10)))
a[(5, 5)] = ("Plains", 0)
a[(7, 5)] = ("Plains", 0)
put(f, 1, a)

b = {(0, 11): ("EneAt", 4000), (1, 11): ("Base", 4000), (2, 11): ("RottenSea", 5),
     (3, 11): mon(23, 5), (4, 11): ("Town", 100), (5, 5): ("Plains", 0), (6, 5): ("Plains", 0)}
put(f, 3, b)
f.ips(3, etc7="2,5,2")
f.main(3, money=MONEY, eis5=3)
f.main(1, money=MONEY)
f.main(2, money=400)
f.commands(1, [
    (NM, 99, 0, 0, 1),
    (NM, 3, 5, 5, 1),
    (PP, 2, 0, 0, 3),
    (NM, 2, 6, 0, 2),
    (NM, 2, 0, 4, 1),
    (NM, 2, 6, 4, 1),
    (NM, 2, 0, 8, 1),
    (ST, 2, 6, 8, 2),
    (SPP, 3, 5, 5, 3),
    (NM, 1, 7, 5, 1),
    (SEND, 3, 0, 0, 1),
    (TAISHI, 3, 5, 5, 0),
])
f.commands(3, [
    (NM, 2, 6, 8, 1),
    (NM, 3, 6, 5, 3),
])
f.commands(2, [
    (SPP, 2, 2, 0, 2),
    (NM, 1, 5, 5, 1),
    (NM, 2, 8, 10, 0),
    (NM, 2, 9, 10, 0),
])
f.save()


# ---------------------------------------------------------------------------
# phase3-attack-mon / -mon6: 怪獣に当たるミサイル (硬化・叩き落とし・退治・王蟲・人造怪獣・
# 神殿と神社の収入・魔方陣)。-mon6 はターン 6 (めたはむ系が硬化せず、クジラが硬化する)
MON_SPEC = [  # (地形, 撃つ島, 計画, 弾数)
    (mon(2, 1), 1, NM, 1), (mon(9, 1), 3, NM, 1), (mon(3, 1), 1, NM, 1),
    (mon(15, 1), 3, NM, 1), (mon(13, 1), 2, NM, 1), (mon(20, 1), 1, NM, 1),
    (mon(21, 1), 3, NM, 1), (mon(22, 1), 2, NM, 1), (mon(18, 1), 1, NM, 1),
    (mon(30, 1), 3, NM, 1), (mon(19, 1), 2, NM, 1), (mon(14, 1), 1, NM, 1),
    (mon(17, 1), 3, NM, 1), (mon(8, 1), 2, NM, 1), (mon(1, 3), 1, NM, 1),
    (mon(1, 1), 3, ST, 1), (mon(1, 2), 2, NM, 3), (("Monument", 25), 1, ST, 2),
    (mon(6, 1), 3, ST, 1), (mon(10, 2), 2, NM, 2),
]
for name, turn in (("phase3-attack-mon", None), ("phase3-attack-mon6", 6)):
    f = Fixture(name)
    t = {}
    for (x, y), (land, _, _, _) in zip(SPOTS, MON_SPEC):
        spot(t, x, y, land)
    t.update(TARGET_HOME)
    put(f, 2, t)
    # 島 1: 同盟、神殿・神社、基地 2 つ (rena が大きいので魔方陣から怪獣が出る)
    a = {}
    home(a, row=11, bases=(("Base", 4000), ("Base", 4000)),
         extra=(("Taishi", 2), ("Monument", 26), ("Monument", 27)))
    put(f, 1, a)
    # 島 3: 撃つ許可、大学 99 と 4 (叩き落とされにくい)
    b = {}
    home(b, row=11, extra=(("College", 99), ("College", 4)))
    b[(11, 0)] = mon(1, 5)  # 島 1 は島 3 を撃つ許可がない (怪獣がいるので賠償金ではなく中止)
    put(f, 3, b)
    f.ips(3, etc7="2,5,2")
    for i in (1, 2, 3):
        f.main(i, money=MONEY)
    cmds = {1: [], 3: [], 2: []}
    for (x, y), (_, shooter, kind, arg) in zip(SPOTS, MON_SPEC):
        cmds[shooter].append((kind, 2, x, y, arg))
    cmds[1].append((NM, 3, 11, 0, 1))
    for i, c in cmds.items():
        f.commands(i, c)
    if turn:
        set_turn(f, turn)
    f.save()

# ---------------------------------------------------------------------------
# phase3-attack-boat: 難民 (平和賞 16・32、平地に 5 人を超える残り)、ステルスは難民なし、
# 基地なし、賠償金 (許可の状態が 2 でも相手の島が違えば賠償金)、動物園のない島への動物派遣
f = Fixture("phase3-attack-boat")
t = {(0, 0): ("Bigtown", 3000), (2, 0): ("Bigtown", 3000), (1, 1): ("Bigtown", 3000),
     (6, 0): ("Bigtown", 2015), (8, 0): ("Bigtown", 2015), (7, 1): ("Bigtown", 2015),
     (0, 4): ("Town", 114), (2, 4): ("Town", 114), (1, 5): ("Town", 114)}
t.update(TARGET_HOME)
t[(11, 11)] = ("Plains", 0)  # 島 2 は基地を持たない
t[(11, 10)] = ("College", 99)  # 動物園はないが、eisei5 (経験値) は残る
put(f, 2, t)
f.main(2, eisei5="0,0,0,0,0,1000,0")
# 島 1: 同盟、平和賞 8 を持つ。値 150 の町が 12 個、その後に平地が 12 個
a = {}
home(a, row=11, bases=(("Base", 4000),), extra=(("Taishi", 2),))
for x in range(12):
    a[(x, 0)] = ("Town", 150)
    a[(x, 1)] = ("Plains", 0)
put(f, 1, a)
f.main(1, prize="8,0,")
# 島 3: 撃つ許可、平和賞 8 と 16 を持つ。値 0 の町が 20 個、その次が平地
b = {}
home(b, row=11)
for p in range(20):
    b[(p % 12, p // 12)] = ("Town", 0)
b[(8, 1)] = ("Plains", 0)
b[(0, 5)] = ("Zoo", 0)
put(f, 3, b)
f.ips(3, etc6=",".join(["1"] * 31))
f.main(3, prize="24,0,1,2")
f.ips(3, etc7="2,5,2")
for i in (1, 2, 3):
    f.main(i, money=MONEY)
f.commands(1, [
    (NM, 2, 0, 0, 1),
    (NM, 3, 5, 5, 1),
])
f.commands(3, [
    (PP, 2, 6, 0, 1),
    (ST, 2, 0, 4, 1),
    (SEND, 2, 0, 0, 1),
    (NM, 1, 5, 5, 1),
])
f.commands(2, [
    (NM, 2, 0, 0, 1),
])
f.save()

# ---------------------------------------------------------------------------
# phase3-attack-send: 動物派遣と大使派遣
f = Fixture("phase3-attack-send")
# 大学 99 があるので eisei5 が残る (estimate が消さない)
# 島 2: 動物園 (怪獣 1 が 3 匹)、大使館 3 つ (それ以上受け入れない)。許可は島 3 (状態 1)
t = {(x, 0): ("Plains", 0) for x in range(12)}
t.update({(0, 2): ("Zoo", 0), (1, 2): ("Taishi", 3), (2, 2): ("Taishi", 3),
          (3, 2): ("Taishi", 3), (4, 2): ("Forest", 10), (5, 2): ("College", 99)})
home(t, row=11)
put(f, 2, t)
f.ips(2, etc7="1,0,3", etc6=",".join(["0", "3"] + ["0"] * 29))
f.main(2, eisei5="0,0,0,0,0,50,0")
# 島 1: 動物園 (怪獣 1 と 30 を 2 匹ずつ、7 を 1 匹)、島 2 への許可。
# 島 2 の経験値 (eisei5 の 6 番目) は 50 なので、怪獣 7 (経験値 30 の 2 倍) は送れない
a = {(x, 0): ("Plains", 0) for x in range(12)}
a[(0, 2)] = ("Zoo", 0)
a[(1, 2)] = ("College", 99)
a[(2, 2)] = ("RottenSea", 5)  # 怪獣はいないが腐海があるので、許可がなくても賠償金にはならない
home(a, row=11)
put(f, 1, a)
f.ips(1, etc7="2,0,2", etc6=",".join(["0", "2"] + ["0"] * 5 + ["1"] + ["0"] * 22 + ["2"]))
f.main(1, eisei5="0,0,0,0,0,100,0")
# 島 3: 発電所がない (エネルギー不足)、島 2 への許可
b = {(x, 0): ("Plains", 0) for x in range(12)}
b.update({(0, 2): ("Zoo", 0), (1, 2): ("College", 99), (0, 11): ("Town", 200), (1, 11): ("Town", 200),
          (2, 11): ("Town", 200), (3, 11): ("Base", 4000)})
put(f, 3, b)
f.ips(3, etc7="2,5,2", etc6=",".join(["1"] * 31))
f.main(3, eisei5="0,0,0,0,0,5000,0")
for i in (1, 2, 3):
    f.main(i, money=MONEY)
f.commands(1, [
    (SEND, 99, 0, 0, 1),
    (SEND, 3, 0, 0, 1),
    (SEND, 2, 0, 0, 31),
    (SEND, 2, 0, 0, 7),
    (SEND, 2, 0, 0, 1),
    (TAISHI, 99, 0, 0, 0),
    (TAISHI, 1, 0, 0, 0),
    (TAISHI, 2, 0, 0, 0),
    (TAISHI, 3, 20, 0, 0),
    (TAISHI, 3, 0, 2, 0),
    (TAISHI, 3, 1, 0, 0),
    (NM, 3, 0, 0, 1),  # 島 3 がこのターンに島 1 に大使館を置いたので同盟になっている
])
f.commands(3, [
    (NM, 2, 0, 0, 1),
    (SEND, 2, 0, 0, 1),
    (TAISHI, 2, 5, 0, 0),
    (TAISHI, 1, 5, 0, 0),
])
f.commands(2, [
    (SEND, 1, 0, 0, 1),
    (TAISHI, 1, 3, 0, 0),
    (TAISHI, 3, 3, 0, 0),
    (NM, 1, 0, 0, 1),
])
f.save()

# ---------------------------------------------------------------------------
# phase3-attack-defhex: 防衛施設の判定を覚える @HdefenceHex (撃った島と座標で覚えるので
# 別の島を狙っても前の判定を使う)、防衛施設に当たると周りの判定を消す、SPP が防衛施設に
# 当たると防衛される。島 3 は 0 発 (撃てるだけ = 100 発) 撃ち、不発弾の数 $alltotal を増やす
f = Fixture("phase3-attack-defhex")
D, P, Q = (5, 5), (5, 3), (1, 8)
t = {D: ("Defence", 0), (1, 10): ("Defence", 0), P: ("Plains", 0), Q: ("Plains", 0)}
t.update(TARGET_HOME)
put(f, 2, t)
a = {P: ("Plains", 0), Q: ("Plains", 0)}
home(a, row=11, bases=(("Base", 4000), ("Base", 4000)), extra=(("Taishi", 2),))
put(f, 1, a)
f.ips(1, etc7="2,0,3")
b = {P: ("Plains", 0), Q: ("Plains", 0)}
for p in range(24):
    b[(p % 12, 9 + p // 12)] = ("Base", 200)
b.update({(0, 11): ("Town", 200), (1, 11): ("Town", 200), (2, 11): ("Town", 200),
          (3, 11): ("EneAt", 4000)})
put(f, 3, b)
f.ips(3, etc7="2,5,2")
for i in (1, 2, 3):
    f.main(i, money=MONEY)
f.main(2, absent=0)  # 計画がないと資金繰りが続いて放棄されるので
f.commands(3, [(NM, 2, 9, 7, 0)])
f.commands(1, [
    (SPP, 2, *D, 1),
    (SPP, 2, *P, 1),
    (SPP, 3, *P, 1),
    (SPP, 3, *Q, 1),
    (SPP, 2, *Q, 1),
    (NM, 2, *D, 1),
    (SPP, 2, *P, 1),
])
f.save()
