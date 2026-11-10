//! ハコオクの落札処理 (Perl 版 15788〜16957 行)。
//!
//! ターン杯のターン (`$HislandTurn % $HturnPrizeUnit == 0`) か、連続 1 位の賞品を受け取る島
//! (`$auc4b == $aucshouhin`) で動く。出品 3 枠 (`$auction1..3`) のそれぞれについて、
//! この島の入札額 (`auc1..3`) が最高額なら代金を払って品物を受け取る。賞品の島は
//! 3 枠目の処理で、`auc0` に残した品物を受け取る。
//!
//! Perl 版は 3 枠をほぼ同じコードの写しで書いている。違いは
//! - 1 枠目の前だけ `auc6` の待ちターンを減らす
//! - 1・2 枠目は賞品の島では動かない。3 枠目だけが賞品の処理を持つ
//!
//! で、移植版は 1 つの関数 [`lot`] にまとめた。

use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{self, Captures, MatchScope, trunc};
use crate::tables::LandKind as L;
use crate::turn::TurnContext;
use crate::turn::hex::town::set;

use super::ProcRun;

/// この段階で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$tauc6a`, `$tauc6x`, `$tauc6y` (出品した島の `auc6` を分解した先)
    pub tauc6: Captures<3>,
    /// `$dashiname` (出品された地形の説明 = 出品した島の `auc7`)。
    /// 出品した島が見つからなければ前の値のまま
    pub dashiname: String,
}

/// `$auc9c2` (補助金の万の位より上) と `$auc9c3` (補助金を 1 万単位に切り捨てたもの)
struct Subsidy {
    c2: i64,
    c3: i64,
}

pub(super) fn run(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, p: &mut ProcRun) {
    // 15784-15786 行の auc4 の分解 (人工衛星の維持の段階の範囲にある)。
    // そちらで移植されていても、同じ文字列を同じスコープで分解し直すだけなので結果は変わらない
    ctx.globals
        .auc4
        .assign(p.scope.fields(&islands[idx].auction.auc4));
    let auc4b = ctx.globals.auc4.0[1];
    let shouhin = ctx.config.auction_prize_streak;

    let unit = ctx.config.turn_prize_unit;
    // $HturnPrizeUnit が 0 なら Perl 版は 0 除算で止まる
    if !((unit != 0 && ctx.turn % unit == 0) || auc4b == shouhin) {
        return;
    }

    // if ブロックの中の $1..
    let mut m = p.scope.clone();
    ctx.globals.hex.stadium.hcturn = trunc(ctx.turn as f64 / 100.0) * 100;

    let a9 = ctx
        .globals
        .auc9
        .assign(m.fields(&islands[idx].auction.auc9));
    // $auc9c3 は 3 枠を通して計算し直さない (前の枠で補助金を使っても減らない。Perl 版のまま)
    let mut sub = Subsidy {
        c2: trunc(a9[2] as f64 / 10000.0),
        c3: trunc(a9[2] as f64 / 10000.0) * 10000,
    };

    for n in 0..3 {
        lot(ctx, islands, idx, &mut m, &mut sub, n);
    }

    let a = &mut islands[idx].auction;
    a.auc1 = 0;
    a.auc2 = 0;
    a.auc3 = 0;
}

/// 出品 `n` 枠目 (0 始まり) の落札
fn lot(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    m: &mut MatchScope,
    sub: &mut Subsidy,
    n: usize,
) {
    let lot_str = ctx.globals.command.ops.auction[n].clone();
    let caps = ctx.globals.command.ops.auction_caps[n].assign(m.fields(&lot_str));
    let topvalue = caps[3];

    if n == 0 {
        // 待ちターンを減らす
        let mut a6 = ctx
            .globals
            .auc6
            .assign(m.fields(&islands[idx].auction.auc6));
        if a6[0] > 2 {
            a6[0] -= 1;
            ctx.globals.auc6.0 = a6;
            islands[idx].auction.auc6 = perl::join(&a6);
        }
    }

    let auc4b = ctx.globals.auc4.0[1];
    let prize_turn = auc4b == ctx.config.auction_prize_streak;
    let bid = match n {
        0 => islands[idx].auction.auc1,
        1 => islands[idx].auction.auc2,
        _ => islands[idx].auction.auc3,
    };
    // 最高額と同じ額を入れた島はどれも落札する (Perl 版のまま)
    let top_bid = bid == topvalue && topvalue != 0;
    let money = islands[idx].money;

    // 資金が足りない (ちょうど同じ額なら何もしない。Perl 版のまま)
    if top_bid && money + sub.c3 < topvalue * 10000 && !prize_turn {
        islands[idx].auction.auc6 = "7,0,0".into();
    }

    let won = top_bid && money + sub.c3 > topvalue * 10000;
    // 1・2 枠目は賞品の島では落札しない。3 枠目は賞品の島なら必ず受け取る
    let enter = if n == 2 {
        won || prize_turn
    } else {
        won && !prize_turn
    };
    if !enter {
        return;
    }
    // 賞品を受け取る (3 枠目だけ)
    let prize = n == 2 && prize_turn;

    // 落札した if ブロックの中の $1..
    let mut mb = m.clone();
    if prize {
        let mut mp = mb.clone();
        let a0 = ctx
            .globals
            .auc0
            .assign(mp.fields(&islands[idx].auction.auc0));
        let g = &mut ctx.globals.command.ops.auction_caps[n].0;
        g[0] = a0[0];
        g[1] = a0[1];
        ctx.globals.auc4.0[2] += 1;
        ctx.globals
            .auc5
            .assign(mp.fields(&islands[idx].auction.auc5));
    } else {
        pay(ctx, &mut islands[idx], sub, topvalue);
        let shuppin = caps[0];
        if shuppin != 30 {
            let mut mi = mb.clone();
            let mut a6 = ctx
                .globals
                .auc6
                .assign(mi.fields(&islands[idx].auction.auc6));
            a6[0] = 1;
            ctx.globals.auc6.0 = a6;
            islands[idx].auction.auc6 = perl::join(&a6);
        }
        ctx.globals.hex.aucflag[n] += topvalue;
        let a0 = ctx
            .globals
            .auc0
            .assign(mb.fields(&islands[idx].auction.auc0));
        if topvalue > a0[2] {
            let hcturn = ctx.globals.hex.stadium.hcturn;
            islands[idx].auction.auc0 = perl::join(&[caps[0], caps[1], topvalue, hcturn, a0[4]]);
        }
    }

    let [shuppin, avalue, _, _, topid] = ctx.globals.command.ops.auction_caps[n].0;
    let mut ac = item_name(ctx, islands, shuppin, avalue);

    match shuppin {
        6 | 7 | 8 | 19 | 20 | 21 => {
            let island = &islands[idx];
            let zlv: i64 = ctx
                .points
                .iter()
                .filter_map(|&(x, y)| island.map.get(x, y))
                .filter(|c| c.kind == L::Zoo as u8)
                .map(|c| c.value)
                .sum();
            // $z0..$z30 と $z->{...} の両方に代入する
            let mut mz = mb.clone();
            let z = mz.fields::<31>(&island.etc_raw[1]);
            ctx.globals.zoo = z;
            ctx.globals.hex.leisure.z = z;
            let zookazu: i64 = z.iter().sum();
            if zlv > zookazu && island.scratch.zoo > 0 {
                let ack = match shuppin {
                    6 => 13,
                    7 => 22,
                    8 => 14,
                    19 => 17,
                    20 => 21,
                    _ => 23,
                };
                announce(ctx, &mut islands[idx], &ac, topvalue, prize);
                ctx.globals.hex.leisure.z[ack] += 1;
                islands[idx].etc_raw[1] = perl::join(&ctx.globals.hex.leisure.z);
            }
        }
        9 => {
            let mut mi = mb.clone();
            let island = &mut islands[idx];
            let mut t = ctx.globals.etc8.assign(mi.fields(&island.etc_raw[3]));
            t[1] += avalue;
            ctx.globals.etc8.0 = t;
            island.etc_raw[3] = perl::join(&t);
            announce(ctx, island, &ac, topvalue, prize);
        }
        14 => {
            let island = &mut islands[idx];
            for e in &mut island.eis[..6] {
                *e = 200;
            }
            announce(ctx, island, &ac, topvalue, prize);
        }
        15 => {
            let island = &mut islands[idx];
            island.eis[6] = 100099;
            announce(ctx, island, &ac, topvalue, prize);
        }
        22 => {
            let mut mi = mb.clone();
            let island = &mut islands[idx];
            let mut st = ctx.globals.eisei4.assign(mi.fields(&island.eisei_raw[1]));
            for v in &mut st[..3] {
                *v += trunc(*v as f64 * avalue as f64 / 10.0);
            }
            ctx.globals.eisei4.0 = st;
            island.eisei_raw[1] = perl::join(&st);
            announce(ctx, island, &ac, topvalue, prize);
        }
        23 | 24 => {
            let mut mi = mb.clone();
            let island = &mut islands[idx];
            let mut ms = ctx.globals.eisei5.assign(mi.fields(&island.eisei_raw[2]));
            if shuppin == 23 {
                for v in &mut ms[1..4] {
                    *v += trunc(*v as f64 * avalue as f64 / 10.0);
                }
            } else {
                ms[5] += avalue;
            }
            ctx.globals.eisei5.0 = ms;
            island.eisei_raw[2] = perl::join(&ms);
            announce(ctx, island, &ac, topvalue, prize);
        }
        _ => {
            // どこに現れるか決める (最初に見つかった平地・開発予定地)
            let points = ctx.points.clone();
            for (bx, by) in points {
                let Some(cell) = islands[idx].map.get(bx, by) else {
                    continue;
                };
                if cell.kind != L::Plains as u8 && cell.kind != L::Plains2 as u8 {
                    continue;
                }
                let placed = match shuppin {
                    0 | 13 => Some((L::Monument, 74)),
                    1 => Some((L::Monument, 75)),
                    2 => Some((L::Monument, 76)),
                    3 => Some((L::Monument, 77)),
                    4 => Some((L::Monument, 78)),
                    5 => Some((L::Monument, 79)),
                    10 => Some((L::Umiamu, avalue)),
                    11 => Some((L::Foodim, avalue)),
                    12 => Some((L::EneCs, avalue)),
                    16 => Some((L::Conden3, 0)),
                    17 => Some((L::Gold, avalue)),
                    18 => Some((L::Nursery, avalue)),
                    25 => Some((L::Monument, avalue)),
                    26 => Some((L::College, 4)),
                    27 => Some((L::EneWd, avalue)),
                    28 => Some((L::EneBo, avalue)),
                    _ => None,
                };
                if let Some((kind, value)) = placed {
                    set(&mut islands[idx], bx, by, kind, value);
                } else if shuppin == 30 && !prize {
                    let mut mi = mb.clone();
                    move_land(
                        ctx,
                        islands,
                        idx,
                        &mut mi,
                        (bx, by),
                        avalue,
                        topvalue,
                        topid,
                    );
                } else if shuppin == 30 {
                    ac = "なし".into();
                }
                // メッセージ
                announce(ctx, &mut islands[idx], &ac, topvalue, prize);
                break;
            }
        }
    }
}

/// 代金を払う。補助金 (`auc9` の 3 番目) から先に使い、足りない分を資金から払う
fn pay(ctx: &mut TurnContext, island: &mut Island, sub: &mut Subsidy, topvalue: i64) {
    let a9 = &mut ctx.globals.auc9.0;
    let shouhiauc9 = sub.c2 - topvalue;
    if shouhiauc9 < 0 {
        island.money -= (topvalue - sub.c2) * 10000;
        sub.c2 = 0;
        a9[2] = a9[2].rem_euclid(10000);
    } else {
        a9[2] -= topvalue * 10000;
        sub.c2 = trunc(a9[2] as f64 / 10000.0);
    }
    a9[0] = a9[1] + sub.c2 + a9[3] + a9[4];
    island.auction.auc9 = perl::join(a9);
}

/// 落札した地形 (出品 30 番) を、出品した島からこの島の `(bx, by)` に移す
#[allow(clippy::too_many_arguments)]
fn move_land(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    m: &mut MatchScope,
    (bx, by): (usize, usize),
    avalue: i64,
    topvalue: i64,
    topid: i64,
) {
    // %HidToNumber は読み込み時の位置 (Perl 版のまま)
    let Some(tn) = ctx.id_to_number.get(&avalue).copied() else {
        return;
    };
    let Some(t) = islands.get_mut(tn) else {
        return;
    };
    let t_name = t.name.clone();
    let [_, tx, ty] = ctx
        .globals
        .process
        .auction
        .tauc6
        .assign(m.fields(&t.auction.auc6));
    t.auction.auc6 = "0,0,0".into();
    // 範囲外は Perl 版では未定義 (0) を読み、書き込みは保存されない
    let (tx, ty) = (tx as usize, ty as usize);
    let (t_l, t_lv) = t.map.get(tx, ty).map_or((0, 0), |c| (c.kind, c.value));
    let t_lname = crate::land::land_name(t_l, t_lv);
    {
        let st = &mut islands[idx].scratch.command.city;
        st.stocklandkind = i64::from(t_l);
        st.stocklandvalue = t_lv;
    }
    set(&mut islands[tn], tx, ty, L::Plains, 0);
    let island = &mut islands[idx];
    let (sk, sv) = (
        island.scratch.command.city.stocklandkind,
        island.scratch.command.city.stocklandvalue,
    );
    if let Some(c) = island.map.get_mut(bx, by) {
        c.kind = sk as u8;
        c.value = sv;
        island.scratch.land_frac.remove(&(bx, by));
    }

    let t = &mut islands[tn];
    let mut ta = ctx
        .globals
        .hex
        .stadium
        .tauc9
        .assign(m.fields(&t.auction.auc9));
    ta[2] += topvalue * 10000;
    let c2 = trunc(ta[2] as f64 / 10000.0);
    ta[0] = ta[1] + c2 + ta[3] + ta[4];
    ctx.globals.hex.stadium.tauc9.0 = ta;
    t.auction.auc9 = perl::join(&ta);

    islands[idx].auction.auc8 = format!("{t_name}島出品の{t_lname}");

    let aucland = i64::from(t_l) * t_lv;
    ctx.globals.command.ops.aucland = aucland;
    if aucland != topid {
        islands[tn].auction.auc6 = "77,0,0".into();
    }
}

/// 落札・賞品のメッセージ。賞品なら連続 1 位の記録を更新し、殿堂入りを判定する
fn announce(ctx: &mut TurnContext, island: &mut Island, ac: &str, topvalue: i64, prize: bool) {
    let name = wrap(tags::NAME, &format!("{}島様", island.name));
    if !prize {
        // logMonsCome2 ($hcturn も計算し直す)
        let hcturn = trunc(ctx.turn as f64 / 100.0) * 100;
        ctx.globals.hex.stadium.hcturn = hcturn;
        ctx.log.auction(
            ctx.turn,
            format!(
                "{name}、<B>Hakoniwa Auction{hcturn} </B>にて<FONT COLOR=\"MEDIUMSEAGREEN\"><B>{ac}</B></font>を<B>{topvalue}兆円</B>でお買い上げありがとうございます。"
            ),
        );
        return;
    }
    // logPrizeAuc2
    let shouhin = ctx.config.auction_prize_streak;
    ctx.log.auction(
        ctx.turn,
        format!(
            "{name}、<FONT COLOR=\"royalblue\"><B>{shouhin}連続ランキング１位！</B></font>（賞品 <FONT COLOR=\"MEDIUMSEAGREEN\"><B>{ac}</B></font>)"
        ),
    );
    let [auc4a, _, auc4c] = ctx.globals.auc4.0;
    island.auction.auc4 = perl::join(&[auc4a, 0, auc4c]);
    if auc4c >= ctx.config.auction_hall_of_fame {
        let a0 = ctx.globals.auc0.0;
        let a5 = ctx.globals.auc5.0;
        island.auction.auc5 = if a0[2] > a5[2] {
            perl::join(&[a0[0], a0[1], a0[2], a0[3], auc4a])
        } else {
            perl::join(&a5)
        };
        island.auction.auc0 = "0,0,0,0,11".into();
        island.auction.auc4 = "0,0,0".into();
    }
}

/// 品物の名前 (`$ac`)
fn item_name(ctx: &mut TurnContext, islands: &[Island], shuppin: i64, avalue: i64) -> String {
    match shuppin {
        0 | 13 => "闇石".into(),
        1 => "地石".into(),
        2 => "氷石".into(),
        3 => "風石".into(),
        4 => "炎石".into(),
        5 => "光石".into(),
        6 => "天使ミカエル".into(),
        7 => "アイススコーピオン".into(),
        8 => "スライムレジェンド".into(),
        9 => format!("お守り{avalue}個"),
        10 => format!("海あみゅ{}人規模", avalue * 1000),
        11 => format!("食研{}人規模", avalue * 1000),
        12 => format!("コスモ{avalue}万ｋＷ"),
        14 => "衛星６種".into(),
        15 => "宇宙ステーション".into(),
        16 => "黄金のコンデンサ".into(),
        17 => format!("金山{}人規模", avalue * 1000),
        18 => format!("養殖場{}人規模", avalue * 1000),
        19 => "人造怪獣f02".into(),
        20 => "魔王サタン".into(),
        21 => "unknown".into(),
        22 => format!("サッカーチーム力1.{avalue}倍"),
        23 => format!("生物大学能力1.{avalue}倍"),
        24 => format!("生物大学経験値{avalue}"),
        25 => "卵".into(),
        26 => "生物大学".into(),
        27 => format!("風力{avalue}万ｋＷ"),
        28 => format!("バイオマス{avalue}万ｋＷ"),
        29 => "今回はお休み".into(),
        30 => {
            // 出品した島の auc7 (見つからなければ前の値のまま)
            let g = &mut ctx.globals.process.auction;
            for island in islands.iter().take(ctx.island_number) {
                if avalue == island.id {
                    g.dashiname.clone_from(&island.auction.auc7);
                }
            }
            g.dashiname.clone()
        }
        _ => "？".into(),
    }
}
