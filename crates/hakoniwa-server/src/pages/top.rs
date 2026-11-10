//! トップページ。中身は `hakoniwa_core::view::top` が Perl 版 (`tempTopPage`) のとおりに作る。
//!
//! 画面は Perl 版を再現せず作り直す方針。

use std::fmt::Write;

use hakoniwa_core::GameConfig;
use hakoniwa_core::model::GameState;
use hakoniwa_core::view::top::{
    Badge, CommentLine, Hover, LotStatus, TopPage, Value, ViewRange, top_page,
};

use crate::layout::{csrf_field, esc};
use crate::render::plain;

/// Perl 版から引き継いだログは HTML を含むので、タグを取り除いてから表示する
fn log_text(message: &str) -> String {
    esc(&plain(message))
}

fn remaining(secs: i64) -> String {
    if secs <= 0 {
        return "まもなく更新".into();
    }
    format!("次のターンまで {}時間{}分", secs / 3600, secs % 3600 / 60)
}

fn hover_title(h: &Hover) -> String {
    let mut s = plain(&h.title);
    for section in &h.detail {
        for line in section {
            s.push('\n');
            s.push_str(&plain(line));
        }
    }
    s
}

fn value(v: &Value) -> String {
    let text = esc(&plain(&v.text));
    match &v.hover {
        Some(h) => format!("<span title=\"{}\">{text}</span>", esc(&hover_title(h))),
        None => text,
    }
}

fn badge(b: &Badge) -> String {
    let mut text = plain(&b.text);
    if text.trim().is_empty() {
        text = plain(&b.alt);
    }
    let title = b
        .hover
        .as_ref()
        .map(hover_title)
        .unwrap_or_else(|| plain(&b.alt));
    format!(
        "<span class=\"badge\" title=\"{}\">{}</span>",
        esc(&title),
        esc(text.trim())
    )
}

/// 名前とコメントは保存の時点でエスケープ済み (Perl 版と同じ)
fn comment(c: &CommentLine) -> String {
    match c {
        CommentLine::Comment { comment } => {
            format!("<span class=\"muted\">コメント :</span> {comment}")
        }
        CommentLine::Owner { owner, comment } => format!("<b>{owner}</b> : {comment}"),
        CommentLine::AidRequested {
            owner,
            target,
            turns_left,
        } => format!(
            "<b>{owner}</b> : {}島への援助射撃許可を申請中 (残り{}ターン)",
            esc(target),
            esc(turns_left)
        ),
        CommentLine::AidAllowed {
            owner,
            target,
            turns_left,
        } => format!(
            "<b>{owner}</b> : {}島への援助射撃が可能 (残り{}ターン)",
            esc(target),
            esc(turns_left)
        ),
    }
}

fn list(h: &mut String, page: &TopPage) {
    let list = &page.list;
    let _ = writeln!(h, "<h2>諸島の状況</h2>");
    if list.rows.is_empty() {
        let _ = writeln!(
            h,
            "<p>まだ島がありません。<a href=\"/register\">最初の島を探しましょう</a>。</p>"
        );
        return;
    }
    let paging = |h: &mut String| {
        if let Some(p) = &list.paging {
            h.push_str("<p class=\"paging\">");
            if let Some(prev) = p.prev {
                let _ = write!(h, "<a href=\"/?view{prev}\">前へ</a> ");
            }
            if let Some((next, _)) = p.next {
                let _ = write!(h, "<a href=\"/?view{next}\">次へ</a> ");
            }
            h.push_str("<a href=\"/?viewALL\">すべて</a></p>\n");
        }
    };
    let _ = writeln!(
        h,
        "<p class=\"muted\">{}位〜{}位</p>",
        list.first, list.last
    );
    paging(h);
    let _ = writeln!(
        h,
        "<div class=\"table-scroll\"><table class=\"islands\">\n<tr><th class=\"num\">順位</th><th>島</th>\
         <th class=\"num\">人口</th><th class=\"num\">面積</th>{}<th class=\"num\">食料</th>\
         <th class=\"num\">農場</th><th class=\"num\">職場</th><th class=\"num\">採掘場</th>\
         <th class=\"num\">電力</th><th class=\"num\">軍事力</th></tr>",
        if list.show_money {
            "<th class=\"num\">資金</th>"
        } else {
            ""
        }
    );
    for row in &list.rows {
        let name = if row.absent > 0 {
            format!(
                "<span class=\"muted\">{}島({})</span>",
                esc(&row.name),
                row.absent
            )
        } else {
            format!("{}島", esc(&row.name))
        };
        let money = if list.show_money {
            format!(
                "<td class=\"num\">{}{}</td>",
                row.money
                    .as_deref()
                    .map(|m| esc(&plain(m)))
                    .unwrap_or_default(),
                row.savings
                    .as_ref()
                    .map(|s| format!(" {}", badge(s)))
                    .unwrap_or_default()
            )
        } else {
            String::new()
        };
        let mut badges: Vec<String> = row.info.iter().map(badge).collect();
        badges.extend(row.prizes.iter().map(badge));
        let _ = writeln!(
            h,
            "<tr><td class=\"num\" rowspan=\"2\">{rank}</td>\
             <td><a href=\"/island/{id}\">{name}</a>{capital}<br><small class=\"muted\">{pts}pts / 失業率 {unemp}</small></td>\
             <td class=\"num\">{pop}</td><td class=\"num\">{area}</td>{money}<td class=\"num\">{food}</td>\
             <td class=\"num\">{farm}</td><td class=\"num\">{factory}</td><td class=\"num\">{mountain}</td>\
             <td class=\"num\">{power}</td><td class=\"num\">{military}</td></tr>\n\
             <tr><td colspan=\"{span}\" class=\"sub\">{badges}<div>{comment}</div></td></tr>",
            rank = row.rank,
            id = row.id,
            capital = row
                .capital
                .as_ref()
                .map(|c| format!(" <small>首都 {}</small>", esc(&plain(c))))
                .unwrap_or_default(),
            pts = row.pts,
            unemp = row
                .unemployment
                .as_deref()
                .map(|u| esc(&plain(u)))
                .unwrap_or_else(|| "-".into()),
            pop = esc(&plain(&row.pop)),
            area = esc(&plain(&row.area)),
            food = esc(&plain(&row.food)),
            farm = value(&row.farm),
            factory = value(&row.factory),
            mountain = value(&row.mountain),
            power = esc(&plain(&row.power)),
            military = esc(&plain(&row.military)),
            span = if list.show_money { 10 } else { 9 },
            badges = if badges.is_empty() {
                String::new()
            } else {
                format!("<div class=\"badges\">{}</div>", badges.join(" "))
            },
            comment = comment(&row.comment),
        );
    }
    h.push_str("</table></div>\n");
    paging(h);
}

/// トップページの中身 (外枠は [`crate::layout::page`])
pub fn top(
    config: &GameConfig,
    game: &GameState,
    now: i64,
    query: &str,
    csrf: Option<&str>,
) -> String {
    let page = top_page(game, config, now, ViewRange::from_query(query));
    let mut h = String::new();
    let _ = write!(
        h,
        "<h1>ターン{}</h1>\n<p>{}</p>\n",
        page.turn,
        remaining(page.remaining_secs)
    );
    if config.debug {
        let _ = writeln!(
            h,
            "<form method=\"post\" action=\"/debug/turn\">{}<button>ターンを進める</button></form>",
            csrf.map(csrf_field).unwrap_or_default()
        );
    }
    if !page.can_register {
        h.push_str("<p class=\"muted\">いまは新しい島を登録できません。</p>\n");
    }

    if !page.departments.is_empty() {
        h.push_str("<h2>各部門の No.1</h2>\n<div class=\"departments\">");
        for d in &page.departments {
            let _ = write!(
                h,
                "<div class=\"card dept\"><div class=\"muted\">{}</div><a href=\"/island/{}\">{}島</a><div>{}</div></div>",
                esc(d.department.label()),
                d.island_id,
                esc(&d.island_name),
                esc(&plain(&d.value))
            );
        }
        h.push_str("</div>\n");
    }

    list(&mut h, &page);

    if let Some(s) = &page.survey {
        let _ = writeln!(
            h,
            "<h2>アンケート</h2>\n<p>{}</p>\n<p><b>{}</b></p>\n<ul>",
            esc(&plain(&s.description)),
            esc(&plain(&s.question))
        );
        for c in &s.choices {
            let _ = writeln!(
                h,
                "<li>{}．{} — {}票 ({}%)</li>",
                esc(c.label),
                esc(&plain(&c.text)),
                c.votes,
                c.percent
            );
        }
        let _ = writeln!(
            h,
            "</ul>\n<p class=\"muted\">投票率 {}%</p>",
            s.turnout_percent
        );
        if let Some(csrf) = csrf {
            let _ = write!(
                h,
                "<form method=\"post\" action=\"/survey\" class=\"card\">{}",
                csrf_field(csrf)
            );
            for (i, c) in s.choices.iter().enumerate() {
                let _ = write!(
                    h,
                    "<label><input type=\"radio\" name=\"choice\" value=\"{}\"> {}．{}</label>",
                    i + 1,
                    esc(c.label),
                    esc(&plain(&c.text))
                );
            }
            h.push_str("<p><button>投票する</button></p></form>\n");
        }
    }

    if !page.auction.lots.is_empty() {
        h.push_str("<h2>ハコオク</h2>\n<div class=\"table-scroll\"><table>\n<tr><th>出品</th><th>品名</th><th>状態</th><th>入札</th></tr>\n");
        for lot in &page.auction.lots {
            let status = match lot.status {
                LotStatus::Sold => "落札済み".to_string(),
                LotStatus::Remaining(t) => format!("残り{t}ターン"),
            };
            let bids: Vec<String> = lot
                .bids
                .iter()
                .map(|b| {
                    format!(
                        "{}位 {} {}",
                        b.rank,
                        esc(&plain(&b.bidder)),
                        esc(&plain(&b.amount))
                    )
                })
                .collect();
            let _ = writeln!(
                h,
                "<tr><td class=\"num\">{}</td><td>{}</td><td>{status}</td><td>{}</td></tr>",
                lot.number,
                esc(&plain(&lot.item)),
                bids.join("<br>")
            );
        }
        h.push_str("</table></div>\n");
    }

    h.push_str("<h2>最近の出来事</h2>\n<div class=\"log\">\n");
    for m in &page.logs {
        let _ = writeln!(h, "<p>ターン{}：{}</p>", m.turn, log_text(&m.message));
    }
    h.push_str("</div>\n<p><a href=\"/history\">それより前の出来事</a></p>\n");
    if !page.hcup_log.is_empty() {
        h.push_str("<h2>Hakoniwa Cup の記録</h2>\n<div class=\"log\">\n");
        for m in &page.hcup_log {
            let _ = writeln!(h, "<p>ターン{}：{}</p>", m.turn, log_text(&m.message));
        }
        h.push_str("</div>\n");
    }
    h.push_str("<h2>発見の記録</h2>\n<div class=\"log\">\n");
    for m in &page.history {
        let _ = writeln!(h, "<p>ターン{}：{}</p>", m.turn, log_text(&m.message));
    }
    h.push_str("</div>\n");
    h
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn log_text_strips_tags_and_escapes() {
        assert_eq!(
            log_text(r##"<FONT COLOR="#a06040"><B>テスト島</B></FONT>が発見される。"##),
            "テスト島が発見される。"
        );
        assert_eq!(log_text("a &amp; b"), "a &amp; b");
    }

    #[test]
    fn remaining_time() {
        assert_eq!(remaining(0), "まもなく更新");
        assert_eq!(
            remaining(3 * 3600 + 25 * 60 + 10),
            "次のターンまで 3時間25分"
        );
    }
}
