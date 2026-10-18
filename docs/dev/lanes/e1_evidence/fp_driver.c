/* lane e1 scratch: every subject over a small alphabet up to length 5, every
 * start, rx_search's return and span printed. */
#include <stdio.h>
#include <stddef.h>
#include <string.h>
#include "x.h"
int main(void) {
    const char al[] = "abcdz _";
    unsigned char s[8]; unsigned long h = 1469598103934665603UL, calls = 0;
    for (int len = 0; len <= 5; len++) {
        int idx[8] = {0}; long total = 1; for (int i = 0; i < len; i++) total *= 7;
        for (long t = 0; t < total; t++) {
            long v = t; for (int i = 0; i < len; i++) { s[i] = (unsigned char)al[v % 7]; v /= 7; }
            for (int sf = 0; sf <= len; sf++) {
                ptrdiff_t caps[16][2]; memset(caps, 0, sizeof caps);
                int r = rx_search(s, (size_t)len, (size_t)sf, caps);
                long out[3] = { r, r > 0 ? (long)caps[0][0] : -9, r > 0 ? (long)caps[0][1] : -9 };
                for (int k = 0; k < 3; k++) { h ^= (unsigned long)out[k] + 0x9e37; h *= 1099511628211UL; }
                calls++;
            }
        }
        (void)idx;
    }
    printf("calls=%lu hash=%016lx\n", calls, h);
    return 0;
}
