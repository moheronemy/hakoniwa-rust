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
        "eis5" => n(island.eis[4]),
        "etc7" => island.etc_raw[2].clone(),
        "monstersend" => n(sc.command.attack.monstersend),
        "monstersendkind" => n(sc.command.attack.monstersendkind),
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
        "trainmoney" => n(sc.trainmoney),
        "trainmoney2" => n(sc.trainmoney2),
        "hcsankaflag" => n(sc.hcsankaflag),
        "stsankahantei" => n(sc.hex.stadium.stsankahantei),
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
    check_fixture_at(fixture, if rng_value == 0 { "0" } else { "50" });
}

/// `rand()` を `0.<digits>` に固定した期待値 (`<fixture>.rand<digits>.expected.json`) と突き合わせる。
/// `0.<digits>` は 2 進で割り切れる数 (1/32 = 0.03125 など) にすること
pub(crate) fn check_fixture_at(fixture: &str, digits: &str) {
    let r: f64 = format!("0.{digits}").parse().unwrap();
    // rand 0.8 の f64 は u64 の上位 53 ビット × 2^-53
    let mantissa = r * (1u64 << 53) as f64;
    assert_eq!(mantissa.fract(), 0.0, "0.{digits} is not representable");
    let rng_value = (mantissa as u64) << 11;
    check_fixture_inner(
        fixture,
        rng_value,
        &format!("{fixture}.rand{digits}.expected.json"),
    );
}

fn check_fixture_inner(fixture: &str, rng_value: u64, expected_file: &str) {
    let config = GameConfig::default();
    let import = legacy::import_dir(
        &fixture_dir().join(fixture),
        &ImportOptions::default(),
        &mut StepRng::new(0, 0),
    )
    .unwrap();
    let mut islands = import.state.world.islands;
    let expected: Vec<Value> = serde_json::from_str(
        &std::fs::read_to_string(fixture_dir().join(expected_file))
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
                        if cell.kind.to_string() != w {
                            mismatches.push(format!(
                                "{}: rust {} perl {w}",
                                at(
                                    island,
                                    &format!("land kind ({}, {})", idx % size, idx / size)
                                ),
                                cell.kind
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
fn phase2_train_matches_perl_with_rand_0() {
    check_fixture("phase2-train", 0);
}

#[test]
fn phase2_train_matches_perl_with_rand_half() {
    check_fixture("phase2-train", RAND_HALF);
}

#[test]
fn phase2_sea_matches_perl_with_rand_0() {
    check_fixture("phase2-sea", 0);
}

#[test]
fn phase2_sea_matches_perl_with_rand_half() {
    check_fixture("phase2-sea", RAND_HALF);
}

#[test]
fn phase2_stadium_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium", 0);
}

#[test]
fn phase2_stadium_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium", RAND_HALF);
}

#[test]
fn phase2_stadium_reset_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium-reset", 0);
}

#[test]
fn phase2_stadium_reset_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium-reset", RAND_HALF);
}

#[test]
fn phase2_stadium_r2_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium-r2", 0);
}

#[test]
fn phase2_stadium_r2_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium-r2", RAND_HALF);
}

#[test]
fn phase2_stadium_r4_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium-r4", 0);
}

#[test]
fn phase2_stadium_r4_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium-r4", RAND_HALF);
}

#[test]
fn phase2_stadium_qf_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium-qf", 0);
}

#[test]
fn phase2_stadium_qf_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium-qf", RAND_HALF);
}

#[test]
fn phase2_stadium_sf_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium-sf", 0);
}

#[test]
fn phase2_stadium_sf_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium-sf", RAND_HALF);
}

#[test]
fn phase2_stadium_final_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium-final", 0);
}

#[test]
fn phase2_stadium_final_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium-final", RAND_HALF);
}

#[test]
fn phase2_stadium_end_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium-end", 0);
}

#[test]
fn phase2_stadium_end_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium-end", RAND_HALF);
}

#[test]
fn phase2_stadium_52_matches_perl_with_rand_0() {
    check_fixture("phase2-stadium-52", 0);
}

#[test]
fn phase2_stadium_52_matches_perl_with_rand_half() {
    check_fixture("phase2-stadium-52", RAND_HALF);
}

#[test]
fn phase2_leisure_matches_perl_with_rand_0() {
    check_fixture("phase2-leisure", 0);
}

#[test]
fn phase2_leisure_matches_perl_with_rand_half() {
    check_fixture("phase2-leisure", RAND_HALF);
}

#[test]
fn phase2_special_matches_perl_with_rand_0() {
    check_fixture("phase2-special", 0);
}

#[test]
fn phase2_special_matches_perl_with_rand_half() {
    check_fixture("phase2-special", RAND_HALF);
}

#[test]
fn phase2_special_egg_matches_perl_with_rand_0() {
    check_fixture("phase2-special-egg", 0);
    check_fixture("phase2-special-egg2", 0);
}

#[test]
fn phase2_special_egg_matches_perl_with_rand_half() {
    check_fixture("phase2-special-egg", RAND_HALF);
    check_fixture("phase2-special-egg2", RAND_HALF);
}

#[test]
fn phase2_special_mons_matches_perl_with_rand_0() {
    check_fixture("phase2-special-mons", 0);
    check_fixture("phase2-special-mons2", 0);
}

#[test]
fn phase2_special_mons_matches_perl_with_rand_half() {
    check_fixture("phase2-special-mons", RAND_HALF);
    check_fixture("phase2-special-mons2", RAND_HALF);
}

#[test]
fn phase2_industry_matches_perl_with_rand_0() {
    check_fixture("phase2-industry", 0);
}

#[test]
fn phase2_industry_matches_perl_with_rand_half() {
    check_fixture("phase2-industry", RAND_HALF);
}

#[test]
fn phase2_industry_t10_matches_perl_with_rand_0() {
    check_fixture("phase2-industry-t10", 0);
}

#[test]
fn phase2_industry_t10_matches_perl_with_rand_half() {
    check_fixture("phase2-industry-t10", RAND_HALF);
}

#[test]
fn phase2_city_matches_perl_with_rand_0() {
    check_fixture("phase2-city", 0);
}

#[test]
fn phase2_city_matches_perl_with_rand_half() {
    check_fixture("phase2-city", RAND_HALF);
}

#[test]
fn phase2_city2_matches_perl_with_rand_0() {
    check_fixture("phase2-city2", 0);
}

#[test]
fn phase2_city2_matches_perl_with_rand_half() {
    check_fixture("phase2-city2", RAND_HALF);
}

#[test]
fn phase2_city3_matches_perl_with_rand_0() {
    check_fixture("phase2-city3", 0);
}

#[test]
fn phase2_city3_matches_perl_with_rand_half() {
    check_fixture("phase2-city3", RAND_HALF);
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

#[test]
fn phase2_mix_1_matches_perl_with_rand_0() {
    check_fixture("phase2-mix-1", 0);
}

#[test]
fn phase2_mix_1_matches_perl_with_rand_half() {
    check_fixture("phase2-mix-1", RAND_HALF);
}

#[test]
fn phase2_mix_2_matches_perl_with_rand_0() {
    check_fixture("phase2-mix-2", 0);
}

#[test]
fn phase2_mix_2_matches_perl_with_rand_half() {
    check_fixture("phase2-mix-2", RAND_HALF);
}

#[test]
fn phase2_mix_3_matches_perl_with_rand_0() {
    check_fixture("phase2-mix-3", 0);
}

#[test]
fn phase2_mix_3_matches_perl_with_rand_half() {
    check_fixture("phase2-mix-3", RAND_HALF);
}

#[test]
fn phase2_mix_4_matches_perl_with_rand_0() {
    check_fixture("phase2-mix-4", 0);
}

#[test]
fn phase2_mix_4_matches_perl_with_rand_half() {
    check_fixture("phase2-mix-4", RAND_HALF);
}

#[test]
fn phase2_mix_1_matches_perl_with_rand_1_32() {
    check_fixture_at("phase2-mix-1", "03125");
}

#[test]
fn phase2_mix_1_matches_perl_with_rand_31_32() {
    check_fixture_at("phase2-mix-1", "96875");
}

#[test]
fn phase2_mix_2_matches_perl_with_rand_1_32() {
    check_fixture_at("phase2-mix-2", "03125");
}

#[test]
fn phase2_mix_2_matches_perl_with_rand_31_32() {
    check_fixture_at("phase2-mix-2", "96875");
}

#[test]
fn phase2_mix_3_matches_perl_with_rand_1_32() {
    check_fixture_at("phase2-mix-3", "03125");
}

#[test]
fn phase2_mix_3_matches_perl_with_rand_31_32() {
    check_fixture_at("phase2-mix-3", "96875");
}

#[test]
fn phase2_mix_4_matches_perl_with_rand_1_32() {
    check_fixture_at("phase2-mix-4", "03125");
}

#[test]
fn phase2_mix_4_matches_perl_with_rand_31_32() {
    check_fixture_at("phase2-mix-4", "96875");
}

#[test]
fn phase2_badfields_matches_perl_with_rand_0() {
    check_fixture("phase2-badfields", 0);
}

#[test]
fn phase2_badfields_matches_perl_with_rand_half() {
    check_fixture("phase2-badfields", RAND_HALF);
}

#[test]
fn phase2_mix_5_matches_perl_with_rand_0() {
    check_fixture_at("phase2-mix-5", "0");
}

#[test]
fn phase2_mix_5_matches_perl_with_rand_03125() {
    check_fixture_at("phase2-mix-5", "03125");
}

#[test]
fn phase2_mix_5_matches_perl_with_rand_50() {
    check_fixture_at("phase2-mix-5", "50");
}

#[test]
fn phase2_mix_5_matches_perl_with_rand_96875() {
    check_fixture_at("phase2-mix-5", "96875");
}

#[test]
fn phase2_mix_6_matches_perl_with_rand_0() {
    check_fixture_at("phase2-mix-6", "0");
}

#[test]
fn phase2_mix_6_matches_perl_with_rand_03125() {
    check_fixture_at("phase2-mix-6", "03125");
}

#[test]
fn phase2_mix_6_matches_perl_with_rand_50() {
    check_fixture_at("phase2-mix-6", "50");
}

#[test]
fn phase2_mix_6_matches_perl_with_rand_96875() {
    check_fixture_at("phase2-mix-6", "96875");
}

#[test]
fn phase3_attack_matches_perl_with_rand_0() {
    check_fixture("phase3-attack", 0);
}

#[test]
fn phase3_attack_matches_perl_with_rand_half() {
    check_fixture("phase3-attack", RAND_HALF);
}

#[test]
fn phase3_attack_matches_perl_with_rand_03125() {
    check_fixture_at("phase3-attack", "03125");
}

#[test]
fn phase3_attack_matches_perl_with_rand_96875() {
    check_fixture_at("phase3-attack", "96875");
}

#[test]
fn phase3_attack_lr_matches_perl_with_rand_0() {
    check_fixture("phase3-attack-lr", 0);
}

#[test]
fn phase3_attack_lr_matches_perl_with_rand_half() {
    check_fixture("phase3-attack-lr", RAND_HALF);
}

#[test]
fn phase3_attack_lr_matches_perl_with_rand_03125() {
    check_fixture_at("phase3-attack-lr", "03125");
}

#[test]
fn phase3_attack_lr_matches_perl_with_rand_96875() {
    check_fixture_at("phase3-attack-lr", "96875");
}

#[test]
fn phase3_attack_ld_matches_perl_with_rand_0() {
    check_fixture("phase3-attack-ld", 0);
}

#[test]
fn phase3_attack_ld_matches_perl_with_rand_half() {
    check_fixture("phase3-attack-ld", RAND_HALF);
}

#[test]
fn phase3_attack_ld_matches_perl_with_rand_03125() {
    check_fixture_at("phase3-attack-ld", "03125");
}

#[test]
fn phase3_attack_ld_matches_perl_with_rand_96875() {
    check_fixture_at("phase3-attack-ld", "96875");
}

#[test]
fn phase3_attack_guard_matches_perl_with_rand_0() {
    check_fixture("phase3-attack-guard", 0);
}

#[test]
fn phase3_attack_guard_matches_perl_with_rand_half() {
    check_fixture("phase3-attack-guard", RAND_HALF);
}

#[test]
fn phase3_attack_guard_matches_perl_with_rand_03125() {
    check_fixture_at("phase3-attack-guard", "03125");
}

#[test]
fn phase3_attack_guard_matches_perl_with_rand_96875() {
    check_fixture_at("phase3-attack-guard", "96875");
}

#[test]
fn phase3_attack_mon_matches_perl_with_rand_0() {
    check_fixture("phase3-attack-mon", 0);
}

#[test]
fn phase3_attack_mon_matches_perl_with_rand_half() {
    check_fixture("phase3-attack-mon", RAND_HALF);
}

#[test]
fn phase3_attack_mon_matches_perl_with_rand_03125() {
    check_fixture_at("phase3-attack-mon", "03125");
}

#[test]
fn phase3_attack_mon_matches_perl_with_rand_96875() {
    check_fixture_at("phase3-attack-mon", "96875");
}

#[test]
fn phase3_attack_send_matches_perl_with_rand_0() {
    check_fixture("phase3-attack-send", 0);
}

#[test]
fn phase3_attack_send_matches_perl_with_rand_half() {
    check_fixture("phase3-attack-send", RAND_HALF);
}

#[test]
fn phase3_attack_send_matches_perl_with_rand_03125() {
    check_fixture_at("phase3-attack-send", "03125");
}

#[test]
fn phase3_attack_send_matches_perl_with_rand_96875() {
    check_fixture_at("phase3-attack-send", "96875");
}
