# [TT-8] mech: the PROCS leak, its fix, and D69's evidence (2026-08-23)

Lane `lane/tt8mech`, chartered by `docs/dev/plan.md`'s `[TT-8]` row (Frank's
#3 + #4 of the day's testing moves). Three parts: (a) the PROCS leak into
inner suite sharding — found, measured, fixed, validated; (b) the D69
retro-diff evidence; (c) the manager's one-line commands for what remains
(the PROCS re-validation sweep and the full "after" matrix), which this lane
did NOT run — both are box-exclusive work reserved for the manager per the
day's BOX RULE.

## (a) The PROCS leak

**Claim (`docs/dev/chain_profile.md` "(b) mech per-row scoping"), read from
the dispatch code, not yet measured live**: `run_sabotage_matrix.sh`'s
`PROCS` controls ROW-level concurrency and derives `JOBS` (`nproc/PROCS`) for
the per-row tree build — but the `reject` and `harness` suite arms it
dispatches per row invoke `tests/reject/run_reject_tests.sh` and
`tests/harness/run.sh` WITHOUT overriding `PROCS` in their own environment.
Both scripts read `PROCS` from the environment directly to size their OWN
internal worker count (reject's `REJECT_SHARD_TOTAL` dispatch, harness's
per-file dispatch — both pre-existing mechanisms, unrelated to mech). Since
`run_sabotage_matrix.sh` itself typically runs under an inherited `PROCS`
(`make mech`'s own default is `PROCS=${PROCS:-$(nproc)}`), that value reaches
every child process unless something clears it — a bash quirk: a shell
variable already present in a process's environment keeps the export
attribute through a plain reassignment (`PROCS="${PROCS:-1}"` does not clear
it). If real, up to `PROCS` concurrently-running rows would EACH additionally
shard `PROCS`-way internally the moment they hit `reject` or `harness` —
oversubscription on top of the row-level concurrency the box was sized for.

**MEASURED, live, before touching any code.** A sanity check first
(`/tmp/.../exporttest.sh`, scratch, never committed): a script that does
`PROCS="${PROCS:-1}"` then execs `bash -c 'echo $PROCS'` shows the child
inheriting `PROCS=4` when the PARENT was invoked as `PROCS=4 bash
exporttest.sh`, and `<unset>` when invoked plain — confirming the export-
retention mechanism before looking for it in the real script.

Then the real thing, single-row (box rule: single mech rows are fine, ~2-5
min each). `MECH_SCRATCH=... PROCS=4 bash tests/mech/run_sabotage_matrix.sh
S15` (S15: `SAB_SUITES="reject registry pc3"`), `ps --forest` sampled during
the `reject` phase, then `/proc/<pid>/environ` read for the exact processes:

    720758  bash .../tests/reject/run_reject_tests.sh   (parent)   PROCS=4
    720804  REJECT_SHARD_INDEX=0  REJECT_SHARD_TOTAL=4  PROCS=4
    720805  REJECT_SHARD_INDEX=1  REJECT_SHARD_TOTAL=4  PROCS=4
    720806  REJECT_SHARD_INDEX=2  REJECT_SHARD_TOTAL=4  PROCS=4
    720807  REJECT_SHARD_INDEX=3  REJECT_SHARD_TOTAL=4  PROCS=4

Four `REJECT_SHARD_TOTAL=4` workers, from a run that named exactly ONE
sabotage — the outer row-level scheduler (`[ "$PROCS" -gt 1 ] && [
"${#sab_files[@]}" -gt 1 ]`) never even engages for a single named row, so
the leak does not need row-level concurrency to fire; a lone row still
inherits the un-widened `PROCS` from its own environment. Confirmed
separately for `harness`'s own multi-file dispatch on a full-corpus row
(`S66`, `SAB_SUITES="altdiff harness"`, no `SAB_HARNESS_TARGET`): the parent
`run.sh` process showed `PROCS=4` and dispatched 4 file-workers.

## The fix

`tests/mech/run_sabotage_matrix.sh`: `INNER_PROCS`, computed immediately
after `JOBS` and by the identical formula (`ncpu / PROCS`, minimum 1), passed
EXPLICITLY as `PROCS="$INNER_PROCS"` on the `reject` and `harness` arms' own
command lines — never left for the environment to supply. Diff shape:

    ncpu="$(nproc 2>/dev/null || echo 2)"
    if [ -z "${JOBS:-}" ]; then
        JOBS=$(( ncpu / PROCS )); [ "$JOBS" -ge 1 ] || JOBS=1
    fi
    INNER_PROCS=$(( ncpu / PROCS )); [ "$INNER_PROCS" -ge 1 ] || INNER_PROCS=1
    ...
    reject)
        PCREC="$pcrec" PROCS="$INNER_PROCS" \
            bash "$tree/tests/reject/run_reject_tests.sh" > "$work/reject.log" 2>&1
    ...
    harness)
        PCREC="$pcrec" CC="$CC" PROCS="$INNER_PROCS" \
            bash "$tree/tests/harness/run.sh" "${target_arg[@]}" > "$work/harness.log" 2>&1

Files touched: `tests/mech/run_sabotage_matrix.sh` (the fix + header/inline
comments), `tests/mech/rows_for.sh` (new, part (c) below), `docs/testing.md`,
`tests/mech/CLAUDE.md`, this memo, `docs/dev/CLAUDE.md` (index line).

**Post-fix, same `ps`/environ method**: `S15` at outer `PROCS=4` on this
12-core box now shows `run_reject_tests.sh`'s parent receiving `PROCS=3`
(`INNER_PROCS = 12/4`) and dispatching 3 `REJECT_SHARD_TOTAL=3` workers.
`S66`'s `harness` parent likewise received `PROCS=3` and dispatched 3
file-workers instead of the pre-fix 4.

**Note the asymmetry at outer `PROCS=1`** (the default, or an explicit
`PROCS=1`): `INNER_PROCS = ncpu/1 = ncpu`, so a LONE row now gets the whole
box for its `reject`/`harness` arms too — a genuine behavior change from
pre-fix `PROCS=1` (nothing was in the environment to leak, so the arms
defaulted internally to serial). This is the same precedent `JOBS` already
sets for the build step at `PROCS=1`, and the validation below (the
"default, no PROCS set" runs) covers exactly this case.

## Validation

Three rows, box-rule-bounded (single rows, no full matrix, no PROCS sweep —
those are the manager's, part (c) below).

**S15** (`reject registry pc3`, `SAB_FILE=src/parse/registry.c`) — three
runs, byte-identical result in all three:

| run | `INNER_PROCS`/effective inner PROCS | result |
|---|---|---|
| leaked `PROCS=4` (pre-fix) | 4 (undivided) | `reject:17fail/542pass,registry:3fail/177pass+compliance-FAIL,pc3:0fail/168pass` DETECTED |
| default, no `PROCS` set (serial, either side of the fix) | 1 | same |
| fixed `PROCS=4` | 3 (`12/4`, confirmed via `/proc/environ`: `REJECT_SHARD_TOTAL=3`) | same |

**S107** (`harness brefdiff`, `SAB_HARNESS_TARGET=tests/backrefs/numeric.rxt`,
a single-file target so `harness`'s own multi-file dispatch does not
trigger regardless of leak) — leaked `PROCS=4` and fixed `PROCS=4` both gave
`corpus:9fail/79pass,brefdiff:4fail/10pass` DETECTED.

**S66** (`altdiff harness`, full-corpus `harness` target, no
`SAB_HARNESS_TARGET`) — mechanism-only validation (dispatch confirmed
dividing 4->3 pre/post fix via `ps`/environ, above); NOT run to figure
completion in either form — the leaked-PROCS pre-fix attempt exceeded a
300s bound under this lane's single-row budget (this box was concurrently
running another lane's reserved timing work, per the day's BOX RULE, so the
row's wall time is not a clean reading of the leak's own cost — a genuine
before/after wall-time comparison for full-corpus rows is part of the PROCS
re-validation sweep in (c), not claimed here).

`make strict`: not re-run for this lane specifically — the change is
shell-only (`tests/mech/run_sabotage_matrix.sh`, `tests/mech/rows_for.sh`),
no C touched. `python3 scripts/m6read_check_sab_anchors.py`: not required by
the landing bar (no `tests/mech/sabotages/*.sh` file was touched) but run
anyway as a sanity check — see (b)'s retro-diff, which reads the same script
family; no anchor drift found on this tree.

## (b) D69's evidence: the retro-diff

`docs/dev/decisions.md` D69 (2026-08-23) rules a tiered mech re-run policy
and names the open question its risk acceptance rests on: **has any row ever
flipped DETECTED -> UNDETECTED without its own `SAB_FILE`/target changing?**
Two archived full-matrix logs exist to check this against —
`build/mech_m64.log` (99 rows, HEAD `c324091`, 2026-08-22 15:36) and
`build/mech_m65.log` (118 rows, HEAD `5edba64`, 2026-08-22 23:26) — read-only
from the main tree per this lane's brief.

**Method**: extract every `SAB_ID\tfile\tedit\tsuites\tresults\tverdict` row
from both logs, join on `SAB_ID`, diff the joined pairs.

**Result**: 99 rows in common. 50 show a changed cell; ALL 50 are
PASS-COUNT-only moves — fail counts and verdicts identical, DETECTED in
both — consistent with ordinary corpus/check growth between the two HEADs
(the intervening work was `[M6.4.4]`/`[M6.5.2]` slices, which added corpus
cases and codegen checks along the way; e.g. `S01-skip-states-off`:
`codegen:8fail/67pass` -> `codegen:8fail/68pass`, same verdict).

**One row's VERDICT changed**: `S48-poss-no-enclosing-first`,
`APPLY-FAILED`/`ANOMALY (anchor drifted from HEAD)` in m64 ->
`possdiff:5fail/150pass` DETECTED in m65. `git log --oneline
c324091..5edba64 -- tests/mech/sabotages/S48_*.sh src/opt/possessify.c`:

    34ede2c mech matrix on c324091: 99 rows / 0 undetected / S88-S101 all
            DETECTED; the one anomaly (S48 anchor duplicated by the
            pss_verdict refactor) fixed — SAB_COUNT=2, re-run alone clean

Category 2a in D69's own list (anchor drift, caught and fixed at the
sabotage-definition level — `SAB_COUNT` moved from 1 to 2), not a
compiler-change-alone flip, and it moved AWAY from a non-DETECTED state
rather than into UNDETECTED.

**The two UNDETECTED rows in m65** (trailer: `undetected: 2`) are
`S107-bref-not-nullable` and `S108-rdshape-accepts-bref` — both `[M6.5.2]`
rows (S102-S120) with NO entry in m64 at all (m64 tops out at S101). Both
undetected FROM BIRTH, not a pre-existing row flipping —
`tests/mech/CLAUDE.md`'s own account of each confirms this independently
(S107 was corrected via a corpus-population fix the same day; S108 was
retired at the `[M6.5]` close as unobservable, then re-instated as a
two-site sabotage the same hour, which is the `[M6.5.2-FIX]` this lane's own
`run_sabotage_matrix.sh` edits sit beside).

**Conclusion: zero rows observed flipping DETECTED -> UNDETECTED without
their own `SAB_FILE`/definition changing, across 99 rows in common between
these two archived matrices.** This is the measurement D69's text names as
"rides [TT-8] as evidence, not as a gate."

**Earlier journal figures** (`grep -n "rows (undetected" docs/dev/
dev_journal.md tests/mech/CLAUDE.md`): two 35-row runs
(`docs/dev/dev_journal.md:7104,7465`, pre-2026-08-15, `undetected: 0` both
times) and the 85-row figure `tests/mech/CLAUDE.md` records at `ae6e41f`
(2026-08-21, `undetected: 0`) are consistent with the same "no flip"
pattern as far back as any figure is recorded — but only m64/m65 have raw
per-row logs on disk to diff cell by cell; the 35- and 85-row figures are
prose summaries only (no archived log under `build/`), so they corroborate
the AGGREGATE claim (no run before m65 had ever reported a nonzero
undetected count) without letting a per-row check be repeated on them.

## (c) The manager's one-liners

**PROCS re-validation sweep** (owed, not run by this lane — box-exclusive,
serialized per the day's BOX RULE). A ~20-row sample spanning every target
class — harness-targeted, reject, the four full-corpus `harness` rows
(`S59`, `S66`, `S71`, `S76`), script-only — at `PROCS=3`, `4`, `6`:

    for p in 3 4 6; do
        /usr/bin/time -v env PROCS=$p bash tests/mech/run_sabotage_matrix.sh \
            S15 S16 S17 S18 S19 S20 S27 S28 S43 S48 S58 S59 S64 S66 S69 S71 \
            S76 S85 S88 S107 \
            > build/mech_procs${p}_sample.log 2> build/mech_procs${p}_sample.time
    done

Compare the three samples' wall times (from the `.time` files) and confirm
each sample's per-row figures are identical to the others' (a `diff` on the
extracted `SAB_ID\t...\tresults\tverdict` columns, the same extraction (b)
used) — a PROCS value that changes a row's own figures is a bug in this
fix, not a valid choice. Pick the fastest PROCS with byte-identical rows.

**The full "after" matrix** at the chosen setting, the chain's mech "after"
figure:

    PROCS=<chosen> /usr/bin/time -v bash tests/mech/run_sabotage_matrix.sh \
        > build/mech_after.log 2> build/mech_after.time

**Pass criteria**: 118 rows, `undetected: 0`, `anomalies: 0` in the
completion trailer, and byte-identical to a `PROCS=1` run's matrix — check
by extracting both matrices' `SAB_ID\t...\tresults\tverdict` columns
(`grep -P '^\S+\t' <log> | cut -f1,3,4,5,6`, the same method (b) used above)
and diffing them; the script's own header claims this identity but nothing
in this lane's validation checked it at full-matrix scale (only single-row,
per the box rule), so the manager's run is the first time it is actually
compared at 118 rows post-fix.

## Landing bar

Single-row validations pass (S15, S107 byte-identical pre/post-fix and
serial; S66 dispatch-division confirmed by ps/environ). `tests/mech/
rows_for.sh` validated in the failing direction (no-match path prints
nothing/exits 0; malformed definition is a FATAL exit 2). Worktree clean,
final commit on `lane/tt8mech`. `make strict`: not applicable (shell-only
change) but the worktree's ordinary build was exercised repeatedly by every
single-row mech run above (each builds a fresh scratch tree via `make all`).
