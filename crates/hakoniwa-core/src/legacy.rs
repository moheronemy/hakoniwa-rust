//! Perl 版のセーブデータ (`data/` ディレクトリ) の読み込み。
//!
//! `hako-main.cgi` の `readIslandsFile` / `readIsland` と、各ログの読み込み処理を移植したもの。
//! ファイルは EUC-JP の行単位テキスト。Perl 版と同じく、行が足りないときは空行として扱う。
//!
//! 読み込む順番や既定値の入れ方は Perl 版に合わせてある。とくに
//! `if($x == '')` は「数値として 0 なら」という意味になる点に注意 ([`perl::num_eq_empty`])。

use std::fs;
use std::path::{Path, PathBuf};

use rand::Rng;
use thiserror::Error;

use crate::model::{
    AuctionState, FORMAT_VERSION, GameState, Island, IslandMap, LandCell, LogEntry, Logs,
    OwnerStats, PlannedCommand, TurnMessage, World,
};
use crate::perl;

/// `hakojima.dat` の島 1 つあたりの行数 (怪獣出現数を `monslive.dat` に保存する形式)
const ISLAND_LINES_BASE: usize = 24;
/// 怪獣出現数・人工衛星の 8 行を `hakojima.dat` に含む形式 (`$HnewGame = 1`) の行数
const ISLAND_LINES_NEW_GAME: usize = ISLAND_LINES_BASE + 8;
/// ターンログを何ファイルまで探すか
const MAX_LOG_FILES: usize = 100;

#[derive(Debug, Error)]
pub enum LegacyError {
    #[error("{path}: {source}")]
    Io {
        path: PathBuf,
        source: std::io::Error,
    },
    #[error("hakojima.dat にゲームのデータがありません (ターン数か最終更新時刻が 0)")]
    NoData,
    #[error(
        "hakojima.dat の行数 {lines} が島の数 {islands} と合いません \
         (島 1 つあたり {ISLAND_LINES_BASE} 行または {ISLAND_LINES_NEW_GAME} 行のはず)"
    )]
    UnknownLayout { lines: usize, islands: usize },
}

/// `hakojima.dat` の島データの形式 (`$HnewGame`)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum IslandLayout {
    /// `$HnewGame = 1`: 怪獣出現数・人工衛星を `hakojima.dat` に保存
    NewGame,
    /// `$HnewGame = 0`: それらを `monslive.dat` に保存
    MonsLive,
}

#[derive(Debug, Clone)]
pub struct ImportOptions {
    /// `None` なら `hakojima.dat` の行数から判定する
    pub layout: Option<IslandLayout>,
    /// 島の大きさ (`$HislandSize`)
    pub island_size: usize,
    /// コマンド入力限界数 (`$HcommandMax`)
    pub command_max: usize,
    /// ローカル掲示板行数 (`$HlbbsMax`)
    pub lbbs_max: usize,
    /// 旧形式の掲示板ログを変換する (`$HlbbsOldToNew`)
    pub lbbs_old_to_new: bool,
}

impl Default for ImportOptions {
    fn default() -> Self {
        Self {
            layout: None,
            island_size: 12,
            command_max: 40,
            lbbs_max: 15,
            lbbs_old_to_new: true,
        }
    }
}

/// 読み込み結果
#[derive(Debug)]
pub struct Import {
    pub state: GameState,
    pub layout: IslandLayout,
    /// 文字化けなど、読み込めたが注意が必要な点
    pub warnings: Vec<String>,
}

/// Perl 版の `data/` ディレクトリを読み込む。
///
/// `rng` は Perl 版と同じく、空のハコオク出品枠に品物を割り当てるのに使う。
pub fn import_dir<R: Rng + ?Sized>(
    dir: &Path,
    opts: &ImportOptions,
    rng: &mut R,
) -> Result<Import, LegacyError> {
    let mut warnings = Vec::new();
    let mut read = |name: &str| read_lines(&dir.join(name), &mut warnings);

    let main_lines = read("hakojima.dat")?.ok_or_else(|| LegacyError::Io {
        path: dir.join("hakojima.dat"),
        source: std::io::ErrorKind::NotFound.into(),
    })?;
    let mut main = Lines::new(main_lines);
    let mut owner = Lines::new(read("howner.dat")?.unwrap_or_default());
    let mut ips = Lines::new(read("ips.dat")?.unwrap_or_default());
    let mut auction = Lines::new(read("auction.dat")?.unwrap_or_default());
    let mut an = Lines::new(read("an.dat")?.unwrap_or_default());
    let monslive = read("monslive.dat")?;

    // 共通データ
    let turn = perl::int(main.next());
    if turn == 0 {
        return Err(LegacyError::NoData);
    }
    let last_time = perl::int(main.next());
    if last_time == 0 {
        return Err(LegacyError::NoData);
    }
    let island_number = perl::int(main.next()).max(0) as usize;
    let next_id = perl::int(main.next());

    let layout = match opts.layout {
        Some(l) => l,
        None => detect_layout(main.len(), island_number)?,
    };

    let mut auction_lots: Vec<String> = (0..3).map(|_| auction.next().to_string()).collect();
    crate::model::reroll_empty_lots(&mut auction_lots, rng);
    let mut survey_votes = [0i64; 5];
    for v in survey_votes.iter_mut() {
        *v = perl::int(an.next());
    }

    let mut islands = Vec::with_capacity(island_number);
    for _ in 0..island_number {
        let mut island = read_island(
            &mut main,
            &mut owner,
            &mut ips,
            &mut auction,
            &mut an,
            layout,
        );
        let path = dir.join(format!("island.{}", island.id));
        let fallback = dir.join(format!("islandtmp.{}", island.id));
        let lines = match read_lines(&path, &mut warnings)? {
            Some(l) => Some(l),
            // Perl 版は書き込み途中で止まったときのために islandtmp.N も見る
            None => read_lines(&fallback, &mut warnings)?,
        };
        match lines {
            Some(lines) => read_island_file(&mut island, Lines::new(lines), opts),
            None => {
                warnings.push(format!(
                    "{} がありません。海だけの地図にします",
                    path.display()
                ));
                island.map = IslandMap::new_sea(opts.island_size);
                island.commands = vec![PlannedCommand::default(); opts.command_max];
                island.lbbs = vec![String::new(); opts.lbbs_max];
            }
        }
        islands.push(island);
    }

    if layout == IslandLayout::MonsLive {
        let mut m = Lines::new(monslive.unwrap_or_default());
        for island in islands.iter_mut() {
            island.monster_live = perl::int(m.next());
            island.monster_live_type = perl::int(m.next());
            island.eisei = [perl::int(m.next()), perl::int(m.next())];
            island.eisei_raw = std::array::from_fn(|_| perl::int(m.next()).to_string());
        }
    }

    let logs = read_logs(dir, &mut warnings)?;

    Ok(Import {
        state: GameState {
            format_version: FORMAT_VERSION,
            world: World {
                turn,
                last_time,
                next_id,
                islands,
                auction_lots,
                survey_votes,
            },
            logs,
        },
        layout,
        warnings,
    })
}

fn detect_layout(lines: usize, islands: usize) -> Result<IslandLayout, LegacyError> {
    let body = lines.saturating_sub(4);
    if islands == 0 || body == islands * ISLAND_LINES_NEW_GAME {
        Ok(IslandLayout::NewGame)
    } else if body == islands * ISLAND_LINES_BASE {
        Ok(IslandLayout::MonsLive)
    } else {
        Err(LegacyError::UnknownLayout { lines, islands })
    }
}

/// `readIsland` のうち、`island.N` 以外の部分
fn read_island(
    main: &mut Lines,
    owner: &mut Lines,
    ips: &mut Lines,
    auction: &mut Lines,
    an: &mut Lines,
    layout: IslandLayout,
) -> Island {
    // 名前の行は「名前,スコア」
    let name_line = main.next();
    let (name, score) = match name_line.split_once(',') {
        Some((n, s)) => (n.to_string(), perl::int(s)),
        None => (name_line.to_string(), 0),
    };
    let id = perl::int(main.next());

    let id1 = perl::int(owner.next());
    let owner_name = owner.next_string();
    let totoyoso = owner.next_string();
    let totoyoso2 = owner.next_string();
    let owner_stats = OwnerStats {
        kei: perl::int(owner.next()),
        rena: perl::int(owner.next()),
        momotan: perl::int(owner.next()),
        fore: perl::int(owner.next()),
        pika: perl::int(owner.next()),
        hamu: perl::int(owner.next()),
        monta: perl::int(owner.next()),
        tare: perl::int(owner.next()),
        zipro: perl::int(owner.next()),
        leje: perl::int(owner.next()),
    };

    let ip_name = ips.next_string();
    let ip = std::array::from_fn(|_| ips.next_string());
    let ip_counters = [perl::int(ips.next()), perl::int(ips.next())];
    let etc_num = std::array::from_fn(|_| perl::int(ips.next()));
    let etc_raw = std::array::from_fn(|_| ips.next_string());

    let with_default = |s: String, default: &str| {
        if perl::num_eq_empty(&s) {
            default.to_string()
        } else {
            s
        }
    };
    let auction = AuctionState {
        auc0: with_default(auction.next_string(), "0,0,0,0,0"),
        auc1: perl::int(auction.next()),
        auc2: perl::int(auction.next()),
        auc3: perl::int(auction.next()),
        auc4: with_default(auction.next_string(), "0,0,0"),
        auc5: with_default(auction.next_string(), "0,0,0,0,0"),
        auc6: with_default(auction.next_string(), "0,0,0"),
        auc7: auction.next_string(),
        auc8: auction.next_string(),
        auc9: with_default(auction.next_string(), "0,0,0,0,0"),
    };

    // `$anflag = int(<KIN>); if($anflag == '') { $anflag = '1'; }`
    let survey_flag = match perl::int(an.next()) {
        0 => 1,
        v => v,
    };

    let prize = main.next_string();
    let absent = perl::int(main.next());
    let comment = main.next_string();
    let password = main.next_string();
    let money = perl::int(main.next());
    let food = perl::int(main.next());
    let pop = perl::int(main.next());
    let area = perl::int(main.next());
    let farm = perl::int(main.next());
    let factory = main.next_string();
    let mountain = perl::int(main.next());
    let pts = perl::int(main.next());
    let eis = std::array::from_fn(|_| perl::int(main.next()));
    let eis8 = main.next_string();
    let taiji = perl::int(main.next());
    let onm = main.next_string();

    let (monster_live, monster_live_type, eisei, eisei_raw) = match layout {
        IslandLayout::NewGame => (
            perl::int(main.next()),
            perl::int(main.next()),
            [perl::int(main.next()), perl::int(main.next())],
            std::array::from_fn(|_| main.next_string()),
        ),
        // monslive.dat から後で埋める
        IslandLayout::MonsLive => (0, 0, [0, 0], Default::default()),
    };

    Island {
        name,
        id,
        score,
        prize,
        absent,
        comment,
        password,
        money,
        food,
        pop,
        area,
        farm,
        factory,
        mountain,
        pts,
        eis,
        eis8,
        taiji,
        onm,
        monster_live,
        monster_live_type,
        eisei,
        eisei_raw,
        id1,
        owner_name,
        totoyoso,
        totoyoso2,
        owner_stats,
        ip_name,
        ip,
        ip_counters,
        etc_num,
        etc_raw,
        auction,
        survey_flag,
        map: IslandMap::new_sea(0),
        commands: Vec::new(),
        lbbs: Vec::new(),
        scratch: Default::default(),
    }
}

/// `island.N` (地図・計画・ローカル掲示板)
fn read_island_file(island: &mut Island, mut lines: Lines, opts: &ImportOptions) {
    let size = opts.island_size;
    let mut map = IslandMap::new_sea(size);
    for y in 0..size {
        let line = lines.next().as_bytes();
        for x in 0..size {
            // 1 マスは「種類 2 桁 + 値 3 桁」の 16 進。足りなければ Perl の hex('') と同じく 0
            let cell = line.get(x * 5..x * 5 + 5).unwrap_or(&[]);
            let hex = |b: &[u8]| {
                std::str::from_utf8(b)
                    .ok()
                    .and_then(|s| u32::from_str_radix(s, 16).ok())
                    .unwrap_or(0)
            };
            *map.get_mut(x, y).expect("in range") = LandCell {
                kind: hex(cell.get(..2).unwrap_or(&[])) as u8,
                value: i64::from(hex(cell.get(2..).unwrap_or(&[]))),
            };
        }
    }
    island.map = map;

    island.commands = (0..opts.command_max)
        .map(|_| parse_command(lines.next()))
        .collect();

    island.lbbs = (0..opts.lbbs_max)
        .map(|_| {
            let line = lines.next();
            if opts.lbbs_old_to_new {
                convert_old_lbbs(line)
            } else {
                line.to_string()
            }
        })
        .collect();
}

/// `^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$`
fn parse_command(line: &str) -> PlannedCommand {
    let parts: Vec<&str> = line.split(',').collect();
    let valid = parts.len() == 5 && parts.iter().all(|p| p.bytes().all(|b| b.is_ascii_digit()));
    if !valid {
        // Perl 版はマッチ失敗時に直前の $1..$5 を使ってしまうが、ここでは空の計画にする
        return PlannedCommand::default();
    }
    PlannedCommand {
        kind: perl::int(parts[0]).clamp(0, i64::from(u16::MAX)) as u16,
        target: perl::int(parts[1]),
        x: perl::int(parts[2]),
        y: perl::int(parts[3]),
        arg: perl::int(parts[4]),
    }
}

/// 旧形式 `ID>名前>本文` を新形式 `0<<ID>名前>本文` に変換する (`$HlbbsOldToNew`)
fn convert_old_lbbs(line: &str) -> String {
    let mut it = line.splitn(2, '>');
    let (Some(id), Some(rest)) = (it.next(), it.next()) else {
        return line.to_string();
    };
    // 旧形式は先頭が数字だけで、残りにもう 1 つ '>' がある
    if id.bytes().all(|b| b.is_ascii_digit()) && rest.contains('>') {
        // Perl の正規表現 `(.*)\>(.*)` は貪欲なので、名前側が最後の '>' までを取る
        let (name, body) = rest.rsplit_once('>').expect("contains '>'");
        format!("0<<{id}>{name}>{body}")
    } else {
        line.to_string()
    }
}

fn read_logs(dir: &Path, warnings: &mut Vec<String>) -> Result<Logs, LegacyError> {
    let mut logs = Logs::default();
    for i in 0..MAX_LOG_FILES {
        let Some(lines) = read_lines(&dir.join(format!("hakojima.log{i}")), warnings)? else {
            break;
        };
        logs.turns
            .push(lines.iter().filter_map(|l| parse_log_entry(l)).collect());
    }
    let turn_messages = |name: &str, warnings: &mut Vec<String>| -> Result<_, LegacyError> {
        Ok(read_lines(&dir.join(name), warnings)?
            .unwrap_or_default()
            .iter()
            .filter(|l| !l.is_empty())
            .map(|l| parse_turn_message(l))
            .collect())
    };
    logs.history = turn_messages("hakojima.his", warnings)?;
    logs.hcup = turn_messages("hakojima.lhc", warnings)?;
    logs.auction = turn_messages("hakojima.auc", warnings)?;
    Ok(logs)
}

/// `^([0-9]*),([0-9]*),([0-9]*),([0-9]*),(.*)$`
fn parse_log_entry(line: &str) -> Option<LogEntry> {
    let mut it = line.splitn(5, ',');
    let fields: [&str; 5] = std::array::from_fn(|_| it.next().unwrap_or(""));
    if fields[..4]
        .iter()
        .any(|f| !f.bytes().all(|b| b.is_ascii_digit()))
        || line.matches(',').count() < 4
    {
        return None;
    }
    let id = |s: &str| (!s.is_empty()).then(|| perl::int(s));
    Some(LogEntry {
        secret: perl::int(fields[0]) == 1,
        turn: perl::int(fields[1]),
        island1: id(fields[2]),
        island2: id(fields[3]),
        message: fields[4].to_string(),
    })
}

/// `^([0-9]*),(.*)$`
fn parse_turn_message(line: &str) -> TurnMessage {
    match line.split_once(',') {
        Some((t, m)) if t.bytes().all(|b| b.is_ascii_digit()) => TurnMessage {
            turn: perl::int(t),
            message: m.to_string(),
        },
        _ => TurnMessage {
            turn: 0,
            message: line.to_string(),
        },
    }
}

/// ファイルを EUC-JP として読み、行に分ける。ファイルが無ければ `None`
fn read_lines(path: &Path, warnings: &mut Vec<String>) -> Result<Option<Vec<String>>, LegacyError> {
    let bytes = match fs::read(path) {
        Ok(b) => b,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(source) => {
            return Err(LegacyError::Io {
                path: path.to_path_buf(),
                source,
            });
        }
    };
    let (text, _, had_errors) = encoding_rs::EUC_JP.decode(&bytes);
    if had_errors {
        warnings.push(format!(
            "{}: EUC-JP として読めない文字がありました (U+FFFD に置き換えました)",
            path.display()
        ));
    }
    let mut lines: Vec<String> = text
        .split('\n')
        .map(|l| l.strip_suffix('\r').unwrap_or(l).to_string())
        .collect();
    // 最後の改行の後ろの空要素
    if lines.last().is_some_and(String::is_empty) {
        lines.pop();
    }
    Ok(Some(lines))
}

/// Perl の `<IN>` のように 1 行ずつ取り出す。尽きたら空文字列を返す
struct Lines {
    lines: Vec<String>,
    pos: usize,
}

impl Lines {
    fn new(lines: Vec<String>) -> Self {
        Self { lines, pos: 0 }
    }

    fn len(&self) -> usize {
        self.lines.len()
    }

    fn next(&mut self) -> &str {
        let line = self.lines.get(self.pos).map(String::as_str).unwrap_or("");
        self.pos += 1;
        line
    }

    fn next_string(&mut self) -> String {
        self.next().to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn old_lbbs_is_converted() {
        assert_eq!(
            convert_old_lbbs("3>名無し>こんにちは"),
            "0<<3>名無し>こんにちは"
        );
        assert_eq!(
            convert_old_lbbs("0<<1>1：島主>ようこそ"),
            "0<<1>1：島主>ようこそ"
        );
        assert_eq!(convert_old_lbbs("0<<0>>"), "0<<0>>");
        assert_eq!(convert_old_lbbs(""), "");
    }

    #[test]
    fn log_entry_parsing() {
        let e = parse_log_entry("1,13,2,,<B>本文, カンマ入り</B>").unwrap();
        assert!(e.secret);
        assert_eq!(e.turn, 13);
        assert_eq!(e.island1, Some(2));
        assert_eq!(e.island2, None);
        assert_eq!(e.message, "<B>本文, カンマ入り</B>");
        assert!(parse_log_entry("garbage").is_none());
    }

    #[test]
    fn command_parsing() {
        assert_eq!(
            parse_command("31,2,5,6,1"),
            PlannedCommand {
                kind: 31,
                target: 2,
                x: 5,
                y: 6,
                arg: 1
            }
        );
        assert_eq!(parse_command(""), PlannedCommand::default());
    }

    #[test]
    fn layout_detection() {
        assert_eq!(detect_layout(4, 0).unwrap(), IslandLayout::NewGame);
        assert_eq!(detect_layout(4 + 2 * 32, 2).unwrap(), IslandLayout::NewGame);
        assert_eq!(
            detect_layout(4 + 2 * 24, 2).unwrap(),
            IslandLayout::MonsLive
        );
        assert!(detect_layout(10, 2).is_err());
    }
}
