/* The backtracking VM as EMITTED SPECIALIZED C (docs/design/engine_m4.md §2).
 *
 * THERE IS NO INTERPRETER. APPROACH's opening sentence is that the generated
 * matcher "has no runtime interpreter, no dispatch tables to walk
 * generically", and a backtracking VM is the construct most likely to smuggle
 * one back in — the textbook shape is a bytecode array plus a `switch` in a
 * loop. So the pattern's program IS the emitted control flow: one label per
 * pattern position, every continuation resolved at compile time into a
 * fallthrough or a direct `goto`, and exactly ONE indirect jump in the whole
 * function — the `goto *` at the fail label, which fires once per backtrack
 * and never per byte (§2.7: the VM has no per-byte dispatch, so D13's
 * table-vs-computed-goto arbitration simply does not arise here).
 *
 * The five decisions the emitted shape encodes (§2.2):
 *   1. One function per pattern. Label addresses are function-local, which is
 *      fine WITHIN a call — APPROACH §6's A-4/A-5 "&&label does not survive a
 *      return" is a STREAMING constraint, not a within-call one.
 *   2. The fail label is the only backtracker and the only indirect jump.
 *   3. Greedy vs lazy is WHICH SIDE IS THE FALLTHROUGH. Greedy pushes the
 *      exit and falls into the body; lazy pushes the body and falls into the
 *      exit. No flag is consulted at run time (D18: options compile away,
 *      applied to quantifier preference).
 *   4. Alternation is the same shape, as a CHAIN — one live frame per
 *      alternation at any instant, not one frame per untried branch.
 *   5. Position is a plain local, restored from the resume frame, never
 *      trailed. So is the §2.5 cursor (D44/R21 E-4: a resume frame IS its
 *      save point, the same relationship `pos` has to every frame).
 *
 * BACKTRACKING IS AN EXPLICIT ARRAY, NEVER C RECURSION (§2.3), for three
 * independent reasons any one of which suffices: this project has already
 * paid for unbounded recursion on pattern structure twice (DD-10, D10); D19's
 * 128 KB thread-stack budget is a real number and a recursive matcher's depth
 * is data-dependent; and you cannot portably check C stack depth, while DD-2
 * requires that you check something.
 *
 * WHAT THIS FILE DOES NOT DO, deliberately (§6.4, and the [M4.5] scope line):
 * no DFA islands, no accept-list islands, no auto-possessification, no
 * RX_HYBRID_MIN threshold, no trie-factored first-byte switch. Those are
 * M4.6's, and several of them are gated on measurements nobody has taken.
 * The §2.5 cursor ladder lands at its two lowest rungs (see vm_det_seq).
 */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

/* ---- capacities ------------------------------------------------------------
 *
 * BRING-UP PLACEHOLDERS, and stated as such (§4.6, D12: budgets come from
 * measured medians, and there is no measurement yet — [M4.6] takes it by
 * running the corpus and the bench matrix with the counter instrumented and
 * setting the default from the maximum any legitimate pattern needs, with a
 * stated margin). What is NOT a placeholder is the MECHANISM and the honest
 * stamping: whatever these numbers are, rx_info says what the artifact
 * actually enforces.
 *
 * PCRE2's own match_limit default (10,000,000) is explicitly NOT adopted: its
 * unit is internal match() calls, which it also spends on non-backtracking
 * recursion, where ours is resumptions. Copying the number would be false
 * precision dressed as compatibility, which D26 tier 3 exists to prevent.
 *
 * The two array caps are bounded by D19's 128 KB thread stack rather than
 * chosen for generosity: rx_work is a LOCAL of the search entry, a resume
 * frame is 24 B and a trail entry 16 B (D44.1's measured per-entry constants),
 * so 1024 + 1536 is ~49 KB — a large but survivable share of that budget, and
 * the reason the residual unbounded class carries a stamped subject_ceiling
 * instead of pretending the limit is not there. */
enum {
    VM_DEFAULT_BT_FRAMES    = 1024,
    VM_DEFAULT_TRAIL_FRAMES = 1536,
    /* Exact sizing (§2.5: "where the pattern's dynamic depth is statically
     * bounded the emitter computes the exact requirement") is clamped here.
     * Past the clamp the requirement is bounded but does not fit the stack
     * budget, so the artifact enforces the clamp and says so. */
    VM_MAX_AUTO_BT_FRAMES    = 1024,
    VM_MAX_AUTO_TRAIL_FRAMES = 1536
};

/* §4.6's provisional placeholder, named rather than spelled inline. */
#define VM_DEFAULT_STEP_BUDGET 1000000LL

/* The §2.5 cursor rung only fires for bodies whose emitted inline test stays
 * small; past this the body goes to the frames rung, which is correct and
 * merely costs frames. Keeps `(?:abcdef){3}*`-shaped bodies from emitting a
 * wide conjunction for no gain. */
enum { VM_MAX_STRIDE = 32 };

/* Capture groups a cursor-rung body may contain. A body of stride <= 32 can
 * still nest arbitrarily many groups (`((((a))))` is four groups in one byte),
 * so this is NOT implied by VM_MAX_STRIDE and needs its own bound. */
enum { VM_MAX_BODY_CAPS = 64 };

/* ---- the emitter's state -------------------------------------------------*/

typedef struct {
    Ctx      *cx;
    StrBuf   *b;          /* SCRATCH: the VM function's body, see vm_emit_all */
    const char *p;        /* --prefix */
    char      up[80];     /* uppercased prefix */
    int       nlabel;
    int       ngroups;    /* capturing groups (0 when --no-captures) */
    int       nguard;     /* empty-iteration guard slots assigned so far */
    int       nguard_total; /* the count vm_count_slots found: the low-water
                             * slots sit ABOVE all of them, so their base can
                             * only be computed from the TOTAL, never from
                             * the running assignment counter */
    int       nlow;       /* cursor low-water slots assigned so far */
    long long nodes;      /* emitted-node budget, against PCREC_MAX_VM_NODES */
    bool      used_cursor;
    /* class bitmap pool, deduplicated */
    uint8_t (*cls)[32];
    int       ncls, clscap;
} Vm;

static int vm_label(Vm *v) { return v->nlabel++; }

static void vm_charge(Vm *v)
{
    if (++v->nodes > PCREC_MAX_VM_NODES)
        ctx_fail(v->cx, 0, "pattern too large (VM exceeds %d emitted nodes)",
                 PCREC_MAX_VM_NODES);
}

/* Slot layout in `stv` (§2.4: ONE flat array, so the restore loop is written
 * once, the overflow bound is one number, and a future slot class costs a
 * layout row rather than a new save/restore path).
 *
 *   [0 .. 2*ngroups+1]  capture pairs; slots 0,1 are $0 (written by the ENTRY,
 *                       not by the VM — §3.4)
 *   next nguard         empty-iteration guards (§3.3), one per rmax==-1
 *                       nullable quantifier on the frames rung
 *   next nlow           cursor low-water marks (§2.5's RULED re-push
 *                       discipline). NOT the cursor itself, which is a plain
 *                       untrailed local: what a span loop cannot recover from
 *                       its own resume frame is where the loop STARTED, and
 *                       that is what lives here. It is written once per loop
 *                       ENTRY (not per iteration, and not per retreat), so it
 *                       costs O(1) trail per entry, which is the whole point.
 */
static int vm_slot_guard(Vm *v, int i) { return 2 * (v->ngroups + 1) + i; }
static int vm_slot_low(Vm *v, int i)   { return 2 * (v->ngroups + 1) + v->nguard_total + i; }

/* ---- AST predicates ------------------------------------------------------*/

static const Ast *bare(const Ast *a)
{
    while (a->k == A_CAP) a = a->l;
    return a;
}

/* §3.3: a quantifier whose body can match the empty string must not loop
 * forever. Nullability is the compile-time property that decides whether the
 * guard is emitted at all. */
static bool vm_nullable(const Ast *a)
{
    switch (a->k) {
    case A_CLASS: return false;
    case A_EMPTY: case A_BOL: case A_EOL: return true;
    case A_CAP:   return vm_nullable(a->l);
    case A_CAT:   return vm_nullable(a->l) && vm_nullable(a->r);
    case A_ALT:   return vm_nullable(a->l) || vm_nullable(a->r);
    case A_REP:   return a->rmin == 0 || vm_nullable(a->l);
    }
    return true;
}

/* ---- the class pool -----------------------------------------------------*/

static int vm_cls(Vm *v, const uint8_t *bits)
{
    for (int i = 0; i < v->ncls; i++)
        if (memcmp(v->cls[i], bits, 32) == 0) return i;
    if (v->ncls == v->clscap) {
        int ncap = v->clscap ? v->clscap * 2 : 16;
        uint8_t (*nv)[32] = arena_alloc(&v->cx->arena, (size_t)ncap * 32);
        if (v->ncls) memcpy(nv, v->cls, (size_t)v->ncls * 32);
        v->cls = nv;
        v->clscap = ncap;
    }
    memcpy(v->cls[v->ncls], bits, 32);
    return v->ncls++;
}

/* The membership test for class `ci` on byte expression `byte`.
 *
 * Three shapes, cheapest first, and the choice is a property of the SET, not a
 * heuristic: a singleton is one compare, a contiguous range is the standard
 * unsigned-subtract trick (one subtract, one compare, no branch), and anything
 * else reads the 32-byte bitmap. A full 256-byte set needs no test at all
 * beyond the caller's own bounds check. The bitmap is the same 256-bit
 * representation the AST and the DFA already use (§2.9), so nothing here has
 * to agree with a second encoding of "which bytes". */
static void vm_cls_test(Vm *v, StrBuf *b, int ci, const char *byte)
{
    const uint8_t *bits = v->cls[ci];
    int lo = -1, hi = -1, count = 0;
    for (int c = 0; c < 256; c++)
        if (cls_has(bits, (unsigned)c)) { if (lo < 0) lo = c; hi = c; count++; }

    if (count == 256) { sb_puts(b, "1"); return; }
    if (count == 1)   { sb_printf(b, "%s == %d", byte, lo); return; }
    if (count == hi - lo + 1) {
        sb_printf(b, "(unsigned)(%s - %d) <= %du", byte, lo, hi - lo);
        return;
    }
    sb_printf(b, "(%s_k%d[(%s) >> 3] >> ((%s) & 7)) & 1", v->p, ci, byte, byte);
}

/* ---- §2.5's cursor ladder: is this body a deterministic fixed-length run? --
 *
 * Returns the body's length in bytes (>= 1) and fills `out` with its class
 * sequence, or 0 when the body does not qualify.
 *
 * WHY THIS RUNG IS NOT OPTIONAL. §2.5's STRUCTURAL note: a quantified SIMPLE
 * item must not push one frame per iteration, because an 8 MB `a*` cannot
 * store 8 M frames in an allocation-free matcher. So this is not a speed
 * optimization that could be deferred to M4.6 — without it the VM cannot run
 * `a*` on a long subject at all.
 *
 * EXACTNESS CONDITION (§2.5): determinism plus fixed length give any consumed
 * run a UNIQUE decomposition into iterations, so every retreat position is a
 * real iteration boundary and no other exists. A choice-bearing body like
 * `(a|bc)` breaks the constant stride and falls back to frames — which is why
 * A_ALT is rejected here even when its branches happen to have equal length:
 * equal length is not determinism, and the capture spans D44.1 derives from
 * the cursor would be wrong for the branch not taken.
 *
 * D44.1 EXTENDS the rung to CAPTURE-BEARING bodies, which §2.5 as originally
 * written excluded by definition (a capture write needs an RX_SET call, which
 * a plain span loop never makes) — so every capture-bearing quantifier fell
 * back to one frame PER ITERATION regardless of whether its body was actually
 * deterministic, which is where the panel's measured Θ(n) working set came
 * from. Here A_CAP is transparent to the length computation and its group's
 * span is DERIVED FROM THE CURSOR at loop exit instead (see vm_cap_offsets),
 * so a deterministic capture-bearing body allocates no per-iteration frame
 * AND no per-iteration trail entry.
 *
 * THE RUNGS THIS DOES NOT IMPLEMENT, named so they are not mistaken for
 * oversights: disjoint-follow auto-possessification (§6.3 schedules it at
 * M4.6 with the island work it shares an analysis with), the
 * reverse-deterministic backwards walk, and the boundary-record rung. Each is
 * a strict improvement over falling back to frames, none is needed for
 * correctness, and the last two need a per-quantifier reversed automaton this
 * milestone has no other customer for. */
static int vm_det_seq(const Ast *a, const uint8_t **out, int cap)
{
    a = bare(a);
    switch (a->k) {
    case A_CLASS:
        if (cap < 1) return 0;
        out[0] = a->cls;
        return 1;
    case A_CAT: {
        int nl = vm_det_seq(a->l, out, cap);
        if (nl == 0) return 0;
        int nr = vm_det_seq(a->r, out + nl, cap - nl);
        if (nr == 0) return 0;
        return nl + nr;
    }
    case A_REP: {
        /* A fixed count is still deterministic: `(?:ab){2}` is a 4-byte run.
         * Anything else — a range, or unbounded — is a choice point. */
        if (a->rmin != a->rmax || a->rmin <= 0) return 0;
        int total = 0;
        for (int i = 0; i < a->rmin; i++) {
            int nl = vm_det_seq(a->l, out + total, cap - total);
            if (nl == 0) return 0;
            total += nl;
        }
        return total;
    }
    default:
        /* A_ALT (choice), A_EMPTY (zero length), A_BOL/A_EOL (zero-width
         * assertions, which would make "scan ahead by stride" wrong). */
        return 0;
    }
}

/* For the D44.1 extension: every capturing group inside a deterministic
 * fixed-length body, with its byte offset and length RELATIVE to the
 * iteration start. Returns the count, or -1 if more than `cap` were found. */
typedef struct { int group, off, len; } CapOff;

static int vm_cap_offsets(const Ast *a, int base, CapOff *out, int *n, int cap)
{
    switch (a->k) {
    case A_CLASS: return base + 1;
    case A_CAP: {
        int end = vm_cap_offsets(a->l, base, out, n, cap);
        if (end < 0) return -1;
        if (*n >= cap) return -1;
        out[*n].group = a->capno;
        out[*n].off = base;
        out[*n].len = end - base;
        (*n)++;
        return end;
    }
    case A_CAT: {
        int mid = vm_cap_offsets(a->l, base, out, n, cap);
        if (mid < 0) return -1;
        return vm_cap_offsets(a->r, mid, out, n, cap);
    }
    case A_REP: {
        int at = base;
        for (int i = 0; i < a->rmin; i++) {
            at = vm_cap_offsets(a->l, at, out, n, cap);
            if (at < 0) return -1;
        }
        return at;
    }
    default:
        return -1;   /* unreachable for a vm_det_seq-approved body */
    }
}

/* THE RUNG DECISION, in ONE place (§2.5's ladder, D44.1's extension).
 *
 * Three call sites need it and they MUST agree: the slot counter (which sizes
 * `stv` before anything is emitted), the capacity analysis (which sizes the
 * two arrays and stamps the ceiling), and the emitter itself. Two of them
 * disagreeing does not produce a diagnostic — it produces a matcher whose
 * arrays are sized for a shape it does not have.
 *
 * It returns false when the body is not deterministic-fixed-length, AND when
 * its captures overflow `VM_MAX_BODY_CAPS`. The second condition is not a
 * tidiness bound: the cursor rung writes each group's span from the cursor at
 * loop exit, so a group the offset table could not hold would simply never be
 * written and would report UNSET on a match it participated in — a silent
 * wrong span, the one failure mode this project's compatibility standard
 * refuses outright. Falling back to the frames rung costs frames and is
 * always correct. */
static bool vm_cursor_fits(const Ast *rep, const uint8_t **seq, int *stride,
                           CapOff *caps, int *ncaps)
{
    int n = 0;
    int len = vm_det_seq(rep->l, seq, VM_MAX_STRIDE);
    if (len <= 0) return false;
    if (vm_cap_offsets(rep->l, 0, caps, &n, VM_MAX_BODY_CAPS) < 0) return false;
    *stride = len;
    *ncaps = n;
    return true;
}

/* ---- capacity analysis (§2.5's two capacities, §4.5's SECOND bound) -------
 *
 * Two bounds, two errors, and they are different failures with different
 * diagnoses (§4.5): a pattern can overflow the frame array in a handful of
 * steps (`((a)|b){0,10000}` on a long subject) and a pattern can burn the step
 * budget with a two-frame stack (`(a*)b`).
 *
 * `unbounded` marks the residual class D44.1 names: quantifier bodies that are
 * NOT provably single-path, whose depth grows with the subject. For those the
 * artifact carries an HONEST STAMPED CEILING rather than silently capping at
 * whatever the default array size happens to be — a caller can then know the
 * limit without discovering it by triggering <PREFIX>_ERR_FRAMES.
 *
 * Conservative in the safe direction throughout: over-estimating cost lowers
 * the stamped ceiling, which under-promises rather than over-promises. */
typedef struct {
    long long frames, trail;  /* max simultaneously live (bounded part) */
    long long pf, pt;         /* per-ITERATION frames/trail of the outermost
                               * growing quantifier — the divisor the stamped
                               * ceiling is computed from. Read as per-byte,
                               * which is the conservative direction: an
                               * iteration consumes at least one byte unless the
                               * body is nullable, and a nullable body's loop is
                               * stopped by the empty-iteration guard after one
                               * such iteration (S3.3). */
    bool      unbounded;      /* depth grows without a static bound */
    bool      growable;       /* depth grows WITH the subject at all — true for
                               * `unbounded`, and ALSO for a bounded repeat
                               * whose count is large. The two are stamped the
                               * same way and the distinction only decides
                               * whether the EXACT requirement is worth trying
                               * to honour. */
} Cost;

static Cost vm_cost(Vm *v, const Ast *a);

static Cost vm_cost_rep(Vm *v, const Ast *a)
{
    const uint8_t *seq[VM_MAX_STRIDE];
    CapOff caps[VM_MAX_BODY_CAPS];
    int stride = 0, nc = 0;
    Cost c = { 0, 0, 0, 0, false, false };
    Cost body = vm_cost(v, a->l);

    if (a->rmin == 0 && a->rmax == 0) return c;

    if (vm_cursor_fits(a, seq, &stride, caps, &nc)) {
        /* cursor rung: ONE live frame ever, one low-water write per entry,
         * plus one write per capture in the body per (re)try — all of which
         * the resume frame's own mark rewinds, so they do not accumulate. */
        c.frames = 1;
        c.trail = 1 + 2 * nc;
        return c;
    }

    if (a->rmax < 0) {
        /* frames rung, unbounded: one frame per iteration, and an iteration
         * that consumes nothing terminates the loop (§3.3's guard), so every
         * completed iteration but the last consumes at least one byte. */
        c.unbounded = c.growable = true;
        c.pf = 1 + body.frames + body.pf;
        c.pt = (vm_nullable(a->l) ? 1 : 0) + body.trail + body.pt;
        c.frames = (long long)a->rmin * body.frames;
        c.trail = (long long)a->rmin * body.trail;
        return c;
    }

    /* frames rung, bounded: rmin mandatory copies plus (rmax - rmin) nested
     * optionals, each optional contributing its own live frame (§3.3's RULED
     * replication reading — a bounded quantifier compiles as its copies, with
     * no guard slot and no suppression test at all).
     *
     * `growable` is set here too, and that is the point of the flag. A bounded
     * repeat's requirement IS statically known — but "statically known" and
     * "fits the emitted array" are different claims, and `((a)|b){0,4000}c`
     * satisfies the first and not the second. Stamping subject_ceiling = 0
     * ("not applicable") for such an artifact says there is no limit when
     * there is one, which is exactly the silent cap D44.1's honest stamp
     * exists to replace. The per-iteration costs below let pcrec_emit_vm
     * stamp a real ceiling whenever the requirement does not fit. */
    c.frames = (long long)a->rmin * body.frames
             + (long long)(a->rmax - a->rmin) * (1 + body.frames);
    c.trail = (long long)a->rmax * body.trail;
    c.unbounded = body.unbounded;
    c.growable = true;
    c.pf = 1 + body.frames + body.pf;
    c.pt = body.trail + body.pt;
    return c;
}

static Cost vm_cost(Vm *v, const Ast *a)
{
    Cost c = { 0, 0, 0, 0, false, false };
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL:
        return c;
    case A_CAP:
        c = vm_cost(v, a->l);
        c.trail += 2;
        return c;
    case A_CAT: {
        Cost l = vm_cost(v, a->l), r = vm_cost(v, a->r);
        c.frames = l.frames + r.frames;
        c.trail = l.trail + r.trail;
        c.pf = l.pf + r.pf;
        c.pt = l.pt + r.pt;
        c.unbounded = l.unbounded || r.unbounded;
        c.growable = l.growable || r.growable;
        return c;
    }
    case A_ALT: {
        /* The chain shape keeps exactly ONE alternation frame live at a time
         * (see vm_alt), and a failed branch's own frames are popped before the
         * next branch runs — so this is max-plus-one, not a sum. */
        Cost l = vm_cost(v, a->l), r = vm_cost(v, a->r);
        c.frames = 1 + (l.frames > r.frames ? l.frames : r.frames);
        c.trail = l.trail > r.trail ? l.trail : r.trail;
        c.pf = l.pf > r.pf ? l.pf : r.pf;
        c.pt = l.pt > r.pt ? l.pt : r.pt;
        c.unbounded = l.unbounded || r.unbounded;
        c.growable = l.growable || r.growable;
        return c;
    }
    case A_REP:
        return vm_cost_rep(v, a);
    }
    return c;
}

/* ---- slot counting (must mirror the emitter's own rung decisions) --------*/

static void vm_count_slots(Vm *v, const Ast *a)
{
    const uint8_t *seq[VM_MAX_STRIDE];
    CapOff caps[VM_MAX_BODY_CAPS];
    int stride = 0, nc = 0;
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL:
        return;
    case A_CAP: vm_count_slots(v, a->l); return;
    case A_CAT: case A_ALT:
        vm_count_slots(v, a->l); vm_count_slots(v, a->r); return;
    case A_REP:
        if (a->rmin == 0 && a->rmax == 0) return;
        if (vm_cursor_fits(a, seq, &stride, caps, &nc)) { v->nlow++; return; }
        /* Frames rung: the body's code is REPLICATED once per mandatory copy
         * and once per optional copy, and each copy's own loops need their own
         * slots — so the count must replicate exactly as the emitter does or
         * two live loops would share one slot. */
        {
            int copies = a->rmax < 0 ? a->rmin + 1 : a->rmax;
            if (copies < 1) copies = 1;
            for (int i = 0; i < copies; i++) vm_count_slots(v, a->l);
            if (a->rmax < 0 && vm_nullable(a->l)) v->nguard++;
        }
        return;
    }
}

/* ---- emission -----------------------------------------------------------*/

static void vm_emit(Vm *v, int entry, const Ast *a, int next);

static void vm_lbl(Vm *v, int id)
{
    /* The `__attribute__((unused))` follows emit_attempt's precedent: a label
     * that is only ever reached through a resume frame's `&&` address, or one
     * the flattening below makes unreachable, must not fail the harness's
     * -Werror generated-code build. */
    sb_printf(v->b, "%s_L%d: __attribute__((unused));\n", v->p, id);
}

static void vm_goto(Vm *v, int id) { sb_printf(v->b, "    goto %s_L%d;\n", v->p, id); }
static void vm_fail(Vm *v)         { sb_printf(v->b, "    goto %s_fail;\n", v->p); }

static void vm_push(Vm *v, int lblid)
{
    sb_printf(v->b, "    %s_PUSH(&&%s_L%d, pos);\n", v->up, v->p, lblid);
}

static void vm_set(Vm *v, int slot, const char *val)
{
    sb_printf(v->b, "    %s_SET(%d, %s);\n", v->up, slot, val);
}

/* Flat alternation as a CHAIN (§2.2 property 4, refined). The design's text
 * says "N-way alternation pushes a chain, one frame per untried branch, in
 * reverse preference order"; pushing all N-1 frames eagerly and pushing them
 * one at a time as each branch is tried are both correct, and this emits the
 * second because it holds ONE live frame per alternation instead of N-1,
 * which is what keeps `(a|b|c|...)` off the frame-capacity bound. The
 * preference order is identical either way: the frame pushed at branch k
 * resumes branch k+1. */
static void vm_alt(Vm *v, int entry, const Ast *a, int next)
{
    Ctx *cx = v->cx;
    int nbr = 1;
    for (const Ast *t = a; t->k == A_ALT; t = t->l) nbr++;
    const Ast **br = arena_alloc(&cx->arena, (size_t)nbr * sizeof(Ast *));
    int i = nbr;
    const Ast *t = a;
    while (t->k == A_ALT) { br[--i] = t->r; t = t->l; }
    br[0] = t;

    int *bentry = arena_alloc(&cx->arena, (size_t)nbr * sizeof(int));
    int *resume = arena_alloc(&cx->arena, (size_t)nbr * sizeof(int));
    for (int j = 0; j < nbr; j++) bentry[j] = vm_label(v);
    resume[0] = entry;
    for (int j = 1; j < nbr; j++) resume[j] = vm_label(v);

    for (int j = 0; j < nbr; j++) {
        vm_lbl(v, resume[j]);
        if (j + 1 < nbr) vm_push(v, resume[j + 1]);
        vm_goto(v, bentry[j]);
    }
    for (int j = 0; j < nbr; j++) vm_emit(v, bentry[j], br[j], next);
}

/* §2.5's cursor rung, with D44.1's capture extension.
 *
 * GREEDY: consume greedily to the furthest position, then push exactly ONE
 * resume frame recording the cursor. On BACKTRACK the engine decrements the
 * cursor by the stride and RE-PUSHES the same frame (same label, new pos)
 * before retrying the continuation — so a second backtrack into the loop has
 * somewhere to land, and the stack still holds never more than one live frame
 * for this loop even though the loop may be re-entered (furthest − low-water)
 * times across the whole match. Each re-push REPLACES the just-popped frame
 * rather than growing the stack (D44/R21 E-4's re-push discipline, written out
 * explicitly there because it had been left unshown).
 *
 * The cursor is a plain local; the resume frame's own `pos` field is its save
 * point. What the frame cannot carry is where the loop STARTED, which the
 * low-water test needs and which an OUTER backtrack must restore — a second
 * entry to the same loop at a different position would otherwise leave a stale
 * low-water mark behind for the first entry's frame to retreat against. That
 * is what the trailed low-water slot is for, and it is written once per loop
 * ENTRY, so the mechanism designed to avoid per-iteration trail entries does
 * not quietly reintroduce one.
 *
 * CAPTURES (D44.1): a deterministic body's group spans are computed FROM THE
 * CURSOR at the point the continuation is taken, not written per iteration —
 * `[cursor − stride + off, cursor − stride + off + len)` for a group at
 * relative offset `off`. The writes go AFTER the push, so the frame's own mark
 * rewinds them on every retreat and they never accumulate on the trail. */
static void vm_cursor_rep(Vm *v, int entry, const Ast *a, int next,
                          const uint8_t **seq, int stride,
                          const CapOff *caps, int ncaps)
{
    StrBuf *b = v->b;
    int low = vm_slot_low(v, v->nlow++);
    int retry = vm_label(v), again = vm_label(v);
    long long lo_off = (long long)a->rmin * stride;

    v->used_cursor = true;

    /* class ids first, so the pool is stable before any test is written */
    int *ci = arena_alloc(&v->cx->arena, (size_t)stride * sizeof(int));
    for (int i = 0; i < stride; i++) ci[i] = vm_cls(v, seq[i]);

    /* The body's own inline test, written once and reused by both rungs. */
    StrBuf t;
    memset(&t, 0, sizeof t);
    for (int i = 0; i < stride; i++) {
        char byte[64];
        snprintf(byte, sizeof byte, "s[%s_cur + %d]", v->p, i);
        sb_puts(&t, " && (");
        vm_cls_test(v, &t, ci[i], byte);
        sb_puts(&t, ")");
    }
    const char *test = t.p ? t.p : "";

    vm_lbl(v, entry);
    /* The loop's ENTRY position, trailed. Both rungs derive their bounds from
     * it: low-water is entry + stride*rmin, ceiling is entry + stride*rmax. */
    vm_set(v, low, "(ptrdiff_t)pos");

    if (a->greedy) {
        /* consume greedily to the furthest position */
        sb_puts(b, "    {\n");
        if (a->rmax >= 0) sb_puts(b, "        unsigned long it_ = 0;\n");
        sb_printf(b, "        %s_cur = pos;\n", v->p);
        sb_printf(b, "        while (%s_cur + %d <= n", v->p, stride);
        if (a->rmax >= 0) sb_printf(b, " && it_ < %dUL", a->rmax);
        sb_printf(b, "%s) { %s_cur += %d;", test, v->p, stride);
        if (a->rmax >= 0) sb_puts(b, " it_++;");
        sb_puts(b, " }\n    }\n");
        vm_goto(v, retry);

        vm_lbl(v, retry);
        sb_printf(b, "    if ((ptrdiff_t)%s_cur < stv[%d] + %lld) goto %s_fail;\n",
                  v->p, low, lo_off, v->p);
    } else {
        /* LAZY: the shortest acceptable run first, extended one stride per
         * backtrack. Greedy vs lazy is which side is the fallthrough (S2.2
         * property 3) — here the CONTINUATION is, and the frame resumes the
         * extension, exactly mirroring the greedy rung's frame resuming the
         * retreat. Getting this wrong is not a performance difference: `(a*?)a`
         * on "aa" gives [0,2)/g1=[0,1) under a greedy scan where both oracles
         * give [0,1)/g1=[0,0). */
        sb_printf(b, "    %s_cur = pos;\n", v->p);
        if (a->rmin > 0) {
            sb_puts(b, "    {\n        unsigned long it_ = 0;\n");
            sb_printf(b, "        while (it_ < %dUL) {\n", a->rmin);
            sb_printf(b, "            if (!(%s_cur + %d <= n%s)) goto %s_fail;\n",
                      v->p, stride, test, v->p);
            sb_printf(b, "            %s_cur += %d; it_++;\n", v->p, stride);
            sb_puts(b, "        }\n    }\n");
        }
        vm_goto(v, retry);

        vm_lbl(v, retry);
    }

    sb_printf(b, "    %s_PUSH(&&%s_L%d, %s_cur);\n", v->up, v->p, again, v->p);
    if (ncaps) {
        /* Only a loop that ran at least once wrote its groups. Below that the
         * previous value stands, which is what `(a)*` matching zero times must
         * report — and, inside an enclosing loop, is what makes a failed final
         * iteration restore group k to the value the SUCCESSFUL earlier
         * iteration left rather than to unset (S3.2). */
        sb_printf(b, "    if ((ptrdiff_t)%s_cur >= stv[%d] + %d) {\n",
                  v->p, low, stride);
        for (int i = 0; i < ncaps; i++) {
            char val[96];
            snprintf(val, sizeof val, "(ptrdiff_t)(%s_cur - %d)", v->p,
                     stride - caps[i].off);
            sb_printf(b, "    %s_SET(%d, %s);\n", v->up,
                      2 * caps[i].group, val);
            snprintf(val, sizeof val, "(ptrdiff_t)(%s_cur - %d)", v->p,
                     stride - caps[i].off - caps[i].len);
            sb_printf(b, "    %s_SET(%d, %s);\n", v->up,
                      2 * caps[i].group + 1, val);
        }
        sb_puts(b, "    }\n");
    }
    sb_printf(b, "    pos = %s_cur;\n", v->p);
    vm_goto(v, next);

    vm_lbl(v, again);
    /* the fail label restored pos from this frame, i.e. to the cursor value
     * the push recorded — so the retreat/extension needs no save slot */
    sb_printf(b, "    %s_cur = pos;\n", v->p);
    if (a->greedy) {
        sb_printf(b, "    if ((ptrdiff_t)%s_cur < stv[%d] + %lld + %d) goto %s_fail;\n",
                  v->p, low, lo_off, stride, v->p);
        sb_printf(b, "    %s_cur -= %d;\n", v->p, stride);
    } else {
        if (a->rmax >= 0)
            sb_printf(b, "    if ((ptrdiff_t)%s_cur >= stv[%d] + %lld) goto %s_fail;\n",
                      v->p, low, (long long)a->rmax * stride, v->p);
        sb_printf(b, "    if (!(%s_cur + %d <= n%s)) goto %s_fail;\n",
                  v->p, stride, test, v->p);
        sb_printf(b, "    %s_cur += %d;\n", v->p, stride);
    }
    vm_goto(v, retry);
    sb_free(&t);
}

/* Nested optional chain for a bounded repeat: `X{0,3}` is `(X(X(X)?)?)?`,
 * NESTED and not chained. The two accept the same language and differ in
 * BACKTRACK PREFERENCE — with chained optionals a later copy's alternation
 * choice outranks an earlier copy's, so lazy bounded repeats pick the wrong
 * span. nfa.c's A_REP arm carries the measurement that found this
 * (`(?:ab|a){0,2}?b` on "abab" gave [0,2) where PCRE2 and python give [0,4)),
 * and the VM must make the same choice for the same reason. */
static void vm_opt_chain(Vm *v, int entry, const Ast *body, int count,
                         int next, bool greedy)
{
    if (count <= 0) {
        vm_lbl(v, entry);
        vm_goto(v, next);
        return;
    }
    int bentry = vm_label(v), other = vm_label(v), inner = vm_label(v);
    vm_lbl(v, entry);
    if (greedy) {
        vm_push(v, other);           /* the skip is the resume */
        vm_goto(v, bentry);
    } else {
        vm_push(v, other);           /* the body is the resume */
        vm_goto(v, next);
    }
    vm_lbl(v, other);
    vm_goto(v, greedy ? next : bentry);
    vm_emit(v, bentry, body, inner);
    vm_opt_chain(v, inner, body, count - 1, next, greedy);
}

static void vm_rep(Vm *v, int entry, const Ast *a, int next)
{
    const uint8_t *seq[VM_MAX_STRIDE];
    CapOff caps[VM_MAX_BODY_CAPS];
    int stride = 0, ncaps = 0;

    if (a->rmin == 0 && a->rmax == 0) {   /* X{0} matches empty */
        vm_lbl(v, entry);
        vm_goto(v, next);
        return;
    }

    if (vm_cursor_fits(a, seq, &stride, caps, &ncaps)) {
        vm_cursor_rep(v, entry, a, next, seq, stride, caps, ncaps);
        return;
    }

    /* ---- the frames rung ------------------------------------------------
     * rmin mandatory copies, then either the unbounded star or (rmax - rmin)
     * nested optionals. RULED (D44/R21 E-2): the empty-iteration guard exists
     * ONLY for rmax == -1. The panel MEASURED the "or high-bounded" reading
     * against libpcre2 — with the guard applied to bounded repeats too, 60 of
     * 225,240 generated pairs diverge; restricted to rmax == -1, 0 of 225,240.
     * PCRE2's actual behaviour is that bounded repeats REPLICATE: a {1,2} body
     * is body-body?, each copy an independent opportunity to match empty or
     * not, because there IS no "continuation" test at a bounded count — there
     * is just the next copy. */
    int cur = entry;
    for (int i = 0; i < a->rmin; i++) {
        int nx = vm_label(v);
        vm_emit(v, cur, a->l, nx);
        cur = nx;
    }

    if (a->rmax >= 0) {
        vm_opt_chain(v, cur, a->l, a->rmax - a->rmin, next, a->greedy);
        return;
    }

    /* the unbounded star */
    bool guard = vm_nullable(a->l);
    int gslot = guard ? vm_slot_guard(v, v->nguard++) : -1;
    int bentry = vm_label(v), bend = vm_label(v), exit = vm_label(v);

    vm_lbl(v, cur);
    if (guard) vm_set(v, gslot, "(ptrdiff_t)pos");
    if (a->greedy) {
        vm_push(v, exit);            /* greedy: another iteration is preferred */
        vm_goto(v, bentry);
    } else {
        vm_push(v, bentry);          /* lazy: the exit is preferred */
        vm_goto(v, exit);
    }

    vm_emit(v, bentry, a->l, bend);

    vm_lbl(v, bend);
    if (guard) {
        /* THE EMPTY-ITERATION RULE (§3.3), and its exact shape matters.
         *
         * An iteration that consumed nothing must not iterate again — but it
         * is NOT rolled back. Control takes the EXIT CONTINUATION, so the
         * empty iteration's own capture writes STAND. §3.3 says exactly this
         * ("control takes the exit continuation") and it is worth stating why,
         * because the mechanism invites the other reading: failing the path
         * instead would let the trail undo the write for free, and it is
         * WRONG. Both oracles give `(a*)*` on "a" a group 1 of [1,1) — the
         * second, empty iteration at position 1 ran, wrote its group, and then
         * stopped the loop. The roll-back reading reports [0,1), the FIRST
         * iteration's value, across the whole nullable-body family; `(|a)+`
         * additionally loses the WHOLE MATCH, reporting [0,1) where both
         * oracles give [0,0), because rolling back the empty iteration lets
         * the loop go round again.
         *
         * The exit frame this iteration pushed stays on the stack, so a later
         * failure of the continuation resumes it and enters the exit once more
         * with the empty iteration's writes rewound. That duplicate is
         * harmless — same position, same continuation, and base-tier matching
         * never reads captures, so the second attempt fails exactly as the
         * first did — but it is real work and one charged step. Dropping the
         * frame instead is not available: it need not be on top, because the
         * body may have left its own choice points above it and those must
         * still get their turn. Recorded for [M4.6] rather than solved with a
         * mechanism that mutates a frame in place, which does not survive the
         * loop being re-entered. */
        sb_printf(v->b, "    if ((ptrdiff_t)pos != stv[%d]) goto %s_L%d;\n",
                  gslot, v->p, cur);
        vm_goto(v, exit);
    } else {
        vm_goto(v, cur);
    }

    vm_lbl(v, exit);
    vm_goto(v, next);
}

static void vm_emit(Vm *v, int entry, const Ast *a, int next)
{
    StrBuf *b = v->b;
    vm_charge(v);

    switch (a->k) {
    case A_CLASS: {
        int ci = vm_cls(v, a->cls);
        vm_lbl(v, entry);
        sb_puts(b, "    if (pos < n && (");
        vm_cls_test(v, b, ci, "s[pos]");
        sb_printf(b, ")) { pos++; goto %s_L%d; }\n", v->p, next);
        vm_fail(v);
        return;
    }
    case A_EMPTY:
        vm_lbl(v, entry);
        vm_goto(v, next);
        return;
    case A_BOL:
        /* `^` is start of SUBJECT, absolute — it anchors to offset 0 whatever
         * startpos was, matching the emitted contract in lib/pcrec.h and the
         * DFA's own N_BOT. */
        vm_lbl(v, entry);
        sb_printf(b, "    if (pos == 0) goto %s_L%d;\n", v->p, next);
        vm_fail(v);
        return;
    case A_EOL:
        vm_lbl(v, entry);
        sb_printf(b, "    if (pos == n || (pos + 1 == n && s[pos] == '\\n')) "
                     "goto %s_L%d;\n", v->p, next);
        vm_fail(v);
        return;
    case A_CAP: {
        /* §3.2 WRITE ON TRAVERSE: caps[k][0] when control passes the opening
         * position, caps[k][1] when it passes the closing one. Undo is EXACT
         * RESTORE of the previous value, never a clear — the trail, not this
         * site, is where that lives. */
        int inner = vm_label(v), close = vm_label(v);
        vm_lbl(v, entry);
        vm_set(v, 2 * a->capno, "(ptrdiff_t)pos");
        vm_goto(v, inner);
        vm_emit(v, inner, a->l, close);
        vm_lbl(v, close);
        vm_set(v, 2 * a->capno + 1, "(ptrdiff_t)pos");
        vm_goto(v, next);
        return;
    }
    case A_CAT: {
        /* flatten the left-leaning spine iteratively (nfa.c's R-2 hardening,
         * for the same reason: a flat concatenation of any length must not
         * overflow the C stack of pcrec's OWN emitter) */
        int nsp = 0;
        const Ast *t = a;
        while (t->k == A_CAT) { nsp++; t = t->l; }
        const Ast **rs = arena_alloc(&v->cx->arena, (size_t)nsp * sizeof(Ast *));
        int i = nsp;
        t = a;
        while (t->k == A_CAT) { rs[--i] = t->r; t = t->l; }
        int cur = entry;
        int nx = vm_label(v);
        vm_emit(v, cur, t, nx);
        cur = nx;
        for (int j = 0; j < nsp; j++) {
            int after = (j + 1 == nsp) ? next : vm_label(v);
            vm_emit(v, cur, rs[j], after);
            cur = after;
        }
        return;
    }
    case A_ALT:
        vm_alt(v, entry, a, next);
        return;
    case A_REP:
        vm_rep(v, entry, a, next);
        return;
    }
    ctx_fail(v->cx, 0, "internal error: bad AST node in VM emitter");
}

/* ---- the artifact -------------------------------------------------------*/

static long long vm_ceiling(long long cap, long long per)
{
    if (per <= 0) return 0;
    return cap / per;
}

void pcrec_emit_vm(Ctx *cx, const Ast *root)
{
    Job *job = cx->job;
    StrBuf *c = &job->csb;
    Vm v;
    GenNames g;

    memset(&v, 0, sizeof v);
    v.cx = cx;
    v.b = &job->vmsb;   /* Job-owned, so the longjmp cleanup path frees it */
    v.p = cx->opt->prefix;
    v.ngroups = cx->want_caps ? (int)cx->ncap : 0;

    pcrec_gen_names(cx, &g);
    memcpy(v.up, g.upper, sizeof v.up);

    const int ncaps = v.ngroups + 1;

    /* Slot counting first: RX_NSTATE has to be known before the rx_work type
     * is emitted, and it must agree EXACTLY with what the emitter goes on to
     * assign — so the counter mirrors the emitter's own rung decisions rather
     * than approximating them. */
    vm_count_slots(&v, root);
    const int nguard_total = v.nguard, nlow_total = v.nlow;
    v.nguard_total = nguard_total;
    v.nguard = v.nlow = 0;
    const int nstate = 2 * ncaps + nguard_total + nlow_total;

    /* §2.5's two capacities. */
    Cost cost = vm_cost(&v, root);
    long long bt_frames, trail_frames, ceiling = 0;
    bool fits;
    if (cx->opt->frame_capacity > 0) {
        bt_frames = cx->opt->frame_capacity;
        trail_frames = cx->opt->frame_capacity;
    } else if (cost.unbounded) {
        bt_frames = VM_DEFAULT_BT_FRAMES;
        trail_frames = VM_DEFAULT_TRAIL_FRAMES;
    } else {
        bt_frames = cost.frames + 1;
        trail_frames = cost.trail + 1;
        if (bt_frames > VM_MAX_AUTO_BT_FRAMES) bt_frames = VM_MAX_AUTO_BT_FRAMES;
        if (trail_frames > VM_MAX_AUTO_TRAIL_FRAMES)
            trail_frames = VM_MAX_AUTO_TRAIL_FRAMES;
    }
    if (bt_frames < 1) bt_frames = 1;
    if (trail_frames < 1) trail_frames = 1;

    /* THE STAMP IS ABOUT WHAT THE ARTIFACT ENFORCES, NOT WHAT IT WANTED.
     * A ceiling is owed whenever the depth grows with the subject AND the
     * exact requirement does not fit the arrays actually emitted — which
     * covers the unbounded class (where no exact requirement exists) and the
     * large-bounded one (where it exists and is too big) with one rule. A
     * pattern whose requirement DOES fit has no limit to declare, and stamps
     * 0 truthfully. Getting this wrong in the other direction is what a
     * silent cap looks like: `((a)|b){0,4000}c` is statically bounded at 4000
     * frames, gets 1024, and would otherwise have stamped "not applicable". */
    fits = !cost.unbounded && cost.frames + 1 <= bt_frames
                           && cost.trail + 1 <= trail_frames;
    if (cost.growable && !fits) {
        long long a = vm_ceiling(bt_frames, cost.pf);
        long long b = vm_ceiling(trail_frames, cost.pt);
        ceiling = (a && b) ? (a < b ? a : b) : (a ? a : b);
    }

    long long budget = cx->opt->step_budget;
    if (budget == PCREC_STEP_BUDGET_DEFAULT) budget = VM_DEFAULT_STEP_BUDGET;
    const bool has_budget = budget != PCREC_STEP_BUDGET_NONE;

    /* Emit the program into the scratch buffer FIRST: the class pool, the
     * cursor-local's presence and the emitted-node count are all discovered
     * by emitting, and all three have to appear in text that precedes the
     * program. Assembling in this order is what keeps them from being
     * predicted by a second, drift-prone analysis. */
    {
        int rootentry = vm_label(&v);
        int acc = vm_label(&v);
        vm_emit(&v, rootentry, root, acc);
        sb_printf(v.b, "%s_L%d: __attribute__((unused));\n", v.p, acc);
        sb_printf(v.b, "    goto %s_accept;\n", v.p);
        /* rootentry is label 0 by construction; the prologue jumps to it */
    }

    pcrec_emit_prologue(cx, &g, ncaps);

    /* §5.5's stamp. RETAINED alongside rx_info (D43.1 makes rx_info the
     * CANONICAL machine-readable record) because the two serve different
     * consumers and are therefore not redundant: rx_info is a .rodata symbol,
     * readable only by LINKING against the artifact or reading the compiled
     * binary, while these are preprocessor-visible at COMPILE time, which is
     * what a tests/codegen structural check or a build-time `#ifdef` needs.
     *
     * [AS-BUILT DEVIATION, REPORTED] §5.5 shows this stamp on every artifact;
     * it is emitted on VM artifacts ONLY. Emitting it on the DFA path too
     * would put a new line in output that §5.4's byte-identity gate compares,
     * forcing the gate to FILTER rather than compare whole files — and a
     * filtered gate is exactly the check-design failure this project has
     * recorded twice. rx_info.engine already carries the engine on both
     * artifacts, so nothing is lost but the compile-time visibility, which on
     * a DFA artifact has no consumer. */
    sb_printf(c, "/* Engine: vm (forced by: %s) */\n",
              job->fit.why ? job->fit.why : "--engine=vm");
    if (has_budget)
        sb_printf(c, "/* Step budget: %lld backtrack resumptions; backtrack "
                     "frames: %lld */\n", budget, bt_frames);
    else
        sb_printf(c, "/* Step budget: none (--fno-step-budget); backtrack "
                     "frames: %lld */\n", bt_frames);
    sb_printf(c, "#define %s_ENGINE \"vm\"\n", v.up);
    sb_puts(c, "#define ");
    sb_printf(c, "%s_ENGINE_WHY ", v.up);
    pcrec_emit_c_string_literal(c, job->fit.why ? job->fit.why : "--engine=vm",
                                strlen(job->fit.why ? job->fit.why : "--engine=vm"));
    sb_puts(c, "\n");
    sb_printf(c, "#define %s_NSTATE %d\n", v.up, nstate < 1 ? 1 : nstate);
    sb_printf(c, "#define %s_BT_FRAMES %lld\n", v.up, bt_frames);
    sb_printf(c, "#define %s_TRAIL_FRAMES %lld\n", v.up, trail_frames);
    if (has_budget)
        sb_printf(c, "#define %s_STEP_BUDGET %lldLL\n", v.up, budget);
    sb_puts(c, "\n");

    /* ---- rx_work: the whole mutable working set, §2.2 ------------------
     * All locals — no globals (TS-1: usable FROM threads, all-const tables,
     * no mutable state outside the caller's own frame) and no allocation
     * (PC-5/D38's COPY_MATCHED_SUBJECT = NEVER precedent). */
    sb_printf(c,
        "typedef struct {\n"
        "    ptrdiff_t stv[%s_NSTATE];\n"
        "    struct { const void *k; size_t pos; unsigned mark; } bt[%s_BT_FRAMES];\n"
        "    struct { unsigned slot; ptrdiff_t v; }               tr[%s_TRAIL_FRAMES];\n"
        "    unsigned btn, trn;\n",
        v.up, v.up, v.up);
    if (has_budget) sb_puts(c, "    long long budget;\n");
    sb_printf(c, "} %s_work;\n\n", v.p);

    /* The internal give-up sentinels. They share the search entry's public
     * <PREFIX>_ERR_* values, but they are a different contract at a different
     * layer (§4.4's three layers: impl returns a private sentinel, the
     * rx_matchfn export collapses it to -1 per D38.4's frozen return space,
     * and only <prefix>_search — which D38 says nothing about — has room for
     * the honest code), so they get their own names. */
    sb_printf(c, "#define %s_R_STEPS  ((ptrdiff_t)%s_ERR_STEPS)\n", v.up, v.up);
    sb_printf(c, "#define %s_R_FRAMES ((ptrdiff_t)%s_ERR_FRAMES)\n\n", v.up, v.up);

    sb_printf(c,
        "#define %s_TRAIL(slot_) do {                                  \\\n"
        "        if (w->trn >= %s_TRAIL_FRAMES) return %s_R_FRAMES;    \\\n"
        "        w->tr[w->trn].slot = (unsigned)(slot_);               \\\n"
        "        w->tr[w->trn].v = stv[(slot_)];                       \\\n"
        "        w->trn++;                                             \\\n"
        "    } while (0)\n"
        "#define %s_SET(slot_, v_) do {                                \\\n"
        "        %s_TRAIL(slot_); stv[(slot_)] = (v_);                 \\\n"
        "    } while (0)\n"
        "#define %s_PUSH(lbl_, p_) do {                                \\\n"
        "        if (w->btn >= %s_BT_FRAMES) return %s_R_FRAMES;       \\\n"
        "        w->bt[w->btn].k = (lbl_);                             \\\n"
        "        w->bt[w->btn].pos = (p_);                             \\\n"
        "        w->bt[w->btn].mark = w->trn;                          \\\n"
        "        w->btn++;                                             \\\n"
        "    } while (0)\n\n",
        v.up, v.up, v.up, v.up, v.up, v.up, v.up, v.up);

    /* The per-search reset (§2.4): stv is initialised to UNSET ONCE per
     * SEARCH call, not per start position. On a failed attempt the trail
     * rewind to mark 0 restores every slot the attempt wrote back to UNSET by
     * construction, so the per-attempt reset is O(writes-since-attempt-start)
     * rather than O(NG) — which matters for the VM-only per-start loop, where
     * a naive memset per start position would be O(NG*n). */
    sb_printf(c,
        "static void %s_work_init(%s_work *w)\n"
        "{\n"
        "    int i;\n"
        "    for (i = 0; i < %s_NSTATE; i++) w->stv[i] = %s_UNSET;\n"
        "    w->btn = 0; w->trn = 0;\n",
        v.p, v.p, v.up, v.up);
    if (has_budget) sb_printf(c, "    w->budget = %s_STEP_BUDGET;\n", v.up);
    sb_puts(c, "}\n\n");

    sb_printf(c,
        "static void %s_unwind(%s_work *w)\n"
        "{\n"
        "    while (w->trn) { w->trn--; w->stv[w->tr[w->trn].slot] = w->tr[w->trn].v; }\n"
        "    w->btn = 0;\n"
        "}\n\n",
        v.p, v.p);

    /* ---- the class bitmaps ------------------------------------------------
     * File-scope `static const` (TS-1: all-const tables, no mutable globals),
     * named under --prefix like every other file-scope symbol this project
     * emits, and only for classes that actually needed a bitmap — singletons
     * and contiguous ranges compile to a compare and never reach the pool. */
    {
        bool any = false;
        for (int i = 0; i < v.ncls; i++) {
            int lo = -1, hi = -1, count = 0;
            for (int cb = 0; cb < 256; cb++)
                if (cls_has(v.cls[i], (unsigned)cb)) {
                    if (lo < 0) lo = cb;
                    hi = cb;
                    count++;
                }
            if (count == 256 || count == 1 || count == hi - lo + 1) continue;
            any = true;
            sb_printf(c, "static const unsigned char %s_k%d[32] = {", v.p, i);
            for (int j = 0; j < 32; j++) {
                if (j % 8 == 0) sb_puts(c, "\n   ");
                sb_printf(c, " %3d,", v.cls[i][j]);
            }
            sb_puts(c, "\n};\n");
        }
        if (any) sb_puts(c, "\n");
    }

    /* ---- the prefilter (§6.1, §4.7) ------------------------------------ */
    const char *prefn = NULL;
    if (job->fit.prefilter) {
        size_t sz = strlen(v.p) + sizeof("_prefilter");
        char *pf = arena_alloc(&cx->arena, sz);
        snprintf(pf, sz, "%s_prefilter", v.p);
        prefn = pf;
        sb_puts(c,
            "/* The capture-erased forward+reverse DFA pair, emitted by the\n"
            " * SAME emitter the DFA-only artifact uses (src/gen/emit_dfa.c),\n"
            " * under a private name. It is not an over-approximation: D31\n"
            " * erases the group at parse time and A_CAP is invisible to the\n"
            " * NFA builder, so this IS the machine the capture-erased pattern\n"
            " * compiles to (engine_m4.md 6.1, STRUCTURAL). It hands the VM an\n"
            " * anchored window so the VM never scans the subject, which is not\n"
            " * an optimization but the guard on a measured cliff: bench case\n"
            " * (e) is 25.4 GB/s on pcrec today against pcre2-interp's DNF>90s,\n"
            " * and adding two parentheses must not move pcrec onto the DNF\n"
            " * side. Prefilter-before-VM is therefore an ORDERING RULE (4.7),\n"
            " * not a tuning knob: a pattern whose prefilter can answer must\n"
            " * never reach the step budget. */\n");
        pcrec_emit_dfa_engine(cx, prefn, "static ");
        sb_puts(c, "\n");
    }

    /* ---- rx_match_impl: the program ------------------------------------ */
    sb_printf(c,
        "static ptrdiff_t %s_match_impl(const rx_ctx *ctx, %s_work *w)\n"
        "{\n"
        "    const unsigned char *const s = ctx->subject;\n"
        "    const size_t n = ctx->len;\n"
        "    size_t pos = ctx->pos;\n"
        "    ptrdiff_t *const stv = w->stv;\n",
        v.p, v.p);
    if (v.used_cursor)
        sb_printf(c, "    size_t %s_cur = 0;   /* the span-loop cursor (engine_m4.md 2.5):\n"
                     "                             a plain local, UNTRAILED, whose save\n"
                     "                             point is a resume frame */\n",
                  v.p);
    sb_puts(c, "    (void)s; (void)n; (void)stv;\n");
    sb_printf(c, "    goto %s_L0;\n\n", v.p);
    sb_puts(c, v.b->p ? v.b->p : "");
    sb_printf(c,
        "\n%s_accept: __attribute__((unused));\n"
        "    /* 3.1: leftmost-first is FIRST COMPLETE MATCH WINS, not compare\n"
        "     * candidates. The VM returns here immediately and the capture\n"
        "     * slots at this instant are the answer — no candidate comparison,\n"
        "     * no longest-wins, no second pass. The caller's caps array is\n"
        "     * filled by the ENTRY, not here (3.4). */\n"
        "    return (ptrdiff_t)(pos - ctx->pos);\n"
        "\n%s_fail: __attribute__((unused));\n"
        "    /* THE ONLY BACKTRACKER AND THE ONLY INDIRECT JUMP.\n"
        "     * A step is one backtrack resumption (4.2), counted at exactly\n"
        "     * this place — so forward progress is FREE (a linear match over\n"
        "     * 100 MB costs zero steps), the budget is subject-length-\n"
        "     * independent, and the counter measures precisely the thing it is\n"
        "     * meant to bound. D22: DD-2 is ROBUSTNESS, not a security\n"
        "     * boundary, and it must not be traded against execution speed. */\n"
        "    if (w->btn == 0) return -1;\n",
        v.p, v.p);
    if (has_budget)
        sb_printf(c, "    if (--w->budget < 0) return %s_R_STEPS;\n", v.up);
    sb_puts(c,
        "    {\n"
        "        const unsigned b_ = --w->btn;\n"
        "        pos = w->bt[b_].pos;\n"
        "        while (w->trn > w->bt[b_].mark) {\n"
        "            w->trn--;\n"
        "            stv[w->tr[w->trn].slot] = w->tr[w->trn].v;\n"
        "        }\n"
        "        goto *w->bt[b_].k;\n"
        "    }\n"
        "}\n\n");

    sb_printf(c, "#undef %s_TRAIL\n#undef %s_SET\n#undef %s_PUSH\n\n",
              v.up, v.up, v.up);

    /* ---- the caps copy-out (§3.4) --------------------------------------
     * The VM's working slots are LOCAL and the ENTRY copies the capture region
     * out on a completed match — one linear copy of 2*ncaps ptrdiff_t on the
     * success path only. Aliasing the caller's array directly was considered
     * and rejected: stv also holds guards and low-water marks, so aliasing
     * would split the trail's slot space across two base pointers to save a
     * copy whose size is the GROUP COUNT, not the subject length.
     *
     * On a completed match EVERY pair is written (subst C6): slots untouched
     * during the match still hold UNSET from the initialisation. On a failed
     * match the caller's array is UNTOUCHED, because nothing was copied. */
    sb_printf(c,
        "static void %s_caps_out(const %s_work *w, ptrdiff_t (*caps)[2],\n"
        "                        size_t start, ptrdiff_t len)\n"
        "{\n"
        "    int k;\n"
        "    caps[0][0] = (ptrdiff_t)start;\n"
        "    caps[0][1] = (ptrdiff_t)start + len;\n"
        "    for (k = 1; k < %s_NCAPS; k++) {\n"
        "        caps[k][0] = w->stv[2 * k];\n"
        "        caps[k][1] = w->stv[2 * k + 1];\n"
        "    }\n"
        "}\n\n",
        v.p, v.p, v.up);

    /* ---- <prefix>_search (§2.6) ---------------------------------------- */
    sb_printf(c,
        "int %s(const unsigned char *s, size_t n, size_t startpos,\n"
        "       ptrdiff_t (*caps)[2])\n"
        "{\n"
        "    %s_work w;\n"
        "    rx_ctx ctx;\n"
        "    ptrdiff_t r;\n"
        "    size_t start;\n"
        "    if (startpos > n) return 0;\n",
        g.searchfn, v.p);

    if (prefn) {
        sb_printf(c,
            "    {\n"
            "        ptrdiff_t win[1][2];\n"
            "        if (%s(s, n, startpos, win) != 1) return 0;\n"
            "        start = (size_t)win[0][0];\n"
            "    }\n",
            prefn);
    } else {
        sb_puts(c, "    start = startpos;\n");
    }

    sb_printf(c,
        "    %s_work_init(&w);\n"
        "    ctx.subject = s; ctx.len = n; ctx.ncap = 0;\n"
        "    ctx.caps = NULL; ctx.user = NULL;\n"
        "    for (;;) {\n"
        "        ctx.pos = start;\n"
        "        r = %s_match_impl(&ctx, &w);\n"
        "        if (r == %s_R_STEPS)  return %s_ERR_STEPS;\n"
        "        if (r == %s_R_FRAMES) return %s_ERR_FRAMES;\n"
        "        if (r >= 0) break;\n"
        "        %s_unwind(&w);\n"
        "        if (start >= n) return 0;\n"
        "        start++;\n"
        "    }\n"
        "    if (caps) %s_caps_out(&w, caps, start, r);\n"
        "    return 1;\n"
        "}\n\n",
        v.p, v.p, v.up, v.up, v.up, v.up, v.p, v.p);

    /* ---- <prefix>_match / <prefix>_match_caps (§3, §3.1, §4.4) --------- */
    sb_printf(c,
        "/* F1's unconditional export, typed rx_matchfn. Budget exhaustion and\n"
        " * frame overflow both report -1 here — INDISTINGUISHABLE from no-match,\n"
        " * because D38.4 froze this return space (>= 0 length, -1 fail, < -1\n"
        " * RESERVED and __builtin_trap()-enforced at call sites) and D42.3 kept\n"
        " * that reservation intact rather than spending it on DD-2. The residual\n"
        " * is real and narrow and is recorded rather than hidden: a compiled\n"
        " * matcher used AS a callout cannot tell its caller it gave up. That is\n"
        " * confined to the composition path, which has no users in v1; re-open\n"
        " * when a composition customer appears (cheap pre-v1 per D40). The\n"
        " * honest codes live on %s, whose negative space D38 never\n"
        " * touched (4.4's three layers). */\n"
        "ptrdiff_t %s(const rx_ctx *ctx)\n"
        "{\n"
        "    %s_work w;\n"
        "    ptrdiff_t r;\n"
        "    if (ctx->pos > ctx->len) return -1;\n"
        "    %s_work_init(&w);\n"
        "    r = %s_match_impl(ctx, &w);\n"
        "    return r < 0 ? -1 : r;\n"
        "}\n\n",
        g.searchfn, g.matchfn, v.p, v.p, v.p);

    sb_printf(c,
        "ptrdiff_t %s(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2])\n"
        "{\n"
        "    %s_work w;\n"
        "    ptrdiff_t r;\n"
        "    if (ctx->pos > ctx->len) return -1;\n"
        "    %s_work_init(&w);\n"
        "    r = %s_match_impl(ctx, &w);\n"
        "    if (r < 0) return -1;\n"
        "    if (caps_out) %s_caps_out(&w, caps_out, ctx->pos, r);\n"
        "    return r;\n"
        "}\n\n",
        g.matchcapsfn, v.p, v.p, v.p, v.p);

    pcrec_emit_info(cx, &g, 2, job->fit.why,
                    has_budget ? budget : -1, bt_frames, ceiling);

    if (cx->opt->flags & PCREC_EMIT_MAIN)
        pcrec_emit_main(cx, &g);

}
