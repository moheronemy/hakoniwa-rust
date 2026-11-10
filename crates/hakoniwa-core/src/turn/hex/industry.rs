//! 畜産・食品加工・発電・工場・森・倉庫・家・防衛施設・油田・浅瀬・砂浜・氷河・関所・役所・金山・遊園地。
//!
//! Perl 版でこの系統の分岐が `my` を付けずに代入する変数 (`$value`, `$valuek`, `$seq`,
//! `$choki`, `$zeikin`, `$AtAttackslog`, `$str`) は、どれも分岐の中で読む前に必ず代入しているので、
//! 前の値が結果に影響しない。移植版では局所変数にしている。
//! (`$value`, `$str` などは他の処理も同じ名前のグローバル変数として使う)

use crate::land::{around, count_around, in_island, land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::trunc;
use crate::tables::{HOUSE_LEVELS, LandKind as L};
use crate::turn::{TurnContext, monster_spec};

use super::town::{set, set_value, town_count};
use super::{Flow, HexRun, k, msg};

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| kind == k(l))
}

fn cell_value(island: &Island, x: usize, y: usize) -> i64 {
    island.map.get(x, y).map_or(0, |c| c.value)
}

/// 養鶏場・養豚場・牧場。
///
/// 周りに食品加工工場があり電力が足りていれば、食料の代わりに加工品の収益を上げる。
/// 3 種類は Perl 版では別々の分岐だが、違いは食料の倍率と成長の式だけ
pub(super) fn livestock(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    let farm_count = count_around(&island.map, x as i64, y as i64, L::Farm, 7);
    let foodka_count = count_around(&island.map, x as i64, y as i64, L::Foodka, 7);
    let mult = if h.land_kind == k(L::Farmchi) {
        1
    } else if h.land_kind == k(L::Farmpic) {
        2
    } else {
        3
    };
    let value = mult * h.lv;

    if foodka_count > 0 && island.scratch.shouhi < island.scratch.ene {
        let valuek = trunc((h.lv * mult) as f64 / foodka_count as f64);
        let valuek = valuek as f64;
        for i in 1..7 {
            let Some((sx, sy)) = in_island(&island.map, around(x as i64, y as i64, i)) else {
                continue;
            };
            let c = island.map.get(sx, sy).unwrap_or_default();
            if c.kind != k(L::Foodka) {
                continue;
            }
            let (money, shouhi) = match c.value {
                1 => (0.175, 0.005),
                2 => (0.25, 0.015),
                3 => (0.4, 0.03),
                _ => continue,
            };
            island.money += trunc(valuek * money);
            island.scratch.shouhi += trunc(valuek * shouhi);
        }
    } else {
        island.food += value;
    }

    let s08b = ctx.globals.hex.s08b;
    h.lv += if h.land_kind == k(L::Farmchi) {
        ctx.random(8 + farm_count * 3) + 5 + s08b
    } else if h.land_kind == k(L::Farmpic) {
        ctx.random(4 + farm_count * 2 + s08b) + 3 + s08b
    } else {
        ctx.random(4 + farm_count + s08b) + 1 + trunc(s08b as f64 / 2.0)
    };
    if h.lv > 4000 {
        h.lv = 4000;
    }
    set_value(island, x, y, h.lv);
    Flow::Continue
}

/// 食品加工工場: 周りの畜産施設と町の数で規模 (0〜3) が決まる
pub(super) fn foodka(
    _ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x as i64, h.y as i64);
    let map = &island.map;
    let chi = count_around(map, x, y, L::Farmchi, 7);
    let pic = count_around(map, x, y, L::Farmpic, 7);
    let cow = count_around(map, x, y, L::Farmcow, 7);
    let farm = count_around(map, x, y, L::Farm, 7);
    let towns = town_count(island, h.x, h.y);
    let towns_a: i64 = [
        L::Town,
        L::Newtown,
        L::Bigtown,
        L::Bettown,
        L::Skycity,
        L::Umicity,
        L::Rizort,
        L::Kajino,
        L::BigRizort,
    ]
    .iter()
    .map(|&l| count_around(map, x, y, l, 19))
    .sum();
    // $lv は my の無い外側の変数なので、書き換えた値で共通の判定をする
    h.lv = if island.scratch.shouhi > island.scratch.ene {
        0
    } else if farm > 0 && cow > 0 && chi > 0 && towns_a > 3 {
        3
    } else if farm > 0 && cow > 0 && towns > 2 {
        2
    } else if chi > 0 || pic > 0 || cow > 0 {
        1
    } else {
        0
    };
    set_value(island, h.x, h.y, h.lv);
    Flow::Continue
}

/// バイオマス発電所: 食料を消費する
pub(super) fn ene_bo(
    _ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    islands[idx].food -= h.lv * 5;
    Flow::Continue
}

/// ソーラー発電所: 少しずつ劣化し、値が尽きると平地に戻る
pub(super) fn ene_so(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let v = cell_value(island, h.x, h.y) - ctx.random(20);
    set_value(island, h.x, h.y, v);
    if v <= 0 {
        set(island, h.x, h.y, L::Plains, 0);
        return Flow::Next;
    }
    Flow::Continue
}

/// 原子力発電所: 放射能漏れで周囲 2 ヘックスの町系の値が減る
pub(super) fn ene_at(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    if ctx.random(1000) >= 50 - trunc(h.lv as f64 / 100.0) {
        return Flow::Continue;
    }
    let mut logged = 0;
    // 内側のループの $i, $landKind, $lv は my で宣言した別の変数
    for i in 0..19 {
        let Some((sx, sy)) = in_island(&island.map, around(x as i64, y as i64, i)) else {
            continue;
        };
        let c = island.map.get(sx, sy).unwrap_or_default();
        if c.value > 1
            && is_one_of(
                c.kind,
                &[
                    L::Town,
                    L::Minato,
                    L::Procity,
                    L::Frocity,
                    L::Newtown,
                    L::Bigtown,
                    L::Bettown,
                    L::Skycity,
                    L::Umicity,
                    L::Rizort,
                    L::Kajino,
                    L::BigRizort,
                    L::Shuto,
                    L::Onsen,
                ],
            )
        {
            let v = c.value - ctx.random(25);
            set_value(island, sx, sy, v);
            // Perl 版は減らす前の値 (> 1) で「0 以下なら平地に戻す」を判定しているので、
            // 値が 0 以下になっても地形はそのまま (Perl 版のまま)
            if logged <= 0 {
                let me = island.map.get(x, y).unwrap_or_default();
                ctx.log.out(
                    ctx.turn,
                    format!(
                        "{}の<B>{}</B>での{}が噂され、付近の住民への不安が広がってます。",
                        msg::island_at(&island.name, &h.point()),
                        land_name(me.kind, me.value),
                        wrap(tags::DISASTER, "放射能漏れ")
                    ),
                    Some(island.id),
                    None,
                );
                logged += 1;
            }
        }
    }
    Flow::Continue
}

/// ハイテク工場・超ハイテク工場: 島主の `pika` があれば規模が増える
fn high_tech(islands: &mut [Island], idx: usize, h: &HexRun, step: i64) -> Flow {
    let island = &mut islands[idx];
    if island.owner_stats.pika > 0 {
        let v = (cell_value(island, h.x, h.y) + step).min(500);
        set_value(island, h.x, h.y, v);
    }
    Flow::Continue
}

pub(super) fn ht_factory(
    _ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    high_tech(islands, idx, h, 2)
}

pub(super) fn shtf(
    _ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    high_tech(islands, idx, h, 1)
}

/// 森: 周りの森の数に応じて木が増える
pub(super) fn forest(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    // 自分も数えるので 1 以上
    let forest_count = count_around(&island.map, x as i64, y as i64, L::Forest, 19);
    let cap = 200 + forest_count * 200;
    if h.lv < cap {
        let add = 1 + ctx.random(forest_count) + ctx.globals.hex.s08b;
        let v = cell_value(island, x, y) + add;
        set_value(island, x, y, v);
    }
    // 増やす前の値で上限を判定する (Perl 版のまま)
    if h.lv > cap {
        set_value(island, x, y, cap);
    }
    Flow::Continue
}

/// 倉庫: 大怪盗に貯蓄を盗まれる
pub(super) fn kura(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    let mut seq = trunc(h.lv as f64 / 100.0);
    let mut choki = h.lv.rem_euclid(100);
    if ctx.random(100) < 9 - seq {
        let r = ctx.random(100);
        choki = trunc(choki as f64 / 100.0 * r as f64);
        seq -= 1;
        if seq < 0 {
            seq = 0;
        }
        set_value(island, x, y, seq * 100 + choki);
        ctx.log.out(
            ctx.turn,
            format!(
                "{}の<B>{}</B>へ{}",
                msg::island_at(&island.name, &h.point()),
                land_name(h.land_kind, h.lv),
                wrap(tags::DISASTER, "大怪盗が侵入したようです！！")
            ),
            Some(island.id),
            None,
        );
    }
    if ctx.config.another_mode {
        choki -= trunc(choki as f64 / 100.0 * seq as f64);
        if choki < 0 {
            choki = 0;
        }
        set_value(island, x, y, seq * 100 + choki);
    }
    Flow::Continue
}

/// 家: 税収
pub(super) fn house(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let zeikin = trunc((island.pop * (h.lv + 1) * island.eisei[0]) as f64 / 100.0);
    let pay = if ctx.config.another_mode {
        true
    } else if zeikin > 10000 {
        ctx.turn % 5 == 0
    } else if zeikin > 5000 {
        ctx.turn % 2 == 0
    } else {
        true
    };
    if pay {
        island.money += zeikin;
    }
    Flow::Continue
}

/// 防衛施設: 値が 1 なら自爆する
pub(super) fn defence(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    if h.lv == 1 {
        let island = &mut islands[idx];
        ctx.log.out(
            ctx.turn,
            format!(
                "{}の<B>{}</B>、{}",
                msg::island_at(&island.name, &h.point()),
                land_name(h.land_kind, h.lv),
                wrap(tags::DISASTER, "自爆装置作動！！")
            ),
            Some(island.id),
            None,
        );
        wide_damage(ctx, island, h.x, h.y);
    }
    Flow::Continue
}

/// `wideDamage`: 広域被害ルーチン (中心と隣は海に、その外側は荒地になる)
pub(crate) fn wide_damage(ctx: &mut TurnContext, island: &mut Island, x: usize, y: usize) {
    let (id, turn) = (island.id, ctx.turn);
    for i in 0..19 {
        let (sx, sy) = around(x as i64, y as i64, i);
        // Perl 版は範囲を確かめる前に読む (名前を作るだけなので結果は変わらない)
        let (kind, lv) = perl_get(&island.map, sx, sy);
        let Some((sx, sy)) = in_island(&island.map, (sx, sy)) else {
            continue;
        };
        let name = land_name(kind, lv);
        let at = msg::island_at(&island.name, &format!("({sx}, {sy})"));
        if i < 7 {
            // 中心、および 1 ヘックス
            if kind == k(L::Sea) {
                set_value(island, sx, sy, 0);
                continue;
            } else if is_one_of(
                kind,
                &[
                    L::Sbase,
                    L::Seacity,
                    L::Seatown,
                    L::Umishuto,
                    L::Fune,
                    L::Ice,
                    L::Frocity,
                    L::Umiamu,
                    L::Oil,
                ],
            ) {
                ctx.log.out(
                    turn,
                    format!("{at}の<B>{name}</B>は跡形もなくなりました。"),
                    Some(id),
                    None,
                );
                set(island, sx, sy, L::Sea, 0);
            } else {
                if kind == k(L::Monster) {
                    let (m_kind, _, _) = monster_spec(lv);
                    if (m_kind == 20 || m_kind == 21) && i == 0 {
                        continue;
                    }
                    ctx.log.out(
                        turn,
                        format!("{at}の陸地は<B>{name}</B>もろとも水没しました。"),
                        Some(id),
                        None,
                    );
                } else {
                    ctx.log.out(
                        turn,
                        format!("{at}の<B>{name}</B>は<B>水没</B>しました。"),
                        Some(id),
                        None,
                    );
                }
                // 中心は海、隣は浅瀬
                set(island, sx, sy, L::Sea, if i == 0 { 0 } else { 1 });
            }
        } else {
            // 2 ヘックス
            if is_one_of(
                kind,
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
                continue;
            }
            let text = if kind == k(L::Monster) {
                format!("{at}の<B>{name}</B>は消し飛びました。")
            } else {
                format!("{at}の<B>{name}</B>は一瞬にして<B>荒地</B>と化しました。")
            };
            ctx.log.out(turn, text, Some(id), None);
            set(island, sx, sy, L::Waste, 0);
        }
    }
}

/// 海底油田: 収入 (ログは doEachHex の最後にまとめて出す) と枯渇
pub(super) fn oil(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let l_name = land_name(h.land_kind, h.lv);
    let value = ctx.config.oil_money + ctx.random(1001);
    island.money += value;
    ctx.globals.hex.oilincome += value;
    if ctx.random(1000) < ctx.config.oil_ratio {
        ctx.log.out(
            ctx.turn,
            oil_end(&island.name, &l_name, &h.point()),
            Some(island.id),
            None,
        );
        set(island, h.x, h.y, L::Sea, 0);
    }
    Flow::Continue
}

/// 浅瀬: 砂浜や氷河ができる (両方当たれば氷河)
pub(super) fn shallow_sea(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if ctx.random(100) < 5 {
        set(island, h.x, h.y, L::Sunahama, 0);
    }
    if ctx.random(100) < 1 {
        set(island, h.x, h.y, L::Ice, 0);
    }
    Flow::Continue
}

/// 砂浜: 浅瀬に戻ることがある
pub(super) fn sunahama(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    if ctx.random(100) < 30 {
        set(&mut islands[idx], h.x, h.y, L::Sea, 1);
    }
    Flow::Continue
}

/// 氷河・天然スケート場: スケート場なら収入、ときどき浅瀬に戻る
pub(super) fn ice(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let lv = cell_value(island, h.x, h.y);
    if lv > 0 {
        let l_name = land_name(h.land_kind, lv);
        let value = lv * 25 + ctx.random(501);
        island.money += value;
        let amount = format!("{value}{}", ctx.config.units.money);
        ctx.log.out(
            ctx.turn,
            oil_money(&island.name, &l_name, &h.point(), &amount),
            Some(island.id),
            None,
        );
    }
    if ctx.random(100) < 10 {
        set(island, h.x, h.y, L::Sea, 1);
    }
    Flow::Continue
}

/// 関所: ときどき関税収入
pub(super) fn seki(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    if ctx.random(1000) < 7 {
        let l_name = land_name(h.land_kind, h.lv);
        let value = ctx.config.oil_money + ctx.random(1001);
        island.money += value;
        let amount = format!("{value}{}", ctx.config.units.money);
        ctx.log.out(
            ctx.turn,
            format!(
                "{}の<B>{l_name}</B>から、<B>{amount}</B>の関税収益が上がりました。",
                msg::island_at(&island.name, &h.point())
            ),
            Some(island.id),
            None,
        );
    }
    Flow::Continue
}

/// 島役所: 条件がそろうと大学 (値 77) になる
pub(super) fn yakusho(
    _ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let sc = &island.scratch;
    if sc.co0 > 0
        && sc.co01 > 0
        && sc.co2 > 0
        && sc.co3 > 0
        && sc.co4 > 0
        && sc.co5 > 0
        && sc.co6 > 0
        && sc.co7 > 0
        && sc.co8 > 0
        && island.eis[6] > 1_000_000
        && island.owner_stats.rena > 10000
        && island.pts > HOUSE_LEVELS[6]
    {
        set(island, h.x, h.y, L::College, 77);
    }
    Flow::Continue
}

/// 金山: 収入と枯渇 (枯渇すると値はそのままで山になる)
pub(super) fn gold(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let lv = cell_value(island, h.x, h.y);
    let l_name = land_name(h.land_kind, lv);
    let value = lv * 25 + ctx.random(501);
    island.money += value;
    let amount = format!("{value}{}", ctx.config.units.money);
    ctx.log.out(
        ctx.turn,
        oil_money(&island.name, &l_name, &h.point(), &amount),
        Some(island.id),
        None,
    );
    if ctx.random(100) < 7 {
        ctx.log.out(
            ctx.turn,
            format!(
                "{}の<B>{l_name}</B>から金が採れなくなったようです。",
                msg::island_at(&island.name, &h.point())
            ),
            Some(island.id),
            None,
        );
        // 値は消さない (Perl 版のまま)
        island.map.get_mut(h.x, h.y).expect("in range").kind = k(L::Mountain);
    }
    Flow::Continue
}

/// 遊園地: 収入 (ログは doEachHex の最後にまとめて出す)、イベント、閉園
pub(super) fn park(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x as i64, h.y as i64);
    let (id, turn) = (island.id, ctx.turn);
    if island.scratch.par <= 5 {
        let nv: i64 = [L::Park, L::Kyujo, L::Kyujokai, L::Umiamu]
            .iter()
            .map(|&l| count_around(&island.map, x, y, l, 7))
            .sum();
        let nx = nv + 10;
        let mut value = trunc(((island.pop / 50) * 3 * nx) as f64 / 10.0);
        if island.scratch.shouhi > island.scratch.ene {
            value = trunc(value as f64 / 10.0);
        }
        if value > 0 {
            island.money += value;
            ctx.globals.hex.parkincome += value;
        }
    }

    // イベント
    if ctx.random(100) < 3 {
        let value = (island.pop / 50) * 10;
        island.food -= value;
        if value > 0 {
            let amount = format!("{value}{}", ctx.config.units.food);
            ctx.log.out(
                turn,
                format!(
                    "{}の<B>{}</B>でイベントが開催され、<B>{amount}</B>の食料が消費されました。",
                    msg::island_at(&island.name, &h.point()),
                    land_name(h.land_kind, h.lv)
                ),
                Some(id),
                None,
            );
        }
    }

    // 老朽化
    if ctx.random(100) < 2 {
        ctx.log.out(
            turn,
            format!(
                "{}の<B>{}</B>は施設が老朽化したため取り壊されました。",
                msg::island_at(&island.name, &h.point()),
                land_name(h.land_kind, h.lv)
            ),
            Some(id),
            None,
        );
        set(island, h.x, h.y, L::Plains, 0);
    }
    Flow::Continue
}

/// `logOilMoney`
pub(super) fn oil_money(name: &str, land_name: &str, point: &str, amount: &str) -> String {
    format!(
        "{}の<B>{land_name}</B>から、<B>{amount}</B>の収益が上がりました。",
        msg::island_at(name, point)
    )
}

/// `logOilEnd`
pub(super) fn oil_end(name: &str, land_name: &str, point: &str) -> String {
    format!(
        "{}の<B>{land_name}</B>は枯渇したようです。",
        msg::island_at(name, point)
    )
}
