//! ゲームの状態の置き場所 (docs/SCALING.md の手順 2)。
//!
//! - 読み取りは、その時点の状態のスナップショット (`Arc<GameState>`) を受け取るだけで、待たない。
//!   ターン処理や保存のあいだも、画面は 1 つ前の状態を出し続ける
//! - 書き込み (画面の操作・ターン処理・管理画面) は 1 本の順番待ち (公平な `tokio::sync::Mutex`) に並ぶ。
//!   ターン処理中に来た操作は、ターンが終わってから順に行われる (Perl 版でもターン中の入力はターンのあとに効く)
//! - 書き込む側は今の状態を複製して書き換え、保存できたときだけ新しいスナップショットとして公開する。
//!   地図とターンのログは複製のあいだで共有されるので (`hakoniwa_core::model`)、複製は安い
//! - 重い処理 (ターン処理・保存) は `spawn_blocking` で行い、非同期の処理を止めない

use std::path::PathBuf;
use std::sync::{Arc, RwLock};

use hakoniwa_core::model::GameState;
use hakoniwa_core::storage;
use rand::rngs::StdRng;
use tokio::sync::{Mutex, MutexGuard};

pub struct Store {
    /// 公開中のスナップショット。ロックはポインタを取り出す・差し替えるあいだだけ持つ
    current: RwLock<Arc<GameState>>,
    /// 書き込みの順番待ち。乱数は書き込む側だけが使うので、ここに持つ
    writer: Mutex<StdRng>,
}

impl Store {
    pub fn new(game: GameState, rng: StdRng) -> Self {
        Self {
            current: RwLock::new(Arc::new(game)),
            writer: Mutex::new(rng),
        }
    }

    /// 今の状態のスナップショット (待たない)
    pub fn snapshot(&self) -> Arc<GameState> {
        self.current.read().expect("snapshot lock poisoned").clone()
    }

    /// [`Self::snapshot`] と同じ。以前の `RwLock` と同じ書き方で読めるように残してある
    pub async fn read(&self) -> Arc<GameState> {
        self.snapshot()
    }

    /// 書き込みの順番を待つ。返した [`Writer`] を持っているあいだ、ほかの書き込みは待つ
    pub async fn write(&self) -> Writer<'_> {
        Writer {
            store: self,
            rng: self.writer.lock().await,
        }
    }
}

/// 書き込みの権利。今の状態の取り出し・乱数・新しい状態の公開ができる
pub struct Writer<'a> {
    store: &'a Store,
    rng: MutexGuard<'a, StdRng>,
}

impl Writer<'_> {
    /// 今の状態 (書き込みの順番を持っているので、公開するまで変わらない)
    pub fn current(&self) -> Arc<GameState> {
        self.store.snapshot()
    }

    pub fn rng(&mut self) -> &mut StdRng {
        &mut self.rng
    }

    /// 新しい状態を公開する (保存が済んでから呼ぶ)
    pub fn publish(&mut self, next: Arc<GameState>) {
        *self.store.current.write().expect("snapshot lock poisoned") = next;
    }
}

/// `state` を `path` に保存する。`rotate_backups` が `Some(n)` なら、先にバックアップを n 個までずらす。
/// 保存は別のスレッドで行う
pub async fn save(
    path: PathBuf,
    state: Arc<GameState>,
    rotate_backups: Option<usize>,
) -> anyhow::Result<()> {
    tokio::task::spawn_blocking(move || -> anyhow::Result<()> {
        if let Some(keep) = rotate_backups {
            storage::rotate_backups(&path, keep)?;
        }
        storage::save(&path, &state)?;
        Ok(())
    })
    .await?
}

#[cfg(test)]
mod tests {
    use super::*;
    use hakoniwa_core::GameConfig;
    use rand::SeedableRng;

    #[tokio::test]
    async fn readers_keep_their_snapshot_while_a_writer_publishes() {
        let store = Store::new(
            GameState::new_game(1_000_000, &GameConfig::default()),
            StdRng::seed_from_u64(0),
        );
        let before = store.snapshot();
        let mut w = store.write().await;
        // 書き込み中でも読める
        assert_eq!(store.read().await.world.turn, 1);
        let mut next = (*w.current()).clone();
        next.world.turn = 2;
        w.publish(Arc::new(next));
        drop(w);
        assert_eq!(before.world.turn, 1);
        assert_eq!(store.snapshot().world.turn, 2);
    }

    #[tokio::test]
    async fn writers_wait_in_order() {
        let store = Arc::new(Store::new(
            GameState::new_game(1_000_000, &GameConfig::default()),
            StdRng::seed_from_u64(0),
        ));
        let first = store.write().await;
        let order = Arc::new(std::sync::Mutex::new(Vec::new()));
        let mut tasks = Vec::new();
        for i in 0..5 {
            let (store, order) = (store.clone(), order.clone());
            tasks.push(tokio::spawn(async move {
                let _w = store.write().await;
                order.lock().unwrap().push(i);
            }));
            // 並ぶ順を決めるため、1 つずつ待ち行列に入れる
            tokio::task::yield_now().await;
        }
        assert!(order.lock().unwrap().is_empty());
        drop(first);
        for t in tasks {
            t.await.unwrap();
        }
        assert_eq!(*order.lock().unwrap(), [0, 1, 2, 3, 4]);
    }
}
