//! Hakoniwa R.A. (箱庭諸島2 ver2.30 改造版) の Rust 移植のコア。
//!
//! - [`config`] — ゲーム設定 (Perl 版の設定値)
//! - [`tables`] — 地形・計画・怪獣などの定義表 (Perl 版から自動生成)
//! - [`model`] — セーブデータのモデル
//! - [`storage`] — 移植版のセーブデータ (JSON) の読み書き
//! - [`land`] — 地形の名前と周囲の数え上げ
//! - [`legacy`] — Perl 版のセーブデータの読み込み
//! - [`turn`] — ターン処理
//! - [`log`] — ターン処理のログ
//! - [`perl`] — Perl の挙動を再現するヘルパー
//!
//! ゲームのルールは移植の途中。進み具合は `docs/PORTING.md` を参照。

pub mod config;
pub mod land;
pub mod legacy;
pub mod log;
pub mod model;
pub mod perl;
pub mod storage;
pub mod tables;
pub mod turn;

pub use config::GameConfig;
pub use model::GameState;
