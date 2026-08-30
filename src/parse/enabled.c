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
 * thread suite compiles concurrently and relies on that — this extends to
 * the label/module-list state added below: both are filled by `install()`
 * at spec-parse time, before any compile, and never touched again). It is
 * NOT a pcrec_options field on purpose — D20 rules the core API's option
 * surface stays scalar and this is internal configuration, not a
 * caller-facing option; a library channel can be promoted later if a real
 * caller wants one (the usual easy-to-promote, hard-to-unpromote direction).
 *
 * The default is EMPTY: with nothing enabled, every gate demotes and pcrec
 * behaves byte-identically to the pre-slice build — which the 952-pattern
 * differential asserts rather than assumes. Enabling a module whose ports do
 * not exist yet changes NO verdict today; what it changes today is the probe
 * channel's answered_at, and check07 exists to hold the verdict-equivalence
 * half forever.
 *
 * D37 (docs/dev/decisions.md) ADDS frozen named sets on top of the mask
 * machinery above, WITHOUT changing it: a named set is just a fixed list of
 * module names that expands to a mask through the same registry lookup an
 * explicit list already uses. See STD1_MODULES and g_named_sets below. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

static unsigned g_enabled_features;     /* FEAT_* mask; empty at start */

/* D37's stamping payload: WHICH NAME resolved the currently-installed set
 * ("std1", "all", "none", or "explicit" for a hand-written module list) and
 * the set's own EXPANDED module list, comma-separated, rendered from the
 * mask so it can never drift from what is actually enabled. Both are filled
 * once by install() below, at spec-parse time, and read by src/gen's
 * artifact stamping — a fixed-size buffer rather than malloc/free because
 * every valid value is short and bounded, and it keeps the write-once/
 * read-many contract this file already documents above (safe under the
 * thread suite's concurrent COMPILES, because nothing writes here again
 * after install() returns). */
static char g_enabled_label[24]   = "none";
static char g_enabled_modules[512] = "";

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

/* D37's artifact-stamping readers: src/gen consults these at emission time
 * (still before any concurrent compile could start writing anything, since
 * nothing here is ever written again after install()). */
const char *pcrec_enabled_set_label(void)
{
    return g_enabled_label;
}

const char *pcrec_enabled_set_modules(void)
{
    return g_enabled_modules;
}

/* ---- D37: frozen named feature sets ------------------------------------
 *
 * `std1` = {classes, modifiers} — the two modules that had, at freeze time
 * (2026-08-12), survived a checkpoint panel AND carry PC-3 differential
 * coverage against libpcre2. FROZEN FOREVER once shipped: `--features std1`
 * must compile identically for as long as pcrec exists. DO NOT add a module
 * to STD1_MODULES — a future graduate forms the NEXT named set (std2 =
 * std1 + {x}), it does not join this one. */
static const char *const STD1_MODULES[] = { "classes", "modifiers" };

typedef struct {
    const char *name;
    const char *const *modules;
    size_t nmodules;
} NamedFeatureSet;

static const NamedFeatureSet g_named_sets[] = {
    { "std1", STD1_MODULES, sizeof STD1_MODULES / sizeof STD1_MODULES[0] },
};

/* D37's bare-default MAPPING POINT: the one place "no --features flag at
 * all" resolves to a value from the same vocabulary --features itself
 * accepts (a named set, "all", or "none"). The CLI (and any future non-CLI
 * caller) reads this rather than deciding the default for itself.
 *
 * FLIPPED TO "std1" at [STD1b] (docs/dev/plan.md, 2026-08-13) — the first
 * announced version-boundary advance D37 describes, travelling in the
 * same landing as the full suite re-baseline (reject_gated inversions,
 * corpus `features` directives, check07's gate equivalence, the PC-3 gate
 * state). Every older set stays available verbatim forever: a caller who
 * wants the old bare behaviour passes --features none, and one who wants
 * THIS default pinned regardless of future boundaries passes --features
 * std1. The next advance (std2, when a module graduates) changes this
 * constant and nothing else. */
const char *const PCREC_DEFAULT_FEATURES = "std1";

/* [M6.4.2] RK_QUANTSUFFIX joins the list, and it MATTERS here rather than
 * being cosmetic: this array is what `find_module_bits` and `render_modules`
 * iterate, so a kind missing from it is a module whose name `--features` does
 * not recognise and a mask whose rendered module list is short. Module
 * `atomic-groups` owns rows in TWO kinds (`(?>` is RK_GROUP), so the omission
 * would have been invisible to `--features atomic-groups` and visible only if
 * a future module owned quant-suffix rows alone. No `-Wswitch` guards this;
 * `tests/registry/registry_check.c`'s `check_kind_coverage` reads the dump. */
static const RegKind kinds[] = { RK_ESC, RK_GROUP, RK_VERB, RK_CLASSBRACKET,
                                 RK_QUANTSUFFIX, RK_BARE };

/* The one name->bits lookup in this file (a spec's explicit list and a
 * named set's expansion both go through it, so there is no second copy of
 * the pairing to drift). Name->bits comes from the registry rows
 * themselves, exactly as before D37; tests/registry/ already proves
 * module<->feature is a bijection. */
static unsigned find_module_bits(const char *name, size_t len)
{
    for (size_t k = 0; k < sizeof kinds / sizeof kinds[0]; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry(kinds[k], &n);
        for (size_t i = 0; i < n; i++) {
            const char *m = rows[i].module;
            if (m && strlen(m) == len && strncmp(m, name, len) == 0)
                return rows[i].feature;
        }
    }
    return 0;
}

/* Whole-token membership test over a comma list, used only to DEDUP
 * render_modules' output below (a module can own more than one row). */
static bool module_listed(const char *list, const char *name)
{
    size_t nlen = strlen(name);
    const char *p = list;
    while (*p) {
        const char *comma = strchr(p, ',');
        size_t len = comma ? (size_t)(comma - p) : strlen(p);
        if (len == nlen && strncmp(p, name, nlen) == 0) return true;
        p = comma ? comma + 1 : p + len;
    }
    return false;
}

/* D37's reproducible payload: the module list rendered FROM THE MASK, not
 * carried along from whichever path (named set / "all" / explicit list)
 * produced it — so it can never say something the mask disagrees with.
 * Truncates rather than overflows if the registry ever outgrows the
 * buffer (nothing in the tree is close to that today). */
static void render_modules(unsigned mask, char *out, size_t outsz)
{
    out[0] = 0;
    if (!mask) return;
    size_t used = 0;
    for (size_t k = 0; k < sizeof kinds / sizeof kinds[0]; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry(kinds[k], &n);
        for (size_t i = 0; i < n; i++) {
            unsigned f = rows[i].feature;
            const char *m = rows[i].module;
            if (!f || !m || (mask & f) != f) continue;
            if (module_listed(out, m)) continue;
            size_t mlen = strlen(m);
            size_t need = mlen + (used ? 1 : 0);
            if (used + need >= outsz) continue;
            if (used) out[used++] = ',';
            memcpy(out + used, m, mlen);
            used += mlen;
            out[used] = 0;
        }
    }
}

static void install(unsigned mask, const char *label)
{
    g_enabled_features = mask;
    snprintf(g_enabled_label, sizeof g_enabled_label, "%s", label);
    render_modules(mask, g_enabled_modules, sizeof g_enabled_modules);
}

/* Parse an enabled-set spec: a comma-separated list of module names exactly
 * as `--list-syntax`'s module column spells them, "all", "none" / the empty
 * string, or (D37) a frozen named set's own name ("std1" today). Unknown
 * names are refused BY NAME — a typo must not silently enable nothing (the
 * --flavour rule, applied here). Returns 0 and installs the set, or -1 with
 * `err` filled and the set UNCHANGED. */
int pcrec_enabled_set_spec(const char *spec, char *err, size_t errsz)
{
    if (!spec) spec = "";

    if (!strcmp(spec, "all")) {
        unsigned mask = 0;
        for (size_t k = 0; k < sizeof kinds / sizeof kinds[0]; k++) {
            size_t n;
            const RegRow *rows = pcrec_registry(kinds[k], &n);
            for (size_t i = 0; i < n; i++) mask |= rows[i].feature;
        }
        install(mask, "all");
        return 0;
    }
    if (!*spec || !strcmp(spec, "none")) {
        install(0, "none");
        return 0;
    }

    /* D37 named-set resolution: a spec that is EXACTLY one known frozen
     * set's name (no comma, nothing composed with it) expands to that
     * set's module list. Checked before the explicit-list parse below, so
     * "std1" resolves as a SET rather than being looked up as a
     * (nonexistent) module name. */
    for (size_t s = 0; s < sizeof g_named_sets / sizeof g_named_sets[0]; s++) {
        if (strcmp(spec, g_named_sets[s].name) != 0) continue;
        unsigned mask = 0;
        for (size_t i = 0; i < g_named_sets[s].nmodules; i++) {
            const char *m = g_named_sets[s].modules[i];
            mask |= find_module_bits(m, strlen(m));
        }
        install(mask, g_named_sets[s].name);
        return 0;
    }

    unsigned mask = 0;
    const char *p = spec;
    while (*p) {
        const char *comma = strchr(p, ',');
        size_t len = comma ? (size_t)(comma - p) : strlen(p);
        unsigned bits = find_module_bits(p, len);
        if (!bits) {
            snprintf(err, errsz, "unknown module '%.*s' (names are "
                     "--list-syntax's module column; also 'all', 'none', "
                     "or a named set: std1)", (int)len, p);
            return -1;
        }
        mask |= bits;
        p = comma ? comma + 1 : p + len;
    }
    install(mask, "explicit");
    return 0;
}
