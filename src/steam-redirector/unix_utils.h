#pragma once

#define PATH_SEPARATOR '/'

#define PATHSUBST "%s"

#define MAIN(argc, argv) main(int argc, char** argv)

typedef char char_t;

void execute(const char_t* path, const char_t* arg);

void check_can_execute(const char_t* path);

