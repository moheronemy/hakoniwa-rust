#include "template.h"

void Template::header() {
    if(Value::id != 0) {
	static char tmp[16];
	sprintf(tmp, "%d", Value::id);
	HakoIO::cookieOutput("ISLAND", tmp);
    }

    if(strcmp(Value::password, "") != 0) {
	HakoIO::cookieOutput("PASSWORD", Value::password);
    }

    out("Content-type: text/html\n\n<HTML><HEAD>"
	"<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=Shift_JIS\">"
	"\n<TITLE>箱庭諸島２＋</TITLE>\n"
	"<BASE HREF=\""
	);
    out(Value::fileDir);
    out(
	"/\">\n<SCRIPT SRC=\"hakow.js\"></SCRIPT>\n</HEAD>\n"
	"<BODY id=\"mainBody\" "
	);
    out(Value::htmlBody);
    out("></BODY>\n<SCRIPT Language=\"JavaScript\">\n");
}

void Template::footer() {
    out("\nmain();\n</SCRIPT></HTML>");
}
