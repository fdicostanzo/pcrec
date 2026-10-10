# k68fix — K68: `rx_info.flags` leaves deny bits 28/29/30 unmasked

Branch `lane/k68fix`, from `lane/reqrunenc2` (abi 38). 2026-09-26, sonnet.

## What K68 was

`emit_info_def`'s `strategy_denials` mask (`src/gen/emit_dfa.c`) omitted
the three [OPTLOOP.1] batch-1 whole-window pre-check deny bits —
`PCREC_NO_VM_ANCHOR_BOUND` (28), `PCREC_NO_END_WINDOW` (29),
`PCREC_NO_REQ_BYTE` (30) — so each moved five bytes of the emitted
`rx_info.flags` on EVERY artifact, including ones the flag cannot act on.
This is the identical defect the `-fno-prefilter-collapse` comment (bit
19) records as measured; the omission was deferred "to their own
delivery" at batch-1's own landing and never taken up until now. Found by
pcrec-bench re-pinning I-111, fact-found by lane `bit30`, filed and
scheduled by Frank as K68, fixed on top of `lane/reqrunenc2` so the bench
re-pins once (I-112).

## The fix

All three bits joined the mask, the same shape as every other masked bit
(deny-only, answer-identity-preserving). `lib/pcrec.h`'s comments on bits
28-30 each gained a "masked out of `rx_info.flags` ... [K68] (FIXED)"
paragraph matching the convention every other masked bit already states.

Verified against the repro at `ec79d98c` (router-prefix-order,
`/user|/users`): baseline `.flags = 2`; before the fix, 1073741826 under
`-fno-req-byte`, 536870914 under `-fno-end-window`, 268435458 under
`-fno-vm-anchor-bound`; after the fix, `.flags = 2` under all three.

## The abi ritual (38 -> 39)

- `src/gen/emit_dfa.c:51` — `PCREC_ARTIFACT_ABI` 38 -> 39.
- `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT=39`; the narrative
  string gains its own clause for this bump (copied FROM `match_api.md`
  docs/dev/history/abi_changelog.md per D76 addendum, not authored twice).
- `docs/dev/history/abi_changelog.md` — new change-log entry, "gap-free from 2 to
  39".
- `tests/codegen/run_recursion_identity.sh` — (B) FILEPIN re-pinned to
  `b255027f` (this lane's own last `src/`-touching commit — the mask fix
  + abi bump landed together). Comparison (A) untouched: the mask states
  a reflection-surface property that sits above `prog_region()`'s
  `goto <p>_L0;` start, so no PROGRAM byte moves.
- `docs/spec/tuning.md` §2.27 — one sentence cross-referencing §2.30:
  denying `PCREC_NO_REQ_BYTE` (bit 30) also zeroes `Job.req_run`, so
  §2.30's run-pinned `dfa_pfs[]` rows have no pin to test
  (`docs/design/litscan_s1.md` §1.1 invariant 2).

**Every abi-39-reader found by grep** (the whole tree, both `38`-as-current
and `ABI_EXPECT=38` forms): the four sites above are the complete list.
No other file asserted the numeric value 38 as current; every remaining
`38` in the tree is a historical `37 -> 38`/`"was 38"` citation, left
alone.

## Re-pinning the old unmasked `.flags` value

**None existed.** Grepped the whole tree for the pre-fix literal values
(`1073741824`/`536870912`/`268435456` and their router-prefix-order
combined forms `1073741826`/`536870914`/`268435458`): zero hits outside
this lane's own new comments. `run_prechecks.sh`'s §1.2/§2.2/§3.2 "denial
leaves no trace" sections (the closest candidates the brief named) assert
only the STAMP and the emitted TEXT, never `rx_info.flags` as a number —
they pass unmodified (292/0, then 301/0 once §6 is added). This is
consistent with K68 itself: the defect was invisible to pcrec's own suite
and was found only by pcrec-bench's external reflection-surface check.

## The guard: `run_prechecks.sh` §6

A new section asserting `rx_info.flags` is byte-identical to baseline
under each of the three deny bits, on three witnesses chosen so the flag
CANNOT act on most of them:

- `/user|/users` (K68's own repro): no `^`/`\A`/`\G`, no `$`/`\Z`/`\z`, so
  `-fno-vm-anchor-bound` and `-fno-end-window` leaked even though neither
  analysis had anything to act on; `-fno-req-byte` was the one that
  genuinely fires here.
- `^abc --engine=vm`: engages `PCREC_NO_VM_ANCHOR_BOUND` for real.
- `abc$`: engages `PCREC_NO_END_WINDOW` for real.

301/301 pass on the fixed tree. **Validated in the failing direction**:
reverting the mask (a scratch `0ULL;` in place of the three bits, rebuilt,
run, reverted) reproduces the exact pre-fix values
(268435456/536870912/1073741824) and fails exactly the 9 new §6 rows,
with every other section (292 checks) unaffected — the localization the
brief's "look for an existing check first" step needed: no existing
"denials masked" check covered these three bits (the closest analogues,
S65/S67's per-family flags-numeric-read shape, live in `prefilter`'s and
`altcls`' own test files and never touched batch-1's bits).

## Sabotage S295

`tests/mech/sabotages/S295_vm_anchor_bound_flags_leak.sh`: drops
`PCREC_NO_VM_ANCHOR_BOUND` back out of the mask (one of the three, the
S65/S67 granularity). `SAB_SUITES="prechecks harness"`; `harness` is
EXPECTED GREEN (the leak moves no answer, S263's own precedent for a
plant with no answer-level detector); `prechecks` is the sole detector,
via §6. Carries a `[MECH-REACH]` probe confirming the mask mechanism
still applies to this bit on the clean tree (a denied and an undenied
build of the same witness read the same `.flags`).

**NOT YET RUN through `run_sabotage_matrix.sh`** — queued in the
detached validation chain below (box rule).

## Box rule compliance

The heavy validation chain for `lane/reqrunenc2` (`make test` then
`make test-recursion-identity`) was still running for this lane's whole
working period. All work above was done with only `make`, `make strict`,
and the two fast codegen scripts (`run_prechecks.sh`, `run_codegen_tests.sh`),
per the box rule.

A single detached script, `/tmp/k68fix_chain.sh` (launched, `nohup … &
disown`), polls `/tmp/reqrunenc2_make_test.log` for `MT EXIT=` AND
`/tmp/reqrunenc2_recid.log` for `RECID EXIT=` (30 s interval), then runs,
serially:

1. `make strict CC=gcc-16` -> `/tmp/k68fix_strict.log`
2. `make test CC=gcc-16` (timeout 9000s) -> `/tmp/k68fix_test.log`,
   trailer line `K68FIX TEST EXIT=`
3. `make test-recursion-identity CC=gcc-16` (timeout 3600s) ->
   `/tmp/k68fix_recid.log`, trailer line `K68FIX RECID EXIT=`
4. `bash tests/mech/run_sabotage_matrix.sh S295` ->
   `/tmp/k68fix_s295.log`, trailer line `K68FIX S295 EXIT=`

Progress/completion markers: `/tmp/k68fix_chain.log`, final line
`K68FIX CHAIN: ALL DONE at <date>` when everything has finished.

## OWED at hand-off

- `make strict`/`make test`/`make test-recursion-identity` numbers for
  THIS lane's own tree (already spot-verified clean via `make strict` in
  the foreground above; the detached run re-confirms and adds the full
  suite + recursion-identity numbers).
- `bash tests/mech/run_sabotage_matrix.sh S295` DETECTED/UNDETECTED
  verdict.
- Verdict reading is make's `*** [test-X] Error` lines (never "sections
  ran" or a `FAIL:` grep) per the house rule.

## Delivered without validation gaps

- The mask fix itself: verified against the exact repro, both directions
  (present and reverted).
- The abi ritual: `make` (plain build) + `make strict` + both fast
  codegen scripts, green, on the final committed tree.
- The guard: validated in the failing direction, not merely written.
- `git status --short` clean on the final tree; every commit builds and
  passes `make strict` at that point.

## Commits (in order)

1. `b255027f` — the flags-mask fix + abi ritual (bump 38 -> 39).
2. `885aeb81` — abi ritual docs (docs/dev/history/abi_changelog.md, ABI_EXPECT, tuning.md
   §2.27 cross-ref).
3. `9d0d3597`, `c5d3e155` — cherry-picked from `main` (K68's own filing/
   scheduling commits, docs-only, needed because `lane/reqrunenc2` branches
   off before they landed on `main`).
4. `b4fc02e5` — re-pin `run_recursion_identity.sh` (B) to `b255027f`.
5. `d81515c6` — the guard (§6) + sabotage S295 + CLAUDE.md entries.
6. `bf17adc3` — `known_issues.md` K68 -> FIXED-pending-merge.
