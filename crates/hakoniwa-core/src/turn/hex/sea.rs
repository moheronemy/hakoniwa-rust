//! 海上都市・船舶。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 船の移動済みの印 `@funeMove` は `my` の無いグローバル変数で、doEachHex のたびに
//!   消されない。ある島で船が (x, y) に動くと、そのターンに後で処理する島の (x, y) にいる
//!   船は「すでに動いた後」として何もしない。[`Globals::fune_move`] で持つ。
//! - 海上都市と船の移動は、移動先に印を付けない (海上都市) か、付けても同じ島の後の
//!   マスでしか見ない。移動先のマスがまだ処理されていなければ、海上都市はもう一度成長・移動する。
//! - 船が老朽化で沈む (海になる) と、続けて読み直した値 0 で「漁船・改」の収入
//!   (保険金のログ) が出て、さらに海のマスが「移動」する (移動先は海のまま、元の位置も海)。
//! - 豪華客船が沈んで氷山になると、その氷山が船と同じように移動する。
//! - 戦艦ERADICATE・改のエネルギー砲の暴発は、怪獣の周りではなく自分の周り (自分の位置を含む
//!   4 マス) を壊す。自分のマスは海になり、そのあと海のマスが「移動」する。
//! - 内側のループはどれも `my($i)` を宣言しているので、外側のループの添字は変わらない。

use std::collections::HashMap;

use crate::land::{around, in_island, land_name};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::trunc;
use crate::tables::{LandKind as L, MONSTERS, SHIPS};
use crate::turn::{TurnContext, monster_spec};

use super::town::{set, set_value};
use super::{Flow, HexRun, k, msg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `@funeMove` (座標 → 移動済みの印)。島をまたいで残る
    pub fune_move: HashMap<(usize, usize), i64>,
    /// `$heat` (エネルギー砲を撃った回数)。島をまたいで増え続ける
    pub heat: i64,
    /// `$rena` (直前にエネルギー砲を撃った島の `rena`)
    pub rena: i64,
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| kind == k(l))
}

/// 海上都市・船が移動できない地形 (「海、海基、海底都市、油田、怪獣、山、記念碑以外」の判定)
const MOVE_BLOCKED: [L; 69] = [
    L::Waste,
    L::Plains,
    L::Plains2,
    L::Town,
    L::Forest,
    L::Farm,
    L::EneAt,
    L::EneFw,
    L::EneWt,
    L::EneWd,
    L::EneBo,
    L::EneSo,
    L::EneCs,
    L::Conden,
    L::Conden2,
    L::Conden3,
    L::Conden4,
    L::Foodim,
    L::Foodka,
    L::Farmchi,
    L::Farmpic,
    L::Farmcow,
    L::College,
    L::Yakusho,
    L::Factory,
    L::HTFactory,
    L::SHTF,
    L::OWNF,
    L::Base,
    L::Defence,
    L::Minato,
    L::Seki,
    L::Park,
    L::Haribote,
    L::Sbase,
    L::Seacity,
    L::Fune,
    L::Ice,
    L::Frocity,
    L::Umiamu,
    L::Oil,
    L::Gold,
    L::Mountain,
    L::Onsen,
    L::Monument,
    L::Mine,
    L::Nursery,
    L::Kyujo,
    L::Kyujokai,
    L::Zoo,
    L::RottenSea,
    L::Procity,
    L::Newtown,
    L::Bigtown,
    L::Bettown,
    L::Skycity,
    L::Umicity,
    L::Seatown,
    L::Rizort,
    L::Kajino,
    L::BigRizort,
    L::Shuto,
    L::Umishuto,
    L::House,
    L::Taishi,
    L::Train,
    L::Kura,
    L::Kuraf,
    L::Monster,
];

/// 船の攻撃の巻き添えで壊れない地形
const BLAST_SAFE: [L; 14] = [
    L::Sea,
    L::Oil,
    L::Ice,
    L::Waste,
    L::Mountain,
    L::Gold,
    L::Onsen,
    L::Seacity,
    L::Seatown,
    L::Umishuto,
    L::Umiamu,
    L::Fune,
    L::Frocity,
    L::Sbase,
];

/// 動く方向を決める (3 回まで試す)。動けなければ `None`
fn choose_move(
    ctx: &mut TurnContext,
    island: &Island,
    x: usize,
    y: usize,
) -> Option<(usize, usize)> {
    for _ in 0..3 {
        let d = (ctx.random(6) + 1) as usize;
        // 範囲外判定
        let Some((sx, sy)) = in_island(&island.map, around(x as i64, y as i64, d)) else {
            continue;
        };
        let kind = island.map.get(sx, sy).unwrap_or_default().kind;
        if !is_one_of(kind, &MOVE_BLOCKED) {
            return Some((sx, sy));
        }
    }
    None
}

/// (x, y) の地形と値を (sx, sy) に写し、もと居た位置を海にする
fn move_cell(island: &mut Island, (x, y): (usize, usize), (sx, sy): (usize, usize)) {
    let cell = island.map.get(x, y).unwrap_or_default();
    let frac = island.scratch.land_frac.get(&(x, y)).copied();
    if let Some(c) = island.map.get_mut(sx, sy) {
        *c = cell;
    }
    match frac {
        Some(f) => island.scratch.land_frac.insert((sx, sy), f),
        None => island.scratch.land_frac.remove(&(sx, sy)),
    };
    set(island, x, y, L::Sea, 0);
}

/// 海上都市: 町と同じように成長し、海の上を動く
pub(super) fn frocity(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    if h.addpop < 0 {
        // 不足
        h.lv -= ctx.random(-h.addpop) + 1;
        if h.lv <= 0 {
            // 平地に戻す
            set(island, x, y, L::Plains, 0);
            return Flow::Next;
        }
    } else if h.lv < 100 {
        // 成長
        h.lv += ctx.random(h.addpop) + 1;
        if h.lv > 100 {
            h.lv = 100;
        }
    } else if h.addpop2 > 0 {
        // 都市になると成長遅い
        h.lv += ctx.random(h.addpop2) + 1;
    }
    if h.lv > 200 {
        h.lv = 200;
    }
    set_value(island, x, y, h.lv);

    let Some(to) = choose_move(ctx, island, x, y) else {
        // 動かなかった
        return Flow::Next;
    };
    // 移動先には印を付けないので、後で処理するマスに動くとまた成長・移動する (Perl 版のまま)
    move_cell(island, (x, y), to);
    Flow::Continue
}

/// `$HfuneSpecial[$lv]` (範囲外は未定義 = 0、負の添字は末尾から)
fn fune_special(lv: i64) -> i64 {
    let n = SHIPS.len() as i64;
    let i = if lv < 0 { lv + n } else { lv };
    usize::try_from(i)
        .ok()
        .and_then(|i| SHIPS.get(i))
        .map_or(0, |s| s.2)
}

/// `seqnum($v)`: `sin($v + 1234)` を文字列にした最後から 2 文字目 (数字でなければ 0)
fn seqnum(v: i64) -> i64 {
    let s = perl_num_string((v as f64 + 1234.0).sin());
    let chars: Vec<char> = s.chars().collect();
    chars
        .len()
        .checked_sub(2)
        .and_then(|i| chars[i].to_digit(10))
        .map_or(0, i64::from)
}

/// Perl が浮動小数点数を文字列にするときの形 (`%.15g`)
fn perl_num_string(v: f64) -> String {
    if v == 0.0 {
        return "0".into();
    }
    let e = format!("{v:.14e}");
    let (mantissa, exp) = e.split_once('e').expect("exponent");
    let exp: i32 = exp.parse().expect("exponent");
    let strip = |s: &str| -> String {
        if s.contains('.') {
            s.trim_end_matches('0').trim_end_matches('.').to_string()
        } else {
            s.to_string()
        }
    };
    if (-4..15).contains(&exp) {
        let decimals = (14 - exp) as usize;
        strip(&format!("{v:.decimals$}"))
    } else {
        let sign = if exp < 0 { '-' } else { '+' };
        format!("{}e{sign}{:02}", strip(mantissa), exp.abs())
    }
}

/// 船舶: 漁・観光・探索をし、戦艦は怪獣を攻撃し、海の上を動く
pub(super) fn fune(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    let here = h.point();

    if ctx.globals.hex.sea.fune_move.get(&(x, y)).copied() == Some(2) {
        // すでに動いた後
        return Flow::Next;
    }

    // 老朽化判定
    let flv = island.map.get(x, y).unwrap_or_default().value;
    let l_name = land_name(h.land_kind, h.lv);
    let sinks = if flv == 8 || flv == 9 || flv == 19 || flv == 10 {
        ctx.random(1000) < 5
    } else {
        ctx.random(100) < 3
    };
    if sinks {
        ctx.log.out(
            turn,
            park_endf(&island.name, &l_name, &here),
            Some(id),
            None,
        );
        set(island, x, y, L::Sea, 0);
    }

    // 沈んだあとは値 0 として続ける (Perl 版のまま)
    let flv = island.map.get(x, y).unwrap_or_default().value;
    let funespe = fune_special(h.lv);
    let money_unit = ctx.config.units.money.clone();

    match flv {
        0 => {
            let value = 1 + ctx.random(399);
            island.money += value;
            let s = format!("{value}{money_unit}");
            if value > 0 {
                ctx.log.out(
                    turn,
                    hoken(&island.name, &l_name, &here, &s),
                    Some(id),
                    None,
                );
            }
        }
        1 => fish(ctx, island, 5, 290, 30),
        2 => fish(ctx, island, 20, 490, 40),
        3 => {
            island.money -= 300;
            if ctx.random(1000) < 5 {
                treasure(ctx, island, &l_name, &here, 49999);
            }
        }
        4 => {
            let value = 150 + ctx.random(250);
            island.money += value;
            let s = format!("{value}{money_unit}");
            if value > 0 {
                ctx.log.out(
                    turn,
                    park_moneyf(&island.name, &l_name, &here, &s),
                    Some(id),
                    None,
                );
            }
            island.food -= 1000;
        }
        5 | 11 => fish(ctx, island, 60, 690, 40),
        6 => fish(ctx, island, 30, 490, 40),
        7 => {
            island.money -= 500;
            if ctx.random(100) < 1 {
                treasure(ctx, island, &l_name, &here, 29999);
            }
        }
        8 => {
            let value = 1500 + trunc(island.pop as f64 / 10.0);
            island.money += value;
            let s = format!("{value}{money_unit}");
            if value > 0 {
                ctx.log.out(
                    turn,
                    park_moneyf(&island.name, &l_name, &here, &s),
                    Some(id),
                    None,
                );
            }
            island.food -= 3000;
            if ctx.random(100) < 10 {
                ctx.log
                    .out(turn, titanic(&island.name, &l_name, &here), Some(id), None);
                let value = trunc(island.pop as f64 / 10.0) * 2;
                island.money += value;
                let s = format!("{value}{money_unit}");
                if value > 0 {
                    ctx.log.out(
                        turn,
                        titanic_end(&island.name, &l_name, &here, &s),
                        Some(id),
                        None,
                    );
                }
                // 氷山になり、このあと氷山が移動する (Perl 版のまま)
                set(island, x, y, L::Ice, 0);
            }
        }
        9 => {
            island.money -= 100;
            renas(ctx, island, &l_name, &here);
        }
        10 => {
            island.money -= 400;
            eradicate(ctx, island, &l_name, &here);
        }
        19 => {
            island.money -= 1000;
            eradicate_kai(ctx, island, h, &l_name, &here);
        }
        _ => {}
    }

    // 動く方向を決定
    let Some((sx, sy)) = choose_move(ctx, island, x, y) else {
        // 動かなかった
        return Flow::Next;
    };
    move_cell(island, (x, y), (sx, sy));

    // 油田見っけ
    let oil_chance = match flv {
        3 => Some(30 - island.scratch.oil * 3),
        7 => Some(40 - island.scratch.oil * 4),
        _ => None,
    };
    if let Some(chance) = oil_chance
        && ctx.rand_f64(1000.0) < chance as f64
    {
        let c = island.map.get(sx, sy).unwrap_or_default();
        let name = land_name(c.kind, c.value);
        ctx.log.out(
            turn,
            tansaku_oil(&island.name, &name, &here),
            Some(id),
            None,
        );
        set(island, x, y, L::Oil, 0);
        island.scratch.oil += 1;
    }

    // 移動済みフラグ
    let moved = &mut ctx.globals.hex.sea.fune_move;
    match funespe {
        // 移動済みフラグは立てない
        2 => {}
        // 速い船
        1 => {
            let v = moved.get(&(x, y)).copied().unwrap_or(0) + 1;
            moved.insert((sx, sy), v);
        }
        _ => {
            moved.insert((sx, sy), 2);
        }
    }
    Flow::Continue
}

/// 漁船: 維持費を払い、食料を取る
fn fish(ctx: &mut TurnContext, island: &mut Island, cost: i64, base: i64, range: i64) {
    island.money -= cost;
    let value = base + ctx.random(range);
    island.food += value;
    ctx.globals.hex.gyosenincome += value;
}

/// 探査船: 財宝を見つける
fn treasure(ctx: &mut TurnContext, island: &mut Island, l_name: &str, point: &str, range: i64) {
    let value = 1 + ctx.random(range);
    island.money += value;
    let s = format!("{value}{}", ctx.config.units.money);
    if value > 0 {
        ctx.log.out(
            ctx.turn,
            tansaku(&island.name, l_name, point, &s),
            Some(island.id),
            None,
        );
    }
}

/// 怪獣を探して島の全マスを見る順 (`@Hrpx`, `@Hrpy` の順)
fn monster_points(ctx: &TurnContext) -> Vec<(usize, usize)> {
    let n = ctx.config.point_number();
    ctx.points.iter().take(n).copied().collect()
}

fn is_monster(island: &Island, sx: usize, sy: usize) -> bool {
    island
        .map
        .get(sx, sy)
        .is_some_and(|c| c.kind == k(L::Monster))
}

/// 戦艦RENAS: 島の怪獣を (1 ターンに 2 回まで) 攻撃する
fn renas(ctx: &mut TurnContext, island: &mut Island, l_name: &str, here: &str) {
    let (id, turn) = (island.id, ctx.turn);
    for (sx, sy) in monster_points(ctx) {
        if !is_monster(island, sx, sy) || ctx.globals.hex.kougekiseigen >= 2 {
            continue;
        }
        let t_value = island.map.get(sx, sy).unwrap_or_default().value;
        let (t_kind, t_name, mut t_hp) = monster_spec(t_value);
        let mut tlv = t_value;
        let t_special = MONSTERS.get(t_kind).map_or(0, |m| m.special);
        if (t_special == 3 && turn % 2 == 1)
            || (t_special == 8 && seqnum(turn) % 2 == 0)
            || (t_special == 4 && turn % 2 == 0)
        {
            // 対象が硬化中なら効果なし
            continue;
        }
        // `$tPoint` は代入されていないグローバル変数なので空 (Perl 版のまま)
        let t_id = ctx.globals.hex.t_id;
        ctx.log.out(
            turn,
            mons_attackt(&island.name, l_name, here, t_name, ""),
            Some(id),
            t_id,
        );
        ctx.globals.hex.kougekiseigen += 1;

        t_hp -= 1;
        if t_hp != 0 {
            // 対象の体力を減らす
            tlv -= 1;
            set_value(island, sx, sy, tlv);
        } else {
            // 対象の怪獣が倒れて荒地になる
            set(island, sx, sy, L::Waste, 0);
            // 報奨金
            let value = MONSTERS.get(t_kind).map_or(0, |m| m.value);
            island.money += value;
            ctx.log.out(
                turn,
                ms_mon_money(t_name, value, &ctx.config.units.money),
                Some(id),
                None,
            );
        }
    }
}

/// 戦艦ERADICATE: 島の怪獣すべてに多弾頭ミサイルを撃つ
fn eradicate(ctx: &mut TurnContext, island: &mut Island, l_name: &str, here: &str) {
    let (id, turn) = (island.id, ctx.turn);
    for (sx, sy) in monster_points(ctx) {
        if !is_monster(island, sx, sy) {
            continue;
        }
        island.money -= 3000;
        let t_value = island.map.get(sx, sy).unwrap_or_default().value;
        let (_, t_name, _) = monster_spec(t_value);
        let t_id = ctx.globals.hex.t_id;
        ctx.log.out(
            turn,
            fune_attack(&island.name, l_name, here, t_name),
            Some(id),
            t_id,
        );
        for i in 0..7 {
            let Some((ssx, ssy)) = in_island(&island.map, around(sx as i64, sy as i64, i)) else {
                continue;
            };
            let c = island.map.get(ssx, ssy).unwrap_or_default();
            let name = land_name(c.kind, c.value);
            let point = format!("({ssx}, {ssy})");
            if i < 1 {
                // 中心は浅瀬になる
                set(island, ssx, ssy, L::Sea, 1);
                ctx.log.out(
                    turn,
                    fune_monster_sea(&island.name, &name, &point),
                    Some(id),
                    None,
                );
            } else {
                blast(ctx, island, c.kind, &name, (ssx, ssy), &point);
            }
        }
    }
}

/// 戦艦ERADICATE・改: 島の怪獣すべてにエネルギー砲を撃つ。オーバーヒートすると自分の周りが壊れる
fn eradicate_kai(ctx: &mut TurnContext, island: &mut Island, h: &HexRun, l_name: &str, here: &str) {
    let (id, turn) = (island.id, ctx.turn);
    for (sx, sy) in monster_points(ctx) {
        if !is_monster(island, sx, sy) {
            continue;
        }
        island.money -= 50000;
        let t_value = island.map.get(sx, sy).unwrap_or_default().value;
        let (_, t_name, _) = monster_spec(t_value);
        let t_id = ctx.globals.hex.t_id;
        ctx.log.out(
            turn,
            fune_attack_sss(&island.name, l_name, here, t_name),
            Some(id),
            t_id,
        );
        set(island, sx, sy, L::Waste, 0);
        let g = &mut ctx.globals.hex.sea;
        g.heat += 1;
        g.rena = island.owner_stats.rena;
        let (rena, heat) = (g.rena, g.heat);
        if ctx.rand_f64(rena as f64) > (3000 + heat * 1000) as f64 {
            ctx.log
                .out(turn, fune_attack_sssr(&island.name, t_name), Some(id), t_id);
            continue;
        }
        ctx.log.out(
            turn,
            fune_attack_ssst(&island.name, l_name, t_name),
            Some(id),
            t_id,
        );
        // 怪獣ではなく自分の周りを壊す (Perl 版のまま)
        for i in 0..4 {
            let Some((ssx, ssy)) = in_island(&island.map, around(h.x as i64, h.y as i64, i)) else {
                continue;
            };
            let c = island.map.get(ssx, ssy).unwrap_or_default();
            let name = land_name(c.kind, c.value);
            let point = format!("({ssx}, {ssy})");
            if i < 1 {
                set(island, ssx, ssy, L::Sea, 0);
            } else {
                blast(ctx, island, c.kind, &name, (ssx, ssy), &point);
            }
        }
    }
}

/// 巻き添え (2 ヘックスの扱い): 海などはそのまま、怪獣は消し飛び、ほかは荒地になる
fn blast(
    ctx: &mut TurnContext,
    island: &mut Island,
    kind: u8,
    name: &str,
    (sx, sy): (usize, usize),
    point: &str,
) {
    if is_one_of(kind, &BLAST_SAFE) {
        return;
    }
    let message = if kind == k(L::Monster) {
        wide_damage_monster(&island.name, name, point)
    } else {
        wide_damage_waste(&island.name, name, point)
    };
    ctx.log.out(ctx.turn, message, Some(island.id), None);
    set(island, sx, sy, L::Waste, 0);
}

/// `logHoken`
fn hoken(name: &str, l_name: &str, point: &str, s: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>の事故により、<B>{s}</B>の保険がおりました。",
        msg::island_at(name, point)
    )
}

/// `logParkMoneyf`
fn park_moneyf(name: &str, l_name: &str, point: &str, s: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>から、<B>{s}</B>の観光収入が上がりました。",
        msg::island_at(name, point)
    )
}

/// `logTitanicEnd`
fn titanic_end(name: &str, l_name: &str, point: &str, s: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>の沈没は映画化され、多くの人が涙を流しました。(<B>{s}</B>の利益収入)",
        msg::island_at(name, point)
    )
}

/// `logTansaku`
fn tansaku(name: &str, l_name: &str, point: &str, s: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>が財宝を発見！<B>{s}</B>の価値があることがわかりました。",
        msg::island_at(name, point)
    )
}

/// `logTansakuoil`
fn tansaku_oil(name: &str, l_name: &str, point: &str) -> String {
    format!(
        "{}で<B>{l_name}</B>が油田を発見！",
        msg::island_at(name, point)
    )
}

/// `logParkEndf`
fn park_endf(name: &str, l_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>は事故ため沈没しました。",
        msg::island_at(name, point)
    )
}

/// `logTitanic`
fn titanic(name: &str, l_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>は氷山に激突し真っ二つになり沈没しました。",
        msg::island_at(name, point)
    )
}

/// `logMsMonMoney`
fn ms_mon_money(m_name: &str, value: i64, unit: &str) -> String {
    format!("<B>{m_name}</B>の残骸には、<B>{value}{unit}</B>の値が付きました。")
}

/// `logMonsAttackt`
fn mons_attackt(name: &str, m_name: &str, point: &str, t_name: &str, t_point: &str) -> String {
    format!(
        "{}の<B>{m_name}</B>が{}の<B>{t_name}</B>を攻撃しました。",
        msg::island_at(name, point),
        wrap(tags::NAME, t_point)
    )
}

/// `logFuneAttack`
fn fune_attack(name: &str, l_name: &str, point: &str, t_name: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>が多弾頭ミサイルを発射し、<B>{t_name}</B>に命中しました。",
        msg::island_at(name, point)
    )
}

/// `logFuneAttackSSS`
fn fune_attack_sss(name: &str, l_name: &str, point: &str, t_name: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>が<B>エネルギー砲</B>を発射し、<B>{t_name}</B>に命中しました。",
        msg::island_at(name, point)
    )
}

/// `logFuneAttackSSSR`
fn fune_attack_sssr(name: &str, t_name: &str) -> String {
    format!(
        "{}の<B>{t_name}</B>は<B>木っ端微塵</B>になりました。",
        msg::island(name)
    )
}

/// `logFuneAttackSSST`
fn fune_attack_ssst(name: &str, l_name: &str, t_name: &str) -> String {
    format!(
        "{}の<B>{t_name}</B>は<B>木っ端微塵</B>になり、<B>{l_name}</B>は{}により{}しました。",
        msg::island(name),
        wrap(tags::DISASTER, "オーバーヒート"),
        wrap(tags::DISASTER, "大爆発")
    )
}

/// `logFuneMonsterSea`
fn fune_monster_sea(name: &str, l_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>は吹き飛び水没しました。",
        msg::island_at(name, point)
    )
}

/// `logWideDamageMonster`
fn wide_damage_monster(name: &str, l_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>は消し飛びました。",
        msg::island_at(name, point)
    )
}

/// `logWideDamageWaste`
fn wide_damage_waste(name: &str, l_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>は一瞬にして<B>荒地</B>と化しました。",
        msg::island_at(name, point)
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn perl_number_strings() {
        assert_eq!(perl_num_string(0.5), "0.5");
        assert_eq!(perl_num_string(-0.25), "-0.25");
        assert_eq!(perl_num_string(1.0 / 3.0), "0.333333333333333");
        assert_eq!(perl_num_string(1e-5), "1e-05");
        assert_eq!(perl_num_string(0.0001), "0.0001");
    }

    /// Perl の `sin($t + 1234)` と `seqnum($t)` で確かめた値
    #[test]
    fn seqnum_matches_perl() {
        assert_eq!(perl_num_string(-0.0708424422185499), "-0.0708424422185499");
        let cases = [
            (1, 2),
            (2, 8),
            (3, 6),
            (4, 8),
            (5, 0),
            (6, 7),
            (7, 9),
            (8, 0),
            (9, 5),
            (10, 5),
            (11, 7),
            (12, 5),
            (100, 9),
            (1234, 0),
            (99999, 5),
        ];
        for (turn, want) in cases {
            assert_eq!(seqnum(turn), want, "turn {turn}");
        }
    }
}
