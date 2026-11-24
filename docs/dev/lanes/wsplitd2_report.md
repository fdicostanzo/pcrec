# Lane wsplitd2 — the window family split, DESIGN rev 2 (review r95 applied)

Lane wsplitd2 (opus), 2026-11-24. Branch lane/wsplitd2, cut from the kit branch lane/memfn-wsplit
@ a0742283a. Design only: nothing under `src/`, `cli/`, `lib/`, `memfn/` (code) or `tests/` was
edited; no make was run; the assembler wrote only to `$PCREC_TMPDIR/scratch/wsplitd2/`.

## Summary

`docs/design/memfn/window_split.md` is rewritten as rev 2. It answers every r95 item by id (§R2
table there) and applies the ruled open choices O1-O7. The main change is r95's lesson 1. The cut is
no longer only a name census. A committed assembler (`window_split/assemble.py`) turns
`cut.spec` + `files.spec` + `window_h.in` + `edits.spec` into the actual tip tree: 22 new `.c` files
plus the private header `window.h`, with window.c removed. Every assembled file compiles with
`gcc-16 -fsyntax-only` under the strict flags plus `-Wmissing-prototypes`, plain and with
`-DMF_TRACE`. The result is **82/82 PASS**, and both controls behave as expected (§Assembler evidence).

The new instruments are:
- `binders.py`, the re-aim table plus the compile probe for every mech, G2, purity and census binder;
- `rekey.py`, which writes the decider census map at the tip;
- `tables.py`, Goal 1's single population;
- `syncheck.sh` and `unused.py`.

What changed in the design:
- **The split itself:**
  - frame/ren are split (O1), and the {frame, ren} SCC is gone: frame -> ren is 3 calls, ren -> frame is 0.
  - ARV-7's `kit_kb.c` leaf comes first (C0b).
  - The set family comes in with the widened U2b (O6).
  - The TIE table is exposed through two predicates with its enum private (O3).
- **The header:**
  - window.h is derived by assembly, not by counting names.
  - kit.h holds only names that something outside the family calls, plus one stated vocabulary exception.
- **The checks:**
  - The decider census pins are counted per commit: U3 gives 73/66, U5 gives 78/62.
  - The plant reading is stated, with the dependency on lane/memfn-plantcheck landing first (C0).
  - The gates are split by box. G2's x86-64-v3 arm runs on this Mac because it is text emission.

## Findings answered

| W | disposition | answer (note section) |
|---|---|---|
| W1 | FIX-NOW, applied (O1) | frame 277 + ren 415 lines. Pure move costs 86 statics / 40 types. The SCC through `wf_erows` is removed by per-table checks (`wf_span_check`, `wf_ren_check`) and `wf_ren_pieces`: frame -> ren 3, ren -> frame 0 (§5, §12) |
| W2 | FIX-NOW | Two-file reading, stated for main to confirm. `kit_pos.c` holds the position questions + `kit_run_member` + `kit_mass`. `kit_pick.c` holds the TIE table and its searchers. `kit_tie_member_key` goes static into presence.c. `sets_at` stays family-private. `kit_run_set/run_at/wspan_at` stay in presence.c (§6.2) |
| W3 | FIX-NOW | The vocabulary (`WF_SERVES_*`, `NU`, `use_nothing`) is in window.h's shared section. `use_nothing` is `static const` there; no code compares its address (grep 0) (§4.1) |
| W4 | FIX-NOW | C0b: `kit_kb.c <- compose.c 27-115` before the split. kit_kb.c is in no cycle at the tip (§6.4) |
| W5 | FIX-NOW | finder <-> window_ren (`wf_renders`/`fd_find`) is the H1 outcome. Reason: breaking it is a behaviour change. Trigger: the next T-FIND asker unit or H8's row (§6.5) |
| W6 | DOC | `mf_pres_ports` stays in presence.c; presence.c is outside the cut (§6.6) |
| W7 | DOC | D204 cited; main's readings attributed to main; limits stated ([IR-FORM] (4) at this trigger only, "emitter-shaped SIMD forms" binds §9, the [SP1D-KITSPLIT-SEAMS] seam half stays) (§0) |
| W8 | PLAN (main's) | recorded only (§13) |
| W9 | FIX-NOW | The general form is `kit_<family>.c`. Unlocks: [SP1D-ARGMIN]'s argmin goes to kit_pick.c; new position questions go to kit_pos.c (§6.3) |
| W10 | FIX-NOW | One spelling, `kit_pos_count(s) == 1`; the class_of claim is withdrawn (§6.1) |
| W11 | NOTED | A4 `wf_legacy_stream` sits beside `ren_find` as a noted deviation, recorded in its comment (§5) |
| W12 | FIX-NOW (O6 inside) | Widened: pffind `set_size`, finder :940, generic :110-111, `kit_mass`'s read. R-1 exclusions named (formhash.c:493, k1_ref.c). S452/S804 anchors kept byte for byte (§6.1) |
| W13 | FIX-NOW | kit.h rule + the H3/TIE vocabulary exception. Leaving kit.h: `wf_find_arm`, `wf_floor_arm`, `wf_part_site`, `kit_tie_takes`, `kit_tie_member_key`; 134 -> 137 names (§4.3) |
| W14 | DOC | `WF_VBLK_MIN/MAX` live in window.h; a NEON width is one header line (§9) |
| W15 | FIX-NOW | window.h is assembled (complete row types, `ren_key`, `wf_rc` body) and compiled through every includer; composition counted from the assembled file (§4.1, §11) |
| W16 | FIX-NOW | Assembler R4: an exported name's prototype is deleted; any other prototype moves to its definition's file (`plan_ix` included) (§11.1) |
| W17 | FIX-NOW | cut.spec corrected: ask -2876, text -3879, floor 3880-, efind 2649, vform 4321, floor 4608, presence.c 56-83 (§3) |
| W18 | FIX-NOW | `run_member` not renamed. It is the one tip "crossing static" and is a macro-argument false positive (§4.2) |
| W19 | FIX-NOW | Each accessor's kind (move / new read / merge / wrapper + propagation) and signature (§5) |
| W20 | FIX-NOW | 18 peels U6-U23 + U24, a pure `git mv` (100 % rename). Names declared in both directions. U23 writes decide's head. 20 new family files; 23 with the kit_* files (§8.1) |
| W21 | FIX-NOW | G1 runs `syncheck.sh` (`-Wmissing-prototypes`, `-DMF_TRACE` pass) and `unused.py` (§8.2) |
| W22 | FIX-NOW | Plants are read through lane/memfn-plantcheck's one applier (FILE any name). Per commit: `--plant-check`. At the tip: `--plants` executes them. The build DEPENDS on that branch landing first (C0) (§7.3) |
| W23 | FIX-NOW | Per-commit pins: U3 MEMBER_COUNT 73 / HITS 66; U5 78 / 62. Map edits listed. Tip census: 97 pass, 0 fail with those pins (§7.2) |
| W24 | FIX-NOW in U1 | Family list; NEVER insertion and link exclusion per the file holding the row (homes: ren 26, verify 12, stop 4, frame 4, margin 3) (§7.4) |
| W25 | FIX-NOW | Lists derived by binders.py: mech S1417, S3106, S3525; G2 S1402, S1405, S1410, S1428, S3106, S1427 (TO only); purity MARGIN. S3006/S452/S804/S3250 checked unaffected (§7.5) |
| W26 | FIX-NOW | §7 corrected (BUILD-FAILED, not killed). Probe: mech 186 PASS + S3285 through 19 includers; G2 75 PASS; same at B (§7.5) |
| W27 | FIX-NOW | G1 = `make CC=gcc-16 strict test-memfn-rows test-memfn-finder test-memfn-link` + the static checks (§8.2) |
| W28 | FIX-NOW | Third arm `--extra=-fmemfn-simd=x86-64-v3 --no-differ-floor` with a w32-stamp reach floor pinned from the base run; `--ref` is the unit's base. It runs on this aarch64 Mac (text emission, explicit family); executing x86 code is G3's, on Linux (§8.2) |
| W29 | FIX-NOW | Gates-by-box table. `g2_vspan.py` and G3's second layer are Linux-only and not run on the Mac. G6 owes a base run (§8.3) |
| W30 | DOC | 50 reader files (CENSUS of the spelling; a FLOOR of readers) (§7.7) |
| W31 | DOC | The "halves" claim is withdrawn (§12) |
| W32 | FIX-NOW | Blind spots stated beside their numbers; the header and compile questions now go to assembler + gcc (§13.1) |
| W33 | DOC | Re-measured: cites 819 in 186; B's SCC 9 files; public names from the assembled tree; presence.c and compose.c edges in the kitgraph runs (§2, §3, §6.5) |
| W34 | DOC | `wf_wsearch`/`wsearch_of` are ask's. presence.c's `run_modes[]` and its interface are outside the cut, with a trigger. `wf_rc` goes to window.h (§4.4) |
| W35 | DOC | Use memfn/NOTES.md (§13 F1) |
| W36 | FIX-NOW | `tables.py`, one population at both ends: pure move 13 of 30, tip 2 (the arm objects, by address) (§1, §4.4) |
| W37 | DOC | `spec_v4` and `fields.py` numbers dropped (F4 withdrawn); C-39's numbers are not restated (§13) |

## Assembler evidence

All commands were run from the worktree root, with `S=/var/tmp/pcrec-claude/scratch/wsplitd2`,
`TMPDIR=$S/tmp`, and gcc-16 = Homebrew GCC 16.2.0 on this aarch64 Mac.

| command | result |
|---|---|
| `python3 -I docs/design/memfn/window_split/assemble.py . $S/asm` | 22 new `.c` + window.h (561 lines). window.c keeps 0 lines. 7 other files edited (presence, compose, finder, ofsskip, precheck, pffind, generic) |
| `bash docs/design/memfn/window_split/syncheck.sh $S/asm gcc-16` | **82 PASS, 0 FAIL**: 39 .c plain + 39 .c `-DMF_TRACE` + 4 white-box drivers |
| control: the same over a copy of B's `memfn/{src,include}` | 40 PASS, 0 FAIL |
| control: `assemble.py . $S/pure --pure`, then syncheck | 44 PASS, 38 FAIL (all 19 family files, both defines): the edits are load-bearing |
| `unused.py` over the family + every edited file (tip) | 0 UNUSED; B control 0 |
| `binders.py . $S/asm $S/plantcheck --compile` (runners from lane/memfn-plantcheck 8bd727eab) | mech 187/187 OK (186 PASS + 1 header SKIP); g2 75/75 OK, all PASS; purity 49/49; census 57/57 |
| S3285 planted into the tip's window.h, then `-fsyntax-only` of each family file | 19/19 PASS |
| `decider_census.py --src $S/asm/memfn/src --map <rekey.py output> --no-plants`, pins 62/78 | 97 passed, 0 failed (B's pins: exactly the 2 pin checks fail) |
| `kitgraph.py` over the tip, every non-family file but presence.c dropped | no CYCLE |
| `tables.py` tip / pure | 2 / 13 of 30 |

The iterations to 82/82 are listed in the note §11.2.

The assembly does NOT prove that each intermediate commit (U2-U23) compiles. That is G1's job, per commit, using the same `syncheck.sh`.

## Open choices applied

All seven were applied as ruled in r95's RULING. Numbers are in the note §12.
- **O1 SPLIT frame/ren:** 277 + 415 lines; no SCC.
- **O2:** the planner stays separate files.
- **O3:** two TIE predicates; the enum stays private.
- **O4:** no file keeps the name window.c; U24 is a pure rename.
- **O5:** MARGIN gets its own file (98 lines).
- **O6:** U2b is inside the unit, widened.
- **O7:** find stays separate from frame.

The STOP RULE did not fire. Every searched table is static in its file at the tip. The two
crossing objects are arm objects compared by address, not searched tables (§4.4).

One reading is for main to confirm: W2's two-file reading of D204's "their final file" (§6.2).

## STATE AT HANDOFF

- Branch lane/wsplitd2. Commits: the instrument WIP commits plus the rev 2 commit carrying the note, the report and the CLAUDE.md lines. Nothing was merged.
- The rulings file `docs/dev/lanes/wsplitd2_rulings.md` was empty at every read (before each commit and before this report). No entry was applied.
- Depends on lane/memfn-plantcheck landing first (C0). It is not merged here (merge-base b9f81ef80).
- Owed at build time, not by this lane:
  - G6's base `-fstack-usage` run;
  - G2's x86-64-v3 reach floor, pinned from the base run;
  - G3's Linux half;
  - per-commit compile of the intermediate trees (G1).
- For main:
  - W8, the [IR-FORM] pointer;
  - confirm the W2 reading;
  - the re-check review number (r95 RULING: one or two critics on rev 2);
  - lessons 1-3 for the critic skill and the guide.
- OWED: none
