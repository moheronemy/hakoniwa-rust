//! 怪獣 (`$landKind == $HlandMonster` の分岐) と、そこから呼ぶ広域被害 (`wideDamage`)。
//!
//! 怪獣ごとの特殊能力 (硬化、自爆、ミサイル、隕石、地震、ドレイン、封印解除、
//! 怪獣どうしの攻撃、マスコットの戦闘) のあと、移動して周囲を壊す。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 移動の後で `my($lv) = $landValue->[$sx][$sy]` (移動先の値) を宣言しているので、
//!   スライムの分裂・召喚・王蟲の脱皮が `$lv = $lv = ...` で代入するのはこの変数になる。
//!   そのあとの地雷の判定 (`$mHp < $lv`) は、移動先の地雷の値ではなく新しい怪獣の値と比べる。
//! - マスコット (いのら・超神獣テトラ) と神獣テトラは、研究所を探すループで外側の
//!   `$landKind` と `$lv` に代入する。この値で共通の災害判定 (火災など) をする。
//! - 怪獣の値の書き換え (`$lv += 2` など) は体力の 4 ビットからあふれると種類が変わる。
//! - 怪獣の能力で自分のマスが変わっても (自爆で海になったなど)、移動はそのマスの
//!   地形をそのまま移動先に写す。
//! - 怪獣どうしの攻撃のログに出す `$tPoint` はどこでも代入されない (空文字列)。
//! - 地震の「温泉なら山に戻す」は未定義のグローバル変数 `$kind` を見ている。

use std::collections::HashMap;

use crate::land::{around, in_island, land_name, perl_get};
use crate::log::tags::{self, wrap};
use crate::model::Island;
use crate::perl::trunc;
use crate::tables::{LandKind as L, MONSTERS};
use crate::turn::{TurnContext, monster_spec};

use super::hazards::wide_damage_sea2;
use super::town::{set, set_value};
use super::{Flow, HexRun, k, msg};

/// この系統で使う Perl 版のグローバル変数。
///
/// どれもこの系統の中では代入した直後に使うだけだが、Perl 版では `my` の無い
/// グローバル変数なので、ほかの処理から見えるように値を残しておく
#[derive(Debug, Default)]
pub struct Globals {
    /// `$tKind` (サタン・アイススコーピオンが地形の種類を入れる)
    pub t_kind: i64,
    /// `$tlv`
    pub tlv: i64,
    /// `$dmge`
    pub dmge: i64,
    /// `$attackdamege`, `$counterdamege` (マスコットの戦闘)
    pub attackdamege: i64,
    pub counterdamege: i64,
    /// `$landName` (マスコット・テトラが研究所を探すループで代入する)
    pub land_name: String,
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {}

/// doEachHex 1 回分の状態 (`@monsterMove`)
#[derive(Debug, Default)]
pub struct RunState {
    moved: HashMap<(usize, usize), i64>,
}

impl RunState {
    /// `$monsterMove[$x][$y]` (未定義なら 0)
    fn get(&self, x: usize, y: usize) -> i64 {
        self.moved.get(&(x, y)).copied().unwrap_or(0)
    }

    fn set(&mut self, x: usize, y: usize, v: i64) {
        self.moved.insert((x, y), v);
    }
}

fn is_one_of(kind: u8, list: &[L]) -> bool {
    list.iter().any(|&l| kind == k(l))
}

/// 島の中のマスの (種類, 値)
fn get(island: &Island, x: usize, y: usize) -> (u8, i64) {
    island.map.get(x, y).map_or((0, 0), |c| (c.kind, c.value))
}

/// マスの種類 (数値のまま) と値を書き換える (値の小数部分は消える)
fn put(island: &mut Island, x: usize, y: usize, kind: u8, value: i64) {
    if let Some(c) = island.map.get_mut(x, y) {
        c.kind = kind;
        c.value = value;
        island.scratch.land_frac.remove(&(x, y));
    }
}

fn point(x: impl std::fmt::Display, y: impl std::fmt::Display) -> String {
    format!("({x}, {y})")
}

/// Perl の `random($n)`。`$n` が負なら `int(rand(1) * $n)` は 0 以下になる
/// (共通の `random` は負の `$n` で 0 を返すので、ここでは自前で計算する)
fn random_signed(ctx: &mut TurnContext, n: i64) -> i64 {
    if n > 0 {
        ctx.random(n)
    } else {
        trunc(ctx.rand_f64(1.0) * n as f64)
    }
}

/// Perl が数値を文字列にするときの形 (`%.15g`)
fn perl_num_str(v: f64) -> String {
    if v == 0.0 {
        return "0".into();
    }
    let trim = |s: &str| -> String {
        if s.contains('.') {
            s.trim_end_matches('0').trim_end_matches('.').to_string()
        } else {
            s.to_string()
        }
    };
    let e = format!("{v:.14e}");
    let (mant, exp) = e.split_once('e').expect("exponent");
    let exp: i32 = exp.parse().expect("exponent");
    if !(-4..15).contains(&exp) {
        format!(
            "{}e{}{:02}",
            trim(mant),
            if exp < 0 { '-' } else { '+' },
            exp.abs()
        )
    } else {
        let prec = (14 - exp) as usize;
        trim(&format!("{v:.prec$}"))
    }
}

/// `seqnum($n)`: `sin($n + 1234)` を文字列にした末尾から 2 文字目 (数字でなければ 0)
pub(crate) fn seqnum(n: i64) -> i64 {
    let s = perl_num_str((n as f64 + 1234.0).sin());
    let b = s.as_bytes();
    if b.len() < 2 {
        return 0;
    }
    let c = b[b.len() - 2];
    if c.is_ascii_digit() {
        i64::from(c - b'0')
    } else {
        0
    }
}

/// 硬化中か (サンジラは奇数ターン、クジラは偶数ターン、めたはむ系は `seqnum` で決まる)
fn hardened(special: i64, turn: i64) -> bool {
    (special == 3 && turn % 2 == 1)
        || (special == 8 && seqnum(turn) % 2 == 0)
        || (special == 4 && turn % 2 == 0)
}

/// 新しい怪獣の値 (`($kind << 4) + $HmonsterBHP[$kind] + random($HmonsterDHP[$kind])`)
fn new_monster(ctx: &mut TurnContext, kind: usize) -> i64 {
    ((kind as i64) << 4) + MONSTERS[kind].base_hp + ctx.random(MONSTERS[kind].hp_range)
}

/// 海にあって、壊れると跡形もなくなるもの (`wideDamage` の中心と 1 ヘックス)
const SEA_THINGS: [L; 9] = [
    L::Sbase,
    L::Seacity,
    L::Seatown,
    L::Umishuto,
    L::Fune,
    L::Ice,
    L::Frocity,
    L::Umiamu,
    L::Oil,
];

/// 2 ヘックス先の被害を受けないもの (`wideDamage` と多弾頭ミサイル)
const OUTER_SAFE: [L; 14] = [
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
];

/// 怪獣が移動できないマス
const MOVE_BLOCK: [L; 26] = [
    L::Sea,
    L::Sbase,
    L::Seacity,
    L::Seatown,
    L::Bigtown,
    L::Bettown,
    L::Skycity,
    L::Umicity,
    L::Shuto,
    L::Umishuto,
    L::Fune,
    L::Frocity,
    L::Umiamu,
    L::Oil,
    L::Zoo,
    L::Nursery,
    L::BigRizort,
    L::Kajino,
    L::Gold,
    L::Mountain,
    L::Onsen,
    L::Monument,
    L::RottenSea,
    L::House,
    L::Taishi,
    L::Monster,
];

/// 衝撃波で壊れないもの
const FIRE_SAFE: [L; 8] = [
    L::Sea,
    L::Seacity,
    L::Seatown,
    L::Umishuto,
    L::Ice,
    L::Waste,
    L::Umiamu,
    L::Sbase,
];

fn out(ctx: &mut TurnContext, id: i64, message: String) {
    ctx.log.out(ctx.turn, message, Some(id), None);
}

/// 2 番目の島 ID に `$tId` を使うログ
fn out_t(ctx: &mut TurnContext, id: i64, message: String) {
    let t_id = ctx.globals.hex.t_id;
    ctx.log.out(ctx.turn, message, Some(id), t_id);
}

/// 怪獣の死体の値段を足してログを出す
fn reward(ctx: &mut TurnContext, island: &mut Island, kind: usize, name: &str) {
    let value = MONSTERS[kind].value;
    island.money += value;
    let unit = ctx.config.units.money.clone();
    out(ctx, island.id, m::ms_mon_money(name, value, &unit));
}

/// 賞関係: `prize` の 2 番目の欄に倒した怪獣の印を立てる。
///
/// Perl 版は `/([0-9]*),([0-9]*),(.*)/` (先頭に固定しない) で分解するので、
/// マッチした位置より前は捨てられる。マッチしなければ (Perl 版は前回の `$1` などを使うが)
/// 何もしない
fn add_prize_monster(island: &mut Island, kind: usize) {
    let s = island.prize.clone();
    let digits = |t: &str| t.bytes().take_while(u8::is_ascii_digit).count();
    for p in 0..=s.len() {
        if !s.is_char_boundary(p) {
            continue;
        }
        let rest = &s[p..];
        let d1 = digits(rest);
        if rest.as_bytes().get(d1) != Some(&b',') {
            continue;
        }
        let rest2 = &rest[d1 + 1..];
        let d2 = digits(rest2);
        if rest2.as_bytes().get(d2) != Some(&b',') {
            continue;
        }
        let flags = &rest[..d1];
        let monsters = crate::perl::int(&rest2[..d2]) | (1i64 << kind);
        // `.` は改行に当たらない
        let turns = rest2[d2 + 1..].split('\n').next().unwrap_or("");
        island.prize = format!("{flags},{monsters},{turns}");
        return;
    }
}

/// 移動前の怪獣
#[derive(Debug, Clone, Copy)]
struct Mon {
    kind: usize,
    name: &'static str,
    /// `$mHp` (マスコットの戦闘で減る)
    hp: i64,
    special: i64,
}

/// 怪獣
pub(super) fn monster(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let island = &mut islands[idx];
    let (x, y) = (h.x, h.y);
    if h.monster.get(x, y) == 2 {
        // すでに動いた後
        return Flow::Next;
    }

    let (kind, name, hp) = monster_spec(get(island, x, y).1);
    let mut mon = Mon {
        kind,
        name,
        hp,
        special: MONSTERS[kind].special,
    };
    let turn = ctx.turn;

    if mon.kind == 13 {
        // 幸運 (ログは出さない)
        let value = ctx.config.oil_money + ctx.random(500);
        island.money += value;
        let value = trunc(island.pop as f64 / 20.0) + ctx.random(11);
        island.food += value;
    }

    let outer_next = if hardened(mon.special, turn) {
        // 硬化中
        true
    } else if mon.kind == 16 && turn % 2 == 0 && mon.hp < 4 && ctx.rand_f64(1000.0) < 700.0 {
        out(
            ctx,
            island.id,
            m::mons_bomb(&island.name, &h.point(), mon.name),
        );
        wide_damage(ctx, island, x as i64, y as i64);
        if ctx.rand_f64(1000.0) < 250.0 {
            set(island, x, y, L::Monument, 78);
        }
        false
    } else if mon.kind == 17 {
        f02(ctx, island, h, &mon)
    } else if mon.kind == 18 {
        uriel(ctx, island, h, &mon)
    } else if mon.kind == 22 {
        ice_scorpion(ctx, island, h, &mon);
        false
    } else if mon.kind == 19 {
        alv(ctx, island, h, &mon);
        false
    } else if mon.kind == 20 {
        iseria(ctx, island, h, &mon);
        false
    } else if mon.kind == 21 {
        satan(ctx, island, h, &mon);
        false
    } else if mon.kind == 30 {
        mascot(ctx, island, h, &mut mon, &SUPER_TETRA);
        false
    } else if mon.kind == 29 {
        tetra(ctx, island, h);
        false
    } else if mon.kind == 28 {
        mascot(ctx, island, h, &mut mon, &MASCOT_INORA);
        false
    } else if mon.special == 6 || mon.kind == 13 {
        attack_monsters(ctx, island, h, &mon);
        false
    } else {
        false
    };
    if outer_next {
        return Flow::Next;
    }

    movement(ctx, island, h, &mon)
}

/// 人造怪獣f02: ミサイル・多弾頭ミサイル・アトミック☆ボム。戻り値は外側のループの `next`
fn f02(ctx: &mut TurnContext, island: &mut Island, h: &HexRun, mon: &Mon) -> bool {
    let (id, here) = (island.id, h.point());
    let size = ctx.config.island_size as i64;
    // 発射
    let tx = ctx.random(size);
    let ty = ctx.random(size);
    let (lk, lv) = get(island, tx as usize, ty as usize);
    let t_name = land_name(lk, lv);
    let t_point = point(tx, ty);

    if ctx.rand_f64(1000.0) < 600.0 {
        if is_one_of(
            lk,
            &[
                L::Sea,
                L::Mountain,
                L::Gold,
                L::Onsen,
                L::Ice,
                L::Seacity,
                L::Seatown,
                L::Umishuto,
                L::Umiamu,
                L::Sbase,
            ],
        ) {
            out_t(
                ctx,
                id,
                m::meka_ndamage(&island.name, mon.name, &here, &t_name, &t_point),
            );
            return true;
        }
        set(island, tx as usize, ty as usize, L::Waste, 1);
        out_t(
            ctx,
            id,
            m::meka_nmiss(&island.name, mon.name, &here, &t_name, &t_point),
        );
    } else if ctx.rand_f64(1000.0) < 400.0 {
        out_t(
            ctx,
            id,
            m::meka_smiss(&island.name, mon.name, &here, &t_name, &t_point),
        );
        for i in 0..7 {
            let (ssx, ssy) = around(tx, ty, i);
            // 範囲を確かめる前に読む
            let (kind, value) = perl_get(&island.map, ssx, ssy);
            let l_name = land_name(kind, value);
            let Some((ssx, ssy)) = in_island(&island.map, (ssx, ssy)) else {
                continue;
            };
            let p = point(ssx, ssy);
            if i < 1 {
                if is_one_of(
                    kind,
                    &[
                        L::Sea,
                        L::Seacity,
                        L::Seatown,
                        L::Umishuto,
                        L::Umiamu,
                        L::Sbase,
                    ],
                ) {
                    continue;
                }
                set(island, ssx, ssy, L::Sea, 1);
                out(ctx, id, m::fune_monster_sea(&island.name, &l_name, &p));
            } else if is_one_of(kind, &OUTER_SAFE) {
                continue;
            } else if kind == k(L::Monster) {
                out(ctx, id, m::wide_damage_monster(&island.name, &l_name, &p));
                set(island, ssx, ssy, L::Waste, 0);
            } else {
                out(ctx, id, m::wide_damage_waste(&island.name, &l_name, &p));
                set(island, ssx, ssy, L::Waste, 0);
            }
        }
    } else if ctx.rand_f64(1000.0) < 200.0 {
        // 落下
        let sx = ctx.random(size);
        let sy = ctx.random(size);
        let (lk, lv) = get(island, sx as usize, sy as usize);
        out_t(
            ctx,
            id,
            m::meka_ab(
                &island.name,
                mon.name,
                &here,
                &land_name(lk, lv),
                &point(sx, sy),
            ),
        );
        wide_damage(ctx, island, sx, sy);
    }
    false
}

/// 天使ウリエル: 島じゅうの怪獣の首を刎ね、小隕石を引き寄せる。戻り値は外側のループの `next`
fn uriel(ctx: &mut TurnContext, island: &mut Island, h: &HexRun, mon: &Mon) -> bool {
    let (id, here, turn) = (island.id, h.point(), ctx.turn);
    for i in 0..ctx.config.point_number() {
        let Some(&(sx, sy)) = ctx.points.get(i) else {
            break;
        };
        let (kind, value) = get(island, sx, sy);
        if kind != k(L::Monster) {
            continue;
        }
        let (t_kind, t_name, mut t_hp) = monster_spec(value);
        let mut tlv = value;
        if hardened(MONSTERS[t_kind].special, turn) {
            // 対象が硬化中なら効果なし
            continue;
        }
        if ctx.rand_f64(1000.0) < 600.0 {
            if t_kind == 18 {
            } else if t_kind == 28 || t_kind == 30 {
                out_t(
                    ctx,
                    id,
                    m::iti_attackms(&island.name, mon.name, &here, t_name, ""),
                );
                let dmge = ctx.random(4);
                ctx.globals.hex.monster.dmge = dmge;
                t_hp -= dmge;
                tlv -= dmge;
                set_value(island, sx, sy, tlv);
                if t_hp < 1 {
                    set(island, sx, sy, L::Waste, 0);
                    reward(ctx, island, t_kind, t_name);
                }
            } else {
                out_t(
                    ctx,
                    id,
                    m::iti_attack(&island.name, mon.name, &here, t_name, ""),
                );
                set(island, sx, sy, L::Waste, 0);
                reward(ctx, island, t_kind, t_name);
            }
        }
    }
    if ctx.rand_f64(1000.0) < 600.0 {
        let size = ctx.config.island_size as i64;
        let tx = ctx.random(size) as usize;
        let ty = ctx.random(size) as usize;
        let (lk, lv) = get(island, tx, ty);
        if is_one_of(lk, &[L::Sea, L::Mountain, L::Gold]) {
            return true;
        }
        set(island, tx, ty, L::Sea, 1);
        out_t(
            ctx,
            id,
            m::urieru_meteo(
                &island.name,
                mon.name,
                &here,
                &land_name(lk, lv),
                &point(tx, ty),
            ),
        );
        if ctx.rand_f64(1000.0) < 100.0 {
            set(island, tx, ty, L::Monument, 79);
        }
    }
    false
}

/// アイススコーピオン: 島じゅうの怪獣とミサイル基地などを氷漬けにする
fn ice_scorpion(ctx: &mut TurnContext, island: &mut Island, h: &HexRun, mon: &Mon) {
    let (id, here, turn) = (island.id, h.point(), ctx.turn);
    for i in 0..ctx.config.point_number() {
        let Some(&(sx, sy)) = ctx.points.get(i) else {
            break;
        };
        let (kind, value) = get(island, sx, sy);
        let p = point(sx, sy);
        if kind == k(L::Monster) {
            let (t_kind, t_name, mut t_hp) = monster_spec(value);
            let mut tlv = value;
            if hardened(MONSTERS[t_kind].special, turn) {
                continue;
            }
            if ctx.rand_f64(1000.0) < 600.0 {
                if t_kind == 22 {
                } else if t_kind == 28 || t_kind == 30 {
                    out_t(
                        ctx,
                        id,
                        m::ice_attack(&island.name, mon.name, &here, t_name, &p),
                    );
                    let dmge = ctx.random(4);
                    ctx.globals.hex.monster.dmge = dmge;
                    t_hp -= dmge;
                    tlv -= dmge;
                    set_value(island, sx, sy, tlv);
                    if t_hp < 1 {
                        set(island, sx, sy, L::Waste, 0);
                        reward(ctx, island, t_kind, t_name);
                    }
                } else {
                    out_t(
                        ctx,
                        id,
                        m::ice_attack(&island.name, mon.name, &here, t_name, &p),
                    );
                    set(island, sx, sy, L::Ice, 0);
                    if ctx.rand_f64(1000.0) < 100.0 {
                        set(island, sx, sy, L::Monument, 76);
                    }
                    reward(ctx, island, t_kind, t_name);
                }
            }
        } else if is_one_of(kind, &[L::Base, L::Defence, L::Oil, L::Fune]) {
            let g = &mut ctx.globals.hex.monster;
            g.t_kind = i64::from(kind);
            g.tlv = value;
            if ctx.rand_f64(1000.0) < 200.0 {
                out_t(
                    ctx,
                    id,
                    m::ice_attack(&island.name, mon.name, &here, &land_name(kind, value), &p),
                );
                set(island, sx, sy, L::Ice, 0);
                if ctx.rand_f64(1000.0) < 100.0 {
                    set(island, sx, sy, L::Monument, 76);
                }
            }
        }
    }
}

/// 魔術師アールヴ: 禁呪メテオ、巨大隕石、クエイク、ドレイン
fn alv(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun, mon: &Mon) {
    let (id, here, turn) = (island.id, h.point(), ctx.turn);
    let size = ctx.config.island_size as i64;
    let n = ctx.config.point_number();

    if ctx.rand_f64(1000.0) < 333.0 {
        out(ctx, id, m::mg_meteo(&island.name, mon.name, &here));
        let mut first = true;
        // random(3) を先に引く (Perl 版の `||` の順)
        while ctx.random(3) == 0 || first {
            first = false;
            let sx = ctx.random(size) as usize;
            let sy = ctx.random(size) as usize;
            let (lk, lv) = get(island, sx, sy);
            let l_name = land_name(lk, lv);
            let p = point(sx, sy);
            let name = island.name.clone();
            if lk == k(L::Sea) && lv == 0 {
                // 海ポチャ
                out(ctx, id, m::meteo_sea(&name, &l_name, &p));
            } else if is_one_of(lk, &[L::Mountain, L::Gold, L::Onsen]) {
                // 山破壊
                out(ctx, id, m::meteo_mountain(&name, &l_name, &p));
                set(island, sx, sy, L::Waste, 0);
                continue;
            } else if is_one_of(
                lk,
                &[
                    L::Sbase,
                    L::Seacity,
                    L::Seatown,
                    L::Umishuto,
                    L::Fune,
                    L::Frocity,
                    L::Umiamu,
                ],
            ) {
                out(ctx, id, m::meteo_sbase(&name, &l_name, &p));
            } else if lk == k(L::Monster) {
                out(ctx, id, m::meteo_monster(&name, &l_name, &p));
            } else if lk == k(L::Sea) || lk == k(L::Ice) {
                // 浅瀬
                out(ctx, id, m::meteo_sea1(&name, &l_name, &p));
            } else {
                out(ctx, id, m::meteo_normal(&name, &l_name, &p));
            }
            set(island, sx, sy, L::Sea, 0);
        }
    }

    if ctx.rand_f64(1000.0) < 400.0 {
        out(ctx, id, m::mg_meteo(&island.name, mon.name, &here));
        let sx = ctx.random(size);
        let sy = ctx.random(size);
        out(ctx, id, m::huge_meteo(&island.name, &point(sx, sy)));
        wide_damage(ctx, island, sx, sy);
    }

    if ctx.random(1000) < 450 {
        out(ctx, id, m::mg_earthquake(&island.name, mon.name, &here));
        out(ctx, id, m::earthquake(&island.name));
        for i in 0..n {
            let Some(&(sx, sy)) = ctx.points.get(i) else {
                break;
            };
            let (lk, lv) = get(island, sx, sy);
            let hit = (lk == k(L::Town) && lv >= 100)
                || (lk == k(L::Foodim) && lv < 480)
                || (lk == k(L::Procity) && lv < 130)
                || (lk == k(L::Newtown) && lv < 300)
                || (lk == k(L::Bigtown) && lv < 300)
                || (lk == k(L::HTFactory) && lv < 500)
                || (lk == k(L::SHTF) && lv < 500)
                || is_one_of(
                    lk,
                    &[
                        L::Rizort,
                        L::Kajino,
                        L::BigRizort,
                        L::Haribote,
                        L::Park,
                        L::Minato,
                        L::Kyujo,
                        L::Kyujokai,
                        L::Onsen,
                        L::Factory,
                    ],
                );
            // 1/4で壊滅
            if hit && ctx.random(4) == 0 {
                out(
                    ctx,
                    id,
                    m::eq_damage(&island.name, &land_name(lk, lv), &point(sx, sy)),
                );
                set(island, sx, sy, L::Waste, 0);
                // Perl 版は未定義のグローバル変数 $kind を見ている
                if ctx.globals.hex.kind == L::Onsen as i64 {
                    set(island, sx, sy, L::Mountain, 0);
                }
            }
        }
    }

    // ドレイン: 自分より体力の多い怪獣から体力を奪う
    for i in 0..n {
        let Some(&(sx, sy)) = ctx.points.get(i) else {
            break;
        };
        let (kind, value) = get(island, sx, sy);
        if kind != k(L::Monster) {
            continue;
        }
        let (t_kind, t_name, t_hp) = monster_spec(value);
        let mut tlv = value;
        if t_kind != 19 && t_hp > mon.hp {
            if hardened(MONSTERS[t_kind].special, turn) {
                continue;
            }
            out(ctx, id, m::mg_drain(&island.name, mon.name, t_name, &here));
            tlv -= t_hp - mon.hp;
            set_value(island, sx, sy, tlv);
            // $mHp は変えないので、何体から奪っても同じ差を足す (体力の 4 ビットからあふれうる)
            if mon.hp < 9 {
                h.lv += t_hp - mon.hp;
            }
            set_value(island, h.x, h.y, h.lv);
        }
    }
}

/// 堕天使イセリア: 体力が増え、食料を腐らせ、体力が 13 を超えると封印が解けて魔王サタンになる
fn iseria(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun, mon: &Mon) {
    let (id, here, (x, y)) = (island.id, h.point(), (h.x, h.y));
    h.lv += 2;
    set_value(island, x, y, h.lv);
    if ctx.random(1000) < 200 {
        island.food -= trunc(island.food as f64 / 2.0);
        out(ctx, id, m::fushoku(&island.name, mon.name, &here));
    }
    if mon.hp > 13 {
        out(ctx, id, m::umlimit(&island.name, mon.name, &here));
        wide_damage(ctx, island, x as i64, y as i64);

        for i in 0..ctx.config.point_number() {
            let Some(&(sx, sy)) = ctx.points.get(i) else {
                break;
            };
            let (lk, lv) = get(island, sx, sy);
            let hit = (lk == k(L::Town) && lv >= 100)
                || (lk == k(L::Foodim) && lv < 480)
                || (lk == k(L::Procity) && lv < 130)
                || is_one_of(
                    lk,
                    &[
                        L::Haribote,
                        L::Park,
                        L::Minato,
                        L::Kyujo,
                        L::Kyujokai,
                        L::Base,
                        L::Factory,
                    ],
                );
            // 1/6で壊滅
            if hit && ctx.random(6) == 0 {
                out(
                    ctx,
                    id,
                    m::umlimit_damage(&island.name, mon.name, &land_name(lk, lv), &point(sx, sy)),
                );
                set(island, sx, sy, L::Waste, 0);
                if ctx.rand_f64(1000.0) < 150.0 {
                    set(island, sx, sy, L::Monument, 74);
                }
            }
        }
        // 魔王サタンになる。この $lv はブロックの中の my 変数 (外側の $lv は変わらない)
        ctx.globals.hex.kind = 21;
        let lv = new_monster(ctx, 21);
        set(island, x, y, L::Monster, lv);
    }
}

/// 魔王サタン: 体力が増え、資金・食料を奪い、平地や森などを焼き尽くす
fn satan(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun, mon: &Mon) {
    let (id, here) = (island.id, h.point());
    if mon.hp < 9 {
        h.lv += 3;
    }
    set_value(island, h.x, h.y, h.lv);
    if ctx.random(1000) < 150 {
        island.money -= trunc(island.money as f64 / 2.0);
        out(ctx, id, m::kyoukou(&island.name, mon.name, &here));
    }
    if ctx.random(1000) < 200 {
        island.food = 0;
        out(ctx, id, m::fushoku(&island.name, mon.name, &here));
    }
    for i in 0..ctx.config.point_number() {
        let Some(&(sx, sy)) = ctx.points.get(i) else {
            break;
        };
        let (lk, lv) = get(island, sx, sy);
        if !is_one_of(
            lk,
            &[
                L::Plains,
                L::Plains2,
                L::Forest,
                L::Nursery,
                L::Farmchi,
                L::Farmpic,
                L::Farmcow,
                L::RottenSea,
            ],
        ) {
            continue;
        }
        let g = &mut ctx.globals.hex.monster;
        g.t_kind = i64::from(lk);
        g.tlv = lv;
        if ctx.rand_f64(1000.0) < 200.0 {
            out_t(
                ctx,
                id,
                m::hell_attack(
                    &island.name,
                    mon.name,
                    &here,
                    &land_name(lk, lv),
                    &point(sx, sy),
                ),
            );
            set(island, sx, sy, L::Waste, 0);
            if ctx.rand_f64(1000.0) < 100.0 {
                set(island, sx, sy, L::Monument, 78);
            }
            if ctx.rand_f64(1000.0) < 100.0 {
                set(island, sx, sy, L::Monument, 74);
            }
        }
    }
}

/// マスコットいのら・超神獣テトラの違い
struct Mascot {
    /// 帰宅・旅立ちのログに出す名前
    away_name: &'static str,
    /// 戦闘のログに出す名前
    battle_name: &'static str,
    /// 帰ってきた研究所の新しい値
    home_value: i64,
    /// 戦わない相手 (23 番とこれ)
    skip_kind: usize,
    /// 与えるダメージが 1 未満のときの値
    min_attack: i64,
    /// ミカエルを倒すと幸福の女神像を建てる
    mika: bool,
}

const SUPER_TETRA: Mascot = Mascot {
    away_name: "出撃中の超神獣テトラ",
    battle_name: "超神獣テトラ",
    home_value: 98,
    skip_kind: 30,
    min_attack: 2,
    mika: true,
};

const MASCOT_INORA: Mascot = Mascot {
    away_name: "出撃中のマスコットいのら",
    battle_name: "マスコットいのら",
    home_value: 4,
    skip_kind: 28,
    min_attack: 1,
    mika: false,
};

/// マスコットいのら・超神獣テトラ: 島に自分しかいなければ研究所に帰り、ほかの怪獣と 1 回戦う
fn mascot(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun, mon: &mut Mon, c: &Mascot) {
    let (id, (x, y)) = (island.id, (h.x, h.y));
    let n = ctx.config.point_number();

    if island.monster_live - island.scratch.c28 == 0 {
        if island.scratch.co99 == 0 {
            out(ctx, id, m::mstakeiede(&island.name, c.away_name));
        } else {
            for i in 1..n {
                let Some(&(sx, sy)) = ctx.points.get(i) else {
                    break;
                };
                // 外側のループの $landKind と $lv に代入している (Perl 版のまま)
                let (lk, lv) = get(island, sx, sy);
                h.land_kind = lk;
                h.lv = lv;
                ctx.globals.hex.monster.land_name = land_name(lk, lv);
                if lk == k(L::College) && h.lv == 99 {
                    set_value(island, sx, sy, c.home_value);
                    out(
                        ctx,
                        id,
                        m::mstakeokaeri(
                            &island.name,
                            c.away_name,
                            &point(sx, sy),
                            &land_name(h.land_kind, h.lv),
                        ),
                    );
                }
            }
        }
        set(island, x, y, L::Waste, 0);
    }

    for i in 1..n {
        let Some(&(sx, sy)) = ctx.points.get(i) else {
            break;
        };
        let (kind, value) = get(island, sx, sy);
        if kind != k(L::Monster) || ctx.globals.hex.msseigen >= 1 {
            continue;
        }
        let (t_kind, t_name, mut t_hp) = monster_spec(value);
        let mut tlv = value;
        if t_kind == c.skip_kind || t_kind == 23 {
            continue;
        }
        let [
            mut mshp,
            mut msap,
            mut msdp,
            mut mssp,
            mut mswin,
            mut msexe,
            tet,
        ] = ctx.globals.eisei5.update(&island.eisei_raw[2]);
        let t = t_kind as i64;
        let mut attack = random_signed(ctx, msap - t);
        let mut counter = random_signed(ctx, t - msdp);
        if attack < 1 {
            attack = c.min_attack;
        }
        if counter < 1 {
            counter = 1;
        }
        if ctx.rand_f64((5 + t) as f64) > mssp as f64 {
            attack = 0;
        }
        if ctx.rand_f64((5 + t) as f64) < mssp as f64 {
            counter = 0;
        }
        let g = &mut ctx.globals.hex.monster;
        g.attackdamege = attack;
        g.counterdamege = counter;

        out_t(
            ctx,
            id,
            m::ms_attackt(
                &island.name,
                c.battle_name,
                attack,
                counter,
                t_name,
                &point(sx, sy),
            ),
        );
        ctx.globals.hex.msseigen += 1;
        t_hp -= attack;
        tlv -= attack;
        set_value(island, sx, sy, tlv);
        mon.hp -= counter;
        h.lv -= counter;
        set_value(island, x, y, h.lv);

        if t_hp < 1 {
            set(island, sx, sy, L::Waste, 0);
            if c.mika && t_kind == 13 {
                set(island, sx, sy, L::Monument, 93);
                out_t(
                    ctx,
                    id,
                    m::ms_attackmika(&island.name, c.battle_name, t_name),
                );
            }
            let value = MONSTERS[t_kind].value;
            island.money += value;
            if ctx.rand_f64(1000.0) < value as f64 {
                if ctx.rand_f64(100.0) < 30.0 {
                    msap += 1;
                } else if ctx.rand_f64(100.0) < 30.0 {
                    msdp += 1;
                } else if ctx.rand_f64(100.0) < 30.0 {
                    mssp += 1;
                } else {
                    mshp += 1;
                    if mshp > 15 {
                        mshp = 15;
                    }
                }
            }
            msexe += MONSTERS[t_kind].exp;
            mswin += 1;
            island.taiji += 1;
            add_prize_monster(island, t_kind);
            island.eisei_raw[2] = crate::perl::join(&[mshp, msap, msdp, mssp, mswin, msexe, tet]);
            let unit = ctx.config.units.money.clone();
            out(ctx, id, m::ms_mon_money(t_name, value, &unit));
        }
        // $mshp などはグローバル変数
        ctx.globals.eisei5.0 = [mshp, msap, msdp, mssp, mswin, msexe, tet];

        if mon.hp < 1 {
            set(island, x, y, L::Waste, 0);
            reward(ctx, island, mon.kind, mon.name);
        }
    }
}

/// 神獣テトラ: 島に自分しかいなければ研究所に帰る
fn tetra(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun) {
    let id = island.id;
    if island.monster_live != 1 || island.scratch.co99 == 0 {
        return;
    }
    for i in 1..ctx.config.point_number() {
        let Some(&(sx, sy)) = ctx.points.get(i) else {
            break;
        };
        // 外側のループの $landKind と $lv に代入している (Perl 版のまま)
        let (lk, lv) = get(island, sx, sy);
        h.land_kind = lk;
        h.lv = lv;
        ctx.globals.hex.monster.land_name = land_name(lk, lv);
        if lk == k(L::College) && h.lv == 99 {
            set_value(island, sx, sy, 98);
            set(island, h.x, h.y, L::Waste, 0);
            out(
                ctx,
                id,
                m::mstakeokaeri(
                    &island.name,
                    "テトラ",
                    &point(sx, sy),
                    &land_name(h.land_kind, h.lv),
                ),
            );
        }
    }
}

/// 天使ミカエル (と特殊能力 6 の怪獣): 自分より体力の少ない怪獣を攻撃する (島で 2 回まで)
fn attack_monsters(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun, mon: &Mon) {
    let (id, here, turn) = (island.id, h.point(), ctx.turn);
    for i in 0..ctx.config.point_number() {
        let Some(&(sx, sy)) = ctx.points.get(i) else {
            break;
        };
        let (kind, value) = get(island, sx, sy);
        if kind != k(L::Monster) || ctx.globals.hex.kougekiseigenm >= 2 {
            continue;
        }
        let (t_kind, t_name, mut t_hp) = monster_spec(value);
        let mut tlv = value;
        if mon.hp <= t_hp {
            // 対象より体力が低かった場合は何もしない
            continue;
        }
        if hardened(MONSTERS[t_kind].special, turn) {
            continue;
        }
        let message = if mon.kind == 13 {
            m::mons_attackt(&island.name, mon.name, &here, t_name, "")
        } else {
            m::mons_attack(&island.name, mon.name, &here, t_name, "")
        };
        out_t(ctx, id, message);
        ctx.globals.hex.kougekiseigenm += 1;

        t_hp -= 1;
        if t_hp != 0 {
            tlv -= 1;
            set_value(island, sx, sy, tlv);
        } else {
            set(island, sx, sy, L::Waste, 0);
            reward(ctx, island, t_kind, t_name);
        }
        // 対象の怪獣の体力を奪って自分の体力を回復
        if mon.hp < 9 {
            h.lv += 1;
        }
        set_value(island, h.x, h.y, h.lv);
    }
}

/// 移動と、移動した後の能力 (分裂・召喚・脱皮・衝撃波・冷気)、移動先の地形の処理
fn movement(ctx: &mut TurnContext, island: &mut Island, h: &mut HexRun, mon: &Mon) -> Flow {
    let (id, (x, y)) = (island.id, (h.x, h.y));

    // 動く方向を決定
    let mut target = None;
    for _ in 0..3 {
        let d = ctx.random(6) + 1;
        let Some((sx, sy)) = in_island(&island.map, around(x as i64, y as i64, d as usize)) else {
            continue;
        };
        if !is_one_of(get(island, sx, sy).0, &MOVE_BLOCK) {
            target = Some((sx, sy));
            break;
        }
    }
    let Some((sx, sy)) = target else {
        // 動かなかった
        return Flow::Next;
    };

    if (mon.kind == 28 || mon.kind == 30) && get(island, sx, sy).0 != k(L::Waste) {
        return Flow::Next;
    }

    // 動いた先の地形によりメッセージ
    let (l, target_value) = get(island, sx, sy);
    // この `my($lv)` に分裂・召喚・脱皮が新しい怪獣の値を代入する (Perl 版のまま)
    let mut lv = target_value;
    let l_name = land_name(l, lv);
    let to = point(sx, sy);
    let here = h.point();

    // 移動 (自分のマスが能力で変わっていても、そのまま写す)
    let (src_kind, src_value) = get(island, x, y);
    put(island, sx, sy, src_kind, src_value);
    // もと居た位置を荒地に
    set(island, x, y, L::Waste, 0);

    let monster_live = island.monster_live;
    if mon.kind == 11 {
        // スライムの分裂
        if ctx.rand_f64(1000.0) < 900.0 && monster_live < 7 {
            ctx.globals.hex.kind = 11;
            lv = new_monster(ctx, 11);
            set(island, x, y, L::Monster, lv);
        } else if ctx.rand_f64(20000.0) < (400 - monster_live) as f64 && monster_live > 7 {
            ctx.globals.hex.kind = 11;
            lv = new_monster(ctx, 11);
            set(island, x, y, L::Monster, lv);
            out(ctx, id, m::new_monster_born(&island.name, &here));
        }
    }

    if (mon.kind == 15 || mon.kind == 19) && ctx.rand_f64(1000.0) < 600.0 && monster_live < 7 {
        // 召喚
        let kind = (ctx.random(ctx.config.monster.levels[2]) + 1) as usize;
        ctx.globals.hex.kind = kind as i64;
        lv = new_monster(ctx, kind);
        set(island, x, y, L::Monster, lv);
        let (new_kind, new_name, _) = monster_spec(lv);
        // 新しい怪獣の種類と比べるので、レイジラ (15) は呼ばれず、いつも召喚のログになる
        if new_kind == 15 {
            out(ctx, id, m::new_kaiju(&island.name, new_name, &here));
        } else {
            let (l2, v2) = get(island, sx, sy);
            out(
                ctx,
                id,
                m::shoukan(&island.name, &land_name(l2, v2), new_name, &here),
            );
        }
    }

    if mon.kind == 8 {
        if ctx.rand_f64(1000.0) < 400.0 {
            // 腐海が生まれる
            out(ctx, id, m::rotten_sea_born(&island.name, &here));
            set(island, x, y, L::RottenSea, 1);
        } else if ctx.rand_f64(1000.0) < 200.0 {
            // 脱皮
            out(ctx, id, m::nuginugi(&island.name, &here));
            set(island, x, y, L::Monument, 87);
            ctx.globals.hex.kind = 8;
            lv = (8 << 4) + MONSTERS[8].base_hp + ctx.random(3);
            set(island, sx, sy, L::Monster, lv);
        }
    }

    // 怪獣が周囲を焼き尽くす能力
    if mon.special == 7 || mon.kind == 16 {
        shock_wave(ctx, island, (sx, sy), 7, mon.name);
    }
    if mon.kind == 13 || mon.kind == 18 {
        shock_wave(ctx, island, (sx, sy), 19, mon.name);
    }
    // フリーズストーム
    if mon.special == 9 || mon.kind == 22 {
        freeze_storm(ctx, island, (sx, sy), mon.name);
    }
    // スライムレジェンド: 周りにスライムを産む
    if mon.kind == 14 && island.monster_live < 7 {
        for i in 1..7 {
            let Some((ssx, ssy)) = in_island(&island.map, around(sx as i64, sy as i64, i)) else {
                continue;
            };
            let (kind, _) = get(island, ssx, ssy);
            if is_one_of(
                kind,
                &[
                    L::Sea,
                    L::Seacity,
                    L::Seatown,
                    L::Umishuto,
                    L::Oil,
                    L::Fune,
                    L::Frocity,
                    L::Nursery,
                    L::Umiamu,
                    L::Mountain,
                    L::Gold,
                    L::Onsen,
                    L::Monster,
                    L::Sbase,
                ],
            ) {
                continue;
            }
            // ここの $kind と $lv はブロックの中の my 変数
            let v = new_monster(ctx, 11);
            set(island, ssx, ssy, L::Monster, v);
            if ctx.rand_f64(1000.0) < 50.0 {
                set(island, ssx, ssy, L::Monument, 77);
            }
            out(ctx, id, m::new_monster_born(&island.name, &point(ssx, ssy)));
        }
    }

    // 移動済みフラグ
    match MONSTERS[mon.kind].special {
        // 移動済みフラグは立てない
        2 => {}
        // 速い怪獣
        1 => {
            let v = h.monster.get(x, y) + 1;
            h.monster.set(sx, sy, v);
        }
        // 普通の怪獣
        _ => h.monster.set(sx, sy, 2),
    }

    if l == k(L::Defence) && ctx.config.defence_self_destruct {
        // 防衛施設を踏んだ
        out(
            ctx,
            id,
            m::mons_move_defence(&island.name, &l_name, &to, mon.name),
        );
        wide_damage(ctx, island, sx as i64, sy as i64);
    } else if l == k(L::Mine) {
        // 地雷を踏んだ
        if mon.hp < lv {
            // 死亡して死体が飛び散った
            out(
                ctx,
                id,
                m::mons_mine(&island.name, &l_name, &to, mon.name, "消し飛びました。"),
            );
        } else if mon.hp == lv {
            // 死亡して死体が残った
            out(
                ctx,
                id,
                m::mons_mine(&island.name, &l_name, &to, mon.name, "力尽き、倒れました。"),
            );
            let value = MONSTERS[mon.kind].value;
            if value > 0 {
                island.money += value;
                let unit = ctx.config.units.money.clone();
                out(ctx, id, m::ms_mon_money(mon.name, value, &unit));
            }
            island.taiji += 1;
            add_prize_monster(island, mon.kind);
        } else {
            // 生き残った
            out(
                ctx,
                id,
                m::mons_mine(
                    &island.name,
                    &l_name,
                    &to,
                    mon.name,
                    "苦しそうに咆哮しました。",
                ),
            );
            let v = get(island, sx, sy).1 - lv;
            set_value(island, sx, sy, v);
            return Flow::Next;
        }
        // 怪獣は荒地に
        set(island, sx, sy, L::Waste, 1);
    } else if l != k(L::Waste) {
        out(ctx, id, m::mons_move(&island.name, &l_name, &to, mon.name));
    }
    Flow::Continue
}

/// 衝撃波: 移動先の周囲 (`range` 個のマス) を壊す
fn shock_wave(
    ctx: &mut TurnContext,
    island: &mut Island,
    (sx, sy): (usize, usize),
    range: usize,
    m_name: &str,
) {
    let id = island.id;
    for i in 1..range {
        let Some((ssx, ssy)) = in_island(&island.map, around(sx as i64, sy as i64, i)) else {
            continue;
        };
        let (kind, lv) = get(island, ssx, ssy);
        if is_one_of(kind, &FIRE_SAFE) {
            // 海と海底基地は焼かれない
            continue;
        } else if is_one_of(kind, &[L::Oil, L::Fune, L::Frocity]) {
            set(island, ssx, ssy, L::Sea, 0);
        } else if kind == k(L::Nursery) {
            set(island, ssx, ssy, L::Sea, 1);
        } else if kind == k(L::Gold) || kind == k(L::Onsen) {
            set(island, ssx, ssy, L::Mountain, 0);
        } else if kind == k(L::Mountain) && lv > 0 {
            // 採掘場は山に戻る (値が 0 の山は次の else で荒地になる)
            set_value(island, ssx, ssy, 0);
        } else if kind == k(L::Monster) {
            hurt_mascot(ctx, island, (ssx, ssy), L::Waste);
        } else {
            // 全てが焼き尽くされる
            set(island, ssx, ssy, L::Waste, 0);
        }
        out(
            ctx,
            id,
            m::mons_fire(&island.name, &land_name(kind, lv), &point(ssx, ssy), m_name),
        );
    }
}

/// フリーズストーム: 移動先の周囲を氷河にする
fn freeze_storm(
    ctx: &mut TurnContext,
    island: &mut Island,
    (sx, sy): (usize, usize),
    m_name: &str,
) {
    let id = island.id;
    for i in 1..7 {
        let Some((ssx, ssy)) = in_island(&island.map, around(sx as i64, sy as i64, i)) else {
            continue;
        };
        let (kind, lv) = get(island, ssx, ssy);
        if is_one_of(
            kind,
            &[
                L::Seacity,
                L::Seatown,
                L::Umishuto,
                L::Ice,
                L::Umiamu,
                L::Sbase,
            ],
        ) {
            continue;
        } else if is_one_of(kind, &[L::Oil, L::Fune, L::Frocity]) {
            set(island, ssx, ssy, L::Ice, 0);
        } else if kind == k(L::Nursery) {
            set(island, ssx, ssy, L::Ice, 1);
        } else if kind == k(L::Monster) {
            hurt_mascot(ctx, island, (ssx, ssy), L::Ice);
        } else {
            // 海も氷河になる
            set(island, ssx, ssy, L::Ice, 0);
        }
        out(
            ctx,
            id,
            m::mons_cold(&island.name, &land_name(kind, lv), &point(ssx, ssy), m_name),
        );
    }
}

/// 衝撃波・冷気が怪獣に当たったとき: マスコットだけが傷つく (倒れると `dead` の地形になる)
fn hurt_mascot(ctx: &mut TurnContext, island: &mut Island, (sx, sy): (usize, usize), dead: L) {
    let value = get(island, sx, sy).1;
    let (t_kind, t_name, mut t_hp) = monster_spec(value);
    let mut tlv = value;
    if t_kind == 28 || t_kind == 30 {
        let dmge = ctx.random(4);
        ctx.globals.hex.monster.dmge = dmge;
        t_hp -= dmge;
        tlv -= dmge;
        set_value(island, sx, sy, tlv);
        if t_hp < 1 {
            set(island, sx, sy, dead, 0);
            reward(ctx, island, t_kind, t_name);
        }
    }
}

/// `wideDamage`: (x, y) を中心に、1 ヘックスまでを水没させ、2 ヘックスを荒地にする
pub(crate) fn wide_damage(ctx: &mut TurnContext, island: &mut Island, x: i64, y: i64) {
    let id = island.id;
    for i in 0..19 {
        let (sx, sy) = around(x, y, i);
        // 範囲を確かめる前に読む
        let (kind, lv) = perl_get(&island.map, sx, sy);
        let l_name = land_name(kind, lv);
        let Some((sx, sy)) = in_island(&island.map, (sx, sy)) else {
            continue;
        };
        let p = point(sx, sy);
        if i < 7 {
            // 中心、および1ヘックス
            if kind == k(L::Sea) {
                set_value(island, sx, sy, 0);
                continue;
            } else if is_one_of(kind, &SEA_THINGS) {
                out(ctx, id, wide_damage_sea2(&island.name, &l_name, &p));
                set(island, sx, sy, L::Sea, 0);
            } else {
                if kind == k(L::Monster) {
                    let (m_kind, _, _) = monster_spec(lv);
                    if (m_kind == 20 || m_kind == 21) && i == 0 {
                        continue;
                    }
                    out(
                        ctx,
                        id,
                        m::wide_damage_monster_sea(&island.name, &l_name, &p),
                    );
                } else {
                    out(ctx, id, m::wide_damage_sea(&island.name, &l_name, &p));
                }
                // 中心は海、まわりは浅瀬
                set(island, sx, sy, L::Sea, if i == 0 { 0 } else { 1 });
            }
        } else if is_one_of(kind, &OUTER_SAFE) {
            continue;
        } else if kind == k(L::Monster) {
            out(ctx, id, m::wide_damage_monster(&island.name, &l_name, &p));
            set(island, sx, sy, L::Waste, 0);
        } else {
            out(ctx, id, m::wide_damage_waste(&island.name, &l_name, &p));
            set(island, sx, sy, L::Waste, 0);
        }
    }
}

/// ログの文面
mod m {
    use super::{msg, tags, wrap};

    fn ia(name: &str, point: &str) -> String {
        msg::island_at(name, point)
    }

    fn n(s: &str) -> String {
        wrap(tags::NAME, s)
    }

    fn d(s: &str) -> String {
        wrap(tags::DISASTER, s)
    }

    /// `logMonsBomb`
    pub fn mons_bomb(name: &str, point: &str, m_name: &str) -> String {
        format!(
            "{}の<B>{m_name}</B>が{}を起こし自爆しました。",
            ia(name, point),
            d("メルトダウン")
        )
    }

    /// `logMekaNdamage`
    pub fn meka_ndamage(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が発射したミサイルが{}の<B>{t}</B>に着弾しました。",
            ia(name, point),
            n(tp)
        )
    }

    /// `logMekaNmiss`
    pub fn meka_nmiss(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が発射したミサイルが{}の<B>{t}</B>に着弾し一帯が壊滅しました。",
            ia(name, point),
            n(tp)
        )
    }

    /// `logMekaSmiss`
    pub fn meka_smiss(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が発射した{}が{}の<B>{t}</B>に着弾しました。",
            ia(name, point),
            d("多弾頭ミサイル"),
            n(tp)
        )
    }

    /// `logMekaAB`
    pub fn meka_ab(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が発射した{}が{}の<B>{t}</B>に着弾し大爆発しました。",
            ia(name, point),
            d("アトミック☆ボム"),
            n(tp)
        )
    }

    /// `logFuneMonsterSea`
    pub fn fune_monster_sea(name: &str, l: &str, point: &str) -> String {
        format!("{}の<B>{l}</B>は吹き飛び水没しました。", ia(name, point))
    }

    /// `logWideDamageMonster`
    pub fn wide_damage_monster(name: &str, l: &str, point: &str) -> String {
        format!("{}の<B>{l}</B>は消し飛びました。", ia(name, point))
    }

    /// `logWideDamageWaste`
    pub fn wide_damage_waste(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}の<B>{l}</B>は一瞬にして<B>荒地</B>と化しました。",
            ia(name, point)
        )
    }

    /// `logWideDamageMonsterSea`
    pub fn wide_damage_monster_sea(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}の陸地は<B>{l}</B>もろとも水没しました。",
            ia(name, point)
        )
    }

    /// `logWideDamageSea`
    pub fn wide_damage_sea(name: &str, l: &str, point: &str) -> String {
        format!("{}の<B>{l}</B>は<B>水没</B>しました。", ia(name, point))
    }

    /// `logItiAttack`
    pub fn iti_attack(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が{}の<B>{t}</B>の首を刎ねました。",
            ia(name, point),
            n(tp)
        )
    }

    /// `logItiAttackms`
    pub fn iti_attackms(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が{}の<B>{t}</B>を斬りつけました。",
            ia(name, point),
            n(tp)
        )
    }

    /// `logMsMonMoney`
    pub fn ms_mon_money(m: &str, value: i64, unit: &str) -> String {
        format!("<B>{m}</B>の残骸には、<B>{value}{unit}</B>の値が付きました。")
    }

    /// `logUrieruMeteo`
    pub fn urieru_meteo(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が引き寄せた{}が{}の<B>{t}</B>に落下し一帯が壊滅しました。",
            ia(name, point),
            d("小隕石"),
            n(tp)
        )
    }

    /// `logIceAttack`
    pub fn ice_attack(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>の発する氷の矢は{}の<B>{t}</B>の中心を貫きました。",
            ia(name, point),
            n(tp)
        )
    }

    /// `logMgMeteo`
    pub fn mg_meteo(name: &str, m: &str, point: &str) -> String {
        format!(
            "{}の<B>{m}</B>は{}を唱えました。",
            ia(name, point),
            d("禁呪メテオ")
        )
    }

    /// `logMeteoSea`
    pub fn meteo_sea(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}の<B>{l}</B>に{}が落下しました。",
            ia(name, point),
            d("隕石")
        )
    }

    /// `logMeteoMountain`
    pub fn meteo_mountain(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}の<B>{l}</B>に{}が落下、<B>{l}</B>は消し飛びました。",
            ia(name, point),
            d("隕石")
        )
    }

    /// `logMeteoSbase`
    pub fn meteo_sbase(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}の<B>{l}</B>に{}が落下、<B>{l}</B>は崩壊しました。",
            ia(name, point),
            d("隕石")
        )
    }

    /// `logMeteoMonster`
    pub fn meteo_monster(name: &str, l: &str, point: &str) -> String {
        format!(
            "<B>{l}</B>がいた{}地点に{}が落下、陸地は<B>{l}</B>もろとも水没しました。",
            ia(name, point),
            d("隕石")
        )
    }

    /// `logMeteoSea1` (`$lName` は使わない)
    pub fn meteo_sea1(name: &str, _l: &str, point: &str) -> String {
        format!(
            "{}地点に{}が落下、海底がえぐられました。",
            ia(name, point),
            d("隕石")
        )
    }

    /// `logMeteoNormal`
    pub fn meteo_normal(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}地点の<B>{l}</B>に{}が落下、一帯が水没しました。",
            ia(name, point),
            d("隕石")
        )
    }

    /// `logHugeMeteo`
    pub fn huge_meteo(name: &str, point: &str) -> String {
        format!("{}地点に{}が落下！！", ia(name, point), d("巨大隕石"))
    }

    /// `logMgEarthquake`
    pub fn mg_earthquake(name: &str, m: &str, point: &str) -> String {
        format!(
            "{}の<B>{m}</B>は{}を唱えました。",
            ia(name, point),
            d("クエイク")
        )
    }

    /// `logEarthquake`
    pub fn earthquake(name: &str) -> String {
        format!("{}で大規模な{}が発生！！", msg::island(name), d("地震"))
    }

    /// `logEQDamage`
    pub fn eq_damage(name: &str, l: &str, point: &str) -> String {
        format!(
            "{}の<B>{l}</B>は{}により壊滅しました。",
            ia(name, point),
            d("地震")
        )
    }

    /// `logMgDrain`
    pub fn mg_drain(name: &str, m: &str, t: &str, point: &str) -> String {
        format!(
            "{}の<B>{m}</B>は<B>{t}</B>に対して{}を唱えました。",
            ia(name, point),
            d("ドレイン")
        )
    }

    /// `logFushoku`
    pub fn fushoku(name: &str, m: &str, point: &str) -> String {
        format!(
            "{}の<B>{m}</B>は{}の蓄えていた<B>食料</B>を{}させてしまったようです。",
            ia(name, point),
            msg::island(name),
            d("腐敗")
        )
    }

    /// `logUmlimit`
    pub fn umlimit(name: &str, m: &str, point: &str) -> String {
        format!(
            "{}の<B>{m}</B>の<B>封印</B>が{}してしまったようです。",
            ia(name, point),
            d("解除")
        )
    }

    /// `logUmlimitDamage`
    pub fn umlimit_damage(name: &str, m: &str, l: &str, point: &str) -> String {
        format!(
            "{}の<B>{l}</B>は<B>{m}</B>の{}により壊滅しました。",
            ia(name, point),
            d("解放されたエネルギー")
        )
    }

    /// `logKyoukou`
    pub fn kyoukou(name: &str, m: &str, point: &str) -> String {
        format!(
            "{}の<B>{m}</B>は{}に{}をもたらしました。",
            ia(name, point),
            msg::island(name),
            d("大恐慌")
        )
    }

    /// `logHellAttack`
    pub fn hell_attack(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>の呼び起こした地獄の炎は{}の<B>{t}</B>を焼き尽くしました。",
            ia(name, point),
            n(tp)
        )
    }

    /// `logMstakeiede`
    pub fn mstakeiede(name: &str, l: &str) -> String {
        format!(
            "{}の<B>{l}</B>は帰るべき家がないために旅に出ました。",
            msg::island(name)
        )
    }

    /// `logMstakeokaeri`
    pub fn mstakeokaeri(name: &str, l: &str, point: &str, t: &str) -> String {
        format!(
            "{}の<B>{l}</B>が{}の<B>{t}</B>に帰ってきました。おつかれさま。",
            msg::island(name),
            n(point)
        )
    }

    /// `logMsAttackt`
    pub fn ms_attackt(name: &str, m: &str, attack: i64, counter: i64, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が{}の<B>{t}</B>を攻撃し{}のダメージを与え{}のダメージを受けました。",
            msg::island(name),
            n(tp),
            d(&attack.to_string()),
            d(&counter.to_string())
        )
    }

    /// `logMsAttackmika`
    pub fn ms_attackmika(name: &str, m: &str, t: &str) -> String {
        format!(
            "{}の<B>{m}</B>と<B>{t}</B>の戦いは伝説となり、島民は<B>幸福の女神像</B>を建造しました。",
            msg::island(name)
        )
    }

    /// `logMonsAttack`
    pub fn mons_attack(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が{}の<B>{t}</B>に向かって炎を吐きつけました。",
            ia(name, point),
            n(tp)
        )
    }

    /// `logMonsAttackt`
    pub fn mons_attackt(name: &str, m: &str, point: &str, t: &str, tp: &str) -> String {
        format!(
            "{}の<B>{m}</B>が{}の<B>{t}</B>を攻撃しました。",
            ia(name, point),
            n(tp)
        )
    }

    /// `lognewMonsterBorn`
    pub fn new_monster_born(name: &str, point: &str) -> String {
        format!("{}に<B>スライム</B>が分裂しました。", ia(name, point))
    }

    /// `lognewKaiju`
    pub fn new_kaiju(name: &str, m: &str, point: &str) -> String {
        format!("{}に<B>{m}</B>が助けに来ました。", ia(name, point))
    }

    /// `logShoukan`
    pub fn shoukan(name: &str, by: &str, m: &str, point: &str) -> String {
        format!(
            "<B>{by}</B>は{}に<B>{m}</B>を{}しました。",
            ia(name, point),
            d("召喚")
        )
    }

    /// `logRottenSeaBorn`
    pub fn rotten_sea_born(name: &str, point: &str) -> String {
        format!(
            "{}に<B>王蟲</B>から<B>腐海</B>が生まれました。",
            ia(name, point)
        )
    }

    /// `logNuginugi`
    pub fn nuginugi(name: &str, point: &str) -> String {
        format!("{}に<B>王蟲</B>が脱皮しました。", ia(name, point))
    }

    /// `logMonsFire`
    pub fn mons_fire(name: &str, l: &str, point: &str, m: &str) -> String {
        format!(
            "{}の<B>{l}</B>が<B>{m}</B>による衝撃波で壊滅しました。",
            ia(name, point)
        )
    }

    /// `logMonsCold`
    pub fn mons_cold(name: &str, l: &str, point: &str, m: &str) -> String {
        format!(
            "{}の<B>{l}</B>は<B>{m}</B>を取り巻く冷気により凍てつきました。",
            ia(name, point)
        )
    }

    /// `logMonsMoveDefence`
    pub fn mons_move_defence(name: &str, l: &str, point: &str, m: &str) -> String {
        format!(
            "<B>{m}</B>が{}の<B>{l}</B>へ到達、<B>{l}の自爆装置が作動！！</B>",
            ia(name, point)
        )
    }

    /// `logMonsMineKill` / `logMonsMineDead` / `logMonsMineHit` (`end` だけが違う)
    pub fn mons_mine(name: &str, l: &str, point: &str, m: &str, end: &str) -> String {
        format!(
            "<B>怪獣{m}</B>が{}の<B>{l}</B>を踏んで爆発、<B>怪獣{m}</B>は{end}",
            ia(name, point)
        )
    }

    /// `logMonsMove`
    pub fn mons_move(name: &str, l: &str, point: &str, m: &str) -> String {
        format!(
            "{}の<B>{l}</B>が<B>{m}</B>に踏み荒らされました。",
            ia(name, point)
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn perl_number_strings() {
        assert_eq!(perl_num_str(0.5), "0.5");
        assert_eq!(perl_num_str(-0.25), "-0.25");
        assert_eq!(perl_num_str(1.0 / 3.0), "0.333333333333333");
        assert_eq!(perl_num_str(0.000_012_5), "1.25e-05");
        assert_eq!(perl_num_str(1235f64.sin()), "-0.346734279815226");
    }

    #[test]
    fn seqnum_matches_perl() {
        // perl -e 'for $t (0..40){ print substr(sin($t+1234),-2,1)+0, "," }'
        let want = [
            9, 2, 8, 6, 8, 0, 7, 9, 0, 5, 5, 7, 5, 3, 9, 1, 0, 4, 9, 3, 9, 2, 7, 3, 5, 5, 4, 3, 8,
            8, 5, 9, 8, 1, 0, 3, 5, 4, 1, 8, 9,
        ];
        let got: Vec<i64> = (0..=40).map(seqnum).collect();
        assert_eq!(got, want);
    }
}
