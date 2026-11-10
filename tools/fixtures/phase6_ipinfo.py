#!/usr/bin/env python3
"""phase6-ipinfo: 裏ランキング (hako-top2.cgi、IP の重なり) の突き合わせ用データ。

島の並び (保存順) は ID 3 (箱庭), 1 (テスト), 2 (Alpha)。島 1 は放棄 2 ターン目。
ip0 (登録時) .. ip5 (最新) を島どうしで重ねる。空の欄どうしも「同じ IP」に数える。

    python3 -I tools/fixtures/phase6_ipinfo.py
    python3 -I tools/perl-harness/run_cgi.py crates/hakoniwa-core/tests/fixtures/cgi/view-ipinfo.json
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fixturelib import Fixture  # noqa: E402

f = Fixture("phase6-ipinfo")
f.main(1, absent=2)
IPS = {
    # 島 3: 登録時と最新 1 つが島 2 の登録時と同じ
    3: ["10.0.0.9", "10.0.0.3", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.9"],
    # 島 1: 登録時が島 3・島 2 と同じ。島 2 と 2 か所、最新は空 (島 2 の最新も空)
    1: ["10.0.0.9", "10.0.0.1", "10.0.0.7", "10.0.0.7", "10.0.0.8", ""],
    # 島 2
    2: ["10.0.0.9", "10.0.0.7", "10.0.0.2", "10.0.0.2", "10.0.0.2", ""],
}
for island_id, ips in IPS.items():
    f.ips(island_id, **{f"ip{i}": v for i, v in enumerate(ips)}, ip6="10.0.0.9", ip7="0",
          ip8=island_id, ip9=island_id * 10)
f.save()
