# NOTES — history, lessons and rationale for this directory

Not auto-injected. CLAUDE.md is the orientation guide; text moved here verbatim from it (2026-10-22, size limit) lives below.

## Rationale sections (oracle rule, U9, batching, M6.4.4 shape, asserted populations)

## THE ORACLE RULE, and why the divergences were DETECTED rather than declared

Every expectation was produced by libpcre2 10.46 through
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`, and python3 `re`
was driven over the SAME cells in the same pass. A block carries
`# pcre2-only` exactly where python disagreed or could not compile the pattern
— measured, never assumed. **13 of 729 generated cells diverge, and they are
EXACTLY the four families the design's Appendix B.3 names**, which is an
independent confirmation of that table rather than a transcription of it:

- `\K` and `\G` — python cannot express them at all;
- the BRACE possessive over a two-exit body — python cuts PER ITERATION and
  PCRE2 cuts at the GROUP EXIT, so `(?:a|ab){2}+` on "aba" is (0,3) in PCRE2
  and NO MATCH in python, while `(?:a|ab)*+` on "aba" is (0,1) in BOTH. The
  divergence runs in the dangerous direction and the `*+`/`++` controls beside
  it are what make it a family rather than a one-off;
- U9 — see below;
- scoped `(?i)` inside a group — python rejects the pattern outright.

## U9 IS NOT IN THIS DIRECTORY, AND THAT IS A RULING SOMEBODY OWES

`tests/known_fail/u9_atomic.rxt` holds the two U9 patterns with LIBPCRE2's
answer, which pcrec does not reproduce: pcrec agrees with python `re` and with
a hand derivation. D26 makes PCRE2 the source of truth, and
`docs/dev/upstream_issues.md` U9 classifies the divergence as PCRE2-SIDE and
names THIS MODULE LANDING as the event that makes it reachable ("pcrec refuses
the spelling today, module `atomic-groups`"). The implementation lane is not
the place to decide which wins, so the ratchet holds it: the cells stay, they
stay loud, and if pcrec is ever changed to reproduce U9 the ratchet FIRES.
The three CONTROLS that each drop one of U9's conjuncts are live and green in
possessive.rxt section 9.

## THE SWEEP HAD TO BE BATCHED, and the number is the argument

`run_atomic_diff.sh`'s first form spawned one `pcre2_oracle` and three
`fuzz_driver` processes PER CELL, over ~120,000 cells. MEASURED: **44 cells per
minute — about eleven hours for one run**, which is not a test anyone runs and
certainly not a sabotage-matrix arm. The oracle side is now ONE python process
(`atomic_oracle.py`, driving the same libpcre2 through the project's committed
ctypes binding) and the pcrec side is one process per (pattern, arm) reading
cells on stdin (`atomic_batch.c`): **~60 seconds**, same cells, same comparison.

`atomic_batch.c` is deliberately NOT a replacement for
`tests/fuzz/fuzz_driver.c` — that file is the fuzzer's own template, compiled
ONCE and linked against every pattern's `gen.o`, which is why it cannot batch.

Because the comparison is POSITIONAL, both batch programs treat an unreadable
input line as a HARD failure, and the driver's output LINE COUNT is asserted
per arm. A driver that dropped a line would shift every later cell against the
wrong answer — the one failure mode the batched shape introduces.

## THE SHAPE THIS DIRECTORY DID NOT HAVE, AND WHAT IT COST ([M6.4.4])

The blinded D27 corpus found `(?:aa|a)++ab` answering (0,4) on "aaab" where
libpcre2 10.46 and python3 `re` both say NO MATCH — in every mode, on every
frames rung. **The defect SHIPPED**: live in main from [M6.4.2]'s merge
(`69f3b93`) to [M6.4.4], with 748 corpus cases and a 39,326-cell x 3-arm
differential green over it the whole time.

ROOT CAUSE, one sentence: `vm_atomic` emitted the atomic body with the
caller's follow-min still in force, and the possessive rungs turn that number
into a loop bound — they end the loop at the first position where "one more
iteration PLUS THE FOLLOW" does not fit. For an UNCUT loop that is
answer-preserving because the exit it jumps to is one a retreat could reach
anyway; under a cut there is no retreat, so the loop stops where the greedy
run would have walked on and the follow matches there. The fix scopes
`v->fmin`/`v->fdyn` to zero across the whole atomic body: THE FOLLOW DOES NOT
CROSS A CUT.

**WHY EVERY CELL HERE WAS GREEN ON IT, which is the part to keep.** Every
`cut` pattern in this directory and in `run_atomic_diff.sh` had a follow whose
first byte cannot also start a body iteration — `(?>a|ab)c`, `(?:a|ab)++c`,
`(?>a*)b`. Under that disjointness the early exit lands on a byte the loop
could never have eaten, the follow fails there too, and NO ANSWER MOVES. The
alphabet was uniform in a way nobody had noticed, which is D27's own thesis
arriving a second time: tests derived from the implementation inherit the
implementer's shapes, and the shape absent here was absent from the design's
own examples too.

THE FAMILY THAT SEES IT needs BOTH halves: a **two-exit body** (so the loop's
stopping position is a CHOICE rather than a byte-determined fact) and an
**overlapping follow at least two bytes wide** (so the early exit lands
somewhere the follow can actually match). It is class `cut2` in
`run_atomic_diff.sh` — 30 patterns, all five possessive rungs (the coverage is
ASSERTED from the artifacts' own `RX_VM_RUNGS`, ORed to 0x1f, never inferred
from the quantifier spelling), both preferences, its own non-vacuity floor of
18 (measured 30/30). The floor is kept SEPARATE from the `cut` family's on
purpose: the `cut` rows clear 15 by themselves, so a merged counter would
have stayed green with this entire family answering its uncut twin — which is
the state the tree was actually in.

Sabotage row **S101** re-introduces it, and is the only row in the matrix
whose defect shipped. Validated: applies at 1 site, builds, reproduces
`(?:aa|a)++ab` = (0,4) on "aaab", and takes this directory's differential to
2,484 disagreeing cells plus 4 follow-barrier failures — 11 checks red where
the fixed tree is 8 green.

## EVERY POPULATION IS ASSERTED, NEVER PRINTED

A sweep that quietly generated nothing prints the same silence as one that
agreed everywhere, and this project's record is full of that shape. Each
section ends in a floor its own run must clear, and the sharpest is the
NON-VACUITY floor: the cut must MEASURABLY change the answer on at least 15 of
the cut patterns, measured against each one's two-byte UNCUT twin (`(?>` ->
`(?:`, a possessive `+` dropped) rather than inferred from the pattern's shape.
Without it the whole sweep would be green on a compiler that lowered the group
by ignoring the atomicity — which is the trap `src/parse/registry.c`'s own row
comment has warned about since before there was a producer, and sabotage row
S91.
