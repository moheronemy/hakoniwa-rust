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

/// 失敗したセットをやり直すまでの間隔 (秒)。失敗が続くと倍にし、[`RETRY_MAX_SECS`] まで延ばす
const RETRY_FIRST_SECS: i64 = 60;
const RETRY_MAX_SECS: i64 = 3600;

/// セットごとのターン処理の様子
#[derive(Debug, Default, Clone)]
struct SetTurnState {
    /// いまターン処理をしている (重ねて始めない)
    running: bool,
    /// 続けて失敗した回数
    failures: u32,
    /// この時刻 (Unix 秒) まではやり直さない
    retry_at: i64,
}

/// 全セットのターンを進める 1 本の定期処理 (docs/MULTISET.md の手順 2)。
///
/// - `tick_secs` ごとに全セットの「ターンの時刻が来たか」を見て、来ているセットのターン処理を始める
/// - 同時に回すターン処理は `workers` 個まで (ターンが重なっても画面の処理を押し出さない)
/// - 処理中のセットは重ねて始めない
/// - あるセットのターン処理が失敗しても (別のスレッドでの異常終了も含む)、ほかのセットは続ける。
///   失敗したセットは 1 分から倍々に、最大 1 時間空けてやり直す
pub struct Scheduler {
    /// (ログに出す名前, セット)
    sets: Vec<(String, Arc<AppState>)>,
    permits: Arc<tokio::sync::Semaphore>,
    state: std::sync::Mutex<Vec<SetTurnState>>,
    in_flight: std::sync::atomic::AtomicUsize,
    /// 同時に回ったターン処理の数のいちばん多いとき (テストと記録用)
    peak: std::sync::atomic::AtomicUsize,
}

impl Scheduler {
    pub fn new(sets: Vec<(String, Arc<AppState>)>, workers: usize) -> Arc<Self> {
        let n = sets.len();
        Arc::new(Self {
            sets,
            permits: Arc::new(tokio::sync::Semaphore::new(workers.max(1))),
            state: std::sync::Mutex::new(vec![SetTurnState::default(); n]),
            in_flight: Default::default(),
            peak: Default::default(),
        })
    }

    #[cfg(test)]
    pub fn peak(&self) -> usize {
        self.peak.load(std::sync::atomic::Ordering::SeqCst)
    }

    /// 1 回分: 時刻が来ているセットのターン処理を始め、その処理を返す (終わりを待たない)
    pub fn round(self: &Arc<Self>, now: i64) -> Vec<tokio::task::JoinHandle<()>> {
        let mut started = Vec::new();
        let mut state = self.state.lock().expect("scheduler lock poisoned");
        for (i, (_, app)) in self.sets.iter().enumerate() {
            let st = &mut state[i];
            if st.running || now < st.retry_at {
                continue;
            }
            if !app.game.snapshot().world.turn_due(now, &app.config) {
                continue;
            }
            st.running = true;
            let me = self.clone();
            started.push(tokio::spawn(async move { me.run_set(i, now).await }));
        }
        started
    }

    async fn run_set(self: Arc<Self>, i: usize, now: i64) {
        use std::sync::atomic::Ordering::SeqCst;
        let (name, app) = &self.sets[i];
        let result = {
            let _permit = self.permits.acquire().await.expect("semaphore closed");
            let n = self.in_flight.fetch_add(1, SeqCst) + 1;
            self.peak.fetch_max(n, SeqCst);
            // ターン処理は別のタスクで動かし、異常終了してもここで受け止める
            let task = tokio::spawn({
                let app = app.clone();
                async move { run_due_turns(&app, now).await }
            });
            let r = match task.await {
                Ok(r) => r,
                Err(e) => Err(anyhow::anyhow!("ターン処理が異常終了しました: {e}")),
            };
            self.in_flight.fetch_sub(1, SeqCst);
            r
        };
        let mut state = self.state.lock().expect("scheduler lock poisoned");
        let st = &mut state[i];
        st.running = false;
        match result {
            Ok(turns) => {
                st.failures = 0;
                st.retry_at = 0;
                if !turns.is_empty() {
                    tracing::info!(set = %name, ?turns, "ターンを処理しました");
                }
            }
            Err(e) => {
                st.failures += 1;
                let wait = (RETRY_FIRST_SECS << (st.failures - 1).min(6)).min(RETRY_MAX_SECS);
                st.retry_at = now + wait;
                tracing::error!(
                    set = %name,
                    failures = st.failures,
                    retry_in_secs = wait,
                    "ターン処理に失敗しました: {e:#}"
                );
            }
        }
    }

    /// `every` ごとに [`Scheduler::round`] を回す
    pub async fn run(self: Arc<Self>, every: Duration) {
        let mut interval = tokio::time::interval(every);
        interval.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Delay);
        loop {
            interval.tick().await;
            self.round(now_unix());
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

    /// 時刻が来たセットをすべて進め、同時に回すのは workers 個まで。同じ時刻でもう一度回しても重ねない
    #[tokio::test(flavor = "multi_thread", worker_threads = 4)]
    async fn scheduler_runs_due_sets_within_the_worker_limit() {
        for workers in [1, 2] {
            let apps: Vec<_> = (0..5).map(|_| test_app()).collect();
            let sets: Vec<_> = apps
                .iter()
                .enumerate()
                .map(|(i, (a, _))| (format!("s{i}"), a.clone()))
                .collect();
            let start = apps[0].0.game.snapshot().world.last_time;
            let now = start + apps[0].0.config.unit_time + 1;
            let scheduler = Scheduler::new(sets, workers);
            let tasks = scheduler.round(now);
            assert_eq!(tasks.len(), 5);
            for t in tasks {
                t.await.unwrap();
            }
            for (a, _) in &apps {
                assert_eq!(a.game.snapshot().world.turn, 2);
            }
            assert!(scheduler.peak() >= 1 && scheduler.peak() <= workers);
            // 進んだので、同じ時刻ではもう何も始めない
            assert!(scheduler.round(now).is_empty());
        }
    }

    /// あるセットの保存が壊れても、ほかのセットは進む。壊れたセットは状態が変わらず、間隔を空けてやり直す
    #[tokio::test]
    async fn a_failing_set_does_not_stop_the_others() {
        let (good, _d1) = test_app();
        let (bad, _d2) = test_app();
        // データディレクトリをファイルに置き換えて、保存できなくする
        std::fs::remove_dir_all(&bad.data_dir).unwrap();
        std::fs::write(&bad.data_dir, "not a directory").unwrap();
        let start = good.game.snapshot().world.last_time;
        let now = start + good.config.unit_time + 1;
        let scheduler = Scheduler::new(
            vec![("good".into(), good.clone()), ("bad".into(), bad.clone())],
            2,
        );
        for t in scheduler.round(now) {
            t.await.unwrap();
        }
        assert_eq!(good.game.snapshot().world.turn, 2);
        assert_eq!(bad.game.snapshot().world.turn, 1);
        // 失敗したセットは 1 分経つまでやり直さない
        assert!(scheduler.round(now + 30).is_empty());
        let retry = scheduler.round(now + RETRY_FIRST_SECS);
        assert_eq!(retry.len(), 1);
        for t in retry {
            t.await.unwrap();
        }
        assert_eq!(bad.game.snapshot().world.turn, 1);
        // 2 回目の失敗のあとは 2 分空ける
        assert!(
            scheduler
                .round(now + RETRY_FIRST_SECS + RETRY_FIRST_SECS + 1)
                .is_empty()
        );
        assert_eq!(
            scheduler
                .round(now + RETRY_FIRST_SECS + 2 * RETRY_FIRST_SECS)
                .len(),
            1
        );
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
