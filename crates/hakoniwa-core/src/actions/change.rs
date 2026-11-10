//! 島の名前・パスワード・オーナー名の変更 (`changeMain`, `changeOwner`)。
//!
//! Perl 版との違い (わざと変えた点):
//! - 新しいパスワードは [`hash_password`] (SHA-512 crypt) で保存する。Perl 版の DES crypt は
//!   先頭 8 文字しか効かないが、移植版は切り詰めない。
//! - 管理用パスワード (`config.passwords` の `special` など) は、設定されたときだけ有効
//!   (Perl 版はソースに直書きされていた)。

use crate::GameConfig;
use crate::model::{GameState, Island, IslandMap, PlannedCommand, TurnMessage, World};
use crate::perl::{self, cgi_text, cut_column, html_escape};

use super::create::{MSG_ALREADY, MSG_BAD_NAME, is_bad_name, island_tag};
use super::password::{check_password, hash_password};
use super::{ActionError, island_index};

/// 何も変えるものが無い (`tempChangeNothing`)
pub const MSG_NOTHING: &str = "名前、パスワードともに空欄です";
/// 名前の変更の資金が足りない (`tempChangeNoMoney`)
pub const MSG_NO_MONEY: &str = "資金不足のため変更できません";
/// 成功したとき Perl 版が出していた文面 (`tempChange`)
pub const MSG_CHANGED: &str = "変更完了しました";

/// 「島の名前とパスワードの変更」フォームの入力。どれも利用者が打ったままの文字列
#[derive(Debug, Clone, Copy, Default)]
pub struct ChangeInput<'a> {
    /// いまのパスワード (`OLDPASS`、必須)。管理用パスワードもここに入れる
    pub old_password: &'a str,
    /// 新しい島の名前 (`ISLANDNAME`、変えるときだけ)
    pub name: &'a str,
    /// 新しいオーナー名 (`OWNERNAME`、変えるときだけ)。島のコメントの前に出る名前 (`onm`) が変わる
    pub owner_name: &'a str,
    /// 新しいパスワード (`PASSWORD`、変えるときだけ)
    pub password: &'a str,
    /// 確認用 (`PASSWORD2`)。`password` と同じでなければならない (どちらも空でもよい)
    pub password2: &'a str,
}

/// `$HidToNumber{$HcurrentID}`。Perl 版は見つからない ID でも `$Hislands[undef]`、
/// つまり先頭 (1 位) の島を相手にしてしまう (Perl 版のまま)
fn target_index(world: &World, id: i64) -> Result<usize, ActionError> {
    if world.islands.is_empty() {
        return Err(ActionError::NoSuchIsland);
    }
    Ok(island_index(world, id).unwrap_or(0))
}

/// `writeIslandsFile` は `ips.dat` の先頭行に島の名前を書くので、保存すると
/// すべての島の `ipname` が名前と同じになる
fn sync_ip_names(world: &mut World) {
    for island in world.islands.iter_mut() {
        island.ip_name.clone_from(&island.name);
    }
}

/// `changeMain`: 島の名前・パスワード・オーナー名 (`onm`) を変える。
///
/// `id` の島が無いときは、Perl 版と同じく先頭の島が対象になる (島が 1 つも無ければ
/// [`ActionError::NoSuchIsland`])。名前の変更は `config.cost_change_name` かかり、
/// 発見の記録に「名称を変更する」が残る。エラーは [`ActionError::WrongPassword`]
/// (いまのパスワード・確認用パスワードの違い) と [`ActionError::Rejected`]
/// (`MSG_BAD_NAME`, `MSG_ALREADY`, `MSG_NO_MONEY`, `MSG_NOTHING`)。失敗したときは何も変えない。
///
/// `old_password` が `config.passwords` の管理用パスワードなら、パスワードの照合の代わりに:
/// - `special`: 資金 999999・食料 99999 にし、名前の変更を無料にする (何も変えなくても成功)
/// - `shuto`: 首都名 (`totoyoso2`) をオーナー名の欄の値にする
/// - `omamori`: `etc8` の 2 番目 (おまもり) を 1 増やす
/// - `ijiri`: オーナー名の欄で指定した Perl 版の項目 (`money`, `comment`, `mshp` など) を
///   名前の欄の値にして、すぐに終わる ([`ijiri`] を参照)
/// - `ip`: アクセス元の記録 (`ip0`〜`ip9`) を 0 にする
///
/// `special`・`ijiri` 以外は、そのあと通常どおり名前などの変更も行う。
pub fn change_info(
    game: &mut GameState,
    config: &GameConfig,
    id: i64,
    input: &ChangeInput,
) -> Result<(), ActionError> {
    let n = target_index(&game.world, id)?;
    let old = cgi_text(input.old_password);
    let name = cut_column(&cgi_text(input.name), 20);
    let owner_name = cut_column(&cgi_text(input.owner_name), 20);
    let password = cgi_text(input.password);
    let password2 = cgi_text(input.password2);

    let pw = &config.passwords;
    let is = |p: &Option<String>| p.as_deref() == Some(old.as_str());
    let special = is(&pw.special);

    // 途中で失敗したら何も保存しないので、写しを書き換える
    let mut island = game.world.islands[n].clone();
    let mut flag = false;

    // パスワードチェック
    if special {
        island.money = 999999;
        island.food = 99999;
    } else if is(&pw.shuto) {
        island.totoyoso2 = html_escape(&owner_name);
        flag = true;
    } else if is(&pw.omamori) {
        // 一致しなければ $1.. は未定義 (空)。$toto2++ で 1 になる
        let mut t = raw_fields::<7>(&island.etc_raw[3]).unwrap_or_default();
        t[1] = (perl::int(&t[1]) + 1).to_string();
        island.etc_raw[3] = t.join(",");
        flag = true;
    } else if is(&pw.ijiri) {
        ijiri(&mut game.world, config, n, &owner_name, &name);
        return Ok(());
    } else if is(&pw.ip) {
        island.ip = std::array::from_fn(|_| "0".to_string());
        island.ip_counters = [0; 2];
        flag = true;
    } else if !check_password(config, &island.password, &old) {
        return Err(ActionError::WrongPassword);
    }

    // 確認用パスワード
    if password2 != password {
        return Err(ActionError::WrongPassword);
    }

    let mut history = None;
    if !name.is_empty() {
        // 名前変更の場合。登録と違い '$' は使える (Perl 版のまま)
        if is_bad_name(&name, false) {
            return Err(ActionError::Rejected(MSG_BAD_NAME.into()));
        }
        // 名前の重複チェック (いまの自分の名前も重複になる)
        if game.world.islands.iter().any(|i| i.name == name) {
            return Err(ActionError::Rejected(MSG_ALREADY.into()));
        }
        if island.money < config.cost_change_name {
            return Err(ActionError::Rejected(MSG_NO_MONEY.into()));
        }
        if !special {
            island.money -= config.cost_change_name;
        }
        // logChangeName
        history = Some(format!(
            "{}、名称を{}に変更する。",
            island_tag(&island.name),
            island_tag(&name)
        ));
        island.name = name;
        flag = true;
    }

    // パスワード変更の場合
    if !password.is_empty() {
        island.password = hash_password(&password);
        flag = true;
    }

    if !owner_name.is_empty() {
        island.onm = html_escape(&owner_name);
        flag = true;
    }

    if !flag && !special {
        return Err(ActionError::Rejected(MSG_NOTHING.into()));
    }

    game.world.islands[n] = island;
    sync_ip_names(&mut game.world);
    if let Some(message) = history {
        // logHistory (logHistoryTrim は呼ばれない)
        game.logs.history.push(TurnMessage {
            turn: game.world.turn,
            message,
        });
    }
    Ok(())
}

/// `changeOwner`: オーナー名 (`ownername`) を変える。フォームの `OLDPASS` と `OWNERNAME`。
///
/// オーナー名が空でもそのまま空にする (Perl 版のまま)。管理用パスワードは効かない
/// (マスターパスワードは効く)。`id` の島が無いときは先頭の島が対象になる (Perl 版のまま)。
pub fn change_owner(
    game: &mut GameState,
    config: &GameConfig,
    id: i64,
    old_password: &str,
    owner_name: &str,
) -> Result<(), ActionError> {
    let n = target_index(&game.world, id)?;
    let island = &mut game.world.islands[n];
    if !check_password(config, &island.password, &cgi_text(old_password)) {
        return Err(ActionError::WrongPassword);
    }
    island.owner_name = html_escape(&cut_column(&cgi_text(owner_name), 20));
    Ok(())
}

/// `^([0-9]*),...,([0-9]*)$` (N 個) に一致すれば各欄の文字列 (空もありうる)
fn raw_fields<const N: usize>(s: &str) -> Option<[String; N]> {
    let parts: Vec<&str> = s.split(',').collect();
    (parts.len() == N && parts.iter().all(|p| p.bytes().all(|b| b.is_ascii_digit())))
        .then(|| std::array::from_fn(|i| parts[i].to_string()))
}

/// `changeMain` の `$HijiriPassword` の処理: `$island->{htmlEscape(オーナー名)} = 名前`。
///
/// Perl 版は島のハッシュの任意のキーに書き込み、保存して読み直したときの値になる。
/// 移植版はそれを項目ごとに再現する ([`set_perl_field`])。ただしマスコット
/// (`mshp`, `msap`, `msdp`, `mssp`, `msexe`) は `eisei5` の該当する欄を書き換える
/// (`eisei5` が数字だけの 7 欄でなければ、ほかの欄は空になる: Perl 版のまま)。
/// パスワードの照合も確認用パスワードの確認もしない。
fn ijiri(world: &mut World, config: &GameConfig, n: usize, owner_name: &str, value: &str) {
    let key = html_escape(owner_name);
    let island = &mut world.islands[n];
    let slot = match key.as_str() {
        "mshp" => Some(0),
        "msap" => Some(1),
        "msdp" => Some(2),
        "mssp" => Some(3),
        "msexe" => Some(5),
        _ => None,
    };
    match slot {
        Some(i) => {
            let mut f = raw_fields::<7>(&island.eisei_raw[2]).unwrap_or_default();
            f[i] = value.to_string();
            island.eisei_raw[2] = f.join(",");
        }
        None => set_perl_field(island, config, &key, value),
    }
    sync_ip_names(world);
}

/// Perl 版の島のハッシュのキー `key` に文字列 `value` を入れて、保存・読み込みを経た値にする。
///
/// - 数値として読む項目 (`money`, `id`, `eis1` など) は `int()` した値
/// - `auc0` などの既定値のある複合値は、数値として 0 なら既定値 (読み込み時の補完)
/// - `anflag` は 0 なら 1
/// - `land` / `landValue` / `command` / `lbbs` は文字列を配列として書き出すことになり、
///   地形の種類 / 地形の値 / 計画 / 掲示板がすべて 0 (空) になる
///   (値が Perl 版の既存のグローバル配列の名前と同じ場合の挙動は再現しない)
/// - `id`: Perl 版は地図のファイル `island.ID` を `island.値` に改名する。値が数字だけで
///   書かれた整数そのもの (`"9"` など) でなければ、読み込み時に地図が見つからず海になる
/// - 保存されないキー (`ipname`, `mswin` など) は何も変えない
pub fn set_perl_field(island: &mut Island, config: &GameConfig, key: &str, value: &str) {
    let int = perl::int(value);
    let s = value.to_string();
    let with_default = |d: &str| {
        if perl::num_eq_empty(value) {
            d.to_string()
        } else {
            value.to_string()
        }
    };
    let idx = |prefix: &str, max: usize| -> Option<usize> {
        let rest = key.strip_prefix(prefix)?;
        let i: usize = rest.parse().ok()?;
        (rest == i.to_string() && (1..=max).contains(&i)).then_some(i)
    };
    match key {
        "name" => island.name = s,
        "id" => {
            island.id = int;
            if int.to_string() != value {
                island.map = IslandMap::new_sea(config.island_size);
                island.commands = vec![PlannedCommand::default(); config.command_max];
                island.lbbs = vec![String::new(); config.lbbs.max];
            }
        }
        "score" => island.score = int,
        "prize" => island.prize = s,
        "absent" => island.absent = int,
        "comment" => island.comment = s,
        "password" => island.password = s,
        "money" => island.money = int,
        "food" => island.food = int,
        "pop" => island.pop = int,
        "area" => island.area = int,
        "farm" => island.farm = int,
        "factory" => island.factory = s,
        "mountain" => island.mountain = int,
        "pts" => island.pts = int,
        "eis8" => island.eis8 = s,
        "taiji" => island.taiji = int,
        "onm" => island.onm = s,
        "monsterlive" => island.monster_live = int,
        "monsterlivetype" => island.monster_live_type = int,
        "id1" => island.id1 = int,
        "ownername" => island.owner_name = s,
        "totoyoso" => island.totoyoso = s,
        "totoyoso2" => island.totoyoso2 = s,
        "kei" => island.owner_stats.kei = int,
        "rena" => island.owner_stats.rena = int,
        "momotan" => island.owner_stats.momotan = int,
        "fore" => island.owner_stats.fore = int,
        "pika" => island.owner_stats.pika = int,
        "hamu" => island.owner_stats.hamu = int,
        "monta" => island.owner_stats.monta = int,
        "tare" => island.owner_stats.tare = int,
        "zipro" => island.owner_stats.zipro = int,
        "leje" => island.owner_stats.leje = int,
        "ip8" => island.ip_counters[0] = int,
        "ip9" => island.ip_counters[1] = int,
        "auc0" => island.auction.auc0 = with_default("0,0,0,0,0"),
        "auc1" => island.auction.auc1 = int,
        "auc2" => island.auction.auc2 = int,
        "auc3" => island.auction.auc3 = int,
        "auc4" => island.auction.auc4 = with_default("0,0,0"),
        "auc5" => island.auction.auc5 = with_default("0,0,0,0,0"),
        "auc6" => island.auction.auc6 = with_default("0,0,0"),
        "auc7" => island.auction.auc7 = s,
        "auc8" => island.auction.auc8 = s,
        "auc9" => island.auction.auc9 = with_default("0,0,0,0,0"),
        "anflag" => island.survey_flag = if int == 0 { 1 } else { int },
        "land" => island.map.cells_mut().iter_mut().for_each(|c| c.kind = 0),
        "landValue" => island.map.cells_mut().iter_mut().for_each(|c| c.value = 0),
        "command" => island.commands.fill(PlannedCommand::default()),
        "lbbs" => island.lbbs.fill(String::new()),
        _ => {
            if let Some(i) = idx("eis", 7) {
                island.eis[i - 1] = int;
            } else if let Some(i) = idx("eisei", 6) {
                if i <= 2 {
                    island.eisei[i - 1] = int;
                } else {
                    island.eisei_raw[i - 3] = s;
                }
            } else if let Some(i) = key.strip_prefix("ip").and_then(single_digit) {
                if i < 8 {
                    island.ip[i] = s;
                }
            } else if let Some(i) = key.strip_prefix("etc").and_then(single_digit) {
                if i < 5 {
                    island.etc_num[i] = int;
                } else {
                    island.etc_raw[i - 5] = s;
                }
            }
        }
    }
}

/// `"0"`〜`"9"` の 1 文字
fn single_digit(s: &str) -> Option<usize> {
    (s.len() == 1)
        .then(|| s.as_bytes()[0])
        .filter(u8::is_ascii_digit)
        .map(|b| usize::from(b - b'0'))
}

#[cfg(test)]
mod tests {
    use super::super::password::verify;
    use super::super::perl_compat_tests::{Case, check_case};
    use super::*;
    use crate::config::Passwords;

    /// Perl 版 hako-main.cgi に直書きされている管理用パスワード
    fn perl_config(config: &GameConfig) -> GameConfig {
        let s = |v: &str| Some(v.to_string());
        GameConfig {
            passwords: Passwords {
                master: s("uhusnuvnurkanjhfh"),
                special: s("uhusnuvnurkanjhfhmax"),
                shuto: s("uhusnuvnurkanjhfhshuto"),
                ip: s("uhusnuvnurkanjhfhip"),
                omamori: s("uhusnuvnurkanjhfhomiya"),
                ijiri: s("uhusnuvnurkanjhfhiji"),
            },
            ..config.clone()
        }
    }

    fn change(game: &mut GameState, config: &GameConfig, case: &Case, n: usize) -> String {
        let f = |k| case.form(n, k);
        let (old, name, owner, pw, pw2) = (
            f("OLDPASS"),
            f("ISLANDNAME"),
            f("OWNERNAME"),
            f("PASSWORD"),
            f("PASSWORD2"),
        );
        let id = perl::int(&f("ISLANDID"));
        let r = change_info(
            game,
            config,
            id,
            &ChangeInput {
                old_password: &old,
                name: &name,
                owner_name: &owner,
                password: &pw,
                password2: &pw2,
            },
        );
        match r {
            Ok(()) => MSG_CHANGED.to_string(),
            Err(e) => e.to_string(),
        }
    }

    #[test]
    fn change_info_matches_perl() {
        let wrong = "パスワードが違います";
        let ok = MSG_CHANGED;
        // 新しいパスワードはわざと保存形式を変えているので比べない (下で verify する)
        check_case(
            "change-1",
            &["/world/islands/1/password"],
            |game, config, case| {
                let config = perl_config(config);
                let got: Vec<String> = (0..case.requests.len())
                    .map(|n| change(game, &config, case, n))
                    .collect();
                assert_eq!(
                    got,
                    [
                        wrong,
                        MSG_NOTHING,
                        wrong,
                        MSG_BAD_NAME,
                        ok,
                        MSG_ALREADY,
                        MSG_ALREADY,
                        ok,
                        ok,
                        ok,
                        ok,
                        ok,
                        MSG_NO_MONEY,
                        ok,
                        ok,
                        ok,
                        ok,
                        wrong,
                        ok,
                        ok,
                        ok,
                    ]
                );
                let island = game.world.island_by_id(1).unwrap();
                assert!(verify(&island.password, "newpassword"));
                assert!(!verify(&island.password, "newpasswordX"));
            },
        );
    }

    #[test]
    fn ijiri_matches_perl() {
        check_case("change-ijiri", &[], |game, config, case| {
            let config = perl_config(config);
            for n in 0..case.requests.len() {
                assert_eq!(change(game, &config, case, n), MSG_CHANGED);
            }
        });
    }

    #[test]
    fn ijiri_id_loses_map_like_perl() {
        check_case("change-ijiri-id", &[], |game, config, case| {
            let config = perl_config(config);
            assert_eq!(change(game, &config, case, 0), MSG_CHANGED);
            assert_eq!(game.world.islands[1].id, 0);
        });
    }

    #[test]
    fn change_owner_matches_perl() {
        check_case("change-owner-1", &[], |game, config, case| {
            let config = perl_config(config);
            let got: Vec<String> = (0..case.requests.len())
                .map(|n| {
                    let r = change_owner(
                        game,
                        &config,
                        perl::int(&case.form(n, "ISLANDID")),
                        &case.form(n, "OLDPASS"),
                        &case.form(n, "OWNERNAME"),
                    );
                    match r {
                        Ok(()) => MSG_CHANGED.to_string(),
                        Err(e) => e.to_string(),
                    }
                })
                .collect();
            let wrong = "パスワードが違います";
            assert_eq!(
                got,
                [
                    wrong,
                    MSG_CHANGED,
                    MSG_CHANGED,
                    MSG_CHANGED,
                    MSG_CHANGED,
                    wrong
                ]
            );
        });
    }

    #[test]
    fn admin_passwords_disabled_by_default() {
        let config = GameConfig::default();
        let mut game = GameState::new_game(0, &config);
        assert_eq!(
            change_info(&mut game, &config, 1, &ChangeInput::default()),
            Err(ActionError::NoSuchIsland)
        );
        let mut island = Island::blank(1, "a", &config);
        island.password = hash_password("p");
        game.world.islands.push(island);
        // 未設定 (None) の管理用パスワードは空のパスワードとも一致しない
        assert_eq!(
            change_info(&mut game, &config, 1, &ChangeInput::default()),
            Err(ActionError::WrongPassword)
        );
    }
}
