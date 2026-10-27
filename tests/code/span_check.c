/* tests/code/span_check.c — the span helpers' unit check ([INLINE-C] stage 2;
 * docs/spec/match_api.md §11.10).
 *
 * Built with `-include` of an emitted artifact header, so the helpers under
 * test are the artifact's own text. Each helper is compared with a reference
 * written HERE from §11.10's table (a direct reading of the contract, not of
 * the emitted code) over an exhaustive population: every span of length 0-3
 * over a 7-byte alphabet chosen to reach every branch (digits, hex letters of
 * both cases, a non-hex letter, a high byte), every needle of length 0-2 over
 * the same alphabet, the unset span, the 64-bit overflow boundary, and every
 * UTF-8 lead/continuation shape of length 1-4. Prints one line per failure
 * and a count; exits nonzero on any failure or an empty population. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static long checks, fails;

#define CHECK(cond, ...) do { checks++; if (!(cond)) { fails++; \
    if (fails < 20) { printf("FAIL: "); printf(__VA_ARGS__); putchar('\n'); } } } while (0)

static const unsigned char alpha[] = { '0', '9', 'a', 'F', 'g', 'G', 0xC3 };
#define NA (sizeof alpha)

/* ---- the references, from §11.10 ---------------------------------------- */
static int ref_eq(const unsigned char *p, ptrdiff_t n, const char *z, int fold)
{
    if (!p || n < 0 || (size_t)n != strlen(z)) return 0;
    for (ptrdiff_t i = 0; i < n; i++) {
        unsigned a = p[i], b = (unsigned char)z[i];
        if (fold) {
            if (a >= 'A' && a <= 'Z') a += 32;
            if (b >= 'A' && b <= 'Z') b += 32;
        }
        if (a != b) return 0;
    }
    return 1;
}

static int ref_num(const unsigned char *p, ptrdiff_t n, unsigned base, uint64_t *out)
{
    if (!p || n <= 0) return 0;
    uint64_t v = 0;
    for (ptrdiff_t i = 0; i < n; i++) {
        unsigned d, c = p[i];
        if (c >= '0' && c <= '9') d = c - '0';
        else if (base == 16 && c >= 'a' && c <= 'f') d = c - 'a' + 10;
        else if (base == 16 && c >= 'A' && c <= 'F') d = c - 'A' + 10;
        else return 0;
        if (v > (UINT64_MAX - d) / base) return 0;
        v = v * base + d;
    }
    *out = v;
    return 1;
}

static ptrdiff_t ref_find(const unsigned char *p, ptrdiff_t n, const char *z)
{
    if (!p || n < 0) return -1;
    size_t m = strlen(z);
    for (ptrdiff_t i = 0; i + (ptrdiff_t)m <= n; i++)
        if (!memcmp(p + i, z, m)) return i;
    return -1;
}

/* UTF-8 by the table of well-formed sequences (Unicode 16.0 Table 3-7). */
static int ref_u8(const unsigned char *p, ptrdiff_t n, ptrdiff_t i, uint32_t *cp)
{
    if (!p || n < 0 || i >= n) return 0;
    unsigned b0 = p[i];
    if (b0 < 0x80) { *cp = b0; return 1; }
    int len; unsigned lo = 0x80, hi = 0xBF; uint32_t v;
    if (b0 >= 0xC2 && b0 <= 0xDF) { len = 2; v = b0 & 0x1F; }
    else if (b0 == 0xE0) { len = 3; lo = 0xA0; v = 0; }
    else if (b0 >= 0xE1 && b0 <= 0xEC) { len = 3; v = b0 & 0x0F; }
    else if (b0 == 0xED) { len = 3; hi = 0x9F; v = 0x0D; }
    else if (b0 >= 0xEE && b0 <= 0xEF) { len = 3; v = b0 & 0x0F; }
    else if (b0 == 0xF0) { len = 4; lo = 0x90; v = 0; }
    else if (b0 >= 0xF1 && b0 <= 0xF3) { len = 4; v = b0 & 0x07; }
    else if (b0 == 0xF4) { len = 4; hi = 0x8F; v = 4; }
    else return -1;
    if (i + len > n) return -1;
    for (int k = 1; k < len; k++) {
        unsigned b = p[i + k];
        unsigned l = k == 1 ? lo : 0x80, h = k == 1 ? hi : 0xBF;
        if (b < l || b > h) return -1;
        v = (v << 6) | (b & 0x3F);
    }
    *cp = v;
    return len;
}

/* ---- one span against every helper -------------------------------------- */
static void one(const unsigned char *p, ptrdiff_t n)
{
    const rx_span s = { p, n };
    static const char *needles[1 + NA + NA * NA];
    static char singles[NA][2], pairs[NA * NA][3];
    static int built;
    if (!built) {
        int k = 0;
        needles[k++] = "";
        for (size_t a = 0; a < NA; a++) {
            singles[a][0] = (char)alpha[a];
            needles[k++] = singles[a];
        }
        for (size_t a = 0; a < NA; a++)
            for (size_t b = 0; b < NA; b++) {
                pairs[a * NA + b][0] = (char)alpha[a];
                pairs[a * NA + b][1] = (char)alpha[b];
                pairs[a * NA + b][2] = 0;
                needles[k++] = pairs[a * NA + b];
            }
        built = 1;
    }
    for (size_t k = 0; k < sizeof needles / sizeof needles[0]; k++) {
        const char *z = needles[k];
        CHECK(rx_eq(s, z) == ref_eq(p, n, z, 0), "rx_eq len %td z '%s'", n, z);
        CHECK(rx_eqi(s, z) == ref_eq(p, n, z, 1), "rx_eqi len %td z '%s'", n, z);
        CHECK(rx_find(s, z) == ref_find(p, n, z), "rx_find len %td z '%s'", n, z);
    }
    uint64_t a = 7, b = 7;
    int ra = rx_u64(s, &a), rb = ref_num(p, n, 10, &b);
    CHECK(ra == rb && a == (rb ? b : 7), "rx_u64 len %td", n);
    a = b = 7;
    ra = rx_hex(s, &a); rb = ref_num(p, n, 16, &b);
    CHECK(ra == rb && a == (rb ? b : 7), "rx_hex len %td", n);
    uint64_t v = 0;
    rb = ref_num(p, n, 10, &v);
    CHECK(rx_in(s, 0, 9) == (rb && v <= 9), "rx_in len %td [0,9]", n);
    CHECK(rx_in(s, 10, 99) == (rb && v >= 10 && v <= 99), "rx_in len %td [10,99]", n);
}

static void u8one(const unsigned char *p, ptrdiff_t n)
{
    const rx_span s = { p, n };
    ptrdiff_t i = 0, ri = 0;
    for (int guard = 0; guard < 8; guard++) {
        uint32_t cp = 0xDEAD, rcp = 0xDEAD;
        const ptrdiff_t before = i;
        int r = rx_u8next(s, &i, &cp);
        int rr = ref_u8(p, n, ri, &rcp);
        if (rr > 0) ri += rr;
        CHECK(r == rr && i == ri && (rr > 0 ? cp == rcp : cp == 0xDEAD),
              "rx_u8next len %td at %td: got %d (i %td cp %X) want %d (cp %X)",
              n, before, r, i, (unsigned)cp, rr, (unsigned)rcp);
        if (r <= 0 || rr <= 0) break;
    }
}

int main(void)
{
    unsigned char b[4] = { 0 };
    /* every span of length 0-3 over the alphabet */
    one(b, 0);
    for (size_t x = 0; x < NA; x++) {
        b[0] = alpha[x]; one(b, 1);
        for (size_t y = 0; y < NA; y++) {
            b[1] = alpha[y]; one(b, 2);
            for (size_t z = 0; z < NA; z++) { b[2] = alpha[z]; one(b, 3); }
        }
    }
    /* the unset span reads as matching nothing */
    const rx_span u = { NULL, -1 };
    uint64_t v = 5;
    ptrdiff_t ui = 0;
    uint32_t ucp = 0;
    CHECK(!rx_eq(u, "") && !rx_eqi(u, "") && rx_find(u, "") == -1 &&
          !rx_u64(u, &v) && !rx_hex(u, &v) && v == 5 && !rx_in(u, 0, ~0ull) &&
          rx_u8next(u, &ui, &ucp) == 0 && ui == 0, "the unset span");
    /* the 64-bit boundary */
    static const char *const big[] = {
        "18446744073709551615", "18446744073709551616", "00018446744073709551615",
        "99999999999999999999", "ffffffffffffffff", "10000000000000000",
        "FFFFFFFFFFFFFFFF0",
    };
    for (size_t k = 0; k < sizeof big / sizeof big[0]; k++) {
        const rx_span s = { (const unsigned char *)big[k], (ptrdiff_t)strlen(big[k]) };
        uint64_t a = 1, r = 1;
        int ra = rx_u64(s, &a), rr = ref_num(s.p, s.len, 10, &r);
        CHECK(ra == rr && (!rr || a == r), "rx_u64 '%s'", big[k]);
        a = r = 1;
        ra = rx_hex(s, &a); rr = ref_num(s.p, s.len, 16, &r);
        CHECK(ra == rr && (!rr || a == r), "rx_hex '%s'", big[k]);
    }
    /* UTF-8: every 1-byte value, every lead with every continuation class,
     * truncated and complete. */
    static const unsigned char cont[] = { 0x00, 0x7F, 0x80, 0x8F, 0x90, 0x9F, 0xA0, 0xBF, 0xC0 };
    for (unsigned l = 0; l < 256; l++) {
        b[0] = (unsigned char)l;
        u8one(b, 1);
        for (size_t c1 = 0; c1 < sizeof cont; c1++) {
            b[1] = cont[c1]; u8one(b, 2);
            for (size_t c2 = 0; c2 < sizeof cont; c2++) {
                b[2] = cont[c2]; u8one(b, 3);
                for (size_t c3 = 0; c3 < sizeof cont; c3++) { b[3] = cont[c3]; u8one(b, 4); }
            }
        }
    }
    printf("span_check: %ld checks, %ld failed\n", checks, fails);
    return fails || checks < 100000;
}
