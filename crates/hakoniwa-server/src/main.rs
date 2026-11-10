//! Hakoniwa R.A. Rust 版の Web サーバー。
//!
//! 保存データを読み込んで画面を出し、時刻が来たらターンを進める。
//! 画面は Perl 版を再現せず作り直している (ゲームのルールは `hakoniwa-core` が Perl 版のとおりに持つ)。

mod edit;
mod layout;
mod pages;
mod render;
mod session;
mod store;
mod turns;

use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use anyhow::{Context, Result};
use axum::Router;
use axum::extract::State;
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Redirect, Response};
use axum::routing::{get, post};
use clap::Parser;
use hakoniwa_core::persist::DataDir;
use hakoniwa_core::{GameConfig, GameState, storage};
use rand::SeedableRng;
use rand::rngs::StdRng;
use serde::Deserialize;

#[derive(Parser)]
#[command(version, about = "Hakoniwa R.A. Rust 版のサーバー")]
struct Args {
    /// 設定ファイル (TOML)。省略時は既定値で動く
    #[arg(long, short)]
    config: Option<PathBuf>,
    /// サーバーを起動せず、データディレクトリの状態を JSON に書き出して終わる
    /// (中身を確かめるとき、データの形式の版が変わるときに使う。書き出した JSON は
    /// データディレクトリを消して `state_path` に置けば、次の起動で読み込まれる)
    #[arg(long, value_name = "PATH")]
    export_json: Option<PathBuf>,
}

/// サーバーの設定ファイル
#[derive(Debug, Deserialize)]
#[serde(default)]
struct ServerConfig {
    /// 待ち受けるアドレス
    bind: String,
    /// JSON のセーブデータ (`hako-convert` が書くもの)。データディレクトリがまだ無いときに読み込む
    state_path: PathBuf,
    /// データディレクトリ (スナップショット・操作の差分・ターンごとのログ・バックアップ)。
    /// 省略時は `state_path` と同じディレクトリの `store`
    data_dir: Option<PathBuf>,
    /// ターンの時刻を確かめる間隔 (秒)
    tick_secs: u64,
    /// 画面まわりの設定
    #[serde(flatten)]
    options: ServerOptions,
    /// ゲームの設定
    game: GameConfig,
}

/// 画面まわりの設定 (ゲームのルールに関係しないもの)
#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct ServerOptions {
    /// ログインのクッキーに Secure を付ける (HTTPS で公開するとき)
    pub secure_cookie: bool,
    /// リバースプロキシの X-Forwarded-For を接続元として信じる
    pub trust_forwarded: bool,
    /// Perl 版の地形の画像を置いたディレクトリ。無ければ地図は色と文字のタイルで描く
    /// (画像は移植元の著作物で再配布できないので同梱していない)
    pub image_dir: Option<PathBuf>,
    /// トップページの「最近の出来事」に出す行数の上限 (続きは /history で見る)。
    /// 多くの島・大きな地図では 1 ターンのログが数百万行になるので打ち切る
    pub top_log_lines: usize,
    /// 最近の出来事 (/history) の 1 ページの行数
    pub history_page_lines: usize,
}

impl Default for ServerOptions {
    fn default() -> Self {
        Self {
            secure_cookie: false,
            trust_forwarded: false,
            image_dir: None,
            top_log_lines: 500,
            history_page_lines: 500,
        }
    }
}

impl Default for ServerConfig {
    fn default() -> Self {
        Self {
            bind: "127.0.0.1:8080".into(),
            state_path: "data/state.json".into(),
            data_dir: None,
            tick_secs: 10,
            options: ServerOptions::default(),
            game: GameConfig::default(),
        }
    }
}

pub struct AppState {
    pub config: GameConfig,
    pub options: ServerOptions,
    pub sessions: session::Sessions,
    /// データディレクトリ (バックアップの一覧に使う)
    pub data_dir: PathBuf,
    /// ゲームの状態 (読み取りはスナップショット、書き込みは順番待ち。[`store`] を参照)
    pub game: store::Store,
}

pub fn now_unix() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs() as i64)
        .unwrap_or(0)
}

pub fn app(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/", get(top_page))
        .route(
            "/login",
            get(pages::auth::login_page).post(pages::auth::login),
        )
        .route("/logout", post(pages::auth::logout))
        .route(
            "/register",
            get(pages::register::register_page).post(pages::register::register),
        )
        .route("/owner", get(pages::owner::owner_page))
        .route("/owner/change", post(pages::register::change))
        .route("/owner/change-owner", post(pages::register::change_owner))
        .route("/owner/comment", post(pages::owner::comment))
        .route("/owner/command", post(pages::owner::command))
        .route("/owner/policy", post(pages::owner::policy))
        .route("/owner/lbbs", post(pages::owner::lbbs))
        .route("/owner/extra", post(pages::extras::extra))
        .route("/survey", post(pages::extras::vote))
        .route("/island/{id}", get(pages::island::island_page))
        .route("/island/{id}/lbbs", post(pages::island::visitor_lbbs_post))
        .route("/img/{name}", get(pages::images::image))
        .route("/history", get(pages::history::history_page))
        .route("/admin", get(pages::admin::admin_page))
        .route("/admin/login", post(pages::admin::admin_login))
        .route("/admin/time", post(pages::admin::set_time))
        .route("/admin/restore", post(pages::admin::restore))
        .route("/admin/delete-backup", post(pages::admin::delete_backup))
        .route("/admin/reset", post(pages::admin::reset))
        .route("/healthz", get(|| async { "ok" }))
        .route("/debug/turn", post(debug_turn))
        .with_state(state)
}

async fn top_page(
    State(app): State<Arc<AppState>>,
    headers: HeaderMap,
    uri: axum::http::Uri,
) -> Response {
    let login = pages::login_of(&app, &headers).await;
    let body = {
        let game = app.game.read().await;
        pages::top::top(
            &app.config,
            &game,
            now_unix(),
            uri.query().unwrap_or_default(),
            login.as_ref().map(|l| l.session.csrf.as_str()),
            app.options.top_log_lines,
        )
    };
    pages::render(&app, login.as_ref(), "", &body)
        .await
        .into_response()
}

/// デバッグモードの「ターンを進める」
async fn debug_turn(State(app): State<Arc<AppState>>) -> Response {
    if !app.config.debug {
        return StatusCode::NOT_FOUND.into_response();
    }
    match turns::force_turn(&app).await {
        Ok(turn) => {
            tracing::info!(turn, "デバッグモードでターンを進めました");
            Redirect::to("/").into_response()
        }
        Err(e) => {
            tracing::error!("ターン処理に失敗しました: {e:#}");
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                "ターン処理に失敗しました",
            )
                .into_response()
        }
    }
}

/// データディレクトリを読み込む。無ければ JSON のセーブデータ (`state_path`) から作り、
/// それも無ければ新しいゲームを始める
fn open_data(
    data_dir: &std::path::Path,
    state_path: &std::path::Path,
    config: &GameConfig,
) -> Result<(DataDir, GameState)> {
    let started = std::time::Instant::now();
    if let Some((data, game)) = DataDir::open(data_dir)? {
        tracing::info!(
            path = %data_dir.display(),
            turn = game.world.turn,
            islands = game.world.islands.len(),
            secs = started.elapsed().as_secs_f64(),
            "セーブデータを読み込みました"
        );
        return Ok((data, game));
    }
    let game = match storage::load(state_path)? {
        Some(game) => {
            tracing::info!(
                from = %state_path.display(),
                to = %data_dir.display(),
                turn = game.world.turn,
                islands = game.world.islands.len(),
                "JSON のセーブデータをデータディレクトリに移しました"
            );
            game
        }
        None => {
            tracing::info!(path = %data_dir.display(), "新しいゲームを作りました");
            GameState::new_game(now_unix(), config)
        }
    };
    let data = DataDir::create(data_dir, &game)?;
    Ok((data, game))
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()),
        )
        .init();

    let args = Args::parse();
    let config: ServerConfig = match &args.config {
        Some(path) => {
            let text = std::fs::read_to_string(path)
                .with_context(|| format!("{} を読めません", path.display()))?;
            toml::from_str(&text).with_context(|| format!("{} の形式が違います", path.display()))?
        }
        None => ServerConfig::default(),
    };

    let data_dir = config.data_dir.clone().unwrap_or_else(|| {
        config
            .state_path
            .parent()
            .unwrap_or(std::path::Path::new("."))
            .join("store")
    });
    if let Some(out) = &args.export_json {
        let (_, game) = DataDir::open(&data_dir)?
            .with_context(|| format!("{} にセーブデータがありません", data_dir.display()))?;
        storage::save(out, &game)?;
        tracing::info!(path = %out.display(), turn = game.world.turn, "JSON に書き出しました");
        return Ok(());
    }
    let (data, game) = open_data(&data_dir, &config.state_path, &config.game)?;

    let state = Arc::new(AppState {
        config: config.game,
        options: config.options,
        sessions: Default::default(),
        data_dir,
        game: store::Store::new(game, StdRng::from_entropy(), data),
    });
    tokio::spawn(turns::scheduler(
        state.clone(),
        Duration::from_secs(config.tick_secs.max(1)),
    ));
    let listener = tokio::net::TcpListener::bind(&config.bind)
        .await
        .with_context(|| format!("{} で待ち受けできません", config.bind))?;
    tracing::info!("http://{} で待ち受けています", listener.local_addr()?);
    axum::serve(
        listener,
        app(state).into_make_service_with_connect_info::<SocketAddr>(),
    )
    .with_graceful_shutdown(async {
        let _ = tokio::signal::ctrl_c().await;
    })
    .await?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::Body;
    use axum::http::{Request, StatusCode};
    use http_body_util::BodyExt;
    use tower::ServiceExt;

    /// 一時ディレクトリに保存する新しいゲーム
    pub(crate) fn test_app_with(config: GameConfig) -> (Arc<AppState>, tempfile::TempDir) {
        let dir = tempfile::tempdir().unwrap();
        let game = GameState::new_game(1_794_250_000, &config);
        let data_dir = dir.path().join("store");
        let data = DataDir::create(&data_dir, &game).unwrap();
        let app = Arc::new(AppState {
            config,
            options: ServerOptions::default(),
            sessions: Default::default(),
            data_dir,
            game: store::Store::new(game, StdRng::seed_from_u64(0), data),
        });
        (app, dir)
    }

    pub(crate) fn test_app() -> (Arc<AppState>, tempfile::TempDir) {
        test_app_with(GameConfig::default())
    }

    #[tokio::test]
    async fn debug_turn_requires_debug_mode() {
        let (state, _dir) = test_app();
        let res = app(state)
            .oneshot(Request::post("/debug/turn").body(Body::empty()).unwrap())
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::NOT_FOUND);

        let (state, _dir) = test_app_with(GameConfig {
            debug: true,
            ..Default::default()
        });
        let res = app(state.clone())
            .oneshot(Request::post("/debug/turn").body(Body::empty()).unwrap())
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::SEE_OTHER);
        assert_eq!(state.game.read().await.world.turn, 2);
    }

    /// 書き込み (ターン処理など) のあいだも画面は 1 つ前の状態で返り、
    /// そのあいだに来た書き込みは待って、前の書き込みが終わってから行われる
    #[tokio::test]
    async fn pages_are_served_while_a_writer_holds_the_state() {
        let (state, _dir) = test_app_with(GameConfig {
            debug: true,
            ..Default::default()
        });
        let writer = state.game.write().await;

        let res = tokio::time::timeout(
            Duration::from_secs(5),
            app(state.clone()).oneshot(Request::get("/").body(Body::empty()).unwrap()),
        )
        .await
        .expect("書き込み中に画面が返らない")
        .unwrap();
        assert_eq!(res.status(), StatusCode::OK);

        let turn = tokio::spawn(
            app(state.clone()).oneshot(Request::post("/debug/turn").body(Body::empty()).unwrap()),
        );
        tokio::time::sleep(Duration::from_millis(100)).await;
        assert!(!turn.is_finished(), "書き込みが順番を待っていない");
        assert_eq!(state.game.snapshot().world.turn, 1);

        drop(writer);
        let res = turn.await.unwrap().unwrap();
        assert_eq!(res.status(), StatusCode::SEE_OTHER);
        assert_eq!(state.game.snapshot().world.turn, 2);
    }

    #[tokio::test]
    async fn serves_top_page() {
        let (state, _dir) = test_app();
        let res = app(state)
            .oneshot(Request::get("/").body(Body::empty()).unwrap())
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::OK);
        let body = res.into_body().collect().await.unwrap().to_bytes();
        let html = String::from_utf8(body.to_vec()).unwrap();
        assert!(html.contains("ターン1"));
        assert!(html.contains(layout::ORIGINAL_SITE));
    }
}
