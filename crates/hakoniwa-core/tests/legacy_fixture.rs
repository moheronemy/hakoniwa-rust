//! Perl 版で実際に作ったセーブデータを読み込むテスト。
//!
//! `tests/fixtures/legacy-turn3/` は、Perl 版 (hako-r-a_FE) をローカルで動かして
//! 島を 3 つ登録し、ローカル掲示板に 2 件書き込み、デバッグモードで 2 ターン進めたもの。

use std::path::Path;

use hakoniwa_core::legacy::{self, ImportOptions, IslandLayout};
use hakoniwa_core::model::LandCell;
use hakoniwa_core::storage;
use hakoniwa_core::tables::{CommandKind, LandKind};

fn import() -> legacy::Import {
    let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/legacy-turn3");
    legacy::import_dir(&dir, &ImportOptions::default(), &mut rand::thread_rng()).unwrap()
}

#[test]
fn reads_world() {
    let import = import();
    assert!(import.warnings.is_empty(), "{:?}", import.warnings);
    assert_eq!(import.layout, IslandLayout::NewGame);

    let world = &import.state.world;
    assert_eq!(world.turn, 3);
    assert_eq!(world.last_time, 1_794_290_400);
    assert_eq!(world.next_id, 4);
    assert_eq!(world.auction_lots.len(), 3);
    assert_eq!(world.survey_votes, [0; 5]);

    // Perl 版は人口順に並べて保存する
    let order: Vec<_> = world
        .islands
        .iter()
        .map(|i| (i.id, i.name.as_str()))
        .collect();
    assert_eq!(order, [(3, "箱庭"), (1, "テスト"), (2, "Alpha")]);
}

#[test]
fn reads_island() {
    let import = import();
    let island = import.state.world.island_by_id(1).unwrap();
    assert_eq!(island.name, "テスト");
    assert_eq!(island.owner_name, "オーナー1");
    assert_eq!(island.comment, "こんにちは");
    assert_eq!(island.password, "h2USP8HoS6YNQ");
    assert_eq!(
        (island.money, island.food, island.pop, island.area),
        (2219, 187, 72, 33)
    );
    assert_eq!(island.ip[0], "10.0.0.1");
    assert_eq!(island.survey_flag, 1);
    // eisei3..6 は Perl 版でもカンマ区切りの文字列のまま扱われている
    assert_eq!(island.eisei_raw[0].matches(',').count(), 4);

    // 地図: island.1 の 3 行目 (y=2) は x=5 が浅瀬 (海, 値 1)、x=6 が荒地
    assert_eq!(island.map.size, 12);
    assert_eq!(island.map.get(5, 2), Some(LandCell { kind: 0, value: 1 }));
    assert_eq!(
        island.map.get(6, 2).unwrap().land_kind(),
        Some(LandKind::Waste)
    );
    assert!(island.map.cells.iter().all(|c| c.land_kind().is_some()));

    // 計画は 40 件。未入力の枠は「資金繰り」で埋まっている
    assert_eq!(island.commands.len(), 40);
    assert_eq!(
        island.commands[0].command_kind(),
        Some(CommandKind::DoNothing)
    );

    // ローカル掲示板は 15 行。新しい順
    assert_eq!(island.lbbs.len(), 15);
    assert_eq!(
        island.lbbs[0],
        "0<Alpha島<0>1：観光客>こんにちは 訪問しました"
    );
    assert_eq!(island.lbbs[1], "0<<1>1：島主>ようこそ！");
    assert_eq!(island.lbbs[2], "0<<0>>");
}

#[test]
fn reads_logs() {
    let import = import();
    let logs = &import.state.logs;
    assert_eq!(logs.turns.len(), 2);
    assert_eq!(logs.turns[0].entries()[0].turn, 3);
    assert_eq!(logs.turns[1].entries()[0].turn, 2);
    assert!(!logs.turns[0].entries()[0].secret);
    assert_eq!(logs.turns[0].entries()[0].island1, Some(0));
    assert_eq!(logs.turns[0].entries()[0].island2, None);

    assert_eq!(logs.history.len(), 3);
    assert_eq!(logs.history[0].turn, 1);
    assert!(logs.history[0].message.contains("テスト島"));
    assert!(logs.hcup.is_empty());
    assert!(logs.auction.is_empty());
}

#[test]
fn survives_json_round_trip() {
    let import = import();
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("state.json");
    storage::save(&path, &import.state).unwrap();
    assert_eq!(storage::load(&path).unwrap().unwrap(), import.state);
}
