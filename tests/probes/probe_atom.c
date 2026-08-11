/* probe_atom.c — atom-position facts for the per-port recognition sections.
 * Build: TMPDIR=/var/tmp gcc -I /home/duxevents/pcrec/tests/fuzz -o probe_atom probe_atom.c -ldl
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
    printf("%-10s %-34s ", label, pat);
    if (!code) {
        unsigned char msg[120];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %3d @%zu  %s\n", err, (size_t)eoff, msg);
        return;
    }
    printf("COMPILES");
    if (s1) {
        pcre2_match_data_8 *md = abi.match_data_create(8, NULL);
        int rc = abi.match(code, (PCRE2_SPTR)s1, strlen(s1), 0, 0, md, NULL);
        printf("   vs \"");
        for (const char *p = s1; *p; p++)
            if (*p >= 32 && *p < 127) putchar(*p);
            else printf("\\x%02x", (unsigned char)*p);
        if (rc >= 0) {
            PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
            printf("\": MATCH [%zu,%zu)", (size_t)ov[0], (size_t)ov[1]);
        } else printf("\": no");
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

    puts("== atom position: the class-side literal-fallback four ==");
    one("g-bare", "^\\g$", NULL);
    one("k-bare", "^\\k$", NULL);
    one("8-bare", "^\\8$", "8");
    one("9-bare", "^\\9$", "9");
    one("8-grp", "(a)(a)(a)(a)(a)(a)(a)(a)\\8", "aaaaaaaaa");

    puts("");
    puts("== backref vs octal at atom vs class (per-port recognition) ==");
    one("br-0", "^\\12$", "\n");
    one("br-1", "^(a)\\12$", "a\n");
    one("br-12", "^(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)\\12$",
        "aaaaaaaaaaaaa");
    one("br-12c", "^(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)[\\12]$",
        "aaaaaaaaaaaa\n");

    puts("");
    puts("== C2/F3 re-verification: \\1 validity depends on later text ==");
    one("fw-1", "\\1(a)", NULL);
    one("fw-2", "\\1\\Q(a)\\E", NULL);
    one("fw-3", "\\1(?#()", NULL);
    one("fw-4", "\\1(?|(a))", NULL);
    one("fw-5", "(?n)(a)x12\\12", NULL);

    puts("");
    puts("== \\0 can never be a backreference ==");
    one("z-1", "^\\0$", NULL);
    one("z-2", "^(a)\\0$", "a\x00");

    return 0;
}
