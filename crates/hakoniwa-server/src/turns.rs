//! ターン処理の実行 (定時実行とデバッグ用の手動実行)。
//!
//! Perl 版はアクセスがあったときに「前回の更新から 1 ターンの秒数が過ぎていれば」
//! 1 ターン進めていた。移植版はサーバーが定期的に時刻を確かめ、過ぎているターンを
//! すべて順に処理する (止まっていた間の分も追いつく)。

use std::sync::Arc;
use std::time::Duration;

use anyhow::Result;
use hakoniwa_core::model::GameState;
use hakoniwa_core::storage;
use hakoniwa_core::turn::run_turn;

use crate::{AppState, now_unix};

/// 1 ターン進めて保存する。バックアップのターンなら、保存の前に前のデータを退避する
fn run_one(app: &AppState, game: &mut GameState) -> Result<i64> {
    let mut next = game.clone();
    let report = {
        let mut rng = app.rng.lock().expect("rng lock poisoned");
        run_turn(&mut next, &app.config, &mut *rng)
    };
    if report.backup_due {
        storage::rotate_backups(&app.state_path, app.config.backup_keep)?;
    }
    storage::save(&app.state_path, &next)?;
    // 保存できたときだけメモリ上の状態を進める
    *game = next;
    Ok(report.turn)
}

/// 時刻が来ているターンをすべて処理する。処理したターン番号を返す
pub async fn run_due_turns(app: &AppState, now: i64) -> Result<Vec<i64>> {
    let mut game = app.game.write().await;
    let mut done = Vec::new();
    while game.world.turn_due(now, &app.config) {
        done.push(run_one(app, &mut game)?);
    }
    Ok(done)
}

/// 時刻に関係なく 1 ターン進める (デバッグモードの「ターンを進める」)。
/// Perl 版と同じく、最終更新時刻も 1 ターン分進む
pub async fn force_turn(app: &AppState) -> Result<i64> {
    let mut game = app.game.write().await;
    run_one(app, &mut game)
}

/// 定期的にターンの時刻を確かめる
pub async fn scheduler(app: Arc<AppState>, every: Duration) {
    let mut interval = tokio::time::interval(every);
    interval.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Delay);
    loop {
        interval.tick().await;
        match run_due_turns(&app, now_unix()).await {
            Ok(turns) if !turns.is_empty() => {
                tracing::info!(?turns, "ターンを処理しました");
            }
            Ok(_) => {}
            Err(e) => tracing::error!("ターン処理に失敗しました: {e:#}"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tests::test_app;

    #[tokio::test]
    async fn catches_up_on_missed_turns() {
        let (app, _dir) = test_app();
        let start = app.game.read().await.world.last_time;
        let unit = app.config.unit_time;

        assert!(
            run_due_turns(&app, start + unit - 1)
                .await
                .unwrap()
                .is_empty()
        );

        // 3 ターン分の時間が過ぎていれば 3 ターン進む
        let turns = run_due_turns(&app, start + unit * 3 + 10).await.unwrap();
        assert_eq!(turns, [2, 3, 4]);
        let game = app.game.read().await;
        assert_eq!(game.world.last_time, start + unit * 3);
        // 保存もされている
        let saved = storage::load(&app.state_path).unwrap().unwrap();
        assert_eq!(saved.world.turn, 4);
    }

    #[tokio::test]
    async fn forced_turn_moves_clock() {
        let (app, _dir) = test_app();
        let start = app.game.read().await.world.last_time;
        assert_eq!(force_turn(&app).await.unwrap(), 2);
        assert_eq!(
            app.game.read().await.world.last_time,
            start + app.config.unit_time
        );
    }
}
