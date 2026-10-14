/* r17loss: one pass of alpha_r17b.sh's drv.c `pass`, printing the site's counters (no timing). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
extern size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);
extern unsigned long long r17l_masks, r17l_uses, r17l_skip, r17l_zero, r17l_cold, r17l_cached, r17l_skip_cold;
static ptrdiff_t cp[64][2];
int main(int c, char **v)
{
    FILE *f = fopen(v[1], "rb"); int all = c > 2 && !strcmp(v[2], "all");
    fseek(f, 0, 2); long n = ftell(f); fseek(f, 0, 0); unsigned char *b = malloc(n + 1);
    if (fread(b, 1, n, f) != (size_t)n) return 2;
    long calls = 0, k = 0;
    if (!all) { calls = 1; k = rx_search(b, n, 0, cp) == 1; }
    else {
        size_t p = 0;
        while (p <= (size_t)n) {
            calls++;
            if (rx_search(b, n, p, cp) != 1) break;
            k++;
            p = cp[0][1] > cp[0][0] ? rx_next_pos(b, n, (size_t)cp[0][1] - 1) : rx_next_pos(b, n, (size_t)cp[0][1]);
            if (cp[0][1] == cp[0][0] && (size_t)cp[0][1] >= (size_t)n) break;
        }
    }
    printf("n=%ld calls=%ld matches=%ld uses=%llu cold=%llu zero=%llu cached=%llu skip=%llu skip_cold=%llu masks=%llu\n",
           n, calls, k, r17l_uses, r17l_cold, r17l_zero, r17l_cached, r17l_skip, r17l_skip_cold, r17l_masks);
    return 0;
}
