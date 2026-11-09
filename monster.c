#include"monster.h"
// 何種類居るか
const int number = 8;

// 基本HP
const int baseHP[] = {2, 1, 1, 3, 2, 1, 4, 5};

// 変動体力
const int diffHP[] = {0, 1, 1, 1, 1, 0, 1, 1};

// 特殊能力
// 0 特になし
// 1 足が速い(最大2歩あるく)
// 2 足がとても速い(最大何歩あるくか不明)
// 3 奇数ターンは硬化
// 4 偶数ターンは硬化
const int skill[] = {0, 0, 3, 0, 1, 2, 4, 0};

// 経験値
const int expPoint[] = { 5, 5, 7, 12, 15, 10, 20, 30};

// 残骸の値段
const int value[] = { 0, 400, 500, 1000, 800, 300, 1500, 2000};


int Monster::kind = 0;
int Monster::hp = 0;
int Monster::move = 0;

// 種類から怪獣を作る
void Monster::makeMonster(int l) {
    int k = 0;
    switch(l) {
    case 0:
	k = 0;
	break;

    case 1:
	k = 1 + Util::dice(2);
	break;

    case 2:
	k = 1 + Util::dice(5);
	break;

    case 3:
	k = 1 + Util::dice(7);
	break;
    }
    
    int param = k * 20 + baseHP[k] + Util::dice(diffHP[k] + 1);
    fromParam(param);
}

// パラメータから各値を設定
void Monster::fromParam(int param) {
    kind = param / 20;
    hp = param % 20;
    if(skill[kind] == 1) {
	move = 2;
    } else if(skill[kind] == 2) {
	move = 9999;
    } else {
	move = 1;
    }
}

// パラメータを取得
int Monster::toParam() {
    return kind * 20 + hp;
}

// 硬化判定
int Monster::isHard() {
    int s;
    s = skill[kind];
    switch(s) {
    case 3:
	return ((Info::turn % 2) == 1) ? 1 : 0;

    case 4:
	return ((Info::turn % 2) == 0) ? 1 : 0;

    default:
	return 0;
    }
}

// 経験値
int Monster::getExp() {
    return expPoint[kind];
}

// 値段
int Monster::getValue() {
    return value[kind];
}
