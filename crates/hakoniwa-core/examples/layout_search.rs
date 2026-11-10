//! 20×20 の島で、ターンを進めたあとの総合ポイントがいちばん高くなる配置を探す。
//!
//! - 配置: 地形と値の組 ([`PALETTE`]) を 1 マスずつ自由に置く (値はルール上の上限)。
//!   首都・島主の家は島に 1 つまで
//! - 評価: 島 1 つのゲームに置き、ターンを `--turns` 回進めたあとの総合ポイントを、
//!   乱数の種 `--seeds` 通りで平均する (災害・怪獣も起きる)。計画は入れない (放棄しない設定にする)
//! - 探索: 1 マスを別の地形に変えて良くなれば採る、を候補を並べて繰り返す (同じ種で比べる)
//!
//! ```sh
//! cargo run --release -p hakoniwa-core --example layout_search -- --evals 6000
//! cargo run --release -p hakoniwa-core --example layout_search -- --try 1    # 手で組んだ配置を比べる
//! cargo run --release -p hakoniwa-core --example layout_search -- --sweep 1  # 海都市 + 食物研究所・総合大学の数を振る
//! PROBE="海都市 + 食物研究所 8・総合大学 16" cargo run --release -p hakoniwa-core --example layout_search -- --probe 1
//! ```
//!
//! 調べた結果 (20×20、計画なし、災害あり): ほぼ全面を海都市にし、首都 1・食物研究所 2・総合大学 8〜32 を
//! 散らした配置がいちばん高い (30 ターン後 約 122 万、100 ターン後 約 94 万)。1 マスずつ変える探索は
//! 出発点に縛られて 71 万で行き詰まったので、結果は `--try` と `--sweep` で出した

use std::time::Instant;

use hakoniwa_core::GameConfig;
use hakoniwa_core::model::{GameState, Island, IslandMap, LandCell};
use hakoniwa_core::tables::LandKind as L;
use hakoniwa_core::turn::run_turn;
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};

const SIZE: usize = 20;
const N: usize = SIZE * SIZE;

/// 置ける地形と値 (名前は表示用)
const PALETTE: &[(L, i64, &str)] = &[
    (L::Sea, 0, "海"),
    (L::Plains, 0, "平地"),
    (L::Foodim, 500, "食物研究所500"),
    (L::Farm, 50, "農場50"),
    (L::Factory, 100, "工場100"),
    (L::College, 0, "大学0(農業)"),
    (L::College, 1, "大学1(工業)"),
    (L::College, 2, "大学2(総合)"),
    (L::Skycity, 3000, "空中都市3000"),
    (L::Umicity, 3000, "海都市3000"),
    (L::Bettown, 2000, "輝ける都市2000"),
    (L::Shuto, 4000, "首都4000"),
    (L::Bigtown, 500, "現代都市500"),
    (L::Newtown, 300, "ニュータウン300"),
    (L::Town, 200, "都市200"),
    (L::EneBo, 2000, "バイオ発電2000"),
    (L::EneAt, 1500, "原子力発電1500"),
    (L::Monument, 74, "記念碑74"),
    (L::Monument, 75, "記念碑75"),
    (L::Monument, 76, "記念碑76"),
    (L::Monument, 77, "記念碑77"),
    (L::Monument, 78, "記念碑78"),
    (L::Monument, 79, "記念碑79"),
    (L::Oil, 0, "海底油田"),
    (L::Gold, 200, "金山200"),
    (L::House, 1, "島主の家"),
];

/// 島に 1 つまでのもの
fn unique(i: u8) -> bool {
    matches!(PALETTE[i as usize].0, L::Shuto | L::House)
}

struct Args {
    evals: usize,
    turns: usize,
    seeds: u64,
    threads: usize,
    restarts: usize,
}

fn parse() -> Args {
    let mut a = Args {
        evals: 6000,
        turns: 30,
        seeds: 3,
        threads: std::thread::available_parallelism().map_or(4, |n| n.get()),
        restarts: 1,
    };
    let mut it = std::env::args().skip(1);
    while let Some(k) = it.next() {
        if k == "--try" || k == "--probe" || k == "--sweep" {
            it.next();
            continue;
        }
        let v: usize = it.next().expect("値").parse().expect("数");
        match k.as_str() {
            "--evals" => a.evals = v,
            "--turns" => a.turns = v,
            "--seeds" => a.seeds = v as u64,
            "--threads" => a.threads = v,
            "--restarts" => a.restarts = v,
            _ => panic!("知らない引数 {k}"),
        }
    }
    a
}

fn config() -> GameConfig {
    GameConfig {
        island_size: SIZE,
        // 計画を入れないので、放棄されないようにする
        giveup_turn: i64::MAX / 4,
        ..GameConfig::default()
    }
}

/// 配置を置いてターンを進め、総合ポイントを返す
fn run(layout: &[u8; N], config: &GameConfig, turns: usize, seed: u64) -> i64 {
    let mut game = GameState::new_game(1_000_000_000, config);
    let mut island = Island::blank(1, "最適", config);
    island.money = config.initial_money;
    island.food = config.initial_food;
    let mut map = IslandMap::new_sea(SIZE);
    for (i, &p) in layout.iter().enumerate() {
        let (kind, value, _) = PALETTE[p as usize];
        map.cells_mut()[i] = LandCell {
            kind: kind as u8,
            value,
        };
    }
    island.map = map;
    game.world.islands.push(island);
    game.world.next_id = 2;
    let mut rng = StdRng::seed_from_u64(seed);
    for _ in 0..turns {
        run_turn(&mut game, config, &mut rng);
        if game.world.islands.is_empty() {
            return 0;
        }
    }
    game.world.islands[0].pts
}

fn eval(layout: &[u8; N], config: &GameConfig, turns: usize, seeds: u64) -> f64 {
    (0..seeds)
        .map(|s| run(layout, config, turns, 1000 + s) as f64)
        .sum::<f64>()
        / seeds as f64
}

fn idx(kind: L, value: i64) -> u8 {
    PALETTE
        .iter()
        .position(|&(k, v, _)| k == kind && v == value)
        .expect("palette") as u8
}

/// 手で考えた出発点: 空中都市を敷き詰め、食物研究所・発電所・大学を少し混ぜる
fn heuristic(rng: &mut StdRng) -> [u8; N] {
    let mut l = [idx(L::Skycity, 3000); N];
    for cell in l.iter_mut() {
        let r: f64 = rng.r#gen();
        *cell = if r < 0.08 {
            idx(L::Foodim, 500)
        } else if r < 0.30 {
            idx(L::EneBo, 2000)
        } else if r < 0.34 {
            idx(L::College, 2)
        } else {
            idx(L::Skycity, 3000)
        };
    }
    l[0] = idx(L::Shuto, 4000);
    l
}

fn show(layout: &[u8; N]) {
    let mut legend: Vec<(u8, usize)> = Vec::new();
    for &p in layout {
        match legend.iter_mut().find(|(q, _)| *q == p) {
            Some(e) => e.1 += 1,
            None => legend.push((p, 1)),
        }
    }
    legend.sort_by_key(|e| std::cmp::Reverse(e.1));
    let sym = |p: u8| -> char {
        let i = legend.iter().position(|(q, _)| *q == p).unwrap();
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i] as char
    };
    for y in 0..SIZE {
        let row: String = (0..SIZE).map(|x| sym(layout[y * SIZE + x])).collect();
        println!("  {}{row}", if y % 2 == 1 { " " } else { "" });
    }
    for (p, n) in &legend {
        println!("  {} {:<16} {n:>3} マス", sym(*p), PALETTE[*p as usize].2);
    }
}

/// 仮説を確かめるための、手で組んだ配置 (`--try 1` で評価だけする)
fn designed() -> Vec<(&'static str, [u8; N])> {
    let sky = idx(L::Skycity, 3000);
    let base = |extra: &[(usize, u8)]| {
        let mut l = [sky; N];
        l[0] = idx(L::Shuto, 4000);
        for &(i, p) in extra {
            l[i] = p;
        }
        l
    };
    let fi = idx(L::Foodim, 500);
    let c2 = idx(L::College, 2);
    let c0 = idx(L::College, 0);
    let bo = idx(L::EneBo, 2000);
    // 島じゅうに散らす位置 (i * 37 % 400)
    let spread = |n: usize, p: u8, off: usize| -> Vec<(usize, u8)> {
        (0..n).map(|i| ((off + i * 37) % N, p)).collect()
    };
    let umi = idx(L::Umicity, 3000);
    // 空中都市の代わりに海都市 (面積に数えない) を敷く
    let sea_base = |extra: &[(usize, u8)]| {
        let mut l = [umi; N];
        l[0] = idx(L::Shuto, 4000);
        for &(i, p) in extra {
            l[i] = p;
        }
        l
    };
    let mut out = Vec::new();
    // 失業者を出さない (暴動を起こさない): 海都市 3000 人に仕事 1000、食物研究所 1 マスで仕事 5000
    let riot_free = |n_f: usize, n_c: usize| {
        let mut l = [umi; N];
        // 食物研究所を均等に散らす
        for i in 0..n_f {
            l[(i * N) / n_f] = fi;
        }
        for i in 0..n_c {
            l[(i * N / n_c.max(1) + 3) % N] = c2;
        }
        l[1] = idx(L::Shuto, 4000);
        l
    };
    out.push(("海都市 + 食物研究所 100 (失業なし近く)", riot_free(100, 0)));
    out.push(("海都市 + 食物研究所 115 (失業なし)", riot_free(115, 0)));
    out.push(("海都市 + 食物研究所 125", riot_free(125, 0)));
    out.push(("海都市 + 食物研究所 115・総合大学 4", riot_free(115, 4)));
    out.push((
        "海都市 + 食物研究所 8・総合大学 8",
        sea_base(&[spread(8, fi, 210), spread(8, c2, 50)].concat()),
    ));
    out.push((
        "海都市 + 食物研究所 40・総合大学 8",
        sea_base(&[spread(40, fi, 210), spread(8, c2, 50)].concat()),
    ));
    out.push((
        "海都市 + 食物研究所 8・総合大学 16",
        sea_base(&[spread(8, fi, 210), spread(16, c2, 50)].concat()),
    ));
    out.push((
        "空中都市 + 海都市 60 + 食物研究所 8・総合大学 8",
        base(&[spread(8, fi, 210), spread(8, c2, 50), spread(60, umi, 7)].concat()),
    ));
    out.push(("空中都市 + 首都だけ", base(&[])));
    out.push(("+ 食物研究所 1", base(&[(210, fi)])));
    out.push((
        "+ 食物研究所 1・総合大学 4",
        base(&[spread(1, fi, 210), spread(4, c2, 50)].concat()),
    ));
    out.push((
        "+ 食物研究所 4・総合大学 4",
        base(&[spread(4, fi, 210), spread(4, c2, 50)].concat()),
    ));
    out.push((
        "+ 食物研究所 8・総合大学 8",
        base(&[spread(8, fi, 210), spread(8, c2, 50)].concat()),
    ));
    out.push((
        "+ 食物研究所 8・総合大学 8・農業大学 8",
        base(&[spread(8, fi, 210), spread(8, c2, 50), spread(8, c0, 90)].concat()),
    ));
    out.push((
        "+ 食物研究所 16・総合大学 16",
        base(&[spread(16, fi, 210), spread(16, c2, 50)].concat()),
    ));
    out.push((
        "+ 食物研究所 8・総合大学 8・バイオ発電 40",
        base(&[spread(8, fi, 210), spread(8, c2, 50), spread(40, bo, 130)].concat()),
    ));
    out
}

fn main() {
    let a = parse();
    if std::env::args().any(|x| x == "--probe") {
        // いちばん良かった手組みの配置を 60 ターン進め、何が起きたかと地形の移り変わりを見る
        let config = config();
        let pick = std::env::var("PROBE").unwrap_or_else(|_| "+ 食物研究所 8・総合大学 8".into());
        let (_, l) = designed()
            .into_iter()
            .find(|(n, _)| *n == pick)
            .expect("配置の名前");
        for seed in [9000u64, 9003] {
            let mut game = GameState::new_game(1_000_000_000, &config);
            let mut island = Island::blank(1, "最適", &config);
            island.money = config.initial_money;
            island.food = config.initial_food;
            let mut map = IslandMap::new_sea(SIZE);
            for (i, &p) in l.iter().enumerate() {
                let (kind, value, _) = PALETTE[p as usize];
                map.cells_mut()[i] = LandCell {
                    kind: kind as u8,
                    value,
                };
            }
            island.map = map;
            game.world.islands.push(island);
            let mut rng = StdRng::seed_from_u64(seed);
            let mut kinds = std::collections::BTreeMap::<String, usize>::new();
            for t in 1..=60 {
                run_turn(&mut game, &config, &mut rng);
                if game.world.islands.is_empty() {
                    println!("種 {seed}: ターン {t} で島が無くなった");
                    break;
                }
                for e in game.logs.turns[0].entries() {
                    let mut key = String::new();
                    let mut tag = false;
                    for c in e.message.chars() {
                        match c {
                            '<' => tag = true,
                            '>' => tag = false,
                            _ if tag => {}
                            c if c.is_ascii_digit() => {}
                            c => key.push(c),
                        }
                    }
                    let key = key.replace("最適島", "").replace("(, )", "");
                    *kinds.entry(key.chars().take(40).collect()).or_default() += 1;
                }
                if t % 20 == 0 {
                    let i = &game.world.islands[0];
                    let sky = i
                        .map
                        .cells
                        .iter()
                        .filter(|c| c.kind == L::Skycity as u8)
                        .count();
                    println!(
                        "種 {seed} ターン {t}: 点 {} 人口 {} 食料 {} 空中都市 {sky} マス",
                        i.pts, i.pop, i.food
                    );
                }
            }
            let mut v: Vec<_> = kinds.into_iter().collect();
            v.sort_by_key(|e| std::cmp::Reverse(e.1));
            for (k, n) in v.iter().take(12) {
                println!("    {n:>5} {k}");
            }
        }
        return;
    }
    if std::env::args().any(|x| x == "--sweep") {
        // 海都市を敷き、首都 1、食物研究所 nf、総合大学 nc を均等に散らす
        let config = config();
        let umi = idx(L::Umicity, 3000);
        let (fi, c2) = (idx(L::Foodim, 500), idx(L::College, 2));
        println!("食物研究所 総合大学   30ターン   60ターン  100ターン (種 16 通りの平均)");
        for nf in [2usize, 4, 8, 12] {
            for nc in [4usize, 8, 16, 24, 32, 48] {
                let mut l = [umi; N];
                for i in 0..nf {
                    l[(i * N / nf + 7) % N] = fi;
                }
                for i in 0..nc {
                    l[(i * N / nc + 3) % N] = c2;
                }
                l[1] = idx(L::Shuto, 4000);
                let mean = |turns| {
                    let v: Vec<i64> = (0..16).map(|s| run(&l, &config, turns, 9000 + s)).collect();
                    v.iter().sum::<i64>() as f64 / 16.0
                };
                println!(
                    "{nf:>10} {nc:>8} {:>10.0} {:>10.0} {:>10.0}",
                    mean(30),
                    mean(60),
                    mean(100)
                );
            }
        }
        return;
    }
    if std::env::args().any(|x| x == "--try") {
        let config = config();
        for (name, l) in designed() {
            for turns in [30, 100, 200] {
                let scores: Vec<i64> = (0..16).map(|s| run(&l, &config, turns, 9000 + s)).collect();
                let mean = scores.iter().sum::<i64>() as f64 / 16.0;
                println!(
                    "{name:<40} {turns:>3} ターン: 平均 {mean:>8.0} 最小 {:>8} 最大 {:>8}",
                    scores.iter().min().unwrap(),
                    scores.iter().max().unwrap()
                );
            }
        }
        return;
    }
    let config = config();
    let mut rng = StdRng::seed_from_u64(42);
    let started = Instant::now();
    let mut overall: Option<([u8; N], f64)> = None;
    for r in 0..a.restarts {
        let mut cur = heuristic(&mut rng);
        let mut cur_score = eval(&cur, &config, a.turns, a.seeds);
        println!("出発点 {r}: {cur_score:.0}");
        let mut done = 0;
        let mut last_print = Instant::now();
        while done < a.evals {
            // 候補を threads 個作り、並べて評価する
            let cands: Vec<[u8; N]> = (0..a.threads)
                .map(|_| {
                    let mut c = cur;
                    let changes = if rng.gen_bool(0.2) { 2 } else { 1 };
                    for _ in 0..changes {
                        let i = rng.gen_range(0..N);
                        let p = rng.gen_range(0..PALETTE.len()) as u8;
                        if unique(p) && c.contains(&p) {
                            continue;
                        }
                        c[i] = p;
                    }
                    c
                })
                .collect();
            let scores: Vec<f64> = std::thread::scope(|s| {
                let hs: Vec<_> = cands
                    .iter()
                    .map(|c| {
                        let config = &config;
                        s.spawn(move || eval(c, config, a.turns, a.seeds))
                    })
                    .collect();
                hs.into_iter().map(|h| h.join().unwrap()).collect()
            });
            done += cands.len();
            let (bi, bs) = scores
                .iter()
                .copied()
                .enumerate()
                .max_by(|x, y| x.1.total_cmp(&y.1))
                .unwrap();
            if bs >= cur_score {
                cur = cands[bi];
                cur_score = bs;
            }
            if last_print.elapsed().as_secs() >= 20 {
                println!(
                    "  {done:>6} 回評価 ({:.0} 秒): {cur_score:.0}",
                    started.elapsed().as_secs_f64()
                );
                last_print = Instant::now();
            }
        }
        println!("出発点 {r} の結果: {cur_score:.0}");
        if overall.as_ref().is_none_or(|(_, s)| cur_score > *s) {
            overall = Some((cur, cur_score));
        }
    }
    let (best, _) = overall.unwrap();
    // 探索に使わなかった種と、長いターン数で確かめる
    for turns in [a.turns, 60, 100] {
        let scores: Vec<i64> = (0..8)
            .map(|s| run(&best, &config, turns, 9000 + s))
            .collect();
        let mean = scores.iter().sum::<i64>() as f64 / 8.0;
        println!(
            "確認 {turns} ターン (種 8 通り): 平均 {mean:.0}、最小 {}、最大 {}",
            scores.iter().min().unwrap(),
            scores.iter().max().unwrap()
        );
    }
    show(&best);
    println!("{:.0} 秒", started.elapsed().as_secs_f64());
}
