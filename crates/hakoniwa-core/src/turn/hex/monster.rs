//! 怪獣。
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

/// doEachHex 1 回分の状態 (`@monsterMove` など)
#[derive(Debug, Default)]
pub struct RunState {}

pub(super) fn monster(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _h: &mut HexRun,
) -> Flow {
    Flow::Continue
}
