#include"rename.h"

void Rename::main() {
    // パスワードチェック
    int mode = Util::passCheck();
    if(mode == 0) {
	return;
    }

    // 島の取得
    Island *island = Info::getIslandByID(Value::id);

    if(island == 0) {
	TopPage::main();
	return;
    }

    // 変更フラグ
    int flag = 0;

    // 名前がある場合は、名前を変更
    if(strcmp(Value::islandName, "") != 0) {
	if(island->money < 500) {
	    Util::unlock();
	    HakoIO::out("mainMode = 'errorNotEnoughMoney';");
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

	// 変更
	// 発見ログ書きこみ
	HakoIO::hisOutput(3, island->name,  Value::islandName);

	strcpy(island->name, Value::islandName);
	island->money -= 500;
	flag = 1;
    }


    // 変更用パスワードがある場合は、パスワードを変更
    if(strcmp(Value::password3, "") != 0) {

	// 確認用パスワード
	if(strcmp(Value::password3, Value::password2)) {
	    // password間違い
	    Util::unlock();
	    HakoIO::out("mainMode = 'errorWrongPassword';");
	    return;
	}

	// 変更
	strcpy(island->password, Value::password3);
	flag = 1;
    }

    if(flag == 0) {
	if(mode == 3) {
	    // 資金、食料増幅
	    island->money = 9999;
	    island->food = 9999;
	    HakoIO::writeInfoFile();
	    HakoIO::out("mainMode = 'errorMaxMoney';");
	} else {
	    // 変更しなかったメッセージ
	    HakoIO::out("mainMode = 'errorNotChange';");
	}
    } else {
	// 変更ログ
	HakoIO::out("mainMode = 'errorChange';");
	HakoIO::writeInfoFile();
    }

    Util::unlock();
    return;
}
