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
        let idx = actions::island_index(&game.world, island.id).unwrap_or_default();
        let view = hakoniwa_core::view::island_view(
            &game.world,
            &app.config,
            idx,
            hakoniwa_core::view::Viewer::Owner {
                master: login.session.master,
            },
        );
        format!(
            "<h1>{name}島開発計画</h1>\n{info}{map}\n\
             <h2>コメント</h2>\n<form method=\"post\" action=\"/owner/comment\" class=\"card\">{csrf}\n\
             <label for=\"message\">島のコメント</label>\n\
             <input id=\"message\" type=\"text\" name=\"message\" value=\"{comment}\" maxlength=\"80\" size=\"60\">\n\
             <p><button>コメントを変える</button></p>\n</form>\n{lbbs}{change}",
            change = super::register::change_forms(&app, &login.session.csrf),
            lbbs = if app.config.lbbs.enabled {
                owner_lbbs(&app.config, island, &login.session.csrf)
            } else {
                String::new()
            },
            name = esc(&island.name),
            info = crate::render::info_html(&view.info),
            map = crate::render::map_html(&view, app.options.image_dir.is_some(), true),
            csrf = csrf_field(&login.session.csrf),
            // コメントは保存の時点でエスケープ済み (Perl 版と同じ)。入力欄に戻すときは元の文字に戻す
            comment = esc(&unescape(&island.comment)),
        )
    };
    render(&app, Some(&login), "開発画面", &body)
        .await
        .into_response()
}

/// 開発画面の掲示板の欄 (島主の書き込みと削除。極秘の書き込みも見える)
fn owner_lbbs(
    config: &hakoniwa_core::GameConfig,
    island: &hakoniwa_core::model::Island,
    csrf: &str,
) -> String {
    use hakoniwa_core::actions::lbbs::{LbbsViewer, lbbs_posts};
    let posts = lbbs_posts(island, config, LbbsViewer::Owner);
    format!(
        "<h2>{name}島観光者通信</h2>\n<form method=\"post\" action=\"/owner/lbbs\" class=\"card\">{csrf}\n\
         <label for=\"lbbs-name\">名前</label><input id=\"lbbs-name\" type=\"text\" name=\"name\" maxlength=\"32\" required>\n\
         <label for=\"lbbs-message\">内容</label><input id=\"lbbs-message\" type=\"text\" name=\"message\" maxlength=\"80\" size=\"60\">\n\
         <p><button>記帳する</button></p>\n</form>\n{list}",
        name = esc(&island.name),
        csrf = csrf_field(csrf),
        list = super::island::lbbs_list(&posts, Some(csrf)),
    )
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

/// フォームの CSRF 対策のトークンとログインを確かめる
async fn guard(app: &AppState, headers: &HeaderMap, csrf: &str) -> Result<super::Login, Response> {
    let Some(login) = login_of(app, headers).await else {
        return Err(require_login(app).await);
    };
    if !csrf_ok(&login, csrf) {
        return Err(error_page(
            app,
            Some(&login),
            StatusCode::FORBIDDEN,
            "画面を開き直してください。",
        )
        .await);
    }
    Ok(login)
}

#[derive(Deserialize)]
pub struct CommandForm {
    #[serde(default)]
    csrf: String,
    #[serde(default)]
    number: usize,
    #[serde(default)]
    mode: String,
    #[serde(default)]
    kind: String,
    #[serde(default)]
    amount: String,
    #[serde(default)]
    target: String,
    #[serde(default)]
    x: String,
    #[serde(default)]
    y: String,
    #[serde(default)]
    lamount1: String,
    #[serde(default)]
    lamount2: String,
}

/// 計画の入力 (Perl 版の `commandMain`)
pub async fn command(
    State(app): State<Arc<AppState>>,
    headers: HeaderMap,
    peer: Option<axum::Extension<axum::extract::ConnectInfo<std::net::SocketAddr>>>,
    Form(form): Form<CommandForm>,
) -> Response {
    let login = match guard(&app, &headers, &form.csrf).await {
        Ok(l) => l,
        Err(r) => return r,
    };
    // いじり (デバッグ用の書き換え) はマスターパスワードでログインしたときだけ
    let ijiri = hakoniwa_core::tables::CommandKind::Ijiri as u16;
    if hakoniwa_core::perl::int(&form.kind) == ijiri as i64 && !login.session.master {
        return error_page(
            &app,
            Some(&login),
            StatusCode::FORBIDDEN,
            "この計画は使えません。",
        )
        .await;
    }
    let addr = super::remote_addr(&app, &headers, peer.map(|p| (p.0).0));
    let id = login.session.island_id;
    let input = actions::command::CommandInput {
        number: form.number,
        mode: actions::command::CommandMode::from_form(&form.mode),
        kind: &form.kind,
        amount: &form.amount,
        target: &form.target,
        x: &form.x,
        y: &form.y,
        lamount1: &form.lamount1,
        lamount2: &form.lamount2,
    };
    let req = actions::Request {
        now: crate::now_unix(),
        remote_addr: &addr,
    };
    let config = &app.config;
    let result = edit(&app, |game, rng| {
        actions::command::input_command(game, config, req, rng, id, &input)
    })
    .await;
    let message = match &result {
        Ok(actions::command::CommandOutcome::Deleted) => "計画を削除しました",
        Ok(actions::command::CommandOutcome::Edited) => "書き換えました",
        _ => "計画を登録しました",
    };
    finish(&app, &login, result.map(|_| ()), message).await
}

#[derive(Deserialize)]
pub struct PolicyForm {
    #[serde(default)]
    csrf: String,
    policy: String,
    #[serde(default)]
    amount: String,
}

/// 政策の予算 (Perl 版の `shoueneMain` など)
pub async fn policy(
    State(app): State<Arc<AppState>>,
    headers: HeaderMap,
    Form(form): Form<PolicyForm>,
) -> Response {
    use actions::policy::Policy;
    let login = match guard(&app, &headers, &form.csrf).await {
        Ok(l) => l,
        Err(r) => return r,
    };
    let policy = match form.policy.as_str() {
        "shouene" => Policy::Shouene,
        "bousai" => Policy::Bousai,
        "kankou" => Policy::Kankou,
        "sizen" => Policy::Sizen,
        "kyouiku" => Policy::Kyouiku,
        "chochiku" => Policy::Chochiku,
        _ => {
            return error_page(
                &app,
                Some(&login),
                StatusCode::BAD_REQUEST,
                "政策の種類が違います。",
            )
            .await;
        }
    };
    let id = login.session.island_id;
    let result = edit(&app, |game, _| {
        actions::policy::set_policy(game, id, policy, &form.amount)
    })
    .await;
    finish(&app, &login, result, "政策を変更しました").await
}

#[derive(Deserialize)]
pub struct LbbsForm {
    #[serde(default)]
    csrf: String,
    #[serde(default)]
    name: String,
    #[serde(default)]
    message: String,
    /// 削除するときの番号 (0 始まり)
    delete: Option<usize>,
}

/// 自分の島の掲示板への書き込みと削除
pub async fn lbbs(
    State(app): State<Arc<AppState>>,
    headers: HeaderMap,
    Form(form): Form<LbbsForm>,
) -> Response {
    let login = match guard(&app, &headers, &form.csrf).await {
        Ok(l) => l,
        Err(r) => return r,
    };
    let id = login.session.island_id;
    let config = &app.config;
    match form.delete {
        Some(n) => {
            let result = edit(&app, |game, _| {
                actions::lbbs::owner_delete(game, config, id, n)
            })
            .await;
            finish(&app, &login, result, "記帳内容を削除しました").await
        }
        None => {
            let result = edit(&app, |game, _| {
                actions::lbbs::owner_post(game, config, id, &form.name, &form.message)
            })
            .await;
            finish(&app, &login, result, "記帳を行いました").await
        }
    }
}
