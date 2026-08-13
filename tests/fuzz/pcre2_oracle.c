/*
 * pcre2_oracle — minimal PCRE2 8-bit CLI oracle for differential fuzzing.
 *
 * WHY the hand-declared ABI: this box has the PCRE2 8-bit runtime but not the
 * -dev package, so we cannot #include <pcre2.h> or link -lpcre2-8. The full
 * rationale, the declarations and the dlopen loader now live in pcre2_abi.h —
 * moved there by PC-3, when a second consumer (tests/registry/pcre2_check.c)
 * would otherwise have COPIED them. Adapted from the R1 semantics critic's
 * ad-hoc pcre2try.c (session scratchpad), which established this approach
 * against the same PCRE2 10.46 runtime.
 *
 * ALL COMPILES HERE USE options = 0. No PCRE2_UTF, no PCRE2_UCP, no
 * PCRE2_CASELESS. Anything this oracle says is a statement about default
 * 8-bit mode only; it measures no UTF conformance whatsoever.
 *
 * Usage: pcre2_oracle 'PATTERN' <subject-file> [startpos]
 *   PATTERN      the regex, taken verbatim from argv (a C string — argv
 *                entries can never contain embedded NULs, so this is safe
 *                even though patterns generally may contain any byte).
 *   subject-file path to a file whose raw bytes are the subject; using a
 *                file (not argv) lets subjects contain NUL bytes and
 *                arbitrary binary content that argv/the shell can't carry
 *                reliably.
 *   startpos     optional byte offset to start the search from (default 0).
 *
 * Prints exactly one line to stdout:
 *   "match <start> <end>"   PCRE2 found a match; byte offsets, end exclusive
 *   "nomatch"               PCRE2 compiled the pattern and genuinely found
 *                           no match (pcre2_match_8 returned exactly
 *                           PCRE2_ERROR_NOMATCH, i.e. -1)
 *   "cerr <code>"           PCRE2 rejected the pattern at compile time;
 *                           <code> is the PCRE2 error code (see
 *                           pcre2_get_error_message_8); the human-readable
 *                           message is additionally printed to stderr
 *   "mlimit <code>"         pcre2_match_8 returned some OTHER negative code
 *                           (e.g. -47 "match limit exceeded", or a
 *                           recursion/heap/depth limit) -- PCRE2's own
 *                           backtracking-budget safeguard tripped before it
 *                           could determine match/no-match. This is NOT a
 *                           verdict and must not be compared against
 *                           pcrec's output: pcrec's DFA has no backtracking
 *                           and cannot hit this class of limit, so treating
 *                           an "mlimit" outcome as if it meant "nomatch"
 *                           would manufacture false content divergences on
 *                           exactly the catastrophic-backtracking-shaped
 *                           patterns pcrec's architecture is designed to
 *                           handle better. Confirmed empirically during the
 *                           M2.5 build (see README.md): pattern
 *                           "(((b{0,})){2,}){0,}$" against a 9-byte run of
 *                           'b' plus one non-'b' byte returns rc=-47 (not
 *                           -1) from pcre2_match_8.
 *
 * Exit codes: 0 normal (any of the three outcomes above was printed),
 * 2 usage error, 3 failed to load/resolve the PCRE2 library at runtime.
 */
/* FIRST: pcre2_abi.h defines _GNU_SOURCE, which must precede every libc
 * header in the translation unit or dlinfo() is not declared. */
#include "pcre2_abi.h"

#include <errno.h>
#include <stdlib.h>

static Pcre2Abi pcre2;

/* This consumer's policy on a missing library is FAIL HARD: an absent oracle
 * means no ground truth, and a fuzz run that silently proceeded without one
 * would report agreement it never measured. tests/registry/pcre2_check.c takes
 * the opposite policy for the opposite reason — see pcre2_abi.h. */
static void load_pcre2(void)
{
    char why[512];
    if (pcre2_abi_load(&pcre2, why, sizeof why) == PCRE2_ABI_OK) return;
    fprintf(stderr,
        "pcre2_oracle: %s\n"
        "  Install the PCRE2 8-bit runtime (Debian/Ubuntu package\n"
        "  'libpcre2-8-0') to use this oracle.\n", why);
    exit(3);
}

static unsigned char *read_file(const char *path, size_t *out_len)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "pcre2_oracle: cannot open subject file '%s': %s\n",
                path, strerror(errno));
        exit(2);
    }
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); fprintf(stderr, "pcre2_oracle: fseek failed on '%s'\n", path); exit(2); }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); fprintf(stderr, "pcre2_oracle: ftell failed on '%s'\n", path); exit(2); }
    rewind(f);
    unsigned char *buf = malloc(sz > 0 ? (size_t)sz : 1);
    if (!buf) { fclose(f); fprintf(stderr, "pcre2_oracle: out of memory\n"); exit(2); }
    size_t got = sz > 0 ? fread(buf, 1, (size_t)sz, f) : 0;
    if (got != (size_t)sz) {
        fclose(f);
        fprintf(stderr, "pcre2_oracle: short read on '%s'\n", path);
        exit(2);
    }
    fclose(f);
    *out_len = (size_t)sz;
    return buf;
}

/* R2-PR5: the oracle previously verified only that symbols RESOLVED. If
 * dlopen picked up a different libpcre2-8 (e.g. pre-10.43, where {,n}
 * semantics differ — see docs/dev/upstream_issues.md U2), it would have produced
 * silently wrong "ground truth". Callers can now query the version and record
 * it alongside results. */
static void print_version(void)
{
    char buf[64];
    pcre2_abi_version(&pcre2, buf, sizeof buf);
    printf("%s\n", buf);
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        load_pcre2();
        print_version();
        return 0;
    }
    if (argc < 3 || argc > 4) {
        fprintf(stderr, "usage: %s 'PATTERN' <subject-file> [startpos]\n", argv[0]);
        return 2;
    }
    const char *pat = argv[1];
    const char *subject_path = argv[2];
    size_t startpos = 0;
    if (argc == 4) {
        char *end;
        long v = strtol(argv[3], &end, 10);
        if (*end != '\0' || v < 0) {
            fprintf(stderr, "pcre2_oracle: invalid startpos '%s'\n", argv[3]);
            return 2;
        }
        startpos = (size_t)v;
    }

    load_pcre2();

    size_t subjlen = 0;
    unsigned char *subj = read_file(subject_path, &subjlen);

    int errorcode;
    PCRE2_SIZE erroffset;
    pcre2_code_8 *re = pcre2.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                  &errorcode, &erroffset, NULL);
    if (!re) {
        unsigned char buf[256];
        pcre2.get_error_message(errorcode, buf, sizeof buf);
        fprintf(stderr, "pcre2_oracle: compile error at offset %zu: %s\n",
                (size_t)erroffset, buf);
        printf("cerr %d\n", errorcode);
        free(subj);
        return 0;
    }

    pcre2_match_data_8 *md = pcre2.match_data_create(16, NULL);
    int rc = pcre2.match(re, (PCRE2_SPTR)subj, subjlen, startpos, 0, md, NULL);
    if (rc == -1) {
        /* PCRE2_ERROR_NOMATCH: a genuine verdict. */
        printf("nomatch\n");
    } else if (rc < 0) {
        /* Some other negative code (match/heap/depth limit, ...): PCRE2's
         * own safeguard tripped, not a match/no-match verdict. See the
         * header comment's "mlimit" documentation. */
        unsigned char buf[256];
        pcre2.get_error_message(rc, buf, sizeof buf);
        fprintf(stderr, "pcre2_oracle: match-time limit hit (rc=%d): %s\n", rc, buf);
        printf("inconclusive %d\n", rc);
    } else {
        PCRE2_SIZE *ov = pcre2.get_ovector_pointer(md);
        printf("match %zu %zu\n", (size_t)ov[0], (size_t)ov[1]);
    }

    pcre2.match_data_free(md);
    pcre2.code_free(re);
    free(subj);
    return 0;
}
