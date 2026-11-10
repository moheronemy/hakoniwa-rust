//! 整地・地ならし・埋め立て・港町開発・造船・関所・掘削・温泉掘削・伐採・採掘場整備。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 地ならしと伐採は 0 を返す (ターンを使わず、続けて次の計画を実行する)。
//! - 埋め立て (遠距離) は周りが全部海でも中止しない。2 段階埋め立てで浅瀬を山にする分岐は
//!   その前の分岐に先に捕まるので通らない。
//! - 2 段階掘削は山・金山・氷河以外の陸地を海にするが、面積を減らさない。
//! - 温泉掘削は値が 0 でない山だと何もせず (費用も引かず) 1 ターン使う。
//! - 神殿・神社のログはグローバル変数の `$point` を使う (doCommand の `$point` ではない)。
//! - `$value` や `$eggnum` は `my` の無いグローバル変数だが、読む前に必ず代入しているか
//!   ログの文面に出ないので、局所変数にしている。

use crate::land::{around, count_around, in_island};
use crate::log::tags::{self, wrap};
use crate::model::{Island, IslandMap, PlannedCommand};
use crate::perl::trunc;
use crate::tables::{CommandKind as C, LandKind as L};
use crate::turn::TurnContext;
use crate::turn::hex::msg::island_at;
use crate::turn::hex::town::{set, set_value};

use super::{CmdRun, cmsg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {
    /// `$island->{'prepare2'}`: このターンの地ならしの回数 (地震の確率に効く)
    pub prepare2: i64,
}

/// `slideBack($comArray, $number)`: `number` 番目の計画を複製して後ろにずらす (末尾は消える)
pub(super) fn slide_back(commands: &mut Vec<PlannedCommand>, number: usize) {
    // return if $number == $#$command;
    if commands.len() == number + 1 {
        return;
    }
    commands.pop();
    let copy = commands.get(number).copied().unwrap_or_default();
    let at = number.min(commands.len());
    commands.insert(at, copy);
}

/// `$arg` 回繰り返す計画の残りを先頭に入れ直す (`$arg--` して slideBack)
fn repeat_command(island: &mut Island, c: &mut CmdRun) {
    if c.arg > 1 {
        c.arg -= 1;
        slide_back(&mut island.commands, 0);
        let cmd = PlannedCommand {
            kind: c.kind,
            target: c.target,
            x: c.x,
            y: c.y,
            arg: c.arg,
        };
        if let Some(first) = island.commands.first_mut() {
            *first = cmd;
        } else {
            island.commands.push(cmd);
        }
    }
}

/// 予定地 `$land->[$x][$y]` の書き込み先。負の添字は Perl と同じく反対側から数える
/// (大きすぎる添字は Perl だと地図の外に値を作るが、移植版では書かない)
fn target(map: &IslandMap, x: i64, y: i64) -> Option<(usize, usize)> {
    let size = map.size as i64;
    let wrap = |v: i64| if v < 0 { v + size } else { v };
    in_island(map, (wrap(x), wrap(y)))
}

fn put(island: &mut Island, c: &CmdRun, kind: L, value: i64) {
    if let Some((x, y)) = target(&island.map, c.x, c.y) {
        set(island, x, y, kind, value);
    }
}

fn put_value(island: &mut Island, c: &CmdRun, value: i64) {
    if let Some((x, y)) = target(&island.map, c.x, c.y) {
        set_value(island, x, y, value);
    }
}

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| l as u8 == kind)
}

/// 埋め立て・港町・関所の「周りの海の数」(`$seaCount`)
fn sea_count(map: &IslandMap, x: i64, y: i64) -> i64 {
    [
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
    .sum()
}

/// 周りの海を浅瀬にする
fn make_shallow_around(island: &mut Island, x: i64, y: i64) {
    for i in 1..7 {
        if let Some((sx, sy)) = in_island(&island.map, around(x, y, i))
            && island
                .map
                .get(sx, sy)
                .is_some_and(|c| c.kind == L::Sea as u8)
        {
            set_value(island, sx, sy, 1);
        }
    }
}

/// 埋め立て・港町・造船・関所で予定地にできる海の地形
const SEA_SITES: [L; 8] = [
    L::Sea,
    L::Oil,
    L::Sbase,
    L::Nursery,
    L::Umiamu,
    L::Seatown,
    L::Umishuto,
    L::Seacity,
];

fn log_out(ctx: &mut TurnContext, island: &Island, message: String) {
    ctx.log.out(ctx.turn, message, Some(island.id), None);
}

fn land_fail(ctx: &mut TurnContext, island: &Island, c: &CmdRun) {
    log_out(
        ctx,
        island,
        cmsg::land_fail(&island.name, c.com_name, &c.land_name, &c.point),
    );
}

fn land_suc(ctx: &mut TurnContext, island: &Island, com_name: &str, c: &CmdRun) {
    log_out(
        ctx,
        island,
        cmsg::land_suc(&island.name, com_name, &c.point),
    );
}

fn pay(island: &mut Island, c: &CmdRun) {
    // 費用は最後に int() されているので整数
    island.money -= c.cost as i64;
}

/// 神殿・神社のお祝い (油田・金塊・金山を見つけたとき)
fn shrine_bonus(ctx: &mut TurnContext, island: &mut Island) {
    for (count, building) in [(island.scratch.sin, "神殿"), (island.scratch.jin, "神社")] {
        if count > 0 {
            let value = ctx.random(1001);
            island.money += value;
            let amount = format!("{value}{}", ctx.config.units.money);
            // logSinMoney はグローバル変数の $point を使う (Perl 版のまま)
            let message = msg::shrine(&island.name, &ctx.globals.hex.point, building, &amount);
            log_out(ctx, island, message);
        }
    }
}

/// 卵 (記念碑 80〜82) を置く
fn egg_found(ctx: &mut TurnContext, island: &mut Island, c: &CmdRun) {
    log_out(ctx, island, msg::egg_found(&island.name, c.com_name));
    let eggnum = 80 + ctx.random(3);
    put(island, c, L::Monument, eggnum);
}

/// 埋蔵金
fn maizo(ctx: &mut TurnContext, island: &mut Island, c: &CmdRun) {
    let v = 100 + ctx.random(901);
    island.money += v;
    let message = msg::maizo(&island.name, c.com_name, v, &ctx.config.units.money);
    log_out(ctx, island, message);
}

/// 投資額 (`min($arg * $cost, money)`)、`"$value$HunitMoney"`、`int($value / $cost)`
fn invest(ctx: &TurnContext, island: &mut Island, c: &mut CmdRun) -> (String, i64) {
    if c.arg == 0 {
        c.arg = 1;
    }
    let value = (c.arg as f64 * c.cost).min(island.money as f64) as i64;
    let amount = format!("{value}{}", ctx.config.units.money);
    let p = trunc(value as f64 / c.cost);
    island.money -= value;
    (amount, p)
}

/// 整地・地ならし
pub(super) fn prepare(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if is_one_of(
        c.land_kind,
        &[
            L::Sea,
            L::Sbase,
            L::Seacity,
            L::Seatown,
            L::Oil,
            L::Ice,
            L::Fune,
            L::Frocity,
            L::Nursery,
            L::Umiamu,
            L::Gold,
            L::RottenSea,
            L::Mountain,
            L::Umishuto,
            L::Monster,
        ],
    ) {
        land_fail(ctx, island, c);
        return false;
    }
    if c.land_kind == L::Monument as u8 {
        if (80..=83).contains(&c.lv) {
            // 食べちゃえ
            island.food += 20000;
        }
        if (74..=79).contains(&c.lv) {
            // 宝石会社売却
            island.money += 20000;
        }
    }
    put(island, c, L::Plains, 0);
    land_suc(ctx, island, "整地", c);
    pay(island, c);

    if c.command_kind() == Some(C::Prepare2) {
        island.scratch.command.land.prepare2 += 1;
        // ターン消費せず
        false
    } else {
        if ctx.random(1000) < ctx.config.disaster.maizo {
            maizo(ctx, island, c);
        }
        true
    }
}

/// 埋め立て・埋め立て (遠距離)・2 段階埋め立て
pub(super) fn reclaim(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    let kind = c.command_kind();
    if !is_one_of(c.land_kind, &SEA_SITES)
        && !is_one_of(c.land_kind, &[L::Plains, L::Plains2, L::Waste])
    {
        land_fail(ctx, island, c);
        return false;
    }
    let sea = sea_count(&island.map, c.x, c.y);
    if sea == 7 && matches!(kind, Some(C::Reclaim | C::Reclaim3)) {
        log_out(
            ctx,
            island,
            msg::no_land_around(&island.name, c.com_name, &c.point, "陸地"),
        );
        return false;
    }

    let reclaim3 = kind == Some(C::Reclaim3);
    if c.land_kind == L::Sea as u8 && c.lv == 1 {
        // 浅瀬なら荒地に (2 段階なら山に)
        put(island, c, L::Waste, 0);
        if reclaim3 {
            put(island, c, L::Mountain, 0);
        }
        land_suc(ctx, island, c.com_name, c);
        island.area += 1;
        if sea <= 4 {
            make_shallow_around(island, c.x, c.y);
        }
    } else if is_one_of(c.land_kind, &[L::Plains, L::Plains2, L::Waste]) {
        put(island, c, L::Mountain, 0);
        land_suc(ctx, island, c.com_name, c);
    } else if reclaim3 {
        // (Perl 版にはこの前に「2 段階で浅瀬なら山」の分岐があるが、最初の分岐が先に捕まえる)
        put(island, c, L::Waste, 0);
        land_suc(ctx, island, c.com_name, c);
    } else {
        put(island, c, L::Sea, 1);
        land_suc(ctx, island, c.com_name, c);
    }
    pay(island, c);
    true
}

/// 港町開発
pub(super) fn minato(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if !is_one_of(c.land_kind, &SEA_SITES) {
        land_fail(ctx, island, c);
        return false;
    }
    let sea = sea_count(&island.map, c.x, c.y);
    if sea == 7 {
        log_out(
            ctx,
            island,
            msg::no_land_around(&island.name, c.com_name, &c.point, "陸地"),
        );
        return false;
    }
    if c.land_kind == L::Sea as u8 && c.lv == 1 {
        put(island, c, L::Minato, 0);
        land_suc(ctx, island, c.com_name, c);
        island.area += 1;
        if sea <= 4 {
            make_shallow_around(island, c.x, c.y);
        }
    } else {
        put(island, c, L::Sea, 1);
        land_suc(ctx, island, c.com_name, c);
    }
    pay(island, c);
    true
}

/// 造船・出航
pub(super) fn fune(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if !is_one_of(c.land_kind, &SEA_SITES) {
        land_fail(ctx, island, c);
        return false;
    }
    if count_around(&island.map, c.x, c.y, L::Minato, 7) == 0 {
        log_out(
            ctx,
            island,
            msg::no_land_around(&island.name, c.com_name, &c.point, "港町"),
        );
        return false;
    }
    if c.land_kind != L::Sea as u8 {
        land_fail(ctx, island, c);
        return false;
    }
    if c.arg == 77 {
        put(island, c, L::Frocity, 1);
        let value = (c.arg as f64 * c.cost).min(island.money as f64) as i64;
        island.money -= value;
        land_suc(ctx, island, c.com_name, c);
        return true;
    }
    if c.arg >= ctx.config.ship_number as i64 || c.arg == 0 {
        c.arg = 1;
    }
    put(island, c, L::Fune, c.arg);
    land_suc(ctx, island, c.com_name, c);
    if matches!(c.arg, 1 | 2 | 5 | 6 | 11) {
        island.scratch.gyo += 1;
    }
    let value = (c.arg as f64 * c.cost).min(island.money as f64) as i64;
    island.money -= value;
    true
}

/// 関所建設
pub(super) fn seki(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if !is_one_of(c.land_kind, &SEA_SITES) {
        land_fail(ctx, island, c);
        return false;
    }
    let sea = sea_count(&island.map, c.x, c.y);
    if c.land_kind == L::Sea as u8 && c.lv == 1 {
        put(island, c, L::Seki, 0);
        land_suc(ctx, island, c.com_name, c);
        island.area += 1;
        if sea <= 4 {
            make_shallow_around(island, c.x, c.y);
        }
    } else {
        land_fail(ctx, island, c);
        return false;
    }
    pay(island, c);
    true
}

/// 掘削・2 段階掘削 (海なら油田探し)
pub(super) fn destroy(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if is_one_of(
        c.land_kind,
        &[
            L::Sbase,
            L::Seacity,
            L::Seatown,
            L::Oil,
            L::Fune,
            L::Frocity,
            L::Nursery,
            L::Umiamu,
            L::RottenSea,
            L::Umishuto,
            L::Monster,
        ],
    ) {
        land_fail(ctx, island, c);
        return false;
    }

    if c.land_kind == L::Sea as u8 && c.lv == 0 {
        // 油田探し
        let (amount, p) = invest(ctx, island, c);
        if p > ctx.random(100) + island.scratch.oil * 25 {
            log_out(
                ctx,
                island,
                msg::found(&island.name, &c.point, c.com_name, &amount, "油田"),
            );
            put(island, c, L::Oil, 0);
            island.scratch.oil += 1;
            shrine_bonus(ctx, island);
        } else {
            log_out(
                ctx,
                island,
                msg::not_found(&island.name, &c.point, c.com_name, &amount, "油田"),
            );
        }
        return true;
    }

    let destroy3 = c.command_kind() == Some(C::Destroy3);
    if c.land_kind == L::Mountain as u8 || c.land_kind == L::Gold as u8 {
        put(island, c, L::Waste, 0);
        if destroy3 {
            put(island, c, L::Sea, 1);
        }
    } else if c.land_kind == L::Ice as u8 {
        put(island, c, L::Sea, 1);
        if destroy3 {
            put(island, c, L::Sea, 0);
        }
    } else if destroy3 {
        // 陸地を海にしても面積を減らさない (Perl 版のまま)
        put(island, c, L::Sea, 0);
    } else if c.land_kind == L::Sea as u8 {
        put_value(island, c, 0);
    } else {
        put(island, c, L::Sea, 1);
        island.area -= 1;
    }
    land_suc(ctx, island, c.com_name, c);
    pay(island, c);
    true
}

/// 温泉掘削
pub(super) fn onsen(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if c.land_kind != L::Mountain as u8 {
        land_fail(ctx, island, c);
        return false;
    }
    if c.lv != 0 {
        // 採掘場では何もせず、費用も引かずに 1 ターン使う (Perl 版のまま)
        return true;
    }
    let (amount, p) = invest(ctx, island, c);
    if ctx.random(10000) < p * 15 {
        let v = 1000 + ctx.random(2001);
        island.money += v;
        put(island, c, L::Gold, 1);
        let message = msg::gold(&island.name, c.com_name, v, &ctx.config.units.money);
        log_out(ctx, island, message);
        shrine_bonus(ctx, island);
    } else if ctx.random(1000) < 50 {
        egg_found(ctx, island, c);
    } else if ctx.random(1000) < 50 && island.scratch.m84 < 4 {
        log_out(ctx, island, msg::iseki_found(&island.name, c.com_name));
        put(island, c, L::Monument, 84);
    } else if p > ctx.random(100) + island.scratch.hot * 30 {
        log_out(
            ctx,
            island,
            msg::found(&island.name, &c.point, c.com_name, &amount, "温泉"),
        );
        put(island, c, L::Onsen, 1);
    } else {
        log_out(
            ctx,
            island,
            msg::not_found(&island.name, &c.point, c.com_name, &amount, "温泉"),
        );
    }
    if ctx.random(1000) < 15 {
        maizo(ctx, island, c);
    }
    pay(island, c);
    true
}

/// 伐採 (ターンを使わない)
pub(super) fn sell_tree(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    if c.land_kind != L::Forest as u8 {
        land_fail(ctx, island, c);
        return false;
    }
    put(island, c, L::Plains, 0);
    land_suc(ctx, island, c.com_name, c);
    if ctx.random(1000) < 75 {
        egg_found(ctx, island, c);
    }
    island.money += ctx.config.tree_value * c.lv;
    false
}

/// 採掘場整備 (`$arg` 回繰り返す)
pub(super) fn mountain(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let island = &mut islands[idx];
    let add = if c.land_kind == L::Mountain as u8 {
        // 規模 + 5000人
        5
    } else if c.land_kind == L::Gold as u8 {
        // 規模 + 20000人
        20
    } else {
        land_fail(ctx, island, c);
        return false;
    };
    if let Some((x, y)) = target(&island.map, c.x, c.y) {
        // 小数部分はそのまま残る ($landValue->[$x][$y] += 5)
        let frac = island
            .scratch
            .land_frac
            .get(&(x, y))
            .copied()
            .unwrap_or(0.0);
        let cell = island.map.get_mut(x, y).expect("in range");
        cell.value += add;
        if cell.value as f64 + frac > 200.0 {
            // 最大 200000人
            set_value(island, x, y, 200);
        }
    }
    land_suc(ctx, island, c.com_name, c);
    pay(island, c);
    repeat_command(island, c);

    if ctx.random(1000) < 9 {
        let v = 1000 + ctx.random(4001);
        island.money += v;
        // 地形だけ金山にする (値はそのまま)
        if let Some((x, y)) = target(&island.map, c.x, c.y) {
            island.map.get_mut(x, y).expect("in range").kind = L::Gold as u8;
        }
        let message = msg::gold(&island.name, c.com_name, v, &ctx.config.units.money);
        log_out(ctx, island, message);
        shrine_bonus(ctx, island);
    }
    true
}

/// この系統のログの文面
mod msg {
    use super::{island_at, tags, wrap};

    fn island(name: &str) -> String {
        wrap(tags::NAME, &format!("{name}島"))
    }

    fn com(com_name: &str) -> String {
        wrap(tags::COM_NAME, com_name)
    }

    /// `logNoLandAround` (陸地) と `logNoLandAroundm` (港町)
    pub fn no_land_around(name: &str, com_name: &str, point: &str, what: &str) -> String {
        format!(
            "{}で予定されていた{}は、予定地の{}の周辺に{what}がなかったため中止されました。",
            island(name),
            com(com_name),
            wrap(tags::NAME, point)
        )
    }

    /// `logOilFound` / `logHotFound`
    pub fn found(name: &str, point: &str, com_name: &str, amount: &str, what: &str) -> String {
        format!(
            "{}で<B>{amount}</B>の予算をつぎ込んだ{}が行われ、<B>{what}が掘り当てられました</B>。",
            island_at(name, point),
            com(com_name)
        )
    }

    /// `logOilFail` / `logHotFail`
    pub fn not_found(name: &str, point: &str, com_name: &str, amount: &str, what: &str) -> String {
        format!(
            "{}で<B>{amount}</B>の予算をつぎ込んだ{}が行われましたが、{what}は見つかりませんでした。",
            island_at(name, point),
            com(com_name)
        )
    }

    /// `logSinMoney` / `logJinMoney` (`point` はグローバル変数の `$point`)
    pub fn shrine(name: &str, point: &str, building: &str, amount: &str) -> String {
        format!(
            "{}の<B>{building}</B>で祝いの祭りが行われ、<B>{amount}</B>の収益が上がりました。",
            island_at(name, point)
        )
    }

    /// `logMaizo`
    pub fn maizo(name: &str, com_name: &str, value: i64, unit: &str) -> String {
        format!(
            "{}での{}中に、<B>{value}{unit}もの埋蔵金</B>が発見されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logGold`
    pub fn gold(name: &str, com_name: &str, value: i64, unit: &str) -> String {
        format!(
            "{}での{}中に、<B>金塊</B>が発見され<B>{value}{unit}</B>の利益があがりました。",
            island(name),
            com(com_name)
        )
    }

    /// `logEggFound`
    pub fn egg_found(name: &str, com_name: &str) -> String {
        format!(
            "{}での{}中に、<B>何かの卵</B>が発見され{}には破壊が無理なので放置することにしました。",
            island(name),
            com(com_name),
            com(&format!("{com_name}業者"))
        )
    }

    /// `logIsekiFound`
    pub fn iseki_found(name: &str, com_name: &str) -> String {
        format!(
            "{}での{}中に、<B>古代遺跡</B>が発見され<B>島の重要埋蔵文化財</B>に指定されました。",
            island(name),
            com(com_name)
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cmds(kinds: &[u16]) -> Vec<PlannedCommand> {
        kinds
            .iter()
            .map(|&kind| PlannedCommand {
                kind,
                ..Default::default()
            })
            .collect()
    }

    #[test]
    fn slide_back_duplicates_and_drops_last() {
        let mut v = cmds(&[1, 2, 3]);
        slide_back(&mut v, 0);
        let kinds: Vec<_> = v.iter().map(|c| c.kind).collect();
        assert_eq!(kinds, [1, 1, 2]);

        let mut v = cmds(&[1]);
        slide_back(&mut v, 0);
        assert_eq!(v.len(), 1);
    }
}
