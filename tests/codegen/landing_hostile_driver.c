/* tests/codegen/landing_hostile_driver.c — [START-LANDING] the STANDING
 * HOSTILE CELL's driver (docs/design/start_landing.md §7.3 §H, §2.5.5).
 *
 * The RECOVER row `landing` reads the start off the forward scan's last
 * landing, and where the character there does not decode, §2.5.2's post-loop
 * SKIP steps to the first position after it that does. That skip is linear:
 * one decode per ill-formed byte of the final excursion, never a re-scan.
 * Revision 1's RESTART (re-enter the scan at `landing + 1`) was QUADRATIC on
 * exactly this subject — `K` copies of one lead byte, then `a` — measured
 * 2.99 s at K = 64 Ki and ~13 min at 1 MiB. This driver builds that subject
 * (`argv[1]` the lead byte in hex, `argv[2]` K) and runs a FIND-ALL over it
 * through `on_search` (match_api.md §3.1's loop); the caller bounds it with a
 * wall clock, so a re-entering guard is caught by the bound, and checks the
 * one answer printed: `count first_start first_end`. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "on.h"

int main(int argc, char **argv)
{
    if (argc != 3) { fprintf(stderr, "usage: %s LEADHEX K\n", argv[0]); return 2; }
    unsigned lead = (unsigned)strtoul(argv[1], NULL, 16);
    size_t k = (size_t)strtoul(argv[2], NULL, 10), n = k + 1, pos = 0;
    unsigned char *s = malloc(n);
    if (!s) return 2;
    memset(s, (int)lead, k);
    s[k] = 'a';
    long count = 0;
    ptrdiff_t first[2] = { -1, -1 };
    while (pos <= n) {
        ptrdiff_t caps[ON_NCAPS][2];
        int r = on_search(s, n, pos, caps);
        if (r != 1) break;
        if (count++ == 0) { first[0] = caps[0][0]; first[1] = caps[0][1]; }
        if (caps[0][1] > caps[0][0]) pos = (size_t)caps[0][1];
        else pos = (size_t)caps[0][1] + 1;
    }
    printf("%ld %td %td\n", count, first[0], first[1]);
    free(s);
    return 0;
}
