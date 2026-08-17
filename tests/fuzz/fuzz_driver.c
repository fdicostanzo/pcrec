/*
 * fuzz_driver.c — runs one pcrec-generated matcher against a subject read
 * from a file, for differential comparison against tests/fuzz/pcre2_oracle.
 *
 * This is a separate, fuzzer-owned driver template — deliberately NOT a
 * reuse of tests/harness/driver.c, which is owned by the base-tier test
 * harness and may change shape independently (its subject comes from argv
 * with escape-decoding, not from a raw file).
 *
 * fuzz.py compiles this file ONCE, ahead of time, against a throwaway
 * pattern's gen.h, then links the resulting driver.o against EVERY
 * subsequent pattern's gen.o without ever recompiling driver.c again (the
 * dominant per-pattern cost is then just `pcrec` + one `gcc -c` of the
 * small generated matcher). That optimization is only sound if this file's
 * own compiled code makes NO assumption that varies per pattern. It used
 * to declare `ptrdiff_t caps[RX_NCAPS][2]` as a stack array — RX_NCAPS is a
 * preprocessor macro, baked in at THIS file's compile time from whichever
 * pattern the template happened to be built against, not the pattern the
 * resulting caps array is actually used with. Before [M4.5] every pattern's
 * RX_NCAPS was 1 (DFA-only, whole-match slot only) so the mismatch was
 * invisible; since RX_NCAPS is per-pattern (ngroups+1 on VM artifacts), any
 * group-bearing pattern that matches writes past a 1-slot stack array and
 * smashes this driver's own stack. The fix: never read RX_NCAPS at all.
 * `rx_info` (declared in gen.h, defined in each pattern's own gen.c) is
 * this ABI's reflection struct, and `rx_info.ncaps` is the SAME fact
 * available at RUNTIME, correct for whichever pattern's gen.o this driver.o
 * is linked against. The caps array is heap-allocated to that size, so this
 * file compiles once and is correct for every pattern.
 *
 * Usage: t <subject-file> [startpos]
 *   <subject-file>  path to a file whose raw bytes are the subject (no
 *                   escape decoding — the fuzzer writes exact bytes,
 *                   including NUL/newline/high bytes, directly to disk).
 *   startpos        optional byte offset to start the search from (default 0).
 *
 * Prints exactly one line to stdout, in the same format pcre2_oracle uses
 * for its match/nomatch cases (a compiled matcher never emits "cerr"):
 *   "match <s0> <e0> [<s1> <e1> ...]"   [M4.7d]: every caps[k] pair, k in
 *                                       [0, rx_info.ncaps) -- caps[0] is the
 *                                       whole match, caps[1..] are capture
 *                                       groups 1..RX_NCAPS-1 in pcrec's own
 *                                       numbering (C9: same left-to-right
 *                                       order PCRE2 uses, so this line's
 *                                       pairs line up positionally with
 *                                       pcre2_oracle's own multi-pair output
 *                                       -- see pcre2_oracle.c's header
 *                                       comment). An unset group prints as
 *                                       "-1 -1" (RX_UNSET, both slots).
 *   "nomatch"
 * or, on a VM artifact whose step or frame budget ran out before a verdict
 * (RX_ERR_STEPS / RX_ERR_FRAMES — never produced by a DFA-only artifact):
 *   "steps"
 *   "frames"
 * and exits 0. Exits 2 on a usage or file I/O error, or if rx_info.ncaps is
 * somehow 0 (would make a 0-byte allocation for a slot 0 the ABI always
 * requires — a harness bug, not a fuzzer finding).
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

    if (rx_info.ncaps < 1) {
        fprintf(stderr, "fuzz_driver: rx_info.ncaps=%d (expected >= 1)\n",
                rx_info.ncaps);
        free(buf);
        return 2;
    }
    ptrdiff_t (*caps)[2] = calloc((size_t)rx_info.ncaps, sizeof *caps);
    if (!caps) {
        fprintf(stderr, "fuzz_driver: out of memory (ncaps=%d)\n", rx_info.ncaps);
        free(buf);
        return 2;
    }

    int found = rx_search(buf, len, startpos, caps);
    if (found == 1) {
        /* [M4.7d]: every caps[k] pair, not just the whole match -- see this
         * file's own header comment. */
        printf("match");
        for (int k = 0; k < rx_info.ncaps; k++)
            printf(" %td %td", caps[k][0], caps[k][1]);
        printf("\n");
    } else if (found == 0) {
        printf("nomatch\n");
    } else if (found == RX_ERR_STEPS) {
        printf("steps\n");
    } else if (found == RX_ERR_FRAMES) {
        printf("frames\n");
    } else {
        fprintf(stderr, "fuzz_driver: rx_search returned unrecognized %d\n", found);
        free(caps);
        free(buf);
        return 2;
    }

    free(caps);
    free(buf);
    return 0;
}
