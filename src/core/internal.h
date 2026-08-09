/* Internal shared definitions for the pcrec compiler. Not installed. */
#ifndef PCREC_INTERNAL_H
#define PCREC_INTERNAL_H

#include <setjmp.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "pcrec.h"

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

enum {
    /* M2.8 raised this from 20000. It is a MEMORY backstop (48 B/state, two
     * machines, so ~12.6 MB), not the real ceiling: the DFA caps below are
     * grounded in emitter cost (R1 A-3) and now bind first across the
     * realistic keyword range — 6000-word lists compile, 10000-word lists
     * fail on the DFA cap with its actionable "VM engine arrives in M4".
     * Stack depth is no longer a constraint here: clo_visit's tail edges are
     * iterative (verified at -O0 on a 1,000,000-branch alternation). */
    PCREC_MAX_NFA_STATES       = 131072,
    PCREC_MAX_DFA_STATES_GOTO  = 10000,   /* computed-goto attempt engine */
    PCREC_MAX_DFA_STATES_TABLE = 32000,   /* table engine; must fit in short */
    PCREC_MAX_TABLE_ENTRIES    = 2000000  /* states*ncls bound (~12 MB source) */
};

#endif /* PCREC_INTERNAL_H */
