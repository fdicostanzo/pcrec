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

#include <stdarg.h>
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

/* ---- [M4.5c] the emitted-program LISTING (DD-8, engine_m4.md S10) --------
 *
 * S10's ONE constraint is load-bearing and it is the reason this is an EVENT
 * STREAM rather than a second walk over the AST: "the dump must be derived
 * from the same structure the emitter walks, never a parallel description — a
 * second source of truth for what the VM does is worse than no dump."
 *
 * So every event below is appended by the SAME call that writes the
 * corresponding C. `vm_lbl` writes a label and records one; `vm_push` writes an
 * RX_PUSH and records one; `vm_set` writes an RX_SET and records one. There is
 * no code path that can emit a label without recording it, because there is no
 * second way to emit a label.
 *
 * Every SECTION of the listing is then a VIEW over that one stream — the
 * program listing, the choice-point summary with its preference order, the
 * slot map, the island list and the callout list are all filters, so they
 * cannot disagree with each other either. Two sections drifting apart is the
 * same failure as the dump drifting from the emitter, one level down.
 *
 * The `role` strings are the only content that is not mechanically derived,
 * and they are decoration: they say WHY a choice point exists, never that one
 * does. The structural check (tests/codegen/run_ir_listing.sh) pins the
 * derivable half — label set, push count, slot set — against the emitted C. */
typedef enum {
    VE_LABEL,    /* a: label id                                    */
    VE_CLASS,    /* a: class pool id, b: next label                */
    VE_PUSH,     /* a: resume label id                             */
    VE_SET,      /* a: stv slot                                    */
    VE_GOTO,     /* a: target label id                             */
    VE_FAIL,
    VE_ACCEPT,
    VE_ASSERT,   /* text: the assertion's name                     */
    VE_NOTE,     /* text: an inline note on the current label      */
    VE_ISLAND,   /* reserved: no producer (engine_m4.md S6.3)      */
    VE_CALLOUT,  /* reserved: no producer (module 'callouts')      */
    VE_RUNG,     /* [D46] a: the A_REP's own entry label id,
                  *       b: VmRungKind ordinal                     */
    VE_STRAT,    /* [ENG-BREP] a: the A_REP's own entry label id,
                  *       b: VmStratKind ordinal                    */
    VE_CUT       /* [ENG-BREP] a: the cut-mark stv slot            */
} VEKind;

/* [D46] the S2.5 rung ladder's own small named value set, ONE PER
 * QUANTIFIER BODY (never per artifact — vm_cursor_fits is consulted once
 * per A_REP node, at this file's own three call sites, so two quantifiers
 * in one pattern can and do land on different rungs). Bit values, not
 * sequential ordinals, because the compile-time macro is a SUMMARY BITMASK
 * over however many distinct rungs one program's quantifiers actually use. */
typedef enum {
    VM_RUNG_CURSOR           = 0,  /* index into vm_rung_bit[], not a bit */
    VM_RUNG_FRAMES_BOUNDED   = 1,
    VM_RUNG_FRAMES_UNBOUNDED = 2,
    /* [ENG-BREP] engine_m4.md §2.5's REVERSE-DETERMINISTIC rung, between the
     * cursor and the frames: ONE body copy, a deterministic forward scan, one
     * resume frame for the whole loop, and a backward walk over the reversed
     * body for the retreat and for §3.4's last-iteration captures. */
    VM_RUNG_REVDET           = 3
} VmRungKind;
enum { VM_NRUNG = 4 };
static const unsigned vm_rung_bit[VM_NRUNG] = { 0x1u, 0x2u, 0x4u, 0x8u };
static const char    *const vm_rung_kindname[VM_NRUNG] =
    { "cursor", "frames-bounded", "frames-unbounded", "revdet" };

/* [ENG-BREP/D46] the LADDER's first rung as its own small named value set,
 * sitting BESIDE the rung rather than inside it: a possessified quantifier
 * still takes a rung (it is the rung's machinery that shrinks), so folding
 * possessification into VmRungKind would make the two facts compete for one
 * value. Same bitmask shape and same reason — the strategy is chosen PER
 * A_REP, so an artifact whose quantifiers differ needs a mask, not a scalar.
 *
 * The do-or-die half D47.3 moves to observability rides on this: under
 * `-fno-possessify` the POSSESSIVE bit must not appear in any artifact, and
 * tests/possessify/run_possessify_tests.sh asserts exactly that rather than
 * trusting the flag. */
typedef enum {
    VM_STRAT_POSSESSIVE   = 0,   /* index into vm_strat_bit[], not a bit */
    VM_STRAT_BACKTRACKING = 1
} VmStratKind;
static const unsigned vm_strat_bit[2] = { 0x1u, 0x2u };
static const char    *const vm_strat_kindname[2] =
    { "possessive", "backtracking" };

typedef struct {
    VEKind      k;
    int         a, b;
    const char *role;   /* arena-owned; NULL when there is nothing to say */
} VEvent;

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
    int       nlow_total; /* the count vm_count_slots found — vm_slot_mark's
                           * base, for vm_slot_low's own reason */
    int       nmark;      /* [ENG-BREP] possessive cut-mark slots so far */
    int       nmark_total;
    int       nrev;       /* [ENG-BREP] revdet LOOPS so far (3 slots each) */
    int       nrev_total;
    int       nrevcaps;   /* the largest capture-group count any one revdet
                           * body has — sizes the SHARED recovery locals. One
                           * array serves every revdet loop because a walk's
                           * results are PUBLISHED into stv before control
                           * leaves the loop, so nothing outlives its own
                           * commit. */
    int       nocap;      /* [ENG-BREP] >0 while emitting (or costing) a revdet
                           * loop's FORWARD body, where capture writes are
                           * SUPPRESSED: they are what would otherwise make the
                           * trail grow per iteration, and they are redundant,
                           * because §3.4's backward walk recovers every one of
                           * them from the committed span. A counter rather
                           * than a bool so a nested construct cannot clear a
                           * suppression it did not set. */
    long long npush;      /* [M4.5c fix] emitted RX_PUSH sites, counted in the
                           * pre-pass. Reported in the listing so a check can
                           * hold it against the artifact; not itself a cap. */
    long long maxcopies;  /* the largest REPLICATION FACTOR any one bounded
                           * repeat over a choice-bearing body demands. This is
                           * what PCREC_MAX_VM_REPEAT_COPIES bounds, and it is
                           * known before emission — which is the point. */
    long long nodes;      /* emitted-node budget, against PCREC_MAX_VM_NODES */
    unsigned  rungs;       /* [D46] BITMASK of VmRungKind values PRESENT in
                            * this program — the rung decision is PER
                            * QUANTIFIER BODY (vm_cursor_fits is consulted
                            * once per A_REP, emit_vm.c's own emission and
                            * slot-counting call sites), so a pattern with
                            * two quantified bodies can and does mix rungs;
                            * a SCALAR "the rung" would lie on that case.
                            * Set bit-by-bit, once per A_REP, by
                            * vm_rung_mark() — called from the same real
                            * emission sites that already label that A_REP's
                            * own entry (vm_cursor_rep / vm_rep's frames
                            * fallthrough), never re-derived from the AST.
                            * See vm_rung_mark() and the VE_RUNG listing
                            * section for the per-quantifier detail this
                            * mask summarizes. */
    unsigned  strats;      /* [ENG-BREP] the same shape one rung down the
                            * ladder: BITMASK of VmStratKind values present,
                            * set by the same vm_rung_mark() call that sets
                            * `rungs`, from the same `a->possessive` the
                            * emitter is about to act on. One call, one
                            * truth — the macro, the listing section and the
                            * emitted machinery cannot disagree about whether
                            * a quantifier was possessified, because there is
                            * one place that says so. */
    bool      tracing;    /* --trace: emit an instrumented artifact */
    /* class bitmap pool, deduplicated */
    uint8_t (*cls)[32];
    int       ncls, clscap;
    /* [M4.5c] the listing's event stream — see VEvent above */
    VEvent   *ev;
    int       nev, evcap;
} Vm;

static void vm_ev(Vm *v, VEKind k, int a, int b, const char *role)
{
    if (v->nev == v->evcap) {
        int ncap = v->evcap ? v->evcap * 2 : 256;
        VEvent *nv = arena_alloc(&v->cx->arena, (size_t)ncap * sizeof(VEvent));
        if (v->nev) memcpy(nv, v->ev, (size_t)v->nev * sizeof(VEvent));
        v->ev = nv;
        v->evcap = ncap;
    }
    v->ev[v->nev].k = k;
    v->ev[v->nev].a = a;
    v->ev[v->nev].b = b;
    v->ev[v->nev].role = role;
    v->nev++;
}

/* Arena-owned formatted text for a role string. */
static const char *vm_rolef(Vm *v, const char *fmt, ...)
    __attribute__((format(printf, 2, 3)));
static const char *vm_rolef(Vm *v, const char *fmt, ...)
{
    char buf[160];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof buf, fmt, ap);
    va_end(ap);
    if (n < 0) return NULL;
    size_t sz = (size_t)n + 1;
    if (sz > sizeof buf) sz = sizeof buf;
    char *q = arena_alloc(&v->cx->arena, sz);
    memcpy(q, buf, sz - 1);
    q[sz - 1] = 0;
    return q;
}

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
/* [ENG-BREP] the fourth slot class: a possessified frames-rung loop's CUT
 * MARK, the resume-stack depth to truncate back to. It sits above the low-water
 * marks, so like them its base is computed from the TOTALS the pre-pass found
 * and never from a running counter. */
static int vm_slot_mark(Vm *v, int i)
{
    return 2 * (v->ngroups + 1) + v->nguard_total + v->nlow_total + i;
}
/* [ENG-BREP] the fifth slot class: THREE per reverse-deterministic loop, and
 * three whatever the preference or the verdict.
 *
 *   +0  `entry` — the loop's start position. The capture walk's FLOOR.
 *   +1  `low`   — the boundary after `rmin` iterations. The retreat's FLOOR.
 *   +2  `hi`    — the maximal boundary the forward scan reached. The lazy
 *                 extension's CEILING, which is what lets a lazy loop enforce
 *                 its `{m,n}` cap POSITIONALLY instead of with a per-extension
 *                 trailed counter.
 *
 * A uniform three even where a given shape reads only two: the count has to
 * agree across vm_count_slots, vm_cost_rep and the emitter, and a
 * per-preference rule would put that agreement in three places instead of one.
 * All three are written ONCE per loop ENTRY, never per iteration, which is the
 * property this whole rung exists for. */
static int vm_slot_rev(Vm *v, int loop, int which)
{
    return 2 * (v->ngroups + 1) + v->nguard_total + v->nlow_total
         + v->nmark_total + 3 * loop + which;
}

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
    /* A_CAT and A_ALT spines are walked ITERATIVELY, not recursed on. That is
     * R1's R-2 hardening and D10/DD-10's rule, and this function violated it
     * until a 20,000-character literal SEGFAULTED pcrec at the default 8 MB
     * stack (`(aaa...)`, no special flag — measured, and the threshold tracks
     * `ulimit -s`, which is what identifies it as stack exhaustion rather than
     * anything subtler). src/ir/nfa.c's compile_ast flattens for exactly this
     * reason and says so; three functions in this file did not, and this is
     * one of them. The recursion that REMAINS is on a spine node's RIGHT
     * child, whose own depth is bounded by the parser's group-nesting cap. */
    for (;;) {
        switch (a->k) {
        case A_CLASS: return false;
        case A_EMPTY: case A_BOL: case A_EOL: return true;
        case A_CAP:   a = a->l; continue;
        case A_REP:   if (a->rmin == 0) return true; a = a->l; continue;
        case A_CAT:
            /* nullable iff EVERY element is */
            while (a->k == A_CAT) {
                if (!vm_nullable(a->r)) return false;
                a = a->l;
            }
            continue;
        case A_ALT:
            /* nullable iff ANY branch is */
            while (a->k == A_ALT) {
                if (vm_nullable(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        return true;
    }
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

/* ---- §2.5's REVERSE-DETERMINISTIC rung: the two facts every site needs ----
 *
 * The VERDICT itself is not computed here: src/opt/revdet.c decides it and
 * leaves the body's REVERSED AST on `Ast.revbody`, non-NULL exactly when the
 * rung applies. That is deliberate — the rung has three call sites that must
 * agree (the slot counter, the capacity analysis and the emitter) and the
 * cursor rung's own history is that a condition read three times is a condition
 * that can drift. One field, read three times, cannot.
 *
 * These two helpers are the DERIVED facts the three sites still share.
 *
 * `vm_rev_canmove`: whether the loop owes a resume frame at all. It does not
 * when it is possessified (no retreat is reachable, by §2.2's verdict) and it
 * does not at an EXACT count (there is one exit, so top and bottom of §2.3's
 * chain are the same position). Both cases still run the backward walk when the
 * body has groups, because the captures still have to be derived. */
static bool vm_rev_canmove(const Ast *a)
{
    return !a->possessive && (a->rmax < 0 || a->rmax > a->rmin);
}

/* `vm_rev_caps`: the body's capturing group NUMBERS, in AST order, which is the
 * dense index the emitted recovery locals are addressed by. One number per
 * A_CAP node and not per emitted instance — a fixed-count repeat around a group
 * emits it several times and they all share one number and one pair of slots
 * (revdet.c's shape scan counts the same way, which is what keeps its
 * PCREC_MAX_REVDET_BODY_GROUPS bound meaning the same thing this array's size
 * means). */
static void vm_rev_caps(const Ast *a, int *out, int *n, int cap)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL:
            return;
        case A_CAP:
            if (*n < cap) out[(*n)++] = a->capno;
            a = a->l;
            continue;
        case A_REP:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) { vm_rev_caps(a->r, out, n, cap); a = a->l; }
            continue;
        case A_ALT:
            while (a->k == A_ALT) { vm_rev_caps(a->r, out, n, cap); a = a->l; }
            continue;
        }
        return;
    }
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

    if (a->rmin == 0 && a->rmax == 0) return c;

    /* [ENG-BREP] The REVERSE-DETERMINISTIC arm is taken BEFORE the body's cost
     * is computed, because on this rung the body is costed with capture writes
     * SUPPRESSED and that changes the number. The ladder order is the emitter's
     * (vm_rep): cursor first, then this, then frames.
     *
     * THE HEADLINE IS `pf = 0`. Frames do not grow with the iteration count —
     * the scan cuts the body's choice points at every iteration boundary and
     * the whole loop owes ONE resume frame — so an artifact whose only growing
     * quantifier is on this rung declares no subject ceiling at all, where the
     * frames rung declared one per iteration.
     *
     * The TRAIL still can grow, and saying so is the honest half (the same
     * honesty the possessive arm below already carries). Suppressed captures
     * cost nothing per iteration, so a body like `((a)|b)` grows nothing; a
     * body containing a nested quantifier that owns slots of its own still
     * writes them once per iteration, and that case earns a real ceiling from a
     * real per-iteration divisor. */
    if (!vm_cursor_fits(a, seq, &stride, caps, &nc) && a->revbody) {
        const bool move = vm_rev_canmove(a);
        int grp[PCREC_MAX_REVDET_BODY_GROUPS];
        int ng = 0;
        Cost body;
        vm_rev_caps(a->l, grp, &ng, PCREC_MAX_REVDET_BODY_GROUPS);
        v->nocap++;
        body = vm_cost(v, a->l);
        v->nocap--;
        c.frames = 1 + body.frames + (move ? 1 : 0);
        c.pf     = 0;
        /* THE TRAIL ACCUMULATES ACROSS ITERATIONS AND THE FRAMES DO NOT, and
         * the asymmetry is the cut's doing: the scan discards the body's frames
         * at every boundary and deliberately does NOT rewind its trail (the
         * same rule vm_cut carries, for the same reason — a failure OUTSIDE the
         * loop still has to restore what the loop wrote). So a body that owns
         * any trailed slot of its own pays for it once per ITERATION.
         *
         * Counting one iteration's worth here was this arm's first version and
         * it is a SILENT CAP, which is the one failure mode this analysis
         * exists to prevent. MEASURED: `(?:x((a)|b){2}y){0,3}z`'s body contains
         * a possessified exact-count repeat, whose cut mark is one trailed
         * write per entry, so three outer iterations need three of them — and
         * the artifact stamped a capacity for one and returned RX_ERR_FRAMES on
         * "xabyxabyxaayz", a subject it should answer. Caught by this rung's
         * own .rxt corpus on the run that added the nested-repeat family.
         *
         * Capture writes inside the body are SUPPRESSED on this rung, so the
         * common case has `periter == 0` and nothing accumulates at all — which
         * is why the defect needed a body with a nested quantifier owning a
         * slot to show up. */
        {
            const long long periter = body.trail + body.pt;
            const long long base = 3 + 2 * (long long)ng;
            c.pt = periter;
            if (a->rmax >= 0) {
                c.trail = base + (long long)a->rmax * periter;
                c.unbounded = body.unbounded;
            } else {
                /* No static iteration bound, so no exact requirement exists
                 * when the body writes anything: the ceiling machinery takes
                 * over from `pt`. */
                c.trail = base + periter;
                c.unbounded = body.unbounded || periter > 0;
            }
            c.growable = body.growable || c.unbounded || periter > 0;
        }
        return c;
    }

    Cost body = vm_cost(v, a->l);

    if (vm_cursor_fits(a, seq, &stride, caps, &nc)) {
        /* cursor rung: ONE live frame ever, one low-water write per entry,
         * plus one write per capture in the body per (re)try — all of which
         * the resume frame's own mark rewinds, so they do not accumulate.
         *
         * [ENG-BREP] Possessified, the frame and the low-water write are both
         * gone (vm_cursor_rep's possessive path emits neither), so the honest
         * requirement is zero frames and the capture writes alone. This is
         * where §7's "those artifacts newly stamp no limit truthfully" comes
         * from: an artifact whose every quantifier is possessified reports a
         * frame requirement of 0, and pcrec_emit_vm's `fits` test then finds
         * nothing to declare a ceiling for. Under-reporting here would be a
         * silent cap, so the branch has to mirror the emitter exactly. */
        c.frames = a->possessive ? 0 : 1;
        c.trail  = (a->possessive ? 0 : 1) + (v->nocap ? 0 : 2 * nc);
        return c;
    }

    /* [ENG-BREP] the possessified frames rung, both bounds in one arm because
     * the whole point is that the two now cost the same: ONE loop frame is
     * live at a time (vm_poss_chain / vm_poss_star cut back to the mark at
     * every copy boundary), so the frame requirement stops depending on the
     * iteration count entirely.
     *
     * The TRAIL still does depend on it, and saying so is the honest half. The
     * cut discards frames and deliberately does not rewind the trail, so a
     * body that writes captures still adds entries per iteration. That is why
     * `growable` is decided on the trail here rather than assumed false: for a
     * capture-free body nothing grows and the artifact stamps "no limit"
     * truthfully (§7's prediction), while for a capture-bearing one the
     * ceiling machinery still has a real per-iteration divisor to work from —
     * just no longer a frames one. */
    if (a->possessive) {
        long long peak_mandatory = (long long)a->rmin * body.frames;
        long long peak_loop      = 1 + body.frames;
        c.frames = peak_mandatory > peak_loop ? peak_mandatory : peak_loop;
        c.trail  = 1 + (a->rmax < 0 ? (long long)a->rmin
                                    : (long long)a->rmax) * body.trail;
        c.pf     = body.pf;                    /* frames: NOT per iteration */
        c.pt     = body.trail + body.pt;       /* trail: still per iteration */
        {
            bool grows = body.unbounded || body.growable || c.pt > 0;
            c.unbounded = a->rmax < 0 ? grows : body.unbounded;
            c.growable  = a->rmax < 0 ? grows : (body.growable || c.pt > 0);
        }
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
        /* [ENG-BREP] no trail entry while capture writes are suppressed —
         * vm_emit's own A_CAP arm reads the same flag, so the cost and the
         * emitted code cannot disagree about whether the write happens. */
        if (!v->nocap) c.trail += 2;
        return c;
    case A_CAT: {
        /* Spine walked ITERATIVELY (R1 R-2 / D10) — see vm_nullable's comment
         * for the segfault that says why. The accumulation order reproduces
         * the recursive definition exactly: A_CAT sums both sides, so summing
         * along the spine is the same number. */
        const Ast *t = a;
        while (t->k == A_CAT) {
            Cost r = vm_cost(v, t->r);
            c.frames += r.frames;
            c.trail  += r.trail;
            c.pf     += r.pf;
            c.pt     += r.pt;
            c.unbounded = c.unbounded || r.unbounded;
            c.growable  = c.growable  || r.growable;
            t = t->l;
        }
        {
            Cost h = vm_cost(v, t);
            c.frames += h.frames;
            c.trail  += h.trail;
            c.pf     += h.pf;
            c.pt     += h.pt;
            c.unbounded = c.unbounded || h.unbounded;
            c.growable  = c.growable  || h.growable;
        }
        return c;
    }
    case A_ALT: {
        /* The chain shape keeps exactly ONE alternation frame live at a time
         * (see vm_alt), and a failed branch's own frames are popped before the
         * next branch runs — so this is max-plus-one, not a sum.
         *
         * Iterative, and the fold is INNERMOST-FIRST because that is the shape
         * the recursion had: a flat alternation is a LEFT-NESTED chain, so
         * `1 + max` applied at each node accumulates outward. Folding in any
         * other order would silently change the number this function reports,
         * which is what sizes the frame array. */
        int nbr = 1;
        for (const Ast *t = a; t->k == A_ALT; t = t->l) nbr++;
        const Ast **br = arena_alloc(&v->cx->arena, (size_t)nbr * sizeof(Ast *));
        int i = nbr;
        const Ast *t = a;
        while (t->k == A_ALT) { br[--i] = t->r; t = t->l; }
        br[0] = t;

        c = vm_cost(v, br[0]);
        for (int j = 1; j < nbr; j++) {
            Cost r = vm_cost(v, br[j]);
            c.frames = 1 + (c.frames > r.frames ? c.frames : r.frames);
            c.trail  = c.trail > r.trail ? c.trail : r.trail;
            c.pf     = c.pf > r.pf ? c.pf : r.pf;
            c.pt     = c.pt > r.pt ? c.pt : r.pt;
            c.unbounded = c.unbounded || r.unbounded;
            c.growable  = c.growable  || r.growable;
        }
        return c;
    }
    case A_REP:
        return vm_cost_rep(v, a);
    }
    return c;
}

/* ---- slot counting (must mirror the emitter's own rung decisions) --------*/

/* Counts stv slots AND emitted resume points, in one walk that mirrors the
 * emitter's own rung decisions and its replication. Both counts have to be
 * exact for the same reason: a slot count that under-counts makes two live
 * loops share one slot, and a resume-point count that under-counts lets an
 * artifact past the cap that the cap exists to stop. The push arithmetic
 * matches the emitter site for site — vm_alt pushes nbr-1 for an nbr-branch
 * alternation (which is one per A_ALT node, since a flat alternation is
 * left-nested), vm_cursor_rep pushes 1, the unbounded star pushes 1, and
 * vm_opt_chain pushes one per optional copy. Verified against the emitted
 * `&&label` count over the corpus.
 *
 * [K22] `repl` is the PRODUCT of the replication factors of every frames-rung
 * bounded repeat this call is nested inside — 1 at the root. It exists because
 * this walk is the one place in the compiler that pays the copy tree's full
 * cost before anything bounds it: `PCREC_MAX_VM_REPEAT_COPIES` bounds one
 * quantifier's own factor (a `{0,2}` tower never comes near it) and
 * `PCREC_MAX_VM_NODES` is charged during EMISSION, which this pre-pass runs
 * before. So a depth-40 `{0,2}` tower walked 2^40 nodes here and hung the
 * compiler with no diagnostic. Multiplying the factors down the nesting path
 * and refusing above PCREC_MAX_VM_REPLICATION_PRODUCT costs one multiply per
 * A_REP and turns the hang into the refusal the node cap was always going to
 * produce; see limits.h for why the two share a value and why that makes the
 * check unable to refuse anything that compiles today. */
static void vm_count_slots(Vm *v, const Ast *a, long long repl)
{
    const uint8_t *seq[VM_MAX_STRIDE];
    CapOff caps[VM_MAX_BODY_CAPS];
    int stride = 0, nc = 0;
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL:
        return;
    case A_CAP: vm_count_slots(v, a->l, repl); return;
    case A_ALT:
        /* Iterative spine walk (R1 R-2 / D10) — see vm_nullable. One push per
         * A_ALT NODE, which for a left-nested flat alternation of k branches
         * is k-1, exactly what vm_alt emits. */
        while (a->k == A_ALT) {
            v->npush++;
            vm_count_slots(v, a->r, repl);
            a = a->l;
        }
        vm_count_slots(v, a, repl);
        return;
    case A_CAT:
        while (a->k == A_CAT) { vm_count_slots(v, a->r, repl); a = a->l; }
        vm_count_slots(v, a, repl);
        return;
    case A_REP:
        if (a->rmin == 0 && a->rmax == 0) return;
        if (vm_cursor_fits(a, seq, &stride, caps, &nc)) {
            /* [ENG-BREP] the possessive span loop allocates NEITHER — no
             * low-water slot and no resume point. Mirrors vm_cursor_rep's own
             * branch; the two are the same condition read twice, which is the
             * standing hazard this function's header comment is about. */
            if (!a->possessive) {
                v->nlow++;
                v->npush++;              /* vm_cursor_rep: exactly one */
            }
            return;
        }
        /* [ENG-BREP] the REVERSE-DETERMINISTIC rung. Three slots, one loop, and
         * NO REPLICATION — which is the whole point, and is also why this arm
         * returns before the `maxcopies` line below ever sees the quantifier:
         * `((a)|b){0,4000}c` demands one body copy here where the frames rung
         * demanded four thousand.
         *
         * The push arithmetic, site for site with vm_revdet_rep:
         *   1  the scan's exit frame (this iteration cannot run -> leave)
         *   1  the retreat/extension frame, only when the loop can move
         * and NOTHING for the backward walk, which is emitted as a
         * DETERMINISTIC matcher with no choice point at all — reverse
         * one-unambiguity is exactly the licence to dispatch on the next byte
         * instead of pushing a frame per branch.
         *
         * The forward body is walked ONCE, or twice for a lazy loop that can
         * move, because that shape emits a second forward copy for its
         * extension step. The REVERSED body allocates no slots and pushes
         * nothing, so it is not walked here at all. */
        if (a->revbody) {
            int grp[PCREC_MAX_REVDET_BODY_GROUPS];
            int ng = 0;
            bool move = vm_rev_canmove(a);
            vm_rev_caps(a->l, grp, &ng, PCREC_MAX_REVDET_BODY_GROUPS);
            if (ng > v->nrevcaps) v->nrevcaps = ng;
            v->nrev++;
            v->npush += 1 + (move ? 1 : 0);
            vm_count_slots(v, a->l, repl);
            if (move && !a->greedy) vm_count_slots(v, a->l, repl);
            return;
        }
        /* frames rung: the star's own push, or one per optional copy. The
         * possessive shapes push at the SAME sites (vm_poss_star once,
         * vm_poss_chain once per optional copy) — what changes is how many are
         * live at a time, not how many are emitted — so this arithmetic is
         * unchanged. The cut mark is the one new slot. */
        v->npush += a->rmax < 0 ? 1 : (a->rmax - a->rmin);
        if (a->possessive) v->nmark++;
        /* Frames rung: the body's code is REPLICATED once per mandatory copy
         * and once per optional copy, and each copy's own loops need their own
         * slots — so the count must replicate exactly as the emitter does or
         * two live loops would share one slot. */
        {
            int copies = a->rmax < 0 ? a->rmin + 1 : a->rmax;
            if (copies < 1) copies = 1;
            /* THE REPLICATION FACTOR, recorded before any of it is emitted.
             * Only the frames rung reaches here: a body the cursor rung
             * accepts is single-path and compiles to a span loop whatever the
             * count, so `a{0,65535}` never contributes. */
            if (copies > v->maxcopies) v->maxcopies = copies;
            /* [K22] and the factor's PRODUCT down the nesting path, checked
             * BEFORE the loop below walks it. `v->maxcopies` above is a MAX and
             * structurally cannot see this: nesting multiplies factors that are
             * individually far under PCREC_MAX_VM_REPEAT_COPIES. The check is
             * placed here rather than after the walk for the only reason it
             * exists — the walk is the cost. Overflow is not reachable: the
             * running product is refused the moment it exceeds the limit, so it
             * never carries more than limit * PCREC_MAX_REPEAT. */
            {
                long long total = repl * copies;
                if (total > PCREC_MAX_VM_REPLICATION_PRODUCT)
                    ctx_fail(v->cx, 0,
                             "pattern too large: nested bounded repeats would "
                             "replicate a body %lld times in total (limit %d). "
                             "Repetition counts MULTIPLY through nesting, so "
                             "depth costs far more than any one count suggests "
                             "-- lower a count, or reduce the nesting",
                             total, PCREC_MAX_VM_REPLICATION_PRODUCT);
                for (int i = 0; i < copies; i++)
                    vm_count_slots(v, a->l, total);
            }
            if (a->rmax < 0 && vm_nullable(a->l)) v->nguard++;
        }
        return;
    }
}

/* ---- emission -----------------------------------------------------------*/

static void vm_emit(Vm *v, int entry, const Ast *a, int next);

/* THE FIVE PRIMITIVES. Every one of them writes C *and* records the listing
 * event for what it just wrote — one call, one truth (engine_m4.md S10). A
 * label that does not appear in the listing is not a listing bug, it is an
 * impossibility: there is no other way to emit a label. */

static void vm_lbl(Vm *v, int id, const char *role)
{
    /* The `__attribute__((unused))` follows emit_attempt's precedent: a label
     * that is only ever reached through a resume frame's `&&` address, or one
     * the flattening below makes unreachable, must not fail the harness's
     * -Werror generated-code build. */
    sb_printf(v->b, "%s_L%d: __attribute__((unused));\n", v->p, id);
    vm_ev(v, VE_LABEL, id, 0, role);
}

static void vm_goto(Vm *v, int id)
{
    sb_printf(v->b, "    goto %s_L%d;\n", v->p, id);
    vm_ev(v, VE_GOTO, id, 0, NULL);
}

static void vm_fail(Vm *v)
{
    sb_printf(v->b, "    goto %s_fail;\n", v->p);
    vm_ev(v, VE_FAIL, 0, 0, NULL);
}

/* `posexpr` is what the frame records as its resume position — `pos` for every
 * ordinary choice point, and the span-loop cursor for S2.5's rung, which is
 * the one site that resumes somewhere other than the current position. Under
 * --trace the macro takes the label id too, so the instrumented artifact can
 * name the frame it is pushing; that extra argument is the ONLY difference
 * --trace makes to this line, and it makes none at all without it. */
static void vm_push_at(Vm *v, int lblid, const char *posexpr, const char *role)
{
    if (v->tracing)
        sb_printf(v->b, "    %s_PUSH(%d, &&%s_L%d, %s);\n",
                  v->up, lblid, v->p, lblid, posexpr);
    else
        sb_printf(v->b, "    %s_PUSH(&&%s_L%d, %s);\n",
                  v->up, v->p, lblid, posexpr);
    vm_ev(v, VE_PUSH, lblid, 0, role);
}

static void vm_push(Vm *v, int lblid, const char *role)
{
    vm_push_at(v, lblid, "pos", role);
}

static void vm_set(Vm *v, int slot, const char *val, const char *role)
{
    sb_printf(v->b, "    %s_SET(%d, %s);\n", v->up, slot, val);
    vm_ev(v, VE_SET, slot, 0, role);
}

/* [ENG-BREP] THE CUT — the possessive loop's one new operation, and a
 * primitive rather than an inline sb_printf for the same "one call, one truth"
 * reason as the five above.
 *
 * It truncates the resume stack back to the depth recorded in `slot`,
 * discarding every frame the loop and its body pushed since. That is exactly
 * what a positive §2.2 verdict licenses: no retreat into this loop can produce
 * a match the preferred path does not, so those frames are provably dead.
 *
 * IT DOES NOT TOUCH THE TRAIL, and must not. The frames are dead; the capture
 * writes they would have rewound are NOT, because a failure OUTSIDE the loop
 * still has to restore the loop's groups to their pre-loop values. A frame
 * below the cut carries a trail mark from before the loop ran, so unwinding to
 * it still rewinds everything the loop wrote — which is why discarding frames
 * without rewinding the trail is safe rather than merely convenient. */
static void vm_cut(Vm *v, int slot, const char *role)
{
    sb_printf(v->b, "    %s_CUT(%d);\n", v->up, slot);
    vm_ev(v, VE_CUT, slot, 0, role);
}

/* [D46] the SIXTH primitive: writes no C (the rung was already selected by
 * the C written around this call), but records the SAME "one call, one
 * truth" way every other primitive does — sets the artifact-wide summary
 * bit AND appends the per-quantifier VE_RUNG event in one place, so the
 * bitmask macro and the RUNGS listing section can never drift apart. Called
 * once per A_REP, at the point vm_cursor_rep / vm_rep's frames fallthrough
 * already knows which rung THIS quantifier took — never a second pass over
 * the AST re-deciding it (that would risk drifting from vm_cursor_fits's
 * three real call sites, exactly what the 0b4b0be fix consolidated away). */
static void vm_rung_mark(Vm *v, int lblid, VmRungKind k, bool possessive,
                         const char *role)
{
    VmStratKind s = possessive ? VM_STRAT_POSSESSIVE : VM_STRAT_BACKTRACKING;
    v->rungs  |= vm_rung_bit[k];
    v->strats |= vm_strat_bit[s];
    vm_ev(v, VE_RUNG,  lblid, (int)k, role);
    vm_ev(v, VE_STRAT, lblid, (int)s, role);
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
        vm_lbl(v, resume[j], j == 0
               ? vm_rolef(v, "alternation entry (%d branches)", nbr)
               : vm_rolef(v, "alternation resume: try branch %d of %d",
                          j + 1, nbr));
        if (j + 1 < nbr)
            vm_push(v, resume[j + 1],
                    vm_rolef(v, "branch %d of %d preferred; resume tries "
                                "branch %d", j + 1, nbr, j + 2));
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
    /* [ENG-BREP] A POSSESSIFIED span loop owes NOTHING but the scan: no resume
     * frame, no low-water slot and no trail entry of its own.
     *
     * The low-water slot exists so the RETREAT can tell "still above rmin"
     * from "exhausted", and it has to be a trailed slot rather than a local
     * because the frame that resumes the retreat may be popped long after the
     * loop was left. With no retreat there is no such reader — and `pos` is
     * still the loop's entry position at every point below, because the scan
     * writes only `<p>_cur` and `pos` is not assigned until the loop commits.
     * So the possessive path reads `pos` where the backtracking one reads
     * `stv[low]`, allocates no slot, and writes no trail entry. vm_cost_rep
     * and vm_count_slots carry the same branch; all three must agree or two
     * live loops share one slot. */
    const bool poss = a->possessive;
    /* [ENG-BREP] a cursor loop NESTED in a revdet loop's forward scan writes no
     * captures either (v->nocap): the enclosing rung's backward walk recovers
     * this body's groups along with every other group in it, and a per-iteration
     * write here would reintroduce the trail growth the enclosing rung removed.
     * vm_cost_rep's cursor arm reads the same flag for the same number. */
    if (v->nocap) ncaps = 0;
    int low = poss ? -1 : vm_slot_low(v, v->nlow++);
    int retry = poss ? -1 : vm_label(v), again = poss ? -1 : vm_label(v);
    long long lo_off = (long long)a->rmin * stride;
    /* The loop's entry position, spelled for whichever of the two it is. */
    char entrypos[32];
    if (poss) snprintf(entrypos, sizeof entrypos, "(ptrdiff_t)pos");
    else      snprintf(entrypos, sizeof entrypos, "stv[%d]", low);

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

    char bounds[32];
    if (a->rmax < 0) snprintf(bounds, sizeof bounds, "{%d,}", a->rmin);
    else             snprintf(bounds, sizeof bounds, "{%d,%d}", a->rmin, a->rmax);
    /* The PREFERENCE disappears when the quantifier is possessified, and that
     * is the analysis's conclusion rather than a shortcut. On the exact-count
     * arm there is one exit, so top and bottom of §2.3's chain are the same
     * position. On the disjointness arm a greedy loop tops out by preference,
     * and a LAZY one is FORCED to the same top: at any non-maximal exit the
     * body could iterate again, so that byte is in FIRST(X), so by
     * disjointness the follow cannot begin there — and the lazy conjunct
     * (non-nullable remainder) is what rules out the match simply ENDING
     * there instead. Both preferences therefore land on the maximal exit,
     * which is what makes one emitted shape correct for both. */
    const char *rung = vm_rolef(v, "span-loop cursor %s, stride %d, %s%s",
                                bounds, stride,
                                a->greedy ? "greedy" : "lazy",
                                poss ? ", POSSESSIFIED (no frame, no giveback)"
                                     : "");
    vm_lbl(v, entry, rung);
    /* [D46] this A_REP's own rung, reusing the SAME role text vm_lbl just
     * wrote — one description, two views (the PROGRAM section's label line
     * and the RUNGS section's per-quantifier entry), not two computations
     * of "what is this quantifier doing" that could disagree. */
    vm_rung_mark(v, entry, VM_RUNG_CURSOR, poss, rung);
    /* The loop's ENTRY position, trailed. Both rungs derive their bounds from
     * it: low-water is entry + stride*rmin, ceiling is entry + stride*rmax.
     * The possessive path reads `pos` for the same quantity and writes no
     * slot at all — see the note at the top of this function. */
    if (!poss)
        vm_set(v, low, "(ptrdiff_t)pos",
               "span-loop low-water mark (loop entry pos)");

    if (poss) {
        /* The scan, and then the commit. One straight line: consume to the
         * furthest position the bound allows, refuse if that is short of
         * rmin, publish the groups, take the continuation. Nothing here can
         * be resumed, which is the whole point — the emitted C contains no
         * label the loop could come back to. */
        sb_puts(b, "    {\n");
        if (a->rmax >= 0) sb_puts(b, "        unsigned long it_ = 0;\n");
        sb_printf(b, "        %s_cur = pos;\n", v->p);
        sb_printf(b, "        while (%s_cur + %d <= n", v->p, stride);
        if (a->rmax >= 0) sb_printf(b, " && it_ < %dUL", a->rmax);
        sb_printf(b, "%s) { %s_cur += %d;", test, v->p, stride);
        if (a->rmax >= 0) sb_puts(b, " it_++;");
        sb_puts(b, " }\n    }\n");
        sb_printf(b, "    if ((ptrdiff_t)%s_cur < %s + %lld) goto %s_fail;\n",
                  v->p, entrypos, lo_off, v->p);
        vm_ev(v, VE_NOTE, 0, 0,
              "fewer than rmin iterations: the loop cannot be satisfied");
        if (ncaps) {
            sb_printf(b, "    if ((ptrdiff_t)%s_cur >= %s + %d) {\n",
                      v->p, entrypos, stride);
            for (int i = 0; i < ncaps; i++) {
                char val[96];
                snprintf(val, sizeof val, "(ptrdiff_t)(%s_cur - %d)", v->p,
                         stride - caps[i].off);
                vm_set(v, 2 * caps[i].group, val,
                       vm_rolef(v, "group %d open, derived from the cursor",
                                caps[i].group));
                snprintf(val, sizeof val, "(ptrdiff_t)(%s_cur - %d)", v->p,
                         stride - caps[i].off - caps[i].len);
                vm_set(v, 2 * caps[i].group + 1, val,
                       vm_rolef(v, "group %d close, derived from the cursor",
                                caps[i].group));
            }
            sb_puts(b, "    }\n");
        }
        sb_printf(b, "    pos = %s_cur;\n", v->p);
        vm_goto(v, next);
        sb_free(&t);
        return;
    }

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

        vm_lbl(v, retry, "span-loop: take the continuation at the cursor");
        sb_printf(b, "    if ((ptrdiff_t)%s_cur < stv[%d] + %lld) goto %s_fail;\n",
                  v->p, low, lo_off, v->p);
        vm_ev(v, VE_NOTE, 0, 0, "below the low-water mark: exhausted");
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

        vm_lbl(v, retry, "span-loop: take the continuation at the cursor");
    }

    {
        char cur[64];
        snprintf(cur, sizeof cur, "%s_cur", v->p);
        vm_push_at(v, again, cur, a->greedy
                   ? "shorter run is the resume (retreat one stride)"
                   : "longer run is the resume (extend one stride)");
    }
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
            vm_set(v, 2 * caps[i].group, val,
                   vm_rolef(v, "group %d open, derived from the cursor "
                               "(D44.1: not written per iteration)",
                            caps[i].group));
            snprintf(val, sizeof val, "(ptrdiff_t)(%s_cur - %d)", v->p,
                     stride - caps[i].off - caps[i].len);
            vm_set(v, 2 * caps[i].group + 1, val,
                   vm_rolef(v, "group %d close, derived from the cursor",
                            caps[i].group));
        }
        sb_puts(b, "    }\n");
    }
    sb_printf(b, "    pos = %s_cur;\n", v->p);
    vm_goto(v, next);

    vm_lbl(v, again, a->greedy ? "span-loop retreat (resumed from the frame)"
                               : "span-loop extend (resumed from the frame)");
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
        vm_lbl(v, entry, "bounded repeat: all optional copies exhausted");
        vm_goto(v, next);
        return;
    }
    int bentry = vm_label(v), other = vm_label(v), inner = vm_label(v);
    vm_lbl(v, entry, vm_rolef(v, "optional copy (%d remaining), %s",
                              count, greedy ? "greedy" : "lazy"));
    if (greedy) {
        vm_push(v, other, "body preferred; resume SKIPS this copy");
        vm_goto(v, bentry);
    } else {
        vm_push(v, other, "skip preferred; resume TAKES this copy");
        vm_goto(v, next);
    }
    vm_lbl(v, other, greedy ? "optional copy: the skip"
                            : "optional copy: the body");
    vm_goto(v, greedy ? next : bentry);
    vm_emit(v, bentry, body, inner);
    vm_opt_chain(v, inner, body, count - 1, next, greedy);
}

/* [ENG-BREP] The possessified frames rung, bounded: `X{m,n}` after its `m`
 * mandatory copies, with `count` optional copies left to run.
 *
 * The shape, and why it is not simply vm_opt_chain minus the pushes. In this
 * VM a frame serves TWO purposes at an optional copy — resume when the
 * CONTINUATION fails (retreat into the loop), and resume when the BODY fails
 * (this copy cannot run, so exit the loop). Possessification kills the first
 * and leaves the second completely alive: `(?:a|bc){0,4}d` still has to notice
 * that neither branch matches and leave the loop. Deleting the push would
 * break that, which is why this is a different emission rather than a smaller
 * one.
 *
 * So exactly ONE loop frame is live at a time, whatever the count:
 *
 *     Lj:  CUT(mark)          <- the previous copy is committed; its frames,
 *                                and its body's, are dead by the verdict
 *          PUSH(exit, pos)    <- the only loop frame: if this copy's body
 *                                fails, resume here with pos back at the
 *                                start of the copy that failed
 *          <body>  -> L(j+1)
 *     L(count+1): CUT(mark); goto next     <- every copy taken
 *     exit:       goto next                <- the pop already restored pos,
 *                                             and left btn exactly at mark
 *
 * The body's OWN frames are not disturbed while it runs, which matters: a
 * one-unambiguous body still needs them to FIND its match (`(?:a|bc)` on "bc"
 * tries `a` first and backtracks). One-unambiguity says at most one branch can
 * SUCCEED, not that the emitter guesses right — so the cut is at the copy
 * boundary, where the previous body has already succeeded, and never inside
 * one.
 *
 * The frame requirement is therefore `1 + body` instead of
 * `(n-m) * (1 + body)`, and it no longer depends on the count at all. That is
 * the §7 prediction about `rx_info`'s stamped ceiling, and vm_cost_rep carries
 * the matching arithmetic. */
static void vm_poss_chain(Vm *v, int entry, const Ast *body, int count,
                          int next, int mslot)
{
    int exitl = vm_label(v);
    int cur = entry;

    for (int j = 0; j < count; j++) {
        int bentry = vm_label(v), after = vm_label(v);
        vm_lbl(v, cur, vm_rolef(v, "possessified optional copy (%d remaining)",
                                count - j));
        vm_cut(v, mslot,
               "cut: the previous copy is committed, its choice points are dead");
        vm_push_at(v, exitl, "pos",
                   "the loop's ONLY frame: this copy failing leaves the loop");
        vm_goto(v, bentry);
        vm_emit(v, bentry, body, after);
        cur = after;
    }

    vm_lbl(v, cur, "possessified repeat: every copy taken");
    vm_cut(v, mslot, "cut: the loop is complete and owns no live choice point");
    vm_goto(v, next);

    if (count > 0) {
        vm_lbl(v, exitl, "possessified repeat: a copy could not run -- exit "
                         "with the iterations that did");
        /* The pop restored `pos` to this copy's start AND left the resume
         * stack at exactly `mark`, because the frame it popped was the one
         * this loop pushed at that depth. Nothing to undo. */
        vm_goto(v, next);
    } else {
        /* X{m,m}: no optional copy, so nothing ever pushed `exitl`. The label
         * is still emitted so the listing's label set matches the artifact's
         * — vm_lbl is the only way to emit one, and a label the emitter
         * allocated but never wrote would break that correspondence. */
        vm_lbl(v, exitl, "possessified repeat: unreachable (exact count)");
        vm_goto(v, next);
    }
}

/* [ENG-BREP] The possessified frames rung, UNBOUNDED (`X{m,}`). Same one-frame
 * discipline as the bounded chain, with the copies replaced by a real loop.
 *
 * NO EMPTY-ITERATION GUARD IS NEEDED, and that is structural rather than an
 * omission. §3.3's guard exists to stop a NULLABLE body iterating forever;
 * §2.2's rule refuses to possessify a nullable body at all, and the two
 * nullability predicates are the same function computed twice — src/opt/
 * possessify.c's Glushkov nullability (A_CLASS false, zero-width true, CAT
 * and, ALT or, REP `|| rmin == 0`, A_CAP transparent) is `vm_nullable` above,
 * arm for arm. So `a->possessive` on an unbounded repeat implies
 * `!vm_nullable(a->l)`, every iteration consumes at least one byte, and the
 * loop terminates on the subject rather than on a guard. */
static void vm_poss_star(Vm *v, int entry, const Ast *body, int next, int mslot)
{
    int bentry = vm_label(v), bend = vm_label(v), exitl = vm_label(v);

    vm_lbl(v, entry, "possessified unbounded repeat: one frame for the whole "
                     "loop, however many iterations run");
    vm_cut(v, mslot,
           "cut: the previous iteration is committed, its choice points are dead");
    vm_push_at(v, exitl, "pos",
               "the loop's ONLY frame: the iteration failing leaves the loop");
    vm_goto(v, bentry);

    vm_emit(v, bentry, body, bend);

    vm_lbl(v, bend, "possessified unbounded repeat: one iteration done");
    vm_goto(v, entry);

    vm_lbl(v, exitl, "possessified unbounded repeat: the exit");
    /* No cut here: the frame this loop pushed sat at depth `mark`, so popping
     * it left the stack there already, and the body's frames above it were
     * popped on the way. */
    vm_goto(v, next);
}

/* ---- [ENG-BREP] the REVERSE-DETERMINISTIC rung ---------------------------
 *
 * engine_m4.md §2.5's rung, between the cursor and the frames. Design and the
 * full derivation: docs/design/rungselect_impl/rungselect_design.md.
 *
 * ONE body copy instead of `rmax` of them. The emitted loop is a deterministic
 * FORWARD SCAN that counts iterations, ONE resume frame for the whole loop, and
 * a BACKWARD WALK over the reversed body that serves two jobs at once — it
 * finds the previous iteration boundary for a retreat, and it recovers §3.4's
 * last-iteration captures.
 *
 * THE BACKWARD WALK HAS NO CHOICE POINTS, and that is the rung's name made
 * concrete. src/opt/revdet.c only selects the rung when the REVERSED body is
 * one-unambiguous, so at an alternation the next byte decides the branch and
 * the walk dispatches on it instead of pushing a frame per branch. A failure
 * anywhere in a step is therefore final for that step, which is why every
 * failure edge below goes to ONE label (the walk's end) rather than to
 * `rx_fail`.
 *
 * IT NEVER TOUCHES `pos`. The walk is a DERIVATION, not a move: it runs on its
 * own cursor local, so the boundary the loop committed at is still `pos` when
 * the walk finishes and the continuation is taken. */
typedef struct {
    const char *cur;    /* the walk's own cursor local */
    const char *floor;  /* the loop's entry position, as an stv read */
    const char *ga;     /* the capture-recovery locals: spans */
    const char *gs;     /* ... and their seen flags */
    const char *ns;     /* the seen counter */
    const int  *grp;    /* body group numbers, in the dense index's order */
    int         ngrp;
    int         faill;  /* where any failure in a step lands */
} Rev;

static int vm_rev_index(const Rev *R, int capno)
{
    for (int i = 0; i < R->ngrp; i++) if (R->grp[i] == capno) return i;
    return -1;
}

static void vm_rev_emit(Vm *v, int entry, const Ast *a, int next, const Rev *R)
{
    StrBuf *b = v->b;
    char byte[80];
    vm_charge(v);
    snprintf(byte, sizeof byte, "s[%s - 1]", R->cur);

    switch (a->k) {
    case A_CLASS: {
        int ci = vm_cls(v, a->cls);
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_CLASS, ci, next, "consumed BACKWARD");
        sb_printf(b, "    if (%s > %s && (", R->cur, R->floor);
        vm_cls_test(v, b, ci, byte);
        sb_printf(b, ")) { %s--; goto %s_L%d; }\n", R->cur, v->p, next);
        vm_goto(v, R->faill);
        return;
    }
    case A_CAP: {
        /* §3.4's rule, delivered by the direction of travel. Going backward the
         * FIRST time a group is met is the LAST iteration that ENTERED it,
         * which is exactly the value PCRE2 reports — and exactly what the plan
         * row's constant-offset formula got wrong on 1,799 of 15,036 matches,
         * because a later iteration taking the other branch does not CLEAR a
         * group an earlier one wrote.
         *
         * The writes go to LOCALS, not through RX_SET. Two reasons and both are
         * load-bearing: the values must be published AFTER the loop's resume
         * frame is pushed (so a retreat rewinds them rather than accumulating
         * them, the cursor rung's own ordering rule), and a walk that wrote
         * through the trail would cost entries per ITERATION where publishing
         * costs them per GROUP.
         *
         * A partially-written group is harmless: `seen` is set only at the
         * group's left edge, i.e. only once the whole group has matched, so a
         * step that dies in the middle leaves a stale span nobody publishes. */
        int j = vm_rev_index(R, a->capno);
        int inner = vm_label(v), close = vm_label(v);
        vm_lbl(v, entry, vm_rolef(v, "group %d: its END, met first going backward",
                                  a->capno));
        if (j >= 0)
            sb_printf(b, "    if (!%s[%d]) %s[%d][1] = (ptrdiff_t)%s;\n",
                      R->gs, j, R->ga, j, R->cur);
        vm_goto(v, inner);
        vm_rev_emit(v, inner, a->l, close, R);
        vm_lbl(v, close, vm_rolef(v, "group %d: its START -- the last iteration "
                                     "that entered it wins", a->capno));
        if (j >= 0)
            sb_printf(b, "    if (!%s[%d]) { %s[%d][0] = (ptrdiff_t)%s;"
                         " %s[%d] = 1; %s++; }\n",
                      R->gs, j, R->ga, j, R->cur, R->gs, j, R->ns);
        vm_goto(v, next);
        return;
    }
    case A_CAT: {
        /* The tree is ALREADY reversed (src/opt/revdet.c swapped every A_CAT's
         * children), so this walks it in the ordinary left-to-right way and the
         * reversal is not re-applied here. Spine flattened iteratively for
         * nfa.c's R-2 reason. */
        int nsp = 0;
        const Ast *t = a;
        while (t->k == A_CAT) { nsp++; t = t->l; }
        const Ast **rs = arena_alloc(&v->cx->arena, (size_t)nsp * sizeof(Ast *));
        int i = nsp;
        t = a;
        while (t->k == A_CAT) { rs[--i] = t->r; t = t->l; }
        int cur = entry, nx = vm_label(v);
        vm_rev_emit(v, cur, t, nx, R);
        cur = nx;
        for (int j = 0; j < nsp; j++) {
            int after = (j + 1 == nsp) ? next : vm_label(v);
            vm_rev_emit(v, cur, rs[j], after, R);
            cur = after;
        }
        return;
    }
    case A_ALT: {
        /* THE BYTE DECIDES, so there is no frame here. Reverse one-unambiguity
         * makes the branches' first sets pairwise disjoint — checked directly
         * on this tree by src/opt/revdet.c's `rd_alt_disjoint`, at the place the
         * emitter depends on it rather than inherited from (U1) three functions
         * away — so at most one test below can succeed and a branch that fails
         * after being chosen has no alternative to try. */
        int nbr = 1;
        for (const Ast *t = a; t->k == A_ALT; t = t->l) nbr++;
        const Ast **br = arena_alloc(&v->cx->arena, (size_t)nbr * sizeof(Ast *));
        int i = nbr;
        const Ast *t = a;
        while (t->k == A_ALT) { br[--i] = t->r; t = t->l; }
        br[0] = t;
        int *bentry = arena_alloc(&v->cx->arena, (size_t)nbr * sizeof(int));
        for (int j = 0; j < nbr; j++) bentry[j] = vm_label(v);

        vm_lbl(v, entry, vm_rolef(v, "backward alternation (%d branches):"
                                     " the byte selects, no frame", nbr));
        sb_printf(b, "    if (%s <= %s) goto %s_L%d;\n",
                  R->cur, R->floor, v->p, R->faill);
        for (int j = 0; j < nbr; j++) {
            uint8_t f[32];
            pcrec_revdet_first(br[j], f);
            int ci = vm_cls(v, f);
            sb_puts(b, "    if (");
            vm_cls_test(v, b, ci, byte);
            sb_printf(b, ") goto %s_L%d;\n", v->p, bentry[j]);
        }
        vm_goto(v, R->faill);
        for (int j = 0; j < nbr; j++) vm_rev_emit(v, bentry[j], br[j], next, R);
        return;
    }
    case A_REP: {
        /* Only an EXACT count reaches here (revdet.c's shape scan declines
         * every other kind), and an exact count is literal replication, which
         * reverses to literal replication of the reversed sub-body. */
        int cur = entry;
        for (int i = 0; i < a->rmin; i++) {
            int nx = (i + 1 == a->rmin) ? next : vm_label(v);
            vm_rev_emit(v, cur, a->l, nx, R);
            cur = nx;
        }
        return;
    }
    default:
        break;
    }
    ctx_fail(v->cx, 0, "internal error: bad AST node in the backward walk");
}

static void vm_revdet_rep(Vm *v, int entry, const Ast *a, int next)
{
    StrBuf *b = v->b;
    const int loop = v->nrev++;
    const int se = vm_slot_rev(v, loop, 0);
    const int sl = vm_slot_rev(v, loop, 1);
    const int sh = vm_slot_rev(v, loop, 2);
    const bool move   = vm_rev_canmove(a);
    const bool greedy = a->greedy;
    int grp[PCREC_MAX_REVDET_BODY_GROUPS];
    int ng = 0;
    vm_rev_caps(a->l, grp, &ng, PCREC_MAX_REVDET_BODY_GROUPS);
    /* The walk runs when something needs it: a GREEDY loop that can move needs
     * the previous boundary, and any loop with groups needs their values. A
     * lazy loop moves FORWARD, so it needs the walk only for captures. */
    const bool walk = (greedy && move) || ng > 0;

    /* One named scalar per field per loop, rather than one array of structs.
     * Not a style choice: the emitted matcher is built -Wall -Wextra -Werror,
     * and gcc cannot see through a computed-goto control flow well enough to
     * prove an array element is written before it is read, so the array form
     * failed -Wmaybe-uninitialized on four corpus patterns. A scalar carries
     * its own `= 0` at its declaration and the question does not arise. */
    char rv[80], cur[96], flr[32];
    snprintf(rv,  sizeof rv,  "%s_rv%d", v->p, loop);
    snprintf(cur, sizeof cur, "%s_rv%d_c", v->p, loop);
    snprintf(flr, sizeof flr, "(size_t)stv[%d]", se);

    char bounds[32];
    if (a->rmax < 0) snprintf(bounds, sizeof bounds, "{%d,}", a->rmin);
    else             snprintf(bounds, sizeof bounds, "{%d,%d}", a->rmin, a->rmax);
    const char *role = vm_rolef(v, "reverse-deterministic rung %s, %s%s"
                                   " -- ONE body copy, no replication",
                                bounds, greedy ? "greedy" : "lazy",
                                a->possessive ? ", POSSESSIFIED" : "");

    int scanl = vm_label(v), bodyl = vm_label(v), bodyok = vm_label(v);
    int shortl = vm_label(v), fulll = vm_label(v), commitl = vm_label(v);
    int walkl = 0, revl = 0, wstepl = 0, wendl = 0, extl = 0, extbl = 0, extok = 0;
    if (walk) {
        walkl = vm_label(v); revl = vm_label(v);
        wstepl = vm_label(v); wendl = vm_label(v);
    }
    if (move && !greedy) {
        extl = vm_label(v); extbl = vm_label(v); extok = vm_label(v);
    }

    /* ---- entry ---------------------------------------------------------- */
    vm_lbl(v, entry, role);
    vm_rung_mark(v, entry, VM_RUNG_REVDET, a->possessive, role);
    vm_set(v, se, "(ptrdiff_t)pos",
           "revdet: the loop's entry position (the capture walk's floor)");
    if (a->rmin == 0)
        vm_set(v, sl, "(ptrdiff_t)pos",
               "revdet: low-water = the entry, since rmin is 0");
    sb_printf(b, "    %s_it = 0;\n", rv);
    vm_goto(v, scanl);

    /* ---- the forward scan ------------------------------------------------
     * One body copy, run to the maximal boundary. The CUT at every iteration
     * boundary is what makes the resume stack O(1) in the iteration count, and
     * it is licensed by the forward unique-iteration property: once the body
     * has matched [p,q) there is no other way to match an iteration there, so
     * its internal choice points are provably dead. The cut is at a BOUNDARY
     * and never inside a body — a one-unambiguous body still needs its own
     * frames to FIND its match, which is vm_poss_chain's own recorded lesson. */
    vm_lbl(v, scanl, "revdet scan: try one more iteration");
    if (a->rmax >= 0)
        sb_printf(b, "    if (%s_it >= %dUL) goto %s_L%d;\n",
                  rv, a->rmax, v->p, fulll);
    sb_printf(b, "    %s_mk = w->btn;\n", rv);
    vm_push_at(v, shortl, "pos",
               "this iteration cannot run -- leave the loop with the ones that did");
    vm_goto(v, bodyl);

    /* Capture writes SUPPRESSED for the whole forward body: they are what would
     * make the trail grow per iteration, and the backward walk recovers every
     * one of them from the committed span. */
    v->nocap++;
    vm_emit(v, bodyl, a->l, bodyok);
    v->nocap--;

    vm_lbl(v, bodyok, "revdet scan: one iteration committed");
    sb_printf(b, "    w->btn = %s_mk;\n", rv);
    vm_ev(v, VE_NOTE, 0, 0, "cut to the iteration's entry depth: a unique-iteration"
                            " body has no second parse of what just matched");
    sb_printf(b, "    %s_it++;\n", rv);
    if (a->rmin > 0) {
        sb_printf(b, "    if (%s_it == %dUL) {\n", rv, a->rmin);
        vm_set(v, sl, "(ptrdiff_t)pos",
               "revdet: low-water = the boundary after rmin iterations");
        sb_puts(b, "    }\n");
    }
    vm_goto(v, scanl);

    /* `it` is read HERE and never at the commit label, which a retreat re-enters
     * long after an outer backtrack may have re-entered the loop and reset it.
     * Everything the commit tests is a slot or `pos`. */
    vm_lbl(v, shortl, "revdet scan: the body could not run at this boundary");
    if (a->rmin > 0)
        sb_printf(b, "    if (%s_it < %dUL) goto %s_fail;\n", rv, a->rmin, v->p);
    vm_goto(v, fulll);

    vm_lbl(v, fulll, "revdet: the forward scan is complete");
    vm_set(v, sh, "(ptrdiff_t)pos",
           "revdet: the maximal boundary reached (the lazy extension's ceiling)");
    if (!greedy && move) {
        sb_printf(b, "    pos = (size_t)stv[%d];\n", sl);
        vm_ev(v, VE_NOTE, 0, 0,
              "lazy: commit at the MINIMUM and extend on backtrack");
    }
    vm_goto(v, commitl);

    /* ---- commit ---------------------------------------------------------- */
    vm_lbl(v, commitl, "revdet: commit at this boundary");
    if (walk) {
        Rev R;
        char ga[64], gs[64], ns[64];
        snprintf(ga, sizeof ga, "%s_rvg", v->p);
        snprintf(gs, sizeof gs, "%s_rvs", v->p);
        snprintf(ns, sizeof ns, "%s_rv%d_ns", v->p, loop);
        R.cur = cur; R.floor = flr; R.ga = ga; R.gs = gs; R.ns = ns;
        R.grp = grp; R.ngrp = ng; R.faill = wendl;

        sb_printf(b, "    %s_c = pos;\n", rv);
        sb_printf(b, "    %s_prev = -1;\n", rv);
        if (ng) {
            sb_printf(b, "    %s_ns = 0;\n", rv);
            sb_printf(b, "    { int i_; for (i_ = 0; i_ < %d; i_++)"
                         " %s_rvs[i_] = 0; }\n", ng, v->p);
        }
        vm_goto(v, walkl);

        vm_lbl(v, walkl, "revdet walk: one step back over the committed span");
        sb_printf(b, "    if (%s <= %s) goto %s_L%d;\n",
                  cur, flr, v->p, wendl);
        vm_goto(v, revl);
        vm_rev_emit(v, revl, a->revbody, wstepl, &R);

        vm_lbl(v, wstepl, "revdet walk: landed on the previous boundary");
        sb_printf(b, "    if (%s_prev < 0) %s_prev = (ptrdiff_t)%s;\n",
                  rv, rv, cur);
        if (ng) {
            sb_printf(b, "    if (%s_ns >= %d) goto %s_L%d;\n",
                      rv, ng, v->p, wendl);
            vm_goto(v, walkl);
        } else {
            vm_ev(v, VE_NOTE, 0, 0,
                  "no group to witness: one step is all the retreat needs");
            vm_goto(v, wendl);
        }
        vm_lbl(v, wendl, "revdet walk: done (all groups witnessed, or the "
                         "loop's entry reached)");
    }

    /* The frame is pushed BEFORE the captures are published, so its trail mark
     * sits below them and every retreat rewinds the previous commit's values
     * instead of accumulating them (the cursor rung's own ordering rule). */
    if (move) {
        if (greedy) {
            char pv[112];
            snprintf(pv, sizeof pv, "(size_t)%s_prev", rv);
            sb_printf(b, "    if ((ptrdiff_t)pos > stv[%d] && %s_prev >= 0) {\n",
                      sl, rv);
            vm_push_at(v, commitl, pv,
                       "retreat: resume this very label with pos at the "
                       "PREVIOUS boundary, and re-derive from there");
            sb_puts(b, "    }\n");
        } else {
            sb_printf(b, "    if ((ptrdiff_t)pos < stv[%d]) {\n", sh);
            vm_push_at(v, extl, "pos",
                       "extend: one more iteration is the lazy resume");
            sb_puts(b, "    }\n");
        }
    }
    for (int j = 0; j < ng; j++) {
        char val[64];
        sb_printf(b, "    if (%s_rvs[%d]) {\n", v->p, j);
        snprintf(val, sizeof val, "%s_rvg[%d][0]", v->p, j);
        vm_set(v, 2 * grp[j], val,
               vm_rolef(v, "group %d open, recovered by the backward walk",
                        grp[j]));
        snprintf(val, sizeof val, "%s_rvg[%d][1]", v->p, j);
        vm_set(v, 2 * grp[j] + 1, val,
               vm_rolef(v, "group %d close, recovered by the backward walk",
                        grp[j]));
        sb_puts(b, "    }\n");
    }
    vm_ev(v, VE_NOTE, 0, 0, "a group the walk never witnessed keeps its previous"
                            " value -- which is §3.4's ZERO-ITERATION clause at"
                            " the boundary where the loop never ran");
    vm_goto(v, next);

    /* ---- the lazy extension --------------------------------------------- */
    if (move && !greedy) {
        vm_lbl(v, extl, "revdet: extend by one iteration (lazy resume)");
        sb_printf(b, "    %s_mk = w->btn;\n", rv);
        vm_goto(v, extbl);
        v->nocap++;
        vm_emit(v, extbl, a->l, extok);
        v->nocap--;
        vm_lbl(v, extok, "revdet: the extra iteration matched");
        sb_printf(b, "    w->btn = %s_mk;\n", rv);
        vm_goto(v, commitl);
        /* The body FAILING here needs no frame of its own: the push above only
         * happens below `hi`, and below `hi` the chain guarantees a next
         * boundary — so a failure means this path is genuinely exhausted, which
         * is what falling through to rx_fail already means. */
    }
}

static void vm_rep(Vm *v, int entry, const Ast *a, int next)
{
    const uint8_t *seq[VM_MAX_STRIDE];
    CapOff caps[VM_MAX_BODY_CAPS];
    int stride = 0, ncaps = 0;

    if (a->rmin == 0 && a->rmax == 0) {   /* X{0} matches empty */
        vm_lbl(v, entry, "X{0}: matches empty, no code");
        vm_goto(v, next);
        return;
    }

    if (vm_cursor_fits(a, seq, &stride, caps, &ncaps)) {
        vm_cursor_rep(v, entry, a, next, seq, stride, caps, ncaps);
        return;
    }

    /* [ENG-BREP] the ladder's second rung, below the cursor and above the
     * frames. `a->revbody` is src/opt/revdet.c's verdict AND the material the
     * backward walk is emitted from, so this site cannot select the rung
     * without having the thing the rung needs. */
    if (a->revbody) {
        vm_revdet_rep(v, entry, a, next);
        return;
    }

    /* [D46] the fallthrough below is the WHOLE frames rung for this
     * quantifier — mandatory copies, the bounded opt-chain and the unbounded
     * star are marked once here rather than at each of their own returns.
     * `a->rmax` already distinguishes bounded from unbounded at this point
     * (nothing downstream can change it), so the split is made HERE rather
     * than duplicated at each return site below. */
    {
        char fbounds[32];
        bool bounded = a->rmax >= 0;
        if (bounded) snprintf(fbounds, sizeof fbounds, "{%d,%d}", a->rmin, a->rmax);
        else         snprintf(fbounds, sizeof fbounds, "{%d,}", a->rmin);
        const char *frole = vm_rolef(v, "frames rung, %s %s, %s%s",
                                     bounded ? "bounded" : "unbounded", fbounds,
                                     a->greedy ? "greedy" : "lazy",
                                     a->possessive
                                       ? ", POSSESSIFIED (one frame for the"
                                         " whole loop, no giveback)" : "");
        vm_rung_mark(v, entry, bounded ? VM_RUNG_FRAMES_BOUNDED
                                        : VM_RUNG_FRAMES_UNBOUNDED,
                     a->possessive, frole);
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

    /* [ENG-BREP] The possessified frames rung takes the SAME mandatory copies
     * and then a different tail. The cut mark is recorded FIRST, before the
     * mandatory copies rather than after them, so the cut at the first
     * optional copy also discards the mandatory bodies' own dead frames — the
     * loop is atomic as a whole, which is what "possessive" means. Leaving
     * them would also be correct (the verdict says they are dead, so resuming
     * one cannot change the answer); discarding them is simply the win. */
    if (a->possessive) {
        int mslot = vm_slot_mark(v, v->nmark++);
        int body0 = vm_label(v);
        vm_lbl(v, entry, "possessified repeat: record the resume-stack depth "
                         "to cut back to");
        vm_set(v, mslot, "(ptrdiff_t)w->btn",
               "possessive cut mark (resume-stack depth at loop entry)");
        vm_goto(v, body0);
        cur = body0;
        for (int i = 0; i < a->rmin; i++) {
            int nx = vm_label(v);
            vm_emit(v, cur, a->l, nx);
            cur = nx;
        }
        if (a->rmax >= 0) vm_poss_chain(v, cur, a->l, a->rmax - a->rmin, next, mslot);
        else              vm_poss_star(v, cur, a->l, next, mslot);
        return;
    }

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

    vm_lbl(v, cur, vm_rolef(v, "unbounded repeat, %s, frames rung%s",
                            a->greedy ? "greedy" : "lazy",
                            guard ? ", nullable body (empty-iteration guard)"
                                  : ""));
    if (guard)
        vm_set(v, gslot, "(ptrdiff_t)pos",
               "empty-iteration guard: where this iteration began");
    if (a->greedy) {
        vm_push(v, exit, "another iteration preferred; resume is the EXIT");
        vm_goto(v, bentry);
    } else {
        vm_push(v, bentry, "the exit is preferred; resume is another ITERATION");
        vm_goto(v, exit);
    }

    vm_emit(v, bentry, a->l, bend);

    vm_lbl(v, bend, "unbounded repeat: one iteration done");
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

    vm_lbl(v, exit, "unbounded repeat: the exit");
    vm_goto(v, next);
}

static void vm_emit(Vm *v, int entry, const Ast *a, int next)
{
    StrBuf *b = v->b;
    vm_charge(v);

    switch (a->k) {
    case A_CLASS: {
        int ci = vm_cls(v, a->cls);
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_CLASS, ci, next, NULL);
        sb_puts(b, "    if (pos < n && (");
        vm_cls_test(v, b, ci, "s[pos]");
        sb_printf(b, ")) { pos++; goto %s_L%d; }\n", v->p, next);
        vm_fail(v);
        return;
    }
    case A_EMPTY:
        vm_lbl(v, entry, "empty");
        vm_goto(v, next);
        return;
    case A_BOL:
        /* `^` is start of SUBJECT, absolute — it anchors to offset 0 whatever
         * startpos was, matching the emitted contract in lib/pcrec.h and the
         * DFA's own N_BOT. */
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_ASSERT, next, 0, "^ start of subject (absolute offset 0)");
        sb_printf(b, "    if (pos == 0) goto %s_L%d;\n", v->p, next);
        vm_fail(v);
        return;
    case A_EOL:
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_ASSERT, next, 0,
              "$ end of subject, or before a final newline");
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
        vm_lbl(v, entry, vm_rolef(v, "group %d opens", a->capno));
        /* [ENG-BREP] SUPPRESSED inside a revdet loop's forward scan (v->nocap):
         * a per-iteration write is exactly the trail growth that rung exists to
         * remove, and §3.4's backward walk recovers the value the scan would
         * have left. vm_cost's A_CAP arm reads the same flag, so the emitted
         * code and the number the capacities are sized from cannot disagree. */
        if (!v->nocap)
            vm_set(v, 2 * a->capno, "(ptrdiff_t)pos",
                   vm_rolef(v, "group %d open, written on traverse", a->capno));
        vm_goto(v, inner);
        vm_emit(v, inner, a->l, close);
        vm_lbl(v, close, vm_rolef(v, "group %d closes", a->capno));
        if (!v->nocap)
            vm_set(v, 2 * a->capno + 1, "(ptrdiff_t)pos",
                   vm_rolef(v, "group %d close, written on traverse", a->capno));
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

/* ---- [M4.5c] rendering the listing ---------------------------------------
 *
 * Every section below is a VIEW over v->ev, the stream the emitter's own walk
 * produced. Nothing here re-derives anything from the AST — if it did, it
 * would be the parallel description engine_m4.md S10 forbids, and the first
 * time someone changed the emitter without changing the dump the dump would
 * start lying quietly. */

/* A byte class as a human reads it: 'a', [a-z], [0-9a-fx], or a count when it
 * is too scattered to spell. Derived from the SAME 256-bit bitmap the emitted
 * test is derived from (the class pool), not from the pattern text. */
static void vm_cls_describe(Vm *v, StrBuf *o, int ci)
{
    const uint8_t *bits = v->cls[ci];
    int count = 0;
    for (int c = 0; c < 256; c++) if (cls_has(bits, (unsigned)c)) count++;
    if (count == 256) { sb_puts(o, "any byte"); return; }
    if (count == 0)   { sb_puts(o, "(empty class)"); return; }

    /* Spell at most eight ranges; past that the count is more informative
     * than a wall of hex. */
    int nr = 0, shown = 0;
    for (int c = 0; c < 256; ) {
        if (!cls_has(bits, (unsigned)c)) { c++; continue; }
        int lo = c;
        while (c < 256 && cls_has(bits, (unsigned)c)) c++;
        nr++;
        if (nr > 8) continue;
        if (shown++ == 0) sb_puts(o, count == 1 ? "" : "[");
        else sb_puts(o, "");
        int hi = c - 1;
        char a[8], b[8];
        for (int k = 0; k < 2; k++) {
            int ch = k ? hi : lo;
            char *dst = k ? b : a;
            if (ch >= 32 && ch < 127 && ch != '\\' && ch != ']' && ch != '\'')
                snprintf(dst, 8, "%c", ch);
            else
                snprintf(dst, 8, "\\x%02x", ch);
        }
        if (lo == hi) sb_printf(o, count == 1 ? "'%s'" : "%s", a);
        else          sb_printf(o, "%s-%s", a, b);
    }
    if (nr > 8) {
        sb_printf(o, "...%d ranges, %d bytes]", nr, count);
    } else if (count != 1) {
        sb_puts(o, "]");
    }
}

typedef struct {
    long long budget, bt_frames, trail_frames, ceiling;
    int       nstate, nguard, nlow, nmark, ncaps;
    bool      has_budget, prefilter;
    const char *why;
} VmStamp;

/* [D46] renders v->rungs (the summary bitmask) as a comma-joined list of
 * kind names, e.g. "cursor, frames-unbounded", or "none" for a pattern with
 * no A_REP at all (a real, distinct answer — a caller asking "did the
 * cursor rung ever run" needs to tell "there was nothing to select between"
 * from "frames won every time", and D46's controllability half will need
 * the same distinction to report a forced selection with nothing to act
 * on). Read straight from the mask vm_rung_mark() built during the real
 * emission walk — never re-derived from the AST, per S10's own rule
 * (engine_m4.md S10): one structure, walked once, is what every view has
 * to agree with. The PER-QUANTIFIER detail this summarizes is the RUNGS
 * listing section below, built from the same VE_RUNG events. */
static void vm_rungs_describe(unsigned mask, StrBuf *o)
{
    if (!mask) { sb_puts(o, "none"); return; }
    bool first = true;
    for (int k = 0; k < VM_NRUNG; k++) {
        if (!(mask & vm_rung_bit[k])) continue;
        if (!first) sb_puts(o, ", ");
        sb_puts(o, vm_rung_kindname[k]);
        first = false;
    }
}

static void vm_strats_describe(unsigned mask, StrBuf *o)
{
    if (!mask) { sb_puts(o, "none"); return; }
    bool first = true;
    for (int k = 0; k < 2; k++) {
        if (!(mask & vm_strat_bit[k])) continue;
        if (!first) sb_puts(o, ", ");
        sb_puts(o, vm_strat_kindname[k]);
        first = false;
    }
}

static void vm_render_listing(Vm *v, StrBuf *o, const VmStamp *st)
{
    Ctx *cx = v->cx;

    sb_puts(o, "; pcrec VM program listing (DD-8; docs/design/engine_m4.md S10)\n");
    sb_puts(o, ";\n");
    sb_puts(o, "; Produced BY the emitter's own walk, not by a second walk over the\n");
    sb_puts(o, "; AST: every line below was written by the same call that wrote the\n");
    sb_puts(o, "; corresponding C. S10's one constraint -- \"the dump must be derived\n");
    sb_puts(o, "; from the same structure the emitter walks, never a parallel\n");
    sb_puts(o, "; description\" -- is therefore structural here, not a discipline.\n");
    sb_puts(o, ";\n");
    sb_puts(o, "; pattern      ");
    for (size_t i = 0; i < cx->patlen; i++) {
        unsigned char ch = (unsigned char)cx->pat[i];
        if (ch >= 32 && ch < 127) sb_putc(o, (char)ch);
        else sb_printf(o, "\\x%02x", ch);
    }
    sb_puts(o, "\n");
    sb_printf(o, "; engine       vm (forced by: %s)\n", st->why ? st->why : "--engine=vm");
    sb_printf(o, "; prefilter    %s\n", st->prefilter
              ? "yes -- the capture-erased forward+reverse DFA pair hands the VM"
                " an exact window (S6.1); the VM never scans"
              : "NO (--engine=vm) -- the VM scans from startpos itself (R21 E-6)");
    /* [D46] the rung stamp's QUICK-GLANCE summary: which rung KINDS appear
     * ANYWHERE in this program, not which one "the" program uses -- the
     * rung is selected per A_REP, so a pattern with two quantified bodies
     * can and does mix rungs (that is exactly the case a scalar summary
     * would get wrong). Read straight off v->rungs, the same bitmask the
     * <PREFIX>_VM_RUNGS macro below is built from. The RUNGS section further
     * down is the per-quantifier detail this line summarizes. */
    sb_puts(o, "; rungs        ");
    vm_rungs_describe(v->rungs, o);
    sb_puts(o, " -- see the RUNGS section below for which quantifier took"
               " which\n");
    /* [ENG-BREP] the ladder's first rung, summarized the same way and for the
     * same reason. "possessive" appearing here means at least one quantifier
     * needs no backtracking machinery at all; "backtracking" means at least
     * one still does. Both appearing is the mixed artifact a scalar would
     * misreport. */
    sb_puts(o, "; strategies   ");
    vm_strats_describe(v->strats, o);
    sb_puts(o, " -- see the STRATEGIES section below for which quantifier"
               " took which\n");
    /* [ENG-BREP] the pass's OWN census, from src/opt/possessify.c, and it is
     * deliberately not derived from the STRATEGIES rows below. Those are per
     * EMITTED quantifier, so a replicated bounded-repeat body contributes one
     * row per copy; these are per SOURCE `A_REP`, which is the only population
     * comparable with eng_brep_design.md §2.6's own census. Counting the rows
     * instead would measure replication as much as it measures the rule. */
    if (cx->opt->flags & PCREC_NO_POSSESSIFY)
        /* "0 of 0" would read as "this program has no quantifiers", which is
         * a different fact and usually a false one. A denied pass has not
         * counted anything, and the line says so. */
        sb_puts(o, "; possessify   DENIED (-fno-possessify): the pass did not"
                   " run, so nothing here was analysed\n");
    else
        sb_printf(o, "; possessify   %d of %d source quantifier%s possessified"
                     " (eng_brep_design.md S2)\n",
                  cx->poss_marked, cx->poss_total,
                  cx->poss_total == 1 ? "" : "s");
    /* The macro is <PREFIX>_NCAPS, not RX_NCAPS: naming a macro the artifact
     * does not contain would send a reader of a `-p myrx` listing looking for
     * a symbol that is not there. Every emitted name in this listing comes
     * from the same v->up/v->p the emitter used. */
    sb_printf(o, "; caps         %s_NCAPS %d (%d capturing group%s in the"
                 " pattern text)\n",
              v->up, st->ncaps, (int)cx->ncap, cx->ncap == 1 ? "" : "s");
    if (st->has_budget)
        sb_printf(o, "; step budget  %lld backtrack resumptions\n", st->budget);
    else
        sb_puts(o, "; step budget  none (--fno-step-budget)\n");
    sb_printf(o, "; capacities   %lld resume frames, %lld trail entries",
              st->bt_frames, st->trail_frames);
    if (st->ceiling > 0)
        sb_printf(o, " (subject ceiling %lld bytes)\n", st->ceiling);
    else
        sb_puts(o, " (exact: no subject ceiling)\n");
    sb_printf(o, "; program      %d labels, %d events\n", v->nlabel, v->nev);
    /* The PRE-PASS count, not a recount of the event stream. It is what
     * PCREC_MAX_VM_RESUME_POINTS is checked against before emission, so
     * printing it here is what lets a check compare the cap's own input
     * against the artifact that came out (tests/codegen/run_ir_listing.sh). */
    sb_printf(o, "; resume pts   %lld\n", v->npush);
    sb_printf(o, "; max replicas %lld (limit %d, checked before emission)\n",
              v->maxcopies, PCREC_MAX_VM_REPEAT_COPIES);

    /* ---- SLOTS ---------------------------------------------------------
     * The layout comes from vm_slot_guard/vm_slot_low, the same two functions
     * the emitter indexes with; "written" is derived from the VE_SET events,
     * so a slot the layout reserves and the program never writes shows up as
     * exactly that. */
    sb_puts(o, "\nSLOTS (the stv array, engine_m4.md S2.4)\n");
    sb_printf(o, "  %-12s %-22s %s\n", "slot", "holds", "note");
    for (int k = 0; k <= v->ngroups; k++) {
        int w = 0;
        for (int i = 0; i < v->nev; i++)
            if (v->ev[i].k == VE_SET && (v->ev[i].a == 2 * k || v->ev[i].a == 2 * k + 1))
                w++;
        char what[32];
        if (k == 0) snprintf(what, sizeof what, "$0 whole match");
        else        snprintf(what, sizeof what, "group %d", k);
        sb_printf(o, "  %2d,%-9d %-22s %s\n", 2 * k, 2 * k + 1, what,
                  k == 0 ? "written by the ENTRY, not the VM (S3.4)"
                         : (w ? "written on traverse, trailed" : "never written"));
    }
    if (v->nguard_total == 0)
        sb_puts(o, "  (no empty-iteration guard slots: no nullable unbounded"
                   " quantifier on the frames rung)\n");
    for (int i = 0; i < v->nguard_total; i++)
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_guard(v, i),
                  "empty-iteration guard", "where the current iteration began (S3.3)");
    if (v->nlow == 0)
        sb_puts(o, "  (no span-loop low-water slots: no cursor rung in this"
                   " program)\n");
    for (int i = 0; i < v->nlow; i++)
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_low(v, i),
                  "span-loop low-water", "the loop's entry position (S2.5)");
    for (int i = 0; i < v->nmark; i++)
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_mark(v, i),
                  "possessive cut mark",
                  "resume-stack depth at loop entry (eng_brep_design.md S2)");
    for (int i = 0; i < v->nrev; i++) {
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_rev(v, i, 0),
                  "revdet loop entry", "the capture walk's floor (S2.5)");
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_rev(v, i, 1),
                  "revdet low-water", "boundary after rmin iterations: the retreat's floor");
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_rev(v, i, 2),
                  "revdet ceiling", "maximal boundary reached: the lazy extension's cap");
    }

    /* ---- RUNGS -----------------------------------------------------------
     * [D46] the PER-QUANTIFIER detail the header's "; rungs" summary line
     * folds into one bitmask. One row per A_REP, in emission order, each
     * naming the label the rung was recorded against (vm_rung_mark's own
     * `entry` argument) and the rung kind — never re-derived: every row
     * below is a VE_RUNG event vm_cursor_rep / vm_rep's frames fallthrough
     * appended at the same call that decided the rung. */
    sb_puts(o, "\nRUNGS (engine_m4.md S2.5; D46's per-quantifier stamp)\n");
    {
        int n = 0;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k != VE_RUNG) continue;
            n++;
            sb_printf(o, "  at L%-6d %-18s %s\n", v->ev[i].a,
                      vm_rung_kindname[v->ev[i].b],
                      v->ev[i].role ? v->ev[i].role : "");
        }
        if (n == 0)
            sb_puts(o, "  (none: no quantifier in this program consulted the"
                       " rung ladder at all)\n");
    }

    /* ---- STRATEGIES ------------------------------------------------------
     * [ENG-BREP] the per-quantifier possessification verdict, as ACTED ON:
     * every row is a VE_STRAT event appended by the same vm_rung_mark() call
     * that decided the emitted shape, so a row saying "possessive" and an
     * artifact that emitted a resume frame for that quantifier are not two
     * things that could disagree — there is one call and it did both. */
    sb_puts(o, "\nSTRATEGIES (eng_brep_design.md S2; D47.3's per-quantifier"
               " stamp)\n");
    {
        int n = 0;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k != VE_STRAT) continue;
            n++;
            sb_printf(o, "  at L%-6d %-14s %s\n", v->ev[i].a,
                      vm_strat_kindname[v->ev[i].b],
                      v->ev[i].role ? v->ev[i].role : "");
        }
        if (n == 0)
            sb_puts(o, "  (none: this program has no quantifier to possessify)\n");
    }

    /* ---- PROGRAM -------------------------------------------------------*/
    sb_puts(o, "\nPROGRAM\n");
    for (int i = 0; i < v->nev; i++) {
        const VEvent *e = &v->ev[i];
        switch (e->k) {
        case VE_LABEL:
            if (e->role) sb_printf(o, "  L%-6d ; %s\n", e->a, e->role);
            else         sb_printf(o, "  L%d\n", e->a);
            break;
        case VE_CLASS: {
            StrBuf d;
            memset(&d, 0, sizeof d);
            vm_cls_describe(v, &d, e->a);
            sb_printf(o, "         consume %-28s -> L%d\n", d.p ? d.p : "?", e->b);
            (void)0;
            sb_free(&d);
            break;
        }
        case VE_ASSERT:
            sb_printf(o, "         assert  %-28s -> L%d\n",
                      e->role ? e->role : "?", e->a);
            break;
        case VE_PUSH: {
            char tgt[24];
            snprintf(tgt, sizeof tgt, "resume L%d", e->a);
            sb_printf(o, "         PUSH    %-28s ; %s\n", tgt,
                      e->role ? e->role : "choice point");
            break;
        }
        case VE_SET: {
            char slot[24];
            snprintf(slot, sizeof slot, "stv[%d] <- pos", e->a);
            sb_printf(o, "         set     %-28s ; %s\n", slot,
                      e->role ? e->role : "");
            break;
        }
        case VE_GOTO:
            sb_printf(o, "         -> L%d\n", e->a);
            break;
        case VE_FAIL:
            sb_puts(o, "         -> fail (backtrack)\n");
            break;
        case VE_NOTE:
            sb_printf(o, "         ; %s\n", e->role ? e->role : "");
            break;
        case VE_ACCEPT:
            sb_puts(o, "         -> accept\n");
            break;
        case VE_ISLAND: case VE_CALLOUT:
            break;
        case VE_RUNG:
        case VE_STRAT:
            /* the RUNGS and STRATEGIES sections above are these events' own
             * views; PROGRAM stays a straight-line trace of what actually
             * executes, and neither a rung nor a strategy selection writes C
             * of its own to trace. */
            break;
        case VE_CUT: {
            /* [ENG-BREP] this one DOES write C, so unlike the two above it
             * belongs in the trace. */
            char slot[32];
            snprintf(slot, sizeof slot, "frames <- stv[%d]", e->a);
            sb_printf(o, "         CUT     %-28s ; %s\n", slot,
                      e->role ? e->role : "commit: discard the loop's frames");
            break;
        }
        }
    }
    sb_puts(o, "  accept   ; return pos - ctx->pos; the capture slots at this"
               " instant ARE the answer (S3.1)\n");
    sb_puts(o, "  fail     ; the ONLY backtracker and the only indirect jump;"
               " one step charged here (S4.2)\n");

    /* ---- CHOICE POINTS -------------------------------------------------*/
    {
        int n = 0;
        sb_puts(o, "\nCHOICE POINTS (preference order: the frame pushed at a site"
                   " resumes the LESS preferred alternative)\n");
        int cur = -1;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k == VE_LABEL) cur = v->ev[i].a;
            if (v->ev[i].k != VE_PUSH) continue;
            n++;
            sb_printf(o, "  at L%-6d resume L%-6d %s\n", cur, v->ev[i].a,
                      v->ev[i].role ? v->ev[i].role : "");
        }
        if (n == 0)
            sb_puts(o, "  (none: this program never backtracks -- it is a straight"
                       " line, and the resume stack is never pushed)\n");
    }

    /* ---- ISLANDS / CALLOUTS --------------------------------------------
     * Honestly empty, and empty by COUNT rather than by a hardcoded blank:
     * the day a producer exists these sections fill in with no change here. */
    {
        int isl = 0, co = 0;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k == VE_ISLAND)  isl++;
            if (v->ev[i].k == VE_CALLOUT) co++;
        }
        sb_printf(o, "\nDFA ISLANDS (%d)\n", isl);
        if (isl == 0)
            sb_puts(o, "  (none: islands are [M4.6]; engine_m4.md S6.3/S6.4 --"
                       " the auto-possessification that proves an island exact"
                       " does not exist yet)\n");
        sb_printf(o, "\nCALLOUT SITES (%d)\n", co);
        if (co == 0)
            sb_puts(o, "  (none: module 'callouts' has no producer, so no"
                       " pattern can reach a call site -- engine_m4.md S9.1)\n");
    }
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
    /* Set BEFORE the walk: vm_push_at reads it to decide whether the emitted
     * RX_PUSH carries its label id. */
    v.tracing = (cx->opt->flags & PCREC_TRACE) != 0;

    pcrec_gen_names(cx, &g);
    memcpy(v.up, g.upper, sizeof v.up);

    const int ncaps = v.ngroups + 1;

    /* Slot counting first: RX_NSTATE has to be known before the rx_work type
     * is emitted, and it must agree EXACTLY with what the emitter goes on to
     * assign — so the counter mirrors the emitter's own rung decisions rather
     * than approximating them. */
    vm_count_slots(&v, root, 1);
    /* [M4.5c fix] REFUSE BEFORE EMITTING. PCREC_MAX_VM_NODES alone let
     * `((a)|b){0,4000}c` through at 3.5 MB (D45's own case); this is the
     * compiler-side bound that stops it, and it is checked here — after the
     * pre-pass, before a single byte of the matcher is written — because the
     * whole point is not to do the work. See limits.h for the measurement
     * behind the number and for why the cap is on REPLICATION rather than on
     * total emitted size. */
    if (v.maxcopies > PCREC_MAX_VM_REPEAT_COPIES)
        ctx_fail(cx, cx->first_cap_pos == (size_t)-1 ? 0 : cx->first_cap_pos,
                 /* Inside pcrec_error.msg's 256 bytes on purpose: a diagnostic
                  * that names the fix and is then truncated has not named it. */
                 "pattern too large: a bounded repeat would replicate its body "
                 "%lld times (limit %d). A body containing an alternation is "
                 "copied once per repetition -- lower the count, or remove the "
                 "alternation so the body compiles to a span loop instead",
                 v.maxcopies, PCREC_MAX_VM_REPEAT_COPIES);
    const int nguard_total = v.nguard, nlow_total = v.nlow;
    const int nmark_total = v.nmark;   /* [ENG-BREP] possessive cut marks */
    const int nrev_total  = v.nrev;    /* [ENG-BREP] revdet loops, 3 slots each */
    v.nguard_total = nguard_total;
    v.nlow_total   = nlow_total;
    v.nmark_total  = nmark_total;
    v.nrev_total   = nrev_total;
    v.nguard = v.nlow = v.nmark = v.nrev = 0;
    const int nstate = 2 * ncaps + nguard_total + nlow_total + nmark_total
                     + 3 * nrev_total;

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
        /* THROUGH vm_lbl, not a direct sb_printf. This was the one place that
         * emitted a label by a second route, and it is exactly the drift
         * engine_m4.md S10 warns about: the label existed in the artifact and
         * not in the listing, so the listing described a program one label
         * short of the emitted one. Caught by
         * tests/codegen/run_ir_listing.sh's label-set check on its first run,
         * which is the argument for having written that check at all — the
         * "one call, one truth" property is structural only while there is
         * genuinely one call. */
        vm_lbl(&v, acc, "the pattern is complete");
        vm_ev(&v, VE_ACCEPT, 0, 0, NULL);
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
    /* [D46] the RUNG STAMP: same PLACEMENT as RX_ENGINE/RX_ENGINE_WHY above
     * (a per-prefix, preprocessor-visible macro family, VM-artifacts-only
     * for the same §5.4 byte-identity reason the comment above states), but
     * a SUMMARY BITMASK rather than a scalar -- the rung is selected PER
     * QUANTIFIER BODY (vm_cursor_fits is consulted once per A_REP, at this
     * file's three real call sites), so a pattern with two quantified
     * bodies can and does mix rungs, and a scalar "the rung" would LIE on
     * that case. Named bit constants first (fixed values, independent of
     * this artifact), then the artifact's own OR'd value -- v.rungs is
     * already final here: vm_emit's real walk (above, in the scratch
     * buffer) is the ONLY place vm_rung_mark() runs, so this is the same
     * per-quantifier selection the emitted C actually made, not a second
     * computation of it. The PER-QUANTIFIER detail (which A_REP took which
     * rung) is --emit-ir's RUNGS section, off the same v->rungs-building
     * VE_RUNG events; this macro is deliberately only the summary a
     * build-time #ifdef/grep can act on.
     *
     * rx_info deliberately does NOT gain a member for this at [M4.5e]: the
     * struct's layout is the frozen M4 ABI (match_api_m4.md S5, D44.5's
     * "the layout below is FINAL" ruling), and adding a field is an abi-
     * version-bump event this close does not take on its own -- flagged for
     * the manager rather than done here. */
    sb_printf(c, "#define %s_VM_RUNG_CURSOR           0x%xu\n", v.up, vm_rung_bit[VM_RUNG_CURSOR]);
    sb_printf(c, "#define %s_VM_RUNG_FRAMES_BOUNDED   0x%xu\n", v.up, vm_rung_bit[VM_RUNG_FRAMES_BOUNDED]);
    sb_printf(c, "#define %s_VM_RUNG_FRAMES_UNBOUNDED 0x%xu\n", v.up, vm_rung_bit[VM_RUNG_FRAMES_UNBOUNDED]);
    sb_printf(c, "#define %s_VM_RUNG_REVDET           0x%xu\n", v.up, vm_rung_bit[VM_RUNG_REVDET]);
    sb_printf(c, "#define %s_VM_RUNGS 0x%xu\n", v.up, v.rungs);
    /* [ENG-BREP] the STRATEGY stamp, D46's observability half for the ladder's
     * first rung, in the same shape and the same place and for the same
     * reason: possessification is decided PER A_REP, so an artifact whose
     * quantifiers differ needs a mask.
     *
     * It also carries D47.3's do-or-die half. `-fno-possessify` denies the
     * rewrite, and the way a check knows the denial was honoured is that
     * <PREFIX>_VM_STRAT_POSSESSIVE is absent from this value — not that the
     * flag was passed. A denied strategy appearing in a stamp is a hard test
     * failure, which is testable precisely because the stamp is built from
     * `a->possessive` at the point the emitter acts on it. */
    sb_printf(c, "#define %s_VM_STRAT_POSSESSIVE   0x%xu\n", v.up, vm_strat_bit[VM_STRAT_POSSESSIVE]);
    sb_printf(c, "#define %s_VM_STRAT_BACKTRACKING 0x%xu\n", v.up, vm_strat_bit[VM_STRAT_BACKTRACKING]);
    sb_printf(c, "#define %s_VM_STRATS 0x%xu\n", v.up, v.strats);
    if (v.tracing) {
        sb_puts(c,
            "/* TRACED ARTIFACT (--trace, DD-8/engine_m4.md S10): this matcher\n"
            " * prints every resume-frame push and pop, every capture write,\n"
            " * and its accept/fail to STDERR as it runs. It is a DEBUG build\n"
            " * and nothing else: it writes to stderr, it is not fast, and it\n"
            " * is never what a plain invocation produces. */\n");
        sb_puts(c, "#include <stdio.h>\n");
        sb_printf(c, "#define %s_TRACE 1\n", v.up);
    }
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
        "    struct { const void *k; size_t pos; unsigned mark;%s } bt[%s_BT_FRAMES];\n"
        "    struct { unsigned slot; ptrdiff_t v; }               tr[%s_TRAIL_FRAMES];\n"
        "    unsigned btn, trn;\n",
        v.up, v.tracing ? " int id;" : "", v.up, v.up);
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

    if (!v.tracing) {
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
            "    } while (0)\n"
            /* [ENG-BREP] the possessive CUT. No trail rewind, deliberately —
             * see vm_cut()'s comment: the frames are dead, the capture writes
             * they would have rewound are not. */
            "#define %s_CUT(slot_) do {                                   \\\n"
            "        w->btn = (unsigned)stv[(slot_)];                      \\\n"
            "    } while (0)\n\n",
            v.up, v.up, v.up, v.up, v.up, v.up, v.up, v.up, v.up);
    } else {
        /* The traced forms. Same mechanism, same order of operations, one
         * fprintf each — deliberately NOT a separate implementation: a traced
         * run that took a different path from the untraced one would be a
         * debugging tool that lies, which is worse than none. */
        sb_printf(c,
            "#define %s_TRAIL(slot_) do {                                  \\\n"
            "        if (w->trn >= %s_TRAIL_FRAMES) return %s_R_FRAMES;    \\\n"
            "        w->tr[w->trn].slot = (unsigned)(slot_);               \\\n"
            "        w->tr[w->trn].v = stv[(slot_)];                       \\\n"
            "        w->trn++;                                             \\\n"
            "    } while (0)\n"
            "#define %s_SET(slot_, v_) do {                                \\\n"
            "        fprintf(stderr, \"[%s] set   stv[%%d] %%td -> %%td\\n\",  \\\n"
            "                (int)(slot_), stv[(slot_)], (ptrdiff_t)(v_));  \\\n"
            "        %s_TRAIL(slot_); stv[(slot_)] = (v_);                 \\\n"
            "    } while (0)\n"
            "#define %s_PUSH(id_, lbl_, p_) do {                           \\\n"
            "        if (w->btn >= %s_BT_FRAMES) return %s_R_FRAMES;       \\\n"
            "        w->bt[w->btn].k = (lbl_);                             \\\n"
            "        w->bt[w->btn].pos = (p_);                             \\\n"
            "        w->bt[w->btn].mark = w->trn;                          \\\n"
            "        w->bt[w->btn].id = (id_);                             \\\n"
            "        fprintf(stderr, \"[%s] push  #%%u resume L%%d at pos %%zu"
                        " (trail %%u)\\n\",                                 \\\n"
            "                w->btn, (id_), (size_t)(p_), w->trn);         \\\n"
            "        w->btn++;                                             \\\n"
            "    } while (0)\n"
            "#define %s_CUT(slot_) do {                                   \\\n"
            "        fprintf(stderr, \"[%s] cut   %%u -> %%td frame(s)\\n\",   \\\n"
            "                w->btn, stv[(slot_)]);                        \\\n"
            "        w->btn = (unsigned)stv[(slot_)];                      \\\n"
            "    } while (0)\n\n",
            v.up, v.up, v.up, v.up, v.p, v.up, v.up, v.up, v.up, v.p,
            v.up, v.p);
    }

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
    if (v.rungs & vm_rung_bit[VM_RUNG_CURSOR])
        sb_printf(c, "    size_t %s_cur = 0;   /* the span-loop cursor (engine_m4.md 2.5):\n"
                     "                             a plain local, UNTRAILED, whose save\n"
                     "                             point is a resume frame */\n",
                  v.p);
    /* [ENG-BREP] the reverse-deterministic rung's working locals. All UNTRAILED
     * and all read only where they are provably live: `it`/`mk` inside the
     * forward scan, `c`/`prev`/`ns` inside one commit's own backward walk. What
     * has to survive a backtrack lives in stv (the three slots per loop) or in
     * the resume frame's recorded position, which is where the retreat target
     * rides.
     *
     * The capture-recovery arrays are SHARED across every revdet loop in the
     * program and sized by the widest body, because a walk's results are
     * published into stv before control leaves the loop that ran it — nothing
     * here outlives its own commit. */
    for (int i = 0; i < nrev_total; i++)
        sb_printf(c,
            "    size_t %s_rv%d_c = 0; unsigned long %s_rv%d_it = 0;\n"
            "    unsigned %s_rv%d_mk = 0; ptrdiff_t %s_rv%d_prev = -1;\n"
            "    int %s_rv%d_ns = 0;\n",
            v.p, i, v.p, i, v.p, i, v.p, i, v.p, i);
    if (nrev_total && v.nrevcaps) {
        sb_printf(c, "    ptrdiff_t %s_rvg[%d][2] = {{0}};\n", v.p, v.nrevcaps);
        sb_printf(c, "    unsigned char %s_rvs[%d] = {0};\n", v.p, v.nrevcaps);
    }
    sb_puts(c, "    (void)s; (void)n; (void)stv;\n");
    /* Three of the five per-loop locals are used only by shapes that do not
     * always occur — the walk cursor and `prev` exist only when a walk is
     * emitted, and the seen-counter only when the body has groups — and the
     * generated matcher is built -Wall -Wextra -Werror. `--no-captures` on a
     * possessified rung loop is the combination that has none of them, and it
     * failed -Wunused-variable before this line. `it` and `mk` are used by every
     * shape and are deliberately not listed, so a future shape that stops using
     * one still gets caught. */
    for (int i = 0; i < nrev_total; i++)
        sb_printf(c, "    (void)%s_rv%d_c; (void)%s_rv%d_prev; (void)%s_rv%d_ns;\n",
                  v.p, i, v.p, i, v.p, i);
    if (v.tracing)
        sb_printf(c, "    fprintf(stderr, \"[%s] enter at pos %%zu of %%zu\\n\","
                     " pos, n);\n", v.p);
    sb_printf(c, "    goto %s_L0;\n\n", v.p);
    sb_puts(c, v.b->p ? v.b->p : "");
    /* The three trace lines. Built here rather than inline so the untraced
     * artifact's text is the SAME format string with three empty inserts —
     * one emitted shape, not two, for the same reason the traced macros above
     * keep the untraced order of operations: a debug build that took a
     * different path would be a tool that lies. */
    char accept_tr[160], fail_tr[192], exhaust_tr[128];
    accept_tr[0] = fail_tr[0] = exhaust_tr[0] = 0;
    if (v.tracing) {
        snprintf(accept_tr, sizeof accept_tr,
                 "    fprintf(stderr, \"[%s] ACCEPT [%%zu,%%zu)\\n\","
                 " ctx->pos, pos);\n", v.p);
        snprintf(fail_tr, sizeof fail_tr,
                 "    fprintf(stderr, \"[%s] backtrack: %%u frame(s), trail %%u\\n\","
                 " w->btn, w->trn);\n", v.p);
        /* A separate guarded statement rather than a brace around the
         * existing one: that keeps the UNTRACED artifact's bytes identical
         * (the insert is simply empty), which is what run_vm_identity.sh's
         * gate cares about and what a debug flag has no business changing. */
        snprintf(exhaust_tr, sizeof exhaust_tr,
                 "    if (w->btn == 0)\n"
                 "        fprintf(stderr, \"[%s] FAIL: resume stack empty\\n\");\n",
                 v.p);
    }
    sb_printf(c,
        "\n%s_accept: __attribute__((unused));\n"
        "    /* 3.1: leftmost-first is FIRST COMPLETE MATCH WINS, not compare\n"
        "     * candidates. The VM returns here immediately and the capture\n"
        "     * slots at this instant are the answer — no candidate comparison,\n"
        "     * no longest-wins, no second pass. The caller's caps array is\n"
        "     * filled by the ENTRY, not here (3.4). */\n"
        "%s"
        "    return (ptrdiff_t)(pos - ctx->pos);\n"
        "\n%s_fail: __attribute__((unused));\n"
        "    /* THE ONLY BACKTRACKER AND THE ONLY INDIRECT JUMP.\n"
        "     * A step is one backtrack resumption (4.2), counted at exactly\n"
        "     * this place — so forward progress is FREE (a linear match over\n"
        "     * 100 MB costs zero steps), the budget is subject-length-\n"
        "     * independent, and the counter measures precisely the thing it is\n"
        "     * meant to bound. D22: DD-2 is ROBUSTNESS, not a security\n"
        "     * boundary, and it must not be traded against execution speed. */\n"
        "%s%s"
        "    if (w->btn == 0) return -1;\n",
        v.p, accept_tr, v.p, fail_tr, exhaust_tr);
    if (has_budget)
        sb_printf(c, "    if (--w->budget < 0) return %s_R_STEPS;\n", v.up);
    {
        char pop_tr[224];
        pop_tr[0] = 0;
        if (v.tracing)
            snprintf(pop_tr, sizeof pop_tr,
                     "        fprintf(stderr, \"[%s] pop   #%%u resume L%%d at"
                     " pos %%zu (rewind trail %%u -> %%u)\\n\",\n"
                     "                b_, w->bt[b_].id, pos, w->trn,"
                     " w->bt[b_].mark);\n", v.p);
        sb_printf(c,
            "    {\n"
            "        const unsigned b_ = --w->btn;\n"
            "        pos = w->bt[b_].pos;\n"
            "%s", pop_tr);
    }
    sb_puts(c,
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

    /* [M4.5c] The listing, rendered LAST — the event stream is complete by
     * now, and so are the stamp numbers it reports, which are the same
     * variables the artifact above was stamped from rather than a second
     * computation of them. */
    if (cx->want_ir) {
        VmStamp st;
        st.budget = budget;
        st.bt_frames = bt_frames;
        st.trail_frames = trail_frames;
        st.ceiling = ceiling;
        st.nstate = nstate;
        st.nguard = nguard_total;
        st.nlow = nlow_total;
        st.nmark = nmark_total;
        st.ncaps = ncaps;
        st.has_budget = has_budget;
        st.prefilter = prefn != NULL;
        st.why = job->fit.why;
        vm_render_listing(&v, &job->irsb, &st);
    }
}
