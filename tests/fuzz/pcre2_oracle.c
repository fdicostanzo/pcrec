/*
 * pcre2_oracle — minimal PCRE2 8-bit CLI oracle for differential fuzzing.
 *
 * WHY the hand-declared ABI: this box has the PCRE2 8-bit runtime library
 * (libpcre2-8-0, providing /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0.*) but
 * NOT the -dev package: there is no pcre2.h, no unversioned libpcre2-8.so
 * symlink, and no pkg-config file (verified: `pkg-config --exists
 * libpcre2-8` fails, and `gcc -lpcre2-8` fails to find the library at link
 * time — only the .so.0 SONAME file exists). We cannot #include <pcre2.h>
 * or link with -lpcre2-8. Instead we hand-declare the small slice of the
 * PCRE2 8-bit ABI we need (opaque struct pointers + extern function
 * prototypes matching the documented/stable PCRE2 8-bit API) and load the
 * library at runtime with dlopen()/dlsym(), which requires neither headers
 * nor a dev symlink. This also lets us fail with our own clear diagnostic
 * if the library is ever missing, instead of a cryptic dynamic-linker error
 * at process startup. Adapted from the R1 semantics critic's ad-hoc
 * pcre2try.c (session scratchpad), which established this same approach
 * against the same PCRE2 10.46 runtime.
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
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---- Hand-declared PCRE2 8-bit ABI (see header comment for why) ---- */

typedef size_t PCRE2_SIZE;
typedef const unsigned char *PCRE2_SPTR;
typedef struct pcre2_real_code_8 pcre2_code_8;
typedef struct pcre2_real_match_data_8 pcre2_match_data_8;
typedef struct pcre2_real_general_context_8 pcre2_general_context_8;
typedef struct pcre2_real_compile_context_8 pcre2_compile_context_8;
typedef struct pcre2_real_match_context_8 pcre2_match_context_8;

typedef pcre2_code_8 *(*fn_compile)(PCRE2_SPTR pattern, PCRE2_SIZE length,
    uint32_t options, int *errorcode, PCRE2_SIZE *erroroffset,
    pcre2_compile_context_8 *ccontext);
typedef pcre2_match_data_8 *(*fn_match_data_create)(uint32_t ovecsize,
    pcre2_general_context_8 *gcontext);
typedef int (*fn_match)(const pcre2_code_8 *code, PCRE2_SPTR subject,
    PCRE2_SIZE length, PCRE2_SIZE startoffset, uint32_t options,
    pcre2_match_data_8 *match_data, pcre2_match_context_8 *mcontext);
typedef PCRE2_SIZE *(*fn_get_ovector_pointer)(pcre2_match_data_8 *match_data);
typedef void (*fn_match_data_free)(pcre2_match_data_8 *match_data);
typedef void (*fn_code_free)(pcre2_code_8 *code);
typedef int (*fn_get_error_message)(int errorcode, unsigned char *buffer,
    PCRE2_SIZE bufflen);

static fn_compile             p_compile;
static fn_match_data_create   p_match_data_create;
static fn_match               p_match;
static fn_get_ovector_pointer p_get_ovector_pointer;
static fn_match_data_free     p_match_data_free;
static fn_code_free           p_code_free;
static fn_get_error_message   p_get_error_message;

/* Candidate names to dlopen: the SONAME first (always present with the
 * runtime package), then the unversioned name in case a -dev package is
 * installed on some other box this is run on. */
static const char *CANDIDATE_LIBS[] = {
    "libpcre2-8.so.0",
    "libpcre2-8.so",
    NULL
};

static void *load_symbol(void *handle, const char *name)
{
    dlerror(); /* clear any existing error */
    void *sym = dlsym(handle, name);
    const char *err = dlerror();
    if (err != NULL) {
        fprintf(stderr,
            "pcre2_oracle: PCRE2 library is missing expected symbol '%s': %s\n"
            "  This oracle hand-declares the PCRE2 8-bit ABI against PCRE2\n"
            "  10.46 (libpcre2-8-0 on this box); a different PCRE2 version\n"
            "  or build may not export this symbol. See the header comment\n"
            "  in tests/fuzz/pcre2_oracle.c.\n", name, err);
        exit(3);
    }
    return sym;
}

static void load_pcre2(void)
{
    void *handle = NULL;
    for (int i = 0; CANDIDATE_LIBS[i] != NULL; i++) {
        handle = dlopen(CANDIDATE_LIBS[i], RTLD_NOW | RTLD_LOCAL);
        if (handle) break;
    }
    if (!handle) {
        fprintf(stderr,
            "pcre2_oracle: could not load the PCRE2 8-bit runtime library.\n"
            "  Tried: libpcre2-8.so.0, libpcre2-8.so\n"
            "  dlopen error: %s\n"
            "  Install the PCRE2 8-bit runtime (Debian/Ubuntu package\n"
            "  'libpcre2-8-0') to use this oracle.\n", dlerror());
        exit(3);
    }

    p_compile             = (fn_compile)load_symbol(handle, "pcre2_compile_8");
    p_match_data_create   = (fn_match_data_create)load_symbol(handle, "pcre2_match_data_create_8");
    p_match               = (fn_match)load_symbol(handle, "pcre2_match_8");
    p_get_ovector_pointer = (fn_get_ovector_pointer)load_symbol(handle, "pcre2_get_ovector_pointer_8");
    p_match_data_free     = (fn_match_data_free)load_symbol(handle, "pcre2_match_data_free_8");
    p_code_free            = (fn_code_free)load_symbol(handle, "pcre2_code_free_8");
    p_get_error_message   = (fn_get_error_message)load_symbol(handle, "pcre2_get_error_message_8");
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

int main(int argc, char **argv)
{
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
    pcre2_code_8 *re = p_compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                  &errorcode, &erroffset, NULL);
    if (!re) {
        unsigned char buf[256];
        p_get_error_message(errorcode, buf, sizeof buf);
        fprintf(stderr, "pcre2_oracle: compile error at offset %zu: %s\n",
                (size_t)erroffset, buf);
        printf("cerr %d\n", errorcode);
        free(subj);
        return 0;
    }

    pcre2_match_data_8 *md = p_match_data_create(16, NULL);
    int rc = p_match(re, (PCRE2_SPTR)subj, subjlen, startpos, 0, md, NULL);
    if (rc == -1) {
        /* PCRE2_ERROR_NOMATCH: a genuine verdict. */
        printf("nomatch\n");
    } else if (rc < 0) {
        /* Some other negative code (match/heap/depth limit, ...): PCRE2's
         * own safeguard tripped, not a match/no-match verdict. See the
         * header comment's "mlimit" documentation. */
        unsigned char buf[256];
        p_get_error_message(rc, buf, sizeof buf);
        fprintf(stderr, "pcre2_oracle: match-time limit hit (rc=%d): %s\n", rc, buf);
        printf("mlimit %d\n", rc);
    } else {
        PCRE2_SIZE *ov = p_get_ovector_pointer(md);
        printf("match %zu %zu\n", (size_t)ov[0], (size_t)ov[1]);
    }

    p_match_data_free(md);
    p_code_free(re);
    free(subj);
    return 0;
}
