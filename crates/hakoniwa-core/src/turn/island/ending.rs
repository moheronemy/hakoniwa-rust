//! doIslandProcess の最後 (Perl 版 16958〜17143 行): 政策の値の調整と維持費、
//! 食料・資金のあふれ、大使館への寄付、集計 (`estimate`)、繁栄賞と災難賞。

use crate::log::msg;
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{self, trunc};
use crate::tables::{LandKind as L, PRIZE_NAMES};
use crate::turn::TurnContext;
use crate::turn::estimate::estimate;
use crate::turn::hex::town::set;

use super::ProcRun;

/// この段階で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$kifukin` (寄付金)
    pub kifukin: i64,
    /// `$ttlv` (大使館の値 = 相手の島 ID)
    pub ttlv: i64,
    /// `$anotherkifu`
    pub anotherkifu: i64,
}

/// 大使館のある島へ `kifukin` ずつ寄付する。相手の島が無い大使館は平地になる
fn donate(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, kifukin: i64) {
    ctx.globals.process.ending.kifukin = kifukin;
    let mut kifu = String::new();
    for &(x, y) in &ctx.points.clone() {
        let Some(cell) = islands[idx].map.get(x, y) else {
            continue;
        };
        if cell.kind != L::Taishi as u8 {
            continue;
        }
        ctx.globals.process.ending.ttlv = cell.value;
        match ctx.id_to_number.get(&cell.value).copied() {
            // ターゲットがすでにない
            None => set(&mut islands[idx], x, y, L::Plains, 0),
            // %HidToNumber は読み込み時の位置なので、並べ替えのあとは別の島を指すことがある (Perl 版のまま)
            Some(tn) => {
                if let Some(t) = islands.get_mut(tn) {
                    t.money += kifukin;
                    kifu.push_str(&format!("{}島、", t.name));
                }
            }
        }
    }
    let island = &islands[idx];
    // logKifu
    ctx.log.out(
        ctx.turn,
        format!(
            "{}は持ちきれなかった<B>{kifukin}億円</B>を{}に寄付しました。",
            wrap(tags::NAME, &format!("{}島", island.name)),
            wrap(tags::NAME, &format!("{kifu}大使館"))
        ),
        Some(island.id),
        ctx.globals.hex.t_id,
    );
}

pub(super) fn run(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, p: &mut ProcRun) {
    // 政策の値 ($s00..$s30、最後に分解した値) を調整する
    let mut s = ctx.globals.etc5.0;
    if s[1] > s[2] {
        s[2] += 1;
    }
    if s[2] > s[1] + 10 {
        s[2] -= 2;
    }
    if s[3] > s[4] {
        s[4] += 1;
    }
    if s[4] > s[3] + 5 {
        s[4] -= 3;
    }
    if s[5] > s[6] {
        s[6] += 2;
    }
    if s[6] > s[5] + 15 {
        s[6] -= 1;
    }
    if s[7] > s[8] {
        s[8] += 2;
    }
    if s[8] > s[7] + 20 {
        s[8] -= 1;
    }
    if s[9] > s[10] {
        s[10] += 5;
    }
    if s[10] > s[9] + 50 {
        s[10] -= 1;
    }
    if s[11] > s[12] {
        s[12] += 5;
    }
    if s[12] > s[11] + 1 {
        s[12] -= 5;
    }
    ctx.globals.etc5.0 = s;

    let island = &mut islands[idx];
    // 政策の維持費 (奇数番目の欄の合計 × 1 万)
    let upkeep: i64 = s[1..30].iter().step_by(2).sum();
    island.money -= upkeep * 10000;
    island.etc_raw[0] = perl::join(&s);

    let s12b = (trunc(s[12] as f64 / 5.0) + 1).min(10);
    ctx.globals.hex.s12b = s12b;

    // 食料があふれてたら換金
    let food_cap = 99999 * s12b;
    if island.food > food_cap {
        island.money += trunc((island.food - food_cap) as f64 / 10.0);
        island.food = food_cap;
    }

    // 収入チェック
    island.owner_stats.pika = island.money - island.scratch.old_money;

    // 金があふれてたら切り捨て (大使館があれば寄付する)
    let money_cap = 999_999 * s12b;
    if island.money > money_cap && !ctx.config.another_mode {
        let tai = island.scratch.tai;
        if tai > 0 {
            let kifukin = trunc((island.money - money_cap) as f64 / tai as f64);
            donate(ctx, islands, idx, kifukin);
        }
        islands[idx].money = money_cap;
    }

    ctx.globals.process.ending.anotherkifu = 0;
    let island = &islands[idx];
    if ctx.config.another_mode && island.scratch.amarimoney > 0 && island.scratch.tai > 0 {
        let kifukin = trunc(island.scratch.amarimoney as f64 / island.scratch.tai as f64 / 10.0);
        donate(ctx, islands, idx, kifukin);
        ctx.globals.process.ending.anotherkifu += 1;
    }

    // 各種の値を計算
    estimate(ctx, islands, idx);

    // 繁栄、災難賞
    let island = &mut islands[idx];
    let (id, turn) = (island.id, ctx.turn);
    p.pop = island.pop;
    let pop = p.pop;
    let damage = island.scratch.old_pop - pop;
    let (mut flags, monsters, turns) = split_prize(&island.prize, p);

    island.owner_stats.hamu = island.pop - island.scratch.old_pop;
    island.owner_stats.monta = island.pts - island.scratch.old_pts;

    // 繁栄賞 (人口 30 万, 50 万, 100 万)
    let flag_n = perl::int(&flags);
    let prosperity = [(1, 3000, 1, 3001), (2, 5000, 2, 4001), (4, 10000, 3, 5001)];
    if let Some(&(bit, _, prize, range)) = prosperity
        .iter()
        .find(|&&(bit, border, _, _)| flag_n & bit == 0 && pop >= border)
    {
        flags = (perl::int(&flags) | bit).to_string();
        prize_log(ctx, id, &island.name, PRIZE_NAMES[prize]);
        for (count, building) in [(island.scratch.sin, "神殿"), (island.scratch.jin, "神社")] {
            if count > 0 {
                let value = ctx.random(range);
                island.money += value;
                let amount = format!("{value}{}", ctx.config.units.money);
                ctx.log.out(
                    turn,
                    msg::shrine_money(&island.name, &ctx.globals.hex.point, building, &amount),
                    Some(id),
                    None,
                );
            }
        }
    }

    // 災難賞 (被害 5 万, 10 万, 20 万人)
    let flag_n = perl::int(&flags);
    let disaster = [(64, 500, 7), (128, 1000, 8), (256, 2000, 9)];
    if let Some(&(bit, _, prize)) = disaster
        .iter()
        .find(|&&(bit, border, _)| flag_n & bit == 0 && damage >= border)
    {
        flags = (flag_n | bit).to_string();
        prize_log(ctx, id, &island.name, PRIZE_NAMES[prize]);
    }

    island.prize = format!("{flags},{monsters},{turns}");
}

/// `logPrize`
fn prize_log(ctx: &mut TurnContext, id: i64, name: &str, prize_name: &str) {
    let island = wrap(tags::NAME, &format!("{name}島"));
    ctx.log.out(
        ctx.turn,
        format!("{island}が<B>{prize_name}</B>を受賞しました。"),
        Some(id),
        None,
    );
    ctx.log
        .history(ctx.turn, format!("{island}、<B>{prize_name}</B>を受賞"));
}

/// `$prize =~ /([0-9]*),([0-9]*),(.*)/` (先頭に固定していない)。
/// 一致しなければ最後に成功したマッチの `$1`..`$3` を使う (Perl 版のまま)
fn split_prize(prize: &str, p: &mut ProcRun) -> (String, String, String) {
    let bytes = prize.as_bytes();
    for start in 0..=bytes.len() {
        let digits = |from: usize| {
            from + bytes[from..]
                .iter()
                .take_while(|b| b.is_ascii_digit())
                .count()
        };
        let a_end = digits(start);
        if bytes.get(a_end) != Some(&b',') {
            continue;
        }
        let b_end = digits(a_end + 1);
        if bytes.get(b_end) != Some(&b',') {
            continue;
        }
        let rest = &prize[b_end + 1..];
        // `.` は改行に一致しないので、改行の前まで
        let rest = rest.split('\n').next().unwrap_or("");
        let caps = (
            prize[start..a_end].to_string(),
            prize[a_end + 1..b_end].to_string(),
            rest.to_string(),
        );
        p.scope.set(vec![
            perl::int(&caps.0),
            perl::int(&caps.1),
            perl::int(&caps.2),
        ]);
        return caps;
    }
    let [a, b, c] = p.scope.current::<3>();
    (a.to_string(), b.to_string(), c.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn prize_split_is_unanchored() {
        let mut p = ProcRun::default();
        assert_eq!(
            split_prize("1,2,100,200,", &mut p),
            ("1".into(), "2".into(), "100,200,".into())
        );
        assert_eq!(
            split_prize("0,0,", &mut p),
            ("0".into(), "0".into(), String::new())
        );
        assert_eq!(
            split_prize("x,3,4", &mut p),
            (String::new(), "3".into(), "4".into())
        );
    }
}
