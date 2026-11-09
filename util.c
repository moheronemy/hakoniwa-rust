#include"util.h"

int Util::lockFd = 0;

// 名前の正当性をチェック
int Util::badNameCheck(char *name) {
    if((strcmp(Value::islandName, "忘れ去られた") == 0) ||
       charCheck(Value::islandName, ' ') ||
       charCheck(Value::islandName, '"') ||
       charCheck(Value::islandName, ',') ||
       charCheck(Value::islandName, '?') ||
       charCheck(Value::islandName, '(') ||
       charCheck(Value::islandName, ')') ||
       charCheck(Value::islandName, '<') ||
       charCheck(Value::islandName, '>') ||
       charCheck(Value::islandName, '$')) {
	return 1;
    }
    return 0;
}

// その文字を含むかどうかチェック
int Util::charCheck(char *str, char c) {
    char *ptr = str;
    while(*ptr != 0) {
	if(c == *ptr) {
	    return 1;
	}
	ptr++;
    }
    return 0;
}

// その名前がすでに使われているかチェック
int Util::dupCheck(char *name) {
    for(int i = 0; i < Info::totalNumber; i++) {
	if(strcmp(name, Info::islands[i].name) == 0) {
	    return 1;
	}
    }
    return 0;
}

// 文字列の16進数化
int Util::hex(char *s) {
    char *ptr = s;
    int v = 0;
    while(*ptr != 0) {
	v = v * 16;
	char c = *ptr;
	if(c <= '9') {
	    c -= '0';
	} else {
	    c += 10 - 'a';
	}
	v += c;
	ptr++;
    }
    return v;
}

// 乱数(0 -> n-1)
int Util::dice(int n) {
    return random() % n;
}

// n byte以下に切り詰める
void Util::cutColumn(char *s, int n) {
    unsigned char *ptr = (unsigned char *)s;
    int count = 0;
    while(*ptr != 0) {
	if(((*ptr >= 0x81) && (*ptr <= 0x9f)) ||
	   ((*ptr >= 0xe0) && (*ptr <= 0xfc))) {
	    // 多分2byte文字
	    if(count < (n - 1)) {
		count += 2;
		ptr += 2;
	    } else {
		*ptr = 0;
		break;
	    }
	} else {
	    // 多分1byte文字
	    if(count < n) {
		if((*ptr < ' ') || (*ptr == '<') || (*ptr == '>') ||
		   (*ptr == '\\') || (*ptr == '\'') || (*ptr == '"')) {
		  *ptr = ' '; // やばそな文字をカット
		}
		count ++;
		ptr ++;
	    } else {
		*ptr = 0;
		break;
	    }
	}
    }
}

// パスワードチェック
int Util::passCheck() {
    if(strcmp(Value::password, Value::masterPassword) == 0) {
	return 2;
    }

    if(strcmp(Value::password, Value::specialPassword) == 0) {
	return 3;
    }

    Island *island = Info::getIslandByID(Value::id);

    if(island != 0) {
	if(strcmp(Value::password, island->password) == 0) {
	    return 1;
	}
    }

    // 失敗
    Util::unlock();
    HakoIO::out("mainMode = 'errorWrongPassword';");
    return 0;
}

// ロック
void Util::lock() {
#ifndef LOCAL
    lockFd = open(Value::dirName, O_RDWR);
    if(flock(lockFd, LOCK_EX)) {
	// 成功
	return;
    } else {
	// 失敗
	exit(0);
    }
#endif
}

// アンロック
void Util::unlock() {
#ifndef LOCAL
    flock(lockFd, LOCK_UN);
    close(lockFd);
#endif
}
