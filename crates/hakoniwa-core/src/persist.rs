//! 大規模向けのセーブデータ (docs/SCALING.md の手順 3)。
//!
//! JSON 1 ファイル ([`crate::storage`]) は、1000 島・128×128 では 1 回 1 GB を超え、操作のたびに
//! 書き直せない。そこでデータディレクトリに次のものを置く。
//!
//! ```text
//! snapshot.bin          状態のスナップショット (ターンのログを除く)。ターンのたびに書き直す
//! journal-<世代>.bin    そのスナップショットのあとの画面の操作の差分 (追記)
//! logs/<番号>.bin       1 ターン分のログ ([`TurnLog`])。一度書いたら変えない
//! backup<N>/            バックアップ (snapshot.bin と logs/ の写し。ログはハードリンク)
//! ```
//!
//! - スナップショットは、見出し (世代・ターン・最終更新時刻・島の数・ログの番号) と、
//!   状態を bincode にして zstd で圧縮したもの。書くときは一時ファイルに書いて rename する
//! - 画面の操作は、前の状態との差分 ([`Delta`]: 全体の値と、変わった島。地図は変わったときだけ) を
//!   1 件ずつ追記し、そのつど fsync する。差分は「変わったあとのデータ」なので、読み直すときに
//!   ゲームのルールを動かさない (版が変わっても同じ状態に戻る)
//! - 読み込むときは、スナップショットに同じ世代の差分を順に当てる。最後の 1 件が書きかけなら捨てる
//! - スナップショットを書き直したら世代を 1 つ進め、古い差分と、どこからも指されないログを消す
//!
//! 状態と差分は項目名付きの MessagePack で書く (形式の版 2)。データモデルに項目を足しても、
//! 足す前のデータは無い項目を既定値にして読める (消した項目は読み飛ばす)。項目の意味を変えるときは
//! データモデルの版 ([`crate::model::FORMAT_VERSION`]) を上げ、[`crate::model::upgrade`] に直す手順を足す。
//! 形式の版 1 (bincode) のデータも読め、開いたときに版 2 のスナップショットに書き直す。
//! ターンのログ (`logs/`) は bincode のまま ([`TurnLog`] の中身はほとんど変わらないので)。

use std::collections::HashMap;
use std::fs::{self, File, OpenOptions};
use std::io::{BufReader, BufWriter, Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};
use std::sync::Arc;

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::model::{GameState, Island, IslandMap, Logs, World};
use crate::turn_log::TurnLog;

/// スナップショットのファイルの先頭
const MAGIC: &[u8; 8] = b"HAKOSNAP";
/// 形式の版 (いま書くもの)。2: 項目名付きの MessagePack
pub const FORMAT: u32 = 2;
/// 形式の版 1: bincode (読むだけ)
const FORMAT_BINCODE: u32 = 1;

/// 書く: 項目名付きの MessagePack
fn encode<T: Serialize>(v: &T) -> std::result::Result<Vec<u8>, String> {
    rmp_serde::to_vec_named(v).map_err(|e| e.to_string())
}

/// 読む: 形式の版で読み方を変える
fn decode<T: serde::de::DeserializeOwned>(
    bytes: &[u8],
    format: u32,
) -> std::result::Result<T, String> {
    if format == FORMAT_BINCODE {
        bincode::deserialize(bytes).map_err(|e| e.to_string())
    } else {
        rmp_serde::from_slice(bytes).map_err(|e| e.to_string())
    }
}
/// スナップショット・差分の圧縮の強さ (zstd)
const LEVEL: i32 = 1;

const SNAPSHOT: &str = "snapshot.bin";
const LOGS: &str = "logs";

#[derive(Debug, Error)]
pub enum PersistError {
    #[error("{path}: {source}")]
    Io {
        path: PathBuf,
        source: std::io::Error,
    },
    #[error("{path}: 形が違います: {message}")]
    Format { path: PathBuf, message: String },
    #[error("{path}: 未対応の形式の版 {found} (対応しているのは {FORMAT})")]
    Version { path: PathBuf, found: u32 },
}

type Result<T> = std::result::Result<T, PersistError>;

/// ディスクにあるログと、そのファイルの番号
type LogsOnDisk = Vec<(Arc<TurnLog>, u64)>;

fn io(path: &Path) -> impl FnOnce(std::io::Error) -> PersistError + '_ {
    move |source| PersistError::Io {
        path: path.to_path_buf(),
        source,
    }
}

fn format_err(path: &Path, message: impl ToString) -> PersistError {
    PersistError::Format {
        path: path.to_path_buf(),
        message: message.to_string(),
    }
}

/// スナップショットの見出し (状態を展開しなくても読める)
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(default)]
pub struct Header {
    /// 世代 (スナップショットを書き直すたびに 1 つ進む。差分のファイルの名前に使う)
    pub generation: u64,
    pub turn: i64,
    pub last_time: i64,
    pub islands: usize,
    /// `logs.turns` に対応するログのファイルの番号 (新しい順)
    pub log_ids: Vec<u64>,
    /// 次に使うログの番号
    pub next_log_id: u64,
}

/// 画面の操作 1 件の差分 (変わったあとのデータ)
#[derive(Debug, Serialize, Deserialize)]
pub struct Delta {
    /// 島の一覧以外の全体の値
    world: World,
    /// 島の並び (ID)
    order: Vec<i64>,
    /// 変わった島・増えた島。地図は変わったときだけ入れる (`map` が `None` なら前のまま)
    islands: Vec<(Island, Option<IslandMap>)>,
    /// ターンのログ以外のログ (発見・Hakoniwa Cup・ハコオクの記録)
    logs: Logs,
}

impl Delta {
    /// `prev` から `next` への差分。ターンのログが変わっていたら `None` (スナップショットを書く)
    pub fn between(prev: &GameState, next: &GameState) -> Option<Self> {
        let same_turn_logs = prev.logs.turns.len() == next.logs.turns.len()
            && prev
                .logs
                .turns
                .iter()
                .zip(&next.logs.turns)
                .all(|(a, b)| Arc::ptr_eq(a, b));
        if !same_turn_logs || prev.format_version != next.format_version {
            return None;
        }
        let before: HashMap<i64, &Island> = prev.world.islands.iter().map(|i| (i.id, i)).collect();
        let mut islands = Vec::new();
        for island in &next.world.islands {
            match before.get(&island.id) {
                // 地図は `Arc` を共有していれば同じとみなして速く比べる (Eq の型なので内容でも同じ)
                Some(old) if *old == island => {}
                Some(old) if Arc::ptr_eq(&old.map.cells, &island.map.cells) => {
                    islands.push((without_map(island), None));
                }
                _ => islands.push((without_map(island), Some(island.map.clone()))),
            }
        }
        Some(Self {
            world: World {
                islands: Vec::new(),
                ..next.world.clone()
            },
            order: next.world.islands.iter().map(|i| i.id).collect(),
            islands,
            logs: Logs {
                turns: Vec::new(),
                ..next.logs.clone()
            },
        })
    }

    /// `state` に当てる
    fn apply(self, state: &mut GameState) -> std::result::Result<(), String> {
        let mut before: HashMap<i64, Island> = std::mem::take(&mut state.world.islands)
            .into_iter()
            .map(|i| (i.id, i))
            .collect();
        let mut changed: HashMap<i64, (Island, Option<IslandMap>)> = self
            .islands
            .into_iter()
            .map(|(i, m)| (i.id, (i, m)))
            .collect();
        let mut islands = Vec::with_capacity(self.order.len());
        for id in self.order {
            let old = before.remove(&id);
            let island = match (changed.remove(&id), old) {
                (Some((mut island, Some(map))), _) => {
                    island.map = map;
                    island
                }
                (Some((mut island, None)), Some(old)) => {
                    island.map = old.map;
                    island
                }
                (None, Some(old)) => old,
                (_, None) => return Err(format!("島 {id} の地図がありません")),
            };
            islands.push(island);
        }
        let turns = std::mem::take(&mut state.logs.turns);
        state.world = World {
            islands,
            ..self.world
        };
        state.logs = Logs { turns, ..self.logs };
        Ok(())
    }
}

/// 地図を空にした島の写し (地図は別に持つ)
fn without_map(island: &Island) -> Island {
    let mut copy = island.clone();
    copy.map = IslandMap {
        size: island.map.size,
        cells: Arc::new(Vec::new()),
    };
    copy
}

/// データディレクトリ
pub struct DataDir {
    dir: PathBuf,
    header: Header,
    /// ディスクにあるログと番号 (`Arc` が同じなら同じログ)
    logs_on_disk: LogsOnDisk,
    /// 今の世代の差分のファイル
    journal: File,
    /// 開いたときに前の形式の版から書き直したなら、その版
    migrated_from: Option<u32>,
}

impl DataDir {
    /// データディレクトリを読み込む。スナップショットが無ければ `None`
    pub fn open(dir: &Path) -> Result<Option<(Self, GameState)>> {
        let path = dir.join(SNAPSHOT);
        if !path.exists() {
            return Ok(None);
        }
        let (header, mut state, format) = read_snapshot(dir)?;
        let logs_on_disk = state
            .logs
            .turns
            .iter()
            .cloned()
            .zip(header.log_ids.iter().copied())
            .collect();
        let journal_path = journal_path(dir, header.generation);
        replay(&journal_path, &mut state, format)?;
        let journal = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&journal_path)
            .map_err(io(&journal_path))?;
        let mut me = Self {
            dir: dir.to_path_buf(),
            header,
            logs_on_disk,
            journal,
            migrated_from: None,
        };
        if format != FORMAT {
            // 前の形式の版: いまの形式でスナップショットを書き直す (世代が進み、前の形式の差分は消える。
            // 同じ差分のファイルに 2 つの形式が混ざらないように)
            me.snapshot(&state)?;
            me.migrated_from = Some(format);
        }
        me.remove_stale()?;
        Ok(Some((me, state)))
    }

    /// 新しいデータディレクトリに `state` を書く (前のデータがあれば上書きする)
    pub fn create(dir: &Path, state: &GameState) -> Result<Self> {
        fs::create_dir_all(dir.join(LOGS)).map_err(io(dir))?;
        // 前のデータがあれば、その世代とログの番号の続きから (書き終わるまで前のデータが読めるように)
        let (generation, next_log_id) = match read_header(&dir.join(SNAPSHOT)) {
            Ok(h) => (h.generation + 1, h.next_log_id),
            Err(_) => (1, 1),
        };
        let (header, logs_on_disk) =
            write_snapshot(dir, state, generation, next_log_id, &[], None)?;
        let journal = new_journal(dir, generation)?;
        let me = Self {
            dir: dir.to_path_buf(),
            header,
            logs_on_disk,
            journal,
            migrated_from: None,
        };
        me.remove_stale()?;
        Ok(me)
    }

    pub fn header(&self) -> &Header {
        &self.header
    }

    /// 開いたときに前の形式の版から書き直したなら、その版
    pub fn migrated_from(&self) -> Option<u32> {
        self.migrated_from
    }

    /// 画面の操作を記録する (`prev` から `next` への差分を追記する)。
    /// ターンのログが変わっていればスナップショットを書き直す
    pub fn record(&mut self, prev: &GameState, next: &GameState) -> Result<()> {
        let Some(delta) = Delta::between(prev, next) else {
            return self.snapshot(next);
        };
        let path = journal_path(&self.dir, self.header.generation);
        let raw = encode(&delta).map_err(|e| format_err(&path, e))?;
        let packed = compress(&raw).map_err(io(&path))?;
        let mut record = Vec::with_capacity(packed.len() + 4);
        record.extend_from_slice(&(packed.len() as u32).to_le_bytes());
        record.extend_from_slice(&packed);
        self.journal.write_all(&record).map_err(io(&path))?;
        self.journal.sync_data().map_err(io(&path))?;
        Ok(())
    }

    /// `state` のスナップショットを書き、世代を進める (ターンのあとなど)
    pub fn snapshot(&mut self, state: &GameState) -> Result<()> {
        let generation = self.header.generation + 1;
        let (header, logs_on_disk) = write_snapshot(
            &self.dir,
            state,
            generation,
            self.header.next_log_id,
            &self.logs_on_disk,
            None,
        )?;
        self.journal = new_journal(&self.dir, generation)?;
        self.header = header;
        self.logs_on_disk = logs_on_disk;
        self.remove_stale()
    }

    /// `state` をバックアップ 0 に書き、前のバックアップを 1, 2, ... とずらして `keep` 個まで残す。
    /// `state` のログはディスクにあるものならハードリンクする
    pub fn backup(&self, state: &GameState, keep: usize) -> Result<()> {
        if keep == 0 {
            return Ok(());
        }
        let oldest = backup_dir(&self.dir, keep - 1);
        if oldest.exists() {
            fs::remove_dir_all(&oldest).map_err(io(&oldest))?;
        }
        for i in (1..keep).rev() {
            let from = backup_dir(&self.dir, i - 1);
            if from.exists() {
                let to = backup_dir(&self.dir, i);
                fs::rename(&from, &to).map_err(io(&from))?;
            }
        }
        let to = backup_dir(&self.dir, 0);
        let tmp = self.dir.join("backup.tmp");
        if tmp.exists() {
            fs::remove_dir_all(&tmp).map_err(io(&tmp))?;
        }
        fs::create_dir_all(tmp.join(LOGS)).map_err(io(&tmp))?;
        write_snapshot(
            &tmp,
            state,
            self.header.generation,
            self.header.next_log_id,
            &self.logs_on_disk,
            Some(&self.dir.join(LOGS)),
        )?;
        fs::rename(&tmp, &to).map_err(io(&tmp))?;
        Ok(())
    }

    /// 前の世代の差分と、どこからも指されないログのファイルを消す
    fn remove_stale(&self) -> Result<()> {
        let current = journal_path(&self.dir, self.header.generation);
        for entry in fs::read_dir(&self.dir).map_err(io(&self.dir))?.flatten() {
            let path = entry.path();
            let name = entry.file_name();
            let name = name.to_string_lossy();
            if name.starts_with("journal-") && name.ends_with(".bin") && path != current {
                fs::remove_file(&path).map_err(io(&path))?;
            }
        }
        let logs = self.dir.join(LOGS);
        for entry in fs::read_dir(&logs).map_err(io(&logs))?.flatten() {
            let path = entry.path();
            let id = path
                .file_stem()
                .and_then(|s| s.to_str())
                .and_then(|s| s.parse::<u64>().ok());
            if id.is_none_or(|id| !self.header.log_ids.contains(&id)) {
                fs::remove_file(&path).map_err(io(&path))?;
            }
        }
        Ok(())
    }
}

/// `n` 番目のバックアップのディレクトリ
pub fn backup_dir(dir: &Path, n: usize) -> PathBuf {
    dir.join(format!("backup{n}"))
}

/// バックアップ (やデータディレクトリ) の見出しだけを読む。無ければ `None`
pub fn read_backup_header(dir: &Path) -> Result<Option<Header>> {
    let path = dir.join(SNAPSHOT);
    if !path.exists() {
        return Ok(None);
    }
    read_header(&path).map(Some)
}

/// バックアップ (やデータディレクトリ) のスナップショットを読む (差分は当てない)
pub fn read_backup(dir: &Path) -> Result<GameState> {
    read_snapshot(dir).map(|(_, state, _)| state)
}

fn journal_path(dir: &Path, generation: u64) -> PathBuf {
    dir.join(format!("journal-{generation}.bin"))
}

fn new_journal(dir: &Path, generation: u64) -> Result<File> {
    let path = journal_path(dir, generation);
    let file = File::create(&path).map_err(io(&path))?;
    sync_dir(dir)?;
    Ok(file)
}

fn compress(raw: &[u8]) -> std::io::Result<Vec<u8>> {
    let mut enc = zstd::stream::Encoder::new(Vec::new(), LEVEL)?;
    // 壊れた記録を見分けられるように、展開した内容の検査値を付ける
    enc.include_checksum(true)?;
    enc.write_all(raw)?;
    enc.finish()
}

fn decompress(packed: &[u8]) -> std::io::Result<Vec<u8>> {
    let mut out = Vec::new();
    zstd::stream::Decoder::new(packed)?.read_to_end(&mut out)?;
    Ok(out)
}

fn sync_dir(dir: &Path) -> Result<()> {
    // ディレクトリの fsync (rename を確かにする)。できない環境では何もしない
    if let Ok(d) = File::open(dir) {
        let _ = d.sync_all();
    }
    Ok(())
}

/// `dir` に `state` のスナップショットを書く。
/// ログは `on_disk` にある (`Arc` が同じ) ものはそのまま使い、無いものは新しい番号で書く。
/// `link_from` があれば、ディスクにあるログはそこからハードリンクする (バックアップ用)
fn write_snapshot(
    dir: &Path,
    state: &GameState,
    generation: u64,
    mut next_log_id: u64,
    on_disk: &[(Arc<TurnLog>, u64)],
    link_from: Option<&Path>,
) -> Result<(Header, LogsOnDisk)> {
    let logs_dir = dir.join(LOGS);
    fs::create_dir_all(&logs_dir).map_err(io(&logs_dir))?;
    let mut logs = Vec::with_capacity(state.logs.turns.len());
    for log in &state.logs.turns {
        let known = on_disk.iter().find(|(l, _)| Arc::ptr_eq(l, log));
        let id = match known {
            Some((_, id)) => {
                if let Some(src) = link_from {
                    let from = src.join(format!("{id}.bin"));
                    let to = logs_dir.join(format!("{id}.bin"));
                    if fs::hard_link(&from, &to).is_err() {
                        fs::copy(&from, &to).map_err(io(&from))?;
                    }
                }
                *id
            }
            None => {
                let id = next_log_id;
                next_log_id += 1;
                let path = logs_dir.join(format!("{id}.bin"));
                let tmp = logs_dir.join(format!("{id}.tmp"));
                let bytes = bincode::serialize(&**log).map_err(|e| format_err(&path, e))?;
                let mut f = File::create(&tmp).map_err(io(&tmp))?;
                f.write_all(&bytes).map_err(io(&tmp))?;
                f.sync_all().map_err(io(&tmp))?;
                fs::rename(&tmp, &path).map_err(io(&path))?;
                id
            }
        };
        logs.push((log.clone(), id));
    }
    sync_dir(&logs_dir)?;

    let header = Header {
        generation,
        turn: state.world.turn,
        last_time: state.world.last_time,
        islands: state.world.islands.len(),
        log_ids: logs.iter().map(|(_, id)| *id).collect(),
        next_log_id,
    };
    let path = dir.join(SNAPSHOT);
    let tmp = dir.join("snapshot.tmp");
    // ターンのログは別のファイルにあるので、状態からは外す (共有しているので写さない)
    let body = GameState {
        format_version: state.format_version,
        world: state.world.clone(),
        logs: Logs {
            turns: Vec::new(),
            ..state.logs.clone()
        },
    };
    let raw = encode(&body).map_err(|e| format_err(&path, e))?;
    let packed = compress(&raw).map_err(io(&path))?;
    let head = encode(&header).map_err(|e| format_err(&path, e))?;
    let mut w = BufWriter::new(File::create(&tmp).map_err(io(&tmp))?);
    w.write_all(MAGIC).map_err(io(&tmp))?;
    w.write_all(&FORMAT.to_le_bytes()).map_err(io(&tmp))?;
    w.write_all(&(head.len() as u32).to_le_bytes())
        .map_err(io(&tmp))?;
    w.write_all(&head).map_err(io(&tmp))?;
    w.write_all(&packed).map_err(io(&tmp))?;
    let f = w.into_inner().map_err(|e| io(&tmp)(e.into_error()))?;
    f.sync_all().map_err(io(&tmp))?;
    fs::rename(&tmp, &path).map_err(io(&path))?;
    sync_dir(dir)?;
    Ok((header, logs))
}

/// 見出しと形式の版を読む。読めない版 (新しすぎる・0) ならエラー
fn read_header_from(r: &mut impl Read, path: &Path) -> Result<(Header, u32)> {
    let mut magic = [0u8; 8];
    r.read_exact(&mut magic).map_err(io(path))?;
    if &magic != MAGIC {
        return Err(format_err(path, "スナップショットではありません"));
    }
    let mut n = [0u8; 4];
    r.read_exact(&mut n).map_err(io(path))?;
    let found = u32::from_le_bytes(n);
    if found == 0 || found > FORMAT {
        return Err(PersistError::Version {
            path: path.to_path_buf(),
            found,
        });
    }
    r.read_exact(&mut n).map_err(io(path))?;
    let mut head = vec![0u8; u32::from_le_bytes(n) as usize];
    r.read_exact(&mut head).map_err(io(path))?;
    let header = decode(&head, found).map_err(|e| format_err(path, e))?;
    Ok((header, found))
}

fn read_header(path: &Path) -> Result<Header> {
    let mut r = BufReader::new(File::open(path).map_err(io(path))?);
    read_header_from(&mut r, path).map(|(h, _)| h)
}

/// スナップショットを読む (見出し・状態・形式の版)。状態はいまのデータモデルの版にそろえる
fn read_snapshot(dir: &Path) -> Result<(Header, GameState, u32)> {
    let path = dir.join(SNAPSHOT);
    let mut r = BufReader::new(File::open(&path).map_err(io(&path))?);
    let (header, format) = read_header_from(&mut r, &path)?;
    let mut packed = Vec::new();
    r.read_to_end(&mut packed).map_err(io(&path))?;
    let raw = decompress(&packed).map_err(io(&path))?;
    let mut state: GameState = decode(&raw, format).map_err(|e| format_err(&path, e))?;
    crate::model::upgrade(&mut state).map_err(|e| format_err(&path, e))?;
    for id in &header.log_ids {
        let p = dir.join(LOGS).join(format!("{id}.bin"));
        let bytes = fs::read(&p).map_err(io(&p))?;
        let log: TurnLog = bincode::deserialize(&bytes).map_err(|e| format_err(&p, e))?;
        state.logs.turns.push(Arc::new(log));
    }
    Ok((header, state, format))
}

/// 差分を順に当てる。最後の 1 件が書きかけ (途中で止まった) なら、そこで切り詰める
fn replay(path: &Path, state: &mut GameState, format: u32) -> Result<usize> {
    let mut file = match OpenOptions::new().read(true).write(true).open(path) {
        Ok(f) => f,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(0),
        Err(e) => return Err(io(path)(e)),
    };
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes).map_err(io(path))?;
    let mut pos = 0;
    let mut count = 0;
    while pos < bytes.len() {
        let record = bytes
            .get(pos..pos + 4)
            .map(|n| u32::from_le_bytes(n.try_into().expect("4 bytes")) as usize)
            .and_then(|len| bytes.get(pos + 4..pos + 4 + len));
        let Some(record) = record else {
            break; // 書きかけ
        };
        let delta: Delta = match decompress(record)
            .ok()
            .and_then(|raw| decode(&raw, format).ok())
        {
            Some(d) => d,
            None if pos + 4 + record.len() == bytes.len() => break, // 最後の 1 件が壊れている
            None => {
                return Err(format_err(
                    path,
                    format!("{count} 件目の差分が壊れています"),
                ));
            }
        };
        delta.apply(state).map_err(|m| format_err(path, m))?;
        pos += 4 + record.len();
        count += 1;
    }
    if pos < bytes.len() {
        file.set_len(pos as u64).map_err(io(path))?;
        file.seek(SeekFrom::End(0)).map_err(io(path))?;
        file.sync_all().map_err(io(path))?;
    }
    Ok(count)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::GameConfig;
    use crate::legacy::{self, ImportOptions};
    use crate::turn::run_turn;
    use rand::SeedableRng;
    use rand::rngs::StdRng;

    fn legacy_state() -> GameState {
        let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/legacy-turn3");
        legacy::import_dir(
            &dir,
            &ImportOptions::default(),
            &mut StdRng::seed_from_u64(0),
        )
        .unwrap()
        .state
    }

    /// JSON で比べる (ログは行の並びになる。`scratch` は保存しない)
    fn json(state: &GameState) -> serde_json::Value {
        serde_json::to_value(state).unwrap()
    }

    #[test]
    fn snapshot_journal_and_turns_read_back() {
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path();
        let config = GameConfig::default();
        let mut rng = StdRng::seed_from_u64(1);
        let mut state = legacy_state();
        let mut data = DataDir::create(dir, &state).unwrap();

        // 画面の操作: 地図を変えない変更、地図を変える変更、島の削除
        let mut next = state.clone();
        next.world.islands[0].comment = "こんにちは".into();
        next.logs.history.push(crate::model::TurnMessage {
            turn: 3,
            message: "発見".into(),
        });
        data.record(&state, &next).unwrap();
        state = next;
        let mut next = state.clone();
        next.world.islands[1].map.get_mut(3, 4).unwrap().kind = 2;
        data.record(&state, &next).unwrap();
        state = next;
        let mut next = state.clone();
        next.world.islands.remove(2);
        next.world.last_time += 5;
        data.record(&state, &next).unwrap();
        state = next;

        let (_, back) = DataDir::open(dir).unwrap().unwrap();
        assert_eq!(json(&back), json(&state));

        // ターンを進めてスナップショット。差分は新しい世代から
        let mut next = state.clone();
        run_turn(&mut next, &config, &mut rng);
        let (mut data, _) = DataDir::open(dir).unwrap().unwrap();
        data.snapshot(&next).unwrap();
        state = next;
        let mut next = state.clone();
        next.world.islands[0].money += 1;
        data.record(&state, &next).unwrap();
        state = next;
        let (data, back) = DataDir::open(dir).unwrap().unwrap();
        assert_eq!(json(&back), json(&state));
        assert_eq!(data.header().turn, 4);
        // 古い世代の差分は消えている
        let journals = fs::read_dir(dir)
            .unwrap()
            .flatten()
            .filter(|e| e.file_name().to_string_lossy().starts_with("journal-"))
            .count();
        assert_eq!(journals, 1);
    }

    /// ディレクトリを丸ごと複製する (テスト用データを開くと中身を整理するので、写しを開く)
    fn copy_dir(from: &Path, to: &Path) {
        fs::create_dir_all(to).unwrap();
        for e in fs::read_dir(from).unwrap().flatten() {
            let p = e.path();
            if p.is_dir() {
                copy_dir(&p, &to.join(e.file_name()));
            } else {
                fs::copy(&p, to.join(e.file_name())).unwrap();
            }
        }
    }

    /// 形式の版 1 (bincode) で書いたデータディレクトリ (`tests/fixtures/persist-v1`、
    /// スナップショット・ターンのログ・操作の差分 3 件) を読める。今後、形式を変えても読めること
    #[test]
    fn reads_format_1_data() {
        let fixtures = Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures");
        let tmp = tempfile::tempdir().unwrap();
        copy_dir(&fixtures.join("persist-v1"), tmp.path());
        let (_, state) = DataDir::open(tmp.path()).unwrap().unwrap();
        let file = fs::File::open(fixtures.join("persist-v1.expected.json.gz")).unwrap();
        let want: serde_json::Value =
            serde_json::from_reader(flate2::read::GzDecoder::new(file)).unwrap();
        assert_eq!(json(&state), want);
    }

    fn snapshot_format(dir: &Path) -> u32 {
        let bytes = fs::read(dir.join(SNAPSHOT)).unwrap();
        u32::from_le_bytes(bytes[8..12].try_into().unwrap())
    }

    /// 形式の版 1 のデータを開くと版 2 に書き直し、前の形式の差分は消える。開き直しても同じ状態
    #[test]
    fn format_1_data_is_rewritten_as_format_2() {
        let fixtures = Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures");
        let tmp = tempfile::tempdir().unwrap();
        copy_dir(&fixtures.join("persist-v1"), tmp.path());
        assert_eq!(snapshot_format(tmp.path()), 1);
        let (data, state) = DataDir::open(tmp.path()).unwrap().unwrap();
        assert_eq!(data.migrated_from(), Some(1));
        assert_eq!(snapshot_format(tmp.path()), FORMAT);
        assert!(!journal_path(tmp.path(), 2).exists());
        drop(data);
        let (data, again) = DataDir::open(tmp.path()).unwrap().unwrap();
        assert_eq!(data.migrated_from(), None);
        assert_eq!(json(&again), json(&state));
    }

    /// 状態を JSON の値にして `edit` で書き換え、スナップショットに書き戻す
    /// (データモデルに項目が足された・消されたときを作る)
    fn edit_snapshot(dir: &Path, edit: impl FnOnce(&mut serde_json::Value)) {
        let path = dir.join(SNAPSHOT);
        let bytes = fs::read(&path).unwrap();
        let head_len = u32::from_le_bytes(bytes[12..16].try_into().unwrap()) as usize;
        let (prefix, body) = bytes.split_at(16 + head_len);
        let mut value: serde_json::Value =
            rmp_serde::from_slice(&decompress(body).unwrap()).unwrap();
        edit(&mut value);
        let mut out = prefix.to_vec();
        out.extend(compress(&rmp_serde::to_vec_named(&value).unwrap()).unwrap());
        fs::write(&path, out).unwrap();
    }

    /// 無い項目は既定値、知らない項目は読み飛ばす (項目を足した版・消した版のデータ)
    #[test]
    fn missing_and_unknown_fields_are_tolerated() {
        let tmp = tempfile::tempdir().unwrap();
        let state = legacy_state();
        DataDir::create(tmp.path(), &state).unwrap();
        edit_snapshot(tmp.path(), |v| {
            let island = &mut v["world"]["islands"][0];
            island.as_object_mut().unwrap().remove("comment");
            island.as_object_mut().unwrap().remove("owner_stats");
            island["未来の項目"] = serde_json::json!({"a": 1});
            v["world"]["未来の全体の値"] = serde_json::json!(5);
        });
        let (_, back) = DataDir::open(tmp.path()).unwrap().unwrap();
        let mut want = state.clone();
        want.world.islands[0].comment = String::new();
        want.world.islands[0].owner_stats = Default::default();
        assert_eq!(json(&back), json(&want));
    }

    /// 新しすぎる形式の版・データモデルの版のデータは読まない
    #[test]
    fn newer_data_is_refused() {
        let tmp = tempfile::tempdir().unwrap();
        DataDir::create(tmp.path(), &legacy_state()).unwrap();
        let path = tmp.path().join(SNAPSHOT);
        let mut bytes = fs::read(&path).unwrap();
        bytes[8..12].copy_from_slice(&(FORMAT + 1).to_le_bytes());
        fs::write(&path, &bytes).unwrap();
        let e = DataDir::open(tmp.path()).err().unwrap();
        assert!(
            matches!(e, PersistError::Version { found, .. } if found == FORMAT + 1),
            "{e}"
        );

        let tmp = tempfile::tempdir().unwrap();
        DataDir::create(tmp.path(), &legacy_state()).unwrap();
        edit_snapshot(tmp.path(), |v| {
            v["format_version"] = serde_json::json!(crate::model::FORMAT_VERSION + 1);
        });
        let e = DataDir::open(tmp.path()).err().unwrap().to_string();
        assert!(e.contains("新しい"), "{e}");
    }

    #[test]
    fn a_half_written_record_is_dropped() {
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path();
        let state = legacy_state();
        let mut data = DataDir::create(dir, &state).unwrap();
        let mut next = state.clone();
        next.world.islands[0].money = 12345;
        data.record(&state, &next).unwrap();
        let mut later = next.clone();
        later.world.islands[0].money = 99999;
        data.record(&next, &later).unwrap();
        drop(data);

        // 最後の記録の途中で止まった
        let path = journal_path(dir, 1);
        let len = fs::metadata(&path).unwrap().len();
        OpenOptions::new()
            .write(true)
            .open(&path)
            .unwrap()
            .set_len(len - 3)
            .unwrap();
        let (mut data, back) = DataDir::open(dir).unwrap().unwrap();
        assert_eq!(back.world.islands[0].money, 12345);
        // 切り詰めたあとに続けて書ける
        data.record(&back, &later).unwrap();
        let (_, back) = DataDir::open(dir).unwrap().unwrap();
        assert_eq!(back.world.islands[0].money, 99999);
    }

    #[test]
    fn backups_rotate_and_keep_their_logs() {
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path();
        let config = GameConfig::default();
        let mut rng = StdRng::seed_from_u64(1);
        let mut state = legacy_state();
        let mut data = DataDir::create(dir, &state).unwrap();
        let mut turns = Vec::new();
        for _ in 0..3 {
            let mut next = state.clone();
            run_turn(&mut next, &config, &mut rng);
            data.backup(&state, 2).unwrap();
            data.snapshot(&next).unwrap();
            turns.push(state.world.turn);
            state = next;
        }
        // 今のデータから外れたログも、バックアップにはハードリンクで残る
        let b0 = read_backup(&backup_dir(dir, 0)).unwrap();
        let b1 = read_backup(&backup_dir(dir, 1)).unwrap();
        assert_eq!(b0.world.turn, turns[2]);
        assert_eq!(b1.world.turn, turns[1]);
        assert!(!backup_dir(dir, 2).exists());
        assert_eq!(
            read_backup_header(&backup_dir(dir, 0))
                .unwrap()
                .unwrap()
                .turn,
            turns[2]
        );
        let (_, back) = DataDir::open(dir).unwrap().unwrap();
        assert_eq!(json(&back), json(&state));
        assert_eq!(b0.logs.turns.len() + 1, state.logs.turns.len());
        assert_eq!(json(&b0)["logs"], {
            let mut s = json(&state)["logs"].clone();
            s["turns"].as_array_mut().unwrap().remove(0);
            s["history"] = json(&b0)["logs"]["history"].clone();
            s["hcup"] = json(&b0)["logs"]["hcup"].clone();
            s["auction"] = json(&b0)["logs"]["auction"].clone();
            s
        });
    }

    #[test]
    fn create_over_existing_data_starts_a_new_generation() {
        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path();
        let state = legacy_state();
        let mut data = DataDir::create(dir, &state).unwrap();
        let mut next = state.clone();
        next.world.islands[0].money = 1;
        data.record(&state, &next).unwrap();
        drop(data);
        // やり直し: 古い差分は新しいスナップショットに当てない
        let fresh = GameState::new_game(1000, &GameConfig::default());
        DataDir::create(dir, &fresh).unwrap();
        let (_, back) = DataDir::open(dir).unwrap().unwrap();
        assert_eq!(json(&back), json(&fresh));
    }
}
