/* Possessification — docs/design/eng_brep_design.md §2, the first rung of the
 * [ENG-BREP] bounded-repeat ladder (D47.1: possessify-first, both orders).
 *
 * THE CLAIM. For a precisely characterisable class of quantifiers, no retreat
 * into the loop can ever produce a match the PREFERRED path does not. For
 * those the emitter owes zero resume frames and no giveback: the loop is a
 * forward scan. This pass finds them and marks them (`Ast.u.rep.possessive`);
 * src/gen/emit_vm.c is what acts on the mark.
 *
 * THE RULE (§2.2, as REPAIRED by the R24 panel — read the history below before
 * touching it, because the obvious version of this analysis is measured
 * WRONG). `Q = X{m,n}` is possessive-equivalent when
 *
 *     X admits a UNIQUE ITERATION, X is NOT NULLABLE, and EITHER
 *       - m == n                        (the EXACT-COUNT arm), or
 *       - FIRST(X) is disjoint from FOLLOW(Q)   (the DISJOINTNESS arm)
 *
 * where "admits a unique iteration" is two conditions on the body's position
 * (Glushkov) automaton — (U1) one-unambiguous, (U2) prefix-free — and the
 * disjointness arm carries a LAZY-ONLY conjunct: a lazy `Q` additionally
 * requires that the match cannot also END at the quantifier (everything after
 * `Q`, propagated out to the end of the pattern, is non-nullable).
 *
 * WHY EACH CONJUNCT IS THERE, with the witness that put it there. Every one of
 * these is a MEASURED refutation of a simpler rule somebody believed:
 *
 *   - Disjointness ALONE — the rule as the plan row stated it — is UNSOUND.
 *     117 counterexamples, every one a body like `(a|ab)` whose iteration can
 *     end in two places: `(a|ab){0,4}c` on "abc" is (0,3) greedy and (2,3)
 *     possessive. FIRST is {a}, FOLLOW is {c}, disjoint, and wrong — because
 *     the retreat re-decides the SAME iteration as `ab` and moves the exit
 *     RIGHT rather than left. That is (U1). §2.4.
 *   - (U2) needs no alternation at all: `(?:ab?){0,4}b` on "ab" is (0,2)
 *     greedy and no match possessive. The body is one-unambiguous; its
 *     accepting position `a` (with `b?` empty) simply has an outgoing edge.
 *   - The LAZY conjunct: `a{1,3}?` on "aaaa" is (0,1) lazy and (0,3)
 *     possessive. On a NULLABLE remainder the follow's first-byte test is
 *     vacuous — there is no first byte to test — so a greedy loop is unharmed
 *     (it tops out at the exit chain's top, where the vacuous follow succeeds
 *     anyway) while a lazy loop stops at the BOTTOM of the same chain and
 *     reports a shorter span. 316 measured cells, both oracles agreeing.
 *     [R24 S-F1]
 *   - A zero-width assertion REACHED IN THE FOLLOW breaks the first-set model
 *     outright: `[ab]{0,4}\b` on "abc" is (0,0) greedy and (3,3) possessive,
 *     because `\b` can succeed at a retreat position and fail at the maximal
 *     exit, which is precisely what a first-BYTE set cannot express. So an
 *     assertion in the follow widens FOLLOW to all bytes, i.e. declines. §2.5.
 *     [ART-POSS-ARMS] narrows that for `A_CTX` (arm A, below).
 *
 * THE TWO ARMS ([ART-POSS-ARMS], docs/design/poss_arms.md revision 2.1 — the
 * design of record; every witness below is 10.46-confirmed there). Neither
 * adds a ladder row: each changes what FIRST answers for one node kind.
 *
 *   - ARM A, a context gate in the follow (`-fno-poss-ctx-follow` denies
 *     both halves). An `A_CTX(C, fn)` passes only where the next
 *     character's membership in C is in Q(P) = { q : some p in P, fn(p,q) },
 *     P the possible left polarities; FIRST is S(P), the bytes with that
 *     membership (`pcrec_poss_ctx_admits`), NON-NULLABLE (§2.1: every reader
 *     asks at a retreat exit, where the right character exists).
 *       A0: P = {0,1} — context-free, so read everywhere `first_of` is;
 *           narrows only lookahead-born gates. `[A-Za-z0-9.]+(?=@)`.
 *       A1: P = the polarities of X's Glushkov LAST classes, read only by
 *           row 3 over Q's own continuation (`a1_admits`). Conjuncts, each
 *           a measured refutation: m >= 1 (` \w?\b` on " aa"), polarity
 *           from LAST not FIRST (`(?:a\.)+\b` on "a.a."), a mixed LAST
 *           declines (`(?:a[a.])+\b`), ENCL unioned ungated
 *           (`(?:a+(?:\b|)|ab)+c` on "aabc"), a called group's end unions
 *           its call sites' joined context (`(a+(?:\b|))|b(?1)a` on "baa",
 *           A-F1), and GREEDY ONLY, load-bearing (`(\w+?(?:\b|))` on "ab":
 *           a lazy loop stops at its lowest exit through an empty bypass,
 *           which row 2's may_end catches and A1 would skip, N2).
 *   - ARM B, a backreference's FIRST (`-fno-poss-bref-first`): the union
 *     over every member of refs[] of every A_CAP with that number of the
 *     TEXT the body can begin with (`text_first`: a zero-width item is
 *     (no bytes, nullable) — a gate is in no text, N1's
 *     `(?:((?=a))a)?b+\1b`), folded when the REFERENCE is caseless, and
 *     nullable iff some member body is. Each clause is a refutation
 *     (§3.2's table); `(*ACCEPT)` and MATCH_UNSET_BACKREF have no producer
 *     and are tripwired in tests/registry.
 *
 *   An A1 continuation that disagrees with this walk's FOLLOW is an
 *   INTERNAL ERROR at every verdict (§8.7 R-5), so the two computations of
 *   one set cannot drift silently.
 *
 * `$` IS THE ONE EXEMPTION, AND ITS GATE IS LIVE (D47.5, §2.5, [R24 S-F2]).
 * `$` in the follow is MEASURED safe — 0 of 720 diverging cells — on an
 * upward-closure argument: `$` holds only at the subject end (and before a
 * final newline), which is the top one or two positions, and a retreat moves
 * strictly LEFT, so no retreat position below a failing maximal exit can
 * satisfy it. Under `(?m)` that argument collapses per-line and the same sweep
 * gives 180 of 720 diverging. The exemption is therefore CONDITIONAL, and
 * D47.5 rules the condition a live check rather than a comment. The failing
 * direction is not inert on the same instrument: `\b`/`\B` follows give
 * 332/720 and `^` gives 80/240.
 *
 * THE GATE IS NOW SCOPE-CORRECT TOO ([M6.2] wave A; D62;
 * assertions_design.md §8; D47.5's 2026-08-18 addendum). "Live" is
 * NECESSARY AND NOT SUFFICIENT, and this file is where that was found out.
 * The live read used to be `P.multiline = cx->mods.multiline`, taken once
 * after the parse had finished — i.e. the parser's END-OF-PATTERN option
 * state — while `(?m)` in PCRE2 is SCOPED. Two of the four reachable shapes
 * disagree in the unsound direction: `(?m:a{0,4}$)` and `(?m)a{0,4}$(?-m)`
 * both end the parse with multiline=false and both contain a genuinely
 * multiline `$`, so both would have taken the transparent arm and lost a
 * match the day the `m` letter is accepted (§8.1.1 measures them as cells:
 * correct answer (0,1), possessified answer NO MATCH). The cure is
 * structural rather than a bigger read: multiline is resolved AT PARSE TIME
 * onto the node (`Ast.u.anch.multiline`), this analysis reads the node it is
 * already holding, and `ParseMods` is now an incomplete type outside
 * src/parse/ so no later pass can repeat the mistake (§8.6). `\z` needs no
 * gate at all — see the A_END arm.
 *
 * EVERY SET IS COMPUTED IN THE SOUND DIRECTION. A construct this analysis
 * cannot model widens to "all bytes", which makes the disjointness test fail
 * and the quantifier KEEP its machinery. Declining is always available and
 * always safe; that is the invariant to preserve when extending this file.
 *
 * WHAT THIS IS NOT: a port of `eng_brep_measurements/probes/probe_possess.py`.
 * That probe is the oracle-validated statement of the VERDICT FUNCTION and
 * this file reproduces its decisions, but it models python's parse tree and
 * its byte-set model is UNSOUND for caseless — python folds case at compile
 * time, so the probe computes FIRST((?i)a) = {a} and misses `A` [R24 S-F4].
 * pcrec is exact here STRUCTURALLY and the reason is worth knowing: every
 * literal in pcrec is an A_CLASS, and src/parse/parse.c's `cls_casefold` folds
 * case into the bitmap at PARSE time, so by the time this pass runs a caseless
 * `a` already has both `a` and `A` in it. The analysis below reads those
 * bitmaps directly and is therefore exact where the probe approximates.
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, and K20 the third time). A_CAT and
 * A_ALT spines are LEFT-NESTED and can be as long as the pattern, so every
 * walk here descends the spine ITERATIVELY and recurses only into the items
 * hanging off it, whose depth the parser's own nesting cap bounds. A
 * 20,000-character pattern segfaulted pcrec once already for want of this.
 */

#include <string.h>

#include "core/internal.h"
#include "core/limits.h"
#include "enc/enc.h"

/* ---- byte sets ----------------------------------------------------------
 *
 * 256 bits, the same shape as an A_CLASS bitmap, so `cls_set`/`cls_has` serve
 * both. POSITION sets below use the identical representation over position
 * ids, which is what bounds PSS_MAX_POS at 256. */

/* Zeroes a 256-bit byte set. */
static void bs_clear(uint8_t *s) { memset(s, 0, 32); }
/* Sets every bit of a 256-bit byte set. */
static void bs_all(uint8_t *s)   { memset(s, 0xff, 32); }

/* d |= s, bitwise, over a 256-bit byte set. */
static void bs_or(uint8_t *d, const uint8_t *s)
{
    for (int i = 0; i < 32; i++) d[i] |= s[i];
}

/* True iff `a` and `b` share any set bit. */
static bool bs_intersects(const uint8_t *a, const uint8_t *b)
{
    for (int i = 0; i < 32; i++) if (a[i] & b[i]) return true;
    return false;
}

/* ---- FIRST and NULLABLE (§2.2's first half) ------------------------------
 *
 * FIRST(a) is the set of bytes that can begin `a`; nullable says whether `a`
 * can match empty. Both are needed together because a nullable item does not
 * end the outward propagation — `b?c` contributes BOTH `b` and `c`.
 *
 * The assertion arms are the sound-direction rule made concrete, and they
 * differ for a MEASURED reason rather than a stylistic one: `^` widens to all
 * bytes (80 of 240 diverging cells if it does not), while `$` is transparent
 * when multiline is off (0 of 720) and widens when it is on (180 of 720).
 * `\z` (A_END) is transparent unconditionally — the same argument with a
 * singleton position set and nothing to gate on. Multiline-ness is read off
 * THE NODE, never from the parse state; see the A_EOL arm. */
typedef struct {
    uint8_t f[32];
    bool    nullable;
} First;

/* An empty First value: FIRST = {}, nullable as given. */
static First fst_empty(bool nullable)
{
    First r;
    bs_clear(r.f);
    r.nullable = nullable;
    return r;
}

/* `x` followed by `rest`, as a sequence. The one composition rule the CAT and
 * A_REP arms both fold with. */
static First fst_seq(First x, First rest)
{
    First r = x;
    if (x.nullable) {
        bs_or(r.f, rest.f);
        r.nullable = rest.nullable;
    }
    return r;
}

/* ---- [ART-POSS-ARMS] what FIRST reads beyond the node --------------------
 *
 * One record per walk, so arm B's capture fact and both arms' deny bits live
 * on the walk and never in a file static (§3.1, R-4; [TS-3]'s re-entrancy).
 * [POSS-CTX-TABLE] is where this becomes a context record with a READER
 * field; until then the two readers are two functions, `first_of` (the next
 * character at a POSITION) and `text_first` (the first character of a
 * captured TEXT), and the difference is N1's miscompile. */
typedef struct PossCap PossCap;

typedef struct {
    Ctx     *cx;
    bool     arm_a;     /* A0 + A1; cleared by -fno-poss-ctx-follow */
    bool     arm_b;     /* cleared by -fno-poss-bref-first */
    PossCap *cap;       /* arm B's capture fact; NULL when arm_b is off */
    /* Did an arm NARROW an answer on this walk? Only then can its stamp
     * bit be set, so only then does `pcrec_possessify` pay the counterfactual
     * walk that decides it. */
    bool     a0_used, b_used;
} Fq;

static First first_of(Fq *q, const Ast *a);

/* S(P) for the gate `(fn, C)`: the bytes whose membership in C some left
 * polarity in `pmask` (bit 0: not in C, bit 1: in C) lets `fn` pass, into
 * `out`. False means NO NARROWING — Q(P) admits both memberships, or §2.1's
 * truncation rule widens because Q(P) is non-empty while S(P), cut at 0xFF,
 * came out empty. A true return with `out` empty is exact: the gate never
 * passes (`\w+(?<!\w)`). Exported for its exhaustive model check
 * (tests/possessify/ctx_admits_check.c); this file is its only reader. */
bool pcrec_poss_ctx_admits(uint8_t fn, const PcrecCpRange *iv, int n,
                           unsigned pmask, uint8_t out[32])
{
    bool qok[2] = { false, false };
    for (unsigned p = 0; p < 2; p++) {
        if (!(pmask & (1u << p))) continue;
        for (unsigned qv = 0; qv < 2; qv++)
            if (fn & (1u << ((p << 1) | qv))) qok[qv] = true;
    }
    if (qok[0] && qok[1]) return false;
    bs_clear(out);
    if (!qok[0] && !qok[1]) return true;
    /* One walk over the sorted intervals marks the bytes IN C; the
     * admitted side is that set or its complement within the byte tier. */
    uint8_t in[32];
    bs_clear(in);
    for (int i = 0; i < n && iv[i].lo <= 0xFFu; i++) {
        unsigned hi = iv[i].hi > 0xFFu ? 0xFFu : iv[i].hi;
        for (unsigned c = iv[i].lo; c <= hi; c++) cls_set(in, c);
    }
    bool any = false;
    for (int i = 0; i < 32; i++) {
        out[i] = qok[1] ? in[i] : (uint8_t)~in[i];
        if (out[i]) any = true;
    }
    return any;
}

/* A gate's S(P) for the node `g`. */
static bool ctx_admits(const Ast *g, unsigned pmask, uint8_t out[32])
{
    return pcrec_poss_ctx_admits(g->u.ctx.fn, g->u.ctx.iv, g->u.ctx.n,
                                 pmask, out);
}

/* ---- [ART-POSS-ARMS] arm B's capture fact (§3.1, R-4) ------------------
 *
 * CAP(g), the union of TEXT_FIRST over every A_CAP numbered g, computed ONCE
 * PER GROUP NUMBER: one walk indexes every A_CAP by number (lookaround and
 * DEFINE bodies included — the number is the key, as in K93's `cc[]`, so
 * `(?|` is correct on arrival), and each value is memoized. A group asked
 * again while IN PROGRESS (a reference cycle, `(a\2)(b\1)`) answers WIDEN,
 * and so does a resolution deeper than PCREC_MAX_POSS_REF_DEPTH, which bounds
 * this fold's C stack on a pattern-shaped reference chain (D10/K20). Both
 * are the sound direction. */
enum { CF_UNKNOWN, CF_BUSY, CF_DONE };

struct PossCap {
    int          ncap;      /* slots 1..ncap */
    int         *cnt;       /* per number: how many A_CAP nodes */
    const Ast ***caps;      /* per number: those nodes */
    uint8_t     *state;     /* CF_* */
    First       *val;
    int          depth;     /* cap_group recursion in progress */
};

/* Counts (`fill` false) or records (`fill` true) every A_CAP under `a` by
 * number. A whole-tree walk: it does not follow a call's back edge, and it
 * is iterative on the spine (atomic.c:22-36). */
static void cap_index(PossCap *F, const Ast *a, bool fill)
{
    while (a) {
        switch (a->k) {
        case A_CAP: {
            int no = a->u.cap.no;
            if (no >= 1 && no <= F->ncap) {
                if (fill) F->caps[no][F->cnt[no]] = a;
                F->cnt[no]++;
            }
            a = a->l;
            continue;
        }
        case A_CAT: case A_ALT:
            cap_index(F, a->r, fill);
            a = a->l;
            continue;
        case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CLASS: case A_WCLASS: case A_EMPTY: case A_BOL: case A_EOL:
        case A_END: case A_CTX: case A_GSTART: case A_KRESET: case A_BREF:
        case A_VAR:
        /* a call's body is the AST's back edge; its A_CAP is visited at its
         * own lexical position */
        case A_CALL:
            return;
        }
        return;
    }
}

/* Builds the capture fact for `root`: two index walks (count, then fill). */
static PossCap *cap_build(Ctx *cx, const Ast *root)
{
    PossCap *F = pcrec_arena_alloc(&cx->arena, sizeof *F);
    F->ncap  = (int)cx->ncap;
    size_t n = (size_t)F->ncap + 1;
    F->cnt   = pcrec_arena_alloc(&cx->arena, n * sizeof *F->cnt);
    F->caps  = pcrec_arena_alloc(&cx->arena, n * sizeof *F->caps);
    F->state = pcrec_arena_alloc(&cx->arena, n * sizeof *F->state);
    F->val   = pcrec_arena_alloc(&cx->arena, n * sizeof *F->val);
    cap_index(F, root, false);
    for (size_t g = 0; g < n; g++) {
        if (F->cnt[g])
            F->caps[g] = pcrec_arena_alloc(&cx->arena,
                                           (size_t)F->cnt[g] * sizeof **F->caps);
        F->cnt[g] = 0;
    }
    cap_index(F, root, true);
    return F;
}

static First text_first(Fq *q, const Ast *a);

/* CAP(g) into `*out`; false = WIDEN (in progress, or past the depth bound).
 * A number with no A_CAP answers the empty, non-nullable set: a reference
 * to it always fails. */
static bool cap_group(Fq *q, int g, First *out)
{
    PossCap *F = q->cap;
    if (g < 1 || g > F->ncap) return false;
    if (F->state[g] == CF_DONE) { *out = F->val[g]; return true; }
    if (F->state[g] == CF_BUSY) return false;
    if (F->depth >= PCREC_MAX_POSS_REF_DEPTH) return false;
    F->state[g] = CF_BUSY;
    F->depth++;
    First acc = fst_empty(false);
    for (int i = 0; i < F->cnt[g]; i++) {
        First f = text_first(q, F->caps[g][i]->l);
        bs_or(acc.f, f.f);
        acc.nullable = acc.nullable || f.nullable;
    }
    F->depth--;
    F->val[g]   = acc;
    F->state[g] = CF_DONE;
    *out = acc;
    return true;
}

/* "Which character can a captured TEXT begin with" (N1, §3.1) — `first_of`'s
 * fold with every ZERO-WIDTH kind answering (no bytes, nullable): a gate,
 * an anchor or `\K` contributes no character to a text, so this is exact.
 * Every consuming kind defers to `first_of`, whose A_BREF arm re-enters the
 * capture fact. Recursion is the parser's nesting plus the reference depth
 * bound; spines are iterative. */
static First text_first(Fq *q, const Ast *a)
{
    switch (a->k) {
    case A_EMPTY: case A_BOL: case A_EOL: case A_END: case A_CTX:
    case A_GSTART: case A_KRESET: case A_LOOK:
        return fst_empty(true);
    case A_CAP: case A_ATOMIC:
        return text_first(q, a->l);
    case A_CAT: {
        First acc = fst_empty(true);
        const Ast *t = a;
        while (t->k == A_CAT) {
            acc = fst_seq(text_first(q, t->r), acc);
            t = t->l;
        }
        return fst_seq(text_first(q, t), acc);
    }
    case A_ALT: {
        First acc = fst_empty(false);
        const Ast *t = a;
        for (;;) {
            const Ast *br = t->k == A_ALT ? t->r : t;
            First r = text_first(q, br);
            bs_or(acc.f, r.f);
            acc.nullable = acc.nullable || r.nullable;
            if (t->k != A_ALT) break;
            t = t->l;
        }
        return acc;
    }
    case A_REP: {
        First r = text_first(q, a->l);
        r.nullable = r.nullable || a->u.rep.rmin == 0;
        return r;
    }
    case A_CLASS: case A_WCLASS: case A_BREF: case A_CALL: case A_VAR:
        return first_of(q, a);
    }
    return first_of(q, a);   /* unreachable: every AKind is listed */
}

/* Closes `f` under the fold relation the CASELESS SPAN COMPARE of a
 * reference with `ucp` in force uses (`pcrec_enc_span_fold`, the relation
 * the seam is generated from), widening to all bytes when a partner falls
 * outside the byte tier (`k` -> U+212A under utf8). */
static void bref_fold(Ctx *cx, bool ucp, uint8_t f[32])
{
    const PcrecFold *rel =
        pcrec_enc_span_fold(pcrec_enc_by_id(cx->opt->encoding), ucp);
    PcrecCpSet in, out;
    pcrec_cpset_init(&in, &cx->arena);
    pcrec_cpset_init(&out, &cx->arena);
    pcrec_cpset_add_bits(&in, f);
    rel->partners(&in, &out);
    for (int i = 0; i < out.n; i++) {
        if (out.iv[i].hi > 0xFFu) { bs_all(f); return; }
        for (unsigned c = out.iv[i].lo; c <= out.iv[i].hi; c++) cls_set(f, c);
    }
}

/* Arm B: FIRST(\n) = fold_ref(union over refs[] of CAP(g)), nullable iff a
 * member body is; false = WIDEN (some member is in progress or too deep).
 * An unset member contributes nothing, because a reference to it fails
 * (PCRE2_MATCH_UNSET_BACKREF has no producer; tests/registry tripwires it). */
static bool bref_first(Fq *q, const Ast *a, First *out)
{
    First acc = fst_empty(false);
    for (int i = 0; i < a->u.bref.nrefs; i++) {
        First v;
        if (!cap_group(q, a->u.bref.refs[i], &v)) return false;
        bs_or(acc.f, v.f);
        acc.nullable = acc.nullable || v.nullable;
    }
    if (a->u.bref.caseless) bref_fold(q->cx, a->u.bref.ucp, acc.f);
    *out = acc;
    return true;
}

/* The byte SET that can begin whatever runs from a position at `a`, plus
 * whether `a` can match empty — the NEXT CHARACTER AT A POSITION, which is
 * what every reader here asks about (a captured text's first character is
 * `text_first`'s question, and the two differ at a gate). A structural fold
 * over `a`, walked TRANSPARENTLY through A_CAP/A_ATOMIC (a bracketing
 * construct's FIRST is its body's); it reads the walk's arms and arm B's
 * memo from `q` and writes only that memo and the `*_used` flags. Every set
 * is computed in the SOUND direction: anything unmodellable (a wide class, a
 * call) widens to ALL BYTES rather than refusing, which can only cost a
 * possessification, never a wrong answer. Feeds §2.2's disjointness test in
 * `pss_walk` below. */
static First first_of(Fq *q, const Ast *a)
{
    switch (a->k) {
    /* [CLS-TREE] S3 (D-1): above the encoding lowering, so never
     * met; LOUD, because this arm would read the set as bytes. */
    case A_WCLASS:
        pcrec_wcls_misplaced(q->cx, "first_of");
    case A_CLASS: {
        First r;
        /* [M5.0 stage 1] §2.5.1's DECLINE row 4. This pass runs inside
         * `pcrec_select_engine` (compile.c:988), ABOVE the encoding lowering
         * at :1000, so the class carries CODE POINTS — and a node reaching
         * outside the byte range widens to ALL BYTES rather than refusing.
         * That makes the disjointness test harder to satisfy, so the cost is a
         * lost possessification and never a wrong answer; under
         * `--encoding=byte` no interval can exceed 0xFF and the cost is zero,
         * which is why the identity gate still reads 100%. */
        pcrec_cls_bits_widen(q->cx, a, r.f);
        r.nullable = false;
        return r;
    }
    /* [M6.5.2] A BACKREFERENCE WIDENS TO EVERY BYTE AND IS NULLABLE — the
     * maximally conservative answer, and the one this analysis's own safe
     * direction demands.
     *
     * `first_of` feeds the §2.2 follow-set disjointness test, and this
     * analysis is UNSOUND when it under-states what a construct can match: a
     * FIRST set that is too small makes two sets look disjoint, possessifies a
     * quantifier whose retreat is the only way to the match, and deletes it
     * silently. A backreference's first byte is whatever the referenced group
     * captured, which is not a compile-time fact at all, so the only honest
     * answer is "any of the 256". NULLABLE because an empty capture makes the
     * whole construct consume nothing.
     *
     * That combination makes every disjointness test involving it FAIL, so a
     * quantifier near a backreference keeps its machinery — the direction
     * `pcrec_revdet_first` already takes for `$`, and the direction this file
     * is allowed to be wrong in.
     *
     * [ART-POSS-ARMS] ARM B makes it a compile-time fact after all: every
     * value a published capture can hold is a string some A_CAP with that
     * number matched, so FIRST(\n) is the union of those bodies' TEXT firsts
     * (`bref_first`, §3.1). The widen above stays the answer when the arm is
     * denied, and for a member in progress or past the depth bound. */
    case A_BREF: {
        First r;
        if (q->arm_b && q->cap && bref_first(q, a, &r)) {
            q->b_used = true;
            return r;
        }
        memset(r.f, 0xff, 32);
        r.nullable = true;
        return r;
    }
    case A_VAR: {
        First r;
        memset(r.f, 0xff, 32);
        r.nullable = true;
        return r;
    }
    /* [M6.6.2] A LOOKAROUND WIDENS TO EVERY BYTE AND IS NULLABLE — the same
     * maximally conservative answer `A_BREF` gets, reached differently.
     *
     * NULLABLE is the LITERAL truth: a lookaround consumes nothing on every
     * path. The widening is the conservative half, and it is the half that
     * matters. This analysis is UNSOUND when it under-states what a construct
     * admits: a FIRST set that is too small makes two sets look disjoint,
     * possessifies a quantifier whose retreat is the only route to the match,
     * and deletes it silently. A lookaround is a GATE — it decides which
     * continuations are live without contributing a byte of its own — and this
     * representation has no way to express a gate at all. `fst_empty(true)`
     * would model it as ABSENT, which is exactly the under-statement the file
     * is not allowed to make.
     *
     * The combination makes every disjointness test that meets one FAIL, so a
     * quantifier near a lookaround keeps its machinery. That is the direction
     * `pcrec_revdet_first` already takes for `$` and the one this file is
     * allowed to be wrong in. Note the arm does not read the body: a body that
     * cannot match makes the assertion FAIL rather than making it narrower,
     * and "0xff plus nullable" already dominates whatever the body would
     * contribute. */
    case A_LOOK: {
        First r;
        memset(r.f, 0xff, 32);
        r.nullable = true;
        return r;
    }
    /* [DD-14] A SUBROUTINE CALL WIDENS TO EVERY BYTE AND IS NULLABLE — the
     * same maximally conservative answer `A_BREF` and `A_LOOK` get, and
     * design §4.4a site 19 is explicit that the EXACT answer here (the
     * callee's own FIRST set) is a wave-G OPTIMISATION and not a correctness
     * need.
     *
     * WIDENING IS THE SOUND HALF. This analysis is unsound when it
     * UNDER-states what a construct admits: a FIRST set that is too small
     * makes two sets look disjoint, possessifies a quantifier whose retreat is
     * the only route to the match, and deletes it silently. A call runs
     * another group's whole pattern, so its first byte is that group's — a
     * fact this node cannot reach without the call graph, and one that does
     * not exist at all for a left-recursive callee.
     *
     * NULLABLE IS THE CONSERVATIVE HALF HERE, not the literal truth, and the
     * two differ for this kind in a way they do not for `A_LOOK`. A call
     * consumes exactly what its callee consumes, which may well be positive;
     * claiming nullable makes the enclosing concatenation's FIRST set include
     * whatever FOLLOWS the call as well, which widens further in the same safe
     * direction. `pcrec_nullable`'s own arm is the SCC fixpoint (§2.6) and is a
     * different question asked for a different consumer — the empty-iteration
     * guard — so the two are allowed to disagree, and this comment is the
     * record that the disagreement is deliberate.
     *
     * IT DOES NOT READ `u.call.body`: 0xff-plus-nullable already dominates
     * anything the callee could contribute, and following the back edge in a
     * function that recurses on `A_CAT`/`A_ALT` with no visited set is design
     * §4.4's hang. */
    case A_CALL: {
        First r;
        memset(r.f, 0xff, 32);
        r.nullable = true;
        return r;
    }
    case A_EMPTY:
    /* [M6.2 wave E] `\K` takes A_EMPTY's arm, and it is the ONE arm in this
     * switch that needs no closure argument at all.
     *
     * Every other zero-width kind here had to be classified by WHICH WAY its
     * satisfying set is closed, because each of them can FAIL and the whole
     * question is whether a retreat can turn a failure into a success. `\K`
     * cannot fail. It is an epsilon in the NFA (src/ir/nfa.c), so it is
     * absent from the language this analysis reasons about, and "modelled as
     * absent" is not an approximation here — it is the fact.
     *
     * WHAT THIS DOES NOT SAY, spelled out because it is the tempting wrong
     * worry: possessifying a loop that CONTAINS a `\K` is also safe, and not
     * because `\K` is invisible. The cut discards retreat frames only after
     * the loop has exited at its chosen count, and a trial iteration that
     * failed has already had its `\K` write rewound by the fail label's trail
     * rewind. So the writes that survive a cut are exactly the winning path's,
     * which is what PCRE2 reports. `(?:a\K)*ab` on "aaab" is the cell that
     * would expose an error here, and possessification DECLINES it anyway
     * (body and follow both start with `a`), which is why the corpus carries
     * both it and a shape that does possessify. */
    case A_KRESET:
        return fst_empty(true);

    case A_BOL: {
        /* `^` is DOWNWARD-closed where `$` is upward-closed: it holds only at
         * offset 0, so a retreat can reach a position satisfying it from one
         * that does not. Widen and decline. */
        First r;
        bs_all(r.f);
        r.nullable = false;
        return r;
    }
    case A_EOL:
        /* D47.5's LIVE GATE, AND IT READS THE NODE ([M6.2] wave A, D62,
         * assertions_design.md §8). Transparent while `$` means "the subject
         * end (or before a final newline)" — a set no retreat can reach from
         * further left; all bytes once `(?m)` makes it true before every
         * newline.
         *
         * `a->u.anch.multiline` and NOT `cx->mods`. This arm used to consult a bool
         * captured once for the whole pass, from the parser's END-OF-PATTERN
         * option state, and `(?m)` is SCOPED: `(?m:a{0,4}$)` and
         * `(?m)a{0,4}$(?-m)` each read false there while their `$` is
         * genuinely multiline, so each would have taken the transparent arm
         * and possessified a quantifier whose retreat is the only route to
         * the match. Two measured lost-match cells (§8.1.1); D47.5's own
         * recorded obligation names only the leading-`(?m)` shape, the one
         * the old code got right. The fact now lives on the node, resolved
         * at the `$` itself, and this analysis reads the node it is already
         * holding — which is also why no threading of scoped state through
         * `pss_walk` was needed (§8.5). */
        if (a->u.anch.multiline) {
            First r;
            bs_all(r.f);
            r.nullable = false;
            return r;
        }
        return fst_empty(true);

    case A_END:
        /* [M6.2 wave A] `\z` is the exemption's own argument, sharpened.
         * `$`'s satisfying set is {n} plus {n-1} before a final newline, and
         * the upward-closure argument has to reason about that second
         * position; `\z`'s is the SINGLETON {n}. If `\z` fails at a
         * quantifier's maximal exit it fails at every retreat position, since
         * every retreat position is strictly smaller. Transparent, and
         * UNCONDITIONALLY so — no option makes `\z` true anywhere else, which
         * is exactly why it is a separate node kind and not a flag on
         * A_EOL. */
        return fst_empty(true);

    case A_GSTART:
        /* [M6.2 wave D] WIDEN AND DECLINE, and `\G` takes `^`'s arm for
         * `^`'s exact reason rather than `\z`'s.
         *
         * The exemption below rests on UPWARD CLOSURE: if the assertion fails
         * at a quantifier's maximal exit it fails at every smaller retreat
         * position too, so the retreat cannot rescue a match. `\G` is
         * DOWNWARD-closed, like `^` two arms up — it holds at exactly one
         * position, `startpos`, and every retreat moves TOWARD it. So a
         * retreat can reach a position satisfying `\G` from one that does
         * not, which is precisely the case possessification would delete.
         *
         * The witness is `a{0,4}\G` at `startpos == 0` on `"aaaa"`: the
         * maximal exit is 4, `\G` fails there, and the retreat to 0 is the
         * only route to the correct `(0,0)`. Possessified, that pattern
         * answers no match at every start. Widen to all bytes and decline —
         * always available, always safe, this file's standing invariant. */
        {
            First r;
            bs_all(r.f);
            r.nullable = false;
            return r;
        }

    case A_CTX:
        /* [M6.2 wave B] WIDEN AND DECLINE, and this is NOT the treatment
         * `\z`/`$` get one arm up -- it is `^`'s.
         *
         * The exemption above rests on UPWARD CLOSURE: if `$` fails at a
         * quantifier's maximal exit it fails at every smaller retreat
         * position too, so the retreat cannot rescue a match and possessifying
         * loses nothing. A word boundary is closed in NEITHER direction,
         * because its truth is a property of the two bytes around the
         * position rather than of the position's rank. `\w{0,4}\b` on
         * "abcd" is the witness in one direction: the maximal exit at 4 is a
         * boundary (end of subject) and the retreat position 3 is not, so
         * `\b` holding at the top says nothing about the retreat; `\B`
         * inverts it. Both belong with `^`, which widens to all bytes and
         * declines.
         *
         * [ART-POSS-ARMS] A0: that holds for a gate whose truth depends on
         * the LEFT character. Knowing nothing about it (P = {0,1}), a gate
         * still passes only where the next character's membership is in
         * Q({0,1}); a lookahead-born gate ignores the left, so it narrows to
         * S = C or its complement (§2.1, `[A-Za-z0-9.]+(?=@)`). Non-nullable
         * either way, which is the shipped value. `\b`/`\B` and the
         * lookbehinds get nothing here — Q({0,1}) is both memberships — and
         * are A1's, which knows the left (`pss_verdict`). */
        {
            First r;
            r.nullable = false;
            if (q->arm_a && ctx_admits(a, 3u, r.f)) {
                q->a0_used = true;
                return r;
            }
            bs_all(r.f);
            return r;
        }

    case A_CAP:
    /* [M6.4.2] TRANSPARENT: FIRST is a property of the bytes a node can BEGIN
     * with, and a cut removes whole matches rather than first bytes — every
     * string `(?>X)` matches is one `X` matches, so FIRST(X) is a sound (and
     * here exact) super-set. It is A_CAP's arm because it is A_CAP's answer.
     *
     * SOUND BUT MEASURABLY INCOMPLETE, and that is worth knowing rather than
     * hiding: an atomic group is EXACTLY a unique-match guarantee, so a §2.2
     * that understood `A_ATOMIC` instead of seeing through it would accept
     * every one of the 8,820 patterns in `probe_puc_targeted.py`'s
     * "quantifier WRAPPING the atomic group" position, where transparency
     * accepts 0. Declining is always safe (this file's own invariant), so
     * that is an opportunity and not a defect, and [M6.4.2] deliberately does
     * not take it — the transparency is what §6.4a's 776,160-cell sweep was
     * measured over. */
    case A_ATOMIC:
        return first_of(q, a->l);

    case A_CAT: {
        /* The spine is left-nested, so walking it from the top visits the
         * sequence RIGHT TO LEFT — which is the direction this fold wants:
         * each step composes one item in front of the suffix already folded.
         * Iterative on the spine (see the recursion-discipline note above). */
        First acc = fst_empty(true);          /* the empty suffix */
        const Ast *t = a;
        while (t->k == A_CAT) {
            acc = fst_seq(first_of(q, t->r), acc);
            t = t->l;
        }
        return fst_seq(first_of(q, t), acc);
    }
    case A_ALT: {
        /* Union of the branches; order-independent, so a plain spine walk. */
        First acc = fst_empty(false);
        const Ast *t = a;
        while (t->k == A_ALT) {
            First r = first_of(q, t->r);
            bs_or(acc.f, r.f);
            acc.nullable = acc.nullable || r.nullable;
            t = t->l;
        }
        First h = first_of(q, t);
        bs_or(acc.f, h.f);
        acc.nullable = acc.nullable || h.nullable;
        return acc;
    }
    case A_REP: {
        First r = first_of(q, a->l);
        r.nullable = r.nullable || a->u.rep.rmin == 0;
        return r;
    }
    }
    /* Unreachable today: every AKind is handled. A future node kind lands here
     * and widens, which declines rather than guesses. */
    {
        First r;
        bs_all(r.f);
        r.nullable = true;
        return r;
    }
}

/* ---- (U1) one-unambiguity and (U2) prefix-freeness -----------------------
 *
 * Both are decided on the body's GLUSHKOV (position) automaton: positions are
 * the byte-consuming leaves — in pcrec, exactly the A_CLASS nodes — and the
 * expression is ONE-UNAMBIGUOUS when the initial position set and every
 * position's follow set are pairwise byte-disjoint. Equivalently: at most one
 * position is live after any prefix. It is prefix-free when no ACCEPTING
 * position has an outgoing edge, so no proper prefix of an iteration is
 * itself a complete iteration.
 *
 * Together with non-nullability these give §2.3's chain: from any start at
 * most one iteration can run and it has exactly one end, so the loop's
 * reachable exits form a strictly increasing chain determined by the start.
 * That chain is the premise the whole soundness argument rests on, and it is
 * the premise disjointness-alone silently assumed.
 *
 * PAIRWISE DISJOINTNESS IS CHECKED INCREMENTALLY. A family of sets is pairwise
 * disjoint iff each member is disjoint from the union of those before it, so
 * `funion` accumulates and `fconflict` records the first overlap. That also
 * reproduces the reference probe's treatment of a DUPLICATED edge (the same
 * successor linked twice reads as an overlap and declines), which is
 * conservative and deliberate.
 *
 * ASSERTIONS INSIDE THE BODY ARE TRANSPARENT here, and that is sound in the
 * direction it needs to be [R24 H4, 1,512 pairs, 0 diverging]. Dropping an
 * assertion OVER-approximates the body's language, and both properties this
 * function tests are inherited downward: if the over-approximation admits at
 * most one end from any start, so does every subset of it, and if the
 * over-approximation is non-nullable so is the subset. The argument does not
 * depend on the multiline state, which is why this half has no gate while
 * first_of does. */

enum {
    PSS_MAX_POS = PCREC_MAX_POSSESS_POSITIONS  /* == the position-set width */
};

typedef struct {
    Ctx    *cx;                       /* the compile, for a loud refusal */
    int     npos;
    bool    ok;                       /* cleared by anything unmodellable */
    uint8_t set[PSS_MAX_POS][32];     /* position -> its byte set */
    uint8_t funion[PSS_MAX_POS][32];  /* position -> union of its successors' */
    bool    fconflict[PSS_MAX_POS];   /* ... and whether two of them overlapped */
    bool    hasfollow[PSS_MAX_POS];   /* (U2): does it have any successor */
    /* [ART-POSS-ARMS] A1 reads the classes at the body's LAST positions:
     * each position's A_CLASS (code points, folded at parse time) and the
     * LAST set of the body `body_admits_unique_iteration` last built. */
    const Ast *cls[PSS_MAX_POS];
    uint8_t    last[32];
} Gk;

/* first/last as POSITION sets, sharing the 256-bit representation. Keeping
 * them as sets rather than lists is what keeps a build frame at 65 bytes, so
 * the recursion into nested items costs bytes rather than kilobytes. */
typedef struct {
    uint8_t first[32], last[32];
    bool    nullable;
} GkParts;

/* An empty GkParts value: first/last = {}, nullable as given. */
static GkParts gk_parts_empty(bool nullable)
{
    GkParts p;
    bs_clear(p.first);
    bs_clear(p.last);
    p.nullable = nullable;
    return p;
}

/* Interns a new Glushkov position for byte-set `bytes` (the class `cls`) in `g`, or fails
 * (`g->ok = false`) past PSS_MAX_POS; initializes its
 * follow-union/conflict/hasfollow slots empty. */
static int gk_newpos(Gk *g, const uint8_t *bytes, const Ast *cls)
{
    if (g->npos >= PSS_MAX_POS) { g->ok = false; return -1; }
    int p = g->npos++;
    g->cls[p] = cls;
    memcpy(g->set[p], bytes, 32);
    bs_clear(g->funion[p]);
    g->fconflict[p] = false;
    g->hasfollow[p] = false;
    return p;
}

/* Wires FOLLOW for every position pair (p in `lasts`, q in `firsts`): unions
 * q's byte set into p's follow-union and marks a conflict if it already
 * intersected. */
static void gk_link(Gk *g, const uint8_t *lasts, const uint8_t *firsts)
{
    for (int p = 0; p < g->npos; p++) {
        if (!cls_has(lasts, (unsigned)p)) continue;
        for (int q = 0; q < g->npos; q++) {
            if (!cls_has(firsts, (unsigned)q)) continue;
            g->hasfollow[p] = true;
            if (bs_intersects(g->set[q], g->funion[p])) g->fconflict[p] = true;
            bs_or(g->funion[p], g->set[q]);
        }
    }
}

/* Builds `a`'s fragment of the Glushkov position automaton `g` accumulates:
 * one interned POSITION per leaf byte-set, with the fragment's own FIRST
 * and LAST position sets returned so the caller can wire them into the
 * enclosing construct. This is what `pss_walk`'s (U1)/(U2) unique-iteration
 * test runs over. `g->ok` false means an earlier subtree already declined
 * the whole construction (a backreference, a wide class outside the byte
 * range, or the position budget) — every arm checks it first and refuses to
 * add positions to a build that has already given up. */
static GkParts gk_build(Gk *g, const Ast *a)
{
    if (!g->ok) return gk_parts_empty(true);

    switch (a->k) {
    /* [CLS-TREE] S3 (D-1): above the encoding lowering, so never
     * met; LOUD, because this arm would read the set as bytes. */
    case A_WCLASS:
        pcrec_wcls_misplaced(g->cx, "gk_build");
    case A_CLASS: {
        /* [M5.0 stage 1] §2.5.1's DECLINE row 5, `first_of`'s argument
         * verbatim one rung down: a Glushkov position's LABEL is a byte set,
         * and a class reaching outside the byte range labels the position with
         * ALL BYTES. A wider label makes (U1)'s at-most-one-live-position test
         * and (U2)'s follow-set disjointness harder to prove, so the verdict
         * is lost and no answer moves. */
        uint8_t lab[32];
        pcrec_cls_bits_widen(g->cx, a, lab);
        int p = gk_newpos(g, lab, a);
        if (p < 0) return gk_parts_empty(true);
        GkParts r = gk_parts_empty(false);
        cls_set(r.first, (unsigned)p);
        cls_set(r.last, (unsigned)p);
        return r;
    }
    /* [M6.5.2] DECLINE THE WHOLE CONSTRUCTION. Every other member of the arm
     * below is a genuine epsilon in the position automaton this builds; a
     * backreference is not — it consumes a variable amount of text, so it has
     * no POSITION and the (U1)/(U2) unique-iteration argument the automaton
     * exists to decide is not expressible over it. Declining is always
     * available and always safe here (the caller reads `g->ok`), and it costs
     * only the possessification of a quantifier whose body holds a reference. */
    case A_BREF:
    case A_VAR:
        g->ok = false;
        return gk_parts_empty(true);
    /* [M6.6.2] DECLINE THE WHOLE CONSTRUCTION, `A_BREF`'s arm for a reason
     * one step subtler, and the subtlety is why it is written out.
     *
     * A lookaround genuinely IS zero-width, so `gk_parts_empty(true)` — the
     * epsilon arm below — looks correct and is even arguably SOUND for the two
     * questions this automaton decides: erasing a lookaround yields a SUPERSET
     * language (design §5.3), and (U1) one-unambiguity and (U2) prefix-freeness
     * are both inherited by a subset. So the automaton would not be lied to.
     *
     * It declines anyway, and the reason is that this automaton is not the
     * only thing possessify decides on. The verdict it feeds is combined with
     * a FOLLOW-set disjointness test, and design §3.2.1 is explicit that a
     * lookaround body's follow is NOT the enclosing follow — the assertion's
     * bytes and the follow's bytes are THE SAME BYTES. Modelling the node as a
     * genuine epsilon here while the follow machinery cannot see the boundary
     * is how a positive verdict gets assembled from two half-right halves.
     * Declining is always available and always safe (the caller reads
     * `g->ok`), and it costs only the possessification of a quantifier whose
     * body holds an assertion. */
    case A_LOOK:
        g->ok = false;
        return gk_parts_empty(true);
    /* [DD-14] DECLINE THE WHOLE CONSTRUCTION, `A_BREF`'s arm for `A_BREF`'s
     * reason and then some. This builds a POSITION AUTOMATON over the body's
     * byte-consuming positions to decide (U1) one-unambiguity and (U2)
     * prefix-freeness; a call has no position of its own — it stands for a
     * whole sub-automaton that lives somewhere else in the tree and may be its
     * own ancestor. Neither question is expressible over it.
     *
     * The epsilon arm below would be a LIE here in a way it is not even for a
     * lookaround: a lookaround really does consume nothing, while a call
     * consumes whatever its callee consumes, so modelling it as an epsilon
     * would make a body look prefix-free that is not.
     *
     * Declining is always available and always safe (the caller reads
     * `g->ok`), and it costs only the possessification of a quantifier whose
     * body holds a call. */
    case A_CALL:
        g->ok = false;
        return gk_parts_empty(true);
    case A_EMPTY:
    case A_BOL:
    case A_EOL:
    case A_END:
    case A_CTX:
    case A_GSTART:
    /* [M6.2 wave E] `\K` too, and here it is the LITERAL truth rather than
     * a modelling choice: this walk asks whether the body admits a unique
     * iteration, which is a question about the language, and `\K` lowers to
     * an epsilon. */
    case A_KRESET:
        /* Zero-width: contributes no position and does not change
         * nullability, so the sequence rules below leave the surrounding
         * fold untouched — the reference probe's "modelled as absent". */
        return gk_parts_empty(true);

    case A_CAP:
    /* [M6.4.2] TRANSPARENT, and here the transparency is load-bearing in the
     * sound direction. This builds the body's POSITION (Glushkov) automaton,
     * which (U1) one-unambiguity and (U2) prefix-freeness are decided on.
     * Reading through the cut gives the UNCUT position automaton, which has
     * MORE positions and MORE follow edges than a cut-aware one would — so
     * every ambiguity and every non-prefix-free witness the real construct has
     * is still present, and the verdict can only become MORE conservative,
     * never less. Declining a possessification is always safe; wrongly
     * granting one is a miscompile. */
    case A_ATOMIC:
        return gk_build(g, a->l);

    case A_CAT: {
        /* Right-to-left fold along the left-nested spine, the same direction
         * first_of uses and for the same reason. At each step `acc` is the
         * suffix already built and `x` the item in front of it:
         *   first = first(x) + (nullable(x) ? first(acc) : {})
         *   link(last(x), first(acc))
         *   last  = nullable(acc) ? last(x) + last(acc) : last(acc)
         * Position IDS are therefore handed out in reverse text order, which
         * nothing here depends on: every test below is order-independent. */
        GkParts acc = gk_parts_empty(true);
        const Ast *t = a;
        for (;;) {
            const Ast *item = (t->k == A_CAT) ? t->r : t;
            GkParts x = gk_build(g, item);
            gk_link(g, x.last, acc.first);
            GkParts r;
            memcpy(r.first, x.first, 32);
            if (x.nullable) bs_or(r.first, acc.first);
            if (acc.nullable) {
                memcpy(r.last, x.last, 32);
                bs_or(r.last, acc.last);
            } else {
                memcpy(r.last, acc.last, 32);
            }
            r.nullable = x.nullable && acc.nullable;
            acc = r;
            if (t->k != A_CAT) break;
            t = t->l;
        }
        return acc;
    }
    case A_ALT: {
        GkParts acc = gk_parts_empty(false);
        const Ast *t = a;
        for (;;) {
            const Ast *br = (t->k == A_ALT) ? t->r : t;
            GkParts x = gk_build(g, br);
            bs_or(acc.first, x.first);
            bs_or(acc.last, x.last);
            acc.nullable = acc.nullable || x.nullable;
            if (t->k != A_ALT) break;
            t = t->l;
        }
        return acc;
    }
    case A_REP: {
        GkParts r = gk_build(g, a->l);
        /* The loop's own back edge exists exactly when two iterations can run
         * consecutively. `X{0,1}` and `X{0}` have no back edge. */
        if (a->u.rep.rmax < 0 || a->u.rep.rmax > 1) gk_link(g, r.last, r.first);
        r.nullable = r.nullable || a->u.rep.rmin == 0;
        return r;
    }
    }
    g->ok = false;
    return gk_parts_empty(true);
}

/* §2.2's "X admits a unique iteration", plus the non-nullability conjunct that
 * always travels with it. `why` names the failing condition for the listing. */
static bool body_admits_unique_iteration(Gk *g, const Ast *body,
                                         const char **why)
{
    g->npos = 0;
    g->ok = true;

    GkParts p = gk_build(g, body);
    memcpy(g->last, p.last, 32);

    if (!g->ok)     { *why = "model-error";    return false; }
    if (p.nullable) { *why = "nullable-body";  return false; }

    /* (U1a) the initial position set is pairwise byte-disjoint */
    uint8_t seen[32];
    bs_clear(seen);
    for (int i = 0; i < g->npos; i++) {
        if (!cls_has(p.first, (unsigned)i)) continue;
        if (bs_intersects(g->set[i], seen)) { *why = "ambiguous-body"; return false; }
        bs_or(seen, g->set[i]);
    }
    /* (U1b) every position's follow set is pairwise byte-disjoint */
    for (int i = 0; i < g->npos; i++)
        if (g->fconflict[i]) { *why = "ambiguous-body"; return false; }

    /* (U2) prefix-free: no accepting position may continue */
    for (int i = 0; i < g->npos; i++) {
        if (!cls_has(p.last, (unsigned)i)) continue;
        if (g->hasfollow[i]) { *why = "not-prefix-free"; return false; }
    }

    *why = "unique-iteration";
    return true;
}

/* The same predicate, exported for src/opt/revdet.c (internal.h carries the
 * contract). The REVERSE-DETERMINISTIC rung asks the identical question of the
 * REVERSED body, and every conjunct above is a refutation somebody measured —
 * so the one thing that must not happen is a second implementation of it
 * drifting from this one. The scratch is opaque to the caller because its only
 * relevant property is that it is reusable across quantifiers: it is 16 KB of
 * position state, and allocating one per verdict would be the pass's whole
 * cost. */
void *pcrec_uniq_scratch(Ctx *cx)
{
    Gk *g = pcrec_arena_alloc(&cx->arena, sizeof(Gk));
    g->cx = cx;
    return g;
}

/* body_admits_unique_iteration over the scratch Gk `scratch` -- the verdict
 * pcrec_uniq_scratch's allocation exists to make cheap to ask repeatedly. */
bool pcrec_uniq_iteration(void *scratch, const Ast *body, const char **why)
{
    return body_admits_unique_iteration((Gk *)scratch, body, why);
}

/* ---- the walk: FOLLOW, transitively, and the verdict ---------------------
 *
 * FOLLOW(Q) is the set of bytes that can begin whatever runs after `Q`,
 * computed OUTWARD: the first set of Q's remaining siblings, extended past
 * nullable siblings to the enclosing constructs, and including FIRST(B) for
 * the body B of every ENCLOSING LOOP — because an enclosing loop can start
 * another iteration once Q's parent finishes.
 *
 * That enclosing-loop term is the line §8 of the design note nominated as "the
 * single most likely place for a soundness bug to be hiding". It survived a
 * 42,336-pair targeted attack at 0 divergences, and the failing-direction
 * control confirms it is load-bearing rather than inert: dropping the term
 * yields 172 counterexamples [R24 H1]. Only the UNION of the enclosing firsts
 * is ever consulted, so one accumulated set carries it exactly.
 *
 * `may_end` is the other half of the context and exists only for the lazy
 * conjunct: it says whether the match can legitimately FINISH where `Q` ends,
 * which is what makes the follow's first-byte test vacuous. */
/* [K93] EVERY CONTEXT A GROUP'S BODY CAN RUN IN, joined. A subroutine call
 * re-runs the called group's body — the whole `A_CAP`, or the whole pattern
 * for `(?R)` — under the CALL SITE's follow, not the group's lexical one, so
 * a verdict on a quantifier inside it is sound only if it holds in EVERY such
 * context. The verdict is a conjunction over contexts (disjointness from a
 * union of follows is disjointness from each; the lazy conjunct fires if any
 * context may end there; the exact-count arm reads no context at all), and
 * the follow a nested item sees distributes over that union, so one walk of
 * the group under the JOINED context answers for all of them at once.
 * `follow`/`may_end`/`encl` are exactly `pss_walk`'s three parameters, and
 * the arena's zero is the join's identity, so a group nothing calls walks
 * under its lexical context unchanged. */
typedef struct {
    uint8_t follow[32];
    uint8_t encl[32];
    bool    may_end;
} CallCtx;

typedef struct {
    Ctx  *cx;
    Gk   *g;
    int   marked;      /* newly marked on THIS call — the fixpoint's signal */
    int   seen;        /* A_REP nodes walked */
    int   possessive;  /* A_REP nodes possessive AFTER this call */
    /* [M6.4.2] THE SURVEY CHANNEL. When `fn` is non-NULL this walk does NOT
     * write `Ast.u.rep.possessive` at all — it reports every positive verdict
     * through the callback instead. `pcrec_poss_survey` is the entry; the free
     * discharge (src/opt/atomic.c) is the caller. Same walk, same FOLLOW, same
     * conjuncts: a second implementation of §2.2 is the one thing this file
     * must never grow. */
    void (*fn)(void *user, Ast *rep);
    void *user;
    /* [K93] THE CALL-SITE CONTEXTS, indexed by group number (0 = the root,
     * `(?R)`'s target). NULL for a call-free pattern. See `pss_run`. */
    CallCtx *cc;
    int      ncc;
    bool     collect;     /* a context-only walk: no verdict, no counters */
    bool     cc_grew;     /* a context-only walk widened some `cc[t]` */
    /* [ART-POSS-ARMS] the arms' per-walk facts, `first_of`'s argument. */
    Fq       fq;
    /* [ART-POSS-ARMS] A1's continuation summaries (below): the scratch
     * stack `ps_chain` folds on, the root end's summary (built once per
     * run) and the one atomic-body END every atomic body shares. */
    struct PCont **stk;
    int            nstk, capstk;
    struct PSum   *root_sum;
    struct PCont  *atomic_end;
    /* [ART-POSS-ARMS] the stamp's evidence: positive verdicts from rows 1-3
     * and from A1 alone. A SHADOW walk (`pss_shadow`) only counts them. */
    int      n_rows, n_a1;
    bool     shadow;
} Pss;

/* ---- [ART-POSS-ARMS] A1: Q's continuation, summarized once (§2.3, §7) ----
 *
 * A1 re-asks row 3 with every gate in Q's continuation valued by Q's own
 * LAST polarities, so it needs that continuation as a SEQUENCE of items, not
 * the byte set the walk threads. `pss_walk` therefore threads a chain beside
 * FOLLOW: a `PCont` per item that runs after this point, a marker at the END
 * of every A_CAP the walk is inside (crossing it at zero consumption unions
 * the group's joined call-site context, A0-valued — A-F1's fix (a); `cc`
 * never holds an A1 value, it would need one per Q), and an atomic body's
 * own END (the walk analyses that body as a self-contained pattern).
 *
 * WHY A SUMMARY (R-4). Folding the chain per quantifier is quadratic:
 * `(?:a+|a+|…)(?:\b|)…` at n = 6,400 took 64.85 s against 0.90 s denied. But
 * WHICH items are reached at zero consumption does not depend on Q, because
 * every A_CTX is non-nullable whatever P is. So each chain link carries,
 * once, a `PSum`: the bytes of every reached item that is not a
 * left-dependent gate, the reached gates grouped by their set C with S(P)
 * precomputed for the three non-empty P, and whether the match can end.
 * Per Q only the groups are evaluated: O(distinct gate sets x |LAST|).
 *
 * The same summary valued A0 IS the walk's FOLLOW (and its may_end), which
 * `pss_verdict` asserts at every verdict (R-5); under `--emit-ir` it is also
 * checked against the plain per-Q fold it replaces (`cont_fold`, R4SUM). */
typedef struct PGate {
    const PcrecCpRange *iv;     /* the gate set C */
    int                 n;
    uint8_t             s[4][32];   /* S(P) for pmask 1..3 */
    bool                nar[4];     /* ctx_admits narrowed for that pmask */
    struct PGate       *next;
} PGate;

typedef struct PSum {
    uint8_t u[32];      /* bytes of the reached items that are not gates */
    PGate  *g;          /* the reached gates, grouped by C */
    bool    nullable;   /* (node summary) the item can match empty */
    bool    ends;       /* (chain summary) the match can end from here at
                         * zero consumption: lexically, or through a crossed
                         * call site's joined may_end */
} PSum;

typedef struct PCont {
    const Ast    *node;     /* the next item; NULL on a marker */
    int           capend;   /* > 0: a marker, the END of that group */
    bool          atomic_end;   /* a marker: an atomic body's END */
    struct PCont *next;
    PSum         *sum;      /* the chain summary from here, once computed */
} PCont;

static void pss_walk(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                     const uint8_t *encl, PCont *k);

/* A new chain link for item `node` (or the marker `capend`) before `next`. */
static PCont *pc_new(Pss *P, const Ast *node, int capend, PCont *next)
{
    PCont *c = pcrec_arena_alloc(&P->cx->arena, sizeof *c);
    c->node   = node;
    c->capend = capend;
    c->next   = next;
    return c;
}

/* True iff the two interval lists are the same set. */
static bool iv_eq(const PcrecCpRange *a, int na, const PcrecCpRange *b, int nb)
{
    return na == nb && (na == 0 || memcmp(a, b, (size_t)na * sizeof *a) == 0);
}

/* ORs the gate group `x` into the list `*l`, merging with the group of the
 * same C (a pmask that does not narrow in either stays not narrowed). */
static void pg_add(Ctx *cx, PGate **l, const PGate *x)
{
    for (PGate *y = *l; y; y = y->next)
        if (iv_eq(y->iv, y->n, x->iv, x->n)) {
            for (int pm = 1; pm < 4; pm++) {
                y->nar[pm] = y->nar[pm] && x->nar[pm];
                if (y->nar[pm]) bs_or(y->s[pm], x->s[pm]);
            }
            return;
        }
    PGate *c = pcrec_arena_alloc(&cx->arena, sizeof *c);
    *c = *x;
    c->next = *l;
    *l = c;
}

/* ORs every group of the list `x` into `*l`. */
static void pg_union(Ctx *cx, PGate **l, const PGate *x)
{
    for (; x; x = x->next) pg_add(cx, l, x);
}

/* The summary of ONE item: `first_of`'s fold with every A_CTX recorded as a
 * gate group instead of valued (when arm A is on; denied, `first_of`'s
 * widen goes into the bytes, so the summary is built either way). */
static PSum ps_node(Pss *P, const Ast *a)
{
    PSum r;
    memset(&r, 0, sizeof r);
    switch (a->k) {
    case A_CTX:
        if (P->fq.arm_a) {
            PGate x;
            memset(&x, 0, sizeof x);
            x.iv = a->u.ctx.iv;
            x.n  = a->u.ctx.n;
            for (unsigned pm = 1; pm < 4; pm++)
                x.nar[pm] = ctx_admits(a, pm, x.s[pm]);
            pg_add(P->cx, &r.g, &x);
        } else {
            First f = first_of(&P->fq, a);
            memcpy(r.u, f.f, 32);
        }
        return r;                       /* non-nullable, as `first_of` */
    case A_CAP: case A_ATOMIC:
        return ps_node(P, a->l);
    case A_CAT: {
        /* right to left, as `first_of`: seq(x, rest) */
        r.nullable = true;
        const Ast *t = a;
        for (;;) {
            PSum x = ps_node(P, t->k == A_CAT ? t->r : t);
            if (x.nullable) {
                bs_or(x.u, r.u);
                pg_union(P->cx, &x.g, r.g);
                x.nullable = r.nullable;
            }
            r = x;
            if (t->k != A_CAT) break;
            t = t->l;
        }
        return r;
    }
    case A_ALT: {
        const Ast *t = a;
        for (;;) {
            PSum x = ps_node(P, t->k == A_ALT ? t->r : t);
            bs_or(r.u, x.u);
            pg_union(P->cx, &r.g, x.g);
            r.nullable = r.nullable || x.nullable;
            if (t->k != A_ALT) break;
            t = t->l;
        }
        return r;
    }
    case A_REP:
        r = ps_node(P, a->l);
        r.nullable = r.nullable || a->u.rep.rmin == 0;
        return r;
    case A_CLASS: case A_WCLASS: case A_EMPTY: case A_BOL: case A_EOL:
    case A_END: case A_GSTART: case A_KRESET: case A_BREF: case A_LOOK:
    case A_CALL: case A_VAR:
        break;
    }
    First f = first_of(&P->fq, a);
    memcpy(r.u, f.f, 32);
    r.nullable = f.nullable;
    return r;
}

/* The root end's summary: `(?R)`'s joined call sites, and the match may end
 * (the walk's `pss_root` context). Built once per run. */
static const PSum *ps_root(Pss *P)
{
    if (!P->root_sum) {
        PSum *r = pcrec_arena_alloc(&P->cx->arena, sizeof *r);
        if (P->cc) {
            bs_or(r->u, P->cc[0].follow);
            bs_or(r->u, P->cc[0].encl);
        }
        r->ends = true;
        P->root_sum = r;
    }
    return P->root_sum;
}

/* Pushes `c` on the walk's scratch stack, growing it (arena) by doubling. */
static void ps_push(Pss *P, PCont *c)
{
    if (P->nstk == P->capstk) {
        int ncap = P->capstk ? 2 * P->capstk : 64;
        PCont **ns = pcrec_arena_alloc(&P->cx->arena,
                                       (size_t)ncap * sizeof *ns);
        if (P->nstk) memcpy(ns, P->stk, (size_t)P->nstk * sizeof *ns);
        P->stk    = ns;
        P->capstk = ncap;
    }
    P->stk[P->nstk++] = c;
}

/* The chain summary from `k` (NULL: the root end), memoized on each link.
 * ITERATIVE: a chain is as long as the spine it came from (D10/K20), so the
 * unmemoized prefix is pushed, stopping at a memo, the root, or an item the
 * match cannot pass at zero consumption, and folded back to front. */
static const PSum *ps_chain(Pss *P, PCont *k)
{
    if (!k) return ps_root(P);
    if (k->sum) return k->sum;
    P->nstk = 0;
    const PSum *tail = NULL;     /* NULL: the last link reads nothing beyond */
    for (PCont *c = k; ; c = c->next) {
        if (!c)     { tail = ps_root(P); break; }
        if (c->sum) { tail = c->sum;     break; }
        ps_push(P, c);
        c->sum = pcrec_arena_alloc(&P->cx->arena, sizeof *c->sum);
        if (c->capend) {
            if (P->cc && c->capend < P->ncc) {
                bs_or(c->sum->u, P->cc[c->capend].follow);
                bs_or(c->sum->u, P->cc[c->capend].encl);
                c->sum->ends = P->cc[c->capend].may_end;
            }
            continue;
        }
        *c->sum = ps_node(P, c->node);
        if (!c->sum->nullable) break;
    }
    for (int i = P->nstk - 1; i >= 0; i--) {
        PSum *r = P->stk[i]->sum;
        const PSum *nx = i == P->nstk - 1 ? tail : P->stk[i + 1]->sum;
        if (!nx) continue;              /* a non-nullable last item */
        if (!P->stk[i]->capend && !r->nullable) { r->ends = false; continue; }
        bs_or(r->u, nx->u);
        pg_union(P->cx, &r->g, nx->g);
        r->ends = r->ends || nx->ends;
    }
    return k->sum;
}

/* The polarity mask of class `x` against the set C: bit 0 when some member
 * is outside C, bit 1 when some is inside (sorted interval sweeps). */
static unsigned cls_polarity(const Ast *x, const PcrecCpRange *C, int n)
{
    unsigned m = 0;
    int j = 0;
    for (int i = 0; i < x->u.cls.n && m != 3u; i++) {
        unsigned c = x->u.cls.iv[i].lo, hi = x->u.cls.iv[i].hi;
        for (;;) {
            while (j < n && C[j].hi < c) j++;
            if (j < n && C[j].lo <= c) {
                m |= 2u;
                if (C[j].hi >= hi) break;
                c = C[j].hi + 1;
            } else {
                m |= 1u;
                if (j == n || C[j].lo > hi) break;
                c = C[j].lo;
            }
        }
    }
    return m;
}

/* A1's P for a gate over C: the polarities of the classes at the LAST
 * positions of the body `body_admits_unique_iteration` last built in `g`
 * (§2.3; a mixed LAST gives {0,1}, which narrows nothing). */
static unsigned a1_pmask(const Gk *g, const PcrecCpRange *C, int n)
{
    unsigned pm = 0;
    for (int i = 0; i < g->npos && pm != 3u; i++)
        if (cls_has(g->last, (unsigned)i)) pm |= cls_polarity(g->cls[i], C, n);
    return pm;
}

/* Values the chain summary `sm`: every gate A0 (`a0`, P = {0,1}) or A1
 * (Q's LAST polarities, read from `P->g`). `nullable` is the summary's
 * `ends`. */
static First ps_eval(const Pss *P, const PSum *sm, bool a0)
{
    First acc;
    memcpy(acc.f, sm->u, 32);
    acc.nullable = sm->ends;
    for (const PGate *x = sm->g; x; x = x->next) {
        unsigned pm = a0 ? 3u : a1_pmask(P->g, x->iv, x->n);
        if (pm == 0) continue;          /* LAST empty: not under base_ok */
        if (!x->nar[pm]) { bs_all(acc.f); return acc; }
        bs_or(acc.f, x->s[pm]);
    }
    return acc;
}

/* FIRST of one item with every gate A1-valued (`a0` false) or as `first_of`
 * values it — the plain fold `ps_node` summarizes, for `cont_fold`. */
static First item_first(Pss *P, const Ast *a, bool a0)
{
    if (a0) return first_of(&P->fq, a);
    switch (a->k) {
    case A_CTX: {
        First r;
        r.nullable = false;
        if (P->fq.arm_a &&
            ctx_admits(a, a1_pmask(P->g, a->u.ctx.iv, a->u.ctx.n), r.f))
            return r;
        return first_of(&P->fq, a);
    }
    case A_CAP: case A_ATOMIC:
        return item_first(P, a->l, false);
    case A_CAT: {
        First acc = fst_empty(true);
        const Ast *t = a;
        while (t->k == A_CAT) {
            acc = fst_seq(item_first(P, t->r, false), acc);
            t = t->l;
        }
        return fst_seq(item_first(P, t, false), acc);
    }
    case A_ALT: {
        First acc = fst_empty(false);
        const Ast *t = a;
        for (;;) {
            First r = item_first(P, t->k == A_ALT ? t->r : t, false);
            bs_or(acc.f, r.f);
            acc.nullable = acc.nullable || r.nullable;
            if (t->k != A_ALT) break;
            t = t->l;
        }
        return acc;
    }
    case A_REP: {
        First r = item_first(P, a->l, false);
        r.nullable = r.nullable || a->u.rep.rmin == 0;
        return r;
    }
    case A_CLASS: case A_WCLASS: case A_EMPTY: case A_BOL: case A_EOL:
    case A_END: case A_GSTART: case A_KRESET: case A_BREF: case A_LOOK:
    case A_CALL: case A_VAR:
        break;
    }
    return first_of(&P->fq, a);
}

/* The PLAIN per-Q fold of the continuation from `k` that `ps_chain`'s
 * summary replaces (R-4): linear in the chain, so asked only under
 * `--emit-ir`, as the summary's own check (R4SUM). */
static First cont_fold(Pss *P, const PCont *k, bool a0)
{
    First acc = fst_empty(true);
    bool cc_end = false;
    for (; k; k = k->next) {
        if (k->atomic_end) return acc;
        if (k->capend) {
            if (P->cc && k->capend < P->ncc) {
                bs_or(acc.f, P->cc[k->capend].follow);
                bs_or(acc.f, P->cc[k->capend].encl);
                cc_end = cc_end || P->cc[k->capend].may_end;
            }
            continue;
        }
        First x = item_first(P, k->node, a0);
        bs_or(acc.f, x.f);
        if (!x.nullable) { acc.nullable = cc_end; return acc; }
    }
    bs_or(acc.f, ps_root(P)->u);
    return acc;
}

/* True iff `x` and `y` are the same First value. */
static bool fst_eq(const First *x, const First *y)
{
    return memcmp(x->f, y->f, 32) == 0 && x->nullable == y->nullable;
}

/* [K93] Joins one call site's context into `cc[t]`, noting whether it grew —
 * the fixpoint's signal. A target with no slot would be a call whose body
 * never receives this context, so the verdicts inside it would be computed
 * without it: unsound, hence an internal error rather than a quiet return. */
static void cc_join(Pss *P, int t, const uint8_t *follow, bool may_end,
                    const uint8_t *encl)
{
    if (t < 0 || t >= P->ncc)
        pcrec_ctx_fail(P->cx, 0, "internal error: possessify: call target %d "
                       "has no context slot (ncc %d)", t, P->ncc);
    CallCtx *c = &P->cc[t];
    for (int i = 0; i < 32; i++) {
        uint8_t f = c->follow[i] | follow[i], e = c->encl[i] | encl[i];
        if (f != c->follow[i] || e != c->encl[i]) P->cc_grew = true;
        c->follow[i] = f;
        c->encl[i]   = e;
    }
    if (may_end && !c->may_end) { c->may_end = true; P->cc_grew = true; }
}

/* [K93] Widens a lexical context (`follow`/`*may_end`/`encl`, the caller's
 * copies) by every call site's context joined for group `t`. */
static void cc_widen(const Pss *P, int t, uint8_t *follow, bool *may_end,
                     uint8_t *encl)
{
    if (t < 0 || t >= P->ncc) return;
    const CallCtx *c = &P->cc[t];
    bs_or(follow, c->follow);
    bs_or(encl, c->encl);
    *may_end = *may_end || c->may_end;
}

/* [K93] pcrec_ast_visit callback: a call this walk does not reach with a
 * context — one inside a lookaround body, which `pss_walk` never enters —
 * joins the TOP context (every byte follows, the match may end, every byte
 * can restart), which declines every disjointness verdict in its callee. */
static void cc_top_visit(void *ud, const Ast *a)
{
    if (a->k != A_CALL) return;
    uint8_t all[32];
    bs_all(all);
    cc_join(ud, a->u.call.target, all, true, all);
}

/* [ART-POSS-ARMS] R-5: the chain summary `ks` at Q, valued A0, must BE the
 * walk's FOLLOW and may_end (modulo ENCL, which both union) — two
 * computations of one set, checked at every verdict so neither can drift.
 * Under `--emit-ir` the summary is also checked against the plain fold it
 * replaces (R4SUM). Either disagreement is an internal error. */
static void cont_check(Pss *P, const PSum *ks, const PCont *k,
                       const uint8_t *follow, bool may_end,
                       const uint8_t *encl)
{
    First c0 = ps_eval(P, ks, true);
    if (P->cx->want_ir) {
        First f0 = cont_fold(P, k, true);
        if (!fst_eq(&c0, &f0))
            pcrec_ctx_fail(P->cx, 0, "internal error: possessify: A1 "
                           "continuation summary disagrees with its fold");
    }
    uint8_t u1[32], u2[32];
    memcpy(u1, c0.f, 32);
    bs_or(u1, encl);
    memcpy(u2, follow, 32);
    bs_or(u2, encl);
    if (memcmp(u1, u2, 32) != 0 || c0.nullable != may_end)
        pcrec_ctx_fail(P->cx, 0, "internal error: possessify: A1 "
                       "continuation disagrees with FOLLOW");
}

/* §2.2's verdict on ONE A_REP, side-effect-free, given the context its caller
 * computed and the continuation chain `k` after it. Factored out of
 * `pss_rep` at [M6.4.2] so the free discharge can ask the SAME question the
 * marking walk asks, from the same lines. `*by_a1` is set when only arm A1
 * made it positive (the stamp's evidence). */
static bool pss_verdict(Pss *P, const Ast *a, const uint8_t *follow,
                        bool may_end, const uint8_t *encl, PCont *k,
                        bool *by_a1)
{
    First body = first_of(&P->fq, a->l);
    const PSum *ks = ps_chain(P, k);
    cont_check(P, ks, k, follow, may_end, encl);
    *by_a1 = false;

    /* The effective follow: what comes after Q here, plus what every
     * enclosing loop could restart with. */
    uint8_t eff[32];
    memcpy(eff, follow, 32);
    bs_or(eff, encl);

    const char *uwhy = NULL;
    bool uniq     = body_admits_unique_iteration(P->g, a->l, &uwhy);
    bool disjoint = !bs_intersects(body.f, eff);
    bool exact    = a->u.rep.rmax >= 0 && a->u.rep.rmin == a->u.rep.rmax;
    bool lazy     = !a->u.rep.greedy;
    bool base_ok  = uniq && !body.nullable;

    /* §2.2's ladder, in the order the arms are stated. The EXACT-COUNT arm is
     * tested FIRST and is preference-independent: with a unique-iteration body
     * there is exactly one way to run k iterations from a given start, so the
     * loop's only freedom is k, and m == n removes it without any reference to
     * what follows. It needs no lazy conjunct because it leaves ONE exit — top
     * and bottom of §2.3's chain are the same position — which is also why it
     * survived every attack the panel made [R24 H8] and why it carries 52 of
     * the 76 possessifiable verdicts on realistic patterns. */
    if (base_ok && exact)                            return true;
    if (base_ok && disjoint && lazy && may_end)      return false;
    if (base_ok && disjoint)                         return true;

    /* [ART-POSS-ARMS] A1: row 3 again, over Q's continuation with every gate
     * reached at zero consumption valued by Q's own LAST polarities, ENCL
     * unioned ungated (§2.3's full predicate). GREEDY ONLY and m >= 1 are
     * the measured conjuncts in the file header; neither is conservative. A
     * body FIRST of all bytes meets every non-empty set, so it is skipped. */
    uint8_t all[32];
    bs_all(all);
    if (P->fq.arm_a && base_ok && !lazy && a->u.rep.rmin >= 1 &&
        memcmp(body.f, all, 32) != 0) {
        First cf = ps_eval(P, ks, false);
        if (P->cx->want_ir) {
            First ff = cont_fold(P, k, false);
            if (!fst_eq(&cf, &ff))
                pcrec_ctx_fail(P->cx, 0, "internal error: possessify: A1 "
                               "continuation summary disagrees with its fold");
        }
        bs_or(cf.f, encl);
        if (!bs_intersects(body.f, cf.f)) { *by_a1 = true; return true; }
    }
    return false;
}

static void pss_mark(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                     const uint8_t *encl, bool survey_this, PCont *k);

/* `survey_this` is false at exactly one caller — the `A_ATOMIC` arm below,
 * which has already asked this node's verdict in a DIFFERENT context. */
static void pss_rep(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                    const uint8_t *encl, bool survey_this, PCont *k)
{
    First body = first_of(&P->fq, a->l);

    /* The effective follow: what comes after Q here, plus what every
     * enclosing loop could restart with. */
    uint8_t eff[32];
    memcpy(eff, follow, 32);
    bs_or(eff, encl);

    if (!P->collect) pss_mark(P, a, follow, may_end, encl, survey_this, k);

    /* Descend into the body. Its own quantifiers see this loop's follow AND
     * this loop's FIRST as part of theirs. */
    uint8_t inner[32];
    memcpy(inner, encl, 32);
    bs_or(inner, body.f);
    pss_walk(P, a->l, eff, may_end, inner, k);
}

/* `pss_rep`'s verdict half: asks §2.2 of `a` in the context given and acts on
 * the answer — marks it, or reports it in survey mode — and keeps the census.
 * Never reached on a context-only walk (`P->collect`), which must neither
 * mark on a context still being widened nor count a node twice. */
static void pss_mark(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                     const uint8_t *encl, bool survey_this, PCont *k)
{
    P->seen++;

    bool by_a1;
    bool verdict = pss_verdict(P, a, follow, may_end, encl, k, &by_a1);
    if (verdict) {
        if (by_a1) P->n_a1++;
        else       P->n_rows++;
    }

    if (P->shadow) {
        /* [ART-POSS-ARMS] A SHADOW WALK only counts (`pss_shadow`). */
    } else if (P->fn) {
        /* SURVEY MODE writes nothing (`pcrec_poss_survey`'s whole contract).
         * The census counters below are still maintained so a survey cannot
         * silently corrupt `cx->poss_*`; `pcrec_poss_survey` restores them. */
        if (verdict && survey_this) P->fn(P->user, a);
    } else if (verdict && !a->u.rep.possessive) {
        a->u.rep.possessive = true;
        P->marked++;
    }
    if (a->u.rep.possessive) P->possessive++;
}

/* Descends `a` computing §2.2's possessification verdict for every A_REP it
 * finds, threading FOLLOW (the byte set that can come next) and `may_end`
 * (can the surrounding context end right here) down the tree exactly as the
 * construct being walked would consume them. `encl` is the innermost
 * enclosing loop's own follow, needed for the lazy-quantifier conjunct.
 * Marks `Ast.u.rep.possessive` in place; every conjunct in the verdict is a
 * measured refutation of a simpler rule (file header) — do not simplify it
 * without re-reading which counterexample it exists to catch. */
static void pss_walk(Pss *P, Ast *a, const uint8_t *follow, bool may_end,
                     const uint8_t *encl, PCont *k)
{
    switch (a->k) {
    /* [CLS-TREE] S3: made by the encoding lowering, below this pass. */
    case A_WCLASS:
        return;
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    /* [M6.2 wave E] `\K` joins them with no caveat: this walk only HUNTS
     * for A_REP nodes to offer the verdict to, and a leaf hosts none. What
     * `\K` MEANS to the analysis is `first_of`'s answer, above. */
    /* [M6.5.2] a leaf: this walk only HUNTS for A_REP nodes to offer the
     * verdict to, and a backreference hosts none. What it MEANS to the
     * analysis is `first_of`'s answer above (every byte, nullable). */
    case A_CTX: case A_GSTART: case A_KRESET: case A_BREF:
    case A_VAR:
        return;

    /* [M6.6.2] THIS WALK DOES NOT ENTER A LOOKAROUND BODY AT ALL, so no
     * quantifier inside one is ever possessified. Three reasons, in the order
     * they were weighed.
     *
     * 1. THE FOLLOW DOES NOT CROSS THE BOUNDARY (design §3.2.1). This walk
     *    THREADS follow, and a lookahead's follow starts at the assertion's
     *    ENTRY position — so the body's bytes and the follow's bytes are the
     *    same bytes, and passing `follow` inward would double-count them. The
     *    A_ATOMIC arm below meets a version of this and answers it by walking
     *    the body with an EMPTY follow, which is available here too.
     *
     * 2. BUT THAT ANSWER WOULD HAVE TO READ `.atomic`, AND THAT IS THE REAL
     *    OBJECTION. Empty-follow-plus-`may_end` is right for the ATOMIC
     *    spellings, which commit to the body's first success; it is NOT right
     *    for `(?*` / `(*napla:`, which can be re-entered, so a quantifier at
     *    the end of a non-atomic body does have somewhere to retreat to. An
     *    arm that got this right would make possessify a SECOND READER of
     *    `Ast.u.look.atomic` — and design §3.1(a) settles ONE KIND rather than
     *    four precisely on the claim that all three flags are read at exactly
     *    one site (`vm_look`), "so there is no second reader to drift". This
     *    arm would be that second reader, and D62 control 3 is the record of
     *    what happens to a flag with two homes.
     *
     * 3. DECLINING IS ALWAYS SAFE. Not possessifying costs run-time work and
     *    emitted size, never an answer, and nothing produces an A_LOOK in this
     *    wave, so a verdict granted in there could not be exercised by any
     *    test in the tree.
     *
     * CONSEQUENCE WORTH RECORDING, because design §9.3's S-LA1 (C2-13) asks
     * for it: possessify cannot narrow ANY lookaround body, whatever is in it.
     * The row wants a detector body possessify provably cannot touch, and the
     * proof is now structural rather than per-shape — it does not enter. The
     * alternation in `(?=(a|ab))\1$` is doubly safe: this pass only ever marks
     * A_REP nodes, and an alternation with no quantifier over it offers none.
     *
     * `first_of` and `gk_build` above are the OTHER two questions and answer
     * differently: FIRST widens (a lookaround is opaque, so nothing near it is
     * possessified either) and the position automaton declines outright. */
    case A_LOOK:
        /* [K93] ...but a CALL in there still runs its callee, in a context
         * this walk never computes; the callee's verdicts must hold in it. */
        if (P->collect) pcrec_ast_visit(a, cc_top_visit, P);
        return;

    /* [DD-14] MUST NOT POSSESSIFY ACROSS A CALL BOUNDARY (design §4.4a site
     * 21), and for this kind the arm is a LEAF as well as a decline — there
     * is nothing to enter: an `A_CALL` has no `l` and no `r`, and the callee
     * hangs off `u.call.body`, the back edge §4.4 forbids this walk from
     * following.
     *
     * DECLINING TO FOLLOW IT IS NOT MERELY THE CHEAP OPTION. This walk THREADS
     * FOLLOW, and a callee's follow is not a property of the callee at all: it
     * is whatever follows the CALL SITE, and a group called from three places
     * has three different follows. Possessifying an `A_REP` inside the callee
     * against one call site's follow would delete matches at the other two —
     * the §2.2 verdict is only as good as the follow it was computed with, and
     * this is a construct where one subtree has many.
     *
     * [K93] AND THE SITE'S FOLLOW IS NOT DISCARDED, IT IS RECORDED. The
     * `A_REP` nodes in the callee get their verdict at the callee's own
     * lexical position, and this arm's comment used to say that was where
     * "the enclosing follow is the real one". It is not the only real one:
     * `(a+)b(?1)a` possessified `a+` against `{b}` and the call re-ran it
     * against `{a}`, NOMATCH on "abaa" where 10.46 answers (0,4). So on a
     * context-only walk this site joins its context into `cc[target]`, and
     * the `A_CAP` arm (or `pss_run`, for `(?R)`'s root) walks the group under
     * the join — one verdict per node, holding at every site. See `CallCtx`.
     *
     * `first_of` and `gk_build` above are the OTHER two questions and answer
     * differently — FIRST widens to all bytes, the position automaton
     * declines outright.
     *
     * SABOTAGE ROW S-SR9a IS THIS ARM'S, and its suite is `timeout` rather
     * than an answer comparison: letting this walk possessify a call-bearing
     * body routes `^(?(DEFINE)(?<g>a?))(?&g)*+$` onto `vm_poss_star`, which
     * emits NO empty-iteration guard and fires no work charge, so the
     * artifact HANGS. Design §2.6's RULED rung decline is what this arm and
     * `rd_shape`'s implement between them. */
    case A_CALL:
        if (P->collect) cc_join(P, a->u.call.target, follow, may_end, encl);
        return;

    case A_CAP: {
        /* [K93] the group's lexical context joined with every call site's.
         * EVERY `A_CAP` numbered `no` gets the join, not only the first the
         * call graph binds: a superset, and the safe direction. */
        uint8_t f[32], e[32];
        bool    me = may_end;
        memcpy(f, follow, 32);
        memcpy(e, encl, 32);
        cc_widen(P, a->u.cap.no, f, &me, e);
        /* [ART-POSS-ARMS] and A1's continuation crosses the group's END,
         * where it meets the same join (§2.3a). */
        pss_walk(P, a->l, f, me, e, pc_new(P, NULL, a->u.cap.no, k));
        return;
    }

    case A_REP:
        pss_rep(P, a, follow, may_end, encl, true, k);
        return;

    /* [M6.4.2] AN ATOMIC BODY IS ANALYSED AS A SELF-CONTAINED PATTERN, and
     * THAT IS NOT WHAT "TRANSPARENT" WOULD DO.
     *
     * `first_of` and `gk_build` above ARE transparent — FIRST and the position
     * automaton are properties of the strings the node can match, and a cut
     * removes whole MATCHES rather than first bytes or positions. This walk is
     * different: it threads FOLLOW, and FOLLOW is exactly what the cut cuts.
     *
     * MEASURED, on both engines, before this arm was written: with the group's
     * own follow passed through, `(?>(?:a|bc)*?)d` on "abcd" answers (0,4)
     * where libpcre2 answers (3,4). The lazy loop's §2.2 verdict came out
     * POSITIVE because its follow looked like {d} and `may_end` looked false —
     * so the lazy conjunct did not fire — and the emitter then collapsed the
     * preference to maximal. But `d` is NOT this loop's follow: the group
     * COMMITS at the loop's first exit, which for a lazy loop is the MINIMAL
     * one, and `d` runs only after that commitment. §2.2's collapse argument
     * ("at any non-maximal exit the body could iterate again, so that byte is
     * in FIRST(X), so by disjointness the follow cannot begin there") assumes
     * the loop can be RE-ENTERED, which is precisely what the cut deletes.
     *
     * So the body is walked with an EMPTY follow and `may_end = true`: nothing
     * follows the body INSIDE the group, and the group's body may legitimately
     * end at its own end. A quantifier that is NOT last in the body gets its
     * real within-body follow from the A_CAT arm, unchanged — `(?>X*?y)d`
     * still sees {y}. `encl` is carried through rather than cleared, which is
     * the conservative direction (a larger follow makes disjointness harder).
     *
     * THE SURVEY ASKS A DIFFERENT QUESTION AND GETS THE OTHER FOLLOW, which is
     * why it is answered HERE rather than inside the descent. The free
     * discharge asks "would DELETING this A_ATOMIC change the answer", and the
     * answer for the erased tree is the verdict computed with the GROUP's own
     * follow — the transparent one. The two genuinely differ: `(?>a*)a` is
     * NOMATCH on "aaa" while `a*a` is (0,3), and only the transparent reading
     * (follow = {a}, not disjoint, verdict FALSE) refuses to discharge it,
     * while only the cut-aware reading (follow = {}, verdict TRUE) is right
     * about the MARK the emitter needs. Same node, two questions, two follows.
     *
     * §6.4a's 776,160-cell sweep did not find this: its generator is
     * `PRE (?>QB q|QB xy) tail`-shaped, so a quantifier inside the group is
     * always followed by something INSIDE it, and the cell where the
     * quantifier ENDS the atomic body is not in its population. */
    case A_ATOMIC: {
        Ast *body = a->l;
        uint8_t none[32];
        bs_clear(none);
        if (body->k == A_REP) {
            /* THE SURVEY REPORTS THE `A_ATOMIC`, NOT ITS CHILD, and that is a
             * MEASURED requirement rather than a naming choice. The discharge's
             * question is about THIS GROUP — "would deleting it change the
             * answer" — and its context is THIS group's follow. Reporting the
             * `A_REP` made the answer look like a property of the quantifier,
             * and NESTED atomics then shared it: `(?>a*+)a` parses to
             * A_ATOMIC(A_ATOMIC(A_REP(a))), the inner group's verdict (follow
             * EMPTY, positive) discharged the inner correctly, and the OUTER
             * then found its own — now-spliced — `A_REP` child already in the
             * set and discharged itself too, on a verdict computed for a
             * different follow. Measured: `a*a` on "aaa" answers (0,3) where
             * `(?>a*+)a` is NOMATCH in libpcre2. Keyed on the group, the outer
             * is never reported (its child was not an `A_REP` when the survey
             * ran) and simply keeps its cut, which is always safe.
             *
             * GREEDY ONLY, and this is CARVE-OUT TWO one consumer over. The
             * discharge's claim is that the cut fires where §2.2 says the loop
             * lands. For a GREEDY body the loop's FIRST exit IS the maximal
             * exit, so the two coincide. For a LAZY one the first exit is the
             * MINIMAL exit, while §2.2's positive verdict rests on the
             * PREFERENCE COLLAPSE (emit_vm.c:2053-2062: under disjointness a
             * lazy loop is FORCED to the maximal exit, because at any
             * non-maximal exit the FOLLOW cannot begin) — and the cut fires
             * BEFORE the follow is ever consulted. Measured: `(?>a*?)b` on
             * "aaab" is (3,4) in libpcre2 and `a*?b` is (0,4), so deleting the
             * group changes the answer on a positive verdict.
             *
             * §5.3's measurement could not have found this and says so once
             * read carefully: `probe_free_discharge.py` drives the possessive
             * SUFFIX spellings, and there is no lazy one — `a*?+` is an ERROR
             * in both oracles — so its 532 positive-verdict patterns are all
             * greedy. The `(?>X q?)` group spelling is outside its population.
             * §14 item 9's pattern, a third time: another §2.2 consequence an
             * emitted shape depended on. The EXACT-COUNT sub-case (`(?>a{2}?)`,
             * where there is one exit and the preferences coincide) would be
             * safe and is declined anyway — declining is always safe, and a
             * second condition here would need its own evidence. */
            bool by_a1;
            if (P->fn && !P->collect && body->u.rep.greedy &&
                pss_verdict(P, body, follow, may_end, encl, k, &by_a1))
                P->fn(P->user, a);
            pss_rep(P, body, none, true, encl, false, P->atomic_end);
        } else {
            /* [ART-POSS-ARMS] the continuation stops at the body's END, as
             * the follow does (§8.7 R-5's one disagreement before it
             * agreed: it used to run on to the root's (?R) join). */
            pss_walk(P, body, none, true, encl, P->atomic_end);
        }
        return;
    }

    case A_CAT: {
        /* Right-to-left along the spine, carrying the follow of the suffix
         * already passed. Each item is visited with what follows IT, which is
         * the whole reason this walk cannot be a plain recursive descent. */
        uint8_t cur[32];
        memcpy(cur, follow, 32);
        bool cur_end = may_end;
        PCont *ck = k;
        Ast *t = a;
        while (t->k == A_CAT) {
            pss_walk(P, t->r, cur, cur_end, encl, ck);
            ck = pc_new(P, t->r, 0, ck);
            First x = first_of(&P->fq, t->r);
            uint8_t nf[32];
            memcpy(nf, x.f, 32);
            if (x.nullable) bs_or(nf, cur);
            else            cur_end = false;
            memcpy(cur, nf, 32);
            t = t->l;
        }
        pss_walk(P, t, cur, cur_end, encl, ck);   /* the spine's head */
        return;
    }
    case A_ALT: {
        /* Every branch is followed by the same thing. */
        Ast *t = a;
        while (t->k == A_ALT) {
            pss_walk(P, t->r, follow, may_end, encl, k);
            t = t->l;
        }
        pss_walk(P, t, follow, may_end, encl, k);
        return;
    }
    }
}

/* The whole pattern under the context of the top level — nothing follows it
 * and the match may end there (pcrec's entry points are a SEARCH) — joined
 * with every `(?R)` site's ([K93]: group 0's region is the root). */
static void pss_root(Pss *P, Ast *root)
{
    uint8_t f[32], e[32];
    bool    me = true;
    bs_clear(f);
    bs_clear(e);
    cc_widen(P, 0, f, &me, e);
    pss_walk(P, root, f, me, e, NULL);
}

/* [ART-POSS-ARMS] The walk's arms, from the two deny bits (§9: each denies
 * its arm in BOTH entries — one verdict). */
static void fq_init(Fq *q, Ctx *cx)
{
    uint64_t fl = cx->opt ? cx->opt->flags : 0;
    memset(q, 0, sizeof *q);
    q->cx    = cx;
    q->arm_a = !(fl & PCREC_NO_POSS_CTX_FOLLOW);
    q->arm_b = !(fl & PCREC_NO_POSS_BREF_FIRST);
}

static void pss_run(Pss *P, Ast *root);

/* [ART-POSS-ARMS] A SHADOW WALK: the marking walk's verdicts under the arms
 * given, COUNTED and never written — `poss_arms_fired`'s counterfactual.
 * Shares the real walk's position scratch `g`. */
static int pss_shadow(Ctx *cx, Ast *root, Gk *g, bool arm_a, bool arm_b)
{
    Pss S;
    memset(&S, 0, sizeof S);
    S.cx = cx;
    fq_init(&S.fq, cx);
    S.fq.arm_a = arm_a;
    S.fq.arm_b = arm_b;
    S.g = g;
    S.shadow = true;
    pss_run(&S, root);
    return S.n_rows + S.n_a1;
}

/* The `<PREFIX>_VM_POSS_ARMS` bits (§8.5) for the marking walk `R`: which
 * arm a positive verdict NEEDED. A1 is direct (it decides only after row 3
 * declined). A0 and B are counterfactual: the verdicts are monotone in each
 * arm (an arm only narrows a FIRST or clears a nullable), so the arm is
 * needed iff the walk without it counts fewer positives — A0 against rows
 * 1-3 with A1 off too (A1's summary values a lookahead gate as A0 does),
 * B against everything. A shadow walk runs only when its arm narrowed
 * something, so an arm-free compile pays nothing. A denied arm never
 * narrows, so its bits are 0 by construction — D47.3's do-or-die, read off
 * the artifact. */
static unsigned poss_arms_fired(Ctx *cx, Ast *root, const Pss *R)
{
    unsigned bits = 0;
    if (R->n_a1) bits |= PCREC_POSS_ARM_A1;
    if (R->fq.a0_used &&
        pss_shadow(cx, root, R->g, false, R->fq.arm_b) < R->n_rows)
        bits |= PCREC_POSS_ARM_A0;
    if (R->fq.b_used &&
        pss_shadow(cx, root, R->g, R->fq.arm_a, false) < R->n_rows + R->n_a1)
        bits |= PCREC_POSS_ARM_B;
    return bits;
}

/* [K93] Both entries' walk. On a call-bearing pattern the call-site contexts
 * are first driven to their FIXPOINT by context-only walks: a site inside a
 * called group sees a context that depends on its group's own join, so one
 * walk is not enough for nested calls and none is final for recursion. Every
 * join only widens a finite set, so it terminates; the marking walk then runs
 * once, under contexts no further walk would change. A call-free pattern
 * allocates nothing and walks once, exactly as before. */
static void pss_run(Pss *P, Ast *root)
{
    /* [ART-POSS-ARMS] this run's capture fact (arm B; a group-free pattern
     * has no reference to resolve) and its one atomic-body END: the walk
     * analyses an atomic body as a self-contained pattern, so its
     * continuation ends there and may end the match. */
    P->fq.cap = P->fq.arm_b && P->cx->ncap > 0 ? cap_build(P->cx, root) : NULL;
    P->atomic_end = pc_new(P, NULL, 0, NULL);
    P->atomic_end->atomic_end = true;
    P->atomic_end->sum = pcrec_arena_alloc(&P->cx->arena,
                                           sizeof *P->atomic_end->sum);
    P->atomic_end->sum->ends = true;
    P->root_sum = NULL;
    if (pcrec_has_call(root)) {
        P->ncc = (int)P->cx->ncap + 1;
        P->cc  = pcrec_arena_alloc(&P->cx->arena,
                                   (size_t)P->ncc * sizeof *P->cc);
        memset(P->cc, 0, (size_t)P->ncc * sizeof *P->cc);
        P->collect = true;
        do {
            P->cc_grew = false;
            pss_root(P, root);
        } while (P->cc_grew);
        P->collect = false;
    }
    pss_root(P, root);
}

/* Runs the possessify walk over `root` in SURVEY mode (calling `fn` per
 * provably-safe possessive candidate without marking anything), saving and
 * restoring cx's poss_total/poss_marked census counters around it so a survey
 * never perturbs pcrec_possessify's own reporting. */
void pcrec_poss_survey(Ctx *cx, Ast *root,
                       void (*fn)(void *user, Ast *rep), void *user)
{
    Pss P;
    memset(&P, 0, sizeof P);
    P.cx = cx;
    fq_init(&P.fq, cx);
    P.fn = fn;
    P.user = user;
    P.g = pcrec_uniq_scratch(cx);

    /* The census counters this walk maintains are `pcrec_possessify`'s, and a
     * SURVEY must not move them: `--emit-ir`'s header reports them and the
     * survey is not a pass anyone asked about. Saved and restored rather than
     * left to the fact that survey mode writes nothing, because `P.possessive`
     * is counted from the FIELD and would be reported as this survey's own. */
    const int saved_total = cx->poss_total, saved_marked = cx->poss_marked;

    pss_run(&P, root);

    cx->poss_total  = saved_total;
    cx->poss_marked = saved_marked;
}

/* Runs the possessify walk over `root`, marking every quantifier it proves
 * admits unique iteration as possessive; publishes cx->poss_total/poss_marked
 * from the walk's own counts and returns the number marked. */
int pcrec_possessify(Ctx *cx, Ast *root)
{
    Pss P;
    memset(&P, 0, sizeof P);
    P.cx = cx;
    fq_init(&P.fq, cx);
    P.marked = 0;

    /* One Gk for the whole pass, reset per quantifier: it is 16 KB of position
     * state and the corpus analyses up to a few thousand quantifiers per
     * compile, so allocating one per verdict would be the pass's whole cost. */
    P.g = pcrec_uniq_scratch(cx);

    pss_run(&P, root);

    cx->poss_total  = P.seen;
    cx->poss_marked = P.possessive;
    cx->poss_arms   = poss_arms_fired(cx, root, &P);
    return P.marked;
}
