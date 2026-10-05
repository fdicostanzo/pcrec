/* memfnsurvey: exhaustive + guard-page correctness check of third-party
 * byte-search kernels (requirements.md N-6 shape). Scratch only.
 * Spans: n 0..NMAX, every hit position (and none), an optional second hit,
 * placements: flush against a PROT_NONE page at the END, and at offsets
 * 0..15 just after a PROT_NONE page at the START. A SIGSEGV/SIGBUS is caught
 * and recorded per kernel. NOTE: page guards only catch reads that CROSS a
 * page; an aligned-down over-read inside one page is invisible here. */
#include <setjmp.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#define SZ_DYNAMIC_DISPATCH 0
#include "stringzilla/find.h"

#ifndef PLMAX
#define PLMAX 16
#endif
#ifndef NMAX
#define NMAX 300
#endif

enum { BYTE, RBYTE, SET, RSET, NSET, LIT };
typedef size_t (*fbyte)(const uint8_t *, size_t, uint8_t);
typedef size_t (*fset)(const uint8_t *, size_t, const uint64_t *);
typedef size_t (*flit)(const uint8_t *, size_t, const uint8_t *, size_t);

#define IDX(p, s, n) ((p) ? (size_t)((const uint8_t *)(p) - (s)) : (n))

static size_t w_libc_memchr(const uint8_t *s, size_t n, uint8_t c) { return IDX(memchr(s, c, n), s, n); }
static size_t w_libc_memmem(const uint8_t *s, size_t n, const uint8_t *l, size_t L) { return IDX(memmem(s, n, l, L), s, n); }
#ifdef __aarch64__
void *musl_memchr(const void *, int, size_t);
void *musl_memmem(const void *, size_t, const void *, size_t);
void *__memchr_aarch64(const void *, int, size_t);
void *__memchr_aarch64_mte(const void *, int, size_t);
void *__memrchr_aarch64(const void *, int, size_t);
static size_t w_musl_memchr(const uint8_t *s, size_t n, uint8_t c) { return IDX(musl_memchr(s, c, n), s, n); }
static size_t w_musl_memmem(const uint8_t *s, size_t n, const uint8_t *l, size_t L) { return IDX(musl_memmem(s, n, l, L), s, n); }
static size_t w_or_memchr(const uint8_t *s, size_t n, uint8_t c) { return IDX(__memchr_aarch64(s, c, n), s, n); }
static size_t w_or_memchr_mte(const uint8_t *s, size_t n, uint8_t c) { return IDX(__memchr_aarch64_mte(s, c, n), s, n); }
static size_t w_or_memrchr(const uint8_t *s, size_t n, uint8_t c) { return IDX(__memrchr_aarch64(s, c, n), s, n); }
#endif

#define SZB(name)                                                                                     \
    static size_t w_##name(const uint8_t *s, size_t n, uint8_t c) {                                    \
        return IDX(name((sz_cptr_t)s, n, (sz_cptr_t)&c), s, n);                                       \
    }
#define SZS(name)                                                                                     \
    static size_t w_##name(const uint8_t *s, size_t n, const uint64_t *set) {                          \
        sz_byteset_t b;                                                                               \
        memcpy(&b, set, 32);                                                                          \
        return IDX(name((sz_cptr_t)s, n, &b), s, n);                                                  \
    }
#define SZN(name) /* skip_in_set through the inverted set, as sz_find_byte_not_from does */            \
    static size_t w_not_##name(const uint8_t *s, size_t n, const uint64_t *set) {                      \
        sz_byteset_t b;                                                                               \
        memcpy(&b, set, 32);                                                                          \
        sz_byteset_invert(&b);                                                                        \
        return IDX(name((sz_cptr_t)s, n, &b), s, n);                                                  \
    }
#define SZL(name)                                                                                     \
    static size_t w_##name(const uint8_t *s, size_t n, const uint8_t *l, size_t L) {                   \
        return IDX(name((sz_cptr_t)s, n, (sz_cptr_t)l, L), s, n);                                     \
    }
SZB(sz_find_byte_serial) SZB(sz_rfind_byte_serial) SZS(sz_find_byteset_serial) SZS(sz_rfind_byteset_serial)
SZN(sz_find_byteset_serial) SZL(sz_find_serial)
#if SZ_USE_NEON
SZB(sz_find_byte_neon) SZB(sz_rfind_byte_neon) SZS(sz_find_byteset_neon) SZS(sz_rfind_byteset_neon)
SZN(sz_find_byteset_neon) SZL(sz_find_neon)
#endif
#if SZ_USE_WESTMERE
SZB(sz_find_byte_westmere) SZB(sz_rfind_byte_westmere) SZL(sz_find_westmere)
#endif
#if SZ_USE_HASWELL
SZB(sz_find_byte_haswell) SZB(sz_rfind_byte_haswell) SZS(sz_find_byteset_haswell)
SZS(sz_rfind_byteset_haswell) SZN(sz_find_byteset_haswell) SZL(sz_find_haswell)
#endif

struct K { const char *name; int kind; void *f; };
static const struct K ks[] = {
    {"libc memchr", BYTE, (void *)w_libc_memchr},
    {"libc memmem", LIT, (void *)w_libc_memmem},
#ifdef __aarch64__
    {"musl memchr", BYTE, (void *)w_musl_memchr},
    {"musl memmem", LIT, (void *)w_musl_memmem},
    {"arm-or memchr", BYTE, (void *)w_or_memchr},
    {"arm-or memchr-mte", BYTE, (void *)w_or_memchr_mte},
    {"arm-or memrchr", RBYTE, (void *)w_or_memrchr},
#endif
    {"sz find_byte serial", BYTE, (void *)w_sz_find_byte_serial},
    {"sz rfind_byte serial", RBYTE, (void *)w_sz_rfind_byte_serial},
    {"sz find_byteset serial", SET, (void *)w_sz_find_byteset_serial},
    {"sz rfind_byteset serial", RSET, (void *)w_sz_rfind_byteset_serial},
    {"sz not_from serial", NSET, (void *)w_not_sz_find_byteset_serial},
    {"sz find serial", LIT, (void *)w_sz_find_serial},
#if SZ_USE_NEON
    {"sz find_byte neon", BYTE, (void *)w_sz_find_byte_neon},
    {"sz rfind_byte neon", RBYTE, (void *)w_sz_rfind_byte_neon},
    {"sz find_byteset neon", SET, (void *)w_sz_find_byteset_neon},
    {"sz rfind_byteset neon", RSET, (void *)w_sz_rfind_byteset_neon},
    {"sz not_from neon", NSET, (void *)w_not_sz_find_byteset_neon},
    {"sz find neon", LIT, (void *)w_sz_find_neon},
#endif
#if SZ_USE_WESTMERE
    {"sz find_byte westmere", BYTE, (void *)w_sz_find_byte_westmere},
    {"sz rfind_byte westmere", RBYTE, (void *)w_sz_rfind_byte_westmere},
    {"sz find westmere", LIT, (void *)w_sz_find_westmere},
#endif
#if SZ_USE_HASWELL
    {"sz find_byte haswell", BYTE, (void *)w_sz_find_byte_haswell},
    {"sz rfind_byte haswell", RBYTE, (void *)w_sz_rfind_byte_haswell},
    {"sz find_byteset haswell", SET, (void *)w_sz_find_byteset_haswell},
    {"sz rfind_byteset haswell", RSET, (void *)w_sz_rfind_byteset_haswell},
    {"sz not_from haswell", NSET, (void *)w_not_sz_find_byteset_haswell},
    {"sz find haswell", LIT, (void *)w_sz_find_haswell},
#endif
};

static sigjmp_buf jb;
static void onsig(int sig) { siglongjmp(jb, sig); }

static uint64_t rs = 88172645463325252ull;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static int inset(const uint64_t *st, uint8_t c) { return (st[c >> 6] >> (c & 63)) & 1; }

/* the set shapes: the classes pcrec scans for, plus edge sets */
static void mkset(int k, uint64_t *st) {
    memset(st, 0, 32);
#define ADD(c) (st[(uint8_t)(c) >> 6] |= 1ull << ((uint8_t)(c) & 63))
    switch (k) {
    case 0: ADD('x'); break;
    case 1: ADD('u'); ADD('U'); break;
    case 2: ADD('\r'); ADD('\n'); ADD('\t'); break;
    case 3: for (int c = '0'; c <= '9'; c++) ADD(c); break;
    case 4: for (int c = 'a'; c <= 'z'; c++) { ADD(c); ADD(c - 32); } break;
    case 5: for (int c = 0x80; c <= 0xff; c++) ADD(c); break;
    case 6: for (int c = 0; c < 256; c++) if (rnd() & 1) ADD(c); break;
    case 7: ADD(0); ADD(0xff); ADD(0x7f); ADD(0x80); break;
    case 8: for (int c = 0; c < 256; c++) ADD(c); st[0] &= ~1ull; break; /* all but NUL */
    }
}
#define NSETS 9

int main(void) {
    long pg = sysconf(_SC_PAGESIZE);
    size_t data = (size_t)pg * ((NMAX + 64 + pg - 1) / pg + 1);
    uint8_t *base = mmap(0, data + 2 * pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    if (base == MAP_FAILED) return 2;
    mprotect(base, pg, PROT_NONE);
    mprotect(base + pg + data, pg, PROT_NONE);
    uint8_t *lo = base + pg, *hi = base + pg + data;
    signal(SIGSEGV, onsig);
    signal(SIGBUS, onsig);
    int allbad = 0;
    for (size_t ki = 0; ki < sizeof ks / sizeof ks[0]; ki++) {
        const struct K *k = &ks[ki];
        long cases = 0, bad = 0;
        volatile int crashed = 0;
        int sig;
        char firstbad[160] = "";
        if ((sig = sigsetjmp(jb, 1)) != 0) {
            crashed = sig;
            goto done;
        }
        for (size_t n = 0; n <= NMAX; n++) {
            for (int pl = -1; pl < PLMAX; pl++) {
                uint8_t *s = pl < 0 ? hi - n : lo + pl;
                if (k->kind == LIT) {
                    for (size_t L = 1; L <= 20; L++)
                        for (int t = 0; t < 4; t++) {
                            uint8_t nd[20];
                            for (size_t i = 0; i < L; i++) nd[i] = "abc"[rnd() % 3];
                            for (size_t i = 0; i < n; i++) s[i] = "abc"[rnd() % 3];
                            if (n >= L && (t & 1)) memcpy(s + rnd() % (n - L + 1), nd, L);
                            size_t ref = n;
                            for (size_t i = 0; i + L <= n; i++)
                                if (!memcmp(s + i, nd, L)) { ref = i; break; }
#ifdef EXACT
                            uint8_t *x = malloc(n ? n : 1); memcpy(x, s, n);
                            size_t got = ((flit)k->f)(x, n, nd, L); free(x);
#else
                            size_t got = ((flit)k->f)(s, n, nd, L);
#endif
                            cases++;
                            if (got != ref && !bad++)
                                snprintf(firstbad, sizeof firstbad, "n=%zu L=%zu pl=%d got=%zu ref=%zu", n, L, pl, got, ref);
                        }
                    continue;
                }
                for (int sk = 0; sk < ((k->kind == BYTE || k->kind == RBYTE) ? 3 : NSETS); sk++) {
                    uint64_t st[4];
                    uint8_t c = 0;
                    if (k->kind == BYTE || k->kind == RBYTE) {
                        c = sk == 0 ? 'x' : sk == 1 ? 0 : 0xff;
                        memset(st, 0, 32);
                        st[c >> 6] |= 1ull << (c & 63);
                    } else
                        mkset(sk, st);
                    int want_in = k->kind != NSET; /* a "hit" is a member, except for skip */
                    uint8_t hitb[256], fillb[256];
                    int nh = 0, nf = 0;
                    for (int b = 0; b < 256; b++) {
                        if (inset(st, (uint8_t)b) == want_in) hitb[nh++] = (uint8_t)b;
                        else fillb[nf++] = (uint8_t)b;
                    }
                    if (!nf) continue;
                    for (long pos = -1; pos < (long)n; pos++) {
                        for (size_t i = 0; i < n; i++) s[i] = fillb[rnd() % nf];
                        if (pos >= 0 && nh) {
                            s[pos] = hitb[rnd() % nh];
                            /* a second hit beyond the first (forward) or before it (reverse) */
                            int rev = k->kind == RBYTE || k->kind == RSET;
                            if (rnd() & 1) {
                                if (!rev && pos + 1 < (long)n) s[pos + 1 + rnd() % (n - pos - 1)] = hitb[rnd() % nh];
                                if (rev && pos > 0) s[rnd() % pos] = hitb[rnd() % nh];
                            }
                        }
                        size_t ref = n;
                        if (k->kind == RBYTE || k->kind == RSET) {
                            for (size_t i = n; i-- > 0;)
                                if (inset(st, s[i])) { ref = i; break; }
                        } else {
                            for (size_t i = 0; i < n; i++)
                                if (inset(st, s[i]) == want_in) { ref = i; break; }
                        }
#ifdef EXACT
                        uint8_t *x = malloc(n ? n : 1); memcpy(x, s, n);
#else
                        uint8_t *x = s;
#endif
                        size_t got = (k->kind == BYTE || k->kind == RBYTE) ? ((fbyte)k->f)(x, n, c)
                                                                           : ((fset)k->f)(x, n, st);
#ifdef EXACT
                        free(x);
#endif
                        cases++;
                        if (got != ref && !bad++)
                            snprintf(firstbad, sizeof firstbad, "n=%zu pos=%ld pl=%d set=%d got=%zu ref=%zu", n, pos, pl, sk, got, ref);
                    }
                }
            }
        }
    done:
        printf("%-26s cases %9ld  bad %6ld  %s%s\n", k->name, cases, bad,
               crashed ? (crashed == SIGSEGV ? "CRASH SIGSEGV (guard page) " : "CRASH SIGBUS ") : "", firstbad);
        allbad |= bad || crashed;
        signal(SIGSEGV, onsig);
        signal(SIGBUS, onsig);
    }
    return allbad;
}
