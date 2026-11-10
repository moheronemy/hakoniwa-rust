//! 最近の出来事の一覧 (Perl 版の `history.cgi`)。
//!
//! 保存しているターンのログ (機密を除く) を新しい順にすべて出す。トップページは
//! `top_log_turns` ターン分だけなので、それより前を見たいとき用。

use std::fmt::Write;
use std::sync::Arc;

use axum::extract::State;
use axum::http::HeaderMap;
use axum::response::{IntoResponse, Response};

use super::{login_of, render};
use crate::AppState;
use crate::layout::esc;
use crate::render::plain;

pub async fn history_page(State(app): State<Arc<AppState>>, headers: HeaderMap) -> Response {
    let login = login_of(&app, &headers).await;
    let mut h = String::from("<h1>最近の出来事</h1>\n<div class=\"log\">\n");
    {
        let game = app.game.read().await;
        for entry in game
            .logs
            .turns
            .iter()
            .flat_map(|t| t.iter())
            .filter(|e| !e.secret)
        {
            let _ = writeln!(
                h,
                "<p>ターン{}：{}</p>",
                entry.turn,
                esc(&plain(&entry.message))
            );
        }
    }
    h.push_str("</div>\n");
    render(&app, login.as_ref(), "最近の出来事", &h)
        .await
        .into_response()
}
