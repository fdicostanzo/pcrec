#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>
long long g_steps;
#include ARTIFACT
int main(int argc, char **argv) {
    for (int i = 1; i < argc; i++) {
        FILE *f = fopen(argv[i], "rb"); static unsigned char buf[1<<22];
        size_t n = fread(buf, 1, sizeof buf, f); fclose(f);
        ptrdiff_t caps[RX_NCAPS > 0 ? RX_NCAPS : 1][2];
        struct timespec a, b; clock_gettime(CLOCK_MONOTONIC, &a);
        int rc = rx_search(buf, n, 0, caps);
        clock_gettime(CLOCK_MONOTONIC, &b);
        double s = (b.tv_sec - a.tv_sec) + (b.tv_nsec - a.tv_nsec) / 1e9;
        const char *nm = strrchr(argv[i], '/'); nm = nm ? nm + 1 : argv[i];
        printf("%-28s len=%-6zu rc=%-3d steps=%-11lld %.6fs\n", nm, n, rc, g_steps, s);
    }
    return 0;
}
