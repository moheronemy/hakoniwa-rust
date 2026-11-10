//! 開発画面の小さな操作: コメントの変更 (`commentMain`)。

use crate::GameConfig;
use crate::model::GameState;
use crate::perl::{cgi_text, html_escape};

use super::password::check_password;
use super::{ActionError, island_index};

/// `commentMain`: 島のコメントを変える
pub fn change_comment(
    game: &mut GameState,
    config: &GameConfig,
    id: i64,
    password: &str,
    message: &str,
) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    let island = &mut game.world.islands[n];
    if !check_password(config, &island.password, password) {
        return Err(ActionError::WrongPassword);
    }
    island.comment = html_escape(&cgi_text(message));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::super::perl_compat_tests::check_case;
    use super::*;

    #[test]
    fn comment_matches_perl() {
        check_case("comment-1", &[], |game, config, case| {
            change_comment(
                game,
                config,
                1,
                &case.form(0, "PASSWORD"),
                &case.form(0, "MESSAGE"),
            )
            .unwrap();
        });
    }
}
