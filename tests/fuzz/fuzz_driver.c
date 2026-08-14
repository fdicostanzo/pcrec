/*
 * fuzz_driver.c — runs one pcrec-generated matcher against a subject read
 * from a file, for differential comparison against tests/fuzz/pcre2_oracle.
 *
 * This is a separate, fuzzer-owned driver template — deliberately NOT a
 * reuse of tests/harness/driver.c, which is owned by the base-tier test
 * harness and may change shape independently (its subject comes from argv
 * with escape-decoding, not from a raw file).
 *
 * Usage: t <subject-file> [startpos]
 *   <subject-file>  path to a file whose raw bytes are the subject (no
 *                   escape decoding — the fuzzer writes exact bytes,
 *                   including NUL/newline/high bytes, directly to disk).
 *   startpos        optional byte offset to start the search from (default 0).
 *
 * Prints exactly one line to stdout, in the same format pcre2_oracle uses
 * for its match/nomatch cases (a compiled matcher never emits "cerr"):
 *   "match <start> <end>"
 *   "nomatch"
 * and exits 0. Exits 2 on a usage or file I/O error.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

static unsigned char *read_file(const char *path, size_t *out_len)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "fuzz_driver: cannot open subject file '%s'\n", path);
        exit(2);
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        fprintf(stderr, "fuzz_driver: fseek failed on '%s'\n", path);
        exit(2);
    }
    long sz = ftell(f);
    if (sz < 0) {
        fclose(f);
        fprintf(stderr, "fuzz_driver: ftell failed on '%s'\n", path);
        exit(2);
    }
    rewind(f);
    unsigned char *buf = malloc(sz > 0 ? (size_t)sz : 1);
    if (!buf) {
        fclose(f);
        fprintf(stderr, "fuzz_driver: out of memory\n");
        exit(2);
    }
    size_t got = sz > 0 ? fread(buf, 1, (size_t)sz, f) : 0;
    if (got != (size_t)sz) {
        fclose(f);
        fprintf(stderr, "fuzz_driver: short read on '%s'\n", path);
        exit(2);
    }
    fclose(f);
    *out_len = (size_t)sz;
    return buf;
}

int main(int argc, char **argv)
{
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "usage: %s <subject-file> [startpos]\n", argc > 0 ? argv[0] : "t");
        return 2;
    }

    size_t startpos = 0;
    if (argc == 3) {
        char *end;
        long v = strtol(argv[2], &end, 10);
        if (*end != '\0' || v < 0) {
            fprintf(stderr, "fuzz_driver: invalid startpos '%s'\n", argv[2]);
            return 2;
        }
        startpos = (size_t)v;
    }

    size_t len = 0;
    unsigned char *buf = read_file(argv[1], &len);

    ptrdiff_t caps[RX_NCAPS][2];
    int found = rx_search(buf, len, startpos, caps);
    if (found) {
        printf("match %td %td\n", caps[0][0], caps[0][1]);
    } else {
        printf("nomatch\n");
    }

    free(buf);
    return 0;
}
