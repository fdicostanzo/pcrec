# reqvm1 — [REQRUN-VM] build: the required-run handoff and re-entry on both VM routes

Lane reqvm1 (opus), 2026-10-27, worktree `worktrees/reqvm1`, branch
`lane/reqvm1` from main 13b7bb38c. Frank's go 2026-10-27 ("Yes go both
halves."), with the one-way give-up movement on the VM-only half accepted.
Rulings file: `(none yet)` at every checkpoint.

## Summary

- **Both halves built, at ONE site.** The handoff's existing PRE site, entry
  and re-entry move are reused. There is no parallel mechanism and no new
  flag bit. `-fno-req-handoff` (bit 46) denies every new row.
  - **VM hybrid (bench subst case 2).** NEXT's `handoff` prefilter row now
    also applies inside the hybrid's inlined prefilter. The forward scan
    re-enters the handoff at each restart. The pre-check's site is defined
    above the prefilter, and the VM search loop reuses it. Answer-identical
    and give-up-preserving: the prefilter's answers, and so the VM's
    attempts, do not change.
  - **VM-only (bench subst case 7).** Two new FIRST rows of the `req-use`
    table: `handoff-attempts` (entry plus a re-entry after each failed
    attempt) and `handoff-attempts-entry` (entry only). The LANDMARK is the
    necessary run's WHOLE run, never the window pick, and `K` is the whole
    run's `whole_maxoff`. Answer-identical. Give-ups move one way only: a
    deny-arm give-up may become the unbounded answer, never the reverse.
- **Measured (instructions:u, subst on `acc-main`, output sha256 identical to
  the bench expectations):**
  - case 2: 1,273.9M -> 791.0M (x1.61). subtri's twin 2b is 783.8M.
  - case 7: 3,295.1M -> 1,304.9M (x2.53). Twin 7a is 922.7M; the gap is a
    redundant window re-ask per re-find (Deviations 2).
  - Wall time UNMEASURED: no timing on this box today.
- Give-up witness `(a|aa){0,10}cxyz` (`budget steps=3000`). Denied, startpos
  0..7 give up; with the row they answer (51,55). It moves only
  `-fno-req-handoff` and the two pre-check denies; every other deny arm is
  identical (measured).
- Sabotage S1700-S1707: all eight plants detected in a scratch copy. Five
  rows re-aimed (S460, S463, S529, S813, S814).
- abi: FILL.

## What was built

All in `src/gen/emit_dfa.c` and `src/gen/emit_vm.c`, plus two declarations in
`src/core/internal.h`.

- **`CandUse`** (the `req-use` payload) gains `whole` (the landmark is the
  WHOLE run) and `reenter` (the attempt loop re-enters).
- **`req_handoff_k(cx)`** is the one spelling of the subtracted K. It is the
  whole run's `whole_maxoff` where FIRST keeps the whole run, else
  `req_landmark_maxoff`. Every reader asks it: the entry's move, both
  re-entries, the site's `head_max` and `<PREFIX>_REQ_HANDOFF`.
- **`req_site_define`** keeps (`ret_pred`) the whole run's FUNC part where
  the row keeps the whole run. A whole run that the parts do not compare is
  an internal error, never a silent window.
- **`emit_req_landmark_move`** is the re-entered move's one text, shared by
  its two consumers:
  - the forward scan's `pf_emit_handoff` (unchanged bytes: the S809 anchor
    line is kept verbatim);
  - the attempt loop's new `pcrec_emit_req_attempt_reentry`. With `f` NULL
    there is no reseed.
- **`emit_vm.c`**:
  - the first attempt starts at the handoff's position (`first`);
  - the "[K82] handoff reached a VM route with no prefilter" internal error
    is retired, because that route is now admitted;
  - the retry calls the re-entry after the encoding's advance and before
    the start-set seek;
  - the pre-check's blocks are emitted once, above the prefilter, where the
    prefilter re-enters (`pcrec_req_site_in_prefilter`).
- **`pf_handoff_applies`** (NEXT's `handoff` row) drops the
  `cand_finish_of == VM` decline. It reads FIRST's row and declines a
  whole-run row, so the attempt rows and the scan row never both apply.

## Admission table

The `req-use` table's FIRST rows, first-match (`--list-axes`, axis
`req-use`):

| # | row | applies where | stamp |
|---|---|---|---|
| 1 | `handoff` | unchanged: a DFA scan in front (DFA body or VM hybrid prefilter), finite landmark K, not count-collapsed, not `\G`+prefilter-window | `_REQ_HANDOFF` K |
| 2 | `handoff-attempts` | pre-check emitted; VM with NO DFA scan; BOUND not one-start (`^`, `\A`, `\G` start: one attempt); whole run of 2+ positions with finite `whole_maxoff`; every other part (gate byte, set-rest members, window) a byte or slice of the whole run (`req_parts_in_whole`, so a re-ask stops at the run's next hit: linear) | `_REQ_HANDOFF` whole K; entry + retry re-entry |
| 3 | `handoff-attempts-entry` | row 2 without the parts conjunct (a set-rest byte the run does not hold, e.g. `x{2,5}(?i:cat)`) | entry only |
| 4 | `scan-from-startpos` | fallback | `"none"` |

Prefilter axis: the `handoff` row (rank unchanged) now applies on the VM
hybrid's inlined prefilter too, its desc says so.

reqvm0's soundness rules, as built:

- V1 (reset run state per attempt): the attempts the loop runs are ones it
  ran before.
- V2: `\G` reads `search_from`; only `attempt_position` moves (S1703).
- V3: round-up to a character start, `PCREC_START0_ROUNDUP` (S1701).
- V4: unbounded K declines. Backreferences, variables, subroutine calls and
  unbounded prefixes are unbounded on the lowered tree (S1706).
- V5: budgets are per call, so give-ups move one way (§2.41¶9a).

**Callouts.** No callout conjunct, following the callout contract:
`match_api.md` §11.6¶1 leaves fires on skipped attempts unspecified, and a
consumer's text is ANY on the lowered tree, so K bounds it. `x(?C1)abc` takes
the entry-only row (K=1). A skipped attempt cannot end the search with a
callout error, as under the start-set seek (tuning §2.41¶8b says so).

## Spec hunks

- `docs/spec/tuning.md` §2.41:
  - ¶4: a VM artifact with no DFA scan takes ¶8b's rows instead.
  - ¶8a: the re-entry also applies inside a VM hybrid's prefilter.
  - ¶7a: dropped the "listing text unchanged" sentence.
  - NEW ¶8b: the attempt-loop rows.
  - ¶9: give-up-preserving on DFA-scan routes.
  - NEW ¶9a: the one-way give-up paragraph, written like §2.42¶3, with the
    witness.
- `docs/spec/match_api.md`:
  - §3.1¶14 is amended honestly: the DFA-scan routes only.
  - NEW §3.1¶15a: the `-fno-req-handoff` one-way movement on the attempt
    loop.
  - §6.3.7¶11: `_REQ_HANDOFF` on the attempt-loop rows (the whole run's K),
    and the closing sentence's give-up claim narrowed.
- `docs/spec/facts_listing.md` §4.1.2¶8/¶8b: `_REQ_HANDOFF` carries the
  whole run's own offset on ¶8b's rows.

## Tests and sabotage

FILL

## Measurement

FILL

## abi and re-pins

FILL

## Deviations

FILL

## STATE AT HANDOFF

FILL
