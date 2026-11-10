//! 1 ターン分のログ (`hakojima.log<N>` 1 つ分) を、圧縮して持つ型。
//!
//! 大きな地図・多くの島では 1 ターンのログが数百万行・数百 MB になる (docs/SCALING.md)。
//! そこでログを並び順のまま [`CHUNK`] 行ずつのかたまりに分けて圧縮し、
//! 「島 ID → その島が関わる行 (1 番目か 2 番目の島) を含むかたまり」の索引を持つ。
//!
//! - 全部の行が要るとき (トップページ・最近の出来事) は、かたまりを順に展開する ([`TurnLog::entries`])
//! - 1 つの島の行だけが要るとき (島の近況) は、索引にあるかたまりだけを展開する ([`TurnLog::entries_for`])
//!
//! 行の文面は Perl 版と同じ HTML のまま。人が読む形 (JSON) では今までどおり行の並びとして読み書きし、
//! バイナリの形 (bincode) では圧縮したかたまりと索引をそのまま読み書きする。

use std::collections::BTreeMap;
use std::fmt;

use serde::de::Error as _;
use serde::{Deserialize, Deserializer, Serialize, Serializer};

use crate::model::{LogEntry, LogRecord};

/// 1 つのかたまりの行数
pub const CHUNK: usize = 1024;

/// かたまりの圧縮の強さ (zstd)。速さを優先する
const LEVEL: i32 = 1;

/// 1 ターン分のログ (変わらない)
#[derive(Clone, Default, Serialize, Deserialize)]
#[serde(rename = "TurnLog")]
struct Packed {
    /// 行数
    len: usize,
    /// `CHUNK` 行ずつ ([`LogRecord`] の並び) bincode にして zstd で圧縮したもの
    chunks: Vec<Vec<u8>>,
    /// 島 ID → その島が関わる行を含むかたまりの番号 (昇順)
    index: BTreeMap<i64, Vec<u32>>,
}

#[derive(Clone, Default)]
pub struct TurnLog(Packed);

impl TurnLog {
    /// 行の並びから作る。かたまりの圧縮は CPU の数だけ並べて行う (ゲームの結果には関わらない)
    pub fn new(entries: Vec<LogEntry>) -> Self {
        Self::from_records(entries.into_iter().map(LogRecord::from_entry).collect())
    }

    /// 溜めたログ (文面と出来事) から作る。出来事は文面にせずに持つ
    pub fn from_records(entries: Vec<LogRecord>) -> Self {
        let len = entries.len();
        let mut index: BTreeMap<i64, Vec<u32>> = BTreeMap::new();
        let groups: Vec<&[LogRecord]> = entries.chunks(CHUNK).collect();
        // かたまりごとに島 ID を集めて重複を除いてから索引に入れる
        // (行ごとに索引を引くと、数百万行では圧縮より時間がかかる)
        let mut ids: Vec<i64> = Vec::with_capacity(CHUNK * 2);
        for (n, group) in groups.iter().enumerate() {
            ids.clear();
            ids.extend(group.iter().flat_map(|e| [e.island1, e.island2]).flatten());
            ids.sort_unstable();
            ids.dedup();
            for &id in &ids {
                index.entry(id).or_default().push(n as u32);
            }
        }
        let chunks = compress_all(&groups);
        Self(Packed { len, chunks, index })
    }

    pub fn len(&self) -> usize {
        self.0.len
    }

    pub fn is_empty(&self) -> bool {
        self.0.len == 0
    }

    /// 全部の行 (保存された順)
    pub fn entries(&self) -> Vec<LogEntry> {
        let mut out = Vec::with_capacity(self.0.len);
        for chunk in &self.0.chunks {
            out.extend(decompress(chunk).iter().map(LogRecord::to_entry));
        }
        out
    }

    /// 島 `id` が 1 番目か 2 番目の島である行 (保存された順)
    pub fn entries_for(&self, id: i64) -> Vec<LogEntry> {
        let Some(list) = self.0.index.get(&id) else {
            return Vec::new();
        };
        list.iter()
            .flat_map(|&n| decompress(&self.0.chunks[n as usize]))
            .filter(|e| e.island1 == Some(id) || e.island2 == Some(id))
            .map(|r| r.to_entry())
            .collect()
    }

    /// `start` 行目 (0 から) から後ろの行を、位置と一緒に順に返す。
    /// かたまりは読み進めたぶんだけ展開する (ページ送りで先頭の数百行だけ要るときなど)
    pub fn iter_from(&self, start: usize) -> impl Iterator<Item = (usize, LogEntry)> + '_ {
        let first = start / CHUNK;
        self.0
            .chunks
            .iter()
            .enumerate()
            .skip(first)
            .flat_map(|(n, chunk)| {
                decompress(chunk)
                    .into_iter()
                    .enumerate()
                    .map(move |(i, r)| (n * CHUNK + i, r.to_entry()))
            })
            .skip(start % CHUNK)
    }

    /// 行を書き換えたものを作る (テストで Perl 版の結果を直すときなど)
    pub fn map_entries(&self, f: impl FnOnce(&mut Vec<LogEntry>)) -> Self {
        let mut entries = self.entries();
        f(&mut entries);
        Self::new(entries)
    }

    /// 圧縮したかたまりの合計の大きさ (バイト)
    pub fn packed_bytes(&self) -> usize {
        self.0.chunks.iter().map(Vec::len).sum()
    }
}

/// 1 つのかたまりを圧縮する。圧縮器 (zstd の作業領域) はスレッドの中で使い回す
/// (かたまりごとに作ると、それだけで圧縮より時間がかかる)
fn compress(z: &mut zstd::bulk::Compressor<'_>, raw: &mut Vec<u8>, group: &[LogRecord]) -> Vec<u8> {
    raw.clear();
    bincode::serialize_into(&mut *raw, group).expect("ログを bincode にできない");
    z.compress(raw).expect("ログを圧縮できない")
}

fn compress_part(part: &[&[LogRecord]]) -> Vec<Vec<u8>> {
    let mut z = zstd::bulk::Compressor::new(LEVEL).expect("圧縮器を作れない");
    let mut raw = Vec::new();
    part.iter().map(|g| compress(&mut z, &mut raw, g)).collect()
}

fn compress_all(groups: &[&[LogRecord]]) -> Vec<Vec<u8>> {
    let threads = std::thread::available_parallelism()
        .map(|n| n.get())
        .unwrap_or(1)
        .min(groups.len().div_ceil(8).max(1));
    if threads <= 1 {
        return compress_part(groups);
    }
    let per = groups.len().div_ceil(threads);
    std::thread::scope(|s| {
        let handles: Vec<_> = groups
            .chunks(per)
            .map(|part| s.spawn(move || compress_part(part)))
            .collect();
        handles
            .into_iter()
            .flat_map(|h| h.join().expect("ログの圧縮が止まった"))
            .collect()
    })
}

fn decompress(chunk: &[u8]) -> Vec<LogRecord> {
    // 1 かたまりは CHUNK 行。1 行あたりの上限を大きめに見積もる
    let raw = zstd::bulk::decompress(chunk, CHUNK * 64 * 1024).expect("ログを展開できない");
    bincode::deserialize(&raw).expect("ログの形が違う")
}

impl From<Vec<LogEntry>> for TurnLog {
    fn from(entries: Vec<LogEntry>) -> Self {
        Self::new(entries)
    }
}

impl PartialEq for TurnLog {
    fn eq(&self, other: &Self) -> bool {
        self.0.len == other.0.len
            && (self.0.chunks == other.0.chunks || self.entries() == other.entries())
    }
}

impl Eq for TurnLog {}

impl fmt::Debug for TurnLog {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "TurnLog({} 行, 圧縮後 {} バイト)",
            self.0.len,
            self.packed_bytes()
        )
    }
}

impl Serialize for TurnLog {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        if s.is_human_readable() {
            self.entries().serialize(s)
        } else {
            self.0.serialize(s)
        }
    }
}

impl<'de> Deserialize<'de> for TurnLog {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        if d.is_human_readable() {
            Ok(Self::new(Vec::<LogEntry>::deserialize(d)?))
        } else {
            let p = Packed::deserialize(d)?;
            if p.chunks.len() != p.len.div_ceil(CHUNK) {
                return Err(D::Error::custom("ログのかたまりの数が行数と合わない"));
            }
            Ok(Self(p))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn entry(n: usize, island1: Option<i64>, island2: Option<i64>) -> LogEntry {
        LogEntry {
            secret: n.is_multiple_of(7),
            turn: 5,
            island1,
            island2,
            message: format!("<B>行{n}</B>"),
        }
    }

    fn sample(len: usize) -> Vec<LogEntry> {
        (0..len)
            .map(|n| match n % 5 {
                0 => entry(n, None, None),
                1 => entry(n, Some(1), Some(2)),
                _ => entry(n, Some((n % 4) as i64), None),
            })
            .collect()
    }

    #[test]
    fn keeps_order_and_finds_entries_by_island() {
        for len in [0, 1, CHUNK - 1, CHUNK, CHUNK * 3 + 17] {
            let all = sample(len);
            let log = TurnLog::new(all.clone());
            assert_eq!(log.len(), len);
            assert_eq!(log.entries(), all);
            for id in 0..5 {
                let want: Vec<_> = all
                    .iter()
                    .filter(|e| e.island1 == Some(id) || e.island2 == Some(id))
                    .cloned()
                    .collect();
                assert_eq!(log.entries_for(id), want, "len {len} id {id}");
            }
        }
    }

    #[test]
    fn iter_from_starts_anywhere() {
        let all = sample(CHUNK * 2 + 10);
        let log = TurnLog::new(all.clone());
        for start in [
            0,
            1,
            CHUNK - 1,
            CHUNK,
            CHUNK + 3,
            CHUNK * 2 + 9,
            CHUNK * 2 + 10,
            99_999,
        ] {
            let got: Vec<_> = log.iter_from(start).collect();
            let want: Vec<_> = all.iter().cloned().enumerate().skip(start).collect();
            assert_eq!(got, want, "start {start}");
        }
    }

    #[test]
    fn json_is_the_plain_list_and_bincode_keeps_the_packed_form() {
        let all = sample(CHUNK + 5);
        let log = TurnLog::new(all.clone());
        let json = serde_json::to_value(&log).unwrap();
        assert_eq!(json, serde_json::to_value(&all).unwrap());
        assert_eq!(serde_json::from_value::<TurnLog>(json).unwrap(), log);
        let bin = bincode::serialize(&log).unwrap();
        let back: TurnLog = bincode::deserialize(&bin).unwrap();
        assert_eq!(back.entries(), all);
        assert_eq!(back.entries_for(2), log.entries_for(2));
    }
}
