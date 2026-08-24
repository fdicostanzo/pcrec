/* mod_named_groups.c — module `named-groups` ([M6.3]): the three declaring
 * spellings, (?<name>...) (?'name'...) (?P<name>...), as one shared
 * producer.
 *
 * WHICH SPELLING dispatched here is read off the ELECTED ROW's own `sel`/
 * `tail` (registry.c's rows for this module): `sel == '<'` with no tail is
 * the bare-angle-bracket form, `sel == '\''` is the Perl-quote form, and
 * `sel == 'P'` with `tail == "<"` is the Python form. All three differ only
 * in their CLOSING delimiter (`>` for the first and third, `'` for the
 * second) — the name grammar, the numbering, the duplicate check and the
 * body parse are identical, which is why one port serves all three rather
 * than three copies of the same logic (the `\v`-bug lesson this whole
 * registry exists to avoid, one level up: three near-identical hand copies
 * of a grammar drift the same way three near-identical hand copies of a
 * module attribution did).
 *
 * NAME GRAMMAR, measured against libpcre2 10.46 (tests/probes/
 * probe_named_groups.c — predictor stated before the run, per that
 * directory's own method):
 *
 *   first byte    ASCII letter or '_'   (a leading DIGIT is PCRE2 error
 *                                        144, not merely unconventional —
 *                                        swept, all 256 first-byte values)
 *   later bytes   ASCII letter, digit or '_'
 *   length        1..128 bytes          (129 is PCRE2 error 148; swept
 *                                        1..2000 bytes of an otherwise-
 *                                        valid name — a measured WALL, not
 *                                        an assumed carry-over of PCRE1's
 *                                        older 32-byte limit; the number
 *                                        lives in src/core/limits.h as
 *                                        PCREC_MAX_GROUP_NAME)
 *   duplicate     a compile error       (PCRE2 error 143 with no
 *                                        PCRE2_DUPNAMES; the sibling
 *                                        construct that lifts this,
 *                                        (?J)/DUPNAMES, is RULED OUT OF
 *                                        SCOPE — see mod_modifiers.c's own
 *                                        'J' case, which refuses it
 *                                        unconditionally regardless of
 *                                        whether this module is enabled,
 *                                        so this port never needs to ask)
 *
 * NUMBERING is exactly the base grammar's own rule (parse.c's p_group_body
 * comment): PCRE2 assigns group numbers by OPENING-PAREN order, and a named
 * group participates in that count exactly as a plain `(` does, with ONE
 * measured difference — `(?n)` (no-auto-capture) suppresses a PLAIN group's
 * number but NOT a named one's (probe step 9: `(?n)(a)(?<x>b)` has
 * capturecount=1, namecount=1 — "a" never gets a number at all, and "x"
 * becomes group 1, not group 2). So this port increments `cx->ncap`
 * UNCONDITIONALLY, ignoring `cx->mods.nocap` — the opposite of
 * p_group_body's plain-`(` hook, which gates the increment ON `!nocap`.
 * `cx->want_caps` (the --no-captures BUILD axis, orthogonal to `nocap`,
 * which is a PCRE2 pattern-text axis) still gates whether an A_CAP node is
 * actually built, exactly as it does for a plain group.
 *
 * ENGINE: no forcing rule is added here. A named group's A_CAP node is
 * indistinguishable from a plain numbered group's, so the pre-existing
 * generic capture-forcing rule (src/opt/select_engine.c's
 * `forces_captures`) already selects the VM whenever this construct
 * delivers a real capture slot, and a --no-captures build never builds the
 * A_CAP node at all — see internal.h's comment on this port's declaration
 * and docs/dev/decisions.md's [M6.3] entry for why the three declaring
 * rows' `engines` mask moved from VM_ONLY to ANY_ENGINE instead of this
 * file adding a second, redundant forcer. */

#include <ctype.h>
#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* An arena-owned, NUL-terminated copy of pat[start, start+len) — the one
 * place this module needs a string outliving the pattern buffer's own
 * lifetime guarantees (a `NamedGroup` node is read back at EMISSION time,
 * long after parsing finished). */
static const char *ng_arena_strndup(Ctx *cx, const char *s, size_t len)
{
    char *p = arena_alloc(&cx->arena, len + 1);
    memcpy(p, s, len);
    p[len] = '\0';
    return p;
}

/* [M6.5.2] THE NAME GRAMMAR AS ONE FUNCTION, four readers.
 *
 * This port owns the rule (see the header's measured table); module
 * `backrefs`' three by-name reference spellings must agree with it EXACTLY,
 * because a reference whose grammar is NARROWER than the declaration's cannot
 * name a group that exists, and one that is WIDER accepts a spelling PCRE2
 * refuses. Two hand copies of one grammar is the drift
 * `pcrec_is_bare_anchor` was made a single function for, one construct
 * earlier, and the drift `mod_named_groups.c`'s own three spellings share one
 * port to avoid.
 *
 * Returns the name's length starting at `p[i]`, or 0 with `*why` set. The
 * caller decides what a SHORT answer means: the declaring port requires the
 * closing delimiter next, the reference ports require the whole body. */
size_t pcrec_group_name_scan(const char *p, size_t n, size_t i,
                             const char **why)
{
    size_t start = i;
    if (i >= n || !(isalpha((unsigned char)p[i]) || p[i] == '_')) {
        *why = "subpattern name expected (a name starts with a letter or "
               "'_', never a digit)";
        return 0;
    }
    while (i < n && (isalnum((unsigned char)p[i]) || p[i] == '_'))
        i++;
    return i - start;
}

/* THE LENGTH WALL IS NOT PART OF THE SCAN, and the split is deliberate. It is
 * a separate MEASURED fact (129 bytes is PCRE2 error 148, swept 1..2000), it
 * has its own home in `PCREC_MAX_GROUP_NAME` (src/core/limits.h), and the two
 * callers apply it at DIFFERENT points in their own grammars: this port
 * checks the closing delimiter FIRST, so `(?<`+130 bytes+`x` reports the
 * missing `>` rather than the length. Folding the wall into the scan would
 * move that diagnostic without anyone deciding to. */

/* Is `name` (length `len`) already declared earlier in this pattern? A
 * linear scan of the declaration-order list — named groups are a handful
 * per pattern in any realistic corpus, so this trades a hash table pcrec
 * would have to build, size and free for a dozen-or-so strcmp calls the
 * arena never has to reclaim early. */
static bool ng_is_duplicate(const Ctx *cx, const char *name, size_t len)
{
    for (const NamedGroup *g = cx->named_groups; g; g = g->next)
        if (strlen(g->name) == len && memcmp(g->name, name, len) == 0)
            return true;
    return false;
}

ExtResult pcrec_ngport_declare(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from)
{
    const int close = (rw->sel == '\'') ? '\'' : '>';
    const char *p = cx->pat;
    const size_t n = cx->patlen;
    size_t i = from;

    /* NAME GRAMMAR (see header): an empty or digit-led name is PCRE2's
     * error 144 ("subpattern name must start with a non-digit"). D26
     * owns none of that WORDING — only that a real syntax boundary
     * refuses cleanly — so this port's own message is written for a
     * pcrec reader, not transcribed from PCRE2's. */
    size_t name_start = i;
    {
        const char *why = NULL;
        size_t len = pcrec_group_name_scan(p, n, i, &why);
        if (len == 0) REFUSE(i < n ? i : at, "%s", why);
        i += len;
    }
    size_t name_len = i - name_start;

    if (i >= n || p[i] != close)
        REFUSE(i < n ? i : at,
               close == '\''
                   ? "missing closing ' after subpattern name"
                   : "missing closing > after subpattern name");

    if (name_len > PCREC_MAX_GROUP_NAME)
        REFUSE(name_start,
               "subpattern name is too long (maximum %d bytes)",
               (int)PCREC_MAX_GROUP_NAME);

    /* [M6.5.2] THE DUPLICATE CHECK IS NOW CONDITIONAL, and the condition is
     * READ HERE — at the DECLARATION, against the SCOPED `(?J)` state in force
     * at THIS declaration, never at the pattern's start and never once per
     * compile. That is what seventeen measured libpcre2 cells determine
     * (backrefs_design.md §8.1) and the four separating ones are worth
     * naming, because each kills a plausible alternative reading:
     *
     *   `(?<a>x)(?J)(?<a>y)`      LEGAL   — the SECOND declaration is under it
     *   `(?J:(?<a>x))(?<a>y)`     ERROR   — the second is not
     *   `(?<a>x)(?<a>y)(?J)`      ERROR   — so `(?J)` anywhere does NOT
     *                                       legalise everything
     *   `(?J)(?<a>x)(?-J)(?<a>y)` ERROR even with PCRE2_DUPNAMES set — the
     *                                       inline letter is the authoritative
     *                                       scoped state and can turn the API
     *                                       option OFF
     *
     * So it is `caseless`'s shape one layer up, and the save/restore this port
     * and `p_group_body` already perform around a body is the whole of the
     * scoping. THE REFUSAL'S OLD LONG COMMENT DID NOT RETIRE WITH IT: it
     * recorded two earlier wordings that were both wrong, and that history now
     * lives in mod_modifiers.c's `case 'J'`, which is where the letter is. */
    if (!cx->mods->dupnames && ng_is_duplicate(cx, p + name_start, name_len))
        REFUSE(name_start,
               "two named subpatterns have the same name (write (?J) before "
               "this declaration to allow duplicates)");

    /* NUMBERING (see header): unconditional on `cx->mods.nocap` — a named
     * group always gets a number, even under (?n).
     *
     * [M6.5.2] AND THE `A_CAP` WRAPPER IS NOW BUILT UNCONDITIONALLY TOO,
     * exactly as `p_group_body`'s plain-`(` hook does it and for the same
     * reason: under `--no-captures` a group a BACKREFERENCE names still needs
     * its internal slots (§6.3), and "will any reference name this group" is
     * not a question this line can answer — a forward reference makes it
     * unanswerable here in principle. `pcrec_bref_resolve` deletes the
     * wrapper of every group nothing reads, which for a pattern with no
     * reference deletes ALL of them and reproduces this port's pre-[M6.5]
     * output.
     *
     * Leaving this site gated while `p_group_body` was not is exactly the
     * two-homes drift the shared `pcrec_is_bare_anchor` predicate exists to
     * prevent one construct over, and it was a live miscompile rather than an
     * inconsistency: `--no-captures '(?<n>a)\k<n>'` answered NOMATCH on "aa"
     * because the reference had no slots to read. `run_backref_diff.sh`'s §4
     * arm is what found it. */
    cx->ncap++;
    int capno = (int)cx->ncap;
    if (cx->want_caps && cx->first_cap_pos == (size_t)-1)
        cx->first_cap_pos = at;

    /* Recorded regardless of `want_caps` — the name/number pairing is a
     * LEXICAL fact about the pattern text (the same tier `ngroups`
     * already is), not a build-output fact. */
    {
        NamedGroup *g = arena_alloc(&cx->arena, sizeof *g);
        g->name = ng_arena_strndup(cx, p + name_start, name_len);
        g->number = (int)cx->ncap;
        g->next = cx->named_groups;
        cx->named_groups = g;
        cx->n_named_groups++;
    }

    /* BODY: set/parse/restore, exactly p_group_body's own shape for a
     * plain `(...)` (there is no scoped-state DELTA to apply here — a
     * named group carries no option run — so this is simpler than
     * mod_modifiers.c's `:` branch, but the save/restore/anchor-wrap
     * choreography is the same, because the terminator is the same `)`). */
    {
        ParseMods saved_mods = *cx->mods;
        size_t   saved_pos  = cx->pos;
        cx->pos = i + 1;
        AltInfo info;
        Ast *body = pcrec_parse_body(cx, &info);
        if (cx->pos >= n || p[cx->pos] != ')') {
            *cx->mods = saved_mods;
            cx->pos = saved_pos;
            REFUSE(at, "missing closing ) for group");
        }
        size_t end = cx->pos + 1;
        *cx->mods = saved_mods;
        cx->pos = saved_pos;

        /* The S-M1 anchor wrap: `(?<n>^)*` stays quantifiable exactly as
         * `(^)*` is. [M6.2 wave D] SHARED with p_group_body and
         * mod_modifiers.c rather than mirrored — this site's own copy had
         * gone stale the same way that one had (`(?<n>\b)*` refused where
         * libpcre2 gives (0,0)). See pcrec_is_bare_anchor's comment. */
        body = pcrec_wrap_bare_anchor(cx, body);

        if (capno) {
            Ast *cap = pcrec_ast_node(cx, A_CAP);
            cap->l = body;
            cap->u.cap.no = capno;
            cap->not_repeatable = body->not_repeatable;
            body = cap;
        }

        ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                          .answered_at = want };
        res.node = body;
        res.end = end;
        return res;
    }
}
