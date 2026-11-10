#!/usr/bin/env python3
"""phase2-special*: doEachHex の大学・島営企業・記念碑の突き合わせ用データ。

    python3 -I tools/fixtures/phase2_special.py
    tools/perl-harness/run-harness.sh phase2-special estimate,eachhex,estimate
    tools/perl-harness/run-harness.sh phase2-special-egg estimate,eachhex,estimate
    tools/perl-harness/run-harness.sh phase2-special-egg2 estimate,eachhex,estimate
    tools/perl-harness/run-harness.sh phase2-special-mons estimate,eachhex,estimate
    tools/perl-harness/run-harness.sh phase2-special-mons2 estimate,eachhex,estimate

ほかの (未移植の) 系統の地形は原則として置かないが、文部科学省・島営企業が周りに
必要とする首都・島主の家・ハイテク多国籍企業 (・改) だけは、Perl 版の分岐が何もしない
状態で置く: 首都は値 750 以上 4000 以下 (食料が足り、誘致活動中でない)、島主の家は
eisei1 = 0 (税収 0)、ハイテク多国籍企業 (・改) は pika = 0。
怪獣は、まだ処理されていないうちに記念碑 94 が倒す位置にだけ置く (怪獣の分岐は通らない)。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture, monster  # noqa: E402

LEGEND = {
    ".": ("Sea", 0),
    "W": ("Waste", 0),
    "P": ("Plains", 0),
    "F": ("Factory", 0),
    "f": ("Factory", 10),
    "v": ("Town", 50),
    "S": ("Seacity", 200),
    "N": ("Mountain", 10),
    "A": ("Taishi", 2),
    # 大学
    "0": ("College", 0),
    "1": ("College", 1),
    "2": ("College", 2),
    "3": ("College", 3),
    "4": ("College", 4),
    "5": ("College", 5),
    "6": ("College", 6),
    "7": ("College", 7),
    "8": ("College", 8),
    "w": ("College", 77),
    "x": ("College", 78),
    "y": ("College", 79),
    "z": ("College", 80),
    "q": ("College", 98),
    "Q": ("College", 99),
    # 島営企業
    "O": ("OWNF", 0),
    "o": ("OWNF", 1123),
    "u": ("OWNF", 5),
    # 記念碑
    "a": ("Monument", 0),
    "b": ("Monument", 1),
    "c": ("Monument", 10),
    "d": ("Monument", 15),
    "e": ("Monument", 16),
    "g": ("Monument", 74),
    "h": ("Monument", 84),
    "i": ("Monument", 93),
    "j": ("Monument", 94),
    "E": ("Monument", 80),
    "G": ("Monument", 81),
    "J": ("Monument", 82),
    "K": ("Monument", 83),
    # 吸収される施設 (Perl 版の分岐が何もしない状態)
    "U": ("Shuto", 4000),
    "H": ("House", 0),
    "I": ("Foodim", 500),
    "T": ("HTFactory", 500),
    "Z": ("SHTF", 500),
    # 怪獣
    "m": ("Monster", monster(1, 3)),
    "n": ("Monster", monster(28, 5)),
}

# 何も無い島 (テンプレートの地図にはほかの系統の地形があるので、使わない島も書き換える)
QUIET = ["............"] * 4 + ["....SS......", "....SSN....."] + ["............"] * 6


def quiet(f, island_id):
    f.grid(island_id, QUIET, LEGEND)
    f.main(island_id, money=300000, food=50000)


# 政策 (島営企業の吸収に使う合計 $costseisaku)。先頭が 0 だと estimate が全部消す
ETC5 = "1,50," + ",".join(["0"] * 29)

# ---------------------------------------------------------------- phase2-special
f = Fixture("phase2-special")
# 島 3: 文部科学省が周囲を吸収して島営企業になり、条件を満たすので島役所には戻らない。
# 大学 0〜8、文部科学省 77〜79、出動中の生物大学 (平地に戻る)、記念碑のお土産・豊作・古代遺跡・幸運
f.grid(3, [
    "............",
    ".....HI.....",
    "....azU.....",
    ".....ZT.....",
    "..012345....",
    "..678wxyQ...",
    "....SSSS....",
    "...bShSSc...",
    "...dSSSSe...",
    "....aig.....",
    "............",
    "............",
], LEGEND)
f.main(3, money=500000, food=50000, eis7=1000000, eisei1=0,
       eisei5="0,0,0,0,0,500000,0")
f.owner(3, pika=0)

# 島 1: 島営企業が隣の食物研究所・ハイテク多国籍企業 (・改) を吸収する。
# 政策 (etc5) は文部科学省が無いと estimate が消すので 77 を 1 つ置く (島役所に戻る)
f.grid(1, [
    "............",
    "..SSSSSSSS..",
    "..SSSSSSSS..",
    "..SS........",
    "...eFU......",
    "....ZOH.....",
    "....TI......",
    "..SSSSSS....",
    ".........w..",
    "............",
    "............",
    "............",
], LEGEND)
f.main(1, money=300000, food=50000, eisei1=0, eisei5="0,0,0,0,0,5000,0")
f.owner(1, pika=0)
f.ips(1, etc5=ETC5)

# 島 2: 島営企業が 2 つあると先に処理した方が開発予定地になる。
# 条件を満たさない文部科学省 (77〜80) は島役所に戻る
f.grid(2, [
    "............",
    "..o.........",
    "....SS......",
    "...SSS..w...",
    "....x.y.....",
    "......z.....",
    "....I.......",
    "........u...",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(2, money=300000, food=50000)
f.ips(2, etc5=ETC5)
f.save()

# ---------------------------------------------------------------- phase2-special-egg
# 卵は 1 行目に置く (孵化すると外側のループが 8 番目のマスに飛ぶので、それより前でないと
# 孵化した怪獣をもう一度処理してしまう)。
# (3, -1) の読み出しは反対側の端 (3, 11) になり、その工場の値で火災の判定をする
f = Fixture("phase2-special-egg")
for island_id, egg in ((3, "E"), (1, "G"), (2, "J")):
    f.grid(island_id, [
        ".v.{}vvvvv...".format(egg),
        "...PS.......",
        "..SSSS......",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "...f........",
    ], LEGEND)
    f.main(island_id, money=300000, food=50000)
f.save()

f = Fixture("phase2-special-egg2")
f.grid(3, [
    "K.vvvvvvvv..",
    "PNA.........",
    "SSSS........",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "F...........",
], LEGEND)
f.main(3, money=300000, food=50000)
quiet(f, 1)
quiet(f, 2)
f.save()

# ---------------------------------------------------------------- phase2-special-mons
# 島 3: 超神獣テトラが怪獣の隣の荒地に出動し、記念碑 94 が両方を倒す。
# 島 1: 出動は 1 ターンに 1 回だけ ($take)。マスコットいのらがいると出動中の生物大学は戻らない。
#       x = 0 の記念碑 94 は (-1, 7) = (11, 7) の怪獣を倒す
f = Fixture("phase2-special-mons")
f.grid(3, [
    "............",
    "............",
    "..q.........",
    "............",
    "............",
    ".....jm.....",
    "......W.....",
    "..SS........",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(3, money=300000, food=50000, eisei5="3,0,0,0,0,0,0")
f.grid(1, [
    "............",
    "............",
    "............",
    "............",
    "............",
    ".....jn.....",
    ".....mW.....",
    "j..........m",
    "..Q.........",
    "............",
    "..4.........",
    "..SS........",
], LEGEND)
f.main(1, money=300000, food=50000)
quiet(f, 2)
f.save()

# 島 3: 生物大学のマスコットいのらが出動する
f = Fixture("phase2-special-mons2")
f.grid(3, [
    "............",
    "............",
    "..4.........",
    "............",
    "............",
    ".....jm.....",
    "......W.....",
    "..SS........",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.main(3, money=300000, food=50000, eisei5="2,0,0,0,0,0,0")
quiet(f, 1)
quiet(f, 2)
f.save()
