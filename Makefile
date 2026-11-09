TARGET = hakow.cgi
#TARGET = hakow.exe
CC = g++
LINKER = g++

SRCS = main.c hako_io.c template.c value.c \
       mentenance.c info.c map.c sight.c \
       new_island.c util.c toppage.c command.c owner.c \
       turn.c monster.c rename.c
OBJS = $(SRCS:.c=.o)

#CFLAGS=-c -O4 -Wall -DLOCAL
CFLAGS=-c -O2 -Wall

$(TARGET) : $(OBJS)
	     $(LINKER) $(OBJS) -o $(TARGET)

%.o : %.c
	$(CC) $(CFLAGS) $*.c

clean:
	rm $(OBJS) $(TARGET)
