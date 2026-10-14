/* The layout probe's driver (compound_entries.md §2): N iterations of
 *   (a) a find-all over SUBJ with <p>_search and today's advance (§3.1.3), and
 *   (b) one <p>_match probe at every position of SUBJ,
 * summed into a checksum so nothing is dead. Built once per (witness, layout
 * variant); run under callgrind for an INSTRUCTION count (no clock).
 * usage: drv N SUBJECT   (SUBJECT taken as bytes, no escapes) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include ARTIFACT_H

int main(int argc, char **argv)
{
    if (argc < 3) return 2;
    long N = atol(argv[1]);
    const unsigned char *s = (const unsigned char *)argv[2];
    size_t n = strlen(argv[2]);
    unsigned long sum = 0;
    ptrdiff_t caps[RX_NCAPS][2];
    for (long it = 0; it < N; it++) {
        size_t p = 0;
        while (p <= n) {
            int r = rx_search(s, n, p, caps);
            if (r != 1) break;
            sum += (unsigned long)caps[0][0] * 31u + (unsigned long)caps[0][1];
            size_t b = (size_t)caps[0][0], e = (size_t)caps[0][1];
            p = e > b ? rx_next_pos(s, n, e - 1) : rx_next_pos(s, n, b);
        }
        for (size_t q = 0; q <= n; q++) {
            rx_ctx c = { 0 };
            c.subject = s; c.len = n; c.pos = q;
            ptrdiff_t m = rx_match(&c);
            sum += (unsigned long)(m + 2);
        }
    }
    printf("%lu\n", sum);
    return 0;
}
