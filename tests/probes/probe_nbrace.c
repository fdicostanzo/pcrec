/* \N{...} vs quantifier fallback: the full boundary, measured.
   PREDICTOR (from the critic's cells): digits-only bodies that parse as a
   valid PCRE2 quantifier -> bare \N quantified (ACCEPT); everything else
   -> the unsupported \N{name} construct (err 137 family). Unknown cells:
   whitespace ({2, 3} — K8 says whitespace kills a quantifier), reversed
   ({3,2}), overflow, {0}. */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>
static Pcre2Abi abi;
static void v(const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0, &err, &eoff, NULL);
    if (c) { printf("%-18s COMPILES\n", pat); abi.code_free(c); }
    else    printf("%-18s err %d at %zu\n", pat, err, (size_t)eoff);
}
int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) { fprintf(stderr, "SKIP\n"); return 2; }
    v("\\N{2,3}"); v("\\N{2}"); v("\\N{3,}"); v("\\N{0}"); v("\\N{00}");
    v("\\N{007}"); v("\\N{3,2}"); v("\\N{2, 3}"); v("\\N{ 2}"); v("\\N{2 }");
    v("\\N{2,3,4}"); v("\\N{}"); v("\\N{,}"); v("\\N{,3}"); v("\\N{2,}");
    v("\\N{99999999999}"); v("\\N{65536}"); v("\\N{65535}");
    v("\\N{2x}"); v("\\N{x2}"); v("\\N{U+41}"); v("\\N{2");
    return 0;
}
