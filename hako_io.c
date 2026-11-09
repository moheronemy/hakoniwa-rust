#include"hako_io.h"

ofstream *HakoIO::logofs;

// 汎用バッファ
char HakoIO::buffer[8192];
char HakoIO::buffer2[8192];
char HakoIO::buffer3[8192];
char HakoIO::buffer4[8192];

// 16進数1ケタ(大文字限定)を整数化
#define DECODEX(X) (((X) >= 'A') ? (X) - 'A' + 10 : (X) - '0')

// (仮)
void HakoIO::out(char *s){
    cout << s;
/*    ofstream o;
    o.open("logfile", ios::app);
    o << s;
    o.close();*/
}

// 設定ファイル読み込み
void HakoIO::readConfigFile() {
    // ファイルを開く
    ifstream ifs;
    ifs.open("config.cgi");

    if(ifs.fail()) {
	exit(0);
    }

    // 島情報クラスにストリームを渡す
    Value::input(&ifs);
    return;
}

// 情報ファイルを読む
int HakoIO::readInfoFile(int number){
    // ファイル名の設定
    if(number == -1) {
	// 通常のファイル
	sprintf(buffer, "%s/info.cgi", Value::dirName);
    } else {
	// バックアップファイル
	sprintf(buffer, "%s.bak%d/info.cgi", Value::dirName, number);
    }
    
    // ファイルを開く
    ifstream ifs;
    ifs.open(buffer);
    if(ifs.fail()) {
	return 0;
    }

    // 島情報クラスにストリームを渡す
    Info::input(&ifs);
    return 1;
}

// 情報ファイルを書く
int HakoIO::writeInfoFile(){
    // ファイル名の設定
    sprintf(buffer, "%s/info.cgi", Value::dirName);
    
    // ファイルを開く
    ofstream ofs;
    ofs.open(buffer);
    if(ofs.fail()) {
	return 0;
    }

    // 島情報クラスにストリームを渡す
    Info::output(&ofs);

    return 1;
}

// コマンドファイル読み込み
int HakoIO::readComFile(int id) {
    // ファイル名の設定
    sprintf(buffer, "%s/command%d.cgi", Value::dirName, id);

    // ファイルを開く
    ifstream ifs;
    ifs.open(buffer);
    if(ifs.fail()) {
	return 0;
    }

    // コマンドクラスにストリームを渡す
    if(Command::coms == 0) {
	Command::alloc();
    }
    Command::input(&ifs);
    return 1;
}

// コマンドファイル書きこみ
int HakoIO::writeComFile(int id) {
    // ファイル名の設定
    sprintf(buffer, "%s/command%d.cgi", Value::dirName, id);

    // ファイルを開く
    ofstream ofs;
    ofs.open(buffer);
    if(ofs.fail()) {
	return 0;
    }

    // コマンドクラスにストリームを渡す
    Command::output(&ofs);
    return 1;
}

// 地図ファイルを読む
int HakoIO::readMapFile(){
    // ファイル名の設定
    sprintf(buffer, "%s/map.cgi", Value::dirName);
    
    // ファイルを開く
    ifstream ifs;
    ifs.open(buffer);
    if(ifs.fail()) {
	Info::totalNumber = 0;
	return 0;
    }

    // 地図クラスにストリームを渡す
    Map::alloc();
    Map::input(&ifs);

    return 1;
}

// 地図ファイルを書く
int HakoIO::writeMapFile(){
    // ファイル名の設定
    sprintf(buffer, "%s/map.cgi", Value::dirName);
    
    // ファイルを開く
    ofstream ofs;
    ofs.open(buffer);
    if(ofs.fail()) {
	return 0;
    }

    // 地図クラスにストリームを渡す
    Map::output(&ofs);

    return 1;
}

// クッキー入力(結果はJavaScript出力)
void HakoIO::cookieInput() {
    out("dpass = ''; did = 0;\n");

    char *httpcookie = getenv("HTTP_COOKIE");
    if(httpcookie == 0) {
	return;
    }
    int len = strlen(httpcookie);
    char *cookie = new char[len + 2];

    // クッキーをコピー
    strcpy(cookie, httpcookie);

    // 末尾に';'をつける
    cookie[len] = ';';
    cookie[len + 1] = 0;

    // フラグ
    char *cookiePass = "";
    int cookieID = 0;

    // まわす
    char *src = cookie;
    char *name = "";
    char *cont = "";
    int mode = 0;
    while(*src != 0) {
	switch(mode) {
	case 0:
	    // ' 'でなければ現在位置を名前の先頭に
	    if(*src != ' ') {
		name = src;
		mode = 1;
	    }
	    break;

	case 1:
	    // '='の場合はモード変更
	    if(*src == '=') {
		*src = 0;
		mode = 2;
	    }
	    break;

	case 2:
	    // 現在位置を内容の先頭に
	    cont = src;
	    mode = 3;
	    break;

	case 3:
	    // ';'の場合はクッキーの解釈
	    if(*src == ';') {
		*src = 0;
		mode = 0;

		// パスワード
		sprintf(buffer, "%s%sPASSWORD", Value::cgiURL,Value::configName);
		if(strcmp(buffer, name) == 0) {
		    cookiePass = cont;
		} else {
		    // 島ID
		    sprintf(buffer, "%s%sISLAND", Value::cgiURL,Value::configName);
		    if(strcmp(buffer, name) == 0) {
			cookieID = atoi(cont);
		    }
		}
	    }
	    break;
	}
	src++;
    }

    if(Value::password[0] != 0) {
	cookiePass = Value::password;
    }

    if(Value::id != 0) {
	cookieID = Value::id;
    }

    sprintf(buffer, "dpass = '%s'; did = %d;\n", cookiePass, cookieID);
    out(buffer);

    delete(cookie);
}


// CGI入力
int HakoIO::cgiInput(){
    char *line;

    // POSTの長さを求める
    char *cLen = getenv("CONTENT_LENGTH");
    if(cLen > 0) {
	// POSTの場合
	// バッファ確保
	int len = atol(cLen);
	if(len > 8192) { return 0; } // あんまり長いと却下
	line = new char[len + 3];
	if(line == 0) { return 0; }
	// POSTを読みこむ
	cin.getline(line, len + 3);
    } else {
	char *g = getenv("QUERY_STRING");
	if(g == 0)  {
	    // どちらでもない場合
	    return 1;
	}
	// GETの場合
	line = new char[strlen(g) + 3];
	strcpy(line, g);
    }


/*	    ofstream o;
	    o.open("logfile", ios::app);
	    o << line << "\n";
	    o.close();*/

    // +や%の解釈をしつつ、項目毎に分割
    char *keyword[maxInput];
    char *content[maxInput];
    for(int i = 0; i < maxInput; i++){
	keyword[i] = 0;
	content[i] = 0;
    }
    int mode = 0;
    int count = 0;
    char *pos = line;
    char *pos2 = line;
    while(*pos != 0) {
	if(mode == 0) {
	    keyword[count] = pos2;
	    mode = 1;
	} else if(mode == 2) {
	    content[count] = pos2;
	    mode = 3;
	}
	switch(*pos) {
	case '+':
	    *pos = ' ';
	    break;

	case '%':
	    // 16進の解釈
	    *pos2 = DECODEX(*(pos + 1)) * 16 + DECODEX(*(pos + 2));
	    pos += 2;
	    break;

	case '=':
	    // キーワード終了
	    *pos2 = 0;
	    mode = 2;
	    break;

	case '&':
	    // キーワード終了
	    *pos2 = 0;
	    mode = 0;
	    count++;
	    if(count >= maxInput) {
		count = 0;
	    }
	    break;

	case '\'':
	    // 都合によりダブルクォート化
	    *pos2 = '"';
	    break;

	default:
	    *pos2 = *pos;
	    break;
	}

	pos++;
	pos2++;
    }
    *pos2 = 0;
    

    // 各キーワードの解釈
    count = 0;
    while(keyword[count] != 0) {
	char *key = keyword[count];
	char *cont = content[count];

//	cout << "\n//" << key << "\n";
//	cout << "\n//" << cont << "\n";

	if(strcmp(key, "MenteMode") == 0) {
	    Value::mainMode = MODE_MENTENANCE;

	} else if(strcmp(key, "MapMode") == 0) {
	    Value::mainMode = MODE_MAP;

	} else if(strcmp(key, "OwnerMode") == 0) {
	    Value::mainMode = MODE_MAP_OWNER;

	} else if(strcmp(key, "CommandMode") == 0) {
	    Value::mainMode = MODE_MAP_COMMAND;

	} else if(strcmp(key, "NewIslandMode") == 0) {
	    Value::mainMode = MODE_NEW;

	} else if(strcmp(key, "RenameMode") == 0) {
	    Value::mainMode = MODE_RENAME;

	} else if(strcmp(key, "TurnMode") == 0) {
	    if(Value::debugMode == 1) {
		Value::mainMode = MODE_TURN;
	    }
	} else if(strncmp(key, "MesMode", 7) == 0) {
	    Value::mainMode = MODE_MESSAGE;
	    Value::id = atoi(key + 7);

	} else if(strncmp(key, "Activate", 8) == 0) {
	    Value::mainMode = MODE_MENTENANCE_ACTIVATE;
	    Value::id = atoi(key + 8);

	} else if(strcmp(key, "Second") == 0) {
	    Value::cTime = atoi(cont);

	} else if(strcmp(key, "MakeData") == 0) {
	    Value::mainMode = MODE_MENTENANCE_MAKEDATA;


	} else if(strcmp(key, "BackUp") == 0) {
	    Value::mainMode = MODE_MENTENANCE_BACKUP;

	} else if(strcmp(key, "ChangeTime") == 0) {
	    Value::mainMode = MODE_MENTENANCE_TIME;

	} else if(strncmp(key, "Delete", 6) == 0) {
	    Value::mainMode = MODE_MENTENANCE_DELETE;
	    if(strcmp(key, "Delete") == 0) {
		Value::id = -1;
	    } else {
		Value::id = atoi(key + 6);
	    }

	} else if(strcmp(key, "cname") == 0) {
	    if(cont != 0) {
		Util::cutColumn(cont, 32);
		Value::configName = cont;
	    }
	} else if(strcmp(key, "IslandName") == 0) {
	    if(cont != 0) {
		Util::cutColumn(cont, 32);
		Value::islandName = cont;
	    }

	} else if(strcmp(key, "Message") == 0) {
	    if(cont != 0) {
		Util::cutColumn(cont, 80);
		Value::message = cont;
	    }
	} else if(strcmp(key, "Password") == 0) {
	    if(cont != 0) {
		Util::cutColumn(cont, 32);
		Value::password = cont;
//		cookieOutput("PASSWORD", cont);
	    }
	} else if(strcmp(key, "Password2") == 0) {
	    if(cont != 0) {
		Util::cutColumn(cont, 32);
		Value::password2 = cont;
	    }
	} else if(strcmp(key, "Password3") == 0) {
	    if(cont != 0) {
		Util::cutColumn(cont, 32);
		Value::password3 = cont;
	    }
	} else if(strcmp(key, "PointX") == 0) {
	    Value::pointX = atoi(cont);

	} else if(strcmp(key, "PointY") == 0) {
	    Value::pointY = atoi(cont);

	} else if(strcmp(key, "Island") == 0) {
	    Value::id = atoi(cont);
//	    cookieOutput("ISLAND", cont);

	} else if(strcmp(key, "CommandList") == 0) {
	    if(cont != 0) {
		Value::commandList = cont;
	    }

	}

	count++;
    }

    return 1;
}

// クッキー出力
void HakoIO::cookieOutput(char *name, char *cont) {
    time_t tt = time(0) + 2592000; // 30日
    tm *t = gmtime(&tt);
    char *day[] = { "Sunday", "Monday", "Tuesday", "Wednesday",
		   "Thursday", "Friday", "Saturday"};
    char *mon[] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun",
		   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
    sprintf(buffer, 
	    "Set-Cookie: %s%s%s=%s; expires=%s, %02d-%s-%04d %02d:%02d:%02d GMT\n",
	    Value::cgiURL,Value::configName,name, cont, day[t->tm_wday], t->tm_mday,
	    mon[t->tm_mon], 1900 + t->tm_year, t->tm_hour, t->tm_min, t->tm_sec);
    out(buffer);
}

// ログファイル名の設定
void HakoIO::setLogfileName(char *c, int num) {
     sprintf(c, "%s/logfile%d.cgi", Value::dirName, num);
}

// ログファイル開く
void HakoIO::logOpen() {
    // ファイル名の設定
    setLogfileName(buffer, 0);
    
    // ファイルを開く
    logofs = new ofstream();
    logofs->open(buffer);
}

// ログファイル開く
void HakoIO::logClose() {
    logofs->close();
    delete(logofs);
}

// ログファイル書きこみ基本関数
// 種類 * 機密フラグ * 主関連島 * 副関連島 *
// コマンドの種類 * 量 *
// x座標2 * y座標2 * 地形
void HakoIO::logOutput(int kind, int secret, int mIsland, int sIsland,
		       int cKind, int x, int y, int land, int amount) {
    (*logofs)
	<< kind << " "
	<< secret << " "
	<< mIsland << " "
	<< sIsland << " "
	<< cKind << " "
	<< x << " "
	<< y << " "
	<< land << " "
	<< amount << "\n";
}

// 発見ログ書きこみ
void HakoIO::hisOutput(int kind, char *name, char *name2) {
    // 発見ログファイル名の設定
    sprintf(buffer, "%s/loghis.cgi", Value::dirName);
    
    // ファイルを開く(こちらは追加オープン)
    ofstream ofs;
    ofs.open(buffer, ios::app);

    // 出力
    if(!ofs.fail()) {
	ofs << Info::turn << " " << kind << " " << name << " ";
	if(name2 != 0) {
	    ofs << name2;
	} else {
	    ofs << " <>";
	}
	ofs<< "\n";

	// 閉じる
	ofs.close();
    }
}

// 発見ログを10行に切り詰め
void HakoIO::hisCut() {
    char logBuf[10][80];

    // 発見ログファイル名の設定
    sprintf(buffer, "%s/loghis.cgi", Value::dirName);
    
    // ファイルを開く
    ifstream ifs;
    ifs.open(buffer);

    // 行数を数える
    int num = 0;
    if(!ifs.fail()) {
	while(!ifs.eof()) {
	    ifs.getline(logBuf[0], 80);
	    num++;
	}
	ifs.close();
    }

    // 10行以下なら何もしない
    if(num <= 11) {
	return;
    }

    // もう一度開く
    ifs.open(buffer);

    // 10行残して読み飛ばす
    for(int i = 0; i < num - 11; i++) {
	ifs.getline(logBuf[0], 80);
    }

    // 最後の10行を読む
    for(int i = 0; i < 10; i++) {
	logBuf[i][0] = 0;
	ifs.getline(logBuf[i], 80);
    }
    ifs.close();

    // outで開く
    ofstream ofs;
    ofs.open(buffer);

    // 10行書き込む
    for(int i = 0; i < 10; i++) {
	ofs << logBuf[i] << "\n";
    }
    ofs.close();
}

// ログファイルずらす
void HakoIO::logSlide() {
    setLogfileName(buffer, Value::logMax - 1);
    unlink(buffer);
    for(int i = Value::logMax - 2; i >= 0; i--) {
	setLogfileName(buffer, i);
	setLogfileName(buffer2, i + 1);
	rename(buffer, buffer2);
    }
}

// ログファイルJavaScript出力(発見ログも)
void HakoIO::logJsOut(int id) {
    ifstream ifs;
    int kind, secret, mIsland, sIsland, cKind, x, y, land, amount, turn;
    out("logData = [");
    for(int i = 0; i < Value::logMax; i++) {
	setLogfileName(buffer, i);
	ifs.open(buffer);
	if(ifs.fail()) {
	    out("[]");
	    break;
	}
	out("[");
	while(!ifs.eof()) {
	    kind = -1;
	    ifs >> kind >> secret >> mIsland >> sIsland >> cKind
		>> x >> y >> land >> amount;
	    if(kind == -1) {
		out("[]");
		break;
	    }
	    if(((secret == 1) && (id != mIsland)) ||
	       ((secret == 2) && (id == mIsland))) {
		continue;
	    }
	    sprintf(buffer, "[%d,%d,%d,%d,%d,%d,%d,%d]",
		    kind, mIsland, sIsland, cKind, x, y, land, amount);
	    out(buffer);
	    if(!ifs.eof()) {
		out(",\n");
	    }
	}
	out("]");
	ifs.close();
	if(i < (Value::logMax - 1)) {
	    out(",");
	}
    }
    out("];");
    ifs.close();

    // 発見ログ
    sprintf(buffer, "%s/loghis.cgi", Value::dirName);
    ifs.open(buffer);
    out("\nhisData = [");
    while(!ifs.eof()) {
	kind = -1;
	ifs >> turn >> kind >> buffer2 >> buffer3;
	if(kind == -1) {
	    out("[]");
	    break;
	}
	sprintf(buffer, "[%d, %d,\"%s\",\"%s\"]", turn, kind, buffer2, buffer3);
	out(buffer);
	if(!ifs.eof()) {
	    out(",\n");
	}
    }
    out("];");
}
