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
 * not enough, and this driver reports FOUR things per subject:
 *
 *   ans     what <prefix>_search returns (the tiered entry).
 *   ref     what <prefix>_search_in returns with a DEFAULT-sized descriptor.
 *           This is the SINGLE-TIER execution, reached through an entry
 *           [OPT-1] does not touch — the reference `ans` must equal.
 *   spans   whether the CAPTURE SPANS the two agree on match, byte for byte
 *           (`memcmp` over the whole `RX_NCAPS`-pair array). See below.
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
 * **THE SPANS ARE COMPARED, NOT ONLY THE RETURNS** (r38 finding 3b). Design
 * §6 and spec §10.9 promise "the value returned AND the capture spans
 * written", and a returns-only driver checks half of that. The half it skips
 * is the half a tier bug would land in: the deep tier re-runs the match from
 * scratch, so a defect that lost the capture copy-out, or that returned the
 * FAST attempt's untouched `caps` array beside the DEEP attempt's return
 * value, is invisible in `ans` and loud here. The comparison is a `memcmp`
 * over the whole array rather than a per-group loop, so a group nobody
 * thought to check is still covered.
 *
 * **AND THE WITNESS MUST HAVE MORE THAN ONE GROUP.** The `^(a(?1)?b)$`
 * specimen has a single group whose span is the whole match, so on it "the
 * spans agree" is nearly implied by "the returns agree" and the check is much
 * weaker than it looks. `((a)|(aa))+b` (r38's own witness) has three groups,
 * two of them alternation arms that a re-run could legitimately fill
 * differently if anything about the replay were not a replay. The harness
 * drives both.
 *
 * THE HOOK IS AN EXTERN THE ARTIFACT CALLS AND THIS FILE DEFINES. The artifact
 * declares no mutable state of its own on any build, which spec §5.3 requires
 * and TS-1 (D19) enforces by scanning emitted text. The counter lives here.
 *
 * SUBJECT SHAPES, because the two witnesses need different ones:
 *   anbn   a^n b^n  — the `^(a(?1)?b)$` specimen, whose per-level cost
 *                     `fb_exact_driver.c` measures at 2.000 resume frames and
 *                     8.982 trail entries.
 *   anb    a^n b    — `((a)|(aa))+b`, where the depth is the ITERATION count.
 *
 * THE DEPTHS ARE NOT HARDCODED: the caller passes them, having found the two
 * tier boundaries by bisection through the same `_in` entry (see
 * run_tiered_entry.sh §3), so this file cannot go green by testing depths that
 * happen to sit on one side of a boundary that moved.
 *
 * Prints one line per depth:
 *     row <n> <ans> <ref> <esc> <pred> <spans>
 * where <pred> is 1 when the FAST-sized descriptor gave up and 0 otherwise,
 * and <spans> is 1 when the two capture arrays agree, 0 when they differ, and
 * `-` when neither call matched so there is nothing to compare.
 * Exit 0 on a clean run, 2 on allocation failure or an inert artifact.
 *
 * Usage: tier_driver <anbn|anb> <n> [n ...]
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

/* a^n b^n (shape 0) or a^n b (shape 1). */
static unsigned char *subject_of(size_t n, int shape, size_t *len_out)
{
    size_t len = shape ? n + 1 : 2 * n;
    unsigned char *s = malloc(len + 1);
    if (!s) { fprintf(stderr, "tier_driver: out of memory\n"); exit(2); }
    memset(s, 'a', n);
    if (shape) s[n] = 'b'; else memset(s + n, 'b', n);
    s[len] = 0;
    *len_out = len;
    return s;
}

/* One `_in` call at a named capacity. `caps_out`, when non-NULL, receives the
 * capture array EXACTLY as the entry left it — untouched on a negative return,
 * which is A-8's rule and is why the caller only compares spans when both
 * calls matched. */
static int in_at(const unsigned char *s, size_t len, size_t nframes, size_t ntrail,
                 ptrdiff_t (*caps_out)[2])
{
    ptrdiff_t caps[RX_NCAPS][2];
    rx_buffers b;
    int r;
    void *f = malloc(nframes * (size_t)RX_RESUME_FRAME_SIZE);
    void *t = malloc(ntrail  * (size_t)RX_TRAIL_FRAME_SIZE);
    if (!f || !t) { fprintf(stderr, "tier_driver: out of memory\n"); exit(2); }
    memset(caps, 0, sizeof caps);
    b.frames = f; b.nframes = nframes;
    b.trail  = t; b.ntrail  = ntrail;
    r = rx_search_in(s, len, 0, caps, &b);
    if (caps_out) memcpy(caps_out, caps, sizeof caps);
    free(f); free(t);
    return r;
}

int main(int argc, char **argv)
{
    int i, shape;

    if (RX_RESUME_FRAME_SIZE == 0 || RX_TRAIL_FRAME_SIZE == 0) {
        fprintf(stderr, "tier_driver: this artifact reports no resume stack to size\n");
        return 2;
    }
    if (argc < 3) { fprintf(stderr, "usage: tier_driver <anbn|anb> <n> [n ...]\n"); return 2; }
    if      (strcmp(argv[1], "anbn") == 0) shape = 0;
    else if (strcmp(argv[1], "anb")  == 0) shape = 1;
    else { fprintf(stderr, "tier_driver: unknown subject shape '%s'\n", argv[1]); return 2; }

    for (i = 2; i < argc; i++) {
        size_t n = (size_t)strtoull(argv[i], NULL, 10), len;
        unsigned char *s = subject_of(n, shape, &len);
        ptrdiff_t ref_caps[RX_NCAPS][2], ans_caps[RX_NCAPS][2];
        int ans, ref, pred;
        const char *spans;

        /* The reference FIRST and the tiered entry SECOND, so the counter the
         * tiered call leaves behind is not cleared by a later `_in` call. */
        memset(ref_caps, 0, sizeof ref_caps);
        memset(ans_caps, 0, sizeof ans_caps);
        ref  = in_at(s, len, (size_t)RX_RESUME_FRAMES, (size_t)RX_TRAIL_FRAMES, ref_caps);
        pred = in_at(s, len, (size_t)TIER_FAST_FRAMES, (size_t)TIER_FAST_TRAIL, NULL)
               == PCREC_ERR_FRAMES;
        escalations = 0;
        ans = rx_search(s, len, 0, ans_caps);

        /* Spans are only DEFINED on a match (§3.1: `caps` is left untouched on
         * every other return), so comparing them elsewhere would be comparing
         * two arrays this driver zeroed — green for a reason that has nothing
         * to do with the tier. Reported as `-` there instead, and the harness
         * asserts that the compared population is not empty. */
        if (ans == 1 && ref == 1)
            spans = memcmp(ans_caps, ref_caps, sizeof ans_caps) == 0 ? "1" : "0";
        else
            spans = "-";

        printf("row %zu %d %d %lu %d %s\n", n, ans, ref, escalations, pred, spans);
        free(s);
    }
    return 0;
}
