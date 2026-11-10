# Perl 版からの移行手順

運営中の Perl 版 Hakoniwa R.A. (`hako-main.cgi` ほか) を、この移植版 (`hakoniwa-server`) に
置き換える手順。ゲームのデータ (島・地形・計画・ログ・記録・ハコオク・アンケート) と、
`hako-main.cgi` の設定 (ターンの長さ・島の数・掲示板・資金の見せ方・災害の確率・パスワードなど) を移せる。
プレイヤーはいまのパスワードのままログインできる。

## 1. 用意するもの

- Rust (stable) でビルドした `hakoniwa-server` と `hako-convert`
  ```sh
  cargo build --release
  # target/release/hakoniwa-server, target/release/hako-convert
  ```
- Perl 版のデータディレクトリ (`$HdirName`、ふつうは `data/`。`hakojima.dat` があるところ)
- Perl 版の `hako-main.cgi` (設定を読むため。EUC-JP のままでよい)
- (任意) Perl 版の地形の画像 (`hakoimg/` の `land0.gif` など)。移植元の著作物で再配布できないので
  移植版には入っていない。持っていれば使える (下記 4)

## 2. Perl 版を止めてデータを写す

データを書き換えられないように Perl 版を止めてから (CGI を置き換える、`.htaccess` で閉じるなど)、
データディレクトリを丸ごと複製する。移行は複製に対して行うので、元のデータは変わらない
(うまくいかなければ Perl 版をそのまま再開できる)。

ターンの時刻の途中で止めれば、移植版は同じ時刻から続きのターンを進める。

## 3. 変換する

```sh
hako-convert --settings path/to/hako-main.cgi path/to/data-copy new/state.json
```

- `new/state.json` — 移植版のセーブデータ (JSON)。サーバーは最初の起動のときにこれを読み込み、
  データディレクトリ (既定では `new/store/`) に移す。以後はデータディレクトリだけを使う
- `new/hakoniwa.toml` — サーバーの設定ファイル (`--config-out` で場所を変えられる)。
  Perl 版の設定を移したもの。**パスワードが平文で入る**ので、ファイルの権限に気をつける
- 読めなかった値や形式の違うデータは「警告」として出る。島の数・ターン数が合っているか確かめる

止めていた時間が 1 ターンより長いと、移植版のサーバーは起動したときに止めていた間のターンを
すべて処理する (Perl 版は次のアクセスのときに 1 ターンずつ進めていた)。その間を飛ばしたければ
`--skip-missed-turns` を付ける (最終更新時刻を、ターンの区切りの位置を保ったまま進める)。

データの形式 (`$HnewGame`)、島の大きさ、計画の数、掲示板の行数は `--settings` の設定から決まる。
設定を渡さないときは、Perl 版の配布時の値として読む (`--island-size` などで指定もできる)。

## 4. 設定を確かめる

`hakoniwa.toml` の先頭はサーバーの設定:

```toml
bind = "127.0.0.1:8080"        # 待ち受けるアドレス
state_path = "new/state.json"  # 最初の起動で読み込む JSON のセーブデータ
# data_dir = "new/store"       # データディレクトリ (省略時は state_path と同じ場所の store)
tick_secs = 10                 # ターンの時刻を確かめる間隔 (秒)
secure_cookie = true           # HTTPS で公開するなら true (ログインのクッキーに Secure を付ける)
trust_forwarded = true         # リバースプロキシの後ろに置くなら true (X-Forwarded-For を接続元にする)
image_dir = "path/to/hakoimg"  # Perl 版の画像を持っていれば。無ければ地図は色と文字のタイルで描く

[game]
# hako-main.cgi から移した設定 (書かなかった項目は配布時の値)
```

- `[game.passwords] master` — マスターパスワード。管理画面 (`/admin`) と、すべての島へのログインに使える。
  Perl 版の値が入っているので、**公開前に変える**ことを勧める (使わないなら消す。消すと管理画面も無くなる)
- `special`, `shuto`, `ip`, `omamori`, `ijiri` — 名前変更の画面で使う管理用パスワード。使わないなら消す
- 見た目だけの設定 (色・タグ・画像のパス) は移していない (画面は作り直している)

## 5. 起動する

```sh
hakoniwa-server --config new/hakoniwa.toml
```

`http://<bind>/` でトップページが出る。外に公開するときは nginx などのリバースプロキシで HTTPS にして、
`secure_cookie` と `trust_forwarded` を true にする。systemd で動かす例:

```ini
[Service]
ExecStart=/opt/hakoniwa/hakoniwa-server --config /opt/hakoniwa/hakoniwa.toml
WorkingDirectory=/opt/hakoniwa
User=hakoniwa
Restart=on-failure
```

保存はデータディレクトリ (`data_dir`) に行う ([SCALING.md](SCALING.md) の手順 3):

- `snapshot.bin` — 状態のスナップショット (ターンのたびに書き直す)
- `journal-<世代>.bin` — そのあとの画面の操作の差分 (操作のたびに追記する)
- `logs/` — ターンごとのログ
- `backup<N>/` — ターン処理で `$HbackupTurn` ターンおきに `$HbackupTimes` 個まで残すバックアップ

動かしたままディレクトリを複製すると、スナップショットと差分の組が合わないことがある。
外にバックアップを取るときは `backup<N>/` を複製するか、JSON に書き出す
(`hakoniwa-server --config ... --export-json backup.json`。動かしたままでも読める)。
書き出した JSON は、データディレクトリを消して `state_path` に置けば次の起動で読み込まれる
(移植版を新しい版にしてデータの形式が変わったときも、この手順で移す)。

## 6. 確かめる

- トップページの島の順位・ターン数・残り時間が Perl 版と同じか
- 自分の島にいまのパスワードでログインできるか
- (管理者) `/admin` にマスターパスワードで入れるか、バックアップが見えるか

## プレイヤーにとっての違い

- ログインは 1 回だけ。以後はクッキーで開発画面を開ける (Perl 版はパスワードをクッキーに保存していた)
- Perl 版のパスワードは先頭 8 文字しか見ていなかった。移行後の最初のログインで、入力したとおりの
  パスワードが新しい形式で保存される (以後は入力したものすべてが照合される)
- 画面は作り直している (ゲームのルール・数値・確率は Perl 版と同じ)

## 移さないもの

- アクセスログ (`axes-hako.log`)、ロックファイル、クッキー
- Perl 版の負荷計測のログ
- 見た目の設定 (色・タグ・画像のパス・JavaScript)
