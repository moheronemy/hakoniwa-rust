//! 開発画面 (`tempOwner` hako-map.cgi 2936〜3423 行、`tempCommand` 3424〜3753 行) に出す情報。
//!
//! 地図と島の情報の表 (`islandMap`, `islandInfo`) は [`super`] のほかのモジュールが受け持つ。
//! ここでは次のものを返す:
//!
//! - [`command_menu`] — 計画入力のフォーム: 計画番号・計画の種類と値段 (コスト修正の後)・
//!   座標・数量・目標の島、マスターパスワードのときの「いじり」の選択肢
//! - [`plan_lines`] — 入力済みの計画の一覧 (`tempCommand`) の文面
//! - [`owner_screen`] — 上の 2 つに加えて、政策の予算・ハコオク・コメントの更新・
//!   援助射撃の申請・観光する島・ローカル掲示板の削除番号のフォームの中身
//!
//! 文面は Perl 版の HTML からタグ (色・太字) を除いたもの。島の名前などは保存されている
//! とおり (HTML エスケープ済み) で入るので、HTML に出すときにもう一度エスケープしない。
//!
//! # Perl 版の癖で、再現していること
//!
//! - 「オークション出品」の選択肢の値段と選択状態は、その直前の計画 (全計画を白紙撤回) の
//!   ものがそのまま使われる (変数の使い回し)
//! - 計画の一覧で `$HcomMissileWP` は定義されていない (= 0) ので、計画番号 0 はミサイルとして
//!   書かれる
//! - 衛星・魔法・畜産の種類の名前 `$t` は一覧の行をまたいで残る変数で、数量が負など
//!   どの名前にも当たらないときは前の行の名前が出る
//! - ハコオクの出品の表示: 3 枠目の「お守り」は 2 枠目の値を使う。出品の計画の条件は
//!   順位 50 位未満、「(出品可能)」の表示は 51 位未満
//! - `$s =~ /^([0-9]*),...$/` が合わないときは前に合った値が残る。ただし
//!   `islandInfo` など、この画面の前の部分で合ったものまではたどらず、空から始める

use crate::GameConfig;
use crate::actions::policy::Policy;
use crate::land::land_name;
use crate::model::{GameState, Island};
use crate::perl::{self, num, num_to_string};
use crate::tables::{COMMAND_LIST, CommandKind, HOUSE_LEVELS, MONSTERS, MONUMENTS, SHIPS};

/// 開発画面に並べる計画の数 (`$HcommandTotal`)。[`COMMAND_LIST`] の先頭からこの数だけ出す
/// (残りの「オークション出品」と「いじり」は条件付きで別に出す)
pub const COMMAND_TOTAL: usize = 90;

/// 選択肢 1 つ (`<OPTION VALUE=value SELECTED>label`)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Choice {
    pub value: i64,
    pub label: String,
    /// Perl 版が `SELECTED` を付けるか (いじりの選択肢では複数に付く。HTML では最後のものが効く)
    pub selected: bool,
}

/// 計画の種類の選択肢
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CommandChoice {
    /// 計画番号 (フォームの `COMMAND` の値)
    pub kind: u16,
    /// 計画の名前 (`$HcomName`)
    pub name: String,
    /// 値段の表示 (`1200億円`、`100トン`、`無料`)。「いじり」には無い
    pub cost: Option<String>,
    pub selected: bool,
}

impl CommandChoice {
    /// Perl 版の選択肢の文面 (`整地(4億円)`)
    pub fn label(&self) -> String {
        match &self.cost {
            Some(c) => format!("{}({c})", self.name),
            None => self.name.clone(),
        }
    }
}

/// コスト修正の説明 (計画の選択肢にマウスを載せたときに出る `コスト修正(...)` と内訳)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CostModifier {
    /// 全体の倍率。1 なら `なし`、そうでなければ `x0.941` の形
    pub total: String,
    /// 内訳の行 (`所持資金…x1`、`開発度修正…x2`、`文部科学省…x0.782`、
    /// `ハイテク多国籍企業…x0.666`、`ハイテク多国籍企業・改…x0.9`、`経済大学(貯金中)…x0.903`)
    pub details: Vec<String>,
}

/// フォームの既定の選択 (Perl 版はクッキーと、直前に送った計画入力のフォームから取る:
/// `KIND` / `COMMAND`、`POINTX`、`POINTY`、`LAMOUNT1`、`LAMOUNT2`)。
/// 値は受け取った文字列のまま渡す (Perl 版と同じく数値として比べる。空は 0 と同じ)
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct MenuDefaults {
    pub kind: String,
    pub x: String,
    pub y: String,
    pub lamount1: String,
    /// いじりの `LAMOUNT2` の入力欄の初期値 (Perl 版は直前の入力を `cutColumn(…, 40)` して出す)
    pub lamount2: String,
}

/// 計画入力のフォーム
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CommandMenu {
    /// 計画番号 (`NUMBER`、値 0 始まり・表示 1 始まり)
    pub plan_numbers: Vec<Choice>,
    /// 計画の種類 (`COMMAND`)
    pub commands: Vec<CommandChoice>,
    pub cost_modifier: CostModifier,
    /// 座標 (`POINTX`, `POINTY`)
    pub xs: Vec<Choice>,
    pub ys: Vec<Choice>,
    /// マスターパスワードで開いたときだけ: いじりの対象 (`LAMOUNT1`) と値の欄 (`LAMOUNT2`)
    pub ijiri: Option<IjiriChoices>,
    /// 数量 (`AMOUNT`、0〜99。いじりのときは 0 が「単体」、1 が「一括」)
    pub amounts: Vec<Choice>,
    /// 目標の島 (`TARGETID`、自分の島が選ばれている)
    pub targets: Vec<Choice>,
}

/// いじりの選択肢
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IjiriChoices {
    /// `LAMOUNT1`: 負の値は島の値 (すべて `SELECTED` 付き、Perl 版のまま)、0〜70 は地形
    pub lamount1: Vec<Choice>,
    /// `LAMOUNT2` の初期値
    pub lamount2: String,
}

/// 入力済みの計画 1 行
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlanLine {
    /// 計画番号 (1 始まり)
    pub number: usize,
    /// 計画の種類の番号 (保存されている値)
    pub kind: u16,
    /// 文面 (`(3,4)で整地`、`ほげ島(1,2)へミサイル発射(3発)` など)
    pub text: String,
}

impl PlanLine {
    /// Perl 版の表示 (`01：(3,4)で整地`)
    pub fn numbered(&self) -> String {
        format!("{:02}：{}", self.number, self.text)
    }
}

/// 政策の予算の 1 行 (政策のボタンと `予算3兆円/消費電力-4%` の文面)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PolicyLine {
    pub policy: Policy,
    pub text: String,
}

/// ハコオクの出品 1 枠
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuctionLot {
    /// 品番 (1〜3)
    pub number: usize,
    /// 品物 (`サッカーチーム力1.05倍`、島の出品なら出品名)
    pub item: String,
    /// 最低入札額 (保存されている文字列のまま。`兆円以上` を付けて出す)
    pub min_bid: String,
    /// `(落札済み)` か `(残り3ターン)`
    pub status: String,
}

impl AuctionLot {
    /// Perl 版の表示 (`①品物／120兆円以上(残り3ターン)`)
    pub fn text(&self) -> String {
        let mark = ["①", "②", "③"][(self.number - 1).min(2)];
        format!(
            "{mark}{}／{}兆円以上{}",
            self.item, self.min_bid, self.status
        )
    }
}

/// ハコオクのフォーム
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuctionPanel {
    /// 「(出品可能)」を出すか (51 位未満、`auc6` の先頭が 1、どれかの枠が「今回はお休み」)
    pub can_list: bool,
    /// 入札できるか (`auc6` の先頭が 2 以下)。できなければ「(入札不可)」を出し、入札の
    /// ボタンを出さない
    pub can_bid: bool,
    /// 出品の表示 (3 枠目は 21 位以下の島にだけ出る)
    pub lots: Vec<AuctionLot>,
    /// 品番 (`AUCNUMBER`)
    pub lot_numbers: Vec<Choice>,
    /// 金額 (`AMOUNT`、1〜99 兆円を上乗せ)
    pub amounts: Vec<Choice>,
}

/// コメントの更新と援助射撃の申請のフォーム
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CommentForm {
    /// いまのコメント (`MESSAGE` の初期値、保存されているとおり)
    pub comment: String,
    /// 「各種予想」のボタン (`TotoButton`) を出すか: ターン数を 100 で割った余りが 0〜25 か 50〜75
    pub prediction: bool,
    /// 「首都名変更」のボタン (`TotosButton`) を出すか: `totoyoso2` が数値として 0
    pub capital_name: bool,
    /// 目標の島 (`TARGETID`、自分の島が選ばれている)
    pub targets: Vec<Choice>,
    /// 有効ターン数 (`AMOUNT`、0〜24)
    pub turns: Vec<Choice>,
    /// 自分の島に援助射撃を申請している島 (`〇〇島` の形、島の並び順)
    pub missile_requests: Vec<String>,
}

impl CommentForm {
    /// 申請が届いているときの文面 (Perl 版は `★…★` で囲んで出す)
    pub fn missile_request_notice(&self) -> Option<String> {
        if self.missile_requests.is_empty() {
            return None;
        }
        let names: String = self
            .missile_requests
            .iter()
            .map(|n| format!("{n}、"))
            .collect();
        Some(format!(
            "{names}から、あなたの島への援助射撃の申請が届いてます。"
        ))
    }
}

/// 開発画面の、地図と島の情報の表を除いた中身
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OwnerScreen {
    pub menu: CommandMenu,
    /// 政策 (`etc5` の先頭が 0 でない島だけ。計画入力のフォームの下に出て、数量の欄を使う)
    pub policies: Option<Vec<PolicyLine>>,
    /// 観光する島 (`TARGETID`、自分の島が選ばれている)
    pub sightseeing_targets: Vec<Choice>,
    pub auction: AuctionPanel,
    pub plans: Vec<PlanLine>,
    pub comment: CommentForm,
    /// ローカル掲示板の削除の番号 (`NUMBER`、値 0 始まり・表示 1 始まり)
    pub lbbs_numbers: Vec<Choice>,
}

/// `$s =~ /^([0-9]*),...,([0-9]*)$/` の `$1`.. (文字列のまま)。合わなければ前に合った値が残る
#[derive(Debug, Default)]
struct Caps(Vec<String>);

impl Caps {
    fn fields(&mut self, s: &str, n: usize) -> Vec<String> {
        let parts: Vec<&str> = s.split(',').collect();
        if parts.len() == n && parts.iter().all(|p| p.bytes().all(|b| b.is_ascii_digit())) {
            self.0 = parts.iter().map(|p| p.to_string()).collect();
        }
        (0..n)
            .map(|i| self.0.get(i).cloned().unwrap_or_default())
            .collect()
    }
}

/// Perl の配列の添字 (負なら後ろから、範囲外は空)
fn perl_index<T: Copy>(list: &[T], i: i64) -> Option<T> {
    let i = if i < 0 { list.len() as i64 + i } else { i };
    usize::try_from(i).ok().and_then(|i| list.get(i).copied())
}

fn command_name(kind: u16) -> String {
    CommandKind::from_u16(kind)
        .map(|k| k.name().to_string())
        .unwrap_or_default()
}

fn command_cost(kind: u16) -> i64 {
    CommandKind::from_u16(kind).map(|k| k.cost()).unwrap_or(0)
}

/// 自分の島を選んだ島の一覧 (`getIslandList($defaultID)`)
fn island_list(game: &GameState, current_id: i64) -> Vec<Choice> {
    game.world
        .islands
        .iter()
        .map(|i| Choice {
            value: i.id,
            label: format!("{}島", i.name),
            selected: i.id == current_id,
        })
        .collect()
}

fn numbers(range: std::ops::Range<i64>, offset: i64) -> Vec<Choice> {
    range
        .map(|i| Choice {
            value: i,
            label: (i + offset).to_string(),
            selected: false,
        })
        .collect()
}

/// `$HdefaultX` などとの比較で選ぶ数の選択肢
fn numbers_selected(range: std::ops::Range<i64>, default: &str) -> Vec<Choice> {
    let d = num(default);
    range
        .map(|i| Choice {
            value: i,
            label: i.to_string(),
            selected: i as f64 == d,
        })
        .collect()
}

/// 計画の値段の表示 (0 は無料、負は食料)
fn cost_text(cost: f64, config: &GameConfig) -> String {
    if cost == 0.0 {
        "無料".into()
    } else if cost < 0.0 {
        format!("{}{}", num_to_string(-cost), config.units.food)
    } else {
        format!("{}{}", num_to_string(cost), config.units.money)
    }
}

/// `tempOwner` が計画の値段に掛ける倍率
struct CostFactors {
    /// 開発度 (`$costx`)
    costx: f64,
    htf: f64,
    shtf: f64,
    co95: f64,
    costco95: f64,
    s00: f64,
    costseisaku2: f64,
    costmoney: f64,
    modifier: CostModifier,
}

fn cost_factors(config: &GameConfig, island: &Island, caps: &mut Caps) -> CostFactors {
    let pts = island.pts;
    let h = HOUSE_LEVELS;
    let costx = if pts > h[8] {
        2.0
    } else if pts > h[6] {
        1.8
    } else if pts > h[4] {
        1.6
    } else if pts > h[2] {
        1.4
    } else if pts > h[1] {
        1.2
    } else {
        1.0
    };
    let mut details = Vec::new();
    let mut shusei;
    let costxx = if !config.another_mode {
        shusei = costx;
        Some(format!("開発度修正…x{}", num_to_string(costx)))
    } else {
        shusei = 1.0;
        None
    };

    // ($factory1, $factory2, $co0, $co1, $htf, $shtf, $co95, $co95, $co95, $co95):
    // co95 には最後の欄が入る
    let f = caps.fields(&island.factory, 10);
    let (htf, shtf, co95) = (num(&f[4]), num(&f[5]), num(&f[9]));
    let mut costco95 = perl::trunc(0.975f64.powf(co95) * 1000.0) as f64 / 1000.0;
    if costco95 < 0.9 {
        costco95 = 0.9;
    }
    let mut late = Vec::new();
    if htf > 0.0 {
        late.push("ハイテク多国籍企業…x0.666".to_string());
        shusei = shusei * 2.0 / 3.0;
    } else if shtf > 0.0 {
        late.push("ハイテク多国籍企業・改…x0.9".to_string());
        shusei = shusei * 9.0 / 10.0;
    }
    if co95 > 0.0 {
        late.push(format!("経済大学(貯金中)…x{}", num_to_string(costco95)));
        shusei *= costco95;
    }

    let s = caps.fields(&island.etc_raw[0], 31);
    let s00 = num(&s[0]);
    let sum: f64 = s[1..].iter().map(|v| num(v)).sum();
    let mut costseisaku2 = perl::trunc(0.9975f64.powf(sum) * 1000.0) as f64 / 1000.0;
    if costseisaku2 < 0.75 {
        costseisaku2 = 0.75;
    }
    let seisaku3 = if s00 > 0.0 {
        shusei *= costseisaku2;
        Some(format!("文部科学省…x{}", num_to_string(costseisaku2)))
    } else {
        None
    };

    let s12b = (perl::trunc(num(&s[12]) / 5.0) + 1).min(10) as f64;
    let costmoney =
        perl::trunc((island.money as f64 / 5.0 / (999999.0 * s12b) + 0.8) * 1000.0) as f64 / 1000.0;
    details.push(format!("所持資金…x{}", num_to_string(costmoney)));
    shusei *= costmoney;
    let shusei = perl::trunc(shusei * 1000.0) as f64 / 1000.0;
    let total = if shusei == 1.0 {
        "なし".to_string()
    } else {
        format!("x{}", num_to_string(shusei))
    };
    details.extend(costxx);
    details.extend(seisaku3);
    details.extend(late);

    CostFactors {
        costx,
        htf,
        shtf,
        co95,
        costco95,
        s00,
        costseisaku2,
        costmoney,
        modifier: CostModifier { total, details },
    }
}

/// 計画 `kind` の、開発画面に出す値段 (`tempOwner` の `$cost`)
fn menu_cost(config: &GameConfig, island: &Island, f: &CostFactors, kind: CommandKind) -> f64 {
    use CommandKind as K;
    let pts = island.pts as f64;
    let mut cost = kind.cost() as f64;
    if config.another_mode {
        match kind {
            K::House | K::Kai => cost = pts * 2.0,
            K::Boku2 => cost = pts * 4.0,
            _ => {}
        }
    } else {
        match kind {
            K::House => cost = pts * 3.0,
            K::Bettown | K::Kai => cost = pts,
            K::Boku2 => cost = pts * 4.0,
            _ => {}
        }
    }
    let excluded = matches!(
        kind,
        K::Kura | K::Kura2 | K::Kuraf | K::Sell | K::Money | K::Food | K::Givefood
    );
    let no_costx = excluded
        || matches!(
            kind,
            K::House | K::Bettown | K::Kai | K::Boku2 | K::EneCs | K::EneNF | K::Eisei
        );
    if !config.another_mode && !no_costx {
        cost *= f.costx;
    }
    if excluded {
        return cost;
    }
    let int = |x: f64| perl::trunc(x) as f64;
    if f.htf > 0.0 {
        cost = int(cost * 2.0 / 3.0);
    } else if f.shtf > 0.0 {
        cost = int(cost * 9.0 / 10.0);
    }
    if f.co95 > 0.0 {
        cost = int(cost * f.costco95);
    }
    if f.s00 > 0.0 {
        cost = int(cost * f.costseisaku2);
    }
    int(cost * f.costmoney)
}

/// ハコオクの出品 3 枠 (`$auction1`..`$auction3`)。無い枠は空文字列
fn lot_strings(game: &GameState) -> [&str; 3] {
    std::array::from_fn(|i| {
        game.world
            .auction_lots
            .get(i)
            .map(String::as_str)
            .unwrap_or("")
    })
}

/// 計画入力のフォーム (`tempOwner` の前半)。
///
/// `master` はマスターパスワードで開いたとき (Perl 版の `$HmainMode2 eq 'ijiri'`)。
/// `defaults` は既定の選択 ([`MenuDefaults`])
pub fn command_menu(
    config: &GameConfig,
    game: &GameState,
    island_idx: usize,
    master: bool,
    defaults: &MenuDefaults,
) -> CommandMenu {
    let island = &game.world.islands[island_idx];
    let mut caps = Caps::default();
    let f = cost_factors(config, island, &mut caps);

    let mut commands = Vec::new();
    if master {
        commands.push(CommandChoice {
            kind: CommandKind::Ijiri as u16,
            name: CommandKind::Ijiri.name().into(),
            cost: None,
            selected: false,
        });
    }
    let default_kind = num(&defaults.kind);
    let mut last = (String::new(), false);
    for &kind in &COMMAND_LIST[..COMMAND_TOTAL] {
        let cost = cost_text(menu_cost(config, island, &f, kind), config);
        let selected = kind as u16 as f64 == default_kind;
        last = (cost.clone(), selected);
        commands.push(CommandChoice {
            kind: kind as u16,
            name: kind.name().into(),
            cost: Some(cost),
            selected,
        });
    }

    // オークション出品: 値段と選択状態は直前の計画のもの (Perl 版のまま)
    let rank = island_idx + 1;
    let auc6a = num(&caps.fields(&island.auction.auc6, 3)[0]);
    let shuppin: Vec<f64> = lot_strings(game)
        .iter()
        .map(|l| num(&caps.fields(l, 5)[0]))
        .collect();
    if rank < 50 && auc6a == 1.0 && shuppin.contains(&29.0) {
        commands.push(CommandChoice {
            kind: CommandKind::Auction as u16,
            name: CommandKind::Auction.name().into(),
            cost: Some(last.0),
            selected: last.1,
        });
    }

    let size = config.island_size as i64;
    let ijiri = master.then(|| {
        const VALUES: [(i64, &str); 18] = [
            (-15, "動物園入荷"),
            (-10, "お守り数"),
            (-9, "気象衛星"),
            (-8, "観測衛星"),
            (-7, "迎撃衛星"),
            (-6, "軍事衛星"),
            (-5, "防衛衛星"),
            (-4, "イレギュラー"),
            (-3, "首都の名前"),
            (-2, "宇宙ステ人口"),
            (-18, "サッカー(KP)"),
            (-17, "サッカー(守)"),
            (-16, "サッカー(攻)"),
            (-14, "生物大ＳＰ"),
            (-13, "生物大ＤＰ"),
            (-12, "生物大ＡＰ"),
            (-11, "生物大ＨＰ"),
            (-1, "生物大経験値"),
        ];
        let d = num(&defaults.lamount1);
        let mut lamount1: Vec<Choice> = VALUES
            .iter()
            .map(|&(value, label)| Choice {
                value,
                label: label.into(),
                selected: true,
            })
            .collect();
        lamount1.extend((0..71).map(|i| Choice {
            value: i,
            label: land_name(i as u8, 0),
            selected: i as f64 == d,
        }));
        IjiriChoices {
            lamount1,
            lamount2: defaults.lamount2.clone(),
        }
    });
    let amounts = (0..100)
        .map(|i| Choice {
            value: i,
            label: match (master, i) {
                (true, 0) => "単体".into(),
                (true, 1) => "一括".into(),
                _ => i.to_string(),
            },
            selected: false,
        })
        .collect();

    CommandMenu {
        plan_numbers: numbers(0..config.command_max as i64, 1),
        commands,
        cost_modifier: f.modifier,
        xs: numbers_selected(0..size, &defaults.x),
        ys: numbers_selected(0..size, &defaults.y),
        ijiri,
        amounts,
        targets: island_list(game, island.id),
    }
}

/// 衛星の種類の名前 (`$t`)。数量が 1〜6, 99 のどれでもなければ `t` は変わらない
fn satellite_name(arg: i64, t: &mut String) {
    let arg = if arg == 99 {
        99
    } else if arg >= 7 || arg == 0 {
        1
    } else {
        arg
    };
    let name = match arg {
        1 => "気象衛星",
        2 => "観測衛星",
        3 => "迎撃衛星",
        4 => "軍事衛星",
        5 => "防衛衛星",
        6 => "イレギュラー",
        99 => "宇宙ステーション",
        _ => return,
    };
    *t = name.into();
}

/// 入力済みの計画の一覧 (`tempCommand` を計画の数だけ)
pub fn plan_lines(config: &GameConfig, game: &GameState, island_idx: usize) -> Vec<PlanLine> {
    let island = &game.world.islands[island_idx];
    // $t と正規表現の $1.. は行をまたいで残る
    let mut t = String::new();
    let mut caps = Caps::default();
    island
        .commands
        .iter()
        .take(config.command_max)
        .enumerate()
        .map(|(i, c)| PlanLine {
            number: i + 1,
            kind: c.kind,
            text: plan_text(config, game, island, c, &mut t, &mut caps),
        })
        .collect()
}

fn plan_text(
    config: &GameConfig,
    game: &GameState,
    island: &Island,
    c: &crate::model::PlannedCommand,
    t: &mut String,
    caps: &mut Caps,
) -> String {
    use CommandKind as K;
    let kind = c.kind;
    let mut arg = c.arg;
    let name = command_name(kind);
    let point = format!("({},{})", c.x, c.y);
    let target_name = game
        .world
        .island_by_id(c.target)
        .map(|i| i.name.as_str())
        .unwrap_or("");
    let target = if target_name.is_empty() {
        "無人島".to_string()
    } else {
        format!("{target_name}島")
    };
    let unit_cost = command_cost(kind);
    let mut value = arg as f64 * unit_cost as f64;
    if value == 0.0 {
        value = unit_cost as f64;
    }
    let value = if value < 0.0 {
        format!("{}{}", num_to_string(-value), config.units.food)
    } else {
        format!("{}{}", num_to_string(value), config.units.money)
    };
    let monster = |a: i64| {
        perl_index(&MONSTERS, a)
            .map(|m| m.name.to_string())
            .unwrap_or_default()
    };
    let is = |k: K| kind == k as u16;

    if is(K::DoNothing) || is(K::Giveup) {
        return name;
    }
    // $HcomMissileWP は定義されていない (0) ので、計画番号 0 もミサイルになる (Perl 版のまま)
    if kind == 0
        || [
            K::MissileNM,
            K::MissilePP,
            K::MissileSPP,
            K::MissileST,
            K::MissileSS,
            K::MissileLR,
            K::MissileLD,
        ]
        .into_iter()
        .any(is)
    {
        let n = if arg == 0 {
            "無制限".to_string()
        } else {
            format!("{arg}発")
        };
        return format!("{target}{point}へ{name}({n})");
    }
    if is(K::Taishi) || is(K::EiseiLzr) {
        return format!("{target}{point}へ{name}");
    }
    if is(K::EiseiAtt) {
        satellite_name(arg, t);
        return format!("{target}の{t}へ{name}");
    }
    if is(K::Magic) {
        if arg >= 8 {
            arg = 0;
        }
        const MAGIC: [&str; 8] = [
            "炎系魔術師派遣",
            "氷系魔術師派遣",
            "地系魔術師派遣",
            "風系魔術師派遣",
            "光系魔術師派遣",
            "闇系魔術師派遣",
            "天空城砲撃",
            "動物園飼育係派遣",
        ];
        if let Some(m) = usize::try_from(arg).ok().and_then(|a| MAGIC.get(a)) {
            *t = m.to_string();
        }
        return format!("{target}{point}へ{t}");
    }
    if is(K::SendMonster) {
        return format!("{target}へ{name}({})", monster(arg.min(30)));
    }
    if is(K::Sell) {
        return format!("{name}{value}");
    }
    if is(K::Propaganda) {
        return if arg == 0 {
            name
        } else {
            format!("{name}({arg}回)")
        };
    }
    if is(K::Eisei) {
        satellite_name(arg, t);
        return format!("{t}打ち上げ");
    }
    if is(K::Eiseimente) {
        satellite_name(arg, t);
        return format!("{t}修復");
    }
    if is(K::Money) || is(K::Food) {
        return format!("{target}へ{name}{value}");
    }
    if is(K::EneGive) {
        return format!("{target}へ{name}({arg}00kW)");
    }
    if is(K::Destroy) {
        return if arg != 0 {
            format!("{point}で{name}(予算{value})")
        } else {
            format!("{point}で{name}")
        };
    }
    if is(K::Mine) {
        let a = if arg == 0 { 1 } else { arg.min(9) };
        return format!("{point}で{name}(ダメージ{a})");
    }
    if is(K::Zoo) {
        return format!("{point}で{name}(もしくは{}脱出)", monster(arg.min(30)));
    }
    if is(K::Train) {
        let a = if arg > 9 { 0 } else { arg };
        return format!("{point}で{name}(指定{a})");
    }
    if is(K::Kura) {
        let a = if arg == 0 { 1 } else { arg };
        return format!("{point}で{name}({a}兆円)");
    }
    if is(K::Kuraf) {
        let a = if arg == 0 { 1 } else { arg.min(9) };
        return format!("{point}で{name}({a}00万トン)");
    }
    if is(K::Kura2) {
        let a = if arg == 0 { 1 } else { arg };
        return format!("{point}で{name}({a}兆円or{a}00万トン)");
    }
    if is(K::Fune) {
        let a = if arg == 0 { 1 } else { arg };
        let ship = perl_index(&SHIPS, a).map(|s| s.0).unwrap_or("");
        return format!("{point}で{name}({ship})");
    }
    if is(K::Monument) {
        let m = perl_index(&MONUMENTS, arg).map(|m| m.0).unwrap_or("");
        return format!("{point}で{name}({m})");
    }
    if is(K::Farmcpc) {
        if arg >= 4 || arg == 0 {
            arg = 1;
        }
        match arg {
            1 => *t = "養鶏場".into(),
            2 => *t = "養豚場".into(),
            3 => *t = "牧場".into(),
            _ => {}
        }
        return format!("{point}で{name}({t})");
    }
    if is(K::College) {
        let s = caps.fields(&island.etc_raw[0], 31);
        let s10b = perl::trunc(num(&s[10]) / 5.0) + 1;
        if num(&s[0]) > 0.0 && arg < 10 && arg != 0 && arg - 1 < s10b {
            const COLLEGES: [&str; 9] = [
                "農業大学",
                "工業大学",
                "総合大学",
                "軍事大学",
                "生物大学",
                "気象大学",
                "経済大学",
                "魔法学校",
                "電工大学",
            ];
            if let Some(c) = usize::try_from(arg - 1).ok().and_then(|a| COLLEGES.get(a)) {
                *t = c.to_string();
            }
            return format!("{point}で{name}({t})");
        }
        return format!("{point}で{name}");
    }
    let counted = [
        K::Farm,
        K::Foodim,
        K::Factory,
        K::Nursery,
        K::EneAt,
        K::EneFw,
        K::EneWt,
        K::EneBo,
        K::EneWd,
        K::EneSo,
        K::EneCs,
        K::Boku,
        K::Park,
        K::Umiamu,
        K::Kai,
        K::HTget,
        K::Givefood,
        K::Mountain,
    ];
    if counted.into_iter().any(is) && arg != 0 {
        return format!("{point}で{name}({arg}回)");
    }
    format!("{point}で{name}")
}

/// 政策の予算 (`islandInfo` が作る `$seisaku`)。`etc5` の先頭が 0 なら出さない
fn policies(island: &Island) -> Option<Vec<PolicyLine>> {
    let s = Caps::default().fields(&island.etc_raw[0], 31);
    if num(&s[0]) == 0.0 {
        return None;
    }
    let b = |i: usize, d: f64| perl::trunc(num(&s[i]) / d);
    let s04b = b(4, 10.0);
    let s06b = b(6, 5.0);
    let s08b = b(8, 5.0);
    let s10b = (b(10, 5.0) + 1).min(9);
    let s12b = (b(12, 5.0) + 1).min(10);
    let line = |policy, text: String| PolicyLine { policy, text };
    Some(vec![
        line(
            Policy::Shouene,
            format!("予算{}兆円/消費電力-{}%", s[1], s[2]),
        ),
        line(Policy::Kyouiku, format!("予算{}兆円/指定可能+{s10b}", s[9])),
        line(Policy::Bousai, format!("予算{}兆円/予測精度+{s04b}", s[3])),
        line(Policy::Kankou, format!("予算{}兆円/人気+{s06b}", s[5])),
        line(Policy::Sizen, format!("予算{}兆円/清浄+{s08b}", s[7])),
        line(Policy::Chochiku, format!("予算{}兆円/貯蓄{s12b}倍", s[11])),
    ])
}

/// ハコオクの品物の名前 (`islandMap` の `$ac1`..`$ac3`)。
/// `value` は表示に使う値 (海あみゅなどは 1000 倍にして書き戻す)、`first` は 1 枠目か
/// (品番 0 が「？」になる。2・3 枠目は「闇石」)
fn lot_item(
    game: &GameState,
    shuppin: f64,
    value: &mut String,
    first: bool,
    dashi: &mut String,
) -> String {
    let v = value.clone();
    let mul = |value: &mut String| {
        *value = num_to_string(num(value) * 1000.0);
        value.clone()
    };
    match shuppin as i64 {
        _ if shuppin.fract() != 0.0 => "？".into(),
        0 if first => "？".into(),
        0 | 13 => "闇石".into(),
        1 => "地石".into(),
        2 => "氷石".into(),
        3 => "風石".into(),
        4 => "炎石".into(),
        5 => "光石".into(),
        6 => "天使ミカエル".into(),
        7 => "アイススコーピオン".into(),
        8 => "スライムレジェンド".into(),
        9 => format!("お守り{v}個"),
        10 => format!("海あみゅ{}人規模", mul(value)),
        11 => format!("食研{}人規模", mul(value)),
        12 => format!("コスモ{v}万ｋＷ"),
        14 => "衛星６種".into(),
        15 => "宇宙ステーション".into(),
        16 => "黄金のコンデンサ".into(),
        17 => format!("金山{}人規模", mul(value)),
        18 => format!("養殖場{}人規模", mul(value)),
        19 => "人造怪獣f02".into(),
        20 => "魔王サタン".into(),
        21 => "unknown".into(),
        22 => format!("サッカーチーム力1.{v}倍"),
        23 => format!("生物大学能力1.{v}倍"),
        24 => format!("生物大学経験値{v}"),
        25 => "卵".into(),
        26 => "生物大学".into(),
        27 => format!("風力{v}万ｋＷ"),
        28 => format!("バイオマス{v}万ｋＷ"),
        29 => "今回はお休み".into(),
        30 => {
            // 出品した島の出品名 ($dashiname は枠をまたいで残る)
            for i in &game.world.islands {
                if num(&v) == i.id as f64 {
                    *dashi = i.auction.auc7.clone();
                }
            }
            dashi.clone()
        }
        _ => "？".into(),
    }
}

/// 開発画面の、地図と島の情報の表を除いた中身 (`tempOwner`、`islandInfo` の
/// 政策・ボタンの部分、`islandMap` のハコオクの部分、`tempLbbsInputOW` の削除番号)
pub fn owner_screen(
    config: &GameConfig,
    game: &GameState,
    island_idx: usize,
    master: bool,
    defaults: &MenuDefaults,
) -> OwnerScreen {
    let island = &game.world.islands[island_idx];
    let rank = island_idx + 1;
    let turn = game.world.turn % 100;

    // islandMap の正規表現の並び (eisei5, eisei4, etc9, etc6, auc6, 出品 3 枠)
    let mut caps = Caps::default();
    caps.fields(&island.eisei_raw[2], 7);
    caps.fields(&island.eisei_raw[1], 11);
    caps.fields(&island.etc_raw[4], 7);
    caps.fields(&island.etc_raw[1], 31);
    let auc6a = num(&caps.fields(&island.auction.auc6, 3)[0]);
    let mut dashi = String::new();
    let mut lots = Vec::new();
    let mut shuppin = Vec::new();
    let mut value2 = String::new();
    for (n, lot) in lot_strings(game).iter().enumerate() {
        let a = caps.fields(lot, 5);
        let s = num(&a[0]);
        shuppin.push(s);
        let mut value = a[1].clone();
        // 3 枠目の「お守り」は 2 枠目の値を使う (Perl 版のまま)
        let item = if n == 2 && s == 9.0 {
            format!("お守り{value2}個")
        } else {
            lot_item(game, s, &mut value, n == 0, &mut dashi)
        };
        if n == 1 {
            value2 = value.clone();
        }
        let jo = num(&a[2]);
        let status = if jo == 15.0 {
            "(落札済み)".to_string()
        } else {
            format!("(残り{}ターン)", num_to_string(15.0 - jo))
        };
        lots.push(AuctionLot {
            number: n + 1,
            item,
            min_bid: a[3].clone(),
            status,
        });
    }
    if rank <= 20 {
        lots.truncate(2);
    }
    let any29 = shuppin.contains(&29.0);
    let mut lot_numbers = numbers(1..3, 0);
    if rank > 20 {
        lot_numbers.push(Choice {
            value: 3,
            label: "3".into(),
            selected: false,
        });
    }
    let auction = AuctionPanel {
        can_list: rank < 51 && auc6a == 1.0 && any29,
        can_bid: auc6a <= 2.0,
        lots,
        lot_numbers,
        amounts: numbers(1..100, 0),
    };

    // 援助射撃の申請 (etc7 = 状態,残りターン,相手の島 ID)
    let mut missile_requests = Vec::new();
    for i in &game.world.islands {
        let e = caps.fields(&i.etc_raw[2], 3);
        if num(&e[2]) == island.id as f64 && num(&e[0]) == 1.0 {
            missile_requests.push(format!("{}島", i.name));
        }
    }

    OwnerScreen {
        menu: command_menu(config, game, island_idx, master, defaults),
        policies: policies(island),
        sightseeing_targets: island_list(game, island.id),
        auction,
        plans: plan_lines(config, game, island_idx),
        comment: CommentForm {
            comment: island.comment.clone(),
            prediction: (0..26).contains(&turn) || (50..76).contains(&turn),
            capital_name: num(&island.totoyoso2) == 0.0,
            targets: island_list(game, island.id),
            turns: numbers(0..25, 0),
            missile_requests,
        },
        lbbs_numbers: numbers(0..config.lbbs.max as i64, 1),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::actions::island_index;
    use crate::actions::perl_compat_tests::cgi_dir;
    use crate::legacy::{self, ImportOptions};
    use rand::rngs::mock::StepRng;
    use serde_json::Value;

    const MASTER: &str = "uhusnuvnurkanjhfh";

    type Opt = (String, bool, String);

    /// `<SELECT NAME=名前 ...>` ごとの選択肢 (値, SELECTED か, 文面)
    fn selects(html: &str) -> Vec<(String, Vec<Opt>)> {
        let mut out = Vec::new();
        for part in html.split("<SELECT NAME=").skip(1) {
            let name: String = part
                .chars()
                .take_while(|c| c.is_ascii_alphanumeric())
                .collect();
            let body = &part[..part.find("</SELECT>").unwrap()];
            let options = body
                .split("<OPTION VALUE=")
                .skip(1)
                .map(|o| {
                    let end = o.find('>').unwrap();
                    let tag = &o[..end];
                    let value = tag.split_whitespace().next().unwrap_or("");
                    let value = value.trim_matches(|c| c == '"' || c == '\'').to_string();
                    let label = o[end + 1..].split('\n').next().unwrap().trim().to_string();
                    (value, tag.contains("SELECTED"), label)
                })
                .collect();
            out.push((name, options));
        }
        out
    }

    fn strip_tags(s: &str) -> String {
        let mut out = String::new();
        let mut in_tag = false;
        for c in s.chars() {
            match c {
                '<' => in_tag = true,
                '>' if in_tag => in_tag = false,
                _ if !in_tag => out.push(c),
                _ => {}
            }
        }
        out
    }

    fn choices(c: &[Choice]) -> Vec<Opt> {
        c.iter()
            .map(|c| (c.value.to_string(), c.selected, c.label.clone()))
            .collect()
    }

    fn cookie(req: &Value, key: &str) -> String {
        let c = req["cookie"].as_str().unwrap_or("");
        let pat = format!("hako-main.cgi{key}=(");
        c.find(&pat)
            .map(|i| {
                let rest = &c[i + pat.len()..];
                rest[..rest.find(')').unwrap()].to_string()
            })
            .unwrap_or_default()
    }

    /// `name` の各操作 (開発画面を開く) の Perl 版の画面と、移植版の中身を比べる
    fn check_owner_case(name: &str) {
        let dir = cgi_dir().join(name);
        let json: Value = serde_json::from_str(
            &std::fs::read_to_string(cgi_dir().join(format!("{name}.json"))).unwrap(),
        )
        .unwrap();
        let game = legacy::import_dir(
            &dir.join("before"),
            &ImportOptions::default(),
            &mut StepRng::new(0, 0),
        )
        .unwrap()
        .state;
        let mut config = GameConfig::default();
        config.passwords.master = Some(MASTER.into());

        for (n, req) in json["requests"].as_array().unwrap().iter().enumerate() {
            let html = std::fs::read_to_string(dir.join(format!("response{n}.html"))).unwrap();
            let id: i64 = req["form"]["ISLANDID"].as_str().unwrap().parse().unwrap();
            let idx = island_index(&game.world, id).unwrap();
            let master = config.passwords.master.as_deref() == req["form"]["PASSWORD"].as_str();
            let defaults = MenuDefaults {
                kind: cookie(req, "KIND"),
                x: cookie(req, "POINTX"),
                y: cookie(req, "POINTY"),
                lamount1: cookie(req, "LAMOUNT1"),
                lamount2: String::new(),
            };
            let s = owner_screen(&config, &game, idx, master, &defaults);
            let ctx = format!("{name} response{n}");

            // フォームの選択肢 (出てくる順)
            let m = &s.menu;
            let mut want: Vec<(&str, Vec<Opt>)> = vec![
                ("NUMBER", choices(&m.plan_numbers)),
                (
                    "COMMAND",
                    m.commands
                        .iter()
                        .map(|c| (c.kind.to_string(), c.selected, c.label()))
                        .collect(),
                ),
                ("POINTX", choices(&m.xs)),
                ("POINTY", choices(&m.ys)),
            ];
            if let Some(ij) = &m.ijiri {
                want.push(("LAMOUNT1", choices(&ij.lamount1)));
            }
            want.extend([
                ("AMOUNT", choices(&m.amounts)),
                ("TARGETID", choices(&m.targets)),
                ("TARGETID", choices(&s.sightseeing_targets)),
                ("AUCNUMBER", choices(&s.auction.lot_numbers)),
                ("AMOUNT", choices(&s.auction.amounts)),
                ("TARGETID", choices(&s.comment.targets)),
                ("AMOUNT", choices(&s.comment.turns)),
                ("NUMBER", choices(&s.lbbs_numbers)),
            ]);
            let got = selects(&html);
            assert_eq!(got.len(), want.len(), "{ctx}: selects");
            for ((gn, go), (wn, wo)) in got.iter().zip(&want) {
                assert_eq!(gn, wn, "{ctx}");
                assert_eq!(go.len(), wo.len(), "{ctx}: {wn}");
                for (g, w) in go.iter().zip(wo) {
                    assert_eq!(g, w, "{ctx}: {wn}");
                }
            }
            assert_eq!(m.ijiri.is_some(), master);

            // コスト修正
            let c = &html[html.find("NAME=COMMAND").unwrap()..];
            let c = &c[c.find("MM_displayStatusMsg('").unwrap() + 21..];
            let c = &c[..c.find("')").unwrap()];
            assert_eq!(
                c,
                format!(
                    "コスト修正({})/{}",
                    m.cost_modifier.total,
                    m.cost_modifier.details.join("<br>")
                ),
                "{ctx}"
            );

            // 計画の一覧
            let plans: Vec<String> = html
                .split("onClick=\"ns(")
                .skip(1)
                .map(|p| strip_tags(&p[p.find("<NOBR>").unwrap()..p.find("</NOBR>").unwrap()]))
                .collect();
            let want: Vec<String> = s.plans.iter().map(PlanLine::numbered).collect();
            assert_eq!(plans.len(), want.len(), "{ctx}");
            for (g, w) in plans.iter().zip(&want) {
                assert_eq!(g, w, "{ctx}");
            }

            // 政策
            let policy_rows = html.matches("<td>　予算").count();
            match &s.policies {
                Some(p) => {
                    assert!(html.contains("<B>政策(数量0"), "{ctx}");
                    assert_eq!(policy_rows, p.len(), "{ctx}");
                    for l in p {
                        assert!(
                            html.contains(&format!("<td>　{}</td>", l.text)),
                            "{ctx}: {l:?}"
                        );
                    }
                }
                None => assert_eq!(policy_rows, 0, "{ctx}"),
            }

            // ハコオク
            let a = &s.auction;
            let head = html
                .lines()
                .find(|l| l.contains("<B>Hakoniwa Auction</B>"))
                .unwrap();
            assert_eq!(head.contains("(出品可能)"), a.can_list, "{ctx}");
            assert_eq!(head.contains("(入札不可)"), !a.can_bid, "{ctx}");
            assert_eq!(html.contains("NAME=\"AuctionButton"), a.can_bid, "{ctx}");
            let lots: Vec<String> = html
                .lines()
                .filter(|l| ["<br>①", "<br>②", "<br>③"].iter().any(|m| l.starts_with(m)))
                .map(strip_tags)
                .collect();
            let want: Vec<String> = a.lots.iter().map(AuctionLot::text).collect();
            assert_eq!(lots, want, "{ctx}");

            // コメントの更新と援助射撃の申請
            let cf = &s.comment;
            assert!(
                html.contains(&format!("NAME=MESSAGE SIZE=80 VALUE=\"{}\"", cf.comment)),
                "{ctx}"
            );
            assert_eq!(html.contains("NAME=\"TotoButton"), cf.prediction, "{ctx}");
            assert_eq!(
                html.contains("NAME=\"TotosButton"),
                cf.capital_name,
                "{ctx}"
            );
            let notice = html
                .lines()
                .find(|l| l.contains("援助射撃の申請が届いてます"))
                .map(|l| {
                    strip_tags(l)
                        .trim_start_matches('★')
                        .trim_end_matches('★')
                        .to_string()
                });
            assert_eq!(notice, cf.missile_request_notice(), "{ctx}");
        }
    }

    #[test]
    fn owner_view_matches_perl() {
        check_owner_case("owner-view");
    }

    #[test]
    fn owner_view_turn3_matches_perl() {
        check_owner_case("owner-turn3");
    }

    #[test]
    fn auction_lot_three_and_rank() {
        // 21 位以下の島には 3 枠目と品番 3 が出る (Perl の突き合わせでは島が 3 つしかない)
        let config = GameConfig::default();
        let mut game = GameState::new_game(0, &config);
        for id in 0..22 {
            game.world.islands.push(Island::blank(id, "テ", &config));
        }
        game.world.auction_lots = vec!["10,7,3,5,0".into(), "9,4,0,5,0".into(), "9,0,0,6,0".into()];
        let s = owner_screen(&config, &game, 21, false, &MenuDefaults::default());
        let lots: Vec<String> = s.auction.lots.iter().map(AuctionLot::text).collect();
        assert_eq!(
            lots,
            [
                "①海あみゅ7000人規模／5兆円以上(残り12ターン)",
                "②お守り4個／5兆円以上(残り15ターン)",
                "③お守り4個／6兆円以上(残り15ターン)",
            ]
        );
        assert_eq!(s.auction.lot_numbers.len(), 3);
        let s = owner_screen(&config, &game, 19, false, &MenuDefaults::default());
        assert_eq!(s.auction.lots.len(), 2);
        assert_eq!(s.auction.lot_numbers.len(), 2);
    }

    #[test]
    fn auction_listing_rank_limits() {
        // 出品の計画は 50 位未満、「(出品可能)」は 51 位未満 (Perl 版のまま食い違う)
        let config = GameConfig::default();
        let mut game = GameState::new_game(0, &config);
        for id in 0..51 {
            let mut i = Island::blank(id, "テ", &config);
            i.auction.auc6 = "1,0,0".into();
            game.world.islands.push(i);
        }
        game.world.auction_lots = vec!["1,0,0,0,0".into(), "29,0,0,0,0".into(), "2,0,0,0,0".into()];
        let listed = |idx: usize| {
            let s = owner_screen(&config, &game, idx, false, &MenuDefaults::default());
            let menu = s
                .menu
                .commands
                .iter()
                .any(|c| c.kind == CommandKind::Auction as u16);
            (menu, s.auction.can_list)
        };
        assert_eq!(listed(48), (true, true));
        assert_eq!(listed(49), (false, true));
        assert_eq!(listed(50), (false, false));
    }
}
