//! Hakoniwa R.A. Rust 版の Web サーバー。
//!
//! 保存データを読み込んで画面を出し、時刻が来たらターンを進める。
//! 画面は Perl 版を再現せず作り直している (ゲームのルールは `hakoniwa-core` が Perl 版のとおりに持つ)。

mod edit;
mod layout;
mod pages;
mod render;
mod session;
mod sets;
mod store;
mod turns;

use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use anyhow::{Context, Result};
use axum::Router;
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Redirect, Response};
use axum::routing::{get, post};
use clap::Parser;
use hakoniwa_core::persist::DataDir;
use hakoniwa_core::{GameConfig, GameState, storage};
use rand::SeedableRng;
use rand::rngs::StdRng;
use serde::Deserialize;
use sets::{Set, Sets};

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
    /// `--export-json` で書き出すセットの ID (`sets_dir` の下のディレクトリ名)。省略時は既定のセット
    #[arg(long, value_name = "ID", requires = "export_json")]
    set: Option<String>,
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
    /// 同時に回すターン処理の数 (全セットで)。0 なら CPU の数
    turn_workers: usize,
    /// 画面まわりの設定
    #[serde(flatten)]
    options: ServerOptions,
    /// ゲームの設定 (既定のセット)
    game: GameConfig,
    /// 既定のセットを動かすか (`[game]`・`state_path`・`data_dir` のゲーム)。
    /// どのセットのホスト名にも当たらない要求はこのセットに来る。false なら 404
    default_set: bool,
    /// 複数のゲーム (セット) を置くディレクトリ。`<ID>/hakoniwa.toml` ([`SetConfig`]) があるものを
    /// すべて読み込む (docs/MULTISET.md)
    sets_dir: Option<PathBuf>,
}

/// セットごとの設定ファイル (`sets_dir/<ID>/hakoniwa.toml`)
#[derive(Debug, Default, Deserialize)]
#[serde(default)]
struct SetConfig {
    /// このセットのホスト名 (`set1.example.com` など。ポートは書かない)
    hosts: Vec<String>,
    /// 最初の起動で読み込む JSON。省略時は `<ID>/state.json`
    state_path: Option<PathBuf>,
    /// データディレクトリ。省略時は `<ID>/store`
    data_dir: Option<PathBuf>,
    /// ゲームの設定
    game: GameConfig,
}

impl SetConfig {
    fn read(dir: &std::path::Path) -> Result<Self> {
        let path = dir.join("hakoniwa.toml");
        let text = std::fs::read_to_string(&path)
            .with_context(|| format!("{} を読めません", path.display()))?;
        toml::from_str(&text).with_context(|| format!("{} の形式が違います", path.display()))
    }

    /// (state_path, data_dir)
    fn paths(&self, dir: &std::path::Path) -> (PathBuf, PathBuf) {
        (
            self.state_path
                .clone()
                .unwrap_or_else(|| dir.join("state.json")),
            self.data_dir.clone().unwrap_or_else(|| dir.join("store")),
        )
    }
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
            turn_workers: 0,
            options: ServerOptions::default(),
            game: GameConfig::default(),
            default_set: true,
            sets_dir: None,
        }
    }
}

impl ServerConfig {
    /// 既定のセットのデータディレクトリ
    fn data_dir(&self) -> PathBuf {
        self.data_dir.clone().unwrap_or_else(|| {
            self.state_path
                .parent()
                .unwrap_or(std::path::Path::new("."))
                .join("store")
        })
    }

    /// `sets_dir` の下のセット (ID とディレクトリ。ID の順)
    fn set_dirs(&self) -> Result<Vec<(String, PathBuf)>> {
        let Some(root) = &self.sets_dir else {
            return Ok(Vec::new());
        };
        let mut out = Vec::new();
        for entry in
            std::fs::read_dir(root).with_context(|| format!("{} を読めません", root.display()))?
        {
            let path = entry?.path();
            if path.join("hakoniwa.toml").is_file() {
                let id = path
                    .file_name()
                    .map(|n| n.to_string_lossy().into_owned())
                    .unwrap_or_default();
                out.push((id, path));
            }
        }
        out.sort();
        Ok(out)
    }
}

/// 1 つのセットを読み込む (データディレクトリが無ければ作る)
fn open_set(
    state_path: &std::path::Path,
    data_dir: PathBuf,
    game: GameConfig,
    options: ServerOptions,
    stagger: Option<&str>,
) -> Result<Arc<AppState>> {
    let (data, state) = open_data(&data_dir, state_path, &game, stagger)?;
    // ログインはデータディレクトリに残し、再起動しても続くようにする
    let sessions = session::Sessions::open(&data_dir.join("sessions.json"), now_unix());
    Ok(Arc::new(AppState {
        config: game,
        options,
        sessions,
        data_dir,
        game: store::Store::new(state, StdRng::from_entropy(), data),
    }))
}

/// 設定ファイルのセット (既定のセットと `sets_dir` の下) をすべて読み込む
fn open_sets(config: &ServerConfig) -> Result<Sets> {
    let mut sets = Sets::default();
    if config.default_set {
        sets.set_default(open_set(
            &config.state_path,
            config.data_dir(),
            config.game.clone(),
            config.options.clone(),
            None,
        )?);
    }
    for (id, dir) in config.set_dirs()? {
        let set = SetConfig::read(&dir)?;
        if set.hosts.is_empty() {
            anyhow::bail!("セット {id} にホスト名 (hosts) がありません");
        }
        let (state_path, data_dir) = set.paths(&dir);
        // 新しく作るセットは ID から決まる分だけ開始時刻をずらす (ターンが一斉に来ないように)
        let app = open_set(
            &state_path,
            data_dir,
            set.game,
            config.options.clone(),
            Some(&id),
        )
        .with_context(|| format!("セット {id} を読み込めません"))?;
        sets.add(&id, &set.hosts, app)?;
    }
    if sets.default_set().is_none() && sets.list().is_empty() {
        anyhow::bail!(
            "動かすゲームがありません (default_set = false で、sets_dir にセットもありません)"
        );
    }
    Ok(sets)
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

/// 1 つのゲームだけを動かすサーバー (テストと、これまでの形)
#[cfg(test)]
pub fn app(state: Arc<AppState>) -> Router {
    router(Arc::new(Sets::single(state)))
}

/// 要求のホスト名でセットを選んで画面を出すサーバー
pub fn router(sets: Arc<Sets>) -> Router {
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
        .with_state(sets)
}

async fn top_page(Set(app): Set, headers: HeaderMap, uri: axum::http::Uri) -> Response {
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
async fn debug_turn(Set(app): Set) -> Response {
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

/// 新しいゲームの最終更新時刻を、ID から決まる秒数 (`0..unit_time`) だけずらす。
/// ずらしたあとも `now` 以前の、いちばん近い時刻にする (最初のターンは 1 ターンの秒数より先にはならない)
fn staggered_start(game: &mut GameState, config: &GameConfig, id: &str, now: i64) {
    let unit = config.unit_time.max(1);
    // FNV-1a (版や環境で変わらない)
    let hash = id.bytes().fold(0xcbf2_9ce4_8422_2325_u64, |h, b| {
        (h ^ u64::from(b)).wrapping_mul(0x100_0000_01b3)
    });
    let offset = (hash % unit as u64) as i64;
    let mut start = game.world.last_time + offset;
    if start > now {
        start -= unit;
    }
    game.world.last_time = start;
}

/// データディレクトリを読み込む。無ければ JSON のセーブデータ (`state_path`) から作り、
/// それも無ければ新しいゲームを始める (`stagger` があれば、その ID で開始時刻をずらす)
fn open_data(
    data_dir: &std::path::Path,
    state_path: &std::path::Path,
    config: &GameConfig,
    stagger: Option<&str>,
) -> Result<(DataDir, GameState)> {
    let started = std::time::Instant::now();
    if let Some((data, game)) = DataDir::open(data_dir)? {
        if let Some(from) = data.migrated_from() {
            tracing::info!(
                path = %data_dir.display(),
                from,
                to = hakoniwa_core::persist::FORMAT,
                "セーブデータを新しい形式の版に書き直しました"
            );
        }
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
            let now = now_unix();
            let mut game = GameState::new_game(now, config);
            if let Some(id) = stagger {
                staggered_start(&mut game, config, id, now);
            }
            game
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

    if let Some(out) = &args.export_json {
        let data_dir = match &args.set {
            None => config.data_dir(),
            Some(id) => {
                let dir = config
                    .set_dirs()?
                    .into_iter()
                    .find(|(i, _)| i == id)
                    .map(|(_, d)| d)
                    .with_context(|| format!("セット {id} がありません"))?;
                SetConfig::read(&dir)?.paths(&dir).1
            }
        };
        let (_, game) = DataDir::open(&data_dir)?
            .with_context(|| format!("{} にセーブデータがありません", data_dir.display()))?;
        storage::save(out, &game)?;
        tracing::info!(path = %out.display(), turn = game.world.turn, "JSON に書き出しました");
        return Ok(());
    }

    let sets = Arc::new(open_sets(&config)?);
    let every = Duration::from_secs(config.tick_secs.max(1));
    let workers = match config.turn_workers {
        0 => std::thread::available_parallelism().map_or(1, |n| n.get()),
        n => n,
    };
    tokio::spawn(turns::Scheduler::new(sets.all(), workers).run(every));
    tracing::info!(
        default = sets.default_set().is_some(),
        sets = sets.list().len(),
        turn_workers = workers,
        "ゲームを読み込みました"
    );
    let listener = tokio::net::TcpListener::bind(&config.bind)
        .await
        .with_context(|| format!("{} で待ち受けできません", config.bind))?;
    tracing::info!("http://{} で待ち受けています", listener.local_addr()?);
    axum::serve(
        listener,
        router(sets).into_make_service_with_connect_info::<SocketAddr>(),
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

    fn with_host(mut req: Request<Body>, host: &str) -> Request<Body> {
        req.headers_mut()
            .insert(axum::http::header::HOST, host.parse().unwrap());
        req
    }

    fn register_req(name: &str) -> Request<Body> {
        let body = format!("name={name}&owner=o&password=pw&password2=pw&message=m");
        Request::post("/register")
            .header(
                axum::http::header::CONTENT_TYPE,
                "application/x-www-form-urlencoded",
            )
            .body(Body::from(body))
            .unwrap()
    }

    /// 要求のホスト名でセットが決まり、セットどうしは状態もログインも混ざらない
    #[tokio::test]
    async fn sets_are_chosen_by_host() {
        let (a, _da) = test_app();
        let (b, _db) = test_app();
        let mut sets = Sets::default();
        sets.add("a", &["a.example.com".into()], a.clone()).unwrap();
        sets.add("b", &["b.example.com".into()], b.clone()).unwrap();
        let server = router(Arc::new(sets));

        // セット a に島を登録する (ポートと大文字は無視する)
        let res = server
            .clone()
            .oneshot(with_host(register_req("alpha"), "A.Example.com:8080"))
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::SEE_OTHER);
        let cookie = res.headers()[axum::http::header::SET_COOKIE]
            .to_str()
            .unwrap()
            .split(';')
            .next()
            .unwrap()
            .to_string();
        assert_eq!(a.game.snapshot().world.islands.len(), 1);
        assert_eq!(b.game.snapshot().world.islands.len(), 0);

        // a のログインは a でだけ通る
        let owner = |host: &str| {
            with_host(
                Request::get("/owner")
                    .header(axum::http::header::COOKIE, &cookie)
                    .body(Body::empty())
                    .unwrap(),
                host,
            )
        };
        let res = server
            .clone()
            .oneshot(owner("a.example.com"))
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::OK);
        let res = server
            .clone()
            .oneshot(owner("b.example.com"))
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::UNAUTHORIZED);

        // 既定のセットが無ければ、知らないホストは 404
        let get = |host: &str| with_host(Request::get("/").body(Body::empty()).unwrap(), host);
        let res = server.clone().oneshot(get("c.example.com")).await.unwrap();
        assert_eq!(res.status(), StatusCode::NOT_FOUND);

        // 既定のセットがあれば、知らないホストはそこに来る
        let (d, _dd) = test_app();
        let mut sets = Sets::default();
        sets.add("a", &["a.example.com".into()], a.clone()).unwrap();
        sets.set_default(d.clone());
        let server = router(Arc::new(sets));
        let res = server
            .clone()
            .oneshot(with_host(register_req("delta"), "c.example.com"))
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::SEE_OTHER);
        assert_eq!(d.game.snapshot().world.islands.len(), 1);
        assert_eq!(a.game.snapshot().world.islands.len(), 1);
    }

    /// 再起動しても (同じデータディレクトリから開き直しても) ログインが続く
    #[tokio::test]
    async fn login_survives_restart() {
        let tmp = tempfile::tempdir().unwrap();
        let state_path = tmp.path().join("state.json");
        let data_dir = tmp.path().join("store");
        let open = || {
            open_set(
                &state_path,
                data_dir.clone(),
                GameConfig::default(),
                ServerOptions::default(),
                None,
            )
            .unwrap()
        };
        let first = open();
        let res = app(first.clone())
            .oneshot(register_req("kappa"))
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::SEE_OTHER);
        let cookie = res.headers()[axum::http::header::SET_COOKIE]
            .to_str()
            .unwrap()
            .split(';')
            .next()
            .unwrap()
            .to_string();
        drop(first);

        let second = open();
        let res = app(second)
            .oneshot(
                Request::get("/owner")
                    .header(axum::http::header::COOKIE, &cookie)
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::OK);
        let html = String::from_utf8(res.into_body().collect().await.unwrap().to_bytes().to_vec())
            .unwrap();
        assert!(html.contains("kappa島開発計画"), "{html}");
    }

    /// 新しいセットの開始時刻は ID で決まり、1 ターンの秒数の範囲で、いまより前になる
    #[test]
    fn staggered_starts_spread_within_one_turn() {
        let config = GameConfig {
            unit_time: 3600,
            ..GameConfig::default()
        };
        let now = 1_794_300_123;
        let mut starts = std::collections::BTreeSet::new();
        for i in 0..50 {
            let mut game = GameState::new_game(now, &config);
            let base = game.world.last_time;
            staggered_start(&mut game, &config, &format!("set{i}"), now);
            let t = game.world.last_time;
            assert!(t <= now && t > now - config.unit_time, "{t}");
            assert!((t - base).rem_euclid(config.unit_time) < config.unit_time);
            starts.insert(t);
            // 同じ ID なら同じ時刻
            let mut again = GameState::new_game(now, &config);
            staggered_start(&mut again, &config, &format!("set{i}"), now);
            assert_eq!(again.world.last_time, t);
        }
        // 50 セットがほぼ別々の時刻になる
        assert!(starts.len() > 40, "{}", starts.len());
    }

    /// `sets_dir` の下の `<ID>/hakoniwa.toml` をすべて読み込む
    #[test]
    fn sets_are_loaded_from_sets_dir() {
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path().join("sets");
        let write = |id: &str, toml: &str| {
            std::fs::create_dir_all(root.join(id)).unwrap();
            std::fs::write(root.join(id).join("hakoniwa.toml"), toml).unwrap();
        };
        write("s1", "hosts = [\"s1.test\"]\n[game]\nisland_size = 20\n");
        write("s2", "hosts = [\"s2.test\", \"other.test\"]\n");
        // 設定ファイルの無いディレクトリは読まない
        std::fs::create_dir_all(root.join("notes")).unwrap();
        let config = ServerConfig {
            default_set: false,
            sets_dir: Some(root.clone()),
            ..ServerConfig::default()
        };
        let sets = open_sets(&config).unwrap();
        let ids: Vec<&str> = sets.list().iter().map(|(id, _)| id.as_str()).collect();
        assert_eq!(ids, ["s1", "s2"]);
        assert!(sets.default_set().is_none());
        let s1 = sets.find("s1.test").unwrap();
        assert_eq!(s1.config.island_size, 20);
        assert!(Arc::ptr_eq(
            &sets.find("other.test").unwrap(),
            sets.get("s2").unwrap()
        ));
        assert!(sets.find("nobody.test").is_none());
        // データディレクトリは <ID>/store に作られている
        assert!(root.join("s1/store/snapshot.bin").exists());

        // ホスト名が重なる・書いていないのはエラー
        write("s3", "hosts = [\"S1.test\"]\n");
        assert!(open_sets(&config).is_err());
        write("s3", "");
        let e = open_sets(&config).err().unwrap().to_string();
        assert!(e.contains("s3"), "{e}");
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
