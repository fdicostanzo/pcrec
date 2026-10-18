# rowfix — S689 and S1085 restored (2026-10-18)

Lane `rowfix` (opus), branch `lane/memfn-rowfix`, cut from `lane/memfn-b3b`
at f0785bf3b. Brief: two kit sabotage rows read UNDETECTED on main 65dd423ee
and on B3b (`b3b_report.md` §10 and §12). For each row: name the cause, find
the commit that broke it, restore the row's intent, and re-run it SOLO to
DETECTED.

All runs were pinned `taskset -c 12-15`, mech rows `PROCS=4`, one at a time,
`gnutimeout 1800 bash tests/mech/run_sabotage_matrix.sh SNNN`. Logs are in
`worktrees/memfn-slot/rowfix/logs/` (scratch, not committed).

## 1. S689 (`kit_walk`'s empty-slot rule; detector `n2sample`)

### 1.1 Two causes, one on each side of the row

**(a) The detector was red on a clean tree (B3b only).** b3breach
(f0e41cee0, a35ca8f90) appended `ask_mismatch=M` to `n2_report.py`'s floors
summary. `docs/design/memfn/probes/rowcon/n2_census.sh` matched that line
as one fixed spelling (`NOT-APPLIED,reason_stale=0,reach_dropped=0`), so
EVERY run, full or partial, read rc 4 with every count 0. Measured on the
clean tip: `run_n2_sample.sh` reports `census rc 4`, `checks failed: 1`
(`logs/n2sample_clean.log`). Every `n2sample` row (S668, S689) therefore read
DETECTED on B3b for the wrong reason. My first solo run of S689 at
f0785bf3b read `n2sample:1fail/0pass DETECTED` (`logs/S689_before.log`),
which contradicts b3bmtri's `0/1` at 034f694cf. b3bmtri's run predates
b3breach.

Fix 725abc9e5: `n2_census.sh` now reads the summary FIELD BY FIELD
(`floors_ok`). Every count except `floor_placeholder` must be 0, and
`reason_stale`, `reach_dropped` and `ask_mismatch` must be present. A count
the report adds later must be 0 too, so the next appended field cannot fail
the same way. I checked eight spellings by hand, covering the clean partial
and full lines, each nonzero count, a missing `ask_mismatch`, an unread
line, and a new nonzero field. After the fix the clean n2sample reads rc 0
(`logs/n2sample_clean_fixed.log`).

**(b) The plant had become an equivalent mutant (main and B3b).** With the
detector repaired, S689 solo at 725abc9e5 reads
`n2sample:0fail/1pass UNDETECTED` (`logs/S689_before_fixed.log`), which is
main's verdict. The row plants `kit_walk`'s
`if (!any) return t->n;` (memfn/src/compose.c). That rule fires only when
the asked slot holds no row. No kit table walk asks such a slot today:
- `fn`: BODY holds fn-pair and fn-memchr; PREFIX holds vrun-w32 and vrun-w16;
- `fd`: FIND and PRES both hold rows;
- `arms` and `rc`: one slot each (`slot` NULL), never empty.

So dropping the rule changes no walk.

**Breaking commit: 55d5ece2c** (r13 2/7, "vrun-w16, the first SIMD row").
It put the first row into fn_rows[]' PREFIX slot, which the row calls
"born empty". This was b3bmtri's unverified hypothesis; it is now verified
by the equivalence argument above and by the solo run.

### 1.2 The fix: re-aimed at the choice's current home (bbdb446da)

The row guards this choice: a FUNC part whose PREFIX walk chooses no row is
an ordinary answer, never a refused site in the trace. Since R-13 that
choice is the walk's `optional` tctx. `fn_select` (memfn/src/ofsskip.c) sets
it for the PREFIX walk, and `gate_trace_end` then spells a no-row END
`chosen=none` instead of a refusal's `chosen=-`. The new plant drops it:
`slot == FN_PREFIX` becomes `0` in fn_select's tctx initializer. Every
offset-skip/pre-check FUNC part at SIMD-off, where the vrun rows decline,
then writes `END ... chosen=-`.

I planted at fn_select rather than at gate.c's ternary. The DECISION that
the PREFIX slot needs no row is made in fn_select; gate.c only spells it.
The other optional walk (fn_rungs' named rungs) is not reached at SIMD-off
either way.

The detector (`n2sample`) and SAB_ID are unchanged. SAB_FILE moves to
memfn/src/ofsskip.c. The row gains `SAB_REACH_POP` on the sample's
offset-skip witness `abc[0-9]+xyz`.

| run | tree | verdict | log |
|---|---|---|---|
| before, solo (detector red) | f0785bf3b | n2sample 1/0 DETECTED (false: clean tree rc 4) | `logs/S689_before.log` |
| before, solo (detector fixed) | 725abc9e5 | n2sample 0/1 UNDETECTED (equivalent plant) | `logs/S689_before_fixed.log` |
| after, solo | 1099d14d9 (= bbdb446da's code) | `pop ok, reach ok(1/1), n2sample:1fail/0pass` DETECTED | `logs/S689_after.log` |
| hand check of the cause | scratch copy of HEAD + plant | census `rc=5 noend=33`, would_decline 0 | (console) |

The hand check shows the row fails for its own reason: `noend` (no-row
ENDs) went from 0 to 33, and no would-decline appeared.

## 2. S1085 (the readers' PF site carries E; detector `candoracle`)

### 2.1 Cause

The plant makes `cand_pf_site` (src/gen/emit_dfa.c) hand the kit the start
state's escape set E instead of the row's scanned set. On the DFA-hat
witness `\B(?<!a)d`, T = {d} and E is 62 bytes. The detector is the trace
build's asked-class hold (`cand_asked_hold`). It compares the class a
reader asked with the class the PF site's define reports.

Probe on the planted trees, with a temporary `fprintf` in `cand_asked_hold`
in scratch copies only:
- **At 92ec25906 (fdb2fix's measurement):** the readers ask a 62-byte walk
  class, the define reports memchr {d}, and the hold aborts
  (`asked-class-differs ... PF`). This is the 1 fail / 99 pass.
- **At main 65dd423ee and at this branch's f0785bf3b:** the readers still
  ask the 62-byte class (68 asks on main), but NO define record exists. The
  wrong class flips the artifact's start search from
  `RX_DFA_PREFILTER "first-memchr-bounded"` to `"handoff"`
  (`RX_REQ_HANDOFF "0"`). The PF site is therefore never defined, the hold
  has only one side and stays silent, and candoracle reads 0 fail.

The artifact MOVED under the plant, but the witness line still "reaches"
first-memchr-bounded. Its CANDROW hits come from the readers' reads of the
row (NEXT, `dfa_pf_read`), not from the emitted selection.

**Breaking commit: fe7ece905** (lane lmfacts, "landmark admission restated
as facts, one start-set source with R4", merged at d1a1fdf4b). It was
bisected with planted default builds of `\B(?<!a)d`:

| commit | unplanted prefilter | planted prefilter |
|---|---|---|
| 92ec25906 | first-memchr-bounded | first-memchr-bounded |
| fe7ece905^ | first-memchr-bounded | first-memchr-bounded |
| fe7ece905 | first-memchr-bounded | **handoff** |
| 65dd423ee (main) | first-memchr-bounded | **handoff** |

After fe7ece905 the handoff's landmark admission prices the displaced
start-byte row off the readers' class. So a wrong class now changes WHICH
row is emitted instead of producing a second, disagreeing define. The
hypothesis in `b3b_report.md` §12 ("no reader asks", or "the classes
compare equal") was half right: readers do ask, and nothing defines.

### 2.2 The fix: a witness the detector reaches (3999c287e, figure 3c4e94923)

A new line in `tests/codegen/cand_oracle_witnesses.tsv`:
`first-memchr-bounded  -fno-req-handoff  \B(?<!a)d`. It is the same DFA hat
with the handoff denied, so the PF row is emitted and defined, and G1 asks
its site. This follows the house precedent for witnesses under a deny
(`byte-class -fno-req-handoff`, `scan-from-startpos -fno-req-handoff`). The
detector, `cand_asked_hold`, is unchanged and not weakened. On the planted
tree this line aborts with `asked-class-differs`. One reader ask was
followed by one define, `pc0=1` against 62. Clean, the line passes:
`run_cand_oracle.sh` reads 166/0 on the branch (was 165/0).

| run | tree | verdict | log |
|---|---|---|---|
| s1085tri, solo | main 65dd423ee | candoracle 0/141 UNDETECTED | `worktrees/memfn-slot/b3b/s1085/main.log` |
| s1085tri, solo | B3b e5a5cf653 | candoracle 0/165 UNDETECTED | `worktrees/memfn-slot/b3b/s1085/tip.log` |
| hand, planted trace build | this branch f0785bf3b | no CANDORACLE on any witness | (console) |
| after, solo | 3999c287e (= 3c4e94923's code) | `candoracle:1fail/165pass` DETECTED | `logs/S1085_after.log` |

### 2.3 Not fixed here (finding for main)

Under the plant, the DEFAULT configuration moves an artifact byte: the
prefilter goes from first-memchr-bounded to handoff on `\B(?<!a)d`.
candoracle cannot see that. Its reach test counts every CANDROW hit for the
row, including readers' reads of a row the artifact does not emit, so
"reaches its row" does not mean "the artifact selects its row". A reach test
keyed on the emitted selection, such as the `RX_DFA_PREFILTER` stamp, would
see such moves on every witness. That is a check-design change to a shared
detector, so it is outside this brief.

## 3. Validation

All pinned to `taskset -c 12-15` and run on this branch's tip, with logs in
`worktrees/memfn-slot/rowfix/logs/`:

| run | result | log |
|---|---|---|
| S689 solo, after | DETECTED, n2sample 1/0 | `S689_after.log` |
| S1085 solo, after | DETECTED, candoracle 1/165 | `S1085_after.log` |
| S668 solo (the other `n2sample` row, after the detector fix) | DETECTED, n2sample 1/0, reach ok 2/2, pops ok | `S668_after.log` |
| `tests/memfn/run_n2_sample.sh`, clean tree, before / after the fix | rc 1 (census rc 4) / rc 0, `checks failed: 0` | `n2sample_clean.log`, `n2sample_clean_fixed.log` |
| `tests/codegen/run_cand_oracle.sh`, clean tree | 166 passed / 0 failed (was 165; +1 witness) | `candoracle_clean.log` |
| `python3 -I scripts/m6read_check_sab_anchors.py` | 822 sabotages, 849 anchor sites, all resolve | (console) |
| `bash tests/codegen/run_codegen_tests.sh` | 331 passed / 0 failed | `codegen.log` |
| `make strict` | rc 0, "whole tree compiles clean" | `strict.log` |

`floors_ok` was also checked by hand on eight summary spellings (§1.1). Not
run: `make test`, the full N2 census, other mech rows. The changed files are
one probe script (`n2_census.sh`), two sabotage rows and one witness line.
Their suites are `n2sample` (the mech arm and the full census share
`n2_census.sh`) and `candoracle`, and both were re-run above.

**Note for main.** On lane/memfn-b3b, every N2 census run whose report
carries b3breach's `ask_mismatch` field (from a35ca8f90 on) ends rc 4,
whatever its floors say. The cause is the fixed `case`, so this holds for any
`b3b_report.md` §14 or later N2 run I did not re-read. The floor and ask
verdicts in `n2_results.md` and `report.log` are unaffected, because the
report computes them. Only the shell's rc and DONE line were wrong.

## 4. Charter vs committed

| charter item | committed |
|---|---|
| S689: read row, intent, code; solo UNDETECTED with cause named | done: two causes (detector red on B3b; plant equivalent since 55d5ece2c) |
| S689: restore intent (re-aim / witness / UNREACHED) | re-aimed at fn_select's optional PREFIX walk; detector fixed (field-wise floors) |
| S689: one commit, solo DETECTED, SAB_DOC_FIGURE MEASURED | 725abc9e5 (detector), bbdb446da (row); DETECTED 1/0 |
| S1085: same | cause named (no PF define under the plant since fe7ece905); witness added (3999c287e); figure 3c4e94923; DETECTED 1/165 |
| m6read_check_sab_anchors, run_codegen_tests, suites touched, make strict | all green (§3); S668 re-run DETECTED |
| report + lanes index line | this file; index line in docs/dev/lanes/CLAUDE.md |
| bisect | S689: 55d5ece2c (by the equivalence argument); S1085: fe7ece905 (by planted builds) |

Scope note: I used one `cd` inside a single bash call to launch the first
mech run (`cd $W && nohup ...`), against the brief's no-`cd` rule. Every
later launch uses `env -C`. Nothing was written outside the worktree and
the scratch dir.
