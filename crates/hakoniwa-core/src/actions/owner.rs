//! 開発画面の小さな操作: コメントの変更 (`commentMain`)。
//!
//! 開発画面の操作は、ログインのときにパスワードを確かめた島の ID を受け取る
//! (Perl 版は操作のたびに `checkPassword` していた。テストではその確認も再現する)。

use crate::model::GameState;
use crate::perl::{cgi_text, html_escape};

use super::{ActionError, island_index};

/// `commentMain`: 島のコメントを変える
pub fn set_comment(game: &mut GameState, id: i64, message: &str) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    game.world.islands[n].comment = html_escape(&cgi_text(message));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::super::password::check_password;
    use super::super::perl_compat_tests::check_case;
    use super::*;

    #[test]
    fn comment_matches_perl() {
        check_case("comment-1", &[], |game, config, case| {
            let island = &game.world.islands[island_index(&game.world, 1).unwrap()];
            assert!(check_password(
                config,
                &island.password,
                &case.form(0, "PASSWORD")
            ));
            set_comment(game, 1, &case.form(0, "MESSAGE")).unwrap();
        });
    }
}
