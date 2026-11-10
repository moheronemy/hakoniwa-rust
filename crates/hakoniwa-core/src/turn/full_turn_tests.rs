//! ターン全体 (`turnMain`) を、元の Perl CGI でターンを進めた結果と突き合わせる。
//!
//! `tests/fixtures/cgi/turn-*.json` は時刻を最終更新から 1 ターン以上あとにしてあるので、
//! Perl 版はリクエストを受けた時点で `turnMain` を実行する。`rand()` は固定してある。

use crate::actions::perl_compat_tests::check_case_with;

use super::run_turn;

/// `name` のケースの Perl 版のターンと、移植版の `run_turn` を比べる
pub(crate) fn check_turn(name: &str, ignore: &[&str]) {
    check_case_with(
        name,
        ignore,
        |want| {
            // 移植版は Perl 版の負荷計測のログを出さない (このターンに出たものだけ取り除く)
            if let Some(turn) = want.logs.turns.first_mut() {
                turn.retain(|e| !e.message.contains("負荷計測"));
            }
        },
        |game, config, case| {
            run_turn(game, config, &mut case.rng);
        },
    );
}

#[test]
fn turn_basic_matches_perl() {
    check_turn("turn-basic", &[]);
}

// ---- ハコオク (turnMain 857〜903 行、934〜1116 行) -------------------------------
// データは tools/fixtures/phase6_auction.py で作る。

/// ターン 100 にほかの段階が書くもの (並行して移植中: toto・Numbers3 の記録ログ、
/// Hakoniwa Cup の参加数のログ)。マージ後に外す
const OTHERS_AT_TURN_100: &[&str] = &["/logs/history", "/logs/hcup"];

#[test]
fn turn_auction_normal_matches_perl() {
    check_turn("turn-auction-normal", &[]);
}

#[test]
fn turn_auction_late_matches_perl() {
    check_turn("turn-auction-late", &[]);
}

#[test]
fn turn_auction_prize_matches_perl() {
    check_turn("turn-auction-prize", OTHERS_AT_TURN_100);
}

#[test]
fn turn_auction_cap_matches_perl() {
    check_turn("turn-auction-cap", OTHERS_AT_TURN_100);
}

#[test]
fn turn_auction_many_matches_perl() {
    check_turn("turn-auction-many", OTHERS_AT_TURN_100);
}

#[test]
fn turn_auction_rest_matches_perl() {
    check_turn("turn-auction-rest", OTHERS_AT_TURN_100);
}

#[test]
fn turn_auction_sold_matches_perl() {
    check_turn("turn-auction-sold", OTHERS_AT_TURN_100);
}

#[test]
fn turn_auction_mid_matches_perl() {
    check_turn("turn-auction-mid", OTHERS_AT_TURN_100);
}

#[test]
fn turn_auction_rest9_matches_perl() {
    check_turn("turn-auction-rest9", OTHERS_AT_TURN_100);
}

#[test]
fn turn_auction_few_matches_perl() {
    check_turn("turn-auction-few", OTHERS_AT_TURN_100);
}
