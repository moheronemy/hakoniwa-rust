//! 1 プロセスで複数のゲーム (セット) を動かす (docs/MULTISET.md)。
//!
//! セットは [`AppState`] 1 つ (設定・セッション・データディレクトリ・状態)。サーバーはセットの一覧と
//! 「ホスト名 → セット」の対応を持ち、要求のホスト名でセットを決める ([`Set`])。
//! どのセットのホスト名にも当たらなければ既定のセット (サーバーの設定ファイルの `[game]`)、
//! 既定のセットも無ければ 404 にする。

use std::collections::HashMap;
use std::sync::Arc;

use axum::extract::FromRequestParts;
use axum::http::request::Parts;
use axum::http::{StatusCode, header};
use axum::response::{IntoResponse, Response};

use crate::AppState;

/// サーバーが動かしているセット
#[derive(Default)]
pub struct Sets {
    /// どのホスト名にも当たらないときのセット
    default: Option<Arc<AppState>>,
    /// ホスト名 (小文字、ポートを除く) → セット
    by_host: HashMap<String, Arc<AppState>>,
    /// セットの ID と、そのセット (読み込んだ順)
    list: Vec<(String, Arc<AppState>)>,
}

impl Sets {
    /// 既定のセット 1 つだけ (これまでの 1 プロセス 1 ゲームの形)
    pub fn single(app: Arc<AppState>) -> Self {
        Self {
            default: Some(app),
            ..Self::default()
        }
    }

    pub fn set_default(&mut self, app: Arc<AppState>) {
        self.default = Some(app);
    }

    /// セットを足す。ホスト名が別のセットと重なればエラー
    pub fn add(&mut self, id: &str, hosts: &[String], app: Arc<AppState>) -> anyhow::Result<()> {
        if self.list.iter().any(|(i, _)| i == id) {
            anyhow::bail!("セット {id} が 2 回あります");
        }
        for h in hosts {
            let h = normalize_host(h);
            if h.is_empty() {
                anyhow::bail!("セット {id} のホスト名が空です");
            }
            if self.by_host.insert(h.clone(), app.clone()).is_some() {
                anyhow::bail!("ホスト名 {h} が複数のセットにあります");
            }
        }
        self.list.push((id.to_string(), app));
        Ok(())
    }

    /// ID でセットを探す
    pub fn get(&self, id: &str) -> Option<&Arc<AppState>> {
        self.list.iter().find(|(i, _)| i == id).map(|(_, a)| a)
    }

    pub fn default_set(&self) -> Option<&Arc<AppState>> {
        self.default.as_ref()
    }

    /// 読み込んだセット (既定のセットは含まない)
    pub fn list(&self) -> &[(String, Arc<AppState>)] {
        &self.list
    }

    /// ホスト名でセットを探す (当たらなければ既定のセット)
    pub fn find(&self, host: &str) -> Option<Arc<AppState>> {
        self.by_host
            .get(&normalize_host(host))
            .or(self.default.as_ref())
            .cloned()
    }
}

/// ホスト名を比べる形にする: 小文字にし、ポート (`:8080`) と末尾の `.` を除く
pub fn normalize_host(host: &str) -> String {
    let host = host.trim();
    // IPv6 の [::1]:8080 は ] のあとのポートだけを除く
    let without_port = if let Some(rest) = host.strip_prefix('[') {
        match rest.find(']') {
            Some(end) => &host[..end + 2],
            None => host,
        }
    } else {
        host.rsplit_once(':').map_or(host, |(h, _)| h)
    };
    without_port.trim_end_matches('.').to_ascii_lowercase()
}

/// 要求のホスト名で決めたセット。画面の関数はこれを受け取る
pub struct Set(pub Arc<AppState>);

impl FromRequestParts<Arc<Sets>> for Set {
    type Rejection = Response;

    async fn from_request_parts(parts: &mut Parts, sets: &Arc<Sets>) -> Result<Self, Response> {
        // HTTP/1.1 は Host、HTTP/2 は :authority (URI に入る)
        let host = parts
            .headers
            .get(header::HOST)
            .and_then(|v| v.to_str().ok())
            .map(str::to_string)
            .or_else(|| parts.uri.authority().map(|a| a.to_string()))
            .unwrap_or_default();
        sets.find(&host)
            .map(Set)
            .ok_or_else(|| (StatusCode::NOT_FOUND, "そのゲームは見つかりません。").into_response())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hosts_are_compared_without_port_and_case() {
        assert_eq!(normalize_host("Set1.Example.COM:8080"), "set1.example.com");
        assert_eq!(normalize_host("set1.example.com."), "set1.example.com");
        assert_eq!(normalize_host("[::1]:8080"), "[::1]");
        assert_eq!(normalize_host("localhost"), "localhost");
    }
}
