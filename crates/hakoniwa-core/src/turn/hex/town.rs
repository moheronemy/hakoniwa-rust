//! 町・港町・海底都市、平地、およびループ先頭の地形の整備。

use crate::land::{around, count_around, in_island, land_name};
use crate::model::Island;
use crate::tables::LandKind as L;
use crate::turn::TurnContext;

use super::{Flow, HexRun, k, msg};

/// ループの先頭: 文部科学省・島役所があれば平地を開発予定地に、荒地・砂浜を平地にする。
/// `$landKind` は書き換えないので、このあと元の地形として振り分けられる (Perl 版のまま)
pub(super) fn pre_chain(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) {
    let sc = &island.scratch;
    let (co78, co79, co80, yaku) = (sc.co78, sc.co79, sc.co80, sc.yaku);
    let g = &mut ctx.globals.hex;
    if h.land_kind == k(L::Plains) && (co78 > 0 || co80 > 0 || yaku > 0) {
        set(island, h.x, h.y, L::Plains2, 0);
        island.money -= 10000 * g.seisakuflag;
        g.seisakuflag += 1;
    }
    if (h.land_kind == k(L::Waste) || h.land_kind == k(L::Sunahama)) && (co79 > 0 || co80 > 0) {
        set(island, h.x, h.y, L::Plains, 0);
        island.money -= 30000 * g.seisakuflag;
        g.seisakuflag += 1;
    }
}

/// マスの地形と値を書き換える (値の小数部分は消える)
pub(crate) fn set(island: &mut Island, x: usize, y: usize, kind: L, value: i64) {
    if let Some(c) = island.map.get_mut(x, y) {
        c.kind = kind as u8;
        c.value = value;
        island.scratch.land_frac.remove(&(x, y));
    }
}

/// マスの値だけを書き換える (値の小数部分は消える)
pub(crate) fn set_value(island: &mut Island, x: usize, y: usize, value: i64) {
    if let Some(c) = island.map.get_mut(x, y) {
        c.value = value;
        island.scratch.land_frac.remove(&(x, y));
    }
}

/// 町の数を数える地形 (町の成長と現代都市化の判定)
pub(crate) const TOWN_KINDS: [L; 17] = [
    L::Town,
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
    L::Minato,
    L::Frocity,
    L::Onsen,
    L::Seacity,
];

/// 周囲 2 ヘックスの町系の数
pub(crate) fn town_count(island: &Island, x: usize, y: usize) -> i64 {
    TOWN_KINDS
        .iter()
        .map(|&l| count_around(&island.map, x as i64, y as i64, l, 19))
        .sum()
}

/// 町・港町・海底都市
pub(super) fn town(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) -> Flow {
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);

    let monster_count = count_around(&island.map, x as i64, y as i64, L::Monster, 7);
    if monster_count > 0 {
        h.lv -= ctx.random(20) + 10;
        set_value(island, x, y, h.lv);
        ctx.log.out(
            turn,
            msg::mons_attacks(&island.name, &land_name(h.land_kind, h.lv), &h.point()),
            Some(id),
            None,
        );
        if h.lv <= 0 {
            // 海底都市は海に、それ以外は荒地に戻す
            let to = if h.land_kind == k(L::Seacity) {
                L::Sea
            } else {
                L::Waste
            };
            set(island, x, y, to, 0);
            return Flow::Next;
        }
    }

    if town_count(island, x, y) > 17
        && ctx.random(1000) < 1
        && h.lv > 195
        && h.land_kind == k(L::Town)
    {
        // 値はそのままで現代都市になる
        island.map.get_mut(x, y).expect("in range").kind = k(L::Bigtown);
    }

    if h.addpop < 0 {
        // 不足
        h.lv -= ctx.random(-h.addpop) + 1;
        if h.lv <= 0 {
            let to = if h.land_kind == k(L::Seacity) {
                L::Sea
            } else {
                L::Plains
            };
            set(island, x, y, to, 0);
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
    Flow::Continue
}

/// 平地: 周りに農場や町があれば町になる
pub(super) fn plains(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) -> Flow {
    if ctx.random(5) == 0 && count_grow(island, h.x, h.y) {
        set(island, h.x, h.y, L::Town, 1);
        if ctx.random(1000) < island.scratch.nto * 3 {
            set(island, h.x, h.y, L::Newtown, 1);
        }
    }
    Flow::Continue
}

/// `countGrow`: 隣に (値が 1 でない) 町系か農場があるか
fn count_grow(island: &Island, x: usize, y: usize) -> bool {
    const GROW: [L; 11] = [
        L::Town,
        L::Procity,
        L::Newtown,
        L::Rizort,
        L::Kajino,
        L::BigRizort,
        L::Bettown,
        L::Skycity,
        L::Umicity,
        L::Bigtown,
        L::Farm,
    ];
    (1..7).any(|i| {
        in_island(&island.map, around(x as i64, y as i64, i))
            .and_then(|(sx, sy)| island.map.get(sx, sy))
            .is_some_and(|c| GROW.iter().any(|&l| c.kind == k(l)) && c.value != 1)
    })
}
