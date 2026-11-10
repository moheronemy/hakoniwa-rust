//! 魔術師派遣 (Perl 版 doCommand の `$kind == $HcomMagic` の分岐)。
//!
//! 魔法の強さは `etc9` (`estimate` が魔法の記念碑・魔法学校から計算する
//! `$co7, $magicf, $magici, $magica, $magicw, $magicl, $magicd`) で決まる。
//! `arg` が魔術師の種類 (0 炎, 1 氷, 2 地, 3 風, 4 光, 5 闇, 6 天空城, 7 動物園飼育係。
//! 8 以上は 0)。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 自分の島の怪獣を炎〜闇の魔術師で攻撃したときは、doCommand の中の `next` で抜ける。
//!   doCommand は turnMain の `while (doCommand(...) == 0) {}` の条件の中で呼ばれるので、
//!   `next` は `return 0` と同じになり、同じターンに次の計画も実行される。
//!   座標が島の外のときの `next` も同じ。
//! - 費用は攻撃などをしたときにだけ引かれ、何も起きなかったとき (電力が足りない、
//!   対象の地形が違うなど) は費用も取られずに 1 ターン使う。
//! - 電力の条件は `ene` (供給量) だけを見ていて、消費量 (`shouhi`) は見ない
//!   (腐海の処理と冒頭の確認は除く)。
//! - 魔術師のログ (`logIreAttackt*`) の 2 番目の島 ID はグローバル変数の `$tId`。
//! - 動物園飼育係は、`$taiji->{}` (グローバル変数) を `prize` の怪獣のビットの分だけ
//!   毎回増やす (ターンの間ずっと増え続ける)。
//! - `$t` (派遣の名前) はグローバル変数で、`arg` が負なら前の値のまま。

use crate::land::{around, in_island, land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::{self, MatchScope};
use crate::tables::{LandKind as L, MONSTERS};
use crate::turn::hex::town::{set, set_value};
use crate::turn::{TurnContext, monster_spec};

use super::{CmdRun, cmsg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$t` (派遣する魔術師の名前)。`arg` が負なら前の値が残る
    pub t: String,
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

const fn k(l: L) -> u8 {
    l as u8
}

/// 魔法の強さ (`etc9` を分解したもの)
#[derive(Debug, Clone, Copy)]
struct Magic {
    f: i64,
    i: i64,
    a: i64,
    w: i64,
    l: i64,
    d: i64,
}

/// `logTaishi2`
fn taishi2(name: &str, t_name: &str, point: &str, magickind: &str) -> String {
    format!(
        "{}が{}地点に向けて{}を行いました。",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::NAME, &format!("{t_name}島{point}")),
        wrap(tags::COM_NAME, magickind)
    )
}

/// `logIreAttackt2`
fn ire_attackt2(
    name: &str,
    m_name: &str,
    ma_name: &str,
    dpoint: i64,
    t_name: &str,
    t_point: &str,
) -> String {
    format!(
        "{}の<B>{m_name}</B>が引き起こした<B>{ma_name}</B>は{}の<B>{t_name}</B>に{}のダメージを与えました。",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::NAME, t_point),
        wrap(tags::DISASTER, &dpoint.to_string())
    )
}

/// `logIreAttackt3`
fn ire_attackt3(name: &str, m_name: &str, ma_name: &str, t_name: &str, t_point: &str) -> String {
    format!(
        "{}の<B>{m_name}</B>が引き起こした<B>{ma_name}</B>は{}の<B>{t_name}</B>を撃破！",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::NAME, t_point)
    )
}

/// `logIreAttackt4`
fn ire_attackt4(
    name: &str,
    m_name: &str,
    ma_name: &str,
    count: i64,
    t_name: &str,
    verb: &str,
) -> String {
    format!(
        "{}の<B>{m_name}</B>が引き起こした<B>{ma_name}</B>は{}ヶ所の<B>{t_name}</B>を{verb}ました！",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::DISASTER, &count.to_string())
    )
}

/// `logIreAttackt5` / `logIreAttackt6` / `logIreAttackt7` (動物園飼育係)
fn ire_attackt_zoo(name: &str, t_name: &str, t_point: &str, result: &str) -> String {
    format!(
        "{}の<B>動物園飼育係</B>が持ってきた<B>捕獲グッツ</B>は{}の<B>{t_name}</B>{result}",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::NAME, t_point)
    )
}

/// `logMsMonMoney`
fn ms_mon_money(m_name: &str, value: i64, unit: &str) -> String {
    format!("<B>{m_name}</B>の残骸には、<B>{value}{unit}</B>の値が付きました。")
}

/// `logMagicNoTarget`
fn magic_no_target(name: &str, com_name: &str) -> String {
    format!(
        "{}で予定されていた{}は、魔法学校がないため偽者を派遣してみました。",
        wrap(tags::NAME, &format!("{name}島")),
        wrap(tags::COM_NAME, com_name)
    )
}

/// `logMsNoEne2`
fn ms_no_ene2(name: &str) -> String {
    format!(
        "{}で予定されていた<B>捕獲グッツ使用</B>は、電力が不足する可能性があるため中止しました。",
        wrap(tags::NAME, &format!("{name}島"))
    )
}

/// `$prize =~ /([0-9]*),([0-9]*),(.*)/` (先頭に固定しない)。
/// マッチすれば (`$1`, `$2` の数値, `$3`) を返し、`m` の `$1`.. を更新する。
/// マッチしなければ最後に成功したマッチの `$1`..`$3` (数値の欄しか持たないので数値で)
fn split_prize(prize: &str, m: &mut MatchScope) -> (String, i64, String) {
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
        let flags = rest[..d1].to_string();
        let monsters = perl::int(&rest2[..d2]);
        // `.` は改行に当たらない
        let turns = rest2[d2 + 1..].split('\n').next().unwrap_or("").to_string();
        m.set(vec![perl::int(&flags), monsters, perl::int(&turns)]);
        return (flags, monsters, turns);
    }
    // マッチしないときは前のマッチの値を使う (Perl 版のまま)
    let [a, b, c] = m.current::<3>();
    (a.to_string(), b, c.to_string())
}

/// 怪獣が倒れたとき: 跡地にして、死体の値段を対象の島に、退治数と賞の印を自分の島に
#[allow(clippy::too_many_arguments)]
fn kill_monster(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    tn: usize,
    (tx, ty): (usize, usize),
    (after, after_value): (L, i64),
    t_kind: usize,
    m_name: &str,
    m: &MatchScope,
) {
    set(&mut islands[tn], tx, ty, after, after_value);
    // 報奨金
    let value = MONSTERS.get(t_kind).map_or(0, |s| s.value);
    islands[tn].money += value;
    let unit = ctx.config.units.money.clone();
    let t_id = islands[tn].id;
    ctx.log.out(
        ctx.turn,
        ms_mon_money(m_name, value, &unit),
        Some(t_id),
        None,
    );
    // 怪獣退治数
    let island = &mut islands[idx];
    island.taiji += 1;
    // 賞関係
    let mut m = m.clone();
    let (flags, monsters, turns) = split_prize(&island.prize, &mut m);
    let monsters = monsters | (1i64 << t_kind);
    island.prize = format!("{flags},{monsters},{turns}");
}

/// 炎〜天空城の魔術師が怪獣を攻撃する。`arg` と電力の条件に当てはまって攻撃したら `true`。
/// `idx` が自分の島、`tn` が対象の島 (自分の島のこともある)
#[allow(clippy::too_many_arguments)]
fn strike(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    tn: usize,
    c: &CmdRun,
    arg: i64,
    mg: Magic,
    (tx, ty): (usize, usize),
    m: &MatchScope,
) -> bool {
    let ene = islands[idx].scratch.ene;
    let h11 = islands[idx].scratch.h11;
    // (条件, 魔術師, 魔法, 倒れた跡地)
    let (ok, mg_name, ma_name, after) = match arg {
        0 => (ene > 4000 + mg.f * 400, "炎系魔術師", "灼熱の炎", L::Waste),
        1 => (
            ene > 6000 + mg.i * 500,
            "氷系魔術師",
            "アイシクルアロー",
            L::Ice,
        ),
        2 => (ene > 10000, "地系魔術師", "アースクエイク", L::Mountain),
        3 => (ene > 1000 + mg.w * 1000, "風系魔術師", "疾風の刃", L::Waste),
        4 => (ene > 10000, "光系魔術師", "ライトニングボルト", L::Waste),
        5 => (ene > 10000, "闇系魔術師", "ダークアロー", L::Waste),
        6 if idx != tn => (h11 > 0, "天空城", "天の裁き", L::Waste),
        _ => return false,
    };
    if !ok {
        return false;
    }
    // 対象となる怪獣の各要素取り出し
    let lv = islands[tn].map.get(tx, ty).map_or(0, |cell| cell.value);
    let (t_kind, m_name, t_hp) = monster_spec(lv);
    let dpoint = match arg {
        0 => mg.f,
        1 => mg.i + ctx.random(mg.i),
        2 => mg.a * 2,
        3 => ctx.random(mg.w * 2),
        4 => ctx.random(mg.l * 4),
        5 => ctx.random(mg.d * 3),
        // 天空城は $dpoint に代入しない (ログにも出ない)
        _ => 0,
    };
    let shouhi = match arg {
        0 => 4000 + mg.f * 400,
        1 => 6000 + mg.i * 500,
        3 => 1000 + mg.w * 1000,
        6 => ctx.random(20000),
        _ => 10000,
    };
    let island = &mut islands[idx];
    island.scratch.shouhi += shouhi;
    island.money -= c.cost as i64;
    let name = island.name.clone();
    let t_id = islands[tn].id;
    let t_point = format!("({tx}, {ty})");
    let message = if arg >= 5 {
        ire_attackt3(&name, mg_name, ma_name, m_name, &t_point)
    } else {
        ire_attackt2(&name, mg_name, ma_name, dpoint, m_name, &t_point)
    };
    let g_t_id = ctx.globals.hex.t_id;
    ctx.log.out(ctx.turn, message, Some(t_id), g_t_id);

    let killed = match arg {
        5 => ctx.random(100) < mg.d * 10,
        6 => true,
        _ => {
            set_value(&mut islands[tn], tx, ty, lv - dpoint);
            t_hp - dpoint < 1
        }
    };
    if killed {
        let after_value = if arg == 6 { 1 } else { 0 };
        kill_monster(
            ctx,
            islands,
            idx,
            tn,
            (tx, ty),
            (after, after_value),
            t_kind,
            m_name,
            m,
        );
    }
    true
}

/// 動物園飼育係 (自分の島の怪獣を捕まえる)。doCommand の戻り値を返す
fn zoo_keeper(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &CmdRun,
    mg: Magic,
    (tx, ty): (usize, usize),
    m: &MatchScope,
) -> bool {
    let mut m = m.clone();
    let turn = ctx.turn;
    let island = &mut islands[idx];
    let id = island.id;
    let zlv: i64 = ctx
        .points
        .iter()
        .filter_map(|&(sx, sy)| island.map.get(sx, sy))
        .filter(|cell| cell.kind == k(L::Zoo))
        .map(|cell| cell.value)
        .sum();

    // $z0..$z30 と $z->{...} の両方に代入する
    let z = m.fields::<31>(&island.etc_raw[1]);
    ctx.globals.zoo = z;
    ctx.globals.hex.leisure.z = z;
    let zookazu: i64 = z.iter().sum();

    // 対象となる怪獣の各要素取り出し
    let lv = island.map.get(tx, ty).map_or(0, |cell| cell.value);
    let (t_kind, m_name, t_hp) = monster_spec(lv);
    // $dpoint はログに出ないが乱数は使う
    let _dpoint = ctx.random(mg.d * 3);

    if t_kind as i64 * 1000 + 1000 > island.scratch.ene {
        island.money -= c.cost as i64;
        ctx.log.out(turn, ms_no_ene2(&island.name), Some(id), None);
        return false;
    }

    island.scratch.shouhi += t_kind as i64 * 1000;
    island.money -= c.cost as i64;

    let (_, monsters, _) = split_prize(&island.prize, &mut m);
    let taiji = &mut ctx.globals.hex.leisure.taiji;
    for (i, t) in taiji.iter_mut().enumerate() {
        if monsters & (1i64 << i) != 0 {
            *t += 1;
        }
    }

    let t_point = format!("({tx}, {ty})");
    let g_t_id = ctx.globals.hex.t_id;
    let limit = island.owner_stats.rena + island.scratch.co4 * 1000 + island.scratch.co99 * 1000;
    let has_taiji = ctx
        .globals
        .hex
        .leisure
        .taiji
        .get(t_kind)
        .is_some_and(|&v| v > 0);
    if t_kind as i64 * 500 * t_hp < limit && has_taiji {
        if zlv < zookazu {
            let message = ire_attackt_zoo(
                &island.name,
                m_name,
                &t_point,
                "をゲット！できますが、動物園にはこれ以上入りません。",
            );
            ctx.log.out(turn, message, Some(id), g_t_id);
        } else {
            let message = ire_attackt_zoo(&island.name, m_name, &t_point, "をゲット！");
            ctx.log.out(turn, message, Some(id), g_t_id);
            // 対象の怪獣が倒れて荒地になる
            set(island, tx, ty, L::Waste, 0);
            let mut m2 = m.clone();
            let z = m2.fields::<31>(&island.etc_raw[1]);
            ctx.globals.zoo = z;
            let zh = &mut ctx.globals.hex.leisure.z;
            *zh = z;
            if let Some(v) = zh.get_mut(t_kind) {
                *v += 1;
            }
            island.etc_raw[1] = perl::join(zh);
        }
    } else {
        let message = ire_attackt_zoo(&island.name, m_name, &t_point, "の捕獲に失敗！");
        ctx.log.out(turn, message, Some(id), g_t_id);
    }
    true
}

/// 腐海に魔術師を派遣する。`arg` が当てはまらなければ `None`
#[allow(clippy::too_many_arguments)]
fn rotten_sea(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    tn: usize,
    c: &mut CmdRun,
    arg: i64,
    mg: Magic,
    (tx, ty): (usize, usize),
    taishi_log: String,
) -> Option<bool> {
    // (魔術師, 魔法, 動詞, 1 マスあたりの電力)
    let (mg_name, ma_name, verb, per) = match arg {
        0 => (
            "炎系魔術師",
            "灼熱の炎",
            "焼き尽くし",
            (600 - mg.f * 50).max(300),
        ),
        4 => (
            "光系魔術師",
            "ライトニングボルト",
            "焼き尽くし",
            (700 - mg.l * 100).max(500),
        ),
        5 => ("闇系魔術師", "ダークアロー", "老化させ", 200),
        6 => ("天空城", "天の裁き", "吹き飛ばし", 0),
        _ => return None,
    };
    let (id, turn) = (islands[idx].id, ctx.turn);
    let t_id = islands[tn].id;
    ctx.log.out(turn, taishi_log, Some(id), Some(t_id));

    // 炎は着弾点のまわり 19 マス、それ以外は島全体 (@Hrpx, @Hrpy の順)
    let cells: Vec<(i64, i64)> = if arg == 0 {
        (0..19).map(|i| around(tx as i64, ty as i64, i)).collect()
    } else {
        ctx.points
            .iter()
            .map(|&(x, y)| (x as i64, y as i64))
            .collect()
    };
    let mut count = 0;
    for (sx, sy) in cells {
        // doCommand の my 変数 ($landKind, $lv, $landName, $point) に代入する
        let (land_kind, lv) = perl_get(&islands[tn].map, sx, sy);
        c.land_kind = land_kind;
        c.lv = lv;
        c.land_name = land_name(land_kind, lv);
        c.point = format!("({sx}, {sy})");

        // 範囲外判定
        let Some((px, py)) = in_island(&islands[tn].map, (sx, sy)) else {
            continue;
        };
        let rotten = land_kind == k(L::RottenSea);
        match arg {
            0 if rotten => {
                set(&mut islands[tn], px, py, L::Waste, 0);
                islands[idx].scratch.shouhi += per;
                count += 1;
            }
            4 if rotten && ctx.random(10) < mg.l => {
                set(&mut islands[tn], px, py, L::Waste, 0);
                islands[idx].scratch.shouhi += per;
                count += 1;
            }
            5 if rotten && ctx.random(5) < mg.d => {
                // 値の小数部分はそのまま残る
                if let Some(cell) = islands[tn].map.get_mut(px, py) {
                    cell.value += 10 + mg.d;
                }
                islands[idx].scratch.shouhi += per;
                count += 1;
            }
            6 if rotten => {
                set(&mut islands[tn], px, py, L::Waste, 1);
                islands[idx].scratch.shouhi += ctx.random(2500);
                count += 1;
            }
            _ => {}
        }
        let sc = &islands[idx].scratch;
        if sc.shouhi > sc.ene {
            break;
        }
    }
    // 電力が足りなくなって途中でやめたときも、最後まで回ったときも同じ
    let island = &mut islands[idx];
    island.money -= c.cost as i64;
    let g_t_id = ctx.globals.hex.t_id;
    ctx.log.out(
        turn,
        ire_attackt4(&island.name, mg_name, ma_name, count, "腐海", verb),
        Some(t_id),
        g_t_id,
    );
    Some(true)
}

pub(super) fn magic(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    c: &mut CmdRun,
) -> bool {
    let (id, turn) = (islands[idx].id, ctx.turn);
    let name = islands[idx].name.clone();

    if islands[idx].scratch.shouhi > islands[idx].scratch.ene {
        ctx.log
            .out(turn, cmsg::ms_no_ene(&name, c.com_name), Some(id), None);
        return false;
    }

    // ターゲット取得
    let tn = ctx.id_to_number.get(&c.target).copied();

    // $co7, $magicf, ... はグローバル変数
    let mut m = c.scope.clone();
    let [co7, f, i, a, w, l, d] = ctx
        .globals
        .hex
        .etc9
        .assign(m.fields(&islands[idx].etc_raw[4]));
    let mg = Magic { f, i, a, w, l, d };

    let Some(tn) = tn else {
        // ターゲットがすでにない
        ctx.log
            .out(turn, cmsg::ms_no_target(&name, c.com_name), Some(id), None);
        return false;
    };

    if co7 == 0 {
        ctx.log
            .out(turn, magic_no_target(&name, c.com_name), Some(id), None);
        return false;
    }

    let tx = c.x;
    let ty = c.y;
    // ($ty と $y は同じなので、ここでずれることはない)

    // 着弾点範囲内外チェック (範囲外なら next で、次の計画へ進む)
    let Some((tx, ty)) = in_island(&islands[tn].map, (tx, ty)) else {
        return false;
    };

    // 着弾点の地形等算出
    let cell = islands[tn].map.get(tx, ty).unwrap_or_default();
    let t_l = cell.kind;
    let t_name = islands[tn].name.clone();
    let t_id = islands[tn].id;

    if c.arg >= 8 {
        c.arg = 0;
    }
    let arg = c.arg;
    let t = match arg {
        0 => Some("炎系魔術師派遣"),
        1 => Some("氷系魔術師派遣"),
        2 => Some("地系魔術師派遣"),
        3 => Some("風系魔術師派遣"),
        4 => Some("光系魔術師派遣"),
        5 => Some("闇系魔術師派遣"),
        6 => Some("天空城砲撃"),
        7 => Some("動物園飼育係派遣"),
        _ => None,
    };
    if let Some(t) = t {
        ctx.globals.command.magic.t = t.to_string();
    }
    // logTaishi2 ($tLname, $tPoint は文面に出ない)
    let taishi_log = |ctx: &TurnContext, point: &str| {
        taishi2(&name, &t_name, point, &ctx.globals.command.magic.t)
    };

    if id == t_id {
        if t_l == k(L::Monster) {
            let message = taishi_log(ctx, &c.point);
            ctx.log.out(turn, message, Some(id), Some(t_id));
            if strike(ctx, islands, idx, idx, c, arg, mg, (tx, ty), &m) {
                // next (Perl 版のまま。同じターンに次の計画へ進む)
                return false;
            }
            if arg == 7 && islands[idx].scratch.zoo > 0 {
                return zoo_keeper(ctx, islands, idx, c, mg, (tx, ty), &m);
            }
        }
    } else {
        let ene = islands[idx].scratch.ene;
        if t_l == k(L::Plains) && ene > 2000 {
            let monument = match arg {
                0 => mg.f > 2,
                1 => mg.i > 2,
                2 => mg.a > 2,
                3 => mg.w > 2,
                4 => mg.l > 2,
                5 => mg.d > 2,
                6 => islands[idx].scratch.h11 > 0,
                _ => false,
            };
            if monument {
                let value = if arg == 6 { 100 } else { 96 + arg };
                set(&mut islands[tn], tx, ty, L::Monument, value);
            }
            let island = &mut islands[idx];
            island.scratch.shouhi += 2000;
            island.money -= c.cost as i64;
        }

        if t_l == k(L::RottenSea) {
            let message = taishi_log(ctx, &c.point);
            if let Some(r) = rotten_sea(ctx, islands, idx, tn, c, arg, mg, (tx, ty), message) {
                return r;
            }
        }

        if t_l == k(L::Monster) {
            strike(ctx, islands, idx, tn, c, arg, mg, (tx, ty), &m);
        }
    }

    let message = taishi_log(ctx, &c.point);
    ctx.log.out(turn, message, Some(id), Some(t_id));
    true
}
