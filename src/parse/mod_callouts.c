/* mod_callouts.c — module `callouts` ([INLINE-C] stage 1b, [M4-CALLOUTS]
 * step 2): the `(?C` port.
 *
 * Design: docs/design/inline_c.md §1 (the call site) and §2 (the spellings
 * and the attribute grammar), paneled r1 and ruled; D36/D38 (the callout ABI).
 *
 * WHAT A CALLOUT IS, in one sentence: at the site, the engine calls an
 * `rx_matchfn` the user defines (`rx_callout_<n>` for a numbered callout,
 * `rx_callout_<name>` for a named one) with a read-only view of the subject,
 * the position and every group, and the return decides the path: `0` passes,
 * `-1` fails it, a length consumes (a `consume` site only), a code propagates
 * or traps (the return table, src/gen/callsite_rows.h).
 *
 * THE SPELLINGS, all PCRE2's: `(?C)` (number 0), `(?Cn)` (n 0..255), and
 * `(?C` + a string in one of the eight delimiters + `)`. Their SHAPE is
 * `pcrec_callout_extent_scan`'s (src/parse/scans.c), which the row's
 * recogniser also reads, so a text this port sees is well-formed by
 * construction; a malformed `(?C` never reaches here (its own REJECTED row).
 *
 * THE STRING IS A BINDING NAME plus attributes (§2.2): `ident(,attr)*`, with
 * `ident` a C identifier containing no `__` (the namespace table's row: it
 * keeps `rx_callout_<name>` clear of a `<prefix>__<role>` symbol and of the
 * PCRE2 wrapper's helpers) and `attr` one of `consume`, `once`, `verify`.
 * A NUMBERED callout has no string, so its attributes arrive from the `.rxt`
 * `callout` line or `--callout N:attrs` and are applied by the post-parse
 * pass (src/opt/callout.c), which also decides where a site may stand.
 *
 * NOT QUANTIFIABLE. PCRE2 refuses a quantifier after a callout (error 109,
 * measured `(?C1)?`, `(?C1)*`, `a(?C1){2}`), and so does pcrec: the node is
 * `not_repeatable`, the flag p_rep already reads. `(?:(?C1))*` is a group
 * and repeatable, as in PCRE2. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

/* An attribute name of §2.2's v1 set, or -1. */
enum { CO_ATTR_CONSUME, CO_ATTR_ONCE, CO_ATTR_VERIFY, CO_ATTR_N };
static const char *const co_attr_names[CO_ATTR_N] = {
    "consume", "once", "verify"
};

static int co_attr(const char *s, size_t n)
{
    for (int i = 0; i < CO_ATTR_N; i++)
        if (strlen(co_attr_names[i]) == n && !memcmp(co_attr_names[i], s, n))
            return i;
    return -1;
}

static bool co_ident_start(char c)
{
    return c == '_' || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

static bool co_ident_cont(char c)
{
    return co_ident_start(c) || (c >= '0' && c <= '9');
}

/* Applies one attribute list (`attr`, `attr`, ...) to node `a`; `s`/`n` is
 * the list's text with no leading comma, `sep` the separator between items.
 * Returns NULL, or the refusal text. Shared by the string spelling's
 * `,attr` tail and the numbered callout's declarations (`pcrec_callout_
 * apply_attrs`, src/opt/callout.c), so the grammar has one home. */
const char *pcrec_callout_attrs(Ctx *cx, Ast *a, const char *s, size_t n,
                                char sep)
{
    bool seen[CO_ATTR_N] = { false };
    size_t i = 0;
    while (i < n) {
        size_t j = i;
        while (j < n && s[j] != sep) j++;
        int k = co_attr(s + i, j - i);
        if (k < 0)
            return pcrec_ext_msgf(cx, "unknown callout attribute '%.*s' "
                                  "(the attributes are consume, once and "
                                  "verify)", (int)(j - i), s + i);
        if (seen[k])
            return pcrec_ext_msgf(cx, "callout attribute '%s' is repeated",
                                  co_attr_names[k]);
        seen[k] = true;
        switch (k) {
        case CO_ATTR_CONSUME: a->u.callout.consume = true; break;
        case CO_ATTR_ONCE:    a->u.callout.once = true;    break;
        case CO_ATTR_VERIFY:
            /* §4's `verify` mode is stage 4's: refused BY NAME until then. */
            return pcrec_ext_msgf(cx, "module 'callouts' " PCREC_UNBUILT_MARKER
                                  " the callout attribute 'verify' is not "
                                  "implemented yet");
        }
        i = j < n ? j + 1 : j;
        if (j < n && i == n)
            return pcrec_ext_msgf(cx, "empty callout attribute after '%c'",
                                  sep);
    }
    return NULL;
}

ExtResult pcrec_coport_callout(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from)
{
    const char *p = cx->pat;
    PcrecCoScan sc;
    /* The recogniser that elected this row ran the same scan on the same
     * text, so a false here is a registry/doorway defect, not a pattern
     * error. */
    if (from > cx->patlen ||
        !pcrec_callout_extent_scan(p + from, cx->patlen - from, &sc))
        REFUSE(at, "internal error: the (?C port was reached on a text its "
               "row's recogniser does not answer for");

    Ast *a = pcrec_ast_node(cx, A_CALLOUT);
    a->not_repeatable = true;
    a->u.callout.at = at;
    if (!sc.string) {
        a->u.callout.bind = CO_NUM;
        a->u.callout.num = sc.num;
    } else {
        /* Decode: a doubled closing delimiter is one literal byte (PCRE2's
         * rule, §2.3). The decoded text is what the grammar reads. */
        const char *raw = p + from + sc.str;
        char *dec = pcrec_arena_alloc(&cx->arena, sc.rawlen + 1);
        size_t n = 0;
        for (size_t i = 0; i < sc.rawlen; i++) {
            dec[n++] = raw[i];
            if (raw[i] == sc.close) i++;
        }
        dec[n] = 0;

        size_t id = 0;
        if (n > 0 && co_ident_start(dec[0]))
            while (id < n && co_ident_cont(dec[id])) id++;
        /* A tagged-code string (`lang attrs ":"`, §2.2) is stage 2's module
         * `code-c`; until it exists the grammar has one reading here. */
        if (id == 0 || (id < n && dec[id] != ','))
            REFUSE(at, "a (?C\"...\") string is a binding name (a C "
                   "identifier, with optional ,consume ,once ,verify); "
                   "tagged code (c: ...) is not supported yet");
        /* The namespace table's binding row (cli.md §1.17, inline_c.md
         * §1.4): `__` is the `<prefix>__<role>` separator and the PCRE2
         * wrapper's helper namespace, so no binding name may hold it. */
        bool dunder = false;
        for (size_t i = 0; i + 1 < id; i++)
            if (dec[i] == '_' && dec[i + 1] == '_') dunder = true;
        if (dunder)
            REFUSE(at, "callout binding name '%.*s' contains '__', which is "
                   "reserved (rx_callout_<name> must not collide with a "
                   "<prefix>__<role> symbol)", (int)id, dec);
        dec[id] = 0;
        a->u.callout.bind = CO_NAME;
        a->u.callout.name = dec;
        if (id < n) {
            const char *msg = pcrec_callout_attrs(cx, a, dec + id + 1,
                                                  n - id - 1, ',');
            if (msg) REFUSE(at, "%s", msg);
        }
    }
    pcrec_ast_stamp(a, rw, at);
    cx->ncallouts++;

    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = a;
    res.end = from + sc.end;
    return res;
}
