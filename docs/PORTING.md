# Hakoniwa R.A. Rust 移植計画

移植元: `hako-r-a_FE/` (Hakoniwa R.A. Final Edition、箱庭諸島2 ver2.30 ベースの Perl CGI)

## 方針 (決定事項)

| 項目 | 決定 |
|---|---|
| 実行形態 | 常駐する Web サーバー (axum)。ロックはプロセス内の `RwLock` で行い、Perl 版のファイルロック (`hakolock1`〜`4`) は移植しない |
| セーブデータ | 移植版は JSON (`state.json`) で保存する。Perl 版のデータは変換ツール `hako-convert` で取り込む |
| 忠実度 | ゲームのルール (計算式・確率・処理順) は Perl 版と同じにする。画面 (HTML) は作り直す |

## 構成

```
crates/
  hakoniwa-core/    ゲームのルール・データモデル・保存 (ライブラリ)
    src/config.rs   設定値 (Perl 版の「各種設定値」)            … 済
    src/tables.rs   地形・計画・怪獣などの定義表 (自動生成)      … 済
    src/model.rs    セーブデータのモデル                         … 済
    src/storage.rs  JSON の読み書き (一時ファイル + rename)      … 済
    src/legacy.rs   Perl 版データの読み込み                      … 済
    src/perl.rs     Perl の挙動の再現 (int(), == '' など)        … 済
    tests/fixtures/legacy-turn3/  Perl 版で作った実データ
  hakoniwa-server/  Web サーバー (いまはトップページの表示だけ)
  hako-convert/     Perl 版データ → state.json の変換ツール
tools/
  gen-tables.sh     hako-main.cgi から tables.rs を再生成する
```

`tables.rs` は手で書き写さず、Perl に設定部分を実行させて値を取り出している
(`tools/gen-tables.sh`)。Perl 側の値を変えたらこれを流し直す。

## 移植元の概要

| ファイル | 行数 | 関数 | 内容 |
|---|---:|---:|---|
| `hako-main.cgi` | 3,112 | 42 | 設定値、入口 (モード振り分け)、データ読み書き、CGI 入力、ロック、共通部品 |
| `hako-turn.cgi` | 20,637 | 334 | ターン処理、計画の実行、島の登録、名前変更。うち 281 個はログの文面 (`log*`) |
| `hako-map.cgi` | 4,325 | 54 | 開発画面・観光画面、地図表示、計画入力、ローカル掲示板、ハコオク、toto など |
| `hako-top.cgi` | 2,488 | 40 | トップページ、各種ランキング (`islandSort*`)、発見・Cup・ハコオクのログ表示 |
| `hako-top2.cgi` | 688 | 5 | トップページの別表示 (IP 一覧) |
| `hako-mente.cgi` | 328 | 12 | 管理ツール (新規ゲーム、削除、バックアップ復元、時刻変更) |
| `history.cgi` | 194 | 6 | 過去ログの表示 |

文字コードは EUC-JP、改行は CRLF と LF が混在。`hako-map.cgi` には NEC 特殊文字
(0xADA3 など) が含まれていて、`iconv -f EUC-JP` は失敗する (`encoding_rs` や CP51932 なら読める)。

大きな関数:

| 関数 | 行数 | 内容 |
|---|---:|---|
| `doEachHex` | 7,599 | 地形 1 マスごとのターン処理 (人口増減、怪獣の移動、施設の動作など) |
| `doCommand` | 5,171 | 開発計画 1 件の実行 |
| `doIslandProcess` | 2,574 | 島全体の処理 (災害、怪獣の出現、賞など) |
| `estimate` | 926 | 人口・面積・農場規模などの集計 |
| `turnMain` | 800 | ターン処理の全体の流れ |
| `tempTopPage` | 2,088 | トップページの HTML |

## Perl → Rust 対応表

| Perl | 移植先 | 状態 |
|---|---|---|
| 設定値 (`hako-main.cgi` 1〜1240 行) | `core::config`, `core::tables` | 済 |
| `readIslandsFile`, `readIsland` | `core::legacy::import_dir` | 済 |
| `writeIslandsFile`, `writeIsland`, `writeIslandsOwner` | `core::storage::save` (JSON) | 済 (Perl 形式への書き出しはしない) |
| `logFilePrint`, `historyPrint`, `hcPrint`, `aucPrint` | `core::model::Logs` + サーバーの画面 | データは済、画面は一部 |
| `hakolock*`, `unlock` | サーバーの `RwLock` | 済 (不要) |
| `random`, `int`, `htmlEscape`, `aboutMoney` | `core::perl`, `core::model::money_for_others` | 済 |
| `cgiInput`, `cookieInput`, `cookieOutput` | axum のルーティングとフォーム | 未 |
| `encode`, `checkPassword` | パスワード照合 | 未 (下記「パスワード」) |
| `turnMain` | `core::turn` | 未 |
| `estimate`, `income`, `countGrow`, `doIslandunemployed` | `core::turn` | 未 |
| `doEachHex` | `core::turn::hex` (地形ごとに分割) | 未 |
| `doCommand` | `core::command` (計画ごとに分割) | 未 |
| `doIslandProcess`, `wideDamage`, `wideDamageli` | `core::turn::island`, `core::disaster` | 未 |
| `makeRandomPointArray`, `randomArray`, `countAround`, `expToLevel`, `monsterSpec`, `nameToNumber` | `core::util` など | 未 |
| `newIslandMain`, `makeNewIsland`, `makeNewLand` | `core::island::create` | 未 |
| `changeMain`, `changeOwner` | `core::island` | 未 |
| `log*` (281 個の文面) | `core::log` (ログを enum で持ち、文面は表示時に作る) | 未 |
| `tempTopPage`, `islandSort*` | サーバーのトップページ・ランキング | 一部 (順位表のみ) |
| `islandInfo`, `islandMap`, `landString`, `landName`, `tempOwner`, `tempCommand`, `commandMain` | サーバーの開発画面・観光画面 | 未 |
| `localBbsMain` ほか掲示板 | サーバーの掲示板 | 未 |
| `auctionMain`, `totoMain`, `changeAnkeito`, `msMain` ほか | サーバーの各機能 | 未 |
| `hako-mente.cgi` | 管理画面または CLI | 未 (新規ゲームはサーバー起動時に自動作成) |

## 移植で気をつける点

Perl 版の書き方の癖で、そのまま読むと挙動を見誤りやすいもの:

- **`$x == ''` は数値比較。** 「空なら」ではなく「数値として 0 なら」の意味になる。
  たとえば `'0,0,0,0,0' == ''` は真。`perl::num_eq_empty` を使う。
- **`int()` は寛容。** `int('12abc')` は 12、`int('')` は 0。`perl::int` を使う。
- **正規表現のマッチに失敗すると `$1` などが前回の値のまま残る。** 元のコードはこれを
  前提にしていない箇所が多い。移植ではマッチ失敗を明示的に扱い、挙動が変わる箇所はコメントに残す。
- **同名の関数は後の定義が勝つ。** `hako-turn.cgi` の `countAround` (2 つとも同じ内容) と、
  `hako-top.cgi` の `topPageMain` (2 つ目のアクセスログを取るほうが有効)。
- **グローバル変数だらけ。** `@Hislands`、`%HidToNumber`、`$HcurrentID` などを関数間で暗黙に共有している。
  移植ではターン処理の文脈を表す構造体に集めて明示的に渡す。
- **数値は倍精度浮動小数点。** 大きな値は整数の範囲を超えて丸められたり、`1e+20` のような
  表記で保存されたりする。移植版は `i64` を使い、桁あふれは `saturating_*` で止める (必要なら記録する)。
- **カンマ区切りの複合値。** `etc5`〜`etc9`、`auc*`、`eisei3`〜`eisei6`、`factory`、`prize` などは
  1 つの文字列に複数の値を詰めている。いまは文字列のまま持ち、使っている処理を移植するときに型を付ける。
- **乱数。** 乱数の並びは Perl 版と一致させられない。ルールの検証は、乱数を固定したテストと、
  Perl 版との統計的な比較 (災害の発生率など) で行う。
- **ソートの安定性。** Perl 5.8 以降の `sort` は安定 (同順位は元の順を保つ)。Rust でも `sort_by` (安定) を使う。

## パスワード

Perl 版はパスワードを `crypt($pw, 'h2')` (伝統的な DES crypt) で保存している。
移行したプレイヤーがそのままログインできるよう、照合だけは DES crypt に対応させる
(`pwhash` クレートの `unix_crypt` など)。新しく設定するパスワードは argon2 などで保存し、
DES の値はログイン成功時に置き換える。

## 検証の方法

Perl 版を手元で動かし、同じ操作をした結果を比べる。`tests/fixtures/legacy-turn3/` はこの方法で作った。

1. `hako-r-a_FE/` の `*.cgi` と `jcode.pl` を作業用ディレクトリにコピーする
2. 今の Perl で動かすため、`jcode.pl` の `do 関数名(` を `&関数名(` に、`defined %ハッシュ` を `%ハッシュ` に置き換える
3. `hako-main.cgi` の `$Hdebug = 0;` を `1` にすると、`TurnButton` でターンを進められる
4. 実行例 (POST の本文は最後の項目にも `&` が必要):

```sh
printf 'NEW=1&PASSWORD=<マスターパスワード>&' | REQUEST_METHOD=POST perl hako-mente.cgi
printf 'ISLANDNAME=...&OWNERNAME=...&MESSAGE=...&PASSWORD=p&PASSWORD2=p&NewIslandButton=1&' \
  | PERL5LIB=. REQUEST_METHOD=POST REMOTE_ADDR=10.0.0.1 perl hako-main.cgi
printf 'TurnButton=1&' | PERL5LIB=. REQUEST_METHOD=POST perl hako-main.cgi
```

日本語の値は EUC-JP で URL エンコードして渡す。島は連続資金繰りが続くと数ターンで放棄されるので、
長くターンを回すときは計画も入力する。

## 進め方

- [x] **0. 土台** — workspace、設定値、定義表、データモデル、JSON 保存、Perl 版データの変換、トップページの表示
- [ ] **1. ターン処理の骨格** — `turnMain` の流れ、`estimate`、`income`、食料消費、連続資金繰りと自動放棄、
      ログの保存とローテーション、バックアップ、サーバーでの定時実行
- [ ] **2. 地形ごとの処理** — `doEachHex` を地形の種類ごとに分けて移植
- [ ] **3. 計画の実行** — `doCommand` を計画の種類ごとに分けて移植
- [ ] **4. 島全体の処理** — `doIslandProcess` (災害、怪獣の出現、賞)
- [ ] **5. 画面** — 島の登録、開発画面 (計画の入力)、観光画面、ローカル掲示板、ランキング
- [ ] **6. 付加機能** — ハコオク、toto、アンケート、人工衛星、Hakoniwa Cup、管理機能
- [ ] **7. 移行** — パスワードの互換、本番データの変換手順、Perl 版との比較テスト
