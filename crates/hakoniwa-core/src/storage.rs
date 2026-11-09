//! 移植版のセーブデータ (JSON) の読み書き。
//!
//! Perl 版と同じく「一時ファイルに書いてから rename」で置き換えるので、
//! 書き込み途中で止まっても前回のデータが残る。

use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::{Path, PathBuf};

use thiserror::Error;

use crate::model::{FORMAT_VERSION, GameState};

#[derive(Debug, Error)]
pub enum StorageError {
    #[error("{path}: {source}")]
    Io {
        path: PathBuf,
        source: std::io::Error,
    },
    #[error("{path}: JSON として読めません: {source}")]
    Json {
        path: PathBuf,
        source: serde_json::Error,
    },
    #[error("{path}: 未対応のデータ形式バージョン {found} (対応しているのは {FORMAT_VERSION})")]
    Version { path: PathBuf, found: u32 },
}

/// 状態を読み込む。ファイルが無ければ `Ok(None)`
pub fn load(path: &Path) -> Result<Option<GameState>, StorageError> {
    let text = match fs::read_to_string(path) {
        Ok(t) => t,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(source) => {
            return Err(StorageError::Io {
                path: path.into(),
                source,
            });
        }
    };
    let state: GameState = serde_json::from_str(&text).map_err(|source| StorageError::Json {
        path: path.into(),
        source,
    })?;
    if state.format_version != FORMAT_VERSION {
        return Err(StorageError::Version {
            path: path.into(),
            found: state.format_version,
        });
    }
    Ok(Some(state))
}

/// 状態を書き込む (一時ファイル + rename)
pub fn save(path: &Path, state: &GameState) -> Result<(), StorageError> {
    let io = |source| StorageError::Io {
        path: path.into(),
        source,
    };
    if let Some(dir) = path.parent().filter(|d| !d.as_os_str().is_empty()) {
        fs::create_dir_all(dir).map_err(io)?;
    }
    let mut tmp = path.as_os_str().to_owned();
    tmp.push(".tmp");
    let tmp = PathBuf::from(tmp);

    let file = File::create(&tmp).map_err(io)?;
    let mut w = BufWriter::new(file);
    serde_json::to_writer_pretty(&mut w, state).map_err(|source| StorageError::Json {
        path: tmp.clone(),
        source,
    })?;
    w.write_all(b"\n").map_err(io)?;
    let file = w.into_inner().map_err(|e| io(e.into_error()))?;
    file.sync_all().map_err(io)?;
    fs::rename(&tmp, path).map_err(io)?;
    Ok(())
}

/// `n` 番目のバックアップのパス (`state.json` → `state.bak0.json`)
pub fn backup_path(path: &Path, n: usize) -> PathBuf {
    let stem = path.file_stem().unwrap_or_default().to_string_lossy();
    let name = match path.extension() {
        Some(ext) => format!("{stem}.bak{n}.{}", ext.to_string_lossy()),
        None => format!("{stem}.bak{n}"),
    };
    path.with_file_name(name)
}

/// 今の保存データをバックアップに回す (ターン処理の書き込みの前に呼ぶ)。
///
/// Perl 版は `data` を `data.bak0` に名前を変えてから新しいデータを書いていた。
/// 移植版は `state.bak0.json` に複製し、古いものは `bak1`, `bak2`, ... とずらして
/// `keep` 個まで残す。保存データがまだ無ければ何もしない
pub fn rotate_backups(path: &Path, keep: usize) -> Result<(), StorageError> {
    if keep == 0 || !path.exists() {
        return Ok(());
    }
    let io = |p: &Path| {
        let p = p.to_path_buf();
        move |source| StorageError::Io { path: p, source }
    };
    let oldest = backup_path(path, keep - 1);
    if oldest.exists() {
        fs::remove_file(&oldest).map_err(io(&oldest))?;
    }
    for i in (1..keep).rev() {
        let from = backup_path(path, i - 1);
        if from.exists() {
            fs::rename(&from, backup_path(path, i)).map_err(io(&from))?;
        }
    }
    fs::copy(path, backup_path(path, 0)).map_err(io(path))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    #[test]
    fn backups_rotate() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("state.json");
        assert_eq!(backup_path(&path, 1), dir.path().join("state.bak1.json"));
        rotate_backups(&path, 2).unwrap(); // まだ無いので何もしない
        for turn in 1..=3 {
            let mut state = GameState::new_game(0, &GameConfig::default());
            state.world.turn = turn;
            rotate_backups(&path, 2).unwrap();
            save(&path, &state).unwrap();
        }
        let turn = |p: &Path| load(p).unwrap().unwrap().world.turn;
        assert_eq!(turn(&path), 3);
        assert_eq!(turn(&backup_path(&path, 0)), 2);
        assert_eq!(turn(&backup_path(&path, 1)), 1);
        assert!(!backup_path(&path, 2).exists());
    }

    use super::*;
    use crate::config::GameConfig;

    #[test]
    fn round_trip() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("sub/state.json");
        assert!(load(&path).unwrap().is_none());
        let state = GameState::new_game(1_794_250_000, &GameConfig::default());
        save(&path, &state).unwrap();
        assert_eq!(load(&path).unwrap().unwrap(), state);
        assert!(!dir.path().join("sub/state.json.tmp").exists());
    }

    #[test]
    fn rejects_other_versions() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("state.json");
        let mut state = GameState::new_game(0, &GameConfig::default());
        state.format_version = 999;
        save(&path, &state).unwrap();
        assert!(matches!(
            load(&path),
            Err(StorageError::Version { found: 999, .. })
        ));
    }
}
