#ifndef UTIL_H
#define UTIL_H

#include<stdlib.h>
#include<time.h>
#include<sys/file.h>
#include "hako_io.h"
#include "info.h"

#define SWAP(X,Y) {int tmpval; tmpval = (Y); (Y) = (X); (X) = tmpval; }
#define MIN(X,Y) (((X) > (Y)) ? (Y) : (X))

class Util {
public:
    static int lockFd;

    // ロック(未実装、ダミー)
    static void lock();

    // ロック解除(未実装、ダミー)
    static void unlock();

    // 名前の正当性をチェック
    static int badNameCheck(char *);

    // その文字を含むかどうかチェック
    static int charCheck(char *, char);

    // その名前がすでに使われているかチェック
    static int dupCheck(char *);

    // 文字列の16進化
    static int hex(char *);

    // 乱数(0 -> n-1)
    static int dice(int);

    // n byte以下に切り詰める
    static void cutColumn(char *, int);

    // パスワードチェック
    static int passCheck();
};

#endif
