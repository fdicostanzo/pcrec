#define _POSIX_C_SOURCE 200809L
/*
 * fb_mmap_driver.c — [DD-14.FB], docs/spec/match_api.md §10.6's worked
 * example, RUN rather than quoted.
 *
 * THE CLAIM IT EXISTS TO CHECK. D71 item 2 says a caller "may hand over an
 * mmap'd, lazily-committed reservation and get PCRE2-depth recursion with
 * pcrec still never allocating". The spec's §10.6 states that as a table:
 * 128 MB of address space costs ~1.7 MB of resident memory until touched, an
 * 800 KB subject of `^(a(?1)?b)$` shape MATCHES in ~0.056 s having touched
 * ~88 MB, and the SAME artifact returns PCREC_ERR_FRAMES on every one of those
 * subjects through the un-suffixed entry. This program runs exactly that and
 * prints what it measured, so the numbers in the spec are re-derivable rather
 * than inherited.
 *
 * WHY IT IS A C DRIVER AND NOT A .rxt CELL. The `frames-buffer=` directive can
 * express "call `<prefix>_search_in` with N frames and M trail entries", which
 * is enough for the corpus cells in framebuffer.rxt — but not for this, which
 * is about MAP_NORESERVE, resident-set growth and wall time. Those are
 * properties of the reservation, not of the match, and the .rxt format has no
 * business growing a vocabulary for them.
 *
 * WHAT IT PRINTS. One `row` line per subject size:
 *     row <n> <subject_bytes> <result> <seconds> <rss_kb_after> <null_result>
 * where <result> is `<prefix>_search_in`'s return through the reservation and
 * <null_result> is the SAME subject through the un-suffixed entry — the two
 * belong on one line because the contrast is the point. Plus a `reserve` line
 * with the reservation's own facts and the RSS before any match.
 *
 * Exit 0 on a clean run, 2 if the reservation itself could not be made (a
 * machine without MAP_NORESERVE, or without the address space); the runner
 * treats that as SKIPPED-LOUDLY rather than as a pass.
 *
 * Usage: fb_mmap [n ...]      (default: the spec's five rows)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <time.h>

#include "gen.h"

#define RESERVE_BYTES ((size_t)64 << 20)   /* per region, as spec §10.6 */

/* Resident set size in KB, from /proc/self/statm's second field (pages).
 * Returns 0 where /proc is not available — the runner checks for that rather
 * than reporting a confident 0. */
static long rss_kb(void)
{
    FILE *f = fopen("/proc/self/statm", "r");
    long total = 0, res = 0;
    if (!f) return 0;
    if (fscanf(f, "%ld %ld", &total, &res) != 2) { fclose(f); return 0; }
    fclose(f);
    return res * (long)(sysconf(_SC_PAGESIZE) / 1024);
}

static double now_s(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

int main(int argc, char **argv)
{
    static const size_t default_n[] = { 342, 100000, 400000, 466000, 470000 };
    const size_t *ns = default_n;
    size_t nn = sizeof default_n / sizeof default_n[0];
    size_t *parsed = NULL;
    void *f, *t;
    rx_buffers buf;
    size_t i;

    if (RX_RESUME_FRAME_SIZE == 0 || RX_TRAIL_FRAME_SIZE == 0) {
        fprintf(stderr, "fb_mmap: this artifact reports no resume stack to size"
                        " — the worked example needs a VM artifact\n");
        return 2;
    }

    if (argc > 1) {
        parsed = malloc((size_t)(argc - 1) * sizeof *parsed);
        if (!parsed) return 2;
        for (i = 0; i + 1 < (size_t)argc; i++) parsed[i] = strtoull(argv[i + 1], NULL, 10);
        ns = parsed; nn = (size_t)(argc - 1);
    }

    /* THE RESERVATION. MAP_NORESERVE is the whole point: the kernel promises
     * the address space and commits nothing, so the process pays for the pages
     * the match actually touches and not for the ceiling it was given. */
    f = mmap(NULL, RESERVE_BYTES, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
    t = mmap(NULL, RESERVE_BYTES, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
    if (f == MAP_FAILED || t == MAP_FAILED) {
        fprintf(stderr, "fb_mmap: could not reserve 2 x %zu bytes MAP_NORESERVE\n",
                RESERVE_BYTES);
        return 2;
    }

    buf.frames  = f; buf.nframes = RESERVE_BYTES / (size_t)RX_RESUME_FRAME_SIZE;
    buf.trail   = t; buf.ntrail  = RESERVE_BYTES / (size_t)RX_TRAIL_FRAME_SIZE;
    printf("reserve %zu %zu %zu %ld\n",
           RESERVE_BYTES, buf.nframes, buf.ntrail, rss_kb());

    for (i = 0; i < nn; i++) {
        size_t n = ns[i], len = 2 * n;
        unsigned char *s = malloc(len + 1);
        ptrdiff_t caps[RX_NCAPS][2], caps2[RX_NCAPS][2];
        double t0, t1;
        int r, rnull;
        if (!s) { fprintf(stderr, "fb_mmap: out of memory at n=%zu\n", n); return 2; }
        memset(s, 'a', n); memset(s + n, 'b', n); s[len] = 0;

        t0 = now_s();
        r = rx_search_in(s, len, 0, caps, &buf);
        t1 = now_s();
        /* THE CONTROL, on the SAME artifact and the SAME subject: what the
         * un-suffixed entry answers. Without it the table would be a list of
         * matches with nothing to say they were unreachable before. */
        rnull = rx_search(s, len, 0, caps2);

        printf("row %zu %zu %d %.4f %ld %d\n", n, len, r, t1 - t0, rss_kb(), rnull);
        fflush(stdout);
        free(s);
    }

    munmap(f, RESERVE_BYTES); munmap(t, RESERVE_BYTES);
    free(parsed);
    return 0;
}
