#include "map.h"

Land *Map::land;

// (範囲/内包hex数)一覧
// (0/1) (1/7) (2/19) (3/37) (4/61) (5/91) (6/127)
// (7/169) (8/217) (9/271) (10/331) (11/397)
const int ax[] = {0,0,1,-1,1,0,1,-1,0,1,-1,2,-2,2,-1,2,-1,0,1,-1,0,1,2,-2,2,-2,3,-3,3,-2,3,-2,2,-1,0,1,2,-2,-1,0,1,2,-2,3,-3,3,-3,4,-4,4,-3,4,-3,3,-2,3,-2,-1,0,1,2,-2,-1,0,1,2,3,-3,3,-3,4,-4,4,-4,5,-5,5,-4,5,-4,4,-3,4,-3,3,-2,-1,0,1,2,3,-3,-2,-1,0,1,2,3,-3,4,-4,4,-4,5,-5,5,-5,6,-6,6,-5,6,-5,5,-4,5,-4,4,-3,4,-3,-2,-1,0,1,2,3,-3,-2,-1,0,1,2,3,4,-4,4,-4,5,-5,5,-5,6,-6,6,-6,7,-7,7,-6,7,-6,6,-5,6,-5,5,-4,5,-4,4,-3,-2,-1,0,1,2,3,4,-4,-3,-2,-1,0,1,2,3,4,-4,5,-5,5,-5,6,-6,6,-6,7,-7,7,-7,8,-8,8,-7,8,-7,7,-6,7,-6,6,-5,6,-5,5,-4,5,-4,-3,-2,-1,0,1,2,3,4,-4,-3,-2,-1,0,1,2,3,4,5,-5,5,-5,6,-6,6,-6,7,-7,7,-7,8,-8,8,-8,9,-9,9,-8,9,-8,8,-7,8,-7,7,-6,7,-6,6,-5,6,-5,5,-4,-3,-2,-1,0,1,2,3,4,5,-5,-4,-3,-2,-1,0,1,2,3,4,5,-5,6,-6,6,-6,7,-7,7,-7,8,-8,8,-8,9,-9,9,-9,10,-10,10,-9,10,-9,9,-8,9,-8,8,-7,8,-7,7,-6,7,-6,6,-5,6,-5,-4,-3,-2,-1,0,1,2,3,4,5,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,-6,6,-6,7,-7,7,-7,8,-8,8,-8,9,-9,9,-9,10,-10,10,-10,11,-11,11,-10,11,-10,10,-9,10,-9,9,-8,9,-8,8,-7,8,-7,7,-6,7,-6,6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6};

const int ay[] = {0,-1,-1,0,0,1,1,-2,-2,-2,-1,-1,0,0,1,1,2,2,2,-3,-3,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,3,3,-4,-4,-4,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,4,4,4,-5,-5,-5,-5,-5,-5,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,5,5,5,5,-6,-6,-6,-6,-6,-6,-6,-5,-5,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,6,6,6,6,6,6,6,-7,-7,-7,-7,-7,-7,-7,-7,-6,-6,-5,-5,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,7,7,7,7,7,7,-8,-8,-8,-8,-8,-8,-8,-8,-8,-7,-7,-6,-6,-5,-5,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,8,8,8,8,8,8,8,-9,-9,-9,-9,-9,-9,-9,-9,-9,-9,-8,-8,-7,-7,-6,-6,-5,-5,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,9,9,9,9,9,9,9,9,-10,-10,-10,-10,-10,-10,-10,-10,-10,-10,-10,-9,-9,-8,-8,-7,-7,-6,-6,-5,-5,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,10,10,10,10,10,10,10,10,10,-11,-11,-11,-11,-11,-11,-11,-11,-11,-11,-11,-11,-10,-10,-9,-9,-8,-8,-7,-7,-6,-6,-5,-5,-4,-4,-3,-3,-2,-2,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,11,11,11,11,11,11,11,11,11,11};

// 領域確保
void Map::alloc() {
    // 領域確保
    land = new Land[Value::worldSize * Value::worldSize];
}

// 初期化
void Map::initialize() {
    int size = Value::worldSize * Value::worldSize;
    for(int i = 0; i < size; i++) {
	land[i].initialize();
    }
}

// ファイル出力
void Map::output(ofstream *ofs) {
    int i = 0;
    for(int y = 0; y < Value::worldSize; y++) {
	for(int x = 0; x < Value::worldSize; x++) {
	    land[i].output(ofs);
	    i++;
	}
	*ofs << "\n";
    }
}

// ファイル入力
void Map::input(ifstream *ifs) {
    int i = 0;
    for(int y = 0; y < Value::worldSize; y++) {
	for(int x = 0; x < Value::worldSize; x++) {
	    land[i].input(ifs);
	    i++;
	}
	(*ifs).get(); // 改行読み飛ばし
    }
}

// JavaScript出力
void Map::jsOut(int number) {
    int i = 0;
    HakoIO::out("mapData = [\n");
    for(int y = 0; y < Value::worldSize; y++) {
	HakoIO::out("\"");
	for(int x = 0; x < Value::worldSize; x++) {
	    land[i].jsOut(number);
	    i++;
	}
	if(y == Value::worldSize - 1) {
	    HakoIO::out("\"\n");
	} else {
	    HakoIO::out("\",\n");
	}
    }
    HakoIO::out("];\n");
}

// 周辺の座標を返す
Point Map::getPoint(int sx, int sy, int d) {
    Point p;
    p.x = sx + ax[d];
    p.y = sy + ay[d];

    // 行による位置調整
    if(((p.y % 2) == 0) && ((sy % 2) == 1)) {
	p.x--;
    }

    if((p.x < 0) || (p.x >= Value::worldSize) ||
       (p.y < 0) || (p.y >= Value::worldSize)) {
	p.x = -1;
	p.y = -1;
    }
    return p;
}

// 指定座標のLandのポインタを返す
Land *Map::getLand(int x, int y) {
    if((x >= Value::worldSize) ||
       (x < 0) ||
       (y >= Value::worldSize) ||
       (y < 0)) {
	return 0;
    }
    return land + y * Value::worldSize + x;
}

// 指定座標のLandのポインタを返す(周辺版)
Land *Map::getAround(int sx, int sy, int d) {
    Point p = getPoint(sx, sy, d);
    return getLand(p);
}

// 指定座標周辺で、その種類の土地を数える
int Map::countAround(int sx, int sy, int kind, int from, int to, int param) {
    int count = 0;
    for(int i = from; i < to; i++) {
	Land *land = getAround(sx, sy, i);
	if(land == 0) {
	    // 領域外は海
	    if(kind == Land::Sea) {
		if((param == -1) || (param == Land::SeaDeep)) {
		    count++;
		}
	    }
	} else if(land->kind == kind){
	    if((param == -1) || (param == land->param)) {
		count++;
	    }
	}
    }
    return count;
}

// 指定座標周辺で、その種類の土地を数える
int Map::countNeutral(int sx, int sy, int from, int to) {
    int count = 0;
    for(int i = from; i < to; i++) {
	Land *land = getAround(sx, sy, i);
	if(land == 0) {
	    count++;
	} else {
	    if(land->owner == 0) {
		count++;
	    }
	}
    }
    return count;
}


// 指定座標周辺で、自分の土地かつ陸地があるかどうか
int Map::nearLand(int x, int y, int from, int to, int order) {
    for(int i = from; i < to; i++) {
	Land *land = getAround(x, y, i);
	if(land != 0) {
	    if(land->owner == order) {
		// 海または海底基地以外
		if((land->kind != Land::Sea) &&
		   (land->kind != Land::SBase)) {
		    return 1;
		}
	    }
	}
    }
    return 0;
}

// 指定座標周辺で、自分の土地かつ陸地かつ荒地以外があるかどうか
int Map::nearLand2(int x, int y, int from, int to, int order) {
    for(int i = from; i < to; i++) {
	Land *land = getAround(x, y, i);
	if(land != 0) {
	    if(land->owner == order) {
		// 海または海底基地または荒地以外
		if((land->kind != Land::Sea) &&
		   (land->kind != Land::Waste) &&
		   (land->kind != Land::SBase)) {
		    return 1;
		}
	    }
	}
    }
    return 0;
}

// 人口その他を数える
void Map::estimate() {
    int size = Value::worldSize * Value::worldSize;

    // 推定可能情報を初期化
    Info::clear();

    // 全地形をなめる
    for(int i = 0; i < size; i++) {
	land[i].estimate();
    }
}

// 海際度計算
void Map::calcSea(int x, int y) {
    Land *land = getLand(x, y);
    if(land != 0) {
	if((land->kind != Land::Sea) &&
	   (land->kind != Land::SBase)) {
	    // 海、海底基地以外は関係なし
	    return;
	}
    }

    // 周囲4ヘックスへ影響を与える
    for(int i = 0; i < 61; i++) {
	Land *land = getAround(x, y, i);
	if(land != 0) {
	    land->seaLevel++;
	}
    }
}

// 領土の感化
void Map::infLand(int x, int y) {
    Land *land = getLand(x, y);
    if(land == 0) {
	// 領域外なら関係なし
	return;
    }

    if((land->kind == Land::Sea) ||
       (land->kind == Land::Waste) || 
       (land->kind == Land::Monster) || 
       (land->kind == Land::SBase) || 
       (land->kind == Land::Monument)) {
	// 上記地形は関係なし
	return;
    }

    // 中立地帯も関係なし
    if(land->owner == 0) {
	return;
    }

    // 周囲6ヘックスから影響を受ける
    int d = Util::dice(6) + 1;
    Land *land2 = getAround(x, y, d);
    if(land2 == 0) {
	return;
    }
    if(land2->owner == 0) {
	return;
    }
    
    // 他人の土地の場合
    if(land2->owner != land->owner) {
	if((land2->kind == Land::Sea) ||
	   (land2->kind == Land::Waste) || 
	   (land2->kind == Land::Monster) || 
	   (land2->kind == Land::SBase)) {
	    // 上記地形は関係なし
	    return;
	}
	// 持ち主変更
	Island *island = Info::getIsland(land->owner);
	int id = island->id;
	Island *island2 = Info::getIsland(land2->owner);
	int id2 = island2->id;
	int landValue = land->landValue();
	log(214, 0, id, id2, 0, x, y, landValue);
	land->owner = land2->owner;
    }
}

// 指定座標におけるヘックス処理
void Map::process(int x, int y) {
    Land *land = getLand(x, y);
    Island *island = 0;
    int id = 0;

    if(land->owner != 0) {
	island = Info::getIsland(land->owner);
	id = island->id;
    }
    int landValue = land->landValue();

    switch(land->kind) {
    case Land::Sea: // 海
	// 収入
	if(land->param == Land::SeaOil) {
	    log(212, 0, id, 0, 0, x, y, landValue, 1000);
	    island->money += 1000;

	    // 枯渇
	    if(Util::dice(1000) < 40) {
		log(213, 0, id, 0, 0, x, y, landValue);
		land->kind = Land::Sea;
		land->param = Land::SeaDeep;
		land->owner = 0;
	    }

	}


	return;

    case Land::Town: // 平地、町
	// 発生、成長、火災
	if(island == 0) { return; } // 念のため

	if((island->amonster > 0) && (land->param > 0)){
	    // 人造怪獣出現
	    island->amonster--;
	    disMonster(land, x, y, 0);
	    return;
	}

	if(land->param >= 100) {
	    // 都市の場合火災判定
	    if(disFire(land, id, x, y, landValue)) {
		return;
	    }
	}

	if(island->shortage == 1) {
	    // 食料不足
	    int p = ((int)land->param) - Util::dice(30) - 1;
	    if(p < 0) {
		p = 0;
	    }
	    land->param = p;
	} else {
	    if(land->param == 0) {
		// 平地の場合、村発生判定
		// 海際度によって、率を決める
		int ratio;
		if(land->seaLevel >= Land::SeaLevel2) {
		    ratio = 20;
		} else if(land->seaLevel >= Land::SeaLevel1) {
		    ratio = 10;
		} else {
		    ratio = 5;
		}
		if(Util::dice(100) < 20) {
		    int count =
			countAround(x, y, Land::Farm, 1, 7) +
			    countAround(x, y, Land::Town, 1, 7) -
				countAround(x, y, Land::Town, 1, 7, 0);
		    if(count > 0) {
			// 村発生
			land->param++;
		    }
		}
	    } else {
		// 海際度によって、限界値、率を決める
		int max, ratio;
		if(land->seaLevel >= Land::SeaLevel2) {
		    max = 100;
		    ratio = 3;
		} else if(land->seaLevel >= Land::SeaLevel1) {
		    max = 50;
		    ratio = 2;
		} else {
		    max = 20;
		    ratio = 1;
		}

		if(island->shortage == -1) {
		    // 誘致活動中
		    if(land->param < max) {
			land->param += Util::dice(10 * ratio) + 1;
			if(land->param > max) {
			    land->param = max;
			}
		    } else {
			land->param += Util::dice(ratio) + 1;
			if(land->param > 200) {
			    land->param = 200;
			}
		    }
		} else {
		    // 通常時
		    if(land->param < max) {
			land->param += Util::dice(3 * ratio) + 1;
			if(land->param > max) {
			    land->param = max;
			}
		    }
		}
	    }
	}
	break;

    case Land::Forest: // 森
	// 成長
	if(land->param < 200) {
	    land->param++;
	}
	break;

    case Land::Farm: // 農場
	if(island->shortage == 1) {
	    // 食料暴動
	    if(disRiot(land, id, x, y, landValue)) {
		return;
	    }
	}
	break;

    case Land::Factory: // 工場
	// 火災判定
	if(disFire(land, id, x, y, landValue)) {
	    return;
	}
	if(island->shortage == 1) {
	    // 食料暴動
	    if(disRiot(land, id, x, y, landValue)) {
		return;
	    }
	}
	break;

    case Land::Base:
	if(island->shortage == 1) {
	    // 食料暴動
	    if(disRiot(land, id, x, y, landValue)) {
		return;
	    }
	}

    case Land::SBase:
	{
	    int cKind = island->command;
	    int tx = island->tx;
	    int ty = island->ty;
	    int cost = Com::getCost(cKind);
	    if((cKind == Com::MissileNM) ||
	       (cKind == Com::MissilePP) ||
	       (cKind == Com::MissileLD) ||
	       (cKind == Com::MissileIS)) {
		// ミサイル発射
		// 弾道ミサイル以外は距離判定
		if(cKind != Com::MissileIS) {
		    if(distance(x, y, tx, ty) > Value::missileReach) {
			// 届かないので発射しない
			return;
		    }
		}

		// レベルの算出
		int level = land->getLevel();

		// 金があり、発射予定数が残っていてる限り撃ちつづける
		while((island->money >= cost) &&
		      (island->amount > 0) &&
		      (level > 0)) {
		    // 金、回数のカウント
		    island->money -= cost;
		    island->amount--;
		    level--;

		    // 誤差設定
		    int err;
		    if(cKind == Com::MissilePP) {
			// ＰＰミサイル
			err = 7;  // 誤差1ヘックス
		    } else {
			// その他
			err = 19; // 誤差2ヘックス
		    }

		    // 着弾点算出
		    Point p = getPoint(tx, ty, Util::dice(err));
		    if(p.x == -1) {
			// 地図外に落ちた
			log(500, 0, id, 0, cKind);
			continue;
		    }

		    // 着弾点の陸地
		    Land *tLand = getLand(p);
		    int tKind = tLand->kind;
		    int tParam = tLand->param;
		    int tLandValue = tLand->landValue();
		    Island *tIsland = Info::getIsland(tLand->owner);
		    int tid = 0;
		    if(tIsland) {
			tid = tIsland->id;
		    }
		    
		    // 防衛判定
		    if((tKind != Land::DBase) ||
		       (tParam != Land::DBaseTrue)) {
			if(countAround(p.x, p.y, Land::DBase, 1, 19,
				       Land::DBaseTrue)) {
			    // 空中爆破
			    log(510, 0, id, tid, cKind,
				p.x, p.y);
			    continue;
			}
		    }

		    // 陸破弾かどうかで分岐
		    if(cKind == Com::MissileLD) {
			// 陸破弾
			// 陸地の種類で分岐
			if(tKind == Land::Mountain) {
			    // 山
			    // 荒地になる
			    tLand->kind = Land::Waste;
			    tLand->param = Land::WasteMissile;
			    log(507, 0, id, tid, cKind,
				p.x, p.y, tLandValue);
			} else if(tKind == Land::SBase) {
			    // 海底基地
			    // 深海になる
			    tLand->kind = Land::Sea;
			    tLand->param = Land::SeaDeep;
			    tLand->owner = 0;
			    log(506, 0, id, tid, cKind,
				p.x, p.y, tLandValue);
			} else if(tKind == Land::Sea) {
			    if(tParam == Land::SeaDeep) {
				// 深海
				// 落ちただけ
				// 被害なし
				log(505, 0, id, tid, cKind,
				    p.x, p.y, tLandValue);
			    } else if(tParam == Land::SeaShoal) {
				// 浅瀬
				// 深海になる
				tLand->param = Land::SeaDeep;
				log(508, 0, id, tid, cKind,
				    p.x, p.y, tLandValue);
			    } else {
				// 油田
				// 深海になる
				tLand->param = Land::SeaDeep;
				tLand->owner = 0;
				log(506, 0, id, tid, cKind,
				    p.x, p.y, tLandValue);
			    }
			} else {
			    // その他
			    // 浅瀬になる
			    tLand->kind = Land::Sea;
			    tLand->param = Land::SeaShoal;
			    tLand->owner = 0;
			    log(509, 0, id, tid, cKind,
				p.x, p.y, tLandValue);
			}
		    } else {
			// 通常弾
			// 陸地の種類で分岐

			if(tKind == Land::Monster) {
			    // 怪獣
			    // 硬化判定などでいろいろ分岐
			    Monster::fromParam(tParam);
			    if(Monster::isHard()) {
				// 硬化中
				// ダメージなし
				log(501, 0, id, tid, cKind,
				    p.x, p.y, tLandValue);
			    } else {
				// 通常の時
				Monster::hp--;
				if(Monster::hp == 0) {
				    // 倒した
				    // 荒地にする
				    tLand->kind = Land::Waste;
				    tLand->param = Land::WasteMissile;
				    log(503, 0, id, tid, cKind,
					p.x, p.y, tLandValue);
				    int value = Monster::getValue();
				    if((value != 0) &&
				       (tid != 0)) {
					// 残骸に値段がつく
					log(504, 0, tid, 0, cKind,
					    p.x, p.y, tLandValue, value);
					tIsland->money += value;
				    }

				    // キルマーク
				    island->monster |= 1<<Monster::kind;

				    // 基地の経験値
				    land->param += Monster::getExp();
				    if((land->param) > 200) {
					land->param = 200;
				    }
				} else {
				    // ダメージのみ
				    tLand->param = Monster::toParam();
				    log(502, 0, id, tid, cKind,
					p.x, p.y, tLandValue);
				}
			    }
			} else if((tKind == Land::Waste) ||
				  (tKind == Land::Mountain) ||
				  ((tKind == Land::Sea) && 
				   (tParam != Land::SeaOil))) {
			    // 山、荒地、海(油田以外)
			    // 被害なし
			    log(505, 0, id, tid, cKind,
				p.x, p.y, tLandValue);
			} else if(tKind == Land::SBase) {
			    // 海底基地
			    // 海のふり
			    log(505, 0, id, 0, cKind,
				p.x, p.y, 0);
			} else if(tKind == Land::Sea) {
			    // 油田
			    // 海になる
			    tLand->kind = Land::Sea;
			    tLand->param = Land::SeaDeep;
			    tLand->owner = 0;
			    log(506, 0, id, tid, cKind,
				p.x, p.y, tLandValue);
			} else {
			    // その他
			    // 都市なら経験値
			    if(tKind == Land::Town) {
				land->param += tLand->param / 20;
				if((land->param) > 200) {
				    land->param = 200;
				}
				// 弾道弾でなければ難民カウント
				if(cKind != Com::MissileIS) {
				    if(id != tid) {
					island->boatPeople += tLand->param;
				    }
				}
			    }

			    // 荒地になる
			    tLand->kind = Land::Waste;
			    tLand->param = Land::WasteMissile;
			    log(507, 0, id, tid, cKind,
				p.x, p.y, tLandValue);
			}
		    }

		    // この時点ですでに基地でなくなっていれば、
		    // ループを抜ける
		    if((land->kind != Land::Base) &&
		       (land->kind != Land::SBase)) {
			break;
		    }
		}
	    }
	}
	break;

    case Land::DBase:
	if(island->shortage == 1) {
	    // 食料暴動
	    if(disRiot(land, id, x, y, landValue)) {
		return;
	    }
	}

	if(land->param == Land::DBaseFalse) {
	    // ハリボテ火災判定
	    if(disFire(land, id, x, y, landValue)) {
		return;
	    }
	}

	// 自爆
	if(land->flag == 1) {
	    log(404, 0, id, 0, 0,
		x, y, landValue);
	    wideDamage(x, y);
	}
	break;

    case Land::Monster:
	// 移動
	Monster::fromParam(land->param);
	if(Monster::isHard()) {
	    break;
	}
	if(Monster::move > land->flag) {
	    int flag = 0;
	    for(int i = 0; i < 3; i++) {
		int r = Util::dice(6) + 1;
		Point p = getPoint(x, y, r);
		if(p.x == -1) {
		    continue;
		}
		Land *tLand = getLand(p);
		int tKind = tLand->kind;
		switch(tKind) {
		case Land::Sea:
		case Land::SBase:
		case Land::Mountain:
		case Land::Monster:
		case Land::Monument:
		    break;
		default:
		    {
			// 移動
			int tLandValue = tLand->landValue();
			log(406, 0, id, 0, 0,
			    x, y, landValue);
			log(407, 0, id, 0, 0,
			    p.x, p.y, tLandValue);
			// 移動先設定
			tLand->kind = land->kind;
			tLand->param = land->param;
			tLand->flag = land->flag + 1;

			// 元居たところを荒地に
			land->kind = Land::Waste;
			land->param = Land::WasteNormal;
			land->flag = 0;

			flag = 1;
		    }
		    break;
		}
		if(flag == 1) {
		    break;
		}
	    }
	}
	break;

    case Land::Monument:
	// 発射
	if(land->flag == 1) {
	    Island *tIsland = Info::getIslandByID(island->target);
	    log(408, 0, id, 0, 0, x, y, landValue);
	    land->kind = Land::Waste;
	    land->param = Land::WasteNormal;
	    if(tIsland != 0) {
		// 着弾点算出
		Point p = getPoint(tIsland->centerX,
				   tIsland->centerY,
				   Util::dice(91));
		log(409, 0, -1, 0, 0, p.x, p.y);
		wideDamage(p.x, p.y);
	    }
	}
	break;

    default:
	break;
    }
}

// 全体災害
void Map::globalDisaster() {
    // 地震
    if(Util::dice(1000) < Value::disEarthquake1) {
	disEarthquake(Util::dice(Value::worldSize + 10) - 5,
		      Util::dice(Value::worldSize + 10) - 5);
    }

    // 津波
    if(Util::dice(1000) < Value::disTsunami) {
	disTsunami(Util::dice(Value::worldSize + 10) - 5,
		   Util::dice(Value::worldSize + 10) - 5);
    }

    // 台風
    if(Util::dice(1000) < Value::disTyphoon) {
	disTyphoon(Util::dice(Value::worldSize + 10) - 5,
		   Util::dice(Value::worldSize + 10) - 5);
    }

    // 隕石
    if(Util::dice(1000) < Value::disMeteo) {
	disMeteo(Util::dice(Value::worldSize + 10) - 5,
		 Util::dice(Value::worldSize + 10) - 5);
    }

    // 巨大隕石
    if(Util::dice(1000) < Value::disHugeMeteo) {
	int x = Util::dice(Value::worldSize + 4) - 2;
	int y = Util::dice(Value::worldSize + 4) - 2;

	// メッセージ
	log(420, 0, -1, 0, 0, x, y);
	wideDamage(x, y);
    }

    // 噴火
    if(Util::dice(1000) < Value::disEruption) {
	int x = Util::dice(Value::worldSize);
	int y = Util::dice(Value::worldSize);
	disEruption(x, y);
    }

    // 怪獣
    for(int i = 0; i < Value::disMonster; i++) {
	// 座標
	int x = Util::dice(Value::worldSize);
	int y = Util::dice(Value::worldSize);
	Land *land = getLand(x, y);
	switch(land->kind) {
	case Land::SBase:
	case Land::Sea:
	case Land::Monster:
	case Land::Monument:
	case Land::Mountain:
	    break;
	default:
	    {
		int l = 3;
		if(land->owner != 0) {
		    Island *island = Info::getIsland(land->owner);
		    int pop = island->pop;
		    if(pop < 1000) {
			break;
		    } else if(pop < 2500) {
			l = 1;
		    } else if(pop < 4000) {
			l = 2;
		    } else {
			l = 3;
		    }
		}
		disMonster(land, x, y, l);
	    }
	    break;
	}
	
    }
}



// 怪獣
void Map::disMonster(Land *land, int x, int y, int level) {
    int id = 0;
    int landValue = land->landValue();

    if(land->owner != 0) {
	Island *island = Info::getIsland(land->owner);
	id = island->id;
    }
    log(424, 0, id, 0, 0, x, y, landValue);

    Monster::makeMonster(level);
    land->kind = Land::Monster;
    land->param = Monster::toParam();
    return;
}

// 火事
int Map::disFire(Land *land, int id, int x, int y, int landValue) {
    if(countAround(x, y, Land::Forest, 1, 7)) {
	return 0;
    }
    if(countAround(x, y, Land::Monument, 1, 7)) {
	return 0;
    }
    if(Util::dice(1000) < Value::disFire) {
	land->kind = Land::Waste;
	land->param = Land::WasteNormal;
	log(401, 0, id, 0, 0, x, y, landValue);
	return 1;
    } else {
	return 0;
    }
}

// 暴動
int Map::disRiot(Land *land, int id, int x, int y, int landValue) {
    if(Util::dice(4) == 0) {
	land->kind = Land::Waste;
	land->param = Land::WasteNormal;
	log(426, 0, id, 0, 0, x, y, landValue);
	return 1;
    } else {
	return 0;
    }
}

// 地震
void Map::disEarthquake(int x, int y) {
    // 地震発生メッセージ
    log(411, 0, -1, 0, 0, x, y);
    // 10Hex内ループ
    for(int i = 0; i < 331; i++) {
	Point p = getPoint(x, y, i);
	if(p.x == -1) {
	    continue;
	}
	Land *land = getLand(p);
	int landValue = land->landValue();
	int kind = land->kind;
	int param = land->param;
	int id = 0;
	if(land->owner != 0) {
	    Island *island = Info::getIsland(land->owner);
	    id = island->id;
	}

	// 対象地形
	if(((kind == Land::Town) && (param >= 100)) ||
	   ((kind == Land::DBase) && (param == Land::DBaseFalse)) ||
	   (kind == Land::Factory)) {
	    // 1/4の確立で荒地に
	    if(Util::dice(4) == 0) {
		log(410, 0, id, 0, 0, p.x, p.y, landValue);
		land->kind = Land::Waste;
		land->param = Land::WasteNormal;
	    }
	}
    }
    return;
}

// 津波
void Map::disTsunami(int x, int y) {
    // 津波発生メッセージ
    log(412, 0, -1, 0, 0, x, y);

    // 10Hex内ループ
    for(int i = 0; i < 331; i++) {
	Point p = getPoint(x, y, i);
	if(p.x == -1) {
	    continue;
	}
	Land *land = getLand(p);
	int landValue = land->landValue();
	int kind = land->kind;
	int id = 0;
	if(land->owner != 0) {
	    Island *island = Info::getIsland(land->owner);
	    id = island->id;
	}

	// 対象地形
	if((kind != Land::Sea) &&
	   (kind != Land::Waste) &&
	   (kind != Land::Forest) &&
	   (kind != Land::Mountain) &&
	   (kind != Land::Monster) &&
	   (kind != Land::SBase) &&
	   ((kind != Land::Town) || (land->param != 0))&&
	   (kind != Land::Monument)) {
	    int c =
		countAround(p.x, p.y, Land::Sea, 1, 7) + 
		countAround(p.x, p.y, Land::SBase, 1, 7);
	    if(Util::dice(12) < (c - 1)) {
		log(410, 0, id, 0, 0, p.x, p.y, landValue);
		land->kind = Land::Waste;
		land->param = Land::WasteNormal;
	    }
	}
    }
    return;
}

// 台風
void Map::disTyphoon(int x, int y) {
    // 台風発生メッセージ
    log(413, 0, -1, 0, 0, x, y);

    // 10Hex内ループ
    for(int i = 0; i < 331; i++) {
	Point p = getPoint(x, y, i);
	if(p.x == -1) {
	    continue;
	}
	Land *land = getLand(p);
	int landValue = land->landValue();
	int kind = land->kind;
	int id = 0;
	if(land->owner != 0) {
	    Island *island = Info::getIsland(land->owner);
	    id = island->id;
	}

	// 対象地形
	if((kind == Land::Farm) ||
	   ((kind == Land::DBase) && (land->param == Land::DBaseFalse))){
	    // 森、および記念碑を数える
	    int c =
		countAround(p.x, p.y, Land::Forest, 1, 7) + 
		countAround(p.x, p.y, Land::Monument, 1, 7);
	    if(Util::dice(12) < (6 - c)) {
		log(414, 0, id, 0, 0, p.x, p.y, landValue);
		land->kind = Land::Town;
		land->param = 0;
	    }
	}
    }
    return;
}

// 流星群
void Map::disMeteo(int x, int y) {
    // 流星群メッセージ
    log(415, 0, -1, 0, 0, x, y);

    // 10Hex内ループ
    do {
	Point p = getPoint(x, y, Util::dice(331));
	if(p.x == -1) {
	    continue;
	}
	Land *land = getLand(p);
	int landValue = land->landValue();
	int kind = land->kind;
	int param = land->param;
	int id = 0;
	if(land->owner != 0) {
	    Island *island = Info::getIsland(land->owner);
	    id = island->id;
	}


	if((kind == Land::Sea) && (param == Land::SeaDeep)){
	    // 海(落ちただけ)
	    log(416, 0, id, 0, 0, p.x, p.y, landValue);
	} else if((kind == Land::Sea) && (param == Land::SeaShoal)) {
	    // 浅瀬(抉る)
	    log(417, 0, id, 0, 0, p.x, p.y, landValue);
	    land->param = Land::SeaDeep;
	} else if((kind == Land::Sea) || (kind == Land::SBase)) {
	    // 海底基地、油田(海の藻屑)
	    log(418, 0, id, 0, 0, p.x, p.y, landValue);
	    land->kind = Land::Sea;
	    land->param = Land::SeaDeep;
	    land->owner = 0;
	} else {
	    // 水没
	    log(419, 0, id, 0, 0, p.x, p.y, landValue);
	    land->kind = Land::Sea;
	    land->param = Land::SeaDeep;
	    land->owner = 0;
	}
    } while(Util::dice(2) == 0);
    return;
}

// 噴火
void Map::disEruption(int x, int y) {
    // 中心
    log(421, 0, -1, 0, 0, x, y);
    Land *land = getLand(x, y);
    land->kind = Land::Mountain;
    land->param = 0;

    // 周辺
    for(int i = 1; i < 7; i++) {
	Point p = getPoint(x, y, i);
	if(p.x == -1) {
	    continue;
	}

	Land *land = getLand(p);
	int landValue = land->landValue();
	int kind = land->kind;
	int param = land->param;
	int id = 0;
	if(land->owner != 0) {
	    Island *island = Info::getIsland(land->owner);
	    id = island->id;
	}

	if((kind == Land::Sea) || (kind == Land::SBase)) {
	    if((kind == Land::Sea) && (param == Land::SeaShoal)) {
		// 浅瀬から荒地へ
		land->kind = Land::Waste;
		land->param = Land::WasteNormal;
	    } else {
		// 海から浅瀬へ
		land->param = Land::SeaShoal;
	    }
	    int landValue = land->landValue();
	    log(422, 0, id, 0, 0, p.x, p.y, landValue);
	} else if(kind != Land::Mountain) {
	    // 荒地へ
	    land->kind = Land::Waste;
	    land->param = Land::WasteNormal;
	    log(423, 0, id, 0, 0, p.x, p.y, landValue);
	}
    }
}

// 難民
void Map::getBoatPeople(Island *island) {
    island->boatTotal = 0;
    if(island->boatPeople < 2) {
	return;
    }
    int rest = island->boatPeople / 2;
    int total = 0;
    int cx = island->centerX;
    int cy = island->centerY;
    for(int i = 0; i < 91; i++) {
	Land *land = getAround(cx, cy, i);
	if(land == 0) {
	    continue;
	}
	if(land->kind == Land::Town) {
	    if(land->param > 0) {
		int r = MIN(MIN(rest, 200 - land->param), 50);
		land->param += r;
		rest -= r;
		total += r;
		if(rest == 0) {
		    break;
		}
	    }
	}
    }
    if(total > 0) {
	island->boatTotal = total;
	log(425, 0, island->id, 0, 0, 0, 0, 0, total);
    }
}

// 広域被害
void Map::wideDamage(int x, int y) {
    for(int i = 0; i < 19; i++) {
	Point p = getPoint(x, y, i);
	if(p.x == -1) {
	    continue;
	}

	Land *land = getLand(p);
	int landValue = land->landValue();
	int kind = land->kind;
	int param = land->param;
	int id = 0;
	if(land->owner != 0) {
	    Island *island = Info::getIsland(land->owner);
	    id = island->id;
	}

	if(i > 6) {
	    // 荒地に
	    switch(kind) {
	    case Land::Sea:
	    case Land::SBase:
	    case Land::Waste:
	    case Land::Mountain:
		break;
	    default:
		log(403, 0, id, 0, 0, p.x, p.y, landValue);
		land->kind = Land::Waste;
		land->param = Land::WasteNormal;
		break;
	    }
	} else {
	    // 浅瀬
	    if((kind == Land::Sea) || (kind == Land::SBase)) {
		if((param == Land::SeaOil) || (kind == Land::SBase)) {
		    // 消し飛ぶ
		    log(403, 0, id, 0, 0, p.x, p.y, landValue);
		} else if(param == Land::SeaShoal) {
		    // えぐる
		    log(405, 0, id, 0, 0, p.x, p.y, landValue);
		}
		land->kind = Land::Sea;
		land->param = Land::SeaDeep;
		land->owner = 0;
	    } else {
		// 水没
		log(402, 0, id, 0, 0, p.x, p.y, landValue);
		land->kind = Land::Sea;
		land->param = Land::SeaShoal;
		land->owner = 0;
		if(i == 0) {
		    land->param = Land::SeaDeep;
		}
	    }
	}
    }
}


// 土地の持ち主更新
void Map::deleteIslands(int *dFlag) {
    int size = Value::worldSize * Value::worldSize;
    for(int i = 0; i < size; i++) {
	if(dFlag[land[i].owner] == 1) {
	    // 海or浅瀬にする
	    land[i].kind = Land::Sea;
	    land[i].owner = 0;
	    if(Util::dice(3) == 0) {
		land[i].param = Land::SeaDeep;
	    } else {
		land[i].param = Land::SeaShoal;
	    }
	}
    }
}

// 土地の持ち主更新
void Map::changeOwner(int *newOrder) {
    int size = Value::worldSize * Value::worldSize;
    for(int i = 0; i < size; i++) {
	land[i].changeOwner(newOrder);
    }
}

// ログ出力のエイリアス
void Map::log(int kind, int secret, int mIsland, int sIsland,
	      int cKind, int x, int y, int land, int amount) {
    HakoIO::logOutput(kind, secret, mIsland, sIsland,
		      cKind, x, y, land, amount);
}

// 距離計算
int Map::distance(int sx, int sy, int x, int y) {
    int dx, dy;
    int ym = 0;
    if(sx < x) {
	dx = x - sx;
	if((sy % 2) == 0) {
	    ym = 1;
	}
    } else {
	dx = sx - x;
	if((sy % 2) == 1) {
	    ym = 1;
	}
    }

    if(sy < y) {
	dy = y - sy;
    } else {
	dy = sy - y;
    }
    dx -= (dy + ym) / 2;
    if(dx < 0) { dx = 0; }
    return dx + dy;
}

// 地形初期化
void Land::initialize() {
    kind = Sea;
    param = SeaDeep;
    owner = 0;
}

// 地形をファイル出力
void Land::output(ofstream *ofs) {
    sprintf(HakoIO::buffer, "%x%02x%02x", kind, param, owner);
    *ofs << HakoIO::buffer;
}

// 地形をファイル入力
void Land::input(ifstream *ifs) {
    HakoIO::buffer[0] = ifs->get();
    HakoIO::buffer[1] = 0;
    kind = Util::hex(HakoIO::buffer);
    HakoIO::buffer[0] = ifs->get();
    HakoIO::buffer[1] = ifs->get();
    HakoIO::buffer[2] = 0;
    param = Util::hex(HakoIO::buffer);
    HakoIO::buffer[0] = ifs->get();
    HakoIO::buffer[1] = ifs->get();
    owner = Util::hex(HakoIO::buffer);

    // ついでにフラグ等を初期化
    flag = 0;
    seaLevel = 0;
}

// 地形をJavaScript出力
void Land::jsOut(int number) {
    // ownerなら素通し
    if(number == owner) {
	sprintf(HakoIO::buffer, "%x%02x%02x", kind, param, owner);
    } else {
	// ownerでない場合
	// 地形の種類で分岐
	switch(kind) {
	case Forest:
	case Base:
	    // 森と基地
	    sprintf(HakoIO::buffer, "%x%02x%02x", Forest, 0, owner);
	    break;

	case DBase:
	    // 防衛施設とハリボテ
	    sprintf(HakoIO::buffer, "%x%02x%02x", DBase, DBaseTrue, owner);
	    break;

	case SBase:
	    // 海底基地
	    sprintf(HakoIO::buffer, "%x%02x%02x", Sea, SeaDeep, 0);
	    break;

	default:
	    // その他は素通し
	    sprintf(HakoIO::buffer, "%x%02x%02x", kind, param, owner);
	    break;
	}
    }


    HakoIO::out(HakoIO::buffer);
}

// 人口その他を数える
void Land::estimate() {
    if(owner == 0) {
	return;
    }
    Island *island = Info::getIsland(owner);

    // 広さ
    if((kind != SBase) && (kind != Sea)) {
	island->area++;
    }

    // 各要素
    switch(kind) {
    case Town:
	island->pop += param;
	break;

    case Farm:
	island->farm += param;
	break;

    case Factory:
	island->factory += param;
	break;

    case Mountain:
	island->mountain += param;
	break;

    default:
	break;
    }
}

int Land::landValue() {
    switch(kind) {
    case Sea:
	return kind * 10 + param;

    case  Waste:
	return kind * 10;

    case Town:
	if(param == 0) {
	    return 20;
	} else if(param < 30) {
	    return 21;
	} else if(param < 100) {
	    return 22;
	} else {
	    return 23;
	}
	
    case Forest:
    case Farm:
    case Factory:
    case Base:
    case Mountain:
    case SBase:
	return kind * 10;

    case DBase:
	return kind * 10 + param;

    case Monster:
	return 200 + (param / 20);

    case Monument:
	return 300 + param;
    default:
	return 0;
    }
}

// 土地の持ち主更新
void Land::changeOwner(int *newOrder) {
    if(owner == 0) { 
	return;
    }
    owner = newOrder[owner - 1];
}

// レベルを求める
int Land::getLevel() {
    if(kind == Base) {
	if(param < 20) {
	    return 1;
	} else if(param < 60) {
	    return 2;
	} else if(param < 120) {
	    return 3;
	} else if(param < 200) {
	    return 4;
	} else {
	    return 5;
	}
    } else if(kind == SBase) {
	if(param < 50) {
	    return 1;
	} else if(param < 200) {
	    return 2;
	} else {
	    return 3;
	}
    } else {
	return 0;
    }
}
