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

/// Perl の `random($n)` (`int(rand(1) * $n)`) 相当。`n` が正なら 0 以上 `n` 未満。
///
/// Perl 版は `n` が 0 以下でも乱数を 1 つ使う (負なら 0 以下の値を返す) ので、
/// 乱数の並びをそろえるため移植版も必ず 1 つ使う
pub fn random<R: rand::Rng + ?Sized>(rng: &mut R, n: i64) -> i64 {
    trunc(rng.r#gen::<f64>() * n as f64)
}

/// `$s =~ /^([0-9]*),([0-9]*),...$/` (N 個) 相当。
///
/// マッチすれば各欄を数値にして返す (空欄は 0)。欄の数が違う、数字以外が混じるなどで
/// マッチしなければ `None`。Perl 版はマッチ失敗時に前回の `$1`.. や代入先の変数を
/// そのまま使うので、呼び出し側は [`Captures::update`] で「前回値」を保持する。
pub fn fields<const N: usize>(s: &str) -> Option<[i64; N]> {
    // Perl の `$` は末尾の改行の直前にもマッチする
    let s = s.strip_suffix('\n').unwrap_or(s);
    let mut out = [0i64; N];
    let mut parts = s.split(',');
    for slot in out.iter_mut() {
        let p = parts.next()?;
        if !p.bytes().all(|b| b.is_ascii_digit()) {
            return None;
        }
        *slot = int(p);
    }
    if parts.next().is_some() {
        return None;
    }
    Some(out)
}

/// 数値をカンマでつないで複合値の文字列にする (`"$a,$b,$c"` 相当)。
pub fn join(values: &[i64]) -> String {
    values
        .iter()
        .map(i64::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

/// Perl のグローバル変数に正規表現の結果を代入する箇所の再現。
///
/// `($a, $b, ...) = ($1, $2, ...)` は、マッチに失敗すると前回の値が残る。
/// 同じ変数名の組を複数の関数・複数の島で使い回しているので、ターン処理の間は値を持ち越す。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Captures<const N: usize>(pub [i64; N]);

impl<const N: usize> Default for Captures<N> {
    fn default() -> Self {
        Self([0; N])
    }
}

impl<const N: usize> Captures<N> {
    /// `s` がマッチすれば値を更新する。更新後 (失敗時は前回) の値を返す
    pub fn update(&mut self, s: &str) -> [i64; N] {
        if let Some(v) = fields::<N>(s) {
            self.0 = v;
        }
        self.0
    }
}

/// Perl の `int()` を浮動小数点の式に適用する (0 方向への切り捨て)
pub fn trunc(x: f64) -> i64 {
    if x.is_nan() { 0 } else { x.trunc() as i64 }
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
    fn fields_match_perl_regex() {
        assert_eq!(fields::<3>("1,22,333"), Some([1, 22, 333]));
        assert_eq!(fields::<3>("1,,3"), Some([1, 0, 3]));
        assert_eq!(fields::<3>("1,2"), None);
        assert_eq!(fields::<3>("1,2,3,4"), None);
        assert_eq!(fields::<3>("1,-2,3"), None);
        assert_eq!(fields::<1>(""), Some([0]));
        assert_eq!(join(&[1, 0, 3]), "1,0,3");
    }

    #[test]
    fn captures_keep_previous_on_failure() {
        let mut c = Captures::<2>::default();
        assert_eq!(c.update("bad"), [0, 0]);
        assert_eq!(c.update("4,5"), [4, 5]);
        assert_eq!(c.update("bad"), [4, 5]);
    }

    #[test]
    fn random_range() {
        let mut rng = rand::thread_rng();
        for _ in 0..1000 {
            let v = random(&mut rng, 27);
            assert!((0..27).contains(&v));
        }
        assert_eq!(random(&mut rng, 0), 0);
        for _ in 0..100 {
            assert!((-4..=0).contains(&random(&mut rng, -5)));
        }
    }
}
