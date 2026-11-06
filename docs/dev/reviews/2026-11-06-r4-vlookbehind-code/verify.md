## EMIT-1+CONTRACT-1
HOLDS. SUBJECT build/pcrec `(a)(?<=\1)x` -e byte: rc=1 "every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 3)". Own ctypes pcre2_compile_8 (verify/pc.py): `(a)(?<=\1)x` compiles (True), `(?<=a+)x` err 125. Spec pattern_language.md:150 (shape 5 lists "a backreference inside a lookbehind") and :480 (7.4p5 "So is a lookbehind containing a backreference (`(a)(?<=\1)`, shape 5)", unbounded ones "shape 7"). mod_lookaround.c:369 "EVERY ARM IS A REFUSAL PCRE2 MAKES TOO".
## CONTRACT-2
HOLDS. Own driver (verify/drv.c over rx_search, all-'a' subject): `(?<=a{1,254}b)` 7889 -> 0, 7890 -> -2 (PCREC_ERR_STEPS = -2); `(?<=(a{1,120}){1,2}b)` 100 -> 0, 200 -> 0, 500/1000/2000 -> -2; libpcre2 (verify/m.py) at 1000 -> -1 (no match). Spec limits.md:80 states K^2 unqualified.
## CONTRACT-3
HOLDS. compliance.md:1452-1470 still says "DESIGNED, NOT BUILT ... refusal below is today's behaviour" and :166-168 "(?<=(a|bc))x is REFUSED"; build compiles `(?<=(a|bc))x` rc=0. Sweep: docstring :29-33 "EXPECTED and is not a failure"; :199-205 a width refusal is counted pcrec_refuses, continue (bad_refusal only if message is not a width sentence); :244-245 bad excludes pcrec_refuses. So an over-refusal of a libpcre2-compilable body scores PCREC-REFUSES and passes.
## CONTRACT-4
HOLDS (all three). (a) `(?<=(?:(?:a{65535}){65535}){65535})x` -> "(this one is unbounded)"; libpcre2 err 187. (b) `(?<=(?:a{0,65535}){65535})x` -> "(this one has 4294836225)"; source :385 "has %lld" vs :391 "can match up to". (c) `(?<=a+|(?:b{65535}){2})x` pcrec "has 131070", libpcre2 125; reversed order pcrec "unbounded", libpcre2 187. All offsets 0.
## checks-1
HOLDS. emit_vm.c:7711 `if (atomic) vm_cut(...)`; plant S1963 (rc 0, edits vm_look_needs_mark only). Harness with planted compiler on lookbehind_variable_witness.rxt: cases passed 54, failed 0 (rc 0).
## checks-2
HOLDS. S1964 plant (rc 0): harness 54/0. vlb_one `(?<=(é{0,2}))x` utf8: clean+ASAN/UBSAN PASS; plant plain PASS; plant ASAN/UBSAN "FAIL ... the artifact did not finish".
## checks-3
HOLDS. S133 declares no SAB_EXPECT (file lines 40-42: SUITES, TARGET, DESC only). Planted compile of `(?<=a{1,2})x`: gcc errors "rx_BACK_STEP_NONE undeclared", "implicit declaration of rx_back_step". run_sabotage_matrix.sh ~3646: any_nocompile without COMPILE-CATCH -> "ANOMALY (the plant does not compile ...)". (Did not re-run the matrix or confirm ceiling 0.)
## checks-4
HOLDS. S1980 plant harness: 32 pass / 22 fail, all "expected match .. got 'nomatch'" (lines 45 52 60 149 156 ...), 0 "gave up", 0 frames. SAB_DESC/header claim a trailed-write overrun (nine candidates overrun the trail term). Own-plant (GAVE UP frames) claim not re-run.
## checks-6
HOLDS. New-row scripts mention W3b once (S1975), W3 once, W10 zero times, W5 three times. S1975 plant (rc 0) harness 43/11; failing witness lines 45 52 149 162 183 199 223; line 31 (W3b cell) NOT among them, so the DOC_FIGURE "W3b red" is false. Design §7 (lines 1834, 1842) names W3b/W10 sabotages with no matching row. Not re-checked: every row's W3/W7 incidental coverage.
## checks-7
HOLDS. run_lookaround_diff.sh:414-422 comment "each floored at its measured figure" and floors 30000/9000/2000/150/1. vlb_cells.py (python3 -I): 373/233/48/7 patterns. vlb_one cells per pattern (3 samples per mode, constant): 131/65/43/36 -> 48,863 / 15,145 / 2,064 / 252 vs floors 30000 (61%) / 9000 (59%) / 2000 (97%) / 150 (60%). Full run not done; extrapolated from samples.
VERIFY COMPLETE
