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
- abi 89 -> 91 (90 is reserved for [INLINE-C] stage 2, lane ic2fix, which
  lands first); renumber at landing if that order changes (abi and re-pins).

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

- **Corpus.** NEW `tests/litscan/handoff_vm.rxt` (18 blocks, 798 case lines)
  written by `gen_handoff_vm.py` with `gen_handoff.py`'s oracles: byte blocks
  from python3 `re` AND libpcre2 10.46, utf8/`\G`/`\K` blocks from libpcre2
  alone (`# pcre2-only`), cells at every character-boundary start.
  `--check-pcrec` mismatches 0. `handoff.rxt`'s header now says its
  `engine vm` blocks run the attempt-loop handoff too.
- **Reach pins** (`tests/memfn/run_handoff_reach.sh`, 15 pass / 0 fail): the
  hybrid floor 4 (adds `(x)?userz` and bench case 2's pattern); a NEW
  attempt-loop section (floor 4: `(?:xx|y)abc`, `(a|aa){0,10}cxyz`,
  `.{1,3}cd` utf8 with the round-up line, `x{2,5}(?i:cat)` entry-only) and
  its declines (`^abcd`, `^(?:ab|x)cdef`, `\Gabcd`, `a+xyz`, `(a)\1xyz`).
- **Axes.** `tests/axes/run_axes.sh` GIVEUP1 entries for `-fno-req-handoff`,
  `-fno-req-byte`, `-fno-req-run` at `handoff_vm.rxt:20..27` (the one-way
  movement, the deny arm gives up), GROUP F4's comment.
- **Checks moved with the contract** (each states why in place):
  - prechecks 5.12b (the attempt rows' K is the whole run's, at most the
    landmark's), 5.12l (the hybrid prefilter's `= search_from` landmark; the
    attempt loop's re-entry), 5.12q INVERTED (the hybrid now re-enters);
  - startset `[vm-handoff]`: a mover's `REQ_HANDOFF` is `none` or a decimal
    K (counted), not always `none`; VM-hat manifests +12/+13 rows, all
    handoff_vm.rxt blocks;
  - the slot graph declares FIRST reads BOUND on the VM route (cand-oracle's
    trace build aborted on the undeclared read); S607 re-anchored.
- **Sabotage S1700-S1707**, each plant validated DETECTED in a scratch copy
  of HEAD before commit, every REACH probe OK:
  S1700 the attempt rows keep the window, not the whole run (harness);
  S1701 the attempt re-entry drops the utf8 round-up (memfnreach, structural:
  a mid-character start cannot match within K, so no answer moves);
  S1702 an extra `attempt_position++` skips a start (harness);
  S1703 `\G` reads the moved start (harness); S1704 `req_parts_in_whole`
  dropped (memfnreach); S1705 BOUND one-start admitted (memfnreach, witness
  `^(?:ab|x)cdef`); S1706 an unbounded K admitted (memfnreach); S1707 the
  VM-finish decline restored in `pf_handoff_applies` (memfnreach).
  Re-aimed: S460, S463, S529 (reach floor 4), S813, S814, S607, S693 (abi).
  S1708-S1719 unused.
- **Local section runs** (scratch logs, this box, under the box lock): GREEN
  test-registry, test-rxtsource, test-prechecks, test-startset,
  test-codegen, test-memfn-reach/rows/stamps/arms, test-spec-history,
  test-claudemd-size, test-cand-oracle (175/0). test-spec RED on 10 checks
  (`pcre2_compile_8` undefined at link, check06_cursor) is pre-existing: the
  same red on a clean copy of the merge base. Owed queue runs: 630 test,
  631 mech, 632 axes.

## Measurement

Measurement card ([REQRUN-VM] rows; no `measure_store` card: the rows are
first-match admissions, not a priced choice).

| case (bench subst, `acc-main`) | main | reqvm1 | ratio | twins (subtri) |
|---|---:|---:|---:|---|
| 2 `rare` (VM hybrid) | 1,273,872,921 | 790,986,202 | x1.61 | 2b 783.8M, 2a 153.5M |
| 7 `url-tld-fix` (VM-only) | 3,295,070,119 | 1,304,903,257 | x2.53 | 7a 922.7M, 7b 332.8M, 7d 2,169.7M |

- instructions:u, `taskset -c 7`, gcc 15.2 -O2, subtri's `drv.c`, 3 reps
  agreeing within 30 instructions; subject sha256 verified, output sha256
  identical across main, reqvm1 and the twins (2: 0b9c3be4, 7: 80c1df04).
- **Wall time UNMEASURED** (no timing on this box today); the official
  verdict is a bench run.
- **Movers** (`docs/dev/lanes/reqvm1/movers.py`, merge base vs the lane
  built at abi 89, corpus + bench patterns x byte/utf8 x auto/vm +
  `--no-captures`, 34,750 cells): 1,883 vm-attempts, 212 hybrid-reentry,
  1 dropped-hybrid-size (`(\p{Xwd})x` utf8: the size cap's measured hybrid
  size in `_VM_PREFILTER_WHY` moves by 952 bytes), 0 unexpected. The queue
  job re-runs it.

## abi and re-pins

- `PCREC_ARTIFACT_ABI` 89 -> 91: the emitted text moves on every admitted
  artifact (attempt loop and hybrid prefilter). 90 is [INLINE-C] stage 2's
  (ic2fix), expected to land first; if reqvm1 lands first, take 90 and
  replace `91` at every reader below.
- Readers, found by grep for the number: `src/gen/emit_dfa.c` (the define),
  `tests/codegen/run_codegen_tests.sh` (`ABI_EXPECT=91`, transition text
  "89->91"), `docs/spec/match_api.md` (guard block, rx_info row, §6¶17),
  `docs/dev/history/abi_changelog.md` (the 91 entry), S693.
- Other re-pins: registry axes coverage 236 -> 242; rxtsource CENSUS 301 /
  6237 / 75461, RUNSH 277 / 6237 / 75461, C3 PASS 22650, SKIP 52725,
  pcre2-only 19927, verifiable 25036; startset VM-hat manifests;
  `tests/codegen/cand_oracle_witnesses.tsv` (the two new rows' witnesses).
- **Expected red for the manager:** test-recursion-identity against its
  FILEPIN until re-pinned to the merge commit.

## Deviations

1. **abi 91, not "the next number" literally**: main is at 89 with ic2's
   90 in flight; I took 91 so neither lane renumbers if ic2 lands first
   (see abi and re-pins).
2. **Kit-facing finding (not acted on):** on case 7 each re-find calls both
   `rx_reqrun` (the window) and `rx_reqrun_whole`. The window re-ask is
   redundant when the whole run is the landmark. It is the kit's PRES
   decision, so pcrec does not override it; a request for the manager to
   file. The gap to twin 7a (1,304.9M vs 922.7M) is mostly this.
3. **Pre-existing, unrelated:** the DFA-route set-leads gate byte is re-asked
   per re-find (a latent quadratic); `nullable_anch.rxt:48`'s `--engine=vm`
   GIVEUP1 allowance is not reached on this build even with the deny.
4. **Give-up witness swapped:** reqvm0's `(a?){12}a{12}xyz` also moves
   `-fno-length-prune`; `(a|aa){0,10}cxyz` moves only the three req denies.
5. **Callouts:** no conjunct (contract §11.6¶1); `x(?C1)abc` takes the
   entry-only row.

## STATE AT HANDOFF

- Branch `lane/reqvm1`, main merged ALONE at its tip (490bc2baf, clean).
  All work committed; tree clean except the untracked lanecheck file.
- Queued: 630-reqvm1-test (REF = 490bc2baf, abi 89), 631-reqvm1-mech
  (S1700-S1707, the re-aimed rows, the handoff family, plus a REACH_ONLY
  pass), 632-reqvm1-axes. None run yet.
- Rulings file: `(none yet)` at every checkpoint.
- Manager at merge: confirm abi order vs ic2fix; re-pin recursion
  identity's FILEPIN; file Deviations 2 to the kit.
