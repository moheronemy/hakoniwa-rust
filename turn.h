#ifndef TURN_H
#define TURN_H

#include"map.h"
#include"mentenance.h"

class Turn {
public:
    // ターン処理実行順
    static int *order;

    // ヘックス実行順
    static int *orderX;
    static int *orderY;

    // ターン処理実行順を設定
    static void makeOrder();

    // ヘックス実行準備を設定
    static void makeOrderXY();

    // ターン進行
    static void main();

    // ログ出力
    inline static void log(int, int, int, int, int = 0,
			   int = 0, int = 0, int = 0, int = 0);

};

#endif
