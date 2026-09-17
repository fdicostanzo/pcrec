/* f3search measurement driver — lane f3search, O-31 finding 3 round 2.
 *
 * Drives the artifact for ^(([a-z]+)*)+$ (prefix rx) on the bench's exact
 * subject shape b"a"*n + b"!" in four modes:
 *
 *   search1  — ONE <prefix>_search call, timed. THE question's number.
 *   findall  — docs/spec/match_api.md §3.1's find-all loop, transcribed
 *              from tests/encseam/findall_driver.c (the house precedent),
 *              timed end to end. A give-up breaks it, so on this subject
 *              it is one call plus loop overhead.
 *   match    — the anchored match form (rx_match_caps), round-1 contrast.
 *   batch    — the BENCH's regime: an outer iters loop, each iteration
 *              running the bench driver's own find-all body (advance
 *              pos = max(end, pos+1); a give-up breaks the INNER loop
 *              only, the batch continues). testees/pcrec/driver.c:715-733.
 *
 * Compiled with -DRX_TEST_TIER_HOOK so deep-tier escalations are counted.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "evil.h"   /* the emitted artifact for ^(([a-z]+)*)+$, -p rx */

static long escalations = 0;
void rx_tier_escalated(void) { escalations++; }

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

static const char *rname(int r)
{
    switch (r) {
    case 1: return "match";
    case 0: return "nomatch";
    case PCREC_ERR_STEPS:  return "giveup:STEPS";
    case PCREC_ERR_FRAMES: return "giveup:FRAMES";
    case PCREC_ERR_WORK:   return "giveup:WORK";
    default: return "other";
    }
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: %s <n> search1|findall|match|batch [iters]\n", argv[0]);
        return 2;
    }
    size_t n = (size_t)atol(argv[1]);
    const char *mode = argv[2];
    long iters = argc > 3 ? atol(argv[3]) : 1;

    size_t len = n + 1;
    unsigned char *s = malloc(len);
    memset(s, 'a', n);
    s[n] = '!';
    ptrdiff_t caps[RX_NCAPS][2];

    double t0 = now();

    if (!strcmp(mode, "search1")) {
        int r = rx_search(s, len, 0, caps);
        printf("mode=search1 n=%zu r=%d(%s) wall=%.3fs escalations=%ld\n",
               n, r, rname(r), now() - t0, escalations);
    } else if (!strcmp(mode, "findall")) {
        /* §3.1's loop, transcribed (tests/encseam/findall_driver.c). */
        size_t p = 0;
        int last = 0, count = 0;
        while (p <= len) {
            int r = rx_search(s, len, p, caps);
            last = r;
            if (r != 1) break;              /* 0 = done; < 0 = give-up */
            count++;
            p = (caps[0][1] > caps[0][0])
                  ? (size_t)caps[0][1]
                  : rx_next_pos(s, len, (size_t)caps[0][0]);
        }
        printf("mode=findall n=%zu last=%d(%s) matches=%d wall=%.3fs escalations=%ld\n",
               n, last, rname(last), count, now() - t0, escalations);
    } else if (!strcmp(mode, "match")) {
        rx_ctx ctx = { s, len, 0, 0, NULL, NULL };
        ptrdiff_t r = rx_match_caps(&ctx, caps);
        printf("mode=match n=%zu r=%td(%s) wall=%.3fs escalations=%ld\n",
               n, r, r >= 0 ? "match" : rname((int)r), now() - t0, escalations);
    } else if (!strcmp(mode, "batch")) {
        /* The bench's regime, verbatim shape: driver.c:715-733. */
        long it;
        int firstgiveup = 0;
        double firstwall = -1.0;
        for (it = 0; it < iters; it++) {
            size_t pos = 0;
            long count = 0;
            for (;;) {
                int r = rx_search(s, len, pos, caps);
                if (r == 0) break;
                if (r < 0) { if (count == 0 && !firstgiveup) firstgiveup = r; break; }
                count++;
                size_t end = (size_t)caps[0][1];
                pos = (end > pos) ? end : pos + 1;
                if (pos > len) break;
            }
            if (it == 0) firstwall = now() - t0;
        }
        printf("mode=batch n=%zu iters=%ld first_iter_wall=%.3fs total_wall=%.3fs "
               "first_giveup=%d(%s) escalations=%ld\n",
               n, iters, firstwall, now() - t0, firstgiveup, rname(firstgiveup),
               escalations);
    } else if (!strcmp(mode, "search_in")) {
        /* The bench's vm-in-caps arm: caller-supplied buffers, sized like
         * the bench's own descriptor (generous, no FRAMES give-up). */
        void *fr = malloc(65536 * RX_RESUME_FRAME_SIZE);
        void *tr = malloc(65536 * RX_TRAIL_FRAME_SIZE);
        rx_buffers buf = { fr, 65536, tr, 65536 };
        int r = rx_search_in(s, len, 0, caps, &buf);
        printf("mode=search_in n=%zu r=%d(%s) wall=%.3fs escalations=%ld\n",
               n, r, rname(r), now() - t0, escalations);
    } else {
        fprintf(stderr, "unknown mode %s\n", mode);
        return 2;
    }
    return 0;
}
