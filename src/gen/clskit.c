/* src/gen/clskit.c — THE CLASS-MATCHER KIT, its sectioning DP, the whole-set
 * and atom forms, the `--tune` class-form selection, and the C each form
 * emits ([CLS-TREE] S1; docs/design/cls_tree_design.md §1, §6; D129, D131).
 *
 * WHAT IT PRODUCES. From a code-point set and nothing else (clskit.h's
 * Constraint 1), it produces a CHOICE of matcher form and the C text of a
 * `static inline int FN(unsigned cp)` that answers membership for EVERY
 * unsigned `cp`. Every form is branch-bounded by one global span test, so a
 * matcher never reads a table out of range whatever it is handed.
 *
 * WHAT IT READS THAT IS NOT A PARAMETER. Two tables, both below and both
 * data: `LEAF` (each per-section form's fit window and its size and op
 * model) and `PLACE` (the ruled placements: K's λ, the `0` row's gate, the
 * atom threshold, and D131 addendum 1's fitted dispatch/prologue term).
 * `ROWS` is the selection itself, over the per-SET forms only — no row
 * answers the atom table (its own comment, below); `TAB_ROWS` is the
 * artifact-level TABLE selection that does. No global state and no
 * function-local statics: every scratch array is the caller's arena.
 *
 * THE INVARIANT A CALLER MUST NOT BREAK. The input is sorted, disjoint and
 * NON-ADJACENT (cpset.c's own invariant). Two adjacent intervals would make
 * `ALL` claim a gap-free section that the model prices as two, and the
 * study's cross-check would stop meaning anything.
 *
 * THE REFERENCE IMPLEMENTATION is `studies/cls_tree_study/` (`kit.py`,
 * `section.py`, `wholeset.py`, `emit.py`, plus `clsets.py`/`proptest.py`
 * for the populations and `bench_bytes.py` for the atom partition).
 * `studies/` is "never built or tested by pcrec's make" (docs/CLAUDE.md),
 * so `tests/clskit/` does not import it live: `tests/clskit/ref/` is a
 * FROZEN, provenance-headed copy of those files (plus their two transitive
 * imports, `emit.py`/`loadgate.py`) that `tests/clskit/`'s own scripts
 * import instead (clss1b's fix; see `tests/clskit/CLAUDE.md`'s `ref/`
 * entry). It is re-implemented against here, and tests/clskit/ runs both
 * over the populations and compares their sectionings and table choices
 * (design §6's S1 row). Two departures from it, both deliberate:
 *   - the DP is INTEGER (Q16 fixed point, `log2_q16`) where the study's is
 *     floating point. A selection must be bit-reproducible across boxes,
 *     and a libm `log2` is not a promise that it is (prefix_k.c's rule);
 *   - `CUBES` is tier 1 only, the O(k) `cube_of` (design CT-1). The study's
 *     exact Quine-McCluskey tier was measured not worth running.
 */
#include <limits.h>
#include <string.h>

#include "core/internal.h"
#include "gen/clskit.h"

/* ---- the leaf model --------------------------------------------------- */

/* One per-section form: where it FITS (interval-count and span windows,
 * 0 = unbounded above) and what it COSTS in the model. `text*` are the
 * study's MEASURED per-section `.text` slopes (kit.py TEXT_BYTES; the
 * synthetic route, so a best case — see the ClsKit.bytes note). `ops*` are
 * the model's probe-op weights (ALU = CMP = 1, LOAD = 3, dependent load =
 * 5). They steer the size search only and time nothing (D131 item 2).
 * Rodata is not a column: it is a counted property of the table, computed
 * in `leaf_rodata`. */
typedef struct {
    const char *name;
    int         min_k, max_k;
    unsigned    min_w, max_w;
    int         text, text_per_iv;
    int         ops, ops_per_iv, ops_per_log2k;
} LeafModel;

static const LeafModel LEAF[CLSK_NLEAF] = {
    [CLSK_ALL]     = { "ALL",     1, 1,   0,   0,  22,  0,  0, 0, 0 },
    [CLSK_RANGES]  = { "RANGES",  1, 8,   0,   0,  12, 12,  0, 2, 0 },
    [CLSK_MASK64]  = { "MASK64",  1, 0,   0,  64,  24,  0,  3, 0, 0 },
    [CLSK_CUBES]   = { "CUBES",   2, 0,   0, 256,  24,  0,  2, 0, 0 },
    [CLSK_BITMAP]  = { "BITMAP",  1, 0,   0,   0,  60,  0,  6, 0, 0 },
    [CLSK_PAGE64]  = { "PAGE64",  1, 0, 128,   0,  24,  0, 12, 0, 0 },
    [CLSK_BSEARCH] = { "BSEARCH", 8, 0,   0,   0, 104,  0,  0, 0, 5 },
};

/* THE PLACEMENTS, one home. `kit_lambda`, `mid_min_sections` and
 * `z_mid_pct` are D131 item 1's ruled cells (Frank may move the last two).
 * `atom_*` are item 6's, read by `TAB_ROWS`' atom row: `atom_min_sites` is
 * where `256 + 8N` bytes of shared table and masks undercut `32N` bytes of
 * per-class bitmaps (N > 10.7, cls_tree_design.md §1.7.3 item 3), at no
 * measured time cost (the O-77 fair-dispatch re-run, §1.7 addendum: atom and
 * bitmap within noise at N = 4/16/32); `atom_max` is the 64-bit mask's
 * width, the form's own limit. `max_k` is the study's section cap (MAXK), a
 * search bound and not a statement about the answer (design §1.3). The
 * `*_text` values are the whole-set forms' MEASURED `.text` (whole_k53.tsv:
 * obj minus rodata; bitmap1 per clsfit_report.md).
 *
 * `kit_disp_bytes` is D131 ADDENDUM 1's fitted cell: K's DP-MODEL bytes
 * (rodata, exact, plus the study's per-form `.text` constants, `LEAF[]`
 * above) run a near-constant amount below the MEASURED object, because the
 * model omits the sectioned matcher's own dispatch tree and prologue
 * (`DISP_BYTES = 0`, "inside the measured slopes" — clss1_report.md §3).
 * Fit: `measured - model` over the K53 twelve at lambda=4
 * (studies/cls_tree_study/results/sweep_k53.tsv `total` column vs. the
 * model this file computes), a CONSTANT — mean 578 B, residuals -49..+113
 * (std ~44 B). A linear regression against the sectioning's own section
 * count was tried and rejected: R^2 = 0.06 (the fit explains 6% of the
 * variance a constant does not), so the extra term buys nothing and a
 * constant is both simpler and no worse. `kit_sel_bytes()` is the ONE
 * reader: it is added to `ClsKit.bytes` ONLY where the SELECTION compares
 * K's bytes against another form's (`P_P3_SMALLER`, `mid_gate`), never to
 * `ClsKit.bytes` itself — the DP's own sectioning model, and `out->bytes`
 * for a chosen `CLSF_KIT` row, stay the unadjusted model (D131 addendum 1:
 * "The DP's own sectioning model is unchanged").
 *
 * `kit_disp_bytes_byte` is the same fit over the BYTE population, and it is
 * 0: the 41 distinct corpus byte classes' standalone kit matchers (the
 * study's method, gcc-16 -O2 Mach-O) measure model + (-28..+26) B, mean
 * -0.3 B ([CLS-TREE] S2 review fixes, D139 item 1). A byte kit has one to
 * three sections and no dispatch tree to speak of, so the 578 B the K53
 * twelve carry is not a property of a byte kit; applied to one it would
 * price every byte kit above every byte table and retire the row by
 * arithmetic rather than by measurement. */
static const struct {
    unsigned kit_lambda;
    int      disp_ops;
    int      max_k;
    int      mid_min_sections;
    int      z_mid_pct;
    int      atom_min_sites;
    int      atom_max;
    unsigned page3_ts;
    int      page2_text, page3_text, bitmap1_text;
    int      kit_disp_bytes, kit_disp_bytes_byte;
} PLACE = {
    .kit_lambda = 4, .disp_ops = 1, .max_k = 64,
    .mid_min_sections = 16, .z_mid_pct = 126,
    .atom_min_sites = 11, .atom_max = 64,
    .page3_ts = 10,
    .page2_text = 68, .page3_text = 88, .bitmap1_text = 60,
    .kit_disp_bytes = 578, .kit_disp_bytes_byte = 0,
};

/* WHAT A TABLE COSTS WHERE IT IS READ, per `TAB_ROWS` representation: the
 * table's own bytes (paid once) and one read's `.text` (paid per call). The
 * read texts are MEASURED the way `kit_disp_bytes` was: a standalone
 * non-inline function doing exactly that read, gcc-16 -O2 Mach-O `__text`
 * (docs/dev/lanes/clss2_report.md, "Review fixes"). The byte-kit row's
 * smaller-than predicate reads the representation its site would take for
 * a lone set (`lone_table`); the atom table is never that (it needs
 * `atom_min_sites` classes), so its row is the shared table plus a mask. */
static const struct {
    int rodata, read_text;
} TABLE_COST[CLST_NFORM] = {
    [CLST_SITE]    = { 32, 32 },
    [CLST_ATOM]    = { 256 + 8, 32 },
    [CLST_BYTE256] = { 256, 16 },
};

/* The DP's fixed-point unit: an op weight of 1 is Q16 units, a byte is Q16
 * units, so λ·ops and bytes add without a float. */
static const long long Q16 = 65536;

/* ---- bit helpers -------------------------------------------------------- */

/* The number of significant bits in `v` (0 for 0). */
static unsigned bitlen(unsigned v)
{
    unsigned b = 0;
    while (v) { v >>= 1; b++; }
    return b;
}

/* log2(k) in Q16, floored, for k >= 1: the binary-digit squaring method on
 * a Q30 mantissa. Integer arithmetic only, so every box computes the same
 * digits (the file header's first departure). */
static long long log2_q16(unsigned k)
{
    unsigned ip = bitlen(k) - 1;
    uint64_t y = ((uint64_t)k << 30) >> ip;          /* k / 2^ip, in [1, 2) */
    long long r = (long long)ip * Q16;
    for (long long bit = Q16 >> 1; bit; bit >>= 1) {
        y = (y * y) >> 30;
        if (y >= ((uint64_t)2 << 30)) { y >>= 1; r += bit; }
    }
    return r;
}

/* ---- CUBES, tier 1 ------------------------------------------------------ */

/* Is section `i..j` exactly ONE don't-care cube over its base-relative
 * offsets? `pcrec_cube_of` (src/core/cpset.c, [OPT-LITSCAN] S4 P2) over the
 * section's own span: offsets past the span are unreachable behind the
 * dispatch, so they are don't-cares. On success `(x & care) == val` is
 * membership for every base-relative `x` in the span. */
static bool cube_of(const PcrecCpRange *iv, int i, int j,
                    unsigned *care, unsigned *val)
{
    return pcrec_cube_of(iv, i, j, iv[i].lo, iv[j].hi - iv[i].lo + 1, care, val);
}

/* ---- PAGE64's O(k) price ------------------------------------------------ */

/* The one 64-bit page mask interval `t` contributes to absolute page `p`. */
static uint64_t page_part(const PcrecCpRange *r, unsigned p)
{
    unsigned lo = r->lo > (p << 6) ? r->lo : (p << 6);
    unsigned hi = r->hi < (p << 6) + 63 ? r->hi : (p << 6) + 63;
    unsigned wd = hi - lo + 1;
    uint64_t m = wd >= 64 ? ~0ULL : ((1ULL << wd) - 1ULL);
    return m << (lo - (p << 6));
}

/* PAGE64's (page count, distinct leaf count) for section `i..j`, without
 * building its table. Pages are ABSOLUTE (`cp >> 6`), so only a page an
 * interval starts or ends in can be partial: every page strictly inside an
 * interval is all-ones and every untouched page all-zero. The distinct
 * count is therefore over <= 2k boundary masks plus those two constants.
 * `scratch` holds 2 * (j - i + 1) + 2 pages and masks. */
static void page64_price(const PcrecCpRange *iv, int i, int j,
                         unsigned *bp, uint64_t *bm,
                         unsigned *npages_out, unsigned *nleaf_out)
{
    unsigned npages = (iv[j].hi >> 6) - (iv[i].lo >> 6) + 1, touched = 0;
    int nb = 0;
    bool full = false;
    long prev_last = -1;

    for (int t = i; t <= j; t++) {
        unsigned pl = iv[t].lo >> 6, ph = iv[t].hi >> 6;
        if (ph - pl >= 2) full = true;
        touched += ph - pl + 1;
        if (prev_last == (long)pl) touched--;   /* a page two intervals share */
        prev_last = (long)ph;
        for (int e = 0; e < 2; e++) {
            unsigned p = e ? ph : pl;
            int f = nb - 1;
            while (f >= 0 && bp[f] != p) f--;
            if (f < 0) { bp[nb] = p; bm[nb] = 0; f = nb++; }
            bm[f] |= page_part(&iv[t], p);
        }
    }
    if (full) bm[nb++] = ~0ULL;
    if (touched < npages) bm[nb++] = 0;
    unsigned nd = 0;
    for (int z = 0; z < nb; z++) {
        int y = 0;
        while (y < z && bm[y] != bm[z]) y++;
        if (y == z) nd++;
    }
    *npages_out = npages;
    *nleaf_out = nd;
}

/* ---- the sectioning DP -------------------------------------------------- */

/* The cheapest leaf for one candidate section, in the model. */
typedef struct {
    ClsLeaf   leaf;
    unsigned  care, val;
    long long bytes;      /* rodata + text */
    long long value;      /* Q16: bytes + λ·ops */
} Offer;

/* The `.rodata` a leaf form puts in the table for section `i..j`: a counted
 * property of the table it would emit, never a model. */
static long long leaf_rodata(ClsLeaf l, unsigned w, int k,
                             unsigned npages, unsigned nleaf)
{
    switch (l) {
    case CLSK_ALL:
    case CLSK_RANGES:
    case CLSK_MASK64:
    case CLSK_CUBES:   return 0;
    case CLSK_BITMAP:  return (w + 7) / 8;
    case CLSK_PAGE64:  return (long long)npages * (nleaf <= 256 ? 1 : 2)
                              + 8LL * nleaf;
    case CLSK_BSEARCH: return 8LL * k;
    case CLSK_NLEAF:   break;
    }
    return 0;
}

/* Every allowed leaf that FITS section `i..j`, offered in LEAF order; the
 * first cheapest wins (strict `<`). Returns false when none fits. */
static bool section_best(const PcrecCpRange *iv, int i, int j, unsigned lam,
                         unsigned allow, unsigned *bp, uint64_t *bm, Offer *o)
{
    unsigned w = iv[j].hi - iv[i].lo + 1, npages = 0, nleaf = 0;
    int k = j - i + 1;
    bool have = false;

    if (w >= LEAF[CLSK_PAGE64].min_w)
        page64_price(iv, i, j, bp, bm, &npages, &nleaf);
    for (int f = 0; f < CLSK_NLEAF; f++) {
        const LeafModel *m = &LEAF[f];
        unsigned care = 0, val = 0;
        if (!((allow >> f) & 1)) continue;
        if (k < m->min_k || (m->max_k && k > m->max_k)) continue;
        if (w < m->min_w || (m->max_w && w > m->max_w)) continue;
        if (f == CLSK_CUBES && !cube_of(iv, i, j, &care, &val)) continue;
        long long bytes = leaf_rodata((ClsLeaf)f, w, k, npages, nleaf)
                          + m->text + (long long)m->text_per_iv * k;
        long long ops = ((long long)m->ops + (long long)m->ops_per_iv * k) * Q16
                        + m->ops_per_log2k * log2_q16((unsigned)k);
        long long value = bytes * Q16 + (long long)lam * ops;
        if (!have || value < o->value) {
            *o = (Offer){ (ClsLeaf)f, care, val, bytes, value };
            have = true;
        }
    }
    return have;
}

/* THE SECTIONING DP: over every partition of the interval list into
 * contiguous sections of at most `max_k` intervals, minimize
 *     Σ over sections ( bytes + λ·(ops + disp_ops) )
 * which is exact over contiguous partitions because a section's cost does
 * not depend on the others (design §1.2, the study's `section.py`). At the
 * table's λ it is `K`, the kit's size end (D131 items 1-2).
 *
 * `leaf_allow` restricts the leaf forms (bit per ClsLeaf, 0 = all). `ALL`
 * is always allowed so every set has a sectioning. The loop order (`i`
 * from `j` downward, strict `<`) is the study's, and it decides ties. */
void pcrec_clskit_partition(Arena *a, const PcrecCpRange *iv, int n,
                            unsigned lam, unsigned leaf_allow, ClsKit *out)
{
    *out = (ClsKit){ iv, n, NULL, 0, 0 };
    if (n <= 0) return;
    unsigned allow = (leaf_allow ? leaf_allow : ~0u) | (1u << CLSK_ALL);
    long long *best = pcrec_arena_alloc(a, sizeof *best * (size_t)(n + 1));
    int *from = pcrec_arena_alloc(a, sizeof *from * (size_t)(n + 1));
    Offer *pick = pcrec_arena_alloc(a, sizeof *pick * (size_t)(n + 1));
    unsigned *bp = pcrec_arena_alloc(a, sizeof *bp * (size_t)(2 * PLACE.max_k + 2));
    uint64_t *bm = pcrec_arena_alloc(a, sizeof *bm * (size_t)(2 * PLACE.max_k + 2));
    long long disp = (long long)lam * PLACE.disp_ops * Q16;

    for (int j = 1; j <= n; j++) best[j] = LLONG_MAX;
    for (int j = 0; j < n; j++) {
        int lo_i = j - PLACE.max_k + 1 < 0 ? 0 : j - PLACE.max_k + 1;
        for (int i = j; i >= lo_i; i--) {
            Offer o;
            if (best[i] == LLONG_MAX) continue;
            if (!section_best(iv, i, j, lam, allow, bp, bm, &o)) continue;
            long long v = best[i] + o.value + disp;
            if (v < best[j + 1]) { best[j + 1] = v; from[j + 1] = i; pick[j + 1] = o; }
        }
    }

    for (int j = n; j > 0; j = from[j]) out->nsec++;
    out->sec = pcrec_arena_alloc(a, sizeof *out->sec * (size_t)out->nsec);
    int s = out->nsec;
    for (int j = n; j > 0; j = from[j]) {
        const Offer *o = &pick[j];
        out->sec[--s] = (ClsSection){ from[j], j - 1, o->leaf, o->care, o->val };
        out->bytes += o->bytes;
    }
}

/* ---- the whole-set tables ----------------------------------------------- */

/* THE ONE DEDUP both page tables and the atom table use: numbers `nrec`
 * records of `words` 64-bit words each by FIRST OCCURRENCE (so the study's
 * dict-insertion numbering reproduces exactly), writing each record's
 * number to `idx` and the first occurrence of each distinct record to
 * `first`. Returns the distinct count. Open addressing over an FNV-1a hash;
 * the hash only picks a probe sequence and EQUALITY decides a match. */
static int intern_records(Arena *a, const uint64_t *rec, int nrec, int words,
                          int *idx, int *first)
{
    unsigned cap = 16;
    while (cap < 2u * (unsigned)nrec) cap <<= 1;
    int *slot = pcrec_arena_alloc(a, sizeof *slot * cap);
    int nd = 0;

    for (int r = 0; r < nrec; r++) {
        const uint64_t *x = rec + (size_t)r * (size_t)words;
        uint32_t h = fnv1a_32_init();
        for (int w = 0; w < words; w++) {
            h = fnv1a_32_mix(h, (uint32_t)x[w]);
            h = fnv1a_32_mix(h, (uint32_t)(x[w] >> 32));
        }
        unsigned p = h & (cap - 1);
        for (;; p = (p + 1) & (cap - 1)) {
            if (slot[p] == 0) {
                slot[p] = nd + 1;
                first[nd] = r;
                idx[r] = nd++;
                break;
            }
            const uint64_t *y = rec + (size_t)first[slot[p] - 1] * (size_t)words;
            if (!memcmp(x, y, sizeof *x * (size_t)words)) { idx[r] = slot[p] - 1; break; }
        }
    }
    return nd;
}

/* A whole set's page structure: the two-stage table `P2` and, when `ts` is
 * nonzero, the three-stage `P3` above it. Pages run from 0 (absolute, as
 * the study's `wholeset.py`), so the index covers `0..hi >> 6`. */
typedef struct {
    int       npages, nleaf;
    int      *pidx;          /* page -> leaf */
    uint64_t *leaf;          /* distinct leaves, first-occurrence order */
    int       bs, nblk, ntop;
    int      *top;           /* block of pages -> distinct block */
    int      *blk;           /* distinct blocks, bs page indices each */
} WholePages;

/* Build `P2` (and `P3` for `ts > 0`) for a non-empty set. */
static void build_pages(Arena *a, const PcrecCpRange *iv, int n, unsigned ts,
                        WholePages *w)
{
    int np = (int)(iv[n - 1].hi >> 6) + 1;
    uint64_t *mask = pcrec_arena_alloc(a, sizeof *mask * (size_t)np);
    int *first = pcrec_arena_alloc(a, sizeof *first * (size_t)np);

    for (int t = 0; t < n; t++)
        for (unsigned p = iv[t].lo >> 6; p <= iv[t].hi >> 6; p++)
            mask[p] |= page_part(&iv[t], p);
    w->npages = np;
    w->pidx = pcrec_arena_alloc(a, sizeof *w->pidx * (size_t)np);
    w->nleaf = intern_records(a, mask, np, 1, w->pidx, first);
    w->leaf = pcrec_arena_alloc(a, sizeof *w->leaf * (size_t)w->nleaf);
    for (int d = 0; d < w->nleaf; d++) w->leaf[d] = mask[first[d]];
    if (!ts) return;

    /* P3: blocks of `bs` page indices, the last one padded with its own
     * final index, deduplicated as records of `bs` words. */
    int bs = 1 << (ts - 6), nb = (np + bs - 1) / bs;
    uint64_t *blocks = pcrec_arena_alloc(a, sizeof *blocks * (size_t)nb * (size_t)bs);
    int *bfirst = pcrec_arena_alloc(a, sizeof *bfirst * (size_t)nb);
    for (int q = 0; q < nb * bs; q++)
        blocks[q] = (uint64_t)w->pidx[q < np ? q : np - 1];
    w->bs = bs;
    w->ntop = nb;
    w->top = pcrec_arena_alloc(a, sizeof *w->top * (size_t)nb);
    w->nblk = intern_records(a, blocks, nb, bs, w->top, bfirst);
    w->blk = pcrec_arena_alloc(a, sizeof *w->blk * (size_t)w->nblk * (size_t)bs);
    for (int d = 0; d < w->nblk; d++)
        for (int q = 0; q < bs; q++)
            w->blk[d * bs + q] = (int)blocks[(size_t)bfirst[d] * (size_t)bs + (size_t)q];
}

/* Bytes of one table element indexing `count` distinct things. */
static int idx_width(int count)
{
    return count <= 256 ? 1 : 2;
}

/* The model bytes (`.rodata` exact + measured `.text`) of a whole-set form
 * over a set. `PAGE3`/`PAGE2` materialize their tables to count them, so
 * the price and the emitted table cannot disagree (the study's §8 lesson:
 * its O(k) PAGE64 price once did). `CLSF_KIT`/`CLSF_ATOM` are not whole-set
 * forms and answer -1. */
long long pcrec_clskit_whole_bytes(Arena *a, ClsForm f,
                                   const PcrecCpRange *iv, int n)
{
    WholePages w;
    if (n <= 0) return 0;
    switch (f) {
    case CLSF_BITMAP1:
        return (iv[n - 1].hi - iv[0].lo + 1 + 7) / 8 + PLACE.bitmap1_text;
    case CLSF_PAGE2:
        build_pages(a, iv, n, 0, &w);
        return (long long)w.npages * idx_width(w.nleaf) + 8LL * w.nleaf
               + PLACE.page2_text;
    case CLSF_PAGE3:
        build_pages(a, iv, n, PLACE.page3_ts, &w);
        return (long long)w.ntop * idx_width(w.nblk)
               + (long long)w.nblk * w.bs * idx_width(w.nleaf)
               + 8LL * w.nleaf + PLACE.page3_text;
    case CLSF_KIT:
    case CLSF_ATOM:
    case CLSF_NFORM:
        break;
    }
    return -1;
}

/* ---- the atom table ([OPT-CLSPACK]) ------------------------------------- */

/* THE SHARED BYTE->ATOM TABLE over `nset` byte sets: an atom is a distinct
 * SIGNATURE (the set of classes a byte belongs to), numbered by first
 * occurrence over bytes 0..255. Returns false, building nothing usable,
 * when a set has a member above 0xFF or the partition needs more than
 * `atom_max` atoms (a 64-bit mask per class is the test). */
bool pcrec_clskit_atoms(Arena *a, const PcrecCpRange *const *sets,
                        const int *nivs, int nset, ClsAtomTable *out)
{
    int words = (nset + 63) / 64;
    uint64_t *sig;
    int idx[256], first[256];

    memset(out, 0, sizeof *out);
    out->nset = nset;
    for (int k = 0; k < nset; k++)
        if (nivs[k] > 0 && sets[k][nivs[k] - 1].hi > 0xFF) return false;
    if (words == 0) words = 1;
    sig = pcrec_arena_alloc(a, sizeof *sig * 256 * (size_t)words);
    for (int k = 0; k < nset; k++)
        for (int t = 0; t < nivs[k]; t++)
            for (unsigned b = sets[k][t].lo; b <= sets[k][t].hi; b++)
                sig[b * (unsigned)words + (unsigned)k / 64] |= 1ULL << (k % 64);
    out->natoms = intern_records(a, sig, 256, words, idx, first);
    if (out->natoms > PLACE.atom_max) return false;
    out->mask = pcrec_arena_alloc(a, sizeof *out->mask * (size_t)(nset ? nset : 1));
    for (int b = 0; b < 256; b++) {
        out->atom[b] = (unsigned char)idx[b];
        for (int k = 0; k < nset; k++)
            if ((sig[b * words + k / 64] >> (k % 64)) & 1)
                out->mask[k] |= 1ULL << idx[b];
    }
    return true;
}

/* ---- THE SELECTION ------------------------------------------------------ */

/* The predicates, a CLOSED tag set evaluated by ONE exhaustive switch
 * (`pred_holds`): a new predicate is a new tag and a new arm, never a
 * stored callable (the definitions table's rule, definitions_table.md r43). */
typedef enum {
    P_TRUE,
    P_BYTE,
    P_BYTE_ONE,
    P_BYTE_FOLD,
    P_KIT_SMALLER,
    P_P3_SMALLER,
    P_MID_P2,
    P_MID_B1,
    P_MID
} ClsPred;

/* The five `--tune` positions as mask bits, ordinal from `-2`. */
enum { TP_M2, TP_M1, TP_0, TP_P1, TP_P2 };
#define TPOS(p) (1u << (p))

/* D131 item 1 (code-point classes) and items 4-5 (byte classes), as ONE
 * first-match table. A row fires where its position bit is set, its deny
 * is not, and its predicate holds; the first such row's form is the
 * answer. The last row is undeniable and always holds, so every set gets
 * a form. `+2`'s "as `0`" fallback is row order, not a special case: with
 * `speed-*` denied, `mid-page3` (which lists `+2`) answers exactly as `0`
 * does.
 *
 * NO ATOM ROW ([OPT-CLSPACK], D131 item 6, per the manager's clss1b
 * ruling). D131 item 6's "N ~ 11 live class sites" counts sites ACROSS AN
 * ARTIFACT, a fact this per-SET table cannot see — a set is chosen without
 * knowing how many other byte-class sites its own artifact carries, and a
 * table row here would be answering a question it has no input for. The
 * atom table's FORM, its emitter (`pcrec_clskit_emit_atom_table`/
 * `pcrec_clskit_emit_atom`) and its differential all stay (§2.1 below):
 * choosing IT is the ARTIFACT-LEVEL table `TAB_ROWS` below, walked once
 * over every table-reading byte class, not a per-set `ROWS` outcome.
 *
 * THE BYTE ROWS ([CLS-TREE] S2, D131 item 5, D138, D139). `byte-range`
 * comes first at every position and site because a one-interval set is one
 * compare and no table can beat it. The ASCII case pair takes the
 * [FORM-CHAR] fold compare in TWO rows: `byte-fold` at the size-leaning
 * positions, at both sites, and `byte-fold-default` at `0`/`+1`/`+2` on the
 * VM only — D138 Q1 holds the default fold pending FORM-CHAR2's timing, and
 * the scan edge's default for a fold pair stays its table, as it always
 * was. That measurement rules BOTH sites: a flip to the table deletes
 * `byte-fold-default`, a flip to the fold adds the scan site to it — one
 * row either way. `-fno-cls-fold` denies both (`CLSD_BYTE_FOLD`).
 * `byte-kit` fires at the size-leaning positions only where the kit is
 * SMALLER than the table its site would read (D139 item 1: `P_KIT_SMALLER`,
 * `P_P3_SMALLER`'s shape); `-fno-cls-kit` denies it. `byte-table` lists
 * every position and site so a denied or larger kit falls to a table
 * rather than to a code-point row; WHICH table is `TAB_ROWS`' choice. */
#define TP_ALL (TPOS(TP_M2) | TPOS(TP_M1) | TPOS(TP_0) | TPOS(TP_P1) | TPOS(TP_P2))
static const ClsRow ROWS[CLSR_NROWS] = {
    [CLSR_BYTE_RANGE] = { "byte-range",
      "byte set that is ONE interval (a single byte, a range, or all 256): "
      "one inline compare, every position",
      TP_ALL, CLSS_ALL, P_BYTE_ONE, CLSF_KIT, CLSD_NONE },
    [CLSR_BYTE_FOLD] = { "byte-fold",
      "byte set that is an ASCII case pair {X, x}: the inline fold compare, "
      "size-leaning positions, every site",
      TPOS(TP_M2) | TPOS(TP_M1), CLSS_ALL, P_BYTE_FOLD, CLSF_KIT, CLSD_BYTE_FOLD },
    [CLSR_BYTE_FOLD_DEFAULT] = { "byte-fold-default",
      "byte set that is an ASCII case pair {X, x}: the inline fold compare, "
      "default positions, VM only (D138 Q1, held)",
      TPOS(TP_0) | TPOS(TP_P1) | TPOS(TP_P2), CLSSITE(CLSS_VM),
      P_BYTE_FOLD, CLSF_KIT, CLSD_BYTE_FOLD },
    [CLSR_BYTE_KIT] = { "byte-kit",
      "byte set whose kit matcher is smaller than the table its site reads: "
      "the kit's byte forms, size-leaning positions only",
      TPOS(TP_M2) | TPOS(TP_M1), CLSS_ALL, P_KIT_SMALLER, CLSF_KIT, CLSD_BYTE_KIT },
    [CLSR_BYTE_TABLE] = { "byte-table",
      "byte set: a table (the default byte-class form, and every position's "
      "answer when the kit's byte forms are denied or larger)",
      TP_ALL, CLSS_ALL, P_BYTE, CLSF_BITMAP1, CLSD_BYTE_TABLE },
    [CLSR_SIZE_PAGE3] = { "size-page3",
      "bytes(P3) < bytes(K): the smaller of K and P3",
      TPOS(TP_M2) | TPOS(TP_M1), CLSS_ALL, P_P3_SMALLER, CLSF_PAGE3, CLSD_SIZE_PAGE3 },
    [CLSR_SPEED_PAGE2] = { "speed-page2",
      "the mid gate holds and bytes(P2) <= bytes(B1)",
      TPOS(TP_P2), CLSS_ALL, P_MID_P2, CLSF_PAGE2, CLSD_SPEED_PAGE2 },
    [CLSR_SPEED_BITMAP1] = { "speed-bitmap1",
      "the mid gate holds and bytes(B1) < bytes(P2)",
      TPOS(TP_P2), CLSS_ALL, P_MID_B1, CLSF_BITMAP1, CLSD_SPEED_BITMAP1 },
    [CLSR_MID_PAGE3] = { "mid-page3",
      "the mid gate: K has >= mid_min_sections sections and "
      "bytes(P3) <= z_mid x bytes(K)",
      TPOS(TP_0) | TPOS(TP_P1) | TPOS(TP_P2), CLSS_ALL, P_MID, CLSF_PAGE3, CLSD_MID_PAGE3 },
    [CLSR_KIT] = { "kit",
      "always",
      TP_ALL, CLSS_ALL, P_TRUE, CLSF_KIT, CLSD_NONE },
};

/* The selection's lazily-priced inputs for one set: each whole-set form's
 * bytes are computed on first ask (-1 = not yet). */
typedef struct {
    Arena              *a;
    const PcrecCpRange *iv;
    int                 n;
    const ClsSelectIn  *in;
    const ClsKit       *k;
    long long           whole[CLSF_NFORM];
} SelCtx;

/* A whole-set form's model bytes for the set under selection, memoized. */
static long long whole(SelCtx *s, ClsForm f)
{
    if (s->whole[f] < 0) s->whole[f] = pcrec_clskit_whole_bytes(s->a, f, s->iv, s->n);
    return s->whole[f];
}

/* True when every member of the set is a byte (vacuously for the empty set). */
static bool is_byte_set(const PcrecCpRange *iv, int n)
{
    return n == 0 || iv[n - 1].hi <= 0xFF;
}

/* True when the set is exactly an ASCII case pair {X, x}: two single
 * letters one bit (0x20) apart. That is what D23's parse-time fold makes of
 * a caseless letter, recognized from the set alone (Constraint 1). */
static bool is_ascii_fold_pair(const PcrecCpRange *iv, int n)
{
    return n == 2 && iv[0].lo == iv[0].hi && iv[1].lo == iv[1].hi
        && (iv[0].lo ^ iv[1].lo) == 0x20 && iv[0].lo >= 'A' && iv[0].lo <= 'Z';
}

/* K's byte ESTIMATE as read by the SELECTION's comparisons (D131 ADDENDUM
 * 1): the DP's own model bytes (`s->k->bytes`, unchanged) plus the fitted
 * dispatch/prologue term for the set's domain — `PLACE.kit_disp_bytes` for
 * a code-point set, `PLACE.kit_disp_bytes_byte` for a byte set (see PLACE's
 * comment for both fits). The ONLY reader is a predicate comparing K
 * against another form; `s->k->bytes` itself, and `out->bytes` for a chosen
 * `CLSF_KIT` row, are never adjusted. */
static long long kit_sel_bytes(SelCtx *s)
{
    return s->k->bytes + (is_byte_set(s->iv, s->n) ? PLACE.kit_disp_bytes_byte
                                                   : PLACE.kit_disp_bytes);
}

static ClsTabForm lone_table(int tune, ClsSite site);

/* The byte-kit row's predicate (D139 item 1): a byte set whose kit, written
 * `calls` times (each call inlines it), is smaller than the table its site
 * would read for it alone — that table once, plus one read per call. */
static bool kit_smaller(SelCtx *s)
{
    long long calls = s->in->calls > 0 ? s->in->calls : 1;
    ClsTabForm t = lone_table(s->in->tune, s->in->site);
    return is_byte_set(s->iv, s->n)
        && calls * kit_sel_bytes(s) < TABLE_COST[t].rodata + calls * TABLE_COST[t].read_text;
}

/* The `0` row's gate: `K` has enough sections that a dispatch tree is
 * being paid for, and `P3` costs at most `z_mid` times `K`'s (selection)
 * bytes. */
static bool mid_gate(SelCtx *s)
{
    return s->k->nsec >= PLACE.mid_min_sections
        && whole(s, CLSF_PAGE3) * 100 <= (long long)PLACE.z_mid_pct * kit_sel_bytes(s);
}

/* Does predicate `p` hold for the set under selection? */
static bool pred_holds(SelCtx *s, ClsPred p)
{
    switch (p) {
    case P_TRUE:       return true;
    case P_BYTE:       return is_byte_set(s->iv, s->n);
    case P_BYTE_ONE:   return s->n == 1 && is_byte_set(s->iv, s->n);
    case P_BYTE_FOLD:  return is_ascii_fold_pair(s->iv, s->n);
    case P_KIT_SMALLER: return kit_smaller(s);
    case P_P3_SMALLER: return whole(s, CLSF_PAGE3) < kit_sel_bytes(s);
    case P_MID_P2:     return mid_gate(s) && whole(s, CLSF_PAGE2) <= whole(s, CLSF_BITMAP1);
    case P_MID_B1:     return mid_gate(s) && whole(s, CLSF_BITMAP1) < whole(s, CLSF_PAGE2);
    case P_MID:        return mid_gate(s);
    }
    return false;
}

/* THE CLASS-FORM SELECTION: the first row of `ROWS` whose position bit is
 * set for `in->tune` (an out-of-range position reads as `balanced`, as
 * tune.c's own rows do), whose site bit is set for `in->site`, whose deny
 * is clear and whose predicate holds.
 * Always answers (the last row is undeniable). `out->kit` is `K` at the
 * table's λ whatever form wins (`in->kit`, when the caller has it). */
void pcrec_clskit_select(Arena *a, const PcrecCpRange *iv, int n,
                         const ClsSelectIn *in, ClsChoice *out)
{
    SelCtx s = { a, iv, n, in, &out->kit, { 0 } };
    int tune = pcrec_tune_valid(in->tune) ? in->tune : PCREC_TUNE_BALANCED;
    unsigned pos = TPOS(tune - PCREC_TUNE_MIN_SIZE);
    int nrow = (int)(sizeof ROWS / sizeof ROWS[0]);

    for (int f = 0; f < CLSF_NFORM; f++) s.whole[f] = -1;
    if (in->kit) out->kit = *in->kit;
    else pcrec_clskit_partition(a, iv, n, PLACE.kit_lambda, 0, &out->kit);
    for (int r = 0; r < nrow; r++) {
        const ClsRow *row = &ROWS[r];
        if (!(row->positions & pos) || !(row->sites & CLSSITE(in->site))) continue;
        if (row->deny != CLSD_NONE && ((in->deny >> row->deny) & 1)) continue;
        if (!pred_holds(&s, (ClsPred)row->pred)) continue;
        out->form = row->form;
        out->row = r;
        /* No `ROWS` row answers `CLSF_ATOM` (the comment above `ROWS`); the
         * two live forms here are `CLSF_KIT` (the DP's own MODEL bytes,
         * unadjusted by `kit_sel_bytes`'s selection-only term) and a
         * whole-set form. */
        out->bytes = row->form == CLSF_KIT ? out->kit.bytes : whole(&s, row->form);
        return;
    }
}

/* The selection table, for a listing or a check. */
const ClsRow *pcrec_clskit_rows(int *nrows)
{
    *nrows = (int)(sizeof ROWS / sizeof ROWS[0]);
    return ROWS;
}

/* ---- THE TABLE SELECTION ([OPT-CLSPACK], D131 item 6) --------------------
 *
 * How an artifact's TABLE-READING byte classes read their table. The input
 * is all of them at once, which is why this is its own first-match table
 * and not a `ROWS` row: "N live class sites" is a count over the artifact.
 * A row fires where its position and site bits are set, its deny is clear
 * and its predicate holds; the last row is undeniable and always holds.
 *
 * THE THREE REPRESENTATIONS ([CLS-TREE] S2, D139 item 2), each a row:
 *   - `atom`, the VM only: D131 item 6 rules it the DEFAULT at every
 *     position, and at `-2`/`-1` it is also smaller than the kit's byte
 *     forms at N >= 16 (cls_tree_design.md §1.7.3 item 3, clsfit's proposed
 *     `-2`/`-1` order: atom first, then the kit). When it fires every input
 *     class reads it, a `byte-kit` one included;
 *   - `scan-table`, the scan edge only: one 256-byte table per edge, a load
 *     addressed by the byte itself, which is the per-context choice the
 *     edge has always made ([OPT-5]) and is kept as this row's predicate
 *     until measured otherwise;
 *   - `site`, everywhere else: each class keeps its own `ROWS` form, a
 *     32-byte bitmap, or at the size-leaning positions its kit matcher.
 * The input is every byte class `ROWS` did NOT answer with an inline
 * compare. A later ruling moves a position or a site by editing the row. */
typedef enum {
    TABP_ALWAYS,
    TABP_ATOM_FITS
} ClsTabPred;

static const ClsTabRow TAB_ROWS[] = {
    { "atom",
      "at least atom_min_sites table-read byte classes, whose partition "
      "into atoms (bytes with the same class membership) has at most "
      "atom_max atoms: one shared 256-byte atom table and a 64-bit mask "
      "per class",
      TP_ALL, CLSSITE(CLSS_VM), TABP_ATOM_FITS, CLST_ATOM, CLSTD_ATOM },
    { "scan-table",
      "a scan edge's run test: one 256-byte table per edge, read by the "
      "byte itself",
      TP_ALL, CLSSITE(CLSS_SCAN), TABP_ALWAYS, CLST_BYTE256, CLSTD_NONE },
    { "site",
      "always: each class keeps its own form (a 32-byte bitmap, or its "
      "kit matcher at the size-leaning positions)",
      TP_ALL, CLSS_ALL, TABP_ALWAYS, CLST_SITE, CLSTD_NONE },
};

/* THE TABLE SELECTION over the `nset` byte sets an artifact's classes read
 * a table for at `site` (every member <= 0xFF), in the caller's order: the
 * first row of `TAB_ROWS` that fires. Always answers. `out->atoms` holds
 * the partition when the atom row wins; `pcrec_clskit_atoms` is the
 * predicate's own builder, so the table the caller emits is the one the
 * predicate measured. */
void pcrec_clskit_select_tables(Arena *a, const PcrecCpRange *const *sets,
                                const int *nivs, int nset, int tune,
                                ClsSite site, unsigned deny, ClsTabChoice *out)
{
    int t = pcrec_tune_valid(tune) ? tune : PCREC_TUNE_BALANCED;
    unsigned pos = TPOS(t - PCREC_TUNE_MIN_SIZE);
    int nrow = (int)(sizeof TAB_ROWS / sizeof TAB_ROWS[0]);

    memset(out, 0, sizeof *out);
    for (int r = 0; r < nrow; r++) {
        const ClsTabRow *row = &TAB_ROWS[r];
        bool holds = false;
        if (!(row->positions & pos) || !(row->sites & CLSSITE(site))) continue;
        if (row->deny != CLSTD_NONE && ((deny >> row->deny) & 1)) continue;
        switch ((ClsTabPred)row->pred) {
        case TABP_ALWAYS:
            holds = true;
            break;
        case TABP_ATOM_FITS:
            holds = nset >= PLACE.atom_min_sites
                 && pcrec_clskit_atoms(a, sets, nivs, nset, &out->atoms);
            break;
        }
        if (!holds) continue;
        out->form = row->form;
        out->row = r;
        return;
    }
}

/* The representation a LONE byte set would read at `site` — the table
 * selection over that one set. A set alone never meets the atom row's
 * `atom_min_sites`, so no partition is built and no arena is needed. */
static ClsTabForm lone_table(int tune, ClsSite site)
{
    ClsTabChoice ch;
    pcrec_clskit_select_tables(NULL, NULL, NULL, 1, tune, site, 0, &ch);
    return ch.form;
}

/* The table selection's rows, for a listing or a check. */
const ClsTabRow *pcrec_clskit_table_rows(int *nrows)
{
    *nrows = (int)(sizeof TAB_ROWS / sizeof TAB_ROWS[0]);
    return TAB_ROWS;
}

/* The one λ the table runs the DP at (`K`). */
unsigned pcrec_clskit_kit_lambda(void)
{
    return PLACE.kit_lambda;
}

/* The `ROWS` deny mask the public flags ask for: `-fno-cls-kit` denies
 * `byte-kit`, `-fno-cls-fold` both fold rows. The ONE mapping — every
 * caller of `pcrec_clskit_select` passes this, so a flag denies its row
 * wherever the table is read (D139 item 3). */
static const uint64_t DENY_FLAG[CLSD_NDENY] = {
    [CLSD_BYTE_KIT]  = PCREC_NO_CLS_KIT,
    [CLSD_BYTE_FOLD] = PCREC_NO_CLS_FOLD,
};

unsigned pcrec_clskit_deny_of(uint64_t flags)
{
    unsigned m = 0;
    for (int d = 0; d < CLSD_NDENY; d++)
        if (DENY_FLAG[d] && (flags & DENY_FLAG[d])) m |= 1u << d;
    return m;
}

/* The byte-class tests a site can take, for `--list-axes`: `ROWS`' byte
 * rows at `site`, each named as a stamp names it (`pcrec_clskit_test_name`,
 * a table read by the representation a lone set reads there), first row
 * per name, with the public flag that denies it (0 where none does).
 * Returns the count written, at most `cap`. */
size_t pcrec_clskit_byte_tests(ClsSite site, PcrecAxisCand *out, size_t cap)
{
    size_t n = 0;
    ClsTabForm tab = lone_table(PCREC_TUNE_BALANCED, site);
    for (int r = 0; r < CLSR_NROWS && n < cap; r++) {
        const ClsRow *row = &ROWS[r];
        if (!(row->sites & CLSSITE(site))) continue;
        switch ((ClsPred)row->pred) {
        case P_BYTE_ONE: case P_BYTE_FOLD: case P_KIT_SMALLER: case P_BYTE:
            break;
        case P_TRUE: case P_P3_SMALLER: case P_MID_P2: case P_MID_B1: case P_MID:
            continue;
        }
        ClsChoice ch = { row->form, r, { 0 }, 0 };
        const char *name = pcrec_clskit_test_name(pcrec_clskit_test(&ch), tab);
        bool seen = false;
        for (size_t q = 0; q < n; q++) seen = seen || !strcmp(out[q].name, name);
        if (seen) continue;
        out[n].name = name;
        out[n].deny = DENY_FLAG[row->deny];
        n++;
    }
    return n;
}

/* The `TAB_ROWS` deny mask the public flags ask for: the atom table is a
 * kit form, so `-fno-cls-kit` (D129 Q2's one kit-level switch) denies it as
 * `-fno-cls-pack` does. */
unsigned pcrec_clskit_tabdeny_of(uint64_t flags)
{
    return (flags & (PCREC_NO_CLS_PACK | PCREC_NO_CLS_KIT)) ? 1u << CLSTD_ATOM : 0;
}

/* How a byte class's test is spelled, read off its `ROWS` choice: the two
 * inline rows by their predicate (one interval; the fold pair), a kit row
 * as a kit call, and anything else as a table read. */
ClsTest pcrec_clskit_test(const ClsChoice *ch)
{
    switch ((ClsPred)ROWS[ch->row].pred) {
    case P_BYTE_ONE:  return CLS_TEST_RANGE;
    case P_BYTE_FOLD: return CLS_TEST_FOLD;
    case P_TRUE: case P_BYTE: case P_KIT_SMALLER: case P_P3_SMALLER:
    case P_MID_P2: case P_MID_B1: case P_MID:
        break;
    }
    return ch->form == CLSF_KIT ? CLS_TEST_KIT : CLS_TEST_TABLE;
}

/* The name a byte test reports in a stamp (`RX_DFA_SCAN_EDGE`'s values):
 * the inline and kit tests by kind, a table read by its representation.
 * `bitmap` is the 256-byte scan table's name from before it was a row, and
 * it stays that stamp value. */
const char *pcrec_clskit_test_name(ClsTest t, ClsTabForm f)
{
    switch (t) {
    case CLS_TEST_RANGE: return "range";
    case CLS_TEST_FOLD:  return "fold";
    case CLS_TEST_KIT:   return "kit";
    case CLS_TEST_TABLE: break;
    }
    switch (f) {
    case CLST_SITE:    return "bitmap32";
    case CLST_ATOM:    return "atom";
    case CLST_BYTE256: return "bitmap";
    case CLST_NFORM:   break;
    }
    return "?";
}

/* The design note's short names of the matcher forms. */
static const char *const FORM_NAMES[CLSF_NFORM] = { "K", "P3", "P2", "B1", "ATOM" };

/* The study's spelling of a leaf form ("ALL", "PAGE64", ...). */
const char *pcrec_clskit_leaf_name(ClsLeaf l)
{
    return (unsigned)l < CLSK_NLEAF ? LEAF[l].name : "?";
}

/* The design note's short name of a matcher form (`K`, `P3`, ...). */
const char *pcrec_clskit_form_name(ClsForm f)
{
    return (unsigned)f < CLSF_NFORM ? FORM_NAMES[f] : "?";
}

/* ---- the C emitters ----------------------------------------------------- */

/* One `static const TYPE NAME[n] = { ... };` of unsigned values, sixteen
 * to a line. `hex64` spells 64-bit leaves. */
static void emit_array(StrBuf *c, const char *type, const char *name,
                       int n, const void *vals, int elt, bool hex64)
{
    pcrec_sb_printf(c, "static const %s %s[%d] = {", type, name, n);
    for (int q = 0; q < n; q++) {
        pcrec_sb_puts(c, q % 16 ? " " : "\n    ");
        if (hex64)
            pcrec_sb_printf(c, "0x%016llXULL,", (unsigned long long)((const uint64_t *)vals)[q]);
        else if (elt == 1)
            pcrec_sb_printf(c, "%u,", (unsigned)((const unsigned char *)vals)[q]);
        else
            pcrec_sb_printf(c, "%d,", ((const int *)vals)[q]);
    }
    pcrec_sb_puts(c, "\n};\n");
}

/* The tables one section's leaf reads, named `<fn>_t<s>`. */
static void emit_leaf_tables(StrBuf *c, Arena *a, const char *fn, int s,
                             const PcrecCpRange *iv, const ClsSection *sc)
{
    unsigned base = iv[sc->first].lo, w = iv[sc->last].hi - base + 1;
    int k = sc->last - sc->first + 1;
    const char *t = pcrec_sb_fragf(a, "%s_t%d", fn, s);

    switch (sc->leaf) {
    case CLSK_ALL: case CLSK_RANGES: case CLSK_MASK64: case CLSK_CUBES:
        return;
    case CLSK_BITMAP: {
        int nb = (int)((w + 7) / 8);
        unsigned char *b = pcrec_arena_alloc(a, (size_t)nb);
        for (int q = sc->first; q <= sc->last; q++)
            for (unsigned x = iv[q].lo - base; x <= iv[q].hi - base; x++)
                b[x >> 3] |= (unsigned char)(1u << (x & 7));
        emit_array(c, "unsigned char", t, nb, b, 1, false);
        return;
    }
    case CLSK_PAGE64: {
        unsigned pbase = base >> 6;
        int np = (int)((iv[sc->last].hi >> 6) - pbase + 1);
        uint64_t *m = pcrec_arena_alloc(a, sizeof *m * (size_t)np);
        int *idx = pcrec_arena_alloc(a, sizeof *idx * (size_t)np);
        int *first = pcrec_arena_alloc(a, sizeof *first * (size_t)np);
        for (int q = sc->first; q <= sc->last; q++)
            for (unsigned p = iv[q].lo >> 6; p <= iv[q].hi >> 6; p++)
                m[p - pbase] |= page_part(&iv[q], p);
        int nl = intern_records(a, m, np, 1, idx, first);
        uint64_t *leaf = pcrec_arena_alloc(a, sizeof *leaf * (size_t)nl);
        for (int d = 0; d < nl; d++) leaf[d] = m[first[d]];
        emit_array(c, idx_width(nl) == 1 ? "unsigned char" : "unsigned short",
                   pcrec_sb_fragf(a, "%s_i", t), np, idx, 4, false);
        emit_array(c, "unsigned long long", pcrec_sb_fragf(a, "%s_l", t),
                   nl, leaf, 8, true);
        return;
    }
    case CLSK_BSEARCH: {
        int *lo = pcrec_arena_alloc(a, sizeof *lo * (size_t)k);
        int *hi = pcrec_arena_alloc(a, sizeof *hi * (size_t)k);
        for (int q = 0; q < k; q++) {
            lo[q] = (int)(iv[sc->first + q].lo - base);
            hi[q] = (int)(iv[sc->first + q].hi - base);
        }
        emit_array(c, "unsigned", pcrec_sb_fragf(a, "%s_lo", t), k, lo, 4, false);
        emit_array(c, "unsigned", pcrec_sb_fragf(a, "%s_hi", t), k, hi, 4, false);
        return;
    }
    case CLSK_NLEAF:
        return;
    }
}

/* One section's test, as the statement(s) that return its answer. The
 * dispatch above has established `base <= cp <= top`, so `x` (the
 * base-relative offset) is in `[0, w)` and a leaf needs no bound of its
 * own — only the gaps inside its span. */
static void emit_leaf(StrBuf *c, Arena *a, const char *fn, int s,
                      const PcrecCpRange *iv, const ClsSection *sc,
                      const char *ind)
{
    unsigned base = iv[sc->first].lo, w = iv[sc->last].hi - base + 1;
    const char *x = base ? pcrec_sb_fragf(a, "(cp - %uu)", base) : "cp";
    const char *t = pcrec_sb_fragf(a, "%s_t%d", fn, s);

    switch (sc->leaf) {
    case CLSK_ALL:
        pcrec_sb_printf(c, "%sreturn 1;\n", ind);
        return;
    case CLSK_RANGES:
        pcrec_sb_printf(c, "%sreturn (int)(", ind);
        for (int q = sc->first; q <= sc->last; q++) {
            unsigned lo = iv[q].lo - base, hi = iv[q].hi - base;
            if (q > sc->first) pcrec_sb_puts(c, " | ");
            if (lo == hi)            pcrec_sb_printf(c, "(%s == %uu)", x, lo);
            else if (lo == 0)        pcrec_sb_printf(c, "(%s <= %uu)", x, hi);
            else if (hi == w - 1)    pcrec_sb_printf(c, "(%s >= %uu)", x, lo);
            else                     pcrec_sb_printf(c, "((%s - %uu) <= %uu)", x, lo, hi - lo);
        }
        pcrec_sb_puts(c, ");\n");
        return;
    case CLSK_MASK64: {
        uint64_t m = 0;
        for (int q = sc->first; q <= sc->last; q++)
            for (unsigned b = iv[q].lo - base; b <= iv[q].hi - base; b++) m |= 1ULL << b;
        pcrec_sb_printf(c, "%sreturn (int)((0x%016llXULL >> %s) & 1u);\n",
                        ind, (unsigned long long)m, x);
        return;
    }
    case CLSK_CUBES: {
        unsigned full = (1u << (w > 1 ? bitlen(w - 1) : 1)) - 1u;
        if (sc->care == full)
            pcrec_sb_printf(c, "%sreturn (int)(%s == %uu);\n", ind, x, sc->val);
        else
            pcrec_sb_printf(c, "%sreturn (int)((%s & 0x%Xu) == 0x%Xu);\n",
                            ind, x, sc->care, sc->val);
        return;
    }
    case CLSK_BITMAP:
        pcrec_sb_printf(c, "%sreturn (int)((%s[%s >> 3] >> (%s & 7)) & 1u);\n",
                        ind, t, x, x);
        return;
    case CLSK_PAGE64:
        pcrec_sb_printf(c, "%sreturn (int)((%s_l[%s_i[(cp >> 6) - %uu]] >> (cp & 63)) & 1u);\n",
                        ind, t, t, base >> 6);
        return;
    case CLSK_BSEARCH:
        pcrec_sb_printf(c,
            "%s{\n"
            "%s    unsigned x = %s, a = 0, b = %du;\n"
            "%s    while (a < b) {\n"
            "%s        unsigned m = (a + b) >> 1;\n"
            "%s        if (x < %s_lo[m]) b = m;\n"
            "%s        else if (x > %s_hi[m]) a = m + 1;\n"
            "%s        else return 1;\n"
            "%s    }\n"
            "%s    return 0;\n"
            "%s}\n",
            ind, ind, x, sc->last - sc->first + 1, ind, ind, ind, t, ind, t,
            ind, ind, ind, ind);
        return;
    case CLSK_NLEAF:
        return;
    }
}

/* The balanced binary dispatch over sections `lo..hi`. INVARIANT on entry:
 * `base(lo) <= cp <= top(hi)` — the global bound establishes it for the
 * root, and both arms keep it, which is why no leaf tests its own bounds. */
static void emit_tree(StrBuf *c, Arena *a, const char *fn, const ClsKit *k,
                      int lo, int hi, const char *ind)
{
    if (lo == hi) {
        emit_leaf(c, a, fn, lo, k->iv, &k->sec[lo], ind);
        return;
    }
    int m = (lo + hi) / 2;
    const char *in2 = pcrec_sb_fragf(a, "%s    ", ind);
    pcrec_sb_printf(c, "%sif (cp <= %uu) {\n", ind, k->iv[k->sec[m].last].hi);
    emit_tree(c, a, fn, k, lo, m, in2);
    pcrec_sb_printf(c, "%s}\n", ind);
    pcrec_sb_printf(c, "%sif (cp < %uu) return 0;\n", ind, k->iv[k->sec[m + 1].first].lo);
    emit_tree(c, a, fn, k, m + 1, hi, ind);
}

/* The global bound every matcher opens with: outside `[lo, hi]`, not a
 * member. One unsigned compare, and none at all where `[lo, hi]` covers
 * every value the argument can take (`0..cp_max`) — a byte kit over a set
 * spanning 0..255 would otherwise carry a bound that is always false. */
static void emit_bound(StrBuf *c, unsigned lo, unsigned hi, unsigned cp_max)
{
    if (lo == 0 && hi >= cp_max) return;
    pcrec_sb_printf(c, "    if ((unsigned)(cp - %uu) > %uu) return 0;\n", lo, hi - lo);
}

/* The empty set's matcher. */
static void emit_empty(StrBuf *c, const char *fn)
{
    pcrec_sb_printf(c, "static inline int %s(unsigned cp)\n{\n    (void)cp;\n    return 0;\n}\n", fn);
}

/* THE KIT MATCHER for a sectioning: the sections' tables, then `FN`'s
 * global bound, balanced dispatch and leaves (the study's `emit.py`
 * shape). `cp_max` is the largest argument a caller can pass (0xFF for a
 * byte, `UINT_MAX` for a code point), which only the bound reads. Its
 * scratch text lives in a private arena freed on return. */
void pcrec_clskit_emit_kit(StrBuf *c, const char *fn, const ClsKit *k,
                           unsigned cp_max)
{
    Arena a = { NULL, c->cx };
    if (k->nsec <= 0) { emit_empty(c, fn); return; }
    for (int s = 0; s < k->nsec; s++)
        emit_leaf_tables(c, &a, fn, s, k->iv, &k->sec[s]);
    pcrec_sb_printf(c, "static inline int %s(unsigned cp)\n{\n", fn);
    emit_bound(c, k->iv[0].lo, k->iv[k->n - 1].hi, cp_max);
    emit_tree(c, &a, fn, k, 0, k->nsec - 1, "    ");
    pcrec_sb_puts(c, "}\n");
    pcrec_arena_free(&a);
}

/* A WHOLE-SET MATCHER (`P3`, `P2` or `B1`): its tables, then `FN`'s bound
 * and one branch-free lookup. */
void pcrec_clskit_emit_whole(StrBuf *c, Arena *a, const char *fn, ClsForm f,
                             const PcrecCpRange *iv, int n)
{
    WholePages w;
    if (n <= 0) { emit_empty(c, fn); return; }
    unsigned lo = iv[0].lo, hi = iv[n - 1].hi;
    const char *lt = NULL;

    switch (f) {
    case CLSF_BITMAP1: {
        int nb = (int)((hi - lo + 1 + 7) / 8);
        unsigned char *b = pcrec_arena_alloc(a, (size_t)nb);
        for (int q = 0; q < n; q++)
            for (unsigned x = iv[q].lo - lo; x <= iv[q].hi - lo; x++)
                b[x >> 3] |= (unsigned char)(1u << (x & 7));
        emit_array(c, "unsigned char", pcrec_sb_fragf(a, "%s_b", fn), nb, b, 1, false);
        pcrec_sb_printf(c, "static inline int %s(unsigned cp)\n{\n", fn);
        emit_bound(c, lo, hi, UINT_MAX);
        pcrec_sb_printf(c, "    cp -= %uu;\n    return (int)((%s_b[cp >> 3] >> (cp & 7)) & 1u);\n}\n",
                        lo, fn);
        return;
    }
    case CLSF_PAGE2:
        build_pages(a, iv, n, 0, &w);
        lt = idx_width(w.nleaf) == 1 ? "unsigned char" : "unsigned short";
        emit_array(c, lt, pcrec_sb_fragf(a, "%s_i", fn), w.npages, w.pidx, 4, false);
        emit_array(c, "unsigned long long", pcrec_sb_fragf(a, "%s_l", fn), w.nleaf, w.leaf, 8, true);
        pcrec_sb_printf(c, "static inline int %s(unsigned cp)\n{\n", fn);
        emit_bound(c, lo, hi, UINT_MAX);
        pcrec_sb_printf(c, "    return (int)((%s_l[%s_i[cp >> 6]] >> (cp & 63)) & 1u);\n}\n", fn, fn);
        return;
    case CLSF_PAGE3:
        build_pages(a, iv, n, PLACE.page3_ts, &w);
        emit_array(c, idx_width(w.nblk) == 1 ? "unsigned char" : "unsigned short",
                   pcrec_sb_fragf(a, "%s_t", fn), w.ntop, w.top, 4, false);
        emit_array(c, idx_width(w.nleaf) == 1 ? "unsigned char" : "unsigned short",
                   pcrec_sb_fragf(a, "%s_m", fn), w.nblk * w.bs, w.blk, 4, false);
        emit_array(c, "unsigned long long", pcrec_sb_fragf(a, "%s_l", fn), w.nleaf, w.leaf, 8, true);
        pcrec_sb_printf(c, "static inline int %s(unsigned cp)\n{\n", fn);
        emit_bound(c, lo, hi, UINT_MAX);
        pcrec_sb_printf(c,
            "    return (int)((%s_l[%s_m[(%s_t[cp >> %u] << %u) | ((cp >> 6) & %uu)]]"
            " >> (cp & 63)) & 1u);\n}\n",
            fn, fn, fn, PLACE.page3_ts, PLACE.page3_ts - 6, (unsigned)w.bs - 1);
        return;
    case CLSF_KIT:
    case CLSF_ATOM:
    case CLSF_NFORM:
        return;
    }
}

/* The artifact's ONE shared byte->atom table, named `tab`. */
void pcrec_clskit_emit_atom_table(StrBuf *c, const char *tab,
                                  const ClsAtomTable *t)
{
    emit_array(c, "unsigned char", tab, 256, t->atom, 1, false);
}

/* Class `k`'s ATOM MATCHER over the shared table `tab`: one load and one
 * shift of a 64-bit immediate. Bytes only; anything above 0xFF is not a
 * member. */
void pcrec_clskit_emit_atom(StrBuf *c, const char *fn, const char *tab,
                            const ClsAtomTable *t, int k)
{
    pcrec_sb_printf(c,
        "static inline int %s(unsigned cp)\n{\n"
        "    if (cp > 255u) return 0;\n"
        "    return (int)((0x%016llXULL >> %s[cp]) & 1u);\n}\n",
        fn, (unsigned long long)t->mask[k], tab);
}

/* A byte class's INLINE test of byte expression `byte`, for the two inline
 * `ROWS` answers: one interval (no test for all 256, an equality for one
 * byte, one compare from 0, otherwise the unsigned-subtract range) or the
 * ASCII fold pair (`(byte | 0x20) == lower`, one mask and one compare, no
 * load — docs/dev/form_char_step0.md §2). The ONE spelling of both, for the
 * VM's class reads and the DFA scan edge's run test alike (D139 item 2). */
void pcrec_clskit_emit_inline(StrBuf *c, const ClsChoice *ch, const char *byte)
{
    int lo = (int)ch->kit.iv[0].lo, hi = (int)ch->kit.iv[ch->kit.n - 1].hi;
    if (pcrec_clskit_test(ch) == CLS_TEST_FOLD)
        /* {lo, hi} with hi == lo | 0x20 by the row's own predicate: the
         * lowercase member is the compare constant, the mask folds the
         * other onto it. */
        pcrec_sb_printf(c, "(%s | 0x20) == %d", byte, hi);
    else if (lo == 0 && hi == 255) pcrec_sb_puts(c, "1");
    else if (lo == hi)             pcrec_sb_printf(c, "%s == %d", byte, lo);
    else if (lo == 0)              pcrec_sb_printf(c, "%s <= %d", byte, hi);
    else pcrec_sb_printf(c, "(unsigned)(%s - %d) <= %du", byte, lo, hi - lo);
}

/* A byte class's READ of byte expression `byte`, for the two non-inline
 * answers: a call of its kit matcher `name`, or a read of its table `name`
 * in representation `f` (a 32-byte bitmap, the 256-byte scan table, or the
 * class's atom matcher over the shared table). The ONE spelling of each,
 * for both sites. NULL for an inline test, which has no read. */
const char *pcrec_clskit_read(Arena *a, ClsTest t, ClsTabForm f,
                              const char *name, const char *byte)
{
    switch (t) {
    case CLS_TEST_RANGE:
    case CLS_TEST_FOLD:
        return NULL;
    case CLS_TEST_KIT:
        return pcrec_sb_fragf(a, "%s(%s)", name, byte);
    case CLS_TEST_TABLE:
        break;
    }
    switch (f) {
    case CLST_SITE:
        return pcrec_sb_fragf(a, "(%s[(%s) >> 3] >> ((%s) & 7)) & 1", name, byte, byte);
    case CLST_ATOM:
        return pcrec_sb_fragf(a, "%s(%s)", name, byte);
    case CLST_BYTE256:
        return pcrec_sb_fragf(a, "%s[%s]", name, byte);
    case CLST_NFORM:
        break;
    }
    return NULL;
}
