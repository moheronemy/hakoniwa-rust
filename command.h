#ifndef COMMAND_H
#define COMMAND_H

#include<fstream.h>

#include"hako_io.h"
#include"info.h"
#include"value.h"

class Com;
class Land;
class Island;

class Command {
public:
    static Com *coms;
    static void alloc();
    static void initialize();
    static void jsOut();
    static void input(ifstream *);
    static void output(ofstream *);
    static void exec(Island *, int);
};

class Com {
public:
    // ƒRƒ}ƒ“ƒh‚Ìí—Ş
    // ®’nŒn
    static const int Prepare    = 01; // ®’n
    static const int Prepare2   = 02; // ’n‹Ï‚µ
    static const int Reclaim    = 03; // –„—§
    static const int Destroy     = 04; // Œ@í
    static const int SellTree   = 05; // ”°Ì
    static const int Widen      = 06; // —Ì“yŠg’£

    // ŒšİŒn
    static const int Plant      = 21; // A—Ñ
    static const int Farm       = 22; // ”_ê®”õ
    static const int Factory    = 23; // HêŒšİ
    static const int Mountain   = 24; // ÌŒ@ê®”õ
    static const int Base       = 25; // ƒ~ƒTƒCƒ‹Šî’nŒšİ
    static const int DBase      = 26; // –h‰q{İŒšİ
    static const int SBase      = 27; // ŠC’êŠî’nŒšİ
    static const int Monument   = 28; // ‹L”O”èŒš‘¢
    static const int Haribote   = 29; // ƒnƒŠƒ{ƒeİ’u

    // ŒR–Œn
    static const int MissileNM  = 41; // ƒ~ƒTƒCƒ‹”­Ë
    static const int MissilePP  = 42; // PPƒ~ƒTƒCƒ‹”­Ë
    static const int MissileLD  = 43; // —¤’n”j‰ó’e”­Ë
    static const int MissileIS  = 44; // ’e“¹ƒ~ƒTƒCƒ‹”­Ë
    static const int Monster    = 45; // ‰öb”hŒ­

    // ‰^‰cŒn
    static const int DoNothing  = 61; // ‘‹àŒJ‚è
    static const int Sell       = 62; // H—¿—Ao
    static const int Money      = 63; // ‘‹à‰‡•
    static const int Food       = 64; // H—¿‰‡•
    static const int Propaganda = 65; // —U’vŠˆ“®
    static const int Giveup     = 66; // “‡‚Ì•úŠü
    static const int Move       = 67; // ‹’“_•ÏX

    int getCost();
    static int getCost(int);

    // Šeƒpƒ‰ƒ[ƒ^
    int kind;
    int target;
    int x;
    int y;
    int amount;
    void initialize();
    void jsOut();
    void input(ifstream *);
    void output(ofstream *);

    int exec(Island *, int);
    int buildCommand(Island *, Land *, int, int, int, int, int,
		     int, int, int, int, int, int);
    inline void log(int, int, int, int, 
		    int = 0, int = 0, int = 0, int = 0, int = 0);
};

#endif
