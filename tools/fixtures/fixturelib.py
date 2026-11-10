"""Helpers for building Perl-format fixtures for the Perl comparison tests.

A fixture starts as a copy of tests/fixtures/legacy-turn3 (real data written by the
Perl version: 3 islands, ids 3, 1, 2 in that order in hakojima.dat; the password of island N
is "passN") and is then
edited: maps, planned commands and single values of the per-island data files.

Typical use (see phase2_town.py):

    from fixturelib import Fixture, monster
    f = Fixture("phase2-mything")
    f.map(1, [("Town", 120), ("Plains", 0), ...])   # island id 1, row-major, rest sea
    f.cells(3, {(0, 0): ("Base", 40)})               # patch single cells of island 3
    f.main(1, money=500000, food=-10)                 # hakojima.dat values
    f.commands(1, [(41, 0, 0, 0, 0)])                 # kind,target,x,y,arg
    f.save()

Then: tools/perl-harness/run-harness.sh phase2-mything estimate,eachhex
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "crates/hakoniwa-core/tests/fixtures"
TEMPLATE = FIXTURES / "legacy-turn3"
SIZE = 12

_tables = (ROOT / "crates/hakoniwa-core/src/tables.rs").read_text(encoding="utf-8")
_enum = _tables.split("pub enum LandKind {")[1].split("}")[0]
LAND = {m.group(1): int(m.group(2)) for m in re.finditer(r"(\w+) = (\d+),", _enum)}
_enum = _tables.split("pub enum CommandKind {")[1].split("}")[0]
COMMAND = {m.group(1): int(m.group(2)) for m in re.finditer(r"(\w+) = (\d+),", _enum)}

# hakojima.dat の島の並び (島 ID → 何番目か)
POS = {3: 0, 1: 1, 2: 2}

# 各ファイルの島ごとの行 (先頭の共通部分の行数, 島 1 つあたりの行数, 項目 → 何行目か)
MAIN = (4, 32, {k: i for i, k in enumerate(
    "name id prize absent comment password money food pop area farm factory mountain pts "
    "eis1 eis2 eis3 eis4 eis5 eis6 eis7 eis8 taiji onm monsterlive monsterlivetype "
    "eisei1 eisei2 eisei3 eisei4 eisei5 eisei6".split())})
OWNER = (0, 14, {k: i for i, k in enumerate(
    "id1 ownername totoyoso totoyoso2 kei rena momotan fore pika hamu monta tare zipro leje"
    .split())})
IPS = (0, 21, {k: i for i, k in enumerate(
    "ipname ip0 ip1 ip2 ip3 ip4 ip5 ip6 ip7 ip8 ip9 etc0 etc1 etc2 etc3 etc4 etc5 etc6 etc7 "
    "etc8 etc9".split())})
AUCTION = (3, 10, {f"auc{i}": i for i in range(10)})


def monster(kind, hp):
    """怪獣の地形の値 (種類 << 4 | 体力)"""
    return (kind << 4) | hp


class Fixture:
    def __init__(self, name):
        self.dir = FIXTURES / name
        if self.dir.exists():
            shutil.rmtree(self.dir)
        shutil.copytree(TEMPLATE, self.dir)
        # 島 ID → hakojima.dat の何番目か (add_islands で増える)
        self.pos = dict(POS)

    def _lines(self, file):
        return (self.dir / file).read_bytes().split(b"\n")

    def _write(self, file, lines):
        (self.dir / file).write_bytes(b"\n".join(lines))

    def map(self, island_id, cells, fill=("Sea", 0)):
        """島の地図を行優先で cells (地形名, 値) に置き換える。残りは fill"""
        flat = [(LAND[n], v) for n, v in cells]
        flat += [(LAND[fill[0]], fill[1])] * (SIZE * SIZE - len(flat))
        assert len(flat) == SIZE * SIZE, len(flat)
        self._set_map(island_id, flat)

    def grid(self, island_id, rows, legend):
        """文字の格子で地図を書く。rows は 12 文字 × 12 行、legend は 文字 → (地形名, 値)"""
        assert len(rows) == SIZE and all(len(r) == SIZE for r in rows), rows
        flat = [(LAND[legend[c][0]], legend[c][1]) for r in rows for c in r]
        self._set_map(island_id, flat)

    def _set_map(self, island_id, flat):
        # 1 マスは「種類 2 桁 + 値 3 桁」の 16 進なので、値は 0xfff まで
        bad = [c for c in flat if not 0 <= c[1] <= 0xFFF]
        assert not bad, bad
        lines = self._lines(f"island.{island_id}")
        for y in range(SIZE):
            lines[y] = "".join(f"{k:02x}{v:03x}" for k, v in flat[y * SIZE:(y + 1) * SIZE]).encode()
        self._write(f"island.{island_id}", lines)

    def cells(self, island_id, cells):
        """1 マスずつ書き換える。cells は {(x, y): (地形名, 値)}"""
        lines = self._lines(f"island.{island_id}")
        for (x, y), (name, value) in cells.items():
            assert 0 <= value <= 0xFFF, value
            row = bytearray(lines[y])
            row[x * 5:x * 5 + 5] = f"{LAND[name]:02x}{value:03x}".encode()
            lines[y] = bytes(row)
        self._write(f"island.{island_id}", lines)

    def commands(self, island_id, commands):
        """計画の先頭を (kind, target, x, y, arg) の並びで置き換える"""
        lines = self._lines(f"island.{island_id}")
        for i, cmd in enumerate(commands):
            lines[SIZE + i] = ",".join(str(v) for v in cmd).encode()
        self._write(f"island.{island_id}", lines)

    def _set(self, file, layout, island_id, values):
        head, per, offset = layout
        lines = self._lines(file)
        for k, v in values.items():
            lines[head + self.pos[island_id] * per + offset[k]] = str(v).encode("euc_jp")
        self._write(file, lines)

    def main(self, island_id, **values):
        """hakojima.dat の値 (money, food, pts, eis1..7, eisei1..6 など)"""
        self._set("hakojima.dat", MAIN, island_id, values)

    def owner(self, island_id, **values):
        """howner.dat の値 (rena, totoyoso2 など)"""
        self._set("howner.dat", OWNER, island_id, values)

    def ips(self, island_id, **values):
        """ips.dat の値 (etc0..etc9 など)"""
        self._set("ips.dat", IPS, island_id, values)

    def auction(self, island_id, **values):
        """auction.dat の値 (auc0..auc9)"""
        self._set("auction.dat", AUCTION, island_id, values)

    def turn(self, turn):
        """hakojima.dat の 1 行目 (ターン番号 $HislandTurn) を書き換える"""
        lines = self._lines("hakojima.dat")
        lines[0] = str(turn).encode()
        self._write("hakojima.dat", lines)

    def add_islands(self, count, source=1):
        """島 source を複製して count 島を末尾に足す (ID は次の ID から順に、名前は「複製ID」)。
        hakojima.dat・howner.dat・ips.dat・auction.dat の島の部分と island.N を写す。
        足した島の ID の一覧を返す"""
        main = self._lines("hakojima.dat")
        number, next_id = int(main[2]), int(main[3])
        ids = list(range(next_id, next_id + count))
        for file, (head, per, offset), id_key in (
                ("hakojima.dat", MAIN, "id"), ("howner.dat", OWNER, "id1"),
                ("ips.dat", IPS, None), ("auction.dat", AUCTION, None)):
            lines = self._lines(file)
            trailing = lines[-1] == b""
            if trailing:
                lines = lines[:-1]
            start = head + self.pos[source] * per
            block = lines[start:start + per]
            end = head + number * per
            new = []
            for iid in ids:
                b = list(block)
                if id_key:
                    b[offset[id_key]] = str(iid).encode()
                if file == "hakojima.dat":
                    b[offset["name"]] = f"複製{iid},0".encode("euc_jp")
                if file == "ips.dat":
                    # Perl 版は保存のたびに島の名前を書く
                    b[offset["ipname"]] = f"複製{iid}".encode("euc_jp")
                new += b
            lines = lines[:end] + new + lines[end:]
            if trailing:
                lines.append(b"")
            self._write(file, lines)
        main = self._lines("hakojima.dat")
        main[2] = str(number + count).encode()
        main[3] = str(next_id + count).encode()
        self._write("hakojima.dat", main)
        for k, iid in enumerate(ids):
            shutil.copy(self.dir / f"island.{source}", self.dir / f"island.{iid}")
            self.pos[iid] = number + k
        return ids

    def save(self):
        print("wrote", self.dir.relative_to(ROOT))
