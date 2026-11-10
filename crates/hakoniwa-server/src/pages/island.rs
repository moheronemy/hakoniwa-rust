//! 観光画面 (Perl 版の `printIslandMain`) と、ほかの島の掲示板への書き込み。

use std::fmt::Write;
use std::sync::Arc;

use axum::Form;
use axum::extract::{Path, State};
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Redirect, Response};
use hakoniwa_core::GameConfig;
use hakoniwa_core::actions::lbbs::{
    LbbsPost, LbbsViewer, VisitorSpeaker, lbbs_posts, visitor_post,
};
use hakoniwa_core::actions::{self, ActionError};
use hakoniwa_core::model::Island;
use serde::Deserialize;

use super::{csrf_ok, error_page, login_of, redirect_with_flash, render};
use crate::AppState;
use crate::edit::{EditError, edit};
use crate::layout::{csrf_field, esc};

/// 掲示板の一覧 (Perl 版の `tempLbbsContents`)。`delete_csrf` があれば削除のボタンを付ける
pub fn lbbs_list(posts: &[LbbsPost], delete_csrf: Option<&str>) -> String {
    let mut h = String::from("<div class=\"table-scroll\"><table class=\"lbbs\">\n");
    let mut any = false;
    for post in posts {
        let Some(c) = &post.content else {
            any = true;
            let _ = writeln!(
                h,
                "<tr><td class=\"num\">{}</td><td class=\"muted\">- 極秘 -</td><td></td></tr>",
                post.number
            );
            continue;
        };
        if c.name.is_empty() && c.message.is_empty() {
            continue;
        }
        any = true;
        // 名前と本文は保存の時点でエスケープ済み (Perl 版と同じ)
        let _ = write!(
            h,
            "<tr><td class=\"num\">{n}</td><td>{who}<b>{name}</b>{secret}<br>{message}{speaker}</td><td>",
            n = post.number,
            who = if post.by_owner {
                "<span class=\"muted\">島主</span> "
            } else {
                ""
            },
            name = c.name,
            secret = if post.secret {
                " <span class=\"muted\">(秘)</span>"
            } else {
                ""
            },
            message = c.message,
            speaker = c
                .speaker
                .as_ref()
                .map(|s| format!(" <span class=\"muted\">({})</span>", esc(s)))
                .unwrap_or_default(),
        );
        if let Some(csrf) = delete_csrf {
            let _ = write!(
                h,
                "<form method=\"post\" action=\"/owner/lbbs\">{}<input type=\"hidden\" name=\"delete\" value=\"{}\"><button class=\"secondary\">削除</button></form>",
                csrf_field(csrf),
                post.number - 1
            );
        }
        h.push_str("</td></tr>\n");
    }
    h.push_str("</table></div>\n");
    if !any {
        return "<p class=\"muted\">まだ書き込みはありません。</p>\n".into();
    }
    h
}

/// 観光画面の掲示板の欄
fn visitor_lbbs(config: &GameConfig, island: &Island, csrf: Option<&str>) -> String {
    let posts = lbbs_posts(island, config, LbbsViewer::Visitor);
    let mut h = format!("<h2>{}島観光者通信</h2>\n", esc(&island.name));
    let mut types = String::new();
    if csrf.is_some() {
        let _ = write!(
            types,
            "<label><input type=\"radio\" name=\"kind\" value=\"public\" checked> 公開 ({}{})</label>\
             <label><input type=\"radio\" name=\"kind\" value=\"secret\"> 極秘 ({}{})</label>",
            config.lbbs.cost_public,
            esc(&config.units.money),
            config.lbbs.cost_secret,
            esc(&config.units.money),
        );
    }
    if config.lbbs.allow_anonymous {
        let _ = write!(
            types,
            "<label><input type=\"radio\" name=\"kind\" value=\"anonymous\"{}> 匿名</label>",
            if csrf.is_none() { " checked" } else { "" }
        );
    }
    if types.is_empty() {
        h.push_str(
            "<p class=\"muted\">書き込むには<a href=\"/login\">ログイン</a>してください。</p>\n",
        );
    } else {
        let _ = write!(
            h,
            "<form method=\"post\" action=\"/island/{id}/lbbs\" class=\"card\">{csrf}\n\
             <label for=\"lbbs-name\">名前</label><input id=\"lbbs-name\" type=\"text\" name=\"name\" maxlength=\"32\" required>\n\
             <label for=\"lbbs-message\">内容</label><input id=\"lbbs-message\" type=\"text\" name=\"message\" maxlength=\"80\" size=\"60\">\n\
             <div>{types}</div>\n<p><button>記帳する</button></p>\n</form>\n",
            id = island.id,
            csrf = csrf.map(csrf_field).unwrap_or_default(),
        );
    }
    h.push_str(&lbbs_list(&posts, None));
    h
}

pub async fn island_page(
    State(app): State<Arc<AppState>>,
    headers: HeaderMap,
    Path(id): Path<i64>,
) -> Response {
    let login = login_of(&app, &headers).await;
    let body = {
        let game = app.game.read().await;
        let Some(island) = game.world.islands.iter().find(|i| i.id == id) else {
            drop(game);
            return error_page(
                &app,
                login.as_ref(),
                StatusCode::NOT_FOUND,
                "その島は見つかりません。",
            )
            .await;
        };
        let view = match hakoniwa_core::view::sightseeing(&game, &app.config, id) {
            Ok(v) => v,
            Err(e) => {
                drop(game);
                return error_page(&app, login.as_ref(), StatusCode::NOT_FOUND, &e.to_string())
                    .await;
            }
        };
        let mut h = format!(
            "<h1>「{name}島」へようこそ！！</h1>\n<p>{comment}</p>\n{info}{map}",
            name = esc(&island.name),
            // コメントは保存の時点でエスケープ済み
            comment = island.comment,
            info = crate::render::info_html(&view.info),
            map = crate::render::map_html(&view, app.options.image_dir.is_some(), false),
        );
        let recent = crate::render::recent_html(
            &island.name,
            &hakoniwa_core::view::recent_logs(&game, &app.config, id, false),
        );
        if app.config.lbbs.enabled {
            h.push_str(&visitor_lbbs(
                &app.config,
                island,
                login.as_ref().map(|l| l.session.csrf.as_str()),
            ));
        }
        h.push_str(&recent);
        h
    };
    render(&app, login.as_ref(), "観光", &body)
        .await
        .into_response()
}

#[derive(Deserialize)]
pub struct VisitorLbbsForm {
    #[serde(default)]
    csrf: String,
    #[serde(default)]
    name: String,
    #[serde(default)]
    message: String,
    #[serde(default)]
    kind: String,
}

/// ほかの島の掲示板への書き込み (公開・極秘はログインしている島が払う。匿名はログイン不要)
pub async fn visitor_lbbs_post(
    State(app): State<Arc<AppState>>,
    headers: HeaderMap,
    Path(id): Path<i64>,
    peer: Option<axum::Extension<axum::extract::ConnectInfo<std::net::SocketAddr>>>,
    Form(form): Form<VisitorLbbsForm>,
) -> Response {
    let login = login_of(&app, &headers).await;
    if !app.config.lbbs.enabled {
        return error_page(
            &app,
            login.as_ref(),
            StatusCode::NOT_FOUND,
            "掲示板は使えません。",
        )
        .await;
    }
    let speaker = match (form.kind.as_str(), &login) {
        ("anonymous", _) if app.config.lbbs.allow_anonymous => VisitorSpeaker::Anonymous,
        ("public", Some(l)) if csrf_ok(l, &form.csrf) => {
            VisitorSpeaker::Public(l.session.island_id)
        }
        ("secret", Some(l)) if csrf_ok(l, &form.csrf) => {
            VisitorSpeaker::Secret(l.session.island_id)
        }
        _ => {
            return error_page(
                &app,
                login.as_ref(),
                StatusCode::FORBIDDEN,
                "書き込めません。ログインし直してください。",
            )
            .await;
        }
    };
    let addr = super::remote_addr(&app, &headers, peer.map(|p| (p.0).0));
    let req = actions::Request {
        now: crate::now_unix(),
        remote_addr: &addr,
    };
    let config = &app.config;
    let result = edit(&app, |game, _| {
        visitor_post(game, config, req, id, speaker, &form.name, &form.message)
    })
    .await;
    let back = format!("/island/{id}");
    match (result, &login) {
        (Ok(()), Some(l)) => redirect_with_flash(&app, l, &back, "記帳を行いました"),
        (Ok(()), None) => Redirect::to(&back).into_response(),
        (Err(EditError::Action(e @ ActionError::NoSuchIsland)), _) => {
            error_page(&app, login.as_ref(), StatusCode::NOT_FOUND, &e.to_string()).await
        }
        (Err(EditError::Action(e)), Some(l)) => redirect_with_flash(&app, l, &back, e.to_string()),
        (Err(e), _) => {
            error_page(
                &app,
                login.as_ref(),
                StatusCode::BAD_REQUEST,
                &e.to_string(),
            )
            .await
        }
    }
}
