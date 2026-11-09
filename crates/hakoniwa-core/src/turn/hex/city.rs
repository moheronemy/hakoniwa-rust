//! 防災都市・ニュータウン・現代都市・海底新都市・輝ける都市・空中都市・海都市・首都・温泉街。
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

pub(super) fn procity(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn newtown(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn bigtown(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn seatown(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn bettown(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn skycity(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn umicity(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn shuto(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn onsen(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}
