#!/usr/bin/env python3
"""元の Perl CGI (hako-main.cgi) に画面の操作 (POST) を送り、操作のあとのデータを残す。

画面からの操作 (島の登録・計画の入力・掲示板・名前の変更など) を Rust 版と突き合わせるため、
Perl 版を本物の CGI として動かす。rand() と time() は固定する。

    python3 -I tools/perl-harness/run_cgi.py CASE.json

CASE.json (tests/fixtures/cgi/ に置く):

    {
      "fixture": "legacy-turn3",          # 元にするデータ (tests/fixtures/ の下)
      "time": 1794290500,                  # time() の値 (省略時はデータの最終更新時刻 + 1)
      "rand": "50",                        # rand() を 0.50 に固定 (省略時は 0)。
                                           # ["5", "25", ...] のように並べると、各操作で
                                           # rand() が先頭から順にその値を返す (最後まで行けば先頭へ)
      "requests": [
        {"form": {"ISLANDID": "1", "PASSWORD": "p", "MESSAGE": "やあ", "CommentButton1": "1"},
         "addr": "10.0.0.1", "query": "", "cookie": ""}
      ]
    }

form の値は UTF-8 で書く (EUC-JP にして URL エンコードする)。Perl 版の cgiInput は
「キー=値&」の形を正規表現で探すので、最後の項目にも & を付けて送る。

出力は CASE.json と同じ場所の CASE/ ディレクトリ:
    before/      操作の前のデータ (fixture をそのまま複製)
    after/       すべての操作のあとのデータ
    response<N>.html   N 番目の操作の応答 (Shift_JIS から UTF-8 にしたもの)

長く続けて動かすケース (tests/fixtures/cgi/long-*.json) 用の追加の項目:

    "snapshots": true          # 操作ごとのデータを snapshots.json.gz に残す (応答の HTML は残さない)
    "timeout": 120             # 1 つの操作の制限時間 (秒)
    "allow_errors": [3]        # Perl 版がデータを保存したあとで止まる操作 (画面の表示のゼロ除算など)
    "requests": [{"time": ..., "rand": [...], "form": {...}}]
                               # 操作ごとの time() と rand() (rand の既定はケースの "rand")

snapshots.json.gz は操作ごとの「前の操作のあとから変わったファイル」の並び
([{ファイル名: 内容 (latin-1 で文字列にしたもの) または null (消えたファイル)}, ...])。
1 つ目は before/ からの差分。
"""
import json
import os
import pathlib
import re
import shutil
import gzip
import subprocess
import sys
import tempfile
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "crates/hakoniwa-core/tests/fixtures"
PERL_SRC = ROOT / "hako-r-a_FE"

# rand と time を固定する (CORE::GLOBAL は読み込む前に差し替える必要がある)
PRELUDE = r"""
BEGIN {
    my @r = split /,/, ($ENV{HAKO_RAND} // 0);
    my $i = 0;
    *CORE::GLOBAL::rand = sub { my $n = @_ ? $_[0] : 1; $n = 1 if !$n; $r[$i++ % @r] * $n };
    my $t = $ENV{HAKO_TIME};
    *CORE::GLOBAL::time = sub { $t };
}
"""


def patch_jcode(text: bytes) -> bytes:
    # 今の Perl で動かすための書き換え (docs/PORTING.md「Perl 版を手で動かす」)
    text = re.sub(rb"\bdo (\w+)\(", rb"&\1(", text)
    text = re.sub(rb"defined %", rb"%", text)
    return text


def encode_form(form: dict) -> bytes:
    parts = []
    for k, v in form.items():
        parts.append(urllib.parse.quote_from_bytes(str(k).encode("euc-jp"))
                     + "=" + urllib.parse.quote_from_bytes(str(v).encode("euc-jp")) + "&")
    return "".join(parts).encode("ascii")


def rand_env(rand) -> str:
    values = rand if isinstance(rand, list) else [rand]
    return ",".join("0." + str(v) for v in values)


def last_time(data: pathlib.Path) -> int:
    lines = (data / "hakojima.dat").read_bytes().split(b"\n")
    return int(lines[1])


def read_files(data: pathlib.Path) -> dict:
    return {f.name: f.read_bytes().decode("latin-1") for f in sorted(data.iterdir()) if f.is_file()}


def run(case_path: pathlib.Path) -> pathlib.Path:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    out = case_path.with_suffix("")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    src = FIXTURES / case["fixture"]
    shutil.copytree(src, out / "before")

    with tempfile.TemporaryDirectory() as work:
        work = pathlib.Path(work)
        for f in PERL_SRC.glob("*.cgi"):
            shutil.copy(f, work / f.name)
        (work / "jcode.pl").write_bytes(patch_jcode((PERL_SRC / "jcode.pl").read_bytes()))
        (work / "prelude.pl").write_text(PRELUDE)
        shutil.copytree(src, work / "data")
        t = case.get("time") or last_time(work / "data") + 1
        snapshots = case.get("snapshots", False)
        files = read_files(work / "data")
        deltas = []
        for n, req in enumerate(case["requests"]):
            env = {
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "PERL5LIB": str(work),
                "REQUEST_METHOD": "POST",
                "REMOTE_ADDR": req.get("addr", "10.0.0.1"),
                "QUERY_STRING": req.get("query", ""),
                "HTTP_COOKIE": req.get("cookie", ""),
                "HAKO_RAND": rand_env(req.get("rand", case.get("rand", "0"))),
                "HAKO_TIME": str(req.get("time", t)),
            }
            try:
                res = subprocess.run(
                    ["perl", "-I", str(work), "-e",
                     "do './prelude.pl'; $0 = 'hako-main.cgi'; do './hako-main.cgi'; die $@ if $@;"],
                    input=encode_form(req.get("form", {})), cwd=work, env=env,
                    capture_output=True, timeout=case.get("timeout", 120))
            except subprocess.TimeoutExpired:
                sys.exit(f"request {n} timed out (rand の並びによっては Perl 版が終わらない)")
            # 画面は Shift_JIS で出力される (out の jcode::sjis)
            html = res.stdout.decode("cp932", errors="replace")
            if not snapshots or res.returncode != 0:
                (out / f"response{n}.html").write_text(html, encoding="utf-8")
            if res.returncode != 0:
                msg = f"request {n} failed: {res.stderr.decode('euc-jp', 'replace')}"
                if n not in case.get("allow_errors", []):
                    sys.exit(msg)
                print(msg, file=sys.stderr)
            if snapshots:
                now = read_files(work / "data")
                delta = {k: v for k, v in now.items() if files.get(k) != v}
                delta.update({k: None for k in files if k not in now})
                deltas.append(delta)
                files = now
        if snapshots:
            # mtime=0: 作り直しても同じバイト列になるように
            with gzip.GzipFile(out / "snapshots.json.gz", "wb", mtime=0) as f:
                f.write(json.dumps(deltas, ensure_ascii=False).encode("utf-8"))
        shutil.copytree(work / "data", out / "after")
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("wrote", run(pathlib.Path(p).resolve()).relative_to(ROOT))
