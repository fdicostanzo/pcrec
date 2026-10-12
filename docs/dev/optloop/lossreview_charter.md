# [LOSS-REVIEW] charter (Frank, 2026-10-11, session 107)

Frank: "Before deciding priorities after current items complete, review all the
losing patterns (plus any items we have that need it) and assess / measure
why. What's the biggest slow down. What else could be done. Then look for
general fixes to them, and assess them. Prioritize fixes to existing opts."

This is the input to the next [OPTLOOP] round's selection. Non-SIMD scope
(pcrec's shipped default, `-fmemfn-simd` OFF); SIMD-attributable cells are
listed, not attributed.

## Population

1. Every trailing cell in `gapreport_2026-10-11.md` (80 vs pcre2-jit, 87 vs
   the best non-SIMD peer; rust-only and SCAN-SIMD/WIDE-ALT cells listed only).
2. Internal items that need the same treatment: K103 (rev-end entry floor,
   litrun whole rows +3-8%), K104 (github-pat class tail), `tail-dotstar-txt`
   search-short x1.146 (REVEND), syntax `bak-2` x1.55 (the only grower),
   hcolon entry-only +13% (rlhbuild_report.md open item 4), hcolon_in x1.5 on
   colon-dense text (K105 to file), DENSE (15 cells <= x1.68) and BCLS.

## Phase 1 — attribution (per cell, then per cause)

For each cell: the route (stamps: engine, start form, prefilter, scan,
rungs), WHERE the time goes, and WHY the peer is faster.
- Load-insensitive evidence first (valid while the box is busy): emitted C
  and `--emit-facts`, the walk_survey per-phase subject-load instrument
  (`studies/walk_survey/`, loads per phase per subject byte), instruction
  counts (`perf stat -e instructions` if available, else gcc `-S` hot-loop
  reads; NOTE on this box `perf_event_paranoid`=4 blocks unprivileged perf and
  valgrind is not installed — changing either is system config, Frank's call),
  and what the peer does (pcre2-interp / re2 / onig mechanism,
  from their documented algorithms, cited).
- Timing (hand twins: today vs the candidate change) only in a QUIET slot,
  on targeted hardware, interleaved, scratch tier, answer-checked. Name the
  twin and its command if the slot is not yet available.
- Per cell, one line: dominant cost bucket, ns lost (bench number), the
  mechanism, and whether an EXISTING opt was meant to cover it but declined,
  misfired or was denied (name the row/predicate and the decline reason).

Rank causes by TOTAL loss (sum over cells, both caps/nocaps, all regimes),
not by worst ratio.

## Phase 2 — general fixes

Per cause: (a) FIX-EXISTING first — an existing opt widened, its decline
predicate corrected, its cost term fixed, or a dispersed family unified;
(b) only then a new general mechanism (never a per-pattern special case,
D75 / memory general-mechanisms). Each candidate: reach (cells and corpus
population it moves), expected gain from the phase-1 numbers, risk, remodel
overlap ([REQ-HANDOFF-L1], [PRIOR-COST-UNIFY]), and the D77 trigger it meets.

## Phase 3 — assessment

A D6 panel on the phase-2 candidates (lenses: refute the attribution; the
general form + unlocks; sibling-of-a-family), then a ranked list to Frank
with fix-existing items first.
