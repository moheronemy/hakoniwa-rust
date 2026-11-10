//! ミサイル (通常・PP・SPP・ST・核・地形隆起弾・陸地破壊弾)、動物派遣、大使派遣。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 防衛施設の判定結果 `@HdefenceHex` は「撃った島の ID と座標」で覚えるグローバル変数で、
//!   ターンの間ずっと残る (別の島を狙っても同じ座標なら前の判定を使う)。
//! - 不発弾の判定に使う `$alltotal` (撃ったミサイルの数) はターンの間ずっと増え続ける。
//! - 地形隆起弾が海底基地などに当たると、目標の島ではなく**撃った島**の同じ座標を浅瀬にする。
//!   浅瀬に当たると、着弾点ではなく**計画の座標**のまわりの海を浅瀬にする
//!   (未定義の `$seaCount` を見ているので必ずそうなる)。
//! - 魔方陣 (記念碑 25) から怪獣が出ると、doCommand の `$kind` (計画番号) が怪獣の種類で
//!   上書きされ、以後の弾は「その他のミサイル」として扱われる。
//! - 結果のログの `$tLname` と `$tPoint` は未定義のグローバル変数なので空になる。
//! - 大使派遣のログの 2 番目の島 ID はグローバル変数 `$tId` (目標の島ではない)。
//! - 大使派遣の予定地が島の外なら、Perl 版は `next` で doCommand を抜ける
//!   (turnMain の `while (doCommand(...) == 0)` の次の繰り返しになる) ので、0 を返したのと同じ。

use std::collections::HashMap;

use crate::land::{around, count_around, in_island, land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{self, Captures, MatchScope, trunc};
use crate::tables::{
    BASE_LEVEL_UP, CommandKind as C, LandKind as L, MAX_BASE_LEVEL, MAX_SBASE_LEVEL, MONSTERS,
    PRIZE_NAMES, SBASE_LEVEL_UP,
};
use crate::turn::hex::monster::{hardened, m as mm};
use crate::turn::hex::town::{set, set_value};
use crate::turn::{TurnContext, monster_spec};

use super::{CmdRun, cmsg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$msjotai`, `$nokotan`, `$msid` (`etc7` を分解した先)。
    /// 人工衛星攻撃・レーザーの計画と島ごとの処理 (Perl 版 14585 行) も同じ変数に代入する
    pub ms: Captures<3>,
    /// `$alltotal`: このターンに撃ったミサイルの数 (不発弾の判定に使う)。一度も 0 に戻らない
    pub alltotal: i64,
    /// `@HdefenceHex`: (撃った島の ID, x, y) → 1 (防衛される) / -1 (されない) / 0 (未判定)
    pub defence_hex: HashMap<(i64, usize, usize), i64>,
    /// `$z0t`..`$z30t` (動物派遣の相手の島の `etc6`)
    pub zoo_t: Captures<31>,
    /// `$zt->{'0'}`..`$zt->{'30'}` (`$z0t`.. とは別の変数)
    pub zt: [i64; 31],
    /// `$mshpt`, `$msapt`, ... (動物派遣の相手の島の `eisei5`)
    pub eisei5_t: Captures<7>,
    /// `$tradeexe`
    pub tradeexe: i64,
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {
    /// `$island->{'monstersend'}`: 送り込まれた怪獣の数 (doIslandProcess が怪獣を出す)
    pub monstersend: i64,
    /// `$island->{'monstersendkind'}`: 送り込まれた怪獣の種類
    pub monstersendkind: i64,
}

const fn k(l: L) -> u8 {
    l as u8
}

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| kind == k(l))
}

fn kind_at(island: &Island, x: usize, y: usize) -> u8 {
    island.map.get(x, y).map_or(0, |c| c.kind)
}

fn value_at(island: &Island, x: usize, y: usize) -> i64 {
    island.map.get(x, y).map_or(0, |c| c.value)
}

/// `expToLevel($kind, $exp)`: 基地の経験値からレベルを求める
pub(crate) fn exp_to_level(kind: u8, exp: i64) -> i64 {
    if kind == k(L::Base) {
        // ミサイル基地
        (2..=MAX_BASE_LEVEL)
            .rev()
            .find(|&i| exp >= BASE_LEVEL_UP[(i - 2) as usize])
            .unwrap_or(1)
    } else {
        // 海底基地
        (2..=MAX_SBASE_LEVEL)
            .rev()
            .find(|&i| exp >= SBASE_LEVEL_UP[(i - 2) as usize])
            .unwrap_or(1)
    }
}

/// `$prize =~ /([0-9]*),([0-9]*),(.*)/` の `($1, $2, $3)`。
/// 先頭に固定しないので、最初にマッチした位置より前は捨てられる。
/// マッチしなければ Perl 版は直前に成功したマッチの値を使う
fn prize_parts(prize: &str, scope: &MatchScope) -> (String, String, String) {
    let digits = |t: &str| t.bytes().take_while(u8::is_ascii_digit).count();
    for p in 0..=prize.len() {
        if !prize.is_char_boundary(p) {
            continue;
        }
        let rest = &prize[p..];
        let d1 = digits(rest);
        if rest.as_bytes().get(d1) != Some(&b',') {
            continue;
        }
        let rest2 = &rest[d1 + 1..];
        let d2 = digits(rest2);
        if rest2.as_bytes().get(d2) != Some(&b',') {
            continue;
        }
        // `.` は改行に当たらない
        let turns = rest2[d2 + 1..].split('\n').next().unwrap_or("");
        return (rest[..d1].into(), rest2[..d2].into(), turns.into());
    }
    let [a, b, c] = scope.current::<3>();
    (a.to_string(), b.to_string(), c.to_string())
}

/// ログの文面
mod t {
    use super::{tags, wrap};

    fn n(s: &str) -> String {
        wrap(tags::NAME, s)
    }

    fn island(name: &str) -> String {
        n(&format!("{name}島"))
    }

    fn com(s: &str) -> String {
        wrap(tags::COM_NAME, s)
    }

    /// `logNiwaren2`
    pub fn niwaren2(name: &str, com_name: &str) -> String {
        format!(
            "{}の{}は、{}を支払うはめになりました。",
            island(name),
            com(com_name),
            wrap(tags::DISASTER, "賠償金")
        )
    }

    /// `logNiwaren3`
    pub fn niwaren3(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、<B>援助射撃の許可が取れてない</B>ため中止されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logEiseiEnd`
    pub fn eisei_end(name: &str, eisei: &str) -> String {
        format!(
            "{}の<B>{eisei}</B>は{}したようです！！",
            island(name),
            wrap(tags::DISASTER, "崩壊")
        )
    }

    /// `logMsLRSbase`
    pub fn lr_sbase(l: &str, tp: &str) -> String {
        format!(
            "{}に着水後爆発、同地点にあった<B>{l}</B>は隆起して浅瀬になりました。",
            n(tp)
        )
    }

    /// `logMsLRSeaRotten`
    pub fn lr_sea_rotten(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に着弾。腐海は隆起し山になりました。", n(tp))
    }

    /// `logMsLRSea1`
    pub fn lr_sea1(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に着弾。隆起し荒地となりました。", n(tp))
    }

    /// `logMsLRMonster`
    pub fn lr_monster(l: &str, tp: &str) -> String {
        format!(
            "{}に着弾し爆発。陸地は<B>{l}</B>もろとも隆起し山が出来ました。",
            n(tp)
        )
    }

    /// `logMsLRLand`
    pub fn lr_land(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に着弾。隆起し山が出来ました。", n(tp))
    }

    /// `logMsSS`
    pub fn ss(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に着弾し大爆発しました。", n(tp))
    }

    /// `logMsLDMountain`
    pub fn ld_mountain(l: &str, tp: &str) -> String {
        format!(
            "{}の<B>{l}</B>に命中。<B>{l}</B>は消し飛び、荒地と化しました。",
            n(tp)
        )
    }

    /// `logMsLDSbase`
    pub fn ld_sbase(l: &str, tp: &str) -> String {
        format!(
            "{}に着水後爆発、同地点にあった<B>{l}</B>は跡形もなく吹き飛びました。",
            n(tp)
        )
    }

    /// `logMsLDMonster`
    pub fn ld_monster(l: &str, tp: &str) -> String {
        format!(
            "{}に着弾し爆発。陸地は<B>{l}</B>もろとも水没しました。",
            n(tp)
        )
    }

    /// `logMsLDSeaRotten`
    pub fn ld_sea_rotten(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に着弾。腐海は海に沈みました。", n(tp))
    }

    /// `logMsLDSea1`
    pub fn ld_sea1(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に着弾。海底がえぐられました。", n(tp))
    }

    /// `logMsLDLand`
    pub fn ld_land(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に着弾。陸地は水没しました。", n(tp))
    }

    /// `logMsNormalRotten` (と `logMsNormalSRotten` の機密ログ)
    pub fn normal_rotten(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に命中、腐海は焼き払われました。", n(tp))
    }

    /// `logMsNormalSRotten` の遅延ログ。`$` が抜けていて `{HtagName_}` がそのまま出る (Perl 版のまま)
    pub fn normal_rotten_late(l: &str, tp: &str) -> String {
        format!(
            "{{HtagName_}}{tp}{}の<B>{l}</B>に命中、腐海は焼き払われました。",
            tags::NAME.1
        )
    }

    /// `logMsMonKill` (と `logMsMonKillS`)
    pub fn mon_kill(l: &str, tp: &str) -> String {
        format!(
            "{}の<B>{l}</B>に命中。<B>{l}</B>は力尽き、倒れました。",
            n(tp)
        )
    }

    /// `logSinMoney` / `logJinMoney`。`$point` はグローバル変数
    pub fn shrine_money(name: &str, point: &str, building: &str, amount: &str) -> String {
        format!(
            "{}の<B>{building}</B>で祝いの祭りが行われ、<B>{amount}</B>の収益が上がりました。",
            n(&format!("{name}島{point}"))
        )
    }

    /// `logMsNormal` (と `logMsNormalS`)
    pub fn normal(l: &str, tp: &str) -> String {
        format!("{}の<B>{l}</B>に命中、一帯が壊滅しました。", n(tp))
    }

    /// `logMonsComemagic`
    pub fn mons_comemagic(name: &str, m_name: &str) -> String {
        format!(
            "{}の破壊された<B>魔方陣</B>から<B>{m_name}</B>出現！！",
            island(name)
        )
    }

    /// 結果の数 (無効, 防衛, 怪獣相殺, 怪獣命中, 不発弾)
    pub struct Counts {
        pub total: i64,
        pub mukou: i64,
        pub bouei: i64,
        pub kaijumukou: i64,
        pub kaijuhit: i64,
        pub fuhatu: i64,
    }

    fn total_body(t_name: &str, point: &str, com_name: &str, turn: i64, c: &Counts) -> String {
        format!(
            "{}地点に向けて{}を行いました。<br>{}：{}⇒(無効{}発/防衛{}発/怪獣相殺{}発/怪獣命中{}発",
            n(&format!("{t_name}島{point}")),
            com(&format!("{}発の{com_name}", c.total)),
            wrap(tags::NUMBER, &format!("ターン{turn}")),
            n("結果"),
            c.mukou,
            c.bouei,
            c.kaijumukou,
            c.kaijuhit
        )
    }

    /// `logMsTotal` (と `logMsTotalS` の機密ログ)
    pub fn total(
        name: &str,
        t_name: &str,
        point: &str,
        com_name: &str,
        turn: i64,
        c: &Counts,
    ) -> String {
        format!(
            "{}が{}/不発弾{}発)",
            island(name),
            total_body(t_name, point, com_name, turn, c),
            c.fuhatu
        )
    }

    /// `logMsTotalS` の遅延ログ (不発弾の数は出さない)
    pub fn total_late(t_name: &str, point: &str, com_name: &str, turn: i64, c: &Counts) -> String {
        format!(
            "<B>何者か</B>が{})",
            total_body(t_name, point, com_name, turn, c)
        )
    }

    /// `logMsNoBase`
    pub fn no_base(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、<B>ミサイル設備を保有していない</B>ために実行できませんでした。",
            island(name),
            com(com_name)
        )
    }

    /// `logMsBoatPeople`
    pub fn boat_people(name: &str, achive: i64, unit: &str) -> String {
        format!(
            "{}にどこからともなく<B>{achive}{unit}もの難民</B>が漂着しました。{}は快く受け入れたようです。",
            island(name),
            island(name)
        )
    }

    /// `logPrize` (通常ログ)
    pub fn prize(name: &str, p_name: &str) -> String {
        format!("{}が<B>{p_name}</B>を受賞しました。", island(name))
    }

    /// `logPrize` (記録ログ)
    pub fn prize_history(name: &str, p_name: &str) -> String {
        format!("{}、<B>{p_name}</B>を受賞", island(name))
    }

    /// `logMonsSend2`
    pub fn mons_send2(name: &str, t_name: &str, m_name: &str) -> String {
        format!(
            "{}の<B>{m_name}</B>は、{}へ派遣されました。",
            island(name),
            island(t_name)
        )
    }

    /// `logNoMoney2`
    pub fn no_money2(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、条件不足のため中止されました。",
            island(name),
            com(com_name)
        )
    }

    /// `logMonsSend`
    pub fn mons_send(name: &str, t_name: &str, m_name: &str) -> String {
        format!(
            "{}が<B>{m_name}</B>を脱走させ、{}へ送りこみました。",
            island(name),
            island(t_name)
        )
    }

    /// `logTaishi`
    pub fn taishi(name: &str, t_name: &str, com_name: &str, point: &str) -> String {
        format!(
            "{}が{}地点に向けて{}を行いました。",
            island(name),
            n(&format!("{t_name}島{point}")),
            com(com_name)
        )
    }
}

/// 着弾しても効果の無い地形 (地形隆起弾以外。陸地破壊弾は深い海だけ)
const NO_EFFECT: [L; 8] = [
    L::Sea,
    L::Sbase,
    L::Seacity,
    L::Seatown,
    L::Umishuto,
    L::Umiamu,
    L::Gold,
    L::Mountain,
];

/// 地形隆起弾で (撃った島の同じ座標が) 浅瀬になる海の施設
const LR_SBASE: [L; 8] = [
    L::Sbase,
    L::Seacity,
    L::Umishuto,
    L::Seatown,
    L::Oil,
    L::Fune,
    L::Frocity,
    L::Umiamu,
];

/// 陸地破壊弾で「跡形もなく吹き飛ぶ」海の施設
const LD_SBASE: [L; 7] = [
    L::Sbase,
    L::Fune,
    L::Frocity,
    L::Umiamu,
    L::Seatown,
    L::Umishuto,
    L::Seacity,
];

/// 陸地破壊弾のあと浅瀬ではなく海になる地形
const LD_TO_DEEP: [L; 10] = [
    L::Oil,
    L::Sea,
    L::Ice,
    L::Seacity,
    L::Seatown,
    L::Umishuto,
    L::Fune,
    L::Frocity,
    L::Umiamu,
    L::Sbase,
];

/// 経験値と難民の元になる町
const EXP_TOWNS: [L; 4] = [L::Town, L::Minato, L::Newtown, L::Bigtown];

/// 核の周囲で何も起きない地形 (`wideDamageli`)
const WIDE_LI_SAFE: [L; 11] = [
    L::Sea,
    L::Oil,
    L::Waste,
    L::Ice,
    L::Seacity,
    L::Seatown,
    L::Umishuto,
    L::Fune,
    L::Frocity,
    L::Umiamu,
    L::Sbase,
];

/// `wideDamageli`: 核の着弾点のまわり 2 ヘックスを荒地にする (ログは目標の島)
fn wide_damage_li(ctx: &mut TurnContext, t_island: &mut Island, target: i64, tx: i64, ty: i64) {
    for i in 0..19 {
        let (sx, sy) = around(tx, ty, i);
        // 範囲を確かめる前に読む
        let (kind, lv) = perl_get(&t_island.map, sx, sy);
        let l_name = land_name(kind, lv);
        let p = format!("({sx}, {sy})");
        let Some((sx, sy)) = in_island(&t_island.map, (sx, sy)) else {
            continue;
        };
        if is_one_of(kind, &WIDE_LI_SAFE) {
            continue;
        }
        let message = if kind == k(L::Monster) {
            mm::wide_damage_monster(&t_island.name, &l_name, &p)
        } else {
            mm::wide_damage_waste(&t_island.name, &l_name, &p)
        };
        ctx.log.out(ctx.turn, message, Some(target), None);
        set(t_island, sx, sy, L::Waste, 0);
    }
}

/// 基地の経験値を足す (まだ基地のときだけ)。`boat` があれば難民も足す
fn add_exp(ctx: &TurnContext, island: &mut Island, bx: usize, by: usize, exp: i64) -> bool {
    if is_one_of(kind_at(island, bx, by), &[L::Base, L::Sbase]) {
        let v = (value_at(island, bx, by) + exp).min(ctx.config.max_exp_point);
        set_value(island, bx, by, v);
        true
    } else {
        false
    }
}

/// ミサイル 1 発分の状態 (doCommand の `my` 変数と、結果を数えるグローバル変数)
struct Salvo {
    counts: t::Counts,
    /// 難民の数 (`$boat`)
    boat: i64,
    bx: usize,
    by: usize,
    t_name: String,
    /// ミサイルの分岐の中の `$1`.. (etc7 のマッチ)
    scope: MatchScope,
}

/// ミサイル系
pub(super) fn missile(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let (id, turn) = (islands[idx].id, ctx.turn);
    let name = islands[idx].name.clone();
    // ターゲット取得
    let Some(&tn) = ctx.id_to_number.get(&c.target) else {
        // ターゲットがすでにない
        ctx.log
            .out(turn, cmsg::ms_no_target(&name, c.com_name), Some(id), None);
        return false;
    };

    {
        let sc = &islands[idx].scratch;
        if sc.shouhi > sc.ene {
            ctx.log
                .out(turn, cmsg::ms_no_ene(&name, c.com_name), Some(id), None);
            return false;
        }
    }

    let mut flag = false;
    if c.arg == 0 {
        // 0の場合は撃てるだけ
        c.arg = 100;
    }

    let t_name = islands[tn].name.clone();
    let t_id = islands[tn].id;

    // ミサイルの分岐の中の $1.. (etc7 のマッチ)
    let mut scope = c.scope.clone();
    let [msjotai, _, msid] = ctx
        .globals
        .command
        .attack
        .ms
        .assign(scope.fields(&islands[idx].etc_raw[2]));

    // 自島に目標の島の大使館があれば同盟
    let doumei = ctx.points.iter().any(|&(dx, dy)| {
        kind_at(&islands[idx], dx, dy) == k(L::Taishi) && value_at(&islands[idx], dx, dy) == t_id
    });

    if ctx.config.love_peace {
        let other = id != t_id;
        if msjotai == 2 && t_id == msid {
        } else if doumei && other {
        } else if islands[tn].monster_live == 0 && islands[tn].scratch.rot == 0 && other {
            islands[idx].money = 0;
            ctx.log
                .out(turn, t::niwaren2(&name, c.com_name), Some(id), None);
            return false;
        } else if c.kind != C::MissileSPP as u16 && other {
            ctx.log
                .out(turn, t::niwaren3(&name, c.com_name), Some(id), None);
            return false;
        }
    }

    // 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
    let guard = ctx.config.guard_pop;
    if (islands[idx].pop < guard || islands[tn].pop < guard) && islands[tn].scratch.rot == 0 {
        ctx.log
            .out(turn, cmsg::forbidden(&name, c.com_name), Some(id), None);
        return false;
    }

    // 誤差
    let err = match C::from_u16(c.kind) {
        Some(C::MissilePP | C::MissileSS) => 7,
        Some(C::MissileSPP) => 1,
        _ => 19,
    };

    // $mukou などはグローバル変数だが、ほかでは使わないので局所変数で持つ
    let mut s = Salvo {
        counts: t::Counts {
            total: 0,
            mukou: 0,
            bouei: 0,
            kaijumukou: 0,
            kaijuhit: 0,
            fuhatu: 0,
        },
        boat: 0,
        bx: 0,
        by: 0,
        t_name,
        scope,
    };
    let cost = c.cost as i64;
    let n = ctx.points.len();

    // 金が尽きるか指定数に足りるか基地全部が撃つまでループ
    let mut count = 0;
    while c.arg > 0 && islands[idx].money as f64 >= c.cost {
        // 基地を見つけるまでループ
        while count < n {
            (s.bx, s.by) = ctx.points[count];
            if is_one_of(kind_at(&islands[idx], s.bx, s.by), &[L::Base, L::Sbase]) {
                break;
            }
            count += 1;
        }
        if count >= n {
            // 見つからなかったらそこまで
            break;
        }

        // 最低一つ基地があったので、flagを立てる
        flag = true;

        // 基地のレベルを算出
        let mut level = exp_to_level(
            kind_at(&islands[idx], s.bx, s.by),
            value_at(&islands[idx], s.bx, s.by),
        );
        // 基地内でループ
        while level > 0 && c.arg > 0 && islands[idx].money as f64 > c.cost {
            let rena = islands[idx].owner_stats.rena;
            let g = &ctx.globals.command.attack;
            let limit = g.alltotal - trunc(rena as f64 / 100.0);
            if ctx.rand_f64(300.0) < limit as f64 {
                // 不発弾
                level -= 1;
                c.arg -= 1;
                islands[idx].money -= cost;
                s.counts.total += 1;
                ctx.globals.command.attack.alltotal += 1;
                s.counts.fuhatu += 1;
            }
            // 撃ったのが確定なので、各値を消耗させる
            level -= 1;
            c.arg -= 1;
            islands[idx].money -= cost;
            s.counts.total += 1;
            ctx.globals.command.attack.alltotal += 1;
            shoot(ctx, islands, idx, tn, c, &mut s, err);
        }

        // カウント増やしとく
        count += 1;
    }

    // ログ ($tLname と $tPoint は未定義のグローバル変数なので空になる)
    if c.kind == C::MissileST as u16 {
        let msg = t::total(&name, &s.t_name, &c.point, c.com_name, turn, &s.counts);
        ctx.log.secret(turn, msg, Some(id), Some(c.target));
        let msg = t::total_late(&s.t_name, &c.point, c.com_name, turn, &s.counts);
        ctx.log.late(turn, msg, Some(id), Some(c.target));
    } else {
        let msg = t::total(&name, &s.t_name, &c.point, c.com_name, turn, &s.counts);
        ctx.log.out(turn, msg, Some(id), Some(c.target));
    }

    if !flag {
        // 基地が一つも無かった場合
        ctx.log
            .out(turn, t::no_base(&name, c.com_name), Some(id), None);
        return false;
    }

    // 難民判定
    let mut boat = s.boat / 2;
    if boat > 0 && id != c.target && c.kind != C::MissileST as u16 {
        // 難民漂着
        let island = &mut islands[idx];
        let mut achive = 0;
        for &(bx, by) in ctx.points.iter() {
            if boat <= 0 {
                break;
            }
            let kind = kind_at(island, bx, by);
            if kind == k(L::Town) {
                // 町の場合
                let mut lv = value_at(island, bx, by);
                if boat > 50 {
                    lv += 50;
                    boat -= 50;
                    achive += 50;
                } else {
                    lv += boat;
                    achive += boat;
                    boat = 0;
                }
                if lv > 200 {
                    boat += lv - 200;
                    achive -= lv - 200;
                    lv = 200;
                }
                set_value(island, bx, by, lv);
            } else if kind == k(L::Plains) {
                // 平地の場合 (残りが 5 人以下なら値は平地のまま)
                let lv = value_at(island, bx, by);
                set(island, bx, by, L::Town, lv);
                if boat > 10 {
                    set_value(island, bx, by, 5);
                    boat -= 10;
                    achive += 10;
                } else if boat > 5 {
                    set_value(island, bx, by, boat - 5);
                    achive += boat;
                    boat = 0;
                }
            }
            if boat <= 0 {
                break;
            }
        }
        if achive > 0 {
            // 少しでも到着した場合、ログを吐く
            let unit = ctx.config.units.pop.clone();
            ctx.log.out(
                turn,
                t::boat_people(&island.name, achive, &unit),
                Some(id),
                None,
            );

            // 難民の数が一定数以上なら、平和賞の可能性あり
            if achive >= 200 {
                let (flags_s, monsters, turns) = prize_parts(&island.prize, &s.scope);
                let mut flags = perl::int(&flags_s);
                let mut won = None;
                if flags & 8 == 0 && achive >= 200 {
                    flags |= 8;
                    won = Some(PRIZE_NAMES[4]);
                } else if flags & 16 == 0 && achive > 500 {
                    flags |= 16;
                    won = Some(PRIZE_NAMES[5]);
                } else if flags & 32 == 0 && achive > 800 {
                    flags |= 32;
                    won = Some(PRIZE_NAMES[6]);
                }
                let flags_s = match won {
                    Some(p_name) => {
                        ctx.log
                            .out(turn, t::prize(&island.name, p_name), Some(id), None);
                        ctx.log
                            .history(turn, t::prize_history(&island.name, p_name));
                        flags.to_string()
                    }
                    None => flags_s,
                };
                island.prize = format!("{flags_s},{monsters},{turns}");
            }
        }
    }
    true
}

/// 1 発分の着弾処理 (Perl 版の内側の while の本体のうち、撃った後の部分)。
/// `return` は Perl 版の `next`
fn shoot(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    tn: usize,
    c: &mut CmdRun,
    s: &mut Salvo,
    err: i64,
) {
    let id = islands[idx].id;
    let turn = ctx.turn;
    let target = c.target;
    let size = ctx.config.island_size as i64;
    let kind = c.kind;
    let is = |cmd: C| kind == cmd as u16;

    // 着弾点算出
    let r = ctx.random(err);
    let (tx, ty) = around(c.x, c.y, r as usize);

    // 着弾点範囲内外チェック
    if tx < 0 || tx >= size || ty < 0 || ty >= size {
        // 範囲外
        s.counts.mukou += 1;
        return;
    }
    let (tx, ty) = (tx as usize, ty as usize);

    // 着弾点の地形等算出
    let t_l = kind_at(&islands[tn], tx, ty);
    let t_lv = value_at(&islands[tn], tx, ty);
    let t_lname = land_name(t_l, t_lv);
    let t_point = format!("({tx}, {ty})");

    // 防衛施設判定
    let mut defence = is(C::MissileSPP);
    let hex = ctx
        .globals
        .command
        .attack
        .defence_hex
        .get(&(id, tx, ty))
        .copied()
        .unwrap_or(0);
    if hex == 1 {
        defence = true;
    } else if hex == -1 {
        defence = false;
    } else {
        let t_map = &islands[tn].map;
        let sabun = islands[idx].scratch.sabun;
        let (txi, tyi) = (tx as i64, ty as i64);
        let near = |l: L, range: usize| count_around(t_map, txi, tyi, l, range) > 0;
        let dh = &mut ctx.globals.command.attack.defence_hex;
        if t_l == k(L::Defence) || (t_l == k(L::Procity) && t_lv < 160) {
            // 防衛施設に命中。フラグをクリア
            for i in 0..19 {
                let (sx, sy) = around(txi, tyi, i);
                if let Some((sx, sy)) = in_island(t_map, (sx, sy)) {
                    dh.insert((id, sx, sy), 0);
                }
            }
        } else if (near(L::Defence, 19) && sabun > 0.0)
            || (near(L::Procity, 7) && sabun > 0.0)
            || (near(L::House, 1) && sabun > 0.0)
            || (near(L::Shuto, 7) && sabun > 0.0)
        {
            dh.insert((id, tx, ty), 1);
            defence = true;
        } else {
            dh.insert((id, tx, ty), -1);
            defence = false;
        }
    }

    if defence {
        // 空中爆破
        s.counts.bouei += 1;
        return;
    }

    if islands[tn].eis[4] >= 1 && ctx.random(5000) < islands[tn].owner_stats.rena {
        // 防衛衛星
        islands[tn].eis[4] -= 2;
        if islands[tn].eis[4] < 1 {
            islands[tn].eis[4] = 0;
            // 崩壊のログは撃った島の名前で出る (Perl 版のまま)
            let msg = t::eisei_end(&islands[idx].name, "防衛衛星");
            ctx.log.out(turn, msg, Some(id), None);
        }
        s.counts.bouei += 1;
        return;
    }

    if islands[tn].scratch.c23 >= 1 {
        s.counts.kaijumukou += 1;
        return;
    }

    if islands[tn].scratch.h10 >= 1 && id != islands[tn].id {
        s.counts.bouei += 1;
        return;
    }

    // 「効果なし」hexを最初に判定
    if !is(C::MissileLR)
        && ((t_l == k(L::Sea) && t_lv == 0)
            || (is_one_of(t_l, &NO_EFFECT) && !is(C::MissileLD)))
    {
        s.counts.mukou += 1;
        return;
    }

    let log_t = |ctx: &mut TurnContext, msg: String| {
        ctx.log.out(ctx.turn, msg, Some(id), Some(target));
    };

    // 弾の種類で分岐
    if is(C::MissileLR) {
        if is_one_of(t_l, &[L::Mountain, L::Gold]) {
            // 山に着弾した場合無効
            s.counts.mukou += 1;
            return;
        }
        if is_one_of(t_l, &LR_SBASE) {
            // 撃った島の同じ座標を浅瀬にしてしまう (Perl 版のまま)
            set(&mut islands[idx], tx, ty, L::Sea, 1);
            log_t(ctx, t::lr_sbase(&t_lname, &t_point));
            return;
        } else if t_l == k(L::RottenSea) {
            // 撃った島の同じ座標を山にしてしまう (Perl 版のまま)
            set(&mut islands[idx], tx, ty, L::Mountain, 0);
            log_t(ctx, t::lr_sea_rotten(&t_lname, &t_point));
            return;
        } else if is_one_of(t_l, &[L::Sea, L::Ice]) {
            if t_lv == 1 {
                // 浅瀬の場合
                set(&mut islands[tn], tx, ty, L::Waste, 0);
                log_t(ctx, t::lr_sea1(&t_lname, &t_point));
                islands[tn].area += 1;

                // $seaCount は未定義 (0) なので、必ず周りの海を浅瀬にする。
                // しかも着弾点ではなく計画の座標のまわり (Perl 版のまま)
                for i in 1..7 {
                    if let Some((sx, sy)) = in_island(&islands[tn].map, around(c.x, c.y, i)) {
                        if kind_at(&islands[tn], sx, sy) == k(L::Sea) {
                            set_value(&mut islands[tn], sx, sy, 1);
                        }
                    }
                }
            } else {
                // 海なら、目的の場所を浅瀬にする
                set(&mut islands[tn], tx, ty, L::Sea, 1);
                log_t(ctx, t::lr_sbase(&t_lname, &t_point));
            }
            return;
        } else if t_l == k(L::Monster) {
            log_t(ctx, t::lr_monster(&t_lname, &t_point));
            // 山になる
            set(&mut islands[tn], tx, ty, L::Mountain, 0);
            return;
        }

        log_t(ctx, t::lr_land(&t_lname, &t_point));
        // 山になる
        set(&mut islands[tn], tx, ty, L::Mountain, 0);
        if ctx.rand_f64(1000.0) < 22.0 {
            set(&mut islands[tn], tx, ty, L::Monument, 75);
        }
        // (この後の経験値の処理は next の後にあり、実行されない)
        return;
    } else if is(C::MissileSS) {
        log_t(ctx, t::ss(&t_lname, &t_point));
        wide_damage_li(ctx, &mut islands[tn], target, tx as i64, ty as i64);
        return;
    } else if is(C::MissileLD) {
        // 陸地破壊弾
        if is_one_of(t_l, &[L::Mountain, L::Onsen, L::Gold]) {
            // 山(荒地になる)
            log_t(ctx, t::ld_mountain(&t_lname, &t_point));
            set(&mut islands[tn], tx, ty, L::Waste, 0);
            return;
        } else if is_one_of(t_l, &LD_SBASE) {
            // 海底基地 海底都市
            log_t(ctx, t::ld_sbase(&t_lname, &t_point));
        } else if t_l == k(L::Monster) {
            log_t(ctx, t::ld_monster(&t_lname, &t_point));
        } else if t_l == k(L::RottenSea) {
            log_t(ctx, t::ld_sea_rotten(&t_lname, &t_point));
        } else if is_one_of(t_l, &[L::Sea, L::Ice]) {
            // 浅瀬
            log_t(ctx, t::ld_sea1(&t_lname, &t_point));
        } else {
            // その他
            log_t(ctx, t::ld_land(&t_lname, &t_point));
        }

        // 経験値
        if is_one_of(t_l, &EXP_TOWNS) {
            add_exp(ctx, &mut islands[idx], s.bx, s.by, t_lv / 20);
        }

        // 浅瀬になる
        set(&mut islands[tn], tx, ty, L::Sea, 1);
        islands[tn].area -= 1;

        // でも油田、浅瀬、海底基地だったら海
        if is_one_of(t_l, &LD_TO_DEEP) {
            set_value(&mut islands[tn], tx, ty, 0);
        }
        return;
    }

    // その他ミサイル
    let stealth = is(C::MissileST);
    if t_l == k(L::Waste) {
        // 荒地(被害なし)。ただし続けて荒地にし直す
        s.counts.mukou += 1;
    } else if t_l == k(L::RottenSea) {
        if stealth {
            let msg = t::normal_rotten(&t_lname, &t_point);
            ctx.log.secret(turn, msg, Some(id), Some(target));
            let msg = t::normal_rotten_late(&t_lname, &t_point);
            ctx.log.late(turn, msg, Some(target), None);
        } else {
            log_t(ctx, t::normal_rotten(&t_lname, &t_point));
        }
    } else if t_l == k(L::Monster) {
        // 怪獣
        let (m_kind, m_name, m_hp) = monster_spec(t_lv);
        let spec = MONSTERS.get(m_kind).copied();
        let special = spec.map_or(0, |m| m.special);

        // 硬化中?
        if hardened(special, turn) {
            s.counts.kaijumukou += 1;
            return;
        }
        let bonus = islands[idx].scratch.co4 * 100 + islands[idx].scratch.co99 * 100;
        let defence = ctx.config.monster.defence;
        let roll = |ctx: &mut TurnContext| ctx.random(1000) + bonus;
        // 叩き落された (Perl 版の条件の順番と短絡評価のとおりに乱数を使う)
        let blocked = (special == 5 && roll(ctx) < defence)
            || (m_kind == 15 && roll(ctx) < defence)
            || (m_kind == 13 && roll(ctx) < 900)
            || (m_kind == 20 && roll(ctx) < 800)
            || (m_kind == 21 && roll(ctx) < 700)
            || (m_kind == 22 && roll(ctx) < 750)
            || (m_kind == 18 && {
                let a = roll(ctx);
                a < 600 + ctx.random(400)
            })
            || (m_kind == 30 && {
                let a = roll(ctx);
                a < 950 + ctx.random(50)
            })
            || (m_kind == 19 && {
                let a = roll(ctx);
                a < 666 + ctx.random(400)
            })
            || (m_kind == 14 && roll(ctx) < 400)
            || (m_kind == 17 && {
                let a = roll(ctx);
                a < 400 + ctx.random(500)
            });
        if blocked {
            s.counts.kaijumukou += 1;
            return;
        }
        if m_hp == 1 {
            // 怪獣しとめた
            add_exp(
                ctx,
                &mut islands[idx],
                s.bx,
                s.by,
                spec.map_or(0, |m| m.exp),
            );

            if m_kind == 8 {
                // オームなら腐海発生 (ログは撃った島の名前で出る)
                let p = format!("({tx}, {ty})");
                let msg = mm::rotten_sea_born(&islands[idx].name, &p);
                ctx.log.out(turn, msg, Some(id), None);
                set(&mut islands[tn], tx, ty, L::RottenSea, 1);
                return;
            }

            if stealth {
                let msg = t::mon_kill(m_name, &t_point);
                ctx.log.secret(turn, msg.clone(), Some(id), Some(target));
                ctx.log.late(turn, msg, Some(target), None);
            } else {
                log_t(ctx, t::mon_kill(m_name, &t_point));
            }

            // 収入
            let value = spec.map_or(0, |m| m.value);
            if value > 0 {
                islands[tn].money += value;
                let unit = ctx.config.units.money.clone();
                ctx.log.out(
                    turn,
                    mm::ms_mon_money(m_name, value, &unit),
                    Some(target),
                    None,
                );

                for (count, building) in [
                    (islands[idx].scratch.sin, "神殿"),
                    (islands[idx].scratch.jin, "神社"),
                ] {
                    if count > 0 {
                        let v = value + ctx.random(101);
                        islands[idx].money += v;
                        let amount = format!("{v}{unit}");
                        let msg = t::shrine_money(
                            &islands[idx].name,
                            &ctx.globals.hex.point,
                            building,
                            &amount,
                        );
                        ctx.log.out(turn, msg, Some(id), None);
                    }
                }
            }

            // 怪獣退治数
            islands[idx].taiji += 1;

            // 賞関係 (マッチしなければ etc7 のマッチの値を使う)
            let (flags, monsters, turns) = prize_parts(&islands[idx].prize, &s.scope);
            let monsters = perl::int(&monsters) | (1i64 << m_kind);
            islands[idx].prize = format!("{flags},{monsters},{turns}");
        } else {
            // 怪獣生きてる。HPが1減る
            s.counts.kaijuhit += 1;
            let v = value_at(&islands[tn], tx, ty) - 1;
            set_value(&mut islands[tn], tx, ty, v);
            return;
        }
    } else {
        // 通常地形
        if stealth {
            let msg = t::normal(&t_lname, &t_point);
            ctx.log.secret(turn, msg.clone(), Some(id), Some(target));
            ctx.log.late(turn, msg, Some(target), None);
        } else {
            log_t(ctx, t::normal(&t_lname, &t_point));
        }
    }

    // 経験値
    if is_one_of(t_l, &EXP_TOWNS) && add_exp(ctx, &mut islands[idx], s.bx, s.by, t_lv / 20) {
        // 通常ミサイルなので難民にプラス
        s.boat += t_lv;
    }

    // 荒地になる
    set(&mut islands[tn], tx, ty, L::Waste, 1);

    let (m_kind, _, _) = monster_spec(t_lv);
    if m_kind == 17 && t_l == k(L::Monster) {
        set(&mut islands[tn], tx, ty, L::Monument, 86);
    }

    let rena = islands[idx].owner_stats.rena;
    if t_lv == 25 && t_l == k(L::Monument) && ctx.random(10000) < rena && rena > 2000 {
        // 魔方陣から怪獣出現。doCommand の $kind と $lv を書き換える (Perl 版のまま)
        let level4 = ctx.config.monster.levels[3];
        let new_kind = ctx.random(level4) + 1;
        c.kind = new_kind as u16;
        let spec = MONSTERS.get(new_kind as usize).copied();
        let lv = (new_kind << 4)
            + spec.map_or(0, |m| m.base_hp)
            + ctx.random(spec.map_or(0, |m| m.hp_range));
        c.lv = lv;
        set(&mut islands[tn], tx, ty, L::Monster, lv);
        let (_, m_name, _) = monster_spec(lv);
        let msg = t::mons_comemagic(&islands[idx].name, m_name);
        ctx.log.out(turn, msg, Some(id), None);
    }

    // でも油田だったら海
    if is_one_of(t_l, &[L::Oil, L::Frocity, L::Fune]) {
        set(&mut islands[tn], tx, ty, L::Sea, 0);
    }
    // でも養殖場なら浅瀬
    if t_l == k(L::Nursery) {
        set(&mut islands[tn], tx, ty, L::Sea, 1);
    }
    if t_l == k(L::Ice) {
        set(&mut islands[tn], tx, ty, L::Sea, 1);
    }
    if t_l == k(L::Onsen) {
        set(&mut islands[tn], tx, ty, L::Mountain, 0);
    }
}

/// 動物派遣
pub(super) fn send_monster(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let (id, turn) = (islands[idx].id, ctx.turn);
    let name = islands[idx].name.clone();
    {
        let sc = &islands[idx].scratch;
        if sc.shouhi > sc.ene {
            ctx.log
                .out(turn, cmsg::ms_no_ene(&name, c.com_name), Some(id), None);
            return false;
        }
    }
    // ターゲット取得
    let Some(&tn) = ctx.id_to_number.get(&c.target) else {
        // ターゲットがすでにない
        ctx.log
            .out(turn, cmsg::ms_no_target(&name, c.com_name), Some(id), None);
        return false;
    };
    let t_name = islands[tn].name.clone();
    let t_id = islands[tn].id;

    // 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
    let guard = ctx.config.guard_pop;
    if islands[idx].pop < guard || islands[tn].pop < guard {
        ctx.log
            .out(turn, cmsg::forbidden(&name, c.com_name), Some(id), None);
        return false;
    }

    // 動物派遣の分岐の中の $1.. (etc7 のマッチ)
    let mut scope = c.scope.clone();
    let [msjotai, _, msid] = ctx
        .globals
        .command
        .attack
        .ms
        .assign(scope.fields(&islands[idx].etc_raw[2]));
    if msjotai != 2 || t_id != msid {
        ctx.log
            .out(turn, t::niwaren3(&name, c.com_name), Some(id), None);
        return false;
    }

    if c.arg > 30 {
        c.arg = 30;
    }
    let arg = c.arg;
    // 負の arg は Perl 版では配列を後ろから数えるが、計画の入力では作れないので 0 として扱う
    let a = arg.max(0) as usize;

    // doCommand の $kind と $lv を書き換える
    c.kind = arg as u16;
    let spec = MONSTERS[a];
    c.lv = (arg << 4) + spec.base_hp + ctx.random(spec.hp_range);
    let (_, m_name, _) = monster_spec(c.lv);

    // $z0..$z30 と $z->{} の両方に代入する
    let assign_z = |ctx: &mut TurnContext, z: [i64; 31]| {
        ctx.globals.zoo = z;
        ctx.globals.hex.leisure.z = z;
    };

    if ctx.config.love_peace {
        let mut scope = scope.clone();
        let z = scope.fields::<31>(&islands[idx].etc_raw[1]);
        assign_z(ctx, z);
        let zt = scope.fields::<31>(&islands[tn].etc_raw[1]);
        let g = &mut ctx.globals.command.attack;
        g.zoo_t.assign(zt);
        g.zt = zt;

        let ms = ctx
            .globals
            .eisei5
            .assign(scope.fields(&islands[idx].eisei_raw[2]));
        let mst = ctx
            .globals
            .command
            .attack
            .eisei5_t
            .assign(scope.fields(&islands[tn].eisei_raw[2]));

        let tradeexe = spec.exp * 2;
        ctx.globals.command.attack.tradeexe = tradeexe;

        let z = ctx.globals.hex.leisure.z;
        if z[a] > 0
            && islands[tn].scratch.zoo > 0
            && mst[5] > tradeexe
            && islands[tn].owner_stats.rena > arg * 500
        {
            ctx.globals.hex.leisure.z[a] -= 1;
            ctx.globals.command.attack.zt[a] += 1;
            islands[idx].etc_raw[1] = perl::join(&ctx.globals.hex.leisure.z);
            islands[tn].etc_raw[1] = perl::join(&ctx.globals.command.attack.zt);

            let mut ms = ms;
            let mut mst = mst;
            ms[5] += tradeexe;
            mst[5] -= tradeexe;
            ctx.globals.eisei5.0 = ms;
            ctx.globals.command.attack.eisei5_t.0 = mst;
            islands[idx].eisei_raw[2] = perl::join(&ms);
            islands[tn].eisei_raw[2] = perl::join(&mst);

            c.cost *= arg as f64;
            let cost = c.cost as i64;
            islands[idx].money += cost;
            islands[tn].money -= cost;

            ctx.log.out(
                turn,
                t::mons_send2(&name, &t_name, m_name),
                Some(id),
                Some(c.target),
            );
        } else {
            ctx.log
                .out(turn, t::no_money2(&name, c.com_name), Some(id), None);
            return false;
        }
    } else {
        let mut scope = scope.clone();
        let z = scope.fields::<31>(&islands[idx].etc_raw[1]);
        assign_z(ctx, z);
        if z[a] > 0 {
            ctx.globals.hex.leisure.z[a] -= 1;
            islands[idx].etc_raw[1] = perl::join(&ctx.globals.hex.leisure.z);
        }

        let sc = &mut islands[tn].scratch.command.attack;
        sc.monstersend += 1;
        sc.monstersendkind = arg;

        c.cost *= arg as f64;
        islands[idx].money -= c.cost as i64;

        // メッセージ
        ctx.log.out(
            turn,
            t::mons_send(&name, &t_name, m_name),
            Some(id),
            Some(c.target),
        );
    }
    true
}

/// 大使派遣
pub(super) fn taishi(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let (id, turn) = (islands[idx].id, ctx.turn);
    let name = islands[idx].name.clone();
    // ターゲット取得
    let Some(&tn) = ctx.id_to_number.get(&c.target) else {
        // ターゲットがすでにない
        ctx.log
            .out(turn, cmsg::ms_no_target(&name, c.com_name), Some(id), None);
        return false;
    };
    let t_name = islands[tn].name.clone();
    let t_id = islands[tn].id;
    let forbidden = |ctx: &mut TurnContext| {
        ctx.log
            .out(turn, cmsg::forbidden(&name, c.com_name), Some(id), None);
        false
    };

    if id > 4090 {
        // ターゲットが大きい
        return forbidden(ctx);
    }

    // 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
    let guard = ctx.config.guard_pop;
    if islands[idx].pop < guard || islands[tn].pop < guard {
        return forbidden(ctx);
    }

    // 同idなら、実行は許可されない
    if id == t_id {
        return forbidden(ctx);
    }

    // 目標の島の大使館が多すぎるなら、実行は許可されない
    if islands[tn].scratch.tai > 2 {
        return forbidden(ctx);
    }

    let mut scope = c.scope.clone();
    let [msjotai, _, msid] = ctx
        .globals
        .command
        .attack
        .ms
        .assign(scope.fields(&islands[idx].etc_raw[2]));

    if ctx.config.love_peace && msjotai != 2 && t_id != msid {
        return forbidden(ctx);
    }

    // 着弾点範囲内外チェック (島の外なら Perl 版は next で doCommand を抜ける)
    let Some((tx, ty)) = in_island(&islands[tn].map, (c.x, c.y)) else {
        return false;
    };

    // 着弾点の地形等算出
    let t_l = kind_at(&islands[tn], tx, ty);
    let t_lv = value_at(&islands[tn], tx, ty);
    let t_lname = land_name(t_l, t_lv);
    let t_point = format!("({tx}, {ty})");

    if t_l != k(L::Plains) {
        ctx.log.out(
            turn,
            cmsg::land_fail(&name, c.com_name, &t_lname, &t_point),
            Some(id),
            None,
        );
        return false;
    }

    set(&mut islands[tn], tx, ty, L::Taishi, id);

    // ログの 2 番目の島 ID はグローバル変数の $tId (Perl 版のまま)
    let t_id_global = ctx.globals.hex.t_id;
    ctx.log.out(
        turn,
        t::taishi(&name, &t_name, c.com_name, &c.point),
        Some(id),
        t_id_global,
    );

    islands[idx].money -= c.cost as i64;
    true
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exp_to_level_matches_perl_table() {
        let base = k(L::Base);
        assert_eq!(exp_to_level(base, 0), 1);
        assert_eq!(exp_to_level(base, 19), 1);
        assert_eq!(exp_to_level(base, 20), 2);
        assert_eq!(exp_to_level(base, 120), 4);
        assert_eq!(exp_to_level(base, 200), 5);
        let sbase = k(L::Sbase);
        assert_eq!(exp_to_level(sbase, 49), 1);
        assert_eq!(exp_to_level(sbase, 100), 3);
        assert_eq!(exp_to_level(sbase, 255), 4);
    }

    #[test]
    fn prize_parts_falls_back_to_last_match() {
        let mut scope = MatchScope::default();
        assert_eq!(
            prize_parts("1,2,30,", &scope),
            ("1".into(), "2".into(), "30,".into())
        );
        scope.set(vec![2, 0, 3]);
        assert_eq!(
            prize_parts("", &scope),
            ("2".into(), "0".into(), "3".into())
        );
    }
}
