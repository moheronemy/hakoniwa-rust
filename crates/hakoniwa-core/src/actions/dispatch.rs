//! 援助射撃 (大量破壊兵器の使用) の許可申請と許可 (`msMain` / `ms2Main`、hako-map.cgi 1056–1121)。
//!
//! 開発画面のコメント欄のフォームから、目標の島 (`TARGETID`) と有効ターン数 (`AMOUNT`、0〜24) を付けて
//! 「大量破壊兵器の使用許可申請」(`MsButton<島ID>`) か「申請許可」(`Ms2Button<島ID>`) を押す。
//! 状態は各島の `etc7` (`Island::etc_raw[2]`) に `"状態,残りターン,相手の島 ID"` で入る:
//! 申請すると自分の島が `1,ターン数,目標`、目標の島が「申請許可」すると申請した島が `2,ターン数,許可した島`。

use crate::model::GameState;
use crate::perl::{MatchScope, cgi_text, num};

use super::{ActionError, island_index};

/// `msMain`: 島 `id` から島 `target` (`TARGETID`) へ、`turns` (`AMOUNT`) ターンの許可を申請する。
///
/// `etc7` を `"1,<turns>,<target>"` にする (どちらもフォームの文字のまま、`cgi_text` だけ通す。
/// 目標の島があるかは確かめない)。`turns` が数値として 0 (空・数字でないものを含む) なら
/// `"0,0,0"` (申請の取り消し)。Perl 版は「許可申請しました」と出して開発画面に戻る
pub fn request_permission(
    game: &mut GameState,
    id: i64,
    target: &str,
    turns: &str,
) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    let (target, turns) = (cgi_text(target), cgi_text(turns));
    game.world.islands[n].etc_raw[2] = if num(&turns) == 0.0 {
        "0,0,0".into()
    } else {
        format!("1,{turns},{target}")
    };
    Ok(())
}

/// `ms2Main`: 島 `id` が、島 `target` (`TARGETID`) の申請を `turns` (`AMOUNT`) ターンで許可する。
///
/// 目標の島の `etc7` の状態が 1 (申請中) なら `"2,<turns>,<id>"` にして `Ok(true)`
/// (Perl 版は「許可申請しました」と出す)。申請中でなければ何もせず `Ok(false)` (メッセージ無しで開発画面)。
/// 申請の相手が `id` かどうかは確かめない (どの島の申請でも許可できる。Perl 版のまま)。
/// `etc7` が `数字,数字,数字` の形でなければ申請中とみなさない。
///
/// Perl 版はこの操作でパスワードを確かめず、`Ms2Button<島ID>` の島として扱う。移植版は
/// ログインした島 `id` を受け取る。目標の島は `TARGETID` の文字そのままの島 ID で探し
/// (Perl 版のハッシュ `$HidToNumber{...}` と同じ)、無ければ `NoSuchIsland` を返す
/// (Perl 版は先頭の島を使ってしまう。フォームの選択肢では起きないので再現しない)
pub fn grant_permission(
    game: &mut GameState,
    id: i64,
    target: &str,
    turns: &str,
) -> Result<bool, ActionError> {
    let target = cgi_text(target);
    let n = game
        .world
        .islands
        .iter()
        .position(|i| i.id.to_string() == target)
        .ok_or(ActionError::NoSuchIsland)?;
    let island = &mut game.world.islands[n];
    // 合わなければ前のマッチの値 ($1 は未定義) なので状態は 1 ではない
    let state = MatchScope::default().fields::<3>(&island.etc_raw[2])[0];
    if state != 1 {
        return Ok(false);
    }
    island.etc_raw[2] = format!("2,{},{id}", cgi_text(turns));
    Ok(true)
}

#[cfg(test)]
mod tests {
    use super::super::auction::tests::{button_id, password_ok};
    use super::super::perl_compat_tests::check_case;
    use super::*;

    /// `Ok(Some(changed))` は申請許可、`Ok(None)` は申請
    fn run(name: &str, expect: &[Result<Option<bool>, &str>]) {
        check_case(name, &[], |game, config, case| {
            assert_eq!(case.requests.len(), expect.len());
            for (n, want) in expect.iter().enumerate() {
                let (target, turns) = (case.form(n, "TARGETID"), case.form(n, "AMOUNT"));
                let got = if let Some(id) = button_id(case, n, "MsButton") {
                    if password_ok(game, config, case, n, id) {
                        request_permission(game, id, &target, &turns).map(|()| None)
                    } else {
                        Err(ActionError::WrongPassword)
                    }
                } else {
                    // Perl 版はパスワードを確かめない
                    let id = button_id(case, n, "Ms2Button").unwrap();
                    grant_permission(game, id, &target, &turns).map(Some)
                };
                let got = got.map_err(|e| e.to_string());
                assert_eq!(got, want.map_err(str::to_string), "{name} request {n}");
            }
        });
    }

    #[test]
    fn dispatch_matches_perl() {
        run(
            "phase6-dispatch",
            &[
                Ok(None),
                Err("パスワードが違います"),
                Ok(Some(true)),
                Ok(Some(false)),
                Ok(Some(true)),
                Ok(None),
                Ok(None),
                Ok(Some(false)),
            ],
        );
        run(
            "phase6-dispatch-2",
            &[Ok(None), Ok(None), Ok(None), Ok(Some(false))],
        );
    }
}
