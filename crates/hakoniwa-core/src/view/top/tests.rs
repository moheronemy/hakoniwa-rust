//! トップページを、元の Perl CGI が出した画面 (`tests/fixtures/cgi/<名前>/response<N>.html`) と
//! 突き合わせる。
//!
//! Perl 版の HTML を「文字・画像 (SRC・ALT・ステータスバーの文字)・ポップアップ付きの欄・
//! ボタン・選択肢」の並びに分解し、移植版の [`TopPage`] を Perl 版と同じ並びの HTML に
//! 書き出して同じように分解したものと比べる。色や太字のタグ・空白 (ASCII) は比べない。

use std::path::Path;

use rand::rngs::mock::StepRng;
use serde_json::Value as Json;

use super::*;
use crate::actions::perl_compat_tests::{cgi_dir, check_case};
use crate::config::SurveyConfig;
use crate::legacy::{self, ImportOptions};

/// HTML の切れ目
#[derive(Debug, Clone, PartialEq)]
enum Tok {
    Text(String),
    /// 表の欄・行・改行・見出しなどの区切り (続けて出ても 1 つ)
    Break,
    Img {
        src: String,
        alt: String,
        status: Option<String>,
    },
    /// マウスを載せると説明が出る欄 (`<p onMouseOver>`)
    Hover(String),
    Input {
        name: String,
        value: String,
    },
    Option(String),
}

const BREAKS: [&str; 9] = ["tr", "td", "th", "br", "h1", "hr", "p", "table", "center"];

/// タグを読む: (名前 (小文字、閉じタグは `/` 付き), 属性 (名前は小文字), 次の位置)
fn parse_tag(s: &str, start: usize) -> (String, Vec<(String, String)>, usize) {
    let b = s.as_bytes();
    let mut i = start + 1;
    let name_start = i;
    while i < b.len() && !b[i].is_ascii_whitespace() && b[i] != b'>' {
        i += 1;
    }
    let name = s[name_start..i].to_ascii_lowercase();
    let mut attrs = Vec::new();
    loop {
        while i < b.len() && b[i].is_ascii_whitespace() {
            i += 1;
        }
        if i >= b.len() || b[i] == b'>' {
            return (name, attrs, (i + 1).min(b.len()));
        }
        let a = i;
        while i < b.len() && !b[i].is_ascii_whitespace() && b[i] != b'=' && b[i] != b'>' {
            i += 1;
        }
        let key = s[a..i].to_ascii_lowercase();
        while i < b.len() && b[i].is_ascii_whitespace() {
            i += 1;
        }
        let mut value = String::new();
        if i < b.len() && b[i] == b'=' {
            i += 1;
            while i < b.len() && b[i].is_ascii_whitespace() {
                i += 1;
            }
            if i < b.len() && (b[i] == b'"' || b[i] == b'\'') {
                let q = b[i];
                let v = i + 1;
                i = v;
                while i < b.len() && b[i] != q {
                    i += 1;
                }
                value = s[v..i].to_string();
                i += 1;
            } else {
                let v = i;
                while i < b.len() && !b[i].is_ascii_whitespace() && b[i] != b'>' {
                    i += 1;
                }
                value = s[v..i].to_string();
            }
        }
        attrs.push((key, value));
    }
}

fn status_of(attrs: &[(String, String)]) -> Option<String> {
    let (_, v) = attrs.iter().find(|(k, _)| k == "onmouseover")?;
    let start = v.find("MM_displayStatusMsg('")? + "MM_displayStatusMsg('".len();
    let end = v[start..].find("')")? + start;
    Some(v[start..end].to_string())
}

fn tokens(html: &str) -> Vec<Tok> {
    let mut out = Vec::new();
    let mut text = String::new();
    let flush = |text: &mut String, out: &mut Vec<Tok>| {
        let t: String = text.chars().filter(|c| !c.is_ascii_whitespace()).collect();
        if !t.is_empty() {
            out.push(Tok::Text(t));
        }
        text.clear();
    };
    let push = |tok: Tok, out: &mut Vec<Tok>| {
        if !(tok == Tok::Break && out.last() == Some(&Tok::Break)) {
            out.push(tok);
        }
    };
    let mut i = 0;
    while i < html.len() {
        let c = html[i..].chars().next().unwrap();
        if c != '<' {
            text.push(c);
            i += c.len_utf8();
            continue;
        }
        let (name, attrs, next) = parse_tag(html, i);
        i = next;
        let attr = |k: &str| {
            attrs
                .iter()
                .find(|(a, _)| a == k)
                .map(|(_, v)| v.clone())
                .unwrap_or_default()
        };
        match name.as_str() {
            "script" => {
                let end = html[i..].to_ascii_lowercase().find("</script>").unwrap();
                i += end + "</script>".len();
            }
            "img" => {
                flush(&mut text, &mut out);
                push(
                    Tok::Img {
                        src: attr("src"),
                        alt: attr("alt"),
                        status: status_of(&attrs),
                    },
                    &mut out,
                );
            }
            "input" => {
                flush(&mut text, &mut out);
                push(
                    Tok::Input {
                        name: attr("name"),
                        value: attr("value"),
                    },
                    &mut out,
                );
            }
            "option" => {
                flush(&mut text, &mut out);
                push(Tok::Option(attr("value")), &mut out);
            }
            _ => {
                let base = name.trim_start_matches('/');
                if BREAKS.contains(&base) {
                    flush(&mut text, &mut out);
                    push(Tok::Break, &mut out);
                }
                if let Some(s) = status_of(&attrs) {
                    flush(&mut text, &mut out);
                    push(Tok::Hover(s), &mut out);
                }
            }
        }
    }
    flush(&mut text, &mut out);
    out
}

/// Perl 版の画面は Shift_JIS で出て cp932 として読んだので、EUC-JP として読んだ場合
/// (移植版のデータ) と違う文字になるものを戻す
fn normalize_cp932(s: &str) -> String {
    s.chars()
        .map(|c| match c {
            '\u{FF5E}' => '\u{301C}',
            '\u{FF0D}' => '\u{2212}',
            '\u{2225}' => '\u{2016}',
            '\u{FFE0}' => '\u{A2}',
            '\u{FFE1}' => '\u{A3}',
            '\u{FFE2}' => '\u{AC}',
            c => c,
        })
        .collect()
}

/// `start` の文字で始まる最初の位置から、`end` の文字で始まる位置の手前まで
fn region<'a>(toks: &'a [Tok], start: &str, end: &str, include_start: bool) -> &'a [Tok] {
    let is = |t: &Tok, p: &str| matches!(t, Tok::Text(s) if s.starts_with(p));
    let a = toks
        .iter()
        .position(|t| is(t, start))
        .unwrap_or_else(|| panic!("{start} not found"));
    let b = toks[a + 1..]
        .iter()
        .position(|t| is(t, end))
        .unwrap_or_else(|| panic!("{end} not found"))
        + a
        + 1;
    let a = if include_start { a } else { a + 1 };
    // 区切りの違い (前後) は比べない
    let mut r = &toks[a..b];
    while r.first() == Some(&Tok::Break) {
        r = &r[1..];
    }
    while r.last() == Some(&Tok::Break) {
        r = &r[..r.len() - 1];
    }
    r
}

fn trim_breaks(v: &[Tok]) -> &[Tok] {
    let mut r = v;
    while r.first() == Some(&Tok::Break) {
        r = &r[1..];
    }
    while r.last() == Some(&Tok::Break) {
        r = &r[..r.len() - 1];
    }
    r
}

fn assert_same(what: &str, perl: &[Tok], rust: &[Tok]) {
    let rust = trim_breaks(rust);
    if perl == rust {
        return;
    }
    let i = perl
        .iter()
        .zip(rust)
        .position(|(a, b)| a != b)
        .unwrap_or(perl.len().min(rust.len()));
    let ctx = |v: &[Tok]| {
        v[i.saturating_sub(3)..(i + 4).min(v.len())]
            .iter()
            .map(|t| format!("  {t:?}"))
            .collect::<Vec<_>>()
            .join("\n")
    };
    panic!(
        "{what}: differs at token {i} (perl {} tokens, rust {})\nperl:\n{}\nrust:\n{}",
        perl.len(),
        rust.len(),
        ctx(perl),
        ctx(rust)
    );
}

// ---- 移植版の値を Perl 版と同じ並びの HTML にする -------------------------------

fn status(h: &Hover) -> String {
    let detail = h
        .detail
        .iter()
        .map(|sec| {
            sec.iter()
                .map(|l| {
                    if l == "Complete!!" {
                        "<font color = red>Complete!!</font>".to_string()
                    } else {
                        l.clone()
                    }
                })
                .collect::<Vec<_>>()
                .join("<br>")
        })
        .collect::<Vec<_>>()
        .join("<hr>");
    format!("{}/{detail}", h.title)
}

fn badge_html(b: &Badge) -> String {
    let mut s = String::new();
    if let Some(image) = &b.image {
        s += &format!("<img src=\"{image}\" alt=\"{}\"", b.alt);
        if let Some(h) = &b.hover {
            s += &format!(" onMouseOver=\"MM_displayStatusMsg('{}');\"", status(h));
        }
        s += ">";
    }
    s + &b.text
}

fn value_html(v: &Value) -> String {
    match &v.hover {
        Some(h) => format!(
            "<p onMouseOver=\"MM_displayStatusMsg('{}');\">{}</p>",
            status(h),
            v.text
        ),
        None => v.text.clone(),
    }
}

fn render_choices(page: &TopPage) -> String {
    let mut s = "<br>".to_string();
    for c in &page.island_choices {
        s += &format!("<option value=\"{}\">{}島\n", c.id, c.name);
    }
    s + "<br>"
}

fn render_survey(sv: &SurveyView) -> String {
    let mut s = format!("{}<td>", sv.question);
    for (i, c) in sv.choices.iter().enumerate() {
        s += &format!(
            "<input name=\"ann\" value=\"{}\"><td>　{}．{}<td>{}票<td>({}%)<td>",
            i + 1,
            c.label,
            c.text,
            c.votes,
            c.percent
        );
    }
    s + &format!(
        "<input name=\"AnkeButton\" value=\"投票する\">　　({}/{}票…{}%)<td>",
        sv.total_votes, sv.island_count, sv.turnout_percent
    )
}

fn render_departments(page: &TopPage) -> String {
    page.departments
        .iter()
        .map(|d| {
            format!(
                "<td>{}NO.1<td>{}島<td>{}<td>",
                d.department.label(),
                d.island_name,
                d.value
            )
        })
        .collect()
}

fn render_list(page: &TopPage, config: &GameConfig) -> String {
    let l = &page.list;
    let mut s = format!(
        "<h1>諸島の状況({}位〜{}位)</h1><p>島の名前をクリックすると、観光することができます。</p>",
        l.first, l.last
    );
    if let Some(p) = l.paging {
        if let Some(prev) = p.prev {
            s += &format!(
                "<input name=\"view{prev}\" value=\"前の{}島\">",
                config.top_view_number
            );
        }
        if let Some((start, count)) = p.next {
            s += &format!("<input name=\"view{start}\" value=\"次の{count}島\">");
        }
        s += "<input name=\"viewALL\" value=\"全表示\">";
    }
    s += "<th>順位<th>島<th>人口<th>面積";
    if l.show_money {
        s += "<th>資金";
    }
    s += "<th>食料<th>農場<th>職場<th>採掘場<th>発電力<th>軍事技術<tr>";
    for r in &l.rows {
        s += &format!("<td>{}<td>{}島", r.rank, r.name);
        if r.absent != 0 {
            s += &format!("({})", r.absent);
        }
        s += "<br>";
        if let Some(c) = &r.capital {
            s += &format!("首都：{c}<br>");
        }
        s += &format!(
            "ID:({}){}pts.<br>失業率:({})<br>{}<br>(前ターン{}{}{})<td>",
            r.id,
            r.pts,
            r.unemployment.clone().unwrap_or_default(),
            r.tourists,
            r.last_turn.pts,
            r.last_turn.pop,
            r.last_turn.money
        );
        s += &format!("{}<td>{}<td>", r.pop, r.area);
        if let Some(m) = &r.money {
            s += m;
            if let Some(b) = &r.savings {
                s += "＋";
                s += &badge_html(b);
            }
            s += "<td>";
        }
        s += &format!(
            "{}<td>{}<td>{}<td>{}<td>{}<td>{}<tr>",
            r.food,
            value_html(&r.farm),
            value_html(&r.factory),
            value_html(&r.mountain),
            r.power,
            r.military
        );
        s += "<td>　info：";
        for b in &r.info {
            s += &badge_html(b);
        }
        s += "<tr><td>Prize：";
        for b in &r.prizes {
            s += &badge_html(b);
        }
        s += &format!("<td>予想１：{}<tr><td>", r.toto);
        s += &match &r.comment {
            CommentLine::Comment { comment } => format!("コメント : {comment}"),
            CommentLine::Owner { owner, comment } => format!("{owner} : {comment}"),
            CommentLine::AidRequested {
                owner,
                target,
                turns_left,
            } => format!("{owner} : {target}島への援助射撃許可を申請中(残り{turns_left}ターン)"),
            CommentLine::AidAllowed {
                owner,
                target,
                turns_left,
            } => format!("{owner} : {target}島への援助射撃が可能(残り{turns_left}ターン)"),
        };
        s += "<tr>";
    }
    s
}

fn render_auction(page: &TopPage) -> String {
    let a = &page.auction;
    let turn = |t: Option<i64>| t.map(|t| t.to_string()).unwrap_or_default();
    let mut s = format!("<h1>Hakoniwa Auction{}</h1>", turn(a.turn));
    const NUM: [&str; 3] = ["１", "２", "３"];
    for lot in &a.lots {
        let status = match lot.status {
            LotStatus::Sold => "(落札済み)".to_string(),
            LotStatus::Remaining(n) => format!("(残り{n}ターン)"),
        };
        if lot.number == 1 {
            s += "<th>順位";
        }
        s += &format!("<th>{}．{}{}<tr>", NUM[lot.number - 1], lot.item, status);
        for b in &lot.bids {
            if lot.number == 1 {
                s += &format!("<td>{}", b.rank);
            }
            s += &format!("<td>{}<td>{}<tr>", b.bidder, b.amount);
        }
    }
    s += "<th>高額落札ランキング<th>順位<th>落札価格<th>落札島名<th>落札品名<th>セクション<th>ボーナス<tr>";
    for h in &a.high_bids {
        s += &format!(
            "<td>{}<td>{}<td>{}<td>{}<td>{}<td>{}<tr>",
            h.rank, h.amount, h.island, h.item, h.section, h.bonus
        );
    }
    if let Some(l) = &a.leader {
        s += &format!(
            "<td>高額落札ランキング１位<br>{}島<br>１位（{}回）賞品まで（{}/{}）<td>{}連続ランキング１位の賞品を<br>{}回もらうと殿堂入りとなります。<td>",
            l.name, l.times, l.progress, l.streak, l.streak, l.hall_of_fame
        );
    }
    s += "<th>殿堂入り<th>順位<th>落札価格<th>落札島名<th>落札品名<th>セクション<th>１位保守回数<tr>";
    for h in &a.hall_of_fame {
        s += &format!(
            "<td>{}<td>{}<td>{}<td>{}<td>{}<td>{}<tr>",
            h.rank, h.amount, h.island, h.item, h.section, h.times
        );
    }
    s += "<td>(注)品番３は21位以下の島のみ入札可能です。<br>";
    for m in &page.auction_log {
        s += &format!("{m}<br>");
    }
    let turn_lines = |v: &[TurnMessage]| -> String {
        v.iter()
            .map(|m| format!("ターン{}：{}<br>", m.turn, m.message))
            .collect()
    };
    s += &format!("<td><h1>Hakoniwa Cup{}</h1>", turn(page.hcup_turn));
    s += &turn_lines(&page.hcup_log);
    s += "<h1>最近の出来事</h1>";
    s += &turn_lines(&page.logs);
    s += "<h1>発見の記録</h1>";
    s += &turn_lines(&page.history);
    s + "<hr>"
}

// ---- 突き合わせ ---------------------------------------------------------------

/// Perl 版の `hako-main.cgi` のアンケートの文面 (`$AnkeitoShitumon0`..`5`)
fn perl_survey() -> SurveyConfig {
    SurveyConfig {
        enabled: true,
        description: String::new(),
        question: "ハコオクと補助金の対策についてどう思いますか？".into(),
        choices: vec![
            "補助金に上限をつけてみる(個人的には、上限をつけたくなかったりする。。)".into(),
            "高額落札ランキングの賞品制度をいじってみる".into(),
            "HT職場を確保しにくくする(HT企業・改の修正)".into(),
            "補助金の、維持に手数料かかるよ制度".into(),
            "その他、別の選択肢で再アンケート希望でござるよ".into(),
        ],
    }
}

/// `perl_settings` (run_cgi_settings.py) に合わせた設定
fn config_for(settings: &Json) -> GameConfig {
    let mut c = GameConfig::default();
    let get = |k: &str| settings[k].as_str().map(|v| v.to_string());
    if let Some(v) = get("HhideMoneyMode") {
        c.hide_money_mode = match v.as_str() {
            "0" => HideMoneyMode::Hidden,
            "1" => HideMoneyMode::Visible,
            _ => HideMoneyMode::Rounded,
        };
    }
    if let Some(v) = get("viewNumber") {
        c.top_view_number = v.parse().unwrap();
    }
    if let Some(v) = get("HtopLogTurn") {
        c.top_log_turns = v.parse().unwrap();
    }
    if get("AnkeitoOnOff").as_deref() == Some("1") {
        c.survey = perl_survey();
    }
    c
}

fn check_top(name: &str) {
    // トップページはデータを書き換えない
    check_case(name, &[], |_, _, _| {});

    let case: Json = serde_json::from_str(
        &std::fs::read_to_string(cgi_dir().join(format!("{name}.json"))).unwrap(),
    )
    .unwrap();
    let dir = cgi_dir().join(name);
    let game = legacy::import_dir(
        &dir.join("before"),
        &ImportOptions::default(),
        &mut StepRng::new(0, 0),
    )
    .unwrap()
    .state;
    let config = config_for(&case["perl_settings"]);
    let now = case["time"].as_i64().unwrap_or(game.world.last_time + 1);
    for (n, req) in case["requests"].as_array().unwrap().iter().enumerate() {
        let html = read_response(&dir, n);
        let view = ViewRange::from_query(req["query"].as_str().unwrap_or(""));
        let page = top_page(&game, &config, now, view);
        let what = |part: &str| format!("{name} response{n} {part}");

        assert!(html.contains(&format!("nextTurn = {};", page.remaining_secs)));
        assert!(html.contains(&format!(">ターン{}<", page.turn)));
        assert_eq!(
            html.contains("NewIslandButton"),
            page.can_register,
            "{}",
            what("register")
        );

        let perl = tokens(&html);
        let rust = |s: String| tokens(&s);
        assert_same(
            &what("island choices"),
            region(
                &perl,
                "あなたの島の名前は？",
                "パスワードをどうぞ！！",
                false,
            ),
            &rust(render_choices(&page)),
        );
        match &page.survey {
            Some(sv) => assert_same(
                &what("survey"),
                region(&perl, &sv.question, "各部門別ＮＯ.１", true),
                &rust(render_survey(sv)),
            ),
            None => assert!(!html.contains("AnkeButton")),
        }
        assert_same(
            &what("departments"),
            region(&perl, "人口NO.1", "諸島の状況(", true),
            &rust(render_departments(&page)),
        );
        assert_same(
            &what("list"),
            region(&perl, "諸島の状況(", "新しい島を探す", true),
            &rust(render_list(&page, &config)),
        );
        assert_same(
            &what("auction and logs"),
            region(&perl, "HakoniwaAuction", "管理者:", true),
            &rust(render_auction(&page)),
        );
    }
}

fn read_response(dir: &Path, n: usize) -> String {
    normalize_cp932(&std::fs::read_to_string(dir.join(format!("response{n}.html"))).unwrap())
}

/// 値・印・賞・ハコオク・ログ (資金は推定値、表示は 20 島ずつ、先頭・2 番目から・全島)
#[test]
fn top_page_matches_perl() {
    check_top("view-top-1");
}

/// 資金を見せる設定・アンケート・2 島ずつの表示 (先頭・2 番目から・島の数より後ろから)
#[test]
fn top_page_visible_money_survey_paging_matches_perl() {
    check_top("view-top-2");
}

/// 資金を隠す設定・2 ターン分のログ
#[test]
fn top_page_hidden_money_matches_perl() {
    check_top("view-top-3");
}

/// 元の 3 島のデータ (印がほとんど無い島)
#[test]
fn top_page_plain_data_matches_perl() {
    check_top("view-top-plain");
}

#[test]
fn view_range_from_query() {
    assert_eq!(ViewRange::from_query(""), ViewRange::From(0));
    assert_eq!(ViewRange::from_query("view20=次の"), ViewRange::From(20));
    assert_eq!(ViewRange::from_query("viewALL=x"), ViewRange::All);
    assert_eq!(ViewRange::from_query("viewx&view3"), ViewRange::From(3));
    assert_eq!(ViewRange::from_query("Sight=1"), ViewRange::From(0));
}

#[test]
fn prize_regex_and_turn_cups() {
    assert_eq!(match_prize("0,0,"), Some(("0", "0", "")));
    assert_eq!(match_prize("x1,2,3,4,"), Some(("1", "2", "3,4,")));
    assert_eq!(match_prize("a,b"), None);
    assert_eq!(turn_cups("100,200,"), ["100", "200"]);
    assert_eq!(turn_cups("ab1,,3x,"), ["1", "", ""]);
    assert!(turn_cups("12").is_empty());
}

#[test]
fn no_islands() {
    let config = GameConfig::default();
    let game = GameState::new_game(1_794_250_000, &config);
    let page = top_page(&game, &config, game.world.last_time, ViewRange::All);
    assert!(page.departments.is_empty());
    assert!(page.list.rows.is_empty());
    assert!(page.auction.lots.is_empty() && page.auction.leader.is_none());
    assert!(page.can_register);
}
