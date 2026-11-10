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
    // TODO(フェーズ6): ハコオクの出品の入れ替えを移植したら外す
    check_turn("turn-basic", &["/world/auction_lots"]);
}

// Hakoniwa Cup (cup.rs)。TODO(フェーズ6): ハコオクの出品の入れ替えを移植したら
// /world/auction_lots の無視は外す

#[test]
fn turn_cup_seed_matches_perl() {
    // ターン 141: 勝ち点で並べ替え、段階 0 以外の上位チームを決勝トーナメントへ
    check_turn("turn-cup-41", &["/world/auction_lots"]);
}

#[test]
fn turn_cup_seed_without_teams_matches_perl() {
    check_turn("turn-cup-41-none", &["/world/auction_lots"]);
}

/// ターン % 100 == 0 のケース。ターン杯のターンなので、まだ移植していないハコオクの順位と賞品
/// (高額落札ランキング) と、toto・Numbers の当選番号の記録が Perl 版にだけ出る。
/// その記録を取り除き、賞金を差し引いて比べる。
/// 賞品を受け取る島 (どちらのケースも 2 番目の島) の `auc4` (落札の記録) と `etc8` (お守り) は
/// 比べない。TODO(フェーズ6): ハコオクの順位と賞品、toto・Numbers を移植したら、
/// この関数をやめて check_turn に戻す
fn check_turn_without_auction_prize(name: &str) {
    check_case_with(
        name,
        &[
            "/world/auction_lots",
            "/world/islands/1/auction/auc4",
            "/world/islands/1/etc_raw/3",
        ],
        |want| {
            if let Some(turn) = want.logs.turns.first_mut() {
                turn.retain(|e| !e.message.contains("負荷計測"));
            }
            let is_prize = |m: &str| m.contains("高額落札ランキング１位");
            let prize = want
                .logs
                .auction
                .iter()
                .find(|e| is_prize(&e.message))
                .map(|e| e.message.clone())
                .expect("ハコオクの賞品の記録");
            want.logs.auction.retain(|e| !is_prize(&e.message));
            // toto・Numbers の当選番号 (「第200ターン ｔｏｔｏ」など)
            want.logs.history.retain(|e| {
                !(e.message.contains("ターン ｔｏｔｏ") || e.message.contains("ターン Numbers"))
            });
            // 「<B>名前島様</B>、... （賞金<B>950億円/お守り1個</B>)」
            let name = prize
                .split("<B>")
                .nth(1)
                .unwrap()
                .split("島様")
                .next()
                .unwrap();
            let value: i64 = prize
                .split("賞金<B>")
                .nth(1)
                .unwrap()
                .split("億円")
                .next()
                .unwrap()
                .parse()
                .unwrap();
            let island = want
                .world
                .islands
                .iter_mut()
                .find(|i| i.name == name)
                .unwrap();
            island.money -= value;
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
