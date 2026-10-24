/* src/core/findings.c — THE FINDINGS SEAM: the byte-rate a compile reads,
 * the rate primitives, and every reader of a rate, in one file ([FINDINGS]
 * B1 = [PATFACTS] step 3.1; docs/design/findings/design.md §2.5, §6, §8,
 * docs/design/patfacts/design.md §4.2.2 carve-out (b), D122/D123/D126).
 *
 * THE DATA TIER. A byte-rate is DATA about a subject corpus under an
 * encoding, declared by the data (D123-4): a bundle's `freq` block says
 * `serves byte-rate when <encodings> via unigram`, and the accessor's whole
 * selection rule is "use what the data declares" (§2.4): the first block
 * along this compile's CHAIN serving the query under its encoding
 * (`pcrec_find_chain_answer`). The chain is resolved per attempt by
 * src/parse/rxt_find.c ([FINDINGS] B2: the compiling file, `-I DIR/<name>.rxt`,
 * the store) and always ends in the built-in `default`, found here by
 * identity: S3, the embedded store, is every `src/findings/<name>.rxt`
 * compiled in as its TEXT by scripts/embed_text.sh and as that text
 * PRE-PARSED (`make gen-findings`) by the ONE `.rxt` reader in its
 * no-filesystem mode, scripts/ksgen.c — §8, §13 B1 (3). The default
 * declares `byte` only, so with no analysis named the answer under
 * `-e utf8` is NONE.
 *
 * WHAT A RATE READER IS. Every member of a necessary set and every window of
 * a necessary run is SOUND for the emitted pre-check (`src/facts/req.c`
 * proves them), and every offset set the offset-k selection ranks is
 * necessary too, so a rate moves a SPEED and never an answer or a give-up
 * (§6.2a). The member that pays is the one a subject is least likely to
 * contain ([OPT-FREQPICK], docs/design/reqbyte_freq_pick.md), with PCRE2's
 * rightmost rule as the TIEBREAK.
 *
 * THE NONE ANSWER IS SPELLED ONCE PER QUESTION KIND [D126 Q4], inside the
 * primitive that answers it: PICK -> the argmin of the uniform mass, ties to
 * the reader's positional rightmost ([K82] (C)), COMPARE -> false, MASS ->
 * the uniform rate's mass (cardinality). A reader
 * hands the accessor's result to a primitive and never tests it, which is
 * what stops two readers of one question spelling two NONE answers (R13:
 * rightmost against leftmost).
 *
 * A RUN LONGER THAN `PCREC_MAX_REQ_RUN_EMIT` IS TRUNCATED, NEVER SPLIT into
 * two compares (Frank's ruling of 2026-09-22): to the window of that length
 * containing the scan member with the lowest mass, ties leftmost. A second
 * compare would be a second mechanism with its own cost question and no
 * measured need (D77). */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* The accessor's own file defines the functions the trace build's macros
 * (findings.h) stand in for, so it never sees those macros. */
#define PCREC_FIND_DEFINING
#include "core/internal.h"
#include "core/findings.h"
#include "enc/enc.h"

/* One bundle of the embedded store: its name and its `.rxt` text. */
typedef struct {
    const char *name;
    const char *text;
    size_t      len;
} PcrecFindStoreEntry;

/* `pcrec_find_store[]`: the store's TEXT, embedded (`make gen-findings`) by
 * scripts/embed_text.sh (committed; `make gen-findings`). */
#include "findings_store.inc"

/* `pcrec_find_tbl[]`: the same text PRE-PARSED (`make gen-findings`) by the one
 * reader (scripts/ksgen.c). The generator itself links a stage-0
 * library built with PCREC_FIND_STAGE0, whose table is empty: it parses and
 * never compiles, so it never reads one. */
#ifdef PCREC_FIND_STAGE0
static const PcrecFindTblBlock pcrec_find_tbl[1];
static const PcrecFindTblBundle pcrec_find_tbl_bundles[1];
enum { PCREC_FIND_NTBL = 0, PCREC_FIND_NBUNDLES = 0 };
#else
#include "findings_table.inc"
enum {
    PCREC_FIND_NTBL = sizeof pcrec_find_tbl / sizeof *pcrec_find_tbl,
    PCREC_FIND_NBUNDLES = sizeof pcrec_find_tbl_bundles /
                          sizeof *pcrec_find_tbl_bundles
};
#endif

/* ---- THE STORE (design §8) ------------------------------------------------ */

const char *pcrec_find_store_text(const char *name, size_t *len)
{
    for (size_t i = 0; i < sizeof pcrec_find_store / sizeof *pcrec_find_store; i++)
        if (!strcmp(pcrec_find_store[i].name, name)) {
            *len = pcrec_find_store[i].len;
            return pcrec_find_store[i].text;
        }
    return NULL;
}

const char *pcrec_find_store_name(size_t i)
{
    return i < sizeof pcrec_find_store / sizeof *pcrec_find_store
         ? pcrec_find_store[i].name : NULL;
}

const PcrecFindTblBlock *pcrec_find_store_blocks(size_t *n)
{
    *n = PCREC_FIND_NTBL;
    return pcrec_find_tbl;
}

const PcrecFindTblBundle *pcrec_find_store_bundles(size_t *n)
{
    *n = PCREC_FIND_NBUNDLES;
    return pcrec_find_tbl_bundles;
}

/* The store's bundles are contiguous in the table in store order (ksgen
 * writes each file's blocks together), so a link is a slice of it. */
bool pcrec_find_store_link(const char *name, PcrecFindStop stop,
                           PcrecFindLink *out)
{
    size_t nt, nbn, lo, hi = 0;
    const PcrecFindTblBlock *tbl = pcrec_find_store_blocks(&nt);
    const PcrecFindTblBundle *bun = pcrec_find_store_bundles(&nbn);
    lo = nt;
    for (size_t i = 0; i < nbn; i++) {
        if (strcmp(bun[i].name, name) != 0) continue;
        for (size_t j = 0; j < nt; j++)
            if (!strcmp(tbl[j].bundle, name)) {
                if (j < lo) lo = j;
                hi = j + 1;
            }
        memset(out, 0, sizeof *out);
        out->bundle = bun[i].name;
        out->stop = stop;
        out->include = bun[i].include;
        out->blocks = hi > lo ? &tbl[lo] : NULL;
        out->nblocks = hi > lo ? hi - lo : 0;
        return true;
    }
    return false;
}

/* ---- NORMALIZATION: counts -> byte-rate ppm (design §2.5, ONE function) ---- */

int pcrec_find_normalize(const unsigned long long c[256], uint32_t ppm[256])
{
    unsigned long long n = 0, m;
    long long r;
    int z = 0, big = 0;
    for (int b = 0; b < 256; b++) { n += c[b]; if (!c[b]) z++; }
    if (n == 0) return -1;
    m = 1000000ull - (unsigned long long)PCREC_FIND_FLOOR_PPM * (unsigned)z;
    r = 1000000;
    for (int b = 0; b < 256; b++) {
        unsigned long long v = c[b] ? c[b] * m / n : 0;
        if (v < PCREC_FIND_FLOOR_PPM) v = PCREC_FIND_FLOOR_PPM;
        ppm[b] = (uint32_t)v;
        r -= (long long)v;
        if (ppm[b] > ppm[big]) big = b;
    }
    /* The residue (which may be negative) goes to the LARGEST entry, ties to
     * the lowest byte: the strict `>` above keeps the first maximum. */
    ppm[big] = (uint32_t)((long long)ppm[big] + r);
    /* The two postconditions, checked rather than assumed (§2.5 step 5). */
    {
        unsigned long long t = 0;
        for (int b = 0; b < 256; b++) {
            if (ppm[b] < PCREC_FIND_FLOOR_PPM) return -2;
            t += ppm[b];
        }
        if (t != 1000000ull) return -2;
    }
    return 0;
}

/* ---- THE DERIVATIONS (design §2.4): the closed vocabulary, and the
 * arithmetic of each byte-rate derivation ------------------------------- */

/* The derivation vocabulary as DATA, each word naming its query by a row of
 * `find_queries[]` (below), never by a second spelling of the tag; a row
 * whose kind the schema does not admit yet (`bigram`, B4) is still the
 * spec-stated vocabulary, so the reader refuses `via markov1` on a `freq`
 * block as the wrong KIND's derivation rather than as an unknown word. */
static const PcrecFindDeriv find_derivs[] = {
    { "freq",   "unigram",       PCREC_FQ_BYTE_RATE  },
    { "cpfreq", "encode-utf8",   PCREC_FQ_BYTE_RATE  },
    { "cpfreq", "encode-latin1", PCREC_FQ_BYTE_RATE  },
    { "bigram", "markov1",       PCREC_FQ_RUN_RARITY },
};

const PcrecFindDeriv *pcrec_find_deriv(size_t i)
{
    return i < sizeof find_derivs / sizeof *find_derivs ? &find_derivs[i] : NULL;
}

/* A derived count is a sum of stored counts, each <= PCREC_MAX_FIND_COUNT
 * (2^40), over at most PCREC_MAX_FIND_CPFREQ_ROWS rows and four bytes each,
 * so it stays below 2^58 and `out[b] += c` cannot wrap before the ceiling
 * test sees it. */
int pcrec_find_derive_counts(const char *via, const unsigned long long *counts,
                             const PcrecFindCp *cps, size_t ncps,
                             unsigned long long out[256],
                             unsigned long long *dropped)
{
    bool utf8 = !strcmp(via, "encode-utf8");
    memset(out, 0, 256 * sizeof *out);
    if (dropped) *dropped = 0;
    if (!strcmp(via, "unigram")) {
        memcpy(out, counts, 256 * sizeof *out);
        return 0;
    }
    if (!utf8 && strcmp(via, "encode-latin1") != 0) return -2;
    for (size_t i = 0; i < ncps; i++) {
        unsigned char b[4];
        int n = 1;
        if (utf8) {
            n = pcrec_utf8_encode(cps[i].cp, b);
        } else if (cps[i].cp <= 0xFF) {
            b[0] = (unsigned char)cps[i].cp;
        } else {
            if (dropped) *dropped += cps[i].count;
            continue;
        }
        for (int k = 0; k < n; k++) {
            out[b[k]] += cps[i].count;
            if (out[b[k]] > PCREC_MAX_FIND_COUNT) return -1;
        }
    }
    return 0;
}

int pcrec_find_block_byte_rate(const PcrecFindTblBlock *fb, const char *via,
                               uint32_t ppm[256], unsigned long long *dropped)
{
    unsigned long long c[256];
    int r = pcrec_find_derive_counts(via, fb->counts, fb->cps, fb->ncps, c,
                                     dropped);
    if (r == -1) return -3;
    if (r != 0) return -2;
    return pcrec_find_normalize(c, ppm);
}

/* Is `enc` one of the comma-joined encoding names in `encs`? */
static bool encs_list(const char *encs, const char *enc)
{
    size_t n = strlen(enc);
    for (const char *s = encs; *s; ) {
        const char *e = strchr(s, ',');
        size_t k = e ? (size_t)(e - s) : strlen(s);
        if (k == n && !strncmp(s, enc, n)) return true;
        if (!e) break;
        s = e + 1;
    }
    return false;
}

const PcrecFindTblBlock *pcrec_find_chain_answer(const PcrecFindChain *chain,
                                                 const char *query,
                                                 const char *enc,
                                                 size_t *link,
                                                 const PcrecFindServe **serve)
{
    for (size_t l = 0; l < chain->n; l++) {
        const PcrecFindLink *k = &chain->links[l];
        for (size_t i = 0; i < k->nblocks; i++) {
            const PcrecFindTblBlock *fb = &k->blocks[i];
            for (size_t j = 0; j < fb->nserves; j++)
                if (!strcmp(fb->serves[j].query, query) &&
                    encs_list(fb->serves[j].encs, enc)) {
                    if (link) *link = l;
                    if (serve) *serve = &fb->serves[j];
                    return fb;
                }
        }
    }
    return NULL;
}

/* The byte-rate this compile's CHAIN declares for its encoding, into `fr`'s
 * memo, and what deriving it came to: the ONE block the selection rule picks
 * (§2.4, §4.4), derived by its `serves` line's `via`. No such block -> NONE
 * (`byte_rate_have` stays false). A chain the attempt never resolved (a
 * `Ctx` built outside `compile_driver`) reads as the built-in `default`
 * alone — the terminal every chain ends in. Derives once per attempt and
 * NEVER refuses: an answering block that normalizes to nothing is
 * UNDERIVABLE and a broken postcondition is BROKEN, both left for the ASK
 * path to raise (`find_raise_byte_rate`), so the analysis object's offer,
 * which derives on every attempt, refuses nothing (window_contract.md
 * §3.7.4a). */
static PcrecFindStatus find_derive_byte_rate_status(Ctx *cx, PcrecFindRec *fr)
{
    const char *enc = pcrec_enc_by_id(cx->opt->encoding)->name;
    PcrecFindLink dflt;
    PcrecFindChain one = { &dflt, 0 };
    const PcrecFindChain *chain = &fr->chain;
    const PcrecFindTblBlock *fb;
    const PcrecFindServe *sv = NULL;
    size_t link = 0;
    int nr;
    if (fr->byte_rate_status != PCREC_FIND_ST_UNDERIVED)
        return fr->byte_rate_status;
    if (chain->n == 0) {
        if (pcrec_find_store_link("default", PCREC_FIND_STOP_DEFAULT, &dflt))
            one.n = 1;
        chain = &one;
    }
    fb = pcrec_find_chain_answer(chain, "byte-rate", enc, &link, &sv);
    if (!fb) return fr->byte_rate_status = PCREC_FIND_ST_NONE;
    fr->byte_rate_block = fb;
    fr->byte_rate_via = sv->via;
    fr->byte_rate_bundle = chain->links[link].bundle;
    nr = pcrec_find_block_byte_rate(fb, sv->via, fr->byte_rate, NULL);
    if (nr == -1) return fr->byte_rate_status = PCREC_FIND_ST_UNDERIVABLE;
    if (nr != 0) return fr->byte_rate_status = PCREC_FIND_ST_BROKEN;
    fr->byte_rate_have = true;
    fr->byte_rate_digest = pcrec_find_byte_rate_digest(fr->byte_rate);
    return fr->byte_rate_status = PCREC_FIND_ST_OK;
}

/* The ASK path's refusal of a byte-rate the derivation could not produce:
 * today's two diagnostics, verbatim, raised only where a reader asked. */
static void find_raise_byte_rate(Ctx *cx, const PcrecFindRec *fr,
                                 PcrecFindStatus st)
{
    const PcrecFindTblBlock *fb = fr->byte_rate_block;
    if (st == PCREC_FIND_ST_UNDERIVABLE)
        pcrec_ctx_fail(cx, 0, "analysis '%s': its '%s' block at line "
                       "%zu counts nothing via %s, so it has no byte-rate",
                       fb->bundle, fb->kind, fb->line, fr->byte_rate_via);
    if (st == PCREC_FIND_ST_BROKEN)
        pcrec_ctx_fail(cx, 0, "internal error: analysis '%s': its "
                       "'%s' block at line %zu normalizes to a "
                       "byte-rate that breaks its own postcondition",
                       fb->bundle, fb->kind, fb->line);
}

/* ---- THE STAMP AND THE DIGEST (design §7) -------------------------------- */

/* The byte-rate's fold: the 256 derived ppm values, uint32 little-endian,
 * in byte order. FNV and its step are the knowledge module's one copy
 * (`pcrec_ks_fnv1a`, src/core/ksrc.c). */
static uint64_t find_rate_fold(uint64_t h, const void *doc, const char *query)
{
    const uint32_t *ppm = doc;
    (void)query;
    for (int b = 0; b < 256; b++) {
        unsigned char le[4] = { (unsigned char)ppm[b],
                                (unsigned char)(ppm[b] >> 8),
                                (unsigned char)(ppm[b] >> 16),
                                (unsigned char)(ppm[b] >> 24) };
        h = pcrec_ks_fnv1a(h, le, 4);
    }
    return h;
}

/* The rows' fold: per block, its kind and a NUL, then each nonzero
 * (key, count) ascending — a `cpfreq` row as `u32le, u64le`, a `freq` row as
 * `u8, u64le`. */
static uint64_t find_rows_fold(uint64_t h, const void *doc, const char *sub)
{
    const PcrecFindRowsDoc *d = doc;
    (void)sub;
    for (size_t i = 0; i < d->n; i++) {
        const PcrecFindTblBlock *bl = &d->blocks[i];
        h = pcrec_ks_fnv1a(h, bl->kind, strlen(bl->kind) + 1);
        for (size_t j = 0; j < bl->ncps; j++) {
            uint32_t cp = bl->cps[j].cp;
            unsigned long long c = bl->cps[j].count;
            unsigned char row[12];
            for (int k = 0; k < 4; k++) row[k] = (unsigned char)(cp >> (8 * k));
            for (int k = 0; k < 8; k++) row[4 + k] = (unsigned char)(c >> (8 * k));
            h = pcrec_ks_fnv1a(h, row, sizeof row);
        }
        for (int b = 0; bl->counts && b < 256; b++) {
            unsigned long long c = bl->counts[b];
            unsigned char row[9];
            if (!c) continue;
            row[0] = (unsigned char)b;
            for (int k = 0; k < 8; k++) row[1 + k] = (unsigned char)(c >> (8 * k));
            h = pcrec_ks_fnv1a(h, row, sizeof row);
        }
    }
    return h;
}

/* The two shipped domains are GRANDFATHERED byte for byte, terminator
 * included (`KS_DOMAIN` takes the literal's `sizeof`): renaming either moves
 * every `<PREFIX>_FINDINGS` stamp or every `rows_digest` (§9.2 part 5). */
const KsDigest pcrec_find_rate_role = {
    KS_DOMAIN("pcrec-find-1"), KS_SUB_QUERY, find_rate_fold
};
const KsDigest pcrec_find_rows_role = {
    KS_DOMAIN("pcrec-find-rows-1"), KS_SUB_NONE, find_rows_fold
};

uint64_t pcrec_find_byte_rate_digest(const uint32_t ppm[256])
{
    return pcrec_ks_digest(&pcrec_find_rate_role, ppm, "byte-rate");
}

uint64_t pcrec_find_rows_digest(const PcrecFindTblBlock *blocks, size_t n)
{
    PcrecFindRowsDoc d = { blocks, n };
    return pcrec_ks_digest(&pcrec_find_rows_role, &d, NULL);
}

unsigned pcrec_find_asked(const Ctx *cx)
{
    return cx->job->find.byte_rate_asked ? PCREC_FQ_BIT(PCREC_FQ_BYTE_RATE) : 0u;
}

const char *pcrec_find_stamp(Ctx *cx, unsigned consulted)
{
    PcrecFindRec *fr = &cx->job->find;
    if (!(consulted & PCREC_FQ_BIT(PCREC_FQ_BYTE_RATE))) return "";
    /* Another attempt or a part may be the one that asked, so this
     * attempt's memo is derived here if nothing on it has; a consulted
     * answer that cannot be derived refuses, as the ask did (§3.3 rule 9). */
    find_raise_byte_rate(cx, fr, find_derive_byte_rate_status(cx, fr));
    if (!fr->byte_rate_have) return "byte-rate=none";
    return pcrec_sb_fragf(&cx->arena, "byte-rate=%s:%016llx",
                          fr->byte_rate_bundle,
                          (unsigned long long)fr->byte_rate_digest);
}

/* ---- THE ACCESSOR ---------------------------------------------------------
 *
 * THE GATE LIVES HERE AND NOWHERE ELSE (D122 addendum 2 (3)): whether a rate
 * applies to this compile is what the data declares, decided once, by this
 * function; every reader receives a table or NULL and hands it to a
 * primitive untested. */

const uint32_t *pcrec_find_byte_rate(Ctx *cx)
{
    PcrecFindRec *fr = &cx->job->find;
    if (!fr->byte_rate_asked) {
        fr->byte_rate_asked = true;
        find_raise_byte_rate(cx, fr, find_derive_byte_rate_status(cx, fr));
    }
    return fr->byte_rate_have ? fr->byte_rate : NULL;
}

/* ---- THE QUERY VOCABULARY AND THE OFFER ([WINDOW-E1]) ----------------------
 *
 * window_contract.md §3.2 and §3.7.1. `find_queries[]` is the [FINDINGS]
 * query vocabulary's ONE home (findings.h's `PcrecFindQuery`), plus, per
 * row, what the offer needs that the vocabulary's readers do not: the
 * query's NON-RAISING derivation and its payload's digest. A row with no
 * payload shape (version 0) has neither: T-KIND lists it ABSENT before
 * asking anything of it. */

/* One query's answer for the offer: what deriving it came to, and on OK its
 * payload, its answering block and that block's bundle. Never refuses. */
typedef PcrecFindStatus (*FindAnswerFn)(Ctx *cx, PcrecFindRec *fr,
                                        const void **payload,
                                        const PcrecFindTblBlock **block,
                                        const char **bundle);

/* The byte-rate's answer: the memoized status derivation, read back. */
static PcrecFindStatus find_byte_rate_answer(Ctx *cx, PcrecFindRec *fr,
                                             const void **payload,
                                             const PcrecFindTblBlock **block,
                                             const char **bundle)
{
    PcrecFindStatus st = find_derive_byte_rate_status(cx, fr);
    *payload = fr->byte_rate_have ? fr->byte_rate : NULL;
    *block = fr->byte_rate_block;
    *bundle = fr->byte_rate_bundle;
    return st;
}

/* The digest of a byte-rate payload, computed from the payload the offer
 * hands over (never copied from the record), the stamp's own spelling. */
static uint64_t find_byte_rate_payload_digest(const void *payload)
{
    return pcrec_find_byte_rate_digest(payload);
}

static const struct {
    PcrecFindQuery q;
    FindAnswerFn   answer;
    uint64_t     (*digest)(const void *payload);
} find_queries[] = {
    [PCREC_FQ_BYTE_RATE]  = { { "byte-rate",  1, PCREC_FIND_UNMEASURED_ARRIVES },
                              find_byte_rate_answer,
                              find_byte_rate_payload_digest },
    [PCREC_FQ_RUN_RARITY] = { { "run-rarity", 0, PCREC_FIND_UNMEASURED_ABSENT },
                              NULL, NULL },
};
_Static_assert(sizeof find_queries / sizeof *find_queries == PCREC_FQ_N,
               "find_queries[] has one row per PCREC_FQ_* index");

const PcrecFindQuery *pcrec_find_query(size_t i)
{
    return i < PCREC_FQ_N ? &find_queries[i].q : NULL;
}

const char *pcrec_find_query_tags(Arena *a)
{
    const char *t = "";
    for (size_t i = 0; i < PCREC_FQ_N; i++)
        t = pcrec_sb_fragf(a, "%s%s%s", t, i ? ", " : "", find_queries[i].q.tag);
    return t;
}

/* The facts T-KIND reads about one query of this attempt. */
typedef struct {
    bool shaped;    /* the row carries a payload shape (version > 0) */
    bool answers;   /* a block along the chain serves it */
    bool derives;   /* ... and its derivation came to OK */
    bool prior;     /* ... and its stanza is a PRIOR's: `source authored`,
                       or `fidelity synthesized` (D162 add. 4: `measured`
                       needs a measured source and a non-synthesized
                       fidelity) */
    bool arrives;   /* the row's `unmeasured` column is ARRIVES */
} FindKindFacts;

static bool fk_no_shape(const FindKindFacts *f)  { return !f->shaped; }
static bool fk_undrv_arr(const FindKindFacts *f) { return f->answers && !f->derives && f->arrives; }
static bool fk_undrv(const FindKindFacts *f)     { return f->answers && !f->derives; }
static bool fk_measured(const FindKindFacts *f)  { return f->answers && f->derives && !f->prior; }
static bool fk_authored(const FindKindFacts *f)  { return f->answers && f->derives && f->prior && f->arrives; }
static bool fk_auth_abs(const FindKindFacts *f)  { return f->answers && f->prior; }
static bool fk_prior_none(const FindKindFacts *f) { return f->arrives; }
static bool fk_absent(const FindKindFacts *f)    { (void)f; return true; }

/* T-KIND (window_contract.md §3.2), first match, the same rows for every
 * query. A row's `table` says whether the answer's payload, bundle and
 * digest travel (PRIOR_AUTHORED and MEASURED). `underivable-arrives` reads
 * PRIOR_NONE: the answering block has no table, falling through to a later
 * link would break the selection rule, and pcrec's answer with no table IS
 * the no-information answer; nothing observes it unless a reader consults
 * the kind, which refuses the compile (§3.3 rule 9). */
static const struct {
    const char        *name;
    bool             (*applies)(const FindKindFacts *);
    PcrecFindKindState present;
    PcrecFindSource    source;
    bool               table;
} find_kind_rows[] = {
    { "no-shape",            fk_no_shape,   PCREC_FIND_KIND_ABSENT,  PCREC_FIND_SRC_UNSTATED,       false },
    { "underivable-arrives", fk_undrv_arr,  PCREC_FIND_KIND_PRESENT, PCREC_FIND_SRC_PRIOR_NONE,     false },
    { "underivable",         fk_undrv,      PCREC_FIND_KIND_ABSENT,  PCREC_FIND_SRC_UNSTATED,       false },
    { "measured",            fk_measured,   PCREC_FIND_KIND_PRESENT, PCREC_FIND_SRC_MEASURED,       true  },
    { "authored",            fk_authored,   PCREC_FIND_KIND_PRESENT, PCREC_FIND_SRC_PRIOR_AUTHORED, true  },
    { "authored-absent",     fk_auth_abs,   PCREC_FIND_KIND_ABSENT,  PCREC_FIND_SRC_UNSTATED,       false },
    { "prior-none",          fk_prior_none, PCREC_FIND_KIND_PRESENT, PCREC_FIND_SRC_PRIOR_NONE,     false },
    { "absent",              fk_absent,     PCREC_FIND_KIND_ABSENT,  PCREC_FIND_SRC_UNSTATED,       false },
};

/* Is the answering block's own stanza a prior's (FindKindFacts.prior)? */
static bool find_block_prior(const PcrecFindTblBlock *fb)
{
    return (fb->prov_source && !strcmp(fb->prov_source, "authored")) ||
           (fb->prov_fidelity && !strcmp(fb->prov_fidelity, "synthesized"));
}

void pcrec_find_offer(Ctx *cx, size_t query, PcrecFindOffer *out)
{
    PcrecFindRec *fr = &cx->job->find;
    const PcrecFindTblBlock *fb = NULL;
    const char *bundle = NULL;
    const void *payload = NULL;
    PcrecFindStatus st = PCREC_FIND_ST_NONE;
    FindKindFacts f = { 0 };
    size_t r = 0;
    f.shaped = find_queries[query].q.version > 0;
    f.arrives = find_queries[query].q.unmeasured == PCREC_FIND_UNMEASURED_ARRIVES;
    if (f.shaped)
        st = find_queries[query].answer(cx, fr, &payload, &fb, &bundle);
    f.answers = st != PCREC_FIND_ST_NONE;
    f.derives = st == PCREC_FIND_ST_OK;
    f.prior = fb && find_block_prior(fb);
    while (!find_kind_rows[r].applies(&f)) r++;   /* the last row applies */
    memset(out, 0, sizeof *out);
    out->row = find_kind_rows[r].name;
    out->present = find_kind_rows[r].present;
    out->source = find_kind_rows[r].source;
    if (!find_kind_rows[r].table) return;
    out->bundle = bundle;
    out->payload = payload;
    out->digest = find_queries[query].digest(payload);
    out->bytes = out->source == PCREC_FIND_SRC_MEASURED ? fb->prov_bytes : 0;
    out->fidelity = fb->prov_fidelity;
}

bool pcrec_find_byte_rate_answers(Ctx *cx)
{
    pcrec_find_byte_rate(cx);
    return cx->job->find.byte_rate_have;
}

#ifdef PCREC_KS_TRACE
/* The trace build's reader-attributed accessor (findings.h): the read, then
 * its record, so the record names the bundle that answered. */
const uint32_t *pcrec_find_byte_rate_at(Ctx *cx, const char *reader)
{
    const uint32_t *r = pcrec_find_byte_rate(cx);
    PcrecFindRec *fr = &cx->job->find;
    if (fr->trace_last != reader)
        fprintf(stderr, "KSTRACE\tanalysis\tbyte-rate\t%s\t%s\n", reader,
                fr->byte_rate_have ? fr->byte_rate_bundle : "none");
    fr->trace_last = reader;
    return r;
}

unsigned pcrec_find_set_ppm_at(Ctx *cx, const uint8_t set[256],
                               const char *reader)
{
    return pcrec_find_set_mass(pcrec_find_byte_rate_at(cx, reader), set);
}
#endif

/* ---- THE PRIMITIVES: one per rate QUESTION KIND, its NONE answer inside ----
 *
 * [D126 Q4] A uniform table substituted for NONE would be right for MASS
 * only: for COMPARE it answers `true` for every pair, a density claim no
 * data supports. So each kind states its own, once, here (design §6.1).
 * PICK's NONE answer is MASS's own (cardinality) since [K82] (C): its one
 * objection to a uniform table was the tie (`cand[0]`, the run's LEFTMOST,
 * R13's defect), and PICK ties to the reader's `rightmost` under both arms,
 * so a uniform cost answers `rightmost` wherever every candidate is one
 * byte, exactly as before. */

/* The uniform rate's mass for `k` bytes: floor(k * 10^6 / 256). */
static uint32_t uniform_mass(int k)
{
    return (uint32_t)((unsigned long long)k * 1000000u / 256u);
}

/* The rate summed over the members of the cube (t, k): every byte t | f for
 * f a submask of the free bits ~k. A byte (k == 0xFF) is rate[t]. NONE:
 * MASS's own answer, the uniform mass of the cube's 2^popcount(~k) members
 * (cardinality). */
static uint32_t cube_mass(const uint32_t *rate, int t, int k)
{
    unsigned long long m = 0;
    int f = ~k & 0xFF;
    if (!rate) return uniform_mass(1 << __builtin_popcount((unsigned)f));
    for (int b = f;; b = (b - 1) & f) {
        m += rate[t | b];
        if (!b) break;
    }
    return (uint32_t)m;
}

int pcrec_find_pick(const uint32_t *rate, const unsigned char *cand,
                    const unsigned char *care, int n, int rightmost)
{
    int i, best = rightmost;
    uint32_t lo = cube_mass(rate, cand[best], care ? care[best] : 0xFF);
    for (i = 0; i < n; i++) {
        uint32_t m = cube_mass(rate, cand[i], care ? care[i] : 0xFF);
        if (m < lo) { lo = m; best = i; }
    }
    return best;
}

bool pcrec_find_no_commoner(const uint32_t *rate, int p, int q)
{
    if (!rate) return false;
    return rate[p] <= rate[q];
}

uint32_t pcrec_find_set_mass(const uint32_t *rate, const uint8_t set[256])
{
    unsigned long long t = 0;
    int k = 0;
    for (int b = 0; b < 256; b++) if (set[b]) { k++; if (rate) t += rate[b]; }
    if (!rate) t = uniform_mass(k);
    return t > 1000000u ? 1000000u : (uint32_t)t;
}

uint32_t pcrec_find_seq_mass(const uint32_t *rate, const unsigned char *bytes,
                             int n)
{
    unsigned long long t = 0;
    if (!rate) return uniform_mass(n);
    for (int i = 0; i < n; i++) t += rate[bytes[i]];
    return (uint32_t)t;
}

/* ---- THE RATE READERS: each builds a candidate order and asks one primitive */

/* Which member of the necessary SET the emitted `memchr` tests. The order
 * `[rightmost, the other members 255..0]` IS the tie rule: ties go to the
 * threaded rightmost member when it is among the minima, and to the largest
 * such byte otherwise — the rule a loop that silently took "whichever bit it
 * found first" would break, and that `rb_intersect` already refuses. */
int pcrec_find_set_pick(const uint32_t *rate, const unsigned char bits[32],
                        int rightmost)
{
    unsigned char cand[256];
    int n = 0;
#ifdef PCREC_CAND_TRACE
    /* the trace build holds the tie rule's premise: `rightmost` is a member
     * of the set, and -1 only for an empty set */
    bool empty = true;
    for (int b = 0; b < 256; b++)
        if (bits[b >> 3] & (unsigned char)(1u << (b & 7))) empty = false;
    if (rightmost < 0 ? !empty
                      : rightmost > 255 ||
                        !(bits[rightmost >> 3] & (unsigned char)(1u << (rightmost & 7))))
        pcrec_fit_invariant_fail("set-pick-rightmost", rightmost < 0 ? "-1" : "a non-member",
                                 "a member of the set (-1 only when it is empty)",
                                 "pcrec_find_set_pick");
#endif
    if (rightmost < 0) return -1;
    cand[n++] = (unsigned char)rightmost;
    for (int b = 255; b >= 0; b--)
        if (b != rightmost && (bits[b >> 3] & (unsigned char)(1u << (b & 7))))
            cand[n++] = (unsigned char)b;
    return cand[pcrec_find_pick(rate, cand, NULL, n, 0)];
}

/* Which member of the RUN the emitted `memchr` tests: PICK over the run in
 * REVERSE order — `[n-1, n-2, ..., 0]` — the same shape `pcrec_find_set_pick`
 * already threads its own `rightmost` candidate first in. That order IS the
 * tie rule: a data tie goes to the RIGHTMOST member (the earliest candidate
 * in this order), matching the positional rightmost that is also the NONE
 * answer. The per-candidate cost of the whole run check is the number of
 * occurrences of THIS byte in the window, which is why the choice is not
 * cosmetic.
 *
 * [FIND-TIE] (2026-09-28, D126 Q4's own rule applied to itself) A tie
 * carries no information, so a PICK's data-tie answer should equal its NONE
 * answer's — and this reader was the one inconsistent spelling among the
 * three PICK readers in this file: `pcrec_find_set_pick`'s candidate order
 * already starts at `rightmost` (data tie -> rightmost, matching its own
 * NONE), while this reader's left-to-right order made a data tie go
 * LEFTMOST against a rightmost NONE (R13's shape again, this time between
 * one reader's own two arms rather than between two readers). Found on the
 * shipped ASCII-only `weblog`/`log` bundles under `-e utf8`, where every
 * byte >= 0x80 ties at the 2 ppm floor: naming an analysis re-created
 * [OPT-REQRUN-ENC]'s lead-byte defect one call down, in the argmin's own
 * tie rule rather than in the NONE fallback that row already fixed
 * (findb5_report.md §6, docs/dev/optloop/reqrunenc_census.md). Answer-
 * identical (every run byte is necessary regardless of which is scanned) —
 * a SPEED fix, like every other reader in this file.
 *
 * [OPT-REQRUN-ENC] The NONE answer WAS the leftmost, and pcrec-bench's O-60
 * finding falsified it under `-e utf8`: a run's LEFTMOST member is a lead
 * byte whenever the run opens mid-character, shared by every character in
 * that script block (measured: 12.0%/20.7% of the corpus/bench RUN-path
 * artifacts, docs/dev/optloop/reqrunenc_census.md). A run's last byte can be
 * a lead byte only if the run is truncated mid-character, which the census
 * found in ZERO of 912 real `-e utf8` runs, so the rightmost rule closes it
 * with no byte-range logic (D77). */
int pcrec_find_run_scan_index(const uint32_t *rate, const unsigned char *bytes,
                              const unsigned char *mask, int n)
{
    /* `bytes[0..n)`, n <= PCREC_MAX_REQ_RUN_SCAN by its one caller's own
     * bound (RbRun/ReqRun's `whole` array, src/facts/facts_derive.h,
     * src/facts/facts.h) — the only fact about `n` this file, below the
     * facts layer, is entitled to lean on for a fixed buffer's size.
     * GUARDED, not merely trusted: a caller that violates the bound gets a
     * loud stop here, never a silent `cand` overrun (this primitive has no
     * Ctx to route a diagnostic through, so it fails the way sb.c's own
     * no-error-channel sites do — coding_guide.md's fail-loudly rule, never
     * silent truncation). */
    if (n > PCREC_MAX_REQ_RUN_SCAN) abort();
    unsigned char cand[PCREC_MAX_REQ_RUN_SCAN], care[PCREC_MAX_REQ_RUN_SCAN];
    int i;
    for (i = 0; i < n; i++) {
        cand[i] = bytes[n - 1 - i];
        care[i] = mask[n - 1 - i];
    }
    return n - 1 - pcrec_find_pick(rate, cand, care, n, 0);
}

/* Where a run longer than `PCREC_MAX_REQ_RUN_EMIT` is TRUNCATED to: the start
 * of the window of that length containing `idx` with the lowest mass, ties
 * to the leftmost by the strict `<` — so on an exact run under NONE, where
 * every window's mass is equal, the leftmost.
 *
 * [OPT-LITSCAN] S4 C3: a window's mass is its MEMBERS' — T for an exact
 * position, every byte of the cube for a masked one (T and T | ~K for a
 * pair) — listed and handed to one SEQUENCE
 * MASS call, so MASS's own NONE answer (cardinality) applies with no branch
 * here: a window with more exact positions has fewer members and wins.
 *
 * The scan member is in every candidate window by construction, so its own
 * rate is a constant of the comparison and no term has to be excluded. */
int pcrec_find_run_window_start(const uint32_t *rate,
                                const unsigned char *bytes,
                                const unsigned char *mask, int n, int idx)
{
    int lo_s = idx - (PCREC_MAX_REQ_RUN_EMIT - 1), hi_s = idx;
    int s, best;
    uint32_t lo = 0;
    if (lo_s < 0) lo_s = 0;
    if (hi_s > n - PCREC_MAX_REQ_RUN_EMIT) hi_s = n - PCREC_MAX_REQ_RUN_EMIT;
    best = lo_s;
    for (s = lo_s; s <= hi_s; s++) {
        unsigned char mem[256 * PCREC_MAX_REQ_RUN_EMIT];
        int nm = 0;
        for (int j = s; j < s + PCREC_MAX_REQ_RUN_EMIT; j++) {
            int f = ~mask[j] & 0xFF;
            for (int b = f;; b = (b - 1) & f) {   /* every member of the cube */
                mem[nm++] = (unsigned char)(bytes[j] | b);
                if (!b) break;
            }
        }
        uint32_t t = pcrec_find_seq_mass(rate, mem, nm);
        if (s == lo_s || t < lo) { lo = t; best = s; }
    }
    return best;
}

/* A per-set cost input (the DFA candidate rate; the offset-k selection's
 * until D172 S2 commit 6 moved it into the memfn kit): the MASS of `set`
 * under this compile's byte-rate, capped at 1,000,000. It was the
 * one rate read with no gate at all (PFI R9); under NONE it is now the
 * uniform rate's mass, i.e. the set's CARDINALITY, the no-information prior
 * for choosing among sets (findings design §0.8). */
unsigned pcrec_find_set_ppm(Ctx *cx, const uint8_t set[256])
{
    return pcrec_find_set_mass(pcrec_find_byte_rate(cx), set);
}
