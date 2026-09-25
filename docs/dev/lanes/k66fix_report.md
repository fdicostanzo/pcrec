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

- `make strict`: clean ("whole tree compiles clean with -Werror -Wshadow").
- `make test-codegen` (after the abi bump): `run_group: 9/10 scripts
  passed`. The one red is `run_inline_capability.sh` ("nm could not read
  arm_a.o (no rx_search symbol)"), the known darwin Mach-O `nm` red that
  k64fix/k65fix A/B'd as pre-existing. `[DD-14.FB] (§10.4)` passes with abi
  35 on both engines (`ABI_EXPECT=35`). Log: `/tmp/k66fix/codegen.log`.
- `make test-prechecks`: 274 passed / 0 failed (EXIT=0).
- `make test-rxtsource`: EXIT=0, including the re-pinned census
  (219/4006/29169) and C3.
- Targeted: the regression `.rxt` (16/0 on the fix, 8/8 on the base), S278
  and S277 (above).

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

## Landing (2026-09-25, resumed session, rebase onto main `84b4a7a9`)

Rebased the whole 16-commit stack (k65fix's 5 + k66fix's own 4 + the two
lanes' abi/re-pin/report commits) onto main `84b4a7a9` (which had picked up
`lane/chkgaps` and `lane/s1r3`'s K66 filing in the meantime). `git rebase
main` hit conflicts at three commits; each is resolved and recorded below.

**Conflict 1/2 — `tests/codegen/run_prechecks.sh` §5.7 vs §5.8** (k65fix's
first WIP commit and its later re-pin commit). Main already carried §5.6
(K64) and §5.7 (chkgaps' own unanchored G2 positive control, filed at
`84b4a7a9` itself). K65's WIP had ALSO opened its section as §5.7. Resolved
by renumbering K65's whole section to §5.8 (heading, all seven `[5.7]`/
`[5.7r]` bracket tags, and the `s57*`/`S57_PAT` variable/file names — not
just the number) while keeping chkgaps' §5.7 verbatim as HEAD's content, per
the brief's instruction.

**Conflict 3 — `docs/dev/known_issues.md`**. HEAD (main) carried K66 as OPEN
(filed by s1r3) beside the *unfixed* K65 header line; the incoming commit's
diff only touched K65's header (adding "FIXED 2026-09-25 —"). Resolved by
keeping K66's OPEN block (K66 becomes FIXED two commits later, when k66fix's
own commits replay) and taking the incoming FIXED header for K65.

**A fourth conflict, `tests/rxtsource/run_rxtsource_tests.sh`'s CENSUS_*/
RUNSH_* pins**, merged with the SAME three-way shape at the same two
commits: HEAD carried chkgaps' net +0/+0/+0 (a known_fail file added then
retired at the chkgapsmerge landing), the incoming k65fix diff computed its
own +1/+3/+24 against the identical pre-chkgaps baseline (217/4001/29129),
so the two deltas summed cleanly to 218/4004/29153 with no arithmetic
re-derivation needed for THIS pair — merged by concatenating the two
dated notes and taking the incoming numbers.

**The renumbering left a live bug the rebase's own conflict markers did not
show**: `lane/k66fix`'s OWN commit (built on top of `lane/k65fix`'s pre-rebase
tip, before chkgaps existed) had opened ITS section as "§5.8" too — the exact
number K65 now occupies after the fix above — because at the time it was
written, K65 really was §5.7 and K66 really was §5.8. This commit applied
CLEANLY during the rebase (no conflict, since nothing in main's diff touched
that hunk), so it silently reintroduced a duplicate-§5.8 collision that
`bash -n`, the build, and `make strict` all missed (nothing gates on section
NUMBERS). Found by re-grepping `^# §5\.` after the rebase finished. Fixed the
same way: K66's section (heading, all `[5.8]`/`[5.8r]` tags, `s58*` variable/
file names) renumbered to §5.9, in a separate commit (`84741e51`) on top of
the completed rebase.

**Every other reader of the old numbers was swept by grep**, not assumed
fixed by the section-header edit alone: `docs/dev/known_issues.md`'s K65
entry (`§5.7` → `§5.8`, with a one-line note on why), `docs/dev/plan.md`'s
`[OPT-PRECHECK-ADMIT]` row (both K65's and K66's inline section citations),
`tests/codegen/CLAUDE.md`'s `run_prechecks.sh` entry (its own §5.7/§5.8
sub-bullets, renumbered, with a parenthetical explaining why), this file's
own `docs/dev/lanes/CLAUDE.md` index bullets for `k65fix_report.md`/
`k66fix_report.md` (added a renumbering note rather than editing the
per-lane report bodies, which stay historical per that directory's own
convention), and the `S269`/`S270`/`S277`/`S278` sabotage rows' `SAB_DOC_FIGURE`
prose and inline doc-comments (section numbers AND the stale check-count
figures those figures quoted). Left untouched, correctly: every `§5.6`
(K64, unmoved) and `§5.7` (chkgaps, unmoved) reference found by the same
grep sweep, and the per-lane report bodies (`k64fix_report.md`,
`k65fix_report.md`'s own body, `chkgaps_report.md`, `chkgapsmerge_report.md`)
— historical, never edited after merge.

**Re-derived by running, not by arithmetic, per the brief's instruction**:
`bash tests/codegen/run_prechecks.sh` standalone on the fixed tree reads
**278 passed / 0 failed** — higher than either lane's own predicted total
(274) because chkgaps' §5.7 and admin3's §3.6 (five extra `-e utf8`
witnesses) both landed on main concurrently with the k65fix/k66fix stack
and neither lane's own arithmetic could have seen the other's addition.
S269/S270's SAB_DOC_FIGURE "clean tree" total updated to 278 to match;
S277/S278's own figures re-measured live (below) rather than copied
forward.

**Validation, in order, on the rebased + fixed tree** (commit `84741e51`,
then `f0b54f0b` for the sabotage-figure update):

- `make -j4 CC=gcc-16`: clean.
- `make strict CC=gcc-16`: clean ("whole tree compiles clean with -Werror
  -Wshadow").
- `bash tests/mech/run_sabotage_matrix.sh S274` (ran alone; the script
  takes exactly one filter argument, not a space-separated list — a second
  invocation covered the other four): **DETECTED**,
  `prechecks:2fail/276pass, corpus:4fail/5pass`.
- `bash tests/mech/run_sabotage_matrix.sh S275`: **DETECTED**,
  `clsfold:78fail/85pass` (unrelated to this stack — the standing VM
  class-fold row from chkgapsmerge — included because it was in the
  brief's named list).
- `bash tests/mech/run_sabotage_matrix.sh S276`: **DETECTED**,
  `prechecks:20fail/256pass`.
- `bash tests/mech/run_sabotage_matrix.sh S277`: **DETECTED**,
  `reach:ok(1/1), prechecks:6fail/272pass, corpus:9fail/15pass`.
- `bash tests/mech/run_sabotage_matrix.sh S278`: **DETECTED**,
  `reach:ok(1/1), prechecks:3fail/275pass, corpus:8fail/8pass`.
- `make test-codegen CC=gcc-16`: `run_group: 10/11 scripts passed`. The
  one red is `run_inline_capability.sh` ("nm could not read arm_a.o (no
  rx_search symbol)") — the standing darwin Mach-O `nm` probe red, A/B'd
  as pre-existing by k64fix/k65fix and ~20 other lane reports; not this
  stack's.
- `make test-rxtsource CC=gcc-16`: exit 0, `checks passed: 214 / checks
  failed: 0`, including the re-pinned census (219/4006/29169) and C3. One
  `RECORD:` line (python 3.9 vs the pinned 3.14's population-count deltas)
  — the box's own pre-existing darwin/python-version note, unrelated.
- `make test-recursion-identity CC=gcc-16` (opt-in gate, the (B) FILEPIN
  re-pin): `checks passed: 16 / checks failed: 0`. Comparison (B),
  whole-file vs the abi-35 pin `a446a99e`: 2,568 call-free patterns
  identical, 0 differing, 0 refusal mismatches, on both the default and
  `-fno-prefilter` axes. Comparison (A), program-region vs the frozen
  pre-module pin `ac4917d`: 2,145/2,167 identical, 0 differing, every
  named exception bucket (bref-rename/var-construct/island/fold/
  size-term-moved) accounted for with zero UNSTAMPED-BUT-DENY-MOVES or
  UNSTAMPED-BUT-FOLD-DENY-MOVES anomalies. Confirms the K66 abi-35 FILEPIN
  is correctly set.
- `make test CC=gcc-16`: launched **detached** (`nohup … & disown`) as the
  last act, per BOILERPLATE's DO-THEN-FINISH — log
  `/tmp/k66land/maketest.log`, started 2026-09-25 19:31:18 EDT. **OWED.**
  Read the verdict from make's own `*** [test-X] Error` lines (never
  `sections ran:` alone) plus a `FAIL:` grep; the one expected red is the
  same standing `run_inline_capability.sh` nm probe named above.

## Delivered

Tip: `f0b54f0b` on `lane/k66fix`, rebased cleanly onto main `84b4a7a9`
(now 84741e51/f0b54f0b past it). Not merged, per the brief. `make test`
is the only owed item; everything else above is measured green on this
tree.
