//! 地盤沈下・台風・巨大隕石・巨大ミサイル・隕石・噴火 (Perl 版 15248〜15665 行)。
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
