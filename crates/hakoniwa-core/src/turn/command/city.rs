//! ハイテク技術誘致・自宅建設・輝ける都市・改装・海底基地・海底都市・防災都市化・現代都市・海底新都市・僕の引越し。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 自宅建設は自宅がすでにあると税率 (`eisei1`) だけ変えて 0 を返す (費用を払わず、次の計画も実行する)。
//! - 僕の引越しは、町の数を「行による位置調整」をして数えるのに、人口を減らすループは
//!   位置調整も範囲の確認もしない (奇数行では別のマスの町が減り、負の座標は反対側の端になる)。
//! - 僕の引越し２は、1 回目で地形を持ち上げて (平地にして) 0 を返し、2 回目で置く。
//!   `stockflag` は置いたあとも 55 のままなので、同じターンの 3 回目以降は同じ地形をまた置ける。
//!   メッキが施されたときは費用を払わずに 1 を返す。
//! - 改装 (野球場・改) の `$sto`.. はグローバル変数 ([`crate::turn::Globals::eisei4`])。
//!   `eisei4` が形式に合わないと、doCommand の `etc5` のマッチの値が入る。
//!
//! `my` を付けずに代入する `$eisei4`, `$seq`, `$choki`, `$kibo`, `$sizekeisu` は、
//! どれも読む前に必ず代入しているので持ち越さない。

use crate::land::{AX, AY, count_around, land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::{Island, PlannedCommand};
use crate::perl::{MatchScope, trunc};
use crate::tables::{HOUSE_LEVELS, LandKind as L};
use crate::turn::TurnContext;
use crate::turn::hex::town::TOWN_KINDS;
use crate::turn::monster_spec;

use super::{CmdRun, cmsg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {
    /// `$island->{'stockflag'}` (僕の引越し２で地形を持ち上げていると 55)
    pub stockflag: i64,
    /// `$island->{'stocklandkind'}` (持ち上げた地形)
    pub stocklandkind: i64,
    /// `$island->{'stocklandvalue'}` (持ち上げた地形の値)
    pub stocklandvalue: i64,
    /// `$island->{'pointb'}` (ログに出す引越し元と先の座標)
    pub pointb: String,
    /// `$island->{'condenmekki'}` (隣に怪獣 14 番がいると 3)
    pub condenmekki: i64,
}

const fn k(l: L) -> u8 {
    l as u8
}

/// `$land->[$x][$y]` の添字。負の添字は反対側の端から数える。大きすぎる添字は島の外 (`None`)
fn perl_cell(island: &Island, x: i64, y: i64) -> Option<(usize, usize)> {
    let size = island.map.size as i64;
    let wrap = |v: i64| {
        let v = if v < 0 { v + size } else { v };
        (0..size).contains(&v).then_some(v as usize)
    };
    Some((wrap(x)?, wrap(y)?))
}

/// `$land->[$x][$y] = kind; $landValue->[$x][$y] = value;`
fn put(island: &mut Island, x: i64, y: i64, kind: u8, value: i64) {
    if let Some((x, y)) = perl_cell(island, x, y)
        && let Some(c) = island.map.get_mut(x, y)
    {
        c.kind = kind;
        c.value = value;
        island.scratch.land_frac.remove(&(x, y));
    }
}

/// `$land->[$x][$y] = kind;` (値はそのまま)
fn put_kind(island: &mut Island, x: i64, y: i64, kind: u8) {
    if let Some((x, y)) = perl_cell(island, x, y)
        && let Some(c) = island.map.get_mut(x, y)
    {
        c.kind = kind;
    }
}

/// `$landValue->[$x][$y] = value;`
fn put_value(island: &mut Island, x: i64, y: i64, value: i64) {
    if let Some((x, y)) = perl_cell(island, x, y)
        && let Some(c) = island.map.get_mut(x, y)
    {
        c.value = value;
        island.scratch.land_frac.remove(&(x, y));
    }
}

/// いまの `$landValue->[$x][$y]`
fn value_at(island: &Island, x: i64, y: i64) -> i64 {
    perl_get(&island.map, x, y).1
}

/// `$island->{'money'} -= $cost;`。この系統の費用は値引きの計算で必ず整数になる
fn pay(island: &mut Island, c: &CmdRun) {
    island.money -= c.cost as i64;
}

fn log_out(ctx: &mut TurnContext, island: &Island, message: String) {
    ctx.log.out(ctx.turn, message, Some(island.id), None);
}

fn land_suc(ctx: &mut TurnContext, island: &Island, c: &CmdRun, point: &str) {
    log_out(ctx, island, cmsg::land_suc(&island.name, c.com_name, point));
}

fn land_fail(ctx: &mut TurnContext, island: &Island, c: &CmdRun) {
    log_out(
        ctx,
        island,
        cmsg::land_fail(&island.name, c.com_name, &c.land_name, &c.point),
    );
}

fn jo_fail(ctx: &mut TurnContext, island: &Island, c: &CmdRun, point: &str) {
    log_out(
        ctx,
        island,
        cmsg::jo_fail(&island.name, c.com_name, &c.land_name, point),
    );
}

/// 電力不足なら `logMsNoEne` を出して `true`
fn no_ene(ctx: &mut TurnContext, island: &Island, c: &CmdRun) -> bool {
    if island.scratch.shouhi > island.scratch.ene {
        log_out(ctx, island, cmsg::ms_no_ene(&island.name, c.com_name));
        return true;
    }
    false
}

/// `if($arg > 1) { $arg--; slideBack($comArray, 0); $comArray->[0] = {...}; }`
fn repeat(island: &mut Island, c: &mut CmdRun) {
    if c.arg > 1 {
        c.arg -= 1;
        // slideBack: 最後の計画を捨てて先頭を複製する (計画が 1 つしか無ければ何もしない)
        let cmds = &mut island.commands;
        if cmds.len() > 1 {
            cmds.pop();
            let first = cmds[0];
            cmds.insert(0, first);
        }
        let new = PlannedCommand {
            kind: c.kind,
            target: c.target,
            x: c.x,
            y: c.y,
            arg: c.arg,
        };
        if cmds.is_empty() {
            cmds.push(new);
        } else {
            cmds[0] = new;
        }
    }
}

fn island_tag(name: &str) -> String {
    wrap(tags::NAME, &format!("{name}島"))
}

/// `logJo2Fail`
fn msg_jo2_fail(name: &str, com_name: &str) -> String {
    format!(
        "{}で予定されていた{}ですが、まずは、十分な治安を守るために<B>軍事力</B>を確保しましょう。",
        island_tag(name),
        wrap(tags::COM_NAME, com_name)
    )
}

/// `logBokuFail`
fn msg_boku_fail(name: &str, com_name: &str, point: &str) -> String {
    format!(
        "{}で予定されていた{}は、予定地の{}が条件を満たした都市でなかったため中止されました。",
        island_tag(name),
        wrap(tags::COM_NAME, com_name),
        wrap(tags::NAME, point)
    )
}

/// `logBokuFail2`
fn msg_boku_fail2(name: &str, com_name: &str, m_name: &str, point: &str) -> String {
    format!(
        "{}で予定されていた{}は、予定地{}の<b>{m_name}</b>が嫌々をしたため中止されました。",
        island_tag(name),
        wrap(tags::COM_NAME, com_name),
        wrap(tags::NAME, point)
    )
}

/// `logNoTownAround`
fn msg_no_town_around(name: &str, com_name: &str, point: &str) -> String {
    format!(
        "{}で予定されていた{}は、予定地の{}の周辺に人口がいなかったため中止されました。",
        island_tag(name),
        wrap(tags::COM_NAME, com_name),
        wrap(tags::NAME, point)
    )
}

/// `logConsFire`
fn msg_cons_fire(name: &str, l_name: &str, point: &str, com_name: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>は{}で余った黄金によりメッキが施されました。",
        wrap(tags::NAME, &format!("{name}島{point}")),
        wrap(tags::COM_NAME, com_name)
    )
}

/// ハイテク技術誘致 (`$HcomHTget`)
pub(super) fn ht_get(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if no_ene(ctx, island, c) {
        return false;
    }
    if c.land_kind == k(L::HTFactory) {
        // すでにハイテク企業なら規模 + 10000人 (最大 500000人)
        let v = (value_at(island, c.x, c.y) + 10).min(500);
        put_value(island, c.x, c.y, v);
    } else if c.land_kind == k(L::Factory) {
        if c.lv == 100 {
            put_kind(island, c.x, c.y, k(L::HTFactory));
        } else {
            jo_fail(ctx, island, c, &c.point);
            return false;
        }
    } else {
        land_fail(ctx, island, c);
        return false;
    }
    land_suc(ctx, island, c, &c.point);
    pay(island, c);
    repeat(island, c);
    true
}

/// 自宅建設・税率変更 (`$HcomHouse`)
pub(super) fn house(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if island.scratch.hou > 0 {
        // 自宅があれば税率を変えるだけ。費用を払わず 0 を返す (Perl 版のまま)
        island.eisei[0] = c.arg;
        land_suc(ctx, island, c, &c.point);
        return false;
    }
    if !(c.land_kind == k(L::Plains) || c.land_kind == k(L::Plains2) || c.land_kind == k(L::Town)) {
        land_fail(ctx, island, c);
        return false;
    }
    if c.arg == 0 {
        c.arg = 5;
    }
    island.eisei[0] = c.arg;
    let level = (0..9)
        .rev()
        .find(|&i| island.pts > HOUSE_LEVELS[i])
        .map_or(0, |i| i as i64 + 1);
    put(island, c.x, c.y, k(L::House), level);
    land_suc(ctx, island, c, &c.point);
    pay(island, c);
    true
}

/// 輝ける都市計画 (`$HcomBettown`)
pub(super) fn bettown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    let map = &island.map;
    let shuto_count =
        count_around(map, c.x, c.y, L::Shuto, 7) + count_around(map, c.x, c.y, L::Umishuto, 7);
    let bet_count = count_around(map, c.x, c.y, L::Bettown, 7);
    if c.land_kind != k(L::Bigtown) {
        land_fail(ctx, island, c);
        return false;
    }
    if island.scratch.shu > 0 && (shuto_count > 0 || bet_count > 1) {
        put_kind(island, c.x, c.y, k(L::Bettown));
        land_suc(ctx, island, c, &c.point);
        pay(island, c);
        true
    } else {
        jo_fail(ctx, island, c, &c.point);
        false
    }
}

/// 改装・強化 (`$HcomKai`)
pub(super) fn kai(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if no_ene(ctx, island, c) {
        return false;
    }
    let (x, y, lk, lv) = (c.x, c.y, c.land_kind, c.lv);
    if lk == k(L::Kyujo) {
        if island.scratch.ky2 == 0 {
            island.eisei_raw[1] = "1,1,1,0,0,0,0,0,0,0,10".to_string();
        }
        put(island, x, y, k(L::Kyujokai), 0);
    } else if lk == k(L::Kyujokai) {
        // $sto.. はグローバル変数。マッチしなければ etc5 のマッチの値が入る (Perl 版のまま)
        let mut m = c.scope.clone();
        let mut st = ctx
            .globals
            .eisei4
            .assign(m.fields::<11>(&island.eisei_raw[1]));
        st[0] += 1;
        st[1] += 1;
        st[2] += 1;
        ctx.globals.eisei4.0 = st;
        // 書き戻す文字列は、捕まえた文字列をそのまま埋め込む (空欄・先頭の 0 が残る)
        let mut text = capture_strings(&island.eisei_raw[1], &island.etc_raw[0], &c.scope);
        for t in text.iter_mut().take(3) {
            *t = Some(magic_increment(t.as_deref()));
        }
        island.eisei_raw[1] = text
            .iter()
            .map(|t| t.as_deref().unwrap_or(""))
            .collect::<Vec<_>>()
            .join(",");
        land_suc(ctx, island, c, &c.point);
        pay(island, c);
        repeat(island, c);
        return true;
    } else if lk == k(L::Conden4) && lv == 2 {
        put(island, x, y, k(L::Conden2), 0);
    } else if lk == k(L::Conden4) && lv == 3 {
        put(island, x, y, k(L::Conden3), 0);
    } else if lk == k(L::Fune) && lv == 10 {
        put_value(island, x, y, 19);
    } else if lk == k(L::Foodim) && lv >= 480 {
        put(island, x, y, k(L::Foodka), 1);
    } else if lk == k(L::EneSo) {
        put_value(island, x, y, 1250);
    } else if lk == k(L::Zoo) {
        let mut v = value_at(island, x, y) + 10;
        let cap = trunc(island.owner_stats.rena as f64 / 75.0);
        if v > cap {
            v = cap;
        }
        if v > 200 {
            v = 200;
        }
        put_value(island, x, y, v);
        land_suc(ctx, island, c, &c.point);
        pay(island, c);
        repeat(island, c);
        return true;
    } else if lk == k(L::Defence) {
        put_value(island, x, y, 77);
    } else if lk == k(L::HTFactory) {
        put_kind(island, x, y, k(L::SHTF));
    } else if lk == k(L::SHTF) {
        put_kind(island, x, y, k(L::HTFactory));
    } else if lk == k(L::Kura) {
        let seq = (trunc(lv as f64 / 100.0) + 1).min(9);
        let choki = lv.rem_euclid(100);
        put_value(island, x, y, seq * 100 + choki);
        land_suc(ctx, island, c, &c.point);
        pay(island, c);
        repeat(island, c);
        return true;
    } else if lk == k(L::Kuraf) {
        let choki = trunc(lv as f64 / 10.0);
        let kibo = (lv.rem_euclid(10) + 1).min(9);
        put_value(island, x, y, choki * 10 + kibo);
        land_suc(ctx, island, c, &c.point);
        pay(island, c);
        repeat(island, c);
        return true;
    } else if lk == k(L::Rizort) {
        let map = &island.map;
        let sea_count: i64 = [
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
        ]
        .iter()
        .map(|&l| count_around(map, x, y, l, 7))
        .sum();
        let rizort_count: i64 = [L::Rizort, L::Kajino, L::BigRizort]
            .iter()
            .map(|&l| count_around(map, x, y, l, 7))
            .sum();
        let eis = &island.eis;
        let os = &island.owner_stats;
        let value = lv
            + eis[0]
            + eis[1]
            + eis[2]
            + eis[4]
            + trunc(os.fore as f64 / 10.0)
            + trunc(os.rena as f64 / 10.0)
            - island.monster_live * 100;
        if sea_count > 1 && value > 500 && rizort_count > 2 {
            put_kind(island, x, y, k(L::BigRizort));
        } else {
            jo_fail(ctx, island, c, &c.point);
            return false;
        }
    } else if lk == k(L::BigRizort) {
        if island.owner_stats.rena < 15000 {
            log_out(ctx, island, msg_jo2_fail(&island.name, c.com_name));
            return false;
        }
        put_kind(island, x, y, k(L::Kajino));
    } else {
        land_fail(ctx, island, c);
        return false;
    }
    land_suc(ctx, island, c, &c.point);
    pay(island, c);
    true
}

/// 海底基地建設・海底都市建設の共通部分
fn build_on_sea(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
    to: L,
) -> bool {
    let island = &mut islands[idx];
    if no_ene(ctx, island, c) {
        return false;
    }
    if c.land_kind != k(L::Sea) || c.lv != 0 {
        land_fail(ctx, island, c);
        return false;
    }
    put(island, c.x, c.y, k(to), 0);
    land_suc(ctx, island, c, "(?, ?)");
    pay(island, c);
    true
}

/// 海底基地建設 (`$HcomSbase`)
pub(super) fn sbase(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    build_on_sea(ctx, islands, idx, c, L::Sbase)
}

/// 海底都市建設 (`$HcomSeacity`)
pub(super) fn seacity(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    build_on_sea(ctx, islands, idx, c, L::Seacity)
}

/// 防災都市化 (`$HcomProcity`)
pub(super) fn procity(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if c.land_kind != k(L::Town) || c.lv != 100 {
        land_fail(ctx, island, c);
        return false;
    }
    put(island, c.x, c.y, k(L::Procity), 100);
    land_suc(ctx, island, c, &c.point);
    pay(island, c);
    true
}

/// 周囲 2 ヘックスの町系の数 (現代都市・海底新都市の条件)
fn town_count(island: &Island, x: i64, y: i64) -> i64 {
    TOWN_KINDS
        .iter()
        .map(|&l| count_around(&island.map, x, y, l, 19))
        .sum()
}

/// 現代都市建設 (`$HcomBigtown`)
pub(super) fn bigtown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if c.land_kind != k(L::Newtown) || c.lv < 149 {
        jo_fail(ctx, island, c, &c.point);
        return false;
    }
    if town_count(island, c.x, c.y) < 16 {
        jo_fail(ctx, island, c, &c.point);
        return false;
    }
    put_kind(island, c.x, c.y, k(L::Bigtown));
    land_suc(ctx, island, c, &c.point);
    pay(island, c);
    true
}

/// 海底新都市建設 (`$HcomSeatown`)
pub(super) fn seatown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if c.land_kind != k(L::Seacity) || c.lv < 200 {
        jo_fail(ctx, island, c, "(?, ?)");
        return false;
    }
    if town_count(island, c.x, c.y) < 16 {
        jo_fail(ctx, island, c, "(?, ?)");
        return false;
    }
    put_kind(island, c.x, c.y, k(L::Seatown));
    land_suc(ctx, island, c, "(?, ?)");
    pay(island, c);
    true
}

/// 僕の引越し (`$HcomBoku`)
pub(super) fn boku(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    let (x, y) = (c.x, c.y);
    if c.land_kind != k(L::Procity) {
        log_out(
            ctx,
            island,
            msg_boku_fail(&island.name, c.com_name, &c.point),
        );
        return false;
    }
    let town_count = count_around(&island.map, x, y, L::Town, 19);
    if town_count == 0 {
        log_out(
            ctx,
            island,
            msg_no_town_around(&island.name, c.com_name, &c.point),
        );
        return false;
    }
    let v = (value_at(island, x, y) + 10).min(200);
    put_value(island, x, y, v);
    // 行による位置調整も範囲の確認もしない (Perl 版のまま)。
    // 町の数は位置調整をして数えたものなので、減らす町とは別のマスを数えていることがある
    for i in 1..19 {
        let (sx, sy) = (x + AX[i], y + AY[i]);
        let (kind, lv) = perl_get(&island.map, sx, sy);
        if kind == k(L::Town) {
            let v = lv - trunc(20.0 / town_count as f64);
            if v <= 0 {
                // 平地に戻す
                put(island, sx, sy, k(L::Plains), 0);
                continue;
            }
            put_value(island, sx, sy, v);
        }
    }
    land_suc(ctx, island, c, &c.point);
    pay(island, c);
    repeat(island, c);
    true
}

/// 僕の引越し２ (`$HcomBoku2`)。1 回目で予定地の地形を持ち上げ、2 回目で置く
pub(super) fn boku2(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let size = ctx.config.island_size as i64;
    let island = &mut islands[idx];
    let (x, y, lk) = (c.x, c.y, c.land_kind);

    if lk == k(L::Monster) {
        let (_, m_name, _) = monster_spec(value_at(island, x, y));
        log_out(
            ctx,
            island,
            msg_boku_fail2(&island.name, c.com_name, m_name, &c.point),
        );
        return false;
    }

    let st = &island.scratch.command.city;
    let stocked = st.stockflag == 55;
    let city_stock = (st.stocklandkind == i64::from(k(L::Bettown)) && st.stocklandvalue > 1500)
        || (st.stocklandkind == i64::from(k(L::Kajino)) && st.stocklandvalue > 2000);

    if (lk == k(L::Plains) || lk == k(L::Sea)) && stocked {
        let (sk, sv) = (st.stocklandkind, st.stocklandvalue);
        put(island, x, y, sk as u8, sv);
        island.scratch.command.city.pointb += &format!("({x}, {y})");
        let pointb = island.scratch.command.city.pointb.clone();
        land_suc(ctx, island, c, &pointb);

        let sizekeisu = if size > 16 { 5 } else { 1 };
        if sk == i64::from(k(L::House))
            && sv == 9
            && island.scratch.co01 > sizekeisu
            && island.scratch.co8 > sizekeisu
        {
            island.scratch.command.city.condenmekki = 0;
            for i in 1..7 {
                let Some((sx, sy)) = in_map(size, x, y, i) else {
                    continue;
                };
                let (kind, lv) = perl_get(&island.map, sx, sy);
                let (m_kind, _, _) = monster_spec(lv);
                if kind == k(L::Monster) && m_kind == 14 {
                    island.scratch.command.city.condenmekki = 3;
                }
            }
            if island.scratch.command.city.condenmekki == 3 {
                for i in 1..19 {
                    let Some((sx, sy)) = in_map(size, x, y, i) else {
                        continue;
                    };
                    let (kind, lv) = perl_get(&island.map, sx, sy);
                    if kind == k(L::Conden2) {
                        put_kind(island, sx, sy, k(L::Conden3));
                        log_out(
                            ctx,
                            island,
                            msg_cons_fire(
                                &island.name,
                                &land_name(kind, lv),
                                &format!("({sx}, {sy})"),
                                c.com_name,
                            ),
                        );
                        // 費用を払わずに終わる (Perl 版のまま)
                        return true;
                    }
                }
            }
        }
        pay(island, c);
        true
    } else if (lk == k(L::Mountain) || lk == k(L::Frocity)) && stocked && city_stock {
        let sv = st.stocklandvalue;
        if lk == k(L::Mountain) {
            put(island, x, y, k(L::Skycity), sv);
        } else {
            let v = value_at(island, x, y) + sv;
            put(island, x, y, k(L::Umicity), v);
        }
        island.scratch.command.city.pointb += &format!("({x}, {y})");
        let pointb = island.scratch.command.city.pointb.clone();
        land_suc(ctx, island, c, &pointb);
        pay(island, c);
        true
    } else {
        let (kind, lv) = perl_get(&island.map, x, y);
        let st = &mut island.scratch.command.city;
        st.stocklandkind = i64::from(kind);
        st.stocklandvalue = lv;
        put(island, x, y, k(L::Plains), 0);
        let st = &mut island.scratch.command.city;
        st.pointb = format!("({x}, {y})〜");
        st.stockflag = 55;
        false
    }
}

/// `countAround` と同じ位置調整と範囲の確認をした `i` 番目の座標
fn in_map(size: i64, x: i64, y: i64, i: usize) -> Option<(i64, i64)> {
    let (sx, sy) = crate::land::around(x, y, i);
    ((0..size).contains(&sx) && (0..size).contains(&sy)).then_some((sx, sy))
}

/// `/^([0-9]*),...$/` (N 個) が一致したときの各欄の文字列
fn field_strings(s: &str, n: usize) -> Option<Vec<String>> {
    let s = s.strip_suffix('\n').unwrap_or(s);
    let parts: Vec<&str> = s.split(',').collect();
    (parts.len() == n && parts.iter().all(|p| p.bytes().all(|b| b.is_ascii_digit())))
        .then(|| parts.into_iter().map(String::from).collect())
}

/// 野球場・改の改装で `$1`..`$11` に見えている文字列 (未定義なら `None`)。
/// `eisei4` が一致しなければ、doCommand の費用の計算で一致した `etc5` の先頭 11 欄
fn capture_strings(eisei4: &str, etc5: &str, scope: &MatchScope) -> Vec<Option<String>> {
    let caps = field_strings(eisei4, 11).or_else(|| {
        // etc5 の一致は scope に残っている (一致しなかったら $1.. は未定義)
        if *scope == MatchScope::default() {
            None
        } else {
            field_strings(etc5, 31)
        }
    });
    match caps {
        Some(v) => v.into_iter().take(11).map(Some).collect(),
        None => vec![None; 11],
    }
}

/// Perl の `++`。数字だけの文字列は桁数を保って 1 増やす ("007" → "008")。
/// 未定義と空文字列は 1 になる
fn magic_increment(s: Option<&str>) -> String {
    match s {
        None | Some("") => "1".to_string(),
        Some(s) => {
            let mut digits: Vec<u8> = s.bytes().collect();
            let mut i = digits.len();
            loop {
                if i == 0 {
                    digits.insert(0, b'1');
                    break;
                }
                i -= 1;
                if digits[i] == b'9' {
                    digits[i] = b'0';
                } else {
                    digits[i] += 1;
                    break;
                }
            }
            String::from_utf8(digits).unwrap_or_default()
        }
    }
}
