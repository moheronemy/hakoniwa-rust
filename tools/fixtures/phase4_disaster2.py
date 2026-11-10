#!/usr/bin/env python3
"""phase4-disaster2-*: doIslandProcess の地盤沈下・台風・巨大隕石・巨大ミサイル・隕石・噴火
(Perl 版 15248〜15665 行) の突き合わせ用データ。

rand は固定値なので random(n) はいつも int(r * n)。発生判定は人工衛星の値 (負の値で
起きやすくなる) で選び、ほかの段階 (地震・津波・暴動・怪獣・人工衛星の維持・移民) が
Perl 版でも何も起きないようにしてある:

- 地震・津波 (5 - eis2/15) は rand 1/256 (random(1000) = 3) では eis2 >= 30 で止まる。
  噴火 (5 - eis2/40) は eis2 = 40 なら起き、80 なら起きない
- 人工衛星の維持 (eis -= random(2)) は rand < 0.5 なら値が変わらない。rand >= 0.5 では
  人工衛星を 0 以下にしておく (防衛衛星は隕石で 0 になる島だけ持たせる)
- 隕石のくり返し (random(2) == 0 の間) は rand < 0.5 では終わらないので、rand < 0.5 では
  隕石を起こさないか、お守り (toto2) の分岐に入れる
- 地盤沈下は広さ 350 を超えないと起きない (12x12 の島ではありえない) ので、
  estimate を通さない process だけの手順で、hakojima.dat の広さを使う

    python3 -I tools/fixtures/phase4_disaster2.py
    RANDS="00390625 0078125" tools/perl-harness/run-harness.sh phase4-disaster2-a process
    RANDS="00390625" tools/perl-harness/run-harness.sh phase4-disaster2-b process
    RANDS="25 50" tools/perl-harness/run-harness.sh phase4-disaster2-c \\
        estimate,income,commands,eachhex,process,estimate
    RANDS="8125 875 96875" tools/perl-harness/run-harness.sh phase4-disaster2-d \\
        estimate,income,commands,eachhex,process,estimate
    RANDS="75 8125 875 96875" tools/perl-harness/run-harness.sh phase4-disaster2-e \\
        estimate,income,commands,eachhex,process,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, Fixture, monster  # noqa: E402

LEGEND = {
    ".": ("Sea", 0), ",": ("Sea", 1), "p": ("Plains", 0), "T": ("Town", 30),
    "m": ("Mountain", 0), "g": ("Gold", 0), "o": ("Onsen", 0), "S": ("Sbase", 0),
    "c": ("Seacity", 10), "O": ("Oil", 0), "i": ("Ice", 0), "F": ("Farm", 10),
    "f": ("Forest", 10), "W": ("Waste", 0), "M": ("Monster", monster(1, 5)),
    "u": ("Fune", 1), "a": ("Umiamu", 10), "e": ("Seatown", 10), "U": ("Umishuto", 10),
    "w": ("EneWd", 10), "h": ("Haribote", 0), "n": ("Nursery", 10), "k": ("Monument", 0),
    "C": ("College", 5), "D": ("Defence", 77), "H": ("House", 10), "B": ("Town", 200),
    "q": ("Frocity", 10),
}


def toto(toto2):
    return f"0,{toto2},0,0,0,0,0"


def quiet(f):
    """人工衛星・eisei1 (暴動の判定) を 0 にし、お守りを無くす"""
    for island_id in (1, 2, 3):
        f.main(island_id, eisei1=0, **{f"eis{i}": 0 for i in range(1, 8)})
        f.ips(island_id, etc8=toto(0))


# ------------------------------------------------------------- phase4-disaster2-a
# process だけ。rand 1/256 (random(1000) = 3, random(12) = 0) と 1/128 (7, 0)
f = Fixture("phase4-disaster2-a")
# 島 1: 地盤沈下 (広さ 400)
f.grid(1, [
    "pT,.mpppppp.",
    "ppp.gpppTppp",
    "pSpppoppppp,",
    "ppppcpppppp.",
    "pppOpppippp.",
    "ppppepppapp.",
    "ppUpppuppppp",
    "pppppppppppp",
    "pppMpppppppp",
    "pppppppppppp",
    "pppppFFfpppp",
    "pppppppppp,,",
], LEGEND)
# 島 2: 台風の被害 (森の数ごと)、そのあと (0, 0) で噴火
f.grid(2, [
    "T,......ffff",
    "m.....fffFff",
    "....fFfFfff.",
    "....ffffk...",
    "..Fw.h......",
    "...u..n.....",
    ".FFF..pp....",
    "..kFk.......",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
# 島 3: お守りで台風・巨大隕石・隕石を防ぎ (4 -> 3 -> 1 -> 0)、最後の噴火は防げない
f.grid(3, [
    "piFF........",
    "OTppp.......",
    "pppnp.......",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
quiet(f)
f.main(1, area=400, pop=100, eis1=20, eis2=80, eis3=80)
f.main(2, area=100, pop=100, eis1=-100, eis2=40, eis3=80)
f.main(3, area=100, pop=100, eis1=-100, eis2=40, eis3=-100)
f.ips(3, etc8=toto(4))
f.save()

# ------------------------------------------------------------- phase4-disaster2-b
# process だけ。rand 1/256
f = Fixture("phase4-disaster2-b")
# 島 1: 噴火をお守りで防ぐ
f.grid(1, [
    "pTp.........",
    "Tpp.........",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
# 島 2: (0, 0) に巨大隕石 (広域被害)、隕石はお守りで防ぐ
f.grid(2, [
    "TSM,pmk.....",
    "cpTMaWp.....",
    "ppmuOpp.....",
    "TTipppp.....",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
# 島 3: 台風 (もう一つの地図) と、海の上の施設のまわりの噴火
f.grid(3, [
    "pcfFf.......",
    "uWFfFf......",
    "..ffhf......",
    "...nwfF.....",
    "..fffff.....",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
quiet(f)
f.main(1, area=100, pop=100, eis1=20, eis2=40, eis3=80)
f.ips(1, etc8=toto(2))
f.main(2, area=100, pop=100, eis1=20, eis2=80, eis3=-100)
f.ips(2, etc8=toto(1))
f.main(3, area=100, pop=100, eis1=-100, eis2=40, eis3=80)
f.save()

# ------------------------------------------------------------- phase4-disaster2-c
# estimate から通しで。rand 0.25 と 0.5: 台風 (大学 5 の有無) と巨大ミサイル
TYPHOON = [
    "............",
    ".pFppfpFpp..",
    ".ppffFffpp..",
    ".Fpfffwpp...",
    ".phppnppu...",
    ".FFpFpppp...",
    "..ffFfpTp...",
    "..ppFpppp...",
    "..wph.n.u...",
    "..pppppp....",
    "............",
    "............",
]
f = Fixture("phase4-disaster2-c")
f.grid(1, TYPHOON[:9] + ["..pppCpp....", "............", "............"], LEGEND)
f.grid(2, TYPHOON, LEGEND)
# 島 3: 記念碑を発射する (LovePeace なので自分の島に落ちる)
f.grid(3, [
    "............",
    ".BBBpppp....",
    ".pTpFpkp....",
    ".pppppppp...",
    ".pfpSpppp...",
    "..pppmpp....",
    "..pTppMp....",
    "..pppppp....",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
quiet(f)
f.main(1, money=100000, eis1=-10000)
f.main(2, money=100000, eis1=-10000)
f.main(3, money=100000)
f.commands(3, [(COMMAND["Monument"], 3, 6, 2, 0)])
f.save()

# ------------------------------------------------------------- phase4-disaster2-d
# estimate から通しで。eis3 = -40000 で巨大隕石は起きず (2 + 800)、隕石は起きる (5 + 1000)。
# rand 0.8125 / 0.875 / 0.96875 で (9, 9) / (10, 10) / (11, 11) に落ちる
def far_map(cells):
    rows = [["."] * 12 for _ in range(12)]
    for y in range(1, 9):
        for x in range(1, 9):
            rows[y][x] = "p"
    rows[2][2] = "T"
    for (x, y), c in cells.items():
        rows[y][x] = c
    return ["".join(r) for r in rows]


f = Fixture("phase4-disaster2-d")
f.grid(1, far_map({(9, 9): "m", (10, 10): "S", (11, 11): "M", (8, 8): "p"}), LEGEND)
f.grid(2, far_map({(9, 9): "g", (10, 10): ",", (11, 11): "i"}), LEGEND)
# 島 3: 防衛施設・改と防衛衛星 (隕石で 0 になる)
f.grid(3, far_map({(9, 9): "T", (8, 9): "D", (10, 10): "p", (11, 11): "p"}), LEGEND)
quiet(f)
for island_id in (1, 2, 3):
    f.main(island_id, eis3=-40000)
f.main(3, eis5=10)
f.save()

# ------------------------------------------------------------- phase4-disaster2-e
# estimate から通しで。rand 0.75 では巨大隕石も起きる。島 1 はバリア (家 10)、島 2 はお守り
f = Fixture("phase4-disaster2-e")
f.grid(1, far_map({(3, 3): "H", (9, 9): "T", (10, 10): "p", (11, 11): "q"}), LEGEND)
f.grid(2, far_map({(9, 9): "T", (10, 10): "e", (11, 11): "U"}), LEGEND)
f.grid(3, far_map({(9, 9): "o", (10, 10): "c", (11, 11): "p", (10, 9): "a", (9, 10): "u"}),
       LEGEND)
quiet(f)
for island_id in (1, 2, 3):
    f.main(island_id, eis3=-40000)
f.ips(2, etc8=toto(2))
f.save()
