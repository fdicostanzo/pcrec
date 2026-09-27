/* src/facts/facts_derive.h — THE FACTS-PRIVATE header: every pattern-fact
 * DERIVATION's declaration ([PATFACTS], docs/design/patfacts/design.md
 * §4.2.2 carve-out (a)).
 *
 * WHO MAY INCLUDE IT is a checked rule, not a convention: the files under
 * `src/facts/` plus each OWNER file `src/facts/facts.def` names, and no
 * other. A consumer reads a fact through `facts.h`'s accessor; calling a
 * derivation directly would be a second, unmemoized, undenied path to the
 * same answer — the parallel-mechanism shape the record exists to remove.
 * `tests/codegen/run_facts_checks.sh` compares the set of includers of this
 * header against the list generated from `facts.def`, and joins the link
 * symbols so a hand `extern` that bypasses the header fails too.
 *
 * Step 3.0a moves the E2 derivations' declarations here out of
 * `core/internal.h`, before anything else moves, so every later relocation
 * is checkable. */
#ifndef PCREC_FACTS_DERIVE_H
#define PCREC_FACTS_DERIVE_H

#include "core/internal.h"
#include "enc/enc.h"

/* THE E1 FACTS, derived on the STRUCTURAL tree at `pcrec_facts_seal_e1` and
 * re-derived on the lowered one at `pcrec_facts_seal_e2` as the invariance
 * cross-check (design §3). Pure functions of the tree. */
unsigned pcrec_pattern_kinds(const Ast *root);       /* src/facts/kinds.c */
bool     pcrec_pattern_nullable(const Ast *root);    /* src/facts/widths.c */

/* [OPT-ANCHOR-VM] THE START ANCHOR — at which positions can a match BEGIN?
 * `PCREC_SANCH_*` and the renderer `pcrec_start_anchor_name` stay with the
 * consumers in `core/internal.h`. */
int pcrec_start_anchor(const Ast *root);             /* src/facts/startanch.c */

/* [OPT-ENDWIN] THE END-ANCHOR START WINDOW — a match may begin only in the
 * last `W` bytes of the subject, or `-1` where the analysis declines (the
 * four structural declines are in src/facts/endwin.c's own header, which also
 * carries the soundness argument every emitter site rests on). BYTES, and
 * the encoding decline is what makes that true. `e`, the encoding
 * DESCRIPTOR, is a declared input (design §4.2.2 carve-out (d)). `*why`
 * receives which decline answered (`PF_WHY_ENC_MULTIBYTE` and the three
 * structural ones), or `PF_WHY_NONE` with a window — the reason is the
 * derivation's to report, never the listing's to infer from `-1`. */
long long pcrec_end_window(const PcrecEnc *e, const Ast *root, PfWhyCode *why);
                                                     /* src/facts/endwin.c */

/* ---- [OPT-REQBYTE] + [OPT-REQPOS] tier 2b: the necessary set and run ------
 *
 * The WALK's output vocabulary, shared by the walk (`src/facts/req.c`, the
 * CORE facts `req_set`/`req_whole_run`) and the pick readers
 * (`src/core/findings.c`, read by the DERIVED facts `req_run`/`req_byte`
 * below). The lattice
 * that builds them stays `static` in req.c. */

/* A set of necessary bytes plus the member the emitter will use. `pick` is
 * -1 exactly when the set is empty, and is always a member of the set when it
 * is not — an invariant every operation below restores rather than assumes. */
typedef struct { unsigned char bits[32]; int pick; } RbSet;

/* A necessary CONTIGUOUS run, bounded so the walk's per-frame state cannot
 * grow with the pattern (`PCREC_MAX_REQ_RUN_SCAN`'s limits.def row says why).
 *
 * `trunc` means the real run is LONGER than the `n` bytes stored, and every
 * truncation is sound in the only direction that matters: a contiguous
 * substring of a necessary contiguous run is itself one. What differs by ROLE
 * is which END is kept, and the two append helpers below carry that as a
 * stated precondition rather than as a convention — a HEAD keeps its first
 * bytes (so its first byte is still the match's first), a TAIL keeps its last
 * (so its last byte is still the match's last), and `best` keeps whichever
 * the operation that built it produced. */
typedef struct { unsigned char bytes[PCREC_MAX_REQ_RUN_SCAN]; int n; bool trunc; } RbRun;

static inline bool rb_has(const RbSet *s, int b)
{
    return b >= 0 && (s->bits[b >> 3] & (unsigned char)(1u << (b & 7))) != 0;
}

/* THE CORE FACTS from ONE walk of the lowered tree: the whole necessary set
 * (with its threaded rightmost member) and the longest guaranteed contiguous
 * run. src/facts/req.c's header carries the whole account: why the whole
 * window and not PCRE2's "other than at its start", why a SET and a RUN, and
 * why a lookaround's body is a correctness decline. */
void pcrec_req_walk(const Ast *root, RbSet *set, RbRun *run);
                                                        /* src/facts/req.c */

/* THE DERIVED FACTS, speed choices over the core ones, composed in
 * src/facts/req.c from the rate readers in src/core/findings.c (whose header
 * says why each member choice is the argmin of a frequency prior under the
 * `byte` encoding and the rightmost elsewhere). `pcrec_req_window` fills
 * `run`'s window (`bytes`/`len`/`idx`/`at`) from its whole run;
 * `pcrec_req_pick` answers the byte the emitted `memchr` tests. Each asks
 * the byte-rate accessor (`pcrec_find_byte_rate`) once, first, and hands its
 * answer to the readers untested. `*why` receives the rate rule that answered —
 * `PF_WHY_RATE_BUILTIN` (the shipped prior) or `PF_WHY_RATE_NONE` (its NONE
 * answer, the rightmost member) — or `PF_WHY_NONE` where no member was
 * chosen (no window; an empty set). */
void pcrec_req_window(Ctx *cx, ReqRun *run, PfWhyCode *why);
                                                        /* src/facts/req.c */
int  pcrec_req_pick(Ctx *cx, const ReqSet *set, const ReqRun *run,
                    PfWhyCode *why);                    /* src/facts/req.c */

/* [OPT-K] THE K-SET WALK over the wrapped forward NFA from its anchored start
 * (src/facts/kset.c's header: why the anchored start, why it is sound). Reads
 * the NFA alone; scratch from `cx`'s arena. */
void pcrec_kset_walk(Ctx *cx, const Nfa *nfa, KsetWalk *o);
                                                        /* src/facts/kset.c */

#endif /* PCREC_FACTS_DERIVE_H */
