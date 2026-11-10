//! フェーズ 6 の付加機能の画面: ハコオクの入札、各種予想 (toto・Numbers)、首都名、
//! 援助射撃の許可、アンケートの投票。ルールは `hakoniwa_core::actions` の
//! `auction`, `toto`, `dispatch`, `survey`、表示する中身は `view::owner` / `view::top`。

use std::fmt::Write;

use axum::Form;
use axum::http::{HeaderMap, StatusCode};
use axum::response::Response;
use hakoniwa_core::actions;
use hakoniwa_core::model::Island;
use hakoniwa_core::view::owner::{Choice, OwnerScreen};
use serde::Deserialize;

use super::auth::require_login;
use super::owner::finish;
use super::{csrf_ok, error_page, login_of, redirect_with_flash};
use crate::edit::edit;
use crate::layout::{csrf_field, esc};
use crate::render::plain;
use crate::sets::Set;

fn options(choices: &[Choice]) -> String {
    choices
        .iter()
        .map(|c| {
            format!(
                "<option value=\"{}\"{}>{}</option>",
                c.value,
                if c.selected { " selected" } else { "" },
                esc(&c.label)
            )
        })
        .collect()
}

/// 開発画面に出す付加機能の欄
pub fn owner_sections(screen: &OwnerScreen, island: &Island, csrf: &str) -> String {
    let csrf = csrf_field(csrf);
    let mut h = String::new();

    // ハコオク
    let a = &screen.auction;
    if !a.lots.is_empty() {
        h.push_str("<h2>ハコオク</h2>\n<ul>\n");
        for lot in &a.lots {
            let _ = writeln!(h, "<li>{}</li>", esc(&plain(&lot.text())));
        }
        h.push_str("</ul>\n");
        if a.can_list {
            h.push_str("<p class=\"muted\">出品できます (計画の「オークション出品」から)。</p>\n");
        }
        if a.can_bid {
            let _ = write!(
                h,
                "<form method=\"post\" action=\"/owner/extra\" class=\"card\">{csrf}<input type=\"hidden\" name=\"action\" value=\"bid\">\n\
                 <label for=\"lot\">品番</label><select id=\"lot\" name=\"lot\">{}</select>\n\
                 <label for=\"bid\">入札額 (最低額に上乗せ)</label><select id=\"bid\" name=\"amount\">{}</select>\n\
                 <p><button>入札する</button></p>\n</form>\n",
                options(&a.lot_numbers),
                options(&a.amounts)
            );
        } else {
            h.push_str("<p class=\"muted\">(入札不可)</p>\n");
        }
    }

    let c = &screen.comment;
    // 各種予想
    if c.prediction {
        let _ = write!(
            h,
            "<h2>各種予想</h2>\n<form method=\"post\" action=\"/owner/extra\" class=\"card\">{csrf}<input type=\"hidden\" name=\"action\" value=\"predict\">\n\
             <p class=\"muted\">いまの予想: {current}<br>書き方: <code>(toto@1.2.3.4.5.6.7.8)</code> <code>(hc@勝.負)</code> <code>(n3@123)</code> <code>(n4@1234)</code> (並べて書けます)</p>\n\
             <label for=\"predict\">予想</label><input id=\"predict\" type=\"text\" name=\"message\" maxlength=\"44\" size=\"44\">\n\
             <p><button>予想する</button></p>\n</form>\n",
            // eis8 は保存の時点でエスケープ済み
            current = if island.eis8.is_empty() {
                "(なし)".to_string()
            } else {
                island.eis8.clone()
            },
        );
    }
    // 首都名
    if c.capital_name {
        let _ = write!(
            h,
            "<h2>首都名</h2>\n<form method=\"post\" action=\"/owner/extra\" class=\"card\">{csrf}<input type=\"hidden\" name=\"action\" value=\"capital\">\n\
             <label for=\"capital\">首都の名前</label><input id=\"capital\" type=\"text\" name=\"message\" maxlength=\"32\">\n\
             <p><button>首都名を決める</button></p>\n</form>\n"
        );
    }
    // 援助射撃
    let _ = write!(
        h,
        "<h2>援助射撃</h2>\n{notice}<form method=\"post\" action=\"/owner/extra\" class=\"card\">{csrf}\n\
         <label for=\"ms-target\">相手の島</label><select id=\"ms-target\" name=\"target\">{targets}</select>\n\
         <label for=\"ms-turns\">有効ターン数</label><select id=\"ms-turns\" name=\"amount\">{turns}</select>\n\
         <p><button name=\"action\" value=\"ms-request\">許可を申請する</button> \
         <button name=\"action\" value=\"ms-grant\" class=\"secondary\">申請を許可する</button></p>\n</form>\n",
        notice = c
            .missile_request_notice()
            .map(|n| format!("<p class=\"flash\">{}</p>\n", esc(&plain(&n))))
            .unwrap_or_default(),
        targets = options(&c.targets),
        turns = options(&c.turns),
    );
    h
}

#[derive(Deserialize)]
pub struct ExtraForm {
    #[serde(default)]
    csrf: String,
    #[serde(default)]
    action: String,
    #[serde(default)]
    lot: String,
    #[serde(default)]
    amount: String,
    #[serde(default)]
    message: String,
    #[serde(default)]
    target: String,
}

pub async fn extra(Set(app): Set, headers: HeaderMap, Form(form): Form<ExtraForm>) -> Response {
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
    match form.action.as_str() {
        "bid" => {
            let r = edit(&app, |g, rng| {
                actions::auction::bid(g, config, rng, id, &form.lot, &form.amount)
            })
            .await;
            finish(&app, &login, r, "入札しました").await
        }
        "predict" => {
            let r = edit(&app, |g, _| {
                actions::toto::set_prediction(g, id, &form.message)
            })
            .await;
            finish(&app, &login, r, "予想しました").await
        }
        "capital" => {
            let r = edit(&app, |g, _| {
                actions::toto::set_capital_name(g, id, &form.message)
            })
            .await;
            finish(&app, &login, r, "首都名を変更しました").await
        }
        "ms-request" => {
            let r = edit(&app, |g, _| {
                actions::dispatch::request_permission(g, id, &form.target, &form.amount)
            })
            .await;
            finish(&app, &login, r, "許可を申請しました").await
        }
        "ms-grant" => {
            let r = edit(&app, |g, _| {
                actions::dispatch::grant_permission(g, id, &form.target, &form.amount)
            })
            .await;
            match r {
                Ok(true) => redirect_with_flash(&app, &login, "/owner", "援助射撃を許可しました"),
                Ok(false) => {
                    redirect_with_flash(&app, &login, "/owner", "その島からの申請はありません")
                }
                Err(e) => finish(&app, &login, Err(e), "").await,
            }
        }
        _ => {
            error_page(
                &app,
                Some(&login),
                StatusCode::BAD_REQUEST,
                "操作が違います。",
            )
            .await
        }
    }
}

#[derive(Deserialize)]
pub struct VoteForm {
    #[serde(default)]
    csrf: String,
    #[serde(default)]
    choice: String,
}

/// アンケートの投票 (ログインしている島で 1 票)
pub async fn vote(Set(app): Set, headers: HeaderMap, Form(form): Form<VoteForm>) -> Response {
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
    if !app.config.survey.enabled {
        return error_page(
            &app,
            Some(&login),
            StatusCode::NOT_FOUND,
            "アンケートはありません。",
        )
        .await;
    }
    let id = login.session.island_id;
    match edit(&app, |g, _| actions::survey::vote(g, id, &form.choice)).await {
        Ok(()) => redirect_with_flash(&app, &login, "/", "清き１票ありがとうございました。"),
        Err(crate::edit::EditError::Action(e)) => {
            redirect_with_flash(&app, &login, "/", e.to_string())
        }
        Err(e) => {
            error_page(
                &app,
                Some(&login),
                StatusCode::INTERNAL_SERVER_ERROR,
                &e.to_string(),
            )
            .await
        }
    }
}
