//! 島の登録 (`newIslandMain`, `makeNewIsland`, `makeNewLand`)。
//!
//! Perl 版との違い (わざと変えた点):
//! - パスワードは [`hash_password`] (SHA-512 crypt) で保存する。Perl 版の DES crypt は
//!   先頭 8 文字しか効かないが、移植版は切り詰めない。

use rand::RngCore;

use crate::GameConfig;
use crate::land::count_around;
use crate::log::{TurnLog, tags};
use crate::model::{GameState, IslandMap, LandCell, TurnMessage};
use crate::perl::{self, cgi_text, cut_column, html_escape};
use crate::tables::LandKind as L;
use crate::turn::{Globals, TurnContext, estimate::estimate};

use super::password::hash_password;
use super::{ActionError, Request};

/// 島が一杯 (`tempNewIslandFull`)
pub const MSG_FULL: &str = "申し訳ありません、島が一杯で登録できません！！";
/// 名前・オーナー名・意気込みのどれかが空 (`tempNewIslandNoName`)
pub const MSG_NO_NAME: &str = "入力が不十分です。";
/// 使えない名前 (`tempNewIslandBadName`)。名前の変更でも使う
pub const MSG_BAD_NAME: &str =
    "',?()<>$'とか入ってたり、「無人島」とかいった変な名前はやめましょうよ〜";
/// 同じ名前の島がある (`tempNewIslandAlready`)。名前の変更でも使う
pub const MSG_ALREADY: &str = "その島ならすでに発見されています。";
/// 同じ接続元の島がある (`tempIPIslandAlready`)
pub const MSG_SAME_IP: &str =
    "あなたと同じＩＰの島がすでに発見されています。重複登録防止にご協力ください。";
/// パスワードが空 (`tempNewIslandNoPassword`)
pub const MSG_NO_PASSWORD: &str = "パスワードが必要です。";

/// 登録画面の入力 (トップページの「新しい島を探す」フォーム)。どれも利用者が打ったままの文字列
#[derive(Debug, Clone, Copy, Default)]
pub struct NewIslandInput<'a> {
    /// 島の名前 (`ISLANDNAME`、「島」は付けない)
    pub name: &'a str,
    /// オーナー名 (`OWNERNAME`)
    pub owner_name: &'a str,
    /// パスワード (`PASSWORD`)
    pub password: &'a str,
    /// 確認用パスワード (`PASSWORD2`)
    pub password2: &'a str,
    /// 参加にあたっての意気込み (`MESSAGE`、島のコメントになる)
    pub message: &'a str,
}

/// `newIslandMain`: 新しい島を登録し、その島の ID を返す。
///
/// 島は一覧の末尾に加わる。エラーは [`ActionError::Rejected`] (文面は `MSG_*`) と
/// [`ActionError::WrongPassword`] (確認用パスワードが違う)。失敗したときは何も変えない。
/// 成功したら Perl 版は「島を発見しました！！「○○島」と命名します。」と出して、
/// その島の開発画面 (地図と情報) を表示していた。
///
/// `req.remote_addr` は既存の島の `ip0`〜`ip5` との重複判定 (`reject_duplicate_ip`) に使い、
/// 新しい島の `ip0`〜`ip5` に記録する。`rng` は地形の生成と `estimate` に使う。
/// ターン処理が必要な時刻なら、呼び出す前にターンを進めておくこと
/// (Perl 版は読み込み時にターン処理へ切り替えていた)。
pub fn new_island<R: RngCore>(
    game: &mut GameState,
    config: &GameConfig,
    req: Request,
    rng: &mut R,
    input: &NewIslandInput,
) -> Result<i64, ActionError> {
    let rng: &mut dyn RngCore = rng;
    let reject = |m: &str| Err(ActionError::Rejected(m.to_string()));
    let world = &mut game.world;

    // cgiInput の加工
    let name = cut_column(&cgi_text(input.name), 20);
    let owner_name = cut_column(&cgi_text(input.owner_name), 20);
    let message = cut_column(&cgi_text(input.message), 80);
    let password = cgi_text(input.password);
    let password2 = cgi_text(input.password2);

    // 島がいっぱいでないかチェック
    if world.islands.len() >= config.max_islands {
        return reject(MSG_FULL);
    }
    // 名前があるかチェック
    if name.is_empty() || owner_name.is_empty() || message.is_empty() {
        return reject(MSG_NO_NAME);
    }
    // 名前が正当かチェック
    if is_bad_name(&name, true) {
        return reject(MSG_BAD_NAME);
    }
    // 名前の重複チェック
    if world.islands.iter().any(|i| i.name == name) {
        return reject(MSG_ALREADY);
    }
    // パスワードの存在判定
    if password.is_empty() {
        return reject(MSG_NO_PASSWORD);
    }
    // 確認用パスワード
    if password2 != password {
        return Err(ActionError::WrongPassword);
    }
    // IP の重複チェック (`ipToNumber`: どれかの島の ip0〜ip5 と同じなら拒否)
    let speaker = req.remote_addr;
    if config.reject_duplicate_ip
        && world
            .islands
            .iter()
            .any(|i| i.ip[..6].iter().any(|ip| ip == speaker))
    {
        return reject(MSG_SAME_IP);
    }

    // makeNewIsland
    let id = world.next_id;
    world.next_id += 1;
    let mut island = crate::model::Island::blank(id, &name, config);
    island.map = make_new_land(config, rng);
    island.money = config.initial_money;
    island.food = config.initial_food;
    island.prize = "0,0,".into();

    // 各種の値を設定
    island.absent = config.giveup_turn - 3;
    island.comment = html_escape(&message);
    island.password = hash_password(&password);
    island.eis8 = "(未登録)".into();
    let onm = html_escape(&owner_name);
    island.onm = onm.clone();
    island.owner_name = onm.clone();
    // 加算した後の値 (Perl 版のまま)
    island.id1 = world.next_id;
    island.totoyoso = "(未登録)".into();
    island.totoyoso2 = "555".into();
    island.ip_name = name.clone();
    island.ip = std::array::from_fn(|i| {
        if i < 6 {
            speaker.to_string()
        } else {
            "0".to_string()
        }
    });

    if config.another_mode {
        island.totoyoso2 = format!("{onm}シティー");
        island.scratch.shu += 1;
        island.eisei[0] = 7;
    }

    if perl::random(rng, 100) < 50 {
        island.eis[0] = 200;
    } else {
        island.eis[1] = 200;
    }

    world.islands.push(island);
    let idx = world.islands.len() - 1;

    // 人口その他算出 (Perl 版は 1 リクエスト 1 プロセスなので、グローバル変数は空の状態)
    let mut ctx = TurnContext {
        config,
        rng,
        turn: world.turn,
        log: TurnLog::default(),
        // makeRandomPointArray は呼ばれていないので @Hrpx は空
        points: Vec::new(),
        id_to_number: world
            .islands
            .iter()
            .enumerate()
            .map(|(i, island)| (island.id, i))
            .collect(),
        island_number: world.islands.len(),
        globals: Globals::default(),
        oyasumiritu: 0,
    };
    estimate(&mut ctx, &mut world.islands, idx);
    let island = &mut world.islands[idx];
    *island.scratch = Default::default();
    // estimate はアンケートが無効なら anflag を 0 にするが、Perl 版は次に読み込むとき
    // `if($anflag == '') { $anflag = '1'; }` で 1 に戻す。保存と読み込みを挟んだ値にそろえる
    if island.survey_flag == 0 {
        island.survey_flag = 1;
    }

    // logDiscover。Perl 版は logHistoryTrim を呼ばないので、ここでは行数を切り詰めない
    // (次のターン処理で切り詰められる)
    game.logs.history.push(TurnMessage {
        turn: game.world.turn,
        message: format!("{}が発見される。", island_tag(&name)),
    });

    Ok(id)
}

/// `${HtagName_}${name}島${H_tagName}`
pub(crate) fn island_tag(name: &str) -> String {
    tags::wrap(tags::NAME, &format!("{name}島"))
}

/// 使えない名前か。登録は `/[,\?\(\)\<\>\$]|^無人$/`、名前の変更は `$` を許す
/// `/[,\?\(\)\<\>]|^無人$/` (Perl 版のまま)
pub(crate) fn is_bad_name(name: &str, forbid_dollar: bool) -> bool {
    name == "無人"
        || name
            .chars()
            .any(|c| matches!(c, ',' | '?' | '(' | ')' | '<' | '>') || (forbid_dollar && c == '$'))
}

/// `makeNewLand`: 新しい島の地形を作る。乱数の使い方は Perl 版と同じ
pub fn make_new_land(config: &GameConfig, rng: &mut dyn RngCore) -> IslandMap {
    let size = config.island_size;
    let mut map = IslandMap::new_sea(size);
    let set = |map: &mut IslandMap, x: i64, y: i64, kind: L, value: i64| {
        if let Some(c) = map.get_mut(x as usize, y as usize) {
            *c = LandCell {
                kind: kind as u8,
                value,
            };
        }
    };
    let kind_at = |map: &IslandMap, x: i64, y: i64| {
        map.get(x as usize, y as usize)
            .map_or(L::Sea as u8, |c| c.kind)
    };

    // 中央の 4*4 に荒地を配置
    let center = size as i64 / 2 - 1;
    for y in center - 1..center + 3 {
        for x in center - 1..center + 3 {
            set(&mut map, x, y, L::Waste, 0);
        }
    }

    // 8*8 範囲内に陸地を増殖
    for _ in 0..120 {
        let x = perl::random(rng, 8) + center - 3;
        let y = perl::random(rng, 8) + center - 3;
        if count_around(&map, x, y, L::Sea, 7) != 7 {
            // 周りに陸地がある場合、浅瀬にする。浅瀬は荒地に、荒地は平地にする
            // (平地も値 1 を経て荒地に戻る: Perl 版のまま)
            let Some(c) = map.get_mut(x as usize, y as usize) else {
                continue;
            };
            if c.kind == L::Waste as u8 {
                *c = LandCell {
                    kind: L::Plains as u8,
                    value: 0,
                };
            } else if c.value == 1 {
                *c = LandCell {
                    kind: L::Waste as u8,
                    value: 0,
                };
            } else {
                c.value = 1;
            }
        }
    }

    // 中央の 4*4 のどこかを選ぶ
    let pick = |rng: &mut dyn RngCore| {
        let x = perl::random(rng, 4) + center - 1;
        let y = perl::random(rng, 4) + center - 1;
        (x, y)
    };
    let not_in = |map: &IslandMap, x: i64, y: i64, kinds: &[L]| {
        let k = kind_at(map, x, y);
        !kinds.iter().any(|&l| l as u8 == k)
    };

    // 森を作る (最初は 500 本)
    let mut count = 0;
    while count < 4 {
        let (x, y) = pick(rng);
        if not_in(&map, x, y, &[L::Forest]) {
            set(&mut map, x, y, L::Forest, 5);
            count += 1;
        }
    }

    // 町を作る (最初は 500 人)
    let mut count = 0;
    while count < 2 {
        let (x, y) = pick(rng);
        if not_in(&map, x, y, &[L::Town, L::Forest]) {
            set(&mut map, x, y, L::Town, 5);
            count += 1;
        }
    }

    // 山・基地・ニュータウン・大学・港・発電所 (どれも 1 つ)
    let mut avoid = vec![L::Town, L::Forest];
    let place = |map: &mut IslandMap,
                 rng: &mut dyn RngCore,
                 avoid: &[L],
                 kind: L,
                 value: fn(&mut dyn RngCore) -> i64| {
        loop {
            let (x, y) = pick(rng);
            if not_in(map, x, y, avoid) {
                let v = value(rng);
                set(map, x, y, kind, v);
                return (x, y);
            }
        }
    };
    // 山 (最初は採掘場なし)
    place(&mut map, rng, &avoid, L::Mountain, |_| 0);
    avoid.push(L::Mountain);
    place(&mut map, rng, &avoid, L::Base, |_| 0);
    avoid.push(L::Base);
    place(&mut map, rng, &avoid, L::Newtown, |_| 10);
    avoid.push(L::Newtown);
    place(&mut map, rng, &avoid, L::College, |rng| {
        perl::random(rng, 3)
    });
    avoid.push(L::College);
    // 港。Perl 版は周りの海を `countAround($land, ...)` で数えるが、`$land` は
    // 未定義のグローバル変数 (地形は `@land`) なので、範囲内のマスもすべて海と数えられ、
    // 海の数は必ず 7 になる。「周りが全部陸なら置かない」判定は効かない (Perl 版のまま)
    place(&mut map, rng, &avoid, L::Minato, |_| 5);
    avoid.push(L::Minato);
    place(&mut map, rng, &avoid, L::EneWd, |_| 50);
    avoid.push(L::EneWd);
    // コンデンサ (10% でコンデンサ 3)
    let (x, y) = place(&mut map, rng, &avoid, L::Conden, |_| 100);
    if perl::random(rng, 100) < 10 {
        set(&mut map, x, y, L::Conden3, 0);
    }

    if config.another_mode {
        avoid.push(L::Conden);
        avoid.push(L::Conden3);
        place(&mut map, rng, &avoid, L::Shuto, |_| 50);
        avoid.push(L::Shuto);
        place(&mut map, rng, &avoid, L::House, |_| 0);
    }

    map
}

#[cfg(test)]
pub(crate) mod tests {
    use super::super::password::verify;
    use super::super::perl_compat_tests::{Case, cgi_dir, check_case};
    use super::*;
    use rand::RngCore;

    /// `rand()` を JSON の `"rand": ["5", "25", ...]` の順に返す乱数 (Perl 側と同じく先頭へ戻る)
    pub(crate) struct SeqRng {
        values: Vec<u64>,
        pos: usize,
    }

    impl SeqRng {
        pub(crate) fn for_case(name: &str) -> Self {
            let json: serde_json::Value = serde_json::from_str(
                &std::fs::read_to_string(cgi_dir().join(format!("{name}.json"))).unwrap(),
            )
            .unwrap();
            let values = json["rand"]
                .as_array()
                .expect("rand は配列")
                .iter()
                .map(|v| {
                    let r: f64 = format!("0.{}", v.as_str().unwrap()).parse().unwrap();
                    let m = r * (1u64 << 53) as f64;
                    assert_eq!(m.fract(), 0.0);
                    (m as u64) << 11
                })
                .collect();
            Self { values, pos: 0 }
        }
    }

    impl RngCore for SeqRng {
        fn next_u64(&mut self) -> u64 {
            let v = self.values[self.pos % self.values.len()];
            self.pos += 1;
            v
        }
        fn next_u32(&mut self) -> u32 {
            (self.next_u64() >> 32) as u32
        }
        fn fill_bytes(&mut self, dest: &mut [u8]) {
            rand_core_fill(self, dest)
        }
        fn try_fill_bytes(&mut self, dest: &mut [u8]) -> Result<(), rand::Error> {
            rand_core_fill(self, dest);
            Ok(())
        }
    }

    fn rand_core_fill(rng: &mut SeqRng, dest: &mut [u8]) {
        for chunk in dest.chunks_mut(8) {
            let b = rng.next_u64().to_le_bytes();
            chunk.copy_from_slice(&b[..chunk.len()]);
        }
    }

    fn input(case: &Case, n: usize) -> [String; 5] {
        [
            "ISLANDNAME",
            "OWNERNAME",
            "PASSWORD",
            "PASSWORD2",
            "MESSAGE",
        ]
        .map(|k| case.form(n, k))
    }

    /// 各操作を移植版で行い、結果 (ID か エラー) を返す
    fn run(name: &str, game: &mut GameState, config: &GameConfig, case: &Case) -> Vec<String> {
        (0..case.requests.len())
            .map(|n| {
                let [a, b, c, d, e] = input(case, n);
                let addr = case.addr(n);
                let req = Request {
                    now: case.now,
                    remote_addr: &addr,
                };
                // Perl 版は操作ごとに別のプロセスなので、乱数の並びは毎回先頭から
                let mut rng = SeqRng::for_case(name);
                let r = new_island(
                    game,
                    config,
                    req,
                    &mut rng,
                    &NewIslandInput {
                        name: &a,
                        owner_name: &b,
                        password: &c,
                        password2: &d,
                        message: &e,
                    },
                );
                match r {
                    Ok(id) => {
                        let island = game.world.island_by_id(id).unwrap();
                        assert!(verify(&island.password, &c));
                        format!("ok {id}")
                    }
                    Err(e) => e.to_string(),
                }
            })
            .collect()
    }

    fn check(name: &str, existing: usize, expect: &[&str]) {
        let ignore: Vec<String> = (existing..existing + 30)
            .map(|i| format!("/world/islands/{i}/password"))
            .collect();
        let ignore: Vec<&str> = ignore.iter().map(String::as_str).collect();
        check_case(name, &ignore, |game, config, case| {
            let got = run(name, game, config, case);
            if !expect.is_empty() {
                assert_eq!(got, expect);
            }
        });
    }

    #[test]
    fn new_island_matches_perl() {
        check(
            "new-island-1",
            3,
            &[
                "ok 4",
                MSG_ALREADY,
                MSG_ALREADY,
                MSG_BAD_NAME,
                MSG_BAD_NAME,
                MSG_BAD_NAME,
                MSG_BAD_NAME,
                MSG_NO_NAME,
                MSG_NO_NAME,
                MSG_NO_NAME,
                MSG_NO_PASSWORD,
                "パスワードが違います",
                MSG_SAME_IP,
                MSG_SAME_IP,
                "ok 5",
                "ok 6",
            ],
        );
    }

    #[test]
    fn new_island_land_matches_perl() {
        for s in 2..=5 {
            check(&format!("new-island-rand{s}"), 3, &["ok 4"]);
        }
    }

    #[test]
    fn new_island_until_full_matches_perl() {
        let mut expect: Vec<String> = (4..31).map(|id| format!("ok {id}")).collect();
        expect.push(MSG_FULL.into());
        let expect: Vec<&str> = expect.iter().map(String::as_str).collect();
        check("new-island-full", 3, &expect);
    }

    #[test]
    fn duplicate_ip_allowed_when_disabled() {
        let config = GameConfig {
            reject_duplicate_ip: false,
            ..Default::default()
        };
        let mut game = GameState::new_game(0, &config);
        use rand::SeedableRng;
        let mut rng = rand::rngs::StdRng::seed_from_u64(1);
        let req = Request {
            now: 0,
            remote_addr: "1.2.3.4",
        };
        for n in ["a", "b"] {
            let input = NewIslandInput {
                name: n,
                owner_name: "o",
                password: "p",
                password2: "p",
                message: "m",
            };
            new_island(&mut game, &config, req, &mut rng, &input).unwrap();
        }
        assert_eq!(game.world.islands.len(), 2);
        assert_eq!(game.world.next_id, 3);
    }

    #[test]
    fn another_mode_places_capital_and_house() {
        use rand::SeedableRng;
        let config = GameConfig {
            another_mode: true,
            ..Default::default()
        };
        let mut rng = rand::rngs::StdRng::seed_from_u64(3);
        let map = make_new_land(&config, &mut rng);
        let count = |k: L| map.cells.iter().filter(|c| c.kind == k as u8).count();
        assert_eq!(count(L::Shuto), 1);
        assert_eq!(count(L::House), 1);
        assert_eq!(count(L::Forest), 4);
        assert_eq!(count(L::Town), 2);
    }
}
