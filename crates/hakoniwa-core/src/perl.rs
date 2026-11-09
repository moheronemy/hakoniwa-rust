//! Perl 版の挙動を再現するための小さなヘルパー。
//!
//! 元のスクリプトは「文字列を数値として扱う」箇所が多く、その振る舞いを
//! 移植先でも同じにしておかないと、ゲームの計算結果が変わってしまう。

/// Perl の `int($s)` 相当。
///
/// 先頭の空白を読み飛ばし、符号と数字の並びを整数として読む。
/// 数字が無ければ 0 を返す。小数部 (`3.7` → 3) や後続のゴミ (`12abc` → 12) は無視する。
pub fn int(s: &str) -> i64 {
    let s = s.trim_start();
    let (neg, rest) = match s.as_bytes().first() {
        Some(b'-') => (true, &s[1..]),
        Some(b'+') => (false, &s[1..]),
        _ => (false, s),
    };
    let digits = rest.bytes().take_while(u8::is_ascii_digit).count();
    let mut value: i64 = 0;
    for b in rest.as_bytes()[..digits].iter() {
        value = value.saturating_mul(10).saturating_add(i64::from(b - b'0'));
    }
    if neg { -value } else { value }
}

/// Perl の `$x == ''` 相当 (数値比較)。
///
/// 空文字列は数値として 0 なので、`$x` の数値が 0 なら真になる。
/// 例: `"0,0,0,0,0" == ''` は真、`"5,1,2" == ''` は偽。
/// 元のコードは「空なら既定値を入れる」つもりでこれを書いているが、
/// 実際には「先頭の数値が 0 なら既定値を入れる」動作になっている。
pub fn num_eq_empty(s: &str) -> bool {
    int(s) == 0
}

/// Perl の `random($n)` (`int(rand(1) * $n)`) 相当。0 以上 `n` 未満を返す。
pub fn random<R: rand::Rng + ?Sized>(rng: &mut R, n: i64) -> i64 {
    if n <= 0 {
        return 0;
    }
    (rng.r#gen::<f64>() * n as f64) as i64
}

/// `htmlEscape` 相当。
pub fn html_escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            _ => out.push(c),
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn int_matches_perl() {
        assert_eq!(int(""), 0);
        assert_eq!(int("42"), 42);
        assert_eq!(int("  7\n"), 7);
        assert_eq!(int("-15"), -15);
        assert_eq!(int("3.9"), 3);
        assert_eq!(int("12abc"), 12);
        assert_eq!(int("abc"), 0);
        assert_eq!(int("0,0,1,1,0"), 0);
        assert_eq!(int("128,0,0"), 128);
    }

    #[test]
    fn num_eq_empty_matches_perl() {
        assert!(num_eq_empty(""));
        assert!(num_eq_empty("0,0,0,0,0"));
        assert!(!num_eq_empty("5,0,0,0,0"));
    }

    #[test]
    fn random_range() {
        let mut rng = rand::thread_rng();
        for _ in 0..1000 {
            let v = random(&mut rng, 27);
            assert!((0..27).contains(&v));
        }
        assert_eq!(random(&mut rng, 0), 0);
    }
}
