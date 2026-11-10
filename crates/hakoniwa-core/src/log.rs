//! ターン処理のログ。
//!
//! Perl 版の `logOut` / `logLate` / `logSecret` / `logHistory` / `logFlush` の移植。
//! 文面は Perl 版と同じ HTML (タグも同じ) で作る。Perl 版から変換したログと
//! 新しく作るログを同じように扱えるようにするため。
//!
//! 文面のテンプレート (`log*` 関数、Perl 版で 281 個) は、移植した処理が使うものから
//! 順に [`msg`] に追加していく。

use crate::model::{LogEntry, TurnMessage};

/// 文字の装飾 (`$HtagXxx_` と `$H_tagXxx`)
pub mod tags {
    pub const NAME: (&str, &str) = ("<FONT COLOR=\"#a06040\"><B>", "</B></FONT>");
    pub const NAME2: (&str, &str) = ("<FONT COLOR=\"#808080\"><B>", "</B></FONT>");
    pub const NUMBER: (&str, &str) = ("<FONT COLOR=\"#800000\"><B>", "</B></FONT>");
    pub const COM_NAME: (&str, &str) = ("<FONT COLOR=\"#d08000\"><B>", "</B></FONT>");
    pub const DISASTER: (&str, &str) = ("<FONT COLOR=\"#ff0000\"><B>", "</B></FONT>");

    /// `${HtagName_}...${H_tagName}`
    pub fn wrap(tag: (&str, &str), s: &str) -> String {
        format!("{}{}{}", tag.0, s, tag.1)
    }
}

/// 1 ターン分のログを溜めておく
#[derive(Debug, Default)]
pub struct TurnLog {
    normal: Vec<LogEntry>,
    late: Vec<LogEntry>,
    secret: Vec<LogEntry>,
    /// 発見の記録 (`hakojima.his` に追記するもの)
    pub history: Vec<TurnMessage>,
}

impl TurnLog {
    fn entry(
        secret: bool,
        turn: i64,
        message: String,
        id1: Option<i64>,
        id2: Option<i64>,
    ) -> LogEntry {
        LogEntry {
            secret,
            turn,
            island1: id1,
            island2: id2,
            message,
        }
    }

    /// `logOut`
    pub fn out(&mut self, turn: i64, message: String, id1: Option<i64>, id2: Option<i64>) {
        self.normal
            .push(Self::entry(false, turn, message, id1, id2));
    }

    /// `logLate` (遅延ログ)
    pub fn late(&mut self, turn: i64, message: String, id1: Option<i64>, id2: Option<i64>) {
        self.late.push(Self::entry(false, turn, message, id1, id2));
    }

    /// `logSecret` (機密ログ)
    pub fn secret(&mut self, turn: i64, message: String, id1: Option<i64>, id2: Option<i64>) {
        self.secret.push(Self::entry(true, turn, message, id1, id2));
    }

    /// `logHistory`
    pub fn history(&mut self, turn: i64, message: String) {
        self.history.push(TurnMessage { turn, message });
    }

    /// ここまでのログを `flush` と同じ順で複製する (テスト用)
    pub fn snapshot(&self) -> (Vec<LogEntry>, Vec<TurnMessage>) {
        let entries = self
            .secret
            .iter()
            .rev()
            .chain(self.late.iter().rev())
            .chain(self.normal.iter().rev())
            .cloned()
            .collect();
        (entries, self.history.clone())
    }

    /// `logFlush`: 機密・遅延・通常の順に、それぞれ新しいものから並べる
    pub fn flush(self) -> (Vec<LogEntry>, Vec<TurnMessage>) {
        let entries = self
            .secret
            .into_iter()
            .rev()
            .chain(self.late.into_iter().rev())
            .chain(self.normal.into_iter().rev())
            .collect();
        (entries, self.history)
    }
}

/// ログの文面。関数名は Perl 版の `log*` に対応する
pub mod msg {
    use super::tags::{self, wrap};

    fn island(name: &str) -> String {
        wrap(tags::NAME, &format!("{name}島"))
    }

    /// `logNoMoney`
    pub fn no_money(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、資金不足のため中止されました。",
            island(name),
            wrap(tags::COM_NAME, com_name)
        )
    }

    /// `logNoFood`
    pub fn no_food(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、備蓄食料不足のため中止されました。",
            island(name),
            wrap(tags::COM_NAME, com_name)
        )
    }

    /// `logEnjo`
    pub fn enjo(name: &str, amount: &str) -> String {
        format!(
            "開発進行委員会から{}に<B>{amount}</B>の援助金が支給されたようです！",
            island(name)
        )
    }

    /// `logStarve2`
    pub fn starve2(name: &str) -> String {
        format!(
            "{}の{}しています！！",
            island(name),
            wrap(tags::DISASTER, "電力が不足")
        )
    }

    /// `logGiveup` (通常ログ)
    pub fn giveup(name: &str) -> String {
        format!("{}は放棄され、<B>無人島</B>になりました。", island(name))
    }

    /// `logGiveup` (記録ログ)
    pub fn giveup_history(name: &str) -> String {
        format!("{}、放棄され<B>無人島</B>となる。", island(name))
    }

    /// `logDead` (通常ログ)
    pub fn dead(name: &str) -> String {
        format!(
            "{}から人がいなくなり、<B>無人島</B>になりました。",
            island(name)
        )
    }

    /// `logDead` (記録ログ)
    pub fn dead_history(name: &str) -> String {
        format!("{}、人がいなくなり<B>無人島</B>となる。", island(name))
    }

    /// `logPrizet` (通常ログ)
    pub fn prize(name: &str, prize_name: &str) -> String {
        format!("{}が<B>{prize_name}</B>を受賞しました。", island(name))
    }

    /// `logPrizet` (記録ログ)
    pub fn prize_history(name: &str, prize_name: &str, amount: &str) -> String {
        format!(
            "{}、<B>{prize_name}</B>を受賞（賞金<B>{amount}</B>)",
            island(name)
        )
    }

    /// `logSinMoney` / `logJinMoney`。島名の後ろにグローバル変数 `$point` を挟む
    /// (同じターンの前の処理が代入した座標が残っていれば、それが出る。Perl 版のまま)
    pub fn shrine_money(name: &str, point: &str, building: &str, amount: &str) -> String {
        format!(
            "{}の<B>{building}</B>で祝いの祭りが行われ、<B>{amount}</B>の収益が上がりました。",
            wrap(tags::NAME, &format!("{name}島{point}"))
        )
    }

    /// 未移植の計画が実行されたとき (移植作業中だけのもの。Perl 版には無い)
    pub fn not_ported(name: &str, com_name: &str) -> String {
        format!(
            "{}で予定されていた{}は、移植作業中のため実行されませんでした。",
            island(name),
            wrap(tags::COM_NAME, com_name)
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn flush_order_matches_perl() {
        let mut log = TurnLog::default();
        log.out(1, "n1".into(), Some(1), None);
        log.secret(1, "s1".into(), Some(1), None);
        log.out(1, "n2".into(), Some(1), None);
        log.late(1, "l1".into(), Some(1), None);
        log.secret(1, "s2".into(), Some(1), None);
        let (entries, _) = log.flush();
        let order: Vec<_> = entries.iter().map(|e| e.message.as_str()).collect();
        assert_eq!(order, ["s2", "s1", "l1", "n2", "n1"]);
        assert!(entries[0].secret && !entries[2].secret);
    }

    #[test]
    fn message_matches_perl_html() {
        assert_eq!(
            msg::giveup_history("テスト"),
            "<FONT COLOR=\"#a06040\"><B>テスト島</B></FONT>、放棄され<B>無人島</B>となる。"
        );
    }
}
