/*
 * compile_stack_driver.c — [DD-10]: ONE pcrec_compile() call on a thread whose
 * stack this driver owns, reporting whether it fit and how much it used.
 *
 * [TS-4]'s ts4_driver.c asks the same question of a GENERATED MATCHER; this
 * asks it of the COMPILER, which is a library a caller may run on any thread
 * (D19). docs/spec/limits.md §3.10 states the budget this measures.
 *
 * THE STACK IS PAINTED AND GUARDED. It is mmap'd here, filled with a known
 * byte, and its lowest page is made inaccessible, so an overflow is a SIGSEGV
 * at the guard rather than a silent write into whatever lies below (a stack
 * handed to pthread_attr_setstack gets no guard page of its own). After the
 * join the first byte that is no longer the paint marks the high-water point.
 *
 * Usage: compile_stack_driver STACK_BYTES PATTERN_FILE [FEATURES [ENGINE]]
 *   FEATURES  pcrec_options.features (default "all"; "-" for NULL)
 *   ENGINE    pcrec_options.engine as a number (default 0, auto)
 * The emitted-size caps are raised to their maximum so a wide pattern reaches
 * every pass instead of being refused at the first size check.
 *
 * Prints one line, `rc=<0|-1> hw=<bytes> msg=<diagnostic>`, and exits 0; a
 * stack overflow kills the process before anything is printed, which is what
 * the runner reads.
 */
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "pcrec.h"

#define PAINT 0xA5

struct job {
    const char  *pattern;
    const char  *features;
    int          engine;
    int          rc;
    pcrec_error  err;
};

static void *compile_on_thread(void *p)
{
    struct job *j = p;
    pcrec_options o;
    pcrec_output out;

    pcrec_default_options(&o);
    o.features = j->features;
    o.engine = j->engine;
    o.max_emit_code_bytes = UINT64_MAX / 2;
    o.max_emit_bytes = UINT64_MAX / 2;
    memset(&out, 0, sizeof out);
    j->rc = pcrec_compile(j->pattern, &o, &out, &j->err);
    if (j->rc == 0) pcrec_output_free(&out);
    return NULL;
}

static char *slurp(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long n = ftell(f);
    if (n < 0 || fseek(f, 0, SEEK_SET) != 0) { fclose(f); return NULL; }
    char *s = malloc((size_t)n + 1);
    if (s && fread(s, 1, (size_t)n, f) != (size_t)n) { free(s); s = NULL; }
    if (s) s[n] = '\0';
    fclose(f);
    return s;
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: %s STACK_BYTES PATTERN_FILE [FEATURES [ENGINE]]\n", argv[0]);
        return 2;
    }
    const size_t page = (size_t)sysconf(_SC_PAGESIZE);
    const size_t want = (size_t)strtoull(argv[1], NULL, 10);
    const size_t size = (want + page - 1) / page * page;
    struct job j;
    memset(&j, 0, sizeof j);
    j.pattern = slurp(argv[2]);
    if (!j.pattern) { perror(argv[2]); return 2; }
    j.features = argc > 3 ? argv[3] : "all";
    if (strcmp(j.features, "-") == 0) j.features = NULL;
    j.engine = argc > 4 ? atoi(argv[4]) : 0;

    unsigned char *map = mmap(NULL, size + page, PROT_READ | PROT_WRITE,
                              MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (map == MAP_FAILED) { perror("mmap"); return 2; }
    if (mprotect(map, page, PROT_NONE) != 0) { perror("mprotect"); return 2; }
    unsigned char *stk = map + page;
    memset(stk, PAINT, size);

    pthread_attr_t at;
    pthread_t t;
    if (pthread_attr_init(&at) != 0 || pthread_attr_setstack(&at, stk, size) != 0 ||
        pthread_create(&t, &at, compile_on_thread, &j) != 0) {
        fprintf(stderr, "could not start a %zu-byte thread\n", size);
        return 2;
    }
    pthread_join(t, NULL);

    size_t i = 0;
    while (i < size && stk[i] == PAINT) i++;
    printf("rc=%d hw=%zu msg=%s\n", j.rc, size - i, j.rc ? j.err.msg : "");
    return 0;
}
