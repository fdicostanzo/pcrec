/* p1build differential driver: find-all over length-prefixed subjects on stdin. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "gen.c"
int main(void)
{
    static unsigned char buf[1 << 20];
    uint32_t n;
    ptrdiff_t caps[RX_NCAPS][2];
    while (fread(&n, 4, 1, stdin) == 1) {
        if (n && fread(buf, 1, n, stdin) != n) return 2;
        size_t sf = 0;
        for (;;) {
            if (sf > n) break;
            int rc = rx_search(buf, n, sf, caps);
            if (rc == 0) break;
            if (rc < 0) { printf("E%d ", rc); break; }
            printf("%td,%td ", caps[0][0], caps[0][1]);
            sf = caps[0][1] == caps[0][0] ? (size_t)caps[0][1] + 1 : (size_t)caps[0][1];
        }
        putchar('\n');
    }
    return 0;
}
