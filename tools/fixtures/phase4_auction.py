#!/usr/bin/env python3
"""phase4-auction-*: ハコオクの落札・連続 1 位の賞品 (doIslandProcess 15788〜16957 行) の突き合わせ用データ。

出品 3 枠 (auction.dat の先頭 3 行) と島ごとの入札額・補助金・auc0/4/5/6 を組み合わせて、
品物の種類 (0〜31) と落札・資金不足・賞品・殿堂入りの道を通す。

- phase4-auction-lotNN: ターン 100 (ターン杯のターン) に、島 3 が 1 枠目、島 1 が 2 枠目、
  島 2 が 3 枠目を落札する。品物は 3 つずつ
- phase4-auction-prizeN: ターン 7 に、連続 1 位 (auc4 の 2 番目 = 5) の島が賞品を受け取る
- phase4-auction-mix: ターン 100 に、賞品の島と落札する島が混じる

rand を 0.75 / 0.96875 に固定すると、ほかの段階 (災害・暴動・怪獣・維持・移民) は
Perl 版でも何も起きない。人工衛星は置かない。

    python3 -I tools/fixtures/phase4_auction.py
    for d in crates/hakoniwa-core/tests/fixtures/phase4-auction-*/; do
        RANDS="75 96875" tools/perl-harness/run-harness.sh $(basename $d) \\
            estimate,income,commands,eachhex,process,estimate
    done
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import LAND, Fixture  # noqa: E402

IDS = (3, 1, 2)  # hakojima.dat の並び (処理順)
ZOO_ANIMALS = ",".join(["1"] + ["0"] * 30)  # 動物 1 匹 (動物園の値より少ない)
ZOO_FULL = ",".join(["90"] + ["0"] * 30)  # 動物 90 匹 (動物園の値より多い)
FACTORY = ("Factory", 30)  # 出品 30 番で動かす地形


def base_map(zoo=False, plains=True, seller=False):
    cells = [("Town", 40)] * 6
    if zoo:
        cells.append(("Zoo", 60))
    if seller:
        cells.append(FACTORY)
    if plains:
        cells += [("Plains", 0)] * 5
    return cells


class AucFixture(Fixture):
    def turn(self, turn):
        """hakojima.dat の 1 行目 (ターン数)"""
        lines = self._lines("hakojima.dat")
        lines[0] = str(turn).encode()
        self._write("hakojima.dat", lines)

    def lots(self, lots):
        """auction.dat の先頭 3 行 (出品 3 枠)"""
        lines = self._lines("auction.dat")
        for i, lot in enumerate(lots):
            lines[i] = ",".join(str(v) for v in lot).encode()
        self._write("auction.dat", lines)


def make(name, turn, lots, islands):
    """islands: 島 ID → dict(map=..., main=..., auction=..., ips=...)"""
    f = AucFixture(name)
    f.turn(turn)
    f.lots(lots)
    for iid in IDS:
        spec = islands.get(iid, {})
        f.map(iid, spec.get("map", base_map()))
        f.main(iid, **{f"eis{i}": 0 for i in range(1, 8)})
        f.main(iid, **{"money": 200000, "food": 50000, **spec.get("main", {})})
        f.auction(iid, **spec.get("auction", {}))
        if "ips" in spec:
            f.ips(iid, **spec["ips"])
    f.save()
    return name


def lot_value(kind):
    """品物ごとの avalue"""
    return {9: 3, 10: 2, 11: 3, 12: 4, 17: 2, 18: 3, 22: 5, 23: 4, 24: 70, 25: 30,
            27: 6, 28: 7}.get(kind, 0)


def extra(kind):
    """品物が読む島の値と地図"""
    spec = {}
    if kind in (6, 8, 19, 20, 21):
        spec["map"] = base_map(zoo=True)
        spec["ips"] = {"etc6": ZOO_ANIMALS}
    if kind == 7:
        # 動物園があるが動物が多すぎて受け取れない
        spec["map"] = base_map(zoo=True)
        spec["ips"] = {"etc6": ZOO_FULL}
    if kind == 9:
        spec["ips"] = {"etc8": "1,2,3,4,5,6,7"}
    if kind == 22:
        spec["main"] = {"eisei4": "100,81,67,1,2,3,4,5,6,7,8"}
    if kind in (23, 24):
        spec["main"] = {"eisei5": "50,33,47,29,1,9,2"}
    return spec


def merge(a, b):
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict):
            out[k] = {**out.get(k, {}), **v}
        else:
            out[k] = v
    return out


names = []

# ---- 落札 (ターン 100) ----------------------------------------------------
# 1 枠目: 島 3 (補助金で足りる)、2 枠目: 島 1 (補助金が足りず資金からも払う)、
# 3 枠目: 島 2 (補助金なし)。島 3 は auc6 の待ちターンが減る
# 0 番で始まる出品は読み込み時に乱数で選んだ品物に置き換わる (乱数の固定のしかたが Perl 版と
# テストで違う) ので、0 番は賞品 (phase4-auction-prize2) だけで通す
LOT_SETS = [(1, 2, 3), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14), (15, 16, 17),
            (18, 19, 20), (21, 22, 23), (24, 25, 26), (27, 28, 29)]
for n, kinds in enumerate(LOT_SETS):
    lots = [(k, lot_value(k), 2, 5 + i, 0) for i, k in enumerate(kinds)]
    islands = {
        3: merge({"auction": {"auc1": 5, "auc9": "13,0,130000,0,0", "auc6": "5,0,0",
                              "auc0": "1,0,9,0,0"}}, extra(kinds[0])),
        1: merge({"auction": {"auc2": 6, "auc9": "3,0,30000,0,0", "auc0": "1,0,2,0,7"}},
                 extra(kinds[1])),
        2: merge({"auction": {"auc3": 7, "auc6": "2,0,0"}}, extra(kinds[2])),
    }
    names.append(make(f"phase4-auction-lot{n:02}", 100, lots, islands))

# 出品 30 番 (島の地形) と 31 番 (不明な品物)。
# 1 枠目: 島 2 が出品した工場を島 3 が落札 (topid が工場と一致)
# 2 枠目: 存在しない島 9 の出品 (名前は 1 枠目の $dashiname が残る)
# 3 枠目: 不明な品物 31 番
factory = LAND[FACTORY[0]] * FACTORY[1]
names.append(make("phase4-auction-lot10", 100,
                  [(30, 2, 2, 8, factory), (30, 9, 2, 3, 0), (31, 1, 2, 4, 0)], {
                      3: {"auction": {"auc1": 8}},
                      1: {"auction": {"auc2": 3}},
                      2: {"auction": {"auc3": 4, "auc6": "2,6,0", "auc7": "Alpha島(6, 0)の工場"},
                          "map": base_map(seller=True)},
                  }))
# 1 枠目: 島 1 が出品した地形 (topid と違う) を島 3 と島 2 が同額で落札 (2 島とも受け取る)。
# 2 枠目: 島 3 は資金が足りない (auc6 が 7 になる)。島 1 は資金 + 補助金 (島 3 の落札代金) が
# ちょうど同額で何も起きない (収入の 187 を引いておく)。
# 3 枠目: 島 2 が自分の出品を落札。島 1 は auc6 が 77 で待ちターンが減る
names.append(make("phase4-auction-lot11", 100,
                  [(30, 1, 2, 2, 999), (25, 40, 2, 9, 0), (30, 2, 2, 1, factory)], {
                      3: {"auction": {"auc1": 2, "auc2": 9}, "main": {"money": 80000}},
                      1: {"auction": {"auc2": 9, "auc6": "77,6,0", "auc7": "テスト島の工場"},
                          "main": {"money": 69813}, "map": base_map(seller=True)},
                      2: {"auction": {"auc1": 2, "auc3": 1, "auc6": "2,6,0", "auc9": "1,0,15000,0,0"},
                          "map": base_map(seller=True)},
                  }))

# ---- 連続 1 位の賞品 (ターン 7) ------------------------------------------------
# 島 3: auc4c が 1 になるだけ。島 1: 3 回目で殿堂入り (auc0c > auc5c)。
# 島 2: 5 回目で殿堂入り (auc0c <= auc5c)
PRIZE_SETS = [(6, 9, 14), (15, 22, 23), (24, 0, 30), (29, 31, 25), (7, 10, 16), (20, 26, 28)]
for n, kinds in enumerate(PRIZE_SETS):
    auc4 = ["4,5,0", "3,5,2", "1,5,4"]
    auc5 = ["0,0,0,0,0", "2,0,3,0,1", "5,0,50,0,2"]
    islands = {}
    for i, (iid, k) in enumerate(zip(IDS, kinds)):
        islands[iid] = merge({"auction": {"auc0": f"{k},{lot_value(k) or 2},12,0,0",
                                          "auc4": auc4[i], "auc5": auc5[i]}}, extra(k))
    # 3 枠目の出品 (topvalue がメッセージに出る)
    names.append(make(f"phase4-auction-prize{n}", 7,
                      [(1, 0, 2, 0, 0), (2, 0, 2, 0, 0), (12, 3, 2, 6, 0)], islands))

# ---- 混合 (ターン 100) --------------------------------------------------------
# 島 3 は賞品 (平地が無いので受け取れない)。auc6 の待ちターンが減るだけ残る。島 1 は 1・2 枠目を落札。島 2 は 3 枠目を落札
names.append(make("phase4-auction-mix", 100,
                  [(17, 2, 2, 3, 0), (12, 5, 2, 4, 0), (27, 3, 2, 5, 0)], {
                      3: {"auction": {"auc0": "10,2,7,0,0", "auc4": "2,5,1", "auc1": 3, "auc6": "4,3,3"},
                          "map": base_map(plains=False)},
                      1: {"auction": {"auc1": 3, "auc2": 4, "auc9": "5,0,50000,0,0"}},
                      2: {"auction": {"auc3": 5, "auc4": "1,4,0", "auc9": "x"}},
                  }))
