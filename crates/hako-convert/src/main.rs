//! Perl 版 (Hakoniwa R.A.) のセーブデータを移植版の JSON に変換する。
//!
//! 使い方:
//!     hako-convert <Perl版の data ディレクトリ> <出力する state.json>
//!     hako-convert --settings hako-main.cgi <Perl版の data ディレクトリ> <出力する state.json>
//!
//! `--settings` を付けると Perl 版の設定 (`hako-main.cgi`) も読み、島の大きさなどの変換の設定に
//! 使ったうえで、移植版のサーバーの設定ファイル (`--config-out`、既定は出力先と同じ場所の
//! `hakoniwa.toml`) を書く。

use std::path::{Path, PathBuf};

use anyhow::{Context, Result, bail};
use clap::{Parser, ValueEnum};
use hakoniwa_core::legacy::{self, ImportOptions, IslandLayout};
use hakoniwa_core::{GameConfig, legacy_settings, storage};

#[derive(Parser)]
#[command(
    version,
    about = "Perl 版 Hakoniwa R.A. のデータを移植版の JSON に変換する"
)]
struct Args {
    /// Perl 版のデータディレクトリ (hakojima.dat があるところ)
    input: PathBuf,
    /// 出力先 (移植版の state.json)
    output: PathBuf,
    /// 島データの形式。auto なら hakojima.dat の行数から判定する
    #[arg(long, value_enum, default_value_t = Layout::Auto)]
    layout: Layout,
    /// Perl 版の設定 (hako-main.cgi)。読めた設定でサーバーの設定ファイルも書く
    #[arg(long)]
    settings: Option<PathBuf>,
    /// サーバーの設定ファイルの出力先 (--settings のとき。既定は出力先と同じ場所の hakoniwa.toml)
    #[arg(long)]
    config_out: Option<PathBuf>,
    /// 島の大きさ ($HislandSize)。--settings があればその値
    #[arg(long)]
    island_size: Option<usize>,
    /// コマンド入力限界数 ($HcommandMax)。--settings があればその値
    #[arg(long)]
    command_max: Option<usize>,
    /// ローカル掲示板行数 ($HlbbsMax)。--settings があればその値
    #[arg(long)]
    lbbs_max: Option<usize>,
    /// 止めていた間のターンを飛ばす。最終更新時刻を、ターンの区切りの位置を保ったまま
    /// いまに最も近い過去の時刻にする (付けなければ、サーバーは起動時に止めていた間の
    /// ターンをすべて処理する)
    #[arg(long)]
    skip_missed_turns: bool,
    /// 旧形式の掲示板ログを変換しない ($HlbbsOldToNew = 0 のとき)
    #[arg(long)]
    keep_old_lbbs: bool,
    /// 出力先がすでにあっても上書きする
    #[arg(long)]
    force: bool,
}

#[derive(Clone, Copy, ValueEnum)]
enum Layout {
    Auto,
    /// $HnewGame = 1 (怪獣出現数を hakojima.dat に保存)
    NewGame,
    /// $HnewGame = 0 (怪獣出現数を monslive.dat に保存)
    Monslive,
}

fn main() -> Result<()> {
    let args = Args::parse();
    if args.output.exists() && !args.force {
        bail!(
            "{} はすでにあります。上書きするなら --force を付けてください",
            args.output.display()
        );
    }
    let settings = match &args.settings {
        Some(path) => {
            let bytes =
                std::fs::read(path).with_context(|| format!("{} を読めません", path.display()))?;
            let (text, _, _) = encoding_rs::EUC_JP.decode(&bytes);
            let s = legacy_settings::parse(&text.replace("\r\n", "\n"));
            for w in &s.warnings {
                eprintln!("警告 (設定): {w}");
            }
            Some(s)
        }
        None => None,
    };
    let config = settings
        .as_ref()
        .map(|s| s.config.clone())
        .unwrap_or_default();
    let layout = match args.layout {
        Layout::Auto => match settings.as_ref().and_then(|s| s.new_game) {
            Some(true) => Some(IslandLayout::NewGame),
            Some(false) => Some(IslandLayout::MonsLive),
            None => None,
        },
        Layout::NewGame => Some(IslandLayout::NewGame),
        Layout::Monslive => Some(IslandLayout::MonsLive),
    };
    let opts = ImportOptions {
        layout,
        island_size: args.island_size.unwrap_or(config.island_size),
        command_max: args.command_max.unwrap_or(config.command_max),
        lbbs_max: args.lbbs_max.unwrap_or(config.lbbs.max),
        lbbs_old_to_new: !args.keep_old_lbbs
            && settings
                .as_ref()
                .and_then(|s| s.lbbs_old_to_new)
                .unwrap_or(true),
    };
    let import = legacy::import_dir(&args.input, &opts, &mut rand::thread_rng())
        .with_context(|| format!("{} を読み込めませんでした", args.input.display()))?;
    for w in &import.warnings {
        eprintln!("警告: {w}");
    }
    let mut state = import.state;
    if args.skip_missed_turns {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_secs() as i64)
            .unwrap_or(0);
        let before = state.world.last_time;
        state.world.last_time = skip_missed(before, now, config.unit_time);
        if state.world.last_time != before {
            eprintln!(
                "止めていた間のターン ({} ターン分) を飛ばしました",
                (state.world.last_time - before) / config.unit_time.max(1)
            );
        }
    }
    storage::save(&args.output, &state)?;
    if settings.is_some() {
        let out = args
            .config_out
            .clone()
            .unwrap_or_else(|| args.output.with_file_name("hakoniwa.toml"));
        if out.exists() && !args.force {
            bail!(
                "{} はすでにあります。上書きするなら --force を付けてください",
                out.display()
            );
        }
        write_server_config(&out, &args.output, &config)?;
        eprintln!("サーバーの設定ファイルを書きました -> {}", out.display());
    }

    let world = &state.world;
    eprintln!(
        "変換しました: ターン {}、島 {} 個、ターンログ {} 件 (形式: {:?}) -> {}",
        world.turn,
        world.islands.len(),
        state.logs.turns.len(),
        import.layout,
        args.output.display()
    );
    Ok(())
}

/// サーバーの設定ファイル (hakoniwa-server の --config に渡すもの)
fn write_server_config(out: &Path, state_path: &Path, game: &GameConfig) -> Result<()> {
    #[derive(serde::Serialize)]
    struct ServerConfig<'a> {
        bind: &'a str,
        state_path: &'a Path,
        tick_secs: u64,
        game: &'a GameConfig,
    }
    let text = toml::to_string(&ServerConfig {
        bind: "127.0.0.1:8080",
        state_path,
        tick_secs: 10,
        game,
    })?;
    let header = "# Perl 版の hako-main.cgi から hako-convert が作った設定。\n\
                  # パスワードが平文で入っているので、ファイルの権限に気をつけること。\n\n";
    std::fs::write(out, format!("{header}{text}"))
        .with_context(|| format!("{} に書けません", out.display()))?;
    Ok(())
}

/// 最終更新時刻 `last` を、ターンの区切りの位置を保ったまま `now` 以前で最も近い時刻にする
fn skip_missed(last: i64, now: i64, unit: i64) -> i64 {
    let unit = unit.max(1);
    if now <= last {
        return last;
    }
    last + (now - last) / unit * unit
}

#[cfg(test)]
mod tests {
    use super::{skip_missed, write_server_config};
    use hakoniwa_core::GameConfig;
    use hakoniwa_core::legacy_settings;

    /// Perl 版の設定から書いた設定ファイルを読み直すと、同じ設定になる
    #[test]
    fn server_config_round_trips() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../../hako-r-a_FE/hako-main.cgi");
        let bytes = std::fs::read(path).unwrap();
        let (text, _, _) = encoding_rs::EUC_JP.decode(&bytes);
        let mut config = legacy_settings::parse(&text.replace("\r\n", "\n")).config;
        config.unit_time = 3600;
        let dir = tempfile::tempdir().unwrap();
        let out = dir.path().join("hakoniwa.toml");
        write_server_config(&out, &dir.path().join("state.json"), &config).unwrap();
        #[derive(serde::Deserialize)]
        struct File {
            game: GameConfig,
        }
        let read: File = toml::from_str(&std::fs::read_to_string(&out).unwrap()).unwrap();
        assert_eq!(read.game, config);
    }

    #[test]
    fn skips_whole_turns_only() {
        assert_eq!(skip_missed(1000, 1000 + 3 * 600 + 59, 600), 1000 + 3 * 600);
        assert_eq!(skip_missed(1000, 1500, 600), 1000);
        assert_eq!(skip_missed(1000, 900, 600), 1000);
    }
}
