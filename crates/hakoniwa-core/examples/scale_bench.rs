//! 大規模化の負荷テスト (docs/SCALING.md)。
//!
//! 突き合わせ用のデータ (`tests/fixtures/<名前>/`) の島を `--islands` の数まで複製し、
//! ターン処理 (`run_turn`) を `--turns` 回行って、1 ターンの時間・ログの件数・状態の複製と
//! JSON の書き出しの時間を出す。`--max-turn-secs` を超えたターンがあれば失敗 (終了コード 1) にする。
//!
//! ```sh
//! cargo run --release -p hakoniwa-core --example scale_bench -- \
//!     --fixture size-128-1 --islands 1000 --turns 3 --max-turn-secs 10
//! ```
//!
//! `--save PATH` を付けると、複製して作った (ターンを進める前の) 状態を `state.json` の形で保存する
//! (サーバーを目標の規模で動かして確かめるため)。
//!
//! `size-128-1` は 128×128 の 3/4 が陸 (全地形をばらまいたもの) で、最悪の場合に近い。
//! `size-128-2` は 6 割が海。12×12 なら `phase4-mix-1` など。

use std::path::Path;
use std::process::ExitCode;
use std::time::Instant;

use hakoniwa_core::GameConfig;
use hakoniwa_core::legacy::{self, ImportOptions};
use hakoniwa_core::turn::run_turn;
use rand::SeedableRng;
use rand::rngs::StdRng;

struct Args {
    fixture: String,
    islands: usize,
    turns: usize,
    max_turn_secs: Option<f64>,
    save: Option<std::path::PathBuf>,
}

fn parse_args() -> Result<Args, String> {
    let mut args = Args {
        fixture: "size-128-1".into(),
        islands: 1000,
        turns: 3,
        max_turn_secs: None,
        save: None,
    };
    let mut it = std::env::args().skip(1);
    while let Some(a) = it.next() {
        let mut value = || it.next().ok_or(format!("{a} の値がありません"));
        match a.as_str() {
            "--fixture" => args.fixture = value()?,
            "--islands" => args.islands = value()?.parse().map_err(|e| format!("{a}: {e}"))?,
            "--turns" => args.turns = value()?.parse().map_err(|e| format!("{a}: {e}"))?,
            "--max-turn-secs" => {
                args.max_turn_secs = Some(value()?.parse().map_err(|e| format!("{a}: {e}"))?)
            }
            "--save" => args.save = Some(value()?.into()),
            _ => return Err(format!("知らない引数 {a}")),
        }
    }
    Ok(args)
}

fn main() -> ExitCode {
    let args = match parse_args() {
        Ok(a) => a,
        Err(e) => {
            eprintln!("{e}");
            return ExitCode::from(2);
        }
    };
    let dir = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures")
        .join(&args.fixture);
    let size = std::fs::read_to_string(dir.join("island_size"))
        .map(|s| s.trim().parse().expect("island_size"))
        .unwrap_or(GameConfig::default().island_size);
    let opts = ImportOptions {
        island_size: size,
        ..ImportOptions::default()
    };
    let mut game = legacy::import_dir(&dir, &opts, &mut StdRng::seed_from_u64(0))
        .expect("データを読み込めません")
        .state;

    // 島を複製して数をそろえる (ID と名前だけ変える)
    let base = std::mem::take(&mut game.world.islands);
    for i in 0..args.islands {
        let mut island = base[i % base.len()].clone();
        island.id = i as i64 + 1;
        island.name = format!("負荷{}", i + 1);
        game.world.islands.push(island);
    }
    game.world.next_id = args.islands as i64 + 1;
    let config = GameConfig {
        island_size: size,
        max_islands: args.islands.max(GameConfig::default().max_islands),
        ..GameConfig::default()
    };
    println!(
        "{}: {} 島 × {size}×{size} ({} マス)",
        args.fixture,
        args.islands,
        args.islands * size * size
    );

    if let Some(path) = &args.save {
        hakoniwa_core::storage::save(path, &game).expect("保存できません");
        println!("{} に保存しました", path.display());
    }

    let mut rng = StdRng::seed_from_u64(1);
    let mut worst: f64 = 0.0;
    for _ in 0..args.turns {
        let t = Instant::now();
        let report = run_turn(&mut game, &config, &mut rng);
        let secs = t.elapsed().as_secs_f64();
        worst = worst.max(secs);
        let logs = game.logs.turns.first().map_or(0, |t| t.len());
        println!(
            "ターン {:>4}: {secs:>7.3} 秒  ログ {logs} 件  残った島 {}",
            report.turn,
            game.world.islands.len()
        );
    }

    let t = Instant::now();
    let copy = game.clone();
    let clone_secs = t.elapsed().as_secs_f64();
    drop(copy);
    let t = Instant::now();
    let json = serde_json::to_vec(&game).expect("JSON");
    let json_secs = t.elapsed().as_secs_f64();
    println!("状態の複製 {clone_secs:.3} 秒");
    println!(
        "JSON {:.1} MB を {json_secs:.3} 秒で書き出し",
        json.len() as f64 / 1e6
    );

    let packed: usize = game.logs.turns.iter().map(|t| t.packed_bytes()).sum();
    println!(
        "ターンのログ {} ターン分 (圧縮後 {:.1} MB)",
        game.logs.turns.len(),
        packed as f64 / 1e6
    );
    // いちばん多く使ったメモリ (Linux のみ)
    if let Some(line) = std::fs::read_to_string("/proc/self/status")
        .ok()
        .and_then(|s| {
            s.lines()
                .find(|l| l.starts_with("VmHWM"))
                .map(str::to_string)
        })
    {
        println!("{}", line.split_whitespace().collect::<Vec<_>>().join(" "));
    }

    match args.max_turn_secs {
        Some(limit) if worst > limit => {
            println!("失敗: いちばん遅いターン {worst:.3} 秒 > 上限 {limit} 秒");
            ExitCode::FAILURE
        }
        Some(limit) => {
            println!("成功: いちばん遅いターン {worst:.3} 秒 <= 上限 {limit} 秒");
            ExitCode::SUCCESS
        }
        None => ExitCode::SUCCESS,
    }
}
