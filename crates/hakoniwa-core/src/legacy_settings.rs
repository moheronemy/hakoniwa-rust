//! Perl 版の設定 (`hako-main.cgi` の「各種設定値」) を読み、移植版の [`GameConfig`] にする。
//!
//! 運営していた Perl 版の設定 (ターンの長さ、島の数、掲示板、資金の見せ方、災害の確率、
//! パスワードなど) をそのまま移せるようにする。`hako-main.cgi` を実行はせず、
//! `$名前 = 値;` (`my($名前) = 値;` も) の形の代入を、メインの処理 (`require($jcode)`) の前まで読む。
//! 値は数値と、`'...'` か `"..."` の文字列だけを扱う (式や変数を含むものは読まない)。

use std::collections::HashMap;

use crate::config::{GameConfig, HideMoneyMode};

/// 読み込んだ設定と、読まなかったもの・おかしな値の知らせ
#[derive(Debug, Clone)]
pub struct LegacySettings {
    pub config: GameConfig,
    /// `$HnewGame` (怪獣出現数の保存先。データの変換に使う)
    pub new_game: Option<bool>,
    /// `$HlbbsOldToNew` (旧形式の掲示板を変換するか。データの変換に使う)
    pub lbbs_old_to_new: Option<bool>,
    pub warnings: Vec<String>,
}

/// `hako-main.cgi` の中身 (UTF-8 にしたもの) から設定を読む
pub fn parse(text: &str) -> LegacySettings {
    let values = assignments(text);
    let mut warnings = Vec::new();
    let mut c = GameConfig::default();

    let get = |name: &str| values.get(name).map(String::as_str);
    let int = |name: &str, warnings: &mut Vec<String>| -> Option<i64> {
        let v = get(name)?;
        match v.trim().parse::<f64>() {
            Ok(n) if n.fract() == 0.0 => Some(n as i64),
            _ => {
                warnings.push(format!("${name} の値 {v:?} は整数として読めませんでした"));
                None
            }
        }
    };
    macro_rules! set_int {
        ($field:expr, $name:literal) => {
            if let Some(v) = int($name, &mut warnings) {
                $field = v as _;
            }
        };
    }
    macro_rules! set_bool {
        ($field:expr, $name:literal) => {
            if let Some(v) = int($name, &mut warnings) {
                $field = v != 0;
            }
        };
    }
    macro_rules! set_str {
        ($field:expr, $name:literal) => {
            if let Some(v) = get($name) {
                $field = v.to_string();
            }
        };
    }
    macro_rules! set_opt {
        ($field:expr, $name:literal) => {
            if let Some(v) = get($name) {
                $field = (!v.is_empty()).then(|| v.to_string());
            }
        };
    }

    set_str!(c.title, "Htitle");
    set_int!(c.unit_time, "HunitTime");
    set_int!(c.max_islands, "HmaxIsland");
    set_int!(c.island_size, "HislandSize");
    set_int!(c.command_max, "HcommandMax");
    set_int!(c.log_max, "HlogMax");
    set_int!(c.top_log_turns, "HtopLogTurn");
    set_int!(c.top_view_number, "viewNumber");
    set_int!(c.history_max, "HhistoryMax");
    set_int!(c.hcup_log_max, "HhcMax");
    set_int!(c.backup_every_turns, "HbackupTurn");
    set_int!(c.backup_keep, "HbackupTimes");
    set_int!(c.giveup_turn, "HgiveupTurn");
    set_int!(c.guard_pop, "HguardPop");
    if let Some(v) = int("HhideMoneyMode", &mut warnings) {
        c.hide_money_mode = match v {
            0 => HideMoneyMode::Hidden,
            1 => HideMoneyMode::Visible,
            2 => HideMoneyMode::Rounded,
            _ => {
                warnings.push(format!("$HhideMoneyMode の値 {v} は 0〜2 ではありません"));
                c.hide_money_mode
            }
        };
    }
    set_bool!(c.debug, "Hdebug");
    set_bool!(c.love_peace, "lovePeace");
    set_bool!(c.another_mode, "anothermood");
    set_int!(c.auction_prize_streak, "aucshouhin");
    set_int!(c.auction_hall_of_fame, "aucdendou");
    set_bool!(c.reject_duplicate_ip, "IPcut");

    set_bool!(c.lbbs.enabled, "HuseLbbs");
    set_int!(c.lbbs.max, "HlbbsMax");
    set_bool!(c.lbbs.allow_anonymous, "HlbbsAnon");
    set_bool!(c.lbbs.show_speaker, "HlbbsSpeaker");
    set_int!(c.lbbs.cost_public, "HlbbsMoneyPublic");
    set_int!(c.lbbs.cost_secret, "HlbbsMoneySecret");

    set_int!(c.initial_money, "HinitialMoney");
    set_int!(c.initial_food, "HinitialFood");
    set_int!(c.tree_value, "HtreeValue");
    set_int!(c.cost_change_name, "HcostChangeName");
    if let Some(v) = get("HeatenFood") {
        match v.trim().parse::<f64>() {
            Ok(n) => c.eaten_food = n,
            Err(_) => warnings.push(format!("$HeatenFood の値 {v:?} は数として読めませんでした")),
        }
    }
    set_int!(c.oil_money, "HoilMoney");
    set_int!(c.oil_ratio, "HoilRatio");
    set_int!(c.max_exp_point, "HmaxExpPoint");
    set_int!(c.turn_prize_unit, "HturnPrizeUnit");
    set_bool!(c.defence_self_destruct, "HdBaseAuto");

    set_str!(c.units.money, "HunitMoney");
    set_str!(c.units.food, "HunitFood");
    set_str!(c.units.pop, "HunitPop");
    set_str!(c.units.area, "HunitArea");
    set_str!(c.units.tree, "HunitTree");
    set_str!(c.units.monster, "HunitMonster");

    set_int!(c.disaster.earthquake, "HdisEarthquake");
    set_int!(c.disaster.tsunami, "HdisTsunami");
    set_int!(c.disaster.typhoon, "HdisTyphoon");
    set_int!(c.disaster.meteo, "HdisMeteo");
    set_int!(c.disaster.huge_meteo, "HdisHugeMeteo");
    set_int!(c.disaster.eruption, "HdisEruption");
    set_int!(c.disaster.fire, "HdisFire");
    set_int!(c.disaster.maizo, "HdisMaizo");
    set_int!(c.disaster.fall_border, "HdisFallBorder");
    set_int!(c.disaster.falldown, "HdisFalldown");

    set_int!(c.monster.borders[0], "HdisMonsBorder1");
    set_int!(c.monster.borders[1], "HdisMonsBorder2");
    set_int!(c.monster.borders[2], "HdisMonsBorder3");
    set_int!(c.monster.borders[3], "HdisMonsBorder4");
    set_int!(c.monster.appearance_rate, "HdisMonster");
    set_int!(c.monster.levels[0], "HmonsterLevel1");
    set_int!(c.monster.levels[1], "HmonsterLevel2");
    set_int!(c.monster.levels[2], "HmonsterLevel3");
    set_int!(c.monster.levels[3], "HmonsterLevel4");
    set_int!(c.monster.number, "HmonsterNumber");
    set_int!(c.monster.defence, "HmonsterDefence");
    set_int!(c.monument_number, "HmonumentNumber");
    set_int!(c.ship_number, "HfuneNumber");

    set_opt!(c.passwords.master, "masterPassword");
    set_opt!(c.passwords.special, "HspecialPassword");
    set_opt!(c.passwords.shuto, "HshutoPassword");
    set_opt!(c.passwords.ip, "HipPassword");
    set_opt!(c.passwords.omamori, "HomamoriPassword");
    set_opt!(c.passwords.ijiri, "HijiriPassword");

    set_bool!(c.survey.enabled, "AnkeitoOnOff");
    set_str!(c.survey.description, "AnkeitoSetumei");
    set_str!(c.survey.question, "AnkeitoShitumon0");
    let choices: Vec<String> = (1..=5)
        .filter_map(|i| get(&format!("AnkeitoShitumon{i}")).map(str::to_string))
        .collect();
    if !choices.is_empty() {
        c.survey.choices = choices;
    }

    let new_game = int("HnewGame", &mut warnings).map(|v| v != 0);
    let lbbs_old_to_new = int("HlbbsOldToNew", &mut warnings).map(|v| v != 0);
    LegacySettings {
        config: c,
        new_game,
        lbbs_old_to_new,
        warnings,
    }
}

/// `$名前 = 値;` の代入を集める (後の代入が勝つ。Perl と同じ)
fn assignments(text: &str) -> HashMap<String, String> {
    let mut out = HashMap::new();
    let mut rest = text;
    loop {
        // メインの処理の手前まで (設定値はその前にある)
        let line_end = rest.find('\n').map_or(rest.len(), |i| i + 1);
        let line = &rest[..line_end];
        if line.trim_start().starts_with("require($jcode)") {
            break;
        }
        if let Some((name, value, used)) = assignment(rest) {
            out.insert(name, value);
            rest = &rest[used..];
            continue;
        }
        if line_end == 0 || line_end >= rest.len() {
            break;
        }
        rest = &rest[line_end..];
    }
    out
}

/// 行頭の `$name = value;` か `my($name) = value;` を読む。(名前, 値, 読んだバイト数)
fn assignment(s: &str) -> Option<(String, String, usize)> {
    let t = s.trim_start_matches([' ', '\t']);
    let (t, my) = match t.strip_prefix("my(") {
        Some(r) => (r, true),
        None => (t, false),
    };
    let t = t.strip_prefix('$')?;
    let name_len = t
        .find(|c: char| !(c.is_ascii_alphanumeric() || c == '_'))
        .unwrap_or(t.len());
    if name_len == 0 {
        return None;
    }
    let name = &t[..name_len];
    let mut r = &t[name_len..];
    if my {
        r = r.strip_prefix(')')?;
    }
    let r2 = r.trim_start_matches([' ', '\t']);
    let r2 = r2.strip_prefix('=')?;
    if r2.starts_with('=') || r2.starts_with('~') {
        return None;
    }
    let v = r2.trim_start_matches([' ', '\t']);
    let consumed_before = s.len() - v.len();
    let (value, len) = match v.chars().next()? {
        q @ ('\'' | '"') => {
            let body = &v[1..];
            let mut end = None;
            let mut escaped = false;
            for (i, ch) in body.char_indices() {
                if escaped {
                    escaped = false;
                } else if ch == '\\' {
                    escaped = true;
                } else if ch == q {
                    end = Some(i);
                    break;
                }
            }
            let end = end?;
            let raw = &body[..end];
            let value = if q == '\'' {
                raw.replace("\\'", "'").replace("\\\\", "\\")
            } else {
                // 変数の埋め込みを含む文字列は読まない
                if raw.contains('$') || raw.contains('@') {
                    return None;
                }
                raw.replace("\\\"", "\"")
                    .replace("\\n", "\n")
                    .replace("\\\\", "\\")
            };
            (value, 1 + end + 1)
        }
        _ => {
            let end = v.find(';')?;
            let raw = v[..end].trim();
            raw.parse::<f64>().ok()?;
            (raw.to_string(), end)
        }
    };
    let after = &v[len..];
    if !after.trim_start().starts_with(';') {
        return None;
    }
    Some((name.to_string(), value, consumed_before + len))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reads_assignments() {
        let text = "my($masterPassword) = 'm';\n$HunitTime = 3600; # 1時間\n$Htitle = \"箱庭\";\n\
                    $HeatenFood = 0.5;\n$HhideMoneyMode = 1;\n$AnkeitoSetumei = \"一行目\n二行目\";\n\
                    $HuseLbbs = 0;\n$HthisFile = \"$baseDir/x.cgi\";\nrequire($jcode);\n$HunitTime = 1;\n";
        let s = parse(text);
        let c = &s.config;
        assert_eq!(c.passwords.master.as_deref(), Some("m"));
        assert_eq!(c.unit_time, 3600);
        assert_eq!(c.title, "箱庭");
        assert_eq!(c.eaten_food, 0.5);
        assert_eq!(c.hide_money_mode, HideMoneyMode::Visible);
        assert_eq!(c.survey.description, "一行目\n二行目");
        assert!(!c.lbbs.enabled);
        assert!(s.warnings.is_empty(), "{:?}", s.warnings);
    }

    /// 配布された hako-main.cgi は、移植版の既定値と同じ設定になる (マスターパスワードなどを除く)
    #[test]
    fn distributed_settings_match_defaults() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../../hako-r-a_FE/hako-main.cgi");
        let bytes = std::fs::read(path).unwrap();
        let (text, _, _) = encoding_rs::EUC_JP.decode(&bytes);
        let s = parse(&text.replace("\r\n", "\n"));
        assert!(s.warnings.is_empty(), "{:?}", s.warnings);
        let mut c = s.config;
        assert_eq!(c.passwords.master.as_deref(), Some("uhusnuvnurkanjhfh"));
        c.passwords = Default::default();
        c.survey = Default::default();
        let d = GameConfig {
            survey: Default::default(),
            ..Default::default()
        };
        assert_eq!(c, d);
        assert_eq!(s.new_game, Some(true));
    }
}
