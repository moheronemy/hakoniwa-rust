//! 収入と食料消費 (`income`)。

use crate::log::msg;
use crate::model::Island;
use crate::perl::{self, MatchScope, trunc};

use super::TurnContext;

/// ハコオクの補助金 (`auc9`) の 3 番目の欄に `add` を足し、合計欄を計算し直す。
/// `m` はこの if ブロックの `$1`.. (income の factory のマッチを複製したもの)
fn add_subsidy(ctx: &mut TurnContext, island: &mut Island, mut m: MatchScope, add: i64) {
    let mut a9 = ctx.globals.auc9.assign(m.fields(&island.auction.auc9));
    a9[2] += add;
    let c2 = trunc(a9[2] as f64 / 10000.0);
    a9[0] = a9[1] + c2 + a9[3] + a9[4];
    ctx.globals.auc9.0 = a9;
    island.auction.auc9 = perl::join(&a9);
}

/// `income($island)`
pub(crate) fn income(ctx: &mut TurnContext, island: &mut Island) {
    let pop = island.pop;
    let farm = island.farm * 10;
    let mountain = island.mountain;
    // income の $1.. (turnMain のトップレベルからはマッチの無い状態で呼ばれる)
    let mut m = MatchScope::default();
    let f = ctx.globals.factory.assign(m.fields(&island.factory));
    let (factory1, factory2) = (f[0], f[1]);

    island.scratch.incomemoney = 0;

    if pop > farm {
        // 農業だけじゃ手が余る場合: 農場フル稼働
        island.food += farm * (island.scratch.co0 + 1);

        if factory2 * 10 > pop - farm {
            // ハイテク企業・改で働き口が足りている。資金ではなく補助金が増える
            add_subsidy(ctx, island, m.clone(), trunc((pop - farm) as f64 / 10.0));
        } else {
            // if ブロックの中のマッチ。失敗すると factory の $1.. が入る (Perl 版のまま)
            let mut inner = m.clone();
            let mut a9 = ctx.globals.auc9.assign(inner.fields(&island.auction.auc9));
            a9[2] += factory2;

            let workers = (pop - farm - factory2 * 10) as f64;
            let earned = if island.scratch.shouhi > island.scratch.ene {
                // 電力不足で稼ぎが半分
                let m = trunc(workers / 20.0).min(trunc((factory1 + mountain) as f64 / 2.0));
                ctx.log
                    .out(ctx.turn, msg::starve2(&island.name), Some(island.id), None);
                m
            } else {
                trunc(workers / 10.0).min(factory1 + mountain) * (island.scratch.co1 + 1)
            };
            island.money += earned;
            island.scratch.incomemoney += earned;

            let c2 = trunc(a9[2] as f64 / 10000.0);
            a9[0] = a9[1] + c2 + a9[3] + a9[4];
            ctx.globals.auc9.0 = a9;
            island.auction.auc9 = perl::join(&a9);
        }
    } else {
        // 農業だけで手一杯の場合: 全員野良仕事
        island.food += pop * (island.scratch.co0 + 1);
    }

    // 食料消費
    island.food = trunc(island.food as f64 - pop as f64 * ctx.config.eaten_food);
}
