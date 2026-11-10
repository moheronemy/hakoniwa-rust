//! 整地・地ならし・埋め立て・港町開発・造船・関所・掘削・温泉掘削・伐採・採掘場整備。
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

pub(super) fn prepare(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn reclaim(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn minato(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn fune(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn seki(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn destroy(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn onsen(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn sell_tree(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn mountain(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}
