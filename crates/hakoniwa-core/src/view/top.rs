//! トップページ (`hako-top.cgi` の `topPageMain` → `tempTopPage`) に出す内容。
//!
//! [`top_page`] が 1 画面分の値を [`TopPage`] にまとめて返す。文字列の値は Perl 版が画面に
//! 出す文字列そのもの (単位は `config.units`、数字の丸め方も Perl 版のとおり) で、
//! HTML の装飾 (色・太字) だけを取り除いてある。
//!
//! Perl 版の画面の並び:
//! 1. ターン数と次のターンまでの残り時間 ([`TopPage::turn`], [`TopPage::remaining_secs`])
//! 2. 「自分の島へ」の島の一覧 ([`TopPage::island_choices`]、保存順)
//! 3. アンケート (`$AnkeitoOnOff` のときだけ、[`TopPage::survey`])
//! 4. 各部門別ＮＯ.１ ([`TopPage::departments`])
//! 5. 諸島の状況 ([`TopPage::list`])
//! 6. 新しい島を探す ([`TopPage::can_register`])、島の名前とパスワードの変更
//! 7. Hakoniwa Auction ([`TopPage::auction`]、ハコオクのログ [`TopPage::auction_log`])
//! 8. Hakoniwa Cup のログ ([`TopPage::hcup_log`])、最近の出来事 ([`TopPage::logs`])、
//!    発見の記録 ([`TopPage::history`])
//!
//! 島の並べ替えは Perl 版と同じく「並べ替えを何度も続けて行う」ので、同じ値の島の順は
//! 直前の並べ替えの結果で決まる (部門の 1 位・諸島の状況の順位・ハコオクの順位に効く)。
//! ターン処理の部門賞 (`turn::ranking`) とは並べ替えの数と順が違う (トップページは
//! 面積・利益・人口増加・ポイント増加でも並べ替える) うえ、値も保存されたデータから
//! 計算し直すので、ここで別に行う。
//!
//! 複合値 (`factory`, `eisei3`〜`eisei6`, `etc6`〜`etc8`, `auc*`, ハコオクの出品) を分解する
//! 正規表現がマッチしなかったときは、Perl 版と同じく直前に成功したマッチの値を使う
//! ([`MatchScope`])。Hakoniwa Cup で負けた島の `eisei4` に負の数が入るときなどに効く。

use crate::config::{GameConfig, HideMoneyMode};
use crate::model::{GameState, Island, TurnMessage, money_for_others};
use crate::perl::{self, MatchScope, trunc};
use crate::tables::{HOUSE_LEVELS, MONSTERS, PRIZE_NAMES};

/// 「諸島の状況」の表示範囲。Perl 版では URL (`QUERY_STRING`) の `view<数>` / `viewALL`
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ViewRange {
    /// `view<n>`: n 番目 (0 から) の島から `config.top_view_number` 島。指定が無いときは `From(0)`
    From(usize),
    /// `viewALL`: すべての島
    All,
}

impl Default for ViewRange {
    fn default() -> Self {
        ViewRange::From(0)
    }
}

impl ViewRange {
    /// `QUERY_STRING` から読む (`cgiInput` の `/view([0-9]+|ALL)/`)。最初に見つかったものを使い、
    /// 無ければ `From(0)`。桁が大きすぎる数は `usize::MAX` にする
    pub fn from_query(query: &str) -> Self {
        let mut rest = query;
        while let Some(p) = rest.find("view") {
            let after = &rest[p + 4..];
            let digits = after.bytes().take_while(u8::is_ascii_digit).count();
            if digits > 0 {
                let n = after[..digits].bytes().fold(0usize, |n, b| {
                    n.saturating_mul(10).saturating_add(usize::from(b - b'0'))
                });
                return ViewRange::From(n);
            }
            if after.starts_with("ALL") {
                return ViewRange::All;
            }
            rest = &rest[p + 1..];
        }
        ViewRange::default()
    }
}

/// トップページ 1 画面分
#[derive(Debug, Clone, PartialEq)]
pub struct TopPage {
    /// ターン数 (`$HislandTurn`)
    pub turn: i64,
    /// 次のターンまでの秒数 (`$HunitTime + $HislandLastTime - time`)。Perl 版はこれを
    /// JavaScript で「次のターンまで残りHH:MM:SS」と数え下げる (0 未満は 0 と表示)
    pub remaining_secs: i64,
    /// 島を選ぶ一覧 (`$HislandList`、保存されている順。「自分の島へ」と「名前の変更」で使う)
    pub island_choices: Vec<IslandChoice>,
    /// アンケート (`config.survey.enabled` のときだけ)
    pub survey: Option<SurveyView>,
    /// 各部門別ＮＯ.１ (画面の順に 20 部門)。島が無ければ空
    pub departments: Vec<DepartmentWinner>,
    /// 諸島の状況
    pub list: IslandList,
    /// 新しい島を登録できるか (`$HislandNumber < $HmaxIsland`)。できなければ Perl 版は
    /// 「Biglobeじゃ限界だー（＞、＜）・・・現在登録できません。」と出す
    pub can_register: bool,
    /// Hakoniwa Auction
    pub auction: AuctionView,
    /// 「Hakoniwa Cup」の見出しのターン (`int($HislandTurn/100)*100`)。Perl 版は諸島の状況の
    /// 行を出すループの中でこれを計算するので、表示する島が無い (`view` が島の数より後ろ) と
    /// 空になる (`None`、Perl 版のまま)
    pub hcup_turn: Option<i64>,
    /// Hakoniwa Cup のログ (`hakojima.lhc`、新しい順)。Perl 版は「ターンN：本文」と出す
    pub hcup_log: Vec<TurnMessage>,
    /// ハコオクのログ (`hakojima.auc`、新しい順)。Perl 版は本文だけを出す
    pub auction_log: Vec<String>,
    /// 最近の出来事 (`logPrintTop`: 最新 `config.top_log_turns` ターン分のログのうち、
    /// 機密でないもの)。Perl 版は「ターンN：本文」と出す。
    /// [`top_page_with_log_limit`] で作ったときは、その行数まで
    pub logs: Vec<TurnMessage>,
    /// `logs` を行数の上限で打ち切ったか (続きは最近の出来事のページで見る)
    pub logs_truncated: bool,
    /// 発見の記録 (`hakojima.his`、新しい順)。Perl 版は「ターンN：本文」と出す
    pub history: Vec<TurnMessage>,
}

/// 島の選択肢
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IslandChoice {
    pub id: i64,
    /// 島の名前 (「島」は付かない。Perl 版は「名前島」と出す)
    pub name: String,
}

/// アンケートの集計
#[derive(Debug, Clone, PartialEq)]
pub struct SurveyView {
    /// 説明 (`$AnkeitoSetumei`、HTML のまま)
    pub description: String,
    /// 質問 (`$AnkeitoShitumon0`)
    pub question: String,
    /// 選択肢 (Ａ〜Ｅ)。投票のフォームの値は `ann` = 1〜5
    pub choices: Vec<SurveyChoice>,
    /// 投票数の合計
    pub total_votes: i64,
    /// 投票率の分母 (島の数。島が無ければ 1)
    pub island_count: i64,
    /// 投票率 (`int(合計 / 島の数 * 100)`)。Perl 版は「(合計/島の数票…N%)」と出す
    pub turnout_percent: i64,
}

/// アンケートの選択肢 1 つ
#[derive(Debug, Clone, PartialEq)]
pub struct SurveyChoice {
    /// 「Ａ」〜「Ｅ」
    pub label: &'static str,
    pub text: String,
    /// 票数 (Perl 版は「N票」と出す)
    pub votes: i64,
    /// 割合 (`int(票数 / 合計 * 100)`、合計が 0 なら 0)。Perl 版は「(N%)」と棒の幅に使う
    pub percent: i64,
}

/// 部門 (Perl 版の画面の順。島の部門賞の一覧もこの順)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Department {
    Pop,
    Farm,
    Factory,
    Mountain,
    Forest,
    Chicken,
    Pig,
    Cow,
    MonsterLive,
    MonsterKill,
    Force,
    Tourists,
    Unique,
    Monument,
    Military,
    HcWinRate,
    HcWins,
    TeamForce,
    Train,
    Power,
}

impl Department {
    /// 画面の順
    pub const ALL: [Department; 20] = [
        Department::Pop,
        Department::Farm,
        Department::Factory,
        Department::Mountain,
        Department::Forest,
        Department::Chicken,
        Department::Pig,
        Department::Cow,
        Department::MonsterLive,
        Department::MonsterKill,
        Department::Force,
        Department::Tourists,
        Department::Unique,
        Department::Monument,
        Department::Military,
        Department::HcWinRate,
        Department::HcWins,
        Department::TeamForce,
        Department::Train,
        Department::Power,
    ];

    /// 部門の名前 (Perl 版は「人口NO.1」の見出しと、島の部門賞の「[人口]」に使う)
    pub fn label(self) -> &'static str {
        match self {
            Department::Pop => "人口",
            Department::Farm => "農場",
            Department::Factory => "職場",
            Department::Mountain => "採掘場",
            Department::Forest => "森林",
            Department::Chicken => "にわとり数",
            Department::Pig => "ぶた数",
            Department::Cow => "うし数",
            Department::MonsterLive => "怪獣出現＆捕獲数",
            Department::MonsterKill => "怪獣退治数",
            Department::Force => "生物大学能力",
            Department::Tourists => "通算観光客",
            Department::Unique => "ユニーク地形数",
            Department::Monument => "記念碑数",
            Department::Military => "軍事技術",
            Department::HcWinRate => "ＨＣ通算勝率",
            Department::HcWins => "ＨＣ優勝回数",
            Department::TeamForce => "サッカーチーム力",
            Department::Train => "鉄道",
            Department::Power => "電力",
        }
    }
}

/// 部門の 1 位
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DepartmentWinner {
    pub department: Department,
    pub island_id: i64,
    /// 島の名前 (「島」は付かない)
    pub island_name: String,
    /// 値 (Perl 版の表示のまま。例「7900人」「1000人規模」「Ｌｖ11」「0％(0勝0敗0分)」)
    pub value: String,
}

/// 諸島の状況
#[derive(Debug, Clone, PartialEq)]
pub struct IslandList {
    /// 見出しの「N位〜M位」の N (`$viewFirst + 1`)
    pub first: usize,
    /// 見出しの「N位〜M位」の M
    pub last: usize,
    /// ページ送りのボタン (`viewALL` のときは `None`: Perl 版はボタンを出さない)
    pub paging: Option<Paging>,
    /// 資金の欄を出すか (`$HhideMoneyMode != 0`)
    pub show_money: bool,
    /// 表示する島 (順位の順)
    pub rows: Vec<IslandRow>,
}

/// ページ送り。「全表示」(`viewALL`) のボタンはいつも出る
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Paging {
    /// 「前のN島」(N = `config.top_view_number`) のボタンの行き先 (`view<数>`)。
    /// Perl 版は「次の島があり、その位置がちょうど N のとき」(= 先頭ページ) だけ出さない
    pub prev: Option<usize>,
    /// 「次のN島」のボタンの (行き先, 島の数)
    pub next: Option<(usize, usize)>,
}

/// 諸島の状況の島 1 つ
#[derive(Debug, Clone, PartialEq)]
pub struct IslandRow {
    /// 順位 (総合ポイント順)
    pub rank: usize,
    pub id: i64,
    /// 島の名前 (「島」は付かない)
    pub name: String,
    /// 連続資金繰り数。0 でなければ Perl 版は名前を灰色にして「名前島(N)」と出す
    pub absent: i64,
    /// 首都の名前 (`totoyoso2`)。Perl 版は「首都：名前」と出す。`totoyoso2` が 555 なら無し、
    /// 0 でも 555 でもない数値なら直前の行の島の値が残る (Perl 版のまま)
    pub capital: Option<String>,
    /// ポイント (Perl 版は「Npts.」)
    pub pts: i64,
    /// 失業率 (「12.34%」の形)。人口が 0 なら `None` (Perl 版は 0 で割って画面が止まる)
    pub unemployment: Option<String>,
    /// 失業率が負か (Perl 版は負なら青、そうでなければ赤で出す)
    pub unemployment_negative: bool,
    /// 「通算観光者数１万人未満」/「通算観光者数N万人」
    pub tourists: String,
    /// 前ターンからの増減。Perl 版は「(前ターン{pts}{pop}{money})」と並べる
    pub last_turn: LastTurn,
    /// 人口
    pub pop: String,
    /// 面積
    pub area: String,
    /// 資金 (`model::money_for_others`)。`HideMoneyMode::Hidden` なら `None` (欄が無い)
    pub money: Option<String>,
    /// へそくり (`auc9`)。`HideMoneyMode::Rounded` で合計が 1 以上のときだけ、
    /// 資金の後ろに「＋」とアイコンで出る
    pub savings: Option<Badge>,
    /// 食料
    pub food: String,
    /// 農場 (「保有せず」/「N0人」)。保有していれば収入見込みのポップアップが付く
    pub farm: Value,
    /// 職場 (普通職場 + ハイテク職場)
    pub factory: Value,
    /// 採掘場
    pub mountain: Value,
    /// 発電力 (「N万ｋＷ」)
    pub power: String,
    /// 軍事技術 (「ＬｖN」)
    pub military: String,
    /// info の行 (Perl 版の順: サッカー・ユニーク地形・家・出現中の怪獣・「出現中！」・
    /// マスコット・家畜・人工衛星・電力の使用状況)
    pub info: Vec<Badge>,
    /// Prize の行 (部門賞・ターン杯・賞・倒した怪獣・お守り)
    pub prizes: Vec<Badge>,
    /// この島が 1 位の部門 (画面の順)
    pub departments: Vec<Department>,
    /// 「予想１」(`eis8`、toto の予想)
    pub toto: String,
    /// コメントの行
    pub comment: CommentLine,
}

/// 前ターンからの増減 (正の数には全角の「＋」が付く)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LastTurn {
    /// ポイント (`monta`、「＋29pts.」)
    pub pts: String,
    /// 人口 (`hamu`、「＋2900人」)
    pub pop: String,
    /// 資金 (`pika`、「＋104億円」)
    pub money: String,
}

/// 表の欄の値。`hover` があれば Perl 版はマウスを載せたときに説明を出す
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Value {
    pub text: String,
    pub hover: Option<Hover>,
}

/// マウスを載せたときの説明 (Perl 版の `Navi` の題と本文)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Hover {
    pub title: String,
    /// 本文。外側は区切り線 (`<hr>`) で分かれた段落、内側は行 (`<br>`)
    pub detail: Vec<Vec<String>>,
}

/// info / Prize の行に並ぶアイコン 1 つ
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Badge {
    pub kind: BadgeKind,
    /// Perl 版の画像のファイル名 (「出現中！」の文字だけのときは `None`)
    pub image: Option<String>,
    /// 画像の代わりの文字 (`ALT`)
    pub alt: String,
    pub hover: Option<Hover>,
    /// アイコンの後ろに出す文字
    pub text: String,
}

/// アイコンの種類
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BadgeKind {
    /// Hakoniwa Cup のサッカーチーム (`eisei4`)
    Soccer,
    /// ユニーク地形 (`eisei6`)
    Unique,
    /// 島主の家 (税率 `eisei1`)
    House,
    /// 出現中の怪獣の種類 (`monsterlivetype`)
    LiveMonsters,
    /// 「出現中！」の文字 (`monsterlive` が 0 でない)
    MonsterAppearing,
    /// マスコットいのら・超神獣テトラ (`eisei5`)
    Mascot,
    Chicken,
    Pig,
    Cow,
    /// 人工衛星 (`eis1`〜`eis6`: 1 気象・2 観測・3 迎撃・4 軍事・5 防衛・6 イレギュラー)
    Satellite(u8),
    /// 宇宙ステーション (`eis7`)
    SpaceStation,
    /// 電力の使用状況 (いつも出る。`text` は不足なら「不足中！」)
    Power,
    /// へそくり (`auc9`)
    Savings,
    /// 部門賞 (`text` は「N冠」)
    Departments,
    /// ターン杯 (受賞ターンは `alt` に「Nターン杯 」の形で並ぶ)
    TurnCups,
    /// 賞 (`@Hprize` の 1〜9)
    Prize(u8),
    /// 倒した怪獣
    MonstersKilled,
    /// お守り (`etc8`)
    Amulet,
}

/// コメントの行
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CommentLine {
    /// `onm` が空: 「コメント : 本文」
    Comment { comment: String },
    /// 「名前 : 本文」
    Owner { owner: String, comment: String },
    /// 援助射撃 (`etc7` の状態 1):
    /// 「名前 : 〜島への援助射撃許可を申請中(残りNターン)」
    AidRequested {
        owner: String,
        target: String,
        turns_left: String,
    },
    /// 援助射撃 (`etc7` の状態 2): 「名前 : 〜島への援助射撃が可能(残りNターン)」
    AidAllowed {
        owner: String,
        target: String,
        turns_left: String,
    },
}

/// Hakoniwa Auction
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuctionView {
    /// 見出しのターン (`(int($HislandTurn/100)+1)*100`)。[`TopPage::hcup_turn`] と同じく、
    /// 表示する島が無ければ `None` (Perl 版のまま)
    pub turn: Option<i64>,
    /// 出品 3 枠 (島が無ければ空: Perl 版は品名を作らない)
    pub lots: Vec<Lot>,
    /// 高額落札ランキング (上位 10 島まで。1 位以外は落札額が 0 の島を出さない)
    pub high_bids: Vec<HighBid>,
    /// 高額落札ランキング 1 位の島の連続 1 位の記録 (島が無ければ `None`)
    pub leader: Option<AuctionLeader>,
    /// 殿堂入り (上位 5 島まで。1 位以外は落札額が 0 の島を出さない)
    pub hall_of_fame: Vec<HallOfFame>,
}

/// 出品 1 枠
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Lot {
    /// 品番 (1〜3)
    pub number: usize,
    /// 品名
    pub item: String,
    pub status: LotStatus,
    /// 入札額の上位 5 位 (島が 5 つ無くても 5 行)
    pub bids: Vec<LotBid>,
}

/// 出品の状態
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LotStatus {
    /// 「(落札済み)」
    Sold,
    /// 「(残りNターン)」
    Remaining(i64),
}

/// 入札の順位 1 行。入札した島の名前は伏せられる
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LotBid {
    pub rank: usize,
    /// 「？？？島」(入札なしなら「−」)
    pub bidder: String,
    /// 「N兆円」(入札なしなら「−」)
    pub amount: String,
}

/// 高額落札ランキング 1 行 (値が無い欄は「−」)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HighBid {
    pub rank: usize,
    /// 落札価格「N兆円」
    pub amount: String,
    /// 落札島名「名前島」
    pub island: String,
    /// 落札品名
    pub item: String,
    /// セクション
    pub section: String,
    /// ボーナス「+Npts.」
    pub bonus: String,
}

/// 高額落札ランキング 1 位の島。Perl 版は
/// 「名前島 / １位（N回）賞品まで（M/{streak}）/ {streak}連続ランキング１位の賞品を
/// {hall_of_fame}回もらうと殿堂入りとなります。」と出す
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuctionLeader {
    /// 島の名前 (「島」は付かない)
    pub name: String,
    /// 1 位の回数 (`auc4` の 1 番目)
    pub times: String,
    /// 賞品までの数 (`auc4` の 2 番目)
    pub progress: String,
    /// `config.auction_prize_streak`
    pub streak: i64,
    /// `config.auction_hall_of_fame`
    pub hall_of_fame: i64,
}

/// 殿堂入り 1 行 (値が無い欄は「−」)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HallOfFame {
    pub rank: usize,
    pub amount: String,
    pub island: String,
    pub item: String,
    pub section: String,
    /// １位保守回数「N回」
    pub times: String,
}

/// 保存されたデータから計算する島ごとの値 (Perl 版の最初のループが島のハッシュに入れる値)
#[derive(Debug, Clone, Default)]
struct Derived {
    factoryt: i64,
    ene: i64,
    /// `$island->{'ene'}` (画面に出す文字列)
    ene_text: String,
    shoritu: i64,
    styusho: i64,
    teamforce: i64,
    force: i64,
    uni: i64,
    tuni: i64,
    monsterlive2: i64,
    auc0c: i64,
    auc5c: i64,
}

/// 出品 1 枠の品名と状態
#[derive(Debug, Clone)]
struct LotHead {
    item: String,
    status: LotStatus,
}

/// `tempTopPage`: トップページに出す内容を作る。`now` はいまの時刻 (Unix 秒)、
/// `view` は表示範囲 (`ViewRange::from_query(QUERY_STRING)`)。
///
/// データは書き換えない。Perl 版はこのほかにアクセスログ (`axeslog`、`./axes-hako.log`) を
/// 書くが、移植していない。ターン処理が必要な時刻なら、呼ぶ前にターン処理を済ませること
/// (Perl 版は `readIslandsFile` がターン処理をしてからトップページを出す)
pub fn top_page(game: &GameState, config: &GameConfig, now: i64, view: ViewRange) -> TopPage {
    top_page_with_log_limit(game, config, now, view, usize::MAX)
}

/// [`top_page`] で、最近の出来事を `log_limit` 行までにしたもの。
/// 大きな地図・多くの島では 1 ターンのログが数百万行になるので、サーバーはこちらを使う
/// (かたまりは要るぶんだけ展開する)
pub fn top_page_with_log_limit(
    game: &GameState,
    config: &GameConfig,
    now: i64,
    view: ViewRange,
    log_limit: usize,
) -> TopPage {
    let world = &game.world;
    let islands = &world.islands;
    let n = islands.len();
    let units = &config.units;

    // ---- 最初のループ (保存順): 並べ替えに使う値と出品の品名 ----
    let mut scope = MatchScope::default();
    let mut derived = Vec::with_capacity(n);
    let mut lots: Option<[LotHead; 3]> = None;
    let mut dashiname = String::new();
    for island in islands {
        let f = scope.fields::<10>(&island.factory);
        let factoryt = f[0] + f[1];
        lots = Some(lot_heads(world, &mut scope, &mut dashiname));
        let (e3t, e3) = parse::<5>(&mut scope, &island.eisei_raw[0]);
        let e4 = scope.fields::<11>(&island.eisei_raw[1]);
        let siaisu = match e4[6] + e4[7] + e4[8] {
            0 => 1,
            s => s,
        };
        let e5 = scope.fields::<7>(&island.eisei_raw[2]);
        let e6 = scope.fields::<12>(&island.eisei_raw[3]);
        let zoo = scope.fields::<31>(&island.etc_raw[1]);
        let auc0 = scope.fields::<5>(&island.auction.auc0);
        let auc5 = scope.fields::<5>(&island.auction.auc5);
        derived.push(Derived {
            factoryt,
            // ($ene, $shouhi, $sabun, $chikuden, $ene) = ($1..$5): 5 番目が残る
            ene: e3[4],
            ene_text: e3t[4].clone(),
            shoritu: trunc(e4[6] as f64 / siaisu as f64 * 100.0),
            styusho: e4[9],
            teamforce: e4[0] + e4[1] + e4[2],
            force: e5[..4].iter().sum(),
            uni: e6.iter().filter(|&&v| v != 0).count() as i64,
            tuni: e6.iter().sum(),
            monsterlive2: island.monster_live + zoo.iter().sum::<i64>(),
            auc0c: auc0[2],
            auc5c: auc5[2],
        });
    }

    // ---- 部門別の並べ替え (並べ替えを続けて行う) ----
    let mut order: Vec<usize> = (0..n).collect();
    let mut won = vec![Vec::<Department>::new(); n];
    let mut winners: Vec<(Department, usize)> = Vec::new();
    {
        use Department as D;
        let i = |k: usize| &islands[k];
        let d = |k: usize| &derived[k];
        // (部門, 並べ替えの値)。部門が None の並べ替えは部門賞を出さないが、同じ値の島の順を変える
        let sorts: [(Option<Department>, &SortKey); 24] = [
            (Some(D::Pop), &|k| i(k).pop),                   // islandSortPop
            (Some(D::Farm), &|k| i(k).farm),                 // islandSortFarm
            (Some(D::Factory), &|k| d(k).factoryt),          // islandSortFactory
            (Some(D::Mountain), &|k| i(k).mountain),         // islandSortMountain
            (None, &|k| i(k).area),                          // islandSortArea
            (Some(D::Monument), &|k| i(k).owner_stats.kei),  // islandSortMonument
            (Some(D::MonsterLive), &|k| d(k).monsterlive2),  // islandSortLive
            (Some(D::Military), &|k| i(k).owner_stats.rena), // islandSortRena
            (Some(D::MonsterKill), &|k| i(k).taiji),         // islandSortKill
            (Some(D::Forest), &|k| i(k).owner_stats.fore),   // islandSortFore
            (None, &|k| i(k).owner_stats.pika),              // islandSortPika
            (None, &|k| i(k).owner_stats.hamu),              // islandSortHamu
            (None, &|k| i(k).owner_stats.monta),             // islandSortMonta
            (Some(D::Chicken), &|k| i(k).owner_stats.tare),  // islandSortTare
            (Some(D::Pig), &|k| i(k).owner_stats.zipro),     // islandSortZipro
            (Some(D::Cow), &|k| i(k).owner_stats.leje),      // islandSortLeje
            (Some(D::Force), &|k| d(k).force),               // islandSortForce
            (Some(D::Tourists), &|k| i(k).eisei[1]),         // islandSortEisei2
            (Some(D::Unique), &|k| d(k).uni),                // islandSortUni
            (Some(D::Power), &|k| d(k).ene),                 // islandSorthck
            (Some(D::Train), &|k| i(k).etc_num[0]),          // islandSorthckt
            (Some(D::HcWinRate), &|k| d(k).shoritu),         // islandSorthcr
            (Some(D::HcWins), &|k| d(k).styusho),            // islandSorthcy
            (Some(D::TeamForce), &|k| d(k).teamforce),       // islandSorthct
        ];
        for (dep, key) in sorts {
            sort_desc(&mut order, key);
            if let (Some(dep), Some(&top)) = (dep, order.first()) {
                winners.push((dep, top));
            }
        }
    }
    for &(dep, k) in &winners {
        won[k].push(dep);
    }
    for w in won.iter_mut() {
        w.sort_by_key(|d| Department::ALL.iter().position(|x| x == d));
    }

    // 部門の 1 位の値。HC 通算勝率の勝敗数はここで (サブルーチンの直下で) 分解する
    let mut sub_scope = MatchScope::default();
    let winner_of = |dep: Department| winners.iter().find(|w| w.0 == dep).map(|w| w.1);
    let mut hc_record: [String; 11] = Default::default();
    for dep in [Department::Power, Department::Train, Department::HcWinRate] {
        if let Some(k) = winner_of(dep) {
            let v = sub_scope.fields_text::<11>(&islands[k].eisei_raw[1]);
            if dep == Department::HcWinRate {
                hc_record = v;
            }
        }
    }
    let departments = Department::ALL
        .iter()
        .filter_map(|&dep| {
            let k = winner_of(dep)?;
            let (i, d) = (&islands[k], &derived[k]);
            let value = match dep {
                Department::Pop => format!("{}{}", i.pop, units.pop),
                Department::Farm => format!("{}0{}規模", i.farm, units.pop),
                Department::Factory => format!("{}0{}規模", d.factoryt, units.pop),
                Department::Mountain => format!("{}0{}規模", i.mountain, units.pop),
                Department::Forest => format!("{}{}", i.owner_stats.fore, units.tree),
                Department::Chicken => format!("{}万羽", i.owner_stats.tare),
                Department::Pig => format!("{}万頭", i.owner_stats.zipro),
                Department::Cow => format!("{}万頭", i.owner_stats.leje),
                Department::MonsterLive => format!("{}{}", d.monsterlive2, units.monster),
                Department::MonsterKill => format!("{}{}", i.taiji, units.monster),
                Department::Force => format!("合計{}pts.", d.force),
                Department::Tourists => format!("{}{}", i.eisei[1], units.pop),
                Department::Unique => format!("{}種類/{}ヶ所", d.uni, d.tuni),
                Department::Monument => format!("{}ヶ所", i.owner_stats.kei),
                Department::Military => format!("Ｌｖ{}", military_level(i.owner_stats.rena)),
                Department::HcWinRate => format!(
                    "{}％({}勝{}敗{}分)",
                    d.shoritu, hc_record[6], hc_record[8], hc_record[7]
                ),
                Department::HcWins => format!("{}回", d.styusho),
                Department::TeamForce => format!("合計{}pts.", d.teamforce),
                Department::Train => format!("{}ｋｍ＋移動", i.etc_num[0]),
                Department::Power => format!("{}万ｋＷ", d.ene_text),
            };
            Some(DepartmentWinner {
                department: dep,
                island_id: i.id,
                island_name: i.name.clone(),
                value,
            })
        })
        .collect();

    // ---- 総合ポイント順 (islandSort) ----
    sort_desc(&mut order, |k| islands[k].pts);

    // ---- 諸島の状況 ----
    let vn = config.top_view_number;
    let (view_first, all) = match view {
        ViewRange::From(k) => (k, false),
        ViewRange::All => (0, true),
    };
    let mut loop_end = view_first.saturating_add(vn).min(n);
    if all {
        loop_end = n;
    }
    let paging = (!all).then(|| {
        let next = (view_first.saturating_add(vn) < n).then(|| {
            let start = view_first + vn;
            (start, vn.min(n - start))
        });
        // Perl 版は「次」の行き先がちょうど $viewNumber のときだけ「前」を出さない
        let prev = (next.map(|x| x.0) != Some(vn)).then(|| view_first.saturating_sub(vn));
        Paging { prev, next }
    });
    let mut row_scope = sub_scope.clone();
    let mut shutoname: Option<String> = None;
    let rows = (view_first..loop_end)
        .map(|ii| {
            let k = order[ii];
            island_row(
                &RowContext {
                    config,
                    islands,
                    order: &order,
                    rank: ii + 1,
                    island: &islands[k],
                    departments: &won[k],
                },
                &mut row_scope,
                &mut shutoname,
            )
        })
        .collect();
    let list = IslandList {
        first: view_first.saturating_add(1),
        last: loop_end,
        paging,
        show_money: config.hide_money_mode != HideMoneyMode::Hidden,
        rows,
    };

    // ---- Hakoniwa Auction ----
    let lots = lots
        .map(|heads| {
            let keys: [fn(&Island) -> i64; 3] =
                [|i| i.auction.auc1, |i| i.auction.auc2, |i| i.auction.auc3];
            heads
                .into_iter()
                .zip(keys)
                .enumerate()
                .map(|(l, (head, key))| {
                    // islandSortac1..3: 総合ポイント順から続けて並べ替える
                    sort_desc(&mut order, |k| key(&islands[k]));
                    let bids = (0..5)
                        .map(|ii| {
                            let v = order.get(ii).map_or(0, |&k| key(&islands[k]));
                            let (bidder, amount) = if v == 0 {
                                ("−".to_string(), "−".to_string())
                            } else {
                                ("？？？島".to_string(), format!("{v}兆円"))
                            };
                            LotBid {
                                rank: ii + 1,
                                bidder,
                                amount,
                            }
                        })
                        .collect();
                    Lot {
                        number: l + 1,
                        item: head.item,
                        status: head.status,
                        bids,
                    }
                })
                .collect()
        })
        .unwrap_or_default();

    // islandSortac4: 高額落札ランキング
    sort_desc(&mut order, |k| derived[k].auc0c);
    let mut high_bids = Vec::new();
    let mut leader = None;
    let mut s4 = sub_scope.clone();
    for ii in 0..n.min(10) {
        let top = &islands[order[0]];
        let a4 = s4.fields_text::<3>(&top.auction.auc4);
        leader = Some(AuctionLeader {
            name: top.name.clone(),
            times: a4[0].clone(),
            progress: a4[1].clone(),
            streak: config.auction_prize_streak,
            hall_of_fame: config.auction_hall_of_fame,
        });
        let island = &islands[order[ii]];
        let ([_, value, amount, section, _], [kind, _, amount_n, _, place]) =
            parse::<5>(&mut s4, &island.auction.auc0);
        if amount_n != 0 || ii == 0 {
            let none = amount_n == 0;
            high_bids.push(HighBid {
                rank: ii + 1,
                amount: dash_or(none, || format!("{amount}兆円")),
                island: dash_or(none, || format!("{}島", island.name)),
                item: record_item(kind, &value, island),
                section: dash_or(none, || section.clone()),
                bonus: dash_or(none, || format!("+{}pts.", (11 - place) * 500)),
            });
        }
    }

    // islandSortac5: 殿堂入り
    sort_desc(&mut order, |k| derived[k].auc5c);
    let mut hall_of_fame = Vec::new();
    let mut s5 = sub_scope.clone();
    for (ii, &k) in order.iter().enumerate().take(5) {
        let island = &islands[k];
        let ([_, value, amount, section, times], [kind, _, amount_n, ..]) =
            parse::<5>(&mut s5, &island.auction.auc5);
        if amount_n != 0 || ii == 0 {
            let none = amount_n == 0;
            hall_of_fame.push(HallOfFame {
                rank: ii + 1,
                amount: dash_or(none, || format!("{amount}兆円")),
                island: dash_or(none, || format!("{}島", island.name)),
                item: record_item(kind, &value, island),
                section: dash_or(none, || section.clone()),
                times: dash_or(none, || format!("{times}回")),
            });
        }
    }

    let turn = world.turn;
    // $hcturn と $acturn は表示のループの中で決まる
    let shown = !list.rows.is_empty();
    // 最近の出来事: 最新 top_log_turns ターン分の機密でない行を、log_limit 行まで
    let logs = {
        let mut lines = Vec::new();
        let mut truncated = false;
        'turns: for log in game.logs.turns.iter().take(config.top_log_turns) {
            for (_, e) in log.iter_from(0) {
                if e.secret {
                    continue;
                }
                if lines.len() == log_limit {
                    truncated = true;
                    break 'turns;
                }
                lines.push(TurnMessage {
                    turn: e.turn,
                    message: e.message,
                });
            }
        }
        (lines, truncated)
    };
    TopPage {
        turn,
        remaining_secs: config.unit_time + world.last_time - now,
        island_choices: islands
            .iter()
            .map(|i| IslandChoice {
                id: i.id,
                name: i.name.clone(),
            })
            .collect(),
        survey: survey(world, config),
        departments,
        list,
        can_register: n < config.max_islands,
        auction: AuctionView {
            turn: shown.then(|| (turn.div_euclid(100) + 1) * 100),
            lots,
            high_bids,
            leader,
            hall_of_fame,
        },
        hcup_turn: shown.then(|| turn.div_euclid(100) * 100),
        hcup_log: game.logs.hcup.iter().rev().cloned().collect(),
        auction_log: game
            .logs
            .auction
            .iter()
            .rev()
            .map(|m| m.message.clone())
            .collect(),
        logs: logs.0,
        logs_truncated: logs.1,
        history: game.logs.history.iter().rev().cloned().collect(),
    }
}

/// 並べ替えの値 (保存順の位置 → 値)
type SortKey<'a> = dyn Fn(usize) -> i64 + 'a;

/// `$s =~ /^([0-9]*),...$/; (...) = ($1, ...)`: 欄の文字列 (画面に埋め込む値) と数値
fn parse<const N: usize>(scope: &mut MatchScope, s: &str) -> ([String; N], [i64; N]) {
    let t = scope.fields_text::<N>(s);
    let v = std::array::from_fn(|i| perl::int(&t[i]));
    (t, v)
}

/// `sort { $b->{key} <=> $a->{key} || $a <=> $b }`: 大きい順。同じ値なら今の順を保つ (安定)
fn sort_desc(order: &mut [usize], key: impl Fn(usize) -> i64) {
    order.sort_by_key(|&k| std::cmp::Reverse(key(k)));
}

/// `none` なら「−」
fn dash_or(none: bool, f: impl FnOnce() -> String) -> String {
    if none { "−".to_string() } else { f() }
}

/// 軍事技術のレベル (`int($rena / 10) + 1`)
fn military_level(rena: i64) -> i64 {
    trunc(rena as f64 / 10.0) + 1
}

/// アンケートの集計
fn survey(world: &crate::model::World, config: &GameConfig) -> Option<SurveyView> {
    let s = &config.survey;
    if !s.enabled {
        return None;
    }
    let votes = world.survey_votes;
    let total: i64 = votes.iter().sum();
    let divisor = if total == 0 { 1 } else { total };
    // $HislandNumber が 0 なら 1 にする (Perl 版はこのとき島の一覧に空の島が 1 つ出る。
    // それは再現しない)
    let islands = match world.islands.len() as i64 {
        0 => 1,
        k => k,
    };
    const LABELS: [&str; 5] = ["Ａ", "Ｂ", "Ｃ", "Ｄ", "Ｅ"];
    Some(SurveyView {
        description: s.description.clone(),
        question: s.question.clone(),
        choices: LABELS
            .iter()
            .enumerate()
            .map(|(i, &label)| SurveyChoice {
                label,
                text: s.choices.get(i).cloned().unwrap_or_default(),
                votes: votes[i],
                percent: trunc(votes[i] as f64 / divisor as f64 * 100.0),
            })
            .collect(),
        total_votes: total,
        island_count: islands,
        turnout_percent: trunc(total as f64 / islands as f64 * 100.0),
    })
}

/// 品番 1〜29 の品名 (0 と 30 は呼び出し側で決める)。`value` は値の欄の文字列。
/// 10・11・17・18 は値を 1000 倍して出す
fn item_name(kind: i64, value: &str) -> Option<String> {
    let scaled = || perl::int(value) * 1000;
    Some(match kind {
        1 => "地石".into(),
        2 => "氷石".into(),
        3 => "風石".into(),
        4 => "炎石".into(),
        5 => "光石".into(),
        6 => "天使ミカエル".into(),
        7 => "アイススコーピオン".into(),
        8 => "スライムレジェンド".into(),
        9 => format!("お守り{value}個"),
        10 => format!("海あみゅ{}人規模", scaled()),
        11 => format!("食研{}人規模", scaled()),
        12 => format!("コスモ{value}万ｋＷ"),
        13 => "闇石".into(),
        14 => "衛星６種".into(),
        15 => "宇宙ステーション".into(),
        16 => "黄金のコンデンサ".into(),
        17 => format!("金山{}人規模", scaled()),
        18 => format!("養殖場{}人規模", scaled()),
        19 => "人造怪獣f02".into(),
        20 => "魔王サタン".into(),
        21 => "unknown".into(),
        22 => format!("サッカーチーム力1.{value}倍"),
        23 => format!("生物大学能力1.{value}倍"),
        24 => format!("生物大学経験値{value}"),
        25 => "卵".into(),
        26 => "生物大学".into(),
        27 => format!("風力{value}万ｋＷ"),
        28 => format!("バイオマス{value}万ｋＷ"),
        29 => "今回はお休み".into(),
        _ => return None,
    })
}

/// 品名の表示で値を 1000 倍する品番 (`$avalue = $avalue * 1000`)
fn scales_value(kind: i64) -> bool {
    matches!(kind, 10 | 11 | 17 | 18)
}

/// 高額落札ランキング・殿堂入りの品名 (0 は「−」、30 は島の `auc8`)
fn record_item(kind: i64, value: &str, island: &Island) -> String {
    match kind {
        0 => "−".into(),
        30 => island.auction.auc8.clone(),
        _ => item_name(kind, value).unwrap_or_else(|| "？".into()),
    }
}

/// 出品 3 枠の品名と状態 (最初のループの中で島ごとに作り直す)
fn lot_heads(
    world: &crate::model::World,
    scope: &mut MatchScope,
    dashiname: &mut String,
) -> [LotHead; 3] {
    let lot = |i: usize| world.auction_lots.get(i).map_or("", String::as_str);
    let mut prev_value = String::new();
    std::array::from_fn(|l| {
        let ([_, value_text, ..], [kind, value, state, _, _]) = parse::<5>(scope, lot(l));
        let item = match kind {
            // 品番 0 は 1 枠目だけ「？」、2・3 枠目は「闇石」
            0 if l == 0 => "？".to_string(),
            0 => "闇石".to_string(),
            // 3 枠目のお守りの個数は 2 枠目の値を出す (Perl 版のまま)
            9 if l == 2 => format!("お守り{prev_value}個"),
            30 => {
                // 出品した島の名前。見つからなければ前の値が残る (Perl 版のまま)
                if let Some(i) = world.islands.iter().rev().find(|i| i.id == value) {
                    *dashiname = i.auction.auc7.clone();
                }
                dashiname.clone()
            }
            _ => item_name(kind, &value_text).unwrap_or_else(|| "？".into()),
        };
        prev_value = if scales_value(kind) {
            (value * 1000).to_string()
        } else {
            value_text
        };
        let status = if state == 15 {
            LotStatus::Sold
        } else {
            LotStatus::Remaining(15 - state)
        };
        LotHead { item, status }
    })
}

/// 島 1 行を作るのに要るもの
struct RowContext<'a> {
    config: &'a GameConfig,
    /// 保存順の島 (`%HidToNumber` の位置)
    islands: &'a [Island],
    /// いまの並び (総合ポイント順) → 保存順の位置
    order: &'a [usize],
    rank: usize,
    island: &'a Island,
    departments: &'a [Department],
}

/// ユニーク地形の名前 (`eisei6` の欄の順)
const UNIQUE_NAMES: [&str; 12] = [
    "[天使ミカエルor幸福の女神像]",
    "[首都]",
    "[壊れた侵略者]",
    "[王蟲の脱け殻]",
    "[闇石]",
    "[地石]",
    "[氷石]",
    "[風石]",
    "[炎石]",
    "[光石]",
    "[古代遺跡]",
    "[天空城or魔塔]",
];
/// 画面に並べる順 (首都・天使・遺跡・侵略者・王蟲・炎・氷・地・風・光・闇・天空城)
const UNIQUE_ORDER: [usize; 12] = [1, 0, 10, 2, 3, 8, 6, 5, 7, 9, 4, 11];

/// サッカーチームの状態 (`eisei4` の 11 番目)
fn soccer_status(v: i64) -> &'static str {
    match v {
        1 => "予選第１戦待ち",
        2 => "予選第２戦待ち",
        3 => "予選第３戦待ち",
        4 => "予選第４戦待ち",
        5 => "予選終了待ち",
        6 => "準々決勝戦待ち",
        7 => "準決勝戦待ち",
        8 => "決勝戦待ち",
        9 => "優勝！",
        11 => "予選落ち",
        12 => "準々決勝負け",
        13 => "準決勝負け",
        14 => "第２位",
        _ => "練習中",
    }
}

/// 島主の家の名前
const HOUSE_NAMES: [&str; 12] = [
    "の小屋",
    "の簡易住宅",
    "の住宅",
    "の高級住宅",
    "の豪邸",
    "の大豪邸",
    "の高級豪邸",
    "の城",
    "の巨城",
    "の黄金城",
    "の魔塔",
    "の天空城",
];

fn hover(title: impl Into<String>, detail: Vec<Vec<String>>) -> Option<Hover> {
    Some(Hover {
        title: title.into(),
        detail,
    })
}

fn badge(kind: BadgeKind, image: &str, alt: impl Into<String>, text: impl Into<String>) -> Badge {
    Badge {
        kind,
        image: Some(image.to_string()),
        alt: alt.into(),
        hover: None,
        text: text.into(),
    }
}

/// 正の数 (0 を含む) に全角の「＋」を付ける
fn signed(v: i64, unit: &str) -> String {
    if v < 0 {
        format!("{v}{unit}")
    } else {
        format!("＋{v}{unit}")
    }
}

/// `$prize =~ /([0-9]*),([0-9]*),(.*)/` (先頭に固定しない)
fn match_prize(s: &str) -> Option<(&str, &str, &str)> {
    let b = s.as_bytes();
    let digits = |from: usize| b[from..].iter().take_while(|c| c.is_ascii_digit()).count();
    (0..=b.len()).find_map(|start| {
        let e1 = start + digits(start);
        if b.get(e1) != Some(&b',') {
            return None;
        }
        let e2 = e1 + 1 + digits(e1 + 1);
        if b.get(e2) != Some(&b',') {
            return None;
        }
        // (.*) は改行の手前まで
        let rest = &s[e2 + 1..];
        let rest = rest.split('\n').next().unwrap_or("");
        Some((&s[start..e1], &s[e1 + 1..e2], rest))
    })
}

/// `while($turns =~ s/([0-9]*),//)` で取り出す数字の並び
fn turn_cups(turns: &str) -> Vec<String> {
    let mut s = turns.to_string();
    let mut out = Vec::new();
    while let Some(c) = s.find(',') {
        let start = s[..c]
            .rfind(|ch: char| !ch.is_ascii_digit())
            .map_or(0, |p| p + s[p..].chars().next().map_or(1, char::len_utf8));
        out.push(s[start..c].to_string());
        s.replace_range(start..=c, "");
    }
    out
}

/// 怪獣の種類のビット列から名前の一覧 (`[名前] ` を並べたもの)、種類の数、最後の番号
fn monster_list(bits: i64, config: &GameConfig) -> (String, i64, Option<usize>) {
    let mut names = String::new();
    let mut kinds = 0;
    let mut max = None;
    for (i, m) in MONSTERS.iter().enumerate().take(config.monster.number) {
        if i < 63 && bits & (1i64 << i) != 0 {
            names.push_str(&format!("[{}] ", m.name));
            kinds += 1;
            max = Some(i);
        }
    }
    (names, kinds, max)
}

/// 諸島の状況の島 1 行 (表示のループ 1 回分)
fn island_row(
    ctx: &RowContext,
    scope: &mut MatchScope,
    shutoname: &mut Option<String>,
) -> IslandRow {
    let config = ctx.config;
    let units = &config.units;
    let island = ctx.island;
    let (pop, farm, mountain) = (island.pop, island.farm, island.mountain);

    let ([f1_text, f2_text, ..], [factory1, factory2, co0, co1, ..]) =
        parse::<10>(scope, &island.factory);
    let factoryt = factory1 + factory2;
    let unemployed = (pop - (farm + factoryt + mountain) * 10) as f64 / pop as f64 * 100.0;

    // 収入見込み
    let (mut food_in, mut ht_in, mut money_in) = (0, 0, 0);
    if pop > farm * 10 {
        food_in += farm * 10 * (co0 + 1);
        // Perl 版はここで if の中で auc9 を分解するが使わず、マッチの値もブロックを出ると戻る
        if factory2 * 10 > pop - farm * 10 {
            ht_in += trunc((pop - farm * 10) as f64 / 10.0);
        } else {
            ht_in += factory2;
            money_in += trunc((pop - farm * 10 - factory2 * 10) as f64 / 10.0)
                .min(factory1 + mountain)
                * (co1 + 1);
        }
    } else {
        food_in += pop * (co0 + 1);
    }
    let held = |v: i64, text: &str| {
        if v == 0 {
            "保有せず".to_string()
        } else {
            format!("{text}0{}", units.pop)
        }
    };
    let estimate = |v: i64, none: &str, label: &str, unit: &str| {
        if v == 0 {
            none.to_string()
        } else {
            format!("{label}＋{v}{unit}")
        }
    };
    let income = hover(
        "収入見込み",
        vec![
            vec![
                format!("普通職場…{}", held(factory1, &f1_text)),
                format!("ＨＴ職場…{}", held(factory2, &f2_text)),
            ],
            vec![
                estimate(food_in, "食料見込みなし", "食料", &units.food),
                estimate(money_in, "資金見込みなし", "資金", &units.money),
                estimate(ht_in, "補助金見込みなし", "補助金", &units.money),
            ],
        ],
    );
    let scale = |v: i64| Value {
        text: held(v, &v.to_string()),
        hover: if v == 0 { None } else { income.clone() },
    };

    let monster_live = island.monster_live;
    let monsm = if monster_live == 0 {
        ""
    } else {
        "出現中！"
    };
    let eisei2nd = trunc(island.eisei[1] as f64 / 100.0);

    // ユニーク地形
    let uniq = scope.fields::<12>(&island.eisei_raw[3]);
    let unique_names: String = UNIQUE_ORDER
        .iter()
        .filter(|&&k| uniq[k] != 0)
        .map(|&k| UNIQUE_NAMES[k])
        .collect();
    let uni_kinds = uniq.iter().filter(|&&v| v != 0).count();
    let uniquesu: i64 = uniq.iter().sum();
    let mut info = Vec::new();
    let mut unique = None;
    if uni_kinds > 0 {
        let complete = uni_kinds == 12;
        let mut b = badge(
            BadgeKind::Unique,
            "prize10.gif",
            format!(
                "入手の難しいユニーク地形：{unique_names}／{}",
                if complete {
                    "Complete!!"
                } else {
                    "全12種類"
                }
            ),
            format!("{uniquesu}ヶ所"),
        );
        let head = if complete {
            "Complete!!".to_string()
        } else {
            format!("全12種類中{uni_kinds}種類")
        };
        b.hover = hover("ユニーク地形", vec![vec![head, unique_names.clone()]]);
        unique = Some(b);
    }

    // 部門賞
    let mut prizes = Vec::new();
    if !ctx.departments.is_empty() {
        let list: String = ctx
            .departments
            .iter()
            .map(|d| format!("[{}]", d.label()))
            .collect();
        let mut b = badge(
            BadgeKind::Departments,
            "prize11.gif",
            list.clone(),
            format!("{}冠", ctx.departments.len()),
        );
        b.hover = hover("部門賞", vec![vec![list]]);
        prizes.push(b);
    }

    // 賞 (prize = "賞のビット,倒した怪獣のビット,ターン杯のターン,...")
    let (flags, monsters, turns) = match match_prize(&island.prize) {
        Some((a, b, c)) => {
            scope.set_text(vec![a.to_string(), b.to_string(), c.to_string()]);
            (perl::int(a), perl::int(b), c.to_string())
        }
        // マッチしなければ前のマッチの値。数字だけの $3 にはカンマが無いのでターン杯は無い
        None => {
            let [a, b] = scope.current::<2>();
            (a, b, String::new())
        }
    };
    let cups: String = turn_cups(&turns)
        .iter()
        .map(|t| format!("{t}{} ", PRIZE_NAMES[0]))
        .collect();
    if !cups.is_empty() {
        prizes.push(badge(BadgeKind::TurnCups, "prize0.gif", cups, ""));
    }
    for (i, name) in PRIZE_NAMES.iter().enumerate().skip(1) {
        if flags & (1 << (i - 1)) != 0 {
            prizes.push(badge(
                BadgeKind::Prize(i as u8),
                &format!("prize{i}.gif"),
                *name,
                "",
            ));
        }
    }
    let (killed, kinds, max) = monster_list(monsters, config);
    if let Some(max) = max {
        let summary = format!("{kinds}種類{}{}", island.taiji, units.monster);
        let mut b = badge(
            BadgeKind::MonstersKilled,
            MONSTERS[max].image,
            killed.clone(),
            summary.clone(),
        );
        b.hover = hover(format!("{summary}退治"), vec![vec![killed]]);
        prizes.push(b);
    }

    // 出現中の怪獣
    let (live, kinds, max) = monster_list(island.monster_live_type, config);
    let live_badge = max.map(|max| {
        let mut b = badge(
            BadgeKind::LiveMonsters,
            MONSTERS[max].image,
            live.clone(),
            "",
        );
        b.hover = hover(
            format!("{kinds}種類{monster_live}{}{monsm}", units.monster),
            vec![vec![live.clone()]],
        );
        b
    });

    // へそくり
    let ([a9_text, a9b_text, ..], [auc9a, _, auc9c, ..]) = parse::<5>(scope, &island.auction.auc9);
    let savings = (config.hide_money_mode == HideMoneyMode::Rounded && auc9a >= 1).then(|| {
        let mut b = badge(BadgeKind::Savings, "auc.gif", "へそくり", "");
        b.hover = hover(
            "へそくり",
            vec![
                vec![
                    format!("貯金…{a9b_text}兆円"),
                    format!("Auction補助金…{}兆円", trunc(auc9c as f64 / 10000.0)),
                ],
                vec![format!("合計…{a9_text}兆円")],
            ],
        );
        b
    });

    // コメント (援助射撃の状態)
    let ([_, nokotan, msid], [msjotai, ..]) = parse::<3>(scope, &island.etc_raw[2]);
    // %HidToNumber は保存順の位置なのに、並べ替えたあとの @Hislands を引く (Perl 版のまま)。
    // ハッシュのキーは文字列なので "01" は島 1 にならない。見つからなければ先頭
    let pos = ctx
        .islands
        .iter()
        .position(|i| i.id.to_string() == msid)
        .unwrap_or(0);
    let target = ctx.islands[ctx.order[pos]].name.clone();
    let comment = if island.onm.is_empty() {
        CommentLine::Comment {
            comment: island.comment.clone(),
        }
    } else if msjotai == 1 {
        CommentLine::AidRequested {
            owner: island.onm.clone(),
            target,
            turns_left: nokotan.clone(),
        }
    } else if msjotai == 2 {
        CommentLine::AidAllowed {
            owner: island.onm.clone(),
            target,
            turns_left: nokotan,
        }
    } else {
        CommentLine::Owner {
            owner: island.onm.clone(),
            comment: island.comment.clone(),
        }
    };

    // 電力
    let (e3t, e3) = parse::<5>(scope, &island.eisei_raw[0]);
    let (ene, shouhi) = (&e3t[4], &e3t[1]);
    let sabun = e3[4] - e3[1];
    let mut power = badge(
        BadgeKind::Power,
        "ele.gif",
        format!("使用状況(消費{shouhi}万ｋＷ／過不足{sabun}万ｋＷ)"),
        if sabun < 0 { "不足中！" } else { "" },
    );
    power.hover = hover(
        "使用状況",
        vec![vec![
            format!("消費{shouhi}万ｋＷ"),
            format!("過不足{sabun}万ｋＷ"),
        ]],
    );

    // 人工衛星
    let mut satellites = Vec::new();
    const SATELLITES: [(&str, &str); 6] = [
        ("kisho.gif", "気象衛星"),
        ("kansoku.gif", "観測衛星"),
        ("geigeki.gif", "迎撃衛星"),
        ("gunji.gif", "軍事衛星"),
        ("bouei.gif", "防衛衛星"),
        ("ire.gif", "イレギュラー"),
    ];
    for (n, (image, name)) in SATELLITES.iter().enumerate() {
        let v = island.eis[n];
        if v >= 1 {
            satellites.push(badge(
                BadgeKind::Satellite(n as u8 + 1),
                image,
                *name,
                format!("{v}%"),
            ));
        }
    }
    let eis7 = island.eis[6];
    if eis7 >= 1 {
        let cstpop = eis7 / 100;
        let mut b = badge(
            BadgeKind::SpaceStation,
            "cst.gif",
            format!("宇宙ステーション／{cstpop}{}滞在", units.pop),
            format!("{}%", eis7 % 100 + 1),
        );
        b.hover = hover(
            "宇宙ステーション",
            vec![vec![
                format!("{cstpop}{}滞在", units.pop),
                format!("人口維持ロケット数…{}個", cstpop / 10000 + 1),
                format!("人口維持コスト…{cstpop}{}", units.money),
            ]],
        );
        satellites.push(b);
    }

    // 家畜
    let mut livestock = Vec::new();
    let s = &island.owner_stats;
    for (kind, image, name, count, unit, prod, price) in [
        (
            BadgeKind::Chicken,
            "niwatori.gif",
            "にわとり",
            s.tare,
            "万羽",
            100,
            10,
        ),
        (BadgeKind::Pig, "buta.gif", "ぶた", s.zipro, "万頭", 200, 20),
        (BadgeKind::Cow, "ushi.gif", "うし", s.leje, "万頭", 300, 50),
    ] {
        if count >= 1 {
            let mut b = badge(kind, image, name, format!("{count}{unit}"));
            b.hover = hover(
                name,
                vec![vec![
                    format!("{count}{unit}"),
                    format!("生産力{}トン", count * prod),
                    format!("売値{}{}", count * price, units.money),
                ]],
            );
            livestock.push(b);
        }
    }

    // 島主の家
    let [_, toto2, ..] = scope.fields::<7>(&island.etc_raw[3]);
    let pts = island.pts;
    let [
        mika,
        shuto,
        meka,
        oumu,
        anseki,
        tiseki,
        hyouseki,
        fuseki,
        enseki,
        kouseki,
        iseki,
        _,
    ] = uniq;
    let hlv = if pts > HOUSE_LEVELS[8]
        && enseki > 0
        && tiseki > 0
        && hyouseki > 0
        && fuseki > 0
        && mika > 0
        && shuto > 0
        && meka > 0
        && oumu > 0
        && iseki > 0
        && toto2 > 0
    {
        if kouseki > 0 || anseki > 0 {
            if anseki >= kouseki { 10 } else { 11 }
        } else {
            9
        }
    } else {
        (0..9)
            .rev()
            .find(|&l| pts > HOUSE_LEVELS[l])
            .map_or(0, |l| l + 1)
    };
    let eisei1 = island.eisei[0];
    let house = (eisei1 > 0).then(|| {
        let name = format!("{}{}", island.onm, HOUSE_NAMES[hlv]);
        let tax = trunc((pop * (hlv as i64 + 1) * eisei1) as f64 / 100.0);
        let mut b = badge(
            BadgeKind::House,
            &format!("house{hlv}.gif"),
            name.clone(),
            "",
        );
        b.hover = hover(
            name,
            vec![vec![format!("税率{eisei1}％({tax}{})", units.money)]],
        );
        b
    });

    // 首都の名前。0 でも 555 でもない数値なら前の島の値が残る (Perl 版のまま)
    let t2 = perl::num(&island.totoyoso2);
    if t2 == 0.0 {
        *shutoname = Some(island.totoyoso2.clone());
    } else if t2 == 555.0 {
        *shutoname = None;
    }

    // サッカーチーム
    let (
        [
            sto,
            std,
            stk,
            stwin,
            stdrow,
            stlose,
            stwint,
            stdrowt,
            stloset,
            styusho,
            _,
        ],
        e4,
    ) = parse::<11>(scope, &island.eisei_raw[1]);
    let stshoka = e4[10];
    let soccer = (stshoka >= 1).then(|| {
        let nn = soccer_status(stshoka);
        let record = format!(
            "チーム成績(勝点{}/{stwin}勝{stlose}敗{stdrow}分/通算{stwint}勝{stloset}敗{stdrowt}分/優勝{styusho}回)",
            e4[3] * 3 + e4[4]
        );
        let mut b = badge(
            BadgeKind::Soccer,
            "sc.gif",
            format!("{nn}(攻({sto})守({std})KP({stk}){record}"),
            "",
        );
        b.hover = hover(
            nn,
            vec![vec![
                format!("攻撃力({sto})"),
                format!("守備力({std})"),
                format!("キーパー能力({stk})"),
                record,
            ]],
        );
        b
    });

    // マスコット
    let ([mshp, msap, msdp, mssp, mswin, msexe, _], e5) = parse::<7>(scope, &island.eisei_raw[2]);
    let force: i64 = e5[..4].iter().sum();
    let tet = e5[6];
    let mascot = (tet >= 1 || e5[0] >= 1).then(|| {
        let (image, name) = if tet >= 1 {
            ("tet.gif", "超神獣テトラ")
        } else {
            ("ms.gif", "マスコットいのら")
        };
        let mut b = badge(
            BadgeKind::Mascot,
            image,
            format!("{name}(HP{mshp}.AP{msap}.DP{msdp}.SP{mssp}/{mswin}匹撃破/経験値{msexe})"),
            format!("Sum({force})"),
        );
        b.hover = hover(
            name,
            vec![vec![
                format!("HP {mshp}　AP {msap}"),
                format!("DP {msdp}　SP {mssp}"),
                format!("{mswin}匹撃破"),
                format!("経験値{msexe}"),
            ]],
        );
        b
    });

    // お守り
    let ([toto1, toto2, ..], t8) = parse::<7>(scope, &island.etc_raw[3]);
    if t8[0] >= 1 || t8[1] >= 1 {
        let mut b = badge(
            BadgeKind::Amulet,
            "omamori.gif",
            format!("toto的中回数({toto1})/お守り残数({toto2})"),
            format!("残り({toto2})"),
        );
        b.hover = hover(
            "お守り",
            vec![vec![
                format!("toto的中回数…{toto1}回"),
                format!("お守り残数…{toto2}個"),
            ]],
        );
        prizes.push(b);
    }

    info.extend(soccer);
    info.extend(unique);
    info.extend(house);
    info.extend(live_badge);
    if !monsm.is_empty() {
        info.push(Badge {
            kind: BadgeKind::MonsterAppearing,
            image: None,
            alt: String::new(),
            hover: None,
            text: monsm.to_string(),
        });
    }
    info.extend(mascot);
    info.extend(livestock);
    info.extend(satellites);
    info.push(power);

    IslandRow {
        rank: ctx.rank,
        id: island.id,
        name: island.name.clone(),
        absent: island.absent,
        capital: shutoname.clone(),
        pts,
        unemployment: (pop != 0).then(|| format!("{unemployed:.2}%")),
        unemployment_negative: unemployed < 0.0,
        tourists: if eisei2nd == 0 {
            "通算観光者数１万人未満".to_string()
        } else {
            format!("通算観光者数{eisei2nd}万人")
        },
        last_turn: LastTurn {
            pts: signed(s.monta, "pts."),
            pop: signed(s.hamu, &units.pop),
            money: signed(s.pika, &units.money),
        },
        pop: format!("{pop}{}", units.pop),
        area: format!("{}{}", island.area, units.area),
        money: money_for_others(island.money, config.hide_money_mode, &units.money),
        savings,
        food: format!("{}{}", island.food, units.food),
        farm: scale(farm),
        factory: scale(factoryt),
        mountain: scale(mountain),
        power: format!("{ene}万ｋＷ"),
        military: format!("Ｌｖ{}", military_level(s.rena)),
        info,
        prizes,
        departments: ctx.departments.to_vec(),
        toto: island.eis8.clone(),
        comment,
    }
}

#[cfg(test)]
mod tests;
