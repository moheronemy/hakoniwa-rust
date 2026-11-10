//! 開発画面のコメント欄から送る 2 つの操作: 各種予想 (`totoMain`、hako-map.cgi 561–607) と
//! 首都名の変更 (`totosMain`、608–637)。
//!
//! どちらもコメント欄 (`MESSAGE`) の文字を使う。「各種予想」ボタン (`TotoButton<島ID>`) は
//! toto の予想 (`eis8`、トップページの「予想１」) を、「首都名変更」ボタン (`TotosButton<島ID>`) は
//! 首都の名前 (`totoyoso2`、地図の「首都〇〇」) を書き換える。

use crate::model::GameState;
use crate::perl::{cgi_text, cut_column, html_escape};

use super::{ActionError, island_index};

/// 各種予想を受け付けるターンか (ターン数を 100 で割った余りが 0〜25 か 50〜75)
pub fn prediction_open(turn: i64) -> bool {
    let t = turn.rem_euclid(100);
    !((76..=99).contains(&t) || (26..=49).contains(&t))
}

/// `totoMain`: toto の予想 (`eis8`) を `message` (`MESSAGE`) にする。
///
/// 文字は `cgi_text` → 44 桁 (`cutColumn`) → `htmlEscape` の順に加工する。
/// 受付期間 ([`prediction_open`]) の外なら `現在、変更できません`
/// (Perl 版はこれをパスワードより先に確かめる)。成功したら Perl 版は「予想しました」と出して開発画面に戻る
pub fn set_prediction(game: &mut GameState, id: i64, message: &str) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    if !prediction_open(game.world.turn) {
        return Err(ActionError::Rejected("現在、変更できません".into()));
    }
    game.world.islands[n].eis8 = html_escape(&cut_column(&cgi_text(message), 44));
    Ok(())
}

/// `totosMain`: 首都の名前 (`totoyoso2`) を `message` (`MESSAGE`) にする。
///
/// 文字は `cgi_text` → 32 桁 → `htmlEscape`。画面はボタンを `totoyoso2` が数値として 0 のときだけ
/// 出すが、この処理は確かめないので何度でも変えられる (Perl 版のまま)。
/// 成功したら Perl 版は「変更しました」と出して開発画面に戻る
pub fn set_capital_name(game: &mut GameState, id: i64, message: &str) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    game.world.islands[n].totoyoso2 = html_escape(&cut_column(&cgi_text(message), 32));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::super::auction::tests::{button_id, password_ok};
    use super::super::perl_compat_tests::check_case;
    use super::*;

    /// 各操作を Perl 版の順 (予想は受付期間 → パスワード、首都名はパスワード) で行う
    fn run(name: &str, expect: &[Result<(), &str>]) {
        check_case(name, &[], |game, config, case| {
            assert_eq!(case.requests.len(), expect.len());
            for (n, want) in expect.iter().enumerate() {
                let msg = case.form(n, "MESSAGE");
                let got = if let Some(id) = button_id(case, n, "TotoButton") {
                    if prediction_open(game.world.turn) && !password_ok(game, config, case, n, id) {
                        Err(ActionError::WrongPassword)
                    } else {
                        set_prediction(game, id, &msg)
                    }
                } else {
                    let id = button_id(case, n, "TotosButton").unwrap();
                    if password_ok(game, config, case, n, id) {
                        set_capital_name(game, id, &msg)
                    } else {
                        Err(ActionError::WrongPassword)
                    }
                };
                let got = got.map_err(|e| e.to_string());
                assert_eq!(got, want.map_err(str::to_string), "{name} request {n}");
            }
        });
    }

    #[test]
    fn toto_matches_perl() {
        run(
            "phase6-toto",
            &[
                Ok(()),
                Err("パスワードが違います"),
                Ok(()),
                Ok(()),
                Err("パスワードが違います"),
            ],
        );
    }

    #[test]
    fn prediction_period_matches_perl() {
        for (turn, open) in [
            (25, true),
            (26, false),
            (49, false),
            (50, true),
            (76, false),
        ] {
            let want = if open {
                Ok(())
            } else {
                Err("現在、変更できません")
            };
            run(&format!("phase6-toto-t{turn}"), &[want, Ok(())]);
        }
        assert!(prediction_open(0) && prediction_open(75) && prediction_open(100));
        assert!(!prediction_open(99));
    }
}
