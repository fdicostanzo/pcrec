/* check07_gate_equivalence.c — INVARIANT 7: gate equivalence, with a real
 * population. (And invariant 9's population machinery; see check09.)
 *
 * THE PROMISE. "Disabled-feature verdicts equal enabled-feature verdicts,
 * varied over the WHOLE enabled set (all on / all off / one inverted), with a
 * per-name compared-pair count and a ratcheting floor printed on the PASS
 * line — an empty population is indistinguishable from a pass otherwise, and
 * at landing the population IS empty until the first module flips. Membership
 * ('whose validity PCRE2 decides') is computed by asking libpcre2, never
 * hand-listed."
 *
 * THE CLAIM. Whether pcrec has a feature switched on must not change what it
 * says about a pattern's VALIDITY. A disabled feature changes what pcrec can
 * COMPILE — that is the point of a gate — but not what it considers real: a
 * construct pcrec refuses because the module is off must still be refused as
 * "requires module 'X'", never as "that is not valid syntax". Otherwise the
 * gate is not a gate, it is a second, quieter grammar.
 *
 * MEMBERSHIP IS MEASURED, NOT LISTED. "Whose validity PCRE2 decides" is a
 * question about PCRE2, so it is put to PCRE2: a row is a member iff libpcre2
 * ACCEPTS the row's `syntax` probe as a pattern. A hand-maintained list of
 * member rows would be a transcription of somebody's belief about which
 * constructs are real, and it would agree with that belief forever. The count
 * is printed every run, so a row leaving the set is visible.
 *
 * WHY THE PER-NAME COUNT AND THE FLOOR ARE THE WHOLE POINT. The comparison
 * "disabled verdict == enabled verdict" is trivially satisfied when there is
 * nothing to compare, and today there IS nothing: no module is implemented, so
 * no gate can be flipped, so the compared-pair count is ZERO. A check that
 * printed "PASS: no disagreements" here would be lying by omission. So the
 * count is printed per module name, the total is floored, and the check exits
 * nonzero while the population is empty. When the first module lands, its
 * floor is raised from 0 in floors.txt and the pass starts meaning something.
 *
 * WHAT IS ASSERTED, once the surface exists. For each module name, and for
 * each of the three enabled-set configurations the invariant names —
 *      all on   : every module enabled
 *      all off  : none enabled
 *      inverted : every module enabled EXCEPT this one
 * — compile every registry row's syntax probe with pcrec and compare the
 * VERDICT CLASS (accepted / refused-as-unimplemented / refused-as-invalid)
 * against the same row under "all on". The pairs that must match are the ones
 * where libpcre2 decides validity: the membership set above. A row that is
 * refused as INVALID under one configuration and as UNIMPLEMENTED under
 * another is the failure, and it is reported with the row, the module, and
 * both configurations.
 *
 * SABOTAGE (verified on the oracle half): drop the membership test and take
 * all 100 rows as members, and the printed membership count jumps, failing its
 * pinned floor's sibling assertion below. On the pcrec half, the sabotage is
 * the one the invariant implies: make one gated construct report a syntax
 * error instead of "requires module 'X'" when its module is off, and that
 * row's pair mismatches under 'inverted' but not under 'all on'.
 *
 * AWAITED SURFACE (measured 2026-08-11). pcrec has no way to vary the enabled
 * set: `--help` lists -o, -p, -e, -i, --emit-main, -h, --list-syntax,
 * --list-verbs, --explain, --flavour, and none of them enables or disables a
 * feature. `--list-syntax`'s `status` column reports 1 base, 94 module, 5
 * rejected rows, and the 94 are unimplemented rather than switchable. So the
 * compared-pair population is empty by construction today, exactly as the
 * invariant predicts at landing.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check07 check07_gate_equivalence.c -ldl
 * Run:   check07 floors.txt registry.tsv
 */
#include "spec_common.h"

/* module names, as they appear in the registry's `module` column */
static char names[64][64];
static long pairs[64];
static int nnames;

static int name_index(const char *m)
{
    for (int i = 0; i < nnames; i++)
        if (!strcmp(names[i], m)) return i;
    if (nnames >= 64) return -1;
    snprintf(names[nnames], 64, "%s", m);
    pairs[nnames] = 0;
    return nnames++;
}

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check07_gate_equivalence", argc, argv, &rp);

    /* ---- membership: whose validity does PCRE2 decide? ------------------ */
    long members = 0, nonmembers = 0;
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *S = spec_col(r, SPEC_COL_SYNTAX);
        if (spec_compile(S).ok) members++; else nonmembers++;
        const char *m = spec_col(r, SPEC_COL_MODULE);
        if (m && *m) name_index(m);
    }
    printf("  membership (libpcre2 accepts the row's syntax probe): %ld of "
           "%d rows; %ld rows it rejects\n", members, spec_nrows, nonmembers);
    printf("  module names in the registry: %d\n", nnames);
    spec_pop("gate.membership_rows", members);
    spec_pop("gate.module_names", nnames);

    /* Membership must not be everything or nothing: either would mean the
     * question was not actually asked. */
    if (members == 0 || members == spec_nrows)
        spec_fail("membership is %ld of %d — a set that is empty or universal "
                  "is not a measurement, it is a constant", members, spec_nrows);

    /* ---- per-name compared pairs: zero until a module can be flipped ---- */
    long total_pairs = 0;
    for (int i = 0; i < nnames; i++) {
        printf("  PERNAME %-18s pairs %ld\n", names[i], pairs[i]);
        total_pairs += pairs[i];
    }
    spec_pop("gate.compared_pairs", total_pairs);

    if (total_pairs == 0)
        printf("  POPULATION IS EMPTY: zero enabled/disabled pairs were "
               "compared. This is NOT a pass — no module can be toggled yet, "
               "so the equivalence claim is untested. Raise the "
               "gate.compared_pairs floor when the first module lands.\n");

    static const char *const owned[] = {
        "gate.membership_rows", "gate.module_names", "gate.compared_pairs"
    };
    spec_floors_require(owned, 3);
    if (spec_fails) return spec_finish();

    return spec_await(
        "a way to vary pcrec's enabled feature set",
        "this check needs to compile a pattern under a chosen enabled set — "
        "any stable channel (a `--features=a,b,c` flag, a `PCREC_FEATURES` "
        "environment variable, or a library entry point) that accepts the "
        "module names from `--list-syntax`'s module column. It then runs the "
        "three configurations the invariant names (all on / all off / every "
        "module but this one) over all registry rows, compares verdict "
        "CLASSES (accepted / refused-as-unimplemented / refused-as-invalid) "
        "against 'all on' for the membership set computed above, and prints "
        "the compared-pair count per module name");
}
