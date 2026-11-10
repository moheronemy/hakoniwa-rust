//! 建設系 (植林・農場・発電所・コンデンサ・食物研究所・牧場・大学・工場・ミサイル基地・記念碑・ハリボテ・怪獣購入・遊園地・動物園・地雷・養殖場・野球場・海あみゅ・ニュータウン・リゾート地・開発予定・役所・倉庫・電車・防衛施設)。
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

pub(super) fn build(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    not_ported(ctx, &islands[idx], c)
}
