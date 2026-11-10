//! 島の地図と情報の表示 (中身は `hakoniwa_core::view` が Perl 版のとおりに作る)。
//!
//! 地図は、運営者が Perl 版の画像を `image_dir` に置いていればそれを使い、無ければ
//! 地形の種類から色と文字のタイルを描く (種類と値は観光者向けに偽装されたもの)。

use std::fmt::Write;

use hakoniwa_core::tables::LandKind as L;
use hakoniwa_core::view::{CellView, Icon, IslandInfo, IslandView};

use crate::layout::esc;

/// Perl 版の HTML 断片 (`<br>` や `<font>` を含む) を、属性に入れる文字にする
pub fn plain(html: &str) -> String {
    let mut out = String::new();
    let mut tag = String::new();
    let mut in_tag = false;
    for c in html.chars() {
        match c {
            '<' => {
                in_tag = true;
                tag.clear();
            }
            '>' if in_tag => {
                in_tag = false;
                let t = tag.to_ascii_lowercase();
                if t.starts_with("br") || t.starts_with("hr") {
                    out.push('\n');
                }
            }
            _ if in_tag => tag.push(c),
            _ => out.push(c),
        }
    }
    out.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", "\"")
        .replace("&nbsp;", " ")
        .replace("&amp;", "&")
}

/// 画像が無いときのタイルの色 (背景, 文字)
fn tile_colors(kind: u8, value: Option<i64>) -> (&'static str, &'static str) {
    let Some(k) = L::from_u8(kind) else {
        return ("#888", "#fff");
    };
    match k {
        L::Sea if value == Some(1) => ("#7fb8e6", "#123"),
        L::Sea => ("#2f6fae", "#dfeefa"),
        L::Seacity
        | L::Umishuto
        | L::Seatown
        | L::Umicity
        | L::Fune
        | L::Oil
        | L::Sbase
        | L::Umiamu
        | L::Nursery => ("#3d86c6", "#fff"),
        L::Waste => ("#b9a37f", "#3b2f1d"),
        L::Plains | L::Plains2 => ("#a9d67c", "#28401a"),
        L::Forest => ("#2f7d3a", "#e6f5e6"),
        L::Mountain | L::Gold => ("#8a6a4a", "#fff"),
        L::Town
        | L::Minato
        | L::House
        | L::Newtown
        | L::Bigtown
        | L::Bettown
        | L::Procity
        | L::Frocity
        | L::Shuto
        | L::Skycity => ("#e2a24a", "#3a2408"),
        L::Farm | L::Farmchi | L::Farmpic | L::Farmcow => ("#d8d45a", "#3a3808"),
        L::Factory | L::HTFactory | L::SHTF | L::OWNF | L::Foodim | L::Foodka => {
            ("#8d939a", "#fff")
        }
        L::EneAt
        | L::EneFw
        | L::EneWt
        | L::EneWd
        | L::EneBo
        | L::EneSo
        | L::EneCs
        | L::Conden
        | L::Conden2
        | L::Conden3
        | L::Conden4 => ("#8b6fc4", "#fff"),
        L::Base | L::Defence | L::Haribote | L::Mine => ("#6b7a3a", "#fff"),
        L::Monster => ("#c23b2b", "#fff"),
        L::Monument => ("#d9b84a", "#3a2c05"),
        L::Park
        | L::Kyujo
        | L::Kyujokai
        | L::Rizort
        | L::BigRizort
        | L::Kajino
        | L::Zoo
        | L::Onsen
        | L::Sunahama => ("#e48fb4", "#3a0f22"),
        L::RottenSea => ("#5a3b6b", "#fff"),
        L::Ice => ("#dff1f7", "#234"),
        _ => ("#7c8f9c", "#fff"),
    }
}

/// 地図。`owner` なら計画の印を出し、マスをクリックすると計画の座標に入る
pub fn map_html(view: &IslandView, use_images: bool, owner: bool) -> String {
    let n = view.size;
    let mut h = format!(
        "<div class=\"table-scroll\"><div class=\"map\" style=\"grid-template-columns: 20px repeat({n}, auto)\" role=\"grid\" aria-label=\"{}島の地図\">\n<span></span>",
        esc(&view.name)
    );
    for x in 0..n {
        let _ = write!(h, "<span class=\"cell axis\">{x}</span>");
    }
    for y in 0..n {
        let _ = write!(h, "\n<span class=\"cell axis\">{y}</span>");
        for x in 0..n {
            let Some(cell) = view.map.get(y * n + x) else {
                continue;
            };
            h.push_str(&cell_html(cell, use_images, owner));
        }
    }
    h.push_str("\n</div></div>\n");
    h
}

fn cell_html(cell: &CellView, use_images: bool, owner: bool) -> String {
    let mut title = format!("({}, {}) {}", cell.x, cell.y, plain(&cell.alt));
    let detail = plain(&cell.detail);
    if !detail.trim().is_empty() {
        title.push('\n');
        title.push_str(detail.trim());
    }
    if owner && !cell.planned.is_empty() {
        title.push('\n');
        title.push_str(&plain(&cell.planned_text()));
    }
    let mark = match (owner, cell.planned.first()) {
        (true, Some(p)) => format!("<span class=\"plan\">{}</span>", p.number),
        _ => String::new(),
    };
    let inner = if use_images && !cell.image.is_empty() {
        format!(
            "<img src=\"/img/{}\" alt=\"{}\">",
            esc(&cell.image),
            esc(&plain(&cell.alt))
        )
    } else {
        let (bg, fg) = tile_colors(cell.kind, cell.value);
        let glyph: String = plain(&cell.alt)
            .chars()
            .next()
            .map(String::from)
            .unwrap_or_default();
        format!(
            "<span class=\"tile\" style=\"background:{bg};color:{fg}\" aria-hidden=\"true\">{}</span>",
            esc(&glyph)
        )
    };
    let data = if owner {
        format!(
            " data-x=\"{}\" data-y=\"{}\" tabindex=\"0\"",
            cell.x, cell.y
        )
    } else {
        String::new()
    };
    format!(
        "<span class=\"cell\" role=\"gridcell\" title=\"{t}\" aria-label=\"{t}\"{data}>{inner}{mark}</span>",
        t = esc(&title)
    )
}

fn icon_text(icon: &Icon) -> String {
    let mut s = plain(&icon.text);
    if s.trim().is_empty() {
        s = plain(&icon.alt);
    }
    match &icon.popup {
        Some(p) => format!(
            "<span title=\"{}\">{}</span>",
            esc(&format!("{}\n{}", plain(&p.title), plain(&p.body))),
            esc(s.trim())
        ),
        None => esc(s.trim()),
    }
}

/// 島の情報の表 (Perl 版の `islandInfo`)
pub fn info_html(info: &IslandInfo) -> String {
    let mut rows: Vec<(String, String)> = vec![
        ("順位".into(), format!("{}位", info.rank)),
        (plain(info.points_label), info.points.to_string()),
        ("人口".into(), esc(&plain(&info.population))),
    ];
    if let Some(m) = &info.money {
        rows.push(("資金".into(), esc(&plain(m))));
    }
    if let Some(s) = &info.savings {
        rows.push(("へそくり".into(), icon_text(s)));
    }
    rows.push(("食料".into(), esc(&plain(&info.food))));
    rows.push(("面積".into(), esc(&plain(&info.area))));
    rows.push(("農場".into(), esc(&plain(&info.farm.text))));
    rows.push(("職場".into(), esc(&plain(&info.jobs.text))));
    rows.push(("採掘場".into(), esc(&plain(&info.mining.text))));
    rows.push((
        "収入見込み".into(),
        format!(
            "<span class=\"pre\">{}</span>",
            esc(&plain(&info.income_estimate.body()))
        ),
    ));
    rows.push(("電力".into(), esc(&plain(&info.power))));
    if let Some(u) = &info.unemployment {
        let t = esc(&plain(&u.text));
        rows.push((
            "失業率".into(),
            if u.red {
                format!("<span class=\"error\">{t}</span>")
            } else {
                t
            },
        ));
    }
    rows.push(("軍事力".into(), esc(&plain(&info.military))));
    let mut extra: Vec<String> = Vec::new();
    if let Some(i) = &info.house {
        extra.push(icon_text(i));
    }
    if let Some(i) = &info.live_monster_icon {
        extra.push(icon_text(i));
    }
    if let Some(t) = &info.live_monsters {
        extra.push(esc(&plain(t)));
    }
    extra.extend(info.livestock.iter().map(icon_text));
    extra.extend(info.satellites.iter().map(icon_text));
    let mut ele = icon_text(&info.electricity);
    if info.power_shortage {
        ele = format!("<span class=\"error\">{ele}</span>");
    }
    extra.push(ele);

    let mut h = String::from("<div class=\"table-scroll\"><table class=\"info\">\n");
    for (k, v) in rows {
        let _ = writeln!(h, "<tr><th>{}</th><td>{v}</td></tr>", esc(&k));
    }
    let extra: Vec<String> = extra.into_iter().filter(|s| !s.trim().is_empty()).collect();
    if !extra.is_empty() {
        let _ = writeln!(
            h,
            "<tr><th>そのほか</th><td>{}</td></tr>",
            extra.join(" / ")
        );
    }
    h.push_str("</table></div>\n");
    if let Some(policies) = &info.policies {
        h.push_str("<h3>政策</h3>\n<div class=\"table-scroll\"><table class=\"policies\">\n<tr><th>政策</th><th>予算</th><th>効果</th></tr>\n");
        for p in policies {
            let _ = writeln!(
                h,
                "<tr><td>{}</td><td>{}</td><td>{}</td></tr>",
                esc(p.name),
                esc(&plain(&p.budget)),
                esc(&plain(&p.effect))
            );
        }
        h.push_str("</table></div>\n");
    }
    h
}

/// 島の近況 (Perl 版の `tempRecent`)。ログの HTML はタグを取り除いて出す
pub fn recent_html(name: &str, logs: &[hakoniwa_core::view::RecentLog]) -> String {
    let mut h = format!("<h2>{}島の近況</h2>\n<div class=\"log\">\n", esc(name));
    if logs.is_empty() {
        h.push_str("<p class=\"muted\">まだ何も起きていません。</p>\n");
    }
    for l in logs {
        let _ = writeln!(
            h,
            "<p>ターン{}{}：{}</p>",
            l.turn,
            if l.secret { " <b>(機密)</b>" } else { "" },
            esc(&plain(&l.message))
        );
    }
    h.push_str("</div>\n");
    h
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn plain_text() {
        assert_eq!(
            plain("a<br>b<FONT COLOR=\"red\">c</FONT> &amp; d"),
            "a\nbc & d"
        );
    }
}
