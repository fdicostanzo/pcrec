/* d27 driver: one search over a subject file, through a self-contained
 * artifact (`-o -`, cli.md §1.2¶2) #included as GEN_C, prefix rx.
 * Prints "M s e [s1 e1 ...]", "N", or "R <code>" (match_api.md §3.1¶1). */
#include <stdio.h>
#include <stdlib.h>
#include GEN_C

int main(int argc, char **argv)
{
    static unsigned char buf[4096];
    FILE *f;
    size_t n;
    ptrdiff_t caps[RX_NCAPS][2];
    int r, k;

    if (argc != 2 || !(f = fopen(argv[1], "rb")))
        return 2;
    n = fread(buf, 1, sizeof buf, f);
    fclose(f);
    r = rx_search(buf, n, 0, caps);
    if (r == 1) {
        printf("M");
        for (k = 0; k < RX_NCAPS; k++)
            printf(" %td %td", caps[k][0], caps[k][1]);
        printf("\n");
    } else if (r == 0) {
        printf("N\n");
    } else {
        printf("R %d\n", r);
    }
    return 0;
}
