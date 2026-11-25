# Review r99 memfn-winsplit3 (design, LIGHT re-check): window_split.md rev 2.1, §8 gates only


## RULING (kit manager, 2026-11-24)

- Verdict accepted: READY after the listed fixes. They are text only, and the kit manager checks them against the diff; no further round is needed.
- CLOSURE-1, FIX-NOW: the Linux-listed arms' BASE run becomes the build lane's FIRST step (step 0, before C0b): one dev-box queue job by main, whose green is the build's precondition. §8 must stop relying on pres --plants executing S3012: lane s3012fix moves S3012 to run_g2_win.sh (PR #1), so §8 takes PR #1's final populations.
- OC1 (ruled): the macOS awk `-v` newline is a kit test-portability defect. It is NOT fixed inside U1, because the split stays a pure move. It gets its own pre-split commit C0a, with a grep of sibling sites (D203). Once C0a lands, the finder arm is a Mac arm too.
- OC2 and OC3 (ruled): Linux arms, with the reasons recorded (stamps MOVERS_FLOOR=1 against 0 on the Mac; x86 text on arm64).
- DOC items: as proposed (G5's mech half, G3's id ranges, the kit_pos.c title in files.spec).
- Process: the coordinator's one stray temp file in /tmp (an unset TMPDIR) is recorded.

DRAFT by the coordinator, 2026-11-24, for the kit manager to rule. Dispositions are PROPOSED.

## Subject

- DESIGN rev 2.1: `docs/design/memfn/window_split.md` + `docs/design/memfn/window_split/` at `8a5b8f0f4`
  (rev-parsed: lane/memfn-wsplit tip `03e7cc0dc` = `8a5b8f0f4` + 6 memfn journal lines; no subject drift).
- Base for the gate re-runs: a `git archive` of `8a5b8f0f4` (code equal to B' `79388197d`: empty diff over
  memfn/src, memfn/include, tests, memfn/tests, Makefile, scripts, src, lib, cli) with C0's 12 runner files
  from `838deefe2` overlaid, built `nice make CC=gcc-16 -j4` (rc 0) under the Mac suite lock. No review
  worktree was needed (the archive is the base); none was created.
- Tip: `assemble.py . asm` at the base (49 files in memfn/src; the critic re-assembled byte-identically).
- Scope (kit manager's r98 ruling): §8 and its gates, R3's binders drill, R1-R26 closure by id. Not
  re-argued: R13, O1-O7, the two-file reading. OC1-OC3: facts only.
- Rulings: main `e11c5f4ef` = the subject's merge-base, unchanged at hand-back. FREEZE DRIFT: none.

## Verdict

**READY for the build go after ONE listed text fix (CLOSURE-1) plus four DOC items.** Every r98 item
R1-R26 is CLOSED by id (26/26; R13 with a stale title, CLOSURE-4). Every Mac gate arm §8.3 lists re-runs
GREEN at the base on this Mac with the last line §8.4 records; every arm §8.4 shows red re-runs red with the
stated cause, and each is named Linux's with a reason. syncheck at the tip: `82 PASS, 0 FAIL (gcc-16)`.
The binders drill reproduces: a re-keyed broken AFTER goes red (rc 1), a row leaving the selection goes
red (rc 1, on two populations), and rev 2's binders.py on the same tree stays green (rc 0, 186 rows).
What is open: the Linux-listed arms have NO base run and no stated point at which one is taken, while
r98's rule ("on the box it is listed for") has no Mac qualifier, and the one arm that executes S3012
(under triage as not detected on x86) is among them.

## Gate arms re-run at the base on the Mac (coordinator; last line verbatim; logs .coord/arms/)

| arm | rc | last line | = §8.4 |
|---|---|---|---|
| G1.1 syncheck (base memfn copy) | 0 | `syncheck: 40 PASS, 0 FAIL (gcc-16)` | yes |
| G1.1 syncheck (assembled TIP) | 0 | `syncheck: 82 PASS, 0 FAIL (gcc-16)` | = r98 |
| G1.2 `make CC=gcc-16 test-memfn-rows test-memfn-link` | 0 | `checks failed: 0` | yes |
| G1.3 SABANCHOR | 0 | `all runner plants apply` | yes |
| G1.4 decider census | 0 | `checks failed: 0` | yes |
| G1.6 plant-check win / pres / proof / wreply | 0 x4 | `38 plants, 38 edits, 0 bad` / `35 plants, 41 edits, 0 bad` / `6 plants, 6 edits, 0 bad` / `2 plants, 4 edits, 0 bad` | yes |
| G1.7 unused.py | 0 | (no UNUSED line) | yes |
| G1.8 binders `--compile` | 0 | `binders: rows 4 rows, 4 OK, 0 bad, floor 4` (mech 187, g2 75, purity 49, census 67, all at floor) | yes |
| G2 arm 1 | 0 | `emit_sweep: DONE rc=0` (851 s) | yes |
| G2 arm 2 (`-fmemfn-simd=x86-64`) | 0 | `emit_sweep: DONE rc=0` (1,206 s) | yes |
| G2 arm 3 (`x86-64-v3 --no-differ-floor`) | 0 | `emit_sweep: DONE rc=0` (1,092 s; differ 90/90 c-default, 35/35 c-vm; the WAIVED line) | yes |
| G2 w32reach | 0 | `w32reach: byte 28, utf8 20` | yes |
| G2 w32reach drill (`--extra=--memfn=no-span-vector`) | 1 | `w32reach: utf8 0 BELOW FLOOR 20` | yes |
| G3 `run_g2_win.sh --plants` | 0 | `PLANT S3118 RED ...` (1,281 s; 38 of 38 PLANT lines RED) | yes |
| G3 `run_proof.sh` | 0 | `checks failed: 0` | yes |
| G3 `run_proof.sh --plants` | 0 | `PLANT S3242 RED ...` (121 s; 6 of 6 RED, S1419 among them) | yes |
| G4 nm | 0 | `178` | yes |
| G6 (R-28 in G1.2's test-memfn-link) | 0 | `465 kit functions measured, floor 100; largest frame: 3504 pcrec_mf_wf_parts_prepare` | yes |
| G7 defines | 0 | `MF_SITE_ABI 30`, `MF_VOCAB 4`, `MF_CLASS_V 11` | yes |
| (Linux claim) `make CC=gcc-16 test-memfn-finder` | 2 | `make: *** [test-memfn-finder] Error 1`; `checks passed: 28889`, `checks failed: 49`, all 49 "does not occur exactly once" | yes (OC1) |
| (Linux claim) `make CC=gcc-16 test-memfn-stamps` | 2 | `make: *** [test-memfn-stamps] Error 1`; `FAIL: FORMS movers: 0 SIMD-on movers < floor 1` | yes (OC2) |

Not re-run: `make CC=gcc-16 test-memfn-g2` (849 s red in §8.4; OC3's facts were checked statically by the
critic: run_g2.sh :290's bare exit 2, its window section runs plain run_g2_win.sh with v_section, its
presence section runs run_g2_pres.sh whose `host_has` accepts x86-64 on arm64), and `make strict` (red by
`check_targets.sh || exit 1`, Makefile :1999, quoted by the critic).

## The binders drill (R3), re-run by the coordinator

Tree: the assembled tip's memfn/ + the base's tests/mech and tests/memfn, ROOT = TREE = that tree, runners
of C0 (the base). `TMPDIR` under the round dir.

| case | row edit | result |
|---|---|---|
| (a) control | S3535 SAB_FILE -> `memfn/src/window_vform.c` | rc 0; `S3535 ... OK window_vform.c ... PASS`; `mech 187 rows, 187 OK, 0 bad, floor 187` |
| (b) re-keyed broken AFTER | + `stamp = w64_undeclared;` | **rc 1**; `... FAIL .../window_vform.c: In function 'pcrec_mf_wf_span_v_define'`; `mech 187 rows, 186 OK, 1 bad, floor 187` |
| (b') rev 2's binders.py (d408626c5), same tree | as (b) | rc 0; `mech 186 rows, 186 OK, 0 bad` (r98's defect reproduced) |
| (d) mech row leaves the selection | SAB_FILE -> `memfn/src/levels.c` | **rc 1**; `mech POPULATION 186 BELOW FLOOR 187 (rows left the selection)` |
| (e1) census control | `ren_search` row key -> `window_ren.c` | rc 0; `census 67 rows, 67 OK` |
| (e2) census row leaves the selection | key -> `levels.c` | **rc 1**; `census POPULATION 66 BELOW FLOOR 67` |
| (e3) census row MIS-keyed inside the population | key -> `window_vform.c` (text is in window_ren.c) | rc 0, `OK window_ren.c window_vform.c`: see COORD-1 |

## Lenses as run

| agent | model | question | time | raised |
|---|---|---|---|---|
| closure (critic) | sonnet | (a) R1-R26 closed by id in the text and instruments; (b) §8.2/§8.3/§8.4 name every Linux arm with a reason, consistently; OC1-OC3 facts | ~8 min | 5 |
| verifier | sonnet | CLOSURE-1..4, independently | ~2 min | 4 HOLDS |
| coordinator | (inline) | every Mac arm at the base, syncheck at the tip, the binders drill | ~2 h wall (18:30-20:27 under the lock; the sweeps ran slower than §8.4's, 851-1,206 s vs 467-581 s, because the box was shared) | 2 notes |

One critic by the launcher's scaling; the verifier ran as a SEPARATE agent (r98's gap not repeated).

## Findings (PROPOSED disposition)

- **CLOSURE-1 The Linux-listed arms have no base run and no stated point for one** (critic; verifier HOLDS).
  §8.2 states the rule as "a gate arm is used only on a box where its BASE run is GREEN"; r98's RULING:
  "Every gate arm's BASE run must be GREEN on the box it is listed for before it is used" (no Mac
  qualifier). §8.4 is Mac-only; §8.3 says "The Linux arms are OWED by the build lane at the tip". Every
  arm moved to Linux (`make strict`, test-memfn-finder + purity reach, test-memfn-stamps, test-memfn-g2 /
  run_g2.sh, plain run_g2_win.sh, run_g2_pres.sh + `--plants`, g2_vspan.py, the g2v/simdfloor mech rows,
  G5) was moved on evidence that it is red on the Mac, not that it is green on Linux; the "no base run,
  not listed" reason used to drop the Mac's G5 is not applied to the Linux side. S3012: §8.2 relies on
  `run_g2_pres.sh --plants` EXECUTING S3012 on Linux ("EXECUTES its 7 re-aimed plants (S3012 stop; ...)"),
  the only arm that does, and S3012 is under triage as not detected on x86. **FIX-NOW** (text): §8 makes
  "every Linux-listed arm's base run, green, recorded" the build lane's FIRST step, before C0b (a red one
  is moved or ruled like OC1-OC3), and says what follows if S3012 stays undetected (its arm is not a
  gate for that plant until the triage lands).
- **CLOSURE-2 G5's REACH_ONLY mech half dropped from the Mac without its own reason** (critic; HOLDS).
  Rev 2's Mac cell "`make test` yes; mech yes" became "not listed (no base run: ~100 min)"; the reason
  covers `make test` only; §R2.1 has no G5 row. **DOC**: one clause for the mech half (measured and
  moved, or run and listed) and a §R2.1 mention.
- **CLOSURE-3 G3's Mac plant ids written as ranges that over-read** (critic; HOLDS). "S1400-S1428, ...
  S3084-S3096" covers ~20 ids that are not re-aimed (S1408, S1411-S1421, S1424, S2988, S2990,
  S3085-S3088, S3094, S3095); the count 33 (and pres 7, proof 1) is right. **DOC**: list the 33, or
  "the run_g2_win rows repoint.py prints".
- **CLOSURE-4 kit_pos.c's title omits R13's two names** (critic; HOLDS). files.spec:6's title (which
  assemble.py writes into the file's head comment, asm kit_pos.c :4) names kit_mass and kit_run_member
  only; kit_run_set (:130) and kit_run_at (:139) are in the file. cut.spec:1 still reads "rev 2 §3 ... at T
  a0f13ad83". **DOC** (files.spec + cut.spec header; no assembled byte the gates read moves).
- **CLOSURE-5 §7.8's drill labels skip (c); the drill tree is uncommitted** (critic). **NOTED**: this round
  rebuilt it from the prose in minutes (table above).
- **COORD-1 binders.py's OK means "found once, anywhere", not "found in its key"** (coordinator, probed).
  A row mis-keyed to another population file reads OK (e3), so arm 8 alone does not catch a peel that
  re-keys a row to the WRONG file or forgets one. The sibling arms do: SABANCHOR on the drill tree with
  S3535 keyed window_ren.c prints `ANCHOR NOT FOUND`; decider_census.py at the tip with `ren_search` keyed
  window_vform.c prints `FAIL: window_vform.c: member ren_search is not defined there`; `--plant-check`
  reads FILE@@FROM. **NOTED** (+ DOC: §7's "OK file" sentence says the key itself is bound by G1.3, G1.4,
  G1.6).
- **COORD-2 `--compile`'s temp files follow `$TMPDIR`**; G1.8's command does not set it (the coordinator's
  first drill call, without it, wrote a tempfile under /tmp, which the mandate keeps out of use). **DOC**:
  G1.8 spelled with `TMPDIR=$PCREC_TMPDIR/...`.

## OC1-OC3: facts (no disposition)

- OC1: `tests/memfn/run_purity_reach.sh` :70 passes the 4-line NEVER as `awk -v nv="$NEVER"`; this Mac's
  /usr/bin/awk (20200816) refuses a newline in `-v` (`awk: newline in string`, rc 2; gawk absent);
  re-run: test-memfn-finder `checks passed: 28889`, `checks failed: 49`, all 49 purity-reach rows,
  nothing else red. U1 rewrites the script anyway (§7.4), so choice (a) (ENVIRON or a file) is inside a
  file the unit already edits.
- OC2: `tests/memfn/libc_census.py` `MOVERS_FLOOR = 1`; re-run red with `0 SIMD-on movers < floor 1`. The
  FORMS/LIBC stamps are lines of artifact text, so G2's byte-identity arms already compare them on the
  Mac (critic's fact; §8.2 G7 does not say so).
- OC3: run_g2.sh bare exits 2 at :290 (mftrace lib missing); as the make target its window section runs
  plain run_g2_win.sh (v_section, x86-64-v3 text) and its presence section run_g2_pres.sh (`host_has`
  accepts x86-64 on arm64, :411-416); `run_g2_win.sh --plants` (:370-395) never calls v_section, which is
  why the Mac keeps that run.

## Closure R1-R26 (critic's table, review/closure.md)

R1-R26: 26 CLOSED (R13 with CLOSURE-4's title). Re-derived by the critic: binders 382 rows at floors;
repoint 202 rows / 19 units, per-unit counts equal §8.1, U3's 10 equal the text; U24's rows S3252 +
census `decide`; R16's four cites; R17's 48/46, 32, 18; kit.h 134 -> 137; kitgraph empty spec 1 SCC of
24 files without kit_kb.c/kit_pos.c; tables.py 0 crossings.

## PROBED-AND-HELD

- 25 Mac arm commands re-run at the base, each its own command; every §8.4 last line reproduced.
- syncheck at the tip 82/82; at the base 40/40.
- Drill: 7 cases (3 red as designed, 1 rev-2 control green, 3 controls/probes green); 2 sibling-gate
  probes red as COORD-1 needs.
- Critic: 382 binder rows, 202 re-points, 4 counts, 12 quoted facts against B (critic file).

## Lessons for the guide (proposed)

1. A box rule ("green at the base on the box it is listed for") is applied to EVERY box a design lists,
   or the design names when the other box's base run is taken; a light re-check brief asks for both
   (CLOSURE-1: the Mac half was done thoroughly, the Linux half silently became "owed").
2. A re-aim instrument that reports "found" is not a key check; a per-commit gate list names which arm
   binds the KEY (COORD-1).
