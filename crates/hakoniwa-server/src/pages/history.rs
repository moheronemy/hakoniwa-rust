//! 最近の出来事 (Perl 版の `history.cgi`)。
//!
//! Perl 版は保存しているターンのログ (機密を除く) を新しい順にすべて出す。多くの島・大きな地図では
//! 1 ターンのログが数百万行になるので、移植版はターンごとに `history_page_lines` 行ずつページを送る
//! (`/history?turn=<何ターン前か>&from=<行の位置>`)。

use std::fmt::Write;

use axum::extract::Query;
use axum::http::HeaderMap;
use axum::response::{IntoResponse, Response};
use hakoniwa_core::view::logs::public_logs;
use serde::Deserialize;

use super::{login_of, render};
use crate::layout::esc;
use crate::render::plain;
use crate::sets::Set;

#[derive(Debug, Deserialize)]
pub struct HistoryQuery {
    /// 何ターン前のログか (0 が最新)
    #[serde(default)]
    turn: usize,
    /// 行の位置
    #[serde(default)]
    from: usize,
}

pub async fn history_page(
    Set(app): Set,
    headers: HeaderMap,
    Query(q): Query<HistoryQuery>,
) -> Response {
    let login = login_of(&app, &headers).await;
    let game = app.game.read().await;
    let mut h = String::from("<h1>最近の出来事</h1>\n");
    let limit = app.options.history_page_lines.max(1);
    match public_logs(&game, q.turn, q.from, limit) {
        None => h.push_str("<p class=\"muted\">このターンのログはありません。</p>\n"),
        Some(page) => {
            // ターンを選ぶ
            h.push_str("<nav class=\"pager\">");
            for i in 0..page.turn_count {
                let label = match public_logs(&game, i, usize::MAX, 0).and_then(|p| p.turn) {
                    Some(t) => format!("ターン{t}"),
                    None => format!("{i}ターン前"),
                };
                if i == page.index {
                    let _ = write!(h, "<strong>{label}</strong> ");
                } else {
                    let _ = write!(h, "<a href=\"/history?turn={i}\">{label}</a> ");
                }
            }
            h.push_str("</nav>\n");
            let _ = writeln!(
                h,
                "<p class=\"muted\">全 {} 行 (機密を含む) のうち {} 行目から</p>",
                page.total,
                page.start.min(page.total) + 1
            );
            h.push_str("<div class=\"log\">\n");
            for m in &page.lines {
                let _ = writeln!(h, "<p>ターン{}：{}</p>", m.turn, esc(&plain(&m.message)));
            }
            h.push_str("</div>\n<nav class=\"pager\">");
            if page.start > 0 {
                let _ = write!(
                    h,
                    "<a href=\"/history?turn={}\">このターンの最初へ</a> ",
                    page.index
                );
            }
            match page.next {
                Some(next) => {
                    let _ = write!(
                        h,
                        "<a href=\"/history?turn={}&amp;from={next}\">続き</a>",
                        page.index
                    );
                }
                None if page.index + 1 < page.turn_count => {
                    let _ = write!(
                        h,
                        "<a href=\"/history?turn={}\">前のターン</a>",
                        page.index + 1
                    );
                }
                None => {}
            }
            h.push_str("</nav>\n");
        }
    }
    drop(game);
    render(&app, login.as_ref(), "最近の出来事", &h)
        .await
        .into_response()
}
