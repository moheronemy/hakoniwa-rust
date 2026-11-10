//! ローカル掲示板 (`localBbsMain`、hako-map.cgi 1122〜1248 行、`slideLbbsMessage` /
//! `slideBackLbbsMessage` 1297〜1318 行) と、その表示 (`tempLbbsContents` 3859〜3908 行)。
//!
//! 1 件は `発言者<種別>名前>本文` の形の 1 行で、[`Island::lbbs`] に新しい順に入る:
//! - `発言者` は `秘密フラグ<発言島`。秘密フラグは極秘なら 1、そうでなければ 0。
//!   発言島は観光者の発言なら `〇〇島` (匿名なら接続元のアドレス)、島主の発言なら空
//! - `種別` は観光者なら 0、島主なら 1
//! - `名前` は `ターン数：名前`。名前と本文は HTML エスケープ済み
//!
//! 空の欄は `0<<0>>`。

use crate::GameConfig;
use crate::model::{GameState, Island};
use crate::perl::{self, cgi_text, cut_column, html_escape};

use super::{ActionError, Request, island_index};

const EMPTY: &str = "0<<0>>";

fn no_message() -> ActionError {
    ActionError::Rejected("名前または内容の欄が空欄です。".into())
}

/// 観光者の発言のしかた (フォームの `LBBSTYPE` と `ISLANDID2`)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VisitorSpeaker {
    /// 公開 (`PUBLIC`)。発言する島 (ログインしている島) の ID。`cost_public` を払う
    Public(i64),
    /// 極秘 (`SECRET`)。発言する島の ID。`cost_secret` を払う (足りなければ断る)
    Secret(i64),
    /// 匿名 (`ANON`)。発言者は接続元のアドレスになり、費用はかからない。
    /// Perl 版は `$HlbbsAnon` が 0 でもフォームに無いだけで受け付ける。
    /// サーバーは `config.lbbs.allow_anonymous` のときだけ出すこと
    Anonymous,
}

/// 島主の記帳 (`LbbsButtonOW<島ID>`)。島の持ち主であることは呼び出し側で確かめておく。
///
/// `name` (`LBBSNAME`) が空なら「名前または内容の欄が空欄です。」で断る
/// (Perl 版は名前を 2 回調べていて本文は調べないので、本文は空でもよい)。
/// 成功したら Perl 版は「記帳を行いました」と出して開発画面に戻る
pub fn owner_post(
    game: &mut GameState,
    config: &GameConfig,
    id: i64,
    name: &str,
    message: &str,
) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    let name = cgi_text(name);
    if name.is_empty() {
        return Err(no_message());
    }
    let turn = game.world.turn;
    post(
        &mut game.world.islands[n],
        config,
        turn,
        "0<",
        '1',
        &name,
        message,
    );
    Ok(())
}

/// 島主による削除 (`LbbsButtonDL<島ID>`、`NUMBER` は 0 始まりの番号)。
/// 島の持ち主であることは呼び出し側で確かめておく。
///
/// その番号を消して前に詰め、最後の欄を空にする。番号が掲示板の行数以上なら何も消さずに
/// 最後の欄だけ空にする (Perl 版のまま)。
/// 成功したら Perl 版は「記帳内容を削除しました」と出して開発画面に戻る
pub fn owner_delete(
    game: &mut GameState,
    config: &GameConfig,
    id: i64,
    number: usize,
) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    let lbbs = &mut game.world.islands[n].lbbs;
    let max = config.lbbs.max;
    // slideBackLbbsMessage
    if number < lbbs.len() {
        lbbs.remove(number);
    }
    if lbbs.len() < max {
        lbbs.resize(max, String::new());
    }
    lbbs[max - 1] = EMPTY.to_string();
    Ok(())
}

/// 観光者の記帳 (`LbbsButtonSS<島ID>`): 島 `target` の掲示板に書く。
///
/// 公開・極秘の発言では、`speaker` の島 (呼び出し側でパスワードを確かめておく) が費用を払う。
/// Perl 版と同じ順で調べる: 書く先の島が無い ([`ActionError::NoSuchIsland`])、
/// 名前が空 (「名前または内容の欄が空欄です。」)、発言する島が無い (NoSuchIsland)、
/// 極秘で資金が `cost_secret` に足りない (「資金不足のため記帳できません」)。
/// 公開の費用は足りなくても払う (資金が負になりうる、Perl 版のまま)。
///
/// 成功したら Perl 版は「記帳を行いました」と出して観光画面に戻る
pub fn visitor_post(
    game: &mut GameState,
    config: &GameConfig,
    req: Request,
    target: i64,
    speaker: VisitorSpeaker,
    name: &str,
    message: &str,
) -> Result<(), ActionError> {
    let n = island_index(&game.world, target).ok_or(ActionError::NoSuchIsland)?;
    let name = cgi_text(name);
    if name.is_empty() {
        return Err(no_message());
    }
    let prefix = match speaker {
        VisitorSpeaker::Public(id) | VisitorSpeaker::Secret(id) => {
            let secret = matches!(speaker, VisitorSpeaker::Secret(_));
            // 発言する島 (Perl 版では内側の my($island)。費用はこちらから払う)
            let s = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
            let island = &mut game.world.islands[s];
            let cost = if secret {
                config.lbbs.cost_secret
            } else {
                config.lbbs.cost_public
            };
            if secret && island.money < cost {
                return Err(ActionError::Rejected("資金不足のため記帳できません".into()));
            }
            island.money -= cost;
            let flag = if secret { '1' } else { '0' };
            format!("{flag}<{}島", island.name)
        }
        VisitorSpeaker::Anonymous => format!("0<{}", req.remote_addr),
    };
    let turn = game.world.turn;
    post(
        &mut game.world.islands[n],
        config,
        turn,
        &prefix,
        '0',
        &name,
        message,
    );
    Ok(())
}

/// 記帳モード: 後ろにずらして先頭に書く。`name` は `cgi_text` 済み
fn post(
    island: &mut Island,
    config: &GameConfig,
    turn: i64,
    speaker: &str,
    kind: char,
    name: &str,
    message: &str,
) {
    let lbbs = &mut island.lbbs;
    // slideLbbsMessage: pop して先頭を複製する
    lbbs.resize(config.lbbs.max, String::new());
    lbbs.pop();
    let first = lbbs.first().cloned().unwrap_or_default();
    lbbs.insert(0, first);
    let name = format!("{turn}：{}", html_escape(name));
    let message = html_escape(&cut_column(&cgi_text(message), 80));
    lbbs[0] = format!("{speaker}<{kind}>{name}>{message}");
}

/// 掲示板を見る人
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LbbsViewer {
    /// 島の持ち主 (開発画面)。極秘の発言も見える
    Owner,
    /// それ以外 (観光画面)。極秘の発言は「- 極秘 -」とだけ出る
    Visitor,
}

/// 掲示板の 1 件 (表示用)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LbbsPost {
    /// 番号 (1 始まり、削除の番号は これ - 1)
    pub number: usize,
    /// 島主の発言か (Perl 版では色が違う)
    pub by_owner: bool,
    /// 極秘の発言か (島主に見せるときは本文の前に「(秘)」を付ける)
    pub secret: bool,
    /// 中身。見る人が観光者で極秘の発言なら `None` (「- 極秘 -」と出す)
    pub content: Option<LbbsContent>,
}

/// 掲示板の 1 件の中身。**`name` と `message` は保存時に HTML エスケープ済み**なので、
/// そのまま HTML に出す (もう一度エスケープしない)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LbbsContent {
    /// 発言島 (`〇〇島` か接続元)。`show_speaker` が偽か、空なら `None`。Perl 版は
    /// 本文の後ろに `(発言島)` と出す
    pub speaker: Option<String>,
    /// `ターン数：名前`
    pub name: String,
    /// 本文
    pub message: String,
}

/// `tempLbbsContents`: 島の掲示板のうち表示するもの (新しい順)。
///
/// Perl 版は形式に合う行をすべて出す。空の欄 (`0<<0>>`) も名前と本文が空の行として出るので、
/// 画面で省くなら `name` と `message` が空のものを省く
pub fn lbbs_posts(island: &Island, config: &GameConfig, viewer: LbbsViewer) -> Vec<LbbsPost> {
    let mut out = Vec::new();
    for i in 0..config.lbbs.max {
        let Some(line) = island.lbbs.get(i) else {
            continue;
        };
        let Some([flag, speaker, kind, name, message]) = parse_line(line) else {
            continue;
        };
        let by_owner = perl::num(kind) != 0.0;
        let secret = !by_owner && perl::num(flag) != 0.0;
        let hidden = secret && viewer == LbbsViewer::Visitor;
        out.push(LbbsPost {
            number: i + 1,
            by_owner,
            secret,
            content: (!hidden).then(|| LbbsContent {
                speaker: (config.lbbs.show_speaker && !speaker.is_empty())
                    .then(|| speaker.to_string()),
                name: name.to_string(),
                message: message.to_string(),
            }),
        });
    }
    out
}

/// `/([0-9]*)\<(.*)\<([0-9]*)\>(.*)\>(.*)$/` (先頭に固定しない、貪欲) の `$1`〜`$5`
fn parse_line(line: &str) -> Option<[&str; 5]> {
    // いちばん左で始まるマッチ: 最初の '<' の直前の数字の並びが $1 になる
    let lt = line.find('<')?;
    let d1 = line[..lt]
        .bytes()
        .rev()
        .take_while(u8::is_ascii_digit)
        .count();
    let flag = &line[lt - d1..lt];
    let rest = &line[lt + 1..];
    // $2 は貪欲なので、後ろの '<' から順に「数字 '>' ... '>'」が続くものを探す
    for (i, _) in rest.rmatch_indices('<') {
        let after = &rest[i + 1..];
        let d3 = after.bytes().take_while(u8::is_ascii_digit).count();
        let Some(tail) = after[d3..].strip_prefix('>') else {
            continue;
        };
        if let Some(j) = tail.rfind('>') {
            return Some([flag, &rest[..i], &after[..d3], &tail[..j], &tail[j + 1..]]);
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::super::password::check_password;
    use super::super::perl_compat_tests::check_case;
    use super::*;

    fn button(form: &serde_json::Map<String, serde_json::Value>) -> Option<(String, i64)> {
        form.keys().find_map(|k| {
            let rest = k.strip_prefix("LbbsButton")?;
            Some((rest[..2].to_string(), perl::int(&rest[2..])))
        })
    }

    /// Perl 版の画面の掲示板の表 (番号, タグを除いた中身)
    fn perl_board(html: &str) -> Vec<(usize, String)> {
        let strip = |s: &str| {
            let mut out = String::new();
            let mut tag = false;
            for c in s.chars() {
                match c {
                    '<' => tag = true,
                    '>' if tag => tag = false,
                    _ if !tag => out.push(c),
                    _ => {}
                }
            }
            out
        };
        html.split("<TR><TD align=center>")
            .skip(1)
            .filter_map(|part| {
                let (num, rest) = part.split_once("</TD><TD>")?;
                let cell = rest.split("</TD></TR>").next()?;
                Some((strip(num).trim().parse().ok()?, strip(cell)))
            })
            .collect()
    }

    /// 移植版の表示を Perl 版の表の中身 (タグを除いたもの) と同じ形にする
    fn render(posts: &[LbbsPost]) -> Vec<(usize, String)> {
        posts
            .iter()
            .map(|p| {
                let text = match &p.content {
                    None => "- 極秘 -".to_string(),
                    Some(c) => {
                        let speaker = c
                            .speaker
                            .as_ref()
                            .map(|s| format!("({s})"))
                            .unwrap_or_default();
                        let mark = if p.secret { "(秘)" } else { "" };
                        format!("{} >{mark} {} {speaker}", c.name, c.message)
                    }
                };
                (p.number, text)
            })
            .collect()
    }

    #[test]
    fn lbbs_matches_perl() {
        check_case("lbbs", &[], |game, config, case| {
            for n in 0..case.requests.len() {
                let form = case.requests[n]["form"].as_object().unwrap().clone();
                let html = std::fs::read_to_string(
                    super::super::perl_compat_tests::cgi_dir()
                        .join(format!("lbbs/response{n}.html")),
                )
                .unwrap();
                let Some((mode, id)) = button(&form) else {
                    // 表示だけの操作 (開発画面・観光画面)
                    let (id, viewer) = if form.contains_key("OwnerButton") {
                        (perl::int(&case.form(n, "ISLANDID")), LbbsViewer::Owner)
                    } else {
                        (perl::int(&case.form(n, "TARGETID")), LbbsViewer::Visitor)
                    };
                    let island = game.world.island_by_id(id).unwrap();
                    assert_eq!(
                        render(&lbbs_posts(island, config, viewer)),
                        perl_board(&html)
                    );
                    continue;
                };
                let pw = case.form(n, "PASSWORD");
                let name = case.form(n, "LBBSNAME");
                let message = case.form(n, "LBBSMESSAGE");
                let addr = case.addr(n);
                let req = Request {
                    now: case.now,
                    remote_addr: &addr,
                };
                let ok = |game: &GameState, id: i64| {
                    game.world
                        .island_by_id(id)
                        .is_some_and(|i| check_password(config, &i.password, &pw))
                };
                let result = match mode.as_str() {
                    "OW" => {
                        // Perl 版の順: 島 → 名前 → パスワード
                        if game.world.island_by_id(id).is_some()
                            && !cgi_text(&name).is_empty()
                            && !ok(game, id)
                        {
                            continue;
                        }
                        owner_post(game, config, id, &name, &message)
                    }
                    "DL" => {
                        if game.world.island_by_id(id).is_some() && !ok(game, id) {
                            continue;
                        }
                        owner_delete(
                            game,
                            config,
                            id,
                            perl::int(&case.form(n, "NUMBER")) as usize,
                        )
                    }
                    _ => {
                        let speaker_id = perl::int(&case.form(n, "ISLANDID2"));
                        let speaker = match case.form(n, "LBBSTYPE").as_str() {
                            "ANON" => VisitorSpeaker::Anonymous,
                            "SECRET" => VisitorSpeaker::Secret(speaker_id),
                            _ => VisitorSpeaker::Public(speaker_id),
                        };
                        if speaker != VisitorSpeaker::Anonymous
                            && game.world.island_by_id(id).is_some()
                            && !cgi_text(&name).is_empty()
                            && game.world.island_by_id(speaker_id).is_some()
                            && !ok(game, speaker_id)
                        {
                            continue;
                        }
                        visitor_post(game, config, req, id, speaker, &name, &message)
                    }
                };
                // Perl 版の画面と同じ結果か
                match result {
                    Ok(()) => {
                        assert!(
                            html.contains("記帳を行いました")
                                || html.contains("記帳内容を削除しました"),
                            "request {n}"
                        );
                        // そのあとに出る掲示板 (島主は開発画面、観光者は観光画面)
                        let viewer = if mode == "SS" {
                            LbbsViewer::Visitor
                        } else {
                            LbbsViewer::Owner
                        };
                        let island = game.world.island_by_id(id).unwrap();
                        assert_eq!(
                            render(&lbbs_posts(island, config, viewer)),
                            perl_board(&html),
                            "request {n}"
                        );
                    }
                    Err(ActionError::NoSuchIsland) => {
                        assert!(html.contains("問題発生"), "request {n}")
                    }
                    Err(e) => assert!(html.contains(&e.to_string()), "request {n}: {e}"),
                }
            }
        });
    }

    #[test]
    fn line_parsing_matches_perl_regex() {
        assert_eq!(parse_line("0<<0>>"), Some(["0", "", "0", "", ""]));
        assert_eq!(
            parse_line("1<テスト島<0>3：秘密>ないしょ"),
            Some(["1", "テスト島", "0", "3：秘密", "ないしょ"])
        );
        // 先頭に固定しないので、前のゴミは飛ばす。$2 と $4 は貪欲
        assert_eq!(
            parse_line("ab12<x<y<3>n>m>z"),
            Some(["12", "x<y", "3", "n>m", "z"])
        );
        // 後ろの '<' が形式に合わなければ前の '<' まで戻る
        assert_eq!(parse_line("0<a<1>b>c<d"), Some(["0", "a", "1", "b", "c<d"]));
        assert_eq!(parse_line(""), None);
        assert_eq!(parse_line("0<<0>"), None);
    }

    #[test]
    fn visitor_does_not_see_secret_posts() {
        let config = GameConfig::default();
        let mut island = Island::blank(1, "テスト", &config);
        island.lbbs[0] = "1<Alpha島<0>3：秘密>ないしょ".into();
        island.lbbs[1] = "0<Alpha島<0>3：旅人>こんにちは".into();
        island.lbbs[2] = "0<<1>3：島主>ようこそ".into();
        let owner = lbbs_posts(&island, &config, LbbsViewer::Owner);
        let visitor = lbbs_posts(&island, &config, LbbsViewer::Visitor);
        assert_eq!(owner.len(), config.lbbs.max);
        assert!(owner[0].secret && owner[0].content.is_some());
        assert_eq!(
            owner[0].content.as_ref().unwrap().speaker.as_deref(),
            Some("Alpha島")
        );
        assert!(visitor[0].secret && visitor[0].content.is_none());
        assert_eq!(visitor[1].content, owner[1].content);
        assert!(visitor[2].by_owner && !visitor[2].secret);
        assert_eq!(visitor[2].content.as_ref().unwrap().speaker, None);
        assert_eq!(visitor[3].content.as_ref().unwrap().name, "");
    }
}
