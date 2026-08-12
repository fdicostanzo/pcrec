/* mod_modifiers.c — module `modifiers` (MOD-0.5): the `(?` doorway's OPTION
 * RUN grammar.
 *
 * MOD-0.5b, slice 1 — THE GRAMMAR MOVE, byte-identity only. This TU carries
 * pcrec_registry_option_run_ok out of registry.c, together with the whole
 * measured grammar comment below it (the probes-and-code-together rule:
 * R8/C2-9 found the `(*LIMIT_*=digits` rule's measured description in
 * registry.c and its implementation in ext.c had DRIFTED — ext.c accepted
 * `=99999999999` that the description forbade — which is exactly the failure
 * mode of separating a construct's measurements from its code. So the whole
 * block, probes and grammar together, moves as one unit). No semantics
 * change here: RF_OPTION_RUN retires and the twelve GROUP_OPT rows carry a
 * `recognise` pointer instead (see pcrec_registry_option_run_recognise
 * below), but what a pattern compiles to is unchanged — measured over the
 * base/classes corpora, the reject table, and the twelve option-setting
 * shapes swept both valid and malformed, against the pre-move tree.
 *
 * WHERE THIS FUNCTION USED TO LIVE. Until this slice it sat in registry.c
 * under a comment reading "THIS FUNCTION'S HOME IS PROVISIONAL AND WILL
 * MOVE" — a body PARSER living in a file whose own header describes itself
 * as `static const` data plus a lookup, unlike how the other two multi-byte
 * doorways are split (`(*`'s NAME tables and `[[:...:]]`'s NAME table both
 * keep their tables in registry.c and their SCANNING in ext.c/scans.c).
 * Frank's call, 2026-08-10, still stands as the target this slice moves
 * TOWARD, not the design it delivers: a module should expose SEVERAL PORTS
 * — a semantic one and a syntax one — and the doorway should identify the
 * construct from key+tail and then call the row's SYNTAX handler for the
 * details. This slice gets the syntax handler into its own module file and
 * off the flag ext.c used to test; the semantic ports (Ctx modifier state,
 * per-letter production) are MOD-0.5c and are not built yet.
 *
 * It is written in its own file rather than inlined into ext.c for one
 * reason worth keeping wherever it ultimately lands: the grammar below and
 * the measurements that establish it must not be separated. Whichever file
 * holds the port, the probes and the code go together. */

#include "core/internal.h"

/* Splitting the catch-all into eleven option-letter rows fixed the BYTE and
 * left the same over-promise one level down: `(?iZ)`, `(?-Z)` and `(?i-Z)` are
 * PCRE2 error 111 and pcrec still answered "requires module 'modifiers'",
 * because the row is chosen by the first byte and nothing read the rest. That
 * is Q2's own defect at a smaller scale — the shape the wake brief warns about
 * as "fixing the narrowest instance and calling it the class".
 *
 * So this doorway reads its whole run, exactly as `(*` reads its whole name.
 *
 * THE GRAMMAR IS MEASURED, and the sub-option rule is why it had to be. Swept
 * against libpcre2 10.46 over single bytes, both terminators, the `^` and `-`
 * prefixes, and every two-byte run:
 *
 *     letters   J U a i m n r s x          and NOTHING else
 *     a<sub>    aD aP aS aT aW             one ASCII-restrict letter after `a`
 *     (?aPP)    error 111                  ...and only one; `P` is not a letter
 *     (?aDPS)   error 111                  same
 *     repeats   (?xx) (?xxx) (?imsxJU)     OK — a letter may repeat
 *     hyphen    (?i-m) (?i-) (?-) (?aP-i)  OK
 *     caret     (?^) (?^i) (?^aP)          OK — and only at the very start
 *     terminator  ')' or ':'
 *
 * Every one of those lines is a probe that was run, not a sentence from
 * pcre2syntax. The `a` sub-options in particular are invisible to any rule
 * derived from single letters, and a "set of option letters" implementation —
 * the obvious one — accepts `(?aPP)` and rejects `(?aP)`, getting BOTH
 * directions wrong.
 *
 * THE QUESTION IS RECOGNITION, NOT VALIDITY, and getting that backwards is the
 * mistake this function was written with. PCRE2 has two answers for a bad run
 * and only one of them means "no construct here":
 *
 *     (?i-m-s) (?--i) (?-i-) (?i--m) (?^-i)   error 194 "invalid hyphen in
 *                                             option setting" — PCRE2 HAS
 *                                             recognised an option setting
 *     (?i-mZ) (?a-P) (?^^i) (?i^m)            error 111 — no construct at all
 *
 * So hyphens may appear anywhere and repeat: a misplaced one is a MALFORMED
 * option setting, which module 'modifiers' is exactly what would diagnose. The
 * doorway names the module; the module validates the body. Writing the stricter
 * "at most one hyphen, never after ^" rule here made pcrec answer "unrecognized
 * character" for five shapes PCRE2 calls option settings — an UNDER-promise,
 * the mirror of the over-promise Q2 removes, and the generated differential in
 * pcre2_check.c refused it within a minute of being pointed at it. */

static bool opt_letter(int c)
{
    return c == 'J' || c == 'U' || c == 'a' || c == 'i' || c == 'm' ||
           c == 'n' || c == 'r' || c == 's' || c == 'x';
}

/* The ASCII-restrict sub-options, valid ONLY directly after `a`. */
static bool opt_a_sub(int c)
{
    return c == 'D' || c == 'P' || c == 'S' || c == 'T' || c == 'W';
}

bool pcrec_registry_option_run_ok(const char *at, size_t avail)
{
    size_t i = 0;
    bool caret = false, hyphen = false;

    if (!at) return false;

    /* `^` only at the very start: `(?^^i)` and `(?i^m)` are error 111. */
    if (i < avail && at[i] == '^') { caret = true; i++; }

    for (;;) {
        /* Running off the END of the pattern is not an illegal byte: `(?i` is
         * PCRE2 error 114, "missing closing parenthesis", which is a RECOGNISED
         * option setting that was truncated. Returning false here made pcrec
         * answer "unrecognized character" for every truncated option run, and
         * registry_check's own 255-byte sweep — whose template is `(?%c`, with
         * no terminator at all — failed on all eleven option bytes at once. */
        if (i >= avail) return true;
        if (at[i] == ')' || at[i] == ':') return true;   /* a terminator ends it */

        if (at[i] == '-') {
            /* PCRE2 STOPS AT THE FIRST ERROR, and that ordering is part of the
             * rule rather than an implementation detail to be normalised away.
             * A hyphen that is invalid HERE — a second one, or one after `^` —
             * raises error 194 and PCRE2 never looks at what follows. So
             * `(?--D)` is a recognised (malformed) option setting even though
             * `D` would have been error 111 on its own, and a rule that scanned
             * the whole run before deciding got that backwards for 24 shapes. */
            if (caret || hyphen) return true;
            hyphen = true;
            i++;
            continue;
        }
        if (!opt_letter((unsigned char)at[i])) return false;
        bool is_a = at[i] == 'a';
        i++;
        /* `a` may take exactly one ASCII-restrict sub-option, and those letters
         * are not option letters anywhere else: `(?aP)` compiles, `(?a-P)` and
         * `(?aPP)` are error 111. */
        if (is_a && i < avail && opt_a_sub((unsigned char)at[i])) i++;
    }
}

/* ---- MOD-0.5b: the recogniser that retires RF_OPTION_RUN -----------------
 *
 * The twelve GROUP_OPT rows now carry this in their `recognise` field so
 * ext.c can key off the FIELD instead of a flag: "does this row's construct
 * need the doorway's whole-run check" becomes a pointer-identity question
 * (`r->recognise == pcrec_registry_option_run_recognise`) rather than a bit.
 *
 * IT DOES NOT RUN THE CHECK ITSELF, and that is a deliberate, measured
 * choice, not a shortcut. The obvious design — wrap pcrec_registry_option_
 * run_ok in the standard `(at, avail, tail)` signature and let MOD-0.2's
 * arbitration run it directly, the way recognise_N_name_brace (registry.c)
 * decides its own row — does not fit here, for a reason specific to this
 * construct: option_run_ok's grammar starts AT THE SELECTOR BYTE (`(?i-m`'s
 * run is "i-m", the letter included), one byte before what `at` conventionally
 * means everywhere else in this table (text AFTER the selector, what a `tail`
 * is compared against). Reconstructing that earlier byte as `at - 1` is safe
 * from ext.c's own arbitrate call, where `at` is always cx->pat plus a real
 * offset with a real selector byte sitting before it — but the SAME
 * recogniser is also called, through the SAME field, by
 * tests/registry/registry_check.c's arbitration sweeps
 * (check_arbitration_liveness's bucket floors and its no-ambiguity sweep),
 * against hand-built probe buffers that carry no such byte. `at - 1` there
 * reads outside the probe array — undefined behaviour introduced by a row's
 * OWN recogniser, exercised by the very checks meant to keep arbitration
 * honest. So this function stays a pure MARKER, answering exactly what the
 * old tail-less default already answered ("no tail: answers always", D32 §2)
 * — zero change to any arbitration or liveness count — and ext.c keeps doing
 * the real check itself, with the real Ctx, exactly as it did under the flag. */
bool pcrec_registry_option_run_recognise(const char *at, size_t avail,
                                         const char *tail)
{
    (void)at; (void)avail; (void)tail;
    return true;
}
