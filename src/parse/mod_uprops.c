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

/* The complete one-letter Unicode general-category short codes libpcre2
 * 10.46 accepts as a bare `\pX`/`\PX` form, case-insensitive — measured by
 * tests/probes/probe_uprops.c's 52-letter sweep (both cases of A-Z), 2026-
 * 08-12: `\pC \pL \pM \pN \pP \pS \pZ` compile (as do their lowercase
 * spellings and their `\P` negations); the other 19 letters, either case,
 * are PCRE2 error 147 ("unknown property"), not error 146 — a DISPATCHED,
 * well-formed, unrecognised name, same bucket a multi-character unknown
 * name falls into. HAND-WRITTEN (see this file's header for why); kept
 * independently honest by tests/registry/pcre2_check.c's PC-3 differential,
 * which sweeps all 52 letters against the live oracle every run. */
static const char UPROPS_SHORT_NAMES[] = "CLMNPSZ";

static int uprops_fold(int c)
{
    return (c >= 'a' && c <= 'z') ? c - 'a' + 'A' : c;
}

/* Expects an ALREADY-FOLDED byte and deliberately does NOT fold again: the
 * brace path passes name[0] straight from the normalised-name accumulator,
 * so the accumulator's case fold is LOAD-BEARING through this lookup — a
 * lookup that re-folded would repair a broken accumulator on the way in,
 * which is exactly how mech measured S34 UNDETECTED at first landing (the
 * buffer's only reader masked the sabotage; docs/design_notes_mod06.md §8).
 * The bare-letter path folds its raw pattern byte explicitly at the call. */
static bool uprops_short_lookup(int folded)
{
    return strchr(UPROPS_SHORT_NAMES, folded) != NULL;
}

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

/* The `\p`/`\P` body scanner. Called DIRECTLY from `pcrec_ext_escape`
 * (keyed on `r->recognise == pcrec_registry_uprops_recognise`), not through
 * `r->aport`/`r->cport` — those stay `NO_PORT` on both rows this phase. The
 * `ExtPortFn` signature is kept anyway: `at` (the backslash's offset) is
 * UNUSED here on purpose — every measured blame offset for this construct
 * is a SCAN position derived from `from`, never the backslash (see this
 * file's header) — and `from` is the byte immediately after the `p`/`P`
 * selector, exactly where `cx->pos` already sits when `pcrec_ext_escape`
 * calls this (mirrors `pcrec_modport_optrun`'s own convention,
 * mod_modifiers.c). Always returns `EXT_REFUSAL` — see the header's "no
 * producer" note. */
ExtResult pcrec_modport_uprops(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from)
{
    (void)at;
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
        i++;
        if (uprops_short_lookup(uprops_fold(c0)))
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

    if (i < n && p[i] == '^')
        i++;   /* negation caret: consumed, does NOT enter the 48-char
                  budget below (measured — see this file's header) */

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

    /* well-formed body: `i` is one past the closing '}'. Table lookup ONLY
     * for the axis pcrec's table is EXHAUSTIVE and can answer truthfully
     * about WITHOUT claiming anything about PCRE2: a
     * single significant character (including the empty-name case,
     * sig_count == 0 — measured PCRE2-side as the SAME "unknown property"
     * bucket as a real single unknown letter), no `=` (manager ruling 3,
     * phase-2 authorization). Multi-character and
     * Script=/sc=-shaped bodies promise the module WITHOUT any lookup —
     * pcrec's table does not cover that axis and a "not recognised" claim
     * there would be a claim about PCRE2 pcrec cannot back. */
    bool verifiable_axis = !has_eq && sig_count <= 1;
    bool verifiable_hit = verifiable_axis && sig_count == 1 &&
                          uprops_short_lookup(name[0]);
    if (verifiable_axis && !verifiable_hit)
        REFUSE(i, "\\%c{...}: not a one-letter Unicode property code pcrec "
                  "recognises — requires module '%s'", sel, rw->module);

    REFUSE(i, "\\%c requires module '%s'", sel, rw->module);
}
