# CHECK-ADEQUACY — ic1b-code
critic: check-adequacy (sonnet); 2026-10-26; status: COMPLETE
Denylist: nothing denied was opened. Probes: all 14 S1646-S1659 SAB_BEFORE texts (plus S1653's second file, S475/S496/S693) counted by a scratch script against the SUBJECT tree: each occurs exactly SAB_COUNT times. One scratch run of a COPY of gen_diff.py (n=45) in /tmp to count matches.

## CHK-1 firing-class bound has no counted floor, and is checked on the generated population only
- status: CONFIRMED
- severity: maintenance
- effort: S ; blast radius: tests/callouts/gen_diff.py, S1655 (S-IC19), run_callouts_tests.sh arm 3
- where: tests/callouts/gen_diff.py (prints "artifacts with a checked firing-class bound", never compares it to a floor; only `len(compared) < a.floor` is floored); inline_c.md §9.1 says "each class's bound checked by a counting binding over the corpus"
- repro: n=45 sample: 38 of 45 artifacts carried a checked bound, so today it is healthy. But if the listing ever classed every site `repeated` (or the single-binding filter `len(classes)!=1` excluded all), the bound would check nothing and arm 3 stays green. S1655's only witness is this bound.
- argument: K35 (populations nobody counts). The mech arm cuts the population to 300/floor 250, so S1655 detection rests on an uncounted subset. Also promised "over the corpus" is delivered only over generated patterns (shapes.rxt cells are never run through the fire log). Fix: floor the checked-bound count (e.g. >= 100 of 1000) and print match/no-match share.

## CHK-2 "libpcre2 unavailable" (exit 3) also swallows a broken oracle driver; two arms and S1655 then SKIP green
- status: CONFIRMED (by reading)
- severity: maintenance
- effort: S ; blast radius: arms 2 and 3, mech arm callouts
- where: verify_callouts.py and gen_diff.py: any nonzero gcc status on co_oracle.c returns 3; run_callouts_tests.sh maps 3 to `note` (SKIP, not fail)
- repro: introduce a compile error in co_oracle.c or behaviors.h: both oracle arms SKIP, `checks failed: 0`, make test green, and the S1655 witness (arm 3) silently vanishes from the mech arm.
- argument: PC-3's shape distinguishes absent library from broken probe. Test for the header/library (`pcre2.h` present, `-lpcre2-8` links a one-line probe) and make a failure to build co_oracle.c a FAIL. Related: verify_callouts' floor is `agree < 20` against a 59-cell corpus (axes floor says 50), and m/n lines the regex fails to parse are `continue`d silently, uncounted. Raise the floor to ~50 and count unparsed cell lines.

## CHK-3 trap checks accept any fatal signal, including SIGSEGV
- status: CONFIRMED (by reading)
- severity: maintenance
- effort: S ; blast radius: arm 4 traps overlong/midchar/pred1, S1652, S1654
- where: run_callouts_tests.sh `[ "$rc" -gt 128 ] && [ "$rc" -ne 124 ]`
- argument: the call site's trap is `__builtin_trap()` (SIGILL, 132). An out-of-bounds read from a removed bound (S1652) or any crash in the driver is also >128 and reads as "the call site trapped". For these three artifacts the sabotage happens to print "no trap" rather than crash (the pattern ends at the site), so detection holds today, but a sabotage or bug that crashes instead is accepted. Pin rc == 132 (or check the signal is SIGILL) and have the trap path reach a read past the end before it can crash.

## CHK-4 a few witnesses are hand-derived constants with no independent leg
- status: SUSPECTED
- severity: maintenance
- effort: M ; blast radius: checks.c A5 (S1657), the view's slot-0 end, gen_diff coverage
- where: checks.c vn/vc (`--no-captures`); behaviors.h/co_oracle.c (caps[0][1]); gen_diff.py Gen
- argument: (a) behaviors.h is the one table both sides call; I judge that sound (the rows are pure functions of pos/len/subject/caps, view construction is separate on each side, and libpcre2 reads its own offset_vector under capture_top). But NO row reads slot 0's end: the oracle fills `-1` and pcrec's value there is never compared, so a wrong slot-0 end is invisible. (b) The generated differential has no `\K`, lookbehind, backref, subroutine, UTF, `--no-captures` or nonzero start offset (ask() always passes 0), so S1651 (slot-0 restore), S1647, S1657 ride only checks.c's hand-written expectations (A4 also has the oracle-checked `a\Kb(?C"notone")c` in shapes.rxt:79, which is good; A5 has none). Cheap upgrade: run the generator population a second time under `--no-captures`, answer-compared against the same oracle answers.
- class derivation: gen_diff reads the class from pcrec's own `--emit-ir` listing, but only to decide WHICH sites to bound-check; the expectation (<= 1 fire per start) is the spec's, observed from the independent stub log. A pcrec bug that over-classes (`repeated`) is invisible there but arm 5's hard-coded table (11 rows, independent of the derivation) covers the class text. Held.

## CHK-5 sabotage reach probes check emitted text, not that the witness executes the sabotaged line
- status: SUSPECTED
- severity: maintenance
- effort: S ; blast radius: S1656 (and weakly S1646-S1659)
- where: tests/mech/sabotages/S1656_marked_set_unconditional.sh SAB_REACH (`grep -qF 'rx_'` on `(a)(b)c`, true of every artifact)
- argument: the reach for S1656 proves nothing about `case KREADS_NONE`; reach should show a group retained or dropped by the changed branch (e.g. `--no-captures` NCAPS of `(a)b`). The other 13 reaches grep a callout-specific emitted fragment, which proves the SITE is emitted, and I confirmed each witness (checks.c check, shapes.rxt cell, arm-5 row) names that pattern, so they are adequate. S1658's note "answers 0 without the charge; measured by hand" is the only evidence that budget 5 is not exhausted by other charges; the mech run is its first real proof (owed job 541).

## CHK-6 mech `callouts` arm and registry docs
- status: CONFIRMED
- severity: doc
- effort: S
- where: tests/mech/run_sabotage_matrix.sh header vocabulary list (~line 185) does not list `callouts` although the arm exists at :1882; arm cuts N to 300/floor 250 (reason given in the arm comment, justified).

## Promised vs delivered (inline_c.md §9.1 stage 1b, §9.2)
- Sabotage list: S-IC1,2,3,3b,4,5,6,6b,11,19,20,25,26,27 = 14 = S1646..S1659 one-for-one. None missing. S-IC20 (S1656) is carried by suite brefidentity as designed.
- Tests: A1 (shapes.rxt:63), A2 both (checks.c + shapes 73/94), A4, A5, enclosing group, retention, give-up STEPS and tiered FRAMES (with `_deep(` reach assert), step charge, overlong/midchar/pred1 traps, `,consume` artifact as callee, two-byte consumer, malformed forms on and off, firing-class table, once accepted/refused with reason, DT-4.1, axes floor: all present.
- Weaker than promised: (1) bound "over the corpus" only on generated patterns (CHK-1); (2) the §9.2 test-owned backtracker leg is absent, but the manager's 2026-10-26 ruling (INLINE-C.md line 8: no separate backtracker, harness minimal) drops it. Not a finding. Consequence: libpcre2 is the sole answer control, and `consume` is checked only via a spliced regex equivalent; (3) "PCRE2-sensitive" default-flags filter dropped, same ruling.
- No sabotage covers the new `callout` prefilter-admit row, the `-fprefilter` refusal, or the retirement of the (g)/V callout conjuncts. The latter is covered behaviourally: I compiled 4 callout patterns and all take the VM start-scan hat (`RX_VM_START_SCAN "first-class"`), so gen_diff exercises skipped attempts against libpcre2. The prefilter decline is answer-neutral by the diff's own text (erasure would be sound), so a sabotage would be stamp-only; acceptable, but there is no test that a callout pattern gets `no-callout` (the only mention is the new ir baseline). Low.

## TRADE AUDIT
- ir_listing baselines: 17 existing files changed by the SAME 2-line swap (callouts section header+none row), plus one new fixture baseline 3ed51727 captured from pcrec's own output. Gives up: byte-neutrality for the callouts section of callout-free listings (inevitable: the section schema changed). Justified by ir_listing.md §3.7 and the script comment; verified the 17 diffs are only that swap. The reason for the RE-baseline is not stated in run_ir_listing.sh next to CAPTURE_IR_BASELINE (doc, trivial). Only ONE fixture has a callout site (named + numbered, no consume, no repeat class).
- S475/S496: re-scoped to verbs; still SAB_EXPECT=UNREACHED, so the callout half of the conjunct is retired with no mechanical witness of its own (gen_diff's behavioural coverage above is the substitute). The prose retirement argument (superset erasure + unspecified fire counts) is stated in emit_dfa.c and matches the ruling D4. Justified.
- S693: 87->89 skipping 88 ("ic0's", provisional); plant 88 is a valid lower value. FILEPIN of run_recursion_identity.sh moved to the lane's own last src commit cfdf8f5fd (src identical to SUBJECT except CLAUDE.md). Gives up: the (B) identity pin now certifies "later changes did not move", not "ic1b moved nothing"; the zero-mover claim rests on the owed census job 540 and the (A) pre-module pin. Follows the documented self-pin convention; manager re-pins at merge.
- compliance_section.py 142 -> 143: one new REJECTED row `(?Cx)`; comment states why. Justified; assertion remains an exact count.
- test-axes floor 50: measured 59, so slack of 9; counts REFUSED compiles too (dfa/prefilter axes), so it floors "reached the axis", not "ran". Stated in the diff comment. Justified, slightly loose.
- tests/ci/shards.tsv: test-callouts weight 120 is ESTIMATED, labelled as such.

## PROBED-AND-HELD
- 14 sabotage targets x exact-once match in SUBJECT source (plus S1653 file2, S475, S496): all counts = SAB_COUNT.
- S1659's `!rep` plant leaves `(?:(?C1)(a))+` (rep) accepted while arm 5 expects refusal: detected; S1646/S1650/S1654 plants swap a real row field to a real existing symbol (cs_part, CS_FAIL, CS_SUCCESS exist in the table).
- gen_diff sample (n=45, copy in scratch): 45/45 compiled and compared, 138 of 270 cases match (51%), 0 disagreements, 0 class violations, 38/45 with a checked bound.
- libpcre2 leg independence: separate view construction (capture_top hiding, start_match as slot 0), separate flags, consume spliced as regex.
