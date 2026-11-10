//! ターン処理 (`hako-turn.cgi` の `turnMain` とその下請け)。
//!
//! Perl 版の処理順をそのまま再現する。まだ移植していない段階 (地形ごとの処理、
//! 計画の大半、島全体の処理、ハコオク・toto など) は、該当する場所にコメントで
//! 印を付けてある。詳しくは docs/PORTING.md を参照。

pub(crate) mod command;
mod estimate;
pub(crate) mod hex;
mod income;
mod ranking;

#[cfg(test)]
mod perl_compat_tests;

use std::collections::HashMap;

use rand::RngCore;

use crate::config::GameConfig;
use crate::log::{TurnLog, msg};
use crate::model::{GameState, Island};
use crate::perl::{self, Captures};
use crate::tables::PRIZE_NAMES;

pub use estimate::monster_spec;

/// ターン処理中だけ島に持たせる値。
///
/// Perl 版では島のハッシュに一時的に書き込んでいた値で、ファイルには保存されない。
/// Perl 版は 1 リクエスト = 1 プロセスなので、ターンの開始時には必ず空 (0) だった。
/// 移植版でもターンの開始時に初期化する。
///
/// `estimate` が 1 ターンに 2 回呼ばれるため、1 回目の値を 2 回目が読む箇所がある
/// (`shouhi` の積み増し、`oil`、`h10` など)。
#[derive(Debug, Clone, Default, PartialEq)]
#[allow(missing_docs)]
pub struct IslandScratch {
    /// 電力消費量 (`estimate` のたびに積み増される)
    pub shouhi: i64,
    /// 電力供給量
    pub ene: i64,
    /// 電力の余り (コンデンサへの充電に使う)。Perl 版では小数になることがある
    pub sabun: f64,
    pub con99: i64,
    pub factory1: i64,
    pub factory2: i64,
    pub factoryt: i64,
    pub oil: i64,
    pub bas: i64,
    pub kyu: i64,
    pub ky2: i64,
    pub zoo: i64,
    pub amu: i64,
    pub par: i64,
    pub riz: i64,
    pub fim: i64,
    pub rot: i64,
    pub sci: i64,
    pub sba: i64,
    pub pro: i64,
    pub kin: i64,
    pub nto: i64,
    pub m17: i64,
    pub m26: i64,
    pub m27: i64,
    pub m73: i64,
    pub m74: i64,
    pub m75: i64,
    pub m76: i64,
    pub m77: i64,
    pub m78: i64,
    pub m79: i64,
    pub m84: i64,
    pub m93: i64,
    pub m96: i64,
    pub m97: i64,
    pub m98: i64,
    pub m99: i64,
    pub m100: i64,
    pub m101: i64,
    pub c11: i64,
    pub c13: i64,
    pub c21: i64,
    pub c23: i64,
    pub c28: i64,
    pub co0: i64,
    pub co01: i64,
    pub co1: i64,
    pub co2: i64,
    pub co3: i64,
    pub co4: i64,
    pub co5: i64,
    pub co6: i64,
    pub co7: i64,
    pub co8: i64,
    pub co77: i64,
    pub co78: i64,
    pub co79: i64,
    pub co80: i64,
    pub co99: i64,
    /// `$island->{'co95'}`。Perl 版では一度も代入されない (estimate は局所変数にしか数えない) ので
    /// 常に 0 で、これを見る計画の値引きは働かない。それも再現する
    pub co95: i64,
    pub yaku: i64,
    pub tet: i64,
    pub hot: i64,
    pub hou: i64,
    pub tai: i64,
    pub shu: i64,
    pub sin: i64,
    pub jin: i64,
    pub h10: i64,
    pub h11: i64,
    pub gyo: i64,
    pub htf: i64,
    pub shtf: i64,
    pub ownf: i64,
    pub ownfe: i64,
    pub tra: i64,
    pub tra1: i64,
    pub tra2: i64,
    pub trainmoney: i64,
    pub trainmoney2: i64,
    pub fukeikimoney: i64,
    pub incomemoney: i64,
    pub monsterlive2: i64,
    pub unemployed: i64,
    pub kachiten: i64,
    pub kachitent: i64,
    pub shoritu: i64,
    pub styusho: i64,
    pub teamforce: i64,
    pub force: i64,
    pub uni: i64,
    pub tuni: i64,
    pub auc0c: i64,
    pub auc5c: i64,
    /// 部門賞の数 (総合ポイントに加算される)
    pub bumon: i64,
    /// 台風が来た (風力・水力発電が増え、太陽光が止まる)
    pub typhoon: bool,
    /// 無人島になった・放棄された
    pub dead: bool,
    pub old_pop: i64,
    pub old_money: i64,
    pub old_pts: i64,
    /// アナザーモードで doEachHex の間だけ退避する資金
    pub amarimoney: i64,
    /// 誘致活動中 (doCommand の誘致活動が立てる)
    pub propaganda: i64,
    pub hcsankaflag: i64,
    /// このターンに漏電・小彗星が起きた数
    pub roudenflag: i64,
    /// 毒消し薬が売り切れた
    pub urikireflag: i64,
    /// doEachHex の系統ごとの値
    pub hex: hex::Scratch,
    /// doCommand の系統ごとの値
    pub command: command::Scratch,
    /// 地形の値の小数部分 (座標 → 小数)。Perl 版はコンデンサの充電で値が小数になり、
    /// ターンの間はそのまま使われる (保存時に切り捨て)。地形の値を書き換えるときは
    /// `hex::town::set` などを使って消すこと
    pub land_frac: std::collections::HashMap<(usize, usize), f64>,
}

/// Perl 版のグローバル変数のうち、島をまたいで値が持ち越されるもの。
///
/// どれも「カンマ区切りの複合値を正規表現で分解して代入する先」で、
/// マッチに失敗したときや、別の関数が同じ変数名を使っているときに前の島の値が残る。
#[derive(Debug, Default)]
pub(crate) struct Globals {
    /// `$s00`..`$s30` (`etc5`、政策)
    pub etc5: Captures<31>,
    /// `$sto`, `$std`, `$stk`, `$stwin`, ... (`eisei4`、Hakoniwa Cup のチーム)
    pub eisei4: Captures<11>,
    /// `$mshp`, `$msap`, ... (`eisei5`、マスコット)
    pub eisei5: Captures<7>,
    /// `$unimika`, `$unishuto`, ... (`eisei6`、ユニーク地形)
    pub eisei6: Captures<12>,
    /// `$z0`..`$z30` (動物園の動物の数)。`doCommand` の動物園系の計画が 31 個すべてに代入し、
    /// `estimate` は `$z00`..`$z09` (別の変数) と `$z10`..`$z30` (こちらと同じ変数) に代入する
    pub zoo: [i64; 31],
    /// `estimate` の `$z00`..`$z09`
    pub zoo_estimate_low: [i64; 10],
    /// `$toto1`..`$toto7` (`etc8`)
    pub etc8: Captures<7>,
    pub auc0: Captures<5>,
    pub auc4: Captures<3>,
    pub auc5: Captures<5>,
    pub auc6: Captures<3>,
    pub auc9: Captures<5>,
    /// `$factory1`, `$factory2`, `$co0`, ... (`income` が `factory` を分解する先)
    pub factory: Captures<10>,
    /// doEachHex で使うグローバル変数
    pub hex: hex::HexGlobals,
    /// doCommand だけで使うグローバル変数
    pub command: command::CommandGlobals,
}

/// ターン処理全体で共有する状態
pub(crate) struct TurnContext<'a> {
    pub config: &'a GameConfig,
    pub rng: &'a mut dyn RngCore,
    /// 処理中のターン番号 (`$HislandTurn`、加算後)
    pub turn: i64,
    pub log: TurnLog,
    /// 島の全座標をシャッフルしたもの (`@Hrpx`, `@Hrpy`)
    pub points: Vec<(usize, usize)>,
    /// 島 ID → 配列の位置 (`%HidToNumber`)。
    /// Perl 版はデータの読み込み時に作ったきり更新しないので、途中で並べ替えた後は
    /// ずれた位置を指す。それも再現するため、ターン開始時の値を持ち続ける
    pub id_to_number: HashMap<i64, usize>,
    /// 島の数 (`$HislandNumber`)。ターンの最後に無人島を除くまでは変わらない
    pub island_number: usize,
    pub globals: Globals,
    /// ハコオクを休んでいる島の数 (`$oyasumiritu`)。`estimate` のたびに数えるので 2 重に数えられる
    pub oyasumiritu: i64,
}

impl TurnContext<'_> {
    pub fn random(&mut self, n: i64) -> i64 {
        perl::random(self.rng, n)
    }

    /// `rand($n)` (小数)。Perl の `rand(0)` は `rand(1)` と同じ
    pub fn rand_f64(&mut self, n: f64) -> f64 {
        use rand::Rng;
        let n = if n == 0.0 { 1.0 } else { n };
        self.rng.r#gen::<f64>() * n
    }
}

/// ターン処理の結果
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TurnReport {
    /// 処理したターン番号
    pub turn: i64,
    /// このターンの保存前にバックアップを取るべきか (`$HbackupTurn`)
    pub backup_due: bool,
}

/// `makeRandomPointArray`
fn make_random_point_array(rng: &mut dyn RngCore, size: usize) -> Vec<(usize, usize)> {
    let mut points: Vec<(usize, usize)> = (0..size)
        .flat_map(|y| (0..size).map(move |x| (x, y)))
        .collect();
    shuffle_like_perl(rng, &mut points);
    points
}

/// `randomArray`: 0..n を並べ替えたもの。n が 0 なら `[0]` (Perl 版と同じ)
fn random_array(rng: &mut dyn RngCore, n: usize) -> Vec<usize> {
    let mut list: Vec<usize> = (0..n.max(1)).collect();
    shuffle_like_perl(rng, &mut list);
    list
}

/// Perl 版のシャッフル (`for ($i = $n; --$i; ) { $j = int(rand($i+1)); ... }`)
fn shuffle_like_perl<T>(rng: &mut dyn RngCore, list: &mut [T]) {
    for i in (1..list.len()).rev() {
        let j = perl::random(rng, i as i64 + 1) as usize;
        if i != j {
            list.swap(i, j);
        }
    }
}

/// 1 ターン進める (`turnMain`)。
///
/// 時刻の判定はしない (呼び出し側で [`crate::model::World::turn_due`] を見る)。
pub fn run_turn(state: &mut GameState, config: &GameConfig, rng: &mut dyn RngCore) -> TurnReport {
    let world = &mut state.world;

    // 最終更新時間を更新
    world.last_time += config.unit_time;

    // (ログファイルを後ろにずらす処理は、最後にまとめて logs.turns に入れるときに行う)

    let points = make_random_point_array(rng, config.island_size);
    world.turn += 1;

    let n = world.islands.len();
    let id_to_number = world
        .islands
        .iter()
        .enumerate()
        .map(|(i, island)| (island.id, i))
        .collect();
    for island in world.islands.iter_mut() {
        *island.scratch = IslandScratch::default();
    }

    // 順番決め
    let order: Vec<usize> = random_array(rng, n)
        .into_iter()
        .filter(|&i| i < n)
        .collect();

    let mut ctx = TurnContext {
        config,
        rng,
        turn: world.turn,
        log: TurnLog::default(),
        points,
        id_to_number,
        island_number: n,
        globals: Globals::default(),
        oyasumiritu: 0,
    };
    let islands = &mut world.islands;

    // 収入、消費フェイズ
    for &i in &order {
        estimate::estimate(&mut ctx, islands, i);
        income::income(&mut ctx, &mut islands[i]);
        let island = &mut islands[i];
        island.scratch.old_pop = island.pop;
        island.scratch.old_money = island.money;
        island.scratch.old_pts = island.pts;
    }

    // コマンド処理 (戻り値が「実行した」になるまで繰り返す)
    for &i in &order {
        while !command::do_command(&mut ctx, islands, i) {}
    }

    // 成長および単ヘックス災害
    for &i in &order {
        hex::do_each_hex(&mut ctx, islands, i);
    }

    // TODO(フェーズ4): 島全体処理 (doIslandProcess, doIslandunemployed)
    // TODO(フェーズ6): Hakoniwa Cup のシード (ターン % 100 == 41)

    // 部門賞
    ranking::award_departments(islands);

    // 死滅判定。部門賞の並べ替えの後なので、order[i] はターン開始時とは別の島を指す (Perl 版のまま)
    let mut remain = n;
    for &i in &order {
        estimate::estimate(&mut ctx, islands, i);
        let island = &mut islands[i];
        if island.scratch.dead {
            island.pop = 0;
            island.pts = 0;
            remain -= 1;
        } else if island.pop == 0 {
            // estimate の最後で pop == 0 なら dead になるので、ここには来ない (Perl 版のまま)
            island.scratch.dead = true;
            island.pts = 0;
            remain -= 1;
            let (id, name) = (island.id, island.name.clone());
            ctx.log.out(ctx.turn, msg::dead(&name), Some(id), None);
            ctx.log.history(ctx.turn, msg::dead_history(&name));
        }
    }

    // TODO(フェーズ6): ハコオクの順位と賞品 (ターン杯のターン)

    // ポイント順にソート
    ranking::sort_by_pts(islands);

    // ターン杯
    if config.turn_prize_unit > 0 && ctx.turn % config.turn_prize_unit == 0 && !islands.is_empty() {
        turn_prize(&mut ctx, &mut islands[0]);
    }

    // TODO(フェーズ6): ハコオクの出品の入れ替えと状態の更新

    // 島数カット (無人島はポイント 0 で末尾に並んでいる)
    islands.truncate(remain);

    // TODO(フェーズ6): toto、Hakoniwa Cup toto、Numbers3、Numbers4、Hakoniwa Cup の参加数

    if !config.survey.enabled {
        world.survey_votes = [0; 5];
    }

    let turn = ctx.turn;
    let backup_due = config.backup_every_turns > 0 && turn % config.backup_every_turns == 0;

    // ログ書き出し (Perl 版の負荷計測ログは出さない)
    let (entries, history) = ctx.log.flush();
    let logs = &mut state.logs;
    logs.turns.insert(0, entries);
    logs.turns.truncate(config.log_max + 1);
    logs.history.extend(history);
    trim_front(&mut logs.history, config.history_max);
    // Hakoniwa Cup のログ (Perl 版は logHcup で hakojima.lhc に直接追記する)
    logs.hcup.append(&mut ctx.globals.hex.stadium.hcup_log);
    trim_front(&mut logs.hcup, config.hcup_log_max);
    trim_front(&mut logs.auction, 10);

    TurnReport { turn, backup_due }
}

/// 古いものから削って `max` 件にする (`logHistoryTrim` など)
fn trim_front<T>(v: &mut Vec<T>, max: usize) {
    if v.len() > max {
        v.drain(..v.len() - max);
    }
}

/// ターン杯 (`turnMain` の `$HislandTurn % $HturnPrizeUnit == 0` の部分)
fn turn_prize(ctx: &mut TurnContext, island: &mut Island) {
    let unit = &ctx.config.units.money;
    let prize_name = format!("{}{}", ctx.turn, PRIZE_NAMES[0]);

    let value = ctx.turn + ctx.random(1001);
    island.money += value;
    let amount = format!("{value}{unit}");
    ctx.log.out(
        ctx.turn,
        msg::prize(&island.name, &prize_name),
        Some(island.id),
        None,
    );
    ctx.log.history(
        ctx.turn,
        msg::prize_history(&island.name, &prize_name, &amount),
    );

    for (count, building) in [(island.scratch.sin, "神殿"), (island.scratch.jin, "神社")] {
        if count > 0 {
            let value = ctx.turn + ctx.random(1001);
            island.money += value;
            let amount = format!("{value}{unit}");
            ctx.log.out(
                ctx.turn,
                msg::shrine_money(&island.name, building, &amount),
                Some(island.id),
                None,
            );
        }
    }
    island.prize.push_str(&format!("{},", ctx.turn));
}

#[cfg(test)]
pub(crate) mod tests_support {
    use crate::config::GameConfig;
    use crate::model::Island;

    pub fn island() -> Island {
        Island::blank(1, "テスト", &GameConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;
    use rand::rngs::StdRng;

    #[test]
    fn random_array_is_permutation() {
        let mut rng = StdRng::seed_from_u64(1);
        let mut a = random_array(&mut rng, 10);
        a.sort();
        assert_eq!(a, (0..10).collect::<Vec<_>>());
        assert_eq!(random_array(&mut rng, 0), vec![0]);
    }

    #[test]
    fn point_array_covers_island() {
        let mut rng = StdRng::seed_from_u64(1);
        let mut p = make_random_point_array(&mut rng, 12);
        assert_eq!(p.len(), 144);
        p.sort();
        p.dedup();
        assert_eq!(p.len(), 144);
    }

    #[test]
    fn trim_keeps_newest() {
        let mut v = vec![1, 2, 3, 4];
        trim_front(&mut v, 2);
        assert_eq!(v, [3, 4]);
    }
}
