/* pcre2_throughput.c -- libpcre2 reference point for the throughput table.
 * No pcre2.h on this box (matches pcre2_ctypes.py's own finding), so this
 * dlopen()s libpcre2-8.so.0 directly and hand-declares the same small,
 * documented, stable function subset pcre2_ctypes.py uses -- nothing
 * guessed, same rationale as that module's own header comment.
 * Usage: pcre2_throughput PATTERNFILE SUBJECTFILE
 * Runs a find-all loop 5x (CLOCK_MONOTONIC), same shape as throughput_driver.c.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <dlfcn.h>

typedef void *pcre2_code_p;
typedef void *pcre2_match_data_p;

static void *(*p_compile)(const char *, size_t, uint32_t, int *, size_t *, void *);
static void *(*p_match_data_create_from_pattern)(void *, void *);
static int (*p_match)(void *, const char *, size_t, size_t, uint32_t, void *, void *);
static size_t *(*p_get_ovector_pointer)(void *);
static void (*p_match_data_free)(void *);
static void (*p_code_free)(void *);
static int (*p_get_error_message)(int, char *, size_t);

#define PCRE2_ERROR_NOMATCH (-1)

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

static int cmp_double(const void *a, const void *b) {
    double da = *(const double *)a, db = *(const double *)b;
    return (da > db) - (da < db);
}

static unsigned char *slurp(const char *path, long *sz_out) {
    FILE *f = fopen(path, "rb");
    if (!f) { perror("fopen"); exit(2); }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *buf = malloc(sz > 0 ? (size_t)sz : 1);
    if (sz > 0 && fread(buf, 1, (size_t)sz, f) != (size_t)sz) { fprintf(stderr, "short read\n"); exit(2); }
    fclose(f);
    *sz_out = sz;
    return buf;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: %s patternfile subjectfile\n", argv[0]);
        return 2;
    }

    void *lib = dlopen("libpcre2-8.so.0", RTLD_NOW);
    if (!lib) { fprintf(stderr, "dlopen: %s\n", dlerror()); return 2; }

    p_compile = dlsym(lib, "pcre2_compile_8");
    p_match_data_create_from_pattern = dlsym(lib, "pcre2_match_data_create_from_pattern_8");
    p_match = dlsym(lib, "pcre2_match_8");
    p_get_ovector_pointer = dlsym(lib, "pcre2_get_ovector_pointer_8");
    p_match_data_free = dlsym(lib, "pcre2_match_data_free_8");
    p_code_free = dlsym(lib, "pcre2_code_free_8");
    p_get_error_message = dlsym(lib, "pcre2_get_error_message_8");
    if (!p_compile || !p_match_data_create_from_pattern || !p_match ||
        !p_get_ovector_pointer || !p_match_data_free || !p_code_free) {
        fprintf(stderr, "dlsym failed\n");
        return 2;
    }

    long patlen;
    unsigned char *pat = slurp(argv[1], &patlen);

    int errcode = 0;
    size_t erroff = 0;
    void *code = p_compile((const char *)pat, (size_t)patlen, 0, &errcode, &erroff, NULL);
    if (!code) {
        char msg[256];
        p_get_error_message(errcode, msg, sizeof msg);
        fprintf(stderr, "pcre2_compile failed at %zu: %s\n", erroff, msg);
        return 2;
    }

    long sz;
    unsigned char *buf = slurp(argv[2], &sz);

    double reps[5];
    long matchcount = -1;

    for (int rep = 0; rep < 5; rep++) {
        void *md = p_match_data_create_from_pattern(code, NULL);
        size_t pos = 0;
        long mc = 0;
        double t0 = now();
        while (pos <= (size_t)sz) {
            int rc = p_match(code, (const char *)buf, (size_t)sz, pos, 0, md, NULL);
            if (rc == PCRE2_ERROR_NOMATCH) break;
            if (rc < 0) break;
            size_t *ov = p_get_ovector_pointer(md);
            size_t mstart = ov[0], mend = ov[1];
            mc++;
            pos = (mend > pos) ? mend : pos + 1;
        }
        double t1 = now();
        reps[rep] = t1 - t0;
        if (rep == 0) matchcount = mc;
        p_match_data_free(md);
    }

    double sorted[5];
    memcpy(sorted, reps, sizeof(reps));
    qsort(sorted, 5, sizeof(double), cmp_double);
    double median = sorted[2];

    printf("subject=%s bytes=%ld matches=%ld reps=[%.6f %.6f %.6f %.6f %.6f] median=%.6f\n",
           argv[2], sz, matchcount, reps[0], reps[1], reps[2], reps[3], reps[4], median);

    p_code_free(code);
    return 0;
}
