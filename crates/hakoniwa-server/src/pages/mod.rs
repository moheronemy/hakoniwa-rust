//! 画面ごとの処理 (ルーティングの先)。

pub mod admin;
pub mod auth;
pub mod extras;
pub mod history;
pub mod images;
pub mod island;
pub mod owner;
pub mod register;
pub mod top;

use std::net::SocketAddr;
use std::sync::Arc;

use axum::http::HeaderMap;
use axum::http::header::SET_COOKIE;
use axum::response::{Html, IntoResponse, Redirect, Response};

use crate::layout::{self, Viewer};
use crate::session::{self, Session};
use crate::{AppState, now_unix};

/// ログイン中ならそのセッション (トークンと中身)
pub struct Login {
    pub token: String,
    pub session: Session,
}

/// リクエストのクッキーからログイン中のセッションを探す。島が無くなっていたら無効
pub async fn login_of(app: &AppState, headers: &HeaderMap) -> Option<Login> {
    let token = session::token_from(headers)?;
    let session = app.sessions.get(&token, now_unix())?;
    if session.island_id == session::ADMIN_ISLAND && session.master {
        return Some(Login { token, session });
    }
    let game = app.game.read().await;
    if !game.world.islands.iter().any(|i| i.id == session.island_id) {
        app.sessions.remove(&token);
        return None;
    }
    Some(Login { token, session })
}

/// 共通の外枠で画面を返す。ログイン中なら知らせ (flash) も取り出して出す
pub async fn render(
    app: &AppState,
    login: Option<&Login>,
    title: &str,
    body: &str,
) -> Html<String> {
    let game = app.game.read().await;
    let name = login.and_then(|l| {
        game.world
            .islands
            .iter()
            .find(|i| i.id == l.session.island_id)
            .map(|i| i.name.clone())
    });
    drop(game);
    let flash = login.and_then(|l| app.sessions.take_flash(&l.token));
    let viewer = match (login, &name) {
        (Some(l), Some(n)) => Some(Viewer {
            island_name: n,
            csrf: &l.session.csrf,
        }),
        _ => None,
    };
    Html(layout::page(
        &app.config.title,
        title,
        viewer.as_ref(),
        flash.as_deref(),
        body,
    ))
}

/// POST のフォームの CSRF 対策のトークンを確かめる
pub fn csrf_ok(login: &Login, token: &str) -> bool {
    session::same(&login.session.csrf, token)
}

/// エラーの画面 (ステータス 400 など)
pub async fn error_page(
    app: &AppState,
    login: Option<&Login>,
    status: axum::http::StatusCode,
    message: &str,
) -> Response {
    let body = format!(
        "<p class=\"error\">{}</p>\n<p><a href=\"/\">トップへ戻る</a></p>",
        layout::esc(message)
    );
    (status, render(app, login, "エラー", &body).await).into_response()
}

/// 操作のあと、知らせを付けて別の画面へ移る
pub fn redirect_with_flash(
    app: &AppState,
    login: &Login,
    to: &str,
    message: impl Into<String>,
) -> Response {
    app.sessions.set_flash(&login.token, message);
    Redirect::to(to).into_response()
}

/// クッキーを付けて移る
pub fn redirect_with_cookie(to: &str, cookie: String) -> Response {
    ([(SET_COOKIE, cookie)], Redirect::to(to)).into_response()
}

/// 接続元のアドレス (Perl 版の `REMOTE_ADDR`)。`trust_forwarded` なら X-Forwarded-For の先頭を使う
pub fn remote_addr(app: &Arc<AppState>, headers: &HeaderMap, peer: Option<SocketAddr>) -> String {
    let forwarded = headers
        .get("x-forwarded-for")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.split(',').next())
        .map(str::trim)
        .filter(|v| app.options.trust_forwarded && !v.is_empty());
    if let Some(first) = forwarded {
        return first.to_string();
    }
    peer.map(|p| p.ip().to_string()).unwrap_or_default()
}

#[cfg(test)]
pub(crate) mod test_util {
    use std::sync::Arc;

    use axum::body::Body;
    use axum::http::{Request, header};
    use axum::response::Response;
    use hakoniwa_core::GameConfig;
    use hakoniwa_core::legacy::{self, ImportOptions};
    use http_body_util::BodyExt;
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    use tower::ServiceExt;

    use crate::{AppState, ServerOptions, app};

    /// Perl 版のデータ (3 島。島 N のパスワードは "passN") を読み込んだサーバー。
    ///
    /// 最終更新時刻はいまにする。島の登録は時刻が来ていれば先にターンを進めるので、
    /// データの時刻のままだと、テストを走らせる日によってターンが進んで結果が変わる
    pub fn legacy_app() -> (Arc<AppState>, tempfile::TempDir) {
        let dir = tempfile::tempdir().unwrap();
        let src = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../hakoniwa-core/tests/fixtures/legacy-turn3");
        let mut game = legacy::import_dir(
            &src,
            &ImportOptions::default(),
            &mut StdRng::seed_from_u64(0),
        )
        .unwrap()
        .state;
        game.world.last_time = crate::now_unix();
        let data_dir = dir.path().join("store");
        let data = hakoniwa_core::persist::DataDir::create(&data_dir, &game).unwrap();
        let state = Arc::new(AppState {
            config: GameConfig::default(),
            options: ServerOptions::default(),
            sessions: Default::default(),
            data_dir,
            game: crate::store::Store::new(game, StdRng::seed_from_u64(0), data),
        });
        (state, dir)
    }

    pub async fn send(state: &Arc<AppState>, req: Request<Body>) -> Response {
        app(state.clone()).oneshot(req).await.unwrap()
    }

    pub async fn body(res: Response) -> String {
        String::from_utf8(res.into_body().collect().await.unwrap().to_bytes().to_vec()).unwrap()
    }

    pub fn get(uri: &str, cookie: Option<&str>) -> Request<Body> {
        let mut b = Request::get(uri);
        if let Some(c) = cookie {
            b = b.header(header::COOKIE, c);
        }
        b.body(Body::empty()).unwrap()
    }

    pub fn post(uri: &str, cookie: Option<&str>, form: &[(&str, &str)]) -> Request<Body> {
        let body: String = form
            .iter()
            .map(|(k, v)| format!("{}={}", enc(k), enc(v)))
            .collect::<Vec<_>>()
            .join("&");
        let mut b =
            Request::post(uri).header(header::CONTENT_TYPE, "application/x-www-form-urlencoded");
        if let Some(c) = cookie {
            b = b.header(header::COOKIE, c);
        }
        b.body(Body::from(body)).unwrap()
    }

    fn enc(s: &str) -> String {
        s.bytes()
            .map(|b| match b {
                b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                    (b as char).to_string()
                }
                _ => format!("%{b:02X}"),
            })
            .collect()
    }

    /// ログインしてセッションのクッキーと CSRF 対策のトークンを返す
    pub async fn login(state: &Arc<AppState>, id: i64, password: &str) -> (String, String) {
        let res = send(
            state,
            post(
                "/login",
                None,
                &[("island", &id.to_string()), ("password", password)],
            ),
        )
        .await;
        assert_eq!(res.status(), 303, "login failed");
        let cookie = res.headers()[header::SET_COOKIE].to_str().unwrap();
        let cookie = cookie.split(';').next().unwrap().to_string();
        let token = cookie.split_once('=').unwrap().1;
        let csrf = state.sessions.get(token, crate::now_unix()).unwrap().csrf;
        (cookie, csrf)
    }
}

#[cfg(test)]
mod tests {
    use super::test_util::*;
    use hakoniwa_core::actions::password;

    #[tokio::test]
    async fn login_comment_logout() {
        let (state, _dir) = legacy_app();
        // パスワード違い
        let res = send(
            &state,
            post("/login", None, &[("island", "1"), ("password", "x")]),
        )
        .await;
        assert_eq!(res.status(), 401);
        assert!(body(res).await.contains("パスワードが違います"));

        let (cookie, csrf) = login(&state, 1, "pass1").await;
        // Perl 版の DES crypt は新しい形式に置き換わる
        {
            let game = state.game.read().await;
            let island = game.world.islands.iter().find(|i| i.id == 1).unwrap();
            assert!(!password::is_legacy(&island.password));
            assert!(password::verify(&island.password, "pass1"));
        }
        let page = body(send(&state, get("/owner", Some(&cookie))).await).await;
        assert!(page.contains("開発計画"), "{page}");
        // 計画の入力欄と計画の一覧
        assert!(
            page.contains("name=\"kind\"") && page.contains("資金繰り"),
            "{page}"
        );

        // CSRF 対策のトークンが無い POST は受け付けない
        let res = send(
            &state,
            post("/owner/comment", Some(&cookie), &[("message", "x")]),
        )
        .await;
        assert_eq!(res.status(), 403);

        let res = send(
            &state,
            post(
                "/owner/comment",
                Some(&cookie),
                &[("csrf", &csrf), ("message", "やあ<b>")],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        let page = body(send(&state, get("/owner", Some(&cookie))).await).await;
        assert!(page.contains("コメントを更新しました"));
        assert!(page.contains("value=\"やあ&lt;b&gt;\""), "{page}");
        // 保存もされている (データディレクトリを読み直すと、操作の差分が当たっている)
        let (_, saved) = hakoniwa_core::persist::DataDir::open(&state.data_dir)
            .unwrap()
            .unwrap();
        assert_eq!(
            saved
                .world
                .islands
                .iter()
                .find(|i| i.id == 1)
                .unwrap()
                .comment,
            "やあ&lt;b&gt;"
        );

        // 政策・計画・掲示板
        let res = send(
            &state,
            post(
                "/owner/policy",
                Some(&cookie),
                &[("csrf", &csrf), ("policy", "kankou"), ("amount", "60")],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        let res = send(
            &state,
            post(
                "/owner/command",
                Some(&cookie),
                &[
                    ("csrf", &csrf),
                    ("number", "0"),
                    ("mode", "insert"),
                    ("kind", "41"),
                    ("amount", "0"),
                    ("target", "1"),
                    ("x", "3"),
                    ("y", "4"),
                ],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        // いじりはマスターパスワードのときだけ
        let res = send(
            &state,
            post(
                "/owner/command",
                Some(&cookie),
                &[("csrf", &csrf), ("number", "0"), ("kind", "60")],
            ),
        )
        .await;
        assert_eq!(res.status(), 403);
        let res = send(
            &state,
            post(
                "/owner/lbbs",
                Some(&cookie),
                &[("csrf", &csrf), ("name", "島主"), ("message", "ようこそ")],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        {
            let game = state.game.read().await;
            let island = game.world.islands.iter().find(|i| i.id == 1).unwrap();
            assert_eq!(island.etc_raw[0].split(',').nth(5), Some("50"));
            assert_eq!(
                (
                    island.commands[0].kind,
                    island.commands[0].x,
                    island.commands[0].y
                ),
                (41, 3, 4)
            );
            assert!(island.lbbs[0].contains("ようこそ"));
        }
        // ほかの島 (2) の観光画面から公開で書き込む (島 1 が払う)
        let res = send(
            &state,
            post(
                "/island/2/lbbs",
                Some(&cookie),
                &[
                    ("csrf", &csrf),
                    ("name", "客"),
                    ("message", "こんにちは"),
                    ("kind", "public"),
                ],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        let page = body(send(&state, get("/island/2", None)).await).await;
        assert!(
            page.contains("こんにちは") && page.contains("Alpha島"),
            "{page}"
        );
        // 匿名は設定で許されていない
        let res = send(
            &state,
            post(
                "/island/2/lbbs",
                None,
                &[("name", "x"), ("message", "y"), ("kind", "anonymous")],
            ),
        )
        .await;
        assert_eq!(res.status(), 403);

        let res = send(&state, post("/logout", Some(&cookie), &[("csrf", &csrf)])).await;
        assert_eq!(res.status(), 303);
        assert_eq!(
            send(&state, get("/owner", Some(&cookie))).await.status(),
            401
        );
    }

    #[tokio::test]
    async fn register_and_change() {
        let (state, _dir) = legacy_app();
        // 確認用のパスワードが違う
        let res = send(
            &state,
            post(
                "/register",
                None,
                &[
                    ("name", "新"),
                    ("owner", "私"),
                    ("password", "a"),
                    ("password2", "b"),
                    ("message", "m"),
                ],
            ),
        )
        .await;
        assert_eq!(res.status(), 400);
        let b = body(res).await;
        assert!(b.contains("一致しません"), "{b}");
        // 同じ名前
        let res = send(
            &state,
            post(
                "/register",
                None,
                &[
                    ("name", "Alpha"),
                    ("owner", "私"),
                    ("password", "a"),
                    ("password2", "a"),
                    ("message", "m"),
                ],
            ),
        )
        .await;
        assert_eq!(res.status(), 400);

        let res = send(
            &state,
            post(
                "/register",
                None,
                &[
                    ("name", "新天地"),
                    ("owner", "私"),
                    ("password", "secret1"),
                    ("password2", "secret1"),
                    ("message", "よろしく"),
                ],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        let cookie = res.headers()[axum::http::header::SET_COOKIE]
            .to_str()
            .unwrap()
            .split(';')
            .next()
            .unwrap()
            .to_string();
        let page = body(send(&state, get("/owner", Some(&cookie))).await).await;
        assert!(page.contains("「新天地島」と命名します"), "{page}");
        let id = {
            let game = state.game.read().await;
            game.world
                .islands
                .iter()
                .find(|i| i.name == "新天地")
                .unwrap()
                .id
        };

        // 名前の変更は、いまのパスワードが要る
        let token = cookie.split_once('=').unwrap().1;
        let csrf = state.sessions.get(token, crate::now_unix()).unwrap().csrf;
        let res = send(
            &state,
            post(
                "/owner/change",
                Some(&cookie),
                &[("csrf", &csrf), ("old_password", "x"), ("name", "別天地")],
            ),
        )
        .await;
        assert_eq!(res.status(), 403);
        let res = send(
            &state,
            post(
                "/owner/change",
                Some(&cookie),
                &[
                    ("csrf", &csrf),
                    ("old_password", "secret1"),
                    ("name", "別天地"),
                ],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        let game = state.game.read().await;
        assert_eq!(
            game.world.islands.iter().find(|i| i.id == id).unwrap().name,
            "別天地"
        );
    }

    /// 最近の出来事はターンごとに決まった行数ずつページを送り、トップページは行数を打ち切って続きへ案内する
    #[tokio::test]
    async fn history_pages_through_the_logs() {
        let (mut state, _dir) = legacy_app();
        {
            let app = std::sync::Arc::get_mut(&mut state).unwrap();
            app.options.history_page_lines = 2;
            app.options.top_log_lines = 1;
        }
        // 最新のターンのログを、行の多いもの (3 行に 1 行は機密) にする
        {
            let mut w = state.game.write().await;
            let mut next = (*w.current()).clone();
            let entries = (0..7)
                .map(|i| hakoniwa_core::model::LogEntry {
                    secret: i % 3 == 2,
                    turn: next.world.turn,
                    island1: Some(1),
                    island2: None,
                    message: format!("<B>出来事{i}</B>"),
                })
                .collect();
            next.logs.turns[0] =
                std::sync::Arc::new(hakoniwa_core::turn_log::TurnLog::new(entries));
            w.publish(std::sync::Arc::new(next));
        }
        let game = state.game.snapshot();
        let want: Vec<String> = game.logs.turns[0]
            .entries()
            .into_iter()
            .filter(|e| !e.secret)
            .map(|e| crate::render::plain(&e.message))
            .collect();
        assert!(want.len() > 2, "{want:?}");

        // ページを送って、最新のターンの機密でない行をすべて読む
        let mut got = Vec::new();
        let mut uri = "/history".to_string();
        loop {
            let page = body(send(&state, get(&uri, None)).await).await;
            for line in page.split("<p>ターン").skip(1) {
                let text = line
                    .split_once('：')
                    .unwrap()
                    .1
                    .split("</p>")
                    .next()
                    .unwrap();
                got.push(text.to_string());
            }
            match page.split("href=\"/history?turn=0&amp;from=").nth(1) {
                Some(rest) => {
                    let from = rest.split('"').next().unwrap();
                    uri = format!("/history?turn=0&from={from}");
                }
                None => {
                    assert!(
                        page.contains("href=\"/history?turn=1\">前のターン"),
                        "{page}"
                    );
                    break;
                }
            }
        }
        let want: Vec<String> = want.iter().map(|w| crate::layout::esc(w)).collect();
        assert_eq!(got, want);

        // 古いターンも開ける。範囲外は空
        let page = body(send(&state, get("/history?turn=1", None)).await).await;
        assert!(page.contains("<strong>ターン"), "{page}");
        let page = body(send(&state, get("/history?turn=99", None)).await).await;
        assert!(page.contains("このターンのログはありません"), "{page}");

        let top = body(send(&state, get("/", None)).await).await;
        assert!(top.contains("続きと、それより前の出来事"), "{top}");
    }

    /// 大きな地図は canvas で描き (データは JSON で埋め込む)、`?map=table` なら表で出す
    #[tokio::test]
    async fn large_maps_are_drawn_on_a_canvas() {
        let (state, _dir) = crate::tests::test_app_with(hakoniwa_core::GameConfig {
            island_size: 40,
            ..Default::default()
        });
        let id = crate::edit::edit(&state, |game, rng| {
            hakoniwa_core::actions::create::new_island(
                game,
                &state.config,
                hakoniwa_core::actions::Request {
                    now: 1_794_250_000,
                    remote_addr: "10.0.0.9",
                },
                rng,
                &hakoniwa_core::actions::create::NewIslandInput {
                    name: "大地",
                    owner_name: "o",
                    password: "pw",
                    password2: "pw",
                    message: "m",
                },
            )
        })
        .await
        .unwrap();

        let page = body(send(&state, get(&format!("/island/{id}"), None)).await).await;
        assert!(
            page.contains("data-map") && page.contains("<canvas"),
            "{page}"
        );
        assert!(!page.contains("role=\"grid\""));
        let json = page
            .split("<script type=\"application/json\" class=\"map-data\">")
            .nth(1)
            .unwrap()
            .split("</script>")
            .next()
            .unwrap();
        let data: serde_json::Value = serde_json::from_str(json).unwrap();
        assert_eq!(data["size"], 40);
        assert_eq!(data["t"].as_array().unwrap().len(), 1600);
        assert_eq!(data["l"].as_array().unwrap().len(), 1600);
        assert_eq!(data["owner"], false);
        // 辞書の番号は辞書の中を指す
        let tiles = data["tiles"].as_array().unwrap().len() as u64;
        assert!(
            data["t"]
                .as_array()
                .unwrap()
                .iter()
                .all(|v| v.as_u64().unwrap() < tiles)
        );

        let page = body(send(&state, get(&format!("/island/{id}?map=table"), None)).await).await;
        assert!(page.contains("role=\"grid\"") && !page.contains("<canvas"));
    }

    #[tokio::test]
    async fn admin_flow() {
        let (mut state, _dir) = legacy_app();
        // マスターパスワードが無ければ管理画面は無い
        assert_eq!(send(&state, get("/admin", None)).await.status(), 404);
        std::sync::Arc::get_mut(&mut state)
            .unwrap()
            .config
            .passwords
            .master = Some("mm".into());
        let res = send(&state, post("/admin/login", None, &[("password", "x")])).await;
        assert_eq!(res.status(), 401);
        let res = send(&state, post("/admin/login", None, &[("password", "mm")])).await;
        assert_eq!(res.status(), 303);
        let cookie = res.headers()[axum::http::header::SET_COOKIE]
            .to_str()
            .unwrap()
            .split(';')
            .next()
            .unwrap()
            .to_string();
        let token = cookie.split_once('=').unwrap().1.to_string();
        let csrf = state.sessions.get(&token, crate::now_unix()).unwrap().csrf;
        let page = body(send(&state, get("/admin", Some(&cookie))).await).await;
        assert!(
            page.contains("現役データ") && page.contains("裏ランキング"),
            "{page}"
        );

        let res = send(
            &state,
            post(
                "/admin/time",
                Some(&cookie),
                &[("csrf", &csrf), ("last_time", "1000")],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        assert_eq!(state.game.read().await.world.last_time, 1000);
        // 確認の文字が違えば消さない
        send(
            &state,
            post(
                "/admin/reset",
                Some(&cookie),
                &[("csrf", &csrf), ("confirm", "x")],
            ),
        )
        .await;
        assert_eq!(state.game.read().await.world.islands.len(), 3);
        let res = send(
            &state,
            post(
                "/admin/reset",
                Some(&cookie),
                &[("csrf", &csrf), ("confirm", "削除する")],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        assert!(state.game.read().await.world.islands.is_empty());
        // 消す前のデータはバックアップに残っていて、戻せる
        let res = send(
            &state,
            post(
                "/admin/restore",
                Some(&cookie),
                &[("csrf", &csrf), ("n", "0")],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        assert_eq!(state.game.read().await.world.islands.len(), 3);
        // データディレクトリを読み直しても戻っている (再起動したときと同じ)
        let (_, saved) = hakoniwa_core::persist::DataDir::open(&state.data_dir)
            .unwrap()
            .unwrap();
        assert_eq!(saved.world.islands.len(), 3);
        assert_eq!(saved.world.last_time, 1000);
        let page = body(send(&state, get("/admin", Some(&cookie))).await).await;
        assert!(page.contains("バックアップ0"), "{page}");
    }

    #[tokio::test]
    async fn extras_flow() {
        let (state, _dir) = legacy_app();
        let (cookie, csrf) = login(&state, 1, "pass1").await;
        let page = body(send(&state, get("/owner", Some(&cookie))).await).await;
        assert!(page.contains("援助射撃"), "{page}");
        // 援助射撃の許可を島 2 に申請し、島 2 が許可する
        let res = send(
            &state,
            post(
                "/owner/extra",
                Some(&cookie),
                &[
                    ("csrf", &csrf),
                    ("action", "ms-request"),
                    ("target", "2"),
                    ("amount", "3"),
                ],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        assert_eq!(
            state
                .game
                .read()
                .await
                .world
                .islands
                .iter()
                .find(|i| i.id == 1)
                .unwrap()
                .etc_raw[2],
            "1,3,2"
        );
        let (cookie2, csrf2) = login(&state, 2, "pass2").await;
        let res = send(
            &state,
            post(
                "/owner/extra",
                Some(&cookie2),
                &[
                    ("csrf", &csrf2),
                    ("action", "ms-grant"),
                    ("target", "1"),
                    ("amount", "3"),
                ],
            ),
        )
        .await;
        assert_eq!(res.status(), 303);
        assert_eq!(
            state
                .game
                .read()
                .await
                .world
                .islands
                .iter()
                .find(|i| i.id == 1)
                .unwrap()
                .etc_raw[2],
            "2,3,2"
        );
        // アンケートは設定で無効
        let res = send(
            &state,
            post(
                "/survey",
                Some(&cookie),
                &[("csrf", &csrf), ("choice", "1")],
            ),
        )
        .await;
        assert_eq!(res.status(), 404);
    }
}
