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
    tests/fixtures/phase1-mix/    突き合わせ用データ (+ *.expected.json)。ほかに phase2-* など
  hakoniwa-server/  Web サーバー (トップページ、ターンの定時実行、デバッグ用のターン進行)
  hako-convert/     Perl 版データ → state.json の変換ツール
tools/
  gen-tables.sh     hako-main.cgi から tables.rs を再生成する
  fixtures/                   突き合わせ用データを作るスクリプト (fixturelib.py と各データ)
  perl-harness/run-harness.sh 元の Perl コードで期待値 (*.expected.json) を作る
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
| `turnMain` | `core::turn::run_turn` | 一部 (下記「フェーズ 1」) |
| `estimate`, `income` | `core::turn::estimate`, `core::turn::income` | 済 (Perl 版と突き合わせ済み) |
| `countGrow`, `doIslandunemployed` | `core::turn` | 未 |
| `doEachHex` | `core::turn::hex` (地形ごとに分割) | 未 |
| `doCommand` | `core::turn::command` (計画ごとに分割) | 共通部分・資金繰り・放棄のみ |
| `doIslandProcess`, `wideDamage`, `wideDamageli` | `core::turn::island`, `core::disaster` | 未 |
| `makeRandomPointArray`, `randomArray`, `monsterSpec` | `core::turn` | 済 |
| `countAround`, `expToLevel`, `nameToNumber` | `core::turn` など | 未 |
| `newIslandMain`, `makeNewIsland`, `makeNewLand` | `core::island::create` | 未 |
| `changeMain`, `changeOwner` | `core::island` | 未 |
| `logOut`, `logLate`, `logSecret`, `logHistory`, `logFlush` | `core::log::TurnLog` | 済 |
| `log*` (281 個の文面) | `core::log::msg` (Perl 版と同じ HTML の文面) | 使う分から順に (いま 10 個) |
| `islandSort`, 部門賞の `islandSort*` | `core::turn::ranking` | 済 |
| `tempTopPage`, ランキング表示の `islandSort*` | サーバーのトップページ・ランキング | 一部 (順位表のみ) |
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
- **乱数。** 乱数の並びは Perl 版と一致させられない。ルールの検証は、乱数を固定して
  元の Perl コードと突き合わせるテスト (下記「検証の方法」) と、統計的な比較 (災害の発生率など) で行う。
- **途中で並べ替えた配列を、並べ替える前の位置で指す。** `turnMain` は部門賞を決めるために
  `@Hislands` を並べ替えるが、そのあとも並べ替え前の `@order` と `%HidToNumber` を使い続ける。
- **島に入れた一時的な値。** `$island->{'shouhi'}` などは保存されず、ターンの開始時は空。
  `estimate` が 1 ターンに 2 回呼ばれ、2 回目は 1 回目の値を読む (`shouhi` は積み増し)。
  移植版は `IslandScratch` に入れ、ターンの開始時に初期化する。
- **ソートの安定性。** Perl 5.8 以降の `sort` は安定 (同順位は元の順を保つ)。Rust でも `sort_by` (安定) を使う。

## パスワード

Perl 版はパスワードを `crypt($pw, 'h2')` (伝統的な DES crypt) で保存している。
移行したプレイヤーがそのままログインできるよう、照合だけは DES crypt に対応させる
(`pwhash` クレートの `unix_crypt` など)。新しく設定するパスワードは argon2 などで保存し、
DES の値はログイン成功時に置き換える。

## 検証の方法

### 元の Perl コードとの突き合わせ (自動テスト)

移植した関数は、元の Perl コードそのものを同じ入力で動かした結果と比べる。

1. `tools/fixtures/*.py` が、`fixturelib.py` を使って Perl 形式のデータ
   (`tests/fixtures/<名前>/`) を作る。元にするのは Perl 版で作った `legacy-turn3`
2. `tools/perl-harness/run-harness.sh <名前> <段階>` が、`hako-main.cgi` (設定と関数だけ) と
   `hako-turn.cgi` を読み込み、`rand()` の値と座標の並びを固定して、指定した段階
   (`estimate`, `income`, `commands`, `eachhex` を並べたもの) を島ごとに動かす。
   段階ごとにすべての値とログを `*.expected.json` に書き出す (`rand()` を 0 と 0.5 に固定した 2 通り)
3. `turn::perl_compat_tests` が同じ条件で移植版を動かし、島の値・一時値・地形の値・
   計画・ログが 1 つ残らず一致することを確かめる

| データ | 段階 | 確かめていること |
|---|---|---|
| `phase1-mix` | estimate, estimate, income, commands | 集計・収入・資金繰りと放棄 (ほぼ全地形) |
| `phase2-town` | estimate, eachhex, estimate | 町・平地・火災・漏電・不景気・人口の増減 |

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
- [ ] **2. 地形ごとの処理** — `doEachHex` を地形の種類ごとに分けて移植
- [ ] **3. 計画の実行** — `doCommand` を計画の種類ごとに分けて移植
- [ ] **4. 島全体の処理** — `doIslandProcess` (災害、怪獣の出現、賞)
- [ ] **5. 画面** — 島の登録、開発画面 (計画の入力)、観光画面、ローカル掲示板、ランキング
- [ ] **6. 付加機能** — ハコオク、toto、アンケート、人工衛星、Hakoniwa Cup、管理機能
- [ ] **7. 移行** — パスワードの互換、本番データの変換手順、Perl 版との比較テスト

## フェーズ 1 (ターン処理の骨格) の内容

`turnMain` の処理順はそのまま移植し、まだ移植していない段階には `TODO(フェーズN)` の印を付けた。

| `turnMain` の段階 | 状態 |
|---|---|
| 最終更新時刻・ターン番号・座標の並び・処理順の決定 | 済 |
| 収入・消費 (`estimate` → `income`) | 済 |
| 計画の実行 (`doCommand`) | 共通部分 (費用の計算と確認)、資金繰り (援助金、連続資金繰り数、自動放棄)、放棄のみ |
| 成長と単ヘックス災害 (`doEachHex`) | フェーズ 2 |
| 島全体の処理 (`doIslandProcess`, `doIslandunemployed`) | フェーズ 4 |
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

- まだ移植していない計画は、費用の確認を通ったら「移植作業中のため実行されませんでした」のログを出し、
  費用を払わずに 1 ターン使う
- Perl 版の負荷計測ログ (`負荷計測 CPU(...)`) は出さない
- 複合値の空欄 (`1,,3`) は 0 として書き戻す
- コンデンサの充電で地形の値が小数になる場合は切り捨てる (Perl 版も保存時に切り捨てる)
- ターンは、アクセスのたびではなくサーバーが定期的に (`tick_secs` 秒ごとに) 時刻を確かめて進める。
  止まっていた間の分はまとめて処理する
- バックアップは `data` ディレクトリの名前を変える代わりに `state.bak0.json`, `state.bak1.json`, ... に複製する
