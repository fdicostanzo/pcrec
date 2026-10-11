/* lossreview lrvm: the bench find-all loop (match_api.md §3.1, byte advance),
 * once per subject file argument; prints calls/matches per subject. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "rx.h"
int main(int argc, char **argv)
{
    for (int a = 1; a < argc; a++) {
        FILE *f = fopen(argv[a], "rb"); if (!f) return 2;
        fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
        unsigned char *b = malloc(n + 1); if (fread(b, 1, n, f) != (size_t)n) return 2; fclose(f);
        ptrdiff_t caps[RX_NCAPS][2]; long calls = 0, cnt = 0; unsigned long long ck = 0;
        size_t pos = 0;
        for (;;) {
            int rc = rx_search(b, n, pos, caps); calls++;
            if (rc != 1) { if (rc < 0) printf("GIVEUP rc=%d\n", rc); break; }
            cnt++;
            size_t st = caps[0][0], en = caps[0][1];
            ck = ck * 1000003u + st * 31u + en;
            pos = en > st ? en : st + 1;
            if (pos > (size_t)n) break;
        }
        printf("%s\t%ld\tcalls=%ld\tmatches=%ld\tck=%016llx\n", argv[a], n, calls, cnt, ck);
        free(b);
    }
    return 0;
}
