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
    A_EOL      /* $ : end of subject or before a final \n */
} AKind;

typedef struct Ast Ast;
struct Ast {
    AKind    k;
    uint8_t  cls[32];       /* A_CLASS: 256-bit membership bitmap */
    Ast     *l, *r;
    int      rmin, rmax;
    bool     greedy;
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

typedef struct {
    /* heap-held so longjmp cleanup sees consistent pointers */
    Nfa    nfa;      /* forward NFA (unanchored-wrapped for ENG_UNANCH) */
    Nfa    rnfa;     /* reversed-pattern NFA (ENG_UNANCH only) */
    Dfa    dfa;      /* forward DFA */
    Dfa    rdfa;     /* reverse DFA, non-pruning (ENG_UNANCH only) */
    int    engine;
    StrBuf csb, hsb;
} Job;

typedef struct {
    Arena                arena;
    const char          *pat;
    size_t               patlen;
    size_t               pos;      /* parser cursor */
    int                  depth;    /* parser group-nesting depth (bounded) */
    /* SCOPED PARSE STATE (PARSE-1). Seeded from opt->caseless at parse entry
     * and saved/restored around every group body, because that is where PCRE2
     * restores it: measured 17/17 against libpcre2 10.46, `(?i)` set anywhere
     * inside a group stays in force to the end of THAT group — it leaks across
     * sibling alternation branches, `(a(?i)b|c)d` matching `Cd` — and is
     * restored at the immediately-enclosing `)`, not the outermost one. A
     * top-level `(?i)` is never restored.
     *
     * `opt` is const and caller-owned, so it CANNOT hold this: a module doing
     * D29's "set parse state, parse body, restore" has nothing to set. Nothing
     * mutates this field yet — module `modifiers` (MOD-0.5) is its first
     * writer — so today it is exactly opt->caseless for the whole parse, which
     * is asserted by byte-identity rather than assumed. */
    bool                 caseless;
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
    jmp_buf              jb;
    pcrec_error         *err;
    const pcrec_options *opt;
    Job                 *job;
} Ctx;

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

    /* The row is an INLINE OPTION SETTING, so its construct is the whole run of
     * option letters up to `)` or `:` — not the single byte that selected it
     * (Q2). ext.c validates the run with pcrec_registry_option_run_ok and falls
     * back to the doorway's rejection when it is not one.
     *
     * It exists because splitting the `(?` catch-all into eleven letter rows
     * fixed the first byte and left `(?iZ)` still promising a module for syntax
     * PCRE2 refuses. A row-per-byte cannot express "and the rest must parse";
     * this flag is where that obligation lives. */
    RF_OPTION_RUN = 1u << 4,

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

typedef struct RegRow RegRow;
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
     * (SR-9, docs/design_registry_selectors.md §7). Since MOD-0.2 the lookup
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
/* Is `at[0..avail)` a valid PCRE2 inline option run — the text starting at the
 * byte after `(?`, up to and including its `)` or `:` terminator? The grammar
 * is measured against libpcre2; see registry.c. */
bool pcrec_registry_option_run_ok(const char *at, size_t avail);

/* ---- doorway 3's NAME tables (Q1) --------------------------------------
 *
 * The other three doorways are decided by a BYTE and a RegRow can carry the
 * whole answer. `(*` is decided by a NAME, and until Q1 pcrec had no name
 * table at all: one catch-all row answered "requires module 'verbs'" for every
 * name, including names PCRE2 does not have. That was a live over-promise —
 * `(*NOTAVERB)` was told a module would implement it — and it made an external
 * name differential impossible, because pcrec's answer did not depend on the
 * name. See docs/decisions.md D25.
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
 * inverted; the doorway FUNCTIONS stay here. */

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
size_t pcrec_verb_name_extent_scan(const char *pat, size_t patlen,
                                   size_t nstart);

/* src/parse/enabled.c — the enabled feature set (slice 9): one home,
 * process-wide, written once by the CLI's --features before any compile.
 * NOT a pcrec_options field (D20 keeps the core API's option surface
 * scalar); promote a library channel later if a caller wants one. */
bool     pcrec_feature_enabled(unsigned featmask);
unsigned pcrec_enabled_mask(void);
int      pcrec_enabled_set_spec(const char *spec, char *err, size_t errsz);

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
char *pcrec_syntax_explain(const char *query, unsigned flavours);
unsigned pcrec_flavour_by_name(const char *name);
/* MOD-0.1 (§18.2): the probe channel behind `pcrec --probe-ask` — one
 * doorway call for `construct` at ask level `want_name` ("claim" /
 * "verdict" / "result"), placed exactly as parse.c would place it, reporting
 * the REAL Ctx cursor before and after. Returns a malloc'd TSV line the
 * caller frees, or NULL when the want name is unknown or the text reaches no
 * doorway. check06 (the cursor rule) compares over this surface. */
char *pcrec_probe_ask(const char *want_name, const char *construct);

/* ---- stage entry points ---- */

Ast *pcrec_parse(Ctx *cx);                          /* src/parse/parse.c */
Ast *pcrec_parse_info(Ctx *cx, AltInfo *info);      /* PARSE-1; info may be NULL */
/* src/core/compile.c — parse-only: the running capture count's end-of-parse
 * value (§18.1; the CLI's --count-groups channel), or -1 with `err` filled
 * on the same refusal pcrec_compile would give. Internal, like the dumps. */
int pcrec_count_groups(const char *pattern, pcrec_error *err);
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

#endif /* PCREC_INTERNAL_H */
