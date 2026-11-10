#!/usr/bin/env python3
"""phase2-badfields: 複合値が正規表現に一致しない (負の数を含む) ときの突き合わせ用データ。

Perl では一致しなかったとき $1.. は「同じスコープで最後に一致した正規表現」の値になる。
実際のゲームでも Hakoniwa Cup の負けで eisei4 の値が負になり、こうなる。

    python3 -I tools/fixtures/phase2_badfields.py
    tools/perl-harness/run-harness.sh phase2-badfields estimate,income,commands,eachhex,estimate
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

f = Fixture("phase2-badfields")
# 島 1: eisei4 (チーム) が負、スタジアムあり
f.main(1, money=400000, eisei4="300,-43,-43,2,1,0,4,3,2,1,0")
f.cells(1, {(5, 5): ("Kyujokai", 0)})
# 島 2: eisei4 も eisei5 (マスコット) も壊れている
f.main(2, money=300000, eisei4="5,6,7,-1,0,0,0,0,0,0,0", eisei5="10,-20,30,40,5,6,7")
f.ips(2, etc8="1,-2,3,4,5,6,7")
# 島 3: 正常 (前の島の値が残るかどうかを見るため)
f.main(3, money=200000, eisei4="9,8,7,3,2,1,6,5,4,1,0", eisei5="1,2,3,4,5,6,7")
f.save()
