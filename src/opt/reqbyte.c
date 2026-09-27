/* [OPT-REQBYTE] + [OPT-REQPOS] tier 2b + [OPT-FREQPICK] THE PICK: which
 * member of the necessary SET the emitted `memchr` tests, and which member
 * and which window of the necessary RUN — the DERIVED half of the facts
 * `src/facts/req.c`'s walk proves.
 *
 * WHICH MEMBER: THE ARGMIN OF A BYTE-FREQUENCY PRIOR ([OPT-FREQPICK],
 * docs/design/reqbyte_freq_pick.md, ratified 2026-09-22). Every member of the
 * set is a byte every match must contain, so the emitted `memchr` is sound
 * for ANY member and the choice can only move a SPEED. The one that pays is
 * the one a subject is least likely to contain, and `pcrec_byte_freq_ppm`
 * (src/opt/prefix_k.c, shipped for `[OPT-OFSK]`) already orders bytes by
 * exactly that. PCRE2's rightmost rule survives as the TIEBREAK, so the
 * property `reqbyte.c` chose it for is preserved: a later multi-byte form is
 * a WIDENING of this mechanism and not a different one. "Rightmost" is
 * carried alongside the set rather than recovered from it — a set has no
 * order — and at an `A_ALT`, where the two branches' rightmost members are
 * incomparable, the rule is stated and deterministic (prefer the right
 * branch's own pick, then the left's, then the largest surviving byte)
 * rather than left to whichever bit a loop found first.
 *
 * AND THE PRIOR IS READ ONLY UNDER THE `byte` ENCODING. A byte-frequency
 * table is a fact about a subject corpus UNDER an encoding, and the shipped
 * table is keyed to `byte` by its own contents: its whole 0x80-0xFF half sits
 * at the table's 2 ppm floor, so under `-e utf8` it calls the bytes a Latin
 * corpus uses MOST the rarest bytes there are, and an argmin over it would
 * prefer a shared UTF-8 lead byte (`é@` lowers to {0xC3, 0xA9, 0x40} and the
 * argmin takes 0xC3 over a genuinely rare `@`). So under every encoding but
 * `byte` this file falls back to the rightmost member and the leftmost run
 * position — which is byte for byte the answer before [OPT-FREQPICK] landed,
 * so the fallback can never regress anything and the `-e utf8` identity gates
 * are a free control (reqbyte_freq_pick.md §3, Frank's ruling 2026-09-22).
 *
 * WHICH MEMBER OF THE RUN THE `memchr` SCANS FOR is the same argmin under the
 * same prior over a smaller set, ties to the LEFTMOST — and when a run ships,
 * the `req_byte` fact becomes that member rather than the whole set's own pick,
 * because there is ONE emitted `memchr` and the stamp reports what it tests.
 * The two are therefore chosen at one site, `pcrec_req_pick`'s single
 * return.
 *
 * A RUN LONGER THAN `PCREC_MAX_REQ_RUN_EMIT` IS TRUNCATED, NEVER SPLIT into
 * two compares: to the window of that length containing the scan member whose
 * bytes sum to the LOWEST prior (ties leftmost), and under any other encoding
 * to the leftmost window containing it — Frank's ruling of 2026-09-22
 * ("that is precisely the sort of precompiling analysis that gives this
 * project its advantage"). A second compare would be a second mechanism with
 * its own cost question and no measured need (D77).
 *
 * THESE ARE SPEED CHOICES AND NOTHING ELSE ([PATFACTS] step 3.0,
 * docs/design/patfacts/design.md §4.1): every member of the set and every
 * window of the run is sound, so the worst a bad pick costs is speed on some
 * subject. The WALK that proves them moved to `src/facts/req.c` at step 3.0;
 * these readers stay here until [FINDINGS] B1 moves them beside the rate
 * primitives, after which this file is deleted (design §4.2.2 carve-out (b)).
 *
 * Called by the pattern-facts record (`src/facts/facts.c`) when the `req_run`
 * or `req_byte` fact is first asked. */

#include <string.h>

#include "core/internal.h"
#include "facts/facts_derive.h"

/* ---- THE PICK ([OPT-FREQPICK]) -------------------------------------------
 *
 * Nothing below changes WHAT is necessary. Every function here chooses among
 * facts the walk above already proved, so the worst a bad choice can cost is
 * speed on some subject — `prefix_k.c`'s own sentence about the table it
 * reads ("THE TABLE IS A PRIOR AND NOT A PROMISE ... a badly-fitted prior
 * costs speed on some input and can never cost a match"). */

/* Which member of the necessary SET the emitted `memchr` tests: the rarest
 * under the prior, ties broken by the threaded rightmost `pick` when it is
 * among the minima and by the largest such byte otherwise.
 *
 * `bytekey` is false under every encoding the shipped table is not keyed to,
 * and then this is today's answer unchanged — the header says why that
 * fallback is free. The tiebreak's second clause exists because `pick` is not
 * always among the minima, and a rule that silently fell back to "whichever
 * bit a loop found first" is what `rb_intersect` already refuses. */
static int rb_pick(const RbSet *s, bool bytekey)
{
    int b, best = -1;
    unsigned lo = 0;
    if (!bytekey || s->pick < 0) return s->pick;
    for (b = 255; b >= 0; b--) {
        unsigned p;
        if (!rb_has(s, b)) continue;
        p = pcrec_byte_freq_ppm(b);
        if (best < 0 || p < lo) { lo = p; best = b; }
    }
    /* Scanning DOWN above already leaves `best` as the LARGEST of the minima,
     * so only the "today's pick is among them" clause needs stating. */
    if (pcrec_byte_freq_ppm(s->pick) == lo) return s->pick;
    return best;
}

/* Which member of the RUN the emitted `memchr` tests: the rarest under the
 * prior, ties to the LEFTMOST — and `rb_pick`'s own `!bytekey` fallback
 * (rightmost — `cat`/`alt`'s threaded convention) where the prior does not
 * apply. The per-candidate cost of the whole run check is the number of
 * occurrences of THIS byte in the window, which is why the choice is not
 * cosmetic.
 *
 * [OPT-REQRUN-ENC] `!bytekey` WAS the leftmost fallback (reqpos_2b.md §2.3's
 * ratified "costs nothing measurable"), and pcrec-bench's O-60 finding
 * falsified that under `-e utf8`: a `-e utf8` run is complete lowered UTF-8
 * code-unit sequences, so its LEFTMOST member is a lead byte whenever the
 * run opens mid-character — shared by every character in that script block,
 * so the emitted `memchr` stops on nearly every byte of a non-Latin subject
 * rather than the rare one the literal needs (measured: 12.0%/20.7% of the
 * corpus/bench RUN-path artifacts under `-e utf8`,
 * docs/dev/optloop/reqrunenc_census.md §0/§2.1). The rightmost member is
 * never this defect on a REAL run — a run's last byte can only be a lead
 * byte if the run is truncated mid-character (an alternation's common
 * suffix stopping between a lead byte and its continuation), which the
 * census's D77 measurement found in ZERO of 912 real `-e utf8` runs
 * (bench+corpus) — so `rb_pick`'s own fallback closes this with no new
 * byte-range logic: one mechanism, two call sites, general-mechanism rule.
 * A byte-range-aware "skip lead bytes" candidate (S in the census) was
 * measured byte-IDENTICAL to this one on the whole real population and is
 * not built (D77's "wait for a measured need" — the one case where it
 * would differ has never been observed). */
static int rn_scan_index(const RbRun *r, bool bytekey)
{
    int i, best = 0;
    unsigned lo;
    if (!bytekey) return r->n - 1;
    lo = pcrec_byte_freq_ppm(r->bytes[0]);
    for (i = 1; i < r->n; i++) {
        unsigned p = pcrec_byte_freq_ppm(r->bytes[i]);
        if (p < lo) { lo = p; best = i; }
    }
    return best;
}

/* Where a run longer than `PCREC_MAX_REQ_RUN_EMIT` is TRUNCATED to: the start
 * of the window of that length containing `idx` whose bytes sum to the lowest
 * prior, ties to the leftmost — Frank's ruling of 2026-09-22 — and the
 * leftmost such window where the prior does not apply.
 *
 * The scan member is in every candidate window by construction, so its own
 * ppm is a constant of the comparison and no term has to be excluded. */
static int rn_window_start(const RbRun *r, int idx, bool bytekey)
{
    int lo_s = idx - (PCREC_MAX_REQ_RUN_EMIT - 1), hi_s = idx;
    int s, best;
    unsigned long long lo = 0;
    if (lo_s < 0) lo_s = 0;
    if (hi_s > r->n - PCREC_MAX_REQ_RUN_EMIT) hi_s = r->n - PCREC_MAX_REQ_RUN_EMIT;
    best = lo_s;
    if (!bytekey) return best;
    for (s = lo_s; s <= hi_s; s++) {
        unsigned long long t = 0;
        int k;
        for (k = 0; k < PCREC_MAX_REQ_RUN_EMIT; k++)
            t += pcrec_byte_freq_ppm(r->bytes[s + k]);
        if (s == lo_s || t < lo) { lo = t; best = s; }
    }
    return best;
}

/* THE WINDOW, the `req_run` fact's derived half, cut from the whole run the
 * core `req_whole_run` fact holds (`run->whole`/`whole_len`): which member of
 * the run the emitted `memchr` scans for (`idx`), and where a run longer than
 * `PCREC_MAX_REQ_RUN_EMIT` is truncated to (`at`, with `bytes` exactly
 * `whole + at` for `len` bytes). A whole run shorter than two bytes has no
 * window (`len == 0`). See the header for why the member is the argmin of a
 * frequency prior under `byte` and the rightmost elsewhere, and why a long
 * run is truncated and never split. */
void pcrec_req_window(Ctx *cx, ReqRun *run, PfWhyCode *why)
{
    bool bytekey = cx->opt->encoding == PCREC_ENC_BYTE;
    RbRun r;

    memset(run->bytes, 0, sizeof run->bytes);
    run->len = 0;
    run->idx = 0;
    run->at = 0;
    *why = PF_WHY_NONE;
    if (run->whole_len < 2) return;
    *why = bytekey ? PF_WHY_RATE_BUILTIN : PF_WHY_RATE_NONE;

    memset(&r, 0, sizeof r);
    memcpy(r.bytes, run->whole, (size_t)run->whole_len);
    r.n = run->whole_len;
    {
        int i = rn_scan_index(&r, bytekey);
        int s = r.n > PCREC_MAX_REQ_RUN_EMIT ? rn_window_start(&r, i, bytekey) : 0;
        int len = r.n - s;
        if (len > PCREC_MAX_REQ_RUN_EMIT) len = PCREC_MAX_REQ_RUN_EMIT;
        memcpy(run->bytes, r.bytes + s, (size_t)len);
        run->len = len;
        run->idx = i - s;
        run->at = s;
    }
}

/* THE BYTE the emitted `memchr` tests — the `req_byte` fact — at ONE return:
 * the run's own scan member where a run window shipped (there is one emitted
 * `memchr`, and `<PREFIX>_REQ_BYTE` reports what it tests), and otherwise the
 * set's pick, the argmin of the prior under `byte` with the walk's threaded
 * rightmost member as the tiebreak and the whole answer elsewhere. -1 exactly
 * when the set is empty. */
int pcrec_req_pick(Ctx *cx, const ReqSet *set, const ReqRun *run,
                   PfWhyCode *why)
{
    bool bytekey = cx->opt->encoding == PCREC_ENC_BYTE;
    RbSet s;
    *why = bytekey ? PF_WHY_RATE_BUILTIN : PF_WHY_RATE_NONE;
    if (run->len >= 2) return run->bytes[run->idx];
    if (set->rightmost < 0) *why = PF_WHY_NONE;
    memcpy(s.bits, set->bits, sizeof s.bits);
    s.pick = set->rightmost;
    return rb_pick(&s, bytekey);
}
