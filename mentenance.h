#ifndef MENTENANCE_H
#define MENTENANCE_H

#include "value.h"
#include "hako_io.h"
#include "sys/types.h"
#include "dirent.h"

class Mentenance {
public:
    static void common();
    static void makeData();

    // データ削除
    static void deleteData();

    // ディレクトリ削除
    static void removeData(int);

    // バックアップを行う
    static void backUpData();

    // バックアップを行う(実体)
    static void slideBack();

    // 更新時刻変更
    static void changeTime();

    // バックアップデータを現役化
    static void activateData();

    // 最後3文字が'cgi'かどうか判定
    static int checkTail(char *);
};

#endif
