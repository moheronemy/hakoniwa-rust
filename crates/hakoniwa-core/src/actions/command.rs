//! 開発計画の入力 (`commandMain`、hako-map.cgi 98〜527 行)。
//!
//! 計画番号の位置への上書き・挿入・削除、自動入力 (整地・地ならし・浅瀬埋め立て・浅瀬掘削・
//! 伐採・伐採と植林・開発予定・宇宙ステ修復・全消し)、デバッグ用の「いじり」
//! (`$HcomIjiri`、地形やいくつかの値を直接書き換える)、最後に IP 履歴の更新をする。

use rand::RngCore;

use crate::GameConfig;
use crate::model::{GameState, Island, PlannedCommand};
use crate::perl::{self, cgi_text, cut_column};
use crate::tables::{CommandKind, LandKind};
use crate::turn::command::slide_back;
use crate::turn::make_random_point_array;

use super::{ActionError, Request, island_index};

/// 計画の入れ方 (フォームの `COMMANDMODE`)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CommandMode {
    /// `write`: その番号の計画を上書きする
    Write,
    /// `insert`: その番号に挿入する (後ろはずれて、最後の計画は消える)
    Insert,
    /// `delete`: その番号の計画を消す (前に詰めて、最後は「資金繰り」になる)
    Delete,
}

impl CommandMode {
    /// フォームの値から。Perl 版は `/COMMANDMODE=(write|insert|delete)/` なので前方一致で読む。
    /// どれでもなければ (Perl 版では前のマッチの値が残るが) 上書きとする
    pub fn from_form(s: &str) -> Self {
        if s.starts_with("insert") {
            Self::Insert
        } else if s.starts_with("delete") {
            Self::Delete
        } else {
            Self::Write
        }
    }
}

/// 計画入力のフォームの値。数値の欄も受け取った文字列のまま渡す
/// (Perl 版と同じく、比べるときは数値として、保存するときは `%d` で整数にする)
#[derive(Debug, Clone, Copy)]
pub struct CommandInput<'a> {
    /// 計画番号 (`NUMBER`、0 始まり)
    pub number: usize,
    /// `COMMANDMODE`
    pub mode: CommandMode,
    /// 計画の種類 (`COMMAND`)
    pub kind: &'a str,
    /// 数量 (`AMOUNT`)
    pub amount: &'a str,
    /// 目標の島 ID (`TARGETID`)
    pub target: &'a str,
    /// 座標 (`POINTX`, `POINTY`)
    pub x: &'a str,
    pub y: &'a str,
    /// いじりの対象 (`LAMOUNT1`)。地形番号、または負の数で値の種類
    pub lamount1: &'a str,
    /// いじりの値 (`LAMOUNT2`)
    pub lamount2: &'a str,
}

/// 計画入力の結果 (このあとは開発画面を出す)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CommandOutcome {
    /// 「コマンドを登録しました」(上書き・挿入・自動入力)
    Added,
    /// 「コマンドを削除しました」(削除・全消し)
    Deleted,
    /// いじり (Perl 版は何も表示しない)
    Edited,
}

/// `commandMain`: 島 `id` の開発計画を変える。
///
/// 島の持ち主であることは呼び出し側で確かめておく (Perl 版はここでパスワードを照合する)。
/// いじり (`kind` が 60) はデバッグ用で、Perl 版の画面はマスターパスワードのときだけ出す。
/// この関数は種類を確かめないので、サーバー側でマスターパスワードのときだけ受け付けること。
///
/// 自動入力は `makeRandomPointArray` で乱数を使う。最後に接続元
/// ([`Request::remote_addr`]) で IP 履歴 (`ip0`〜`ip9`) を更新する。
///
/// エラー: 島が無い ([`ActionError::NoSuchIsland`])、計画番号が `command_max` 以上、
/// いじりの座標が負で島の外 (Perl 版はここで止まって何も保存しない)
pub fn input_command(
    game: &mut GameState,
    config: &GameConfig,
    req: Request,
    rng: &mut dyn RngCore,
    id: i64,
    input: &CommandInput,
) -> Result<CommandOutcome, ActionError> {
    // Perl 版は島が無いと 0 番目の島を使う。移植版では島が無いことにする
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    let max = config.command_max;
    let number = input.number;
    // Perl 版は範囲外の番号でも配列を伸ばして書き込む (保存されない) か、最後の計画を壊す。
    // フォームからは送られない値なので受け付けない
    if number >= max {
        return Err(ActionError::Rejected("計画番号が範囲外です".into()));
    }

    let kind_s = cgi_text(input.kind);
    let arg_s = cgi_text(input.amount);
    let kind = perl::num(&kind_s);
    let arg = perl::num(&arg_s);
    let island = &mut game.world.islands[n];
    island.commands.resize(max, do_nothing());
    let is = |k: CommandKind| kind == f64::from(k as u16);

    let outcome = if input.mode == CommandMode::Delete {
        slide_front(&mut island.commands, number, max);
        CommandOutcome::Deleted
    } else if is(CommandKind::AutoPrepare) || is(CommandKind::AutoPrepare2) {
        // フル整地、フル地ならし
        let points = make_random_point_array(rng, config.island_size);
        let k = if is(CommandKind::AutoPrepare2) {
            CommandKind::Prepare2
        } else {
            CommandKind::Prepare
        };
        let mut i = 0;
        for &(x, y) in &points {
            if i >= max {
                break;
            }
            if land_is(island, x, y, LandKind::Waste) {
                put(island, number, k, x, y, 0);
                i += 1;
            }
        }
        CommandOutcome::Added
    } else if is(CommandKind::AutoReclaim) || is(CommandKind::AutoDestroy) {
        // 浅瀬埋め立て、浅瀬掘削
        let points = make_random_point_array(rng, config.island_size);
        let k = if is(CommandKind::AutoReclaim) {
            CommandKind::Reclaim
        } else {
            CommandKind::Destroy
        };
        let mut c = 0;
        for &(x, y) in &points {
            if c >= max {
                break;
            }
            if land_is(island, x, y, LandKind::Sea) && value(island, x, y) == 1 {
                put(island, number, k, x, y, 0);
                c += 1;
            }
        }
        CommandOutcome::Added
    } else if is(CommandKind::AutoSellTree) || is(CommandKind::AutoForestry) {
        // 伐採 (と植林)。数量 × 200 本より多い森だけ
        let points = make_random_point_array(rng, config.island_size);
        let plant = is(CommandKind::AutoForestry);
        let mut c = 0;
        for &(x, y) in &points {
            if c + 1 >= max {
                break;
            }
            if land_is(island, x, y, LandKind::Forest) && value(island, x, y) as f64 > arg * 2.0 {
                if plant {
                    put(island, number, CommandKind::Plant, x, y, 0);
                }
                put(island, number, CommandKind::SellTree, x, y, 0);
                c += 2;
            }
        }
        CommandOutcome::Added
    } else if is(CommandKind::AutoYoyaku) {
        // 開発予定 (平地すべて)
        let points = make_random_point_array(rng, config.island_size);
        let mut c = 0;
        for &(x, y) in &points {
            if c >= max {
                break;
            }
            if land_is(island, x, y, LandKind::Plains) {
                put(island, number, CommandKind::Yoyaku, x, y, 0);
                c += 1;
            }
        }
        CommandOutcome::Added
    } else if is(CommandKind::AutoUchuste) {
        // 宇宙ステ修復 (人工衛星メンテを数量の回数)
        let times = if arg >= max as f64 || arg == 0.0 {
            1.0
        } else {
            arg
        };
        let mut i = 0.0;
        while i < times {
            // 座標は未定義の $x, $y なので 0 (Perl 版のまま)
            put(island, number, CommandKind::Eiseimente, 0, 0, 99);
            i += 1.0;
        }
        CommandOutcome::Added
    } else if is(CommandKind::AutoDelete) {
        // 全消し (その番号から後ろ)
        for _ in 0..max {
            slide_front(&mut island.commands, number, max);
        }
        CommandOutcome::Deleted
    } else if is(CommandKind::Ijiri) {
        ijiri(island, config, input, arg)?;
        CommandOutcome::Edited
    } else {
        if input.mode == CommandMode::Insert {
            slide_back(&mut island.commands, number);
        }
        island.commands[number] = PlannedCommand {
            kind: perl::trunc(kind).clamp(0, i64::from(u16::MAX)) as u16,
            target: perl::trunc(perl::num(&cgi_text(input.target))),
            x: perl::trunc(perl::num(&cgi_text(input.x))),
            y: perl::trunc(perl::num(&cgi_text(input.y))),
            arg: perl::trunc(arg),
        };
        CommandOutcome::Added
    };

    update_ip_history(island, req.remote_addr);
    Ok(outcome)
}

fn do_nothing() -> PlannedCommand {
    PlannedCommand {
        kind: CommandKind::DoNothing as u16,
        ..Default::default()
    }
}

/// `slideFront($command, $number)`: `number` 番目を消して前に詰め、最後を「資金繰り」にする
fn slide_front(commands: &mut Vec<PlannedCommand>, number: usize, max: usize) {
    if number < commands.len() {
        commands.remove(number);
    }
    commands.resize(max, do_nothing());
    commands[max - 1] = do_nothing();
}

/// 自動入力の 1 件: `slideBack` してから `number` 番目に入れる
fn put(island: &mut Island, number: usize, kind: CommandKind, x: usize, y: usize, arg: i64) {
    slide_back(&mut island.commands, number);
    island.commands[number] = PlannedCommand {
        kind: kind as u16,
        target: 0,
        x: x as i64,
        y: y as i64,
        arg,
    };
}

fn land_is(island: &Island, x: usize, y: usize, kind: LandKind) -> bool {
    island.map.get(x, y).is_some_and(|c| c.kind == kind as u8)
}

fn value(island: &Island, x: usize, y: usize) -> i64 {
    island.map.get(x, y).map_or(0, |c| c.value)
}

/// `/^([0-9]*),...$/` (`n` 欄) の結果を文字列のまま。合わなければすべて空
/// (この画面より前に成功したマッチが無いので `$1`.. は未定義)
fn digit_fields(s: &str, n: usize) -> Vec<String> {
    let parts: Vec<&str> = s.split(',').collect();
    if parts.len() == n && parts.iter().all(|p| p.bytes().all(|b| b.is_ascii_digit())) {
        parts.into_iter().map(str::to_string).collect()
    } else {
        vec![String::new(); n]
    }
}

/// `n` 欄の数字の複合値の `index` 番目を `value` にする
fn replace_field(s: &str, n: usize, index: usize, value: &str) -> String {
    let mut f = digit_fields(s, n);
    f[index] = value.to_string();
    f.join(",")
}

/// いじり (`$HcomIjiri`)
fn ijiri(
    island: &mut Island,
    config: &GameConfig,
    input: &CommandInput,
    arg: f64,
) -> Result<(), ActionError> {
    let l1 = perl::num(&cgi_text(input.lamount1));
    let mut l2 = cut_column(&cgi_text(input.lamount2), 40);
    // if($lamount2 == '') { $lamount2 = 0; } (数値として 0 なら "0")
    if perl::num(&l2) == 0.0 {
        l2 = "0".into();
    }
    let l2n = perl::num(&l2);
    let eis = |island: &mut Island, i: usize, v: &str| island.eis[i] = perl::int(v);
    // 負の整数なら値の種類、それ以外は地形番号
    let code = if l1.fract() == 0.0 && (-18.0..=-1.0).contains(&l1) {
        l1 as i64
    } else {
        0
    };
    match code {
        -1 => island.eisei_raw[2] = replace_field(&island.eisei_raw[2], 7, 5, &l2),
        -2 => island.eis[6] = perl::trunc(l2n * 100.0 + 99.0),
        -3 => island.totoyoso2 = l2,
        -4 => eis(island, 5, &l2),
        -5 => eis(island, 4, &l2),
        -6 => eis(island, 3, &l2),
        -7 => eis(island, 2, &l2),
        -8 => eis(island, 1, &l2),
        -9 => eis(island, 0, &l2),
        -10 => island.etc_raw[3] = replace_field(&island.etc_raw[3], 7, 1, &l2),
        -11 => {
            if l2n > 15.0 {
                l2 = "15".into();
            }
            island.eisei_raw[2] = replace_field(&island.eisei_raw[2], 7, 0, &l2);
        }
        -12 => island.eisei_raw[2] = replace_field(&island.eisei_raw[2], 7, 1, &l2),
        -13 => island.eisei_raw[2] = replace_field(&island.eisei_raw[2], 7, 2, &l2),
        -14 => island.eisei_raw[2] = replace_field(&island.eisei_raw[2], 7, 3, &l2),
        -15 => {
            // etc6 の 31 欄。値は文字列のまま扱う ("007"++ は "008")
            if l2n > 30.0 {
                l2 = "30".into();
            }
            if (24.0..=27.0).contains(&perl::num(&l2)) && perl::num(&l2).fract() == 0.0 {
                l2 = "7".into();
            }
            let mut z = digit_fields(&island.etc_raw[1], 31);
            // $z->{"$lamount2"}: キーが "0".."30" と同じ文字列のときだけ欄に当たる
            let key = (0..31).find(|i| i.to_string() == l2);
            if arg == 1.0 {
                for (i, v) in z.iter_mut().enumerate() {
                    if !(24..28).contains(&i) {
                        *v = perl::digits_inc(v);
                    }
                }
            } else if arg > 1.0 {
                if let Some(k) = key {
                    z[k] = perl::num_to_string(perl::num(&z[k]) + arg);
                }
            } else if let Some(k) = key {
                z[k] = perl::digits_inc(&z[k]);
            }
            island.etc_raw[1] = z.join(",");
        }
        -18..=-16 => {
            let mut f = digit_fields(&island.eisei_raw[1], 11);
            if perl::num(&f[10]) == 0.0 {
                f[10] = "16".into();
            }
            f[(-16 - code) as usize] = l2;
            island.eisei_raw[1] = f.join(",");
        }
        _ => {
            // 地形を直接書き換える (%02x%03x で保存されるので整数にする)
            let kind = perl::trunc(l1).clamp(0, 255) as u8;
            let v = if l2n > 4000.0 { 4000 } else { perl::trunc(l2n) };
            let size = config.island_size;
            if arg == 1.0 {
                for c in island.map.cells_mut().iter_mut() {
                    c.kind = kind;
                    c.value = v;
                }
            } else {
                // $land->[$x][$y]: 負の添字は後ろから数える。島の外の行 (x が大きい) は
                // 空の配列が作られるので、そこへの負の添字や、島の外に出る負の添字では
                // Perl 版が止まって何も保存しない
                let outside = || ActionError::Rejected("座標が島の外です".into());
                let index = |s: &str, len: usize| -> Result<i64, ActionError> {
                    let mut i = perl::trunc(perl::num(&cgi_text(s)));
                    if i < 0 {
                        i += len as i64;
                        if i < 0 {
                            return Err(outside());
                        }
                    }
                    Ok(i)
                };
                let x = index(input.x, size)?;
                let row = if x < size as i64 { size } else { 0 };
                let y = index(input.y, row)?;
                if let Some(c) = island.map.get_mut(x as usize, y as usize) {
                    c.kind = kind;
                    c.value = v;
                }
            }
        }
    }
    Ok(())
}

/// IP 履歴の更新 (commandMain の最後)
fn update_ip_history(island: &mut Island, speaker: &str) {
    let ip = &mut island.ip;
    if ip[0] == "0" || ip[0].is_empty() {
        for v in ip.iter_mut().take(6) {
            *v = speaker.to_string();
        }
        ip[6] = "0".into();
        ip[7] = "0".into();
        island.ip_counters = [0, 0];
    }
    // != は数値比較なので、"10.0.0.1" と "10.0.0.2" は同じ (10.0) になる (Perl 版のまま)
    if perl::num(&island.ip[5]) != perl::num(speaker) {
        let ip = &mut island.ip;
        for i in 1..5 {
            ip[i] = ip[i + 1].clone();
        }
        ip[5] = speaker.to_string();
        ip[6] = "0".into();
        ip[7] = "0".into();
        island.ip_counters[0] += 1;
        island.ip_counters[1] += 1;
    }
}

#[cfg(test)]
mod tests {
    use super::super::password::check_password;
    use super::super::perl_compat_tests::{Case, check_case};
    use super::*;

    /// フォームの `CommandButton<id>` から島 ID を取る
    fn button_id(case: &Case, n: usize, prefix: &str) -> i64 {
        case.requests[n]["form"]
            .as_object()
            .unwrap()
            .keys()
            .find_map(|k| k.strip_prefix(prefix))
            .unwrap()
            .parse()
            .unwrap()
    }

    fn run(name: &str) {
        check_case(name, &[], |game, config, case| {
            for n in 0..case.requests.len() {
                let id = button_id(case, n, "CommandButton");
                let island = game.world.island_by_id(id).unwrap();
                if !check_password(config, &island.password, &case.form(n, "PASSWORD")) {
                    continue;
                }
                let input = CommandInput {
                    number: perl::int(&case.form(n, "NUMBER")) as usize,
                    mode: CommandMode::from_form(&case.form(n, "COMMANDMODE")),
                    kind: &case.form(n, "COMMAND"),
                    amount: &case.form(n, "AMOUNT"),
                    target: &case.form(n, "TARGETID"),
                    x: &case.form(n, "POINTX"),
                    y: &case.form(n, "POINTY"),
                    lamount1: &case.form(n, "LAMOUNT1"),
                    lamount2: &case.form(n, "LAMOUNT2"),
                };
                let addr = case.addr(n);
                let req = Request {
                    now: case.now,
                    remote_addr: &addr,
                };
                input_command(game, config, req, &mut case.rng, id, &input).unwrap();
            }
        });
    }

    #[test]
    fn write_insert_delete_match_perl() {
        run("command-write");
    }

    #[test]
    fn auto_input_matches_perl() {
        run("command-auto");
    }

    #[test]
    fn ijiri_matches_perl() {
        run("command-ijiri");
    }

    #[test]
    fn errors() {
        let config = GameConfig::default();
        let mut game = GameState::new_game(0, &config);
        game.world.islands.push(Island::blank(1, "テスト", &config));
        let req = Request {
            now: 0,
            remote_addr: "10.0.0.1",
        };
        let mut input = CommandInput {
            number: 0,
            mode: CommandMode::Write,
            kind: "60",
            amount: "0",
            target: "0",
            x: "0",
            y: "-13",
            lamount1: "3",
            lamount2: "1",
        };
        let mut rng = rand::rngs::mock::StepRng::new(0, 0);
        let before = game.clone();
        assert_eq!(
            input_command(&mut game, &config, req, &mut rng, 2, &input),
            Err(ActionError::NoSuchIsland)
        );
        assert!(matches!(
            input_command(&mut game, &config, req, &mut rng, 1, &input),
            Err(ActionError::Rejected(_))
        ));
        input.y = "0";
        input.number = 40;
        assert!(matches!(
            input_command(&mut game, &config, req, &mut rng, 1, &input),
            Err(ActionError::Rejected(_))
        ));
        assert_eq!(game, before);
        input.number = 39;
        assert_eq!(
            input_command(&mut game, &config, req, &mut rng, 1, &input),
            Ok(CommandOutcome::Edited)
        );
        assert_eq!(game.world.islands[0].map.get(0, 0).unwrap().kind, 3);
    }
}
