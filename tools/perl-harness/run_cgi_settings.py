#!/usr/bin/env python3
"""run_cgi.py に、Perl 版の設定値を書き換えて動かす機能を足したもの。

    python3 -I tools/perl-harness/run_cgi_settings.py CASE.json

CASE.json に run_cgi.py の項目のほか "perl_settings" を書ける:

    "perl_settings": {"HhideMoneyMode": "1", "viewNumber": "2", "AnkeitoOnOff": "1"}

hako-main.cgi の行頭の `$名前 = 値;` を書き換えた写しで動かす (元のファイルは変えない)。
"""
import json
import pathlib
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_cgi  # noqa: E402


def patched_sources(settings: dict, work: pathlib.Path) -> pathlib.Path:
    src = work / "src"
    shutil.copytree(run_cgi.PERL_SRC, src)
    main = src / "hako-main.cgi"
    text = main.read_bytes()
    for name, value in settings.items():
        pattern = rb"^\$" + re.escape(name.encode()) + rb"\s*=[^;\n]*;"
        text, n = re.subn(pattern, b"$" + name.encode() + b" = " + str(value).encode() + b";",
                          text, count=1, flags=re.M)
        if n != 1:
            sys.exit(f"setting ${name} not found in hako-main.cgi")
    main.write_bytes(text)
    return src


ORIGINAL_SRC = run_cgi.PERL_SRC

if __name__ == "__main__":
    for p in sys.argv[1:]:
        run_cgi.PERL_SRC = ORIGINAL_SRC
        case = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as work:
            run_cgi.PERL_SRC = patched_sources(case.get("perl_settings", {}), pathlib.Path(work))
            print("wrote", run_cgi.run(pathlib.Path(p).resolve()).relative_to(run_cgi.ROOT))
