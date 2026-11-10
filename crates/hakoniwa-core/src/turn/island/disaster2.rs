//! 地盤沈下・台風・巨大隕石・巨大ミサイル・隕石・噴火 (Perl 版 15248〜15665 行)。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 地盤沈下は沈むマスをいったん -1 にしてから浅瀬にする。周りの海を数えるとき、
//!   先に -1 になったマスは海として数えない (マスを見る順番で結果が変わる)。
//! - 隕石の「バリア」「お守り」の分岐は `my` の無い `$x`, `$y`, `$landKind`, `$lv`, `$point`
//!   (グローバル変数) に代入する。
//! - 隕石が防衛施設・改に守られるかの判定は、島の外のマスを未定義のグローバル変数 `$kind`
//!   と海で比べて数える (`$kind` が 0 = 海なら、島の端に落ちた隕石は外側の数だけ数えられる)。
//! - 隕石のくり返しは `random(2) == 0` を先に評価するので、1 回目にも乱数を引く。
//! - 噴火の周りのマスは、範囲を確かめる前に読む (`my` の変数なので結果は変わらない)。

use crate::land::{around, count_around, in_island, land_name};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl;
use crate::tables::LandKind as L;
use crate::turn::TurnContext;
use crate::turn::hex::monster::{m as mm, wide_damage};
use crate::turn::hex::msg;
use crate::turn::hex::town::{set, set_value};

use super::ProcRun;

/// この段階で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$x`, `$y` (隕石の「バリア」「お守り」の分岐が `my` を付けずに代入する)
    pub x: i64,
    pub y: i64,
    /// `$landKind`, `$lv` (同上)
    pub land_kind: i64,
    pub lv: i64,
}

/// この段階で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

/// 地盤沈下で沈むマスの印 (Perl 版の -1)。どの地形の番号とも重ならない値
const SINKING: u8 = u8::MAX;

const fn k(l: L) -> u8 {
    l as u8
}

fn is_one_of(kind: u8, kinds: &[L]) -> bool {
    kinds.iter().any(|&l| kind == l as u8)
}

fn out(ctx: &mut TurnContext, id: i64, message: String) {
    ctx.log.out(ctx.turn, message, Some(id), None);
}

fn point(x: impl std::fmt::Display, y: impl std::fmt::Display) -> String {
    format!("({x}, {y})")
}

/// `$toto2` を書き換えて `etc8` に書き戻す
fn set_toto2(ctx: &mut TurnContext, island: &mut Island, toto2: i64) {
    ctx.globals.etc8.0[1] = toto2;
    island.etc_raw[3] = perl::join(&ctx.globals.etc8.0);
}

pub(super) fn run(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, _p: &mut ProcRun) {
    let island = &mut islands[idx];
    falldown(ctx, island);
    typhoon(ctx, island);
    huge_meteo(ctx, island);
    big_missile(ctx, island);
    meteo(ctx, island);
    eruption(ctx, island);
}

/// 地盤沈下 (15248〜15306 行)
fn falldown(ctx: &mut TurnContext, island: &mut Island) {
    let d = &ctx.config.disaster;
    if !(island.area > d.fall_border && ctx.random(1000) < d.falldown) {
        return;
    }
    let id = island.id;
    out(ctx, id, m::falldown(&island.name));

    const SAFE: [L; 12] = [
        L::Sea,
        L::Ice,
        L::Sbase,
        L::Seacity,
        L::Seatown,
        L::Umishuto,
        L::Fune,
        L::Umiamu,
        L::Oil,
        L::Gold,
        L::Onsen,
        L::Mountain,
    ];
    const SEA: [L; 7] = [
        L::Sea,
        L::Seacity,
        L::Seatown,
        L::Umishuto,
        L::Fune,
        L::Umiamu,
        L::Sbase,
    ];
    for &(x, y) in &ctx.points.clone() {
        let Some(c) = island.map.get(x, y) else {
            continue;
        };
        if c.kind == SINKING || is_one_of(c.kind, &SAFE) {
            continue;
        }
        // 周囲に海があれば、値を-1に
        let sea: i64 = SEA
            .iter()
            .map(|&l| count_around(&island.map, x as i64, y as i64, l, 7))
            .sum();
        if sea > 0 {
            out(
                ctx,
                id,
                m::falldown_land(&island.name, &land_name(c.kind, c.value), &point(x, y)),
            );
            set_value(island, x, y, 0);
            if let Some(c) = island.map.get_mut(x, y) {
                c.kind = SINKING;
            }
        }
    }

    for &(x, y) in &ctx.points.clone() {
        let Some(c) = island.map.get(x, y) else {
            continue;
        };
        if c.kind == SINKING {
            // -1になっている所を浅瀬に
            set(island, x, y, L::Sea, 1);
        } else if c.kind == k(L::Sea) {
            // 浅瀬は海に
            set_value(island, x, y, 0);
        }
    }
}

/// 台風 (15308〜15355 行)
fn typhoon(ctx: &mut TurnContext, island: &mut Island) {
    if ctx.random(1000) >= ctx.config.disaster.typhoon - island.eis[0] / 10 {
        return;
    }
    let id = island.id;
    out(ctx, id, m::typhoon(&island.name));
    island.scratch.typhoon = true;

    let toto2 = ctx.globals.etc8.0[1];
    if toto2 > 0 {
        set_toto2(ctx, island, toto2 - 1);
        out(ctx, id, m::omamori(&island.name));
        return;
    }

    let co5 = island.scratch.co5;
    for &(x, y) in &ctx.points.clone() {
        let Some(c) = island.map.get(x, y) else {
            continue;
        };
        let (kind, lv) = (c.kind, c.value);
        if is_one_of(kind, &[L::Farm, L::EneWd, L::Haribote]) {
            // 1d12 <= (6 - 周囲の森) で崩壊
            let r = ctx.random(12 + co5 * 5);
            if r < 6
                - count_around(&island.map, x as i64, y as i64, L::Forest, 7)
                - count_around(&island.map, x as i64, y as i64, L::Monument, 7)
            {
                out(
                    ctx,
                    id,
                    m::typhoon_damage(&island.name, &land_name(kind, lv), &point(x, y)),
                );
                set(island, x, y, L::Plains, 0);
            }
        }
        // 上で平地になっていても、読んだときの地形で判定する
        if is_one_of(kind, &[L::Fune, L::Nursery]) && ctx.random(100 + co5 * 50) < 10 {
            out(
                ctx,
                id,
                m::typhoon_hason(&island.name, &land_name(kind, lv), &point(x, y)),
            );
            set(island, x, y, L::Sea, 1);
        }
    }
}

/// 巨大隕石 (15357〜15391 行)
fn huge_meteo(ctx: &mut TurnContext, island: &mut Island) {
    let s04 = ctx.globals.etc5.0[4];
    if ctx.random(1000) >= ctx.config.disaster.huge_meteo - island.eis[2] / 50 - s04 / 10 {
        return;
    }
    let id = island.id;
    let size = ctx.config.island_size as i64;
    // 落下
    let x = ctx.random(size);
    let y = ctx.random(size);
    out(ctx, id, mm::huge_meteo(&island.name, &point(x, y)));
    let (ux, uy) = (x as usize, y as usize);

    let toto2 = ctx.globals.etc8.0[1];
    if island.scratch.h10 >= 1 {
        out(ctx, id, m::omamori2(&island.name));
        set(island, ux, uy, L::Sea, 0);
    } else if toto2 > 1 {
        set_toto2(ctx, island, toto2 - 2);
        out(ctx, id, m::omamori(&island.name));
        set(island, ux, uy, L::Sea, 0);
    } else {
        // 広域被害ルーチン
        wide_damage(ctx, island, x, y);
        if ctx.rand_f64(1000.0) < 100.0 {
            set(island, ux, uy, L::Monument, 79);
        }
    }
}

/// 巨大ミサイル (15393〜15411 行)。記念碑の発射の回数だけ落ちる
fn big_missile(ctx: &mut TurnContext, island: &mut Island) {
    let id = island.id;
    let size = ctx.config.island_size as i64;
    while island.scratch.command.build.bigmissile > 0 {
        island.scratch.command.build.bigmissile -= 1;
        // 落下
        let x = ctx.random(size);
        let y = ctx.random(size);
        out(ctx, id, m::mon_damage(&island.name, &point(x, y)));
        // 広域被害ルーチン
        wide_damage(ctx, island, x, y);
    }
}

/// 隕石 (15413〜15571 行)
fn meteo(ctx: &mut TurnContext, island: &mut Island) {
    let s04 = ctx.globals.etc5.0[4];
    if ctx.random(1000) >= ctx.config.disaster.meteo - island.eis[2] / 40 - s04 / 10 {
        return;
    }
    let id = island.id;
    let size = ctx.config.island_size as i64;
    let toto2 = ctx.globals.etc8.0[1];
    let barrier = island.scratch.h10 >= 1;
    if barrier || toto2 > 0 {
        // 落下 ($x, $y, $landKind, $lv, $point はグローバル変数)
        let x = ctx.random(size);
        let y = ctx.random(size);
        let (ux, uy) = (x as usize, y as usize);
        let c = island.map.get(ux, uy).unwrap_or_default();
        let g = &mut ctx.globals.process.disaster2;
        (g.x, g.y, g.land_kind, g.lv) = (x, y, c.kind as i64, c.value);
        let p = point(x, y);
        ctx.globals.hex.point = p.clone();
        set(island, ux, uy, L::Sea, 0);
        // メッセージ
        out(ctx, id, m::huge_meteo4(&island.name, &p));
        if barrier {
            out(ctx, id, m::omamori2(&island.name));
        } else {
            set_toto2(ctx, island, toto2 - 1);
            out(ctx, id, m::omamori(&island.name));
        }
        return;
    }

    let mut first = true;
    while ctx.random(2) == 0 || first {
        first = false;
        // 落下
        let x = ctx.random(size);
        let y = ctx.random(size);
        let (ux, uy) = (x as usize, y as usize);
        let c = island.map.get(ux, uy).unwrap_or_default();
        let (kind, lv) = (c.kind, c.value);
        let p = point(x, y);

        let mut count = 0;
        for i in 0..19 {
            match in_island(&island.map, around(x, y, i)) {
                None => {
                    // 範囲外の場合。Perl 版は未定義のグローバル変数 $kind と比べている
                    if ctx.globals.hex.kind == L::Sea as i64 {
                        count += 1;
                    }
                }
                Some((sx, sy)) => {
                    let c = island.map.get(sx, sy).unwrap_or_default();
                    if c.kind == k(L::Defence) && c.value == 77 {
                        if ctx.rand_f64(100.0) < 30.0 {
                            set(island, sx, sy, L::Waste, 0);
                            out(
                                ctx,
                                id,
                                m::train_end2(&island.name, "防衛施設・改", &point(sx, sy)),
                            );
                        }
                        count += 1;
                    }
                }
            }
        }

        if count > 0 && island.eis[4] >= 1 {
            out(ctx, id, m::mid_meteo3(&island.name, &p));
            island.scratch.roudenflag += 1;
            island.eis[4] -= ctx.random(50);
            if island.eis[4] < 1 {
                island.eis[4] = 0;
                out(ctx, id, m::eisei_end(&island.name, "防衛衛星"));
            }
            continue;
        }

        let l_name = land_name(kind, lv);
        let name = &island.name;
        let message = match L::from_u8(kind) {
            // 海ポチャ
            Some(L::Sea) if lv == 0 => mm::meteo_sea(name, &l_name, &p),
            // 山破壊
            Some(L::Mountain | L::Gold | L::Onsen) => {
                out(ctx, id, mm::meteo_mountain(name, &l_name, &p));
                set(island, ux, uy, L::Waste, 0);
                continue;
            }
            Some(
                L::Sbase | L::Seacity | L::Umishuto | L::Seatown | L::Fune | L::Frocity | L::Umiamu,
            ) => mm::meteo_sbase(name, &l_name, &p),
            Some(L::Monster) => mm::meteo_monster(name, &l_name, &p),
            // 浅瀬
            Some(L::Sea | L::Ice) => mm::meteo_sea1(name, &l_name, &p),
            _ => mm::meteo_normal(name, &l_name, &p),
        };
        out(ctx, id, message);
        set(island, ux, uy, L::Sea, 0);
        if ctx.rand_f64(1000.0) < 50.0 {
            set(island, ux, uy, L::Monument, 79);
        }
    }
}

/// 噴火 (15573〜15665 行)
fn eruption(ctx: &mut TurnContext, island: &mut Island) {
    let s04 = ctx.globals.etc5.0[4];
    if ctx.random(1000) >= ctx.config.disaster.eruption - island.eis[1] / 40 - s04 / 10 {
        return;
    }
    let id = island.id;
    let size = ctx.config.island_size as i64;
    let x = ctx.random(size);
    let y = ctx.random(size);
    let (ux, uy) = (x as usize, y as usize);
    out(ctx, id, m::eruption(&island.name, &point(x, y)));
    set(island, ux, uy, L::Mountain, 0);

    let toto2 = ctx.globals.etc8.0[1];
    if toto2 > 1 {
        set_toto2(ctx, island, toto2 - 2);
        out(ctx, id, m::omamori(&island.name));
        return;
    }

    if ctx.rand_f64(1000.0) < 50.0 {
        set(island, ux, uy, L::Monument, 78);
    }
    if ctx.rand_f64(1000.0) < 100.0 {
        set(island, ux, uy, L::Monument, 75);
    }
    const SEA: [L; 10] = [
        L::Sea,
        L::Ice,
        L::Oil,
        L::Fune,
        L::Frocity,
        L::Umiamu,
        L::Seacity,
        L::Seatown,
        L::Umishuto,
        L::Sbase,
    ];
    const KEEP: [L; 5] = [L::Mountain, L::Monster, L::Gold, L::Onsen, L::Waste];
    for i in 1..7 {
        // Perl 版は範囲を確かめる前にも読むが、その値は使わない
        let Some((sx, sy)) = in_island(&island.map, around(x, y, i)) else {
            continue;
        };
        let c = island.map.get(sx, sy).unwrap_or_default();
        let (kind, lv) = (c.kind, c.value);
        let p = point(sx, sy);
        let l_name = land_name(kind, lv);
        if is_one_of(kind, &SEA) {
            // 海の場合
            if lv == 1 || kind == k(L::Ice) {
                // 浅瀬 (陸地になる)
                out(ctx, id, m::eruption_sea1(&island.name, &l_name, &p));
            } else {
                out(ctx, id, m::eruption_sea(&island.name, &l_name, &p));
                set(island, sx, sy, L::Sea, 1);
                continue;
            }
        } else if is_one_of(kind, &KEEP) {
            continue;
        } else {
            // それ以外の場合
            out(ctx, id, m::eruption_normal(&island.name, &l_name, &p));
        }
        set(island, sx, sy, L::Waste, 0);
        if ctx.rand_f64(1000.0) < 50.0 {
            set(island, sx, sy, L::Monument, 75);
        }
    }
}

/// ログの文面
mod m {
    use super::{msg, tags, wrap};

    fn ia(name: &str, point: &str) -> String {
        msg::island_at(name, point)
    }

    fn d(s: &str) -> String {
        wrap(tags::DISASTER, s)
    }

    /// `logFalldown`
    pub fn falldown(name: &str) -> String {
        format!("{}で{}が発生しました！！", msg::island(name), d("地盤沈下"))
    }

    /// `logFalldownLand`
    pub fn falldown_land(name: &str, l: &str, point: &str) -> String {
        format!("{}の<B>{l}</B>は海の中へ沈みました。", ia(name, point))
    }

    /// `logTyphoon`
    pub fn typhoon(name: &str) -> String {
        format!("{}に{}上陸！！", msg::island(name), d("台風"))
    }

    /// `logOmamori`
    pub fn omamori(name: &str) -> String {
        format!(
            "{}所有の<B>お守り</B>のお陰でしょうか、{}が少なかったようです！！",
            msg::island(name),
            d("被害")
        )
    }

    /// `logOmamori2`
    pub fn omamori2(name: &str) -> String {
        format!(
            "{}を取り巻く<B>バリア</B>のお陰で{}が少なかったようです！！",
            msg::island(name),
            d("被害")
        )
    }

    /// `logTyphoonDamage`
    pub fn typhoon_damage(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}の<B>{l}</B>は{}で飛ばされました。",
            ia(name, point),
            d("台風")
        )
    }

    /// `logTyphoonHason`
    pub fn typhoon_hason(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}の<B>{l}</B>は{}によって破損しました。",
            ia(name, point),
            d("台風")
        )
    }

    /// `logMonDamage`
    pub fn mon_damage(name: &str, point: &str) -> String {
        format!(
            "<B>何かとてつもないもの</B>が{}地点に落下しました！！",
            ia(name, point)
        )
    }

    /// `logHugeMeteo4`
    pub fn huge_meteo4(name: &str, point: &str) -> String {
        format!("{}地点に{}が落下！！", ia(name, point), d("隕石"))
    }

    /// `logTrainEnd2`
    pub fn train_end2(name: &str, l: &str, point: &str) -> String {
        format!("{}の<B>{l}</B>は壊滅したようです。", ia(name, point))
    }

    /// `logMidMeteo3`
    pub fn mid_meteo3(name: &str, point: &str) -> String {
        format!(
            "{}地点に{}が落下！！しましたが、周囲の<b>防衛施設・改</b>が防衛したようです。",
            ia(name, point),
            d("隕石")
        )
    }

    /// `logEiseiEnd`
    pub fn eisei_end(name: &str, eisei: &str) -> String {
        format!(
            "{}の<B>{eisei}</B>は{}したようです！！",
            msg::island(name),
            d("崩壊")
        )
    }

    /// `logEruption` (`$lName` は使わない)
    pub fn eruption(name: &str, point: &str) -> String {
        format!(
            "{}地点で{}、<B>山</B>が出来ました。",
            ia(name, point),
            d("火山が噴火")
        )
    }

    /// `logEruptionSea1`
    pub fn eruption_sea1(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}地点の<B>{l}</B>は、{}の影響で陸地になりました。",
            ia(name, point),
            d("噴火")
        )
    }

    /// `logEruptionSea`
    pub fn eruption_sea(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}地点の<B>{l}</B>は、{}の影響で海底が隆起、浅瀬になりました。",
            ia(name, point),
            d("噴火")
        )
    }

    /// `logEruptionNormal`
    pub fn eruption_normal(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}地点の<B>{l}</B>は、{}の影響で壊滅しました。",
            ia(name, point),
            d("噴火")
        )
    }
}
