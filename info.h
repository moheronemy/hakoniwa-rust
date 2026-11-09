#ifndef INFO_H
#define INFO_H

#include<time.h>
#include<fstream.h>

#include "value.h"
#include "hako_io.h"

class Island;

class Info {
public:
    // 共通データ
    static int turn;
    static time_t lastTime;
    static int totalNumber;
    static int nextID;

    // 各島の情報
    static Island *islands;

    // 人口順にソート、及び順位変化テーブルの書きこみ
    static void sortIslands(int *);

    // 初期データ
    static void initialize();

    // 読み込み
    static void input(ifstream *);

    // 書き込み
    static void output(ofstream *);

    // 共通情報出力
    static void commonOut();

    // estimateによって導出される値を初期化
    static void clear();

    // その番号(IDじゃなくて順位)の島を取得
    static Island *getIsland(int);

    // その番号(ID)の島を取得
    static Island *getIslandByID(int);

    // その番号(ID)の島の順位を取得
    static int getOrderByID(int);

    // JavaScript出力
    static void jsOut(int);
};

class Island {
public:
    // 賞定数
    static const int PrizeTurn1 = 0x0001;
    static const int PrizeTurn2 = 0x0002;
    static const int PrizeTurn3 = 0x0004;
    static const int PrizePros1 = 0x0008;
    static const int PrizePros2 = 0x0010;
    static const int PrizePros3 = 0x0020;
    static const int PrizeDis1  = 0x0040;
    static const int PrizeDis2  = 0x0080;
    static const int PrizeDis3  = 0x0100;
    static const int PrizeWar1  = 0x0200;
    static const int PrizeWar2  = 0x0400;
    static const int PrizeWar3  = 0x0800;

    // 島の属性
    char name[32];     // 島名
    int id;            // ID番号
    int centerX;       // 中心地のX座標
    int centerY;       // 中心地のY座標
    int prize;         // 受賞
    int monster;       // 怪獣
    int absent;        // 連続資金繰り数
    char comment[100];  // コメント
    char password[100]; // パスワード
    int money;         // 資金
    int food;          // 食料
    int pop;           // 人口
    int area;          // 広さ
    int farm;          // 農場規模
    int factory;       // 工場規模
    int mountain;      // 採掘場規模

    // 途中で使う値
    int shortage; // 飢餓状態だと1、誘致活動中だと-1、でなければ0
    int target; // 島としてのターゲット
    int tx, ty; // ミサイル等のターゲット
    int command; // 行動
    int amount; // ミサイル等の数
    int amonster; // 出現人造怪獣の数
    int boatPeople;
    int order; // 順位
    int prePop; // ターン開始時点での人口
    int boatTotal;   // 受け入れ難民

    // 読み込み
    void input(ifstream *);

    // 書き込み
    void output(ofstream *);

    // 初期状態へセット
    void initialize();

    // estimateによって導出される値を初期化
    void clear();

    // 途中で使用される値を初期化
    void clear2();

    // JavaScript出力
    void jsOut(int);

    // 収入、消費
    void income();

    // 受賞
    void getPrize(int);
    void prizeLog(int);
};

#endif
