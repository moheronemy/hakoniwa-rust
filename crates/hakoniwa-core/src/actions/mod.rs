//! 画面からの操作 (島の登録・計画の入力・コメント・掲示板・名前の変更・政策など)。
//!
//! Perl 版では `hako-main.cgi` の `$HmainMode` ごとの処理 (`newIslandMain`, `commandMain`,
//! `commentMain`, `localBbsMain`, `changeMain`, ...) に当たる。画面は作り直すが、
//! データの変え方 (費用・上限・文字の加工・乱数の使い方・Perl 版の癖) は Perl 版のとおりにする。
//!
//! 操作はどれも「入力を受け取り、[`GameState`](crate::GameState) を書き換えて結果を返す」
//! 関数にする。HTTP・セッション・HTML はサーバー側 (`hakoniwa-server`) の仕事で、ここには置かない。
//!
//! 検証は `perl_compat_tests`: 元の Perl CGI に同じ操作を送った結果
//! (`tools/perl-harness/run_cgi.py` が `tests/fixtures/cgi/` に作る) と突き合わせる。

pub mod auction;
pub mod change;
pub mod command;
pub mod create;
pub mod dispatch;
pub mod lbbs;
pub mod owner;
pub mod password;
pub mod policy;
pub mod survey;
pub mod toto;

use crate::model::World;

/// 操作が受け付けられなかった理由。Perl 版の `temp*` のエラー画面に当たる
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum ActionError {
    /// `tempProblem` (島が見つからない)
    #[error("島が見つかりません")]
    NoSuchIsland,
    /// `tempWrongPassword`
    #[error("パスワードが違います")]
    WrongPassword,
    /// そのほかの理由。文面は Perl 版の画面に出るものに合わせる
    #[error("{0}")]
    Rejected(String),
}

/// 操作を送ってきた人の情報 (Perl 版の `$ENV{'REMOTE_ADDR'}` と `time`)
#[derive(Debug, Clone, Copy)]
pub struct Request<'a> {
    /// いまの時刻 (Unix 秒)
    pub now: i64,
    /// 接続元のアドレス (`REMOTE_HOST` が無ければ `REMOTE_ADDR`)
    pub remote_addr: &'a str,
}

/// `$HidToNumber{$id}`: 島 ID から配列の位置を探す
pub fn island_index(world: &World, id: i64) -> Option<usize> {
    world.islands.iter().position(|i| i.id == id)
}

#[cfg(test)]
pub(crate) mod perl_compat_tests;
