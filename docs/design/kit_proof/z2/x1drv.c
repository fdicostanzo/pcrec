/* docs/design/kit_proof/z2/x1drv.c — X1's pcrec side (kit_proof.md §7 Z2).
 *
 * Linked with ONE built harness artifact (`build/pcrec-harness
 * --harness=kit-proof ... -o a.c`), it answers x0pcre.c's `F` question for
 * the artifact: per subject line (hex, "" = empty) on stdin, one reply line
 *   rx_search at every startoffset 0..n: "a:b" | "-" | "eRC", comma list,
 *   then "|" and the find-all loop's matches: match_api.md §3.1.3's loop as
 *   written, rx_next_pos(end - 1) after a non-empty match, rx_next_pos(start)
 *   after an empty one.
 * The reply format is x0pcre's (whose loop is PCRE2's pos = end, +1 after an
 * empty match), so x1 compares the two lines' fields.
 *
 * X1_PLANT=1 in the environment reports every match end one byte late: X1's
 * own failing-direction control (it must read red).
 *
 *   gcc -O1 -std=gnu11 -include DIR/a.h -o DIR/drv x1drv.c DIR/a.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>

static int hexval(int c)
{
    return c <= '9' ? c - '0' : (c | 0x20) - 'a' + 10;
}

int main(void)
{
    static char line[1 << 16];
    static unsigned char s[1 << 15];
    ptrdiff_t caps[64][2];
    int plant = getenv("X1_PLANT") != NULL;
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        for (char *h = line; h[0] && h[1] && h[0] != '\n'; h += 2)
            s[n++] = (unsigned char)(hexval(h[0]) << 4 | hexval(h[1]));
        for (size_t sf = 0; sf <= n; sf++) {
            int r = rx_search(s, n, sf, caps);
            if (sf) putchar(',');
            if (r == 1) printf("%td:%td", caps[0][0], caps[0][1] + plant);
            else if (r == 0) putchar('-');
            else printf("e%d", r);
        }
        putchar('|');
        size_t pos = 0;
        int first = 1;
        while (pos <= n) {
            if (rx_search(s, n, pos, caps) != 1)
                break;
            printf("%s%td:%td", first ? "" : ",", caps[0][0], caps[0][1]);
            first = 0;
            pos = caps[0][1] > caps[0][0] ? rx_next_pos(s, n, (size_t)caps[0][1] - 1)
                                          : rx_next_pos(s, n, (size_t)caps[0][0]);
        }
        putchar('\n');
        fflush(stdout);
    }
    return 0;
}
