#ifndef OWNER_H
#define OWNER_H

#include"hako_io.h"
#include"value.h"
#include"command.h"
#include"toppage.h"

class Owner {
public:
    static int parsePoint;
    static void main(int);
    static int parseNumber();
    static void parseCommand();
};

#endif
