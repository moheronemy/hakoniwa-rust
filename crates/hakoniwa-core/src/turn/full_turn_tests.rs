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
    check_turn("turn-basic", &[]);
}

/// 地図の大きさ ($HislandSize) を 32・128 にしたターン全体 (tools/fixtures/scale_size.py のデータ)
#[test]
fn turn_size_32_matches_perl() {
    check_turn("turn-size-32", &[]);
}

#[test]
fn turn_size_128_matches_perl() {
    check_turn("turn-size-128", &[]);
}

// ---- ハコオク (turnMain 857〜903 行、934〜1116 行) -------------------------------
// データは tools/fixtures/phase6_auction.py で作る。

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
    check_turn("turn-auction-prize", &[]);
}

#[test]
fn turn_auction_cap_matches_perl() {
    check_turn("turn-auction-cap", &[]);
}

#[test]
fn turn_auction_many_matches_perl() {
    check_turn("turn-auction-many", &[]);
}

#[test]
fn turn_auction_rest_matches_perl() {
    check_turn("turn-auction-rest", &[]);
}

#[test]
fn turn_auction_sold_matches_perl() {
    check_turn("turn-auction-sold", &[]);
}

#[test]
fn turn_auction_mid_matches_perl() {
    check_turn("turn-auction-mid", &[]);
}

#[test]
fn turn_auction_rest9_matches_perl() {
    check_turn("turn-auction-rest9", &[]);
}

#[test]
fn turn_auction_few_matches_perl() {
    check_turn("turn-auction-few", &[]);
}

// Hakoniwa Cup (cup.rs)

#[test]
fn turn_cup_seed_matches_perl() {
    // ターン 141: 勝ち点で並べ替え、段階 0 以外の上位チームを決勝トーナメントへ
    check_turn("turn-cup-41", &[]);
}

#[test]
fn turn_cup_seed_without_teams_matches_perl() {
    check_turn("turn-cup-41-none", &[]);
}

#[test]
fn turn_cup_opening_matches_perl() {
    // ターン 200: 開催と参加数 ($stsanka − 1)
    check_turn("turn-cup-00", &[]);
}

#[test]
fn turn_cup_opening_without_teams_matches_perl() {
    check_turn("turn-cup-00-none", &[]);
}

// toto・Numbers (lottery.rs)

/// Hakoniwa Cup の試合のログの「−」は、Perl 版のデータ (EUC-JP の 0xA1DD) を読み込むと
/// U+FF0D「－」になるが、移植版の stadium.rs は U+2212「−」で書く (ターン処理の突き合わせ
/// (Perl の Encode で読む) では U+2212 なので、stadium.rs はそのままにしている)
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
    check_turn("turn-lottery-100", &[]);
}

/// ターン 200: toto の資金不足、7 点 2 島で分ける (6 点の率の繰り越し)、Numbers3 の資金不足
#[test]
fn turn_lottery_200_matches_perl() {
    check_turn("turn-lottery-200", &[]);
}

/// ターン 150: Hakoniwa Cup toto (2 点・1 点・資金不足) と Numbers4 (3 島が的中)
#[test]
fn turn_lottery_150_matches_perl() {
    check_turn_with("turn-lottery-150", &[], stadium_dash, |_| {});
}

/// ターン 150 (優勝が逆): 1 点の的中がいない (2 点の率の繰り越し)、Numbers4 の資金不足と外れ
#[test]
fn turn_lottery_150b_matches_perl() {
    check_turn_with("turn-lottery-150b", &[], stadium_dash, |_| {});
}
