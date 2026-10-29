/* callouts_dump.c — [INLINE-C] stage 3 THE REVIEWER'S VIEW, `pcrec
 * --list-callouts FILE` (docs/design/inline_c.md §5.6; contract
 * docs/spec/cli.md).
 *
 * One row per callout site of a target: where it is, who it calls, how
 * often it can fire, whether its code would be trusted and through which
 * lines, and the code itself, escaped. A projection of what the compile
 * already decided — the sites pass's numbering and firing class, the code
 * port's trust verdict, the reach graph's chains — never a second
 * derivation of any of them.
 *
 * IT READS CODE BEFORE IT IS TRUSTED. The compile runs as a DESCRIBE entry
 * (every language opened, no grant needed) and as a REVIEW compile
 * (`PcrecEmitIn.code_review`): a refused character and an unpinned chain
 * are recorded on the site and printed, never raised. The C is thrown away;
 * nothing a review compile emits leaves this file. */
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "pcrec.h"

static const char *const lc_cols[] = {
    "target", "site", "source", "binding", "symbol", "lang", "width",
    "class", "class_reason", "trust", "chain", "flag", "code",
};
#define LC_NCOLS (sizeof lc_cols / sizeof *lc_cols)

/* The binding row's listing token (inline_c.md §1.4). */
static const char *lc_bind_name(int bind)
{
    switch ((CalloutBind)bind) {
    case CO_CODE: return "code";
    case CO_NAME: return "named";
    case CO_NUM:  return "numbered";
    }
    return "?";
}

/* `s[0..n)` for a reader: printable ASCII as is, a backslash doubled, every
 * other byte `\xNN` (§5.6's escaper: what the reader sees is byte for byte
 * what gcc compiles). */
static const char *lc_escape(Arena *a, const char *s, size_t n)
{
    char *o = pcrec_arena_alloc(a, 4 * n + 1), *w = o;
    for (size_t i = 0; i < n; i++) {
        const unsigned char c = (unsigned char)s[i];
        if (c == '\\') { *w++ = '\\'; *w++ = '\\'; }
        else if (c >= 0x20 && c < 0x7f) *w++ = (char)c;
        else {
            static const char hex[] = "0123456789abcdef";
            *w++ = '\\'; *w++ = 'x'; *w++ = hex[c >> 4]; *w++ = hex[c & 15];
        }
    }
    *w = 0;
    return o;
}

/* A reached segment's chain of lines from the local file, root first: each
 * line as `FILE:LINE KIND "PATH"` and its pin or `unpinned`, joined by
 * ` > `. */
static const char *lc_chain(Ctx *cx, const Ast *a)
{
    const RxtReach *g = a->u.callout.reach;
    if (!g) return "-";
    const RxtReachEdge *path[64];
    const size_t n = pcrec_rxt_reach_chain(g, a->u.callout.reach_real, path,
                                           sizeof path / sizeof *path);
    StrBuf sb = { 0 };
    for (size_t i = 0; i < n; i++)
        pcrec_sb_printf(&sb, "%s%s:%zu %s %s %s%s", i ? " > " : "",
                        path[i]->from, path[i]->line, path[i]->kind,
                        path[i]->to, path[i]->pin ? "sha256 " : "unpinned",
                        path[i]->pin ? path[i]->pin : "");
    const char *out = pcrec_sb_fragf(&cx->arena, "%s", sb.p ? sb.p : "-");
    pcrec_sb_free(&sb);
    return out;
}

typedef struct {
    StrBuf      rows;
    const char *target;
} LcRows;

/* THE HOOK the driver calls on the final attempt's success path: one row
 * per site, in site order. */
static void lc_hook(Ctx *cx, const char *artifact, size_t len, void *ud)
{
    (void)artifact; (void)len;
    LcRows *r = ud;
    for (int i = 1; i <= cx->ncallouts; i++) {
        const Ast *a = cx->callout_nodes[i];
        const bool code = a->u.callout.bind == CO_CODE;
        const char *src = "-";
        if (code) {
            size_t line, col;
            const char *file = pcrec_code_source_pos(a, &line, &col);
            src = col ? pcrec_sb_fragf(&cx->arena, "%s:%zu:%zu", file, line, col)
                      : pcrec_sb_fragf(&cx->arena, "%s:%zu", file, line);
        }
        const char *cells[LC_NCOLS] = {
            r->target,
            pcrec_sb_fragf(&cx->arena, "%d", a->u.callout.site),
            src,
            lc_bind_name(a->u.callout.bind),
            pcrec_callout_binding(cx, a).symbol,
            code ? a->u.callout.lang : "-",
            a->u.callout.consume ? "consume" : "check",
            pcrec_callout_class_name(a->u.callout.fclass),
            a->u.callout.why ? a->u.callout.why : "-",
            code ? a->u.callout.trust : "-",
            code ? lc_chain(cx, a) : "-",
            a->u.callout.flag ? a->u.callout.flag : "-",
            code ? lc_escape(&cx->arena, a->u.callout.text,
                             a->u.callout.textlen)
                 : "-",
        };
        pcrec_sb_row(&r->rows, cells, LC_NCOLS);
    }
}

const char *pcrec_list_callouts_header(void)
{
    return "# pcrec --list-callouts: one row per callout site of each target, "
           "in site order\n"
           "# (docs/spec/cli.md). `trust` is what a build with the grant "
           "would do with the\n"
           "# site's code; `code` is its text with every byte outside "
           "printable ASCII as \\xNN.\n"
           "#target\tsite\tsource\tbinding\tsymbol\tlang\twidth\tclass"
           "\tclass_reason\ttrust\tchain\tflag\tcode\n";
}

char *pcrec_list_callouts(const char *pattern, const pcrec_options *opt,
                          const RxtDefs *defs, const PcrecEmitIn *in,
                          const char *target, pcrec_error *err)
{
    pcrec_options defo;
    pcrec_output out;
    LcRows r = { { 0 }, target };

    pcrec_default_options(&defo);
    if (opt) defo = *opt;
    defo.header_name = NULL;
    /* A REVIEW compile (§5.6). The DESCRIBE grant is the caller's: the
     * CLI's mode table gives it to this entry by its class column (F27). */
    PcrecEmitIn rin = { .bound = PCREC_PB_UNSTATED };
    if (in) rin = *in;
    rin.code_review = true;

    if (pcrec_compile_driver(pattern, &defo, &out, err, NULL, defs,
                             pcrec_rxt_compose, lc_hook, &r, &rin) != 0) {
        pcrec_sb_free(&r.rows);
        return NULL;
    }
    pcrec_output_free(&out);
    if (!r.rows.p) {
        char *e = malloc(1);
        if (e) *e = 0;
        return e;
    }
    return r.rows.p;
}
