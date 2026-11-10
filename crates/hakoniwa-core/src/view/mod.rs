//! 島の画面に出すもの: 観光画面 (`printIslandMain`) と開発画面 (`ownerMain` → `tempOwner`) の
//! 島の情報の表 ([`info`]) と地図 ([`map`])。
//!
//! HTML は作り直すので、ここでは「何を見せるか」だけを Perl 版のとおりに作る。
//! 他人 (観光者) に隠すもの: 資金 (`$HhideMoneyMode`)、森の木の数、ミサイル基地・地雷・
//! 海底基地などの偽装、計画の印、政策の予算。
//!
//! どちらの画面もデータを変えない (Perl 版も何も保存しない。ターン処理の時刻になっていれば
//! 画面を開く前にターンが進むが、それはターン処理の側の仕事)。

pub mod info;
pub mod map;

use crate::GameConfig;
use crate::actions::password::check_password;
use crate::actions::{ActionError, island_index};
use crate::model::{GameState, World};

pub use info::{
    Holding, Icon, IncomeEstimate, IslandInfo, Policy, Popup, Unemployment, island_info,
};
pub use map::{CellView, PlannedMark};

/// 誰が見ているか
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Viewer {
    /// 観光者 (`islandMap(0)`)
    Visitor,
    /// 島の持ち主 (`islandMap(1)`)。`master` はマスターパスワードで開いたとき
    /// (`$HmainMode2 eq 'ijiri'`、地図の説明に地形の番号と値が付く)
    Owner { master: bool },
}

/// 島の画面の中身
#[derive(Debug, Clone, PartialEq)]
pub struct IslandView {
    /// 島の名前 (「島」は付かない)
    pub name: String,
    pub info: IslandInfo,
    /// 地図。行優先 (`cells[y * size + x]`)
    pub map: Vec<CellView>,
    /// 地図の一辺
    pub size: usize,
}

/// 観光画面 (`printIslandMain`)。島が無ければ [`ActionError::NoSuchIsland`] (`tempProblem`)
pub fn sightseeing(
    game: &GameState,
    config: &GameConfig,
    id: i64,
) -> Result<IslandView, ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    Ok(island_view(&game.world, config, n, Viewer::Visitor))
}

/// 開発画面 (`ownerMain`) の島の情報と地図。`password` はフォームの `PASSWORD`。
///
/// パスワードが違えば [`ActionError::WrongPassword`] (`tempWrongPassword`)。
/// マスターパスワードならどの島でも開けて、地図に地形の番号と値が出る。
/// Perl 版は無い島の ID だと 1 位の島をそのパスワードで開いてしまうが、移植版は
/// [`ActionError::NoSuchIsland`] にする
pub fn owner_view(
    game: &GameState,
    config: &GameConfig,
    id: i64,
    password: &str,
) -> Result<IslandView, ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    if !check_password(config, &game.world.islands[n].password, password) {
        return Err(ActionError::WrongPassword);
    }
    let master = !password.is_empty() && config.passwords.master.as_deref() == Some(password);
    Ok(island_view(
        &game.world,
        config,
        n,
        Viewer::Owner { master },
    ))
}

/// `index` 番目 (順位順) の島の情報と地図 (パスワードは確かめない)
pub fn island_view(world: &World, config: &GameConfig, index: usize, viewer: Viewer) -> IslandView {
    let owner = matches!(viewer, Viewer::Owner { .. });
    let (info, globals) = info::island_info_globals(world, config, index, owner);
    let map = map::island_map(world, config, index, viewer, &globals);
    let island = &world.islands[index];
    IslandView {
        name: island.name.clone(),
        info,
        map,
        size: island.map.size,
    }
}

#[cfg(test)]
mod tests;
