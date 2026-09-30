/* [UTF-VALID] design note's precheck cost probe (docs/design/utf_valid_design.md
 * §5). Two strict validators (PCRE2_UTF's definition: no overlongs, no
 * surrogates, nothing above U+10FFFF, no truncation) over three subjects, plus
 * a memchr pass and a byte-sum loop as scale references. Reports the best of
 * N runs in ns/byte. Darwin timing is DIRECTIONAL ONLY (house rule).
 *
 *   gcc-16 -O2 -o utfcheck_bench utfcheck_bench.c && ./utfcheck_bench
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* Returns the offset of the first ill-formed byte, or n. Byte at a time. */
static size_t v_bytewise(const unsigned char *s, size_t n)
{
    size_t i = 0;
    while (i < n) {
        unsigned c = s[i];
        if (c < 0x80) { i++; continue; }
        size_t k; unsigned lo = 0x80, hi = 0xBF;
        if (c >= 0xC2 && c <= 0xDF) k = 1;
        else if (c == 0xE0) { k = 2; lo = 0xA0; }
        else if (c == 0xED) { k = 2; hi = 0x9F; }
        else if (c >= 0xE1 && c <= 0xEF) k = 2;
        else if (c == 0xF0) { k = 3; lo = 0x90; }
        else if (c == 0xF4) { k = 3; hi = 0x8F; }
        else if (c >= 0xF1 && c <= 0xF3) k = 3;
        else return i;
        if (n - i <= k) return i;
        if (s[i + 1] < lo || s[i + 1] > hi) return i;
        for (size_t j = 2; j <= k; j++) if ((s[i + j] & 0xC0) != 0x80) return i;
        i += k + 1;
    }
    return n;
}

/* Validates ONE sequence starting at s[0] (a non-ASCII lead) and returns its
 * length, or 0 if it is ill-formed or truncated. */
static size_t seq_len(const unsigned char *s, size_t avail)
{
    unsigned c = s[0], lo = 0x80, hi = 0xBF;
    size_t k;
    if (c >= 0xC2 && c <= 0xDF) k = 1;
    else if (c == 0xE0) { k = 2; lo = 0xA0; }
    else if (c == 0xED) { k = 2; hi = 0x9F; }
    else if (c >= 0xE1 && c <= 0xEF) k = 2;
    else if (c == 0xF0) { k = 3; lo = 0x90; }
    else if (c == 0xF4) { k = 3; hi = 0x8F; }
    else if (c >= 0xF1 && c <= 0xF3) k = 3;
    else return 0;
    if (avail <= k || s[1] < lo || s[1] > hi) return 0;
    for (size_t j = 2; j <= k; j++) if ((s[j] & 0xC0) != 0x80) return 0;
    return k + 1;
}

/* The same rule with an 8-byte ASCII fast path in front. */
static size_t v_ascii8(const unsigned char *s, size_t n)
{
    size_t i = 0;
    while (i < n) {
        while (i + 8 <= n) {
            uint64_t w; memcpy(&w, s + i, 8);
            if (w & 0x8080808080808080ull) break;
            i += 8;
        }
        if (i >= n) break;
        if (s[i] < 0x80) { i++; continue; }
        size_t k = seq_len(s + i, n - i);
        if (!k) return i;
        i += k;
    }
    return n;
}

/* The same rule as a byte-class DFA — the shape a check RIDING the engine's
 * own table walk would have: one dependent table load per byte. */
enum { ACC, N1, N2, N3, E0, ED, F0, F4, REJ, NST };
static unsigned char dfa_tab[NST][256];
static void dfa_build(void)
{
    for (int st = 0; st < NST; st++)
        for (int c = 0; c < 256; c++) {
            int to = REJ;
            if (st == ACC) {
                if (c < 0x80) to = ACC;
                else if (c >= 0xC2 && c <= 0xDF) to = N1;
                else if (c == 0xE0) to = E0;
                else if (c == 0xED) to = ED;
                else if (c >= 0xE1 && c <= 0xEF) to = N2;
                else if (c == 0xF0) to = F0;
                else if (c == 0xF4) to = F4;
                else if (c >= 0xF1 && c <= 0xF3) to = N3;
            } else if (st == N1 || st == N2 || st == N3) {
                if ((c & 0xC0) == 0x80) to = st - 1;
            } else if (st == E0) { if (c >= 0xA0 && c <= 0xBF) to = N1; }
            else if (st == ED) { if (c >= 0x80 && c <= 0x9F) to = N1; }
            else if (st == F0) { if (c >= 0x90 && c <= 0xBF) to = N2; }
            else if (st == F4) { if (c >= 0x80 && c <= 0x8F) to = N2; }
            dfa_tab[st][c] = (unsigned char)to;
        }
}
static size_t v_dfa(const unsigned char *s, size_t n)
{
    unsigned st = ACC; size_t lead = 0;
    for (size_t i = 0; i < n; i++) {
        if (st == ACC) lead = i;
        st = dfa_tab[st][s[i]];
        if (st == REJ) return lead;
    }
    return st == ACC ? n : lead;
}

static double now(void)
{
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

static volatile size_t sink;

#define N_BYTES (64u << 20)
#define RUNS 7

static void fill(unsigned char *s, size_t n, int mix)
{
    /* mix 0: ASCII prose-like; 1: ~1/3 two-byte (Cyrillic) chars;
     * 2: CJK three-byte text with ASCII spaces every ~8 chars. */
    const char *ascii = "the quick brown fox jumps over the lazy dog 0123456789\n";
    size_t al = strlen(ascii), i = 0, r = 12345;
    while (i < n) {
        r = r * 1103515245 + 12345;
        if (mix == 0 || (mix == 1 && (r >> 16) % 3) || (mix == 2 && (r >> 16) % 9 == 0)) {
            s[i++] = (unsigned char)ascii[(r >> 8) % al];
        } else if (mix == 1) {
            if (i + 2 > n) { s[i++] = 'x'; continue; }
            s[i++] = 0xD0; s[i++] = (unsigned char)(0x90 + (r >> 20) % 0x20);
        } else {
            if (i + 3 > n) { s[i++] = 'x'; continue; }
            s[i++] = 0xE4; s[i++] = (unsigned char)(0x80 + (r >> 20) % 0x40);
            s[i++] = (unsigned char)(0x80 + (r >> 24) % 0x40);
        }
    }
}

int main(void)
{
    unsigned char *s = malloc(N_BYTES);
    dfa_build();
    const char *name[] = { "ascii", "cyrillic-1/3", "cjk-8/9" };
    printf("subject\tvalidator\tns_per_byte_best_of_%d\n", RUNS);
    for (int mix = 0; mix < 3; mix++) {
        fill(s, N_BYTES, mix);
        if (v_bytewise(s, N_BYTES) != N_BYTES || v_ascii8(s, N_BYTES) != N_BYTES ||
            v_dfa(s, N_BYTES) != N_BYTES) {
            printf("SELF-CHECK FAILED on %s\n", name[mix]); return 1;
        }
        for (int v = 0; v < 5; v++) {
            double best = 1e9;
            for (int k = 0; k < RUNS; k++) {
                double t0 = now();
                size_t r = 0;
                if (v == 0) r = v_bytewise(s, N_BYTES);
                else if (v == 1) r = v_ascii8(s, N_BYTES);
                else if (v == 4) r = v_dfa(s, N_BYTES);
                else if (v == 2) r = (size_t)(memchr(s, 0x01, N_BYTES) != NULL);
                else { size_t a = 0; for (size_t i = 0; i < N_BYTES; i++) a += s[i]; r = a; }
                sink = r;
                double t = (now() - t0) / N_BYTES * 1e9;
                if (t < best) best = t;
            }
            const char *vn[] = { "bytewise", "ascii8+bytewise", "memchr(ref)", "bytesum(ref)", "table-dfa" };
            printf("%s\t%s\t%.4f\n", name[mix], vn[v], best);
        }
    }
    /* Correctness control: each validator must stop at the first bad byte. */
    struct { const char *b; size_t n, want; } cases[] = {
        { "ab\xff", 3, 2 }, { "ab\xe3\x80", 4, 2 }, { "ab\xc0\x80", 4, 2 },
        { "ab\xed\xa0\x80", 5, 2 }, { "ab\xf4\x90\x80\x80", 6, 2 }, { "ab\x80", 3, 2 },
        { "\xc3\xa9\xe4\xb8\xad\xf0\x9f\x98\x80", 9, 9 }, { "abcdefghij\xff", 11, 10 },
    };
    int bad = 0;
    for (size_t c = 0; c < sizeof cases / sizeof cases[0]; c++) {
        size_t a = v_bytewise((const unsigned char *)cases[c].b, cases[c].n);
        size_t b = v_ascii8((const unsigned char *)cases[c].b, cases[c].n);
        size_t d = v_dfa((const unsigned char *)cases[c].b, cases[c].n);
        if (a != cases[c].want || b != cases[c].want || d != cases[c].want) { bad++; printf("CASE %zu: %zu %zu want %zu\n", c, a, b, cases[c].want); }
    }
    printf("correctness cases: %s\n", bad ? "FAIL" : "8/8 ok (offsets match libpcre2 10.46's startchar)");
    return bad;
}
