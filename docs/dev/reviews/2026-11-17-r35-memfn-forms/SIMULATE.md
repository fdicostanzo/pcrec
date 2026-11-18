# SIMULATE findings: crit-memfn-forms

## Findings

### SIMULATE-1: the "predicted tie" does not give h* = 64: on pure noise the rule ships a MEASURED shorter head about 1 time in 3 (text and script agree)
- status: CONFIRMED (simulation of the rule, and cards.py `rule` itself on sampled outcomes)
- severity: design (a byte move shipped on noise: h* < 64 moves covers/pre-check runs at today's width, labelled MEASURED)
- effort: M ; blast radius: every card night; the identity population and the width night follow the noise pick
- where: r45_reply rev 6 §3 R1 steps (2)-(4) and "Why the dominance step" ("When nothing dominates anything (the predicted tie), step (3) removes nothing, and h* is still 64"); cards.py:501-543, 583
- repro: `python3 -I SIMULATE/noise.py 2000` (my text implementation SIMULATE/myrule.py, written from §3 before reading r1): every arm-cell of C1-C2 (108 cells x 10 arms) gets its own noisy median ratio, as cards.py times them (it times H(h) separately even where its text IS I's, e.g. every head on lit40/abc60, H(64) everywhere); f = max |aa/aa-twin - 1| over the 12 A/A cells (cards.py:572-582). Result: P(h* != 64) = 0.341 / 0.354 / 0.333 at median sigma 0.2 % / 0.5 % / 1 % (2000 trials each; picks spread 0..32, 32 most often). With text-identical cells forced to t(I) exactly (not what the script does) it is WORSE, 0.464. Six sampled outcomes pushed through `cards.py rule` (`python3 -I SIMULATE/noise.py 6 sample`, cases/noise1..6): script h* = 32, 32, 32, 32, 24, 0, all "MEASURED", identical to my text implementation.
- argument: f is the max of 12 A/A draws but is used as a per-cell threshold over 108 cells x 9 heads (W's max and dominance's "beyond f in at least one cell"). A multiple-comparison effect: some head is "faster beyond f" somewhere and "slower beyond f" nowhere by chance, dominates 64, and the largest kept head < 64 ships. The design's drills (i)/(iv) use 1-6 cells with every ratio inside f, so they never exercise it. The rule needs a floor sized to the number of comparisons (or a per-cell A/A twin, or dominance requiring a win reproduced across regimes/layers) before the night; as written the "nothing moves at h* = 64" prediction holds only about two nights in three.

### SIMULATE-2: cmd_rule's bimodal test (launch range > 2 f x median) voids ~95 % of C1-C2 cells under ordinary unimodal noise, so step (5) fires every night
- status: CONFIRMED (simulation + cards.py `rule` on one constructed outcome)
- severity: design (the cards can never pick: h* = 64 "void twice" every night, the run's cost bought nothing)
- effort: S ; blast radius: every card night
- where: cards.py:592-594 (`med[k][1] > 2 * f * med[k][0]`), :403 (spread = max - min of the LAUNCHES launches); cover_cap.md §11.4 procedure ("the launches' spread exceeds twice the floor")
- repro: `python3 -I SIMULATE/launch.py 500`: 5 Gaussian launches per arm-cell, median and max-min exactly as run_cell writes them, f from the A/A medians as cmd_rule computes it: void cells per trial median 102 / 104 of 108 at launch sigma 0.3 % / 1 %; step (5) fired in 500/500 trials each. Through the script: `python3 -I SIMULATE/launch_one.py` (cases/launch1/results.tsv) prints `h* = 64, h = grid top (64, CHOSEN): cell(s) abc60/hit-dense/off, ... void twice` listing most cells.
- argument: f is a |ratio of two medians - 1| (about 2.8 sigma_median at its max over 12), the spread is the RANGE of 5 raw launches (about 4.2 sigma_median on average, per arm), and a cell is void if ANY of its 10 arms exceeds 2f. A range-vs-median-ratio comparison is not bimodality. The bench's "spread" field (a bench-only question in cover_cap.md) may not be a raw range; the script picked one and nothing checks it fires only on bimodal data. Needs a bimodality statistic that a unimodal control passes (e.g. a sabotage-style self-test: unimodal launches must not void).

### SIMULATE-3: C3 always times H(64), so at any h* < 64 R2 and R5 read no C3 cell and print nothing (a silent pass of the long-span sanity check)
- status: CONFIRMED
- severity: design (R5's trigger and R2's C3 dial evidence are lost exactly when a byte-moving head is picked)
- effort: S-M ; blast radius: R2, R5, the trigger to extend the grid past 64
- where: cards.py:129-140 (`cells(hstar=GRID_TOP)`), :488 (`cmd_run` calls `cells()` with no h*), :609-626 (R2/R5 look up `"h%d" % hs`); r45_reply §3 "The cards" C3 = I, L, H(h*); R1 "C3 times only I, L and H(h*): it cannot feed the pick it depends on"
- repro: `python3 -I SIMULATE/c3.py`: C3 rows as cmd_run writes them (arms I, h0, h64; H(64) 1.3 x I, L 1.5 x I in every cell). With C1-C2 data whose pick is h* = 16 (drill (x)): `rule: h* = 16, MEASURED`, R2 lines 0, R5 lines 0. Same C3 rows at h* = 64: R2 48 lines, R5 48 lines.
- argument: `run` times C1-C3 in one pass before any pick, so C3's H(h*) arm is H(64), and no command times C3 at the picked head; cmd_rule then silently finds no `("C3", pat, "h<h*>")` key and reports no loss. The script needs a second pass (C3 at the picked h*, before the identity check) or at least a loud "R5/R2(C3) NOT COMPUTED at h* = N" line. Note the design itself puts C3 in night-order step 1 beside C1-C2 (§3 "night order" step 1: "The form cards C1-C3 and C5 run ... h set through the head lever"), which cannot time H(h*) before step 2 freezes h; the design and the script should say C3 runs after the pick.

### SIMULATE-4: a wrong answer during `run` is recorded as a VOID cell, not R0's DEFECTIVE; with step (5) the defective head can be the one that ships (H(64)); the text itself ships 64 under a void even when R0 removed 64
- status: CONFIRMED
- severity: answer (a gate-failing form can ship as the default) / design
- effort: S ; blast radius: R0's whole meaning on the night
- where: cards.py:489-492 (`run_cell` raises on `GATE FAIL`, cmd_run writes `void <msg>`), :567-570, :540-542 (`return top, ...` with no check that `top` survived R0); r45_reply §3 R0 row and step (5) ("h* = 64")
- repro: (a) `SIMULATE/adv.py` case gatefail-h64 (cases/gatefail-h64/results.tsv: one row `C1 hex32 h64 hit-dense off void x`, as cmd_run writes a gate failure): `rule: h* = 64, h = grid top (64, CHOSEN): cell(s) hex32/hit-dense/off void twice; the cells read picked H(64)`. H(64) gave a wrong answer and is both shipped and the recorded pick. (b) case r0-64-void (`--g2` file `64`, drill (ii)'s data plus one twice-void cell): `h* = 64 ... the cells read picked H(32)` while R0's line says `R0 defective heads: [64]`. My text implementation does the same in (b): §3 step (5) says h* = 64 unconditionally.
- argument: R0 says a form whose answers differ "leaves the grid, is filed, and sets nothing"; the script only learns R0 from a hand-written `--g2` file and turns its own gate's failure into a void, which (SIMULATE-2/step 5) ships 64. Fix: a GATE FAIL row is R0 for that head (a distinct row kind, read into `defective`), and step (5)'s fallback must be the largest R0-surviving head (or "no form ships") - a text edit too.

### SIMULATE-5: drill (viii)'s last case (every finite head fails R0) crashes cmd_rule with a ValueError; the selftest omits that drill
- status: CONFIRMED
- severity: maintenance (the plan-A fallback outcome is a traceback, not "no form ships")
- effort: S ; blast radius: the rule's one fallback outcome
- where: cards.py:514 (`min(W.values())` on empty), :583; DRILLS (:675-757) has no "(viii) every finite h fails" row; r45_reply §3 drill (viii) "If every finite h fails, no form ships and plan A falls back"
- repro: `python3 -I cards.py rule SIMULATE/cases/r0-all/results.tsv --g2 SIMULATE/cases/r0-all/g2.txt` (g2.txt = `0 1 2 4 8 16 24 32 64`) -> `ValueError: min() iterable argument is empty` (cards.py line 514), exit 1.
- argument: §3 states this outcome; the script should print it (and the selftest should state it), per the drill list it claims to cover ("selftest: the rule against every drill r45_reply rev 6 §3 lists").

### SIMULATE-6: no re-run: a cell void ONCE is read as "void twice" (step (5) fires on the first void)
- status: CONFIRMED (by reading; no re-run path exists)
- severity: design (with SIMULATE-2 this makes every night a void night; alone it doubles the void rate's effect)
- effort: S-M ; blast radius: step (5)
- where: cards.py:482-494 (`run` times each cell once, writes `void`), :589-602 (any void/missing/bimodal cell goes straight into `void_cells`); `grep -n -i "re-run\|rerun" cards.py` finds nothing; r45_reply §3 "A cell missing a regime": "VOID and re-run once, and R1 waits for the re-run only. A cell still void after the re-run is read by step (5)"
- argument: the label the script prints says "void twice" for a cell timed once. Needs a re-run command over the void cell list (results merged by cell), and cmd_rule should refuse to apply step (5) to a cell with only one attempt (or label it "void once: re-run owed").

### SIMULATE-7: NOT-WARM and short-subject cells are timed by the kit's own approximations and READ by R1 as those regimes; nothing in results.tsv or the rule's output marks them, and §3's branch (bench method, else void twice) is not implemented
- status: CONFIRMED (by reading; `plan` is the only command that prints the APPROX note)
- severity: design (an h* labelled MEASURED can rest on a regime method §3 says the cards may not substitute)
- effort: S ; blast radius: 2 of 6 regimes, about a third of R1's cells
- where: cards.py:104-112 (APPROX), :187-189 + DRIVER `call()` regimes 1/2, :416-417 (printed by `plan` only), cmd_rule :586-603 (reads every regime alike); r45_reply §3 "The regimes' methods": "NOT-WARM's method is the bench dev's (D198 (f)), and `short-subject-search` is the bench's subject ... If either cannot run on the kit's harness, the cells in that regime run on the bench ... If neither, those cells are void twice, and step (5) reads them"; kit-grid.tsv ver-7 header says the same "approximations until the bench names its methods"
- argument: §3 allows exactly two readings for these regimes: the bench's method, or void twice (h* = 64, labelled). The script adds a third (an unvetted approximation read as the regime). At minimum `rule` should print which regimes were approximations and refuse a MEASURED label resting on them (or treat them as void, per §3) until the bench's method replaces them. The not-warm subject is also miss-heavy text only (cards.py:187), so NOT-WARM is never timed on hit-dense or near-miss subjects.

### SIMULATE-8: `identity`'s population is a hand list: the "census covers" are 6 literals that omit most of cover_cap.md §6's census, and the predicted movers are an OPTIONAL file whose absence passes silently
- status: CONFIRMED (list comparison; run: `WIDTH_FLAG=none cards.py identity 64` -> "21 patterns x 2 layers, 0 differ"; control `identity 0` -> 14 differ, so the comparison itself works)
- severity: design (the identity check is what ties the width night's binary to the timed one; at h* < 64 its population is §3's "EVERY predicted mover")
- effort: S-M ; blast radius: the night order step 3 gate
- where: cards.py:780-785; r45_reply §3 "The identity check": "EVERY predicted mover at h*, cover or not (the sweep's prediction ...), plus every card pattern and every census cover"; cover_cap.md §6 Movers table
- argument: the script's census list is `[0-9a-f]{32}`, `\d{32}`, `\b[0-9a-f]{32}\b`, a uuid PREFIX `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}`, `\w{32}\B`, `(?i)[0-9a-f]{40}`. §6's census has `lit-l31`, `dig-exact-32`, `hex32-id`, `loglines/uuid`, `wild-validator-uuid-grok`, `litrun.rxt:1204`/`:1320`, the 10 k = 1 patterns of §2, `counterk.rxt:1919`, `spanarms.rxt:96`, `d27_large_counts.rxt:6`/`:37`, both encodings (the script never compiles `-e utf8`/`-i`). The census should be READ from its source (the sweep's corpus list), not retyped, and `identity H` with H < 64 and no PATTERNS file should refuse ("predicted movers missing") rather than pass on the cards alone. Also, with FROZEN unset the "frozen" harness and the "rebuilt" pcrec are the same build dir, so a mis-set run compares a binary with itself's harness and passes.

### SIMULATE-9: labels: MEASURED carries no card ids, DERIVED is never printed (R3 prints per-class picks but no tracks/does-not-track verdict), and the grid-top punctuation differs from drill (v)'s
- status: CONFIRMED
- severity: doc
- effort: S ; blast radius: the record the landing ships with
- where: cards.py:536-537 (`label = "MEASURED"`), :627-634 (R3); r45_reply §3 step (4) "labelled MEASURED with its card ids (DERIVED if R3 fires)"; R3 row "if h* tracks E[D] in every class, h becomes a derivation"; drill (v) "grid top (64, CHOSEN): every shorter..." vs the step-(4) wording the script uses ", every shorter..."
- repro: every MEASURED drill in `cards.py selftest` prints the bare word MEASURED; my 300 random outcomes differed from the script ONLY in the (v) punctuation (12 of 300, all the "every shorter finite head" label; SIMULATE/rand.py).
- argument: the label is the record D149 requires (MEASURED with its card ids); the R3 verdict that would switch MEASURED to DERIVED is never computed. The (v) colon/comma is the design's own inconsistency; pick one.

### SIMULATE-10: the NOT-WARM driver runs an untimed 32 MiB eviction sweep before EVERY 4 KiB chunk inside the 50 ms calibration loop: by arithmetic the not-warm cells alone are hours per night
- status: SUSPECTED (no timing allowed; confirm with one not-warm launch's wall time in the cards' own window)
- severity: speed (the night's fit: "one night, or two")
- effort: S ; blast radius: the window request
- where: cards.py DRIVER `call()` regime 2 (`for (i = 0; i < EVICT; i += 64) evict[i]++` per CHUNK) and the `do ... while (ns < 5e7)` loop; run_cell LAUNCHES = 5; plan: not-warm cells = C1 80 + C2 100 + C3 24 + C5 13 + AA 4 = 221
- argument: a 1 MiB subject is 256 chunks; each sweep touches 524,288 lines of 32 MiB (memory-bound, ~2-5 ms), so one call is ~0.5-1.3 s untimed for ~1 ms timed (about 4 us per 4 KiB at 1 ns/B). Reaching 50 ms timed needs ~50 calls: ~25-65 s per launch, x 5 launches x 221 cells = ~8-20 h, before the other regimes. Calibrate on CALLS for not-warm (or a smaller subject), and state the expected wall in `plan`.

## PROBED-AND-HELD

- (a) Rule fidelity. My text implementation (SIMULATE/myrule.py, written from §3 before reading cards.py's r1/cmd_rule) vs `cards.py rule` over constructed results.tsv + same_as_I.json (SIMULATE/sim.py, drills.py, adv.py, rand.py): drills (i)-(xiv) and R3-1 mapped onto real C1-C2 cells (19 cases): h*, recorded pick and label agree in all 19 (one punctuation difference, SIMULATE-9). 300 random multi-cell outcomes (1-8 perturbed cells, f in {0.01, 0.025, 0.04}, 30 % with 1-2 twice-void cells, 15 % with one R0 head): h* and recorded pick agree in 300/300, labels in 288 (the 12 = SIMULATE-9 punctuation). A twice-void cell in EVERY one of the 108 C1-C2 positions on drill (ix)'s data: 108/108 agree. R0 removing the top head (clean): agree (h* = 8). Ties exactly at 1 + f: both use strict `>` for dominance and `<=` for E; the one boundary case differed only through %.9f rounding of the written median (held). f not computable (A/A not-warm/on missing): script prints the night VOID and exits 2, as R5-7 (c). W only over cells READ, dominance only over cells READ, the twice-void term 1 only for heads whose text is I there (read from same_as_I.json, i.e. from the artifacts): held.
- `cards.py selftest`: 21 drills ok; each states the §3 result (h*, label) for (i)-(xiv), R3-1, (vii'), the three (x) variants and both (xi) variants; data checked against §3's numbers by hand (W, thresholds, dominance) for (ii), (vi), (ix), (x), (xii) clean/void24/void40, (xiii), (xiv). Missing only (viii)'s last case (SIMULATE-5).
- (b) Fidelity. `dry --quick` on the comb tree (PCREC_TREE/FROZEN = crit-memfn-forms-comb, width 4095): 1374 cells built and gated, 0 failures, 269 distinct compiles; artifacts: every timed C1-C4 arm takes `cover`, C5's engine arm `unanchored`; loop counts as the forms predict (uuid36 L = 5 loops; hex24/dig24 H(h >= 24) and I 0 loops); H(h) text identical to I exactly where h >= k for the class shapes and in every head for lit40 / abc60. The timer's exe is the gated exe (same cached binary; the timed launch re-gates its first call). I = `pcrec-harness --memfn=no-span-loop`, h<N> = `--harness=span-head=N`, engine = `--memfn=no-window-search`, A/A = the same lit16 binary twice: all on ONE frozen harness binary, as §3. Regimes: the six of C1's list, both layers (C5 off only, §3 "n/a"); near-miss = k - 1 members then a non-member of the last set, as EMITTED-2. f = max |aa/aa-twin - 1| over 6 regimes x 2 layers, a ratio, as §3 / cover_cap §11.4. `identity 64` (subject tree, WIDTH_FLAG=none): 21 patterns x 2 layers, 0 differ; control `identity 0`: 14 differ.
- kit-grid@7 rows (span_cross, span_pop, span_long, span_size, span_engine) match C1-C5's patterns, k, layers and launches (5; C4 1, compile only); C2's 49/60 rows are counterk.rxt:1919 and spanarms.rxt:96, cover_cap §6's census rows. Note (not filed): R4 compares C1's near-miss H(h*) on BOTH layers against C5's engine on layer off only; the ver-7 header calls C5's unit "the engine route over I" while R4 reads it against H(h*).
- Simulations: 8000 noise trials (SIMULATE-1), 1000 launch-level trials (SIMULATE-2), 6 + 1 of them through cards.py. Compiles used: ~270 (dry) + 168 (identity x 2).

CRITIC COMPLETE
