# checks — memfn-s2a
## Findings

### CHECKS-1 (CONFIRMED, maintenance, effort: one fixture line, radius: tests/knowledge only)
The loader's upper noise bound has no boundary witness: nothing asserts that noise_e6 == 10^15 LOADS
(measures.md §2.2¶3a "at most 10^15"). f2-noise-bound uses 10^15+1 only; fx-f2's noises are 1730 and 0.
Repro: hand-plant src/core/ks_measures.c:384 `m->noise_e6 > KS_MEAS_MAX` -> `>= KS_MEAS_MAX`, build per COMMON,
`PCREC=<planted> run_measures_tests.sh`: rc 0, 0 FAIL (SILENT; 91 pass, same as baseline). The kit side has the
boundary (g2_gen.c "MEASURED MF_MEASURE_MAX" accepted) but the loader side, which S2907 and S2910 guard, does not.
Fix: an ok-fixture row (or a pair) with noise 1000000000000000, or a `LOADS` row in the refuse loop. Likewise
there is no `fitted`-row-with-noise fixture (§7 names it; only derived and null are witnessed), though one
shared branch (ks_measures.c:387) serves all three, so that part is low.

### CHECKS-2 (CONFIRMED, maintenance, effort: tighten a literal, radius: run_measures_tests.sh)
The refusal-population floor has slack of one, and "6 of them format 2" is a comment, not a check.
run_measures_tests.sh floor is `nbad -ge 26`; mfixtures.py currently emits 27 (21 f1 + 6 f2).
Repro: copy of mfixtures.py that drops one class (f2-events, then separately cr) from bad/ + EXPECT.tsv:
rc 0, 0 FAIL (SILENT). Dropping two: red "25 classes, under the floor 26". So one deleted refusal fixture
(including a format-2 one, i.e. an unwitnessed §7 class) goes unseen. Fix: floor 27, or a separate `f2-*`
count == 6 (the other floors, ok = 6 and pairs = 2, are exact and DID go red on delete and invent).
Invented bad fixtures pass by design of `>=` (acceptable).

## PROBED-AND-HELD
Field validation: `VALIDATE_ONLY=1 run_sabotage_matrix.sh` on S2900..S2910 and S1232 (13 rows): all FIELDS OK; and
my hand plant applied every anchor with exactly one occurrence (S2900-S2910, S1232, 12 plants). (The
m6read_check_sab_anchors.py derives its root from the MAIN tree's scripts/, so it does not read the review tree; not run.)
Hand-built plants, classified (all LOUD, none SAME/SILENT-MOVE), detector line that went red:
- S2900 LOUD (4): "format-2 fixture store ... did not build/run" (ksgen refuses), "fx-f2: does not load ... values_digest ... but the rows hash to", pair fx-f2-class, pair fx-f2-noise.
- S2901 LOUD (4): same four lines.  S2909 LOUD (4): same four lines.
- S2906 LOUD (4): fx-f2 R1, R2, R3, "canonical view does not load as --measures=FILE".
- S2907 LOUD (1): "refuse f2-noise-bound: the set LOADED" (only one detector line; guarded by CHECKS-1's sibling gap, not a defect).
- S1232 LOUD (6): store zen4-grid1@1 R4, fx-f2 R3, fx-rich R1/R2/R3/compile.
- S2908 LOUD (1, via shadow tree with planted scripts/ksgen.c): "format-2 fixture store: the pre-parse differs from a fresh parse ... noise_e6 0/-9223372036854775808"; the committed-store embedded check stays green under it (as the row states; the fixture store is the detector).
- S2910 LOUD at compile: meas_store_check.c:40 "static assertion failed" with KS_MEAS_MAX=10^16; unplanted control compiles. The TU is built by run_measures_tests.sh (both the committed-store and fixture-store compile), whose failure goes `bad` and the trailer still prints; run_knowledge_tests.sh:237 folds it in. It fails the CHECK, not `make` (designed).
- S2902 LOUD (trace harness, (C) reproduced by hand): fx-f1noise got 3/31a7fa43... want 0/5e21380e...
- S2904 LOUD: fx-f2 got 0/a94e50eb... want 2/a9057c4f...   S2905 LOUD: fx-f2 count 2 right, digest 5c870ffa... vs a9057c4f... (the digest, not the count, catches it, as the row says).
- S2903 LOUD (g2_gen.c built against planted libpcrec.a, --gate-only 1): api_fail=2 ("zero-initialized (UNSTATED)", "state 3"); control api_fail=0; refusal_table runs under --gate-only (g2_gen.c:4764). Accepted-row cases (MEASURED 0, MEASURED max, UNMEASURED 0) prove a refusal is for the noise state alone. Message text is not checked (acceptable given the accept cases).
Independence: ks_ref.py shares no code with ks_measures.c; constants (domain pcrec-meas-2, unit/status codes, 10^15) are spec text; mfixtures.py digests via ks_ref (not the C), so fixtures' digests are not C-produced; (C)'s expected count/digest come from `ks_ref.py handed` over the FILE, and the MFMEAS side is computed by memfn_sites.c's own trace code. fx-f2 witnesses the handed filter: a null row, a pcrec. row (noise 25), a derived row and an unmeasured-value row are present; measured count 2 incl. a measured noise 0; rows are in non-canonical file order so the sort is exercised.
Floors: ok fixtures = 6 and pairs = 2 are exact: deleted fx-f2 -> red ("5 fixtures"), invented ok -> red (7), deleted pair -> red (1), invented pair -> red (3). run_part_measures floor 16 = 7 x 2 arms + 2, exact.
Spelling probes on the loader (12): noise "05", "", "1e3", "-0", "+5", events "", "03", "-3", fitted row noise 5: all refused with the right text; noise 10^15 and a fitted row with "-" load; a format-1 set with `med` round loads.
zen4-grid1@1 canonical and decoded views: BASE vs SUBJECT byte-identical (2 pairs).
Deliberately unexercised: the mech tree's `make gen-measures` regeneration for S2908's second leg (needs make).
