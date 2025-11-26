#include <io.h>
#include <process.h>
#include <stdio.h>
#include <windows.h>

#include "win32_utils.h"

void execute(const char_t* path, const char_t* arg) {
	if (arg != NULL) {
		_wexecl(path, path, arg, NULL);
	} else {
		_wexecl(path, path, NULL);
	}
}

void check_can_execute(const char_t* path) {
	_waccess(path, 0);
}

void log_conversion_error() {
	int error_code = GetLastError();

	if (error_code == ERROR_NO_UNICODE_TRANSLATION) {
		fprintf(stderr, "ERROR: File contains invalid unicode data\n");
	} else {
		fprintf(stderr, "ERROR: conversion failed with code %d", error_code);
	}
}

char_t* convert_utf8_to_wchar(const char* str) {
	int character_count = MultiByteToWideChar(CP_UTF8, 0, str, -1, NULL, 0);
	char_t* converted_str = (char_t*)malloc((character_count + 1) * sizeof(char_t));
	int bytes_written = MultiByteToWideChar(CP_UTF8, 0, str, -1, converted_str, character_count);

	if (bytes_written == 0) {
		log_conversion_error();
		return NULL;
	}

	return converted_str;
}

