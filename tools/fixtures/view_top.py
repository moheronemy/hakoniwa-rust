"""Fixture for the top page view (hako-top.cgi tempTopPage).

    python3 tools/fixtures/view_top.py
    python3 -I tools/perl-harness/run_cgi_settings.py crates/hakoniwa-core/tests/fixtures/cgi/view-top-*.json

島 3, 1, 2 (保存順) に、トップページの欄と印 (賞・倒した怪獣・ターン杯・ユニーク地形・家・
人工衛星・家畜・マスコット・お守り・へそくり・援助射撃・首都の名前の持ち越し・負の数の入った
eisei4・同じポイントの島の順) が出るような値を入れる。
"""
from fixturelib import Fixture


def lines(f, name, text_lines):
    (f.dir / name).write_bytes(("\n".join(text_lines) + "\n").encode("euc_jp"))


f = Fixture("view-top")

# ---- 島 3 (保存順 1 番目): 賞・倒した怪獣・ターン杯・ユニーク地形コンプリート・魔塔・
#      壊れた eisei3 ----
f.main(3, prize="5,1073741825,100,200,", taiji=7, monsterlive=2, monsterlivetype=6,
       pts=60000, pop=7900, farm=30, factory="50,20,1,2,0,0,0,0,0,0", mountain=10,
       eisei1=10, eisei2=12345, eisei3="300,-40,0,0,250",
       eisei4="10,20,30,2,1,0,5,2,1,1,9", eisei5="5,6,7,8,3,100,1",
       eisei6="1,1,1,1,1,1,1,1,1,1,1,1",
       eis1=50, eis2=0, eis3=30, eis4=0, eis5=0, eis6=10, eis7=1234567,
       onm="オーナー3", eis8="1-0")
f.owner(3, totoyoso2="東京シティー", tare=5, zipro=0, leje=2, monta=-3, hamu=0, pika=12)
f.ips(3, etc6=",".join(["1"] * 31), etc7="1,3,1", etc8="0,3,0,0,0,0,0", etc0=7)
f.auction(3, auc0="9,4,1200,2,1", auc1=100, auc2=0, auc3=40, auc4="2,3,0",
          auc5="0,0,0,0,0", auc9="12,5,30000,0,0")

# ---- 島 1: 同じポイント (島 2 と、家の境界の値)・負の数の eisei4・壊れた eisei6・
#      首都の持ち越し・お守り・へそくり ----
f.main(1, pts=15000, absent=3, pop=7200, farm=0, factory="0,800,0,0,0,0,0,0,0,0", mountain=0,
       eisei1=0, eisei3="100,30,0,0,90", eisei4="1,2,3,-1,0,0,0,0,0,0,1",
       eisei6="1,-1,0,0,0,0,0,0,0,0,0,0", onm="", comment="ひとこと&lt;b&gt;")
f.owner(1, totoyoso2="123", zipro=4, tare=0, leje=0, monta=0, hamu=-200, pika=-7)
f.ips(1, etc8="2,0,0,0,0,0,0", etc7="2,5,2", etc0=3)
f.auction(1, auc0="30,0,800,1,3", auc8="テスト品", auc7="出品島の品", auc1=300, auc2=0,
          auc3=40, auc5="10,5,5000,3,2", auc4="1,1,0",
          auc9="7,1,20000,0,0")

# ---- 島 2: 援助射撃 (見つからない島)・電力不足・マスコット・首都なし・小屋。
#      壊れた auc9。チーム力で島 1 より前に来るので、総合ポイント順が保存順と変わる ----
f.main(2, prize="4,0,", pts=15000, eisei1=5, pop=5700, farm=600, factory="0,0,1,0,0,0,0,0,0,0", mountain=0,
       eisei3="10,50,0,0,10", eisei4="100,100,100,0,0,0,3,1,2,4,11", eisei5="3,1,1,1,0,9,0",
       eisei6="0,0,0,0,0,0,0,0,0,0,0,0", onm="オーナー2", eis8="2-2", monsterlive=0)
f.owner(2, totoyoso2="555", rena=35, monta=5, hamu=100, pika=-50, tare=1)
f.ips(2, etc7="2,4,99", etc0=15)
f.auction(2, auc0="0,0,0,0,0", auc1=300, auc2=50, auc3=0, auc5="0,0,0,0,0",
          auc9="1,-2,0,0,0")

# ハコオクの出品 (auction.dat の先頭 3 行): 出品した島の名前・1000 倍・3 枠目のお守りの癖
raw = f._lines("auction.dat")
raw[0:3] = [b"30,1,3,0,0", b"10,2,15,0,0", b"9,7,0,0,0"]
f._write("auction.dat", raw)

# アンケート (an.dat の先頭 5 行)
raw = f._lines("an.dat")
raw[0:5] = [b"2", b"1", b"0", b"0", b"0"]
f._write("an.dat", raw)

# ログ: 機密のログは出ない
lines(f, "hakojima.log0", [
    "0,3,0,,<SMALL>負荷計測</SMALL>",
    "1,3,1,,<B>機密</B>のログ",
    "0,3,2,1,公開の<B>ログ</B>",
])
lines(f, "hakojima.log1", ["0,2,3,,前のターンのログ", "1,2,3,,前のターンの機密"])
lines(f, "hakojima.lhc", ["2,カップの古い記録", "3,カップの新しい記録"])
lines(f, "hakojima.auc", ["2,オークションの古い記録", "3,オークションの新しい記録"])
f.save()
