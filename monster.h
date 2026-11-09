#ifndef MONSTER_H
#define MONSTER_H

#include"value.h"
#include"info.h"

class Monster {
public:
    static int kind;
    static int hp;
    static int move;

    // 種類から怪獣を作る
    static void makeMonster(int);

    // パラメータから各値を設定
    static void fromParam(int);

    // パラメータを取得
    static int toParam();

    // 硬化判定
    static int isHard();

    // 経験値
    static int getExp();

    // 値段
    static int getValue();
};

#endif
