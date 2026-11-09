//! 全マス共通の判定 (地形ごとの分岐のあと): 核融合発電所の暴走、コンデンサの漏電、
//! 小彗星、火災。

use crate::land::{around, count_around, in_island, land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::tables::LandKind as L;
use crate::turn::TurnContext;

use super::town::{set, set_value};
use super::{Flow, HexRun, k, msg};

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| kind == k(l))
}

/// 海にあって、壊れると跡形もなくなるもの
const SEA_THINGS: [L; 9] = [
    L::Sbase,
    L::Seacity,
    L::Seatown,
    L::Umishuto,
    L::Fune,
    L::Ice,
    L::Frocity,
    L::Umiamu,
    L::Oil,
];

pub(super) fn post_chain(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if h.land_kind == k(L::Conden4) && h.lv == 99 {
        fusion(ctx, island, h);
    }
    if (h.land_kind == k(L::Conden2) || h.land_kind == k(L::Conden3))
        && island.scratch.roudenflag == 0
    {
        leak(ctx, island, h);
    }
    if (h.land_kind == k(L::Conden2)
        || h.land_kind == k(L::Conden3)
        || (h.land_kind == k(L::College) && h.lv == 8))
        && island.scratch.roudenflag == 0
    {
        meteor(ctx, island, h);
    }
    fire(ctx, island, h)
}

/// 核融合発電所: 魔力のバランスが崩れていると周囲を押し潰す
fn fusion(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) {
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    let cell = island.map.get(x, y).unwrap_or_default();
    let l_name = land_name(cell.kind, cell.value);
    let magic = ctx.globals.hex.etc9.update(&island.etc_raw[4]);
    let (magica, magicl) = (magic[3], magic[5]);
    if magica == magicl {
        return;
    }
    ctx.log.out(
        turn,
        rouden2(&island.name, &l_name, &h.point()),
        Some(id),
        None,
    );

    // $s02 は直前に分解した政策の値 (グローバル変数)
    let yh = if ctx.globals.etc5.0[2] >= 25 { 7 } else { 19 };
    let t_id = ctx.globals.hex.t_id;
    for i in 1..yh {
        let (sx, sy) = around(x as i64, y as i64, i);
        let Some((sx, sy)) = in_island(&island.map, (sx, sy)) else {
            continue;
        };
        let c = island.map.get(sx, sy).unwrap_or_default();
        let name = land_name(c.kind, c.value);
        let point = format!("({sx}, {sy})");
        if i < 7 {
            if c.kind == k(L::Sea) {
                set_value(island, sx, sy, 0);
            } else if is_one_of(c.kind, &SEA_THINGS) {
                ctx.log.out(
                    turn,
                    wide_damage_sea2(&island.name, &name, &point),
                    Some(id),
                    None,
                );
                set(island, sx, sy, L::Sea, 0);
            } else {
                ctx.log.out(
                    turn,
                    baria_attack(&island.name, &name, &point),
                    Some(id),
                    t_id,
                );
                // i は 1 以上なので浅瀬になる
                set(island, sx, sy, L::Sea, 1);
            }
        } else if !is_one_of(
            c.kind,
            &[
                L::Sea,
                L::Ice,
                L::Oil,
                L::Waste,
                L::Mountain,
                L::Gold,
                L::Onsen,
                L::Seacity,
                L::Umishuto,
                L::Seatown,
                L::Fune,
                L::Frocity,
                L::Umiamu,
                L::Sbase,
            ],
        ) {
            ctx.log.out(
                turn,
                baria_attack(&island.name, &name, &point),
                Some(id),
                t_id,
            );
            set(island, sx, sy, L::Waste, 0);
        }
    }
}

/// コンデンサ・改、黄金のコンデンサの漏電
fn leak(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) {
    let (x, y) = (h.x, h.y);
    let cell = island.map.get(x, y).unwrap_or_default();
    let l_name = land_name(cell.kind, cell.value);
    if (ctx.random(150_000) as f64) < 125.0 + island.scratch.co8 as f64 / 2.5 {
        ctx.log.out(
            ctx.turn,
            format!(
                "{}の<B>{l_name}</B>は{}をしているようです。",
                msg::island_at(&island.name, &h.point()),
                wrap(tags::DISASTER, "漏電")
            ),
            Some(island.id),
            None,
        );
        island.map.get_mut(x, y).expect("in range").kind = k(L::Conden4);
        island.scratch.roudenflag += 1;
        if h.land_kind == k(L::Conden2) {
            set_value(island, x, y, 2);
        }
        if h.land_kind == k(L::Conden3) {
            set_value(island, x, y, 3);
        }
    }
}

/// 小彗星 (中型隕石)
fn meteor(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) {
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    if !((ctx.random(333_333) as f64) < 100.0 + island.scratch.co8 as f64 / 3.0
        && island.scratch.ene > 5_000_000)
    {
        return;
    }
    // この中の $point は "(x, y)" の局所変数
    let center = h.point();

    let mut count = 0;
    for i in 0..7 {
        match in_island(&island.map, around(x as i64, y as i64, i)) {
            None => {
                // Perl 版は未定義のグローバル変数 $kind と比べている
                if ctx.globals.hex.kind == L::Sea as i64 {
                    count += 1;
                }
            }
            Some((sx, sy)) => {
                let c = island.map.get(sx, sy).unwrap_or_default();
                if c.kind == k(L::Defence) && c.value == 77 {
                    ctx.log.out(
                        turn,
                        format!(
                            "{}の<B>防衛施設・改</B>は壊滅したようです。",
                            msg::island_at(&island.name, &format!("({sx}, {sy})"))
                        ),
                        Some(id),
                        None,
                    );
                    set(island, sx, sy, L::Waste, 0);
                    count += 1;
                }
            }
        }
    }

    let comet = wrap(tags::DISASTER, "小彗星");
    if count > 0 && island.eis[4] >= 1 {
        ctx.log.out(
            turn,
            format!(
                "{}地点に{comet}が落下！！しましたが、周囲の<b>防衛施設・改</b>が防衛したようです。",
                msg::island_at(&island.name, &center)
            ),
            Some(id),
            None,
        );
        island.scratch.roudenflag += 1;
        island.eis[4] -= ctx.random(50);
        if island.eis[4] < 1 {
            island.eis[4] = 0;
            ctx.log.out(
                turn,
                format!(
                    "{}の<B>防衛衛星</B>は{}したようです！！",
                    msg::island(&island.name),
                    wrap(tags::DISASTER, "崩壊")
                ),
                Some(id),
                None,
            );
        }
        return;
    }

    ctx.log.out(
        turn,
        format!(
            "{}地点に{comet}が落下！！",
            msg::island_at(&island.name, &center)
        ),
        Some(id),
        None,
    );
    island.scratch.roudenflag += 1;

    for i in 0..7 {
        let (sx, sy) = around(x as i64, y as i64, i);
        // Perl 版は範囲を確かめる前に読み、外側のループの $landKind に代入している。
        // この値がこのあとの火災の判定に使われる
        let (read_kind, read_value) = perl_get(&island.map, sx, sy);
        h.land_kind = read_kind;
        let Some((sx, sy)) = in_island(&island.map, (sx, sy)) else {
            continue;
        };
        let name = land_name(read_kind, read_value);
        let point = format!("({sx}, {sy})");
        if i < 1 {
            if read_kind == k(L::Sea) {
                set_value(island, sx, sy, 0);
                continue;
            } else if is_one_of(read_kind, &SEA_THINGS) {
                ctx.log.out(
                    turn,
                    wide_damage_sea2(&island.name, &name, &point),
                    Some(id),
                    None,
                );
                set(island, sx, sy, L::Sea, 1);
            }
            ctx.log.out(
                turn,
                format!(
                    "{}の<B>{name}</B>は<B>水没</B>しました。",
                    msg::island_at(&island.name, &point)
                ),
                Some(id),
                None,
            );
            set(island, sx, sy, L::Sea, 1);
        } else {
            let mut skip = SEA_THINGS.to_vec();
            skip.extend([L::Sea, L::Waste]);
            if is_one_of(read_kind, &skip) {
                continue;
            }
            if ctx.random(100) < 40 {
                ctx.log.out(
                    turn,
                    format!(
                        "{}の<B>{name}</B>は一瞬にして<B>荒地</B>と化しました。",
                        msg::island_at(&island.name, &point)
                    ),
                    Some(id),
                    None,
                );
                set(island, sx, sy, L::Waste, 0);
            }
        }
    }
}

/// 火災。周囲に森・防災都市・家・大使館・記念碑が無ければ燃える
fn fire(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) -> Flow {
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    let fire_rate = ctx.config.disaster.fire - island.eis[0] / 20;
    let protected = |island: &Island| {
        [L::Forest, L::Procity, L::House, L::Taishi, L::Monument]
            .iter()
            .map(|&l| count_around(&island.map, x as i64, y as i64, l, 7))
            .sum::<i64>()
            > 0
    };

    let kind = h.land_kind;
    let burnable = (kind == k(L::Town) && h.lv > 30)
        || is_one_of(
            kind,
            &[
                L::Haribote,
                L::Minato,
                L::Foodim,
                L::Foodka,
                L::Onsen,
                L::Kura,
                L::Kuraf,
                L::HTFactory,
                L::SHTF,
                L::Factory,
            ],
        );
    // 地形が当てはまるときだけ乱数を引く (Perl 版と同じ順)
    if burnable && ctx.random(1000) < fire_rate && !protected(island) {
        let c = island.map.get(x, y).unwrap_or_default();
        ctx.log.out(
            turn,
            fire_msg(&island.name, &land_name(c.kind, c.value), &h.point()),
            Some(id),
            None,
        );
        set(island, x, y, L::Waste, 0);
        // Perl 版は未定義のグローバル変数 $kind を見ている
        if ctx.globals.hex.kind == L::Onsen as i64 {
            set(island, x, y, L::Mountain, 0);
        }
    }

    if is_one_of(
        kind,
        &[
            L::Newtown,
            L::Rizort,
            L::Kajino,
            L::BigRizort,
            L::Bettown,
            L::Skycity,
            L::Umicity,
            L::Bigtown,
        ],
    ) && ctx.random(750) < fire_rate
    {
        if !protected(island) {
            let c = island.map.get(x, y).unwrap_or_default();
            ctx.log.out(
                turn,
                format!(
                    "{}の<B>{}</B>が{}により被害を受けました。",
                    msg::island_at(&island.name, &h.point()),
                    land_name(c.kind, c.value),
                    wrap(tags::DISASTER, "火災")
                ),
                Some(id),
                None,
            );
            let damage = ctx.random(100) + 50;
            island.map.get_mut(x, y).expect("in range").value -= damage;
        }
        let c = island.map.get(x, y).unwrap_or_default();
        if c.value <= 0 {
            let name = land_name(c.kind, c.value);
            set(island, x, y, L::Waste, 0);
            ctx.log.out(
                turn,
                fire_msg(&island.name, &name, &h.point()),
                Some(id),
                None,
            );
            return Flow::Next;
        }
    }
    Flow::Continue
}

/// `logFire`
fn fire_msg(name: &str, land_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{land_name}</B>が{}により壊滅しました。",
        msg::island_at(name, point),
        wrap(tags::DISASTER, "火災")
    )
}

/// `logRouden2`
fn rouden2(name: &str, land_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{land_name}</B>は{}になっているようです。",
        msg::island_at(name, point),
        wrap(tags::DISASTER, "エネルギーバランスが不均衡")
    )
}

/// `logWideDamageSea2`
pub(crate) fn wide_damage_sea2(name: &str, land_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{land_name}</B>は跡形もなくなりました。",
        msg::island_at(name, point)
    )
}

/// `logBariaAttack`
fn baria_attack(name: &str, land_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{land_name}</B>が<B>強力な力場</B>に押し潰されました。",
        msg::island_at(name, point)
    )
}
