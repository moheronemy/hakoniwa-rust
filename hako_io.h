#ifndef HAKO_IO_H
#define HAKO_IO_H

#include<iostream.h>
#include<fstream.h>
#include<stdlib.h>
#include<string.h>
#include<stdio.h>
#include<time.h>
#include<unistd.h>

#include"info.h"
#include"value.h"
#include"map.h"
#include"command.h"

class HakoIO {
public:
    // 汎用バッファ
    static char buffer[8192];
    static char buffer2[8192];
    static char buffer3[8192];
    static char buffer4[8192];

    // CGI入力の項目最大数
    static const int maxInput = 16;

    // ログファイル用ストリーム
    static ofstream *logofs;

    // 通常出力
    static void out(char *);

    // 設定ファイル読み込み
    static void readConfigFile();

    // 島情報ファイル読み込み
    static int readInfoFile(int = -1);

    // 島情報ファイル書き込み
    static int writeInfoFile();

    // コマンドファイル読み込み
    static int readComFile(int);

    // コマンドファイル書き込み
    static int writeComFile(int);

    // 地図ファイル読み込み
    static int readMapFile();

    // 地図ファイル書き込み
    static int writeMapFile();

    // CGI入力
    static int cgiInput();

    // クッキー入力
    static void cookieInput();

    // クッキー出力
    static void cookieOutput(char *, char *);

    // ログファイル名設定
    static void setLogfileName(char *, int);

    // ログファイル開く
    static void logOpen();

    // ログファイル書きこみ基本関数
    // 種類 * 機密フラグ * 主関連島 * 副関連島 *
    // コマンドの種類 * 量 *
    // x座標2 * y座標2 * 地形
    // 機密フラグ: 0通常 1関係島のみ 2無関係な島のみ
    static void logOutput(int, int, int, int,
			  int, int, int, int, int);

    // 発見ログ書きこみ
    static void hisOutput(int, char *, char * = 0);

    // 発見ログ10行に切り詰め
    static void hisCut();

    // ログファイル閉じる
    static void logClose();

    // ログファイルずらす
    static void logSlide();

    // ログファイルJavaScript出力
    static void logJsOut(int);
};

#endif
