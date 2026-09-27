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

/* [OPT-ANCHOR-VM] THE START ANCHOR — at which positions can a match BEGIN?
 * `PCREC_SANCH_*` and the renderer `pcrec_start_anchor_name` stay with the
 * consumers in `core/internal.h`. */
int pcrec_start_anchor(const Ast *root);             /* src/facts/startanch.c */

/* [OPT-ENDWIN] THE END-ANCHOR START WINDOW — a match may begin only in the
 * last `W` bytes of the subject, or `-1` where the analysis declines (the
 * four structural declines are in src/facts/endwin.c's own header, which also
 * carries the soundness argument every emitter site rests on). BYTES, and
 * the encoding decline is what makes that true. `e`, the encoding
 * DESCRIPTOR, is a declared input (design §4.2.2 carve-out (d)). */
long long pcrec_end_window(const PcrecEnc *e, const Ast *root);
                                                     /* src/facts/endwin.c */

/* [OPT-REQBYTE] + [OPT-REQPOS] tier 2b — THE NECESSARY BYTE AND THE NECESSARY
 * LITERAL RUN, from ONE walk over the lowered tree. Returns the byte every
 * match must contain, or -1 where the analysis found none (which DISABLES the
 * check and is always sound), and writes the run into `*run` (`len == 0` where
 * it found none). src/opt/reqbyte.c's header carries the whole account: why
 * the whole window and not PCRE2's "other than at its start", why the analysis
 * produces a SET and a RUN, why the member it picks is the argmin of a
 * frequency prior under the `byte` encoding and the rightmost elsewhere, and
 * why a lookaround's body is a correctness decline.
 *
 * `run_ok` is [OPT-REQPOS]'s own axis, threaded rather than read here, because
 * the BYTE the artifact emits depends on whether the run ships: with a run the
 * `memchr` is the run loop's and tests the run's scan member, without one it
 * tests the whole set's own pick. Both answers come out of this one call so
 * they cannot be chosen in two places and disagree. `cx` is read for the
 * ENCODING alone (the prior is a fact about a corpus under one). `set`
 * receives the whole necessary set the returned byte was picked from ([K65]),
 * empty exactly when the return is -1. */
int pcrec_req_byte(Ctx *cx, const Ast *root, bool run_ok, ReqRun *run,
                   ReqSet *set);
                                                      /* src/opt/reqbyte.c */

#endif /* PCREC_FACTS_DERIVE_H */
