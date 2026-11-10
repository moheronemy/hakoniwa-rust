//! ハコオクの順位と賞品、出品の入れ替え (`turnMain` の 857〜903 行と 934〜1116 行)。
//!
//! - [`rank`]: ターン杯のターンに、落札額 (`auc0` の 3 番目) の順に島を並べて順位を
//!   `auc0` の 5 番目に書き、1 位の島の連続 1 位の記録 (`auc4`) を伸ばして賞金を出す
//!   (死滅判定の後、`islandSort` の前)
//! - [`rotate`]: ターン杯のターンに出品 3 枠を新しい品物に入れ替え、毎ターン各枠の
//!   状態 (3 番目、15 で締め切り) を進める (ターン杯の後、島数カットの前)
//!
//! 出品を落札する処理は doIslandProcess の中 ([`super::island`] の `auction`) にある。
//!
//! 正規表現の `$1`.. は Perl 版のまま [`MatchScope`] で扱う。`turnMain` の本体の
//! スコープは、ここより前に (ブロックの外で) 成功したマッチが無いので空から始める。

use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{MatchScope, digits_inc, num_eq_empty};
use crate::turn::TurnContext;

/// ターン杯のターンか (`$HislandTurn % $HturnPrizeUnit == 0`)。
/// `$HturnPrizeUnit` が 0 なら Perl 版は 0 除算で止まるので、移植版は何もしない
fn prize_turn(ctx: &TurnContext) -> bool {
    let unit = ctx.config.turn_prize_unit;
    unit != 0 && ctx.turn % unit == 0
}

/// ハコオクの順位と賞品 (857〜903 行)。ターン杯のターンだけ動く。
///
/// 島を `auc0c` (estimate が読んだ `auc0` の 3 番目) の大きい順に並べ替える
/// (`islandSortac4`)。この並びが後の `islandSort` の同点の順になる (Perl 版のまま)。
pub(crate) fn rank(ctx: &mut TurnContext, islands: &mut [Island]) {
    if !prize_turn(ctx) {
        return;
    }

    // islandSortac4
    islands.sort_by_key(|i| std::cmp::Reverse(i.scratch.auc0c));

    // if ブロックの $1..
    let mb = MatchScope::default();
    let shouhin = ctx.config.auction_prize_streak;
    for (ii, island) in islands.iter_mut().enumerate() {
        // for の 1 回ごとに $1.. は入る前の値に戻る
        let mut mi = mb.clone();
        let a = &mut island.auction;

        let t0 = mi.fields_text::<5>(&a.auc0);
        ctx.globals.auc0.assign(mi.current());
        a.auc0 = format!("{},{},{},{},{}", t0[0], t0[1], t0[2], t0[3], ii + 1);

        let t4 = mi.fields_text::<3>(&a.auc4);
        ctx.globals.auc4.assign(mi.current());
        if ii == 0 {
            let auc4a = digits_inc(&t4[0]);
            let mut auc4b = digits_inc(&t4[1]);
            if crate::perl::int(&auc4b) >= shouhin {
                auc4b = shouhin.to_string();
            }
            let g = &mut ctx.globals.auc4.0;
            g[0] = crate::perl::int(&auc4a);
            g[1] = crate::perl::int(&auc4b);
            a.auc4 = format!("{auc4a},{auc4b},{}", t4[2]);
        } else {
            a.auc4 = format!("{},0,0", t4[0]);
        }
    }

    // 1 位の島に賞金とお守り 1 個
    let value = ctx.turn + ctx.random(1001);
    let Some(island) = islands.first_mut() else {
        return;
    };
    island.money += value;
    let prize = format!("{value}{}/お守り1個", ctx.config.units.money);

    let mut m = mb.clone();
    let t = m.fields_text::<7>(&island.etc_raw[3]);
    let mut toto = ctx.globals.etc8.assign(m.current());
    toto[1] += 1;
    ctx.globals.etc8.0 = toto;
    island.etc_raw[3] = format!(
        "{},{},{},{},{},{},{}",
        t[0], toto[1], t[2], t[3], t[4], t[5], t[6]
    );

    // logPrizeAuc ($hcturn も計算し直す)
    let hcturn = crate::perl::trunc(ctx.turn as f64 / 100.0) * 100;
    ctx.globals.hex.stadium.hcturn = hcturn;
    let name = wrap(tags::NAME, &format!("{}島様", island.name));
    ctx.log.auction(
        ctx.turn,
        format!(
            "{name}、<B>Hakoniwa Auction{hcturn} 高額落札ランキング１位！</B>（賞金<B>{prize}</B>)"
        ),
    );
}

/// 新しい品物の値 (`$value`)。品物によっては乱数を使う
fn item_value(ctx: &mut TurnContext, shuppin: i64) -> i64 {
    match shuppin {
        9 => 1 + ctx.random(5),
        10 => 1000 + ctx.random(1500),
        11 => 500 + ctx.random(1000),
        12 => 2000 + ctx.random(2000),
        17 => 500 + ctx.random(750),
        18 => 300 + ctx.random(500),
        22 | 23 => 1 + ctx.random(4),
        24 => 1 + ctx.random(999),
        25 => 80 + ctx.random(3),
        27 | 28 => 500 + ctx.random(2000),
        _ => 0,
    }
}

/// 前回の落札総額 (`$aucflag1..3`) がこれ未満なら、その枠は次回お休み (29 番) にする
const AUCFLAG_MIN: [i64; 3] = [90, 120, 60];

/// ハコオクの出品の入れ替えと状態の更新 (934〜1116 行)。
///
/// 出品 (`$auction1..3`) は `ctx.globals.command.ops.auction` にあり、
/// `run_turn` の最後に `World::auction_lots` に書き戻される。
pub(crate) fn rotate(ctx: &mut TurnContext) {
    if prize_turn(ctx) {
        // if ブロックの $1..
        let mut r = MatchScope::default();
        let n_islands = ctx.island_number as i64;
        let oyasumi = ctx.oyasumiritu;
        for (n, &aucflag_min) in AUCFLAG_MIN.iter().enumerate() {
            let lot = ctx.globals.command.ops.auction[n].clone();
            let old = ctx.globals.command.ops.auction_caps[n].assign(r.fields(&lot));

            let mut shuppin = ctx.random(28) + 1;
            let value = item_value(ctx, shuppin);
            match n {
                1 => {
                    if n_islands < 20 {
                        shuppin = 29;
                    }
                    if ctx.random(1000) < 100 - n_islands + oyasumi * 25 {
                        shuppin = 29;
                    }
                }
                2 => {
                    if n_islands < 30 {
                        shuppin = 29;
                    }
                    if (ctx.random(1000) as f64) < oyasumi as f64 * 12.5 {
                        shuppin = 29;
                    }
                }
                _ => {}
            }
            // 2・3 枠目はお休み (29 番) なら締め切り。1 枠目は乱数では 29 番にならない
            let mut ajoutai = if n != 0 && shuppin == 29 { 15 } else { 0 };
            // 前回の落札が少なければ、前回がお休みでない限りお休み
            if ctx.globals.hex.aucflag[n] < aucflag_min && old[0] != 29 {
                shuppin = 29;
                ajoutai = 15;
            }
            let mut motone = ctx.random(shuppin);
            if n == 1 {
                motone *= 2;
            }
            ctx.globals.command.ops.auction[n] = format!("{shuppin},{value},{ajoutai},{motone},0");
        }
    }

    // 毎ターン: 状態を 1 進める (15 で締め切り)。ターン杯の残り 25 ターンからは 5% で締め切る
    // (turnMain の本体のスコープの $1..)
    let mut top = MatchScope::default();
    let unit = ctx.config.turn_prize_unit;
    for n in 0..3 {
        let lot = ctx.globals.command.ops.auction[n].clone();
        let t = top.fields_text::<5>(&lot);
        let mut caps = top.current::<5>();
        // `$ajoutai1 < 15` で数値として使った後なので、`++` は数値の加算 ("007" は 8 になる)
        let mut ajoutai = t[2].clone();
        if caps[2] < 15 {
            caps[2] += 1;
            ajoutai = caps[2].to_string();
        }
        if unit != 0 && ctx.turn % unit > 74 && ctx.random(100) < 5 {
            caps[2] = 15;
            ajoutai = "15".into();
        }
        ctx.globals.command.ops.auction_caps[n].assign(caps);
        ctx.globals.command.ops.auction[n] =
            format!("{},{},{ajoutai},{},{}", t[0], t[1], t[3], t[4]);
    }
}

/// Perl 版が次に読み込むときの既定値 (`readIsland` の `if($auc0 == '') { $auc0 = '0,0,0,0,0'; }` など)。
///
/// 数値として 0 の値 (`"0,0,0,0,3"` のように先頭の欄が 0 のものも) は既定値に戻る。
/// 順位 (`auc0` の 5 番目) は、落札したことのない島では次の読み込みで消える (Perl 版のまま)。
/// 保存と読み込みを挟んだ値にそろえるため、ターンの最後に呼ぶ
pub(crate) fn reload_defaults(islands: &mut [Island]) {
    fn fix(s: &mut String, default: &str) {
        if num_eq_empty(s) {
            *s = default.to_string();
        }
    }
    for island in islands {
        let a = &mut island.auction;
        fix(&mut a.auc0, "0,0,0,0,0");
        fix(&mut a.auc4, "0,0,0");
        fix(&mut a.auc5, "0,0,0,0,0");
        fix(&mut a.auc6, "0,0,0");
        fix(&mut a.auc9, "0,0,0,0,0");
    }
}
