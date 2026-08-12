/* The four doorways: dispatch from the base grammar into the construct
 * registry (D24, step SR-2).
 *
 * WHY THIS FILE EXISTS. SR-1 built registry.c — one declarative home for every
 * non-base construct — but parse.c did not read it, so the registry was a
 * SIXTH copy of knowledge that already lived in five places. This file is the
 * edge that makes it the only copy: parse.c now keeps the base grammar and
 * nothing else, and every non-base byte leaves it through one of four calls.
 *
 *     after `\`              pcrec_ext_escape        (\d \v \p \K \g \Q \1)
 *     after `(?`             pcrec_ext_group         ((?= (?< (?> (?# (?i)
 *     after `(*`             pcrec_ext_verb          ((*SKIP) (*CR)) — MOD-0.4
 *                                                     moved this one to
 *                                                     mod_verbs.c; declared
 *                                                     in internal.h, called
 *                                                     from parse.c unchanged
 *     after `[` in a class   pcrec_ext_class_bracket ([[:alpha:]] [[.a.]])
 *
 * THE BASE SWITCH RUNS FIRST AND RETURNS. Every one of these is called only
 * after parse.c's own switch has declined, which is what keeps the common path
 * cheap: a base-tier pattern reaches only the class-bracket one, once per
 * non-negated `[` (measured, R6 — the older claim of "none at all" was wrong).
 * `(?:` is the one
 * construct that shares a doorway with non-base syntax, and parse.c answers it
 * before the call — its registry row exists so the table is COMPLETE for SR-3's
 * dump, not because anything looks it up. SR-5 turns that from a claim into an
 * instrumented measurement.
 *
 * WHAT DOES NOT LIVE HERE. Base syntax, including two things that look like
 * they belong: `\x{...}` and the possessive `+` are sub-cases of BASE
 * constructs (the `\x` decoder and the quantifier suffix), not doorways.
 * (`\b`-in-class IS routed here since MOD-0.3d — still base SEMANTICS, but
 * carried as the row's own BASE class port instead of a parse.c special
 * case; ExtPort.base is what keeps the gate off it.)
 *
 * THE CLAIM IS RETURNED, NOT RAISED (MOD-0.1, D33 §5). Every dispatch still
 * ends in a refusal — every row is RS_MODULE or RS_REJECTED — but the refusal
 * is now an ExtResult the CALLER receives and hands to pcrec_ext_finish, the
 * one epilogue below, instead of a ctx_fail that longjmps past it. The
 * diagnostic is formatted AT CLAIM TIME into the result (representability:
 * a diagnostic must outlive its handler or D33 §6 collapses and pair_opens'
 * deletion — later reversed by R14 anyway — comes back). Byte-identity: the
 * REFUSE macro runs the exact snprintf the old ctx_fail ran, into a buffer of
 * the same size, and the epilogue fires it at the same offset; no rendered
 * diagnostic moved. The `noreturn` era's R5 lesson (warn-not-error, no guard
 * without -Werror) is retired with the attributes themselves: falling off a
 * value-returning doorway is now an ordinary -Wreturn-type warning that
 * `make strict` promotes. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

/* THE GATE (§5.4/§15, the ASK contract — see ExtWant in internal.h): demote
 * RESULT to VERDICT for a row whose module is not in the enabled set,
 * flooring at VERDICT — never CLAIM, which would be silence where a
 * diagnostic is owed. Since MOD-0.1 slice 9 this is the real membership
 * test: it sits AFTER row choice (enablement is a fact about the row's
 * module) and consults enabled.c — the one place ext.o's undefined list
 * gains the enabled-set symbol, which is exactly where check01's nm
 * contract wants it: the gate at the seam, never in a scan.
 *
 * A NULL row and a non-module row both demote: no row means nobody's
 * construct (the refusal is a terminal verdict), and an RS_REJECTED row can
 * never be enabled. An ENABLED row keeps WANT_RESULT — and since no module
 * port EXISTS yet, its refusal then reports answered_at = result, which is
 * the externally visible difference between "gate open, port missing"
 * (D33's NULL-port refusal) and "gate closed" (--probe-ask, cli case10).
 * Equivalence of the VERDICT itself across enabled sets is check07's
 * subject, and holds today by construction: no port, same refusal.
 *
 * NON-STATIC since MOD-0.4: `pcrec_ext_verb` moved out to mod_verbs.c and
 * still needs this exact gate, so this is now the ONE definition two TUs
 * share (declared in internal.h) rather than a second copy risking drift. */
ExtWant pcrec_ext_gate(const RegRow *r, ExtWant want)
{
    if (want == WANT_RESULT &&
        !(r && r->status == RS_MODULE && pcrec_feature_enabled(r->feature)))
        return WANT_VERDICT;
    return want;
}

/* REFUSE and BAD_ROW moved to internal.h at MOD-0.4 for the same reason —
 * mod_verbs.c's `pcrec_ext_verb` uses both, and one shared definition beats
 * two copies of the refusal epilogue. DECLINE stays here: only doorway 4
 * (this file) ever produces it. */

/* No construct here; the cursor is unchanged. Only doorway 4 produces this.
 * A decline is a CLAIM-level answer — "not mine" costs nothing to say. */
#define DECLINE() return (ExtResult){ .what = EXT_NOT_MINE, .at = 0, .msg = "", \
                                      .answered_at = WANT_CLAIM }

/* The ONE epilogue (D33 §5/§8): a refusal fires here, and only here. A caller
 * that must override a claim — the endpoint rule, D33 §6 — looks at the
 * ExtResult BEFORE calling this; today no caller overrides.
 *
 * A PRODUCING outcome (EXT_SCALAR / EXT_MEMBERS / EXT_NODE) must be
 * consumed by the CALLER before this runs — the epilogue renders refusals,
 * it does not splice results. Reaching the wall below means a port produced
 * a value its call site does not yet handle: the PARSE-1 silent-discard
 * defect, reported loudly instead of dropped. */
void pcrec_ext_finish(Ctx *cx, const ExtResult *r)
{
    if (r->what == EXT_NOT_MINE) return;
    if (r->what != EXT_REFUSAL)
        ctx_fail(cx, r->at,
                 "internal error: unconsumed producing doorway outcome %d",
                 (int)r->what);
    ctx_fail(cx, r->at, "%s", r->msg);
}

/* SR-9's tail context, computed from the Ctx these functions already hold.
 * `after` is the offset of the first byte PAST the doorway's selector byte, so
 * a row's `tail` is compared against the text the pattern really has there.
 *
 * THE POINT OF DOING IT HERE is that parse.c does not change: the design's
 * comparison table claims "parse.c call sites changed: 0" against the string
 * selector alternative, and this is what makes that true. A truncated pattern
 * yields avail = 0, which matches no tail, so `(?P` at end-of-pattern falls to
 * the bare `P` row instead of reading past the buffer. */
static const char *tail_at(const Ctx *cx, size_t after, size_t *avail)
{
    if (after >= cx->patlen) { *avail = 0; return NULL; }
    *avail = cx->patlen - after;
    return cx->pat + after;
}

/* ---- doorway 1: after '\' ----------------------------------------------
 * `c` is the byte after the backslash and the cursor sits just past it. Called
 * only once parse.c's decoder has declined: the plain character escapes
 * (\n \t \r \f \a \e \xHH) and escaped punctuation return a byte value and
 * never arrive here. (Class-context `\b`/octal/literal-fallbacks DO arrive
 * since MOD-0.3d — their BASE class ports answer below.)
 *
 * `in_class` selects the diagnostic, and it selects more than the wording:
 * RD_MODULE_OCTAL is the ATOM form only. Since MOD-0.3d the digit rows and
 * `\g`/`\k` DO arrive here with in_class set — their class position is base
 * semantics (octal / literal fallback, FIX-3/K13) carried as BASE class
 * ports, produced below regardless of the enabled set. */
static ExtResult esc_answer(Ctx *cx, ExtWant want, int c, bool in_class,
                            size_t at, const RegRow **elected)
{
    /* cx->pos sits just past the escape byte, so that IS the tail position. */
    size_t avail;
    bool amb = false;
    const char *tl = tail_at(cx, cx->pos, &avail);
    const RegRow *r = pcrec_registry_arbitrate(RK_ESC, c, tl, avail, &amb);
    *elected = r;   /* MOD-0.7 slice 2; NULL for an unknown escape */
    /* `asked` survives the gate for BASE ports (MOD-0.3d): a port whose
     * semantics are PCRE2 base facts ([\b] is backspace, [\12] is octal)
     * answers at the level the CALLER asked, whatever the enabled set —
     * per-port gating, §14.3's split. Module ports keep the demoted level. */
    ExtWant asked = want;
    want = pcrec_ext_gate(r, want);

    if (!r) {
        if (in_class) REFUSE(at, "unknown escape \\%c in class", c);
        REFUSE(at, "unknown escape \\%c", c);
    }
    /* Two answering rows at the winning rank (MOD-0.2, D32 §2): a registry
     * defect, not a pattern error — arbitration cannot elect a row and must
     * say so rather than let declaration order decide. Unreachable on the
     * correct table; registry_check's liveness floors keep that measured. */
    if (amb)
        REFUSE(at, "internal error: ambiguous registry arbitration for an escape");
    if (r->diag == RD_FIXED)
        REFUSE(at, "%s", r->msg);
    if (r->diag != RD_MODULE && r->diag != RD_MODULE_OCTAL)
        BAD_ROW(at, "an escape");

    /* MOD-0.6 phase 2: \p/\P get a REFINED refusal (a malformed-vs-
     * unknown-name split with a load-bearing offset, measured against
     * libpcre2 — tests/probes/probe_uprops.c) instead of falling through to
     * the generic module-refusal text below. Keyed off POINTER IDENTITY on
     * `recognise`, mirroring GROUP_OPT's `pcrec_registry_option_run_recognise`
     * marker (mod_modifiers.c) rather than a hardcoded `c == 'p'` special
     * case, so the connection lives in the registry row, not here.
     * Position-invariant on purpose (mod_uprops.c's own header): still
     * ALWAYS refuses — no aport/cport wiring this phase (D33 §9.3's "nothing
     * that refuses today may start COMPILING"). */
    if (r->recognise == pcrec_registry_uprops_recognise)
        return pcrec_modport_uprops(cx, r, want, at, cx->pos);

    /* PCRE2 forbids some of these INSIDE a class and always will, so naming a
     * module there is the over-promise D26 calls a defect: module `assertions`
     * will implement `\A`, and will never implement `\A`-in-a-class, because
     * that is not a construct (error 107; 71 for `\N`). Ten rows carry the flag
     * — A B G K Z z C R X N — and it was found by a test writer reading the spec
     * with no sight of this file (R9/SPEC-classes-F1). The knowledge was already
     * HERE, in the `\N` row's own note, in a field no check reads.
     *
     * Distinct from RF_CLASS_BASE, where the doorway is never entered at all
     * (`[\b]` is backspace, base syntax). */
    if (in_class && (r->flags & RF_CLASS_INVALID))
        REFUSE(at, "\\%c is not valid inside a character class", c);

    /* THE PRODUCERS (MOD-0.3c, base ports MOD-0.3d). Position selects the
     * PORT — §14's per-port rule. A BASE port answers at the level the
     * caller ASKED (the gate never touches PCRE2 base facts); a module
     * port answers at the post-gate level, so WANT_RESULT there means the
     * gate is open. PORT_NONE falls through to the refusals below
     * unchanged. The doorway never moves cx->pos even when producing —
     * a result carries `end` and the CALLER advances (check06's rule). */
    {
        const ExtPort *p = in_class ? &r->cport : &r->aport;
        ExtWant w = p->base ? asked : want;
        if (w == WANT_RESULT && p->kind != PORT_NONE) {
            if (p->kind == PORT_SCALAR) {
                ExtResult res = { .what = EXT_SCALAR, .at = at, .msg = "",
                                  .answered_at = w };
                res.scalar = p->scalar;
                res.end = cx->pos;    /* the two-byte escape, already read */
                return res;
            }
            if (p->kind == PORT_FN)
                return p->fn(cx, r, w, at, cx->pos);
            /* PORT_SET */
            ExtResult res = { .what = in_class ? EXT_MEMBERS : EXT_NODE,
                              .at = at, .msg = "", .answered_at = w };
            res.node = pcrec_ast_class_from_bits(cx, p->set, p->scalar != 0);
            return res;
        }
    }

    if (in_class) {
        /* The K12 endpoint payload (§16.3(e), exercisable subset): certify
         * SET-shape only where the row's measured class_expect covers every
         * form that can reach it — the construct must BE its selector byte
         * (syntax "\X", length 2), which is the ten char-type escapes and
         * excludes every body-carrying row (\p{...} is "set 117" for the
         * probe form, but [0-\p{Foo}] is PCRE2 147, so the row cannot be
         * certified; see the ExtResult comment). */
        ExtResult res = { .what = EXT_REFUSAL, .at = at, .msg = "",
                          .answered_at = want };
        res.ep_set_certain = r->class_expect &&
                             strncmp(r->class_expect, "set ", 4) == 0 &&
                             r->syntax[0] == '\\' && r->syntax[1] != '\0' &&
                             r->syntax[2] == '\0';
        snprintf(res.msg, sizeof res.msg,
                 "\\%c in a class requires module '%s'", c, r->module);
        return res;
    }
    if (r->diag == RD_MODULE_OCTAL)
        REFUSE(at, "\\%c (backreference/octal) requires module '%s'",
               c, r->module);
    REFUSE(at, "\\%c requires module '%s'", c, r->module);
}

/* THE ELECTED-ROW WRAPPERS (MOD-0.7 slice 2, design note §5.3). Each public
 * doorway is a two-liner around the body above, stamping `res.row` on the ONE
 * return. The alternative — teaching the REFUSE macro to pick a
 * conventionally-named local out of its caller's scope — would stamp only the
 * refusal paths and silently miss the producing ones, and a `return` added
 * inside a doorway later would inherit whatever the macro happened to see.
 * `--explain` is the only reader; parse.c's six call sites are unchanged and
 * every rendered diagnostic is byte-identical (measured: 876 compile cells,
 * tests/reject's 470 checks, the .rxt corpus). */
ExtResult pcrec_ext_escape(Ctx *cx, ExtWant want, int c, bool in_class,
                           size_t at)
{
    const RegRow *elected = NULL;
    ExtResult res = esc_answer(cx, want, c, in_class, at, &elected);
    res.row = elected;
    return res;
}

/* ---- doorway 2: after '(?' ----------------------------------------------
 * `c2` is the byte after the '?', or -1 when the pattern ends there. That -1 is
 * also REG_SEL_ANY's value, so the lookup lands on the catch-all row twice
 * over — once as an exact selector match, once as the fallback. It is the same
 * row and the same diagnostic either way, and parse.c printed '?' for the
 * missing byte, which is reproduced below. */
static ExtResult group_answer(Ctx *cx, ExtWant want, int c2, size_t at,
                              const RegRow **elected)
{
    /* cx->pos is at the '?'; c2 is the byte after it; so the tail starts two
     * past the cursor. When the pattern ends at the '?' that is already beyond
     * patlen and tail_at reports avail = 0. */
    size_t avail;
    bool amb = false;
    const char *tl = tail_at(cx, cx->pos + 2, &avail);
    const RegRow *r = pcrec_registry_arbitrate(RK_GROUP, c2, tl, avail, &amb);
    *elected = r;   /* MOD-0.7 slice 2 */
    int shown = c2 < 0 ? '?' : c2;
    want = pcrec_ext_gate(r, want);

    /* Only reachable by deleting the catch-all row, which tests/registry's
     * hand-written manifest also refuses; a NULL deref is not an acceptable
     * second answer to that. */
    if (!r) REFUSE(at, "internal error: no registry row for (?%c", shown);
    /* The MOD-0.2 ambiguity defect — see the escape doorway's comment. */
    if (amb)
        REFUSE(at, "internal error: ambiguous registry arbitration for a (? construct");

    /* The pattern ENDS at `(?` (R17 engine finding, fixed at disposition).
     * c2 == -1 aliases REG_SEL_ANY, so the natural lookup lands on the
     * catch-all's "unrecognized character" answer — the 111 family, a claim
     * PCRE2 does not make here: `(`, `(?`, `(?i`, `(?^` and `(?-` are ALL
     * error 114, "missing closing parenthesis" (measured, probe cells in
     * docs/reviews/2026-08-12-r17-mod05.md) — an UNCLOSED GROUP, the same
     * answer bare `(` gets, not an unrecognisable byte. So answer in the
     * family pcrec already uses for bare `(`, in both gate states (this is
     * base-family truth, not module truth). The Q2-era pin asserting the
     * old answer carried prose claiming PCRE2 agreement; the measurement
     * says otherwise, and the pin moved with this fix.
     *
     * AND IT ANSWERS WITHOUT A ROW (R20/MOD07-4), so the stamp is cleared.
     * The lookup above landed on the catch-all only because c2 == -1 aliases
     * REG_SEL_ANY — an accident of the sentinel, not an arbitration — and
     * this branch then walks past whatever it found. Leaving the stamp made
     * `--explain '(?'` print `live elected (?q)` and tag that row's block
     * `fallback`, both asserting an election that never happened. NULL is
     * what `ExtResult.row` promises here. */
    if (c2 < 0) {
        *elected = NULL;
        REFUSE(at, "missing closing ) for group");
    }

    if (r->diag == RD_FIXED)
        REFUSE(at, "%s", r->msg);
    if (r->diag != RD_MODULE)
        BAD_ROW(at, "a (? construct");

    /* AN OPTION SETTING IS A RUN, NOT A BYTE (Q2). Splitting the old catch-all
     * into eleven letter rows fixed `(?q)` and left `(?iZ)` — PCRE2 error 111 —
     * still being promised module 'modifiers', because the row was chosen by the
     * first byte and nothing read the rest. Reading the run is what makes this
     * doorway's answer depend on the whole construct, exactly as Q1 made the
     * `(*` doorway depend on the whole name.
     *
     * The run starts AT the selector byte (`(?i-m:` has the run "i-m"), so this
     * asks about cx->pos + 1 rather than the tail position used above. On
     * failure the answer is the doorway's own catch-all row, so the rejection
     * has ONE home: rewording it there changes it here too, and a second copy of
     * PCRE2's sentence is exactly the drift this registry exists to prevent.
     *
     * RF_OPTION_RUN retired at MOD-0.5b: this branch now keys off `r->recognise`
     * — a GROUP_OPT row's identity, not a bit — rather than a flag. The
     * recogniser itself is a MARKER (mod_modifiers.c's own comment says why:
     * the real check needs the selector byte, one position earlier than a
     * recogniser's `at` conventionally means, and reconstructing that from
     * `at` is unsafe against the synthetic buffers registry_check.c's
     * arbitration sweeps call it with). So the real check still lives here,
     * unchanged, with the real Ctx. */
    if (r->recognise == pcrec_registry_option_run_recognise) {
        size_t oavail;
        const char *orun = tail_at(cx, cx->pos + 1, &oavail);
        if (!pcrec_registry_option_run_ok(orun, oavail)) {
            const RegRow *any = pcrec_registry_find(RK_GROUP, REG_SEL_ANY, NULL, 0);
            if (!any || any->diag != RD_FIXED)
                BAD_ROW(at, "the (? doorway's catch-all");
            REFUSE(at, "%s", any->msg);
        }
        /* THE PRODUCER (MOD-0.5c). Post-gate WANT_RESULT means module
         * `modifiers` is enabled; the run is recognised (which INCLUDES the
         * recognised-malformed err-194 shapes — diagnosing them is the
         * module's job, D28's SYN_MALFORMED half). The port parses the run
         * from the SELECTOR byte (cx->pos + 1 — the same position the check
         * above asked about), applies or refuses per letter, and returns the
         * construct's node with `end` past its `)`; the cursor stays here
         * (check06) and p_group_body advances. */
        if (want == WANT_RESULT && r->aport.kind == PORT_FN)
            return r->aport.fn(cx, r, want, at, cx->pos + 1);
    }
    /* K14 (design §17.2): a ROADMAP_NEVER row is real PCRE2 syntax pcrec
     * deliberately excludes, and promising its module is the defect D26's
     * tier-2 row names. The module stays on the row as classification; it is
     * just never rendered as a promise. */
    if (r->roadmap == ROADMAP_NEVER)
        REFUSE(at, "(?%c...) is outside pcrec's scope and no module will implement it (see docs/pcre2_compliance.md)", shown);
    REFUSE(at, "(?%c...) requires module '%s'", shown, r->module);
}

ExtResult pcrec_ext_group(Ctx *cx, ExtWant want, int c2, size_t at)
{
    const RegRow *elected = NULL;
    ExtResult res = group_answer(cx, want, c2, at, &elected);
    res.row = elected;
    return res;
}

/* ---- doorway 3: after '(*' ----------------------------------------------
 * Moved to src/parse/mod_verbs.c at MOD-0.4 (the migration test): the whole
 * `pcrec_ext_verb` function, together with the VerbName tables it reads and
 * their four accessors. It keeps this file's exact signature — declared in
 * internal.h, called unchanged from parse.c — and reuses `pcrec_ext_gate`
 * and `REFUSE`/`BAD_ROW` from this file/internal.h rather than duplicating
 * them; see mod_verbs.c's header for why the move needed no new port or
 * recognise-pointer wiring despite moving the whole doorway function out. */

/* ---- doorway 4: after '[' inside a class --------------------------------
 * The only doorway that can decline. `[` is an ordinary class member most of
 * the time, so this returns false to mean "no construct here, carry on" — and
 * for the delimiter-pair constructs it returns false far more often than it
 * fails, because PCRE2 only reads `[.` as a collating element when the matching
 * `.]` appears later. `[[.]`, `[a[.b]` and `[.]` all compile.
 *
 * `at` is the offset to report, `from` the offset just past the delimiter, and
 * `at_class_open` says whether the CLASS's own bracket is acting as the opener
 * (`[.a.]`) rather than a bracket inside it (`[[.a.]]`). That distinction is
 * not decoration: `[.a.]` is an error at offset 0 while `[:alpha:]` is a
 * perfectly ordinary class of five characters, pinned against libpcre2 10.46.
 * RF_CLASS_DELIM is what separates them — see its definition in internal.h. */
/* pcrec_ext_class_pair_opens — K4's scan as a predicate — MOVED to scans.c
 * (MOD-0.1 slice 9) with the K4 three-rule scan itself: extent scans are the
 * always-live half of recognition and live in a TU that never links the
 * enabled-set symbol (check01's nm contract). This file keeps the SEAM: row
 * choice, the gate, and the terminal answer. */

static ExtResult clsbracket_answer(Ctx *cx, ExtWant want, int c2, size_t at,
                                   size_t from, bool at_class_open,
                                   bool at_content_start,
                                   const RegRow **elected)
{
    /* No `if (c2 < 0)` guard: it was here, and it was redundant rather than
     * defensive. `find(RK_CLASSBRACKET, -1)` returns NULL because this kind has
     * no catch-all row — which registry_check.c now REQUIRES of it, since a
     * catch-all would turn every unmatched byte in a class into a construct. So
     * the end-of-pattern case is handled one line below, by the check that
     * handles every other unrecognised byte. */
    const RegRow *r = pcrec_registry_find(RK_CLASSBRACKET, c2, NULL, 0);
    *elected = r;   /* MOD-0.7 slice 2; NULL on the decline below */
    if (!r) DECLINE();
    want = pcrec_ext_gate(r, want);

    /* K4, fixed 2026-08-10 (FIX-2): the three-rule delimiter-pair scan, which
     * used to run to the end of the PATTERN rather than the end of the CLASS
     * (`[a[.b]c]d.]` was the sharpest repro). The scan itself now lives in
     * scans.c (MOD-0.1 slice 9 — always-live extent scans in their own TU,
     * check01's nm contract) WITH its rule documentation and the four
     * measured pin patterns; what this call site keeps is the outcome
     * mapping: a pair that never closes is a DECLINE either way (rule 2's
     * nested-opener return was measured behaviourally identical to rule 1's
     * break over 1,239,480 patterns, R9/C2, so the two collapse here).
     *
     * `close_at` starts at `from`, not 0, so that a row reaching the
     * RF_CLASS_NAMED check below without having run the scan asks about a
     * ZERO-length name rather than about `0 - from`, which wraps to a huge
     * size_t. No shipped row does that (the one RF_CLASS_NAMED row also
     * carries RF_CLASS_DELIM, and registry_check.c requires that pairing) —
     * two guards, because the coupling that made the wrap memory-safe was
     * accidental (R9/C3-1). */
    size_t close_at = from;              /* index of the closing delimiter */
    if (r->flags & RF_CLASS_DELIM) {
        if (!pcrec_class_delim_extent_scan(cx->pat, cx->patlen, c2, from,
                                           &close_at)) {
            /* R20/MOD07-4: this DECLINE answers without a row, so clear the
             * stamp the lookup left. A pair that never closes is not this
             * construct — `[[.]`, `[a[.b]` and `[.]` are ordinary classes —
             * and reporting the row the scan just rejected made
             * `--explain '[[:alpha]'` say `live elected [[:alpha:]]` beside
             * `declines — no construct at this doorway`. The `!r` decline
             * above already yields NULL because the lookup itself found
             * nothing; this is the same contract, one branch later. */
            *elected = NULL;
            DECLINE();
        }
    }

    /* The `else if (at_class_open) return;` that stood here is GONE, and its
     * removal is K3's fix rather than a tidy-up: it was what kept `[:alpha:]`
     * compiling, because the `:` row was the only one without RF_CLASS_DELIM
     * and so the only one that reached it. All three rows carry the flag now,
     * which made the branch unreachable as well as wrong.
     *
     * R5's sabotage battery found K3 by observing that deleting that branch
     * changed 0 of 4173 emission cases and broke no test — an invisible branch
     * with a real divergence behind it. `at_class_open` survives, but it is no
     * longer invisible: it now SELECTS THE MESSAGE, and tests/reject/ pins both. */
    if (r->diag != RD_FIXED)
        BAD_ROW(at, "a [ construct in a class");

    /* POSITION FIRST, then the name — which is libpcre2's own order, measured:
     * `[:foo:]` is "POSIX named classes are supported only within a class" at
     * offset 0, NOT "unknown POSIX class name". The construct is in the wrong
     * place, so whether its name is real never comes up. */
    if (at_class_open && r->open_msg)
        REFUSE(at, "%s", r->open_msg);

    /* A name outside the known set is not this construct at all, so naming a
     * module for it would be the over-promise this flag exists to remove:
     * `[[:foo:]]` is an error libpcre2 will never accept, and module 'classes'
     * cannot make it one. See RF_CLASS_NAMED in internal.h. */
    if ((r->flags & RF_CLASS_NAMED) &&
        !pcrec_registry_posix_known(cx->pat + from, close_at - from))
        REFUSE(at, "%s", pcrec_registry_posix_unknown_msg());

    /* A REAL name in a position libpcre2 will not take is still not a construct
     * (R9/C3-4). `<` and `>` are word-boundary assertions rather than classes,
     * and libpcre2 recognises them only as a class's ENTIRE content — so
     * `[[:<:]]` compiles while `[x[:<:]]`, `[^[:<:]]` and `[[:<:]a]` are all
     * "unknown POSIX class name". Answering "requires module 'classes'" for
     * those is the over-promise this row exists to remove, surviving for the
     * two names FIX-2 itself added.
     *
     * Entire content means: nothing before it (`at_content_start`, which is
     * false after any member and false when a `^` negated the class) and the
     * class's `]` immediately after the construct's own. */
    if ((r->flags & RF_CLASS_NAMED) &&
        pcrec_registry_posix_whole_class_only(cx->pat + from, close_at - from) &&
        !(at_content_start && close_at + 2 < cx->patlen && cx->pat[close_at + 2] == ']'))
        REFUSE(at, "%s", pcrec_registry_posix_unknown_msg());

    /* A whole-class-only name in its ONE legal position is still not a class:
     * `[[:<:]]` is a zero-width word-boundary assertion, and the honest
     * promise is the module that owns assertions, not this doorway's
     * (MOD-0.3a — the posix_names[] comment reserved this split for whoever
     * implemented the doorway). Decided by the NAME's own module field, so a
     * future name in someone else's module renders itself with no edit here.
     * Negated spellings never reach this: `^`-prefixed names fail
     * posix_find, and a negated whole-class-only name already refused as
     * unknown above. */
    if (r->flags & RF_CLASS_NAMED) {
        const PosixName *pn = pcrec_registry_posix_find(cx->pat + from,
                                                        close_at - from);
        if (pn && strcmp(pn->module, r->module) != 0)
            REFUSE(at, "[[:%s:]] is a word-boundary assertion and requires "
                       "module '%s'", pn->name, pn->module);
    }

    /* THE PRODUCER (MOD-0.3c): post-gate WANT_RESULT and the row carries a
     * class port. Every own-error check above declined first — the pair
     * closes, the name is known, and it is not a whole-class-only assertion
     * name — so the port's only job is name -> set -> members. PORT_FN
     * because a NAME is not a fixed set per row (the `:` row is one row for
     * fourteen names and both polarities). The caller consumes res.node and
     * advances to res.end; the doorway leaves cx->pos alone. */
    if (want == WANT_RESULT && r->cport.kind == PORT_FN)
        return r->cport.fn(cx, r, want, at, from);

    /* The final refusal — reached only after every own-error check above
     * declined to fire, so for the `:` row this is a KNOWN POSIX name in a
     * legal position: certifiably SET-shaped for the K12 endpoint rule (the
     * collating rows' class_expect is "err 113", never certified). `end` is
     * where a low endpoint's range dash would sit. */
    {
        ExtResult res = { .what = EXT_REFUSAL, .at = at, .msg = "",
                          .answered_at = want };
        res.ep_set_certain = r->class_expect &&
                             strncmp(r->class_expect, "set ", 4) == 0;
        res.end = close_at + 2;
        snprintf(res.msg, sizeof res.msg, "%s", r->msg);
        return res;
    }
}

ExtResult pcrec_ext_class_bracket(Ctx *cx, ExtWant want, int c2, size_t at,
                                  size_t from, bool at_class_open,
                                  bool at_content_start)
{
    const RegRow *elected = NULL;
    ExtResult res = clsbracket_answer(cx, want, c2, at, from, at_class_open,
                                      at_content_start, &elected);
    res.row = elected;
    return res;
}
