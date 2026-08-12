/* caseless x posix cells: PREDICTOR (fold-before-negate, OS-1/D23):
   /[[:lower:]]/i matches 'A'; /[[:^lower:]]/i matches NEITHER 'a' nor 'A'
   but matches '0'; /[^[:lower:]]/i same as [[:^lower:]]/i. */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>
static Pcre2Abi abi;
#define PCRE2_CASELESS_OPT 0x00000008u
static void tryci(const char *pat, const char *subj)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = abi.compile((PCRE2_SPTR)pat, strlen(pat), PCRE2_CASELESS_OPT, &err, &eoff, NULL);
    if (!c) { printf("%-16s (err %d)\n", pat, err); return; }
    pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
    int rc = abi.match(c, (PCRE2_SPTR)subj, strlen(subj), 0, 0, md, NULL);
    printf("%-16s vs %-4s %s\n", pat, subj, rc >= 0 ? "MATCH" : "nomatch");
    abi.match_data_free(md); abi.code_free(c);
}
int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) { fprintf(stderr, "SKIP\n"); return 2; }
    tryci("^[[:lower:]]$", "A");
    tryci("^[[:lower:]]$", "a");
    tryci("^[[:^lower:]]$", "a");
    tryci("^[[:^lower:]]$", "A");
    tryci("^[[:^lower:]]$", "0");
    tryci("^[^[:lower:]]$", "A");
    tryci("^[^[:lower:]]$", "0");
    tryci("^[[:upper:]]$", "a");
    return 0;
}
