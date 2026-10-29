/*
 * trail_compact_driver.c -- [K134] the VM's trail compaction changes no
 * answer, at any trail capacity.
 *
 * The artifact (prefix `rx`, header "gen.h") is run on one subject through
 * `rx_search_in`: first with large buffers (the REFERENCE, whose trail
 * high-water is read off a canary fill), then once per trail capacity of a
 * ladder from 1 entry up to the high-water, with the reference's frames.
 * Each smaller run must either give up with PCREC_ERR_FRAMES or return
 * EXACTLY the reference's answer: the same rc and the same capture array.
 * Every rung's trail is allocated at EXACTLY its capacity (review
 * 2026-10-29-r2 F11), so under AddressSanitizer a write past the capacity
 * is a heap-buffer-overflow rather than a quiet write into a large buffer's
 * slack that reads as "answered below the high-water". The ladder always
 * ends with a run at the high-water itself, which must answer, so every
 * witness compares at least one answer (F10).
 * A run that answers with less trail than the reference touched is one
 * the compaction made possible (no plain run can answer below its own
 * high-water); the runner counts those so a witness that never reaches the
 * compaction is visible as such (K35).
 *
 * With -DRX_TEST_TIER_HOOK it also runs the un-suffixed entry once and
 * counts the fast tier's escalations: a compaction that could not leave a
 * quarter of the trail free stops for the attempt, so a long subject on
 * the small fast tier escalates once instead of compacting forever.
 *
 * Each further argument is a trail capacity to report on its own, as
 * ` at <capacity>:<rc>`, for a check that pins a documented boundary.
 * TRAIL_LADDER=0 in the environment skips the ladder (`runs 0`): a witness
 * that only times its `at` runs (the bounded-work check) on a subject too
 * long to run a whole ladder over.
 *
 * Prints one line:
 *   ref <rc> hw <entries> runs <n> answered <a> below_hw <b> gaveup <g> mismatch <m> [escalations <e> default_rc <r>] [at <capacity>:<rc>...]
 * Exit 0 when there is no mismatch, 1 on a mismatch, 2 on a setup failure.
 *
 * Usage: trail_compact SUBJECT-FILE [CAPACITY...]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

#ifdef RX_TEST_TIER_HOOK
static unsigned escalations;
void rx_tier_escalated(void) { escalations++; }
#endif

#define REF_FRAMES ((size_t)1 << 20)
#define REF_TRAIL  ((size_t)1 << 22)
#define CANARY     0xA5

static unsigned char *slurp(const char *path, size_t *n)
{
    FILE *f = fopen(path, "rb");
    unsigned char *b;
    long len;
    if (!f) { perror(path); exit(2); }
    if (fseek(f, 0, SEEK_END) != 0 || (len = ftell(f)) < 0) exit(2);
    rewind(f);
    b = malloc((size_t)len + 1);
    if (!b || fread(b, 1, (size_t)len, f) != (size_t)len) exit(2);
    fclose(f);
    *n = (size_t)len;
    return b;
}

static int run(const unsigned char *s, size_t n, void *frames, size_t nframes,
               void *trail, size_t ntrail, ptrdiff_t (*caps)[2])
{
    rx_buffers b;
    b.frames = frames; b.nframes = nframes;
    b.trail  = trail;  b.ntrail  = ntrail;
    return rx_search_in(s, n, 0, caps, &b);
}

/* The ladder: every capacity up to 256, then about 64 steps per doubling,
 * and always the high-water itself last. */
static size_t next_rung(size_t nt, size_t hw)
{
    size_t step = nt < 256 ? 1 : (nt / 64 > 0 ? nt / 64 : 1);
    if (nt == hw) return hw + 1;
    return nt + step > hw ? hw : nt + step;
}

/* One run on a trail of exactly `ntrail` entries, its own allocation. */
static int run_exact(const unsigned char *s, size_t n, void *frames, size_t nframes,
                     size_t ntrail, ptrdiff_t (*caps)[2])
{
    void *t = malloc(ntrail ? ntrail * (size_t)RX_TRAIL_FRAME_SIZE : 1);
    int rc;
    if (!t) { fprintf(stderr, "trail_compact: out of memory\n"); exit(2); }
    rc = run(s, n, frames, nframes, t, ntrail, caps);
    free(t);
    return rc;
}

int main(int argc, char **argv)
{
    size_t n, hw, nt, runs = 0, answered = 0, below = 0, gaveup = 0, mismatch = 0;
    unsigned char *s, *trail;
    void *frames;
    ptrdiff_t ref[RX_NCAPS][2], got[RX_NCAPS][2];
    int rc0, rc, i;
    const int ladder = !(getenv("TRAIL_LADDER") && strcmp(getenv("TRAIL_LADDER"), "0") == 0);

    if (argc < 2) { fprintf(stderr, "usage: trail_compact SUBJECT-FILE [CAPACITY...]\n"); return 2; }
    s = slurp(argv[1], &n);
    frames = malloc(REF_FRAMES * (size_t)RX_RESUME_FRAME_SIZE);
    trail  = malloc(REF_TRAIL  * (size_t)RX_TRAIL_FRAME_SIZE);
    if (!frames || !trail) { fprintf(stderr, "trail_compact: out of memory\n"); return 2; }
    memset(trail, CANARY, REF_TRAIL * (size_t)RX_TRAIL_FRAME_SIZE);
    memset(ref, 0, sizeof ref);
    rc0 = run(s, n, frames, REF_FRAMES, trail, REF_TRAIL, ref);
    {
        size_t bytes = REF_TRAIL * (size_t)RX_TRAIL_FRAME_SIZE;
        while (bytes > 0 && trail[bytes - 1] == CANARY) bytes--;
        hw = (bytes + (size_t)RX_TRAIL_FRAME_SIZE - 1) / (size_t)RX_TRAIL_FRAME_SIZE;
    }
    if (rc0 == PCREC_ERR_FRAMES) { fprintf(stderr, "trail_compact: the reference gave up\n"); return 2; }

    /* Every capacity up to 256, then about 64 steps per doubling up to the
     * high-water: the small end is where compaction runs at every
     * checkpoint, the ladder above is where it runs once or twice. */
    for (nt = ladder ? 1 : hw + 1; nt <= hw; nt = next_rung(nt, hw)) {
        memset(got, 0, sizeof got);
        rc = run_exact(s, n, frames, REF_FRAMES, nt, got);
        runs++;
        if (rc == PCREC_ERR_FRAMES) { gaveup++; continue; }
        if (rc != rc0 || (rc0 >= 0 && memcmp(got, ref, sizeof ref) != 0)) {
            mismatch++;
            fprintf(stderr, "MISMATCH at trail %zu: rc %d (reference %d), group 0 %td..%td (reference %td..%td)\n",
                    nt, rc, rc0, got[0][0], got[0][1], ref[0][0], ref[0][1]);
            continue;
        }
        answered++;
        if (nt < hw) below++;
    }
    printf("ref %d hw %zu runs %zu answered %zu below_hw %zu gaveup %zu mismatch %zu",
           rc0, hw, runs, answered, below, gaveup, mismatch);
#ifdef RX_TEST_TIER_HOOK
    {
        int rd = rx_search(s, n, 0, got);
        printf(" escalations %u default_rc %d", escalations, rd);
        if (rd != PCREC_ERR_FRAMES && (rd != rc0 || (rc0 >= 0 && memcmp(got, ref, sizeof ref) != 0)))
            mismatch++;
    }
#endif
    for (i = 2; i < argc; i++) {
        nt = (size_t)strtoul(argv[i], NULL, 10);
        printf(" at %zu:%d", nt, run_exact(s, n, frames, REF_FRAMES, nt, got));
    }
    printf("\n");
    free(s); free(frames); free(trail);
    return mismatch ? 1 : 0;
}
