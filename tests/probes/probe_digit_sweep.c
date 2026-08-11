/* probe_digit_sweep.c — generated sweep of the digit-escape model behind the
 * deferred-resolution design (§18.1). PREDICTOR, stated before running:
 *
 *   escape run E at position with B groups before, A groups after (T = B+A):
 *   - E starts with '0'                  -> octal always; compiles; no backref
 *   - E single digit d in 1..9          -> backref always; compiles iff T >= d
 *   - E multi-digit n, leading 1..7:
 *         B >= n  -> backref n
 *         B <  n  -> OCTAL (running count decides; total is irrelevant)
 *   - E multi-digit n, leading 8..9:
 *         backref always; compiles iff T >= n   (validity by TOTAL, like \1)
 *
 * Verified via PCRE2_INFO_BACKREFMAX (sanity-checked first) so backref-ness
 * is read from libpcre2, not inferred from matching.
 *
 * Build: TMPDIR=/var/tmp gcc -I /home/duxevents/pcrec/tests/fuzz -o probe_digit_sweep probe_digit_sweep.c -ldl
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define INFO_BACKREFMAX   2u
#define INFO_CAPTURECOUNT 4u
typedef int (*fn_pattern_info)(const pcre2_code_8 *, uint32_t, void *);

static Pcre2Abi abi;
static fn_pattern_info pattern_info;

static int fails, total_probes;

static void run(int B, int A, const char *e)
{
    char pat[1024]; size_t k = 0;
    pat[k++] = '^';
    for (int i = 0; i < B; i++) { memcpy(pat + k, "(a)", 3); k += 3; }
    pat[k++] = '\\';
    memcpy(pat + k, e, strlen(e)); k += strlen(e);
    for (int i = 0; i < A; i++) { memcpy(pat + k, "(a)", 3); k += 3; }
    pat[k++] = '$'; pat[k] = 0;

    int n = atoi(e), T = B + A;
    int exp_compile, exp_backref; /* predictor */
    if (e[0] == '0')            { exp_compile = 1; exp_backref = 0; }
    else if (strlen(e) == 1)    { exp_compile = (T >= n); exp_backref = 1; }
    else if (e[0] >= '8')       { exp_compile = (T >= n); exp_backref = 1; }
    else                        { exp_backref = (B >= n); exp_compile = 1; }

    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                     &err, &eoff, NULL);
    total_probes++;
    if (!code) {
        if (exp_compile || err != 115) {
            printf("DISAGREE B=%-3d A=%-3d \\%s: predicted %s, got ERR %d\n",
                   B, A, e, exp_compile ? "compile" : "115", err);
            fails++;
        }
        return;
    }
    uint32_t brmax = 0;
    pattern_info(code, INFO_BACKREFMAX, &brmax);
    int got_backref = brmax == (uint32_t)n && n > 0;
    if (!exp_compile || got_backref != exp_backref) {
        printf("DISAGREE B=%-3d A=%-3d \\%s: predicted %s/%s, got compile brmax=%u\n",
               B, A, e, exp_compile ? "compile" : "115",
               exp_backref ? "backref" : "octal", brmax);
        fails++;
    }
    abi.code_free(code);
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why); return 2;
    }
    void *h = dlopen("libpcre2-8.so.0", RTLD_NOW | RTLD_LOCAL);
    pattern_info = (fn_pattern_info)dlsym(h, "pcre2_pattern_info_8");
    if (!pattern_info) { fprintf(stderr, "SKIP: no pattern_info\n"); return 2; }

    /* sanity: constants right? (a)\1 -> capturecount 1, backrefmax 1 */
    {
        int err; PCRE2_SIZE eo;
        pcre2_code_8 *c = abi.compile((PCRE2_SPTR)"(a)\\1", 5, 0, &err, &eo, NULL);
        uint32_t cc = 99, bm = 99;
        pattern_info(c, INFO_CAPTURECOUNT, &cc);
        pattern_info(c, INFO_BACKREFMAX, &bm);
        if (cc != 1 || bm != 1) {
            fprintf(stderr, "SANITY FAIL: cc=%u bm=%u — INFO constants wrong\n", cc, bm);
            return 3;
        }
        abi.code_free(c);
    }

    const char *escapes[] = { "1","3","7","9","10","11","12","13","17",
                              "0","01","08","012", NULL };
    for (int B = 0; B <= 14; B++)
        for (int A = 0; A <= 14; A++)
            for (int i = 0; escapes[i]; i++)
                run(B, A, escapes[i]);

    /* the 8/9-start forward-validity cells need big counts */
    run(0, 89, "89");   /* predict: compiles, backref 89 (validity by TOTAL) */
    run(0, 88, "89");   /* predict: 115 */
    run(89, 0, "89");   /* predict: compiles, backref */
    run(0, 81, "81");   /* predict: compiles, backref */
    run(0, 12, "12");   /* the t1a cell: predict octal */
    run(12, 0, "12");   /* predict backref */

    printf("probes: %d, disagreements: %d\n", total_probes, fails);
    return fails ? 1 : 0;
}
