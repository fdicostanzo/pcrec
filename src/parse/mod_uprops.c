/* mod_uprops.c — module `unicode-props` (MOD-0.6 phase 2): the `\p`/`\P`
 * doorway's BODY SCANNER.
 *
 * NO PRODUCER LANDS HERE (Frank's ruling, 2026-08-12 MOD-0.6 phase 2
 * session): `\p`/`\P`/`\N{U+` all still REFUSE — nothing that refuses today
 * may start COMPILING. What this file adds is a REFINED refusal: today
 * every tail after `\p`/`\P` gets the identical generic "\p requires module
 * 'unicode-props'" text from ext.c's fallback, at the BACKSLASH's offset.
 * Measured against libpcre2 10.46 (tests/probes/probe_uprops.c, the full
 * 256-byte tail sweep), that single text hides a real, load-bearing split:
 * every possible tail lands on exactly one of PCRE2's two "yes, this is a
 * property escape" outcomes — error 146 "malformed \P or \p sequence" (the
 * shape itself is not even attemptable: no letter, no `{`, an unterminated
 * `{`, or more than 48 significant characters) or error 147 "unknown
 * property..." (a WELL-FORMED body PCRE2 does not recognise) — and NEVER
 * anything a caller could read as "not a \p construct at all". Both are
 * D28's CLAIM sub-case SYN_MALFORMED, restored to primary by D30 §3: PCRE2
 * DISPATCHED, so pcrec still owes the module either way — but the OFFSET
 * differs, and offsets are pcrec's own convention to get right (D26's
 * addendum), not PCRE2's wording to chase.
 *
 * THE SEAM. Not an aport/cport (those stay NO_PORT on both rows — no
 * producer, so nothing installed there could ever legally return anything
 * but a refusal, and D33's port slots are for constructs that DO produce).
 * Instead: `\p`/`\P` are single-row buckets (no sibling to arbitrate
 * against — measured, the full 256-byte sweep has no DECLINE-shaped tail
 * at all, so `recognise` answering "always" is not a placeholder, it is
 * the permanently correct answer, D32 §2's honest fallback). Their
 * `recognise` field is set to `pcrec_registry_uprops_recognise` below — a
 * MARKER, functionally identical to the tail-less default, exactly the
 * shape mod_modifiers.c's `pcrec_registry_option_run_recognise` uses for
 * the twelve GROUP_OPT rows: ext.c keys off the POINTER's identity
 * (`r->recognise == pcrec_registry_uprops_recognise`) and calls
 * `pcrec_modport_uprops` DIRECTLY, bypassing the generic RD_MODULE
 * fallback text — the mod_verbs.c precedent (a direct call outside the
 * port machinery) crossed with the mod_modifiers.c precedent (the row
 * carries the connection, not a hardcoded selector-byte special case in
 * ext.c). `pcrec_modport_uprops` keeps the full `ExtPortFn` signature on
 * purpose: when a producer eventually lands, wiring `aport`/`cport` to this
 * SAME function is a one-line row edit, not a rewrite.
 *
 * THE ALGORITHM is measured, not designed from the PCRE2 documentation
 * (there is none worth trusting per D26): normalise WHILE SCANNING, count
 * SIGNIFICANT characters only, and stop at 49 — R10 disposition 5's ruling,
 * confirmed exactly by the probe (not corrected: 48 is right). Every
 * insignificant byte (space, tab, hyphen, underscore) is skipped without
 * counting; ASCII case is folded on the way in; a leading `^` is consumed
 * once, before the count starts, and does NOT itself count (measured:
 * `\p{^` + 48 sig chars `}` and `\p{^` + 49 sig chars `}` land on the exact
 * same two errors, one byte later than the no-caret case). The blame
 * offset for every outcome is the SCAN POSITION at the moment of decision
 * — one past the last byte consumed — which happens to agree with every
 * PCRE2 offset measured for this construct (coincidence D26's addendum
 * says is fine to take and never to chase).
 *
 * THE SHORT-NAME TABLE is HAND-WRITTEN, not generated from a libpcre2
 * census (manager ruling at the 2026-08-12 phase-2 authorization,
 * overriding the probe_cls_bits.c precedent this file's design note
 * proposed): a table generated from libpcre2 and then
 * checked by a differential against the SAME libpcre2 install is one
 * source wearing two hats — see the memory `pcrec-check-design-lessons`
 * and this project's repeated finding of exactly that shape (R4 through
 * R9, D27's whole argument). Independently verified by
 * tests/registry/pcre2_check.c's PC-3 differential, whose name axis sweeps
 * ALL 52 letters — not just these 14 — so an eighth short-category letter
 * a future PCRE2 adds surfaces as a differential failure, not a stale
 * table (D26's addendum: a version bump is a re-measurement event).
 *
 * THE MESSAGE TAXONOMY, and the wording constraint that shapes it (manager
 * ruling 3, same authorization): pcrec's own "not recognised" claim must be phrased as
 * a claim about PCREC's knowledge, never PCRE2's — so it is used ONLY where
 * pcrec's own table is EXHAUSTIVE for the axis in question (a single
 * significant character, no `=`; the 14-of-52 table is complete, PC-3-
 * verified). A multi-character name or a `Script=`/`sc=`-shaped body
 * promises the module WITHOUT any lookup, because pcrec's table does not
 * cover that axis and must not imply that it does — a well-formed shape
 * pcrec cannot verify is not the same claim as a well-formed shape pcrec
 * has checked and rejected. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse_mods.h"   /* `-i`/`(?i)` selects which of a row's two spans
                           * this module produces — see uprops_lookup */

#include "uprops_tables.inc"

/* THE NAME LOOKUP. `name`/`len` is the accumulator's NORMALISED content —
 * upper-cased, with space/tab/hyphen/underscore already dropped — and the
 * generated table's keys are normalised by the SAME rule at generation time
 * (third_party/ucd-16.0.0/generate.py's `normalise`, which quotes this
 * scanner's rule at its own definition). So the comparison is a plain
 * length-then-memcmp and there is no second normalisation here to disagree
 * with the first.
 *
 * IT DELIBERATELY DOES NOT FOLD, and that is a mech finding rather than a
 * micro-optimisation: the accumulator's case fold is LOAD-BEARING through
 * this lookup, and a lookup that re-folded would REPAIR a broken accumulator
 * on the way in — which is exactly how mech measured S34 UNDETECTED at first
 * landing (docs/design/design_notes_mod06.md §8). The bare-letter path folds
 * its raw pattern byte explicitly at the call, once. */
/* `caseless` selects which of the row's TWO spans is returned, and that is
 * the whole of this module's interaction with `-i`. It is NOT the generic
 * `cls_casefold` widening every other set producer gets: MEASURED, PCRE2
 * under caseless reads `\p{Lu}`, `\p{Ll}` and `\p{Lt}` as `\p{L&}` and leaves
 * every other property alone (the generator's CASELESS_AS carries the two
 * sweeps), while an ASCII fold of `\p{Lu}` would produce a set that is
 * neither. So the substitution IS the caseless rule, and no fold is applied
 * on top of it. */
static const PcrecCpRange *uprops_lookup(const char *name, size_t len,
                                         bool caseless, int *n)
{
    for (size_t i = 0; i < pcrec_uprop_names_n; i++) {
        const char *k = pcrec_uprop_names[i].name;
        if (strlen(k) != len || memcmp(k, name, len) != 0) continue;
        *n = caseless ? pcrec_uprop_names[i].ci_n : pcrec_uprop_names[i].n;
        return pcrec_uprop_iv + (caseless ? pcrec_uprop_names[i].ci_off
                                          : pcrec_uprop_names[i].off);
    }
    return NULL;
}

static int uprops_fold(int c)
{
    return (c >= 'a' && c <= 'z') ? c - 'a' + 'A' : c;
}

/* THE ONE-LETTER AXIS, and stage 3 RETIRED THE HAND-WRITTEN TABLE THAT USED
 * TO ANSWER IT.
 *
 * Until this stage the seven short general-category codes (`C L M N P S Z`)
 * were a hand-written string literal here, under a manager ruling whose
 * reason was that *"a table generated from libpcre2 and then checked by a
 * differential against the SAME libpcre2 install is one source wearing two
 * hats"*. THAT RULING IS UNTOUCHED AND IS WHY THE TABLE IS STILL NOT
 * GENERATED FROM libpcre2. What changed is that there is now a THIRD source
 * — the vendored UCD — and the seven letters fall out of it as the seven
 * major categories, so keeping a hand copy beside the generated one would be
 * a second home for one fact (the D24 drift shape, at the scale of a single
 * `strchr`).
 *
 * THE INDEPENDENCE ARGUMENT SURVIVES INTACT, which is the point: the check
 * that keeps this axis honest is `tests/registry/pcre2_check.c`'s PC-3
 * name-axis sweep, which asks the LIVE ORACLE about all 52 letters — not
 * about the seven — so an eighth short-category letter a future PCRE2 adds
 * still surfaces as a differential failure rather than as a stale table. The
 * oracle is still checking a table it did not produce; only the table's
 * source moved from a human to the UCD.
 *
 * There is no `uprops_short_lookup` any more either: the one-letter axis is
 * `uprops_lookup(&folded, 1, ...)`, one call, at the one site that asks it. A
 * wrapper whose whole body was a length-1 call would be the second home this
 * paragraph is about, one indirection smaller. */

/* The twelve GROUP_OPT rows' `recognise` field carries
 * `pcrec_registry_option_run_recognise` as a MARKER rather than a flag
 * (mod_modifiers.c). This is the same shape for the escape doorway's two
 * `\p`/`\P` rows: always answers true — identically to the tail-less
 * default `pcrec_recognise_tail_default(at, avail, NULL)` — because
 * measured (this file's header) there is no tail shape that should route
 * away from these rows. It exists as a POINTER ext.c can key off, so the
 * row carries its own connection to the body scanner rather than ext.c
 * hardcoding a `c == 'p'` special case disconnected from the registry. */
bool pcrec_registry_uprops_recognise(const char *at, size_t avail,
                                     const char *tail)
{
    (void)at; (void)avail; (void)tail;
    return true;
}

/* PRODUCE. `at` is the backslash's offset (what the CALLER blames), `end` is
 * one past the closing `}` or the bare letter — the caller advances there
 * (check06's cursor rule: the doorway never writes `cx->pos`).
 *
 * THE POSITION MAPPING IS ext.c's OWN, spelled the same way its `PORT_SET`
 * branch spells it: a set at atom position is the whole node, a set inside a
 * class is members the caller ORs in. Repeating the two-line rule here rather
 * than routing through that branch is deliberate — the branch's set is 32
 * static bytes on the row and this one is an interval list chosen at scan
 * time, so there is nothing to share but the mapping itself. */
static ExtResult uprops_produce(Ctx *cx, ExtWant want, bool in_class,
                                size_t at, size_t end,
                                const PcrecCpRange *iv, int n, bool negate)
{
    ExtResult res = { .what = in_class ? EXT_MEMBERS : EXT_NODE,
                      .at = at, .msg = "", .answered_at = want };
    res.node = pcrec_ast_class_from_iv(cx, iv, n, negate);
    res.end  = end;
    return res;
}

/* The `\p`/`\P` body scanner AND PRODUCER. Called DIRECTLY from
 * `pcrec_ext_escape` (keyed on `r->recognise ==
 * pcrec_registry_uprops_recognise`), not through `r->aport`/`r->cport` —
 * those stay `NO_PORT` on both rows, and `internal.h`'s declaration carries
 * the argument for why that is now a decision rather than a phase.
 *
 * `at` is the backslash's offset and is used ONLY as the produced result's
 * blame anchor: every measured REFUSAL offset for this construct is a SCAN
 * position derived from `from`, never the backslash (see this file's header).
 * `from` is the byte immediately after the `p`/`P` selector, exactly where
 * `cx->pos` already sits when `pcrec_ext_escape` calls this (mirrors
 * `pcrec_modport_optrun`'s own convention, mod_modifiers.c).
 *
 * THE NEGATION IS AN XOR OF TWO INDEPENDENT SPELLINGS, `\P{X}` and `\p{^X}`,
 * so `\P{^L}` is `L` — measured against the oracle rather than assumed, and
 * it is the reading under which the caret is a property of the BODY and the
 * selector a property of the ESCAPE, which is how the scanner already treats
 * them (the caret is consumed before the significant-character budget opens
 * and the selector never enters the name). */
ExtResult pcrec_modport_uprops(Ctx *cx, const RegRow *rw, ExtWant want,
                               bool in_class, size_t at, size_t from)
{
    const char *p = cx->pat;
    size_t n = cx->patlen;
    size_t i = from;
    int sel = rw->sel;   /* 'p' or 'P' */

    if (i >= n)
        REFUSE(i, "\\%c: malformed property escape — requires module '%s'",
               sel, rw->module);

    int c0 = (unsigned char)p[i];

    /* the bare-letter form, \pX: the WHOLE construct is one byte, and its
     * blame offset is always "one past that byte" whether or not the
     * letter is one pcrec's table recognises (measured: \pA and \pC — an
     * unknown and a known short name — both blame the SAME relative
     * position; only the message differs). */
    if ((c0 >= 'A' && c0 <= 'Z') || (c0 >= 'a' && c0 <= 'z')) {
        char folded = (char)uprops_fold(c0);
        int nv;
        const PcrecCpRange *iv = uprops_lookup(&folded, 1, cx->mods->caseless,
                                               &nv);
        i++;
        if (iv && want == WANT_RESULT)
            return uprops_produce(cx, want, in_class, at, i, iv, nv,
                                  sel == 'P');
        if (iv)
            REFUSE(i, "\\%c requires module '%s'", sel, rw->module);
        REFUSE(i, "\\%c: not a one-letter Unicode property code pcrec "
                  "recognises — requires module '%s'", sel, rw->module);
    }

    if (c0 != '{') {
        /* neither a letter nor `{`: no property-escape SHAPE at all.
         * Measured (the 256-byte sweep): every one of the 204 non-letter
         * tail bytes, including a truncated pattern (the avail==0 case
         * just above), is PCRE2 error 146 — dispatched, malformed, still
         * owed a module per D28's SYN_MALFORMED rule (D30 §3). Blame is
         * ONE PAST the bad byte (measured: \p! and \p9 both blame offset 3,
         * not 2), so the byte is consumed before REFUSE fires. */
        i++;
        REFUSE(i, "\\%c: malformed property escape — requires module '%s'",
               sel, rw->module);
    }

    i++;   /* consume '{' */

    bool caret = false;
    if (i < n && p[i] == '^') {
        i++;   /* negation caret: consumed, does NOT enter the 48-char
                  budget below (measured — see this file's header) */
        caret = true;
    }

    int sig_count = 0;
    char name[PCREC_UPROP_NAME_MAX];   /* fixed buffer, never an arena (D29:
                                          arena_alloc aborts under a memory
                                          limit, K7) */
    bool has_eq = false;

    for (;;) {
        if (i >= n)
            /* unterminated `{...` — malformed regardless of what the
               partial body contained (measured: \p{L at EOF is 146, same
               as \p{ at EOF). */
            REFUSE(i, "\\%c: malformed property escape — requires module '%s'",
                   sel, rw->module);
        int c = (unsigned char)p[i];
        if (c == '}') {
            i++;
            break;
        }
        i++;
        if (c == ' ' || c == '\t' || c == '-' || c == '_')
            continue;   /* insignificant — measured exhaustively for
                           \p{L}-vs-variants; does not enter the count */
        if (c == '=')
            has_eq = true;
        if (sig_count == PCREC_UPROP_NAME_MAX)
            /* the 49th significant character: pcrec's own blame convention
             * is "right after the byte that overflowed the budget", which
             * measures identically to libpcre2's own offset in every cell
             * probed — both a bare run of significant characters and one
             * padded with insignificant filler between every character
             * (the padding proves it is SIGNIFICANT count, not total body
             * length, that is being tracked: the blame offset tracks the
             * count, not the padding). A coincidence worth taking per
             * D26's addendum, never to be chased if a future PCRE2
             * disagrees. */
            REFUSE(i, "\\%c: malformed property escape — requires module '%s'",
                   sel, rw->module);
        name[sig_count++] = (char)((c >= 'a' && c <= 'z') ? c - 'a' + 'A' : c);
    }

    /* WELL-FORMED BODY. `i` is one past the closing '}'. Three questions, in
     * this order, and the order is what keeps each answer honest:
     *
     * (1) DOES PCREC HAVE THIS SET? The lookup is over the WHOLE generated
     *     table, not only the one-letter axis — `\p{Lu}`, `\p{L&}`, `\p{Xan}`
     *     and `\p{Assigned}` are all multi-character names pcrec DOES know,
     *     so production is orthogonal to the exhaustiveness claim below.
     *     A hit at post-gate WANT_RESULT produces; a hit at any lower level
     *     means the module's gate is shut, which is the ordinary
     *     "requires module" answer and is unchanged from before stage 3.
     *
     * (2) IS THE MISS ON AN AXIS PCREC'S TABLE IS EXHAUSTIVE FOR? Only the
     *     single-significant-character, no-`=` axis is (the empty name,
     *     sig_count == 0, rides with it — measured PCRE2-side as the SAME
     *     "unknown property" bucket as a real unknown letter). There pcrec
     *     may say the name is not one it recognises, because the claim is
     *     about PCREC's own vocabulary and that vocabulary is complete for
     *     one-letter codes. Manager ruling 3, phase-2 authorization, intact.
     *
     * (3) OTHERWISE THE MISS IS UNCLASSIFIABLE BY PCREC and must not be
     *     dressed up as either. `\p{Greek}` and `\p{Alphabetic}` are REAL
     *     PCRE2 properties this stage does not ship (§3.4 stages scripts to
     *     [M5.0] stage 5 and declines booleans outright); `\p{Script=Greek}`
     *     is a whole axis the table does not cover; `\p{Foo}` is genuinely
     *     unknown — and nothing here can tell them apart, so all three get
     *     the same answer, which names the MODULE and never the name.
     *
     * WHAT STAGE 3 CHANGED IN THE WORDING, AND WHY IT HAD TO. Before the
     * producer, every one of these refusals ended in "requires module
     * 'unicode-props'", which was true at every gate state because the module
     * could compile nothing. It is now a LIE at an OPEN gate — it asks the
     * user to do the thing they have already done, which is exactly K14's
     * shape and exactly what ext.c's own UNBUILT epilogue exists to avoid
     * ([M6.2] wave A: "a module that lands its constructs across several
     * waves ... 'requires module X' is then a lie of the most annoying
     * kind"). So each refusal below is gate-split:
     *
     *   - the EXHAUSTIVE-axis miss drops the module clause entirely at an
     *     open gate, because an unknown one-letter code is a PATTERN error
     *     and no module will ever implement it;
     *   - the UNCLASSIFIABLE miss takes the UNBUILT tier's wording, because
     *     "this module has not implemented it yet" is the true sentence for
     *     `\p{Greek}` and the closest honest one for the other two.
     *
     * The CLOSED-gate texts are unchanged, byte for byte, which is what keeps
     * every pre-stage-3 `tests/reject/` pin green rather than re-baselined —
     * and the open-gate texts get their own `reject_gated` pins beside them. */
    int nv = 0;
    const PcrecCpRange *iv =
        has_eq ? NULL
               : uprops_lookup(name, (size_t)sig_count, cx->mods->caseless, &nv);
    if (iv && want == WANT_RESULT)
        return uprops_produce(cx, want, in_class, at, i, iv, nv,
                              (sel == 'P') ^ caret);
    if (iv)
        REFUSE(i, "\\%c requires module '%s'", sel, rw->module);

    bool verifiable_axis = !has_eq && sig_count <= 1;
    if (verifiable_axis) {
        if (want == WANT_RESULT)
            REFUSE(i, "\\%c{...}: not a one-letter Unicode property code "
                      "pcrec recognises", sel);
        REFUSE(i, "\\%c{...}: not a one-letter Unicode property code pcrec "
                  "recognises — requires module '%s'", sel, rw->module);
    }

    if (want == WANT_RESULT)
        /* ext.c's UNBUILT macro spelled out rather than invoked: that macro
         * reads a `const RegRow *r` from its includer's scope and this
         * function's row is `rw`. PCREC_UNBUILT_MARKER is kept inside the
         * format for the macro's own stated reason (D65 keys on the
         * substring), so the two sites cannot drift in the half that is
         * machine-read. */
        REFUSE(i, "module '%s' " PCREC_UNBUILT_MARKER " \\%c{...}: this "
                  "Unicode property is not implemented yet", rw->module, sel);
    REFUSE(i, "\\%c requires module '%s'", sel, rw->module);
}
