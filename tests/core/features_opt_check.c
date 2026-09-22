/* tests/core/features_opt_check.c — [REL-1.11] THE LIBRARY'S OWN
 * `--features` LEVER: `pcrec_options.features`.
 *
 * WHY IT LIVES HERE. This is not a check on an internal helper spanning
 * several feature directories (this directory's usual charter, see
 * CLAUDE.md) — it is the PUBLIC library surface's own acceptance check for
 * a new `pcrec_options` field, and there is no existing per-module test
 * directory that owns "the enabled-feature-set lever" as a subject; it is
 * orthogonal to any one construct family. `tests/spec_mod0/` is NOT the
 * home despite its ten module-0 checks covering the enabled-set MACHINERY
 * (check01/check07/check09) — every check there runs `build/pcrec` as a
 * BLACK BOX (`spec_pcrec.h`'s own header: "running the pcrec BINARY as a
 * black box"), never links `libpcrec.a`, and this row's whole subject is a
 * LIBRARY struct field no CLI invocation can exercise directly. This
 * directory's own `unit_build` (`tests/lib/unit_cc.sh`) is the shape that
 * fits: one gcc invocation, one process, `libpcrec.a` linked directly.
 *
 * WHAT IT CHECKS, per the row's own acceptance bar. A single construct,
 * `(?=a)b` (module `lookaround`, never a member of the frozen `std1` set —
 * src/parse/enabled.c's own STD1_MODULES comment: "DO NOT add a module to
 * STD1_MODULES"), compiled four ways through `pcrec_compile()` alone, no
 * CLI invocation anywhere:
 *
 *   1. `features = NULL`      -> REFUSED, naming module 'lookaround'.
 *   2. `features = "all"`     -> COMPILES.
 *   3. `features = "std1"`    -> REFUSED, naming module 'lookaround'
 *                                 (std1 does not carry it — the case NULL
 *                                 and "std1" are expected to agree on,
 *                                 which is exactly the design note this
 *                                 lane's report argues for: NULL means "no
 *                                 request", not "std1" — see
 *                                 docs/dev/lanes/libfeat_report.md).
 *   4. `features = "nosuchmodule"` -> REFUSED at spec-validation, with the
 *                                 IDENTICAL text `pcrec --features
 *                                 nosuchmodule` prints on stderr (minus
 *                                 the CLI's own "--features: " prefix) —
 *                                 `pcrec_enabled_resolve_spec`'s one
 *                                 wording, read by both callers.
 *
 * Plus the PER-CALL / NOT-GLOBAL claim (D19) the row exists to make safe:
 * two back-to-back `pcrec_compile()` calls on the SAME PROCESS with
 * DIFFERENT `features` values must not leak into each other — asserted
 * directly by interleaving "all" and "none" compiles of the same
 * lookaround pattern and checking each call's own verdict, which would be
 * impossible to get wrong under the OLD global-install mechanism (nothing
 * install-and-restores between these calls, unlike every process-global
 * consumer elsewhere in this tree) and is exactly the property a
 * global-install redesign would have made fragile.
 */

#include "pcrec.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

static int pass_n, fail_n;

static void ok(const char *fmt, ...)
{
    va_list ap; va_start(ap, fmt);
    printf("PASS: "); vprintf(fmt, ap); printf("\n");
    va_end(ap);
    pass_n++;
}
static void bad(const char *fmt, ...)
{
    va_list ap; va_start(ap, fmt);
    fprintf(stderr, "FAIL: "); vfprintf(stderr, fmt, ap); fprintf(stderr, "\n");
    va_end(ap);
    fail_n++;
}

#define WITNESS "(?=a)b"   /* module `lookaround`, never in std1 */

/* Compiles WITNESS under `features`; on success frees `out` and returns 1;
 * on refusal copies the diagnostic into `msg` and returns 0. */
static int try_witness(const char *features, char *msg, size_t msgsz)
{
    pcrec_options opt; pcrec_output out; pcrec_error err;
    pcrec_default_options(&opt);
    opt.features = features;
    memset(&out, 0, sizeof out);
    memset(&err, 0, sizeof err);
    int rc = pcrec_compile(WITNESS, &opt, &out, &err);
    if (rc == 0) { pcrec_output_free(&out); return 1; }
    snprintf(msg, msgsz, "%s", err.msg);
    return 0;
}

int main(void)
{
    char msg[256];

    /* ==================================================================
     * 1. NULL -> refused naming the module.
     * ================================================================== */
    if (try_witness(NULL, msg, sizeof msg))
        bad("features=NULL compiled '%s' -- module 'lookaround' should not "
            "be reachable with no request made", WITNESS);
    else if (!strstr(msg, "lookaround"))
        bad("features=NULL refused '%s' but not naming 'lookaround': %s",
            WITNESS, msg);
    else
        ok("features=NULL: refused naming the module (%s)", msg);

    /* ==================================================================
     * 2. "all" -> compiles.
     * ================================================================== */
    if (!try_witness("all", msg, sizeof msg))
        bad("features=\"all\" refused '%s': %s", WITNESS, msg);
    else
        ok("features=\"all\": compiled");

    /* ==================================================================
     * 3. "std1" -> refused naming the module (std1 does not carry it).
     * ================================================================== */
    if (try_witness("std1", msg, sizeof msg))
        bad("features=\"std1\" compiled '%s' -- lookaround is not one of "
            "std1's frozen members (src/parse/enabled.c STD1_MODULES)",
            WITNESS);
    else if (!strstr(msg, "lookaround"))
        bad("features=\"std1\" refused '%s' but not naming 'lookaround': %s",
            WITNESS, msg);
    else
        ok("features=\"std1\": refused naming the module (%s)", msg);

    /* ==================================================================
     * 4. "nosuchmodule" -> the SAME error text the CLI prints, minus the
     *    CLI's own "--features: " prefix (cli/main.c's own cli_err call).
     *    A trivial pattern is used since the spec is invalid before the
     *    pattern is even looked at.
     * ================================================================== */
    {
        pcrec_options opt; pcrec_output out; pcrec_error err;
        pcrec_default_options(&opt);
        opt.features = "nosuchmodule";
        memset(&out, 0, sizeof out);
        memset(&err, 0, sizeof err);
        int rc = pcrec_compile("a", &opt, &out, &err);
        static const char *const EXPECT =
            "unknown module 'nosuchmodule' (names are --list-syntax's "
            "module column; also 'all', 'none', or a named set: std1)";
        if (rc == 0) {
            pcrec_output_free(&out);
            bad("features=\"nosuchmodule\" compiled instead of refusing "
                "the spec");
        } else if (strcmp(err.msg, EXPECT) != 0) {
            bad("features=\"nosuchmodule\" wording differs from the CLI's "
                "own text.\n     got: %s\n    want: %s", err.msg, EXPECT);
        } else {
            ok("features=\"nosuchmodule\": identical wording to the CLI's "
               "own \"--features: %s\"", err.msg);
        }
    }

    /* ==================================================================
     * 5. PER-CALL, NOT GLOBAL (D19): interleaved "all"/"none" compiles of
     *    the SAME pattern in the SAME process, with nothing install-ing or
     *    restoring anything between them -- the shape that would corrupt
     *    under a process-global mechanism the moment two calls disagreed.
     * ================================================================== */
    {
        int ok_all1 = try_witness("all", msg, sizeof msg);
        int ok_none = !try_witness("none", msg, sizeof msg);   /* expect refusal */
        int ok_all2 = try_witness("all", msg, sizeof msg);
        int ok_null = !try_witness(NULL, msg, sizeof msg);     /* expect refusal */
        int ok_all3 = try_witness("all", msg, sizeof msg);
        if (ok_all1 && ok_none && ok_all2 && ok_null && ok_all3)
            ok("interleaved all/none/all/NULL/all calls each answered "
               "independently -- no state survives between compiles");
        else
            bad("interleaved calls disagreed with a fresh single call: "
                "all1=%d none=%d all2=%d null=%d all3=%d (each should be 1)",
                ok_all1, ok_none, ok_all2, ok_null, ok_all3);
    }

    printf("\nchecks passed: %d\n", pass_n);
    printf("checks failed: %d\n", fail_n);
    return fail_n ? 1 : 0;
}
