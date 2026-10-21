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
    /* [OPT-LITSCAN] S4 C3 THE MASKS, each position's K: `(x & mask[i]) ==
     * bytes[i]` is the position's membership test, `0xFF` an exact byte, one
     * clear bit a two-member cube (litscan_s4.md §2.3.2). `mask` is exactly
     * `whole_mask + at`, as `bytes` is `whole + at`. All `0xFF` on an exact
     * run, so a reader of `bytes`/`len` alone stays correct on every exact
     * run; `pcrec_req_run_masked` is the one spelling of "is it masked". */
    unsigned char mask[PCREC_MAX_REQ_RUN_EMIT];
    unsigned char whole_mask[PCREC_MAX_REQ_RUN_SCAN];
    /* [K82] THE RUN'S MAXIMUM BYTE OFFSET FROM THE ATTEMPT START, in its two
     * halves, as `whole`/`bytes` are: `whole_maxoff` the core walk's bound on
     * where `whole` begins inside any match (`req_whole_run`), and `maxoff`
     * the window's, `whole_maxoff + at` (`req_run_maxoff`). Either is
     * `PCREC_W_UNBOUNDED` where no static bound exists; meaningful only where
     * the run itself is (`whole_len`/`len` >= 2). docs/design/litscan_k82h.md
     * §1.3: every successful attempt at `p` holds the window at some `q` in
     * `[p, p + maxoff]` (invariant F), which is what lets a search begin its
     * scan `maxoff` bytes before the pre-check's first hit. */
    long long whole_maxoff;
    long long maxoff;
} ReqRun;

/* Does the run's WINDOW carry a position that is not one exact byte? */
static inline bool pcrec_req_run_masked(const ReqRun *r)
{
    for (int i = 0; i < r->len; i++)
        if (r->mask[i] != 0xFF) return true;
    return false;
}

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
    /* [REQ-HANDOFF-L1] per MEMBER, the largest byte offset from the attempt
     * start at which some guaranteed occurrence of it begins, or
     * `PCREC_W_UNBOUNDED` (the walk's `RbSet.off`, published by the core
     * fact `req_set_maxoff`, not by `req_set`, whose text a stamp renders).
     * Unread for a non-member. Invariant F at one byte: every successful
     * attempt at `p` holds member `b` at some `q` in `[p, p + maxoff[b]]`. */
    long long maxoff[256];
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

/* [OPT-REVEND] L1 THE END PIN — where can a match END? The view half of
 * `end_window` (src/facts/endwin.c's header): every match ends at the
 * subject's end (`\z`), or at it or one byte before a final newline (`$`,
 * `\Z`), with no width and no encoding conjunct. Declines `\G` anywhere and
 * a multiline `$`; a trailing zero-width factor (a lookaround included) is
 * transparent, which is sound for a seeded walk because a seed where no match
 * ends accepts nothing there (a DEAD seed is skipped, revend.md §3.7). Ordered
 * weakest first, `ew_walk`'s order. */
enum {
    PCREC_EPIN_NONE = 0,    /* not end-pinned (or `\G`, or a multiline `$`) */
    PCREC_EPIN_EOL,         /* every match ends at n, or at n-1 before a final '\n' */
    PCREC_EPIN_Z            /* every match ends at n */
};

/* [START-SET] THE START SET (fact `start_set`, E2 core; D148,
 * docs/design/startset.md §3): a SUPERSET of the bytes the first consumed byte
 * of a non-empty match can be, on the lowered tree, with every zero-width node
 * erased (src/facts/startset.c carries the argument). `nullable` is the ERASED
 * language's: where it is set no byte test is a necessary condition and
 * `bits` must not be read as one. Bit `b` of `bits` is `bits[b >> 3] >>
 * (b & 7)`, `pcrec_cls_bits`' layout. The empty value (no fact) is every
 * byte, nullable — "nothing known". */
typedef struct {
    unsigned char bits[32];
    bool          nullable;
} StartSet;

/* [OPT-K] ONE OFFSET OF THE K-SET WALK: the bytes every match carries `k`
 * bytes after its own start, as the pattern's NFA proves them
 * (src/facts/kset.c's header carries the soundness argument). */
typedef struct {
    int      k;          /* the offset, in bytes from the candidate start */
    uint8_t  set[256];   /* the bytes a match may carry there */
    int      count;      /* how many */
    int      byte;       /* the single value when count == 1 */
} PrefixK;

/* THE K-SET WALK (fact `kset_walk`, E3): offsets 0..nwalk-1, consecutive
 * from 0, each a proper subset of the alphabet. `nwalk == 0` is the empty
 * value — no offset says anything — and is what an unsealed route reads. */
typedef struct {
    int      nwalk;
    PrefixK  k[PCREC_PREFIX_K_MAX];
} KsetWalk;

/* [OPT-LITSCAN] S1 THE RUN PIN (fact `run_pin`, E3 derived): an EXACT
 * stretch of the necessary run's window (`req_run`'s `bytes[at .. at+len)`)
 * sits at offset `o` of EVERY match — the walk's `k[o + i]` is the singleton
 * `bytes[at + i]` for every i < len. On an exact run the stretch is the whole
 * window (`at == 0`, `len == req_run.len`, `idx == req_run.idx`); on a
 * masked one ([OPT-LITSCAN] S4 C3, litscan_s4.md §2.3.5) it is the maximal
 * exact stretch around the window's rarest exact position `at + idx`, so a
 * pin is a fact about EXACT positions only. A pure NFA+window fact: it may
 * be true where the forward scan carries no offset-0 prefilter, so EVERY
 * READER OWES THE KIND GATE (design §4.5) — read it only where the
 * prefilter kind is not `DFA_PF_NONE`. `pinned == false` is the empty value
 * (no run, a denied run, no pin, an unsealed route). */
typedef struct {
    bool     pinned;
    int      o;          /* meaningful only when pinned, as are the three below */
    int      at, len;    /* the stretch inside the window */
    int      idx;        /* the scanned position inside the stretch */
} RunPin;

/* [START-LANDING] THE ONE-CHARACTER FACT (fact `land_char`, E3 core,
 * docs/design/start_landing.md §2.4): `holds` where every one-character path
 * from the pattern's anchored start ends dead or unconditionally accepting,
 * with no assertion before it and no empty match; `wide` where a first byte
 * lies above the encoding's `onebyte_max`, so the character at a landing may
 * span bytes and §2.5's guard is owed. The empty value is `{ false, false }`. */
typedef struct {
    bool holds;
    bool wide;
} LandChar;

/* D164 B3 THE END MARK's TAILS (fact `end_mark`, E2 derived,
 * docs/design/endmark.md §1.1, §R.2): the path-final non-multiline `$`/`\Z`
 * nodes of the lowered tree (`tail[0..ntails)`, arena), which the NFA builder
 * lowers to the tail `T` under the mark when asked (`pcrec_build_nfa_marked`); and
 * `complete`, true where lowering them leaves every match ending at `\z`
 * (every `eol` pin is a tail), the precondition of the one-walk `tagged`
 * form. Declined (empty: no tails) where the pin is not `eol`, or where the
 * pattern calls a subroutine (L3: a call site re-enters a body with another
 * continuation). */
typedef struct {
    int                ntails;
    bool               complete;
    const struct Ast **tail;
    /* The tail `T` itself (`pcrec_eol_tail`: `\Z`'s definitions row, §R.2.4),
     * NULL where the row gives no usable tail; its width `L` in bytes (the
     * distance domain 0..L); and its first byte where its first-byte set is
     * exactly one byte, else -1. */
    const struct Ast  *body;
    int                width;
    int                byte;
} EndMark;

/* [START-LANDING] THE BYTE WIDTH INTERVAL (fact `width`, E3 core, §3.1):
 * every match is between `bmin` and `bmax` bytes long; `bmax` is
 * `PCREC_W_UNBOUNDED` where no bound exists, and `bmin` is -1 (the empty
 * value, with `bmax` -1) where nothing is known. A fixed width is
 * `bmin == bmax`. */
typedef struct {
    long long bmin, bmax;
} WidthIv;

/* [KIT-VERIFY] U1 Z2 THE SPAN SLICE (fact `span_facts`, E3 core;
 * docs/design/kit_proof.md §5.1-§5.2 UL-0, docs/design/ctx_span.md §3.2-§3.4,
 * §3.8): span 0 at the MATCH-START origin, priority-free, on the lowered
 * machine the k-set walk reads. `set[d]` is the TRUE byte set some match
 * carries at offset d from its own start, the context before it ranging
 * over every byte and the subject start (kit_proof.md §R2.2's ruling: a
 * byte reached through a `$` before a final newline is in it), and
 * `exact_len` the largest L such that, for every d < L, the length-(d+1)
 * prefixes of the matches are exactly `set[0] x .. x set[d]` and no match
 * ends before d + 1. An UNDER-statement of `exact_len` is sound; `set[d]`
 * is meaningful only for d < `exact_len`. `stated` is MK_LANG_UNSTATED (the
 * empty value) on a route that never sealed E3 or where the walk declined
 * (an erased or marked machine): a reader then states 0. The k-set walk's
 * `KsetWalk` stays the pass-through HULL its consumers read; these are the
 * narrowed sets (ctx_span.md §3.8 [r4rc R2]). */
typedef enum { MK_LANG_UNSTATED = 0, MK_LANG_STATED } MkLangState;
typedef struct {
    uint8_t  stated;                       /* MkLangState                     */
    uint8_t  exact_len;                    /* 0..PCREC_PREFIX_K_MAX           */
    uint8_t  set[PCREC_PREFIX_K_MAX][32];  /* S_d, d < exact_len; bit b & 7 of
                                              byte b >> 3 (mf_term.set's)   */
} MkLang;

/* THE KIND MASK's bits (fact `kinds`, E1): which construct kinds the pattern
 * contains, each the root answer of the node predicate named beside it
 * (src/facts/kinds.c). A bit exists only where a pass asks it at the root. */
enum {
    PF_KIND_BREF            = 1u << 0,   /* pcrec_has_bref */
    PF_KIND_LINKED_CALL     = 1u << 1,   /* pcrec_has_linked_call */
    PF_KIND_VAR             = 1u << 2,   /* pcrec_has_var */
    PF_KIND_ATOMIC          = 1u << 3,   /* pcrec_has_atomic */
    PF_KIND_LOOK            = 1u << 4,   /* pcrec_has_lookaround */
    PF_KIND_LIVE_CAPTURE    = 1u << 5,   /* pcrec_has_live_capture */
    PF_KIND_COLLAPSIBLE_REP = 1u << 6    /* pcrec_has_collapsible_rep */
};

/* ---- the record --------------------------------------------------------- */

/* The seals (design §3). A fact may be asked only after its epoch's seal. E1
 * is sealed by `compile_driver` right after `pcrec_callgraph_build`, on the
 * STRUCTURAL tree, and its facts are FORCED there rather than derived on
 * first ask, because `pcrec_lower_enc` later rewrites that tree in place. E2
 * is sealed right after `pcrec_lower_enc`, the last tree rewrite. E3 (the
 * wrapped NFA) is sealed per BRANCH, on `ENG_UNANCH` alone. */
typedef enum { PF_E0 = 0, PF_E1_STRUCT, PF_E2_LOWERED, PF_E3_MACHINE } PfEpoch;

/* `facts.def`'s `kind` column (design §4.1): a CORE fact is a walk of the
 * sealed IR reading no prior and no other fact's choice; a DERIVED fact is a
 * function of core facts (and, from [FINDINGS] B1, the byte-rate). */
typedef enum { PF_CORE = 0, PF_DERIVED } PfKind;

/* One id per `facts.def` row, in row order. */
typedef enum {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) PF_##ID,
#include "facts/facts.def"
    PF_NFACTS
} PfFactId;

/* A fact's STATUS — `--emit-facts`' closed `status` vocabulary
 * (docs/spec/facts_listing.md). `PF_ST_UNASKED` never reaches the listing: the
 * force loop asks every fact whose epoch was sealed. */
typedef enum {
    PF_ST_UNASKED = 0,
    PF_ST_DERIVED, /* the derivation ran; its answer may be an empty value */
    PF_ST_DENIED,     /* a fact deny stored the empty value; `why.deny` names it */
    PF_ST_DECLINED,   /* the derivation ran and declined with a stated reason */
    PF_ST_ABSENT      /* never derivable on this route, or forcing it failed */
} PfStatus;

/* WHY a fact has its value, STORED when the value is stored and never
 * reconstructed from the value (design §11.3 item 3). */
typedef enum {
    PF_WHY_NONE = 0,         /* a plain derivation */
    PF_WHY_DENY,             /* `deny` holds the one flag bit that denied it */
    /* `end_window`'s four structural declines (src/facts/endwin.c's header):
     * an encoding with non-boundary positions; no end anchor on every path;
     * a `\G` anywhere; an unbounded maximum width. */
    PF_WHY_ENC_MULTIBYTE,
    PF_WHY_NOT_END_ANCHORED,
    PF_WHY_GSTART,
    PF_WHY_UNBOUNDED,
    /* Which RATE RULE a derived pick answered by (design §6.3): the shipped
     * byte-frequency prior, or the prior's NONE answer (the rightmost member)
     * under an encoding it is not keyed to. */
    PF_WHY_RATE_BUILTIN,
    PF_WHY_RATE_NONE,
    PF_WHY_FORCE_FAILED,     /* the listing's forced ask failed (§11.4) */
    /* An E3 fact on a route that never sealed E3 (design §3, r1 A3): a
     * forward NFA exists but `ENG_ATTEMPT` never wraps it, or no forward NFA
     * was built at all (a VM route with no DFA scan). Status `absent`. */
    PF_WHY_ATTEMPT_UNWRAPPED,
    PF_WHY_NO_FORWARD_NFA,
    /* [START-LANDING] `land_char`'s declines (src/facts/kset.c): Λ.1 the
     * pattern matches empty, an assertion reads the start edge, or nothing
     * consumes from the start; Λ.3 a whole character leaves a thread alive
     * and not accepting, or an assertion stands before the accept. */
    PF_WHY_NULLABLE,
    PF_WHY_ASSERT_AT_START,
    PF_WHY_DEAD_START,
    PF_WHY_ALIVE_NOT_ACCEPT,
    PF_WHY_ASSERT_AFTER,
    /* D164 B3 `end_mark`'s L3 decline: a subroutine call re-enters a body with
     * another continuation, so no node is path-final for every caller. */
    PF_WHY_CALL,
    /* [KIT-VERIFY] U1 Z2 `span_facts`' declines (src/facts/kset.c): the
     * machine's language is a SUPERSET of the pattern's (`Nfa.erased`), or
     * its accepts carry D164 mark distances (a lowered `$` tail, whose bytes
     * lie past the match end); `nullable` and `dead-start` are Λ's. */
    PF_WHY_ERASED,
    PF_WHY_MARKED
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
    const struct Ast *root;  /* the tree sealed at the latest epoch */
    /* E1 structural, forced at `pcrec_facts_seal_e1`: the `PF_KIND_*` mask,
     * and whether the empty string is in the language. Neither has a deny. */
    unsigned  kinds;
    bool      nullable;
    /* [NULLABLE-ANCH] E1 structural, forced at the seal: the set of anchor
     * masks the empty paths carry (src/facts/widths.c), nonzero exactly where
     * `nullable`. No deny. Read as `empty_admits` (`pcrec_fact_empty_admits`). */
    unsigned  empty_masks;
    /* [OPT-ANCHOR-VM] E2 core: `PCREC_SANCH_*`; `PCREC_SANCH_NONE` under
     * `-fno-vm-anchor-bound`, deliberately indistinguishable from "nothing to
     * bound". The VM bounds its attempt loop on it; the DFA asserts its own,
     * independently derived answer agrees in the sound direction. */
    int       start_anchor;
    /* [START-SET] E2 core: the start set; no deny of its own (the hats' row
     * deny, `-fno-start-set`, never empties the fact). */
    StartSet  start_set;
    /* [OPT-REVEND] L1 E2 core: `PCREC_EPIN_*`, the end anchor every match
     * satisfies; no deny of its own (the reader rows carry theirs). */
    int       end_pin;
    /* [OPT-ENDWIN] E2 core: the end-anchor start window in BYTES, or -1 where
     * the analysis declines; -1 under `-fno-end-window`. Both emitters. Since
     * [OPT-REVEND] L1 a READER of `end_pin` (the width and the encoding over
     * the pin), so the two cannot drift. */
    long long end_window;
    /* D164 B3 E2 derived: the end mark's tails and whether lowering them
     * completes the pin (`EndMark`). No deny of its own: the reader row's
     * deny (`-fno-rev-end-onewalk`) never empties the fact. */
    EndMark   end_mark;
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
    /* [REQ-HANDOFF-L1] E2 derived: the landmark's K
     * (`pcrec_fact_req_landmark_maxoff`), -1 where there is no landmark. */
    long long req_landmark_maxoff;
    /* [OPT-K] E3 core, sealed on the `ENG_UNANCH` branch only: the k-set walk
     * over the wrapped forward NFA from its anchored start. The offset-k
     * selection (src/opt/prefix_k.c) reads it; no deny — each USE has its
     * row deny (`-fno-offset-skip`, `-fno-run-prefilter`). */
    KsetWalk  kset_walk;
    /* [OPT-LITSCAN] S1 E3 derived: the run's window pinned on the walk. No
     * deny of its own; a denied run (`len == 0`) pins nothing. */
    RunPin    run_pin;
    /* [START-LANDING] E3 core, sealed on the `ENG_UNANCH` branch only: the
     * one-character fact and the byte width interval over the wrapped NFA.
     * No deny of their own: each reader row (`landing`, `end-minus-width`)
     * carries its row deny. */
    LandChar  land_char;
    WidthIv   width;
    /* [KIT-VERIFY] U1 Z2 E3 core, sealed on the `ENG_UNANCH` branch only:
     * the span slice over the wrapped NFA (`MkLang`). No deny of its own:
     * its readers (the `cover` row, the FIND sites' `exact_len` statement)
     * state what it gives. */
    MkLang    span;
    PfWhy     why[PF_NFACTS];
    /* `--emit-facts`' FORCE LOOP (design §11.4, ruled Q10): true while it
     * asks the facts no pass asked, after the artifact is complete, and
     * `force_next` is the row it is on. `compile_driver`'s recovery point
     * tests `forcing` FIRST: a forced ask that fails marks that one fact
     * `absent` and the loop resumes at the next row, so the listing never
     * refuses a compile that succeeded. Both live here, in the heap `Job`,
     * because they cross that `longjmp`. */
    bool      forcing;
    int       force_next;
} PatFacts;

/* ---- the seals -------------------------------------------------------- */

/* Seals E1 over `root`, the STRUCTURAL tree, and derives both E1 facts on it
 * there and then. Called once per attempt, by `compile_driver`, after
 * `pcrec_callgraph_build`. */
void pcrec_facts_seal_e1(Ctx *cx, const struct Ast *root);

/* Seals E2 over `root`, the LOWERED tree: first re-derives the E1 facts on it
 * and refuses the compile (an internal error) if either disagrees with the
 * value sealed at E1 — the lowering-invariance cross-check (design §3) —
 * then records the tree and advances the epoch. Called once per attempt, by
 * `compile_driver`, after `pcrec_lower_enc`. */
void pcrec_facts_seal_e2(Ctx *cx, const struct Ast *root);

/* Seals E3 — the WRAPPED forward NFA, `Job.nfa` — and nothing else. Called
 * by `compile_driver` inside the `ENG_UNANCH` arm only, right after
 * `pcrec_nfa_wrap_unanchored` (design §3): the count-collapse ladder may
 * rebuild the machine before that point, and `ENG_ATTEMPT` never wraps it.
 * On every other route an E3 fact is not an error: its accessor returns the
 * empty value, status `absent`, with the route's decline reason. */
void pcrec_facts_seal_e3(Ctx *cx);

/* ---- the accessors ------------------------------------------------------ */

unsigned       pcrec_fact_kinds(Ctx *cx);        /* E1: the PF_KIND_* mask */
bool           pcrec_fact_nullable(Ctx *cx);     /* E1 */
/* E1: some empty match is not confined to a subject that is empty up to a
 * final newline — an empty path lacks a non-multiline start or end anchor.
 * False where the pattern is not nullable. */
bool           pcrec_fact_empty_admits(Ctx *cx);

int            pcrec_fact_start_anchor(Ctx *cx);
const StartSet *pcrec_fact_start_set(Ctx *cx);   /* E2 */
int            pcrec_fact_end_pin(Ctx *cx);        /* E2: PCREC_EPIN_* */
long long      pcrec_fact_end_window(Ctx *cx);
const EndMark *pcrec_fact_end_mark(Ctx *cx);      /* E2 */
const ReqSet  *pcrec_fact_req_set(Ctx *cx);
/* Both return `PatFacts.req_run`: the whole run is its core half, the
 * window its derived half, and each accessor answers for its own. */
const ReqRun  *pcrec_fact_req_whole_run(Ctx *cx);
const ReqRun  *pcrec_fact_req_run(Ctx *cx);
/* [MEMFN] R17-b' B3a THE PRESENCE STATEMENT's two reads (r17b_prime.md §4.1,
 * PR-5): the same facts and derivation as `pcrec_fact_req_set` and
 * `pcrec_fact_req_whole_run`, NOT a pass's ask, so `--emit-facts`' `used`
 * column stays today's (Q-WR-12, ruled: `req_set` is asked only where today
 * asks; the column flips with B3b's row move). Their one reader is
 * `req_pres_spans` (src/gen/emit_dfa.c), which STATES the unpicked spans to
 * the kit; no selection and no rendering reads what it states before B3b. */
const ReqSet  *pcrec_fact_req_set_stated(Ctx *cx);
const ReqRun  *pcrec_fact_req_whole_run_stated(Ctx *cx);
/* The same non-pass reads of the window and of `req_byte`, for the trace
 * build's pick shadow (`req_pick_shadow`): a check, not a pass, so the
 * trace build's `used` column is the default build's. */
const ReqRun  *pcrec_fact_req_run_stated(Ctx *cx);
int            pcrec_fact_req_byte_stated(Ctx *cx);
/* E2 derived: the window's `maxoff` where a run shipped, -1 where none
 * did ([K82]). `PCREC_W_UNBOUNDED` reads as "no bound". */
long long      pcrec_fact_req_run_maxoff(Ctx *cx);
int            pcrec_fact_req_byte(Ctx *cx);
/* E2 core: `ReqSet.maxoff` ([REQ-HANDOFF-L1]); the set it annotates. */
const ReqSet  *pcrec_fact_req_set_maxoff(Ctx *cx);
/* E2 derived ([REQ-HANDOFF-L1]): THE LANDMARK's K — the pre-check gate's
 * needle, whatever its length — the run window's `maxoff` where a run
 * shipped, else the `req_byte` member's; -1 where the gate has no needle.
 * `PCREC_W_UNBOUNDED` reads as "no bound". */
long long      pcrec_fact_req_landmark_maxoff(Ctx *cx);
const KsetWalk *pcrec_fact_kset_walk(Ctx *cx);   /* E3 */
const RunPin   *pcrec_fact_run_pin(Ctx *cx);     /* E3; its reader owes the kind gate */
const LandChar *pcrec_fact_land_char(Ctx *cx);   /* E3 [START-LANDING] */
const WidthIv  *pcrec_fact_width(Ctx *cx);       /* E3 [START-LANDING] */
const MkLang   *pcrec_fact_span(Ctx *cx);        /* E3 [KIT-VERIFY] U1 Z2 */

/* ---- the listing's force loop (design §11.4, ruled Q10) ----------------
 *
 * `pcrec_facts_force_all` asks every fact no pass asked — the SAME accessor
 * and derivation, never a recomputation beside it — marking them `used no`.
 * `compile_driver` calls it only AFTER the artifact and every stamp exist,
 * so a forced ask cannot move the artifact, and never past a seal the route
 * did not write. `pcrec_facts_force_failed` is the recovery point's one arm
 * for a forced ask that `longjmp`ed: that fact becomes `absent`
 * (`decline:force-failed`) and the loop moves on. */
void pcrec_facts_force_all(Ctx *cx);
void pcrec_facts_force_failed(Ctx *cx);

/* ---- the renderers (design §11.3 item 4, §11.5; ruled Q9) -------------
 *
 * Fact `f`'s value as TEXT, through its ONE renderer — the spelling the
 * artifact's fact-valued stamps (`<PREFIX>_REQ_BYTE`, `_REQ_RUN`,
 * `_END_WINDOW`, `_VM_START`) carry and `--emit-facts` prints, so a stamp and
 * the listing cannot disagree: there is one spelling of each value. Arena
 * text, valid for the compile.
 *
 * `pcrec_fact_stamp` ASKS `f` as a pass and renders it — the stamp sites'
 * one call. `pcrec_fact_render` reads the memo only and asks nothing: it is
 * the listing's, which must never change what the passes asked. */
const char *pcrec_fact_stamp(Ctx *cx, PfFactId f);
const char *pcrec_fact_render(Ctx *cx, PfFactId f);

#endif /* PCREC_FACTS_H */
