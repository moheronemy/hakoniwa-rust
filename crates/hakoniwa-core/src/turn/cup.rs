//! Hakoniwa Cup のうち turnMain が直接行う部分。
//!
//! - ターン % 100 == 41: 予選の勝ち点 (`kachiten`) で島を並べ替え、上位 8 島のうち
//!   参加中のチームを決勝トーナメント (段階 6) に進める (hako-turn.cgi 752–769、`islandSortHC`)
//! - ターン % 100 == 0: 開催と参加島数の記録 (hako-turn.cgi 1431–1434、`logHC`)
//!
//! 試合そのものと参加の受け付けは多目的スタジアムの処理 ([`super::hex`] の stadium)、
//! 開会式は島ごとの処理 ([`super::island`]) にある。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 並べ替えは `@Hislands` そのものに行うので、その後の部門賞の並べ替えはこの順から始まる。
//! - 島が 8 つ未満でも 8 回まわる。存在しない島は `eisei4` が空でマッチに失敗し、
//!   `$stshoka` は未定義 (0) になるので何もしない。turnMain から見える `$1`.. は無い
//!   (呼び出し元の hako-main.cgi の本体はマッチをしない)。
//! - `eisei4` は欄の文字列をそのまま書き戻す (`"020"` は `"020"` のまま)。
//! - 参加島数のログは `$stsanka - 1` (スタジアムの処理が数えた数より 1 少ない)。

use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{fields_raw, int};

use super::TurnContext;

/// 決勝トーナメントに進める島の数 (上位 8 島)
const SEEDS: usize = 8;

/// `eisei4` の勝ち上がり段階の欄
const SHOKA: usize = 10;

/// 決勝トーナメントのシード (`if(($HislandTurn % 100) == 41)` の部分)。
/// 島の配列を勝ち点の順に並べ替える
pub(crate) fn seed(ctx: &mut TurnContext, islands: &mut [Island]) {
    if ctx.turn.rem_euclid(100) != 41 {
        return;
    }
    // islandSortHC (同じ勝ち点なら元の順。sort_by_key は安定)
    islands.sort_by_key(|i| std::cmp::Reverse(i.scratch.kachiten));

    // $stsin はグローバル変数で、ここでしか使われない
    let mut stsin = String::new();
    for island in islands.iter_mut().take(SEEDS) {
        let Some(raw) = fields_raw::<11>(&island.eisei_raw[1]) else {
            // マッチに失敗すると $sto.. は未定義になる
            ctx.globals.eisei4.0 = [0; 11];
            continue;
        };
        ctx.globals.eisei4.0 = raw.map(int);
        if int(raw[SHOKA]) != 0 {
            ctx.globals.eisei4.0[SHOKA] = 6;
            let mut texts = raw.map(str::to_string);
            texts[SHOKA] = "6".into();
            island.eisei_raw[1] = texts.join(",");
            stsin.push_str(&format!("{}島、", island.name));
        }
    }
    // logHCsin
    let message = format!(
        "{}<br><font size=\"-1\"><B>{stsin}</B></font>",
        wrap(tags::NAME, "Hakoniwa Cup決勝トーナメント進出島!!")
    );
    ctx.log.history(ctx.turn, message.clone());
    ctx.log.hcup(ctx.turn, message);
}

/// 開催の記録 (`if(($HislandTurn % 100) == 0)` の部分、`logHC`)
pub(crate) fn opening(ctx: &mut TurnContext) {
    if ctx.turn.rem_euclid(100) != 0 {
        return;
    }
    let stadium = &mut ctx.globals.hex.stadium;
    stadium.stsanka -= 1;
    let message = format!(
        "{}開催！参加数{}島！",
        wrap(tags::NAME, &format!("Hakoniwa Cup{}", ctx.turn)),
        stadium.stsanka
    );
    ctx.log.history(ctx.turn, message.clone());
    ctx.log.hcup(ctx.turn, message);
}
