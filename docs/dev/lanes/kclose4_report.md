# kclose4 report: the variant TAG-floor drops that turned R-13a's gate red

STATE: delivered (branch lane/memfn-kclose, re-pin commit 646a8c0be)
OWED: none

## Summary

Cause (i): the pins were stale on main too. Job 580-kit-kclose2-r13a already
ran BASE against tip over one corpus (`--ref dc1988069 --tree-rev HEAD`, 6,479
rows, both sides read the tree's corpus). It printed every dropping tag with
IDENTICAL a/b counts and 0 movers / 0 asymmetric in every stream, so main
dc1988069 reads the same counts as the tip. No branch hunk moves a tally and no
site refuses because of the branch. The byte cells of `VARIANT_PINS` in
scripts/emit_sweep.py were last pinned at 7924c9136 (2026-10-22, corpus about
5.8k rows) and nobody had re-pinned them since. I re-pinned the five byte cells
to the measured values with a dated comment that names the run and the cause.
The utf8 cells are untouched because the job runs `--bases byte` only.

Correction to the brief: the cells that dropped are lowsize and lowboth, not
"plain". The plain cell read every floor as held. The triage's "plain" label is
on lines 211-229 of sweep.log, which sit under the `VARIANT lowsize` header
(line 196). Likewise the brief's "lowdfa no-linked-call 96<122, yes-collapsed
31<46" is the lowboth cell. lowdfa's no-linked-call is 132, above its pin of 131.

## Tag drops BASE vs tip

Source: /var/tmp/pcrec-pcrec/scratch/memfn/kclose2/r13a/sweep.log, with side
a = BASE dc1988069 and side b = the lane/memfn-kclose tip. Every count is
identical on a and b.

| cell / stream | tag | pin | BASE (a) | tip (b) |
|---|---|---|---|---|
| lowsize emit-ir-auto, -fno-prefilter, -fno-prefilter-collapse | no-linked-call | 122 | 96 | 96 |
| lowsize emit-ir-auto | yes-collapsed | 35 | 22 | 22 |
| lowsize emit-ir-auto[-fprefilter] | yes-collapsed | 32 | 20 | 20 |
| lowdfa emit-ir-auto | yes-collapsed | 28 | 27 | 27 |
| lowdfa -fno-prefilter | no-dfa-overflow | 14 | 13 | 13 |
| lowdfa -fno-prefilter-collapse | no-dfa-overflow | 37 | 36 | 36 |
| lowdfa stderr | stderr-default | 37 | 36 | 36 |
| lowboth emit-ir-auto, -fno-prefilter, -fno-prefilter-collapse | no-linked-call | 122 | 96 | 96 |
| lowboth emit-ir-auto | yes-collapsed | 46 | 31 | 31 |
| lowboth -fno-prefilter | no-dfa-overflow | 9 | 8 | 8 |
| lowboth -fno-prefilter-collapse | no-dfa-overflow | 32 | 31 | 31 |

The companion counts that rose: lowsize no-size-cap went from 83 to 214, and
lowboth's went from 81 to 199. In the cells that keep the shipped size cap
(plain, lowdfa, lowthr), no-linked-call ROSE from 131 to 132. Reach rose by
about 470 to 560 in every cell (corpus growth).

I queued no new job. The brief asked for "one queued BASE-vs-tip job over the
same corpus, dropping tags only". The failed 580 record is exactly that
comparison (same corpus, BASE built from `git archive`, all cells), so a
second run would only repeat it (about 11 minutes of box time).

## Cause

(i) The pins were stale on main. Neither (ii) nor (iii) applies.

- Not (ii): the branch's emit_sweep.py diff against dc1988069 touches only
  TRACE_VARIANT_RECORDS_FLOOR (kclose3). Its other hunks are compose.c
  SEAM-2, g2_gen, check_targets, axes wording and libc_census. None of them
  changes an emit-ir-auto or stderr tally: a = b in every cell, with 0 movers.
- Not (iii): the population is the tree's corpus on both sides. The branch
  adds no .rxt file (`git diff dc1988069..HEAD --stat` shows none), and the
  arm set is unchanged.
- Mechanism of the large drops: they occur only in the LOWERED size-cap cells
  (lowsize and lowboth: 30000 B VM code, 60000 B emit). Linked-call and
  collapsed patterns now emit more than the lowered cap allows, so they are
  refused with the size-cap error and tagged `no-size-cap`, where they used to
  be tagged `no-linked-call` or `yes-collapsed`. Probe: `(a|b(?1)c)+d` is
  refused at 31331 B by both the src_ref-lowsize (BASE) and src_tree-lowsize
  (tip) binaries, and the lowdfa binary (shipped size cap) tags it
  `no-linked-call`. This is the same shape as the R4e'.0b and M0 re-pins
  already recorded above VARIANT_PINS. It is an intended refusal under a test
  variant's lowered limit, not a refusal of a real site. I did not attribute
  it to a single main commit between 7924c9136 and dc1988069 (no bisect run).
- The falls of one in lowdfa and lowboth (no-dfa-overflow, yes-collapsed and
  stderr-default, all -1) mean one pattern no longer crosses the
  3000-element DFA cap. They are identical on a and b, so they are main-side.
  I did not bisect them.

## Re-pin or fix

The fix is a re-pin, with no code change. Commit 646a8c0be pastes the
`--emit-pins` byte cells from /var/tmp/pcrec-pcrec/scratch/memfn/kclose2/r13a/pins.py
(reach, tags and manifests) into scripts/emit_sweep.py `VARIANT_PINS` through
pprint at width 120. The old block's pprint round-trip was checked identical
first. A dated RE-PINNED comment (2026-11-12, lane kclose4) names job 580, the
identical a/b sides, the lowered-cap mechanism and the probe. The utf8 cells
are byte-identical to before (checked by loading both dicts).

Manifest moves from the run: no-linked-call is now a thin tag in
lowsize/lowboth (`(?R)a`), and no-size-cap is no longer thin. no-callout
(`a(?C)b`) and stderr-vm (`(a{3,5}){3,6}`) are new tags.

I did not re-point the 580 job. It reads the TREE's emit_sweep.py, and its
`--dry-run` passes (rc=0). I did not queue it; the kit manager does that.

Note for the manager: the utf8 VARIANT_PINS were pinned at the same time and
are probably stale in the same way. 580 runs `--bases byte`, so they do not
gate it. Any later `--variant all` run without `--bases byte` will likely
read utf8 TAG FLOOR lines too.

## Checks

- Measured-vs-pinned: /var/tmp/pcrec-pcrec/scratch/memfn/kclose4/cmp.py, run
  on the committed scripts/emit_sweep.py against r13a/pins.py, reports no
  byte-cell difference. Every byte floor now equals the measured smaller side,
  so 580's sweep would read no TAG FLOOR line.
- `make strict` in worktrees/kclose: rc=0 ("whole tree compiles clean with
  -Werror -Wshadow"). Log: /var/tmp/pcrec-pcrec/scratch/memfn/kclose4/strict.log.
- scripts/tests/emit_sweep.py.test (the file run, against worktrees/kclose
  build/pcrec, rebuilt at the tip): rc=0, checks passed 28, failed 0. Log:
  /var/tmp/pcrec-pcrec/scratch/memfn/kclose4/selftest.log.
- 580-kit-kclose2-r13a `--dry-run`: rc=0.

## Charter-vs-committed checklist

- Explain the drops, classified (i)/(ii)/(iii): done. The cause is (i), and
  the BASE tallies are shown above.
- If a refusal of a real site was found, STOP: not applicable. The refusals
  are the lowered-cap variant's own, identical on BASE.
- Re-pin with a comment naming the run and the cause: done (646a8c0be).
- Re-point 580 if needed: not needed, and its dry-run passes.
- Do not queue 580: not queued.
- `make strict`: rc=0.
- emit_sweep self-test: rc=0 (28 passed / 0 failed).
- One queued BASE-vs-tip job: not queued, because the existing job 580 record
  is that comparison (reason above).

## STATE AT HANDOFF

Re-pin committed (646a8c0be); make strict rc=0; self-test rc=0 (28/0); 580 dry-run rc=0, not queued. Nothing owed by this lane.
