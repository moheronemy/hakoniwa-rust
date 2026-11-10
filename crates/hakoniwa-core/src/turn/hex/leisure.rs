//! リゾート地・臨海リゾートホテル・カジノ・動物園・野球場・海あみゅ・腐海・枯死海。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - リゾート系の観光: 観光先を探すループは `last if ($employed <= 0)` で抜けるが、
//!   この `$employed` は (まだ宣言されていない) 未定義のグローバル変数なので、
//!   いつも 1 島目を調べたところで抜ける。
//! - 観光の計算で `$kyujoCount` を 2 回宣言していて、野球場の数は捨てられ、
//!   野球場改 (`Kyujokai`) の数だけが使われる。
//! - 観光者が来ると、外側の `$lv` に観光者数が足され、その値で成長する。
//! - カジノの魅力度の計算で `$kajinoCount` に数えているのはリゾート地の数。
//! - 臨海リゾートホテルには収益の計算が無い。
//! - 動物園の 2 回目の脱走判定と腐海の広がりは、隣のマスの地形を外側の `$landKind` に
//!   代入する。このあとの共通の災害判定 (火災など) はその地形で判定される。
//! - 動物園の `$taiji` (退治した怪獣の記録) はグローバル変数のハッシュで、入荷の判定の
//!   たびに `prize` の怪獣のビットの分だけ増え続ける。

use crate::land::{around, count_around, in_island, land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{self, Captures, trunc};
use crate::tables::{LandKind as L, MONSTERS};
use crate::turn::{TurnContext, monster_spec, random_array};

use super::town::{TOWN_KINDS, set, set_value};
use super::{Flow, HexRun, k, msg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$ts00`..`$ts30` (観光先の島の `etc5`)。doIslandunemployed も同じ変数に代入する
    pub ts: Captures<31>,
    /// `$z->{'0'}`..`$z->{'30'}` (動物園の動物の数のハッシュ。`$z0`..`$z30` とは別の変数)。
    /// doCommand の動物園系の計画も使う
    pub z: [i64; 31],
    /// `$taiji->{'0'}`..`$taiji->{'30'}` (退治した怪獣の記録)。ターンの間ずっと増え続ける。
    /// doCommand の怪獣派遣も使う
    pub taiji: [i64; 31],
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| kind == k(l))
}

fn count(island: &Island, x: usize, y: usize, kind: L, range: usize) -> i64 {
    count_around(&island.map, x as i64, y as i64, kind, range)
}

/// リゾート地
pub(super) fn rizort(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let s06b = ctx.globals.hex.s06b;
    if h.lv < 400 && ctx.rand_f64(500.0) < (15 + s06b * 2) as f64 {
        tourism(ctx, islands, idx, h);
    }
    let island = &mut islands[idx];
    if grow(ctx, island, h, 400) == Flow::Next {
        return Flow::Next;
    }

    let (x, y) = (h.x, h.y);
    let miryoku = miryoku(island, x, y, L::Kajino);
    let mut value = miryoku * base_value(island, h.lv, 25) as f64;
    if island.scratch.shouhi > island.scratch.ene {
        value = trunc(value / 2.0) as f64;
    }
    if value > 0.0 {
        ctx.globals.hex.rizortincome += trunc(value);
        island.money += trunc(value);
    }
    Flow::Continue
}

/// 臨海リゾートホテル (収益の計算は無い)
pub(super) fn big_rizort(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let s06b = ctx.globals.hex.s06b;
    if h.lv < 1000 && ctx.rand_f64(500.0) < (20 + s06b * 2) as f64 {
        tourism(ctx, islands, idx, h);
    }
    let island = &mut islands[idx];
    if grow(ctx, island, h, 1000) == Flow::Next {
        return Flow::Next;
    }
    monster_attack(ctx, island, h)
}

/// カジノ
pub(super) fn kajino(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let s06b = ctx.globals.hex.s06b;
    if h.lv < 2000 && ctx.rand_f64(500.0) < (15 + s06b * 2) as f64 {
        tourism(ctx, islands, idx, h);
    }
    let island = &mut islands[idx];
    if grow(ctx, island, h, 2500) == Flow::Next {
        return Flow::Next;
    }

    let (x, y) = (h.x, h.y);
    // $kajinoCount に数えているのはリゾート地 (Perl 版のまま)
    let miryoku = miryoku(island, x, y, L::Rizort);
    let mut value = trunc(base_value(island, h.lv, 10) as f64 / 5.0 * miryoku);
    if island.scratch.shouhi > island.scratch.ene {
        value = -(value * 10);
        h.lv -= ctx.random(250) + 100;
        if h.lv <= 0 {
            set(island, x, y, L::Plains, 0);
            return Flow::Next;
        }
        set_value(island, x, y, h.lv);
    }
    ctx.globals.hex.rizortincome += value;
    island.money += value;

    monster_attack(ctx, island, h)
}

/// 魅力度 (`$miryoku`)。`casino` は `$kajinoCount` に数える地形
fn miryoku(island: &Island, x: usize, y: usize, casino: L) -> f64 {
    let c = |kind| count(island, x, y, kind, 7) as f64;
    (2.0 * c(L::Sea) / 10.0)
        + (5.0 * c(L::Forest) / 10.0)
        + (5.0 * c(L::Mountain) / 10.0)
        + (20.0 * c(L::Sunahama) / 10.0)
        + (20.0 * c(L::Onsen) / 10.0)
        + (10.0 * c(L::Park) / 10.0)
        + (2.0 * c(casino) / 10.0)
        + 1.0
}

/// 収益の元になる値 (地形の値 + 衛星 + 森 + レナ - 怪獣)。`rena_div` はレナを割る数
fn base_value(island: &Island, lv: i64, rena_div: i64) -> i64 {
    lv + island.eis[0]
        + island.eis[1]
        + island.eis[2]
        + island.eis[4]
        + trunc(island.owner_stats.fore as f64 / 10.0)
        + trunc(island.owner_stats.rena as f64 / rena_div as f64)
        - island.monster_live * 100
}

/// リゾート系の成長。平地に戻ったら `Flow::Next`
fn grow(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun, cap: i64) -> Flow {
    let (x, y) = (h.x, h.y);
    if h.addpop < 0 {
        // 不足
        h.lv -= ctx.random(-h.addpop) + 1;
        if h.lv <= 0 {
            set(island, x, y, L::Plains, 0);
            return Flow::Next;
        }
    } else if h.lv < 10 {
        // 成長
        h.lv += ctx.random(h.addpop) + 1;
        if h.lv > 10 {
            h.lv = 10;
        }
    } else if h.addpop2 > 0 {
        h.lv += ctx.random(h.addpop2) + 1;
    }
    if h.lv > cap {
        h.lv = cap;
    }
    set_value(island, x, y, h.lv);
    Flow::Continue
}

/// 隣に怪獣がいれば被害を受ける (臨海リゾートホテル、カジノ)
fn monster_attack(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) -> Flow {
    let (x, y) = (h.x, h.y);
    if count(island, x, y, L::Monster, 7) > 0 {
        h.lv -= ctx.random(20) + 10;
        set_value(island, x, y, h.lv);
        ctx.log.out(
            ctx.turn,
            msg::mons_attacks(&island.name, &land_name(h.land_kind, h.lv), &h.point()),
            Some(island.id),
            None,
        );
        if h.lv <= 0 {
            set(island, x, y, L::Waste, 0);
            return Flow::Next;
        }
    }
    Flow::Continue
}

/// 観光: 人口の多い島から観光者が来る (リゾート地・臨海リゾートホテル・カジノ共通)
fn tourism(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, h: &mut HexRun) {
    let order = random_array(&mut *ctx.rng, ctx.island_number);
    let n = ctx.island_number.min(5);
    if n == 0 {
        return;
    }
    // 観光先を探すループは未定義の $employed を見て、いつも 1 島目で抜ける (Perl 版のまま)
    let t = order[0];
    let Some(t_island) = islands.get(t) else {
        return;
    };
    let t_pop = t_island.pop;
    let ts = ctx.globals.hex.leisure.ts.update(&t_island.etc_raw[0]);
    let ts06b = trunc(ts[6] as f64 / 5.0);

    let (x, y) = (h.x, h.y);
    // $migrate は未定義 (0) のまま進むことがある
    let mut migrate = 0;
    let island = &islands[idx];
    if island.pop < t_pop {
        let c = |kind| count(island, x, y, kind, 19);
        let sea = c(L::Sea);
        let forest = c(L::Forest);
        let mountain = c(L::Mountain);
        let park = c(L::Park);
        // $kyujoCount を 2 回宣言していて、野球場改の数で上書きされる (Perl 版のまま)
        let kyujo = c(L::Kyujokai);
        let umiamu = c(L::Umiamu);
        let sunahama = c(L::Sunahama);
        let rizort = c(L::Rizort) + c(L::Kajino) + c(L::BigRizort);
        let cell = island.map.get(x, y).unwrap_or_default();
        h.land_kind = cell.kind;
        h.lv = cell.value;
        let s06b = ctx.globals.hex.s06b;
        migrate = sea * 3
            + forest * 3
            + mountain * 3
            + park * 4
            + kyujo * 4
            + umiamu * 7
            + sunahama * 10
            + rizort * 5
            + s06b * 10
            - ts06b * 10;
        if migrate < 0 {
            migrate = 1;
        }
        // 外側の $lv に観光者数が足される
        h.lv += migrate;
        let t_island = &islands[t];
        ctx.log.out(
            ctx.turn,
            kankou_migrate(
                &island.name,
                &land_name(h.land_kind, h.lv),
                &t_island.name,
                &h.point(),
                &format!("{migrate}{}", ctx.config.units.pop),
            ),
            Some(island.id),
            Some(t_island.id),
        );
    }

    if migrate == 0 {
        // 足し引きする値が 0 なので何も変わらない (観光先が自分の島のときもここに来る)
        return;
    }
    let island = &mut islands[idx];
    island.eisei[1] += migrate;
    island.pop += migrate;
    let t_island = &mut islands[t];
    t_island.pop -= migrate;

    // 観光にきてくれた分人口減少
    let mut employed = migrate;
    for &(px, py) in &ctx.points {
        let Some(cell) = t_island.map.get(px, py) else {
            continue;
        };
        if is_one_of(cell.kind, &TOWN_KINDS) && cell.value > 1 {
            // min($lv - 1, $employed)
            let n = if cell.value - 1 < employed {
                cell.value - 1
            } else {
                employed
            };
            let c = t_island.map.get_mut(px, py).expect("in range");
            c.value -= n;
            employed -= n;
            if c.value <= 0 {
                set(t_island, px, py, L::Plains, 0);
            }
        }
    }
}

/// 動物園
pub(super) fn zoo(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    /// `$zookazus` の重み
    const WEIGHT: [i64; 31] = [
        2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 3, 3, 3, 3, 4, 4, 5, 4, 5, 3, 3, 3, 3, 3, 3, 4, 1, 4,
    ];
    let (x, y) = (h.x, h.y);
    let (id, turn) = (islands[idx].id, ctx.turn);

    // $z0..$z30 と $z->{...} の両方に代入する (マッチしなければ前の値のまま)
    if let Some(z) = perl::fields::<31>(&islands[idx].etc_raw[1]) {
        ctx.globals.zoo = z;
        ctx.globals.hex.leisure.z = z;
    }
    let zv = ctx.globals.zoo;
    let zookazu: i64 = zv.iter().sum();
    let zookazus: i64 = zv.iter().zip(WEIGHT).map(|(z, w)| z * w).sum();

    if ctx.globals.hex.zooflag <= 0 {
        ctx.globals.hex.zooflag = 1;
        let mshurui = ctx.globals.hex.leisure.z.iter().filter(|&&v| v > 0).count() as i64;
        let island = &mut islands[idx];
        let mut value = zookazus * 15 + mshurui * 150;
        let valuef = zookazu * 250;
        if island.scratch.shouhi > island.scratch.ene {
            value = trunc(value as f64 / 10.0);
        }

        let s08 = ctx.globals.etc5.0[8];
        if ctx.random(1000) < 25 + s08 {
            let zlv: i64 = ctx
                .points
                .iter()
                .filter_map(|&(sx, sy)| island.map.get(sx, sy))
                .filter(|c| c.kind == k(L::Zoo))
                .map(|c| c.value)
                .sum();
            let mut siire = ctx.random(12);
            if ctx.random(100) < 20 {
                siire = ctx.random(10) + 13;
            }

            let monsters = prize_monsters(&island.prize, &zv);
            let g = &mut ctx.globals.hex.leisure;
            for (i, taiji) in g.taiji.iter_mut().enumerate() {
                if monsters & (1 << i) != 0 {
                    *taiji += 1;
                }
            }

            let s = siire as usize;
            if g.taiji[s] > 0 && zlv > zookazu {
                g.z[s] += 1;
                value *= siire;
                ctx.log.out(
                    turn,
                    siire_msg(
                        &island.name,
                        &land_name(h.land_kind, h.lv),
                        MONSTERS[s].name,
                        &h.point(),
                    ),
                    Some(id),
                    None,
                );
                island.etc_raw[1] = perl::join(&g.z);
            }
        }

        if value > 0 {
            island.money += value;
            let units = &ctx.config.units;
            ctx.log.out(
                turn,
                oil_money2(
                    &island.name,
                    &land_name(h.land_kind, h.lv),
                    &h.point(),
                    &format!("{value}{}", units.money),
                    &format!("{valuef}{}", units.food),
                ),
                Some(id),
                None,
            );
        }
    }

    // 脱走 (動物園のマスが怪獣になる)
    let island = &mut islands[idx];
    if island.owner_stats.rena < zookazus * 25 && ctx.random(100) < 15 {
        let nk = ctx.random(30) as usize;
        if ctx.globals.hex.leisure.z[nk] > 0 {
            ctx.globals.hex.leisure.z[nk] -= 1;
            ctx.globals.hex.kind = nk as i64;
            // 外側の $lv を書き換える
            h.lv = ((nk as i64) << 4) + MONSTERS[nk].base_hp + ctx.random(MONSTERS[nk].hp_range);
            set(island, x, y, L::Monster, h.lv);
            let (_, m_name, _) = monster_spec(h.lv);
            ctx.log
                .out(turn, nige(&island.name, m_name, &h.point()), Some(id), None);
            ctx.log.out(
                turn,
                mons_move(
                    &island.name,
                    &land_name(h.land_kind, h.lv),
                    &h.point(),
                    m_name,
                ),
                Some(id),
                None,
            );
            island.etc_raw[1] = perl::join(&ctx.globals.hex.leisure.z);
        }
    }

    // 脱走 (隣の陸地に怪獣が出る)
    if island.owner_stats.rena < zookazus * 50 || island.scratch.shouhi > island.scratch.ene {
        let nk = ctx.random(30) as usize;
        if ctx.globals.hex.leisure.z[nk] > 0 {
            let mut nigeflag = 0;
            for i in 1..7 {
                let (sx, sy) = around(x as i64, y as i64, i);
                // 範囲を確かめる前に外側の $landKind とグローバル変数の $point に代入している
                // (Perl 版のまま)。$landKind はこのあとの共通の災害判定に使われる
                h.land_kind = perl_get(&island.map, sx, sy).0;
                ctx.globals.hex.point = format!("({sx}, {sy})");
                let Some((sx, sy)) = in_island(&island.map, (sx, sy)) else {
                    continue;
                };
                let c = island.map.get(sx, sy).unwrap_or_default();
                h.land_kind = c.kind;
                if is_one_of(
                    c.kind,
                    &[
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
                    ],
                ) || nigeflag != 0
                {
                    continue;
                }
                nigeflag += 1;
                ctx.globals.hex.leisure.z[nk] -= 1;
                // この $kind と $lv は局所変数
                let lv =
                    ((nk as i64) << 4) + MONSTERS[nk].base_hp + ctx.random(MONSTERS[nk].hp_range);
                set(island, sx, sy, L::Monster, lv);
                let (_, m_name, _) = monster_spec(lv);
                ctx.log
                    .out(turn, nige(&island.name, m_name, &h.point()), Some(id), None);
                island.etc_raw[1] = perl::join(&ctx.globals.hex.leisure.z);
            }
        }
    }
    Flow::Continue
}

/// `$prize =~ /([0-9]*),([0-9]*),(.*)/` の 2 番目 (退治した怪獣のビット)。
///
/// マッチしなければ Perl 版は直前に成功したマッチの `$2` を使う。この時点では
/// 直前の `etc6` のマッチ (`$z1`) になる
fn prize_monsters(prize: &str, z: &[i64; 31]) -> i64 {
    let b = prize.as_bytes();
    let digits = |from: usize| from + b[from..].iter().take_while(|c| c.is_ascii_digit()).count();
    for start in 0..b.len() {
        let e1 = digits(start);
        if b.get(e1) != Some(&b',') {
            continue;
        }
        let e2 = digits(e1 + 1);
        if b.get(e2) != Some(&b',') {
            continue;
        }
        return perl::int(&prize[e1 + 1..e2]);
    }
    z[1]
}

/// 野球場
pub(super) fn kyujo(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    if !(island.scratch.kyu > 1 || island.scratch.amu > 1) {
        let nt = super::town::town_count(island, x, y) - 6;
        let ns = 1 + 2 * count(island, x, y, L::Park, 19);
        let nr = 1 + 3 * count(island, x, y, L::Umiamu, 19);
        let nu = 10 + ctx.random(10);
        let mut value = nt * nu * ns * nr + trunc(island.pop as f64 / 25.0);
        if island.scratch.shouhi > island.scratch.ene {
            value = trunc(value as f64 / 5.0);
        }
        if value > 0 {
            island.money += value;
            ctx.log.out(
                turn,
                oil_money(
                    &island.name,
                    &land_name(h.land_kind, h.lv),
                    &h.point(),
                    &format!("{value}{}", ctx.config.units.money),
                ),
                Some(id),
                None,
            );
        }
    }

    park_event(ctx, island, h);

    // 老朽化判定
    if ctx.random(100) < 1 {
        ctx.log.out(
            turn,
            park_end(&island.name, &land_name(h.land_kind, h.lv), &h.point()),
            Some(id),
            None,
        );
        set(island, x, y, L::Plains, 0);
    }
    if ctx.random(100) < 3 {
        let l_name = land_name(h.land_kind, h.lv);
        let value = 500 + ctx.random(500);
        island.money += value;
        if value > 0 {
            ctx.log.out(
                turn,
                yusho(
                    &island.name,
                    &l_name,
                    &h.point(),
                    &format!("{value}{}", ctx.config.units.money),
                ),
                Some(id),
                None,
            );
        }
    }
    Flow::Continue
}

/// 野球場・海あみゅのイベント (食料を消費する)
fn park_event(ctx: &mut TurnContext, island: &mut Island, h: &HexRun) {
    if ctx.random(100) < 10 {
        let value = trunc(island.pop as f64 / 50.0) * 10;
        island.food -= value;
        if value > 0 {
            ctx.log.out(
                ctx.turn,
                park_event_msg(
                    &island.name,
                    &land_name(h.land_kind, h.lv),
                    &h.point(),
                    &format!("{value}{}", ctx.config.units.food),
                ),
                Some(island.id),
                None,
            );
        }
    }
}

/// 海あみゅ
pub(super) fn umiamu(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    if !(island.scratch.kyu > 1 || island.scratch.amu > 1) {
        let no = super::town::town_count(island, x, y) - 3;
        let np = 1 + 3 * count(island, x, y, L::Park, 19);
        let nq = 1 + 4 * count(island, x, y, L::Kyujo, 19);
        let nqk = 1 + 4 * count(island, x, y, L::Kyujokai, 19);
        let nu = 5 + ctx.random(5);
        let mut value = no * np * nq * nqk * nu + trunc(island.pop as f64 / 25.0) + ctx.random(200);
        if island.scratch.shouhi > island.scratch.ene {
            value = trunc(value as f64 / 7.0);
        }
        if value > 0 {
            island.money += value;
            ctx.log.out(
                ctx.turn,
                oil_money(
                    &island.name,
                    &land_name(h.land_kind, h.lv),
                    &h.point(),
                    &format!("{value}{}", ctx.config.units.money),
                ),
                Some(island.id),
                None,
            );
        }
    }
    park_event(ctx, island, h);
    Flow::Continue
}

/// 腐海 (値が 20 未満): 育ちながら周りの陸地を飲み込む
pub(super) fn rotten_sea(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    let v = island.map.get(x, y).unwrap_or_default().value + 1;
    set_value(island, x, y, v);
    let m73 = island.scratch.m73;
    for i in 1..7 {
        let Some((sx, sy)) = in_island(&island.map, around(x as i64, y as i64, i)) else {
            continue;
        };
        let c = island.map.get(sx, sy).unwrap_or_default();
        // 外側の $landKind に代入している (Perl 版のまま)。共通の災害判定に使われる
        h.land_kind = c.kind;
        let l_name = land_name(c.kind, c.value);
        if is_one_of(
            c.kind,
            &[
                L::Sea,
                L::Sbase,
                L::Ice,
                L::Seacity,
                L::Seatown,
                L::Umishuto,
                L::Fune,
                L::Frocity,
                L::Umiamu,
                L::Oil,
                L::Nursery,
                L::RottenSea,
            ],
        ) {
            continue;
        }
        let n = count(island, sx, sy, L::RottenSea, 7);
        let point = format!("({sx}, {sy})");
        let swallow = (n >= 4 && ctx.rand_f64(1000.0) + ((m73 * 100) as f64) < 300.0)
            || (n != 0 && ctx.rand_f64(1000.0) + ((m73 * 100) as f64) < 200.0);
        if swallow {
            ctx.log.out(
                turn,
                format!(
                    "{}の<B>{l_name}</B>は<B>腐海</B>に飲み込まれました。",
                    msg::island_at(&island.name, &point)
                ),
                Some(id),
                None,
            );
            set(island, sx, sy, L::RottenSea, 1);
        }
    }
    Flow::Continue
}

/// 枯死海 (腐海の値が 20 以上): 古くなると記念碑 (遺跡) や荒地になる
pub(super) fn dead_sea(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    let v = island.map.get(x, y).unwrap_or_default().value + 1;
    set_value(island, x, y, v);
    if v > 4000 {
        set(island, x, y, L::Waste, 0);
    } else if v > 1000 && ctx.random(250) == 0 {
        let m = 80 + ctx.random(3);
        set(island, x, y, L::Monument, m);
    } else if v > 750 && ctx.random(250) == 0 {
        set(island, x, y, L::Monument, 73);
    } else if v > 500 && ctx.random(250) == 0 {
        let m = 74 + ctx.random(5);
        set(island, x, y, L::Monument, m);
    } else if v > 250 && ctx.random(250) == 0 {
        set(island, x, y, L::Monument, 87);
    } else if v > 125 && ctx.random(250) == 0 && island.scratch.m84 < 4 {
        set(island, x, y, L::Monument, 84);
    }
    Flow::Continue
}

/// `logKankouMigrate` (`pop` は単位付き)
fn kankou_migrate(name: &str, l_name: &str, t_name: &str, point: &str, pop: &str) -> String {
    format!(
        "{}から{}の<B>{l_name}</B>へ<B>{pop}</B>の観光者が来てくれました。ありがとうございます。",
        msg::island(t_name),
        msg::island_at(name, point)
    )
}

/// `logOilMoney`
fn oil_money(name: &str, l_name: &str, point: &str, amount: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>から、<B>{amount}</B>の収益が上がりました。",
        msg::island_at(name, point)
    )
}

/// `logOilMoney2`
fn oil_money2(name: &str, l_name: &str, point: &str, amount: &str, food: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>から、<B>{amount}</B>の収益が上がりました。(食料<B>{food}</B>消費)",
        msg::island_at(name, point)
    )
}

/// `logSiire`
fn siire_msg(name: &str, l_name: &str, m_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>は<B>{m_name}</B>を入荷し話題をよんでいます。",
        msg::island_at(name, point)
    )
}

/// `logNige`
fn nige(name: &str, m_name: &str, point: &str) -> String {
    format!(
        "{}の<B>動物園</B>から<B>{m_name}</B>が{}しました。",
        msg::island_at(name, point),
        wrap(tags::DISASTER, "脱走")
    )
}

/// `logMonsMove`
fn mons_move(name: &str, l_name: &str, point: &str, m_name: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>が<B>{m_name}</B>に踏み荒らされました。",
        msg::island_at(name, point)
    )
}

/// `logParkEvent`
fn park_event_msg(name: &str, l_name: &str, point: &str, amount: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>でイベントが開催され、<B>{amount}</B>の食料が消費されました。",
        msg::island_at(name, point)
    )
}

/// `logParkEnd`
fn park_end(name: &str, l_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{l_name}</B>は施設が老朽化したため取り壊されました。",
        msg::island_at(name, point)
    )
}

/// `logYusho`
fn yusho(name: &str, l_name: &str, point: &str, amount: &str) -> String {
    format!(
        "{}の野球チームは{}の<B>{l_name}</B>で行われた箱庭リーグ決勝戦でみごと優勝し、<B>{amount}</B>の経済効果があがりました。",
        msg::island(name),
        wrap(tags::NAME, point)
    )
}
