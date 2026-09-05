/* lower_enc.c — [M5.0] THE ENCODING LOWERING: the pass that turns a tree of
 * CODE-POINT classes into a tree the byte tier can express, and the one place
 * in this compiler that knows how an encoding spells a character.
 *
 * Design: docs/design/utf8_design.md §2.1 (where it runs and why), §2.1.2 (the
 * position and the splice-in-place invariant, as corrected by stage-1 ruling
 * R2), §2.1.4 (the render helper this pass makes safe), §2.3 (the
 * byte-sequence construction, built here at stage 2).
 *
 * ============================================================================
 * THE INSTANCES ([M5.0] stage 2)
 * ============================================================================
 *
 * An encoding is a SEALED INSTANCE here exactly as it is a sealed backend at
 * the emitter's seam (src/gen/enc/, DD-12 (7)): one `LowerOps` row per
 * encoding, selected ONCE per compile by id, and no `if (enc == UTF8)`
 * anywhere else in the tree. A row carries the three things an encoding knows
 * about its own spelling of a character:
 *
 *   - `lower_class`: rewrite one leaf `A_CLASS` of code-point intervals into
 *     the byte-level form, or answer NULL for "already byte-level". The BYTE
 *     instance is the identity plus §2.1's confinement rule; the UTF8 instance
 *     is §2.3's range-to-byte-sequence decomposition.
 *   - `identity_max`: the greatest code point whose encoded form is its own
 *     single byte, i.e. the bound below which `lower_class` is the identity.
 *     0xFF for `byte`, 0x7F for `utf8`. Read by the `u.rep.revbody` rule
 *     below, which needs "would the lowering change anything in this subtree"
 *     WITHOUT running it.
 *   - `pat_char`: decode ONE PATTERN CHARACTER at a byte offset — the parser's
 *     literal reader (exported as `pcrec_pat_char`), because a literal byte
 *     >= 0x80 in the pattern text IS a place where the encoding changes the
 *     language (§2.7's rule), and ill-formed pattern text is a compile-time
 *     refusal (§2.6 (a): pcrec owes the refusal; the wording is D26 tier 3).
 *
 * ============================================================================
 * THE POSITION, AND THE INVARIANT THAT REPLACES THE ORDERING ARGUMENT
 * ============================================================================
 *
 * `pcrec_lower_enc` runs at `src/core/compile.c:1000`, between
 * `pcrec_postresolve` and the guarded `pcrec_build_nfa`. Two ordering
 * constraints hold it there:
 *
 *   1. IT MUST RUN BEFORE `pcrec_build_nfa` AND BEFORE `pcrec_emit_vm`.
 *      Those are the two consumers that can only express bytes, and the
 *      second is handed the AST ROOT rather than the IR — which is why
 *      "between the parser and the IR" is not a position at all for the VM
 *      half of this compiler. Getting this wrong is r54 E1: a silent
 *      miscompile, not a refusal.
 *   2. IT MUST RUN AFTER `pcrec_postresolve` (:999), which asks module
 *      `lookaround`'s fixed-width rule in CHARACTERS. After the lowering a
 *      two-byte character is an `A_CAT` of two byte classes, so a
 *      character-width walk over a lowered tree would answer 2 where the
 *      truth is 1.
 *
 * THE THIRD CONSTRAINT IS A PROPERTY, NOT A POSITION (stage-1 lane utf8s1's
 * measurement + manager ruling R2; docs/dev/lanes/utf8s1_report.md §4):
 *
 *   THE INVARIANT — `pcrec_lower_enc` SPLICES IN PLACE. It replaces a leaf
 *   `A_CLASS` by MUTATING THE PARENT'S CHILD POINTER, never by rebuilding
 *   the parent, and it NEVER REALLOCATES A NODE THAT IS OR CONTAINS A GROUP
 *   ROOT.
 *
 * `pcrec_callgraph_build` (:961) caches `u.call.body` — "which subtree is
 * that group's, IN THE TREE THE EMITTER WILL WALK" — so a pass that REBUILDS
 * nodes below the graph strands those pointers (MEASURED: a scratch
 * rebuilding lowering at this position moves 45 of tests/recursion's 179
 * artifacts, the call sites' `W` save/restore emitted EMPTY). A group root is
 * an `A_CAP` node (plus the whole `root` for group 0); a leaf `A_CLASS` is
 * neither; and every node on the path down to a replaced leaf keeps its
 * address — so the graph's bindings stay valid and the pass sits below it.
 *
 * THE INVARIANT IS MECHANICAL AT STAGE 2 (R2's owed check): the ONE write the
 * walk can make is `*slot = repl`, and the write site asserts the node being
 * replaced is a leaf `A_CLASS` — the only kind `lower_class` is ever handed,
 * and a kind that is never a group root and contains nothing. A group root's
 * address therefore cannot move across this pass BY CONSTRUCTION, and the
 * assertion is what turns "by construction" into a diagnosed internal error
 * the day the construction changes. `lower_walk` is handed `Ast **slot` — the
 * ADDRESS of the pointer that holds the current node — so it cannot reach a
 * parent even by accident, and the replacement SUBTREE is new arena nodes
 * that never alias an existing one.
 *
 * THE ROOT IS THE ONE SLOT THAT IS NOT A PARENT'S FIELD, and it is handled by
 * the same mechanism: `pcrec_lower_enc` passes `&root` and returns it, sound
 * for group 0's own `.body` because a pattern whose ROOT is a bare `A_CLASS`
 * has no group construct in it at all — asserted at the bottom of this file
 * rather than argued.
 *
 * ============================================================================
 * `u.rep.revbody` — THE REVERSED COPY, RESOLVED (stage 2; utf8s1 report §4)
 * ============================================================================
 *
 * `src/opt/revdet.c` builds a REVERSED COPY of a quantifier body at
 * compile.c:988 — BEFORE this pass — and stage 1 measured 413 corpus classes
 * reachable only through it. Three facts decide what happens to it here:
 *
 *   (1) REVERSAL AND LOWERING DO NOT COMMUTE. The backward walk reads subject
 *       BYTES right-to-left, so the reversed form of a two-byte character
 *       `CE B1` is the byte sequence `B1 CE` — but `revbody` is reversed at
 *       the CODE-POINT level (a class node reverses to itself), so lowering
 *       the reversed copy would emit `CE B1` where the walk needs `B1 CE`.
 *       "Lower revbody too" is therefore NOT one of the available fixes; it
 *       is a silent wrong-order miscompile.
 *   (2) A subtree the lowering LEAVES ALONE has this problem nowhere: if
 *       every class in the body is confined to `identity_max`, forward and
 *       reversed copies alike are already byte-level and the rung's whole
 *       analysis (run in code-point space that coincides with byte space
 *       below `identity_max`... for `byte`, everywhere) is exact.
 *   (3) Declining a rung is ALWAYS sound and costs a VERDICT, never an
 *       answer (§2.5.1's own rule for the possessify/revdet rows).
 *
 * So the rule, applied at the `A_REP` arm: a quantifier whose body the
 * lowering WOULD CHANGE loses the reverse-deterministic rung — `revbody` is
 * cleared, and the emitter's three agreeing readers (vm_cost_rep,
 * vm_count_slots, vm_rep) all see the ordinary frames/counter rung. Under
 * `--encoding=byte` `identity_max == max_cp`, no class is ever above it, and
 * the clear is UNREACHABLE — which is what keeps the identity gate at 100%
 * without an argument. Under `utf8` the 413-class population is ASCII (the
 * corpus's), below `identity_max`, so every one of those reverse machines is
 * consistent with its forward twin BY IDENTITY; the clear reaches only
 * genuinely non-ASCII bodies, where it trades throughput for correctness.
 *
 * ============================================================================
 *
 * ITERATIVE ON `A_CAT`/`A_ALT` SPINES (D10/DD-10/K20): a flat concatenation is
 * as long as the PATTERN and this project has segfaulted its own compiler on a
 * 20,000-character literal once already. IT DOES NOT FOLLOW `u.call.body` —
 * `src/opt/postresolve.c`'s walk header has the full argument, and both halves
 * apply here: following the back edge does not terminate on a recursive call,
 * and it is redundant because a class inside a called group is visited at its
 * own LEXICAL position by this same walk. */

#include "core/internal.h"
#include "gen/enc/enc.h"

typedef struct LowerCtx LowerCtx;

typedef struct {
    int       id;            /* PCREC_ENC_* */
    unsigned  identity_max;  /* lower_class is the identity at or below this */
    Ast     *(*lower_class)(LowerCtx *lc, Ast *a);
    unsigned (*pat_char)(Ctx *cx, size_t at, int *len);
} LowerOps;

struct LowerCtx {
    Ctx            *cx;
    const LowerOps *ops;
    unsigned        max_cp;  /* the BACKEND's, never a constant here */
};

/* ---- the BYTE instance --------------------------------------------------- */

/* The identity plus §2.1's confinement rule. The error arm is UNREACHABLE by
 * construction — the parser range-checks `\x{...}` on its literal input
 * (§2.7.3) and a complement cannot exceed `max_cp` — which makes it the
 * assertion that those two facts stay true, at the one place that would
 * notice them stopping. */
static Ast *lower_class_byte(LowerCtx *lc, Ast *a)
{
    for (int i = 0; i < a->u.cls.n; i++)
        if (a->u.cls.iv[i].hi > lc->max_cp)
            ctx_fail(lc->cx, 0,
                     "internal error: a class holding code point U+%04X "
                     "survived to the encoding lowering, whose universe ends "
                     "at U+%04X", a->u.cls.iv[i].hi, lc->max_cp);
    return NULL;
}

static unsigned pat_char_byte(Ctx *cx, size_t at, int *len)
{
    *len = 1;
    return (unsigned char)cx->pat[at];
}

/* ---- the UTF8 instance --------------------------------------------------- */

/* Encode `cp` (a scalar value: not a surrogate, <= 0x10FFFF — both excluded
 * by the callers) into b[0..3]; returns the length 1..4. */
static int u8_enc(unsigned cp, unsigned char *b)
{
    if (cp <= 0x7F)   { b[0] = (unsigned char)cp; return 1; }
    if (cp <= 0x7FF)  { b[0] = (unsigned char)(0xC0 | (cp >> 6));
                        b[1] = (unsigned char)(0x80 | (cp & 0x3F)); return 2; }
    if (cp <= 0xFFFF) { b[0] = (unsigned char)(0xE0 | (cp >> 12));
                        b[1] = (unsigned char)(0x80 | ((cp >> 6) & 0x3F));
                        b[2] = (unsigned char)(0x80 | (cp & 0x3F)); return 3; }
    b[0] = (unsigned char)(0xF0 | (cp >> 18));
    b[1] = (unsigned char)(0x80 | ((cp >> 12) & 0x3F));
    b[2] = (unsigned char)(0x80 | ((cp >> 6) & 0x3F));
    b[3] = (unsigned char)(0x80 | (cp & 0x3F));
    return 4;
}

/* A growable list of alternation BRANCHES, arena-backed for cpset.c's own
 * reason: this runs inside a compile that can `ctx_fail` mid-build. */
typedef struct {
    Ctx  *cx;
    Ast **br;
    int   n, cap;
} U8Branches;

static void u8_push_branch(U8Branches *bl, Ast *a)
{
    if (bl->n == bl->cap) {
        int ncap = bl->cap ? bl->cap * 2 : 16;
        Ast **grown = arena_alloc(&bl->cx->arena, (size_t)ncap * sizeof *grown);
        for (int i = 0; i < bl->n; i++) grown[i] = bl->br[i];
        bl->br = grown;
        bl->cap = ncap;
    }
    bl->br[bl->n++] = a;
}

/* One byte-range leaf: an `A_CLASS` whose single interval is a contiguous
 * BYTE range — exactly what src/ir/nfa.c compiles into one N_CLASS state and
 * §2.1.4's render helper accepts without complaint. */
static Ast *u8_byte_class(Ctx *cx, unsigned lo, unsigned hi)
{
    Ast *a = pcrec_ast_node(cx, A_CLASS);
    PcrecCpSet s;
    pcrec_cpset_init(&s, &cx->arena);
    pcrec_cpset_add(&s, lo, hi);
    pcrec_cpset_publish(&s, a);
    return a;
}

/* One SEQUENCE branch from per-position byte ranges: a left-nested `A_CAT`
 * spine of byte-range classes — p_cat's own shape, so nothing downstream
 * meets a new tree geometry. n == 1 is the bare class. */
static Ast *u8_seq(Ctx *cx, const unsigned char *rlo, const unsigned char *rhi,
                   int n)
{
    Ast *res = u8_byte_class(cx, rlo[0], rhi[0]);
    for (int i = 1; i < n; i++) {
        Ast *cat = pcrec_ast_node(cx, A_CAT);
        cat->l = res;
        cat->r = u8_byte_class(cx, rlo[i], rhi[i]);
        res = cat;
    }
    return res;
}

/* Emit branches covering the code-point interval [lo, hi], where both ends
 * encode to the same length `n`. The classic decomposition ([Cox07], [Ragel];
 * §2.3): peel until the low end's suffix is all-minimum and the high end's is
 * all-maximum, at which point the interval is a "box" — an exact byte prefix,
 * one lead range, full continuation ranges — and one branch expresses it.
 * Each recursion pins at least one more suffix byte, so depth is O(n). */
static void u8_box(U8Branches *bl, unsigned lo, unsigned hi, int n)
{
    unsigned char lb[4], hb[4];
    u8_enc(lo, lb);
    u8_enc(hi, hb);

    /* longest common prefix */
    int p = 0;
    while (p < n && lb[p] == hb[p]) p++;

    if (p == n) {               /* lo == hi: one exact sequence */
        u8_push_branch(bl, u8_seq(bl->cx, lb, hb, n));
        return;
    }

    /* If the LOW end's suffix past position p is not all-minimum, split off
     * the largest cp sharing lo's byte at position p: its suffix is all 0xBF
     * (all 0x3F in value bits). */
    bool lo_min = true, hi_max = true;
    for (int i = p + 1; i < n; i++) {
        if (lb[i] != 0x80) lo_min = false;
        if (hb[i] != 0xBF) hi_max = false;
    }
    if (!lo_min) {
        unsigned m = lo | ((1u << (6 * (n - 1 - p))) - 1u);
        u8_box(bl, lo, m, n);
        u8_box(bl, m + 1, hi, n);
        return;
    }
    if (!hi_max) {
        unsigned m = hi & ~((1u << (6 * (n - 1 - p))) - 1u);
        u8_box(bl, lo, m - 1, n);
        u8_box(bl, m, hi, n);
        return;
    }

    /* The box: exact bytes 0..p-1, lead range at p, full ranges after. */
    {
        unsigned char rlo[4], rhi[4];
        for (int i = 0; i < p; i++) { rlo[i] = lb[i]; rhi[i] = lb[i]; }
        rlo[p] = lb[p]; rhi[p] = hb[p];
        for (int i = p + 1; i < n; i++) { rlo[i] = 0x80; rhi[i] = 0xBF; }
        u8_push_branch(bl, u8_seq(bl->cx, rlo, rhi, n));
    }
}

/* Split [lo, hi] at the UTF-8 length boundaries and the surrogate range, then
 * hand each same-length piece to u8_box. The surrogate exclusion is §2.3's:
 * U+D800–U+DFFF have no UTF-8 encoding, so they are simply ABSENT from the
 * automaton — which is where §2.6's "ill-formed matches nothing" comes from,
 * and what sabotage row S-U7 deletes. */
static void u8_ranges(U8Branches *bl, unsigned lo, unsigned hi)
{
    static const struct { unsigned lo, hi; int n; } band[] = {
        { 0x0,     0x7F,     1 },
        { 0x80,    0x7FF,    2 },
        { 0x800,   0xD7FF,   3 },
        /* U+D800–U+DFFF: no encoding — deliberately no band. */
        { 0xE000,  0xFFFF,   3 },
        { 0x10000, 0x10FFFF, 4 },
    };
    for (size_t i = 0; i < sizeof band / sizeof *band; i++) {
        unsigned l = lo > band[i].lo ? lo : band[i].lo;
        unsigned h = hi < band[i].hi ? hi : band[i].hi;
        if (l <= h) u8_box(bl, l, h, band[i].n);
    }
}

/* The UTF8 rewrite of one class node: NULL for a class the byte tier already
 * expresses (every interval at or below 0x7F — the identity fast path that
 * keeps an ASCII pattern's tree untouched, and with it §8.5's expectation
 * that the two encodings' artifacts agree on ASCII by construction), else an
 * `A_ALT` of byte-range sequences covering the set. */
static Ast *lower_class_utf8(LowerCtx *lc, Ast *a)
{
    bool ascii = true;
    for (int i = 0; i < a->u.cls.n; i++)
        if (a->u.cls.iv[i].hi > 0x7F) { ascii = false; break; }
    if (ascii) return NULL;

    for (int i = 0; i < a->u.cls.n; i++)
        if (a->u.cls.iv[i].hi > lc->max_cp)
            ctx_fail(lc->cx, 0,
                     "internal error: a class holding code point U+%04X "
                     "survived to the encoding lowering, whose universe ends "
                     "at U+%04X", a->u.cls.iv[i].hi, lc->max_cp);

    {
        U8Branches bl = { lc->cx, NULL, 0, 0 };
        for (int i = 0; i < a->u.cls.n; i++)
            u8_ranges(&bl, a->u.cls.iv[i].lo, a->u.cls.iv[i].hi);

        if (bl.n == 0) {
            /* Everything fell in the surrogate gap: the set has no encodable
             * member, so the class matches nothing. An empty interval list
             * renders to the all-zero bitmap, which is exactly that. */
            Ast *e = pcrec_ast_node(lc->cx, A_CLASS);
            PcrecCpSet s;
            pcrec_cpset_init(&s, &lc->cx->arena);
            pcrec_cpset_publish(&s, e);
            return e;
        }

        /* Left-nested A_ALT chain, ascending code-point order. The branches
         * are pairwise disjoint on their FIRST byte or share it with disjoint
         * continuations, so preference order cannot matter semantically;
         * ascending is picked for determinism. */
        {
            Ast *res = bl.br[0];
            for (int i = 1; i < bl.n; i++) {
                Ast *alt = pcrec_ast_node(lc->cx, A_ALT);
                alt->l = res;
                alt->r = bl.br[i];
                res = alt;
            }
            /* AN `A_ALT` REPLACEMENT IS SEALED IN AN `A_CAT(A_EMPTY, alt)`
             * WRAPPER, and the wrapper is load-bearing rather than tidy: the
             * spliced node sits in whatever SLOT the leaf sat in, and a slot
             * at the top of a structure whose owner walks its own spine —
             * `vm_look_behind`'s per-branch chain over `u.look.nbranch`
             * parse-time branches is the live one — would read a bare
             * alternation AS more spine. `(?<=[a\x{3b1}])x` compiled to an
             * internal error ("alternation spine is longer than its stored
             * branch count") before this wrapper existed; the two extra
             * nodes emit nothing (`A_EMPTY` is an epsilon in both backends)
             * and keep every enclosing structure's arity what the parse
             * said it was. */
            if (bl.n > 1) {
                Ast *seal = pcrec_ast_node(lc->cx, A_CAT);
                seal->l = pcrec_ast_node(lc->cx, A_EMPTY);
                seal->r = res;
                res = seal;
            }
            return res;
        }
    }
}

static unsigned pat_char_utf8(Ctx *cx, size_t at, int *len)
{
    const unsigned char *p = (const unsigned char *)cx->pat;
    unsigned char b0 = p[at];
    unsigned cp;
    int need;

    if (b0 < 0x80) { *len = 1; return b0; }
    else if ((b0 & 0xE0) == 0xC0) { need = 2; cp = b0 & 0x1Fu; }
    else if ((b0 & 0xF0) == 0xE0) { need = 3; cp = b0 & 0x0Fu; }
    else if ((b0 & 0xF8) == 0xF0) { need = 4; cp = b0 & 0x07u; }
    else
        ctx_fail(cx, at, "ill-formed UTF-8 in pattern: byte 0x%02X cannot "
                         "start a character", b0);

    for (int i = 1; i < need; i++) {
        if (at + (size_t)i >= cx->patlen ||
            (p[at + (size_t)i] & 0xC0) != 0x80)
            ctx_fail(cx, at, "ill-formed UTF-8 in pattern: truncated %d-byte "
                             "character", need);
        cp = (cp << 6) | (p[at + (size_t)i] & 0x3Fu);
    }

    {
        /* The minimum value each length may encode — anything below it is an
         * OVERLONG spelling, which 10.46 refuses in patterns too. */
        static const unsigned min_of[5] = { 0, 0, 0x80, 0x800, 0x10000 };
        if (cp < min_of[need])
            ctx_fail(cx, at, "ill-formed UTF-8 in pattern: overlong encoding");
    }
    if (cp >= 0xD800 && cp <= 0xDFFF)
        ctx_fail(cx, at, "ill-formed UTF-8 in pattern: surrogate code point "
                         "U+%04X", cp);
    if (cp > 0x10FFFF)
        ctx_fail(cx, at, "ill-formed UTF-8 in pattern: code point above "
                         "U+10FFFF");

    *len = need;
    return cp;
}

/* ---- the instance table and its one dispatch ----------------------------- */

static const LowerOps lower_ops[] = {
    { PCREC_ENC_BYTE, 0xFFu, lower_class_byte, pat_char_byte },
    { PCREC_ENC_UTF8, 0x7Fu, lower_class_utf8, pat_char_utf8 },
};

static const LowerOps *ops_for(Ctx *cx)
{
    for (size_t i = 0; i < sizeof lower_ops / sizeof *lower_ops; i++)
        if (lower_ops[i].id == cx->opt->encoding) return &lower_ops[i];
    ctx_fail(cx, 0, "internal error: no lowering instance for encoding id %d "
                    "(the compile gate admitted an encoding this pass does "
                    "not know)", cx->opt->encoding);
    return NULL; /* unreachable */
}

/* THE PARSER'S LITERAL READER (§2.7): decode one pattern character at `at`,
 * report its byte length. Under `byte` this is the byte itself; under `utf8`
 * it is a full UTF-8 decode with compile-time refusals for ill-formed text.
 * Exported for src/parse/parse.c's literal sites — the decode lives HERE
 * because this file is the one place that knows how an encoding spells a
 * character, and a second spelling of that fact in the parser would be the
 * two-decoders drift §5.2.1 already refuses once for `back_step`. */
unsigned pcrec_pat_char(Ctx *cx, size_t at, int *len)
{
    return ops_for(cx)->pat_char(cx, at, len);
}

/* Does the lowering leave every class in this subtree alone? Walked over a
 * DETACHED subtree (`u.rep.revbody`), so unlike `lower_walk` it follows plain
 * child edges and carries no slot. Iterative on spines for the same K20
 * reason; A_CALL is a back edge and stops (a detached reversed body cannot
 * contain one today — revdet declines calls — but the arm costs nothing and
 * the walk must not be the first to find out otherwise). */
static bool subtree_is_identity(const LowerOps *ops, const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS:
            for (int i = 0; i < a->u.cls.n; i++)
                if (a->u.cls.iv[i].hi > ops->identity_max) return false;
            return true;
        case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF: case A_CALL:
            return true;
        case A_CAP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_REP:
            if (a->u.rep.revbody &&
                !subtree_is_identity(ops, a->u.rep.revbody))
                return false;
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            while (a->k == k) {
                if (!subtree_is_identity(ops, a->r)) return false;
                a = a->l;
            }
            continue;
        }
        }
        /* No `default:` — mrl.c:18-24's rule; see lower_walk's twin comment. */
        return true;
    }
}

/* `slot` is the ADDRESS of the pointer holding the current node — its
 * parent's `->l` or `->r`, or `&root` at the top. Writing through it is the
 * whole of the in-place splice, and it is the only write this walk makes
 * besides the `A_REP` arm's revbody clear (a field on a node the walk was
 * handed, never a reallocation). */
static void lower_walk(LowerCtx *lc, Ast **slot)
{
    for (;;) {
        Ast *a = *slot;
        switch (a->k) {
        case A_CLASS: {
            Ast *repl = lc->ops->lower_class(lc, a);
            /* THE SPLICE: one pointer, in a parent this walk never rebuilt.
             * That the replaced node is a LEAF `A_CLASS` — never a group
             * root, containing none — is guaranteed by this arm being the
             * only splice site; the check that makes the guarantee
             * MECHANICAL rather than shape-read is the group-root address
             * signature in `pcrec_lower_enc` below (R2's owed check), which
             * would catch a future arm splicing anything else. */
            if (repl) *slot = repl;
            return;
        }
        case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
        /* THE BACK EDGE STOPS HERE — see this file's header. */
        case A_CALL:
            return;
        case A_REP:
            /* THE `u.rep.revbody` RULE — see the header's own section. The
             * reversed copy was built at code-point level BEFORE this pass;
             * reversal and lowering do not commute, so a body this instance
             * would CHANGE loses the rung rather than gaining a wrong-order
             * reverse machine. Cleared BEFORE descending, so the decision is
             * taken on the same un-lowered view revdet analysed. */
            if (a->u.rep.revbody &&
                !subtree_is_identity(lc->ops, a->u.rep.revbody))
                a->u.rep.revbody = NULL;
            slot = &a->l;
            continue;
        case A_CAP: case A_ATOMIC: case A_LOOK:
            slot = &a->l;
            continue;
        case A_CAT: case A_ALT: {
            /* The spine is walked ITERATIVELY with the slot carried down it,
             * so a 20,000-element concatenation costs no stack (K20). `s`
             * always holds the address of the pointer to the current spine
             * node, and recursion is into the ITEMS only. */
            const AKind k = a->k;
            Ast **s = slot;
            while ((*s)->k == k) {
                Ast *t = *s;
                lower_walk(lc, &t->r);
                s = &t->l;
            }
            slot = s;
            continue;
        }
        }
        /* No `default:` — mrl.c:18-24's rule, and `postresolve.c`'s. A node
         * kind added after this file is written must be a COMPILE ERROR here,
         * because "can this construct CONTAIN a character set" is a question
         * only the author of the new kind can answer and inheriting "no" is
         * the silent wrong answer: it would leave a code-point class in a
         * subtree the emitter then reads as bytes, which is r54 E1 with the
         * lowering present and blind. */
        return;
    }
}

/* THE GROUP-ROOT ADDRESS SIGNATURE (R2's owed stage-2 check): the count of
 * `A_CAP` nodes in the MAIN tree and a mixed hash of their addresses. Taken
 * before and after the pass and compared, it is the splice-in-place invariant
 * as a diagnosed fact rather than a shape a reviewer reads: a lowering that
 * reallocated, dropped or duplicated any group root — the exact staleness
 * that emptied `W` on 45 of tests/recursion's artifacts in the stage-1
 * measurement — changes the signature. It deliberately does NOT follow
 * `u.call.body` (an alias into this same tree — every callee is reached at
 * its lexical position) or `u.rep.revbody` (a DETACHED copy; its `A_CAP`
 * clones are not graph-bound roots, and this pass legitimately clears the
 * field between the two snapshots). */
static void cap_sig(const Ast *a, int *n, uintptr_t *sig)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF: case A_CALL:
            return;
        case A_CAP:
            (*n)++;
            /* Fibonacci-style mix so a swap of two addresses cannot cancel
             * the way a plain XOR of an even multiset would. */
            *sig = (*sig ^ (uintptr_t)a) * (uintptr_t)0x9E3779B97F4A7C15ull;
            a = a->l;
            continue;
        case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            while (a->k == k) {
                cap_sig(a->r, n, sig);
                a = a->l;
            }
            continue;
        }
        }
        return;
    }
}

Ast *pcrec_lower_enc(Ctx *cx, Ast *root)
{
    LowerCtx lc = { cx, ops_for(cx), 0 };
    int cap_n0 = 0, cap_n1 = 0;
    uintptr_t sig0 = 0, sig1 = 0;
    const PcrecEnc *e = pcrec_enc_by_id(cx->opt->encoding);
    if (!e)
        ctx_fail(cx, 0, "internal error: no encoding row for id %d",
                 cx->opt->encoding);
    lc.max_cp = e->max_cp;

    {
        Ast *was = root;
        cap_sig(root, &cap_n0, &sig0);
        lower_walk(&lc, &root);
        cap_sig(root, &cap_n1, &sig1);
        if (cap_n0 != cap_n1 || sig0 != sig1)
            ctx_fail(cx, 0, "internal error: a group root's node address "
                            "moved across the encoding lowering — the "
                            "splice-in-place invariant (R2) is broken "
                            "(%d/%d group roots)", cap_n0, cap_n1);

        /* THE ROOT ASSERTION — the one place the in-place-splice invariant
         * could stop holding, checked rather than argued.
         *
         * Replacing the ROOT is legal only because a pattern whose root is a
         * bare `A_CLASS` contains no group construct, hence no `A_CALL`,
         * hence nothing that captured group 0's `.body` at
         * `pcrec_callgraph_build`. That is a claim about a coincidence of two
         * facts, and coincidences are what stop being true — so it is
         * asserted here, at the moment the root moves. (Reachable at stage 2:
         * `-e utf8 'α'` really does replace the root — with `cx->callgraph`
         * NULL, which is why the conjunction and not the replacement is the
         * error.) */
        if (root != was && cx->callgraph)
            ctx_fail(cx, 0, "internal error: the encoding lowering replaced "
                            "the AST root of a call-bearing pattern — group "
                            "0's cached body now names an abandoned node");
    }
    return root;
}
