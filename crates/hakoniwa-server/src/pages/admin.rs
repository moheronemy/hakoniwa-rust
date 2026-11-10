//! 管理画面 (Perl 版の `hako-mente.cgi`)。
//!
//! マスターパスワード (`passwords.master`) を設定したときだけ使える。できること:
//! いまのデータとバックアップの状態を見る、最終更新時刻を変える、バックアップを現役に戻す、
//! バックアップを消す、ゲームを最初からやり直す。
//! Perl 版はデータのディレクトリごと消したり複製したりしていた。移植版はデータディレクトリの
//! 今の状態とバックアップ (`backup<N>/`、[`hakoniwa_core::persist`]) を扱う。

use std::fmt::Write;
use std::sync::Arc;

use axum::Form;
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Redirect, Response};
use hakoniwa_core::model::GameState;
use hakoniwa_core::persist;
use serde::Deserialize;

use super::{
    Login, csrf_ok, error_page, login_of, redirect_with_cookie, redirect_with_flash, render,
};
use crate::layout::{csrf_field, esc};
use crate::session::{self, ADMIN_ISLAND};
use crate::sets::Set;
use crate::{AppState, now_unix};

/// UTC の日時 (`YYYY-MM-DD hh:mm:ss`)
pub fn utc(t: i64) -> String {
    let days = t.div_euclid(86400);
    let secs = t.rem_euclid(86400);
    // 1970-01-01 からの日数を年月日に (Howard Hinnant の civil_from_days)
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if m <= 2 { y + 1 } else { y };
    format!(
        "{y:04}-{m:02}-{d:02} {:02}:{:02}:{:02} UTC",
        secs / 3600,
        secs % 3600 / 60,
        secs % 60
    )
}

fn is_admin(login: &Option<Login>) -> bool {
    login
        .as_ref()
        .is_some_and(|l| l.session.master && l.session.island_id == ADMIN_ISLAND)
}

fn login_form(error: Option<&str>) -> String {
    format!(
        "<h1>管理画面</h1>\n{}<form method=\"post\" action=\"/admin/login\" class=\"card\">\n\
         <label for=\"password\">マスターパスワード</label>\
         <input id=\"password\" type=\"password\" name=\"password\" maxlength=\"64\" autocomplete=\"current-password\" required>\n\
         <p><button>入る</button></p>\n</form>\n",
        error
            .map(|e| format!("<p class=\"error\">{}</p>\n", esc(e)))
            .unwrap_or_default()
    )
}

/// データ 1 つ分の概要
fn summary(title: &str, turn: i64, last_time: i64, islands: usize) -> String {
    format!(
        "<tr><th>{}</th><td class=\"num\">ターン{}</td><td>{}<br><small class=\"muted\">{} 秒</small></td><td class=\"num\">{} 島</td>",
        esc(title),
        turn,
        utc(last_time),
        last_time,
        islands
    )
}

pub async fn admin_page(Set(app): Set, headers: HeaderMap) -> Response {
    if app.config.passwords.master.is_none() {
        return StatusCode::NOT_FOUND.into_response();
    }
    let login = login_of(&app, &headers).await;
    if !is_admin(&login) {
        return render(&app, login.as_ref(), "管理画面", &login_form(None))
            .await
            .into_response();
    }
    let login = login.expect("admin");
    let csrf = csrf_field(&login.session.csrf);
    let mut h = String::from(
        "<h1>管理画面</h1>\n<div class=\"table-scroll\"><table>\n<tr><th></th><th class=\"num\">ターン</th><th>最終更新時刻</th><th class=\"num\">島</th><th></th></tr>\n",
    );
    {
        let game = app.game.read().await;
        h.push_str(&summary(
            "現役データ",
            game.world.turn,
            game.world.last_time,
            game.world.islands.len(),
        ));
        h.push_str("<td></td></tr>\n");
    }
    for n in 0..app.config.backup_keep {
        // 見出しだけを読む (状態は展開しない)
        match persist::read_backup_header(&persist::backup_dir(&app.data_dir, n)) {
            Ok(Some(head)) => {
                h.push_str(&summary(
                    &format!("バックアップ{n}"),
                    head.turn,
                    head.last_time,
                    head.islands,
                ));
                let _ = writeln!(
                    h,
                    "<td><form class=\"inline\" method=\"post\" action=\"/admin/restore\">{csrf}<input type=\"hidden\" name=\"n\" value=\"{n}\"><button class=\"secondary\">このデータを現役に</button></form> \
                     <form class=\"inline\" method=\"post\" action=\"/admin/delete-backup\">{csrf}<input type=\"hidden\" name=\"n\" value=\"{n}\"><button class=\"secondary\">削除</button></form></td></tr>"
                );
            }
            Ok(None) => {}
            Err(e) => {
                let _ = writeln!(
                    h,
                    "<tr><th>バックアップ{n}</th><td colspan=\"4\" class=\"error\">{}</td></tr>",
                    esc(&e.to_string())
                );
            }
        }
    }
    h.push_str("</table></div>\n");
    h.push_str(&ip_ranking(&app).await);
    let last = app.game.read().await.world.last_time;
    let _ = write!(
        h,
        "<h2>最終更新時刻の変更</h2>\n<form method=\"post\" action=\"/admin/time\" class=\"card\">{csrf}\n\
         <label for=\"last\">1970年1月1日 (UTC) からの秒数</label><input id=\"last\" type=\"number\" name=\"last_time\" value=\"{last}\">\n\
         <p><button>変更</button></p>\n</form>\n\
         <h2>最初からやり直す</h2>\n<form method=\"post\" action=\"/admin/reset\" class=\"card\">{csrf}\n\
         <p class=\"error\">いまのデータを消して、島の無い新しいゲームにします (消す前のデータはバックアップに残ります)。</p>\n\
         <label for=\"confirm\">よければ「削除する」と入力</label><input id=\"confirm\" type=\"text\" name=\"confirm\" required>\n\
         <p><button>新しいゲームを始める</button></p>\n</form>\n\
         <form method=\"post\" action=\"/logout\">{csrf}<button class=\"secondary\">管理画面から出る</button></form>\n"
    );
    render(&app, Some(&login), "管理画面", &h)
        .await
        .into_response()
}

/// 裏ランキング (Perl 版の `hako-top2.cgi`): 接続元が同じ島を数える (多重登録の確認用)
async fn ip_ranking(app: &AppState) -> String {
    let master = app.config.passwords.master.clone().unwrap_or_default();
    let game = app.game.read().await;
    let Ok(rows) = hakoniwa_core::view::ipinfo::ip_ranking(&game, &app.config, &master) else {
        return String::new();
    };
    let mut h = String::from(
        "<h2>裏ランキング (接続元の重なり)</h2>\n<div class=\"table-scroll\"><table>\n\
         <tr><th class=\"num\">順位</th><th>島</th><th class=\"num\">重なり</th><th>重なった島</th>\
         <th>接続元 (新しい順、最後は登録時)</th><th class=\"num\">変更</th></tr>\n",
    );
    for r in rows {
        let matches: Vec<String> = r
            .matches
            .iter()
            .map(|m| format!("{}島(ID:{})", esc(&m.name), m.id))
            .collect();
        let ips: Vec<String> = r.ips.iter().rev().map(|ip| esc(ip)).collect();
        let _ = writeln!(
            h,
            "<tr><td class=\"num\">{}</td><td>{}島 <small class=\"muted\">ID:{}</small></td><td class=\"num\">{}</td><td>{}</td><td><small>{}</small></td><td class=\"num\">{} / {}</td></tr>",
            r.rank,
            esc(&r.name),
            r.id,
            r.found,
            matches.join("、"),
            ips.join(" / "),
            r.changes_this_century,
            r.changes_total
        );
    }
    h.push_str("</table></div>\n");
    h
}

#[derive(Deserialize)]
pub struct AdminLogin {
    password: String,
}

pub async fn admin_login(Set(app): Set, Form(form): Form<AdminLogin>) -> Response {
    let Some(master) = &app.config.passwords.master else {
        return StatusCode::NOT_FOUND.into_response();
    };
    if form.password.is_empty() || !session::same(master, &form.password) {
        return (
            StatusCode::UNAUTHORIZED,
            render(
                &app,
                None,
                "管理画面",
                &login_form(Some("パスワードが違います。")),
            )
            .await,
        )
            .into_response();
    }
    let token = app.sessions.create(ADMIN_ISLAND, true, now_unix());
    redirect_with_cookie(
        "/admin",
        session::set_cookie(&token, app.options.secure_cookie),
    )
}

#[derive(Deserialize)]
pub struct AdminForm {
    #[serde(default)]
    csrf: String,
    n: Option<usize>,
    last_time: Option<i64>,
    #[serde(default)]
    confirm: String,
}

async fn guard(app: &AppState, headers: &HeaderMap, csrf: &str) -> Result<Login, Response> {
    let login = login_of(app, headers).await;
    if app.config.passwords.master.is_none() || !is_admin(&login) {
        return Err(StatusCode::NOT_FOUND.into_response());
    }
    let login = login.expect("admin");
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

/// いまのデータを `make` が作るデータに差し替えて保存する (差し替える前のデータはバックアップに回す)。
/// `make` は書き込みの順番を持ってから呼ぶ (バックアップを読むあいだにターン処理がずらさないように)
async fn replace(
    app: &AppState,
    make: impl FnOnce() -> anyhow::Result<GameState>,
) -> anyhow::Result<()> {
    let mut writer = app.game.write().await;
    let next = Arc::new(make()?);
    let (current, saved, keep) = (writer.current(), next.clone(), app.config.backup_keep);
    writer
        .with_data(move |data| {
            data.backup(&current, keep)?;
            data.snapshot(&saved)?;
            Ok(())
        })
        .await?;
    writer.publish(next);
    Ok(())
}

async fn done(
    app: &AppState,
    login: &Login,
    result: anyhow::Result<()>,
    message: &str,
) -> Response {
    match result {
        Ok(()) => redirect_with_flash(app, login, "/admin", message),
        Err(e) => {
            tracing::error!("管理画面の操作に失敗しました: {e:#}");
            error_page(
                app,
                Some(login),
                StatusCode::INTERNAL_SERVER_ERROR,
                &format!("失敗しました: {e:#}"),
            )
            .await
        }
    }
}

pub async fn set_time(Set(app): Set, headers: HeaderMap, Form(form): Form<AdminForm>) -> Response {
    let login = match guard(&app, &headers, &form.csrf).await {
        Ok(l) => l,
        Err(r) => return r,
    };
    let Some(t) = form.last_time else {
        return Redirect::to("/admin").into_response();
    };
    let result = crate::edit::edit(&app, |game, _| {
        game.world.last_time = t;
        Ok(())
    })
    .await
    .map_err(|e| anyhow::anyhow!("{e}"));
    done(&app, &login, result, "最終更新時刻を変更しました").await
}

pub async fn restore(Set(app): Set, headers: HeaderMap, Form(form): Form<AdminForm>) -> Response {
    let login = match guard(&app, &headers, &form.csrf).await {
        Ok(l) => l,
        Err(r) => return r,
    };
    let Some(n) = form.n.filter(|&n| n < app.config.backup_keep) else {
        return Redirect::to("/admin").into_response();
    };
    let dir = persist::backup_dir(&app.data_dir, n);
    // 戻す前にバックアップの番号がずれるので、読み込んでから差し替える
    let result = replace(&app, || {
        if !dir.exists() {
            anyhow::bail!("バックアップ{n}がありません");
        }
        Ok(persist::read_backup(&dir)?)
    })
    .await;
    done(
        &app,
        &login,
        result,
        &format!("バックアップ{n}を現役にしました"),
    )
    .await
}

pub async fn delete_backup(
    Set(app): Set,
    headers: HeaderMap,
    Form(form): Form<AdminForm>,
) -> Response {
    let login = match guard(&app, &headers, &form.csrf).await {
        Ok(l) => l,
        Err(r) => return r,
    };
    let Some(n) = form.n.filter(|&n| n < app.config.backup_keep) else {
        return Redirect::to("/admin").into_response();
    };
    let dir = persist::backup_dir(&app.data_dir, n);
    // バックアップのログはハードリンクなので、消しても今のデータのログは残る
    let result = {
        let _writer = app.game.write().await;
        std::fs::remove_dir_all(&dir).map_err(anyhow::Error::from)
    };
    done(
        &app,
        &login,
        result,
        &format!("バックアップ{n}を削除しました"),
    )
    .await
}

pub async fn reset(Set(app): Set, headers: HeaderMap, Form(form): Form<AdminForm>) -> Response {
    let login = match guard(&app, &headers, &form.csrf).await {
        Ok(l) => l,
        Err(r) => return r,
    };
    if form.confirm != "削除する" {
        return redirect_with_flash(&app, &login, "/admin", "「削除する」と入力してください");
    }
    let result = replace(&app, || Ok(GameState::new_game(now_unix(), &app.config))).await;
    // 島が無くなるので、島のセッションはすべて無効になる (login_of が確かめる)
    done(&app, &login, result, "新しいゲームを始めました").await
}

#[cfg(test)]
mod tests {
    use super::utc;

    #[test]
    fn utc_dates() {
        assert_eq!(utc(0), "1970-01-01 00:00:00 UTC");
        assert_eq!(utc(1_794_290_400), "2026-11-10 06:00:00 UTC");
        assert_eq!(utc(951_782_400), "2000-02-29 00:00:00 UTC");
    }
}
