//! ターン処理の実行 (定時実行とデバッグ用の手動実行)。
//!
//! Perl 版はアクセスがあったときに「前回の更新から 1 ターンの秒数が過ぎていれば」
//! 1 ターン進めていた。移植版はサーバーが定期的に時刻を確かめ、過ぎているターンを
//! すべて順に処理する (止まっていた間の分も追いつく)。
//!
//! ターン処理は書き込みの順番待ち ([`crate::store`]) に並び、今の状態の複製に対して
//! 別のスレッドで行う。そのあいだ画面は 1 つ前の状態を出し、操作はターンが終わるまで待つ。

use std::sync::Arc;
use std::time::Duration;

use anyhow::Result;
use hakoniwa_core::turn::run_turn;

use crate::store::Writer;
use crate::{AppState, now_unix};

/// 1 ターン進めて保存する。バックアップのターンなら、保存の前に前のデータを退避する
async fn run_one(app: &AppState, writer: &mut Writer<'_>) -> Result<i64> {
    let current = writer.current();
    let config = app.config.clone();
    let mut rng = writer.rng().clone();
    let (next, turn, rng) = writer
        .with_data(move |data| {
            let mut next = (*current).clone();
            let report = run_turn(&mut next, &config, &mut rng);
            // バックアップはターンの前のデータ (Perl 版がターンの前に data を退避していたのと同じ)
            if report.backup_due {
                data.backup(&current, config.backup_keep)?;
            }
            data.snapshot(&next)?;
            Ok((next, report.turn, rng))
        })
        .await?;
    // 保存できたときだけ新しい状態を公開し、乱数を進める
    *writer.rng() = rng;
    writer.publish(Arc::new(next));
    Ok(turn)
}

/// 時刻が来ているターンをすべて処理する。処理したターン番号を返す
pub async fn run_due_turns(app: &AppState, now: i64) -> Result<Vec<i64>> {
    let mut writer = app.game.write().await;
    let mut done = Vec::new();
    while writer.current().world.turn_due(now, &app.config) {
        done.push(run_one(app, &mut writer).await?);
    }
    Ok(done)
}

/// 時刻に関係なく 1 ターン進める (デバッグモードの「ターンを進める」)。
/// Perl 版と同じく、最終更新時刻も 1 ターン分進む
pub async fn force_turn(app: &AppState) -> Result<i64> {
    let mut writer = app.game.write().await;
    run_one(app, &mut writer).await
}

/// 定期的にターンの時刻を確かめる。`set` はログに出すセットの名前
pub async fn scheduler(app: Arc<AppState>, every: Duration, set: String) {
    let mut interval = tokio::time::interval(every);
    interval.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Delay);
    loop {
        interval.tick().await;
        match run_due_turns(&app, now_unix()).await {
            Ok(turns) if !turns.is_empty() => {
                tracing::info!(set, ?turns, "ターンを処理しました");
            }
            Ok(_) => {}
            Err(e) => tracing::error!(set, "ターン処理に失敗しました: {e:#}"),
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
        let (data, saved) = hakoniwa_core::persist::DataDir::open(&app.data_dir)
            .unwrap()
            .unwrap();
        assert_eq!(data.header().turn, 4);
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
