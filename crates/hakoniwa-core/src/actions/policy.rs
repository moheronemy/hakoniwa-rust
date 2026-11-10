//! 政策の予算 (`shoueneMain`, `bousaiMain`, `kankouMain`, `sizenMain`, `kyouikuMain`,
//! `chochikuMain`、hako-map.cgi 638〜870 行)。
//!
//! 予算は `etc5` (`island.etc_raw[0]`、31 欄のカンマ区切り) の決まった欄に入る。

use crate::model::GameState;
use crate::perl::{self, cgi_text};

use super::{ActionError, island_index};

/// 政策の種類 (開発画面のボタン `<名前>Button<島ID>`)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Policy {
    /// 省エネ (`ShoueneButton`、etc5 の 1 番目の欄)
    Shouene,
    /// 防災 (`BousaiButton`、3 番目)
    Bousai,
    /// 観光 (`KankouButton`、5 番目)
    Kankou,
    /// 自然 (`SizenButton`、7 番目)
    Sizen,
    /// 教育 (`KyouikuButton`、9 番目)
    Kyouiku,
    /// 貯蓄 (`ChochikuButton`、11 番目)
    Chochiku,
}

impl Policy {
    /// etc5 の何番目の欄か (0 始まり)
    pub fn field(self) -> usize {
        match self {
            Self::Shouene => 1,
            Self::Bousai => 3,
            Self::Kankou => 5,
            Self::Sizen => 7,
            Self::Kyouiku => 9,
            Self::Chochiku => 11,
        }
    }
}

/// 政策の予算を `amount` (フォームの `AMOUNT`、受け取った文字列のまま) にする。
/// 成功したら Perl 版は「変更しました」と出して開発画面に戻る。
///
/// 島の持ち主であることは呼び出し側で確かめておく。Perl 版のとおり:
/// - `etc5` が数値として 0 (先頭の欄が 0) なら、まず 31 欄すべて 0 にする。先頭の欄は
///   ふつう 0 なので、ほかの政策の予算は消える (Perl 版のまま)
/// - 50 より大きければ 50。下限や数字かどうかは確かめず、そのまま保存する
///   (数字でない値が入ると次からは欄が読めず、ほかの欄は空になる。Perl 版のまま)
pub fn set_policy(
    game: &mut GameState,
    id: i64,
    policy: Policy,
    amount: &str,
) -> Result<(), ActionError> {
    // Perl 版は島が無いと 0 番目の島を使う。移植版では島が無いことにする
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    let island = &mut game.world.islands[n];
    // if($island->{'etc5'} == 0) は数値比較
    if perl::num(&island.etc_raw[0]) == 0.0 {
        island.etc_raw[0] = vec!["0"; 31].join(",");
    }
    let mut arg = cgi_text(amount);
    if perl::num(&arg) > 50.0 {
        arg = "50".into();
    }
    // /^([0-9]*),...$/ (31 欄) に合わなければ $1.. は未定義なので、すべて空になる
    let parts: Vec<&str> = island.etc_raw[0].split(',').collect();
    let mut fields: Vec<String> =
        if parts.len() == 31 && parts.iter().all(|p| p.bytes().all(|b| b.is_ascii_digit())) {
            parts.into_iter().map(str::to_string).collect()
        } else {
            vec![String::new(); 31]
        };
    fields[policy.field()] = arg;
    island.etc_raw[0] = fields.join(",");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::super::password::check_password;
    use super::super::perl_compat_tests::check_case;
    use super::*;
    use crate::GameConfig;

    #[test]
    fn policies_match_perl() {
        check_case("policy", &[], |game, config, case| {
            for n in 0..case.requests.len() {
                let form = case.requests[n]["form"].as_object().unwrap();
                let (policy, id) = form
                    .keys()
                    .find_map(|k| {
                        let (name, id) = k.split_once("Button")?;
                        let p = match name {
                            "Shouene" => Policy::Shouene,
                            "Bousai" => Policy::Bousai,
                            "Kankou" => Policy::Kankou,
                            "Sizen" => Policy::Sizen,
                            "Kyouiku" => Policy::Kyouiku,
                            "Chochiku" => Policy::Chochiku,
                            _ => return None,
                        };
                        Some((p, id.parse::<i64>().ok()?))
                    })
                    .unwrap();
                let island = game.world.island_by_id(id).unwrap();
                if !check_password(config, &island.password, &case.form(n, "PASSWORD")) {
                    continue;
                }
                set_policy(game, id, policy, &case.form(n, "AMOUNT")).unwrap();
            }
        });
    }

    #[test]
    fn missing_island() {
        let config = GameConfig::default();
        let mut game = GameState::new_game(0, &config);
        assert_eq!(
            set_policy(&mut game, 1, Policy::Bousai, "5"),
            Err(ActionError::NoSuchIsland)
        );
    }
}
