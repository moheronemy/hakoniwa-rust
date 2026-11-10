//! 電車 (駅・線路・普通電車・貨物列車)。
//!
//! 線路の値は 0〜9 が線路 (向きや駅) で、普通電車が走っている線路は値 +10 (10〜19)、
//! 貨物列車が走っている線路は値 +20 (20〜29)。電車は乱数で進む方向を選び、
//! 進んだ先が決まった値の線路なら、そのマスに +10 (+20) し、元のマスから -10 (-20) する。
//!
//! Perl 版は値ごとにほぼ同じコードを 20 回書き写している (`hako-turn.cgi` 7257〜8533 行)。
//! 移植版は値ごとの違い (乱数の閾値、進む方向、進める線路の値) を [`ROUTES`] の表にして、
//! 動かす処理を 1 つにまとめた。表は Perl のコードから機械的に抜き出し、表から Perl の
//! コードを作り直して元と一致することを確かめてある。乱数を呼ぶ順番も Perl 版と同じ
//! (`if(random(100) < 33) ... elsif(random(100) < 50) ... else`)。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 進む先が島の外なら `next` で次のマスに行く (このマスの共通の災害判定をしない)。
//! - 値 19 の普通電車の 1 つ目の方向は `$sx = $x + 0` で自分のマスを指していて、
//!   決して進まない (値 29 の貨物列車は `$x + 1` になっている)。
//! - 電力不足 (`shouhi > ene`) のときは、進む先のマスだけを元に戻すので、
//!   電車は消えてしまう (元のマスは -10 / -20 されたまま)。収益と消費電力は加算されたまま。
//! - 進んだ先のマスがこのあとループで回ってくると、同じターンにもう一度動く。

use crate::model::Island;
use crate::tables::LandKind as L;
use crate::turn::TurnContext;

use super::{Flow, HexRun, k, town};

/// この系統で使う Perl 版のグローバル変数 (`$sx`, `$sy` は必ず代入してから使うので持たない)
#[derive(Debug, Default)]
pub struct Globals {}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

/// 行による位置調整のしかた
#[derive(Debug, Clone, Copy)]
enum Adjust {
    /// `if((($sy % 2) == 0) && (($y % 2) == 1)) { $sx--; }`
    Dec,
    /// `if((($sy % 2) == 1) && (($y % 2) == 0)) { $sx++; }`
    Inc,
}

/// 電車が進む 1 方向: `$sx = $x + dx; $sy = $y + dy;`、位置調整、進める線路の値
type Step = (i64, i64, Adjust, &'static [i64]);

/// 進める線路の値 (Perl 版の条件式ごと)
const E: &[i64] = &[0, 1, 2, 3, 6, 8];
const E1: &[i64] = &[1, 2, 3, 6, 8];
const W: &[i64] = &[0, 1, 4, 5, 7, 9];
const W1: &[i64] = &[1, 4, 5, 7, 9];
const NE: &[i64] = &[5, 7, 8];
const SE: &[i64] = &[4, 7];
const NW: &[i64] = &[3, 6, 9];
const SW: &[i64] = &[2, 6];

use Adjust::{Dec, Inc};

/// 値 (の 1 の位) ごとの動き。`(閾値, 方向)`:
/// 方向が 2 つなら `random(100) < 50` で 1 つ目、そうでなければ 2 つ目。
/// 3 つなら `random(100) < 33` で 1 つ目、`random(100) < 50` で 2 つ目、そうでなければ 3 つ目。
/// 普通電車 (10〜19) と貨物列車 (20〜29) で同じ表を使う。ただし値 19 の 1 つ目だけ違う
const ROUTES: [&[Step]; 10] = [
    // 0
    &[(1, 0, Dec, E1), (-1, 0, Dec, W1)],
    // 1
    &[(1, 0, Dec, E), (-1, 0, Dec, W)],
    // 2
    &[(1, -1, Dec, NE), (-1, 0, Dec, W)],
    // 3
    &[(1, 1, Dec, SE), (-1, 0, Dec, W)],
    // 4
    &[(1, 0, Dec, E), (-1, -1, Inc, NW)],
    // 5
    &[(1, 0, Dec, E), (-1, 1, Inc, SW)],
    // 6
    &[(1, -1, Dec, NE), (1, 1, Dec, SE), (-1, 0, Dec, W)],
    // 7
    &[(-1, -1, Inc, NW), (-1, 1, Inc, SW), (1, 0, Dec, E)],
    // 8
    &[(-1, 0, Dec, W), (-1, 1, Inc, SW)],
    // 9 (貨物列車 29)
    &[(1, 0, Dec, E), (1, 1, Dec, SE)],
];

/// 値 19 の普通電車の動き。1 つ目の方向が自分のマスになっていて進めない (Perl 版のまま)
const ROUTE_19: &[Step] = &[(0, 0, Dec, E), (1, 1, Dec, SE)];

/// 電車の種類ごとの値
struct Kind {
    /// マスの値の増減
    step: i64,
    /// 収益
    money: i64,
    /// 消費電力
    shouhi: i64,
    name: &'static str,
}

const PASSENGER: Kind = Kind {
    step: 10,
    money: 1000,
    shouhi: 100,
    name: "普通電車",
};

const FREIGHT: Kind = Kind {
    step: 20,
    money: 500,
    shouhi: 10,
    name: "貨物列車",
};

/// 線路 (`$landKind == $HlandTrain`)
pub(super) fn train(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let lv = h.lv;
    let (kind, route) = match lv {
        19 => (&PASSENGER, ROUTE_19),
        10..=18 => (&PASSENGER, ROUTES[(lv - 10) as usize]),
        20..=29 => (&FREIGHT, ROUTES[(lv - 20) as usize]),
        _ => return Flow::Continue,
    };

    // 方向を選ぶ (乱数を呼ぶ順番は Perl 版の if/elsif どおり)
    let which = if route.len() == 2 {
        if ctx.random(100) < 50 { 0 } else { 1 }
    } else if ctx.random(100) < 33 {
        0
    } else if ctx.random(100) < 50 {
        1
    } else {
        2
    };

    let island = &mut islands[idx];
    let (x, y) = (h.x as i64, h.y as i64);
    let (dx, dy, adjust, allowed) = route[which];
    let mut sx = x + dx;
    let sy = y + dy;
    // 行による位置調整 (Perl の % は負の数でも 0 か 1 になる)
    match adjust {
        Adjust::Dec => {
            if sy.rem_euclid(2) == 0 && y.rem_euclid(2) == 1 {
                sx -= 1;
            }
        }
        Adjust::Inc => {
            if sy.rem_euclid(2) == 1 && y.rem_euclid(2) == 0 {
                sx += 1;
            }
        }
    }
    // 範囲外判定
    let size = ctx.config.island_size as i64;
    if sx < 0 || sx >= size || sy < 0 || sy >= size {
        return Flow::Next;
    }
    let (sxu, syu) = (sx as usize, sy as usize);
    let Some(target) = island.map.get(sxu, syu) else {
        return Flow::Next;
    };
    if target.kind != k(L::Train) || !allowed.contains(&target.value) {
        return Flow::Continue;
    }

    let slv = target.value;
    town::set_value(island, sxu, syu, slv + kind.step);
    let here = island.map.get(h.x, h.y).map_or(0, |c| c.value);
    town::set_value(island, h.x, h.y, here - kind.step);
    island.money += kind.money;
    if kind.step == PASSENGER.step {
        island.scratch.trainmoney += kind.money;
    } else {
        island.scratch.trainmoney2 += kind.money;
    }
    island.scratch.shouhi += kind.shouhi;

    if island.scratch.shouhi > island.scratch.ene {
        // 進む先だけ戻すので電車が消える (Perl 版のまま)
        let v = island.map.get(sxu, syu).map_or(0, |c| c.value);
        town::set_value(island, sxu, syu, v - kind.step);
        let point = format!("({sx}, {sy})");
        ctx.log.out(
            ctx.turn,
            starve3(&island.name, kind.name, &point),
            Some(island.id),
            None,
        );
    }
    Flow::Continue
}

/// `logStarve3`
fn starve3(name: &str, tname: &str, point: &str) -> String {
    format!(
        "{}の<B>{tname}</B>は{}により停止しました！！",
        super::msg::island_at(name, point),
        crate::log::tags::wrap(crate::log::tags::DISASTER, "電力不足")
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    /// 表の方向と進める線路の値が Perl 版の条件式と一致していること (Perl から抜き出した一覧)
    #[test]
    fn routes_match_perl() {
        let expect: [&[(i64, i64, &[i64])]; 10] = [
            &[(1, 0, &[1, 2, 3, 6, 8]), (-1, 0, &[1, 4, 5, 7, 9])],
            &[(1, 0, &[0, 1, 2, 3, 6, 8]), (-1, 0, &[0, 1, 4, 5, 7, 9])],
            &[(1, -1, &[5, 7, 8]), (-1, 0, &[0, 1, 4, 5, 7, 9])],
            &[(1, 1, &[4, 7]), (-1, 0, &[0, 1, 4, 5, 7, 9])],
            &[(1, 0, &[0, 1, 2, 3, 6, 8]), (-1, -1, &[3, 6, 9])],
            &[(1, 0, &[0, 1, 2, 3, 6, 8]), (-1, 1, &[2, 6])],
            &[
                (1, -1, &[5, 7, 8]),
                (1, 1, &[4, 7]),
                (-1, 0, &[0, 1, 4, 5, 7, 9]),
            ],
            &[
                (-1, -1, &[3, 6, 9]),
                (-1, 1, &[2, 6]),
                (1, 0, &[0, 1, 2, 3, 6, 8]),
            ],
            &[(-1, 0, &[0, 1, 4, 5, 7, 9]), (-1, 1, &[2, 6])],
            &[(1, 0, &[0, 1, 2, 3, 6, 8]), (1, 1, &[4, 7])],
        ];
        for (r, e) in ROUTES.iter().zip(expect.iter()) {
            assert_eq!(r.len(), e.len());
            for (s, t) in r.iter().zip(e.iter()) {
                assert_eq!((s.0, s.1, s.3), (t.0, t.1, t.2));
                // 左に動く斜めだけ Inc (Perl 版の位置調整)
                let inc = matches!(s.2, Adjust::Inc);
                assert_eq!(inc, s.0 == -1 && s.1 != 0);
            }
        }
    }
}
