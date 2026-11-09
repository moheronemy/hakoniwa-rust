#ifndef VALUE_H
#define VALUE_H

#include<sys/stat.h>
#include<fstream.h>
#include<string.h>
#include<stdio.h>
#include<stdlib.h>

#define MODE_TOPPAGE             100
#define MODE_MENTENANCE          200
#define MODE_MENTENANCE_MAKEDATA 201
#define MODE_MENTENANCE_DELETE   202
#define MODE_MENTENANCE_BACKUP   203
#define MODE_MENTENANCE_TIME     204
#define MODE_MENTENANCE_ACTIVATE 205
#define MODE_MAP                 300
#define MODE_MAP_OWNER           301
#define MODE_MAP_COMMAND         302
#define MODE_NEW                 400
#define MODE_TURN                500
#define MODE_MESSAGE             600
#define MODE_RENAME              700

class Value {
public:
    static int mode;

    // 読み込み
    static void input(ifstream *);

    // コメント行判定
    static int commentLine(char *);

    // モード切り替え行判定
    static int modeLine(char *);

    // 内容の開始点
    static char *contStart(char *);

    // 設定ファイルから読むやつ
    // マスターパス
    static char *masterPassword;

    // 特殊パス
    static char *specialPassword;

    // 画像ファイルなどを置く所
    static char *fileDir;

    // CGI実行ファイルの位置
    static char *cgiURL;

    // 掲示板の位置
    static char *bbsURL;

    // 設定ファイルの項目
    static char *configName;

    // タイトル
    static char *titleName;

    // データディレクトリの名前
    static char *dirName;

    // データディレクトリのモード
    static mode_t dirMode;

    // BODYタグのオプション
    static char *htmlBody;

    // 資金繰り数の初期値
    static int initialAbsent;

    // 最終ターン
    static int endTurn;

    // 自動放棄ターン
    static int giveupTurn;

    // 資金の初期値
    static int initialMoney;

    // 食料の初期値
    static int initialFood;

    // 地図の大きさ
    static int worldSize;

    // 島の最大数
    static int maxNumber;

    // コマンド入力数
    static int commandMax;

    // 1ターンの秒数
    static int unitTime;

    // バックアップの頻度、保持数
    static int backUpTurn;
    static int backUpMax;

    // デバッグモードかどうか
    static int debugMode;

    // 食料消費率
    static int eatenFood;

    // ログ保持ターン数
    static int logMax;

    // 木1単位の値段
    static int treeValue;

    // 記念碑の種類
    static int monumentVar;

    // 災害
    static int disFire;        // 火事
    static int disEarthquake1; // 地震(天災)
    static int disEarthquake2; // 地震(人災)
    static int disTsunami;     // 津波
    static int disTyphoon;     // 台風
    static int disMeteo;       // 隕石
    static int disHugeMeteo;   // 巨大隕石
    static int disEruption;    // 噴火
    static int disMaizo;       // 埋蔵金
    static int disMonster;     // 怪獣出現率(回数)

    // ミサイル射程
    static int missileReach;

    // 変数
    // モード
    static int mainMode;

    // 島名
    static char *islandName;

    // パスワード
    static char *password;

    // 確認用パスワード
    static char *password2;

    // 変更パスワード
    static char *password3;

    // X座標
    static int pointX;

    // Y座標
    static int pointY;

    // 島のID(メンテナンス時はデータのID、現役は-1)
    static int id;

    // 入力コマンド文字列
    static char *commandList;

    // コメント
    static char *message;

    // 変更時刻
    static unsigned int cTime;

};

#endif

