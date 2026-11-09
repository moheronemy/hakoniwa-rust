//! 畜産・食品加工・発電・工場・森・倉庫・家・防衛施設・油田・浅瀬・砂浜・氷河・関所・役所・金山・遊園地。
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

pub(super) fn livestock(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn foodka(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn ene_bo(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn ene_so(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn ene_at(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn ht_factory(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn shtf(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn forest(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn kura(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn house(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn defence(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn oil(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn shallow_sea(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn sunahama(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn ice(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn seki(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn yakusho(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn gold(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}

pub(super) fn park(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}
