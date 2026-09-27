/* src/facts/facts.h — THE PATTERN-FACTS RECORD's CONSUMER header
 * ([PATFACTS], D120/D126; docs/design/patfacts/design.md §2, §4.2.1).
 *
 * A consumer of a pattern fact reads it through this header and nothing
 * else: value types, accessors and renderers — never a derivation. The
 * derivations are declared in `facts_derive.h`, which only this directory and
 * the OWNER files `facts.def` names may include; `tests/codegen/
 * run_facts_checks.sh` enforces that from the include graph and the link
 * symbols (design §4.2.3).
 *
 * THE RECORD IS LAZY AND MEMOIZED (design §2, ruled Q2). A fact is derived on
 * its first ask, cached for the rest of the compile ATTEMPT, and reset with
 * the attempt's `Job` (one `calloc` per attempt, so the retry ladder resets it
 * for free). Every accessor does four things, in order: the EPOCH GUARD (a
 * fact asked before its seal is an internal-error refusal), the MEMO, the
 * DENY (a fact-level `-fno-` stores the fact's empty value without deriving —
 * "nothing to find" for EVERY consumer, design §7.1, ruled Q3), and the
 * DERIVATION, called once.
 *
 * ASK ORDER CANNOT CHANGE AN ANSWER: each derivation is a pure function of
 * the tree sealed at its epoch and `cx->opt`. That is what lets a DFA-only
 * artifact skip the VM's facts, and it is what `--emit-facts`' force loop
 * (after the artifact is complete, design §11.4) relies on.
 *
 * Self-contained on purpose: `core/internal.h` includes it mid-file for
 * `Job.pf`, and it needs nothing of that header but the `Ctx` name. */
#ifndef PCREC_FACTS_H
#define PCREC_FACTS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "core/limits.h"

typedef struct Ctx Ctx;
struct Ast;

/* ---- the facts' value types -------------------------------------------- */

/* [OPT-REQPOS] tier 2b — THE NECESSARY LITERAL RUN, in the bounded form the
 * emitted compare needs: `len` contiguous bytes every match of the pattern
 * must contain, and the INDEX within them of the one the emitted `memchr`
 * scans for.
 *
 * `len == 0` is the decline and is the safe direction, exactly as
 * `req_byte`'s -1 is: no run, no compare, the artifact is the shape it
 * was before this mechanism. `len` is never 1 — a one-byte run is
 * `[OPT-REQBYTE]`'s own `L = 1` case and is carried by the
 * `req_byte` fact alone, so the two facts never describe the same emitted text.
 *
 * `idx` is a position INSIDE the run and nothing else. It is not an offset
 * from the match start, not a `dmin`/`dmax`, and the mechanism reads no such
 * thing — a run is a statement about its own members' RELATIVE positions
 * (docs/design/reqpos_2b.md §0 finding 1).
 *
 * [K66] `whole` is the run the WINDOW `bytes` was cut from, as the analysis
 * stored it (at most `PCREC_MAX_REQ_RUN_SCAN` bytes), and `bytes` is exactly
 * `whole + at` for `len` bytes — one derivation, both halves published by it.
 * The window is the speed choice every route compares; the whole run is what
 * a VM route with no DFA scan in front ALSO compares, because there the
 * pre-check is the only linear no-match proof and a proof resting on one
 * window made NOMATCH-vs-give-up follow the prior's window pick. */
typedef struct {
    unsigned char bytes[PCREC_MAX_REQ_RUN_EMIT];
    int len;   /* 0 = declined; otherwise 2..PCREC_MAX_REQ_RUN_EMIT */
    int idx;   /* 0..len-1: which member the emitted memchr tests */
    unsigned char whole[PCREC_MAX_REQ_RUN_SCAN];
    int whole_len;   /* 0 exactly when `len` is; otherwise len..SCAN */
    int at;          /* where the window starts inside `whole` */
} ReqRun;

/* [K65] THE WHOLE NECESSARY SET, as a 256-bit membership table: every byte
 * every match of the pattern must contain, of which the `req_byte` fact is the
 * one member the pick chose. Empty exactly when `req_byte` is -1.
 *
 * It is carried past the analysis because one route needs more than the pick.
 * On a VM artifact with no DFA scan in front, the pre-check is the only
 * linear NO-MATCH PROOF the call has, and a proof resting on one member makes
 * the answer on a hostile subject (NOMATCH or a step give-up) depend on which
 * member a SPEED rule chose (K65). Testing every member makes it depend on the
 * set alone, which is a fact about the pattern. */
typedef struct {
    unsigned char bits[32];
    /* The walk's THREADED RIGHTMOST member — PCRE2's LASTCODEUNIT rule, the
     * tiebreak the derived pick falls back on (and its whole answer under
     * every encoding but `byte`) — or -1 exactly when `bits` is empty. A set
     * has no order, so it is carried beside the bits rather than recovered
     * from them ([PATFACTS] step 3.0: the core/derived split). */
    int rightmost;
} ReqSet;

/* [OPT-ANCHOR-VM] THE START ANCHOR — at which positions can a match BEGIN?
 * ONE predicate, read by both emitters (src/facts/startanch.c's header carries
 * the whole account, including why the DFA's own `dfa_interior_dead` pair
 * becomes a CONFIRMATION of this answer rather than a second source of it,
 * and why the implication runs in only one direction). `_NONE` is the safe
 * answer and every undecidable arm gives it. */
enum {
    PCREC_SANCH_NONE = 0,   /* a match may begin anywhere */
    PCREC_SANCH_GSTART,     /* every match begins at the caller's startpos */
    PCREC_SANCH_BOT         /* every match begins at absolute offset 0 */
};
/* The stamp/emitted-token spelling of the three values, so `<PREFIX>_VM_START`
 * and `--list-axes`' own row cannot drift from the enum. */
const char *pcrec_start_anchor_name(int sanch);      /* src/facts/startanch.c */

/* ---- the record --------------------------------------------------------- */

/* The seals (design §3). A fact may be asked only after its epoch's seal; E2
 * is sealed by `compile_driver` right after `pcrec_lower_enc`, the last tree
 * rewrite. E1 (structural, forced eagerly) and E3 (the wrapped NFA, sealed
 * per branch) arrive with their facts in later migration steps. */
typedef enum { PF_E0 = 0, PF_E1_STRUCT, PF_E2_LOWERED, PF_E3_MACHINE } PfEpoch;

/* One id per `facts.def` row, in row order. */
typedef enum {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) PF_##ID,
#include "facts/facts.def"
    PF_NFACTS
} PfFactId;

/* A fact's STATUS — `--emit-facts`' closed `status` vocabulary
 * (docs/spec/facts_listing.md). `PF_UNASKED` never reaches the listing: the
 * force loop asks every fact whose epoch was sealed. */
typedef enum {
    PF_UNASKED = 0,
    PF_DERIVED,    /* the derivation ran; its answer may be an empty value */
    PF_DENIED,     /* a fact deny stored the empty value; `why.deny` names it */
    PF_DECLINED,   /* the derivation ran and declined with a stated reason */
    PF_ABSENT      /* never derivable on this route, or forcing it failed */
} PfStatus;

/* WHY a fact has its value, STORED when the value is stored and never
 * reconstructed from the value (design §11.3 item 3). */
typedef enum {
    PF_WHY_NONE = 0,         /* a plain derivation */
    PF_WHY_DENY,             /* `deny` holds the one flag bit that denied it */
    PF_WHY_FORCE_FAILED      /* the listing's forced ask failed (§11.4) */
} PfWhyCode;

typedef struct {
    unsigned char status;    /* PfStatus */
    unsigned char code;      /* PfWhyCode */
    uint64_t      deny;      /* the flag bit, when code == PF_WHY_DENY */
} PfWhy;

typedef struct {
    uint32_t have;           /* one bit per fact: asked and cached */
    uint32_t used;           /* one bit per fact: asked by a PASS (§11.4) */
    PfEpoch  epoch;          /* advanced ONLY by compile_driver at the seals */
    const struct Ast *root;  /* the tree sealed at E2 */
    /* [OPT-ANCHOR-VM] E2 core: `PCREC_SANCH_*`; `PCREC_SANCH_NONE` under
     * `-fno-vm-anchor-bound`, deliberately indistinguishable from "nothing to
     * bound". The VM bounds its attempt loop on it; the DFA asserts its own,
     * independently derived answer agrees in the sound direction. */
    int       start_anchor;
    /* [OPT-ENDWIN] E2 core: the end-anchor start window in BYTES, or -1 where
     * the analysis declines; -1 under `-fno-end-window`. Both emitters. */
    long long end_window;
    /* [K65] E2 core: the whole necessary set; empty under `-fno-req-byte`. */
    ReqSet    req_set;
    /* [OPT-REQPOS] E2 core `whole` + derived window (`bytes`/`len`/`idx`/
     * `at`): `len == 0` under `-fno-req-run` and under `-fno-req-byte`, which
     * denies the run with it — there is no run check without a byte to
     * `memchr`. One struct, two facts: `req_whole_run` and `req_run`. */
    ReqRun    req_run;
    /* [OPT-REQBYTE] E2 derived: the byte the emitted `memchr` tests (the
     * run's scan member where a run shipped, the set's pick otherwise), or
     * -1; -1 under `-fno-req-byte`. */
    int       req_byte;
    PfWhy     why[PF_NFACTS];
} PatFacts;

/* ---- the seals -------------------------------------------------------- */

/* Seals E2 over `root`, the LOWERED tree: records it and advances the epoch.
 * Called once per attempt, by `compile_driver`, after `pcrec_lower_enc`. */
void pcrec_facts_seal_e2(Ctx *cx, const struct Ast *root);

/* ---- the accessors (every one E2 today) ------------------------------- */

int            pcrec_fact_start_anchor(Ctx *cx);
long long      pcrec_fact_end_window(Ctx *cx);
const ReqSet  *pcrec_fact_req_set(Ctx *cx);
/* Both return `PatFacts.req_run`: the whole run is its core half, the
 * window its derived half, and each accessor answers for its own. */
const ReqRun  *pcrec_fact_req_whole_run(Ctx *cx);
const ReqRun  *pcrec_fact_req_run(Ctx *cx);
int            pcrec_fact_req_byte(Ctx *cx);

#endif /* PCREC_FACTS_H */
