//! ターン全体 (`turnMain`) を、元の Perl CGI でターンを進めた結果と突き合わせる。
//!
//! `tests/fixtures/cgi/turn-*.json` は時刻を最終更新から 1 ターン以上あとにしてあるので、
//! Perl 版はリクエストを受けた時点で `turnMain` を実行する。`rand()` は固定してある。

use crate::actions::perl_compat_tests::check_case_with;
use crate::model::GameState;

use super::run_turn;

/// `name` のケースの Perl 版のターンと、移植版の `run_turn` を比べる
pub(crate) fn check_turn(name: &str, ignore: &[&str]) {
    check_turn_with(name, ignore, |_| {}, |_| {});
}

/// [`check_turn`] で、比べる前に Perl 版の結果を `fix_want` で、移植版の結果を `fix_got` で直すもの
pub(crate) fn check_turn_with(
    name: &str,
    ignore: &[&str],
    fix_want: impl FnOnce(&mut GameState),
    fix_got: impl FnOnce(&mut GameState),
) {
    check_case_with(
        name,
        ignore,
        |want| {
            // 移植版は Perl 版の負荷計測のログを出さない (このターンに出たものだけ取り除く)
            if let Some(turn) = want.logs.turns.first_mut() {
                turn.retain(|e| !e.message.contains("負荷計測"));
            }
            fix_want(want);
        },
        |game, config, case| {
            run_turn(game, config, &mut case.rng);
            fix_got(game);
        },
    );
}

#[test]
fn turn_basic_matches_perl() {
    // TODO(フェーズ6): ハコオクの出品の入れ替えを移植したら外す
    check_turn("turn-basic", &["/world/auction_lots"]);
}

/// ターン杯のターンに、まだ移植していない Perl 版の処理 (ハコオクの順位と賞品、
/// Hakoniwa Cup の参加数のログ) を Perl 版の結果から取り除く。
/// `auction_top` はハコオクの賞品をもらう島 (islandSortac4 の 1 位) の ID。
/// TODO(フェーズ6): ハコオクの順位と賞品、Hakoniwa Cup の参加数を移植したら外す
fn undo_unported_prize_turn(want: &mut GameState, auction_top: i64) {
    let turn = want.world.turn;
    let rand = 750; // random(1001) (rand 0.75)
    let island = want
        .world
        .islands
        .iter_mut()
        .find(|i| i.id == auction_top)
        .unwrap();
    island.money -= turn + rand;
    let mut toto: Vec<i64> = island.etc_raw[3]
        .split(',')
        .map(|s| s.parse().unwrap())
        .collect();
    toto[1] -= 1;
    island.etc_raw[3] = crate::perl::join(&toto);
    let auction_log = want.logs.auction.len();
    want.logs
        .auction
        .retain(|m| !(m.turn == turn && m.message.contains("高額落札ランキング１位")));
    assert_eq!(want.logs.auction.len(), auction_log - 1);
    want.logs
        .history
        .retain(|m| !(m.turn == turn && m.message.contains("開催！参加数")));
    want.logs.hcup.retain(|m| m.turn != turn);
}

/// ハコオクの順位 (auc0 の 5 番目) と連続 1 位 (auc4) は、ターン杯のターンに全島で変わる。
/// TODO(フェーズ6): ハコオクの順位と賞品を移植したら外す
const PRIZE_TURN_AUCTION: &[&str] = &[
    "/world/auction_lots",
    "/world/islands/0/auction/auc0",
    "/world/islands/0/auction/auc4",
    "/world/islands/1/auction/auc0",
    "/world/islands/1/auction/auc4",
    "/world/islands/2/auction/auc0",
    "/world/islands/2/auction/auc4",
];

/// Perl 版は読み込むときに、数として 0 の複合値 (`'0,0,4000,0,0' == ''` は真) を既定値に戻す。
/// 補助金が 1 万未満で合計欄が 0 の `auc9` は、次の読み込みで消える。Perl 版の結果は保存して
/// 読み込んだものなので、移植版の結果も同じように直してから比べる。
/// TODO: run_turn でそろえるか (アンケートの anflag と同じ) は別に決める
fn reload_auction_like_perl(game: &mut GameState) {
    for island in &mut game.world.islands {
        let a = &mut island.auction;
        for (s, default) in [
            (&mut a.auc0, "0,0,0,0,0"),
            (&mut a.auc4, "0,0,0"),
            (&mut a.auc5, "0,0,0,0,0"),
            (&mut a.auc6, "0,0,0"),
            (&mut a.auc9, "0,0,0,0,0"),
        ] {
            if crate::perl::num_eq_empty(s) {
                *s = default.to_string();
            }
        }
    }
}

/// Hakoniwa Cup の試合のログの「−」は、Perl 版のデータ (EUC-JP の 0xA1DD) を読み込むと
/// U+FF0D「－」になるが、移植版の stadium.rs は U+2212「−」で書く。
/// TODO: stadium.rs の文字をそろえたら外す
fn stadium_dash(want: &mut GameState) {
    let fix = |m: &mut String| *m = m.replace('－', "−");
    want.logs.hcup.iter_mut().for_each(|m| fix(&mut m.message));
    want.logs.turns[0]
        .iter_mut()
        .for_each(|e| fix(&mut e.message));
}

/// ターン 100: toto (切り捨てた無人島の ID が正解に入る、8 点と 6 点、7 点の率の繰り越し) と
/// Numbers3 (配当が読み込み時の位置の島へ行き、無人島に行った分は消える)
#[test]
fn turn_lottery_100_matches_perl() {
    check_turn_with(
        "turn-lottery-100",
        PRIZE_TURN_AUCTION,
        |want| undo_unported_prize_turn(want, 2),
        reload_auction_like_perl,
    );
}

/// ターン 200: toto の資金不足、7 点 2 島で分ける (6 点の率の繰り越し)、Numbers3 の資金不足
#[test]
fn turn_lottery_200_matches_perl() {
    check_turn_with(
        "turn-lottery-200",
        PRIZE_TURN_AUCTION,
        |want| undo_unported_prize_turn(want, 2),
        reload_auction_like_perl,
    );
}

/// ターン 150: Hakoniwa Cup toto (2 点・1 点・資金不足) と Numbers4 (3 島が的中)
#[test]
fn turn_lottery_150_matches_perl() {
    // TODO(フェーズ6): ハコオクの出品の入れ替えを移植したら外す
    check_turn_with(
        "turn-lottery-150",
        &["/world/auction_lots"],
        stadium_dash,
        reload_auction_like_perl,
    );
}

/// ターン 150 (優勝が逆): 1 点の的中がいない (2 点の率の繰り越し)、Numbers4 の資金不足と外れ
#[test]
fn turn_lottery_150b_matches_perl() {
    // TODO(フェーズ6): ハコオクの出品の入れ替えを移植したら外す
    check_turn_with(
        "turn-lottery-150b",
        &["/world/auction_lots"],
        stadium_dash,
        reload_auction_like_perl,
    );
}
