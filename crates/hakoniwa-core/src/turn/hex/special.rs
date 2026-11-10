//! 大学 (生物大学のマスコット、文部科学省)・島営企業・記念碑。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 卵 (記念碑 80〜83) の分岐は `my` 無しの `for($i = 0; $i < 7; $i++)` で外側のループの
//!   添字を使い回す。孵化すると外側のループは 8 番目のマスから続く ([`HexRun::i`])。
//!   同じく `$landKind`/`$lv` は最後に見た隣のマス (島の外なら範囲外の読み出し) の値になり、
//!   そのまま共通の災害判定に使われる。
//! - 文部科学省 (大学 80) と島営企業の周囲の数え上げも `$landKind` を書き換える
//!   (`$lv` は `my` なので変わらない)。
//! - 生物大学の出動 (`$take`) はグローバル変数で、一度も初期化しない。ターン中に
//!   どこかの島で一度出動すると、以後どの島の生物大学も出動しない。
//! - 記念碑 94 は「行による位置調整」をせずに隣を見る。島の外の負の添字は反対側の端になり、
//!   そこにいる怪獣を倒す (書き込みも反対側の端に行く)。

use crate::land::{AX, AY, around, in_island, land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::trunc;
use crate::tables::{LandKind as L, MONSTERS};
use crate::turn::{TurnContext, monster_spec};

use super::town::{set, set_value, town_count};
use super::{Flow, HexRun, k, msg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$take` (生物大学が出動した数)。どこでも 0 に戻さない
    pub take: i64,
    /// `$costseisaku` (政策の合計)。doCommand も同じ変数に代入して使う
    pub costseisaku: i64,
    /// `$ownfe`, `$shts`, `$hts`, `$noujous`, `$totals` (島営企業の値を分解したもの)
    pub ownfe: i64,
    pub shts: i64,
    pub hts: i64,
    pub noujous: i64,
    pub totals: i64,
    /// `$sx`, `$sy`, `$landName` (卵の分岐が `my` 無しで代入する)
    pub sx: i64,
    pub sy: i64,
    pub land_name: String,
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

/// 大学
pub(super) fn college(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let clv = h.lv;

    // 生物大学 (待機中): 怪獣の隣の荒地にマスコットを出す
    if clv == 4 {
        mascot(ctx, island, h, 28, "生物大学のマスコットいのら");
    }
    if clv == 98 {
        mascot(ctx, island, h, 30, "超神獣テトラ");
    }

    // 生物大学 (出動中): マスコットがいなくなったら平地に戻る
    if clv == 99 && island.scratch.c28 == 0 {
        set(island, h.x, h.y, L::Plains, 0);
        ctx.log.out(
            ctx.turn,
            format!(
                "{}の<B>{}</B>は<B>マスコットいのら</B>損失のため運営困難になりました。",
                msg::island_at(&island.name, &h.point()),
                land_name(h.land_kind, h.lv)
            ),
            Some(island.id),
            None,
        );
    }

    // 文部科学省: 周囲の施設を吸収して島営企業になる
    if clv == 80 {
        let (mut shuto, mut house, mut foodim, mut htf, mut shtf) = (0, 0, 0, 0, 0);
        for i in 1..7 {
            let Some((_, c)) = read_around(ctx, island, h, i) else {
                continue;
            };
            if c.0 == k(L::Shuto) || c.0 == k(L::Umishuto) {
                shuto += 1;
            } else if c.0 == k(L::House) {
                house += 1;
            } else if c.0 == k(L::Foodim) && c.1 == 500 {
                foodim += 1;
            } else if c.0 == k(L::HTFactory) && c.1 == 500 {
                htf += 1;
            } else if c.0 == k(L::SHTF) && c.1 == 500 {
                shtf += 1;
            }
        }

        if island.scratch.ownf == 0
            && shuto == 1
            && house == 1
            && foodim == 1
            && htf == 1
            && shtf == 1
        {
            let cell = island.map.get(h.x, h.y).unwrap_or_default();
            ctx.log.out(
                ctx.turn,
                format!(
                    "{}の<B>{}</B>は周囲の施設を吸収し、<B>{}社</B>となりました。",
                    msg::island_at(&island.name, &h.point()),
                    land_name(cell.kind, cell.value),
                    island.onm
                ),
                Some(island.id),
                None,
            );
            set(island, h.x, h.y, L::OWNF, 111);
            for i in 1..7 {
                let Some(((sx, sy), c)) = read_around(ctx, island, h, i) else {
                    continue;
                };
                if (c.0 == k(L::Foodim) || c.0 == k(L::HTFactory) || c.0 == k(L::SHTF))
                    && c.1 == 500
                {
                    set(island, sx, sy, L::Plains2, 0);
                }
            }
        }
    }

    // 文部科学省: 条件を満たさなくなったら島役所に戻る。
    // 直前に島営企業になったマスも島役所になる (Perl 版のまま)
    if (77..=80).contains(&clv) {
        let sc = &island.scratch;
        if sc.co0 < 1
            || sc.co01 < 1
            || sc.co2 < 1
            || sc.co3 < 1
            || sc.co4 < 1
            || sc.co5 < 1
            || sc.co6 < 1
            || sc.co7 < 1
            || sc.co8 < 1
            || island.eis[6] < 1_000_000
            || island.owner_stats.rena < 10000
            || island.pts < crate::tables::HOUSE_LEVELS[6]
        {
            set(island, h.x, h.y, L::Yakusho, 0);
        }
    }
    Flow::Continue
}

/// 周囲 `i` 番目のマスを読む (文部科学省・島営企業の数え上げ)。
///
/// Perl 版は範囲を確かめる前に `$landKind` と `$point` (どちらも `my` 無し) に代入する。
/// 島の中なら座標と (地形, 値) を返す
fn read_around(
    ctx: &mut TurnContext,
    island: &Island,
    h: &mut HexRun,
    i: usize,
) -> Option<((usize, usize), (u8, i64))> {
    let (sx, sy) = around(h.x as i64, h.y as i64, i);
    h.land_kind = perl_get(&island.map, sx, sy).0;
    ctx.globals.hex.point = format!("({sx}, {sy})");
    let (sx, sy) = in_island(&island.map, (sx, sy))?;
    let c = island.map.get(sx, sy).unwrap_or_default();
    Some(((sx, sy), (c.kind, c.value)))
}

/// 生物大学: 島のどこかの怪獣 (`skip_kind` 以外) の隣の荒地に `kind` の怪獣を出す。
/// 内側のループの変数はすべて `my` なので、外側のループには影響しない
fn mascot(ctx: &mut TurnContext, island: &mut Island, h: &HexRun, kind: usize, name: &str) {
    let skip_kind = kind;
    for p in 0..ctx.points.len() {
        let (sx, sy) = ctx.points[p];
        let Some(cell) = island.map.get(sx, sy) else {
            continue;
        };
        if cell.kind != k(L::Monster) {
            continue;
        }
        if monster_spec(cell.value).0 == skip_kind {
            continue;
        }
        for i in 1..7 {
            let Some((ssx, ssy)) = in_island(&island.map, around(sx as i64, sy as i64, i)) else {
                continue;
            };
            let c = island.map.get(ssx, ssy).unwrap_or_default();
            if ctx.globals.hex.special.take < 1 && c.kind == k(L::Waste) && island.scratch.c28 == 0
            {
                let ms = {
                    // 分岐の中のマッチ: 失敗すると doEachHex 冒頭の etc5 の $1.. が入る
                    let mut m = h.scope.clone();
                    ctx.globals.eisei5.assign(m.fields(&island.eisei_raw[2]))
                };
                let mshp = ms[0];
                ctx.globals.hex.kind = kind as i64;
                let spec = &MONSTERS[kind];
                let lv = ((kind as i64) << 4) + spec.base_hp + ctx.random(spec.hp_range) + mshp;
                set(island, ssx, ssy, L::Monster, lv);
                ctx.log.out(
                    ctx.turn,
                    format!(
                        "{}の<B>{name}</B>は<B>怪獣退治</B>に向かいました。",
                        msg::island_at(&island.name, &h.point())
                    ),
                    Some(island.id),
                    None,
                );
                set_value(island, h.x, h.y, 99);
                ctx.globals.hex.special.take += 1;
                island.scratch.co99 += 1;
                island.monster_live += 1;
            }
        }
    }
}

/// 島営企業
pub(super) fn ownf(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    let lv = h.lv;
    let s = {
        // 分岐の中のマッチ: 失敗すると doEachHex 冒頭の etc5 の $1.. が入る
        let mut m = h.scope.clone();
        ctx.globals.etc5.assign(m.fields(&island.etc_raw[0]))
    };
    let g = &mut ctx.globals.hex.special;
    g.ownfe = trunc(lv as f64 / 1000.0);
    g.shts = trunc(lv as f64 / 100.0).rem_euclid(10);
    g.hts = trunc(lv.rem_euclid(100) as f64 / 10.0);
    g.noujous = lv.rem_euclid(10);
    g.totals = g.shts + g.hts + g.noujous;
    g.costseisaku = s[1..].iter().sum();

    let onm = island.onm.clone();
    // 人口が 0 なら Perl 版は 0 除算で止まる (移植版は比較がすべて偽になる)
    let pop = island.pop as f64;
    let workers = (island.farm + island.scratch.factoryt + island.mountain) as f64 * 10.0;
    let mut unemployed = (pop - workers) / pop * 100.0;
    if unemployed < 0.0 {
        unemployed = -unemployed;
    }

    if island.scratch.ownf > 1 {
        set(island, x, y, L::Plains2, 0);
        island.scratch.ownf -= 1;
    }

    // "$shts$hts$noujous" (Perl 版は先頭が 0 のとき "012" のような文字列になる)
    let digits = g.shts * 100 + g.hts * 10 + g.noujous;
    if island.scratch.urikireflag == 1 {
        set_value(island, x, y, digits);
    }

    if ctx.random(1000) < trunc(island.owner_stats.rena as f64 / 1000.0)
        && ctx.globals.hex.special.ownfe == 0
    {
        set_value(island, x, y, 1000 + digits);
        ctx.log.out(
            turn,
            format!(
                "{}の<B>{onm}社</B>は、<B>腐海の毒消し薬</B>を開発しました。",
                msg::island_at(&island.name, &h.point())
            ),
            Some(id),
            None,
        );
    }

    let (mut shuto, mut house) = (0, 0);
    for i in 1..7 {
        let Some((_, c)) = read_around(ctx, island, h, i) else {
            continue;
        };
        if c.0 == k(L::Shuto) || c.0 == k(L::Umishuto) {
            shuto += 1;
        } else if c.0 == k(L::House) {
            house += 1;
        }
    }

    for i in 1..7 {
        let Some(((sx, sy), c)) = read_around(ctx, island, h, i) else {
            continue;
        };
        let g = &ctx.globals.hex.special;
        let rena = island.owner_stats.rena;
        // 吸収できるか (部門の数 n は吸収する地形ごとに違う)
        let ok = |n: i64| {
            n < 8
                && ((8 - n) * 20) as f64 > unemployed
                && shuto == 1
                && house == 1
                && n * 15 < g.costseisaku
                && ((24 - g.totals) * 5) as f64 > unemployed
                && g.totals * 5 < g.costseisaku
                && g.totals * 800 < rena
                && n * 1875 < rena
        };
        let add = if c.0 == k(L::Foodim) && c.1 == 500 && ok(g.noujous) {
            1
        } else if c.0 == k(L::HTFactory) && c.1 == 500 && ok(g.hts) {
            10
        } else if c.0 == k(L::SHTF) && c.1 == 500 && ok(g.shts) {
            100
        } else {
            continue;
        };
        let target = land_name(c.0, c.1);
        ctx.log.out(
            turn,
            format!(
                "{}の<B>{onm}社</B>は<B>{target}</B>を吸収合併しました。",
                msg::island_at(&island.name, &h.point())
            ),
            Some(id),
            None,
        );
        set(island, sx, sy, L::Plains2, 0);
        let v = island.map.get(x, y).unwrap_or_default().value;
        set_value(island, x, y, v + add);
        let g = &mut ctx.globals.hex.special;
        match add {
            1 => g.noujous += 1,
            10 => g.hts += 1,
            _ => g.shts += 1,
        }
        g.totals += 1;
    }
    Flow::Continue
}

/// 記念碑
pub(super) fn monument(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    let molv = h.lv;
    match molv {
        0 | 10 | 15 | 16 => {
            if ctx.random(100) < 5 {
                // お土産屋さんの収入
                let l_name = land_name(h.land_kind, h.lv);
                let value = 1 + ctx.random(49);
                island.money += value;
                let amount = format!("{value}{}", ctx.config.units.money);
                ctx.log.out(
                    turn,
                    format!(
                        "{}の<B>{l_name}記念碑公園</B>のお土産屋さんから<B>{amount}</B>の収入がありました。",
                        msg::island_at(&island.name, &h.point())
                    ),
                    Some(id),
                    None,
                );
            }
        }
        1 => {
            if ctx.random(100) < 1 {
                // 豊作
                let l_name = land_name(h.land_kind, h.lv);
                let value = trunc(island.pop as f64 / 100.0) * 10 + ctx.random(11);
                island.food += value;
                let amount = format!("{value}{}", ctx.config.units.food);
                if value > 0 {
                    ctx.log.out(
                        turn,
                        format!(
                            "{}の<B>{l_name}</B>がもたらした豊作により、さらに<B>{amount}</B>の食料が出来ました。",
                            msg::island_at(&island.name, &h.point())
                        ),
                        Some(id),
                        None,
                    );
                }
            }
        }
        80 => egg(ctx, island, h, 5, [5, 25, 35, 25]),
        81 => egg(ctx, island, h, 3, [3, 20, 40, 15]),
        82 => egg(ctx, island, h, 3, [3, 30, 40, 30]),
        83 => egg(ctx, island, h, 5, [10, 25, 30, 30]),
        84 => {
            if ctx.random(100) < 75 {
                // 古代遺跡の収入
                let nt = town_count(island, x, y);
                let value = ctx.random(nt * 20 + h.lv * 5 + trunc(island.pop as f64 / 20.0))
                    + ctx.random(100)
                    + 100;
                if value > 0 {
                    island.money += value;
                    ctx.globals.hex.m84income += value;
                }
            }
        }
        93 => {
            // 幸運 (ログは出さない)
            island.money += ctx.config.oil_money + ctx.random(500);
            island.food += trunc(island.pop as f64 / 20.0) + ctx.random(11);
        }
        94 => baria(ctx, island, h),
        _ => {}
    }
    Flow::Continue
}

/// 卵 (記念碑 80〜83): `rate`% で孵化し、怪獣になって周りを水没させる。
/// `odds` はミカエル・テトラ・スラレジェ・はねはむを順に引く確率 (外れはいのら)
fn egg(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun, rate: i64, odds: [i64; 4]) {
    if ctx.random(100) >= rate {
        return;
    }
    let (id, turn) = (island.id, ctx.turn);
    // `$i` は外側のループの添字 (Perl 版のまま)
    h.i = 0;
    while h.i < 7 {
        let i = h.i;
        let (sx, sy) = around(h.x as i64, h.y as i64, i);
        let (kind, lv) = perl_get(&island.map, sx, sy);
        let g = &mut ctx.globals.hex;
        g.special.sx = sx;
        g.special.sy = sy;
        h.land_kind = kind;
        h.lv = lv;
        g.special.land_name = land_name(kind, lv);
        let point = format!("({sx}, {sy})");
        g.point = point.clone();

        let Some((sx, sy)) = in_island(&island.map, (sx, sy)) else {
            h.i += 1;
            continue;
        };

        if i < 1 {
            // 中心: 怪獣が出てくる
            let m_kind = if ctx.random(100) < odds[0] {
                13 // ミカエル
            } else if ctx.random(100) < odds[1] {
                29 // テトラ
            } else if ctx.random(100) < odds[2] {
                14 // スラレジェ
            } else if ctx.random(100) < odds[3] {
                12 // はねはむ
            } else {
                1 // いのら (はずれ)
            };
            ctx.globals.hex.kind = m_kind as i64;
            let spec = &MONSTERS[m_kind];
            h.lv = ((m_kind as i64) << 4) + spec.base_hp + ctx.random(spec.hp_range);
            set(island, sx, sy, L::Monster, h.lv);
            let m_name = monster_spec(h.lv).1;
            ctx.log.out(
                turn,
                format!(
                    "{}の<B>{}</B>から<B>{m_name}</B>が出現しました。",
                    msg::island_at(&island.name, &point),
                    ctx.globals.hex.special.land_name
                ),
                Some(id),
                None,
            );
        } else {
            const SAFE: [L; 12] = [
                L::Sea,
                L::Oil,
                L::Mountain,
                L::Gold,
                L::Onsen,
                L::Seacity,
                L::Umishuto,
                L::Seatown,
                L::Umiamu,
                L::Fune,
                L::Frocity,
                L::Sbase,
            ];
            if !SAFE.iter().any(|&l| kind == k(l)) {
                let name = land_name(kind, h.lv);
                ctx.globals.hex.special.land_name = name.clone();
                ctx.log.out(
                    turn,
                    format!(
                        "{}の<B>{name}</B>は{}により水没しました。",
                        msg::island_at(&island.name, &point),
                        wrap(tags::DISASTER, "卵の破裂によるエネルギー")
                    ),
                    Some(id),
                    None,
                );
                set(island, sx, sy, L::Sea, 0);
            }
        }
        h.i += 1;
    }
}

/// 記念碑 94: 隣の怪獣を押し潰す。「行による位置調整」をしない (Perl 版のまま)
fn baria(ctx: &mut TurnContext, island: &mut Island, h: &HexRun) {
    let size = island.map.size as i64;
    // 負の添字は反対側の端 (Perl の配列)、大きすぎる添字は未定義
    let wrap_index = |v: i64| {
        let v = if v < 0 { v + size } else { v };
        (0..size).contains(&v).then_some(v as usize)
    };
    for i in 1..7 {
        let sx = h.x as i64 + AX[i];
        let sy = h.y as i64 + AY[i];
        let (kind, value) = perl_get(&island.map, sx, sy);
        if kind != k(L::Monster) {
            continue;
        }
        let (Some(wx), Some(wy)) = (wrap_index(sx), wrap_index(sy)) else {
            continue;
        };
        let t_name = monster_spec(value).1;
        ctx.log.out(
            ctx.turn,
            format!(
                "{}の<B>{t_name}</B>が<B>強力な力場</B>に押し潰されました。",
                msg::island_at(&island.name, &format!("({sx}, {sy})"))
            ),
            Some(island.id),
            ctx.globals.hex.t_id,
        );
        set(island, wx, wy, L::Waste, 1);
    }
}
