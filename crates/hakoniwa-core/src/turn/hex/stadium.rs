//! 多目的スタジアム (Hakoniwa Cup)。
//!
//! Perl 版 `doEachHex` の `$landKind == $HlandKyujokai` の分岐 (hako-turn.cgi 9838–10972)。
//! ターン数を 100 で割った余りで大会の段階が決まり、スタジアムのマスを処理するたびに
//! ほかの島のチームと試合をする。チームの状態は `eisei4`
//! (`攻撃,守備,キーパー,勝,分,負,通算勝,通算分,通算負,優勝回数,勝ち上がり段階`) に入っている。
//!
//! | ターン % 100 | 処理 |
//! |---|---|
//! | 0 | 今季の成績を消して参加 (`stshoka = 1`)、参加島数 (`$stsanka`) を数える |
//! | 1–40 | 予選第１〜４戦 (段階 1〜4)。各戦の翌ターン (11, 21, 31, 41) は相手がいなければ不戦勝 |
//! | 42–46 | 段階が 6 未満なら敗退 (11)。段階 6 同士で準々決勝 (46 は不戦勝の判定も) |
//! | 47–49 | 段階 7 同士で準決勝 (49 は不戦勝の判定も) |
//! | 50–51 | 段階 8 同士で決勝 (51 は不戦勝で「とりあえずの優勝」) |
//! | 52 | 段階 9 (優勝) 以外は 10 に |
//!
//! 段階 10・11 のチームは毎ターン能力が 1 上がる。そのあと野球場と同じ収入とイベントがある。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - `$sto`, `$std`, ... (`eisei4` を分解した先、[`crate::turn::Globals::eisei4`]) と相手の
//!   `$tSto`, ... ([`Globals::t_eisei4`]) はグローバル変数。`eisei4` が形式に合わないと
//!   (負けた側の能力は負の数になりうる)、外側のブロックで最後に成功したマッチの `$1`.. が
//!   代入され、それを書き戻す。相手の島なら自島の `eisei4` の値、自島なら doEachHex 冒頭の
//!   `etc5` の値になる ([`Groups`])。`auc9` も同じ。
//! - 試合の判定に入った島は、相手の島の `eisei4` を (試合をしなくても) 毎回書き戻す。
//! - `$yosengameend` (このターンの試合数) は初期化されないので、ターン全体で数え続ける。
//! - 予選の 4 戦目の不戦勝 (41) で段階 5 になったチームは、42 の判定で敗退 (11) になる。
//! - 11, 21, 31 では不戦勝で段階が進んだあと、同じマスで次の戦の試合もしうる。
//! - 段階 0 のときの `$stsanka == 1` の判定は参加済みかどうかに関係なく毎マス行うので、
//!   最初の島にスタジアムが 2 つあると `stsankahantei` が 2 になる。
//! - `random($sto)` は能力が負の数でもそのまま `int(rand(1) * $sto)` を計算する。

use crate::land::{count_around, land_name};
use crate::log::tags::{self, wrap};
use crate::model::{Island, TurnMessage};
use crate::perl::{Captures, fields, join, trunc};
use crate::tables::LandKind as L;
use crate::turn::TurnContext;

use super::town::town_count;
use super::{Flow, HexRun, msg};

/// この系統で使う Perl 版のグローバル変数
#[derive(Debug, Default)]
pub struct Globals {
    /// `$stsanka` (Hakoniwa Cup の参加島数)。turnMain (開催ログ) と doIslandProcess
    /// (開会式の収入) も使う
    pub stsanka: i64,
    /// `$yosengameend` (このターンに行った試合の数。初期化されない)
    pub yosengameend: i64,
    /// `$tSto`, `$tStd`, ... (相手の島の `eisei4` を分解した先)
    pub t_eisei4: Captures<11>,
    /// `$tauc9a`..`$tauc9e` (相手の島の `auc9` を分解した先)
    pub tauc9: Captures<5>,
    /// `$yushouflag` (決勝で 1: 自島が優勝、2: 相手が優勝)。turnMain の HCtoto が使う
    pub yushouflag: i64,
    /// `$yushounamber`, `$yushounamber2` (優勝した島と準優勝の島の ID)。HCtoto が使う
    pub yushounamber: i64,
    pub yushounamber2: i64,
    /// `$hcturn`
    pub hcturn: i64,
    /// `logHcup` で `hakojima.lhc` に追記する行。run_turn の最後で `logs.hcup` に移す
    pub hcup_log: Vec<TurnMessage>,
}

/// この系統で使う、島に一時的に持たせる値 (`$island->{'...'}` で保存されないもの)
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Scratch {
    /// `stsankahantei` (この島で参加島数が 1 になった回数)。doIslandProcess の開会式が見る
    pub stsankahantei: i64,
}

// eisei4 の欄
const STO: usize = 0;
const STD: usize = 1;
const STK: usize = 2;
const WIN: usize = 3;
const DROW: usize = 4;
const LOSE: usize = 5;
const WINT: usize = 6;
const DROWT: usize = 7;
const LOSET: usize = 8;
const YUSHO: usize = 9;
const SHOKA: usize = 10;

/// 試合の種類
#[derive(Clone, Copy, PartialEq, Eq)]
enum Stage {
    /// 予選 (5 本と 3 本、引き分けあり、負けた側の能力が勝った側との差に応じて上がる)
    Yosen,
    /// 準々決勝・準決勝 (3 本ずつ、同点ならくじ、負けた側の能力が 30 上がる)
    Knockout {
        /// 負けたチームの段階
        lost: i64,
    },
    /// 決勝 (賞金 2 倍、優勝回数、負けた側の能力が 50 上がる)
    Final,
}

/// 多目的スタジアム
pub(super) fn kyujokai(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    h: &mut HexRun,
) -> Flow {
    let mut endm = 0;
    let seigen = if ctx.config.max_islands < 21 { 1 } else { 3 };
    let t = ctx.turn.rem_euclid(100);
    // 分岐に入った時点の $1.. は doEachHex の冒頭の etc5 のマッチのもの
    let entry = fields::<31>(&islands[idx].etc_raw[0])
        .map(|v| Groups(v.to_vec()))
        .unwrap_or_default();
    let own = fields::<11>(&islands[idx].eisei_raw[1]);
    let scope = own.map(|v| Groups(v.to_vec())).unwrap_or(entry);
    let mut st = own.unwrap_or_else(|| scope.take());

    if t == 0 {
        st[WIN] = 0;
        st[DROW] = 0;
        st[LOSE] = 0;
        st[SHOKA] = 1;
        let g = &mut ctx.globals.hex.stadium;
        let island = &mut islands[idx];
        if island.scratch.hcsankaflag == 0 {
            g.stsanka += 1;
            island.scratch.hcsankaflag = 1;
        }
        island.eisei_raw[1] = join(&st);
        if g.stsanka == 1 {
            island.scratch.hex.stadium.stsankahantei += 1;
        }
    }

    const YOSEN: [&str; 4] = ["予選第１戦", "予選第２戦", "予選第３戦", "予選第４戦"];
    for (n, game) in (1..=4).zip(YOSEN) {
        let first = (n - 1) * 10 + 1;
        if (first..=first + 9).contains(&t) {
            let ctl = RoundCtl {
                shoka: n,
                limit: seigen,
                stage: Stage::Yosen,
                game,
            };
            round(ctx, islands, idx, &scope, &mut st, &mut endm, &ctl);
        }
        if t == first + 10 {
            antiwin(ctx, islands, idx, &mut st, n, game);
        }
    }

    if (42..=46).contains(&t) {
        if st[SHOKA] < 6 {
            st[SHOKA] = 11;
            islands[idx].eisei_raw[1] = join(&st);
        }
        let ctl = RoundCtl {
            shoka: 6,
            limit: 1,
            stage: Stage::Knockout { lost: 12 },
            game: "準々決勝戦",
        };
        round(ctx, islands, idx, &scope, &mut st, &mut endm, &ctl);
    }
    if t == 46 {
        antiwin(ctx, islands, idx, &mut st, 6, "準々決勝戦");
    }
    if (47..=49).contains(&t) {
        let ctl = RoundCtl {
            shoka: 7,
            limit: 1,
            stage: Stage::Knockout { lost: 13 },
            game: "準決勝戦",
        };
        round(ctx, islands, idx, &scope, &mut st, &mut endm, &ctl);
    }
    if t == 49 {
        antiwin(ctx, islands, idx, &mut st, 7, "準決勝戦");
    }
    if (50..=51).contains(&t) {
        let ctl = RoundCtl {
            shoka: 8,
            limit: 1,
            stage: Stage::Final,
            game: "決勝戦",
        };
        round(ctx, islands, idx, &scope, &mut st, &mut endm, &ctl);
    }
    if t == 51 && st[SHOKA] == 8 {
        // 決勝の不戦勝
        st[WIN] += 1;
        st[WINT] += 1;
        st[SHOKA] += 1;
        st[YUSHO] += 1;
        let (id, name) = (islands[idx].id, islands[idx].name.clone());
        log_hc_antiwin(ctx, id, &name, "Hakoniwa Cup 決勝戦は不戦勝");
        let value = (st[WIN] * 3 + st[DROW]) * 1000 * 2;
        add_auc9(
            &mut ctx.globals.auc9,
            &mut islands[idx].auction.auc9,
            value,
            &scope,
        );
        let s = format!("Auction補助金{value}{}", ctx.config.units.money);
        log_hc_win(ctx, id, &name, &s);
        ctx.globals.hex.stadium.hcturn = trunc(ctx.turn as f64 / 100.0) * 100;
        log_hc_wintop(ctx, &name);
        islands[idx].eisei_raw[1] = join(&st);
    }
    if t == 52 && st[SHOKA] != 9 {
        st[SHOKA] = 10;
        islands[idx].eisei_raw[1] = join(&st);
    }
    if st[SHOKA] == 10 || st[SHOKA] == 11 {
        match ctx.random(3) {
            0 => st[STO] += 1,
            1 => st[STD] += 1,
            _ => st[STK] += 1,
        }
        islands[idx].eisei_raw[1] = join(&st);
    }
    ctx.globals.eisei4.0 = st;

    stadium_income(ctx, &mut islands[idx], h);
    Flow::Continue
}

/// その時点で見えている正規表現の `$1`, `$2`, ... (数値にしたもの)。
///
/// Perl の `$1` などは「いまのブロックから見て最後に成功したマッチ」の値で、ブロックを出ると
/// 元に戻る。`($a, $b) = ($1, $2)` はマッチに失敗すると、外側のブロックで最後に成功した
/// マッチの値を代入する (前回の `$a` が残るのではない)。
/// 分岐の入口で見えるのは doEachHex の冒頭の `etc5` のマッチ。それも失敗していた場合
/// (呼び出し元のマッチが見える) は再現せず、未定義 (0) として扱う
#[derive(Debug, Clone, Default)]
struct Groups(Vec<i64>);

impl Groups {
    fn take<const N: usize>(&self) -> [i64; N] {
        std::array::from_fn(|i| self.0.get(i).copied().unwrap_or(0))
    }
}

/// 1 つの戦の条件
struct RoundCtl {
    /// 試合をする段階 (`$stshoka`)
    shoka: i64,
    /// このターンの試合数の上限 (`$yosengameend` と比べる)
    limit: i64,
    stage: Stage,
    /// ログに出す戦の名前 (`Hakoniwa Cup ` の後)
    game: &'static str,
}

/// 1 つの戦: 段階の合うほかの島を探して 1 試合する
fn round(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    scope: &Groups,
    st: &mut [i64; 11],
    endm: &mut i64,
    ctl: &RoundCtl,
) {
    let ready = |ctx: &TurnContext, s: i64, endm: i64| {
        s == ctl.shoka && endm == 0 && ctx.globals.hex.stadium.yosengameend < ctl.limit
    };
    if !ready(ctx, st[SHOKA], *endm) {
        return;
    }
    let id = islands[idx].id;
    for j in 0..ctx.island_number {
        if islands[j].id == id {
            continue;
        }
        // 形式に合わなければ、外側の最後のマッチの $1.. が入る (Perl 版のまま)
        let t_match = fields::<11>(&islands[j].eisei_raw[1]);
        let mut ts = t_match.unwrap_or_else(|| scope.take());
        let inner = t_match.map_or_else(|| scope.clone(), |v| Groups(v.to_vec()));
        if ready(ctx, ts[SHOKA], *endm) {
            play(ctx, islands, idx, j, &inner, st, &mut ts, endm, ctl);
        }
        // 試合をしなくても両方の eisei4 を書き戻す (Perl 版のまま)
        ctx.globals.hex.stadium.t_eisei4.0 = ts;
        islands[idx].eisei_raw[1] = join(st);
        islands[j].eisei_raw[1] = join(&ts);
    }
}

/// 試合 1 つ
#[allow(clippy::too_many_arguments)]
fn play(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    j: usize,
    scope: &Groups,
    st: &mut [i64; 11],
    ts: &mut [i64; 11],
    endm: &mut i64,
    ctl: &RoundCtl,
) {
    let (id, name) = (islands[idx].id, islands[idx].name.clone());
    let (t_id, t_name) = (islands[j].id, islands[j].name.clone());
    let knockout = ctl.stage != Stage::Yosen;

    let mut goal = 0;
    let mut tgoal = 0;
    for _ in 0..(if knockout { 3 } else { 5 }) {
        if ctx.random(st[STO]) > ctx.random(ts[STD]) && ctx.random(st[STO]) > ctx.random(ts[STK]) {
            goal += 1;
        }
    }
    for _ in 0..3 {
        if ctx.random(ts[STO]) > ctx.random(st[STD]) && ctx.random(ts[STO]) > ctx.random(st[STK]) {
            tgoal += 1;
        }
    }
    if knockout && goal == tgoal {
        if ctx.random(100) < 60 {
            goal += 1;
        } else {
            tgoal += 1;
        }
    }

    let money = ctx.config.units.money.clone();
    if goal != tgoal {
        // 勝った側 (w) と負けた側 (l)
        let mine_won = goal > tgoal;
        let (w, l) = if mine_won {
            (&mut *st, &mut *ts)
        } else {
            (&mut *ts, &mut *st)
        };
        w[WIN] += 1;
        w[WINT] += 1;
        if ctl.stage == Stage::Final {
            w[YUSHO] += 1;
        }
        match ctl.stage {
            Stage::Yosen => {
                w[SHOKA] += 1;
                l[SHOKA] += 1;
            }
            Stage::Knockout { lost } => {
                w[SHOKA] += 1;
                l[SHOKA] = lost;
            }
            Stage::Final => {
                w[SHOKA] += 1;
                l[SHOKA] = 14;
            }
        }
        l[LOSE] += 1;
        l[LOSET] += 1;
        ctx.globals.hex.stadium.yosengameend += 1;
        *endm += 1;

        let mut value = (w[WIN] * 3 + w[DROW]) * 1000;
        if ctl.stage == Stage::Final {
            value *= 2;
        }
        let (w_idx, w_id, w_name, l_id) = if mine_won {
            (idx, id, &name, t_id)
        } else {
            (j, t_id, &t_name, id)
        };
        if mine_won {
            add_auc9(
                &mut ctx.globals.auc9,
                &mut islands[w_idx].auction.auc9,
                value,
                scope,
            );
        } else {
            add_auc9(
                &mut ctx.globals.hex.stadium.tauc9,
                &mut islands[w_idx].auction.auc9,
                value,
                scope,
            );
        }
        let s = format!("Auction補助金{value}{money}");
        if ctl.stage == Stage::Final {
            let g = &mut ctx.globals.hex.stadium;
            g.yushouflag = if mine_won { 1 } else { 2 };
            g.yushounamber = w_id;
            g.yushounamber2 = l_id;
        }
        log_hc_win(ctx, w_id, w_name, &s);
        if ctl.stage == Stage::Final {
            ctx.globals.hex.stadium.hcturn = trunc(ctx.turn as f64 / 100.0) * 100;
            log_hc_wintop(ctx, w_name);
        }

        let stup = ctx.random(3);
        let (w, l) = if mine_won {
            (&*st, &mut *ts)
        } else {
            (&*ts, &mut *st)
        };
        match ctl.stage {
            Stage::Yosen => {
                let uphey = trunc((w[STO] + w[STD] + w[STK]) as f64 / 3.0);
                let tuphey = trunc((l[STO] + l[STD] + l[STK]) as f64 / 3.0);
                let uppoint = trunc((uphey - tuphey) as f64 / 2.0) + 5;
                let (a, b) = match stup {
                    0 => (STO, STD),
                    1 => (STD, STK),
                    _ => (STK, STO),
                };
                l[a] += uppoint;
                l[b] += uppoint;
            }
            Stage::Knockout { .. } | Stage::Final => {
                let up = if ctl.stage == Stage::Final { 50 } else { 30 };
                let a = match stup {
                    0 => STO,
                    1 => STD,
                    _ => STK,
                };
                l[a] += up;
            }
        }
    } else {
        // 引き分け (決勝トーナメントではくじで決まるので起きない)
        st[DROW] += 1;
        st[DROWT] += 1;
        ts[DROW] += 1;
        ts[DROWT] += 1;
        st[SHOKA] += 1;
        ts[SHOKA] += 1;
        ctx.globals.hex.stadium.yosengameend += 1;
        *endm += 1;
    }

    // logHCgame の $lName (landName) は文面に使われない
    let game = format!("Hakoniwa Cup {}", ctl.game);
    let vs = format!(
        "{}<B>VS</B>{} ⇒ <B>{goal}−{tgoal}</B>",
        wrap(tags::NAME, &format!("{name}島代表")),
        wrap(tags::NAME, &format!("{t_name}島代表")),
    );
    ctx.log.late(
        ctx.turn,
        format!("{}で<B>{game}</B>が行われました。{vs}", msg::island(&name)),
        Some(id),
        Some(t_id),
    );
    hcup(ctx, format!("{}、{vs}", wrap(tags::NAME, &game)));
}

/// 不戦勝 (予選・準々決勝・準決勝)
fn antiwin(
    ctx: &mut TurnContext,
    islands: &mut [Island],
    idx: usize,
    st: &mut [i64; 11],
    shoka: i64,
    game: &str,
) {
    if st[SHOKA] != shoka {
        return;
    }
    st[WIN] += 1;
    st[WINT] += 1;
    st[SHOKA] += 1;
    let (id, name) = (islands[idx].id, islands[idx].name.clone());
    log_hc_antiwin(ctx, id, &name, &format!("Hakoniwa Cup {game}は不戦勝"));
    islands[idx].eisei_raw[1] = join(st);
}

/// `auc9` にハコオクの補助金を足す (`$auc9c += $value` と `$auc9a` の計算し直し)。
/// 分解先はグローバル変数。形式に合わなければ外側の最後のマッチの `$1`..`$5` を使う
fn add_auc9(caps: &mut Captures<5>, auc9: &mut String, value: i64, scope: &Groups) {
    let mut a = fields::<5>(auc9).unwrap_or_else(|| scope.take());
    a[2] += value;
    let c2 = trunc(a[2] as f64 / 10000.0);
    a[0] = a[1] + c2 + a[3] + a[4];
    caps.0 = a;
    *auc9 = join(&a);
}

/// `logHcup` (`hakojima.lhc` に追記)
fn hcup(ctx: &mut TurnContext, message: String) {
    let turn = ctx.turn;
    ctx.globals
        .hex
        .stadium
        .hcup_log
        .push(TurnMessage { turn, message });
}

fn team(name: &str) -> String {
    wrap(tags::NAME, &format!("{name}島代表"))
}

/// `logHCwin` (`$cName` は文面に使われない)
fn log_hc_win(ctx: &mut TurnContext, id: i64, name: &str, s: &str) {
    ctx.log.late(
        ctx.turn,
        format!("{}は、<B>{s}</B>を獲得しました。", team(name)),
        Some(id),
        None,
    );
}

/// `logHCwintop` (`$hcturn` 回の優勝)
fn log_hc_wintop(ctx: &mut TurnContext, name: &str) {
    let hcturn = ctx.globals.hex.stadium.hcturn;
    let m = format!("{}、<B>Hakoniwa Cup{hcturn}優勝！</B>", team(name));
    ctx.log.history(ctx.turn, m.clone());
    hcup(ctx, m);
}

/// `logHCantiwin`
fn log_hc_antiwin(ctx: &mut TurnContext, id: i64, name: &str, game: &str) {
    ctx.log.late(
        ctx.turn,
        format!(
            "{}は<B>対戦チーム</B>がいないため<B>{game}</B>となりました。",
            team(name)
        ),
        Some(id),
        None,
    );
    hcup(
        ctx,
        format!(
            "{}は<B>対戦チーム</B>がいないため<B>{game}</B>。",
            team(name)
        ),
    );
}

/// 野球場改の収入とイベント (野球場と同じ計算)
fn stadium_income(ctx: &mut TurnContext, island: &mut Island, h: &HexRun) {
    let (x, y) = (h.x, h.y);
    let (id, turn) = (island.id, ctx.turn);
    let l_name = land_name(h.land_kind, h.lv);
    let point = h.point();
    if !(island.scratch.kyu > 1 || island.scratch.amu > 1) {
        let nt = town_count(island, x, y) - 6;
        let ns = 1 + 2 * count_around(&island.map, x as i64, y as i64, L::Park, 19);
        let nr = 1 + 3 * count_around(&island.map, x as i64, y as i64, L::Umiamu, 19);
        let nu = 10 + ctx.random(10);
        let mut value = nt * nu * ns * nr + trunc(island.pop as f64 / 25.0);
        if island.scratch.shouhi > island.scratch.ene {
            value = trunc(value as f64 / 5.0);
        }
        if value > 0 {
            island.money += value;
            let s = format!("{value}{}", ctx.config.units.money);
            ctx.log.out(
                turn,
                format!(
                    "{}の<B>{l_name}</B>から、<B>{s}</B>の収益が上がりました。",
                    msg::island_at(&island.name, &point)
                ),
                Some(id),
                None,
            );
        }
    }

    // イベント判定
    if ctx.random(100) < 10 {
        let value = trunc(island.pop as f64 / 50.0) * 10;
        island.food -= value;
        if value > 0 {
            let s = format!("{value}{}", ctx.config.units.food);
            ctx.log.out(
                turn,
                format!(
                    "{}の<B>{l_name}</B>でイベントが開催され、<B>{s}</B>の食料が消費されました。",
                    msg::island_at(&island.name, &point)
                ),
                Some(id),
                None,
            );
        }
    }
}
