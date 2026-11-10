//! Perl 版との突き合わせテスト。
//!
//! `tests/fixtures/<名前>.rand*.expected.json` は、元の Perl コードを
//! `tools/perl-harness/run-harness.sh` で実行して作ったもの。`rand()` の値を固定し
//! (0 と 0.5)、座標の並びは行優先にしてある。同じ条件で移植版を同じ段階
//! (`estimate`, `income`, `commands`, `eachhex`) の順に動かし、各段階のあとで
//! 島の値・一時値・地形の値・計画・ログがすべて一致することを確かめる。
//!
//! 新しい突き合わせを足すには、Perl 形式のデータを `tests/fixtures/<名前>/` に置き、
//! `run-harness.sh <名前> <段階>` で期待値を作り、ここに `#[test]` を 1 つ足す。

use std::collections::HashMap;
use std::path::Path;

use rand::rngs::mock::StepRng;
use serde_json::Value;

use crate::config::GameConfig;
use crate::legacy::{self, ImportOptions};
use crate::log::TurnLog;
use crate::model::Island;

use super::{
    Globals, TurnContext, command::do_command, estimate::estimate, hex::do_each_hex, income::income,
};

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
        "prize" => island.prize.clone(),
        "taiji" => n(island.taiji),
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
    check_fixture("phase1-mix", 0);
}

#[test]
fn phase1_matches_perl_with_rand_half() {
    check_fixture("phase1-mix", RAND_HALF);
}

/// rand 0.8 の f64 は上位 53 ビットから作るので、1 << 63 で 0.5 になる
pub(crate) const RAND_HALF: u64 = 1 << 63;

/// `fixture` を Perl 版の期待値と突き合わせる。`rng_value` は 0 か [`RAND_HALF`]
pub(crate) fn check_fixture(fixture: &str, rng_value: u64) {
    let config = GameConfig::default();
    let import = legacy::import_dir(
        &fixture_dir().join(fixture),
        &ImportOptions::default(),
        &mut StepRng::new(0, 0),
    )
    .unwrap();
    let mut islands = import.state.world.islands;
    let expected_file = format!(
        "{fixture}.rand{}.expected.json",
        if rng_value == 0 { "0" } else { "50" }
    );
    let expected: Vec<Value> = serde_json::from_str(
        &std::fs::read_to_string(fixture_dir().join(&expected_file))
            .unwrap_or_else(|e| panic!("{expected_file}: {e}")),
    )
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
    for exp in &expected {
        let step = exp["name"].as_str().unwrap();
        for i in 0..islands.len() {
            match step {
                "estimate" => estimate(&mut ctx, &mut islands, i),
                "income" => income(&mut ctx, &mut islands[i]),
                "commands" => while !do_command(&mut ctx, &mut islands, i) {},
                "eachhex" => do_each_hex(&mut ctx, &mut islands, i),
                other => panic!("unknown step {other}"),
            }
        }
        let at = |island: &Island, what: &str| format!("{step}: island {} {what}", island.id);
        let exp_islands = exp["islands"].as_array().unwrap();
        assert_eq!(exp_islands.len(), islands.len());
        for (island, exp_island) in islands.iter().zip(exp_islands) {
            for (key, value) in exp_island.as_object().unwrap() {
                compared += 1;
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
                        mismatches.push(format!("{}: rust {got:?} perl {want:?}", at(island, key)));
                    }
                    continue;
                }
                if key == "land_kinds" {
                    let want = value.as_array().unwrap();
                    for (idx, (cell, w)) in island.map.cells.iter().zip(want).enumerate() {
                        let w = normalize(w.as_str().unwrap());
                        let got = cell.kind.to_string();
                        if got != w {
                            let (x, y) = (idx % size, idx / size);
                            mismatches.push(format!(
                                "{}: rust {got} perl {w}",
                                at(island, &format!("land kind ({x}, {y})"))
                            ));
                        }
                    }
                    continue;
                }
                if key == "land_values" {
                    let want = value.as_array().unwrap();
                    for (idx, (cell, w)) in island.map.cells.iter().zip(want).enumerate() {
                        let w = normalize(w.as_str().unwrap());
                        let (x, y) = (idx % size, idx / size);
                        let frac = island
                            .scratch
                            .land_frac
                            .get(&(x, y))
                            .copied()
                            .unwrap_or(0.0);
                        let got = if frac == 0.0 {
                            cell.value.to_string()
                        } else {
                            (cell.value as f64 + frac).to_string()
                        };
                        if got != w {
                            mismatches.push(format!(
                                "{}: rust {got} perl {w}",
                                at(island, &format!("land ({x}, {y})"))
                            ));
                        }
                    }
                    continue;
                }
                let want = normalize(value.as_str().unwrap());
                let got = field(island, key);
                if normalize(&got) != want {
                    mismatches.push(format!("{}: rust {got:?} perl {want:?}", at(island, key)));
                }
            }
        }

        let (entries, history) = ctx.log.snapshot();
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
        let want: Vec<&str> = exp["logs"]
            .as_array()
            .unwrap()
            .iter()
            .map(|v| v.as_str().unwrap())
            .collect();
        if got != want {
            let first = got.iter().zip(&want).position(|(g, w)| g != w);
            mismatches.push(format!(
                "{step}: logs differ (rust {} lines, perl {} lines, first difference at {first:?})\n  rust {got:#?}\n  perl {want:#?}",
                got.len(),
                want.len()
            ));
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
            mismatches.push(format!("{step}: history: rust {got:?} perl {want:?}"));
        }

        let want = normalize(exp["oyasumiritu"].as_str().unwrap());
        if ctx.oyasumiritu.to_string() != want {
            mismatches.push(format!(
                "{step}: oyasumiritu: rust {} perl {want}",
                ctx.oyasumiritu
            ));
        }
    }
    assert!(
        mismatches.is_empty(),
        "{expected_file}: {} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n")
    );
    assert!(compared > 100, "only {compared} values compared");
}

#[test]
fn phase2_town_matches_perl_with_rand_0() {
    check_fixture("phase2-town", 0);
}

#[test]
fn phase2_town_matches_perl_with_rand_half() {
    check_fixture("phase2-town", RAND_HALF);
}

#[test]
fn phase2_monster_matches_perl_with_rand_0() {
    check_fixture("phase2-monster", 0);
}

#[test]
fn phase2_monster_matches_perl_with_rand_half() {
    check_fixture("phase2-monster", RAND_HALF);
}

#[test]
fn phase2_monster_even_matches_perl_with_rand_0() {
    check_fixture("phase2-monster-even", 0);
}

#[test]
fn phase2_monster_even_matches_perl_with_rand_half() {
    check_fixture("phase2-monster-even", RAND_HALF);
}

#[test]
fn phase2_monster_lords_matches_perl_with_rand_0() {
    check_fixture("phase2-monster-lords", 0);
}

#[test]
fn phase2_monster_lords_matches_perl_with_rand_half() {
    check_fixture("phase2-monster-lords", RAND_HALF);
}

#[test]
fn phase2_monster_mascot_matches_perl_with_rand_0() {
    check_fixture("phase2-monster-mascot", 0);
}

#[test]
fn phase2_monster_mascot_matches_perl_with_rand_half() {
    check_fixture("phase2-monster-mascot", RAND_HALF);
}

#[test]
fn phase2_monster_misc_matches_perl_with_rand_0() {
    check_fixture("phase2-monster-misc", 0);
}

#[test]
fn phase2_monster_misc_matches_perl_with_rand_half() {
    check_fixture("phase2-monster-misc", RAND_HALF);
}
