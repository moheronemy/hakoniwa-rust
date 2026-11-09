#include "command.h"

Com *Command::coms = 0;

// 費用
const int costTable[] = {
    Com::Prepare,   5,    // 整地
    Com::Prepare2,  100,  // 地均し
    Com::Reclaim,   150,  // 埋立
    Com::Destroy,   200,  // 掘削
    Com::SellTree,  0,    // 伐採
    Com::Widen,     100,  // 領土拡張
    Com::Plant,     50,   // 植林
    Com::Farm,      20,   // 農場整備
    Com::Factory,   100,  // 工場建設
    Com::Mountain,  300,  // 採掘場整備
    Com::Base,      300,  // ミサイル基地建設
    Com::DBase,     800,  // 防衛施設建設
    Com::SBase,     8000, // 海底基地建設
    Com::Monument,  9999, // 記念碑建造
    Com::Haribote,  1,    // ハリボテ設置
    Com::MissileNM, 20,   // ミサイル発射
    Com::MissilePP, 50,   // PPミサイル発射
    Com::MissileLD, 100,  // 陸地破壊弾発射
    Com::MissileIS, 150,  // 弾道ミサイル発射
    Com::Monster,   3000, // 怪獣派遣
    Com::DoNothing, 0,    // 資金繰り
    Com::Sell,      -100, // 食料輸出
    Com::Money,     100,  // 資金援助
    Com::Food,      -100, // 食料援助
    Com::Propaganda,1000, // 誘致活動
    Com::Giveup,    0,    // 島の放棄
    Com::Move,      1000, // 拠点変更
    -1
    };

void Command::alloc() {
    coms = new Com[Value::commandMax];
}

void Command::initialize() {
    if(coms == 0) {
	Command::alloc();
    }
    for(int i = 0; i < Value::commandMax; i++) {
	coms[i].initialize();
    }
}

void Command::jsOut() {
    HakoIO::out("comData = [\n");
    for(int i = 0; i < Value::commandMax; i++) {
	coms[i].jsOut();
	if(i < (Value::commandMax - 1)) {
	    HakoIO::out(",");
	}
	HakoIO::out("\n");
    }
    HakoIO::out("];\n");
}

void Command::input(ifstream *ifs) {
    for(int i = 0; i < Value::commandMax; i++) {
	coms[i].input(ifs);
    }
}

void Command::output(ofstream *ofs) {
    for(int i = 0; i < Value::commandMax; i++) {
	coms[i].output(ofs);
    }
}

void Command::exec(Island *island, int order) {
    // 1つ目を取り出す
    Com *c = &(coms[0]);

    // 実行する
    int r = c->exec(island, order);
    if(r == 2) {
	// 回数減っただけ
	// 何もしない
    }  else {
	// ずらす
	for(int i = 0; i < (Value::commandMax - 1); i++) {
	    coms[i] = coms[i + 1];
	}

	// 末尾に資金繰り
	Com c2;
	c2.kind = Com::DoNothing;
	c2.target = 0;
	c2.x = 0;
	c2.y = 0;
	c2.amount = 0;
	coms[Value::commandMax - 1] = c2;

	if(r == 0) {
	    // 無効コマンドなら次を実行
	    exec(island, order);
	}
    }
}

void Com::jsOut() {
    sprintf(HakoIO::buffer, "[%d,%d,%d,%d,%d]",kind,target,x,y,amount);
    HakoIO::out(HakoIO::buffer);
}

void Com::input(ifstream *ifs) {
    *ifs >> kind >> target >> x >> y >> amount;
}

void Com::output(ofstream *ofs) {
    *ofs << kind << " " << target << " " <<
	x << " " << y << " " << amount << "\n";
}

void Com::initialize() {
    kind = DoNothing;
    target = 0;
    x = 0;
    y = 0;
    amount = 0;
}

int Com::exec(Island *island, int order) {
    // 各種の値
    int id = island->id;
    Land *land = Map::getLand(x, y);
    if(land == 0) {
	return 1;
    }
    int landValue = land->landValue();

    // 値のテスト(一応)
    if(x < 0) { x = 0; } 
    else if(x >=  Value::worldSize) { x = Value::worldSize - 1; }
    if(y < 0) { y = 0; } 
    else if(y >=  Value::worldSize) { x = Value::worldSize - 1; }
    if(amount < 0) { amount = 0; } 
    else if(amount >= 100) { amount = 99; }

    if(kind == DoNothing) {
	// 資金繰りチェック
	island->money += 10;
	island->absent++;
	if(island->absent >= Value::giveupTurn) {
	    // 自動放棄
	    Com c;
	    c.kind = Giveup;
	    c.target = 0;
	    c.x = 0;
	    c.y = 0;
	    c.amount = 0;
	    Command::coms[0] = c;
	    return 2;
	}
	return 1;
    }
    island->absent = 0;

    // 資金チェック
    int cost = getCost();
    if(cost > 0) {
	// 金の場合
	if(island->money < cost) {
	    // 資金不足ログ
	    log(100, 0, id, 0, kind);
	    return 0;
	}
    } else if(cost < 0) {
	// 食料の場合
	if(island->food < cost) {
	    // 食料不足ログ
	    log(101, 0, id, 0, kind);
	    return 0;
	}
    }

    // その座標が自分のものでないと出来ないやつのチェック
    switch(kind) {
    case Prepare:  // 整地
    case Prepare2: // 地均し
    case SellTree: // 伐採
    case Plant: // 植林
    case Farm: // 農場整備
    case Factory: // 工場建設
    case Mountain: // 採掘場整備
    case Base: // ミサイル基地建設
    case DBase: // 防衛施設建設
    case Monument: // 記念碑建造
    case Haribote: // ハリボテ設置
    case Move: // 拠点変更
	if(land->owner != order) {
	    // 自分の土地でないログ 
	    log(102, 0, id, 0, kind, x, y);
	    return 0;
	}
	break;
    default:
	break;
    }

    switch(kind) {
    case Prepare:  // 整地
    case Prepare2: // 地均し
	// 自分の土地である事はチェック済み
	// 山、怪獣、海底基地、海以外は成功
	if((land->kind == Land::Mountain) ||
	   (land->kind == Land::Monster) ||
	   (land->kind == Land::SBase) ||
	   (land->kind == Land::Sea)) {
	    // 土地が不適当ログ
	    log(103, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}

	// 成功
	// コスト差し引き
	island->money -= cost;

	// 平地化
	land->kind = Land::Town;
	land->param = 0;
	
	// ログ
	log(200, 0, id, 0, kind, x, y);

	if(kind == Prepare2) {
	    // 地均しはターン進まず
	    if(Util::dice(1000) < Value::disEarthquake2) {
		// 地震発生
		Map::disEarthquake(x, y);
	    }
	    return 0;
	} else {
	    if(Util::dice(1000) < Value::disMaizo) {
		// 埋蔵金発見
		int v = 100 + Util::dice(901);
		island->money += v;
		log(211, 0, id, 0, 0, 0, 0, 0, v);
	    }
	    return 1;
	}
	break;

    case Reclaim: // 埋立
	if(Map::nearLand(x, y, 1, 7, order) == 0) {
	    // 周囲に自分の土地、かつ陸地がなければ失敗
	    // 周囲に領地がないログ
	    log(104, 0, id, 0, kind, x, y);
	    return 0;
	}
	
	if((land->kind != Land::Sea) &&
	   (land->kind != Land::SBase)) {
	    // 海、海底基地以外は、不適切な土地
	    log(103, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}

	// 成功
	// コスト差し引き
	island->money -= cost;
	
	if((land->kind == Land::Sea) &&
	   (land->param == Land::SeaShoal)) {
	    // 浅瀬は荒地にする
	    land->kind = Land::Waste;
	    land->param = Land::WasteNormal;
	    land->owner = order;

	    if((Map::countAround(x, y, Land::Sea, 1, 7) +
		Map::countAround(x, y, Land::SBase, 1, 7)) <= 3) {
		// 周囲の海(or海底基地)の数が3以下
		// それらすべてを浅瀬にする
		for(int i = 1; i < 7; i++) {
		    Land *l = Map::getAround(x, y, i);
		    if(l == 0) {
			continue;
		    }
		    if((l->kind == Land::Sea) ||
		       (l->kind == Land::SBase)) {
			// 浅瀬にする
			l->kind = Land::Sea;
			l->param = Land::SeaShoal;
			l->owner = 0;
		    }
		}
	    }

	} else {
	    // それ以外は浅瀬にする
	    land->kind = Land::Sea;
	    land->param = Land::SeaShoal;
	    land->owner = 0;
	}

	// ログ
	log(200, 0, id, 0, kind, x, y);
	return 1;
	break;

    case Destroy: // 掘削
	if(Map::nearLand(x, y, 0, 37, order) == 0) {
	    // 周囲3ヘックス内に自分の土地、かつ陸地がなければ失敗
	    // 周囲に領地がないログ
	    log(104, 0, id, 0, kind, x, y);
	    return 0;
	}

	if((land->kind == Land::Monster) ||
	   (land->kind == Land::SBase)) {
	    // 怪獣、海底基地は掘削不可
	    log(103, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}

	// 対象地形によって分岐
	if(land->kind == Land::Sea) {
	    if(land->param == Land::SeaDeep) {
		// 石油掘削
		// 量が関係してくる
		if(amount == 0) {
		    amount = 1;
		}
		int c = MIN((cost * amount), island->money);
		island->money -= c;
		int ratio = c / cost;
		if(Util::dice(100) < ratio) {
		    // 油田発見
		    land->kind = Land::Sea;
		    land->param = Land::SeaOil;
		    land->owner = order;
		    log(201, 0, id, 0, kind, x, y, 0, c);
		} else {
		    // 油田発見ならず
		    log(202, 0, id, 0, kind, x, y, 0, c);
		}
		return 1;
	    } else if(land->param == Land::SeaOil) {
		// 油田は掘削できず
		// 土地が不適当ログ
		log(103, 0, id, 0, kind, x, y, landValue);
		return 0;
	    }
	} else {
	    if(land->owner != order) {
		// 海以外で自分の土地でないログ 
		log(102, 0, id, 0, kind, x, y);
		return 0;
	    }
	}

	// 通常の掘削
	island->money -= cost;
	if(land->kind == Land::Sea) {
	    // 浅瀬
	    land->param = Land::SeaDeep;
	} else if(land->kind == Land::Mountain) {
	    // 山
	    land->kind = Land::Waste;
	    land->param = Land::WasteNormal;
	} else {
	    // その他
	    land->kind = Land::Sea;
	    land->param = Land::SeaShoal;
	    land->owner = 0;
	}

	// ログ
	log(200, 0, id, 0, kind, x, y);
	return 1;

    case SellTree: // 伐採
	// 自分の土地である事はチェック済み
	// 森でないと失敗
	if(land->kind != Land::Forest) {
	    // 土地が不適当ログ
	    log(103, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}

	// 売却益
	island->money += Value::treeValue * land->param;

	// 平地にする
	land->kind = Land::Town;
	land->param = 0;

	// ログ
	log(200, 0, id, 0, kind, x, y);
	return 1;

    case Widen: // 領土拡張
	if(Map::nearLand2(x, y, 1, 7, order) == 0) {
	    // 周囲に自分の土地、かつ陸地がなければ失敗
	    // 周囲に領地がないログ
	    log(104, 0, id, 0, kind, x, y);
	    return 0;
	}

	if(land->owner == order) {
	    // すでに自分の土地
	    log(105, 0, id, 0, kind, x, y);
	    return 0;
	}

	if((land->kind != Land::Waste) &&
	   (land->owner != 0)) {
	    // 他人の土地かつ荒地でない
	    if(land->owner == 0) {
		log(106, 0, id, 0, kind, x, y);
	    } else {
		log(106, 0, id, (Info::getIsland(land->owner))->id, kind, x, y);
	    }
	    return 0;
	}

	// 怪獣、海底基地、海はだめ
	if((land->kind == Land::Monster) ||
	   (land->kind == Land::SBase) ||
	   (land->kind == Land::Sea)) {
	    // 土地が不適当ログ
	    log(103, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}

	// 成功
	land->owner = order;
	island->money -= cost;

	// ログ
	log(200, 0, id, 0, kind, x, y);
	return 1;

    case Plant: // 植林
	return buildCommand(island, land, id, cost, order, kind,
			    x, y, landValue,
			    Land::Forest, 5, 0, 0);
    case Farm: // 農場整備
	if(land->seaLevel < Land::SeaLevel1) {
	    // 土地が不適当ログ
	    log(108, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}
	return buildCommand(island, land, id, cost, order, kind,
			    x, y, landValue,
			    Land::Farm, 10, 2, 50);
    case Factory: // 工場建設
	if(land->seaLevel < Land::SeaLevel2) {
	    // 土地が不適当ログ
	    log(108, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}
	return buildCommand(island, land, id, cost, order, kind,
			    x, y, landValue,
			    Land::Factory, 30, 10, 100);

    case Base: // ミサイル基地建設
	return buildCommand(island, land, id, cost, order, kind,
			    x, y, landValue,
			    Land::Base, 0, 0, 0);

    case DBase: // 防衛施設建設
	return buildCommand(island, land, id, cost, order, kind,
			    x, y, landValue,
			    Land::DBase, 0, -1, 0);

    case Monument: // 記念碑建造
	if(amount >= Value::monumentVar) {
	    amount = 0;
	}
	return buildCommand(island, land, id, cost, order, kind,
			    x, y, landValue,
			    Land::Monument, amount, -1, 0);

    case Haribote: // ハリボテ設置
	return buildCommand(island, land, id, cost, order, kind,
			    x, y, landValue,
			    Land::DBase, 1, 0, 0);

    case Mountain: // 採掘場整備
	// 山以外はだめ
	if(land->kind != Land::Mountain) {
	    log(103, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}

	// 成功
	island->money -= cost;

	land->param += 5;
	if(land->param > 200) {
	    land->param = 200;
	}

	// 通常ログ
	log(200, 0, id, 0, kind, x, y);
	if(amount > 0) {
	    amount--;
	    if(amount > 0) {
		return 2;
	    }
	}
	return 1;

    case SBase: // 海底基地建設
	if(Map::nearLand(x, y, 0, 37, order) == 0) {
	    // 周囲3ヘックス内に自分の土地、かつ陸地がなければ失敗
	    // 周囲に領地がないログ
	    log(104, 0, id, 0, kind, x, y);
	    return 0;
	}

	// 海以外はだめ
	if((land->kind != Land::Sea) && (land->kind != Land::SeaDeep)) {
	    log(103, 0, id, 0, kind, x, y, landValue);
	    return 0;
	}

	// 成功
	island->money -= cost;

	land->kind = Land::SBase;
	land->param = 0;
	land->owner = order;

	// 通常ログ
	log(200, 1, id, 0, kind, x, y);
	log(200, 2, id, 0, kind, -999, -1);
	return 1;

    case MissileNM: // ミサイル発射
    case MissilePP: // PPミサイル発射
    case MissileLD: // 陸地破壊弾発射
    case MissileIS: // 弾道ミサイル発射
	island->tx = x;
	island->ty = y;
	island->command = kind;
	if(amount) {
	    island->amount = amount;
	} else {
	    island->amount = 1000;
	}
	log(205, 0, id, 0, kind, x, y);
	return 1;

    case Monster: // 怪獣派遣
	{
	    Island *ti = Info::getIslandByID(target);
	    if(ti == 0) {
		// ターゲットがなくて失敗
		log(107, 0, id, 0, kind);
		return 0;
	    }

	    // 成功
	    island->money -= cost;
	    ti->amonster++;
	    log(206, 0, id, ti->id, kind);
	    return 1;
	}

    case Money: // 資金援助
    case Food: // 食料援助
    case Sell: // 食料輸出
	{
	    Island *ti = 0;
	    if(kind != Sell) {
		ti = Info::getIslandByID(target);
		if(ti == 0) {
		    // ターゲットがなくて失敗
		    log(107, 0, id, 0, kind);
		    return 0;
		}
	    }

	    // 成功
	    if(kind == Money) {
		int c;
		c = MIN(island->money, cost * amount);
		if((c == 0) && (island->money != 0)) { c = cost; }
		island->money -= c;
		ti->money += c;
		log(207, 0, id, target, kind, 0, 0, 0, c);
	    } else {
		int c;
		c = MIN(island->food, (-cost) * amount);
		if((c == 0) && (island->food != 0)) { c = -cost; }
		island->food -= c;
		if(kind == Food) {
		    // 援助
		    ti->food += c;
		    log(208, 0, id, target, kind, 0, 0, 0, c);
		} else {
		    // 輸出
		    island->money += c / 10;
		    log(209, 0, id, 0, kind, 0, 0, 0, c);
		}
	    }
	    return 0;
	}

    case Propaganda: // 誘致活動
	island->money -= cost;
	island->shortage = -1;
	log(210, 0, id, 0, kind);
	return 1;

    case Giveup: // 島の放棄
	island->command = Giveup;
	return 1;

    case Move: // 拠点変更
	island->centerX = x;
	island->centerY = y;
	island->money -= cost;
	return 1;
    }

    return 0;
}

int Com::buildCommand(Island *island, Land *land, int id, int cost, int order,
		       int kind, int x, int y, int landValue,
		       int lKind, int iParam, int param, int maxparam) {
    // 都市(平地) or 目的の地形以外はだめ
    if((land->kind != Land::Town) &&
       ((param == 0 ) || (land->kind != lKind))) {
	// 土地が不適当ログ
	log(103, 0, id, 0, kind, x, y, landValue);
	return 0;
    }

    // ハリボテの上はだめ
    if((land->kind == Land::DBase) && (land->param == Land::DBaseFalse)) {
	// 土地が不適当ログ
	log(103, 0, id, 0, kind, x, y, landValue);
	return 0;
    }

    // 成功
    island->money -= cost;
    if(land->kind == lKind) {
	if(param > 0) {
	    land->param += param;
	    if(land->param > maxparam) {
		land->param = maxparam;
	    }
	} else {
	    // 自爆or記念碑飛ばし
	    land->flag = 1;

	    // 起爆装置起動ログ
	    log(203, 0, id, 0, kind, x, y, landValue);
	    island->command = kind;
	    island->target = target;
	    return 1;
	}
    } else {
	// 建設
	land->kind = lKind;
	land->param = iParam;
	land->owner = order;
    }

    if(kind == Base) {
	// 秘密ログ
	log(200, 1, id, 0, kind, x, y);
	// こころなしか・・・
	log(204, 2, id, 0, kind);
    } else if(kind == Plant) {
	// 秘密ログ
	log(200, 1, id, 0, kind, x, y);
	// こころなしか・・・
	log(204, 2, id, 0, kind);
    } else if(kind == Haribote) {
	// 秘密ログ
	log(200, 1, id, 0, kind, x, y);
	// 防衛施設のふり
	log(200, 2, id, 0, DBase, x, y);
    } else {
	// 通常ログ
	log(200, 0, id, 0, kind, x, y);
    }

    if((kind == Farm) || (kind == Factory)) {
	if(amount > 0) {
	    amount--;
	    if(amount > 0) {
		return 2;
	    }
	}
    }
    return 1;
}


// ログ出力のエイリアス
void Com::log(int kind, int secret, int mIsland, int sIsland,
	      int cKind, int x, int y, int land, int amount) {
    HakoIO::logOutput(kind, secret, mIsland, sIsland,
		      cKind, x, y, land, amount);
}

// 値段
int Com::getCost() {
    return getCost(kind);
}

// 値段
int Com::getCost(int k) {
    int i = 0;
    while(costTable[i] != -1) {
	if(k == costTable[i]) {
	    return costTable[i + 1];
	}
	i+=2;
    }
    return 0;
}
