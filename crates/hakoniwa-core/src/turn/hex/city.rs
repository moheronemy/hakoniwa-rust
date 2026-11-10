//! 防災都市・ニュータウン・現代都市・海底新都市・輝ける都市・空中都市・海都市・首都・温泉街。
//!
//! Perl 版のこれらの分岐が書き換える `$lv` は doEachHex の `my` 変数なので、
//! 書き換え後の値 ([`HexRun::lv`]) で共通の災害判定をする。

use crate::land::{AX, AY, count_around, land_name, perl_get};
use crate::model::Island;
use crate::tables::LandKind as L;
use crate::turn::{TurnContext, monster_spec};

use super::industry::oil_end;
use super::town::{set, set_value, town_count};
use super::{Flow, HexRun, k, msg};

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

/// 隣に怪獣がいれば攻撃され、値が `random(n) + base` 減る (いなければ乱数を引かない)。
/// 値が 0 以下になったら `to` にして `true` (Perl の `next`)
fn monster_attack(
    ctx: &mut TurnContext,
    island: &mut Island,
    h: &mut HexRun,
    (n, base): (i64, i64),
    to: L,
) -> bool {
    if count_around(&island.map, h.x as i64, h.y as i64, L::Monster, 7) == 0 {
        return false;
    }
    h.lv -= ctx.random(n) + base;
    set_value(island, h.x, h.y, h.lv);
    ctx.log.out(
        ctx.turn,
        msg::mons_attacks(&island.name, &land_name(h.land_kind, h.lv), &h.point()),
        Some(island.id),
        None,
    );
    if h.lv <= 0 {
        set(island, h.x, h.y, to, 0);
        return true;
    }
    false
}

/// 人口の増減の共通部分。
/// 不足なら減らし、0 以下になったら `shrink_to` にして `true` (Perl の `next`)。
/// 成長は `soft_cap` まで (`clamp_soft` なら超えた分を切る)、そこからは `addpop2` で
fn grow(
    ctx: &mut TurnContext,
    island: &mut Island,
    h: &mut HexRun,
    shrink_to: L,
    soft_cap: i64,
    clamp_soft: bool,
) -> bool {
    if h.addpop < 0 {
        h.lv -= ctx.random(-h.addpop) + 1;
        if h.lv <= 0 {
            set(island, h.x, h.y, shrink_to, 0);
            return true;
        }
    } else if h.lv < soft_cap {
        h.lv += ctx.random(h.addpop) + 1;
        if clamp_soft && h.lv > soft_cap {
            h.lv = soft_cap;
        }
    } else if h.addpop2 > 0 {
        h.lv += ctx.random(h.addpop2) + 1;
    }
    false
}

/// 値の上限を掛けて書き込む
fn store(island: &mut Island, h: &mut HexRun, cap: i64) {
    if h.lv > cap {
        h.lv = cap;
    }
    set_value(island, h.x, h.y, h.lv);
}

/// 防災都市。値が 200 になると隣の怪獣を倒す
pub(super) fn procity(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if grow(ctx, island, h, L::Plains, 100, true) {
        return Flow::Next;
    }
    store(island, h, 200);

    if h.lv == 200 {
        // 内側のループの $i は my で宣言した別の変数。
        // Perl 版はここだけ行による位置調整も範囲の確認もしない。負の添字は反対側の端を指し、
        // 書き込みもそのマスに行く (Perl 版のまま)
        let size = island.map.size as i64;
        for i in 1..7 {
            let sx = h.x as i64 + AX[i];
            let sy = h.y as i64 + AY[i];
            let (kind, lv) = perl_get(&island.map, sx, sy);
            if kind != k(L::Monster) {
                continue;
            }
            let (_, t_name, _) = monster_spec(lv);
            ctx.log.out(
                ctx.turn,
                format!(
                    "{}の<B>{t_name}</B>が<B>強力な力場</B>に押し潰されました。",
                    msg::island_at(&island.name, &format!("({sx}, {sy})"))
                ),
                Some(island.id),
                ctx.globals.hex.t_id,
            );
            // perl_get が怪獣を返したので、折り返した座標は島の中にある
            let wx = if sx < 0 { sx + size } else { sx } as usize;
            let wy = if sy < 0 { sy + size } else { sy } as usize;
            set(island, wx, wy, L::Waste, 1);
        }
    }
    Flow::Continue
}

/// ニュータウン。町が密集していると現代都市になる (値はそのまま)
pub(super) fn newtown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if town_count(island, h.x, h.y) > 17 && ctx.random(1000) < 3 && h.lv > 295 {
        island.map.get_mut(h.x, h.y).expect("in range").kind = k(L::Bigtown);
    }
    if grow(ctx, island, h, L::Plains, 100, true) {
        return Flow::Next;
    }
    store(island, h, 300);
    Flow::Continue
}

/// 現代都市・海底新都市が首都になる判定 (島に首都が無く、隣に家が 1 つ、町が密集している)
fn make_shuto(ctx: &mut TurnContext, island: &mut Island, h: &HexRun, to: L) {
    let towns = town_count(island, h.x, h.y);
    let houses = count_around(&island.map, h.x as i64, h.y as i64, L::House, 7);
    if island.scratch.shu == 0 && houses == 1 && towns > 16 && ctx.random(1000) < 300 {
        island.map.get_mut(h.x, h.y).expect("in range").kind = k(to);
        let s_name = format!("{}シティー", island.onm);
        island.totoyoso2 = s_name.clone();
        let l_name = land_name(h.land_kind, h.lv);
        ctx.log.out(
            ctx.turn,
            format!(
                "{}の<B>{l_name}</B>は、<B>首都{s_name}</B>として島の中心的都市へとなりました。",
                msg::island_at(&island.name, &h.point())
            ),
            Some(island.id),
            None,
        );
        ctx.log.history(
            ctx.turn,
            format!(
                "{}に<B>首都{s_name}</B>が出来ました。",
                msg::island(&island.name)
            ),
        );
        island.scratch.shu += 1;
    }
}

/// 現代都市
pub(super) fn bigtown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if monster_attack(ctx, island, h, (20, 10), L::Waste) {
        return Flow::Next;
    }
    make_shuto(ctx, island, h, L::Shuto);
    if grow(ctx, island, h, L::Plains, 200, true) {
        return Flow::Next;
    }
    store(island, h, 500);
    Flow::Continue
}

/// 海底新都市 (首都になると海底首都)
pub(super) fn seatown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    make_shuto(ctx, island, h, L::Umishuto);
    if grow(ctx, island, h, L::Sea, 250, true) {
        return Flow::Next;
    }
    store(island, h, 400);
    Flow::Continue
}

/// 輝ける都市: 島に首都があり、隣に首都か輝ける都市があるときだけ成長する
pub(super) fn bettown(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if monster_attack(ctx, island, h, (20, 10), L::Waste) {
        return Flow::Next;
    }
    let (x, y) = (h.x as i64, h.y as i64);
    let shuto_count = count_around(&island.map, x, y, L::Shuto, 7)
        + count_around(&island.map, x, y, L::Umishuto, 7);
    // 自分も数えるので、隣に 1 つあれば 2
    let bet_count = count_around(&island.map, x, y, L::Bettown, 7);
    if h.addpop < 0 {
        h.lv -= ctx.random(-h.addpop) + 1;
        if h.lv <= 0 {
            set(island, h.x, h.y, L::Plains, 0);
            return Flow::Next;
        }
    } else if island.scratch.shu > 0 && (shuto_count > 0 || bet_count > 1) {
        if h.lv < 1000 {
            h.lv += ctx.random(h.addpop) + 1;
            if h.lv > 1000 {
                h.lv = 1000;
            }
        } else if h.addpop2 > 0 {
            h.lv += ctx.random(h.addpop2) + 1;
        }
    }
    store(island, h, 2000);
    Flow::Continue
}

/// 空中都市
pub(super) fn skycity(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if monster_attack(ctx, island, h, (20, 10), L::Waste) {
        return Flow::Next;
    }
    // 2250 で止めない (Perl 版のまま)
    if grow(ctx, island, h, L::Plains, 2250, false) {
        return Flow::Next;
    }
    store(island, h, 3000);
    Flow::Continue
}

/// 海都市
pub(super) fn umicity(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if monster_attack(ctx, island, h, (20, 10), L::Sea) {
        return Flow::Next;
    }
    // 2500 で止めない (Perl 版のまま)
    if grow(ctx, island, h, L::Sea, 2500, false) {
        return Flow::Next;
    }
    store(island, h, 3000);
    Flow::Continue
}

/// 首都・海底首都
pub(super) fn shuto(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if island.scratch.shu > 1 {
        // 首都が 2 つ以上あれば開発予定地にする。このあとも処理を続け、
        // 開発予定地に人口の値を書き込む (Perl 版のまま)
        set(island, h.x, h.y, L::Plains2, 0);
        island.scratch.shu -= 1;
    }
    // 怪獣に壊されたときの戻し先は、海底首都なら海、首都なら平地
    let to = if h.land_kind == k(L::Umishuto) {
        L::Sea
    } else {
        L::Plains
    };
    if monster_attack(ctx, island, h, (100, 200), to) {
        return Flow::Next;
    }
    // 不足で 0 以下になると、首都でも海になる (Perl 版のまま)
    if grow(ctx, island, h, L::Sea, 750, true) {
        return Flow::Next;
    }
    store(island, h, 4000);
    Flow::Continue
}

/// 温泉街: 収入と枯渇 (枯渇すると山になる)
pub(super) fn onsen(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if grow(ctx, island, h, L::Plains, 50, true) {
        return Flow::Next;
    }
    store(island, h, 100);

    let nt = town_count(island, h.x, h.y);
    let value = ctx.random(nt * 20 + h.lv * 5 + island.pop / 20) + ctx.random(100) + 100;
    let l_name = land_name(h.land_kind, h.lv);
    if value > 0 {
        island.money += value;
        ctx.log.oil_money(
            ctx.turn,
            island.id,
            &island.name,
            (h.x, h.y),
            (h.land_kind, h.lv),
            value,
            &ctx.config.units.money,
        );
    }
    if ctx.random(1000) < 10 {
        ctx.log.out(
            ctx.turn,
            oil_end(&island.name, &l_name, &h.point()),
            Some(island.id),
            None,
        );
        set(island, h.x, h.y, L::Mountain, 0);
    }
    Flow::Continue
}
