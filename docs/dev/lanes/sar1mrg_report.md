# Lane sar1mrg report: semantic merge of span arms R1 (lane/sar1) onto main's E1+E2

Lane sar1mrg (opus), 2026-11-09/10. Worktree `worktrees/sar1mrg`, branch
`lane/sar1mrg`, cut from main 3f46eba9b (E1+E2). Merged lane/sar1 at
b3d90dbfe (R1 + sar1fix + sar1mt). Build go: D191, merge reconciliation
only. No abi number moves and no emitted scaffolding moved. Merge commit
e2ad73586.

## MERGE

`git merge --no-ff lane/sar1` ran alone. It had 13 conflicted files, the
same set the landing lane found:

- Code: `src/facts/req.c`, `src/facts/walk_arms.def`.
- Specs: `docs/spec/facts_listing.md` §4.1.2¶8c and §4.1.3¶4/¶4a,
  `docs/spec/tuning.md` §2.28¶3.
- Orientation: `src/facts/CLAUDE.md`, `tests/litscan/CLAUDE.md`,
  `docs/dev/history/claude_md/docs__dev__lanes.md`.
- Checks: `tests/axes/run_axes.sh`, `tests/codegen/run_facts_checks.sh`,
  `tests/compound/run_lever_fence.sh`, `tests/rxtsource/run_rxtsource_tests.sh`.
- Manifests: `tests/startset/manifests/manifest_s2_vm_{auto,forced}.tsv`.

`tests/litscan/spanarms.rxt` and `tests/codegen/manifests/k50_gate_refinement.txt`
auto-merged. The merged spanarms.rxt has 84 blocks, which is base 18 + E2's
46 + R1's 20; nothing was duplicated or lost.

Every spec and doc conflict was unioned, and the text now states all three
units:
- ¶8c keeps E2's "successful attempt" wording and its zero-width clause, and
  adds R1's exact-repeat and saturation clauses.
- ¶4 is R1's text, with the tie rule's `rate:`.
- ¶4a names the arms `empty`, `zero` and `rep`.
- §2.28¶3 is R1's repeat sentence plus E2's zero-width sentence.

The axes `INTERNAL_ARMS` list now carries all three restore arms. The lever
fence ALLOW list covers rows S1921, S1922, S1928 and S1929 (`S192[1289]_`)
plus S446/S807.

## RECONCILED CODE

**One dispatch.** `rb_row_into(const RbWalk *w, RbVal *acc, const Ast *a)`
is now defined once. It reads the kind row's TEXT:
- ZERO goes to `rb_zero_into`, which is T3, `rb_zero_rows` (E2's
  first-match table: E-1 under arm `empty`, E-4/E-5 under `zero`, the last
  row being the old cut).
- ANY is the unbounded gap.
- OWN falls through to the gap.

Repeats keep their own declared table, reached from the `A_REP` arm:
T2's `rb_rep_rows` (E1 row 1 under `empty`, R1 rows 2-3 under `rep`, then
the two replaced forms). T2 and T3 stay two tables because their rows match
different inputs: a repeat plus its body's value, against a zero-width node.
Each unit's behaviour is behind its own rows and its own arm bit, and no
`if` reads a unit.

`rb_assert_into(const RbWalk *w, RbVal *acc)` (T3's CUT row) and
`rb_zero_unit_into` both call R1's threaded `rr_cat(w, ...)`. The
`walk_arms.def` rows are `EMPTY`, `ZERO` and `REP`. Bit order follows the
row order and no reader pins a bit.

**Constness.** The dispatch takes `const RbWalk *`. Every T2/T3 row reads
only the walk's parameters: `restored`, `cx` (the arena is reached through
the pointer), `pd` and `rate`. None of them writes walk state (`slot`,
`depth`, the `single[]` cache). R1's signature was already const. E2's
non-const one was not needed by anything inside it. The one caller,
`rb_walk_at`, holds a non-const `w` and passes it through.

`make strict`: clean (whole tree, `-Werror -Wshadow`).

## PINS

Each pin below was re-measured on the merged build through its own command:

- **[facts-arm]** (`tests/codegen/run_facts_checks.sh`): 12 passed, 0
  failed, after three re-pins. All three come from R1's rules acting on E2's
  cells:
  - `^a|abcd\Befgh$` under `zero` lists `61626364@1`. E2 alone gave
    `65666768@2`. The restored cut leaves `abcd`/`efgh` with equal
    information, and R1's `rn_choice_rows` takes the rarer.
  - `abcd()efgh` under `empty` lists `61626364` (E2 gave `65666768`), for
    the same reason.
  - `zd`/`ed` `req_whole_run` why is now `rate:builtin-prior`, R1's DERIVED
    relabel.
  - S1928 and S1929 still separate. An ignored arm lists the joined 7 or 8
    bytes, not the cut.
- **rxtsource census/C3** (`tests/rxtsource/run_rxtsource_tests.sh`, run
  standalone): 300 passed, 0 failed. Pins: main's value plus R1's own delta
  over base b819993a4:
  - census/RUNSH 318/6479/76520;
  - C3 PASS 22940, SKIP 53487, PCRE2ONLY 20617, VERIFIABLE 25353.

  The check's own reconcile line confirms them.
- **startset manifests**: the spanarms rows of both sides were unioned by
  (options, pattern hex): auto 34+20 gives 44, forced 64+38 gives 84. They
  were re-keyed to the merged file's lines with `startset_lib.corpus_blocks`
  ids, and all rows mapped. No row was added or dropped. VERIFIED ONLY BY
  the queued maketest (`test-startset`'s `[vm-movers]`).
- **k50 `#UNDECLARED`**: R1's `\Gcat\Kdog` row is RETIRED. With E2, `\G` and
  `\K` are width-0 units, so the run is `catdog`, `636174646f67@5` in BOTH
  encodings (measured). There is no tie, so there is no divergence, and the
  exact list must not keep an expired claim. E2's `(?:x\Kac|xab)` entry is
  unchanged: `786162@0/fffffe` byte, `@1` utf8 (measured). VERIFIED ONLY BY
  the maketest (`test-encoding-checks`).
- **run_prechecks.sh** (R1's re-pinned cells): 395 passed, 0 failed,
  standalone.
- **OWED to the maketest, not measured by hand** (each is checked by its own
  section): the simd-form floor 16 (main's value; it is an every-10th sample
  and spanarms.rxt grew 64 to 84 blocks, so it can drift again), the
  findings witness files, the memfn presence and pick witnesses, and the
  resource counts.

## HAND CHECKS

**The brief's identity statement cannot hold as written.** "restore=rep
equals main" is false in general. R1's tie rule (`rn_choice_rows`) has NO
restore arm: sar1fix made it unconditional, and its report says so. Any
equal-information tie therefore differs from main even with `rep` restored.

So each unit's identity is checked EXACTLY with a scratch PROBE. The probe
is the merged tree with `rn_choice_rows` cut to its first row, which is the
pre-R1 choice: information, then `a` on a tie, exactly base's `rn_better`.
The probe lives at `$PCREC_TMPDIR/scratch/sar1mrg/probe`, scratch only.

These are the exact pairs, all byte-identical artifacts required:

| pair | reference | working | reverts |
|---|---|---|---|
| A | lane/sar1 `restore=empty` | merged `restore=empty+zero` | E1 and E2: R1 alone, tie rule live in both |
| B | main 3f46eba9b | PROBE `restore=rep` | R1 |
| C | main `restore=empty` | PROBE `restore=empty+rep` | E1 + E-1, and R1 |
| D | main `restore=zero` | PROBE `restore=zero+rep` | E2's E-4/E-5, and R1 |

The tie rule's own effect is accounted for by the census below: it lists TIE
differences apart, and the ident check requires every mover to be a census
mover.

Smoke results (8 witnesses, `.c` artifacts):
- A, B, C, D and empty+zero+rep all showed 0 diffs.
- Merged vs main moved exactly the four R1 repeat witnesses. It did not move
  `abcd\Befgh`, `abcd()efgh`, `abcd(?:\b)*efgh` or `xyz(?<=yz)ab\Bcd`.
- An `emit_sweep` dry run through the wrapper binaries read 0 movers for
  B's pair and 4 for the negative control, merged vs main.

**Answers.** Nothing here changes an answer. The corpus answers are OWED to
the maketest and the axes job. The prechecks (395/0) and the facts checks
(12/0) are green.

## QUEUED GATES

Job scripts are in `$PCREC_TMPDIR/scratch/sar1mrg/jobs/` (`common.sh` holds
the hold gate, the wrappers and `pair()`). Every job is hold-aware: no start
19:00-01:00 unless `hold_lifted_<night>` exists. No job is chained on
another job's key; ident is ordered on the census's RESULT FILE.

| key | what | verdict line / log |
|---|---|---|
| main-sar1mrg-census | census_r1.py, REF = main 3f46eba9b, WORK = merged, corpus + bench | `== census COMPLETE:` in `census/summary.txt` |
| main-sar1mrg-ident | emit_sweep main vs merged, all streams + bench; ident_check.py over the census | `== ident_check COMPLETE: 0 unexplained` |
| main-sar1mrg-identarms1 | pairs A, B (exact) | `== identarms1: 2 of 2 pairs identical`; `arms/{A,B}/sweep.log` |
| main-sar1mrg-identarms2 | pairs C, D (exact) | `== identarms2: 2 of 2 pairs identical` |
| main-sar1mrg-maketest | make strict + make test (perfrun) | `maketest.log`; verdict = make's `*** [test-` lines |
| main-sar1mrg-axes | test-axes, AXES = the three restore arms | `axes.log` |
| main-sar1mrg-mech1 | S1905-S1910, S1915-S1923, S1925-S1929 (20 rows) | `mech1.log` `== mech run COMPLETE: 20 rows (... 0 ...)` |
| main-sar1mrg-mech2 | re-aimed S446 S463 S470 S474 S807 S1653 S1704 | `mech2.log` `== mech run COMPLETE: 7 rows (... 0 ...)` |

The identarms jobs depend on the scratch builds `main_ref/`, `sar1_ref/` and
`probe/` and on the `bin/` wrappers. Do not delete them before those jobs
end.

## STATE AT HANDOFF

STATE: delivered, validation OWED.
- Committed on lane/sar1mrg: the merge (e2ad73586) and this report.
- `make strict` is clean.
- Green by hand: facts checks 12/0, rxtsource 300/0, prechecks 395/0.
- OWED gate keys, all queued at prio 210-217: `main-sar1mrg-census`,
  `-ident`, `-identarms1`, `-identarms2`, `-maketest`, `-axes`, `-mech1`,
  `-mech2`.
- Likely re-pins if a gate goes red: the simd-form floor (sample drift),
  the startset spanarms rows (only if the merged corpus changes the dedup),
  and the k50 exact list.
- No rulings file was named in the brief.
- Open for the manager: the brief's "restore=rep equals main" was replaced by
  pairs A-D plus the probe, because R1's tie rule has no restore arm. Should
  the tie rule get its own arm? That is a design question, not done here.
