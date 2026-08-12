/* probe_mod05b.c — MOD-0.5 follow-up cells.
 * PREDICTOR, stated before the run:
 *   a{1, 2}  vs "aa":   MEASUREMENT — quantifier ([0,2)) or literal (no match)
 *   a{1, 2}  vs "a{1, 2}": the complement cell
 *   a{ 26}   vs "aa...": does a space-form still quantify
 *   (?^) reset scope: MEASUREMENT per letter —
 *     (?xx)(?^)[a b]   does ^ unset xx (space member again)?
 *     (?U)(?^)a+ /aaa  does ^ unset U (greedy again)?
 *     (?J)(?^)(?<g>a)(?<g>b)  does ^ unset J?
 *     (?s)(?^). /\n    does ^ unset s?
 *     (?n)(?^)(a) /a   does ^ unset n (rc=2 again)?
 *   x-skip census REDONE with a no-x control: skipped iff (?x)a<b>b matches
 *     "ab" [0,2) AND plain a<b>b does not — predict {09,0A,0B,0C,0D,20,85}
 * Build: gcc -I tests/fuzz -o probe_mod05b probe_mod05b.c -ldl
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>

static Pcre2Abi abi;

static pcre2_code_8 *comp(const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    return abi.compile((PCRE2_SPTR)pat, strlen(pat), 0, &err, &eoff, NULL);
}

static void try_match(const char *pat, const char *subj, size_t slen)
{
    pcre2_code_8 *code = comp(pat);
    printf("%-24s vs ", pat);
    for (size_t i = 0; i < slen; i++)
        printf(subj[i] >= 0x21 && subj[i] <= 0x7e ? "%c" : "\\x%02x",
               (unsigned char)subj[i]);
    printf("  ");
    if (!code) { puts("(no compile)"); return; }
    pcre2_match_data_8 *md = abi.match_data_create(8, NULL);
    int rc = abi.match(code, (PCRE2_SPTR)subj, slen, 0, 0, md, NULL);
    if (rc >= 0) {
        PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
        printf("rc=%d MATCH [%zu,%zu)\n", rc, (size_t)ov[0], (size_t)ov[1]);
    } else printf("no match (%d)\n", rc);
    abi.match_data_free(md);
    abi.code_free(code);
}
#define TM(p, s) try_match((p), (s), strlen(s))

static int matches_ab_fully(const char *pat, size_t plen)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, plen, 0, &err, &eoff, NULL);
    if (!code) return 0;
    pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
    int rc = abi.match(code, (PCRE2_SPTR)"ab", 2, 0, 0, md, NULL);
    PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
    int full = rc >= 0 && ov[0] == 0 && ov[1] == 2;
    abi.match_data_free(md);
    abi.code_free(code);
    return full;
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why); return 2;
    }

    puts("== brace quantifiers with spaces: quantifier or literal? ==");
    TM("a{1, 2}", "aa");
    TM("a{1, 2}", "a{1, 2}");
    TM("a{ 1,2}", "aa");
    TM("a{1,2 }", "aa");
    TM("a{ 2 }", "aa");
    TM("a{2 , 3}", "aaa");
    TM("a{,2}", "aa");
    TM("a{, 2}", "aa");
    TM("a{ ,2}", "aa");
    TM("(?x)a{1, 2}", "aa");
    TM("(?xx)a{1, 2}", "aa");

    puts("== (?^) reset scope per letter ==");
    TM("(?xx)(?^)[a b]", " ");
    TM("(?xx)(?^)a b", "ab");
    TM("(?U)(?^)a+", "aaa");
    TM("(?s)(?^).", "\n");
    TM("(?n)(?^)(a)", "a");
    {
        int err = 0; PCRE2_SIZE eoff = 0;
        const char *p = "(?J)(?^)(?<g>a)(?<g>b)";
        pcre2_code_8 *c = abi.compile((PCRE2_SPTR)p, strlen(p), 0, &err, &eoff, NULL);
        printf("%-24s %s", p, c ? "COMPILES (J survives ^)\n" : "");
        if (!c) {
            unsigned char msg[90];
            abi.get_error_message(err, msg, sizeof msg);
            printf("ERR %d  %s (J reset by ^)\n", err, msg);
        } else abi.code_free(c);
    }
    /* r: (?ri) is a no-op at options=0 so ^'s effect on r is unobservable
     * here; recorded as unobservable rather than probed. */

    puts("== x-skip census, controlled ==");
    {
        int n = 0;
        for (int b = 0; b < 256; b++) {
            char px[8] = "(?x)a?b", pp[4] = "a?b";
            px[5] = (char)b; pp[1] = (char)b;
            if (matches_ab_fully(px, 7) && !matches_ab_fully(pp, 3)) {
                printf("  skipped: 0x%02x\n", b); n++;
            }
        }
        printf("  total: %d\n", n);
    }
    return 0;
}
