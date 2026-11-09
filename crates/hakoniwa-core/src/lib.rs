//! Hakoniwa R.A. (箱庭諸島2 ver2.30 改造版) の Rust 移植のコア。
//!
//! - [`config`] — ゲーム設定 (Perl 版の設定値)
//! - [`tables`] — 地形・計画・怪獣などの定義表 (Perl 版から自動生成)
//! - [`model`] — セーブデータのモデル
//! - [`storage`] — 移植版のセーブデータ (JSON) の読み書き
//! - [`legacy`] — Perl 版のセーブデータの読み込み
//! - [`perl`] — Perl の挙動を再現するヘルパー
//!
//! ゲームのルール (ターン処理・計画の実行など) はまだ移植していない。
//! 進め方は `docs/PORTING.md` を参照。

pub mod config;
pub mod legacy;
pub mod model;
pub mod perl;
pub mod storage;
pub mod tables;

pub use config::GameConfig;
pub use model::GameState;
