/* cpset.c — [M5.0 stage 1] THE CODE-POINT INTERVAL SET: the `A_CLASS`
 * payload's one representation, its builder, and the ONE function that turns
 * a class node back into the 32-byte bitmap the byte tier wants.
 *
 * Design: docs/design/utf8_design.md §2.2 (the payload), §2.1.4 (the render
 * helper and the assertion that is its whole point), §2.7.1 (the complement
 * universe).
 *
 * ============================================================================
 * WHY THIS FILE IS THE ONLY PLACE A BITMAP IS MADE
 * ============================================================================
 *
 * r54 E1 is the finding this file's shape is a response to, and it is worth
 * stating in full because the shape looks like ceremony otherwise. Under the
 * design's first pipeline, `src/gen/emit_vm.c` would have handed a CODE-POINT
 * interval list to `vm_cls`, which interns "the 32 bytes at this address" — so
 * the emitter would have interned the first 32 bytes of an interval array as
 * if they were a membership bitmap. The artifact still compiles. It still
 * matches SOMETHING. No answer check in this project can see it, because
 * every one of them compares what pcrec produced against what an oracle
 * produced for a pattern both understood, and the miscompile changes what
 * pcrec produced for a pattern nothing else disagrees about.
 *
 * So the repair is not "put the lowering in the right place" — that is
 * `src/opt/lower_enc.c`'s job and it is done. The repair is that the WRONG
 * PLACE IS NO LONGER EXPRESSIBLE: `Ast.u.cls` has no `bits` member to take
 * the address of, the only path from a node to 32 bytes is
 * `pcrec_cls_bits` below, and that function REFUSES a node whose intervals
 * are not byte-confined. A lowering that did not run is a diagnosed internal
 * error at the site that would have committed the miscompile, not a wrong
 * artifact.
 *
 * `tests/codegen/run_cpset_structure.sh` is the standing form of the same
 * claim (design §8.1.1 check 2): a future emitter site that reaches for the
 * payload directly trips a grep, because an assertion in code nobody
 * re-derives is only as good as the next author's memory.
 *
 * ============================================================================
 * THE BUILDER IS ARENA-BACKED, AND THAT IS ABOUT `ctx_fail`
 * ============================================================================
 *
 * `ctx_fail` longjmps to `compile_driver`'s single `setjmp`, which frees the
 * arena wholesale. Every class in this compiler is built inside a region of
 * code that can refuse — `p_class` raises "invalid range in character class"
 * from the middle of its own accumulation — so a `malloc`/`realloc` builder
 * would leak on every diagnosed pattern, and the leak would be found by the
 * ASan/LSan axis rather than by review. Growing through `arena_alloc` costs
 * the abandoned smaller block (a class reaching 64 intervals wastes 8+16+32
 * ranges' worth, under a kilobyte) and cannot leak by construction.
 *
 * THE INVARIANT, maintained by every operation here and relied on by every
 * consumer: the list is SORTED, DISJOINT and NON-ADJACENT —
 * `lo[i] <= hi[i]` and `hi[i] + 1 < lo[i+1]`. Non-adjacency is the half that
 * is easy to drop and expensive to lose: without it `[a-mn-z]` and `[a-z]`
 * are two different lists denoting one set, and §2.7.2's argument that the
 * artifact does not depend on the pattern's SPELLING stops being true. */

#include <string.h>

#include "core/internal.h"

/* ---- the builder --------------------------------------------------------- */

void pcrec_cpset_init(PcrecCpSet *s, Arena *ar)
{
    s->ar = ar;
    s->iv = NULL;
    s->n = 0;
    s->cap = 0;
}

static void cpset_grow(PcrecCpSet *s, int want)
{
    if (want <= s->cap) return;
    int cap = s->cap ? s->cap * 2 : 8;
    while (cap < want) cap *= 2;
    PcrecCpRange *iv = arena_alloc(s->ar, (size_t)cap * sizeof *iv);
    if (s->n) memcpy(iv, s->iv, (size_t)s->n * sizeof *iv);
    s->iv = iv;
    s->cap = cap;
}

/* Union one closed interval into the set, restoring the invariant.
 *
 * O(n) per call and deliberately not a sorted-merge batch API: the parser adds
 * members ONE AT A TIME in whatever order the pattern wrote them (`[z-ax]`
 * refuses, but `[zax]` does not), the counts are small — a byte class cannot
 * exceed 128 disjoint non-adjacent intervals, and the measured corpus maximum
 * is far below that — and a batch path would be a second, rarer, less-tested
 * spelling of the same merge. */
void pcrec_cpset_add(PcrecCpSet *s, unsigned lo, unsigned hi)
{
    if (lo > hi) return;

    /* First interval that could touch or follow [lo,hi]. `lo` may be 0, so the
     * comparison is written to avoid `lo - 1` underflowing. */
    int i = 0;
    while (i < s->n && s->iv[i].hi + 1 < lo) i++;

    /* Absorb every interval that touches or is adjacent to the new one, and
     * widen [lo,hi] to their union. */
    int j = i;
    while (j < s->n && s->iv[j].lo <= hi + 1) {
        if (s->iv[j].lo < lo) lo = s->iv[j].lo;
        if (s->iv[j].hi > hi) hi = s->iv[j].hi;
        j++;
    }

    if (j - i == 1) {                       /* in place, no shift */
        s->iv[i].lo = lo; s->iv[i].hi = hi;
        return;
    }
    if (j > i) {                            /* absorbed >1: close the gap */
        memmove(s->iv + i + 1, s->iv + j, (size_t)(s->n - j) * sizeof *s->iv);
        s->n -= (j - i - 1);
        s->iv[i].lo = lo; s->iv[i].hi = hi;
        return;
    }
    cpset_grow(s, s->n + 1);                /* absorbed none: insert */
    memmove(s->iv + i + 1, s->iv + i, (size_t)(s->n - i) * sizeof *s->iv);
    s->iv[i].lo = lo; s->iv[i].hi = hi;
    s->n++;
}

/* Remove one closed interval. `.`'s "every code point but `\n`" is the only
 * caller today; §2.3's surrogate excision is the next one. */
void pcrec_cpset_remove(PcrecCpSet *s, unsigned lo, unsigned hi)
{
    if (lo > hi) return;
    for (int i = 0; i < s->n; ) {
        PcrecCpRange r = s->iv[i];
        if (r.hi < lo || r.lo > hi) { i++; continue; }
        if (r.lo >= lo && r.hi <= hi) {     /* wholly removed */
            memmove(s->iv + i, s->iv + i + 1,
                    (size_t)(s->n - i - 1) * sizeof *s->iv);
            s->n--;
            continue;
        }
        if (r.lo < lo && r.hi > hi) {       /* split in two */
            cpset_grow(s, s->n + 1);
            memmove(s->iv + i + 1, s->iv + i,
                    (size_t)(s->n - i) * sizeof *s->iv);
            s->n++;
            s->iv[i].lo = r.lo;     s->iv[i].hi     = lo - 1;
            s->iv[i + 1].lo = hi + 1; s->iv[i + 1].hi = r.hi;
            i += 2;
            continue;
        }
        if (r.lo < lo) s->iv[i].hi = lo - 1;   /* trimmed on the right */
        else           s->iv[i].lo = hi + 1;   /* trimmed on the left */
        i++;
    }
}

void pcrec_cpset_add_set(PcrecCpSet *s, const PcrecCpRange *iv, int n)
{
    for (int i = 0; i < n; i++) pcrec_cpset_add(s, iv[i].lo, iv[i].hi);
}

/* THE BRIDGE FROM THE BYTE-TIER TABLES (§2.2.2). `src/parse/cls_bits.inc`'s
 * generated `pcrec_cls_*[32]` tables and every module port that hands the
 * parser a 32-byte set arrive here; the runs are appended in ascending order,
 * so each `add` lands at the end and the whole conversion is linear. */
void pcrec_cpset_add_bits(PcrecCpSet *s, const unsigned char bits[32])
{
    unsigned c = 0;
    while (c < 256) {
        if (!cls_has(bits, c)) { c++; continue; }
        unsigned lo = c;
        while (c < 256 && cls_has(bits, c)) c++;
        pcrec_cpset_add(s, lo, c - 1);
    }
}

/* THE COMPLEMENT, WITHIN THE ENCODING'S UNIVERSE (§2.7.1, r54 BLOCKING E2).
 *
 * `negate(S) = [0, max_cp] \ S`, and `max_cp` comes from `PcrecEnc` rather
 * than from a constant here. Under `--encoding=byte` (`max_cp == 0xFF`) this
 * is the SAME FUNCTION as the `~bits[i]` loop it replaces, on the same set —
 * which is not a measurement, it is the reason the identity gate has nothing
 * to catch. Complementing within the CODE-POINT space instead, which is what
 * the design's first version said, would have made `[^a]`, `.`, `\D`, `\W`,
 * `\S`, `\H` and `\V` all refuse under the default encoding. */
void pcrec_cpset_complement(PcrecCpSet *s, unsigned max_cp)
{
    PcrecCpSet out;
    pcrec_cpset_init(&out, s->ar);
    unsigned next = 0;        /* lowest code point not yet accounted for */
    bool topped = false;      /* the input already reached `max_cp` */
    for (int i = 0; i < s->n; i++) {
        if (s->iv[i].lo > max_cp) break;
        if (s->iv[i].lo > next) pcrec_cpset_add(&out, next, s->iv[i].lo - 1);
        if (s->iv[i].hi >= max_cp) { topped = true; break; }
        next = s->iv[i].hi + 1;
    }
    if (!topped) pcrec_cpset_add(&out, next, max_cp);
    *s = out;
}

bool pcrec_cpset_has(const PcrecCpSet *s, unsigned c)
{
    for (int i = 0; i < s->n; i++) {
        if (c < s->iv[i].lo) return false;
        if (c <= s->iv[i].hi) return true;
    }
    return false;
}

/* PUBLISH: hand the accumulated list to a node.
 *
 * The builder's array is already arena memory, so this is a pointer store and
 * not a copy — and it is why nothing may mutate a PUBLISHED list: two nodes
 * can share one (`src/opt/revdet.c`'s copy constructor copies the pointer,
 * which is exactly what makes a reversed `A_CLASS` free). Every producer
 * builds into its own `PcrecCpSet` and publishes once. */
void pcrec_cpset_publish(PcrecCpSet *s, Ast *a)
{
    a->u.cls.iv = s->iv;
    a->u.cls.n  = s->n;
}

/* ---- the readers of a published payload ---------------------------------- */

/* THE RENDER HELPER (§2.1.4) — the SOLE path from a class node to a 32-byte
 * bitmap, and the assertion is the point rather than the rendering.
 *
 * An interval above 0xFF arriving here means the encoding lowering did not run
 * on this subtree, and the caller is one line away from interning a code-point
 * interval list as if it were a membership bitmap (r54 E1). This turns that
 * into a diagnosed internal error AT THE SITE THAT WOULD HAVE COMMITTED IT.
 *
 * IT IS A `ctx_fail` AND NOT AN `assert`, deliberately (§13 obligation 5). The
 * builds this project ships and tests are `-O2 -g` with no `-DNDEBUG` either
 * way, but "the assertion happens to be enabled in the configuration everyone
 * happens to use" is not a property a check can rest on, and an `assert` in a
 * library kills the caller — [M4.7b]/K7's rule, which is why `arena_alloc`'s
 * out-of-memory path is a diagnosed refusal too. */
void pcrec_cls_bits(Ctx *cx, const Ast *a, uint8_t out[32])
{
    memset(out, 0, 32);
    for (int i = 0; i < a->u.cls.n; i++) {
        unsigned lo = a->u.cls.iv[i].lo, hi = a->u.cls.iv[i].hi;
        if (hi > 0xFF)
            ctx_fail(cx, 0,
                     "internal error: a class holding code point U+%04X "
                     "reached a byte-tier consumer — the encoding lowering "
                     "did not run on this subtree", hi);
        for (unsigned c = lo; c <= hi; c++) cls_set(out, c);
    }
}

/* THE SAME RENDER, FOR THE THREE ANALYSES THAT RUN ABOVE THE LOWERING
 * (§2.5.1's DECLINE rows: `possessify`'s FIRST set and Glushkov position
 * label, `revdet`'s first-byte set).
 *
 * `src/opt/possessify.c` and `src/opt/revdet.c` run inside
 * `pcrec_select_engine` at `compile.c:988`, which is ABOVE the lowering
 * because `pcrec_callgraph_build` forces the lowering down past it (§2.1.2
 * constraint 2). They therefore see CODE POINTS, and refusing here would
 * refuse a legal pattern for an optimisation's convenience.
 *
 * SO THE OUT-OF-RANGE ANSWER IS ALL BYTES, WHICH IS THE SOUND DIRECTION FOR
 * BOTH CALLERS AND IS ALREADY THE ANSWER THEY GIVE FOR A BACKREFERENCE.
 * Both compute a FIRST set to prove a DISJOINTNESS property; a wider FIRST set
 * makes disjointness harder to prove, so the cost is a VERDICT — fewer
 * possessifications, fewer reverse-deterministic rungs — and never an answer.
 * `internal.h`'s `pcrec_revdet_first` note ("WIDENS to all bytes, the sound"
 * answer) is the same argument one level down.
 *
 * IT COSTS NOTHING UNDER `--encoding=byte`, where no interval can exceed 0xFF,
 * which is why the identity gate still reads 100%. Widening these two analyses
 * to reason about intervals properly is deferred under D77 with its
 * measurement named (§2.5.1): a form census over a UTF-8 corpus reporting what
 * fraction of non-ASCII patterns loses a rung, and that corpus does not exist
 * until stage 2. */
void pcrec_cls_bits_widen(const Ast *a, uint8_t out[32])
{
    for (int i = 0; i < a->u.cls.n; i++)
        if (a->u.cls.iv[i].hi > 0xFF) { memset(out, 0xFF, 32); return; }
    memset(out, 0, 32);
    for (int i = 0; i < a->u.cls.n; i++)
        for (unsigned c = a->u.cls.iv[i].lo; c <= a->u.cls.iv[i].hi; c++)
            cls_set(out, c);
}

/* "Is this class exactly one code point, and is that code point a BYTE?" —
 * the interval form of the `altcls_single_bit` popcount the two callers used
 * to write out (`src/opt/altcls.c`'s peelable-branch test, `src/gen/
 * emit_vm.c`'s island literal). Returns the code point, or -1.
 *
 * The `> 0xFF` arm is a DECLINE and not an error: `altcls` runs above the
 * lowering, and "this branch does not start with a single literal byte" is an
 * answer both callers already handle. */
int pcrec_cls_single(const Ast *a)
{
    if (a->u.cls.n != 1) return -1;
    if (a->u.cls.iv[0].lo != a->u.cls.iv[0].hi) return -1;
    if (a->u.cls.iv[0].lo > 0xFF) return -1;
    return (int)a->u.cls.iv[0].lo;
}

bool pcrec_cls_has(const Ast *a, unsigned c)
{
    for (int i = 0; i < a->u.cls.n; i++) {
        if (c < a->u.cls.iv[i].lo) return false;
        if (c <= a->u.cls.iv[i].hi) return true;
    }
    return false;
}
