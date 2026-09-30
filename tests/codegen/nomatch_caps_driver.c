/* tests/codegen/nomatch_caps_driver.c — K78: match_api.md §3.1's caps
 * contract, asserted on every caller-facing entry of ONE artifact.
 *
 * Compiled against a `-p rx` artifact (`a.c`/`a.h`, `-I` its directory) by
 * run_nomatch_caps.sh. For every subject below at every startpos 0..n+1,
 * each entry that takes a caps array is called on an array pre-filled with a
 * SENTINEL (neither PCREC_UNSET nor any offset), one pair LONGER than
 * RX_NCAPS, and the result is scored:
 *
 *   non-positive / negative return  every pair, the guard pair included,
 *                                   still holds the sentinel ("untouched")
 *   success                         pairs 0..RX_NCAPS-1 all written, the
 *                                   guard pair RX_NCAPS still the sentinel
 *
 * `_search` succeeds on 1; the anchored `_match_caps` on a length >= 0. The
 * `_in` spellings are called with NULL (defined to be the un-suffixed entry,
 * §10.3) and, when the script passes -DNMC_HAVE_FRAMES (a VM artifact's
 * buffers struct), with a one-frame descriptor too — so a FRAMES give-up,
 * another negative return, is scored the same way.
 *
 * Output: one line `cells NEG NEGBAD POS POSBAD` on stdout, and the first
 * few offending calls on stderr. Exit 0 whatever the counts (the script
 * scores them); 2 on an internal error. */
#include <stdio.h>
#include <string.h>
#include "a.h"

#define NMC_SENT ((ptrdiff_t)-77)

static const char *const subjects[] = {
    "", "zz", "b", "ab", "abc", "ba", "aaaa", "bbbb", "a\nb", "\n",
    "xyz", "0123", "foo bar", "hello world", "ZZZZZZZZ", "\xc3\xa9t\xc3\xa9",
    "\x80\xff", "a1b2c3", "_ _", "abcabcabc",
};

static ptrdiff_t caps[RX_NCAPS + 1][2];
static long neg, negbad, pos, posbad, shown;

static void fill(void)
{
    for (int k = 0; k <= RX_NCAPS; k++) caps[k][0] = caps[k][1] = NMC_SENT;
}

/* The first slot that breaks the contract for this outcome, or -1. */
static int first_bad(int success)
{
    for (int k = 0; k <= RX_NCAPS; k++) {
        int untouched = caps[k][0] == NMC_SENT && caps[k][1] == NMC_SENT;
        int written   = caps[k][0] != NMC_SENT && caps[k][1] != NMC_SENT;
        if (k == RX_NCAPS || !success) { if (!untouched) return k; }
        else if (!written) return k;
    }
    return -1;
}

static void score(const char *entry, const char *subj, size_t at,
                  long ret, int success)
{
    int k = first_bad(success);
    if (success) { pos++; if (k >= 0) posbad++; }
    else         { neg++; if (k >= 0) negbad++; }
    if (k >= 0 && shown++ < 4)
        fprintf(stderr, "  %s on \"%s\" at %zu returned %ld: slot %d is {%td,%td}\n",
                entry, subj, at, ret, k, caps[k][0], caps[k][1]);
}

int main(void)
{
#ifdef NMC_HAVE_FRAMES
    static _Alignas(16) unsigned char fr[RX_RESUME_FRAME_SIZE + 16];
    static _Alignas(16) unsigned char tr[RX_TRAIL_FRAME_SIZE + 16];
    rx_buffers tiny;
    memset(&tiny, 0, sizeof tiny);
    tiny.frames = fr; tiny.nframes = 1;
    tiny.trail  = tr; tiny.ntrail  = 1;
#endif
    for (size_t si = 0; si < sizeof subjects / sizeof subjects[0]; si++) {
        const unsigned char *s = (const unsigned char *)subjects[si];
        size_t n = strlen(subjects[si]);
        for (size_t at = 0; at <= n + 1; at++) {
            rx_ctx ctx;
            memset(&ctx, 0, sizeof ctx);
            ctx.subject = s; ctx.len = n; ctx.pos = at;
            long r;

            fill(); r = rx_search(s, n, at, caps);
            score("_search", subjects[si], at, r, r == 1);
            fill(); r = rx_search_in(s, n, at, caps, NULL);
            score("_search_in(NULL)", subjects[si], at, r, r == 1);
            fill(); r = (long)rx_match_caps(&ctx, caps);
            score("_match_caps", subjects[si], at, r, r >= 0);
            fill(); r = (long)rx_match_caps_in(&ctx, caps, NULL);
            score("_match_caps_in(NULL)", subjects[si], at, r, r >= 0);
#ifdef NMC_HAVE_FRAMES
            fill(); r = rx_search_in(s, n, at, caps, &tiny);
            score("_search_in(1 frame)", subjects[si], at, r, r == 1);
            fill(); r = (long)rx_match_caps_in(&ctx, caps, &tiny);
            score("_match_caps_in(1 frame)", subjects[si], at, r, r >= 0);
#endif
        }
    }
    printf("cells %ld %ld %ld %ld\n", neg, negbad, pos, posbad);
    return 0;
}
