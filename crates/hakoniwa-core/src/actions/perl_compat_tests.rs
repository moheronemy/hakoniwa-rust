//! 画面からの操作を、元の Perl CGI に同じ操作を送った結果と突き合わせる。
//!
//! 期待値は `tools/perl-harness/run_cgi.py tests/fixtures/cgi/<名前>.json` が作る
//! `tests/fixtures/cgi/<名前>/{before,after}` (Perl 形式のデータ)。`before` を読み込んで
//! 移植版の操作を加え、`after` を読み込んだものと比べる。

use std::path::{Path, PathBuf};

use rand::rngs::mock::StepRng;
use serde_json::Value;

use crate::GameConfig;
use crate::legacy::{self, ImportOptions};
use crate::model::GameState;

pub(crate) fn cgi_dir() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/cgi")
}

/// 操作の入力 (`<名前>.json`)
pub(crate) struct Case {
    /// `time()` の値
    pub now: i64,
    /// `rand()` を固定した値を作る乱数
    pub rng: StepRng,
    /// 送った操作 (フォームの値は UTF-8 の文字列)
    pub requests: Vec<Value>,
}

impl Case {
    /// `n` 番目の操作のフォームの値 (無ければ空)
    pub fn form(&self, n: usize, key: &str) -> String {
        self.requests[n]["form"][key]
            .as_str()
            .unwrap_or_default()
            .to_string()
    }

    /// `n` 番目の操作の接続元 (省略時は 10.0.0.1)
    pub fn addr(&self, n: usize) -> String {
        self.requests[n]["addr"]
            .as_str()
            .unwrap_or("10.0.0.1")
            .to_string()
    }
}

fn import(dir: &Path) -> GameState {
    legacy::import_dir(dir, &ImportOptions::default(), &mut StepRng::new(0, 0))
        .unwrap_or_else(|e| panic!("{}: {e}", dir.display()))
        .state
}

/// `rand()` を `0.<digits>` に固定する乱数 (rand 0.8 の f64 は u64 の上位 53 ビット × 2^-53)
pub(crate) fn pinned_rng(digits: &str) -> StepRng {
    let r: f64 = format!("0.{digits}").parse().unwrap();
    let mantissa = r * (1u64 << 53) as f64;
    assert_eq!(mantissa.fract(), 0.0, "0.{digits} is not representable");
    StepRng::new((mantissa as u64) << 11, 0)
}

/// `name` の操作を移植版で `apply` して、Perl 版の結果と比べる。
/// `apply` は読み込んだ `before` の状態を書き換える。比べないパス (JSON Pointer の前方一致) を
/// `ignore` に渡せる (パスワードの保存形式のように、わざと変えたもの)
pub(crate) fn check_case(
    name: &str,
    ignore: &[&str],
    apply: impl FnOnce(&mut GameState, &GameConfig, &mut Case),
) {
    let dir = cgi_dir().join(name);
    let json: Value = serde_json::from_str(
        &std::fs::read_to_string(cgi_dir().join(format!("{name}.json"))).unwrap(),
    )
    .unwrap();
    let mut game = import(&dir.join("before"));
    let mut case = Case {
        now: json["time"].as_i64().unwrap_or(game.world.last_time + 1),
        rng: pinned_rng(json["rand"].as_str().unwrap_or("0")),
        requests: json["requests"].as_array().cloned().unwrap_or_default(),
    };
    let config = GameConfig::default();
    apply(&mut game, &config, &mut case);

    let want = serde_json::to_value(import(&dir.join("after"))).unwrap();
    let got = serde_json::to_value(&game).unwrap();
    let mut diffs = Vec::new();
    diff(&want, &got, String::new(), ignore, &mut diffs);
    assert!(
        diffs.is_empty(),
        "{name}: {} differences\n{}",
        diffs.len(),
        diffs[..diffs.len().min(40)].join("\n")
    );
}

/// JSON の違いを `path: Perl の値 != 移植版の値` の形で集める
pub(crate) fn diff(
    want: &Value,
    got: &Value,
    path: String,
    ignore: &[&str],
    out: &mut Vec<String>,
) {
    if ignore.iter().any(|p| path.starts_with(p)) {
        return;
    }
    match (want, got) {
        (Value::Object(a), Value::Object(b)) => {
            for k in a.keys().chain(b.keys().filter(|k| !a.contains_key(*k))) {
                let (x, y) = (
                    a.get(k).unwrap_or(&Value::Null),
                    b.get(k).unwrap_or(&Value::Null),
                );
                diff(x, y, format!("{path}/{k}"), ignore, out);
            }
        }
        (Value::Array(a), Value::Array(b)) if a.len() == b.len() => {
            for (i, (x, y)) in a.iter().zip(b).enumerate() {
                diff(x, y, format!("{path}/{i}"), ignore, out);
            }
        }
        _ if want != got => {
            let s = |v: &Value| {
                let t = v.to_string();
                if t.len() > 200 {
                    format!("{}…", &t[..t.floor_char_boundary(200)])
                } else {
                    t
                }
            };
            out.push(format!("{path}: perl {} != rust {}", s(want), s(got)));
        }
        _ => {}
    }
}
