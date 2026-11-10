#!/usr/bin/env python3
"""phase7-long-*: 何十ターンも続けて Perl 版と移植版を突き合わせる (長期の比較) ためのデータとケース。

ケース tests/fixtures/cgi/long-*.json は 1 つに 10〜30 個のリクエストを持つ。ターンのリクエストは
time() を前のターンの 1 ターン (21600 秒) あとにしてあり、Perl 版はリクエストのたびに turnMain を
1 回行う (ターンごとにデータを保存して読み直す。本番と同じ)。そのあいだに計画の入力・政策・
島の登録の画面の操作を挟み、島が発展し続けるようにする。rand() はリクエストごとに並びの先頭から。

操作ごとのデータは snapshots.json.gz に残る (run_cgi.py の "snapshots")。
移植版の側は turn/long_run_tests.rs。

- long-play: legacy-turn3 (ターン 3) に島を 2 つ登録し、ふつうの開発の計画 (整地・埋め立て・農場・
  工場・植林・採掘場・ミサイル基地・ミサイル・資金繰りなど) を入れながら 24 ターン (4〜27)。
  Numbers (10・20 ターン) を通る
- long-mix-100: 全地形を混ぜた 5 島 (政策・人工衛星・怪獣・toto と Numbers の予想入り)、
  ターン 89〜111。ハコオクの終盤 (% 100 > 74)、ターン杯・ハコオクの順位・toto・Numbers3 (100)、
  Hakoniwa Cup の開催 (100)、Numbers4 (90・110) を通る
- long-mix-140: 全地形を混ぜた 5 島 (Hakoniwa Cup のチーム入り)、ターン 136〜160。
  決勝トーナメントのシード (141)、決勝と Hakoniwa Cup toto (150)、Numbers (140・150・160) を通る
- long-mix-200: 怪獣の多い全地形の 6 島、ターン 191〜212 (200 と 210 を通る)

    python3 -I tools/fixtures/phase7_long.py
    for c in long-play long-mix-100 long-mix-140 long-mix-200; do
        python3 -I tools/perl-harness/run_cgi.py crates/hakoniwa-core/tests/fixtures/cgi/$c.json
    done
"""
import contextlib
import io
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import COMMAND, FIXTURES, ROOT, Fixture  # noqa: E402

# phase2_mix / phase3_mix は読み込むと自分の fixture を作り直す (同じ内容になる)。出力は捨てる
with contextlib.redirect_stdout(io.StringIO()):
    from phase2_mix import island_map  # noqa: E402
    from phase3_mix import commands  # noqa: E402

UNIT = 21600
CGI = FIXTURES / "cgi"


def policy(rng):
    """etc5 ($s00..$s30)。先頭が 0 だと estimate が消すので 1 以上 (phase4_mix と同じ)"""
    v = [rng.randrange(1, 4)] + [rng.choice([0, 0, 1, 3, 8, 20, 60]) for _ in range(30)]
    return ",".join(str(x) for x in v)


def rand_list(seed, n, high=256, low=1):
    """rand() の並び。k/256 (k = low..high-1) を n 個。2 進で割り切れるので移植版でも同じ値になる。
    短い並びだと Perl 版が終わらない道筋 (島の地形の生成、隕石のくり返しなど) があるので長めにする"""
    r = random.Random(seed)
    return [f"{r.randrange(low, high) * 390625:08d}" for _ in range(n)]


def last_time(f):
    return int((f.dir / "hakojima.dat").read_bytes().split(b"\n")[1])


def command_form(island_id, password, number, kind, target, x, y, amount, mode="insert"):
    return {"PASSWORD": password, "NUMBER": str(number), "COMMAND": str(kind),
            "AMOUNT": str(amount), "TARGETID": str(target), "POINTX": str(x), "POINTY": str(y),
            "COMMANDMODE": mode, "LAMOUNT1": "0", f"CommandButton{island_id}": "1"}


POLICIES = ["Shouene", "Bousai", "Kankou", "Sizen", "Kyouiku", "Chochiku"]


class Session:
    """リクエストの並びを作る。ターンのリクエストは前のターンの 1 ターンあと、
    画面の操作は直前のターンの数十秒後 (ターンは進まない)"""

    def __init__(self, f, rand):
        self.base = last_time(f)
        self.turns = 0
        self.sub = 0
        self.requests = []
        self.case = {"fixture": f.dir.name, "rand": rand, "snapshots": True, "timeout": 60,
                     "requests": self.requests}

    def _screen(self, form, addr="10.0.0.1"):
        self.sub += 1
        self.requests.append({"time": self.base + self.turns * UNIT + 10 * self.sub,
                              "addr": addr, "form": form})

    def turn(self):
        self.turns += 1
        self.sub = 0
        self.requests.append({"time": self.base + self.turns * UNIT, "form": {}})

    def command(self, island_id, password, number, kind, target, x, y, amount, mode="insert",
                addr="10.0.0.1"):
        self._screen(command_form(island_id, password, number, kind, target, x, y, amount, mode),
                     addr)

    def policy(self, island_id, password, name, amount):
        self._screen({"PASSWORD": password, "AMOUNT": str(amount),
                      f"{name}Button{island_id}": "1"})

    def bid(self, island_id, password, lot, amount):
        self._screen({"PASSWORD": password, "AUCNUMBER": str(lot), "AMOUNT": str(amount),
                      f"AuctionButton{island_id}": "1"})

    def toto(self, island_id, password, message):
        self._screen({"PASSWORD": password, "MESSAGE": message, f"TotoButton{island_id}": "1"})

    def new_island(self, name, owner, password, addr):
        self._screen({"ISLANDNAME": name, "OWNERNAME": owner, "PASSWORD": password,
                      "PASSWORD2": password, "MESSAGE": "よろしく", "NewIslandButton": "1"},
                     addr)

    def save(self, name, allow_errors=()):
        if allow_errors:
            self.case["allow_errors"] = list(allow_errors)
        path = CGI / f"{name}.json"
        path.write_text(json.dumps(self.case, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
        print("wrote", path.relative_to(ROOT))


def mix_fixture(name, seed, turn, extra, sea_ratio=0.25):
    """phase4_mix と同じ作り方の島 (3 島 + 島 1 の複製 extra 島)。島 ID と パスワードの組を返す"""
    rng = random.Random(seed)
    f = Fixture(name)
    f.turn(turn)
    ids = [1, 2, 3] + f.add_islands(extra)
    for island_id in ids:
        cells = island_map(rng, sea_ratio)
        # 文部科学省 (大学 77) が無いと estimate が政策を消す
        cells[rng.randrange(len(cells))] = ("College", 77)
        f.map(island_id, cells)
        f.main(island_id, money=rng.randrange(200000, 3000000), food=rng.randrange(20000, 300000),
               pts=rng.randrange(1000, 80000),
               eis1=rng.randrange(0, 5), eis2=rng.randrange(0, 5), eis3=rng.randrange(0, 5),
               eis4=rng.randrange(0, 5), eis5=rng.randrange(0, 60), eis6=rng.randrange(0, 40),
               eis7=rng.choice([0, 0, 150050, 2000099]), absent=rng.randrange(0, 8))
        f.ips(island_id, etc5=policy(rng),
              etc8=",".join(str(rng.randrange(0, 3)) for _ in range(7)))
        f.commands(island_id, commands(rng, 25))
    passwords = {i: f"pass{i}" if i <= 3 else "pass1" for i in ids}
    return f, rng, passwords


# 手で選んだ「ふつうの」開発の計画
PLAY_KINDS = ["Prepare", "Prepare", "Prepare2", "Reclaim", "Reclaim", "Plant", "Farm", "Farm",
              "Factory", "Factory", "Mountain", "Mine", "Base", "Dbase", "MissileNM", "MissilePP",
              "Minato", "Fune", "Park", "Nursery", "Monument", "Money", "Food", "Propaganda",
              "DoNothing", "SellTree", "Destroy", "Seacity", "House", "Newtown", "College",
              "Kura", "Eisei"]


def random_commands(s, rng, passwords, count, kinds=None, targets=None):
    ids = sorted(passwords)
    for _ in range(count):
        island_id = rng.choice(ids)
        kind = COMMAND[rng.choice(kinds)] if kinds else rng.choice(
            [k for n, k in COMMAND.items()
             if n not in {"Zoo", "Giveup", "Ijiri", "DoNothing"} and not n.startswith("Auto")])
        s.command(island_id, passwords[island_id], rng.randrange(0, 6), kind,
                  rng.choice(targets or ids), rng.randrange(1, 11), rng.randrange(1, 11),
                  rng.choice([0, 0, 1, 2, 3, 5]))


# ---- long-play ---------------------------------------------------------------------------
rng = random.Random(7001)
f = Fixture("phase7-long-play")
for island_id in (1, 2, 3):
    # legacy-turn3 の島は資金繰りが 23 ターン続いていて、次のターンに放棄される
    f.main(island_id, absent=0, money=rng.randrange(20000, 60000), food=rng.randrange(20000, 50000))
    f.commands(island_id, [(COMMAND[rng.choice(PLAY_KINDS)], rng.choice([1, 2, 3]),
                            rng.randrange(1, 11), rng.randrange(1, 11), rng.choice([0, 1, 2]))
                           for _ in range(20)])
f.save()
s = Session(f, rand_list(1, 97))
s.new_island("四番島", "四", "pw4", "10.4.4.4")
s.new_island("五番島", "五", "pw5", "10.5.5.5")
# 登録したばかりの島は計画が資金繰りだけで、数ターンで放棄される。計画を入れておく
for island_id, password in ((4, "pw4"), (5, "pw5")):
    for n in range(10):
        s.command(island_id, password, n, COMMAND[rng.choice(PLAY_KINDS)], rng.choice([1, 2, 3]),
                  rng.randrange(1, 11), rng.randrange(1, 11), rng.choice([0, 1, 2]), mode="write",
                  addr=f"10.{island_id}.{island_id}.{island_id}")
play = {1: "pass1", 2: "pass2", 3: "pass3", 4: "pw4", 5: "pw5"}
for t in range(24):
    random_commands(s, rng, play, rng.randrange(1, 4), PLAY_KINDS)
    if t % 6 == 3:
        island_id = rng.choice(sorted(play))
        s.policy(island_id, play[island_id], rng.choice(POLICIES), rng.choice([5, 10, 30]))
    s.turn()
s.save("long-play")

# ---- long-mix-100 ------------------------------------------------------------------------
f, rng, pw = mix_fixture("phase7-long-mix-100", 7100, 88, 2)
for island_id in pw:
    f.main(island_id, eis8=rng.choice(["(toto@1.2.3.4.5.0.0.0)(n3@749)", "(n4@4999)",
                                       "(toto@3.1.2.5.4.0.0.0)(n4@1234)(n3@100)", ""]))
f.auction(1, auc9="3,0,30000,0,0")
f.save()
s = Session(f, rand_list(2, 101))
for t in range(23):
    random_commands(s, rng, pw, rng.randrange(0, 3))
    if t % 7 == 2:
        island_id = rng.choice(sorted(pw))
        s.policy(island_id, pw[island_id], rng.choice(POLICIES), rng.choice([0, 20, 50]))
    s.turn()
# リクエスト 26 (ターン 100) は、ターンの処理と保存のあとのトップページの表示 (hako-top.cgi 1068 行の
# 失業率の計算) がゼロ除算で止まる (表示する島の人口が空)。データは保存済み
s.save("long-mix-100", allow_errors=[26])

# ---- long-mix-140 ------------------------------------------------------------------------
f, rng, pw = mix_fixture("phase7-long-mix-140", 7140, 135, 2)
for island_id in pw:
    # Hakoniwa Cup のチーム (攻撃,守備,キーパー,勝,分,負,通算勝,通算分,通算負,優勝回数,段階)
    a, d, k = (rng.randrange(10, 80) for _ in range(3))
    w, l = rng.randrange(0, 4), rng.randrange(0, 3)
    f.main(island_id, eisei4=f"{a},{d},{k},{w},0,{l},{w},0,{l},0,{rng.randrange(1, 10)}",
           eis8=rng.choice(["(hc@1.2)(n4@4999)", "(hc@3.1)(n3@500)", "(hc@2.4)", ""]))
    f.cells(island_id, {(5, 5): ("Kyujokai", 0)})
f.save()
s = Session(f, rand_list(3, 103))
for t in range(25):
    random_commands(s, rng, pw, rng.randrange(0, 3))
    s.turn()
s.save("long-mix-140")

# ---- long-mix-200 ------------------------------------------------------------------------
f, rng, pw = mix_fixture("phase7-long-mix-200", 7200, 190, 3, sea_ratio=0.35)
f.save()
s = Session(f, rand_list(4, 107))
for t in range(22):
    random_commands(s, rng, pw, rng.randrange(0, 4))
    s.turn()
s.save("long-mix-200")

# ---- long-auction-300 --------------------------------------------------------------------
f, rng, pw = mix_fixture("phase7-long-auction-300", 7300, 269, 4)
f.save()
s = Session(f, rand_list(5, 127))
AUCTION = COMMAND["Auction"]
for t in range(31):
    random_commands(s, rng, pw, rng.randrange(0, 3))
    turn = 270 + t
    for island_id in rng.sample(sorted(pw), 2):
        if turn % 100 <= 75:
            s.toto(island_id, pw[island_id], rng.choice([
                "(toto@1.2.3.4.5.6.7.0)(n3@" + str(rng.randrange(1000)) + ")",
                "(n4@" + str(rng.randrange(10000)) + ")(toto@7.6.5.4.3.2.1.0)", "(n3@5)"]))
        if rng.random() < 0.5:
            s.command(island_id, pw[island_id], 0, AUCTION, island_id, rng.randrange(12),
                      rng.randrange(12), rng.randrange(0, 4))
        s.bid(island_id, pw[island_id], rng.randrange(1, 4), rng.randrange(1, 6))
    s.turn()
s.save("long-auction-300")

# ---- long-disaster ----------------------------------------------------------------------
# 乱数を小さい値に寄せる (災害・怪獣の出現が増える)。
f, rng, pw = mix_fixture("phase7-long-disaster", 7400, 60, 2, sea_ratio=0.2)
f.save()
s = Session(f, rand_list(7, 131, high=128))
for t in range(20):
    random_commands(s, rng, pw, rng.randrange(1, 4))
    s.turn()
s.save("long-disaster")

# ---- long-growth ------------------------------------------------------------------------
# 乱数を大きい値に寄せる (災害が少なく、成長が続く)。ターン 11〜40 (30 ターン)
f, rng, pw = mix_fixture("phase7-long-growth", 7500, 10, 1, sea_ratio=0.4)
f.save()
s = Session(f, rand_list(8, 137, low=112))
for t in range(30):
    random_commands(s, rng, pw, rng.randrange(0, 3))
    s.turn()
s.save("long-growth")
