#include <unistd.h>
#include <stdio.h>

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

