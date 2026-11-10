//! アンケートの投票 (`changeAnkeito`、hako-map.cgi 1249–1296)。
//!
//! トップページの「投票する」ボタン (`AnkeButton`) で、島 (`ISLANDID`)・パスワード・選んだ項目
//! (ラジオボタン `ann`、1〜5) が送られる。票は `World::survey_votes` (`an.dat`) に足され、
//! 島の `survey_flag` (`anflag`) が 2 (投票済み) になる。
//! アンケートを出しているか (`$AnkeitoOnOff`) は、この処理では確かめない (Perl 版のまま)。

use crate::model::GameState;
use crate::perl::{cgi_text, num};

use super::{ActionError, island_index};

/// `changeAnkeito`: 島 `id` が項目 `choice` (`ann` の値をそのまま。無ければ空) に投票する。
///
/// `choice` は数値として読む (`"5.0"` は 5)。エラー (Perl 版の文面):
/// - 数値として 0 (空・未選択・数字でない): `どれか選んでね。`
/// - もう投票した (`survey_flag` が 2): `１島１票まででお願いします。`
///
/// 1〜5 以外の数値でも票は増えないまま投票済みになる (Perl 版のまま)。
/// 成功したら Perl 版は「清き１票ありがとうございました。」と出す
pub fn vote(game: &mut GameState, id: i64, choice: &str) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    let choice = num(&cgi_text(choice));
    if choice == 0.0 {
        return Err(ActionError::Rejected("どれか選んでね。".into()));
    }
    let island = &mut game.world.islands[n];
    if island.survey_flag == 2 {
        return Err(ActionError::Rejected("１島１票まででお願いします。".into()));
    }
    if let Some(k) = (1..=5).position(|k| f64::from(k) == choice) {
        game.world.survey_votes[k] += 1;
    }
    island.survey_flag = 2;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::super::auction::tests::password_ok;
    use super::super::perl_compat_tests::check_case;
    use super::*;
    use crate::perl::int;

    fn run(name: &str, expect: &[Result<(), &str>]) {
        check_case(name, &[], |game, config, case| {
            assert_eq!(case.requests.len(), expect.len());
            for (n, want) in expect.iter().enumerate() {
                let id = int(&case.form(n, "ISLANDID"));
                let got = if password_ok(game, config, case, n, id) {
                    vote(game, id, &case.form(n, "ann"))
                } else {
                    Err(ActionError::WrongPassword)
                };
                let got = got.map_err(|e| e.to_string());
                assert_eq!(got, want.map_err(str::to_string), "{name} request {n}");
            }
        });
    }

    #[test]
    fn vote_matches_perl() {
        run(
            "phase6-survey",
            &[
                Err("パスワードが違います"),
                Err("どれか選んでね。"),
                Err("どれか選んでね。"),
                Err("１島１票まででお願いします。"),
                Ok(()),
                Err("１島１票まででお願いします。"),
                Ok(()),
            ],
        );
        run(
            "phase6-survey-2",
            &[Ok(()), Err("どれか選んでね。"), Ok(())],
        );
    }
}
