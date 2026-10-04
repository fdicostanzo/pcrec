# r1alpha — [OPTLOOP] round 1 Linux alpha timings, prepared and LAUNCHED (2026-10-04)

Lane r1alpha (sonnet), branch `lane/r1alpha` from main 8562ff3a; its sibling
`lane/a2fix` (from lane/a2build 98b13551) carries the A2 kit fix. The lane
PREPARED and LAUNCHED one serial driver on the Linux box and ENDED; the
timings are OWED (read the log, below).

## Driver

- Driver: `/home/duxevents/pcrec/scratch_lx/run_r1alpha.sh` (copy of
  `docs/dev/optloop/run_r1alpha.sh`), log `scratch_lx/r1alpha.log`.
- One `<ITEM>_RC=` line after each item (`VEDGE_RC`, `C1_RC`, `C3_RC`,
  `A2_RC`), then `ALL_DONE <date>`. Verdict = the item's own output file, not
  the RC alone.
- Strictly serial, CPU 2 (`taskset -c 2`), each item under `gnutimeout 7200`
  (A2: 3600, plus 900 s per row inside the kit).
- Per-item outputs under `scratch_lx/r1alpha/`: `vedge.out`, `c1.out`,
  `c3.out`, `a2.out`; scratch trees `vedge/ c1/ c3/`; a scratch clone
  `repo/` of the Linux checkout with the 8562ff3a + a2fix objects fetched
  from `r1alpha.bundle` (so nothing in the Linux working tree moved).
- Box at launch: load 0.04-0.9, no other heavy process (top: pcrecdev2's idle
  claude process only, 2% CPU). Nothing killed except this lane's own first
  driver launch (see below).
- Expected runtime: item 1 ~15 min, item 2 ~10 min, item 3 ~25 min (18
  cells x 3-4 subjects x 3 arms x 5 launches), item 4 ~2-3 min after
  compiles. Each script waits for load1 < 0.5 per cell (vedge: at most 10
  minutes per cell).

## Scripts checked against D144 addendum 1

| item | script | verdict |
|---|---|---|
| 1 [OPT-VEDGE] | none existed; §5/§7 give shell fragments driving `docs/design/sel_cost/percall.c` | percall.c calibrates to only 20 ms, reports one launch, no floor, and its `cp[1][2]` is the same overrun as the A2 bug below. NEW `docs/dev/optloop/alpha_vedge.sh`: >= 50 ms loops, 5 interleaved launches, `taskset`, ABSOLUTE ns/call delta beside the floor |DENY-BASE|, NULL inside it, no ratio anywhere, caps[64]. BASE = 74017b71 (the commit BEFORE vedge: 14e78104 already carries the feature, so it cannot be the base), NEW = 8562ff3a, DENY = NEW + `-fno-view-edge -fno-run-overlap -fno-req-run-fold` so it equals BASE modulo the abi digits and the `RX_RUN_WORDS 0` stamp (verified per cell by `check`) |
| 2 S4 C1 | `s4/alpha_c1.sh` | already conforming (60 ms calibrated loops, absolute ns/byte, floor, NULL). Two fixes, committed: DENY gets `DENYFLAGS` (default `-fno-run-overlap -fno-req-run-fold`) because NEW = 8562ff3a also carries C3, else DENY != BASE; and the abi-digit normalizer widened 5[5-8] -> 5[5-9] (abi 59). Note the NEW/BASE delta is therefore C1+C3 together; the DENY arm switches both off |
| 3 S4 C3 | `s4/alpha_c3.sh` | conforming as is (50 ms calibrated, ns/byte and ns/call absolute, floor, NULL; its normalizer already covers 58/59). BASE = a588c668 (abi 58) |

One mistake of this lane's own: the first launch's vedge `check` flagged
`DENY!=BASE` on every cell. The only difference was the `RX_RUN_WORDS 0` line
(abi 58 scaffolding); the normalizer now drops it (as alpha_c1.sh's does).
The lane stopped that first driver with `scripts/safekill` 2 minutes in,
fixed the script and relaunched; no timing had been taken.

## A2 bake-off remainder (lane/a2fix 7a1f6c50)

"Rows 39 and 40" are the lpatom label under gcc and clang: raw.tsv carries 20
labels x 2 compilers; rows 1-38 are the other 19 labels.

THE BUG. `studies/hyb_reseed_cal/shape/sdrv.c` declared `ptrdiff_t
caps[1][2]`. lpatom's pattern has a capture group, so any MATCHING subject
(`cap/lp-atomic-hit.bin`) makes `rx_search` write `caps[1]`, past the array,
and clobber the driver's timing accumulator: the driver printed `0.0` for
every iteration count and file set containing that subject (checked by
bisecting the 75 files: 20 files fine, 40 files 0.0; the single hit file
alone 0.0). The calibration `per` = 0.0 was floored by `max(per, 1.0)` to
1.0, so `it = ceil(50e6 / 1.0)` = 50,000,000 and each timed run took ~3
minutes. (Not a units issue: per-iteration, per-set summing is correct.)
Round 1's other rows are unaffected (their patterns have no groups, or the
subjects do not match).

THE FIX (a2fix): `caps[64][2]`; `bakeoff.sh` gains `ROWCAP` (wall seconds per
(row, compiler), default 900, cuts the launch loop and says so), a guard
that a calibration `per` under 1 ns SKIPS the row loudly instead of flooring
it, and `ONLY="id ..."` (rerun just those ids into the EXISTING work dir:
other ids' raw.tsv lines and binaries are kept, the named ids' lines are
replaced, `raw.before_only.tsv` is a copy made first).

PROTECTION OF ROWS 1-38: before launch `raw.tsv` was copied to
`scratch_lx/bakeoff/raw.rows1-38+partial39.r1alpha.tsv`; the pack's old
`bakeoff.sh`, `sdrv.c` and `work/header` are `*.pre_a2fix` beside them. The
driver copies the fixed `sdrv.c` and `bakeoff.sh` into the pack (the pack's
MANIFEST sha256 lines for those two files now describe the pre-fix files),
reruns `ONLY=lpatom ... bakeoff.sh . 2`, and the kit's EXIT trap renders
`work/table.txt` over all 40 rows. The a1 role builds only `a`/`d` variants
for lpatom; only its binaries are rebuilt.

## Owed

1. The four item results (logs above). Reading rule: D144 add. 1 — absolute
   deltas vs the floor, inside the floor = NULL, ns-scale never a percentage,
   Mac numbers never a verdict.
2. The vedge short-call regressions (`(?:\d{4})\z` etc.) become issue rows
   ONLY if `alpha_vedge.sh`'s Linux delta clears its floor.
3. C1's `overlap` row: Q3 (ships only on a win beyond the floor).
4. Not merged, not pushed: `lane/r1alpha` (scripts + this report) and
   `lane/a2fix` (kit fix) wait for the manager. `docs/dev/optloop/s4/
   CLAUDE.md`, if it lists scripts, is unchanged (no files added there).
