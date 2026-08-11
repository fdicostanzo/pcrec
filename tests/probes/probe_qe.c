/* probe_qe.c — measurements for the OQ 6/7/8/9/10/11 redesign addendum.
 *
 * Sections:
 *   A  \Q...\E quantifier binding and grouping
 *   B  \Q...\E inside classes (metacharacter quoting, range interaction)
 *   C  \Q lexical-vs-semantic interactions ((?i), (?x), backrefs, nesting)
 *   D  (?#...) transparency at atom position
 *   E  class-position escape sweep: literal-fallback vs construct vs error
 *   F  range-endpoint decision table, per doorway x per side
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -o probe_qe probe_qe.c -ldl
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>

static Pcre2Abi abi;

static void one(const char *label, const char *pat, uint32_t opts,
                const char *s1, const char *s2)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat), opts,
                                     &err, &eoff, NULL);
    printf("%-14s %-24s opt=%06x  ", label, pat, opts);
    if (!code) {
        unsigned char msg[120];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %3d @%zu  %s\n", err, (size_t)eoff, msg);
        return;
    }
    printf("COMPILES");
    const char *subs[2] = { s1, s2 };
    for (int i = 0; i < 2; i++) {
        if (!subs[i]) continue;
        pcre2_match_data_8 *md = abi.match_data_create(8, NULL);
        int rc = abi.match(code, (PCRE2_SPTR)subs[i], strlen(subs[i]),
                           0, 0, md, NULL);
        /* print subject with escapes for non-printables */
        printf("   vs \"");
        for (const char *p = subs[i]; *p; p++)
            if (*p >= 32 && *p < 127) putchar(*p);
            else printf("\\x%02x", (unsigned char)*p);
        if (rc >= 0) {
            PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
            printf("\": MATCH [%zu,%zu)", (size_t)ov[0], (size_t)ov[1]);
        } else {
            printf("\": no");
        }
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

    puts("== A. \\Q\\E quantifier binding ==");
    one("A1", "^\\Qab\\E*$", 0, "abbb", "ababab");
    one("A2", "^a\\Q\\E*$", 0, "aaa", NULL);
    one("A3", "^\\Q\\E*$", 0, NULL, NULL);
    one("A4", "^(\\Qab\\E)*$", 0, "ababab", "abbb");
    one("A5", "^\\Qab\\E+$", 0, "abbb", "ab");
    one("A6", "^\\Qab\\E{2}$", 0, "abb", "abab");

    puts("");
    puts("== B. \\Q\\E inside classes ==");
    one("B1", "^[\\Qa-z\\E]$", 0, "-", "b");
    one("B2", "^[\\Q]\\E]$", 0, "]", NULL);
    one("B3", "^[a\\Q\\E-z]$", 0, "m", "-");
    one("B4", "^[\\Q^\\Ea]$", 0, "^", "a");
    one("B5", "^[0-\\Q\\Ea]$", 0, "5", "a");
    one("B6", "^[0-\\E9]$", 0, "5", "-");
    one("B7", "^[\\Q\\\\\\E]$", 0, "\\", NULL);

    puts("");
    puts("== C. lexical interactions ==");
    one("C1", "(?i)\\Qa\\E", 0, "A", "a");
    one("C2", "(?x)\\Q a\\E", 0, " a", "a");
    one("C3", "^(a)\\Q\\1\\E$", 0, "a\\1", "aa");
    one("C4", "^\\Q\\Q\\E$", 0, "\\Q", NULL);
    one("C5", "^\\Qab$", 0, "ab", "ab$");
    one("C6", "^a\\Eb$", 0, "ab", NULL);
    one("C7", "^[a\\E]$", 0, "a", NULL);
    one("C8", "^\\Qa\\E\\E b$", 0x00000080u /* EXTENDED */, "ab", "a b");

    puts("");
    puts("== D. (?#...) transparency ==");
    one("D1", "^a(?#x)*$", 0, "aaa", "a");
    one("D2", "^(?#x)*$", 0, "", NULL);
    one("D3", "^a(?#x)b$", 0, "ab", NULL);
    one("D4", "^[0-(?#x)]$", 0, "(", "5");

    puts("");
    puts("== E. class-position escape sweep [\\c] ==");
    {
        const char *set = "abcdefghijklmnopqrstuvwxyz"
                          "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        for (const char *p = set; *p; p++) {
            char pat[16], lbl[8], sub1[2] = { *p, 0 };
            char sub2[2] = { 0, 0 };
            snprintf(pat, sizeof pat, "^[\\%c]$", *p);
            snprintf(lbl, sizeof lbl, "E-%c", *p);
            /* for digits also try the octal byte value */
            if (*p >= '1' && *p <= '7') sub2[0] = (char)(*p - '0');
            one(lbl, pat, 0, sub1, sub2[0] ? sub2 : NULL);
        }
    }

    puts("");
    puts("== F. endpoint decision table ==");
    puts("-- high side, escape doorway --");
    one("F-h-e1", "[0-\\d]", 0, NULL, NULL);
    one("F-h-e2", "[0-\\p{L}]", 0, NULL, NULL);
    one("F-h-e3", "[0-\\p{Foo}]", 0, NULL, NULL);
    one("F-h-e4", "[0-\\p]", 0, NULL, NULL);
    one("F-h-e5", "[0-\\N{U+41}]", 0, NULL, NULL);
    one("F-h-e6", "[0-\\x{110000}]", 0, NULL, NULL);
    one("F-h-e7", "^[0-\\x41]$", 0, "5", NULL);
    one("F-h-e8", "^[0-\\k]$", 0, "5", NULL);
    one("F-h-e9", "[0-\\8]", 0, NULL, NULL);
    one("F-h-e10", "[0-\\A]", 0, NULL, NULL);
    puts("-- high side, bracket doorway --");
    one("F-h-b1", "[0-[:digit:]]", 0, NULL, NULL);
    one("F-h-b2", "[0-[:foo:]]", 0, NULL, NULL);
    one("F-h-b3", "[0-[.ab.]]", 0, NULL, NULL);
    one("F-h-b4", "[0-[=x=]]", 0, NULL, NULL);
    puts("-- low side, escape doorway --");
    one("F-l-e1", "[\\d-z]", 0, NULL, NULL);
    one("F-l-e2", "[\\p{L}-z]", 0, NULL, NULL);
    one("F-l-e3", "[\\p{Foo}-z]", 0, NULL, NULL);
    one("F-l-e4", "[\\p-z]", 0, NULL, NULL);
    one("F-l-e5", "[\\N{U+41}-z]", 0, NULL, NULL);
    one("F-l-e6", "^[\\x41-z]$", 0, "b", NULL);
    one("F-l-e7", "^[\\k-z]$", 0, "m", NULL);
    one("F-l-e8", "[\\8-z]", 0, NULL, NULL);
    one("F-l-e9", "[\\A-z]", 0, NULL, NULL);
    puts("-- low side, bracket doorway --");
    one("F-l-b1", "[[:alpha:]-z]", 0, NULL, NULL);
    one("F-l-b2", "[[:foo:]-z]", 0, NULL, NULL);
    one("F-l-b3", "[[.a.]-z]", 0, NULL, NULL);
    one("F-l-b4", "[[=a=]-z]", 0, NULL, NULL);
    one("F-l-b5", "[[:<:]-z]", 0, NULL, NULL);
    puts("-- order / dissolution --");
    one("F-x1", "[z-\\x41]", 0, NULL, NULL);
    one("F-x2", "[0-\\Q\\Ea]", 0, NULL, NULL);
    one("F-x3", "[0-\\Q-\\E9]", 0, NULL, NULL);
    one("F-x4", "^[0-\\E]$", 0, "-", "0");

    return 0;
}
