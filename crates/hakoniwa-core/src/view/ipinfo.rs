//! 裏ランキング (`hako-top2.cgi` の `tempTopPage`)。
//!
//! 情報変更の欄の「パスワード」(`OLDPASS`) にマスターパスワードを入れて `(・∀・)`
//! (`IPInfoButton`) を押すと、ふつうのトップページの代わりに出る管理者向けの表。
//! 島ごとに、記録された 6 つの IP (`ip0` 登録時、`ip1` 古 〜 `ip5` 最新) が
//! ほかの島の 6 つの IP と同じになる組の数 (同IP発見数、`ippts`) を数え、多い順に並べる。
//!
//! # Perl 版の癖で、移植でも再現していること
//!
//! - 並べ替え (`islandSortip`) を島を 1 つ数えるたびに行い、次は並べ替えた後の配列の
//!   次の位置の島を数える。数えていない島は 0 として後ろに残るので、どの島もちょうど 1 回ずつ
//!   数えられ、最後の並びは 1 回で並べ替えたのと同じになる。ただし同IPを発見した島の列
//!   (`ipkaburi`) は、同じ欄どうしで一致した島がその時点の (途中まで並べ替えた) 配列の順に並ぶ。
//! - 比べるのは文字列の一致 (`eq`)。空の欄どうしも同じ IP として数える。
//! - 自島 (同じ ID) は数えない。同じ島のほかの欄と何度一致しても、その数だけ数える。
//!
//! 表の上下 (ターン数、「自分の島へ」、新しい島を探す、島の名前とパスワードの変更) は
//! ふつうのトップページと同じ (部門・諸島の状況・ハコオク・ログは出ない)。
//! データは何も変えない。

use crate::GameConfig;
use crate::actions::ActionError;
use crate::model::GameState;
use crate::perl::cgi_text;

/// 裏ランキングの 1 行 (`tempTopPage` の表の 1 島分)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IpRankRow {
    /// 順位 (1 から)
    pub rank: usize,
    pub id: i64,
    /// 島の名前 (「島」は付かない)
    pub name: String,
    /// 放棄ターン数。0 でなければ Perl 版は名前を灰色にして `名前島(absent)` と出す
    pub absent: i64,
    /// 同IP発見数 (`ippts`)
    pub found: i64,
    /// 同IPを発見した島 (`ipkaburi`)。一致した組ごとに 1 つずつ、見つけた順。
    /// Perl 版は `名前島(ID:id)／` をつないで出す
    pub matches: Vec<IpMatch>,
    /// `ip0` (登録時)、`ip1` (古) 〜 `ip5` (最新)。Perl 版は 最新, ―, ―, ―, 古, 登録時 の
    /// 欄に `ip5`, `ip4`, `ip3`, `ip2`, `ip1`, `ip0` の順で出す
    pub ips: [String; 6],
    /// 00〜99ターンでのIP変動数 (`ip8`)
    pub changes_this_century: i64,
    /// 通算IP変動数 (`ip9`)
    pub changes_total: i64,
}

/// 同じ IP を持っていた島
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IpMatch {
    pub id: i64,
    /// 島の名前 (「島」は付かない)
    pub name: String,
}

/// 裏ランキング。`old_pass` はフォームの `OLDPASS` (情報変更の「パスワード」欄)。
///
/// マスターパスワード (`config.passwords.master`) と文字列として一致しなければ
/// [`ActionError::WrongPassword`]。Perl 版はそのときエラーを出さずにふつうのトップページを
/// 出す (`hako-top.cgi` の `topPageMain`) ので、サーバーもそうすること。
pub fn ip_ranking(
    game: &GameState,
    config: &GameConfig,
    old_pass: &str,
) -> Result<Vec<IpRankRow>, ActionError> {
    if config.passwords.master.as_deref() != Some(cgi_text(old_pass).as_str()) {
        return Err(ActionError::WrongPassword);
    }
    let islands = &game.world.islands;
    let n = islands.len();
    // @Hislands の並び (島の位置)
    let mut order: Vec<usize> = (0..n).collect();
    let mut found: Vec<Option<i64>> = vec![None; n];
    let mut matches: Vec<Vec<IpMatch>> = vec![Vec::new(); n];
    for ii in 0..n {
        let k = order[ii];
        let island = &islands[k];
        let mut pts = 0;
        // ($island->{'ipkaburi'} は初期化されない。どの島も 1 回しか数えないので効かない)
        for own in &island.ip[..6] {
            for field in 0..6 {
                for &o in &order {
                    let other = &islands[o];
                    if other.ip[field] == *own && other.id != island.id {
                        pts += 1;
                        matches[k].push(IpMatch {
                            id: other.id,
                            name: other.name.clone(),
                        });
                    }
                }
            }
        }
        found[k] = Some(pts);
        // islandSortip (iprank の大きい順、同じなら直前の順。数えていない島は 0)
        order.sort_by_key(|&i| std::cmp::Reverse(found[i].unwrap_or(0)));
    }
    Ok(order
        .iter()
        .enumerate()
        .map(|(j, &k)| {
            let island = &islands[k];
            IpRankRow {
                rank: j + 1,
                id: island.id,
                name: island.name.clone(),
                absent: island.absent,
                found: found[k].unwrap_or(0),
                matches: std::mem::take(&mut matches[k]),
                ips: std::array::from_fn(|i| island.ip[i].clone()),
                changes_this_century: island.ip_counters[0],
                changes_total: island.ip_counters[1],
            }
        })
        .collect())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::actions::perl_compat_tests::{cgi_dir, check_case};

    const MASTER: &str = "uhusnuvnurkanjhfh";

    fn response(case: &str, n: usize) -> String {
        std::fs::read_to_string(cgi_dir().join(case).join(format!("response{n}.html"))).unwrap()
    }

    /// 移植版の行から Perl 版と同じ表の HTML を組み立てる
    fn table_html(rows: &[IpRankRow]) -> String {
        let mut out = String::new();
        for r in rows {
            let name = if r.absent == 0 {
                format!("<FONT COLOR=\"#a06040\"><B>{}島</B></FONT>", r.name)
            } else {
                format!(
                    "<FONT COLOR=\"#808080\"><B>{}島({})</B></FONT>",
                    r.name, r.absent
                )
            };
            let kaburi: String = r
                .matches
                .iter()
                .map(|m| format!("{}島(ID:{})／", m.name, m.id))
                .collect();
            let th = |s: &str| format!("<FONT COLOR=\"#C00000\"><B>{s}</B></FONT>");
            out.push_str(&format!(
                "<TR>\n<TD BGCOLOR=\"LAVENDER\" ROWSPAN=3 align=center nowrap=nowrap><NOBR><FONT COLOR=\"#800000\"><B>{}</B></FONT></NOBR></TD>\n\
<TD BGCOLOR=\"LAVENDERBLUSH\" ROWSPAN=3 align=left nowrap=nowrap>\n<NOBR>\n\
<A STYlE=\"text-decoration:none\" HREF=\"http://www.xxxxxxxx/cgi-bin/hako/hako-main.cgi?Sight={}\">\n{name}\n</A><br>(ID:{})\n</NOBR>\n</TD>\n",
                r.rank, r.id, r.id
            ));
            out.push_str(&format!(
                "<TD BGCOLOR=\"LIGHTPINK\" align=right nowrap=nowrap><NOBR>{}</NOBR></TD>\n",
                r.found
            ));
            for ip in r.ips.iter().rev() {
                out.push_str(&format!(
                    "<TD BGCOLOR=\"LIGHTPINK\" align=right nowrap=nowrap><NOBR>{ip}</NOBR></TD>\n"
                ));
            }
            out.push_str(&format!(
                "</TR>\n<TR>\n<TD BGCOLOR=\"LAVENDER\" COLSPAN=7 align=left nowrap=nowrap><NOBR>{}{kaburi}</NOBR></TD>\n</TR>\n\
<TR>\n<TD BGCOLOR=\"LAVENDER\" COLSPAN=7 align=left nowrap=nowrap><NOBR>{}00～99ターンでのIP変動数({}回)・通算IP変動数({}回)</NOBR></TD>\n</TR>\n",
                th("同IPを発見した島："),
                th("その他情報："),
                r.changes_this_century,
                r.changes_total
            ));
        }
        out
    }

    #[test]
    fn ip_ranking_matches_perl() {
        check_case("view-ipinfo", &[], |game, config, case| {
            let mut config = config.clone();
            config.passwords.master = Some(MASTER.into());

            // マスターパスワード: 裏ランキング
            let rows = ip_ranking(game, &config, &case.form(0, "OLDPASS")).unwrap();
            let html = response("view-ipinfo", 0);
            let start = html.find("<TABLE BORDER>").unwrap();
            let body = &html[start..];
            let a = body.find("</TR>\n").unwrap() + "</TR>\n".len();
            let b = body.find("</TABLE>").unwrap();
            assert_eq!(table_html(&rows), &body[a..b]);
            // 島 1 と島 2 は同じ数 (元の順)。島 2 の列は、途中の並べ替えで島 3 より前に来た
            // 島 1 が先 (保存順なら島 3 が先)
            let ids: Vec<i64> = rows.iter().map(|r| r.id).collect();
            assert_eq!(ids, [1, 2, 3]);
            assert_eq!(rows[1].matches[0].id, 1);
            assert_eq!(rows[1].matches[1].id, 3);

            // 島のパスワードではふつうのトップページ
            assert_eq!(
                ip_ranking(game, &config, &case.form(1, "OLDPASS")),
                Err(ActionError::WrongPassword)
            );
            assert!(!response("view-ipinfo", 1).contains("裏ランキング"));
        });
    }

    #[test]
    fn ip_ranking_needs_a_master_password() {
        // マスターパスワードの設定が無ければ、空のパスワードでも見られない
        let config = GameConfig::default();
        let game = GameState::new_game(0, &config);
        assert_eq!(
            ip_ranking(&game, &config, ""),
            Err(ActionError::WrongPassword)
        );
    }
}
