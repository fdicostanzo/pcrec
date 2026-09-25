# k66fix — K66 fix (lane k66fix, opus, 2026-09-25)

Branch `lane/k66fix` from `lane/k65fix`'s tip `bbbf58e5` (abi 34, unmerged).
Brief: fix K66 as ruled by Frank on 2026-09-25, extending K65's fix (a) to
runs. On VM routes with no DFA scan in front, the pre-check proves no-match
from EVERY necessary window of a necessary run longer than `REQ_RUN`'s
8-byte window. The proof must no longer depend on the prior's window pick.
Invariant: S1 reads `Job.req_run`, so that field must not fork.

## FINDINGS FIRST

1. **The fix compares the WHOLE run, not each window.** Where the stored
   run is longer than the window, `emit_req_run_rest` (`src/gen/emit_dfa.c`)
   follows the window's scan loop with a second loop of the same shape.
   - The second loop compares the whole run the window was cut from, scanned
     on the same member.
   - A subject without any one window of the run has no whole run. So one
     compare proves NOMATCH from the absence of EVERY window, and the proof
     rests on the run, which is a fact about the pattern.
   - Emitting one loop per window would be up to 24 loops, each weaker than
     the one whole compare. This is K65's shape one grain up: one extra
     half, same guard (`!pcrec_artifact_has_dfa_scan(cx)`), plus
     `whole_len > len`.
   - The loop text is shared. `emit_run_scan_loop` is split out of
     `emit_req_run_check` byte-identically, and both callers emit it, so the
     two compares cannot differ in shape. S267's two-format anchor sits in
     it once, so `SAB_COUNT=2` still holds.
   - K65's `rq_set[]` half now marks the whole run's bytes as done, since
     the whole compare has tested them.
2. **What `Job.req_run` holds now (the S1 invariant).** It is still ONE field,
   a `ReqRun`, written by one call (`pcrec_req_byte`, `src/opt/reqbyte.c`)
   from one derivation.
   - `bytes[PCREC_MAX_REQ_RUN_EMIT]`, `len`, `idx`: **unchanged in meaning and
     value.** They are the ≤8-byte WINDOW the prior cut (`rn_window_start`)
     and its scan member. `<PREFIX>_REQ_RUN` stamps them. The window check,
     S1's pin (`run_o`) and `OfsTest.run_bytes`/`run_len` read them exactly
     as before.
   - NEW `whole[PCREC_MAX_REQ_RUN_SCAN]`, `whole_len`, `at`: the stored run
     the window was cut from (`RbRun best`, up to 32 bytes), its length, and
     where the window starts inside it. `bytes == whole + at` for `len`
     bytes. `whole_len` is 0 exactly when `len` is 0.
   - So the pre-check's whole compare is derivable from the same field S1
     reads. A reader wanting the whole run reads `whole`/`whole_len`, and
     the window is `whole + at`. There is no second field and no second
     walk.
   - When S1 step 6 rewrites the run loop, it should treat
     `emit_run_scan_loop` as the one loop both compares go through.
3. **The witness is fixed in both directions.**
   `(x?)([a-z]+)+eeeeeeee~#~#~#~#\1` on `e` + `a`×36 + `~#~#~#~#`:
   - `-e byte`: `steps` in 2.24 s on the base, `nomatch` after.
   - `-e utf8`: `nomatch` before and after.
   - After the fix, both artifacts compare `eeeeeeee~#~#~#~#` (16 bytes).
     `REQ_RUN` still reads `7e237e237e237e23@0` / `6565656565656565@0`.
4. **Census.**
   - **Pre-code:** base build `bbbf58e5`, 5,920 compiling artifact-configs
     (bench 256 configs + corpus 3,193 patterns × auto/`--engine=vm`). On a
     no-DFA-front route (`RX_ENGINE "vm"`, `RX_VM_PREFILTER "none"`), 28
     carry a FULL 8-byte `REQ_RUN` window, the only artifacts that can hold
     a longer run.
     - 16 of the 28 emit the pre-check.
     - The other 12 are `REQ_WHY "one-attempt"` (G2 declines, so there is no
       pre-check to extend, same scope as K65).
   - **Movers:** `docs/dev/optloop/admitfix/k66_census.py`, base vs. the fix
     at the same abi, byte for byte. 12 changed, all predicted.
     - Bench: 2 of 256 (`wild-secrets-github-pat`, vm-caps + vm-nocaps,
       whole run 11 bytes `github_pat_`).
     - Corpus: 10 of 6,386 (8 `--engine=vm`, 2 auto): `(a)…(j)\10`,
       `\10(a)…(j)`, `(a)…(i)\9`, `hello world`, `needleXYZW`,
       `a{65536x}`, `a{65536,x}`, `abcdefghij|abcdefghik|abcdefghil`. Runs
       are 9–11 bytes.
     - Every mover: +13 lines (one whole-run loop), and a 6-line `rq_set[]`
       block removed (every one of the 12 had its K65 rest entirely inside
       the whole run). Nothing else moves: the residue after stripping both
       is byte-identical, and no stamp moves.
     - The other 4 full-window emitted artifacts have runs of exactly 8 and
       are identical (`(a)…(h)\8` ×2, `a{2,3,4}`, `\Qabc\$xyz\E`).
     - 0 refusal mismatches, 0 timeouts.
   - **The population is not zero outside synthetic witnesses**: one bench
     pattern on its two forced-VM configs, and ten corpus configs. None was a
     measured give-up; the defect needs a hostile subject.
5. **abi 34 → 35** (the brief's ruling).
   - No stamp, stamp value, declaration or layout moves. The bump moves
     emitted PROGRAM text on the 12.
   - The ritual: `PCREC_ARTIFACT_ABI`, `match_api.md` §6's new top entry
     (and "gap-free from 2 to 35"), `run_codegen_tests.sh` `ABI_EXPECT` and
     its narrative, and `run_recursion_identity.sh` (B) FILEPIN →
     `a446a99e` (the bump commit).
   - The digit is a same-length substitution. The movers are small corpus
     patterns, and none is a byte-count manifest pin (the `tests/resource`
     `a{5,25000}` pin is not a no-DFA-front run artifact).
   - Readers were found by grep. The remaining `34` hits are history
     (review docs, design tables).

## Residue (stated)

- Runs longer than `PCREC_MAX_REQ_RUN_SCAN` (32) are stored truncated. The
  whole compare covers the stored 32 bytes. That bound is structural
  (`rn_app`/`rn_pre` keep the first or last 32 by role), not a prior, so no
  encoding moves it. The corpus/bench maximum is 11.
- Two DISJOINT necessary runs: only `best` (the longest) is compared. Its
  bytes, and the other run's bytes, are all set members, so K65's half still
  tests the other run byte by byte. This is not K66's shape (a window
  choice) and was not measured.
- On this route the window check is now redundant with the whole compare.
  It costs one extra linear pass, only on the 12 movers. It stays because
  S1's pin and `REQ_RUN` describe it; dropping it is S1 step 6's business
  (D77).

## Checks (both directions verified)

- **`tests/base/k66_precheck_whole_run.rxt`**: 2 blocks × (6 n + 1 m + 1 gu),
  `features backrefs`, `budget steps=10000`.
  - The `n` cells hold every set byte, so K65's half cannot cover them. They
    hold a window but not the whole run: byte's window, utf8's window, and
    both windows.
  - A 16-byte `!` tail defeats the VM's minimum-remaining-length prune. The
    first draft, without the tail, passed on the base: the MRL prune capped
    the backtracking below the budget.
  - `tests/harness/run.sh` on the file: **16/0 on the fix**, **8 failed /
    8 passed with `PCREC=<bbbf58e5 build>`**. All eight are `steps` give-ups,
    exactly the predicted cells.
  - `verify_rxt.py`: PASS=14, SKIP=2 (giveup). libpcre2 10.48 spot check:
    NOMATCH on the three shapes, `m 0 19` on the match cell.
- **`tests/codegen/run_prechecks.sh` §5.8** (+7 checks, 267 → 274).
  - Six rows with a HAND-DERIVED expected whole run and `rq_set`:
    - the witness under byte and under utf8;
    - `(x?)([a-z]+)+Q.abcdefghij\1` (rest `{81}` only);
    - three `none` controls: a run of exactly 8, an exact hybrid, and
      `-fno-req-run`.
  - Plus `[5.8r]`: the witness is unguarded VM with an 8-byte window.
  - On the base build: 3 fail / 271 pass (the three rows expecting a whole
    run).
- **Sabotage S278** (`tests/mech/sabotages/S278_precheck_whole_run_removed.sh`):
  plants `return;` at `emit_req_run_rest`'s guard. `SAB_HARNESS_TARGET` is
  the new `.rxt`, and `SAB_REACH` probes the witness's stamps and its
  16-byte compare. `run_sabotage_matrix.sh S278` result: **DETECTED,
  `reach:ok(1/1)`, `prechecks:3fail/271pass`, `corpus:8fail/8pass`**, with
  0 unexpected, 0 undetected, 0 unreached and 0 anomalies.
- **S277 re-anchored** (its context line now marks `whole` done; plant and
  intent unchanged) and re-run: **DETECTED, `reach:ok(1/1)`,
  `prechecks:6fail/268pass`, `corpus:9fail/15pass`**. The figure was
  updated: §5.8's Q and `-fno-req-run` rows also expect a K65 rest.

## Re-pins (readers found by grep)

- `tests/rxtsource/run_rxtsource_tests.sh`:
  - CENSUS_* and RUNSH_* move 218/4004/29153 → 219/4006/29169.
  - C3_PASS 13750 → 13764, C3_SKIP 15231 → 15233, C3_SKIP_GIVEUP 27 → 29,
    from the file checked alone.
- S269/S270's clean-tree prechecks figure: 267 → 274.
- The abi readers listed above, plus the (B) FILEPIN.

## Validation

(Filled in below from the logs; the chain ran detached.)

VALIDATION_PLACEHOLDER

- **OWED: the full `make test`.** The box's one heavy slot is queued:
  chkgaps first, then k65fix. Not run.
- **OWED at merge/mech:**
  - `make test-recursion-identity`: the (B) re-pin, an opt-in gate, not run.
  - `make test-axes` for `-fno-req-run`/`-fno-req-byte`: both remove the
    whole compare, so the sweeps should stay answer-identical.

## Merge notes

- Stacked on `lane/k65fix`: merge k65fix first.
- `docs/dev/known_issues.md` carries main's K66 block, marked fixed. Main
  added the same block at the same place, so expect a both-added conflict
  there. Resolve by keeping this branch's version.
