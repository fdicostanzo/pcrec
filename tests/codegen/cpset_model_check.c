/* tests/codegen/cpset_model_check.c — [M5.0 stage 1] A RANDOMIZED MODEL CHECK
 * of `src/core/cpset.c`'s interval algebra against a bitset oracle.
 *
 * ============================================================================
 * WHY THIS EXISTS WHEN THE IDENTITY GATE ALREADY READS 100%
 * ============================================================================
 *
 * The gate proves the interval set produces what the bitmap produced FOR THE
 * PATTERNS THE CORPUS CONTAINS. That is a strong statement about a population
 * and a weak one about a data structure: `pcrec_cpset_complement` is only ever
 * called by the corpus with `max_cp == 0xFF`, `pcrec_cpset_remove` has exactly
 * one caller (`.`, removing `\n`), and no corpus pattern produces an interval
 * list long enough to exercise the absorb-many path in `pcrec_cpset_add`.
 *
 * **STAGE 2 AND STAGE 3 WILL.** `\p{L}` is ~770 intervals, `utf8`'s universe
 * is 0x10FFFF, and §2.3's surrogate excision is `remove`'s second caller. A
 * bug in any of those is invisible today and a miscompile then — and it would
 * arrive in a wave whose OWN acceptance is a corpus that did not exist when
 * the bug shipped. So the algebra is checked directly, now, against an oracle
 * that shares nothing with it.
 *
 * THE ORACLE IS A FLAT BYTE ARRAY, which is the point: it has no intervals, no
 * merging, no ordering and no invariant, so it cannot fail the same way the
 * subject does. The universe is small (4096) precisely so the oracle can be
 * exhaustive — every point is compared after every operation, rather than
 * sampled.
 *
 * TWO PROPERTIES ARE CHECKED, and the second is the one a membership-only
 * check would miss. (1) MEMBERSHIP agrees at every point. (2) THE INVARIANT
 * holds — sorted, non-empty, disjoint AND NON-ADJACENT. A representation that
 * answered every membership query correctly while leaving `[a-m][n-z]` as two
 * intervals would pass (1) and break §2.7.2's argument that the artifact does
 * not depend on the pattern's SPELLING.
 *
 * THE SEVEN EDGE CASES ARE WRITTEN OUT rather than left to the random walk,
 * because each is a boundary the walk hits rarely or never: the complement of
 * the empty set and of the full universe, double complement as the identity,
 * adjacency coalescing, a mid-interval split, a complement of an interval
 * touching 0 (where a careless `lo - 1` underflows), and absorbing 100
 * intervals in one `add`. The last two are the ones that would have been found
 * here rather than in stage 3.
 *
 * Deterministic by construction: the PRNG is seeded to a constant, so a
 * failure is reproducible from the printed iteration number. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "core/internal.h"

#define UNIV 4096u                 /* model universe; small enough to bitset */
static unsigned char model[UNIV];

static unsigned rng_s = 12345u;
static unsigned rnd(unsigned n){ rng_s = rng_s*1103515245u + 12345u; return (rng_s>>16) % n; }

static int check(PcrecCpSet *s, const char *what, int iter)
{
    /* (1) membership agrees with the model on every point */
    for (unsigned c = 0; c < UNIV; c++) {
        bool a = pcrec_cpset_has(s, c), b = model[c] != 0;
        if (a != b) {
            printf("MISMATCH after %s iter %d at %u: set=%d model=%d\n", what, iter, c, a, b);
            return 1;
        }
    }
    /* (2) the INVARIANT: sorted, non-empty, disjoint AND non-adjacent */
    for (int i = 0; i < s->n; i++) {
        if (s->iv[i].lo > s->iv[i].hi) { printf("INVARIANT lo>hi after %s iter %d at %d\n", what, iter, i); return 1; }
        if (i && !(s->iv[i-1].hi + 1 < s->iv[i].lo)) {
            printf("INVARIANT not sorted/non-adjacent after %s iter %d at %d: [%u,%u] then [%u,%u]\n",
                   what, iter, i, s->iv[i-1].lo, s->iv[i-1].hi, s->iv[i].lo, s->iv[i].hi);
            return 1;
        }
    }
    return 0;
}

int main(void)
{
    Ctx cx; memset(&cx, 0, sizeof cx); cx.arena.cx = &cx;
    int bad = 0;
    const int TRIALS = 400, OPS = 60;

    for (int t = 0; t < TRIALS && !bad; t++) {
        PcrecCpSet s; pcrec_cpset_init(&s, &cx.arena);
        memset(model, 0, sizeof model);
        for (int o = 0; o < OPS && !bad; o++) {
            unsigned lo = rnd(UNIV), hi = lo + rnd(40);
            if (hi >= UNIV) hi = UNIV - 1;
            int op = rnd(10);
            if (op < 6) {                              /* add */
                pcrec_cpset_add(&s, lo, hi);
                for (unsigned c = lo; c <= hi; c++) model[c] = 1;
                bad |= check(&s, "add", o);
            } else if (op < 9) {                       /* remove */
                pcrec_cpset_remove(&s, lo, hi);
                for (unsigned c = lo; c <= hi; c++) model[c] = 0;
                bad |= check(&s, "remove", o);
            } else {                                   /* complement */
                unsigned max = UNIV - 1;
                pcrec_cpset_complement(&s, max);
                for (unsigned c = 0; c <= max; c++) model[c] = !model[c];
                bad |= check(&s, "complement", o);
            }
        }
    }

    /* EDGE CASES the random walk will not reliably hit. */
    { /* complement of the EMPTY set is the whole universe */
      PcrecCpSet s; pcrec_cpset_init(&s, &cx.arena);
      pcrec_cpset_complement(&s, 0x10FFFF);
      if (s.n != 1 || s.iv[0].lo != 0 || s.iv[0].hi != 0x10FFFF) { printf("EDGE empty-complement wrong: n=%d\n", s.n); bad = 1; }
    }
    { /* complement of the FULL universe is empty */
      PcrecCpSet s; pcrec_cpset_init(&s, &cx.arena);
      pcrec_cpset_add(&s, 0, 0x10FFFF);
      pcrec_cpset_complement(&s, 0x10FFFF);
      if (s.n != 0) { printf("EDGE full-complement wrong: n=%d\n", s.n); bad = 1; }
    }
    { /* double complement is the identity */
      PcrecCpSet s; pcrec_cpset_init(&s, &cx.arena);
      pcrec_cpset_add(&s, 'a', 'z'); pcrec_cpset_add(&s, '0', '9');
      pcrec_cpset_complement(&s, 0xFF); pcrec_cpset_complement(&s, 0xFF);
      if (s.n != 2 || s.iv[0].lo != '0' || s.iv[0].hi != '9' ||
          s.iv[1].lo != 'a' || s.iv[1].hi != 'z') { printf("EDGE double-complement wrong: n=%d\n", s.n); bad = 1; }
    }
    { /* ADJACENT intervals must COALESCE: [a-m] + [n-z] is one interval */
      PcrecCpSet s; pcrec_cpset_init(&s, &cx.arena);
      pcrec_cpset_add(&s, 'a', 'm'); pcrec_cpset_add(&s, 'n', 'z');
      if (s.n != 1 || s.iv[0].lo != 'a' || s.iv[0].hi != 'z') { printf("EDGE adjacency wrong: n=%d\n", s.n); bad = 1; }
    }
    { /* removing the MIDDLE splits in two */
      PcrecCpSet s; pcrec_cpset_init(&s, &cx.arena);
      pcrec_cpset_add(&s, 0, 100); pcrec_cpset_remove(&s, 40, 60);
      if (s.n != 2 || s.iv[0].hi != 39 || s.iv[1].lo != 61) { printf("EDGE split wrong: n=%d\n", s.n); bad = 1; }
    }
    { /* an interval touching 0 complements without underflow */
      PcrecCpSet s; pcrec_cpset_init(&s, &cx.arena);
      pcrec_cpset_add(&s, 0, 0);
      pcrec_cpset_complement(&s, 0xFF);
      if (s.n != 1 || s.iv[0].lo != 1 || s.iv[0].hi != 0xFF) { printf("EDGE zero-complement wrong: n=%d\n", s.n); bad = 1; }
    }
    { /* many absorbed at once: fill alternating, then one add swallowing all */
      PcrecCpSet s; pcrec_cpset_init(&s, &cx.arena);
      for (unsigned c = 0; c < 200; c += 2) pcrec_cpset_add(&s, c, c);
      if (s.n != 100) { printf("EDGE alternating wrong: n=%d\n", s.n); bad = 1; }
      pcrec_cpset_add(&s, 0, 199);
      if (s.n != 1 || s.iv[0].lo != 0 || s.iv[0].hi != 199) { printf("EDGE absorb-all wrong: n=%d\n", s.n); bad = 1; }
    }

    printf(bad ? "cpset model check: FAILED\n" : "cpset model check: PASS (%d trials x %d ops + 7 edge cases)\n", TRIALS, OPS);
    return bad;
}
