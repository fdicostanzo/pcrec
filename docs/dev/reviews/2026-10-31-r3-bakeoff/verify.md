# VERIFY: critic round bakeoff (pricing_bakeoff.md @ a7b229f3f)

Review tree: /home/pcrec/projects/pcrec/worktrees/crit-bakeoff (main a3cc4de82). All compiles single, `gnutimeout 30 nice`, outputs under verify/w/.

## V-1

PREMISE-1, SIM-1: L-ROW by name lands unsound or contract-moving rows.
- Verdict: HOLDS (RETRY part fully; NEXT bounded/unbounded part holds on the predicates, the consequence is read from comments, not demonstrated by a miscompile because L-ROW does not exist).
- Re-ran: read `emit_dfa.c:10430-10447` and the rows at `:10449-10487`: `exact`, `clamped`, `retry-anchored` have deny 0 and `.contract = CG_FIXED`; the comment says `exact` stays undeniable because a step "would carry [the window END] stale", and past `clamped` "a give-up can become an answer". The slot's fallback is `fixed` (last VM row, `:10484`; `cand_fallback` `:10739-10747` returns the last row routed on the route), so §3.1 step 1 ("every row that is not the slot's fallback") names `exact`/`clamped`/`retry-anchored`. `cand_select` (`:10721-10731`) simply `continue`s past a denied row, so denying `exact` lands `adaptive-dense`/`adaptive` (no deny bit set). Compiled `foobar\d --engine=vm -fprefilter` (verify/w/v1.c): `RX_ENGINE "vm"`, `RX_VM_PREFILTER "hybrid"`, `RX_VM_RESEED "exact"` (line 29). LOCATE rows at `:10285,10294,10300` also carry CG_FIXED.
- NEXT pairs: `pf_memchr_bounded_applies` = `forward && ONE_BYTE && views` (`:6599-6601`), `pf_memchr_applies` = `forward && ONE_BYTE` (`:6603-6604`): the unbounded predicate does not exclude `views`; both rows have deny 0 and no public flag, so only a by-name deny splits them. The `views` comment (`:4603-4605`) says every skip is then bounded at n-1. Same for byte-class pair. Today the unbounded row is unreachable on a views site only because the bounded row sits above it.
- Severity: "answer" is slightly high; "design" (the lever as specified is unsound; effect is a hard stop or a bad arm in the census, fixed by an allowlist) is more accurate. The fix is cheap.

## V-2

PREMISE-3, MEAS-1, COST-2 part 1: the bench's timed loop is REPEATED, not streamed.
- Verdict: HOLDS for the standard loop; PARTLY refuted on "no stream mode" (a `call-stream` regime exists, which both critics missed).
- Quotes: pcrec-bench `docs/methodology.md:74` "Each subject's iteration count is calibrated per engine toward a fixed timed-work target"; `:76` "times a loop of repeated calls to the same compiled matcher"; `docs/design/harness_contract.md:146-154` "for each subject runs `iters` iterations ... `iters` chosen so one subject's loop is >= 50 ms"; `testees/pcrec/timed.h:12-15` `struct timed_in { buf; len; iters; ...}` (one buffer, an iteration count). `grep -i stream|cursor|rotat` over timed.h, methodology.md, root CLAUDE.md finds no cursor/rotation mode for the ordinary regimes.
- Not found by the critics: bench record schema v1.11 has a `call-stream` regime (`docs/design/unusual_set_v1.md` §7, `gate_shape_v14.md` §3.8): ONE subject, a declared list of (offset, length, binding) calls, one iteration = one full replay of the list, replay count calibrated to >= 50 ms. It is designed for cscan/vars streams, not for the bake-off, and a replay still repeats the same call list; but a 64-window list (4 MiB) is a candidate vehicle and nobody asked. So the finding's remedy "ask the bench for a streamed mode" is right, and the premise "bench already does this" (§5.1) is unsupported for the ordinary regimes.
- regime_eval.md change-log item 1 (`:216-218`) confirms the repeated-64-KiB flattering effect that the design itself invokes.
- Severity: "answer" is right in direction (the design's own §1 says repeated flips decisions) but the gap is a question to the bench (B5 should name the loop and call-stream), so "design" fits unless the bench says no.

## V-3

PREMISE-5, SIM-5, MEAS-9: (a) is J yet sits in §9.3's candidate set.
- Verdict: HOLDS.
- Re-read: §2 line 172 "(a) is J in this simulation ... not a gap", §0 item 2 "scores as J by construction", F4 (line 873-875, asks if scoring (a) as J is acceptable) versus §9.3 line 767 "The options in rows 3-6 are ... A1, HY, Dx, MN, KF and (a)", row 5 "lower than every other's by at least delta". F4 acknowledges (a) cannot lose on picks but no row says what happens when (a) is the numeric best.
- Read `simulate/bin/verdict.py` before running: it encodes rows 0-7 in order, OPTS includes '(a)' set equal to J (matches line 767); row 2 = FM - J < delta; row 3 = model_err (r[J]) > 3 x max pairwise |placement-loss difference|; row 4 = max-min of the six options' per-site regret < delta on >= 95 % of sites; row 5 = one option at least delta below every other, then the 15-site floor. Faithful, with two stated simplifications (noise tests pass at |diff| >= delta; strata hold). One ambiguity: row 4 says "the priced options" while the script uses all six (MN and (a) included); that is the preamble's literal reading and does not change S3/S5.
- Ran it: S5 (J=(a) 2 %, A1/HY/Dx/KF 5 %, MN 8 %, FM 20 %) -> `row5 (a) WINS`. S3 -> `row7 INCONCLUSIVE`.
- My own variant (verify/w/vd2.py: (a) removed from the candidate list, otherwise the same code): S3 with Dx better on 12 sites -> row7 UNDERPOWERED anyway (12 < 15), so the critic's "expected: Dx wins" is not right at 12 sites; with Dx better on 20 sites -> `row5 Dx WINS` (with (a) in the set the same vector reads row 7, because Dx only equals (a)). S5 without (a) -> row 7 (A1/HY/Dx/KF tie at 5 %, none is delta below the others; also SIM-6's missing top-group row).
- Severity: "answer" is right for SIM-5/MEAS-9: (a) can be crowned "on numbers", and any option that equals J can never win row 5. SIM-5's S3 example overstates, as shown.

## V-4

PREMISE-6, SIM-9: MARGIN kept in A1/HY/KF/MN but not stated for Dx/J; placement loss can be negative; row 2 can stop while MN beats FM by more than delta.
- Verdict: HOLDS (MARGIN-asymmetry part PARTLY: the text is ambiguous, not contradictory).
- `memfn/src/window.c:669-684`: MARGIN "a RESEED alternative wins only at less than HALF the least-cost PARKED one" (`l < r` with MATERIAL_NUM/DEN), a bias toward PARKED, as quoted. Design: §2 table says "MARGIN kept" for A1, A1u (as A1), KF (as A1), MN (Table A as shipped), HY via A1 shape; Dx/Dp rows ("returns every option", "backend takes the argmin") and J ("full sum of all terms") do not mention it; K4 (line 918) says "MARGIN 2/1 stays in every kit-level rule as shipped", which could be read to include Dx's kit level. So whether A1 and Dx differ by MARGIN is not stated; where they do, "placement loss" includes a guard, as PREMISE-6 says.
- Arithmetic (SIM-9): per cell 1+r = (1+m)(1+p). Example t_O=1, t_J=2, t_A1=1: m = 100 %, p (A1 against J) = -50 %, r = 0, and 100 % + (-50 %) = 50 % != 0. Holds. §7.1 says "model error = J against O; placement loss = rule against J" without sign.
- Ran verdict.py S6 (FM 6 %, J/A1/HY/Dx/KF 4.5 %, MN 3 %): `row2 MODEL CANNOT BEAT FM`. The script's row 2 is FM - J < delta, which is row 2's text, so the row can stop while MN beats FM by 3 pp. It needs J to mis-price a term that MN's view avoids; §9.1 item 3 itself predicts J's model error is large, so not far-fetched.
- Severity: PREMISE-6 "answer" is high (the main contest A1 vs Dx is affected only if MARGIN bites on H; the fix is an on/off dimension); SIM-9 "design" is right.

## V-5

PREMISE-7, SIM-10, MEAS-5: C-BLIND vacuous without L-KIT, low reach with 2 draws.
- Verdict: HOLDS.
- Arithmetic: 1-(1-f)^2 = 0.0396 at f = 2 % (4 of 204), 0.0975 at f = 5 %, 0.19 at f = 10 %. A model blind on EVERY site (each site has f = 5 % of options beating the model's picks) is detected on 9.75 % of sites, under the 10 % stop bar.
- Text: §3.5 line 339-340 (the 2 random draws are per KIT site from L-KIT's dump); §8 line 736 (C-BLIND "above 10 % stops stage 4", planted failure "none (it is itself the probe); its reach is reported as the number of random arms timed", so reach is reported, never gated); §9.3 row 1 line 777 (reads "C-BLIND's rate ... at or below 10 %"); §10 closing paragraph and F7 (lines 827-829, 881-884: run without L-KIT, "do not wait"). Cross-path arms are all timed, not drawn, so with no L-KIT the random-draw population is empty: 0 of 0, and row 1's "<= 10 %" holds vacuously.
- Also checked §1 item 2: "every control in §8 has a planted failure that must turn it red" versus C-BLIND's "none": contradiction confirmed.
- Severity: "answer" right (row 1 ends the whole question as PRICING DOES NOT PAY).

## V-6

SIM-7, SIM-6, MEAS-8, MEAS-11: verdict-table power and ordering.
- Verdict: HOLDS (all four), one caveat on MEAS-8's "50 % at delta".
- Script check first: verdict.py encodes rows as written (see V-3). Ran S1, S1b, S2 (outputs above): S1 (priced options identical at 4 %, MN 7 %, FM 10 %, the §9.1 prediction) -> `row7 INCONCLUSIVE`; S1b (everything but FM at 4 %) -> `row3 UNRESOLVABLE (model err 0.040 > 3x 0.000)`; S2 (A1 loses 80 % on 5 of 110 sites, mean A1-Dx = 3.64 pp > delta) -> `row4 TIE (105/110 sites equivalent)`. Row 4's 95 % of 110 is 104.5, so 105 passes. Row 3 fires on any nonzero model error once the options agree because its right side is 3 x (largest paired placement-loss difference) = 0; that is a mislabel for "the options are the same" and sits before row 4. The only caveat on S1: it depends on reading "the priced options" in row 4 as all six candidates incl. MN (the literal preamble, line 767); with a narrower set S1 would reach row 4.
- Power floor arithmetic: 15/110 = 13.6 % > the 5 % disagreement §9.1 item 2 predicts for A1/HY/Dx, so those pairs are UNDERPOWERED by construction unless they differ on >= 15 sites; 0.02 x 110 / 15 = 14.7 % net gain per differing site to reach delta. Stage-0 floor: 60 H sites -> H-open 60 x 2/3 = 40; 15/40 = 37.5 %; 0.02 x 40 / 15 = 5.3 %. All three re-done and match.
- Unreachable region (MEAS-8): 10 % worse on 9 % of 220 sites = 20 differing sites (>= 15, so powered): row 4 fails (91 % < 95 %), row 5 fails (mean 0.9 pp < 2 pp), so the catch-all row 7 prints INCONCLUSIVE "more sites", which cannot help. Row 7's own label says "(UNDERPOWERED comparisons)", so the label and the catch-all disagree. Holds.
- Ran `measurement/sims/row5.py` after reading it (it simulates row 5's point test mean >= delta plus a site-bootstrap CI, n = 110, k differing sites; it does not apply the 15-site floor, so its k = 10 line is outside what the design would score): true 1.5 pp -> 2.0 %, 1.8 pp -> 29.5 %, 2.0 pp -> 50-60 %, 1.91 pp -> 42.8 %. Matches MEAS-8. Caveat: ~50 % pass probability at a true advantage equal to the threshold is inherent in any "at least delta" superiority test, not a defect by itself; the defect is the missing row for "differ on a minority of sites, below delta in aggregate".
- Row 5's robustness clause is a non-inferiority form ("degrades no more than delta worse"); the text has no power condition on it (line 781), as MEAS-11 says.
- Severity: SIM-7 "answer" fair (a 1.8x loss on 5 % of sites reads TIE); SIM-6, MEAS-8, MEAS-11 "design" fair.

## V-7

SIM-8, MEAS-20 item 4: model error vs per-CELL oracle while rules pick per SITE; C-SCORE ORACLE rule cannot score 0.
- Verdict: HOLDS.
- Text: §6.1 lines 584-586 "Under P-PRIOR a rule picks ONE arm per site, and that arm is scored on every cell of the site (every subject, both call shapes); the oracle is per cell" (under P-SUBJ one arm per site and subject class, still several subjects and two call shapes per class); §5.4 oracle per cell; §0 item 1 and §7.1 "model error = J against O"; §8 line 730 C-SCORE "an ORACLE rule (picks the measured best) must score 0 regret exactly"; §5.2 line 522 "a no-search path wins on DENSE cells and loses on MISS cells by construction".
- Arithmetic re-done: arm N = (DENSE 1.0, MISS 3.0), arm S = (DENSE 1.6, MISS 1.0). Per-cell oracle = 1.0 and 1.0. Pick S: regret (0.6 + 0)/2 = 30 %; pick N: (0 + 2.0)/2 = 100 %. Best single pick has 30 % regret, so a perfect-model J has 30 % "model error", and a site-bound ORACLE rule scores 30 %, not 0. If the ORACLE rule is allowed per-cell picks it is not a rule in the §6.1 sense and tests only the join. The two critics propose different fixes (SIM-8: site oracle; MEAS-20.4: per-cell oracle), both consistent with the defect.
- Severity: "design" right; row 3 is inflated by this term when cells within a site disagree about the best arm.

## V-8

MEAS-4: C-PRICE's pooled Spearman passes at zero within-site skill.
- Verdict: HOLDS (mechanism), with the caveat that the synthetic assumes the model's price carries each site's scale correctly.
- Read `measurement/sims/cprice.py` first: price = base x within^skill x noise, true = base x within, where base is a site-wide scale shared by all arms of a site (log-normal, sd 0.5/1/2); skill = 0 means no within-site information; the pooled Spearman is over all arms of all sites. It implements the design's "pooled" statistic (§6.4 line 653: "A pooled rank correlation below 0.5 on D stops stage 4"; row 0 says "C-PRICE's rank correlation on D" unqualified).
- Ran it: skill 0 -> pooled Spearman 0.88 / 0.98 / 1.00 at between-site sd 0.5 / 1 / 2, and the model picks the true best on 23 / 20 / 29 of 100 sites (chance for 3-6 arms is about 20-25 %). The stop at 0.5 would not fire. Plausible in the real design because arms of one site share subject bytes and engine, so any cost model carries site scale; real between-site sd of log time across engines and text classes is well above 0.5.
- Mitigation the critic did not mention: a zero-skill J would usually fail row 2 (J beats FM by less than delta), so the harm is that rows 3-5 can run on a weak model between those gates, not a free pass. Per-site Spearman is also printed (§6.4) but not gated.
- Severity: "answer" is high; "design" is right (control cannot go red for the reason it exists).

## V-9

MEAS-2, COST-2 part 2: run-length prediction; the bench's 50 ms calibration is per SUBJECT.
- Verdict: HOLDS (conditional on how the 64 buffers map to bench subjects).
- Quotes: pcrec-bench `docs/methodology.md:81` "Per-row calibration target (ns of timed work per trial): 50000000"; `docs/methodology.md:74` "Each subject's iteration count is calibrated ..."; `docs/design/harness_contract.md:150-153` "`iters` chosen so one subject's loop is >= 50 ms"; `docs/design/gate_shape_v14.md:656` "row key = (pattern_id, regime, form or "plain", subject_id)". So calibration is per row = per subject.
- Arithmetic redone under §5.2's 64 buffers as 64 subjects: 64 x 5 trials x 50 ms = 16 s per LONG cell; §5.6 says 9,000 cells, half LONG = 4,500 x 16 s = 72,000 s = 20 h before SHORT (more rows per line bucket), compiles and pre-flights; the gate_shape_v14 ceiling `TRIAL_BUDGET_SECONDS = 20` per group pass (`:47-48`) is not violated by 3.2 s per pass but is not a per-cell budget either. §5.6's 0.25 s per cell (5 x 50 ms) is only right if a whole 64-buffer stream is ONE bench subject with one 50 ms calibration, which is the unasked streamed-mode question of V-2 (a `call-stream` replay would be exactly one such subject).
- Severity: "design" is right; the window request (F6, B2) and G4 are sized on 0.25 s per cell.

## V-10

MEAS-3: arms are separate testee runs, so "paired trial deltas" and "timing group" are unmapped.
- Verdict: HOLDS.
- Quotes: `harness_contract.md:172` "`python3 -m pcrecbench run --subbench email --testee pcre2-jit [--trials 5]`" (one testee per run; step (2) quiet pre-flight is per run; step (5) trial_agreement is stamped per record); `gate_shape_v14.md:42-44` "a PASS is one trial's sweep over every subject of one group (`harness.py`: trials are interleaved by group, so trial t of every subject in a group is one contiguous stretch of wall time"; `methodology.md:110` "Each cell runs five trials, interleaved". The interleaving is across the subjects of one group inside one testee's run. §5.1 makes every arm a testee config, so the 7-9 arms of a site are 7-9 separate runs; trial t of arm A and arm B are not adjacent in time. §5.4's "paired trial deltas disagree in sign", §7.2's "linear within a timing group, quadrature across groups" and the cross-fit's trial halves have no stated mapping to the bench.
- Severity: "design" right; fix is a bench question (multi-config interleaved pass) or a rotated-block definition.

## V-11

COST-3: levers in the trace build cannot reach the PINNED tier.
- Verdict: HOLDS.
- Quotes: pcrec-bench `testees/pcrec/pin.sh:107-108` `( cd "$dest.partial" && gnutimeout "$BUILD_TIMEOUT" make -j"$JOBS" )` (plain default build, no CAND_TRACE variable); `testees/pcrec/configs.toml:247-273` pcrec-local: "a PROVIDED binary, no pin.sh ... SCRATCH-TIER BY CONSTRUCTION ... the store refuses the record into the canonical tree", `$PCREC_LOCAL_FLAGS` is one process-wide string appended to the base flags (no per-config environment). The design (§5.1) requires H at the PINNED tier and the levers as environment variables of a trace build; B4 asks only about spelling. So either a test-only CLI spelling in the default build (a public-surface/spec change, against "default build moves no byte" and C-LEVER) or a pin.sh variant building a second compiler per pin per box. Not costed in §11.
- Severity: "design" right.

## V-12

PREMISE-4: scratch tier timings are never stored, so by-reference provenance has nothing for D.
- Verdict: HOLDS.
- Quote: `pcrec-bench/testees/pcrec/CLAUDE.md:60`: `pcrec-local` "a PROVIDED binary, `$PCREC_BIN` ... No pin, SCRATCH TIER BY CONSTRUCTION, never in `store/`, never ranked"; configs.toml:261-263 repeats "the store refuses the record". §4.1 row 2 says ground-truth timings live in the bench's own store by reference (pin, config id, tier, record id); §5.1 puts the D sweep at the scratch tier. D feeds K-fit, C-PRICE (a row-0 stop) and C-FM/C-KIT/C-RULE; none of that has a store record id. The D-sweep output must be archived by the bake-off with sha, which the design does not say.
- Severity: "design" right.

## V-13

PREMISE-8, SIM-13, MEAS-18: C-FM near-tautological; L-VALID optional and default-path only.
- Verdict: HOLDS.
- Text: §3.4 "L-VALID ... (pcrec, trace build only, optional). A QUIET walk ... evaluates EVERY row of every slot on the default path ... Not needed for the bake-off's correctness"; §6.2 FM "walk the valid rows of each slot in `cand_rows[]` order on the hypothesized upstream path"; §6.4 C-FM "re-derives FM from the valid-row records and the table order ... compared with the compiler's actual stamps"; §8 C-ENUM "L-VALID's dump against the census walk's reached rows"; §6.1 table has no row for L-VALID's dump (the FM column lists arms/paths, facts, rates). The valid-row records exist only through L-VALID. A site's census gives reached arms, not valid rows.
- Code: `emit_dfa.c:10675-10680` (cand_eval_flags: "G1 reads NEXT under the handoff's deny while NEXT's unmasked selection is open") and `:10693-10702` (`cand_nested_read`): predicates read other slots' selections under other deny bits, so row validity on a non-default upstream path cannot be computed from a dump on the default path. The first valid row in table order IS `cand_select`'s pick (`:10721-10731`), so the compiler's stamps and the valid-row records are the same predicates on the same compile: C-FM can detect a mis-copied table order and nothing else, and if L-VALID is not built the simulator can satisfy C-FM by returning the census arm whose deny set is empty.
- Severity: "design" is right.

## V-14

SIM-2: the deny walk never reaches route-pair arms.
- Verdict: HOLDS (one of the critic's examples is conditional on `--no-captures`).
- Ran (build/pcrec, `--features all`): `POP_EST:(\d{9,})` default -> `RX_ENGINE "vm"`, `RX_VM_PREFILTER "hybrid"` with captures on; with `--no-captures` default -> `RX_ENGINE "dfa"`. `--engine=vm` (with or without `--no-captures`) -> `ENGINE vm`, `VM_PREFILTER "none"`, `VM_START_SCAN "first-class"`. `(?<=^|\W)\w+(?=\W|$)` default -> `vm`/`hybrid`; `-fno-prefilter` -> `vm`/`none`/`first-class`. So each pattern has a valid second route-pair arm; the critic's "default ENGINE dfa" for POP_EST holds only under `--no-captures` (the critic's walk presumably used it), not under captures-on default.
- Route levers are not row denies: `grep NO_PREFILTER emit_dfa.c` finds only a comment (`:3190`); `PCREC_NO_PREFILTER`/`FORCE_PREFILTER` and `--engine=` are selection inputs (`lib/pcrec.h:192`), not any `cand_rows[]` row's `c.deny`. §3.1 step 1 adds compiles only "with that row denied", so the walk never emits them, while §3.3 lists the route pair as forceable and §7.3 has an "engine route" stratum.
- Severity: "design" right.

## V-15

SIM-3, PREMISE-15 c: one artifact holds several rows per (slot, route) keyed by asker/hand; CandPath is not a row-per-slot path.
- Verdict: HOLDS.
- Ran `build-trace/pcrec -p rx --features all -o t1.c --pattern '\b[A-Z]{4,}\b'` (stderr in verify/w/t1.err): 51 CANDROW lines. NEXT dfa records: `first-class-bounded` (askers `scan-state`, `pf-of`, `form-fwd`) and `next-none` (asker `scan-state`) = two distinct rows in one (slot, route); FINISH dfa has `verify-at` (hand AT, asker finish-match) and `report` (hand SPAN, asker finish-search) = two rows; PRESENCE `presence-none` many times. `CANDPATH dfa dfa FRA LOCATE@dfa,WINDOW@dfa,...` is only the route pair plus asked-slot masks.
- `CandPath` (`emit_dfa.c:11828-11834`): fields body, locate, finish, built/needs/members, asks[3], recover. `cand_path_row` (`:11842-11858`) selects only LOCATE and RECOVER (FINISH per hand elsewhere); every other slot returns NULL. The design's "The tree already derives the selected path as a value (CandPath ...)" in the Words list is an overstatement for a "row in every slot".
- Severity: "design" right for C-FM's label problem.

## V-16

PREMISE-9, SIM-4: the walk denies unpriced slots (FINISH twins, RECOVER doubling).
- Verdict: HOLDS.
- Read `premise/combo.py` first: for each of 6 public flags ({-fno-run-prefilter, -fno-offset-skip, -fno-req-handoff, -fno-start-set, --memfn=no-fd-pres-g1, -fno-anchored-dfa}) it compiles all 64 subsets with the review tree's compiler under `gnutimeout 30 nice`, hashes `.c` + `.h`, and lists stamps; it implements what the critic says. I re-ran a copy with outputs under verify/w/combo (128 compiles): `foo\d+` -> 10 distinct artifacts, exactly 5 of them with `RX_DFA_MATCH "search-filter"` (the `-fno-anchored-dfa` twins); `req-[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}` -> 14 distinct, 7 of them search-filter twins (the critic's 10 came from the walk with a different flag set; mine is the exhaustive 6-flag product, so the count differs but the doubling is the same).
- Diff of `foo\d+` default vs `-fno-anchored-dfa` (verify/w/f0.c, f1.c): hunks at lines 17, 30 (stamps), 198-283 (`rx_match`/`rx_match_caps`) and 437 only; `rx_search` (lines 100-197) is identical, so the twin changes only the match-here entry, which neither §5.3 call shape (find-all, first-match search) times. FINISH is not in §3.1's priced-slot list.
- RECOVER: UUID pattern default `RX_DFA_START "end-minus-width"`; with `-fno-start-width` -> `"reverse-pass"` (different bytes, 9c8fab417dec vs 869e26e7c270). §3.3 calls RECOVER "a dominance ... timed only as the dependent slot it is", but §3.1 step 1 walks every slot on the path, so RECOVER doubles every NEXT arm.
- Severity: "speed" right (arm counts and §5.6 sizing; dedupe by bytes cannot merge the twins because `_match` differs).

## V-17

PREMISE-2: FINISH per-hand totality; the walk can deny a hand's only finisher.
- Verdict: HOLDS.
- Code: `cand_fallback` (`emit_dfa.c:10739-10747`) returns the LAST row of the slot routed on the route, hand-blind. FINISH rows (`:10589-10630`): `prio-const`, `verify-at` (deny `PCREC_NO_ANCHORED_DFA`, hands AT/ENDSET on DFA), `search-from` (`cand_always`, routes all, DFA takes AT and ENDSET), `nomatch`, `report` (`CR_DFA | CR_ATTEMPT`, takes SPAN only, last). So on the DFA route the slot "fallback" is `report`, while the AT hand's last row is `search-from`. The totality comment at `:11394-11400` says exactly that: "FINISH's totality is per HAND ... the last row taking each hand ... is undeniable".
- Ran: `foo\d+ -fno-anchored-dfa` -> `RX_DFA_MATCH "search-filter"` (= `search-from`'s tok) vs default `"unwrapped"` (verify/w/f0.c:30, f1.c:30). Under §3.1 step 1 the next step denies any row that is "not the slot's fallback" (here `search-from`), leaving no row for AT; the self-check's `finish-no-hand` failure (`:11513`) is the trace build's outcome.
- Severity: "design" right, with the same fix as V-16 (restrict the walk to priced slots).

## V-18

MEAS-6: C7 turns red on honest noise, and its planted failure does not reach it.
- Verdict: PARTLY (the mechanism holds as the design is written; the floor definition the sim uses is thinner than the one regime_eval ships).
- Read `measurement/sims/c7.py` first: 7 arms, true times 1.0, 1+gap, then three-plus arms 0.02-0.5 slower, per-trial multiplicative gaussian noise sigma; the cell's floor = |mean(default arm, 5 trials) - mean(A/A copy, 5 trials)| (ONE A/A pair); a cell qualifies if the full-trial top-two gap exceeds that floor; C7(b) compares the best arm on trials {1,3,5} against {2,4}. This implements §5.1 (two A/A configs per site for "the cell's floor") plus §5.4/§8 C7.
- Ran it: top-two TIED -> 49-50 % of cells qualify and 35.4-35.6 % disagree between halves at sigma 0.5/1/2 % (bar 5 %); 1 % gap at sigma 1 % -> 14.3 %; mixed gaps at sigma 1 % -> 5.8 %, at 2 % -> 9.4 %. Reproduced exactly.
- Caveat the critic did not state: regime_eval.md defines the cell's threshold as `NULL_c = max(AA_c, nu x ns_walk(c))` (`:540`), i.e. a RELATIVE floor of at least about 3 % on top of one A/A pair, which would stop ties qualifying at these sigmas; the bake-off's §5.4 says only "the cell's A/A floor" ("gridread's rule") and never defines nu. So the failure is real for the design as written and would largely vanish if the design adopted regime_eval's NULL_c; it is a missing definition. The planted failure (time one arm twice under two config ids, halves must call it NULL) is an A/A check of the NULL rule and cannot make C7(a) or (b) red: confirmed by reading §8 line 731. regime_eval's C7 split is 7 rounds as 4/3 (`:2105-2112`), the bake-off's is 5 trials as 3/2.
- Severity: "design" right.

## V-19

PREMISE-12, MEAS-7: `noise_e6` absent on every row of the only set; the all-rows agreement arithmetic.
- Verdict: HOLDS.
- Ran: `awk` over `measure_store/zen4-grid1/1/set.tsv` rows section: 26 `-|derived`, 42 `-|measured`: all 68 rows have `noise_e6 = -` and `n = -` (header line 36 lists the columns). `docs/spec/measures.md:79` only names the column; `docs/design/measure_sets.md` says the noise is the A/A floor and fit spread in quadrature, so the band is a one-sigma-scale quantity when present.
- Arithmetic (`measurement/sims/repro_blind.py` read, then run; I also recomputed by hand): two independent measurements of a row differ with sd sqrt(2) x sd, so P(|diff| < b sd) = 2 Phi(b/sqrt 2) - 1 = 0.520 / 0.843 / 0.966 / 0.995 at b = 1 / 2 / 3 / 4. Over 68 rows: 5e-20 / 8.8e-6 / 0.096 / 0.73. Matches the critic. This assumes the band is b x the per-row sd and no between-window drift; §4.3 says only "within its own stated noise band" with no multiplier, so the control as written is underspecified, and with `noise_e6` empty there is no band at all.
- Severity: "design" right.

## V-20

PREMISE-11: D166 addendum 2 vs §4.2/K6.
- Verdict: PARTLY.
- Quotes: `decisions.md:9719-9724` D166 item 1 "pcrec is compiled with the latest set by default ... A default-set change carries a mover census in the same commit"; `:9739` Q-MS-1 "until a SECOND OFFICIAL set exists ..., a bare compile reads the LATEST set"; `docs/spec/measures.md` 5¶6 "its default is the latest committed set". Mechanically `measure_store/DEFAULTS` is an explicit pointer (`idk zen4-grid1@1`, with `DEFAULTS.log`) and `index.tsv` has a `status` column (`current`), so a non-default committed set is mechanically possible; but the rulings say "latest", and the design (§4.2) offers "outside the default pointer ... or a separate set id" as if D166 addendum 2 allowed it. The cite is accurate as a quote but does not support the departure. The store owner is main (D167 Q-R17P-14 "Main (measure_sets' owner)", `:9756`), yet K6 is listed under "For the kit" (§12); the design text itself says "the store's rule decides". A ruling from Frank is needed to depart from "latest".
- Severity: "design" is right but small (a question re-homed, not a flaw in the experiment).

## V-21

PREMISE-10: ruling clauses each option reverses.
- Verdict: PARTLY (the quotes are right; the proposed option-to-ruling mapping is incomplete, which is the finding's own point).
- Quoted at the cited lines: `decisions.md:8995` D146 "pcrec does no cost comparison and carries no architecture knowledge"; `:9497` D161 add. 11 "pcrec PRODUCES the knowledge and owns the origin, the engine/route ... the kit owns every pick row, its constants ..."; `:9526` Q-WR-9 "pricing waits for add. 11's trigger ... the consumer's cost enters as a per-route MEASURED constant in the D166 set, never a pcrec price model"; `:9918` D176 Q4 "presence and stop ... ONE decider, the kit's window family". Also `:9468` D161 add. 6 title "CONSUMER PRICE is DROPPED from the contract; memfn owns choosing the best windows".
- Check of the critic's mapping: D146's "pcrec does no cost comparison" is contradicted by EVERY option whose backend takes an argmin (A1, A1u, HY, Dx, Dp, KF per §2), not only Dx/Dp/HY, and Q-WR-9's "never a pcrec price model" is arguable for A1's backend sum of invariant terms; the critic's "consistent with A1/A1u/KF/MN" is not established. So §9.4 criterion 1 (the predicted deciding path, per §9.1 item 2's tie prediction) needs a pre-registered option x clause table, but the table PREMISE-10 sketches would itself need a ruling-by-ruling read.
- Severity: "design" right; no data-dependent consequence beyond G3's "mechanical" claim.

## V-22

COST-1: stage order; does stage 2 depend on stage 1; does row 1 read any card.
- Verdict: PARTLY (the dependency claim holds; the cost consequence depends on an execution order the design does not fix).
- §11 table (lines 837-842): stage 2's prerequisites cell reads "stage 0's census and arm list; L-KIT for the within-site arms; the bench's answers to B1, B4, B5": no stage 1. Row 1 (line 777) reads FM's mean regret, FM's 1.5x cell count and C-BLIND on H-open: no card, no simulator. Stage 1's own text calls its sets "owed under every outcome" (§4 intro, §11 total paragraph, G4) by PR R9.1 "under every PRICED option"; row 1's verdict says "the pricing build is not triggered (D77)". The Mac set and the Zen 1 line (stage 1 plus the 60-site subset) feed only §7.4's cross-box reading, read only in rows 5-6. So if executed in listed order, ~9 of 13 box hours (Zen 4 stage 1 2 h, Zen 1 5 h, Mac 2 h) precede row 1.
- Against the critic: the table is numbered, not declared sequential; Frank's [R-M2]/[R-M4] ("remeasure and save by architecture") is a standing owner request for per-box sets independent of the bake-off's outcome, which the design cites as the reason stage 1 is owed. Also the reverse omission: stage 3 (simulator) lists only "stage 2's D records" but J needs stage 1's cards, so the table omits stage 1 as a prerequisite of stage 3.
- Severity: "design" fair; fix is to state conditionality (and the stage 3 prerequisite).

## V-23

MEAS-10, MEAS-15: strata sizes per class; corpus pool sizes against regime_eval §2.4 rules 3/4.
- Verdict: MEAS-10 HOLDS; MEAS-15 PARTLY.
- MEAS-10: `awk` on `docs/dev/lanes/rwquest/questions.tsv`: structured 24, logs 28, markup 24, nonenglish 25, code 27, binary 22, prose 27 (176 data rows). x 0.7 x 2/3 (H share, H-open share per §3.2) = 11.2 / 13.1 / 11.2 / 11.7 / 12.6 / 10.3 / 12.6: none reaches 15, even if every question qualified. Density bins on the full-file `py_matches_per_MiB_full` column: MISS 9 (rows with 0), SPARSE 88, DENSE 74, n/a 5. Matches. S-bench sites could add to prose/logs only; "density bin" and "call shape" are cell attributes in a SITE-counted stratum rule (§7.3), site counts undefined.
- MEAS-15: file sizes (ls of worktrees/.corpus): apache_access 2,369,603; linux_syslog 2,302,067; rust 1,691,876; javascript 2,730,048; go 467,001; but logs also holds bgl/hadoop/openstack at ~42 MB each and zookeeper 10.6 MB, so "logs has two small sources" is true only per source; regime_eval's pool for logs is "the same source" (`:941`), so the apache and linux_syslog pools are small. Rule 3 gives M = min(64, floor(U/64 KiB)) from U = pool minus a 1/8 reserve: rust U about 1.48 MB -> M about 22; apache_access M about 31; go M = 6 (< 16, rule 4's floor -> `short-pool`, GATE-EXCLUDED, counted). So "64 distinct 64 KiB buffers" (§5.2) is a ceiling, not a guarantee, and the rule itself admits 16-64. The windows are per POOL (`h(pool, W, j)`), so every D and H site of a pool shares the same windows; the rule has no D/H split, so H-vs-fit-buffer disjointness (§3.2 item 2) cannot hold for K-fit's reading, where D's timings are the fit data. Impact on the verdict is small (K-fit is robustness only, §6.3), larger on the "held-out" wording.
- Severity: MEAS-10 "design" right; MEAS-15 "design" slightly high ("doc"/"design" depending on whether K-fit's H reading is called subject-held-out).

## V-24

MEAS-12, MEAS-13, MEAS-16, MEAS-17: card regime vs application regime; signed rows; P-SUBJ in-sample; inconclusive-spread handling.
- Verdict: MEAS-12 HOLDS; MEAS-13 HOLDS; MEAS-16 HOLDS (severity doc); MEAS-17 HOLDS.
- MEAS-12: armread_report.md quotes re-read: `:57` "VM: C_call is not separable ... The VM is not linear"; `:85` "C_match is not a constant here" (falls as matches get denser, p1 dfa 7.7 -> 3.9 -> 3.2 ns); `:94` "C_call is not transferable between modes". Density check: digit bytes are 0.2388 of `worktrees/.corpus/logs/apache_access.log` (my own count, python3 -I), against C-ENTRY's top planted rate of 1/32 = 0.031 per byte (§4.2 line 376): 7.7x extrapolation. §4.2 keys cards by consumer kind only; no card pattern is named.
- MEAS-13: `measure_store/zen4-grid1/1/set.tsv` has 4 rows with negative `value_e6` (e.g. `kit.delta.V1.WALK.DFA_SCAN.n48 = -23784355`, `n63 = -29598309`); a relative "A/A floor exceeds 20 % of its value" (§4.5) is undefined or always tripped on a signed or near-zero quantity (armread's VM C_match -0.32 ns). The sentence is "or a card's A/A floor exceeds 20 % of its value", so existing kit delta rows are in scope.
- MEAS-16: design lines 573 and 578 (P-SUBJ rates and fractions "counted on the site's subjects (§5.2)", i.e. the timed windows) vs lines 250-252 (H subject buffers disjoint from "every analysis exemplar"). In-sample by construction; the arm's label "the cell's own measured rates" admits it, but the disjointness rule is stated without exempting P-SUBJ. Severity doc is right.
- MEAS-17: `harness_contract.md` step (5) "exit code 4 = the written record's status is `inconclusive-spread` ... a window script re-measures such a cell once"; `gate_shape_v14.md:584-627` §3.4 "An `inconclusive-spread` record is UNRANKED". §5.5 counts only answer failures and give-ups; B3 asks suitability only. Slow-trial counts re-checked in `gate_shape_v14.md:382-386`: k = 1.30 -> 724 rows, k = 1.50 -> 387 rows of 62,923 (~1 %, `:222`). Median-based tolerance vs the design's half-means: one 1.4x trial in a 2-trial half moves its mean by (1 + 1.4)/2 - 1 = 20 % (arithmetic). The design does not specify the half estimator, so a median-of-half is available as a fix.

## V-25

SIM-11: MN's view vs its formula.
- Verdict: HOLDS.
- §6.1 table consumer-cards row (line 576), column "A1/A1u/HY/KF/MN kit level": "yes (MN: C-BYTE only)"; §2 MN row "kit (per-byte card only)"; §6.2 MN (lines 614-616): "priced `C-BYTE(kind) x bytes`, against the kit's shipped pick priced with the kit's own cards plus `entries x C-ENTRY(kind)`". C-ENTRY is a consumer card (§4.2) and is absent from MN's declared view while MN's formula reads it. The view check ("other fields raise on access") would raise on the correct rule. Severity: "design" is a little high ("doc" for a one-line fix), but harmless to keep.

## V-26

SIM-14: verdict rows do not name call shape or prior arm.
- Verdict: HOLDS.
- `grep P-PRIOR|P-SUBJ|LONG|SHORT` on the design: §5.3 (defines the shapes), §6.1 (the arms), §7.1 line 661 ("Per rule, per call shape, per prior arm"), §7.4 line 709, and only row 6 of §9.3 (line 782) mentions LONG/SHORT. Rows 1-5 name "H-open" without a call shape or prior arm; with two shapes and two arms each row has four candidate numbers. Row 4 asks per-site equivalence "on at least 95 % of H sites" then defers to "the §7.2 tests", which are population-level (site bootstrap) plus 2.N measurement noise, so what a per-site test means is undefined. G3's "mechanical" claim needs the prereg to name them.
- Severity: "design" right.

## V-27

PREMISE-13, COST-6: M3/M4 naming.
- Verdict: HOLDS.
- `docs/design/measure_sets.md:2199-2200`: "M3 | `pcrec-measure` (the parts + the measures row only, §7.1), the quick profile, per-group gates and PARTIAL, `local` tier ... | a stated install-time need (D166 item 3 names it ...)"; "M4 | pcrec's own quantities (`pcrec.c_call`, `pcrec.c_byte`), their cards, the pcrec-side dependency hash's body normalization (§2.4) [r2 n7], and `cand_rows[]` as readers in the census | the regime table's pcrec-side build". `:2329-2333`: the key-only schema is a separate deferred row "Trigger: M4, if the cards for `c_call`/`c_byte` turn out to be all boilerplate". `:1174-1182` §7 "The install-time tool (M3)": `pcrec-measure`, one driver, owner-supplied cards, quiet gate, A/A pairs. The design (§4.2) lists the key-only schema as part of M4 and never names M3 (`grep M3|pcrec-measure` finds only the tag "[R-M3]", line 386); §4.3's "one wrapper" is M3's driver in all but name. C-WALK is "counted, not timed" and C-MATCH is not an M4 quantity.
- Severity: PREMISE-13 "doc" right; COST-6 "maintenance" right (lane estimate hides two milestones, one with a spec hunk).

## V-28

PREMISE-14, COST-4, MEAS-20 items 1-3: goals' measurable forms vs the body; hour totals; A/A vs dedupe; census cite line.
- Verdict: HOLDS (all), one nuance.
- G1 line 91 "100 % of H sites" vs C-RULE line 728 "100 % of D sites before H is read" (the blinded author could not see H sites before the pick). G3 line 93 "prereg file's sha is in the journal before the first H timing" vs §3.2 item 3 (lines 253-255) "H's timing may run before the rules are frozen" and §11 stage 3 "the prereg file frozen and its sha journalled" (after stage 2's H sweep); nuance: stage 0 builds a prereg SKELETON (salt, counts, margins), so G3 can be read as the skeleton's sha, which the critic's fix proposes; the design does not say so. G4/F6 "2 on the Mac" vs §11 stage 1 "~1-2 h" per window x 2 windows = 2-4 h. Zen 4: stage 1 2 x 1 h + stage 2 1-2 h + 3b <= 1 h = 4-5 h against "about 6"; the SIMD-on reading (line 506) and the VMREC re-measure (line 853-856) are untimed extras. Lanes: stage 0 two, stage 1 one, stage 2 one, stage 3 two, stage 3b "a fresh small lane", stage 4 one = 8 incl. 3b, 7 without (COST-4 d, a count nit).
- G5 vs PR R5.2: `git show 90d5150f7:docs/design/memfn/pricing_requirements.md` R5.2 "(c) ... both engines, both SIMD layers" and R5.5 "Both SIMD layers are read (D147)"; design non-goal (line 107) and line 506 time SIMD-off for every graded cell, SIMD-on secondary on H-open only. So H is not "the held-out regret population PR R5.2 requires" for SIMD.
- §3.5 dedupes byte-identical arms (line 332) while §5.1 line 504 adds "two A/A configs per site (the default compile under two config ids)", byte-identical by construction: the dedupe must exempt them (MEAS-20.1).
- Census cite: `tests/codegen/run_form_census.sh` memchr 750 at `:315`, offset-set 290 at `:323`; the design cites `:307-316` for both; and `:281` shows the floors count artifacts over "patterns x 2 engine requests", not patterns. MEAS-20.3 holds.
- Severity: PREMISE-14 "design" (G3 timing) fair; the rest "doc".

## V-29

PREMISE-15 a, b, d, e, f; SIM-12: probe and cite mismatches.
- Verdict: HOLDS (all).
- (a) `[<>&]x`: default `RX_DFA_SCAN "cover"`, `RX_REQ_WHY "dominated"`, `RX_DFA_PREFILTER "none"`, `RX_DFA_START "attempt-start"`; with `--memfn=no-window-search`: `RX_DFA_SCAN "unanchored"`, `RX_REQ_WHY "dominated"` (unchanged), `RX_DFA_PREFILTER "offset-set"`, `RX_DFA_PREFILTER_OFFSETS "0,1*"`, `RX_DFA_START "end-minus-width"`. The design (line 198) says PRESENCE moves "from `dominated` to `emitted`": not reproduced; RECOVER and NEXT and LOCATE do move.
- (b) `[.,;]\d` with `-fno-run-prefilter -fno-offset-skip -fno-req-handoff -fno-start-set`: `RX_DFA_SCAN "cover"`, `RX_DFA_PREFILTER "none"` (no NEXT row asked), `RX_REQ_WHY "none"`; adding `--memfn=no-window-search`: `"unanchored"` / `"byte-class"` / `RX_DFA_START "end-minus-width"`. §3.3/§10 omit the flag.
- (d) `grep -c MF_TRACE memfn/src/*.c`: compose.c 3, finder.c 1, gate.c 5, window.c 0 (all other files 0). The design (line 317) names `window.c`; the Table A code L-KIT must dump has no trace hook today.
- (e) see V-28: cite range omits :323 and floors count artifacts.
- (f) `decisions.md:9385-9387` D156 addendum 2 "the stamps of the LOCATE x FINISH slots are generated from the path derivation ... REQ_WHY stays at four tokens"; the design (line 195-196) lists `RX_DFA_PREFILTER`, `RX_REQ_WHY`, `RX_VM_RESEED` (NEXT, PRESENCE, RETRY) as D156-add.-2-generated; those are outside its stated scope, so C-FM's "a source it did not compute" leans on CANDTRACE for those slots.
- Severity: "doc" right (SIM-12's collateral-move example does not change the conclusion that a deny is not a one-slot counterfactual).

VERIFY COMPLETE
