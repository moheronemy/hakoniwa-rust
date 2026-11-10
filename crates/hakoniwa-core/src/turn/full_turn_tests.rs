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
const OTHERS_AT_TURN_100: &[&str] = &["/logs/history"];

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

// Hakoniwa Cup (cup.rs)。TODO(フェーズ6): ハコオクの出品の入れ替えを移植したら
// /world/auction_lots の無視は外す

#[test]
fn turn_cup_seed_matches_perl() {
    // ターン 141: 勝ち点で並べ替え、段階 0 以外の上位チームを決勝トーナメントへ
    check_turn("turn-cup-41", &[]);
}

#[test]
fn turn_cup_seed_without_teams_matches_perl() {
    check_turn("turn-cup-41-none", &[]);
}

/// ターン % 100 == 0 のケース。ターン杯のターンなので、まだ移植していない toto・Numbers の
/// 当選番号の記録が Perl 版にだけ出る。その記録を取り除いて比べる。
/// TODO(フェーズ6): toto・Numbers を移植したら、この関数をやめて check_turn に戻す
fn check_turn_without_auction_prize(name: &str) {
    check_case_with(
        name,
        &[],
        |want| {
            if let Some(turn) = want.logs.turns.first_mut() {
                turn.retain(|e| !e.message.contains("負荷計測"));
            }
            // toto・Numbers の当選番号 (「第200ターン ｔｏｔｏ」など)
            want.logs.history.retain(|e| {
                !(e.message.contains("ターン ｔｏｔｏ") || e.message.contains("ターン Numbers"))
            });
        },
        |game, config, case| {
            run_turn(game, config, &mut case.rng);
        },
    );
}

#[test]
fn turn_cup_opening_matches_perl() {
    // ターン 200: 開催と参加数 ($stsanka − 1)
    check_turn_without_auction_prize("turn-cup-00");
}

#[test]
fn turn_cup_opening_without_teams_matches_perl() {
    check_turn_without_auction_prize("turn-cup-00-none");
}
