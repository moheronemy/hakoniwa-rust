//! 失業者の移民 (doIslandunemployed、Perl 版 14388〜14569 行) と、リゾートに飽きられた住民の移住 (14635〜14849 行)。
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

pub(super) fn unemployed(_ctx: &mut TurnContext, _islands: &mut [Island], _idx: usize) {}

pub(super) fn resort_fatigue(
    _ctx: &mut TurnContext,
    _islands: &mut [Island],
    _idx: usize,
    _p: &mut ProcRun,
) {
}
