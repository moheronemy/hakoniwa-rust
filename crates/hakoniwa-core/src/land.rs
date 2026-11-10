//! 地形まわりの共通処理: 名前 (`landName`) と周囲の数え上げ (`countAround`)。

use crate::model::IslandMap;
use crate::tables::{LandKind as L, MONUMENTS, SHIPS};
use crate::turn::monster_spec;

/// 周囲 2 ヘックスまでの座標のずれ (`@ax`, `@ay`)。
/// 0 番目が自分、1〜6 番目が隣、7〜18 番目がその外側
pub const AX: [i64; 19] = [
    0, 1, 1, 1, 0, -1, 0, 1, 2, 2, 2, 1, 0, -1, -1, -2, -1, -1, 0,
];
pub const AY: [i64; 19] = [
    0, -1, 0, 1, 1, 0, -1, -2, -1, 0, 1, 2, 2, 2, 1, 0, -1, -2, -2,
];

/// (x, y) から `i` 番目の方向にある座標。島の外でもそのまま返す。
///
/// ヘックスは奇数行が右にずれているので、偶数行から奇数行を見るときに x を 1 減らす
/// (Perl 版の「行による位置調整」)。Perl の `%` は負の数でも 0 か 1 を返すので `rem_euclid` を使う
pub fn around(x: i64, y: i64, i: usize) -> (i64, i64) {
    let mut sx = x + AX[i];
    let sy = y + AY[i];
    if sy.rem_euclid(2) == 0 && y.rem_euclid(2) == 1 {
        sx -= 1;
    }
    (sx, sy)
}

/// 島の中の座標なら `(usize, usize)` にする
pub fn in_island(map: &IslandMap, (x, y): (i64, i64)) -> Option<(usize, usize)> {
    let size = map.size as i64;
    (0..size)
        .contains(&x)
        .then_some(())
        .filter(|_| (0..size).contains(&y))
        .map(|_| (x as usize, y as usize))
}

/// 範囲を確かめずに `$land->[$sx][$sy]` と `$landValue->[$sx][$sy]` を読んだときの値。
///
/// Perl の配列は負の添字で末尾から数えるので、-1 は反対側の端のマスになる。
/// 大きすぎる添字は未定義 (数値として 0) になる。
/// (Perl は大きすぎる `$sx` で読むと列を自動で作り、以後の負の添字の意味が変わるが、
/// そこまでは再現しない)
pub fn perl_get(map: &IslandMap, sx: i64, sy: i64) -> (u8, i64) {
    let size = map.size as i64;
    let wrap = |v: i64| {
        let v = if v < 0 { v + size } else { v };
        (0..size).contains(&v).then_some(v as usize)
    };
    match (wrap(sx), wrap(sy)) {
        (Some(x), Some(y)) => map.get(x, y).map_or((0, 0), |c| (c.kind, c.value)),
        _ => (0, 0),
    }
}

/// `countAround($land, $x, $y, $kind, $range)`: 周囲 `range` 個のマスのうち `kind` の数。
/// 島の外は海として数える
pub fn count_around(map: &IslandMap, x: i64, y: i64, kind: L, range: usize) -> i64 {
    let mut mask = [false; 256];
    mask[kind as usize] = true;
    count_around_mask(map, x, y, &mask, range)
}

/// 地形の種類の集まり ([`count_around_mask`] に渡す)
pub const fn kind_mask(kinds: &[L]) -> [bool; 256] {
    let mut mask = [false; 256];
    let mut i = 0;
    while i < kinds.len() {
        mask[kinds[i] as usize] = true;
        i += 1;
    }
    mask
}

/// 周囲 `range` 個のマスのうち、地形が `mask` に入っているものの数 (島の外は海として数える)。
/// 種類ごとの [`count_around`] の合計と同じ (同じマスを 1 回だけ見るので速い)
pub fn count_around_mask(map: &IslandMap, x: i64, y: i64, mask: &[bool; 256], range: usize) -> i64 {
    let size = map.size as i64;
    let cells = &map.cells;
    // 奇数行から偶数行を見るときは x を 1 減らす ([`around`] と同じ)
    let odd = y.rem_euclid(2) == 1;
    let mut n = 0;
    for i in 0..range {
        let sy = y + AY[i];
        let mut sx = x + AX[i];
        if odd && sy.rem_euclid(2) == 0 {
            sx -= 1;
        }
        let hit = if (0..size).contains(&sx) && (0..size).contains(&sy) {
            mask[cells[(sy * size + sx) as usize].kind as usize]
        } else {
            mask[L::Sea as usize]
        };
        n += i64::from(hit);
    }
    n
}

/// `landName($land, $lv)`: ログに出す地形の名前。Perl 版で名前の無いものは空文字列
pub fn land_name(kind: u8, lv: i64) -> String {
    let Some(kind) = L::from_u8(kind) else {
        return String::new();
    };
    let s: &str = match kind {
        L::Sea => {
            if lv == 1 {
                "浅瀬"
            } else {
                "海"
            }
        }
        L::Ice => {
            if lv > 0 {
                "天然スケート場"
            } else {
                "氷河"
            }
        }
        L::Waste => "荒地",
        L::Plains => "平地",
        L::Plains2 => "開発予定地",
        L::Town => {
            if lv < 30 {
                "村"
            } else if lv < 100 {
                "町"
            } else {
                "都市"
            }
        }
        L::Procity => "防災都市",
        L::Newtown => "ニュータウン",
        L::Bigtown => "現代都市",
        L::Bettown => "輝ける都市",
        L::Skycity => "空中都市",
        L::Umicity => "海都市",
        L::Seatown => "海底新都市",
        L::Rizort => "リゾート地",
        L::Kajino => "カジノ",
        L::BigRizort => "臨海リゾートホテル",
        L::Shuto => "首都",
        L::Umishuto => "海底首都",
        L::Forest => "森",
        L::Farm => "農場",
        L::EneAt => "原子力発電所",
        L::EneFw => "火力発電所",
        L::EneWt => "水力発電所",
        L::EneWd => "風力発電所",
        L::EneBo => "バイオマス発電所",
        L::EneSo => "ソーラー発電所",
        L::EneCs => "コスモ発電所",
        L::Conden => "コンデンサ",
        L::Conden2 => "コンデンサ・改",
        L::Conden3 => "黄金のコンデンサ",
        L::Conden4 => match lv {
            2 => "コンデンサ・改(漏電中)",
            99 => "核融合発電所",
            _ => "黄金のコンデンサ(漏電中)",
        },
        L::Foodka => "食品加工工場",
        L::Foodim => {
            if lv < 480 {
                "食物研究所"
            } else {
                "防災型食物研究所"
            }
        }
        L::Farmchi => "養鶏場",
        L::Farmpic => "養豚場",
        L::Farmcow => "牧場",
        L::Yakusho => "島役所",
        L::College => match lv {
            0 => "農業大学",
            1 => "工業大学",
            2 => "総合大学",
            3 => "軍事大学",
            4 | 98 => "生物大学(待機中)",
            96 | 97 => "生物大学(出禁中)",
            99 => "生物大学(出動中)",
            6 => "経済大学",
            7 => "魔法学校",
            8 => "電工大学",
            77..=80 => "文部科学省",
            95 => "経済大学(貯金中)",
            _ => "気象大学",
        },
        L::House => match lv {
            0 => "小屋",
            1 => "簡易住宅",
            2 => "住宅",
            3 => "高級住宅",
            4 => "豪邸",
            5 => "大豪邸",
            6 => "高級豪邸",
            7 => "城",
            8 => "巨城",
            _ => "黄金城",
        },
        L::Train => match lv {
            0 => "駅",
            ..0 | 1..10 => "線路",
            10 => "駅(普通電車停車中)",
            11..20 => "普通電車",
            20 => "駅(貨物列車停車中)",
            21..30 => "貨物列車",
            _ => "",
        },
        L::Taishi => "大使館",
        L::Kura | L::Kuraf => "倉庫",
        L::Factory => "工場",
        L::HTFactory => "ハイテク多国籍企業",
        L::SHTF => "ハイテク多国籍企業・改",
        L::OWNF => "島営企業",
        L::Base => "ミサイル基地",
        L::Defence => {
            if lv == 77 {
                "防衛施設・改"
            } else {
                "防衛施設"
            }
        }
        L::Mountain => "山",
        L::Gold => "金山",
        L::Onsen => "温泉街",
        L::Monster => return monster_spec(lv).1.to_string(),
        L::Sbase => "海底基地",
        L::Seacity => "海底都市",
        L::Oil => "海底油田",
        L::Monument => {
            return usize::try_from(lv)
                .ok()
                .and_then(|i| MONUMENTS.get(i))
                .map(|m| m.0.to_string())
                .unwrap_or_default();
        }
        L::Haribote => "ハリボテ",
        L::Park => "遊園地",
        L::Minato => "港町",
        L::Fune => {
            return usize::try_from(lv)
                .ok()
                .and_then(|i| SHIPS.get(i))
                .map(|s| s.0.to_string())
                .unwrap_or_default();
        }
        L::Frocity => "海上都市",
        L::Sunahama => "砂浜",
        L::Mine => "地雷",
        L::Nursery => "養殖場",
        L::Kyujo => "野球場",
        L::Kyujokai => "多目的スタジアム",
        L::Zoo => "動物園",
        L::Umiamu => "海あみゅ",
        L::Seki => "関所",
        L::RottenSea => {
            if lv < 20 {
                "腐海"
            } else {
                "枯死海"
            }
        }
    };
    s.to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hex_offsets_match_perl() {
        // 奇数行 (y=1) から偶数行 (y=0) を見ると x が 1 ずれる
        assert_eq!(around(5, 1, 1), (5, 0));
        assert_eq!(around(5, 2, 1), (6, 1));
        assert_eq!(around(0, 0, 0), (0, 0));
        // 負の行でも Perl と同じ (-1 % 2 == 1)
        assert_eq!(around(0, 0, 18), (0, -2));
        assert_eq!(around(0, 1, 18), (0, -1));
    }

    #[test]
    fn count_around_treats_outside_as_sea() {
        let map = IslandMap::new_sea(12);
        assert_eq!(count_around(&map, 0, 0, L::Sea, 7), 7);
        let mut map = map;
        map.get_mut(1, 0).unwrap().kind = L::Town as u8;
        assert_eq!(count_around(&map, 0, 0, L::Town, 7), 1);
        assert_eq!(count_around(&map, 0, 0, L::Sea, 7), 6);
    }

    #[test]
    fn names() {
        assert_eq!(land_name(L::Town as u8, 50), "町");
        assert_eq!(land_name(L::Monument as u8, 1), "聖樹");
        assert_eq!(land_name(L::Monument as u8, 999), "");
        assert_eq!(land_name(L::Train as u8, 35), "");
        assert_eq!(land_name(200, 0), "");
    }
}
