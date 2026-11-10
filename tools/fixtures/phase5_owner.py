#!/usr/bin/env python3
"""phase5-owner: 開発画面 (tempOwner / tempCommand) の表示の突き合わせ用データ。

島 3 (1 位): ポイント 60000 (開発度 x2)、ハイテク多国籍企業・経済大学 (factory)、政策あり
      (etc5 の先頭 2、教育 45 → 表示は上限の +9、大学はすべて)、資金が多い、ハコオク出品可、首都名変更なし (555)。
      計画は大学・畜産・回数付きの計画など。
島 1 (2 位): ポイント 32000 (x1.4)、ハイテク多国籍企業・改、政策なし、ハコオク入札不可 (auc6 = 3)、
      首都名変更あり (0)、ほかの 2 島から援助射撃の申請 (etc7)。計画はミサイル・衛星・魔法・援助など。
島 2 (3 位): ポイント 46000 (x1.8)、ハコオク出品可、資金が大きく負 (値段が負になり食料で表示)、首都名変更の値が 7、政策あり (教育 10 → 大学 3 種類まで)。計画は掘削・地雷・倉庫・船・記念碑など、
      名前の無い計画番号 (0, 50, 999) も入れる。
ハコオクの出品: 1 枠目はサッカー (値 "05" をそのまま出す)、2 枠目は島の出品 (auc7)・落札済み、
      3 枠目は「今回はお休み」(29、出品の計画が出る条件)。ターンは 30 (各種予想が出ない)。

    python3 -I tools/fixtures/phase5_owner.py
    python3 -I tools/perl-harness/run_cgi.py crates/hakoniwa-core/tests/fixtures/cgi/owner-view.json
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, Fixture  # noqa: E402


def plans(items):
    out = []
    for i, (kind, target, arg) in enumerate(items):
        k = COMMAND[kind] if isinstance(kind, str) else kind
        out.append((k, target, i % 12, (i * 5) % 12, arg))
    return out


f = Fixture("phase5-owner")

# ターン数 (hakojima.dat 1 行目)
lines = (f.dir / "hakojima.dat").read_bytes().split(b"\n")
lines[0] = b"30"
(f.dir / "hakojima.dat").write_bytes(b"\n".join(lines))

# ハコオクの出品 3 枠 (auction.dat 先頭 3 行: 品番,値,状態,最高額,最高額の島)
lines = (f.dir / "auction.dat").read_bytes().split(b"\n")
lines[0:3] = [b"22,05,3,0120,1", b"30,1,15,50,0", b"29,0,0,0,0"]
(f.dir / "auction.dat").write_bytes(b"\n".join(lines))

# 島 3
f.main(3, pts=60000, money=3000000, factory="0,0,0,0,1,0,0,0,0,4")
f.ips(3, etc5="2,3,4,5,6,7,8,9,10,11,45,13,12,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
      etc7="1,5,1")
f.auction(3, auc6="1,0,0")
f.owner(3, totoyoso2="555")
f.commands(3, plans([
    ("College", 0, 0), ("College", 0, 1), ("College", 0, 2), ("College", 0, 3),
    ("College", 0, 4), ("College", 0, 9), ("College", 0, 10),
    ("Farmcpc", 0, 0), ("Farmcpc", 0, 2), ("Farmcpc", 0, 3), ("Farmcpc", 0, 5),
    ("Farm", 0, 0), ("Farm", 0, 3), ("Foodim", 0, 2), ("Factory", 0, 0), ("Nursery", 0, 1),
    ("EneAt", 0, 4), ("EneFw", 0, 1), ("EneWt", 0, 0), ("EneBo", 0, 2), ("EneWd", 0, 1),
    ("EneSo", 0, 3), ("EneCs", 0, 2), ("Boku", 0, 1), ("Park", 0, 1), ("Umiamu", 0, 0),
    ("Kai", 0, 5), ("HTget", 0, 1), ("Givefood", 0, 2), ("Mountain", 0, 3),
    ("Prepare", 0, 0), ("Reclaim", 0, 7), ("Taishi", 1, 0), ("EiseiLzr", 2, 0),
    ("House", 0, 3), ("Base", 0, 0), ("Seki", 0, 0),
]))

# 島 1
f.main(1, pts=32000, money=100, factory="0,0,0,0,0,1,0,0,0,0")
f.ips(1, etc5="0,3,4,5,6,7,8,9,10,11,10,13,12,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
f.auction(1, auc6="3,0,0", auc7="ドリーム")
f.owner(1, totoyoso2="0")
f.commands(1, plans([
    (0, 3, 2), ("MissileNM", 3, 0), ("MissilePP", 2, 3), ("MissileST", 99, 1),
    ("MissileSPP", 3, 2), ("MissileSS", 3, 0), ("MissileLR", 2, 4), ("MissileLD", 2, 5),
    ("Taishi", 99, 0),
    ("EiseiAtt", 2, 0), ("EiseiAtt", 2, 3), ("EiseiAtt", 2, 6), ("EiseiAtt", 2, 7),
    ("EiseiAtt", 2, 99), ("EiseiAtt", 2, 2),
    ("Magic", 3, 0), ("Magic", 3, 3), ("Magic", 3, 6), ("Magic", 3, 7), ("Magic", 3, 8),
    ("SendMonster", 3, 5), ("SendMonster", 3, 31), ("SendMonster", 3, 30),
    ("Sell", 0, 0), ("Sell", 0, 5), ("Propaganda", 0, 0), ("Propaganda", 0, 2),
    ("Eisei", 0, 2), ("Eisei", 0, 99), ("Eisei", 0, 9), ("Eisei", 0, 5),
    ("Eiseimente", 0, 6), ("Eiseimente", 0, 0),
    ("Money", 99, 0), ("Money", 3, 10), ("Food", 2, 3), ("Food", 2, 0), ("EneGive", 3, 5),
    ("Givefood", 0, 0), ("College", 0, 2),
]))

# 島 2
f.main(2, pts=46000, money=-5000000)
f.ips(2, etc7="1,9,1")
f.ips(2, etc5="1,0,0,0,0,0,0,0,0,0,10," + ",".join(["0"] * 20))
f.owner(2, totoyoso2="7")
f.auction(2, auc6="1,0,0")
f.commands(2, plans([
    ("Destroy", 0, 0), ("Destroy", 0, 4), ("Mine", 0, 0), ("Mine", 0, 5), ("Mine", 0, 12),
    ("Zoo", 0, 3), ("Zoo", 0, 40), ("Train", 0, 4), ("Train", 0, 11),
    ("Kura", 0, 0), ("Kura", 0, 5), ("Kuraf", 0, 0), ("Kuraf", 0, 3), ("Kuraf", 0, 15),
    ("Kura2", 0, 0), ("Kura2", 0, 2), ("Fune", 0, 0), ("Fune", 0, 3), ("Fune", 0, 25),
    ("Monument", 0, 2), ("Monument", 0, 200), ("DoNothing", 0, 0), ("Giveup", 0, 0),
    (999, 0, 3), (50, 1, 2), ("College", 0, 2), ("Prepare2", 0, 0), ("AutoDelete", 0, 0),
    ("Sell", 0, 1), ("EneNF", 0, 0), ("Bettown", 0, 0), ("Boku2", 0, 0), ("Eisei", 0, 1),
    ("College", 0, 3), ("College", 0, 4),
]))
f.save()
