/* [LOSS-REVIEW] lrdfa: COUNTED find-all work, no clock. Links one pcrec
 * artifact (prefix rx) and wraps memchr/memcmp/memrchr with -Wl,--wrap to
 * count calls and bytes each examines (by its semantics: up to and incl. the
 * hit). Per subject prints: bytes, rx_search calls, matches, memchr calls,
 * memchr bytes, memcmp calls, span checksum. Find-all = the bench protocol
 * (resume at end; after an empty match at end+1; walk_survey fatime.c).
 * Build: gcc -O2 -fno-builtin -I. facount.c ART.c -Wl,--wrap=memchr
 *        -Wl,--wrap=memcmp -Wl,--wrap=memrchr -o fc                    */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include RXH
static unsigned long long mc_calls, mc_bytes, mcmp_calls, mcmp_bytes, mr_calls, mr_bytes;
void *__real_memchr(const void *, int, size_t);
void *__real_memrchr(const void *, int, size_t);
int __real_memcmp(const void *, const void *, size_t);
void *__wrap_memchr(const void *s, int c, size_t n)
{
    void *r = __real_memchr(s, c, n);
    mc_calls++; mc_bytes += r ? (size_t)((const char *)r - (const char *)s) + 1 : n;
    return r;
}
void *__wrap_memrchr(const void *s, int c, size_t n)
{
    void *r = __real_memrchr(s, c, n);
    mr_calls++; mr_bytes += r ? n - (size_t)((const char *)r - (const char *)s) : n;
    return r;
}
int __wrap_memcmp(const void *a, const void *b, size_t n)
{ mcmp_calls++; mcmp_bytes += n; return __real_memcmp(a, b, n); }
int main(int argc, char **argv)
{
    int fa = !strcmp(argv[1], "findall");
    printf("subject\tbytes\tcalls\tmatches\tmemchr_calls\tmemchr_bytes\tmemrchr_calls\tmemcmp_calls\tck\n");
    for (int i = 2; i < argc; i++) {
        FILE *f = fopen(argv[i], "rb"); fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
        unsigned char *b = malloc(n + 1); if (fread(b, 1, n, f) != (size_t)n) return 2; fclose(f);
        ptrdiff_t caps[64][2]; unsigned long long ck = 0; long cnt = 0, calls = 0;
        mc_calls = mc_bytes = mcmp_calls = mcmp_bytes = mr_calls = mr_bytes = 0;
        size_t pos = 0;
        for (;;) {
            int rc = rx_search(b, n, pos, caps); calls++;
            if (rc != 1) break;
            cnt++;
            size_t st = caps[0][0], en = caps[0][1];
            ck = ck * 1000003u + st * 31u + en;
            if (!fa) break;
            pos = en > st ? en : st + 1;
            if (pos > (size_t)n) break;
        }
        const char *base = strrchr(argv[i], '/');
        printf("%s\t%ld\t%ld\t%ld\t%llu\t%llu\t%llu\t%llu\t%016llx\n", base ? base + 1 : argv[i], n, calls, cnt,
               mc_calls, mc_bytes, mr_calls, mcmp_calls, ck);
        free(b);
    }
    return 0;
}
