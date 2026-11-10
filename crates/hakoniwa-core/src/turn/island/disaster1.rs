//! 地震・重税への反発・食料不足・海底首都・津波・怪獣の出現 (Perl 版 14850〜15247 行)。
//!
//! TODO(フェーズ4): Perl 版の該当する部分を移植する。いまは何もしない。

use crate::model::Island;
use crate::turn::TurnContext;

use super::ProcRun;

/// この段階で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {}

/// この段階で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

pub(super) fn run(_ctx: &mut TurnContext, _islands: &mut [Island], _idx: usize, _p: &mut ProcRun) {}
