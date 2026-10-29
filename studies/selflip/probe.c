/* probe: time rx_search over one subject file. usage: probe FILE [iters] */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "rx.h"
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 2;
    static unsigned char buf[1 << 21];
    size_t n = fread(buf, 1, sizeof buf, f);
    fclose(f);
    long it = argc > 2 ? atol(argv[2]) : 2000;
    ptrdiff_t caps[16][2];
    int r = 0, all = getenv("FINDALL") != NULL;
    long cnt = 0;
    double best = 1e18;
    for (int t = 0; t < 7; t++) {
        struct timespec a, b;
        clock_gettime(CLOCK_MONOTONIC, &a);
        for (long i = 0; i < it; i++) {
            if (!all) { r = rx_search(buf, n, 0, caps); continue; }
            size_t pos = 0; cnt = 0;
            while (pos <= n && (r = rx_search(buf, n, pos, caps)) == 1) {
                cnt++; pos = (size_t)caps[0][1] + (caps[0][1] == caps[0][0]);
            }
        }
        clock_gettime(CLOCK_MONOTONIC, &b);
        double ns = ((b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec)) / it;
        if (ns < best) best = ns;
    }
    printf("%.1f ns/call  rc=%d span=%td,%td n=%zu%s\n", best, r, caps[0][0], caps[0][1], n, "");
    if (all) printf("   findall matches=%ld\n", cnt);
    return 0;
}
