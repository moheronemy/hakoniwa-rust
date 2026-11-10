//! 島の地図 (`islandMap`, hako-map.cgi 1778–2216) と 1 マスの表示 (`landString`, 2217–2916)。
//!
//! マスごとに、Perl 版が出す画像のファイル名 (`SRC`)、マウスを乗せたときの名前 (`$alt`) と
//! 説明 (`$alt2`) を作る。観光者には隠すもの (森の木の数、ミサイル基地・地雷・海底基地など
//! の偽装) は Perl 版と同じに隠す。開発画面では、そのマスに入っている計画の印も付ける。
//!
//! 画像のファイル名は Perl 版のまま (元の画像を使えるように)。地形と値も返すので、
//! 元の画像が無ければサーバーが自前のタイルを描ける。

use crate::GameConfig;
use crate::model::World;
use crate::tables::{CommandKind, LandKind as L, MONSTERS, MONUMENTS, SHIPS};
use crate::turn::command::exp_to_level;
use crate::turn::hex::monster::seqnum;
use crate::turn::monster_spec;

use super::Viewer;
use super::info::{Cap, InfoGlobals, Regs, num, undef};

/// 地図の 1 マス
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CellView {
    pub x: usize,
    pub y: usize,
    /// 見せる地形 ([`L`] の値)。観光者には偽装した地形 (ミサイル基地・地雷 → 森、
    /// 海底基地・海底都市・海底首都・海底新都市 → 海、ハリボテ → 防衛施設)
    pub kind: u8,
    /// 見せる地形の値。観光者に隠すもの (森の木の数、偽装したマス) は `None`
    pub value: Option<i64>,
    /// 画像のファイル名 (Perl 版の `SRC`)。Perl 版で画像の決まらないマス (未知の地形など) は空
    pub image: String,
    /// 名前 (Perl 版の `$alt`)
    pub alt: String,
    /// 説明 (Perl 版の `$alt2`、人口・規模など)。HTML 断片 (`<br>`, `<font>`) を含むことがある。
    /// マスターパスワードで開いた開発画面では地形の番号と値が後ろに付く
    pub detail: String,
    /// このマスに入っている計画 (開発画面だけ)。計画番号の順
    pub planned: Vec<PlannedMark>,
}

/// 地図に出る計画の印 (`[3]整地`)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlannedMark {
    /// 計画番号 (1 から)
    pub number: usize,
    /// 計画の種類 ([`CommandKind`] の値)
    pub kind: u16,
    /// 計画の名前 (`$HcomName`)。名前の無い番号は空
    pub name: &'static str,
}

impl CellView {
    /// Perl 版の `$comStr` (「 [1]整地 [3]植林」、先頭に空白)
    pub fn planned_text(&self) -> String {
        self.planned
            .iter()
            .map(|p| format!(" [{}]{}", p.number, p.name))
            .collect()
    }
}

/// `islandMap` が地図の前に島のデータから作る値 (`landString` が使うグローバル変数)
struct MapContext<'a> {
    world: &'a World,
    config: &'a GameConfig,
    turn: i64,
    onm: &'a str,
    totoyoso2: &'a str,
    mikomi: i64,
    /// 生物大学 (`eisei5`): HP, AP, DP, SP, 撃破数, 経験値 (`None` は Perl で未定義)
    college: [Cap; 7],
    /// スタジアム (`eisei4`)
    stadium: [Cap; 11],
    /// 魔法学校 (`etc9`)
    magic: [Cap; 7],
    /// 動物園
    zoo_kinds: i64,
    zoo_count: i64,
    zoo_names: String,
    barrier: (i64, i64),
    info: &'a InfoGlobals,
}

/// スタジアムの選手の状態 (`$nn`)
fn stadium_state(n: i64) -> &'static str {
    match n {
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

/// 動物園の怪獣の数え方の重み (`$zookazus`)
const ZOO_WEIGHT: [i64; 31] = [
    2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 3, 3, 3, 3, 4, 4, 5, 4, 5, 3, 3, 3, 3, 3, 3, 4, 1, 4,
];

/// `islandMap`: `index` 番目の島の地図を行優先 (`y * size + x`) で返す
pub(crate) fn island_map(
    world: &World,
    config: &GameConfig,
    index: usize,
    viewer: Viewer,
    info: &InfoGlobals,
) -> Vec<CellView> {
    let island = &world.islands[index];
    let owner = matches!(viewer, Viewer::Owner { .. });
    // 正規表現が一致しなければ直前に一致した $1.. を使う。開発画面では呼び出し元の tempOwner が
    // 地図の前に factory, etc5, auc6, ハコオクの 3 枠を読んでいる
    let mut m = Regs::default();
    let mut info = info.clone();
    if owner {
        m.fields::<10>(&island.factory);
        // tempOwner は政策をもう一度読み、$s02 と $s12b を上書きする (正しいデータなら同じ値)
        let s5 = m.fields::<31>(&island.etc_raw[0]);
        info.s02 = undef(&s5[2]);
        info.s12b = (num(&s5[12]) / 5 + 1).min(10);
        m.fields::<3>(&island.auction.auc6);
        for lot in world.auction_lots.iter().take(3) {
            m.fields::<5>(lot);
        }
    }
    let college = m.fields::<7>(&island.eisei_raw[2]);
    let stadium = m.fields::<11>(&island.eisei_raw[1]);
    let magic = m.fields::<7>(&island.etc_raw[4]);
    let z = m.nums::<31>(&island.etc_raw[1]);
    let zoo_count: i64 = z.iter().sum();
    let weighted: i64 = z.iter().zip(ZOO_WEIGHT).map(|(a, w)| a * w).sum();
    let rena = island.owner_stats.rena;
    let mut zoo_names = String::new();
    let mut zoo_kinds = 0;
    for (i, &n) in z.iter().enumerate() {
        if n > 0 {
            let name = MONSTERS.get(i).map_or("", |s| s.name);
            zoo_names.push_str(&format!("[{name}{n}匹] "));
            zoo_kinds += 1;
        }
    }
    let ctx = MapContext {
        world,
        config,
        turn: world.turn,
        onm: &island.onm,
        totoyoso2: &island.totoyoso2,
        mikomi: island.pop * 3 * 11 / 500,
        college,
        stadium,
        magic,
        zoo_kinds,
        zoo_count,
        zoo_names,
        barrier: (rena - weighted * 25, rena - weighted * 50),
        info: &info,
    };

    // 計画の印 (開発画面だけ)
    let size = island.map.size;
    let mut planned: Vec<Vec<PlannedMark>> = vec![Vec::new(); size * size];
    if owner {
        for (i, c) in island.commands.iter().take(config.command_max).enumerate() {
            let shown = c.kind < 31 || (70..=79).contains(&c.kind) || (100..=130).contains(&c.kind);
            let (Ok(x), Ok(y)) = (usize::try_from(c.x), usize::try_from(c.y)) else {
                continue;
            };
            if shown && x < size && y < size {
                planned[y * size + x].push(PlannedMark {
                    number: i + 1,
                    kind: c.kind,
                    name: CommandKind::from_u16(c.kind).map_or("", CommandKind::name),
                });
            }
        }
    }

    // `landString` で名前を決めない地形は、前に決めた名前 (グローバル変数 `$n`) を引き継ぐ
    let mut last_n = info.house_suffix.to_string();
    let mut out = Vec::with_capacity(size * size);
    for y in 0..size {
        for x in 0..size {
            let cell = island.map.cells[y * size + x];
            let mut v = land_string(&ctx, cell.kind, cell.value, owner, &mut last_n);
            if let Viewer::Owner { master: true } = viewer {
                v.detail.push_str(&format!(
                    "<br>land = <font color = red>{}</font><br>landValue = <font color = red>{}</font>",
                    cell.kind, cell.value
                ));
            }
            out.push(CellView {
                x,
                y,
                kind: v.kind,
                value: v.value,
                image: v.image,
                alt: v.alt,
                detail: v.detail,
                planned: std::mem::take(&mut planned[y * size + x]),
            });
        }
    }
    out
}

struct Shown {
    kind: u8,
    value: Option<i64>,
    image: String,
    alt: String,
    detail: String,
}

/// `landString` の地形ごとの表示
fn land_string(ctx: &MapContext, l: u8, lv: i64, owner: bool, last_n: &mut String) -> Shown {
    let u = &ctx.config.units;
    let Some(land) = L::from_u8(l) else {
        // Perl 版で分岐の無い地形は画像も名前も空
        return Shown {
            kind: l,
            value: Some(lv),
            image: String::new(),
            alt: String::new(),
            detail: String::new(),
        };
    };
    let mut kind = l;
    let mut value = Some(lv);
    // 観光者に偽装して見せる
    let mut disguise = |k: L, image: &str, alt: &str| {
        kind = k as u8;
        value = None;
        (image.to_string(), alt.to_string(), String::new())
    };
    let s = |image: &str, alt: &str, detail: String| (image.to_string(), alt.to_string(), detail);
    let none = String::new;
    let pop = |v: i64| format!("{v}{}", u.pop);
    let scale = |v: i64| format!("{v}0{}規模", u.pop);
    let [mshp, msap, msdp, mssp, mswin, msexe, _] = ctx.college.each_ref().map(undef);
    let (magica_n, magicl_n) = (num(&ctx.magic[3]), num(&ctx.magic[5]));
    let [_, magicf, magici, magica, magicw, magicl, magicd] = ctx.magic.each_ref().map(undef);
    let i = ctx.info;
    let policy_text = || {
        format!(
            "消費電力-{}%/指定可能+{}/予測精度+{}/人気+{}/清浄+{}/貯蓄{}倍",
            i.s02, i.s10b, i.s04b, i.s06b, i.s08b, i.s12b
        )
    };

    let (image, alt, detail) = match land {
        L::Sea => {
            if lv == 1 {
                s("land14.gif", "海(浅瀬)", none())
            } else {
                s("land0.gif", "海", none())
            }
        }
        L::Waste => s(
            if lv == 1 { "land13.gif" } else { "land1.gif" },
            "荒地",
            none(),
        ),
        L::Plains => s("land2.gif", "平地", none()),
        L::Plains2 => s("land53.gif", "開発予定地", none()),
        L::Yakusho => s("land52.gif", "島役所", none()),
        L::Kura => s(
            "land55.gif",
            "倉庫",
            format!(
                "セキュリティーLevel{}／貯金{}兆円",
                lv / 100,
                lv.rem_euclid(100)
            ),
        ),
        L::Kuraf => s(
            "land55.gif",
            "倉庫",
            format!("規模Level{}／貯食{}00万トン", lv.rem_euclid(10), lv / 10),
        ),
        L::Forest => {
            if owner {
                s("land6.gif", "森", format!("{lv}{}", u.tree))
            } else {
                // 観光者の場合は木の本数隠す
                disguise(L::Forest, "land6.gif", "森")
            }
        }
        L::House => (
            format!("house{lv}.gif"),
            format!("{}{}", ctx.onm, super::info::house_suffix(lv)),
            format!("税率{}％({}{})", ctx.info.tax_rate, ctx.info.tax, u.money),
        ),
        L::Train => {
            let n = match lv {
                0 => "駅",
                ..0 | 1..10 => "線路",
                10 => "駅(普通電車停車中)",
                11..20 => "普通電車",
                20 => "駅(貨物列車停車中)",
                21..30 => "貨物列車",
                _ => "路線",
            };
            (format!("train{lv}.gif"), n.to_string(), none())
        }
        L::Taishi => {
            // 無い島の ID なら $HidToNumber{$lv} が未定義で、0 番目 (1 位) の島の名前になる
            // (Perl 版のまま)
            let t = ctx
                .world
                .islands
                .iter()
                .find(|i| i.id == lv)
                .or(ctx.world.islands.first());
            let name = t.map_or("", |i| i.name.as_str());
            s("land51.gif", &format!("{name}島大使館"), none())
        }
        L::Town => {
            let (p, n) = if lv < 30 {
                (3, "村")
            } else if lv < 100 {
                (4, "町")
            } else {
                (5, "都市")
            };
            (format!("land{p}.gif"), n.to_string(), pop(lv))
        }
        L::Procity => {
            let c = if lv < 110 {
                "防災都市ランクＥ"
            } else if lv < 130 {
                "防災都市ランクＤ"
            } else if lv < 160 {
                "防災都市ランクＣ"
            } else if lv < 200 {
                "防災都市ランクＢ"
            } else {
                "防災都市ランクＡ"
            };
            s("land26.gif", c, pop(lv))
        }
        L::College => {
            let bio = |state: &str| {
                format!("{state}/HP{mshp}.AP{msap}.DP{msdp}.SP{mssp}/{mswin}匹撃破/経験値{msexe}")
            };
            let (p, n, n2) = match lv {
                0 => (34, "農業大学", none()),
                1 => (35, "工業大学", none()),
                2 => (36, "総合大学", none()),
                3 => (37, "軍事大学", none()),
                4 => (44, "生物大学", bio("待機")),
                98 => (48, "生物大学", bio("待機")),
                96 => (44, "生物大学", bio("出禁")),
                97 => (48, "生物大学", bio("出禁")),
                99 => (47, "生物大学(出動中)", none()),
                5 => (46, "気象大学", none()),
                6 => (47, "経済大学", none()),
                7 => (
                    65,
                    "魔法学校",
                    format!(
                        "炎:lv{magicf}氷:lv{magici}地:lv{magica}風:lv{magicw}光:lv{magicl}闇:lv{magicd}"
                    ),
                ),
                8 => (71, "電工大学", none()),
                77 => (75, "文部科学省", policy_text()),
                78 => (
                    75,
                    "文部科学省",
                    policy_text() + "<br><font color = royalblue>(自動開発予定地実施中)</font>",
                ),
                79 => (
                    75,
                    "文部科学省",
                    policy_text() + "<br><font color = royalblue>(自動地ならし実施中)</font>",
                ),
                80 => (
                    75,
                    "文部科学省",
                    policy_text()
                        + "<br><font color = royalblue>(自動開発予定地実施中)<br>(自動地ならし実施中)</font>",
                ),
                95 => (54, "経済大学(貯金中)", none()),
                _ => (46, "気象大学", none()),
            };
            (format!("land{p}.gif"), n.to_string(), n2)
        }
        L::Kyujokai => {
            let st = &ctx.stadium;
            let kachiten = num(&st[3]) * 3 + num(&st[4]);
            let stshoka = num(&st[10]);
            let [
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
            ] = st.each_ref().map(undef);
            s(
                "land23.gif",
                "多目的スタジアム",
                format!(
                    "選手{}(攻({sto})守({std})KP({stk})チーム成績(勝点{kachiten}/{stwin}勝{stlose}敗{stdrow}分/通算{stwint}勝{stloset}敗{stdrowt}分/優勝{styusho}回)",
                    stadium_state(stshoka)
                ),
            )
        }
        L::Zoo => s(
            "land84.gif",
            &format!("動物園Lv{lv}"),
            format!(
                "{}種類{}匹/{}<br>バリアＡ[{}]バリアＢ[{}]",
                ctx.zoo_kinds, ctx.zoo_count, ctx.zoo_names, ctx.barrier.0, ctx.barrier.1
            ),
        ),
        L::Farm => s("land7.gif", "農場", scale(lv)),
        L::EneAt => s("land62.gif", "原子力発電所", format!("出力{lv}万ｋＷ")),
        L::EneFw => s("land61.gif", "火力発電所", format!("出力{lv}万ｋＷ")),
        L::EneWt => s(
            "land63.gif",
            "水力発電所",
            format!("出力{lv}万ｋＷ/70-150%変動"),
        ),
        L::EneBo => s("land67.gif", "バイオマス発電所", format!("出力{lv}万ｋＷ")),
        L::EneWd => s(
            "land66.gif",
            "風力発電所",
            format!("出力{lv}万ｋＷ/50-125%変動"),
        ),
        L::EneCs => s("land70.gif", "コスモ発電所", format!("出力{lv}万ｋＷ")),
        L::EneSo => s(
            "land68.gif",
            "ソーラー発電所",
            format!("出力{lv}万ｋＷ/75-100%変動"),
        ),
        L::Conden => s("land64.gif", "コンデンサ", format!("蓄電{lv}万ｋＷ")),
        L::Conden2 => s("land64.gif", "コンデンサ・改", format!("蓄電{lv}万ｋＷ")),
        L::Conden3 => s(
            "land76.gif",
            "黄金のコンデンサ",
            format!("蓄電{}万ｋＷ", lv * 2),
        ),
        L::Conden4 => {
            let (image, n2) = match lv {
                3 => {
                    *last_n = "黄金のコンデンサ".into();
                    ("land78.gif", "漏電中".to_string())
                }
                2 => {
                    *last_n = "コンデンサ・改".into();
                    ("land77.gif", "漏電中".to_string())
                }
                99 => {
                    *last_n = "核融合発電所".into();
                    let n2 = if magicl_n == magica_n {
                        format!("{}万ｋＷ", magicl_n * 15000 + 50000)
                    } else {
                        "不安定".into()
                    };
                    ("land79.gif", n2)
                }
                // 画像は決まらず、名前は前のマスのまま (Perl 版のまま)
                _ => ("", none()),
            };
            s(image, &last_n.clone(), n2)
        }
        L::Foodim => s(
            "land25.gif",
            if lv < 480 {
                "食物研究所"
            } else {
                "防災型食物研究所"
            },
            format!("農場換算{lv}0{}規模", u.pop),
        ),
        L::Foodka => {
            let klv = lv * 200;
            let work = |head: &str| format!("{head}・農場＆普通職場{klv}0{}規模", u.pop);
            let n2 = match lv {
                0 => {
                    *last_n = "加工工場".into();
                    "休業中".to_string()
                }
                1 => {
                    *last_n = "精肉工場".into();
                    work("100トン＆50kWで0.175億円")
                }
                2 => {
                    *last_n = "ハンバーガー工場".into();
                    work("100トン＆150kWで0.25億円")
                }
                3 => {
                    *last_n = "ケーキ工場".into();
                    work("100トン＆300kWで0.4億円")
                }
                // 名前は前のマスのまま (Perl 版のまま)
                _ => none(),
            };
            s("land73.gif", &last_n.clone(), n2)
        }
        L::Farmchi => s(
            "land31.gif",
            "養鶏場",
            format!("{lv}万羽/生産力{lv}{}", u.food),
        ),
        L::Farmpic => s(
            "land32.gif",
            "養豚場",
            format!("{lv}万頭/生産力{}{}", lv * 2, u.food),
        ),
        L::Farmcow => s(
            "land33.gif",
            "牧場",
            format!("{lv}万頭/生産力{}{}", lv * 3, u.food),
        ),
        L::Factory => s("land8.gif", "工場", scale(lv)),
        L::HTFactory => s("land50.gif", "ハイテク多国籍企業", scale(lv)),
        L::SHTF => s(
            "land85.gif",
            "ハイテク多国籍企業・改",
            format!("ＨＴ職場{}", scale(lv)),
        ),
        L::OWNF => {
            let ownfe = lv / 1000;
            let shts = (lv / 100).rem_euclid(10) * 250;
            let hts = lv.rem_euclid(100) / 10 * 250;
            let noujous = lv.rem_euclid(10) * 250;
            let mut n = String::new();
            if ownfe > 0 {
                n.push_str("<br><font color = royalblue>(腐海の毒消し薬所有)</font>");
            }
            if ownfe > 1 {
                n.push_str("<br><font color = royalblue>(ウィルスワクチン所有)</font>");
            }
            if ownfe > 2 {
                n.push_str("<br><font color = royalblue>(長寿薬所有)</font>");
            }
            let detail = format!(
                "農場{}<br>職場{}<br>ＨＴ職場{}{n}",
                scale(noujous),
                scale(hts),
                scale(shts)
            );
            *last_n = n;
            s("land86.gif", &format!("{}社", ctx.onm), detail)
        }
        L::Base => {
            if owner {
                let level = exp_to_level(l, lv);
                s(
                    "land9.gif",
                    "ミサイル基地",
                    format!("レベル {level}/経験値 {lv}"),
                )
            } else {
                // 観光者の場合は森のふり
                disguise(L::Forest, "land6.gif", "森")
            }
        }
        L::Sbase => {
            if owner {
                let level = exp_to_level(l, lv);
                s(
                    "land12.gif",
                    "海底基地",
                    format!("レベル {level}/経験値 {lv}"),
                )
            } else {
                // 観光者の場合は海のふり
                disguise(L::Sea, "land0.gif", "海")
            }
        }
        L::Seacity => {
            if owner {
                s("land17.gif", "海底都市", pop(lv))
            } else {
                disguise(L::Sea, "land0.gif", "海")
            }
        }
        L::Frocity => s("land39.gif", "海上都市メガフロート", pop(lv)),
        L::Minato => s("land21.gif", "港町", pop(lv)),
        L::Onsen => s("land40.gif", "温泉街", pop(lv)),
        L::Sunahama => s("land38.gif", "砂浜", none()),
        L::Defence => {
            if lv == 77 {
                s("land80.gif", "防衛施設・改", none())
            } else {
                s("land10.gif", "防衛施設", none())
            }
        }
        L::Haribote => {
            if owner {
                s("land10.gif", "ハリボテ", none())
            } else {
                // 観光者の場合は防衛施設のふり
                disguise(L::Defence, "land10.gif", "防衛施設")
            }
        }
        L::Nursery => s("nursery.gif", "養殖場", scale(lv)),
        L::Mine => {
            if owner {
                s("land22.gif", "地雷", format!("ダメージ{lv}"))
            } else {
                // 観光者の場合は森のふり
                disguise(L::Forest, "land6.gif", "森")
            }
        }
        L::Ice => {
            if lv > 0 {
                s("land42.gif", "天然スケート場", none())
            } else {
                s("land41.gif", "氷河", none())
            }
        }
        L::Oil => s("land16.gif", "海底油田", none()),
        L::Gold => s("land15.gif", "金山", format!("採掘場{}", scale(lv))),
        L::Mountain => {
            if lv > 0 {
                s("land15.gif", "山", format!("採掘場{}", scale(lv)))
            } else {
                s("land11.gif", "山", none())
            }
        }
        L::Monument => {
            let m = usize::try_from(lv).ok().and_then(|i| MONUMENTS.get(i));
            s(m.map_or("", |m| m.1), m.map_or("", |m| m.0), none())
        }
        L::Fune => {
            let f = usize::try_from(lv).ok().and_then(|i| SHIPS.get(i));
            s(f.map_or("", |f| f.1), f.map_or("", |f| f.0), none())
        }
        L::Monster => {
            let (k, name, hp) = monster_spec(lv);
            let spec = MONSTERS.get(k);
            let special = spec.map_or(0, |m| m.special);
            let t = ctx.turn;
            // 硬化中? (硬化中の画像の無い怪獣は画像が空になる、Perl 版のまま)
            let hard = (special == 3 && t.rem_euclid(2) == 1)
                || (special == 8 && seqnum(t) % 2 == 0)
                || (special == 4 && t.rem_euclid(2) == 0);
            let image = spec.map_or("", |m| if hard { m.image_hardened } else { m.image });
            s(image, name, format!("体力{hp}"))
        }
        L::Park => s(
            "land19.gif",
            "遊園地",
            format!("従業員{lv}0{}/収益見込{}{}以上", u.pop, ctx.mikomi, u.money),
        ),
        L::Kyujo => s("land23.gif", "野球場", none()),
        L::Umiamu => s("land24.gif", "海あみゅ", format!("従業員{lv}0{}", u.pop)),
        L::Seki => s("land27.gif", "関所", none()),
        L::RottenSea => {
            if lv > 20 {
                s("land72.gif", "枯死海", format!("樹齢{lv}ターン"))
            } else {
                s("land20.gif", "腐海", format!("樹齢{lv}ターン"))
            }
        }
        L::Newtown => s(
            "land28.gif",
            "ニュータウン",
            format!("{}/普通職場{}0{}", pop(lv), lv / 15, u.pop),
        ),
        L::Bigtown => s(
            "land29.gif",
            "現代都市",
            format!(
                "{}/普通職場{}0{}/農場{}0{}",
                pop(lv),
                lv / 20,
                u.pop,
                lv / 30,
                u.pop
            ),
        ),
        L::Rizort => s("land43.gif", "リゾート地", format!("滞在観光客{}", pop(lv))),
        L::Kajino => s("land74.gif", "カジノ", format!("滞在観光客{}", pop(lv))),
        L::BigRizort => s(
            "land49.gif",
            "臨海リゾートホテル",
            format!("滞在観光客{}", pop(lv)),
        ),
        L::Shuto => s("land29.gif", &format!("首都{}", ctx.totoyoso2), pop(lv)),
        L::Umishuto => {
            if owner {
                s("land30.gif", &format!("海底首都{}", ctx.totoyoso2), pop(lv))
            } else {
                disguise(L::Sea, "land0.gif", "海")
            }
        }
        L::Bettown => s("land45.gif", "輝ける都市", pop(lv)),
        L::Skycity | L::Umicity => {
            let (image, alt) = if land == L::Skycity {
                ("land81.gif", "空中都市")
            } else {
                ("land82.gif", "海都市")
            };
            s(
                image,
                alt,
                format!(
                    "{}/ＨＴ職場{}0{}/農場{}0{}/電力消費{}万ｋＷ",
                    pop(lv),
                    lv / 60,
                    u.pop,
                    lv / 60,
                    u.pop,
                    lv / 2 * 3
                ),
            )
        }
        L::Seatown => {
            if owner {
                let owork = lv / 40;
                s(
                    "land30.gif",
                    "海底新都市",
                    format!(
                        "{}/普通職場{owork}0{}/農場{owork}0{}",
                        pop(lv),
                        u.pop,
                        u.pop
                    ),
                )
            } else {
                disguise(L::Sea, "land0.gif", "海")
            }
        }
    };
    Shown {
        kind,
        value,
        image,
        alt,
        detail,
    }
}
