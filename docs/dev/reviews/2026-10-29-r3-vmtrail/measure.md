# CRITIC measure — vmtrail

Lens: measurement regime, independent control, population (K35), what moves, and
internal consistency of the three documents (trailgen = TG, vmbc = VB, altd = AD).
Probes: my own scripts under measure/ (pop.py..pop4.py) read the bench store
(index.tsv, newest `pcrec_*_auto-caps-simdna` record per subbench) and bench/*/patterns.
All arithmetic below was recomputed from the documents' own tables.

## Findings

### MEASURE-1 The end state of the build sequence was never measured; "R and D compound, do not overlap" contradicts TG's own mechanism
- status: CONFIRMED (the gap) / SUSPECTED (the overlap)
- severity: design
- effort: M      blast radius: the sequencing claims and the goal numbers in all three docs
- where: TG "Interaction with B+C and D" bullets 2-3; AD twin modes (`BCd_*` only); TG twin modes (no D); VB (no U, no D, no R)
- claim: Every twin is built on lane/trailgc plus AT MOST two of {R, B, C, U, D}. AD's D twins are `BCd_A/AL/ALkf` (no R, no U). TG's R/U twins have no D. No document measures R+U+B+C+D, which is the thing the build sequence ships. AD's headline ratios (nest-paren x0.52, nest-brace x0.25) and TG's headline (idents 79.6 M "below jit") belong to different stacks, so the "final" gap-to-jit table does not exist anywhere.
- evidence / repro: TG line 409-411 says D "cuts pushes per byte... R cuts the cost per push. They compound and do not overlap", while TG lines 278-279 and 258 say R's measured gain "is mostly that loop (the restore/unwind) and the push path". AD table: nest-paren and nest-brace go to 0 pushes per byte under `ALkf` (AD "Pushes per subject byte"). With 0 pushes the push/fail path R speeds up is not executed on those two subjects, which are exactly where R's largest gains are (R on B+C: nest-brace -20.1 %, nest-paren -19.6 %, recomputed from TG's table 72.72/91.02 and 20.12/25.04). So the overlap is likely and the additive expectation is untested. To confirm: one twin B+C+D+R (+U) on cscan, rate.sh instructions.
- proposal: Add a STEP 0c "full-stack twin" card (all five on cscan and JSON) to the build plan, and state the final gap table from it. Until then, drop "compound and do not overlap" or qualify it as untested.

### MEASURE-2 "General VM win" (-21.7 % summed instructions) is the backreference family; the headline is sum-weighted
- status: CONFIRMED
- severity: design
- effort: S      blast radius: TG Summary, Premise test "Frank's bet holds", Question 1
- where: TG Summary bullet 2, Census table, Totals table
- claim: Of 46 census artifacts, 21 write no trail on their subject and 25 do. Of those 25, the only rows with an all-twin effect of 10 % or more are bak-2, phone-palindrome-6, bak-1, bak-py, bak-g-rel and mod-j-uc: six artifacts (13 % of 46). I read the pattern files: `(\w)(\w)\2\1`, `(\d)(\d)(\d)\3\2\1`, `(\w+) \1`, `(?P<t>\w+) (?P=t)`, `(\w+) \g{-1}`, `(?J)(?:(?<w>the)|(?<w>\w+)) \k<w>` - every one is a backreference pattern. The capture-bearing non-backreference rows (grok, subst, lookaround) are -0.6 % to -4.0 %. The median change over the 46 artifacts is 0 %. The 21.7 % is an instruction SUM over heterogeneous subjects (each pattern's largest bench subject, sizes differ by orders of magnitude, per-artifact instructions are not printed), so it is weighted by whichever subjects are biggest.
- evidence: pattern files `/home/pcrec/projects/pcrec-bench/bench/{syntax,capability}/patterns/{bak-2,bak-1,bak-py,bak-g-rel,mod-j-uc,phone-palindrome-6}.rx`; table rows in TG lines 125-137.
- proposal: Restate the finding as "UNDO-DEAD removes the trail cost of backreference-reading patterns, where the captures are live but their old values are dead" and print per-artifact instructions plus the unweighted median. The decision (build U) may well stand on the 63 % / 47 % rows, but the "general" framing and the 87.8 % entries figure should say whom it is for.

### MEASURE-3 The sample leaves out the most relevant members; population is stale-routed
- status: CONFIRMED (sample membership, reproduced) / SUSPECTED (effect)
- severity: design
- effort: S
- where: TG Census "Method", Skipped
- claim: I reproduced the declared rule (79 distinct VM texts from the newest auto-caps records, 5 subst forced, the other 74 ordered by sha256 of the text, first 45): 5 recursive patterns are in the sample (nested-comment-rec, rec-back, rec-g-angle, rec-1, rec-py), and the 29 not sampled include `balanced-parens-rec`, `bracket-array-define`, `rec-name`, `rec-fwd`, `doubled-word` (backreference), `quoted-delim-match` (backreference), `trim-nested-star` `^(\s+)*$` and `numeric-id-nested-plus` `^(\d+)+$` (the backtracking-heavy shapes where the trail matters most), `bak-k-named`, `grp-callout`, and the large bounded `.{0,256}` pairs. The two recursive bench members closest to the cscan/JSON gap subjects, and two of three backreference patterns that U would help, are unmeasured. The population itself comes from records made by pcrec pins 6b2dbd3e / 9ae59f5d4 / 614d45eb3 (store/index.tsv), not the lane/trailgc pin: TG already found 3 `bounded/cls-*` flip to DFA, so the same staleness hides patterns that are VM at this pin but DFA in the record (they cannot be in the population). The census totals "flat 41 / recursive 5" therefore describe a 61 % hash sample of a stale list.
- evidence: pop4.py output in measure/ (sampled rec list, notsampled list); `grep -c` shows the bench store's VM set is 86 rows (reproduces TG's "86 VM rows") from `engine_metadata.engine == "vm"`.
- proposal: Make the 29 unsampled (TG already lists them as STEP 0) part of the gate before "flat -21.7 %" is quoted, and re-derive engine membership by emitting at the lane/trailgc pin, not from records. Note `utf8/` patterns ran as byte patterns and are labelled `utf8/` in the table anyway (asr-lb-varwidth row, -6.8 %): relabel or drop. (I count 2 utf8 patterns inside the first 45, not the 3 TG states; SUSPECTED, hash input may differ.)

### MEASURE-4 R's quoted range is wrong against its own table; R's "gap subjects" are two patterns
- status: CONFIRMED
- severity: doc
- effort: S
- where: TG Summary ("on top of B+C: another -8 % to -20 %"), Structure review row 2 ("-8 to -20 % on B+C"), Question 2
- claim: Recomputing B+C -> B+C+R instructions from TG's gap table: idents 79.63/91.73 = -13.2 %, nest-brace -20.1 %, splice -8.1 %, js -10.5 %, nest-paren -19.6 %, comment-5m 132.97/133.47 = **-0.4 %**. The stated floor of -8 % is false for comment-5m. Also B+C+U+R (129.97) is WORSE than B+C+U (128.47) on comment-5m. Stock-vs-R range (-8.1 % to -18.2 %, cycles -14.8 % to -33 %) does recompute. Separately: five of the six "gap subjects" (idents, splice, comment, nest-brace, nest-paren) are subjects of the one cscan artifact, the sixth is JSON (TG line 62-64 says idents/splice/comment run the cscan pattern, VB Premise table); so R's -8..-18 % is n = 2 emitted matchers. The census (46 artifacts, default arm) shows R at +0.2 % flat, and VB/TG both state it only fires when the matcher is not inlined.
- proposal: Correct the range to "-0.4 % to -20 %", say "two matchers", and give the number of bench/corpus VM artifacts whose matcher is a separate function (that is R's real population; neither document counts it).

### MEASURE-5 The "independent checker" is independent in code only; its refusal mode and its reference text are unspecified
- status: CONFIRMED (gaps) / SUSPECTED (consequences)
- severity: design
- effort: M      blast radius: all three Standing-question-2 sections; the build's check
- where: TG standing Q2 bullet 2 and Build plan stage 1; VB standing Q2 bullet 2; AD standing Q2 bullet 1
- claim: Each doc says its text-reading prototype (`vmopt_tg.py`, `vmopt.py`, `altd.py`) "shares no source with a future emitter analysis" and becomes the build's independent checker. Four problems against learnings.md section 3:
  1. Same model, different code. The prototype and the build implement the same declared rule table (VB rows 1-11, TG verdict rows 1-5, AD rows 1-13) written by the same author family. A modelling error (a missing edge, an unsound row such as AD row 6 "trailed or undone", MAYFRAMES' CUT approximation) is replicated; only implementation slips are caught. The truly independent controls are the stock-vs-twin answers and the oracle `.rxt` expectations, which the docs also have. The checker should be described as a second implementation, not an independent control.
  2. Refusal is a vacuous pass. Each prototype "refuses" anything unrecognised (VB row 11, AD row 13, "a file it cannot parse is refused", VB "the twin refused the 11 callout artifacts"). A checker that refuses an artifact that the build optimised produces no verdict - the empty-vs-empty failure mode of section 3. None of the three says the build must decline exactly where the checker declines, or that a checker refusal on an optimised artifact fails the gate.
  3. The checker goes dark when the next doc lands. After D, B+C artifacts contain AD's `switch` dispatch; `vmopt.py` row 11 refuses it (AD: "whichever lands second adds the dispatch's row"). The wired-check/removal-caught-check split of section 3: both components honest, the composition blind.
  4. What does it compare against? "every kept restore set equals its own" (VB) and "must be justified by the text analysis" (TG) need the stock (unoptimised) text of the same artifact. Only AD names a deny flag (`-fno-first-byte-dispatch`, AD line 195); TG and VB name none (grep `deny|-fno-|test-axes` over the three: only AD). Without a per-pass deny flag there is neither the stock text for the checker nor the byte-identity A/B control `make test-axes` expects (CLAUDE.md "answer-identical to default over the whole corpus").
- proposal: (a) Give R, the verdict pass (U/B) and C each a deny flag named per D174, in the build plan. (b) State the checker's refusal rule: build declines iff checker declines, and a counted "checker-refused optimised artifact" is a gate failure. (c) Re-describe the checker as "second implementation" and keep the answer comparison as the independent control.

### MEASURE-6 Identity evidence: cells are counted per twin, cover two patterns, and ~1,000 cells have no reference; U is thinnest
- status: CONFIRMED (counting) / SUSPECTED (gap)
- severity: design
- effort: S
- where: TG "Identity"; VB "Answer identity"; AD "Answer identity"
- claim: "5,460 cells" (VB for B/C/BC, TG for R/P/RP), "7,280 cells" (AD) are 99+161 = 260 subjects x 7 capacity settings = 1,820 base cells, multiplied by 3 (or 4) twin modes: 1,820 x 3 = 5,460; 1,820 x 4 = 7,280. Both are the same two patterns (cscan, JSON). They are quoted as if independent evidence. For R specifically (a change to EVERY VM matcher's prologue and exits) the only identity evidence is these two patterns, the 46 census artifacts on one subject each, and 16 trap patterns (492 cells). The twin answers 484-747 (TG), 498/484 (VB), 510/496 (AD) cells where stock gives up; in those cells there is no stock answer, and none of the docs says they were compared with libpcre2 or an unlimited stock run - they are the cells where a wrong twin is least visible. U is the change in R25 E5's failure class (an untrailed write) and has the least corpus evidence: no harness run at all (STEP 0b not run), one subject per census artifact.
- proposal: Report cells as subjects x settings, per mode; check the twin-answers-where-stock-gave-up cells against libpcre2 (installed, 10.46) or stock with a large cap; run U through the same 9-file `tests/recursion` harness VB used for B+C (50 compiles) before the design is approved rather than at build STEP 0b.

### MEASURE-7 Sabotage rows are mostly lists of witnesses, not run sabotages; the reach of B, COPY, C and D is unproved
- status: CONFIRMED
- severity: design
- effort: M
- where: VB standing Q2 "Sabotage witnesses to carry into the build"; AD "Sabotage witnesses to carry"; TG "Controls, run here"
- claim: Only TG ran sabotages (two, on U: entry liveness dropped, MAYFRAMES dropped; both detected, with a 1,020-subject sweep for the second: 610 differ vs 0 for the correct twin, which recomputes: sum 2^n for n=2..9 = 1,020). VB lists six witness patterns and AD ten, but neither ran a sabotaged twin showing the witness changes the answer: i.e. no proof the witness reaches the site ([MECH-REACH]) for DEAD, COPY, C's keep-set narrowing, the push edge, CUT-opacity (AD found it by accident in the harness, 97/6 before the fix - that one row is real evidence), the lookbehind/backreference OPAQUE rows, the callout row, caseless/UTF-8 lead bytes, end-of-subject. AD's list has no mapping sabotage -> witness -> site. VB's own text records that trap 2 of C over-keeps rather than being unsound, so its only listed C-sabotage is a REACH witness, not a soundness one. TG's R sabotages (drop `steps_left` write-back, skip reload after compaction) are planned, not run.
- proposal: Make each doc's sabotage table (rule row -> sabotage -> witness -> expected delta), and run the cheap ones at design stage on the existing prototypes (a one-line sabotage flag per row, as TG did with TG_SAB_ENTRY).

### MEASURE-8 Rule (iii) "identical" is not in VB's tables, and VB's B vs Bd columns show (iii) moving counts by up to 2.2 %
- status: CONFIRMED
- severity: doc
- effort: S
- where: VB Summary ("B+C... identical"), "Rule (iii)" section, instructions table; TG Structure review row 6 ("runtime twin of vmbc's rule (iii), measured at zero on top of B+C")
- claim: VB says B+C with (iii) and without give identical instructions on all six subjects. The instructions table has columns Bd (no iii), B (iii), BCd (no iii) but NO `BC` (with iii) column, so the claim cannot be checked from the report. Where both Bd and B exist they differ: idents 88.63 vs 90.02 (+1.6 %, the "untrailing" variant ADDS instructions), js 209.09 vs 204.50 (-2.2 %), nest-brace 126.02 vs 124.62, splice 19.42 vs 19.76, comment 134.47 vs 133.47. An untrail rewrite adding instructions suggests the rewrite itself perturbs code layout/checkpoints at the 1-2 % level - the noise floor of the twin method, which is the same size as many of TG's U-on-top rows (+1.6 % lka-pos). TG row 6 then relabels this STATIC measurement as the result of a RUNTIME epoch twin ("runtime twin of rule (iii), measured at zero") - no epoch twin appears in TG's cards or tables.
- proposal: Print the BC (with iii) row, state the twin method's layout noise floor once, and either run the epoch twin or change TG row 6's wording to "argued, not measured".

### MEASURE-9 Regime: cycle goals rest on a loaded box and cross-load mixing; "below pcre2-jit" is an instruction statement
- status: CONFIRMED (inconsistencies) / SUSPECTED (compiler/arm)
- severity: doc
- effort: S
- where: VB Goals 2-3 and Standing Q1; TG Summary bullet 4, cycles tables; AD Summary table and Standing Q1
- claim:
  1. Goals are stated as cycle ratios to jit (VB x1.21/x0.80/x1.89/x1.40; AD x0.52/x0.25/x0.89) but the cycles were taken at load 3.2-3.5 (VB), 6.6-6.9 (TG), 6.8-7.0 yet 5.6-9.8 in AD's own method paragraph (AD contradicts itself), with a kit heavy job on a 16-thread box and no per-core occupancy or pinning stated (learnings section 1). The bench would gate such runs out (the bench record environment block shows its quiet gate: load limit 2.0 and a per-core occupancy field).
  2. Mixed loads in one ratio: TG's B+C+R cycles (load 6.6-6.9) are compared to "jit (vmbc, load 3.5)".
  3. TG says idents B+C+R at 79.6 M is "below pcre2-jit's 82.1 M". In cycles it is 20.50 vs jit 18.30 = x1.12 (TG's own table; IPC 3.9 vs 4.5). Instructions are the decision currency, but the sentence reads as parity in time.
  4. Suspicious equality across loads: TG's B+C cycles for comment-5m (27.28) and splice-1m (3.71) are identical to four digits with VB's BCd cycles measured at half the load, while idents differs by 10 % (24.34 vs 22.11). If these were copied from VB the "min of 5 at load 6.6-6.9" caption is wrong for those cells.
  5. Compiler/arm: gcc 15.2 -O2 only; R's gain is an aliasing effect that depends on the optimiser (TG's own account) and on the matcher not being inlined; the gap numbers are the `_in` arm (NF=4M, NT=64M) while the census uses the default arm. Whether R survives -O3 or the default arm (3,072-entry stack run struct) on cscan is not measured. The bench has cf-o3 / cc-clang testee variants in store/index.tsv, so the regimes exist.
- proposal: Re-take the cycle columns once under the bench's quiet gate (or drop cycle-ratio goals), fix AD's load statement, re-label TG's "below jit", and add one R twin at -O3 and in the default arm to the STEP 0 card.

### MEASURE-10 Two matchers' worth of evidence per prototype and a shared refusal class
- status: SUSPECTED
- severity: design
- effort: S
- where: TG "Not done"/Skipped (R, 2 artifacts with `<prefix>__match_notempty`), AD Population (3 of 16 refused "two VM bodies in one file"; 9 of 60 refused in harness sample 2), VB "refused 11 callout artifacts"
- claim: All three prototypes decline the same shape - an artifact with a second matcher body - and the callout shape. AD's refusal rate is 3/16 (19 %) and 9/60 (15 %). A pass that is "answer-identical over everything the prototype could read" has zero evidence on the declined shape, yet the build must handle it (R: "every matcher function"). TG also sums the R and B+C+U+R columns over a set that excludes the 2 R-unbuildable artifacts (its flat R of +0.2 % and B+C+U+R of -20.8 % are against B+C+U -21.7 %: R "costs" +0.9 points after U but only +0.2 % alone, which only reconciles if the columns are not over one artifact set).
- proposal: Count the refused shape in the build's STEP 0 as a first-class category; print totals over the common artifact set; state the build's behaviour on the declined shape.

### MEASURE-11 U (untrailed writes) and D's "slot write is undone on failure" are inconsistent when both land
- status: SUSPECTED
- severity: answer (if both land and AD's rule 6 is implemented as written)
- effort: S
- where: AD FIRST+ row 6 ("slot write... trailed or undone on the failure path, so not an effect") and Soundness "Captures"; TG row 4 (SETU, no entry)
- claim: AD's proof that dropping a continuation is invisible relies on writes before the first consumed byte being trailed and undone by the unwind. Under TG's UNTRAIL verdict some of those writes are plain stores that the unwind does NOT undo; soundness then rests on TG's argument that the slot is dead at the resume labels, which was computed on the stock graph. D's twin was built on `BCd` only, so the combination was never run; TG says only "D can only widen U" and "whichever lands second adds the row". The two soundness proofs are each correct alone; their composition is asserted.
- what would confirm: a B+C+U+D twin on the sabotage witnesses `(a|ab)(c|bcd)(d*)` on abcd and `^(?(DEFINE)(?<g>a|ab))(?>(?&g))c$` on abc with SETU lines present in the dropped arm.
- proposal: Add the combined twin to STEP 0c (MEASURE-1) and restate AD row 6 as "a write is non-effect only if trailed OR dead at every resume reachable".

### MEASURE-12 What moves: the bench null band and the stamped capacities of 63 of 86 VM bench artifacts
- status: CONFIRMED (readers exist) / SUSPECTED (severity)
- severity: maintenance
- effort: S
- where: TG standing Q3 ("every VM artifact's prologue and macros (R)"); all three "one abi event with a mover census"
- claim: The three lists of readers (spec hunks, identity gate, movers.py) omit the bench's program-identity machinery. Bench records carry `engine_metadata.program_sha256`, normalised to drop comments, the ABI block and unreferenced defines but NOT code (pcrec-bench/docs/design/null_band_v1.md, BD13); the trend report and the null band read it. R changes the matcher text of every VM artifact, so the identical-program population the band uses as noise control for VM cells becomes empty at that pin - the abi-32 precedent in null_band_v1.md ("read all 373 compiled capability rows changed -- an EMPTY band"). Also `rx_info.trail_frames` / `resume_frames` stamps are caller-visible and are in the bench record: in the newest records 63 of 86 VM artifacts carry small statically bounded `trail_frames` (the other 23 are the 3,072 default), so U's re-sizing (TG standing Q3, "the stamped trail capacities") changes `rx_info` for about three quarters of the VM population (D80 spec hunk).
- evidence: `/home/pcrec/projects/pcrec-bench/docs/design/null_band_v1.md` lines 85-105; pop2.py output (Counter of trail_frames: 3072 x23, 3 x23, 4 x10, 2 x9, 13 x7, 1 x6...).
- proposal: Add the bench null band / `program_sha256` pin and the `trail_frames` stamp class to the mover-census reader list; decide whether R lands alone and early (then the VM null band is spent once) or with the stages (once).

### MEASURE-13 Small internal inconsistencies
- status: CONFIRMED
- severity: doc
- where / claim:
  - TG Summary "B removes 0.4 % of trail entries": no table contains B-only trail entries (the entries table is stock -> B+C+U).
  - TG Premise "B's DEAD rule fires on 7 of 46 artifacts (38 of 276 SET sites), and mostly on the rec-* family": the census table's B-dead column sums to 16 sites (4 + 9 + 3), 12 of them rec-*; the other 22 are on artifacts not shown.
  - AD Standing Q1 "cycles under load 6.8-7.0" vs AD Method "load was 5.6-9.8".
  - VB summary table header says "B" and "B+C" but the "B" column is the (iii) variant (90.02) while the text cites 88.6 for DEAD+COPY; the summary "B" for idents (90.02) is therefore not B-without-iii.
- proposal: fix when the notes are next revised.

## PROBED-AND-HELD
- Shared numbers across documents - held; stock, B+C and jit instruction counts for all six gap subjects are identical in VB, TG and AD tables (idents 191.67/91.73/82.09, nest-brace 162.72/91.02/50.40, splice 47.76/20.42/23.66, js 260.71/72.63/58.58, nest-paren 31.07/25.04/10.35, comment 220.97/133.47/86.50).
- VB cycle ratios to jit - held; all 12 recomputed (x3.00 -> x1.21, x5.33 -> x1.89, x2.79 -> x0.80, x5.73 -> x1.40, x5.70 -> x3.56, x2.45 -> x1.52).
- AD cycle ratios and D percentages - held; ratios x0.52/x0.25/x0.89/x0.70/x0.73/x1.15 and B+C-was values recompute from its cycles table; "81 % of the B+C program" (25.04 -> 4.72), idents +11 % / splice +19 % for rule-all recompute.
- VB B-alone / C-alone / B+C percentages (js -22 / -37 / -72; nest-brace -23 / -15 / -44) - held.
- TG R stock ranges (-8.1 % to -18.2 % instructions, -14.8 % to -33 % cycles) and "U on gap subjects 0 to -3.7 %" - held.
- TG totals: 16,094,053 -> 1,960,073 = -87.8 % entries; 41 + 5 = 46 = 50 - 4 skipped; 25 trail-writing = 21 + 4 (row count of the table); 1,020 = sum 2^n, n = 2..9.
- Cell arithmetic: 5,460 = 3 x 1,820; 7,280 = 4 x 1,820; 2,079/3,381 = 99/161 x 7 x 3 - held (this is the basis of MEASURE-6, the numbers themselves are right).
- Depth arithmetic - held; 2048 frames / 4 per level = 511, / 7 per level = 291, ~5 per level = 408, 1 per level = 2046.
- Bench population claims - held; 86 VM rows reproduced from the newest auto-caps record per subbench (capability 33, syntax 27, bounded 10, subst 5, sentinel 4, utf8 4, litrun 2, loglines 1); 79 distinct texts (74 found + 5 subst); the sha256-order sample reproduces TG's "5 recursive of 46" and its 29 unsampled; `unusual/` has 25 patterns and no store record (TG claim true).
- Gap-subject sample identity (484-747 / 498 / 510 give-up-cell counts) - held as stated; the problem is MEASURE-6's missing reference, not the counts.
- P (packed entry) numbers cross-document (js page faults 82.9 k -> 48.5 k stock, 15.7 k -> 14.8 k after B+C, VB 82,907 -> 15,666) - held.
