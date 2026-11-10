#!/usr/bin/env python3
"""phase3-city / phase3-city2: doCommand の都市系 (ハイテク技術誘致・自宅建設・輝ける都市・
改装・海底基地・海底都市・防災都市化・現代都市・海底新都市・僕の引越し・僕の引越し２) の
突き合わせ用データ。

    python3 -I tools/fixtures/phase3_city.py
    tools/perl-harness/run-harness.sh phase3-city estimate,income,commands,...(12 回),estimate
    tools/perl-harness/run-harness.sh phase3-city2 estimate,income,commands,...(12 回),estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND as C, Fixture, monster  # noqa: E402


def cmd(kind, x=0, y=0, arg=0, target=0):
    return (C[kind], target, x, y, arg)


# ---------------------------------------------------------------- phase3-city
f = Fixture("phase3-city")

# 島 1: 電力は足りる。首都・自宅・基地が無い (shu = hou = rena = 0)。
# 失敗する計画を並べて (どれも 0 を返すので 1 ターンでまとめて実行される)、そのあと成功する計画
f.grid(1, [
    "............",
    ".TTTTT.F.G..",
    ".TTTTT.P....",
    ".TTXTT.B.r..",
    ".TTTTT.Z.N..",
    ".TTYTT.n.Q..",
    ".TTTTT.C.c..",
    "............",
    ".s.U.M.H.z..",
    ".t..........",
    "............",
    "AAAA........",
], {
    "A": ("EneAt", 4000),
    ".": ("Sea", 0), "T": ("Town", 20), "F": ("Factory", 50), "G": ("Factory", 100),
    "P": ("Plains", 0), "X": ("Newtown", 149), "B": ("Bigtown", 100), "r": ("Rizort", 10),
    "Z": ("BigRizort", 10), "N": ("Newtown", 149), "Y": ("Seacity", 200),
    "n": ("Newtown", 50), "Q": ("Procity", 50), "C": ("Seacity", 200), "c": ("Seacity", 100),
    "s": ("Sea", 1), "U": ("Town", 100), "M": ("Monster", monster(3, 2)),
    "H": ("HTFactory", 495), "z": ("Zoo", 0), "t": ("Town", 50),
})
f.main(1, money=3000000, food=500000)
f.commands(1, [
    cmd("HTget", 7, 1),          # 工場だが 100 でない → logJoFail
    cmd("HTget", 7, 2),          # 平地 → logLandFail
    cmd("House", 0, 0),          # 海 → logLandFail
    cmd("Bettown", 1, 1),        # 町 → logLandFail
    cmd("Bettown", 7, 3),        # 現代都市だが首都が無い → logJoFail
    cmd("Kai", 7, 2),            # 平地 → logLandFail
    cmd("Kai", 9, 3),            # リゾート (条件不足) → logJoFail
    cmd("Kai", 7, 4),            # 大リゾート (rena 不足) → logJo2Fail
    cmd("Sbase", 1, 8),          # 浅瀬 → logLandFail
    cmd("Seacity", 7, 2),        # 平地 → logLandFail
    cmd("Procity", 1, 9),        # 町 (100 でない) → logLandFail
    cmd("Bigtown", 7, 5),        # ニュータウン 50 → logJoFail
    cmd("Bigtown", 9, 4),        # ニュータウン 149 だが町が少ない → logJoFail
    cmd("Seatown", 9, 6),        # 海底都市 100 → logJoFail (?, ?)
    cmd("Seatown", 7, 6),        # 海底都市 200 だが町が少ない → logJoFail (?, ?)
    cmd("Boku", 7, 2),           # 平地 → logBokuFail
    cmd("Boku", 9, 5),           # 周りに町が無い防災都市 → logNoTownAround
    cmd("Boku2", 5, 8),          # 怪獣 → logBokuFail2
    cmd("Kai", 9, 8),            # 動物園 (rena/75 で頭打ち) ← 1 ターン目
    cmd("HTget", 9, 1, 3),       # 工場 100 → ハイテク企業、あと 2 回繰り返す
    cmd("HTget", 7, 8),          # ハイテク企業 495 → 500
    cmd("House", 7, 2),          # 平地に自宅 (税率 0 → 5)
    cmd("Procity", 3, 8),
    cmd("Bigtown", 3, 3),
    cmd("Seatown", 3, 5),
    cmd("Sbase", 0, 0),
    cmd("Seacity", 11, 11),
])

# 島 2: 首都・自宅がある。基地があるので rena (estimate が基地の値から計算する) が多い
f.grid(2, [
    "............",
    ".hSb........",
    "............",
    ".EbE....bE..",
    "............",
    ".k.c.d.g....",
    "............",
    ".f.u.o.O....",
    "............",
    ".v.z.x.H.J..",
    "............",
    "AAAAWWWW....",
], {
    "A": ("EneAt", 4000), "W": ("Base", 4000),  # 基地は rena を増やす
    ".": ("Sea", 0), "h": ("House", 3), "S": ("Shuto", 100), "b": ("Bigtown", 200),
    "E": ("Bettown", 300), "k": ("Kyujo", 0), "c": ("Conden4", 2), "d": ("Conden4", 3),
    "g": ("Conden4", 5), "f": ("Fune", 10), "u": ("Fune", 5), "o": ("Foodim", 480),
    "O": ("Foodim", 479), "v": ("EneSo", 100), "z": ("Zoo", 195), "x": ("Defence", 0),
    "H": ("HTFactory", 50), "J": ("SHTF", 60),
})
f.main(2, money=3000000, food=500000, eisei1=2)
f.commands(2, [
    cmd("House", 5, 0, 7),       # 自宅がある → 税率だけ変えて 0
    cmd("Kai", 7, 5),            # コンデンサ 4 (値 5) → logLandFail
    cmd("Kai", 3, 7),            # 船 (値 5) → logLandFail
    cmd("Kai", 7, 7),            # 食品工場 479 → logLandFail
    cmd("Bettown", 3, 1),        # 首都の隣
    cmd("Bettown", 2, 3),        # 輝ける都市 2 つの隣
    cmd("Bettown", 8, 3),        # 輝ける都市 1 つの隣 → logJoFail
    cmd("Kai", 1, 5),            # 野球場 (ky2 = 0 → eisei4 を初期化)
    cmd("Kai", 3, 5),
    cmd("Kai", 5, 5),
    cmd("Kai", 1, 7),
    cmd("Kai", 5, 7),
    cmd("Kai", 1, 9),
    cmd("Kai", 3, 9),            # 動物園 195 → 200 で頭打ち
    cmd("Kai", 5, 9),
    cmd("Kai", 7, 9),
    cmd("Kai", 9, 9),
])

# 島 3: 電力不足。僕の引越し・僕の引越し２
f.grid(3, [
    "............",
    ".....E.M.K..",
    "T...........",
    "QT...e.M.F.t",
    ".TT.........",
    "............",
    "..H.........",
    "............",
    "......PmD...",
    "aabb.ZT.P...",
    ".P..........",
    "WWWWWWWWWWWW",
], {
    ".": ("Sea", 0), "E": ("Bettown", 1600), "M": ("Mountain", 0), "K": ("Kajino", 2100),
    "Q": ("Procity", 50), "T": ("Town", 50), "e": ("Bettown", 1000), "F": ("Frocity", 30),
    "t": ("Town", 5), "Z": ("Procity", 195), "H": ("House", 9), "P": ("Plains", 0),
    "m": ("Monster", monster(14, 2)),
    "D": ("Conden2", 100), "a": ("College", 1), "b": ("College", 8), "W": ("Base", 4000),
})
f.main(3, money=3000000, food=500000)
f.commands(3, [
    cmd("HTget", 0, 0),          # 電力不足 → logMsNoEne
    cmd("Kai", 0, 0),
    cmd("Sbase", 0, 0),
    cmd("Seacity", 0, 0),
    cmd("Boku", 0, 3, 2),        # 防災都市。位置調整なしで周りの町を減らす (2 回)
    cmd("Boku2", 2, 6),          # 自宅 9 を持ち上げる
    cmd("Boku2", 6, 8),          # 怪獣 14 の隣に置く → コンデンサ 2 にメッキ (費用なし)
    cmd("Boku2", 8, 9),          # もう一度置ける。怪獣の隣だがコンデンサ 2 が無い
    cmd("Boku2", 1, 10),         # もう一度。怪獣がいない
    cmd("Boku2", 5, 1),          # 輝ける都市 1600 を持ち上げ
    cmd("Boku2", 7, 1),          # 山に置く → 空中都市
    cmd("Boku2", 9, 1),          # カジノ 2100 を持ち上げ
    cmd("Boku2", 9, 3),          # 海上都市に置く → 海都市
    cmd("Boku2", 5, 3),          # 輝ける都市 1000 を持ち上げ
    cmd("Boku2", 7, 3),          # 山には置けず、山を持ち上げる
    cmd("Boku2", 11, 6),         # 海に置く
    cmd("Boku", 5, 9),           # 防災都市 195 → 200 で頭打ち
])
f.save()

# ---------------------------------------------------------------- phase3-city2
f = Fixture("phase3-city2")

# 島 1: 野球場・改がある (ky2 > 0)。倉庫、リゾート、大リゾート、町に自宅
f.grid(1, [
    "............",
    ".k.q........",
    ".KrR....rR..",
    "............",
    "............",
    ".a.b.c.d....",
    "............",
    ".T.......Z..",
    "............",
    "............",
    "............",
    "AAAAWWWW....",
], {
    "A": ("EneAt", 4000), "W": ("Base", 4000),  # 基地は rena を増やす
    ".": ("Sea", 0), "k": ("Kyujo", 0), "q": ("Kyujokai", 0), "K": ("Kajino", 10),
    "r": ("Rizort", 100), "R": ("Rizort", 10), "Z": ("BigRizort", 10), "a": ("Kura", 850),
    "b": ("Kura", 950), "c": ("Kuraf", 37), "d": ("Kuraf", 39), "T": ("Town", 30),
})
f.main(1, money=3000000, food=500000, eisei4="5,06,99,1,2,3,4,5,6,7,8")
f.commands(1, [
    cmd("Kai", 1, 1),            # 野球場 (ky2 > 0 なので eisei4 はそのまま)
    cmd("Kai", 3, 1, 2),         # 野球場・改 (2 回)
    cmd("Kai", 1, 5, 2),         # 倉庫 850 → 950 → 950
    cmd("Kai", 5, 5, 2),         # 食料倉庫 37 → 38 → 39
    cmd("Kai", 7, 5),            # 食料倉庫 39 → 39
    cmd("Kai", 8, 2),            # リゾート (周りのリゾートが足りない) → logJoFail
    cmd("Kai", 2, 2),            # リゾート → 大リゾート
    cmd("Kai", 9, 7),            # 大リゾート → カジノ
    cmd("House", 1, 7, 3),       # 町に自宅
])

# 島 2: eisei4 に空欄がある (Perl の ++ で 1 になり、ほかの空欄はそのまま)
f.grid(2, [
    "............",
    ".q.p........",
] + ["............"] * 9 + ["AAAA........"], {
    "A": ("EneAt", 4000),
    ".": ("Sea", 0), "q": ("Kyujokai", 0), "p": ("Plains2", 0),
})
f.main(2, money=3000000, food=500000, eisei4="1,,9,,0,0,0,0,0,0,")  # 空欄もそのまま書き戻す
f.commands(2, [
    cmd("Kai", 1, 1),            # 野球場・改
    cmd("House", 3, 1),          # 開発予定地に自宅
])

# 島 3: eisei4 が形式に合わない → etc5 のマッチの値が入る (etc5 は estimate が必ず 31 欄にする)
f.grid(3, [
    "............",
    ".q.p........",
] + ["............"] * 9 + ["AAAA........"], {
    "A": ("EneAt", 4000),
    ".": ("Sea", 0), "q": ("Kyujokai", 0), "p": ("Plains", 0),
})
f.main(3, money=3000000, food=500000, eisei4="bad")
f.commands(3, [
    cmd("Kai", 1, 1, 2),
    cmd("House", 3, 1, 9),
])
f.save()
