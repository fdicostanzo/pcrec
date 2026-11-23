/*
 * growth_driver.c — [GROWTH-SWEEP]: pcrec_compile() on a thread whose stack
 * this driver owns, under an optional memory cap, in two modes.
 *
 *   growth_driver one CAP STACK RAISE FEATURES ENGINE PATFILE [CSRC_OUT]
 *       ONE compile, then exit. With CSRC_OUT the artifact is compiled with a
 *       main() (PCREC_EMIT_MAIN) and its C source written there, for the
 *       runner to build and run (a LIMIT cell's matcher). Prints `rc=<0|-1> hw=<bytes> msg=<diag>` and
 *       exits 0 (the line also carries ` cpu=<seconds>` after hw: the process's own
 *       user+sys CPU, all threads; the runner's per-doubling report reads it); a crash
 *       kills the process before the line, which is what the runner reads.
 *   growth_driver lib CONTROL_OUT SERIES_FILE
 *       LIBRARY MODE: ONE process compiles a whole series of cells, refusals
 *       and memory-capped failures included, to see whether a series in one
 *       process crashes or leaks (build it with ASan+LSan and the process
 *       exit reports a leak). SERIES_FILE has one TAB-separated line per cell:
 *       CAP STACK RAISE FEATURES ENGINE PATFILE [BOUND_S]. BOUND_S is that
 *       cell's own wall-time bound in seconds (0 or absent = none): a
 *       compile still running when it expires is a FAIL (a timeout is a
 *       crash): the SIGALRM handler prints `cell <n> TIMEOUT bound=<s> pat=<file>`
 *       and exits 124, naming the cell, so the series stops cleanly (one
 *       in-process compile cannot be abandoned and the process go on). Before
 *       each compile a `begin <n> bound=<s> pat=<file>` progress line is
 *       printed, so a stuck cell is visible on the pipe. A CONTROL pattern is compiled
 *       before the series and again after it; both outputs are written to
 *       CONTROL_OUT.before / .after for the runner to compare and to run.
 *       Prints one `cell <n> rc=.. hw=.. msg=..` line per cell.
 *
 * CAP is bytes of RLIMIT_DATA (0 = none): private writable mappings and the
 * heap, which a failing malloc turns into a refusal. RLIMIT_DATA and not
 * RLIMIT_AS because AddressSanitizer reserves terabytes of address space
 * and cannot start under an AS cap; the cap is set AFTER the runtime is up,
 * so it is the data size the compile itself may reach. Under ASan even
 * RLIMIT_DATA fails (the runtime's own shadow mappings), so the sanitizer
 * build defines GROWTH_HEAPCAP and the cap is a live-heap budget (below).
 *
 * STACK is the thread's size in bytes, painted and guarded as
 * tests/thread/compile_stack_driver.c does; 0 = run the compile on the main
 * thread (the process's own stack). RAISE=1 lifts the emitted-size caps to
 * their maximum (so a wide pattern reaches every pass), 0 keeps the defaults.
 * FEATURES is pcrec_options.features ("-" = NULL), ENGINE a number.
 */
#define _GNU_SOURCE
#include <pthread.h>
#include <signal.h>
#include <time.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>

#include "pcrec.h"

#define PAINT 0xA5
#define GUARD (64 * 1024)

struct job {
    const char  *pattern;
    const char  *features;
    int          engine, raise, emit_main;
    int          rc;
    pcrec_error  err;
    char        *out;      /* the c_src, kept only when emit_main */
};

static void *compile_job(void *p)
{
    struct job *j = p;
    pcrec_options o;
    pcrec_output out;

    pcrec_default_options(&o);
    o.features = j->features;
    o.engine = j->engine;
    if (j->emit_main) o.flags |= PCREC_EMIT_MAIN;
    if (j->raise) {
        o.max_emit_code_bytes = UINT64_MAX / 2;
        o.max_emit_bytes = UINT64_MAX / 2;
    }
    memset(&out, 0, sizeof out);
    j->rc = pcrec_compile(j->pattern, &o, &out, &j->err);
    if (j->rc == 0) {
        if (j->emit_main) j->out = out.c_src, out.c_src = NULL;
        pcrec_output_free(&out);
    }
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

#ifdef GROWTH_HEAPCAP
/* The cap as a LIVE-HEAP budget (build with -DGROWTH_HEAPCAP and
 * -Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free): malloc, calloc
 * and realloc in the objects linked here (pcrec's and this driver's) return
 * NULL when the live bytes would pass the cap, which is what an exhausted
 * address space does to them. For the ASan build, whose runtime cannot start
 * its shadow mappings under RLIMIT_DATA (the runner's library-mode ASan stage);
 * the counts are approximate (strdup and friends are libc-internal calls the
 * wrap does not see), so the cap is a ladder rung, not a measurement. */
#include <malloc.h>
static size_t heap_cap;
static long   heap_live;
void *__real_malloc(size_t), *__real_calloc(size_t, size_t), *__real_realloc(void *, size_t);
void  __real_free(void *);
static int over(size_t add)
{
    long live = __atomic_load_n(&heap_live, __ATOMIC_RELAXED);
    if (live < 0) live = 0;     /* an unwrapped alloc (strdup) freed through the wrap can drive it negative */
    return heap_cap && (size_t)live + add > heap_cap;
}
void *__wrap_malloc(size_t n)
{
    if (over(n)) return NULL;
    void *p = __real_malloc(n);
    if (p) __atomic_add_fetch(&heap_live, (long)malloc_usable_size(p), __ATOMIC_RELAXED);
    return p;
}
void *__wrap_calloc(size_t a, size_t b)
{
    if (b && a > (size_t)-1 / b) return NULL;
    if (over(a * b)) return NULL;
    void *p = __real_calloc(a, b);
    if (p) __atomic_add_fetch(&heap_live, (long)malloc_usable_size(p), __ATOMIC_RELAXED);
    return p;
}
void *__wrap_realloc(void *q, size_t n)
{
    long old = q ? (long)malloc_usable_size(q) : 0;
    if (over(n > (size_t)old ? n - (size_t)old : 0)) return NULL;
    void *p = __real_realloc(q, n);
    if (p) __atomic_add_fetch(&heap_live, (long)malloc_usable_size(p) - old, __ATOMIC_RELAXED);
    return p;
}
void __wrap_free(void *q)
{
    if (q) __atomic_sub_fetch(&heap_live, (long)malloc_usable_size(q), __ATOMIC_RELAXED);
    __real_free(q);
}
static int set_cap(size_t bytes) { heap_cap = bytes; return 0; }
#else
/* 0 on success; nonzero when the cap cannot be set (above the hard limit): the
 * run would be UNCAPPED and its cap column would read green. */
static int set_cap(size_t bytes)
{
    struct rlimit r;
    if (getrlimit(RLIMIT_DATA, &r) != 0) return -1;
    r.rlim_cur = bytes ? bytes : r.rlim_max;
    return setrlimit(RLIMIT_DATA, &r);
}
#endif

/* Compile j on a STACK-byte painted thread (0: this thread); the high-water
 * mark of the stack goes to *hw. Returns 0, or -1 when the thread could not
 * be started (the cap may be below what a thread needs). */
static int run_job(struct job *j, size_t want, size_t *hw)
{
    *hw = 0;
    if (want == 0) { compile_job(j); return 0; }
    const size_t page = (size_t)sysconf(_SC_PAGESIZE);
    const size_t size = (want + page - 1) / page * page;
    const size_t guard = (GUARD + page - 1) / page * page;
    unsigned char *map = mmap(NULL, size + guard, PROT_READ | PROT_WRITE,
                              MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (map == MAP_FAILED) return -1;
    if (mprotect(map, guard, PROT_NONE) != 0) { munmap(map, size + guard); return -1; }
    unsigned char *stk = map + guard;
    memset(stk, PAINT, size);
    pthread_attr_t at;
    pthread_t t;
    if (pthread_attr_init(&at) != 0 || pthread_attr_setstack(&at, stk, size) != 0 ||
        pthread_create(&t, &at, compile_job, j) != 0) {
        munmap(map, size + guard);
        return -1;
    }
    pthread_join(t, NULL);
    size_t i = 0;
    while (i < size && stk[i] == PAINT) i++;
    *hw = size - i;
    munmap(map, size + guard);
    return 0;
}

static void job_report(const char *lead, struct job *j, size_t hw, int started, double wall)
{
    char w[48] = "";   /* `one` mode (wall < 0) carries the process's CPU seconds (user+sys, all threads) */
    if (wall >= 0) snprintf(w, sizeof w, " wall=%.2f", wall);
    else {
        struct rusage ru;
        if (getrusage(RUSAGE_SELF, &ru) == 0)
            snprintf(w, sizeof w, " cpu=%.3f", (double)(ru.ru_utime.tv_sec + ru.ru_stime.tv_sec) +
                     (double)(ru.ru_utime.tv_usec + ru.ru_stime.tv_usec) / 1e6);
    }
    if (!started) printf("%src=-9 hw=0%s msg=could not start the thread (the cap is below what a thread needs)\n", lead, w);
    else printf("%src=%d hw=%zu%s msg=%s\n", lead, j->rc, hw, w, j->rc ? j->err.msg : "");
    fflush(stdout);
}

static double now_s(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

/* The per-cell bound: the current cell's line is prebuilt (async-signal-safe:
 * write() only) when the alarm is armed. */
static char timeout_line[8400];
static size_t timeout_len;
static void on_alarm(int sig)
{
    (void)sig;
    ssize_t w = write(1, timeout_line, timeout_len);
    (void)w;
    _exit(124);
}
static void arm_bound(int n, unsigned bound, const char *pat)
{
    if (!bound) return;
    int k = snprintf(timeout_line, sizeof timeout_line, "cell %d TIMEOUT bound=%u pat=%s\n", n, bound, pat);
    timeout_len = k < 0 ? 0 : (size_t)k < sizeof timeout_line ? (size_t)k : sizeof timeout_line - 1;
    signal(SIGALRM, on_alarm);
    alarm(bound);
}

static int write_file(const char *path, const char *s)
{
    FILE *f = fopen(path, "wb");
    if (!f) return -1;
    if (s) fputs(s, f);
    return fclose(f);
}

/* The control: compiled with a main(), uncapped, on the main thread. */
static int control(const char *path)
{
    struct job j;
    size_t hw;
    memset(&j, 0, sizeof j);
    j.pattern = "^(?:ab|cd)+e(f)?$";
    j.features = "all";
    j.emit_main = 1;
    run_job(&j, 0, &hw);
    if (j.rc != 0) { fprintf(stderr, "control: compile refused: %s\n", j.err.msg); return -1; }
    int rc = write_file(path, j.out);
    free(j.out);
    return rc;
}

int main(int argc, char **argv)
{
    if ((argc == 8 || argc == 9) && strcmp(argv[1], "one") == 0) {
        struct job j;
        size_t hw;
        memset(&j, 0, sizeof j);
        j.pattern = slurp(argv[7]);
        if (!j.pattern) { perror(argv[7]); return 2; }
        j.raise = atoi(argv[4]);
        j.features = argv[5];
        if (strcmp(j.features, "-") == 0) j.features = NULL;
        j.engine = atoi(argv[6]);
        if (set_cap((size_t)strtoull(argv[2], NULL, 10)) != 0) {
            fprintf(stderr, "growth_driver: cannot set the memory cap %s (above the hard limit?)\n", argv[2]);
            return 2;
        }
        if (argc >= 9) j.emit_main = 1;
        int started = run_job(&j, (size_t)strtoull(argv[3], NULL, 10), &hw) == 0;
        if (argc >= 9 && started && j.rc == 0 && write_file(argv[8], j.out) != 0) {
            perror(argv[8]);
            return 2;
        }
        job_report("", &j, hw, started, -1.0);
        return 0;
    }
    if (argc == 4 && strcmp(argv[1], "lib") == 0) {
        char path[4096];
        snprintf(path, sizeof path, "%s.before", argv[2]);
        if (control(path) != 0) return 2;
        FILE *f = fopen(argv[3], "r");
        if (!f) { perror(argv[3]); return 2; }
        char line[8192];
        int n = 0;
        while (fgets(line, sizeof line, f)) {
            char *fld[7];
            char *s = line, *nl = strchr(line, '\n');
            if (nl) *nl = '\0';
            int k = 0;
            for (; k < 7; k++) {
                fld[k] = s;
                char *t = strchr(s, '\t');
                if (!t) { k++; break; }
                *t = '\0';
                s = t + 1;
            }
            if (k < 6) continue;
            unsigned bound = k >= 7 ? (unsigned)strtoul(fld[6], NULL, 10) : 0;
            struct job j;
            size_t hw;
            memset(&j, 0, sizeof j);
            j.pattern = slurp(fld[5]);
            if (!j.pattern) { perror(fld[5]); return 2; }
            j.raise = atoi(fld[2]);
            j.features = fld[3];
            if (strcmp(j.features, "-") == 0) j.features = NULL;
            j.engine = atoi(fld[4]);
            printf("begin %d bound=%u pat=%s\n", n, bound, fld[5]);
            fflush(stdout);
            if (set_cap((size_t)strtoull(fld[0], NULL, 10)) != 0) {
                fprintf(stderr, "growth_driver: cannot set the memory cap %s (above the hard limit?)\n", fld[0]);
                return 2;
            }
            double t0 = now_s();
            arm_bound(n, bound, fld[5]);
            int started = run_job(&j, (size_t)strtoull(fld[1], NULL, 10), &hw) == 0;
            alarm(0);
            double wall = now_s() - t0;
            set_cap(0);
            char lead[64];
            snprintf(lead, sizeof lead, "cell %d ", n++);
            job_report(lead, &j, hw, started, wall);
            free((void *)j.pattern);
        }
        fclose(f);
        snprintf(path, sizeof path, "%s.after", argv[2]);
        if (control(path) != 0) return 2;
        printf("series done: %d cells\n", n);
        return 0;
    }
    fprintf(stderr, "usage: %s one CAP STACK RAISE FEATURES ENGINE PATFILE [CSRC_OUT] | lib CONTROL_OUT SERIES_FILE\n", argv[0]);
    return 2;
}
