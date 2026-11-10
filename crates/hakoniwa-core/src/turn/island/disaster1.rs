//! 地震・重税への反発・食料不足 (宇宙ステーション)・津波・怪獣の出現 (Perl 版 14850〜15247 行)。

use crate::land::{count_around, land_name};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{self, trunc};
use crate::tables::{LandKind as L, MONSTERS};
use crate::turn::hex::town::{set, set_value};
use crate::turn::{TurnContext, monster_spec};

use super::ProcRun;

/// この段階で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {}

/// この段階で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

const fn k(l: L) -> u8 {
    l as u8
}

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| kind == k(l))
}

/// 島の中のマスの (種類, 値)
fn get(island: &Island, x: usize, y: usize) -> (u8, i64) {
    island.map.get(x, y).map_or((0, 0), |c| (c.kind, c.value))
}

fn island_name(name: &str) -> String {
    wrap(tags::NAME, &format!("{name}島"))
}

fn island_at(name: &str, point: &str) -> String {
    wrap(tags::NAME, &format!("{name}島{point}"))
}

fn d(s: &str) -> String {
    wrap(tags::DISASTER, s)
}

/// `logEarthquake`
fn earthquake(name: &str) -> String {
    format!("{}で大規模な{}が発生！！", island_name(name), d("地震"))
}

/// `logOmamori`
fn omamori(name: &str) -> String {
    format!(
        "{}所有の<B>お守り</B>のお陰でしょうか、{}が少なかったようです！！",
        island_name(name),
        d("被害")
    )
}

/// `logEQDamage`
fn eq_damage(name: &str, l: &str, point: &str) -> String {
    format!(
        "{}の<B>{l}</B>は{}により壊滅しました。",
        island_at(name, point),
        d("地震")
    )
}

/// `logEQDamagenot`
fn eq_damage_not(name: &str, l: &str, point: &str) -> String {
    format!(
        "{}の<B>{l}</B>は{}により被害を受けました。",
        island_at(name, point),
        d("地震")
    )
}

/// `logKire`
fn kire(name: &str) -> String {
    format!(
        "{}の<B>重税</B>に島民は{}ました！！",
        island_name(name),
        d("キレ")
    )
}

/// `logKireDamage`
fn kire_damage(name: &str, l: &str, point: &str) -> String {
    format!(
        "{}の<B>{l}</B>は{}によって{}されました。",
        island_at(name, point),
        d("暴れる島民"),
        d("破壊")
    )
}

/// `logStarve`
fn starve(name: &str) -> String {
    format!("{}の{}しています！！", island_name(name), d("食料が不足"))
}

/// `logEiseiEndNopop`
fn eisei_end_nopop(name: &str, eisei: &str) -> String {
    format!(
        "{}の<B>{eisei}</B>は{}ようです！！",
        island_name(name),
        d("人がいなくなった")
    )
}

/// `logSvDamage`
fn sv_damage(name: &str, l: &str, point: &str) -> String {
    format!(
        "{}の<B>{l}</B>に<B>食料を求めて住民が殺到</B>。<B>{l}</B>は壊滅しました。",
        island_at(name, point)
    )
}

/// `logTsunami`
fn tsunami(name: &str) -> String {
    format!("{}付近で{}発生！！", island_name(name), d("津波"))
}

/// `logTsunamiDamage`
fn tsunami_damage(name: &str, l: &str, point: &str) -> String {
    format!(
        "{}の<B>{l}</B>は{}により崩壊しました。",
        island_at(name, point),
        d("津波")
    )
}

/// `logMonsCome`
fn mons_come(name: &str, m_name: &str, point: &str, l_name: &str) -> String {
    format!(
        "{}に<B>{m_name}</B>出現！！{}の<B>{l_name}</B>が踏み荒らされました。",
        island_name(name),
        wrap(tags::NAME, point)
    )
}

fn out(ctx: &mut TurnContext, id: i64, message: String) {
    ctx.log.out(ctx.turn, message, Some(id), None);
}

/// 地震・津波でお守り (`$toto2`) があれば 1 つ使って被害を防ぐ。使ったら `true`
fn use_omamori(ctx: &mut TurnContext, island: &mut Island) -> bool {
    if ctx.globals.etc8.0[1] > 0 {
        ctx.globals.etc8.0[1] -= 1;
        island.etc_raw[3] = perl::join(&ctx.globals.etc8.0);
        out(ctx, island.id, omamori(&island.name));
        true
    } else {
        false
    }
}

pub(super) fn run(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, p: &mut ProcRun) {
    let island = &mut islands[idx];
    earthquake_check(ctx, island);
    riot(ctx, island);
    food_shortage(ctx, island);
    tsunami_check(ctx, island);
    monster_appear(ctx, island, p);
}

/// 地震判定 (14850〜14937 行)
fn earthquake_check(ctx: &mut TurnContext, island: &mut Island) {
    let s04 = ctx.globals.etc5.0[4];
    let threshold = (island.scratch.command.land.prepare2 + 1) * ctx.config.disaster.earthquake
        - trunc(island.eis[1] as f64 / 15.0)
        - trunc(s04 as f64 / 10.0);
    if ctx.random(1000) >= threshold {
        return;
    }
    let (id, name) = (island.id, island.name.clone());
    out(ctx, id, earthquake(&name));
    if use_omamori(ctx, island) {
        return;
    }

    let co5 = island.scratch.co5;
    for &(x, y) in &ctx.points.clone() {
        let (land_kind, lv) = get(island, x, y);
        let point = format!("({x}, {y})");

        if (land_kind == k(L::Town) && lv >= 100)
            || (land_kind == k(L::Foodim) && lv < 480)
            || (land_kind == k(L::Procity) && lv < 130)
            || is_one_of(
                land_kind,
                &[
                    L::Haribote,
                    L::Park,
                    L::Minato,
                    L::Onsen,
                    L::Kyujo,
                    L::Kyujokai,
                    L::Factory,
                ],
            )
        {
            // 1/4で壊滅
            if ctx.random(4 + co5 * 5) == 0 {
                out(ctx, id, eq_damage(&name, &land_name(land_kind, lv), &point));
                set(island, x, y, L::Waste, 0);
                // 金山は山に戻るはずが、地形ではなくグローバル変数 $kind を見ている (Perl 版のまま)
                if ctx.globals.hex.kind == L::Onsen as i64 {
                    set(island, x, y, L::Mountain, 0);
                }
            }
        }
        if ((land_kind == k(L::Bigtown)
            || land_kind == k(L::Bettown)
            || land_kind == k(L::Skycity)
            || land_kind == k(L::Shuto)
            || land_kind == k(L::Umishuto)
            || land_kind == k(L::Newtown))
            && lv >= 100)
            || (is_one_of(
                land_kind,
                &[L::Rizort, L::Kajino, L::BigRizort, L::HTFactory, L::SHTF],
            ) && lv >= 10)
        {
            if ctx.random(3 + co5 * 5) == 0 {
                out(
                    ctx,
                    id,
                    eq_damage_not(&name, &land_name(land_kind, lv), &point),
                );
                let v = get(island, x, y).1 - (ctx.random(100) + 50);
                set_value(island, x, y, v);
            }
            if get(island, x, y).1 <= 0 {
                // 平地に戻す
                set(island, x, y, L::Waste, 0);
                out(ctx, id, eq_damage(&name, &land_name(land_kind, lv), &point));
                continue;
            }
        }
        if is_one_of(land_kind, &[L::Farmchi, L::Farmpic, L::Farmcow]) {
            if ctx.random(6) == 0 {
                out(
                    ctx,
                    id,
                    eq_damage_not(&name, &land_name(land_kind, lv), &point),
                );
                let v = get(island, x, y).1 - (ctx.random(400) + 50);
                set_value(island, x, y, v);
            }
            if get(island, x, y).1 <= 0 {
                // 平地に戻す
                set(island, x, y, L::Waste, 0);
                out(ctx, id, eq_damage(&name, &land_name(land_kind, lv), &point));
                continue;
            }
        }
    }
}

/// 重税にきれる住民 (14940〜15021 行)
fn riot(ctx: &mut TurnContext, island: &mut Island) {
    let eisei1 = island.eisei[0];
    let r = ctx.random(100);
    if r >= eisei1 - 10 - ctx.random(5) {
        return;
    }
    let (id, name) = (island.id, island.name.clone());
    out(ctx, id, kire(&name));

    for &(x, y) in &ctx.points.clone() {
        let (land_kind, lv) = get(island, x, y);
        let point = format!("({x}, {y})");

        if is_one_of(
            land_kind,
            &[
                L::Farm,
                L::College,
                L::Yakusho,
                L::Factory,
                L::SHTF,
                L::OWNF,
                L::HTFactory,
                L::Nursery,
                L::EneAt,
                L::EneFw,
                L::EneWt,
                L::EneWd,
                L::EneBo,
                L::EneSo,
                L::EneCs,
                L::Base,
                L::Park,
                L::Kyujo,
                L::Kyujokai,
                L::Zoo,
                L::House,
                L::Taishi,
                L::Train,
                L::Kura,
                L::Kuraf,
                L::Defence,
            ],
        ) && ctx.random(100) < eisei1
        {
            out(
                ctx,
                id,
                kire_damage(&name, &land_name(land_kind, lv), &point),
            );
            set(island, x, y, L::Waste, 0);
            // でも養殖場なら浅瀬
            if land_kind == k(L::Nursery) {
                set(island, x, y, L::Sea, 1);
            }
        }
        if is_one_of(
            land_kind,
            &[
                L::Town,
                L::Minato,
                L::Foodim,
                L::Procity,
                L::Farmchi,
                L::Farmpic,
                L::Farmcow,
            ],
        ) && ctx.random(100) < eisei1 - 30
        {
            out(
                ctx,
                id,
                kire_damage(&name, &land_name(land_kind, lv), &point),
            );
            set(island, x, y, L::Waste, 0);
        }
        if is_one_of(land_kind, &[L::Sbase, L::Seacity, L::Umiamu, L::Frocity])
            && ctx.random(100) < eisei1 - 60
        {
            out(
                ctx,
                id,
                kire_damage(&name, &land_name(land_kind, lv), &point),
            );
            set(island, x, y, L::Sea, 0);
        }
    }
}

/// 食料不足 (15024〜15085 行)。宇宙ステーションの住民も減る
fn food_shortage(ctx: &mut TurnContext, island: &mut Island) {
    if island.food > 0 {
        return;
    }
    let (id, name) = (island.id, island.name.clone());
    out(ctx, id, starve(&name));
    island.food = 0;

    if island.eis[6] >= 1 {
        let eis7 = island.eis[6];
        ctx.globals.process.eis7 = eis7;
        let cstpop = trunc(eis7 as f64 / 100.0);
        let csten = eis7.rem_euclid(100);
        let tdmg = ctx.random(1000);
        ctx.globals.command.ops.tcst.2 = tdmg;
        let cstpop = trunc((cstpop * tdmg) as f64 / 1000.0);
        ctx.globals.command.ops.cst = (cstpop, csten);
        island.eis[6] = cstpop * 100 + csten;
        if cstpop < tdmg {
            island.eis[6] = 0;
            out(ctx, id, eisei_end_nopop(&name, "宇宙ステーション"));
        }
    }

    for &(x, y) in &ctx.points.clone() {
        let (land_kind, lv) = get(island, x, y);
        if is_one_of(
            land_kind,
            &[
                L::Farm,
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
                L::Nursery,
                L::Base,
                L::Mine,
                L::Kura,
                L::Kuraf,
                L::Defence,
            ],
        ) && ctx.random(4) == 0
        {
            // 1/4で壊滅
            let point = format!("({x}, {y})");
            out(ctx, id, sv_damage(&name, &land_name(land_kind, lv), &point));
            set(island, x, y, L::Waste, 0);
            // でも養殖場なら浅瀬
            if land_kind == k(L::Nursery) {
                set(island, x, y, L::Sea, 1);
            }
        }
    }
}

/// 津波判定 (15087〜15180 行)
fn tsunami_check(ctx: &mut TurnContext, island: &mut Island) {
    let s04 = ctx.globals.etc5.0[4];
    let threshold =
        ctx.config.disaster.tsunami - trunc(island.eis[1] as f64 / 15.0) - trunc(s04 as f64 / 10.0);
    if ctx.random(1000) >= threshold {
        return;
    }
    let (id, name) = (island.id, island.name.clone());
    out(ctx, id, tsunami(&name));
    if use_omamori(ctx, island) {
        return;
    }

    let co5 = island.scratch.co5;
    for &(x, y) in &ctx.points.clone() {
        let (land_kind, lv) = get(island, x, y);
        if !((land_kind == k(L::Procity) && lv < 110)
            || is_one_of(
                land_kind,
                &[
                    L::Town,
                    L::Farm,
                    L::Farmchi,
                    L::Farmpic,
                    L::Farmcow,
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
                    L::Train,
                    L::College,
                    L::Yakusho,
                    L::Foodim,
                    L::Foodka,
                    L::Factory,
                    L::HTFactory,
                    L::SHTF,
                    L::OWNF,
                    L::Base,
                    L::Defence,
                    L::Park,
                    L::Minato,
                    L::Fune,
                    L::Seki,
                    L::Mine,
                    L::Nursery,
                    L::Kyujo,
                    L::Kyujokai,
                    L::Zoo,
                    L::Newtown,
                    L::Bigtown,
                    L::Bettown,
                    L::Rizort,
                    L::Kajino,
                    L::Umicity,
                    L::BigRizort,
                    L::Shuto,
                    L::Kura,
                    L::Kuraf,
                    L::Haribote,
                ],
            ))
        {
            continue;
        }
        // 1d12 <= (周囲の海 - 1) で崩壊
        let r = ctx.random(12 + co5 * 5);
        let (sx, sy) = (x as i64, y as i64);
        let seas: i64 = [
            L::Oil,
            L::Sbase,
            L::Seacity,
            L::Seatown,
            L::Umishuto,
            L::Fune,
            L::Frocity,
            L::Umiamu,
            L::Sea,
        ]
        .iter()
        .map(|&l| count_around(&island.map, sx, sy, l, 7))
        .sum();
        if r < seas - 1 {
            let point = format!("({x}, {y})");
            out(
                ctx,
                id,
                tsunami_damage(&name, &land_name(land_kind, lv), &point),
            );
            if land_kind == k(L::Fune) {
                set(island, x, y, L::Sea, 0);
            } else if land_kind == k(L::Nursery) {
                // でも養殖場なら浅瀬
                set(island, x, y, L::Sea, 1);
            } else {
                set(island, x, y, L::Waste, 0);
            }
        }
    }
}

/// 怪獣判定 (15182〜15247 行)。`$r` と `$pop` は doIslandProcess の `my` 変数
fn monster_appear(ctx: &mut TurnContext, island: &mut Island, p: &mut ProcRun) {
    p.r = ctx.random(10000);
    p.pop = island.pop;
    let (id, name) = (island.id, island.name.clone());
    let mc = ctx.config.monster.clone();
    loop {
        let send = island.scratch.command.attack.monstersend;
        if (p.r < mc.appearance_rate * island.area && p.pop >= mc.borders[0]) || send > 0 {
            // 怪獣出現。種類を決める
            let kind = if send > 0 {
                // 人造
                island.scratch.command.attack.monstersend -= 1;
                island.scratch.command.attack.monstersendkind
            } else if p.pop >= mc.borders[3] {
                ctx.random(mc.levels[3]) + 1
            } else if p.pop >= mc.borders[2] {
                ctx.random(mc.levels[2]) + 1
            } else if p.pop >= mc.borders[1] {
                ctx.random(mc.levels[1]) + 1
            } else {
                ctx.random(mc.levels[0]) + 1
            };

            // lvの値を決める (表の外の種類は 0 として扱う)
            let spec = usize::try_from(kind).ok().and_then(|i| MONSTERS.get(i));
            let lv = (kind << 4)
                + spec.map_or(0, |m| m.base_hp)
                + ctx.random(spec.map_or(0, |m| m.hp_range));

            // どこに現れるか決める
            for &(bx, by) in &ctx.points.clone() {
                let (kind_here, value_here) = get(island, bx, by);
                if is_one_of(
                    kind_here,
                    &[
                        L::Town,
                        L::Bigtown,
                        L::Bettown,
                        L::Skycity,
                        L::Umicity,
                        L::Rizort,
                        L::Kajino,
                        L::BigRizort,
                        L::Newtown,
                    ],
                ) {
                    // 地形名 (町として名前を付ける)
                    let l_name = land_name(k(L::Town), value_here);
                    set(island, bx, by, L::Monster, lv);
                    let (_, m_name, _) = monster_spec(lv);
                    out(
                        ctx,
                        id,
                        mons_come(&name, m_name, &format!("({bx}, {by})"), &l_name),
                    );
                    break;
                }
            }
        }
        if island.scratch.command.attack.monstersend <= 0 {
            break;
        }
    }
}
