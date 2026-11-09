//! リゾート地・臨海リゾートホテル・カジノ・動物園・野球場・海あみゅ・腐海・枯死海。
//!
//! TODO(フェーズ2): Perl 版の doEachHex の該当する分岐を移植する。
//! いまは何もせず、共通の災害判定に進む。

use crate::model::Island;
use crate::turn::TurnContext;

use super::{Flow, HexRun};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

pub(super) fn rizort(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn big_rizort(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn kajino(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn zoo(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn kyujo(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn umiamu(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn rotten_sea(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn dead_sea(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}
