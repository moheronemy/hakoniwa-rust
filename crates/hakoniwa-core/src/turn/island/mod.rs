//! 島全体の処理 (`doIslandProcess`) と失業者の移民 (`doIslandunemployed`)。
//!
//! doIslandProcess は 1 本の長い関数で、災害・怪獣の出現・人工衛星の維持・ハコオクの
//! 落札・政策・賞などを順に処理する。移植版は段階ごとにファイルを分け、ここで Perl 版と
//! 同じ順に呼ぶ。
//!
//! doIslandProcess の `my` 変数は少なく (`$number`, `$r`, `$pop` など)、[`ProcRun`] に持つ。
//! ほとんどの値は `my` の無いグローバル変数 (`$toto2`, `$s00`.., `$msjotai`, `$value`, `$str` など) で、
//! doEachHex・doCommand や別の島と値を共有する。

// TODO(フェーズ4): すべての段階を移植したら外す
#![allow(dead_code, unused_imports)]

mod auction;
mod disaster1;
mod disaster2;
mod ending;
mod migrate;
mod upkeep;

use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{self, MatchScope, trunc};

use super::TurnContext;

/// doIslandProcess 1 回分の状態。Perl 版の doIslandProcess の `my` 変数に当たる
#[derive(Debug, Default)]
pub struct ProcRun {
    /// 島の配列の位置 (`$number`)
    pub number: usize,
    /// 怪獣判定の乱数 (`my($r) = random(10000)`)
    pub r: i64,
    /// 人口 (`my($pop)`)
    pub pop: i64,
    /// doIslandProcess のトップレベルの `$1`..。段階のトップレベルの正規表現はこれを使い、
    /// ブロックの中の正規表現は `clone()` したものを使う
    pub scope: MatchScope,
}

/// doIslandProcess / doIslandunemployed だけで使うグローバル変数
#[derive(Debug, Default)]
pub struct ProcessGlobals {
    /// `$value`
    pub value: i64,
    /// `$pika2` (ハイテク企業の維持費)
    pub pika2: i64,
    pub migrate: migrate::Globals,
    pub disaster1: disaster1::Globals,
    pub disaster2: disaster2::Globals,
    pub ending: ending::Globals,
    pub upkeep: upkeep::Globals,
    pub auction: auction::Globals,
}

/// 島に一時的に持たせる値のうち、島全体の処理の段階ごとのもの
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {
    pub migrate: migrate::Scratch,
    pub disaster1: disaster1::Scratch,
    pub disaster2: disaster2::Scratch,
    pub upkeep: upkeep::Scratch,
    pub auction: auction::Scratch,
}

/// `doIslandProcess($number, $island)`
pub(crate) fn do_island_process(ctx: &mut TurnContext, islands: &mut [Island], idx: usize) {
    // turnMain のループの中から、マッチの無い状態で呼ばれる
    let mut p = ProcRun {
        number: idx,
        ..Default::default()
    };
    prologue(ctx, &mut islands[idx], &mut p);
    migrate::resort_fatigue(ctx, islands, idx, &mut p); // 14635-14849
    disaster1::run(ctx, islands, idx, &mut p); // 14850-15247
    disaster2::run(ctx, islands, idx, &mut p); // 15248-15665
    upkeep::run(ctx, islands, idx, &mut p); // 15666-15787
    auction::run(ctx, islands, idx, &mut p); // 15788-16957
    ending::run(ctx, islands, idx, &mut p); // 16958-17143
}

/// `doIslandunemployed($number, $island)`
pub(crate) fn do_island_unemployed(ctx: &mut TurnContext, islands: &mut [Island], idx: usize) {
    migrate::unemployed(ctx, islands, idx);
}

/// doIslandProcess の先頭 (Perl 版 14570〜14634 行)
fn prologue(ctx: &mut TurnContext, island: &mut Island, p: &mut ProcRun) {
    let (id, turn) = (island.id, ctx.turn);

    ctx.globals.etc5.assign(p.scope.fields(&island.etc_raw[0]));

    // 怪獣派遣・ミサイルの状態 (etc7) の残りターンを減らす
    let [msjotai, nokotan, msid] = ctx.globals.etc7.assign(p.scope.fields(&island.etc_raw[2]));
    let nokotan = nokotan - 1;
    ctx.globals.etc7.0[1] = nokotan;
    island.etc_raw[2] = perl::join(&[msjotai, nokotan, msid]);
    if nokotan < 1 {
        island.etc_raw[2] = "0,0,0".into();
    }

    // Hakoniwa Cup 開会式
    if island.scratch.hex.stadium.stsankahantei == 1 {
        let value = ctx.globals.hex.stadium.stsanka * ctx.random(2000);
        ctx.globals.process.value = value;
        island.money += value;
        let amount = format!("{value}{}", ctx.config.units.money);
        let message = format!(
            "{}で<B>Hakoniwa Cup開会式</B>が行なわれ、<B>{amount}</B>の経済効果を巻き起こしました。",
            wrap(tags::NAME, &format!("{}島", island.name))
        );
        ctx.log.history(turn, message.clone());
        ctx.log.hcup(turn, message);
    }
    let _ = id;

    // ハイテク企業の維持費 (利益の半分、ハイテク企業・改は 5 分の 1)
    let divisor = if island.scratch.htf > 0 {
        Some(2.0)
    } else if island.scratch.shtf > 0 {
        Some(5.0)
    } else {
        None
    };
    if let Some(d) = divisor {
        let base = if ctx.config.another_mode {
            island.scratch.amarimoney
        } else {
            island.owner_stats.pika
        };
        let pika2 = trunc(base as f64 / d).max(0);
        ctx.globals.process.pika2 = pika2;
        island.money -= pika2;
    }

    if ctx.turn % 100 == 0 {
        island.ip_counters[0] = 0;
    }

    // $toto1..$toto7 (このあとの段階が $toto2 を使う)
    ctx.globals.etc8.assign(p.scope.fields(&island.etc_raw[3]));
}
