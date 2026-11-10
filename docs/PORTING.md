# Hakoniwa R.A. Rust 移植計画

移植元: `hako-r-a_FE/` (Hakoniwa R.A. Final Edition、箱庭諸島2 ver2.30 ベースの Perl CGI)

## 方針 (決定事項)

| 項目 | 決定 |
|---|---|
| 実行形態 | 常駐する Web サーバー (axum)。Perl 版のファイルロック (`hakolock1`〜`4`) は移植しない。排他はプロセス内で行い、読み取りは状態のスナップショットを見るだけで待たず、書き込み (画面の操作・ターン処理・管理画面) は 1 本の順番待ちに並ぶ ([SCALING.md](SCALING.md) の手順 2) |
| セーブデータ | 移植版はデータディレクトリ (スナップショット・操作の差分・ターンごとのログ。[SCALING.md](SCALING.md) の手順 3) に保存する。Perl 版のデータは変換ツール `hako-convert` で JSON (`state.json`) にし、サーバーが最初の起動で取り込む |
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
    src/log.rs      ターンログ (Perl 版と同じ HTML の文面)       … フェーズ 1 で使う分
    src/turn/       ターン処理                                   … フェーズ 1
      mod.rs          turnMain の流れ、ターン杯
      estimate.rs     estimate (集計と総合ポイント)
      income.rs       income (収入と食料消費)
      command.rs      doCommand の共通部分、資金繰り、放棄
      ranking.rs      並べ替えと部門賞
      hex/            doEachHex (成長と単ヘックス災害)              … フェーズ 2
        mod.rs          前置き・マスのループ・地形ごとの振り分け・収益ログ
        town.rs         町・港町・海底都市・平地
        hazards.rs      全マス共通の判定 (核融合発電所・漏電・小彗星・火災)
        industry.rs city.rs train.rs leisure.rs stadium.rs special.rs sea.rs monster.rs
                        地形の系統ごと
      perl_compat_tests.rs  Perl 版との突き合わせテスト
    src/land.rs     地形の名前 (landName)・周囲の数え上げ (countAround)
    tests/fixtures/legacy-turn3/  Perl 版で作った実データ
    tests/fixtures/phase1-mix/    突き合わせ用データ (+ *.expected.json.gz)。ほかに phase2-* など
  hakoniwa-server/  Web サーバー (トップページ、ターンの定時実行、デバッグ用のターン進行)
  hako-convert/     Perl 版データ → state.json の変換ツール
tools/
  gen-tables.sh     hako-main.cgi から tables.rs を再生成する
  fixtures/                   突き合わせ用データを作るスクリプト (fixturelib.py と各データ)
  perl-harness/run-harness.sh 元の Perl コードで期待値 (*.expected.json.gz) を作る
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
| `cgiInput`, `cookieInput`, `cookieOutput` | サーバーのフォームとセッション (`pages/`, `session.rs`)、入力の加工は `perl::cgi_text` / `cut_column` | 済 (クッキーにパスワードは入れない) |
| `encode`, `checkPassword` | `core::actions::password` | 済 (下記「パスワード」) |
| `turnMain` | `core::turn::run_turn` (+ `turn::{cup, auction, lottery}`) | 済 (ターン全体を Perl 版と突き合わせ済み) |
| `estimate`, `income` | `core::turn::estimate`, `core::turn::income` | 済 (Perl 版と突き合わせ済み) |
| `doIslandunemployed` | `core::turn::island::migrate` | 済 (Perl 版と突き合わせ済み) |
| `doEachHex` | `core::turn::hex` (地形の系統ごとに分割) | 済 (Perl 版と突き合わせ済み) |
| `doCommand` | `core::turn::command` (計画の系統ごとに分割) | 済 (Perl 版と突き合わせ済み) |
| `doIslandProcess` | `core::turn::island` (段階ごとに分割) | 済 (Perl 版と突き合わせ済み) |
| `wideDamageli` | `core::turn::command::attack::wide_damage_li` | 済 (核ミサイルだけが使う) |
| `wideDamage` | `core::turn::hex::monster::wide_damage` | 済 |
| `makeRandomPointArray`, `randomArray`, `monsterSpec` | `core::turn` | 済 |
| `countAround`, `countGrow`, `landName` | `core::land`, `core::turn::hex::town` | 済 |
| `expToLevel`, `nameToNumber` | `core::turn` など | 未 |
| `newIslandMain`, `makeNewIsland`, `makeNewLand` | `core::actions::create` | 済 (Perl 版と突き合わせ済み) |
| `changeMain`, `changeOwner` | `core::actions::change` | 済 (Perl 版と突き合わせ済み) |
| `commandMain`, `commentMain`, `shoueneMain` ほか政策, `localBbsMain` | `core::actions::{command, owner, policy, lbbs}` | 済 (Perl 版と突き合わせ済み) |
| `logOut`, `logLate`, `logSecret`, `logHistory`, `logFlush` | `core::log::TurnLog` | 済 |
| `log*` (281 個の文面) | `core::log::msg` と各ファイルの文面 (Perl 版と同じ HTML) | 使う分から順に (doEachHex で使う分まで済) |
| `islandSort`, 部門賞の `islandSort*` | `core::turn::ranking` | 済 |
| `tempTopPage`, ランキング表示の `islandSort*` | `core::view::top` + サーバーのトップページ | 済 (Perl 版と突き合わせ済み) |
| `islandInfo`, `islandMap`, `landString`, `tempOwner`, `tempCommand`, `tempRecent` | `core::view::{info, map, owner}` + サーバーの開発画面・観光画面 | 済 (Perl 版と突き合わせ済み) |
| `tempLbbsContents` ほか掲示板の表示 | `core::actions::lbbs::lbbs_posts` + サーバー | 済 |
| `auctionMain`, `totoMain`, `totosMain`, `changeAnkeito`, `msMain`, `ms2Main` | `core::actions::{auction, toto, survey, dispatch}` + サーバー | 済 (Perl 版と突き合わせ済み) |
| `hako-top2.cgi` (IP 情報の裏ランキング) | `core::view::ipinfo` + 管理画面 | 済 (Perl 版と突き合わせ済み) |
| `history.cgi` | サーバーの「最近の出来事」 | 済 |
| `hako-mente.cgi` | サーバーの管理画面 (`/admin`) | 済 (データの状態・最終更新時刻・バックアップの復元と削除・やり直し) |

## 移植で気をつける点

Perl 版の書き方の癖で、そのまま読むと挙動を見誤りやすいもの:

- **`$x == ''` は数値比較。** 「空なら」ではなく「数値として 0 なら」の意味になる。
  たとえば `'0,0,0,0,0' == ''` は真。`perl::num_eq_empty` を使う。
- **`int()` は寛容。** `int('12abc')` は 12、`int('')` は 0。`perl::int` を使う。
- **正規表現のマッチに失敗すると `$1` などは「最後に成功したマッチ」の値になる。** その値は
  ブロック単位の動的スコープで、sub からは呼び出し元のマッチが見え、ブロックを出ると戻る。
  `($a, $b) = ($1, $2)` は失敗すると別の正規表現の値を代入する (前回の `$a` が残るのではない)。
  実際に、Hakoniwa Cup で負けた島の `eisei4` に負の数が入って起きる。`perl::MatchScope` で再現する。
- **同名の関数は後の定義が勝つ。** `hako-turn.cgi` の `countAround` (2 つとも同じ内容) と、
  `hako-top.cgi` の `topPageMain` (2 つ目のアクセスログを取るほうが有効)。
- **グローバル変数だらけ。** `@Hislands`、`%HidToNumber`、`$HcurrentID` などを関数間で暗黙に共有している。
  移植ではターン処理の文脈を表す構造体に集めて明示的に渡す。
- **数値は倍精度浮動小数点。** 大きな値は整数の範囲を超えて丸められたり、`1e+20` のような
  表記で保存されたりする。移植版は `i64` を使い、桁あふれは `saturating_*` で止める (必要なら記録する)。
- **カンマ区切りの複合値。** `etc5`〜`etc9`、`auc*`、`eisei3`〜`eisei6`、`factory`、`prize` などは
  1 つの文字列に複数の値を詰めている。いまは文字列のまま持ち、使っている処理を移植するときに型を付ける。
- **乱数。** 乱数の並びは Perl 版と一致させられない。ルールの検証は、乱数を固定して
  元の Perl コードと突き合わせるテスト (下記「検証の方法」) と、統計的な比較 (災害の発生率など) で行う。
- **途中で並べ替えた配列を、並べ替える前の位置で指す。** `turnMain` は部門賞を決めるために
  `@Hislands` を並べ替えるが、そのあとも並べ替え前の `@order` と `%HidToNumber` を使い続ける。
- **島に入れた一時的な値。** `$island->{'shouhi'}` などは保存されず、ターンの開始時は空。
  `estimate` が 1 ターンに 2 回呼ばれ、2 回目は 1 回目の値を読む (`shouhi` は積み増し)。
  移植版は `IslandScratch` に入れ、ターンの開始時に初期化する。
- **ソートの安定性。** Perl 5.8 以降の `sort` は安定 (同順位は元の順を保つ)。Rust でも `sort_by` (安定) を使う。

## パスワード

Perl 版はパスワードを `crypt($pw, 'h2')` (伝統的な DES crypt。先頭 8 文字だけが効く) で保存している。
移行したプレイヤーがそのままログインできるよう、照合は DES crypt にも対応する (`pwhash`)。
新しく設定するパスワードは SHA-512 crypt で保存し、DES の値はログインに成功したときに置き換える。
マスターパスワード (`passwords.master`) と管理用パスワードは、設定したときだけ使える。

## 検証の方法

### 元の Perl コードとの突き合わせ (自動テスト)

移植した関数は、元の Perl コードそのものを同じ入力で動かした結果と比べる。

1. `tools/fixtures/*.py` が、`fixturelib.py` を使って Perl 形式のデータ
   (`tests/fixtures/<名前>/`) を作る。元にするのは Perl 版で作った `legacy-turn3`
2. `tools/perl-harness/run-harness.sh <名前> <段階>` が、`hako-main.cgi` (設定と関数だけ) と
   `hako-turn.cgi` を読み込み、`rand()` の値と座標の並びを固定して、指定した段階
   (`estimate`, `income`, `commands`, `eachhex`, `process` を並べたもの。`process` は全島の
   doIslandProcess と doIslandunemployed) を島ごとに動かす。
   段階ごとにすべての値とログを `*.expected.json.gz` に書き出す (`rand()` を 0 と 0.5 に固定した 2 通り)
3. `turn::perl_compat_tests` が同じ条件で移植版を動かし、島の値・一時値・地形の値・
   計画・ログが 1 つ残らず一致することを確かめる

| データ | 段階 | 確かめていること |
|---|---|---|
| `phase1-mix` | estimate, estimate, income, commands | 集計・収入・資金繰りと放棄 (ほぼ全地形) |
| `phase2-town` | estimate, eachhex, estimate | 町・平地・火災・漏電・不景気・人口の増減 |
| `phase2-industry*`, `phase2-city*`, `phase2-train`, `phase2-leisure`, `phase2-stadium*`, `phase2-special*`, `phase2-sea`, `phase2-monster*` | estimate, eachhex, estimate | doEachHex の系統ごと |
| `phase2-badfields` | estimate, income, commands, eachhex, estimate | 複合値が正規表現に一致しないとき |
| `phase3-land`, `phase3-build-*`, `phase3-city*`, `phase3-ops-*`, `phase3-attack*`, `phase3-magic*` | estimate, income, commands × n, estimate | doCommand の系統ごと |
| `phase3-mix-1`〜`8` | estimate, income, commands, eachhex, ... (2〜3 ターン分) | 全地形の島に全種類の計画をランダムに入れたもの。rand は 0, 1/32, 1/2, 31/32 |
| `phase4-migrate-*`, `phase4-disaster1*`, `phase4-disaster2-*`, `phase4-upkeep*`, `phase4-auction-*`, `phase4-ending` | process または estimate, income, commands, eachhex, process, estimate | doIslandProcess の段階ごと |
| `phase4-mix-1`〜`6` | estimate, income, commands, eachhex, process, estimate (2 ターン分) | 政策・人工衛星・お守りも入れた全地形の島に全種類の計画。rand は 1/2, 3/4, 31/32 |
| `phase4-policy-1`〜`4` | process | 政策の調整・維持費・食料と資金のあふれの上限 |
| `phase2-mix-1`〜`6` | estimate, income, commands, eachhex, estimate, eachhex, estimate | 全地形を混ぜた島 (系統をまたぐ相互作用)。5, 6 は複合値も壊してある。rand は 0, 1/32, 1/2, 31/32 |
| `size-13-1`, `size-32-1`, `size-128-1`, `size-128-2` | estimate, income, commands, eachhex, process, estimate | 地図の大きさ (`$HislandSize`) を 12 以外にした島。データの `island_size` で大きさを指定する ([SCALING.md](SCALING.md)) |

比べているのは、島の保存される値と一時値、全マスの地形の種類と値、計画、ログ、記録ログ。
`rand()` の固定値は `RANDS="0 03125 50 96875"` のように指定できる (2 進で割り切れる数にすること)。

データを作るときは、まだ移植していない系統の地形を置かないこと (Perl と結果が変わる)。

### Perl 版を手で動かす

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
- [x] **1. ターン処理の骨格** — `turnMain` の流れ、`estimate`、`income`、食料消費、連続資金繰りと自動放棄、
      ログの保存とローテーション、バックアップ、サーバーでの定時実行 (詳細は下記)
- [x] **2. 地形ごとの処理** — `doEachHex` を地形の種類ごとに分けて移植 (詳細は下記)
- [x] **3. 計画の実行** — `doCommand` を計画の種類ごとに分けて移植 (詳細は下記)
- [x] **4. 島全体の処理** — `doIslandProcess` (災害、怪獣の出現、賞)、`doIslandunemployed` (詳細は下記)
- [x] **5. 画面** — 島の登録、開発画面 (計画の入力)、観光画面、ローカル掲示板、ランキング (詳細は下記)
- [x] **6. 付加機能** — ハコオク、toto、アンケート、人工衛星、Hakoniwa Cup、管理機能 (詳細は下記)
- [x] **7. 移行** — パスワードの互換、本番データの変換手順 ([MIGRATION.md](MIGRATION.md))、Perl 版との比較テスト

## フェーズ 1 (ターン処理の骨格) の内容

`turnMain` の処理順はそのまま移植し、まだ移植していない段階には `TODO(フェーズN)` の印を付けた。

| `turnMain` の段階 | 状態 |
|---|---|
| 最終更新時刻・ターン番号・座標の並び・処理順の決定 | 済 |
| 収入・消費 (`estimate` → `income`) | 済 |
| 計画の実行 (`doCommand`) | 済 (フェーズ 3) |
| 成長と単ヘックス災害 (`doEachHex`) | 済 (フェーズ 2) |
| 島全体の処理 (`doIslandProcess`, `doIslandunemployed`) | 済 (フェーズ 4) |
| 部門賞 (20 部門の並べ替え) | 済 |
| 2 回目の `estimate` と死滅判定 | 済 |
| ポイント順の並べ替え、ターン杯 (神殿・神社の祭りを含む) | 済 |
| 無人島の除去 | 済 |
| ハコオク、toto、Numbers3/4、Hakoniwa Cup | フェーズ 6 |
| アンケートの集計リセット | 済 |
| バックアップ、ログの書き出しとローテーション、記録ログの調整 | 済 |

### Perl 版の挙動をそのまま再現しているもの

一見バグに見えるが、ゲームの結果に影響するので Perl 版のとおりにしてある。

- 電力消費 `shouhi` は `estimate` のたびに積み増される (1 ターンに 2 回)
- 火力発電の判定は前回の `estimate` の油田数を見る (1 回目は必ず 0)
- `$island->{'co95'}` は一度も代入されないので、大学 95 による計画の値引きは働かない
- 動物の数の合計 `zookazu` は、`estimate` が代入しない `$z0`〜`$z9` (動物園系の計画が最後に代入した値) を足す
- コンデンサの上限の判定は、地図の最後のマスの値と比べている
- 海底新都市は「海底都市の数」に 2 回数えられる
- 大使館の判定で、存在しない島 ID は先頭の島として扱われる
- 2 回目の `estimate` の時点で人口 0 の島は無人島扱いになるので、`logDead` (人がいなくなった) は出ない
- 複合値の正規表現が一致しなかったときは、前回の値 (別の島の値のこともある) が使われる (`perl::Captures`)

### 移植版で変えたもの

- Perl 版の負荷計測ログ (`負荷計測 CPU(...)`) は出さない
- 複合値の空欄 (`1,,3`) は 0 として書き戻す
- コンデンサの充電で地形の値が小数になる場合は切り捨てる (Perl 版も保存時に切り捨てる)
- ターンは、アクセスのたびではなくサーバーが定期的に (`tick_secs` 秒ごとに) 時刻を確かめて進める。
  止まっていた間の分はまとめて処理する
- バックアップは `data` ディレクトリの名前を変える代わりに、データディレクトリの `backup0/`, `backup1/`, ... に
  ターンの前の状態を書く (スナップショットとログ。ログはハードリンク)。古いものは番号をずらして `$HbackupTimes` 個まで残す

## フェーズ 2 (地形ごとの処理 doEachHex) の内容

`doEachHex` (Perl 版 7,600 行) をすべて移植した。地形の系統ごとに `turn/hex/` のファイルに分け、
どれも元の Perl コードとの突き合わせで値・地形・ログが一致している (上記「検証の方法」)。

| ファイル | 内容 |
|---|---|
| `mod.rs` | 前置き (不景気・人口の増え方)、マスのループ、振り分け、収益ログ |
| `town.rs` | 町・港町・海底都市・平地・ループ先頭の整備 |
| `hazards.rs` | 核融合発電所・漏電・小彗星・火災 |
| `industry.rs` | 畜産・食品加工・発電所・ハイテク企業・森・倉庫・家・防衛施設・油田・浅瀬・砂浜・氷河・関所・役所・金山・遊園地 |
| `city.rs` | 防災都市・ニュータウン・現代都市・海底新都市・輝ける都市・空中都市・海都市・首都・温泉街 |
| `train.rs` | 駅・線路・普通電車・貨物列車 (20 通りの進路を表にまとめた) |
| `leisure.rs` | リゾート・カジノ・動物園・野球場・海あみゅ・腐海・枯死海 |
| `stadium.rs` | 多目的スタジアム (Hakoniwa Cup の予選・決勝トーナメント) |
| `special.rs` | 大学・文部科学省・島営企業・記念碑 (卵の孵化など) |
| `sea.rs` | 海上都市・船舶 |
| `monster.rs` | 怪獣 (特殊能力・硬化・移動・分裂・召喚・地雷・防衛施設の自爆など)、`wideDamage` |

### Perl 版の挙動をそのまま再現しているもの (主なもの)

- 分岐の中のループが外側のマスのループの添字 `$i` を使い回す (卵の孵化のあとは 8 番目のマスから続きになる)
- 分岐が外側の `$landKind` / `$lv` を書き換え、その値で共通の災害判定をする
  (小彗星・腐海・動物園・大学の探索・文部科学省など。腐海が隣のハリボテの地形として燃える)
- 範囲を確かめる前に `$land->[$sx][$sy]` を読む。負の添字は反対側の端になる (防災都市・記念碑 94 は書き込みも反対側の端に行う)
- 船の移動済みの印 `@funeMove`、マスコットの孵化数 `$take` などのグローバル変数が島をまたいで残る
- コンデンサの充電で地形の値が小数になり、ターンの間はそのまま使われる
- 観光は未定義の `$employed` のせいで 1 島しか調べない、カジノはリゾート地の数を数える、など
- 体力の加算が 4 ビットの欄からあふれて怪獣の種類が変わる
- Perl の `random($n)` は `$n` が 0 以下でも乱数を 1 つ使い、負なら 0 以下を返す

一覧は各ファイルの先頭とコメントにある。

### 再現していないもの

- Perl は島の幅を超える添字 (`$land->[12]`) を読むと列を自動で作り、以後の負の添字の意味が変わる。
  ここまでは再現しない (`land::perl_get` の説明を参照)
- 複合値の空欄・未定義の欄は、Perl 版は空文字列のまま書き戻すが、移植版は 0 を書く
- 分岐の中で、同じブロックの前の正規表現が成功していた場合の `$1`.. は、分岐の入口の値として扱う
  (いまのところそうなる箇所は見つかっていない)

### 突き合わせで通っていない道筋

乱数を一定の値に固定するため、「ある乱数では成功し、次の乱数では失敗する」ような組み合わせは
通せないものがある (アールヴの隕石、f02 の多弾頭ミサイル、王蟲の脱皮、電車 16/17/26/27 の中央の進路など)。
詳細は各系統の移植時の記録 (コミットメッセージ) を参照。

### 後のフェーズに渡す値

doEachHex が書き、ほかの処理が読むグローバル変数・一時値:

- `ctx.globals.hex.stadium` (`stsanka`, `yushouflag`, `yushounamber(2)`, `hcturn`) と
  `scratch.hex.stadium.stsankahantei`: turnMain の Hakoniwa Cup・toto、doIslandProcess (フェーズ 4・6)
- `ctx.globals.hex.leisure.{ts, z, taiji}` (`$ts00`.., `$z->{}`, `$taiji->{}`): doIslandunemployed と動物園系の計画 (フェーズ 3・4)
- `ctx.globals.hex.aucflag`: ハコオクの出品 (フェーズ 6)
- `ctx.globals.hex.special.costseisaku`: doCommand も同じ変数を使う (フェーズ 3)
- `monster::wide_damage` (`wideDamage`): 計画 (ミサイルなど) からも使う (フェーズ 3)

## フェーズ 3 (計画の実行 doCommand) の内容

`doCommand` (Perl 版 5,200 行) をすべて移植した。計画の系統ごとに `turn/command/` のファイルに分け、
どれも元の Perl コードとの突き合わせで一致している。全地形の島に全種類の計画をランダムに入れた
`phase3-mix-*` でも、計画の実行と地形ごとの処理を 2〜3 ターン分続けて一致する。

| ファイル | 内容 |
|---|---|
| `mod.rs` | 計画の取り出し、費用の計算と確認、資金繰り、放棄、振り分け、`slideBack` と数量分のくり返し、共通の文面 |
| `land.rs` | 整地・地ならし・埋め立て・港町開発・造船・関所・掘削・温泉掘削・伐採・採掘場整備 |
| `build.rs` | 建設系 (植林・農場・発電所・コンデンサ・食物研究所・牧場・大学・工場・基地・記念碑・ハリボテ・怪獣購入・遊園地・動物園・地雷・養殖場・野球場・海あみゅ・ニュータウン・リゾート地・開発予定・役所・倉庫・電車・防衛施設) |
| `city.rs` | ハイテク技術誘致・自宅建設・輝ける都市・改装・海底基地・海底都市・防災都市化・現代都市・海底新都市・僕の引越し |
| `ops.rs` | 人工衛星 (打ち上げ・修復・破壊砲・レーザー)・ハコオク出品・エサ・食料輸出・資金/食料援助・電力援助・誘致活動 |
| `attack.rs` | ミサイル 7 種・動物派遣・大使派遣 |
| `magic.rs` | 魔術師派遣 |

### Perl 版の挙動をそのまま再現しているもの (主なもの)

- doCommand の中の `next` は、turnMain の `while (doCommand(...) == 0)` に効いて「0 を返した」扱いになる
  (自分の島の怪獣を魔術で攻撃すると、同じターンに次の計画も実行される)
- 地ならし・伐採・食料輸出・援助などは 0 を返し、同じターンに次の計画も実行される
- 怪獣の購入は doCommand の局所変数 `$kind` を書き換える (数量 2 以上だと農場整備の計画が入ることがある)
- ミサイルの防衛施設の判定結果 (`@HdefenceHex`) は発射した島と座標で記録され、別の島でも使い回される
- 不発のあとの発射は数量・資金を確かめ直さないので、どちらも負になりうる
- 援助先の島が存在しないと先頭の島に送られる (ログには予定していた島の番号が出る)
- 衛星レーザーの跡にできる記念碑は、撃った側の島の同じ座標に置かれる
- 改装でチームの能力値を上げるとき、Perl の文字列の `++` で `"06"` は `"07"` になる

一覧は各ファイルの先頭とコメントにある。

### 再現していないもの・突き合わせで通っていない道筋

- 食料輸出の代金は Perl 版ではターンの間だけ資金が小数になることがあるが、移植版はすぐ切り捨てる
- 記念碑の季節ものは実行時の日付で決まる (移植版は UTC、Perl 版はサーバーの時刻) ので突き合わせていない
- 乱数を一つの値に固定するため、「1 回目と 2 回目で結果が違う」組み合わせ (大学のランダム建設の
  一部、エサのマスコット強化の一部、古代遺跡の発見など) は通せない
- 動物園建設は Perl 版が rand 0.5 などで無限ループになるので、rand 0 と 1/32 だけで突き合わせている

### 後のフェーズに渡す値

doCommand が書き、島全体の処理 (フェーズ 4)・turnMain の付加機能 (フェーズ 6) が読むもの:

- `scratch.command.land.prepare2` (地ならしの回数): 地震の確率
- `scratch.command.attack.{monstersend, monstersendkind}`: doIslandProcess が派遣された怪獣を出す
- `scratch.command.build.bigmissile`: doIslandProcess
- `scratch.command.city.{stocklandkind, stocklandvalue}`: doIslandProcess のハコオクの落札処理も書く
- `ctx.globals.command.ops.auction` (`$auction1`..`3`): ターンの開始時に `World::auction_lots` から読み、
  終わりに書き戻す。turnMain のハコオクの処理が読む
- `ctx.globals.etc7` (`$msjotai`, `$nokotan`, `$msid`): doIslandProcess も代入する
- `scratch.propaganda` (誘致活動): doEachHex が読む (済)

## フェーズ 4 (島全体の処理 doIslandProcess) の内容

`doIslandProcess` (Perl 版 2,600 行) と `doIslandunemployed` をすべて移植した。Perl 版は 1 本の長い関数なので、
処理の段階ごとに `turn/island/` のファイルに分け、`mod.rs` から Perl 版と同じ順に呼ぶ。どれも元の
Perl コードとの突き合わせで一致し、全地形・全計画を入れた `phase4-mix-*` でも、ターン全体
(計画・地形ごとの処理・島全体の処理) を 2 ターン続けて一致する。

| ファイル | Perl 版の行 | 内容 |
|---|---|---|
| `mod.rs` | 14570〜14634 | 前置き (政策の分解、怪獣派遣の残りターン、Hakoniwa Cup の開幕、ハイテク企業の維持費、お守りの分解)、段階の呼び出し、共通の文面 |
| `migrate.rs` | 14388〜14569, 14635〜14849 | 失業者の移民・暴動・デモ (doIslandunemployed)、リゾートに飽きた住民の移住 |
| `disaster1.rs` | 14850〜15247 | 地震・重税への反発・食料不足 (宇宙ステーション)・津波・怪獣の出現 |
| `disaster2.rs` | 15248〜15665 | 地盤沈下・台風・巨大隕石・巨大ミサイル・隕石・噴火 |
| `upkeep.rs` | 15666〜15787 | 人工衛星の消耗・イレギュラーの攻撃・宇宙ステーションの維持・天空城 |
| `auction.rs` | 15788〜16957 | ハコオクの落札 (3 枠を 1 つの関数にまとめた) と連続 1 位の賞品 |
| `ending.rs` | 16958〜17143 | 政策の調整と維持費、食料・資金のあふれ (大使館への寄付)、`estimate`、繁栄賞・災難賞、神殿・神社の祭り |

### Perl 版の挙動をそのまま再現しているもの (主なもの)

- `$migrate2` (移民の人数) はグローバル変数で、最初は未定義 (ログに空で出る)。暴動・デモのログは前の島の値を出す
- 上限を超えたマスへの移住は `rand` に負の数を渡すので、移民の数が負になり、元の島の家の値が増える
- 関所で移住を断っても、最初のマスへの移住の処理は走る (平地が値 0 の町になる)
- 金山の地震の被害は、地形ではなくグローバル変数 `$kind` を見ている
- 地盤沈下は沈むマスをいったん -1 にしてから浅瀬にする (マスを見る順で結果が変わる)
- 隕石が防衛施設・改に守られるかは、島の外のマスを未定義の `$kind` と比べて数える
  (`$kind` が 0 = 海なら、島の端に落ちた隕石は必ず守られる)
- 隕石のくり返しは `random(2) == 0` を先に評価するので、1 回目にも乱数を引く
- 天空城の電力の判定はループの前の 1 回だけで、消し飛ばした跡の荒地の値は 1
- ハコオクは最高額と同じ額を入れた島がどれも落札する。補助金の残り `$auc9c3` は 3 枠を通して計算し直さない
- 大使館への寄付は読み込み時の島の位置 (`%HidToNumber`) で相手を探す (並べ替えのあとは別の島になる)
- 賞の判定は `prize` の複合値の正規表現が一致しないと、最後に成功したマッチの値を使う
- 神殿・神社の祭りのログは、前の処理が `$point` に入れた座標を島名の後ろに出す

一覧は各ファイルの先頭とコメントにある。

### 突き合わせで通っていない道筋

- `rand` を 0 に固定すると Perl 版が終わらない道筋がある (隕石のくり返し、イレギュラーのある島など)。
  そのため島全体の処理を含むデータは、多くを 1/2 以上の固定値で突き合わせている
- 隕石が防衛施設・改を壊す・隕石のあとの記念碑・2 回以上の隕石は、「1 回目は小さく、2 回目は大きい」
  乱数が要るので通せない
- 文部科学省 (大学 77) は doEachHex の条件 (大学 0〜8・宇宙ステーション 100 万人・rena) を満たさないと
  役所に戻るので、政策の値が残る道筋は `phase4-policy-*` (島全体の処理だけを回す) で確かめている
- リゾートの移住で `$migrate <= 0` を 1 にする行は、条件の組み合わせ上どちらの分岐でも起きない

### 後のフェーズに渡す値

- `ctx.globals.process.auction` と `World::auction_lots`: turnMain のハコオクの出品の入れ替え (フェーズ 6)
- `logs.hcup` (`logHcup`) と `logs.auction` (`logAuc`): Hakoniwa Cup とハコオクの記録の画面 (フェーズ 5・6)
- `IslandScratch::typhoon`, `roudenflag`: estimate と doEachHex も読む (済)

## フェーズ 5 (画面) の内容

画面は作り直し、データの変え方と「何を見せるか」は Perl 版のとおりにした。

- **ルール (`core::actions`)**: 島の登録・名前とパスワードとオーナー名の変更・計画の入力 (自動入力・
  いじりを含む)・コメント・政策・ローカル掲示板。どれも「入力を受け取って `GameState` を書き換える」関数。
- **表示 (`core::view`)**: トップページ (`top`)、島の情報 (`info`)、地図 (`map`)、開発画面の計画の入力欄と
  計画の一覧 (`owner`)、島の近況 (`recent_logs`)。観光者に隠すもの (資金・森の木の数・基地や地雷の偽装・
  計画の印・政策) も Perl 版のとおり。
- **サーバー (`hakoniwa-server`)**: axum の画面とフォーム。ログインのときに 1 回だけパスワードを確かめ、
  ランダムなトークンを HttpOnly のクッキーに入れる (Perl 版はパスワードをクッキーに入れていた)。
  POST には CSRF 対策のトークンを付ける。データの書き換えは複製に対して行い、保存できたときだけ反映する。
- **地図の画像**: Perl 版の画像は再配布できないので同梱しない。持っている運営者が `image_dir` に置けば使い、
  無ければ地形の種類 (観光者には偽装後の種類) から色と文字のタイルを描く。

### 突き合わせの方法

`tools/perl-harness/run_cgi.py` が元の `hako-main.cgi` を本物の CGI として動かし (`rand()` と `time()` を固定)、
操作の前後の Perl 形式のデータと応答の HTML を `tests/fixtures/cgi/<名前>/` に残す。
操作は `actions::perl_compat_tests::check_case` が前のデータに移植版の操作を加え、後のデータと
比べる (`GameState` 全体)。表示は Perl 版の HTML から値を取り出して、`view` の結果と比べる。

| データ | 確かめていること |
|---|---|
| `cgi/comment-1` | コメント |
| `cgi/new-island-*`, `cgi/change-*` | 島の登録 (地形の生成・上限・名前の規則・同じ接続元)、名前・パスワード・オーナー名の変更、管理用パスワード |
| `cgi/command-*`, `cgi/policy`, `cgi/lbbs` | 計画の入力・自動入力・いじり・IP の記録、政策、掲示板 (公開・極秘・匿名・削除) |
| `cgi/view-*` | 観光画面と開発画面の島の情報と地図 (全地形・偽装・マスターパスワード) |
| `cgi/view-top-*` | トップページ (並べ替え・部門賞・資金の隠し方・ページ送り・アンケート・ハコオク) |
| `cgi/owner-*` | 開発画面の計画の選択肢 (コストの修正)・計画の一覧の文面 |

### 移植版で変えたもの

- 入力の値の中の `&` から後ろが消える (`cgiInput` の読み取りの不具合) のは再現しない
- 島が無い ID の操作は、Perl 版は 1 位の島に対して行ってしまうが、移植版はエラーにする (開発画面・計画・政策)。
  名前の変更とオーナー名の変更は Perl 版のまま (ログイン中の島しか送られないので起きない)
- 計画の番号が範囲外の入力は受け付けない。計画の値は整数で保存する
- パスワードは上記「パスワード」のとおり。いじり (計画 60) はマスターパスワードでログインしたときだけ受け付ける
- アクセスログ (`axeslog`)、ロック、クッキーへのパスワードの保存は移植しない
- トップページの最近の出来事は `top_log_lines` 行まで、最近の出来事 (`history.cgi`) は `history_page_lines` 行ずつの
  ページ送りにした (Perl 版はすべて出す。大規模化のため。[SCALING.md](SCALING.md) の手順 4)。出す行と順は Perl 版のとおり
- 32×32 を超える地図は canvas で描く (`?map=table` で表)

### 後のフェーズに残したもの

ハコオクの入札・出品の画面、toto・首都名、アンケートの投票、怪獣派遣の許可 (`msMain`)、
IP 情報の裏ランキング (`hako-top2.cgi`)、管理画面 (`hako-mente.cgi`) はフェーズ 6。
`view::owner::OwnerScreen` の `auction`・`comment` (toto・首都名・ミサイルの申請) と
`view::top::TopPage` の `survey`・`auction` はすでにあるので、画面を作るときに使う。

## フェーズ 6 (付加機能) の内容

### ターン処理の残り

`turnMain` のうち残っていた部分を移植し、`run_turn` が `turnMain` をすべて再現するようになった。

| ファイル | 内容 |
|---|---|
| `turn/cup.rs` | Hakoniwa Cup の決勝トーナメントの進出 (ターン % 100 == 41) と開催の記録 (ターン % 100 == 0) |
| `turn/auction.rs` | ハコオクの順位と賞品 (ターン杯のターン)、出品の入れ替えと残りターンの更新、読み込み時の既定値 |
| `turn/lottery.rs` | toto、Hakoniwa Cup toto、Numbers3、Numbers4 |

**ターン全体の突き合わせ**: 時刻を最終更新から 1 ターン以上あとにして元の CGI にリクエストを送ると、
Perl 版は `turnMain` をまるごと実行する。`turn/full_turn_tests.rs` はその前後のデータを読み込み、
移植版の `run_turn` の結果と比べる (`tests/fixtures/cgi/turn-*`)。補正は 2 つだけ:
Perl 版の負荷計測のログ (移植版は出さない) と、Hakoniwa Cup の試合のログの「−」の文字
(Perl 版のデータを読み込むと U+FF0D になる)。

Perl 版が保存して次に読み込むときに値を直すもの (`anflag` の 0 → 1、数値として 0 の `auc0`/`auc4`〜`auc6`/`auc9`
を既定値に、空の出品の品物を振り直す) は、移植版はターンの終わり (と画面の操作の保存の前) にそろえる。

### 画面

- ハコオクの入札、各種予想 (toto・Numbers の予想を `eis8` に書く)、首都名、援助射撃の許可の申請と許可、
  アンケートの投票 (`core::actions::{auction, toto, dispatch, survey}`)
- 管理画面 (`/admin`、マスターパスワードを設定したときだけ): データの状態、最終更新時刻の変更、
  バックアップの復元と削除、やり直し、IP 情報の裏ランキング (`hako-top2.cgi`)
- 最近の出来事 (`/history`、`history.cgi`)

### 移植版で変えたもの

- 援助射撃の許可 (`ms2Main`) は、Perl 版はパスワードを確かめずボタンの島として動くが、移植版はログイン中の島で動く
- 入札の品番が範囲外のとき、Perl 版は空の画面を出すが、移植版はエラーにする
- 管理画面は Perl 版のデータディレクトリではなく、移植版のデータディレクトリの今の状態と `backup<N>/` を扱う。
  やり直しや復元の前のデータはバックアップに回す

## フェーズ 7 (移行) の内容

### 長期の比較

1 ターンずつの突き合わせでは見つからない、ターンをまたぐ相互作用 (保存と読み直し、ログの積み重ね、
島の放棄、出品の入れ替え、Hakoniwa Cup の日程など) を確かめるため、Perl 版と移植版で何十ターンも
続けてゲームを進めて比べる。

- `tools/fixtures/phase7_long.py` がデータ (`tests/fixtures/phase7-*`) とケース (`tests/fixtures/cgi/long-*.json`) を作る。
  ケースは 10〜30 個のターンのリクエスト (時刻を 1 ターンずつ進めたもの) と、そのあいだの画面の操作
  (計画の入力・政策・島の登録・toto の予想・ハコオクの入札) の並び。`rand()` はリクエストごとに並びの先頭から
- `run_cgi.py` はケースに `"snapshots": true` があると、リクエストごとのデータを `snapshots.json.gz`
  (前のリクエストからの差分) に残す。リクエストごとの `"time"`・`"rand"`、`"timeout"`、
  Perl 版がデータを保存したあとで止まるリクエストを許す `"allow_errors"` も指定できる
- `turn/long_run_tests.rs` が `before` から同じ並びを移植版で行い (ターンは `run_turn`、画面の操作は
  `actions::*`)、リクエストごとに Perl 版のデータと比べる。食い違えば最初のリクエストとターンを報告する。
  移植版の状態はリクエストごとに JSON にして読み直す (再起動したときと同じ)

| ケース | ターン | 内容 |
|---|---|---|
| `long-play` | 4〜27 | legacy-turn3 に島を 2 つ登録し、ふつうの開発の計画と政策を入れる。登録した島の放棄、Numbers (10・20) |
| `long-mix-100` | 89〜111 | 全地形の 5 島 (政策・人工衛星・怪獣・予想)。ハコオクの終盤、ターン杯・ハコオクの順位・toto・Numbers3・Hakoniwa Cup の開催 (100)、Numbers4 (90・110) |
| `long-mix-140` | 136〜160 | Hakoniwa Cup のチームを持つ 5 島。決勝トーナメントのシード (141)、決勝と Hakoniwa Cup toto (150)、Numbers |
| `long-mix-200` | 191〜212 | 6 島 (海が多め)。200 と 210 |
| `long-auction-300` | 270〜300 | 7 島。毎ターンの toto の予想 (受付期間の内外)・ハコオクの出品の計画と入札、ターン 300 の落札・順位 |
| `long-disaster` | 61〜80 | 乱数を 1/2 未満に寄せる (災害・怪獣が増える) |
| `long-growth` | 11〜40 | 乱数を 7/16 以上に寄せる (成長が続く)。30 ターン |

乱数の並びは k/256 を 97〜137 個並べたもの (並びが短いと Perl 版が終わらない道筋がある。
たとえば k < 96 に寄せた並びでは、あるターンで Perl 版が終わらなかった)。

すべてのリクエストで Perl 版と一致している (補正は負荷計測のログと Hakoniwa Cup の試合のログの「−」だけ)。
Perl 版は `long-mix-100` のターン 100 で、保存のあとのトップページの表示 (`hako-top.cgi` 1068 行の失業率) が
ゼロ除算で止まる。toto の正解を作る `foreach (@Hislands[0..4, 9, 19, 29])` が `@Hislands` に空の島を作るためと
思われる (データには影響しない。移植版の画面はこの空の島を作らない)。
