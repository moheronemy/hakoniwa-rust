# hakoniwa-rust

Hakoniwa R.A. Final Edition (箱庭諸島2 ver2.30 をもとにした Perl CGI ゲーム) の Rust 移植。

ゲームのルール (ターン処理・計画・災害・ハコオク・toto・Hakoniwa Cup など) は Perl 版のとおりに移植し、
元の Perl コードと同じ入力で動かした結果と突き合わせてある。画面は作り直した。
移植の内容と検証の方法は [docs/PORTING.md](docs/PORTING.md)、運営中の Perl 版からの移行は
[docs/MIGRATION.md](docs/MIGRATION.md)、大規模化 (1000 島・128×128・数十秒ごとのターン) の設計は
[docs/SCALING.md](docs/SCALING.md) を参照。

## 構成

- `crates/hakoniwa-core` — ゲームのルール・データモデル・保存
- `crates/hakoniwa-server` — Web サーバー (axum)
- `crates/hako-convert` — Perl 版のセーブデータを移植版の JSON に変換する
- `hako-r-a_FE/` — 移植元の Perl スクリプト (画像は再配布禁止のためリポジトリに含めない)
- `tools/` — 移植元から定義表を生成するスクリプト、Perl 版と突き合わせるためのハーネスとテストデータの生成

## 使い方

```sh
cargo test --workspace

# Perl 版のデータと設定を変換する (data/hakoniwa.toml も作る。詳しくは docs/MIGRATION.md)
cargo run -p hako-convert -- --settings path/to/hako-main.cgi path/to/perl/data data/state.json

# サーバーを起動する (http://127.0.0.1:8080)。データが無ければ新しいゲームを始める
cargo run -p hakoniwa-server -- --config data/hakoniwa.toml

# セーブデータを JSON に書き出す (中身を確かめるとき、データの形式が変わるとき)
cargo run -p hakoniwa-server -- --config data/hakoniwa.toml --export-json backup.json
```

設定ファイルの例 (書かなかった項目は Perl 版の既定値になる):

```toml
bind = "127.0.0.1:8080"
state_path = "data/state.json"  # 最初の起動で読み込む JSON (hako-convert が書くもの)
# data_dir = "data/store"       # セーブデータの置き場所 (省略時は state_path と同じ場所の store)
tick_secs = 10                # ターンの時刻を確かめる間隔
secure_cookie = false         # HTTPS で公開するなら true
trust_forwarded = false       # リバースプロキシの後ろなら true
# image_dir = "hakoimg"       # Perl 版の画像を持っていれば (無ければ色と文字のタイルで描く)

[game]
title = "☆Hakoniwa R.A.☆"
unit_time = 21600
hide_money_mode = "rounded"   # hidden / visible / rounded
debug = false                 # true でトップページに「ターンを進める」ボタンが出る

[game.passwords]
master = "..."                # 管理画面 (/admin) とすべての島へのログイン。無ければ管理画面も無い
```

## ライセンス

移植元の使用条件 (`hako-r-a_FE/hako-readme.txt`、`hako-r-a_FE/read-renas.txt`) に従う。
とくに、ゲーム画面の最上部に箱庭諸島スクリプト配布元へのリンクを置くこと、
付属の画像を再配布しないことに注意。
