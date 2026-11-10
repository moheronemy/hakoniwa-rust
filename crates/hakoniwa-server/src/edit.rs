//! ゲームのデータを書き換える操作の共通部分。
//!
//! 操作は書き込みの順番待ち ([`crate::store`]) に並び、今の状態の複製に対して行い、
//! 保存できたときだけ新しい状態として公開する (保存に失敗したら何も変わらない。
//! ターン処理の [`crate::turns`] と同じ考え方)。待っているあいだも画面は読める。

use std::sync::Arc;

use hakoniwa_core::actions::ActionError;
use hakoniwa_core::model::GameState;
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
    let mut writer = app.game.write().await;
    let mut next = (*writer.current()).clone();
    let rng = writer.rng();
    let out = f(&mut next, rng)?;
    // Perl 版は次に読み込むときに空の出品の品物を決め直す (入札の値が壊れたときなど)
    hakoniwa_core::model::reroll_empty_lots(&mut next.world.auction_lots, rng);
    let next = Arc::new(next);
    let (prev, saved) = (writer.current(), next.clone());
    writer
        .with_data(move |data| Ok(data.record(&prev, &saved)?))
        .await
        .map_err(EditError::Save)?;
    writer.publish(next);
    Ok(out)
}
