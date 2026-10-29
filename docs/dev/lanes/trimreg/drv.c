/* trimreg driver: ./drv SUBJECT ITERS ; includes artifact via -DART. */
#include ART
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb"); static unsigned char buf[1<<21];
    size_t n = fread(buf, 1, sizeof buf, f); fclose(f);
    long it = atol(argv[2]);
    ptrdiff_t caps[4][2]; int r = 0;
    struct timespec a, b;
    for (int rep = 0; rep < 5; rep++) {
        clock_gettime(CLOCK_MONOTONIC, &a);
        for (long i = 0; i < it; i++) r = rx_search(buf, n, 0, caps);
        clock_gettime(CLOCK_MONOTONIC, &b);
        printf("r=%d [%td,%td) %.1f ns/call\n", r, caps[0][0], caps[0][1],
               ((b.tv_sec-a.tv_sec)*1e9 + (b.tv_nsec-a.tv_nsec)) / it);
    }
    return 0;
}
