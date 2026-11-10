//! ミサイル (通常・PP・SPP・ST・核・地形隆起弾・陸地破壊弾)、動物派遣、大使派遣。
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

pub(super) fn missile(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn send_monster(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}

pub(super) fn taishi(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}
