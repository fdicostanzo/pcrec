/* tests/probes/probe_fix3.c — FIX-3 (K13) measurement: the twelve escape rows'
 * CLASS-position semantics, cell by cell, against libpcre2.
 *
 * PREDICTOR, stated before the first run (the probe_digit_sweep.c method).
 * From PCRE2's documented class-position escape rules — inside a class a
 * backreference is impossible, so check_escape falls back:
 *
 *   P1. [\g] [\k] [\8] [\9] compile and match exactly the literal letter
 *       (the §14.3 literal-fallback partition, complete at these four).
 *   P2. [\0]..[\7] are OCTAL: up to THREE octal digits are consumed starting
 *       at the first, value is the byte; a non-octal-digit stops the run and
 *       re-enters the class as an ordinary member ([\08] is {NUL,'8'},
 *       [\1234] is {0x53,'4'}).
 *   P3. A consumed value above \377 is PCRE2 error 151 in 8-bit non-UTF mode
 *       ([\400], [\777]).
 *   P4. Tails after the literal fallback re-enter as ordinary members:
 *       [\k<n>] is {k,<,n,>}; [\g{1}] is {g,{,1,}}.
 *   P5. Range endpoints ride along: a decoded escape is an ordinary endpoint
 *       ([0-\k] is 0x30..0x6b, [\1-\7] is 0x01..0x07), and out-of-order pairs
 *       are PCRE2 error 108.
 *
 * Error OFFSETS and message wording are RECORDED (printed per cell), not
 * predicted — they become the conformance data for pcrec's own diagnostics.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -o /var/tmp/probe_fix3 \
 *            tests/probes/probe_fix3.c -ldl
 */
#include "pcre2_abi.h"
#include <stdlib.h>

static Pcre2Abi abi;
static int npass, nfail;

/* spec: "N" negated; members given as comma-separated tokens `0xNN` or
 * `0xNN-0xNN`. verdict: 0 = compiles with exactly that member set,
 * else the predicted PCRE2 error code. */
typedef struct { const char *pat; int err; const char *members; int neg; } Cell;

static const Cell cells[] = {
    /* P1: the literal-fallback four */
    {"[\\g]",  0, "0x67", 0},
    {"[\\k]",  0, "0x6b", 0},
    {"[\\8]",  0, "0x38", 0},
    {"[\\9]",  0, "0x39", 0},
    {"[^\\k]", 0, "0x6b", 1},
    {"[\\g\\k]", 0, "0x67,0x6b", 0},
    /* P2: octal singles and runs */
    {"[\\0]",   0, "0x00", 0},
    {"[\\1]",   0, "0x01", 0},
    {"[\\7]",   0, "0x07", 0},
    {"[\\12]",  0, "0x0a", 0},
    {"[\\123]", 0, "0x53", 0},
    {"[\\1234]",0, "0x53,0x34", 0},
    {"[\\08]",  0, "0x00,0x38", 0},
    {"[\\18]",  0, "0x01,0x38", 0},
    {"[\\077]", 0, "0x3f", 0},
    {"[\\377]", 0, "0xff", 0},
    {"[\\0777]",0, "0x3f,0x37", 0},
    {"[\\378]", 0, "0x1f,0x38", 0},
    {"[\\0x]",  0, "0x00,0x78", 0},
    /* P1+P2 interactions: 8/9 stop an octal run and are literal */
    {"[\\81]",  0, "0x38,0x31", 0},
    {"[\\89]",  0, "0x38,0x39", 0},
    {"[\\98]",  0, "0x39,0x38", 0},
    {"[\\9x]",  0, "0x39,0x78", 0},
    /* P3: overflow */
    {"[\\400]", 151, "", 0},
    {"[\\777]", 151, "", 0},
    /* P4: tails re-enter as members */
    {"[\\k<n>]", 0, "0x6b,0x3c,0x6e,0x3e", 0},
    {"[\\g{1}]", 0, "0x67,0x7b,0x31,0x7d", 0},
    {"[\\g1]",   0, "0x67,0x31", 0},
    {"[\\k'n']", 0, "0x6b,0x27,0x6e", 0},
    /* P5: endpoints */
    {"[0-\\k]",  0, "0x30-0x6b", 0},
    {"[\\k-z]",  0, "0x6b-0x7a", 0},
    {"[\\1-\\7]",0, "0x01-0x07", 0},
    {"[\\0-\\7]",0, "0x00-0x07", 0},
    {"[\\8-\\9]",0, "0x38-0x39", 0},
    {"[\\g-\\k]",0, "0x67-0x6b", 0},
    {"[0-\\g]",  0, "0x30-0x67", 0},
    {"[\\15-\\17]", 0, "0x0d-0x0f", 0},
    {"[\\1-\\123]", 0, "0x01-0x53", 0},
    {"[a-\\1]",  108, "", 0},
    {"[0-\\12]", 108, "", 0},
    {"[\\k-\\g]",108, "", 0},
    /* The \g row's own `syntax` field wrapped in a class: after the literal
     * fallback, `{-1` is an ordinary out-of-order range ({ is 0x7b, 1 is
     * 0x31), so this must be error 108 — pcrec rejecting it is agreement,
     * and registry_check's class-base probe must not demand it compile. */
    {"[\\g{-1}]", 108, "", 0},
    {"[\\k<name>]", 0, "0x6b,0x3c,0x6e,0x61,0x6d,0x65,0x3e", 0},
};

static void want_set(const Cell *c, unsigned char set[256])
{
    memset(set, 0, 256);
    const char *p = c->members;
    while (p && *p) {
        unsigned lo, hi;
        int n = 0;
        if (sscanf(p, "0x%x-0x%x%n", &lo, &hi, &n) == 2 && n > 0) ;
        else if (sscanf(p, "0x%x%n", &lo, &n) == 1 && n > 0) hi = lo;
        else { fprintf(stderr, "bad members spec: %s\n", p); exit(2); }
        for (unsigned b = lo; b <= hi && b < 256; b++) set[b] = 1;
        p += n;
        if (*p == ',') p++;
    }
    if (c->neg)
        for (int b = 0; b < 256; b++) set[b] = !set[b];
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why);
        return 1;
    }
    for (size_t i = 0; i < sizeof cells / sizeof cells[0]; i++) {
        const Cell *c = &cells[i];
        int ec = 0;
        PCRE2_SIZE eo = 0;
        pcre2_code_8 *code = abi.compile((PCRE2_SPTR)c->pat, strlen(c->pat),
                                         0, &ec, &eo, NULL);
        if (!code) {
            unsigned char msg[128];
            abi.get_error_message(ec, msg, sizeof msg);
            if (c->err == ec) {
                printf("PASS %-12s -> error %d at offset %zu: %s\n",
                       c->pat, ec, (size_t)eo, msg);
                npass++;
            } else {
                printf("FAIL %-12s -> error %d at offset %zu (%s), predicted %s%d\n",
                       c->pat, ec, (size_t)eo, msg,
                       c->err ? "error " : "compile, got error ", c->err);
                nfail++;
            }
            continue;
        }
        if (c->err != 0) {
            printf("FAIL %-12s -> COMPILED, predicted error %d\n", c->pat, c->err);
            nfail++;
            abi.code_free(code);
            continue;
        }
        unsigned char want[256], got[256];
        want_set(c, want);
        pcre2_match_data_8 *md = abi.match_data_create(8, NULL);
        for (int b = 0; b < 256; b++) {
            unsigned char subj[1] = {(unsigned char)b};
            got[b] = abi.match(code, subj, 1, 0, 0, md, NULL) >= 0;
        }
        abi.match_data_free(md);
        abi.code_free(code);
        int diffs = 0, first = -1;
        for (int b = 0; b < 256; b++)
            if (want[b] != got[b]) { diffs++; if (first < 0) first = b; }
        if (diffs == 0) {
            printf("PASS %-12s -> compiles, member set exact\n", c->pat);
            npass++;
        } else {
            printf("FAIL %-12s -> %d member bytes differ (first: 0x%02x predicted %d got %d)\n",
                   c->pat, diffs, first, first >= 0 ? want[first] : 0,
                   first >= 0 ? got[first] : 0);
            nfail++;
        }
    }
    printf("probe_fix3: %d pass, %d fail of %zu cells\n",
           npass, nfail, sizeof cells / sizeof cells[0]);
    return nfail != 0;
}
