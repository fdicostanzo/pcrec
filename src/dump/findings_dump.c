/* src/dump/findings_dump.c — `pcrec --list-analyses` and `pcrec
 * --list-analysis`, the ANALYSIS listings ([FINDINGS] B2;
 * docs/design/findings/design.md §5.2, docs/spec/findings.md §6).
 *
 * THREE VIEWS, one resolver. `--list-analyses` is the NAME LIST: one row per
 * bundle BUILT INTO this library (the store) — `-I` directories are never
 * enumerated, because resolution never discovers a bundle by listing a
 * directory (§4.1). `--list-analysis NAME` is the chain THIS invocation
 * would resolve for NAME, what each (query, encoding) resolves to, and the
 * named bundle's own blocks, declarations and provenance.
 * `--list-analysis FILE` is the per-TARGET view [r2 M-S8]: what each target
 * of a `.rxt` file resolves to after config joins and the fill-only
 * `--analysis`.
 *
 * THE RESOLUTION SECTION IS THE STAMP'S ANSWER BY CONSTRUCTION: it asks the
 * compile's own resolver (`pcrec_find_chain_build`), its own selection rule
 * (`pcrec_find_chain_answer`), its own normalization and its own digest, so
 * a `resolution` digest and an artifact's `<PREFIX>_FINDINGS` digest cannot
 * disagree except by a bug in the one shared path — which is why the
 * fixture that compares them uses an INDEPENDENT digest implementation
 * (tests/findings/findings_ref.py), never this file.
 *
 * Wire format: docs/spec/table_contract.md, every table a named `#section`,
 * every cell through `pcrec_sb_row` (the contract's own field escaping — a
 * user bundle's prose may carry a TAB). */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"
#include "pcrec.h"

/* The three kinds, in the canonical order every listing uses (§5.2). */
static const char *const FIND_KINDS[] = { "freq", "cpfreq", "bigram" };
#define N_FIND_KINDS (sizeof FIND_KINDS / sizeof *FIND_KINDS)

/* The two queries, in the stamp's fixed order (§7). */
static const char *const FIND_QUERIES[] = { "byte-rate", "run-rarity" };
#define N_FIND_QUERIES (sizeof FIND_QUERIES / sizeof *FIND_QUERIES)

/* The name a listing gives a stop (§5.2's `stop` column). */
static const char *stop_name(PcrecFindStop s)
{
    switch (s) {
    case PCREC_FIND_STOP_SOURCE:  return "source";
    case PCREC_FIND_STOP_DIR:     return "-I";
    case PCREC_FIND_STOP_STORE:   return "store";
    case PCREC_FIND_STOP_DEFAULT: return "store-default";
    }
    return "?";
}

/* A `#section NAME` line, its prose comment, then its header row. */
static void section(StrBuf *sb, const char *name, const char *comment,
                    const char *const *cols, size_t ncol)
{
    pcrec_sb_printf(sb, "#section %s\n# %s\n#", name, comment);
    pcrec_sb_join(sb, "\t", cols, ncol);
    pcrec_sb_putc(sb, '\n');
}

/* The `digest` cell for (query, enc) along `chain`: the 16-hex digest a stamp
 * would carry, or "none". Fills `cells` (link, bundle, kind, via, digest,
 * dropped) from the buffers, which must outlive the row; `dropped` is the
 * count of code-point occurrences the derivation dropped (`encode-latin1`'s
 * code points above U+00FF, design §2.4), 0 for the others, empty with no
 * answer. -1 with `err` filled when the answering block cannot be
 * normalized (the compile would refuse too). */
static int resolution_cells(const PcrecFindChain *chain, const char *query,
                            const char *enc, char linkbuf[24],
                            char digbuf[24], char dropbuf[24],
                            const char *cells[6], pcrec_error *err)
{
    size_t link = 0;
    const PcrecFindServe *sv = NULL;
    const PcrecFindTblBlock *fb =
        pcrec_find_chain_answer(chain, query, enc, &link, &sv);
    cells[0] = cells[1] = cells[2] = cells[3] = cells[5] = "";
    cells[4] = "none";
    if (!fb) return 0;
    snprintf(linkbuf, 24, "%zu", link);
    cells[0] = linkbuf;
    cells[1] = chain->links[link].bundle;
    cells[2] = fb->kind;
    cells[3] = sv->via;
    if (!strcmp(query, "byte-rate")) {
        uint32_t ppm[256];
        unsigned long long dropped = 0;
        if (pcrec_find_block_byte_rate(fb, sv->via, ppm, &dropped) != 0) {
            snprintf(err->msg, sizeof err->msg, "analysis '%s': its '%s' block "
                     "at line %zu counts nothing via %s, so it has no "
                     "byte-rate", fb->bundle, fb->kind, fb->line, sv->via);
            return -1;
        }
        snprintf(digbuf, 24, "%016llx",
                 (unsigned long long)pcrec_find_byte_rate_digest(ppm));
        snprintf(dropbuf, 24, "%llu", dropped);
        cells[4] = digbuf;
        cells[5] = dropbuf;
    }
    return 0;
}

/* The `chain` rows of `chain`, each led by `lead` cells (the per-target view
 * leads with its target; the name view with nothing). */
static void chain_rows(StrBuf *sb, const PcrecFindChain *chain,
                       const char *const *lead, size_t nlead)
{
    for (size_t l = 0; l < chain->n; l++) {
        const PcrecFindLink *k = &chain->links[l];
        char lk[24];
        const char *cells[8];
        size_t n = 0;
        snprintf(lk, sizeof lk, "%zu", l);
        for (size_t i = 0; i < nlead; i++) cells[n++] = lead[i];
        cells[n++] = lk;
        cells[n++] = k->bundle;
        cells[n++] = stop_name(k->stop);
        cells[n++] = k->location ? k->location : "";
        cells[n++] = k->include ? k->include : "";
        pcrec_sb_row(sb, cells, n);
    }
}

/* The `resolution` rows of `chain`: one per (query x every compile
 * encoding this build implements), led by `lead` cells. */
static int resolution_rows(StrBuf *sb, const PcrecFindChain *chain,
                           const char *const *lead, size_t nlead,
                           pcrec_error *err)
{
    for (size_t q = 0; q < N_FIND_QUERIES; q++)
        for (int id = 0; pcrec_enc_by_id(id); id++) {
            const PcrecEnc *e = pcrec_enc_by_id(id);
            char lk[24], dg[24], dr[24];
            const char *res[6], *cells[10];
            size_t n = 0;
            if (!pcrec_enc_ready(e)) continue;
            if (resolution_cells(chain, FIND_QUERIES[q], e->name, lk, dg, dr,
                                 res, err) != 0)
                return -1;
            for (size_t i = 0; i < nlead; i++) cells[n++] = lead[i];
            cells[n++] = FIND_QUERIES[q];
            cells[n++] = e->name;
            for (size_t i = 0; i < 6; i++) cells[n++] = res[i];
            pcrec_sb_row(sb, cells, n);
        }
    return 0;
}

/* The parsed `.rxt` text a link's bundle was read from, for its prose and
 * provenance (which a chain does not copy): the `-I` file, or the store's
 * embedded text. NULL with `err` filled on a parse failure. */
static RxtSource *link_source(const PcrecFindLink *k, pcrec_error *err)
{
    if (k->stop == PCREC_FIND_STOP_DIR)
        return pcrec_rxt_source_parse(k->location, err);
    {
        size_t len;
        const char *text = pcrec_find_store_text(k->bundle, &len);
        if (!text) {
            snprintf(err->msg, sizeof err->msg, "internal error: the store "
                     "has no text for '%s'", k->bundle);
            return NULL;
        }
        return pcrec_rxt_source_parse_buf(k->bundle, text, len, err);
    }
}

/* One `serves` line re-spelled as written: `<query> when <encs> via <via>`. */
static const char *serves_text(Arena *a, const RxtFindBlock *fb)
{
    size_t n = 1;
    char *t;
    for (size_t j = 0; j < fb->nserves; j++)
        n += strlen(fb->serves[j].query) + strlen(fb->serves[j].encs) +
             strlen(fb->serves[j].via) + 16;
    t = pcrec_arena_alloc(a, n);
    t[0] = 0;
    for (size_t j = 0; j < fb->nserves; j++)
        snprintf(t + strlen(t), n - strlen(t), "%s%s when %s via %s",
                 j ? "; " : "", fb->serves[j].query, fb->serves[j].encs,
                 fb->serves[j].via);
    return t;
}

/* The named bundle's own blocks (one section per kind it carries), its
 * declarations and its provenance, from the parse `src`. */
static void bundle_sections(StrBuf *sb, Arena *a, const RxtSource *src,
                            const char *bundle)
{
    static const char *const decl_cols[] = {
        "kind", "encoding", "serves", "question", "reader", "analyzer" };
    static const char *const prov_cols[] = { "kind", "field", "value" };
    for (size_t k = 0; k < N_FIND_KINDS; k++)
        for (size_t i = 0; i < src->nfblocks; i++) {
            const RxtFindBlock *fb = &src->fblocks[i];
            uint32_t ppm[256];
            bool freq = !strcmp(fb->kind, "freq");
            static const char *const freq_cols[] = { "key", "count", "ppm" };
            if (strcmp(fb->bundle, bundle) || strcmp(fb->kind, FIND_KINDS[k]))
                continue;
            section(sb, fb->kind, "the named bundle's own rows: one per nonzero "
                    "key, ascending; ppm (freq) is the normalized byte-rate "
                    "(design §2.5)", freq_cols, freq ? 3 : 2);
            bool rated = freq && pcrec_find_normalize(fb->counts, ppm) == 0;
            for (int b = 0; fb->counts && b < 256; b++) {
                char key[4], cnt[24], pp[16];
                const char *cells[3] = { key, cnt, pp };
                if (!fb->counts[b]) continue;
                snprintf(key, sizeof key, "%02x", b);
                snprintf(cnt, sizeof cnt, "%llu", fb->counts[b]);
                snprintf(pp, sizeof pp, "%u", rated ? ppm[b] : 0u);
                pcrec_sb_row(sb, cells, freq ? 3 : 2);
            }
            for (size_t j = 0; j < fb->ncps; j++) {
                char key[16], cnt[24];
                const char *cells[2] = { key, cnt };
                snprintf(key, sizeof key, "U+%04lX", (unsigned long)fb->cps[j].cp);
                snprintf(cnt, sizeof cnt, "%llu", fb->cps[j].count);
                pcrec_sb_row(sb, cells, 2);
            }
        }
    section(sb, "declarations", "one row per block of the named bundle: what "
            "its counted data is (encoding, prose) and what it serves",
            decl_cols, 6);
    for (size_t i = 0; i < src->nfblocks; i++) {
        const RxtFindBlock *fb = &src->fblocks[i];
        const char *cells[6];
        if (strcmp(fb->bundle, bundle)) continue;
        cells[0] = fb->kind;
        cells[1] = fb->encoding ? fb->encoding : "";
        cells[2] = serves_text(a, fb);
        cells[3] = fb->question ? fb->question : "";
        cells[4] = fb->reader ? fb->reader : "";
        cells[5] = fb->analyzer ? fb->analyzer : "";
        pcrec_sb_row(sb, cells, 6);
    }
    section(sb, "provenance", "one row per block x provenance field written",
            prov_cols, 3);
    for (size_t i = 0; i < src->nprovs; i++) {
        const RxtProv *r = &src->provs[i];
        const struct { const char *f, *v; } fld[] = {
            { "source", r->source }, { "url", r->url }, { "ref", r->ref },
            { "retrieved", r->retrieved }, { "license", r->license },
            { "license-note", r->license_note }, { "fidelity", r->fidelity },
            { "adaptation", r->adaptation }, { "attribution", r->attribution },
            { "bytes", r->bytes }, { "sha256", r->sha256 } };
        if (!r->data_kind || !r->block_name || strcmp(r->block_name, bundle))
            continue;
        for (size_t f = 0; f < sizeof fld / sizeof *fld; f++) {
            const char *cells[3] = { r->data_kind, fld[f].f, fld[f].v };
            if (fld[f].v) pcrec_sb_row(sb, cells, 3);
        }
    }
}

char *pcrec_find_list_names(void)
{
    static const char *const cols[] = { "name", "kinds", "serves", "include",
        "source", "license", "retrieved", "rows_digest", "bytes" };
    StrBuf sb = { 0 };
    Arena a = { 0 };
    pcrec_sb_puts(&sb, "# pcrec --list-analyses: one row per analysis BUILT "
                  "INTO this library (docs/spec/findings.md §6).\n"
                  "# -I directories are never enumerated; `--list-analysis "
                  "NAME -I DIR` shows what one resolves to.\n#");
    pcrec_sb_join(&sb, "\t", cols, sizeof cols / sizeof *cols);
    pcrec_sb_putc(&sb, '\n');
    for (size_t i = 0; pcrec_find_store_name(i); i++) {
        const char *name = pcrec_find_store_name(i);
        PcrecFindLink k;
        size_t len;
        const char *text = pcrec_find_store_text(name, &len);
        pcrec_error err = { 0 };
        RxtSource *src;
        char kinds[64] = "", serves[256] = "", dig[24], bytes[24];
        const char *source = "", *license = "", *retrieved = "";
        if (!pcrec_find_store_link(name, PCREC_FIND_STOP_STORE, &k)) continue;
        for (size_t kk = 0; kk < N_FIND_KINDS; kk++)
            for (size_t b = 0; b < k.nblocks; b++) {
                if (strcmp(k.blocks[b].kind, FIND_KINDS[kk])) continue;
                snprintf(kinds + strlen(kinds), sizeof kinds - strlen(kinds),
                         "%s%s", kinds[0] ? "," : "", FIND_KINDS[kk]);
                for (size_t j = 0; j < k.blocks[b].nserves; j++) {
                    const char *e = k.blocks[b].serves[j].encs;
                    while (*e) {
                        size_t n = strcspn(e, ",");
                        snprintf(serves + strlen(serves),
                                 sizeof serves - strlen(serves), "%s%s@%.*s",
                                 serves[0] ? "," : "",
                                 k.blocks[b].serves[j].query, (int)n, e);
                        e += n + (e[n] == ',');
                    }
                }
            }
        src = pcrec_rxt_source_parse_buf(name, text, len, &err);
        for (size_t p = 0; src && p < src->nprovs; p++)
            if (src->provs[p].data_kind) {
                const RxtProv *r = &src->provs[p];
                source = r->source ? r->source : "";
                license = r->license ? r->license : "";
                retrieved = r->retrieved ? r->retrieved : "";
                break;
            }
        snprintf(dig, sizeof dig, "%016llx",
                 (unsigned long long)pcrec_find_rows_digest(k.blocks, k.nblocks));
        snprintf(bytes, sizeof bytes, "%zu", len);
        {
            const char *cells[] = { name, kinds, serves,
                                    k.include ? k.include : "", source,
                                    license, retrieved, dig, bytes };
            pcrec_sb_row(&sb, cells, sizeof cells / sizeof *cells);
        }
        if (src) pcrec_rxt_source_free(src);
    }
    pcrec_arena_free(&a);
    return pcrec_sb_take(&sb);
}

static const char *const CHAIN_COLS[] = {
    "link", "bundle", "stop", "location", "include" };
static const char *const RES_COLS[] = {
    "query", "encoding", "link", "bundle", "kind", "via", "digest", "dropped" };

char *pcrec_find_list_name(const char *name, const char *const *dirs,
                           pcrec_error *err)
{
    StrBuf sb = { 0 };
    Arena a = { 0 };
    PcrecFindChain chain;
    RxtSource *src;
    memset(err, 0, sizeof *err);
    if (pcrec_find_chain_build(&a, name, NULL, dirs, true, &chain, err) != 0) {
        pcrec_arena_free(&a);
        return NULL;
    }
    pcrec_sb_printf(&sb, "# pcrec --list-analysis %s: the chain this "
                    "invocation resolves, what each (query, encoding) "
                    "answers from, and the named bundle's own data "
                    "(docs/spec/findings.md §6).\n", name);
    section(&sb, "chain", "one row per link, in search order; the last is the "
            "built-in default (by identity)", CHAIN_COLS, 5);
    chain_rows(&sb, &chain, NULL, 0);
    section(&sb, "resolution", "one row per query x compile encoding; digest "
            "is exactly what a <PREFIX>_FINDINGS stamp would carry, or none; "
            "dropped counts the code points its derivation dropped",
            RES_COLS, 8);
    if (resolution_rows(&sb, &chain, NULL, 0, err) != 0 ||
        !(src = link_source(&chain.links[0], err))) {
        pcrec_sb_free(&sb);
        pcrec_arena_free(&a);
        return NULL;
    }
    bundle_sections(&sb, &a, src, chain.links[0].bundle);
    pcrec_rxt_source_free(src);
    pcrec_arena_free(&a);
    return pcrec_sb_take(&sb);
}

/* The `with` list of target `t`, as written — the target row's own. */
static const char *target_with(const RxtSource *src, const RxtTarget *t)
{
    for (size_t i = 0; i < src->nrows; i++)
        if (src->rows[i].kind == RXT_DECL_TARGET && src->rows[i].line == t->line)
            return src->rows[i].with_list ? src->rows[i].with_list : "";
    return "";
}

char *pcrec_find_list_file(const char *path, const char *const *dirs,
                           const char *fill, pcrec_error *err)
{
    static const char *const tcols[] = {
        "target", "configs", "analysis", "named_by", "config_line" };
    static const char *const ccols[] = {
        "target", "link", "bundle", "stop", "location", "include" };
    static const char *const rcols[] = {
        "target", "query", "encoding", "link", "bundle", "kind", "via",
        "digest", "dropped" };
    StrBuf sb = { 0 };
    Arena a = { 0 };
    RxtSource *src;
    RxtTarget *ts = NULL;
    size_t nt = 0, nd = 0;
    PcrecFindChain *chains;
    memset(err, 0, sizeof *err);
    if (!(src = pcrec_rxt_source_parse(path, err))) return NULL;
    if (dirs) while (dirs[nd]) nd++;
    if (pcrec_rxt_source_resolve(src, dirs, nd, &ts, &nt, err) != 0) {
        pcrec_rxt_source_free(src);
        return NULL;
    }
    chains = pcrec_arena_alloc(&a, (nt ? nt : 1) * sizeof *chains);
    for (size_t i = 0; i < nt; i++) {
        const char *name = ts[i].analysis ? ts[i].analysis : fill;
        if (pcrec_find_chain_build(&a, name, src, dirs, i == 0, &chains[i],
                                   err) != 0) {
            char m[sizeof err->msg];
            snprintf(m, sizeof m, "%s:%zu: target '%s': %.200s", path,
                     ts[i].line, ts[i].prefix, err->msg);
            memcpy(err->msg, m, sizeof m);
            pcrec_rxt_source_free(src);
            pcrec_arena_free(&a);
            return NULL;
        }
    }
    pcrec_sb_printf(&sb, "# pcrec --list-analysis %s: what each TARGET's "
                    "analysis resolves to, after config joins and the "
                    "fill-only --analysis (docs/spec/findings.md §6).\n",
                    path);
    section(&sb, "targets", "one row per target; named_by is config, cli-fill "
            "or none", tcols, 5);
    for (size_t i = 0; i < nt; i++) {
        char cl[24] = "";
        const char *by = ts[i].analysis ? "config" : fill ? "cli-fill" : "none";
        const char *an = ts[i].analysis ? ts[i].analysis : fill ? fill : "";
        const char *cells[5];
        if (ts[i].analysis_line) snprintf(cl, sizeof cl, "%zu", ts[i].analysis_line);
        cells[0] = ts[i].prefix;
        cells[1] = target_with(src, &ts[i]);
        cells[2] = an;
        cells[3] = by;
        cells[4] = cl;
        pcrec_sb_row(&sb, cells, 5);
    }
    section(&sb, "chain", "one row per target x link, in search order",
            ccols, 6);
    for (size_t i = 0; i < nt; i++) chain_rows(&sb, &chains[i], &ts[i].prefix, 1);
    section(&sb, "resolution", "one row per target x query x compile "
            "encoding; digest is what that target's <PREFIX>_FINDINGS would "
            "carry, or none; dropped as in the name view", rcols, 9);
    for (size_t i = 0; i < nt; i++)
        if (resolution_rows(&sb, &chains[i], &ts[i].prefix, 1, err) != 0) {
            pcrec_sb_free(&sb);
            pcrec_rxt_source_free(src);
            pcrec_arena_free(&a);
            return NULL;
        }
    pcrec_rxt_source_free(src);
    pcrec_arena_free(&a);
    return pcrec_sb_take(&sb);
}
