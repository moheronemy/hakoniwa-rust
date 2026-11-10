#!/usr/bin/env python3
"""phase2-industry / phase2-industry-t10: doEachHex の産業系 (畜産・食品加工工場・発電所・
ハイテク工場・森・倉庫・家・防衛施設・油田・浅瀬・砂浜・氷河・関所・役所・金山・遊園地)
の突き合わせ用データ。この系統の地形と、分岐の無い地形・移植済みの地形だけを置く。

    python3 -I tools/fixtures/phase2_industry.py
    tools/perl-harness/run-harness.sh phase2-industry estimate,eachhex,estimate
    tools/perl-harness/run-harness.sh phase2-industry-t10 estimate,eachhex,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

LEGEND = {
    ".": ("Sea", 0),
    "~": ("Sea", 1),
    "T": ("Town", 150),
    "v": ("Town", 1),
    "a": ("Farm", 20),
    "c": ("Farmchi", 100),
    "C": ("Farmchi", 3998),
    "p": ("Farmpic", 200),
    "w": ("Farmcow", 300),
    "0": ("Foodka", 0),
    "1": ("Foodka", 1),
    "2": ("Foodka", 2),
    "3": ("Foodka", 3),
    "f": ("EneFw", 4000),
    "o": ("EneSo", 5),
    "O": ("EneSo", 300),
    "b": ("EneBo", 10),
    "A": ("EneAt", 300),
    "B": ("EneAt", 4000),
    "h": ("HTFactory", 499),
    "H": ("HTFactory", 100),
    "s": ("SHTF", 500),
    "S": ("SHTF", 10),
    "F": ("Forest", 100),
    "G": ("Forest", 4000),
    "K": ("Kura", 850),
    "J": ("Kura", 50),
    "Q": ("Kura", 950),
    "E": ("House", 5),
    "e": ("House", 0),
    "d": ("Defence", 1),
    "D": ("Defence", 0),
    "L": ("Oil", 0),
    "n": ("Sunahama", 0),
    "i": ("Ice", 0),
    "I": ("Ice", 30),
    "x": ("Seki", 0),
    "y": ("Yakusho", 0),
    "g": ("Gold", 10),
    "r": ("Park", 0),
    "W": ("Waste", 0),
    "M": ("Mountain", 10),
    "P": ("Plains", 0),
    "U": ("Onsen", 30),
    "Z": ("Seacity", 50),
    "R": ("Sbase", 10),
}


def build(name, turn=None):
    f = Fixture(name)
    # 島 1: 電力が足りている。食品加工工場の各段階、発電所、工場、森、倉庫、家
    f.grid(1, [
        "............",
        ".TTTTTTT~n.i",
        ".Tc3wapT.IL.",
        ".Tcaw2T.~.x.",
        ".TTTTTTT..~.",
        "..ff.TAT.TT.",
        ".ob.hsHSBTTT",
        ".FF.G.KJQEv.",
        "....y...Av..",
        "..pa1..0c...",
        "..Cw..D..0.L",
        "..........i.",
    ], LEGEND)
    f.main(1, money=500000, food=30000, eisei1=1)
    f.owner(1, pika=5)

    # 島 2: 電力不足 (rena が大きいと消費が増える)。防衛施設の自爆 (端の近くも)
    f.grid(2, [
        "............",
        "....TTTT....",
        "...MTLiT~...",
        "...TndZW....",
        "...gTxRU....",
        "....TMTT....",
        "............",
        ".c0p..r..TT.",
        ".aw...h.TEe.",
        "..3c....TT..",
        "..........TL",
        ".........Mid",
    ], LEGEND)
    f.main(2, money=400000, food=20000, eisei1=500)
    f.owner(2, rena=3000000, pika=0)

    # 島 3: 遊園地が 6 つ以上 (収入なし)、家の税収の段階、値 1 の村しか無い原子力発電所
    f.grid(3, [
        "............",
        ".rrr........",
        ".rrrT.......",
        "..TTEe......",
        "..TTTT......",
        "...QJK......",
        "..o.O.......",
        "...FGF......",
        "...FFF......",
        "....y...Av..",
        "............",
        "............",
    ], LEGEND)
    f.main(3, money=300000, food=10000, eisei1=700)
    f.owner(3, pika=0)
    if turn is not None:
        lines = (f.dir / "hakojima.dat").read_bytes().split(b"\n")
        lines[0] = str(turn).encode()
        (f.dir / "hakojima.dat").write_bytes(b"\n".join(lines))
    f.save()


build("phase2-industry")
# ターン 10 (5 でも 2 でも割り切れる): 家の税収が多いときも入る
build("phase2-industry-t10", turn=10)
