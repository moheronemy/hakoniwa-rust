//! 島の登録 (Perl 版の `newIslandMain`) と、島の名前・パスワード・オーナー名の変更
//! (`changeMain`, `changeOwner`)。

use std::fmt::Write;

use axum::Form;
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Response};
use hakoniwa_core::actions::{self, ActionError};
use serde::Deserialize;

use super::auth::require_login;
use super::owner::finish;
use super::{csrf_ok, error_page, login_of, redirect_with_cookie, render};
use crate::edit::{EditError, edit};
use crate::layout::{csrf_field, esc};
use crate::sets::Set;
use crate::{AppState, now_unix, session, turns};

fn register_form(app: &AppState, error: Option<&str>, f: &RegisterForm) -> String {
    let mut h = String::from("<h1>新しい島を探す</h1>\n");
    if let Some(e) = error {
        let _ = writeln!(h, "<p class=\"error\">{}</p>", esc(e));
    }
    let _ = write!(
        h,
        "<form method=\"post\" action=\"/register\" class=\"card\">\n\
         <label for=\"name\">島の名前 (「島」は付けない)</label>\
         <input id=\"name\" type=\"text\" name=\"name\" value=\"{name}\" maxlength=\"32\" required>\n\
         <label for=\"owner\">あなたの名前</label>\
         <input id=\"owner\" type=\"text\" name=\"owner\" value=\"{owner}\" maxlength=\"32\" required>\n\
         <label for=\"password\">パスワード</label>\
         <input id=\"password\" type=\"password\" name=\"password\" maxlength=\"64\" autocomplete=\"new-password\" required>\n\
         <label for=\"password2\">パスワード (確認)</label>\
         <input id=\"password2\" type=\"password\" name=\"password2\" maxlength=\"64\" autocomplete=\"new-password\" required>\n\
         <label for=\"message\">参加にあたっての意気込み (島のコメントになります)</label>\
         <input id=\"message\" type=\"text\" name=\"message\" value=\"{message}\" maxlength=\"80\" size=\"60\" required>\n\
         <p><button>島を探しに行く</button></p>\n</form>\n\
         <p class=\"muted\">島は最大 {max} 個まで。名前は全角 10 文字 (半角 20 文字) までです。</p>\n",
        name = esc(&f.name),
        owner = esc(&f.owner),
        message = esc(&f.message),
        max = app.config.max_islands,
    );
    h
}

#[derive(Deserialize, Default)]
pub struct RegisterForm {
    #[serde(default)]
    name: String,
    #[serde(default)]
    owner: String,
    #[serde(default)]
    password: String,
    #[serde(default)]
    password2: String,
    #[serde(default)]
    message: String,
}

pub async fn register_page(Set(app): Set, headers: HeaderMap) -> Response {
    let login = login_of(&app, &headers).await;
    let body = register_form(&app, None, &RegisterForm::default());
    render(&app, login.as_ref(), "新しい島", &body)
        .await
        .into_response()
}

pub async fn register(
    Set(app): Set,
    headers: HeaderMap,
    peer: Option<axum::Extension<axum::extract::ConnectInfo<std::net::SocketAddr>>>,
    Form(form): Form<RegisterForm>,
) -> Response {
    // Perl 版は時刻が来ていれば先にターンを進めた
    if let Err(e) = turns::run_due_turns(&app, now_unix()).await {
        tracing::error!("ターン処理に失敗しました: {e:#}");
    }
    let addr = super::remote_addr(&app, &headers, peer.map(|p| (p.0).0));
    let req = actions::Request {
        now: now_unix(),
        remote_addr: &addr,
    };
    let input = actions::create::NewIslandInput {
        name: &form.name,
        owner_name: &form.owner,
        password: &form.password,
        password2: &form.password2,
        message: &form.message,
    };
    let config = &app.config;
    let result = edit(&app, |game, rng| {
        let id = actions::create::new_island(game, config, req, rng, &input)?;
        let name = game
            .world
            .islands
            .iter()
            .find(|i| i.id == id)
            .map(|i| i.name.clone());
        Ok((id, name.unwrap_or_default()))
    })
    .await;
    match result {
        Ok((id, name)) => {
            let token = app.sessions.create(id, false, now_unix());
            app.sessions.set_flash(
                &token,
                format!("島を発見しました！！「{name}島」と命名します。"),
            );
            redirect_with_cookie(
                "/owner",
                session::set_cookie(&token, app.options.secure_cookie),
            )
        }
        Err(EditError::Action(e)) => {
            let message = match &e {
                ActionError::WrongPassword => "パスワードが確認用と一致しません。".to_string(),
                e => e.to_string(),
            };
            let body = register_form(&app, Some(&message), &form);
            (
                StatusCode::BAD_REQUEST,
                render(&app, None, "新しい島", &body).await,
            )
                .into_response()
        }
        Err(e) => {
            error_page(
                &app,
                None,
                StatusCode::INTERNAL_SERVER_ERROR,
                &e.to_string(),
            )
            .await
        }
    }
}

/// 開発画面に出す、名前・パスワード・オーナー名の変更の欄
pub fn change_forms(app: &AppState, csrf: &str) -> String {
    format!(
        "<h2>島の名前とパスワードの変更</h2>\n\
         <form method=\"post\" action=\"/owner/change\" class=\"card\">{csrf}\n\
         <p class=\"muted\">名前の変更には {cost}{unit} かかります。変えない欄は空のままにします。</p>\n\
         <label for=\"c-name\">新しい島の名前</label><input id=\"c-name\" type=\"text\" name=\"name\" maxlength=\"32\">\n\
         <label for=\"c-pw\">新しいパスワード</label><input id=\"c-pw\" type=\"password\" name=\"password\" maxlength=\"64\" autocomplete=\"new-password\">\n\
         <label for=\"c-pw2\">新しいパスワード (確認)</label><input id=\"c-pw2\" type=\"password\" name=\"password2\" maxlength=\"64\" autocomplete=\"new-password\">\n\
         <label for=\"c-old\">いまのパスワード</label><input id=\"c-old\" type=\"password\" name=\"old_password\" maxlength=\"64\" autocomplete=\"current-password\" required>\n\
         <p><button>変更する</button></p>\n</form>\n\
         <form method=\"post\" action=\"/owner/change-owner\" class=\"card\">{csrf}\n\
         <label for=\"o-name\">新しいオーナー名</label><input id=\"o-name\" type=\"text\" name=\"owner\" maxlength=\"32\" required>\n\
         <label for=\"o-old\">いまのパスワード</label><input id=\"o-old\" type=\"password\" name=\"old_password\" maxlength=\"64\" autocomplete=\"current-password\" required>\n\
         <p><button>オーナー名を変える</button></p>\n</form>\n",
        csrf = csrf_field(csrf),
        cost = app.config.cost_change_name,
        unit = esc(&app.config.units.money),
    )
}

#[derive(Deserialize)]
pub struct ChangeForm {
    #[serde(default)]
    csrf: String,
    #[serde(default)]
    old_password: String,
    #[serde(default)]
    name: String,
    #[serde(default)]
    owner: String,
    #[serde(default)]
    password: String,
    #[serde(default)]
    password2: String,
}

pub async fn change(Set(app): Set, headers: HeaderMap, Form(form): Form<ChangeForm>) -> Response {
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
    let input = actions::change::ChangeInput {
        old_password: &form.old_password,
        name: &form.name,
        owner_name: "",
        password: &form.password,
        password2: &form.password2,
    };
    let config = &app.config;
    let result = edit(&app, |game, _| {
        actions::change::change_info(game, config, id, &input)
    })
    .await;
    finish(&app, &login, result, actions::change::MSG_CHANGED).await
}

pub async fn change_owner(
    Set(app): Set,
    headers: HeaderMap,
    Form(form): Form<ChangeForm>,
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
    let config = &app.config;
    let result = edit(&app, |game, _| {
        actions::change::change_owner(game, config, id, &form.old_password, &form.owner)
    })
    .await;
    finish(&app, &login, result, "オーナー名を変更しました").await
}
