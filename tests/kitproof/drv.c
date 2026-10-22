/* tests/kitproof/drv.c — pcrec's side of run_cover.sh ([KIT-VERIFY] Z2).
 *
 * Linked with ONE built artifact (compiled by run_cover.sh, usually through
 * the harness lever that routes `cover`), it answers oracle.c's question:
 * per subject line (hex) on stdin, one reply line in oracle.c's format —
 * rx_search at every startoffset 0..n, "-" no match, "eRC" a give-up, or
 * every group's span "s:e" joined by "/" (PCREC_UNSET reads -1:-1); then "|"
 * and match_api.md §3.1.3's find-all loop as written (rx_next_pos after each
 * match). Where oracle.c wrote "x" (a startoffset on a UTF-8 continuation
 * byte) the check does not compare. Before every call the array is filled
 * with a sentinel, so a group the artifact leaves unwritten reads as that
 * sentinel rather than as whatever an earlier call left (K78's fill).
 *
 *   gcc -O1 -std=gnu11 -include DIR/a.h -o DIR/drv tests/kitproof/drv.c DIR/a.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>

static int hexval(int c)
{
    return c <= '9' ? c - '0' : (c | 0x20) - 'a' + 10;
}

static void spans(ptrdiff_t (*caps)[2])
{
    for (int g = 0; g < RX_NCAPS; g++)
        printf("%s%td:%td", g ? "/" : "", caps[g][0], caps[g][1]);
}

int main(void)
{
    static char line[1 << 16];
    static unsigned char s[1 << 15];
    ptrdiff_t caps[RX_NCAPS][2];
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        for (char *h = line; h[0] && h[1] && h[0] != '\n'; h += 2)
            s[n++] = (unsigned char)(hexval(h[0]) << 4 | hexval(h[1]));
        for (size_t sf = 0; sf <= n; sf++) {
            memset(caps, 0x55, sizeof caps);
            int r = rx_search(s, n, sf, caps);
            if (sf) putchar(',');
            if (r == 1) spans(caps);
            else if (r == 0) putchar('-');
            else printf("e%d", r);
        }
        putchar('|');
        size_t pos = 0;
        for (int it = 0; pos <= n; it++) {
            memset(caps, 0x55, sizeof caps);
            if (rx_search(s, n, pos, caps) != 1)
                break;
            if (it) putchar(',');
            spans(caps);
            pos = caps[0][1] > caps[0][0] ? rx_next_pos(s, n, (size_t)caps[0][1] - 1)
                                          : rx_next_pos(s, n, (size_t)caps[0][0]);
        }
        putchar('\n');
        fflush(stdout);
    }
    return 0;
}
