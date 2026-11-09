# hakoniwa-rust

Hakoniwa R.A. Final Edition (箱庭諸島2 ver2.30 をもとにした Perl CGI ゲーム) の Rust 移植。

まだ土台の段階で、ターン処理や開発画面は移植していない。計画と進み具合は [docs/PORTING.md](docs/PORTING.md) を参照。

## 構成

- `crates/hakoniwa-core` — ゲームのルール・データモデル・保存
- `crates/hakoniwa-server` — Web サーバー (axum)
- `crates/hako-convert` — Perl 版のセーブデータを移植版の JSON に変換する
- `hako-r-a_FE/` — 移植元の Perl スクリプト (画像は再配布禁止のためリポジトリに含めない)
- `tools/` — 移植元から定義表を生成するスクリプト

## 使い方

```sh
cargo test --workspace

# Perl 版のデータを変換する
cargo run -p hako-convert -- path/to/perl/data data/state.json

# サーバーを起動する (http://127.0.0.1:8080)
cargo run -p hakoniwa-server -- --config hakoniwa.toml
```

設定ファイルの例 (書かなかった項目は Perl 版の既定値になる):

```toml
bind = "127.0.0.1:8080"
state_path = "data/state.json"

[game]
title = "☆Hakoniwa R.A.☆"
unit_time = 21600
hide_money_mode = "rounded"   # hidden / visible / rounded

[game.passwords]
master = "..."
```

## ライセンス

移植元の使用条件 (`hako-r-a_FE/hako-readme.txt`、`hako-r-a_FE/read-renas.txt`) に従う。
とくに、ゲーム画面の最上部に箱庭諸島スクリプト配布元へのリンクを置くこと、
付属の画像を再配布しないことに注意。
