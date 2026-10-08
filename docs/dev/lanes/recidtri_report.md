# recidtri: triage of `run_recursion_identity.sh` REDs on main 77b6b37e (abi 66)

Lane recidtri (sonnet, 2026-10-08). Branch `lane/recidtri` from 77b6b37e.
Check-side fix only: one script (`tests/codegen/run_recursion_identity.sh`) and
its directory's CLAUDE.md. No `src/` change, no abi event, no spec hunk.

## Verdict

Both reds are STALE/INCORRECT CHECK, not a regression. Evidence below is from
a reproduction on the unmodified gate (the poss-stamped population, 106 of
3,961 call-free patterns, on the default and `--engine=vm` axes), then the
fixed gate, then three failing-direction plants.

| FAIL line | count | class | evidence |
|---|---|---|---|
| "(A) N call-free patterns emit a DIFFERENT PROGRAM REGION ... possarms=0 stamped, but denying them does NOT restore the pinned region" | 10 (default axis) | stale check: the bucket cannot reach an engine-selecting arm | Arm A (`-fno-poss-ctx-follow`) is ENGINE-SELECTING (tuning.md section 2.44, kept in `rx_info.flags`). On the default axis it moves these 10 patterns from the VM the pin compiles to the DFA (possfin's "10 vm->dfa flips on post-r21 rows"; ruled intended by the manager at possland2). A DFA artifact has no `RX_VM_POSS_ARMS` (VM-only), so `poss_a` is empty, the stamped excuse is skipped, and the context-node set (`-fno-ctx-node ...`) omitted the arms. Measured per pattern: context set alone restores 0/10; the same set plus both arm denies restores 10/10. |
| "(A) N artifacts stamp RX_VM_POSS_ARMS nonzero and yet are BYTE-IDENTICAL to their own both-arms-denied build" | 5 (default), 16 (vm) | incorrect check: asserts more than the stamp promises | The stamp is "an arm was NEEDED for some positive possessify verdict" (match_api.md section 6.3). All 16 patterns carry a SOURCE possessive/atomic loop (`\w++\b`, `(?>\w+)\b`, `(a?)x++\1\b`, ...). A verdict on such a loop marks nothing; its one consumer is the free discharge, which only moves the route where the route is free. Where it does, the effect is visible in `RX_ENGINE_WHY` (11 of 16 on vm: armed `--engine=vm`, denied `possessive quantifier ...`); where the route is VM-forced by a capture or backreference (5 on default and vm), the artifacts differ only in the stamp, `.flags` (the kept bit) and at most `RX_VM_RESEED`, nothing in the program region. The stamp is true and the program is unchanged. |

The two (4 + 1) other lines nullanch1 may have counted ("POSS_ARMS stamped but
deny changes nothing" x5 plus "10 call-free region differs" = the 5 FAIL lines
across the four axes) are these two messages repeated per axis.

## Did possland2's landing validation run this gate? No.

The gate is `make test-recursion-identity`, on demand: it is not in
`TEST_SECTIONS` (verified against the Makefile), only the battery's
`recidentity` stage (D136). possbuild's report line says "Its run is in `make
test` (OWED)", which could not be true; the slot chain (possbuild addendum 2:
make test, mech x10, composition, census, test-axes) never named it, and
possland2 merged on `make test` 805 s green. So the bucket's logic and the
`POSS_PATTERNS` manifest landed without a single complete run of the script
they live in. learnings section 3.ab applies verbatim: a check never run to
completion rots (here, it was wrong on its first run). The mech `recidentity`
arm cannot cover it either (scratch trees there have no `.git`; the gate SKIPs
loudly, varland finding 7).

## The fix

1. **Engine-flip bucket** (`poss-arm-a-engine-flip-moved`). In the
   context-node branch, after the existing `-fno-ctx-node -fno-alt-island
   -fno-cls-fold` set fails to restore the pin, try it with
   `-fno-poss-ctx-follow -fno-poss-bref-first` added. Second, never folded
   into the older sets, so every older bucket keeps its exact meaning and
   nothing is credited to this one that they explain. Non-vacuity is a NAMED
   manifest, `POSS_FLIP_PATTERNS` (the 10), each of which must land in the
   bucket on the default axis; the count must be 0 on `--engine=vm` (engine
   forced on both sides).
2. **Stamped-direction converse** restated at the stamp's own definition. An
   unchanged region under both-arms-denied is excused ONLY for a pattern whose
   TEXT says a possessive/atomic construct (`POSSRC_POP`, a new independent
   text census in the existing python block, escape pairs collapsed so `\++`
   is not a possessive). The excuse is a counted population
   (`poss-arms-stamped-on-source-possessive`), bounded above by its census and
   floored at 8 on the vm axis (measured 16): if the stamp ever becomes
   consequence-aware the floor goes red and the excuse is to be deleted. A
   self-check refuses a `POSS_PATTERNS` member that the excuse could reach, so
   the manifest's three witnesses keep the strict (region must move) claim.
3. Summary line gains `poss-arms-stamped-on-source-possessive=` and
   `poss-arm-a-engine-flip-moved=`.

### Failing direction (poss population, default + vm axes)

| plant | result |
|---|---|
| arms removed from the flip set | `differing=10`; "10 of the POSS_FLIP_PATTERNS manifest no longer land in the arm-A engine-flip bucket" |
| `POSSRC_POP` emptied | 5 (default) and 16 (vm) "STAMPED ... BYTE-IDENTICAL" FAILs, plus the excuse floor |
| both-arms-denied build replaced by no deny at all | 18 (default) and 75 (vm) FAILs (the excuse reaches only 7 and 18 of them) |

## Finding for the manager (not fixed; design-level, optional)

The stamp counts verdicts on loops the source already made possessive/atomic.
That is its documented meaning, but on a VM-forced pattern the bit then reports
an arm "needed" for a verdict that cannot change any artifact byte
(`(a?)x++\1\b` stamps `0x6u` and differs from its denied build only in the
stamp and `.flags`). Making the stamp consequence-aware (count only verdicts
that mark a new loop, or discharge one on a free route) would be a compiler
change with an abi/stamp ritual; per the brief I stopped at the classification
and did not touch `src/`. The floor in fix 2 makes the gate notice the day
this happens.

## Validation

COMPLETE. The full gate, unmodified committed script (`bash
tests/codegen/run_recursion_identity.sh` at lane/recidtri 677caf74, this
worktree, after lane advnorm's DONE; log `build/recid_full.log`, gitignored),
ended `checks passed: 16`, `checks failed: 0`. Per-axis population counters
(from the (A) lines; (B) whole-file differing=0 on all four axes):

| axis | (A) same / differing | poss-arms-moved | stamped-on-source-possessive | arm-A engine-flip | stamped-but-deny-noop | unstamped-but-deny-moves |
|---|---|---|---|---|---|---|
| default | 2339 / 0 | 20 | 5 | 10 (manifest, all 10 asserted) | 0 | 0 |
| vm | 2094 / 0 | 81 | 16 (floor 8) | 0 (asserted 0) | 0 | 0 |
| noprefilter | 2340 / 0 | 20 | 5 | 10 | 0 | 0 |
| nocaptures | 2399 / 0 | 18 | 4 | 11 | 0 | 0 |

Corpus 4,377 patterns: 416 call-bearing, 3,961 call-free, source-
possessive/atomic text census 311. nocaptures flips 11 (the 10 plus one
pattern whose capture group, absent under `--no-captures`, no longer forces
the VM); it is printed, not asserted, and the 10-pattern manifest is asserted
on `default` only.

Before the fix (same script at 77b6b37e, poss-stamped sub-population only,
default + vm): default `differing=10` plus 5 converse FAILs, vm 16 converse
FAILs.

Not run here: the mech `recidentity` arm (no `.git` in scratch trees, SKIPs
loudly by design), `make test` (this gate is not in it; no change outside
`tests/codegen/` was made).
