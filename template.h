#ifndef TEMPLATE_H
#define TEMPLATE_H

#include"value.h"
#include"hako_io.h"

class Template {
public:
    static inline void out(char *s) {
	HakoIO::out(s);
    }
    
    static void header();
    static void footer();
};

#endif
