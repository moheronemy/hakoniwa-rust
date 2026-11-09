//! Perl 版 (Hakoniwa R.A.) のセーブデータを移植版の JSON に変換する。
//!
//! 使い方:
//!     hako-convert <Perl版の data ディレクトリ> <出力する state.json>

use std::path::PathBuf;

use anyhow::{Context, Result, bail};
use clap::{Parser, ValueEnum};
use hakoniwa_core::legacy::{self, ImportOptions, IslandLayout};
use hakoniwa_core::storage;

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
    /// 島の大きさ ($HislandSize)
    #[arg(long, default_value_t = 12)]
    island_size: usize,
    /// コマンド入力限界数 ($HcommandMax)
    #[arg(long, default_value_t = 40)]
    command_max: usize,
    /// ローカル掲示板行数 ($HlbbsMax)
    #[arg(long, default_value_t = 15)]
    lbbs_max: usize,
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
    let opts = ImportOptions {
        layout: match args.layout {
            Layout::Auto => None,
            Layout::NewGame => Some(IslandLayout::NewGame),
            Layout::Monslive => Some(IslandLayout::MonsLive),
        },
        island_size: args.island_size,
        command_max: args.command_max,
        lbbs_max: args.lbbs_max,
        lbbs_old_to_new: !args.keep_old_lbbs,
    };
    let import = legacy::import_dir(&args.input, &opts, &mut rand::thread_rng())
        .with_context(|| format!("{} を読み込めませんでした", args.input.display()))?;
    for w in &import.warnings {
        eprintln!("警告: {w}");
    }
    storage::save(&args.output, &import.state)?;

    let world = &import.state.world;
    eprintln!(
        "変換しました: ターン {}、島 {} 個、ターンログ {} 件 (形式: {:?}) -> {}",
        world.turn,
        world.islands.len(),
        import.state.logs.turns.len(),
        import.layout,
        args.output.display()
    );
    Ok(())
}
