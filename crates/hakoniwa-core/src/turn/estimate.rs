//! 人口・面積などの集計と総合ポイントの計算 (`estimate`)。
//!
//! Perl 版の `estimate` を、処理順と Perl 特有の挙動も含めて移植したもの。
//! Perl 版はコンデンサの充電量 (`$n/2`) が小数になり、ターンの間は地形の値に小数が残る
//! (保存時に `%03x` で切り捨てられる)。移植版は小数部分を `IslandScratch::land_frac` に持つ。
//!
//! 移植版の都合で変えた点:
//! - 複合値が正規表現に一致しないとき (負の数が入っているときなど)、Perl 版は最後に成功した
//!   マッチの `$1`.. を代入する。移植版は [`MatchScope`] で再現する。
//! - 複合値の欄が空 (`"1,,3"`) のとき、Perl 版は空のまま書き戻すが、移植版は 0 を書く。

use crate::model::Island;
use crate::perl::{self, MatchScope, trunc};
use crate::tables::{HOUSE_LEVELS, LandKind as L, MONSTERS};

use super::TurnContext;

/// `monsterSpec`: 怪獣の値から (種類, 名前, 体力) を取り出す
pub fn monster_spec(value: i64) -> (usize, &'static str, i64) {
    let kind = ((value >> 4) & 31) as usize;
    let name = MONSTERS.get(kind).map(|m| m.name).unwrap_or("");
    (kind, name, value & 15)
}

const fn k(l: L) -> u8 {
    l as u8
}

/// 島の値が「総合ポイントのどの段階を超えているか」(`$HouseLevel1`..`9` との比較) を
/// 高い方から調べ、対応する値を返す。どれも超えていなければ `base`
fn by_house_level<T: Copy>(pts: i64, table: [T; 9], base: T) -> T {
    for i in (0..9).rev() {
        if pts > HOUSE_LEVELS[i] {
            return table[i];
        }
    }
    base
}

/// `estimate($number)`
pub(crate) fn estimate(ctx: &mut TurnContext, islands: &mut [Island], idx: usize) {
    // 大使館の判定で他の島の資金を見るので、先に控えておく (estimate 中に他の島の資金は変わらない)
    let money_by_index: Vec<i64> = islands.iter().map(|i| i.money).collect();
    let island_number = ctx.island_number as i64;
    let size = ctx.config.island_size;
    let island = &mut islands[idx];
    let sc = &mut *island.scratch;
    // この estimate 呼び出しの $1.. (turnMain のトップレベルからはマッチの無い状態で呼ばれる)
    let mut m = MatchScope::default();

    let mut s = ctx.globals.etc5.assign(m.fields(&island.etc_raw[0]));

    if sc.fukeikimoney < island.money {
        sc.fukeikimoney = island.money;
    }

    let (mut pop, mut area, mut farm, mut mountain) = (0i64, 0i64, 0i64, 0i64);
    let (mut factory1, mut factory2) = (0i64, 0i64);
    let (mut monslive, mut monslivetype) = (0i64, 0i64);
    let (mut rena, mut fore, mut tare, mut zipro, mut leje) = (0, 0, 0, 0, 0);
    let mut ownfe = 0;
    let mut ene = 0i64;
    // コンデンサの値の小数部分 (Perl 版では ene も小数になる)
    let mut ene_frac = 0.0f64;
    let mut con99 = 0;
    let mut choki2 = 0;
    // 1 マスごとの数え上げ (Perl 版の my($oil) などに対応)
    let mut c = Counts::default();
    // Perl 版はループの後で `$value` (最後に見たマスの値) を使ってしまう箇所がある
    let mut last_value = 0i64;

    let s02 = s[2] as f64;
    let reduce = |v: f64| (100.0 - s02) / 100.0 * v;

    for y in 0..size {
        for x in 0..size {
            let cell = island.map.get(x, y).unwrap_or_default();
            let kind = cell.kind;
            let value = cell.value;
            last_value = value;
            let v = value as f64;
            let (m_kind, _, _) = monster_spec(value);

            let on_sea = [
                L::Sea,
                L::Ice,
                L::Sbase,
                L::Fune,
                L::Frocity,
                L::Umicity,
                L::Nursery,
                L::Umiamu,
                L::Seacity,
                L::Seatown,
                L::Umishuto,
                L::Oil,
            ]
            .iter()
            .any(|&l| kind == k(l));

            if !on_sea {
                area += 1;
                if [L::Town, L::Procity, L::Onsen, L::Shuto, L::Minato]
                    .iter()
                    .any(|&l| kind == k(l))
                {
                    pop += value;
                } else if kind == k(L::Farm) || kind == k(L::Foodim) {
                    farm += value;
                } else if kind == k(L::Foodka) && value > 0 {
                    factory1 += value * 200;
                    farm += value * 200;
                } else if kind == k(L::Farmchi) {
                    tare += value;
                    factory1 += trunc(v / 100.0) + 1;
                } else if kind == k(L::Farmpic) {
                    zipro += value;
                    factory1 += trunc(v / 80.0) + 1;
                } else if kind == k(L::Farmcow) {
                    leje += value;
                    factory1 += trunc(v / 50.0) + 1;
                } else if kind == k(L::Factory) || kind == k(L::HTFactory) || kind == k(L::Park) {
                    factory1 += value;
                } else if kind == k(L::SHTF) {
                    factory2 += value;
                } else if kind == k(L::OWNF) {
                    ownfe = trunc(v / 1000.0);
                    factory2 += trunc(v / 100.0).rem_euclid(10) * 250;
                    factory1 += trunc(value.rem_euclid(100) as f64 / 10.0) * 250;
                    farm += value.rem_euclid(10) * 250;
                } else if kind == k(L::Mountain) || kind == k(L::Gold) {
                    mountain += value;
                } else if kind == k(L::Forest) {
                    fore += value;
                } else if kind == k(L::Newtown) {
                    pop += value;
                    factory1 += trunc(v / 15.0);
                } else if kind == k(L::Bigtown) {
                    pop += value;
                    factory1 += trunc(v / 20.0);
                    farm += trunc(v / 30.0);
                } else if kind == k(L::Bettown) {
                    pop += value;
                } else if kind == k(L::Skycity) {
                    pop += value;
                    factory2 += trunc(v / 60.0);
                    farm += trunc(v / 60.0);
                    sc.shouhi += trunc(reduce(v / 2.0));
                } else if kind == k(L::Rizort) {
                    pop += value;
                } else if kind == k(L::Kajino) {
                    pop += value;
                    sc.shouhi += trunc(reduce(v / 10.0));
                } else if kind == k(L::BigRizort) {
                    pop += value;
                } else if kind == k(L::Base) {
                    c.bas += value;
                    rena += value;
                    sc.shouhi += trunc(reduce(v / 4.0));
                }
            } else if kind == k(L::Nursery) {
                // 養殖場は農場の一種
                farm += value;
            } else if kind == k(L::Umiamu) {
                factory1 += value;
            } else if kind == k(L::Seacity) || kind == k(L::Frocity) {
                pop += value;
            } else if kind == k(L::Umicity) {
                pop += value;
                factory2 += trunc(v / 60.0);
                farm += trunc(v / 60.0);
                sc.shouhi += trunc(reduce(v / 2.0));
            } else if kind == k(L::Umishuto) {
                pop += value;
            } else if kind == k(L::Seatown) {
                pop += value;
                let owork = trunc(v / 40.0);
                factory1 += owork;
                farm += owork;
            } else if kind == k(L::Sbase) {
                c.bas += value;
                rena += value;
                sc.shouhi += trunc(reduce(v / 2.0));
            }

            c.count(kind, value, m_kind);

            // 発電
            if kind == k(L::EneAt) || kind == k(L::EneBo) {
                ene += value;
            }
            if kind == k(L::EneWt) {
                ene += trunc(v * (ctx.random(80) + 70) as f64 / 100.0);
                if sc.typhoon {
                    ene += trunc(v * (ctx.random(80) + 70) as f64 / 100.0);
                }
            }
            if kind == k(L::EneSo) && !sc.typhoon {
                ene += trunc(v * (ctx.random(25) + 75) as f64 / 100.0);
            }
            if kind == k(L::EneWd) {
                ene += trunc(v * (ctx.random(75) + 50) as f64 / 100.0);
                if sc.typhoon {
                    ene += trunc(v * (ctx.random(75) + 50) as f64 / 100.0);
                }
            }
            // 火力発電は油田があれば 2 倍。油田・採掘場の数は前回の estimate の値を見る
            if kind == k(L::EneFw) && sc.oil > 0 {
                ene += value * 2;
            } else if kind == k(L::EneFw) && island.mountain > 0 {
                ene += value;
            }
            if kind == k(L::EneCs) && island.eis[6] > 0 {
                ene += value;
            }
            if kind == k(L::Conden4) && value == 99 {
                con99 += 1;
            }
            if kind == k(L::Conden) || kind == k(L::Conden2) || kind == k(L::Conden3) {
                let frac = sc.land_frac.remove(&(x, y)).unwrap_or(0.0);
                if kind == k(L::Conden3) {
                    ene += value * 2;
                    ene_frac += frac * 2.0;
                } else {
                    ene += value;
                    ene_frac += frac;
                }
                island.map.get_mut(x, y).expect("in range").value = 0;
            }

            if kind == k(L::Monster) {
                monslive += 1;
                monslivetype |= 1i64 << m_kind;
            }

            if kind == k(L::Taishi) {
                // 存在しない ID なら Perl 版は $Hislands[undef] = 先頭の島を見る
                let tn = ctx.id_to_number.get(&value).copied().unwrap_or(0);
                let t_money = money_by_index.get(tn).copied().unwrap_or(0);
                if t_money > island.money {
                    sc.fukeikimoney = t_money;
                }
            }

            if kind == k(L::Kura) {
                choki2 += value.rem_euclid(100);
            }
        }
    }

    if con99 > 0 {
        let mut magicl = c.m79 + c.m100 / 2;
        let mut magica = c.m75 + c.m98 / 2;
        // h10 / h11 は前回の estimate の値
        if sc.h10 > 0 {
            magica += 10;
        }
        if sc.h11 > 0 {
            magicl += 10;
        }
        if magica != magicl {
            ene += ctx.random(magicl * 15000 + 50000);
            ene -= trunc(ctx.random(magicl * 15000 + 50000) as f64 * (50.0 - s02) / 50.0);
        } else {
            ene += magicl * 15000 + 50000 + s[2] * 1000;
        }
    }

    if island.eis[6] >= 1 {
        pop += trunc(island.eis[6] as f64 / 100.0);
    }

    // 代入
    island.pop = pop;
    island.area = area;
    island.farm = farm;
    island.factory = format!(
        "{factory1},{factory2},{},{},{},{},{co95},{co95},{co95},{co95}",
        c.co0,
        c.co1,
        c.htf,
        c.shtf,
        co95 = c.co95
    );
    sc.factory1 = factory1;
    sc.factory2 = factory2;
    sc.factoryt = factory1 + factory2;
    island.mountain = mountain;
    c.store(sc);
    island.etc_num[0] =
        c.tra + trunc(sc.trainmoney as f64 / 1000.0) + trunc(sc.trainmoney2 as f64 / 500.0);
    sc.ownfe = ownfe;

    ene = trunc((ene as f64 + ene_frac) * (1.0 + c.co8 as f64 / 10.0));
    if ene < 0 {
        ene = 0;
    }

    // 電力消費 (前回までの値に積み増す。pts と rena は更新前の値)
    sc.shouhi += trunc(reduce(pop as f64 / 200.0))
        + trunc(reduce(factory1 as f64 / 20.0))
        + trunc(reduce(factory2 as f64 / 10.0));
    sc.shouhi += trunc(reduce(island.pts as f64 / 300.0));
    sc.shouhi += trunc(reduce(island.owner_stats.rena as f64 / 30.0));
    sc.shouhi += trunc(reduce(island.owner_stats.rena as f64 / 30.0));
    sc.sabun = (ene - sc.shouhi) as f64;
    island.eisei_raw[0] = format!("{ene},{s},{s},{ene},{ene}", s = sc.shouhi);
    sc.ene = ene;
    sc.con99 = con99;

    let mut enekeisu = by_house_level(
        island.pts,
        [1.2, 1.45, 1.6, 1.75, 1.9, 2.15, 2.2, 2.35, 2.5],
        1.0,
    );
    if size < 16 {
        enekeisu = 1.0;
    }
    let enepoint = trunc(ene as f64 / (10.0 * enekeisu));

    let mut magicf = c.m78 + c.m96 / 2;
    let mut magici = c.m76 + c.m97 / 2;
    let mut magica = c.m75 + c.m98 / 2;
    let mut magicw = c.m77 + c.m99 / 2;
    let mut magicl = c.m79 + c.m100 / 2;
    let mut magicd = c.m74 + c.m101 / 2;
    if sc.h10 > 0 {
        magicf += 10;
        magici += 10;
        magica += 10;
        magicw += 10;
        magicd += 10;
    }
    if sc.h11 > 0 {
        magicl += 10;
    }
    island.etc_raw[4] = perl::join(&[c.co7, magicf, magici, magica, magicw, magicl, magicd]);

    // 余った電力をコンデンサに充電する
    if sc.sabun > 0.0 {
        for &(x, y) in &ctx.points.clone() {
            let Some(cell) = island.map.get_mut(x, y) else {
                continue;
            };
            // 小数部分も含めた値 (Perl 版の $landValue)
            let lv = cell.value as f64 + sc.land_frac.get(&(x, y)).copied().unwrap_or(0.0);
            // 値を書き込む。小数部分は land_frac に残す
            let mut store = |cell: &mut crate::model::LandCell, v: f64| {
                cell.value = trunc(v);
                let frac = v - v.trunc();
                if frac == 0.0 {
                    sc.land_frac.remove(&(x, y));
                } else {
                    sc.land_frac.insert((x, y), frac);
                }
            };
            if cell.kind == k(L::Conden) && lv < 2000.0 {
                let n = trunc((2000.0 - lv) / 2.0) as f64;
                let n = (n + n).trunc().min(sc.sabun);
                sc.sabun -= n;
                store(cell, lv + n);
                // Perl 版は最後に見たマスの値 ($value) と比べている
                if last_value > 2000 {
                    store(cell, 2000.0);
                }
            }
            if cell.kind == k(L::Conden2) && lv < 4000.0 {
                let n = trunc((4000.0 - lv) / 10.0) as f64;
                let r = ctx.rand_f64(n);
                let n = (n * 9.0 + r).trunc().min(sc.sabun);
                sc.sabun -= n;
                store(cell, lv + n);
                if last_value > 4000 {
                    store(cell, 4000.0);
                }
            }
            if cell.kind == k(L::Conden3) && lv < 7000.0 {
                let n = trunc((7000.0 - lv) / 2.0) as f64;
                let n = (n + n).trunc().min(sc.sabun);
                sc.sabun -= n / 2.0;
                store(cell, lv + n / 2.0);
                if last_value > 7000 {
                    store(cell, 7000.0);
                }
            }
            if sc.sabun <= 0.0 {
                break;
            }
        }
    }

    // 島主の家判定
    if c.hou == 0 {
        island.eisei[0] = 0;
    }

    // 首都判定
    if c.shu == 0 {
        island.totoyoso2 = "555".into();
    } else if perl::int(&island.totoyoso2) == 555 {
        island.totoyoso2 = format!("{}シティー", island.onm);
    }

    // 通算観光者
    if island.eisei[1] < 0 {
        island.eisei[1] = 0;
    }

    let st = ctx.globals.eisei4.assign(m.fields(&island.eisei_raw[1]));
    sc.kachiten = st[3] * 3 + st[4];
    if c.ky2 == 0 {
        island.eisei_raw[1] =
            perl::join(&[st[0], st[1], st[2], 0, 0, 0, st[6], st[7], st[8], st[9], 0]);
    }

    // 政策 (etc5)。先頭は大学 77〜80 の数
    if c.co77 == 0 || perl::num_eq_empty(&island.etc_raw[0]) {
        island.etc_raw[0] = perl::join(&[0; 31]);
    }
    s = ctx.globals.etc5.assign(m.fields(&island.etc_raw[0]));
    let mut etc5 = s;
    etc5[0] = c.co77;
    island.etc_raw[0] = perl::join(&etc5);

    // 動物園 (etc6)
    if c.zoo == 0 {
        island.etc_raw[1] = perl::join(&[0; 31]);
    }
    let z = m.fields::<31>(&island.etc_raw[1]);
    ctx.globals.zoo_estimate_low.copy_from_slice(&z[..10]);
    ctx.globals.zoo[10..].copy_from_slice(&z[10..]);
    // Perl 版は $z0..$z9 (別の処理が最後に代入した値) と $z10..$z30 を足している
    let zookazu: i64 = ctx.globals.zoo.iter().sum();
    let mut etc6 = [0i64; 31];
    etc6[..10].copy_from_slice(&ctx.globals.zoo_estimate_low);
    etc6[10..].copy_from_slice(&ctx.globals.zoo[10..]);
    island.etc_raw[1] = perl::join(&etc6);

    island.monster_live = monslive;
    island.monster_live_type = monslivetype;
    sc.monsterlive2 = monslive + zookazu;

    island.owner_stats.kei = c.kei;
    let ms = ctx.globals.eisei5.assign(m.fields(&island.eisei_raw[2]));
    island.owner_stats.rena = rena + c.co2 * 100 + c.co3 * 500 + ms[5];
    island.owner_stats.fore = fore;
    island.owner_stats.tare = tare;
    island.owner_stats.zipro = zipro;
    island.owner_stats.leje = leje;

    // マスコット判定
    if c.co4 == 0 && c.co99 == 0 && c.c28 == 0 {
        island.eisei_raw[2] = "0,0,0,0,0,0,0".into();
    }
    let ms = ctx.globals.eisei5.assign(m.fields(&island.eisei_raw[2]));
    island.eisei_raw[2] = perl::join(&[ms[0], ms[1], ms[2], ms[3], ms[4], ms[5], c.tet]);

    island.eisei_raw[3] = perl::join(&[
        c.c13, c.shu, c.m26, c.m27, c.m74, c.m75, c.m76, c.m77, c.m78, c.m79, c.m84, c.m93,
    ]);

    // 失業者数
    sc.unemployed = pop - (farm + factory1 + factory2 + mountain) * 10;

    // 人工衛星のポイント
    let eisei_points: i64 = [100, 300, 500, 900, 1500, 2000]
        .iter()
        .zip(&island.eis[..6])
        .map(|(&base, &e)| if e >= 1 { base + e * 2 } else { 0 })
        .sum();

    let toto = ctx.globals.etc8.assign(m.fields(&island.etc_raw[3]));
    island.etc_raw[3] = perl::join(&toto);

    let a4 = ctx.globals.auc4.assign(m.fields(&island.auction.auc4));
    island.auction.auc4 = perl::join(&a4);
    let a0 = ctx.globals.auc0.assign(m.fields(&island.auction.auc0));
    island.auction.auc0 = perl::join(&a0);
    sc.auc0c = a0[2];
    let a5 = ctx.globals.auc5.assign(m.fields(&island.auction.auc5));
    island.auction.auc5 = perl::join(&a5);
    sc.auc5c = a5[2];
    let a6 = ctx.globals.auc6.assign(m.fields(&island.auction.auc6));
    island.auction.auc6 = perl::join(&a6);
    if a6[0] == 1 {
        ctx.oyasumiritu += 1;
    }
    let mut a9 = ctx.globals.auc9.assign(m.fields(&island.auction.auc9));
    let auc9c2 = trunc(a9[2] as f64 / 10000.0);
    a9[1] = c.co95 * 25 + choki2;
    a9[0] = a9[1] + auc9c2 + a9[3] + a9[4];
    ctx.globals.auc9.0 = a9;
    island.auction.auc9 = perl::join(&a9);

    let mut auc0es = (11 - a0[4]) * 500;
    if a0[2] == 0 || auc0es < 0 {
        auc0es = 0;
    }

    if !ctx.config.survey.enabled {
        island.survey_flag = 0;
    }

    s = ctx.globals.etc5.assign(m.fields(&island.etc_raw[0]));
    let s12b = (trunc(s[12] as f64 / 5.0) + 1).min(10);
    let money = island.money as f64;
    let limit = 999_999.0 * s12b as f64;
    let moneypts = if money > limit {
        9999.0 * s12b as f64 + ((money - limit) / 100.0).powf(0.75)
    } else {
        money / 100.0
    };

    // 総合ポイント
    let rena_now = island.owner_stats.rena;
    let pts = pop as f64
        + moneypts
        + island.food as f64 / 100.0
        + (farm * 2 + factory1 + factory2 * 2 + mountain * 2) as f64
        + (c.bas
            + area * 5
            + trunc(fore as f64 / 15.0)
            + c.sci * 30
            + c.pro * 20
            + c.sba * 10
            + c.amu * 10
            + c.oil * 500
            + c.kin * 500
            + c.m26 * 500
            + c.m27 * 500
            + (c.m74 + c.m75 + c.m76 + c.m77 + c.m78 + c.m79) * 750
            + c.m93 * 2000
            + trunc(tare as f64 / 15.0)
            + trunc(zipro as f64 / 12.0)
            + trunc(leje as f64 / 10.0)
            + trunc(rena_now as f64 / 10.0)
            + eisei_points
            + c.hou * 500
            + enepoint
            + c.tra1 * 150
            + c.tra2 * 150
            + auc0es) as f64;
    island.pts = trunc(pts);

    let st = ctx.globals.eisei4.assign(m.fields(&island.eisei_raw[1]));
    sc.kachitent = st[6] * 3 + st[7];
    let siaisu = match st[6] + st[7] + st[8] {
        0 => 1,
        v => v,
    };
    sc.shoritu = trunc(st[6] as f64 / siaisu as f64 * 100.0);
    sc.styusho = st[9];
    sc.teamforce = st[0] + st[1] + st[2];

    let ms = ctx.globals.eisei5.assign(m.fields(&island.eisei_raw[2]));
    sc.force = ms[0] + ms[1] + ms[2] + ms[3];

    let uni = ctx.globals.eisei6.assign(m.fields(&island.eisei_raw[3]));
    sc.uni = uni.iter().filter(|&&u| u != 0).count() as i64;
    sc.tuni = uni.iter().sum();

    island.pts += sc.bumon * 100 * island_number;

    if ctx.config.another_mode {
        island.money += sc.bumon * 100 * island_number + auc0es;
        island.pts = island.money + sc.incomemoney;
    }

    // 島主の家の格付け
    if c.hou > 0 {
        for &(x, y) in &ctx.points.clone() {
            let Some(cell) = island.map.get(x, y) else {
                continue;
            };
            if cell.kind != k(L::House) {
                continue;
            }
            // if ブロックの中のマッチなので、外の $1.. には影響しない
            let mut inner = m.clone();
            let toto = ctx.globals.etc8.assign(inner.fields(&island.etc_raw[3]));
            let pts = island.pts;
            let new_value = if pts > HOUSE_LEVELS[8]
                && c.m75 > 0
                && c.m76 > 0
                && c.m77 > 0
                && c.m78 > 0
                && c.c13 > 0
                && c.shu > 0
                && c.m26 > 0
                && c.m27 > 0
                && c.m84 > 0
                && toto[1] > 0
            {
                // 条件を満たしても、闇石・光石が無ければ値は変わらない
                if c.m74 > 0 || c.m79 > 0 {
                    Some(if c.m74 >= c.m79 { 10 } else { 11 })
                } else {
                    None
                }
            } else {
                Some(by_house_level(pts, [1, 2, 3, 4, 5, 6, 7, 8, 9], 0))
            };
            if let Some(v) = new_value {
                island.map.get_mut(x, y).expect("in range").value = v;
            }
        }
    }

    // 死滅判定 2
    if sc.dead {
        island.pop = 0;
        island.pts = 0;
    } else if island.pop == 0 {
        sc.dead = true;
        island.pts = 0;
    }
}

/// マスごとに数える値 (Perl 版の `$oil++ if (...)` の並び)
#[derive(Default)]
#[cfg_attr(test, derive(Debug, PartialEq))]
struct Counts {
    oil: i64,
    bas: i64,
    htf: i64,
    shtf: i64,
    ownf: i64,
    kei: i64,
    kyu: i64,
    ky2: i64,
    zoo: i64,
    amu: i64,
    par: i64,
    riz: i64,
    fim: i64,
    rot: i64,
    sci: i64,
    sba: i64,
    pro: i64,
    kin: i64,
    nto: i64,
    m17: i64,
    m26: i64,
    m27: i64,
    m73: i64,
    m74: i64,
    m75: i64,
    m76: i64,
    m77: i64,
    m78: i64,
    m79: i64,
    m84: i64,
    m93: i64,
    m96: i64,
    m97: i64,
    m98: i64,
    m99: i64,
    m100: i64,
    m101: i64,
    h10: i64,
    h11: i64,
    sin: i64,
    jin: i64,
    c11: i64,
    c13: i64,
    c21: i64,
    c23: i64,
    c28: i64,
    co0: i64,
    co01: i64,
    co1: i64,
    co2: i64,
    co3: i64,
    co4: i64,
    co5: i64,
    co6: i64,
    co7: i64,
    co8: i64,
    co77: i64,
    co78: i64,
    co79: i64,
    co80: i64,
    co95: i64,
    co99: i64,
    yaku: i64,
    tet: i64,
    hot: i64,
    hou: i64,
    tai: i64,
    shu: i64,
    gyo: i64,
    tra: i64,
    tra1: i64,
    tra2: i64,
}

impl Counts {
    /// 1 マス分を数える。Perl 版はマスごとに約 100 個の `$x++ if (...)` を順に評価する
    /// ([`Counts::count_each`] がそのまま写したもの)。結果は同じなので、地形の種類で分けて
    /// 当てはまるものだけを数える (大きな地図ではターン処理の時間の 1 割ほどになっていた)
    fn count(&mut self, kind: u8, value: i64, m_kind: usize) {
        let Some(l) = L::from_u8(kind) else {
            return;
        };
        match l {
            L::Oil => self.oil += 1,
            L::HTFactory => self.htf += 1,
            L::SHTF => self.shtf += 1,
            L::OWNF => self.ownf += 1,
            L::Monument => {
                self.kei += 1;
                match value {
                    73 => self.m73 += 1,
                    96 => self.m96 += 1,
                    97 => self.m97 += 1,
                    98 => self.m98 += 1,
                    99 => self.m99 += 1,
                    100 => self.m100 += 1,
                    101 => self.m101 += 1,
                    86 => self.m26 += 1,
                    87 => self.m27 += 1,
                    74 => self.m74 += 1,
                    75 => self.m75 += 1,
                    76 => self.m76 += 1,
                    77 => self.m77 += 1,
                    78 => self.m78 += 1,
                    79 => self.m79 += 1,
                    84 => self.m84 += 1,
                    17 => self.m17 += 1,
                    26 => self.sin += 1,
                    27 => self.jin += 1,
                    93 => self.c13 += 1,
                    _ => {}
                }
            }
            L::Kyujo => self.kyu += 1,
            L::Kyujokai => {
                self.kyu += 1;
                self.ky2 += 1;
            }
            L::Zoo => self.zoo += 1,
            L::Umiamu => self.amu += 1,
            L::Park => self.par += 1,
            L::Rizort | L::Kajino => self.riz += 1,
            L::Foodim if value < 480 => self.fim += 1,
            L::RottenSea if value < 20 => self.rot += 1,
            L::Seacity => self.sci += 1,
            // 海底新都市は 2 回数えられる (Perl 版のまま)
            L::Seatown => self.sci += 2,
            L::Sbase => self.sba += 1,
            L::Procity | L::Frocity => self.pro += 1,
            L::Gold => self.kin += 1,
            L::Newtown => self.nto += 1,
            L::House => {
                self.hou += 1;
                if value == 10 {
                    self.m93 += 1;
                    self.h10 += 1;
                }
                if value == 11 {
                    self.m93 += 1;
                    self.h11 += 1;
                }
            }
            L::EneCs => self.m17 += 1,
            L::Monster => match m_kind {
                11 => self.c11 += 1,
                13 => self.c13 += 1,
                21 => self.c21 += 1,
                23 => self.c23 += 1,
                28 => self.c28 += 1,
                30 => {
                    self.c28 += 1;
                    self.tet += 1;
                }
                _ => {}
            },
            L::College => match value {
                0 => self.co0 += 1,
                1 => {
                    self.co1 += 1;
                    self.co01 += 1;
                }
                2 => {
                    self.co2 += 1;
                    self.co1 += 1;
                    self.co0 += 1;
                }
                3 => self.co3 += 1,
                4 | 96 => self.co4 += 1,
                97 | 98 => {
                    self.co4 += 1;
                    self.tet += 1;
                }
                5 => self.co5 += 1,
                6 => self.co6 += 1,
                95 => {
                    self.co6 += 1;
                    self.co95 += 1;
                }
                7 => self.co7 += 1,
                8 => {
                    self.co1 += 1;
                    self.co8 += 1;
                }
                99 => self.co99 += 1,
                77 => self.co77 += 1,
                78 => {
                    self.co77 += 1;
                    self.co78 += 1;
                }
                79 => {
                    self.co77 += 1;
                    self.co79 += 1;
                }
                80 => {
                    self.co77 += 1;
                    self.co80 += 1;
                }
                _ => {}
            },
            L::Yakusho => self.yaku += 1,
            L::Onsen => self.hot += 1,
            L::Taishi => self.tai += 1,
            L::Shuto | L::Umishuto => self.shu += 1,
            L::Fune if matches!(value, 1 | 2 | 5 | 6 | 11) => self.gyo += 1,
            L::Train => {
                self.tra += 1;
                if (10..=19).contains(&value) {
                    self.tra1 += 1;
                }
                if (20..=29).contains(&value) {
                    self.tra2 += 1;
                }
            }
            _ => {}
        }
    }

    /// Perl 版の並びをそのまま写したもの ([`Counts::count`] と同じ結果になることをテストで確かめる)
    #[cfg(test)]
    fn count_each(&mut self, kind: u8, value: i64, m_kind: usize) {
        let is = |l: L| kind == k(l);
        let monument = |v: i64| is(L::Monument) && value == v;
        let college = |v: i64| is(L::College) && value == v;
        let monster = |m: usize| is(L::Monster) && m_kind == m;
        let add = |n: &mut i64, cond: bool| {
            if cond {
                *n += 1;
            }
        };

        add(&mut self.oil, is(L::Oil));
        add(&mut self.htf, is(L::HTFactory));
        add(&mut self.shtf, is(L::SHTF));
        add(&mut self.ownf, is(L::OWNF));
        add(&mut self.kei, is(L::Monument));
        add(&mut self.kyu, is(L::Kyujo));
        add(&mut self.kyu, is(L::Kyujokai));
        add(&mut self.ky2, is(L::Kyujokai));
        add(&mut self.zoo, is(L::Zoo));
        add(&mut self.amu, is(L::Umiamu));
        add(&mut self.par, is(L::Park));
        add(&mut self.riz, is(L::Rizort));
        add(&mut self.riz, is(L::Kajino));
        add(&mut self.fim, is(L::Foodim) && value < 480);
        add(&mut self.rot, is(L::RottenSea) && value < 20);
        add(&mut self.sci, is(L::Seacity));
        // 海底新都市は 2 回数えられる (Perl 版のまま)
        add(&mut self.sci, is(L::Seatown));
        add(&mut self.sci, is(L::Seatown));
        add(&mut self.sba, is(L::Sbase));
        add(&mut self.pro, is(L::Procity));
        add(&mut self.pro, is(L::Frocity));
        add(&mut self.kin, is(L::Gold));
        add(&mut self.nto, is(L::Newtown));
        add(&mut self.m73, monument(73));
        add(&mut self.m96, monument(96));
        add(&mut self.m97, monument(97));
        add(&mut self.m98, monument(98));
        add(&mut self.m99, monument(99));
        add(&mut self.m100, monument(100));
        add(&mut self.m101, monument(101));
        add(&mut self.m26, monument(86));
        add(&mut self.m27, monument(87));
        add(&mut self.m74, monument(74));
        add(&mut self.m75, monument(75));
        add(&mut self.m76, monument(76));
        add(&mut self.m77, monument(77));
        add(&mut self.m78, monument(78));
        add(&mut self.m79, monument(79));
        add(&mut self.m84, monument(84));
        add(&mut self.m93, is(L::House) && value == 10);
        add(&mut self.m93, is(L::House) && value == 11);
        add(&mut self.h10, is(L::House) && value == 10);
        add(&mut self.h11, is(L::House) && value == 11);
        add(&mut self.m17, monument(17));
        add(&mut self.m17, is(L::EneCs));
        add(&mut self.sin, monument(26));
        add(&mut self.jin, monument(27));
        add(&mut self.c11, monster(11));
        add(&mut self.c13, monster(13));
        add(&mut self.c13, monument(93));
        add(&mut self.c21, monster(21));
        add(&mut self.c28, monster(28));
        add(&mut self.c28, monster(30));
        add(&mut self.c23, monster(23));
        add(&mut self.co0, college(0));
        add(&mut self.co1, college(1));
        add(&mut self.co01, college(1));
        add(&mut self.co1, college(8));
        add(&mut self.co2, college(2));
        add(&mut self.co1, college(2));
        add(&mut self.co0, college(2));
        add(&mut self.co3, college(3));
        add(&mut self.co4, college(4));
        add(&mut self.co4, college(98));
        add(&mut self.co4, college(97));
        add(&mut self.co4, college(96));
        add(&mut self.co99, college(99));
        add(&mut self.co5, college(5));
        add(&mut self.co6, college(6));
        add(&mut self.co6, college(95));
        add(&mut self.co95, college(95));
        add(&mut self.co7, college(7));
        add(&mut self.co8, college(8));
        add(&mut self.co77, college(77));
        add(&mut self.co77, college(78));
        add(&mut self.co77, college(79));
        add(&mut self.co77, college(80));
        add(&mut self.co78, college(78));
        add(&mut self.co79, college(79));
        add(&mut self.co80, college(80));
        add(&mut self.yaku, is(L::Yakusho));
        add(&mut self.tet, college(98));
        add(&mut self.tet, college(97));
        add(&mut self.tet, monster(30));
        add(&mut self.hot, is(L::Onsen));
        add(&mut self.hou, is(L::House));
        add(&mut self.tai, is(L::Taishi));
        add(&mut self.shu, is(L::Shuto));
        add(&mut self.shu, is(L::Umishuto));
        add(
            &mut self.gyo,
            is(L::Fune) && matches!(value, 1 | 2 | 5 | 6 | 11),
        );
        add(&mut self.tra, is(L::Train));
        add(&mut self.tra1, is(L::Train) && (10..=19).contains(&value));
        add(&mut self.tra2, is(L::Train) && (20..=29).contains(&value));
    }

    /// 島の一時値に書き込む (Perl 版の「代入」の部分)。
    /// `co95` は Perl 版で島に代入されないので書かない
    fn store(&self, sc: &mut super::IslandScratch) {
        sc.oil = self.oil;
        sc.bas = self.bas;
        sc.kyu = self.kyu;
        sc.ky2 = self.ky2;
        sc.zoo = self.zoo;
        sc.amu = self.amu;
        sc.par = self.par;
        sc.riz = self.riz;
        sc.fim = self.fim;
        sc.rot = self.rot;
        sc.sci = self.sci;
        sc.sba = self.sba;
        sc.pro = self.pro;
        sc.kin = self.kin;
        sc.nto = self.nto;
        sc.m26 = self.m26;
        sc.m27 = self.m27;
        sc.m17 = self.m17;
        sc.c11 = self.c11;
        sc.c13 = self.c13;
        sc.c21 = self.c21;
        sc.c28 = self.c28;
        sc.c23 = self.c23;
        sc.co0 = self.co0;
        sc.co1 = self.co1;
        sc.co01 = self.co01;
        sc.co2 = self.co2;
        sc.co3 = self.co3;
        sc.co4 = self.co4;
        sc.co5 = self.co5;
        sc.co6 = self.co6;
        sc.co7 = self.co7;
        sc.co8 = self.co8;
        sc.co99 = self.co99;
        sc.co77 = self.co77;
        sc.co78 = self.co78;
        sc.co79 = self.co79;
        sc.co80 = self.co80;
        sc.yaku = self.yaku;
        sc.tet = self.tet;
        sc.hot = self.hot;
        sc.hou = self.hou;
        sc.tai = self.tai;
        sc.shu = self.shu;
        sc.sin = self.sin;
        sc.jin = self.jin;
        sc.m96 = self.m96;
        sc.m97 = self.m97;
        sc.m98 = self.m98;
        sc.m99 = self.m99;
        sc.m100 = self.m100;
        sc.m101 = self.m101;
        sc.m74 = self.m74;
        sc.m75 = self.m75;
        sc.m76 = self.m76;
        sc.m77 = self.m77;
        sc.m78 = self.m78;
        sc.m79 = self.m79;
        sc.m84 = self.m84;
        sc.m93 = self.m93;
        sc.m73 = self.m73;
        sc.h10 = self.h10;
        sc.h11 = self.h11;
        sc.gyo = self.gyo;
        sc.htf = self.htf;
        sc.shtf = self.shtf;
        sc.ownf = self.ownf;
        sc.tra = self.tra;
        sc.tra1 = self.tra1;
        sc.tra2 = self.tra2;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn monster_spec_unpacks_value() {
        // 種類 3 (怪獣レッドいのら)、体力 5
        assert_eq!(monster_spec((3 << 4) | 5), (3, "怪獣レッドいのら", 5));
    }

    #[test]
    fn count_by_kind_matches_the_perl_order() {
        // すべての地形の番号 (未知のものも)、値の境目、怪獣の種類の組み合わせ
        let values: Vec<i64> = (-2..=110).chain([479, 480, 481, 4095, 9999]).collect();
        for kind in 0..=u8::MAX {
            for &value in &values {
                for m_kind in 0..=32 {
                    let (mut a, mut b) = (Counts::default(), Counts::default());
                    a.count(kind, value, m_kind);
                    b.count_each(kind, value, m_kind);
                    assert_eq!(a, b, "kind {kind} value {value} monster {m_kind}");
                }
            }
        }
    }

    #[test]
    fn house_level_thresholds() {
        let t = [1, 2, 3, 4, 5, 6, 7, 8, 9];
        assert_eq!(by_house_level(0, t, 0), 0);
        assert_eq!(by_house_level(15000, t, 0), 0);
        assert_eq!(by_house_level(15001, t, 0), 1);
        assert_eq!(by_house_level(55001, t, 0), 9);
    }
}
