/* [MATCH-SPLIT] STEP-0 (d): the counted-work driver -- a WORK COUNT, not a timing, no clock.
 *
 * The artifact (prefix rx) is compiled -O0 with
 *   -fsanitize=kernel-address --param asan-instrumentation-with-call-threshold=0
 *   --param asan-stack=0 --param asan-globals=0
 * so every load becomes a call to __asan_loadK_noabort; this file (compiled WITHOUT
 * instrumentation) defines those hooks and counts the loads that land inside the subject
 * buffer.  It is studies/walk_survey/wsdrv.c's mechanism reduced to ONE number: the total
 * subject-byte loads T of a whole find-all, plus calls, matches and (when the survey's
 * text transform put it in the artifact) `rx_ms_attempts`, the number of attempt-loop
 * entries.  memchr/memrchr/memcmp are interposed and count the bytes their semantics
 * examine (the artifact is built -fno-builtin-<fn>).
 *
 *   qdrv PREFIX_HEX RUNBYTE_HEX K SUFFIX_HEX     subject = prefix . run*K . suffix
 * prints: n calls matches T attempts                                                  */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include "rx.h"
#undef memchr
#undef memrchr
#undef memcmp

static const unsigned char *lo, *hi;
static unsigned long long T;
extern unsigned long long rx_ms_attempts __attribute__((weak));

static void touch(const unsigned char *p, size_t sz)
{
    if (p + sz <= lo || p >= hi || sz == 0) return;
    const unsigned char *a = p < lo ? lo : p, *b = p + sz > hi ? hi : p + sz;
    T += (unsigned long long)(b - a);
}
#define H(sz) void __asan_load##sz##_noabort(uintptr_t a) { touch((const unsigned char *)a, sz); } \
    void __asan_store##sz##_noabort(uintptr_t a) { (void)a; }
H(1) H(2) H(4) H(8) H(16)
void __asan_loadN_noabort(uintptr_t a, size_t s) { touch((const unsigned char *)a, s); }
void __asan_storeN_noabort(uintptr_t a, size_t s) { (void)a; (void)s; }
void __asan_handle_no_return(void) {}

void *memchr(const void *s, int c, size_t n)
{
    const unsigned char *p = s;
    for (size_t i = 0; i < n; i++) { touch(p + i, 1); if (p[i] == (unsigned char)c) return (void *)(p + i); }
    return NULL;
}
void *memrchr(const void *s, int c, size_t n)
{
    const unsigned char *p = s;
    for (size_t i = n; i-- > 0;) { touch(p + i, 1); if (p[i] == (unsigned char)c) return (void *)(p + i); }
    return NULL;
}
int memcmp(const void *a, const void *b, size_t n)
{
    const unsigned char *p = a, *q = b;
    for (size_t i = 0; i < n; i++) { touch(p + i, 1); touch(q + i, 1); if (p[i] != q[i]) return p[i] - q[i]; }
    return 0;
}

static size_t unhex(const char *h, unsigned char *out)
{
    size_t n = strlen(h) / 2;
    for (size_t i = 0; i < n; i++) { unsigned v; sscanf(h + 2 * i, "%2x", &v); out[i] = (unsigned char)v; }
    return n;
}

int main(int argc, char **argv)
{
    if (argc != 5) return 2;
    unsigned char pre[4096], run[64], suf[4096];
    size_t np = unhex(argv[1], pre), nr = unhex(argv[2], run), ns = unhex(argv[4], suf);
    long k = atol(argv[3]);
    size_t n = np + nr * (size_t)k + ns;
    unsigned char *subj = malloc(n + 1);
    memcpy(subj, pre, np);
    for (long i = 0; i < k; i++) memcpy(subj + np + (size_t)i * nr, run, nr);
    memcpy(subj + np + nr * (size_t)k, suf, ns);
    lo = subj; hi = subj + n;
    ptrdiff_t spans[RX_NCAPS][2];
    unsigned long long calls = 0, matches = 0;
    size_t pos = 0;
    while (pos <= n) {
        int got = rx_search(subj, n, pos, spans);
        calls++;
        if (got <= 0) break;
        matches++;
        size_t s = (size_t)spans[0][0], e = (size_t)spans[0][1];
        pos = e == s ? e + 1 : e;
        if (calls > 5000000ull) break;
    }
    printf("%zu %llu %llu %llu %lld\n", n, calls, matches, T, &rx_ms_attempts ? (long long)rx_ms_attempts : -1LL);
    return 0;
}
