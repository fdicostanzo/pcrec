# origsurvey — search ORIGIN vs best necessary condition, per R17-b ALPHA cell (facts only)

Lane origsurvey, 2026-10-13, branch `lane/origsurvey` (off main b17aca968). Facts only: no
design, no fix, no ruling, no clock. Question (Frank): how many of the kit's R17-b timing
losses are "pcrec picked the wrong search origin" versus genuinely kit-side cost?

## Inputs and how each number is produced

- Cells, flags and timings: the kit's `r17loss_report.md` (`lane/r17loss`) and slot25c's
  `time.log` (copied byte for byte to `docs/dev/lanes/origsurvey/time.log`; `counts.txt`
  likewise, from `lane/r17loss`). Cell flags are `alpha_r17b.sh`'s CELLS list. Loss =
  `new-deny` ns on REGRESSION rows of the OFF layer (ON is an identical artifact, a replicate).
- Stamps: `build/pcrec -p rx <flags> --pattern P` at main, read off the emitted `#define RX_*`.
- Subjects: `slot25c/alpha/subj/*`, read-only. All densities and counts below are MEASURED on
  them (`docs/dev/lanes/origsurvey/survey.py`; run: `python3 -I survey.py <slot25c> src/findings/default.rxt`).
  "prior" = `src/findings/default.rxt`'s unigram ppm summed over the set (the shipped prior is
  unigram only, so a bigram prior is the independence product: labelled). The run-level
  estimator is not shipped in the default analysis; I used measured runs instead.
- Two density notions, both reported, because they disagree and the disagreement is the finding:
  - BYTE density: member bytes / subject bytes (what the brief's "~4x rarer" reads).
  - LANDINGS: maximal runs of the origin set S (a run-consuming scan lands once per run), versus
    occurrences of the condition. The control: the kit's counted `uses` per activation equals
    S-runs almost exactly (bounded prose64k 10079 vs 10079; hex-run prose64k 10454 vs 10454;
    dig digits64k 9055 vs 9057; vm-hat-1 prose64k 2210 vs 2144; dfa-hat prose64k 4717 vs 5767,
    the \b filter explaining the gap). So landings is what the site is actually charged for.
- Verdict rule per (cell, subject, mode) row: GATED = site never reached (kit `uses`=0);
  SHORT = `first` mode with the match within 10 landings (origin irrelevant); NO-COND = the
  pattern provides nothing but its own set; WRONG-ORIGIN = a necessary condition with >=4x
  fewer LANDINGS; BYTE-ONLY = >=4x by byte density but <4x by landings; else ORIGIN-OK.

## 1. Cell facts (stamps at main; origin; necessary conditions)

| cell | pattern, flags | stamps (REQ_BYTE / REQ_RUN / WHY / HANDOFF; PREFILTER; START) | origin S (prior ppm) | other necessary conditions and where they sit |
|---|---|---|---|---|
| dig | `[0-9]+x` | 120 / none / emitted / none; byte-class; reverse-pass | [0-9] (74 760) | `x`: END byte (variable offset from start; prior 997); `[0-9]x` end bigram (prior 75, indep.) |
| email | `[a-z]+@[a-z]+\.com` | 46 / `2e636f6d@0` / emitted / none; byte-class; reverse-pass | [a-z] (663 413) | `@` inner (665); `.` (9 969); run `.com` at the END (REQ_RUN, used as a presence gate); `[a-z]@[a-z]` inner trigram (293) |
| word-eq | `[A-Za-z_]+=` | 61 / none / emitted / none; byte-class; reverse-pass | A-Za-z_ (732 246) | `=`: END byte (3 323); `[A-Za-z_]=` end bigram (2 433) |
| hex-run | `[a-f0-9]+` | none / none / none / none; byte-class; landing | [0-9a-f] (284 434) | none: the pattern provides nothing but its own set (no boundary, no second byte) |
| bounded | `[a-z]+\b` (`--features all`) | none / none / none / none; byte-class-bounded; reverse-pass | [a-z] (663 413) | the \b's FAR side: next byte is \W or subject end (192 994); `[a-z]\W` run-exit bigram (128 035, indep.) |
| dfa-hat | `\b(?:true\|false\|null)\b` (`--features all`) | none / none / none / none; first-class-bounded; reverse-pass | {f,n,t} (119 624) | 2-byte prefix set `tr\|fa\|nu` at offset 0 (4 008, indep.); the whole words (4); no single byte common to all three alternatives |
| vm-hat | `[ab]+c` (`--engine=vm`) | 99 / none / emitted / none; VM_START_SCAN first-class | {a,b} (64 049) | `c`: END byte (18 442); `[ab]c` end bigram (1 181, indep.) |
| vm-hat-1 | `q[bc]+d` (`--engine=vm`) | 113 / none / emitted / none; first-class | {q} (665) | `d`: END byte (28 161); `q[bc]` START bigram, offsets 0-1 (19, indep.) |

Every REQ_BYTE above is stamped WHY "emitted" with HANDOFF "none": it is a PRESENCE gate (start
table, `where_to_start.md` §1.2: mapping PRESENCE), never a search origin. That is Frank's
word-eq observation, and it holds for dig, email, word-eq, vm-hat and vm-hat-1.

## 2. Measured densities on the subjects (b = byte ppm, L = landings; reached subjects)

| cell | subject | S: b / L | best condition: b / L | b ratio | L ratio |
|---|---|---|---|---|---|
| dig | digits64k | 834 442 / 9 057 | `x` 84 290 / 5 051; `[0-9]x` 70 236 / 4 603 | 9.9-11.9 | 1.8-2.0 |
| dig | mix64k | 454 071 / 16 193 | `[0-9]x` 21 042 / 1 379 | 21.6 | 11.7 |
| word-eq | mix64k (only reached) | 319 794 / 14 208 | `=` 46 616 / 2 904; `[A-Za-z_]=` 14 328 / 939 | 6.9-22 | 4.9-15.1 |
| bounded | prose64k / prose1m | 846 222 / 10 079 (161 475) | `\W` 153 778 / 10 078 (161 474) | 5.5 | **1.0** |
| bounded | digits64k | 84 290 / 5 051 | `\W` 81 268 / 4 889; `[a-z]\W` 6 653 / 436 | 1.0 / 12.7 | 1.0 / 11.6 |
| bounded | mix64k | 273 804 / 13 005 | `\W` 226 135 / 11 448; `[a-z]\W` 61 127 / 4 006 | 1.2 / 4.5 | 1.1 / 3.2 |
| dfa-hat | prose64k / prose1m | 97 214 / 5 767 (97 797 / 92 796) | `tr\|fa\|nu` 2 960 / 194 (3 016 / 3 162) | 32.8 | 29.7 / 29.3 |
| vm-hat | prose64k / prose1m / mix64k | 65 353 / 4 025; 65 229 / 64 096; 91 965 / 5 462 | `[ab]c` 1 907 / 125; 2 156 / 2 261; 3 845 / 252 | 34 / 30 / 24 | 32 / 28 / 22 |
| vm-hat-1 | prose64k / prose1m / mix64k | 33 707 / 2 144; 32 539 / 33 013; 46 112 / 2 891 | `q[bc]` 2 151 / 141; 2 047 / 2 146; 4 745 / 311 | 16 / 16 / 9.7 | 15 / 15 / 9.3 |
| hex-run | all | 75 k-834 k | none | - | - |
| email | all | - | `.com` 0 on every subject (the REQ_RUN gate rejects: S never scanned) | - | GATED |

PRIOR vs MEASURED (the brief asked which): the prior ranks every cell's best condition as rarer
than S except bounded's `\W` (192 994 vs 663 413, 3.4x; bigram 5.2x) and vm-hat's `c` (3.5x).
vm-hat-1 disagrees outright: prior puts `q` at 665 ppm (rarer than `d`, 28 161: ORIGIN-OK on the
prior) while the subjects hold `q` at 32-46k ppm, level with `d` (the subjects plant q). The prior
is unigram, so it cannot see the bigram conditions at all.

## 3. Per-cell verdicts (REGRESSION loss ns, OFF layer; rows = regress rows)

| cell | rows regress | loss ns | verdict | tactic that would use the better condition | pcrec has it? |
|---|---|---|---|---|---|
| dig | 2 `first`, 0 reached `all` (digits64k all is NULL/REGRESSION replicate) | +13 | ORIGIN-OK: the match is within 7-8 landings of the start; the kit's fixed per-use cost (+0.8 ns). mix64k `all` is WRONG-ORIGIN by landings (11.7x) but WINS (-30 030 ns) | end-landmark / reverse-inner from `x` | parked ([ENG-TACTICS], rev-inner HELD) |
| email | 6 regress (all `uses`=0) | +34 | GATED: `.com` REQ_RUN rejects every subject before the site runs; the +0.2..+33 ns are a codegen side effect of the changed function, not the form | n/a | gate already ships |
| word-eq | 2 reached (mix64k) + 3 unreached | +18 372 (reached) + 2 | reached: **WRONG-ORIGIN** (S lands 14 208 times, `=` 2 904, `[A-Za-z_]=` 939). 16 of 20 rows are GATED (no `=` in the subject): Frank's example is real on the one subject that contains `=` | end-landmark / reverse-inner from `=` | no (parked) |
| hex-run | 9 regress | +49 400 (incl. dfa-hat short, bounded `first`) | ORIGIN-OK / NO-COND: nothing but its own set; loss is the kit's per-use cost (+2.2..2.7 ns/use cold) | none exists | - |
| bounded | 10 regress: 4 `all` byte-only, 2 digits64k WRONG, 4 `first` SHORT | +657 770 (4 `all` rows; `first` rows +2..+5 each) | **BYTE-ONLY**: on prose the \W side is 5.5x rarer by bytes but 1.0x by landings (one word, one landing, either side). On digits64k only the BIGRAM `[a-z]\W` is rarer (11.6x landings) -> WRONG-ORIGIN (2 rows, +3 226) | boundary far side; digits64k needs a bigram/window scan | boundary side no; bigram: no kit-facing fact for it (pcrec facts `kset_walk` are offset-bytes, not run-exit) |
| dfa-hat | 4 regress (prose) | +478 961 | **WRONG-ORIGIN**: S lands 5 767 / 92 796, `tr\|fa\|nu` 194 / 3 162 (~30x) | multi-literal / per-alternative prefix set ([OPT-A] "multi-literal", FILED, not started); \b-preceded | **no** |
| vm-hat | 1 regress (prose1m all) | +33 470 | WRONG-ORIGIN by landings (28x) on every reached subject, but 7 of 8 reached rows WIN: a VM-hat use costs ~0 (r17loss a_VM = -0.1), so origin density does not translate into loss here | end-landmark `c` (a presence gate today) / reverse-inner | parked |
| vm-hat-1 | 0 regress | 0 (16 WIN) | WRONG-ORIGIN by landings (9-15x via `q[bc]`) but all reached rows WIN. Control: wrong origin without loss | pair scan on offsets 0-1 (`kset_walk` already holds `(0,{q}),(1,{b,c})`) | `offset-set` exists for fixed-offset bytes; the class pair at offset 1 is not rarer than q by single byte |

## 4. Counts and shares

Total OFF-layer REGRESSION loss on the table: 1 241 235 ns over 42 rows (of 80 OFF rows; ON replicates agree
on direction except the bimodal 64K find-all rows r17loss §3.4 names).

| class | rows | loss ns | share of loss |
|---|---|---|---|
| WRONG-ORIGIN | 9 | 534 028 | 43.0% |
| BYTE-ONLY (byte density says wrong, landings say OK) | 4 | 657 770 | 53.0% |
| ORIGIN-OK (hex-run 9, dig 2, dfa-hat short 2, bounded `first` 4) | 17 | 49 400 | 4.0% |
| GATED (site not reached; side effect) | 12 | 36 | ~0% |

By tactic (WRONG-ORIGIN only): multi-literal prefix set (dfa-hat prose, 4 rows) 478 961 ns = 38.6% of
total; end-landmark / reverse-inner (word-eq mix64k 2 rows 18 372; vm-hat prose1m 1 row 33 470) 51 842 =
4.2%; bigram / run-exit window (bounded digits64k, 2 rows) 3 226 = 0.3%.

READ THESE SHARES WITH THREE CAVEATS. (1) ns shares are dominated by the 1 MB subject: excluding
prose1m, the same classes are WRONG 34 159 (6 rows), BYTE-ONLY 58 503 (3), NO-COND 48 247 (3), SHORT 33,
GATED 3, so the wrong-origin share by ns on the 64K subjects is 24%, and bounded + hex-run's fixed
per-use cost is the larger share. (2) The BYTE-ONLY class IS Frank's `[a-z]+\b` example: by the
landings measure the \W side is not a better origin (it lands once per word too), and the kit's
r17loss §3.2 already shows the loss is a fixed +3.7..3.9 ns per use at skip 0. Whether a \W-origin
scan would still cost less per landing than the [a-z] scan is a kit-side timing question this lane
did not measure. (3) The wrong-origin cells that WIN (vm-hat, vm-hat-1: 24 reached rows, 22 WIN)
show origin density predicts loss only where the per-use cost is positive (PF/DFA sites,
+1.1..2.1 ns), which is why the same ~30x ratio costs dfa-hat 479 µs and vm-hat 0.

Answer to the question, in one line: of the 1.24 ms of loss, ~43% is wrong origin (all of it needing
a tactic pcrec lacks or has parked), ~53% is the bounded cell whose "better" condition is only better
per byte, ~4% is kit-side cost with no better condition, and the 12 unreached rows are noise.

## 5. Tactics needed that pcrec does not have

- Per-alternative prefix literal set (dfa-hat): [OPT-A] multi-literal, filed, not started. Biggest single item.
- End-landmark with an unbounded-prefix reverse walk (dig, word-eq, vm-hat): rev-inner / [ENG-TACTICS],
  PARKED. Soundness precondition is satisfied in these cells (the prefix class cannot consume the
  landmark: `[0-9]` vs `x`, `[A-Za-z_]` vs `=`, `[ab]` vs `c`), unlike `\S+@\S+`.
- Run-exit bigram / class-pair scan (bounded digits64k, vm-hat-1): no start-table row; a kit-side
  window need (D161), the fact pcrec could state is the pair, not a byte.
- Boundary-far-side scan (bounded prose): exists as an idea ([FIND-BOUNDARY-SIDE]); the data here
  says it does not reduce landings on prose.

## 6. Family: which plan rows each wrong-origin cell belongs to

- dfa-hat -> [OPT-A] (multi-literal) and [START-DENSE] (the DFA-hat route: dense start set, 97k ppm,
  11% cache-served); [PRIOR-COST-UNIFY] for the admission.
- word-eq (mix64k), dig (mix64k), vm-hat -> [ENG-TACTICS] rev-inner (parked), with
  `where_to_start.md` §1.4's admission "landmark >= F x rarer than the offset-0 row": the ratios
  here are 5x-30x, over every F the census tried (1, 2, 8).
- bounded -> [FIND-BOUNDARY-SIDE] (byte-only; digits64k bigram case only), plus [START-DENSE].
- vm-hat-1 -> [ENG-TACTICS]/[OPT-K] pair-scan territory; no loss, control only.
- [REPEAT-RUN]: NO cell. No pattern in the table has an exact repeat `X{n}`; nothing here bears on it.
- hex-run, email: no wrong-origin cell (hex-run is a pure kit per-use cost; email is gated).

## Files

- `docs/dev/lanes/origsurvey/survey.py` (densities, landings, per-row verdicts; pure, no clock),
  `time.log`, `counts.txt` (copies of the kit's inputs, so the script reproduces).
