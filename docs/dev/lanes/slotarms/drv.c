/* slotarms driver: the kit harness's vdrv.c (= slot25c's drv.c) without the KEEP
 * branch, plus a `check` mode (no clock). Interface: drv SUBJECT_FILE [first|all] [check].
 * Timed: one line "matches=N hash=H ns/pass=X" (X = median of 7 rounds, each calibrated to >= 50 ms).
 * check: "matches=N hash=H first=S:E" (first = the span of the match from offset 0, or -1:-1). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
extern size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);
static uint64_t now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000000000ull+t.tv_nsec;}
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return x<y?-1:x>y;}
static ptrdiff_t cp[64][2];
/* one pass: `first` = one call from 0; `all` = match_api.md §3.1.3's find-all loop */
static long pass(const unsigned char *b, size_t n, int all, unsigned long *h)
{
    if (!all) { int r = rx_search(b, n, 0, cp); *h ^= r == 1 ? (unsigned long)cp[0][0] * 31u + cp[0][1] : 7u; return r == 1; }
    size_t p = 0; long k = 0;
    while (p <= n && rx_search(b, n, p, cp) == 1) {
        k++; *h = *h * 131u + (unsigned long)cp[0][0] * 31u + (unsigned long)cp[0][1];
        p = cp[0][1] > cp[0][0] ? rx_next_pos(b, n, (size_t)cp[0][1] - 1) : rx_next_pos(b, n, (size_t)cp[0][1]);
        if (cp[0][1] == cp[0][0] && (size_t)cp[0][1] >= n) break;
    }
    return k;
}
int main(int c, char **v)
{
    FILE *f = fopen(v[1], "rb"); int all = c > 2 && !strcmp(v[2], "all");
    if (!f) return 2;
    fseek(f, 0, 2); long n = ftell(f); fseek(f, 0, 0); unsigned char *b = malloc(n + 1);
    if (fread(b, 1, n, f) != (size_t)n) return 2;
    unsigned long h = 0; long m = pass(b, n, all, &h), it = 1; uint64_t t0;
    if (c > 3 && !strcmp(v[3], "check")) {
        ptrdiff_t s = -1, e = -1; if (rx_search(b, n, 0, cp) == 1) { s = cp[0][0]; e = cp[0][1]; }
        printf("matches=%ld hash=%lx first=%td:%td\n", m, h, s, e); return 0;
    }
    do { it *= 2; t0 = now(); unsigned long g = 0; for (long i = 0; i < it; i++) pass(b, n, all, &g); } while (now() - t0 < 50000000);
    double t[7];
    for (int k = 0; k < 7; k++) { unsigned long g = 0; t0 = now(); for (long i = 0; i < it; i++) pass(b, n, all, &g); t[k] = (double)(now() - t0) / it; }
    qsort(t, 7, sizeof t[0], cmp);
    printf("matches=%ld hash=%lx ns/pass=%.2f\n", m, h, t[3]);
    return 0;
}
