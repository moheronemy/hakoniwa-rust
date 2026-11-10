//! 全部の島のログのページ送り (最近の出来事)。
//!
//! 大きな地図・多くの島では 1 ターンのログが数百万行になる (docs/SCALING.md)。
//! Perl 版の `history.cgi` とトップページは保存しているログをすべて出すが、移植版は
//! 1 ページに決まった行数だけを出し、続きはページを送って見る。ページの中の行
//! (機密でない行、保存された順) と文面は Perl 版のとおり。

use crate::model::{GameState, TurnMessage};

/// 1 ページ分
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PublicLogPage {
    /// 何ターン前のログか (0 が最新)
    pub index: usize,
    /// 保存しているターンのログの数
    pub turn_count: usize,
    /// このログのターン (行が無ければ `None`)
    pub turn: Option<i64>,
    /// このターンのログの行数 (機密の行も含む)
    pub total: usize,
    /// このページの最初の行の位置 (0 から。機密の行も数える)
    pub start: usize,
    /// 機密でない行 (保存された順)
    pub lines: Vec<TurnMessage>,
    /// 続きのページの `start` (このターンの終わりまで出したら `None`)
    pub next: Option<usize>,
}

/// `index` ターン前のログの、`start` 行目から機密でない行を `limit` 行まで。
/// `index` が保存しているターンの数を超えていれば `None`
pub fn public_logs(
    game: &GameState,
    index: usize,
    start: usize,
    limit: usize,
) -> Option<PublicLogPage> {
    let log = game.logs.turns.get(index)?;
    let mut lines = Vec::new();
    let mut next = None;
    let mut turn = None;
    for (pos, entry) in log.iter_from(start) {
        turn.get_or_insert(entry.turn);
        if entry.secret {
            continue;
        }
        if lines.len() == limit {
            next = Some(pos);
            break;
        }
        lines.push(TurnMessage {
            turn: entry.turn,
            message: entry.message,
        });
    }
    if turn.is_none() {
        turn = log.iter_from(0).next().map(|(_, e)| e.turn);
    }
    Some(PublicLogPage {
        index,
        turn_count: game.logs.turns.len(),
        turn,
        total: log.len(),
        start,
        lines,
        next,
    })
}

#[cfg(test)]
mod tests {
    use std::sync::Arc;

    use super::*;
    use crate::config::GameConfig;
    use crate::model::LogEntry;
    use crate::turn_log::TurnLog;

    fn game() -> GameState {
        let mut g = GameState::new_game(0, &GameConfig::default());
        let log = |turn: i64, n: usize| {
            Arc::new(TurnLog::new(
                (0..n)
                    .map(|i| LogEntry {
                        secret: i % 3 == 2,
                        turn,
                        island1: Some(1),
                        island2: None,
                        message: format!("{turn}-{i}"),
                    })
                    .collect(),
            ))
        };
        g.logs.turns = vec![log(5, 3000), log(4, 2)];
        g
    }

    #[test]
    fn pages_skip_secret_lines_and_continue() {
        let g = game();
        let p = public_logs(&g, 0, 0, 10).unwrap();
        assert_eq!(p.turn, Some(5));
        assert_eq!(p.turn_count, 2);
        assert_eq!(p.total, 3000);
        let msgs: Vec<_> = p.lines.iter().map(|l| l.message.as_str()).collect();
        assert_eq!(msgs[..4], ["5-0", "5-1", "5-3", "5-4"]);
        assert_eq!(p.lines.len(), 10);
        // 10 行目 (機密でない行の 11 番目) は 15 行目 (0 から)
        assert_eq!(p.next, Some(15));

        // ページを送ると、機密でない行を 1 行も落とさずに最後まで読める
        let mut all = Vec::new();
        let mut start = 0;
        loop {
            let p = public_logs(&g, 0, start, 700).unwrap();
            all.extend(p.lines);
            match p.next {
                Some(n) => start = n,
                None => break,
            }
        }
        assert_eq!(all.len(), 2000);
        assert_eq!(all.last().unwrap().message, "5-2998"); // 2999 は機密

        let p = public_logs(&g, 1, 0, 10).unwrap();
        assert_eq!((p.turn, p.lines.len(), p.next), (Some(4), 2, None));
        assert!(public_logs(&g, 2, 0, 10).is_none());
        // 終わりより後ろから読んでも、ターンはわかる
        let p = public_logs(&g, 0, 5000, 10).unwrap();
        assert_eq!((p.turn, p.lines.len(), p.next), (Some(5), 0, None));
    }
}
