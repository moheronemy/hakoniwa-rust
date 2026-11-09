#include"turn.h"

// ターン処理実行順
int *Turn::order;
int *Turn::orderX;
int *Turn::orderY;

// ターン進行
void Turn::main() {
    // ターン進行
    Info::turn++;

    // 地図読み込み
    HakoIO::readMapFile();

    // 乱数順列の用意
    makeOrder();
    makeOrderXY();

    // ログファイルずらす
    HakoIO::logSlide();

    // ログファイル開く
    HakoIO::logOpen();

    // 海際度計算、領土の感化
    for(int x = -4; x < Value::worldSize + 4; x++) {
	for(int y = -4; y < Value::worldSize + 4; y++) {
	    Map::calcSea(x, y);
	}
    }

    int world2 = Value::worldSize * Value::worldSize;
    for(int i = 0; i < world2; i++) {
	    Map::infLand(orderX[i], orderY[i]);
    }

    // 収入、消費フェイズ
    for(int i = 0; i < Info::totalNumber; i++) {
	Island *island = Info::getIsland(i + 1);
	island->clear2();
	island->order = i + 1;
	island->income();

	// 旧人口を記録
	island->prePop = island->pop;
    }
    
    // コマンドフェイズ
    for(int i = 0; i < Info::totalNumber; i++) {
	Island *island = Info::getIsland(order[i]);
	HakoIO::readComFile(island->id);
	Command::exec(island, order[i]);
	HakoIO::writeComFile(island->id);
    }
    
    // 各ヘックス処理フェイズ
    for(int i = 0; i < world2; i++) {
	Map::process(orderX[i],orderY[i]);
    }

    // コマンドフェイズ
    for(int i = 0; i < Info::totalNumber; i++) {
	Island *island = Info::getIsland(order[i]);
	Map::getBoatPeople(island);
    }

    // 全体災害フェイズ
    Map::globalDisaster();

    // パラメータ算出
    Map::estimate();

    // 消滅判定
    int *dFlag = new int[Info::totalNumber + 1];
    dFlag[0] = 0;
    int newTotal = Info::totalNumber;
    for(int i = 0; i < Info::totalNumber; i++) {
	Island *island = Info::getIsland(order[i]);
	dFlag[order[i]] = 0;
	// 食料切り捨て
	if(island->food > 9999) {
	    int r = island->food - 9999;
	    island->food = 9999;
	    island->money += r / 10;
	}

	// 資金切り捨て
	if(island->money > 9999) {
	    island->money = 9999;
	}

	if(island->command == Com::Giveup) {
	    // 放棄で消滅
	    HakoIO::hisOutput(1, island->name);
	    island->pop = 0;
	    dFlag[order[i]] = 1;
	} else if(island->pop <= 0) {
	    // 人が消えて消滅
	    HakoIO::hisOutput(2, island->name);
	    dFlag[order[i]] = 1;
	}
	if(dFlag[order[i]] == 1) {
	    // 島数を1つ減らす
	    newTotal--;

	    // コマンドファイル消す
	    sprintf(HakoIO::buffer, "%s/command%d.cgi",
		    Value::dirName, island->id);
	    unlink(HakoIO::buffer);
	} else {
    	    // 消えなかった場合、受賞判定
	    island->getPrize(order[i]);
	}
    }
    
    if(newTotal != Info::totalNumber) {
	// 1島以上消えた場合
	// 消えた島を、地図から消去
	Map::deleteIslands(dFlag);
    }
    delete(dFlag);

    // 人口によるソート
    int *newOrder = new int[Info::totalNumber];
    Info::sortIslands(newOrder);
    Info::totalNumber = newTotal;

    // 土地の持ち主更新
    Map::changeOwner(newOrder);
    delete(newOrder);

    // ログファイル閉じる
    HakoIO::logClose();

    // 地図書きこみ
    HakoIO::writeMapFile();

    // 情報書きこみ
    HakoIO::writeInfoFile();

    // 発見ログ切り詰め
    HakoIO::hisCut();

    // バックアップ
    if((Info::turn % Value::backUpTurn) == 0) {
	Mentenance::slideBack();
    }
}

// 1～島数までの数字が一回づつ出てくる数列を作る
void Turn::makeOrder() {
    int n = Info::totalNumber;

    // 初期値
    if(n == 0) {
	order = 0;
    } else {
	order = new int[n];
    }
    for(int i = 0; i < n; i++) {
	order[i] = i + 1;
    }

    // シャッフル
    for (int i = (n - 1); i >= 0; i--) {
	int j = Util::dice(i + 1);
	if(i != j) {
	    SWAP(order[i], order[j]);
	}
    }
}

// 座標の実行順序を作る
void Turn::makeOrderXY() {
    int n = Value::worldSize * Value::worldSize;

    // 初期値
    orderX = new int[n];
    orderY = new int[n];
    int i = 0;
    for(int y = 0; y < Value::worldSize; y++) {
	for(int x = 0; x < Value::worldSize; x++) {
	    orderX[i] = x;
	    orderY[i] = y;
	    i++;
	}
    }

    // シャッフル
    for (int i = (n - 1); i >= 0; i--) {
	int j = Util::dice(i + 1);
	if(i != j) {
	    SWAP(orderX[i], orderX[j]);
	    SWAP(orderY[i], orderY[j]);
	}
    }
}

// ログ出力のエイリアス
void Turn::log(int kind, int secret, int mIsland, int sIsland,
	      int cKind, int x, int y, int land, int amount) {
    HakoIO::logOutput(kind, secret, mIsland, sIsland,
		      cKind, x, y, land, amount);
}
