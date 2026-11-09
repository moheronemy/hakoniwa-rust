#include "owner.h"

int Owner::parsePoint;

// 共通モジュール
void Owner::main(int mode) {
    // コマンド入力モードなら島IDを取得
    if(mode == 1) {
	parsePoint = 0;
	Value::id = parseNumber();
    }

    // パスワードチェック
    if(Util::passCheck() == 0) {
	return;
    }

    // 島の取得
    Island *island = Info::getIslandByID(Value::id);

    if(island == 0) {
	TopPage::main();
	return;
    }
    int id = island->id;

    // 地図、コマンド読みこみ
    HakoIO::readMapFile();
    HakoIO::readComFile(id);

    if(mode == 1) {
	// コマンド入力モードなら入力処理、書きこみ
	parseCommand();
	HakoIO::writeComFile(id);
    } else if(mode == 2) {
	// コメントモードなら書き込み
	strcpy(island->comment, Value::message);
	HakoIO::writeInfoFile();
    }
    Util::unlock();

    // 地図情報出力
    Map::jsOut(Info::getOrderByID(id));

    // 島情報出力
    Info::jsOut(id);

    // コマンド情報出力
    Command::jsOut();

    // ログ出力
    HakoIO::logJsOut(id);

    // 出力
    sprintf(HakoIO::buffer, "currentID = %d;", id);
    HakoIO::out(HakoIO::buffer);
    HakoIO::out("mainMode = 'owner';");
}

// commandListから整数一つ読む
int Owner::parseNumber() {
    char *ptr = Value::commandList + parsePoint;
    char *ptr2 = HakoIO::buffer;
    while((*ptr != ' ') && (*ptr != 0)){
	*ptr2 = *ptr;
	ptr ++;
	ptr2 ++;
	parsePoint++;
    }
    *ptr2 = 0;
    parsePoint++;
    return atoi(HakoIO::buffer);
}

void Owner::parseCommand() {
    for(int i = 0; i < Value::commandMax; i++) {
	Com *c = (Command::coms + i);
	c->kind = parseNumber();
	c->target = parseNumber();
	c->x = parseNumber();
	c->y = parseNumber();
	c->amount = parseNumber();
    }
}
