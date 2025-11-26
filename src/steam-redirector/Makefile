GNU_C=gcc
WIN_C=x86_64-w64-mingw32-gcc
WIN_FLAGS=-municode -static -static-libgcc -Bstatic
WIN_SRC=main.c win32_utils.c

default: main.exe

all: main.exe main

# this build is mostly for debugging purposes
main: main.c unix_utils.c
	$(GNU_C) -o main unix_utils.c main.c

main.exe: $(WIN_SRC)
	$(WIN_C) $(WIN_FLAGS) -mwindows -o main.exe $^

main_debug.exe: $(WIN_SRC)
	$(WIN_C) $(WIN_FLAGS) -D DEBUG -o main_debug.exe $^
