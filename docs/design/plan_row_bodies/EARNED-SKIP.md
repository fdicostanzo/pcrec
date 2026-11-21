# [EARNED-SKIP] body (filed 2026-11-09)

Frank 2026-11-09: "Do we send an index into the span that says don't bother proving beyond this point when we know we'll have to check it with engine"; "File the idea".

When a unit builds the skip: when a unit builds the skip: pcrec derives, per run, its PROOF EXTENT [lo, hi): the stretch over which the stated byte sets are EXACT (every admitted string is an attempt of that span: SUFFICIENT) and the outputs need no engine (no capture inside, no \K: OUTPUTS-DETERMINED); empty when nothing can be proved. A zero-width item whose pair condition the neighbouring sets do not decide (`\b` between [a-z] and [a-z]) ends the extent there; one the sets decide (`[a-z]\b[ ,.]`) does not. pcrec states the extent to the kit as a fact; the kit prices verifying up to hi as 'earns a skip' and beyond it as a filter only; pcrec reports the match when the kit's verified extent covers [lo, hi) = the whole attempt.

Kit side: memfn/docs/requests.md, R-38 Part C (unscheduled).

## Parked (Frank 2026-11-11 evening)

Wanted eventually; a bigger piece than intended for now. Raise the caps first ([COVER-CAP], set S3). Not in S4. Part C becomes one PRODUCER feeding [MATCH-KNOWN]'s compile-time walk of the engine program, not its own mechanism. Notes (a)-(e): [MATCH-KNOWN] row in docs/dev/plan.md and D194's 2026-11-11 evening addendum.

**2026-11-15 OWNER NOTE (Frank, on [COVER-CAP] design rev 4.1, which reads the exact stretch from the anchored DFA).**
His words: "reading dfa for the span is fine. In my goal of partial span proofs that means either rebuilding the dfa on
the remainder or editing out the proven span states." RECORD: for the partial case (an exact stretch that proves only
a fraction of the pattern, the engine running the rest), the engine side has two candidate forms: (a) build a DFA for
the REMAINDER of the pattern, or (b) take the existing DFA and EDIT OUT the states the proven stretch already walked.
Neither is designed or scheduled (this row stays PARKED); the note is the owner's statement of the end state's two
routes, for whoever designs it. See decisions D198 and docs/design/cover_cap.md (end-state section).

**2026-11-15 (manager, from [COVER-CAP] rev 5.1, review r13 F23/F24).** [COVER-CAP] stage 2
bounds the cover ROUTE by a per-compile width (`--window-search-width=N`, default measured): a
fixed-width pattern wider than the limit gets no cover and runs the engine for every position,
a CLIFF. The no-cliff form, "prove the first N positions, the engine finishes the rest", is
this row's proof extent read at the width limit, and it is where the cliff goes away (the
owner's 14:10 "1." names its two engine-side routes, recorded above). Status unchanged:
PARKED. Trigger unchanged (lookaround-as-run lands, then a bench cell where the engine's
finish is a measurable share), plus one: the owner answers [COVER-CAP]'s route-versus-stretch
question for the stretch.
