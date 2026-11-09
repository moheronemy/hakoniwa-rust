#ifndef MAP_H
#define MAP_H

#include<fstream.h>
#include<stdio.h>

#include"util.h"
#include"value.h"
#include"hako_io.h"
#include"monster.h"

class Island;

struct Point {
    int x;
    int y;
};

class Land;

class Map {
public:
    static Land *land;

    // 領域確保
    static void alloc();

    // 初期化
    static void initialize();

    // ファイル出力
    static void output(ofstream *);

    // ファイル入力
    static void input(ifstream *);

    // JavaScript出力
    static void jsOut(int);

    // 周辺の座標を返す
    static Point getPoint(int, int, int);

    // 指定座標のLandのポインタを返す
    static Land *getLand(int, int);

    // 指定座標のLandのポインタを返す(引数Point版)
    inline static Land *getLand(Point p) {
	return getLand(p.x, p.y);
    }

    // 指定座標の周辺のLandのポインタを返す
    static Land *getAround(int, int, int);

    // 指定座標の周辺のLandのポインタを返す(引数Point版)
    inline static Land *getAround(Point p, int n) {
	return getAround(p.x, p.y, n);
    }

    // 指定座標周辺で、その種類の土地を数える
    static int countAround(int, int, int, int, int, int = -1);

    // 指定座標周辺で、その種類の土地を数える(引数Point版)
    inline static int countAround(Point p, int kind, int from,
				  int to, int param = -1) {
	return countAround(p.x, p.y, kind, from, to, param);
    }

    // 指定座標周辺で、中立地帯を数える
    static int countNeutral(int, int, int, int);

    // 指定座標周辺で、自分の土地かつ陸地があるかどうか
    static int nearLand(int, int, int, int, int id);

    // 指定座標周辺で、自分の土地かつ陸地かつ荒地以外があるかどうか
    static int nearLand2(int, int, int, int, int id);

    // 海際度計算
    static void calcSea(int, int);

    // 領土の感化
    static void infLand(int, int);

    // 指定座標におけるヘックス処理
    static void process(int, int);

    // 全体災害
    static void globalDisaster();

    // 人口その他を数える
    static void estimate();

    // 地震
    static void disEarthquake(int, int);

    // 津波
    static void disTsunami(int, int);

    // 台風
    static void disTyphoon(int, int);

    // 流星群
    static void disMeteo(int, int);

    // 噴火
    static void disEruption(int, int);

    // 怪獣
    static void disMonster(Land *, int, int, int);

    // 火災発生
    static int disFire(Land *, int, int, int, int);

    // 食料暴動
    static int disRiot(Land *, int, int, int, int);

    // 難民
    static void getBoatPeople(Island *);

    // 広域被害
    static void wideDamage(int, int);

    // 島の消滅
    static void deleteIslands(int *);

    // 土地の持ち主更新
    static void changeOwner(int *);

    // 距離計算
    static int distance(int, int, int, int);

    // ログ出力
    inline static void log(int, int, int, int, int = 0,
			   int = 0, int = 0, int = 0, int = 0);
};

class Land {
public:
    // 地形の種類
    static const int Sea      = 0x0;
    static const int Waste    = 0x1;
    static const int Town     = 0x2;
    static const int Forest   = 0x3;
    static const int Farm     = 0x4;
    static const int Factory  = 0x5;
    static const int Base     = 0x6;
    static const int DBase    = 0x7;
    static const int Mountain = 0x8;
    static const int Monster  = 0x9;
    static const int SBase    = 0xa;
    static const int Monument = 0xb;

    // 地形のパラメータ
    // 海
    static const int SeaDeep  = 0x0;
    static const int SeaShoal = 0x1;
    static const int SeaOil   = 0x2;

    // 荒地
    static const int WasteNormal  = 0x0;
    static const int WasteMissile = 0x1;

    // 防衛施設
    static const int DBaseTrue  = 0x0;
    static const int DBaseFalse = 0x1;

    // 海際度
    static const int SeaLevel1 = 12;
    static const int SeaLevel2 = 24;


    unsigned char kind;  // 種類
    unsigned char param; // パラメータ
    unsigned char owner; // どこの領地か

    // フラグ(起爆装置など)
    unsigned char flag;

    // 海際度
    unsigned char seaLevel;

    // 初期化
    void initialize();

    // ファイル出力
    void output(ofstream *);

    // ファイル人力
    void input(ifstream *);

    // JavaScript出力
    void jsOut(int);

    // 人口その他を数える
    void estimate();

    // ログ用の土地番号を求める
    int landValue();

    // 土地の持ち主更新
    void changeOwner(int *);

    // レベルを求める
    int getLevel();
};

#endif
