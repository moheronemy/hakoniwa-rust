//! ログインとログアウト (Perl 版の「開発しに行く」)。
//!
//! パスワードの照合は `hakoniwa_core::actions::password` (Perl 版の DES crypt にも対応)。
//! Perl 版から移した島の DES crypt は、ログインに成功したときに新しい形式で保存し直す。

use std::fmt::Write;
use std::sync::Arc;

use axum::Form;
use axum::extract::State;
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Response};
use hakoniwa_core::actions::password::{self, check_password, hash_password};
use serde::Deserialize;

use super::{csrf_ok, error_page, login_of, redirect_with_cookie, render};
use crate::edit::edit;
use crate::layout::esc;
use crate::session;
use crate::{AppState, now_unix};

/// 島を選ぶ `<option>` の並び (順位の順)
pub async fn island_options(app: &AppState, selected: Option<i64>) -> String {
    let game = app.game.read().await;
    let mut h = String::new();
    for island in &game.world.islands {
        let _ = writeln!(
            h,
            "<option value=\"{id}\"{sel}>{name}島</option>",
            id = island.id,
            sel = if Some(island.id) == selected {
                " selected"
            } else {
                ""
            },
            name = esc(&island.name)
        );
    }
    h
}

fn login_form(options: &str, error: Option<&str>) -> String {
    format!(
        "<h1>自分の島へ</h1>\n{err}<form method=\"post\" action=\"/login\" class=\"card\">\n\
         <label for=\"island\">あなたの島</label>\n<select id=\"island\" name=\"island\" required>\n{options}</select>\n\
         <label for=\"password\">パスワード</label>\n\
         <input id=\"password\" type=\"password\" name=\"password\" maxlength=\"64\" autocomplete=\"current-password\" required>\n\
         <p><button>開発しに行く</button></p>\n</form>\n\
         <p class=\"muted\">島をまだ持っていない人は<a href=\"/register\">新しい島を探す</a>。</p>\n",
        err = error
            .map(|e| format!("<p class=\"error\">{}</p>\n", esc(e)))
            .unwrap_or_default()
    )
}

pub async fn login_page(State(app): State<Arc<AppState>>, headers: HeaderMap) -> Response {
    let login = login_of(&app, &headers).await;
    let options = island_options(&app, login.as_ref().map(|l| l.session.island_id)).await;
    render(
        &app,
        login.as_ref(),
        "ログイン",
        &login_form(&options, None),
    )
    .await
    .into_response()
}

#[derive(Deserialize)]
pub struct LoginForm {
    island: i64,
    password: String,
}

pub async fn login(State(app): State<Arc<AppState>>, Form(form): Form<LoginForm>) -> Response {
    let now = now_unix();
    let (ok, master, legacy) = {
        let game = app.game.read().await;
        match game.world.islands.iter().find(|i| i.id == form.island) {
            Some(island) => {
                let master = app.config.passwords.master.as_deref() == Some(form.password.as_str());
                (
                    check_password(&app.config, &island.password, &form.password),
                    master,
                    password::is_legacy(&island.password),
                )
            }
            None => (false, false, false),
        }
    };
    if !ok {
        let options = island_options(&app, Some(form.island)).await;
        let body = login_form(&options, Some("パスワードが違います。"));
        return (
            StatusCode::UNAUTHORIZED,
            render(&app, None, "ログイン", &body).await,
        )
            .into_response();
    }
    // Perl 版の DES crypt は先頭 8 文字しか見ないので、新しい形式で保存し直す
    if legacy && !master {
        let id = form.island;
        let hash = hash_password(&form.password);
        if let Err(e) = edit(&app, |game, _| {
            if let Some(island) = game.world.islands.iter_mut().find(|i| i.id == id) {
                island.password = hash;
            }
            Ok(())
        })
        .await
        {
            tracing::warn!("パスワードの形式を新しくできませんでした: {e}");
        }
    }
    let token = app.sessions.create(form.island, master, now);
    redirect_with_cookie(
        "/owner",
        session::set_cookie(&token, app.options.secure_cookie),
    )
}

#[derive(Deserialize)]
pub struct CsrfForm {
    #[serde(default)]
    csrf: String,
}

pub async fn logout(
    State(app): State<Arc<AppState>>,
    headers: HeaderMap,
    Form(form): Form<CsrfForm>,
) -> Response {
    match login_of(&app, &headers).await {
        Some(login) if csrf_ok(&login, &form.csrf) => {
            app.sessions.remove(&login.token);
            redirect_with_cookie("/", session::clear_cookie())
        }
        Some(login) => {
            error_page(
                &app,
                Some(&login),
                StatusCode::FORBIDDEN,
                "画面を開き直してください。",
            )
            .await
        }
        None => redirect_with_cookie("/", session::clear_cookie()),
    }
}

/// ログインが要る画面で、ログインしていなかったとき
pub async fn require_login(app: &AppState) -> Response {
    let options = island_options(app, None).await;
    let body = login_form(&options, Some("ログインしてください。"));
    (
        StatusCode::UNAUTHORIZED,
        render(app, None, "ログイン", &body).await,
    )
        .into_response()
}
