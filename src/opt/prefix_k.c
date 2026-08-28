/* [OPT-K] THE OFFSET-k PREFIX ANALYSIS — which bytes every match must carry,
 * at which offsets from its own start, and which of those offsets are worth
 * testing before the transition loop is entered.
 *
 * docs/design/offset_k_skip.md is the note; read §3 (the derivation's domain)
 * and §4 (the cost model) before changing anything here.
 *
 * THE ONE FACT THAT DECIDES WHERE THIS FILE LIVES AND WHAT IT WALKS. The
 * candidate-start filter pcrec shipped before this row derives its byte set
 * from the forward DFA's START STATE (`cand_from_escapes` in
 * src/gen/emit_dfa.c): the bytes on which the start state does not stay put.
 * That is exact at offset 0 and USELESS past it, because an ENG_UNANCH DFA
 * state is the merge of the threads from EVERY subject position — after four
 * bytes of `\d{4}-`, the state carries threads at 4, 3, 2, 1 and 0 digits, so
 * "a byte that does not return the machine to the start state" at offset 4 is
 * `[0-9-]`, not `-`, and the selectivity the row is after is gone.
 *
 * The thread whose bytes we want to constrain is the one from the CANDIDATE
 * START ALONE, and the only place it exists on its own is the pattern's own
 * NFA, walked from `Nfa.anch_start` — the state `nfa_wrap_unanchored` puts
 * the self-loop in FRONT of, and which it deliberately leaves pointing at the
 * pattern (src/ir/nfa.c). So: offsets >= 1 come from this walk, offset 0
 * keeps coming from the DFA derivation that already owns it, and no fact has
 * two sources.
 *
 * WHY IT IS SOUND. A match beginning at subject position p runs a thread from
 * `anch_start`; after j consumed bytes that thread sits in some NFA state of
 * `frontier[j]` (this walk's set, closed over epsilon and over every
 * assertion — an assertion is passed as though it held, which can only make a
 * set LARGER); its next byte is consumed by an N_CLASS state of that set; so
 * `s[p+j]` is in `S_j`, the union of those states' classes. The walk stops the
 * moment N_ACCEPT enters the frontier, because from there the match may be
 * over and `s[p+j]` need not exist at all. Every failure mode of the analysis
 * — an assertion it cannot evaluate, an alternation of unequal widths, a
 * bounded repeat that lets the frontier fan out — makes some `S_j` bigger and
 * the selection below decline it. There is no direction in which this file
 * can refuse a start the scan would have accepted.
 */

#include "core/internal.h"

#include <string.h>

/* ---- THE BYTE-FREQUENCY PRIOR -------------------------------------------
 *
 * D83's ruling, applied: the REAL prior is a file-general findings file
 * measured off the deployment's own exemplar, and this static table is the
 * FALLBACK for every compile that is not given one. The selection code below
 * reads `pcrec_byte_freq_ppm` and nothing else, so adopting a findings file
 * is a second implementation of THIS ONE FUNCTION and touches nothing else in
 * the row. **THAT HOOK IS NAMED AND NOT BUILT** (D77): no measured need has
 * asked for it yet, and the note's §4.4 states what measurement would.
 *
 * WHERE THE NUMBERS COME FROM, AND WHY NOT FROM THE BENCH. The obvious source
 * for a log-text prior is the comparative bench's own log lines — and using
 * them would be the exact failure `docs/dev/learnings.md` §3 catalogues: a
 * control that shares a source with the thing it controls. The table would
 * then be fitted to the subjects the optimization is measured on, and a good
 * measurement would prove nothing. So the mass is assigned from two
 * INDEPENDENT, citable priors and rounded to two significant figures:
 *
 *   - letters: the classical English letter-frequency ordering
 *     (etaoin shrdlu), scaled to 52% of the mass for lower case with upper
 *     case at a tenth of its lower-case twin;
 *   - space at 15% and newline at 1.2%, the usual whitespace share of prose;
 *   - digits at 0.9% EACH (9% together) and the structural punctuation of
 *     machine-written lines — `.` `:` `-` `/` `=` `"` `,` `_` and the
 *     brackets — raised well above their prose frequencies, because the
 *     population this prior is FOR is log lines and not novels;
 *   - every remaining byte, the whole 0x80-0xff half included, gets a floor
 *     of 2 ppm rather than zero: a zero would let the model believe a byte is
 *     IMPOSSIBLE and select a skip on a certainty it does not have.
 *
 * The units are parts per million. The assignment above was made in round
 * numbers and then NORMALISED to sum to exactly 1,000,000 — the residue of
 * the rounding is added to `' '`, the largest entry, so that the sum is a
 * checkable fact rather than an approximate one: `pcrec_byte_freq_total_ppm`
 * returns it and tests/codegen/run_offset_skip.sh §1 asserts 1000000. A
 * table that did not sum to one would make "the whole alphabet" cost
 * something other than one candidate per byte, which is the one place the
 * model's arithmetic assumes a probability. Integers, not doubles: the
 * selection must be bit-reproducible across boxes, which is the same reason
 * nothing else in this compiler computes in floating point.
 *
 * THE TABLE IS A PRIOR AND NOT A PROMISE. It orders bytes; it does not
 * predict any particular subject. Everything downstream of it is an
 * ANSWER-IDENTITY-preserving choice, so a badly-fitted prior costs speed on
 * some input and can never cost a match. */
static const unsigned byte_freq_ppm_tbl[256] = {
    /* 00  . . . . . . . . . \t \n . . \r . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,   2492,   9969,      2,      2,    831,      2,      2,
    /* 10  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
    /* 20  SP ! " # $ % & ' ( ) * + , - . / */
    124561,    249,   3323,    498,    249,    415,    332,   1246,   1661,   1661,    332,    665,   6646,   4984,   9969,   4154,
    /* 30  0 1 2 3 4 5 6 7 8 9 : ; < = > ? */
      7476,   7476,   7476,   7476,   7476,   7476,   7476,   7476,   7476,   7476,   6646,    665,    332,   3323,    332,    415,
    /* 40  @ A B C D E F G H I J K L M N O */
       665,   5416,    989,   1844,   2816,   8423,   1479,   1337,   4037,   4610,    108,    515,   2667,   1595,   4478,   4993,
    /* 50  P Q R S T U V W X Y Z [ \ ] ^ _ */
      1279,     66,   3971,   4203,   6006,   1836,    648,   1562,    100,   1313,     50,   1661,    498,   1661,     83,   2492,
    /* 60  ` a b c d e f g h i j k l m n o */
        83,  54163,   9886,  18442,  28161,  84235,  14787,  13375,  40373,  46105,   1080,   5150,  26666,  15950,  44776,  49926,
    /* 70  p q r s t u v w x y z { | } ~ . */
     12793,    665,  39708,  42034,  60061,  18359,   6480,  15618,    997,  13125,    498,    831,    332,    831,     83,      2,
    /* 80  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
    /* 90  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
    /* a0  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
    /* b0  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
    /* c0  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
    /* d0  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
    /* e0  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
    /* f0  . . . . . . . . . . . . . . . . */
         2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,      2,
};

unsigned pcrec_byte_freq_ppm(int b)
{
    return byte_freq_ppm_tbl[(unsigned char)b];
}

/* The residue the table's rounding leaves, published rather than hidden: the
 * cost model reads `pcrec_byte_freq_ppm` as a probability in ppm, so a table
 * that did not sum to 1e6 would make "the whole alphabet" cost something
 * other than one byte per byte. tests/codegen/run_offset_skip.sh §1 asserts
 * this returns 1000000. */
unsigned pcrec_byte_freq_total_ppm(void)
{
    unsigned t = 0;
    for (int b = 0; b < 256; b++) t += byte_freq_ppm_tbl[b];
    return t;
}

/* ---- THE WALK ------------------------------------------------------------
 *
 * `frontier[j]` is the set of NFA states a thread from the candidate start
 * can occupy after consuming exactly j bytes, closed over epsilon. The
 * closure passes every assertion node UNCONDITIONALLY: `\b` at offset 0 is
 * true on some subjects and false on others, and a set that assumes it true
 * is the superset, hence the sound direction. */

typedef struct {
    const Nfa *nfa;
    uint8_t   *seen;      /* one byte per NFA state, generation-stamped */
    unsigned char gen;
    int       *stack;
    int        nstack;
    int       *cur, ncur; /* the closed frontier: N_CLASS states only */
    bool       accept;    /* N_ACCEPT is in the closure */
} Walk;

static void wpush(Walk *w, int s)
{
    if (s < 0 || s >= w->nfa->n) return;
    if (w->seen[s] == w->gen) return;
    w->seen[s] = w->gen;
    w->stack[w->nstack++] = s;
}

/* Close `seeds` over epsilon and assertions, leaving the N_CLASS members in
 * `w->cur` and setting `w->accept` if the match may already be over. */
static void wclose(Walk *w, const int *seeds, int nseeds)
{
    w->gen++;
    w->nstack = 0;
    w->ncur = 0;
    w->accept = false;
    for (int i = 0; i < nseeds; i++) wpush(w, seeds[i]);
    while (w->nstack > 0) {
        int s = w->stack[--w->nstack];
        const NState *st = &w->nfa->st[s];
        switch (st->k) {
        case N_CLASS:
            w->cur[w->ncur++] = s;
            break;
        case N_ACCEPT:
            w->accept = true;
            break;
        case N_SPLIT:
            wpush(w, st->t1);
            wpush(w, st->t2);
            break;
        /* EVERY ASSERTION IS PASSED. Listing them one by one rather than
         * writing `default:` is deliberate: a new NKind must come here and be
         * classified, and the compiler says so. A new CONSUMING kind treated
         * as an assertion would be the one unsound direction this file has,
         * so the absent `default` is the check that prevents it. */
        case N_EPS:
        case N_BOT:
        case N_EOL:
        case N_END:
        case N_BOT_M:
        case N_EOL_M:
        case N_WORDB:
        case N_NWORDB:
        case N_GSTART:
            wpush(w, st->t1);
            break;
        }
    }
}

/* The union of the classes the frontier's consuming states read — i.e. the
 * bytes a thread from the candidate start may consume next. Returns how many. */
static int frontier_union(const Walk *w, uint8_t set[256])
{
    int count = 0;
    memset(set, 0, 256);
    for (int i = 0; i < w->ncur; i++) {
        const uint8_t *cls = w->nfa->st[w->cur[i]].cls;
        for (int b = 0; b < 256; b++) if (cls_has(cls, (unsigned)b)) set[b] = 1;
    }
    for (int b = 0; b < 256; b++) if (set[b]) count++;
    return count;
}

/* ---- THE COST MODEL ------------------------------------------------------
 *
 * Units: HUNDREDTHS OF A CYCLE PER SUBJECT BYTE. The four constants are the
 * note's §4.2 and every one of them is a MEASURED number off this box, not a
 * guess; re-measuring them is `scripts/`-free work the note describes.
 *
 *   C_MEMCHR   glibc memchr (AVX2) over a miss-heavy range — MEASURED at
 *              0.055 cycles/byte, docs/dev/opt3_dfa_scan_measurement.md §4's
 *              CONTROL 1
 *   C_BITMAP   the 256-entry `can_begin_match` walk, one byte at a time —
 *              MEASURED at 1.16 cycles/byte, the same table's first row
 *   C_VERIFY   one extra offset's load + table probe, per CANDIDATE
 *   C_ENTER    the expected cost of entering the transition loop on a
 *              candidate that will not match: [OPT-3]'s measured 10.7
 *              cycles/byte times the ~2 bytes a false start survives
 *
 * `C_ENTER` IS THE ONE WITH REAL SPREAD, AND THE DRAFT'S CLAIM THAT THE MODEL
 * IS INSENSITIVE TO IT WAS MEASURED FALSE. Swept over 8/12/20/30/40/60 cycles
 * across 1,352 corpus patterns (`docs/design/offset_k_skip.md` §4.3): the
 * three patterns this row exists for select the IDENTICAL k-set at every one
 * of them, and so do both email patterns, but 11 of 1,352 corpus patterns
 * change between 12 and 20 cycles and 120 between 8 and 20. The selection is
 * stable where the gap is 10x-30x and unstable where it is 1.2x-1.6x, which
 * is the right way round — but it means this constant is MEASURED (10.7
 * cycles/byte times the ~2 bytes a false start survives) rather than chosen,
 * and that §7's timing rather than this model is the acceptance. */
#define C_MEMCHR    6u
#define C_BITMAP  116u
#define C_VERIFY  250u
#define C_ENTER 2000u

/* THE FIFTH CONSTANT, AND THE MODEL IS WRONG WITHOUT IT. A verify is a
 * CONDITIONAL BRANCH on the candidate path, so its cost is not `C_VERIFY` but
 * `C_VERIFY` plus what the branch predictor loses. A test that is almost
 * always true, or almost always false, is free; a test that passes a third of
 * the time is a coin flip, and a mispredicted branch on this box costs a
 * pipeline. So the effective cost carries `C_MISPRED * min(p, 1-p)`.
 *
 * IT IS NOT A REFINEMENT, IT IS WHAT SEPARATES THE OUTLIERS FROM THE
 * CONTROLS. Without the term the model recommends verifying a SIXTEEN-byte
 * hex class at offsets 1 and 2 of `\b[0-9a-f]{32}\b` — a pair of coin-flip
 * branches on 80% of all positions, predicted a 2.56x win and in truth a
 * regression on a pattern pcrec is already ahead of the JIT on. With it that
 * pattern's predicted gain falls to 1.29x, below §4.5's materiality bar, and
 * the artifact does not move. The measured before/after that made this term
 * exist is docs/design/offset_k_skip.md §7.3. */
#define C_MISPRED 1500u

/* A skip is only adopted when the model says it is this many times cheaper
 * than the offset-0 filter that ships today. It is not a safety margin — the
 * change is answer-identical either way — it is what keeps an artifact from
 * MOVING for a predicted gain the box could not measure. §4.5.
 *
 * TWO, not the 1.5 the draft note carried: at 1.5 the corpus's marginal
 * members are patterns whose predicted gain (1.5x-1.6x on ipv4) is inside
 * the model's own error bars, and an artifact that moves for a gain nobody
 * can measure is a re-pinned identity gate and a changed objdump bought for
 * nothing. The three patterns this row exists for predict 19x, 31x and
 * 3,600x, so no reachable value of this constant between 1.5 and 100 changes
 * which of them is selected. */
#define MATERIAL_NUM 2u
#define MATERIAL_DEN 1u

static unsigned set_ppm(const uint8_t set[256])
{
    unsigned t = 0;
    for (int b = 0; b < 256; b++) if (set[b]) t += byte_freq_ppm_tbl[b];
    return t > 1000000u ? 1000000u : t;
}

/* One verify's cost per CANDIDATE, in hundredths of a cycle: the probe plus
 * what its branch costs a predictor that has to guess an outcome of
 * probability `ppm`. */
static unsigned verify_cost(unsigned ppm)
{
    unsigned tail = ppm < 1000000u - ppm ? ppm : 1000000u - ppm;
    return C_VERIFY + (unsigned)((unsigned long long)C_MISPRED * tail / 1000000ull);
}

/* cost, in hundredths of a cycle per subject byte, of scanning at `scan` and
 * verifying a chain of offsets whose costs sum to `vcost` per candidate and
 * whose rates multiply out to `vrate` ppm. */
static unsigned long long model_cost(unsigned scan_cost, unsigned scan_ppm,
                                     unsigned long long vcost,
                                     unsigned long long vrate_ppm)
{
    unsigned long long c = scan_cost;
    c += (unsigned long long)scan_ppm * vcost / 1000000ull;
    c += (unsigned long long)scan_ppm * vrate_ppm / 1000000ull
             * C_ENTER / 1000000ull;
    return c;
}

/* ---- THE SELECTION -------------------------------------------------------
 *
 * OFFSET 0 HAS TWO ROLES AND THEY NEED TWO DIFFERENT SETS. Getting this wrong
 * was [OPT-K]'s one MEASURED MISCOMPILE (MISCOMPILE-1, found by the D6
 * semantics critic and reproduced running on both engines), and the note's
 * §2.1 states the fact that makes it a miscompile without, in its first
 * draft, drawing the consequence:
 *
 *   ROLE A — THE SCAN at k = 0, the `memchr`/bitmap-walk form that shipped
 *     before this row. Its set is `k0`, the DFA start state's ESCAPE set, and
 *     that is exactly right: the scan skips only while the machine is PARKED
 *     in `fs`, those bytes provably keep it there, and a `\b` machine's start
 *     state escapes on every word character because it must REMEMBER the
 *     left-hand context. `k0` answers "does this byte move the machine off
 *     `fs`".
 *
 *   ROLE B — A VERIFY at offset 0, which is new here and is what an offset-k
 *     skip does when its scan sits at k* > 0. It REFUSES a candidate start,
 *     so its set must answer "can a match BEGIN here", and `k0` does not. The
 *     skip lands at a position whose left neighbour it jumped over, so the
 *     parked state there may be `s1u[UPC_WORD]` rather than `fs` — and a byte
 *     that cannot begin a match from `fs` can begin one from there.
 *     MEASURED: `\b\.[0-9]{4}Z` has `k0` = exactly the 63 word bytes with
 *     `.` excluded, and `.` is the ONLY byte a match can start with. With
 *     `k0` as the verify, "ab.1234Z" answered NOMATCH against a baseline and
 *     python3 `re` of (2,8) — nine lost-match cells over the witness set, on
 *     both engines. Sabotage row S188 restores it.
 *
 * SO ROLE B TAKES THE WALK'S OWN `frontier[0]`, and its soundness is §3.2's
 * proof unchanged and UNIVERSALLY QUANTIFIED over the preceding byte: a match
 * beginning anywhere runs a thread from `anch_start`, whose first byte is
 * consumed by an `N_CLASS` of that closure — a statement about the PATTERN,
 * true from `fs` and from every `s1u[u]` alike, because the closure passes
 * every assertion as though it held. **A new member of the k-set is
 * admissible only if its set comes from this walk**; a set that is a fact
 * about one STATE is valid only at the positions that state describes, which
 * is the whole of what went wrong.
 *
 * It is also strictly TIGHTER, which is the C4 improvement arriving as a
 * consequence of a correctness fix: `uuid`'s offset-0 verify goes from 63
 * bytes to the 16-byte hex class, `stack-frame`'s to `{a}`.
 *
 * `k0` still owns the BASELINE (`base_ppm`), because the baseline is what the
 * artifact costs today and today it filters on `k0`. */
void pcrec_prefix_ksets(Ctx *cx, const Nfa *nfa, const uint8_t k0[256],
                        PrefixKSets *o)
{
    memset(o, 0, sizeof *o);
    o->nsel = 0;

    /* THE BASELINE'S mass is the DFA set's — role A, what ships today. */
    int k0count = 0;
    for (int b = 0; b < 256; b++) if (k0[b]) k0count++;
    o->base_ppm = set_ppm(k0);

    if (nfa->n <= 0 || nfa->anch_start < 0 || nfa->anch_start >= nfa->n)
        return;

    Walk w;
    w.nfa = nfa;
    w.gen = 0;
    w.seen  = arena_alloc(&cx->arena, (size_t)nfa->n);
    w.stack = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    w.cur   = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    int *next = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    int seed = nfa->anch_start;
    wclose(&w, &seed, 1);

    /* ROLE B's set, and the walk's own offset 0. `w.accept` here would mean
     * the pattern matches empty, which `unanch_start` has already excluded
     * (`start_acc`) before calling us — checked rather than assumed, because
     * a zero-length match makes every offset test vacuous. */
    if (w.accept || w.ncur == 0) return;
    o->k[0].k = 0;
    o->k[0].count = frontier_union(&w, o->k[0].set);
    if (o->k[0].count == 0 || o->k[0].count >= 256) return;
    for (int b = 0; b < 256; b++) if (o->k[0].set[b]) o->k[0].byte = b;
    o->k[0].ppm = set_ppm(o->k[0].set);
    o->nwalk = 1;

    for (int j = 1; j < PCREC_PREFIX_K_MAX; j++) {
        /* THE STOP CONDITIONS, in the order they must be asked.
         *
         * (a) the match may already be over, so `s[p+j]` need not exist;
         * (b) the frontier is empty (nothing consumes) — the same thing;
         * (c) the walk got wide enough that the union is the alphabet, at
         *     which point every further offset is at least as wide and the
         *     walk has nothing left to say. */
        if (w.accept || w.ncur == 0) break;
        int nnext = 0;
        for (int i = 0; i < w.ncur; i++) next[nnext++] = w.nfa->st[w.cur[i]].t1;
        wclose(&w, next, nnext);
        if (w.accept || w.ncur == 0) break;

        uint8_t set[256];
        memset(set, 0, sizeof set);
        for (int i = 0; i < w.ncur; i++) {
            const uint8_t *cls = w.nfa->st[w.cur[i]].cls;
            for (int b = 0; b < 256; b++) if (cls_has(cls, (unsigned)b)) set[b] = 1;
        }
        int count = 0, byte = 0;
        for (int b = 0; b < 256; b++) if (set[b]) { count++; byte = b; }
        if (count == 0 || count == 256) break;

        PrefixK *pk = &o->k[o->nwalk];
        pk->k = j;
        memcpy(pk->set, set, 256);
        pk->count = count;
        pk->byte = byte;
        pk->ppm = set_ppm(set);
        o->nwalk++;
    }

    /* ---- pick a scan offset and its verifies -------------------------- */

    if (k0count == 0 || k0count >= 256) return;  /* today's filter is not usable */

    /* THE BASELINE IS ROLE A's: the offset-0 filter this artifact ships with. */
    unsigned base_scan = k0count == 1 ? C_MEMCHR : C_BITMAP;
    unsigned long long base = model_cost(base_scan, o->base_ppm, 0, 1000000ull);
    o->rate_ppm = o->base_ppm;

    unsigned long long best = base;
    int best_scan = -1, best_sel[PCREC_OFSK_MAX_SET], best_n = 0;
    unsigned long long best_rate = base;

    for (int si = 1; si < o->nwalk; si++) {
        /* THE SCAN STARTS AT si = 1, WHICH IS TWO RULES IN ONE INDEX.
         *
         * (a) The scan offset must MOVE off 0 — the measured rule below, and
         *     the reason there is no `si == 0` arm here to reason about.
         * (b) A scan offset past 0 must be a SINGLETON, a scope line with
         *     `attempt_cand`'s reasoning behind it (src/gen/emit_dfa.c): a
         *     multi-byte set at k > 0 would need a bitmap WALK at that
         *     offset — emitted code no measured pattern reaches, since a set
         *     wide enough to need one is never selective enough to be chosen.
         *
         * Together they also mean `o->k[0]` is ALWAYS role B here and never
         * the scan, so the two sets cannot be confused at this site. */
        if (o->k[si].count != 1) continue;
        unsigned scan_cost = C_MEMCHR;

        /* Greedy over the remaining offsets, most selective first. Greedy is
         * exact here and not an approximation: each verify multiplies the
         * entry rate by its own ppm independently of the others, so the k
         * best offsets are the k with the lowest ppm and no exchange can
         * improve a set of that size. */
        int order[PCREC_PREFIX_K_MAX], no = 0;
        for (int j = 1; j < o->nwalk; j++) if (j != si) order[no++] = j;
        for (int a = 0; a < no; a++)
            for (int b = a + 1; b < no; b++)
                if (o->k[order[b]].ppm < o->k[order[a]].ppm) {
                    int t = order[a]; order[a] = order[b]; order[b] = t;
                }

        /* OFFSET 0 IS ALWAYS IN THE SET, as the scan or as a mandatory
         * verify, and that is a CORRECTNESS-ADJACENT rule and not a
         * refinement. The emitted skip lands on its candidate and falls
         * through to the step; if the landing byte did not escape the start
         * state the machine would still be parked there on the next
         * iteration and the skip would run again — terminating, because the
         * step advances the position, but re-searching from every parked
         * position for a candidate it has already rejected. Verifying offset
         * 0 makes the landing byte one the step provably leaves the start
         * state on, which is exactly the invariant today's offset-0 filter
         * has and the property the whole mechanism is a generalisation of.
         * It costs a probe at the SCAN's rate, which on every pattern the
         * selection reaches is under a hundredth of a cycle per byte. */
        int sel[PCREC_OFSK_MAX_SET], n = 0;
        unsigned long long vrate, vcost;
        sel[n++] = 0;
        vrate = o->k[0].ppm;
        vcost = verify_cost(o->k[0].ppm);
        unsigned long long cost = model_cost(scan_cost, o->k[si].ppm, vcost, vrate);
        for (int a = 0; a < no && n < PCREC_OFSK_MAX_SET - 1; a++) {
            unsigned long long nv = vrate * o->k[order[a]].ppm / 1000000ull;
            unsigned long long nvc = vcost + verify_cost(o->k[order[a]].ppm);
            unsigned long long nc = model_cost(scan_cost, o->k[si].ppm, nvc, nv);
            if (nc >= cost) continue;
            sel[n++] = order[a];
            vrate = nv;
            vcost = nvc;
            cost = nc;
        }
        if (cost < best) {
            best = cost;
            best_scan = si;
            best_n = n;
            best_rate = (unsigned long long)o->k[si].ppm * vrate / 1000000ull;
            memcpy(best_sel, sel, sizeof sel);
        }
    }

    if (best_scan < 0) return;
    if (best * MATERIAL_NUM >= base * MATERIAL_DEN) return;   /* §4.5 */

    /* THE SCAN MUST MOVE, AND THIS RULE IS MEASURED RATHER THAN MODELLED.
     * §7.3 of the note carries the six-pattern before/after that forced it:
     *
     *   scan MOVED off offset 0     uuid 4.5x  iso-ts 4.8x  stack-frame 7.2x
     *                               needleXYZW 17.1x
     *   scan STAYED at offset 0     bignum 0.96-1.02x   [01]*1[01]{8} 0.97x
     *
     * The model predicted 13x for `bignum` and the box measured a wash, three
     * times, inside a +-14% spread. The reason is structural and the model
     * cannot see it: a VERIFY removes loop ENTRIES, while the SCAN removes
     * BYTES. With the scan still at offset 0 the artifact walks every byte in
     * the same loop it already had, and the entries a verify saves are entries
     * that die in one or two steps on real text — a saving `C_ENTER` prices at
     * 20 cycles and the box cannot resolve. Move the scan to a rare byte and
     * the whole subject is crossed at memchr speed instead, which is where
     * every order of magnitude in the table above lives.
     *
     * IT IS ALSO WHAT KEEPS TWO MEASURED TUNING PINS FROM MOVING:
     * `tests/codegen/run_codegen_tests.sh`'s M2.12 ordering check and its
     * `needleXYZW` prefilter check both fired on the version without this
     * rule, and M2.12's own text says the pin exists so the change cannot be
     * re-landed on plausibility alone. `[01]*1[01]{8}` keeps its `memchr`,
     * measured.
     *
     * The loop above starts at `si = 1`, so this is UNREACHABLE and is kept as
     * an assertion of the rule rather than as a second gate. */
    if (o->k[best_scan].k == 0) return;

    /* Publish, offsets ASCENDING — the emitted verify chain reads left to
     * right and a reader of the artifact should see the pattern's own order. */
    int all[PCREC_OFSK_MAX_SET], n = 0;
    all[n++] = best_scan;
    for (int i = 0; i < best_n; i++) all[n++] = best_sel[i];
    for (int a = 0; a < n; a++)
        for (int b = a + 1; b < n; b++)
            if (o->k[all[b]].k < o->k[all[a]].k) { int t = all[a]; all[a] = all[b]; all[b] = t; }

    o->nsel = n;
    for (int i = 0; i < n; i++) {
        o->sel[i] = all[i];
        if (all[i] == best_scan) o->scan = i;
    }
    o->maxk = o->k[all[n - 1]].k;
    o->rate_ppm = (unsigned)(best_rate > 1000000ull ? 1000000ull : best_rate);
}
