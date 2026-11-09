//! HTML の組み立て。
//!
//! 画面は Perl 版を再現せず作り直す方針。いまはトップページの最小限だけ。

use std::fmt::Write;

use hakoniwa_core::GameConfig;
use hakoniwa_core::model::{GameState, money_for_others};
use hakoniwa_core::perl::html_escape;

/// Perl 版から引き継いだログは HTML を含むので、タグを取り除いてから表示する
fn log_text(message: &str) -> String {
    let mut out = String::with_capacity(message.len());
    let mut in_tag = false;
    for c in message.chars() {
        match c {
            '<' => in_tag = true,
            '>' if in_tag => in_tag = false,
            _ if !in_tag => out.push(c),
            _ => {}
        }
    }
    html_escape(&out)
}

fn remaining(secs: i64) -> String {
    if secs <= 0 {
        return "まもなく更新".into();
    }
    format!("次の更新まで {}時間{}分", secs / 3600, secs % 3600 / 60)
}

/// 移植元の使用条件により、ゲーム画面の最上部に置く必要がある配布元へのリンク
pub const ORIGINAL_SITE: &str = "http://www.bekkoame.ne.jp/~tokuoka/hakoniwa.html";

pub fn top(config: &GameConfig, game: &GameState, now: i64) -> String {
    let world = &game.world;
    let units = &config.units;
    let title = html_escape(&config.title);
    let mut h = String::new();

    let _ = write!(
        h,
        r#"<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 0 auto; max-width: 960px; padding: 16px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #ccc; padding: 4px 8px; text-align: left; }}
td.num {{ text-align: right; white-space: nowrap; }}
.log {{ font-size: 0.9em; }}
</style>
</head>
<body>
<p><a href="{ORIGINAL_SITE}">箱庭諸島スクリプト配布元</a></p>
<h1>{title}</h1>
<h2>ターン{turn}</h2>
<p>{remain}</p>
"#,
        turn = world.turn,
        remain = remaining(world.next_turn_time(config) - now),
    );

    let _ = writeln!(h, "<h2>諸島の状況</h2>");
    if world.islands.is_empty() {
        let _ = writeln!(h, "<p>まだ島がありません。</p>");
    } else {
        let show_money = money_for_others(0, config.hide_money_mode, "").is_some();
        let _ = writeln!(
            h,
            "<table>\n<tr><th>順位</th><th>島</th><th>人口</th><th>面積</th>{}<th>食料</th><th>コメント</th></tr>",
            if show_money { "<th>資金</th>" } else { "" }
        );
        for (rank, island) in world.islands.iter().enumerate() {
            let money = money_for_others(island.money, config.hide_money_mode, &units.money)
                .map(|m| format!("<td class=\"num\">{}</td>", html_escape(&m)))
                .unwrap_or_default();
            let _ = writeln!(
                h,
                "<tr><td class=\"num\">{rank}</td><td>{name}島<br><small>{owner}</small></td>\
                 <td class=\"num\">{pop}{up}</td><td class=\"num\">{area}{ua}</td>{money}\
                 <td class=\"num\">{food}{uf}</td><td>{comment}</td></tr>",
                rank = rank + 1,
                name = html_escape(&island.name),
                owner = html_escape(&island.owner_name),
                pop = island.pop,
                up = html_escape(&units.pop),
                area = island.area,
                ua = html_escape(&units.area),
                food = island.food,
                uf = html_escape(&units.food),
                comment = html_escape(&island.comment),
            );
        }
        let _ = writeln!(h, "</table>");
    }

    let _ = writeln!(h, "<h2>最近の出来事</h2>\n<div class=\"log\">");
    for entry in game
        .logs
        .turns
        .iter()
        .take(config.top_log_turns)
        .flatten()
        .filter(|e| !e.secret)
    {
        let _ = writeln!(
            h,
            "<p>ターン{}：{}</p>",
            entry.turn,
            log_text(&entry.message)
        );
    }
    let _ = writeln!(h, "</div>\n<h2>発見の記録</h2>\n<div class=\"log\">");
    for m in game.logs.history.iter().rev() {
        let _ = writeln!(h, "<p>ターン{}：{}</p>", m.turn, log_text(&m.message));
    }
    let _ = writeln!(h, "</div>\n</body>\n</html>");
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
        assert_eq!(log_text("a & b"), "a &amp; b");
        assert_eq!(log_text("x > y"), "x &gt; y");
    }

    #[test]
    fn remaining_time() {
        assert_eq!(remaining(0), "まもなく更新");
        assert_eq!(remaining(3 * 3600 + 25 * 60 + 10), "次の更新まで 3時間25分");
    }
}
