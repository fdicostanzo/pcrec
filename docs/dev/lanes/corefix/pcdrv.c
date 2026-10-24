#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "art.h"
int main(int argc, char **argv)
{
    for (int i = 1; i < argc; i++) {
        const unsigned char *s = (const unsigned char *)argv[i]; size_t n = strlen(argv[i]);
        printf("'%s':", argv[i]);
        for (size_t sp = 0; sp <= n; sp++) {
            ptrdiff_t c[RX_NCAPS][2];
            int r = rx_search(s, n, sp, c);
            printf(" [%zu:%s", sp, r == 1 ? "" : r == 0 ? "-" : "ERR");
            if (r == 1) for (int g = 0; g < RX_NCAPS; g++)
                printf("%s%td,%td", g ? " " : "", c[g][0], c[g][1]);
            printf("]");
        }
        printf("\n");
    }
    return 0;
}
