//! ハイテク技術誘致・自宅建設・輝ける都市・改装・海底基地・海底都市・防災都市化・現代都市・海底新都市・僕の引越し。
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

pub(super) fn ht_get(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn house(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn bettown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn kai(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn sbase(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn seacity(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn procity(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn bigtown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn seatown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn boku(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn boku2(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}
