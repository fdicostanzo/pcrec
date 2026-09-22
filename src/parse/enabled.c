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
 * explicit list already uses. See STD1_MODULES and g_named_sets below.
 *
 * [REL-1.11] (2026-09-21) `pcrec_options.features` promoted a LIBRARY
 * channel for this spec vocabulary (D20's own "promote later" clause).
 * D19 (thread-safety) is why `pcrec_compile` does NOT simply call
 * `pcrec_enabled_set_spec` below on every call: that would make the
 * process-global a per-call WRITE from every concurrent compile, which is
 * exactly the race D19 exists to rule out (one thread's install racing
 * another thread's mid-parse read of a DIFFERENT spec). Instead
 * `pcrec_enabled_resolve_spec` (bottom of this file) is the SAME
 * validation/expansion logic, factored out to touch no global state at
 * all; `compile_driver` (src/core/compile.c) calls it once per compile and
 * stores the result on that compile's own `Ctx` (`Ctx.enabled_features`,
 * internal.h), which `pcrec_feature_enabled` now takes explicitly rather
 * than reading a global. Everything below this comment is UNCHANGED and
 * stays the mechanism for this file's OTHER customers, none of which goes
 * through `pcrec_compile`: the CLI's own query surfaces
 * (--probe-ask/--count-groups/--list-source/--explain, installed once in
 * cli/main.c before mode dispatch, exactly as before) and
 * `--list-syntax`'s built-status probe (src/dump/syntax_dump.c's
 * save/force/restore dance) — both keep reading `pcrec_enabled_mask()`
 * into their own throwaway `Ctx`es. */

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
 * is never "enabled": there is nothing to switch. [REL-1.11]: `enabled_mask`
 * is the caller's OWN resolved mask (a compile's `Ctx.enabled_features`, or
 * a query surface's own `pcrec_enabled_mask()` read) — this function no
 * longer reads `g_enabled_features` itself, which is what makes it safe to
 * call with a mask that was never installed anywhere. */
bool pcrec_feature_enabled(unsigned enabled_mask, unsigned featmask)
{
    return featmask != 0 && (enabled_mask & featmask) == featmask;
}

/* The full FEAT_* mask currently installed by install() -- read-only after
 * spec-parse time. */
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

/* The installed set's expanded, comma-separated module-name list, rendered
 * once by install() so it can never drift from the mask. */
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
const char *const pcrec_default_features = "std1";

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
 *
 * [REVW.1] wave 1, L10-2: THE OVER-LONG POLICY IS AN ORDERED PREFIX, AND IT
 * USED TO BE SOMETHING NOBODY WOULD HAVE CHOSEN. A name that did not fit was
 * `continue`d past and SHORTER LATER NAMES WERE STILL APPENDED, so an
 * over-long list came back as an out-of-order, gap-toothed selection reading
 * exactly like a complete one — a stamp claiming a feature set the build does
 * not have. Returning is the whole fix: what does not fit is the TAIL, and a
 * truncated prefix is visibly truncated.
 *
 * THE DEFECT IS LATENT, NOT LIVE, AND THAT IS WHY THIS IS ONE KEYWORD AND NOT
 * A MECHANISM. Measured 2026-09-18: `--features all` renders 179 bytes into a
 * 512-byte buffer (35%), so the branch has never been taken. The kit's
 * `pcrec_sb_join` (src/core/sb.c) cannot truncate at all and is the better answer —
 * but it needs a `StrBuf`, i.e. a heap allocation, and this function's sibling
 * `pcrec_enc_names` (src/enc/enc.c) sits on `pcrec_compile`'s own refusal
 * path, where a failed realloc has no error channel and would `abort()` the
 * CALLER. One stated policy at both bounded sites beats one of them reaching
 * the primitive and the other not. */
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
            if (used + need >= outsz) return;   /* an ordered PREFIX, never a gap */
            if (used) out[used++] = ',';
            memcpy(out + used, m, mlen);
            used += mlen;
            out[used] = 0;
        }
    }
}

/* Records `mask`/`label` as the process-wide enabled set and renders its
 * expanded module-name list; the ONE writer, called once at spec-parse time
 * before any compile starts. */
static void install(unsigned mask, const char *label)
{
    g_enabled_features = mask;
    snprintf(g_enabled_label, sizeof g_enabled_label, "%s", label);
    render_modules(mask, g_enabled_modules, sizeof g_enabled_modules);
}

/* [REL-1.11] THE PURE RESOLVER: `pcrec_enabled_set_spec`'s own validation
 * and expansion logic, factored out to write NOTHING — no global, no
 * static buffer — so `compile_driver` can call it once per
 * `pcrec_compile()` with no D19 hazard (see this file's own top comment
 * and internal.h's declaration). Every rule below is copied verbatim from
 * the pre-[REL-1.11] `pcrec_enabled_set_spec` body: same vocabulary
 * (`all`/`none`/empty/a D37 named set/a comma list), same order of
 * checks, same unknown-module wording. `render_modules` (above) is
 * already pure; this function is what makes the REST of spec resolution
 * pure alongside it. */
int pcrec_enabled_resolve_spec(const char *spec, unsigned *mask_out,
                                char *label_out, size_t label_sz,
                                char *modules_out, size_t modules_sz,
                                char *err, size_t errsz)
{
    if (!spec) spec = "";
    unsigned mask = 0;
    const char *label;

    if (!strcmp(spec, "all")) {
        for (size_t k = 0; k < sizeof kinds / sizeof kinds[0]; k++) {
            size_t n;
            const RegRow *rows = pcrec_registry(kinds[k], &n);
            for (size_t i = 0; i < n; i++) mask |= rows[i].feature;
        }
        label = "all";
    } else if (!*spec || !strcmp(spec, "none")) {
        mask = 0;
        label = "none";
    } else {
        /* D37 named-set resolution: a spec that is EXACTLY one known frozen
         * set's name (no comma, nothing composed with it) expands to that
         * set's module list. Checked before the explicit-list parse below,
         * so "std1" resolves as a SET rather than being looked up as a
         * (nonexistent) module name. */
        const char *named = NULL;
        for (size_t s = 0; s < sizeof g_named_sets / sizeof g_named_sets[0]; s++) {
            if (strcmp(spec, g_named_sets[s].name) != 0) continue;
            for (size_t i = 0; i < g_named_sets[s].nmodules; i++) {
                const char *m = g_named_sets[s].modules[i];
                mask |= find_module_bits(m, strlen(m));
            }
            named = g_named_sets[s].name;
            break;
        }
        if (named) {
            label = named;
        } else {
            const char *p = spec;
            while (*p) {
                const char *comma = strchr(p, ',');
                size_t len = comma ? (size_t)(comma - p) : strlen(p);
                unsigned bits = find_module_bits(p, len);
                if (!bits) {
                    snprintf(err, errsz, "unknown module '%.*s' (names are "
                             "--list-syntax's module column; also 'all', "
                             "'none', or a named set: std1)", (int)len, p);
                    return -1;
                }
                mask |= bits;
                p = comma ? comma + 1 : p + len;
            }
            label = "explicit";
        }
    }

    *mask_out = mask;
    snprintf(label_out, label_sz, "%s", label);
    render_modules(mask, modules_out, modules_sz);
    return 0;
}

/* Parse an enabled-set spec: a comma-separated list of module names exactly
 * as `--list-syntax`'s module column spells them, "all", "none" / the empty
 * string, or (D37) a frozen named set's own name ("std1" today). Unknown
 * names are refused BY NAME — a typo must not silently enable nothing (the
 * --flavour rule, applied here). Returns 0 and installs the set, or -1 with
 * `err` filled and the set UNCHANGED. [REL-1.11]: now a thin caller of the
 * pure resolver above plus the global install — see this file's top
 * comment for why the two are separate functions. */
int pcrec_enabled_set_spec(const char *spec, char *err, size_t errsz)
{
    unsigned mask;
    char label[sizeof g_enabled_label];
    char modules[sizeof g_enabled_modules];
    if (pcrec_enabled_resolve_spec(spec, &mask, label, sizeof label,
                                    modules, sizeof modules, err, errsz) != 0)
        return -1;
    /* `install()` re-renders the module list from `mask` rather than
     * copying `modules` above — the same render_modules call, done twice,
     * which is cheap and keeps `install()` the ONE writer exactly as its
     * own comment states (unchanged by this refactor). */
    install(mask, label);
    return 0;
}
