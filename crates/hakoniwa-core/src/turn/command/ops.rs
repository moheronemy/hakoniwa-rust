//! 人工衛星 (打ち上げ・修復・破壊砲・レーザー)、ハコオク出品、エサ、食料輸出、資金・食料援助、電力援助、誘致活動。
//!
//! TODO(フェーズ3): Perl 版の doCommand の該当する分岐を移植する。
//! いまは「移植作業中」のログを出して 1 ターン使う。

use crate::log::msg;
use crate::model::Island;
use crate::turn::TurnContext;

use super::CmdRun;

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

fn not_ported(ctx: &mut TurnContext, island: &Island, c: &CmdRun) -> bool {
    ctx.log.out(
        ctx.turn,
        msg::not_ported(&island.name, c.com_name),
        Some(island.id),
        None,
    );
    true
}

pub(super) fn auction(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn givefood(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn eisei(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn eiseimente(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn eisei_att(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn eisei_lzr(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn sell(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn aid(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn ene_give(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn propaganda(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}
