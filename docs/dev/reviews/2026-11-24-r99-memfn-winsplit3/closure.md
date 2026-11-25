# CRITIC closure (sonnet): memfn-winsplit3

## Findings

### CLOSURE-1 (design, medium; text only; §8.2 G1/G3/G5/G7, §8.3, §8.4) CONFIRMED
The base-green rule is applied to the Mac only. §8.2's rule sentence: "a gate arm is used only on a box where its BASE run is GREEN"; G5's own sentence: "an arm with no base run on a box is not listed for it (R1's rule)". Yet every arm moved to Linux is listed REQUIRED for Linux with no Linux base run (the design lane has none; §8.3 last paragraph: "Linux arms are OWED by the build lane at the tip, not run by this design lane"): `make strict`, `test-memfn-finder` (+ purity reach), `test-memfn-stamps`, `test-memfn-g2` / `run_g2.sh`, plain `run_g2_win.sh` (v_section), `run_g2_pres.sh` + `--plants`, `g2_vspan.py`, mech g2v/simdfloor rows, and G5 (`make test`, listed Linux-REQUIRED while Mac G5 is dropped for exactly "no base run"). r98's RULING says "every gate arm's BASE run green on the box it is listed for" (no Mac qualifier). Observed: §8.4's title and table are Mac-only; no text says the Linux base run is the build lane's FIRST step (before commit C0b). Expected: either a line in §8.1/§8.2 making "the Linux base run of every Linux-listed arm, green, before C0b" a precondition (the OC1-OC3 arms were moved to Linux on the evidence they are red on the Mac, not that they are green on Linux), or the same "not listed" treatment. Note for the S3012 clause: §8.2 G3 and §8.3 rely on run_g2_pres.sh `--plants` EXECUTING S3012 (stop) on Linux (§8.2 line "EXECUTES its 7 re-aimed plants (S3012 stop; ...)", §8.3 G3 Linux cell "its 7 plants"); S3012's detection on x86 is under separate triage, so that Linux arm's base run is the one most likely to read red.

### CLOSURE-2 (doc, small; §8.2 G5, §8.3 G5 row, §R2.1) CONFIRMED
Rev 2's Mac G5 cell was "`make test` yes; mech yes" (diff, removed line `| G5 | `make test` yes; mech yes | yes |`). Rev 2.1 drops the whole Mac G5 with one reason, "`make test` measures ~100-105 minutes ... its base run is not taken here". That reason covers `make test`; G5's first half, "REACH_ONLY mech over the re-pointed rows", is a separate arm with no stated Mac base run and no stated reason, so it is dropped without a row of its own. §R2.1's table has no G5 row either (R1 and R2 rows name G1, G3, stamps; G5 appears only in §8.2/§8.3). Fix: one clause naming REACH_ONLY mech as measured-and-moved or run-and-listed, plus a §R2.1 mention.

### CLOSURE-3 (doc, small; §8.2 G3 Mac bullet) CONFIRMED
The 33 re-aimed run_g2_win plants are written as ranges "S1400-S1428, S1543, S2986-S2991, S3040, S3041, S3084-S3096, S3116-S3118". binders.py over the assembled tip (`python3 -I binders.py <B tree> asm <C0 runners>`, rows with new key != B key, run_g2_win.sh) gives exactly 33 labels: S1400-S1407, S1409, S1410, S1422, S1423, S1425-S1428, S1543, S2986, S2987, S2989, S2991, S3040, S3041, S3084, S3089-S3093, S3096, S3116-S3118. The ranges include ids that are not re-aimed (e.g. S1408, S1411-S1421, S1424, S2988, S2990, S3085-S3088, S3094, S3095; S2988 is rows_check's). The count 33 and the pres 7 / proof 1 are right (pres: S3012, S3047, S3106, S3110, S3112, S3125, S3126; proof: S1419); only the id spelling over-reads. Cheap fix: "the plants repoint.py lists for run_g2_win".

### CLOSURE-4 (doc, small; files.spec, cut.spec, §3) CONFIRMED
R13 is closed in cut.spec (`kit_pos.c <- presence.c 56-91 112-118`), §3 row, §6.2, §8.1 U3 and the assembled kit_pos.c (kit_run_set :130, kit_run_at :139; kit_wspan_at stays in presence.c :80), but files.spec's kit_pos.c title, which assemble.py writes into the file's header comment, still lists only "kit_mass, from presence.c" and "kit_run_member": `head -5 asm/memfn/src/kit_pos.c`. The built file would carry a header that omits two of its four moved names. (cut.spec's first comment line also still reads "rev 2 §3 ... at T a0f13ad83".)

### CLOSURE-5 (doc, trivial; §7.8) CONFIRMED
The drill table lists cases (a), (b), (d); there is no (c). The drill's tree ($S/drill) is lane scratch, not committed, so a reader reproduces it only from the prose. Reproduced here statically (no compile): S3535 re-keyed to window_vform.c over the assembled tip -> `binders: mech 187 rows, 187 OK, 0 bad, floor 187` rc 0; re-keyed to levels.c -> `binders: mech POPULATION 186 BELOW FLOOR 187 (rows left the selection)` rc 1. The broken-AFTER case (b) needs a compiler; not run (the coordinator's drill).

## (b) facts for OC1-OC3 (no disposition)
- OC1: tests/memfn/run_purity_reach.sh line 70 at the base: `awk -v o="$old" -v n="$new" -v nv="$NEVER"`, with NEVER a 4-line single-quoted string (lines 63-66). On this Mac, `/usr/bin/awk` is "awk version 20200816" and `echo x | awk -v nv="$(printf 'a\nb')" '{print nv}'` prints `awk: newline in string a` / `b... at source line 1`, rc 2; so the script's failure path (line 74, "its text does not occur exactly once in window.c") fires for every row with text. gawk is absent here. The script's population is read from window.c (line 27 `win=`), so U1 rewrites it in any case (§7.4). Matches §8.4.
- OC2: tests/memfn/libc_census.py has the literal `MOVERS_FLOOR = 1` (line ~127) and `bad('FORMS movers: %d SIMD-on movers < floor %d')` at ~422; the target is `test-memfn-stamps` -> `bash tests/memfn/run_libc_census.sh` (Makefile :1538-1540). Not run (needs build). Related fact: the `_MEMFN_FORMS`/`_MEMFN_LIBC` stamps are lines of artifact text (STAMP regex over the .c), so G2's byte-identity arms 2 and 3 on the Mac compare them; §8.2 G7 does not say so.
- OC3: run_g2.sh line 290 `[ -f "$lib" ] || { echo "run_g2.sh: $lib missing (build pcrec first)" >&2; exit 2; }` (bare exit 2, as §8.4); `make test-memfn-g2` = `bash memfn/tests/run_g2.sh --quick` with the mftrace lib (Makefile :1648-1650); its window section runs plain run_g2_win.sh (v_section) plus a traced pass (:1047-1070), its presence section runs run_g2_pres.sh (:1078-1086), whose `host_has` returns 0 for every target except x86-64-v3 (run_g2_pres.sh :411-416), so x86-64 text is attempted on arm64. run_g2_win.sh `--plants` (:370-395) never calls v_section (that is at :433/:448/:651). Matches §8.2/§8.4.
- Also: `make strict`'s tail, Makefile :1999, `bash memfn/tests/check_targets.sh >/dev/null || { ...; exit 1; }`, as §8.2 says.

## (b) consistency of §8.2 / §8.3 / §8.4 / §R2.1
- Every Mac arm in §8.3 has a green base row in §8.4 (G1.1, G1.2, G1.3, G1.4, G1.6 x4, G1.7, G1.8, G2 arms 1-3 + reach counter, G3 win plants / proof / proof plants, G4 nm, G6, G7 defines); no Mac-listed arm is shown red there. G1 arm 5 (purity reach), `make strict`, test-memfn-finder, run_g2.sh --quick / test-memfn-g2, plain run_g2_win.sh, run_g2_pres.sh (+ plants), g2_vspan, g2v/simdfloor mech rows, test-memfn-stamps and G5 are named Linux's with a stated reason in §8.2 and §8.3 (OC1/OC2/OC3, host ISA, no-base-run for G5) and agree across §8.2/§8.3/§8.4/§R2.1 except G5's mech half (CLOSURE-2) and the base for Linux (CLOSURE-1).
- Small wording gap: `make test-memfn-g2` and standalone `g2_vspan.py` appear as Linux arms in §8.3's cell but §8.2's Linux-only G3 bullet names neither (it names run_g2.sh (full) and v_section inside plain run_g2_win.sh); the Mac side says so in the stop-rule bullet. Cosmetic.


## Closure table (R1-R26)
| id | verdict | closing text / check |
|---|---|---|
| R1 | CLOSED | §8.2 G1 arm 1 (syncheck on the Mac), arm 2 (rows+link own command), `make strict` Linux's; §8.4 G1.1 `40 PASS`, G1.2 rc 0 (but see CLOSURE-1 for Linux arms' base) |
| R2 | CLOSED | §8.2 G3 by box, §8.3 G3 row, §8.4 rows; dropped run_g2.sh modes; plant counts 33/7/1 verified (ids spelled loosely: CLOSURE-3); text-only for S3012 caveat in CLOSURE-1 |
| R3 | CLOSED | binders.py: BORN from cut.spec + B_EDITED, FLOORS 187/75/49/67/4, CC env-only; rerun over the tip: 187/75/49/67/4 all OK; floor drill (d) and re-keyed control reproduced (CLOSURE-5). Ruling's "57" is the window/presence/compose subset; script and §7 use 67 = 57 + 10, verified: B decider_census.tsv keys 50+5+2 and 5+3+2 |
| R4 | CLOSED | §8.1 U24; repoint.py U24 rows = S3252, census `decide` (2), exactly as the text |
| R5 | CLOSED | `python3 -I repoint.py` over the tip: 202 rows in 19 units, per-unit counts equal §8.1 (U3 10, U4 1, ... U24 2); U3's 10 rows equal the text's list (S1094, S3106 x2, S1403, 6 census) |
| R6 | CLOSED | §8.1 U4 (` */` after :7; S3285 to window.h); B window.c :1-7 / :65 checked; cut.spec has 1493-1494 in window.h |
| R7 | CLOSED | §7.4 anchor per commit range, include clause dropped |
| R8 | CLOSED | §7.2 F2 restated, rev 1 sentence restored; anchor `static const ren_search_row ren_search[] = {` occurs once at B (window.c) and once at the tip (window_ren.c) |
| R9 | CLOSED | §8.1 C0b, §13 F1 (B CLAUDE.md 12,277 B; window.c entry ~4.5 KB to move) |
| R10 | CLOSED | §7.6, §8.1 (kit_kb.c C0b, kit_pos.c U2, kit_pick.c U3, window.h U4, peels, U24); files.spec has a title for every new .c file |
| R11 | CLOSED | §8.2 G2 counter, w32reach.py reads, floors 28/20 in §8.4 (arm text matches emit_sweep's no-span-vector pins 28/20 at emit_sweep.py :634-635); not run here (needs build/pcrec) |
| R12 | CLOSED | G4 +82/-3 (window.h 76 MF_NS names = 74 new + 2 already external; kit.h 134 -> 137 reproduced), G7 readers named; B memfn.h defines 30/4/11 as §8.4 |
| R13 | CLOSED (CLOSURE-4 for a title) | cut.spec, §3, §6.2, §8.1 U3, §7.6 PROVENANCE note; assembled kit_pos.c holds kit_run_set/kit_run_at; kit_wspan_at in presence.c; kit.h names unchanged; no binder in their text (repoint asserts) |
| R14 | CLOSED | §10 first bullet |
| R15 | CLOSED | §7.6 (window_ren.c, U13), binders.py `rows` population floor 4, 3 + S2984 |
| R16 | CLOSED | §4.4 :223, §6.6 :283, §3 :132-139, §6.1 :938-939; all four checked against B |
| R17 | CLOSED | §7.7: 48/46 at the stated command (reproduced 48 total / 46 without the two records), compose.c 32 and presence.c 18 (reproduced with the stated command; 30/17 without the lane records); 0 binders |
| R18 | CLOSED | §4.3; grep of the assembled tip: in/count/first have non-family callers, shape/two/full and the TIE predicates family-only |
| R19 | CLOSED | §1 Goal 1 (4 objects), §13.1 |
| R20 | CLOSED | §5 A5 |
| R21 | CLOSED | §12 O1 row (FILE CYCLES empty claim not re-run; tables.py at tip prints 0 crossing) |
| R22 | CLOSED | §1 non-goal, §6.4, §13 |
| R23 | CLOSED | §6.4/§6.5/§13.1: empty-spec kitgraph over the tip prints 1 CYCLE of 24 files, none of them kit_kb.c or kit_pos.c |
| R24 | CLOSED | §1 Goal 4, §6.5 |
| R25 | CLOSED | §7.3, §7.5 name both `count` and `in_set` |
| R26 | CLOSED | edits.spec block `A4 (r98 R26)`; assembled tip carries it (reassembling at B reproduces $S/asm, `diff -rq` empty) |

No NEW hole found in §7 or §8 from the rev 2.1 changes beyond CLOSURE-1/2: the per-commit binders population keeps re-keyed rows (drilled), the repoint lists are derived, and the U24/U4 additions are internally consistent.


## PROBED-AND-HELD
- binders.py over the assembled tip, B tests + C0 runners: 5 populations, 187+75+49+67+4 = 382 rows, 382 OK, all at floors.
- repoint.py: 202 rows / 19 units, 19 per-unit counts equal the doc's.
- assemble.py re-run at B: byte-identical to the coordinator's asm (49 files).
- floor drill without compile: 2 cases (control 187/187 rc 0; levels.c re-key 186 < 187 rc 1).
- kitgraph empty spec: 1 SCC, 24 files, no kit_kb.c / kit_pos.c. tables.py: 0 crossings.
- Counts re-derived: reader census 48/46, compose 32, presence 18 (3 greps); kit.h 134 -> 137; window.h 76 names; census.tsv key counts (50/5/2/5/3/2 + 4 other-key rows outside the population); g2 re-aimed per runner 33/7/1.
- Quoted facts checked against B: `make strict` tail, run_purity_reach awk, host awk 20200816, run_g2.sh :290, MOVERS_FLOOR = 1, B memfn.h defines, F1's CLAUDE.md size 12,277, finder.c :938-940, presence.c :223/:283, window.c :1-7/:65.
- Not run (need a build): w32reach.py, emit_sweep arms, every --compile probe, the drill's broken-AFTER case.

CRITIC COMPLETE
