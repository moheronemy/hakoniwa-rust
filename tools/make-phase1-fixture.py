#!/usr/bin/env python3
"""Build the `phase1-mix` legacy fixture used to check estimate() against Perl.

Starts from tests/fixtures/legacy-turn3 (real Perl output) and rewrites the maps of
island 1 and 2 so that almost every land kind and the special monument / college /
house / train values appear, and sets a few composite fields that estimate() reads.

Usage: python3 -I tools/make-phase1-fixture.py
Then regenerate the expected values with tools/perl-harness/run-phase1.sh.
The planned commands are chosen so that the command phase only runs code that is
already ported (cost checks that fail, DoNothing, Giveup).
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIX = ROOT / "crates/hakoniwa-core/tests/fixtures"
SRC = FIX / "legacy-turn3"
DST = FIX / "phase1-mix"

tables = (ROOT / "crates/hakoniwa-core/src/tables.rs").read_text(encoding="utf-8")
enum = tables.split("pub enum LandKind {")[1].split("}")[0]
L = {m.group(1): int(m.group(2)) for m in re.finditer(r"(\w+) = (\d+),", enum)}


def monster(kind, hp):
    return (kind << 4) | hp


ISLAND1 = [
    ("Town", 120), ("Procity", 50), ("Onsen", 30), ("Shuto", 200), ("Minato", 40),
    ("Farm", 30), ("Foodim", 100), ("Foodim", 600), ("Foodka", 2), ("Farmchi", 250),
    ("Farmpic", 170), ("Farmcow", 99), ("Factory", 40), ("HTFactory", 60), ("Park", 20),
    ("SHTF", 30), ("OWNF", 1234), ("Mountain", 25), ("Gold", 10), ("Forest", 77),
    ("Newtown", 150), ("Bigtown", 333), ("Bettown", 500), ("Skycity", 600), ("Rizort", 80),
    ("Kajino", 90), ("BigRizort", 70), ("Base", 35), ("Defence", 0), ("Haribote", 0),
    ("Mine", 3), ("Kyujo", 0), ("Kyujokai", 0), ("Zoo", 0), ("Seki", 0),
    ("RottenSea", 5), ("RottenSea", 30), ("Sunahama", 0), ("House", 3), ("Yakusho", 0),
    ("Kura", 1234), ("Kura", 99), ("Kuraf", 10), ("Taishi", 2), ("Taishi", 99),
    ("Train", 5), ("Train", 12), ("Train", 25), ("Monument", 26), ("Monument", 27),
    ("Monument", 73), ("Monument", 86), ("Monument", 87), ("Monument", 17), ("Monument", 93),
    ("College", 77), ("College", 0), ("College", 1), ("College", 2), ("College", 3),
    ("College", 5), ("College", 6), ("College", 7), ("College", 8), ("College", 95),
    ("Plains2", 0), ("Waste", 0), ("Plains", 0), ("Monster", monster(11, 3)),
    ("Monster", monster(21, 2)), ("Monster", monster(23, 9)), ("EneAt", 300), ("EneBo", 150),
    ("EneFw", 200), ("EneCs", 400), ("EneWt", 100), ("EneSo", 120), ("EneWd", 90),
    ("Conden", 500), ("Conden3", 800), ("Conden4", 99),
    # 海のもの
    ("Oil", 0), ("Sbase", 20), ("Fune", 1), ("Fune", 5), ("Fune", 3), ("Nursery", 12),
    ("Umiamu", 44), ("Seacity", 66), ("Frocity", 77), ("Umicity", 300), ("Umishuto", 55),
    ("Seatown", 400), ("Ice", 0),
]

ISLAND2 = [
    ("Town", 10), ("House", 0), ("Monument", 74), ("Monument", 75), ("Monument", 76),
    ("Monument", 77), ("Monument", 78), ("Monument", 79), ("Monument", 84), ("Monument", 96),
    ("Monument", 97), ("Monument", 98), ("Monument", 99), ("Monument", 100), ("Monument", 101),
    ("Monument", 26), ("Monument", 27), ("Monument", 86), ("Monument", 87), ("Monument", 93),
    ("Shuto", 30), ("College", 4), ("College", 96), ("College", 97), ("College", 98),
    ("College", 99), ("College", 78), ("College", 79), ("College", 80),
    ("Monster", monster(28, 1)), ("Monster", monster(30, 4)), ("Monster", monster(13, 7)),
    ("Conden", 100), ("Conden2", 3000), ("Conden3", 50), ("Conden4", 99), ("EneAt", 4000),
    ("EneFw", 100), ("Oil", 0), ("Gold", 3), ("Train", 19), ("Train", 29),
    ("Kyujokai", 0), ("Zoo", 0),
]


def map_lines(cells, size=12):
    flat = [(L[name], value) for name, value in cells]
    # 1 マスは「種類 2 桁 + 値 3 桁」の 16 進なので、値は 0xfff まで
    assert all(0 <= v <= 0xFFF for _, v in flat), [c for c in cells if not 0 <= c[1] <= 0xFFF]
    flat += [(L["Sea"], 1)] * (size * size - len(flat))
    assert len(flat) == size * size, len(flat)
    rows = []
    for y in range(size):
        rows.append("".join(f"{k:02x}{v:03x}" for k, v in flat[y * size:(y + 1) * size]))
    return rows


def rewrite_map(path, cells):
    lines = path.read_bytes().split(b"\n")
    for i, row in enumerate(map_lines(cells)):
        lines[i] = row.encode()
    path.write_bytes(b"\n".join(lines))


def patch_cells(path, cells):
    """Overwrite single cells {(x, y): (kind name, value)} of an island.N map."""
    lines = path.read_bytes().split(b"\n")
    for (x, y), (name, value) in cells.items():
        assert 0 <= value <= 0xFFF
        row = bytearray(lines[y])
        row[x * 5:x * 5 + 5] = f"{L[name]:02x}{value:03x}".encode()
        lines[y] = bytes(row)
    path.write_bytes(b"\n".join(lines))


def set_commands(path, commands, size=12):
    """Replace the first planned commands of an island.N file (kind,target,x,y,arg)."""
    lines = path.read_bytes().split(b"\n")
    for i, cmd in enumerate(commands):
        lines[size + i] = ",".join(str(v) for v in cmd).encode()
    path.write_bytes(b"\n".join(lines))


def set_lines(path, block, per_island, island_pos, offset, values):
    """Replace lines of one island's block in a per-island file (EUC-JP, kept as bytes)."""
    lines = path.read_bytes().split(b"\n")
    for k, v in values.items():
        lines[block + island_pos * per_island + offset[k]] = v.encode()
    path.write_bytes(b"\n".join(lines))


if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)

rewrite_map(DST / "island.1", ISLAND1)
rewrite_map(DST / "island.2", ISLAND2)
# income の 3 つの分岐を通るように:
# 島 1 は農業だけで手一杯、島 2 はハイテク企業・改で働き口が足りる (補助金が増える)、
# 島 3 (元の地図のまま) はミサイル基地の電力消費で電力不足になる
patch_cells(DST / "island.2", {(11, 11): ("SHTF", 30)})
patch_cells(DST / "island.3", {(0, 0): ("Base", 4000)})

# hakojima.dat の島の並び: 3 (箱庭), 1 (テスト), 2 (Alpha)
POS = {3: 0, 1: 1, 2: 2}
MAIN = {"money": 6, "food": 7, "pts": 13, "eis1": 14, "eis2": 15, "eis7": 20,
        "eisei2": 27, "eisei4": 29, "eisei5": 30}
IPS = {"etc5": 16, "etc6": 17, "etc8": 19}
AUC = {"auc0": 0, "auc6": 6, "auc9": 9}
OWNER = {"rena": 5, "totoyoso2": 3}

set_lines(DST / "hakojima.dat", 4, 32, POS[1], MAIN, {
    "money": "5000000", "food": "123456", "pts": "60000", "eis1": "3", "eis2": "7",
    "eisei4": "5,6,7,2,1,0,4,3,2,1,0",
})
set_lines(DST / "hakojima.dat", 4, 32, POS[2], MAIN, {
    "money": "9000000", "pts": "70000", "eis7": "1234", "eisei2": "-5",
    "eisei5": "10,20,30,40,5,6,7",
})
set_lines(DST / "ips.dat", 0, 21, POS[1], IPS, {
    "etc5": ",".join(str(i) for i in [1, 2, 30, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] + [1] * 18),
    "etc8": "1,2,3,4,5,6,7",
})
set_lines(DST / "ips.dat", 0, 21, POS[2], IPS, {
    "etc6": ",".join(str(i % 4) for i in range(31)),
    "etc8": "0,1,0,0,0,0,0",
})
set_lines(DST / "auction.dat", 3, 10, POS[1], AUC, {
    "auc0": "1,2,3,4,5", "auc6": "1,0,0", "auc9": "1,2,30000,4,5",
})
set_lines(DST / "howner.dat", 0, 14, POS[1], OWNER, {"rena": "300", "totoyoso2": "555"})

# 計画: 島 3 は資金・食料の不足で飛ばされる計画のあとに資金繰り、
# 島 1 は放棄、島 2 は連続資金繰りがあと 1 回で自動放棄
COM = {"Monument": 18, "Givefood": 100, "Zoo": 121, "Giveup": 46, "DoNothing": 41}
set_commands(DST / "island.3", [
    (COM["Monument"], 0, 3, 3, 1), (COM["Givefood"], 0, 0, 0, 0), (COM["Zoo"], 0, 4, 4, 0),
])
set_commands(DST / "island.1", [(COM["Giveup"], 0, 0, 0, 0)])
set_lines(DST / "hakojima.dat", 4, 32, POS[2], {"absent": 3}, {"absent": "23"})
print("wrote", DST.relative_to(ROOT))
