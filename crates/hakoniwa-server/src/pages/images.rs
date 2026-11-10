//! Perl 版の地形の画像 (`land0.gif` など) を出す。
//!
//! 画像は移植元の著作物で再配布できないので、リポジトリには入れていない。持っている運営者が
//! 設定の `image_dir` に置いたときだけ使い、無ければ地図は色と文字のタイルで描く。

use axum::extract::Path;
use axum::http::{StatusCode, header};
use axum::response::{IntoResponse, Response};

use crate::sets::Set;

/// 出してよい画像の名前 (英数字と `_` `-` だけの `.gif`)
pub fn valid_name(name: &str) -> bool {
    let Some(stem) = name.strip_suffix(".gif") else {
        return false;
    };
    !stem.is_empty()
        && stem.len() <= 64
        && stem
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
}

pub async fn image(Set(app): Set, Path(name): Path<String>) -> Response {
    let Some(dir) = &app.options.image_dir else {
        return StatusCode::NOT_FOUND.into_response();
    };
    if !valid_name(&name) {
        return StatusCode::NOT_FOUND.into_response();
    }
    match tokio::fs::read(dir.join(&name)).await {
        Ok(bytes) => (
            [
                (header::CONTENT_TYPE, "image/gif"),
                (header::CACHE_CONTROL, "public, max-age=86400"),
            ],
            bytes,
        )
            .into_response(),
        Err(_) => StatusCode::NOT_FOUND.into_response(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn names() {
        assert!(valid_name("land0.gif") && valid_name("house3.gif"));
        assert!(!valid_name("../x.gif") && !valid_name("a/b.gif") && !valid_name(".gif"));
        assert!(!valid_name("land0.png"));
    }
}
