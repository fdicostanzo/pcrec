/* probe_endpoint_k12.c — MOD-0.1 endpoint-rule slice (K12): the exact cells
 * the change touches, measured against libpcre2 BEFORE any pin is written.
 *
 * PREDICTOR, stated before the run (§16 as R14-corrected, five steps):
 *   - a certifiably SET-shaped item (the ten char-type escapes; a KNOWN
 *     POSIX name) at either range endpoint => err 150, unless the OTHER
 *     side's own error fires first per the five-step order
 *     (low's own error -> high pair-open -> high's own error -> SET -> order)
 *   - an item with its own class-position error (\A family err 107,
 *     [[:foo:]] err 130, [[.a.]] err 113, whole-class-only names err 130)
 *     keeps that error at the endpoint position the five steps reach it in
 *   - body-dependent rows: \p{L} is SET-shaped (150 at endpoints) but
 *     \p{Foo} errors 147 — the cell pcrec deliberately does NOT certify
 *     (scope judgment in the 2026-08-11 journal entry): pcrec keeps the
 *     module promise for every \p endpoint because it cannot validate the
 *     body until MOD-0.6's property table exists
 *   - non-range dashes ([\d-], [\d-]]) leave the construct's ordinary
 *     class answer in force
 *
 * Output: pattern TAB verdict (0 or the error number). Exit 0 always; this
 * is a measurement, the pins derived from it are the check.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -o /var/tmp/probe_k12 \
 *            tests/probes/probe_endpoint_k12.c -ldl
 */

#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>

static Pcre2Abi abi;

static void probe(const char *pat)
{
    int err = 0;
    PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                  &err, &eoff, NULL);
    if (c) { printf("%s\tCOMPILES\n", pat); abi.code_free(c); }
    else   printf("%s\terr %d at %zu\n", pat, err, (size_t)eoff);
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "FAIL: libpcre2 missing — %s\n", why);
        return 2;
    }
    char ver[64];
    pcre2_abi_version(&abi, ver, sizeof ver);
    printf("# oracle: libpcre2 %s\n", ver);

    /* the ten char-type escapes, both sides, plus both-construct pairs */
    static const char *const esc[] = { "d", "D", "s", "S", "w", "W",
                                       "h", "H", "v", "V", NULL };
    char pat[64];
    for (int i = 0; esc[i]; i++) {
        snprintf(pat, sizeof pat, "[0-\\%s]", esc[i]); probe(pat);
        snprintf(pat, sizeof pat, "[\\%s-z]", esc[i]); probe(pat);
    }
    probe("[\\d-\\d]");
    probe("[\\d-\\w]");
    probe("[z-\\d]");
    probe("[\\d-\\A]");      /* high's own error beats low's SET (step 3) */
    probe("[\\d-\\p{Foo}]"); /* high's own error, body-invalid property */
    probe("[0-\\A]");        /* high's own error, no SET anywhere */

    /* the deliberate non-certified boundary: \p/\P endpoints */
    probe("[0-\\p{L}]");
    probe("[\\p{L}-z]");
    probe("[0-\\p{Foo}]");
    probe("[0-\\P{L}]");

    /* bracket doorway, low side (high side is the pair_opens cell, shipped) */
    probe("[[:alpha:]-z]");
    probe("[[:digit:]-z]");
    probe("[x[:alpha:]-z]"); /* mid-class low endpoint */
    probe("[[:foo:]-z]");    /* own error: unknown name */
    probe("[[:<:]-z]");      /* own error: whole-class-only name */
    probe("[[.a.]-z]");      /* own error: collating */
    probe("[[=a=]-z]");      /* own error: equivalence */

    /* non-range dashes: the construct's ordinary answer must stay */
    probe("[\\d-]");
    probe("[\\d-]]");        /* trailing ] outside the class */
    probe("[[:alpha:]-]");

    /* truncation: dash then end of pattern */
    probe("[[:alpha:]-");
    probe("[\\d-");

    return 0;
}
