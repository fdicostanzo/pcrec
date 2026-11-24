# Lane wsplitd3 — the window family split, DESIGN rev 2.1 (review r98 applied)

Lane wsplitd3 (opus), 2026-11-24. Branch lane/wsplitd3, cut from the kit branch lane/memfn-wsplit
@ 79388197d (code equal to the design's B a0742283a). Design only: nothing under `src/`, `cli/`,
`lib/`, `memfn/` (code) or `tests/` was edited. The assembler and every probe wrote only to
`$PCREC_TMPDIR/scratch/wsplitd3/`. The base gate runs used a `git archive` of 79388197d built there
with `nice make CC=gcc-16 -j4`, under the Mac suite lock (taken 17:05, released after the runs).

## Summary

`docs/design/memfn/window_split.md` is now rev 2.1. It answers every r98 FIX-NOW (R1-R13) and DOC
(R14-R26) item; the §R2.1 table there maps each id to its section. The cut, the header and the
accessors are unchanged except for R13's ruled move. What changed:

- **The gates (R1, R2, R11, R12).** §8.2-§8.4 are rewritten under r98's rule: a gate arm is listed
  for a box only if its base run is green there. On the Mac, G1 is `syncheck.sh` plus the three
  make targets as their own command; `make strict` is Linux-only. Mac G3 is
  `run_g2_win.sh --plants` and `run_proof.sh` (plain and `--plants`). The
  following are Linux-only, named plant by plant: run_g2_pres's 7 plants, g2_vspan, and the
  g2v/simdfloor mech rows, plus three arms found red on the Mac at the base (OC1-OC3 below). G5 is
  Linux-only because `make test` takes about 100 minutes on the Mac,
  so it has no Mac base run. G2's arm 3 gains a reach counter (`window_split/w32reach.py`) with
  floors from its base run. G4 pins both directions, +82 / -3, by name. Each G7 arm names the
  thing that reads it.
- **binders.py (R3, R15).** Its population is now B's eight edited files plus every file the unit
  creates (read from cut.spec). A row a peel re-keys therefore stays counted. Each population has a
  floor: 187/75/49/67/4. `CC` comes from the environment only. It also counts rows_check.py's
  PLANTS. Drilled (below).
- **R13.** `kit_run_set` and `kit_run_at` move to kit_pos.c at U3. They are presence.c :84-91 and
  :112-118 at B. `kit_wspan_at` stays in presence.c. kit_pos.c becomes 143 lines with PUBLIC 12.
  The 22 files total 4,763 lines and PUBLIC is 44.
- **The commit order (R4-R10).** Each unit's re-point list now comes from
  `window_split/repoint.py`, which reads binders.py's output: 202 rows in 19 units. Per-unit fixes:
  - U3 now lists its 10 rows.
  - U4 closes the head comment and re-points S3285.
  - U24 carries the S3252, `decide`, PROVENANCE and CLAUDE.md edits.
  - F1 moves to C0b.
  - Each new file gets its PROVENANCE row in the commit that creates it.
  - U1's purity anchor is stated per commit range.
  - The census's APPEND plants get a target found by content and asserted present.
- **The DOC items** are folded into the sections named in §R2.1.
- **R26.** ren_find's comment edit is in edits.spec.

The re-runs:

| run | result |
|---|---|
| assembler + `syncheck.sh $S/asm gcc-16` | `syncheck: 82 PASS, 0 FAIL (gcc-16)` |
| `--pure` control | `44 PASS, 38 FAIL` |
| B' tree control | `40 PASS, 0 FAIL` |
| binders over the tip (`--compile`, C0 runners) | all OK at 187/75/49/67/4 rows; compiles 186 + 75 + 4 PASS and 1 SKIP (header) |
| decider census at the tip, rev 2's pins | 95/2 (exactly the two pin checks); members 78, hits 62 |
| tables.py | tip 2, pure 13 |
| unused.py | 0 |
| kitgraph, empty spec | 24-file SCC without kit_kb.c; no CYCLE once the 16 others are dropped; a 15-file SCC with compose and gate dropped |

Gate base runs on the Mac, at a `git archive` of 79388197d with C0's runners overlaid. The
green arms:

- G1:
  - syncheck: 40/40.
  - `make CC=gcc-16 test-memfn-rows test-memfn-link`: `checks failed: 0`.
  - SABANCHOR: `all runner plants apply`.
  - The decider census: `checks failed: 0`.
  - The four `--plant-check` runs: 0 bad each.
  - unused.py: 0.
  - binders `--compile`: every population at its floor.
- G2: emit_sweep arms 1-3 all `emit_sweep: DONE rc=0`. w32reach reads byte 28 and utf8 20 at the
  base. Its drill (`--memfn=no-span-vector`) reads 0 and goes red.
- G3: `run_g2_win.sh --plants` gives 38/38 RED, `run_proof.sh` gives `checks failed: 0`, and
  `run_proof.sh --plants` gives 6/6 RED.
- G4: nm reads 178.
- G6: R-28 passes, with the largest frame 3504 B (`wf_parts_prepare`).
- G7: the three defines read 30/4/11.

Three arms are RED on the Mac at the base. The STOP RULE applies: none is bent, each moves to
Linux as an open choice with its evidence (note §8.4).

- **OC1** `test-memfn-finder`: 49 purity-reach FAILs, because BSD awk refuses a newline in a `-v`
  value.
- **OC2** `test-memfn-stamps`: `0 SIMD-on movers < floor 1`.
- **OC3** `test-memfn-g2` / `run_g2.sh --quick`: 29 FAIL lines, from x86 text and a loop-report
  floor.

## Findings answered

| r98 id | how answered | where |
|---|---|---|
| R1 | Mac G1 = `syncheck.sh` + `make CC=gcc-16 test-memfn-rows test-memfn-finder test-memfn-link`, each its own command; `make strict` Linux's (check_targets.sh exits 1 on aarch64); base runs recorded | note §8.2, §8.3, §8.4 |
| R2 | Mac G3 = `run_g2_win.sh --plants` (33), `run_proof.sh` + `--plants` (1), `run_g2.sh --quick`; Linux: plain run_g2_win (g2_vspan), run_g2_pres + `--plants` (7 named), g2_vspan, mech S3525/S3526/S3515/S3530/S3532-S3536 executed; non-existent run_g2.sh modes dropped | note §8.2, §8.3 |
| R3 | binders.py population = B's 8 + cut.spec's new files; floors; CC from env; drilled (b) red, (d) red, rev 2's file green on (b) | note §7, §7.8; `window_split/binders.py` |
| R4 | U24 = `git mv` + S3252, census `decide`, PROVENANCE row 54, CLAUDE.md entry | note §8.1 |
| R5 | `repoint.py` derives every unit's list; U3's 10 rows named | note §8.1; `window_split/repoint.py` |
| R6 | U4 adds ` */` after :7; re-points S3285 (B :1493) | note §8.1 |
| R7 | NEVER anchor: before `wf_arows[]` in window.c while the row is there, after `#include "window.h"` once peeled; include clause dropped | note §7.4 |
| R8 | the 4 APPEND plants' target = the file holding `ren_search[] = {`, asserted present and unique; rev 1's sentence restored | note §7.2 |
| R9 | F1 first in C0b | note §8.1, §13 |
| R10 | one PROVENANCE row per new file in its creating commit, artifact-text cell per file | note §7.6 |
| R11 | `w32reach.py` counter, floors from its base run, pinned on the gate's command line | note §8.2, §8.4; `window_split/w32reach.py` |
| R12 | G4 +82 / -3 by name; G7 = memfn.h's three defines diffed, test-memfn-stamps for FORMS/LIBC, G2 for pcrec's abi | note §8.2 |
| R13 | `kit_run_set` (:84-91), `kit_run_at` (:112-118) to kit_pos.c at U3; `kit_wspan_at` stays; counts re-run | note §3, §6.2; `cut.spec` |
| R14 | §10 admits §6.1's U2b re-spells | note §10 |
| R15 | rows_check S2983/S2988 all window_ren.c, U13; binders.py counts them (rows, floor 4) | note §7.6 |
| R16 | §3 :132-139 restated; run_modes B :223, mf_pres_ports B :283; finder :938-939 | note §3, §4.4, §6.1, §6.6 |
| R17 | strict regex: 48 (46 + 2 append-only); compose.c 32, presence.c 18; 0 binders in the moved compose/presence text; the tip's kit.h re-words are the build's | note §7.7 |
| R18 | the exception's reasons name by name (in/count/first non-family; shape/two/full by H3; TIE predicates structural, kit_pick.c includes kit.h only) | note §4.3 |
| R19 | 4 objects cross (2 arms, 2 contracts), Table E payload; tables.py's initializer blind spot | note §1, §4.4, §13.1 |
| R20 | A5: wf_span_render pure wrapper, wf_span_define merges the NULL test, the added statement is wf_tables_check's | note §5 |
| R21 | the SCC goes with the cut (pure move: no cycle); O1 + A5 remove crossings 13 -> 2 | note §R2 W1, §12 |
| R22 | ARV-7 leaf DONE at C0b, register-row half open (PLAN, main's); "ARV-7/H8" restored; stale :29-108 noted | note §1, §6.4, §13 |
| R23 | the empty spec spelled; kitgraph's split-static blind spot | note §6.4, §6.5, §13.1 |
| R24 | presence <-> compose named (kit_presence_check / kit_pres_run); Goal 4 "into the family" | note §1, §6.5 |
| R25 | S1427: `count` AND `in_set` | note §7.3, §7.5 |
| R26 | ren_find's comment names its two exceptions (edits.spec) | note §5; `window_split/edits.spec` |

## Gate base runs

The full table, with every command and its last line verbatim, is the note's §8.4. In short:

| arm | Mac base verdict |
|---|---|
| G1.1 `syncheck.sh $S/c gcc-16` | rc 0, `syncheck: 40 PASS, 0 FAIL (gcc-16)` |
| G1.2 `make CC=gcc-16 test-memfn-rows test-memfn-link` | rc 0, `checks failed: 0` |
| G1.2 with `test-memfn-finder` | rc 2, `make: *** [test-memfn-finder] Error 1` (49 purity-reach rows; OC1) -> Linux |
| G1.3 `python3 scripts/m6read_check_sab_anchors.py` | rc 0, `all runner plants apply` |
| G1.4 `python3 tests/memfn/decider_census.py --root .` | rc 0, `checks failed: 0` |
| G1.6 `--plant-check` win / pres / proof / wreply | rc 0 each; `38 plants, 38 edits, 0 bad` / `35 plants, 41 edits, 0 bad` / `6 plants, 6 edits, 0 bad` / `2 plants, 4 edits, 0 bad` |
| G1.7 `unused.py` | rc 0, no UNUSED |
| G1.8 `CC=gcc-16 binders.py . . --compile` | rc 0, `binders: rows 4 rows, 4 OK, 0 bad, floor 4` (all five at floor) |
| G2 arm 1 / 2 / 3 `emit_sweep.py --ref-bin .. --bin ..` | rc 0 each, `emit_sweep: DONE rc=0` (467 / 581 / 578 s) |
| G2 `w32reach.py build/pcrec . --floor=byte=28,utf8=20` | rc 0, `w32reach: byte 28, utf8 20`; drill `--extra=--memfn=no-span-vector` rc 1, `w32reach: utf8 0 BELOW FLOOR 20` |
| G3 `run_g2_win.sh --plants` | rc 0, 38/38 `RED` by detector (1,271 s) |
| G3 `run_proof.sh` / `--plants` | rc 0, `checks failed: 0` / 6/6 `RED` |
| G3 `make CC=gcc-16 test-memfn-g2` | rc 2, `make: *** [test-memfn-g2] Error 1` (OC3) -> Linux; bare `run_g2.sh --quick` rc 2, `libpcrec_mftrace.a missing` |
| G4 `nm -g build/libpcrec.a` pcrec_mf_ defined | `178` |
| G6 R-28 (in test-memfn-link) | PASS, largest frame 3504 `pcrec_mf_wf_parts_prepare` |
| G7 defines | `MF_SITE_ABI 30`, `MF_VOCAB 4`, `MF_CLASS_V 11` |
| G7 `make CC=gcc-16 test-memfn-stamps` | rc 2, `FAIL: FORMS movers: 0 SIMD-on movers < floor 1` (OC2) -> Linux |

Linux arms (`make strict`, test-memfn-finder, test-memfn-g2, run_g2_pres plain and `--plants`,
g2_vspan, the g2v/simdfloor mech rows, test-memfn-stamps, G5) are recorded in the note as
Linux-owed by the build lane at the tip. This lane did not run them (brief: OWED RUNS none).
Side observation: plantfix2's mutant-harness children (`run_proof.sh --plant-check`, under
`$PCREC_TMPDIR/scratch/plantfix2/mh/`) were still running at 17:10, after that lane released the
lock. They are not this lane's and were not touched.

## binders drill

The drill uses lane scratch `$S/drill`. It holds the assembled tip's `memfn/` plus copies of B''s
`tests/mech` and `tests/memfn`. ROOT and TREE are both `$S/drill`, and the runners are C0's. This
models a commit that comes after a peel has re-keyed its row. The row is mech S3535.

| case | the row | rev 2.1 binders.py | rev 2's binders.py |
|---|---|---|---|
| (a) control | SAB_FILE `memfn/src/window_vform.c`, AFTER intact | rc 0, `S3535 ... OK window_vform.c ... PASS`, `binders: mech 187 rows, 187 OK, 0 bad, floor 187` | - |
| (b) DRILL | re-keyed, AFTER `stamp = w64_undeclared;` (does not compile) | **rc 1**, `S3535 ... FAIL ...`, `binders: mech 187 rows, 186 OK, 1 bad, floor 187` | rc 0, `binders: mech 186 rows, 186 OK, 0 bad`: the row left the population (r98's defect, reproduced) |
| (d) floor | SAB_FILE `memfn/src/levels.c` (outside the population) | **rc 1**, `binders: mech POPULATION 186 BELOW FLOOR 187 (rows left the selection)` | - |

Command: `CC=gcc-16 python3 -I docs/design/memfn/window_split/binders.py $S/drill $S/drill $S/pc
--compile`. Case (d) runs the same command without `--compile`. Rev 2's binders.py is
`git show 6b60976ad~1:docs/design/memfn/window_split/binders.py`.

## STATE AT HANDOFF

STATE: delivered (design rev 2.1; no build go asked or used).

- Branch lane/wsplitd3; its tip is the last commit carrying this report.
- Rulings file `docs/dev/lanes/wsplitd3_rulings.md`: re-read before each commit and before this
  report. It was EMPTY throughout, so no entry was applied.
- Open choices for the kit manager (STOP RULE), each Linux's until ruled (note §8.4):
  - **OC1**: test-memfn-finder's purity reach under macOS awk. This lane leans toward U1 passing
    NEVER portably, a tests/ edit inside U1.
  - **OC2**: test-memfn-stamps' empty SIMD-on population on aarch64.
  - **OC3**: test-memfn-g2's x86 text and loop-report floor on the Mac.
- PLAN for main (recorded only, note §13): [ARV-7-TEXTBUF-LEAF], with the leaf done at C0b and the
  register-row half open; W8's [IR-FORM] pointer.
- Mac suite lock taken at 17:05 and released at 18:17.
- Scratch: `$PCREC_TMPDIR/scratch/wsplitd3/` holds:
  - `asm` (the tip), `pure`, `btree`;
  - `base` and `basec0` (the built base trees);
  - `drill`;
  - `binders_*.txt`, `repoint.txt`, `arm_*.log`, `g1base.out`, `g23base.out`.
- Owed: none from this lane. The Linux arms are the build lane's, at the tip.
- Next: the LIGHT re-check (note §8 at the base on the Mac, plus the §7.8 drill), then the owner's
  build go.
