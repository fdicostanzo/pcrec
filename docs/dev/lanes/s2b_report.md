# s2b: span_pick stage 2, unit S2b, the step-0 census (lane report)

Lane `s2b`, 2026-11-06. Branch `lane/memfn-s2b`, cut from the design branch `lane/memfn-s2rev11` at e52cd716a.
**BASE (main merged in): 3094c45c0.** Kit request R-35. Design of record: `docs/design/memfn/span_cards.md`
rev 1.1 §7, §9's S2b row, §10.2, §2.5. Nothing emitted moves (no `src/`, `memfn/src/` or abi change).

## Summary

- `docs/design/memfn/span_pick/census0.py` is the ONE kit-side pricer of span_pick's formula. It REPLACES
  `smp20.py` (`git rm`); modes `control` (smp20's site, the golden) and `sweep` (every window site of R-33's
  sweep, outputs (1) movers by class and (2) the card population).
- Readers re-pointed: `span_pick.md` (the two cites, no line cite left), `span_pick/CLAUDE.md`,
  `span_pick/witness.sh`. `git grep smp20.py` now finds only the CLAUDE.md sentence saying census0 replaced it,
  and span_cards.md's design text.
- `census0_control.sh BUNDLEDIR` is the control as a runnable check.

## Control

`census0.py control` on smp20's site reproduces the rev 5 `smp20.out` BYTE FOR BYTE, including every
`incumbent @` line (diff: empty before the appended line), plus ONE appended P-blind grid line. `smp20.out` is
now that output (golden = old bytes + that line; the old bytes are untouched, `git diff` shows one added line):

    == blind P: argmin over the grid (h1 5..40, hit(PAIR) 1-8 x h1, k 1.00-12.00 by 0.05), 3536 points: @0 {X,x} at 155 points; @1 {/} at 3381 points

Cross-check against span_pick.md ("3,536 points ... P's argmin is '/' at 3,381"): **3,381 of 3,536, MATCH**
(no finding). Also run end to end at this base: `witness.sh` on the base-built `build/pcrec` produced a
`witness.out` identical to the committed one, and `census0_control.sh` on its fresh bundle listings was GREEN.

## Sabotage

Row (i), id **S2920** (kit allocation S2920-S2929; only S2920 used): incumbent read from the wrong field. In
`incumbents()` the `memchr on:` stop list was cut to its first stop (`...split()[:1]`). Planted, the control
went RED (the `incumbent` lines of `{X,x}` arms read "not one modelled stop"; `prose DEF` gained a phantom
pick; rc 1); reverted, GREEN again. Why it can see the field: the golden holds the `incumbent @` lines, which
are computed only from that field (the band-0 argmin does not read it). Planted by hand (the sabotage is one
sed on a scratch-diffed copy); it is not in the mech matrix.

## Sweep mode (what the numbers are, and are not)

Run by hand on R-33's existing 2026-11-02 sweep (5,492 records, pre-base) only to test the tool; the
committed `census0.out` is **PROVISIONAL** (its header says so) and J0 overwrites it at the base. Shape of the
provisional result (RTE arm): 3,430 window units; 3,372 incumbents priced; unpriced: hors 14, memchr-back 39,
unobserved 5; **row-1-class units 207** (a NONE alternative whose core position 0 is a two-member set), 206
priced, **166 move at >= 1 corner**, set-to-byte movers (k2/pair -> k1/memchr, NONE alt) 4 among them. DEF
arm: 51 units, 12 row-1-class, all 12 move. The population is non-zero, so the trigger is met (as §7 says it
already was by smp20). Stand-ins are smp20's plus the walk (byte 1.16 = C_BITMAP, hit = h1); corners k {1,12}
x h1 {5,40} x hit(PAIR) {1x,8x h1}; every method admitted by member count (T-FIND's real admission is the
kit's). Movers are stand-in-driven (no noise, no band), so they LOCALIZE and are never the acceptance (SRS §8
item 2). Open for S2c: output (2)'s `cls` vocabulary is census0's reading (rc-* run length short <= 8 / long;
settest set1/set2/setN), not a measured one; S2c fixes the real boundaries when it lists the cells.

## J0 (prepared, NOT queued)

`/var/tmp/pcrec-pcrec/scratch/memfn/s2b/jobs/240-kit-s2b-j0` (key `kit-s2b-j0`, TREE worktrees/s2b; `--dry-run`
green: 5,492 compiles; cap 1800, est 120, patience none; `expect compiles=5492 last=^== r33 collect COMPLETE: `).
Stages in one script (about 1 minute plus the 5,492 compiles at --jobs 8): the traced probe build (`r33_sim/
build.sh`) and `collect.py` to `scratch/.../s2b/j0/sweep.jsonl`; `witness.sh` into `j0/ws`; `census0_control.sh`
(a RED prints `== J0 FAILED` and exits 1); `census0.py sweep` writing
`docs/design/memfn/span_pick/census0.out` IN THE s2b WORKTREE (uncommitted). Read it: the job log's last line
`== census0 J0 COMPLETE: N lines`, then `git -C worktrees/s2b diff --stat`; commit `census0.out` (named path)
on lane/memfn-s2b. A `== J0 NOTE: witness.out ... differs` line means the base moved today's picks: a finding.
The tree needs `build/pcrec` and `build/pcrec-analyze` (built here).

## STATE AT HANDOFF

OWED: J0 (`kit-s2b-j0`) is prepared and not queued; the manager queues it, then commits `census0.out`.
`docs/dev/lanes/s2b_deliver.txt` did NOT exist in the worktree or the main tree when I started (the brief says
it is written by the manager), so lanecheck had no DELIVER block to check; I did not create it.

## Charter vs committed

- §7 census0.py replaces smp20.py, smp20.py deleted: DONE. One kit-side pricer: DONE.
- Readers re-pointed (span_pick.md two cites, span_pick/CLAUDE.md, witness.sh): DONE.
- Per site, candidates (alt x core position x methods) priced under P at smp20's grid corners (k 1/12, h1 5/40,
  hit(PAIR) 1x/8x h1): DONE; BAND-0 argmin vs the incumbent read from the trace (`wr`, `fdroute`/`ends`): DONE.
- Output (1) movers by class (row-1 class vs others, any corner and all corners): DONE (provisional data).
- Output (2) card population to `census0.out` (methods, verify (form, cls), consumer kind x entry): DONE in
  form; real data owed to J0. SKIP/Horspool counts out (R14c): honoured (counted unpriced).
- Control byte for byte incl. `incumbent @` lines + one appended P-blind line: DONE, GREEN.
- P-blind count cross-checked against 3,381 of 3,536: DONE, match.
- Sabotage (i) S2920: DONE (red observed, reverted).
- §9 witness "counts non-zero": DONE on the provisional data (207 row-1-class units); re-read at J0.
- J0 as a boxqueue job file, not queued: DONE, dry-run green. census0.out from J0: OWED.
- Merge of main first, BASE recorded in the first commit message: DONE (3094c45c0).
- CLAUDE.md updated (span_pick/): DONE.
