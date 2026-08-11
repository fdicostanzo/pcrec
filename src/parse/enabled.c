/* The ENABLED SET (MOD-0.1 slice 9) — in its own translation unit ON PURPOSE.
 *
 * This is the one home of "which feature modules are switched on". The gate
 * at the doorway seam (ext.c) is its only compile-path consumer; the CLI's
 * --features flag is its only writer. The extent scans in scans.c must never
 * link the symbols defined here — that is spec check01's nm contract, and it
 * is the mechanical form of §12's rule that recognisers are ALWAYS LIVE: what
 * a construct IS cannot depend on what is switched on, only whether its
 * producer may run.
 *
 * PROCESS-WIDE, WRITE-ONCE-THEN-READ by design: the CLI parses the spec
 * before any compile starts, and nothing writes during compilation (the
 * thread suite compiles concurrently and relies on that). It is NOT a
 * pcrec_options field on purpose — D20 rules the core API's option surface
 * stays scalar and this is internal configuration, not a caller-facing
 * option; a library channel can be promoted later if a real caller wants
 * one (the usual easy-to-promote, hard-to-unpromote direction).
 *
 * The default is EMPTY: with nothing enabled, every gate demotes and pcrec
 * behaves byte-identically to the pre-slice build — which the 952-pattern
 * differential asserts rather than assumes. Enabling a module whose ports do
 * not exist yet changes NO verdict (the NULL-port refusal is the same
 * refusal); what it changes today is the probe channel's answered_at, and
 * check07 exists to hold the verdict-equivalence half forever. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

static unsigned g_enabled_features;     /* FEAT_* mask; empty at start */

/* The membership question the gate asks. A zero mask (base/rejected rows)
 * is never "enabled": there is nothing to switch. */
bool pcrec_feature_enabled(unsigned featmask)
{
    return featmask != 0 && (g_enabled_features & featmask) == featmask;
}

unsigned pcrec_enabled_mask(void)
{
    return g_enabled_features;
}

/* Parse an enabled-set spec: a comma-separated list of module names exactly
 * as `--list-syntax`'s module column spells them, or "all", or "none" / the
 * empty string. Unknown names are refused BY NAME — a typo must not silently
 * enable nothing (the --flavour rule, applied here).
 *
 * Name->bits comes from the registry rows themselves (module string beside
 * feature mask), so this function cannot hold a second copy of the pairing;
 * tests/registry/ already proves module<->feature is a bijection. Returns 0
 * and installs the set, or -1 with `err` filled and the set UNCHANGED. */
int pcrec_enabled_set_spec(const char *spec, char *err, size_t errsz)
{
    static const RegKind kinds[] = { RK_ESC, RK_GROUP, RK_VERB,
                                     RK_CLASSBRACKET };
    unsigned mask = 0;

    if (!spec) spec = "";
    if (!strcmp(spec, "all")) {
        for (size_t k = 0; k < sizeof kinds / sizeof kinds[0]; k++) {
            size_t n;
            const RegRow *rows = pcrec_registry(kinds[k], &n);
            for (size_t i = 0; i < n; i++) mask |= rows[i].feature;
        }
        g_enabled_features = mask;
        return 0;
    }
    if (!*spec || !strcmp(spec, "none")) {
        g_enabled_features = 0;
        return 0;
    }

    const char *p = spec;
    while (*p) {
        const char *comma = strchr(p, ',');
        size_t len = comma ? (size_t)(comma - p) : strlen(p);
        unsigned bits = 0;
        for (size_t k = 0; k < sizeof kinds / sizeof kinds[0] && !bits; k++) {
            size_t n;
            const RegRow *rows = pcrec_registry(kinds[k], &n);
            for (size_t i = 0; i < n; i++) {
                const char *m = rows[i].module;
                if (m && strlen(m) == len && strncmp(m, p, len) == 0) {
                    bits = rows[i].feature;
                    break;
                }
            }
        }
        if (!bits) {
            snprintf(err, errsz, "unknown module '%.*s' (names are "
                     "--list-syntax's module column; also 'all', 'none')",
                     (int)len, p);
            return -1;
        }
        mask |= bits;
        p = comma ? comma + 1 : p + len;
    }
    g_enabled_features = mask;
    return 0;
}
