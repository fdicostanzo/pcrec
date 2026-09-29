/* src/parse/mod_ucp.c — module `ucp` (docs/design/ucp_design.md, D130).
 *
 * WHAT THE MODULE OWNS. The `(*UCP)` start-of-pattern verb, the `--ucp`
 * generation axis's parse-time meaning, and — through the definitions table's
 * `DEF_UCP_*` rows (registry.c) — what `\d \s \w` and the POSIX classes mean
 * under UCP. It also owns `(*UTF)`/`(*UTF8)`, which RESTATE `--encoding=utf8`
 * rather than switch to it (§1.2, D130 Q2): the encoding is a property of the
 * ARTIFACT's entry points, so a pattern may confirm it and may never change it.
 *
 * O-71: an encoding may IMPLY this module (`PcrecEnc.implied_features`), which
 * is how `-e utf8` makes `(*UCP)` and `(*UTF)` available without `--features`.
 * Enabled is not ON: UCP semantics apply only when `(*UCP)` or `--ucp` says so. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"
#include "parse_mods.h"

/* Builds this module's refusal ExtResult carrying `msg` at `at`. */
static ExtResult ucp_refuse(ExtWant want, size_t at, const char *msg)
{
    ExtResult res = { .what = EXT_REFUSAL, .at = at, .msg = "",
                      .answered_at = want };
    snprintf(res.msg, sizeof res.msg, "%s", msg);
    return res;
}

/* An accepted start-of-pattern option: an A_EMPTY that matches nothing and is
 * not a repeatable item (`(*UTF)*` is PCRE2 error 109, the `(?i)*` shape), and
 * that extends the accepted option run so the NEXT option may follow it. */
static ExtResult ucp_option_node(Ctx *cx, ExtWant want, size_t at, size_t end)
{
    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = pcrec_ast_node(cx, A_EMPTY);
    res.node->not_repeatable = true;
    res.end = end;
    cx->optrun_end = end;
    return res;
}

/* The `(*UTF)`/`(*UTF8)` port: accepted as a restatement when the compile's
 * encoding IS Unicode (its universe is Unicode's, `max_cp`), refused by the
 * row's own fixed sentence otherwise — asked of the encoding, never of its
 * identity (DD-12 (7)). `from` is one past the verb's `)`. */
ExtResult pcrec_ucpport_utf(Ctx *cx, const RegRow *rw, ExtWant want,
                            size_t at, size_t from)
{
    if (pcrec_enc_by_id(cx->opt->encoding)->max_cp < 0x10FFFFu)
        return ucp_refuse(want, at, rw->msg);
    return ucp_option_node(cx, want, at, from);
}

/* The `(*UCP)` port: UCP semantics for the whole pattern (a start-of-pattern
 * verb, so there is nothing scoped to save or restore), then the option node. */
ExtResult pcrec_ucpport_ucp(Ctx *cx, const RegRow *rw, ExtWant want,
                            size_t at, size_t from)
{
    (void)rw;
    cx->mods->ucp = true;
    return ucp_option_node(cx, want, at, from);
}

/* ---- the UCP SETS, as compositions of existing tables (§1.1, §1.4) --------
 *
 * Every right-hand side is a SET EQUALITY measured against libpcre2 10.46
 * under UTF|UCP ([O] `docs/design/ucp_measurements/out/ucp_sets_10.46.txt`,
 * 57 relations, 0 off expectation). A property term is a unicode-props
 * bare-namespace name (normalised) read through `pcrec_uprops_span`, so a UCP
 * set is the same generated table `\p{..}` is; a range term is a code-point
 * run. `[:graph:]`/`[:print:]` are COMPLEMENTS whose carve-out code points are
 * all `Cf`, which is what makes "not in these" equal to the measured formula
 * `[^\p{Z}\p{C}] ∪ (\p{Cf} minus them)`. */
#define PROP(n)     { (n), 0, 0 }
#define RANGE(a, b) { NULL, (a), (b) }
#define SETDEF(var, nm, cmp, inert, terms) \
    const PcrecSetDef var = { (nm), (cmp), (inert), (terms), \
                              (int)(sizeof (terms) / sizeof (terms)[0]) }

static const PcrecSetTerm t_nd[]    = { PROP("ND") };
static const PcrecSetTerm t_xsp[]   = { PROP("XSP") };
static const PcrecSetTerm t_xps[]   = { PROP("XPS") };
static const PcrecSetTerm t_xwd[]   = { PROP("XWD") };
static const PcrecSetTerm t_l[]     = { PROP("L") };
static const PcrecSetTerm t_xan[]   = { PROP("XAN") };
static const PcrecSetTerm t_ll[]    = { PROP("LL") };
static const PcrecSetTerm t_lu[]    = { PROP("LU") };
static const PcrecSetTerm t_cc[]    = { PROP("CC") };
/* `\h` under UTF (19 code points, [O] `[[:blank:]]` = `\h`). */
static const PcrecSetTerm t_blank[] = {
    RANGE(0x09, 0x09), RANGE(0x20, 0x20), RANGE(0xA0, 0xA0),
    RANGE(0x1680, 0x1680), RANGE(0x180E, 0x180E), RANGE(0x2000, 0x200A),
    RANGE(0x202F, 0x202F), RANGE(0x205F, 0x205F), RANGE(0x3000, 0x3000) };
static const PcrecSetTerm t_xdigit[] = {
    RANGE('0', '9'), RANGE('A', 'F'), RANGE('a', 'f'),
    RANGE(0xFF10, 0xFF19), RANGE(0xFF21, 0xFF26), RANGE(0xFF41, 0xFF46) };
/* `\p{P}` ∪ (`\p{S}` ∩ ASCII): the nine ASCII symbols $ + < = > ^ ` | ~. */
static const PcrecSetTerm t_punct[] = {
    PROP("P"), RANGE('$', '$'), RANGE('+', '+'), RANGE('<', '>'),
    RANGE('^', '^'), RANGE('`', '`'), RANGE('|', '|'), RANGE('~', '~') };
static const PcrecSetTerm t_graph_not[] = {
    PROP("Z"), PROP("CC"), PROP("CS"), PROP("CO"), PROP("CN"),
    RANGE(0x061C, 0x061C), RANGE(0x180E, 0x180E), RANGE(0x2066, 0x2069) };
static const PcrecSetTerm t_print_not[] = {
    PROP("ZL"), PROP("ZP"), PROP("CC"), PROP("CS"), PROP("CO"), PROP("CN"),
    RANGE(0x061C, 0x061C), RANGE(0x2066, 0x2069) };

SETDEF(pcrec_ucp_set_digit,    "ucp-digit",    false, false, t_nd);
SETDEF(pcrec_ucp_set_space,    "ucp-space",    false, false, t_xsp);
SETDEF(pcrec_ucp_set_pspace,   "ucp-posix-space", false, false, t_xps);
SETDEF(pcrec_ucp_set_word,     "ucp-word",     false, false, t_xwd);
SETDEF(pcrec_ucp_set_alpha,    "ucp-alpha",    false, false, t_l);
SETDEF(pcrec_ucp_set_alnum,    "ucp-alnum",    false, false, t_xan);
SETDEF(pcrec_ucp_set_lower,    "ucp-lower",    false, true,  t_ll);
SETDEF(pcrec_ucp_set_upper,    "ucp-upper",    false, true,  t_lu);
SETDEF(pcrec_ucp_set_cntrl,    "ucp-cntrl",    false, false, t_cc);
SETDEF(pcrec_ucp_set_blank,    "ucp-blank",    false, false, t_blank);
SETDEF(pcrec_ucp_set_xdigit,   "ucp-xdigit",   false, false, t_xdigit);
SETDEF(pcrec_ucp_set_punct,    "ucp-punct",    false, false, t_punct);
SETDEF(pcrec_ucp_set_graph,    "ucp-graph",    true,  false, t_graph_not);
SETDEF(pcrec_ucp_set_print,    "ucp-print",    true,  false, t_print_not);

#undef PROP
#undef RANGE
#undef SETDEF

/* Builds `d` as a code-point set over Unicode, then clamps it to the
 * compile's encoding universe (a set, not a named code point, so clamping is
 * not an error — `pcrec_ast_class_from_iv`'s own rule). */
void pcrec_setdef_build(Ctx *cx, const PcrecSetDef *d, PcrecCpSet *s)
{
    pcrec_cpset_init(s, &cx->arena);
    for (int i = 0; i < d->nterms; i++) {
        const PcrecSetTerm *t = &d->terms[i];
        if (!t->prop) {
            pcrec_cpset_add(s, t->lo, t->hi);
            continue;
        }
        int n = 0;
        const PcrecCpRange *iv = pcrec_uprops_span(t->prop, &n);
        if (!iv)
            pcrec_ctx_fail(cx, cx->pos, "internal error: UCP set '%s' names "
                           "property '%s', which unicode-props does not ship",
                           d->name, t->prop);
        pcrec_cpset_add_set(s, iv, n);
    }
    if (d->complement) pcrec_cpset_complement(s, 0x10FFFFu);
    unsigned uni = pcrec_enc_by_id(cx->opt->encoding)->max_cp;
    if (uni < 0x10FFFFu) pcrec_cpset_remove(s, uni + 1, 0x10FFFFu);
}

/* ---- the ROUTE a built UCP set takes today (D130 Q3) ----------------------
 *
 * A first-match TABLE (§0.1's rule), rows as data. The WIDE sets are refused
 * by name until a kit-sized route exists ([CLS-TREE] S4 for the VM, [UCP] U3
 * for the DFA): accepting them is correct and costs a minute-long compile
 * (`\w+` under UCP utf8: 330 KB, 66 s). "Wide" is a measured fact of the
 * CLAMPED set, not a list of names — so every set under `byte` is narrow, and
 * the partition `tests/ucp` pins is what the limit reproduces. No deny flag:
 * a row whose denial changes whether a pattern compiles is not a form choice. */
typedef struct {
    const char *name;
    const char *applies;
    bool (*pred)(int nintervals);
    bool build;
} UcpRouteRow;

static bool rr_narrow(int n) { return n <= PCREC_UCP_NARROW_MAX_INTERVALS; }
static bool rr_always(int n) { (void)n; return true; }

static const UcpRouteRow route_rows[] = {
    { "narrow", "clamped set has <= PCREC_UCP_NARROW_MAX_INTERVALS intervals",
      rr_narrow, true },
    { "wide",   "always: refused by name until a kit-sized route exists",
      rr_always, false },
};

Ast *pcrec_setdef_class(Ctx *cx, const PcrecSetDef *d, bool negate,
                        const char *construct, char *why, size_t whysz)
{
    PcrecCpSet s;
    pcrec_setdef_build(cx, d, &s);
    const UcpRouteRow *r = NULL;
    for (size_t i = 0; i < sizeof route_rows / sizeof route_rows[0]; i++)
        if (route_rows[i].pred(s.n)) { r = &route_rows[i]; break; }
    if (!r || !r->build) {
        snprintf(why, whysz,
                 "UCP %s is a wide set (%d intervals) and is refused under "
                 "encoding '%s' until a kit-sized class route exists "
                 "([CLS-TREE] S4 / [UCP] U3); restrict it with (?a) or use "
                 "-e byte", construct, s.n,
                 pcrec_enc_by_id(cx->opt->encoding)->name);
        return NULL;
    }
    return pcrec_ast_class_from_cpset(cx, &s, d->fold_inert ? CLS_UCP_SET_INERT
                                                           : CLS_UCP_SET,
                                      negate);
}
