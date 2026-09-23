# EXECUTIVE SUMMARY — the optimization loop, cycle 1 end to end (2026-09-23)

Published page: https://claude.ai/artifact/6my3pgvehYA3J3aNkZvpHp (2026-09-23; private; the file below is the source of record).

For Frank. Cycle 1 of D119's loop ran 2026-09-21 → 2026-09-23 on pcrec-bench's
`capability@0.1`: analysis, Linux profile pass, a batch of three mechanisms,
and the bench's after-measurement. Numbers cite sources.

## 1. FINDINGS

The analysis ranked all 128 cells at pin `25b1984f` and found five mechanisms
covering 78% of the loss (`docs/dev/optloop/cycle1_analysis.md`).

| mechanism | class-weighted score | target rows |
|---|---|---|
| [OPT-REQBYTE] necessary-byte pre-check | 3.714 | 5 |
| [OPT-ANCHOR-VM] VM attempt-loop start bound | 2.112 | 2 (+3) |
| [OPT-FIRSTSET] AST-derived candidate-start set | 1.002 | 4 |
| [OPT-ENDWIN] end-anchor start window | 0.871 | 1 |
| [OPT-ATTEMPT-SPLIT] `^` on some branches | 0.306 | 2 |
| **union** | **8.005 of 10.284** | 14 |

The apples-to-apples re-ranking (`cycle1_caps_view.md` §4-5) confirmed all
five move under 2% when pcrec's side is pinned to the shipped default, which
wins or ties **84 of 123** cells against capture-bearing engines, and named
the largest un-mined population in the matrix: 14 rows, score 4.6833, all
`RX_ENGINE_WHY "capture group"`. The Linux profile pass (`cycle1_profile.md`,
12 transcripts) confirmed [OPT-ENDWIN] cleanly and the other four partially,
and is why [OPT-FIRSTSET] was swapped out of batch 1. Lane `optimpl1` then
shipped three mechanisms as three axes, one `abi` 28→29 event; the
after-measurement is O-45 and its ledger
`2026-09-23-optloop1-batch1-after-8d716693.md`. Read per mechanism
(`docs/dev/optloop/cycle1_ledger_reading.md` §2):

**39 of 41** named target rows meet the D119 bar and 5 of 5 stamp expectations
are confirmed by value; the two misses are `router-prefix-order` on the DFA
route, +1.19% / +1.21%.

| mechanism | D119 verdict |
|---|---|
| **[OPT-ANCHOR-VM]** | **MEETS** — 13/13 targets, no attributable regression |
| **[OPT-ENDWIN]** | **MEETS** — 4/4 targets |
| **[OPT-REQBYTE]** | **targets meet, carve-out clause FAILS** — 12 cells regress 18.7-38.5% |

## 2. SURPRISES

**A. Sixteen "regressions" have no code change at all.** Compiling all 64
patterns at both pins in all three flag sets, **56 of 187 artifacts are
program-identical** across the pin, and 16 of the ledger's 64 non-named
regressing cells sit on them — the worst being `phone-palindrome-6`
throughput, **6,585,254 → 7,142,400 ns, +8.46%, 35× its own IQR**, whose
compiled `__text` is byte-identical by md5. D119's bar uses a cell's
within-window IQR as its noise model, but the comparison spans two windows a
day apart. Re-read against that null band, **the ledger's "64-cell everyday
regression population" is 14 cells**, and the two misses sit inside the band.
Independently confirmed by the Linux executor (O-48, [B78], on the box that
measures the ledger): the null band is **two-sided** — 120 program-identical
cells, min −5.74%, max +8.46% (matching this file's own worst cell to four
significant figures), median −0.08%, 41 regressing / 79 improving — so a
claimed IMPROVEMENT of less than roughly that magnitude is equally inside
the noise. No verdict in this file turns on an improvement that small.

**B. The pre-check is emitted above the free check that decides the call.**
Nine patterns are `^`-anchored: the artifact emits `const size_t start_max =
0` and runs one attempt, and the whole-window `memchr` sits **59 lines above**
that line. `winpath-near-miss` went **20.1 ns → 23,123.6 ns**, a 1,150×
regression to the same answer, because its required byte `\` occurs **zero**
times in the 1,376,256 bytes of throughput subject. The declining rule is
already in the emitter (`src/gen/emit_dfa.c:2999`, for the prefilter) and the
new check did not inherit it. 29 cells.

**C. One artifact runs the same `memchr` twice.**
`wild-codegrammar-json-array-begin` is `\[`; its emitted C calls `memchr(…,
91, …)` at line 49 as the pre-check and at line 107 as the prefilter (+32.5%).
On `router-prefix-order` the pre-check's byte is 1.85× **commoner** than the
prefilter's, so it can dismiss nothing.

**D. Four regressions are 111× to 60,674× larger than the mechanism's own
work, and the proposed cause does not hold on the box that measures.**
`nested-comment-rec`'s pre-check reads 1,051 bytes in 3 calls (≈25 ns); the
cell regresses **+1,528,965 ns** on a four-line diff. The arm64/gcc-16
reading attributed this to gcc losing a partial-inlining split of
`rx_search_run` (the function holding the attempt loop) on 24 of 62
forced-VM artifacts. **The Linux executor's disassembly (O-48, [B78])
REFUTES this on gcc-15.2/x86_64 — no `.part.0` symbol exists at EITHER pin,
on any pattern** — and it does not confirm the next-ranked hypothesis
either (an x86_64-specific inlining/frame effect: `rx_match_anchored` is
out-of-line at both pins, the stack frame is flat 104 B at both pins). The
regression is **unattributed** as of this writing
(`docs/dev/optloop/cycle1_ledger_reading.md` §9); a driver-level
acceptance test is drafted (I-98) to settle it.

**E. [OPT-FIRSTSET] is unsound as ratified and the symptom is a deleted
match** (`firstset_design.md` §4.6): 4.03M subjects, **552 lost, 0 spurious**;
the repair already ships as `pf_emit_ofs_reseed` ([OPT-K]).

## 3. IMPACT

Eight named pathological patterns fell from 1.28-20.1 million ns to
23,100-89,500 ns on all four configurations; `bracket-array-define` to 72-90
ns, `trim-nested-star` −99.9986%. Size grew +200 to +334 bytes per artifact.
Every regressing cell was attributed at reading time (§4-5); one class is
now **unattributed** pending a driver-level re-measurement (§9):

| class | cells | fix |
|---|---|---|
| pre-check on a one-attempt route | 29 | one predicate |
| duplicated / dominated pass | 4 | one comparison |
| code-generation perturbation | ~4 | **unattributed (placement mechanism refuted on x86_64, O-48; §9)** |
| inside the null band | 50 | not attributable |

**Recommended dispositions, yours to rule:** [OPT-ANCHOR-VM] and [OPT-ENDWIN]
**default-on as shipped**; [OPT-REQBYTE] **default-on with the admission
fix**. A `--tune` position is the wrong instrument for the third — its losses
are an admission defect with a one-predicate fix, not a size/speed trade, and
parking it forfeits the loop's largest win.

## 4. NEXT STEPS

**Proposed as cycle 2's first row, [OPT-PRECHECK-ADMIT] — SCOPE NOW G1+G2
ONLY.** G1 (decline where the artifact already filters on a byte at least
as rare) and G2 (decline where the candidate-start set is a single
position) stand: they rest on this file's own arithmetic, not on the
refuted placement claim. **G3 (emit the VM's check in the entry wrappers)
is DROPPED from this row pending the driver-level measurement** — O-48
refutes its stated mechanism (the arm64/gcc-16 partial-inlining loss) on
the gcc-15.2/x86_64 box that measures the ledger, and Block C's own
disassembly does not confirm the next-ranked hypothesis either (reading
§9). G3 may still be worth landing as a byte-identity DISCIPLINE (its own
acceptance criterion), but not yet as a claimed performance fix.

| already in flight | state |
|---|---|
| batch 2, [OPT-FREQPICK] + [OPT-REQPOS] 2b, `abi` 29→30 | built, parked on `lane/optimpl2`; `router-prefix-order`'s miss is a live case for the freq pick |
| [OPT-FIRSTSET] | reconciled, repair identified, awaiting a cycle-2 slot |
| `utf8` subbench (I-90) | requested of the bench; the byte-frequency prior is inverted under UTF-8 and has three readers |
| [PATFACTS] (D120) | chartered; inventory in cycle 3's measurement waits |

**I-91 (§8) is ANSWERED — O-48, [B78], 2026-09-23, reconciled at
`cycle1_ledger_reading.md` §9.** Every EXPECT direction held on the axis
isolation; the null band came back two-sided; the partial-inlining
mechanism was REFUTED on the box that measures; the placement hand-twin
did not resolve on its own instrument. A follow-on block (I-98 candidate,
§9(D)) re-runs the hand-twin under the bench's own driver rather than the
hand-rolled `findall.c` instrument.

**One ask of the bench beyond measurement — MET.** O-48 already carries a
two-sided null-control band from the program-identical population (§9(B)
above); a standing per-report NULL-CONTROL BAND, and stating D119's bar as
|Δ| > max(IQR, null band), remains the ask for every future `capability`
report.
