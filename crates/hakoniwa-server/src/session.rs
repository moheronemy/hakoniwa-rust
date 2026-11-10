//! ログインの状態 (セッション)。
//!
//! Perl 版は島の ID とパスワードをクッキーに入れ、操作のたびにパスワードを送っていた。
//! 移植版はログインのときに 1 回だけパスワードを確かめ、ランダムなトークンをクッキーに入れる
//! (トークンとログイン中の島はサーバーのメモリにだけ置く。サーバーを再起動するとログアウトになる)。
//! フォームには別のトークン (CSRF 対策) を埋め込み、POST のたびに確かめる。

use std::collections::HashMap;
use std::sync::Mutex;

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

/// ログイン中の 1 人分
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Session {
    /// 開発している島の ID
    pub island_id: i64,
    /// フォームに埋め込む CSRF 対策のトークン
    pub csrf: String,
    /// この時刻 (Unix 秒) を過ぎたら無効
    pub expires: i64,
    /// マスターパスワードでログインした (管理者)
    pub master: bool,
    /// 次に表示する画面に出す知らせ (操作の結果)
    pub flash: Option<String>,
}

#[derive(Debug, Default)]
pub struct Sessions {
    map: Mutex<HashMap<String, Session>>,
}

/// 推測できないトークン (256 ビットの 16 進)
pub fn new_token() -> String {
    let mut bytes = [0u8; 32];
    OsRng.fill_bytes(&mut bytes);
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

impl Sessions {
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
        map.insert(token.clone(), session);
        token
    }

    /// トークンのセッション。使うたびに期限を延ばす
    pub fn get(&self, token: &str, now: i64) -> Option<Session> {
        let mut map = self.map.lock().expect("sessions lock poisoned");
        let s = map.get_mut(token)?;
        if s.expires <= now {
            map.remove(token);
            return None;
        }
        s.expires = now + LIFETIME_SECS;
        Some(s.clone())
    }

    /// 次の画面に出す知らせを入れる
    pub fn set_flash(&self, token: &str, message: impl Into<String>) {
        if let Some(s) = self
            .map
            .lock()
            .expect("sessions lock poisoned")
            .get_mut(token)
        {
            s.flash = Some(message.into());
        }
    }

    /// 知らせを取り出す (1 回だけ表示する)
    pub fn take_flash(&self, token: &str) -> Option<String> {
        self.map
            .lock()
            .expect("sessions lock poisoned")
            .get_mut(token)
            .and_then(|s| s.flash.take())
    }

    pub fn remove(&self, token: &str) {
        self.map
            .lock()
            .expect("sessions lock poisoned")
            .remove(token);
    }

    /// 島が無くなったときなど、その島のセッションをすべて消す
    pub fn remove_island(&self, island_id: i64) {
        self.map
            .lock()
            .expect("sessions lock poisoned")
            .retain(|_, s| s.island_id != island_id);
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
