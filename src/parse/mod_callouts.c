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

/* Copies `n` bytes of user text into the arena as a diagnostic echo, with
 * every control byte (ESC, BEL, ...) written as `\xNN` (`pcrec_sb_textn`),
 * so a refusal cannot drive the reader's terminal. */
static const char *co_echo(Ctx *cx, const char *s, size_t n)
{
    StrBuf b = { .cx = cx };
    pcrec_sb_textn(&b, s, n);
    const char *t = pcrec_sb_fragf(&cx->arena, "%s", b.p ? b.p : "");
    pcrec_sb_free(&b);
    return t;
}

/* Applies one attribute list (`attr`, `attr`, ...) to node `a`; `s`/`n` is
 * the list's text with no leading comma, `sep` the separator between items.
 * Returns NULL, or the refusal text. Shared by the string spelling's
 * `,attr` tail and the numbered callout's declarations (`pcrec_callout_
 * apply_attrs`, src/opt/callout.c), so the grammar has one home. Every item
 * is a name, so an empty item is refused wherever it stands (`x,`, `x,,y`,
 * and an empty list, which declares nothing). */
const char *pcrec_callout_attrs(Ctx *cx, Ast *a, const char *s, size_t n,
                                char sep)
{
    bool seen[CO_ATTR_N] = { false };
    size_t i = 0;
    for (;;) {
        size_t j = i;
        while (j < n && s[j] != sep) j++;
        if (j == i)
            return pcrec_ext_msgf(cx, "empty callout attribute (each item "
                                  "of the '%c'-separated list is consume, "
                                  "once or verify)", sep);
        int k = co_attr(s + i, j - i);
        if (k < 0)
            return pcrec_ext_msgf(cx, "unknown callout attribute '%s' "
                                  "(the attributes are consume, once and "
                                  "verify)", co_echo(cx, s + i, j - i));
        if (seen[k])
            return pcrec_ext_msgf(cx, "callout attribute '%s' is repeated",
                                  co_attr_names[k]);
        seen[k] = true;
        switch (k) {
        case CO_ATTR_CONSUME: a->u.callout.consume = true; break;
        case CO_ATTR_ONCE:    a->u.callout.once = true;    break;
        case CO_ATTR_VERIFY:
            /* §4's `verify` mode is stage 4's: refused BY NAME until then.
             * The module named is the SITE's, which is enabled here: a code
             * site's is `code-<lang>`, never `callouts` (review
             * 2026-10-27-r1-ic2 F15: "module 'callouts' is enabled" was
             * false in a compile without it). */
            return a->u.callout.bind == CO_CODE
                ? pcrec_ext_msgf(cx, "module 'code-%s' " PCREC_UNBUILT_MARKER
                                 " the callout attribute 'verify' is not "
                                 "implemented yet", a->u.callout.lang)
                : pcrec_ext_msgf(cx, "module 'callouts' " PCREC_UNBUILT_MARKER
                                 " the callout attribute 'verify' is not "
                                 "implemented yet");
        }
        if (j == n) return NULL;
        i = j + 1;
    }
}

/* Reads one numbered callout's declaration, `N<sep>ATTRS`: N a decimal
 * 0-255, then `sep` (`:` on the command line; one or more spaces or tabs in
 * a `.rxt` `callout` line), then a non-empty comma-separated list of
 * lower-case names. The ONE SHAPE READER of both surfaces (the `.rxt` reader
 * and `--callout`), so the two refuse the same texts; which attributes exist
 * is `pcrec_callout_attrs`' question, asked by the compile. True with `d`
 * filled (`d->attrs` points into `v`), else false. */
bool pcrec_callout_decl_read(const char *v, char sep, PcrecCalloutDecl *d)
{
    int n = 0;
    const char *q = v;
    if (*q < '0' || *q > '9') return false;
    while (*q >= '0' && *q <= '9')
        if ((n = n * 10 + (*q++ - '0')) > 255) return false;
    if (sep == ':') {
        if (*q++ != ':') return false;
    } else {
        if (*q != ' ' && *q != '\t') return false;
        while (*q == ' ' || *q == '\t') q++;
    }
    const char *attrs = q;
    for (bool item = false; ; q++) {
        if (*q >= 'a' && *q <= 'z') { item = true; continue; }
        if ((*q != ',' && *q != '\0') || !item) return false;
        if (*q == '\0') break;
        item = false;
    }
    d->num = n;
    d->attrs = attrs;
    return true;
}

/* THE BINDING ROWS (inline_c.md §1.4), first match on the site's `bind`: the
 * symbol of the site's `rx_callout_ref`, the call's callee expression and the
 * view's `user` expression. Every reader (the call site, the listing, the
 * header's extern list, the artifact's file-local bindings, `--emit-main`'s
 * refusal, the binding-name rule below) takes them from here.
 *
 * ONE CALL FORM (Frank 2026-10-27, "we would be using the same path
 * ourselves"): every row's callee is `<symbol>.fn` and its `user`
 * `<symbol>.user`; the rows differ ONLY in who writes the definition, its
 * name and its linkage:
 *   - `code` (CO_CODE): pcrec writes `static ptrdiff_t <prefix>__code<seg>`
 *     and `static const rx_callout_ref <prefix>__code<seg>_ref = { fn, NULL
 *     }` in the artifact, file-local (`is_extern` false); a generated name,
 *     since C forbids an extern-then-static of one name;
 *   - `named`, `numbered`: `extern const rx_callout_ref rx_callout_<name>`
 *     (`_<n>`), declared by the artifact, defined by the user (D38 §1.1).
 * A definition the compiler can see (same file, or -flto) is called
 * directly and may be inlined; a separately compiled one is an indirect
 * call (match_api.md §11.2). `cx` supplies the arena and the prefix. */
PcrecCalloutBinding pcrec_callout_binding(Ctx *cx, const Ast *a)
{
    Arena *ar = &cx->arena;
    PcrecCalloutBinding b = { NULL, NULL, NULL, false };
    switch (a->u.callout.bind) {
    case CO_CODE:
        b.symbol = pcrec_sb_fragf(ar, "%s__code%d_ref", cx->opt->prefix,
                                  a->u.callout.seg);
        break;
    case CO_NAME:
        b.symbol = pcrec_sb_fragf(ar, "rx_callout_%s", a->u.callout.name);
        b.is_extern = true;
        break;
    case CO_NUM:
        b.symbol = pcrec_sb_fragf(ar, "rx_callout_%d", a->u.callout.num);
        b.is_extern = true;
        break;
    }
    b.callee = pcrec_sb_fragf(ar, "%s.fn", b.symbol);
    b.user = pcrec_sb_fragf(ar, "%s.user", b.symbol);
    return b;
}

/* THE NAMES PCREC ITSELF DECLARES UNPREFIXED in every artifact that a binding
 * symbol shares a translation unit with: the shared ABI block's fixed
 * identifiers (match_api.md §1¶5, types and the iterator's helpers). A binding
 * symbol equal to one of them redeclares it and the artifact does not compile
 * (`(?C"ref")` binds `rx_callout_ref`, the typedef), so the rule is general:
 * a binding whose symbol is a name on this list is refused. Only the
 * `rx_callout_` members can match today (the binding family is
 * `rx_callout_<ident>`); the list is the whole block so a new fixed name in
 * the family is refused by adding it here. tests/callouts arm 6 reads the
 * family members off an emitted header rather than off this table. */
static const char *const co_abi_names[] = {
    "rx_var", "rx_ctx", "rx_matchfn", "rx_callout_ref", "rx_renderfn",
    "rx_group_entry", "rx_nextfn", "rx_nextnfn", "rx_info", "rx_iter",
    "rx_iter_init", "rx_iter_at", "rx_iter_vars",
};

static bool co_abi_name(const char *sym)
{
    for (size_t i = 0; i < sizeof co_abi_names / sizeof co_abi_names[0]; i++)
        if (!strcmp(sym, co_abi_names[i])) return true;
    return false;
}

/* Does this tree contain a callout site? The kind mask's `PF_KIND_CALLOUT`
 * (src/facts/kinds.c), asked at the root by the prefilter admission's
 * `callout` row (src/opt/select_engine.c). */
static void co_has_visit(void *ud, const Ast *a)
{
    if (a->k == A_CALLOUT) *(bool *)ud = true;
}

bool pcrec_has_callout(const Ast *root)
{
    bool found = false;
    if (root) pcrec_ast_visit(root, co_has_visit, &found);
    return found;
}

ExtResult pcrec_coport_callout(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from)
{
    const char *p = cx->pat;
    PcrecCoScan sc;
    /* The recogniser that elected this row ran the same scan on the same
     * text (a pattern ending at `(?C` elects the malformed row), so this
     * refusal is a guard, not a path. */
    if (from >= cx->patlen ||
        !pcrec_callout_extent_scan(p + from, cx->patlen - from, &sc))
        REFUSE(at, "internal error: the callout row was elected for a "
               "malformed (?C");

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
        /* A tagged-code string (`lang attrs ":"` with a registered `lang`,
         * §2.2) is module `code-<lang>`'s row, which outranks this one on
         * exactly that text; what reaches here is a binding or nothing. */
        if (id == 0 || (id < n && dec[id] != ','))
            REFUSE(at, "a (?C\"...\") string is a binding name (a C "
                   "identifier, with optional ,consume ,once ,verify) or "
                   "tagged code (c: ...)");
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
    const char *sym = pcrec_callout_binding(cx, a).symbol;
    if (co_abi_name(sym))
        REFUSE(at, "callout binding %s is a name the artifact's shared ABI "
               "block already declares; choose another name", sym);
    pcrec_ast_stamp(a, rw, at);
    cx->ncallouts++;

    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = a;
    res.end = from + sc.end;
    return res;
}
