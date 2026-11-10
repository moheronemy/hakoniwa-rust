//! 人工衛星・宇宙ステーションなどの維持 (Perl 版 15666〜15787 行)。
//!
//! - 気象衛星〜防衛衛星 (`eis1`〜`eis5`) は毎ターン `random(2)` ずつ減り、1 未満で崩壊する。
//! - イレギュラー (`eis6`) は島の怪獣をすべて攻撃し (1 体ごとに `eis6` が 10 減る)、そのあと
//!   `random(2)` 減る。
//! - 宇宙ステーション (`eis7` = 人口 × 100 + 耐久) は人口ぶんの資金を払う。ロケットが足りないと
//!   人口が 1000 減る。
//! - 天空城 (`h11`) は電力が余っていれば島の怪獣をすべて消し飛ばす。
//!
//! グローバル変数 `$point` (`HexGlobals::point`)、`$tId` (ログの 2 番目の島 ID)、
//! `($cstpop, $csten)` (`command::ops::Globals::cst`) を使う。

use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::trunc;
use crate::tables::{LandKind as L, MONSTERS};
use crate::turn::TurnContext;
use crate::turn::estimate::monster_spec;
use crate::turn::hex::town::{set, set_value};

use super::ProcRun;

/// この段階で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {}

/// この段階で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

fn island_name(name: &str) -> String {
    wrap(tags::NAME, &format!("{name}島"))
}

/// `logEiseiEnd`
fn eisei_end(name: &str, eisei: &str) -> String {
    format!(
        "{}の<B>{eisei}</B>は{}したようです！！",
        island_name(name),
        wrap(tags::DISASTER, "崩壊")
    )
}

/// `logEiseiEndNopop`
fn eisei_end_nopop(name: &str, eisei: &str) -> String {
    format!(
        "{}の<B>{eisei}</B>は{}ようです！！",
        island_name(name),
        wrap(tags::DISASTER, "人がいなくなった")
    )
}

/// `logNoRokeCst`
fn no_roke_cst(name: &str) -> String {
    format!(
        "{}は{}により<B>宇宙ステーション</B>に食料が運べません！！",
        island_name(name),
        wrap(tags::DISASTER, "ロケット不足")
    )
}

/// `logIreAttackt`
fn ire_attackt(name: &str, m_name: &str, point: &str, t_name: &str, t_point: &str) -> String {
    format!(
        "{}の<B>{m_name}</B>が{}の<B>{t_name}</B>を攻撃し{}のダメージを与えました。",
        island_name(name),
        wrap(tags::NAME, t_point),
        wrap(tags::DISASTER, point)
    )
}

/// `logMsMonMoney`
fn ms_mon_money(m_name: &str, value: i64, unit: &str) -> String {
    format!("<B>{m_name}</B>の残骸には、<B>{value}{unit}</B>の値が付きました。")
}

/// `logFuneAttackSSS3`
fn fune_attack_sss3(name: &str, l_name: &str, t_name: &str, t_point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>が<B>エネルギー砲</B>を発射し、{}の<B>{t_name}</B>に命中。跡形もなく吹き飛びました。",
        island_name(name),
        wrap(tags::NAME, t_point)
    )
}

/// 衛星の名前 (`eis1`〜`eis6`)
const EISEI_NAMES: [&str; 6] = [
    "気象衛星",
    "観測衛星",
    "迎撃衛星",
    "軍事衛星",
    "防衛衛星",
    "イレギュラー",
];

/// 衛星を `random(2)` 減らし、1 未満になったら崩壊させる
fn wear(ctx: &mut TurnContext, island: &mut Island, i: usize) {
    island.eis[i] -= ctx.random(2);
    if island.eis[i] < 1 {
        island.eis[i] = 0;
        let message = eisei_end(&island.name, EISEI_NAMES[i]);
        ctx.log.out(ctx.turn, message, Some(island.id), None);
    }
}

/// イレギュラーが島の怪獣をすべて攻撃する
fn irregular(ctx: &mut TurnContext, island: &mut Island) {
    let (id, turn) = (island.id, ctx.turn);
    for &(x, y) in &ctx.points.clone() {
        let Some(cell) = island.map.get(x, y) else {
            continue;
        };
        if cell.kind != L::Monster as u8 {
            continue;
        }
        let (t_kind, t_name, mut t_hp) = monster_spec(cell.value);
        let mut tlv = cell.value;
        let damage = island.owner_stats.rena / 1000;
        ctx.globals.hex.point = damage.to_string();
        let t_point = format!("({x}, {y})");
        let message = ire_attackt(
            &island.name,
            "イレギュラー",
            &ctx.globals.hex.point,
            t_name,
            &t_point,
        );
        ctx.log.out(turn, message, Some(id), ctx.globals.hex.t_id);

        island.eis[5] -= 10;

        t_hp -= damage;
        tlv -= damage;
        set_value(island, x, y, tlv);
        if t_hp < 1 {
            // 対象の怪獣が倒れて荒地になる
            set(island, x, y, L::Waste, 0);
            // 報奨金
            let value = MONSTERS.get(t_kind).map(|m| m.value).unwrap_or(0);
            island.money += value;
            let message = ms_mon_money(t_name, value, &ctx.config.units.money);
            ctx.log.out(turn, message, Some(id), None);
        }
    }
}

/// 宇宙ステーションの維持
fn space_station(ctx: &mut TurnContext, island: &mut Island) {
    let (id, turn) = (island.id, ctx.turn);
    let eis7 = island.eis[6];
    let mut cstpop = trunc(eis7 as f64 / 100.0);
    let csten = eis7.rem_euclid(100);

    if island.scratch.m17 < trunc(cstpop as f64 / 10000.0) + 1 {
        ctx.log.out(turn, no_roke_cst(&island.name), Some(id), None);
        cstpop -= 1000;
    } else {
        island.money -= cstpop;
    }
    ctx.globals.command.ops.cst = (cstpop, csten);

    island.eis[6] = cstpop * 100 + csten;

    if cstpop < 1 {
        island.eis[6] = 0;
        let message = eisei_end_nopop(&island.name, "宇宙ステーション");
        ctx.log.out(turn, message, Some(id), None);
    }
    if csten < 1 {
        island.eis[6] = 0;
        let message = eisei_end(&island.name, "宇宙ステーション");
        ctx.log.out(turn, message, Some(id), None);
    }
}

/// 天空城が島の怪獣をすべて消し飛ばす
fn sky_castle(ctx: &mut TurnContext, island: &mut Island) {
    let (id, turn) = (island.id, ctx.turn);
    // 電力の判定はループの前の 1 回だけ (Perl 版のまま)
    for &(x, y) in &ctx.points.clone() {
        let Some(cell) = island.map.get(x, y) else {
            continue;
        };
        if cell.kind != L::Monster as u8 {
            continue;
        }
        let (_, t_name, _) = monster_spec(cell.value);
        ctx.globals.hex.point = (island.owner_stats.rena / 1000).to_string();
        island.scratch.shouhi += ctx.random(20000);
        let t_point = format!("({x}, {y})");
        let message = fune_attack_sss3(&island.name, "天空城", t_name, &t_point);
        ctx.log.out(turn, message, Some(id), ctx.globals.hex.t_id);

        // 対象の怪獣が倒れて荒地になる (荒地の値が 1 になる。Perl 版のまま)
        set(island, x, y, L::Waste, 1);
    }
}

pub(super) fn run(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, _p: &mut ProcRun) {
    let island = &mut islands[idx];

    for i in 0..5 {
        if island.eis[i] >= 1 {
            wear(ctx, island, i);
        }
    }
    if island.eis[5] >= 1 {
        irregular(ctx, island);
        wear(ctx, island, 5);
    }

    if island.eis[6] >= 1 {
        space_station(ctx, island);
    }

    if island.scratch.h11 >= 1 && island.scratch.shouhi < island.scratch.ene {
        sky_castle(ctx, island);
    }
}
