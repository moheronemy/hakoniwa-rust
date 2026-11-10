//! 開発画面 (Perl 版の `ownerMain` / `tempOwner`) と、そこからの操作。

use std::sync::Arc;

use axum::Form;
use axum::extract::State;
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Response};
use hakoniwa_core::actions::{self, ActionError};
use serde::Deserialize;

use super::auth::require_login;
use super::{csrf_ok, error_page, login_of, redirect_with_flash, render};
use crate::AppState;
use crate::edit::{EditError, edit};
use crate::layout::{csrf_field, esc};

pub async fn owner_page(State(app): State<Arc<AppState>>, headers: HeaderMap) -> Response {
    let Some(login) = login_of(&app, &headers).await else {
        return require_login(&app).await;
    };
    let body = {
        let game = app.game.read().await;
        let Some(island) = game
            .world
            .islands
            .iter()
            .find(|i| i.id == login.session.island_id)
        else {
            return require_login(&app).await;
        };
        format!(
            "<h1>{name}島開発計画</h1>\n\
             <h2>コメント</h2>\n<form method=\"post\" action=\"/owner/comment\" class=\"card\">{csrf}\n\
             <label for=\"message\">島のコメント</label>\n\
             <input id=\"message\" type=\"text\" name=\"message\" value=\"{comment}\" maxlength=\"80\" size=\"60\">\n\
             <p><button>コメントを変える</button></p>\n</form>\n",
            name = esc(&island.name),
            csrf = csrf_field(&login.session.csrf),
            // コメントは保存の時点でエスケープ済み (Perl 版と同じ)。入力欄に戻すときは元の文字に戻す
            comment = esc(&unescape(&island.comment)),
        )
    };
    render(&app, Some(&login), "開発画面", &body)
        .await
        .into_response()
}

/// `htmlEscape` で保存した文字を元に戻す (入力欄の初期値に使う)
pub fn unescape(s: &str) -> String {
    s.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", "\"")
        .replace("&amp;", "&")
}

#[derive(Deserialize)]
pub struct CommentForm {
    #[serde(default)]
    csrf: String,
    #[serde(default)]
    message: String,
}

/// 操作の結果を画面に出す。成功なら開発画面へ戻る
pub async fn finish(
    app: &AppState,
    login: &super::Login,
    result: Result<(), EditError>,
    done: &str,
) -> Response {
    match result {
        Ok(()) => redirect_with_flash(app, login, "/owner", done),
        Err(EditError::Action(e @ ActionError::WrongPassword)) => {
            error_page(app, Some(login), StatusCode::FORBIDDEN, &e.to_string()).await
        }
        Err(EditError::Action(e)) => redirect_with_flash(app, login, "/owner", e.to_string()),
        Err(e @ EditError::Save(_)) => {
            tracing::error!("{e}");
            error_page(
                app,
                Some(login),
                StatusCode::INTERNAL_SERVER_ERROR,
                &e.to_string(),
            )
            .await
        }
    }
}

pub async fn comment(
    State(app): State<Arc<AppState>>,
    headers: HeaderMap,
    Form(form): Form<CommentForm>,
) -> Response {
    let Some(login) = login_of(&app, &headers).await else {
        return require_login(&app).await;
    };
    if !csrf_ok(&login, &form.csrf) {
        return error_page(
            &app,
            Some(&login),
            StatusCode::FORBIDDEN,
            "画面を開き直してください。",
        )
        .await;
    }
    let id = login.session.island_id;
    let result = edit(&app, |game, _| {
        actions::owner::set_comment(game, id, &form.message)
    })
    .await;
    finish(&app, &login, result, "コメントを更新しました").await
}
