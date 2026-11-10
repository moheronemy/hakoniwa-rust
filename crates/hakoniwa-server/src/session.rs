//! ログインの状態 (セッション)。
//!
//! Perl 版は島の ID とパスワードをクッキーに入れ、操作のたびにパスワードを送っていた。
//! 移植版はログインのときに 1 回だけパスワードを確かめ、ランダムなトークンをクッキーに入れる。
//! フォームには別のトークン (CSRF 対策) を埋め込み、POST のたびに確かめる。
//!
//! セッションはセットのデータディレクトリの `sessions.json` にも書き、サーバーを再起動しても
//! ログインが続くようにする ([`Sessions::open`])。ファイルにはクッキーのトークンそのものは書かず、
//! SHA-256 のハッシュだけを書く (ファイルを読まれても、そのままではログインに使えない)。
//! 書くのはログイン・ログアウト・島の削除のときと、使ったことで有効期限が保存した値より
//! 1 日以上延びたとき。画面の知らせ (`flash`) は書かない。

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use axum::http::HeaderMap;
use axum::http::header::COOKIE;
use rand::RngCore;
use rand::rngs::OsRng;

/// セッションのクッキーの名前
pub const COOKIE_NAME: &str = "hako_session";

/// 管理者 (マスターパスワードで管理画面に入った人) のセッションの島 ID。島には結び付かない
pub const ADMIN_ISLAND: i64 = -1;

/// 何もしないでいるとログアウトになるまでの秒数 (30 日)
pub const LIFETIME_SECS: i64 = 30 * 24 * 3600;

/// 有効期限がこれだけ延びたらファイルに書く
const PERSIST_RENEWAL_SECS: i64 = 24 * 3600;

/// ログイン中の 1 人分
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Session {
    /// 開発している島の ID
    pub island_id: i64,
    /// フォームに埋め込む CSRF 対策のトークン
    pub csrf: String,
    /// この時刻 (Unix 秒) を過ぎたら無効
    pub expires: i64,
    /// マスターパスワードでログインした (管理者)
    pub master: bool,
    /// 次に表示する画面に出す知らせ (操作の結果)。ファイルには書かない
    #[serde(skip)]
    pub flash: Option<String>,
}

/// ログイン中のセッション。キーはトークンの SHA-256 (16 進)
#[derive(Debug, Default)]
pub struct Sessions {
    map: Mutex<HashMap<String, Session>>,
    /// 書き込む先 (`None` ならメモリだけ。テスト用)
    path: Option<PathBuf>,
    /// ファイルに書いた有効期限 (延びたら書き直すかの判断に使う)
    persisted: Mutex<HashMap<String, i64>>,
}

/// ファイルの形
#[derive(Serialize, Deserialize)]
struct SessionsFile {
    version: u32,
    /// トークンの SHA-256 (16 進) → セッション
    sessions: HashMap<String, Session>,
}

fn key(token: &str) -> String {
    Sha256::digest(token.as_bytes())
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect()
}

/// 推測できないトークン (256 ビットの 16 進)
pub fn new_token() -> String {
    let mut bytes = [0u8; 32];
    OsRng.fill_bytes(&mut bytes);
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

impl Sessions {
    /// `path` (`sessions.json`) から読み込み、以後の変更もそこに書く。ファイルが無ければ空。
    /// 読めなければ空で始める (ログアウトになるだけなので、サーバーは止めない)
    pub fn open(path: &Path, now: i64) -> Self {
        let mut map = HashMap::new();
        match std::fs::read(path) {
            Ok(bytes) => match serde_json::from_slice::<SessionsFile>(&bytes) {
                Ok(f) => map = f.sessions,
                Err(e) => tracing::warn!(path = %path.display(), "セッションを読めません: {e}"),
            },
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => {}
            Err(e) => tracing::warn!(path = %path.display(), "セッションを読めません: {e}"),
        }
        map.retain(|_, s: &mut Session| s.expires > now);
        let persisted = map.iter().map(|(k, s)| (k.clone(), s.expires)).collect();
        Self {
            map: Mutex::new(map),
            path: Some(path.to_path_buf()),
            persisted: Mutex::new(persisted),
        }
    }

    /// いまのセッションをファイルに書く (一時ファイル + rename)。書けなくても止めない
    fn save(&self, map: &HashMap<String, Session>) {
        let Some(path) = &self.path else {
            return;
        };
        let file = SessionsFile {
            version: 1,
            sessions: map.clone(),
        };
        let result = (|| -> std::io::Result<()> {
            let tmp = path.with_extension("json.tmp");
            let bytes = serde_json::to_vec(&file).map_err(std::io::Error::other)?;
            {
                use std::io::Write;
                let mut opts = std::fs::OpenOptions::new();
                opts.write(true).create(true).truncate(true);
                #[cfg(unix)]
                {
                    use std::os::unix::fs::OpenOptionsExt;
                    opts.mode(0o600);
                }
                let mut f = opts.open(&tmp)?;
                f.write_all(&bytes)?;
            }
            std::fs::rename(&tmp, path)
        })();
        match result {
            Ok(()) => {
                *self.persisted.lock().expect("sessions lock poisoned") =
                    map.iter().map(|(k, s)| (k.clone(), s.expires)).collect();
            }
            Err(e) => tracing::warn!(path = %path.display(), "セッションを書けません: {e}"),
        }
    }

    /// ログインした島のセッションを作り、クッキーに入れるトークンを返す
    pub fn create(&self, island_id: i64, master: bool, now: i64) -> String {
        let token = new_token();
        let session = Session {
            island_id,
            csrf: new_token(),
            expires: now + LIFETIME_SECS,
            master,
            flash: None,
        };
        let mut map = self.map.lock().expect("sessions lock poisoned");
        map.retain(|_, s| s.expires > now);
        map.insert(key(&token), session);
        self.save(&map);
        token
    }

    /// トークンのセッション。使うたびに期限を延ばす
    pub fn get(&self, token: &str, now: i64) -> Option<Session> {
        let k = key(token);
        let mut map = self.map.lock().expect("sessions lock poisoned");
        let s = map.get_mut(&k)?;
        if s.expires <= now {
            map.remove(&k);
            return None;
        }
        s.expires = now + LIFETIME_SECS;
        let out = s.clone();
        let stale = self
            .persisted
            .lock()
            .expect("sessions lock poisoned")
            .get(&k)
            .is_none_or(|&e| out.expires - e >= PERSIST_RENEWAL_SECS);
        if stale {
            self.save(&map);
        }
        Some(out)
    }

    /// 次の画面に出す知らせを入れる
    pub fn set_flash(&self, token: &str, message: impl Into<String>) {
        if let Some(s) = self
            .map
            .lock()
            .expect("sessions lock poisoned")
            .get_mut(&key(token))
        {
            s.flash = Some(message.into());
        }
    }

    /// 知らせを取り出す (1 回だけ表示する)
    pub fn take_flash(&self, token: &str) -> Option<String> {
        self.map
            .lock()
            .expect("sessions lock poisoned")
            .get_mut(&key(token))
            .and_then(|s| s.flash.take())
    }

    pub fn remove(&self, token: &str) {
        let mut map = self.map.lock().expect("sessions lock poisoned");
        if map.remove(&key(token)).is_some() {
            self.save(&map);
        }
    }

    /// 島が無くなったときなど、その島のセッションをすべて消す
    pub fn remove_island(&self, island_id: i64) {
        let mut map = self.map.lock().expect("sessions lock poisoned");
        let before = map.len();
        map.retain(|_, s| s.island_id != island_id);
        if map.len() != before {
            self.save(&map);
        }
    }
}

/// リクエストのクッキーからセッションのトークンを取り出す
pub fn token_from(headers: &HeaderMap) -> Option<String> {
    headers
        .get_all(COOKIE)
        .iter()
        .filter_map(|v| v.to_str().ok())
        .flat_map(|v| v.split(';'))
        .filter_map(|kv| kv.trim().split_once('='))
        .find(|(k, _)| *k == COOKIE_NAME)
        .map(|(_, v)| v.to_string())
}

/// ログインのクッキー (`Set-Cookie` の値)
pub fn set_cookie(token: &str, secure: bool) -> String {
    format!(
        "{COOKIE_NAME}={token}; Path=/; Max-Age={LIFETIME_SECS}; HttpOnly; SameSite=Lax{}",
        if secure { "; Secure" } else { "" }
    )
}

/// ログアウトのクッキー
pub fn clear_cookie() -> String {
    format!("{COOKIE_NAME}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")
}

/// 2 つの文字列を、長さ以外の情報が漏れないように比べる
pub fn same(a: &str, b: &str) -> bool {
    a.len() == b.len()
        && a.bytes()
            .zip(b.bytes())
            .fold(0u8, |acc, (x, y)| acc | (x ^ y))
            == 0
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::http::HeaderValue;

    /// 開き直しても (再起動しても) ログインが続く。ファイルにはトークンそのものを書かない
    #[test]
    fn sessions_survive_reopen() {
        let tmp = tempfile::tempdir().unwrap();
        let path = tmp.path().join("sessions.json");
        let now = 1_000_000;
        let s = Sessions::open(&path, now);
        let a = s.create(1, false, now);
        let b = s.create(2, false, now);
        let admin = s.create(ADMIN_ISLAND, true, now);
        s.set_flash(&a, "知らせ");
        let csrf = s.get(&a, now).unwrap().csrf;
        let text = std::fs::read_to_string(&path).unwrap();
        assert!(!text.contains(&a) && !text.contains(&b) && !text.contains(&admin));
        assert!(text.contains(&key(&a)));
        assert!(!text.contains("知らせ"));

        let s = Sessions::open(&path, now + 10);
        let got = s.get(&a, now + 10).unwrap();
        assert_eq!((got.island_id, got.csrf, got.master), (1, csrf, false));
        assert!(got.flash.is_none());
        assert!(s.get(&admin, now + 10).unwrap().master);

        // ログアウトと島の削除も残る
        s.remove(&b);
        s.remove_island(1);
        let s = Sessions::open(&path, now + 20);
        assert!(s.get(&a, now + 20).is_none());
        assert!(s.get(&b, now + 20).is_none());
        assert!(s.get(&admin, now + 20).is_some());
    }

    /// 期限切れは読み込むときに捨てる。期限の延長は 1 日以上延びたときだけ書く
    #[test]
    fn expiry_and_renewal_writes() {
        let tmp = tempfile::tempdir().unwrap();
        let path = tmp.path().join("sessions.json");
        let now = 1_000_000;
        let s = Sessions::open(&path, now);
        let a = s.create(1, false, now);
        let written = |p: &Path| -> i64 {
            let f: SessionsFile = serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap();
            f.sessions.values().next().unwrap().expires
        };
        assert_eq!(written(&path), now + LIFETIME_SECS);
        s.get(&a, now + 60).unwrap();
        assert_eq!(
            written(&path),
            now + LIFETIME_SECS,
            "1 日たたないうちは書かない"
        );
        s.get(&a, now + 2 * 24 * 3600).unwrap();
        assert_eq!(written(&path), now + 2 * 24 * 3600 + LIFETIME_SECS);

        let later = now + 2 * 24 * 3600 + LIFETIME_SECS + 1;
        let s = Sessions::open(&path, later);
        assert!(s.get(&a, later).is_none());
    }

    /// 壊れたファイルは空として始める (止めない)
    #[test]
    fn broken_file_starts_empty() {
        let tmp = tempfile::tempdir().unwrap();
        let path = tmp.path().join("sessions.json");
        std::fs::write(&path, "{ not json").unwrap();
        let s = Sessions::open(&path, 1);
        let t = s.create(3, false, 1);
        assert!(Sessions::open(&path, 2).get(&t, 2).is_some());
    }

    #[test]
    fn create_get_expire() {
        let s = Sessions::default();
        let t = s.create(3, false, 100);
        assert_eq!(t.len(), 64);
        assert_eq!(s.get(&t, 200).unwrap().island_id, 3);
        assert!(s.get(&t, 200 + LIFETIME_SECS).is_none());
        assert!(s.get("nope", 0).is_none());
        let t = s.create(4, false, 0);
        s.remove_island(4);
        assert!(s.get(&t, 1).is_none());
    }

    #[test]
    fn cookie_parsing() {
        let mut h = HeaderMap::new();
        h.insert(
            COOKIE,
            HeaderValue::from_static("a=1; hako_session=abc; b=2"),
        );
        assert_eq!(token_from(&h).as_deref(), Some("abc"));
        assert!(same("abc", "abc") && !same("abc", "abd") && !same("a", "ab"));
    }
}
