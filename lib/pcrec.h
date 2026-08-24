/* pcrec — PCRE-to-C regex compiler: public library API.
 * Compile a pattern to specialized C source; the generated code has no
 * dependency on this library. */
#ifndef PCREC_H
#define PCREC_H

#include <stddef.h>
#include <stdint.h>

/* [M5-SEAM] (D58, 2026-08-18) THE ENCODING NAMESPACE. Exactly one encoding
 * per COMPILE CALL — a `pcrec_options` field, never process- or file-global,
 * so mixed encodings in one compilation unit or binary are supported by
 * construction (self-contained artifacts, distinct prefixes, each embedding
 * exactly one encoding's residual block; DD-12 (8)).
 *
 * `PCREC_ENC_BYTE` was spelled `PCREC_ENC_ASCII` before [M5-SEAM], and the
 * CLI spelled it `-e ascii`. RENAMED, not aliased (pre-v1, docs/spec/
 * match_api.md §9's announced-boundary form): the semantics were always
 * "every byte is a character, 8-bit clean" — bytes >= 0x80 are ordinary
 * bytes with no case and no meaning, which is precisely NOT what "ASCII"
 * says — and D58 names the encoding `byte` in the ruling text itself. Two
 * names for one namespace member is [SR-10]'s motivating defect, so there
 * is no compatibility alias: `-e ascii` is now an unknown encoding. */
enum {
    PCREC_ENC_BYTE = 0,   /* byte semantics, 8-bit clean; the default */
    PCREC_ENC_UTF8 = 1    /* not yet implemented (arrives with milestone M5) */
};

/* [M4.4] (D43.2/D44.8): pcrec's own boolean options, one bit each in
 * pcrec_options.flags. `PCREC_CASELESS` parallels PCRE2_CASELESS (RULED
 * D44.8: not PCREC_CASE_INSENSITIVE) so a caller porting from PCRE2
 * recognises it on sight; `PCREC_EMIT_MAIN` and `PCREC_NO_CAPTURES` have no
 * PCRE2 equivalent. `PCREC_NO_CAPTURES` is RESERVED here (D42.1's
 * captures-default axis is M4.5-era) — no CLI flag or compile-time behavior
 * sets or reads it yet; the bit exists so a caller's code compiled against
 * this header does not need revisiting when M4.5 wires it.
 *
 * [M4.5b] PCREC_NO_CAPTURES is now LIVE (D42.1: captures are ON by default;
 * this bit recovers the pre-M4.5 pure-DFA artifact, RX_NCAPS 1). */
enum {
    PCREC_CASELESS    = 1u << 0,  /* was pcrec_options.caseless */
    PCREC_EMIT_MAIN   = 1u << 1,  /* was pcrec_options.emit_main */
    PCREC_NO_CAPTURES = 1u << 2,  /* --no-captures (D42.1) */
    /* [M4.5c] (DD-8, engine_m4.md S10): emit an INSTRUMENTED matcher that
     * prints every resume-frame push/pop and capture write to stderr as it
     * runs. A GENERATION AXIS like every other option here (D18) — the
     * instrumentation is compiled in, not switched at run time — and never
     * the default: a traced artifact writes to stderr, which is not something
     * a shipped matcher should ever do. The artifact stamps that it is
     * traced, so no one has to guess. VM artifacts only; a DFA matcher has
     * no resume frames to trace. */
    PCREC_TRACE       = 1u << 3,
    /* [ENG-BREP] `-fno-possessify`: DENY the possessification rewrite
     * (docs/design/eng_brep_design.md §2, D47.3).
     *
     * A TESTING AND TUNING AXIS, not a user feature. Possessification changes
     * no answer — that is its entire claim — so the only reason to turn it off
     * is to CHECK that claim: the row's primary instrument is a
     * pcrec-vs-pcrec differential that compiles the same pattern twice, once
     * with the rewrite and once without, and compares spans, every capture
     * slot and the failure surface. A strategy that cannot be denied cannot be
     * differentially tested.
     *
     * DENY rather than FORCE, and D47.3 rules the difference load-bearing:
     * each quantifier walks its own ladder skipping the denied steps, so a
     * denial composes per-quantifier with no need to ADDRESS one quantifier
     * inside a pattern. It is the first member of a family — the rest of the
     * ladder's denials (`-fno-counter`, a rung selector, a value parameter for
     * K) arrive with the strategies they deny. */
    PCREC_NO_POSSESSIFY = 1u << 4,
    /* [ENG-BREP] `-fno-revdet`: DENY the REVERSE-DETERMINISTIC rung
     * (docs/design/engine_m4.md §2.5, D47.3), the second member of the family
     * the bit above opened.
     *
     * Same shape and same reasons. The rung changes no answer — a quantifier
     * emitted as one body copy plus a backward walk matches exactly what the
     * same quantifier replicated `n` times matches — so the only reason to turn
     * it off is to CHECK that claim, and the check is a pcrec-vs-pcrec
     * differential in which the DENIED build falls one rung to frames, i.e. to
     * literal replication, i.e. to the semantic ground truth
     * (eng_brep_design.md §5.1). A strategy that cannot be denied cannot be
     * differentially tested.
     *
     * DENY rather than FORCE, so it composes per quantifier with no need to
     * ADDRESS one quantifier inside a pattern: each walks its own ladder
     * skipping the denied rungs. Denying this one drops a qualifying
     * quantifier to frames; denying it does not, and must not, deny
     * possessification, which is an orthogonal modifier at every rung. */
    PCREC_NO_REVDET     = 1u << 5,
    /* [ENG-BREP] `-fno-counter`: DENY the COUNTER rung
     * (docs/design/counterk_impl/counterk_design.md), the THIRD member of the
     * family, and the one whose denial is load-bearing beyond testing.
     *
     * Same shape and same reasons as the two above. What is specific to it:
     * denying the rung drops a bounded repeat to VM_RUNG_FRAMES_BOUNDED, which
     * for a bounded repeat is LITERAL REPLICATION — N copies of the body, which
     * is exactly what ships today and is therefore the semantic GROUND TRUTH
     * the differential compares against (§8.1). So this flag is not merely how
     * the rung is tested; it is what makes the ground truth reachable at all,
     * the same role `-fno-revdet` plays one rung up.
     *
     * That ground truth has a KNOWN LIMIT, and it is this rung's own endgame:
     * above the replication cap there is no `-fno-counter` build to compare
     * against, because the cap is what refuses it. §8.1's differential is blind
     * there by construction, and §8.5 cell 1 covers that region by the oracle
     * sweep and by the strategy's own N-independence instead. */
    PCREC_NO_COUNTER    = 1u << 6,
    /* [M4.6d] `-fno-length-prune`: DENY MINIMUM-REMAINING-LENGTH pruning
     * (docs/design/k23_impl/k23_design.md, D51 ruling 1), the family's FOURTH
     * member and D46's controllability half for this optimization.
     *
     * Same shape and same reasons as the three above, with one difference
     * worth stating: MRL is not a RUNG, it is a bound emitted ON whichever
     * rung a quantifier already took, so denying it changes no rung, no slot
     * and no capacity — an artifact built with it is byte-for-byte the one
     * pcrec emitted before MRL existed. That is what makes the denial the
     * ground truth of the differential: the same corpus, the same subjects,
     * pruned against unpruned, byte-identical answers expected on every
     * capture slot (§7.4's pcrec-vs-pcrec instrument). */
    PCREC_NO_LENGTH_PRUNE = 1u << 7,
    /* [M4.6f] `-fno-prefilter`/`-fprefilter`: the D46 close-out for the
     * PREFILTER axis (docs/design/engine_m4.md §6.1/§4.7, D46/D47.3).
     *
     * A DIFFERENT SHAPE from the four bits above, and deliberately so.
     * Those deny a per-QUANTIFIER strategy, which is why D47.3 rules DENY
     * (not FORCE) the right spelling for them — each quantifier walks its
     * own ladder skipping a denied step, so "force possessify on THIS
     * quantifier" has no addressing problem to solve because there is
     * nothing to address. `fit.prefilter` (src/opt/select_engine.c) is not
     * per-quantifier; it is ONE verdict for the whole artifact, decided
     * jointly with `--engine`: auto+captures turns it on, `--engine=vm`
     * turns it off (R21 E-6) as a SIDE EFFECT of choosing the engine, with
     * no way to ask for the combination independently. D46's own
     * motivating scenario is exactly this coupling: a test built to pin
     * one axis silently moves on another. So this is a FORCE PAIR, not a
     * deny-only flag — both directions are independently reachable, which
     * is what decouples "which engine" from "does the hybrid prefilter
     * run ahead of it".
     *
     * DO-OR-DIE (D47.3's posture) rather than a silent downgrade:
     * `PCREC_FORCE_PREFILTER` on a pattern that compiles to the DFA engine
     * (no VM artifact exists to attach a prefilter to) REFUSES, the same
     * `--engine`-precedent shape as the DFA/VM engine conflicts in
     * src/opt/select_engine.c's own switch. `PCREC_NO_PREFILTER` is always
     * buildable — `--engine=vm` already ships that exact configuration
     * today — so it never refuses.
     *
     * Same masked-out-of-`rx_info.flags` treatment as the four bits above
     * and for the identical reason (src/gen/emit_dfa.c's emit_info_def):
     * the prefilter changes no answer, only how one is found (§6.1's
     * exactness claim), so two identically-behaving artifacts must not
     * differ in their reflection surface over a knob with no observable
     * effect. What the axis DOES is recorded in `<PREFIX>_VM_PREFILTER`
     * (src/gen/emit_vm.c), which reports what the emitter did rather than
     * what it was asked — the D46 half a denied-or-forced request can be
     * checked against. */
    PCREC_NO_PREFILTER    = 1u << 8,
    PCREC_FORCE_PREFILTER = 1u << 9,
    /* [OPT-ALTCLS] `-fno-altcls-merge`/`-fno-altcls-factor`: D46's
     * controllability half for the ALTERNATION->CLASS NORMALIZATION pass
     * (docs/dev/plan.md's [OPT-ALTCLS] row, src/opt/altcls.c).
     *
     * BACK TO D47.3's DENY-ONLY SHAPE, not `_PREFILTER`'s force pair — and
     * for the family's original reason, not the prefilter's exception to
     * it. Each mergeable/factorable alternation RUN in the pattern is its
     * own selection point, addressed independently the way each A_REP
     * walks its own possessify/revdet ladder; there is no single
     * artifact-wide verdict the way `fit.prefilter` is one, so FORCE has
     * no addressing problem to solve because (as with possessify/revdet)
     * there is nothing to force — a run that cannot merge/factor always
     * DECLINES, safely, the same as an A_REP that cannot possessify.
     *
     * TWO BITS, not one, because the two stages are independently useful
     * to pin: stage 1 (single-char runs -> one class) and stage 2 (prefix
     * factoring, emitting no new capturing groups) are different rewrites
     * with different soundness arguments, and stage 2 runs on stage 1's
     * OUTPUT (docs/dev/plan.md's interaction note), so denying stage 1
     * alone still lets stage 2 factor an all-single-char run's literal
     * spelling, while denying stage 2 alone leaves single-char merging
     * live. A differential that wants ONLY one stage held constant needs
     * both knobs separately reachable.
     *
     * Same masked-out-of-`rx_info.flags` treatment as the deny family
     * above and for the identical reason (src/gen/emit_dfa.c's
     * emit_info_def): the pass changes no answer, only the emitted shape,
     * so two identically-behaving artifacts must not differ in their
     * reflection surface over a knob with no observable effect. What the
     * pass DID is recorded in `<PREFIX>_ALTCLS_MERGES`/
     * `<PREFIX>_ALTCLS_FACTORED` (pcrec_emit_prologue, shared by both
     * emitters since this pass runs before either engine is built,
     * unlike the VM-only possessify/revdet stamps) — the D46 half a
     * denied request can be checked against. */
    PCREC_NO_ALTCLS_MERGE  = 1u << 10,
    PCREC_NO_ALTCLS_FACTOR = 1u << 11,
    /* [M6.4.2] `-fno-atomic-discharge`: DENY the FREE DISCHARGE
     * (docs/design/atomic_groups_design.md §5.3; src/opt/atomic.c).
     *
     * The discharge deletes an `A_ATOMIC` whose cut possessify's §2.2 verdict
     * proves is a NO-OP. Like every other member of this family it changes no
     * ANSWER — that is its entire claim — so the only reason to turn it off is
     * to CHECK that claim, with a pcrec-vs-pcrec differential that compiles the
     * same pattern twice and compares spans, every capture slot and the failure
     * surface. A rewrite that cannot be denied cannot be differentially tested.
     *
     * WHAT IT DENIES IS AN ENGINE, NOT A STRATEGY, and that is the one way it
     * differs from the five above. Every other `-fno-` here leaves the same
     * artifact kind and changes the machinery inside it; denying THIS one
     * leaves the `A_ATOMIC` in the tree, so SR-8's consultation sees a
     * DFA-excluding node and the pattern compiles to the VM where it would have
     * compiled to a pure DFA. `--engine=dfa -fno-atomic-discharge '[^"]*+"'`
     * therefore REFUSES, which is correct and is the flag doing its job.
     *
     * IT IS SEPARATE FROM `-fno-possessify` DELIBERATELY. The discharge is NOT
     * gated by that flag (src/opt/select_engine.c drives it unconditionally),
     * because an OPTIMISATION denial must not decide which engine a pattern
     * gets. Folding the two together would have made `-fno-possessify` do
     * exactly that. */
    PCREC_NO_ATOMIC_DISCHARGE = 1u << 12
};

/* [ENG-BREP] the counter rung's UNROLL FACTOR, K (counterk_design.md §4.1;
 * eng_brep_design.md §4.5's "K must not become a per-pattern heuristic in v1",
 * held strictly by D47's ADDENDUM). ONE per-artifact constant: every
 * quantifier in a pattern unrolls by the same K, with no per-quantifier
 * variation of any kind. The downward clamp that would have varied it moved
 * whole to plan row [ENG-CLAMP].
 *
 * A TUNING AXIS, and the value parameter of the deny flag above. K = 0 means
 * the built-in default (PCREC_DEFAULT_UNROLL_K, D47.2). */
enum {
    PCREC_UNROLL_K_DEFAULT = 0
};

/* [M4.5b] (docs/design/engine_m4.md §5.6): the per-pattern engine override.
 * AUTO is APPROACH §2's "automatic per pattern"; the other two are diagnostic
 * (reproduce a bug, measure the hybrid against VM-only) and REFUSE cleanly
 * rather than falling back silently. PCREC_ENGINE_VM additionally DISABLES
 * the DFA prefilter (D44/R21 E-6), which is what makes it an independent
 * second derivation of the match span rather than an echo of the DFA's. */
enum {
    PCREC_ENGINE_AUTO = 0
};

/* [ABI-NS] (D60 addendum, 2026-08-18): PCREC_ENGINE_DFA/PCREC_ENGINE_VM are
 * `#define`d here, NOT `enum` members like PCREC_ENGINE_AUTO above, and that
 * is a forced choice, not a style pick. Every generated artifact ALSO emits
 * `#define PCREC_ENGINE_DFA 1` / `#define PCREC_ENGINE_VM 2` (its
 * PCREC_RX_ABI_H block, src/gen/emit_dfa.c) naming `rx_info.engine`'s
 * contract, byte-identical to the two lines below on purpose — an artifact
 * must stay self-contained (no dependency on pcrec.h, top-level CLAUDE.md),
 * so it cannot simply reference this header's spelling. A consumer TU that
 * includes BOTH this header and a generated artifact's header therefore sees
 * the SAME name declared twice; two identical `#define`s of one name are a
 * silent no-op redefinition (measured: no diagnostic under
 * `-Wall -Wextra -Werror`), regardless of which file is included first. An
 * `enum` member here would NOT be safe the same way: `#define PCREC_ENGINE_DFA
 * 1` from an artifact's header, included BEFORE this one, textually rewrites
 * this file's own `PCREC_ENGINE_DFA = 1,` enumerator to `1 = 1,` -- a hard
 * compile error, verified directly. Keep these two byte-identical to
 * emit_dfa.c's emission if either side's spelling ever needs to change. */
#define PCREC_ENGINE_DFA 1
#define PCREC_ENGINE_VM  2

/* [M4.5b] `step_budget`'s sentinels (engine_m4.md §4.6). The default is a
 * BRING-UP PLACEHOLDER: D12 rules that budgets come from measured medians and
 * [M4.6] is where the measurement happens. */
enum {
    PCREC_STEP_BUDGET_DEFAULT = 0,   /* emit the placeholder default */
    PCREC_STEP_BUDGET_NONE    = -1   /* --fno-step-budget: emit no counter */
};

/* [ENG-BREP counter-K] `work_budget`'s sentinels, the same shape as the pair
 * above (D47 SECOND ADDENDUM settlement 4; default ruled at D49). The THIRD
 * bound: per-iteration forward work the fail label never sees — frames
 * discarded at a cut, and iterations of a frameless scan. A step is still one
 * backtrack resumption and this counter never touches it.
 *
 * There is deliberately NO `--fno-work-budget`: v1 rides ONE existence gate,
 * so `--fno-step-budget` suppresses both counters (D49's manager-accepted
 * conventions). That keeps tests/vm/run_vm_tests.sh's no-counter pin true as
 * written, and splitting the gate later is purely additive. `_NONE` exists
 * anyway because it is what that single gate SETS this field to. */
enum {
    PCREC_WORK_BUDGET_DEFAULT = 0,   /* emit the placeholder default */
    PCREC_WORK_BUDGET_NONE    = -1   /* no work counter (rides --fno-step-budget) */
};

typedef struct {
    const char *prefix;      /* C identifier prefix for generated symbols; default "rx" */
    int         encoding;    /* PCREC_ENC_* */
    uint64_t    flags;       /* PCREC_CASELESS | PCREC_EMIT_MAIN | ... (D43.2/D44.8,
                                 [M4.4]: BREAKS the prior separate `caseless`/`emit_main`
                                 int fields into bits of one word — one representation of
                                 each boolean fact end to end, CLI parse through this field
                                 through the generated rx_info.flags, §5 match_api_m4.md).
                                 PCREC_CASELESS: match case-insensitively (ASCII letters
                                 only — Unicode folding is module 'utf8', M5). Compiled
                                 AWAY into the automaton's byte classes: the generated code
                                 carries no flag, no branch and no case conversion, and its
                                 entry point has the same signature either way (D18). That
                                 zero-cost claim is scoped to the ASCII tier's constructs:
                                 backreferences under (?i) (module 'backrefs', and the M4 VM
                                 before them) compare captured SUBJECT text at run time and
                                 are where it gets re-examined (D23).
                                 PCREC_EMIT_MAIN: append a standalone main() to the .c. */
    const char *header_name; /* name used in the generated #include "...";
                                NULL = self-contained .c (declarations inlined,
                                h_src not produced) */
    int         engine;      /* [M4.5b] PCREC_ENGINE_* (default AUTO) */
    int64_t     step_budget; /* [M4.5b] backtrack resumptions the emitted VM
                                 will spend before returning <PREFIX>_ERR_STEPS;
                                 PCREC_STEP_BUDGET_DEFAULT / _NONE. A GENERATION
                                 AXIS, not a runtime parameter (D18) — and the
                                 only shape the frozen rx_matchfn signature
                                 leaves open (engine_m4.md §4.6). Ignored on a
                                 DFA artifact, which cannot backtrack. */
    int64_t     work_budget; /* [ENG-BREP counter-K] work units the emitted VM
                                 will spend on forward work the fail label does
                                 not see before returning <PREFIX>_ERR_WORK;
                                 PCREC_WORK_BUDGET_DEFAULT / _NONE. A GENERATION
                                 AXIS like step_budget, and a SEPARATE counter
                                 from it (D47 SECOND ADDENDUM settlement 4):
                                 one unit per frame discarded at a cut, one per
                                 frameless scan iteration. Ignored on a DFA
                                 artifact, which does neither. */
    int         unroll_k;    /* [ENG-BREP] the counter rung's unroll factor K:
                                 one emitted body copy per K iterations.
                                 PCREC_UNROLL_K_DEFAULT (0) = the built-in
                                 PCREC_DEFAULT_UNROLL_K. A TUNING AXIS; one
                                 value per artifact, never per quantifier
                                 (D47 ADDENDUM). Ignored on a DFA artifact and
                                 wherever the counter rung is not selected. */
    int         frame_capacity; /* [M4.5b] <PREFIX>_BT_FRAMES, the resume-stack
                                 capacity (engine_m4.md §4.5's SECOND bound);
                                 0 = let the compiler size it (exactly, where
                                 the pattern's dynamic depth is statically
                                 bounded; the default otherwise). */
} pcrec_options;

/* [M4.4] (subst note §9 Q8, D42.4): which input string pcrec_error.pos
 * indexes into. pcrec_compile()'s error path always sets
 * PCREC_ERR_INPUT_PATTERN today — it has no other input yet; the
 * substitution-template compiler ([M4-SUBST], not yet built) is the first
 * producer of PCREC_ERR_INPUT_TEMPLATE. */
typedef enum {
    PCREC_ERR_INPUT_PATTERN  = 0,
    PCREC_ERR_INPUT_TEMPLATE = 1
} pcrec_err_input;

typedef struct {
    char            msg[256];  /* human-readable diagnostic */
    size_t          pos;       /* byte offset into the input named by `input`,
                                   when applicable */
    pcrec_err_input input;     /* which input string `pos` indexes into */
} pcrec_error;

typedef struct {
    char *c_src;      /* malloc'd; free with pcrec_output_free */
    char *h_src;      /* malloc'd or NULL when options.header_name == NULL */
} pcrec_output;

void pcrec_default_options(pcrec_options *opt);

/* Returns 0 on success (out filled), -1 on failure (err filled if non-NULL). */
int pcrec_compile(const char *pattern, const pcrec_options *opt,
                  pcrec_output *out, pcrec_error *err);

/* Generated searcher contract, RESHAPED at [M4.4] (D44.2, docs/design/
 * match_api_m4.md §1.0) — the prior `<prefix>_span` out-struct form is
 * RETIRED, with no compatibility alias, in favor of a caps-array parameter
 * that is already the FINAL shape (RX_NCAPS simply grows from 1 upward at
 * [M4.5] with no further signature change):
 *
 *   int <prefix>_search(const unsigned char *s, size_t n, size_t startpos,
 *                        ptrdiff_t (*caps)[2]);
 *
 * Searches s[startpos..n) and returns 1 on a match, 0 on no match, or a
 * NEGATIVE typed give-up code when the engine ran out of budget: the
 * artifact's `<PREFIX>_ERR_STEPS`/`_FRAMES`/`_WORK`/`_RECURSE`, all inside
 * [`<PREFIX>_ERR_FLOOR`, -2] (D49; the same code space `<prefix>_match`
 * and `<prefix>_match_caps` return, docs/spec/match_api.md §4).
 * [DD-14 wave A, D71 item 1] `_RECURSE` is RESERVED, no producer today —
 * the recursion-depth counter is a future diagnostic-generation axis, not
 * part of the default artifact.
 * The return is therefore NOT two-valued: `if (<prefix>_search(...))` treats a give-up
 * as a match, and a caller that must not do that tests `== 1` (or `> 0`)
 * for "matched" and `< 0` for "gave up". Values strictly below the floor
 * are reserved for a future abort semantic.
 * [DD-14 wave A commit 2, D71 item 1] `<PREFIX>_ERR_INTERNAL`, below the
 * floor, is that semantic's first producer: it means the artifact caught
 * its OWN analysis/emission inconsistency, never a resource give-up
 * (module 'lookaround''s negative-polarity lookbehind end-check is the
 * one producer today). This entry PROPAGATES it exactly like a give-up
 * rather than trapping on it — trapping is what a COMPOSED call site
 * (one `rx_matchfn` invoking another) must do, not a top-level entry.
 * `caps` may be NULL (existence-only search, today's entire caller
 * population). On a match, if caps != NULL, RX_NCAPS pairs are written as
 * half-open [start, end) byte offsets; caps[0] IS the whole-match span (no
 * second name for it). On no match — and on a give-up, which is a failure
 * for this rule too — caps (if non-NULL) is left UNTOUCHED; the int return
 * value alone communicates the outcome. startpos > n returns 0. `^` anchors
 * to absolute offset 0 regardless of startpos. s may be NULL only when
 * n == 0, and the matcher never reads s[n]. RX_NCAPS is 1 on any
 * DFA-compiled artifact (which is every artifact built `--no-captures`);
 * RX_NCAPS > 1 implies the VM engine ([M4.5], where captures became the
 * default).
 *
 * Every generated matcher also exports, unconditionally: `<prefix>_match`
 * (the `rx_matchfn`-typed match-here entry, anchored at `ctx->pos`, no
 * search loop, no capture output — a length, -1, or a give-up code from
 * the same space as above), `<prefix>_match_caps`
 * (the anchored capture-DELIVERING sibling: same anchoring and same return
 * space, plus a `caps_out` parameter),
 * `extern const struct rx_info <prefix>_info` (a static
 * reflection structure: option flags, encoding, pattern text, group counts,
 * selected engine, budgets), and — since [M5-SEAM] (D58) —
 * `size_t <prefix>_next_pos(const unsigned char *s, size_t n, size_t pos)`,
 * the ENCODING RESIDUAL: the next CHARACTER boundary strictly after `pos`,
 * every position >= n counting as a boundary. It is the ONE place an
 * artifact's byte-vs-character distinction lives, and it is what a find-all
 * loop advances through after a ZERO-LENGTH match (docs/spec/match_api.md
 * §3.1 writes that loop out and §3.1.1 states this entry's contract). Under
 * the byte encoding its body is `pos + 1`; a UTF-8-compiled artifact
 * supplies a boundary-aware body under this same signature, so a caller's
 * loop is written once. Do NOT inline the `+ 1` back: that is the one edit
 * that makes a byte-compiled caller wrong against another encoding's
 * artifact. The fixed-literal ABI types these entries
 * share (`rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_renderfn`,
 * `rx_group_entry`, `struct rx_info`) are declared in the generated .c/.h,
 * not here — they are PER-ARTIFACT-EMITTED, not part of pcrec's own library
 * surface, exactly like `<prefix>_search` itself. The CONTRACT for all of
 * this — every entry point, the give-up codes, capture semantics, the
 * reflection surface — is docs/spec/match_api.md, which is authoritative;
 * docs/design/match_api_m4.md is the design record behind it.
 *
 * The one-shot search form above is the WHOLE generated search contract
 * today. The streaming interface APPROACH.md §6 specifies (<prefix>_stream_init/
 * feed/end) is not emitted yet: it arrives with milestone M3, whose design gate
 * (docs/dev/plan.md, M3.0) owns reconciling that contract with the two-pass
 * engine before any streaming code is written. */

void pcrec_output_free(pcrec_output *out);

#endif /* PCREC_H */
