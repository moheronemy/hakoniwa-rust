//! 島の並べ替え (`islandSort*`) と部門賞 (`bumon`)。
//!
//! Perl 版の並べ替えは `sort { $b->{key} <=> $a->{key} || $a <=> $b }` で、
//! 同じ値なら元の順を保つ。Rust の `sort_by` も安定なので同じ結果になる。
//! Perl 版は `@Hislands` そのものを並べ替えるので、移植版も島の配列を並べ替える。

use crate::model::Island;

/// 値の大きい順に並べ替える (同じ値なら元の順)
fn sort_desc(islands: &mut [Island], key: impl Fn(&Island) -> i64) {
    islands.sort_by_key(|i| std::cmp::Reverse(key(i)));
}

/// `islandSort`: 総合ポイント順
pub(crate) fn sort_by_pts(islands: &mut [Island]) {
    sort_desc(islands, |i| i.pts);
}

/// 部門賞の対象 (turnMain で並べ替える順)
const DEPARTMENTS: [fn(&Island) -> i64; 20] = [
    |i| i.pop,                  // islandSortPop
    |i| i.farm,                 // islandSortFarm
    |i| i.scratch.factoryt,     // islandSortFactory
    |i| i.mountain,             // islandSortMountain
    |i| i.owner_stats.kei,      // islandSortMonument
    |i| i.scratch.monsterlive2, // islandSortLive
    |i| i.owner_stats.rena,     // islandSortRena
    |i| i.taiji,                // islandSortKill
    |i| i.owner_stats.fore,     // islandSortFore
    |i| i.owner_stats.tare,     // islandSortTare
    |i| i.owner_stats.zipro,    // islandSortZipro
    |i| i.owner_stats.leje,     // islandSortLeje
    |i| i.scratch.force,        // islandSortForce
    |i| i.eisei[1],             // islandSortEisei2
    |i| i.scratch.uni,          // islandSortUni
    |i| i.scratch.ene,          // islandSorthck
    |i| i.etc_num[0],           // islandSorthckt
    |i| i.scratch.shoritu,      // islandSorthcr
    |i| i.scratch.styusho,      // islandSorthcy
    |i| i.scratch.teamforce,    // islandSorthct
];

/// 部門ごとに並べ替えて 1 位の島の `bumon` を 1 増やす。
/// 配列は最後の部門 (チーム力) の順に並んだまま残る (Perl 版のまま)
pub(crate) fn award_departments(islands: &mut [Island]) {
    if islands.is_empty() {
        return;
    }
    let mut winners = Vec::with_capacity(DEPARTMENTS.len());
    for key in DEPARTMENTS {
        sort_desc(islands, key);
        winners.push(islands[0].id);
    }
    for id in winners {
        if let Some(island) = islands.iter_mut().find(|i| i.id == id) {
            island.scratch.bumon += 1;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::turn::tests_support::island;

    #[test]
    fn departments_award_top_islands() {
        let mut a = island();
        a.id = 1;
        a.pop = 10;
        let mut b = island();
        b.id = 2;
        b.farm = 5;
        let mut islands = vec![a, b];
        award_departments(&mut islands);
        let bumon = |id| islands.iter().find(|i| i.id == id).unwrap().scratch.bumon;
        // 島 2 は農場部門だけ、残り 19 部門は同点で先頭にいる島 (並べ替えのたびに変わる)
        assert_eq!(bumon(1) + bumon(2), 20);
        assert!(bumon(2) >= 1);
    }

    #[test]
    fn sort_is_stable() {
        let mut islands: Vec<_> = (1..=3)
            .map(|id| {
                let mut i = island();
                i.id = id;
                i.pts = if id == 3 { 50 } else { 10 };
                i
            })
            .collect();
        sort_by_pts(&mut islands);
        let ids: Vec<_> = islands.iter().map(|i| i.id).collect();
        assert_eq!(ids, [3, 1, 2]);
    }
}
