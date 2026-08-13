/*
 * eng_pcre2.c — dlopen-based PCRE2 8-bit timing driver (interp + JIT), used
 * by tests/bench/compare/compare.sh's cross-engine performance comparison.
 *
 * WHY dlopen + hand-declared ABI: identical situation to, and directly
 * reusing the technique established by, tests/fuzz/pcre2_oracle.c — this
 * box has libpcre2-8-0 (the runtime .so.0) but no -dev package, so there is
 * no pcre2.h and no unversioned libpcre2-8.so to link against. See that
 * file's header comment for the full rationale; this file hand-declares
 * the same opaque-struct-pointer + extern-prototype slice of the ABI, plus
 * the JIT entry points (pcre2_jit_compile_8, pcre2_jit_match_8) and
 * pcre2_config_8 (for version/JIT-availability reporting) that the oracle
 * doesn't need.
 *
 * PCRE2_CONFIG_* and PCRE2_JIT_* values below are NOT guessed from a
 * pcre2.h.generic memory of the enum: PCRE2_CONFIG_JIT=1 and
 * PCRE2_CONFIG_VERSION=11 were confirmed empirically against the actual
 * libpcre2-8.so.0 on this box (PCRE2 10.46 2025-08-27) with a throwaway
 * ctypes probe that called pcre2_config_8 for codes 0..19 and inspected
 * which ones returned recognizable JIT-flag/version-string output.
 * PCRE2_JIT_COMPLETE=1 is the well-known stable value used by every PCRE2
 * JIT caller (matches upstream pcre2jit.c). These are long-stable public
 * ABI constants, unlike the opaque struct layouts, so hand-declaring them
 * carries the same low risk pcre2_oracle.c already accepted for the
 * function-pointer slice.
 *
 * Modes (argv[1]):
 *   probe                                         -- see below
 *   interp <pattern> <subject-file> <iters>       -- pcre2_match_8 loop
 *   jit    <pattern> <subject-file> <iters>       -- pcre2_jit_compile_8 +
 *                                                     pcre2_jit_match_8 loop
 *
 * `probe` (argv: just "probe", no further args) compiles a trivial pattern
 * ("x"), soft-resolves pcre2_jit_compile_8 (missing symbol is NOT a hard
 * error here, unlike every other symbol -- JIT can be compiled out of a
 * PCRE2 build), attempts an actual JIT compile of that trivial pattern,
 * and prints exactly one line:
 *   jit_available=<0|1> version=<PCRE2 version string, space-escaped as _>
 * exit 0 always (probe failures are reported IN the line, not via exit
 * code, so compare.sh's one-shot startup check never has to distinguish
 * "JIT unavailable" from "driver crashed").
 *
 * `interp`/`jit` modes: same warmup-then-timed-loop shape and same
 * `status=` output line as eng_pcrec.c/eng_py.py (see eng_pcrec.c's header
 * for the full field list and rationale; this file matches it exactly so
 * compare.sh has one parser for all three engines' timing output). Two
 * additional statuses beyond `ok`, both defensive (none of the fixed case
 * matrix is expected to hit them) and both zero out the numeric fields:
 *   status=cerr code=<N>            PCRE2 rejected the pattern at compile
 *                                    time (see pcre2_oracle.c's "cerr")
 *   status=jit_unavailable          jit mode only: pcre2_jit_compile_8 is
 *                                    either not exported by this PCRE2
 *                                    build, or it rejected this specific
 *                                    pattern (some pattern shapes are not
 *                                    JIT-compilable even when the library
 *                                    supports JIT in general)
 * A match-time resource-limit trip (PCRE2's rc < 0 && rc != -1, see
 * pcre2_oracle.c's "mlimit" / docs/dev/upstream_issues.md U4) prints
 * status=mlimit code=<N> -- not a verdict, must not be compared.
 *
 * Exit codes: 0 normal (a status= line was printed), 2 usage/IO error,
 * 3 failed to load/resolve a REQUIRED symbol from the PCRE2 library.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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
typedef int (*fn_config)(uint32_t what, void *where); /* real ABI: (uint32_t, void*) -- no size param */
typedef int (*fn_jit_compile)(pcre2_code_8 *code, uint32_t options);

static fn_compile             p_compile;
static fn_match_data_create   p_match_data_create;
static fn_match               p_match;
static fn_get_ovector_pointer p_get_ovector_pointer;
static fn_match_data_free     p_match_data_free;
static fn_code_free           p_code_free;
static fn_get_error_message   p_get_error_message;
static fn_config              p_config;
static fn_jit_compile         p_jit_compile;   /* soft: may be NULL */
static fn_match               p_jit_match;     /* soft: may be NULL (same signature as pcre2_match_8) */

/* Empirically confirmed against this box's libpcre2-8.so.0 (10.46), see
 * header comment; not guessed from memory. */
#define PCREC_PCRE2_CONFIG_JIT      1u
#define PCREC_PCRE2_CONFIG_VERSION 11u
#define PCREC_PCRE2_JIT_COMPLETE   1u

static const char *CANDIDATE_LIBS[] = {
    "libpcre2-8.so.0",
    "libpcre2-8.so",
    NULL
};

static void *g_handle;

static void *load_symbol_hard(const char *name)
{
    dlerror();
    void *sym = dlsym(g_handle, name);
    const char *err = dlerror();
    if (err != NULL) {
        fprintf(stderr,
            "eng_pcre2: PCRE2 library is missing required symbol '%s': %s\n",
            name, err);
        exit(3);
    }
    return sym;
}

/* Soft resolve: returns NULL (no exit) if the symbol isn't exported --
 * used only for the JIT entry points, which are legitimately absent from
 * a PCRE2 build compiled without --enable-jit. */
static void *load_symbol_soft(const char *name)
{
    dlerror();
    void *sym = dlsym(g_handle, name);
    dlerror();
    return sym;
}

static void load_pcre2(void)
{
    for (int i = 0; CANDIDATE_LIBS[i] != NULL; i++) {
        g_handle = dlopen(CANDIDATE_LIBS[i], RTLD_NOW | RTLD_LOCAL);
        if (g_handle) break;
    }
    if (!g_handle) {
        fprintf(stderr,
            "eng_pcre2: could not load the PCRE2 8-bit runtime library.\n"
            "  Tried: libpcre2-8.so.0, libpcre2-8.so\n"
            "  dlopen error: %s\n", dlerror());
        exit(3);
    }

    p_compile             = (fn_compile)load_symbol_hard("pcre2_compile_8");
    p_match_data_create   = (fn_match_data_create)load_symbol_hard("pcre2_match_data_create_8");
    p_match               = (fn_match)load_symbol_hard("pcre2_match_8");
    p_get_ovector_pointer = (fn_get_ovector_pointer)load_symbol_hard("pcre2_get_ovector_pointer_8");
    p_match_data_free     = (fn_match_data_free)load_symbol_hard("pcre2_match_data_free_8");
    p_code_free           = (fn_code_free)load_symbol_hard("pcre2_code_free_8");
    p_get_error_message   = (fn_get_error_message)load_symbol_hard("pcre2_get_error_message_8");
    p_config              = (fn_config)load_symbol_hard("pcre2_config_8");

    p_jit_compile = (fn_jit_compile)load_symbol_soft("pcre2_jit_compile_8");
    p_jit_match   = (fn_match)load_symbol_soft("pcre2_jit_match_8");
}

static unsigned char *read_file(const char *path, size_t *out_len)
{
    FILE *f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "eng_pcre2: cannot open '%s': %s\n", path, strerror(errno)); exit(2); }
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); fprintf(stderr, "eng_pcre2: fseek failed on '%s'\n", path); exit(2); }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); fprintf(stderr, "eng_pcre2: ftell failed on '%s'\n", path); exit(2); }
    rewind(f);
    unsigned char *buf = malloc(sz > 0 ? (size_t)sz : 1);
    if (!buf) { fclose(f); fprintf(stderr, "eng_pcre2: out of memory\n"); exit(2); }
    size_t got = sz > 0 ? fread(buf, 1, (size_t)sz, f) : 0;
    if (got != (size_t)sz) { fclose(f); fprintf(stderr, "eng_pcre2: short read on '%s'\n", path); exit(2); }
    fclose(f);
    *out_len = (size_t)sz;
    return buf;
}

/* Replace spaces with '_' in-place so the caller can print this inside a
 * space-separated key=value line without quoting. */
static void squash_spaces(char *s)
{
    for (; *s; s++) if (*s == ' ') *s = '_';
}

static int run_probe(void)
{
    load_pcre2();

    unsigned char verbuf[64];
    memset(verbuf, 0, sizeof verbuf);
    int vrc = p_config(PCREC_PCRE2_CONFIG_VERSION, verbuf);
    if (vrc < 0) {
        snprintf((char *)verbuf, sizeof verbuf, "unknown(config_rc=%d)", vrc);
    }
    squash_spaces((char *)verbuf);

    int jit_available = 0;
    if (p_jit_compile != NULL) {
        int errorcode;
        PCRE2_SIZE erroffset;
        pcre2_code_8 *re = p_compile((PCRE2_SPTR)"x", 1, 0, &errorcode,
                                      &erroffset, NULL);
        if (re) {
            int jrc = p_jit_compile(re, PCREC_PCRE2_JIT_COMPLETE);
            if (jrc == 0) jit_available = 1;
            p_code_free(re);
        }
    }

    printf("jit_available=%d version=%s\n", jit_available, (char *)verbuf);
    return 0;
}

/* run_timed: shared interp/jit timing body.
 * use_jit: 0 -> pcre2_match_8, 1 -> pcre2_jit_match_8 (caller must have
 * already confirmed p_jit_match/jit-compile succeeded for `re`). */
static int run_timed(pcre2_code_8 *re, unsigned char *subj, size_t n, long iters, int use_jit)
{
    pcre2_match_data_8 *md = p_match_data_create(16, NULL);
    fn_match matcher = use_jit ? p_jit_match : p_match;

    /* untimed warmup -- see eng_pcrec.c header for why */
    int rc = matcher(re, (PCRE2_SPTR)subj, n, 0, 0, md, NULL);

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < iters; i++) {
        rc = matcher(re, (PCRE2_SPTR)subj, n, 0, 0, md, NULL);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);

    double secs = (double)(t1.tv_sec - t0.tv_sec) +
                  (double)(t1.tv_nsec - t0.tv_nsec) / 1e9;

    if (rc == -1) {
        double mb = ((double)n * (double)iters) / (1024.0 * 1024.0);
        double mbps = secs > 0.0 ? mb / secs : 0.0;
        printf("status=ok bytes=%zu iters=%ld secs=%.6f mbps=%.3f match=0 start=0 end=0\n",
               n, iters, secs, mbps);
    } else if (rc < 0) {
        unsigned char buf[256];
        p_get_error_message(rc, buf, sizeof buf);
        fprintf(stderr, "eng_pcre2: match-time limit hit (rc=%d): %s\n", rc, buf);
        printf("status=mlimit code=%d bytes=%zu iters=%ld secs=%.6f mbps=0.000 match=0 start=0 end=0\n",
               rc, n, iters, secs);
    } else {
        PCRE2_SIZE *ov = p_get_ovector_pointer(md);
        double mb = ((double)n * (double)iters) / (1024.0 * 1024.0);
        double mbps = secs > 0.0 ? mb / secs : 0.0;
        printf("status=ok bytes=%zu iters=%ld secs=%.6f mbps=%.3f match=1 start=%zu end=%zu\n",
               n, iters, secs, mbps, (size_t)ov[0], (size_t)ov[1]);
    }

    p_match_data_free(md);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr,
            "usage: %s probe\n"
            "       %s interp|jit <pattern> <subject-file> <iters>\n",
            argv[0], argv[0]);
        return 2;
    }

    if (!strcmp(argv[1], "probe")) {
        if (argc != 2) { fprintf(stderr, "usage: %s probe\n", argv[0]); return 2; }
        return run_probe();
    }

    int use_jit;
    if (!strcmp(argv[1], "interp")) use_jit = 0;
    else if (!strcmp(argv[1], "jit")) use_jit = 1;
    else {
        fprintf(stderr, "eng_pcre2: unknown mode '%s' (want probe|interp|jit)\n", argv[1]);
        return 2;
    }

    if (argc != 5) {
        fprintf(stderr, "usage: %s %s <pattern> <subject-file> <iters>\n", argv[0], argv[1]);
        return 2;
    }
    const char *pattern = argv[2];
    const char *subj_path = argv[3];
    char *end = NULL;
    long iters = strtol(argv[4], &end, 10);
    if (end == argv[4] || iters <= 0) {
        fprintf(stderr, "eng_pcre2: iters must be a positive integer, got '%s'\n", argv[4]);
        return 2;
    }

    load_pcre2();

    size_t n = 0;
    unsigned char *subj = read_file(subj_path, &n);

    int errorcode;
    PCRE2_SIZE erroffset;
    pcre2_code_8 *re = p_compile((PCRE2_SPTR)pattern, strlen(pattern), 0,
                                  &errorcode, &erroffset, NULL);
    if (!re) {
        unsigned char buf[256];
        p_get_error_message(errorcode, buf, sizeof buf);
        fprintf(stderr, "eng_pcre2: compile error at offset %zu: %s\n", erroffset, buf);
        printf("status=cerr code=%d bytes=%zu iters=0 secs=0.000000 mbps=0.000 match=0 start=0 end=0\n",
               errorcode, n);
        free(subj);
        return 0;
    }

    if (use_jit) {
        if (p_jit_compile == NULL) {
            printf("status=jit_unavailable bytes=%zu iters=0 secs=0.000000 mbps=0.000 match=0 start=0 end=0\n", n);
            p_code_free(re);
            free(subj);
            return 0;
        }
        int jrc = p_jit_compile(re, PCREC_PCRE2_JIT_COMPLETE);
        if (jrc != 0 || p_jit_match == NULL) {
            printf("status=jit_unavailable bytes=%zu iters=0 secs=0.000000 mbps=0.000 match=0 start=0 end=0\n", n);
            p_code_free(re);
            free(subj);
            return 0;
        }
    }

    int rc2 = run_timed(re, subj, n, iters, use_jit);

    p_code_free(re);
    free(subj);
    return rc2;
}
