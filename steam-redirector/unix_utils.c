#include <unistd.h>
#include <string.h>

#include "unix_utils.h"

void execute(const char_t* path, const char_t* arg) {
	if (arg != NULL) {
		execl(path, path, arg, (char*)NULL);
	} else {
		execl(path, path, (char*)NULL);
	}
}

void check_can_execute(const char_t* path) {
	access(path, X_OK);
}

char_t* str_contains(const char_t* string, const char_t* substring) {
	return strstr(string, substring);
}

int str_compare(const char_t* lhs, const char_t* rhs) {
	return strcmp(lhs, rhs);
}
