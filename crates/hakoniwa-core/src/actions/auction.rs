//! ハコオク (Hakoniwa Auction) の入札 (`auctionMain`、hako-map.cgi 871–1055)。
//!
//! 開発画面の「入札する」ボタン (`AuctionButton<島ID>`) で送られる。入力は品番
//! (`AUCNUMBER`、1〜3) と上乗せする金額 (`AMOUNT`、兆円。フォームは 1〜99 を出す)。
//!
//! 出品の枠 (`World::auction_lots`) は `"品番,値,状態,最高額,最高額の島"`。入札すると
//! 枠の最高額が上がり、状態が 0 に戻り、入札した島の `auc1`〜`auc3` (枠ごと) にその額が入る。
//! 枠の「最高額の島」は入札では変わらない (Perl 版のまま。誰がトップかは各島の `auc1`〜`auc3` で決まる)。
//! お金はここでは動かない (落札はターンの処理)。
//!
//! 出品 (島の出品) は画面の操作ではなく、計画 (オークション出品) としてターンで行われる。
//! 画面の「(出品可能)」「(入札不可)」は表示だけで、入札の処理はそれを確かめない (Perl 版のまま)。

use rand::Rng;

use crate::GameConfig;
use crate::model::GameState;
use crate::perl::{self, MatchScope, cgi_text, num, num_to_string};

use super::{ActionError, island_index};

/// `auctionMain`: 品番 `lot` (`AUCNUMBER`) の出品に、いまの最高額 + `amount` (`AMOUNT`、兆円) で入札する。
///
/// `id` はログインで確かめた島。`lot` と `amount` はフォームの文字列のまま渡す
/// (Perl 版は数値として読むので、`"1.5"` や `"-8"` も通る。負の額で最高額を下げられるのも Perl 版のまま)。
/// ターン数を `$HturnPrizeUnit` で割った余りが 89 より大きいと、入札のたびに 3% でその品が落札済み
/// (状態 15) になる (乱数を 1 つ使う。それ以外では使わない)。
///
/// 成功したら Perl 版は「入札しました」と出して開発画面に戻る。エラー (Perl 版の文面):
/// - 品番が 1〜3 のどれでもない: Perl 版は何もせず空の画面を出す。移植版は
///   `Rejected("品番が正しくありません")` を返す (データは変えない)
/// - ほかの枠に入札している (自分の `auc` のほかの 2 つのどれかが 0 でない): `入札は１品までです`
/// - 自分がいまトップ (自分の `auc` = 最高額、かつ最高額が 0 でない): `現在トップですよ`
/// - 落札済み (状態 15): `こちらの商品は落札されました`
/// - 資金 + 利益 (`pika`) + `auc9` の先頭 × 10000 が、新しい最高額 × 10000 より少ない: `資金が足りません`
pub fn bid(
    game: &mut GameState,
    config: &GameConfig,
    rng: &mut impl Rng,
    id: i64,
    lot: &str,
    amount: &str,
) -> Result<(), ActionError> {
    let n = island_index(&game.world, id).ok_or(ActionError::NoSuchIsland)?;
    let lot = num(&cgi_text(lot));
    let Some(k) = [1.0, 2.0, 3.0].iter().position(|&l| l == lot) else {
        return Err(ActionError::Rejected("品番が正しくありません".into()));
    };
    let turn = game.world.turn;
    let island = &mut game.world.islands[n];
    let mut auc = [
        island.auction.auc1,
        island.auction.auc2,
        island.auction.auc3,
    ];
    if (0..3).any(|j| j != k && auc[j] != 0) {
        return Err(ActionError::Rejected("入札は１品までです".into()));
    }

    // `$auctionN =~ /^([0-9]*),...$/`。合わなければ前のマッチの値だが、ここでは何も無いので
    // すべて空になる (Perl 版で確かめた: 最高額 "1.5" の枠に入札すると ",,0,<額>,")
    let mut scope = MatchScope::default();
    if game.world.auction_lots.len() < 3 {
        game.world.auction_lots.resize(3, String::new());
    }
    let [shuppin, avalue, ajoutai, topvalue, topid] =
        scope.fields_text::<5>(&game.world.auction_lots[k]);
    let top = num(&topvalue);
    if auc[k] as f64 == top && top != 0.0 {
        return Err(ActionError::Rejected("現在トップですよ".into()));
    }
    if num(&ajoutai) == 15.0 {
        return Err(ActionError::Rejected("こちらの商品は落札されました".into()));
    }
    let top = top + num(&cgi_text(amount));

    // auc9 が合わなければ $1 は出品の枠のマッチの値 (Perl 版のまま)
    let [auc9a, ..] = scope.fields::<5>(&island.auction.auc9);
    let funds = (island.money + island.owner_stats.pika) as f64 + (auc9a as f64) * 10000.0;
    if funds < top * 10000.0 {
        return Err(ActionError::Rejected("資金が足りません".into()));
    }

    let top = num_to_string(top);
    game.world.auction_lots[k] = format!("{shuppin},{avalue},0,{top},{topid}");
    // ファイルに書いて読み直したときの値 (`int(<AIN>)`、"1.5" は 1)
    auc[k] = perl::int(&top);
    [
        island.auction.auc1,
        island.auction.auc2,
        island.auction.auc3,
    ] = auc;

    if turn.rem_euclid(config.turn_prize_unit) > 89 && perl::random(rng, 100) < 3 {
        game.world.auction_lots[k] = format!("{shuppin},{avalue},15,{top},{topid}");
    }
    Ok(())
}

#[cfg(test)]
pub(crate) mod tests {
    use super::super::password::check_password;
    use super::super::perl_compat_tests::{Case, cgi_dir, check_case};
    use super::*;

    /// フォームのボタン `<prefix><島ID>` の島 ID (無ければ None)
    pub(crate) fn button_id(case: &Case, n: usize, prefix: &str) -> Option<i64> {
        let form = case.requests[n]["form"].as_object()?;
        form.keys().find_map(|k| {
            let rest = k.strip_prefix(prefix)?;
            rest.bytes()
                .all(|b| b.is_ascii_digit())
                .then(|| perl::int(rest))
        })
    }

    /// Perl 版がその操作で確かめるパスワードが合っているか
    pub(crate) fn password_ok(
        game: &GameState,
        config: &GameConfig,
        case: &Case,
        n: usize,
        id: i64,
    ) -> bool {
        let island = &game.world.islands[island_index(&game.world, id).unwrap()];
        check_password(config, &island.password, &case.form(n, "PASSWORD"))
    }

    /// 入札の操作を順に送る。`TotoButton` の操作 (受付期間の外の各種予想) も混ぜられる。
    /// `ignore` は比べないパス、`check` は最後の状態を確かめる
    fn run_with(
        name: &str,
        ignore: &[&str],
        expect: &[Result<(), &str>],
        check: impl FnOnce(&GameState),
    ) {
        check_case(name, ignore, |game, config, case| {
            assert_eq!(case.requests.len(), expect.len());
            for (n, want) in expect.iter().enumerate() {
                let got = if let Some(id) = button_id(case, n, "TotoButton") {
                    super::super::toto::set_prediction(game, id, &case.form(n, "MESSAGE"))
                } else {
                    let id = button_id(case, n, "AuctionButton").unwrap();
                    if password_ok(game, config, case, n, id) {
                        let (lot, amount) = (case.form(n, "AUCNUMBER"), case.form(n, "AMOUNT"));
                        bid(game, config, &mut case.rng, id, &lot, &amount)
                    } else {
                        Err(ActionError::WrongPassword)
                    }
                };
                let got = got.map_err(|e| e.to_string());
                assert_eq!(got, want.map_err(str::to_string), "{name} request {n}");
            }
            check(game);
        });
    }

    fn run(name: &str, expect: &[Result<(), &str>]) {
        run_with(name, &[], expect, |_| {});
    }

    #[test]
    fn bid_matches_perl() {
        // 最後に 1 枠目が ",,0,-3," (数値として 0) になる。読み込むと Perl 版の readIslandsFile と同じく
        // 品番を選び直してしまうので、その枠はファイルの行どうしで比べる
        let after =
            std::fs::read_to_string(cgi_dir().join("phase6-auction/after/auction.dat")).unwrap();
        let lot0 = after.lines().next().unwrap().to_string();
        assert_eq!(lot0, ",,0,-3,");
        run_with(
            "phase6-auction",
            &["/world/auction_lots/0"],
            &[
                Err("パスワードが違います"),
                Err("品番が正しくありません"),
                Err("現在トップですよ"),
                Err("こちらの商品は落札されました"),
                Err("資金が足りません"),
                // 資金 + auc9 の先頭 × 10000 がちょうど足りる
                Ok(()),
                Err("入札は１品までです"),
                Err("入札は１品までです"),
                // auc9 が正規表現に合わず、出品の枠の品番 (7) が使われる
                Ok(()),
                // 負の額で最高額が 0 に戻る
                Ok(()),
                // "1.5" はそのまま書かれ、auc1 は読み直すと 1
                Ok(()),
                // 1 枠目の最高額が "1.5" になり正規表現に合わない: 品番などは空、最高額は 0 + (-3)
                Ok(()),
                // auc1 が負でも「0 でない」
                Err("入札は１品までです"),
            ],
            |game| assert_eq!(game.world.auction_lots[0], lot0),
        );
    }

    #[test]
    fn bid_sold_by_chance_matches_perl() {
        // ターン 89 は落札の判定をしない、90 はする (乱数 0 → 落札)。最後は受付期間の外の各種予想
        let closed = Err("現在、変更できません");
        run("phase6-auction-t89", &[Ok(()), closed]);
        run("phase6-auction-t90", &[Ok(()), Ok(()), closed]);
        // 乱数 0.015625 → random(100) = 1 で落札、0.03125 → 3 で落札しない
        run("phase6-auction-t90-r1", &[Ok(())]);
        run("phase6-auction-t90-r3", &[Ok(())]);
    }
}
