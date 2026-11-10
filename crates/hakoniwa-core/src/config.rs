//! ゲーム設定。
//!
//! Perl 版 `hako-main.cgi` の「各種設定値」のうち、ゲームのルールと運営に関わるものを移植した。
//! 既定値は R.A. Final Edition の配布時の値と同じにしてある。
//! HTML の色・タグなど見た目だけの設定は、画面を作り直すので移植していない。
//!
//! TOML で上書きできる (指定しなかった項目は既定値になる)。

use serde::{Deserialize, Serialize};

/// 他人から資金を見えなくするか (`$HhideMoneyMode`)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HideMoneyMode {
    /// 0: 見えない
    Hidden,
    /// 1: 見える
    Visible,
    /// 2: 1000 単位に丸めた推定値を見せる
    Rounded,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct GameConfig {
    /// ゲームのタイトル (`$Htitle`)
    pub title: String,

    // ---- ゲームの進行 -------------------------------------------------
    /// 1 ターンの秒数 (`$HunitTime`)
    pub unit_time: i64,
    /// 島の最大数 (`$HmaxIsland`)
    pub max_islands: usize,
    /// 島の一辺の大きさ (`$HislandSize`)
    pub island_size: usize,
    /// コマンド入力限界数 (`$HcommandMax`)
    pub command_max: usize,
    /// ログファイル保持ターン数 (`$HlogMax`)
    pub log_max: usize,
    /// トップページに表示するログのターン数 (`$HtopLogTurn`)
    pub top_log_turns: usize,
    /// トップページの「諸島の状況」に一度に表示する島の数 (`$viewNumber`)
    pub top_view_number: usize,
    /// 発見ログ保持行数 (`$HhistoryMax`)
    pub history_max: usize,
    /// Hakoniwa Cup ログ保持行数 (`$HhcMax`)
    pub hcup_log_max: usize,
    /// バックアップを何ターンおきに取るか (`$HbackupTurn`)
    pub backup_every_turns: i64,
    /// バックアップを何回分残すか (`$HbackupTimes`)
    pub backup_keep: usize,
    /// 放棄コマンド自動入力ターン数 (`$HgiveupTurn`)
    pub giveup_turn: i64,
    /// 攻撃・援助・怪獣出現から守られる基準人口 (`$HguardPop`)
    pub guard_pop: i64,
    /// 他人から資金を見えなくするか (`$HhideMoneyMode`)
    pub hide_money_mode: HideMoneyMode,
    /// デバッグモード。「ターンを進める」操作を許可する (`$Hdebug`)
    pub debug: bool,
    /// 平和系モード (`$lovePeace`)
    pub love_peace: bool,
    /// アナザーモード (`$anothermood`)
    pub another_mode: bool,
    /// ハコオク何連続 1 位で賞品を出すか (`$aucshouhin`)
    pub auction_prize_streak: i64,
    /// ハコオクの連続 1 位賞品を何回もらえば殿堂入りか (`$aucdendou`)
    pub auction_hall_of_fame: i64,
    /// 登録時に既存の島と IP が重なれば拒否する (`$IPcut`)
    pub reject_duplicate_ip: bool,

    // ---- ローカル掲示板 -----------------------------------------------
    pub lbbs: LbbsConfig,

    // ---- 資金・食料 ---------------------------------------------------
    /// 初期資金 (`$HinitialMoney`)
    pub initial_money: i64,
    /// 初期食料 (`$HinitialFood`)
    pub initial_food: i64,
    /// 木の単位当たりの売値 (`$HtreeValue`)
    pub tree_value: i64,
    /// 名前変更のコスト (`$HcostChangeName`)
    pub cost_change_name: i64,
    /// 人口 1 単位あたりの食料消費量 (`$HeatenFood`)
    pub eaten_food: f64,
    /// 油田の収入 (`$HoilMoney`)
    pub oil_money: i64,
    /// 油田の枯渇確率 (`$HoilRatio`)
    pub oil_ratio: i64,
    /// 基地の経験値の最大値 (`$HmaxExpPoint`)
    pub max_exp_point: i64,
    /// ターン杯を何ターン毎に出すか (`$HturnPrizeUnit`)
    pub turn_prize_unit: i64,
    /// 防衛施設が怪獣に踏まれたとき自爆するか (`$HdBaseAuto`)
    pub defence_self_destruct: bool,

    pub units: Units,
    pub disaster: DisasterConfig,
    pub monster: MonsterConfig,

    /// 記念碑の種類数 (`$HmonumentNumber`)
    pub monument_number: usize,
    /// 船の種類数 (`$HfuneNumber`)
    pub ship_number: usize,

    pub passwords: Passwords,
    pub survey: SurveyConfig,
}

impl Default for GameConfig {
    fn default() -> Self {
        Self {
            title: "☆Hakoniwa R.A.☆".into(),
            unit_time: 21600,
            max_islands: 30,
            island_size: 12,
            command_max: 40,
            log_max: 8,
            top_log_turns: 1,
            top_view_number: 20,
            history_max: 20,
            hcup_log_max: 20,
            backup_every_turns: 12,
            backup_keep: 1,
            giveup_turn: 24,
            guard_pop: 500,
            hide_money_mode: HideMoneyMode::Rounded,
            debug: false,
            love_peace: true,
            another_mode: false,
            auction_prize_streak: 5,
            auction_hall_of_fame: 3,
            reject_duplicate_ip: true,
            lbbs: LbbsConfig::default(),
            initial_money: 2000,
            initial_food: 200,
            tree_value: 5,
            cost_change_name: 500,
            eaten_food: 0.2,
            oil_money: 2500,
            oil_ratio: 80,
            max_exp_point: 200,
            turn_prize_unit: 100,
            defence_self_destruct: true,
            units: Units::default(),
            disaster: DisasterConfig::default(),
            monster: MonsterConfig::default(),
            monument_number: 70,
            ship_number: 12,
            passwords: Passwords::default(),
            survey: SurveyConfig::default(),
        }
    }
}

impl GameConfig {
    pub fn from_toml(s: &str) -> Result<Self, toml::de::Error> {
        toml::from_str(s)
    }

    /// 島の座標数 (`$HpointNumber`)
    pub fn point_number(&self) -> usize {
        self.island_size * self.island_size
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct LbbsConfig {
    /// ローカル掲示板を使用するか (`$HuseLbbs`)
    pub enabled: bool,
    /// ローカル掲示板行数 (`$HlbbsMax`)
    pub max: usize,
    /// 匿名発言を許可するか (`$HlbbsAnon`)
    pub allow_anonymous: bool,
    /// 発言者の名前を表示するか (`$HlbbsSpeaker`)
    pub show_speaker: bool,
    /// 他島の掲示板に公開で発言する費用 (`$HlbbsMoneyPublic`)
    pub cost_public: i64,
    /// 他島の掲示板に極秘で発言する費用 (`$HlbbsMoneySecret`)
    pub cost_secret: i64,
}

impl Default for LbbsConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            max: 15,
            allow_anonymous: false,
            show_speaker: true,
            cost_public: 0,
            cost_secret: 10000,
        }
    }
}

/// 表示用の単位
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct Units {
    pub money: String,
    pub food: String,
    pub pop: String,
    pub area: String,
    pub tree: String,
    pub monster: String,
}

impl Default for Units {
    fn default() -> Self {
        Self {
            money: "億円".into(),
            food: "00トン".into(),
            pop: "00人".into(),
            area: "00万坪".into(),
            tree: "00本".into(),
            monster: "匹".into(),
        }
    }
}

/// 災害の発生率 (0.1% 単位)
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct DisasterConfig {
    pub earthquake: i64,
    pub tsunami: i64,
    pub typhoon: i64,
    pub meteo: i64,
    pub huge_meteo: i64,
    pub eruption: i64,
    pub fire: i64,
    /// 埋蔵金 (`$HdisMaizo`)
    pub maizo: i64,
    /// 地盤沈下の安全限界の広さ (Hex 数) (`$HdisFallBorder`)
    pub fall_border: i64,
    /// その広さを超えた場合の地盤沈下確率 (`$HdisFalldown`)
    pub falldown: i64,
}

impl Default for DisasterConfig {
    fn default() -> Self {
        Self {
            earthquake: 5,
            tsunami: 5,
            typhoon: 5,
            meteo: 5,
            huge_meteo: 2,
            eruption: 5,
            fire: 5,
            maizo: 10,
            fall_border: 350,
            falldown: 15,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct MonsterConfig {
    /// 怪獣レベル 1〜4 の人口基準 (`$HdisMonsBorder1`..`4`)
    pub borders: [i64; 4],
    /// 単位面積あたりの出現率 (0.01% 単位) (`$HdisMonster`)
    pub appearance_rate: i64,
    /// 各基準で出てくる怪獣番号の最大値 (`$HmonsterLevel1`..`4`)
    pub levels: [i64; 4],
    /// 怪獣の種類数 (`$HmonsterNumber`)
    pub number: usize,
    /// 怪獣がミサイルを叩き落す確率 (`$HmonsterDefence`)
    pub defence: i64,
}

impl Default for MonsterConfig {
    fn default() -> Self {
        Self {
            borders: [5000, 7500, 9000, 10000],
            appearance_rate: 1,
            levels: [4, 8, 12, 23],
            number: 31,
            defence: 500,
        }
    }
}

/// 管理用パスワード。
///
/// Perl 版は既定値がソースに直書きされていたが、移植版では未設定 (`None`) を既定にし、
/// 設定ファイルで指定されたときだけ有効にする。
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct Passwords {
    /// マスターパスワード。すべての島のパスワードを代用できる (`$masterPassword`)
    pub master: Option<String>,
    /// 名前変更で資金・食料を最大にする (`$HspecialPassword`)
    pub special: Option<String>,
    /// 名前変更で首都名を変える (`$HshutoPassword`)
    pub shuto: Option<String>,
    /// 名前変更で IP を変える (`$HipPassword`)
    pub ip: Option<String>,
    /// 名前変更でおまもりを増やす (`$HomamoriPassword`)
    pub omamori: Option<String>,
    /// 名前変更で任意のステータスを変える (`$HijiriPassword`)
    pub ijiri: Option<String>,
}

/// アンケート (`$AnkeitoOnOff` ほか)
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct SurveyConfig {
    pub enabled: bool,
    pub description: String,
    pub question: String,
    /// 選択肢 (`$AnkeitoShitumon1`..`5`)
    pub choices: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_toml_gives_defaults() {
        assert_eq!(GameConfig::from_toml("").unwrap(), GameConfig::default());
    }

    #[test]
    fn partial_override() {
        let c = GameConfig::from_toml(
            "unit_time = 3600\nhide_money_mode = \"visible\"\n[disaster]\nfire = 9\n",
        )
        .unwrap();
        assert_eq!(c.unit_time, 3600);
        assert_eq!(c.hide_money_mode, HideMoneyMode::Visible);
        assert_eq!(c.disaster.fire, 9);
        assert_eq!(c.disaster.earthquake, 5);
        assert_eq!(c.point_number(), 144);
    }
}
