# mfindfix2 — the FIX-NOW items of code round r2-memfn-mfind

Lane mfindfix2 (opus), 2026-11-15, branch `lane/memfn-mfind`, worktree
`worktrees/mfind`. Review: `docs/dev/reviews/2026-11-15-r2-memfn-mfind.md`
(RULED section, kit manager 03:30, plus R1). Scratch evidence:
`$PCREC_TMPDIR/scratch/memfn/mfindfix2/` (below `$S`).

## Summary

Main merged in (one history-index conflict, kept both sides). Every FIX-NOW
item of the RULED list is fixed: F1, F3, F4, F6, F8, F9, F10, F12, F13, F14
(both floors), plus the DOC item F11 and the R1 (F5) labels. Not this
lane's: F2, F7 and F14's fence control (PLAN), F15 (NOTED), F5 (RULED by
Frank via R1: the fused row is a measuring instrument only; this lane only
labelled the declarations). No default moves: 0 movers over 2,830
(pattern, engine) default-flag compiles against the merged main tip, and
`make test-codegen` is green. Validation run by the lane: G2 mfind quick
202/0 with every plant in its class, simd_guarded 19/0, rows 264/0, G7
lever fence, sabotage anchors, cloud axes shard population, `make strict`.
Axes: owed to the combined gate's cloud axes run, not run by the lane (the
kit manager stopped the lane's local run as an out-of-queue heavy run).

## Main merge

- Merge commit 51af1f6ac: main at **04fe41c924869a4773aaebe4cd93dd5ce68e5acc**
  into `lane/memfn-mfind`. One conflict,
  `docs/dev/history/claude_md/docs__dev__lanes.md` (the history index):
  kept both sides (the mfind report line and main's covcap/covcap2 lines).
  `tests/axes/run_axes.sh` auto-merged.
- After the merge: `make -j8` rc 0, `make strict` rc 0. Premise test:
  `run_g2_mfind.py --quick` 168 passed / 0 failed, plants S3150-S3159 in
  their declared classes (`$S/premise.log`).

## Fixes by id

**F1** (MFIND_W16/W32_GUARDED_MAX was not a bound). RED: with the lever,
two long-chain patterns rendered helpers far past the declared maxima
(1400/1500): `a.*\x7f[acegikmoqsuwy]{12}` x86-64 guarded 4,089 (v3 7,831);
`b` + `[0-35-7]`x28 x86-64 2,335 (v3 4,323) (`$S/red/F1_pre.txt`).
FIX: the maxima are now a cap BY CONSTRUCTION, not a relabel: a new
`ofs_fn_fits(x, d)` (memfn/src/ofsskip.c, declared in kit.h) renders the
helper's head + body + call into a counting sink (4 bytes per cstr byte,
the octal-escape worst case `pcrec_sb_cstr` writes) and the mfind row's
`applies` holds only when the text fits `d->guarded_max`; a site over the
cap is declined and keeps the scalar row. `mf_formdecl.applies` takes
`(x, d)`; `fn_in` carries `art`/`h` for the fit render; `vrun_applies`
adapted (pure signature change). The values stay 1400/1500, labelled CHOSEN
caps in vrun.c, and are PINNED: `tests/memfn/simd_guarded_check.py` reads
each `const mf_formdecl` in vrun.c, resolves its `X_GUARDED_MAX` define and
requires it equal to its `simd_bounds.tsv` row (both directions, floor 4
declarations), and its LEVER_NAMED list gains the two long-chain witnesses
(`mfind-long-tbl`, `mfind-long-run`) with a new `lever-capped` population
floor 4. GREEN: both long patterns now `MEMFN_FORMS "none"` (guarded =
the target text only, 469 / 615) while `foo.*bar` keeps `mfind@w16` /
`mfind@w32+w16` (`$S/F1_post.txt`); simd_guarded "kit guarded_max pinned"
x4, "lever-capped: 4 (floor 4)", 19/0 (`$S/guarded.log`). Files:
memfn/src/{ofsskip.c,kit.h,vrun.c}, memfn/data/simd_bounds.tsv (comment),
tests/memfn/simd_guarded_check.py.

**F2** — not this lane's (PLAN: one verify chain).

**F3** (RX_RUN_WORDS counted the helpers' compares). RED: `foo.*bar` under
the lever, RUN_WORDS 2 at SIMD-off, 3 at x86-64, 4 at v3
(`$S/red/F3_pre.txt`). FIX: `mfind_text` saves `art->words` around the
helper path's `ofs_verify_chain` and restores it (vrun.c). GREEN: 2/2/2
(`$S/F3_post.txt`). Files: memfn/src/vrun.c.

**F4** (doc: the frame reply under the lever). RED: memfn.h `mf_lever` doc
claimed the helpers apply everywhere and said nothing of the reply. FIX
(doc): helpers apply "where the helper fits its guarded bound"; the lever
replaces "the libc memchr search (and its restart stream)"; the `mf_wreply`
frame part is NOT updated under the lever (search NONE, stream RESTART
while the text is a MASK stream) and pcrec reads neither field; the
instrument-only line (R1). GREEN: text read back; `make strict` clean.
Files: memfn/include/memfn.h.

**F5** — RULED by Frank (R1): instrument only. Not a fix item; this lane
added the RULED line to the review and the "measuring instrument only (F5,
Frank 2026-11-15): never picked; see review r2-memfn-mfind" label at
ofsskip.c's fn_rows (both comments), kit.h's FF_MFIND comment, rows.tsv and
simd_bounds.tsv comments and the memfn.h `mf_lever` doc. Comments only.

**F6 / F8** (wording: the ver-6 card is the bundle comparison; "the libc
stream" misused D190's word). RED: the cited comments. FIX: formhash.c
(fn-memchr entry), kit-grid.tsv ver-6 comment, memfn/data/cards/CLAUDE.md,
tests/memfn/finder_check.py, vrun.c module comment now say bundle comparison
and "the libc memchr search (and its restart stream)". GREEN: grep of the
old phrases empty in those files. Files as listed.

**F7** — not this lane's (PLAN).

**F9** (S3150/S3151 fault by a runaway loop, not the one-byte bound). RED:
with the driver's guard page disabled (`$S/red/F9_noguard.log`) S3150/S3151
still FAULT (runaway), so they never witnessed the bound. FIX: two
termination-preserving one-byte plants, S3173 `top-one-byte`
(`const size_t e = n...;` -> `+ 1`, w16/w32/body) and S3174
`top-one-byte-dpos` (the `n - D` spelling, per-helper), both declared
FAULT; `plant_text` takes a negative per; the PLANTS comment names
S3150/S3151 runaway witnesses. The same no-guard run shows S3173/S3174 go
LOUD ("got 21 want 22") without the guard page, i.e. they fault on the one
byte, not by runaway. GREEN: S3173 FAULT, S3174 FAULT in
`$S/g2_postF12b.log`. Files: memfn/tests/run_g2_mfind.py.

**F10** (G2 never planted the scanned byte past the last candidate). RED:
the old driver's chance population `beyond=4463`
(`$S/red/F10_noplant.log`); the new floor turns the old driver red
(`$S/red/F9F10_olddriver.log`). FIX: `subject()` in g2_mfind_driver.c
plants the scanned byte at b in [max(e, pos+k), n) half the time (half of
those at the lowest such b) with the fitting terms written to pass, census
counter `beyond`; runner floor `BEYOND_FLOOR_80 = 2040000` (2,553,909
measured). GREEN: `beyond=2553909` on every build, 202/0. Files:
memfn/tests/g2/g2_mfind_driver.c, memfn/tests/run_g2_mfind.py.

**F11** (DOC: S3153 is a specificity control). FIX: vrun.c "no scanned
byte compared twice" is stated as a COST claim no check counts (r2 F11);
the final-block "must not be handed over twice" softened likewise; the
PLANTS comment says S3153 is a specificity control + text pin. Files:
memfn/src/vrun.c, memfn/tests/run_g2_mfind.py.

**F12** (G2 held the site shape constant). RED: every G2 mfind site was a
plain FIND/FUNC/RETURN site; no axes arm crossed `--harness=mfind` with the
SIMD layer. FIX: (a) g2_mfind_gen.c THE SITE SHAPES, chosen by id AFTER the
draw (no RNG draw of their own, so the drawn space and every driver
population stay the plain family's): a PRE-CHECK FUNC PART (odd random ids
whose draw scanned a RUN: the predicate as the one FUNC part of an
ALL_PRESENT/STMT/ON_MISS composite, `fn_ref` naming the part function,
pcrec's `rx_reqrun` shape; the driver calls the part), a policy INLOOP
site (id % 8 == 5: the structural check wants NO helpers) and a policy SIZE
site (id % 8 == 6: helpers render); meta column `shape`; runner population
floors `pre` 4 (6 measured), `inloop` 12 (15), `size` 12 (15). A first cut
that forced a RUN draw for pre sites moved the space (four space floors
and stream2 red, `$S/g2_postF12.log`); the after-draw choice restored it.
(b) tests/axes/run_axes.sh: `memfn_top_target()` and a job
`--harness=mfind -fmemfn-simd=<top target>` (x86-64-v3 here), selected by
an empty AXES or `--harness=mfind`. GREEN: G2 quick 202/0 with
`inloop=15 pre=6 size=15` and populations equal to the pre-F12 run
(`$S/g2_postF12b.log`); `AXES_PLAN=1` lists the new job; cloud
`cloud_axes_check.sh tests/ci/cloud_axes_shards.tsv`: "20 shards ... run
the unsplit sweep's 118 jobs and 28 passes exactly once" (the existing
`--harness=mfind` unit word selects both jobs). The arm's RUN is owed to
the combined gate (see Validation). Files:
memfn/tests/g2/g2_mfind_gen.c, memfn/tests/run_g2_mfind.py,
tests/axes/run_axes.sh, memfn/tests/CLAUDE.md.

**F13** (S3158 declared LOUD but often FAULTs). FIX: `ACCEPT =
{'FAULT':{FAULT}, 'LOUD':{LOUD,FAULT}, 'SAME':{SAME}}` in the per-run check
and the summary; PLANTS comment records S3158's 354 FAULT / 22 MOVE.
GREEN: all plants in class. Files: memfn/tests/run_g2_mfind.py.

**F14** (two K35 literals not raised). RED/COUNT: `run_rows.sh` with
ROWS_FLOOR=999 printed "the kit's trace lists 36 rows"; G2's section 4b
printed "(c) 36 distinct (table,row) pairs >= floor 20" in lane mfindg2's
full and gathered runs on this branch. FIX: tests/memfn/run_rows.sh
ROWS_FLOOR 33 -> 36 and memfn/tests/run_g2.sh FLOOR_ROWS 20 -> 36 (the
review guessed 23 before counting; the count is 36, every kit row), each
with a dated comment; memfn/tests/CLAUDE.md says 36. GREEN: run_rows.sh
264/0 (`$S/rows.log`). FLOOR_ROWS=36 is not yet exercised by a G2 rows run
on this tip (owed to the combined gate's test-memfn-g2). The fence
allowlist control is PLAN, not this lane's.

**F15** — not this lane's (NOTED: the ver-6 card's sparse cell).

## Default-flip proof

Argument: (1) the F1 fit test is reached only from `mfind_applies`, whose
row (OVER = fn-mfind) holds only under the `mfind` lever; at default the
row is never walked. (2) `vrun_applies`' change is the new signature only.
(3) `fn_in`'s two extra fields are read only by the fit test. (4) F3's
save/restore runs only on the helper path (lever). (5) Everything else is
comments, test code, plants, floors and an axes job.
Evidence: `make test-codegen` rc 0 (21/21 scripts, `$S/codegen.log`, no
`*** [test-` lines). Emit diff: main's tip 04fe41c92 built from `git
archive` in `$S/mainsrc`, every 5th corpus pattern (1,415 of 7,071) at
default flags and at `--engine=vm`, `--features all`, compared byte for
byte against this branch's `build/pcrec`: **corpus 7071 sampled 1415 pairs
2830 movers 0** (`$S/emitdiff.log`, script `$S/tools/emitdiff.py`).
Control: `foo.*bar` default text hash equal on both binaries, while the
lever compile (pcrec-harness) differs, so the diff can see a mover.

## Validation

- `make -j8` up to date, `make strict` rc 0 ("whole tree compiles clean").
- `make test-codegen` rc 0.
- `memfn/tests/run_g2_mfind.py --quick`: 202 passed / 0 failed; plants
  S3150-S3159, S3173, S3174 each in its class (S3153 SAME expected).
- `tests/memfn/run_simd_guarded.sh`: 19 passed / 0 failed (pins, lever-capped).
- `tests/memfn/run_rows.sh`: 264 / 0.
- `tests/compound/run_lever_fence.sh`: PASS (3 checks, 4 controls).
- `scripts/m6read_check_sab_anchors.py`: 1300 sabotages, all anchors resolve.
- `tests/ci/cloud_axes_check.sh`: PASS (118 jobs, 28 passes, 20 shards).
- Axes: owed to the combined gate's cloud axes run, not run by the lane.
- Not run (brief): full `make test`, mech, ident gate, G2 full / run_g2.sh.

## STATE AT HANDOFF

- Tip: the commit carrying this report, on top of 1040b12ae
  (`lane/memfn-mfind`).
- Merged main: 04fe41c924869a4773aaebe4cd93dd5ce68e5acc (merge 51af1f6ac).
- Rulings: last entry applied **R1** (F5 instrument only: review RULED line
  + declaration labels).
- Not fixed and why: F2, F7, F14's fence control (PLAN), F15 (NOTED), F5
  (ruled; labels only) — none is this lane's FIX-NOW list.
- Combined-gate stage list (incl. new floors): `make strict`; `make test`
  (incl. test-memfn-g2 quick: run_g2.sh FLOOR_ROWS 36 and section 4z
  run_g2_mfind with `pre`/`inloop`/`size`/`beyond` floors and plants
  S3173/S3174); `make test-memfn-g2-full`; test-memfn-guarded
  (pins + `lever-capped` 4); test-memfn-rows (ROWS_FLOOR 36); cloud axes
  incl. the new `--harness=mfind -fmemfn-simd=x86-64-v3` job; ident gate;
  mech REACH.
- OWED: none

## docs/dev/reviews/2026-11-15-r2-memfn-mfind.md

The review's finding ids (its "Findings and PROPOSED dispositions"): F1,
F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15. (This section
and the next exist because the DELIVER file's `cites` line names the two
files as sections; the check's intent, every review id answered in this
report, is what they carry.)

## docs/dev/lanes/mfindfix2_report.md

Per id, where "Fixes by id" answers it: F1 fixed; F2 not this lane's
(PLAN); F3 fixed; F4 fixed (doc); F5 ruled by R1, labels only; F6 fixed
(wording); F7 not this lane's (PLAN); F8 fixed (wording); F9 fixed; F10
fixed; F11 fixed (doc); F12 fixed (G2 shapes + axes job; the job's run owed
to the combined gate); F13 fixed; F14 both floors fixed (fence control
PLAN, not this lane's); F15 not this lane's (NOTED).
