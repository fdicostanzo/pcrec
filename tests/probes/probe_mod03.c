/* probe_mod03.c — MOD-0.3 scope probes against libpcre2.
 * PREDICTOR, stated before the run:
 *   [[:^alpha:]]   COMPILES; census == [^[:alpha:]] exactly (256 bytes)
 *   [[:^foo:]]     err 130 (unknown name; negation changes nothing)
 *   [[:^digit:]x]  COMPILES
 *   [[:<:]]        COMPILES (whole-class only); zero-width word-start assert
 *   [[:^<:]]       err 130
 *   (?[[a]])       no prediction — MEASUREMENT (extended-class support/option)
 * Build: gcc -I tests/fuzz -o probe_mod03 probe_mod03.c -ldl
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

static void verdict(const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                     &err, &eoff, NULL);
    printf("%-16s ", pat);
    if (!code) {
        unsigned char msg[90];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %3d at %zu  %s\n", err, (size_t)eoff, msg);
        return;
    }
    printf("COMPILES\n");
    abi.code_free(code);
}

static void try_match(const char *pat, const char *subj)
{
    pcre2_code_8 *code = comp(pat);
    printf("%-14s vs %-6s ", pat, subj);
    if (!code) { puts("(no compile)"); return; }
    pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
    int rc = abi.match(code, (PCRE2_SPTR)subj, strlen(subj), 0, 0, md, NULL);
    if (rc >= 0) {
        PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
        printf("MATCH [%zu,%zu)\n", (size_t)ov[0], (size_t)ov[1]);
    } else printf("no match (%d)\n", rc);
    abi.match_data_free(md);
    abi.code_free(code);
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why); return 2;
    }
    puts("== verdicts ==");
    verdict("[[:^alpha:]]");
    verdict("[[:^foo:]]");
    verdict("[[:^digit:]x]");
    verdict("[[:<:]]");
    verdict("[[:^<:]]");
    verdict("[[:>:]]");
    verdict("(?[[a]])");
    verdict("(?[a])");
    verdict("[[:alpha:]]");

    puts("== census: [[:^alpha:]] vs [^[:alpha:]] over 256 bytes ==");
    {
        pcre2_code_8 *a = comp("[[:^alpha:]]");
        pcre2_code_8 *b = comp("[^[:alpha:]]");
        if (a && b) {
            pcre2_match_data_8 *ma = abi.match_data_create(4, NULL);
            pcre2_match_data_8 *mb = abi.match_data_create(4, NULL);
            int diff = 0, members = 0;
            for (int i = 0; i < 256; i++) {
                unsigned char s[1] = { (unsigned char)i };
                int ra = abi.match(a, s, 1, 0, 0, ma, NULL) >= 0;
                int rb = abi.match(b, s, 1, 0, 0, mb, NULL) >= 0;
                members += ra;
                if (ra != rb) { diff++; printf("  0x%02x: ^name=%d [^...]=%d\n", i, ra, rb); }
            }
            printf("  members(^alpha)=%d, diff bytes=%d\n", members, diff);
            abi.match_data_free(ma); abi.match_data_free(mb);
        } else puts("  (a compile failed)");
        if (a) abi.code_free(a);
        if (b) abi.code_free(b);
    }

    puts("== [[:<:]] behaviour (zero-width?) ==");
    try_match("[[:<:]]ab", "ab");
    try_match("a[[:<:]]b", "ab");
    try_match("x[[:<:]]a", "xa");
    try_match("ab[[:>:]]", "ab");
    return 0;
}
