//! ゲームのデータモデル。
//!
//! Perl 版では島のデータがハッシュに入っていて、いくつものファイル
//! (`hakojima.dat`, `howner.dat`, `ips.dat`, `auction.dat`, `an.dat`, `island.N`) に
//! 分けて保存されていた。移植版ではこれを 1 つの [`GameState`] にまとめる。
//!
//! 意味のわかっていない項目 (`eis1` など) は、ターン処理を移植するまで
//! Perl 版の名前と型のまま保持する。Perl 側で `int()` を通して読んでいた項目は `i64`、
//! そのまま読んでいた項目 (カンマ区切りの複合値など) は `String` にしてある。

use std::sync::Arc;

use serde::{Deserialize, Serialize};

use crate::config::{GameConfig, HideMoneyMode};
use crate::tables::{CommandKind, LandKind};
use crate::turn::IslandScratch;
use crate::turn_log::TurnLog;

/// 保存データの形式バージョン
pub const FORMAT_VERSION: u32 = 1;

/// 保存・読み込みの単位になる、ゲーム全体の状態
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct GameState {
    pub format_version: u32,
    pub world: World,
    pub logs: Logs,
}

impl GameState {
    /// 新しいゲームを作る (`hako-mente.cgi` の `newMode` 相当)。
    /// 開始時刻はターンの区切りに切り捨てる。
    pub fn new_game(now: i64, config: &GameConfig) -> Self {
        let unit = config.unit_time.max(1);
        Self {
            format_version: FORMAT_VERSION,
            world: World {
                turn: 1,
                last_time: now - now.rem_euclid(unit),
                next_id: 1,
                islands: Vec::new(),
                auction_lots: Vec::new(),
                survey_votes: [0; 5],
            },
            logs: Logs::default(),
        }
    }
}

/// 全島に共通の情報 (`hakojima.dat` の先頭 4 行など)
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct World {
    /// ターン数 (`$HislandTurn`)
    pub turn: i64,
    /// 最終更新時刻 (UNIX 秒) (`$HislandLastTime`)
    pub last_time: i64,
    /// 次に割り当てる島 ID (`$HislandNextID`)
    pub next_id: i64,
    /// 島の一覧。Perl 版と同じく、保存されている順 (= 順位順) に並ぶ
    pub islands: Vec<Island>,
    /// ハコオクの出品 3 枠 (`auction.dat` 先頭 3 行、`"品番,..."` のカンマ区切り)
    pub auction_lots: Vec<String>,
    /// アンケートの集計 (`an.dat` 先頭 5 行)
    pub survey_votes: [i64; 5],
}

impl World {
    pub fn island_by_id(&self, id: i64) -> Option<&Island> {
        self.islands.iter().find(|i| i.id == id)
    }

    pub fn island_by_id_mut(&mut self, id: i64) -> Option<&mut Island> {
        self.islands.iter_mut().find(|i| i.id == id)
    }

    /// 次のターンを処理すべき時刻
    pub fn next_turn_time(&self, config: &GameConfig) -> i64 {
        self.last_time + config.unit_time
    }

    /// `now` の時点でターン処理が必要か (`readIslandsFile` の判定と同じ)
    pub fn turn_due(&self, now: i64, config: &GameConfig) -> bool {
        now - self.last_time >= config.unit_time
    }
}

/// 島ひとつ分のデータ
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Island {
    // ---- hakojima.dat ---------------------------------------------------
    /// 島の名前 (「島」は付かない)
    pub name: String,
    /// 島 ID
    pub id: i64,
    /// スコア (名前の行に `名前,スコア` の形で保存されていた)
    pub score: i64,
    /// 受賞 (`"ターン杯の受賞ターン,...,"` などを含む複合値)
    pub prize: String,
    /// 連続資金繰り数
    pub absent: i64,
    /// コメント
    pub comment: String,
    /// 暗号化済みパスワード (Perl の `crypt()` の結果)
    pub password: String,
    /// 資金
    pub money: i64,
    /// 食料
    pub food: i64,
    /// 人口
    pub pop: i64,
    /// 広さ
    pub area: i64,
    /// 農場の規模
    pub farm: i64,
    /// 工場の規模など (カンマ区切りの複合値)
    pub factory: String,
    /// 採掘場の規模
    pub mountain: i64,
    /// ポイント
    pub pts: i64,
    /// 用途未解析 (`eis1`〜`eis7`)
    pub eis: [i64; 7],
    /// toto の予想 (`eis8`)
    pub eis8: String,
    /// 怪獣退治数 (`taiji`)
    pub taiji: i64,
    /// コメントの前に表示される名前 (`onm`)
    pub onm: String,
    /// 怪獣出現数 (`monsterlive`)
    pub monster_live: i64,
    /// 出現している怪獣の種類 (`monsterlivetype`)
    pub monster_live_type: i64,
    /// 人工衛星 (`eisei1`, `eisei2`)
    pub eisei: [i64; 2],
    /// 人工衛星 (`eisei3`〜`eisei6`、Perl 版では文字列のまま扱われていた)
    pub eisei_raw: [String; 4],

    // ---- howner.dat -----------------------------------------------------
    /// `id1` (用途未解析)
    pub id1: i64,
    /// オーナー名
    pub owner_name: String,
    /// toto 予想 (`totoyoso`)
    pub totoyoso: String,
    /// toto 予想 2 (`totoyoso2`)
    pub totoyoso2: String,
    /// `kei`, `rena`, `momotan`, `fore`, `pika`, `hamu`, `monta`, `tare`, `zipro`, `leje`。
    /// わかっている用途: `fore`=木の数, `pika`=利益, `hamu`=人口増加, `monta`=ポイント増加,
    /// `tare`=ニワトリ(万羽), `zipro`/`leje`=家畜(万頭)。
    pub owner_stats: OwnerStats,

    // ---- ips.dat --------------------------------------------------------
    /// `ipname` (島名の控え)
    pub ip_name: String,
    /// アクセス元 IP など (`ip0`〜`ip7`)
    pub ip: [String; 8],
    /// カウンタ (`ip8`, `ip9`)
    pub ip_counters: [i64; 2],
    /// `etc0`〜`etc4` (`etc0`=移動距離 km)
    pub etc_num: [i64; 5],
    /// `etc5`〜`etc9` (カンマ区切りの複合値)
    pub etc_raw: [String; 5],

    // ---- auction.dat ----------------------------------------------------
    /// `auc0`〜`auc9`。`auc1`〜`auc3` は数値、それ以外はカンマ区切りの複合値
    pub auction: AuctionState,

    // ---- an.dat ---------------------------------------------------------
    /// アンケート投票フラグ (`anflag`)
    pub survey_flag: i64,

    // ---- island.N -------------------------------------------------------
    pub map: IslandMap,
    /// 開発計画 (`$HcommandMax` 件)
    pub commands: Vec<PlannedCommand>,
    /// ローカル掲示板 (Perl 版の形式 `種別<発言島<ID>名前>本文` のまま)
    pub lbbs: Vec<String>,

    /// ターン処理中だけ使う値 (Perl 版で島のハッシュに一時的に入れていたもの)。保存しない
    #[serde(skip)]
    pub scratch: Box<IslandScratch>,
}

impl Island {
    /// 値がすべて空の島 (海だけの地図、計画はすべて「資金繰り」)。
    /// 複合値の欄は、Perl 版が読み込み時に補う既定値にしておく
    pub fn blank(id: i64, name: &str, config: &GameConfig) -> Self {
        Self {
            name: name.to_string(),
            id,
            score: 0,
            prize: String::new(),
            absent: 0,
            comment: String::new(),
            password: String::new(),
            money: 0,
            food: 0,
            pop: 0,
            area: 0,
            farm: 0,
            factory: "0,0,0,0,0,0,0,0,0,0".into(),
            mountain: 0,
            pts: 0,
            eis: [0; 7],
            eis8: String::new(),
            taiji: 0,
            onm: String::new(),
            monster_live: 0,
            monster_live_type: 0,
            eisei: [0; 2],
            eisei_raw: [
                "0,0,0,0,0".into(),
                "0,0,0,0,0,0,0,0,0,0,0".into(),
                "0,0,0,0,0,0,0".into(),
                "0,0,0,0,0,0,0,0,0,0,0,0".into(),
            ],
            id1: 0,
            owner_name: String::new(),
            totoyoso: String::new(),
            totoyoso2: String::new(),
            owner_stats: OwnerStats::default(),
            ip_name: name.to_string(),
            ip: Default::default(),
            ip_counters: [0; 2],
            etc_num: [0; 5],
            etc_raw: [
                vec!["0"; 31].join(","),
                vec!["0"; 31].join(","),
                "0,0,0".into(),
                "0,0,0,0,0,0,0".into(),
                "0,0,0,0,0,0,0".into(),
            ],
            auction: AuctionState {
                auc0: "0,0,0,0,0".into(),
                auc4: "0,0,0".into(),
                auc5: "0,0,0,0,0".into(),
                auc6: "0,0,0".into(),
                auc7: "0".into(),
                auc8: "0".into(),
                auc9: "0,0,0,0,0".into(),
                ..Default::default()
            },
            survey_flag: 1,
            map: IslandMap::new_sea(config.island_size),
            commands: vec![
                PlannedCommand {
                    kind: CommandKind::DoNothing as u16,
                    ..Default::default()
                };
                config.command_max
            ],
            lbbs: vec!["0<<0>>".to_string(); config.lbbs.max],
            scratch: Default::default(),
        }
    }
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct OwnerStats {
    pub kei: i64,
    pub rena: i64,
    pub momotan: i64,
    pub fore: i64,
    pub pika: i64,
    pub hamu: i64,
    pub monta: i64,
    pub tare: i64,
    pub zipro: i64,
    pub leje: i64,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct AuctionState {
    pub auc0: String,
    pub auc1: i64,
    pub auc2: i64,
    pub auc3: i64,
    pub auc4: String,
    pub auc5: String,
    pub auc6: String,
    pub auc7: String,
    pub auc8: String,
    pub auc9: String,
}

/// 地図の 1 マス。Perl 版では `%02x%03x` (種類 2 桁 + 値 3 桁の 16 進) で保存されていた
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct LandCell {
    /// 地形番号 ([`LandKind`] の値)
    pub kind: u8,
    /// 地形ごとの値 (人口、規模、怪獣の種類と体力など)。
    /// Perl 版では 3 桁の 16 進で保存されるが、ターン処理中は 4095 を超えることがある
    pub value: i64,
}

impl LandCell {
    pub fn land_kind(&self) -> Option<LandKind> {
        LandKind::from_u8(self.kind)
    }
}

/// 島の地図。`cells[y * size + x]`
///
/// マスの並びは複製のあいだで共有し、書き換えるときに初めて写す (`Arc::make_mut`)。
/// 状態のスナップショット ([`GameState`] の複製) を安くするため (docs/SCALING.md)。
/// 保存の形は `Vec` と同じ
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct IslandMap {
    pub size: usize,
    pub cells: Arc<Vec<LandCell>>,
}

impl IslandMap {
    pub fn new_sea(size: usize) -> Self {
        Self {
            size,
            cells: Arc::new(vec![LandCell::default(); size * size]),
        }
    }

    pub fn get(&self, x: usize, y: usize) -> Option<LandCell> {
        (x < self.size && y < self.size).then(|| self.cells[y * self.size + x])
    }

    pub fn get_mut(&mut self, x: usize, y: usize) -> Option<&mut LandCell> {
        if x < self.size && y < self.size {
            let size = self.size;
            Some(&mut self.cells_mut()[y * size + x])
        } else {
            None
        }
    }

    /// 書き換えるためのマスの並び (ほかの複製と共有していれば写す)
    pub fn cells_mut(&mut self) -> &mut Vec<LandCell> {
        Arc::make_mut(&mut self.cells)
    }
}

/// 開発計画 1 件 (`kind,target,x,y,arg`)
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct PlannedCommand {
    /// 計画番号 ([`CommandKind`] の値)
    pub kind: u16,
    /// 対象の島 ID
    pub target: i64,
    pub x: i64,
    pub y: i64,
    /// 数量など
    pub arg: i64,
}

impl PlannedCommand {
    pub fn command_kind(&self) -> Option<CommandKind> {
        CommandKind::from_u16(self.kind)
    }
}

/// ログ類
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct Logs {
    /// ターンごとのログ。`turns[0]` が最新 (`hakojima.log0`)。
    /// 1 ターン分は圧縮して持ち ([`TurnLog`])、済んだターンのログは変わらないので複製のあいだで共有する
    pub turns: Vec<Arc<TurnLog>>,
    /// 発見の記録 (`hakojima.his`)。古い順
    pub history: Vec<TurnMessage>,
    /// Hakoniwa Cup のログ (`hakojima.lhc`)。古い順
    pub hcup: Vec<TurnMessage>,
    /// ハコオクのログ (`hakojima.auc`)。古い順
    pub auction: Vec<TurnMessage>,
}

/// ターンログ 1 行 (`機密,ターン,島ID1,島ID2,本文`)
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct LogEntry {
    /// 機密ログ (関係する島の持ち主にだけ見える)
    pub secret: bool,
    pub turn: i64,
    pub island1: Option<i64>,
    pub island2: Option<i64>,
    /// 本文。移植元のログは HTML を含む
    pub message: String,
}

/// ターンのログ 1 行の、溜めておく・保存するときの形 ([`crate::turn_log::TurnLog`] の中身)。
///
/// 件数の多いログは文面を作らずに出来事 ([`LogBody`] の `Text` 以外) で持ち、
/// 読むときに Perl 版と同じ文面を作る ([`LogRecord::to_entry`])。
/// 大きな地図では 1 ターン数百万行になり、文面を作るだけでターン処理の 3 割ほどかかっていた
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct LogRecord {
    pub secret: bool,
    pub turn: i64,
    pub island1: Option<i64>,
    pub island2: Option<i64>,
    pub body: LogBody,
}

/// ログの本文
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum LogBody {
    /// 文面 (HTML を含む)
    Text(String),
    /// `logOilMoney`: 「(島)(座標)の(地形)から、(金額)の収益が上がりました。」
    /// (金山・温泉街・天然スケート場など。大きな地図ではログの 3 割ほど)
    OilMoney {
        /// 島の名前 (ログを書いた時点のもの)
        name: Arc<str>,
        x: usize,
        y: usize,
        /// 地形の名前を決める地形と値 (`landName($kind, $lv)`)
        kind: u8,
        lv: i64,
        /// 金額と単位 (`"$value$HunitMoney"`)
        value: i64,
        unit: Arc<str>,
    },
}

impl LogBody {
    /// Perl 版と同じ文面
    pub fn text(&self) -> std::borrow::Cow<'_, str> {
        match self {
            LogBody::Text(s) => std::borrow::Cow::Borrowed(s),
            LogBody::OilMoney {
                name,
                x,
                y,
                kind,
                lv,
                value,
                unit,
            } => std::borrow::Cow::Owned(crate::log::msg::oil_money(
                name,
                &crate::land::land_name(*kind, *lv),
                &format!("({x}, {y})"),
                &format!("{value}{unit}"),
            )),
        }
    }
}

impl LogRecord {
    /// 文面の行にする
    pub fn to_entry(&self) -> LogEntry {
        LogEntry {
            secret: self.secret,
            turn: self.turn,
            island1: self.island1,
            island2: self.island2,
            message: self.body.text().into_owned(),
        }
    }

    /// 文面の行を、そのまま文面として持つ
    pub fn from_entry(e: LogEntry) -> Self {
        Self {
            secret: e.secret,
            turn: e.turn,
            island1: e.island1,
            island2: e.island2,
            body: LogBody::Text(e.message),
        }
    }
}

/// `ターン,本文` 形式のログ 1 行
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TurnMessage {
    pub turn: i64,
    pub message: String,
}

/// 他人から見た資金の表示 (`$HhideMoneyMode` と `aboutMoney` 相当)。
/// `Hidden` のときは Perl 版と同じく資金の欄自体を出さないので `None` を返す。
pub fn money_for_others(money: i64, mode: HideMoneyMode, unit: &str) -> Option<String> {
    match mode {
        HideMoneyMode::Visible => Some(format!("{money}{unit}")),
        HideMoneyMode::Hidden => None,
        HideMoneyMode::Rounded => Some(if money < 500 {
            format!("推定500{unit}未満")
        } else {
            format!("推定{}000{unit}", (money + 500) / 1000)
        }),
    }
}

/// `readIslandsFile` の出品の読み込み: 数値として 0 の出品 (`',,0,-3,'` なども) は、品物を
/// `random(27) + 1` で決め直した `品物,0,0,0,0` にする。Perl 版は読み込むたびに (ターン処理の前にも)
/// これを行うので、移植版は読み込みとターン処理の始めと、画面の操作で保存する前に行う
pub fn reroll_empty_lots<R: rand::RngCore + ?Sized>(lots: &mut Vec<String>, rng: &mut R) {
    lots.resize(3, String::new());
    for lot in lots.iter_mut() {
        if crate::perl::num_eq_empty(lot) {
            let item = crate::perl::random(rng, 27) + 1;
            *lot = format!("{item},0,0,0,0");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn new_game_aligns_start_time() {
        let c = GameConfig::default();
        let s = GameState::new_game(1_794_250_000, &c);
        assert_eq!(s.world.turn, 1);
        assert_eq!(s.world.next_id, 1);
        assert_eq!(s.world.last_time % c.unit_time, 0);
        assert!(s.world.last_time <= 1_794_250_000);
        assert!(!s.world.turn_due(s.world.last_time + c.unit_time - 1, &c));
        assert!(s.world.turn_due(s.world.last_time + c.unit_time, &c));
    }

    #[test]
    fn money_display() {
        let u = "億円";
        assert_eq!(
            money_for_others(499, HideMoneyMode::Rounded, u),
            Some("推定500億円未満".into())
        );
        assert_eq!(
            money_for_others(2000, HideMoneyMode::Rounded, u),
            Some("推定2000億円".into())
        );
        assert_eq!(
            money_for_others(2499, HideMoneyMode::Rounded, u),
            Some("推定2000億円".into())
        );
        assert_eq!(
            money_for_others(2500, HideMoneyMode::Rounded, u),
            Some("推定3000億円".into())
        );
        assert_eq!(
            money_for_others(123, HideMoneyMode::Visible, u),
            Some("123億円".into())
        );
        assert_eq!(money_for_others(123, HideMoneyMode::Hidden, u), None);
    }

    #[test]
    fn map_indexing() {
        let mut m = IslandMap::new_sea(12);
        m.get_mut(3, 5).unwrap().kind = LandKind::Town as u8;
        assert_eq!(m.get(3, 5).unwrap().land_kind(), Some(LandKind::Town));
        assert_eq!(m.get(5, 3).unwrap().land_kind(), Some(LandKind::Sea));
        assert!(m.get(12, 0).is_none());
    }
}
