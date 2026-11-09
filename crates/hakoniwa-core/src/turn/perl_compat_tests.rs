//! Perl 版との突き合わせテスト。
//!
//! `tests/fixtures/phase1-mix.rand*.expected.json` は、元の Perl コードを
//! `tools/perl-harness/run-phase1.sh` で実行して作ったもの。`rand()` の値を固定し
//! (0 と 0.5)、座標の並びは行優先にしてある。同じ条件で移植版を動かし、
//! `estimate` 2 回、`income`、計画の実行 (費用不足・資金繰り・自動放棄・放棄) の
//! 各段階で、島の値・一時値・地形の値・計画・ログがすべて一致することを確かめる。

use std::collections::HashMap;
use std::path::Path;

use rand::rngs::mock::StepRng;
use serde_json::Value;

use crate::config::GameConfig;
use crate::legacy::{self, ImportOptions};
use crate::log::TurnLog;
use crate::model::Island;

use super::{Globals, TurnContext, command::do_command, estimate::estimate, income::income};

fn fixture_dir() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures")
}

/// Perl 版の島のハッシュのキーに対応する、移植版の値 (文字列で比べる)
fn field(island: &Island, name: &str) -> String {
    let sc = &island.scratch;
    let n = |v: i64| v.to_string();
    match name {
        "id" => n(island.id),
        "pop" => n(island.pop),
        "area" => n(island.area),
        "farm" => n(island.farm),
        "factory" => island.factory.clone(),
        "mountain" => n(island.mountain),
        "pts" => n(island.pts),
        "money" => n(island.money),
        "food" => n(island.food),
        "etc0" => n(island.etc_num[0]),
        "eisei1" => n(island.eisei[0]),
        "eisei2" => n(island.eisei[1]),
        "eisei3" => island.eisei_raw[0].clone(),
        "eisei4" => island.eisei_raw[1].clone(),
        "eisei5" => island.eisei_raw[2].clone(),
        "eisei6" => island.eisei_raw[3].clone(),
        "etc5" => island.etc_raw[0].clone(),
        "etc6" => island.etc_raw[1].clone(),
        "etc8" => island.etc_raw[3].clone(),
        "etc9" => island.etc_raw[4].clone(),
        "totoyoso2" => island.totoyoso2.clone(),
        "kei" => n(island.owner_stats.kei),
        "rena" => n(island.owner_stats.rena),
        "fore" => n(island.owner_stats.fore),
        "tare" => n(island.owner_stats.tare),
        "zipro" => n(island.owner_stats.zipro),
        "leje" => n(island.owner_stats.leje),
        "monsterlive" => n(island.monster_live),
        "monsterlivetype" => n(island.monster_live_type),
        "anflag" => n(island.survey_flag),
        "auc0" => island.auction.auc0.clone(),
        "auc4" => island.auction.auc4.clone(),
        "auc5" => island.auction.auc5.clone(),
        "auc6" => island.auction.auc6.clone(),
        "auc9" => island.auction.auc9.clone(),
        "shouhi" => n(sc.shouhi),
        "ene" => n(sc.ene),
        "sabun" => {
            if sc.sabun.fract() == 0.0 {
                n(sc.sabun as i64)
            } else {
                sc.sabun.to_string()
            }
        }
        "con99" => n(sc.con99),
        "factory1" => n(sc.factory1),
        "factory2" => n(sc.factory2),
        "factoryt" => n(sc.factoryt),
        "oil" => n(sc.oil),
        "bas" => n(sc.bas),
        "htf" => n(sc.htf),
        "shtf" => n(sc.shtf),
        "hou" => n(sc.hou),
        "shu" => n(sc.shu),
        "sin" => n(sc.sin),
        "jin" => n(sc.jin),
        "h10" => n(sc.h10),
        "h11" => n(sc.h11),
        "co0" => n(sc.co0),
        "co1" => n(sc.co1),
        "co4" => n(sc.co4),
        "co7" => n(sc.co7),
        "co8" => n(sc.co8),
        "co77" => n(sc.co77),
        "co99" => n(sc.co99),
        "c13" => n(sc.c13),
        "c28" => n(sc.c28),
        "tet" => n(sc.tet),
        "m26" => n(sc.m26),
        "m27" => n(sc.m27),
        "m74" => n(sc.m74),
        "m75" => n(sc.m75),
        "m79" => n(sc.m79),
        "m84" => n(sc.m84),
        "m93" => n(sc.m93),
        "kyu" => n(sc.kyu),
        "ky2" => n(sc.ky2),
        "zoo" => n(sc.zoo),
        "sci" => n(sc.sci),
        "pro" => n(sc.pro),
        "sba" => n(sc.sba),
        "amu" => n(sc.amu),
        "kin" => n(sc.kin),
        "tra" => n(sc.tra),
        "tra1" => n(sc.tra1),
        "tra2" => n(sc.tra2),
        "fukeikimoney" => n(sc.fukeikimoney),
        "unemployed" => n(sc.unemployed),
        "monsterlive2" => n(sc.monsterlive2),
        "kachiten" => n(sc.kachiten),
        "kachitent" => n(sc.kachitent),
        "shoritu" => n(sc.shoritu),
        "styusho" => n(sc.styusho),
        "teamforce" => n(sc.teamforce),
        "force" => n(sc.force),
        "uni" => n(sc.uni),
        "tuni" => n(sc.tuni),
        "auc0c" => n(sc.auc0c),
        "auc5c" => n(sc.auc5c),
        "ownfe" => n(sc.ownfe),
        "absent" => n(island.absent),
        "incomemoney" => n(sc.incomemoney),
        "dead" => {
            if sc.dead {
                "1".into()
            } else {
                String::new()
            }
        }
        other => panic!("unknown field {other}"),
    }
}

/// Perl 版は未定義 (一度も代入されていない) の値を空文字列で出力する。
/// 移植版は 0 なので、空文字列は "0" とみなして比べる
fn normalize(v: &str) -> &str {
    if v.is_empty() { "0" } else { v }
}

#[test]
fn phase1_matches_perl_with_rand_0() {
    check_phase1("phase1-mix.rand0.expected.json", 0);
}

#[test]
fn phase1_matches_perl_with_rand_half() {
    // rand 0.8 の f64 は上位 53 ビットから作るので、1 << 63 で 0.5 になる
    check_phase1("phase1-mix.rand50.expected.json", 1 << 63);
}

fn check_phase1(expected_file: &str, rng_value: u64) {
    let config = GameConfig::default();
    let import = legacy::import_dir(
        &fixture_dir().join("phase1-mix"),
        &ImportOptions::default(),
        &mut StepRng::new(0, 0),
    )
    .unwrap();
    let mut islands = import.state.world.islands;
    let expected: Vec<Value> =
        serde_json::from_str(&std::fs::read_to_string(fixture_dir().join(expected_file)).unwrap())
            .unwrap();

    let mut rng = StepRng::new(rng_value, 0);
    let size = config.island_size;
    let mut ctx = TurnContext {
        config: &config,
        rng: &mut rng,
        turn: import.state.world.turn,
        log: TurnLog::default(),
        points: (0..size * size).map(|i| (i % size, i / size)).collect(),
        id_to_number: islands
            .iter()
            .enumerate()
            .map(|(i, island)| (island.id, i))
            .collect::<HashMap<_, _>>(),
        island_number: islands.len(),
        globals: Globals::default(),
        oyasumiritu: 0,
    };

    let mut mismatches = Vec::new();
    let mut compared = 0;
    for (pass, exp) in expected.iter().enumerate() {
        match exp["name"].as_str().unwrap() {
            "estimate1" | "estimate2" => {
                for i in 0..islands.len() {
                    estimate(&mut ctx, &mut islands, i);
                }
            }
            "income" => {
                for island in islands.iter_mut() {
                    income(&mut ctx, island);
                }
            }
            "commands" => {
                for i in 0..islands.len() {
                    while !do_command(&mut ctx, &mut islands, i) {}
                }
            }
            other => panic!("unknown pass {other}"),
        }
        let exp_islands = exp["islands"].as_array().unwrap();
        for (island, exp_island) in islands.iter().zip(exp_islands) {
            for (key, value) in exp_island.as_object().unwrap() {
                if key == "commands" {
                    let got: Vec<String> =
                        island.commands.iter().map(|c| c.kind.to_string()).collect();
                    let want: Vec<&str> = value
                        .as_array()
                        .unwrap()
                        .iter()
                        .map(|v| v.as_str().unwrap())
                        .collect();
                    if got != want {
                        mismatches.push(format!(
                            "pass {} island {} commands: rust {got:?} perl {want:?}",
                            pass + 1,
                            island.id
                        ));
                    }
                    continue;
                }
                if key == "land_values" {
                    let got: Vec<String> = island
                        .map
                        .cells
                        .iter()
                        .map(|c| c.value.to_string())
                        .collect();
                    let want: Vec<&str> = value
                        .as_array()
                        .unwrap()
                        .iter()
                        .map(|v| normalize(v.as_str().unwrap()))
                        .collect();
                    for (idx, (g, w)) in got.iter().zip(&want).enumerate() {
                        if g != w {
                            mismatches.push(format!(
                                "pass {} island {} land ({}, {}): rust {g} perl {w}",
                                pass + 1,
                                island.id,
                                idx % size,
                                idx / size
                            ));
                        }
                    }
                    continue;
                }
                compared += 1;
                let want = normalize(value.as_str().unwrap());
                let got = field(island, key);
                if normalize(&got) != want {
                    mismatches.push(format!(
                        "pass {} island {} {key}: rust {got:?} perl {want:?}",
                        pass + 1,
                        island.id
                    ));
                }
            }
        }
        if let Some(want_logs) = exp.get("logs") {
            let (entries, history) = std::mem::take(&mut ctx.log).flush();
            let got: Vec<String> = entries
                .iter()
                .map(|e| {
                    let id = |v: Option<i64>| v.map(|v| v.to_string()).unwrap_or_default();
                    format!(
                        "{},{},{},{},{}",
                        u8::from(e.secret),
                        e.turn,
                        id(e.island1),
                        id(e.island2),
                        e.message
                    )
                })
                .collect();
            let want: Vec<&str> = want_logs
                .as_array()
                .unwrap()
                .iter()
                .map(|v| v.as_str().unwrap())
                .collect();
            if got != want {
                mismatches.push(format!("logs:\n  rust {got:#?}\n  perl {want:#?}"));
            }
            let got: Vec<String> = history
                .iter()
                .map(|h| format!("{},{}", h.turn, h.message))
                .collect();
            let want: Vec<&str> = exp["history"]
                .as_array()
                .unwrap()
                .iter()
                .map(|v| v.as_str().unwrap())
                .collect();
            if got != want {
                mismatches.push(format!("history: rust {got:?} perl {want:?}"));
            }
        }
        let want = normalize(exp["oyasumiritu"].as_str().unwrap());
        if ctx.oyasumiritu.to_string() != want {
            mismatches.push(format!(
                "pass {} oyasumiritu: rust {} perl {want}",
                pass + 1,
                ctx.oyasumiritu
            ));
        }
    }
    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n")
    );
    // 島 3 つ × 4 段階 × 約 100 項目を比べたはず
    assert!(compared > 500, "only {compared} values compared");
}
