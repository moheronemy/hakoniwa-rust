//! パスワード (`encode`, `checkPassword`)。
//!
//! Perl 版は `crypt($pw, 'h2')` (伝統的な DES crypt。先頭 8 文字だけが効く) で保存している。
//! 移行した島がそのまま使えるよう照合はそれにも対応し、新しく設定するパスワードは
//! SHA-512 crypt (`$6$...`) で保存する。

use crate::GameConfig;

/// 新しく設定するパスワードを保存する形にする
pub fn hash_password(plain: &str) -> String {
    pwhash::sha512_crypt::hash(plain).expect("sha512_crypt")
}

/// `checkPassword`: 空なら不一致、マスターパスワードなら一致、そうでなければ保存した値と照合する
pub fn check_password(config: &GameConfig, stored: &str, input: &str) -> bool {
    if input.is_empty() {
        return false;
    }
    if config.passwords.master.as_deref() == Some(input) {
        return true;
    }
    verify(stored, input)
}

/// 保存した値 (DES crypt か SHA-512 crypt) と照合する
pub fn verify(stored: &str, input: &str) -> bool {
    !stored.is_empty() && pwhash::unix::verify(input, stored)
}

/// 保存した値が Perl 版の DES crypt (`h2` で始まる 13 文字) なら true。
/// ログインに成功したときに [`hash_password`] で置き換えるのに使う
pub fn is_legacy(stored: &str) -> bool {
    stored.len() == 13 && !stored.starts_with('$')
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn legacy_des_crypt_matches_perl() {
        // perl -e 'print crypt("p", "h2")'
        assert!(verify("h2.zw/DzWPsPY", "p"));
        assert!(!verify("h2.zw/DzWPsPY", "q"));
        // DES crypt は先頭 8 文字だけを見る (Perl 版のまま)
        // perl -e 'print crypt("abcdefgh", "h2")'
        assert!(verify("h2jyhWsY/cn3.", "abcdefghXYZ"));
        assert!(is_legacy("h2.zw/DzWPsPY"));
    }

    #[test]
    fn new_hash_and_master() {
        let h = hash_password("secret");
        assert!(!is_legacy(&h));
        assert!(verify(&h, "secret") && !verify(&h, "secreT"));
        let config = GameConfig {
            passwords: crate::config::Passwords {
                master: Some("m".into()),
                ..Default::default()
            },
            ..Default::default()
        };
        assert!(check_password(&config, &h, "m"));
        assert!(!check_password(&config, &h, ""));
        assert!(!check_password(&config, "", "x"));
    }
}
