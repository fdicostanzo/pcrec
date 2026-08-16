#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Cold-mmap substring search: CPU prefetch vs. OS readahead.
 *
 * Every other benchmark in this directory measures a haystack that is already
 * in RAM, where the only question is how fast the core can chew through bytes
 * it can reach in a few hundred cycles.  This one asks a different question:
 * when the bytes are on disk and the page cache is empty, what actually
 * governs throughput?
 *
 * The hypothesis worth falsifying is that software prefetch helps here.  It
 * cannot.  `prefetcht0` is a *cache* hint: the CPU is allowed to drop it for
 * any reason at all, and it is architecturally required to drop it when
 * servicing it would need a page fault.  A prefetch to an address whose page
 * is not resident does nothing — no fault, no I/O, no readahead.  So
 * find_enzyme_pf1024 should tie find_enzyme_rare2 exactly on a cold mapping:
 * both pay a major fault every 4 KiB, and the fault dwarfs everything the
 * vector loop does in between.
 *
 * What *can* help is telling the kernel, which is the only party in the system
 * that can issue I/O ahead of the scan:
 *
 *   MADV_SEQUENTIAL  - raise the readahead window for this mapping; the kernel
 *                      keeps fetching ahead of the fault stream, so faults land
 *                      on pages whose I/O is already in flight or finished.
 *   MADV_WILLNEED    - kick off asynchronous readahead over the whole range
 *                      immediately; the scan races the I/O it started.
 *   MAP_POPULATE     - fault the whole mapping in synchronously at mmap() time.
 *                      The cost does not disappear, it just moves out of the
 *                      scan and into the mmap call, which is why the timed
 *                      region for that strategy has to include mmap().
 *
 * "warm" is the reference ceiling: same scan, same code, pages already
 * resident.  The gap between "warm" and every cold row is the I/O, and the gap
 * between the cold rows is all the OS hints are worth.
 *
 * Linux-only (posix_fadvise/POSIX_FADV_DONTNEED, mincore, MAP_POPULATE).  No
 * privileges required: dropping the page cache for a single file you can read
 * needs no root, unlike /proc/sys/vm/drop_caches.
 * ------------------------------------------------------------------------- */

/* Matchers under test, from cand_rare.c and cand_prefetch.c. */
extern const char *find_enzyme_rare2(const char *hay, size_t n);
extern const char *find_enzyme_pf1024(const char *hay, size_t n);

#define PAGE          4096u
#define GEN_CHUNK     (1u << 20)   /* file is written in 1 MiB pieces */
#define ROUNDS        3
#define DEFAULT_PATH  "coldmap.dat"
#define DEFAULT_MB    1024u
#define GEN_SEED      0x243F6A8885A308D3ull

static void die(const char *what)
{
    fprintf(stderr, "coldmap: %s: %s\n", what, strerror(errno));
    exit(1);
}

/* ------------------------------------------------------------------ */
/* PRNG: splitmix64                                                    */
/* ------------------------------------------------------------------ */

static uint64_t rng_state;

static void rng_seed(uint64_t s)
{
    rng_state = s;
}

static uint64_t rnd(void)
{
    uint64_t z = (rng_state += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

static double now_sec(void)
{
    struct timespec ts;

    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0)
        die("clock_gettime");
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* ------------------------------------------------------------------ */
/* corpus generation                                                   */
/* ------------------------------------------------------------------ */

/* English-frequency-weighted lowercase letters, minus 'z'.
 *
 * The harness scrubs accidental matches out of its generated haystacks with a
 * post-pass.  At a gigabyte that pass is pure overhead, so this file takes the
 * cheap shortcut instead: drop 'z' from the alphabet entirely.  "enzyme"
 * contains a 'z', so text drawn from a z-less table provably cannot contain it
 * anywhere, and the only match in the file is the one planted at the end.  The
 * distortion is negligible for our purposes ('z' is 1 per mille of English)
 * and it does not affect what the benchmark measures: with a single match at
 * the very end, every strategy scans all `size` bytes regardless.
 *
 * Weights are per mille, same table the harness uses; sum is 1002 with 'z'
 * removed. */
static const struct { char c; unsigned short w; } EN25[25] = {
    {'e',127},{'t',91},{'a',82},{'o',75},{'i',70},{'n',67},{'s',63},
    {'h',61},{'r',60},{'d',43},{'l',40},{'c',28},{'u',28},{'m',24},
    {'w',24},{'f',22},{'g',20},{'y',20},{'p',19},{'b',15},{'v',10},
    {'k',8},{'j',2},{'x',2},{'q',1},
};
#define EN25_SUM 1002u

static void gen_file(const char *path, size_t size)
{
    FILE *f;
    char *buf;
    size_t left = size;

    fprintf(stderr, "coldmap: generating %s (%zu bytes)...\n", path, size);

    buf = malloc(GEN_CHUNK);
    if (!buf)
        die("malloc");

    f = fopen(path, "wb");
    if (!f)
        die("fopen for write");

    rng_seed(GEN_SEED);
    while (left > 0) {
        size_t n = left < GEN_CHUNK ? left : GEN_CHUNK;

        for (size_t i = 0; i < n; i++) {
            unsigned r = (unsigned)(rnd() % EN25_SUM);
            int t = 0;

            while (r >= EN25[t].w) {
                r -= EN25[t].w;
                t++;
            }
            buf[i] = EN25[t].c;
        }

        /* Final chunk: the only "enzyme" in the file sits at the very end, so
         * every scan is a full-length scan. */
        if (left == n)
            memcpy(buf + n - 6, "enzyme", 6);

        if (fwrite(buf, 1, n, f) != n)
            die("fwrite");
        left -= n;
    }

    if (fflush(f) != 0)
        die("fflush");
    if (fsync(fileno(f)) != 0)
        die("fsync");
    if (fclose(f) != 0)
        die("fclose");
    free(buf);
}

/* Create the corpus unless a file of exactly the right size is already there. */
static void ensure_file(const char *path, size_t size)
{
    struct stat st;

    if (stat(path, &st) == 0 && S_ISREG(st.st_mode) &&
        (uintmax_t)st.st_size == (uintmax_t)size) {
        fprintf(stderr, "coldmap: reusing %s (%zu bytes)\n", path, size);
        return;
    }
    gen_file(path, size);
}

/* ------------------------------------------------------------------ */
/* strategies                                                          */
/* ------------------------------------------------------------------ */

typedef enum {
    S_COLD_PLAIN,
    S_COLD_PF1024,
    S_COLD_SEQ,
    S_COLD_WILLNEED,
    S_COLD_POPULATE,
    S_WARM,
    S_COUNT
} strat_t;

static const char *const STRAT_NAME[S_COUNT] = {
    "cold-plain",
    "cold-pf1024",
    "cold-seq",
    "cold-willneed",
    "cold-populate",
    "warm",
};

/* Fraction of the mapping currently resident, via mincore().  mincore only
 * reports what is already in the page cache; it does not fault anything in, so
 * calling it between eviction and the scan does not disturb the measurement.
 * The vector is one byte per page: 256 KiB for a 1 GiB mapping. */
static double resident_frac(const char *map, size_t size)
{
    size_t pages = (size + PAGE - 1) / PAGE;
    unsigned char *vec = malloc(pages);
    size_t n = 0;

    if (!vec)
        die("malloc mincore vec");
    if (mincore((void *)(uintptr_t)map, size, vec) != 0)
        die("mincore");
    for (size_t i = 0; i < pages; i++)
        n += (size_t)(vec[i] & 1u);
    free(vec);

    return pages ? (double)n / (double)pages : 0.0;
}

/* Fault in every page ahead of a warm run.  Outside the clock by construction:
 * the caller runs this before starting the timer. */
static void touch_all(const char *map, size_t size)
{
    static volatile unsigned long sink;
    unsigned long sum = 0;

    for (size_t off = 0; off < size; off += PAGE)
        sum += (unsigned char)map[off];
    sum += (unsigned char)map[size - 1];
    sink = sum;
    (void)sink;
}

/* One measured run.  Returns seconds; stores the pre-scan resident fraction in
 * *out_res. */
static double run_one(strat_t s, const char *path, size_t size, double *out_res)
{
    int fd;
    int flags = MAP_PRIVATE;
    void *addr;
    const char *map;
    const char *hit;
    double t_map = 0.0, t_scan, res;

    fd = open(path, O_RDONLY);
    if (fd < 0)
        die("open");

    if (s != S_WARM) {
        /* Drop this file's clean page-cache pages.  Best-effort by design:
         * the kernel will not drop pages that are still dirty or that another
         * mapping holds, and it never reports which case it hit.  A failure
         * here is not fatal — the residency check below is what actually
         * decides whether the run was cold. */
        int rc = posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);

        if (rc != 0)
            fprintf(stderr, "  ! posix_fadvise(DONTNEED) failed: %s "
                            "(continuing; check resident%%)\n", strerror(rc));
    }

    /* MAP_POPULATE does the I/O inside mmap(), so for that strategy the mmap
     * call is part of the work being measured and has to be inside the clock.
     * Every other strategy does its I/O through faults taken during the scan,
     * where mmap() itself is a cheap VMA setup that would only add noise.  The
     * two intervals are timed separately and summed so that the residency
     * check, which must sit between mmap() and the scan, stays outside both. */
    if (s == S_COLD_POPULATE) {
        flags |= MAP_POPULATE;
        t_map = now_sec();
    }

    addr = mmap(NULL, size, PROT_READ, flags, fd, 0);
    if (addr == MAP_FAILED)
        die("mmap");
    map = (const char *)addr;

    if (s == S_COLD_POPULATE)
        t_map = now_sec() - t_map;

    if (s == S_WARM)
        touch_all(map, size);

    res = resident_frac(map, size);

    /* Hints go after the residency check on purpose: for cold-willneed the
     * readahead it starts is part of the strategy under test, so the check
     * ahead of it is measuring the state the strategy inherits (cold), not the
     * state it creates. */
    if (s == S_COLD_SEQ || s == S_COLD_WILLNEED) {
        int adv = (s == S_COLD_SEQ) ? MADV_SEQUENTIAL : MADV_WILLNEED;

        if (madvise((void *)(uintptr_t)map, size, adv) != 0)
            fprintf(stderr, "  ! madvise(%s) failed: %s (continuing)\n",
                    s == S_COLD_SEQ ? "SEQUENTIAL" : "WILLNEED",
                    strerror(errno));
    }

    t_scan = now_sec();
    hit = (s == S_COLD_PF1024) ? find_enzyme_pf1024(map, size)
                               : find_enzyme_rare2(map, size);
    t_scan = now_sec() - t_scan;

    if (hit != map + size - 6) {
        fprintf(stderr, "coldmap: %s returned the wrong pointer "
                        "(got %p, want %p) — corpus is not what we think it "
                        "is, or the matcher is broken\n",
                STRAT_NAME[s], (const void *)hit,
                (const void *)(map + size - 6));
        exit(1);
    }

    if (munmap(addr, size) != 0)
        die("munmap");
    if (close(fd) != 0)
        die("close");

    *out_res = res;
    return t_map + t_scan;
}

_Static_assert(ROUNDS == 3, "median3 takes exactly one sample per round");

static double median3(double a, double b, double c)
{
    if (a > b) { double t = a; a = b; b = t; }
    if (b > c) { double t = b; b = c; c = t; }
    if (a > b) { double t = a; a = b; b = t; }
    return b;
}

int main(int argc, char **argv)
{
    const char *path = (argc > 1) ? argv[1] : DEFAULT_PATH;
    unsigned long mb = DEFAULT_MB;
    size_t size;
    double secs[S_COUNT][ROUNDS];
    double resid[S_COUNT][ROUNDS];

    if (argc > 2) {
        char *end;

        errno = 0;
        mb = strtoul(argv[2], &end, 10);
        if (errno != 0 || *end != '\0' || mb == 0) {
            fprintf(stderr, "usage: %s [path] [size_mb]\n", argv[0]);
            return 2;
        }
    }
    if (argc > 3) {
        fprintf(stderr, "usage: %s [path] [size_mb]\n", argv[0]);
        return 2;
    }
    size = (size_t)mb << 20;

    ensure_file(path, size);

    printf("coldmap: %s, %zu MiB, %d rounds, needle planted at end\n\n",
           path, (size_t)mb, ROUNDS);

    for (int r = 0; r < ROUNDS; r++) {
        printf("round %d\n", r + 1);
        /* Strategies are interleaved rather than repeated back to back so that
         * thermal drift, background I/O, or a slowly filling page cache hit
         * every strategy about equally instead of penalizing whichever one
         * happened to run last. */
        for (int s = 0; s < S_COUNT; s++) {
            double res, sec, mbps;

            sec = run_one((strat_t)s, path, size, &res);
            mbps = (double)size / 1e6 / sec;
            secs[s][r] = sec;
            resid[s][r] = res * 100.0;

            printf("  %-14s  resident %6.2f%%  %8.4f s  %9.1f MB/s\n",
                   STRAT_NAME[s], res * 100.0, sec, mbps);

            if (s != S_WARM && res > 0.05)
                printf("      !! WARNING: %.1f%% resident before a COLD run — "
                       "eviction failed, this row is not measuring cold I/O "
                       "(file may still be dirty; try again, or sync(1) first)\n",
                       res * 100.0);
            if (s == S_WARM && res < 0.95)
                printf("      !! WARNING: only %.1f%% resident on the warm run "
                       "— memory pressure is evicting pages under us\n",
                       res * 100.0);
            fflush(stdout);
        }
        printf("\n");
    }

    printf("median of %d\n", ROUNDS);
    printf("  %-14s  %8s  %9s  %9s\n", "strategy", "resid%", "sec", "MB/s");
    for (int s = 0; s < S_COUNT; s++) {
        double sec = median3(secs[s][0], secs[s][1], secs[s][2]);
        double res = median3(resid[s][0], resid[s][1], resid[s][2]);

        printf("  %-14s  %7.2f%%  %9.4f  %9.1f\n",
               STRAT_NAME[s], res, sec, (double)size / 1e6 / sec);
    }

    return 0;
}
