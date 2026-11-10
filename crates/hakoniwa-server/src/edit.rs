//! ゲームのデータを書き換える操作の共通部分。
//!
//! 操作は複製に対して行い、保存できたときだけメモリ上の状態を差し替える
//! (保存に失敗したら何も変わらない。ターン処理の [`crate::turns`] と同じ考え方)。

use hakoniwa_core::actions::ActionError;
use hakoniwa_core::model::GameState;
use hakoniwa_core::storage;
use rand::rngs::StdRng;

use crate::AppState;

#[derive(Debug, thiserror::Error)]
pub enum EditError {
    /// 操作が受け付けられなかった (画面に理由を出す)
    #[error(transparent)]
    Action(#[from] ActionError),
    /// 保存に失敗した
    #[error("データを保存できませんでした: {0:#}")]
    Save(anyhow::Error),
}

/// `f` でゲームのデータを書き換えて保存する
pub async fn edit<T>(
    app: &AppState,
    f: impl FnOnce(&mut GameState, &mut StdRng) -> Result<T, ActionError>,
) -> Result<T, EditError> {
    let mut game = app.game.write().await;
    let mut next = game.clone();
    let out = {
        let mut rng = app.rng.lock().expect("rng lock poisoned");
        f(&mut next, &mut rng)?
    };
    storage::save(&app.state_path, &next).map_err(|e| EditError::Save(e.into()))?;
    *game = next;
    Ok(out)
}
