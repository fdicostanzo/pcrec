/* d27region: tuning.md §2.43¶3e through the library (pcrec_options.memfn_simd,
 * lib/pcrec.h): "SIMD off with a list is refused; SIMD off is the kit's
 * portable target; SIMD on with a list is exactly that list; SIMD on with no
 * list is the host family's default list." Prints one line per case:
 *   <case> <rc> <TARGETS value or ->
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pcrec.h"

static void one(const char *name, uint64_t bits, const char *list)
{
    pcrec_options o;
    pcrec_output out;
    pcrec_error err;
    pcrec_default_options(&o);
    o.flags |= bits;
    o.memfn_simd = list;
    memset(&out, 0, sizeof out);
    memset(&err, 0, sizeof err);
    int rc = pcrec_compile("needle", &o, &out, &err);
    const char *t = rc == 0 && out.c_src ? strstr(out.c_src, "_TARGETS \"") : NULL;
    char v[64] = "-";
    if (t) {
        t = strchr(t, '"') + 1;
        size_t n = strcspn(t, "\"");
        if (n < sizeof v) { memcpy(v, t, n); v[n] = 0; }
    }
    printf("%s %d %s %s\n", name, rc, v, rc ? err.msg : "");
    if (rc == 0)
        pcrec_output_free(&out);
}

int main(void)
{
    one("off-nolist", 0, NULL);
    one("off-list", 0, "x86-64-v3");
    one("deny-list", PCREC_NO_MEMFN_SIMD, "x86-64-v3");
    one("deny-force-list", PCREC_NO_MEMFN_SIMD | PCREC_FORCE_MEMFN_SIMD, "x86-64-v3");
    one("force-nolist", PCREC_FORCE_MEMFN_SIMD, NULL);
    one("force-list", PCREC_FORCE_MEMFN_SIMD, "x86-64-v3");
    one("force-generic", PCREC_FORCE_MEMFN_SIMD, "generic");
    return 0;
}
