# [OPT-HYB-RESEED-FORM] A2 — the form bake-off, run instructions

Picks A2's emitted form (docs/design/xcall.md §4 A2, manager ruling on §7
Q4) by timing hand-rewritten artifacts on the bench's two compilers, x86
gcc AND clang, BEFORE any emitter text is written. The Mac cannot pick it:
F2, semantically identical to F1, read x1.742 there.

## Round 1 and round 2

**Round 1** (Linux, 2026-10-03, pack from `bea57c8c`) is in
`results/round1_2026-10-03/` with its provenance. It timed 20 of its 40
rows: the pack carried an uncommitted `bakeoff.sh` whose label line failed
under `set -e` on the first single-subject row (lbvar), so the utf8 cells
and A1's `lpatom` cell were never timed. No form cleared both compilers
(`docs/dev/lanes/a2build_report.md`).

**Round 2** (lane a2build) re-runs every row with the fixed kit, adds the
`f1i` form and the `aL` variant (the keep rows' layout floor), and drops f2
and f4 from the default `FORMS` (each lost to f1 or f3 on the rows that
decide round 1). Its pack is built by step 1 below from a committed kit.

## Manager: three steps

1. **Build the pack (Mac, ~1 min).** From a tree at the lane tip, with main's
   compiler at the branch point for the A1 cell:

       bash studies/hyb_reseed_cal/bakeoff/prep.sh \
           $PWD/build/pcrec  <BASE>/build/pcrec  /Users/fdicostanzo/pcrec-bench  <OUT>/rsform_bakeoff

   (lane rsform built one at `worktrees/rsform-scratch/rsform_bakeoff.tgz`,
   892 KB, new = lane tip `bea57c8c`'s compiler, base = main `1f244692`'s; it
   is uncommitted and goes when that scratch directory does.) prep.sh
   regenerates the subjects from the bench's own generators, sha256-verified
   against its manifests (45 syntax + 75 capability), writes nothing into the
   bench checkout, and refuses a cell whose artifact does not stamp the row
   the bake-off assumes.

2. **Copy it (tailnet):**

       scp <OUT>/rsform_bakeoff.tgz duxevents@100.69.121.107:<DIR>/
       ssh duxevents@100.69.121.107 'cd <DIR> && tar xzf rsform_bakeoff.tgz'

3. **Run it (the one command; ~45 min on one pinned core, both compilers):**

       cd <DIR> && nohup bash rsform_bakeoff/bakeoff.sh rsform_bakeoff 2 > bakeoff.log 2>&1 &

   The second argument is the core (`taskset -c`); pick an idle one and keep
   the box quiet (one heavy suite at a time). The table is the tail of
   `bakeoff.log` and `rsform_bakeoff/work/table.txt`; the raw launches are
   `rsform_bakeoff/work/raw.tsv`. `CCS`, `LAUNCHES` (15), `PASSES` (7) and
   `MINMS` (50) are environment overrides.

## Reading the table

One row per (cell, regime, compiler): the deny's ns, then each variant's
median over the launches divided by the deny's, two floors, and `ans`
(every variant's answer hash equals the deny's). `launch` is `|d2/d-1|`, the
same binary relaunched. `layout` is the larger of `|dL/d-1|` and `|aL/a-1|`,
the same source re-linked in the other order. They are reported apart
because round 1 showed they differ in kind: clang lkapos/f read launch 0.0%
and layout 31.5%, every launch of each binary within 0.5%, which is a
deterministic layout effect and not noise. A row whose layout floor exceeds
10% is marked UNMEASURED and left out of the footer. The footer gives, per
compiler and form, the geometric mean and the largest form/d over the
IMPROVE rows, and the worst KEEP-row loss against the shipped `a` beyond
`a`'s own floor (`max(launch, |aL/a-1|)`). The table ends with
`timed rows: N of M` and a `NOT TIMED:` list; a run that stops early still
renders (the EXIT trap). `table.py RAW cells.tsv "FORMS"` re-renders any raw
file; `deltas.py RAW "FORMS"` prints the same rows as ABSOLUTE deltas (ns per
call on short-search rows, us per pass on find-all rows), which is how D144
addendum 1 reads the ns-scale short-search rows.

The xcall.md §6 acceptance, applied to the chosen form: answers same on
every row; every improve row at or under 1 + floor on BOTH compilers; no
keep row losing more than its floor against `a`. If no form passes on both
compilers, that is the finding, and A2 waits for a better spelling.

`lpatom` is A1's own cell (logparse-atomic short search): its `a` is main's
artifact and its `d` the lane's, which A1 made byte-identical to the deny,
so `a` there reads A1's gain directly.
