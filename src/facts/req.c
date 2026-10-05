/* src/facts/req.c — [OPT-REQBYTE] + [OPT-REQPOS] tier 2b THE NECESSARY SET AND
 * THE NECESSARY LITERAL RUN: a byte every match of this pattern must contain, and the
 * longest run of contiguous bytes every match must contain.
 *
 * One AST-level analysis, read by BOTH emitters through the pattern-facts
 * record (the `req_set`/`req_whole_run` facts it derives, and the
 * `req_run`/`req_byte` facts derived at the foot of this file). With it,
 * a search over a window that does not contain the byte (or the run) answers
 * NOMATCH in ONE `memchr`-class pass instead of running an attempt at every
 * start position. PCRE2 calls the one-byte fact `PCRE2_INFO_LASTCODETYPE`/
 * `LASTCODEUNIT` ("the rightmost literal code unit that must exist in any
 * matched string, other than at its start", `man pcre2api`); pcrec computed
 * nothing like it, and `docs/dev/optloop/cycle1_analysis.md` M1 is what that
 * cost — five throughput rows of `capability@0.1` at 0.93-9.74 ns/byte where
 * the winner runs one pass at the floor rate, the largest single weighted gap
 * in the matrix (3.714 of the losing rows' 10.284).
 *
 * IT EXTENDS THE PREFILTER PRIMITIVE RATHER THAN PARALLELING IT. The DFA
 * scan's `RX_DFA_PREFILTER "memchr"` already emits a `memchr` over the same
 * window; that one is keyed on a CANDIDATE START and is hoisted one level out
 * here, keyed on a NECESSARY BYTE — which is what lets it serve the VM route
 * too, where the hybrid prefilter is declined outright for a backreference or
 * a linked call (`src/opt/select_engine.c`). Three of the five target rows
 * are exactly those declines, so the mechanism's whole point is that the fact
 * lives above the engine that cannot compute it.
 *
 * WHY THE WHOLE WINDOW AND NOT "OTHER THAN AT ITS START". PCRE2's own fact
 * excludes the match's first unit because its consumer is a per-attempt
 * check; this one's consumer runs ONCE per call over `[search_from,
 * subject_length)`, and every byte of every match lies in that window
 * whatever its position in the match. The restriction is therefore
 * unnecessary here and is not imposed — a strictly larger set, so strictly
 * more patterns get the check.
 *
 * WHY A SET AND NOT A BYTE. `A_ALT` INTERSECTS: a byte is necessary for
 * `foo|bar` only if it is necessary for both branches. An analysis carrying
 * one byte per node would have to give up at every alternation, and the
 * emitted form is a widening of this one (a later multi-byte test reads the
 * same set), so the set is what the analysis produces and the emitter picks
 * one member from it.
 *
 * THE RUN IS THE SAME FACT AT WORD GRAIN, and today's byte check is its
 * `L = 1` case exactly. A second accumulator on this same walk carries the
 * longest guaranteed-contiguous literal byte sequence of each subtree, plus
 * its own head and tail runs so a concatenation can JOIN them; the soundness
 * statement is the byte's own at a wider grain (every match contains `R` as a
 * contiguous substring; every byte of every match lies in the window; so a
 * window without `R` holds no match). `docs/design/reqpos_2b.md` is the
 * design, and its §0 records what the run is NOT: not a start bound, not an
 * offset from the match start, and not dependent on that note's declined
 * tier 2.
 *
 * THE SAFE DIRECTION IS THE EMPTY SET AND THE EMPTY RUN, which DISABLE the
 * check. Every arm that cannot decide takes it: a class with more than one
 * member for the SET (which is every caselessly-folded literal, since D23
 * folds `(?i)a` to `[aA]` at parse time) and for the RUN a class that is not
 * one small cube (below), a quantifier that admits zero iterations, a
 * backreference, a linked call and every assertion. A lookaround's body is
 * deliberately not descended into: a LOOKBEHIND's bytes sit BEFORE the
 * match's start and can therefore be outside `[search_from, subject_length)`
 * entirely, which would make the check unsound in the direction that deletes
 * matches.
 *
 * WHAT THE RUN DECLINES BEYOND THAT, each with its reason rather than a
 * shared "be careful" (reqpos_2b.md §2.4): a repeat's head and tail runs do
 * NOT survive the repeat, so nothing is ever joined across an iteration
 * boundary; an alternation contributes only its branches' longest COMMON
 * prefix and common suffix, so `(?:xabcy|zabcw)` reports no run where `abc`
 * is one.
 *
 * [OPT-LITSCAN] S4 C3 A RUN IS A RUN OF POSITIONS, NOT OF BYTES
 * (docs/design/litscan_s4.md §2.3.1). A position is a byte or a CUBE of at
 * most `pos_set` members (`PCREC_MAX_REQ_RUN_POS_SET` = 2: a caseless letter
 * `[Ss]`, `[jk]`), stored as `(T, K)` with `(x & K) == T` its membership
 * test, so a caseless word is a run where it used to contribute nothing.
 * Three rules make that one mechanism rather than a second one beside the
 * byte run:
 *   - ONE RANKING: a run's worth is its INFORMATION, `Σ popcount(K)` over
 *     its positions (8 for a byte, 7 for a pair), so among exact runs the
 *     order and the tie are exactly length's (`rn_better`);
 *   - ONE CONSTRUCTOR, `rn_put`, refuses a non-canonical position (`T & ~K`
 *     must be 0: T is the LOWER member, which the pair scan and the masked
 *     compare both read) as an internal error rather than normalizing it;
 *   - an alternation's common head and tail are the CUBE HULL of the two
 *     branches' positions, `K' = Ka & Kb & ~(Ta ^ Tb)`, `T' = Ta & K'`,
 *     symmetric in the branches and stopping at the first position whose
 *     hull leaves the domain — so `frank|fred` reports `fr[ae]` and
 *     `(?:S(?i:ab)|(?i:sab))` reports `[Ss][Aa][Bb]`, never the left
 *     branch's exact `S`.
 * Under `-fno-req-run-fold` `pos_set` is 1, the domain is the single byte,
 * the hull is byte equality and the walk is the pre-row one exactly. The SET
 * is unchanged by all of this: only an exact position is a set member.
 *
 * [K82] THE RUN CARRIES ITS MAXIMUM BYTE OFFSET FROM THE ATTEMPT START
 * (`RbRun.off`, docs/design/litscan_k82h.md §1.3), and only this walk can
 * compute it, because only the walk knows WHICH occurrence its run came from
 * (a left factor, a right factor or a join). Each subtree also carries its
 * maximum width in BYTES (`RbRuns.maxw`, saturating at `PCREC_W_UNBOUNDED`
 * through `pcrec_sat_add`/`pcrec_sat_mul`): a head sits at 0 in every match,
 * a tail at `maxw - n` or earlier, a right factor's run `maxw(left)` further
 * in, and a repeat's run in its FIRST iteration. The offset is an
 * ANNOTATION: `rn_better` ranks by information alone, so no run is chosen
 * for being bounded. It is NOT `pcrec_cwmax`, which counts characters: on
 * the lowered tree a `(?i)s` under utf8 is up to two bytes (U+017F), and a
 * character count there under-states the offset, which DELETES matches.
 *
 * THE WALK IS OVER THE LOWERED TREE, which is what makes the answer a BYTE
 * rather than a code point: after `pcrec_lower_enc` every `A_CLASS` is a byte
 * class, so a singleton is exactly one `memchr` argument. `pcrec_cls_single`
 * is the shared accessor and it already answers "exactly one code point, and
 * it is a byte". The RUN inherits this whole: a multi-byte character lowers
 * to a fixed-width `A_CAT` of singleton byte classes, which is MORE
 * contiguous literal under `-e utf8` and not less, and a run spanning a
 * character boundary is exactly as sound as one inside a character.
 *
 * THE SWITCH IS EXHAUSTIVE WITH NO DEFAULT ARM, `src/opt/mrl.c:38-46`'s rule:
 * a node kind added after this file is written must be a COMPILE ERROR here.
 * A default arm inheriting "the empty set" would be SOUND, which is exactly
 * why the alarm is worth more than the default — a new kind that really does
 * carry a necessary byte would silently never contribute one.
 *
 * THE WALK IS A CORE FACT AND THE PICK IS NOT ([PATFACTS] step 3.0,
 * docs/design/patfacts/design.md §4.1): this file answers WHAT every match
 * must contain — the whole SET (with its threaded rightmost member, the
 * tiebreak the pick falls back on) and the longest guaranteed RUN — and reads
 * no prior. WHICH member the emitted `memchr` tests, and which 8-byte window
 * of a longer run is compared, are SPEED choices made from these answers by
 * the rate readers beside the rate primitives (`src/core/findings.c`,
 * [FINDINGS] B1), composed into the derived facts at the foot of this file.
 * The lattice's helpers are `static` here, so a consumer that
 * wanted this answer another way would have to re-spell the whole walk.
 *
 * Called by the pattern-facts record (`src/facts/facts.c`) on the first ask
 * of `req_set` or `req_whole_run`, over the LOWERED tree the E2 seal recorded
 * after `pcrec_lower_enc`; both facts come off one call. */

#include <string.h>

#include "core/internal.h"
#include "core/findings.h"
#include "facts/facts_derive.h"



/* The three runs a subtree contributes, plus the one flag that says whether
 * the next concatenation may join across it.
 *
 * `all` is "this subtree's language is EXACTLY the one literal string `head`,
 * and all of it is stored". It is what makes `head` extendable by the factor
 * to the right, and it is FALSE the moment a run truncates — otherwise a
 * 20,000-byte literal would report its stored first bytes as adjacent to
 * whatever follows the literal, which is 19,968 bytes of a lie. */
typedef struct { RbRun best, head, tail; bool all; long long maxw; } RbRuns;

/* The two facts, threaded together because they come off one walk. */
typedef struct { RbSet set; RbRuns runs; } RbVal;


static RbSet rb_empty(void)
{
    RbSet s;
    memset(s.bits, 0, sizeof s.bits);
    s.pick = -1;
    return s;
}

static RbSet rb_single(int b)
{
    RbSet s = rb_empty();
    s.bits[b >> 3] |= (unsigned char)(1u << (b & 7));
    s.pick = b;
    return s;
}

/* CONCATENATION: every byte necessary for either factor is necessary for the
 * whole. `r` is the factor to the RIGHT, so its pick wins — that is the
 * "rightmost" rule, applied at the one node kind that has a left and a right
 * in subject order, and it is the TIEBREAK the frequency argmin falls back on
 * (and the whole answer under every encoding but `byte`). */
static RbSet rb_union(RbSet l, RbSet r)
{
    int i;
    for (i = 0; i < 32; i++) l.bits[i] |= r.bits[i];
    if (r.pick >= 0) l.pick = r.pick;
    return l;
}

/* ALTERNATION: only a byte necessary for BOTH branches is necessary for the
 * alternation. The pick rule is stated in the header; the final fallback
 * scans DOWN so "the largest surviving byte" is reached in one pass. */
static RbSet rb_intersect(RbSet l, RbSet r)
{
    RbSet out;
    int i;
    for (i = 0; i < 32; i++) out.bits[i] = (unsigned char)(l.bits[i] & r.bits[i]);
    out.pick = -1;
    if (rb_has(&out, r.pick))       out.pick = r.pick;
    else if (rb_has(&out, l.pick))  out.pick = l.pick;
    else for (i = 255; i >= 0; i--) if (rb_has(&out, i)) { out.pick = i; break; }
    return out;
}

/* ---- THE RUN ACCUMULATOR -------------------------------------------------
 *
 * Seven operations, of which only the two append helpers have a precondition
 * and both state it. Nothing here reads the prior: the run analysis produces
 * a run, and WHICH member of it the scan tests is decided once, by the
 * derived `req_run` fact below, through `src/core/findings.c`. */

/* What every run operation needs besides its operands: the compile (for the
 * position constructor's refusal) and the largest member set one position
 * may have, handed in by `pcrec_req_walk`'s caller. */
typedef struct { Ctx *cx; int pos_set; } RbWalk;

/* How many bytes the cube with mask `k` holds: two to the free bits. */
static int rn_members(int k)
{
    return 1 << (8 - __builtin_popcount((unsigned)k & 0xFFu));
}

/* A position's INFORMATION, the ranking's unit: popcount of its mask. */
static int rn_info(const RbRun *r)
{
    int t = 0;
    for (int i = 0; i < r->n; i++) t += __builtin_popcount(r->mask[i]);
    return t;
}

static RbRun rn_none(void)
{
    RbRun r;
    memset(r.bytes, 0, sizeof r.bytes);
    memset(r.mask, 0, sizeof r.mask);
    r.n = 0;
    r.trunc = false;
    r.off = 0;
    return r;
}

/* THE ONE CONSTRUCTOR of a run position: appends the cube `(t, k)` to `o`
 * (whose room the caller has checked). A NON-CANONICAL pair — a free bit set
 * in `t` — is refused as an internal error, never silently masked: the pair
 * scan's second stream is `t | ~k` and the masked compare tests
 * `(s & k) == t`, so an upper-member `t` would scan one member twice and
 * compare against a value no masked byte can have, DELETING matches. Every
 * producer is canonical by construction (`pcrec_cls_cube` returns the AND of
 * the members, the hull `Ta & K'`), so this fires only on a producer's bug,
 * and loudly, as `ofsk_emit_verify` refuses an empty chain. */
static void rn_put(const RbWalk *w, RbRun *o, int t, int k)
{
    if (t & ~k & 0xFF)
        pcrec_ctx_fail(w->cx, 0, "internal error: a necessary-run position "
                       "0x%02x/0x%02x carries a free bit in its member (T & ~K "
                       "must be 0)", t, k);
    o->bytes[o->n] = (unsigned char)t;
    o->mask[o->n] = (unsigned char)k;
    o->n++;
}

/* The run of the one position `(t, k)`. */
static RbRun rn_pos(const RbWalk *w, int t, int k)
{
    RbRun r = rn_none();
    rn_put(w, &r, t, k);
    return r;
}

/* `a` then `b`, keeping the FIRST PCREC_MAX_REQ_RUN_SCAN bytes.
 *
 * PRECONDITION: `a`'s LAST stored byte is really the last byte of `a`'s own
 * run, so that `b`'s first byte is genuinely adjacent to it. A head satisfies
 * that only when its subtree is `all` (hence untruncated); a tail satisfies it
 * always, since a tail is truncated at its FRONT. */
static RbRun rn_app(RbRun a, RbRun b)
{
    RbRun o = a;
    int i;
    for (i = 0; i < b.n && o.n < PCREC_MAX_REQ_RUN_SCAN; i++) {
        o.mask[o.n] = b.mask[i];
        o.bytes[o.n++] = b.bytes[i];
    }
    if (i < b.n || b.trunc) o.trunc = true;
    return o;
}

/* `a` then `b`, keeping the LAST PCREC_MAX_REQ_RUN_SCAN bytes — the tail
 * form, so that the run's own last byte stays the match's last byte.
 *
 * PRECONDITION: `b`'s FIRST stored byte is really the first byte of `b`'s own
 * run, which is what `all` guarantees at the only site that calls this. */
static RbRun rn_pre(RbRun a, RbRun b)
{
    RbRun o = rn_none();
    int tot = a.n + b.n, drop, i;
    drop = tot > PCREC_MAX_REQ_RUN_SCAN ? tot - PCREC_MAX_REQ_RUN_SCAN : 0;
    for (i = drop; i < tot; i++) {
        o.mask[o.n] = i < a.n ? a.mask[i] : b.mask[i - a.n];
        o.bytes[o.n++] = i < a.n ? a.bytes[i] : b.bytes[i - a.n];
    }
    o.trunc = a.trunc || b.trunc || drop > 0;
    return o;
}

/* The more INFORMATIVE of two runs (`rn_info`), `a` on a tie — so a
 * left-to-right walk's earlier candidate survives and the answer does not
 * depend on traversal order. An exact run's information is 8 x its length,
 * so among exact runs this is "the longer", with the same tie. */
static RbRun rn_better(RbRun a, RbRun b)
{
    return rn_info(&b) > rn_info(&a) ? b : a;
}

/* The CUBE HULL's mask at one position pair: the bits both positions care
 * about AND agree on. `cube(Ta & K', K')` is the smallest cube holding both
 * positions' member sets, and the formula is symmetric in the two. */
static int rn_hull_mask(int ta, int ka, int tb, int kb)
{
    return ka & kb & ~(ta ^ tb) & 0xFF;
}

/* The two branches' longest COMMON PREFIX, position by position their cube
 * HULL, claimed conservatively: only positions both actually store, and only
 * while the hull stays inside the position domain (`pos_set`). A longer real
 * common prefix is a missed opportunity, never an unsound claim — every byte
 * either branch can put at position `i` lies in the hull — and the result is
 * marked untruncated because it IS the whole of what is claimed. */
static RbRun rn_common_head(const RbWalk *w, RbRun a, RbRun b)
{
    RbRun o = rn_none();
    while (o.n < a.n && o.n < b.n) {
        int k = rn_hull_mask(a.bytes[o.n], a.mask[o.n], b.bytes[o.n], b.mask[o.n]);
        if (rn_members(k) > w->pos_set) break;
        rn_put(w, &o, a.bytes[o.n] & k, k);
    }
    return o;
}

/* The two branches' longest COMMON SUFFIX, hulled from the back for the same
 * reason and with the same conservatism. */
static RbRun rn_common_tail(const RbWalk *w, RbRun a, RbRun b)
{
    RbRun o = rn_none();
    int k = 0;
    while (k < a.n && k < b.n &&
           rn_members(rn_hull_mask(a.bytes[a.n - 1 - k], a.mask[a.n - 1 - k],
                                   b.bytes[b.n - 1 - k], b.mask[b.n - 1 - k]))
               <= w->pos_set)
        k++;
    for (int i = 0; i < k; i++) {
        int ia = a.n - k + i, ib = b.n - k + i;
        int m = rn_hull_mask(a.bytes[ia], a.mask[ia], b.bytes[ib], b.mask[ib]);
        rn_put(w, &o, a.bytes[ia] & m, m);
    }
    return o;
}

/* The identity of run concatenation: the EMPTY STRING, which is entirely
 * literal, so `all` is TRUE. That is not a trick — it is what makes an
 * accumulator seeded with it behave like the concatenation of nothing. */
static RbRuns rr_unit(void)
{
    RbRuns r;
    r.best = r.head = r.tail = rn_none();
    r.all = true;
    r.maxw = 0;
    return r;
}

/* Everything declined: no run, and no permission to join across this
 * subtree, whose matches are at most `maxw` bytes wide. */
static RbRuns rr_none(long long maxw)
{
    RbRuns r = rr_unit();
    r.all = false;
    r.maxw = maxw;
    return r;
}

/* A subtree that matches exactly the members of the one position `(t, k)`:
 * one byte wide. */
static RbRuns rr_pos(const RbWalk *w, int t, int k)
{
    RbRuns r;
    r.best = r.head = r.tail = rn_pos(w, t, k);
    r.all = true;
    r.maxw = 1;
    return r;
}

/* [K82] Where a tail of `n` stored bytes may begin inside a subtree at most
 * `maxw` bytes wide: a guaranteed SUFFIX ends at the match's end, so it
 * starts at `len - n <= maxw - n` — after `rn_pre`'s truncation too, which
 * keeps the LAST bytes. */
static long long rn_tail_off(long long maxw, int n)
{
    return maxw >= PCREC_W_UNBOUNDED ? PCREC_W_UNBOUNDED : maxw - n;
}

/* [K82] A repeat's maximum width: `rmax` copies of its body (`rmax < 0`
 * unbounded), saturating, so an unbounded repeat of a zero-width body is 0
 * and of anything wider is `PCREC_W_UNBOUNDED`. */
static long long rr_rep_w(int rmax, long long body)
{
    return pcrec_sat_mul(rmax < 0 ? PCREC_W_UNBOUNDED : (long long)rmax, body,
                         PCREC_W_UNBOUNDED);
}

/* CONCATENATION of runs: `l` is to the LEFT of `r` in subject order.
 *
 * The JOIN is the whole point of carrying head and tail runs — `l`'s
 * guaranteed suffix is adjacent to `r`'s guaranteed prefix, so their
 * concatenation is a guaranteed contiguous run even when neither factor is
 * literal on its own. `best` is the longest of the two factors' bests, that
 * join, and the resulting head and tail (which a `\z`-free literal makes the
 * same string, and which is what makes `rr_unit` a real identity). */
static RbRuns rr_cat(RbRuns l, RbRuns r)
{
    RbRuns o;
    RbRun rb = r.best, join = rn_app(l.tail, r.head);
    o.maxw = pcrec_sat_add(l.maxw, r.maxw, PCREC_W_UNBOUNDED);
    o.head = l.all ? rn_app(l.head, r.head) : l.head;
    o.head.off = 0;
    o.tail = r.all ? rn_pre(l.tail, r.tail) : r.tail;
    o.tail.off = rn_tail_off(o.maxw, o.tail.n);
    o.all  = l.all && r.all && !o.head.trunc;
    /* [K82] `l`'s own best keeps its offset (`l` begins where `o` does);
     * `r`'s sits at most `maxw(l)` further in; the join begins where `l`'s
     * tail does. */
    rb.off = pcrec_sat_add(l.maxw, r.best.off, PCREC_W_UNBOUNDED);
    join.off = rn_tail_off(l.maxw, l.tail.n);
    o.best = rn_better(rn_better(l.best, rb), join);
    o.best = rn_better(rn_better(o.best, o.head), o.tail);
    return o;
}

/* ALTERNATION of runs: only what every branch guarantees, which at the
 * contiguity grain is the common prefix and the common suffix and nothing
 * between them. `all` is false even when both branches are the same literal:
 * the general fact an alternation licenses is "these bytes are common", and a
 * same-literal special case would buy a population this analysis has never
 * measured (D77). */
static RbRuns rr_alt(const RbWalk *w, RbRuns l, RbRuns r)
{
    RbRuns o;
    o.maxw = l.maxw > r.maxw ? l.maxw : r.maxw;
    o.head = rn_common_head(w, l.head, r.head);
    o.head.off = 0;
    o.tail = rn_common_tail(w, l.tail, r.tail);
    o.tail.off = rn_tail_off(o.maxw, o.tail.n);
    o.best = rn_better(o.head, o.tail);
    o.all  = false;
    return o;
}

/* The bytes and the runs EVERY match of `a` must contain.
 *
 * The `A_CAT` spine is walked ITERATIVELY down `->l` and the `A_ALT` spine
 * iteratively down its own, for `src/opt/mrl.c`'s and `pcrec_ast_visit`'s
 * shared reason: both spines are as long as the PATTERN, not as deep as its
 * nesting, and this project has segfaulted its own compiler on a 20,000-byte
 * literal for want of exactly that. What remains recursive descends one paren
 * level per frame. (The census probe that measured this mechanism's
 * population re-learned the same lesson independently, `c2prep_report.md` F5.)
 *
 * `acc` carries what has been learned to the RIGHT of the current node, which
 * is what keeps the rightmost pick correct across an arbitrarily long spine
 * without a second pass — and, for the runs, what makes each step an ordinary
 * concatenation with the accumulated right-hand side. */
static RbVal rb_walk(const RbWalk *w, const Ast *a)
{
    RbVal acc;
    acc.set  = rb_empty();
    acc.runs = rr_unit();

    for (;;) {
        switch (a->k) {
        case A_CAT: {
            /* `a->r` is to the RIGHT of everything still to be walked and to
             * the LEFT of everything in `acc`, which is why the union and the
             * concatenation are spelled in this order and not the other. */
            RbVal r = rb_walk(w, a->r);
            acc.set  = rb_union(r.set, acc.set);
            acc.runs = rr_cat(r.runs, acc.runs);
            a = a->l;
            continue;
        }
        case A_CAP:
        case A_ATOMIC:
        /* [CLS-TREE] S3: TRANSPARENT to its byte child, which is exactly
         * what sat in this slot before the kind existed, so the walk
         * continues as it did then. */
        case A_WCLASS:
            /* Transparent: a group matches what its body matches, and an
             * atomic cut removes MATCHES rather than bytes, so every string
             * the group matches is one the body matches. */
            a = a->l;
            continue;
        case A_ALT: {
            const Ast *t = a->l;
            RbVal r = rb_walk(w, a->r), b;
            while (t->k == A_ALT) {
                b = rb_walk(w, t->r);
                r.set  = rb_intersect(b.set, r.set);
                r.runs = rr_alt(w, b.runs, r.runs);
                t = t->l;
            }
            b = rb_walk(w, t);
            r.set  = rb_intersect(b.set, r.set);
            r.runs = rr_alt(w, b.runs, r.runs);
            acc.set  = rb_union(r.set, acc.set);
            acc.runs = rr_cat(r.runs, acc.runs);
            return acc;
        }
        case A_REP:
            /* `rmin == 0` admits the empty iteration, on which the body
             * contributes no byte at all — the one arm where forgetting the
             * minimum is a deleted match rather than a missed opportunity.
             *
             * At `rmin >= 1` the body's BEST run survives and its head and
             * tail do NOT: nothing is joined across an iteration boundary,
             * which reqpos_2b.md §2.4 item 4 declines with its reason (the
             * population is unmeasured and the reasoning wants its own
             * witness family). So the repeat is walked for the set exactly as
             * before, and its run contribution is taken here rather than by
             * falling through. */
            if (a->u.rep.rmin >= 1) {
                RbVal b = rb_walk(w, a->l);
                RbRuns rep = rr_none(rr_rep_w(a->u.rep.rmax, b.runs.maxw));
                /* [K82] the body's run at its own offset: the FIRST
                 * iteration begins where the repeat does. */
                rep.best = b.runs.best;
                acc.set  = rb_union(b.set, acc.set);
                acc.runs = rr_cat(rep, acc.runs);
                return acc;
            }
            /* AND AT `rmin == 0` THE REPEAT STILL BREAKS CONTIGUITY, which is
             * a different obligation from the empty SET above and is the one
             * arm of this walk where getting it wrong DELETES A MATCH rather
             * than missing an opportunity. A C-comment pattern — an open
             * delimiter, a min-0 repeat of the body, a close delimiter —
             * would otherwise report a FOUR-BYTE run of the two delimiters
             * abutting: true of the match where the repeat takes zero
             * iterations, false of every match where it takes one, and a run
             * must hold on EVERY match. So a min-0 repeat is `rr_none`,
             * exactly as a multi-member class is.
             *
             * [K82] The body is still walked, for its WIDTH alone: a min-0
             * repeat contributes no byte and no run, but it does move every
             * run to its right. */
            acc.runs = rr_cat(rr_none(rr_rep_w(a->u.rep.rmax,
                                               rb_walk(w, a->l).runs.maxw)),
                              acc.runs);
            return acc;
        case A_CLASS: {
            int b = pcrec_cls_single(w->cx, a);
            unsigned char k = 0xFF, t = (unsigned char)b;
            if (b < 0 && (!pcrec_cls_cube(w->cx, a, &k, &t) ||
                          rn_members(k) > w->pos_set)) {
                /* A class that is not one cube of at most `pos_set` members
                 * contributes no byte and no run, and it also BREAKS
                 * contiguity for everything around it — which `rr_none`'s
                 * cleared `all` is exactly what says. One byte wide: the
                 * tree is lowered. */
                acc.runs = rr_cat(rr_none(1), acc.runs);
                return acc;
            }
            /* Only a single byte is a member of the necessary SET; a cube
             * position is one the RUN carries (litscan_s4.md §2.3.1). */
            if (b >= 0) acc.set = rb_union(rb_single(b), acc.set);
            acc.runs = rr_cat(rr_pos(w, t, k), acc.runs);
            return acc;
        }
        /* Consumes nothing, so it can make no byte necessary. `A_LOOK`'s body
         * is not descended into, and the header says why that is a
         * CORRECTNESS decline rather than a missed opportunity.
         *
         * FOR THE RUN THESE ARE NOT TRANSPARENT EITHER, and the reason is not
         * the same one: a zero-width assertion consumes nothing, so the bytes
         * on either side of it ARE adjacent in the subject — but an assertion
         * is also the one place a run could be joined across something that
         * is not a literal, and joining across `A_LOOK` in particular would
         * claim contiguity through a body whose own bytes this analysis
         * refuses to look at. One rule for all of them, `rr_none`, rather
         * than a per-assertion contiguity argument nothing has measured. */
        case A_EMPTY:
        case A_BOL:
        case A_EOL:
        case A_END:
        case A_CTX:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
            acc.runs = rr_cat(rr_none(0), acc.runs);
            return acc;
        /* The two deliberate declines, `src/facts/startanch.c`'s for the same
         * reasons: a backreference's bytes are the subject's business and a
         * linked call's body is `callgraph.c`'s cycle problem. Both are the
         * empty set, which disables the check — always sound. */
        case A_BREF:
        case A_VAR:
        case A_CALL:
            acc.runs = rr_cat(rr_none(PCREC_W_UNBOUNDED), acc.runs);
            return acc;
        }
    }
}

/* THE CORE FACTS, from ONE walk: the whole necessary SET (with its threaded
 * rightmost member, `RbSet.pick`) and the most informative guaranteed
 * contiguous RUN (`RbRun`, at most `PCREC_MAX_REQ_RUN_SCAN` positions
 * stored), its positions single bytes or cubes of at most `pos_set` members.
 * Both are the EMPTY answer where nothing is necessary, which disables every
 * check built on them and is always sound. Reads no prior and no option:
 * `pos_set` is its caller's reading of the fact-level deny. */
void pcrec_req_walk(Ctx *cx, const Ast *root, int pos_set, RbSet *set,
                    RbRun *run)
{
    RbWalk w = { cx, pos_set };
    RbVal v = rb_walk(&w, root);
    *set = v.set;
    *run = v.runs.best;
}

/* The rate rule a derived pick answered by, for `--emit-facts`' `why`
 * column: the byte-rate the compile consumed, or its NONE answer. Read off
 * the consumption record, not off the rate pointer, so no reader here tests
 * a rate (findings design §6.3's structural rule). */
static PfWhyCode req_rate_why(Ctx *cx)
{
    return cx->job->find.byte_rate_have ? PF_WHY_RATE_BUILTIN : PF_WHY_RATE_NONE;
}

/* THE WINDOW, the `req_run` fact's derived half, cut from the whole run the
 * core `req_whole_run` fact holds (`run->whole`/`whole_len`): which member of
 * the run the emitted `memchr` scans for (`idx`), and where a run longer than
 * `PCREC_MAX_REQ_RUN_EMIT` is truncated to (`at`, with `bytes` exactly
 * `whole + at` for `len` bytes). A whole run shorter than two bytes has no
 * window (`len == 0`). [K82] It also derives the window's `maxoff`, the
 * whole run's walk bound plus `at`. The two choices are the rate readers'
 * (`src/core/findings.c`); this composes them into the fact.
 *
 * The byte-rate is asked FIRST, before any branch, so whether the compile
 * consumed it does not depend on the pattern (findings design §6.4 rule 1). */
void pcrec_req_window(Ctx *cx, ReqRun *run, PfWhyCode *why)
{
    const uint32_t *rate = pcrec_find_byte_rate(cx);
    int n = run->whole_len;

    memset(run->bytes, 0, sizeof run->bytes);
    memset(run->mask, 0, sizeof run->mask);
    run->len = 0;
    run->idx = 0;
    run->at = 0;
    run->maxoff = 0;
    *why = PF_WHY_NONE;
    if (n < 2) return;
    *why = req_rate_why(cx);
    {
        int i = pcrec_find_run_scan_index(rate, run->whole, run->whole_mask, n);
        int s = n > PCREC_MAX_REQ_RUN_EMIT
              ? pcrec_find_run_window_start(rate, run->whole, run->whole_mask,
                                            n, i) : 0;
        int len = n - s;
        if (len > PCREC_MAX_REQ_RUN_EMIT) len = PCREC_MAX_REQ_RUN_EMIT;
        memcpy(run->bytes, run->whole + s, (size_t)len);
        memcpy(run->mask, run->whole_mask + s, (size_t)len);
        run->len = len;
        run->idx = i - s;
        run->at = s;
        /* [K82] the window begins `at` bytes into the whole run. */
        run->maxoff = pcrec_sat_add(run->whole_maxoff, s, PCREC_W_UNBOUNDED);
    }
}

/* THE BYTE the emitted `memchr` tests — the `req_byte` fact — at ONE return:
 * the run's own scan member where a run window shipped and that member is
 * one EXACT byte (there is one emitted `memchr`, and `<PREFIX>_REQ_BYTE`
 * reports what it tests), and otherwise the set's pick
 * (`src/core/findings.c`). -1 exactly when the set is empty.
 *
 * [OPT-LITSCAN] S4 C3 A PAIR SCAN MEMBER IS NOT A BYTE ANY MATCH MUST
 * CONTAIN: at a cube position `bytes[idx]` is T, and a match may carry the
 * other member there, so it falls to the set's pick (litscan_s4.md §2.3.3
 * case (ii)) and every value here stays a member of `req_set`. The byte-rate
 * is asked first, as the window's is. */
int pcrec_req_pick(Ctx *cx, const ReqSet *set, const ReqRun *run,
                   PfWhyCode *why)
{
    const uint32_t *rate = pcrec_find_byte_rate(cx);
    *why = req_rate_why(cx);
    if (run->len >= 2 && run->mask[run->idx] == 0xFF) return run->bytes[run->idx];
    if (set->rightmost < 0) *why = PF_WHY_NONE;
    return pcrec_find_set_pick(rate, set->bits, set->rightmost);
}
