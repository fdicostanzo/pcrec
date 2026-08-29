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
| C1 | **MISSING-OBLIGATION (blocks merge; proved from the commit graph, not by a run)** | `run_recursion_identity.sh:382` FILEPIN=60a51ed, but two LATER src-touching commits change emitted whole-file bytes: 5199823 (`#define <P>_MAX_EMIT_BYTES` on every DFA artifact) and b3cf716 (rx_info capacity fields) — D76's "the pin is the commit that introduced the CURRENT scaffolding; byte-exact whole-file within an abi" means comparison (B) against a 60a51ed reference should report every DFA-selected pattern differing, unless the D37 stamp-strip absorbs the line. The fourth-site miss recurring one lane later, on the same site | SENT BACK → run the gate at HEAD; re-pin to the last src-touching commit and re-run to 0 differing, OR name the filter line that absorbs the two commits' bytes |
| C2 | GAP (D80) | `docs/spec/tuning.md` has two `### 2.15` headings (:737 `-fno-anchored-dfa`, :1005 `-fno-size-term`), the new one placed after §3/§4 with a stale TODO (:1031-1033); the note's §7.2 promises a §2 count sentence ("fourteen → fifteen") that does not exist | SENT BACK → §2.16 in bit order, TODO removed, the count sentence written or §7.2 corrected |
| C3 | HOLDS (measured) | registry 67 and `--list-axes` 47 rows / 19 axes reproduced by running the read-only check and the binary; the count is derived (`grep -c '^PASS: '`) | none |
| C4 | HOLDS (measured) | D81: VM artifact carries all four stamps; DFA artifact carries `_MAX_EMIT_BYTES` only; `.abi = 11` at `emit_dfa.c:1310`, ABI_EXPECT=11 at `run_codegen_tests.sh:2707` | none |
| C5 | HOLDS | `m6read_check_sab_anchors.py`: 189 sabotages / 200 sites, all resolve (S191-S193 included) | none |
| C6 | HOLDS | known_issues.md K41 "RE-SCOPED, NOT CLOSED" consistent with the shipped fuzz EXPECT array (`run_capturediff_gate.sh:161-179`: oversize 0, emitted-size cap 1, both-accept 182, pairs 2,730, inconclusive 3), derivation shown in-file; the gate itself not re-run by the critic | none |
| C7 | HOLDS | size log: exactly 3 more rows than main, all traced to `tests/size/size_term.rxt:32,41,55`; tripwire pins byte-identical to main's | none |
