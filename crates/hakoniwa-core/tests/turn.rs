//! ターン処理を通しで動かすテスト。

use std::path::Path;

use hakoniwa_core::GameConfig;
use hakoniwa_core::legacy::{self, ImportOptions};
use hakoniwa_core::model::GameState;
use hakoniwa_core::tables::CommandKind;
use hakoniwa_core::turn::run_turn;
use rand::SeedableRng;
use rand::rngs::StdRng;

fn load(name: &str) -> GameState {
    let dir = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures")
        .join(name);
    legacy::import_dir(
        &dir,
        &ImportOptions::default(),
        &mut StdRng::seed_from_u64(0),
    )
    .unwrap()
    .state
}

/// Perl 版で島を作ってターンを回すと、計画を入れない島は 5 ターン目に自動で放棄された
/// (連続資金繰り数が 21 から始まり、24 で放棄の計画が入る)。同じことが起きるか
#[test]
fn idle_islands_are_abandoned_like_perl() {
    let config = GameConfig::default();
    let mut state = load("legacy-turn3");
    let start_time = state.world.last_time;
    let mut rng = StdRng::seed_from_u64(42);

    // ターン 4: 資金繰りで連続資金繰り数が 24 になり、先頭に「島の放棄」が入る
    let report = run_turn(&mut state, &config, &mut rng);
    assert_eq!(report.turn, 4);
    assert_eq!(state.world.turn, 4);
    assert_eq!(state.world.last_time, start_time + config.unit_time);
    assert_eq!(state.world.islands.len(), 3);
    for island in &state.world.islands {
        assert_eq!(island.absent, 24, "{}", island.name);
        assert_eq!(island.commands[0].command_kind(), Some(CommandKind::Giveup));
        assert_eq!(island.commands.len(), config.command_max);
        assert!(island.pts > 0);
    }
    // ログは新しいターンが先頭
    assert_eq!(state.logs.turns.len(), 3);

    // ターン 5: 放棄されて島がなくなる
    let report = run_turn(&mut state, &config, &mut rng);
    assert_eq!(report.turn, 5);
    assert!(state.world.islands.is_empty());

    let mut abandoned: Vec<_> = state
        .logs
        .history
        .iter()
        .filter(|h| h.turn == 5)
        .map(|h| h.message.as_str())
        .collect();
    abandoned.sort();
    // Perl 版で実際に記録された文面と同じ
    let mut expected = vec![
        "<FONT COLOR=\"#a06040\"><B>箱庭島</B></FONT>、放棄され<B>無人島</B>となる。",
        "<FONT COLOR=\"#a06040\"><B>テスト島</B></FONT>、放棄され<B>無人島</B>となる。",
        "<FONT COLOR=\"#a06040\"><B>Alpha島</B></FONT>、放棄され<B>無人島</B>となる。",
    ];
    expected.sort();
    assert_eq!(abandoned, expected);
    // 失業者の暴動などは乱数しだいで出るので、放棄のログだけ数える
    let giveups = state.logs.turns[0]
        .iter()
        .filter(|e| e.message.contains("は放棄され"))
        .count();
    assert_eq!(giveups, 3);
    assert!(state.logs.turns[0].iter().all(|e| e.turn == 5 && !e.secret));
}

#[test]
fn turn_prize_goes_to_top_island() {
    let config = GameConfig::default();
    let mut state = load("legacy-turn3");
    state.world.turn = 99;
    for island in state.world.islands.iter_mut() {
        island.absent = 0;
    }

    let report = run_turn(&mut state, &config, &mut StdRng::seed_from_u64(7));
    assert_eq!(report.turn, 100);
    assert!(!report.backup_due);

    // ポイント 1 位の島だけが受賞し、受賞記録にターン番号が付く
    let winners: Vec<_> = state
        .world
        .islands
        .iter()
        .filter(|i| i.prize.ends_with("100,"))
        .collect();
    assert_eq!(winners.len(), 1);
    assert_eq!(winners[0].id, state.world.islands[0].id);
    let history: Vec<_> = state
        .logs
        .history
        .iter()
        // toto と Numbers3 の正解の記録は除く
        .filter(|h| {
            h.turn == 100 && !h.message.contains("ｔｏｔｏ") && !h.message.contains("Numbers3")
        })
        .collect();
    assert_eq!(history.len(), 1);
    assert!(history[0].message.contains(&winners[0].name));
    assert!(history[0].message.contains("100ターン杯"));
}

#[test]
fn ranking_and_backup_flags() {
    let config = GameConfig::default();
    let mut state = load("legacy-turn3");
    for island in state.world.islands.iter_mut() {
        island.absent = 0;
    }
    let mut rng = StdRng::seed_from_u64(1);
    let mut backups = Vec::new();
    for _ in 0..10 {
        let report = run_turn(&mut state, &config, &mut rng);
        if report.backup_due {
            backups.push(report.turn);
        }
        let pts: Vec<_> = state.world.islands.iter().map(|i| i.pts).collect();
        let mut sorted = pts.clone();
        sorted.sort_by(|a, b| b.cmp(a));
        assert_eq!(pts, sorted, "islands are ordered by points");
    }
    assert_eq!(backups, [12]);
    // ログは log0..log8 の 9 ターン分まで
    assert_eq!(state.logs.turns.len(), config.log_max + 1);
}
