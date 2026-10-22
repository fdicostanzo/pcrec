/* emit_subst.c — [M4-SUBST] THE SUBST ARTIFACT: a compiled substitution
 * template as an independent element over an rx SHAPE (D173).
 *
 * Design: docs/design/replace_design.md §R3 (the batch element §R3.1, the
 * needed shape and the generic bind §R3.2-§R3.3, the glue §R3.4, the codes
 * §R3.5, BADSPAN §R3.6, the unset axis and `${!name}` §R3.7, one build
 * §R3.8, the caller contract §R3.9, the header §R3.11). Contract:
 * docs/spec/subst_api.md.
 *
 * An artifact is a `.c` and a `.h`. The `.h` carries a copy of the rx shared
 * block (`pcrec_emit_rx_abi_block`, emit_dfa.c's one emitter, under its
 * existing `PCREC_RX_ABI_H` guard), then the SUBST BLOCK below (prefix-
 * independent, guarded by `PCREC_SUBST_H`), then the template's own
 * declarations. The subst block lives ONLY in subst headers, so this file
 * moves no byte of any rx artifact (§R3.8: no rx abi event at landing); a
 * LATER change to the subst block's text is an abi event under D76/D94,
 * because the block is versioned by the shared abi number.
 *
 * The emitted render is straight-line code per template item: no template
 * interpreter, no name lookup. A numbered reference is a constant slot (D61);
 * a named one walks its bound RUN (match_api §5.4¶6). Every byte goes
 * through the block's one write helper, `rx_subst_put`, which holds the fit
 * test and the saturation, so no emitted template restates the overflow
 * rule. */

#include <string.h>

#include "core/internal.h"

/* THE SUBST BLOCK: types, codes, the write helper, the generic bind, the
 * context-init helper, the batch element's type and the glue. Emitted
 * verbatim after a two-line abi guard, so it never names a prefix or an
 * abi digit itself. `PCREC_SUBST_PAIRS` is an UNMEASURED DEFAULT copied from
 * `RX_FOREACH_PAIRS` (replace_design.md §R3.16; §R3.13's cell would measure
 * it). */
static const char subst_block[] =
"#include <string.h>\n"
"\n"
"/* [M4-SUBST] Codes below PCREC_ERR_ITER: none is a give-up, and the\n"
" * element and the glue never return -1. */\n"
"#define PCREC_SUBST_NOSPACE     (-11)  /* out too small: *outlen is the capacity that suffices */\n"
"#define PCREC_SUBST_BADSPAN     (-12)  /* the rx reported a span a splice cannot express */\n"
"#define PCREC_SUBST_RENDER      (-13)  /* an rx_renderfn segment returned -1 */\n"
"#define PCREC_SUBST_UNSET       (-14)  /* --unset=error: a referenced group is unset */\n"
"#define PCREC_SUBST_MISMATCH    (-15)  /* records, binding, flags or caps do not belong together */\n"
"#define PCREC_SUBST_MISSING_REF (-16)  /* bind: the rx delivers no slot for needs[*bad_ref] */\n"
"\n"
"#define PCREC_SUBST_BOUND 0x53554201u   /* rx_subst_binding.tag after a successful bind */\n"
"#define RX_SUBST_GAPS     0x1u          /* copy [cur->prev, start) before each rendering */\n"
"#define PCREC_SUBST_UNSET_EMPTY 0       /* rx_subst_info.unset: the --unset axis */\n"
"#define PCREC_SUBST_UNSET_ERROR 1\n"
"\n"
"/* Where one find-all's output stands between element calls. */\n"
"typedef struct rx_subst_cur {\n"
"    size_t prev;   /* end of the last match consumed: the next gap starts here */\n"
"    size_t w;      /* bytes the output needs so far; SIZE_MAX once that overflowed */\n"
"    int    fits;   /* 1 while every one of those bytes is in out */\n"
"} rx_subst_cur;\n"
"\n"
"/* A named reference's binding: rows [first, first + count) of rx->groups. */\n"
"typedef struct rx_subst_run { int first, count; } rx_subst_run;\n"
"\n"
"struct rx_subst_info;\n"
"typedef struct rx_subst_binding {\n"
"    uint32_t                    tag;      /* PCREC_SUBST_BOUND, written last by a successful bind */\n"
"    int32_t                     ncaps;    /* rx->ncaps at bind: the pairs every caps entry holds */\n"
"    const struct rx_info       *rx;       /* the record bound against */\n"
"    const struct rx_subst_info *sub;\n"
"    const rx_subst_run         *runs;     /* the caller's <S>_NREFS entries, one per NAMED row */\n"
"    void *const                *seg_user; /* one per rx_renderfn segment; NULL when none */\n"
"} rx_subst_binding;\n"
"\n"
"/* THE ELEMENT: renders k consecutive matches. caps holds k * ctx->ncap\n"
" * pairs; match i is at caps + i * ctx->ncap, as <prefix>_next_n writes\n"
" * them. With RX_SUBST_GAPS the gap before each match is copied first\n"
" * (substitution); without it the renderings are written back to back. Any\n"
" * other flag bit is refused. Bytes go to out[cur->w, cap) while everything\n"
" * fits, never past cap. Returns 0 or a negative code; the length is in\n"
" * cur->w, never in the return value. */\n"
"typedef int rx_substfn(const rx_subst_binding *b, const rx_ctx *ctx,\n"
"                       const ptrdiff_t (*caps)[2], size_t k, unsigned flags,\n"
"                       unsigned char *restrict out, size_t cap, rx_subst_cur *cur);\n"
"\n"
"/* A subst artifact's record: what it NEEDS of an rx, and its element. */\n"
"struct rx_subst_info {\n"
"    unsigned              abi;           /* == PCREC_RX_ABI_H of its build */\n"
"    const char           *name;          /* the artifact's own name */\n"
"    const char           *template_text;\n"
"    size_t                template_len;\n"
"    int                   nneeds;        /* rows in needs[] */\n"
"    const rx_group_entry *needs;         /* the NEEDED shape: named rows first\n"
"                                            (number -1), then numbered (name\n"
"                                            NULL); slot -1 throughout */\n"
"    int                   nruns;         /* named rows: the runs a binding holds */\n"
"    int                   maxnum;        /* highest $k, or 0 */\n"
"    int                   nvrefs;        /* ${!name} references */\n"
"    const char *const    *vrefs;         /* their names; NULL when none */\n"
"    int                   nsegs;         /* rx_renderfn segments (0 in module subst) */\n"
"    int                   unset;         /* PCREC_SUBST_UNSET_EMPTY / _ERROR */\n"
"    int                   encoding;      /* the rx encoding the template was read in, or\n"
"                                            -1: an ASCII template reads the same in any */\n"
"    rx_substfn           *render;\n"
"};\n"
"\n"
"/* Appends src[0, len) at out[cur->w] if it fits, and counts it either way.\n"
" * A total past SIZE_MAX - 1 saturates: w = SIZE_MAX, fits = 0. */\n"
"static inline void rx_subst_put(rx_subst_cur *cur, unsigned char *restrict out, size_t cap,\n"
"                                const unsigned char *src, size_t len)\n"
"{\n"
"    if (cur->w == SIZE_MAX) return;\n"
"    if (len >= SIZE_MAX - cur->w) { cur->w = SIZE_MAX; cur->fits = 0; return; }\n"
"    if (cur->fits && len <= cap - cur->w) { if (len) memcpy(out + cur->w, src, len); }\n"
"    else cur->fits = 0;\n"
"    cur->w += len;\n"
"}\n"
"\n"
"/* Checks a match's span and, under RX_SUBST_GAPS, copies the gap before it.\n"
" * A span ending before it starts or past the subject's end, or (with gaps)\n"
" * starting before the previous match's end, is PCREC_SUBST_BADSPAN. */\n"
"static inline int rx_subst_span(rx_subst_cur *cur, unsigned char *restrict out, size_t cap,\n"
"                                const unsigned char *s, size_t len,\n"
"                                const ptrdiff_t (*c)[2], unsigned flags)\n"
"{\n"
"    if (c[0][0] < 0 || c[0][1] < c[0][0] || (size_t)c[0][1] > len) return PCREC_SUBST_BADSPAN;\n"
"    if (flags & RX_SUBST_GAPS) {\n"
"        if ((size_t)c[0][0] < cur->prev) return PCREC_SUBST_BADSPAN;\n"
"        rx_subst_put(cur, out, cap, s + cur->prev, (size_t)c[0][0] - cur->prev);\n"
"    }\n"
"    return 0;\n"
"}\n"
"\n"
"/* Appends group slot sl's bytes. An unset group (sl < 0, or a slot that did\n"
" * not participate) renders nothing, or is PCREC_SUBST_UNSET under\n"
" * unset_error. */\n"
"static inline int rx_subst_group(rx_subst_cur *cur, unsigned char *restrict out, size_t cap,\n"
"                                 const unsigned char *s, const ptrdiff_t (*c)[2],\n"
"                                 int sl, int unset_error)\n"
"{\n"
"    if (sl < 0 || c[sl][0] < 0 || c[sl][1] < 0)\n"
"        return unset_error ? PCREC_SUBST_UNSET : 0;\n"
"    if (c[sl][1] < c[sl][0]) return PCREC_SUBST_BADSPAN;\n"
"    rx_subst_put(cur, out, cap, s + c[sl][0], (size_t)(c[sl][1] - c[sl][0]));\n"
"    return 0;\n"
"}\n"
"\n"
"/* The slot a named reference resolves to in one match: the first member of\n"
" * run j that participated (match_api section 5.4, paragraph 6), or -1 when none did. */\n"
"static inline int rx_subst_run_slot(const rx_subst_binding *b, int j, const ptrdiff_t (*c)[2])\n"
"{\n"
"    const rx_group_entry *g = b->rx->groups + b->runs[j].first;\n"
"    for (int i = 0; i < b->runs[j].count; i++)\n"
"        if (c[g[i].slot][0] >= 0 && c[g[i].slot][1] >= 0) return g[i].slot;\n"
"    return -1;\n"
"}\n"
"\n"
"/* The run of rows named `name` in scope `ref` (NULL: the caller scope, rows\n"
" * [0, nnames); otherwise the site-scoped rows [nnames, nentries) spelled\n"
" * `ref.name`). Writes the first row's index to *first and returns the run's\n"
" * length, 0 when there is none: bsearch, then walk back to the run's head\n"
" * (the first two steps of match_api section 5.4, paragraph 6). */\n"
"static inline int rx_group_run(const struct rx_info *rx, const char *name,\n"
"                               const char *ref, int *first)\n"
"{\n"
"    const rx_group_entry *g = rx->groups;\n"
"    int lo = 0, hi = rx->nnames, at = -1, n = 0;\n"
"    if (!g) return 0;\n"
"    if (ref) {                                     /* site rows: a short linear scan */\n"
"        size_t lr = strlen(ref);\n"
"        for (int i = rx->nnames; i < rx->nentries; i++)\n"
"            if (!strncmp(g[i].name, ref, lr) && g[i].name[lr] == '.'\n"
"                && !strcmp(g[i].name + lr + 1, name)) { if (at < 0) at = i; n++; }\n"
"            else if (at >= 0) break;\n"
"        *first = at;\n"
"        return n;\n"
"    }\n"
"    while (lo < hi) {\n"
"        int mid = lo + (hi - lo) / 2, d = strcmp(g[mid].name, name);\n"
"        if (d == 0) { at = mid; break; }\n"
"        if (d < 0) lo = mid + 1; else hi = mid;\n"
"    }\n"
"    if (at < 0) return 0;\n"
"    while (at > 0 && !strcmp(g[at - 1].name, name)) at--;\n"
"    *first = at;\n"
"    for (n = 0; at + n < rx->nnames && !strcmp(g[at + n].name, name); n++) {}\n"
"    return n;\n"
"}\n"
"\n"
"/* THE GENERIC BIND over two shapes: the index of the first NEEDED row the\n"
" * OFFERED shape (rx) does not satisfy, or -1 when every row is satisfied.\n"
" * Fills runs[j] for the j-th named row. Knows nothing about templates. */\n"
"static inline int rx_shape_match(const rx_group_entry *needs, int nneeds,\n"
"                                 const struct rx_info *rx, rx_subst_run *runs)\n"
"{\n"
"    int j = 0;\n"
"    for (int i = 0; i < nneeds; i++) {\n"
"        const rx_group_entry *e = &needs[i];\n"
"        if (!e->name) {                            /* a number: a constant slot (D61) */\n"
"            if (e->number < 0 || (e->number != 0\n"
"                                  && (e->number > rx->ngroups || e->number >= rx->ncaps)))\n"
"                return i;\n"
"            continue;\n"
"        }\n"
"        int first = 0, n = rx_group_run(rx, e->name, e->ref, &first);\n"
"        if (n < 1) return i;\n"
"        for (int m = 0; m < n; m++)\n"
"            if (rx->groups[first + m].slot < 0 || rx->groups[first + m].slot >= rx->ncaps)\n"
"                return i;\n"
"        runs[j].first = first;\n"
"        runs[j].count = n;\n"
"        j++;\n"
"    }\n"
"    return -1;\n"
"}\n"
"\n"
"/* Binds subst `sub` to rx `rx` into *b: 0, or PCREC_SUBST_MISMATCH (a\n"
" * record of another abi, an rx with no slot or of another encoding than a\n"
" * non-ASCII template's, nruns or nseg too small) or\n"
" * PCREC_SUBST_MISSING_REF (the rx delivers no slot for\n"
" * sub->needs[*bad_ref]). *bad_ref is -1 unless the code is MISSING_REF.\n"
" * Reads only the two records; never allocates. On a refusal b->tag is not\n"
" * BOUND. runs (and seg_user) must outlive the binding. */\n"
"static inline int pcrec_subst_bind(rx_subst_binding *b, const struct rx_info *rx,\n"
"                                   const struct rx_subst_info *sub,\n"
"                                   rx_subst_run *runs, size_t nruns,\n"
"                                   void *const *seg_user, size_t nseg, int *bad_ref)\n"
"{\n"
"    *bad_ref = -1;\n"
"    b->tag = 0;\n"
"    if (rx->abi != PCREC_RX_ABI_H || sub->abi != PCREC_RX_ABI_H || rx->ncaps < 1\n"
"        || (sub->encoding >= 0 && sub->encoding != rx->encoding)\n"
"        || nruns < (size_t)sub->nruns\n"
"        || (sub->nsegs && (!seg_user || nseg < (size_t)sub->nsegs)))\n"
"        return PCREC_SUBST_MISMATCH;\n"
"    int bad = rx_shape_match(sub->needs, sub->nneeds, rx, runs);\n"
"    if (bad >= 0) { *bad_ref = bad; return PCREC_SUBST_MISSING_REF; }\n"
"    b->ncaps = rx->ncaps;\n"
"    b->rx = rx;\n"
"    b->sub = sub;\n"
"    b->runs = runs;\n"
"    b->seg_user = sub->nsegs ? seg_user : (void *const *)0;\n"
"    b->tag = PCREC_SUBST_BOUND;\n"
"    return 0;\n"
"}\n"
"\n"
"/* ctx for an element call over iterator `it` with binding `b`: subject, len\n"
" * and ncap from them; each ${!name} resolved by name (first match wins) into\n"
" * vres (b->sub->nvrefs entries, at least 1), in the template's order; user\n"
" * NULL. Returns 0, or PCREC_ERR_UNSET_VAR under --unset=error. Reads\n"
" * it->vars only when the iterator is BOUND, or FRESH with\n"
" * PCREC_ITER_OPT_VARS set: in any other state the field may hold any value. */\n"
"static inline int rx_subst_ctx_init(rx_ctx *ctx, const rx_iter *it,\n"
"                                    const rx_subst_binding *b, rx_var *vres)\n"
"{\n"
"    const struct rx_subst_info *sub = b->sub;\n"
"    const rx_var *v = (const rx_var *)0;\n"
"    size_t nv = 0;\n"
"    if (it->hdr == PCREC_ITER_BOUND\n"
"        || ((it->hdr & ~PCREC_ITER_OPT_MASK) == PCREC_ITER_FRESH\n"
"            && (it->hdr & PCREC_ITER_OPT_VARS))) { v = it->vars; nv = it->nvars; }\n"
"    ctx->subject = it->s; ctx->len = it->n; ctx->pos = 0;\n"
"    ctx->ncap = (size_t)b->ncaps; ctx->caps = 0; ctx->user = 0;\n"
"    ctx->vars = sub->nvrefs ? vres : (const rx_var *)0;\n"
"    ctx->nvars = (size_t)sub->nvrefs;\n"
"    for (int j = 0; j < sub->nvrefs; j++) {\n"
"        vres[j].name = sub->vrefs[j]; vres[j].p = 0; vres[j].len = 0;\n"
"        for (size_t i = 0; i < nv; i++)\n"
"            if (v[i].name && !strcmp(v[i].name, sub->vrefs[j])) {\n"
"                vres[j].p = v[i].p; vres[j].len = v[i].p ? v[i].len : 0;\n"
"                break;\n"
"            }\n"
"        if (!vres[j].p && sub->unset == PCREC_SUBST_UNSET_ERROR) return PCREC_ERR_UNSET_VAR;\n"
"    }\n"
"    return 0;\n"
"}\n"
"\n"
"#ifndef PCREC_SUBST_PAIRS\n"
"#define PCREC_SUBST_PAIRS 256    /* the glue's batch buffer, in pairs: an UNMEASURED default */\n"
"#endif\n"
"\n"
"/* THE GLUE: every match of `it` (FRESH, setters applied; any other state is\n"
" * PCREC_ERR_ITER), up to `limit` of them (1: the first match; SIZE_MAX:\n"
" * all), gaps copied, each match rendered, the tail copied. Returns 0 or a\n"
" * negative code. *outlen and\n"
" * *nsubst are written on EVERY path: on 0, the produced length and the\n"
" * substitution count; on PCREC_SUBST_NOSPACE, the capacity that suffices\n"
" * (SIZE_MAX: none does) and the full count; on any other code, 0 and 0.\n"
" * out == NULL sizes only. out must not overlap s[0, n); after a negative\n"
" * return its contents are unspecified. After a stop at `limit` the\n"
" * iterator's state is unspecified for this glue: it does not resume. */\n"
"static inline int pcrec_subst(const rx_subst_binding *b, rx_iter *it, size_t limit,\n"
"                              unsigned char *restrict out, size_t cap,\n"
"                              size_t *outlen, size_t *nsubst)\n"
"{\n"
"    *outlen = 0; *nsubst = 0;\n"
"    if (b->tag != PCREC_SUBST_BOUND || b->rx->abi != PCREC_RX_ABI_H\n"
"        || b->sub->abi != PCREC_RX_ABI_H || b->ncaps != b->rx->ncaps || !b->rx->next_n)\n"
"        return PCREC_SUBST_MISMATCH;\n"
"    if ((it->hdr & ~PCREC_ITER_OPT_MASK) != PCREC_ITER_FRESH) return PCREC_ERR_ITER;\n"
"    const size_t nc = (size_t)b->ncaps;\n"
"    size_t kmax = nc <= PCREC_SUBST_PAIRS ? PCREC_SUBST_PAIRS / nc : 1;\n"
"    if (kmax > 64) kmax = 64;\n"
"    ptrdiff_t buf[kmax * nc][2];                 /* at least one match at any ncaps */\n"
"    rx_var vres[b->sub->nvrefs ? b->sub->nvrefs : 1];\n"
"    rx_ctx ctx;\n"
"    int rc = rx_subst_ctx_init(&ctx, it, b, vres);\n"
"    if (rc < 0) return rc;\n"
"    rx_subst_cur cur = { 0, 0, out != (unsigned char *)0 };\n"
"    size_t k = 1, done = 0;\n"
"    while (done < limit) {\n"
"        size_t want = k < limit - done ? k : limit - done;   /* never past limit */\n"
"        size_t got = b->rx->next_n(it, buf, want);\n"
"        rc = b->sub->render(b, &ctx, (const ptrdiff_t (*)[2])buf, got, RX_SUBST_GAPS,\n"
"                            out, cap, &cur);\n"
"        if (rc < 0) return rc;\n"
"        done += got;\n"
"        if (got < want) {                        /* the iterator ended */\n"
"            if (it->rc < 0) return it->rc;\n"
"            break;\n"
"        }\n"
"        if (k < kmax) k = 2 * k < kmax ? 2 * k : kmax;\n"
"    }\n"
"    rx_subst_put(&cur, out, cap, ctx.subject + cur.prev, ctx.len - cur.prev);\n"
"    *nsubst = done;\n"
"    *outlen = cur.w;\n"
"    return (cur.w == SIZE_MAX || (out && !cur.fits)) ? PCREC_SUBST_NOSPACE : 0;\n"
"}\n";

/* The subst block under its guard: an `#error` unless the rx shared block of
 * this build's abi is already defined (the same-build rule, §R3.8), then the
 * block once per translation unit. */
static void emit_subst_block(StrBuf *sb)
{
    int abi = pcrec_artifact_abi();
    pcrec_sb_printf(sb, "#if !defined(PCREC_RX_ABI_H) || (PCREC_RX_ABI_H + 0) != %d\n"
                        "#error \"pcrec: this subst artifact (abi %d) needs the rx shared block of abi %d; "
                        "regenerate the rx and the subst with one pcrec\"\n"
                        "#endif\n", abi, abi, abi);
    pcrec_sb_printf(sb, "#ifndef PCREC_SUBST_H\n#define PCREC_SUBST_H %d\n", abi);
    pcrec_sb_puts(sb, subst_block);
    pcrec_sb_puts(sb, "#endif /* PCREC_SUBST_H */\n");
}

/* The provenance line: pcrec's version, the abi and the template, escaped
 * for a comment. */
static void emit_subst_provenance(StrBuf *sb, const char *tmpl, size_t len)
{
    pcrec_sb_printf(sb, "/* Generated by pcrec %s (abi %d). Template: ",
                    PCREC_VERSION, pcrec_artifact_abi());
    pcrec_emit_comment_bytes(sb, tmpl, len);
    pcrec_sb_puts(sb, " */\n");
}

/* `max(1, n)`: a count that sizes a caller's array (§R3.3, crit3-4). */
static int at_least_one(int n) { return n > 0 ? n : 1; }

/* The declarations a caller includes: the storage stamps (match_api
 * §6.3.1¶1's family), the record and the element. */
static void emit_subst_decls(StrBuf *sb, const char *p, const char *up, const SubstTmpl *t)
{
    pcrec_sb_stampf(sb, up, "NREFS", "%d", at_least_one(t->nnamed));
    pcrec_sb_stampf(sb, up, "NSEGS", "%d", 1);
    pcrec_sb_stampf(sb, up, "MAXNUM", "%d", t->maxnum);
    pcrec_sb_stampf(sb, up, "NVREFS", "%d", at_least_one(t->nvrefs));
    pcrec_sb_printf(sb, "extern const struct rx_subst_info %s_subst_info;\n", p);
    pcrec_sb_printf(sb, "int %s_render(const rx_subst_binding *b, const rx_ctx *ctx,\n"
                        "    const ptrdiff_t (*caps)[2], size_t k, unsigned flags,\n"
                        "    unsigned char *restrict out, size_t cap, rx_subst_cur *cur);\n", p);
}

/* The `.h`: provenance, include guard, the rx shared block, the subst block,
 * the template's declarations. The guard spells the prefix VERBATIM under a
 * stem no rx header uses (an rx guard is `PCREC_GEN_<UPPER>_H`), so it
 * collides with neither an rx header of the same prefix nor a subst header
 * whose prefix differs only in case. */
static void emit_subst_header(StrBuf *h, const char *tmpl, size_t len, const char *p,
                              const char *up, const SubstTmpl *t)
{
    emit_subst_provenance(h, tmpl, len);
    pcrec_sb_printf(h, "#ifndef PCREC_SUBST_GEN_%s_H\n#define PCREC_SUBST_GEN_%s_H\n\n", p, p);
    pcrec_sb_puts(h, "#include <stddef.h>\n#include <stdint.h>\n\n");
    pcrec_emit_rx_abi_block(h);
    pcrec_sb_putc(h, '\n');
    emit_subst_block(h);
    pcrec_sb_putc(h, '\n');
    emit_subst_decls(h, p, up, t);
    pcrec_sb_printf(h, "\n#endif /* PCREC_SUBST_GEN_%s_H */\n", p);
}

/* The record's tables: the NEEDED rows and the `${!name}` names. */
static void emit_subst_tables(StrBuf *c, const char *p, const SubstTmpl *t)
{
    if (t->nneeds) {
        pcrec_sb_printf(c, "static const rx_group_entry %s_subst_needs[] = {\n", p);
        for (int i = 0; i < t->nneeds; i++) {
            const SubstNeed *e = &t->needs[i];
            pcrec_sb_puts(c, "    { ");
            if (e->name) pcrec_emit_c_string_literal(c, e->name, strlen(e->name));
            else pcrec_sb_puts(c, "NULL");
            pcrec_sb_printf(c, ", %d, -1, NULL },\n", e->number);
        }
        pcrec_sb_puts(c, "};\n");
    }
    if (t->nvrefs) {
        pcrec_sb_printf(c, "static const char *const %s_subst_vrefs[] = {\n", p);
        for (int j = 0; j < t->nvrefs; j++) {
            pcrec_sb_puts(c, "    ");
            pcrec_emit_c_string_literal(c, t->vrefs[j], strlen(t->vrefs[j]));
            pcrec_sb_puts(c, ",\n");
        }
        pcrec_sb_puts(c, "};\n");
    }
}

/* One template item's rendering statement, inside the per-match loop. */
static void emit_subst_item(StrBuf *c, const char *tmpl, const SubstItem *it, int uerr)
{
    switch (it->kind) {
    case SUBST_LIT:
        pcrec_sb_puts(c, "        rx_subst_put(cur, out, cap, (const unsigned char *)");
        pcrec_emit_c_string_literal(c, tmpl + it->off, it->len);
        pcrec_sb_printf(c, ", %zu);\n", it->len);
        break;
    case SUBST_GROUP:
        pcrec_sb_printf(c, "        if ((rc = rx_subst_group(cur, out, cap, s, c, %d, %d)) < 0) return rc;\n",
                        it->ref, uerr);
        break;
    case SUBST_NAME:
        pcrec_sb_printf(c, "        if ((rc = rx_subst_group(cur, out, cap, s, c, "
                           "rx_subst_run_slot(b, %d, c), %d)) < 0) return rc;\n", it->ref, uerr);
        break;
    case SUBST_VAR:
        if (uerr)
            pcrec_sb_printf(c, "        if (!ctx->vars[%d].p) return PCREC_ERR_UNSET_VAR;\n", it->ref);
        pcrec_sb_printf(c, "        if (ctx->vars[%d].p) rx_subst_put(cur, out, cap, ctx->vars[%d].p, "
                           "ctx->vars[%d].len);\n", it->ref, it->ref, it->ref);
        break;
    case SUBST_SUBJECT:
        pcrec_sb_puts(c, "        rx_subst_put(cur, out, cap, s, ctx->len);\n");
        break;
    case SUBST_BEFORE:
        pcrec_sb_puts(c, "        rx_subst_put(cur, out, cap, s, (size_t)c[0][0]);\n");
        break;
    case SUBST_AFTER:
        pcrec_sb_puts(c, "        rx_subst_put(cur, out, cap, s + c[0][1], ctx->len - (size_t)c[0][1]);\n");
        break;
    }
}

/* The element: the identity checks once per call, then per match the span
 * check and gap, the items in template order, and the new `prev`. */
static void emit_subst_render(StrBuf *c, const char *tmpl, const char *p, const SubstTmpl *t,
                              bool unset_error)
{
    pcrec_sb_printf(c, "int %s_render(const rx_subst_binding *b, const rx_ctx *ctx,\n"
                       "    const ptrdiff_t (*caps)[2], size_t k, unsigned flags,\n"
                       "    unsigned char *restrict out, size_t cap, rx_subst_cur *cur)\n{\n", p);
    pcrec_sb_puts(c, "    const unsigned char *s = ctx->subject;\n"
                     "    const size_t nc = ctx->ncap;\n"
                     "    int rc;\n");
    pcrec_sb_printf(c, "    if (b->tag != PCREC_SUBST_BOUND || b->sub != &%s_subst_info\n"
                       "        || nc != (size_t)b->ncaps || (flags & ~RX_SUBST_GAPS)", p);
    if (t->nvrefs)          /* a custom ctx must carry the resolved variables */
        pcrec_sb_printf(c, "\n        || !ctx->vars || ctx->nvars < %d", t->nvrefs);
    pcrec_sb_puts(c, ")\n        return PCREC_SUBST_MISMATCH;\n");
    pcrec_sb_puts(c, "    for (size_t i = 0; i < k; i++) {\n"
                     "        const ptrdiff_t (*c)[2] = caps + i * nc;\n"
                     "        if ((rc = rx_subst_span(cur, out, cap, s, ctx->len, c, flags)) < 0) return rc;\n");
    for (size_t i = 0; i < t->nitems; i++)
        emit_subst_item(c, tmpl, &t->items[i], unset_error);
    pcrec_sb_puts(c, "        cur->prev = (size_t)c[0][1];\n"
                     "    }\n");
    pcrec_sb_puts(c, "    return 0;\n}\n");
}

/* The encoding a template binds under: its own, when a byte of it is
 * non-ASCII (it was read in that encoding: names, the UTF check); -1, any,
 * when every byte is ASCII and reads the same in each. */
static int subst_bind_encoding(const char *tmpl, size_t len, int encoding)
{
    for (size_t i = 0; i < len; i++)
        if ((unsigned char)tmpl[i] >= 0x80) return encoding;
    return -1;
}

/* The record. */
static void emit_subst_info(StrBuf *c, const char *tmpl, size_t len, const char *p,
                            const SubstTmpl *t, const PcrecSubstOptions *o)
{
    const bool unset_error = o->unset_error;
    pcrec_sb_printf(c, "const struct rx_subst_info %s_subst_info = {\n", p);
    pcrec_sb_printf(c, "    .abi = %d,\n    .name = \"%s\",\n    .template_text = ",
                    pcrec_artifact_abi(), p);
    pcrec_emit_c_string_literal(c, tmpl, len);
    pcrec_sb_printf(c, ",\n    .template_len = %zu,\n", len);
    pcrec_sb_printf(c, "    .nneeds = %d,\n", t->nneeds);
    if (t->nneeds) pcrec_sb_printf(c, "    .needs = %s_subst_needs,\n", p);
    else pcrec_sb_puts(c, "    .needs = NULL,\n");
    pcrec_sb_printf(c, "    .nruns = %d,\n    .maxnum = %d,\n    .nvrefs = %d,\n",
                    t->nnamed, t->maxnum, t->nvrefs);
    if (t->nvrefs) pcrec_sb_printf(c, "    .vrefs = %s_subst_vrefs,\n", p);
    else pcrec_sb_puts(c, "    .vrefs = NULL,\n");
    pcrec_sb_printf(c, "    .nsegs = 0,\n    .unset = %s,\n    .encoding = %d,\n"
                       "    .render = %s_render,\n};\n",
                    unset_error ? "PCREC_SUBST_UNSET_ERROR" : "PCREC_SUBST_UNSET_EMPTY",
                    subst_bind_encoding(tmpl, len, o->encoding), p);
}

void pcrec_emit_subst(const char *tmpl, size_t len, const SubstTmpl *t,
                      const PcrecSubstOptions *o, pcrec_output *out)
{
    Arena a = { NULL, NULL };
    StrBuf c = { 0 }, h = { 0 };
    const char *p = o->prefix;
    const char *up = pcrec_sb_upper(&a, p);

    emit_subst_provenance(&c, tmpl, len);
    pcrec_sb_stamp_str(&c, up, "SUBST_UNSET", o->unset_error ? "error" : "empty");
    pcrec_sb_stamp_str(&c, up, "SUBST_MODULES", t->uses_pcrec ? "subst,subst-pcrec" : "subst");
    if (o->header_name) {
        pcrec_sb_printf(&c, "#include \"%s\"\n\n", o->header_name);
        emit_subst_header(&h, tmpl, len, p, up, t);
    } else {
        pcrec_sb_puts(&c, "#include <stddef.h>\n#include <stdint.h>\n\n");
        pcrec_emit_rx_abi_block(&c);
        pcrec_sb_putc(&c, '\n');
        emit_subst_block(&c);
        pcrec_sb_putc(&c, '\n');
        emit_subst_decls(&c, p, up, t);
        pcrec_sb_putc(&c, '\n');
    }
    emit_subst_tables(&c, p, t);
    emit_subst_render(&c, tmpl, p, t, o->unset_error);
    emit_subst_info(&c, tmpl, len, p, t, o);

    out->c_src = pcrec_sb_take(&c);
    out->h_src = o->header_name ? pcrec_sb_take(&h) : NULL;
    pcrec_arena_free(&a);
}
