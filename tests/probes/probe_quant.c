/* probe_quant.c — is quantifiability deterministic PER ROW?
 * Candidate refuters:
 *   (1) the option-run row: (?i)* vs (?i:a)* — one row family, two forms
 *   (2) the verb row: (*FAIL)* vs (*pla:a)* — one row, fifty names,
 *       some of which are group constructs in verb spelling
 *   (3) misc atoms: \K, backrefs, subroutine calls, conditionals, callouts
 * Build: TMPDIR=/var/tmp gcc -I /home/duxevents/pcrec/tests/fuzz -o probe_quant probe_quant.c -ldl
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>

static Pcre2Abi abi;

static void one(const char *label, const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                     &err, &eoff, NULL);
    printf("%-8s %-28s ", label, pat);
    if (!code) {
        unsigned char msg[90];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %3d  %s\n", err, msg);
        return;
    }
    printf("COMPILES\n");
    abi.code_free(code);
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why); return 2;
    }
    puts("== (1) option-run row: two forms, one family ==");
    one("q1a", "a(?i)*");
    one("q1b", "a(?i:b)*");
    one("q1c", "a(?i-m)*");
    one("q1d", "a(?i-m:b)*");
    one("q1e", "a(?^)*");
    one("q1f", "a(?^i:b)*");

    puts("== (2) the verb row: fifty names, one row ==");
    one("q2a", "a(*FAIL)*");
    one("q2b", "a(*MARK:x)*");
    one("q2c", "a(*pla:b)*");
    one("q2d", "a(*positive_lookahead:b)*");
    one("q2e", "a(*atomic:b)*");
    one("q2f", "a(*script_run:b)*");
    one("q2g", "a(*nla:b)*");
    one("q2h", "a(*COMMIT)*");
    one("q2i", "a(*CR)*");

    puts("== (3) misc atoms ==");
    one("q3a", "a\\K*");
    one("q3b", "(a)\\1*");
    one("q3c", "(a)(?1)*");
    one("q3d", "(a)(?(1)x|y)*");
    one("q3e", "(?(DEFINE)x)*");
    one("q3f", "a(?C1)*");
    one("q3g", "a(?C\"x\")*");
    one("q3h", "(?<n>a)(?&n)*");
    one("q3i", "(?<n>a)\\k<n>*");
    one("q3j", "a\\R*");
    one("q3k", "a\\X*");
    return 0;
}
