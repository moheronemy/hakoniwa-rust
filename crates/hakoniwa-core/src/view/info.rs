//! 地図の上の島の情報 (`islandInfo`, hako-map.cgi 1319–1777)。
//!
//! 観光画面と開発画面で同じ表を出す。違いは資金の欄 (他人には `$HhideMoneyMode` に従って
//! 隠す・丸める) と、開発画面にだけ出る政策の予算 (`tempOwner` の計画の欄の下)。
//!
//! 文字列の欄は Perl 版の画面に出る文面そのまま (単位付き)。吹き出し (`Navi2`) の本文は
//! Perl 版の HTML 断片 (`<br>`, `<hr>`) を含む。

use crate::GameConfig;
use crate::model::{World, money_for_others};
use crate::tables::{HOUSE_LEVELS, MONSTERS};

/// 島の情報の表 (`islandInfo` が出すもの)
#[derive(Debug, Clone, PartialEq)]
pub struct IslandInfo {
    /// 順位 (`$HcurrentNumber + 1`)
    pub rank: usize,
    /// ポイントの欄の見出し。「総合Point」、アナザーモード (`$anothermood`) なら「経済力」
    pub points_label: &'static str,
    /// ポイント。Perl 版は「pts.」を付けた文字列を作るが、あとで同じ変数を数値で上書きするので
    /// 数字だけが出る (Perl 版のまま)
    pub points: i64,
    /// 人口 (「7200人」)
    pub population: String,
    /// 資金 (「123456億円」「推定2000億円」)。`None` なら資金の欄 (見出しごと) を出さない
    pub money: Option<String>,
    /// へそくり。資金の欄で金額のあとに「＋」とアイコンで出る (資金の欄が無ければ出ない)
    pub savings: Option<Icon>,
    /// 食料 (「18700トン」)
    pub food: String,
    /// 面積 (「3300万坪」)
    pub area: String,
    /// 農場の規模
    pub farm: Holding,
    /// 職場 (工場 + ハイテク) の規模
    pub jobs: Holding,
    /// 採掘場の規模
    pub mining: Holding,
    /// 農場・職場・採掘場の欄の吹き出し「収入見込み」
    pub income_estimate: IncomeEstimate,
    /// 発電力 (「179万ｋＷ」)
    pub power: String,
    /// 失業率。人口が 0 の島では Perl 版は 0 で割って画面ごと止まるので `None`
    pub unemployment: Option<Unemployment>,
    /// 軍事技術 (「Ｌｖ11」)
    pub military: String,
    /// 下の段 (info：) の島主の家。税率が正のときだけ
    pub house: Option<Icon>,
    /// 下の段の出現中の怪獣のアイコン (種類のうち番号のいちばん大きい怪獣の画像、名前の一覧)
    pub live_monster_icon: Option<Icon>,
    /// 下の段の「3匹出現中!!」。出現数が 0 でなければ
    pub live_monsters: Option<String>,
    /// 下の段の家畜 (にわとり・ぶた・うし)
    pub livestock: Vec<Icon>,
    /// 下の段の人工衛星と宇宙ステーション
    pub satellites: Vec<Icon>,
    /// 下の段の最後の電力の使用状況 (いつも出る)。`text` は不足なら「不足中！」(赤字)
    pub electricity: Icon,
    /// 電力が不足しているか (過不足が負)
    pub power_shortage: bool,
    /// 政策の予算と効果 (開発画面の計画の欄の下、見出し「政策(数量0〜50で指定してください)」)。
    /// 開発画面で、政策を始めている (`etc5` の先頭が 0 でない) ときだけ。6 つの順は Perl 版と同じ
    pub policies: Option<Vec<Policy>>,
}

/// 小さなアイコン (`<IMG SRC=画像 ALT=代替文>文字`) と、その吹き出し
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Icon {
    /// 画像のファイル名
    pub image: String,
    /// `ALT` の文
    pub alt: String,
    /// アイコンのあとに続けて出す文字
    pub text: String,
    /// マウスを乗せたときの吹き出し (`Navi2`)
    pub popup: Option<Popup>,
}

/// 吹き出し。`body` は Perl 版の HTML 断片 (`<br>` と `<hr>` を含む)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Popup {
    pub title: String,
    pub body: String,
}

/// 農場・職場・採掘場の欄
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Holding {
    /// 「1000人」、無ければ「保有せず」
    pub text: String,
    /// 保有していれば、マウスを乗せると「収入見込み」の吹き出しが出る
    pub held: bool,
}

/// 「収入見込み」の吹き出しの中身
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IncomeEstimate {
    /// 普通職場 (「1000人」「保有せず」)
    pub normal_jobs: String,
    /// ハイテク職場
    pub ht_jobs: String,
    /// 「食料＋1000トン」「食料見込みなし」
    pub food: String,
    /// 「資金＋2億円」「資金見込みなし」
    pub money: String,
    /// 「補助金＋30億円」「補助金見込みなし」
    pub subsidy: String,
}

impl IncomeEstimate {
    /// 吹き出しの見出し
    pub const TITLE: &'static str = "収入見込み";

    /// 吹き出しの本文 (Perl 版の HTML 断片)
    pub fn body(&self) -> String {
        format!(
            "普通職場…{}<br>ＨＴ職場…{}<hr>{}<br>{}<br>{}",
            self.normal_jobs, self.ht_jobs, self.food, self.money, self.subsidy
        )
    }
}

/// 失業率
#[derive(Debug, Clone, PartialEq)]
pub struct Unemployment {
    /// 百分率の値
    pub rate: f64,
    /// 表示 (`sprintf("%.2f%%")`、「86.11%」)
    pub text: String,
    /// 赤字で出すか (0 以上なら赤、負なら黒)
    pub red: bool,
}

/// 政策 (`etc5`) のひとつ: 「省エネ」の「予算10兆円/消費電力-5%」
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Policy {
    /// 政策の名前 (省エネ・教育・防災・観光・自然・貯蓄)。開発画面ではそれぞれのボタン
    /// (`ShoueneButton<島ID>` など) になっている
    pub name: &'static str,
    /// 予算の数 (兆円)。壊れたデータで Perl 版の値が未定義なら空
    pub budget: String,
    /// 効果 (「消費電力-5%」「指定可能+5」「予測精度+2」「人気+6」「清浄+7」「貯蓄7倍」)
    pub effect: String,
}

/// `islandInfo` が Perl のグローバル変数に残し、続く `islandMap` (`landString`) が使う値
#[derive(Debug, Clone)]
pub(crate) struct InfoGlobals {
    /// 家の名前の後半 (`$n`、「の小屋」など)。`landString` で名前を決めない地形が引き継ぐ
    pub house_suffix: &'static str,
    /// 税率 (`$eisei1`) と税収 (`$zeikin`)
    pub tax_rate: i64,
    pub tax: i64,
    /// 文部科学省の説明に出す政策の効果 (`$s02`, `$s10b`, `$s04b`, `$s06b`, `$s08b`, `$s12b`)
    pub s02: String,
    pub s10b: i64,
    pub s04b: i64,
    pub s06b: i64,
    pub s08b: i64,
    pub s12b: i64,
}

/// 家の段階の名前 (`$n`)。11 以上は天空城
pub(crate) fn house_suffix(level: i64) -> &'static str {
    match level {
        0 => "の小屋",
        1 => "の簡易住宅",
        2 => "の住宅",
        3 => "の高級住宅",
        4 => "の豪邸",
        5 => "の大豪邸",
        6 => "の高級豪邸",
        7 => "の城",
        8 => "の巨城",
        9 => "の黄金城",
        10 => "の魔塔",
        _ => "の天空城",
    }
}

/// `islandInfo`: `index` 番目 (順位順) の島の情報。`owner` は開発画面 (`$HmainMode eq 'owner'`)
pub fn island_info(world: &World, config: &GameConfig, index: usize, owner: bool) -> IslandInfo {
    island_info_globals(world, config, index, owner).0
}

/// `$prize =~ /([0-9]*),([0-9]*),(.*)/` が一致するか (先頭に固定しない)。一致すれば `$1`..`$3`
fn prize_caps(prize: &str) -> Option<Vec<String>> {
    let digits = |t: &str| t.bytes().take_while(u8::is_ascii_digit).count();
    (0..=prize.len())
        .filter(|&p| prize.is_char_boundary(p))
        .find_map(|p| {
            let rest = &prize[p..];
            let d1 = digits(rest);
            (rest.as_bytes().get(d1) == Some(&b',')).then_some(())?;
            let rest2 = &rest[d1 + 1..];
            let d2 = digits(rest2);
            (rest2.as_bytes().get(d2) == Some(&b',')).then_some(())?;
            let turns = rest2[d2 + 1..].split('\n').next().unwrap_or("");
            Some(vec![
                rest[..d1].to_string(),
                rest2[..d2].to_string(),
                turns.to_string(),
            ])
        })
}

/// 正規表現で取り出した Perl の `$1`.. の値 (文字列のまま。未定義は `None`)
pub(crate) type Cap = Option<String>;

/// Perl の `$1`, `$2`, ... を文字列のまま持つ。
///
/// 画面では値をそのまま文字列に埋め込むので、[`MatchScope`](crate::perl::MatchScope) と違い
/// 文字列で持つ (空の欄は空のまま、未定義は空、`prize` の `(.*)` は「12,」のまま出る)。
/// マッチに失敗すると、最後に成功したマッチの値のまま
#[derive(Debug, Clone, Default)]
pub(crate) struct Regs(Vec<String>);

impl Regs {
    /// `$s =~ /^([0-9]*),...$/` (`N` 個) のあとの `($1, ..., $N)`
    pub fn fields<const N: usize>(&mut self, s: &str) -> [Cap; N] {
        let t = s.strip_suffix('\n').unwrap_or(s);
        let parts: Vec<&str> = t.split(',').collect();
        if parts.len() == N && parts.iter().all(|p| p.bytes().all(|b| b.is_ascii_digit())) {
            self.0 = parts.iter().map(|p| p.to_string()).collect();
        }
        std::array::from_fn(|i| self.0.get(i).cloned())
    }

    /// [`fields`](Self::fields) を数値として使うとき (未定義・空は 0)
    pub fn nums<const N: usize>(&mut self, s: &str) -> [i64; N] {
        self.fields::<N>(s).each_ref().map(num)
    }
}

/// `$n` を数値として使う
pub(crate) fn num(c: &Cap) -> i64 {
    c.as_deref().map_or(0, crate::perl::int)
}

/// `$n` を文字列に埋め込む (未定義は空)
pub(crate) fn undef(c: &Cap) -> String {
    c.clone().unwrap_or_default()
}

pub(crate) fn island_info_globals(
    world: &World,
    config: &GameConfig,
    index: usize,
    owner: bool,
) -> (IslandInfo, InfoGlobals) {
    let island = &world.islands[index];
    let u = &config.units;
    // 正規表現が一致しなければ Perl 版は直前に一致した $1.. を使う
    let mut m = Regs::default();
    let pop = island.pop;
    let farm = island.farm;
    let [factory1, factory2, co0, co1, ..] = m.nums::<10>(&island.factory);
    let factoryt = factory1 + factory2;
    let mountain = island.mountain;
    let rena = island.owner_stats.rena;
    let renae = rena / 10 + 1;
    let unemployment = (pop != 0).then(|| {
        let rate = (pop - (farm + factoryt + mountain) * 10) as f64 / pop as f64 * 100.0;
        Unemployment {
            rate,
            text: format!("{rate:.2}%"),
            red: rate >= 0.0,
        }
    });

    // 収入
    let (mut foodincome, mut htincome, mut moneyincome) = (0, 0, 0);
    if pop > farm * 10 {
        // 農業だけじゃ手が余る場合
        foodincome += farm * 10 * (co0 + 1);
        if factory2 * 10 > pop - farm * 10 {
            htincome += (pop - farm * 10) / 10;
        } else {
            htincome += factory2;
            moneyincome +=
                ((pop - farm * 10 - factory2 * 10) / 10).min(factory1 + mountain) * (co1 + 1);
        }
    } else {
        // 農業だけで手一杯の場合
        foodincome += pop * (co0 + 1);
    }
    let held = |n: i64| {
        if n == 0 {
            "保有せず".to_string()
        } else {
            format!("{n}0{}", u.pop)
        }
    };
    let income_estimate = IncomeEstimate {
        normal_jobs: held(factory1),
        ht_jobs: held(factory2),
        food: if foodincome == 0 {
            "食料見込みなし".into()
        } else {
            format!("食料＋{foodincome}{}", u.food)
        },
        money: if moneyincome == 0 {
            "資金見込みなし".into()
        } else {
            format!("資金＋{moneyincome}{}", u.money)
        },
        subsidy: if htincome == 0 {
            "補助金見込みなし".into()
        } else {
            format!("補助金＋{htincome}{}", u.money)
        },
    };
    let holding = |n: i64| Holding {
        text: held(n),
        held: n != 0,
    };

    let monsterlive = island.monster_live;
    let live_monsters = (monsterlive != 0).then(|| format!("{monsterlive}{}出現中!!", u.monster));

    // へそくり
    let [auc9a, auc9b, auc9c, ..] = m.fields::<5>(&island.auction.auc9);
    let auc9c2 = num(&auc9c) / 10000;
    let (auc9a, auc9b) = (num(&auc9a), undef(&auc9b));
    let savings = (auc9a >= 1).then(|| Icon {
        image: "auc.gif".into(),
        alt: "へそくり".into(),
        text: String::new(),
        popup: Some(Popup {
            title: "へそくり".into(),
            body: format!("貯金…{auc9b}兆円<br>Auction補助金…{auc9c2}兆円<hr>合計…{auc9a}兆円"),
        }),
    });
    let money = if owner {
        Some(format!("{}{}", island.money, u.money))
    } else {
        money_for_others(island.money, config.hide_money_mode, &u.money)
    };

    // 電力 (`($ene, $shouhi, $sabun, $chikuden, $ene) = ...` なので発電力は 5 番目の欄)
    let [_, shouhi, _, _, ene] = m.fields::<5>(&island.eisei_raw[0]);
    let sabun = num(&ene) - num(&shouhi);
    let (shouhi, ene) = (undef(&shouhi), undef(&ene));
    let electricity = Icon {
        image: "ele.gif".into(),
        alt: format!("使用状況(消費{shouhi}万ｋＷ／過不足{sabun}万ｋＷ)"),
        text: if sabun < 0 {
            "不足中！".into()
        } else {
            String::new()
        },
        popup: Some(Popup {
            title: "使用状況".into(),
            body: format!("消費{shouhi}万ｋＷ<br>過不足{sabun}万ｋＷ"),
        }),
    };

    // 受賞と退治した怪獣も計算するが、この表には出さない (Perl 版のまま)。
    // 正規表現の $1.. だけが後の一致しなかったときに効く
    if let Some(caps) = prize_caps(&island.prize) {
        m.0 = caps;
    }

    // 出現中の怪獣
    let types = island.monster_live_type;
    let mut names = String::new();
    let mut max = None;
    for (i, spec) in MONSTERS.iter().enumerate().take(config.monster.number) {
        if i < 63 && types & (1i64 << i) != 0 {
            names.push_str(&format!("[{}] ", spec.name));
            max = Some(i);
        }
    }
    let live_monster_icon = max.map(|i| Icon {
        image: MONSTERS[i].image.into(),
        alt: names,
        text: String::new(),
        popup: None,
    });

    // 人工衛星
    let [eis1, eis2, eis3, eis4, eis5, eis6, eis7] = island.eis;
    let cstpop = eis7 / 100;
    let csten = eis7.rem_euclid(100) + 1;
    let csroke = cstpop / 10000 + 1;
    let mut satellites = Vec::new();
    for (v, image, alt) in [
        (eis1, "kisho.gif", "気象衛星"),
        (eis2, "kansoku.gif", "観測衛星"),
        (eis3, "geigeki.gif", "迎撃衛星"),
        (eis4, "gunji.gif", "軍事衛星"),
        (eis5, "bouei.gif", "防衛衛星"),
        (eis6, "ire.gif", "イレギュラー"),
    ] {
        if v >= 1 {
            satellites.push(Icon {
                image: image.into(),
                alt: alt.into(),
                text: format!("{v}%"),
                popup: None,
            });
        }
    }
    if eis7 >= 1 {
        satellites.push(Icon {
            image: "cst.gif".into(),
            alt: format!("宇宙ステーション／{cstpop}{}滞在", u.pop),
            text: format!("{csten}%"),
            popup: Some(Popup {
                title: "宇宙ステーション".into(),
                body: format!(
                    "{cstpop}{}滞在<br>人口維持ロケット数…{csroke}個<br>人口維持コスト…{cstpop}{}",
                    u.pop, u.money
                ),
            }),
        });
    }

    // 牧場系
    let s = &island.owner_stats;
    let mut livestock = Vec::new();
    for (v, image, alt, unit) in [
        (s.tare, "niwatori.gif", "にわとり", "万羽"),
        (s.zipro, "buta.gif", "ぶた", "万頭"),
        (s.leje, "ushi.gif", "うし", "万頭"),
    ] {
        if v >= 1 {
            livestock.push(Icon {
                image: image.into(),
                alt: alt.into(),
                text: format!("{v}{unit}"),
                popup: None,
            });
        }
    }

    // 家
    let [
        unimika,
        unishuto,
        unimeka,
        unioumu,
        unianseki,
        unitiseki,
        unihyouseki,
        unifuseki,
        unienseki,
        unikouseki,
        uniiseki,
        _,
    ] = m.nums::<12>(&island.eisei_raw[3]);
    let [_, toto2, ..] = m.nums::<7>(&island.etc_raw[3]);
    let pts = island.pts;
    let hlv = if pts > HOUSE_LEVELS[8]
        && [
            unienseki,
            unitiseki,
            unihyouseki,
            unifuseki,
            unimika,
            unishuto,
            unimeka,
            unioumu,
            uniiseki,
            toto2,
        ]
        .iter()
        .all(|&v| v > 0)
    {
        if unikouseki > 0 || unianseki > 0 {
            if unianseki >= unikouseki { 10 } else { 11 }
        } else {
            9
        }
    } else {
        (0..9)
            .rev()
            .find(|&i| pts > HOUSE_LEVELS[i])
            .map_or(0, |i| i as i64 + 1)
    };
    let suffix = house_suffix(hlv);
    let eisei1 = island.eisei[0];
    let zeikin = crate::perl::trunc((pop * (hlv + 1) * eisei1) as f64 / 100.0);
    let tax_text = format!("税率{eisei1}％({zeikin}{})", u.money);
    let house = (eisei1 > 0).then(|| Icon {
        image: format!("house{hlv}.gif"),
        alt: format!("{}{suffix}", island.onm),
        text: tax_text.clone(),
        popup: Some(Popup {
            title: format!("{}{suffix}", island.onm),
            body: tax_text.clone(),
        }),
    });

    // 政策 (その前の入札の欄の auc6 の一致も $1.. に効く)
    m.fields::<3>(&island.auction.auc6);
    let s5 = m.fields::<31>(&island.etc_raw[0]);
    let n5 = |i: usize| num(&s5[i]);
    let (s02, s04b, s06b, s08b) = (undef(&s5[2]), n5(4) / 10, n5(6) / 5, n5(8) / 5);
    let s10b = (n5(10) / 5 + 1).min(9);
    let s12b = (n5(12) / 5 + 1).min(10);
    let policy = |name, i: usize, effect| Policy {
        name,
        budget: undef(&s5[i]),
        effect,
    };
    let policies = vec![
        policy("省エネ", 1, format!("消費電力-{}%", s02)),
        policy("教育", 9, format!("指定可能+{s10b}")),
        policy("防災", 3, format!("予測精度+{s04b}")),
        policy("観光", 5, format!("人気+{s06b}")),
        policy("自然", 7, format!("清浄+{s08b}")),
        policy("貯蓄", 11, format!("貯蓄{s12b}倍")),
    ];

    let info = IslandInfo {
        rank: index + 1,
        points_label: if config.another_mode {
            "経済力"
        } else {
            "総合Point"
        },
        points: pts,
        population: format!("{pop}{}", u.pop),
        money,
        savings,
        food: format!("{}{}", island.food, u.food),
        area: format!("{}{}", island.area, u.area),
        farm: holding(farm),
        jobs: holding(factoryt),
        mining: holding(mountain),
        income_estimate,
        power: format!("{ene}万ｋＷ"),
        unemployment,
        military: format!("Ｌｖ{renae}"),
        house,
        live_monster_icon,
        live_monsters,
        livestock,
        satellites,
        electricity,
        power_shortage: sabun < 0,
        policies: (owner && n5(0) != 0).then_some(policies),
    };
    let globals = InfoGlobals {
        house_suffix: suffix,
        tax_rate: eisei1,
        tax: zeikin,
        s02,
        s10b,
        s04b,
        s06b,
        s08b,
        s12b,
    };
    (info, globals)
}
