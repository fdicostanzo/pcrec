/* emit_code.c — [INLINE-C] stage 2: the C text an embedded code segment
 * becomes (docs/design/inline_c.md §3; contract docs/spec/match_api.md
 * §11.9 and §11.10).
 *
 * Three pieces, each written by one function here and called by the engine
 * emitter or the driver at the one place the layout puts it:
 *
 *   - the SPAN HELPERS (`rx_span`, `rx_eq` ...), a guarded fixed-literal
 *     block in every callout artifact's caller-facing surface, beside
 *     `RX_PASS`/`RX_FAIL`, so a hand-written binding has them as much as a
 *     segment does (`pcrec_emit_span_helpers`);
 *   - per segment, the generated function's PROTOTYPE and its file-local
 *     binding `static const rx_callout_ref <prefix>__code<seg>_ref`, before
 *     the VM function: the site calls `<binding>.fn(&ctx)`, the ONE call
 *     form (Frank 2026-10-27), and gcc sees the definition, so the call is
 *     direct and inlinable (`pcrec_emit_code_protos`);
 *   - the SEGMENT BLOCK, LAST in the `.c` (§3.1): the `#undef` of every
 *     artifact-internal macro still live, the `code-header` includes, then
 *     per segment its macro set, its function (the user's text under
 *     `#line`) and the macro set's `#undef` (`pcrec_emit_code_block`).
 *
 * pcrec never reads the user's text beyond copying it: no parse, no check,
 * no substitution (Q7). The text arrives decoded (`mod_code.c`). */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* THE SPAN HELPERS, one text. `static inline` in a block guarded by
 * PCREC_RX_SPAN_H, so two callout artifacts in one translation unit define
 * them once and an unused one costs nothing. Every helper reads an UNSET
 * span (p NULL, len -1: an unset group) as matching nothing. The contracts
 * are match_api.md §11.10's table, one row per helper. */
static const char span_helpers[] =
    "#ifndef PCREC_RX_SPAN_H\n"
    "#define PCREC_RX_SPAN_H\n"
    "typedef struct rx_span { const unsigned char *p; ptrdiff_t len; } rx_span;\n"
    "static inline int rx_eq(rx_span s, const char *z)\n"
    "{\n"
    "    if (!s.p || s.len < 0) return 0;\n"
    "    for (ptrdiff_t i = 0; i < s.len; i++)\n"
    "        if (!z[i] || (unsigned char)z[i] != s.p[i]) return 0;\n"
    "    return z[s.len] == 0;\n"
    "}\n"
    "static inline int rx_eqi(rx_span s, const char *z)\n"
    "{\n"
    "    if (!s.p || s.len < 0) return 0;\n"
    "    for (ptrdiff_t i = 0; i < s.len; i++) {\n"
    "        unsigned a = s.p[i], b = (unsigned char)z[i];\n"
    "        if (!b) return 0;\n"
    "        if (a - 'A' < 26u) a += 32;\n"
    "        if (b - 'A' < 26u) b += 32;\n"
    "        if (a != b) return 0;\n"
    "    }\n"
    "    return z[s.len] == 0;\n"
    "}\n"
    "static inline int rx_u64(rx_span s, uint64_t *out)\n"
    "{\n"
    "    uint64_t v = 0;\n"
    "    if (!s.p || s.len <= 0) return 0;\n"
    "    for (ptrdiff_t i = 0; i < s.len; i++) {\n"
    "        unsigned d = (unsigned)s.p[i] - '0';\n"
    "        if (d > 9 || v > (UINT64_MAX - d) / 10) return 0;\n"
    "        v = v * 10 + d;\n"
    "    }\n"
    "    *out = v;\n"
    "    return 1;\n"
    "}\n"
    "static inline int rx_hex(rx_span s, uint64_t *out)\n"
    "{\n"
    "    uint64_t v = 0;\n"
    "    if (!s.p || s.len <= 0) return 0;\n"
    "    for (ptrdiff_t i = 0; i < s.len; i++) {\n"
    "        unsigned c = s.p[i], d;\n"
    "        if (c - '0' < 10u) d = c - '0';\n"
    "        else if ((c | 32u) - 'a' < 6u) d = (c | 32u) - 'a' + 10;\n"
    "        else return 0;\n"
    "        if (v >> 60) return 0;\n"
    "        v = v << 4 | d;\n"
    "    }\n"
    "    *out = v;\n"
    "    return 1;\n"
    "}\n"
    "static inline int rx_in(rx_span s, uint64_t lo, uint64_t hi)\n"
    "{\n"
    "    uint64_t v;\n"
    "    return rx_u64(s, &v) && v >= lo && v <= hi;\n"
    "}\n"
    "static inline ptrdiff_t rx_find(rx_span s, const char *z)\n"
    "{\n"
    "    ptrdiff_t n = 0;\n"
    "    if (!s.p || s.len < 0) return -1;\n"
    "    while (z[n]) n++;\n"
    "    for (ptrdiff_t i = 0; i + n <= s.len; i++) {\n"
    "        ptrdiff_t k = 0;\n"
    "        while (k < n && s.p[i + k] == (unsigned char)z[k]) k++;\n"
    "        if (k == n) return i;\n"
    "    }\n"
    "    return -1;\n"
    "}\n"
    "static inline int rx_u8next(rx_span s, ptrdiff_t *i, uint32_t *cp)\n"
    "{\n"
    "    ptrdiff_t k = *i, n, j;\n"
    "    uint32_t c, min;\n"
    "    if (!s.p || k < 0 || k >= s.len) return 0;\n"
    "    c = s.p[k];\n"
    "    if (c < 0x80) { *cp = c; *i = k + 1; return 1; }\n"
    "    if (c >= 0xC2 && c <= 0xDF) { n = 2; c &= 0x1F; min = 0x80; }\n"
    "    else if (c >= 0xE0 && c <= 0xEF) { n = 3; c &= 0x0F; min = 0x800; }\n"
    "    else if (c >= 0xF0 && c <= 0xF4) { n = 4; c &= 0x07; min = 0x10000; }\n"
    "    else return -1;\n"
    "    if (s.len - k < n) return -1;\n"
    "    for (j = 1; j < n; j++) {\n"
    "        uint32_t t = s.p[k + j];\n"
    "        if ((t & 0xC0) != 0x80) return -1;\n"
    "        c = c << 6 | (t & 0x3F);\n"
    "    }\n"
    "    if (c < min || c > 0x10FFFF || (c >= 0xD800 && c <= 0xDFFF)) return -1;\n"
    "    *cp = c;\n"
    "    *i = k + n;\n"
    "    return (int)n;\n"
    "}\n"
    "#endif\n";

void pcrec_emit_span_helpers(StrBuf *sb)
{
    pcrec_sb_puts(sb, span_helpers);
}

/* The segment's generated function name, `<prefix>__code<seg>` (§3.1), the
 * binding row's symbol without its `_ref`. */
static const char *code_fn(Ctx *cx, const Ast *a)
{
    return pcrec_sb_fragf(&cx->arena, "%s__code%d", cx->opt->prefix,
                          a->u.callout.seg);
}

void pcrec_emit_code_protos(Ctx *cx, StrBuf *c)
{
    for (int i = 1; i <= cx->ncallouts; i++) {
        const Ast *a = cx->callout_nodes[i];
        if (a->u.callout.bind != CO_CODE) continue;
        const char *fn = code_fn(cx, a);
        const PcrecCalloutBinding b = pcrec_callout_binding(cx, a);
        pcrec_sb_printf(c, "static ptrdiff_t %s(const rx_ctx *ctx);\n"
                           "%sstatic const rx_callout_ref %s = { %s, NULL };\n",
                        fn, pcrec_attr_text(PCREC_ATTR_UNUSED), b.symbol, fn);
    }
}

/* THE PUBLIC CONTRACT AT THE SEGMENT BLOCK (§3.2 "what is live"), first
 * match on a live macro's name: a row that KEEPS it, or the default, which
 * `#undef`s it. Kept: the stamps (the upper prefix's family, match_api.md
 * §6.3), the shared ABI block's and the feature block's `PCREC_` names, the
 * callout family's return names, the iterator initializer, and the
 * compiler-feature shim. `exact` false: the row is a name PREFIX. */
typedef struct { const char *name; bool exact; } CodeKeep;
static const CodeKeep code_keep[] = {
    { "\x01Q_",           false },   /* <PREFIX>_* stamps */
    { "PCREC_",           false },
    { "RX_PASS",          true  },
    { "RX_FAIL",          true  },
    { "RX_ITER_INIT",     true  },
    { "__has_attribute",  true  },
};

/* Is the macro `name` (len bytes) part of the public contract? */
static bool code_keep_name(const char *name, size_t len)
{
    for (size_t r = 0; r < sizeof code_keep / sizeof code_keep[0]; r++) {
        const size_t kl = strlen(code_keep[r].name);
        if (code_keep[r].exact ? (len == kl && !memcmp(name, code_keep[r].name, kl))
                               : (len >= kl && !memcmp(name, code_keep[r].name, kl)))
            return true;
    }
    return false;
}

/* Is `c` a byte of a C identifier, with the prefix placeholder's lead? */
static bool code_ident_byte(unsigned char c)
{
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
           (c >= '0' && c <= '9') || c == '_' || c == (unsigned char)PCREC_PREFIX_LEAD;
}

/* Writes `#undef NAME` for every macro `#define`d and not `#undef`ed in
 * `c`'s finished text that the public contract does not keep, in first-
 * definition order. Reads the emitted text, so a macro a later emitter adds
 * is covered with no list to maintain. */
static void code_undef_live(Ctx *cx, StrBuf *c)
{
    typedef struct { const char *p; size_t n; bool live; } Mac;
    Mac *mac = NULL;
    size_t nmac = 0, cap = 0;
    const char *s = c->p ? c->p : "";
    const char *end = s + c->len;
    for (const char *l = s; l < end;) {
        const char *nl = memchr(l, '\n', (size_t)(end - l));
        const char *le = nl ? nl : end;
        const char *q = l;
        while (q < le && (*q == ' ' || *q == '\t')) q++;
        if (q < le && *q == '#') {
            q++;
            while (q < le && (*q == ' ' || *q == '\t')) q++;
            int def = (le - q > 6 && !memcmp(q, "define", 6)) ? 6 :
                      (le - q > 5 && !memcmp(q, "undef", 5)) ? 5 : 0;
            if (def) {
                q += def;
                while (q < le && (*q == ' ' || *q == '\t')) q++;
                const char *nm = q;
                while (q < le && code_ident_byte((unsigned char)*q)) q++;
                const size_t n = (size_t)(q - nm);
                size_t k = 0;
                while (k < nmac && !(mac[k].n == n && !memcmp(mac[k].p, nm, n))) k++;
                if (k == nmac && n) {
                    if (nmac == cap) {
                        size_t nc = cap ? cap * 2 : 64;
                        Mac *m = pcrec_arena_alloc(&cx->arena, nc * sizeof *m);
                        if (nmac) memcpy(m, mac, nmac * sizeof *m);
                        mac = m;
                        cap = nc;
                    }
                    mac[nmac++] = (Mac){ nm, n, false };
                }
                if (n) mac[k].live = def == 6;
            }
        }
        l = nl ? nl + 1 : end;
    }
    for (size_t k = 0; k < nmac; k++)
        if (mac[k].live && !code_keep_name(mac[k].p, mac[k].n))
            pcrec_sb_printf(c, "#undef %.*s\n", (int)mac[k].n, mac[k].p);
}

/* Is a named group's NAME one the macro set spells as `RX_G_<name>`: ASCII
 * identifier bytes only (§3.2: no macro for a non-ASCII name or a name
 * containing `.`)? */
static bool code_gname_ok(const char *n)
{
    for (; *n; n++)
        if (!(((unsigned char)*n < 0x80) && code_ident_byte((unsigned char)*n)))
            return false;
    return true;
}

static int code_ng_cmp(const void *x, const void *y)
{
    const NamedGroup *a = *(const NamedGroup *const *)x;
    const NamedGroup *b = *(const NamedGroup *const *)y;
    int r = strcmp(a->name, b->name);
    return r ? r : (a->number > b->number) - (a->number < b->number);
}

/* THE MACRO SET (§3.2), `#define`d before a segment's function; `set` true,
 * or its `#undef` list after it. Every accessor taking `n` evaluates it once
 * (a statement expression) and is guarded: an unset or out-of-range group
 * reads -1 / NULL. `RX_G_<name>` for every caller-scope ASCII group name: a
 * name one group has is its number; a name several groups share is the
 * first member, in number order, that is set at this fire, else the first
 * (match_api.md §5.4¶6's walk). */
static void code_macros(Ctx *cx, StrBuf *c, bool set)
{
    static const char *const fixed[] = {
        "RX_SUBJ", "RX_LEN", "RX_POS", "RX_START", "RX_CAP_SET", "RX_CAP_S",
        "RX_CAP_E", "RX_CAP_LEN", "RX_CAP_P", "RX_CAP", "RX_USER",
    };
    if (!set) {
        for (size_t i = 0; i < sizeof fixed / sizeof fixed[0]; i++)
            pcrec_sb_printf(c, "#undef %s\n", fixed[i]);
    } else {
        pcrec_sb_puts(c,
            "#define RX_SUBJ (ctx->subject)\n"
            "#define RX_LEN (ctx->len)\n"
            "#define RX_POS (ctx->pos)\n"
            "#define RX_START (ctx->caps[0][0])\n"
            "#define RX_CAP_SET(n) __extension__ ({ size_t rx__n = (size_t)(n); "
            "rx__n >= 1 && rx__n < ctx->ncap && ctx->caps[rx__n][1] >= 0; })\n"
            "#define RX_CAP_S(n) __extension__ ({ size_t rx__n = (size_t)(n); "
            "rx__n >= 1 && rx__n < ctx->ncap && ctx->caps[rx__n][1] >= 0 "
            "? ctx->caps[rx__n][0] : (ptrdiff_t)-1; })\n"
            "#define RX_CAP_E(n) __extension__ ({ size_t rx__n = (size_t)(n); "
            "rx__n >= 1 && rx__n < ctx->ncap && ctx->caps[rx__n][1] >= 0 "
            "? ctx->caps[rx__n][1] : (ptrdiff_t)-1; })\n"
            "#define RX_CAP_LEN(n) __extension__ ({ size_t rx__n = (size_t)(n); "
            "rx__n >= 1 && rx__n < ctx->ncap && ctx->caps[rx__n][1] >= 0 "
            "? ctx->caps[rx__n][1] - ctx->caps[rx__n][0] : (ptrdiff_t)-1; })\n"
            "#define RX_CAP_P(n) __extension__ ({ size_t rx__n = (size_t)(n); "
            "rx__n >= 1 && rx__n < ctx->ncap && ctx->caps[rx__n][1] >= 0 "
            "? ctx->subject + ctx->caps[rx__n][0] : (const unsigned char *)0; })\n"
            "#define RX_CAP(n) __extension__ ({ size_t rx__n = (size_t)(n); "
            "rx__n >= 1 && rx__n < ctx->ncap && ctx->caps[rx__n][1] >= 0 "
            "? (rx_span){ ctx->subject + ctx->caps[rx__n][0], "
            "ctx->caps[rx__n][1] - ctx->caps[rx__n][0] } "
            ": (rx_span){ (const unsigned char *)0, -1 }; })\n"
            "#define RX_USER (ctx->user)\n");
    }

    /* The caller-scope names, sorted (name, number): a run per name. */
    unsigned n = 0;
    for (const NamedGroup *g = cx->named_groups; g; g = g->next)
        if (!g->site_scoped && !g->scope && code_gname_ok(g->name)) n++;
    if (!n) return;
    const NamedGroup **v = pcrec_arena_alloc(&cx->arena, n * sizeof *v);
    n = 0;
    for (const NamedGroup *g = cx->named_groups; g; g = g->next)
        if (!g->site_scoped && !g->scope && code_gname_ok(g->name)) v[n++] = g;
    qsort(v, n, sizeof *v, code_ng_cmp);
    for (unsigned i = 0; i < n;) {
        unsigned j = i + 1;
        while (j < n && !strcmp(v[j]->name, v[i]->name)) j++;
        if (!set)
            pcrec_sb_printf(c, "#undef RX_G_%s\n", v[i]->name);
        else if (j - i == 1)
            pcrec_sb_printf(c, "#define RX_G_%s %d\n", v[i]->name, v[i]->number);
        else {
            pcrec_sb_printf(c, "#define RX_G_%s __extension__ ({ int rx__g = %d; ",
                            v[i]->name, v[i]->number);
            for (unsigned k = j; k-- > i;)
                pcrec_sb_printf(c, "if ((size_t)%d < ctx->ncap && "
                                   "ctx->caps[%d][1] >= 0) rx__g = %d; ",
                                v[k]->number, v[k]->number, v[k]->number);
            pcrec_sb_puts(c, "rx__g; })\n");
        }
        i = j;
    }
}

/* One segment's `#line` (§3.1, §3.4): the source as written, through the
 * C-text escaper. */
static void code_line_dir(StrBuf *c, size_t line, const char *file)
{
    pcrec_sb_printf(c, "#line %zu \"", line);
    pcrec_sb_ctext(c, (const unsigned char *)file, strlen(file),
                   PCREC_CTEXT_STRING);
    pcrec_sb_puts(c, "\"\n");
}

/* One segment: its comment, its macro set, its function, the set's undef. */
static void code_segment(Ctx *cx, StrBuf *c, const Ast *a)
{
    const PcrecEmitIn *in = cx->emit_in;
    const char *file = in && in->code_file ? in->code_file : "<pattern>";
    const bool esc = in && in->code_esc;
    const size_t at = a->u.callout.code_at;

    /* The segment's first byte, as a source position: the pattern's own
     * lines below its first (a `pattern-esc` value is ONE source line). */
    size_t line = in && in->code_line ? in->code_line : 1;
    size_t col = in ? in->code_col : 1;
    size_t bol = 0;
    if (!esc)
        for (size_t i = 0; i < at; i++)
            if (cx->pat[i] == '\n') { line++; bol = i + 1; }
    if (bol > 0) col = 1;
    bool pad = !esc && a->u.callout.code_exact && col > 0;
    for (size_t i = bol; pad && i < at; i++)
        if (cx->pat[i] == '\t' || (unsigned char)cx->pat[i] >= 0x80) pad = false;
    if (pad) col += at - bol;

    pcrec_sb_putc(c, '\n');
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_printf(c, "/* code segment %d (%s): ", a->u.callout.seg,
                    a->u.callout.lang);
    pcrec_sb_ctext(c, (const unsigned char *)file, strlen(file),
                   PCREC_CTEXT_COMMENT);
    if (pad) pcrec_sb_printf(c, " line %zu, column %zu */\n", line, col);
    else     pcrec_sb_printf(c, " line %zu */\n", line);
    pcrec_sb_cmt_close(c);
    code_macros(cx, c, true);
    pcrec_sb_printf(c, "static ptrdiff_t %s(const rx_ctx *ctx)\n{\n(void)ctx;\n",
                    code_fn(cx, a));

    const char *t = a->u.callout.text;
    const size_t tn = a->u.callout.textlen;
    if (!esc) {
        code_line_dir(c, line, file);
        for (size_t i = 1; pad && i < col; i++) pcrec_sb_putc(c, ' ');
        pcrec_sb_printf(c, "%.*s", (int)tn, t);
    } else {
        /* Every decoded line maps to the opener's line; no column. */
        for (size_t i = 0; i < tn;) {
            const char *nl = memchr(t + i, '\n', tn - i);
            const size_t e = nl ? (size_t)(nl - t) : tn;
            code_line_dir(c, line, file);
            pcrec_sb_printf(c, "%.*s", (int)(e - i), t + i);
            if (nl) pcrec_sb_putc(c, '\n');
            i = e + (nl ? 1 : 0);
        }
    }
    pcrec_sb_puts(c, "\n__builtin_trap(); }\n");
    code_macros(cx, c, false);
}

void pcrec_emit_code_block(Ctx *cx, StrBuf *c)
{
    const PcrecEmitIn *in = cx->emit_in;
    const int nh = in ? in->ncode_headers : 0;
    if (cx->ncodesegs == 0 && nh == 0) return;

    pcrec_sb_putc(c, '\n');
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(c,
        "/* [INLINE-C] the pattern's embedded code (match_api.md section 11.9):\n"
        " * the matcher's own macros end here, then the code-header lines, then\n"
        " * one function per code segment, its text as written. */\n");
    pcrec_sb_cmt_close(c);
    code_undef_live(cx, c);
    for (int i = 0; i < nh; i++) {
        bool dup = false;
        for (int j = 0; j < i; j++)
            dup |= !strcmp(in->code_headers[j].header, in->code_headers[i].header);
        if (dup) continue;
        if (in->code_headers[i].line && in->code_file)
            code_line_dir(c, in->code_headers[i].line, in->code_file);
        pcrec_sb_printf(c, "#include %s\n", in->code_headers[i].header);
    }
    for (int s = 1; s <= cx->ncodesegs; s++)
        for (int i = 1; i <= cx->ncallouts; i++) {
            const Ast *a = cx->callout_nodes[i];
            if (a->u.callout.bind == CO_CODE && a->u.callout.seg == s)
                code_segment(cx, c, a);
        }
}
