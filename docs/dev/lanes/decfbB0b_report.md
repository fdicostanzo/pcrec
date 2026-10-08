# decfbB0b report: B0 items 6 and 11 (branch lane/decfbB0b, off lane/decfbB0)

No change under src/, cli/, lib/ (`git diff lane/decfbB0 -- src cli lib` empty). Validation COMPLETE.

## Item 6: tests/prefilter/run_prefilter_tests.sh §7b (NEW rows; the 3 exists rows kept)
All with `--features all`; every value re-probed against the built compiler.
- backref/NONE `(a)\1` -> no-backreference; linked-call `(a|b(?1)c)+` -> no-linked-call
- var-nullable `^${v}$` and nullable-exact `(a*)*` -> no-nullable-exact
- nullable-collapsed/SEL1 `(?:ab){0,16000}` -> no-nullable-collapsed
- overflow-drop NONE and (`-fno-prefilter`) SEL1 `^(?:(?:a|b)*a(?:a|b){20})?$` -> no-dfa-overflow
- forced-on/SIZECAP `-e utf8 -fprefilter ^(\p{Xwd}{1,3})?$` -> yes-collapsed
- forced-off/SIZECAP `-e utf8 (\p{Xwd})` -> no-fno-prefilter
- var `a${v}b` -> no-engine-vm; with `-fno-prefilter` -> no-fno-prefilter (order)
- default-on NONE `(a)b` -> yes; SEL1 `(1{0,30}?[^]abc][^abc]){28,30}0+|a` -> yes-collapsed
- default-off `--engine=vm (a)b` (with --features all) -> no-engine-vm
- DFA route `abc`: rc != 0 and refusal names the DFA engine
- default-on/SIZECAP: lowsize reference compiler built once in the script (`-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000 -DPCREC_MAX_EMIT_BYTES=60000 -DPCREC_SIZE_TERM_THRESHOLD=10000`, source list via lib_srcs.sh, hard-fail on empty list) `(?:a\K){2,}b` -> yes-collapsed
- UNREACHED (T2 row 5 and row 6 at SIZECAP): comments carry the §4.3a arguments. Header states these rows are the table-independent control of T2's listing half and half of the B4 HARD GATE.
Result: 50 checks pass / 0 fail (was 34), 7.6 s.

## Item 11: tests/codegen/run_fallback_table.sh (NEW), section test-fallback-table, mech arm fallbacktable
- Extractors moved verbatim (with comments) to tests/lib/spec_extract.sh; axes_registry_check.sh sources it. Registry BEFORE/AFTER: 214 PASS / 0 FAIL, byte-identical output; `make test-registry` green (run_registry_tests' 214 pin unchanged).
- (b) observed-stamp leg, 15 witnesses (all probed): ENGINE_SEL selected `(a)b`; forced `--engine=vm (a)b`; declined-nullable-default `(a)*`; overflowed-dfa `^(?:(?:a|b)*a(?:a|b){20})?$`; collapsed-prefilter `(1{0,30}?[^]abc][^abc]){28,30}0+|a`; declined-nullable `(?:ab){0,16000}`; size-cap-retry `-e utf8 (\p{Xwd})`; overflowed-prefilter on lowdfa (`-DPCREC_MAX_AUTO_DFA_ELEMS=3000`) `(x)(?:a|b)*a` + 11 unrolled `(?:a|b)` (from reach/witnesses.tsv fb3-norep). UNROLL_K_WHY: default/option(`--unroll=4`)/denied(`-fno-size-term`) on `a(b|c)+d`; size-model on NEST8 (run_size_term.sh's); cap-rescue `(?:a\K){0,10}ab` and size-model-declined `(?:a\K){0,10}b` on lowsize; capacity-declined on lowthr (`-DPCREC_SIZE_TERM_THRESHOLD=1000`) `--engine=vm (((?:a{0,2}b)+c){0,20}d){0,20}e`. Measured floors: every one of the 8 and 7 values has exactly 1 witness (floor >= 1; others stamp default/selected incidentally). Fail-closed: extraction sizes asserted 8 and 7; observed set checked both directions against match_api.md §6.3 via the shared extractors.
- (c) PFLW: exact `(a){2,3}b`; no counted repeat `(a)b`; nullable collapsed language `-fprefilter-collapse ^(a{2,9})*$`; forced `-fprefilter-collapse (x)?a{0,4}\Gb`; "dfa overflow retry, exact nfa 1899" (FULL text) on the SEL1 witness; size cap retry exact, SHAPE `^size cap retry, exact [0-9]+ > 1000000$` + N > cap numeric, on `-e utf8 (\p{Xwd}{1,3})` (1447884 today; note the brief's `-fprefilter` witness also gives this form); VM_PREFILTER_WHY "size cap retry, hybrid N > M" shape on `-e utf8 (\p{Xwd})` (1028613 today); plus VM_PREFILTER_WHY absent on a surviving hybrid.
- (a) SEQUENCES: header only, lands at B1.
- Result: 66 checks pass / 0 fail, 6.8 s (three reference compilers built in parallel). K37 bare-compiler guard (inside test-codegen) green; `make test-codegen` green (2m39s); `make strict` clean.
- Makefile: TEST_SECTIONS, recipe with TEST_TRAILER_DIR marker, .PHONY. docs/testing.md and CLAUDE.md of tests/codegen, tests/prefilter, tests/lib, tests/registry, tests/mech updated (docs/testing.md names no section count except the 59/59 measurement record; section note added).
- Mech arm `fallbacktable`: vocabulary entry + arm case (registered with no rows; syntax checked, arm not yet run through a sabotage row).

## Both directions (all on this tree, reverted)
- Green on the clean tree: 66/0.
- (i) Drop witness `sel-collapsedpf`: `FAIL: [RX_ENGINE_SEL] floor: NO witness stamps 'collapsed-prefilter'` (62/1). Drop `why-denied`: `FAIL: [RX_UNROLL_K_WHY] floor: NO witness stamps 'denied'` (63/1).
- (ii) match_api.md row `"declined-nullable"` unquoted (throwaway edit, git checkout): `FAIL: K35: match_api.md's ENGINE_SEL set has 7 values, expected 8` and `FAIL: [RX_ENGINE_SEL] observed value 'declined-nullable' is NOT in match_api.md's hand-written set` (63/2).
- (iii) `ESEL_FORCED` returning "selected" in emit_dfa.c:450 (rebuilt): `FAIL: witness sel-forced ...: ENGINE_SEL is 'selected', expected 'forced'` + the `forced` floor (63/2). emit_vm.c:11367 "no counted repeat" -> "no counted repeats" (rebuilt): `FAIL: PFLW 'no counted repeat': '(a)b' stamps "no counted repeats"` (65/1). Both reverted, rebuilt, back to 66/0.

## Commits (lane/decfbB0b)
32be5b02 extractor move; cbff4d54 prefilter §7b; c03a75d1 fallback table script + Makefile + mech arm; 645c0344 docs (the report commit follows).

## Notes for the parent
- Scratch under worktree build/tmp only; the dec_fallback.md `-fprefilter` forced-on SIZECAP witness gives PFLW "size cap retry, exact", not "forced"; this is today's behaviour and is pinned only via the listing row.
- No sabotage rows were written for the new arm (not requested); first rows should name `fallbacktable` in SAB_SUITES.
