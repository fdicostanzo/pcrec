# r42 — D6 close panel on the DELIVERED [ART-SIZE] STEP 2 (lane/artsize3 967a2f1: the emitted-size term — K ladder as attempts, two exact size caps, the declared-capacity floor, seven-value stamps), before merge

Three read-only critics, no make: critic-sem (opus; answer identity
under the term's K, the attempts mechanism's state, the caps' exactness
and the abort, the capacity floor, the retry composition with [SEL-1],
acceptance changes beyond the listed seven — pending), critic-checks
(sonnet; abi 11's four sites, D80/D81, derived-vs-spelled counts, the
ksweep gate's exclusions, the fuzz `size_cap` bucket, S191-S193, the
size log — pending), critic-meas (sonnet; the witnesses' figures, the
term's cost on ordinary compiles, threshold/cap headroom on the final
tree, size_diff's three values, the census, the floor's 69/0, the bench
survey — pending). Opened 2026-08-29 ~08:1x EDT, forty-fourth session.
The design was paneled at r40 (three revision passes + a focused
re-check); this panel reviews the CODE and the as-built note. Merge
waits on it; the union battery follows the merge; I-17 follows the
battery.

## Delivered (lane report, 2026-08-29 ~08:1x)

52 commits over main; tree clean. Post-change `make -k -j12 test`
27/27 sections, 1,747 checks / 2 failed (both the lane's own, fixed:
[K37] the ksweep gate's unbounded probe → `pcrec_run`; [SABANCHOR]
S191's anchor moved by the floor → re-derived), 29 case reds = the
counterk load cell (solo 1,634/0); strict clean; run_codegen_tests
106/0; run_size_term.sh 28/0; test-ksweep PASS rc 0 (22,114 cases per
rung, 0 mismatches, 5 excluded give-up cells all explicit-`--unroll`
flips, 0 on term-built patterns; 8 explicit-K refusals explained by a
size/node limit; 18 interior optima, all K=2). Seven departures from
e72b57d, all recorded (§11, §3.3a): ladder as attempts; post-emission
scan; total cap on both engines; counter-rung gate; code-bytes
threshold; bit 18; the declared-capacity floor (`capacity-declined`,
the seventh stamp value; 69 corpus patterns with K-sensitive capacity,
0 on the counter rung; a synthetic witness through a threshold-lowered
compiler reads `K=8 why="capacity-declined" subject_ceiling=43`).
Acceptance: seven tree-side changes (three resource shapes + K41
witness 2 refused, the K22 tower refused, witness 1 87,118 B); bench
survey 54 emits / 54 accept / 0 K movements. Fuzz pins from a run:
both-accept 182 / both-reject 117 / K41 oversize 0 / emitted-size cap
1 / pairs 2,730 / inconclusive 3. Registry 67; abi 11; `--list-axes`
47 rows / 19 axes (corrected from a from-memory 71/42 — provenance
stated in §7.3). size_diff on the quiet log: −227,281 ×1 / +34 ×1,185 /
+128 ×1,689, +0.23 %. Mech: S191 sizeterm 1fail/27pass, S192 sizeterm
1fail/21pass, S193 resource 7fail/19pass + sizeterm 17fail/3pass +
corpus 21fail/0pass — all DETECTED. Recorded debt (§11.3): the
byte-identity-against-explicit-`--unroll` control (the lane asserts the
stamped K matches the artifact; critic-sem measures the stronger claim).

## critic-checks — findings and triage

| # | severity | finding | disposition |
|---|---|---|---|
| C1 | **MISSING-OBLIGATION (blocks merge; proved from the commit graph, not by a run)** | `run_recursion_identity.sh:382` FILEPIN=60a51ed, but two LATER src-touching commits change emitted whole-file bytes: 5199823 (`#define <P>_MAX_EMIT_BYTES` on every DFA artifact) and b3cf716 (rx_info capacity fields) — D76's "the pin is the commit that introduced the CURRENT scaffolding; byte-exact whole-file within an abi" means comparison (B) against a 60a51ed reference should report every DFA-selected pattern differing, unless the D37 stamp-strip absorbs the line. The fourth-site miss recurring one lane later, on the same site | SENT BACK → run the gate at HEAD; re-pin to the last src-touching commit and re-run to 0 differing. **CONFIRMED BY THE LANE'S RUN (logs/recid1.log, 08:19): `[default] (B) whole-file vs 60a51ed: same=1268 differing=952` (the DFA-selected patterns carrying the post-pin `_MAX_EMIT_BYTES` line); `[vm]` 2225/0.** Re-pin in progress; the D76 lesson goes in the gate's header: the pin moves with the LAST scaffolding change of the abi, not the first |
| C2 | GAP (D80) | `docs/spec/tuning.md` has two `### 2.15` headings (:737 `-fno-anchored-dfa`, :1005 `-fno-size-term`), the new one placed after §3/§4 with a stale TODO (:1031-1033); the note's §7.2 promises a §2 count sentence ("fourteen → fifteen") that does not exist | SENT BACK → §2.16 in bit order, TODO removed, the count sentence written or §7.2 corrected |
| C3 | HOLDS (measured) | registry 67 and `--list-axes` 47 rows / 19 axes reproduced by running the read-only check and the binary; the count is derived (`grep -c '^PASS: '`) | none |
| C4 | HOLDS (measured) | D81: VM artifact carries all four stamps; DFA artifact carries `_MAX_EMIT_BYTES` only; `.abi = 11` at `emit_dfa.c:1310`, ABI_EXPECT=11 at `run_codegen_tests.sh:2707` | none |
| C5 | HOLDS | `m6read_check_sab_anchors.py`: 189 sabotages / 200 sites, all resolve (S191-S193 included) | none |
| C6 | HOLDS | known_issues.md K41 "RE-SCOPED, NOT CLOSED" consistent with the shipped fuzz EXPECT array (`run_capturediff_gate.sh:161-179`: oversize 0, emitted-size cap 1, both-accept 182, pairs 2,730, inconclusive 3), derivation shown in-file; the gate itself not re-run by the critic | none |
| C7 | HOLDS | size log: exactly 3 more rows than main, all traced to `tests/size/size_term.rxt:32,41,55`; tripwire pins byte-identical to main's | none |

## critic-meas — findings and triage

| # | severity | finding | disposition |
|---|---|---|---|
| M1 | WRONG-NUMBER (the standing hazard) | the size log at HEAD 967a2f1 is a LOADED-RUN SUBSET: ff327c5's full `make test` regenerated it to 2,877 rows, dropping `counterk.rxt:1807` (the load cell); c41225d's quiet log (2,878) is what the report describes — on HEAD the diff is +128 × 1,688, not 1,689 (byte effect ~0.0002 %) | SENT BACK → restore c41225d's log or regenerate quiet; report/note figures = HEAD's |
| M2 | NIT | the three witness figures (87,118 / 1,718,425 / 670,650) measure +130-137 B each on the delivered binary (87,251 / 1,718,562 / 670,780) — a stamp/comment grew after the note's measurement | SENT BACK → re-measure at HEAD, state the cause |
| M3 | HOLDS | witness 1: K=1 `size-model`, 0.62 s wall / 30.4 MB RSS (lane 0.78 s / 30 MB); `-fno-size-term` still REFUSES (code cap, no file written) — caps non-deniable | none |
| M4 | HOLDS | witness 2 refused by the code cap at every K; total 1,220,606 vs main's 1,220,605 (size_count.sh's own 1-byte rounding) | none |
| M5 | stale text | §2.2b's R1 illustration "K=8 COMPILES (N=118,098)": under the caps explicit `--unroll=8` is REFUSED by the code cap (53,100,981 B); the default compiles via K=1; `--unroll=6` refuses on nodes as quoted | SENT BACK → rewrite to the shipped behaviour (the longjmp argument stands) |
| M6 | GAP (reproducibility) | the 6-deep `{17}` worst-rung tower's pattern text is not archived; the critic's reconstruction (24,295 B / 0.48 s / 70 MB) ≠ the note's (42,619 B / 0.75 s / 64 MB) | SENT BACK → archive the exact pattern |
| M7 | HOLDS | ksweep2 census: 18 interior optima all K=2, excluded 5 / term-caused 0, explained refusals 8, rc 0 — exact | none |
| M8 | HOLDS (partial) | the synthetic floor witness: subject_ceiling 43 (K=8) → 23 (K=1) exact; the 69-pattern population and the `capacity-declined` reference-build demo not reproducible read-only | none |
| M9 | HOLDS | bench survey re-run read-only: 54/54 accept, 0 refusals, 0 K moves, largest 76,304 B, level-context 22,905/22,905/22,829 — byte-for-byte (a first-pass awk miscount self-caught) | none |
| M10 | HOLDS | `--list-axes` 47 rows / 19 axes exact | none |
| M11 | GAP (critic's) | registry 67 not located read-only — critic-checks C3 reproduced it | closed by C3 |
| M12 | **HOLDS — the cost story** | 14 below-threshold corpus patterns × 150 compiles, abi 10 vs 11: no detectable delta (~1 ms baseline); the corpus's largest above-threshold pattern: 11.7 → 54.5 ms per compile (+43 ms, = the note's §3.3 in-process table) | none |

## critic-sem — findings and triage

Read-only; two reference compilers built with plain gcc into scratch
(the `-D` shape of run_size_term.sh §5/§7 — the only way to reach
cap-rescue and the floor); load ≤ 2.7.

| # | severity | finding | disposition |
|---|---|---|---|
| S1 | **CONTRACT-CHANGE** | compile.c:613 `3 * max_emit_bytes` in uint64, no overflow guard: `--max-emit-bytes=6148914691236517206` (ULLONG_MAX/3+1) wraps the ladder's scratch bound to 2 → every trial aborts at its first append → the term falls through to K=8 → the code cap REFUSES a pattern that compiles with no flag (limits.md §8 promises a raise can never do that); `=18446744073709551615` compiles again (wrap, not magnitude) | SENT BACK → saturate; a cell: a raise past ULLONG_MAX/3 still compiles what the default compiles |
| S2 | **CONTRACT-CHANGE** | compile.c:451-464 cap-rescue loop `for (i = n-1; i >= 0; i--)` over [8,6,4,3,2,1] is K ASCENDING — takes the SMALLEST fitting K against its own comment "Prefer the LARGEST K that fits"; measured on §5's witness under the 30,000-cap reference build: chose K=1 (25,271) when K=3 (28,907) and K=2 (27,711) fit; §5 asserts only `rk != dk` | SENT BACK → fix the direction; §5 pins the chosen K |
| S3 | GAP | the early abort is armed on `csb` only; emit_vm.c:7417 emits the whole VM program into `job->vmsb` (never armed) and splices it at :9132 — a trial builds the entire worst-rung body unbounded (K=6 alone 92 MB peak / 35.5 MB artifact; the ladder run 64 MB — the note's own number read the other way); §2.2c's "the ONE place a buffer grows" is true of csb only | SENT BACK → arm vmsb on the same line; re-measure; correct §2.2c |
| S4 | GAP (recorded) | the floor is VACUOUS on artifacts with `subject_ceiling` unset and `frame_capacity` at the stamped default (both compare +inf/equal): 22 such artifacts, exactly ONE with the counter rung (`^(?:(\((?:[^()]|(?1)){1,9}\))(x(?1)y)){0}(?2)$`); NO live defect (0 of the 121 artifacts whose RX_FAST_FRAMES/TRAIL move with K have the shape; 0 of 1,997 lose a declared ceiling across K); §7b pins a different quantity and reads 0 for a population that is 1 | note states the blind shape; §7b pins that population too |
| S5 | GAP | run_size_term.sh §6's natural cap-rescue ceiling scans `sort -u \| head -400` — a fixed 20 % prefix; 10 of the 37 patterns the term acts on under a lowered threshold are past the cut (m6read_samples' `head -n N` lesson) | SENT BACK → whole corpus, emit-only |
| S6 | GAP — the one-token bug nothing detects | MATERIALITY 75 (compile.c:449) is pinned by nothing: at the shipped threshold only two tree patterns run the ladder (ratios 0.212 / 0.051), so 60/80/85 all leave `make test` green; and §3.3's "nothing in between 0.376 and 0.913" is FALSE on the shape family — under a threshold-1000 reference build the 37 moved patterns (17 K=1, 20 declined) form a CONTINUUM with mass AT the bar (0.740/0.745/0.745 taken; 0.751/0.765/0.768/0.770 declined): the "population you chose" mistake in the one place it still stood | SENT BACK → §3.3 withdraws the separation claim, states the continuum; §5's reference build pins the bar from both sides |
| S7 | NIT | trials stamp a 7-char why, the final up to 19: the ladder selects on figures 3-12 B smaller than what the caps check — a rung within 12 B of a cap can be chosen and then refuse; the identity assertion's subtraction is sound (the literal occurs exactly once) | recorded; add the max why-length to trial figures or state it |
| S8 | NIT | COMPILE_MAX_ATTEMPTS = 8 is exactly tight — a live DFA → SEL-1 fallback → 5 rungs → final path uses all 8; exhaustion returns -1 with err->msg cleared (a refusal with no diagnostic) | SENT BACK → assert non-exhaustion with a diagnostic |
| S9 | NIT | the caps count the `.h` when the split form is requested (~97 B, witness 2 1,220,606 vs 1,220,703) — a pattern within ~100 B of the total cap is accepted one way and refused the other | limits.md §8 says so |

**HOLDS, measured.** Re-emission identity in the STRONGER form (§11.3's debt): shipped artifact vs a separate `--unroll=<chosen K>` compile, why-literal substituted — 0 diff lines on 7/7 (witness 1, the nested witness, `((a)|ab){0,2047}c`, `{4000}c`, `((a)|bc){0,4000}d`, `(((?:a{0,2}b)+c){0,20}d){0,20}e`, `((a)|ab){0,12}c`). Answers under the term's K: the nested witness K=1 vs K=8 identical on 4,365 subjects (rc + every capture slot); all 17 patterns a threshold-1000 build takes to K=1, both ways, 67,677 cells, 17/17 identical; `.subject_ceiling`/`.frame_capacity` identical between term-chosen and default builds on all 37 moved patterns. [SEL-1] composition: three constructed overflow patterns (`a{65535}(?:[^q]{1,2}b){0,60}` → `RX_ENGINE_WHY "dfa overflowed: …"` + `_UNROLL_K 1 size-model`; two more → `size-model-declined`) — engine first, ladder on the fallback's VM, both stamps true; the ladder can never trigger the fallback (`st_phase == ST_LADDER` tested before `retry`). Caps: a python reimplementation of `emit_size_measure` == `size_count.sh` == the refusal-quoted figure TO THE BYTE on both engines incl. the one-line jump-table form (`a{0,25000}` 1,103,598 ×3; `[a-z]{0,30000}` 1,323,602 ×3); `--emit-main` excluded by construction (cli appends `main()` after `pcrec_compile` returns); the abort armed only in ST_LADDER (cx memset / job calloc per attempt); refusal writes NO file; below-default overrides refused as malformed; `--max-emit-bytes=2000000` re-accepts; `-fno-size-term` never reaches the caps (witness 1 under it REFUSES at 1,718,553 code bytes). The floor: sentinels +inf in the right direction; applied to the argmin AND the rescue; the argmin runs over the ADMISSIBLE set (an excluded intermediate rung does not veto a lower admissible one — §8a rule 2 as a filter); `capacity-declined` only when the unrestricted argmin is the removed rung; the §7 witness → `K=8 capacity-declined subject_ceiling 43` against a sweep 43/42/41/40/38/23. Seven stamp values each reachable only by its own path (compile.c:885-892 a total order over disjoint predicates); natural population of the last two on shipped caps 0 of 1,997. Acceptance: 2,002 emits under both binaries — exactly FIVE changes, all abi 10 accepts → abi 11 refuses on the TOTAL cap, all in §4.3a's declared class (`(a|b){0,30000}`, `[a-z]{0,30000}`, `a{0,25000}`, and the note's own exhibits `a{1,25000}`, `a{1,31000}`); ZERO corpus patterns; the K22 tower passes because run_vm_tests.sh:538 raises the caps itself. Method note: the critic's own bare `sort -u` under en_US.UTF-8 merged 634 of 2,002 patterns (K35/R24 M-F1 again).

## Manager's disposition — MERGE AFTER THE FIX COMMIT + a focused re-check

No answer changes; two one-line contract bugs (S1, S2), the abort on
the wrong buffer (S3), a fixed-prefix ceiling (S5), an unpinned bar with
a false separation claim (S6), a silent exhaustion (S8) — all sent to
the lane 2026-08-29 ~08:4x together with critic-checks' C1 (re-pinned
to b3cf716, three axes 0 differing, fourth finishing) / C2 (landed) and
critic-meas' M1 (the loaded-run size log) / M2 / M5 / M6. critic-sem
re-checks S1/S2/S3/S6 on the fix commit; then merge → union battery →
I-17 (nothing moves on the bench).
