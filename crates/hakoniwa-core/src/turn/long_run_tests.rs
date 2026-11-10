//! 長期の比較: 何十ターンも続けて、元の Perl CGI と移植版を突き合わせる。
//!
//! `tests/fixtures/cgi/long-*.json` (`tools/fixtures/phase7_long.py` が作る) は 10〜30 個の
//! リクエストを持つ。ターンのリクエストは前のターンの 1 ターンあとの時刻なので、Perl 版は
//! リクエストのたびに `turnMain` を 1 回行い、データを保存して次のリクエストで読み直す
//! (本番と同じ)。あいだに計画の入力・政策・島の登録の画面の操作が入る。
//! `rand()` の並びはリクエストごとに先頭から始まる (Perl 版はリクエストごとに別のプロセス)。
//!
//! `run_cgi.py` はリクエストごとのデータを `snapshots.json.gz` (前のリクエストからの差分) に
//! 残すので、移植版も 1 リクエストずつ進めては比べ、最初に食い違ったリクエストを報告する。
//! 移植版の状態は、本番で再起動したときと同じく、リクエストごとに JSON で保存して読み直す。

use std::collections::{BTreeMap, HashSet};
use std::io::Read;
use std::path::Path;

use serde_json::Value;

use crate::GameConfig;
use crate::actions::auction::bid;
use crate::actions::command::{CommandInput, CommandMode, input_command};
use crate::actions::create::{NewIslandInput, new_island};
use crate::actions::password::check_password;
use crate::actions::perl_compat_tests::{SeqRng, cgi_dir, diff, import};
use crate::actions::policy::{Policy, set_policy};
use crate::actions::toto::{prediction_open, set_prediction};
use crate::actions::{ActionError, Request};
use crate::model::GameState;
use crate::perl;

use super::run_turn;

/// データのディレクトリのファイル (名前 → 内容を latin-1 で文字列にしたもの)
type Files = BTreeMap<String, String>;

fn read_dir(dir: &Path) -> Files {
    std::fs::read_dir(dir)
        .unwrap()
        .map(|e| e.unwrap().path())
        .filter(|p| p.is_file())
        .map(|p| {
            let bytes = std::fs::read(&p).unwrap();
            let name = p.file_name().unwrap().to_string_lossy().into_owned();
            (name, bytes.into_iter().map(char::from).collect())
        })
        .collect()
}

/// `snapshots.json.gz` (リクエストごとの差分) を読む
fn read_snapshots(dir: &Path) -> Vec<BTreeMap<String, Option<String>>> {
    let file = std::fs::File::open(dir.join("snapshots.json.gz")).unwrap();
    let mut text = String::new();
    flate2::read::GzDecoder::new(file)
        .read_to_string(&mut text)
        .unwrap();
    serde_json::from_str(&text).unwrap()
}

/// Perl 版のデータ `files` を読み込む
fn import_files(files: &Files) -> GameState {
    let tmp = tempfile::tempdir().unwrap();
    for (name, text) in files {
        let bytes: Vec<u8> = text.chars().map(|c| c as u8).collect();
        std::fs::write(tmp.path().join(name), bytes).unwrap();
    }
    import(tmp.path())
}

/// 移植版がわざと出さない・書き方の違うものを Perl 版の結果から直す
fn fix_want(want: &mut GameState) {
    // 移植版は Perl 版の負荷計測のログを出さない
    for turn in &mut want.logs.turns {
        std::sync::Arc::make_mut(turn).retain(|e| !e.message.contains("負荷計測"));
    }
    // Hakoniwa Cup の試合のログの「−」(full_turn_tests.rs の stadium_dash)
    let fix = |m: &mut String| *m = m.replace('－', "−");
    want.logs.hcup.iter_mut().for_each(|m| fix(&mut m.message));
    for turn in &mut want.logs.turns {
        std::sync::Arc::make_mut(turn)
            .iter_mut()
            .for_each(|e| fix(&mut e.message));
    }
}

fn form<'a>(req: &'a Value, key: &str) -> &'a str {
    req["form"][key].as_str().unwrap_or_default()
}

/// フォームのボタン `<prefix><島ID>` を探す
fn button(req: &Value, prefix: &str) -> Option<i64> {
    req["form"]
        .as_object()?
        .keys()
        .find_map(|k| k.strip_prefix(prefix)?.parse().ok())
}

/// 画面の操作を 1 つ行う。登録した島の ID を返す
fn screen(
    game: &mut GameState,
    config: &GameConfig,
    req: &Value,
    now: i64,
    rng: &mut SeqRng,
) -> Option<i64> {
    let addr = req["addr"].as_str().unwrap_or("10.0.0.1");
    let request = Request {
        now,
        remote_addr: addr,
    };
    // Perl 版は島が無い ID の操作を 0 番目の島に対して行う (移植版はエラーにする)。
    // パスワードが合えば Perl 版はその島を書き換えるので、ここではそれに合わせる
    let island_id = |game: &GameState, id: i64| {
        if game.world.island_by_id(id).is_some() {
            id
        } else {
            game.world.islands[0].id
        }
    };
    let password_ok = |game: &GameState, id: i64| {
        let island = game.world.island_by_id(id).unwrap();
        check_password(config, &island.password, form(req, "PASSWORD"))
    };

    if let Some(id) = button(req, "CommandButton") {
        let id = island_id(game, id);
        if !password_ok(game, id) {
            return None;
        }
        let input = CommandInput {
            number: perl::int(form(req, "NUMBER")) as usize,
            mode: CommandMode::from_form(form(req, "COMMANDMODE")),
            kind: form(req, "COMMAND"),
            amount: form(req, "AMOUNT"),
            target: form(req, "TARGETID"),
            x: form(req, "POINTX"),
            y: form(req, "POINTY"),
            lamount1: form(req, "LAMOUNT1"),
            lamount2: form(req, "LAMOUNT2"),
        };
        input_command(game, config, request, rng, id, &input).unwrap();
        return None;
    }
    if let Some(id) = button(req, "TotoButton") {
        // Perl 版は受付期間をパスワードより先に確かめる
        let id = island_id(game, id);
        if prediction_open(game.world.turn) && password_ok(game, id) {
            set_prediction(game, id, form(req, "MESSAGE")).unwrap();
        }
        return None;
    }
    if let Some(id) = button(req, "AuctionButton") {
        let id = island_id(game, id);
        if password_ok(game, id) {
            match bid(
                game,
                config,
                rng,
                id,
                form(req, "AUCNUMBER"),
                form(req, "AMOUNT"),
            ) {
                Ok(()) | Err(ActionError::Rejected(_)) => {}
                Err(e) => panic!("{e}"),
            }
        }
        return None;
    }
    if req["form"].get("NewIslandButton").is_some() {
        let input = NewIslandInput {
            name: form(req, "ISLANDNAME"),
            owner_name: form(req, "OWNERNAME"),
            password: form(req, "PASSWORD"),
            password2: form(req, "PASSWORD2"),
            message: form(req, "MESSAGE"),
        };
        return match new_island(game, config, request, rng, &input) {
            Ok(id) => Some(id),
            Err(ActionError::Rejected(_)) => None,
            Err(e) => panic!("{e}"),
        };
    }
    for (name, policy) in [
        ("ShoueneButton", Policy::Shouene),
        ("BousaiButton", Policy::Bousai),
        ("KankouButton", Policy::Kankou),
        ("SizenButton", Policy::Sizen),
        ("KyouikuButton", Policy::Kyouiku),
        ("ChochikuButton", Policy::Chochiku),
    ] {
        if let Some(id) = button(req, name) {
            let id = island_id(game, id);
            if password_ok(game, id) {
                set_policy(game, id, policy, form(req, "AMOUNT")).unwrap();
            }
            return None;
        }
    }
    panic!("unknown request: {req}");
}

/// ケース `name` のリクエストを順に移植版で行い、リクエストごとに Perl 版のデータと比べる
fn check_long(name: &str) {
    let json: Value = serde_json::from_str(
        &std::fs::read_to_string(cgi_dir().join(format!("{name}.json"))).unwrap(),
    )
    .unwrap();
    let dir = cgi_dir().join(name);
    let mut files = read_dir(&dir.join("before"));
    let snapshots = read_snapshots(&dir);
    let requests = json["requests"].as_array().unwrap();
    assert_eq!(snapshots.len(), requests.len());

    let config = GameConfig::default();
    let mut game = import_files(&files);
    // 前のターンまでのログの負荷計測も取り除いておく
    fix_want(&mut game);
    // 移植版で登録した島 (パスワードの保存形式が違う)
    let mut created = HashSet::new();
    let mut turns = 0;
    for (n, (req, delta)) in requests.iter().zip(&snapshots).enumerate() {
        let now = req["time"].as_i64().unwrap();
        let mut rng = SeqRng::new(req.get("rand").unwrap_or(&json["rand"]));
        // Perl 版の turnMain に切り替える条件 (hako-main.cgi の readIslandsFile)
        let is_turn = now - game.world.last_time >= config.unit_time;
        if is_turn {
            run_turn(&mut game, &config, &mut rng);
            turns += 1;
        } else {
            // Perl 版は読み込むときに空の出品の品物を決め直す (画面の操作の前)
            crate::model::reroll_empty_lots(&mut game.world.auction_lots, &mut rng);
            created.extend(screen(&mut game, &config, req, now, &mut rng));
        }
        // 保存して読み直す
        game = serde_json::from_value(serde_json::to_value(&game).unwrap()).unwrap();

        for (file, text) in delta {
            match text {
                Some(t) => files.insert(file.clone(), t.clone()),
                None => files.remove(file),
            };
        }
        let mut want = import_files(&files);
        fix_want(&mut want);
        for island in game.world.islands.iter_mut() {
            if created.contains(&island.id)
                && let Some(w) = want.world.island_by_id(island.id)
            {
                island.password.clone_from(&w.password);
            }
        }
        let want = serde_json::to_value(&want).unwrap();
        let got = serde_json::to_value(&game).unwrap();
        let mut diffs = Vec::new();
        diff(&want, &got, String::new(), &[], &mut diffs);
        assert!(
            diffs.is_empty(),
            "{name}: request {n} ({}, turn {}): {} differences\n{}",
            if is_turn { "turn" } else { "screen" },
            game.world.turn,
            diffs.len(),
            diffs[..diffs.len().min(40)].join("\n")
        );
    }
    assert!(turns >= 10, "{name}: {turns} turns");
}

#[test]
fn long_play_matches_perl() {
    check_long("long-play");
}

#[test]
fn long_mix_100_matches_perl() {
    check_long("long-mix-100");
}

#[test]
fn long_mix_140_matches_perl() {
    check_long("long-mix-140");
}

#[test]
fn long_mix_200_matches_perl() {
    check_long("long-mix-200");
}

#[test]
fn long_auction_300_matches_perl() {
    check_long("long-auction-300");
}

#[test]
fn long_disaster_matches_perl() {
    check_long("long-disaster");
}

#[test]
fn long_growth_matches_perl() {
    check_long("long-growth");
}
