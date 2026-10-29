/* gdrv SUBJ : the throughput regime -- every non-overlapping match of the
 * pattern over the whole subject (search from pos, resume at the match end,
 * +1 after an empty match), repeated $REPS times (default 1). Prints the
 * match count, a span checksum and the last rc. Default arm (rx_search). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include HDR
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb"); if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END); size_t n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc(n + 1); if (fread(s, 1, n, f) != n) return 2; fclose(f);
    int reps = getenv("REPS") ? atoi(getenv("REPS")) : 1;
    ptrdiff_t caps[PFX_NCAPS][2];
    unsigned long long cnt = 0, sum = 0; int rc = 0, bad = 0;
    for (int r = 0; r < reps; r++) {
        size_t pos = 0; cnt = 0; sum = 0;
        while (pos <= n) {
            rc = PFX_search(s, n, pos, caps);
            if (rc <= 0) { if (rc < 0 && rc != -1) bad = rc; break; }
            cnt++;
            for (int g = 0; g < PFX_NCAPS; g++) sum = sum * 1000003u + (unsigned long long)(caps[g][0] + 7) * 31u + (unsigned long long)(caps[g][1] + 3);
            pos = caps[0][1] > caps[0][0] ? (size_t)caps[0][1] : (size_t)caps[0][1] + 1;
        }
        __asm__ volatile("" ::: "memory");
    }
    printf("matches=%llu sum=%llx lastrc=%d err=%d n=%zu\n", cnt, sum, rc, bad, n);
    return 0;
}
