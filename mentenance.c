#include"mentenance.h"

// 共通部分
void Mentenance::common() {
    HakoIO::out("mainMode = 'mente';\n");

    // 現役データ
    if(HakoIO::readInfoFile()) {
	// ある
	sprintf(HakoIO::buffer, "currentData = [%d, %d];\n", Info::turn,
		(unsigned int)Info::lastTime);
	HakoIO::out(HakoIO::buffer);
    } else {
	// ない
	HakoIO::out("currentData = [0, 0];\n");
    }

    // バックアップデータ
    HakoIO::out("backData = [");
    for(int i = 0; i < Value::backUpMax; i++) {
	if(HakoIO::readInfoFile(i)) {
	    sprintf(HakoIO::buffer, "[%d, %d]", Info::turn,
		    (unsigned int)Info::lastTime);
	    HakoIO::out(HakoIO::buffer);
	} else {
	    HakoIO::out("[0, 0]");
	}
	if((i + 1) < Value::backUpMax) {
	    HakoIO::out(",");
	} else {
	    HakoIO::out("];\n");
	}
    }
    Util::unlock();
}

// 新規データ作成
void Mentenance::makeData() {
    // ディレクトリ作成
    mkdir(Value::dirName, Value::dirMode);

    // 島情報を初期値にする
    Info::initialize();

    // 地図情報を初期値にする
    Map::alloc();
    Map::initialize();

    // 島情報を書き込む
    HakoIO::writeInfoFile();

    // 地図情報を書き込む
    HakoIO::writeMapFile();

    common();
}

// データを一つ消す
void Mentenance::deleteData() {
    removeData(Value::id);
    common();
}

// データディレクトリ削除
void Mentenance::removeData(int num) {
    if(num == -1) {
	strcpy(HakoIO::buffer, Value::dirName);
    } else {
	sprintf(HakoIO::buffer, "%s.bak%d", Value::dirName, num);
    }
    DIR *dp;
    dirent *de;
    dp = opendir(HakoIO::buffer);
    if(dp != 0) {
	while(1) {
	    de = readdir(dp);
	    if(de == 0) {
		break;
	    }
	    sprintf(HakoIO::buffer2, "%s/%s",
		    HakoIO::buffer, de->d_name);
	    unlink(HakoIO::buffer2);
	}
	closedir(dp);
    }
    rmdir(HakoIO::buffer);
}

// データの現役化
void Mentenance::activateData() {
    // 現役データを削除
    removeData(-1);

    // ファイル名設定
    sprintf(HakoIO::buffer, "%s.bak%d", Value::dirName, Value::id);
    rename(HakoIO::buffer, Value::dirName);

    common();
}

// データのバックアップ
void Mentenance::backUpData() {
    slideBack();
    common();
}

// データのバックアップ(実体)
void Mentenance::slideBack() {
    // 最後のデータを削除
    removeData(Value::backUpMax - 1);

    // ずらす
    for(int i = Value::backUpMax - 1; i > 0; i--) {
	sprintf(HakoIO::buffer, "%s.bak%d", Value::dirName, i - 1);
	sprintf(HakoIO::buffer2, "%s.bak%d", Value::dirName, i);
	rename(HakoIO::buffer, HakoIO::buffer2);
    }

    // 現役データをコピー
    sprintf(HakoIO::buffer, "%s.bak0", Value::dirName); // コピー先
    mkdir(HakoIO::buffer, Value::dirMode);

    DIR *dp;
    dirent *de;
    dp = opendir(Value::dirName);
    while(1) {
	de = readdir(dp);
	if(de == 0) {
	    break;
	}
	if(checkTail(de->d_name)) {
	    // コピー元ファイル名
	    sprintf(HakoIO::buffer2, "%s/%s",
		    Value::dirName, de->d_name);

	    // コピー先ファイル名
	    sprintf(HakoIO::buffer3, "%s/%s",
		    HakoIO::buffer, de->d_name);

	    ifstream ifs;
	    ofstream ofs;
	    ifs.open(HakoIO::buffer2);
	    ofs.open(HakoIO::buffer3);
	    while(!ifs.eof()) {
		ifs.getline(HakoIO::buffer4, 8192);
		if(HakoIO::buffer4[0] != 0) {
		    ofs << HakoIO::buffer4 << "\n";
		}
	    }
	}
    }
}

// 更新時刻変更
void Mentenance::changeTime() {
    HakoIO::readInfoFile();
    Info::lastTime = Value::cTime;
    HakoIO::writeInfoFile();
    common();
}

// 'cgi'で終わる名前かチェック
int Mentenance::checkTail(char *name) {
    int l = strlen(name);
    if(l < 3) {
	return 0;
    }
    if((name[l - 3] == 'c') &&
       (name[l - 2] == 'g') &&
       (name[l - 1] == 'i')) {
	return 1;
    } else {
	return 0;
    }
}
