/* Internal shared definitions for the pcrec compiler. Not installed. */
#ifndef PCREC_INTERNAL_H
#define PCREC_INTERNAL_H

#include <setjmp.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "pcrec.h"
/* Every number that decides what pcrec accepts, rejects or promises, with its
 * provenance — ours, PCRE2 syntax, or a PCRE2 internal (D26). */
#include "core/limits.h"

/* ---- arena allocator (all AST/IR memory; freed wholesale) ---- */

typedef struct ABlock {
    struct ABlock *next;
    size_t used, cap;
    char mem[];
} ABlock;

typedef struct { ABlock *head; } Arena;

void *arena_alloc(Arena *a, size_t sz);   /* zeroed, 16-aligned */
void  arena_free(Arena *a);

/* ---- growable string buffer (codegen output) ---- */

typedef struct { char *p; size_t len, cap; } StrBuf;

void  sb_putc(StrBuf *sb, char c);
void  sb_puts(StrBuf *sb, const char *s);
void  sb_printf(StrBuf *sb, const char *fmt, ...)
      __attribute__((format(printf, 2, 3)));
char *sb_take(StrBuf *sb);                /* transfer ownership, resets sb */
void  sb_free(StrBuf *sb);

/* ---- AST ---- */

typedef enum {
    A_CLASS,   /* byte class (literals normalized to singleton classes) */
    A_CAT,     /* l r */
    A_ALT,     /* l | r  (l is preferred branch) */
    A_REP,     /* l{rmin,rmax}, rmax == -1 for unbounded; greedy flag */
    A_EMPTY,   /* matches empty string */
    A_BOL,     /* ^ : start of subject */
    A_EOL,     /* $ : end of subject or before a final \n */
    /* [M4.5b] capturing group `(l)`, group number in `capno`.
     *
     * D31 ruled the group erasure STAYS, on a MEASURED compile-time cost, and
     * engine_m4.md §11.3 records that the VM nonetheless needs SOME node to
     * know where to emit a capture write. Both hold at once because this node
     * is BORN ONLY WHEN CAPTURES ARE REQUESTED (`Ctx.want_caps`, i.e. neither
     * --no-captures nor a capture-free pattern) and because every consumer
     * other than the VM emitter treats it as TRANSPARENT — see ast_bare() in
     * src/ir/nfa.c. So:
     *   - a capture-free pattern's AST is byte-identical to D31's, always;
     *   - `--no-captures` reproduces D31's AST for ANY pattern;
     *   - the prefilter NFA/DFA built for a capture pattern is the SAME
     *     machine the capture-ERASED pattern builds (engine_m4.md §6.1's
     *     STRUCTURAL erasure half, preserved by construction rather than by a
     *     second lowering — §11.3's "two lowerings from one parse" mitigation,
     *     obtained without copying the tree).
     * That is also what makes §5.4's byte-identity gate hold by construction
     * instead of by inspection. */
    A_CAP
} AKind;

typedef struct Ast Ast;
struct Ast {
    AKind    k;
    uint8_t  cls[32];       /* A_CLASS: 256-bit membership bitmap */
    Ast     *l, *r;
    int      rmin, rmax;
    int      capno;         /* A_CAP: 1-based capturing group number */
    bool     greedy;
    /* NOT A REPEATABLE ITEM (R20/SPEC-1). PCRE2 error 109's other half: a
     * quantifier after this node is an error rather than a repetition of it.
     * It cannot be derived from `k`, which is the whole reason it is a field
     * — a bare option run produces A_EMPTY, and A_EMPTY is ORDINARILY
     * quantifiable (`()*` and `(a|)*` both compile in libpcre2, measured).
     * The arena zeroes, so every node that does not say otherwise is
     * repeatable, which is the safe default.
     *
     * WHY IT IS NOT "produces no atom": the genuinely-lexical constructs
     * produce no atom either and are TRANSPARENT — libpcre2 compiles
     * `a\Q\E*` and `a(?#c)*`, letting the quantifier reach back to the `a`.
     * A bare option run does not: `a(?i)*` is err 109 at the quantifier.
     * That measured boundary is what this flag marks, and both sides of it
     * are pinned in tests/reject/. */
    bool     not_repeatable;
    /* [ENG-BREP] POSSESSIFIED (A_REP only). Set by src/opt/possessify.c when
     * the eng_brep_design.md §2.2 rule proves that no retreat into this loop
     * can ever produce a match the PREFERRED path does not, so the emitter
     * owes it no resume frames and no giveback.
     *
     * IT IS AN ANNOTATION, NOT A SPELLING. `a{2,4}` and a possessified
     * `a{2,4}` match the same strings by construction — that is the whole
     * claim — so every consumer other than src/gen/emit_vm.c ignores this
     * field, exactly as they ignore A_CAP. In particular src/ir/nfa.c lowers
     * A_REP by replication regardless (§2.8), which is why the prefilter DFA
     * is unchanged and why possessification is a run-time and emitted-size
     * win rather than a compiler-time one.
     *
     * The arena zeroes, so a node nothing analysed keeps its machinery — the
     * sound default, and the reason `-fno-possessify` is byte-identity-safe:
     * denying the pass leaves every node in the state it was born in. */
    bool     possessive;
    /* [ENG-BREP] REVERSE-DETERMINISTIC (A_REP only). Set by src/opt/revdet.c to
     * the body's REVERSED AST when engine_m4.md §2.5's rung applies, and left
     * NULL otherwise — so this one field is BOTH the verdict and the artifact
     * the emitter needs, and the three sites that must agree about the rung
     * (vm_cost_rep, vm_count_slots, vm_rep) read one field instead of each
     * re-deciding. Ast.possessive's precedent, one rung down.
     *
     * The reversed body is what the emitted backward walk matches: it recovers
     * the previous iteration boundary for a retreat and, per §3.4's corrected
     * derivation, the LAST iteration's captures. Reversal is A_CAT children
     * swapped, recursively; every other node kind reverses to itself.
     *
     * Same annotation-not-a-spelling rule as `possessive`: it changes the
     * emitted machinery and never what the quantifier matches, so every
     * consumer other than src/gen/emit_vm.c ignores it. The arena zeroes, so a
     * node nothing analysed keeps its machinery, which is what makes
     * `-fno-revdet` byte-identity-safe. */
    const Ast *revbody;
};

static inline void cls_set(uint8_t *b, unsigned c)      { b[c >> 3] |= (uint8_t)(1u << (c & 7)); }
static inline bool cls_has(const uint8_t *b, unsigned c){ return (b[c >> 3] >> (c & 7)) & 1u; }

/* ---- NFA (priority Thompson) ---- */

typedef enum {
    N_CLASS,   /* consume one byte in cls, goto t1 */
    N_SPLIT,   /* epsilon: try t1 first (higher priority), then t2 */
    N_EPS,     /* epsilon: goto t1 */
    N_BOT,     /* assert start of subject, goto t1 */
    N_EOL,     /* assert end-of-subject or before-final-\n, goto t1 */
    N_ACCEPT
} NKind;

typedef struct {
    NKind   k;
    uint8_t cls[32];
    int     t1, t2;
    uint8_t loop;        /* star/plus loop-entry split */
    uint8_t exit_is_t2;  /* which edge leaves the loop (greedy: t2) */
} NState;

typedef struct {
    NState *st;
    int     n, cap;
    int     start;
} Nfa;

/* ---- DFA (priority subset construction) ---- */

typedef struct {
    int     *list;     /* priority-ordered N_CLASS state ids (arena) */
    int      nlist;
    uint8_t  accept;   /* match ends here */
    int      eolvar;   /* EOL-variant state (the eol_ok=true closure of the same
                          pre-set: correctly priority-pruned accept + threads),
                          used at EOL positions; -1 = identical to this state */
    int     *tr;       /* [ncls] target dfa state or -1 = dead (arena) */
} DState;

typedef struct {
    DState  *st;       /* heap (realloc'd) */
    int      n, cap;
    int      ncls;     /* number of byte equivalence classes */
    uint8_t  clsmap[256];
    uint8_t  rep[256]; /* representative byte per class id */
    int      s0, s1;   /* start state at pos==0 / pos>0; -1 = dead */
    int      maxstates;/* engine-dependent cap (R1 A-3): table-mode machines
                          afford far more states than computed-goto ones */
    int     *tab;      /* hash table (heap) */
    size_t   tabcap;
} Dfa;

/* ---- compile context ---- */

/* engine selection (D7): assertion-free patterns use the O(n) unanchored
 * forward + reverse-DFA engine with table-driven emission; patterns with
 * ^/$ stay on the per-start attempt engine (computed goto) for now */
enum { PCREC_ENG_ATTEMPT, PCREC_ENG_UNANCH };

/* [M4.5b] engine_m4.md §5.1: selection's answer, computed by a PASS
 * (src/opt/select_engine.c) rather than by compile.c's old inline `if`.
 * `engines` uses the registry's own ENGM_* vocabulary (§5.1), which is what
 * makes SR-8 a consumption rather than a new schema. */
typedef struct {
    unsigned    engines;    /* ENGM_* mask: which engines CAN compile this */
    unsigned    chosen;     /* exactly one ENGM_* bit */
    const char *why;        /* the forcing construct, for the stamp and F7 */
    size_t      why_pos;    /* pattern offset of it */
    bool        prefilter;  /* §6: is a DFA prefilter emitted alongside */
} EngineFit;

typedef struct {
    /* heap-held so longjmp cleanup sees consistent pointers */
    Nfa    nfa;      /* forward NFA (unanchored-wrapped for ENG_UNANCH) */
    Nfa    rnfa;     /* reversed-pattern NFA (ENG_UNANCH only) */
    Dfa    dfa;      /* forward DFA */
    Dfa    rdfa;     /* reverse DFA, non-pruning (ENG_UNANCH only) */
    int    engine;   /* PCREC_ENG_*: which DFA SHAPE (unanch/attempt) */
    EngineFit fit;   /* [M4.5b] which ENGINE (dfa/vm), and why */
    StrBuf csb, hsb;
    /* [M4.5b] the VM emitter's scratch buffer for the matcher's BODY. It is
     * Job-owned rather than a local in pcrec_emit_vm for one reason: the body
     * must be produced BEFORE the text that precedes it (the class pool, the
     * cursor local, RX_NSTATE are all discovered by emitting), and any
     * ctx_fail during that emission longjmps out — a stack-local StrBuf would
     * leak its heap buffer on exactly the path the sanitizer battery checks. */
    StrBuf vmsb;
    /* [M4.5c] the emitted-program LISTING (DD-8, engine_m4.md S10), filled
     * only when Ctx.want_ir is set. Job-owned for vmsb's reason. */
    StrBuf irsb;
} Job;

typedef struct {
    Arena                arena;
    const char          *pat;
    size_t               patlen;
    size_t               pos;      /* parser cursor */
    int                  depth;    /* parser group-nesting depth (bounded) */
    /* SCOPED PARSE STATE (PARSE-1; widened to a struct at MOD-0.5c, the
     * D31-note's "expect a struct, not more bools"). Seeded from opt at parse
     * entry and saved/restored around every BODY-CARRYING group, because that
     * is where PCRE2 restores it: measured 17/17 against libpcre2 10.46,
     * `(?i)` set anywhere inside a group stays in force to the end of THAT
     * group — it leaks across sibling alternation branches, `(a(?i)b|c)d`
     * matching `Cd` — and is restored at the immediately-enclosing `)`, not
     * the outermost one. A top-level `(?i)` is never restored. A BARE option
     * run `(?i)` deliberately escapes its own paren pair's restore — it is an
     * option-setting construct spelled with parens, not a group with a body —
     * which is why the save/restore lives on p_group_body's body-parsing
     * tail, not unconditionally in p_group (the placement IS the scope rule).
     *
     * `opt` is const and caller-owned, so it CANNOT hold this: a module doing
     * D29's "set parse state, parse body, restore" has nothing to set.
     * Module `modifiers`' port (mod_modifiers.c) is the only writer.
     *
     * `(?^)` resets caseless/dotall/nocap/xlevel to the HARDWIRED defaults
     * below — measured, probe_mod05b.c: the reset is to-constant, not
     * to-`opt` (a `(?^)` under `-i` turns caseless OFF), and it does NOT
     * touch ungreedy (U and J both survive `(?^)`; "unset imnsx" is the
     * measured rule, not "unset everything"). */
    struct ModState {
        bool    caseless;   /* i — the OS-1/D23 fold, applied at class
                             * construction time (char_node/from_bits) */
        bool    dotall;     /* s — `.` keeps 0x0A instead of clearing it */
        /* m — `^`/`$` match at every newline rather than only at the subject
         * ends. NO WRITER TODAY: pcrec refuses `(?m)` and has no `-m`, so
         * this is false for every compile that reaches the analysis, and
         * module `assertions` is the writer that makes it live.
         *
         * It exists as a FIELD rather than as a comment because D47.5 rules
         * the `$`-follow exemption's gate a LIVE CHECK. eng_brep_design.md
         * §2.5 measures `$` in a quantifier's follow safe at 0/720 diverging
         * cells and UNSAFE at 180/720 under `(?m)` — the upward-closure
         * argument that makes `$` exempt ("no retreat can reach a position
         * satisfying `$` from further left") collapses per-line when `$` is
         * true before every newline. A comment saying "pcrec does not support
         * (?m) yet" is exactly the kind of fact that stops being true without
         * anyone revisiting the analysis; src/opt/possessify.c reads THIS,
         * and the module that lands `m` inherits the test obligation D47.5
         * attaches (a `(?m)` pattern whose `$`-follow quantifier must NOT
         * possessify). */
        bool    multiline;
        bool    ungreedy;   /* U — quantifier greed default inverted; a
                             * trailing `?` then RE-inverts. NOT reset by ^ */
        bool    nocap;      /* n — plain `(` stops counting as a capture */
        uint8_t xlevel;     /* 0 off / 1 `x` / 2 `xx` — consumed by the
                             * MOD-0.5d lexer; the state exists so one run
                             * parser owns every letter */
    }                    mods;
    /* THE RUNNING CAPTURE COUNT (MOD-0.1, design §18.1 as Frank resolved
     * it: there is NO scanner). Incremented at p_group_body's capturing-`(`
     * hook — group numbers are assigned by opening-paren order, so the
     * count AT a point in the parse is what PCRE2's multi-digit
     * octal-vs-backref rule consults (`\12` is a backreference iff the
     * RUNNING count >= 12, else octal; the TOTAL is irrelevant there). The
     * count at END of parse is the whole-pattern total, which is what
     * validates `\1`..`\9` — deferred resolution: module `backrefs` records
     * pending references and checks them against the final value, and its
     * pending list lands WITH that module (a list nothing can write is
     * unexercised structure, D33 §9.3 / D24's recorded loss — the judgment
     * is in the 2026-08-11 journal entry). Today the count feeds
     * `--count-groups`, the external channel tests/spec_mod0/check02
     * compares against libpcre2's CAPTURECOUNT and err-115 boundary. */
    unsigned             ncap;
    /* [M4.5b] Does this compile want capture OFFSETS out of the matcher?
     * engine_m4.md §5.3: the selection input is the requested OUTPUT, not the
     * presence of a `(`. Seeded from PCREC_NO_CAPTURES at compile entry and
     * read at exactly one place, p_group_body's capturing-`(` hook, which is
     * what makes "--no-captures reproduces today's AST" true by construction
     * rather than by a later erasure pass. Cleared for pcrec_count_groups and
     * the syntax-query surfaces, which never emit. */
    bool                 want_caps;
    /* [M4.5c] Produce the emitted-program listing alongside the artifact
     * (DD-8's `--emit-ir`). A QUERY, not a generation axis: it changes what
     * pcrec REPORTS, never a byte of what it emits — which is why it lives on
     * Ctx rather than in pcrec_options, and why the listing is rendered from
     * the emitter's own event stream instead of from a second walk. */
    bool                 want_ir;
    /* [ENG-BREP] the possessification pass's own census, set by
     * pcrec_possessify on every call (SET, not accumulated, so the fixpoint's
     * second round reports the final state rather than double-counting).
     * `poss_total` counts A_REP nodes in the SOURCE tree, which is the only
     * quantifier population comparable with eng_brep_design.md §2.6's — the
     * emitter's rung marks count a replicated body's copies once EACH, so a
     * census read off those measures replication as much as it measures
     * quantifiers. Reported in --emit-ir's header; nothing else reads it. */
    int                  poss_marked, poss_total;
    /* Pattern offset of the FIRST capturing `(`, or SIZE_MAX if none — the
     * engine_why stamp's `why_pos` (§5.5). */
    size_t               first_cap_pos;
    jmp_buf              jb;
    pcrec_error         *err;
    const pcrec_options *opt;
    Job                 *job;
} Ctx;

/* The scoped-state block above, nameable for save/restore locals. */
typedef struct ModState ModState;

/* PARSE-1: what `p_alt` reports about the alternation it just parsed.
 *
 * WHY THIS IS A STRUCT AND NOT AN `int`. The measured requirement is a branch
 * COUNT — conditionals are error 127 above 2 top-level branches and
 * `(?(DEFINE)` is error 154 above 1 — but `ctx_fail(cx, pos, ...)` takes a
 * POSITION as a required argument, so a module cannot RAISE that error with a
 * count alone. D26 puts pinning pcrec's own offsets against pcrec's own
 * convention in tier 2; only chasing PCRE2's specific number is tier 3. And a
 * per-branch position is not recoverable after the fact: `Ast` has no position
 * field of any kind, so a design that leaves the AST alone forecloses it
 * unless `p_alt` reports it. One `size_t` at the site that already touches
 * `cx->pos` costs the same as the count.
 *
 * `nbr` counts TOP-LEVEL branches, so it is 1 for an alternation-free body and
 * never 0. `last_bar` is the offset of the LAST `|` p_alt consumed, or
 * SIZE_MAX when there was none — the offending separator for a
 * "too many branches" diagnostic. */
typedef struct {
    int    nbr;
    size_t last_bar;
} AltInfo;

void ctx_fail(Ctx *cx, size_t pos, const char *fmt, ...)
     __attribute__((noreturn, format(printf, 3, 4)));

/* ---- syntax construct registry (D24 / SR-1) ----
 *
 * ONE declarative home per non-base construct. Before this table a single
 * construct's identity lived in up to five places (esc_modules[],
 * esc_char_value's switch, the (?X ternary chain, tests/reject/, the
 * compliance report); `\v` shipped wrong because the first two disagreed ten
 * lines apart with nothing enforcing that they agree.
 *
 * The table describes constructs OUTSIDE the base tier only. Base syntax
 * (literals, `.`, classes, quantifiers, `|`, `(...)`, `^`, `$`, and the plain
 * character escapes \n \t \r \f \a \e \xHH) stays in parse.c and never
 * consults the registry. MEASURED 2026-08-10 (R6): that makes the base tier
 * CHEAP, not lookup-free — `[abc]` costs one lookup at the class-bracket
 * doorway and three for a typical class-heavy pattern, while `(?:` costs zero
 * because parse.c answers it before the registry. SR-5 must guard the measured
 * property, not the claimed one.
 *
 * Rows are pure `static const` data. A runtime-mutable registry is rejected
 * because it would be file-scope mutable state in the compiler, which D19's
 * "usable FROM threads" property forbids. Note what actually guards that:
 * D19's COMPILER-side property is audited by hand, NOT mechanized — TS-1 scans
 * emitted output only and would not notice a mutable global added here.
 *
 * Per-compile SELECTION of flavour and feature mask is the DESIGN (D24), not
 * the present tense: pcrec_options carries no flavour or enablement field, and
 * nothing outside tests/registry/ reads the feature/flavour/engine columns. */

typedef enum {
    RK_ESC,           /* doorway 1: after '\'             — one byte decides */
    RK_GROUP,         /* doorway 2: after '(?'            — one byte decides */
    RK_VERB,          /* doorway 3: after '(*'            — a NAME decides   */
    RK_CLASSBRACKET,  /* doorway 4: after '[' in a class  — one byte decides */
    RK_COUNT
} RegKind;

/* Which module owns the construct. A mask, not an index: `(?<` is genuinely
 * two constructs sharing one byte (lookbehind and named group). */
enum {
    FEAT_CLASSES       = 1u << 0,
    FEAT_ASSERTIONS    = 1u << 1,
    FEAT_BACKREFS      = 1u << 2,
    FEAT_UNICODE_PROPS = 1u << 3,
    FEAT_QUOTING       = 1u << 4,
    FEAT_MISC          = 1u << 5,
    FEAT_LOOKAROUND    = 1u << 6,
    FEAT_NAMED_GROUPS  = 1u << 7,
    FEAT_ATOMIC_GROUPS = 1u << 8,
    FEAT_COMMENTS      = 1u << 9,
    FEAT_CALLOUTS      = 1u << 10,
    FEAT_BRANCH_RESET  = 1u << 11,
    FEAT_CONDITIONALS  = 1u << 12,
    FEAT_RECURSION     = 1u << 13,
    FEAT_MODIFIERS     = 1u << 14,
    FEAT_VERBS         = 1u << 15,
    /* MOD-0.3a (2026-08-12): `(?[...])` split out of `classes` the day the
     * classes producers began — an enabled module must never still refuse a
     * construct while naming itself, and set-operation classes are real
     * work `classes` does not contain. The registry row's own comment had
     * reserved this call for whoever implemented the doorway. */
    FEAT_EXTENDED_CLASSES = 1u << 16
};

/* Flavour: which construct a byte MEANS. Exactly one today, by design — D18's
 * earn-its-axis rule applied to the front end. SR-7 adds the rest; the column
 * exists now so a second flavour REBINDS A ROW instead of adding a branch
 * inside a handler. */
enum { FLAV_PCRE2 = 1u << 0 };

/* Engine capability: which engine the construct can LOWER to. NOT a parsing
 * question — `\1` parses fine and simply cannot become a DFA. NOTHING CONSUMES
 * THIS COLUMN YET; it turns on at SR-8, when M4's VM gives the parser a second
 * engine to choose between. Until then the values are recorded DESIGN INTENT,
 * not measured behaviour, and no test may assert on them beyond well-formedness. */
enum {
    ENGM_DFA = 1u << 0,   /* the shipped DFA engines (ENG_UNANCH, ENG_ATTEMPT) */
    ENGM_VM  = 1u << 1    /* the backtracking VM (M4, not built) */
};

typedef enum {
    RS_BASE,      /* implemented today, by the base grammar */
    RS_MODULE,    /* known and unimplemented; `module` names what would implement
                     it. A complete, tested outcome — not a stub */
    RS_REJECTED   /* PCRE2 rejects it too, so agreement IS compliance and there
                     is no module to name (POSIX collating elements) */
} RegStatus;

/* Which diagnostic the construct produces. Kept as data so SR-2's dispatch is
 * a mechanical substitution and byte-identity is provable. */
typedef enum {
    RD_NONE,          /* compiles; no diagnostic */
    RD_MODULE,        /* the doorway's template + `module` */
    RD_MODULE_OCTAL,  /* atom form only: "\N (backreference/octal) requires ..." */
    RD_FIXED          /* `msg`, verbatim */
} RegDiag;

/* K14 / D34 item 1 (design §17.2): a fact about pcrec's ROADMAP, orthogonal to
 * `status` (which is a fact about PCRE2). "requires module 'X'" renders ONLY
 * for ROADMAP_PLANNED; a ROADMAP_NEVER construct is real, refused, and names
 * NO module — these are exactly the constructs docs/pcre2_compliance.md marks
 * OUT-OF-SCOPE, and compliance_section.py asserts prose <=> column in BOTH
 * directions so the survey stays the independent home that caught K14 (the
 * one-source direction is CHECKED, not generated — R14/C2-F8).
 *
 * Zero is deliberately NOT a legal published value: it means "unset" on a
 * row registry_check requires to carry one, and "inherit the row's value" on
 * a VerbName. The legal pairings (registry_check enforces them): RS_BASE
 * rows carry ROADMAP_NONE (the question does not arise for supported
 * syntax); RS_MODULE rows carry PLANNED or NEVER; RS_REJECTED rows carry
 * NEVER (PCRE2 rejects it too, so there is nothing a module could ever
 * implement — the pairing is required, not a choice). */
typedef enum {
    ROADMAP_NONE = 0,
    ROADMAP_PLANNED,
    ROADMAP_NEVER
} Roadmap;

/* MOD-0.1 slice 2 (design §18.3 as ruled, plus SPEC-MOD0's findings A and C):
 * is the construct a legal quantifier target? Populated FROM libpcre2
 * (`a<syntax>*` per row — the sweep is /var-reproducible via
 * tests/spec_mod0/check10, whose oracle recomputes every verdict on every
 * run), never reasoned from documentation.
 *
 *   QF_YES      `a<syntax>*` compiles and the `*` quantifies the construct
 *   QF_NO       err 109 — a real construct that is not a quantifier target
 *               (-family assertions, (?C), bare option-settings... ) OR a
 *               construct PCRE2 rejects outright, whose quantified form
 *               cannot compile either
 *   QF_FORM     the row's FAMILY spans both verdicts and the row cannot say:
 *               option-run rows resolve bare-vs-`:body` in the producer, and
 *               the verb row resolves PER NAME (QV_* below) — `a(*ACCEPT)*`
 *               compiles while `a(*FAIL)*` is 109 with identical table forms
 *               (SPEC-MOD0 finding C)
 *   QF_LEXICAL  quantifying the syntax creates NO quantifier for the
 *               construct at all: `\E`/`(?#)` are transparent (the `*` binds
 *               the PRECEDING atom) and `\Q` literalises it (`a\Q*` compiles
 *               but the star is a literal — SPEC-MOD0 finding A: a bare
 *               "yes" there would be false)
 *   QF_NONE     unset; legal only on RS_BASE rows */
typedef enum {
    QF_NONE = 0,
    QF_YES,
    QF_NO,
    QF_FORM,
    QF_LEXICAL
} QuantFact;

/* The verb row's per-name resolution of QF_FORM. QV_NOT_ASKABLE: the
 * unquantified form itself does not compile (start-of-pattern-only options
 * away from position 0 have no askable cell), which is a THIRD outcome, not
 * a "no" — folding it into no would be wrong (SPEC-MOD0's sweep: 18 yes /
 * 6 no / 26 not-askable over the 50 names). */
typedef enum {
    QV_NOT_ASKABLE = 0,
    QV_YES,
    QV_NO
} QuantVerb;

enum {
    /* RF_CLASS_BASE (1u << 0) RETIRED at MOD-0.3d: "inside a class this
     * byte is BASE syntax" became the row's own BASE class port (ExtPort
     * .base + SCALAR/FN data — one home, and the value is oracle-tied by
     * check_class_ports where the flag was a bare assertion). The bit is
     * left unassigned so an old build's dump and a new one cannot alias. */

    /* A DELIMITER-PAIR construct: the selector byte opens it only when the
     * matching `<sel>]` appears later in the pattern, and the character class's
     * OWN opening bracket can serve as its `[`. Both halves are true of exactly
     * the POSIX collating rows and false of `[:...:]`, which is why one flag
     * carries them: `[.a.]` is an error at offset 0 while `[:alpha:]` is an
     * ordinary five-character class, and `[[.]` compiles because nothing closes
     * the pair. Measured against libpcre2 10.46, not inferred. If a third row
     * ever needs one half without the other, split the flag — the two
     * behaviours coincide here, they are not the same statement. */
    RF_CLASS_DELIM = 1u << 1,

    /* The text between the delimiters is a NAME from a known set, and a name
     * outside it is NOT this construct — PCRE2 says "unknown POSIX class name"
     * rather than routing it anywhere. Exactly one row carries this today
     * (`[[:alpha:]]`), and it is the class-bracket doorway's half of the same
     * over-promise Q1 removed at `(*`: without it pcrec answered "requires
     * module 'classes'" for all 12531 candidate names where libpcre2 has 14,
     * so its answer did not depend on the name at all (R8/C4-7). */
    RF_CLASS_NAMED = 1u << 2,

    /* PCRE2 forbids this construct INSIDE a character class, permanently — no
     * option, no version, no future in which `[\A]` means anything (error 107,
     * or 71 for `\N`). So the in-class doorway must NOT name a module for it:
     * module `assertions` will implement `\A`, and will never implement
     * `\A`-in-a-class, because that is not a construct. Same defect as
     * `(*NOTAVERB)` and `[[:foo:]]`, at the third doorway (R9/SPEC-classes-F1).
     *
     * Distinct from a BASE class port, which says the byte is BASE syntax in a class
     * and the doorway is never entered (`[\b]` is backspace). This says the
     * doorway IS entered and the answer is a refusal that promises nothing. */
    RF_CLASS_INVALID = 1u << 3,

    /* RF_OPTION_RUN (1u << 4) RETIRED at MOD-0.5b: it told ext.c "validate the
     * whole run before trusting this row" for the twelve GROUP_OPT rows. Since
     * MOD-0.2's recogniser+rank arbitration already asks each row a row-local
     * question and falls through to the kind's catch-all when a row declines,
     * the same fact now lives in the row's own `recognise` field —
     * pcrec_registry_option_run_recognise (src/parse/mod_modifiers.c), whose
     * own comment records why it is a MARKER rather than the check itself,
     * and see ext.c for where the real check moved (not far: the same call,
     * gated on identity instead of a bit). The bit is left unassigned so an
     * old build's dump and a new one cannot alias — the RF_CLASS_BASE
     * precedent above. */

    /* The LEXICAL row kind (MOD-0.1 slice 4, design §13.3): the construct is
     * a TOKENIZER MODE, not an atom — `\Q...\E` turns raw bytes into literal
     * character tokens, `\E` alone is the measured no-op, `(?#...)` is a
     * lexer discard. When built, it is built in the lexer; when ports land
     * (MOD-0.2+), a LEXICAL row has NO class port and NO AST port, and its
     * "producer" is the mode transition itself, gating like any producer:
     * disabled -> terminal at the token with the row's existing vocabulary.
     * Until then the three rows keep refusing with their exact strings
     * (byte-identity, §13.3) — this flag changes no behaviour today.
     *
     * MEMBERSHIP IS MEASURED, not asserted: §13.3(d)'s criterion is the same
     * fact the `quant` column carries as QF_LEXICAL, so registry_check
     * requires RF_LEXICAL <=> QF_LEXICAL in both directions and a fourth
     * lexical construct is FOUND (by check10's sweep) rather than assumed
     * away. NOT base grammar: base is never refused and never toggleable;
     * these rows are both (`--without=quoting` must refuse `\Q`). */
    RF_LEXICAL = 1u << 5
};

#define REG_SEL_ANY (-1)      /* catch-all row; last row for its kind */

/* src/parse/ext.c — the four doorways out of the base grammar (SR-2). Each is
 * called only after parse.c's own switch has declined, so a base-tier pattern
 * reaches none of them.
 *
 * THE CLAIM IS RETURNED, NOT RAISED (MOD-0.1, D33 §5 — the load-bearing
 * change). A doorway's terminal answer used to be a `ctx_fail`, which longjmps
 * past the caller; the three `noreturn` attributes that stood here were
 * today's truth and the design's obstacle, because a caller that never sees
 * the claim can never override it — the endpoint rule (D33 §6, K12) needs to
 * see "something claimed" BEFORE the construct's own diagnostic fires. So a
 * doorway now RETURNS an ExtResult and the caller passes it to
 * pcrec_ext_finish, the ONE epilogue that renders a refusal (one epilogue, so
 * D33 §8's "two missing doorway epilogues" cannot be missing). This also
 * retires K11's undefined behaviour: both escape call sites invoked a
 * value-flow through `noreturn` declarations, and a returning doorway
 * corrupted or crashed depending on register allocation; under the value
 * contract the flow is defined C at every site.
 *
 * THE PRODUCING VALUES EXIST SINCE MOD-0.3b AND NOTHING CONSTRUCTS THEM
 * YET: slice 1 lands the vocabulary and the port DATA unwired, so
 * EXT_SCALAR / EXT_MEMBERS / EXT_NODE are unreachable until the classes
 * producers wire in (slices 2-3), and pcrec_ext_finish's wall reports any
 * premature arrival as an internal error. D33 §9.3's obligation — every
 * EXT_* outcome carries a probe that is false the day before — is
 * discharged AT WIRING by the tests/classes/ corpus pins, written first and
 * watched failing (the FIX-3 pattern); until then the exercisable subset is
 * still refusals only, which byte-identity asserts. The call sites in
 * parse.c end in a loud internal-error wall after the epilogue, so a
 * producing port must extend the handling VISIBLY there rather than being
 * silently discarded (the PARSE-1 fallthrough defect, made structurally
 * impossible).
 *
 * "Returns normally" carries NO meaning on its own — the meaning is in the
 * VALUE, which is what keeps the two doorway contracts distinct (the concern
 * parse.c's PARSE-1 note records): the class-bracket doorway declines with
 * EXT_NOT_MINE and the cursor unchanged; the `(?` doorway can never decline
 * (its catch-all is REJECTED), so EXT_NOT_MINE from it is a registry defect
 * the wall reports. */
typedef enum {
    EXT_NOT_MINE = 0,   /* no construct here; cursor unchanged; caller
                           carries on. Only the class-bracket doorway can
                           produce it today. */
    EXT_REFUSAL,        /* a claim that terminates the compile: `msg`/`at`
                           carry the diagnostic, formatted AT CLAIM TIME so it
                           outlives the handler (D33 §5's representability
                           requirement), fired by pcrec_ext_finish. */
    /* The PRODUCING claims (D33 §5's full vocabulary, landed MOD-0.3b,
     * unconstructable until the classes producers wire in): */
    EXT_SCALAR,         /* one code point in `scalar` — the ONLY shape legal
                           as a range endpoint (D33 §6). `\b` in a class. */
    EXT_MEMBERS,        /* a byte-set the caller ORs into the class under
                           construction: `node` is an A_CLASS whose cls[]
                           holds the members. `[\d]`, `[[:alpha:]]`. */
    EXT_NODE            /* a finished subtree the caller splices in at atom
                           position: `\d` outside a class. */
} ExtWhat;

/* THE ASK CONTRACT (MOD-0.1, design §15/§18.2 as Frank ruled it): a doorway
 * is asked at one of three `want` levels, and there is NO `may` capability
 * axis — the fifth-session ruling collapsed it, with the revisit trigger
 * recorded: a terminal answer REQUIRED to depend on a full sub-parse while
 * its module is disabled reintroduces the axis.
 *
 *     WANT_CLAIM     is this yours, and what shape (consumer: arbitration)
 *     WANT_VERDICT   the right terminal answer, whatever it costs
 *     WANT_RESULT    the produced set/node
 *
 * THE CURSOR RULE, the load-bearing line: cx->pos moves ONLY under
 * WANT_RESULT. Below RESULT a doorway may inspect the pattern without limit
 * — the verb-name scan, the option run and the delimiter-pair scan are all
 * bounded row-local reads VERDICT is entitled to — but must leave cx->pos
 * byte-identical, and VERDICT never recurses into the pattern grammar.
 * tests/spec_mod0's check06 measures this over every registry row through
 * the CLI probe channel (`--probe-ask`), which reports the real cursor
 * before and after a single doorway call.
 *
 * THE GATE (§5.4/§15) demotes `want` by exactly one step — RESULT ->
 * VERDICT — for a row whose module is not enabled, and FLOORS at VERDICT: a
 * disabled module still owes its diagnostic, so nothing ever demotes to
 * CLAIM (silence where a message is owed). The enabled set is EMPTY today,
 * so every ask from parse.c (always WANT_RESULT — the real parse wants the
 * construct) is answered at VERDICT, which is why ExtResult's vocabulary is
 * all refusals. ext.c's demotion is unconditional for exactly that reason;
 * the enabled-set slice replaces it with the membership test (check07's
 * subject), and `pcrec_ext_class_pair_opens` below is the one ask that
 * bypasses `want` — it IS the CLAIM-shaped question as a predicate. */
typedef enum { WANT_CLAIM = 0, WANT_VERDICT, WANT_RESULT } ExtWant;

typedef struct RegRow RegRow;

typedef struct {
    ExtWhat what;
    size_t  at;         /* EXT_REFUSAL: offset the diagnostic points at */
    char    msg[256];   /* EXT_REFUSAL: the exact text; 256 matches
                           pcrec_error.msg, so deferring the format cannot
                           truncate differently than ctx_fail did */

    /* §16.3(e)'s verdict-shape payload, exercisable subset (the K12 endpoint
     * slice). TRUE only on a refusal for a construct pcrec can CERTIFY is
     * SET-shaped and PCRE2-accepted for EVERY form that reaches the row: the
     * ten char-type escapes (the construct IS its selector byte — syntax
     * "\X"; the measured class_expect covers all forms) and the bracket
     * doorway's KNOWN POSIX names (the 14-name table validated the body).
     * The range logic overrides such a refusal with PCRE2's verdict —
     * "invalid range in character class", err-150's analogue — at an
     * endpoint (§16's step 4). Body-dependent rows (\p, \N{U+}, ...) are
     * NEVER marked: pcrec cannot certify 150 for an arbitrary body
     * ([0-\p{Foo}] is PCRE2 147, not 150), so their module promise stands —
     * the deliberate boundary pinned in tests/reject/ and recorded in the
     * 2026-08-11 journal entry. */
    bool    ep_set_certain;
    /* class-bracket claims only: offset just past the construct's closing
     * "X]" — where a low endpoint's range dash would sit. */
    size_t  end;
    /* The level the ask was actually ANSWERED at, after the gate — the §5.4
     * demotion made observable (the probe channel prints it; nothing on the
     * compile path reads it, which byte-identity asserts). WANT_RESULT here
     * means THE GATE WAS OPEN — the row's module is in the enabled set
     * (slice 9); on a refusal it distinguishes "gate open, port missing"
     * (D33's NULL-port refusal) from "gate closed" (verdict-level demotion).
     * With the default empty enabled set it is never `result`, which cli
     * case10 pins. A decline is a claim-level answer (zero-init). */
    ExtWant answered_at;

    /* Production payloads (MOD-0.3b; read only for the matching `what`,
     * zero/NULL otherwise — designated initializers leave them so): */
    int     scalar;     /* EXT_SCALAR: the code point */
    Ast    *node;       /* EXT_MEMBERS: A_CLASS whose cls[] the caller ORs in;
                           EXT_NODE: the subtree the caller splices */

    /* THE ELECTED ROW (MOD-0.7 slice 2) — which row the doorway DISPATCHED
     * on. Nothing on the compile path reads it; `--explain` does, and cli
     * case11 asserts it per row.
     *
     * THE CONTRACT IS A BICONDITIONAL: **NULL if and only if the doorway
     * answered WITHOUT a row.** R20/MOD07-4 found the reverse direction false
     * in two of the three cases this comment already named, because both
     * failing paths STAMP AT LOOKUP and then answer somewhere the lookup's
     * result plays no part:
     *
     *   unknown escape              the lookup found nothing. NULL, always.
     *   class-bracket, no row       the lookup found nothing. NULL, always.
     *   class-bracket, pair never   a row WAS found and the delimiter scan
     *     closes                    then rejected it. Cleared at the DECLINE.
     *   `(?` at end of pattern      c2 == -1 aliases REG_SEL_ANY, so the
     *                               catch-all is found by an accident of the
     *                               sentinel and the branch walks past it.
     *                               Cleared in that branch.
     *
     * A path that answers without consulting the row must clear the stamp
     * where it answers, not rely on the lookup having failed. The two that
     * did not made `--explain` assert elections that never happened.
     *
     * IT IS NOT "THE ROW THAT WROTE THE MESSAGE", and the distinction is
     * measured rather than pedantic: for `(?iZ)` the elected row is the `i`
     * GROUP_OPT row while the text is the catch-all row's, because the
     * option-run grammar rejected the run (ext.c's option-run branch). Both
     * facts are true and `--explain` prints them as two fields.
     *
     * WHY IT EXISTS AT ALL, with the number: 13 registry rows share their
     * rendered atom diagnostic with a sibling in the same bucket (10 of the
     * `(?-N)` family, 3 of the `(?<` lookarounds), so a check comparing TEXT
     * — which is what registry_check's check_table_to_parser does — cannot
     * tell which of them answered. Identity can. See docs/design/design_notes_mod07.md
     * §5.3.
     *
     * STAMPED IN EXACTLY ONE PLACE PER DOORWAY: each public `pcrec_ext_*`
     * is a thin wrapper that calls the answering body with an out-parameter
     * and writes this field on the single return. A return added inside a
     * doorway later cannot forget it. */
    const RegRow *row;
} ExtResult;

/* A row's PRODUCING PORTS (design Part II §4/§14; D33 §5). One per position
 * — `aport` answers atom position, `cport` answers class position — because
 * the two positions of one construct genuinely differ in PCRE2 (\12 at 12
 * groups: backref at atom, octal in class — §14.1's measured table). The
 * KIND is the single home of "can this row produce here":
 *
 *   PORT_NONE    atom: the row refuses with its own diagnostic, exactly as
 *                every row does today.
 *                class: PERMANENTLY INVALID at class position — NULL's one
 *                meaning (§14.3, R14-verified mode-invariant). When the
 *                RF_CLASS_* flags retire (slice 3) this replaces them.
 *   PORT_SCALAR  one code point, as DATA: `\b` -> 0x08 (base scalar), and
 *                the literal fallbacks `\g \k \8 \9` -> their own letters
 *                (§14.3 — the K13 semantics, produced instead of asserted).
 *   PORT_SET     a 256-bit membership bitmap, as DATA (32 bytes): the ten
 *                char-type escapes and the POSIX names. Bitmaps are
 *                GENERATED from libpcre2 censuses, never hand-typed, and
 *                PC-4 re-measures them against the live oracle (the PC-3
 *                pattern; a libpcre2 version bump is a re-measurement
 *                event, D26 addendum).
 *   PORT_FN      a bounded row-local scan for shapes data cannot carry (the
 *                octal re-read `[\12]`, the POSIX name lookup): §18.2's
 *                VERDICT legality — may read its own body, never recurses
 *                into the pattern grammar. Signature is provisional until
 *                its first caller wires in (slice 2/3); the FIELD exists now
 *                so every macro initialises the whole port once.
 *
 * Ports are DATA about production; they carry no diagnostic and no module
 * fact (those stay on the row — R11/M5's rule that a handler must not be a
 * second home for tier-2 facts). */
typedef enum { PORT_NONE = 0, PORT_SCALAR, PORT_SET, PORT_FN } PortKind;

/* (`typedef struct RegRow RegRow;` moved ABOVE ExtResult at MOD-0.7 slice 2 —
 * ExtResult.row needs the name, and ExtResult is defined first.) */
typedef ExtResult (*ExtPortFn)(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from);

typedef struct {
    PortKind             kind;
    /* MOD-0.3d: TRUE for a port whose semantics are PCRE2 BASE FACTS the
     * gate must never touch — `\b`-in-class is backspace and `[\12]` is
     * octal WHATEVER is enabled (§14.3: "\b's class port is base (never
     * gated) and its AST port is 'assertions'" — the per-port feature
     * split that makes the C5 miscompile unrepresentable). A module's own
     * producing ports carry false and answer only through an open gate. */
    bool                 base;
    int                  scalar;  /* PORT_SCALAR: the code point.
                                     PORT_SET: the NEGATE flag — nonzero
                                     means the produced set is the exact
                                     256-bit complement of `set` (\D \S \W
                                     \H \V, and \N's not-newline). Only
                                     POSITIVE tables are stored; the
                                     complement law is asserted by the
                                     emitting probe for every pair. */
    const unsigned char *set;     /* PORT_SET: 32 bytes, bit b of set[b>>3] */
    ExtPortFn            fn;      /* PORT_FN */
} ExtPort;

#define NO_PORT { PORT_NONE, false, 0, NULL, NULL }

/* module `classes` (MOD-0.3c) — src/parse/mod_classes.c. The tables are
 * GENERATED from libpcre2 censuses by tests/probes/probe_cls_bits.c
 * (--emit writes src/parse/cls_bits.inc; the provenance header names the
 * version); PC-4 re-measures produced sets against the live oracle. */
extern const unsigned char pcrec_cls_digit_esc[32], pcrec_cls_space_esc[32],
    pcrec_cls_word_esc[32], pcrec_cls_hspace[32], pcrec_cls_vspace[32],
    pcrec_cls_newline[32],
    pcrec_cls_px_alnum[32], pcrec_cls_px_alpha[32], pcrec_cls_px_ascii[32],
    pcrec_cls_px_blank[32], pcrec_cls_px_cntrl[32], pcrec_cls_px_digit[32],
    pcrec_cls_px_graph[32], pcrec_cls_px_lower[32], pcrec_cls_px_print[32],
    pcrec_cls_px_punct[32], pcrec_cls_px_space[32], pcrec_cls_px_upper[32],
    pcrec_cls_px_word[32],  pcrec_cls_px_xdigit[32];
/* The GENERATED name->bits map for the POSIX named classes: emitted by
 * probe_cls_bits.c --emit as part of cls_bits.inc, so the PAIRING of a
 * name to its table is the same artifact as the measurement that produced
 * the table — never a hand-written line (R16's lower/upper swap lived in
 * exactly such a line; this deletes the species). posix_names[] in
 * registry.c stays the separate home of EXISTENCE and ATTRIBUTION (does
 * PCRE2 have the name; whose module is it), which PC-3 measures — two
 * different questions, two homes, one check tying their name sets. */
typedef struct {
    const char          *name;
    const unsigned char *bits;
} PcrecClsNamed;
extern const PcrecClsNamed pcrec_cls_posix_map[];
extern const size_t        pcrec_cls_posix_map_n;

/* The POSIX named-class producer (the `:` row's PORT_FN). */
ExtResult pcrec_clsport_posix(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from);
/* The octal class producer (MOD-0.3d) — the `\0`..`\7` rows' BASE PORT_FN,
 * in parse.c: base grammar's own rule migrated to the seam (FIX-3's measured
 * semantics — selector digit + up to two more octal digits, <= \377, PCRE2
 * err 151 above with the ran-out offset). */
ExtResult pcrec_clsport_octal(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from);
/* src/parse/parse.c — build an A_CLASS from a 32-byte membership bitmap,
 * applying the caseless fold BEFORE the optional negation (the OS-1/D23
 * order rule: both orders produce case-closed sets and only behaviour can
 * tell them apart — see cls_casefold's comment). The ONE constructor every
 * set-producing port uses, so the fold rule cannot be forgotten per site. */
Ast *pcrec_ast_node(Ctx *cx, AKind k);   /* bare-kind ctor for module TUs */
Ast *pcrec_ast_class_from_bits(Ctx *cx, const unsigned char bits[32],
                               bool negate);

/* Field groups are ordered identity / ownership / selection / outcome / doc.
 * `feature` and `module` are ADJACENT on purpose: they are two halves of one
 * fact, and registry.c's M_* macros emit them as a pair so a row cannot carry
 * a feature bit that disagrees with the module name it prints. */

struct RegRow {
    RegKind     kind;
    int         sel;       /* the deciding byte, or REG_SEL_ANY */
    /* The bytes that must FOLLOW `sel` for this row to apply, or NULL for "any"
     * (SR-9, docs/design/design_registry_selectors.md §7). Since MOD-0.2 the lookup
     * engine never interprets this field: it is the PARAMETER of
     * pcrec_recognise_tail_default — a row's recogniser answers when its tail
     * is a prefix of the text, and `rank` (below) elects among answering rows,
     * which is what makes a tailed row beat the same byte's tail-less fallback
     * and `\N{U+` beat `\N{`. SR-9's longest-tail-wins produced identical
     * answers over the whole probe space (261,193-probe scaffold + a
     * 5,247-comparison behavioural differential) and was retired.
     *
     * WHY A SECOND KEY RATHER THAN A STRING SELECTOR (§2, which R6 rejected with
     * measurements): one byte still decides the DOORWAY, and only a handful of
     * constructs need more. Making every selector a string would turn the
     * base-tier class lookup from 3 rows into ~31 and silently narrow the
     * 255-byte sweep; this keeps both exactly as they were.
     *
     * IT IS A LITERAL PREFIX, NOT A PATTERN. `(?-` followed by a digit is a
     * relative subroutine call and followed by a letter is an option setting,
     * so that construct needs ten rows ("0".."9") rather than one "\d" — which
     * is deliberate: a tail nobody has to interpret cannot be interpreted
     * wrongly, and the ten-row digit family is a shape this table already has
     * twice (`(?0)`..`(?9)` and `\0`..`\9`). */
    const char *tail;
    const char *syntax;    /* how it is written — also a valid probe pattern,
                              which is what lets the conformance test cover new
                              rows without being edited */

    unsigned    feature;   /* FEAT_* mask; 0 for RS_BASE/RS_REJECTED */
    const char *module;    /* module name AS IT APPEARS IN DIAGNOSTICS, or NULL */

    unsigned    flavours;  /* FLAV_* mask */
    unsigned    engines;   /* ENGM_* mask — design intent, unconsumed until SR-8 */

    RegStatus   status;
    RegDiag     diag;
    const char *msg;       /* RD_FIXED only, else NULL */
    /* The diagnostic when the CLASS'S OWN bracket is the opener (`[:alpha:]`
     * rather than `[[:alpha:]]`). NULL — every row but one — means the row
     * behaves identically in both positions.
     *
     * It exists because ONE row's outcome genuinely changes KIND with position,
     * measured against libpcre2 10.46: `[[:alpha:]]` is a POSIX class PCRE2
     * SUPPORTS, so pcrec owes "requires module 'classes'"; `[:alpha:]` is an
     * error PCRE2 will never accept, so promising a module there is a lie no
     * module can make true. The two collating rows do NOT need it — `[.a.]`
     * and `[[.a.]]` are both error 113, same text, both positions.
     *
     * This is a TIER 2 distinction under D26 (is a module promised?), not a
     * tier 3 one (what does the sentence say), which is why one extra field
     * buys it and a fifth doorway kind is not needed. */
    const char *open_msg;
    unsigned    flags;     /* RF_* */

    const char *note;      /* one-line PCRE2 semantics (SR-3/SR-4 render this) */

    /* LAST on purpose: every macro-built row initialises these explicitly,
     * and a longhand row that forgets one gets the zero value, which
     * registry_check flags on any non-base row rather than silently reading
     * as a claim. */
    Roadmap     roadmap;
    QuantFact   quant;

    /* MOD-0.1 slice 3 (design §14.4 as R14-corrected): the row's
     * CLASS-POSITION EXPECTATION — what `[<syntax>]` does under libpcre2,
     * two-valued and libpcre2-observable:
     *
     *   "err N"      the class does not compile; N is PCRE2's error number
     *   "char 0xNN"  it compiles and denotes exactly this one byte
     *   "set N"      it compiles and denotes N of the 256 byte values
     *
     * Populated FROM libpcre2 (tests/probes/probe_class_expect.c, 8-bit,
     * options = 0), cross-validated against the independent SPEC-MOD0
     * measurement, and re-verified against a live oracle run by
     * tests/spec_mod0/check04 — never reasoned from documentation.
     *
     * NULL on the 56 group/verb rows, and ONLY there: `(` inside a class is
     * an ordinary member, so those constructs cannot reach a class position
     * and a value would be an invented fact (§4.4's objection). The 41 esc
     * and 3 class-bracket rows must each carry one; registry_check enforces
     * both directions and the vocabulary. */
    const char *class_expect;

    /* MOD-0.2 (design §2.2 as adopted at D32 §§2-4, kept by Part II §14.4):
     * row SELECTION is recogniser + rank, not tail interpretation. Both
     * fields sit after the explicitly-initialised block and are ZERO-
     * DEFAULTED on purpose: 78 rows are alone in their bucket, and a
     * meaningful rank there would be an invented fact (D32 §3 — rank only
     * means anything between clashing recognisers).
     *
     * `rank` is a LOCAL TIEBREAK inside one (kind, sel) bucket, in three
     * tiers:
     *
     *     0   the bucket's fallback, and every row that never clashes
     *    25   a tailed row — beats the fallback; the single-byte tails
     *         within one bucket are mutually exclusive, so equal rank
     *         among them can never produce two ANSWERS
     *    70   the longer half of the table's one prefix-related tail pair
     *         (`\N{U+` over `\N{`) — the only place two tailed
     *         recognisers both answer
     *
     * The VALUES are arbitrary; only the ordering within a clashing set is
     * a fact. (R11 recovered D30's 0/25/40/70 draft mapping; the 40 tier is
     * deliberately not reproduced — `\N{` clashes only with the fallback
     * below it and `\N{U+` above it, so the tailed tier serves it.) Do not
     * add a global rank sweep as a permanent check: R11/M3 measured one
     * redundant with the per-row syntax check in all 5,632 probes. The
     * defect rank CAN carry — two answering rows at the winning rank — is
     * detected at dispatch (pcrec_registry_arbitrate) and floored as
     * exercised by registry_check's arbitration-liveness counter.
     *
     * `recognise` answers "is the text at the tail position my construct's
     * proper form?" — POSITIVE and LOCAL (D32 §2): it recognises its own
     * form and knows nothing about sibling rows (the bare `\N` row
     * answering "always" is CORRECT; elimination is rank's job). NULL
     * means pcrec_recognise_tail_default with this row's `tail` as its
     * parameter — after MOD-0.2 that default is the ONLY reader of `tail`
     * on the lookup path ("tail survives only as the parameter of a
     * tail_default recogniser"). The signature deliberately receives the
     * row's tail and NOTHING ELSE of the row (R11/M5): a recogniser that
     * could read its row would be a second, uncheckable home for tier-2
     * facts like the module name. */
    int  rank;
    bool (*recognise)(const char *at, size_t avail, const char *tail);

    /* MOD-0.3b: the two producing ports (full doc on ExtPort above). Every
     * macro initialises BOTH explicitly — -Wextra's missing-field-initializers
     * is the enforcement, the same property MOD-0.2 measured for rank and
     * recognise. Unwired in slice 1: nothing on the compile path reads them
     * until the classes producers land, which byte-identity asserts. */
    ExtPort aport;   /* atom position */
    ExtPort cport;   /* class position */
};

/* src/parse/registry.c */
const RegRow *pcrec_registry(RegKind k, size_t *n);
/* `at` points at the byte AFTER the doorway's selector byte and `avail` is how
 * many bytes remain there, so a row's `tail` can be compared without the caller
 * knowing any row exists. Passing avail = 0 asks the tail-less question and is
 * what a truncated pattern supplies — a row whose tail cannot fit does not
 * match, which is why `(?P` at end-of-pattern falls to the bare-`P` row rather
 * than reading past the end. */
const RegRow *pcrec_registry_find(RegKind k, int sel, const char *at, size_t avail);
/* The default recogniser (MOD-0.2): answers when `tail` is a prefix of
 * at[0..avail), and always when the row has no tail (the bucket's fallback —
 * D32 §2's "positive and local"). A NULL `at` is the tail-less question
 * exactly as it was under SR-9. */
bool pcrec_recognise_tail_default(const char *at, size_t avail, const char *tail);
/* Does this row's recogniser answer for the text? The engine's own dispatch
 * predicate, exposed so checks count answers with the same code the
 * arbitration runs — one source, no drift (R15). */
bool pcrec_registry_row_answers(const RegRow *r, const char *at, size_t avail);
/* The MOD-0.2 engine behind pcrec_registry_find: every sel-matching row's
 * recogniser runs, the highest-ranked ANSWERING row wins, and two answers at
 * the WINNING rank set *ambiguous — the D32 §2 defect, which the escape and
 * group doorways report as an internal error rather than resolving silently.
 * `ambiguous` may be NULL for callers that only want the row. */
const RegRow *pcrec_registry_arbitrate(RegKind k, int sel, const char *at,
                                       size_t avail, bool *ambiguous);

/* src/parse/mod_modifiers.c — module `modifiers` (MOD-0.5b), moved out of
 * registry.c WITH the measured grammar block that establishes it (the
 * probes-and-code-together rule; see the file's own header for why). */
/* Is `at[0..avail)` a valid PCRE2 inline option run — the text starting at the
 * byte after `(?`, up to and including its `)` or `:` terminator? The grammar
 * is measured against libpcre2; see mod_modifiers.c. */
bool pcrec_registry_option_run_ok(const char *at, size_t avail);
/* The twelve GROUP_OPT rows' `recognise` field (retires RF_OPTION_RUN). A
 * MARKER, not the check itself — always answers true, identically to the
 * tail-less default — so ext.c can key off `r->recognise == this pointer`
 * instead of a flag; see its own comment for why it does not run
 * pcrec_registry_option_run_ok directly. */
bool pcrec_registry_option_run_recognise(const char *at, size_t avail,
                                         const char *tail);
/* The twelve GROUP_OPT rows' atom-port producer (MOD-0.5c): parses the
 * validated run at `from` (the SELECTOR byte — the run includes it),
 * applies the per-letter deltas to cx->mods or refuses per letter, and for
 * the `:` terminator parses the body through pcrec_parse_body under the
 * new state. Returns EXT_NODE with `end` past the construct's `)`; the
 * cursor is returned UNMOVED (check06). Only called at a post-gate
 * WANT_RESULT on a run pcrec_registry_option_run_ok accepted — which
 * includes the RECOGNISED-MALFORMED runs (the err-194 shapes) this port
 * exists to diagnose. */
ExtResult pcrec_modport_optrun(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from);

/* src/parse/mod_uprops.c — module `unicode-props` (MOD-0.6 phase 2). No
 * producer: `\p`/`\P` always REFUSE, but with a REFINED, load-bearing-offset
 * split between "malformed shape" and "well-formed, unrecognised name" —
 * see the file's own header for the full account, docs/design/design_notes_mod06.md
 * for the design, and D33 §9's obligation this discharges (an EXT_* outcome
 * exists here only in the sense that the refusal text/offset changed;
 * SCALAR/MEMBERS/NODE remain unreachable for this module until a producer
 * lands, exactly as MOD-0.3b's own comment on ExtWhat describes). */
/* The `\p`/`\P` rows' `recognise` field — a MARKER, not the check itself
 * (mirrors pcrec_registry_option_run_recognise): both rows are alone in
 * their bucket, so this always answers true, identically to the tail-less
 * default. Its only purpose is POINTER IDENTITY: ext.c keys off
 * `r->recognise == pcrec_registry_uprops_recognise` to hand off to
 * pcrec_modport_uprops instead of the generic RD_MODULE fallback text. */
bool pcrec_registry_uprops_recognise(const char *at, size_t avail,
                                     const char *tail);
/* The \p/\P body scanner (see mod_uprops.c's header for the full algorithm
 * and its measured basis). Called DIRECTLY from pcrec_ext_escape — not
 * through r->aport/r->cport, which stay NO_PORT on both rows this phase —
 * keyed on the recogniser marker above. Always returns EXT_REFUSAL. */
ExtResult pcrec_modport_uprops(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from);

/* ---- doorway 3's NAME tables (Q1) --------------------------------------
 *
 * The other three doorways are decided by a BYTE and a RegRow can carry the
 * whole answer. `(*` is decided by a NAME, and until Q1 pcrec had no name
 * table at all: one catch-all row answered "requires module 'verbs'" for every
 * name, including names PCRE2 does not have. That was a live over-promise —
 * `(*NOTAVERB)` was told a module would implement it — and it made an external
 * name differential impossible, because pcrec's answer did not depend on the
 * name. See docs/dev/decisions.md D25.
 *
 * THESE ARE NOT RegRows, deliberately. A RegRow names a module, a feature bit,
 * an engine mask and a diagnostic template; fifty verb rows would repeat one
 * module fifty times and carry fifty hand-written notes nobody has measured —
 * the fiction SR-1 refused to write. A VerbName answers exactly one question,
 * "does PCRE2 have this name and in which forms", and EVERY BIT OF IT IS
 * VERIFIED against libpcre2 by tests/registry/pcre2_check.c (PC-3). Nothing
 * here is asserted; it is all recorded measurement.
 *
 * PCRE2 keeps TWO tables and picks between them by the CASE of the name's
 * first byte, with a different "not recognized" error for each. Measured
 * against libpcre2 10.46 with options = 0 (no PCRE2_UTF, no PCRE2_UCP):
 * `(*accept)` is error 195 and `(*Accept)` is error 160. */
enum {
    VF_BARE     = 1u << 0,  /* (*NAME)                                       */
    VF_ARG      = 1u << 1,  /* (*NAME:arg) with a non-empty arg              */
    VF_EMPTYARG = 1u << 2,  /* (*NAME:)                                      */
    VF_EQNUM    = 1u << 3,  /* (*NAME=digits), at least one digit            */

    /* The argument is a SUBPATTERN, not a name run, so the doorway does not
       require a `)` to be present: `(*pla:x` is PCRE2 error 114 "missing
       closing parenthesis" (the name WAS recognised) while `(*ACCEPT:x` is
       error 160 (it was not). One bit, two measured behaviours. */
    VF_GROUPARG = 1u << 4,

    /* Valid only at the very start of the pattern: `a(*CR)` is error 160.
       PCRE2 allows a RUN of these (`(*UTF)(*CR)` compiles); pcrec's rule is
       offset 0 exactly — see pcrec_ext_verb for why that is currently
       equivalent and what would change it. */
    VF_ATSTART  = 1u << 5
};

typedef struct {
    const char *name;      /* exact, case-sensitive                          */
    unsigned    forms;     /* VF_* mask: the forms libpcre2 ACCEPTS          */

    /* A form outside `forms` normally produces the table's generic "not
       recognized" message, because that is what PCRE2 produces. `(*MARK)` and
       `(*MARK:)` are the measured exception (error 166), so the row carries
       its own message and the mask of forms it applies to. Both NULL/0 for
       every other name. */
    unsigned    own_forms;
    const char *own_msg;

    /* ROADMAP_NONE = inherit the RK_VERB row's value (PLANNED — module
     * `verbs`). Set explicitly on the names the compliance survey marks
     * OUT-OF-SCOPE; disposition is a PER-NAME fact because RK_VERB is one
     * row for ~50 names spanning both values (design §17.2, R14/C2-F5:
     * `(*COMMIT)` is NEVER while `(*pla:...)` is a lookaround in verb
     * spelling). */
    Roadmap     roadmap;

    /* Meaningful only through the RK_VERB row's QF_FORM (see QuantFact). */
    QuantVerb   quant;
} VerbName;

typedef struct {
    const char     *unknown_msg;  /* PCRE2's wording for a name not in `rows` */
    const VerbName *rows;
    size_t          n;
} VerbTable;

/* Defined in src/parse/mod_verbs.c since MOD-0.4 (the migration test), moved
 * WITH the verb_upper/verb_lower/verb_tables data and their measurement
 * provenance comments — was src/parse/registry.c until this move. */

/* The table PCRE2 would consult for a name whose first byte is `first`. Never
 * NULL: every byte selects one of the two. */
const VerbTable *pcrec_registry_verb_table(int first);
/* Exact lookup within that table, or NULL. */
const VerbName  *pcrec_registry_verb_find(const VerbTable *t,
                                          const char *name, size_t len);
/* Iteration for tests and for --list-verbs; `which` is 0 (the upper table) or
 * 1 (the lower one), matching the order docs and dumps present them in. */
const VerbTable *pcrec_registry_verb_tables(int which);
/* PCRE2's cap on a verb NAME and the complaint past it — shared by both
 * tables, so it is not a VerbTable field. Returns the message; sets *max. */
const char *pcrec_registry_verb_name_limit(size_t *max);

/* The POSIX class-bracket NAME table, for RF_CLASS_NAMED rows — a THIRD
 * schema beside RegRow and VerbName, on D25's reasoning: a POSIX name answers
 * "does PCRE2 have this name" plus, since MOD-0.3a, WHOSE construct it is —
 * because two of the sixteen are not character classes at all. `[[:<:]]` and
 * `[[:>:]]` are zero-width word-boundary assertions, so their honest module
 * is `assertions` (the module `\b`'s own row carries), not the doorway's
 * `classes`; the split is data here, never a special case at a call site. */
typedef struct {
    const char *name;              /* case-sensitive; exactly one spelling */
    bool        whole_class_only;  /* legal ONLY as the class's entire content:
                                      `[[:<:]]` compiles, `[x[:<:]]`,
                                      `[^[:<:]]`, `[[:<:]a]` do not (R9/C3-4);
                                      also unnegatable — `[[:^<:]]` is err 130 */
    unsigned    feature;           /* FEAT_* of the module that will produce it */
    const char *module;            /* that module's name, for diagnostics */
} PosixName;

/* `name` may carry a leading `^` (`[[:^alpha:]]` is a real construct; a
 * whole-class-only name never negates). Returns true if PCRE2 has it;
 * `pcrec_registry_posix_unknown_msg` is what to say when not. */
bool        pcrec_registry_posix_known(const char *name, size_t len);
bool        pcrec_registry_posix_whole_class_only(const char *name, size_t len);
const char *pcrec_registry_posix_unknown_msg(void);
/* Exact lookup (no `^` handling — strip it first), or NULL. */
const PosixName *pcrec_registry_posix_find(const char *name, size_t len);
/* Iteration, for tests and --list-verbs' sibling checks. */
const PosixName *pcrec_registry_posix_names(size_t *n);

/* src/parse/ext.c — the four doorways out of the base grammar (SR-2). The
 * doorway VOCABULARY (ExtWhat / ExtWant / ExtResult and its contract doc)
 * moved above RegRow when MOD-0.3b embedded ports in rows — the dependency
 * inverted; the doorway FUNCTIONS stay here, except `pcrec_ext_verb` (MOD-0.4,
 * the migration test): it moved to src/parse/mod_verbs.c WITH the `(*`
 * doorway's VerbName tables and accessors, keeping this file's exact
 * signature — parse.c's call site did not change. See mod_verbs.c's header
 * for why the move needed no new port/recognise wiring. */

/* THE SHARED GATE and THE SHARED REFUSAL EPILOGUE MACRO, below, are the two
 * pieces of doorway machinery `pcrec_ext_verb` still needs after MOD-0.4's
 * move — promoted from `static`/file-local so mod_verbs.c can call/use them
 * too, with exactly one definition each (ext.c keeps the definitions; the
 * full rationale comments live there, not duplicated here). */
/* Demotes RESULT to VERDICT for a row whose module is not enabled, floors at
 * VERDICT. See ext.c's own comment on the definition for the full ASK-contract
 * rationale. */
ExtWant pcrec_ext_gate(const RegRow *r, ExtWant want);

/* Format a refusal at claim time and return it — relies on the enclosing
 * doorway naming its gated ask level `want`, exactly as ext.c's comment on
 * REFUSE's original site documents. Needs <stdio.h> in the includer for
 * snprintf; every TU that invokes it already carries that include. */
#define REFUSE(atpos, ...) do {                                              \
        ExtResult res_ = { .what = EXT_REFUSAL, .at = (atpos), .msg = "",    \
                           .answered_at = want };                            \
        snprintf(res_.msg, sizeof res_.msg, __VA_ARGS__);                    \
        return res_;                                                         \
    } while (0)
/* A row whose diag value does not belong to its kind is a registry defect,
 * not a pattern error — see REFUSE above; the wording is deliberately not a
 * "requires module" diagnostic since nothing a caller writes can produce it. */
#define BAD_ROW(at, what) \
    REFUSE((at), "internal error: malformed registry row for " what)

/* The ONE epilogue: renders a refusal via ctx_fail (byte-identical to the
 * pre-epilogue diagnostics — same format results, same offsets), returns
 * normally on EXT_NOT_MINE. Every doorway call in parse.c is followed by
 * exactly this call. */
void pcrec_ext_finish(Ctx *cx, const ExtResult *r);

ExtResult pcrec_ext_escape(Ctx *cx, ExtWant want, int c, bool in_class,
                           size_t at);
ExtResult pcrec_ext_group(Ctx *cx, ExtWant want, int c2, size_t at);
ExtResult pcrec_ext_verb(Ctx *cx, ExtWant want, size_t at);
/* The one doorway that can DECLINE: `[` is an ordinary class member most of
 * the time, so EXT_NOT_MINE means "no construct here" and the caller carries
 * on with member parsing. (Its R5-era history — a bool return no path could
 * make true, then `void` — is resolved by the value contract: the decline is
 * IN the value now, and a future "consumed, carry on" outcome extends
 * ExtWhat where both call sites' walls force it to be handled.)
 *
 * `at_content_start` says the construct begins at the FIRST byte of the class's
 * content — no member before it and no `^`. It exists for `[[:<:]]` and
 * `[[:>:]]`, which libpcre2 recognises ONLY as a class's entire content
 * (R9/C3-4); every other POSIX name works in any position. */
ExtResult pcrec_ext_class_bracket(Ctx *cx, ExtWant want, int c2, size_t at,
                                  size_t from, bool at_class_open,
                                  bool at_content_start);

/* True when a `[X...X]` construct really opens at `from` with delimiter `c2` —
 * K4's scan as a predicate, for callers that must ASK rather than diagnose.
 * Used by the range-endpoint check: PCRE2 makes `[0-[:digit:]]` error 150, and
 * pcrec used to read the `[` as a literal and emit a matcher (R9/SPEC-FA).
 * Lives in scans.c since slice 9. */
bool pcrec_ext_class_pair_opens(Ctx *cx, int c2, size_t from);

/* src/parse/scans.c — the ALWAYS-LIVE extent scans (design §12; slice 9).
 * Pure over (pat, patlen) on purpose, named per check01's discovery
 * convention, and their TU must never link the enabled-set symbols below —
 * the linker is the check's oracle. */
bool   pcrec_class_delim_extent_scan(const char *pat, size_t patlen, int c2,
                                     size_t from, size_t *close_at);
/* True iff `at` points at a `{` whose body is quantifier-SHAPED by
 * try_quant's grammar (values unchecked — err-104/105 bodies are shaped).
 * Two load-bearing callers by design: try_quant's pre-test and the `\N{`
 * row's recogniser. See the scan's own comment. */
bool   pcrec_brace_quant_shape(const char *at, size_t avail);
size_t pcrec_verb_name_extent_scan(const char *pat, size_t patlen,
                                   size_t nstart);

/* src/parse/enabled.c — the enabled feature set (slice 9): one home,
 * process-wide, written once by the CLI's --features before any compile.
 * NOT a pcrec_options field (D20 keeps the core API's option surface
 * scalar); promote a library channel later if a caller wants one. */
bool     pcrec_feature_enabled(unsigned featmask);
unsigned pcrec_enabled_mask(void);
int      pcrec_enabled_set_spec(const char *spec, char *err, size_t errsz);
/* D37 (docs/dev/decisions.md): the currently-installed set's own NAME
 * ("std1", "all", "none", or "explicit" for a hand-written module list)
 * and its EXPANDED module list (comma-separated, rendered from the mask —
 * never NULL, "" when nothing is enabled). Filled by pcrec_enabled_set_spec
 * at spec-parse time; src/gen reads both at emission time to stamp the
 * artifact (D37's reproducibility promise). Returned strings point at
 * static storage — do not free. */
const char *pcrec_enabled_set_label(void);
const char *pcrec_enabled_set_modules(void);
/* D37's bare-default MAPPING POINT: the one place "no --features flag"
 * resolves to a named value from --features' own vocabulary. Stays "none"
 * through [STD1] phase A on purpose — see enabled.c's own comment on this
 * constant before changing it. */
extern const char *const PCREC_DEFAULT_FEATURES;

/* src/parse/syntax_dump.c — rendering the registry as text (SR-3). Both
 * renderers return a malloc'd string the caller frees; `flavours` of 0 means
 * "no filter". These are INTERNAL on purpose: the CLI and the test suite are
 * the only consumers today, and promoting one function into lib/pcrec.h later
 * is easy in a way that un-promoting it is not. */
char *pcrec_syntax_tsv(unsigned flavours);
/* `--list-verbs`: the Q1 name tables, which are not RegRows and so cannot
 * appear in the TSV above. Caller frees. */
char *pcrec_syntax_verbs(void);
/* NULL when no construct matches the query. */
/* `--explain QUERY` (SR-3, rewritten at MOD-0.7). NULL when the query reaches
 * no doorway AND no row looks like it — the CLI turns that into exit 1 with
 * its own message. Otherwise the answer, and `*ndissent` (may be NULL) is how
 * many displayed rows FAILED the election/promise/attribution clauses: a
 * defect surfaced, which the CLI reports as exit 3, distinct from exit 1's
 * "your query could not be answered". See syntax_dump.c's own header for the
 * format and for what these clauses can and cannot dissent on.
 *
 * `err` (may be NULL, zeroed on entry) is the R20/MOD07-1 channel and it
 * DISAMBIGUATES THE NULL: empty `err->msg` is "no construct matches" as
 * before; a filled one is a doorway that RAISED — an enabled module port ran
 * a real parse of the query text and that parse failed. Both are exit 1 at
 * the CLI, with different sentences, because "your query could not be
 * answered" is not what happened in the second. */
char *pcrec_syntax_explain(const char *query, unsigned flavours, int *ndissent,
                           pcrec_error *err);
unsigned pcrec_flavour_by_name(const char *name);
/* MOD-0.1 (§18.2): the probe channel behind `pcrec --probe-ask` — one
 * doorway call for `construct` at ask level `want_name` ("claim" /
 * "verdict" / "result"), placed exactly as parse.c would place it, reporting
 * the REAL Ctx cursor before and after. Returns a malloc'd TSV line the
 * caller frees, or NULL when the want name is unknown or the text reaches no
 * doorway. check06 (the cursor rule) compares over this surface.
 *
 * `err` as for `pcrec_syntax_explain` above: zeroed on entry, and a filled
 * `err->msg` on a NULL return is the R20/MOD07-1 case — an enabled port
 * raised rather than the caller asking a bad question. */
char *pcrec_probe_ask(const char *want_name, const char *construct,
                      pcrec_error *err);

/* ---- stage entry points ---- */

Ast *pcrec_parse(Ctx *cx);                          /* src/parse/parse.c */
Ast *pcrec_parse_info(Ctx *cx, AltInfo *info);      /* PARSE-1; info may be NULL */
/* src/core/compile.c — parse-only: the running capture count's end-of-parse
 * value (§18.1; the CLI's --count-groups channel), or -1 with `err` filled
 * on the same refusal pcrec_compile would give. Internal, like the dumps. */
int pcrec_count_groups(const char *pattern, pcrec_error *err);
/* src/core/compile.c — [M4.5c] DD-8's `--emit-ir`: compile as usual but return
 * the VM program LISTING instead of the C. malloc'd, caller frees; NULL with
 * `err` filled on any refusal, including the honest one for a pattern that
 * does not compile to the VM at all. Internal, like the syntax dumps: the CLI
 * and the test suite are its only consumers. */
char *pcrec_emit_ir(const char *pattern, const pcrec_options *opt,
                    pcrec_error *err);
/* PARSE-1: the MODULE CALLBACK. Parses a nested body and stops AT its
 * terminator without consuming it — the caller consumes its own `)` and owns
 * its own unterminated-construct diagnostic. Do NOT hand a module
 * pcrec_parse_info instead: that one requires end-of-pattern and ctx_fails on
 * `)`. info may be NULL. */
Ast *pcrec_parse_body(Ctx *cx, AltInfo *info);
void pcrec_build_nfa(Ctx *cx, Ast *root, Nfa *nfa,  /* src/ir/nfa.c */
                     bool reverse);
void nfa_wrap_unanchored(Ctx *cx, Nfa *nfa);        /* lowest-priority start self-loop */
bool nfa_has_asserts(const Nfa *nfa);
bool nfa_has_bot(const Nfa *nfa);   /* ^ present: still needs ENG_ATTEMPT */
void pcrec_build_dfa(Ctx *cx, Nfa *nfa, Dfa *dfa,   /* src/ir/dfa.c */
                     bool prune, int maxstates);
void pcrec_minimize_dfa(Ctx *cx, Dfa *dfa);         /* src/opt/minimize.c */
void pcrec_emit_dfa(Ctx *cx);                       /* src/gen/emit_dfa.c -> job->csb/hsb */

/* ---- [M4.5b] the VM engine (docs/design/engine_m4.md) ---- */

/* engine_m4.md §5.1: per-pattern engine selection as a PASS, run after parse
 * and before machine construction. Fills cx->job->fit, and ctx_fails with the
 * §5.6/D44.6 refusal when --engine conflicts with what the pattern needs. */
void pcrec_select_engine(Ctx *cx, Ast *root);        /* src/opt/select_engine.c */

/* ---- [ENG-BREP] possessification (docs/design/eng_brep_design.md §2) ---- */

/* The §2.2 rule as a pass: mark every A_REP for which no retreat into the loop
 * can produce a match the preferred path does not. A REWRITE, not an analysis
 * that returns a verdict (§2.8) — it does not observe that the loop needs no
 * frames, it MAKES the quantifier one that needs none, by setting Ast.possessive
 * for src/gen/emit_vm.c to act on.
 *
 * Returns the number of quantifiers it newly marked, which is what makes it
 * MONOTONE and lets a caller drive it to a fixpoint: a second call over the
 * same tree marks nothing and returns 0.
 *
 * Runs only for a VM artifact and only when the pass is allowed — see the call
 * site in pcrec_select_engine, which owns both conditions. */
int  pcrec_possessify(Ctx *cx, Ast *root);           /* src/opt/possessify.c */

/* §2.2's "X admits a unique iteration" — (U1) one-unambiguous, (U2)
 * prefix-free, and non-nullable, decided on the body's position (Glushkov)
 * automaton — exported from possessify.c because the REVERSE-DETERMINISTIC rung
 * needs the identical predicate on the identical construction and a second
 * implementation of a rule that carries three measured refutations is the
 * worst possible place for this project to keep two sources of truth.
 *
 * `pcrec_uniq_scratch` arena-allocates the position state ONCE per pass; the
 * struct is deliberately opaque here because its only property a caller needs
 * is that it is reusable. `*why` names the failing condition
 * ("nullable-body", "ambiguous-body", "not-prefix-free", "model-error") or
 * "unique-iteration" on success. */
void *pcrec_uniq_scratch(Ctx *cx);                   /* src/opt/possessify.c */
bool  pcrec_uniq_iteration(void *scratch, const Ast *body, const char **why);

/* ---- [ENG-BREP] the reverse-deterministic rung (engine_m4.md §2.5) ---- */

/* Mark every A_REP whose consumed run decomposes into iterations UNIQUELY and
 * RECOVERABLY FROM THE RIGHT, by setting Ast.revbody to the body's reversed
 * AST. The emitter then owes it ONE body copy instead of `rmax` of them.
 *
 * Not monotone in possessify's sense and not a fixpoint: the verdict depends
 * only on the body's own shape and its nesting, so one walk decides every
 * quantifier. Returns how many it marked, for the census line.
 *
 * Runs only for a VM artifact and only when the rung is allowed — same call
 * site and same reasoning as pcrec_possessify. */
int  pcrec_revdet(Ctx *cx, Ast *root);               /* src/opt/revdet.c */

/* The set of bytes a node can BEGIN with, over the restricted tree the rung
 * admits (non-nullable, assertion-free), exported so that the emitted backward
 * walk's byte dispatch and the analysis's own check that the dispatch is
 * well-defined read ONE computation. `out` is a 32-byte class bitmap. */
void pcrec_revdet_first(const Ast *a, uint8_t *out);  /* src/opt/revdet.c */

/* ---- [M4.6d] MINIMUM-REMAINING-LENGTH pruning (k23_design.md §4.3) ---- */

/* The least number of subject bytes any match of `a` can consume. The VM
 * emitter threads it down its own walk as a FOLLOW-MIN accumulator and turns
 * the sum into a compile-time constant per program point: a position with
 * fewer bytes left than that constant has no accepting continuation and is
 * cut before a choice point is pushed for it.
 *
 * UNDER-ESTIMATING IS ALWAYS SAFE (it prunes less); over-estimating deletes
 * real matches, silently. src/opt/mrl.c says which cases take which direction
 * and why its switch has no live default arm. */
long long pcrec_minw(const Ast *a);                  /* src/opt/mrl.c */

/* The SATURATION ceiling every minimum-width arithmetic pins itself to. Shared
 * because the emitter's own accumulator has to hold the same ceiling the
 * analysis does — two different ceilings would let a long concatenation of
 * saturated subtrees overflow past the one that was supposed to prevent it.
 * Far above any addressable subject on purpose: a saturated bound reads as
 * "doomed", which at 2^40 remaining bytes it is. */
#define PCREC_MINW_MAX (1LL << 40)

/* engine_m4.md §2: the backtracking VM as emitted specialized C. Emits the
 * whole artifact (prologue, ABI types, the DFA prefilter pair when the fit
 * says so, the VM itself, and the four entry points). */
void pcrec_emit_vm(Ctx *cx, const Ast *root);        /* src/gen/emit_vm.c */

/* src/gen/emit_dfa.c, exported for emit_vm.c: the shared artifact-prologue
 * and entry-point emitters. `pcrec_emit_dfa_engine` emits ONE engine function
 * body (the same forward+reverse or attempt code pcrec_emit_dfa emits) under
 * a caller-chosen name and storage class, which is how the VM's hybrid gets
 * its prefilter without a second copy of that emitter (§6.1, §2.8's "reused
 * unchanged" table). */
typedef struct {
    const char *searchfn, *matchfn, *matchcapsfn, *infoname;
    char        upper[80];
} GenNames;
void pcrec_gen_names(Ctx *cx, GenNames *g);
void pcrec_emit_abi_types(StrBuf *sb);
void pcrec_emit_c_string_literal(StrBuf *sb, const char *s, size_t len);
void pcrec_emit_prologue(Ctx *cx, const GenNames *g, int ncaps);
void pcrec_emit_dfa_engine(Ctx *cx, const char *fn, const char *storage);
void pcrec_emit_info(Ctx *cx, const GenNames *g, int engine, const char *why,
                     long long budget, long long work, long long frames,
                     long long ceiling);
void pcrec_emit_main(Ctx *cx, const GenNames *g);

#endif /* PCREC_INTERNAL_H */
