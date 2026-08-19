/* tests/assertions/gstart_findall.c — [M6.2] WAVE D: `docs/spec/match_api.md`
 * §3.1's find-all loop, compiled against one `\G` artifact and run for real.
 *
 * THIS IS WHERE `\G` GETS ITS MEANING (assertions_design.md §4.3). §3.1's
 * loop passes its resume position as `startpos`, so under that loop `\G`
 * means "contiguous with the previous match" — which is exactly PCRE2's
 * global-iteration semantics, where each `pcre2_match` call advances
 * `start_offset`. The two agree with no work, because pcrec's search entry
 * already threads the parameter PCRE2 threads, and THAT is the property this
 * driver exists to demonstrate rather than assert.
 *
 * A `.rxt` block cannot see it: a block drives ONE search. `\G\w+` on
 * "ab cd" reports (0,2) from a single search at startpos 0 whether or not the
 * `\G` is honoured on the SECOND call, and it is the second call that
 * separates a tokenizer from a scanner.
 *
 * The loop below is TRANSCRIBED from tests/encseam/findall_driver.c, which is
 * itself transcribed from the spec — deliberately the same loop and not a
 * second interpretation of §3.1, since the whole claim is about what §3.1's
 * loop does. It differs in one thing only: it reads its subject from a FILE
 * rather than from argv, because this wave's subjects contain newlines and
 * the runner writes exact bytes to disk for the libpcre2 oracle anyway.
 *
 * The prefix is fixed at `fa` (the runner compiles every case with `-p fa`),
 * because a driver cannot be generic over a C identifier prefix. The HEADER
 * name is not the prefix: `pcrec -o <dir>/gen.c` writes `<dir>/gen.h`
 * whatever `-p` says, so the include is `gen.h` and only the symbols carry
 * the prefix.
 *
 * Usage: fa_findall <subject-file>
 * Prints one `start,end` per match, space-separated. */
#include <stdio.h>
#include <string.h>

#include "gen.h"

int main(int argc, char **argv)
{
    unsigned char buf[1 << 16];
    const unsigned char *s = buf;
    size_t n, p;
    FILE *f;
    ptrdiff_t caps[FA_NCAPS][2];
    int first = 1;

    if (argc < 2) { fprintf(stderr, "usage: %s <subject-file>\n", argv[0]); return 2; }
    f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    n = fread(buf, 1, sizeof buf, f);
    fclose(f);

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
              ? (size_t)caps[0][1]                          /* non-empty */
              : fa_next_pos(s, n, (size_t)caps[0][0]);      /* EMPTY */
    }
    printf("\n");
    return 0;
}
