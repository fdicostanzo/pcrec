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
    jmp_buf              jb;
    pcrec_error         *err;
    const pcrec_options *opt;
    Job                 *job;
} Ctx;

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
    FEAT_VERBS         = 1u << 15
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

enum {
    RF_CLASS_BASE = 1u << 0,  /* inside a class this byte is BASE syntax and the
                                 doorway is not taken (\b is backspace there) */

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
    RF_CLASS_NAMED = 1u << 2
};

#define REG_SEL_ANY (-1)      /* catch-all row; last row for its kind */

/* Field groups are ordered identity / ownership / selection / outcome / doc.
 * `feature` and `module` are ADJACENT on purpose: they are two halves of one
 * fact, and registry.c's M_* macros emit them as a pair so a row cannot carry
 * a feature bit that disagrees with the module name it prints. */
typedef struct {
    RegKind     kind;
    int         sel;       /* the deciding byte, or REG_SEL_ANY */
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
} RegRow;

/* src/parse/registry.c */
const RegRow *pcrec_registry(RegKind k, size_t *n);
const RegRow *pcrec_registry_find(RegKind k, int sel);

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

/* The POSIX class names libpcre2 recognises, for RF_CLASS_NAMED rows. `name`
 * may carry a leading `^` (`[[:^alpha:]]` is a real construct). Returns true if
 * PCRE2 has it; `pcrec_registry_posix_unknown_msg` is what to say when not. */
bool        pcrec_registry_posix_known(const char *name, size_t len);
/* True for the names libpcre2 accepts ONLY as a class's ENTIRE content:
 * `[[:<:]]` compiles, `[x[:<:]]` and `[^[:<:]]` and `[[:<:]a]` do not. Every
 * other POSIX name is position-independent (R9/C3-4). */
bool        pcrec_registry_posix_whole_class_only(const char *name, size_t len);
const char *pcrec_registry_posix_unknown_msg(void);
/* Iteration, for tests and --list-verbs' sibling checks. */
const char *const *pcrec_registry_posix_names(size_t *n);

/* src/parse/ext.c — the four doorways out of the base grammar (SR-2). Each is
 * called only after parse.c's own switch has declined, so a base-tier pattern
 * reaches none of them.
 *
 * The three `noreturn`s are TODAY's truth, not the design's: every row is
 * RS_MODULE or RS_REJECTED, so every dispatch ends in a diagnostic. When SR-6
 * lands the first module handler one of them starts returning a value and gcc
 * WARNS ("'noreturn' function does return").
 *
 * It warns; it does not fail the build. An earlier version of this comment
 * claimed a compile error, and an R5 critic disproved it by writing SR-6's
 * shape and watching `make` succeed: WARN is `-Wall -Wextra` with no -Werror,
 * and this particular warning has no controlling -W option, so only a blanket
 * -Werror would promote it. Whether to adopt one is a live question (R5-Q1),
 * and until it is answered this is a loud hint, not a guard. A comment that
 * asserts a guard which does not exist is worse than no comment. */
void pcrec_ext_escape(Ctx *cx, int c, bool in_class, size_t at)
     __attribute__((noreturn));
void pcrec_ext_group(Ctx *cx, int c2, size_t at) __attribute__((noreturn));
void pcrec_ext_verb(Ctx *cx, size_t at) __attribute__((noreturn));
/* The one doorway that can DECLINE: `[` is an ordinary class member most of the
 * time, so this returns normally to mean "no construct here" and the caller
 * carries on with member parsing.
 *
 * `void`, not `bool`. It returned bool until an R5 critic pointed out that no
 * path could ever produce `true` and both callers discarded the value — a
 * return type that cannot take its second value is a lie of the same kind the
 * `noreturn`s above are honest about, and a worse one, because when SR-6 gives
 * a class-bracket row a handler returning "consumed, carry on", both callers
 * would ignore it and fall straight through to member parsing with nothing in
 * the build objecting. Adding the value back is SR-6's job, at which point the
 * signature change forces both call sites to be looked at.
 *
 * `at_content_start` says the construct begins at the FIRST byte of the class's
 * content — no member before it and no `^`. It exists for `[[:<:]]` and
 * `[[:>:]]`, which libpcre2 recognises ONLY as a class's entire content
 * (R9/C3-4); every other POSIX name works in any position. */
void pcrec_ext_class_bracket(Ctx *cx, int c2, size_t at, size_t from,
                             bool at_class_open, bool at_content_start);

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

/* ---- stage entry points ---- */

Ast *pcrec_parse(Ctx *cx);                          /* src/parse/parse.c */
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
