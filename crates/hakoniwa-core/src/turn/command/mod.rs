//! 開発計画の実行 (`doCommand`)。
//!
//! すべての計画に共通する前半 (計画の取り出し、費用の計算と資金・食料の確認) と
//! 「資金繰り」「島の放棄」はここ、それ以外は計画の系統ごとのファイルにある。
//! 振り分けの順番は Perl 版の `if/elsif` の順番と同じ。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - doCommand は計画を 1 つ実行したら 1、実行しなかったら 0 を返し、turnMain は 1 が
//!   返るまで繰り返す。資金不足などで 0 を返すと、その計画は消費されて次の計画に進む。
//! - `my` で宣言していない変数はグローバル変数で、doEachHex や別の島と値を共有する
//!   (`$kind`, `$point`, `$tId`, `$z0`.., `$costseisaku` など)。[`CmdRun`] にあるのは
//!   doCommand の `my` 変数だけ。

mod attack;
mod build;
mod city;
mod land;
mod magic;
mod ops;

pub(crate) use attack::exp_to_level;

use crate::land::{land_name, perl_get};
use crate::model::{Island, PlannedCommand};
use crate::tables::{CommandKind as C, HOUSE_LEVELS, LandKind};

use super::TurnContext;
use crate::log::msg;
use crate::perl::{MatchScope, trunc};

/// doCommand 1 回分の状態。Perl 版の doCommand の `my` 変数に当たる
#[derive(Debug, Clone)]
pub struct CmdRun {
    /// 計画番号 (`$kind`。グローバルの `$kind` とは別の局所変数)
    pub kind: u16,
    pub target: i64,
    pub x: i64,
    pub y: i64,
    pub arg: i64,
    /// 予定地の地形 (`$landKind = $land->[$x][$y]`。範囲を確かめずに読む)
    pub land_kind: u8,
    /// 予定地の地形の値 (`$lv`)
    pub lv: i64,
    /// 費用 (`$cost`)。Perl 版は小数になることがある
    pub cost: f64,
    /// 計画の名前 (`$comName`)
    pub com_name: &'static str,
    /// `"($x, $y)"` (`$point`。グローバルの `$point` とは別の局所変数)
    pub point: String,
    /// 予定地の地形の名前 (`$landName`)
    pub land_name: String,
    /// doCommand のトップレベルの `$1`.. (費用の計算で etc5 をマッチしたあと)。
    /// 分岐はブロックの中なので、正規表現を使うときはこれを `clone()` して使う
    pub scope: MatchScope,
}

impl CmdRun {
    pub fn command_kind(&self) -> Option<C> {
        C::from_u16(self.kind)
    }

    /// 予定地の座標 (島の中なら)
    pub fn cell(&self, island: &Island) -> Option<(usize, usize)> {
        crate::land::in_island(&island.map, (self.x, self.y))
    }
}

/// doCommand で使うグローバル変数のうち、doCommand だけのもの
#[derive(Debug, Default)]
pub struct CommandGlobals {
    /// `$jikkouarg`
    pub jikkouarg: i64,
    pub build: build::Globals,
    pub ops: ops::Globals,
    pub attack: attack::Globals,
    pub magic: magic::Globals,
}

/// 島に一時的に持たせる値のうち、計画の系統ごとのもの
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {
    pub land: land::Scratch,
    pub build: build::Scratch,
    pub city: city::Scratch,
    pub ops: ops::Scratch,
    pub attack: attack::Scratch,
    pub magic: magic::Scratch,
}

/// `slideFront`: 先頭の計画を取り出して詰め、末尾を「資金繰り」で埋める
fn take_first_command(island: &mut Island, command_max: usize) -> PlannedCommand {
    let first = if island.commands.is_empty() {
        PlannedCommand::default()
    } else {
        island.commands.remove(0)
    };
    island
        .commands
        .resize(command_max.saturating_sub(1), PlannedCommand::default());
    island.commands.push(PlannedCommand {
        kind: C::DoNothing as u16,
        ..Default::default()
    });
    first
}

/// 費用の値引き・割増しが効かない計画 (倉庫・輸出・援助など)
fn is_cost_exempt(kind: Option<C>) -> bool {
    matches!(
        kind,
        Some(C::Kura | C::Kura2 | C::Kuraf | C::Sell | C::Money | C::Food | C::Givefood)
    )
}

/// 島の規模による割増し (`$costx`) が効かない計画
fn is_costx_exempt(kind: Option<C>) -> bool {
    is_cost_exempt(kind)
        || matches!(
            kind,
            Some(C::House | C::Bettown | C::Kai | C::Boku2 | C::EneCs | C::EneNF | C::Eisei)
        )
}

/// 計画の費用。正なら資金、負なら食料。
/// Perl 版は途中で小数になることがあるので `f64` で返す
pub(crate) fn command_cost(
    ctx: &mut TurnContext,
    m: &mut MatchScope,
    island: &Island,
    kind_raw: u16,
) -> f64 {
    let kind = C::from_u16(kind_raw);
    let pts = island.pts;
    let mut cost = kind.map_or(0, C::cost) as f64;

    if ctx.config.another_mode {
        match kind {
            Some(C::House | C::Kai) => cost = (pts * 2) as f64,
            Some(C::Boku2) => cost = (pts * 4) as f64,
            _ => {}
        }
    } else {
        match kind {
            Some(C::House) => cost = (pts * 3) as f64,
            Some(C::Bettown | C::Kai) => cost = pts as f64,
            Some(C::Boku2) => cost = (pts * 4) as f64,
            _ => {}
        }
    }

    // 島の規模による割増し
    let costx = {
        let table = [1.0, 1.2, 1.4, 1.4, 1.6, 1.6, 1.8, 1.8, 2.0];
        (0..9)
            .rev()
            .find(|&i| pts > HOUSE_LEVELS[i])
            .map_or(1.0, |i| table[i])
    };
    if !ctx.config.another_mode && !is_costx_exempt(kind) {
        cost *= costx;
    }

    let sc = &island.scratch;
    let exempt = is_cost_exempt(kind);
    // ハイテク企業があれば 2/3、ハイテク企業・改があれば 9/10
    if sc.htf > 0 && !exempt {
        cost = trunc(cost * 2.0 / 3.0) as f64;
    } else if sc.shtf > 0 && !exempt {
        cost = trunc(cost * 9.0 / 10.0) as f64;
    }

    // 大学 95 による値引き。$island->{'co95'} は常に 0 なので実際には働かない (Perl 版のまま)
    let costco95 = 0.975f64.powi(sc.co95 as i32).max(0.9);
    if sc.co95 > 0 && !exempt {
        cost = trunc(cost * costco95) as f64;
    }

    // 政策による値引き
    let s = ctx.globals.etc5.assign(m.fields(&island.etc_raw[0]));
    let costseisaku: i64 = s[1..].iter().sum();
    // $costseisaku はグローバル変数 (島営企業の処理も同じ変数を使う)
    ctx.globals.hex.special.costseisaku = costseisaku;
    let costseisaku2 = 0.9975f64.powf(costseisaku as f64).max(0.75);
    if s[0] > 0 && !exempt {
        cost = trunc(cost * costseisaku2) as f64;
    }

    // 資金が多いほど割高 (少なければ 2 割引き)
    let s12b = (trunc(s[12] as f64 / 5.0) + 1).min(10);
    let costmoney = island.money as f64 / 5.0 / (999_999.0 * s12b as f64) + 0.8;
    if !exempt {
        cost = trunc(cost * costmoney) as f64;
    }
    cost
}

/// `doCommand($island)`。計画を 1 つ実行したら `true`、
/// 実行せずに次の計画へ進む (資金不足など) なら `false`
pub(crate) fn do_command(ctx: &mut TurnContext, islands: &mut [Island], idx: usize) -> bool {
    let command_max = ctx.config.command_max;
    let island = &mut islands[idx];
    let command = take_first_command(island, command_max);
    let kind = command.command_kind();
    let com_name = kind.map_or("", C::name);
    let (id, turn) = (island.id, ctx.turn);

    if kind == Some(C::DoNothing) {
        // 資金繰り (logDoNothing は Perl 版でコメントアウトされている)
        island.money += 100;
        island.money += ctx.random(100);
        if ctx.random(100) < 5 {
            let value = 1 + ctx.random(1999);
            island.money += value;
            let amount = format!("{value}{}", ctx.config.units.money);
            ctx.log
                .out(turn, msg::enjo(&island.name, &amount), Some(id), None);
        }
        island.absent += 1;

        // 自動放棄
        if island.absent >= ctx.config.giveup_turn {
            island.commands[0] = PlannedCommand {
                kind: C::Giveup as u16,
                ..Default::default()
            };
        }
        return true;
    }

    island.absent = 0;
    ctx.globals.command.jikkouarg = 0;

    // 予定地 (範囲を確かめずに読む)
    let (land_kind, lv) = perl_get(&island.map, command.x, command.y);

    // doCommand の $1.. (turnMain のトップレベルからはマッチの無い状態で呼ばれる)
    let mut m = MatchScope::default();
    let cost = command_cost(ctx, &mut m, island, command.kind);
    let island = &mut islands[idx];

    // 費用の確認
    if cost > 0.0 {
        if (island.money as f64) < cost {
            // 牧場の上に「牧場建設・家畜販売」なら資金が足りなくても実行する
            let farm_sale = kind == Some(C::Farmcpc)
                && LandKind::from_u8(land_kind).is_some_and(|l| {
                    matches!(l, LandKind::Farmchi | LandKind::Farmpic | LandKind::Farmcow)
                });
            if !farm_sale {
                ctx.log
                    .out(turn, msg::no_money(&island.name, com_name), Some(id), None);
                return false;
            }
        }
    } else if cost < 0.0 && (island.food as f64) < -cost {
        ctx.log
            .out(turn, msg::no_food(&island.name, com_name), Some(id), None);
        return false;
    }

    let mut c = CmdRun {
        kind: command.kind,
        target: command.target,
        x: command.x,
        y: command.y,
        arg: command.arg,
        land_kind,
        lv,
        cost,
        com_name,
        point: format!("({}, {})", command.x, command.y),
        land_name: land_name(land_kind, lv),
        scope: m,
    };
    dispatch(ctx, islands, idx, &mut c)
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

/// `$arg` 回繰り返す計画の残りを入れ直す
/// (`if ($arg > 1) { $arg--; slideBack($comArray, 0); $comArray->[0] = {... 'arg' => $arg} }`)
pub(super) fn repeat_if_more(island: &mut Island, c: &mut CmdRun) {
    if c.arg <= 1 {
        return;
    }
    c.arg -= 1;
    slide_back(&mut island.commands, 0);
    let cmd = PlannedCommand {
        kind: c.kind,
        target: c.target,
        x: c.x,
        y: c.y,
        arg: c.arg,
    };
    match island.commands.first_mut() {
        Some(first) => *first = cmd,
        None => island.commands.push(cmd),
    }
}

/// 計画ごとの分岐。Perl 版の `if/elsif` の順番どおり。戻り値は doCommand の戻り値 (1 なら true)
fn dispatch(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, c: &mut CmdRun) -> bool {
    let Some(kind) = c.command_kind() else {
        // 計画番号が定義に無いものは、Perl 版でも何もせずに 1 ターン使う
        return true;
    };
    match kind {
        C::Prepare | C::Prepare2 => land::prepare(ctx, islands, idx, c),
        C::Reclaim | C::Reclaim2 | C::Reclaim3 => land::reclaim(ctx, islands, idx, c),
        C::Minato => land::minato(ctx, islands, idx, c),
        C::Fune => land::fune(ctx, islands, idx, c),
        C::Seki => land::seki(ctx, islands, idx, c),
        C::Destroy | C::Destroy3 => land::destroy(ctx, islands, idx, c),
        C::Onsen => land::onsen(ctx, islands, idx, c),
        C::SellTree => land::sell_tree(ctx, islands, idx, c),
        C::Plant
        | C::Farm
        | C::EneAt
        | C::EneFw
        | C::EneWt
        | C::EneWd
        | C::EneBo
        | C::EneSo
        | C::EneCs
        | C::EneNF
        | C::Conden
        | C::Foodim
        | C::Farmcpc
        | C::College
        | C::Factory
        | C::Base
        | C::Monument
        | C::Haribote
        | C::Monbuy
        | C::Monbuyt
        | C::Park
        | C::Zoo
        | C::Mine
        | C::Nursery
        | C::Kyujo
        | C::Umiamu
        | C::Newtown
        | C::Rizort
        | C::Yoyaku
        | C::Yakusho
        | C::Kura
        | C::Kuraf
        | C::Kura2
        | C::Train
        | C::Dbase => build::build(ctx, islands, idx, c),
        C::Mountain => land::mountain(ctx, islands, idx, c),
        C::HTget => city::ht_get(ctx, islands, idx, c),
        C::House => city::house(ctx, islands, idx, c),
        C::Bettown => city::bettown(ctx, islands, idx, c),
        C::Kai => city::kai(ctx, islands, idx, c),
        C::Sbase => city::sbase(ctx, islands, idx, c),
        C::Seacity => city::seacity(ctx, islands, idx, c),
        C::Procity => city::procity(ctx, islands, idx, c),
        C::Bigtown => city::bigtown(ctx, islands, idx, c),
        C::Seatown => city::seatown(ctx, islands, idx, c),
        C::Boku => city::boku(ctx, islands, idx, c),
        C::Boku2 => city::boku2(ctx, islands, idx, c),
        C::Auction => ops::auction(ctx, islands, idx, c),
        C::Givefood => ops::givefood(ctx, islands, idx, c),
        C::Eisei => ops::eisei(ctx, islands, idx, c),
        C::Eiseimente => ops::eiseimente(ctx, islands, idx, c),
        C::EiseiAtt => ops::eisei_att(ctx, islands, idx, c),
        C::EiseiLzr => ops::eisei_lzr(ctx, islands, idx, c),
        C::MissileNM
        | C::MissilePP
        | C::MissileSPP
        | C::MissileST
        | C::MissileSS
        | C::MissileLR
        | C::MissileLD => attack::missile(ctx, islands, idx, c),
        C::SendMonster => attack::send_monster(ctx, islands, idx, c),
        C::Taishi => attack::taishi(ctx, islands, idx, c),
        C::Magic => magic::magic(ctx, islands, idx, c),
        C::Sell => ops::sell(ctx, islands, idx, c),
        C::Food | C::Money => ops::aid(ctx, islands, idx, c),
        C::EneGive => ops::ene_give(ctx, islands, idx, c),
        C::Propaganda => ops::propaganda(ctx, islands, idx, c),
        C::Giveup => {
            let island = &mut islands[idx];
            let (id, turn) = (island.id, ctx.turn);
            ctx.log.out(turn, msg::giveup(&island.name), Some(id), None);
            ctx.log.history(turn, msg::giveup_history(&island.name));
            island.scratch.dead = true;
            true
        }
        // 資金繰りは前で処理済み。自動入力系 (61〜69) といじり (60) は doCommand に
        // 分岐が無く、何もせずに 1 ターン使う (入力のときに展開される)
        _ => true,
    }
}

/// どの系統でも使うログの文面
pub(crate) mod cmsg {
    use crate::log::tags::{self, wrap};

    fn island(name: &str) -> String {
        wrap(tags::NAME, &format!("{name}島"))
    }

    fn com(com_name: &str) -> String {
        wrap(tags::COM_NAME, com_name)
    }

    /// `logLandSuc`
    pub fn land_suc(name: &str, com_name: &str, point: &str) -> String {
        format!(
            "{}で{}が行われました。",
            wrap(tags::NAME, &format!("{name}島{point}")),
            com(com_name)
        )
    }

    /// `logLandSucmini` (座標を出さない)
    pub fn land_suc_mini(name: &str, com_name: &str) -> String {
        format!("{}で{}が行われました。", island(name), com(com_name))
    }

    /// `logLandFail`
    pub fn land_fail(name: &str, com_name: &str, land_name: &str, point: &str) -> String {
        format!(
            "{}で予定されていた{}は、予定地の{}が<B>{land_name}</B>だったため中止されました。",
            island(name),
            com(com_name),
            wrap(tags::NAME, point)
        )
    }

    /// `logJoFail`
    pub fn jo_fail(name: &str, com_name: &str, land_name: &str, point: &str) -> String {
        format!(
            "{}で予定されていた{}は、予定地の{}が条件を満たしていない<B>{land_name}</B>のため中止されました。",
            island(name),
            com(com_name),
            wrap(tags::NAME, point)
        )
    }

    /// `logMsNoEne`
    pub fn ms_no_ene(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、電力が不足しているのにと、島民が許しませんでした。",
            island(name),
            com(com_name)
        )
    }

    /// `logForbidden`
    pub fn forbidden(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、実行が許可されませんでした。",
            island(name),
            com(com_name)
        )
    }

    /// `logNoTech`
    pub fn no_tech(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は軍事技術が足りないため中止されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logNoRoke`
    pub fn no_roke(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}はロケットが足りないため中止されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logMsNoTarget`
    pub fn ms_no_target(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、目標の島に人が見当たらないため中止されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logNoLandArounde`
    pub fn no_land_arounde(name: &str, com_name: &str, point: &str, land_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、予定地の{}の周辺に<B>{land_name}</B>がなかったため中止されました。",
            island(name),
            com(com_name),
            wrap(tags::NAME, point)
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

    #[test]
    fn slide_front_fills_with_do_nothing() {
        let mut island = crate::turn::tests_support::island();
        island.commands = (1..=3)
            .map(|k| PlannedCommand {
                kind: k,
                ..Default::default()
            })
            .collect();
        let first = take_first_command(&mut island, 3);
        assert_eq!(first.kind, 1);
        let kinds: Vec<_> = island.commands.iter().map(|c| c.kind).collect();
        assert_eq!(kinds, [2, 3, C::DoNothing as u16]);
    }
}
