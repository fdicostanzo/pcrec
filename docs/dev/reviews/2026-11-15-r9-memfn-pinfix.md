# crit-memfn-pinfix: single critic, code round r9-memfn-pinfix (2026-11-15)

Subject: `git diff 38869c333 9d5bbd9dd` (slot est.py / sabotage.sh) + jobs `pinfix/jobs.bak/` -> `mcfixa/jobs/`.
Method: export at 9d5bbd9dd under `x/` (plus `build/libpcrec.a` copied read-only from worktrees/mfind, because
`_synth` links the fixture binary); every repro below ran against that export, in scratch, with no make, suites or
queue jobs. Scripts: `tools/q1.py`, `tools/q1b.py`, `tools/q3.py`. Logs: `st_slot.log`, `st_slotP.log`.

## Verdict: LAND after the listed fixes. Only ADQ-2-1 is worth fixing before tonight's window (one line). The rest are fix-soon or notes. Nothing blocks.

## Q1: constructed records (ADQ-3)

`python3 -I tools/q1.py x/docs/design/memfn/span_cards/slot q1` (mfcard-window `_synth` record, then edited):

```
control (mfcard, all pins)            PRICED (99 rows)
del manifest_sha256_{J2,J2p,JMB,JMH}  REFUSED: MANIFEST PIN absent job ..: the record (window mfcard) ...   (each, 4/4)
del cells_sha256_{J2,J2p,JMB,JMH}     REFUSED: CELLS PIN absent cells.<j>.tsv ...                          (each, 4/4)
wrong manifest_sha256_* / cells_*     REFUSED: MANIFEST MISMATCH / CELLS PIN (each, 8/8)
del ALL pins (windowed)               REFUSED: CELLS PIN absent cells.J2.tsv
legacy: no window, pins kept          PRICED (99 rows)
legacy: no window, no pins            PRICED (99 rows) | 4 NOTE
legacy: no window, wrong manifest pin REFUSED: MANIFEST MISMATCH job J2
window empty value, no pins           REFUSED: CELLS PIN absent ... (window )
window empty value, pins kept         PRICED (99 rows)
window=s2d, no pins                   REFUSED: CELLS PIN absent ... (window s2d)
window key, no value field            CRASH IndexError: list index out of range
```

The real legacy records still price: `tools/q1b.py` on `scratch/memfn/s2d/s2d-20261106` and `s2d-20261107a` gives
PRICED 38 rows each, with 5 NOTEs. Both have no `window`, `cells_sha256_*`, `manifest_sha256_*` or `d197_*` key
(checked by an awk survey of every run_record.tsv under scratch/memfn).

Other readers of the pins: `git grep cells_sha256|manifest_sha256` at 9d5bbd9dd finds only est.py (manifest_check,
read_cells) and record.py (writer). Other code that reaches the pins goes through those two functions:
d197_rule.py through est.compute, rmax_drill.py through est.read_record (run_id only) on s2d records, and est.notes
through read_cells. No other reader tolerates a missing pin. Every promised verdict holds.

### ADQ-3-1 (note): "legacy" rests on a single line
`legacy_record` means "no `window` key". A record with its `window` line deleted along with its pins prices with
NOTEs (rows "legacy: no window, no pins" above). finalize writes `window`, and `window()` writes the D197 rule pins
`d197_rule_tsv_sha256` / `d197_rule_py_sha256` at every step since r6. Neither real legacy record carries either key.
**Proposed disposition:** optional hardening. Treat a record as legacy only when it has neither a `window` key nor a
`d197_rule_*_sha256` key, which costs one more condition and one more selftest case. Otherwise accept as ruled: the
ruling names `window` as the discriminator, and the pins guard the cells and manifest files, not the record itself.

### ADQ-3-2 (note, existed before this change): a `window` line with no tab crashes
`read_record` runs `rec["run"][f[0]] = f[1]`. A key-only line raises IndexError instead of InputError. An empty
value (`window\t`) behaves as promised: refused when pins are absent, priced when they are present.
**Proposed disposition:** note. If convenient, make a malformed run line an InputError.

### ADQ-3-3 (fix soon): m7 plants only the cells site
The manifest site (`manifest_check`, selftest S3225) has a selftest case but no sabotage row. If someone turns that
condition back into `if False`, no plant detects it. **Proposed disposition:** add m8, the same shape as m7, on the
`manifest_check` line with want `\[r8 ADQ-3 S3225\][^\t]*\tWRONG`.

## Q2: the 609/610 command lines (ADQ-2)

Scratch copy of the jobs dir under `root/scratch/memfn/mcfixa/jobs` with `PCREC_TMPDIR=root`, a stub `python3` that
echoes its argv, and a scratch window.vars. Nothing was written to the real jobs dir. Output trimmed to the
d197_rule.py call, with `R=.../run/mfcard-zen4-2`:

```
unset        609: d197_rule.py rule R R.avx2libc                                  rc 0
             610: d197_rule.py rule R R.avx2libc --confirm R.confirm R.confirm.avx2libc
both         609: ... rule R R.avx2libc --second /x/first /x/first.avx2libc       rc 0
             610: ... rule R R.avx2libc --second /x/first /x/first.avx2libc --confirm R.confirm R.confirm.avx2libc
only FIRST   609+610: "window.vars: FIRST_RUNDIR and FIRST_RUNDIR_AVX2 are set together or not at all" rc 1
only AVX2    the same, rc 1
FIRST= (empty) + AVX2 set   the same, rc 1
path with a space           quoted correctly (array expansion)
```

Both states build the intended line. The half-set state refuses for every job, because the check runs while
common.sh is sourced, before any case arm. 610 takes the first-run pair from window.vars through common.sh, with no
hard-coded paths. d197_rule.py's parser accepts `--second A B --confirm C D` in that order (main, lines 529-538).

### ADQ-2-1 (fix before tonight; one line): environment leaks into FIRST_RUNDIR
common.sh resets `RUN_ID="" FROZEN=""` before it sources window.vars, but line 43 is
`FIRST_RUNDIR=${FIRST_RUNDIR:-} ...`. With window.vars holding no FIRST_* entries and both variables exported in the
caller's environment:
```
FIRST_RUNDIR=/env/a FIRST_RUNDIR_AVX2=/env/b bash 609  ->  ... rule R R.avx2libc --second /env/a /env/b
```
A first run silently becomes a `--second` call. That breaks the promise that "when unset, the first-run call is
unchanged". d197_rule would then judge the run against the named records and could score NOT-WIN where a first run
gets INCONCLUSIVE. The trigger is unlikely: boxqueue's job environment would have to carry the variables. The fix is
trivial, though. **Proposed disposition:** add `FIRST_RUNDIR="" FIRST_RUNDIR_AVX2=""` to line 30, beside RUN_ID and
FROZEN, and keep line 43 or drop it.

### ADQ-2-2 (note): the half-set refusal exits 1 for --ready too
Because the check fires while common.sh is sourced, a half-set window.vars makes `--ready` of 600-610 exit 1, not
75 or 77. That is a refusal, as the promise asks. Whoever reads boxqueue should expect a ready error, not a wait.
**Proposed disposition:** note only.

## Q3: does anything change what a valid pinned record scores?

No. The change only adds refusals that raise before anything is read, and `legacy_record` has no side effects.
Repro: `tools/q3.py` compared est.compute's full result (sha-256 of its repr) with est.py at 38869c333 (`x0/`)
against est.py at 9d5bbd9dd (`x/`):
```
                     38869c333          9d5bbd9dd
q1_control (mfcard)  f7aa680197116c4d   f7aa680197116c4d
s2d-20261106         40de05e33010869b   40de05e33010869b
s2d-20261107a        769a4412a55fe153   769a4412a55fe153
```

## Q4: does m7 fail for its stated reason?

Yes. I planted m7's exact replacement in a copy (`slotP/est.py`); the anchor occurs exactly once, as sabotage.sh's
`patch` requires. Then I ran `est.py selftest` both ways:
```
unplanted: [r7 RULE-2, r8 ADQ-3] legacy ... ok | [r8 ADQ-3 S3224] ... ok    | [r8 ADQ-3 S3225] ... ok
planted:   [r7 RULE-2, r8 ADQ-3] legacy ... ok | [r8 ADQ-3 S3224] ... WRONG | [r8 ADQ-3 S3225] ... ok
```
m7's want regex `selftest\t\[r8 ADQ-3 S3224\][^\t]*\tWRONG` matches the planted log. Only the targeted case flips.
Limitation: the full `sabotage.sh SCR m7` run needs a git tree (its control dry run fails with rc 128 in an archive
export), and the tail of `est.py selftest` (the reading and gate cases) needs `build/pcrec`. Every MF case,
including the three ADQ-3 cases, ran with 0 WRONG before that point. I did not build anything, per the brief.

## RULED (kit manager, 2026-11-15 ~15:45)
- ADQ-2-1 FIXED by the manager in the timing jobs' common.sh (kit scratch): FIRST_RUNDIR / FIRST_RUNDIR_AVX2 reset beside RUN_ID/FROZEN before window.vars is sourced; checked: a caller env carrying both no longer yields --second.
- ADQ-3-3 (no sabotage plant for the manifest pin site S3225): PLAN, owed by the kit after tonight's window: a row m8 in slot/sabotage.sh; trigger = the next slot harness change, or the d3wire lane, whichever comes first.
- ADQ-3-1, ADQ-3-2 (pre-existing IndexError on a key-only run line), ADQ-2-2: NOTED.
- Verdict: LAND.
