# s21prep -- [MEMFN] R-14 slot21 PREPARATION (lane s21prep, sonnet, 2026-10-11)

Prepared, NOT run: the 5-arm RQ-4 timing harness and the slot script
`worktrees/memfn-slot/slot21/run.sh`. Branch `lane/s21prep`, cut from the kit
branch `lane/memfn-r14` @ 74b8e0fd. Nothing under `src/`, `cli/`, `lib/`,
`memfn/` or `tests/` changed.

## 1. Summary (resume from here)

- The harness (`docs/design/memfn/probes/rq4/`) takes a configurable arm list.
  New `rq4_arms.py` holds the arm sets and the pair definitions that `rq4.py`
  and `rq4_table.py` both read. `rq4.py --armset slot20` (the default) is
  slot20's three arms and is unchanged: a 3-arm tiny run's `meta.tsv` and
  `raw.tsv` headers are byte-identical to slot20's, and `rq4_table.py` re-renders
  slot20's `run/` to `out/slot20_table.md` byte for byte (`cmp` clean, checked
  after every table edit).
- `--armset slot21` = DEFAULT `-fmemfn-simd`; NOPAD `--memfn=no-vrun-pad` (trim
  only); FULL `--memfn=no-vrun-pad,no-vrun-trim` (R-13's verify); KBDENY
  `--memfn=no-vrun-kb`; OFF `-fno-memfn-simd`. `--armset slot21x` adds FULLKB
  (see 3.2). `--arm NAME=FLAGS` (repeated) builds any other list.
- The table reports, per (cell, regime, level), D-F (DEFAULT-FULL), N-F
  (NOPAD-FULL), D-N (DEFAULT-NOPAD), D-K (DEFAULT-KBDENY), F-K (FULL-KBDENY),
  ON-OFF (DEFAULT-OFF), each against its own null band (max |delta| over the
  cells whose two artifacts are byte-identical, from `meta.tsv`, as before). With
  `--prior slot20/run` it appends the re-read of slot20's 179 D-K losses.
- `slot21/run.sh`: ~3 h 30 min nominal, the 5-arm timing 114 min of it, run
  last. A dry run passed end to end (section 6). Before launch, `lane/s21prep`
  must be merged into the `worktrees/r14` tree: the script's preflight refuses
  a tree without `rq4_arms.py`.

## 2. Commits (lane/s21prep)

| commit | what |
|---|---|
| 03066cea | configurable arm list: `rq4_arms.py`, N-arm meta/table, `--prior`, `--estimate`, `--drop-regimes` |
| 9011673d | table legend and pair labels (slot20 re-render still byte-identical) |
| 0c24ed8e | the re-read counts the prior's sign; the prior is read at its own sib-max |
| 1d40997f | rq4 `CLAUDE.md` note, lanes index line |
| tip | this report |

`slot21/run.sh` and `slot21/dry_parse.py` live outside the tree (the slot
directory, like slot18/slot20).

## 3. The harness

### 3.1 What changed

| file | change |
|---|---|
| `rq4_arms.py` (new) | `ARMSETS` slot20/slot21/slot21x, `PAIRS` (name, description), `id_col` (slot20's `id_DK`/`id_DO`/`id_KO` kept, `id_<X>_<Y>` otherwise), `all_pairs`, `parse_arm` |
| `rq4.py` | arm list from `--armset`/`--arm` (DEFAULT required); emit/build/check/time loops and the artifact/binary/reading counts over `len(arms)`; `meta.tsv` gets `forms_<ARM>` per arm and an `id_*` column per arm pair; `arms.tsv` written; the plan (regimes) is built before anything is created, so `--estimate` prints reading count and wall and exits; `--drop-regimes GLOB,...`; the time START line prints the estimate. The answer-equality check (hits, FNV, position sum) already ran over every arm in the loop and still does |
| `rq4_table.py` | rewritten around a `Run` class (medians, answers, bands, `cmp`); arms from `arms.tsv`, else from `meta.tsv`'s `forms_*` columns (a slot20 run has none); pairs = those of `PAIRS` whose arms ran; slot20's two column headers (`KB verdict`, `SIMD verdict`) kept, others `<pair> verdict`; a pair legend printed only when the run has a pair beyond slot20's two; `--prior RUNDIR` |
| `CLAUDE.md` | the configurable-arms paragraph; `rq4_arms.py` and the table's roles |

The null band rule is unchanged. For a pair (X, Y) it reads the meta column
`id_col(X, Y)` (either order), so each pair gets its own null population: the
cells where that exact pair of artifacts is byte-identical. Pad does not apply
to runs outside L in {3,5,6,7}, trim does not apply to a one-position run, KB to
a cell with no second position, so the five pairs have different null cells
(the dry run's meta shows `id_DEFAULT_NOPAD`, `id_NOPAD_FULL` and the rest).

### 3.2 FULL-KBDENY is not slot20's comparison, text for text

The brief asks for slot20's D-K next to slot21's D-K and FULL-KBDENY, with FULL
reproducing slot20's sign. FULL is R-13's verify with KA and KB. slot21's KBDENY
is `--memfn=no-vrun-kb` with trim and pad still ON, so FULL-KBDENY compares
R-13's whole-run verify against the R-14 verify with KA alone. Slot20's D-K was
whole-run with KB against whole-run without it. The two share a sign only if the
trim and pad effects are small beside KB's. The table reports F-K as asked and
the re-read counts how many of the 179 keep the prior's sign under it.

The exact restatement needs a sixth arm, FULLKB (`no-vrun-pad,no-vrun-trim,no-vrun-kb`),
which is slot20's KBDENY text; F-FK = FULL - FULLKB is then slot20's D-K on this
build. It costs 6/5 of the slot (31,392 readings, 137 min instead of 114).
`S21_ARMSET=slot21x` adds it with no other change; the table picks it up. I did
not make it the default (the brief says 5 arms). Recommendation: run slot21x.
The 23 extra minutes buy the one comparison that settles whether the 179 losses
were KB's or the verify's.

### 3.3 Re-read of slot20's 179

`--prior` lists every slot20 D-K LOSS (re-derived with the same code, 179) next
to this run's D-K, F-K and F-FK on the same (cell, regime, level), prints how
many remain LOSS/NULL/WIN under each, how many keep delta > 0 (the prior's sign)
whether or not past the floor, and how many D-K LOSS in this run were not among
the 179. Self-check: slot20 re-read against itself gives 179/179 persisting
and 179/179 with delta > 0, 0 new. The prior is read at its own sib-max (5), not
the dry table's looser one. Where slot20's 179 sit:

| regime | D-K LOSS | | regime | D-K LOSS |
|---|---|---|---|---|
| space8 | 30 | | space256 | 4 |
| pc16 | 26 | | sweep/sparse-64k | 2 |
| space128 | 22 | | sweep/dense-1m | 2 |
| space64 | 21 | | tail-64k, tail-1m, sparse-1m, pc256, pc1024 | 1 each |
| short75 | 20 | | bench/* | 0 |
| pc64 | 17 | | | |
| space32 | 12 | | | |
| space16 | 11 | | | |
| sweep/dense-64k | 7 | | | |

## 4. Wall time and the cell question

Slot20 measured 4104 s for 15,696 readings (0.2615 s each, 51 cells, 872
cell-regimes with the subjects set, 3 launches, 2 levels) plus ~20 s of
emit/build/check. Readings cost the same whatever the arm, so the wall scales
with the arm count:

| arms | readings | est. | |
|---|---|---|---|
| 3 (slot20) | 15,696 | 68 min | reproduced exactly by `--estimate` |
| 5 (slot21) | 26,160 | **114 min** | + up to 3 x 10 min if the load1 < 1.5 wait holds |
| 6 (slot21x) | 31,392 | 137 min | |

114 min is under the ~2 h line, so all 51 cells and all regimes are kept. If
the manager wants a shorter run, the cut with the least information lost:
`S21_DROP='gate/tail-1m,sweep/*-1m,pc256,pc1024'` removes 255 cell-regimes (the
1 MiB twins of the 64 KiB regimes and the two longest per-call lengths), leaves
18,510 readings (81 min), and drops 6 of slot20's 179 losses (1+1+2+1+1) and 8 of
its 63 ON-OFF losses. Cutting further (the bench regimes, sparse-64k, tail-64k)
reaches 65 min but removes the throughput controls. Not recommended.

## 5. The slot script

### 5.1 Stages and wall estimates (from slot18's and slot20's logs on this box)

| stage | what | est. |
|---|---|---|
| PREFLIGHT | tree has `rq4_arms.py`, both deny base commits, `rows_for.sh`; stale-output refusal | 0 |
| BUILD, STRICT, SABANCHOR | `make -j16`, `make -j16 strict`, `scripts/m6read_check_sab_anchors.py` | 0.5 min |
| SWEEP plain | `emit_sweep --ref REF --tree-rev HEAD` | 1.5 min |
| SWEEP start | `--arms start` | 5 min |
| SWEEP variants | `--variant all` | 7 min |
| SWEEP simd | `--extra=-fmemfn-simd --no-differ-floor` (loud waiver, as slot18) | 13 min |
| SWEEP deny_full | wrapper `--memfn=no-vrun-pad,no-vrun-trim` vs 9fefd983, both `-fmemfn-simd`, streams c-default,c-vm, `--no-differ-floor` | ~5 min |
| SWEEP deny_pad | wrapper `--memfn=no-vrun-pad` vs 14143d53, same | ~5 min |
| G2 | `TMPDIR=$S make test-memfn-g2-full` | 22 min |
| MAKE_TEST | `scripts/perfrun --label memfn-r14`, then `git checkout -- docs/dev/artifact_size_log.tsv` | 15 min |
| MECH | 31 rows, `PROCS=4` | 18 min |
| SUBJECTS, RQ4, TABLE | the 5-arm timing, last, `--wait-load 1.5`; table with `--prior slot20/run` | 114 min |
| total | | ~210 min (3 h 30 min), ceiling ~4 h |

`REF` = `git merge-base HEAD main`, as slot18. A START line carries tip, ref, the
two deny bases, the tree and the armset. Every stage prints one line with its
rc (and wall for the long ones). A trap writes `verdict.txt` and `FAILED`
unless `DONE` was touched; `DONE` needs every stage green. `JUDGE` lines
are the sweep verdicts below; a CHECK makes the slot FAILED but later stages
still run (the timing is worth having either way).

Each SWEEP line shows movers per stream, summed over the sub-streams and
bases (facts, emit-ir-auto and stderr are one `other`), variants prefixed by
their name, `--arms start` with `arms=N armsmis=M` (arm lines whose two sides
disagree on differ/stamp/refusal). Example (slot18's accepted simd log through
the same function): `c-default=44 c-vm=43 emit-ir-vm=0 other=0 composition=0
dumps=1 arms=4 armsmis=2`.

### 5.2 Judges (and how they were checked)

| sweep | expected |
|---|---|
| plain, start, variants | every stream 0 except `dumps` <= 1 (`--list-axes`: the `vrun-trim` and `vrun-pad` rows); start also `armsmis` 0 |
| simd | c-default and c-vm > 0 (the vrun FUNC set; 44 / 43 at slot18), everything else 0 but `dumps` <= 1 |
| deny_full, deny_pad | c-default = c-vm = 0, rc 0 |

The judge and the summary were run on slot18's four real sweep logs
(plain/start/variants/simd): all four read ok. Seven planted summaries
(a mover in zero mode, dumps = 2, a deny mover, simd with 0 movers, an
asymmetry, `armsmis` 1, an empty line) each read CHECK; a clean deny line reads ok.
An empty summary (a crashed sweep) is a CHECK, rc >= 2 is a CHECK.

### 5.3 The deny wrappers: a finding

r14b specifies `--memfn=no-vrun-trim` on the tree side against 9fefd983 and r14p
`--memfn=no-vrun-pad` against 14143d53. On the combined tree the first no longer
reproduces the pre-R-14 rendering: with trim denied the padded word is still on
(measured: on `(?i)select`, `(?i)cat`, `(?i)eqeeez` trim-deny alone differs from
`no-vrun-pad,no-vrun-trim`; on `abcdef` they coincide, no vrun). The FULL pair
(`no-vrun-pad,no-vrun-trim`) is the heir of r14b's check and is the same flag set as
the timing's FULL arm. So the slot runs `deny_full` (vs 9fefd983) and `deny_pad`
(vs 14143d53). Both were checked in the dry run on the 51 RQ-4 cell patterns
(21 vrun artifacts reached, `--extra=-fmemfn-simd`): **0 movers on c-default and
c-vm for both**, so FULL = R-13's rendering and NOPAD = r14b's rendering on that
population before the slot spends an hour on the full corpus. The r14b-spec'd
trim-only wrapper is not run (it would read nonzero by design).

### 5.4 The mech rows (31) and how they were found

`bash tests/mech/rows_for.sh memfn/src/vrun.c memfn/src/runcmp.c` (D69's own
tool: SAB_FILE/SAB_FILE2 path match) gives 25 rows:
S267 S285 S443 S444 S445 S573 (runcmp.c) and S716-S723, S750-S753, S793-S799
(vrun.c / runcmp.c). Plus slot18's S570, S522, S686, S687, S691, S695 = **31**.
`run.sh` regenerates the list at run time (so a tree that moved is followed) and
compares it with the 31 found here, printing `MECH_ROWS 31 rows == ...` or the
difference. `VALIDATE_ONLY=1` over the 31 reads "31 definition(s) valid".

Rows from slot18's list that are NOT in this one: S724-S730 (ofsskip.c), S754
(compose.c, g2simd), S731-S737 (findings.c / emit_dfa.c). They are not anchored
in the two files and R-14 changed neither; adding them is 15 more rows, ~9 min.
S793-S799 and S716-S723 etc. were each run solo by r14b/r14p; the slot's batch is
their first run together.

### 5.5 Not in the slot

- N2 (the row-contract census): slot18 ran it, but neither r14b's nor r14p's
  owed list names it and R-14 adds no kit row. Add the slot18 line if wanted
  (~17 min).
- `make test-axes`: not owed by either report.

## 6. Dry run (S21_MODE=dry, tree = worktrees/s21prep, 37 s, `slot21/dryrun/`)

`verdict.txt` of the final dry run (the heavy stages are parse / `make -n` /
`VALIDATE_ONLY` / `perfrun --next` checks; the two deny sweeps run for real on
the 51 cell patterns; the timing runs `--tiny` with cells mi,m17,v11,kb,n01 and
the table with `--prior slot20/run`):

```
START 2026-10-11T02:50:03-04:00 mode dry tip 1d40997f ref 76428e05 ref9 9fefd983 ref14b 14143d53 tree .../worktrees/s21prep cpus 12-15 armset slot21 dirty=0
PREFLIGHT ok harness=docs/design/memfn/probes/rq4/rq4_arms.py
BUILD rc=0
STRICT rc=0
SABANCHOR rc=0 :: all anchors resolve
DRYCHECK sweep plain rc=0 :: ARGV-OK
DRYCHECK sweep start rc=0 :: ARGV-OK
DRYCHECK sweep variants rc=0 :: ARGV-OK
DRYCHECK sweep simd rc=0 :: ARGV-OK
DRYCHECK wrapper deny_full rc=0 :: exec .../build/pcrec --memfn=no-vrun-pad,no-vrun-trim "$@"
DRYCHECK wrapper deny_pad rc=0 :: exec .../build/pcrec --memfn=no-vrun-pad "$@"
DRYCHECK sweep deny_full rc=0 ::
DRYCHECK sweep deny_pad rc=0 ::
DRYCHECK deny deny_full ok :: c-default=0 c-vm=0 arms=4 armsmis=0
DRYCHECK deny deny_pad ok :: c-default=0 c-vm=0 arms=4 armsmis=0
DRYCHECK g2 make -n rc=0 :: TMPDIR=${TMPDIR:-/var/tmp} bash memfn/tests/run_g2.sh
DRYCHECK perfrun --next :: 4,4 (rc=0)
MECH_ROWS 31 rows == the 31 s21prep found (2026-10-11)
DRYCHECK mech VALIDATE_ONLY rc=0 :: == mech FIELD VALIDATION COMPLETE: 31 definition(s) valid, 0 rows measured ==
SUBJECTS rc=0 :: subjects: -> .../slot21/dryrun/subjects, sha256 mismatches 0
ESTIMATE arms DEFAULT,NOPAD,FULL,KBDENY,OFF: 51 cells, 872 cell-regimes, 3 launches x 2 levels x 5 arms = 26160 readings, ~6841 s (114 min) ...
RQ4 rc=0 wall=3s :: RQ4-RUN COMPLETE .../slot21/dryrun/run fails=0 readings=50 wall=3s
TABLE rc=0 :: .../slot21/dryrun/table.md (prior .../slot20/run)
SLOT21_DONE 2026-10-11T02:50:40-04:00 red=0
```

`DRYCHECK sweep X` for the four main sweeps ran the real argument vector through
`emit_sweep.py`'s own `main()` (argparse and every `ap.error` check) via
`slot21/dry_parse.py`, stopping at the first log line after them; a bad vector
(`--variant` without `--ref`) exits 2 (checked). The tiny timing's meta shows
the five arms' FORMS and the live dispatcher per arm per level (every vrun arm
live at w16/w32, OFF scalar), 50 readings, answers equal across the five arms
(check stage `answers=50`). The dry table's numbers are NOT readings (5 ms
loops, one regime, `--sib-max 100`). The dry run's emit_sweep output dirs, the
artifacts and the subjects were deleted afterwards (693 MB); the logs stay.
A second dry run needs `dryrun/DONE` moved away (the stale-output refusal).

Forbidden items not run: make test, test-axes, a full emit_sweep, G2, mech
batches, real timing.

## 7. Launch

```
cd /home/pcrec/projects/pcrec && git -C worktrees/r14 merge lane/s21prep      # kit manager: brings the harness into the tree
setsid nohup bash /home/pcrec/projects/pcrec/worktrees/memfn-slot/slot21/run.sh > /dev/null 2>&1 < /dev/null & disown
# or, for the 6-arm slot (recommended, 137 min timing):
S21_ARMSET=slot21x setsid nohup bash .../slot21/run.sh > /dev/null 2>&1 < /dev/null & disown
```

Completion: `slot21/DONE` (or `FAILED`), `verdict.txt`, last line `SLOT21_DONE`.
The reading is `slot21/table.md`; its tail is the re-read of the 179.

## 8. Charter vs delivered

| asked | delivered |
|---|---|
| configurable arm list, no hard-coded three | `rq4_arms.py`; `meta.tsv` and the table generated from the arm list |
| 5 arms, interleaved | slot21 preset; the rotated interleave already covered N arms; slot21x optional sixth |
| table pairs DEFAULT-FULL, NOPAD-FULL, DEFAULT-NOPAD, DEFAULT-KBDENY, DEFAULT-OFF with null bands | all five, plus F-K (and F-FK with slot21x), each with its own null population |
| re-read of the 179 | `--prior`; self-checked 179/179 |
| 3-arm mode, slot20 reproducible | default `--armset slot20`; headers and slot20's table byte-identical |
| answer-equality across all arms | the existing check, over all arms |
| time estimate, cut if > ~2 h | 114 min, no cut; cut knob and numbers in section 4 |
| `slot21/run.sh` with the listed stages | all, plus the deny sweeps, `JUDGE` lines, the dry mode |
| dry run | section 6 |
| report, lanes index line, rq4 CLAUDE.md note | this file, the index line, the CLAUDE.md paragraph |
