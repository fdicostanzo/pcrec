/* [OPT-REQBYTE] + [OPT-REQPOS] tier 2b THE NECESSARY BYTE AND THE NECESSARY
 * LITERAL RUN: a byte every match of this pattern must contain, and the
 * longest run of contiguous bytes every match must contain.
 *
 * One AST-level analysis, `pcrec_req_byte`, read by BOTH emitters. With it,
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
 * WHICH MEMBER OF THE RUN THE `memchr` SCANS FOR is the same argmin under the
 * same prior over a smaller set, ties to the LEFTMOST — and when a run ships,
 * `Job.req_byte` becomes that member rather than the whole set's own pick,
 * because there is ONE emitted `memchr` and the stamp reports what it tests.
 * The two are therefore chosen at one site, at this file's single return.
 *
 * A RUN LONGER THAN `PCREC_MAX_REQ_RUN_EMIT` IS TRUNCATED, NEVER SPLIT into
 * two compares: to the window of that length containing the scan member whose
 * bytes sum to the LOWEST prior (ties leftmost), and under any other encoding
 * to the leftmost window containing it — Frank's ruling of 2026-09-22
 * ("that is precisely the sort of precompiling analysis that gives this
 * project its advantage"). A second compare would be a second mechanism with
 * its own cost question and no measured need (D77).
 *
 * THE SAFE DIRECTION IS THE EMPTY SET AND THE EMPTY RUN, which DISABLE the
 * check. Every arm that cannot decide takes it: a class with more than one
 * member (which is every caselessly-folded literal, since D23 folds `(?i)a`
 * to `[aA]` at parse time), a quantifier that admits zero iterations, a
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
 * is one; and every caselessly folded literal contributes nothing, which is
 * the largest decline by population and whose remedy is `[WORD-FOLD]`'s
 * masked compare, a separate row.
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
 * Called from `src/core/compile.c` after `pcrec_lower_enc` and before either
 * emitter, into `Job.req_byte` and `Job.req_run`. */

#include <string.h>

#include "core/internal.h"

/* A set of necessary bytes plus the member the emitter will use. `pick` is
 * -1 exactly when the set is empty, and is always a member of the set when it
 * is not — an invariant every operation below restores rather than assumes. */
typedef struct { unsigned char bits[32]; int pick; } RbSet;

/* A necessary CONTIGUOUS run, bounded so the walk's per-frame state cannot
 * grow with the pattern (`PCREC_MAX_REQ_RUN_SCAN`'s limits.def row says why).
 *
 * `trunc` means the real run is LONGER than the `n` bytes stored, and every
 * truncation is sound in the only direction that matters: a contiguous
 * substring of a necessary contiguous run is itself one. What differs by ROLE
 * is which END is kept, and the two append helpers below carry that as a
 * stated precondition rather than as a convention — a HEAD keeps its first
 * bytes (so its first byte is still the match's first), a TAIL keeps its last
 * (so its last byte is still the match's last), and `best` keeps whichever
 * the operation that built it produced. */
typedef struct { unsigned char bytes[PCREC_MAX_REQ_RUN_SCAN]; int n; bool trunc; } RbRun;

/* The three runs a subtree contributes, plus the one flag that says whether
 * the next concatenation may join across it.
 *
 * `all` is "this subtree's language is EXACTLY the one literal string `head`,
 * and all of it is stored". It is what makes `head` extendable by the factor
 * to the right, and it is FALSE the moment a run truncates — otherwise a
 * 20,000-byte literal would report its stored first bytes as adjacent to
 * whatever follows the literal, which is 19,968 bytes of a lie. */
typedef struct { RbRun best, head, tail; bool all; } RbRuns;

/* The two facts, threaded together because they come off one walk. */
typedef struct { RbSet set; RbRuns runs; } RbVal;

static bool rb_has(const RbSet *s, int b)
{
    return b >= 0 && (s->bits[b >> 3] & (unsigned char)(1u << (b & 7))) != 0;
}

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
 * a run, and WHICH member of it the scan tests is decided once, at the
 * bottom of this file. */

static RbRun rn_none(void)
{
    RbRun r;
    memset(r.bytes, 0, sizeof r.bytes);
    r.n = 0;
    r.trunc = false;
    return r;
}

static RbRun rn_byte(int b)
{
    RbRun r = rn_none();
    r.bytes[0] = (unsigned char)b;
    r.n = 1;
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
    for (i = 0; i < b.n && o.n < PCREC_MAX_REQ_RUN_SCAN; i++)
        o.bytes[o.n++] = b.bytes[i];
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
    for (i = drop; i < tot; i++)
        o.bytes[o.n++] = i < a.n ? a.bytes[i] : b.bytes[i - a.n];
    o.trunc = a.trunc || b.trunc || drop > 0;
    return o;
}

/* The longer of two runs, `a` on a tie — so a left-to-right walk's earlier
 * candidate survives and the answer does not depend on traversal order. */
static RbRun rn_longer(RbRun a, RbRun b)
{
    return b.n > a.n ? b : a;
}

/* The two branches' longest COMMON PREFIX, claimed conservatively: only the
 * bytes both actually store. A longer real common prefix is a missed
 * opportunity, never an unsound claim, and the result is marked untruncated
 * because it IS the whole of what is claimed. */
static RbRun rn_common_head(RbRun a, RbRun b)
{
    RbRun o = rn_none();
    while (o.n < a.n && o.n < b.n && a.bytes[o.n] == b.bytes[o.n]) {
        o.bytes[o.n] = a.bytes[o.n];
        o.n++;
    }
    return o;
}

/* The two branches' longest COMMON SUFFIX, compared from the back for the
 * same reason and with the same conservatism. */
static RbRun rn_common_tail(RbRun a, RbRun b)
{
    RbRun o = rn_none();
    int k = 0;
    while (k < a.n && k < b.n && a.bytes[a.n - 1 - k] == b.bytes[b.n - 1 - k]) k++;
    for (int i = 0; i < k; i++) o.bytes[i] = a.bytes[a.n - k + i];
    o.n = k;
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
    return r;
}

/* Everything declined: no run, and no permission to join across this
 * subtree. */
static RbRuns rr_none(void)
{
    RbRuns r = rr_unit();
    r.all = false;
    return r;
}

/* A subtree that matches exactly the one byte `b`. */
static RbRuns rr_byte(int b)
{
    RbRuns r;
    r.best = r.head = r.tail = rn_byte(b);
    r.all = true;
    return r;
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
    o.head = l.all ? rn_app(l.head, r.head) : l.head;
    o.tail = r.all ? rn_pre(l.tail, r.tail) : r.tail;
    o.all  = l.all && r.all && !o.head.trunc;
    o.best = rn_longer(rn_longer(l.best, r.best), rn_app(l.tail, r.head));
    o.best = rn_longer(rn_longer(o.best, o.head), o.tail);
    return o;
}

/* ALTERNATION of runs: only what every branch guarantees, which at the
 * contiguity grain is the common prefix and the common suffix and nothing
 * between them. `all` is false even when both branches are the same literal:
 * the general fact an alternation licenses is "these bytes are common", and a
 * same-literal special case would buy a population this analysis has never
 * measured (D77). */
static RbRuns rr_alt(RbRuns l, RbRuns r)
{
    RbRuns o;
    o.head = rn_common_head(l.head, r.head);
    o.tail = rn_common_tail(l.tail, r.tail);
    o.best = rn_longer(o.head, o.tail);
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
static RbVal rb_walk(const Ast *a)
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
            RbVal r = rb_walk(a->r);
            acc.set  = rb_union(r.set, acc.set);
            acc.runs = rr_cat(r.runs, acc.runs);
            a = a->l;
            continue;
        }
        case A_CAP:
        case A_ATOMIC:
            /* Transparent: a group matches what its body matches, and an
             * atomic cut removes MATCHES rather than bytes, so every string
             * the group matches is one the body matches. */
            a = a->l;
            continue;
        case A_ALT: {
            const Ast *t = a->l;
            RbVal r = rb_walk(a->r), b;
            while (t->k == A_ALT) {
                b = rb_walk(t->r);
                r.set  = rb_intersect(b.set, r.set);
                r.runs = rr_alt(b.runs, r.runs);
                t = t->l;
            }
            b = rb_walk(t);
            r.set  = rb_intersect(b.set, r.set);
            r.runs = rr_alt(b.runs, r.runs);
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
                RbVal b = rb_walk(a->l);
                RbRuns rep = rr_none();
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
             * exactly as a multi-member class is. */
            acc.runs = rr_cat(rr_none(), acc.runs);
            return acc;
        case A_CLASS: {
            int b = pcrec_cls_single(a);
            if (b < 0) {
                /* A class of more than one member contributes no byte and no
                 * run, and it also BREAKS contiguity for everything around
                 * it — which `rr_none`'s cleared `all` is exactly what says. */
                acc.runs = rr_cat(rr_none(), acc.runs);
                return acc;
            }
            acc.set  = rb_union(rb_single(b), acc.set);
            acc.runs = rr_cat(rr_byte(b), acc.runs);
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
        case A_WORDB:
        case A_NWORDB:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
        /* The two deliberate declines, `src/opt/startanch.c`'s for the same
         * reasons: a backreference's bytes are the subject's business and a
         * linked call's body is `callgraph.c`'s cycle problem. Both are the
         * empty set, which disables the check — always sound. */
        case A_BREF:
        case A_CALL:
            acc.runs = rr_cat(rr_none(), acc.runs);
            return acc;
        }
    }
}

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
 * prior, ties to the LEFTMOST — and the leftmost outright where the prior
 * does not apply (reqpos_2b.md §2.3). The per-candidate cost of the whole run
 * check is the number of occurrences of THIS byte in the window, which is why
 * the choice is not cosmetic. */
static int rn_scan_index(const RbRun *r, bool bytekey)
{
    int i, best = 0;
    unsigned lo;
    if (!bytekey) return 0;
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

/* THE ARTIFACT-LEVEL ANSWER, for both facts, at ONE return. See the header
 * for why the empty set and the empty run are the safe answers, why the
 * member returned is the argmin of a frequency prior under `byte` and the
 * rightmost elsewhere, and why a run's presence MOVES the byte: there is one
 * emitted `memchr`, and `<PREFIX>_REQ_BYTE` reports what it tests. */
int pcrec_req_byte(Ctx *cx, const Ast *root, bool run_ok, ReqRun *run)
{
    bool bytekey = cx->opt->encoding == PCREC_ENC_BYTE;
    RbVal v = rb_walk(root);
    RbRun r = v.runs.best;

    memset(run->bytes, 0, sizeof run->bytes);
    run->len = 0;
    run->idx = 0;

    if (run_ok && r.n >= 2) {
        int i = rn_scan_index(&r, bytekey);
        int s = r.n > PCREC_MAX_REQ_RUN_EMIT ? rn_window_start(&r, i, bytekey) : 0;
        int len = r.n - s;
        if (len > PCREC_MAX_REQ_RUN_EMIT) len = PCREC_MAX_REQ_RUN_EMIT;
        memcpy(run->bytes, r.bytes + s, (size_t)len);
        run->len = len;
        run->idx = i - s;
        return run->bytes[run->idx];
    }
    return rb_pick(&v.set, bytekey);
}
