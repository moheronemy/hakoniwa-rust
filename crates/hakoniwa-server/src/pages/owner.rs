//! 開発画面 (Perl 版の `ownerMain` / `tempOwner`) と、そこからの操作。

use axum::Form;
use std::fmt::Write;

use axum::extract::Query;
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Response};
use hakoniwa_core::actions::{self, ActionError};
use hakoniwa_core::view;
use serde::Deserialize;

use super::auth::require_login;
use super::{csrf_ok, error_page, login_of, redirect_with_flash, render};
use crate::AppState;
use crate::edit::{EditError, edit};
use crate::layout::{csrf_field, esc};
use crate::sets::Set;

/// 開発画面の URL に付ける、前回の計画の入力 (選択の初期値)
#[derive(Deserialize, Default)]
pub struct OwnerQuery {
    #[serde(default)]
    kind: String,
    #[serde(default)]
    x: String,
    #[serde(default)]
    y: String,
    #[serde(default)]
    n: Option<usize>,
    #[serde(default)]
    lamount1: String,
    /// `table` なら大きな地図も表で出す
    #[serde(default)]
    map: String,
}

fn options(choices: &[view::owner::Choice], selected_value: Option<i64>) -> String {
    let mut h = String::new();
    for c in choices {
        let sel = match selected_value {
            Some(v) => c.value == v,
            None => c.selected,
        };
        let _ = write!(
            h,
            "<option value=\"{}\"{}>{}</option>",
            c.value,
            if sel { " selected" } else { "" },
            esc(&c.label)
        );
    }
    h
}

/// 計画の入力欄 (Perl 版の `tempOwner` の計画のフォーム)
fn command_form(screen: &view::owner::OwnerScreen, csrf: &str, number: Option<usize>) -> String {
    let menu = &screen.menu;
    let mut kinds = String::new();
    for c in &menu.commands {
        let _ = write!(
            kinds,
            "<option value=\"{}\"{}>{}</option>",
            c.kind,
            if c.selected { " selected" } else { "" },
            esc(&c.label())
        );
    }
    let ijiri = match &menu.ijiri {
        Some(ij) => format!(
            "<label for=\"lamount1\">いじり (管理者)</label><select id=\"lamount1\" name=\"lamount1\">{}</select>\
             <input type=\"text\" name=\"lamount2\" size=\"10\" aria-label=\"いじりの値\">",
            options(&ij.lamount1, None)
        ),
        None => String::new(),
    };
    format!(
        "<form method=\"post\" action=\"/owner/command\" class=\"card command-form\" id=\"command-form\">{csrf}\n\
         <label for=\"number\">計画番号</label><select id=\"number\" name=\"number\">{numbers}</select>\n\
         <label for=\"kind\">計画 <span class=\"muted\" title=\"{costtitle}\">(コスト修正 {costtotal})</span></label>\
         <select id=\"kind\" name=\"kind\">{kinds}</select>\n\
         <label>座標 (地図をクリックしても選べます)</label>(<select name=\"x\" id=\"px\" aria-label=\"x\">{xs}</select>, \
         <select name=\"y\" id=\"py\" aria-label=\"y\">{ys}</select>)\n\
         <label for=\"amount\">数量</label><select id=\"amount\" name=\"amount\">{amounts}</select>\n\
         <label for=\"target\">目標の島</label><select id=\"target\" name=\"target\">{targets}</select>\n{ijiri}\n\
         <p class=\"buttons\"><button name=\"mode\" value=\"insert\">挿入</button> \
         <button name=\"mode\" value=\"write\" class=\"secondary\">上書き</button> \
         <button name=\"mode\" value=\"delete\" class=\"secondary\">削除</button></p>\n</form>\n",
        csrf = csrf_field(csrf),
        numbers = options(&menu.plan_numbers, number.map(|n| n as i64)),
        costtitle = esc(&menu.cost_modifier.details.join("\n")),
        costtotal = esc(&menu.cost_modifier.total),
        xs = options(&menu.xs, None),
        ys = options(&menu.ys, None),
        amounts = options(&menu.amounts, None),
        targets = options(&menu.targets, None),
    )
}

/// 計画の一覧。番号を押すと入力欄の計画番号に入る
fn plan_list(screen: &view::owner::OwnerScreen) -> String {
    let mut h = String::from("<ol class=\"plans\">\n");
    for p in &screen.plans {
        let _ = writeln!(
            h,
            "<li><button type=\"button\" class=\"plan-no\" data-n=\"{}\">{:02}</button> {}</li>",
            p.number - 1,
            p.number,
            // 島の名前は保存の時点でエスケープ済みのものが入る (view::owner のとおり)
            p.text
        );
    }
    h.push_str("</ol>\n");
    h
}

fn policy_form(screen: &view::owner::OwnerScreen, csrf: &str) -> String {
    let Some(lines) = &screen.policies else {
        return String::new();
    };
    let mut h = String::from("<h2>政策</h2>\n<ul>\n");
    for l in lines {
        let _ = writeln!(h, "<li>{}</li>", esc(&crate::render::plain(&l.text)));
    }
    let _ = write!(
        h,
        "</ul>\n<form method=\"post\" action=\"/owner/policy\" class=\"card\">{}\n\
         <label for=\"policy\">政策</label><select id=\"policy\" name=\"policy\">\
         <option value=\"shouene\">省エネ</option><option value=\"bousai\">防災</option>\
         <option value=\"kankou\">観光</option><option value=\"sizen\">自然</option>\
         <option value=\"kyouiku\">教育</option><option value=\"chochiku\">貯蓄</option></select>\n\
         <label for=\"policy-amount\">予算 (0〜50)</label><input id=\"policy-amount\" type=\"number\" name=\"amount\" min=\"0\" max=\"50\" value=\"0\">\n\
         <p><button>予算を変える</button></p>\n</form>\n",
        csrf_field(csrf)
    );
    h
}

/// 地図のマスと計画番号を押したときに、入力欄に入れる
const OWNER_SCRIPT: &str = r#"<script>
document.querySelectorAll('.map .cell[data-x]').forEach(function (c) {
  function pick() {
    document.getElementById('px').value = c.dataset.x;
    document.getElementById('py').value = c.dataset.y;
    document.querySelectorAll('.map .picked').forEach(function (p) { p.classList.remove('picked'); });
    c.classList.add('picked');
  }
  c.addEventListener('click', pick);
  c.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } });
});
document.querySelectorAll('.plan-no').forEach(function (b) {
  b.addEventListener('click', function () { document.getElementById('number').value = b.dataset.n; });
});
</script>"#;

pub async fn owner_page(
    Set(app): Set,
    headers: HeaderMap,
    Query(q): Query<OwnerQuery>,
) -> Response {
    let Some(login) = login_of(&app, &headers).await else {
        return require_login(&app).await;
    };
    let body = {
        let game = app.game.read().await;
        let Some(idx) = actions::island_index(&game.world, login.session.island_id) else {
            return require_login(&app).await;
        };
        let island = &game.world.islands[idx];
        let master = login.session.master;
        let iv = view::island_view(
            &game.world,
            &app.config,
            idx,
            view::Viewer::Owner { master },
        );
        let defaults = view::owner::MenuDefaults {
            kind: q.kind.clone(),
            x: q.x.clone(),
            y: q.y.clone(),
            lamount1: q.lamount1.clone(),
            ..Default::default()
        };
        let screen = view::owner::owner_screen(&app.config, &game, idx, master, &defaults);
        let csrf = &login.session.csrf;
        format!(
            "<h1>{name}島開発計画</h1>\n\
             <div class=\"owner-grid\"><div>{map}{form}</div><div><h2>計画</h2>{plans}</div></div>\n\
             <h2>島の情報</h2>{info}{policy}\n\
             <h2>コメント</h2>\n<form method=\"post\" action=\"/owner/comment\" class=\"card\">{csrf_f}\n\
             <label for=\"message\">島のコメント</label>\n\
             <input id=\"message\" type=\"text\" name=\"message\" value=\"{comment}\" maxlength=\"80\" size=\"60\">\n\
             <p><button>コメントを変える</button></p>\n</form>\n{extras}{lbbs}{recent}{change}{script}",
            extras = super::extras::owner_sections(&screen, island, csrf),
            recent = crate::render::recent_html(
                &island.name,
                &view::recent_logs(&game, &app.config, island.id, true)
            ),
            name = esc(&island.name),
            map = crate::render::map_html(
                &iv,
                app.options.image_dir.is_some(),
                true,
                q.map == "table"
            ),
            form = command_form(&screen, csrf, q.n),
            plans = plan_list(&screen),
            info = crate::render::info_html(&iv.info),
            policy = policy_form(&screen, csrf),
            csrf_f = csrf_field(csrf),
            // コメントは保存の時点でエスケープ済み (Perl 版と同じ)。入力欄に戻すときは元の文字に戻す
            comment = esc(&unescape(&island.comment)),
            lbbs = if app.config.lbbs.enabled {
                owner_lbbs(&app.config, island, csrf)
            } else {
                String::new()
            },
            change = super::register::change_forms(&app, csrf),
            script = OWNER_SCRIPT,
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

pub async fn comment(Set(app): Set, headers: HeaderMap, Form(form): Form<CommentForm>) -> Response {
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
    Set(app): Set,
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
    let back = format!(
        "/owner?kind={}&x={}&y={}&n={}&lamount1={}",
        enc(&form.kind),
        enc(&form.x),
        enc(&form.y),
        (form.number + 1).min(app.config.command_max.saturating_sub(1)),
        enc(&form.lamount1)
    );
    match result {
        Ok(_) => redirect_with_flash(&app, &login, &back, message),
        Err(e) => finish(&app, &login, Err(e), message).await,
    }
}

/// URL のクエリに入れる値 (数字と符号だけを通す)
fn enc(s: &str) -> String {
    s.chars()
        .filter(|c| c.is_ascii_digit() || *c == '-')
        .take(8)
        .collect()
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
pub async fn policy(Set(app): Set, headers: HeaderMap, Form(form): Form<PolicyForm>) -> Response {
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
pub async fn lbbs(Set(app): Set, headers: HeaderMap, Form(form): Form<LbbsForm>) -> Response {
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
