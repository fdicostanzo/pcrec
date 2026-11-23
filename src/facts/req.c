/* src/facts/req.c — [OPT-REQBYTE] + [OPT-REQPOS] tier 2b THE NECESSARY SET AND
 * THE NECESSARY LITERAL RUN: a byte every match of this pattern must contain, and the
 * longest run of contiguous bytes every match must contain.
 *
 * One AST-level analysis, read by BOTH emitters through the pattern-facts
 * record (the `req_set`/`req_whole_run` facts it derives, and the
 * `req_byte` fact derived at the foot of this file). With it,
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
 * folds `(?i)a` to `[aA]` at parse time) and for the RUN a class outside the
 * position domain (below), a quantifier that admits zero iterations (of a
 * body that consumes something: a width-0 body is CAT's unit, span_arms T2
 * row 1), a backreference and a linked call. A node that consumes nothing
 * (the empty string, an assertion, `\G`, `\K`, a check callout, a
 * lookaround) is CAT's width-0 unit for the run (span_arms T3,
 * `rb_zero_rows`; `restore=empty`/`restore=zero` put the old cuts back): the
 * bytes on its two sides are adjacent in the subject.
 *
 * A POSITIVE LOOKAROUND'S BODY IS READ, BUT ITS BYTES NEVER JOIN THE RUN OR
 * THE SET AS CONSUMED BYTES (docs/design/span_arms.md §5.1, §14.3 D-1..D-4,
 * unit L1): a LOOKBEHIND's bytes sit BEFORE the match's start and can be
 * outside `[search_from, subject_length)` entirely, and a lookahead's past
 * its end, which would make the check unsound in the direction that deletes
 * matches. What leaves the body is its ITEM, the per-offset byte sets every
 * match of it implies at signed offsets from its cursor, carried as GUARDS
 * (`RbRuns.lg`/`rg`) that MEET the consumed positions beside it at equal
 * subject offsets: a guard only NARROWS a consumed position (both are
 * necessary conditions on the same subject byte), never adds one. An empty
 * meet is a contradiction, the never bit (`RbRuns.never`, the never family's
 * rows, kindrow.def's NEVER column), listed as `req_whole_run`'s why `dead`.
 * Each meet that narrows a consumed position to one byte puts that byte in
 * the set where it meets (CAT-SET, `rr_cat`), whatever run TOP later
 * chooses, so the set stays a CORE fact. At the walk's exit TOP offers the
 * guards still standing at the root as candidate runs (`rb_top_rows`; span
 * arms L3: BACK, the left guard joined to the head, a run that begins up to
 * the declared lookbehind length before the attempt start, its CONSUMED
 * extent kept beside it) and drops the rest. A lookbehind byte still never
 * joins the SET, and `req_byte` reads only the run's consumed extent.
 *
 * WHAT THE RUN DECLINES BEYOND THAT, each with its reason rather than a
 * shared "be careful" (reqpos_2b.md §2.4): an alternation contributes only
 * its branches' longest COMMON prefix and common suffix, so
 * `(?:xabcy|zabcw)` reports no run where `abc` is one.
 *
 * A REPEAT IS ITS COPIES (docs/design/span_arms.md §3, T2 rows 2-3, D191):
 * `X{m,n}` reads as `X^m · X{0,n-m}` for its head and best and as
 * `X{0,n-m} · X^m` for its tail, so `xy(?:ab){2}zw` is the run `xyababzw`
 * and the join between two copies is CAT's own join. Only the copies every
 * match takes count: the optional part is a gap, and it never carries the
 * fixed copies' offset. The copies are unrolled only until one more changes
 * no stored byte (`rr_pow_count`); the width is always the repeat's exact
 * one (`rr_rep_w`).
 *
 * [OPT-LITSCAN] S4 C3 A RUN IS A RUN OF POSITIONS, NOT OF BYTES
 * (docs/design/litscan_s4.md §2.3.1), and since [RUN-POS-SET] stage 3 a
 * position is the BYTE SET every match holds there (D187;
 * docs/design/alt_normal_form.md §5 stage 3), admitted by the walk's DOMAIN
 * (`rn_admits`: at most `pos_set` members, and, while the domain's cube
 * clause holds, one cube), so a caseless word, a digit class or a UTF-8
 * continuation set is a run where it used to cut one. Three rules make that
 * one mechanism rather than a second one beside the byte run:
 *   - ONE RANKING: a run's worth is its INFORMATION, `8 - ceil(log2 |S|)`
 *     summed over its positions (`pcrec_req_info`: 8 for a byte, 7 for a
 *     pair, 0 past 128 members), so among exact runs the order is exactly
 *     length's (`rn_choice_rows`, whose later rows break an
 *     equal-information tie by the byte-rate, never by argument order);
 *   - ONE CONSTRUCTOR, `rn_put`, refuses a set outside the domain (the
 *     empty set among it) as an internal error rather than dropping it;
 *   - an alternation's common head and tail are the per-position UNION of
 *     the two branches' sets (the smallest set holding both), symmetric in
 *     the branches and stopping at the first position whose union leaves
 *     the domain — so `frank|fred` reports `fr[ae]`, `(?:S(?i:ab)|(?i:sab))`
 *     reports `[Ss][Aa][Bb]`, never the left branch's exact `S`, and `cat|dog`
 *     (outside the cube clause) `[cd][ao][tg]`, a joint superset: each
 *     position holds, the run need not be one of the matches' strings.
 * A covering cube is a reader's private spelling, rebuilt from the set
 * (`pcrec_req_cube`, D187 addendum 1), never stored. Under
 * `-fno-req-run-fold` `pos_set` is 1, the domain is the single byte, the
 * union is byte equality and the walk is the pre-row one exactly. The SET is
 * unchanged by all of this: only an exact position is a set member.
 *
 * [K82] THE RUN CARRIES ITS MAXIMUM BYTE OFFSET FROM THE ATTEMPT START
 * (`RbRun.off`, docs/design/litscan_k82h.md §1.3), and only this walk can
 * compute it, because only the walk knows WHICH occurrence its run came from
 * (a left factor, a right factor or a join). Each subtree also carries its
 * maximum width in BYTES (`RbRuns.maxw`, saturating at `PCREC_W_UNBOUNDED`
 * through `pcrec_sat_add`/`pcrec_sat_mul`): a head sits at 0 in every match,
 * a tail at `maxw - n` or earlier, a right factor's run `maxw(left)` further
 * in, and a repeat's run in its FIRST iteration. The offset is an
 * ANNOTATION: `rn_choice_rows` ranks by information and then rarity, and
 * reads the offset only to break a tie those leave, so no run is chosen for
 * being bounded. It is NOT `pcrec_cwmax`, which counts characters: on
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
 * THE SET IS A CORE FACT AND THE PICK IS NOT ([PATFACTS] step 3.0,
 * docs/design/patfacts/design.md §4.1): this file answers WHAT every match
 * must contain — the whole SET (with its threaded rightmost member, the
 * tiebreak the pick falls back on), reading no prior, and the most
 * informative guaranteed RUN, a DERIVED fact since its equal-information
 * ties are broken by the byte-rate the walk is handed (`rn_choice_rows`,
 * review 2026-11-09 r5). WHICH member the emitted `memchr` tests, and which 8-byte window
 * of a longer run is compared, are SPEED choices made from these answers by
 * the rate readers beside the rate primitives (`src/core/findings.c`,
 * [FINDINGS] B1), composed into the derived facts at the foot of this file.
 * The lattice's helpers are `static` here, so a consumer that
 * wanted this answer another way would have to re-spell the whole walk.
 *
 * Called by the pattern-facts record (`src/facts/facts.c`) on the first ask
 * of `req_set` or `req_whole_run`, over the LOWERED tree the E2 seal recorded
 * after `pcrec_lower_enc`; both facts come off one call. */

#include <stddef.h>
#include <string.h>

#include "core/internal.h"
#include "core/findings.h"
#include "facts/facts_derive.h"
#include "facts/desc.h"



/* The three runs a subtree contributes, plus the one flag that says whether
 * the next concatenation may join across it.
 *
 * `all` is "this subtree's language is EXACTLY the one literal string `head`,
 * and all of it is stored". It is what makes `head` extendable by the factor
 * to the right, and it is FALSE the moment a run truncates — otherwise a
 * 20,000-byte literal would report its stored first bytes as adjacent to
 * whatever follows the literal, which is 19,968 bytes of a lie. */
typedef struct {
    RbRun best, head, tail;
    bool all;
    long long maxw;
    /* span_arms L1 (§14.3 D-2) THE GUARDS: byte sets every match of the
     * subtree implies OUTSIDE it, read from a positive lookaround's item.
     * `lg` at the offsets `[-lg.n, 0)` before the subtree's START (its LAST
     * positions kept, the ones nearest that edge, `rn_pre`), `rg` at `[0,
     * rg.n)` after its END (its FIRST kept, `rn_app`). Never consumed bytes:
     * a guard only narrows a consumed position it meets (`rr_cat`'s steps)
     * and is dropped at the walk's exit (TOP). */
    RbRun lg, rg;
    /* the NEVER bit: no match of the subtree exists (§14.3 D-9) */
    bool never;
} RbRuns;

/* The facts, threaded together because they come off one walk: the set, the
 * runs, ([RUN-POS-SET] stage 2p) the piece description (desc.h) and (span
 * arms L1, D-10) the adjacency HEAD, computed only while the walk is inside a
 * positive lookahead's body (`RbWalk.ahead`), the one reader of it. */
typedef struct { RbSet set; RbRuns runs; PdDesc desc; PdHead head; } RbVal;


static RbSet rb_empty(void)
{
    RbSet s;
    memset(s.bits, 0, sizeof s.bits);
    memset(s.off, 0, sizeof s.off);
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
 * (and the whole answer under every encoding but `byte`).
 *
 * [REQ-HANDOFF-L1] THE OFFSETS, `RbRun.off`'s rule for a right factor: `r`
 * begins at most `lmaxw` bytes in (the left factor's maximum width), so a
 * member only `r` carries sits at `lmaxw + off_r`. A member BOTH carry has
 * two guaranteed occurrences, either of which is a first-occurrence bound,
 * so the nearer one holds. Every arm that puts width to the left of the
 * accumulated right-hand side calls this with that width and an empty `l`,
 * which is a pure shift. */
static RbSet rb_union(RbSet l, RbSet r, long long lmaxw)
{
    int i;
    for (i = 0; i < 256; i++) {
        long long ro;
        if (!rb_has(&r, i)) continue;
        ro = pcrec_sat_add(lmaxw, r.off[i], PCREC_W_UNBOUNDED);
        if (ro >= RB_OFF_UNBOUNDED) ro = RB_OFF_UNBOUNDED;
        if (!rb_has(&l, i) || ro < l.off[i]) l.off[i] = (uint32_t)ro;
    }
    for (i = 0; i < 32; i++) l.bits[i] |= r.bits[i];
    if (r.pick >= 0) l.pick = r.pick;
    return l;
}

/* ALTERNATION: only a byte necessary for BOTH branches is necessary for the
 * alternation. The pick rule is stated in the header; the final fallback
 * scans DOWN so "the largest surviving byte" is reached in one pass.
 * [REQ-HANDOFF-L1] Either branch may be the one that matched, so a member's
 * bound is the FARTHER of its two. */
static RbSet rb_intersect(RbSet l, RbSet r)
{
    RbSet out;
    int i;
    for (i = 0; i < 32; i++) out.bits[i] = (unsigned char)(l.bits[i] & r.bits[i]);
    for (i = 0; i < 256; i++) out.off[i] = l.off[i] > r.off[i] ? l.off[i] : r.off[i];
    out.pick = -1;
    if (rb_has(&out, r.pick))       out.pick = r.pick;
    else if (rb_has(&out, l.pick))  out.pick = l.pick;
    else for (i = 255; i >= 0; i--) if (rb_has(&out, i)) { out.pick = i; break; }
    return out;
}

/* ---- THE RUN ACCUMULATOR -------------------------------------------------
 *
 * Seven operations, of which only the two append helpers have a precondition
 * and both state it. Only the run choice reads the prior, through the rate
 * primitives, to break an equal-information tie (`rn_choice_rows`); WHICH
 * member of the run pcrec's own pick tests is decided once, by
 * `pcrec_req_pick` below, through `src/core/findings.c`. */

/* What every run operation needs besides its operands: the compile (for the
 * position constructor's refusal), and from the walk parameters
 * `pcrec_req_walk`'s caller hands in (`ReqWalkParams`, span_arms §3.7) the
 * largest member set one position may have, the restored arms and the
 * byte-rate the run choice breaks ties by (`rn_choice_rows`). The rest
 * is `rb_walk`'s
 * own: its per-level result storage, `slot[d]` two `RbVal`s for the children
 * of the walk at recursion depth `d`, so a value never sits in a C frame
 * ([DD-10]: one `RbVal` is over a kilobyte, and the walk recurses once per
 * nesting level). */
typedef struct {
    Ctx *cx;
    int pos_set;     /* the domain: a position's largest member count */
    unsigned restored;
    const uint32_t *rate;   /* the byte-rate, for the run choice's tie row */
    int depth, nslot;
    RbVal **slot;
    /* [RUN-POS-SET] stage 2p: the description's bounds and byte alphabet,
     * and the one-byte position sets, built on first use. */
    PdCfg pd;
    const unsigned char *single[256];
    /* span_arms L1: the encoding's one-byte repertoire (the `A_CTX` item's
     * bound, `ReqWalkParams.onebyte_max`), and how many positive lookahead
     * bodies the walk is inside: the head (`RbVal.head`) is built only then,
     * so a 20,000-byte literal outside one pays nothing for it */
    unsigned onebyte_max;
    int ahead;
    /* span_arms L3 (D-11): TOP's BACK row's cap, `ReqWalkParams.lb_bytes` */
    long long lb_bytes;
    /* review r65 A: `ReqWalkParams.fwd_reentry`, read by BACK's `displaces` */
    bool fwd_reentry;
} RbWalk;

/* How many members the position set `p` has. */
static int rn_count(const unsigned char *p)
{
    int c = 0;
    for (int i = 0; i < 32; i++) c += __builtin_popcount(p[i]);
    return c;
}

/* The covering cube of position set `p` (facts.h says what it is for). */
bool pcrec_req_cube(const unsigned char *p, int *t, int *k)
{
    int a = 0xFF, o = 0;
    for (int b = 0; b < 256; b++)
        if ((p[b >> 3] >> (b & 7)) & 1) { a &= b; o |= b; }
    *t = a;
    *k = ~(a ^ o) & 0xFF;
    return rn_count(p) == 1 << (8 - __builtin_popcount((unsigned)*k));
}

/* Is the position set `p` inside the walk's DOMAIN: at least one and at
 * most `pos_set` members? */
static bool rn_admits(const RbWalk *w, const unsigned char *p)
{
    int c = rn_count(p);
    return c >= 1 && c <= w->pos_set;
}

/* A position's information, 8 - ceil(log2 |p|) (0 for the empty set). */
int pcrec_req_info(const unsigned char *p)
{
    int c = rn_count(p), lg = 0;
    while ((1 << lg) < c) lg++;
    return c < 1 ? 0 : 8 - lg;
}

/* A run's INFORMATION, the ranking's unit: the sum of its positions'. */
static int rn_info(const RbRun *r)
{
    int t = 0;
    for (int i = 0; i < r->n; i++) t += pcrec_req_info(r->pos[i]);
    return t;
}

static RbRun rn_none(void)
{
    RbRun r;
    memset(r.pos, 0, sizeof r.pos);
    r.n = 0;
    r.trunc = false;
    r.off = 0;
    return r;
}

/* THE ONE CONSTRUCTOR of a run position: appends the set `p` to `o` (whose
 * room the caller has checked). A set outside the walk's domain — the empty
 * set among it — is refused as an internal error, never silently dropped:
 * every producer asks `rn_admits` first, so this fires only on a producer's
 * bug, and loudly, as `ofsk_emit_verify` refuses an empty chain. */
static void rn_put(const RbWalk *w, RbRun *o, const unsigned char *p)
{
    if (!rn_admits(w, p))
        pcrec_ctx_fail(w->cx, 0, "internal error: a necessary-run position of %d "
                       "members lies outside the walk's domain (src/facts/req.c)",
                       rn_count(p));
    o->pos[o->n++] = p;
}

/* The run of the one position `p`. */
static RbRun rn_pos(const RbWalk *w, const unsigned char *p)
{
    RbRun r = rn_none();
    rn_put(w, &r, p);
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
    for (i = 0; i < b.n && o.n < PCREC_MAX_REQ_RUN_SCAN; i++) o.pos[o.n++] = b.pos[i];
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
    for (i = drop; i < tot; i++) o.pos[o.n++] = i < a.n ? a.pos[i] : b.pos[i - a.n];
    o.trunc = a.trunc || b.trunc || drop > 0;
    return o;
}

/* THE FIRST-MATCH ROW SCAN, shared by every `{row, arm}` restore table in this
 * file (`rn_choice_rows`, `rr_alt_rows`, `rb_rep_rows`, `rb_zero_rows`; reviews
 * 2026-11-15 r1 posts2 CONTRACT-1, r3 fixposts2 CONTRACT-1/3, r4 fixposts2c
 * RESPELL-2/3). A table holds no CATCH-ALL row: its catch-all is a separate
 * default, taken when the scan runs off the end, so it is reached by
 * construction and carries no arm to be wrong (an arm on a last catch-all row
 * would run the scan off the end; tables without an arm column keep their
 * always-true row). `RB_ROW_SCAN(i, w, TAB, TEST)` leaves in `i` the index of
 * the first row of `TAB` that the walk does not restore and for which `TEST`
 * (which reads the row as `TAB[i]`) holds, or the row count when none does.
 * `TEST` runs at most once per row, so a row that builds its answer (an
 * out-parameter, an arena set) is CAPTURED by the test, never called again. */
#define RB_ROWS(tab) (sizeof (tab) / sizeof (tab)[0])
#define RB_ROW_SCAN(i, w, tab, test)                                        \
    do {                                                                    \
        for ((i) = 0; (i) < RB_ROWS(tab); (i)++)                            \
            if (!((tab)[i].arm & (w)->restored) && (test))                  \
                break;                                                      \
    } while (0)

/* THE ALL-ROWS SCAN, `RB_ROW_SCAN`'s sibling for a COMBINING table (span_arms
 * L1, §14.3 D-4, review r51 CONFORM-2: TOP): `BODY` runs, with the row as
 * `TAB[i]`, for EVERY row of `TAB` the walk does not restore and for which
 * `TEST` holds, in table order; no row stops the scan. (`!=`, not `<`: a
 * table may have no rows yet, TOP at L1, and `< 0` on a `size_t` is a
 * -Wtype-limits warning.) */
#define RB_ROW_EACH(i, w, tab, test, body)                                  \
    do {                                                                    \
        for ((i) = 0; (i) != RB_ROWS(tab); (i)++)                           \
            if (!((tab)[i].arm & (w)->restored) && (test)) { body; }        \
    } while (0)

/* THE RUN CHOICE: which of two candidate runs a subtree keeps as its best.
 * A declared first-match table of comparison rows (`rn_choice_rows`); each
 * row answers > 0 for `a`, < 0 for `b`, or 0 to pass the tie to the next
 * row. Every row reads only the two runs and is antisymmetric, so the choice
 * depends on neither the argument order nor the pattern's spelling: a repeat
 * and its unrolled literal keep the same run (review 2026-11-09 r5 EMIT-1,
 * EMIT-2; span_arms §12d). */
typedef int (*RnChoiceRow)(const RbWalk *w, const RbRun *a, const RbRun *b);

/* Row 1, the ranking: the more INFORMATIVE run (`rn_info`). An exact run's
 * information is 8 x its length, so among exact runs this is "the longer". */
static int rn_more_info(const RbWalk *w, const RbRun *a, const RbRun *b)
{
    (void)w;
    return rn_info(a) - rn_info(b);
}

/* What the emitted scan of run `r` costs: the byte-rate mass of the members
 * of its scan position, the one `pcrec_find_run_scan_index` picks over EVERY
 * run position, the scan the kit may place on any of them (D191.2). Since
 * span_arms L3 this is not the `req_byte` pick, which reads only the run's
 * consumed extent (§14.3 D-4, D-6); the ranking follows the kit's scan. 0 for
 * the empty run, which has none. */
static uint32_t rn_scan_mass(const RbWalk *w, const RbRun *r)
{
    if (r->n == 0) return 0;
    return pcrec_find_pos_mass(w->rate, r->pos[pcrec_find_run_scan_index(w->rate, r->pos, r->n)]);
}

/* Row 2, at equal information: the RARER run, its scan position's mass
 * the smaller. Under NONE the mass is the member count, so it ties wherever
 * both scan positions are exact bytes. */
static int rn_rarer(const RbWalk *w, const RbRun *a, const RbRun *b)
{
    uint32_t ma = rn_scan_mass(w, a), mb = rn_scan_mass(w, b);
    return ma < mb ? 1 : ma > mb ? -1 : 0;
}

/* Row 3, at equal information and rarity: the run with the smaller [K82]
 * offset bound, the earlier occurrence of a tie a walk meets twice. */
static int rn_nearer(const RbWalk *w, const RbRun *a, const RbRun *b)
{
    (void)w;
    return a->off < b->off ? 1 : a->off > b->off ? -1 : 0;
}

/* Row 4, the last: content order (length, then each position's covering
 * cube `(t, k)` by `t` then `k`, then its set, then truncation), a total
 * order on what a run states. Two runs it calls equal are the same run at
 * the same offset. On cube positions the cube IS the set, so the order is
 * the pre-set one exactly (stage 3 moves no tie between cube runs). */
static int rn_content(const RbWalk *w, const RbRun *a, const RbRun *b)
{
    (void)w;
    if (a->n != b->n) return a->n < b->n ? 1 : -1;
    for (int i = 0; i < a->n; i++) {
        int ta, ka, tb, kb, c;
        pcrec_req_cube(a->pos[i], &ta, &ka);
        pcrec_req_cube(b->pos[i], &tb, &kb);
        if (ta != tb) return ta < tb ? 1 : -1;
        if (ka != kb) return ka > kb ? 1 : -1;
        if ((c = memcmp(a->pos[i], b->pos[i], 32)) != 0) return c < 0 ? 1 : -1;
    }
    return (int)b->trunc - (int)a->trunc;
}

/* The default of `rn_choice_rows`, the restored tie form: at equal information, `a`. */
static int rn_first(const RbWalk *w, const RbRun *a, const RbRun *b)
{
    (void)w;
    (void)a;
    (void)b;
    return 1;
}

static const struct {
    RnChoiceRow row;
    unsigned arm;   /* the restored arm (walk_arms.def) that passes it over */
} rn_choice_rows[] = {
    { rn_more_info, 0 },
    /* the tie rule (span_arms R1, D191): rarity, then offset, then content */
    { rn_rarer,     PCREC_WALK_ARM(TIE) },
    { rn_nearer,    PCREC_WALK_ARM(TIE) },
    { rn_content,   PCREC_WALK_ARM(TIE) },
};

/* THE RUN CHOICE's SIGN for `a` against `b`: > 0 keeps `a`, < 0 keeps `b`,
 * from the first row of `rn_choice_rows` that decides and that the walk does
 * not restore; none deciding, the replaced form (`rn_first`, the default):
 * `a`. The one comparator of the run choice, split out of `rn_better` so a
 * caller that keeps more than the run beside each candidate (an extent kept
 * beside its run) asks the same choice, and the two cannot drift. */
static int rn_cmp(const RbWalk *w, const RbRun *a, const RbRun *b)
{
    size_t i;
    int c;
    RB_ROW_SCAN(i, w, rn_choice_rows,
                (c = rn_choice_rows[i].row(w, a, b)) != 0);
    if (i == RB_ROWS(rn_choice_rows)) c = rn_first(w, a, b);
    return c;
}

/* The better of two runs by the run choice (`rn_cmp`): `a` unless it keeps `b`. */
static RbRun rn_better(const RbWalk *w, RbRun a, RbRun b)
{
    return rn_cmp(w, &a, &b) >= 0 ? a : b;
}

static const void *rb_pd_join(Ctx *cx, const void *a, const void *b);

/* The two branches' longest COMMON PREFIX, position by position the UNION
 * of their sets (the smallest set holding both), claimed conservatively: only
 * positions both actually store, and only while the union stays inside the
 * walk's domain (`rn_admits`). A longer real common prefix is a missed
 * opportunity, never an unsound claim — every byte either branch can put at
 * position `i` lies in the union — and the result is marked untruncated
 * because it IS the whole of what is claimed. */
static RbRun rn_common_head(const RbWalk *w, RbRun a, RbRun b)
{
    RbRun o = rn_none();
    while (o.n < a.n && o.n < b.n) {
        const unsigned char *u = rb_pd_join(w->cx, a.pos[o.n], b.pos[o.n]);
        if (!rn_admits(w, u)) break;
        rn_put(w, &o, u);
    }
    return o;
}

/* The two branches' longest COMMON SUFFIX, unioned from the back for the same
 * reason and with the same conservatism. */
static RbRun rn_common_tail(const RbWalk *w, RbRun a, RbRun b)
{
    RbRun o = rn_none();
    const unsigned char *u[PCREC_MAX_REQ_RUN_SCAN];
    int k = 0;
    while (k < a.n && k < b.n) {
        u[k] = rb_pd_join(w->cx, a.pos[a.n - 1 - k], b.pos[b.n - 1 - k]);
        if (!rn_admits(w, u[k])) break;
        k++;
    }
    for (int i = k - 1; i >= 0; i--) rn_put(w, &o, u[i]);
    return o;
}

/* ---- THE GUARDS' MEET (span_arms L1, §14.3 D-3) ---------------------------
 *
 * A guard is a NECESSARY condition on subject bytes outside a subtree, as a
 * consumed position is one on a byte inside it, so where the two fall on the
 * same subject offset the byte lies in both sets: their INTERSECTION is the
 * position. Every meet below is at EQUAL subject offsets, aligned at a
 * shared edge, and none moves an offset. Positions are the byte SETS the
 * run's domain admits (D187 addendum 1: a cube is a reader's private
 * spelling, so the meet is of sets, never of hulls); a nonempty intersection
 * of two admitted sets is admitted. */

/* The intersection of the position sets `a` and `b`: one of them where it is
 * a subset of the other (no allocation), NULL where it is empty. */
static const unsigned char *rn_meet_pos(const RbWalk *w, const unsigned char *a,
                                        const unsigned char *b)
{
    bool as = true, bs = true, any = false;
    for (int i = 0; i < 32; i++) {
        if (a[i] & ~b[i]) as = false;
        if (b[i] & ~a[i]) bs = false;
        if (a[i] & b[i]) any = true;
    }
    if (!any) return NULL;
    if (as) return a;
    if (bs) return b;
    unsigned char *u = pcrec_arena_alloc(&w->cx->arena, 32);
    for (int i = 0; i < 32; i++) u[i] = a[i] & b[i];
    return u;
}

/* THE ONE MEET: run `a` met with the guard `g` position by position from
 * their shared edge (`last`: both end there, read backwards; else both begin
 * there). EMPTY-MEET's rule is inside it, and `*empty` reports it: where `a`
 * is CONSUMED (`!guard`) an empty position keeps `a`'s un-narrowed value and
 * the result is `a`'s length; where both are guards the result reaches as far
 * as either and an empty position is dropped with everything outward of it.
 * `a`'s offset and truncation are kept. */
static RbRun rn_meet(const RbWalk *w, RbRun a, const RbRun *g, bool last,
                     bool guard, bool *empty)
{
    const unsigned char *u[PCREC_MAX_REQ_RUN_SCAN];
    int n = guard && g->n > a.n ? g->n : a.n;
    for (int k = 0; k < n; k++) {
        const unsigned char *pa = k < a.n ? a.pos[last ? a.n - 1 - k : k] : NULL;
        const unsigned char *pg = k < g->n ? g->pos[last ? g->n - 1 - k : k] : NULL;
        const unsigned char *m = pa && pg ? rn_meet_pos(w, pa, pg) : pa ? pa : pg;
        if (!m) {
            *empty = true;
            if (guard) { n = k; break; }
            m = pa;
        }
        u[k] = m;
    }
    RbRun o = rn_none();
    o.trunc = a.trunc;
    o.off = a.off;
    for (int k = 0; k < n; k++) rn_put(w, &o, u[last ? n - 1 - k : k]);
    return o;
}

/* Positions `[lo, hi)` of `r`, as a guard (no offset, no truncation). */
static RbRun rn_slice(const RbRun *r, int lo, int hi)
{
    RbRun o = rn_none();
    for (int i = lo; i < hi; i++) o.pos[o.n++] = r->pos[i];
    return o;
}

/* `dst` takes `src`'s positions where it stores as many: an `all` subtree's
 * head, tail and best are the same positions (its one literal string), so a
 * narrowing of one is a narrowing of the three. */
static void rn_same_positions(RbRun *dst, const RbRun *src)
{
    if (dst->n == src->n) memcpy(dst->pos, src->pos, sizeof dst->pos);
}

/* CAT-R: the left factor's `rg` `g` meets the right factor `r`'s first
 * positions (its head; its tail and best too where `r` is `all`); returns
 * the part of `g` past `r`'s head, the leftover CAT-EDGE may carry. */
static RbRun rn_guard_onto_head(const RbWalk *w, RbRuns *r, RbRun g, bool *empty)
{
    if (g.n == 0) return g;
    r->head = rn_meet(w, r->head, &g, false, false, empty);
    if (r->all) {
        rn_same_positions(&r->tail, &r->head);
        rn_same_positions(&r->best, &r->head);
    }
    return rn_slice(&g, g.n < r->head.n ? g.n : r->head.n, g.n);
}

/* CAT-L, the mirror: the right factor's `lg` `g` meets the left factor `l`'s
 * last positions (its tail; its head and best too where `l` is `all`);
 * returns the part of `g` before `l`'s tail. */
static RbRun rn_guard_onto_tail(const RbWalk *w, RbRuns *l, RbRun g, bool *empty)
{
    if (g.n == 0) return g;
    l->tail = rn_meet(w, l->tail, &g, true, false, empty);
    if (l->all) {
        rn_same_positions(&l->head, &l->tail);
        rn_same_positions(&l->best, &l->tail);
    }
    return rn_slice(&g, 0, g.n - (g.n < l->tail.n ? g.n : l->tail.n));
}

/* CAT-EDGE's two meets of guard against guard: `lg`s end at the shared start
 * (read backwards), `rg`s begin at the shared end. */
static RbRun rn_guard_meet_last(const RbWalk *w, RbRun a, RbRun b, bool *empty)
{
    return rn_meet(w, a, &b, true, true, empty);
}

static RbRun rn_guard_meet_first(const RbWalk *w, RbRun a, RbRun b, bool *empty)
{
    return rn_meet(w, a, &b, false, true, empty);
}

/* The identity of run concatenation: the EMPTY STRING, which is entirely
 * literal, so `all` is TRUE. That is not a trick — it is what makes an
 * accumulator seeded with it behave like the concatenation of nothing.
 * It is also THE STATED VALUE every builder below starts from (span_arms
 * RM-1, req_lookaround_arch.md P1): a field added to `RbRuns` is defaulted
 * here once, never silently left unwritten by a field-by-field builder. */
static RbRuns rr_unit(void)
{
    return (RbRuns){ .best = rn_none(), .head = rn_none(), .tail = rn_none(),
                     .all = true, .maxw = 0, .lg = rn_none(), .rg = rn_none(),
                     .never = false };
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

/* A subtree that matches exactly the members of the one position `p`: one
 * byte wide. */
static RbRuns rr_pos(const RbWalk *w, const unsigned char *p)
{
    RbRuns r = rr_unit();
    r.best = r.head = r.tail = rn_pos(w, p);
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

/* CAT-SET (span_arms §5.2's row as first written; review r55 A): each
 * position of the CONSUMED run `after` that a meet narrowed from `before`'s
 * (a new set: `rn_meet_pos` hands back an operand it did not narrow) to ONE
 * byte puts that byte in the concatenation's necessary set `set` at offset
 * `base + i`, if the set lacks it. Every match holds the byte there (the
 * position is consumed, and both conditions are necessary). `*last` takes the
 * byte joined, so the caller can thread the pick. A member the set already has
 * keeps its offset (lowering it is review r55 EMITTED-1's own row). */
static void rr_cat_set_side(RbSet *set, const RbRun *before, const RbRun *after,
                            long long base, int *last)
{
    for (int i = 0; i < after->n; i++) {
        if (after->pos[i] == before->pos[i] || rn_count(after->pos[i]) != 1) continue;
        int b = 0;
        while (!((after->pos[i][b >> 3] >> (b & 7)) & 1)) b++;
        *last = b;
        if (rb_has(set, b)) continue;
        long long o = pcrec_sat_add(base, i, PCREC_W_UNBOUNDED);
        set->off[b] = o >= RB_OFF_UNBOUNDED ? RB_OFF_UNBOUNDED : (uint32_t)o;
        set->bits[b >> 3] |= (unsigned char)(1u << (b & 7));
    }
}

/* CONCATENATION of runs: `l` is to the LEFT of `r` in subject order.
 *
 * The JOIN is the whole point of carrying head and tail runs — `l`'s
 * guaranteed suffix is adjacent to `r`'s guaranteed prefix, so their
 * concatenation is a guaranteed contiguous run even when neither factor is
 * literal on its own. `best` is the longest of the two factors' bests, that
 * join, and the resulting head and tail (which a `\z`-free literal makes the
 * same string, and which is what makes `rr_unit` a real identity).
 *
 * `set` is the concatenation's necessary set (both factors' already, in
 * `o`'s frame), which CAT-SET adds to; NULL where the caller's factor has no
 * consumed position a guard can meet (a gap, a cut, the unit), and a meet
 * that narrows one anyway is an internal error, never a dropped byte. Its
 * pick, where the set had none, becomes the rightmost byte joined, so the
 * pick is -1 exactly when the set is empty (`pcrec_find_set_pick`'s
 * premise); a set that had a pick keeps it (a joined byte is a necessary
 * byte, so the pick is still one). */
static RbRuns rr_cat(const RbWalk *w, RbRuns l, RbRuns r, RbSet *set)
{
    RbRuns o = rr_unit();
    bool empty = false;
    RbRun lt0 = l.tail, rh0 = r.head;
    int last = -1;
    /* span_arms L1 (§14.3 D-3), FIXED STEPS in this order: CAT-R, CAT-L,
     * CAT-SET, the consumed join, CAT-EDGE, never. */
    RbRun rleft = rn_guard_onto_head(w, &r, l.rg, &empty);   /* CAT-R */
    RbRun lleft = rn_guard_onto_tail(w, &l, r.lg, &empty);   /* CAT-L */
    if (set) {                                                /* CAT-SET */
        rr_cat_set_side(set, &lt0, &l.tail, lt0.off, &last);
        rr_cat_set_side(set, &rh0, &r.head, l.maxw, &last);
        if (set->pick < 0) set->pick = last;
    } else if (memcmp(lt0.pos, l.tail.pos, sizeof lt0.pos) ||
               memcmp(rh0.pos, r.head.pos, sizeof rh0.pos)) {
        pcrec_ctx_fail(w->cx, 0, "internal error: a guard narrowed a consumed "
                       "run position where no necessary set was handed in "
                       "(src/facts/req.c rr_cat)");
    }
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
    o.best = rn_better(w, rn_better(w, l.best, rb), join);
    o.best = rn_better(w, rn_better(w, o.best, o.head), o.tail);
    /* CAT-EDGE: a leftover crosses its neighbour only where that neighbour is
     * `all` (exact width, so the leftover's offset from `o`'s edge is known);
     * elsewhere it is dropped. */
    o.lg = l.all && lleft.n ? rn_guard_meet_last(w, l.lg, lleft, &empty) : l.lg;
    o.rg = r.all && rleft.n ? rn_guard_meet_first(w, r.rg, rleft, &empty) : r.rg;
    o.never = pcrec_never_by_row(w->cx, pcrec_kind_row(A_CAT).never,
                                 l.never || r.never, l.never && r.never) || empty;
    return o;
}

/* ALTERNATION of runs: only what every branch guarantees. The outcome is a
 * declared first-match table (`rr_alt_rows`, alt_normal_form.md §6); each row
 * answers whether it applies and, if so, fills `*o`; a row that does not
 * apply leaves `*o` untouched, so the scan hands `*o` to every row and the
 * applying row's answer is the outcome (RB_ROW_SCAN's capture). An applying
 * row writes a COMPLETE value, from `rr_unit` (RM-1). */
typedef bool (*RrAltRow)(const RbWalk *w, const RbRuns *l, const RbRuns *r,
                         RbRuns *o);

/* Row 1 ([RUN-POS-SET] stage 2a rule (1)): both branches `all`, of the same
 * untruncated width, and their per-position UNION inside the walk's domain at
 * every position: the alternation is `all` and its run is that union. Sound
 * because every match of either branch is exactly `n` bytes, each in its
 * branch's set at that position, so in the union. The default since lane
 * r1on (abi 107); the restored arm `alt` passes it over. */
static bool rr_alt_union(const RbWalk *w, const RbRuns *l, const RbRuns *r,
                         RbRuns *o)
{
    int n = l->head.n;
    if (!l->all || !r->all || l->head.trunc || r->head.trunc ||
        r->head.n != n || l->maxw != n || r->maxw != n)
        return false;
    RbRun u = rn_common_head(w, l->head, r->head);
    if (u.n != n) return false;
    *o = rr_unit();
    o->maxw = n;
    o->head = o->tail = o->best = u;
    o->all = true;
    return true;
}

/* Row 2, every other alternation: the common prefix and the common suffix
 * and nothing between them, `all` false. */
static bool rr_alt_affix(const RbWalk *w, const RbRuns *l, const RbRuns *r,
                         RbRuns *o)
{
    *o = rr_unit();
    o->maxw = l->maxw > r->maxw ? l->maxw : r->maxw;
    o->head = rn_common_head(w, l->head, r->head);
    o->head.off = 0;
    o->tail = rn_common_tail(w, l->tail, r->tail);
    o->tail.off = rn_tail_off(o->maxw, o->tail.n);
    o->best = rn_better(w, o->head, o->tail);
    o->all  = false;
    return true;
}

static const struct {
    RrAltRow row;
    unsigned arm;   /* the restored arm (walk_arms.def) that passes it over */
} rr_alt_rows[] = {
    { rr_alt_union, PCREC_WALK_ARM(ALT) },
};

/* Every alternation not taken by a row of `rr_alt_rows`: `rr_alt_affix`, the
 * default. */
static RbRuns rr_alt(const RbWalk *w, RbRuns l, RbRuns r)
{
    size_t i;
    RbRuns o = rr_unit();
    RB_ROW_SCAN(i, w, rr_alt_rows, rr_alt_rows[i].row(w, &l, &r, &o));
    if (i == RB_ROWS(rr_alt_rows)) rr_alt_affix(w, &l, &r, &o);
    /* span_arms L1 (§14.3 D-3) ALT's guard post-step, whatever row answered
     * the consumed part: the guards both branches imply, by the common-head
     * and common-tail rules the consumed part uses (a branch with no guard
     * gives none); `lg` is placed from the alternation's start and `rg` from
     * its end, which is the end of the branch that matched. */
    o.lg = rn_common_tail(w, l.lg, r.lg);
    o.rg = rn_common_head(w, l.rg, r.rg);
    o.never = pcrec_never_by_row(w->cx, pcrec_kind_row(A_ALT).never,
                                 l.never || r.never, l.never && r.never);
    return o;
}

/* The two result slots for the children of the walk at the current depth,
 * allocated the first time the walk reaches that depth and reused after: the
 * storage is bounded by the deepest nesting, not by the node count. */
static RbVal *rb_slots(RbWalk *w)
{
    if (w->depth >= w->nslot) {
        int n = w->nslot ? 2 * w->nslot : 16;
        RbVal **t = pcrec_arena_alloc(&w->cx->arena, (size_t)n * sizeof *t);
        if (w->nslot) memcpy(t, w->slot, (size_t)w->nslot * sizeof *t);
        w->slot = t;
        w->nslot = n;
    }
    if (!w->slot[w->depth])
        w->slot[w->depth] = pcrec_arena_alloc(&w->cx->arena, 2 * sizeof(RbVal));
    return w->slot[w->depth];
}

/* The combining steps, each in its own frame (`PCREC_OWN_FRAME`): the set and
 * run operations pass kilobyte structs by value, and inlined into
 * `rb_walk_at` their temporaries would ride every level of its recursion. */

/* `acc` := the empty answer, the identity of the concatenation. */
static PCREC_OWN_FRAME void rb_init(RbVal *acc)
{
    acc->set  = rb_empty();
    acc->runs = rr_unit();
    acc->desc = pcrec_pd_unit();
    acc->head = pcrec_ph_unit();
}

/* `acc` := `r` followed by `acc`: `r` is to the RIGHT of everything still to
 * be walked and to the LEFT of everything in `acc`, which is why the union and
 * the concatenation are spelled in this order and not the other. */
static PCREC_OWN_FRAME void rb_cat_into(const RbWalk *w, RbVal *acc,
                                        const RbVal *r)
{
    acc->set  = rb_union(r->set, acc->set, r->runs.maxw);
    acc->runs = rr_cat(w, r->runs, acc->runs, &acc->set);
    acc->desc = pcrec_pd_cat(w->cx, &w->pd, r->desc, acc->desc);
    if (w->ahead) acc->head = pcrec_ph_cat(w->cx, &w->pd, r->head, acc->head);
}

/* `r` := the alternation of `b` and `r`: only what both guarantee. */
static PCREC_OWN_FRAME void rb_alt_into(const RbWalk *w, RbVal *r,
                                        const RbVal *b)
{
    r->set  = rb_intersect(b->set, r->set);
    r->runs = rr_alt(w, b->runs, r->runs);
    r->desc = pcrec_pd_alt(w->cx, &w->pd, b->desc, r->desc);
    if (w->ahead) r->head = pcrec_ph_alt(w->cx, &w->pd, b->head, r->head);
}

/* `acc` := a stretch of width `maxw` that makes no byte necessary and breaks
 * every run, followed by `acc`. */
static PCREC_OWN_FRAME void rb_gap_into(const RbWalk *w, RbVal *acc,
                                        long long maxw)
{
    acc->set  = rb_union(rb_empty(), acc->set, maxw);
    acc->runs = rr_cat(w, rr_none(maxw), acc->runs, NULL);
    acc->desc = pcrec_pd_none();
}

/* span_arms L1 (D-10) the head's per-kind rule's POSITION at byte level: a
 * lowered class is its byte set, whether or not the run's domain admits it
 * (a class outside the domain is still a position of the head, or a body
 * like `(?=a.b)` would lose its terms past it; the item's guard is what stops
 * there). `A_WCLASS` is no position: the walk descends to its byte child (it
 * is transparent, `rb_walk_at`), so the rule never sees one from here. */
static const unsigned char *rb_pos_set(RbWalk *w, const Ast *a, int b);

static const void *rb_ph_pos(void *env, const Ast *a)
{
    RbWalk *w = env;
    if (a->k != A_CLASS) return NULL;
    return rb_pos_set(w, a, pcrec_cls_single(w->cx, a));
}

/* `acc`'s head := node `a`'s head (the per-kind rule, `pcrec_ph_node`, its
 * second caller: span_arms D-10, register row 27) followed by `acc`'s; `body`
 * the head of `a`'s one body, or NULL for a leaf. Only inside a positive
 * lookahead's body, the head's one reader here (`RbWalk.ahead`). */
static void rb_head_node(RbWalk *w, RbVal *acc, const Ast *a, const PdHead *body)
{
    if (!w->ahead) return;
    acc->head = pcrec_ph_cat(w->cx, &w->pd,
                             pcrec_ph_node(w->cx, a, body, rb_ph_pos, w), acc->head);
}

/* ---- THE POWER ARM ([REPEAT-RUN], span_arms R1: T2 rows 2-3) ------------- */

/* How many copies of a body with runs `b` the power unrolls for a repeat of
 * at least `m` (span_arms §3.1 point 3): `m`, or fewer where more copies
 * change no CONTENT field (head, tail and best bytes, `all`, `trunc`). A body
 * that is not `all` stops changing at 2, since every later copy adds the
 * same `tail · head` join. An `all` body of width `w` fills the stored head
 * at `ceil(PCREC_MAX_REQ_RUN_SCAN / w)` copies. So the count derives from the
 * run's storage bound and has no constant of its own. Any count up to `m` is
 * sound (`X^c` is a factor of `X^m`). A width-0 body is T2 row 1's and
 * reaches here only with that row restored; every count gives its runs the
 * same value, so it takes 1, and `rr_rep_exact` keeps its `all` (review r5
 * SLOT-2). */
static int rr_pow_count(const RbRuns *b, int m)
{
    int sat = !b->all ? 2
            : b->maxw > 0 ? (int)((PCREC_MAX_REQ_RUN_SCAN + b->maxw - 1) / b->maxw)
            : 1;
    return m < sat ? m : sat;
}

/* `X^c`: `c` copies of the body with runs `b` and set `bs`, through the CAT
 * step (the join between two copies is `rr_cat`'s; 0 copies is the unit),
 * and into `*set` the copies' necessary set, as `rb_cat_into` builds a
 * concatenation's: each copy's members at their offsets (the first copy's
 * are the nearest), plus every byte CAT-SET joins where one copy's guard
 * narrows the next copy's consumed position (`(?:(?=ln)..){2}`). */
static RbRuns rr_pow(const RbWalk *w, RbRuns b, int c, const RbSet *bs,
                     RbSet *set)
{
    RbRuns o = rr_unit();
    *set = rb_empty();
    for (int i = 0; i < c; i++) {
        *set = rb_union(*bs, *set, b.maxw);
        o = rr_cat(w, b, o, set);
    }
    return o;
}

/* T2 row 2, the exact repeat `X{m}`: `X^c` with `c = rr_pow_count`, its
 * width the repeat's exact one, not `c` copies' (W-R6), and the tail placed
 * from it; `all` only when every copy was unrolled (`c < m` stored a prefix
 * of a longer literal) or the body is width 0 (its copies store nothing, so
 * `X^1` is `X^m`). `m = 0` gives the unit: `xy(?:ab){0}zw` is `xyzw`. */
static RbRuns rr_rep_exact(const RbWalk *w, RbRuns b, int m, const RbSet *bs,
                           RbSet *set)
{
    int c = rr_pow_count(&b, m);
    RbRuns o = rr_pow(w, b, c, bs, set);
    o.all = o.all && (c == m || b.maxw == 0);
    o.maxw = rr_rep_w(m, b.maxw);
    o.tail.off = rn_tail_off(o.maxw, o.tail.n);
    return o;
}

/* T2 row 3, every other repeat `X{m,n}` (`n` > `m`, or unbounded): the head
 * and the best from `X^c · X{0,n-m}`, the tail from `X{0,n-m} · X^c`, the
 * width the repeat's exact one. The optional part is a gap (no byte, no
 * run), so `all` is false and at `m = 0` this is today's gap. The best is
 * the first decomposition's: its offsets are the smaller bounds, and the
 * second's best is the same bytes further in. */
static RbRuns rr_rep_split(const RbWalk *w, RbRuns b, int m, int n,
                           const RbSet *bs, RbSet *set)
{
    RbRuns p = rr_pow(w, b, rr_pow_count(&b, m), bs, set);
    RbRuns gap = rr_none(rr_rep_w(n < 0 ? -1 : n - m, b.maxw));
    RbRuns o = rr_cat(w, p, gap, NULL), tl = rr_cat(w, gap, p, NULL);
    o.tail = tl.tail;
    o.rg = tl.rg;   /* span_arms L1 (D-3): from the decomposition ending in `X^c` */
    o.maxw = rr_rep_w(n, b.maxw);
    o.tail.off = rn_tail_off(o.maxw, o.tail.n);
    return o;
}

/* [RUN-POS-SET] stage 2p THE BYTE ALPHABET of the piece description: a
 * position is a 256-bit set (`rb_has`'s layout), 32 bytes. */
static const void *rb_pd_join(Ctx *cx, const void *a, const void *b)
{
    const unsigned char *x = a, *y = b;
    bool xs = true, ys = true;
    for (int i = 0; i < 32; i++) {
        if (y[i] & ~x[i]) xs = false;
        if (x[i] & ~y[i]) ys = false;
    }
    if (xs) return a;
    if (ys) return b;
    unsigned char *u = pcrec_arena_alloc(&cx->arena, 32);
    for (int i = 0; i < 32; i++) u[i] = x[i] | y[i];
    return u;
}

static bool rb_pd_same(const void *a, const void *b)
{
    return memcmp(a, b, 32) == 0;
}

static const PdAlpha rb_pd_bytes = { rb_pd_join, rb_pd_same };

/* The lowered class `a`'s byte set as a piece position; `b` its single
 * member or -1. A single byte's set is built once per walk. */
static const unsigned char *rb_pos_set(RbWalk *w, const Ast *a, int b)
{
    if (b >= 0 && w->single[b]) return w->single[b];
    unsigned char *s = pcrec_arena_alloc(&w->cx->arena, 32);
    if (b >= 0) {
        s[b >> 3] = (unsigned char)(1u << (b & 7));
        w->single[b] = s;
    } else {
        pcrec_cls_bits(w->cx, a, s);
    }
    return s;
}

/* THE NEVER LEAF (span_arms §14.3 D-9; review r55 C): a node that becomes
 * the EMPTY position matches no character, so the runs of the node alone are
 * never, and CAT's never row (`rr_cat`) carries that to whatever it is
 * concatenated with. The one leaf, asked where the walk turns a node into a
 * position: a lowered class (`rb_class_into`) and the `A_CTX` item
 * (`rb_ctx_item`), so the two lowerings of a one-character lookaround agree
 * (`x(?=[^\x00-\xff])y` under `byte`, with and without `-fno-ctx-node`). */
static bool rb_never_pos(const unsigned char *p)
{
    return rn_count(p) == 0;
}

/* `acc` := the lowered class `a`, followed by `acc`. */
static PCREC_OWN_FRAME void rb_class_into(RbWalk *w, RbVal *acc,
                                          const Ast *a)
{
    int b = pcrec_cls_single(w->cx, a);
    const unsigned char *ps = rb_pos_set(w, a, b);
    rb_head_node(w, acc, a, NULL);
    /* [RUN-POS-SET] stage 2p: a piece position is the class's exact byte
     * SET, with no member bound (nothing scans a piece, §3.4). */
    PdDesc desc = pcrec_pd_cat(w->cx, &w->pd, pcrec_pd_pos(w->cx, ps), acc->desc);
    if (!rn_admits(w, ps)) {
        /* A class outside the run's domain (stage 3: more than `pos_set`
         * members, no information) contributes no byte and no run, and it
         * also BREAKS contiguity for everything around it — which
         * `rr_none`'s cleared `all` is exactly what says. One byte wide: the
         * tree is lowered. */
        RbRuns g = rr_none(1);
        /* span_arms L1 (D-9) the never family's leaf: the class's row is
         * NODE, the answer the set's, read here at byte level after lowering
         * (as derive.c's `is_never_leaf` reads the class before it) */
        g.never = rb_never_pos(ps);
        acc->set = rb_union(rb_empty(), acc->set, 1);
        acc->runs = rr_cat(w, g, acc->runs, NULL);
        acc->desc = desc;
        return;
    }
    /* Only a single byte is a member of the necessary SET; a wider position is
     * one the RUN carries (litscan_s4.md §2.3.1). */
    acc->set = rb_union(b >= 0 ? rb_single(b) : rb_empty(), acc->set, 1);
    acc->runs = rr_cat(w, rr_pos(w, ps), acc->runs, &acc->set);
    acc->desc = desc;
}

/* `acc` := a zero-width node followed by `acc`, in the old form: no byte,
 * and a broken run (T3's last row, the form a restored arm runs). */
static PCREC_OWN_FRAME void rb_assert_into(const RbWalk *w, RbVal *acc)
{
    acc->runs = rr_cat(w, rr_none(0), acc->runs, NULL);
    acc->desc = pcrec_pd_none();   /* a CUT, as in the run (§3.4) */
}

/* `acc` := a node that consumes nothing, followed by `acc`: the width-0 unit
 * for the run (no byte, `all`, width 0), so the bytes on its two sides join.
 * `d` is the node's description, T3's row's: the empty string's (exact) or
 * desc.c `zero` (a width-0 group that is not exact). */
static PCREC_OWN_FRAME void rb_zero_unit_into(const RbWalk *w, RbVal *acc,
                                              PdDesc d)
{
    acc->runs = rr_cat(w, rr_unit(), acc->runs, NULL);
    acc->desc = pcrec_pd_cat(w->cx, &w->pd, d, acc->desc);
}

/* THE REPEAT'S VALUE, one builder per row of T2 below: each writes into
 * `v` what the repeat `X{m,n}` of body `b` contributes, and the walk's
 * `A_REP` arm concatenates it as it does any factor (`rb_cat_into`). The SET
 * is the body's members where every match takes a copy (`m >= 1`), none
 * where it may take none, each at the body's own offsets (the first copy
 * begins where the repeat does). */

/* T2 row 1, a repeat of the WIDTH-0 body `b`: at `m == 0` the unit, else
 * the body's value (every copy is the same zero-width stretch); either way
 * `all`, because a subtree that consumes nothing leaves the bytes on its two
 * sides adjacent in the subject, whether it matches zero times or many. */
static PCREC_OWN_FRAME void rb_rep_unit_val(RbVal *v, const RbVal *b, int m)
{
    if (m == 0) rb_init(v);
    else *v = *b;
    v->desc = pcrec_pd_unit();   /* the body is width 0 at either m */
    v->runs.all = true;
}

/* T2 row 2, the exact repeat `X{m}`: the power arm's runs, and as pieces the
 * body's `m` copies (`pcrec_pd_pow`). */
static PCREC_OWN_FRAME void rb_rep_exact_val(const RbWalk *w, RbVal *v,
                                             const RbVal *b, int m)
{
    v->runs = rr_rep_exact(w, b->runs, m, &b->set, &v->set);
    v->desc = pcrec_pd_pow(w->cx, &w->pd, b->desc, m);
}

/* T2 row 3, the repeat `X{m,n}`: the power arm's runs; not fixed-width, so
 * no pieces. */
static PCREC_OWN_FRAME void rb_rep_split_val(const RbWalk *w, RbVal *v,
                                             const RbVal *b, int m, int n)
{
    v->runs = rr_rep_split(w, b->runs, m, n, &b->set, &v->set);
    v->desc = pcrec_pd_none();
}

/* The replaced form at `m >= 1` (a restored arm): the body's BEST run
 * alone, nothing joined across an iteration boundary (reqpos_2b.md §2.4
 * item 4); [K82] at its own offset, the FIRST iteration beginning where
 * the repeat does. */
static PCREC_OWN_FRAME void rb_rep_best_val(RbVal *v, const RbVal *b, int n)
{
    v->set  = b->set;
    v->runs = rr_none(rr_rep_w(n, b->runs.maxw));
    v->runs.best = b->runs.best;
    /* span_arms L1 (READYL1-8 (a)): REP at `m >= 1` is never where its body
     * is, under this restored form too; it carries no guard */
    v->runs.never = b->runs.never;
    v->desc = pcrec_pd_none();
}

/* The replaced form at `m == 0` (a restored arm): a gap. THE REPEAT STILL
 * BREAKS CONTIGUITY, unless its body is width 0 (row 1), which is a
 * different obligation from the empty SET and is the one arm of this walk
 * where getting it wrong DELETES A MATCH rather than missing an
 * opportunity. A C-comment pattern — an open delimiter, a min-0 repeat of
 * the body, a close delimiter — would otherwise report a FOUR-BYTE run of
 * the two delimiters abutting: true of the match where the repeat takes
 * zero iterations, false of every match where it takes one, and a run must
 * hold on EVERY match. So it is `rr_none`, exactly as a multi-member class
 * is. [K82] It still has its WIDTH: it contributes no byte and no run, but
 * it moves every run (and [REQ-HANDOFF-L1] every set member) to its right. */
static PCREC_OWN_FRAME void rb_rep_gap_val(RbVal *v, const RbVal *b, int n)
{
    v->set  = rb_empty();
    v->runs = rr_none(rr_rep_w(n, b->runs.maxw));
    v->desc = pcrec_pd_none();
}

/* T2, THE REPEAT ROWS (docs/design/span_arms.md §6), first match: what a
 * repeat `X{m,n}` contributes, from its body's value `b`. Rows 1-3 are the
 * design's; the two after them are the forms they replaced (the best-only
 * copy and the min-0 gap), reached only when the walk parameters restore an
 * arm. A row whose `arm` is restored is passed over, so the next row answers
 * in the old form; the default (after the table) matches every repeat: a gap. */
typedef enum {
    RB_REP_UNIT, RB_REP_EXACT, RB_REP_SPLIT, RB_REP_BEST, RB_REP_GAP
} RbRepRow;

/* The body consumes nothing on any path: its widest match is 0 bytes. */
static bool rb_rep_width0(const Ast *a, const RbVal *b)
{
    (void)a;
    return b->runs.maxw == 0;
}

/* Every match takes the same number of copies: `X{m}`. */
static bool rb_rep_exact(const Ast *a, const RbVal *b)
{
    (void)b;
    return a->u.rep.rmin == a->u.rep.rmax;
}

/* Every match takes at least one copy of the body. */
static bool rb_rep_min1(const Ast *a, const RbVal *b)
{
    (void)b;
    return a->u.rep.rmin >= 1;
}

/* Every repeat. */
static bool rb_rep_any(const Ast *a, const RbVal *b)
{
    (void)a;
    (void)b;
    return true;
}

static const struct {
    bool (*when)(const Ast *a, const RbVal *b);
    RbRepRow row;
    unsigned arm;   /* the restored arm (walk_arms.def) that passes it over */
} rb_rep_rows[] = {
    /* 1 (span_arms E1, [REQ-EMPTYCAT]): `abcd(?:)*efgh`, `ab(?:^)+cd` */
    { rb_rep_width0, RB_REP_UNIT,  PCREC_WALK_ARM(EMPTY) },
    /* 2-3 (span_arms R1, [REPEAT-RUN]): `xy(?:ab){2}zw`, `xy(?:ab){1,3}zw` */
    { rb_rep_exact,  RB_REP_EXACT, PCREC_WALK_ARM(REP) },
    { rb_rep_any,    RB_REP_SPLIT, PCREC_WALK_ARM(REP) },
    /* the replaced forms, under a restored arm */
    { rb_rep_min1,   RB_REP_BEST,  0 },
};

/* The first row of T2 that matches the repeat `a` with body value `b` and
 * that the walk does not restore; none, the default: a gap. */
static RbRepRow rb_rep_row(const RbWalk *w, const Ast *a, const RbVal *b)
{
    size_t i;
    RB_ROW_SCAN(i, w, rb_rep_rows, rb_rep_rows[i].when(a, b));
    return i < RB_ROWS(rb_rep_rows) ? rb_rep_rows[i].row : RB_REP_GAP;
}

/* `v` := the value of the repeat `a` with body value `b`, by its T2 row. */
static void rb_rep_val(const RbWalk *w, const Ast *a, const RbVal *b, RbVal *v)
{
    int m = a->u.rep.rmin, n = a->u.rep.rmax;
    switch (rb_rep_row(w, a, b)) {
    case RB_REP_UNIT:  rb_rep_unit_val(v, b, m);     return;
    case RB_REP_EXACT: rb_rep_exact_val(w, v, b, m); return;
    case RB_REP_SPLIT: rb_rep_split_val(w, v, b, m, n); return;
    case RB_REP_BEST:  rb_rep_best_val(v, b, n);     return;
    case RB_REP_GAP:   rb_rep_gap_val(v, b, n);      return;
    }
}

static void rb_walk_at(RbWalk *w, const Ast *a, RbVal *acc, RbVal *t);

/* Writes into `*out` the bytes and the runs EVERY match of `a` must contain,
 * one recursion level deeper than its caller (see `RbWalk.slot`). */
static void rb_walk(RbWalk *w, const Ast *a, RbVal *out)
{
    RbVal *t = rb_slots(w);
    w->depth++;
    rb_walk_at(w, a, out, t);
    w->depth--;
}

/* T3, THE ZERO-WIDTH ROWS (docs/design/span_arms.md §6, §4.1), first match:
 * what a node whose kind row's TEXT is ZERO contributes. A node that
 * consumes nothing leaves the bytes on its two sides ADJACENT in the
 * subject, whether it is the empty string, an assertion, `\K` or a
 * lookaround, so it is CAT's unit (E-1, E-4, E-5); joining ACROSS it puts
 * no byte of a lookaround's body in the run, which is what the header
 * forbids. E-5i (span_arms L1: a positive lookaround, `A_LOOK` or `A_CTX`
 * NEXT/PREV) is that unit CARRYING its item's guards, its body's guards and
 * its body's never bit (§5.1, §14.3 D-1); E-5 is E2's plain unit, which
 * answers when E-5i is restored (`look`). E-1 restores under the `empty`
 * arm (span arms E2 took it from alt_normal_form stage 2a), E-4, E-5 and
 * E-5i under `zero` (E-5i's mask is `look | zero`, so `zero` keeps E2's
 * meaning). A row whose `arm` the walk parameters restore is passed over;
 * the default (after the table, the old cut) matches every node. */
typedef enum {
    RB_ZERO_EMPTY,   /* the unit, described as the empty string (exact) */
    RB_ZERO_ITEM,    /* the unit carrying the lookaround's item (E-5i) */
    RB_ZERO_UNIT,    /* the unit, described by desc.c `zero` (not exact) */
    RB_ZERO_CUT      /* the old form: a cut */
} RbZeroRow;

/* `A_EMPTY`: the empty string (E-1). */
static bool rb_zero_empty(const Ast *a)
{
    return a->k == A_EMPTY;
}

/* A POSITIVE one-sided lookaround, in either lowering (E-5): `A_LOOK` not
 * negated, or `A_CTX` whose function is ctxfn.def's NEXT or PREV row. */
static bool rb_zero_look_pos(const Ast *a)
{
    if (a->k == A_LOOK) return !a->u.look.neg;
    return a->k == A_CTX && (a->u.ctx.fn == CTXFN_NEXT || a->u.ctx.fn == CTXFN_PREV);
}

/* Every zero-width node. */
static bool rb_zero_any(const Ast *a)
{
    (void)a;
    return true;
}

static const struct {
    bool (*when)(const Ast *a);
    RbZeroRow row;
    unsigned arm;   /* the restored arm (walk_arms.def) that passes it over */
} rb_zero_rows[] = {
    /* E-1 (span_arms E2, from alt_normal_form stage 2a): `abcd()efgh` */
    { rb_zero_empty,    RB_ZERO_EMPTY, PCREC_WALK_ARM(EMPTY) },
    { rb_zero_empty,    RB_ZERO_CUT,  0 },   /* E-1 restored */
    /* E-5i (span_arms L1): `xy(?=bc)[bc]c`, `foo(?=bar)baz` */
    { rb_zero_look_pos, RB_ZERO_ITEM, PCREC_WALK_ARM(LOOK) | PCREC_WALK_ARM(ZERO) },
    /* E-5 (span_arms E2), the plain unit `look` restores: `xyz(?<=yz)abc` */
    { rb_zero_look_pos, RB_ZERO_UNIT, PCREC_WALK_ARM(ZERO) },
    /* E-4 (span_arms E2): `foo\bbar`, `x(?!ab)ac`, `ab\Kcd` */
    { rb_zero_any,      RB_ZERO_UNIT, PCREC_WALK_ARM(ZERO) },
};

/* ---- THE ITEM (span_arms L1, §5.1, §14.3 D-1, D-10) ----------------------- */

/* The guard a head `h` states: its positions from the cursor outward, up to
 * the first one outside the run's domain (§5.1), in the head's order. */
static RbRun rb_guard_of_head(const RbWalk *w, const PdHead *h)
{
    RbRun g = rn_none();
    for (int i = 0; i < h->h && i < PCREC_MAX_REQ_RUN_SCAN && rn_admits(w, h->pos[i]); i++)
        rn_put(w, &g, h->pos[i]);
    return g;
}

/* The item of the positive lookaround `a` into the unit `u`, from its body's
 * value `b`, which this walks (`rb_walk(w, a->l, b)`). A LOOKAHEAD's guard is
 * its body's HEAD (the positions every match of the body consumes FIRST, the
 * ones nearest the cursor), followed by the body's own `rg` where the body is
 * `all` and the guard covers it whole (exact width, so its end is known); its
 * `lg` is the body's own (a lookbehind nested in the body, at its own
 * offsets). A LOOKBEHIND's is the mirror, read from the body's DESCRIPTION
 * (its LAST positions, every width group's, united: `pcrec_pd_tail_head`),
 * preceded by the body's own `lg` where it is `all` and covered whole; its
 * `rg` is the body's own. Nothing else leaves the body: its set, its
 * description and its consumed runs stay in `b` (D-1). Its never bit is the
 * body's, by the kind row's NEVER column (BODY for a positive lookaround). */
static PCREC_OWN_FRAME void rb_look_item(RbWalk *w, const Ast *a, RbVal *b,
                                         RbRuns *u)
{
    bool behind = a->u.look.behind;
    const RbRuns *br = &b->runs;
    u->never = pcrec_never_by_row(w->cx, pcrec_ast_row(a).never, br->never, br->never);
    if (!behind) {
        RbRun g = rb_guard_of_head(w, &b->head);
        if (br->all && g.n == br->maxw && g.n == b->head.h && b->head.closed)
            g = rn_app(g, br->rg);
        u->rg = g;
        u->lg = br->lg;
    } else {
        PdHead h = pcrec_pd_tail_head(w->cx, &w->pd, b->desc);
        RbRun r = rb_guard_of_head(w, &h), g = rn_none();
        for (int i = r.n - 1; i >= 0; i--) g.pos[g.n++] = r.pos[i];
        if (br->all && g.n == br->maxw && g.n == h.h && h.closed)
            g = rn_pre(br->lg, g);
        u->lg = g;
        u->rg = br->rg;
    }
}

/* The item of a positive one-character `A_CTX` (`(?=C)` NEXT, `(?<=C)`
 * PREV) into `u`: its set at offset 0 (NEXT, an `rg`) or −1 (PREV, an `lg`),
 * where the set reads exactly as bytes (every member within the encoding's
 * one-byte repertoire, `ReqWalkParams.onebyte_max`) and the run's domain
 * admits it; else no item. An EMPTY set (no character at all: the parser
 * complements within the encoding's repertoire) is the never leaf
 * (`rb_never_pos`). It walks no body. */
static void rb_ctx_item(const RbWalk *w, const Ast *a, RbRuns *u)
{
    unsigned char *s = pcrec_arena_alloc(&w->cx->arena, 32);
    for (int i = 0; i < a->u.ctx.n; i++) {
        if (a->u.ctx.iv[i].hi > w->onebyte_max) return;
        for (unsigned c = a->u.ctx.iv[i].lo; c <= a->u.ctx.iv[i].hi; c++)
            s[c >> 3] |= (unsigned char)(1u << (c & 7));
    }
    u->never = rb_never_pos(s);
    if (!rn_admits(w, s)) return;
    if (a->u.ctx.fn == CTXFN_NEXT) u->rg = rn_pos(w, s);
    else u->lg = rn_pos(w, s);
}

/* E-5i: `acc` := the positive lookaround `a` followed by `acc`, as the unit
 * (E2's: no byte, `all`, width 0, desc.c `zero`) carrying the item `u`,
 * whose guards meet `acc`'s positions in `rr_cat`. `t` is the walk level's
 * child slots; the body's value goes to `t[0]` and stays there. */
static PCREC_OWN_FRAME void rb_zero_item_fin(RbWalk *w, RbVal *acc,
                                             const Ast *a, RbVal *t)
{
    RbRuns u = rr_unit();
    if (a->k == A_LOOK) rb_look_item(w, a, &t[0], &u);
    else rb_ctx_item(w, a, &u);
    acc->runs = rr_cat(w, u, acc->runs, &acc->set);
    acc->desc = pcrec_pd_cat(w->cx, &w->pd, pcrec_pd_zero(), acc->desc);
}

/* THE DESCENT AND THE ITEM IN SEPARATE FRAMES ([DD-10], l1ttri): the body's
 * walk is the one recursive step of a nested lookaround, so the frame that
 * makes it holds only pointers; the item's runs (`RbRuns`, several KB with
 * `rr_cat`'s temporaries) live in `rb_zero_item_fin`, entered after the
 * descent returns. In one frame, a lookaround nested 250 deep cost 6.8 KB a
 * level and overflowed limits.md §3.10's compile-thread budget. */
static void rb_zero_item_into(RbWalk *w, RbVal *acc, const Ast *a, RbVal *t)
{
    if (a->k == A_LOOK) {
        bool behind = a->u.look.behind;
        if (!behind) w->ahead++;
        rb_walk(w, a->l, &t[0]);
        if (!behind) w->ahead--;
    }
    rb_zero_item_fin(w, acc, a, t);
}

/* `acc` := the zero-width node `a` followed by `acc`, by the first row of T3
 * that matches it and that the walk does not restore; none, the default (E-4
 * and E-5 restored): a cut. `t` the level's child slots (E-5i walks a body). */
static void rb_zero_into(RbWalk *w, RbVal *acc, const Ast *a, RbVal *t)
{
    size_t i;
    RbZeroRow row = RB_ZERO_CUT;
    RB_ROW_SCAN(i, w, rb_zero_rows, rb_zero_rows[i].when(a));
    if (i < RB_ROWS(rb_zero_rows)) row = rb_zero_rows[i].row;
    switch (row) {
    case RB_ZERO_EMPTY: rb_zero_unit_into(w, acc, pcrec_pd_unit()); return;
    case RB_ZERO_ITEM:  rb_zero_item_into(w, acc, a, t);           return;
    case RB_ZERO_UNIT:  rb_zero_unit_into(w, acc, pcrec_pd_zero()); return;
    case RB_ZERO_CUT:   rb_assert_into(w, acc);                     return;
    }
}

/* `acc` := node `a` followed by `acc`, for a kind whose ROW answers for its
 * text: ZERO consumes nothing (T3's rows), ANY is a gap of unbounded width
 * (no byte, a broken run, every run to its right moved). An OWN kind has its
 * own arm; it would get the gap, which is always sound. The head reads a
 * lookaround THROUGH whatever its body (`pcrec_ph_node`'s A_LOOK row reads
 * only the body's WRITES, which no reader here asks), so its body is the
 * unit's head. */
static void rb_row_into(RbWalk *w, RbVal *acc, const Ast *a, RbVal *t)
{
    PdHead unit = pcrec_ph_unit();
    rb_head_node(w, acc, a, a->k == A_LOOK ? &unit : NULL);
    switch (pcrec_ast_row(a).text) {
    case KTEXT_ZERO: rb_zero_into(w, acc, a, t); return;
    case KTEXT_ANY:  rb_gap_into(w, acc, PCREC_W_UNBOUNDED); return;
    case KTEXT_OWN:  break;
    }
    rb_gap_into(w, acc, PCREC_W_UNBOUNDED);
}

/* The bytes and the runs EVERY match of `a` must contain, into `*acc`; `t` is
 * this level's two child slots.
 *
 * The `A_CAT` spine is walked ITERATIVELY down `->l` and the `A_ALT` spine
 * iteratively down its own, for `src/opt/mrl.c`'s and `pcrec_ast_visit`'s
 * shared reason: both spines are as long as the PATTERN, not as deep as its
 * nesting, and this project has segfaulted its own compiler on a 20,000-byte
 * literal for want of exactly that. What remains recursive descends one paren
 * level per frame, and holds only pointers across the descent: every value
 * lives in `*acc` or a slot ([DD-10] measured 12.9 KB per frame, 21 KB per
 * nesting level, before it did).
 *
 * `acc` carries what has been learned to the RIGHT of the current node, which
 * is what keeps the rightmost pick correct across an arbitrarily long spine
 * without a second pass — and, for the runs, what makes each step an ordinary
 * concatenation with the accumulated right-hand side. */
static void rb_walk_at(RbWalk *w, const Ast *a, RbVal *acc, RbVal *t)
{
    rb_init(acc);

    for (;;) {
        switch (a->k) {
        case A_CAT:
            rb_walk(w, a->r, &t[0]);
            rb_cat_into(w, acc, &t[0]);
            a = a->l;
            continue;
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
            /* `t[0]` the branches so far, `t[1]` the next one. */
            bool first = true;
            PCREC_SPINE_EACH(b, a, A_ALT) {
                rb_walk(w, b, &t[first ? 0 : 1]);
                if (!first) rb_alt_into(w, &t[0], &t[1]);
                first = false;
            }
            rb_cat_into(w, acc, &t[0]);
            return;
        }
        case A_REP:
            /* T2's rows (`rb_rep_rows`), first match on the body's value,
             * each building the repeat's value into `t[1]`, which then
             * concatenates like any factor. A WIDTH-0 body is the unit
             * (row 1): it consumes nothing, so the bytes on either side
             * abut however many copies match. Any other body is read as
             * its copies (rows 2-3, the power arm): the copies every match
             * takes join their neighbours and each other through CAT, and
             * an optional part is a gap. Under a restored arm the old forms
             * answer (the best-only copy, the gap).
             *
             * `rmin == 0` admits the empty iteration, on which the body
             * contributes no byte at all — the one arm where forgetting the
             * minimum is a deleted match rather than a missed opportunity. */
            rb_walk(w, a->l, &t[0]);
            rb_rep_val(w, a, &t[0], &t[1]);
            t[1].head = pcrec_ph_unit();
            rb_head_node(w, &t[1], a, &t[0].head);
            rb_cat_into(w, acc, &t[1]);
            return;
        case A_CLASS:
            rb_class_into(w, acc, a);
            return;
        /* These nodes BARE; a QUANTIFIED one is T2 row 1's (a repeat of a
         * width-0 body joins, `(?:\b)+` included, by the E1 ruling). The
         * ruled arm for the bare cuts is `zero` (E2); it restores only these.
         *
         * Consumes nothing, so it makes no byte necessary BY ITSELF: a
         * positive lookaround's body bytes never join the run or the set as
         * consumed bytes, and the header says why that is a CORRECTNESS rule.
         *
         * FOR THE RUN EACH IS T3's ROW (`rb_zero_rows`): the bytes on either
         * side of a node that consumes nothing ARE adjacent in the subject,
         * so the run joins ACROSS it (the unit); a POSITIVE lookaround is
         * E-5i's ITEM (span_arms L1), whose body is walked and whose guards
         * narrow the consumed positions beside it (`rb_zero_item_into`). */
        case A_EMPTY:
        case A_EOL:
        case A_CTX:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
        /* The two deliberate declines, `src/facts/startanch.c`'s for the same
         * reasons: a backreference's bytes are the subject's business and a
         * linked call's body is `callgraph.c`'s cycle problem. Both are the
         * empty set, which disables the check — always sound. */
        case A_BREF:
        case A_VAR:
        case A_CALLOUT:
            /* [INLINE-C] 1a: the kind ROW answers (`rb_row_into`): text ZERO
             * for every kind above the backreference and a check callout,
             * ANY for the two and a consuming callout. */
            rb_row_into(w, acc, a, t);
            return;
        /* The call's text is its callee's (row OWN), declined for the reason
         * above rather than computed. */
        case A_CALL:
            rb_head_node(w, acc, a, NULL);
            rb_gap_into(w, acc, PCREC_W_UNBOUNDED);
            return;
        }
    }
}

/* ---- TOP, the walk's exit (span_arms L1, §14.3 D-3, D-4) ------------------ */

/* TOP's candidate rows, a COMBINING table walked in full (`RB_ROW_EACH`): each
 * row whose `when` holds on the root's runs and whose arm is not restored
 * offers a candidate run built from the root's consumed runs and its guards,
 * with its CONSUMED EXTENT `[lo, hi)` (the positions every match consumes),
 * and the run is the best of the consumed `best` and every candidate by the
 * one run choice (`rn_cmp`), its extent kept beside it. The default, outside
 * the table, is the consumed `best`, extent `[0, n)`. Every guard no row
 * reads is dropped. L3 adds BACK (`lg ++ head`); L2 adds AHEAD (`tail ++
 * rg`) and BACK's `++ rg` clause, each under the `look` arm. */
typedef struct {
    bool (*when)(const RbWalk *w, const RbRuns *root);
    RbRun (*cand)(const RbWalk *w, const RbRuns *root, int *lo, int *hi);
    /* may the candidate, its consumed extent `[lo, hi)`, displace the
     * consumed `best` at all (before the run choice compares them)? `set` is
     * the root's necessary set, whose members are the byte landmarks where
     * no run is stated */
    bool (*displaces)(const RbWalk *w, const RbRun *best, const RbSet *set,
                      int lo, int hi);
    unsigned arm;   /* the restored arm (walk_arms.def) that passes it over */
} RbTopRow;

/* BACK's `when`: a left guard stands at the root and begins no further back
 * than the declared lookbehind length allows (`lb_bytes`, D-11). */
static bool rb_top_back_when(const RbWalk *w, const RbRuns *root)
{
    return root->lg.n > 0 && root->lg.n <= w->lb_bytes;
}

/* BACK's candidate (span_arms §14.3 D-4, L3): the left guard joined to the
 * root's head, `lg ++ head`, which begins `lg.n` bytes BEFORE the attempt
 * start (its K, `off`, is `-lg.n`). `lg` keeps the positions nearest the
 * attempt start and `head` sits at 0 in every match, so the two are
 * adjacent. The consumed extent is the head's part, `[lg.n, n)` after the
 * join keeps the first `PCREC_MAX_REQ_RUN_SCAN` positions: EMPTY where the
 * head is empty (`(?<=foo)`) or `lg` fills the stored bound (`(?<=a{32})b`),
 * a run with no consumed position (D-6). L2's `++ rg` clause is not here. */
static RbRun rb_top_back(const RbWalk *w, const RbRuns *root, int *lo, int *hi)
{
    (void)w;
    RbRun r = rn_app(root->lg, root->head);
    r.off = -(long long)root->lg.n;
    *lo = root->lg.n;
    *hi = r.n;
    return r;
}

/* Does the set state a BYTE LANDMARK at a static bound: some member every
 * match holds at most a bounded distance in (`RbSet.off`)? Where no run is
 * stated, the pre-check's needle is a set member (facts_listing §4.1.2¶8b),
 * and a forward scan's re-entry keeps it exactly where its K is bounded. A
 * superset of "the picked member is bounded": the pick is a derived choice
 * this core walk does not read, and the wider answer only keeps BASE more
 * often (review r66 EMIT-3). */
static bool rb_set_bounded_landmark(const RbSet *s)
{
    for (int b = 0; b < 256; b++)
        if (rb_has(s, b) && s->off[b] < RB_OFF_UNBOUNDED) return true;
    return false;
}

/* BACK's displacement condition (span_arms §14.4 L3, REV 3.3 addendum, review
 * r65 A, review r66 EMIT-3): a forward scan declines its re-entry at K < 0
 * (`req_k_reentry_sound`, src/gen/emit_dfa.c), so on a compile that may
 * re-enter a forward scan (`fwd_reentry`) a BACK run that displaced the
 * LANDMARK the re-entry keeps traded that re-entry for a start-byte scan, up
 * to x10 slower than what it displaced. The landmark is the consumed `best`
 * where one is stated, else a necessary byte. There BACK displaces only
 * (1) an EMPTY consumed `best` whose set states no byte landmark at a static
 * bound (`(?<=foo)`; not `(?<=qz)(?:a.|.a)`, whose `a` sits at K 1), or
 * (2) a `best` that begins at no static bound, by a candidate that keeps a
 * consumed position. Where no forward re-entry exists the run choice decides. */
static bool rb_top_back_displaces(const RbWalk *w, const RbRun *best, const RbSet *set,
                                  int lo, int hi)
{
    return !w->fwd_reentry
        || (best->n == 0 && !rb_set_bounded_landmark(set))
        || (lo < hi && best->off >= PCREC_W_UNBOUNDED);
}

static const RbTopRow rb_top_rows[] = {
    { rb_top_back_when, rb_top_back, rb_top_back_displaces, PCREC_WALK_ARM(LOOK) },
};

/* The run TOP chooses from the root's runs `root` and necessary set `set`,
 * its consumed extent into `[*lo, *hi)`. */
static RbRun rb_top(const RbWalk *w, const RbRuns *root, const RbSet *set,
                    int *lo, int *hi)
{
    size_t i;
    RbRun best = root->best;
    *lo = 0;
    *hi = best.n;
    int clo, chi;   /* a candidate's extent (outside the body: a macro argument) */
    RbRun cand;
    RB_ROW_EACH(i, w, rb_top_rows, rb_top_rows[i].when(w, root), {
        cand = rb_top_rows[i].cand(w, root, &clo, &chi);
        if (rb_top_rows[i].displaces(w, &root->best, set, clo, chi) && rn_cmp(w, &best, &cand) < 0) {
            best = cand; *lo = clo; *hi = chi;
        }
    });
    return best;
}

/* THE WALK'S FACTS, from ONE walk: the whole necessary SET (with its threaded
 * rightmost member, `RbSet.pick`) and the most informative guaranteed
 * contiguous RUN (`RbRun`, at most `PCREC_MAX_REQ_RUN_SCAN` positions
 * stored), its positions byte sets inside the walk's domain.
 * Both are the EMPTY answer where nothing is necessary, which disables every
 * check built on them and is always sound. Reads no option and asks for no
 * prior: the parameters `p` are its caller's reading of the fact-level deny,
 * the harness lever (span_arms §3.7) and the byte-rate the run choice's tie
 * rows read. */
void pcrec_req_walk(Ctx *cx, const Ast *root, const ReqWalkParams *p,
                    RbSet *set, RbRun *run, int *cons_lo, int *cons_hi,
                    PdDesc *pieces, bool *never)
{
    RbWalk *w = pcrec_arena_alloc(&cx->arena, sizeof *w);
    w->cx = cx;
    w->pos_set = p->pos_set;
    w->restored = p->restored;
    w->rate = p->rate;
    w->pd = (PdCfg){ &rb_pd_bytes, p->max_pieces, PCREC_MAX_REQ_RUN_SCAN };
    w->onebyte_max = p->onebyte_max;
    w->ahead = 0;
    w->lb_bytes = p->lb_bytes;
    w->fwd_reentry = p->fwd_reentry;
    RbVal *v = pcrec_arena_alloc(&cx->arena, sizeof *v);
    rb_walk(w, root, v);
    *set = v->set;
    *run = rb_top(w, &v->runs, &v->set, cons_lo, cons_hi);
    *pieces = v->desc;
    *never = v->runs.never;
}

/* The rate rule a derived pick answered by, for `--emit-facts`' `why`
 * column: the byte-rate the compile consumed, or its NONE answer. Asked of
 * the accessor's own answer (`pcrec_find_byte_rate_answers`), never of the
 * record's memo and never off the rate pointer, so no reader here tests a
 * rate (findings design §6.3's structural rule) and none reads the memo
 * (window_contract.md §3.7.1). Its callers ask first, so the answer is
 * theirs: the window, the pick and the whole run's choice (`facts.c`). */
PfWhyCode pcrec_req_rate_why(Ctx *cx)
{
    return pcrec_find_byte_rate_answers(cx) ? PF_WHY_RATE_BUILTIN : PF_WHY_RATE_NONE;
}

/* `pcrec_run_scan_index` (facts.h): pcrec's own pick
 * (`pcrec_find_run_scan_index`, src/core/findings.c) over the stretch
 * `run->pos[lo..hi)`, as a run index; -1 for an empty stretch, which has no
 * pick (the primitive is never asked over zero positions). */
int pcrec_run_scan_index(const uint32_t *rate, const ReqRun *run, int lo, int hi)
{
    if (lo >= hi) return -1;
    return lo + pcrec_find_run_scan_index(rate, run->pos + lo, hi - lo);
}

/* THE NECESSARY BYTE — the `req_byte` fact — at ONE return: pcrec's own
 * pick over the run's CONSUMED positions (`pcrec_run_scan_index` over
 * `pcrec_run_cons`, asked here: the retired `req_run` row's `idx`, review
 * 2026-11-11 r1 k382 F5) where a run of two or more positions is stored,
 * its consumed extent is not empty and that position is one EXACT byte, and
 * otherwise the set's pick
 * (`src/core/findings.c`). -1 exactly when the set is empty. It STAYS
 * pcrec's pick at R-38 K38-2 (span_runs_sheet.md §4.1): the pre-check's own
 * scan position is the kit's reply, and may differ from it.
 *
 * span_arms L3 (§14.3 D-6): a run that begins inside a lookbehind holds
 * bytes no match consumes, so the pick reads only the consumed extent and
 * `req_byte` stays "a byte every match consumes" (D191.2). An EMPTY extent
 * (`(?<=foo)`) has no run pick (`pcrec_run_scan_index` answers -1 and never
 * asks the primitive over zero positions) and falls to the set's pick, as a
 * pattern with no run does.
 *
 * [OPT-LITSCAN] S4 C3 A WIDER POSITION IS NOT A BYTE ANY MATCH MUST
 * CONTAIN: a match may carry any of its members there, so it falls to the
 * set's pick (litscan_s4.md §2.3.3
 * case (ii)) and every value here stays a member of `req_set`. The byte-rate
 * is asked FIRST, before any branch, so whether the compile consumed it does
 * not depend on the pattern (findings design §6.4 rule 1). */
int pcrec_req_pick(Ctx *cx, const ReqSet *set, const ReqRun *run,
                   PfWhyCode *why)
{
    const uint32_t *rate = pcrec_find_byte_rate(cx);
    *why = pcrec_req_rate_why(cx);
    if (run->whole_len >= 2) {
        int lo, hi, i;
        pcrec_run_cons(run, &lo, &hi);
        i = pcrec_run_scan_index(rate, run, lo, hi);    /* -1: an empty extent */
        int x = i < 0 ? -1 : pcrec_run_byte(run, i);
        if (x >= 0) return x;
    }
    if (set->rightmost < 0) *why = PF_WHY_NONE;
    return pcrec_find_set_pick(rate, set->bits, set->rightmost);
}
