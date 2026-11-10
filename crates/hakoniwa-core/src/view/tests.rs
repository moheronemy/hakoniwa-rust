//! 観光画面・開発画面を Perl 版の画面 (`tests/fixtures/cgi/view-*/response<N>.html`) と比べる。
//!
//! 移植版の構造から Perl 版と同じ HTML (地図の各マスの `<IMG>`、情報の表の各欄) を組み立てて、
//! Perl 版の画面のその部分と文字単位で比べる。データが変わらないことも `check_case` で確かめる。

use super::*;
use crate::actions::perl_compat_tests::{cgi_dir, check_case};

const MASTER: &str = "uhusnuvnurkanjhfh";

fn response(case: &str, n: usize) -> String {
    std::fs::read_to_string(cgi_dir().join(case).join(format!("response{n}.html"))).unwrap()
}

fn between<'a>(s: &'a str, start: &str, end: &str) -> &'a str {
    let a = s.find(start).unwrap_or_else(|| panic!("{start} not found")) + start.len();
    let b = s[a..]
        .find(end)
        .unwrap_or_else(|| panic!("{end} not found"))
        + a;
    &s[a..b]
}

/// 違っていれば最初に違う所の前後を出して失敗する
fn assert_same(what: &str, want: &str, got: &str) {
    if want == got {
        return;
    }
    let i = want
        .char_indices()
        .zip(got.chars())
        .find(|((_, a), b)| a != b)
        .map_or(want.len().min(got.len()), |((i, _), _)| i);
    let ctx = |s: &str| {
        let a = s.floor_char_boundary(i.saturating_sub(200));
        let b = s.floor_char_boundary((i + 300).min(s.len()));
        s[a..b].to_string()
    };
    panic!(
        "{what}: differs at byte {i}\nperl: {}\nrust: {}",
        ctx(want),
        ctx(got)
    );
}

fn popup_attr(image: &str, p: &Popup) -> String {
    format!(
        " onMouseOver=\"MM_displayStatusMsg('{t}/{b}'); Navi2(12, '{image}', '{t}', '{b}', '', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"",
        t = p.title,
        b = p.body
    )
}

fn icon(i: &Icon) -> String {
    let attr = i
        .popup
        .as_ref()
        .map(|p| popup_attr(&i.image, p))
        .unwrap_or_default();
    format!(
        "<IMG SRC=\"{}\" ALT=\"{}\" WIDTH=16 HEIGHT=\"16\"{attr}>{}",
        i.image, i.alt, i.text
    )
}

fn holding(h: &Holding, est: &IncomeEstimate) -> String {
    if !h.held {
        return h.text.clone();
    }
    let p = Popup {
        title: IncomeEstimate::TITLE.into(),
        body: est.body(),
    };
    format!("<p{}>{}</p>", popup_attr("black.gif", &p), h.text)
}

/// 情報の表の `<NOBR>` の中身を Perl 版と同じに組み立てる
fn info_cells(info: &IslandInfo) -> Vec<String> {
    let th = |s: &str| format!("<FONT COLOR=\"#C00000\"><B>{s}</B></FONT>");
    let mut out = vec![th("順位"), th(info.points_label), th("人口")];
    if info.money.is_some() {
        out.push(th("資金"));
    }
    for s in [
        "食料",
        "面積",
        "農場",
        "職場",
        "採掘場",
        "発電力",
        "失業率",
        "軍事技術",
    ] {
        out.push(th(s));
    }
    out.push(format!(
        "<FONT COLOR=\"#800000\"><B>{}</B></FONT>",
        info.rank
    ));
    out.push(info.points.to_string());
    out.push(info.population.clone());
    if let Some(m) = &info.money {
        let savings = info
            .savings
            .as_ref()
            .map(|s| format!("＋{}", icon(s)))
            .unwrap_or_default();
        out.push(format!("{m}{savings}"));
    }
    out.push(info.food.clone());
    out.push(info.area.clone());
    let est = &info.income_estimate;
    out.push(holding(&info.farm, est));
    out.push(holding(&info.jobs, est));
    out.push(holding(&info.mining, est));
    out.push(info.power.clone());
    let u = info.unemployment.as_ref().unwrap();
    out.push(format!(
        "<font color=\"{}\">{}</font>",
        if u.red { "red" } else { "black" },
        u.text
    ));
    out.push(info.military.clone());
    let house = info.house.as_ref().map(icon).unwrap_or_default();
    let live = info
        .live_monster_icon
        .as_ref()
        .map(|i| {
            format!(
                "<IMG SRC=\"{}\" ALT=\"{}\" WIDTH=16 HEIGHT=16> ",
                i.image, i.alt
            )
        })
        .unwrap_or_default();
    let monsm = info.live_monsters.clone().unwrap_or_default();
    let stock: String = info.livestock.iter().map(icon).collect();
    let sats: String = info.satellites.iter().map(icon).collect();
    let mut ele = info.electricity.clone();
    ele.text = String::new();
    let shortage = if info.power_shortage {
        assert_eq!(info.electricity.text, "不足中！");
        "<font color=red>不足中！</font>"
    } else {
        assert_eq!(info.electricity.text, "");
        ""
    };
    out.push(format!(
        "<FONT COLOR=\"royalblue\"><B>info：<font size=\"-1\"><font color=\"SALMON\">{house}</font>{live}<font color=\"hotpink\">{monsm}</font>{stock}{sats}</font></font>{}{shortage}",
        icon(&ele)
    ));
    out
}

fn perl_info_cells(html: &str) -> Vec<String> {
    let table = between(html, "<TABLE BORDER>\n<TR>\n<TH", "</TABLE>");
    table
        .split("<NOBR>")
        .skip(1)
        .map(|s| s.split("</NOBR>").next().unwrap().to_string())
        .collect()
}

/// 地図 (`islandMap` の出力のうち、上の目盛りと最後の `NaviView` の間) を組み立てる
fn map_html(view: &IslandView, owner: bool) -> String {
    let mut out = String::new();
    let size = view.size;
    for y in 0..size {
        if y % 2 == 0 {
            out.push_str(&format!("<IMG SRC=\"space{y}.gif\" width=16 height=32>"));
        }
        for x in 0..size {
            let c = &view.map[y * size + x];
            assert_eq!((c.x, c.y), (x, y));
            let com = c.planned_text();
            let (p1, p2) = (usize::from(x >= size / 2), usize::from(y >= size / 2));
            if owner {
                out.push_str(&format!(
                    "<A HREF=\"JavaScript:void(0);\" onclick=\"ps({x},{y})\">"
                ));
            }
            out.push_str(&format!(
                "<IMG SRC=\"{img}\" width=32 height=32 BORDER=0 onMouseOver=\"MM_displayStatusMsg('({x},{y}) {alt} {d} {com}'); Navi({size}, {p1}, {p2}, {x}, {y},'{img}', '{alt}', '{d}<br>{com}', '', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">",
                img = c.image,
                alt = c.alt,
                d = c.detail
            ));
            if owner {
                out.push_str("</A>");
            }
        }
        if y % 2 == 1 {
            out.push_str(&format!("<IMG SRC=\"space{y}.gif\" width=16 height=32>"));
        }
        out.push_str("<BR>");
    }
    out
}

fn check_view(case: &str, n: usize, view: &IslandView, owner: bool) {
    let html = response(case, n);
    let what = format!("{case} response{n}");
    assert!(
        html.contains(&format!("{}島", view.name)),
        "{what}: island name"
    );
    let want = between(&html, "<IMG SRC=\"xbar.gif\"><BR>", "<div id=\"NaviView\">");
    assert_same(&format!("{what} map"), want, &map_html(view, owner));
    let want = perl_info_cells(&html);
    assert_same(
        &format!("{what} info"),
        &want.join("\n"),
        &info_cells(&view.info).join("\n"),
    );
    // 政策の予算 (開発画面の計画の欄の下)
    match &view.info.policies {
        Some(ps) => {
            assert_eq!(ps.len(), 6);
            for p in ps {
                let s = format!("<td>　予算{}兆円/{}</td>", p.budget, p.effect);
                assert!(html.contains(&s), "{what}: {s}");
            }
        }
        None => assert!(!html.contains("<B>政策("), "{what}: policies shown"),
    }
}

/// 観光画面 (Sight=id) と開発画面 (OwnerButton) を Perl 版と比べる
fn check_views(case: &str) {
    check_case(case, &[], |game, config, c| {
        let mut config = config.clone();
        config.passwords.master = Some(MASTER.into());
        for n in 0..c.requests.len() {
            let query = c.requests[n]["query"].as_str().unwrap_or_default();
            let html = response(case, n);
            if let Some(id) = query.strip_prefix("Sight=") {
                let id: i64 = id.parse().unwrap();
                match sightseeing(game, &config, id) {
                    Ok(v) => check_view(case, n, &v, false),
                    Err(e) => {
                        assert_eq!(e, ActionError::NoSuchIsland);
                        assert!(html.contains("問題発生"), "{case} {n}");
                    }
                }
            } else {
                let id: i64 = c.form(n, "ISLANDID").parse().unwrap();
                let password = c.form(n, "PASSWORD");
                match owner_view(game, &config, id, &password) {
                    Ok(v) => {
                        assert_eq!(
                            v.map.iter().any(|c| c.detail.contains("landValue")),
                            password == MASTER
                        );
                        check_view(case, n, &v, true)
                    }
                    Err(e) => {
                        assert_eq!(e, ActionError::WrongPassword);
                        assert!(html.contains("パスワードが違います"), "{case} {n}");
                    }
                }
            }
        }
    });
}

#[test]
fn views_match_perl_all_lands() {
    check_views("view-1");
}

#[test]
fn views_match_perl_mixed() {
    check_views("view-2");
    check_views("view-3");
}

#[test]
fn visitor_does_not_see_hidden_things() {
    let game = crate::legacy::import_dir(
        &cgi_dir().join("view-1/before"),
        &Default::default(),
        &mut rand::rngs::mock::StepRng::new(0, 0),
    )
    .unwrap()
    .state;
    let config = GameConfig::default();
    let visitor = sightseeing(&game, &config, 3).unwrap();
    let owner = owner_view(&game, &config, 3, "pass3").unwrap();
    // 島 3 の怪獣のあと: 森 100, ミサイル基地, 地雷, ハリボテ
    let tail = |v: &IslandView| {
        v.map[32..36]
            .iter()
            .map(|c| (c.kind, c.value, c.alt.clone()))
            .collect::<Vec<_>>()
    };
    use crate::tables::LandKind as L;
    let f = L::Forest as u8;
    assert_eq!(
        tail(&visitor),
        [
            (f, None, "森".into()),
            (f, None, "森".into()),
            (f, None, "森".into()),
            (L::Defence as u8, None, "防衛施設".into())
        ]
    );
    assert_eq!(
        tail(&owner),
        [
            (f, Some(100), "森".into()),
            (L::Base as u8, Some(30), "ミサイル基地".into()),
            (L::Mine as u8, Some(3), "地雷".into()),
            (L::Haribote as u8, Some(1), "ハリボテ".into())
        ]
    );
    assert!(visitor.info.policies.is_none());

    // 資金を隠す設定
    let mut c = config.clone();
    c.hide_money_mode = crate::config::HideMoneyMode::Hidden;
    assert_eq!(sightseeing(&game, &c, 1).unwrap().info.money, None);
    assert_eq!(
        owner_view(&game, &c, 1, "pass1").unwrap().info.money,
        Some("123456億円".into())
    );
    c.hide_money_mode = crate::config::HideMoneyMode::Visible;
    assert_eq!(
        sightseeing(&game, &c, 1).unwrap().info.money,
        Some("123456億円".into())
    );
    c.another_mode = true;
    assert_eq!(
        sightseeing(&game, &c, 1).unwrap().info.points_label,
        "経済力"
    );
    // 無い島
    assert_eq!(
        owner_view(&game, &config, 99, "pass3"),
        Err(ActionError::NoSuchIsland)
    );
    assert_eq!(
        owner_view(&game, &config, 3, ""),
        Err(ActionError::WrongPassword)
    );
}
