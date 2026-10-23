/* tests/encseam/findall_driver.c — docs/spec/match_api.md §3.1's find-all
 * loop, compiled against one generated artifact and run for real.
 *
 * The loop below is the spec's, TRANSCRIBED — if the two ever differ, the
 * spec is wrong or this is, and either way the check has stopped meaning
 * what it says. The one thing to notice is the advance: it goes through the
 * artifact's own `fa_next_pos` RESIDUAL entry rather than a literal `+ 1`,
 * which is [M5-SEAM]'s whole claim — under the byte encoding the helper IS
 * `pos + 1`, and a future UTF-8 backend supplies a boundary-aware body
 * without this loop changing a character.
 *
 * Prints one `start,end` per match, space-separated, so the runner can diff
 * it against the python `re` oracle's line for the same case.
 *
 * The prefix is fixed at `fa` (the runner compiles every fixture with
 * `-p fa`), because a driver cannot be generic over a C identifier prefix.
 *
 * `findall_driver iter <subject>` runs the find-all ITERATOR instead, through
 * RX_FOREACH over the artifact's own record (§3.8.2, [FINDALL-NEXT] I4): its
 * matches are PCRE2's global iteration's, so the runner holds them to
 * `re.finditer`, where the loop above is held to the protocol oracle. */
#include <stdio.h>
#include <string.h>

#include "fa.h"

int main(int argc, char **argv)
{
    const unsigned char *s;
    size_t n, p;
    ptrdiff_t caps[FA_NCAPS][2];
    int first = 1;

    if (argc < 2) { fprintf(stderr, "usage: %s [iter] <subject>\n", argv[0]); return 2; }
    if (argc == 3 && strcmp(argv[1], "iter") == 0) {
        rx_iter it;
        s = (const unsigned char *)argv[2];
        n = strlen(argv[2]);
        it = RX_ITER_INIT(s, n);
        RX_FOREACH(&fa_info, &it, m) {
            printf("%s%td,%td", first ? "" : " ", m[0][0], m[0][1]);
            first = 0;
        }
        printf("\n");
        if (it.rc < 0) { fprintf(stderr, "give-up code %d\n", it.rc); return 3; }
        return 0;
    }
    s = (const unsigned char *)argv[1];
    n = strlen(argv[1]);

    p = 0;
    while (p <= n) {
        int r = fa_search(s, n, p, caps);
        if (r != 1) {
            if (r < 0) {           /* a give-up is not a no-match (§4) */
                fprintf(stderr, "give-up code %d\n", r);
                return 3;
            }
            break;                 /* 0 = done */
        }
        printf("%s%td,%td", first ? "" : " ", caps[0][0], caps[0][1]);
        first = 0;
        p = (caps[0][1] > caps[0][0])
              ? fa_next_pos(s, n, (size_t)caps[0][1] - 1)   /* non-empty [K75] */
              : fa_next_pos(s, n, (size_t)caps[0][0]);      /* EMPTY */
    }
    printf("\n");
    return 0;
}
