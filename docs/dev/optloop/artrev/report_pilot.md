# [ARTREV] pilot report (S6)

Lane `artrep`, 2026-10-06. Charter `charter.md` §4 S6 and §5; decision record D150. This is the deliverable Frank asked for: a report of results with suggestions. It writes no new numbers. Every figure is cited from `confirm/verdicts.md` (S4, Linux), `generalize.md` (S5), `pilot_index.md`, `notebook/`, the lane reports (`docs/dev/lanes/{artharness,artprep,artcollect,artgen,artconf}_report.md`) and the 2026-10-05/06 journal entries. Where sources disagree, the disagreement is stated.

Measurement frame (`confirm/verdicts.md`): ubuntubudu (Ryzen 5 1600, gcc 15.2 `-O2 -fPIC`), 11 interleaved rounds, pad-shift layout control at 7 pads, artifacts regenerated at pin `57db5152` (abi 62) with sha256 equal to `pilot_pins.tsv`. WIN/LOSS only past max(null deviation, arm IQR, orig IQR, both pad spreads), same sign plain and at every paired pad. Units ns/B, lower is better. "Cell" is the pad-controlled CELL row.

## 1. Verdict

**Yes.** Bottom-up review of emitted C found real, confirmed wins on all three routes reviewed, and the pilot gate (charter §5) is met on its first criterion (at least one confirmed S4 WIN). Of 22 counted leads, 15 are confirmed cell WINs, 6 NOISE, 1 LOSS. Headline cells:

- **A01 `stack-frame` (DFA find-all, losing x4.83):** L1, anchor the scan on the rarer required byte `(`, is a **-72.2% cell WIN** (0.455 to 0.126 ns/B, 7/7 pads, dense and sparse WIN, 0 repairs). Census population: 17 bench / 90 corpus artifacts have an inner necessary byte at least 2x rarer than the scan key.
- **A09 `level-context` (hybrid, losing x3.82):** L1, skip the `{0,29}` component with two rare-byte `memchr` streams, is a **-94.9% cell WIN** (3.060 to 0.157 ns/B, 7/7 pads); the scalar-table form L2 is -75.9%. The CTX family is 5 bench cells.
- **A07 `doubled-word` (VM with backreference, losing x1.93):** 12 of 13 reviewer arms are cell WINs (-22.3% to -83.4%). The **possessive spelling `\b(\w++)\b\s++\1\b` alone is -57.6%** (17.39 to 7.37 ns/B, 7/7 pads) with **no new codegen**: the shipped emitter already makes that spelling frameless and inline. What is missing is a possessify analysis (two declining arms). Population: 1 bench / 2 corpus.

Two caveats bound the claim. The wins are on 3 hand-picked artifacts of a 16-row selection, and the population numbers come from an upper-bound census, not from the reviews. And three of four reviewers timed nothing (§7), so "iterate with timing" was barely exercised.

## 2. Selection and stratification

`selection.tsv`/`selection.md` hold 16 draft cells, each one the bench already times, stratified by route (read from the artifact's own stamps) and standing (pcrec auto-caps / libpcre2 jit-caps: losing > 1.15, near-tie 0.90-1.15, winning < 0.90). The pilot reviewed 3:

| id | artifact | route | captures | standing | gap group | emitted lines |
|---|---|---|---|---|---|---|
| A01 | loglines/stack-frame | DFA find-all | none | losing x4.83 | FS-DFA / START-SET | 919 |
| A07 | capability/doubled-word | VM, no prefilter | 2 slots (backref) | losing x1.93 | BACKTRACK | 438 |
| A09 | loglines/level-context | hybrid (DFA gate + VM) | none | losing x3.82 | CTX | 1185 |

Four blind reviews (A07 twice, the dual-review pair), each in its own D27 cell, opus. Limits:

- **All three are LOSING cells.** No near-tie or winning artifact was reviewed, so the pilot says nothing about whether winners still waste work.
- **One artifact per route**: a route-level claim is n=1. No utf8, no DFA-attempt route.
- **Compilers differ**: generated at the pin with gcc-16 (Mac), timed on Linux with gcc 15.2.
- **Standing ratios are one pin older than the gap report**; they stratify, they are not results.
- **Population counts are K35-counted but necessary-condition upper bounds** for I3, I7, I14, I15 (labelled in generalize.md). A count is a shape's presence, not its share of time.
- **Count discrepancy:** generalize.md and artgen's report say "25 counted leads". The four leads tables in pilot_index.md total 22 (4+6+6+6) and artcollect re-verified "all 22 final twins". This report uses 22; the 25 is not reconciled in the sources (plausibly counts revisions; A09 alone had 9).

## 3. Per artifact

Verdict = confirmed cell verdict; dense/sparse = generality rows; repairs = give-up repair count (original gives up, twin answers, each checked against libpcre2); tag = `changes-giveup-surface` where repairs > 0. Idea ids and emitter sites are generalize.md §2 (line numbers at `6a0b7953`); known/new is its call.

### A01 loglines/stack-frame (DFA find-all; orig 0.455 ns/B; null deviation 0.039)

| lead | what | cell | vs orig | dense / sparse | repairs | idea | emitter site | pop b/c | known / new |
|---|---|---|---|---|---|---|---|---|---|
| L1 | scan rare byte `(`, walk back over the id run, anchored DFA there | **WIN** | -72.2% (pad spread 0.041, 7/7) | WIN / WIN | 0 | I1 | `emit_unanchored` emit_dfa.c:8565; pre-check :1362 | 17 / 90 (8 / 31 at >=8x) | generalises [ENG-TACTICS] (b) |
| L2 | `memchr('t')` not `'a'` | NOISE | -14.6% (pass 1 only, thr 0.084) | NOISE / NOISE | 0 | I2 | none; findings.c:522 | 109 / 559 run-bearing | known: [OPT-FREQPICK] + [FINDINGS] |
| L3 | backward scan for last "at ", drop reverse DFA | NOISE | -7.8% (5/7 pads) | **WIN** / NOISE | 0 | I3 | axis J dfa_search_starts[] :7659 | <=71 / <=389 | generalises axis J `pinned`; new row |
| L4 | skip first re-skip at handoff | NOISE | +8.4% slower, below thr (pass 1) | NOISE / NOISE | 0 | I4 | pf_open :5809; handoff :1124 | 36 / 114 | candidate mechanism for K88 |

L1 is the whole A01 result: the cell median is set by the 4 `fail` subjects, whose cost is `memchr('a')` once per `a` (33,377 calls/MiB) proving "at " absent; `(` is 3,819/MiB. L3 is regime-only (dense WIN, cell NOISE, pad spread 0.067 about equal to the effect). Repairs 0 on all (DFA route, no budgets), nothing tagged. Stage 3 does not move A01 (ss3 compile byte-identical apart from the abi stamp), so I1 is not moot. The review timed nothing (suite lock and load gate refused every attempt); the reviewer's expectations were work counts.

### A07 capability/doubled-word (VM + backref; orig 17.39 ns/B; null deviation 0.027; run 003 is the verdict run)

Two independent reviewers, ids kept as a_* / b_*. Stacked arms are verdicts of the STACK against orig, joined to the idea that adds the last member (generalize.md §1.4).

| lead | what | cell | vs orig | dense / sparse | repairs | idea / site | pop b/c | known / new |
|---|---|---|---|---|---|---|---|---|
| a_L1 | start only at word starts | **WIN** | -22.3% | WIN/WIN | 0 | I5; vm_start_row emit_dfa.c:6697, seek :6727 | 2 / 1 | generalises [START-SET] stage 2 |
| b_L1 | same (rx_next_word_start) | **WIN** | -22.9% | WIN/WIN | 0 | I5 | same | same |
| a_L2 | drop the two give-back frames | **WIN** | -34.8% | WIN/WIN | 5,380 | I6; possessify.c first_of :213, :377; emit_vm.c:4672 | 1 / 2 (pos) | generalises [ENG-BREP] rung 1 |
| b_L2 | same | **WIN** | -35.4% | WIN/WIN | 5,380 | I6 | same | same |
| a_L3 | straight-line attempt (on L2) | **WIN** stack | -50.9% | WIN/WIN | 294,884 | I7; vm_emit_storage emit_vm.c:11737, vm_set :3464 | <=66 / <=1,454 (frameless 27 / 623) | NEW |
| b_L3 | plain RX_SET stores (on L2) | **WIN** stack | -41.6% | WIN/WIN | 294,884 | I7 | same | NEW |
| a_L4 | fused word walk (L1+L3) | **WIN** stack | -80.0% | WIN/WIN | 294,884 | I5 resume + I7 | | |
| b_L4 | L1+L2+L3 + `rx_fail = return -1` + inline | **WIN** stack | -70.7% | WIN/WIN | 294,884 | I8; [CC-DIFF] entry shapes emit_vm.c:11432-11534 | 30 / 660 frameless today | SHIPPED; follows I6 |
| b_L5 | + restart past dead spans | **WIN** stack | -73.7% | WIN/WIN | 294,884 | I5 restart | | |
| a_L5 | + 256-byte table | **WIN** stack | -83.4% | WIN/WIN | 294,884 | I9; vm_cls_test :1656 | 44 / 67 | known [OPT-A], [CLS-TREE]; codegen-micro |
| b_L6 | + 256-byte tables | **WIN** stack | -74.2% | WIN/WIN | 294,884 | I9 | same | same |
| a_L6 | counters in locals | NOISE | -0.05% (about +2% dense/sparse/t1m; t64k pad spread 3.8) | WIN +2.5% / WIN +1.9% | 0 | I10; emit_vm.c:12108-12160 | 41 / 837 | known territory [OPT-B]; codegen-micro |
| poss | pattern spelled `\b(\w++)\b\s++\1\b` | **WIN** | **-57.6%** (pad spread 1.78 = thr, 7/7) | WIN/WIN | 50,168 | I6 + I8 | 1 / 2 | the gap |

`poss` is the shipped emitter at the pin compiler (`RX_VM_FRAMELESS 1`, `RX_VM_ENTRY_SHAPE "inline"`, zero `RX_PUSH` uses); it sits between b_L3 and b_L4. It is not a counted lead (the confirmer added it). Increments inside stacks were NOT isolated: "tables 3.48 to 2.89 on a_L4" is a stack difference, not a verdict on tables. a_L6's sign is consistent on dense, sparse and t1m but the t64k pad spread keeps the cell inside threshold. All 14 A07 CELL verdicts agree between run 002 and 003; 003 is reported because `orig2` read LOSS (-1.00%) on one dense row of 002.

### A09 loglines/level-context (hybrid; orig 3.060 ns/B; null deviation 0.019)

| lead | what | cell | vs orig | dense / sparse | repairs | idea / site | pop b/c | known / new |
|---|---|---|---|---|---|---|---|---|
| L1 (r2) | skip `{0,29}` with O/T memchr streams | **WIN** | -94.9% (7/7) | WIN/WIN | 0 | I12 (+ byte choice I2); new row in dfa_pfs[] emit_dfa.c:6658, ofsskip :6501 | 21 / 11 (only 3 / 2 prior-cheaper) | generalises [OPT-A] memchr2/3 + startset §8 stage 5 |
| L2 | same skip, scalar 256-byte table loop | **WIN** | -75.9% (7/7) | WIN/WIN | 0 | I11; START-SET stage 3 `first-class-bounded` (lane/ssbuild3) | 30 / 138 seeded; stage 3 takes 18 / 31 | KNOWN: stage 3 itself; moot on landing |
| L3 | after-level exit table | NOISE | -1.9% (pad spread 0.599 = 20% of orig, 0/7) | **WIN** +6.0% / NOISE | 0 | I13; dir_fwd_skip :7213 | 7 / 7 | generalises [OPT-3-RUNEND] (a) |
| L4 (r3) | skip VM when window is the answer | **LOSS** | +22.8% slower (7/7) | **WIN** +47% / **LOSS** | 0 (r3); r2 had 5,562 | I14 (+ I3 r1); vm_emit_search_body emit_vm.c:12552, :13429 | 5 / 0 | NEW |
| L5 | frameless lazy step | NOISE | -1.0% | **WIN** +21% / NOISE | 0 | I15; vm_cursor_rep lazy arm :4672, :4968, :5011 | <=5 / <=54 | NEW |
| L6 | combo L1 r2 + L3 + L4 r3 + L5 | **WIN** | -95.4% (7/7) | WIN/WIN | 0 | combination (no single idea) | | |

Repairs are 0 on every final A09 twin; window-start differential 342,690 windows, 0 differences. L6 (-95.4%) equals L1 (-94.9%) on the cell: L4's loss is hidden under the L1 skip (§6). L1/L2 are one mechanism at two strengths: stage 3 is the L2 shape and L1's rare-byte streams are the residual; the sources do not measure what is left after stage 3 lands.

## 4. Yield

| measure | A01 | A07a | A07b | A09 | pilot |
|---|---|---|---|---|---|
| counted leads | 4 | 6 | 6 | 6 | **22** (generalize.md says 25, see §2) |
| survive hardened identity (plain and --san) | 4 | 6 | 6 | 6 | **22 of 22** |
| with repairs > 0 (`changes-giveup-surface`) | 0 | 4 | 5 | 0 | 9 of 22 (41%); plus `poss` |
| confirmed cell WIN | 1 | 5 | 6 | 3 | **15 of 22 (68%)** |
| of which clean (no repairs) | 1 | 1 | 1 | 3 | 6 |
| confirmed NOISE | 3 | 1 | 0 | 2 | 6 |
| confirmed LOSS | 0 | 0 | 0 | 1 | 1 |

Reading survival correctly: 22 of 22 counts SEALED final twins. The gate did its work earlier: all 14 sabotage controls (A01 3, A07a 2, A07b 1, A09 8) FAILED as intended (A09 `ctlbnd` only under `--san`); A07b L4 r1 was rejected for a stray file; A09 L4 r2 passed default-buffer identity while answering where the original gives up (284k differences, later 5,562 oracle-equal repairs). The confirmer's identity was 52 of 52 PASS over 26 arms; `--strict-giveup` fails exactly the 10 arms with repairs.

**Distinct ideas.** The 22 leads are 15 ideas. Cell WIN: I1, I5, I6, I7 (stacked), I8 (stacked, shipped), I11, I12; I9 WIN only as stacks (increment unisolated). NOISE: I2, I3, I4, I10, I13, I15. LOSS: I14. generalize.md classes: 4 known with a home (I2, I8, I11, partly I13), 5 generalise a known mechanism (I1, I3, I5, I6, I12), 4 new (I4 as a K88 mechanism, I7, I14, I15), 2 codegen-micro (I9, I10).

**Scratch-vs-confirmed agreement: 4 of 4** where a scratch verdict existed (A07b L1-L4: Mac WIN on all, Linux WIN on all). Magnitudes differ: scratch -20/-45/-53/-72 vs confirmed -22.9/-35.4/-41.6/-70.7, the middle two overstated on the Mac. The other 18 leads had no scratch verdict (A01, A07a, A09 timed nothing). n=4 on one artifact is a sign, not a rate.

**Dual-review overlap on A07 (counted, pilot_index.md).** a: 6 leads = 3 matched fully, 2 partially, 1 unique (counters in locals). b: 6 leads = 3 full, 3 partial, 0 unique. Union of distinct ideas: **7**. Each reviewer alone reached 6 of the 7. Both independently found the three highest-value ideas (word-start filter, dead frames, tables) and the same pitfall class (the step budget moves). The only idea one reviewer alone found, a's counters-in-locals, confirmed NOISE (-0.05% cell); b's restart added about 3 points on its stack. **Measured value of the second reviewer here: no confirmed win.** One artifact whose waste is unusually concentrated, so this may overstate.

**Notebook transfer (charter §3.2).** A09 had 2 of 6 leads of `notebook:` origin plus one fresh lead whose byte choice came from the notebook:

| lead | origin | confirmed |
|---|---|---|
| A09 L4 (skip VM / drop reverse pass) | notebook rvA01 (A01 L3's idea) | **LOSS** cell and sparse, WIN +47% dense |
| A09 L5 (frameless lazy step) | notebook rvA07a | NOISE cell, WIN +21% dense |
| A09 L1 r2 byte choice (O/T) | fresh lead; byte-pick from notebook rvA01 | WIN -94.9% |

Transferred ideas were REAL (each won on the hit-dense subject) but neither became a cell win: both are regime-dependent and the cell is a fail/syslog median. n=2, no transfer rate can be claimed. The one transfer that carried a win was a small detail (which byte to scan), not a mechanism.

## 5. Suggestions, ranked

Ranking = confirmed gain x counted population / cost; populations from generalize.md §3, confirmed numbers from §3 above. All are FILED-not-scheduled [OPTLOOP] candidates (D137); Frank ratifies, D125/D119/D144 select. Row ids are generalize.md's proposals, naming is the manager's call. Draft row text is in generalize.md §4; below is the re-ranked shape with the confirmed evidence.

**Reading the ranking honestly.** On gain x population alone, #2 (reverse-inner, -72% x 17) outranks #1 (possessify arms, -58% x 1). #1 leads because it is by far the cheapest (no new codegen) and the only lead whose entire effect is a gap in an analysis. It must be filed with its real population, 1 bench / 2 corpus (K35), not with A07's -58%.

1. **[ART-POSS-ARMS] (the possessify-analysis gap).** STATE:not-started, FILED from [ARTREV] S5 I6.
   - What: two declining arms of `src/opt/possessify.c` widened soundly: a `\b` follow after a greedy word-pure (subset of `\w` or `\W`) single-class repeat with m >= 1; a backreference's FIRST taken as its closed, non-nullable group's FIRST.
   - Confirmed evidence: the hand-possessified `\b(\w++)\b\s++\1\b` is a **-57.6% cell WIN** (17.39 to 7.37 ns/B, 7/7 pads, dense and sparse WIN) with NO new codegen; frames-only a_L2/b_L2 -34.8% / -35.4%. The shipped emitter then makes the matcher frameless and inline by itself (I8, [CC-DIFF]).
   - Population: 1 bench (`doubled-word`) / 2 corpus (`wordb_vm.rxt:339`, `startset/vmhat.rxt:381`); 7 more DFA-route rows carry an arm where frames are moot. Parser coverage caveat: 56% bench, 37% corpus; the 19 unparsed framed bench VM patterns were hand-checked, none has the shape.
   - **changes-giveup-surface** (one-way: a give-up becomes a correct answer; 5,380 repairs for the frames, 50,168 for `poss`). Needs the one-way spec sentence (tuning.md §2.1, limits.md §7) and a K65-style check.
   - Cost/risk: S / M. Possessify has a refutation history (U1, U2, the lazy conjunct): each arm needs `tests/possessify/run_possdiff.sh` extended and a D6 panel before build.
   - Algorithmic (not codegen-micro). Not moot under stage 3.

2. **EVIDENCE FOR AN EXISTING ROW, not a new suggestion: [ENG-TACTICS] (b) reverse-inner — Frank's row (plan.md, BOONIES tier, unscheduled 2026-09-25), here as a DFA-route instance** (I1, A01 L1). The row was framed around the VM/backref population (K66's witness); what ARTREV adds is a measured DFA-route case and its population. [OPT-A] already records stack-frame's `\bat ` gap (bench O-8). Whether this moves the row out of BOONIES is Frank's call; the build would also be a [MEMFN] request.
   - Confirmed: **-72.2%** cell, 0.455 to 0.126 ns/B, all pads, dense and sparse WIN, 0 repairs.
   - Population: 17 bench (8 at >=8x; `stack-frame`, `uuid`, `iso-ts`, `ipv6`, `orig`, `waf-942160-sleep-benchmark`) / 90 corpus (31 at >=8x). 12 / 50 are already presence-checked by K82 `set-leads`: the emitter knows the byte and uses it only to say no. The 2x bar is an unmeasured default. Hybrids not counted.
   - Cost/risk: M-L / M-H: prefix reverse machine, leftmost-start uniqueness argument (rust's reverse-inner quadratic guard), a deny flag, an abi event. A scan site, so a [MEMFN] request (D146/D147).
   - Algorithmic. NOT moot under stage 3 (A01 byte-identical on the ss3 compile).

3. **A09/CTX's skip: START-SET stage 3 (I11), then the residual [OPT-A] per-alternative rare streams (I12).**
   - Confirmed: the skip is **-94.9%** (L1, rare-byte memchr streams) and **-75.9%** (L2, scalar table, the shape stage 3 emits: `first-class-bounded` with conditional re-seed, verified on the ssbuild3 compiler). CTX is the gap report's rank-2 group (level-context x3.8), 5 bench cells.
   - Stage 3 is the filed row for it; I11 is MOOT as a separate row on landing. The residual is L1 vs L2 on the cell (0.157 vs 0.739 ns/B, hand twin vs hand twin). Stage 3's own output on this cell is NOT measured by ARTREV: re-time A09 on it before deciding the residual.
   - I12's population is 21 bench / 11 corpus but only 3 / 2 are predicted cheaper by the byte prior (the pick is findings data), so file it as a cross-note under [OPT-A] / startset §8 stage 5, not a new row.
   - Algorithmic. This is the pilot's real population story (generalize.md §0 item 4).

4. **[ART-VMCTX-START]** (I5). The START-SET VM hat keeps a leading context assertion as a previous-byte predicate.
   - Confirmed: a_L1 -22.3%, b_L1 -22.9% (two reviewers agree), 0 repairs, dense/sparse WIN; stacks adding resume/restart reach -80.0% / -73.7%.
   - Population: 2 bench (`doubled-word`, `dup-param-detect`) / 1 corpus; both already take `first-class`.
   - Cost/risk: S-M / L-M, an abi event. Same `dfa_pfs[]` table that stage 3 edits: SEQUENCE AFTER stage 3. Whether it still pays on top of #1's frameless form is unmeasured; batch with #1.

5. **[ART-TRAIL-ELIDE]** (I7). Untrailed `RX_SET` where every read of the slot is dominated by a write in the same attempt and no frame is live across it.
   - Confirmed only as stacks: b_L3 -41.6% vs b_L2 -35.4% (+6 points), a_L3 -50.9% vs a_L2 -34.8% (+16 points, but a_L3 also restructures the attempt). Isolated increment not measured.
   - Population: upper bound 66 bench / 1,454 corpus with `RX_SET`; frameless 27 / 623 (where only the dominance fact is needed). The largest population in the pilot and an UPPER BOUND, the dominance fact being uncounted.
   - **changes-giveup-surface** (294,884 repairs = every original give-up in the shrunk run; trail FRAMES give-up gone). Spec hunk limits.md §3.2 / §5.
   - Cost/risk: M / M (a dataflow fact, two `RX_SET` spellings). Algorithmic. Needs its own census of the dominance fact first; ranks after #1, which makes A07 frameless.

6. **I3 / I4 (A01 L3, L4) as notes.** [ART-START-MARK] (L3: dense-only, cell NOISE, subsumed by #2 on A01, pop <=71 / <=389 with uniqueness uncounted) is low priority. I4 is not a row but is the `cnt_pre.h`-style twin K88 asked for: A01 L4 measured NOISE (+8.4% slower, below threshold), so it does NOT support the K88 handoff-cost mechanism on this artifact. Reach 36 / 114. Cross-note under [K88-HANDOFF-DENSE].

7. **CTX trio, HOLD:** [ART-HYB-COUNTED] (I14, LOSS), [OPT-3-RUNEND] (a) generalised (I13, NOISE), [ART-LAZY-FRAMELESS] (I15, NOISE). Each wins on the hit-dense subject (+47% / +6% / +21%) and none wins the fail/syslog cell. Do not build until stage 3 lands (the L1 skip hid them) and a bench cell weights hit-dense text. Populations 5/0, 7/7, <=5/<=54.

8. **CODEGEN-MICRO, flagged (D119 algorithmic-only, not loop leads):** I9 (256-byte tables: only stack evidence, and `form_char_step0.md` recommends against the table form on size) and I10 (counters in locals: cell NOISE, about +2%). Recorded as [OPT-B] cross-notes. I4 is also micro.

9. **No row:** I2 (a statement about exemplar data, not the emitter: `pcrec-analyze --scan freq` over the cell's own subjects already yields `memchr('t')`; never a default-prior change, D83), I8 (shipped, follows #1), I11 (is stage 3).

**Moot or reduced under START-SET stage 3:** I11 entirely (A09 L2's shape); the CTX trio is re-read after it; I5 is sequenced after it (same table). Not affected: #1, #2, #5.

**Cheapest next measurements:** re-time A09 on the stage-3 compiler's own output once stage 3 lands, and time A07's single-member increments (tables, restart, trail) as separate arms.

## 6. What did not work, and why

- **A09 L4 (skip the VM when the DFA window is the answer, r3): +22.8% cell LOSS with a +47% dense WIN.** A real mechanism (hit: reverse steps 12.4k to 0, VM attempts 193 to 0 per MiB) that wins on hit-dense text, but the cell is the median of 12 throughput subjects where the fail/syslog groups set the median; there the added check costs and nothing is saved (confirmer: "regime-dependent"). It would also have been blessed by the combination: L6 (-95.4%) equals L1 (-94.9%) because the L1 skip makes fail/syslog so cheap that L4's cost is invisible. A cell-only gate cannot see a regime-losing member of a winning stack; the dense/sparse rows exposed it. It is a LOSS by the charter rule, not a reason to discard the idea: it needs a hit-weighted cell.
- **A09 L5 and L3: NOISE on the cell, dense WIN +21% / +6%.** Same shape, hit-only. L3's pad spread (0.599 ns/B, 20% of orig, 0/7 pads same sign) says layout alone swings that twin as much as the effect.
- **A01 L2 `memchr('t')` -14.6%, below the 0.084 threshold, stopped at pass 1.** Real but small, superseded by L1; the same effect comes with no emitter work from a findings bundle (I2). A01 L4 (+8.4% slower, below threshold): one redundant `memchr` per call is not measurable here. A01 L3 is a dense-only win.
- **A07 a_L6 counters in locals: -0.05% cell, about +2% dense/sparse/t1m, NOISE.** Consistent in sign, below threshold; the one idea the second reviewer did not independently find.
- **Stack increments the experiment cannot attribute.** Tables (I9), restart (b_L5) and trail (I7) were only measured stacked, so their individual worth is unknown rather than shown small.
- **What the method structurally cannot find.** All 22 leads are work the emitted code does that it need not. None found a missing capability or a wrong tier choice; reviewers were blind to the emitter by design.

## 7. Process findings

The experiment's own value. Each is cited to its lane report.

1. **The `_in` shapes were never driven (fixed).** `arm_compile_cmd` never passed `-DARTREV_HAVE_IN=1`, so the shim exported stubs and the identity driver exercised NO caller-buffer entry (SI/MI/CI/FSI) in any pilot identity run, while the summary line claimed them (artcollect). Every "identity PASS" before the fix was blind to them. Fixed in `common.py`; the summary now prints how many `_in` lines were actually driven (14,912 on A07); all 22 final twins were re-verified. Lesson (learnings §3): a summary that names what it ran must count it.
2. **Identity was blind to give-up behaviour under default buffers (the give-up rule).** rvA09's L4 r2 passed default-buffer identity yet returned a match where the original gives up under 0 frames/trail (284k differences once shrunken resources were driven). The charter now carries THE GIVE-UP RULE: shrunken budgets and 0/1 frames/trail with a libpcre2 oracle; a repair equal to libpcre2 is the permitted direction, a lost or differing answer FAILS. r2 PASSES by default with 5,562 repairs and FAILS `--strict-giveup`; the manager ruled (2026-10-06) that the default rule stands for the confirmer, every row carries its repair count, and leads with repairs are tagged `changes-giveup-surface`. 10 of 26 confirmer arms have repairs. An emitter change built from a tagged lead moves a caller-observable limit and needs its spec hunk (D80) and a K65-style check.
3. **D27 cells were git-readable through the parent repo (fixed).** A cell under `worktrees/` reached the main repo's history by upward discovery (`git -C cell show HEAD:src/...` printed the emitter), so EVERY earlier D27 cell had that leak, guarded only by brief wording (artprep). Fixed in `mk_d27_cell.sh` (empty-repo boundary plus a hygiene check proving both directions; ccb49b0a). Open question: earlier D27 results rest on briefs' honesty, not isolation; this experiment's four reviewers worked in the fixed cells.
4. **Per-cell timing locks (fixed).** The timing lock lived per cell, so reviewers in different cells did not exclude each other, and the suite-lock check resolved under the cell. Now shared via `ARTREV_HOST_ROOT` (selftest 101/101, later 168/168).
5. **Reviewers stalled on unavailable timing.** The Mac sat at load1 28-34 and a suite lock was held by the stage-3 build; the harness refused every timing attempt and no gate was overridden (a correct refusal). A01, A07a and A09 timed NOTHING; only A07b timed (one run, 11 rounds, 3 subjects). The charter's "reviewer iterates with timing" was tested on one lead set of one artifact; the other 18 leads steered on work counts. The harness did its job; the schedule gave it no window.
6. **`ARTREV_REMOTE_CC` exported session-wide breaks local identity.** `common.py` uses it for local compiles too; on the Mac `gcc` is clang, so identity runs failed with "indirect goto" and a first batch was discarded and re-run (artconf). Fixed in `confirm_plan.md`: export it on the remote `time` command only.
7. **Smaller harness findings.** `time`'s `summary.tsv` omitted the layout columns (`confirm_collect.py` added); `run_remote` built its bundle from the raw `--arms` string, not the computed list (fixed); one `orig2` LOSS flake under a gate-overridden load of ~20 (selftest) and one on a dense row of A07 run 002 (re-run 003, all controls NOISE); stacked arms need single-member arms to be attributable.
8. **Cost.** Confirmation took about 21 minutes of box wall (7 timing runs; planned 1 h 15). The gates (pad-shift control, null, `orig2`) held up: 14 sabotage controls failed as intended and A07's re-run CELL verdicts agreed.

### Recommendation for the full run (and the manager's gate decision)

The pilot gate (charter §5) is met on its first criterion. **Manager's decision (2026-10-06, journaled): the full run proceeds** on these terms:

- **Single review per artifact.** The one overlap measurement shows the second reviewer added no confirmed win (union 7 ideas, each reviewer reached 6). Spend the saved budget on more artifacts. Caveat: n=1 artifact.
- **Pin after START-SET stage 3 lands** (R4a′ at abi 63 is already in), so the full-run artifacts are not invalidated: A09 changes under stage 3, A01 does not. Re-pin once, all artifacts at one sha.
- **Batches of 3 reviewers**, launched when a timing window exists.
- **Mac scratch timing only when the suite lock is free** and load is under the gate; schedule reviewers into a window rather than overlapping stage-3 or `make test` runs; consider a by-day Linux slot so the reviewer's iterate-and-time loop is real.
- **Isolate stack increments:** have the reviewer seal single-member twins so S4 can attribute them.
- **Add a hit-weighted or dense cell to the gate** for hybrids: A09's L4/L5/L3 regime split would otherwise be invisible or mis-blessed (L6 hides L4's LOSS).
- **Stratify winners and near-ties** in the full run; the pilot reviewed only losing cells.

Report text composed by lane `artrep` (returned as text; written to the tree by the manager after a permission rule blocked the lane's file write).
