#pragma once

#include <wchar.h>

#define PATH_SEPARATOR '\\'

#define PATHSUBST "%ls"

#define MAIN(argc, argv) wmain(int argc, wchar_t** argv)

typedef wchar_t char_t;

void execute(const char_t* path, const char_t* arg);

void check_can_execute(const char_t* path);

char_t read_character(FILE* file);

char_t* convert_utf8_to_wchar(const char* str);

char_t* str_contains(const char_t* string, const char_t* substring);

int str_compare(const char_t* lhs, const char_t* rhs);
