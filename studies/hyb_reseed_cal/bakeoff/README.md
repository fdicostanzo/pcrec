# [OPT-HYB-RESEED-FORM] A2 — the form bake-off, run instructions

Picks A2's emitted form (docs/design/xcall.md §4 A2, manager ruling on §7
Q4) by timing hand-rewritten artifacts on the bench's two compilers, x86
gcc AND clang, BEFORE any emitter text is written. The Mac cannot pick it:
F2, semantically identical to F1, read x1.742 there.

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
median over the launches divided by the deny's, `floor` (the larger of
`d2/d` and `dL/d`: the same program re-launched, and re-linked in the other
order), and `ans` (every variant's answer hash equals the deny's). The
footer gives, per compiler and form, the geometric mean and the worst
form/d over the IMPROVE rows and the worst KEEP-row loss against the shipped
`a` beyond the floor.

The xcall.md §6 acceptance, applied to the chosen form: answers same on
every row; every improve row at or under 1 + floor on BOTH compilers; no
keep row losing more than its floor against `a`. If no form passes on both
compilers, that is the finding, and A2 waits for a better spelling.

`lpatom` is A1's own cell (logparse-atomic short search): its `a` is main's
artifact and its `d` the lane's, which A1 made byte-identical to the deny,
so `a` there reads A1's gain directly.
