//! 人工衛星 (打ち上げ・修復・破壊砲・レーザー)、ハコオク出品、エサ、食料輸出、資金・食料援助、電力援助、誘致活動。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 資金援助・食料援助・電力援助は目標の島があるかを確かめない。島が無ければ
//!   `$Hislands[undef]` = 先頭の島が相手になる (ログの相手の ID は計画の `$target` のまま)。
//! - 食料輸出・資金援助・食料援助は 0 を返すので、同じターンに次の計画も実行される。
//! - 人工衛星打ち上げは、成功しても失敗しても「数量 × 費用」(資金が足りなければ全額) を払う。
//! - 衛星破壊砲・衛星レーザーのログの相手の島 ID は、hako-turn.cgi のどこでも代入されない
//!   グローバル変数 `$tId` (`HexGlobals::t_id`)。宇宙ステーションが崩壊したログは自分の島の名前で出る。
//! - 衛星レーザーの着弾点は `random(1)` (必ず 0) で決まり、いつも予定地そのもの。
//!   荒地にしたマスに記念碑ができるときは、**自分の島**の同じ座標が記念碑になる。
//! - 電力援助は資金を電力の量だけ減らす。コンデンサへの充電で、満杯にするかどうかを
//!   マスの値ではなく援助した電力の量 (`$value`) と比べる。
//! - 食料輸出の代金 (`$value / 10`) は Perl 版では小数になることがある
//!   (食料が足りずに 10 の倍数でない量を輸出したとき)。保存時に切り捨てられるので
//!   移植版は切り捨てて足す (同じターンのうちにその小数を読む処理は再現しない)。

use crate::land::{land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::{Island, PlannedCommand};
use crate::perl::{Captures, trunc};
use crate::tables::LandKind as L;
use crate::turn::hex::town::{set, set_value};
use crate::turn::{TurnContext, monster_spec};

use super::{CmdRun, cmsg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$auction1`..`$auction3` (ハコオクの出品 3 枠、`auction.dat` の先頭 3 行)。
    /// turnMain の初めに `World::auction_lots` から入れ、最後に戻す。
    /// turnMain の後半 (ハコオクの処理) と doIslandProcess も読み書きする
    pub auction: [String; 3],
    /// `($shuppinN, $avalueN, $ajoutaiN, $topvalueN, $topidN)` (N = 1..3)。
    /// turnMain のハコオクの処理と doIslandProcess も同じ変数に代入する
    pub auction_caps: [Captures<5>; 3],
    /// `$aucland` (出品した地形 × 地形の値)。doIslandProcess の落札処理も使う
    pub aucland: i64,
    /// `($msjotai, $nokotan, $msid)` (`etc7`)。ミサイル・怪獣派遣・doIslandProcess も代入する
    pub etc7: Captures<3>,
    /// 人工衛星打ち上げで払った額 (`$value`)
    pub value: i64,
    /// `$err` (着弾のぶれ)。ミサイル発射も代入する
    pub err: i64,
    /// `$n` (電力援助のコンデンサへの充電量)
    pub n: f64,
    /// `($cstpop, $csten)` (宇宙ステーションの値)。doIslandProcess も代入する
    pub cst: (i64, i64),
    /// `($tcstpop, $tcsten, $tdmg)` (衛星破壊砲で宇宙ステーションを撃ったとき)
    pub tcst: (i64, i64, i64),
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

/// `$land->[$x][$y]` の添字 (負なら末尾から数える)。島の外なら `None`
fn perl_index(island: &Island, x: i64, y: i64) -> Option<(usize, usize)> {
    let size = island.map.size as i64;
    let wrap = |v: i64| {
        let v = if v < 0 { v + size } else { v };
        (0..size).contains(&v).then_some(v as usize)
    };
    Some((wrap(x)?, wrap(y)?))
}

/// 費用を資金から引く。この系統の計画の費用は必ず整数 (切り捨て済みか、割増しが効かない)
fn pay(island: &mut Island, cost: f64) {
    island.money -= cost as i64;
}

/// `slideBack($comArray, 0)` のあと先頭を同じ計画 (数量を 1 減らしたもの) にする
fn repeat_command(island: &mut Island, c: &CmdRun, arg: i64) {
    let command = PlannedCommand {
        kind: c.kind,
        target: c.target,
        x: c.x,
        y: c.y,
        arg,
    };
    // slideBack は計画が 1 つしかなければ何もしない
    if island.commands.len() != 1 {
        island.commands.pop();
        island.commands.insert(0, command);
    } else {
        island.commands[0] = command;
    }
}

/// `$HidToNumber{$target}`。無い島なら `$Hislands[undef]` = 先頭の島 (Perl 版のまま)
fn target_or_first(ctx: &TurnContext, target: i64) -> usize {
    ctx.id_to_number.get(&target).copied().unwrap_or(0)
}

/// 人工衛星の名前 (`eis1`..`eis6`)
const EISEI_NAMES: [&str; 6] = [
    "気象衛星",
    "観測衛星",
    "迎撃衛星",
    "軍事衛星",
    "防衛衛星",
    "イレギュラー",
];

/// オークション出品
pub(super) fn auction(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    let (id, turn) = (island.id, ctx.turn);
    let mut m = c.scope.clone();
    let [auc6a, _, _] = ctx.globals.auc6.assign(m.fields(&island.auction.auc6));

    // 予定地を読み直す (doCommand の冒頭と同じ値)
    let (land_kind, lv) = perl_get(&island.map, c.x, c.y);
    c.land_kind = land_kind;
    c.lv = lv;
    let g = &mut ctx.globals.command.ops;
    g.aucland = i64::from(land_kind) * lv;

    if auc6a != 1 {
        ctx.log.out(
            turn,
            msg::ms_no_ene3(&island.name, c.com_name),
            Some(id),
            None,
        );
        return false;
    }

    let mut shuppin = [0i64; 3];
    for (i, s) in shuppin.iter_mut().enumerate() {
        *s = g.auction_caps[i].assign(m.fields(&g.auction[i]))[0];
    }

    if let Some(i) = shuppin.iter().position(|&s| s == 29) {
        island.auction.auc6 = format!("2,{},{}", c.x, c.y);
        island.auction.auc7 = format!("{}島({}, {})の{}", island.name, c.x, c.y, c.land_name);
        g.auction[i] = format!("30,{id},0,{},{}", c.arg, g.aucland);
        pay(island, c.cost);
        ctx.log.out(
            turn,
            cmsg::land_suc(&island.name, c.com_name, &c.point),
            Some(id),
            None,
        );
        return true;
    }

    ctx.log.out(
        turn,
        msg::ms_no_ene4(&island.name, c.com_name),
        Some(id),
        None,
    );
    false
}

/// エサをあげる
pub(super) fn givefood(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    let (id, turn) = (island.id, ctx.turn);
    let kind = L::from_u8(c.land_kind);
    if kind == Some(L::Monster) {
        let (_, _, hp) = monster_spec(c.lv);
        if hp < 10 {
            c.lv += ctx.random(5);
        }
        // 怪獣が読めたのだから予定地は島の中 (負の座標なら末尾から数えた位置)
        if let Some((x, y)) = perl_index(island, c.x, c.y) {
            set_value(island, x, y, c.lv);
        }
    } else if kind == Some(L::College) && matches!(c.lv, 4 | 96 | 97 | 98) {
        let mut m = c.scope.clone();
        let [mut mshp, mut msap, mut msdp, mut mssp, mswin, msexe, tet] =
            ctx.globals.eisei5.assign(m.fields(&island.eisei_raw[2]));
        if ctx.rand_f64(100.0) < 30.0 {
            msap += 1;
        } else if ctx.rand_f64(100.0) < 30.0 {
            msdp += 1;
        } else if ctx.rand_f64(100.0) < 30.0 {
            mssp += 1;
        } else {
            mshp += 1;
            if mshp > 15 {
                mshp = 15;
            }
        }
        let ms = [mshp, msap, msdp, mssp, mswin, msexe, tet];
        // $mshp などはグローバル変数
        ctx.globals.eisei5.0 = ms;
        island.eisei_raw[2] = crate::perl::join(&ms);
    } else {
        // 不適当な地形
        ctx.log.out(
            turn,
            cmsg::land_fail(&island.name, c.com_name, &c.land_name, &c.point),
            Some(id),
            None,
        );
        return false;
    }
    ctx.log.out(
        turn,
        cmsg::land_suc(&island.name, c.com_name, &c.point),
        Some(id),
        None,
    );

    // 費用は負 (食料)
    island.food += c.cost as i64;
    if c.arg > 1 {
        c.arg -= 1;
        repeat_command(island, c, c.arg);
    }
    true
}

/// 人工衛星打ち上げの条件 (数量ごと): ロケット、技術、失敗判定の乱数の幅と基準、成功時の値
struct Launch {
    roke: i64,
    tech: i64,
    range: i64,
    base: i64,
    value: i64,
}

const LAUNCH: [Launch; 6] = [
    Launch {
        roke: 1,
        tech: 10,
        range: 100,
        base: 70,
        value: 100,
    },
    Launch {
        roke: 1,
        tech: 40,
        range: 100,
        base: 50,
        value: 100,
    },
    Launch {
        roke: 2,
        tech: 100,
        range: 1000,
        base: 600,
        value: 100,
    },
    Launch {
        roke: 3,
        tech: 250,
        range: 1000,
        base: 400,
        value: 100,
    },
    Launch {
        roke: 4,
        tech: 1000,
        range: 1000,
        base: 200,
        value: 100,
    },
    Launch {
        roke: 10,
        tech: 2000,
        range: 10000,
        base: 3000,
        value: 250,
    },
];

/// 人工衛星打ち上げ
pub(super) fn eisei(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    let (id, turn) = (island.id, ctx.turn);
    let name = island.name.clone();

    if island.scratch.shouhi > island.scratch.ene {
        ctx.log
            .out(turn, cmsg::ms_no_ene(&name, c.com_name), Some(id), None);
        return false;
    }

    if c.arg != 99 && (c.arg >= 7 || c.arg == 0) {
        c.arg = 1;
    }
    let m17 = island.scratch.m17;
    let rena = island.owner_stats.rena;

    // 数量 × 費用 (資金が足りなければ全額) を払う
    let pay_launch = |ctx: &mut TurnContext, island: &mut Island, arg: i64| {
        let value = (arg as f64 * c.cost).min(island.money as f64) as i64;
        ctx.globals.command.ops.value = value;
        island.money -= value;
    };

    if (1..=6).contains(&c.arg) {
        let l = &LAUNCH[(c.arg - 1) as usize];
        if m17 < l.roke {
            ctx.log
                .out(turn, cmsg::no_roke(&name, c.com_name), Some(id), None);
            return false;
        }
        if rena < l.tech {
            ctx.log
                .out(turn, cmsg::no_tech(&name, c.com_name), Some(id), None);
            return false;
        }
        if ctx.random(l.range) > l.base + rena {
            ctx.log
                .out(turn, msg::eisei_fail(&name, c.com_name), Some(id), None);
            pay_launch(ctx, island, c.arg);
            return true;
        }
        island.eis[(c.arg - 1) as usize] = l.value;
        ctx.log
            .out(turn, cmsg::land_suc_mini(&name, c.com_name), Some(id), None);
    }
    if c.arg == 99 {
        if island.money < 1_000_000 {
            ctx.log
                .out(turn, msg::no_money(&name, c.com_name), Some(id), None);
            return false;
        }
        if m17 < 10 {
            ctx.log
                .out(turn, cmsg::no_roke(&name, c.com_name), Some(id), None);
            return false;
        }
        if rena < 5000 {
            ctx.log
                .out(turn, cmsg::no_tech(&name, c.com_name), Some(id), None);
            return false;
        }
        if ctx.random(10000) > 3000 + rena {
            ctx.log
                .out(turn, msg::eisei_fail(&name, c.com_name), Some(id), None);
            island.money -= 1_000_000;
            return true;
        }
        island.eis[6] = 124;
        ctx.log
            .out(turn, cmsg::land_suc_mini(&name, c.com_name), Some(id), None);
        island.money -= 1_000_000;
        return true;
    }

    pay_launch(ctx, island, c.arg);
    true
}

/// 人工衛星修復
pub(super) fn eiseimente(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    let (id, turn) = (island.id, ctx.turn);
    let name = island.name.clone();

    if island.scratch.shouhi > island.scratch.ene {
        ctx.log
            .out(turn, cmsg::ms_no_ene(&name, c.com_name), Some(id), None);
        return false;
    }

    if c.arg != 99 && (c.arg >= 6 || c.arg == 0) {
        c.arg = 1;
    }
    if (1..=5).contains(&c.arg) {
        let i = (c.arg - 1) as usize;
        if island.eis[i] >= 1 {
            island.eis[i] = 150;
            ctx.log
                .out(turn, cmsg::land_suc_mini(&name, c.com_name), Some(id), None);
        } else {
            ctx.log
                .out(turn, msg::no_eisei(&name, c.com_name), Some(id), None);
            return false;
        }
    }
    if c.arg == 99 {
        let eis7 = island.eis[6];
        let mut cstpop = trunc(eis7 as f64 / 100.0);
        let mut csten = eis7.rem_euclid(100);
        if csten >= 1 {
            csten += 25;
            if csten > 99 {
                csten = 99;
                cstpop += 100;
            }
            ctx.log
                .out(turn, cmsg::land_suc_mini(&name, c.com_name), Some(id), None);
            island.eis[6] = cstpop * 100 + csten;
        } else {
            ctx.globals.command.ops.cst = (cstpop, csten);
            ctx.log
                .out(turn, msg::no_eisei(&name, c.com_name), Some(id), None);
            return false;
        }
        ctx.globals.command.ops.cst = (cstpop, csten);
    }

    pay(island, c.cost);
    true
}

/// `etc7` の「援助射撃の許可」を確かめる (平和系モードのとき)。許可が無ければ `false`
fn niwaren_ok(ctx: &mut TurnContext, c: &CmdRun, own_etc7: &str, target_id: i64) -> bool {
    let mut m = c.scope.clone();
    let [msjotai, _, msid] = ctx.globals.command.ops.etc7.assign(m.fields(own_etc7));
    !((msjotai != 2 || target_id != msid) && ctx.config.love_peace)
}

/// 衛星破壊砲発射
pub(super) fn eisei_att(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let turn = ctx.turn;
    let (id, name) = (islands[idx].id, islands[idx].name.clone());
    if c.arg != 99 && (c.arg >= 7 || c.arg == 0) {
        c.arg = 1;
    }
    // ターゲット取得
    let Some(tn) = ctx.id_to_number.get(&c.target).copied() else {
        ctx.log
            .out(turn, cmsg::ms_no_target(&name, c.com_name), Some(id), None);
        return false;
    };
    // 事前準備
    let t_name = islands[tn].name.clone();
    let t_eis = islands[tn].eis;
    let t_island_id = islands[tn].id;

    if !niwaren_ok(ctx, c, &islands[idx].etc_raw[2].clone(), t_island_id) {
        ctx.log
            .out(turn, msg::niwaren3(&name, c.com_name), Some(id), None);
        return true;
    }

    // イレギュラーがあれば命中率が高く、無ければ軍事衛星を使う
    let (sat, rates, wear) = if islands[idx].eis[5] >= 1 {
        (5usize, [100, 90, 80, 70, 60, 50], 30)
    } else if islands[idx].eis[3] >= 1 {
        (3usize, [70, 60, 50, 40, 30, 20], 30)
    } else {
        ctx.log
            .out(turn, msg::nes_eisei(&name, c.com_name), Some(id), None);
        return false;
    };
    // 相手の島 ID はどこでも代入されないグローバル変数 $tId (Perl 版のまま)
    let t_id = ctx.globals.hex.t_id;

    if (1..=6).contains(&c.arg) {
        let i = (c.arg - 1) as usize;
        if t_eis[i] >= 1 {
            if ctx.random(100) < rates[i] {
                islands[tn].eis[i] = 0;
                ctx.log.out(
                    turn,
                    msg::eisei_atts(&name, &t_name, c.com_name, EISEI_NAMES[i]),
                    Some(id),
                    t_id,
                );
            } else {
                ctx.log.out(
                    turn,
                    msg::eisei_attf(&name, &t_name, c.com_name, EISEI_NAMES[i]),
                    Some(id),
                    t_id,
                );
            }
        } else {
            ctx.log
                .out(turn, msg::no_eisei(&name, c.com_name), Some(id), None);
            return false;
        }
    }
    if c.arg == 99 {
        let t_eisei7 = t_eis[6];
        if t_eisei7 >= 1 {
            let mut tcstpop = trunc(t_eisei7 as f64 / 100.0);
            let mut tcsten = t_eisei7.rem_euclid(100);
            let mut tdmg = ctx.random(100);
            tcstpop = trunc((tcstpop * tdmg) as f64 / 100.0);
            tcsten = trunc((tcsten * tdmg) as f64 / 100.0);
            islands[tn].eis[6] = tcstpop * 100 + tcsten;
            tdmg = 100 - tdmg;
            ctx.globals.command.ops.tcst = (tcstpop, tcsten, tdmg);
            ctx.log.out(
                turn,
                msg::eisei_attcst(&name, &t_name, c.com_name, "宇宙ステーション", tdmg),
                Some(id),
                t_id,
            );
            if tcsten < tdmg {
                islands[tn].eis[6] = 0;
                // 自分の島の名前で崩壊のログが出る (Perl 版のまま)
                ctx.log.out(
                    turn,
                    msg::eisei_end(&name, "宇宙ステーション"),
                    Some(id),
                    None,
                );
            }
        } else {
            ctx.log
                .out(turn, msg::no_eisei(&name, c.com_name), Some(id), None);
            return false;
        }
    }

    // 衛星の消耗
    let island = &mut islands[idx];
    island.eis[sat] -= wear;
    if island.eis[sat] < 1 {
        island.eis[sat] = 0;
        ctx.log.out(
            turn,
            msg::eisei_end(&name, EISEI_NAMES[sat]),
            Some(id),
            None,
        );
    }
    pay(island, c.cost);
    true
}

/// 衛星レーザー発射
pub(super) fn eisei_lzr(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let turn = ctx.turn;
    let (id, name) = (islands[idx].id, islands[idx].name.clone());
    let Some(tn) = ctx.id_to_number.get(&c.target).copied() else {
        ctx.log
            .out(turn, cmsg::ms_no_target(&name, c.com_name), Some(id), None);
        return false;
    };
    let t_name = islands[tn].name.clone();
    let t_island_id = islands[tn].id;

    if !niwaren_ok(ctx, c, &islands[idx].etc_raw[2].clone(), t_island_id) {
        ctx.log
            .out(turn, msg::niwaren3(&name, c.com_name), Some(id), None);
        return true;
    }

    // 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
    let guard = ctx.config.guard_pop;
    if islands[idx].pop < guard || islands[tn].pop < guard {
        ctx.log
            .out(turn, cmsg::forbidden(&name, c.com_name), Some(id), None);
        return false;
    }

    // 着弾点算出 ($err = 1 なので random(1) は必ず 0、着弾点は予定地そのもの)
    ctx.globals.command.ops.err = 1;
    let r = ctx.random(1) as usize;
    let (tx, ty) = crate::land::around(c.x, c.y, r);

    // 着弾点の地形等算出
    let (t_l, t_lv) = perl_get(&islands[tn].map, tx, ty);
    let t_lname = land_name(t_l, t_lv);

    let (sat, wear) = if islands[idx].eis[5] >= 1 {
        (5usize, 5)
    } else if islands[idx].eis[3] >= 1 {
        (3usize, 10)
    } else {
        ctx.log
            .out(turn, msg::nes_eisei(&name, c.com_name), Some(id), None);
        return false;
    };
    let t_id = ctx.globals.hex.t_id;
    let kind = L::from_u8(t_l);
    let is = |list: &[L]| kind.is_some_and(|k| list.contains(&k));

    if is(&[
        L::Sea,
        L::Waste,
        L::Mountain,
        L::Gold,
        L::Seacity,
        L::Seatown,
        L::Umishuto,
        L::Umiamu,
        L::Sbase,
    ]) {
        ctx.log.out(
            turn,
            msg::lzr_efc(&name, &t_name, &c.point, c.com_name, &t_lname),
            Some(id),
            t_id,
        );
    } else {
        ctx.log.out(
            turn,
            msg::lzr_hit(&name, &t_name, &c.point, c.com_name, &t_lname),
            Some(id),
            t_id,
        );
        // 海でない地形が読めたのだから着弾点は島の中
        let cell = perl_index(&islands[tn], tx, ty);
        if is(&[L::Oil, L::Nursery, L::Frocity, L::Ice, L::Fune]) {
            if let Some((x, y)) = cell {
                set(&mut islands[tn], x, y, L::Sea, 1);
            }
        } else if kind == Some(L::Onsen) {
            if let Some((x, y)) = cell {
                set(&mut islands[tn], x, y, L::Mountain, 0);
            }
        } else {
            if let Some((x, y)) = cell {
                set(&mut islands[tn], x, y, L::Waste, 0);
            }
            if ctx.rand_f64(1000.0) < 100.0 {
                // 記念碑ができるのは自分の島 (Perl 版のまま)
                if let Some((x, y)) = perl_index(&islands[idx], tx, ty) {
                    set(&mut islands[idx], x, y, L::Monument, 79);
                }
            }
        }
    }

    let island = &mut islands[idx];
    island.eis[sat] -= wear;
    if island.eis[sat] < 1 {
        island.eis[sat] = 0;
        ctx.log.out(
            turn,
            msg::eisei_end(&name, EISEI_NAMES[sat]),
            Some(id),
            None,
        );
    }
    pay(island, c.cost);
    true
}

/// 食料輸出
pub(super) fn sell(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    // 輸出量決定
    if c.arg == 0 {
        c.arg = 1;
    }
    let value = (c.arg as f64 * -c.cost).min(island.food as f64) as i64;

    // 輸出ログ
    let amount = format!("{value}{}", ctx.config.units.food);
    ctx.log.out(
        ctx.turn,
        msg::sell(&island.name, c.com_name, &amount),
        Some(island.id),
        None,
    );
    island.food -= value;
    // Perl 版は小数になることがある (保存時に切り捨て)
    island.money += trunc(value as f64 / 10.0);
    false
}

/// 食料援助・資金援助
pub(super) fn aid(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let turn = ctx.turn;
    // ターゲット取得 (無い島なら先頭の島)
    let tn = target_or_first(ctx, c.target);
    let t_name = islands[tn].name.clone();
    let (id, name) = (islands[idx].id, islands[idx].name.clone());

    // 自島の人口が少ないなら、実行は許可されない
    if islands[idx].pop < ctx.config.guard_pop {
        ctx.log
            .out(turn, cmsg::forbidden(&name, c.com_name), Some(id), None);
        return false;
    }

    // 援助量決定
    if c.arg == 0 {
        c.arg = 1;
    }
    let food = c.cost < 0.0;
    let value = if food {
        (c.arg as f64 * -c.cost).min(islands[idx].food as f64) as i64
    } else {
        (c.arg as f64 * c.cost).min(islands[idx].money as f64) as i64
    };
    let unit = if food {
        &ctx.config.units.food
    } else {
        &ctx.config.units.money
    };
    let amount = format!("{value}{unit}");

    // 援助ログ (相手の ID は計画の $target のまま)
    ctx.log.out(
        turn,
        msg::aid(&name, &t_name, c.com_name, &amount),
        Some(id),
        Some(c.target),
    );

    if food {
        islands[idx].food -= value;
        islands[tn].food += value;
    } else {
        islands[idx].money -= value;
        islands[tn].money += value;
    }
    false
}

/// 電力援助
pub(super) fn ene_give(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let turn = ctx.turn;
    let tn = target_or_first(ctx, c.target);
    let t_name = islands[tn].name.clone();
    let (id, name) = (islands[idx].id, islands[idx].name.clone());

    // 援助量決定
    if c.arg == 0 {
        c.arg = 1;
    }
    let value = (c.arg as f64 * c.cost).min(islands[idx].scratch.ene as f64) as i64;
    let amount = format!("{value}万kW");

    // 援助ログ
    ctx.log.out(
        turn,
        msg::aid(&name, &t_name, c.com_name, &amount),
        Some(id),
        Some(c.target),
    );

    // 資金を電力の量だけ減らす (Perl 版のまま)
    islands[idx].money -= value;
    islands[idx].scratch.shouhi += value;
    let t = &mut islands[tn];
    t.scratch.sabun = value as f64;

    if t.scratch.sabun > 0.0 {
        let points = ctx.points.clone();
        for (x, y) in points {
            let Some(cell) = t.map.get(x, y) else {
                continue;
            };
            let kind = cell.kind;
            // 小数部分も含めた値 (Perl 版の $landValue)
            let lv = cell.value as f64 + t.scratch.land_frac.get(&(x, y)).copied().unwrap_or(0.0);
            if kind == L::Conden as u8 && lv < 2000.0 {
                let n = trunc((2000.0 - lv) / 2.0) as f64;
                let n = (n + n).trunc().min(t.scratch.sabun);
                ctx.globals.command.ops.n = n;
                t.scratch.sabun -= n;
                store(t, x, y, lv + n);
                // 満杯にするかは援助した電力の量で決める (Perl 版のまま)
                if value > 2000 {
                    store(t, x, y, 2000.0);
                }
            }
            if kind == L::Conden2 as u8 && lv < 4000.0 {
                let n = trunc((4000.0 - lv) / 10.0) as f64;
                let r = ctx.rand_f64(n);
                let n = (n * 9.0 + r).trunc().min(t.scratch.sabun);
                ctx.globals.command.ops.n = n;
                t.scratch.sabun -= n;
                store(t, x, y, lv + n);
                if value > 4000 {
                    store(t, x, y, 4000.0);
                }
            }
            if kind == L::Conden3 as u8 && lv < 7000.0 {
                let n = trunc((7000.0 - lv) / 2.0) as f64;
                let n = (n + n).trunc().min(t.scratch.sabun);
                ctx.globals.command.ops.n = n;
                t.scratch.sabun -= n / 2.0;
                store(t, x, y, lv + n / 2.0);
                if value > 7000 {
                    store(t, x, y, 7000.0);
                }
            }
            if t.scratch.sabun <= 0.0 {
                break;
            }
        }
    }
    true
}

/// マスの値を書き込む。小数部分は `land_frac` に残す
fn store(island: &mut Island, x: usize, y: usize, v: f64) {
    if let Some(cell) = island.map.get_mut(x, y) {
        cell.value = trunc(v);
    }
    let frac = v - v.trunc();
    if frac == 0.0 {
        island.scratch.land_frac.remove(&(x, y));
    } else {
        island.scratch.land_frac.insert((x, y), frac);
    }
}

/// 誘致活動
pub(super) fn propaganda(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    // logPropaganda は logLandSucmini と同じ文面
    ctx.log.out(
        ctx.turn,
        cmsg::land_suc_mini(&island.name, c.com_name),
        Some(island.id),
        None,
    );
    island.scratch.propaganda = 1;
    pay(island, c.cost);
    if c.arg > 1 {
        c.arg -= 1;
        repeat_command(island, c, c.arg);
    }
    true
}

/// この系統のログの文面
mod msg {
    use super::{tags, wrap};

    pub use crate::log::msg::no_money;

    fn island(name: &str) -> String {
        wrap(tags::NAME, &format!("{name}島"))
    }

    fn com(com_name: &str) -> String {
        wrap(tags::COM_NAME, com_name)
    }

    fn b(s: &str) -> String {
        format!("<B>{s}</B>")
    }

    /// `logMsNoEne3`
    pub fn ms_no_ene3(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は出品権利がないため中止となりました。",
            island(name),
            com(com_name)
        )
    }

    /// `logMsNoEne4`
    pub fn ms_no_ene4(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は出品枠が空いてないため中止となりました。",
            island(name),
            com(com_name)
        )
    }

    /// `logEiseifail`
    pub fn eisei_fail(name: &str, com_name: &str) -> String {
        format!(
            "{}で{}が行われましたが{}は{}したようです。",
            island(name),
            com(com_name),
            com(com_name),
            wrap(tags::DISASTER, "失敗")
        )
    }

    /// `logNoEisei`
    pub fn no_eisei(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、指定の人工衛星がないため中止されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logNesEisei`
    pub fn nes_eisei(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、必要な人工衛星がないため中止されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logEiseiAtts`
    pub fn eisei_atts(name: &str, t_name: &str, com_name: &str, eisei: &str) -> String {
        format!(
            "{}が{}に向けて{}を行い、{}に命中。{}は跡形もなく消し飛びました。",
            island(name),
            island(t_name),
            com(com_name),
            b(eisei),
            b(eisei)
        )
    }

    /// `logEiseiAttf`
    pub fn eisei_attf(name: &str, t_name: &str, com_name: &str, eisei: &str) -> String {
        format!(
            "{}が{}の{}に向けて{}を行いましたが、何にも命中せず宇宙の彼方へと飛び去ってしまいました。。",
            island(name),
            island(t_name),
            b(eisei),
            com(com_name)
        )
    }

    /// `logEiseiAttcst`
    pub fn eisei_attcst(
        name: &str,
        t_name: &str,
        com_name: &str,
        eisei: &str,
        tdmg: i64,
    ) -> String {
        format!(
            "{}が{}に向けて{}を行い、{}に命中。{}の損害を与えました。",
            island(name),
            island(t_name),
            com(com_name),
            b(eisei),
            b(&format!("{tdmg}%"))
        )
    }

    /// `logEiseiEnd`
    pub fn eisei_end(name: &str, eisei: &str) -> String {
        format!(
            "{}の{}は{}したようです！！",
            island(name),
            b(eisei),
            wrap(tags::DISASTER, "崩壊")
        )
    }

    /// `logNiwaren3`
    pub fn niwaren3(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、<B>援助射撃の許可が取れてない</B>ため中止されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logLzrefc` (`$point` は自分の予定地。着弾点 `$tPoint` は使わない)
    pub fn lzr_efc(name: &str, t_name: &str, point: &str, com_name: &str, t_lname: &str) -> String {
        format!(
            "{}が{}地点に向けて{}を行い、{}に命中、{}は暖かくなりました。",
            island(name),
            wrap(tags::NAME, &format!("{t_name}島{point}")),
            com(com_name),
            b(t_lname),
            b(t_lname)
        )
    }

    /// `logLzrhit`
    pub fn lzr_hit(name: &str, t_name: &str, point: &str, com_name: &str, t_lname: &str) -> String {
        format!(
            "{}が{}地点に向けて{}を行い、{}に命中、{}は焼き払われました。",
            island(name),
            wrap(tags::NAME, &format!("{t_name}島{point}")),
            com(com_name),
            b(t_lname),
            b(t_lname)
        )
    }

    /// `logSell` (`amount` は単位付き)
    pub fn sell(name: &str, com_name: &str, amount: &str) -> String {
        format!(
            "{}が{}の{}を行いました。",
            island(name),
            b(amount),
            com(com_name)
        )
    }

    /// `logAid`
    pub fn aid(name: &str, t_name: &str, com_name: &str, amount: &str) -> String {
        format!(
            "{}が{}へ{}の{}を行いました。",
            island(name),
            island(t_name),
            b(amount),
            com(com_name)
        )
    }
}
