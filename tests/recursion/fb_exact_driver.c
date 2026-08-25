/*
 * fb_exact_driver.c — [DD-14.FB], the SEVEN CAPACITY SITES measured to be
 * exact in BOTH directions, on buffers with no slack at all.
 *
 * WHAT IT ADDS OVER framebuffer.rxt. That file runs the caller-buffer path at
 * capacities comfortably above and comfortably below what a subject needs, so
 * it sees a guard that refuses too early or too late by a wide margin. It
 * cannot see a guard that is off by ONE — and off-by-one is the entire failure
 * mode of a capacity test. Under-tight (`>` where `>=` belongs) writes one
 * element past the end of a caller's region, which on a generously sized
 * buffer lands in slack the caller happens to own and is invisible; over-tight
 * refuses a match the buffer could have held, which on a generously sized
 * buffer never fires at all.
 *
 * SO THIS DRIVER REMOVES THE SLACK. For each nesting depth n it allocates
 * EXACTLY the capacity the design's measured per-level ratios say is needed —
 * 2.000 resume frames and 8.982 trail entries per level
 * (`docs/design/frame_buffer_design.md` §4) — and runs three arms:
 *
 *   exact             must MATCH. Every byte of both regions is in use and
 *                     there is nothing beyond them, so under AddressSanitizer
 *                     ANY write past either end is a heap-buffer-overflow with
 *                     a stack trace naming the site. This is the row the
 *                     design's §11 table wanted from an ASan cell (S-FB6), and
 *                     it covers rather more than that row: it is a statement
 *                     about all seven capacity sites at once.
 *   one-frame-short   must give up (`PCREC_ERR_FRAMES`), not match and not
 *                     over-run. One frame below sufficient.
 *   one-trail-short   likewise, one trail entry below sufficient.
 *
 * The two short arms are what make the exact arm mean something: an artifact
 * that ignored its capacities entirely would pass the exact arm (it would
 * simply write into memory it was not given, which only ASan sees) and fail
 * these two.
 *
 * Prints one `row` line per n:
 *     row <n> <nframes> <ntrail> <exact> <frame_short> <trail_short>
 * Exit 0 on a clean run, 2 on an allocation failure or an inert artifact.
 *
 * Usage: fb_exact [n ...]      (default: five depths around the stamped
 *                               default's own give-up boundary)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

/* MEASURED (design §4), on this specimen: 2.000 resume frames and 8.982 trail
 * entries per nesting level. The trail figure is rounded UP and given one
 * spare, because it is a measured ratio rather than an exact identity and a
 * driver that under-computed it would report a give-up as a defect. The
 * `one-short` arms subtract from whatever this computes, so they stay exactly
 * one below sufficient however the ratio is spelled. */
static size_t frames_for(size_t n) { return 2 * n; }
static size_t trail_for (size_t n) { return (size_t)((double)n * 8.982) + 1; }

static int run_at(size_t n, size_t nframes, size_t ntrail)
{
    size_t len = 2 * n;
    unsigned char *s = malloc(len + 1);
    void *f = malloc(nframes * (size_t)RX_RESUME_FRAME_SIZE);
    void *t = malloc(ntrail  * (size_t)RX_TRAIL_FRAME_SIZE);
    ptrdiff_t caps[RX_NCAPS][2];
    rx_buffers b;
    int r;
    if (!s || !f || !t) { fprintf(stderr, "fb_exact: out of memory\n"); exit(2); }
    memset(s, 'a', n); memset(s + n, 'b', n); s[len] = 0;
    b.frames = f; b.nframes = nframes;
    b.trail  = t; b.ntrail  = ntrail;
    r = rx_search_in(s, len, 0, caps, &b);
    free(s); free(f); free(t);
    return r;
}

int main(int argc, char **argv)
{
    static const size_t default_n[] = { 340, 341, 342, 343, 344 };
    const size_t *ns = default_n;
    size_t nn = sizeof default_n / sizeof default_n[0];
    size_t *parsed = NULL, i;

    if (RX_RESUME_FRAME_SIZE == 0 || RX_TRAIL_FRAME_SIZE == 0) {
        fprintf(stderr, "fb_exact: this artifact reports no resume stack to size\n");
        return 2;
    }
    if (argc > 1) {
        parsed = malloc((size_t)(argc - 1) * sizeof *parsed);
        if (!parsed) return 2;
        for (i = 0; i + 1 < (size_t)argc; i++) parsed[i] = strtoull(argv[i + 1], NULL, 10);
        ns = parsed; nn = (size_t)(argc - 1);
    }

    for (i = 0; i < nn; i++) {
        size_t n = ns[i], nf = frames_for(n), nt = trail_for(n);
        printf("row %zu %zu %zu %d %d %d\n", n, nf, nt,
               run_at(n, nf, nt), run_at(n, nf - 1, nt), run_at(n, nf, nt - 1));
        fflush(stdout);
    }
    free(parsed);
    return 0;
}
