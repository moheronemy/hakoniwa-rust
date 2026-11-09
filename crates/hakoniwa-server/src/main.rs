//! Hakoniwa R.A. Rust 版の Web サーバー。
//!
//! いまは土台だけで、保存データを読み込んでトップページ (順位表とログ) を表示する。
//! ターン処理・島の登録・開発画面などはまだ無い (docs/PORTING.md を参照)。

mod page;

use std::path::PathBuf;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{Context, Result};
use axum::Router;
use axum::extract::State;
use axum::response::Html;
use axum::routing::get;
use clap::Parser;
use hakoniwa_core::{GameConfig, GameState, storage};
use serde::Deserialize;
use tokio::sync::RwLock;

#[derive(Parser)]
#[command(version, about = "Hakoniwa R.A. Rust 版のサーバー")]
struct Args {
    /// 設定ファイル (TOML)。省略時は既定値で動く
    #[arg(long, short)]
    config: Option<PathBuf>,
}

/// サーバーの設定ファイル
#[derive(Debug, Deserialize)]
#[serde(default)]
struct ServerConfig {
    /// 待ち受けるアドレス
    bind: String,
    /// セーブデータのパス
    state_path: PathBuf,
    /// ゲームの設定
    game: GameConfig,
}

impl Default for ServerConfig {
    fn default() -> Self {
        Self {
            bind: "127.0.0.1:8080".into(),
            state_path: "data/state.json".into(),
            game: GameConfig::default(),
        }
    }
}

pub struct AppState {
    pub config: GameConfig,
    pub game: RwLock<GameState>,
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
        .route("/healthz", get(|| async { "ok" }))
        .with_state(state)
}

async fn top_page(State(app): State<Arc<AppState>>) -> Html<String> {
    let game = app.game.read().await;
    Html(page::top(&app.config, &game, now_unix()))
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

    let game = match storage::load(&config.state_path)? {
        Some(game) => {
            tracing::info!(
                path = %config.state_path.display(),
                turn = game.world.turn,
                islands = game.world.islands.len(),
                "セーブデータを読み込みました"
            );
            game
        }
        None => {
            let game = GameState::new_game(now_unix(), &config.game);
            storage::save(&config.state_path, &game)?;
            tracing::info!(path = %config.state_path.display(), "新しいゲームを作りました");
            game
        }
    };

    let state = Arc::new(AppState {
        config: config.game,
        game: RwLock::new(game),
    });
    let listener = tokio::net::TcpListener::bind(&config.bind)
        .await
        .with_context(|| format!("{} で待ち受けできません", config.bind))?;
    tracing::info!("http://{} で待ち受けています", listener.local_addr()?);
    axum::serve(listener, app(state))
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

    #[tokio::test]
    async fn serves_top_page() {
        let config = GameConfig::default();
        let game = GameState::new_game(1_794_250_000, &config);
        let state = Arc::new(AppState {
            config,
            game: RwLock::new(game),
        });
        let res = app(state)
            .oneshot(Request::get("/").body(Body::empty()).unwrap())
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::OK);
        let body = res.into_body().collect().await.unwrap().to_bytes();
        let html = String::from_utf8(body.to_vec()).unwrap();
        assert!(html.contains("ターン1"));
        assert!(html.contains(page::ORIGINAL_SITE));
    }
}
