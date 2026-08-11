/* probe_verify.c — author verification of R14 panel measurements.
 * Build: TMPDIR=/var/tmp gcc -I /home/duxevents/pcrec/tests/fuzz -o probe_verify probe_verify.c -ldl
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
    printf("%-10s %-26s ", label, pat);
    if (!code) {
        unsigned char msg[100];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %3d @%zu  %s\n", err, (size_t)eoff, msg);
        return;
    }
    printf("COMPILES");
    if (s1) {
        pcre2_match_data_8 *md = abi.match_data_create(8, NULL);
        int rc = abi.match(code, (PCRE2_SPTR)s1, strlen(s1), 0, 0, md, NULL);
        printf("  vs \"%s\": %s", s1, rc >= 0 ? "MATCH" : "no");
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
    puts("== C3/F13: digit runs starting 8/9 ==");
    one("v1", "^\\81$", NULL);
    one("v2", "^\\99$", NULL);
    one("v3", "^\\801$", NULL);
    one("v4", "^\\18$", NULL);
    one("v5", "^\\108$", NULL);
    puts("== C3/F6: quantifiability ==");
    one("v6", "a\\b*", NULL);
    one("v7", "a(?i)*", NULL);
    one("v8", "a(*FAIL)*", NULL);
    one("v9", "a(?=x)*", NULL);
    one("v10", "a(?C1)*", NULL);
    puts("== C3/F4: (?# in class; \\Q in class ==");
    one("v11", "^[a(?#x)]+$", "(#x)");
    one("v12", "^[\\Qa-z\\E]$", "-");
    puts("== C3/F2: capture forms ==");
    one("v13", "\\1(?<n>a)", NULL);
    one("v14", "\\1(?=(a))", NULL);
    one("v15", "\\1(?=a)", NULL);
    one("v16", "\\1(*MARK:(x)", NULL);
    one("v17", "\\1(*MARK:(x)(a)", NULL);
    puts("== C3/F3: conditional with gated-construct body ==");
    one("v18", "(a)(?(1)\\d|y|z)", NULL);
    one("v19", "(a)(?(1)\\q|y|z)", NULL);
    puts("== C3/F12, C2/F2, C3/F5: endpoint edges ==");
    one("v20", "[0-\\c]", NULL);
    one("v21", "[\\c-z]", NULL);
    one("v22", "[0-\\g{1}]", NULL);
    one("v23", "[\\g{1}-z]", NULL);
    one("v24", "[0-[:]", NULL);
    one("v25", "[0-[.a]", NULL);
    one("v26", "[0-[=a]", NULL);
    one("v27", "[0-[:^digit:]]", NULL);
    puts("== C2/F4: (?x) comment changes count ==");
    one("v28", "\\2(?x)#(a)\n(b)", NULL);
    one("v29", "\\2#(a)\n(b)", NULL);
    return 0;
}
