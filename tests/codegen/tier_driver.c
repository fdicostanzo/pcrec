/*
 * tier_driver.c — [OPT-1], the TWO-TIER ENTRY's boundary, driven from three
 * sources that can disagree with each other.
 *
 * docs/design/two_tier_entry.md §6. The claim this file exists to test is an
 * IDENTITY claim — "the un-suffixed entry answers exactly what it answered
 * before the tier existed" — and the trap in testing an identity claim is that
 * the cheapest check for it passes on a build where the optimization is not
 * there at all. An artifact whose fast tier is secretly the stamped default
 * answers every subject correctly and escalates never. So answers alone are
 * not enough, and this driver reports THREE things per subject:
 *
 *   ans     what <prefix>_search returns (the tiered entry).
 *   ref     what <prefix>_search_in returns with a DEFAULT-sized descriptor.
 *           This is the SINGLE-TIER execution, reached through an entry
 *           [OPT-1] does not touch — the reference `ans` must equal.
 *   esc     how many times the artifact escalated, counted at the escalation
 *           site itself through the -D<PREFIX>_TEST_TIER_HOOK extern.
 *   pred    whether escalation was EXPECTED, computed by calling
 *           <prefix>_search_in with a descriptor of exactly the FAST
 *           capacities: that is the same capacity guard the fast tier runs
 *           under, reached without going near the tier code, so a give-up
 *           there is precisely "the fast tier would have given up here".
 *
 * `esc` and `pred` come from different code (the entry's escalation test vs
 * the capacity guard inside the run loop) and are compared by the caller. A
 * fast tier bound at the wrong capacity moves `pred` without moving `esc`; a
 * broken escalation test moves `esc` without moving `pred`.
 *
 * THE HOOK IS AN EXTERN THE ARTIFACT CALLS AND THIS FILE DEFINES. The artifact
 * declares no mutable state of its own on any build, which spec §5.3 requires
 * and TS-1 (D19) enforces by scanning emitted text. The counter lives here.
 *
 * Subjects are `a^n b^n` for the `^(a(?1)?b)$` specimen, whose per-level cost
 * `fb_exact_driver.c` measures at 2.000 resume frames and 8.982 trail entries.
 * The DEPTHS ARE NOT HARDCODED: the caller passes them, having found the two
 * tier boundaries by bisection through the same `_in` entry (see
 * run_tiered_entry.sh §3), so this file cannot go green by testing depths that
 * happen to sit on one side of a boundary that moved.
 *
 * Prints one line per depth:
 *     row <n> <ans> <ref> <esc> <pred>
 * where <pred> is 1 when the FAST-sized descriptor gave up and 0 otherwise.
 * Exit 0 on a clean run, 2 on allocation failure or an inert artifact.
 *
 * Usage: tier_driver <n> [n ...]
 * Build: -DTIER_FAST_FRAMES=<n> -DTIER_FAST_TRAIL=<n> -D<PREFIX>_TEST_TIER_HOOK
 *        (the two capacities are read out of the artifact by the harness --
 *        they are `.c`-private VM capacity stamps, §6.3(b), so a driver that
 *        includes only the header cannot see them.)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

#if !defined(TIER_FAST_FRAMES) || !defined(TIER_FAST_TRAIL)
#error "tier_driver.c needs -DTIER_FAST_FRAMES and -DTIER_FAST_TRAIL, read out of the artifact by run_tiered_entry.sh"
#endif

/* The artifact's escalation hook. Defined HERE, never in the artifact. */
static unsigned long escalations;
void rx_tier_escalated(void);
void rx_tier_escalated(void) { escalations++; }

static unsigned char *subject_of(size_t n, size_t *len_out)
{
    size_t len = 2 * n;
    unsigned char *s = malloc(len + 1);
    if (!s) { fprintf(stderr, "tier_driver: out of memory\n"); exit(2); }
    memset(s, 'a', n);
    memset(s + n, 'b', n);
    s[len] = 0;
    *len_out = len;
    return s;
}

/* One `_in` call at a named capacity. Returns the entry's own return value. */
static int in_at(const unsigned char *s, size_t len, size_t nframes, size_t ntrail)
{
    ptrdiff_t caps[RX_NCAPS][2];
    rx_buffers b;
    int r;
    void *f = malloc(nframes * (size_t)RX_RESUME_FRAME_SIZE);
    void *t = malloc(ntrail  * (size_t)RX_TRAIL_FRAME_SIZE);
    if (!f || !t) { fprintf(stderr, "tier_driver: out of memory\n"); exit(2); }
    b.frames = f; b.nframes = nframes;
    b.trail  = t; b.ntrail  = ntrail;
    r = rx_search_in(s, len, 0, caps, &b);
    free(f); free(t);
    return r;
}

int main(int argc, char **argv)
{
    int i;

    if (RX_RESUME_FRAME_SIZE == 0 || RX_TRAIL_FRAME_SIZE == 0) {
        fprintf(stderr, "tier_driver: this artifact reports no resume stack to size\n");
        return 2;
    }
    if (argc < 2) { fprintf(stderr, "usage: tier_driver <n> [n ...]\n"); return 2; }

    for (i = 1; i < argc; i++) {
        size_t n = (size_t)strtoull(argv[i], NULL, 10), len;
        unsigned char *s = subject_of(n, &len);
        int ans, ref, pred;

        /* The reference FIRST and the tiered entry SECOND, so the counter the
         * tiered call leaves behind is not cleared by a later `_in` call. */
        ref  = in_at(s, len, (size_t)RX_RESUME_FRAMES, (size_t)RX_TRAIL_FRAMES);
        pred = in_at(s, len, (size_t)TIER_FAST_FRAMES, (size_t)TIER_FAST_TRAIL)
               == PCREC_ERR_FRAMES;
        escalations = 0;
        {
            ptrdiff_t caps[RX_NCAPS][2];
            ans = rx_search(s, len, 0, caps);
        }
        printf("row %zu %d %d %lu %d\n", n, ans, ref, escalations, pred);
        free(s);
    }
    return 0;
}
