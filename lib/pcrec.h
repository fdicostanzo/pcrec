/* pcrec — PCRE-to-C regex compiler: public library API.
 * Compile a pattern to specialized C source; the generated code has no
 * dependency on this library. */
#ifndef PCREC_H
#define PCREC_H

#include <stddef.h>
#include <stdint.h>

enum {
    PCREC_ENC_ASCII = 0,   /* byte semantics, 8-bit clean */
    PCREC_ENC_UTF8  = 1    /* not yet implemented (module 'utf8', M5) */
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
    PCREC_NO_CAPTURES = 1u << 2   /* --no-captures (D42.1) */
};

/* [M4.5b] (docs/design/engine_m4.md §5.6): the per-pattern engine override.
 * AUTO is APPROACH §2's "automatic per pattern"; the other two are diagnostic
 * (reproduce a bug, measure the hybrid against VM-only) and REFUSE cleanly
 * rather than falling back silently. PCREC_ENGINE_VM additionally DISABLES
 * the DFA prefilter (D44/R21 E-6), which is what makes it an independent
 * second derivation of the match span rather than an echo of the DFA's. */
enum {
    PCREC_ENGINE_AUTO = 0,
    PCREC_ENGINE_DFA  = 1,
    PCREC_ENGINE_VM   = 2
};

/* [M4.5b] `step_budget`'s sentinels (engine_m4.md §4.6). The default is a
 * BRING-UP PLACEHOLDER: D12 rules that budgets come from measured medians and
 * [M4.6] is where the measurement happens. */
enum {
    PCREC_STEP_BUDGET_DEFAULT = 0,   /* emit the placeholder default */
    PCREC_STEP_BUDGET_NONE    = -1   /* --fno-step-budget: emit no counter */
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
 * Searches s[startpos..n) and returns 1 on a match, 0 on no match.
 * `caps` may be NULL (existence-only search, today's entire caller
 * population). On a match, if caps != NULL, RX_NCAPS pairs are written as
 * half-open [start, end) byte offsets; caps[0] IS the whole-match span (no
 * second name for it). On no match, caps (if non-NULL) is left UNTOUCHED —
 * the int return value alone communicates match/no-match. startpos > n
 * returns 0. `^` anchors to absolute offset 0 regardless of startpos. s may
 * be NULL only when n == 0. RX_NCAPS is 1 on every artifact this milestone
 * emits (a DFA-compiled matcher); RX_NCAPS > 1 implies the VM engine ([M4.5]).
 *
 * Every generated matcher also exports, unconditionally: `<prefix>_match`
 * (the `rx_matchfn`-typed match-here entry, anchored at `ctx->pos`, no
 * search loop, no capture output — a length or -1), `<prefix>_match_caps`
 * (the anchored capture-DELIVERING sibling: same anchoring, plus a
 * `caps_out` parameter), and `extern const rx_info <prefix>_info` (a static
 * reflection structure: option flags, encoding, pattern text, group counts,
 * selected engine, budgets). The fixed-literal ABI types these entries
 * share (`rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_group_entry`,
 * `rx_info`, `rx_renderfn`) are declared in the generated .c/.h, not here —
 * they are PER-ARTIFACT-EMITTED, not part of pcrec's own library surface,
 * exactly like `<prefix>_search` itself. See docs/design/match_api_m4.md.
 *
 * The one-shot search form above is the WHOLE generated search contract
 * today. The streaming interface APPROACH.md §6 specifies (<prefix>_stream_init/
 * feed/end) is not emitted yet: it arrives with milestone M3, whose design gate
 * (docs/dev/plan.md, M3.0) owns reconciling that contract with the two-pass
 * engine before any streaming code is written. */

void pcrec_output_free(pcrec_output *out);

#endif /* PCREC_H */
