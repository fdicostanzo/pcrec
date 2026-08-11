/* Extent scans — the ALWAYS-LIVE half of recognition (design §12: recognisers
 * and extent scans never gate), in their own translation unit ON PURPOSE.
 *
 * THE ISOLATION CONTRACT (MOD-0.1 slice 9; spec check01's nm rule): an extent
 * scan decides WHERE a construct ends and WHETHER its shape is present, and
 * that answer must be the same whatever the enabled feature set says — a
 * disabled module's construct is still ITS construct, refused by name, never
 * re-lexed as something else. The mechanical form of that promise is that
 * this object file never links the enabled-set symbol: `nm` shows
 * `pcrec_feature_enabled` in ext.o's undefined list (the gate lives at the
 * seam) and in nobody's here. The scan functions carry `extent_scan` in
 * their names because the check DISCOVERS its population by that convention
 * rather than trusting a hand list.
 *
 * The scans are byte-moves from ext.c (MOD-0.1 slice 9), not rewrites; their
 * load-bearing comments moved with them. Signatures are pure (pat, patlen)
 * on purpose: an extent scan needs no Ctx and must not grow one. */

#include "core/internal.h"

/* The K4 three-rule delimiter-pair scan, shared by the doorway and the
 * pair-opens predicate below because two copies of this scan is exactly the
 * duplication SR-2 removed. Returns true with *close_at set when the pair
 * really closes; false when it cannot (an unescaped `]` ends the class, a
 * nested `[<delim>` opener wins — behaviourally identical outcomes, measured
 * byte-identical over 1,239,480 patterns and a 172,246-pattern
 * verdict+message+offset dump, R9/C2 — or the pattern just ends).
 *
 * PCRE2's rule has THREE parts and they must land TOGETHER, which is not a
 * style preference — adding the `]` rule without the escape rule flips
 * `[a[.b\].]` from a correct rejection into an over-acceptance, because the
 * `]` that ends the scan is one the backslash was hiding:
 *
 *   1. an unescaped `]` ends the class, so the pair can no longer close
 *   2. a `[` followed by the SAME delimiter is a NESTED opener and WINS —
 *      PCRE2 abandons the outer one and recognises the inner (recognising
 *      the inner happens later, when p_class reaches that `[` and enters
 *      doorway 4b again)
 *   3. `\]` and `\\` are skipped as a UNIT. A backslash escapes a `]` or
 *      another backslash and NOTHING ELSE. Generalised twice — "skip any
 *      `\X`", then "suppress only a class-ending `]`" — and PC-3's generated
 *      sweep refuted both within minutes. Four measured patterns pin it, and
 *      no weaker rule gets all four:
 *
 *        [[.\.]]      REJECT  `\.` is NOT a unit, so `.]` closes the pair
 *        [[.a\\]x.]   accept  `\\` IS a unit, so the `]` is unescaped and
 *                             ends the class before `.]` is reached
 *        [a[.b\].]    REJECT  `\]` IS a unit, so that `]` does not end
 *                             the class and `.]` closes the pair
 *        [[.b].]      accept  a bare `]` ends the class
 *
 * THE ORDER OF THE CLOSE CHECK AGAINST RULE 1 IS ARBITRARY: the predicates
 * are disjoint whenever the delimiter is not `]`, and registry_check.c
 * forbids a `]` selector. A critic moved the close block after rule 1 and
 * got byte-identical results over the same 1,239,480 patterns (R9/C2-1).
 * Keep the order — it reads well — but do not believe it is load-bearing.
 *
 * The `i < patlen` bound is not load-bearing either: every body inside reads
 * `pat[i + 1]` only after its own `i + 1 < patlen` test (R9/C2). */
bool pcrec_class_delim_extent_scan(const char *pat, size_t patlen, int c2,
                                   size_t from, size_t *close_at)
{
    for (size_t i = from; i < patlen; i++) {
        char ch = pat[i];
        if (ch == '\\' && i + 1 < patlen &&
            (pat[i + 1] == ']' || pat[i + 1] == '\\')) {
            i++;                                            /* rule 3 */
            continue;
        }
        if (ch == (char)c2 && i + 1 < patlen && pat[i + 1] == ']') {
            *close_at = i;                                  /* the closer */
            return true;
        }
        if (ch == '[' && i + 1 < patlen && pat[i + 1] == (char)c2)
            return false;                                   /* rule 2 */
        if (ch == ']') return false;                        /* rule 1 */
    }
    return false;
}

/* Does a delimiter-pair construct actually OPEN at `from`, with `c2` as its
 * delimiter? K4's scan as a PREDICATE, so that a caller which is not the
 * doorway can ask the question without triggering a diagnostic.
 *
 * It exists for range endpoints (R9/SPEC-FA). PCRE2 refuses a range whose
 * endpoint is one of these constructs — `[0-[:digit:]]` is error 150,
 * "invalid range in character class" — and pcrec was reading the `[` as an
 * ordinary literal member and EMITTING A MATCHER. Measured against libpcre2
 * 10.46, and the boundary is exactly this scan rather than "the byte is `[`":
 *
 *   [0-[a]         compiles   `[a` opens nothing
 *   [0-[:]         compiles   `[:` with no `:]` after it opens nothing
 *   [0-[:digit]    compiles   same — the pair never closes
 *   [0-[:digit:]]  err 150    the pair closes, so a construct is the endpoint
 *   [0-[.a.]       err 150    ...even when the CLASS itself never closes
 *   [0-[:foo:]]    err 150    position beats name validity; not "unknown name"
 *
 * The registry lookup asks the tail-less question explicitly (NULL/0): no
 * class-bracket row carries a tail, and a future tailed row must not change
 * this scan's meaning by accident. R14 struck this predicate from D33's
 * deletion list — it survives as the endpoint rule's (bracket, high)
 * deviating cell. */
bool pcrec_ext_class_pair_opens(Ctx *cx, int c2, size_t from)
{
    const RegRow *r = pcrec_registry_find(RK_CLASSBRACKET, c2, NULL, 0);
    if (!r || !(r->flags & RF_CLASS_DELIM)) return false;
    size_t close_at;
    return pcrec_class_delim_extent_scan(cx->pat, cx->patlen, c2, from,
                                         &close_at);
}

/* A verb NAME's extent: it runs to the first of `)`, `:`, `=` or the end of
 * the pattern, and nothing else terminates it — `(*NO_JIT )` is not `NO_JIT`
 * with a trailing space, it is the name `NO_JIT ` and PCRE2 rejects it.
 * Returns the index of the terminator (== patlen when the pattern ends
 * first); the caller derives the name's length and reads the FORM. */
size_t pcrec_verb_name_extent_scan(const char *pat, size_t patlen,
                                   size_t nstart)
{
    size_t i = nstart;
    while (i < patlen && pat[i] != ')' && pat[i] != ':' && pat[i] != '=') i++;
    return i;
}
