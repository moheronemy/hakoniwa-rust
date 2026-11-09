#include "sight.h"

// 共通モジュール
void Sight::common() {
    // データ読み込み
    HakoIO::readMapFile();
    Util::unlock();

    // 地図情報出力
    Map::jsOut(0);

    // 島情報出力
    Info::jsOut(0);

    // ログ出力
    HakoIO::logJsOut(0);

    HakoIO::out("mainMode = 'map';");
}
