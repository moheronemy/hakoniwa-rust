//! 失業者の移民 (doIslandunemployed、Perl 版 14388〜14569 行) と、リゾートに飽きられた住民の移住 (14635〜14849 行)。

use crate::land::land_name;
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::trunc;
use crate::tables::LandKind as L;
use crate::turn::hex::town::set;
use crate::turn::{TurnContext, random_array};

use super::ProcRun;

/// この段階で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$migrate2` (ログに書く移民の数)。`my` が無いので島やターンの処理をまたいで残る。
    /// 一度も代入されていなければ未定義 (ログには空で入る)
    pub migrate2: Option<i64>,
}

/// この段階で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| kind == l as u8)
}

/// 暴動で壊される施設
const RIOT_TARGETS: [L; 29] = [
    L::Farm,
    L::Factory,
    L::HTFactory,
    L::SHTF,
    L::OWNF,
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
    L::College,
    L::Yakusho,
    L::Base,
    L::Foodim,
    L::Foodka,
    L::Nursery,
    L::Mine,
    L::Park,
    L::Kyujo,
    L::Kyujokai,
    L::Zoo,
    L::Kura,
    L::Kuraf,
    L::Defence,
];

/// 失業者を受け入れる町
const UNEMPLOYED_HOMES: [L; 6] = [
    L::Town,
    L::Minato,
    L::Newtown,
    L::Frocity,
    L::Onsen,
    L::Seacity,
];

/// 失業者が出て行く町 (値が 1 より大きいもの)
const UNEMPLOYED_OLD_HOMES: [L; 14] = [
    L::Town,
    L::Minato,
    L::Procity,
    L::Frocity,
    L::Newtown,
    L::Bigtown,
    L::Bettown,
    L::Skycity,
    L::Umicity,
    L::Seatown,
    L::Shuto,
    L::Umishuto,
    L::Onsen,
    L::Seacity,
];

/// 観光者が帰ってくる町 (リゾート飽きられの 2 つ目の分岐)
const RETURN_HOMES: [L; 10] = [
    L::Town,
    L::Minato,
    L::Procity,
    L::Frocity,
    L::Newtown,
    L::Bigtown,
    L::Bettown,
    L::Seatown,
    L::Onsen,
    L::Seacity,
];

/// `$migrate2` をログに埋め込む形 (未定義なら空)
fn migrate2_str(ctx: &TurnContext) -> String {
    ctx.globals
        .process
        .migrate
        .migrate2
        .map(|v| v.to_string())
        .unwrap_or_default()
}

/// `$n = int(($cap - $lv) / 2); $n = min(int($n + rand($n)), $employed);`
fn fill(ctx: &mut TurnContext, cap: i64, lv: i64, employed: i64) -> i64 {
    let n = trunc((cap - lv) as f64 / 2.0);
    let r = ctx.rand_f64(n as f64);
    trunc(n as f64 + r).min(employed)
}

/// 「今まで住んでいた家を処分する」ループ (値が 1 より大きい `kinds` の値を `employed` まで減らす)
fn vacate(ctx: &TurnContext, island: &mut Island, kinds: &[L], mut employed: i64) {
    for &(x, y) in &ctx.points {
        let Some(cell) = island.map.get(x, y) else {
            continue;
        };
        if is_one_of(cell.kind, kinds) && cell.value > 1 {
            let n = (cell.value - 1).min(employed);
            let c = island.map.get_mut(x, y).expect("in range");
            c.value -= n;
            employed -= n;
            if c.value <= 0 {
                set(island, x, y, L::Plains, 0);
            }
        }
    }
}

/// `doIslandunemployed`: 失業者の移民 (移民先が無ければ暴動かデモ行進)
pub(super) fn unemployed(ctx: &mut TurnContext, islands: &mut [Island], idx: usize) {
    let turn = ctx.turn;
    let (id, name) = (islands[idx].id, islands[idx].name.clone());
    let unit = ctx.config.units.pop.clone();

    // 失業者が１万人以上いると 25% の確率で移民を希望する
    if !(islands[idx].scratch.unemployed >= 100 && ctx.rand_f64(100.0) < 25.0) {
        return;
    }
    let order = random_array(&mut *ctx.rng, ctx.island_number);
    let mut migrate = 0;

    // 移民先を探す (５島まで調べる)
    let n = ctx.island_number.min(5);
    let mut target = None;
    for &t in order.iter().take(n) {
        let Some(t_island) = islands.get(t) else {
            continue;
        };
        // 仕事のある島に移民する
        if t_island.scratch.unemployed < 0 {
            migrate = islands[idx]
                .scratch
                .unemployed
                .min(-t_island.scratch.unemployed);
            ctx.globals.process.migrate.migrate2 = Some(migrate);
            target = Some(t);
            break;
        }
    }

    let Some(t) = target else {
        // 移民先が見つからなければ、暴動かデモ行進。$migrate は使われない
        let _ = ctx.random(islands[idx].scratch.unemployed - 100);
        let mut n = 0;
        let island = &mut islands[idx];
        for &(x, y) in &ctx.points.clone() {
            let Some(cell) = island.map.get(x, y) else {
                continue;
            };
            if is_one_of(cell.kind, &RIOT_TARGETS) {
                // 25% の確率で壊滅
                if ctx.rand_f64(100.0) < 25.0 {
                    n += 1;
                    // logUnemployedRiot。人数は前の島の $migrate2 のことがある (Perl 版のまま)
                    let l_name = land_name(cell.kind, cell.value);
                    let message = format!(
                        "{}で仕事を求める<B>{}{unit}</B>が暴動を起こして{}地点の<B>{l_name}</B>に<B>殺到</B>。<B>{l_name}</B>は壊滅しました。",
                        wrap(tags::NAME, &format!("{name}島")),
                        migrate2_str(ctx),
                        wrap(tags::NAME, &format!("({x}, {y})")),
                    );
                    ctx.log.out(turn, message, Some(id), None);
                    set(island, x, y, L::Waste, 0);
                }
            }
        }
        // 何も壊さないときはデモ行進を行う
        if n == 0 {
            let message = format!(
                "{}で仕事を求める<B>{}{unit}</B>がデモ行進を行いました。",
                wrap(tags::NAME, &format!("{name}島")),
                migrate2_str(ctx),
            );
            ctx.log.out(turn, message, Some(id), None);
        }
        return;
    };

    // 移民先が見つかったので移民
    let (t_id, t_name) = (islands[t].id, islands[t].name.clone());
    // 移民先に関所があれば受け入れを拒否される
    for &(x, y) in &ctx.points {
        let Some(cell) = islands[t].map.get(x, y) else {
            continue;
        };
        if cell.kind == L::Seki as u8 {
            let message = format!(
                "{}から{}へ仕事を求める<B>{}{unit}</B>の移民が到着しましたが、{}の<B>{}</B>は受け入れを拒否したようです。",
                wrap(tags::NAME, &format!("{name}島")),
                wrap(tags::NAME, &format!("{t_name}島")),
                migrate2_str(ctx),
                wrap(tags::NAME, &format!("{t_name}島")),
                land_name(cell.kind, cell.value),
            );
            ctx.log.out(turn, message, Some(id), Some(t_id));
            return;
        }
    }

    // 移民先の町に家を用意する
    let mut employed = migrate;
    for &(x, y) in &ctx.points.clone() {
        let Some(cell) = islands[t].map.get(x, y) else {
            continue;
        };
        if is_one_of(cell.kind, &UNEMPLOYED_HOMES) {
            // 町
            let n = fill(ctx, 255, cell.value, employed);
            employed -= n;
            islands[t].map.get_mut(x, y).expect("in range").value += n;
        } else if cell.kind == L::Plains as u8 {
            // 平地
            let n = fill(ctx, 255, cell.value, employed);
            employed -= n;
            set(&mut islands[t], x, y, L::Town, n);
        }
        if employed <= 0 {
            break;
        }
    }
    migrate -= employed;
    islands[idx].scratch.unemployed -= migrate;
    islands[t].scratch.unemployed += migrate;
    islands[idx].pop -= migrate;
    islands[t].pop += migrate;

    // 今まで住んでいた家を処分する
    vacate(ctx, &mut islands[idx], &UNEMPLOYED_OLD_HOMES, migrate);

    // logUnemployedMigrate
    let message = format!(
        "{}から{}へ仕事を求める<B>{}{unit}</B>の移民が到着しました。{}は快く受け入れたようです。",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::NAME, &format!("{t_name}島")),
        migrate2_str(ctx),
        wrap(tags::NAME, &format!("{t_name}島")),
    );
    ctx.log.out(turn, message, Some(id), Some(t_id));
}

/// リゾート飽きられました: リゾートの観光者がほかの島へ移る (Perl 版 14635〜14849 行)
pub(super) fn resort_fatigue(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    p: &mut ProcRun,
) {
    let s06 = ctx.globals.etc5.0[6];
    let riz = islands[idx].scratch.riz;
    if riz > 0
        && ctx.rand_f64(40.0) > s06 as f64
        && ctx.rand_f64((500 + s06 * 2) as f64) < 15.0
    {
        fatigue_to_resort(ctx, islands, idx, p, s06);
    } else if riz > 0
        && ctx.rand_f64(20.0) > s06 as f64
        && ctx.rand_f64((500 + s06) as f64) < 20.0
    {
        fatigue_to_town(ctx, islands, idx, s06);
    }
}

/// 1 つ目の分岐: 政策の値が同じか上のリゾートのある島へ観光者が移る
fn fatigue_to_resort(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    p: &ProcRun,
    s06: i64,
) {
    let turn = ctx.turn;
    let unit = ctx.config.units.pop.clone();
    let order = random_array(&mut *ctx.rng, ctx.island_number);
    let mut migrate = 0;

    // 移民先を探す (５島まで調べる)
    let n = ctx.island_number.min(5);
    let mut target = None;
    for &t in order.iter().take(n) {
        let Some(t_island) = islands.get(t) else {
            continue;
        };
        // ループの中のマッチ: 失敗すると doIslandProcess のトップレベルの $1.. が入る
        let mut m = p.scope.clone();
        let ts = ctx
            .globals
            .hex
            .leisure
            .ts
            .assign(m.fields(&t_island.etc_raw[0]));
        let ts06 = ts[6];
        // $ts06b = int($ts06/5) はここでは使われない

        let island = &islands[idx];
        if island.pop > t_island.pop
            && t_island.scratch.riz > 0
            && s06 <= ts06
            && island.id != t_island.id
        {
            migrate = (ts06 - s06 + 1) * (ctx.random(5) + 1);
            if migrate <= 0 {
                migrate = 1;
            }
            ctx.globals.process.migrate.migrate2 = Some(migrate);
            target = Some(t);
            break;
        }
    }
    let Some(t) = target else {
        return;
    };

    // 移民先のリゾートに観光者を入れる
    let mut employed = migrate;
    for &(x, y) in &ctx.points.clone() {
        let Some(cell) = islands[t].map.get(x, y) else {
            continue;
        };
        let cap = if cell.kind == L::Rizort as u8 {
            Some(350)
        } else if cell.kind == L::BigRizort as u8 {
            Some(800)
        } else if cell.kind == L::Kajino as u8 {
            Some(2000)
        } else {
            None
        };
        if let Some(cap) = cap {
            let n = fill(ctx, cap, cell.value, employed);
            employed -= n;
            islands[t].map.get_mut(x, y).expect("in range").value += n;
        }
        if employed <= 0 {
            break;
        }
    }
    migrate -= employed;
    islands[idx].pop -= migrate;
    islands[t].pop += migrate;

    // 今まで住んでいた家を処分する (カジノは減らない、Perl 版のまま)
    vacate(ctx, &mut islands[idx], &[L::Rizort, L::BigRizort], migrate);

    // logUnemployedMigrate2
    let message = format!(
        "{}のリゾート施設は魅力不足により、{}へ<B>{}{unit}</B>の観光者が移りました。",
        wrap(tags::NAME, &format!("{}島", islands[idx].name)),
        wrap(tags::NAME, &format!("{}島", islands[t].name)),
        migrate2_str(ctx),
    );
    ctx.log
        .out(turn, message, Some(islands[idx].id), Some(islands[t].id));
}

/// 2 つ目の分岐: 人口の少ない島の町へ観光者が帰る
fn fatigue_to_town(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, s06: i64) {
    let turn = ctx.turn;
    let unit = ctx.config.units.pop.clone();
    let order = random_array(&mut *ctx.rng, ctx.island_number);
    let mut migrate = 0;

    // 移民先を探す (５島まで調べる)
    let n = ctx.island_number.min(5);
    let mut target = None;
    for &t in order.iter().take(n) {
        let Some(t_island) = islands.get(t) else {
            continue;
        };
        let island = &islands[idx];
        if island.pop > t_island.pop && island.id != t_island.id {
            migrate = (25 - s06 + 1) * (ctx.random(3) + 1);
            if migrate <= 0 {
                migrate = 1;
            }
            ctx.globals.process.migrate.migrate2 = Some(migrate);
            target = Some(t);
            break;
        }
    }
    let Some(t) = target else {
        return;
    };
    let (id, name) = (islands[idx].id, islands[idx].name.clone());
    let (t_id, t_name) = (islands[t].id, islands[t].name.clone());

    // 関所があれば (その数だけ) 拒否のログを出し、移る人数を 0 にする
    let mut sekiflag = 0;
    for &(x, y) in &ctx.points {
        let Some(cell) = islands[t].map.get(x, y) else {
            continue;
        };
        if cell.kind == L::Seki as u8 {
            let message = format!(
                "{}に飽きた<B>{}{unit}</B>の観光者は{}へ観光にきました。しかし{}の<B>{}</B>は受け入れを拒否したようです。",
                wrap(tags::NAME, &format!("{name}島")),
                migrate2_str(ctx),
                wrap(tags::NAME, &format!("{t_name}島")),
                wrap(tags::NAME, &format!("{t_name}島")),
                land_name(cell.kind, cell.value),
            );
            ctx.log.out(turn, message, Some(id), Some(t_id));
            sekiflag += 1;
            migrate = 0;
        }
    }

    // 移民先の町に家を用意する。人数が 0 でも 1 マス目は処理する
    // (平地なら値 0 の町になる、Perl 版のまま)
    let mut employed = migrate;
    for &(x, y) in &ctx.points.clone() {
        let Some(cell) = islands[t].map.get(x, y) else {
            continue;
        };
        if is_one_of(cell.kind, &RETURN_HOMES) {
            // 町
            let n = fill(ctx, 2000, cell.value, employed);
            employed -= n;
            islands[t].map.get_mut(x, y).expect("in range").value += n;
        } else if cell.kind == L::Plains as u8 {
            // 平地
            let n = fill(ctx, 255, cell.value, employed);
            employed -= n;
            set(&mut islands[t], x, y, L::Town, n);
        }
        if employed <= 0 {
            break;
        }
    }
    migrate -= employed;
    islands[idx].pop -= migrate;
    islands[t].pop += migrate;

    // 今まで住んでいた家を処分する
    vacate(
        ctx,
        &mut islands[idx],
        &[L::Rizort, L::BigRizort, L::Kajino],
        migrate,
    );

    if sekiflag == 0 {
        // logUnemployedMigrate3
        let message = format!(
            "{}のリゾート施設は魅力不足により、{}へ<B>{}{unit}</B>の観光者が帰ってきました。おかえりなさい。",
            wrap(tags::NAME, &format!("{name}島")),
            wrap(tags::NAME, &format!("{t_name}島")),
            migrate2_str(ctx),
        );
        ctx.log.out(turn, message, Some(id), Some(t_id));
    }
}
