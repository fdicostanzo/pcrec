/* probe_defer.c — does deferred end-of-parse backref resolution match PCRE2?
 * Key questions:
 *   (1) does \12's octal-vs-backref decision use the TOTAL count (forward
 *       groups included) or the running count?
 *   (2) when an invalid \1 coexists with a later real syntax error, which
 *       error does PCRE2 report? (deferred resolution surfaces the later
 *       error first; a pre-scan surfaces 115 first)
 * Build: TMPDIR=/var/tmp gcc -I /home/duxevents/pcrec/tests/fuzz -o probe_defer probe_defer.c -ldl
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>

static Pcre2Abi abi;

static void one(const char *label, const char *pat, const char *s1)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                     &err, &eoff, NULL);
    printf("%-8s %-44s ", label, pat);
    if (!code) {
        unsigned char msg[100];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %3d @%zu  %s\n", err, (size_t)eoff, msg);
        return;
    }
    printf("COMPILES");
    if (s1) {
        pcre2_match_data_8 *md = abi.match_data_create(16, NULL);
        int rc = abi.match(code, (PCRE2_SPTR)s1, strlen(s1), 0, 0, md, NULL);
        printf("  vs \"");
        for (const char *p = s1; *p; p++)
            if (*p >= 32 && *p < 127) putchar(*p);
            else printf("\\x%02x", (unsigned char)*p);
        printf("\": %s", rc >= 0 ? "MATCH" : "no");
        abi.match_data_free(md);
    }
    printf("\n");
    abi.code_free(code);
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why);
        return 2;
    }
    puts("== (1) \\12 decision: total count or running count? ==");
    /* 12 groups AFTER the \12. If total count decides, \12 is a backref
     * (matches empty at that point? no — backref to group 12 which matches
     * later... a forward backref matches empty only if unset-match... PCRE2:
     * unset backref fails to match by default). Distinguish by matching:
     * octal 012 = \n. */
    one("t1a", "^\\12(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)$", "\nabcdefghijkl");
    one("t1b", "^\\12(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)$", "abcdefghijkl");
    /* control: 12 groups BEFORE -> known backref */
    one("t1c", "^(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)\\12$", "abcdefghijkll");
    one("t1d", "^(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)\\12$", "abcdefghijkl\n");
    /* 11 groups after: total=11 < 12 -> octal if total decides */
    one("t1e", "^\\12(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)$", "\nabcdefghijk");

    puts("");
    puts("== (2) error precedence: invalid \\1 vs later syntax error ==");
    one("t2a", "\\1[", NULL);           /* 115 @1 or 106 (missing ]) ? */
    one("t2b", "\\1(", NULL);           /* 115 or 114 (missing ) ) ? */
    one("t2c", "\\1a**", NULL);         /* 115 or 109 ? -- a** is err? */
    one("t2d", "a**", NULL);            /* control: is ** an error at all */
    one("t2e", "\\1(?P<n", NULL);       /* 115 or 142? */
    one("t2f", "\\1\\q", NULL);         /* 115 or 103? both invalid escapes */
    one("t2g", "\\q\\1", NULL);         /* other order */
    one("t2h", "\\1{2,1}", NULL);       /* 115 or 104 (quant range)? */

    puts("");
    puts("== (3) conditionals reference groups the same way? ==");
    one("t3a", "(?(1)a|b)(x)", NULL);   /* forward group ref in (?(1) */
    one("t3b", "(?(2)a|b)(x)", NULL);   /* group 2 never exists */
    return 0;
}
