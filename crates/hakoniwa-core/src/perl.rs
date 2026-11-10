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

/// 文字列を数値として使ったときの Perl の値 (`$s == 0` などの比較に使う)。
///
/// 先頭の空白を読み飛ばし、符号・数字・小数部・指数部の並びを読む (`"12abc"` は 12、
/// `"0.5"` は 0.5、`"東京"` は 0)。`inf`/`infinity`/`nan` (大文字小文字を問わない) は
/// 無限大・NaN になる
pub fn num(s: &str) -> f64 {
    let s = s.trim_start_matches([' ', '\t', '\n', '\r', '\x0b', '\x0c']);
    let b = s.as_bytes();
    let mut i = 0;
    if matches!(b.first(), Some(b'+' | b'-')) {
        i = 1;
    }
    let neg = b.first() == Some(&b'-');
    let rest = s[i..].to_ascii_lowercase();
    if rest.starts_with("inf") {
        return if neg {
            f64::NEG_INFINITY
        } else {
            f64::INFINITY
        };
    }
    if rest.starts_with("nan") {
        return f64::NAN;
    }
    let digits = |from: usize| b[from..].iter().take_while(|c| c.is_ascii_digit()).count();
    let int_len = digits(i);
    let mut end = i + int_len;
    let mut frac_len = 0;
    if b.get(end) == Some(&b'.') {
        frac_len = digits(end + 1);
        if int_len + frac_len > 0 {
            end += 1 + frac_len;
        }
    }
    if int_len + frac_len == 0 {
        return 0.0;
    }
    if matches!(b.get(end), Some(b'e' | b'E')) {
        let mut j = end + 1;
        if matches!(b.get(j), Some(b'+' | b'-')) {
            j += 1;
        }
        let exp_len = digits(j);
        if exp_len > 0 {
            end = j + exp_len;
        }
    }
    s[..end].parse().unwrap_or(0.0)
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
    fields_raw::<N>(s).map(|v| v.map(int))
}

/// [`fields`] の欄を文字列のまま返す (`"007"` は `"007"`、空欄は `""`)
pub fn fields_raw<const N: usize>(s: &str) -> Option<[&str; N]> {
    // Perl の `$` は末尾の改行の直前にもマッチする
    let s = s.strip_suffix('\n').unwrap_or(s);
    let mut out = [""; N];
    let mut parts = s.split(',');
    for slot in out.iter_mut() {
        let p = parts.next()?;
        if !p.bytes().all(|b| b.is_ascii_digit()) {
            return None;
        }
        *slot = p;
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

/// Perl の `$1`, `$2`, ... (いまのスコープから見て最後に成功したマッチの値)。
///
/// Perl では正規表現のマッチに失敗しても `$1`.. は変わらず、**最後に成功したマッチ**の値のまま。
/// しかもその値はブロック単位の動的スコープで、ブロック (や sub) を出ると入る前の値に戻る。
/// サブルーチンの中からは呼び出し元のマッチの値が見える。
///
/// 移植版では Perl の sub 1 回分 (またはブロック) ごとに `MatchScope` を持ち、
/// 入れ子のブロックでは `clone()` したものを使って、ブロックを出たら捨てる。
/// `$n` が最後のマッチに無ければ未定義なので 0 にする (文字列として埋め込むと Perl は空になる)。
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct MatchScope {
    caps: Vec<i64>,
    /// `$1`.. の文字列 (画面に埋め込むとき用。数字の並びのまま、`""` もある)
    texts: Vec<String>,
}

impl MatchScope {
    /// `$s =~ /^([0-9]*),...$/; ($a, $b, ...) = ($1, $2, ...);` の右辺。
    /// 一致すればその値 (そして以後の `$1`..)、しなければ最後に成功したマッチの値
    pub fn fields<const N: usize>(&mut self, s: &str) -> [i64; N] {
        match self.try_fields::<N>(s) {
            Some(v) => v,
            None => self.current(),
        }
    }

    /// 一致したかどうかが要るとき (`if ($s =~ /.../)`)。一致すれば `$1`.. を更新する
    pub fn try_fields<const N: usize>(&mut self, s: &str) -> Option<[i64; N]> {
        let raw = fields_raw::<N>(s)?;
        self.texts = raw.iter().map(|t| t.to_string()).collect();
        let v = raw.map(int);
        self.caps = v.to_vec();
        Some(v)
    }

    /// [`MatchScope::fields`] の文字列版: 画面に `"$a"` と埋め込むときの値。
    /// 最後のマッチに無い `$n` (未定義) は空文字列になる
    pub fn fields_text<const N: usize>(&mut self, s: &str) -> [String; N] {
        self.try_fields::<N>(s);
        self.current_text()
    }

    /// いまの `$1`..`$N`
    pub fn current<const N: usize>(&self) -> [i64; N] {
        std::array::from_fn(|i| self.caps.get(i).copied().unwrap_or(0))
    }

    /// いまの `$1`..`$N` の文字列 (未定義は空文字列)
    pub fn current_text<const N: usize>(&self) -> [String; N] {
        std::array::from_fn(|i| self.texts.get(i).cloned().unwrap_or_default())
    }

    /// 数字の欄に限らない正規表現が成功したとき (`$1`.. をその値にする)
    pub fn set(&mut self, caps: Vec<i64>) {
        self.texts = caps.iter().map(i64::to_string).collect();
        self.caps = caps;
    }

    /// [`MatchScope::set`] の文字列版 (数値としては [`int`] で読んだ値)
    pub fn set_text(&mut self, texts: Vec<String>) {
        self.caps = texts.iter().map(|t| int(t)).collect();
        self.texts = texts;
    }
}

/// 正規表現の結果を代入する先の Perl のグローバル変数の組 (`$s00`..`$s30` など)。
/// 島や処理をまたいで値が残る
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Captures<const N: usize>(pub [i64; N]);

impl<const N: usize> Default for Captures<N> {
    fn default() -> Self {
        Self([0; N])
    }
}

impl<const N: usize> Captures<N> {
    /// `($a, $b, ...) = ($1, $2, ...)`: 値を代入して返す
    pub fn assign(&mut self, values: [i64; N]) -> [i64; N] {
        self.0 = values;
        values
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

/// `cgiInput` が入力の文字に加える加工: 制御文字 (0x00〜0x1f) とカンマを取り除く。
///
/// Perl 版は値を URL デコードしてから `KEY=([^\&]*)\&` で切り出すので、値の中の `&` から
/// 後ろが消える。これは入力の読み取りの不具合なので移植版では再現しない
/// (突き合わせのデータには `&` を入れない)
pub fn cgi_text(s: &str) -> String {
    s.chars().filter(|&c| c >= ' ' && c != ',').collect()
}

/// `cutColumn($s, $c)`: EUC-JP のバイト数 (半角 1、全角 2) で `c` 桁に切り詰める。
/// 全角の文字で `c` を 1 桁超えることがある (Perl 版のまま)
pub fn cut_column(s: &str, c: usize) -> String {
    let width = |ch: char| if ch.is_ascii() { 1 } else { 2 };
    if s.chars().map(width).sum::<usize>() <= c {
        return s.to_string();
    }
    let mut out = String::new();
    let mut count = 0;
    let mut chars = s.chars();
    while count < c {
        match chars.next() {
            Some(ch) => {
                out.push(ch);
                count += width(ch);
            }
            None => break,
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
    fn num_matches_perl() {
        assert_eq!(num(""), 0.0);
        assert_eq!(num("東京シティー"), 0.0);
        assert_eq!(num("555"), 555.0);
        assert_eq!(num(" 12abc"), 12.0);
        assert_eq!(num("0.5"), 0.5);
        assert_eq!(num("-.5x"), -0.5);
        assert_eq!(num("1e3"), 1000.0);
        assert_eq!(num("1e"), 1.0);
        assert_eq!(num("."), 0.0);
        assert_eq!(num("+7"), 7.0);
        assert!(num("NaN").is_nan());
        assert_eq!(num("-Infinity"), f64::NEG_INFINITY);
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
    fn failed_match_uses_last_successful_match() {
        let mut m = MatchScope::default();
        assert_eq!(m.fields::<2>("bad"), [0, 0]);
        assert_eq!(m.fields::<3>("4,5,6"), [4, 5, 6]);
        // 失敗すると、別の正規表現でも最後に成功したマッチの $1.. になる
        assert_eq!(m.fields::<2>("-1,2"), [4, 5]);
        assert_eq!(m.fields::<4>("x"), [4, 5, 6, 0]);
        // 入れ子のブロックで成功しても、ブロックを出れば元に戻る
        {
            let mut inner = m.clone();
            assert_eq!(inner.fields::<1>("9"), [9]);
        }
        assert_eq!(m.current::<1>(), [4]);
    }

    #[test]
    fn match_texts_keep_the_digits_and_undefined_is_empty() {
        let mut m = MatchScope::default();
        assert_eq!(m.fields_text::<3>("007,,3"), ["007", "", "3"]);
        assert_eq!(m.current::<3>(), [7, 0, 3]);
        // 失敗すると最後のマッチ。そこに無い $4 は未定義 (空)
        assert_eq!(m.fields_text::<4>("-1,2,3,4"), ["007", "", "3", ""]);
        m.set_text(vec!["5".into(), "12,3,".into()]);
        assert_eq!(m.current::<2>(), [5, 12]);
        assert_eq!(m.current_text::<2>(), ["5", "12,3,"]);
        assert_eq!(fields_raw::<2>("1,02"), Some(["1", "02"]));
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

    #[test]
    fn cut_column_counts_euc_bytes() {
        assert_eq!(cut_column("abc", 5), "abc");
        assert_eq!(cut_column("あいうえお", 4), "あい");
        // 全角で 1 桁はみ出す (Perl 版のまま)
        assert_eq!(cut_column("aあいう", 4), "aあい");
        assert_eq!(cgi_text("a,b\tc\nd"), "abcd");
    }
}
