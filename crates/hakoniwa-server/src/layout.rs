//! 画面の共通部分 (HTML の外枠・ナビゲーション・CSS)。
//!
//! 画面は Perl 版を再現せず作り直す。文字はすべて [`esc`] を通してから埋め込む。

use std::fmt::Write;

use hakoniwa_core::perl::html_escape;

/// 移植元の使用条件により、ゲーム画面の最上部に置く必要がある配布元へのリンク
pub const ORIGINAL_SITE: &str = "http://www.bekkoame.ne.jp/~tokuoka/hakoniwa.html";

/// HTML に埋め込む文字のエスケープ
pub fn esc(s: &str) -> String {
    html_escape(s).replace('\'', "&#39;")
}

/// ナビゲーションに出す、ログイン中の島
pub struct Viewer<'a> {
    pub island_name: &'a str,
    /// フォームに埋め込む CSRF 対策のトークン
    pub csrf: &'a str,
}

/// CSRF 対策のトークンを入れる hidden の入力欄
pub fn csrf_field(csrf: &str) -> String {
    format!(
        "<input type=\"hidden\" name=\"csrf\" value=\"{}\">",
        esc(csrf)
    )
}

const CSS: &str = r#"
:root {
  --bg: #f7f7f2; --fg: #1d2421; --muted: #5d6b64; --line: #d5d9d2; --card: #ffffff;
  --accent: #1f6f5c; --accent-fg: #ffffff; --warn: #a33a1f; --sea: #3a78b5; --flash: #e7f3ee;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #151a18; --fg: #e3e8e4; --muted: #9aa8a0; --line: #2f3834; --card: #1d2421;
    --accent: #5cc0a3; --accent-fg: #0d1210; --warn: #f08a6c; --sea: #6aa6dd; --flash: #1f332b;
  }
}
:root[data-theme="dark"] {
  --bg: #151a18; --fg: #e3e8e4; --muted: #9aa8a0; --line: #2f3834; --card: #1d2421;
  --accent: #5cc0a3; --accent-fg: #0d1210; --warn: #f08a6c; --sea: #6aa6dd; --flash: #1f332b;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--fg); margin: 0;
  font-family: system-ui, "Hiragino Sans", "Noto Sans JP", sans-serif; line-height: 1.6; }
a { color: var(--accent); }
.wrap { max-width: 1040px; margin: 0 auto; padding: 0 16px 48px; }
.origin { font-size: .8em; padding: 4px 16px; border-bottom: 1px solid var(--line); }
header.nav { display: flex; flex-wrap: wrap; gap: 4px 16px; align-items: baseline;
  padding: 12px 0; border-bottom: 1px solid var(--line); margin-bottom: 16px; }
header.nav .title { font-weight: 700; font-size: 1.15em; margin-right: auto; text-decoration: none; color: var(--fg); }
h1 { font-size: 1.5em; margin: .6em 0 .3em; } h2 { font-size: 1.2em; margin: 1.4em 0 .4em; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 12px 16px; }
.flash { background: var(--flash); border-left: 4px solid var(--accent); padding: 8px 12px; margin: 8px 0 16px; }
.error { color: var(--warn); font-weight: 600; }
.muted { color: var(--muted); }
.table-scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; }
th, td { border-bottom: 1px solid var(--line); padding: 4px 8px; text-align: left; vertical-align: top; }
td.num, th.num { text-align: right; white-space: nowrap; }
form.inline { display: inline; }
label { display: block; margin: 8px 0 2px; }
input, select, textarea, button { font: inherit; color: inherit; }
input[type=text], input[type=password], input[type=number], select, textarea {
  background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 4px 8px; max-width: 100%; }
button { background: var(--accent); color: var(--accent-fg); border: 0; border-radius: 6px; padding: 6px 14px; cursor: pointer; }
button.secondary { background: transparent; color: var(--accent); border: 1px solid var(--accent); }
.log p { margin: .2em 0; }
.map { display: grid; gap: 0; width: max-content; max-width: 100%; overflow-x: auto; }
.map .cell { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  font-size: 11px; line-height: 1; overflow: hidden; position: relative; }
.map .cell img, .map .cell .tile { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; }
.map .cell[data-x] { cursor: pointer; }
.map .cell[data-x]:focus, .map .cell.picked { outline: 2px solid var(--warn); outline-offset: -2px; }
.map .plan { position: absolute; right: 0; bottom: 0; font-size: 9px; background: rgba(0,0,0,.65); color: #fff; padding: 0 2px; }
.pre { white-space: pre-line; }
.departments { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
.dept { padding: 6px 10px; font-size: .9em; }
table.islands td:nth-child(2) { min-width: 9em; }
table.islands td.sub { border-bottom: 2px solid var(--line); font-size: .9em; }
.badge { display: inline-block; white-space: normal; max-width: 100%; overflow-wrap: anywhere; border: 1px solid var(--line); border-radius: 4px; padding: 0 4px; margin: 1px; font-size: .85em; }
.paging a { margin-right: 8px; }
table.info th { width: 8em; white-space: nowrap; color: var(--muted); font-weight: 500; }
.map .axis { color: var(--muted); font-size: 10px; }
@media (max-width: 480px) { .map .cell, .map .cell img, .map .cell .tile { width: 24px; height: 24px; font-size: 9px; } }
"#;

/// 画面全体を組み立てる
pub fn page(
    site_title: &str,
    title: &str,
    viewer: Option<&Viewer>,
    flash: Option<&str>,
    body: &str,
) -> String {
    let mut h = String::new();
    let full = if title.is_empty() {
        esc(site_title)
    } else {
        format!("{} - {}", esc(title), esc(site_title))
    };
    let _ = write!(
        h,
        "<!doctype html>\n<html lang=\"ja\">\n<head>\n<meta charset=\"utf-8\">\n\
         <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n\
         <title>{full}</title>\n<style>{CSS}</style>\n</head>\n<body>\n\
         <div class=\"origin\"><a href=\"{ORIGINAL_SITE}\">箱庭諸島スクリプト配布元</a></div>\n\
         <div class=\"wrap\">\n<header class=\"nav\"><a class=\"title\" href=\"/\">{site}</a>\n\
         <a href=\"/\">トップ</a>\n",
        site = esc(site_title),
    );
    match viewer {
        Some(v) => {
            let _ = write!(
                h,
                "<a href=\"/owner\">{}島を開発</a>\n\
                 <form class=\"inline\" method=\"post\" action=\"/logout\">{}<button class=\"secondary\">ログアウト</button></form>\n",
                esc(v.island_name),
                csrf_field(v.csrf)
            );
        }
        None => {
            let _ = write!(
                h,
                "<a href=\"/login\">ログイン</a>\n<a href=\"/register\">島を探す</a>\n"
            );
        }
    }
    let _ = writeln!(h, "</header>");
    if let Some(f) = flash {
        let _ = writeln!(h, "<div class=\"flash\" role=\"status\">{}</div>", esc(f));
    }
    h.push_str(body);
    h.push_str("\n</div>\n</body>\n</html>\n");
    h
}
