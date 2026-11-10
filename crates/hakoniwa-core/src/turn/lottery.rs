//! toto、Hakoniwa Cup toto、Numbers3、Numbers4 (`turnMain` の「島数カット」の後、
//! hako-turn.cgi 1119〜1429 行)。
//!
//! 島の予想は `eis8` (オーナー画面の toto 予想の欄、`htmlEscape` 済みの文字列) に
//! `(toto@1.2.3.4.5.6.7.8)`、`(hc@1.2)`、`(n3@123)`、`(n4@1234)` の形で書かれている。
//! どれも正規表現で最初に見つかったものを使い、形に合わなければその籤は買わない。
//!
//! - toto: ターン杯のターン。ポイント順の 1〜5・10・20・30 位の島の ID を当てる (1000 億円)。
//!   6〜8 点的中に払い戻し率 2・8・20 倍、配当はハコオクの補助金 (`auc9`) とお守り (`etc8`)
//! - Hakoniwa Cup toto: ターン % 100 == 50 で決勝が行われたとき。優勝と準優勝の島の ID
//!   (10000 億円)。1・2 点的中に 3・10 倍、配当は toto と同じ
//! - Numbers3 / Numbers4: ターン % 20 == 0 / 10。`random(999)` / `random(9999)` を当てる
//!   (200 億円)。100 / 200 倍を資金で払い戻す
//!
//! 払い戻しは「掛け金の総額 × 率 ÷ 的中した島の数」。的中した島が無い等級の率は、
//! 一つ上の等級に足される。

use crate::log::msg;
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{self, MatchScope, trunc};

use super::TurnContext;

/// `$island->{'eis8'} =~ /\(PREFIX\@(\d+)\.(\d+)...\)/` (数字の欄が `n` 個) の `$1`..。
/// 最初に一致した位置の値を、Perl が数として比べるときの値 (小数) で返す
fn parse_bet(eis8: &str, prefix: &str, n: usize) -> Option<Vec<f64>> {
    let head = format!("({prefix}@");
    let bytes = eis8.as_bytes();
    let mut start = 0;
    while let Some(pos) = eis8[start..].find(&head) {
        let at = start + pos;
        if let Some(v) = parse_numbers(&bytes[at + head.len()..], n) {
            return Some(v);
        }
        start = at + 1;
    }
    None
}

/// `(\d+)\.(\d+)...\)` の部分。`\d` は ASCII の数字だけ (Perl 版は EUC-JP のバイト列を見る)
fn parse_numbers(mut s: &[u8], n: usize) -> Option<Vec<f64>> {
    let mut out = Vec::with_capacity(n);
    for i in 0..n {
        let len = s.iter().take_while(|b| b.is_ascii_digit()).count();
        if len == 0 {
            return None;
        }
        let digits = std::str::from_utf8(&s[..len]).ok()?;
        out.push(digits.parse::<f64>().ok()?);
        s = &s[len..];
        let sep = if i + 1 == n { b')' } else { b'.' };
        if s.first() != Some(&sep) {
            return None;
        }
        s = &s[1..];
    }
    Some(out)
}

/// 籤の種類ごとの違い
struct Lottery<'a> {
    /// ログに出す名前 (`ｔｏｔｏ` など)
    name: &'a str,
    /// `eis8` の予想の印 (`toto` など)
    prefix: &'a str,
    /// 資金不足のログの計画名
    no_money: &'a str,
    /// 購入費用
    cost: i64,
    /// 正解
    answer: Vec<i64>,
    /// 的中点数 → 払い戻し率 (無い等級は 0)
    rate: Vec<i64>,
    /// 払い戻す的中点数 (低い順)
    paid: std::ops::RangeInclusive<usize>,
}

/// 購入した島 (的中点数ごとに、`$totoID[$n]` の並び)
struct Bets {
    all_bet: i64,
    /// 的中点数 → 島 (toto・Hakoniwa Cup toto は配列の位置、Numbers は島 ID)
    hits: Vec<Vec<i64>>,
}

/// 正解のログ、購入 (資金の確認と支払い)、的中点数の判定。
/// `by_id` なら的中した島を ID で覚える (Numbers)、そうでなければ配列の位置 (toto)
fn buy(ctx: &mut TurnContext, islands: &mut [Island], lot: &Lottery, by_id: bool) -> Bets {
    let turn = ctx.turn;
    let answers: Vec<String> = lot.answer.iter().map(i64::to_string).collect();
    // 正解のログ作成
    ctx.log.history(
        turn,
        format!(
            "{} <B>： {}</B>",
            wrap(tags::NAME, &format!("第{turn}ターン {}", lot.name)),
            answers.join(" ")
        ),
    );

    let mut bets = Bets {
        all_bet: 0,
        hits: vec![Vec::new(); lot.answer.len() + 1],
    };
    for (i, island) in islands.iter_mut().enumerate() {
        let Some(bet) = parse_bet(&island.eis8, lot.prefix, lot.answer.len()) else {
            continue;
        };
        if island.money < lot.cost {
            // 購入費用がない
            ctx.log.out(
                turn,
                msg::no_money(&island.name, lot.no_money),
                Some(island.id),
                None,
            );
            continue;
        }
        island.money -= lot.cost;
        bets.all_bet += lot.cost;

        // 的中点数の判定 (数として比べる)
        let n = lot
            .answer
            .iter()
            .zip(&bet)
            .filter(|(a, b)| **a as f64 == **b)
            .count();
        bets.hits[n].push(if by_id { island.id } else { i as i64 });
    }
    bets
}

/// 的中点数ごとの配当 (`int($allBet * $rate[$i] / ($#id + 1))`)。
/// 的中した島が無い等級の率は上の等級に回す。`pay(点数, 配当, 島)` を島ごとに呼ぶ
fn pay_out(
    ctx: &mut TurnContext,
    lot: &Lottery,
    bets: &Bets,
    history: impl Fn(usize, i64) -> String,
    mut pay: impl FnMut(&mut TurnContext, usize, i64, i64),
) {
    let mut rate = lot.rate.clone();
    rate.resize(lot.answer.len() + 2, 0);
    for i in lot.paid.clone() {
        let ids = &bets.hits[i];
        if ids.is_empty() {
            // 正解者がいない: 予算を上位の等級に回す
            rate[i + 1] += rate[i];
            continue;
        }
        let bet = trunc(bets.all_bet as f64 * rate[i] as f64 / ids.len() as f64);
        ctx.log.history(ctx.turn, history(i, bet));
        for &n in ids {
            pay(ctx, i, bet, n);
        }
    }
}

/// toto / Hakoniwa Cup toto の配当: ハコオクの補助金 (`auc9` の 3 番目) とお守り (`etc8`)。
///
/// `$auc9 =~ ...` と `$etc8 =~ ...` は払い戻しのループの中のマッチなので、形に合わなければ
/// `top` (turnMain のトップレベルで最後に成功したマッチ) や `auc9` のマッチの値が入る (Perl 版のまま)
fn pay_omamori(
    ctx: &mut TurnContext,
    island: &mut Island,
    top: &MatchScope,
    lot: &Lottery,
    hits: usize,
    bet: i64,
    get: i64,
) {
    let mut m = top.clone();
    let mut a9 = ctx.globals.auc9.assign(m.fields(&island.auction.auc9));
    a9[2] += bet;
    a9[0] = a9[1] + trunc(a9[2] as f64 / 10000.0) + a9[3] + a9[4];
    ctx.globals.auc9.0 = a9;
    island.auction.auc9 = perl::join(&a9);

    let out = format!(
        "{} {} {hits}点的中！お守り{get}個ゲット！",
        wrap(tags::NAME, &format!("{}島", island.name)),
        wrap(tags::NAME, lot.name)
    );
    // toto はお守りの前に、Hakoniwa Cup toto は後にログを出す
    let log_first = lot.prefix == "toto";
    if log_first {
        ctx.log.out(ctx.turn, out.clone(), Some(island.id), None);
    }
    let mut t = ctx.globals.etc8.assign(m.fields(&island.etc_raw[3]));
    t[0] += 1;
    t[1] += get;
    ctx.globals.etc8.0 = t;
    island.etc_raw[3] = perl::join(&t);
    if !log_first {
        ctx.log.out(ctx.turn, out, Some(island.id), None);
    }
}

/// 配当の記録ログ (`第Nターン 名前 ...`)
fn payout_history(turn: i64, name: &str, rest: &str) -> String {
    format!(
        "{} {rest}",
        wrap(tags::NAME, &format!("第{turn}ターン {name}"))
    )
}

/// toto と Hakoniwa Cup toto
fn toto(ctx: &mut TurnContext, islands: &mut [Island], top: &MatchScope, lot: &Lottery) {
    let bets = buy(ctx, islands, lot, false);
    let (turn, unit) = (ctx.turn, ctx.config.units.money.clone());
    pay_out(
        ctx,
        lot,
        &bets,
        |i, bet| {
            payout_history(
                turn,
                lot.name,
                &format!("{i}点的中☆配当Auction補助金 {bet}{unit}"),
            )
        },
        |ctx, i, bet, n| {
            // toto は 6〜8 点で 1〜3 個、Hakoniwa Cup toto は 1・2 点で 1・2 個
            let get = if lot.prefix == "toto" {
                i as i64 - 5
            } else {
                i as i64
            };
            pay_omamori(ctx, &mut islands[n as usize], top, lot, i, bet, get);
        },
    );
}

/// Numbers3 / Numbers4。配当は資金。
///
/// 的中した島は ID で覚えておき、`$Hislands[$HidToNumber{$n}]` で島を引くが、
/// `%HidToNumber` はデータを読んだときの並びのままなので、ポイント順に並べ替えた後の
/// 別の島 (無人島になって切り捨てた島のこともある) に配当とログの島名が行く。
/// ログの島 ID は的中した島のもの (Perl 版のまま)
fn numbers(ctx: &mut TurnContext, islands: &mut [Island], cut: &[Island], lot: &Lottery) {
    let bets = buy(ctx, islands, lot, true);
    let (turn, unit) = (ctx.turn, ctx.config.units.money.clone());
    pay_out(
        ctx,
        lot,
        &bets,
        |_, bet| payout_history(turn, lot.name, &format!("的中☆配当金 {bet}{unit}")),
        |ctx, _, bet, id| {
            let Some(&pos) = ctx.id_to_number.get(&id) else {
                return;
            };
            let name = if let Some(island) = islands.get_mut(pos) {
                island.money += bet;
                island.name.clone()
            } else {
                // 切り捨てた無人島: 資金を足しても保存されない
                cut[pos - islands.len()].name.clone()
            };
            ctx.log.out(
                turn,
                format!(
                    "{} {} 的中！",
                    wrap(tags::NAME, &format!("{name}島")),
                    wrap(tags::NAME, lot.name)
                ),
                Some(id),
                None,
            );
        },
    );
}

/// toto・Hakoniwa Cup toto・Numbers3・Numbers4 (turnMain の「島数カット」の直後)。
///
/// - `islands`: 島数カット後の島 (ポイント順)
/// - `cut`: 島数カットで切り捨てた島。Perl 版は `$HislandNumber` を減らすだけで `@Hislands`
///   には残っているので、toto の正解 (10・20・30 位) と Numbers の配当先に出てくる
/// - `top`: turnMain のトップレベルで最後に成功したマッチの `$1`.. (ハコオクの出品
///   `$auction1`..`$auction3` のマッチ)。払い戻しの `auc9`・`etc8` が形に合わないときに使われる
pub(crate) fn run(ctx: &mut TurnContext, islands: &mut [Island], cut: &[Island], top: &MatchScope) {
    let turn = ctx.turn;

    // toto の処理 (ターン杯のターン)
    let unit = ctx.config.turn_prize_unit;
    if unit != 0 && turn % unit == 0 {
        // toto の正解: 1〜5・10・20・30 位の島の ID (島が無ければ 0)
        let answer = [0, 1, 2, 3, 4, 9, 19, 29]
            .iter()
            .map(|&r| {
                islands
                    .get(r)
                    .or_else(|| r.checked_sub(islands.len()).and_then(|k| cut.get(k)))
                    .map_or(0, |island| island.id)
            })
            .collect();
        let lot = Lottery {
            name: "ｔｏｔｏ",
            prefix: "toto",
            no_money: "ｔｏｔｏ購入",
            cost: 1000,
            answer,
            rate: vec![0, 0, 0, 0, 0, 0, 2, 8, 20],
            paid: 6..=8,
        };
        toto(ctx, islands, top, &lot);
    }

    // Hakoniwa Cup toto の処理 (このターンに決勝があったとき)
    let stadium = &ctx.globals.hex.stadium;
    if turn % 100 == 50 && (stadium.yushouflag == 1 || stadium.yushouflag == 2) {
        let lot = Lottery {
            name: "Hakoniwa Cup toto",
            prefix: "hc",
            no_money: "Hakoniwa Cup toto",
            cost: 10000,
            answer: vec![stadium.yushounamber, stadium.yushounamber2],
            rate: vec![0, 3, 10],
            paid: 1..=2,
        };
        toto(ctx, islands, top, &lot);
    }

    // Numbers3 の処理
    if turn % 20 == 0 {
        let lot = Lottery {
            name: "Numbers3",
            prefix: "n3",
            no_money: "Numbers3購入",
            cost: 200,
            answer: vec![ctx.random(999)],
            rate: vec![0, 100],
            paid: 1..=1,
        };
        numbers(ctx, islands, cut, &lot);
    }

    // Numbers4 の処理
    if turn % 20 == 10 {
        let lot = Lottery {
            name: "Numbers4",
            prefix: "n4",
            no_money: "Numbers4購入",
            cost: 200,
            answer: vec![ctx.random(9999)],
            rate: vec![0, 200],
            paid: 1..=1,
        };
        numbers(ctx, islands, cut, &lot);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_bet_like_perl_regex() {
        assert_eq!(
            parse_bet("(toto@3.1.2.0.0.0.0.0)", "toto", 8),
            Some(vec![3.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        );
        // 最初に一致したもの。形に合わないものは飛ばす
        assert_eq!(
            parse_bet("x(n3@12(n3@)(n3@0749)(n3@5)", "n3", 1),
            Some(vec![749.0])
        );
        assert_eq!(parse_bet("(hc@1.2.3)", "hc", 2), None);
        assert_eq!(parse_bet("(hc@1.2)", "hc", 2), Some(vec![1.0, 2.0]));
        assert_eq!(parse_bet("(未登録)", "toto", 8), None);
        assert_eq!(parse_bet("(n4@１２)", "n4", 1), None);
        assert_eq!(parse_bet("(n3@-5)", "n3", 1), None);
    }
}
