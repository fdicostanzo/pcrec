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
 * no-filesystem mode, scripts/findgen.c — §8, §13 B1 (3). The default
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
 * primitive that answers it: PICK -> the reader's positional rightmost,
 * COMPARE -> false, MASS -> the uniform rate's mass (cardinality). A reader
 * hands the accessor's result to a primitive and never tests it, which is
 * what stops two readers of one question spelling two NONE answers (R13:
 * rightmost against leftmost).
 *
 * A RUN LONGER THAN `PCREC_MAX_REQ_RUN_EMIT` IS TRUNCATED, NEVER SPLIT into
 * two compares (Frank's ruling of 2026-09-22): to the window of that length
 * containing the scan member with the lowest mass, ties leftmost. A second
 * compare would be a second mechanism with its own cost question and no
 * measured need (D77). */

#include <stdlib.h>
#include <string.h>

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
 * reader (scripts/findgen.c). The generator itself links a stage-0
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

/* The store's bundles are contiguous in the table in store order (findgen
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

bool pcrec_find_name_ok(const char *s, size_t n)
{
    if (n == 0 || s[0] < 'a' || s[0] > 'z') return false;
    for (size_t i = 1; i < n; i++)
        if (!((s[i] >= 'a' && s[i] <= 'z') || (s[i] >= '0' && s[i] <= '9') ||
              s[i] == '_' || s[i] == '-'))
            return false;
    return true;
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

/* The vocabulary as DATA. The query vocabulary is this table's third column,
 * never a second list; a row whose kind the schema does not admit yet
 * (`bigram`, B4) is still the spec-stated vocabulary, so the reader refuses
 * `via markov1` on a `freq` block as the wrong KIND's derivation rather than
 * as an unknown word. */
static const PcrecFindDeriv find_derivs[] = {
    { "freq",   "unigram",       "byte-rate"  },
    { "cpfreq", "encode-utf8",   "byte-rate"  },
    { "cpfreq", "encode-latin1", "byte-rate"  },
    { "bigram", "markov1",       "run-rarity" },
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

/* The byte-rate this compile's CHAIN declares for its encoding, into `fr`:
 * the ONE block the selection rule picks (§2.4, §4.4), derived by its
 * `serves` line's `via`. No such block -> NONE (`byte_rate_have` stays
 * false). A chain the attempt never resolved (a `Ctx` built outside `compile_driver`) reads
 * as the built-in `default` alone — the terminal every chain ends in. */
static void find_derive_byte_rate(Ctx *cx, PcrecFindRec *fr)
{
    const char *enc = pcrec_enc_by_id(cx->opt->encoding)->name;
    PcrecFindLink dflt;
    PcrecFindChain one = { &dflt, 0 };
    const PcrecFindChain *chain = &fr->chain;
    const PcrecFindTblBlock *fb;
    const PcrecFindServe *sv = NULL;
    size_t link = 0;
    int nr;
    if (chain->n == 0) {
        if (pcrec_find_store_link("default", PCREC_FIND_STOP_DEFAULT, &dflt))
            one.n = 1;
        chain = &one;
    }
    fb = pcrec_find_chain_answer(chain, "byte-rate", enc, &link, &sv);
    if (!fb) return;
    nr = pcrec_find_block_byte_rate(fb, sv->via, fr->byte_rate, NULL);
    if (nr == -1)
        pcrec_ctx_fail(cx, 0, "analysis '%s': its '%s' block at line "
                       "%zu counts nothing via %s, so it has no byte-rate",
                       fb->bundle, fb->kind, fb->line, sv->via);
    if (nr != 0)
        pcrec_ctx_fail(cx, 0, "internal error: analysis '%s': its "
                       "'%s' block at line %zu normalizes to a "
                       "byte-rate that breaks its own postcondition",
                       fb->bundle, fb->kind, fb->line);
    fr->byte_rate_have = true;
    fr->byte_rate_bundle = chain->links[link].bundle;
    fr->byte_rate_digest = pcrec_find_byte_rate_digest(fr->byte_rate);
}

/* ---- THE STAMP AND THE DIGEST (design §7) -------------------------------- */

/* One FNV-1a-64 step over `n` bytes. FNV and not SHA-256: this is identity
 * against accidental change, not an adversarial setting, and it keeps
 * libpcrec dependency-free (design §7). */
static uint64_t fnv1a(uint64_t h, const unsigned char *p, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        h ^= p[i];
        h *= 0x100000001b3ull;
    }
    return h;
}

uint64_t pcrec_find_byte_rate_digest(const uint32_t ppm[256])
{
    const unsigned char tag[] = "pcrec-find-1\0byte-rate";
    uint64_t h = fnv1a(0xcbf29ce484222325ull, tag, sizeof tag);
    for (int b = 0; b < 256; b++) {
        unsigned char le[4] = { (unsigned char)ppm[b],
                                (unsigned char)(ppm[b] >> 8),
                                (unsigned char)(ppm[b] >> 16),
                                (unsigned char)(ppm[b] >> 24) };
        h = fnv1a(h, le, 4);
    }
    return h;
}

uint64_t pcrec_find_rows_digest(const PcrecFindTblBlock *blocks, size_t n)
{
    const unsigned char tag[] = "pcrec-find-rows-1";
    uint64_t h = fnv1a(0xcbf29ce484222325ull, tag, sizeof tag);
    for (size_t i = 0; i < n; i++) {
        h = fnv1a(h, (const unsigned char *)blocks[i].kind,
                  strlen(blocks[i].kind) + 1);
        for (size_t j = 0; j < blocks[i].ncps; j++) {
            uint32_t cp = blocks[i].cps[j].cp;
            unsigned long long c = blocks[i].cps[j].count;
            unsigned char row[12];
            for (int k = 0; k < 4; k++) row[k] = (unsigned char)(cp >> (8 * k));
            for (int k = 0; k < 8; k++) row[4 + k] = (unsigned char)(c >> (8 * k));
            h = fnv1a(h, row, sizeof row);
        }
        for (int b = 0; blocks[i].counts && b < 256; b++) {
            unsigned long long c = blocks[i].counts[b];
            unsigned char row[9];
            if (!c) continue;
            row[0] = (unsigned char)b;
            for (int k = 0; k < 8; k++) row[1 + k] = (unsigned char)(c >> (8 * k));
            h = fnv1a(h, row, sizeof row);
        }
    }
    return h;
}

const char *pcrec_find_stamp(Ctx *cx)
{
    const PcrecFindRec *fr = &cx->job->find;
    if (!fr->byte_rate_asked) return "";
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
        find_derive_byte_rate(cx, fr);
    }
    return fr->byte_rate_have ? fr->byte_rate : NULL;
}

/* ---- THE PRIMITIVES: one per rate QUESTION KIND, its NONE answer inside ----
 *
 * [D126 Q4] A uniform table substituted for NONE would be right for MASS
 * only: for PICK it answers `cand[0]`, which is the set pick's rightmost but
 * the run's LEFTMOST (R13's defect again), and for COMPARE it answers `true`
 * for every pair, a density claim no data supports. So each kind states its
 * own, once, here (design §6.1). */

/* The uniform rate's mass for `k` bytes: floor(k * 10^6 / 256). */
static uint32_t uniform_mass(int k)
{
    return (uint32_t)((unsigned long long)k * 1000000u / 256u);
}

/* The rate summed over the members of the cube (t, k): every byte t | f for
 * f a submask of the free bits ~k. A byte (k == 0xFF) is rate[t]. */
static uint32_t cube_mass(const uint32_t *rate, int t, int k)
{
    unsigned long long m = 0;
    int f = ~k & 0xFF;
    for (int b = f;; b = (b - 1) & f) {
        m += rate[t | b];
        if (!b) break;
    }
    return (uint32_t)m;
}

int pcrec_find_pick(const uint32_t *rate, const unsigned char *cand,
                    const unsigned char *care, int n, int rightmost)
{
    int i, best = 0;
    uint32_t lo;
    if (!rate) return rightmost;
    lo = cube_mass(rate, cand[0], care ? care[0] : 0xFF);
    for (i = 1; i < n; i++) {
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

/* The offset-k selection's per-set cost input (src/opt/prefix_k.c): the MASS
 * of `set` under this compile's byte-rate, capped at 1,000,000. It was the
 * one rate read with no gate at all (PFI R9); under NONE it is now the
 * uniform rate's mass, i.e. the set's CARDINALITY, the no-information prior
 * for choosing among sets (findings design §0.8). */
unsigned pcrec_find_set_ppm(Ctx *cx, const uint8_t set[256])
{
    return pcrec_find_set_mass(pcrec_find_byte_rate(cx), set);
}
