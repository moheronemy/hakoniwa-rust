#include "main.h"

int main() {
    // 乱数初期化
    srandom(time(0));

    // cgi入力
    if(HakoIO::cgiInput() == 0) {
	exit(0); // 「不正入力」
    }

    // 設定読み込み
    HakoIO::readConfigFile();

    // ヘッダ出力
    Template::header();

    // クッキー内容の反映
    HakoIO::cookieInput();
    
    // 情報読みこみ
    Util::lock();
    HakoIO::readInfoFile();

    switch(Value::mainMode) {
    case MODE_MENTENANCE:
    case MODE_MENTENANCE_MAKEDATA:
    case MODE_MENTENANCE_DELETE:
    case MODE_MENTENANCE_BACKUP:
    case MODE_MENTENANCE_TIME:
    case MODE_MENTENANCE_ACTIVATE:
	// メンテ系ならターンは進まない
	break;
    default:
	// 時間が経っていればターン進行
	if((Info::turn != 0) && (Info::totalNumber != 0) &&
	   (Info::turn < Value::endTurn)){
	    if((Info::lastTime + Value::unitTime) < time(0)) {
		Value::mainMode = MODE_TURN;
	    }
	}
    }

    // 共通情報出力
    Info::commonOut();

    // モード分岐
    switch(Value::mainMode) {

    case MODE_MAP_OWNER:
	// 開発モード
	if(Util::passCheck()) {
	    Owner::main(0);
	}
	break;

    case MODE_MAP_COMMAND:
	// 開発モード(コマンド入力)
	Owner::main(1); // 内部でパスワードチェック
	break;

    case MODE_MAP:
	// 観光者モード
	Sight::common();
	break;

    case MODE_NEW:
	// 島登録モード
	NewIsland::main();
	break;

    case MODE_TURN:
	// ターン進行モード
	if(Info::totalNumber > 0) {
	    Info::lastTime += Value::unitTime;
	    Turn::main();

	    // 共通情報再出力
	    Info::commonOut();
	}

	// トップページ行き
	TopPage::main();
	break;

    case MODE_MESSAGE:
	// コメント入力モード
	Owner::main(2);
	break;

    case MODE_RENAME:
	// 名前変更モード
	Rename::main();
	break;

    case MODE_MENTENANCE:
	// メンテモード
	if(Util::passCheck() >= 2) {
	    Mentenance::common();
	}
	break;

    case MODE_MENTENANCE_MAKEDATA:
	// メンテモード、新規データ作成
	if(Util::passCheck() >= 2) {
	    Mentenance::makeData();
	}
	break;

    case MODE_MENTENANCE_DELETE:
	// メンテモード、データ削除
	if(Util::passCheck() >= 2) {
	    Mentenance::deleteData();
	}
	break;

    case MODE_MENTENANCE_TIME:
	// メンテモード、時間変更
	if(Util::passCheck() >= 2) {
	    Mentenance::changeTime();
	}
	break;

    case MODE_MENTENANCE_BACKUP:
	// メンテモード、データ削除
	if(Util::passCheck() >= 2) {
	    Mentenance::backUpData();
	}
	break;

    case MODE_MENTENANCE_ACTIVATE:
	// メンテモード、データ現役化
	if(Util::passCheck() >= 2) {
	    Mentenance::activateData();
	}
	break;

    default:
	// その他の場合はトップページ
	TopPage::main();
	break;
    }

    // フッタ出力
    Template::footer();
    return 0;
}
