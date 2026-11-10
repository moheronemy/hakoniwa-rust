#!/usr/bin/env python3
"""phase5-command: 計画の入力 (commandMain)・政策・ローカル掲示板の画面操作の突き合わせ用データ。

島 1: 資金 50000。荒地・浅瀬・森 (本数いろいろ)・平地が少しずつある地図。計画は 41 (資金繰り) を
      数量 0..39 にして、ずれがわかるようにする。etc5 の先頭は 0 (政策を入れるたびに初期化される)。
島 2: etc5 の先頭が 3 (初期化されない)。eisei5 は正規表現に合わない値。資金は少ない。
島 3: ip0 が "0" (IP 履歴を作り直す)。etc6 に先頭 0 付きの値。

    python3 -I tools/fixtures/phase5_command.py
    python3 -I tools/perl-harness/run_cgi.py crates/hakoniwa-core/tests/fixtures/cgi/<case>.json
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

LEGEND = {
    ".": ("Sea", 0),
    "s": ("Sea", 1),  # 浅瀬
    "w": ("Waste", 0),
    "p": ("Plains", 0),
    "f": ("Forest", 50),
    "F": ("Forest", 300),
    "G": ("Forest", 150),
}

f = Fixture("phase5-command")
f.grid(1, [
    "............",
    "..s.....s...",
    "...pppw.....",
    "..pfFGwp....",
    "..pwFfpp.s..",
    "...pppp.....",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
], LEGEND)
f.commands(1, [(41, 0, 0, 0, i) for i in range(40)])
f.main(1, money=50000)
f.main(2, money=500, eisei5="1,2,x", eisei4="5,6,7,1,1,1,1,1,1,1,0")
f.ips(2, etc5="3,1,2,3,4,5,6,7,8,9,10,11,12,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
      etc8="1,2,3,4,5,6,7", ip5="192.168.1.9")
f.ips(3, ip0="0", etc6="007,0,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,099")
f.save()
