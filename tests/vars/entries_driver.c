/* tests/vars/entries_driver.c -- K129: every entry refuses an UNSET bare
 * ${name} with PCREC_ERR_UNSET_VAR, whatever a proof-based early exit could
 * have answered first (vars.md §5; match_api.md §3.2¶2: the anchored entries
 * make the search entry's checks, in its order).
 *
 * Usage: entries_driver HEXSUBJECT...   (each subject hex-encoded, - empty)
 * Calls all six entries -- _search, _search_in, _match, _match_in,
 * _match_caps, _match_caps_in -- at offset 0 with NO variables bound, and
 * prints one line per subject per entry that did NOT return -8, then
 * "refused N of M". Exit 0 only when every call refused. Links against the
 * artifact compiled as prefix `rx` (art.c / art.h). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "art.h"

static size_t unhex(const char *h, unsigned char *out)
{
    size_t n = 0;
    if (strcmp(h, "-") == 0) return 0;
    for (; h[0] && h[1] && n < 256; h += 2) {
        unsigned v;
        if (sscanf(h, "%2x", &v) != 1) { fprintf(stderr, "bad hex: %s\n", h); exit(2); }
        out[n++] = (unsigned char)v;
    }
    return n;
}

int main(int argc, char **argv)
{
    static unsigned char frames[64 * RX_RESUME_FRAME_SIZE] __attribute__((aligned(16)));
    static unsigned char trail[64 * RX_TRAIL_FRAME_SIZE] __attribute__((aligned(16)));
    const rx_buffers buf = { frames, 64, trail, 64 };
    int refused = 0, calls = 0;

    for (int i = 1; i < argc; i++) {
        unsigned char s[256];
        size_t n = unhex(argv[i], s);
        rx_ctx ctx = { s, n, 0, 0, NULL, NULL, NULL, 0 };
        ptrdiff_t caps[RX_NCAPS][2];
        long r[6];
        static const char *const name[6] = {
            "search", "search_in", "match", "match_in", "match_caps", "match_caps_in" };

        r[0] = rx_search(s, n, 0, caps, NULL, 0);
        r[1] = rx_search_in(s, n, 0, caps, NULL, 0, &buf);
        r[2] = (long)rx_match(&ctx);
        r[3] = (long)rx_match_in(&ctx, &buf);
        r[4] = (long)rx_match_caps(&ctx, caps);
        r[5] = (long)rx_match_caps_in(&ctx, caps, &buf);
        for (int e = 0; e < 6; e++) {
            calls++;
            if (r[e] == PCREC_ERR_UNSET_VAR) refused++;
            else printf("subject %s: %s returned %ld, not %d\n",
                        argv[i], name[e], r[e], PCREC_ERR_UNSET_VAR);
        }
    }
    printf("refused %d of %d\n", refused, calls);
    return refused == calls && calls > 0 ? 0 : 1;
}
