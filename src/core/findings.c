/* src/core/findings.c — THE FINDINGS SEAM: the byte-rate a compile reads,
 * the rate primitives, and every reader of a rate, in one file ([FINDINGS]
 * B1 = [PATFACTS] step 3.1; docs/design/findings/design.md §2.5, §6, §8,
 * docs/design/patfacts/design.md §4.2.2 carve-out (b), D122/D123/D126).
 *
 * THE DATA TIER. A byte-rate is DATA about a subject corpus under an
 * encoding, declared by the data (D123-4): a bundle's `freq` block says
 * `serves byte-rate when <encodings> via unigram`, and the accessor's whole
 * selection rule is "use what the data declares" (§2.4). At B1 the chain is
 * the built-in `default` alone (S3, the embedded store: `src/findings/<name>.rxt`
 * compiled in as text by scripts/embed_text.sh and parsed by the ONE `.rxt`
 * reader in its no-filesystem mode, §8). The default declares `byte` only,
 * so under `-e utf8` the answer is NONE. Resolution beyond it (S1/S2,
 * `--analysis`) is B2's.
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

/* `pcrec_find_store[]`: the store's TEXT, embedded at build time by
 * scripts/embed_text.sh (never committed). */
#include "findings_store.inc"

/* `pcrec_find_tbl[]`: the same text PRE-PARSED at build time by the one
 * reader (src/findings/findgen.c). The generator itself links a stage-0
 * library built with PCREC_FIND_STAGE0, whose table is empty: it parses and
 * never compiles, so it never reads one. */
#ifdef PCREC_FIND_STAGE0
static const PcrecFindTblBlock pcrec_find_tbl[1];
enum { PCREC_FIND_NTBL = 0 };
#else
#include "findings_table.inc"
enum { PCREC_FIND_NTBL = sizeof pcrec_find_tbl / sizeof *pcrec_find_tbl };
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

/* The byte-rate the built-in `default` declares for this compile's
 * encoding, into `fr`: the ONE block of that bundle whose `serves byte-rate
 * when …` line lists the encoding (§2.4, §4.4), derived `via unigram`. No
 * such block -> NONE (`byte_rate_have` stays false). At B1 the chain is the
 * default alone (S3); B2 walks a resolved chain here. */
static void find_derive_byte_rate(Ctx *cx, PcrecFindRec *fr)
{
    const char *enc = pcrec_enc_by_id(cx->opt->encoding)->name;
    size_t n;
    const PcrecFindTblBlock *tbl = pcrec_find_store_blocks(&n);
    for (size_t i = 0; i < n; i++) {
        const PcrecFindTblBlock *fb = &tbl[i];
        if (strcmp(fb->bundle, "default") != 0) continue;
        for (size_t j = 0; j < fb->nserves; j++) {
            int nr;
            if (strcmp(fb->serves[j].query, "byte-rate") != 0 ||
                !encs_list(fb->serves[j].encs, enc))
                continue;
            nr = pcrec_find_normalize(fb->counts, fr->byte_rate);
            if (nr == -1)
                pcrec_ctx_fail(cx, 0, "analysis '%s': its '%s' block at line "
                               "%zu counts nothing, so it has no byte-rate",
                               fb->bundle, fb->kind, fb->line);
            if (nr != 0)
                pcrec_ctx_fail(cx, 0, "internal error: analysis '%s': its "
                               "'%s' block at line %zu normalizes to a "
                               "byte-rate that breaks its own postcondition",
                               fb->bundle, fb->kind, fb->line);
            fr->byte_rate_have = true;
            fr->byte_rate_bundle = fb->bundle;
            fr->byte_rate_digest = pcrec_find_byte_rate_digest(fr->byte_rate);
            return;
        }
    }
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

int pcrec_find_pick(const uint32_t *rate, const unsigned char *cand, int n,
                    int rightmost)
{
    int i, best = 0;
    if (!rate) return rightmost;
    for (i = 1; i < n; i++)
        if (rate[cand[i]] < rate[cand[best]]) best = i;
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
    return cand[pcrec_find_pick(rate, cand, n, 0)];
}

/* Which member of the RUN the emitted `memchr` tests: the run in order, so
 * ties go to the LEFTMOST, and the positional rightmost is the NONE answer.
 * The per-candidate cost of the whole run check is the number of occurrences
 * of THIS byte in the window, which is why the choice is not cosmetic.
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
                              int n)
{
    return pcrec_find_pick(rate, bytes, n, n - 1);
}

/* Where a run longer than `PCREC_MAX_REQ_RUN_EMIT` is TRUNCATED to: the start
 * of the window of that length containing `idx` with the lowest mass, ties
 * to the leftmost by the strict `<` — so under NONE, where every window's
 * mass is equal, the leftmost.
 *
 * The scan member is in every candidate window by construction, so its own
 * rate is a constant of the comparison and no term has to be excluded. */
int pcrec_find_run_window_start(const uint32_t *rate,
                                const unsigned char *bytes, int n, int idx)
{
    int lo_s = idx - (PCREC_MAX_REQ_RUN_EMIT - 1), hi_s = idx;
    int s, best;
    uint32_t lo = 0;
    if (lo_s < 0) lo_s = 0;
    if (hi_s > n - PCREC_MAX_REQ_RUN_EMIT) hi_s = n - PCREC_MAX_REQ_RUN_EMIT;
    best = lo_s;
    for (s = lo_s; s <= hi_s; s++) {
        uint32_t t = pcrec_find_seq_mass(rate, bytes + s, PCREC_MAX_REQ_RUN_EMIT);
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
