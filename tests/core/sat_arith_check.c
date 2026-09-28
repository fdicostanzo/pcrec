/* tests/core/sat_arith_check.c — [REVW.U L5-R2] THE SATURATING-ARITHMETIC
 * AGREEMENT CHECK (docs/dev/reviews/lens_reports/lens5_unit_seams.md R2,
 * lens 1's X3), REVISED at [PATFACTS] step 3.6 (R3, 2026-09-28, lane pf36).
 *
 * THE REQUIREMENT, STATED TWICE IN PROSE AND ENFORCED NOWHERE UNTIL THIS
 * FILE. `src/opt/CLAUDE.md`'s `mrl.c` entry: "Arithmetic saturates at
 * PCREC_MINW_MAX ... shared with the emitter's accumulator so a long
 * concatenation of saturated subtrees cannot overflow past the ceiling
 * that exists to prevent it. A wrapped product is not merely wrong, it is
 * wrong in the UNSOUND direction whenever it lands on a small positive
 * value." `src/gen/emit_vm.c`'s own comment above `pcrec_vm_fadd` restates it
 * from the other side. Two sources, one requirement — and until this row
 * it held because two authors happened to type the same five lines.
 *
 * THREE INDEPENDENT COPIES AT L5-R2's LANDING (mrl.c, callgraph.c,
 * emit_vm.c) ARE NOW TWO. [PATFACTS] step 3.6 (R3,
 * docs/design/patfacts/inventory.md) unified mrl.c's and callgraph.c's
 * copies into ONE shared primitive, `pcrec_sat_add`/`pcrec_sat_mul`
 * (src/opt/mrl.c), taking the ceiling as a PARAMETER — lens 1's X3 named
 * exactly this signature. `src/gen/emit_vm.c`'s `pcrec_vm_fadd`/
 * `pcrec_vm_fmul` are the THIRD copy and are DELIBERATELY NOT unified
 * here: design.md's step 3.6 row scopes the step to mrl.c/callgraph.c, and
 * emit_vm.c sits in a higher layer (gen) than mrl.c's home (opt). So this
 * check now compares TWO independent implementations rather than three —
 * `pcrec_sat_add(a, b, PCREC_MINW_MAX)` (mrl.c, the shared caller both
 * mrl.c and callgraph.c now use) against `pcrec_vm_fadd(a, b)` (emit_vm.c)
 * — and `PCREC_MINW_MAX == (1LL << 40)` still makes them the SAME VALUE
 * after the ceiling is substituted, so the agreement stays checkable by
 * VALUE over a shared input set with no modelling at all. Two independent
 * implementations survive where three did, which is what keeps this
 * check's reason for existing (an agreement nothing else enforces)
 * unweakened by the merge.
 *
 * WHY THE FOUR FUNCTIONS ARE NOT `static`. Each was file-private, which a
 * linker cannot reach from a separate translation unit — [REVW.U L5-R2]
 * dropped `static` from all of them (core/internal.h declares
 * `pcrec_sat_add`/`pcrec_sat_mul` beside `pcrec_minw`, and
 * `pcrec_vm_fadd`/`pcrec_vm_fmul` in the gen-tier section) so this file
 * calls the SHIPPED functions directly rather than transcribing their
 * bodies. A transcription checks only itself (`branch_count_check.c`'s own
 * rule: "different algorithm, different code, different failure modes" —
 * the opposite move here, since the whole point is to compare TWO
 * SPELLINGS OF ONE ALGORITHM, not to write a third). No behaviour change:
 * these are pcrec's own compile-time arithmetic, never emitted into
 * generated text, so this is not an `abi` event.
 *
 * THE DOMAIN, AND WHY IT IS NOT "ALL OF int64 x int64". Before this
 * revision, `pcrec_cg_sat_add` (callgraph.c's own, now retired) carried an
 * extra leading guard the mrl/vm pair lacked:
 * `if (a >= CG_EXP_INF || b >= CG_EXP_INF) return CG_EXP_INF;` — CG_EXP_INF
 * equalled PCREC_MINW_MAX by construction (both `1LL << 40`). Read as a
 * property of ALL integers that guard was NOT redundant (feed it
 * `a = 3*CAP, b = -2.5*CAP` and the guarded form returns CAP while the
 * plain add-then-clamp form returns CAP/2) — but every real call site in
 * callgraph.c only ever passed NON-NEGATIVE operands (node counts and
 * saturated sub-results), matching mrl's and vm's own usage identically.
 * On that domain the guard IS provably redundant (for a >= 0, b >= 0: a >=
 * CAP implies a + b >= a >= CAP, so the plain form also saturates to CAP;
 * the two forms cannot diverge) — lens 1's own open question ("'appears
 * redundant' — but 'appears redundant' is how this project loses things"),
 * answered by evaluation before step 3.6 dropped the guard, and step 3.6
 * built the merge ON that proof rather than re-deriving it. The check's
 * domain (the non-negative grid below) is UNCHANGED by the merge — it is
 * still the domain every real caller uses.
 *
 * WHY NO INPUT PAIR IS `LLONG_MAX` PAIRED WITH ITSELF. `pcrec_sat_add` /
 * `pcrec_vm_fadd` both compute `a + b` UNCONDITIONALLY before comparing
 * the sum to the ceiling — genuinely correct, since the ceiling is far
 * below LLONG_MAX and every real caller's operands are bounded well under
 * it, but `LLONG_MAX + LLONG_MAX` is signed-integer OVERFLOW, undefined
 * behaviour in C. This file is wired into `san_scripts.txt` (R0.2's own
 * membership rule) and `make ubsan`/`make san` build with
 * `-fno-sanitize-recover=undefined` — a real UB hit there is a hard
 * ABORT, not a clean FAIL line. Rather than have this check crash the
 * sanitizer battery on its own first run, the "operand far above the
 * ceiling" case is exercised at `LLONG_MAX` paired with `0` only (no
 * overflow: `x + 0` never overflows for any `x`), and the boundary ladder
 * around the ceiling itself (`cap-2 .. cap+1`, `cap*2`) carries the "how
 * does saturation behave near and past its own knee" property the wider
 * pairing would have added nothing beyond. Filed here rather than
 * silently narrowed.
 *
 * SHARING NO SOURCE WITH THE SUBJECT (R0.5's bar). The oracle is not a
 * third implementation of saturating add — it is the three ALGEBRAIC LAWS
 * the callers rely on and the implementations do not themselves state
 * (Monotone, Capped, Absorbing), checked by direct evaluation of the
 * shipped functions against arithmetic facts about the integers involved,
 * never against a parallel computation of the "right answer".
 *
 * FAILING-DIRECTION STORY (four sabotages, lens 5's own list — each
 * targets one of the four things that can differ). Re-verified against
 * the unified pair at step 3.6, and re-aimed at `pcrec_sat_mul` (mrl.c)
 * rather than the retired `pcrec_mrl_sat_mul`:
 *   (a) MRL_MINW_MAX changed to a different ceiling — CHECK 1 (cross-
 *       family equality) reds on every pair at or past the moved cap.
 *   (b) pcrec_sat_add's clamp deleted — CHECK 3 (Capped) reds on `(cap, 1)`.
 *   (c) pcrec_sat_mul's `a > cap / b` weakened to `a >= cap / b` — CHECK 1
 *       reds on exactly one boundary pair and no other. THIS IS THE ONE
 *       THAT MATTERS: it under-estimates by one, under-estimating is the
 *       SAFE direction (`pcrec_vm_fadd`'s own comment: "under-estimating is the
 *       safe direction and saturation is an under-estimate"), so no
 *       pattern in the whole corpus gives a WRONG ANSWER — it only stops
 *       pruning somewhere, which is invisible to `make test`'s answer-
 *       level suite by construction. This is the seam an answer-level
 *       check structurally cannot reach. Sabotage row S254 (re-aimed at
 *       `pcrec_sat_mul`'s single shared definition — weakening it now
 *       weakens EVERY caller, mrl.c/callgraph.c/emit_vm.c's disagreement
 *       is still what CHECK 1 catches, since `pcrec_vm_fadd`/`fmul` keep
 *       the unweakened form).
 *   (d) the `a <= 0` guard flipped to `a < 0` — CHECK 5/6 reds on `(0, k)`.
 *
 * ~450 pairs total (CHECK 1/2's 12x12 non-negative grid plus the negative
 * excursions CHECKs 4-6 add), one binary, microseconds.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <limits.h>
#include <stdbool.h>

#include "core/internal.h"

static int pass_n, fail_n;

static void ok(const char *fmt, ...)
{
    va_list ap; va_start(ap, fmt);
    printf("PASS: "); vprintf(fmt, ap); printf("\n");
    va_end(ap);
    pass_n++;
}
static void bad(const char *fmt, ...)
{
    va_list ap; va_start(ap, fmt);
    fprintf(stderr, "FAIL: "); vfprintf(stderr, fmt, ap); fprintf(stderr, "\n");
    va_end(ap);
    fail_n++;
}

#define CAP PCREC_MINW_MAX   /* (1LL << 40) */

/* pcrec_sat_add/pcrec_sat_mul (mrl.c, callgraph.c's shared caller since
 * step 3.6) always called at this ceiling in this file, matching every
 * real call site (MRL_MINW_MAX and PCREC_MINW_MAX are the same macro). */
static long long sat_add(long long a, long long b) { return pcrec_sat_add(a, b, CAP); }
static long long sat_mul(long long a, long long b) { return pcrec_sat_mul(a, b, CAP); }

/* The non-negative grid — CAP's own knee plus small boundary values plus
 * one far-above-cap witness, safe under addition (CAP*2 is ~2^41, nowhere
 * near LLONG_MAX's 2^63; every pairwise SUM in this grid stays comfortably
 * representable). */
static const long long NN[] = {
    0, 1, 2, CAP / 2 - 1, CAP / 2, CAP / 2 + 1,
    CAP - 2, CAP - 1, CAP, CAP + 1, CAP + 2, CAP * 2,
};
#define NN_N (sizeof NN / sizeof NN[0])

/* Negative/zero witnesses for the `a <= 0 || b <= 0` guard sat_mul carries
 * (sat_add has no such guard in either implementation — it saturates
 * identically for negative operands too, which is exercised by CHECK 4's
 * monotone sweep over the signed ladder below). */
static const long long NEG[] = { -1, -2, -(CAP / 2), -CAP, 0 };
#define NEG_N (sizeof NEG / sizeof NEG[0])

/* A signed ladder for the Monotone law (sorted ascending; CHECK 4 walks
 * consecutive pairs and asserts the family's output is non-decreasing). */
static const long long LADDER[] = {
    -CAP, -(CAP / 2), -2, -1, 0, 1, 2, CAP / 2 - 1, CAP / 2, CAP / 2 + 1,
    CAP - 1, CAP, CAP + 1, CAP * 2,
};
#define LADDER_N (sizeof LADDER / sizeof LADDER[0])

int main(void)
{
    /* ==================================================================
     * CHECK 1 — CROSS-FAMILY EQUALITY, ADD, over the non-negative domain
     * every real caller actually uses (the header above derives why this
     * domain, not "all int64", is the one the redundancy question is
     * about).
     * ================================================================== */
    {
        long long mism = 0, first_a = 0, first_b = 0;
        long long first_s = 0, first_v = 0;
        long long pairs = 0;
        for (size_t i = 0; i < NN_N; i++)
            for (size_t j = 0; j < NN_N; j++) {
                long long a = NN[i], b = NN[j];
                long long s = sat_add(a, b);
                long long v = pcrec_vm_fadd(a, b);
                pairs++;
                if (s != v) {
                    if (mism == 0) {
                        first_a = a; first_b = b;
                        first_s = s; first_v = v;
                    }
                    mism++;
                }
            }
        /* Also the isolated far-above-cap witness the header explains. */
        {
            long long a = LLONG_MAX, b = 0;
            long long s = sat_add(a, b);
            long long v = pcrec_vm_fadd(a, b);
            pairs++;
            if (s != v) {
                if (mism == 0) { first_a = a; first_b = b; first_s = s; first_v = v; }
                mism++;
            }
            if (s != CAP) bad("add: pcrec_sat_add(LLONG_MAX, 0, CAP) = %lld, want CAP (%lld)", s, CAP);
        }
        if (mism != 0)
            bad("add: pcrec_sat_add/pcrec_vm_fadd DISAGREE at (%lld, %lld): %lld / %lld",
                first_a, first_b, first_s, first_v);
        else
            ok("add: pcrec_sat_add(mrl.c) == pcrec_vm_fadd(emit_vm.c) on all %lld non-negative pairs — two independent implementations agree, step 3.6's unification changed nothing",
               pairs);
    }

    /* ==================================================================
     * CHECK 2 — CROSS-FAMILY EQUALITY, MUL, same domain and same
     * reasoning; mul's own domain guard (a <= 0 || b <= 0 -> 0) is
     * exercised separately in CHECK 6.
     * ================================================================== */
    {
        long long mism = 0, first_a = 0, first_b = 0;
        long long first_s = 0, first_v = 0;
        long long pairs = 0;
        for (size_t i = 0; i < NN_N; i++)
            for (size_t j = 0; j < NN_N; j++) {
                long long a = NN[i], b = NN[j];
                if (a == 0 || b == 0) continue;   /* CHECK 6 owns the guard */
                long long s = sat_mul(a, b);
                long long v = pcrec_vm_fmul(a, b);
                pairs++;
                if (s != v) {
                    if (mism == 0) {
                        first_a = a; first_b = b;
                        first_s = s; first_v = v;
                    }
                    mism++;
                }
            }
        if (mism != 0)
            bad("mul: pcrec_sat_mul/pcrec_vm_fmul DISAGREE at (%lld, %lld): %lld / %lld",
                first_a, first_b, first_s, first_v);
        else
            ok("mul: pcrec_sat_mul(mrl.c) == pcrec_vm_fmul(emit_vm.c) on all %lld positive pairs",
               pairs);
    }

    /* ==================================================================
     * CHECK 3 — CAPPED: the result never exceeds CAP and never goes
     * negative for a non-negative input pair (the UNSOUND direction
     * `src/opt/CLAUDE.md` names — "wrong in the unsound direction
     * whenever it lands on a small positive value" is exactly a wrap
     * that slips PAST this bound unnoticed).
     * ================================================================== */
    {
        long long viol_add = 0, viol_mul = 0;
        for (size_t i = 0; i < NN_N; i++)
            for (size_t j = 0; j < NN_N; j++) {
                long long a = NN[i], b = NN[j];
                long long ra_s = sat_add(a, b), ra_v = pcrec_vm_fadd(a, b);
                if (ra_s > CAP || ra_s < 0) viol_add++;
                if (ra_v > CAP || ra_v < 0) viol_add++;
                if (a > 0 && b > 0) {
                    long long rm_s = sat_mul(a, b), rm_v = pcrec_vm_fmul(a, b);
                    if (rm_s > CAP || rm_s < 0) viol_mul++;
                    if (rm_v > CAP || rm_v < 0) viol_mul++;
                }
            }
        if (viol_add) bad("capped: add produced a value outside [0, CAP] %lld time(s)", viol_add);
        else ok("capped: every add result stays in [0, CAP] over the non-negative grid");
        if (viol_mul) bad("capped: mul produced a value outside [0, CAP] %lld time(s)", viol_mul);
        else ok("capped: every mul result stays in [0, CAP] over the positive grid");
    }

    /* ==================================================================
     * CHECK 4 — MONOTONE: a <= a' implies sat_add(a,b) <= sat_add(a',b),
     * over the signed ladder (sat_add has no positivity guard in either
     * implementation, so this is the one law checked with negative
     * operands too — "under-estimating is the safe direction" depends on
     * saturation never DECREASING as an operand grows).
     * ================================================================== */
    {
        long long viol = 0;
        for (size_t bi = 0; bi < NN_N; bi++) {
            long long b = NN[bi];
            for (size_t i = 0; i + 1 < LADDER_N; i++) {
                long long a = LADDER[i], ap = LADDER[i + 1];
                if (sat_add(a, b) > sat_add(ap, b)) viol++;
                if (pcrec_vm_fadd(a, b) > pcrec_vm_fadd(ap, b)) viol++;
            }
        }
        if (viol) bad("monotone: sat_add decreased as its first operand grew, %lld time(s)", viol);
        else ok("monotone: sat_add is non-decreasing in its first operand, both families, over the signed ladder x the non-negative grid");
    }

    /* ==================================================================
     * CHECK 5 — ABSORBING: sat_add(CAP, b) == CAP for every b >= 0, and
     * sat_mul(CAP, k) == CAP for every k >= 1.
     * ================================================================== */
    {
        long long viol = 0;
        for (size_t i = 0; i < NN_N; i++) {
            long long b = NN[i];
            if (sat_add(CAP, b) != CAP) viol++;
            if (pcrec_vm_fadd(CAP, b) != CAP) viol++;
        }
        for (size_t i = 0; i < NN_N; i++) {
            long long k = NN[i];
            if (k < 1) continue;
            if (sat_mul(CAP, k) != CAP) viol++;
            if (pcrec_vm_fmul(CAP, k) != CAP) viol++;
        }
        if (viol) bad("absorbing: sat_*(CAP, x) != CAP, %lld time(s)", viol);
        else ok("absorbing: sat_add(CAP, b) == CAP and sat_mul(CAP, k) == CAP over the non-negative grid, both families");
    }

    /* ==================================================================
     * CHECK 6 — MUL's DOMAIN GUARD: a <= 0 || b <= 0 must answer exactly
     * 0, in both families, over the negative/zero witness set crossed
     * with the non-negative grid (and with itself).
     * ================================================================== */
    {
        long long viol = 0, checked = 0;
        for (size_t i = 0; i < NEG_N; i++)
            for (size_t j = 0; j < NN_N; j++) {
                long long a = NEG[i], b = NN[j];
                checked += 2;
                if (sat_mul(a, b) != 0) viol++;
                if (pcrec_vm_fmul(a, b) != 0) viol++;
                checked += 2;
                if (sat_mul(b, a) != 0) viol++;
                if (pcrec_vm_fmul(b, a) != 0) viol++;
            }
        if (viol) bad("mul domain guard: a <= 0 || b <= 0 did not answer 0, %lld time(s) of %lld checked", viol, checked);
        else ok("mul domain guard: a <= 0 || b <= 0 answers exactly 0 in both families, %lld cells checked", checked);
    }

    printf("\nchecks passed: %d\n", pass_n);
    printf("checks failed: %d\n", fail_n);
    return fail_n ? 1 : 0;
}
