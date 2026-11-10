//! 開発計画の実行 (`doCommand`)。
//!
//! フェーズ 1 で移植したのは、すべての計画に共通する前半 (費用の計算と資金・食料の確認)、
//! 「資金繰り」(連続資金繰り数と自動放棄)、「島の放棄」だけ。
//! それ以外の計画は、費用の確認を通ったら「移植作業中」のログを出して何もしない。

use crate::model::{Island, PlannedCommand};
use crate::tables::{CommandKind as C, HOUSE_LEVELS, LandKind};

use super::TurnContext;
use crate::log::msg;
use crate::perl::{MatchScope, trunc};

/// `slideFront`: 先頭の計画を取り出して詰め、末尾を「資金繰り」で埋める
fn take_first_command(island: &mut Island, command_max: usize) -> PlannedCommand {
    let first = if island.commands.is_empty() {
        PlannedCommand::default()
    } else {
        island.commands.remove(0)
    };
    island
        .commands
        .resize(command_max.saturating_sub(1), PlannedCommand::default());
    island.commands.push(PlannedCommand {
        kind: C::DoNothing as u16,
        ..Default::default()
    });
    first
}

/// 費用の値引き・割増しが効かない計画 (倉庫・輸出・援助など)
fn is_cost_exempt(kind: Option<C>) -> bool {
    matches!(
        kind,
        Some(C::Kura | C::Kura2 | C::Kuraf | C::Sell | C::Money | C::Food | C::Givefood)
    )
}

/// 島の規模による割増し (`$costx`) が効かない計画
fn is_costx_exempt(kind: Option<C>) -> bool {
    is_cost_exempt(kind)
        || matches!(
            kind,
            Some(C::House | C::Bettown | C::Kai | C::Boku2 | C::EneCs | C::EneNF | C::Eisei)
        )
}

/// 計画の費用。正なら資金、負なら食料。
/// Perl 版は途中で小数になることがあるので `f64` で返す
pub(crate) fn command_cost(
    ctx: &mut TurnContext,
    m: &mut MatchScope,
    island: &Island,
    kind_raw: u16,
) -> f64 {
    let kind = C::from_u16(kind_raw);
    let pts = island.pts;
    let mut cost = kind.map_or(0, C::cost) as f64;

    if ctx.config.another_mode {
        match kind {
            Some(C::House | C::Kai) => cost = (pts * 2) as f64,
            Some(C::Boku2) => cost = (pts * 4) as f64,
            _ => {}
        }
    } else {
        match kind {
            Some(C::House) => cost = (pts * 3) as f64,
            Some(C::Bettown | C::Kai) => cost = pts as f64,
            Some(C::Boku2) => cost = (pts * 4) as f64,
            _ => {}
        }
    }

    // 島の規模による割増し
    let costx = {
        let table = [1.0, 1.2, 1.4, 1.4, 1.6, 1.6, 1.8, 1.8, 2.0];
        (0..9)
            .rev()
            .find(|&i| pts > HOUSE_LEVELS[i])
            .map_or(1.0, |i| table[i])
    };
    if !ctx.config.another_mode && !is_costx_exempt(kind) {
        cost *= costx;
    }

    let sc = &island.scratch;
    let exempt = is_cost_exempt(kind);
    // ハイテク企業があれば 2/3、ハイテク企業・改があれば 9/10
    if sc.htf > 0 && !exempt {
        cost = trunc(cost * 2.0 / 3.0) as f64;
    } else if sc.shtf > 0 && !exempt {
        cost = trunc(cost * 9.0 / 10.0) as f64;
    }

    // 大学 95 による値引き。$island->{'co95'} は常に 0 なので実際には働かない (Perl 版のまま)
    let costco95 = 0.975f64.powi(sc.co95 as i32).max(0.9);
    if sc.co95 > 0 && !exempt {
        cost = trunc(cost * costco95) as f64;
    }

    // 政策による値引き
    let s = ctx.globals.etc5.assign(m.fields(&island.etc_raw[0]));
    let costseisaku: i64 = s[1..].iter().sum();
    let costseisaku2 = 0.9975f64.powf(costseisaku as f64).max(0.75);
    if s[0] > 0 && !exempt {
        cost = trunc(cost * costseisaku2) as f64;
    }

    // 資金が多いほど割高 (少なければ 2 割引き)
    let s12b = (trunc(s[12] as f64 / 5.0) + 1).min(10);
    let costmoney = island.money as f64 / 5.0 / (999_999.0 * s12b as f64) + 0.8;
    if !exempt {
        cost = trunc(cost * costmoney) as f64;
    }
    cost
}

/// `doCommand($island)`。計画を 1 つ実行したら `true`、
/// 実行せずに次の計画へ進む (資金不足など) なら `false`
pub(crate) fn do_command(ctx: &mut TurnContext, islands: &mut [Island], idx: usize) -> bool {
    let command_max = ctx.config.command_max;
    let island = &mut islands[idx];
    let command = take_first_command(island, command_max);
    let kind = command.command_kind();
    let com_name = kind.map_or("", C::name);
    let (id, turn) = (island.id, ctx.turn);

    if kind == Some(C::DoNothing) {
        // 資金繰り (logDoNothing は Perl 版でコメントアウトされている)
        island.money += 100;
        island.money += ctx.random(100);
        if ctx.random(100) < 5 {
            let value = 1 + ctx.random(1999);
            island.money += value;
            let amount = format!("{value}{}", ctx.config.units.money);
            ctx.log
                .out(turn, msg::enjo(&island.name, &amount), Some(id), None);
        }
        island.absent += 1;

        // 自動放棄
        if island.absent >= ctx.config.giveup_turn {
            island.commands[0] = PlannedCommand {
                kind: C::Giveup as u16,
                ..Default::default()
            };
        }
        return true;
    }

    island.absent = 0;

    // doCommand の $1.. (turnMain のトップレベルからはマッチの無い状態で呼ばれる)
    let mut m = MatchScope::default();
    let cost = command_cost(ctx, &mut m, island, command.kind);
    let island = &mut islands[idx];

    // 費用の確認
    if cost > 0.0 {
        if (island.money as f64) < cost {
            // 牧場の上に「牧場建設・家畜販売」なら資金が足りなくても実行する
            let land_kind = usize::try_from(command.x)
                .ok()
                .zip(usize::try_from(command.y).ok())
                .and_then(|(x, y)| island.map.get(x, y))
                .and_then(|c| c.land_kind());
            let farm_sale = kind == Some(C::Farmcpc)
                && matches!(
                    land_kind,
                    Some(LandKind::Farmchi | LandKind::Farmpic | LandKind::Farmcow)
                );
            if !farm_sale {
                ctx.log
                    .out(turn, msg::no_money(&island.name, com_name), Some(id), None);
                return false;
            }
        }
    } else if cost < 0.0 && (island.food as f64) < -cost {
        ctx.log
            .out(turn, msg::no_food(&island.name, com_name), Some(id), None);
        return false;
    }

    match kind {
        Some(C::Giveup) => {
            ctx.log.out(turn, msg::giveup(&island.name), Some(id), None);
            ctx.log.history(turn, msg::giveup_history(&island.name));
            island.scratch.dead = true;
            true
        }
        // TODO(フェーズ3): それぞれの計画
        Some(_) => {
            ctx.log.out(
                turn,
                msg::not_ported(&island.name, com_name),
                Some(id),
                None,
            );
            true
        }
        // 計画番号が定義に無いものは、Perl 版でも何もせずに 1 ターン使う
        None => true,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn slide_front_fills_with_do_nothing() {
        let mut island = crate::turn::tests_support::island();
        island.commands = (1..=3)
            .map(|k| PlannedCommand {
                kind: k,
                ..Default::default()
            })
            .collect();
        let first = take_first_command(&mut island, 3);
        assert_eq!(first.kind, 1);
        let kinds: Vec<_> = island.commands.iter().map(|c| c.kind).collect();
        assert_eq!(kinds, [2, 3, C::DoNothing as u16]);
    }
}
