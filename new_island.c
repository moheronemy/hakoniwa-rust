#include"new_island.h"

void NewIsland::main() {
    // データ読み込み
    HakoIO::readMapFile();

    // 島がいっぱいでないかチェック
    if(Info::totalNumber >= Value::maxNumber) {
	Util::unlock();
	HakoIO::out("mainMode = 'errorIslandFull';");
	return;
    }

    // 名前があるかチェック
    if(strcmp(Value::islandName, "") == 0) {
	Util::unlock();
	HakoIO::out("mainMode = 'errorNoName';");
	return;
    }

    // 名前が正当かチェック
    if(Util::badNameCheck(Value::islandName)) {
	Util::unlock();
	HakoIO::out("mainMode = 'errorBadName';");
	return;
    }

    // 名前の重複チェック
    if(Util::dupCheck(Value::islandName)) {
	Util::unlock();
	HakoIO::out("mainMode = 'errorDupName';");
	return;
    }

    // passwordの存在判定
    if(strcmp(Value::password, "") == 0) {
	Util::unlock();
	HakoIO::out("mainMode = 'errorNoPassword';");
	return;
    }

    // 確認用パスワード
    if(strcmp(Value::password, Value::password2)) {
	// password間違い
	Util::unlock();
	HakoIO::out("mainMode = 'errorWrongPassword';");
	return;
    }

    // 土地が空いているかのチェック
    int sx = Value::pointX;
    int sy = Value::pointY;
    if(Map::countNeutral(sx, sy, 0, 91) != 91) {
	// 5ヘックス内に中立以外の地形あり
	// 場所がない
	Util::unlock();
	HakoIO::out("mainMode = 'errorNotEnoughArea';");
	return;
    }

    // 島が作れる事に決定
    // 島番号を取得
    int id = Info::nextID;
    Info::nextID++;

    // 島の数を増やす
    Info::totalNumber++;
    int number = Info::totalNumber;

    // 島オブジェクトの取得
    Island *island = &(Info::islands[number - 1]);
    strcpy(island->name, Value::islandName);
    island->id = id;
    island->centerX = sx;
    island->centerY = sy;
    island->prize = 0;
    island->monster = 0;
    island->absent = Value::initialAbsent;
    strcpy(island->comment, "(未登録)");
    strcpy(island->password, Value::password);
    island->money = Value::initialMoney;
    island->food = Value::initialFood;
    
    // 地形作成
    // 5hex内を海に初期化
    for(int i = 19; i < 91; i++) {
	Land *land = Map::getAround(sx, sy, i);
	if(land == 0) {
	    continue;
	}
	land->kind = Land::Sea;
	land->param = Land::SeaDeep;
	land->owner = 0;
    }

    // 2hex範囲を荒地に初期化
    for(int i = 0; i < 19; i++) {
	Land *land = Map::getAround(sx, sy, i);
	if(land == 0) {
	    continue;
	}
	land->kind = Land::Waste;
	land->param = Land::WasteNormal;
	land->owner = number;
    }

    // 4Hex内に陸地を増殖
    for(int i = 0; i < 100; i++) {
	// ランダム座標
	Point p = Map::getPoint(sx, sy, Util::dice(61));
	if(p.x == -1) {
	    continue;
	}
	if(Map::countAround(p, Land::Sea, 1, 7) < 6){
	    // 周りに陸地がある場合
	    Land *land = Map::getLand(p);
	    int kind = land->kind;
	    if(kind == Land::Waste) {
		// 荒地は平地にする
		land->kind = Land::Town;
		land->param = 0;
	    } else if(land->kind == Land::Sea) {
		if(land->param == Land::SeaShoal) {
		    // 浅瀬は荒地にする
		    land->kind = Land::Waste;
		    land->param = Land::WasteNormal;
		    land->owner = number;
		} else {
		    // 海なら浅瀬にする
		    land->param = Land::SeaShoal;
		}
	    }
	}
    }

    // 森を作る
    int count = 0;
    while(count < 3) {
	// ランダム座標
	Land *land = Map::getAround(sx, sy, Util::dice(19));
	if(land == 0) {
	    continue;
	}

	// そこがすでに森でなければ、森を作る
	if(land->kind != Land::Forest) {
	    land->kind = Land::Forest;
	    land->param = 5; // 木500本
	    count++;
	}
    }

    // 村を作る
    count = 0;
    while(count < 2) {
	// ランダム座標
	Land *land = Map::getAround(sx, sy, Util::dice(19));
	if(land == 0) {
	    continue;
	}

	// そこが森か村でなければ、村を作る
	if((land->kind != Land::Forest) &&
	   ((land->kind != Land::Town) ||
	    (land->param == 0))) {
	    land->kind = Land::Town;
	    land->param = 5; // 人口500人
	    count++;
	}
    }

    // 山を作る
    count = 0;
    while(count < 1) {
	// ランダム座標
	Land *land = Map::getAround(sx, sy, Util::dice(19));
	if(land == 0) {
	    continue;
	}

	// そこが森か村でなければ、山を作る
	if((land->kind != Land::Forest) &&
	   ((land->kind != Land::Town) ||
	    (land->param == 0))) {
	    land->kind = Land::Mountain;
	    land->param = 0; // 採掘場はなし
	    count++;
	}
    }

    // 基地を作る
    count = 0;
    while(count < 1) {
	// ランダム座標
	Land *land = Map::getAround(sx, sy, Util::dice(19));
	if(land == 0) {
	    continue;
	}

	// そこが森か村か山でなければ、基地を作る
	if((land->kind != Land::Forest) &&
	   (land->kind != Land::Mountain) &&
	   ((land->kind != Land::Town) ||
	    (land->param == 0))) {
	    land->kind = Land::Base;
	    land->param = 0; // 経験地0
	    count++;
	}
    }

    // コマンド作成
    Command::initialize();
    
    // 要素推定
    Map::estimate();

    // 発見ログ書きこみ
    HakoIO::hisOutput(0, island->name);

    // データ書き込み
    HakoIO::writeComFile(id);
    HakoIO::writeInfoFile();
    HakoIO::writeMapFile();

    Util::unlock();

    Info::jsOut(0);
    HakoIO::out("mainMode = 'errorNewIsland';");
//    Sight::common();
}
