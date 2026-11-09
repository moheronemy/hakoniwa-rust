#include"toppage.h"

void TopPage::main() {
    Util::unlock();
    Info::jsOut(0);
    HakoIO::out("mainMode = 'top';");
}
