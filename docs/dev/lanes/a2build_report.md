# Lane a2build — [OPT-HYB-RESEED-FORM] A2: the round-1 bake-off read, no form clears, A2 not built (2026-10-03)

Opus. Branch `lane/a2build` from `lane/r1land` `d832fc2a` (abi 58). NOT
merged. Nothing under `src/`, `lib/`, `cli/`, `tests/` or `docs/spec/`
changed, so there is no abi event: the abi 60 / bit 45 / S460+ reservation
is unused.

## Summary (resume from here)

- **Verdict: no form clears the floor on both compilers.** A2 is not
  built. This is the README's own outcome: "If no form passes on both
  compilers, that is the finding, and A2 waits for a better spelling."
- **The deciding cell is possq `a?+a`.** It is the largest O-81 loss
  (bench ss ×1.2281, thr ×1.1939), and both rows are far outside any
  floor.
  - On gcc, only f1 reaches the deny.
  - On clang, no form does. The best is f3, still +3.95 ns per call and
    +342 us per pass (+11-12%). f1 on clang is +11.6 ns and +1,084 us.
- **Round 1 measured half its rows.** The run stopped after 20 of its 40
  (row, compiler) rows, not "after the last timing".
  - The pack carried an uncommitted `bakeoff.sh` whose line 66 fails under
    `set -e` on the first single-subject row (`lbvar`).
  - So these rows were never timed: the utf8 witnesses `lbvar`/`lbfix`/
    `lbneg`, which are Q3's re-calibration cells, and A1's own `lpatom`
    cell.
- **The clang lkapos/lkaverb f keep rows are UNMEASURED.** Their 31.5%
  "floor" is a deterministic layout effect, not noise:
  - `dL` reads 866 us on every one of its 15 launches;
  - `d` and `d2` read 1,264 us;
  - the launch spread is 0.1%.
  The re-run that settles them must measure `a`'s own layout spread. The
  kit now carries an `aL` variant for this.
- **The kit is fixed and a round-2 pack is built.**
  - It covers all 40 rows.
  - New form `f1i` is f1 with its one prefilter site forced inline.
  - Default forms are `ai f1 f1i f3 f3i`.
  - The pack is at
    `worktrees/a2build/scratch/round2/a2_bakeoff_r2.tgz`. It is uncommitted
    and goes when that scratch directory does.
  - It was built from the committed kit `9814f5f7`; its `MANIFEST` reads
    "kit clean".
  - A Mac plumbing smoke run timed 20 of 20 rows (gcc-16, 1 launch) with
    answers the same on every row.
- **Owed to the manager: round 2 on the Linux box**, about 40 minutes on
  one pinned core:

      scp worktrees/a2build/scratch/round2/a2_bakeoff_r2.tgz duxevents@100.69.121.107:<DIR>/
      ssh duxevents@100.69.121.107 'cd <DIR> && tar xzf a2_bakeoff_r2.tgz'
      cd <DIR> && nohup bash a2_bakeoff_r2/bakeoff.sh a2_bakeoff_r2 2 > bakeoff.log 2>&1 &

  The run is complete when the last line reads `timed rows: 40 of 40`. A
  fresh agent then reads `work/table.txt` plus
  `deltas.py work/raw.tsv "ai f1 f1i f3 f3i"` against §2's acceptance, and
  builds A2 if a form clears.

## 1. Step 1 — the table against the A2 criteria

The source is `studies/hyb_reseed_cal/bakeoff/results/round1_2026-10-03/`:
- `table.txt`, which shows the launch and layout floors apart;
- `deltas.txt`, the absolute deltas;
- `README.md`, the provenance.

Ratios are form/deny, where lower is faster.

**Acceptance** (xcall.md §6, the kit README):
- answers the same on every row;
- every improve row at or under 1 + floor on BOTH compilers;
- no keep row losing more than its floor against `a`.

Short-search rows run about 13-36 ns per call, so per D144 addendum 1 they
are read as absolute deltas (`deltas.txt`, ns per call). Find-all rows are
ms-scale, so their ratios stand.

**Improve rows at or under 1 + floor, per form:**

| form | gcc | clang | fails on |
|---|---|---|---|
| ai | 4/8 | 6/8 | possq s and f on both (gcc +10.1 ns, +1,198 us; clang +13.5 ns, +1,658 us) |
| f1 | 1/8 | 0/8 | clang possq (+11.6 ns, +1,084 us); every lka* s +0.9-1.3 ns on both |
| f2 | 1/8 | 0/8 | possq on both |
| f3 | 0/8 | 2/8 | gcc possq s +6.5 ns; clang lkaneg s +4.4 ns; clang possq +3.95 ns, +342 us |
| f3i | 4/8 | 4/8 | gcc possq +9.9 ns, +826 us; clang possq +5.5 ns, +586 us |
| f4 | 2/8 | 1/8 | possq on both |

### Per compiler

**gcc.**
- **f1 is the only form that recovers possq.** Short-search reads +0.13 ns
  per call against a 0.05 ns floor, essentially the deny. Find-all reads
  -210 us per pass, so it beats the deny.
- **f1 does not help the lka* short-search rows.** It reads +1.0-1.3 ns,
  the same as shipped `a`.
- **atalt find-all (0 re-seeds, 0 failed attempts) stays +29-64 us on every
  form** (+3-6%), against a 1.4 us floor. Some shape cost survives every
  spelling on gcc.
- **Forcing the prefilter inline (`ai`, `f3i`) is the only change that
  takes the lka* short-search rows below the deny**, to -0.3 to -2.0 ns. But
  it ruins possq (`ai` +1,198 us, `f3i` +826 us).

**clang.**
- **No form recovers possq.** f3 is the closest at ×1.111 short-search and
  ×1.123 find-all, which is +3.95 ns and +342 us. f1/f2/f4 are near ×1.33
  and ×1.39, little better than shipped (×1.38 / ×1.60).
- **f3 is the clang favourite elsewhere, except lkaneg.** That row is
  framed, and f3 makes it worse than shipped: +4.36 ns against `a`'s +2.11.
- **Forced inline again wins the lka* short-search rows** (`f3i` -1.0 to
  -1.6 ns).

So the forms that fix possq differ by compiler: f1 on gcc, f3 on clang.
The change that fixes the lka* short-search rows (forcing the prefilter
inline) hurts possq on gcc. No single form passes on both.

### Keep-row safety

- **gcc.** Every form keeps the lka-pos and lka-verb thr win (×0.425
  shipped). The worst keep loss against `a` beyond the floor is +0.6%
  (`f3i`); f1 reads +0.0%.
- **clang.** Both keep rows are UNMEASURED, for the layout-floor reason in
  the summary. Read raw against the launch floor, every form sits within
  +0.8% of `a` (f1 516 us against `a`'s 512 us). That reading is
  directional only until `aL` exists.
- **The other keep cells were never timed.** That is the utf8 synth-1m,
  gap64 and bursty families for lbvar, lbfix and lbneg.

### The ns-scale caveat

- **The stated floors on the short-search rows are 0.00-0.39 ns.** That is
  one re-link (`dL`) and one relaunch (`d2`). One re-link is a single
  sample of the layout distribution. The same run shows a single re-link
  moving a clang find-all binary by 31.5%.
- **So the ~1 ns lka* deltas are not decision-grade** in either direction,
  even though they clear the stated floor.
- **The verdict does not rest on them.** It rests on possq, at +4 to +13 ns
  per call and +6% to +60% per find-all pass. Those deltas sit 10-100× above
  any floor in the table, on both compilers.

### Answers

The same on every timed row.

### Recommendation

- Build nothing from round 1.
- Run round 2 (§3) on the fixed kit. Its one new spelling is `f1i`: f1's
  single-call-site loop, which recovers gcc possq, plus the forced-inline
  prefilter, which is the only change that wins the lka* short-search rows
  on both compilers. With one call site the inline duplicates nothing.
- If `f1i` also fails clang possq, the clang loss needs an asm-level
  attribution on x86 clang 21 before another spelling is guessed. f3 is the
  only clang-friendly shape seen so far, and it is the two-call-site one
  that R2 argues against. That attribution would be a separate lane.

One side observation, not filed: forcing the prefilter inline makes even
the SHIPPED retry (`ai`) beat the deny on the lka* short-search rows. So
inlining the entry prefilter may be a win for the fixed arm too, which is
separate from reseed. It is a D77 candidate for whoever owns the hybrid
entry. It is not measured here, because the deny was never inlined.

## 2. Step 2 — not executed

No form clears, so no emitter text, abi bump, deny flag, spec hunk, utf8
re-calibration, sabotage row or FILEPIN re-pin was written. This is the
brief's conditional ("if a form clears").

**Deny flag, decided now so round 2's builder does not re-litigate it.**
A2 is a re-spelling of the same machine:
- the same attempt set under `-e byte`;
- the same rows;
- the same `-fno-hyb-reseed` deny.

It is not a separate mechanism, so it takes no flag of its own, and
`-fno-hyb-reseed` stays the family kill switch. (Under `-e utf8` the block
becomes a byte budget by Q3. That moves where re-seeds happen, not
answers, and it is still the same mechanism.)

The build checklist the brief lists is unchanged for round 2's builder:
- abi 60;
- readers found by grep (D94);
- the `tuning.md` §2.35 byte-budget sentence (D80);
- utf8 re-calibration on `cjk*`/`asr-lb-*`;
- the structural codegen check;
- a sabotage row from S460;
- answer identity over corpus × startpos × engines;
- the mover census;
- the FILEPIN re-pin;
- the S370/S371/S372 re-aims.

## 3. The kit crash and the fixes

**The crash.** The pack's line 66 was:

    label="...$([ ${#files[@]} -gt 1 ] && echo "+N")"

With one subject file, `[ 1 -gt 1 ]` fails, so the substitution and then
the assignment return 1, and `set -e` ends the run. Every row before
`lbvar f cal/synth-dense.bin` has 3 or 42 subjects, so the run timed 20
rows and stopped silently, before the table step.

The committed `bakeoff.sh` (`fbf6bb2c`) already had `|| true`. **The real
defect is that the pack carried an uncommitted copy of the script**: it
was built from `bea57c8c`'s working tree, and the fix was committed after
the pack was built.

**The fixes** (commit `9814f5f7`, `studies/hyb_reseed_cal/bakeoff/`):

| file | change |
|---|---|
| `prep.sh` | Refuses a kit with uncommitted changes (`ALLOW_DIRTY=1` overrides, and the MANIFEST says so). The MANIFEST records `kit clean|DIRTY at <sha>` and the sha256 of `bakeoff.sh`, `table.py`, `cells.tsv` and `sdrv.c`. Ships `table.py`. |
| `bakeoff.sh` | The label is computed with no failing substitution. An ERR trap prints `bakeoff: STOPPED at line N (rc R): <command>`. An EXIT trap renders whatever `raw.tsv` holds. Adds the `aL` variant (`a` re-linked). `FORMS` is an env override, defaulting to `ai f1 f1i f3 f3i`. |
| `table.py` (new) | The table code, split out of `bakeoff.sh` so a stopped run re-renders with the kit's own code. It shows the launch and layout floors apart, marks a row UNMEASURED when its layout floor is over 10%, checks keep rows against `max(launch, \|aL/a-1\|)`, and ends with `timed rows: N of M` and a `NOT TIMED:` list. |
| `deltas.py` (new) | Absolute deltas: ns per call on short-search rows, us per pass on find-all rows (D144 addendum 1). |
| `mkforms.py` | Adds form `f1i`. |
| `results/round1_2026-10-03/` | `header`, `raw.tsv` (sha256 in its README), `table_manager.txt` (the manager's rebuild), `table.txt` (re-rendered), `deltas.txt`, and `README.md` (provenance, the stop mechanism, the clang floor). |

**Verified on the Mac** (plumbing only; these numbers are not evidence):
1. The round-2 pack ran end to end with `CCS=gcc-16 LAUNCHES=1 PASSES=1
   MINMS=1`: `timed rows: 20 of 20`, answers the same, every single-subject
   row and the `a1` row timed. Log: `scratch/round2/smoke.log`.
2. A planted row with a glob that matches nothing stops the run with
   `bakeoff: STOPPED at line 82 (rc 1): files=($(cd "$PACK" && ls $globs))`.
   It still renders the partial table and `timed rows: 1 of 21` with the
   NOT TIMED list, and exits rc 1. Log: `scratch/round2/stoptest.log`.
3. `table.py` over round 1's raw file reproduces the manager's ratios
   exactly and reports `timed rows: 20 of 40`.

**Round 2 is also the re-run that settles the clang keep rows.** `aL`
gives `a`'s own layout spread, and the keep allowance becomes
`max(launch, |aL/a-1|)` rather than the deny's 31.5% re-link swing. More
launches would not settle them, because the launch spread is already 0.1%.

## 4. Validation

- No `src/` change, so `make`, `make strict`, `test-codegen` and
  `test-registry` do not apply.
- `make -j4 CC=gcc-16` was built only as the pack's new compiler
  (`9814f5f7`, rc 0). The base compiler is `1f244692`, built from
  `git archive` in the scratch directory (rc 0).
- `prep.sh` verified 45 syntax and 75 capability subjects against the
  bench manifests (0 mismatched). It wrote nothing in pcrec-bench, and
  `git status` there is clean.
- The Linux box was used read-only: `scp` of `work/` and the pack, plus two
  `ls`/`cat` probes.

## 5. Files

- `studies/hyb_reseed_cal/bakeoff/` — the kit changes and `results/`, as
  in §3. CLAUDE.md and README.md are updated.
- `docs/dev/plan.md` — `[OPT-HYB-RESEED-FORM]` gains the round-1 read.
- This report and its index line in `docs/dev/lanes/CLAUDE.md`.
