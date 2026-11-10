//! 建設系 (植林・農場・発電所・コンデンサ・食物研究所・牧場・大学・工場・ミサイル基地・記念碑・ハリボテ・怪獣購入・遊園地・動物園・地雷・養殖場・野球場・海あみゅ・ニュータウン・リゾート地・開発予定・役所・倉庫・電車・防衛施設)。
//!
//! Perl 版 `hako-turn.cgi` の doCommand の 2325〜3327 行目 (「地上建設系」の分岐)。
//! 予定地が建設できる地形かを確かめ、計画ごとに分岐し、最後に費用を引いて
//! 回数付きの計画を戻す。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 怪獣購入は doCommand の局所変数 `$kind` (計画番号) に怪獣の種類を代入する。
//!   最後の「回数付きなら計画を戻す」はその値で判定するので、種類 12 (= 農場整備の番号)
//!   の怪獣を数量 2 以上で買うと、農場整備の計画が先頭に入る。
//! - 動物園 (動物園の上): 怪獣を逃がすと費用は引かれず、計画も 0 を返す (ターンを使わない)。
//!   逃がす怪獣がいなければ何もログを出さない。
//! - 動物園の新設: 動物の入荷ループの条件 `random(5) != 0 || $first == 1` は、1 回目も
//!   `random(5)` を先に引く。
//! - 牧場の上の「牧場建設・家畜販売」、倉庫の引き出し、大学の切り替え (4/96/97/98/95)、
//!   開発予定地は費用を引かずに 0 を返す (ターンを使わない)。
//! - 食料倉庫は費用が負 (食料) なので、最後の `money -= $cost` で資金が増える。
//! - 倉庫・食料倉庫の新設は、予定地の元の値から `$seq` を計算して使う。
//! - 記念碑の発射は `$lovePeace` なら自分の島の基地・海底基地・記念碑をすべて壊し、
//!   資金を 0 にしてから費用を引く (資金が負になる)。
//! - 記念碑の季節限定の番号は実行した時刻の月日で決まる。12 月 < 月 < 3 月 は
//!   成り立たないので 92 番は建てられない。
//! - 大学 (6 → 95) は資金不足のログを出して 0 を返すことがある。大学の建設後、
//!   文部科学省があれば数量で種類を選び直せる (`$arg == 0` の判定は届かない)。

use std::ops::ControlFlow;

use crate::land::{count_around, land_name};
use crate::log::tags::{self, wrap};
use crate::model::{Island, PlannedCommand};
use crate::perl::trunc;
use crate::tables::{CommandKind as C, LandKind as L, MONSTERS};
use crate::turn::hex::monster::wide_damage;
use crate::turn::hex::town::{set, set_value};
use crate::turn::{TurnContext, monster_spec};

use super::{CmdRun, cmsg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$mKind` (動物園の新設で入荷した動物の種類)。ほかの計画は `my` の `$mKind` を使う
    pub m_kind: i64,
    /// `$nigekaiju`, `$nigeflag` (動物園の上の動物園建設で逃がす怪獣)
    pub nigekaiju: i64,
    pub nigeflag: i64,
    /// `$seq`, `$choki`, `$kibo` (倉庫の計算)。採掘場・倉庫の処理も同じ変数に代入する
    pub seq: i64,
    pub choki: i64,
    pub kibo: i64,
    /// `$s10b` (大学建設で選べる種類の数)
    pub s10b: i64,
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {
    /// `$island->{'bigmissile'}` (記念碑の発射の回数)。doIslandProcess が読む
    pub bigmissile: i64,
}

/// `return 0` で抜けるなら `Break`、共通の後処理 (費用を引く) に進むなら `Continue`
type Step = ControlFlow<()>;
const TAIL: Step = ControlFlow::Continue(());
const STOP: Step = ControlFlow::Break(());

const fn k(l: L) -> u8 {
    l as u8
}

fn is(kind: u8, l: L) -> bool {
    kind == l as u8
}

/// 予定地がこの計画で建設できる地形か (2360〜2404 行目)
fn suitable(c: &CmdRun, kind: C) -> bool {
    let lk = c.land_kind;
    let lv = c.lv;
    let Some(land) = L::from_u8(lk) else {
        return false;
    };
    // ($landKind == $HlandMinato && $kind == $HcomMinato) は、この分岐には港開発が来ないので成り立たない
    match land {
        L::Plains | L::Plains2 | L::Town => true,
        L::Park => kind == C::Park,
        L::Zoo => kind == C::Zoo,
        L::Ice => kind == C::Park,
        L::Umiamu => kind == C::Umiamu,
        L::Sea => (lv == 0 && kind == C::Umiamu) || (lv == 1 && kind == C::Nursery),
        L::Monument => kind == C::Monument,
        L::Farm => kind == C::Farm,
        L::EneAt => kind == C::EneAt,
        L::EneFw => kind == C::EneFw,
        L::EneWt => kind == C::EneWt,
        L::EneWd => kind == C::EneWd,
        L::EneBo => kind == C::EneBo,
        L::EneSo => kind == C::EneSo,
        L::EneCs => kind == C::EneCs,
        L::Farmchi | L::Farmpic | L::Farmcow => kind == C::Farmcpc,
        L::College => kind == C::College || ((77..=80).contains(&lv) && kind == C::Yakusho),
        L::Foodim => kind == C::Foodim,
        L::Factory => kind == C::Factory,
        L::Nursery => kind == C::Nursery,
        L::Kura => kind == C::Kura || kind == C::Kura2,
        L::Kuraf => kind == C::Kuraf || kind == C::Kura2,
        L::Train => lv == 0 && kind == C::Train,
        L::Defence => kind == C::Dbase,
        _ => false,
    }
}

/// 地上建設系の計画 (植林〜防衛施設)
pub(super) fn build(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let kind = c.command_kind().expect("dispatched by kind");
    let (id, turn) = (islands[idx].id, ctx.turn);

    if !suitable(c, kind) {
        // 不適当な地形
        let island = &islands[idx];
        ctx.log.out(
            turn,
            cmsg::land_fail(&island.name, c.com_name, &c.land_name, &c.point),
            Some(id),
            None,
        );
        return false;
    }

    // 予定地。計画の座標は 0 以上だが島の大きさ以上のことがあり、そこは海 (値 0) として
    // 読まれる (海あみゅは建設できる)。Perl 版はそこに書き込んでも保存されないので、
    // 移植版では書き込みを捨てる (島の外の座標を渡すと set/set_value は何もしない)
    let (x, y) = c.cell(&islands[idx]).unwrap_or((usize::MAX, usize::MAX));

    let step = match kind {
        C::Plant => {
            let island = &mut islands[idx];
            set(island, x, y, L::Forest, 1);
            pb_suc(ctx, island, c);
            TAIL
        }
        C::Monbuy | C::Monbuyt => monbuy(ctx, &mut islands[idx], c, x, y, kind),
        C::Base => {
            let island = &mut islands[idx];
            if no_ene(ctx, island, c) {
                return false;
            }
            set(island, x, y, L::Base, 0);
            pb_suc(ctx, island, c);
            TAIL
        }
        C::Haribote => {
            let island = &mut islands[idx];
            set(island, x, y, L::Haribote, 0);
            // logHariSuc: 本当の計画名は機密ログ、ほかの島には防衛施設建設に見せる
            ctx.log.secret(
                turn,
                cmsg::land_suc(&island.name, c.com_name, &c.point),
                Some(id),
                None,
            );
            ctx.log.out(
                turn,
                cmsg::land_suc(&island.name, C::Dbase.name(), &c.point),
                Some(id),
                None,
            );
            TAIL
        }
        C::Park => park(ctx, &mut islands[idx], c, x, y),
        C::Zoo => zoo(ctx, &mut islands[idx], c, x, y),
        C::Mine => {
            let island = &mut islands[idx];
            if c.arg == 0 {
                c.arg = 1;
            } else if c.arg > 9 {
                c.arg = 9;
            }
            c.arg = c.arg.min(trunc(island.money as f64 / c.cost));
            c.cost *= c.arg as f64;
            set(island, x, y, L::Mine, c.arg);
            pb_suc(ctx, island, c);
            TAIL
        }
        C::Conden => {
            let island = &mut islands[idx];
            if c.arg == 0 {
                c.arg = 1;
            } else if c.arg >= 2 {
                c.arg = 2;
            }
            c.arg = c.arg.min(trunc(island.money as f64 / c.cost));
            c.cost *= c.arg as f64;
            if c.arg == 1 {
                set(island, x, y, L::Conden, 0);
            } else if c.arg == 2 {
                set(island, x, y, L::Conden2, 0);
            }
            set_value(island, x, y, 0);
            land_suc(ctx, island, c);
            TAIL
        }
        C::Train => {
            let island = &mut islands[idx];
            if no_ene(ctx, island, c) {
                return false;
            }
            if c.arg > 9 {
                c.arg = 0;
            }
            let on_train = is(c.land_kind, L::Train) && c.lv == 0;
            if on_train && c.arg == 1 {
                set_value(island, x, y, 10);
            } else if on_train && c.arg == 2 {
                set_value(island, x, y, 20);
            } else {
                set(island, x, y, L::Train, c.arg);
            }
            land_suc(ctx, island, c);
            TAIL
        }
        C::Kura => kura(ctx, &mut islands[idx], c, x, y),
        C::Kuraf => kuraf(ctx, &mut islands[idx], c, x, y),
        C::Kura2 => kura2(ctx, &mut islands[idx], c, x, y),
        C::Yoyaku => {
            let island = &mut islands[idx];
            let g = &mut ctx.globals.command;
            g.jikkouarg += 1;
            g.jikkouarg = g.jikkouarg.min(trunc(island.money as f64 / c.cost));
            c.cost *= g.jikkouarg as f64;
            c.cost *= g.jikkouarg as f64;
            set(island, x, y, L::Plains2, 0);
            land_suc(ctx, island, c);
            // 費用は引かれない (Perl 版のまま)
            STOP
        }
        C::Nursery => {
            let island = &mut islands[idx];
            if is(c.land_kind, L::Nursery) {
                add_capped(island, x, y, 5, 100);
            } else if is(c.land_kind, L::Sea) && c.lv == 1 {
                set(island, x, y, L::Nursery, 20);
            } else {
                land_fail(ctx, island, c);
                return false;
            }
            land_suc(ctx, island, c);
            TAIL
        }
        C::Yakusho => yakusho(ctx, &mut islands[idx], c, x, y),
        C::Kyujo | C::Rizort => {
            let island = &mut islands[idx];
            if no_ene(ctx, island, c) {
                return false;
            }
            if kind == C::Kyujo {
                set(island, x, y, L::Kyujo, 0);
            } else {
                set(island, x, y, L::Rizort, 1);
            }
            land_suc(ctx, island, c);
            TAIL
        }
        C::Newtown => {
            let island = &mut islands[idx];
            set(island, x, y, L::Newtown, 1);
            land_suc(ctx, island, c);
            TAIL
        }
        C::Umiamu => {
            let island = &mut islands[idx];
            if no_ene(ctx, island, c) {
                return false;
            }
            if is(c.land_kind, L::Umiamu) {
                add_capped(island, x, y, 30, 1000);
            } else if is(c.land_kind, L::Sea) && c.lv == 0 {
                set(island, x, y, L::Umiamu, 50);
            } else {
                land_fail(ctx, island, c);
                return false;
            }
            land_suc(ctx, island, c);
            TAIL
        }
        C::Farm => grow(ctx, &mut islands[idx], c, x, y, L::Farm, 2, 50, 10),
        C::EneAt => grow(ctx, &mut islands[idx], c, x, y, L::EneAt, 30, 1500, 50),
        C::EneFw | C::EneWt | C::EneWd | C::EneBo => {
            let island = &mut islands[idx];
            let (around_kinds, around_name): (&[L], &str) = match kind {
                C::EneFw => (
                    &[
                        L::Sea,
                        L::Oil,
                        L::Ice,
                        L::Sbase,
                        L::Fune,
                        L::Frocity,
                        L::Nursery,
                        L::Umiamu,
                        L::Seatown,
                        L::Umishuto,
                        L::Seacity,
                    ],
                    "海",
                ),
                C::EneWt => (&[L::Mountain, L::Gold], "山"),
                C::EneWd => (&[L::Plains, L::Plains2], "平地"),
                _ => (&[L::Foodim], "食物研究所"),
            };
            let n: i64 = around_kinds
                .iter()
                .map(|&l| count_around(&island.map, c.x, c.y, l, 7))
                .sum();
            if n == 0 {
                ctx.log.out(
                    turn,
                    cmsg::no_land_arounde(&island.name, c.com_name, &c.point, around_name),
                    Some(id),
                    None,
                );
                return false;
            }
            let (land, add, max, first) = match kind {
                C::EneFw => (L::EneFw, 30, 500, 20),
                C::EneWt => (L::EneWt, 15, 250, 10),
                C::EneWd => (L::EneWd, 25, 150, 25),
                _ => (L::EneBo, 50, 2000, 100),
            };
            grow(ctx, island, c, x, y, land, add, max, first)
        }
        C::EneCs => {
            let island = &mut islands[idx];
            if island.eis[6] == 0 {
                ctx.log.out(
                    turn,
                    nes_eisei(&island.name, c.com_name),
                    Some(id),
                    None,
                );
                return false;
            }
            grow(ctx, island, c, x, y, L::EneCs, 200, 4000, 400)
        }
        C::EneSo => grow(ctx, &mut islands[idx], c, x, y, L::EneSo, 1000, 1000, 1000),
        C::EneNF => {
            let island = &mut islands[idx];
            let mut m = c.scope.clone();
            let v = ctx.globals.hex.etc9.assign(m.fields::<7>(&island.etc_raw[4]));
            // ($co7, $magicf, $magici, $magica, $magicw, $magicl, $magicd)
            let (magica, magicl) = (v[3], v[5]);
            if magica != magicl
                || magicl == 0
                || island.scratch.con99 > 0
                || island.scratch.co77 == 0
            {
                ctx.log.out(
                    turn,
                    eisei_fail(&island.name, c.com_name),
                    Some(id),
                    None,
                );
                // 広域被害ルーチン
                wide_damage(ctx, island, c.x, c.y);
                return false;
            }
            set(island, x, y, L::Conden4, 99);
            land_suc(ctx, island, c);
            TAIL
        }
        C::Foodim => grow(ctx, &mut islands[idx], c, x, y, L::Foodim, 10, 500, 30),
        C::College => college(ctx, &mut islands[idx], c, x, y),
        C::Farmcpc => farmcpc(ctx, &mut islands[idx], c, x, y),
        C::Factory => grow(ctx, &mut islands[idx], c, x, y, L::Factory, 10, 100, 30),
        C::Dbase => {
            let island = &mut islands[idx];
            if no_ene(ctx, island, c) {
                return false;
            }
            if is(c.land_kind, L::Defence) {
                // 自爆装置セット
                set_value(island, x, y, 1);
                ctx.log.out(
                    turn,
                    bomb_set(&island.name, &c.land_name, &c.point),
                    Some(id),
                    None,
                );
            } else {
                set(island, x, y, L::Defence, 0);
                land_suc(ctx, island, c);
            }
            TAIL
        }
        C::Monument => monument(ctx, islands, idx, c, x, y),
        _ => unreachable!("not a build command"),
    };
    if step.is_break() {
        return false;
    }

    // 金を差し引く (費用は整数なので資金は小数にならない)
    let island = &mut islands[idx];
    island.money -= c.cost as i64;

    // 回数付きなら、コマンドを戻す ($kind は怪獣購入で書き換わっていることがある)
    let repeat = matches!(
        C::from_u16(c.kind),
        Some(
            C::Farm
                | C::Foodim
                | C::Nursery
                | C::EneAt
                | C::EneFw
                | C::EneWt
                | C::EneWd
                | C::EneBo
                | C::EneSo
                | C::EneCs
                | C::Park
                | C::Umiamu
                | C::Factory
        )
    );
    if repeat && c.arg > 1 {
        c.arg -= 1;
        slide_back(&mut island.commands);
        island.commands[0] = PlannedCommand {
            kind: c.kind,
            target: c.target,
            x: c.x,
            y: c.y,
            arg: c.arg,
        };
    }
    true
}

/// `slideBack($comArray, 0)`: 末尾を捨てて先頭を複製する (計画が 1 つしかなければ何もしない)
fn slide_back(commands: &mut Vec<PlannedCommand>) {
    if commands.len() <= 1 {
        // return if $number == $#$command (計画が空のときは Perl 版では $#$command が -1)
        if commands.is_empty() {
            commands.push(PlannedCommand::default());
        }
        return;
    }
    commands.pop();
    let first = commands[0].clone();
    commands.insert(0, first);
}

/// `$island->{'shouhi'} > $island->{'ene'}` なら logMsNoEne を出して `true`
fn no_ene(ctx: &mut TurnContext, island: &Island, c: &CmdRun) -> bool {
    if island.scratch.shouhi > island.scratch.ene {
        ctx.log.out(
            ctx.turn,
            cmsg::ms_no_ene(&island.name, c.com_name),
            Some(island.id),
            None,
        );
        return true;
    }
    false
}

fn land_suc(ctx: &mut TurnContext, island: &Island, c: &CmdRun) {
    ctx.log.out(
        ctx.turn,
        cmsg::land_suc(&island.name, c.com_name, &c.point),
        Some(island.id),
        None,
    );
}

fn land_fail(ctx: &mut TurnContext, island: &Island, c: &CmdRun) {
    ctx.log.out(
        ctx.turn,
        cmsg::land_fail(&island.name, c.com_name, &c.land_name, &c.point),
        Some(island.id),
        None,
    );
}

/// `logPBSuc`: 機密ログに計画、ほかの島には森が増えたように見せる
fn pb_suc(ctx: &mut TurnContext, island: &Island, c: &CmdRun) {
    ctx.log.secret(
        ctx.turn,
        cmsg::land_suc(&island.name, c.com_name, &c.point),
        Some(island.id),
        None,
    );
    ctx.log.out(
        ctx.turn,
        format!(
            "こころなしか、{}の<B>森</B>が増えたようです。",
            wrap(tags::NAME, &format!("{}島", island.name))
        ),
        Some(island.id),
        None,
    );
}

/// 値を `add` 増やして `max` で止める
fn add_capped(island: &mut Island, x: usize, y: usize, add: i64, max: i64) {
    let v = island.map.get(x, y).map_or(0, |c| c.value) + add;
    set_value(island, x, y, v.min(max));
}

/// 農場・工場・発電所など: 同じ地形なら規模を増やし、そうでなければ新しく作る
#[allow(clippy::too_many_arguments)]
fn grow(
    ctx: &mut TurnContext,
    island: &mut Island,
    c: &CmdRun,
    x: usize,
    y: usize,
    land: L,
    add: i64,
    max: i64,
    first: i64,
) -> Step {
    if c.land_kind == k(land) {
        add_capped(island, x, y, add, max);
    } else {
        set(island, x, y, land, first);
    }
    land_suc(ctx, island, c);
    TAIL
}

/// 怪獣購入 (怪獣の種類は doCommand の局所変数 `$kind` に入る)
fn monbuy(
    ctx: &mut TurnContext,
    island: &mut Island,
    c: &mut CmdRun,
    x: usize,
    y: usize,
    kind: C,
) -> Step {
    let m = if kind == C::Monbuy {
        ctx.random(ctx.config.monster.levels[2]) + 1
    } else {
        29
    };
    // $kind (計画番号の局所変数) を怪獣の種類で上書きする (Perl 版のまま)
    c.kind = m as u16;
    let spec = &MONSTERS[m as usize];
    c.lv = (m << 4) + spec.base_hp + ctx.random(spec.hp_range);
    set(island, x, y, L::Monster, c.lv);
    let (_, m_name, _) = monster_spec(c.lv);
    ctx.log.out(
        ctx.turn,
        format!(
            "{}で<B>{m_name}</B>を購入・放置しました。",
            wrap(tags::NAME, &format!("{}島{}", island.name, c.point))
        ),
        Some(island.id),
        None,
    );
    TAIL
}

/// 遊園地
fn park(ctx: &mut TurnContext, island: &mut Island, c: &CmdRun, x: usize, y: usize) -> Step {
    if no_ene(ctx, island, c) {
        return STOP;
    }
    if is(c.land_kind, L::Park) {
        add_capped(island, x, y, 30, 100);
    } else if is(c.land_kind, L::Ice) {
        add_capped(island, x, y, 25, 100);
    } else {
        set(island, x, y, L::Park, 10);
        island.scratch.par += 1;
    }
    land_suc(ctx, island, c);
    TAIL
}

/// 動物園 (動物園の上なら動物を逃がす)
fn zoo(ctx: &mut TurnContext, island: &mut Island, c: &mut CmdRun, x: usize, y: usize) -> Step {
    if c.arg > 30 {
        c.arg = 30;
    }
    if no_ene(ctx, island, c) {
        return STOP;
    }
    let (id, turn) = (island.id, ctx.turn);

    if is(c.land_kind, L::Zoo) {
        // $z0..$z30 と $z->{...} に etc6 を分解する (マッチしなければ直前に成功したマッチの値)
        let mut m = c.scope.clone();
        let z = m.fields::<31>(&island.etc_raw[1]);
        ctx.globals.zoo = z;
        ctx.globals.hex.leisure.z = z;

        let g = &mut ctx.globals.command.build;
        g.nigekaiju = c.arg;
        g.nigeflag = 0;
        let nk = g.nigekaiju;
        // $z->{"$nigekaiju"}: 負の番号のキーは無い (未定義 = 0)
        let zn = |ctx: &TurnContext| {
            usize::try_from(nk)
                .ok()
                .and_then(|i| ctx.globals.hex.leisure.z.get(i).copied())
                .unwrap_or(0)
        };
        if zn(ctx) > 0 {
            let nku = nk as usize;
            let spec = &MONSTERS[nku];
            for i in 1..7 {
                let (sx, sy) = crate::land::around(c.x, c.y, i);
                // ここで doCommand の $landKind と $point も書き換わるが、このあと 0 を返すので使われない
                let Some((sx, sy)) = crate::land::in_island(&island.map, (sx, sy)) else {
                    continue;
                };
                let lk = island.map.get(sx, sy).map_or(0, |c| c.kind);
                let sea_like = [
                    L::Sea,
                    L::Ice,
                    L::Oil,
                    L::Fune,
                    L::Frocity,
                    L::Umiamu,
                    L::Seacity,
                    L::Seatown,
                    L::Monster,
                    L::Zoo,
                    L::Umishuto,
                    L::Sbase,
                ];
                if sea_like.iter().any(|&l| is(lk, l)) {
                    continue;
                }
                if ctx.globals.command.build.nigeflag < 1 {
                    ctx.globals.command.build.nigeflag += 1;
                    ctx.globals.hex.leisure.z[nku] -= 1;
                    // この $kind と $lv は局所変数
                    let lv = ((nk) << 4) + spec.base_hp + ctx.random(spec.hp_range);
                    set(island, sx, sy, L::Monster, lv);
                    let (_, m_name, _) = monster_spec(lv);
                    ctx.log
                        .out(turn, nige2(&island.name, m_name, &c.point), Some(id), None);
                    island.etc_raw[1] = crate::perl::join(&ctx.globals.hex.leisure.z);
                }
            }

            if ctx.globals.command.build.nigeflag < 1 {
                // 陸地が無ければ町系の地形に現れる
                let lv = (nk << 4) + spec.base_hp + ctx.random(spec.hp_range);
                let towns = [
                    L::Town,
                    L::Bigtown,
                    L::Bettown,
                    L::Skycity,
                    L::Umicity,
                    L::Rizort,
                    L::Kajino,
                    L::BigRizort,
                    L::Newtown,
                ];
                let found = ctx.points.iter().copied().find(|&(bx, by)| {
                    island
                        .map
                        .get(bx, by)
                        .is_some_and(|cell| towns.iter().any(|&l| is(cell.kind, l)))
                });
                if let Some((bx, by)) = found {
                    let old = island.map.get(bx, by).map_or(0, |cell| cell.value);
                    let l_name = land_name(k(L::Town), old);
                    set(island, bx, by, L::Monster, lv);
                    ctx.globals.hex.leisure.z[nku] -= 1;
                    island.etc_raw[1] = crate::perl::join(&ctx.globals.hex.leisure.z);
                    let (_, m_name, _) = monster_spec(lv);
                    ctx.log.out(
                        turn,
                        mons_come(&island.name, m_name, &format!("({bx}, {by})"), &l_name),
                        Some(id),
                        None,
                    );
                }
            }
        }
        return STOP;
    }

    // 目的の場所を動物園に
    set(island, x, y, L::Zoo, 10);
    if island.scratch.zoo < 1 {
        let mut first = true;
        // random(5) を先に引く (1 回目も)
        while ctx.random(5) != 0 || first {
            first = false;
            let m_kind = ctx.random(12);
            ctx.globals.command.build.m_kind = m_kind;
            let mut m = c.scope.clone();
            let z = m.fields::<31>(&island.etc_raw[1]);
            ctx.globals.zoo = z;
            ctx.globals.hex.leisure.z = z;
            ctx.globals.hex.leisure.z[m_kind as usize] += 1;
            island.scratch.zoo += 1;
            island.etc_raw[1] = crate::perl::join(&ctx.globals.hex.leisure.z);
        }
    }
    land_suc(ctx, island, c);
    TAIL
}

/// 倉庫
fn kura(ctx: &mut TurnContext, island: &mut Island, c: &mut CmdRun, x: usize, y: usize) -> Step {
    if c.arg == 0 {
        c.arg = 1;
    }
    let g = &mut ctx.globals.command.build;
    g.seq = trunc(c.lv as f64 / 100.0);
    g.choki = c.lv.rem_euclid(100);
    c.arg = c.arg.min(trunc(island.money as f64 / c.cost));
    c.cost *= c.arg as f64;
    if is(c.land_kind, L::Kura) {
        g.choki += c.arg;
        if g.choki > 99 {
            g.choki = 99;
        }
        set_value(island, x, y, g.seq * 100 + g.choki);
    } else {
        // 新設でも元の地形の値から計算した $seq を使う (Perl 版のまま)
        set(island, x, y, L::Kura, g.seq * 100 + c.arg);
    }
    land_suc(ctx, island, c);
    TAIL
}

/// 食料倉庫
fn kuraf(ctx: &mut TurnContext, island: &mut Island, c: &mut CmdRun, x: usize, y: usize) -> Step {
    if c.arg == 0 {
        c.arg = 1;
    } else if c.arg > 9 {
        c.arg = 9;
    }
    let g = &mut ctx.globals.command.build;
    g.choki = trunc(c.lv as f64 / 10.0);
    g.kibo = c.lv.rem_euclid(10);
    c.arg = c.arg.min(trunc(island.food as f64 / -c.cost));
    c.cost *= c.arg as f64;
    if is(c.land_kind, L::Kuraf) {
        g.choki += c.arg;
        let max = 400 - 40 * (9 - g.kibo);
        if g.choki > max {
            g.choki = max;
        }
        set_value(island, x, y, g.choki * 10 + g.kibo);
    } else {
        g.choki = 0;
        g.kibo = 0;
        set(island, x, y, L::Kuraf, c.arg * 10);
    }
    island.food -= 10000 * c.arg;
    land_suc(ctx, island, c);
    TAIL
}

/// 倉庫の引き出し (費用は引かず、ターンも使わない)
fn kura2(ctx: &mut TurnContext, island: &mut Island, c: &mut CmdRun, x: usize, y: usize) -> Step {
    if c.arg == 0 {
        c.arg = 1;
    }
    let g = &mut ctx.globals.command.build;
    g.seq = trunc(c.lv as f64 / 100.0);
    g.choki = c.lv.rem_euclid(100);
    if c.arg > g.choki {
        c.arg = g.choki;
    }
    c.cost *= c.arg as f64;

    if is(c.land_kind, L::Kura) {
        g.choki -= c.arg;
        if g.choki < 0 {
            g.choki = 0;
        }
        set_value(island, x, y, g.seq * 100 + g.choki);
        island.money += 10000 * c.arg;
        land_suc(ctx, island, c);
    } else if is(c.land_kind, L::Kuraf) {
        if c.arg == 0 {
            c.arg = 1;
        } else if c.arg > 9 {
            c.arg = 9;
        }
        g.choki = trunc(c.lv as f64 / 10.0);
        g.kibo = c.lv.rem_euclid(10);
        if c.arg > g.choki {
            c.arg = g.choki;
        }
        c.cost *= c.arg as f64;
        g.choki -= c.arg;
        if g.choki < 0 {
            g.choki = 0;
        }
        set_value(island, x, y, g.choki * 10 + g.kibo);
        island.food += 10000 * c.arg;
        land_suc(ctx, island, c);
    } else {
        // 不適当な地形
        land_fail(ctx, island, c);
    }
    STOP
}

/// 島役所 (大学の上なら文部科学省などに)
fn yakusho(ctx: &mut TurnContext, island: &mut Island, c: &CmdRun, x: usize, y: usize) -> Step {
    let shuto_count = count_around(&island.map, c.x, c.y, L::Shuto, 7)
        + count_around(&island.map, c.x, c.y, L::Umishuto, 7);
    if island.scratch.shu == 0 || shuto_count == 0 {
        ctx.log.out(
            ctx.turn,
            cmsg::jo_fail(&island.name, c.com_name, &c.land_name, &c.point),
            Some(island.id),
            None,
        );
        return STOP;
    }
    let costseisaku = ctx.globals.hex.special.costseisaku;
    let college = is(c.land_kind, L::College);
    if college && c.lv == 77 && costseisaku > 35 {
        set(island, x, y, L::College, 78);
    } else if college && c.lv == 78 && costseisaku > 60 {
        set(island, x, y, L::College, 79);
    } else if college && c.lv == 79 && costseisaku > 110 {
        set(island, x, y, L::College, 80);
    } else if college {
        set(island, x, y, L::College, 77);
    } else {
        set(island, x, y, L::Yakusho, 0);
    }
    land_suc(ctx, island, c);
    TAIL
}

/// 大学
fn college(ctx: &mut TurnContext, island: &mut Island, c: &CmdRun, x: usize, y: usize) -> Step {
    let college = is(c.land_kind, L::College);
    // 種類の切り替え (費用を引かず、ターンも使わない)
    let switch = match c.lv {
        4 => Some(96),
        98 => Some(97),
        96 => Some(4),
        97 => Some(98),
        _ => None,
    };
    if let (true, Some(v)) = (college, switch) {
        set_value(island, x, y, v);
        land_suc(ctx, island, c);
        return STOP;
    }
    if college && c.lv == 6 {
        if island.money < 250_000 {
            ctx.log.out(
                ctx.turn,
                crate::log::msg::no_money(&island.name, c.com_name),
                Some(island.id),
                None,
            );
            return STOP;
        }
        set_value(island, x, y, 95);
        island.money -= 250_000;
    } else if college && c.lv == 95 {
        set_value(island, x, y, 6);
        island.money += 250_000;
        land_suc(ctx, island, c);
        return STOP;
    } else {
        let sc = &island.scratch;
        let no_mascot = sc.co4 == 0 && sc.co99 == 0 && sc.c28 == 0;
        let v = if ctx.random(100) < 30 {
            if ctx.random(100) < 40 { 8 } else { 0 }
        } else if ctx.random(100) < 30 {
            if ctx.random(100) < 30 { 7 } else { 1 }
        } else if ctx.random(100) < 25 {
            6
        } else if ctx.random(100) < 15 {
            2
        } else if ctx.random(100) < 15 {
            3
        } else if ctx.random(100) < 15 {
            if no_mascot {
                island.eisei_raw[2] = "3,5,5,5,0,0,0".into();
            }
            4
        } else {
            5
        };
        set(island, x, y, L::College, v);
    }
    land_suc(ctx, island, c);

    // 文部科学省があれば数量で種類を選べる
    let mut m = c.scope.clone();
    let s = ctx.globals.etc5.assign(m.fields::<31>(&island.etc_raw[0]));
    let s10b = trunc(s[10] as f64 / 5.0) + 1;
    ctx.globals.command.build.s10b = s10b;
    let arg = c.arg;
    if island.scratch.co77 > 0 && arg < 10 && arg != 0 && arg - 1 < s10b {
        // ここで $arg == 0 なら 1 にする判定があるが、届かない
        set_value(island, x, y, arg - 1);
        island.money -= arg * 10000;
        let sc = &island.scratch;
        if arg == 4 && sc.co4 == 0 && sc.co99 == 0 && sc.c28 == 0 {
            island.eisei_raw[2] = "3,5,5,5,0,0,0".into();
        }
    }
    TAIL
}

/// 牧場 (牧場の上なら家畜を売る)
fn farmcpc(
    ctx: &mut TurnContext,
    island: &mut Island,
    c: &mut CmdRun,
    x: usize,
    y: usize,
) -> Step {
    if c.arg >= 4 || c.arg == 0 {
        c.arg = 1;
    }
    let price = match L::from_u8(c.land_kind) {
        Some(L::Farmchi) => Some((L::Farmchi, 10)),
        Some(L::Farmpic) => Some((L::Farmpic, 20)),
        Some(L::Farmcow) => Some((L::Farmcow, 50)),
        _ => None,
    };
    if let Some((land, unit)) = price {
        island.money += c.lv * unit;
        set(island, x, y, land, 1);
        land_suc(ctx, island, c);
        c.cost *= 0.0;
        return STOP;
    }
    match c.arg {
        1 => set(island, x, y, L::Farmchi, 1),
        2 => set(island, x, y, L::Farmpic, 1),
        3 => set(island, x, y, L::Farmcow, 1),
        _ => {}
    }
    // 金を差し引く
    c.arg = c.arg.min(trunc(island.money as f64 / c.cost));
    c.cost *= c.arg as f64;
    land_suc(ctx, island, c);
    TAIL
}

/// 記念碑 (記念碑の上なら発射する)
fn monument(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
    x: usize,
    y: usize,
) -> Step {
    let turn = ctx.turn;
    if !is(c.land_kind, L::Monument) {
        // 目的の場所を記念碑に
        let island = &mut islands[idx];
        set(island, x, y, L::Monument, 0);
        let (mon, mday) = local_month_day();
        let arg = c.arg;
        let keep = (arg == 88 && mon > 2 && mon < 6)
            || (arg == 73 && mon > 2 && mon < 6)
            || (arg == 89 && mon > 5 && mon < 9)
            || (arg == 94 && mon > 5 && mon < 9)
            || (arg == 90 && mon > 8 && mon < 12)
            // 12 月より後で 3 月より前、は成り立たない (Perl 版のまま)
            || (arg == 92 && mon > 11 && mon < 3)
            || (arg == 85 && mon == 12 && mday == 24)
            || (arg == 91 && mon == 12 && mday == 25)
            || (arg == 95 && mon == 12);
        if !keep && arg >= ctx.config.monument_number as i64 {
            c.arg = 0;
        }
        set_value(island, x, y, c.arg);
        land_suc(ctx, island, c);
        return TAIL;
    }

    // ターゲット取得 (ターゲットがすでにない場合は何も言わずに中止)
    let Some(&tn) = ctx.id_to_number.get(&c.target) else {
        return STOP;
    };
    let t_pop = islands.get(tn).map_or(0, |t| t.pop);
    let guard = ctx.config.guard_pop;
    if islands[idx].pop < guard || t_pop < guard {
        let island = &islands[idx];
        ctx.log.out(
            turn,
            cmsg::forbidden(&island.name, c.com_name),
            Some(island.id),
            None,
        );
        return STOP;
    }

    if ctx.config.love_peace {
        let island = &mut islands[idx];
        island.scratch.command.build.bigmissile += 1;
        island.money = 0;
        for &(sx, sy) in &ctx.points {
            let Some(cell) = island.map.get(sx, sy) else {
                continue;
            };
            if cell.kind == k(L::Sbase) {
                set(island, sx, sy, L::Sea, 0);
            } else if cell.kind == k(L::Base) || cell.kind == k(L::Monument) {
                set(island, sx, sy, L::Waste, 0);
            }
        }
        ctx.log.out(
            turn,
            format!(
                "{}は、<B>箱庭連合軍</B>に{}されました。",
                wrap(tags::NAME, &format!("{}島", island.name)),
                wrap(tags::DISASTER, "攻撃")
            ),
            Some(island.id),
            None,
        );
    } else if let Some(t) = islands.get_mut(tn) {
        t.scratch.command.build.bigmissile += 1;
    }

    // その場所は荒地に
    let island = &mut islands[idx];
    set(island, x, y, L::Waste, 0);
    ctx.log.out(
        turn,
        format!(
            "{}の<B>{}</B>が<B>轟音とともに飛び立ちました</B>。",
            wrap(tags::NAME, &format!("{}島{}", island.name, c.point)),
            c.land_name
        ),
        Some(island.id),
        None,
    );
    TAIL
}

/// 実行した時刻の (月, 日)。Perl 版は `localtime(time)` (サーバーの地方時) だが、
/// 移植版はタイムゾーンの情報を持たないので協定世界時で計算する
fn local_month_day() -> (i64, i64) {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs() as i64);
    // 日数から暦日を求める (Howard Hinnant の civil_from_days)
    let z = secs.div_euclid(86_400) + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = if mp < 10 { mp + 3 } else { mp - 9 };
    (month, day)
}

/// `logNige2` (地形名の引数は使われない)
fn nige2(name: &str, m_name: &str, point: &str) -> String {
    format!(
        "{}の<B>動物園</B>から<B>{m_name}</B>を{}させました。",
        wrap(tags::NAME, &format!("{name}島{point}")),
        wrap(tags::DISASTER, "脱走")
    )
}

/// `logMonsCome`
fn mons_come(name: &str, m_name: &str, point: &str, l_name: &str) -> String {
    format!(
        "{}に<B>{m_name}</B>出現！！{}の<B>{l_name}</B>が踏み荒らされました。",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::NAME, point)
    )
}

/// `logNesEisei`
fn nes_eisei(name: &str, com_name: &str) -> String {
    format!(
        "{}で予定されていた{}は、必要な人工衛星がないため中止されました。",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::COM_NAME, com_name)
    )
}

/// `logEiseifail`
fn eisei_fail(name: &str, com_name: &str) -> String {
    let com = wrap(tags::COM_NAME, com_name);
    format!(
        "{}で{com}が行われましたが{com}は{}したようです。",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::DISASTER, "失敗")
    )
}

/// `logBombSet`
fn bomb_set(name: &str, l_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>の<B>自爆装置がセット</B>されました。",
        wrap(tags::NAME, &format!("{name}島{point}"))
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn slide_back_duplicates_the_first_command() {
        let mut v: Vec<PlannedCommand> = (1..=3)
            .map(|k| PlannedCommand {
                kind: k,
                ..Default::default()
            })
            .collect();
        slide_back(&mut v);
        let kinds: Vec<_> = v.iter().map(|c| c.kind).collect();
        assert_eq!(kinds, [1, 1, 2]);
    }
}
