//! 成長および単ヘックス災害 (`doEachHex`)。
//!
//! Perl 版は島の全マスを (シャッフルした順に) 1 つずつ見て、地形ごとの巨大な
//! `if/elsif` の連鎖で処理し、そのあと全マス共通の災害 (漏電・小彗星・火災) を判定する。
//! 移植版は地形の系統ごとにファイルを分け、ここで Perl 版と同じ順に振り分ける。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - ループの添字 `$i` を、分岐の中の別のループが使い回している
//!   (`for($i = 1; $i < 7; $i++)` など)。そうした分岐を通ると外側のループの位置が飛ぶ。
//!   移植版は [`HexRun::i`] を共有し、分岐が書き換えられるようにしてある。
//! - ループの中の `$landKind` と `$lv` は分岐が書き換えることがあり、その値で共通の
//!   災害判定をする。マスの地形が変わっていても、判定には書き換え後の `$landKind`/`$lv` を使う。
//!   移植版は [`HexRun::land_kind`] と [`HexRun::lv`] で持つ。
//! - `my` で宣言していない変数 (`$point`, `$kind`, `$aucflag1` など) はグローバル変数で、
//!   別の島・別の処理の値が残っている。移植版は [`HexGlobals`] に持たせる。

mod city;
mod hazards;
mod industry;
mod leisure;
pub(crate) mod monster;
mod sea;
mod special;
mod stadium;
pub(crate) mod town;
mod train;

use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{MatchScope, trunc};
use crate::tables::LandKind as L;

use super::TurnContext;

/// 分岐のあと、ループをどう続けるか
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum Flow {
    /// 共通の災害判定に進む (分岐の終わりまで来た)
    Continue,
    /// Perl の `next`: 共通の災害判定を飛ばして次のマスへ
    Next,
}

/// doEachHex 1 回分 (1 つの島) の状態。Perl 版の doEachHex の `my` 変数に当たる
#[derive(Debug, Default)]
pub struct HexRun {
    /// ループの添字 (`$i`)。分岐が書き換えることがある
    pub i: usize,
    pub x: usize,
    pub y: usize,
    /// `$landKind` (ループの先頭で読んだ地形。分岐が書き換えることがある)
    pub land_kind: u8,
    /// `$lv` (ループの先頭で読んだ地形の値。分岐が書き換えることがある)
    pub lv: i64,
    /// 増える人口のタネ値 (村、町)
    pub addpop: i64,
    /// 増える人口のタネ値 (都市)
    pub addpop2: i64,
    /// 怪獣の移動済みの印 (`@monsterMove`)
    pub monster: monster::RunState,
    /// doEachHex のトップレベルの `$1`.. (冒頭の etc5 のマッチ)。
    /// 分岐はブロックの中なので、正規表現を使うときはこれを `clone()` して使う
    pub scope: MatchScope,
}

impl HexRun {
    /// `"($x, $y)"`
    pub fn point(&self) -> String {
        format!("({}, {})", self.x, self.y)
    }
}

/// doEachHex で使うグローバル変数 (島をまたいで値が残る)
#[derive(Debug, Default)]
pub struct HexGlobals {
    /// `$point`。多くの処理が `my` を付けずに代入していて、ログに前の値が出ることがある
    pub point: String,
    /// `$kind`。怪獣の種類などとして doCommand や動物園が代入する。未定義なら 0
    pub kind: i64,
    /// `$tId`。ログの 2 番目の島 ID に使われる。未定義なら `None`
    pub t_id: Option<i64>,
    /// `$s06b`, `$s08b`, `$s12b` (政策から計算する値)
    pub s06b: i64,
    pub s08b: i64,
    pub s12b: i64,
    /// `$aucflag1`..`3` (ハコオクの出品に使う。最後に処理した島の値が残る)
    pub aucflag: [i64; 3],
    pub zooflag: i64,
    pub seisakuflag: i64,
    pub msseigen: i64,
    pub kougekiseigen: i64,
    pub kougekiseigenm: i64,
    pub oilincome: i64,
    pub parkincome: i64,
    pub rizortincome: i64,
    pub m84income: i64,
    pub gyosenincome: i64,
    /// `$co7`, `$magicf`, `$magici`, `$magica`, `$magicw`, `$magicl`, `$magicd` (`etc9` を分解した先)
    pub etc9: crate::perl::Captures<7>,
    /// 系統ごとのグローバル変数 (各ファイルで定義する)
    pub leisure: leisure::Globals,
    pub stadium: stadium::Globals,
    pub special: special::Globals,
    pub sea: sea::Globals,
    pub monster: monster::Globals,
}

/// 島に一時的に持たせる値のうち、系統ごとのもの
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {
    pub industry: industry::Scratch,
    pub city: city::Scratch,
    pub train: train::Scratch,
    pub leisure: leisure::Scratch,
    pub stadium: stadium::Scratch,
    pub special: special::Scratch,
    pub sea: sea::Scratch,
    pub monster: monster::Scratch,
}

const fn k(l: L) -> u8 {
    l as u8
}

/// `doEachHex($island)`
pub(crate) fn do_each_hex(ctx: &mut TurnContext, islands: &mut [Island], idx: usize) {
    if ctx.config.another_mode {
        let island = &mut islands[idx];
        island.scratch.amarimoney = island.money;
        island.money = 0;
    }

    // doEachHex の $1..。冒頭の etc5 のマッチがそのまま各分岐から見える
    let mut scope = MatchScope::default();
    let s = ctx
        .globals
        .etc5
        .assign(scope.fields(&islands[idx].etc_raw[0]));
    let g = &mut ctx.globals.hex;
    g.s06b = trunc(s[6] as f64 / 5.0);
    g.s08b = trunc(s[8] as f64 / 5.0);
    g.s12b = (trunc(s[12] as f64 / 5.0) + 1).min(10);

    // 不景気
    let s12b = g.s12b;
    let island = &mut islands[idx];
    if ctx.random(20_000_000) + s12b * 1_500_000
        < island.scratch.fukeikimoney - island.scratch.co6 * 100_000
    {
        ctx.log
            .out(ctx.turn, msg::fukeiki(&island.name), Some(island.id), None);
        island.money += 10;
        return;
    }

    let g = &mut ctx.globals.hex;
    g.aucflag = [0; 3];
    g.zooflag = 0;
    g.seisakuflag = 1;
    g.msseigen = 0;
    g.kougekiseigen = 0;
    g.kougekiseigenm = 0;
    g.oilincome = 0;
    g.parkincome = 0;
    g.rizortincome = 0;
    g.m84income = 0;
    g.gyosenincome = 0;
    let sc = &mut island.scratch;
    sc.trainmoney = 0;
    sc.trainmoney2 = 0;
    sc.hcsankaflag = 0;
    sc.roudenflag = 0;
    sc.urikireflag = 0;

    let mut h = HexRun {
        addpop: 10,
        addpop2: 0,
        scope,
        ..Default::default()
    };
    prologue_population(ctx, island, &mut h);

    let n = ctx.config.point_number();
    h.i = 0;
    while h.i < n {
        let Some(&(x, y)) = ctx.points.get(h.i) else {
            break;
        };
        h.x = x;
        h.y = y;
        let cell = islands[idx].map.get(x, y).unwrap_or_default();
        h.land_kind = cell.kind;
        h.lv = cell.value;

        town::pre_chain(ctx, &mut islands[idx], &mut h);

        // 分岐が Perl の `next` をしたら、共通の判定を飛ばして次のマスへ
        if dispatch(ctx, islands, idx, &mut h) == Flow::Continue {
            hazards::post_chain(ctx, islands, idx, &mut h);
        }
        h.i += 1;
    }

    epilogue(ctx, &islands[idx]);
}

/// 人口の増え方を決める (食料不足・誘致活動・腐海の胞子・疫病・副作用)
fn prologue_population(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) {
    let (id, turn) = (island.id, ctx.turn);
    let sc = &island.scratch;
    if island.food < 0 {
        // 食料不足
        h.addpop = -30;
    } else if sc.propaganda == 1 {
        // 誘致活動中
        h.addpop = 30;
        h.addpop2 = 3;
    } else if ctx.rand_f64(1000.0) + ((sc.m73 * 250) as f64) < ((sc.rot * 50) as f64) {
        // 胞子
        if sc.ownfe == 1 {
            ctx.log
                .out(turn, msg::rotsick(&island.name), Some(id), None);
            let pop = island.pop;
            let value = pop * 3 + ctx.random(pop) * 5;
            island.money += value;
            let amount = format!("{value}{}", ctx.config.units.money);
            let urikire = ctx.random(100) < 20;
            if urikire {
                island.scratch.urikireflag = 1;
            }
            ctx.log.out(
                turn,
                msg::miyage2(
                    &island.name,
                    &island.onm,
                    &amount,
                    "腐海の毒消し薬",
                    urikire,
                ),
                Some(id),
                None,
            );
        } else if sc.ownfe > 1 {
        } else {
            ctx.log
                .out(turn, msg::rotsick(&island.name), Some(id), None);
            h.addpop = -10;
        }
    } else if ctx.random(1000) < island.scratch.c21 * 500 {
        // 疫病
        h.addpop = -3;
        island.food -= trunc(island.food as f64 / 2.0);
        ctx.log
            .out(turn, msg::satansick(&island.name), Some(id), None);
    } else if island.scratch.fim > 0 && ctx.random(1000) < 10 {
        // 遺伝子組換え食物の副作用
        h.addpop = -20;
        ctx.log
            .out(turn, msg::starvefood(&island.name), Some(id), None);
    }
}

/// 地形ごとの分岐。Perl 版の `if/elsif` の順番どおり (先に当たったものだけ実行する)
fn dispatch(ctx: &mut TurnContext, islands: &mut [Island], idx: usize, h: &mut HexRun) -> Flow {
    let kind = h.land_kind;
    let is = |l: L| kind == k(l);
    if is(L::Town) || is(L::Minato) || is(L::Seacity) {
        town::town(ctx, &mut islands[idx], h)
    } else if is(L::Plains) {
        town::plains(ctx, &mut islands[idx], h)
    } else if is(L::Farmchi) || is(L::Farmpic) || is(L::Farmcow) {
        industry::livestock(ctx, islands, idx, h)
    } else if is(L::Foodka) {
        industry::foodka(ctx, islands, idx, h)
    } else if is(L::EneBo) {
        industry::ene_bo(ctx, islands, idx, h)
    } else if is(L::EneSo) {
        industry::ene_so(ctx, islands, idx, h)
    } else if is(L::EneAt) {
        industry::ene_at(ctx, islands, idx, h)
    } else if is(L::HTFactory) {
        industry::ht_factory(ctx, islands, idx, h)
    } else if is(L::SHTF) {
        industry::shtf(ctx, islands, idx, h)
    } else if is(L::Forest) {
        industry::forest(ctx, islands, idx, h)
    } else if is(L::Train) {
        train::train(ctx, islands, idx, h)
    } else if is(L::Kura) {
        industry::kura(ctx, islands, idx, h)
    } else if is(L::House) {
        industry::house(ctx, islands, idx, h)
    } else if is(L::Defence) {
        industry::defence(ctx, islands, idx, h)
    } else if is(L::Procity) {
        city::procity(ctx, islands, idx, h)
    } else if is(L::Newtown) {
        city::newtown(ctx, islands, idx, h)
    } else if is(L::Bigtown) {
        city::bigtown(ctx, islands, idx, h)
    } else if is(L::Seatown) {
        city::seatown(ctx, islands, idx, h)
    } else if is(L::Bettown) {
        city::bettown(ctx, islands, idx, h)
    } else if is(L::Skycity) {
        city::skycity(ctx, islands, idx, h)
    } else if is(L::Umicity) {
        city::umicity(ctx, islands, idx, h)
    } else if is(L::Shuto) || is(L::Umishuto) {
        city::shuto(ctx, islands, idx, h)
    } else if is(L::Rizort) {
        leisure::rizort(ctx, islands, idx, h)
    } else if is(L::BigRizort) {
        leisure::big_rizort(ctx, islands, idx, h)
    } else if is(L::Kajino) {
        leisure::kajino(ctx, islands, idx, h)
    } else if is(L::Onsen) {
        city::onsen(ctx, islands, idx, h)
    } else if is(L::Oil) {
        industry::oil(ctx, islands, idx, h)
    } else if is(L::Sea) && h.lv == 1 {
        industry::shallow_sea(ctx, islands, idx, h)
    } else if is(L::Sunahama) {
        industry::sunahama(ctx, islands, idx, h)
    } else if is(L::Ice) {
        industry::ice(ctx, islands, idx, h)
    } else if is(L::Seki) {
        industry::seki(ctx, islands, idx, h)
    } else if is(L::Yakusho) {
        industry::yakusho(ctx, islands, idx, h)
    } else if is(L::Gold) {
        industry::gold(ctx, islands, idx, h)
    } else if is(L::Park) {
        industry::park(ctx, islands, idx, h)
    } else if is(L::Zoo) {
        leisure::zoo(ctx, islands, idx, h)
    } else if is(L::Kyujokai) {
        stadium::kyujokai(ctx, islands, idx, h)
    } else if is(L::Kyujo) {
        leisure::kyujo(ctx, islands, idx, h)
    } else if is(L::Umiamu) {
        leisure::umiamu(ctx, islands, idx, h)
    } else if is(L::RottenSea) && h.lv < 20 {
        leisure::rotten_sea(ctx, islands, idx, h)
    } else if is(L::RottenSea) && h.lv >= 20 {
        leisure::dead_sea(ctx, islands, idx, h)
    } else if is(L::College) {
        special::college(ctx, islands, idx, h)
    } else if is(L::OWNF) {
        special::ownf(ctx, islands, idx, h)
    } else if is(L::Monument) {
        special::monument(ctx, islands, idx, h)
    } else if is(L::Frocity) {
        sea::frocity(ctx, islands, idx, h)
    } else if is(L::Fune) {
        sea::fune(ctx, islands, idx, h)
    } else if is(L::Monster) {
        monster::monster(ctx, islands, idx, h)
    } else {
        Flow::Continue
    }
}

/// ループの後の収益ログ
fn epilogue(ctx: &mut TurnContext, island: &Island) {
    let g = &ctx.globals.hex;
    let sc = &island.scratch;
    let money = &ctx.config.units.money;
    let food = &ctx.config.units.food;
    let mut lines = Vec::new();
    if g.rizortincome > 0 {
        lines.push((format!("{}{money}", g.rizortincome), sc.riz, "リゾート施設"));
    }
    if g.m84income > 0 {
        lines.push((format!("{}{money}", g.m84income), sc.m84, "古代遺跡"));
    }
    if sc.par > 0 {
        lines.push((format!("{}{money}", g.parkincome), sc.par, "遊園地"));
    }
    if sc.oil > 0 {
        lines.push((format!("{}{money}", g.oilincome), sc.oil, "油田"));
    }
    if sc.gyo > 0 {
        lines.push((format!("{}{food}", g.gyosenincome), sc.gyo, "漁船"));
    }
    if sc.trainmoney > 0 {
        lines.push((format!("{}{money}", sc.trainmoney), sc.tra1, "普通電車"));
    }
    if sc.trainmoney2 > 0 {
        lines.push((format!("{}{money}", sc.trainmoney2), sc.tra2, "貨物列車"));
    }
    for (amount, count, what) in lines {
        ctx.log.out(
            ctx.turn,
            msg::park_money(&island.name, &amount, count, what),
            Some(island.id),
            None,
        );
    }
}

/// doEachHex の共通部分で使うログの文面
pub(crate) mod msg {
    use super::{tags, wrap};

    pub fn island(name: &str) -> String {
        wrap(tags::NAME, &format!("{name}島"))
    }

    /// `${HtagName_}${name}島$point${H_tagName}`
    pub fn island_at(name: &str, point: &str) -> String {
        [tags::NAME.0, name, "島", point, tags::NAME.1].concat()
    }

    /// `logFukeiki`
    pub fn fukeiki(name: &str) -> String {
        format!(
            "{}は{}により成長が停滞気味のようです！！",
            island(name),
            wrap(tags::DISASTER, "不景気")
        )
    }

    /// `logRotsick`
    pub fn rotsick(name: &str) -> String {
        format!(
            "{}の<B>腐海</B>が生み出した<B>胞子</B>は{}に{}をもたらしたようです！！",
            island(name),
            island(name),
            wrap(tags::DISASTER, "疫病")
        )
    }

    /// `logMiyage2b` / `logMiyage2c` (`sold_out` なら 2c)
    pub fn miyage2(name: &str, company: &str, amount: &str, item: &str, sold_out: bool) -> String {
        format!(
            "{}の<B>{company}社</B>が所有する<B>{item}</B>は爆発的に売れ、<B>{amount}</B>の経済効果をもたらしました。{}",
            island(name),
            if sold_out {
                "ちなみに薬は売り切れました。"
            } else {
                ""
            }
        )
    }

    /// `logSatansick`
    pub fn satansick(name: &str) -> String {
        format!(
            "<B>魔王サタン</B>は{}の<B>食料</B>を{}させ、{}では{}が流行っているようです！！",
            island(name),
            wrap(tags::DISASTER, "腐敗"),
            island(name),
            wrap(tags::DISASTER, "疫病")
        )
    }

    /// `logStarvefood`
    pub fn starvefood(name: &str) -> String {
        format!(
            "{}の<B>遺伝子組換え食物</B>に{}があったようです！！",
            island(name),
            wrap(tags::DISASTER, "副作用")
        )
    }

    /// `logMonsAttacks`
    pub fn mons_attacks(name: &str, land_name: &str, point: &str) -> String {
        format!(
            "{}の<B>{land_name}</B>は怪獣に{}され被害を受けました。",
            island_at(name, point),
            wrap(tags::DISASTER, "攻撃")
        )
    }

    /// `logParkMoney`
    pub fn park_money(name: &str, amount: &str, count: i64, what: &str) -> String {
        format!(
            "{}の<B>{what}</B>から、<B>合計{amount}</B>の収益が上がりました。",
            wrap(tags::NAME, &format!("{name}島の{count}ヶ所"))
        )
    }
}
