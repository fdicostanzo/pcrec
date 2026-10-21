/* src/parse/ks_analysis.c — [KNOW-SRC] the ANALYSIS kind's row
 * (docs/design/measure_sets.md rev 3 §9.2, §9.5): the analysis object of
 * D162, resolved by `--analysis NAME`, the `analysis` config line and
 * `--list-analysis`, from the compiling file (S1), `-I DIR/<name>.rxt` (S2)
 * and the built-in store (S3).
 *
 * The row is a parse-layer TU because its file probe is the `.rxt` reader;
 * the kind-independent resolver it plugs into is `src/core/ksrc.c`. Its
 * include chain (`include`, the self-name `#include_next`, the terminal
 * `default`) is NOT here: that is this kind's own semantics and stays in
 * `rxt_find.c`, which asks the resolver for one link at a time.
 *
 * [KNOW-SRC] K3: the kind's two VIEWS of one bundle (§9.6). The CANONICAL
 * view is a normalized `.rxt` bundle — a loadable input of this kind, so
 * load -> list -> load keeps the item digest and list -> load -> list is a
 * fixed point — and the DECODED view prints the loaded document field by
 * field as a `table_contract.md` section, the shape `pcrec-analyze
 * --dump-doc` prints from its own independent reader (analyze/, R3 and R5's
 * control). Both read the parse (`PcrecKsAnalysisItem`), never a chain link:
 * a link copies the counts and drops the prose. */

#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

#include "core/internal.h"
#include "core/ksrc.h"

/* Stop S2's file probe: `path` refused over PCREC_MAX_FIND_BUNDLE_BYTES
 * (never truncated), parsed, and its bundles counted; FOUND hands the parse
 * (an `RxtSource *`) to the caller, who frees it. */
static KsFile analysis_probe(const KsAlloc *a, const char *path, const char *name,
                             void **doc, size_t *nitems, KsErr *err)
{
    struct stat sb;
    pcrec_error perr = { 0 };
    RxtSource *src;
    bool named = false;
    size_t n = 0;
    (void)a;                    /* the `.rxt` reader allocates its own parse */
    if (stat(path, &sb) == 0 &&
        (unsigned long long)sb.st_size > PCREC_MAX_FIND_BUNDLE_BYTES) {
        snprintf(err->msg, sizeof err->msg, "%s: %llu bytes, over "
                 "PCREC_MAX_FIND_BUNDLE_BYTES (%llu): an analysis file is "
                 "refused, never truncated",
                 path, (unsigned long long)sb.st_size,
                 (unsigned long long)PCREC_MAX_FIND_BUNDLE_BYTES);
        return KS_FILE_ERROR;
    }
    src = pcrec_rxt_source_parse(path, &perr);
    if (!src) {
        snprintf(err->msg, sizeof err->msg, "%s", perr.msg);
        return KS_FILE_ERROR;
    }
    for (size_t i = 0; i < src->nrows; i++)
        if (src->rows[i].kind == RXT_DECL_ANALYSIS) {
            n++;
            if (!strcmp(src->rows[i].name, name)) named = true;
        }
    *nitems = n;
    if (n > 1 || !named) {
        pcrec_rxt_source_free(src);
        return n > 1 ? KS_FILE_MULTI : KS_FILE_OTHER;
    }
    *doc = src;
    return KS_FILE_FOUND;
}

/* ---- the views (§9.6) ------------------------------------------------ */

/* The eleven provenance fields in `rxt_format.md` §1.9's table order: the
 * order both views write them in. `prose` marks the four that are PROSE
 * (written untrimmed, and in the block-scalar form when multi-line). */
static const struct {
    const char *name;
    size_t      off;
    bool        prose;
} prov_fields[] = {
    { "source",       offsetof(RxtProv, source),       false },
    { "url",          offsetof(RxtProv, url),          false },
    { "ref",          offsetof(RxtProv, ref),          false },
    { "retrieved",    offsetof(RxtProv, retrieved),    false },
    { "license",      offsetof(RxtProv, license),      false },
    { "license-note", offsetof(RxtProv, license_note), true  },
    { "fidelity",     offsetof(RxtProv, fidelity),     false },
    { "adaptation",   offsetof(RxtProv, adaptation),   true  },
    { "attribution",  offsetof(RxtProv, attribution),  true  },
    { "bytes",        offsetof(RxtProv, bytes),        false },
    { "sha256",       offsetof(RxtProv, sha256),       false },
};
#define N_PROV_FIELDS (sizeof prov_fields / sizeof *prov_fields)

/* Field `i` of provenance record `r`, or NULL where it is not written. */
static const char *prov_field(const RxtProv *r, size_t i)
{
    const char *v;
    memcpy(&v, (const char *)r + prov_fields[i].off, sizeof v);
    return v;
}

/* The bundle's own `analysis` row in the item's parse, or NULL. */
static const RxtRow *item_row(const PcrecKsAnalysisItem *it)
{
    for (size_t i = 0; i < it->src->nrows; i++)
        if (it->src->rows[i].kind == RXT_DECL_ANALYSIS &&
            !strcmp(it->src->rows[i].name, it->bundle))
            return &it->src->rows[i];
    return NULL;
}

/* The provenance record of data block `fb`, or NULL. */
static const RxtProv *block_prov(const RxtSource *src, const RxtFindBlock *fb)
{
    for (size_t i = 0; i < src->nprovs; i++)
        if (src->provs[i].data_kind && src->provs[i].data_line == fb->line &&
            src->provs[i].block_name && !strcmp(src->provs[i].block_name, fb->bundle))
            return &src->provs[i];
    return NULL;
}

/* Hands the built text to the caller's writer and frees it. */
static int view_flush(const KsOut *o, StrBuf *sb, KsErr *err)
{
    int rc = sb->len && o->write(o->ctx, sb->p, sb->len) != 0;
    pcrec_sb_free(sb);
    if (rc) snprintf(err->msg, sizeof err->msg, "the view's writer failed");
    return rc ? -1 : 0;
}

/* One `kw value` line at `ind` spaces. A PROSE value that holds a newline,
 * or whose trimmed text is the single byte `|` (which would open a region),
 * takes the block-scalar form: `kw |`, then each line of the value indented
 * four deeper — an empty line as exactly that indent, which decodes to an
 * empty line (`rxt_format.md` §1.4.4, §1.4.7¶4). A prose value never begins
 * with whitespace (the reader strips the first line's indent), so the form
 * reproduces it byte for byte. An empty value is the bare keyword. */
static void canon_line(StrBuf *sb, int ind, const char *kw, const char *v,
                       bool prose)
{
    size_t n = strlen(v), t = n;
    while (t && (v[t - 1] == ' ' || v[t - 1] == '\t')) t--;
    if (!prose || (!strchr(v, '\n') && !(t == 1 && v[0] == '|'))) {
        pcrec_sb_printf(sb, "%*s%s%s%s\n", ind, "", kw, n ? " " : "", v);
        return;
    }
    pcrec_sb_printf(sb, "%*s%s |\n", ind, "", kw);
    for (const char *l = v;;) {
        const char *e = strchr(l, '\n');
        size_t len = e ? (size_t)(e - l) : strlen(l);
        pcrec_sb_printf(sb, "%*s%.*s\n", ind + 4, "", (int)len, l);
        if (!e) break;
        l = e + 1;
    }
}

/* One block's rows in the format's canonical spelling: `row HH N` (freq),
 * `row U+HHHH N` (cpfreq), ascending — the order the reader enforced. */
static void canon_rows(StrBuf *sb, const RxtFindBlock *fb)
{
    for (int b = 0; fb->counts && b < 256; b++)
        if (fb->counts[b])
            pcrec_sb_printf(sb, "        row %02x %llu\n", b, fb->counts[b]);
    for (size_t j = 0; j < fb->ncps; j++)
        pcrec_sb_printf(sb, "        row U+%04lX %llu\n",
                        (unsigned long)fb->cps[j].cp, fb->cps[j].count);
}

/* THE CANONICAL VIEW: the bundle as a normalized `.rxt` text — one fixed
 * comment line, then `analysis NAME`, its `include` and `description`, and
 * its data blocks in FILE order (the item digest, `rows_digest`, folds the
 * blocks in that order, so a reorder would be a value change). Each block's
 * lines in `rxt_format.md` §1.10's table order, its rows ascending, its
 * provenance fields in §1.9's order. `#` prose and blank lines are not
 * carried: that is the canonical form's stated loss (§9.6, §9.9). */
static int analysis_write_canonical(const KsOut *o, const void *doc,
                                    KsErr *err)
{
    const PcrecKsAnalysisItem *it = doc;
    const RxtSource *src = it->src;
    const RxtRow *row = item_row(it);
    StrBuf sb = { 0 };
    if (!row) {
        snprintf(err->msg, sizeof err->msg, "internal error: no analysis "
                 "'%s' in its own parse", it->bundle);
        return -1;
    }
    pcrec_sb_puts(&sb, "# pcrec analysis bundle, canonical view "
                  "(docs/spec/findings.md §8.4)\n");
    pcrec_sb_printf(&sb, "analysis %s\n", it->bundle);
    if (row->value && row->value[0])
        canon_line(&sb, 4, "include", row->value, false);
    if (row->description)
        canon_line(&sb, 4, "description", row->description, true);
    for (size_t i = 0; i < src->nfblocks; i++) {
        const RxtFindBlock *fb = &src->fblocks[i];
        const RxtProv *pv;
        if (strcmp(fb->bundle, it->bundle) != 0) continue;
        pcrec_sb_printf(&sb, "    %s\n", fb->kind);
        if (fb->question) canon_line(&sb, 8, "question", fb->question, false);
        if (fb->reader)   canon_line(&sb, 8, "reader", fb->reader, false);
        if (fb->analyzer) canon_line(&sb, 8, "analyzer", fb->analyzer, false);
        if (fb->encoding) canon_line(&sb, 8, "encoding", fb->encoding, false);
        for (size_t j = 0; j < fb->nserves; j++)
            pcrec_sb_printf(&sb, "        serves %s when %s via %s\n",
                            fb->serves[j].query, fb->serves[j].encs,
                            fb->serves[j].via);
        canon_rows(&sb, fb);
        if (!(pv = block_prov(src, fb))) continue;
        pcrec_sb_puts(&sb, "        provenance\n");
        for (size_t f = 0; f < N_PROV_FIELDS; f++) {
            const char *v = prov_field(pv, f);
            if (v) canon_line(&sb, 12, prov_fields[f].name, v,
                              prov_fields[f].prose);
        }
    }
    return view_flush(o, &sb, err);
}

/* One `decoded` row: scope, field, value, through the contract's escape. */
static void dec_row(StrBuf *sb, const char *scope, const char *field,
                    const char *value)
{
    const char *cells[3] = { scope, field, value };
    pcrec_sb_row(sb, cells, 3);
}

/* THE DECODED VIEW: the LOADED document, one row per field, in document
 * order — the bundle's name, `include` (the bare name) and `description`,
 * then each block in file order: its declarations, each `serves` line
 * respelled from its parsed parts, each row, each provenance field. A
 * derived view: its `decoded` and `item` sections are on the row's
 * `derived_sections` list, so the loader refuses this text as an input.
 * `item` carries the ITEM digest (`rows_digest`, §9.2 part 5) — R1's
 * digest — computed from the same parse. */
static int analysis_write_decoded(const KsOut *o, const void *doc, KsErr *err)
{
    const PcrecKsAnalysisItem *it = doc;
    const RxtSource *src = it->src;
    const RxtRow *row = item_row(it);
    PcrecFindTblBlock bl[8];
    size_t nbl = 0;
    StrBuf sb = { 0 };
    char dig[24];
    static const char *const ihdr[] = { "role", "digest" };
    if (!row) {
        snprintf(err->msg, sizeof err->msg, "internal error: no analysis "
                 "'%s' in its own parse", it->bundle);
        return -1;
    }
    pcrec_sb_printf(&sb, "# pcrec --list-analysis %s --view=decoded: the "
                    "loaded bundle, field by field (docs/spec/findings.md "
                    "§8.5); never an input\n", it->bundle);
    pcrec_sb_puts(&sb, "#section decoded\n# one row per field of the loaded "
                  "document, in document order\n#scope\tfield\tvalue\n");
    dec_row(&sb, "bundle", "name", it->bundle);
    if (row->value && row->value[0]) {     /* `<x>` as written: the name */
        StrBuf v = { 0 };
        pcrec_sb_printf(&v, "%.*s", (int)(strlen(row->value) - 2),
                        row->value + 1);
        dec_row(&sb, "bundle", "include", v.p);
        pcrec_sb_free(&v);
    }
    if (row->description) dec_row(&sb, "bundle", "description", row->description);
    for (size_t i = 0; i < src->nfblocks; i++) {
        const RxtFindBlock *fb = &src->fblocks[i];
        const RxtProv *pv;
        if (strcmp(fb->bundle, it->bundle) != 0) continue;
        if (fb->question) dec_row(&sb, fb->kind, "question", fb->question);
        if (fb->reader)   dec_row(&sb, fb->kind, "reader", fb->reader);
        if (fb->analyzer) dec_row(&sb, fb->kind, "analyzer", fb->analyzer);
        if (fb->encoding) dec_row(&sb, fb->kind, "encoding", fb->encoding);
        for (size_t j = 0; j < fb->nserves; j++) {
            StrBuf v = { 0 };
            pcrec_sb_printf(&v, "%s when %s via %s", fb->serves[j].query,
                            fb->serves[j].encs, fb->serves[j].via);
            dec_row(&sb, fb->kind, "serves", v.p);
            pcrec_sb_free(&v);
        }
        for (int b = 0; fb->counts && b < 256; b++) {
            char r[48];
            if (!fb->counts[b]) continue;
            snprintf(r, sizeof r, "%02x %llu", b, fb->counts[b]);
            dec_row(&sb, fb->kind, "row", r);
        }
        for (size_t j = 0; j < fb->ncps; j++) {
            char r[48];
            snprintf(r, sizeof r, "U+%04lX %llu", (unsigned long)fb->cps[j].cp,
                     fb->cps[j].count);
            dec_row(&sb, fb->kind, "row", r);
        }
        if ((pv = block_prov(src, fb)))
            for (size_t f = 0; f < N_PROV_FIELDS; f++) {
                char fld[32];
                const char *v = prov_field(pv, f);
                if (!v) continue;
                snprintf(fld, sizeof fld, "provenance.%s", prov_fields[f].name);
                dec_row(&sb, fb->kind, fld, v);
            }
        if (nbl < sizeof bl / sizeof *bl) {
            memset(&bl[nbl], 0, sizeof bl[nbl]);
            bl[nbl].kind = fb->kind;
            bl[nbl].counts = fb->counts;
            bl[nbl].cps = fb->cps;
            bl[nbl].ncps = fb->ncps;
            nbl++;
        }
    }
    snprintf(dig, sizeof dig, "%016llx",
             (unsigned long long)pcrec_find_rows_digest(bl, nbl));
    pcrec_sb_puts(&sb, "#section item\n# the item's identity: the ITEM digest "
                  "(rows_digest, docs/spec/findings.md §8.1)\n#");
    pcrec_sb_join(&sb, "\t", ihdr, 2);
    pcrec_sb_putc(&sb, '\n');
    {
        const char *cells[2] = { "rows", dig };
        pcrec_sb_row(&sb, cells, 2);
    }
    return view_flush(o, &sb, err);
}

/* The derived views' section names (§9.5's last row): the `--list-analysis`
 * listings' and this kind's decoded view's. A file carrying one is a listing
 * fed back, refused by the resolver naming it. */
static const char *const analysis_derived[] = {
    "chain", "resolution", "declarations", "targets", "decoded", "item", NULL
};

const KsKind pcrec_ks_analysis = {
    .kind          = "analysis",
    .suffix        = ".rxt",
    .stops         = KS_STOP_BIT(KS_AT_S1) | KS_STOP_BIT(KS_AT_DIRS) |
                     KS_STOP_BIT(KS_AT_STORE),
    .flag_classify = KS_CLS_NAME_ONLY,
    .list_classify = KS_CLS_NAME_ELSE_FILE,
    .revs          = false,
    .s2_mismatch   = KS_S2_FALLTHROUGH_NOTE,
    .s2_multi      = KS_S2_REFUSE,
    .entry_match   = KS_ENTRY_EXACT,
    .join          = KS_JOIN_SLASH,
    .bare_view     = KS_VIEW_SHIPPED,
    .r4            = KS_R4_EXEMPT,
    .list_surface  = KS_LIST_CLI,
    .cli_flag      = "--analysis",
    .cfg_line      = "analysis",
    .list_flag     = "--list-analysis",
    .noun          = "analysis",
    .nouns         = "analyses",
    .item_noun     = "bundle",
    .item          = &pcrec_find_rows_role,
    .stamp         = &pcrec_find_rate_role,
    .probe         = analysis_probe,
    .write_canonical = analysis_write_canonical,
    .write_decoded   = analysis_write_decoded,
    .derived_sections = analysis_derived,
};
