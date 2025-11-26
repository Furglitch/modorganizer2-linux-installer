#ifdef __unix__
#define _GNU_SOURCE
#endif

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32

#include "win32_utils.h"

#define MO2_PATH_FILE "modorganizer2\\instance_path.txt"

#elif __unix__

#include "unix_utils.h"

#define MO2_PATH_FILE "modorganizer2/instance_path.txt"

#endif

char_t* read_path_from_file(const char* file_path) {
	errno = 0;
	FILE* file = fopen(file_path, "r");

	if (errno != 0) {
		fprintf(stderr, "ERROR: failed to open '"PATHSUBST"' - %s\n", file_path, strerror(errno));
		return NULL;
	}

	fseek(file, 0L, SEEK_END);
	size_t estimated_line_length = ftell(file);

	if (estimated_line_length == 0) {
		fprintf(stderr, "ERROR: cannot read empty file '"PATHSUBST"'\n", MO2_PATH_FILE);
		return NULL;
	}

	char* line = (char*)malloc(estimated_line_length + 1);

	fseek(file, 0L, SEEK_SET);
	int current_byte = fgetc(file);
	size_t byte_count = 0;
	do {
		line[byte_count] = (char)current_byte;
		current_byte = fgetc(file);
		byte_count++;
	} while (current_byte != EOF && current_byte != '\n');
	line[byte_count] = '\0';

	fclose(file);

#ifdef _WIN32
	char_t* wline = convert_utf8_to_wchar(line);
	free(line);
	return wline;
#else
	return line;
#endif
}

char_t* get_original_launcher(const char_t* redirector_path) {
	const char_t* filename = 0;
	size_t filename_len = 0;
	for (size_t i = 0; redirector_path[i] != '\0'; i++) {
		if (redirector_path[i] == PATH_SEPARATOR) {
			filename = redirector_path+i+1;
			filename_len = 0;
		} else {
			filename_len++;
		}
	}

	char_t* original_path = (char_t*)malloc(sizeof(char_t)*(filename_len+2));

	original_path[0] = '_';
	for (size_t i = 0; i < filename_len; i++) {
		original_path[i+1] = filename[i];
	}
	original_path[filename_len+1] = '\0';

	return original_path;
}

int check_file_access(const char_t* path) {
	errno = 0;
	check_can_execute(path);

	if (errno == 0) {
		return 1;
	} else {
		return 0;
	}
}

int MAIN(argc, argv) {
	int exit_status = 1;

	char_t *arg = NULL;
	if (argc > 1) {
		arg = argv[1];
	}

	char_t *exe_path = NULL;
	if (getenv("NO_REDIRECT") == NULL) {
		putenv("NO_REDIRECT=1");
		exe_path = read_path_from_file(MO2_PATH_FILE);
	} else {
		exe_path = get_original_launcher(argv[0]);
	}

	if (exe_path == NULL) {
		fprintf(stderr, "ERROR: could not find executable, aborting\n");
		goto exit_point;
	}

	int has_access = check_file_access(exe_path);

	if (has_access == 0) {
		fprintf(stderr, "ERROR: cannot execute '"PATHSUBST"' - %s\n", exe_path, strerror(errno));
		goto exit_point;
	}

	fprintf(stdout, "Launching '"PATHSUBST"'\n", exe_path);
	execute(exe_path, arg);
	exit_status = 0;

#ifdef DEBUG
	fprintf(stdout, "DEBUG: Process finished, press enter to exit\n");
	getchar();
#endif

exit_point:
	if (exe_path != NULL) {
		free(exe_path);
	}
	return exit_status;
}

