# pcrec Project Plan — completed work archive

Completed rows archived verbatim from docs/dev/plan.md on 2026-08-13, grouped by completion date where known (undated rows placed under the nearest inferable date, tagged `(date inferred)`) and in original relative order within each date group. The active plan is docs/dev/plan.md; a row cited elsewhere as "docs/dev/plan.md [ID]" lives here once it is STATE:completed.

    grep -c "STATE:completed" docs/dev/plan_completed.md

## 2026-08-09

- [M0.1] STATE:completed — directory layout, GNU Makefile

- [M0.2] STATE:completed — docs: plan.md, dev_journal.md, decisions.md

- [M0.3] STATE:completed — CLAUDE.md in each directory

- [M0.4] STATE:completed — test harness: run.sh, driver.c, docs/testing.md (subagent)

- [M0.5] STATE:completed — base test corpus in tests/base/, python-re cross-verified (subagent)

- [M1.1] STATE:completed — core utils: arena allocator, string buffer, error/longjmp diagnostics

- [M1.2] STATE:completed — AST + base parser (with module hook points for escapes and (?… groups)

- [M1.3] STATE:completed — NFA construction: priority Thompson with greedy/lazy split ordering

- [M1.4] STATE:completed — priority subset construction (leftmost-first via accept-pruning) + byte equivalence classes

- [M1.5] STATE:completed — codegen: computed-goto DFA, ASCII encoding, string-source search API

- [M1.6] STATE:completed — library API: pcrec_compile() in lib/pcrec.h

- [M1.7] STATE:completed — CLI: pcrec -p/-o/-e/--emit-main

- [M1.8] STATE:completed — integration: base corpus green under harness

Known M1 limitations (tracked for later milestones):
- ~~mid-pattern `$`~~ REMOVED by R1 fix: EOL-variant states make `$` fully general
  (single-line semantics; multiline stays with the assertions module).
- Unanchored search is a per-start-position attempt loop (measured O(n²), R1 A-2);
  M2.0's search-from-anywhere automaton is the fix.
- No DFA minimization yet (M2). Bounded repeats expand states (cap enforced); counter
  loops come with the VM engine (M4).
- Capturing groups parse but only the overall match span is reported (captures are M4).

- [M2.0] STATE:completed — DESIGN GATE (R1 A-2/A-3): adopt the search-from-anywhere self-loop automaton (kills O(n²), same shape M3 streaming needs) and the hybrid emitter (computed goto for small DFAs, table-driven for large); re-ground the state cap in measured gcc compile time

- [M2.1] STATE:completed — scan-avoidance: memchr/bitmap start prefilter, self-loop skip states (fwd+rev), anchored fast path (^-only patterns skip the start loop)

- [M2.2] STATE:completed — DFA minimization (Moore signature refinement, EOL-view as extra symbol); alternation-to-trie DEFERRED with rationale: subset construction already merges alternation prefixes in the final DFA, so a trie pass would only shrink the intermediate NFA (compile-speed win with no current budget pressure)

- [M2.3] STATE:completed — tests/bench: throughput budgets AND gcc-compile-time budgets on generated code as regression tests (R1 A-3)

- [M2.4] STATE:completed — coverage breadth (R1 P-M1/P-M2/P-N1/P-N2): CLI surface, library API direct, startpos != 0, long subjects, high bytes/NUL

- [M2.5] STATE:completed — PCRE2-oracle differential fuzzer committed to tests/ (pulled forward from M7; R1 lesson — semantics critic's libpcre2 binding)

- [M2.6] STATE:completed — K1 fix (landed early at R2: loop-entry empty-iteration rule; also fixed R2-S1 in BOTH engines)

- [M2.7] STATE:completed — engine unification for `$` (D8; `^` deferred, needs a reverse BOT variant) — engine unification (R2-A2, FATAL): `$`-without-`^` patterns route to ENG_ATTEMPT which has NO scan-avoidance and is still O(n²) — measured 14.3x slower on a log pattern, quadratic on `a*b$`. Either fold `^`/`$` into ENG_UNANCH (EOL-variant switching in fwd+rev, BOT handling in reverse) or give ENG_ATTEMPT prefilters. R1's A-2 is only half-fixed until this lands

- [M2.8] STATE:completed — NFA-level alternation trie (R2-A4, D9/D10): priority-preserving prefix trie in src/ir/nfa.c; the quadratic turned out to be closure FAN-OUT, not state count (measured 4045 visits/closure at 2000 branches, 2.36e9 total). 3600-word list: hard-fail -> 0.93 s. NFA cap re-derived 20000 -> 131072 so the emitter-grounded DFA caps bind first; clo_visit tail edges made iterative so the cap no longer depends on gcc's TCO. ALSO fixed an unrelated repo-fatal bug found on the way: `.gitignore`'s unanchored `core` had excluded src/core/ from every commit

- [M2.9] STATE:completed — benchmark rigor (R2-B3/B4, D12): taskset pinning (chrt probed, unprivileged here), governor/turbo/loadavg capture, BENCH_TRIALS repeats judged on the median with max/min spread printed, budgets re-derived as measured-median/1.75 and VALIDATED by sabotage (prefilter+skips disabled fails all 3; the old budgets would have passed all 3), case (c) subject made match-free so it measures a scan rather than early exit, linearity moved to 16/64 MB x20 iterations so it is no longer a timer artifact

- [M2.10] STATE:completed — dense/counting-pattern codegen (R2-A5, D13). Two results, one NEGATIVE and honestly so: (1) widening skip eligibility from ">=192 of 256 bytes" to a fraction of LIVE bytes so `[01]*1[01]{8}` qualifies MEASURED 27% SLOWER on that very case and was REVERTED — the +40% first recorded was a bad un-interleaved sample; a codegen check now asserts the state stays ineligible so it cannot be re-landed on plausibility. (2) D7's promised computed-goto-vs-table arbitration RESOLVED by micro-benchmark, with a correction: computed goto is 2.5x slower on data-dependent transitions but 3.5x FASTER on predictable ones, so the crossover is in PREDICTABILITY, not DFA size. The unconditional table emitter stands because general scanning is the data-dependent case. Case (f) itself remains a loss vs PCRE2 and is now an M4 concern

- [M2.11] STATE:completed — process ratchets (R2-PR7/PR8). tests/known_fail/run_known_fail.sh inverts the verdict on deferred-bug regressions (now-PASSING is flagged and fails, with promotion instructions); tests/bench/compare/gate.sh gates pcrec's own per-case headline numbers against a checked-in floors.tsv (absolute values, not cross-engine ratios, which move for reasons that are not our regression); compare.sh no longer silently overwrites a same-day snapshot. All three validated in both directions

- [M2.12] STATE:completed — restore prefilter/skip loops on the EOL engine path. The two emitters M2.7 forked are merged back into one EOL-aware emit_unanchored (the fork IS how the `$` path lost these for a milestone); skips bounded at n-1, memchr keeps no early return, reverse skip carries a pp+1<n entry guard. Also required moving the accept/EOL evaluation AFTER the skips — bounding alone is not enough, a skip landing on n-1 would consume that byte before its EOL view was taken. `$` throughput 291 -> 22248 MB/s median of 7 (~76x), now at parity with the same pattern without `$`. The reorder is applied ONLY when eol is set: doing it unconditionally shipped a 43% regression on `[01]*1[01]{8}` (158.4 -> 90.8 MB/s), found later the same day by the M2.11 compare gate. Non-`$` codegen is byte-identical to pre-M2.12 on 8 probe patterns — a claim that was made prematurely the first time and is now actually true

- [R1] STATE:completed — M0+M1 checkpoint review (4 critics) — compiled + triaged in docs/dev/reviews/2026-08-09-m1.md

- [R2] STATE:completed — M2 checkpoint review (5 critics; 4 reported, process/tests/docs critic did not deliver — lens carried to R3) — docs/dev/reviews/2026-08-09-m2.md

- [R1.1] STATE:completed — all fix-now items applied and verified (2 wrong-answer bugs via EOL-variant states, 3 crash classes, leak class, LLP64 span type, PCRE accept/reject parity, harness integrity, CLI --); suite 353/353

- [OS-0b] STATE:completed — multi-engine output prep, and it is SMALL (D18, measured): of the 15 identifiers the emitter produces, 12 are FUNCTION-LOCAL statics (fcls ftr facc fev fs<N> rcls rtr racc rev rs<N> first) that cannot collide between engines in separate functions. Only three are file-scope: the `<prefix>_span` typedef and the declaration + definition of `<prefix>_search`. So multi-engine needs (a) `<prefix>_span` emitted ONCE and shared — emitting it twice declares two distinct anonymous struct types, which are incompatible rather than a benign redefinition — and (b) a distinct function name per engine, which the named-entry-point scheme already supplies. Do this prep before anything needs two engines; it is cheap and it blocks everything if left. ALSO in the same change: tests/codegen/run_codegen_tests.sh hardcodes 9 symbol patterns that are unambiguous only while there is one engine per file — with several, `rx_fs[0-9]+\[256\]` can be satisfied by ANY engine, so the check degrades from "this pattern emits a skip table" to "some engine here does" WITHOUT failing. Scope those greps per engine or they quietly stop guarding. DONE 2026-08-09: `emit_span_typedef` (once per file) split from `emit_search_decl` (once per engine), and the entry name now comes from `engine_entry_name()` and nowhere else — output verified BYTE-IDENTICAL over 167 corpus patterns x 3 prefixes x 4 emission modes (1980 hashes). Correction to the count above: it is 19 grep sites across 11 generated files, not 9; all now run against an engine body extracted by entry name. The premise was verified rather than assumed — a duplicated `rx_span` typedef is `error: conflicting types for 'rx_span'` under -std=gnu11 AND -std=c99. A two-engine fixture (built by the transformation the finder will apply) is compiled in the suite and doubles as the control for the scoping: 5 sabotages recorded in tests/codegen/CLAUDE.md

- [OS-1] STATE:completed — ASCII case-insensitivity: PREDICTED to fold entirely into class construction (`bitmap |= swapcase(bitmap)` at parse time), giving zero runtime cost, no second engine, and possibly SMALLER tables via byte-class merging. Measure: table size and throughput, folded vs a hypothetical runtime-checked variant, on a case-heavy pattern set. If the prediction holds, DD-1 stops being an engine question for the ASCII tier and becomes a parser change. Unicode folding is a separate question and stays with DD-1/M5. DONE 2026-08-09 (D23): PREDICTION HELD — `cls_casefold` at parse time, `-i 'aBc'` emits BYTE-IDENTICAL C to `[aA][bB][cC]`, no second engine, no runtime cost, entry-point signature unchanged. Beats the runtime-checked design on every measurable pattern (511.7 vs 458.9 MB/s on keywords; the lc[] indirection alone costs 26% on a letter-free pattern). TWO CORRECTIONS: tables come out the SAME size, not smaller — shrinking needs the pattern to mention both cases already (`aA` 9->6) — and folding a leading letter DESTROYS the memchr prefilter (1 escape byte -> 2), which is a 52% loss on `hello` and a second measured customer for OPT-A's memchr2 lead

- [SR-1] STATE:completed — the CONSTRUCT TABLE. `static const` rows in
  src/parse/registry.c: {kind (ESC|GROUP|VERB|CLASSBRACKET), selector byte,
  feature bit, flavour mask, engines mask, module name, one-line PCRE2
  semantics, handler fn or NULL}. Indexed [256] per kind, short chain for the
  rare flavour-varying byte. NULL handler = known-but-unimplemented, which is a
  complete and tested outcome, not a stub. Everything the parser currently
  knows about non-base syntax moves here: `esc_modules[]`, `esc_char_value`'s
  non-base cases, the `(?X` ternary chain, the `(*` catch, the `[[.`/`[[=`
  rule. (NOT "everything", as built: `\x{...}` and the possessive `+` are
  sub-cases of BASE constructs, not doorways, and stay in parse.c — see D24.) THE POINT is that a construct stops having two homes — `\v` was the
  declarative table and the imperative switch disagreeing ten lines apart.
  BUILT 2026-08-09 as src/parse/registry.c: 67 rows (39 escape, 24 group, 1
  verb, 3 class-bracket), guarded by tests/registry/ (116 checks, five sabotage
  edits, all caught). Two departures from the text above, both recorded under
  D24: the [256]-per-kind index was NOT built (a linear scan over rows the base
  tier never reaches; an index would be an unmeasured axis AND a second home for
  the selector bytes), and the handler field waits for SR-2, where its four
  signatures are actually determined. parse.c is unchanged, so behaviour is
  bit-identical by construction

- [TS-1] STATE:completed — codegen structural check: every `static` in emitted output must be `const`, and the output must not reference a denylist of non-reentrant or allocating symbols (malloc/calloc/realloc/free, errno, getenv, setlocale, strtok, rand, asctime/ctime/gmtime/localtime). Cheap, needs no gcc, and directly sabotage-validatable — add one non-const static to the emitter and it must fail. This is the guard that catches the memoisation-cache and hoisted-scratch-buffer failure modes. DONE 2026-08-09: 18 emitted files across 9 emission shapes (both engines, EOL/non-EOL, both prefilter kinds, skip states, never-matches, case-folded, --emit-main) plus paired .h; the file count is itself asserted. SABOTAGE RESULT WORTH KEEPING: making every emitted table a non-const static fails 8 TS-1 checks and ZERO corpus cases — the code compiles, matches identically and passes the whole suite while being thread-hostile, which is exactly the property nothing else here can see

- [R3.2] STATE:completed — R3 had essentially NO adversarial critic coverage: five critics dispatched across the milestone, one usable headline (independent confirmation of the rule-2 overlapping-class break), zero full reports. One design critic claimed '5 more findings' that were requested repeatedly and never arrived — if any apply to the shipped code they are still live and unknown. Partially closed by self-run differential sweeps after the fact: the trie's guards held over 35,280 cases (nested alternations, quantified groups, overlapping classes, `$`, mixed eligible/ineligible branches) and startpos!=0 held over 12,480 cases. The iterative clo_visit rewrite also held: with ONLY that function reverted to its recursive form, 2,294 random patterns emit byte-IDENTICAL C. STILL UNPROBED: (1) the EOL vs non-EOL ordering asymmetry in emit_unanchored (D11); (2) whether D13's dispatch micro-benchmark represents the real emitter shape. (2) IS NOW CLOSED (2026-08-09, D13 addendum): probed against the REAL emitter and HELD. The micro-benchmark does NOT represent the emitter — it never existed in this repo (git log -S confirms the only "dispatch.c" in history is the D13 prose itself), it models neither the forward+reverse double scan, nor the per-iteration accept/prefilter/skip side work, nor the ncls equivalence-class indirection, and for prefilter-eligible patterns most bytes never reach the dispatch loop at all. Re-derived on real emitter output for 3 patterns (768/225/2915 states): goto/table 0.35-0.91 on random input, 2.75-3.07 on predictable input — the R3 "predictability, not size" correction reproduced at realistic scale, direction never flipping. The decisive argument turns out to be COMPILE time, which D13 never makes: verified on a quiet box, gcc -c only, computed goto costs 10.9x / 35.6x / 319x more than tables. "table always" survives more strongly than D13 states it. (1) IS NOW CLOSED TOO (2026-08-09, D11 addendum): swept to 25,834,470 oracle-checked comparisons across 6432 patterns, 0 divergences on the shipped compiler, including under ASan+UBSan; both directions of the asymmetry sabotage-tested (non-EOL order forced onto the EOL path: 238,144 divergences, confirming the rule far more widely than the 53 originally cited; EOL order forced onto the non-EOL path: 0 divergences, so the split is purely a performance decision). Three claims corrected: the speed win exists for ONE pattern family only (the EOL order is a tie or 1.5-4.1% FASTER on five of six throughput cases), the 43% is a gcc -O1/-O2/-O3 artifact that vanishes at -Os and -O0, and the load-bearing premise — accept monotonicity, no state has plain accept 1 with a non-accepting EOL variant — was never written down. Gap closed: the reverse pp+1<n guard now has mid-pattern-`$` behavioural coverage (14 cases vs the 3 that caught it incidentally before). NOTE the critics that produced both halves of R3.2 reported only after being required to append findings to disk as they went; two earlier ones dispatched at the same targets delivered nothing

- [PC-1] STATE:completed — construct-by-construct compliance survey against
  pcre2syntax.html, recorded in docs/pcre2_compliance.md with a status
  vocabulary that separates verified from believed and clean-rejection from
  miscompile (2026-08-09). Found and fixed one PROVEN divergence (`\v` was
  vertical tab, PCRE2 says vertical whitespace) and one whole missing guard
  (the "never miscompile" mandate had no test)

## 2026-08-10

- [FIX-1] STATE:completed — K5 and K6, the two MISCOMPILES. Landed 2026-08-10.
  `try_quant` now REMEMBERS a count above 65535 and raises PCRE2's error 105
  only where it would have returned true; `p_atom` gained a `case '{'` that
  asks try_quant and raises error 109 when the answer is yes. Both fixes are
  two-phase for the same reason: the malformed braces that must keep compiling
  (`a{`, `a{}`, `a{,}`, `a{1`, `}`, `a{65536x}`) are exactly the forms
  try_quant declines, so the over-reach guard is structural rather than a
  second list. 49 forms differentially probed against libpcre2 10.46 — all
  agree on verdict AND offset. Coverage: +20 tests/reject rows (the
  DIAGNOSTIC, which `perr` cannot express), +15 accept-controls, +37 corpus
  cases. Five sabotages, all caught; the off-by-one is caught by exactly ONE
  check (`(?:){65535}`) and nothing else. Found K7 (a large bounded repeat is
  SIGKILLed, pre-existing) and U5 (python accepts counts PCRE2 rejects).
  **R7's panel then found K8 — a THIRD miscompile of the same class in the same
  function**, whitespace inside `{m,n}`, which all 49 probes had walked past
  because they compared verdicts and the bug lives where both engines accept.
  Fixed in the same checkpoint, with U6. The panel also closed: no test in the
  repo asserted an error OFFSET (22 rows now do); the over-reach guard covered
  only the first number (four rows added); no `{k,k}` existed anywhere (three
  cases added); `tests/reject/` had no `timeout`, making its own rc>=124 promise
  unreachable; and the exact-count hazard was measured disarming the boundary
  row in a two-line diff, answered with a MANIFEST that names irreplaceable rows
  by pattern. See docs/dev/reviews/2026-08-10-r7-fix1.md

- [PC-3] STATE:completed 2026-08-10, WITH Q1 — the first external check in the
  project. `tests/registry/pcre2_check.c`: every row against libpcre2, plus a
  ~824,000-probe differential over ~75,000 verb names generated from libpcre2's
  OWN BINARY. Q1 (D25) gave the `(*` doorway two name tables so pcrec's answer
  depends on the name, which is what makes that differential mean anything.
  **THE "EXTERNALLY VERIFIED BASELINE" CLAIM WAS TOO BIG AND R8 MEASURED HOW
  MUCH**: 65 of the 67 rows are verified by ONE BIT ("libpcre2 compiled a string
  containing this row's syntax"); seven of `RegRow`'s twelve columns —
  `feature`, `module`, `flavours`, `engines`, `diag`, `flags`, `note` — are read
  by no external check at all; and `\v`, the row the registry exists for, is NOT
  verified, because libpcre2 compiles `\v` under either semantics. What IS
  externally verified: no row names a construct PCRE2 lacks, the two RS_REJECTED
  rows agree with PCRE2's error identity, and the verb doorway's whole name
  surface. See docs/dev/reviews/2026-08-10-r8-pc3-q1.md, and PC-4 and Q2 below,
  which are what the panel turned up

- [FIX-2] STATE:completed 2026-08-10 — K3 and K4 both fixed, plus the doorway's
  own over-promise. **PANEL RUN 2026-08-10, a session late: R9,
  docs/dev/reviews/2026-08-10-r9-fix2.md.** The rule held everywhere it was
  attacked — 1,239,480 generated patterns with zero verdict divergences, and the
  16-name POSIX table independently regenerated from libpcre2 over ~2.4 billion
  probes and found exactly right. The CHECKS did not: UB in the new
  differential's nested-opener shape meant that construct was generated ZERO
  times for `.` and `=` while the header printed 1680; `close_at - from` could
  underflow for a future row and was safe only by an unrelated function's
  implementation detail; the MANIFEST had a duplicated row (and two more the
  critic missed) making its uniqueness guarantee false; and three of four counts
  in tests/reject/CLAUDE.md contradicted this very commit. All fixed, each with
  a sabotage that fails without it.
  **The panel's SECOND wave found a live bug in shipped code**, not just in the
  instrument: `[[:<:]]` and `[[:>:]]` are accepted by libpcre2 ONLY as a class's
  entire content, and pcrec promised module 'classes' for every other position —
  the same over-promise FIX-2 removed for bogus names, surviving for the two
  real names FIX-2 itself discovered. Neither differential could see it: the
  name sweep fixes position, the shape sweep fixes the name, and the defect was
  in the cell of the cross-product neither generates. Also: the fourteen
  graduated `accept` rows asserted only that SOMETHING was emitted, so a
  one-line change that drops `:` from `[a[:b]`'s member set passed every suite
  and the fuzzer; the delimiter space was hand-listed so a construct with no
  registry row was invisible; the name pool had no provenance requirement; and
  tests/registry/ had no guard against its own checks being deleted. All fixed
  and sabotage-validated. New: tests/base/class_brackets.rxt (136 cases),
  `check_posix_positions`, a 255-byte delimiter sweep, and a coverage count plus
  manifest for tests/registry/.
  What landed: `RF_CLASS_DELIM` on the `:` row plus an `open_msg` field (no
  fifth doorway kind — see K3 in known_issues.md and D26); K4's three scan rules
  together, with rule 3 implemented EXACTLY as K4 worded it after two looser
  versions were refuted by the generated sweep; a measured 16-name POSIX table
  (the differential found `[[:<:]]` and `[[:>:]]`, word-boundary assertions my
  hand-written 14 had missed); the 4a doorway sweep registry_check.c never had;
  and two new generated differentials in pcre2_check.c — 1680 class patterns and
  ~150k POSIX name probes, both at zero divergences.
  Original entry follows.
- [FIX-2] as planned — K3 and K4, the class-bracket doorway. THIRD, not
  last, and R8 gave it a SECOND job (C4-7): this doorway is NAME-keyed like the
  verb one and has the same over-promise Q1 just removed, 900x wider. Measured
  2026-08-10: libpcre2 recognises 14 POSIX class names and pcrec answers
  "requires module 'classes'" for all 12531 candidates — its answer does not
  depend on the name at all. Land the 14-name table with the K3/K4 fix; PC-3's
  machinery then differentials it the same way it does verbs, for free.
  **ACCEPTANCE CRITERION, carried over from PC-3's own spec text (R8/C4-9):**
  PC-3 was specced as "the natural home for the finding that pcrec accepts
  `[:alpha:]` — findable mechanically", and that differential was NOT built,
  because it goes red today on a pinned deferred bug. FIX-2 is not done until
  `tests/registry/pcre2_check.c` finds K3 and all four K4 cases MECHANICALLY,
  and the four known-wrong pins in tests/reject/ have moved into the normal
  tables. Also add the `"[%ca%c]"` sweep template registry_check.c is missing —
  its current `"[[%ca%c]]"` only tests doorway 4b.
  **SCHEMA CALL MADE, 2026-08-10 (Frank + D26): NO fifth doorway kind.**
  `RK_CLASSOPEN` was proposed because PCRE2 uses different WORDING at a
  class's own bracket than inside one, so one row could not carry both.
  Under D26 that is TIER 3 and one message serves. Give the `:` row
  `RF_CLASS_DELIM` like its two neighbours — one flag, zero schema change —
  which makes both positions answer alike and leaves `at_class_open` used by
  nothing, so the parameter is deleted anyway. That was the entire benefit
  `RK_CLASSOPEN` was justified by, at a fraction of the blast radius. Still
  to get right: the message must not promise that module `classes` will make
  `[:alpha:]` legal, because it never will.
  R6's testability critic showed the "the fix would be thrown away"
  premise was wrong (K4 is untouched by any selector scheme, and its structural
  scan must exist under every design), and fixing them first gives the registry
  change a correctness target at the doorway it changes most. The four
  KNOWN-WRONG pinned lines in tests/reject/ WILL FAIL when this lands — that is
  the signal working; check each against libpcre2 and move it into the normal
  tables in the same commit

- [Q2] STATE:completed 2026-08-10, WITH SR-9 — MEASURED FIRST: a generated
  sweep of all 256 bytes after `(?` with 45 completions each says libpcre2
  recognises 38 and refuses 217 of the 255 probeable bytes, which reconciles the
  two figures below (217 of 255 probeable; 218 of 256 counts NUL, which is K9's
  territory, not Q2's). pcrec promised module 'modifiers' for all 217. The
  catch-all is now RS_REJECTED carrying PCRE2's own error-111 wording, and the
  eleven real option bytes have rows of their own.
  All four named misattributions fixed and measured, plus TWO the plan did not
  list, both found by the sweep rather than by reading: `(?PX)` is PCRE2 error
  141 with its own message, so bare `(?P` promised a module for 252 of 255
  tails; and splitting the catch-all into eleven letter rows fixed the BYTE and
  left `(?iZ)`, `(?-Z)`, `(?i-Z)` and `(?aPP)` still promising 'modifiers',
  because a row keyed on the first byte cannot see the rest of the run. The
  doorway now reads the whole option RUN, as Q1 made `(*` read the whole name.
  **The run grammar was got wrong in both directions before the differential
  refused it** — first too strict (one hyphen, no hyphen after `^`: an
  UNDER-promise for 24 shapes PCRE2 calls option settings, error 194) and then
  wrong about ordering (PCRE2 stops at the FIRST error, so `(?--D)` is 194 and
  never reaches the illegal `D`). Three candidate rules, each refuted by
  measurement — the same shape as K4, recorded because it keeps recurring.
  Coverage: PC-3 gains a 7650-probe byte differential, a 19448-probe option-run
  sweep and 10200 probes of tail sweeps, each with liveness counters and a
  pattern-set checksum; tests/reject/ gains 20 hand-written rows for the module
  NAMES, which no external oracle can judge. Original entry follows.
- [Q2-original] the `(?` doorway's over-promise, R8/C4-7, and
  **INDEPENDENTLY RE-DERIVED 2026-08-10 by a spec-first writer (D27) that had
  not read the registry** — it measured 218 of 256 bytes after `(?` promised a
  module for syntax PCRE2 does not have, arriving at R8's finding from the
  documents alone. That is the strongest evidence Q2 is real and not an artefact
  of how the registry is written.
  The same report named FOUR TIER-2 MISATTRIBUTIONS to fix while this doorway is
  open, each measured against libpcre2 rather than read from documentation:
  `(?+N)` and `(?-N)` are RELATIVE SUBROUTINE CALLS (module `recursion`, not
  `modifiers`); `(?[...])` is an extended CHARACTER CLASS (not `modifiers`);
  `(?P=` is a BACKREFERENCE and `(?P>` a SUBROUTINE CALL (neither is
  `named-groups`). Note the last pair is exactly the `(?P=` vs `(?P<` split
  SR-9's `tail` field exists for, which is why these two steps are sequenced
  together.
  Original entry follows. 217 of 255
  bytes after `(?` are told a pcrec module will implement a construct libpcre2
  rejects outright (error 111, "unrecognized character after (?"), because the
  catch-all `modifiers` row answers for every byte. Same defect as Q1's, at a
  doorway 217x wider, and the escape doorway is the control that proves it is
  not inherent — 39 rows, zero over-promises. Needs the measured set of bytes
  PCRE2 actually accepts after `(?`; PC-3 then covers it with no new
  infrastructure. **Sequenced WITH SR-9, not before it** (Frank, 2026-08-10):
  they touch the same rows, and SR-9's `tail` field is what `(?P=` vs `(?P<`
  needs anyway — doing them apart means opening the same doorway twice

- [MECH-STRICT] STATE:completed 2026-08-10 — `make strict`, answering R5-Q1. Frank's
  call: OPT-IN, never the default, because a stranger's `make` must not fail on
  a newer gcc's new opinion (the same moving-target argument D26 makes about
  PCRE2). It recompiles every source with `-Werror`, writes nothing and touches
  `build/` not at all, so it cannot break a concurrent `make test` — the first
  version ran `make clean` and did exactly that. Validated: one unused variable
  in `src/core/sb.c` leaves plain `make` green and makes `make strict` fail.
  The project's only warnings-as-errors gate was previously ACCIDENTAL
  (run_trie_identity.sh), and R7 measured that accident catching a class of
  offset bug (archived as MECH-STRICT — the original "[MECH-3]" id collided with the later measurement-wrapper row; text otherwise verbatim)

- [SR-9] STATE:completed 2026-08-10, WITH Q2 — the `byte + tail` design from §7
  of docs/design/design_registry_selectors.md (NOT §2's string selectors, which R6
  rejected with measurements). One new field, longest-tail-wins within the
  selector byte's bucket, ZERO changes to parse.c as predicted, base-tier cost
  unchanged, the 255-byte sweep provably identical — the sweep now passes the
  parser's own tail context, derived from the pattern it built rather than from
  a second transcription, so `[\%c]` cannot drift from what the parser sees.
  Five new rows became twenty-eight: the design listed `(?P<` `(?P=` `(?P>`
  `\N{U+` `\N{}`, and a 256-byte tail sweep of each prefix added the three
  lookbehind tails on `<` (which retired the compound module
  `lookaround/named-groups` entirely) and the ten `(?-<digit>)` relative
  subroutine calls. **The lookup's ordering rule was unguarded on arrival**:
  reducing longest-tail-wins to first-tail-wins produced ZERO failures
  repository-wide, because every tail is one byte except `\N`'s pair and those
  were written longest-first, so row ORDER silently stood in for the rule. Fixed
  by writing them shortest-first — so order DISAGREES with the rule — plus
  check_tail_precedence, which asserts it for every prefix-related pair and
  fails loudly if no such pair exists

- [SR-2] STATE:completed — FOUR DISPATCH POINTS in parse.c and nothing else:
  `pcrec_ext_escape(cx, c, in_class)`, `pcrec_ext_group(cx, c2)`,
  `pcrec_ext_verb(cx)`, `pcrec_ext_class_bracket(cx, c2, cls)`. parse.c keeps
  ONLY the base grammar (literals, `.`, classes/ranges, quantifiers, `|`,
  `(...)`, `(?:...)`, `^`, `$`) and stops growing. Emitted output must be
  BYTE-IDENTICAL across the corpus before and after — this is a pure
  restructure, prove it the way OS-0b did (167 patterns x 3 prefixes x 4 modes).
  BUILT 2026-08-10 as src/parse/ext.c. Proved on 4173 hashed cases against a
  pristine `git archive HEAD` build — the corpus (179 patterns x 3 prefixes x 3
  modes, plus -i and utf8), a 255-byte sweep of eight doorway contexts, and
  tests/reject/'s own strings, comparing stdout, stderr, exit status, the paired
  .c AND the .h. Zero differences. Four departures from the text above, each
  with its own reason: (1) the HANDLER FIELD IS NOT BUILT — every row's handler
  would be NULL and the branch calling it would be dead code no test can reach,
  which is the exact shape of unexercised structure this project keeps losing;
  the four signatures are now FIXED by ext.c, so SR-6 adds the field with a real
  first customer at no extra cost. (2) each dispatch takes an explicit `at`
  offset, since cx->pos has moved past the selector by then and recomputing it
  inside would be a second home for the cursor arithmetic. (3) `RF_CLASS_DELIM`
  was added to the row schema: the collating elements' recognition rule (opens
  only when the matching `X]` follows; the class's own bracket can be the
  opener) is the CONSTRUCT's rule, not base grammar, so it had to move with it.
  (4) `pcrec_ext_class_bracket` also takes `at_class_open`, which is the only
  branch of the four the suite CANNOT see — see K3

- [SR-3] STATE:completed — `pcrec --list-syntax [--flavour F]` dumps the
  table (TSV: syntax, module, feature, flavours, engines, status, note), and
  `pcrec --explain '\v'` answers for one construct. This is the anti-drift
  mechanism, not a convenience: SR-4 depends on it.
  BUILT 2026-08-10 as src/parse/syntax_dump.c, 12 columns rather than the 7
  above — `kind`, `selector`, `diag`, `flags` and `expect` were added because
  SR-4 needs to know how to PROBE a row and what text to expect, and deriving
  either from the other five would put the doorway templates in a second home.
  `expect` is a SUBSTRING of the parser's line ("requires module 'X'", or the
  fixed text verbatim), not the whole diagnostic, for exactly that reason.
  INTERNAL, not public API: the CLI includes core/internal.h for two functions
  that return finished text, since the CLI and the tests are the only consumers
  and promoting into lib/pcrec.h later is the reversible direction. `--flavour`
  validates its argument against the one flavour that exists rather than
  silently ignoring a typo. The format is an interface now, so it FORBIDS tabs
  and newlines in a field rather than escaping them (an escaping scheme is a
  thing every SR-4 consumer would have to reimplement identically); tests/cli
  case 10 asserts it by counting fields, 49 -> 73 CLI checks

- [SR-4] STATE:completed — tests/reject/ ITERATES the dump instead of its
  hand-written 93 entries, and docs/pcre2_compliance.md is RENDERED from it.
  Adding a row then covers itself in both. Keep the accept-controls
  hand-written — they must not come from the same source as the thing they
  control, or the control is vacuous (the trie-identity lesson). WARNING (R4
  critic finding): `\x{...}` and the possessive `+` have NO registry row, so
  iterating the dump silently drops their existing tests/reject/ coverage unless
  SR-4 special-cases them explicitly. Same for any construct rejected with fixed
  text rather than a "requires module" diagnostic.
  BUILT 2026-08-10, with the word INSTEAD deliberately not honoured. Iteration
  was ADDED (66 checks, 112 -> 179) and the 93 hand-written rows KEPT, because
  the trade the step text asks for gives away the property it is trying to
  protect: since SR-2 the module names live in ONE place and the parser renders
  its diagnostics from it, so a test that reads the same table cannot see a
  WRONG name. MEASURED rather than argued — changing `\d`'s row from `classes`
  to `misc` fails 2 hand-written checks and 0 iterated ones; changing a row's
  `syntax` to something that does not reach its doorway fails 1 iterated check
  and 0 hand-written. The two layers answer different questions. Also measured
  and worth carrying: a NEW row with a plausible-but-wrong module and no
  hand-written entry is caught by NEITHER — R4's residual circularity is
  UNCHANGED by SR-4, not closed by it, and the only external source of truth
  for those rows is libpcre2 (see PC-3). docs/pcre2_compliance.md is NOT
  rendered wholesale — that would replace a survey with an inventory; a
  generated construct INDEX is spliced into it between markers, and two
  make-test checks hold the seam (index matches the dump; every module named in
  the prose exists in the registry). Both positive-controlled

- [PC-3] STATE:completed — AN EXTERNAL SOURCE OF TRUTH FOR THE REGISTRY, which
  is the one thing SR-4 could not provide. Iteration reads the same table the
  parser renders from, so a row that is plausibly wrong in the single home is
  invisible to it (measured under SR-4: a new row with a wrong module and no
  hand-written entry is caught by nothing). Module NAMES are pcrec's own
  taxonomy and no outside authority can check them — but two things about every
  row ARE externally checkable against libpcre2, and nothing checks them today.
  BOTH RESTATED 2026-08-10 (R6): check (b) was written with the POLARITY
  BACKWARDS here, and as written would have passed every fabricated row it
  exists to catch. (a) every `RS_REJECTED` row claims "PCRE2 rejects this too" —
  libpcre2 must reject the row's `syntax`, AND with a matching error identity,
  not merely reject it for some other reason. (b) every `RS_MODULE` row claims
  PCRE2 HAS the construct and pcrec has not implemented it — so libpcre2 must
  COMPILE the row's `syntax`. A row naming a construct PCRE2 does not have will
  fail to compile there, which is the fabrication check. Note `syntax` cannot be
  handed to libpcre2 unchanged in every case; some probes need a context wrapper. tests/fuzz/
  already links libpcre2 through a dlopen probe, so the machinery exists. This
  is the natural home for the finding that pcrec accepts `[:alpha:]` (K3) —
  found by hand, and findable mechanically

## 2026-08-11

- [R3.3] STATE:completed (date inferred) — M2.8 IS structurally testable and the journal concluded the opposite (R3 semantics critic F4). Emitted C is byte-identical between the shipped build and a trie-disabled one (`elig[j] = false`) across 4722 patterns, and the check is cheap — a 500-pattern enumeration runs in 1.4 s with NO gcc, and flags 14/500 under the disjointness sabotage and 12/500 under the rule-1 sabotage, where the .rxt corpus catches the disjointness sabotage with 2 cases total. Add it as a codegen-level check; it is a far stronger net than subject sampling RESOLVED: tests/codegen/run_trie_identity.sh, wired into `make test` — 500 patterns byte-identical in ~4 s via a -DPCREC_NO_TRIE reference build, with THREE deterministic positive controls at 4, 8 and 256 branches (patterns whose NFA fits the cap only when factored) so the check cannot pass by both builds being unfactored. The first version had ONE control, at 256 branches, while every corpus pattern has 3..8 — a critic defeated it in one clause (`nbr >= 100 &&`), leaving the whole of `make test` green with the trie deleted for every hand-written pattern. The controls must fire INSIDE the corpus's own range. Sabotage-validated four ways, exact edits recorded in tests/codegen/CLAUDE.md: disjointness guard off 21/200 and 64/500; rule-1 accept split hoisted 38/200 and 94/500; trie off in the shipped build 0 differ, only the controls fire; `nbr >= 100` threshold 0 differ, the 4- and 8-branch controls fire. D16.

- [R3.4] STATE:completed (date inferred) — the D11 forward-side regression net has a hole (R3 semantics critic F3): none of the 13 patterns in tests/base/eol_scan_avoidance.rxt produces a forward skip state whose plain accept flag is set, so the FORWARD half of "scan avoidance before accept evaluation" — the half D11 is written about — has no committed case. The critic built 199 such patterns (`a.*|b$`, `=.*|x$`, `a[^\n]*|\n$` family) and all were correct; add one to the .rxt file RESOLVED: 6 patterns / 44 cases added, oracle-verified. The critic's suggested family was right but incomplete — the load-bearing case turned out to be the NON-EOL half: `[a-z].*|q$` compiles to a machine with no EOL variants at all (`[a-z].*` subsumes `q$`), and `a.*|b` / `=.*|;` carry no `$` so that coverage cannot evaporate. Sabotage-validated on both halves separately: EOL accept restricted to the boundary fails 3, non-EOL post-skip `last = pos` dropped fails 10, and the original 13 catch NEITHER. Also found: this file does not catch relaxing the EOL skip bound n-1 -> n either, despite its header — other tests/base files do (3 cases).

- [R3.5] STATE:completed (date inferred) — compare gate margin admits a 29% uniform regression (R3 claims critic F1): GATE_MARGIN=0.70 fires only below 1.43x, so M2.10's 27% case would NOT have been caught (only the 43% one was). Either tighten the margin with more BENCH_TRIALS, or gate per-case against a recorded spread rather than one global margin RESOLVED: per-case margins, floors.tsv gains a 4th column, margin = clamp(1/(spread*1.05), 0.70, 0.90) (D17). The CEILING is fixed rather than derived — the box noise floor is ~10% even at median-of-7 — and the floor keeps a noisy case no looser than the old default, so this is never a loss of strictness. Validated: a uniform 27% regression now fails 8 of 9 cases where it previously failed 0. Case (i) (latency, spread 2.04x) is the one that still cannot see it, and the gate now PRINTS its own weakest case every run instead of leaving that to be recomputed by a critic. Margins measured 2026-08-09 on a quiet box; floor VALUES deliberately not re-baselined (the run reproduced them within 2%).

- [DOC-1] STATE:completed 2026-08-11 (eighth session) — the ambiguities a
  spec-first writer found reading the goal documents cold (D27, 2026-08-10)
  were RE-DERIVED by a fresh cold reader (the originals' scratchpad path was
  dead, exactly as this step predicted) and reconciled: ELEVEN findings, all
  eleven fixed in one commit. The load-bearing ones: `\N{U+hh..}` was
  assigned to module `classes` by the hand table and `unicode-props` by the
  generated index IN THE SAME DOCUMENT, with the resolving cross-reference
  pointing at a note that did not exist (fixed; the note now exists and
  covers the three-way `\N` spelling clash, citing K10); README described
  the shipped, bench-gated M2 optimizer as roadmap and carried a corpus
  count stale since the first commit (fixed; counts now read from runs);
  `^`'s `OK-LIMITED` stated no limit — probed, its only correctness gap is
  multiline exactly like `$`, so it is `OK` with D8's engine caveat named
  as SPEED (fixed); `OK-LIMITED` had accreted three meanings (vocabulary
  now requires the limit's KIND per row); the `becomes` vocabulary lacked
  the generated index's `never` and read `—`-plus-revisit-note as a
  contradiction (both defined); lib/pcrec.h now scopes D18's caseless
  zero-cost claim per D23 and states that streaming is M3's, not part of
  today's generated contract; APPROACH.md's "req. N" citations are flagged
  as founding-brief numbers with no in-repo referent (FLAGGED TO FRANK: the
  brief could be checked in to make them resolvable); D18 carries its D20
  supersession marker; D26 gained the which-PCRE2 addendum (the pinned
  oracle, 10.46; version bumps are deliberate re-measurement events).
  Registry/compliance checks green after the edits (143/143). The reader's
  disclosure recorded the FOURTH D27 ambient-injection instance
  (docs/CLAUDE.md + lib/CLAUDE.md, K10 overlap disclosed and unused)

- [MOD-STATE] STATE:completed — (RETIRED 2026-08-11, subsumed, never built as written: MOD-0.1's amendments record it as "RETIRED, subsumed by" Part II §12.2's lexer-in-count-mode and the slice-7 running-count infrastructure — see [MOD-0.1].) TWO MODULES INHERIT A NON-LEXICAL DEPENDENCY,
  measured at R6 and easy to design past accidentally. `(?(R)` is a recursion
  condition or a named-group condition depending on whether the pattern declares
  a group called `R` ANYWHERE — including AFTER the condition; `\ddd` is octal or
  a backreference depending on the capture count seen so far. Neither is
  resolvable from the doorway text, so module 'conditionals' needs a
  whole-pattern group-name table (a pre-pass or a fix-up pass) and module
  'backrefs' needs a running capture count, with its DIAGNOSTIC chosen from that
  count rather than fixed. Both constructs are cleanly rejected today with the
  right module named, so this is a design constraint, not a bug — recorded so no
  handler signature is designed on the assumption that a row can identify the
  construct. See D24's "THE LIMIT OF THE TABLE" and K2

- [TS-2] STATE:completed 2026-08-11 (subagent; reviewed, wired into `make
  test`) — concurrency test for GENERATED code: 8 threads sharing one
  compiled matcher over different subjects, results required identical to
  the single-threaded run, under `-fsanitize=thread` — across FIVE
  differently-shaped emitted engines (anchored fast path, memchr literal,
  $-EOL/M2.12, self-loop skip states with a liveness grep, alternation
  trie), because the property is about the generated code and one pattern
  tests one shape. Sabotage-validated (planted race caught, marker-count
  guard on the patch). tests/thread/

- [TS-3] STATE:completed 2026-08-11 (same change) — concurrency test for
  the LIBRARY: 8 threads, each its own (pattern, prefix, caseless) job —
  six accepting, two rejecting so ctx_fail/longjmp runs concurrently too —
  the whole library built WITH TSan, every threaded compile byte-identical
  to its single-threaded baseline. Sabotage-validated with a file-scope
  counter planted in a COPY of compile.c — exactly the shape this step
  named. tests/thread/

- [MECH-1] STATE:completed 2026-08-11 (subagent; reviewed + integrated by the
  main session; subsumes MECH-2 as predicted). tests/mech/: 20 sabotages
  encoded as literal before/after edits (lib/replace.py refuses to run unless
  the before-text occurs exactly N times and the after-text landed), one
  FRESH `git archive HEAD` tree per sabotage — never revert-and-reuse, the
  MECH-2 lesson — suites run in the copy, matrix printed with the measured
  SHA. First full run at 499d39d: 20/20 DETECTED; found the trie ".rxt
  corpus" figure stale (2 → 6, alternation_trie.rxt grew) and root-caused
  the "new wrong row" sabotage's change from 0/0-undetected to 1 fail (the
  exact iterated-count tripwire added since — visible, not fail-proof; SR-4
  blind spot narrowed, not closed). Two sabotages deliberately NOT encoded:
  the UB rule-1 form (its own docs say the count is unstable) and the
  prose-only memory-safe rule-1 variant. `make mech` runs it (not in `make
  test`: ~6 min of tree builds). Both hand-written sabotage tables now point
  to the generator for figures and keep the edits + lessons. — GENERATE the sabotage tables rather than hand-writing them. Every "disabling X fails N cases" figure in the docs is a hand-copied number that goes stale silently; this session shipped three wrong ones (a figure never measured, one from a tree with two sabotages stacked, and one whose sabotage form was UB so its count was unstable). Build a script that owns the sabotage edits, applies each to a pristine tree, verifies the edit actually applied, runs the suites, and prints the detection matrix. Docs then cite its output and drift becomes detectable by re-running it

- [MECH-2] STATE:completed 2026-08-11 — SUBSUMED by MECH-1, exactly as the
  last sentence below predicted: tests/mech/ makes one fresh `git archive
  HEAD` tree per sabotage and its replace.py refuses to continue unless the
  target text was found exactly N times and actually changed. — a pristine-sabotage-tree helper. The contaminated 132/200 figure came from a hand-rolled copy+sed+`git checkout` loop where the revert silently failed (`|| true` inside a tarball copy that is not a git repo) so sabotage 2 landed on top of sabotage 1. One helper that makes a fresh tree per sabotage, asserts the target text was found and changed, and refuses to continue otherwise. Subsumed by MECH-1 if that lands first

- [R3.1] STATE:completed (date inferred) — skip states have NO throughput guard anywhere (R3 critic, reframed): all four `make bench` patterns emit ZERO skip tables, so generated code is byte-identical with pick_skip_states returning 0 — bench cannot detect a skip-state regression at any count including zero, and D12's sabotage validation attributed to "prefilter+skips" was measuring the prefilter alone. Asserting a skip-table COUNT is the WRONG fix: the cap of 4 buys nothing measurable (730.8 vs 740.1 MB/s at cap 1, interleaved x9). Add a bench case whose hot state actually self-loops (`.*=.*` over a key=value subject is the shape), then the guard has something to measure RESOLVED: THROUGHPUT case (e), `=[^\n]*!` over an 8 MB key=value subject, ~92% of bytes consumed inside the skip loop. NOTE the suggested shape `.*=.*` is WRONG and the case records why: it matches at offset 0 ending at 127, so an 8 MB run exits after 127 bytes and reports 32 GB/s — R2-B4's exit-latency mistake again. Budget 1000 MB/s = measured-median/1.75 (D12). Sabotage-validated: pick_skip_states returning 0 measures 341.7 MB/s and fails the budget, AND trips the case's own hard-error check that a skip table is still emitted.

- [R3.6] STATE:completed 2026-08-11 (subagent, reviewed; provenance in tests/bench/compare/run_history.tsv — case (i) re-baselined 69.72 → 50.56, the MEDIAN of ten independent quiet runs spanning 1.94x, with rebaseline.sh as the repeatable mechanics) — compare floors.tsv case (i) is 10.4% off the run that verified the others (77.00 vs a recorded 69.72) and its 0.700 margin means this gate CANNOT see it move, so the discrepancy is self-concealing (R3 guards critic F11). The floor values also come from a run that is not in the repository at all — they match neither results-ubuntubudu-20260809.md nor -2.md. Either re-baseline (i) deliberately and record the run, or establish why the latency case drifts; do not leave a floor whose own gate is blind to it

- [R3.7] STATE:completed 2026-08-11 (subagent, reviewed; run_history.tsv + gate.sh EARN=1 report the earned ceiling, gated on 8 distinct dates; first run says all cases too thin, ceiling deliberately unchanged; the unmeasured ~10% claim corrected in tests/bench/ and D17's postscript) — the 0.90 margin CEILING is over-conservative and its stated justification was unmeasured (R3 guards critic F12): "this box's noise floor is ~10% even at median-of-7" appears in D17, gate.sh and floors.tsv and is backed by no measurement in this repo, while the three runs the repo DOES contain move by <=3.3% run-to-run on eight of nine cases. Cases a-h would tolerate 0.95 with 1.5-3x headroom. Collect enough independent runs to earn a tighter ceiling honestly, then raise it — three runs is too thin a basis to gate on, and tightening on it would repeat the error rather than fix it

- [R3.8] STATE:completed 2026-08-11 (subagent, reviewed; six quiet runs: COMPILE and GCC_O1/O2 are the two REAL exceptions, single-sample measurements with 1.87x observed swing — documented, not tightened onto noise; LINEARITY's 2.08x was a stale-reference artifact, fresh median gives 1.61x slack) — four of nine bench budgets are LOOSER than the median/1.75 D12 claims for all of them (R3 guards critic F8): COMPILE 3.60x, GCC_O1/O2 9.13x each, LINEARITY 2.08x. The GCC pair sits inside the "9x-300,000x loose" band D12 opens by condemning. Either tighten them to the stated rule or document each exception the way the BITMAP case documents its tighter one. The claim itself has now been asserted three times and refuted twice; it is currently corrected in tests/bench/CLAUDE.md but still stands unfixed in run_bench.sh's header and in D12

- [R3.9] STATE:completed 2026-08-11 (subagent, reviewed; case (e) subject now matches so the REVERSE skip loop runs — instrumented 8,388,606 iterations each direction; budget 1000 → 700 from five quiet run-medians /1.75; sabotage re-validated at 7.4x; known residual: rx_fs3 still unreached, noted in the code) — bench case (e) is a PRESENCE check with a throughput number attached, not a regression gate (R3 guards critic F19/F22). Capping the skip run at 8 bytes throws away 93% of the loop's reach and still measures 1.15-1.45x ABOVE the 1000 MB/s budget; only near-total deletion (3.1-4.1x) fails it, and the case's own `grep rx_fs[0-9]+\[256\]` hard error already catches deletion for free. D12's own words apply: "a budget that cannot fail is documentation, not a gate". Case (e) also covers ONE forward, NON-accepting skip state — its second emitted skip table (rx_fs3) is entered zero times, so any regression in pick_skip_states' multi-state selection is invisible, and its reverse skip table never executes because the pattern cannot match. REVERSE skip loops have NO throughput coverage anywhere in the suite, which matters because M2.10/D13's negative result rests on the suspicion that a backward byte-at-a-time skip loop loses to the reverse table walk. Either tighten the budget until a graded skip regression fails it, or add a matching subject so the reverse machine runs

- [R3.10] STATE:completed 2026-08-11 (subagent, reviewed; load re-sampled AFTER measuring in run_bench.sh AND compare.sh, gate.sh consumes the load block and downgrades to a distinct exit 2 INCONCLUSIVE per D14; summary prints start/end load) — run_bench.sh reads /proc/loadavg ONCE, before any measurement, and that single sample decides LOADED for the whole run (R3 guards critic F23). Observed 1-min load on this box during four minutes of measuring: 1.94 -> 6.01 -> 8.93 -> 13.32 -> 16.04, against LOAD_LIMIT 6.0. A run starting at 5.9 is judged quiet and then measures under a load of 13; the critic saw a HEALTHY build median 575.5 and 964.2 MB/s on case (e) in such windows, i.e. a clean tree failing its own gate. Re-read the load AFTER the measurements as well and downgrade to INCONCLUSIVE if either sample is over — the D14 machinery for reporting that already exists

## 2026-08-12

- [PC-4] STATE:completed 2026-08-12 (MOD-0.3e, landed WITH module `classes`
  as required) — the SEMANTIC differential, R8/C4-2: 273 deterministic
  patterns × 271 shared subjects, compile verdicts both directions + 62,872
  match cells vs libpcre2 in make test (~2.5 s; skip-loudly), populations
  predicted exactly before the first run and confirmed; includes the `-i`
  axis (first external oracle contact). Liveness proven both axes; the
  first bitmap sabotage found the Makefile's hand-maintained header deps
  missing cls_bits.inc — the sabotage never entered the binary — fixed in
  the same change. `\v`'s semantics — the incident the registry was built
  for — are externally verified at last

## 2026-08-13

**The MOD-0 arc** (design, build-out and close of the module-ports system): [PARSE-1] through [MOD-0.8], archived together here under MOD-0's own close date (2026-08-13) because the arc is one continuous piece of work; each member row below carries its own completion date in its own text, which may be earlier (2026-08-10 through 2026-08-13).

- [PARSE-1] STATE:completed (2026-08-11 — designed, panelled, built, checked and
  sabotage-verified; see **D31**, which partly CORRECTS the diagnosis below).
  **The headline: R10/C3-6's "cannot recover the top-level branch count" is true
  only of recovering it FROM THE AST AFTERWARDS. `p_alt` always computed the
  number and threw it away** — `p_atom` consumes a group as ONE atom, so the
  erasure sits BELOW `p_alt`'s loop and cannot perturb its count. The group node
  stays erased; an `A_GROUP` wrapper would have been built to fix a
  mis-diagnosis. Delivered: `p_alt` reports `AltInfo {nbr, last_bar}` (a struct,
  because `ctx_fail` requires a POSITION and D26 puts pcrec's own offsets in
  tier 2); the group case split into `p_group`/`p_group_body` so entry and exit
  bookkeeping each sit on one path; `caseless` moved from the const caller-owned
  options into `Ctx`, saved/restored at the group boundary (measured 17/17 —
  `(?i)` leaks across sibling branches and restores at the immediately-enclosing
  `)`). A THIRD defect, not in R10's list, was found by asking what `modifiers`
  needs. New suite `tests/parse/`: 16,384 bodies, 32,768 libpcre2 arbitrations
  of an independent reference counter, zero disagreements, three sabotages of
  `p_alt` itself verified caught. **Still open and now MOD-0.1's:** a doorway
  that returns a node still has it silently discarded — **make `p_alt` a usable
  module callback. Split
  out AHEAD of MOD-0 by D30 §5** (R10/C3-6 measured both defects). (a) The GROUP
  NODE IS ERASED: `p_atom`'s group case returns the body with no wrapper
  (`parse.c:275`), so `(a|b)|c` and `a|b|c` build the identical AST — verified,
  the generated C is byte-identical apart from the pattern comment. PCRE2 needs
  exactly that distinction: `(a)(?(1)(a|b)|c)` compiles while `(a)(?(1)a|b|c)`
  is error 127, "conditional subpattern contains more than two branches", so a
  `conditionals` semantic port calling `p_alt` back cannot recover the
  top-level branch count. (b) The depth DECREMENT sits at `parse.c:266`, AFTER
  the doorway call at `:259`, so it is on a path a module never reaches —
  D29's "one depth counter, not two" is right as a rule and unimplementable
  against today's control flow.

  Base-grammar work on the hot path, so it is its own step rather than a
  passenger inside MOD-0: independently testable (the AST-identity property is
  what `tests/codegen` pins), and the callback should EXIST before the first
  semantic port needs it rather than being discovered mid-module. Note this
  spends SR-9's "parse.c call sites changed: 0" lineage, deliberately.

- [MOD-0] STATE:completed — (CLOSED 2026-08-13, fourteenth session, at 569b48f
  with MOD-0.8's checkpoint: the arc ran MOD-0.1 through 0.8 across sessions
  eleven to fourteen — ports/returned-claims/endpoint rule, first producers
  classes+modifiers, verbs migration, unicode-props recogniser, the --explain
  rewrite, and the R20 close that fixed two tier-1s the arc's own instruments
  found. Follow-on rows spawned during close: [STD1] (D37 default-on),
  [SAN-1]+[TT-1] (next session), [SR-10], boonies tier per queue discipline.)
  **MODULE STRUCTURE: define a module's PORTS, and
  build two or three real ones to shape them.** Frank's call, 2026-08-10,
  arising from Q2: option-run parsing had nowhere good to live. `ext.c` exists
  so parse.c holds the core syntax and nothing else, and its role is to find the
  right handler for a matched extension — NOT to accumulate every construct's
  body parser. `registry.c` is declarative data. Q2's option-run grammar is
  currently in registry.c, which matches neither (see the PROVISIONAL note above
  it), and `\p{...}` alone — a loose format needing normalisation, not just
  validation — would outweigh everything in ext.c today.

  The shape: a module exposes SEVERAL PORTS. (1) SEMANTIC, what the construct
  means, which is what SR-6's handler field was for. (2) SYNTAX, for constructs
  whose body is complicated. (3) optimisation, deferred — do not design for it
  yet. The doorway tables establish from key+tail that this IS an options group,
  then call the row's syntax handler for the details.

  **Why the syntax port is needed before any semantics exist:** every module is
  unimplemented today and body parsing is STILL required, because "is this a
  construct at all" is tier 2 under D26 and exact. The two ports have different
  lifecycles, which is what makes them two ports rather than one handler with a
  mode flag.

  A verdict shape that fell out of Q2's measurements rather than being invented
  — PCRE2 distinguishes two kinds of bad body, and only one means "no construct":
  `SYN_OK` / `SYN_MALFORMED` (still promise the module: `(?i-m-s)` is error 194,
  a malformed option setting; `(?0J)` is error 114, a malformed recursion call) /
  `SYN_NOT` (errors 111 and 141 — no construct, promise nothing). Q2 got that
  distinction wrong in BOTH directions before the differential refused it.

  Pick two or three modules that capture DIFFERENT pieces rather than the
  easiest ones — a port designed against one example inherits that example's
  alphabet, which is D27's lesson applied to interface design. Candidates:
  `modifiers` (a simple body; semantics that fold into parse-time state per
  D23/OS-1, not into the engine), `classes` (set-valued return currency, a
  name-keyed body, AND it is the forcing function PC-4 is blocked on), and
  `unicode-props` (the case that breaks a validate-only signature, because it
  must hand back a NORMALISED name). `verbs` is the migration test — it already
  has a name scan in ext.c, so moving it proves the port fits existing code
  rather than only greenfield.

  Files in `src/parse/modules/` (or similar) — decide with the interface. Q2's
  `pcrec_registry_option_run_ok` is the first thing to move.

  **DESIGNED 2026-08-11 — see D29, which supersedes the "key+tail then call the
  syntax port" shape sketched above.** A row names a RECOGNISER; the selector
  byte is only a bucket key; every recogniser in a bucket is called and exactly
  one may answer; two answers is a registry defect, not a precedence question.
  The doorway's three answers are CLAIM / REFUSE / DECLINE, which are NOT
  D28's SYN_OK/SYN_MALFORMED/SYN_NOT — that pair of taxonomies had been treated
  as one thing, and `SYN_NOT` conflates `[[:foo:]]` (an error) with `[a[.b]` (a
  pattern PCRE2 compiles). Recognisers are PURE and allocate nothing; the
  SEMANTIC port takes `Ctx *` and recurses into `p_alt` for a nested body.
  Read D29 before writing any of the substeps below.

  **RESOLVED BY D30, 2026-08-11.** Read D30 before any substep: declared RANK
  replaces "exactly one may answer"; the doorway's answer is three facts rather
  than an enum; the compile MODE is bound and is pcrec's own decision; `p_alt`
  is fixed FIRST as [PARSE-1]; the digit buckets are a stated exception whose
  module attribution belongs to the semantic port; `classes` is built before
  `modifiers`; K10 ships known with MOD-0.6. The history below is kept because
  the refutations are the reasons.

  **R10 PANEL, 2026-08-11 — MOD-0.1 and MOD-0.2 were BLOCKED on a redesign; see
  `docs/dev/reviews/2026-08-11-r10-mod0-design.md` and D29's inline `[R10]` marks.**
  Five critics reviewed the design before any of it was built. The spine holds;
  the ambiguity guard, both proposed controls, and four measured facts do not.
  TWELVE dispositions are listed at the end of R10 and they are the
  specification for the redesign. Three of them (9-12) came from a critic's
  SECOND delivery, after this note had already been drafted from its first —
  the prod is necessary and not sufficient, so poll again after prodding.
  Disposition 10 adds work this plan did not have: **MOD-0 includes a parse.c
  change**, because `p_alt` erases the group node (so `conditionals` cannot
  recover the branch count for PCRE2's error 127) and the depth decrement sits
  on a path a module never reaches. The three that change the most work: "exactly one recogniser
  may answer" fires on a CORRECT registry (every tailed bucket has a tail-less
  fallback whose honest recogniser is "always matches"); a UNIQUENESS guard was
  traded for a REACHABILITY one, so `check_tail_precedence` is NOT retired until
  its replacement catches what it catches; and `registry.c:62-72` already
  forbade this signature, because `\12` is octal or a backreference depending on
  a running capture count and that decides its MODULE, which is tier 2 and exact.

- [MOD-0.1] STATE:completed 2026-08-11 (eighth session). CLOSED against its
  landing bar, all three conditions measured: (1) BYTE-IDENTITY across
  1,045 patterns vs the pre-MOD-0.1 baseline daf3518 — 1,029 identical, 16
  differences all on the guarded exception list (6 K14 no-promise
  diagnostics, 10 K12 endpoint cells including the two enumerated
  evaluation-order cells pinned at tests/reject/run_reject_tests.sh:230-231),
  0 unguarded, and no exception touches an emitted out.c; (2) SPEC-MOD0
  9 pass / 0 fail / 1 awaiting, where the one awaiting (check07,
  AWAITING-POPULATION) awaits a MODULE (MOD-0.3+'s to provide), not a
  surface — every surface MOD-0.1 owed exists and armed its check (01
  self-armed, 02/04/06/10 armed by D27 authors, 07's comparison armed and
  its instrument proven live); (3) full suite, strict, verify_rxt, fuzz,
  bench, mech all green. K11, K12, K13 (at FIX-3), K14 closed along the
  way. The slice history below is the step's record.
  (WAS: STATE:started 2026-08-11, sixth session, after FIX-3 landed;
  SLICES 1-2 LANDED same session: the ROADMAP column with the K14 fix at
  8e5ab5a, the quantifiable column at 41a31a1 — check10 flipped from
  awaiting to PASS and caught two transcription bugs on the surface's
  arrival. SLICE 3 LANDED seventh session: the class_expect column —
  values measured by tests/probes/probe_class_expect.c and cross-validated
  44/44 against the SPEC-MOD0 pins BEFORE transcription; check04 armed by
  a spec-side subagent (denied src/) and flipped awaiting→PASS; SPEC-MOD0
  now 6/0/4; registry_check enforces the pairing (44 esc/class-bracket
  rows carry a value, 56 group/verb rows carry none) and the vocabulary,
  three sabotages each caught with exactly one named failure; dump is
  15/6 fields, emitted code spot-checked byte-identical 10/10 vs HEAD.
  SLICE 4 LANDED seventh session: the LEXICAL row kind as RF_LEXICAL on
  {\Q, \E, (?#} (§13.3 — no behavior change, refusal strings verified
  byte-exact; the macros force QF_LEXICAL so they cannot disagree with the
  measured column; registry_check requires RF_LEXICAL <=> QF_LEXICAL both
  directions, sabotaged both ways — the false-lexical-CELL direction is
  check10's catch, verified with a doctored dump, not registry_check's,
  whose pairing a self-consistent macro sabotage rightly survives).
  SLICE 5 LANDED seventh session: the returned-claims epilogue (D33 §5) —
  doorways return a tagged ExtResult with the diagnostic formatted at claim
  time, pcrec_ext_finish is the ONE epilogue, parse.c call sites consume
  the value and end in internal-error walls (the PARSE-1 fallthrough
  discard and K11's noreturn UB both structurally gone; K11 CLOSED, repro
  re-run clean in a stub tree). Byte-identity: 952-pattern differential
  (registry probes + corpus + per-doorway byte sweeps) vs the pre-epilogue
  build, zero differences over exit/stdout/stderr/out.c/out.h, instrument
  sabotage-validated; full suite, strict, verify_rxt 100%, fuzz seed 1
  zero divergences. EXT vocabulary is deliberately the exercisable subset
  {NOT_MINE, REFUSAL}; SCALAR/MEMBERS/NODE arrive with the first port that
  can produce them, each with a probe false the day before (D33 §9.3).
  SLICE 6 LANDED seventh session: the endpoint rule (design §16 as
  R14-corrected — K12 CLOSED). Five steps in p_class, the (bracket, high)
  deviating cell still implemented BY pair_opens per R14; SET-shape
  certified from the measured class_expect column THROUGH the epilogue's
  returned claims (ep_set_certain, §16.3(e)'s payload, exercisable
  subset); certification scoped to all-forms rows (ten char-type escapes,
  known POSIX names both sides) with the \p boundary pinned as deliberate
  (PCRE2 147 for [0-\p{Foo}] — owned by unicode-props' first WIDE producer;
  MOD-0.6 landed recogniser-only and deliberately kept the boundary,
  design_notes_mod06.md §8.2). 42
  cells measured first (probe_endpoint_k12.c), ten failing-then-passing
  pins + seven boundary pins + two accept-controls (reject counts
  265/99/65, three new MANIFEST entries); 952-pattern differential vs
  pre-slice HEAD shows exactly the one changed cell it contains; full
  suite, strict, verify_rxt, fuzz, SPEC-MOD0 6/0/4 all green.
  SLICE 7 LANDED seventh session: the running capture count (§18.1 —
  Ctx.ncap at p_group_body's hook, incremented at the opening paren so a
  future \12 consults the right value) + the external channel
  (pcrec_count_groups parse-only entry, CLI --count-groups; refusals keep
  pcrec_compile's exact diagnostics — leftmost refusal, no count for a
  pattern pcrec does not fully know). Oracle-verified: python re agrees
  10/10 hand cells + 300/300 generated base-tier patterns; emitted code
  byte-identical 5/5; cli case10 grew 10 assertions (85→95). The PENDING
  LIST and end-of-parse check are DEFERRED to module backrefs by D33
  §9.3's own rule: a list nothing can write is unexercised structure —
  every construct that would record a reference is refused today, so the
  pass condition would hold vacuously (R11/C4-1's shape). check02 armed
  by a spec-side author (denied src/) against the channel.
  SLICE 8 LANDED eighth session: the ASK contract (§18.2 as ruled — three
  `want` levels CLAIM/VERDICT/RESULT, NO `may` axis) threaded through the
  four doorway signatures; parse.c's six call sites all ask WANT_RESULT;
  ext_gate demotes RESULT→VERDICT unconditionally (the §5.4 gate with an
  empty enabled set — floors at VERDICT, never CLAIM; the enabled-set slice
  replaces the constant with the membership test); ExtResult gains
  `answered_at` (the post-gate level, nothing on the compile path reads it)
  so the demotion is EXTERNALLY OBSERVABLE: `--probe-ask WANT [--] TEXT`
  (pcrec_probe_ask in syntax_dump.c) drives ONE doorway call placed exactly
  as parse.c would place it — bytewise scan to the first doorway opener,
  full-text coordinates, `(?:` excluded exactly as the base grammar excludes
  it — and reports the REAL cursor before/after: the check06 channel.
  Cursor rule holds measured: 99/100 rows (the `(?:...)` row is the one
  deliberate non-route) × 3 want levels, cursor unchanged everywhere.
  Byte-identity 952-pattern differential vs pre-slice build: zero
  differences. cli case10 95→109, with the in-repo cursor sweep FLOORED at
  198 probes and the gate demotion pinned as a cell (revisit alongside
  check07 when the first module is enabled). Three sabotages, each caught
  by the predicted assertion set: cursor breach under !RESULT (82/82
  probes + exact-cell), gate returning want unchanged (the demotion pin,
  exactly 1 failure), REFUSE dropping answered_at (2 failures).
  SLICE 9 LANDED eighth session: the enabled-set/toggles surface. enabled.c
  — ONE home for the set (process-wide, written once by the CLI before any
  compile; deliberately NOT a pcrec_options field, D20), `--features LIST`
  (module names from the dump's module column, all/none, unknown names
  refused BY NAME); scans.c — the always-live extent scans extracted from
  ext.c (K4 delimiter-pair scan + pair_opens predicate + verb-name extent),
  pure over (pat,patlen), named per check01's discovery convention, TU
  never links the enabled symbols (nm verified: ext.o carries the undefined
  ref — the gate at the seam — scans.o carries none); ext_gate became the
  real per-row membership test (after row choice; NULL row and RS_REJECTED
  always demote; an ENABLED row keeps WANT_RESULT so a refusal's
  answered_at distinguishes gate-open-port-missing from gate-closed).
  check01 SELF-ARMED and PASSES (4 symbol/TU pairs, 1 recogniser TU);
  SPEC-MOD0 8/0/2 (check06 in flight with its D27 author, check07 needs
  its comparison written now that the surface exists). Byte-identity: the
  952-pattern differential vs the PRE-SLICE-8 binary still zero differences
  (default empty set is inert). cli case10 109→117 (gate-open pin,
  per-module pin, open-gate-moves-nothing pins, refused-by-name,
  byte-identical compile under --features all — whose first version paid
  the emitted-#include basename lesson a THIRD time). Sabotages:
  check01's own one-reference-from-scans.c (caught, object+symbol named),
  gate-ignores-set (caught by the answered_at pin).
  Remaining: check06 merge (author in worktree), check07's comparison
  (spec-side author, surface now exists), then the byte-identity bar)
  (UNBLOCKED 2026-08-11 by **D32**, which resolves
  the interface after three panels — R10 refuted D29, R11 refuted parts of D30,
  R12 refuted the alternative and produced the resolution. **Read D32 before any
  substep.** In one line: a row names ONE PARSER FUNCTION taking `Ctx *` (not a
  pure recogniser plus a semantic port); functions are POSITIVE and LOCAL, each
  knowing only its own form; RANK is a LOCAL TIEBREAK present only where rows
  clash, and the bare fallback answering "always" is CORRECT; multiple answering
  is normal and EQUAL RANK among answerers is the defect; `sel` demotes from key
  to a checkable pre-test; the terminal outcome is the ROW'S EXISTING vocabulary,
  not a uniform enum; and **purity is PER-DOORWAY**, which drops D30 §6's digit
  exception entirely because a parser-continuation function has the running
  capture count. Rejected and recorded so they are not re-proposed: declaration
  ORDER as the rule (refuted on the shipped table, 16/17 and 7/17 probes, plus
  global positional coupling 520/2308), TRIAL MODE (refuted by building it), the
  two-port split with `head_len`, and a uniform three-outcome protocol (would
  have resurrected the over-promise FIX-2 removed).
  **AMENDED 2026-08-11 by D33 — READ D33 AFTER D32, it changes what gets built.**
  A row names TWO functions, one per POSITION: a class port returning a set and
  an AST port returning a node, where the AST port of every class-shaped row is
  ONE shared generic wrapper and the ten character-type escapes' class port is
  DATA rather than a function. The claim is RETURNED, not raised — which is the
  load-bearing change and the thing to attack, since 23 `ctx_fail` sites in
  `ext.c` must yield a representable diagnostic instead of a longjmp.
  `pcrec_ext_class_pair_opens` is DELETED, along with `RF_CLASS_BASE`,
  `RF_CLASS_INVALID`, `parse.c:152`'s `\b` case, the `in_class` parameter and
  `registry_check.c:875`'s skip. Arbitration stays POSITION-INDEPENDENT — pick
  the row exactly as today, THEN consult its port; a NULL port is a refusal, not
  a reason to pick another row.
  **Still owed and NOT resolved by D32 or D33:** the reachability differential's
  fourth residue category; the whole-pattern capture count for `\1..\9`
  ([MOD-STATE] — and note it decides VALIDITY only, so it is NOT on this step's
  path; the RUNNING count is the one this step needs); module swap between two
  rows and row deletion, still guarded only by `tests/reject/`'s manifest.
  D33 subsumes the returning-doorway contract (one epilogue, so the two missing
  ones cannot be missing) and K12)
  **AMENDED AGAIN 2026-08-11 (fourth session) by D34 + extension_design.md
  PART II — READ THOSE AFTER D33.** R13 refuted D33 §4's position-independent
  arbitration (its own revisit-when trigger: `\12` selects differently by
  position) and parts of the design document; Frank ruled on the open
  questions (D34) and Part II (§11-§17) is the redesign of record: recognisers
  always live / producers gate, per-port recognition with one rank, explicit
  literal-fallback class ports (the K13 fix), `\Q`/`\E`/`(?#)` as port-less
  LEXICAL rows, the `want`×`may` ask contract, and the measured endpoint rule
  (one deviating cell; the static SHAPE column is dropped). [MOD-STATE]'s
  pre-scan is subsumed by §12.2's lexer-in-count-mode, which is on the always-
  live side. R14 ran the same session and partly refuted Part II — most
  materially for this step: "backrefs can land alone" is WITHDRAWN (the
  always-live layer is a group-header sub-parser plus verb/callout body
  extents — §18.1 is Frank's migration-order decision), the endpoint rule
  has TWO deviating cells and a five-step order, `pair_opens` SURVIVES, and
  the digit rule gained the 8/9 clause. Corrections inline marked R14;
  checks to be rebuilt by a D27 author per the rebuilt §17.3. A1 landed the
  same session (ten `unknown escape` pins, `tests/reject/` 235→245).

  **THE PLAN, 2026-08-11 (fifth session), after Frank resolved all five §18
  decisions** (no scanner — deferred backref resolution; leftmost-refusal
  policy, `may` collapsed; `quantifiable` three-valued with two form-resolved
  spans, `captures` dead; K13 fix lands first; bound-mode document deferred).
  The substeps [MOD-0.1..0.8] below PREDATE D33/Part II/R14 — **read each
  THROUGH the §18-resolved design; where a substep's text conflicts with
  `extension_design.md` as corrected, the design wins.** The known conflicts,
  so nobody re-derives them: MOD-0.1's D33 amendment says
  `pcrec_ext_class_pair_opens` is DELETED — R14 reversed that, it SURVIVES as
  the (bracket, high) deviating cell's predicate; MOD-0.1's old check (c)
  ("promise a module wherever libpcre2 dispatches") was refuted at R11 and
  its successor is the §17.3 list, owned by SPEC-MOD0 below; any older digit
  handling yields to §18.1's measured model (running-count disambiguation +
  pending-references end-of-parse validity — `[MOD-STATE]` is RETIRED,
  subsumed by that infrastructure); and D33 §4's position-independent
  arbitration is dead — recognition is PER-PORT (Part II §14).
  MOD-0.1 ADDITIONALLY OWNS, per the resolved design: the `ROADMAP_*`
  disposition column (per-row AND per-VerbName — the K14 diagnostic fix),
  the three-valued `quantifiable` column with its two form-resolved spans
  (option-run by form, verbs by name — design §18.3), the class-position
  expectation column (44 rows), the LEXICAL row kind ({`\Q`,`\E`,`(?#`}),
  three `want` levels + the cursor rule with NO `may` axis (§18.2), the
  returned-claims epilogue (fixes K11), the endpoint rule (five-step order,
  TWO deviating cells — closes K12), and the deferred-backref infrastructure
  (running count in `Ctx` + pending-references list + end-of-parse check).
  Its landing bar: byte-identity across the corpus with the GUARDED
  exception list (K12 endpoint and K14 diagnostics land here, each with a
  failing-then-passing pin; §7.1's rows wait for DOC-BM; bare-`\E` waits for
  its module; K13 already landed at FIX-3), plus SPEC-MOD0 green, plus the
  full suite.
  Execution order: **FIX-3 → MOD-0.1 (SPEC-MOD0 alongside) → the shaping
  modules in their existing D30 §7 order (.3 classes, then .5 modifiers, .4
  verbs, .6 unicode-props) → .7/.8.** Modules `backrefs` and `conditionals`
  are POST-MOD-0 milestones, planned at MOD-0.8 close: backrefs exercises
  the deferred resolution and by §18.1 lands alone; conditionals' landing
  bar includes exact E127/E154 (§18.2's ruling).
  (The backrefs and atomic-groups design notes recorded here moved to the active plan's M4/M6 sections, 2026-08-13.)

- [FIX-3] STATE:completed 2026-08-11 — **K13: the twelve class-position
  fallbacks, in the CURRENT parser, before the mechanism** (Frank, design
  §18.4). Landed as designed: `esc_class_value` decodes the class position's
  real semantics — `\0`..`\7` octal (≤3 octal digits; >\377 is PCRE2 error
  151, wording AND offset reproduced), `\8` `\9` `\g` `\k` the literal
  characters (complete fallback set over all 62 `[\c]` probes); tails
  re-enter as members; endpoints ride along with NO extra code (the range
  logic already consumed decoded values). All twelve rows RF_CLASS_BASE —
  the `\b` shape — so ext.c is never entered at class position and
  registry_check's derived in-class expectation flipped with the flag.
  Measured FIRST: tests/probes/probe_fix3.c, 41 cells, predictor stated
  before the run, zero disagreements with libpcre2 10.46. Pins first:
  tests/base/class_escape_fallbacks.rxt, 127 cases, 122 watched failing
  pre-fix. TWO CORRECTIONS to this step's own text, recorded so nobody
  hunts for ghosts: (1) there were NO twelve class-position reject rows to
  delete — K13's rejection was ext.c's generic in-class template asserted
  by registry_check.c's derived sweep, which tests/reject/ never pinned by
  hand, so the "counts move" is +2 rejections (`[\400]`/`[\777]`, the new
  error-151 diagnostic's only home, offset-pinned) +1 accept-control
  (`[\377]`, the boundary) = 248/99/63, one new manifest entry; the ten
  ATOM-position digit rows and `\k`/`\g` stay rejected, correctly. (2) The
  step's "become the literal letters" compressed the digit half: `[\0..\7]`
  are OCTAL per design §14.3's partition ("the literals PCRE2 makes them"
  is exact only for g/k/8/9), and the octal cells are python-verifiable so
  they are ordinary corpus blocks; only the literal-fallback cells carry
  `# pcre2-only` (U7). Closes K13. First `src/` change of the module era.
  ONE CHECK CORRECTED on the way in: registry_check's RF_CLASS_BASE branch
  probed `[<syntax>]`, and the `\g` row's syntax `\g{-1}` wrapped in
  brackets is a class whose `{-1` is an out-of-order RANGE — libpcre2
  rejects it too (108, measured — the probe gained the cell), so the derived
  check was demanding a bug. It now probes `[\<sel>]`, which is the flag's
  actual claim; tail/endpoint behaviour stays pinned in the oracle-verified
  corpus, not in a derived check that cannot consult an oracle.

- [SPEC-MOD0] STATE:completed 2026-08-11 (authorship; the GATE lives in
  MOD-0.1's landing bar) — tests/spec_mod0/, ten checks: 4 green now
  (lexical, digits, endpoints, toggle-coverage), 6 AWAITING a named pcrec
  surface with exit 3 ≠ failure ≠ pass (isolation needs the enabled-set
  symbol; capture-count needs a group-count channel; class-position needs
  the `class_expect` column; cursor needs a recogniser probe channel; gate
  equivalence needs `--features`; quantifiable needs its column — each
  found BY NAME in the dump header, so landing the surface arms the check
  with no edit). Three findings against §17.3 as written, recorded in the
  design doc's §18 tail and tests/spec_mod0/CLAUDE.md. Five sabotages run
  for real. MOD-0.1 cannot close while any check is failed OR vacuously
  awaiting a surface MOD-0.1 itself owns. — **the §17.3 checks, written by an author
  DENIED the design document** (D27; ruled at design §10.12/§18). Handed:
  the ten §17.3 invariant statements, `tests/probes/` (the session's probe
  sources, committed for exactly this hand-off), and the
  predictor-fed-from-the-oracle method its CLAUDE.md states. Includes the
  external sweeps: endpoint (alphabet per §17.3.8), quantifiability
  (`a<syntax>*` × rows + option forms + verb names), class-position
  expectation (probe sets, per-bucket floors), digit-model grid,
  capture-count differential. Runs alongside MOD-0.1; MOD-0.1 cannot close
  without it.

- [MOD-0.2] STATE:completed 2026-08-11 (ninth session; four commits, 1cc6ed6 →
  c1e203d). The 18 tail-bearing rows (16 `GROUP_T` + 1 `REJECTED_T` +
  `registry.c`'s longhand `\N{U+`) migrated to recogniser + rank; `tail`
  RETIRED from the lookup engine — it survives only as
  `pcrec_recognise_tail_default`'s parameter. Landed through the resolved
  design (D32 §§2-4,7,9; Part II §14.4): rank tiers 0/25/70 on the field
  (the D30-era 40 tier deliberately not reproduced — values are meaningless
  except between clashing rows, D32 §3); `pcrec_registry_arbitrate` with sel
  as the checkable pre-test and a tie AT THE WINNING RANK as the defect, an
  internal error at the escape/group doorways, validated LIVE by an
  equal-rank sabotage (`\N{U+0041}` → clean exit 1 + 2 registry failures).
  LANDING BAR MET: ZERO differences over a 5,247-comparison differential vs
  the pre-change snapshot binary (4,330 patterns × compile/count-groups/
  probe-ask channels; instrument liveness proven first — an inverted-rank
  build showed 910), pure seam migration, no guarded exceptions. The D32
  §9.5 discipline followed exactly: the migration scaffold (261,193 probes,
  0 mismatches, 0 ambiguous) was deleted in the same commit as the retired
  engine; `check_tail_precedence` retired in its OWN edit with both
  successors committed and green first (`check_row_ranks`;
  `check_arbitration_liveness` — R11/M3's >1-answer counter, floors
  10/15/15/50 predicted from the generator then confirmed exactly, plus the
  esc-'N' triple-answer assertion). Counts re-read from runs: registry 165,
  reject 430, PC-3 143, mech 20/20 (no anchor drift — macro DEFINITIONS
  changed, call sites did not), full battery green, spec_mod0 9/0/1.
  **The `-\d+)` collapse did NOT land**, per the standing rule: ten digit
  rows stay ten rows until a reachability differential passes on
  `(a)(?-1` / `(a)(?-1x)` / `(a)(?-1:x)` (PCRE2 error 114 — malformed
  bodies pcrec answers correctly today; the collapse as written is a tier-2
  regression). That differential belongs to whoever proposes the collapse,
  not to this step's close.

- [MOD-0.3] STATE:completed 2026-08-12 (tenth session; commits 8273184 →
  R16 close) — **MOVED AHEAD of
  `modifiers` (D30 §7, was
  MOD-0.5)**, so the module that owns the class doorway exists before the module
  that can change its lexing — module `classes`, the richest INPUT case: a scan
  whose end is not known in advance, context the others do not need (class-open,
  content-start, negation), and the only doorway where DECLINE is the normal
  answer. ~~`RF_CLASS_DELIM` retires; `RF_CLASS_NAMED` and `RF_CLASS_INVALID`
  stay as DATA (D29's data/code line). Collapses `pcrec_ext_class_pair_opens`,
  which is a second copy of the scan K4 got wrong three times.~~ Also PC-4's
  forcing function.
  **EXPANDED ON START (tenth session), read through the resolved design**
  (Part II §§12-16 as R14-corrected; D33 as amended by D34 items 6/7 and R14;
  §18 all resolved). TWO CORRECTIONS to this entry's own pre-D33 text, struck
  above, so nobody re-derives them: (1) `pcrec_ext_class_pair_opens` is NOT
  collapsed — R14 correction (c) struck it from every deletion list, three
  critics independently; it survives as the (bracket, high) deviating cell's
  predicate and the deviating cell is implemented BY it. (2) `RF_CLASS_INVALID`
  does NOT stay as data — D33 §3 / D34 item 7 retire it WITH `RF_CLASS_BASE`:
  base scalars and literal fallbacks become explicit data-driven class ports,
  and a NULL class port regains its single meaning, permanently invalid at
  class position (mode-invariant, the R14-verified half of §14.3).
  SCOPE MEASUREMENTS (2026-08-12, probe_mod03 vs libpcre2 10.46, predictor
  stated before the run): `[[:^alpha:]]` COMPILES with census identical to
  `[^[:alpha:]]` (204 members, 0 diff bytes over all 256) — **negated names
  are in the named-class port's scope**; `[[:^foo:]]` and `[[:^<:]]` are err
  130, and pcrec's current answers at both are already correct (module promise
  / unknown-name), so no pre-existing defect there; `[[:<:]]`/`[[:>:]]`
  COMPILE as zero-width word-boundary assertions (`[[:<:]]ab` matches "ab" at
  [0,2), `a[[:<:]]b` does not match "ab") — **not producible without assertion
  engine work (M6), so they stay refused and need an attribution ruling**;
  `(?[[a]])` COMPILES in 10.46 — extended classes are REAL syntax, out of this
  step's producing scope, same ruling needed. Substeps:

- [MOD-0.3a] STATE:completed 2026-08-12 — the DESIGN GATE, short and journal-recorded
  (rulings in the tenth-session journal entry: per-name POSIX attribution with
  `<`/`>` → module 'assertions', `(?[` → new module 'extended-classes'; two
  trailing tagged port fields {NONE,SCALAR,SET,FN} on RegRow; bitmaps
  generated from libpcre2 censuses, PC-4 re-measures; per-block `features`
  directive in .rxt; esc_class_value stays through slices 1-2, FN-port
  callee in slice 3)
  (the D6 panel stays at close; R10's lesson is design review is cheapest
  before code, but this design already carries R13/R14 — what remains is
  milestone-local): (1) what a REAL construct answers while module `classes`
  is ENABLED and its producer is deliberately absent — the `[[:<:]]`,
  `[[:>:]]` and `(?[` cells; candidates are re-attribution to honest module
  names vs keeping 'classes' with the enabled-module-still-refuses wording;
  tier-2 attribution under D26, pinned by hand in tests/reject/ either way,
  and the gate's `answered_at` already distinguishes "gate open, port
  missing". (2) The port representation on RegRow: tagged data-or-function
  class/atom port columns, trailing fields, every macro initialises them —
  MOD-0.2's measured lesson that -Wextra missing-field-initializers IS the
  enforcement, and the macro-DEFINITION edit shape that kept mech anchors
  from drifting. (3) The corpus channel: how tests/classes/*.rxt requests
  `--features classes` from the harness (a per-file directive, not a global
  env — the default-config corpus must keep running unmodified). (4) The
  port-ification scope: classes-owned rows plus the D33 §3 retirements;
  `esc_class_value`'s bare int becomes a tagged claim (the K11 UB shape,
  named in D33 §8)

- [MOD-0.3b] STATE:completed 2026-08-12 — slice 1, vocabulary + port columns,
  UNWIRED. As specified below, plus what execution added: the doorway
  vocabulary block MOVED above RegRow in internal.h (ports embed it — the
  dependency inverted); RegRow gained a struct tag; ESC_CLASS_BASE gained a
  literal-scalar parameter (its three callers are exactly the fixed-byte
  rows) and ESC_DIGIT_LIT split from ESC_DIGIT for \8/\9 (no octal
  continuation exists — 8 and 9 are not octal digits, the FIX-3 [\81]
  cell); pcrec_ext_finish walls unconsumed producing outcomes.
  check_class_ports landed with populations PREDICTED first (5/0/0/0,
  confirmed), values oracle-tied (bare rows to the libpcre2-fed
  class_expect column; body rows to §14.3's fallback law),
  sabotage-validated in three directions (value drift, zeroed scalar,
  deleted call → count 167 + manifest). Byte-identity differential vs the
  post-attribution snapshot: 243 corpus patterns, verdicts + diagnostics +
  emitted C, ZERO differences; instrument liveness proven against the
  pre-MOD-0.3 snapshot (attribution diagnostics differ). Spec: `ExtWhat` gains EXT_SCALAR / EXT_MEMBERS / EXT_NODE (D33 §5's
  vocabulary); the class-port column lands with data ports (`\b` → scalar
  0x08; `\g \k \8 \9` → their letters; NULL = permanently invalid);
  parse.c's call-site walls extend to the new outcomes; **every EXT_*
  outcome gets a probe that is false today** (D33 §9.3 — ask of each: was
  this already true yesterday?). Landing bar: byte-identity, nothing
  consumes a port yet; full battery between this and every later slice

- [MOD-0.3c] STATE:completed 2026-08-12 — slice 2, the PRODUCERS, gated.
  As specified below, plus what execution added: bitmaps GENERATED from
  libpcre2 censuses (probe_cls_bits.c, predictor confirmed exactly on all
  20 tables; the complement law probe-asserted, so only positive tables
  exist to drift — negation is a PORT flag); the caseless×posix cells
  MEASURED before pinning (probe_ci_posix.c, 8/8 fold-before-negate);
  `pcrec_ast_class_from_bits` as the ONE set-node constructor (the OS-1
  fold-order rule owned in one place); the endpoint rule's step 4 now keys
  on ANY surviving claim so a produced SET at an endpoint is err-150's
  analogue in both gate states; check_class_ports extended (populations
  5/10/1/11 predicted and confirmed; SET censuses tied to class_expect;
  negate-flag sabotage fires); the `features` corpus directive landed with
  a validated spec (a typo'd module list can never satisfy a perr block);
  tests/classes/classes.rxt 43 cases green, watched FAILING first against
  the slice-1 binary (37 fail / 31 distinct compile-fails — the D33 §9.3
  record, in the corpus header); S15-S17 sabotage anchors re-derived in
  the same change. AND THE FIRST spec_mod0 EXIT-0 IN PROJECT HISTORY:
  check07's population arrived (12 eligible rows, 24 pairs) and its
  strict-equality sweep reported the gate DOING ITS JOB as 24
  disagreements — replaced by the TRANSITION RULE its own CLAIM paragraph
  had stated all along (dated correction in the file header; dead-gate
  direction sabotage-verified — an ext_gate that never demotes fails 24
  clauses by name; gate.eligible_rows/baseline floors ratcheted;
  gate.compared_pairs stays floor-0 deliberately, check09's all-modules
  assertion being MOD-0.8 work). Spec: the ten
  char-type escapes (atom position → A_CLASS node; class position → members
  ORed into the class; **every A_CLASS-building site calls `cls_casefold`
  itself** — the OS-1/D23 rule, stated in src/parse/CLAUDE.md); bare `\N`'s
  atom port (`[^\n]`, set 255; its class port stays NULL, err-171 wording is
  tier 3); the POSIX named-class port at the bracket doorway, 16 names × 2
  polarities (the `^` form measured real above). Default (empty enabled set)
  stays byte-identical; under `--features classes` the constructs compile
  and MATCH. tests/classes/*.rxt lands here, oracle-verified (python3 re
  where expressible, `# pcre2-only` otherwise)

- [MOD-0.3d] STATE:completed 2026-08-12 — slice 3, retirements, WITH THREE
  MEASURED DEVIATIONS from this step's own spec, each recorded in the
  journal: (1) **RF_CLASS_INVALID STAYS** — D33 §3's precondition ("NULL
  class port regains its one meaning") is measurably FALSE while the
  lexical rows carry class_expect "err 106" for probe-shape reasons ([\Q]
  quotes the ]) and unicode-props' rows await MOD-0.6 ports; a NULL cport
  today means "invalid OR not yet produced", and deriving permanently-
  invalid from the measured column would have changed [\Q] to the wrong
  message. Retirement re-scheduled to MOD-0.6's port population. (2)
  **RF_CLASS_DELIM STAYS AS DATA** — the recogniser conversion buys
  nothing observable (all three rows carry it; the scan is always-live in
  scans.c; pair_opens survived R14 as the deviating-cell predicate) and
  would churn the R9-hardened dispatch of a doorway that has produced
  three shipped bugs. The flag IS the construct's recognition rule as
  data, D29's line. (3) The **in-class tail sweep extension defers WITH
  RF_CLASS_INVALID** (D33 §9.2 conditioned it on the removal; K10's net
  stays MOD-0.6's). WHAT LANDED: RF_CLASS_BASE retired into BASE ports
  (ExtPort.base — the gate never touches PCRE2 base facts): \b/\8/\9/
  \g/\k scalar data, \0..\7 the octal PORT_FN (pcrec_clsport_octal in
  parse.c — base grammar's rule migrated to the seam, err-151 message and
  offset byte-identical); parse.c's FIX-3 block and \b special case
  DELETED; esc_class_value consumes EXT_SCALAR and moves the cursor to
  claim.end; registry_check re-keyed both readers on the port
  (check_table_to_parser's compiles-branch; sweep gained excuse_base_cport,
  scoped to the in-class sweep only) and check_class_ports moved to
  5/10/9/11 predicted-then-confirmed. Byte-identity BOTH gate states: 243
  patterns × verdict/diagnostic/emitted C vs the slice-2 build, ZERO
  differences; the 127 FIX-3 pins and 43 classes cases green through the
  migrated path. ORIGINAL SPEC:
  the five-step evaluation order (§16.2 as R14-corrected: low's own error →
  high's pair-open short-circuit → high's own error → either side SET → 150
  → scalar ordering) live at both class-reachable doorways with real SET
  results — K12's certification scope grows from refusals to produced sets;
  `RF_CLASS_DELIM` retires into recognisers; `RF_CLASS_BASE` /
  `RF_CLASS_INVALID` retire (parse.c:152's `\b` special case deleted;
  registry_check.c:875's skip_flag goes). **D33 §9's migration obligations
  come due in this slice**: SPEC-FA's accept-controls shown passing through
  the new path (`[0-[a]` `[0-[:]` `[0-[:digit]` `[0-[.]` —
  run_reject_tests.sh:1019's warning), and the in-class sweep extended past
  one byte of tail context, because removing `RF_CLASS_INVALID` without it
  leaves K10's gap in a new place (K10's FIX stays MOD-0.6's; the NET comes
  due here)

- [MOD-0.3e] STATE:completed 2026-08-12 — slice 4, PC-4 + the ratchets
  (see [PC-4] above for the instrument's own record; check07's floors
  ratcheted at .3c when its population arrived; check02's compared floor
  is UNCHANGED by measurement — its bodies run without --features, so
  nothing new compiles there until a module is default-on, which is
  MOD-0.8-scope policy). Spec: PC-4 (the
  R8/C4-2 SEMANTIC differential — compile AND MATCH vs libpcre2 over a
  generated class-pattern space, inside make test, skipping loudly without
  libpcre2 exactly as PC-3 does) lands WITH the module per its own step
  text; check07's `gate.compared_pairs` floored above 0
  (AWAITING-POPULATION retires — spec_mod0's first possible exit-0 run);
  check02's compared floor moves if any generator body now compiles;
  check09's assertion 2 arms. Counts re-read from runs, never docs

- [MOD-0.3f] STATE:completed 2026-08-12 — close: R16 panel (three lenses,
  all delivered — docs/dev/reviews/2026-08-12-r16-mod03.md; both behavioural
  findings FIXED same-session: the lower/upper caseless blindness with ten
  discriminating pins, and the \N{quantifier} fallback with the table's
  first custom recogniser + the shared brace-shape scan) + the landing bar
  (default-config differential vs b6adda5: ZERO beyond the three pinned
  attribution diagnostics; PC-4 62,872 cells zero divergences; spec_mod0
  10/0/0; battery green at every commit). Spec: (read-only,
  narrow briefs, one primary question each — the R12 standard; any BLINDED
  author spawns through scripts/mk_d27_cell.sh, the CELL) + the landing
  bar: (a) default-config differential vs the pre-MOD-0.3 snapshot binary,
  ZERO differences, instrument liveness proven first (the mod02_diff.py
  method, rebuilt from the journal — scratchpad is ephemeral); (b) under
  `--features classes`: PC-4 zero divergences + corpus green; (c) full
  battery + strict; (d) journal, wake brief, per-dir CLAUDE.mds

- [MOD-0.4] STATE:completed 2026-08-12 (twelfth session, opened and closed in
  one session: gate 9aa720a -> close after R18; one impl worktree lane
  through four slices + a three-critic close panel; every merge
  battery-green) — module `verbs`, the MIGRATION TEST: existing,
  measured code rather than greenfield. Four answers drawn from its own tables,
  the VF_* form bits, the at-start position rule, and a blame offset that is not
  the doorway's default (`(*)` blames the `*`). If the signature survives this
  it survives

- [MOD-0.4a] STATE:completed 2026-08-12 — scope + design note. Design note
  delivered and approved with four rulings; the seam ruling recorded on
  MOD-0.4b. Scope rulings were: Scope rulings
  (main session): PURE MIGRATION, no verb produces — the parse.c doorway-3
  wall stays; NO new probe harness (PC-3's check_verb_names IS the live
  measurement record, re-taken every make test — a frozen probe_verb.c
  would be a second copy of a measurement that already re-runs; decision
  recorded here rather than silently). Design note (impl lane, reviewed by
  main before code): how pcrec_ext_verb's four table-drawn answers, the
  VF_* form computation, VF_ATSTART (at == 0), and the star = at+1 blame
  offset map onto the mod_modifiers.c seam (recognise pointer / pointer
  identity / port field), preserving the accessor signatures PC-3 and
  --list-verbs consume

- [MOD-0.4b] STATE:completed 2026-08-12 (worktree lane impl-mod04, commit
  043d78a, merged 72f4fcf). Execution detail beyond the spec: the SEAM IS A
  DIRECT CALL, not a port — doorway 3 has ONE RegRow and dispatches by NAME
  through its own tables, so there is no row family for a recognise pointer
  to mark, and an aport now would wire a producer nothing exercises (the
  NULL-port discipline); the milestone's signature question answered YES and
  DOCUMENTED in mod_verbs.c's header (four table answers via the shared
  REFUSE epilogue, VF_* computation, at==0, star=at+1 — no new vocabulary
  needed); ext_gate promoted to pcrec_ext_gate + REFUSE/BAD_ROW to
  internal.h, ONE definition each (DECLINE stayed local to ext.c);
  check01_isolation re-verified post-move (mod_verbs.o does not link the
  enabled-set symbol); extent scan stayed in scans.c (never-links contract);
  differential corpus derived programmatically from baseline --list-verbs —
  resolved name count 50 (31 upper + 19 lower), 602 comparisons across both
  gate states + dumps + --probe-ask, ZERO diffs vs f88ff2e. Spec was:
  pcrec_ext_verb + verb_upper/verb_lower + accessors ->
  src/parse/mod_verbs.c with their measured-grammar comments
  (probes-and-code-together, R8/C2-9's counter-example); RK_VERB row stays
  ONE row in registry.c (D29's shape question answered the same way: the
  per-name machinery already lives on VerbName, K14's ruling); existing
  check surfaces (registry_check, PC-3, reject pins, --list-verbs,
  --probe-ask) move/pass IN THE SAME CHANGE; byte-identity differential vs
  the pre-move build over the verb surface, zero diffs

- [MOD-0.4c] STATE:completed 2026-08-12 (impl-mod04 lane, commit 94b0693 +
  841d73f landing bar, merged 8f94ccd) — S27 (blame-offset regression), S28
  (table case swap, 52 reject failures), S29 (at-start drop, the a(*CR)
  pin; cross-referenced to the PC-3 sabotage table's identical edit).
  FINDING: S27 came back UNDETECTED 0/437 — the (*) reject pin was
  message-only, and the blame-offset regression produces the SAME message;
  closed by pinning "(pattern offset 1)" per the brace family's R7
  convention, both directions measured (0/437 without, 1/436 with). The
  milestone's own marquee hazard was the one unguarded. NOTED, framework
  limit: mech's SAB_SUITES has no `registry` suite, so PC-3/sweep_verb
  coverage cannot be mech-claimed; wiring one is a framework change for a
  future owner, recorded here rather than forced

- [MOD-0.4d] STATE:completed 2026-08-12 — close. R18 panel
  (docs/dev/reviews/2026-08-12-r18-mod04.md): three critics, second consecutive
  clean panel, ZERO tier-1 divergences (the engine critic independently
  re-verified the move's byte-identity, so all behavioural findings are
  pre-existing). Checks -> the S27 finding GENERALIZED: six REFUSE families
  were message-only-pinned; closed on the mod04d-offsets lane (bd9b6a1,
  merged 19020ee) with ten measured offset pins + S30
  (failing-direction: 0/437 pre-pin — S27's exact baseline — then 2/435).
  Engine -> the offset-divergence inventory recorded tier-2 no-action
  (~35 cells; the star=at+1 and (*:) cells MATCH the oracle, now measured
  claims); K15 opened (too-long category divergence on >128-byte
  non-identifier runs, a LINKED PAIR with PC-3's identifier-only length
  generator — docs/dev/known_issues.md). Docs -> three live-doc staleness
  fixes incl. extension_design §5.3's location claim that had aged through
  TWO moves. NOTED inventory in the review file: check07 gate coverage at
  doorway 3 waits for the first producer; check01's aperture excludes
  mod_verbs.o both directions, no isolation floors (MOD-0.8 candidates);
  mech has no registry suite. Close battery green: mech 30/30, reject
  268/99/65/437-checks, registry_check 167, PC-3 143

- [MOD-0.5] STATE:completed 2026-08-12 (eleventh session, opened and closed
  in one session: gate a7b835c -> close after R17; three parallel subagent
  lanes + the main session; every slice battery-green at its landing) —
  module `modifiers`.
  **MOVED AFTER `classes` (D30 §7, was MOD-0.3).**
  R10/C2-11 measured the hazard at options = 0: `[a- ]` is error 108 (range out
  of order) and `(?xx)[a- ]` COMPILES, because `xx` deletes the space — at the
  class RANGE ENDPOINT that `3fca0d8` (SPEC-FA) fixed as a silent wrong matcher
  one commit before the panel. **pcrec is safe today only because `(?x)` is
  rejected outright as "requires module 'modifiers'" — the guard IS the
  unimplemented-ness, and this step removes it.** So the module that OWNS the
  class doorway is built first. The original order put `modifiers` first as the
  cheap module that would shape the interface; the interface is being redesigned
  anyway, so that reason is spent. **Landing this step must include telling
  `classes` about `x`/`xx`** — module `modifiers`. Move
  `pcrec_registry_option_run_ok` out of registry.c into its module file WITH the
  measurements that establish its grammar (D28's carried warning; R8/C2-9's
  drifted `LIMIT_*` rule is the counter-example). `RF_OPTION_RUN` retires — the
  recogniser pointer says the same thing and names which parser. The 12
  option-setting rows STAY as 12 rows sharing one recogniser; see D29 on why a
  byte-set row was rejected

- [MOD-0.5a] STATE:completed 2026-08-12 — the DESIGN GATE, short and
  journal-recorded (evidence: tests/probes/probe_mod05.c + probe_mod05b.c,
  predictions stated first, run against libpcre2 10.46). Rulings:
  (1) PER-LETTER SEMANTIC SCOPE with `--features modifiers` ON — implemented
  as scoped parse state (Ctx grows a modifier struct around the existing
  `caseless` slot, the D31-note's "expect a struct, not more bools"):
  `i`/`-i` (state exists, PARSE-1's 17/17), `s` (dot's set: 255 -> 256,
  parse-time class construction), `U` (greed swap at quantifier
  construction), `n` (capturing-`(` hook consults state; feeds
  --count-groups/check02), `^` (reset to hardwired defaults), `x`/`xx`
  (slice .5d, the lexer), and `r`/`aD aP aS aT aW` as MEASURED NO-OPS at
  options=0 C locale (0 diff cells over full censuses; they become real
  under UTF/UCP — pointer recorded for MOD-0.6/M5, DD-12's owners).
  (2) PER-LETTER REFUSALS, honest names (the MOD-0.3a per-name precedent):
  `m` -> module 'assertions' (multiline ^/$ is assertion-engine work, DD-11's
  $-EOL sibling); `J` -> module 'named-groups' (J is observable only through
  named groups, which are that module). Tier-2 attribution judgements,
  recorded not asked, reversible one-row edits — FLAGGED TO FRANK.
  (3) THE MEASURED (?^) RULE: resets i,m,n,s,x,xx to the hardwired defaults
  and does NOT touch U or J (both probed surviving); the reset is
  to-constant, not to-compile-option (the PARSE-1 landmine, now load-bearing).
  (4) THE MEASURED X-MODE SETS: skip set OUTSIDE classes is
  {09,0A,0B,0C,0D,20,85} — NOT \s's set (0x85 NEL is skipped; census run
  with a no-x control column after the naive template's quantifier false
  positives, probe_mod05b); `#`-comments run to newline; xx additionally
  DELETES {09,20} inside class interiors AHEAD of the endpoint rule; single
  `x` never touches class interiors ((?x)[a b] keeps the space member).
  (5) NON-FINDING, verified both sides: spaced brace quantifiers (`a{1, 2}`
  etc) are QUANTIFIERS at options=0 (10.43+ rule) and
  pcrec_brace_quant_shape already accepts space/tab (R16) — pcrec's emitted
  matcher agrees with libpcre2 on the discriminating subjects.
  (6) Malformed runs with the gate ON are the module's to diagnose
  (D28's SYN_MALFORMED half: `(?i-m-s)` err-194 shape, offset at the
  offending byte); gate OFF keeps today's answers byte-identical.

- [MOD-0.5b] STATE:completed 2026-08-12 (eleventh session; worktree worker
  impl-mod05b authored, main session landed after the worker went idle
  uncommitted; commit 105aecf, merged 1c8883b) — slice 1, the GRAMMAR MOVE,
  byte-identity. As specified below, plus what execution decided: the rows'
  recogniser is a MARKER (always answers, exactly the tail-less default) and
  ext.c keys the whole-run check off POINTER IDENTITY — because the run's
  grammar starts AT the selector byte, and reconstructing `at - 1` inside
  the shared recogniser would be UB against registry_check's synthetic
  probe buffers (rationale in the function's own comment); the retired bit
  stays unassigned so dumps cannot alias. Byte-identity measured: 641
  patterns + list surfaces + 69 --probe-ask combos, zero diffs vs a7b835c.
  Moved code diffed VERBATIM against the original. registry_check QF_FORM
  family test and the tests/registry/CLAUDE.md sabotage table moved with
  the surface. Spec was:
  mod_modifiers.c TU carries pcrec_registry_option_run_ok WITH its measured
  grammar block (probes-and-code-together; R8/C2-9 is the counter-example);
  RF_OPTION_RUN retires — the 12 GROUP_OPT rows point at the recogniser
  (MOD-0.2 machinery; rows stay 12); ext.c's RF_OPTION_RUN branch reads the
  pointer instead of the flag. Landing bar: byte-identity differential over
  the corpus + reject surface, full battery.

- [MOD-0.5c] STATE:completed 2026-08-12 (eleventh session; landed in ONE
  MERGE with .5d and the corpus — sequencing ruling: with the gate ON there
  is no honest refusal wording for `(?x...)` before the lexer exists, so
  the slices were authored separately and landed atomically). Execution
  detail beyond the spec below: Ctx's `bool caseless` widened to the
  ModState struct; THE SCOPE MECHANISM IS PLACEMENT — the group
  save/restore moved from p_group to p_group_body's body-parsing tail, so
  a bare `(?i)`'s doorway splice ESCAPES its own paren pair's restore by
  construction (the measured leak-to-enclosing-`)` rule with no flag and
  no module knowledge in the base grammar); one port function is the shared
  handler for both spellings, diverging only at the terminator; THREE new
  probe rounds (probe_mod05c cells, committed): unset-WINS regardless of
  run order ((?i-i)/(?-ii) both case-sensitive), doubled-x is
  ADJACENCY-sensitive ((?xsx) is level 1) and a later bare (?x) DOWNGRADES
  an earlier xx — the (?xx)(?s) control keeps it; four reject_gated pins
  (m->'assertions', J->'named-groups', err-194 and err-114 shapes) — a NEW
  fourth pin class with its own ratchet counter, because .rxt perr cannot
  assert WHY (corpus author's finding); floors moved with the surface
  (modsyn 105/8, modsem 35/3; zero real disagreements at 140 compared
  cells); corpus merged and green 59/59 after ONE landing correction (the
  \t-escape block had transcribed the raw-tab measurement onto the escape
  form — libpcre2 measured: the escape SURVIVES deletion; pcrec agreed
  before the fix, both forms now pinned). Spec was:
  Ctx modifier state (seeded from opt, saved/restored where `caseless`
  already is); `(?...)`-terminated runs apply to the enclosing scope;
  `(?...:body)` = set state, pcrec_parse_body, restore (the callback PARSE-1
  built); letters per .5a ruling 1-3 incl. per-letter refusals and
  malformed-run diagnostics; corpus tests/modifiers/ (features directive;
  python-re oracle where it agrees — mid-pattern `(?i)` is a py3.11+ error,
  those blocks go pcre2-only); reject pins move by measurement.

- [MOD-0.5d] STATE:completed 2026-08-12 (eleventh session; same landing as
  .5c). Execution detail: probe_mod05d measured the boundary FIRST —
  quantifiers and lazy markers bind across skips ((?x)a + and (?x)a + ?),
  `#`-comments end at 0x0A ONLY (0x0D and even the skipped 0x85 do NOT —
  the terminator is the NEWLINE convention, not the skip set: DD-11 made
  load-bearing), the `(?` option run is lexically tight ((?x)( ?i) is the
  109 shape), a NEWLINE inside a brace quantifier defeats quantifier-hood
  even under x (the brace shape's space/tab rule is its own, raw scan),
  xx deletion precedes the NEGATION check ([ ^a] negates) and RANGE
  parsing ([a\t-\tz] is a-z) and the dash-vs-literal lookahead must see
  THROUGH deletion ([a- ] is {a,-}) — implemented as three parse.c helpers
  (xskip at p_cat entry + p_rep's quantifier and lazy peeks; cls_skip at
  class open/member/range points; cls_peek_past_dash) with every rule
  probe-cited. The D30 §7 hazard compiles correctly under the gate and is
  corpus-pinned in both gate states. Spec was: Skip set + comments outside classes; xx's {09,20} deletion in
  class interiors ahead of the endpoint rule (the D30 §7 hazard cells
  `(?xx)[a- ]` / `(?xx)[a-\ ]` / `(?xx)[\ -a]` in the corpus, both gate
  states); interaction cells with quantifier braces and `\Q`/`\E`/escaped
  whitespace measured in the slice.

- [MOD-0.5e] STATE:completed 2026-08-12 (eleventh session; worktree worker
  mod05e, commit 4f0a964, merged c15374c). Execution: check07/check09 and
  registry_check moved WITH the .5c/.5d landing itself (aports 11->23,
  floors modsyn/modsem, the transition all measured there); this slice
  added the three NEW mech rows — S21 (cls_peek_past_dash raw peek; caught
  by xxmode.rxt 3/11), S22 ((?^) clearing ungreedy; caught by reset.rxt),
  S23 (comment terminator widened to any skip byte; caught by xmode.rxt —
  the surface suspected UNGUARDED was already guarded, by a space inside an
  existing comment block's text, since a space IS a skip-set byte; no
  raw-newline cell needed) — mech 23/23; and resolved the R16 fuzz-note
  item: fuzz.py's own note was ALREADY correct (RESOLVED addendum from
  99eff9e) — the stale copy was tests/fuzz/README.md's summary, now fixed
  and cross-referenced to U2. PC-4 still has no modifier shapes (R16 NOTED
  stands; belongs to whoever next extends PC-4). Spec was:
  check07 gate-equivalence and check09 per-feature toggle meet their first
  modifier population (grep the suites for "nothing produces yet" premises —
  the tenth session's lesson); registry_check ties for the recogniser
  pointer; PC-3/PC-4 implications measured; mech rows for the lexer;
  fuzz.py's stale a{,3} note fixed at this, its next edit (R16 NOTED).

- [MOD-0.5f] STATE:completed 2026-08-12 (eleventh session) — close. The D27
  blinded spec-writer ran EARLY (parallel with .5b, Frank's directive —
  check11/check12 merged 91e6b23, allowlist narrowed to exclude
  tests/probes so the milestone's measured alphabet could not leak; its
  floors were designed transition tripwires that fired at the .5c landing
  exactly as intended). R17 panel (docs/dev/reviews/2026-08-12-r17-mod05.md):
  three critics, ZERO wrong cells (a panel first); checks -> three
  correct-today-unguarded port corners, all pinned + S24-26 with the
  failing direction measured against the unpinned HEAD; engine -> bare
  `(?`-at-EOF fixed into the bare-`(` 114 family (the Q2 pin's
  PCRE2-agreement prose was measured FALSE — its third answer in three
  eras); docs -> five stale-voice fixes incl. tests/modifiers/CLAUDE.md's
  pre-landing §9.3 framing (the R16 failure mode, one module later). The
  option-run grammar got its first adversarial readers (MOD-0.8's note
  discharged early). Journal + wake at close.

- [MOD-0.6] STATE:completed (2026-08-12, thirteenth session; opened and
  closed same session on Frank's go. CLOSURE: phase-1 probe
  (tests/probes/probe_uprops.c, archived per D35) + accepted design note
  (docs/design/design_notes_mod06.md, §8 holds the landing amendments) + five
  slices merged at e2b1d4a — K10 FIXED with check_class_syntax_reach and
  seven pins; mod_uprops.c streaming scanner (48-cap in limits.h, caret
  excluded, fold-free brace-path lookup) with the 146/147-shaped refusal
  split and load-bearing offsets; 35 offset pins total; PC-3 uprops
  differential 1,976 probes + 52-letter table drift guard; mech S31-S35
  with the S33/S34 first-landing UNDETECTED finding closed measured. R19
  panel (docs/dev/reviews/2026-08-12-r19-mod06.md): zero tier-1; K16 opened
  (164/256 malformed body bytes, tier 2, Frank ruled DEFER to first
  producer) + the last two message-only pins offset-pinned + has_eq/digit
  pins; reject 303/99/65/4, registry 168, PC-3 154, mech 35/35. LANDING
  NOTES against this row's own predictions: the "expect a live tier-2
  finding" over-promise did NOT materialize — \p/\P have no decline-shaped
  tail (256-byte sweep), so the catch-all recognise is permanently correct;
  the registry.c:257 citation was stale (the row moved with file growth —
  cite rows by content, not line). Rulings the session recorded: K15
  acceptable tier-2 (exclusion + hostile-alphabet row + compliance entry
  landed as their own lane); D33 §7 WIDENING defers to the first wide
  producer, amendment under D33 §7; this step stayed recogniser-only —
  \p SET-certification and the K12 body-dependent boundary deliberately
  survive to the producer milestone, design note §8.2) — module
  `unicode-props`, the only NEW recogniser:
  `\p{...}` vs `\pL` (two shapes at one byte), `\P` polarity from `sel`,
  normalisation into a CALLER-PROVIDED FIXED BUFFER (never an arena — D29;
  `arena_alloc` aborts, which is K7), and the `\N{U+` half of MOD-0.1's
  acceptance test. **Expect a live tier-2 finding**: `\p` promises its module
  for every tail today, which is the Q2 shape at a fourth doorway. One question
  to MEASURE rather than infer — `\p{Foo}` is PCRE2 error **147** (R10 corrected;
  the plan said 47, which libpcre2 does not produce), which by D28's
  dispatch rule reads as CLAIM, while `[[:foo:]]` was decided as REFUSE in
  FIX-2. State the rule that covers both, with libpcre2 as the arbiter — and
  note R10/C2-2: under `PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL` `\p{Foo}` COMPILES,
  so all three answers are live for one construct and the option set must be
  bound first (R10 disposition 3). **The buffer is not "fixed" (R10/C3-2):** a
  valid `\p{...}` body of 100,006 bytes compiles, because PCRE2 normalises while
  STREAMING; the bound is 48 SIGNIFICANT characters. Normalise as you scan and
  stop at 49 — copy-then-normalise either overruns or silently truncates, and
  truncation turns `\p{____L}` from CLAIM into REFUSE, a tier-2 miscompile of
  the SPEC-classes-F1 shape. Put the 48 in `core/limits.h`.
  **THIS STEP ALSO OWNS K10** (D30 §8, Frank's call): `[\N{U+41}]` is refused as
  class-invalid where libpcre2 recognises it (error 193, every class position).
  The fix is removing `RF_CLASS_INVALID` from `registry.c:257`; the WORK is the
  test, because the in-class sweep's template supplies one byte of tail and
  `registry_check.c:875-876` exempts `RF_CLASS_INVALID` rows from that sweep
  anyway. **Close the in-class tail-sweep gap in the same step**, or the same
  four blind nets survive for the next reader

- [MOD-0.7] STATE:completed — `--explain` REWRITTEN as a live doorway call.
  ~~reads the port's output (what was recognised, the answer, the blame offset,
  the normalised name), with a tests/cli case~~ **R10 WITHDREW that
  justification (C4-1, C4-2)** and MOD-0.7a's design note refuted the
  replacement's own cure. What landed:
  - [MOD-0.7a] STATE:completed — the design note,
    `docs/design/design_notes_mod07.md` (+ §13, the manager's six rulings).
    **Headline, measured:** the declared-vs-live agreement the row above asked
    for CANNOT catch a module swap — ext.c renders the promise from the same
    `r->module` `--explain` prints, so C4-1's sabotage leaves the 100-row
    census bit-identical (93 SAME / 6 SILENT / 1 NOROUTE) and all eight of
    case10's `--explain` assertions green. Module-name truth stays in
    hand-written pins; the live call earns its place on ELECTION (13 rows
    share a rendered diagnostic with a bucket sibling) and PROMISE
    CONSISTENCY. Found by applying the design to its first row: `--explain
    '(?C1)'` promised module `callouts` where the compiler says no module ever
    will — K14 on the query surface, D26 tier 2, one row
  - [MOD-0.7b] STATE:completed — the build, in six slices: ONE doorway router
    shared with `--probe-ask` (1089 cells byte-identical); `ExtResult.row`,
    the elected row (876 compile cells byte-identical); the rewrite (selection
    = prefix ∪ bucket-candidates, each row tagged; the query's live answer as
    DATA and each row's canonical live answer as the ASSERTION; exit 3 for a
    dissent); cli case11, field-level, 63 assertions, with the K14 fix landed
    under the FIX-3 pattern (pin written first, recorded failing); V1-V7
    measured; docs. **The normalised name is DEFERRED to the first
    unicode-props producer** (manager ruling 2, superseding this row's
    original wording — K16's linked-pair logic: the buffer gains an accessor
    when it gains a consumer and the K16 fix, together). In-class routing and
    a mech `cli` suite arm are recorded MOD-0.8 candidates

- [MOD-0.8] STATE:completed — (2026-08-12/13 fourteenth session; closed at 569b48f, final battery green: corpus 1270, cli 221, reject 486, registry 168, PC-3 163, spec 14/14, mech 35/35 0-anomaly) checkpoint close. The D6 panel **must also cover
  Q2+SR-9**, whose panel was deliberately deferred into this step: brief it on
  the option-run grammar in `pcrec_registry_option_run_ok`, which no adversarial
  reader has seen, and the three PC-3 differentials Q2 added. Plus a D27
  spec-first writer, denied `src/` and `tests/`, briefed on `\p{...}` and `(?`
  option-run RECOGNITION from the goal documents and libpcre2 — MOD-0.6 is the
  only part of this step a blind writer can test, which is itself an argument
  for it being in scope
  - [MOD-0.8a] STATE:completed — the D6 close panel (R20), three lenses:
    (1) checks/tests on Q2+SR-9's option-run grammar
    (`pcrec_registry_option_run_ok`, which no adversarial reader has seen)
    plus the three PC-3 differentials Q2 added; (2) engine semantics on
    MOD-0.7's landed surfaces (shared router, ExtResult.row, the
    election/promise/attribution clauses, case11) against the oracle and the
    accepted design note; (3) docs staleness. Compiled to
    docs/dev/reviews/2026-08-12-r20-mod08.md with triage dispositions,
    fix-with-measurement before disposition
  - [MOD-0.8b] STATE:completed — the D27 blinded writer (cell `spec-mod08`,
    scripts/mk_d27_cell.sh): spec-first tests of \p/\P and `(?` option-run
    RECOGNITION from the construct's public promise and libpcre2, denied
    src/ and tests/ (default cell allowlist); cell diffed back into the
    worktree for review-then-merge
  - [MOD-0.8c] STATE:completed — (landed 2026-08-13, merge 569b48f) candidate dispositions RULED 2026-08-12
    (Frank items 1-2 explicit, manager slate unvetoed; execution lane
    mod08c): DEFAULT-ON = D37 (frozen named sets, std1={classes,modifiers};
    implementation is [STD1] below — check09 per-name arming and check01
    aperture/floors land WITH it, their meanings shift with the default);
    MECH SUITE TYPES registry+pc3+cli — BUILD, runtime cost measured before
    wiring (Frank: "this project's greatest benefit will be its testing
    suite — builds confidence and lets us go crazy when we get to
    optimizations"); PC-3 GATE AXIS — BUILD (OPTRUN-B3: no differential
    opens the gate; two modules now produce); DEFERRED-VALIDATION ORDERING
    — DOCUMENT in pcre2_compliance.md (category divergence, module-gate
    runs before run-validity, population can only shrink); `-e utf8`
    MODULE-NAMESPACE GAP — FIX small (K14 shape: names a module the
    namespace lacks); DEFERRED WITH OWNERS: PC-4 missing shapes → first
    wide producer (+ mod08fix's residual: PC-3 still cannot generate the
    zero-tail `(?P` cell), in-class routing → next router toucher,
    OPTRUN-B2 alphabet generation → with the mech pc3 arm; make ubsan →
    EXPANDED by Frank into [SAN-1] (full sanitizer + lint battery, both
    the compiler and the compilee axes), scheduled next session

- [SAN-1] STATE:completed 2026-08-13 (fifteenth session; subagent lane + manager landing after the lane died in the 02:50 box reboot with all code committed. Landed: make ubsan/asan/lint opt-in via BUILD_DIR-separated trees, BOTH axes; the GENCFLAGS compile-site AUDIT found five deaf sites (cli, pc4, registry, parse, trie_identity) and plumbed them — the compilee axis was silently partial before; LINTGEN=1 rides make test's compile pass with -fanalyzer, +53.7s/+13.8% measured quiet; four sabotage validations fired; F1 -Wclobbered triaged benign + volatile-hardened; quiet runtimes: ubsan 408.9s, asan 470.4s, lint 8.8s; placement DECIDED from numbers: ubsan+asan+lint join the merge/close battery, battery-grade make test adopts LINTGEN=1, smoke never; -O1 DSE-eats-unobserved-overflow recorded as a known flag-level limit) — THE SANITIZER + LINT BATTERY (Frank,
  2026-08-12, expanding the R7/T-3 ubsan carry; scheduled NEXT SESSION;
  lands BEFORE [OPT-A] opens — Frank: "we should expect some trouble when
  we start optimizing", so this is the tripwire built before the risk).
  BOTH AXES instrumented, because trouble lands in both: the COMPILER
  (build/pcrec, libpcrec.a, test drivers) and the COMPILEE (every generated
  matcher the harness compiles — the `GENCFLAGS` env hook already exists in
  tests/harness, so the compilee axis may be mostly plumbing; the emitted
  computed-goto code is exactly where OPT-A/B will take its risks). Pieces,
  each an opt-in target like `make strict` (writes nothing, D2 plain-make):
  `make ubsan` (-fsanitize=undefined over the suite — R20's tier-1
  longjmp-into-uninitialized-jmp_buf is this tool's home class, caught at
  first execution instead of by a lucky SIGSEGV); `make asan`
  (AddressSanitizer + LeakSanitizer — K7's abort-under-memory-limit is this
  class); `make lint` (static analysis: survey what the box offers —
  gcc -fanalyzer, cppcheck, clang-tidy if clang present — adopt what earns
  it, RECORD REJECTIONS with reasons per OPT-A's convention); valgrind
  memcheck noted as the no-rebuild alternative where ASan conflicts.
  TSan already lives in tests/thread — this row completes the family.
  Battery integration ruled AFTER runtime is measured, never asserted:
  which stages join wake §3's standing battery vs run checkpoint-only is
  a number-backed decision

- [TT-1] STATE:completed 2026-08-13 (fifteenth session; subagent lane, reviewed+merged by the manager. Landed: 9 section targets wrapping make test's own scripts — test: itself byte-untouched; make smoke = 6 fast sections, measured 31-32s x3, SMOKE_FLOOR=6 literal independent of the list, floor sabotage-validated loud; per-section runtimes 3x load-clean runs recorded in testing.md with the doubling re-record trigger; touched-path table; opt-in make hooks pre-push via git rev-parse --git-path hooks. First timing sweep discarded whole for R3.10 load contamination, re-swept with per-run before/after sampling) — TIERED TESTING (Frank, 2026-08-12: suite crept
  15min → 5min parallelized → growing again, and we only ever ADD tests;
  "spot check the relevant test sections while we work then hit the full
  load at evaluation"; CI DEFERRED, NOT REJECTED — Frank clarified same
  session: he likes CI, but "it's a bunch of trouble and i want to stay
  nimble as long as we can" — revisit CI when a red lands on main that the
  local pre-push discipline should have caught, or when a second regular
  contributor appears). Scheduled next session WITH [SAN-1], because
  the tier design must also place the sanitizer stages. Principles pinned
  now so the fast path never quietly becomes the only path:
  (1) `make test` NEVER WEAKENS — it stays the full suite and a green
  `make test` keeps meaning the complete claim; tiers are new names, not a
  redefinition. (2) SECTION TARGETS — `make test-corpus`, `test-cli`,
  `test-reject`, `test-registry` (PC-3 included), `test-codegen`,
  `test-spec`, `test-thread`, `test-parse` — thin make wrappers over the
  suite scripts that already run standalone, plus a TOUCHED-PATH → SECTIONS
  table in docs/testing.md (src/parse/* → reject+registry+spec+cli;
  src/gen/*+src/opt/* → corpus+codegen+trie+bench; tests/mech/* → mech;
  refine from measurement). (3) `make smoke` — a MEASURED <60s inner-loop
  subset, contents documented and floored so it cannot silently shrink,
  chosen from per-section runtime numbers recorded in testing.md, never
  vibes. (4) FULL LOAD AT EVALUATION POINTS — the wake §3 battery stays
  the merge/close standard; plus an OPT-IN local pre-push hook
  (scripts/hooks/pre-push running `make test`, installed only by an
  explicit `make hooks` — never auto-installed, no CI, D2's
  plain-make-for-strangers holds). (5) Every tier boundary NUMBER-BACKED:
  per-section runtimes measured at setup and re-recorded when any section
  doubles — that re-record trigger is the row's revisit-when


## 2026-08-13 (seventeenth session — [STD1] close)

- [STD1] STATE:completed — implement D37: the bare default becomes
  frozen named set `std1` = {classes, modifiers}; named-set plumbing
  (`--features std1|none|<explicit>`, older sets available verbatim
  forever, bare-default mapping advances only at announced version
  boundaries); artifact stamping (set name + expanded module list in
  emitted header + macro); FULL SUITE RE-BASELINE (reject_gated
  inversions, corpus `features` directives, check07 gate equivalence,
  PC-3 gate state all assume an empty default today); check09 per-name
  arming + check01 aperture/floors land here. Product-face change —
  starts with Frank's go, after MOD-0.8 closes
  - [STD1a] STATE:completed — named-set plumbing + artifact stamping,
    bare default KEPT EMPTY (mapping constant held at "none") so the
    suite stays green; stamp is UNCONDITIONAL incl. bare invocations
    (ruled in-session: D37's reproducibility rationale applies most to
    bare artifacts; skip-when-bare would make stamp presence depend on
    invocation spelling). Lane std1-impl, worktree std1-impl.
  - [STD1b] STATE:completed — flip PCREC_DEFAULT_FEATURES to "std1"
    + full suite re-baseline (reject_gated inversions, corpus features
    directives, PC-3 gate state, check07 population re-measure). Two
    lanes, after STD1a merges.
  - [STD1c] STATE:completed — check09 per-name arming + check01
    aperture/floors per docs/dev/std1_check_rearm.md (spec written
    2026-08-13, sabotage validations named there); after STD1b.

  Landing record: STD1a merge 3048303 (plumbing+stamp, bare default held
  empty); flip ab7592d; STD1b lane merges 5eebbed/09f0535 + compliance
  2aebe8b; STD1c merge + main landing db86a69. Close battery green at
  db86a69 (all steps exit 0; mech 35 rows undetected:0 anomalies:0
  pc3-skipped:0). New baseline counts: corpus 1284, cli 247, reject 528
  checks (274 rejections / 99 accepts / 55 gated / 99 iterated), codegen
  34, registry 168, PC-3 163, spec_mod0 14/14 (check09 per-name +
  check01 aperture ARMED), trie 7, thread 8. Phase C spec
  (std1_check_rearm.md) retired at close — content in git history and
  the sabotage evidence in the STD1c merge message.

## 2026-08-14

- [PC-5] STATE:completed (table LANDED 2026-08-14, merge 258fd79 — docs/pcre2_options.md, 80 flags, 10 measured; remaining work is FRANK'S RULINGS over the proposed-disposition column) — PCRE2 OPTION/FLAG DISPOSITION SURVEY (Frank, 2026-08-13 sixteenth session): every PCRE2 option, flag by flag — sibling to pcre2_compliance.md's construct-by-construct survey. Scope: compile options, match options, PCRE2_EXTRA_*, substitute options, DFA-match options, BSR/NEWLINE values. Columns: what it does, WHEN IT BINDS (pattern-compile vs match-call vs context), and a pcrec disposition from a small vocabulary: DONE-AS (already exists as X — e.g. CASELESS ≡ -i/(?i), D23), RIDES (lands with an owning module/milestone — MULTILINE → assertions/DD-6, UTF/UCP → M5), GENERATION-AXIS (D18 earn-its-axis candidate — ANCHORED/ENDANCHORED compile to the anchored variant; OS-0 named entry points serve callers wanting both), API-PARAM (runtime parameter on the generated entry point — NOTBOL/NOTEOL), EMITTED-LOOP (subsumed by generated iteration: NOTEMPTY/NOTEMPTY_ATSTART exist because PCRE2 callers hand-roll global-match loops around a raw single-match primitive; pcrec emits the loop itself at DD-4/M4-SUBST), LATER, and NEVER with reason (JIT options; NO_START_OPTIMIZE/NO_AUTO_POSSESS are generation-time decisions in an AOT compiler — cite M4-CALLOUTS' PCRE2_NO_START_OPTIMIZE-latitude precedent). Fiddly semantics MEASURED against libpcre2, never read from documentation alone (the Q2/K4 lesson: three candidate grammars refuted by measurement). Fact-gathering is subagent work; DISPOSITIONS ARE FRANK'S RULINGS over the finished table. Sequencing: the table exists BEFORE M4's match-API design freezes (bucket 2 is that design's input). Overlaps, deliberately not merged: DOC-BM owns the EXTRA_* effect on registry DISPATCH (this survey feeds it, does not replace it); DD-11 owns NEWLINE/BSR (those rows point there). Standing constraint to restate in the doc header: the suite's oracle is pinned at options=0 (R10 disposition 3), so adopting any flag is a deliberate re-measurement event. Output artifact: docs/pcre2_options.md, next to pcre2_compliance.md.

  Landing record: table merge 258fd79, review commit 9b0473c; dispositions
  RULED wholesale via D38 (docs/dev/decisions.md), three rows (LITERAL,
  DFA_SHORTEST, COPY_MATCHED_SUBJECT) ruled individually — all outcomes
  match the proposals. Every row stays individually re-openable; adopting
  any flag remains a deliberate re-measurement event.

- [M4.1] STATE:completed (2026-08-14, merge 65b16c6) — DESIGN: the MATCH-API FREEZE document
  (docs/design/match_api_m4.md). Collects every ruled obligation into one
  freezable contract: the rx_span → `ptrdiff_t[2]` pair break (D38 Q12 —
  a DD-3 versioning event at the M4 boundary, D37's announced-boundary
  shape), the caps array + RX_NCAPS/RX_UNSET surface satisfying subst
  C1–C11, the unconditional match-here export (F1/F2), rx_ctx +
  rx_callout_ref (F3, D38), the {name, number, ref} group index (F8, D39
  + addendum), the pcrec_error which-input tag (subst Q8), OS-0
  entry-point naming, the PCREC_* native constants surface (D38
  addendum; PCRE2_* compat-only), and how callout-pattern entry points
  thread nothing extra (user lives in the binding ref). Deliverable: the
  doc; freeze happens only AFTER M4.3's panel

  Landing record: authored by the m41-matchapi lane (sonnet), commit
  ca5742f, merged 65b16c6 same day. 621 lines, 13 sections; every claim
  marked RULED (D38/D39) / PROPOSED-here / BELIEVED; §12 collects the 8
  items introduced beyond the rulings, §13 the five ASKs for Frank
  (highest-leverage: rx_ctx/rx_matchfn/rx_callout_ref as deliberately
  UNPREFIXED fixed names; plus the DFA-with-groups caps[1..] question,
  forwarded to the M4.2 engine lane as its territory). No D38↔D39
  contradiction found. Manager review spot-checked the C8
  overwrite-between-splices consequence (real, carried by the D38 ruling
  text in subst_template_design.md §2) and the emit_dfa.c span-typedef
  citation (accurate). PROPOSED until M4.3's panel; freeze declared at
  that step's close.

- [M4.2] STATE:completed (2026-08-14, merge b726386) — DESIGN: the ENGINE document, its own design
  doc at docs/design/engine_m4.md (Frank, 2026-08-14) — the
  backtracking VM as EMITTED SPECIALIZED C (no runtime interpreter, per
  the project mandate), capture tracking with PCRE2's leftmost/priority
  semantics, DD-2's step budget (robustness tier, not a security
  boundary), per-pattern engine selection (capture-free patterns keep
  today's DFA engines; the backrefs-finite/atomic-cut analyses under
  this milestone are future selection customers), the DFA-prefilter
  hybrid and DFA-islands shape from APPROACH, DD-7 (which machine is
  the capture prefilter; ENG_UNANCH/anchoring absorption ownership),
  DD-9 (decide whether the hybrid owns the case-f dense/counting gap —
  the row's own requirement), and SR-8's lowering-time
  "requires the VM engine" refusal design. DD-8's --emit-ir/--emit-dot
  noted as optional bring-up tooling, schedulable as filler

  Landing record: authored by the m42-engine lane (strong model),
  commits 91a8f9e + 63cf7f5, merged b726386 same day (one CLAUDE.md
  both-added conflict, resolved keeping both entries). 1598 lines, 14
  sections + 8 falsifiable predictions (§13) + 12 ASKs (§12). Manager
  review spot-checked three STRUCTURAL claims, all confirmed:
  <prefix>_search's negative return space unused (lib/pcrec.h),
  selection is one if in compile.c:120, and zero VM_ONLY registry rows
  belong to a producer-backed module (so SR-8 flips nothing today).
  Key outcomes: DD-9 decided (hybrid structurally cannot own capture-free
  case (f); re-home to BENCH-1 with three findings); DD-2 gains a second
  bound (backtrack-frame capacity); budget failure surface reconciled
  with D38's frozen return space via the three-layer entry design (§4.4);
  match_api_m4.md ASK 4 answered (§5.7: RX_NCAPS is an artifact
  property; DFA artifact emits RX_NCAPS 1; RX_NCAPS>1 implies VM);
  three ABI tensions reported not resolved (§11). PROPOSED until
  M4.3's panel; four handed-back M4.1 amendments pending pre-panel.

- [DD-9] STATE:completed (2026-08-14, D42.8 — decided by design, engine_m4.md §8) — case (f) `[01]*1[01]{8}` dense/counting patterns: still a ~6x loss to PCRE2-interp and NO MILESTONE OWNS IT (R3 critic). M2.10 attempted it and produced a negative result; plan and review both say "an M4 concern" but [M4.0] never mentions it. Decide with the M4 hybrid-engine design whether the DFA-prefilter/VM split covers it, and note that the D13 correction makes computed goto a MEASURED win for predictable transition sequences

  Landing record: the decision the row demanded was delivered by
  [M4.2]'s engine document (engine_m4.md §8, merged b726386) and ratified
  by Frank (D42.8): the hybrid does NOT own case (f) and structurally
  cannot — the pattern is capture-free, so per-pattern selection keeps it
  on ENG_UNANCH and no M4 machinery ever runs on it. Ownership moved to
  [BENCH-1]'s prioritizer worklist (case (f) is its known head), carrying
  three findings: computed goto is the WRONG lever (the pattern's DFA is
  a 9-bit shift register over random input — D13's measured-loss regime,
  contra this row's own closing hint); ~2x of the 6.61x gap is the
  reverse pass (prediction P-5, instrument ASK-10); the algorithmic
  candidate is bit-parallel shift-and, detectable from the built DFA as
  an src/opt pass. M4.6 owes the family a non-regression floor via the
  capture-bearing sibling (engine_m4.md §8.5).

- [M4.3] STATE:completed (2026-08-14, nineteenth session) — D6 ADVERSARIAL PANEL over M4.1 + M4.2
  TOGETHER WITH the still-unpaneled design_callout_abi.md and
  subst_template_design.md (their panel-outcome blocks land here).
  Findings file under docs/dev/reviews/; fix-with-measurement before
  disposition. GATE: no implementation substep below opens before this
  panel's tier-1/tier-2 findings are dispositioned; the match-API
  freeze is declared at this step's close

  Landing record: R21 (docs/dev/reviews/2026-08-14-r21-m4-design.md) —
  three read-only critics (ABI/contract, engine-vs-oracles [strong
  model], coherence/staleness [sonnet]), 36 findings (11 tier-1), every
  one dispositioned same day: D44 (+ working-baseline addendum) ratified
  the ruling batch; the r21-fixes lane applied every doc disposition
  (merge f2629a3 + landing bar ae6946b/fc5d98f); the k17-fix lane fixed
  the panel's live shipped miscompile (K17 — K1's one-shot redirect
  guard removed from clo_visit, 120 oracle-verified family tests,
  corpus 1284→1404, 294/294 changed cells toward the oracle in a
  50,400-cell isolation sweep, sabotage-validated fuzz trap templates;
  merge of fb95b88/62690a9) and OPENED K18 (the path-dependent sibling;
  165 known_fail cases, design-first before [M4.6]). ubsan + asan both
  axes green on the composed tree; lint/bench/mech owed at [M4.4] close
  per the standing schedule. FREEZE DECLARED at close as the M4 WORKING
  BASELINE: match_api_m4.md STATUS flipped to FROZEN, engine_m4.md to
  DESIGN OF RECORD. Headline panel results: python-vs-PCRE2 oracle
  disagreement measured ZERO across 225,240 pairs (ASK-1 refuted — the
  planned exclusion mechanism would have hidden K17; three-way
  2-1-minority rule adopted); the erasure argument, trail discipline,
  VM sketch, cliff guard and all 11 STRUCTURAL citations HELD under
  attack; what broke was what was marked BELIEVED.

- [M4.4] COMPLETED 2026-08-14 (merge c18e904, break commit 1dbb6ce) — IMPL: the API BREAK lands mechanically —
  rx_span RETIRES for the caps-array search signature across
  emitters/harness/corpus (D44.2), the pcrec_error tag, PCREC_*
  constants, match-here export + the slot-bearing group index folded
  into rx_info (D43.1/D44.3) retrofitted onto the EXISTING DFA matchers.
  CORRECTED 2026-08-14 (R21 C-4): this clause previously said "rx_span
  becomes the pair type" and "(empty-ref) group index retrofitted",
  both stale against D44's search-signature reshape and D43.1's rx_info
  fold — see docs/design/match_api_m4.md §1.0/§5. Coverage
  conservation per the STD1 re-baseline shape: suite populations
  conserved and accounted, one announced break commit. AMENDED
  2026-08-14 (D42, D43): the same boundary also carries the
  `<prefix>_match_caps` entry (D41.4), the search entry's reserved
  negative returns (RX_ERR_STEPS/RX_ERR_FRAMES, D42.3), the
  RX_NCAPS>1⇒VM structural check (D42.2 — trivially green until M4.5),
  the `pcrec_options` flags-word break (booleans → PCREC_* bits,
  D43.2), and the `rx_info` reflection struct (D43.1 — flags, encoding,
  pattern string, folded group index, engine, budget; the group index
  no longer lands as freestanding symbols).
  COMPLETION RECORD: all 12 of match_api_m4.md §11's checklist items
  discharged (item 12 as a recorded obligation only, per its own text);
  counts corpus 1404, cli 247, reject 528 (274/99/99/0), codegen 34→37
  (+2 structural: ncaps==RX_NCAPS-by-construction and NCAPS>1⇒VM; +1
  cross-prefix one-TU compile, D44/A-2's positive control), registry
  168, PC-3 163, PC-4 273/62,872 cells/0 disagreements, trie 7,
  thread 8, known_fail 1 (K18 deliberate, ratchet did not fire); OS-1
  whole-file diffs and parse's ast-identity re-scoped to the rx_search
  ENGINE BODY (rx_info.pattern/flags differ by design, the D37
  stamp-differs shape), with a manager review fix making empty
  extraction a hard fail (2498bf4); S04 mech sabotage retargeted from
  the retired emit_span_typedef to PCREC_RX_ABI_H guard-neutering, its
  assertion direction deliberately inverted (dup emission is now safe
  BY the guard; validated in the close battery: codegen 2fail,
  DETECTED, 35 rows 0 undetected). New emit_c_string_literal escaper
  for rx_info.pattern (three-digit octal, unconditional \? for
  trigraphs — found failing-first against review_r21.rxt). AS-BUILT
  DEVIATION recorded in match_api_m4.md §5 (needs ruling): rx_info is
  a struct TAG with no typedef alias — the bare typedef collides with
  the default-prefix instance name rx_info, a miscompile-shaped find
  by the lane. Full battery green at close: test + strict + ubsan +
  asan + lint + bench + mech (TMPDIR=/var/tmp), discharging the
  lint/bench/mech debt owed since the eighteenth session.

- [M4.5] COMPLETED 2026-08-15 (STATE:started 2026-08-14 (expanded on opening, twentieth
  session) — IMPL: VM emitter core — captures over the base tier,
  search + match-here entries, DD-2 budget wired; .rxt format extension
  for capture expectations (docs/testing.md updated), python-re
  group-span oracle tier, and a D27-blinded capture test author per
  convention. Substeps:
  - [M4.5a] STATE:completed 2026-08-15 (lane m45a-oracle, 81b8b43 +
    manager-landed comparison fix c021d6e after the RX_NCAPS>1
    integration break; full battery green at 94abf78) —
    capture TEST INFRASTRUCTURE: the .rxt
    capture-expectation format extension, tests/harness caps-array
    reading, the python `re` GROUP-SPAN oracle tier (engine_m4.md §3.6
    as re-scoped by R21 E-ASK-1: the THREE-WAY pcrec/python/pcre2
    2-1-minority rule is the governing rule, NEVER pre-built
    exclusions — a python-vs-pcre2 disagreement is an
    upstream_issues.md row + arbitration, not an exclusion),
    docs/testing.md updated. Landable against [M4.4]'s DFA artifacts
    (caps[0] is live today); the format must already carry group
    slots for the VM. Disjoint from [M4.5b] by construction (tests/
    harness + docs; no src/).
  - [M4.5b] STATE:completed 2026-08-15 (lane m45b-vm, 7 commits ending
    c0f24bc; full battery green at 94abf78. As built: src/gen/emit_vm.c; A_CAP born only when
    captures requested and invisible to the NFA builder so D31's
    erasure holds by construction; the §5.4 gate is a PERMANENT check,
    tests/codegen/run_vm_identity.sh, verified once against a compiler
    built from the pre-lane commit; §3.7's differential is a GATE with
    the prefilter off; new sections tests/vm (18) + run_vm_identity;
    sabotages S36–S40 all DETECTED; also --step-budget/
    --fno-step-budget/--backtrack-frames CLI axes) — the VM EMITTER
    CORE (engine_m4.md is the
    design of record): §2's emitted shape (explicit resume stack +
    capture trail, one cold indirect jump, §2.5's cursor ladder), §3
    captures under leftmost-first with exact-undo and the E-2-narrowed
    empty-iteration guard (rmax == -1 only), §3.4 caps delivery, §4's
    TWO bounds wired as MECHANISM (bring-up placeholder budget;
    RX_ERR_STEPS/RX_ERR_FRAMES produced; [M4.6] calibrates), §2.6
    search-wraps-match-here, §6.1's prefilter (the existing
    capture-erased forward+reverse pair hands the VM an EXACT span —
    the VM never scans), §5.1–5.3 selection as a pass with the
    requested-OUTPUT trigger (D42.1 captures-on-default;
    --no-captures recovers today's artifact), RX_NCAPS>1 artifacts +
    rx_info engine/budget fields live, --engine=dfa|vm|auto do-or-die
    (R21 E-6: --engine=vm disables the prefilter; --engine=dfa
    REFUSES captures-default group-bearing patterns, D44.6). GATE
    (§5.4): emitted C for the capture-free corpus byte-identical to
    the pre-M4.5 emitter modulo stamp lines — a check, not a promise.
  - [M4.5c] STATE:completed 2026-08-15 (lane m45b-vm, d3714b9..de21cce;
    landed WITH the D45 compile-budget wrapper +
    PCREC_MAX_VM_REPEAT_COPIES=64/K19 + the K20 spine-recursion
    segfault find-and-fix + bigbounded resize + hermetic gen-timeout
    units + bench (c)/(d) --no-captures pins; full battery green at
    94abf78) — DD-8's VM TRACER. As built: `--emit-ir` is a QUERY (shaped like --count-groups:
    real pipeline, prints the listing, no -o, no C) printing labels, choice
    points with preference order, capture slot assignments, and honestly
    empty island/callout sections whose emptiness is derived from a COUNT
    rather than blanked; `--trace` is a generation axis (PCREC_TRACE)
    emitting an instrumented artifact that prints every resume-frame
    push/pop and capture write to stderr, never the default and stamped as
    traced. §10's one constraint is STRUCTURAL, not a discipline: the
    listing is an EVENT STREAM appended by the emitter's own primitives
    (vm_lbl/vm_push_at/vm_set each write C and record what they wrote), and
    every section is a view over that one stream. New check
    tests/codegen/run_ir_listing.sh (60), which caught a real drift on its
    FIRST run — the accept label was emitted by a direct sb_printf and so
    was missing from the listing; sabotages S41/S42 both DETECTED. As-built
    decisions for the manager: --emit-ir REFUSES on a pure-DFA artifact
    (§10 and DD-8's row are silent; the alternatives were inventing a DFA
    listing or printing an empty one that looks like a bug), --emit-dot is
    NOT built (§10 steers away from the automaton picture), and
    run_vm_identity.sh + run_ir_listing.sh moved to the test-vm section on
    a measured smoke-budget argument. Original charter: DD-8's VM TRACER
    with bring-up (Frank
    REQUESTED): §10's emitted-program listing (labels, choice points
    with preference order, capture slot assignments, island
    boundaries, callout call sites) + optional one-subject
    resume-frame push/pop trace; derives from the SAME structure the
    emitter walks, never a parallel description. Rides or immediately
    follows [M4.5b]'s lane. DD-8's row stays OPEN for `--emit-dot`, which
    this substep deliberately did not build.
  - [M4.5d] STATE:completed 2026-08-15 (cell m45d-capauthor; merge
    dc5a29a; R22 review + author-notes appendix in docs/dev/reviews/;
    230/230 green, corpus 1449→1679; two contract-text gaps found and
    dispositioned — retention + empty-final-overwrite, three-way
    unanimous, match_api_m4.md §2.2 addendum; M4.7 wording pass owed)
    — D27-BLINDED capture test author
    (CELL, scripts/mk_d27_cell.sh): spec-first capture tests from the
    PROMISE (match_api_m4.md + testing.md's new format), denied src/
    and tests/. Opens once [M4.5a]+[M4.5b] merge.
  - [M4.5e] STATE:completed 2026-08-15 (lane m45e-close, 5 commits ending 655fdf0, merge 7e3ff93; close battery ALL SEVEN LEGS GREEN at 7e3ff93 — mech 44/0/0, bench 0 budget failures; corpus baseline 1704) — CLOSE: oracle-verified capture corpus
    over the base tier, structural checks now non-trivially exercised
    (RX_NCAPS>1⇒VM live), CLAUDE.md sweeps, full battery. ADDED
    2026-08-15 (D46): the cursor-ladder RUNG STAMP — the selection
    [M4.5b] makes silently between its two rungs becomes observable
    (rx_info/macro family per D46's observability half), and the
    existing rung-boundary tests (33-nested → cursor, 70 → frames)
    ASSERT the stamp instead of assuming selection by construction.
    Rung FORCING (D46's controllability half) may land here if cheap
    or ride [ENG-BREP]/[M4.6], whichever comes first — but the stamp
    itself is a close obligation.

## 2026-08-15 (twenty-third session — the K18 rewrite)

- [K18-FIX] STATE:completed 2026-08-15 (lane k18-rewrite, branch
  `k18-rewrite`) — IMPL: the path-sensitive epsilon closure, built from
  `docs/design/k18_memo_design.md` as amended by R23. Scheduled DESIGN-FIRST
  at R21 close and gating [M4.6]; that gate is now DISCHARGED.
  `src/ir/dfa.c`'s closure memo is keyed on (state, OPEN-LOOP CONTEXT) and
  the empty-iteration redirect fires on "this loop is OPEN on my path",
  with A2's empty-context fast path (ctx 0 keeps the pre-K18 per-state
  stamp array, which is worth 7x on a real pattern for byte-identical
  work).

  **§5 item 12, the note's one open decision, is answered ITERATIVE** —
  and the reason it is affordable is a representation change, written up
  in the note at the item and in the code: the prototype's `open[]` array
  is a redundant materialisation of the interned context chain, so the
  chain becomes the open-loop stack's only representation. R23 S3's
  per-frame ENTRY save collapses to one carried int and its
  ancestor-clobber defect stops being expressible; per-frame state then
  fits in a 12-byte deferred-branch record, so the Θ(d²) recursion
  becomes an explicit LIFO and C-stack depth stops depending on the
  pattern at all (better than the pre-K18 Θ(d), and it removes item 11's
  non-main-thread hazard rather than documenting it). Refusing above a
  depth was rejected as a D46-observable selection point for a class that
  compiles in 0.37 s; deliberate stack sizing is unavailable in a library.

  All thirteen §5 items discharged. Corpus 1704 → 3198 cases (+1494: the
  165 activated from `tests/known_fail/` plus 1,329 new on the arm-order,
  `{0,2}`-split, deep-nesting and cost-gate axes, every expectation agreed by
  python3 `re` AND libpcre2 10.46, and the nine K18 fuzz trap rows validated
  at 56 divergences pre-fix / 0 post-fix). Blast radius: 547 identical / 8 differing of
  555 compiling corpus patterns, the 8 exactly the K18 shapes; 249 of
  18,858 shape-space patterns. Direction: 251 changed cells, 251
  old-wrong → new-right, 0 regressed, 0 both-wrong. Non-vacuity measured
  per guard file against the PRE-FIX compiler (26 / 62 / 63 failures).
  Full close battery green: test (parallel and serial PROCS=1), strict,
  ubsan, asan, lint, bench, mech, plus the trie-identity gate run
  explicitly (500 patterns + the `-i` sweep, 0 differing) because that
  gate's erasure argument was written for a path-INSENSITIVE closure.

## 2026-08-17 (twenty-eighth session — counter-K lands, the ladder completes)

- [ENG-BREP] STATE:completed 2026-08-17 (twenty-eighth session — COUNTER-K
  MERGED at main 78b891e, full battery green; row closed with all three
  ladder rungs BUILT: possessify, revdet, counter. Was: STATE:started
  2026-08-15/16, twenty-fourth session — DESIGN
  NOTE BUILT, PANELED R24, dispositions applied: docs/design/
  eng_brep_design.md + reviews/2026-08-15-r24-eng-brep.md. **ALL SIX §9
  RULINGS RULED 2026-08-16 — decisions.md D47** (possessify-first both
  orders; K=8 as a limits.h constant; deny-flag surface, (*...) hints
  deferred; consequence (b) struck-and-replaced below; $-gate ships in
  v1, M6.0 carries the inherited test obligation; lazy conjunct accepted
  at measured cost ZERO — the "20 false declines" were refuted during
  the ruling, all 20 genuinely diverge, subject-alphabet blindness in
  the probe). **POSSESSIFICATION BUILT AND MERGED 2026-08-16 (D47.1's
  first rung; merge 1eac1b9):** src/opt/possessify.c (the §2.2 repaired
  rule, lazy conjunct, LIVE multiline gate — cx->mods.multiline has no
  writer until module `assertions`, which inherits the M6.0 gate-test
  obligation), two emitter shapes (cursor: zero machinery; frames: ONE
  frame via the new vm_cut/RX_CUT primitive), -fno-possessify +
  <PREFIX>_VM_STRATS stamps (D46 both halves), differential 365
  patterns/158,827 cells/0 divergences, byte-identity on all
  verdict-free patterns, mech S45-S49 + re-verified emitter sabotages,
  corpus 3,270 → 5,984 expected post-merge. Guard corpus for the lazy
  conjunct: tests/base/possess_lazy_guard.rxt (D47.6). OWED FROM THIS
  LANDING, recorded: (1) the STEP-BUDGET BLIND SPOT — a possessified
  loop charges no steps, so --engine=vm (diagnostic mode only; the
  default prefilter path is unaffected) turns a fast RX_ERR_STEPS
  give-up into a correct-but-quadratic answer (measured 0.033/0.581/
  2.297 s at 10/50/100 KB; 228.5 s at 1 MB, terminating and correct) —
  fix-of-record CORRECTED 2026-08-17: the E-5-shaped entry charge was
  REFUTED by the counter-K lane's own measurement (R25 §7.2 — entries
  and steps are already the same number; the charge is linear while the
  work is quadratic); the ruled fix is the counter-K design note §7.4's
  forward-work meter under F-2 SETTLEMENT 4 (its own bound, rx_info
  field and RX_ERR_* code — decisions.md D47 SECOND ADDENDUM), owed
  with the counter-K step; (2) tests/vm per-RUN timeout —
  DISCHARGED 2026-08-16, twenty-fifth session: gen_run/gen_run_secs in
  tests/lib/gen_timeout.sh (D45 second addendum; scripts/watchdog-backed,
  wired tree-wide), fire-controls in run_gen_timeout_tests.sh; (3) K22
  filed (nested-bounded-repeat
  compile hang under --engine=vm, known_issues.md — interim product
  guard or counter-K). **RUNG-SELECT BUILT AND MERGED 2026-08-16
  (D47.1's second rung; merge 274e5a0, 8-leg battery green incl.
  bench):** src/opt/revdet.c (TWO unique-iteration checks, forward
  imported from possessify.c, reverse on the REVERSED AST which is
  also the verdict field Ast.revbody; every unmodeled shape DECLINES),
  vm_revdet_rep in emit_vm.c (ONE body copy; forward scan cutting
  choice points at iteration boundaries — O(1) frames; retreat = ONE
  re-pushed frame stepping boundaries backward via the reversed body,
  which doubles as §3.4's last-iteration capture walk, zero-iteration
  clause structural; lazy commits at minimum and extends). K22 INTERIM
  GUARD in the same landing (product-of-replication-factors refusal,
  bound = PCREC_MAX_VM_NODES so it only moves refusals EARLIER; depth
  35/40 hang → 0.12 s refusal; K22 stays OPEN for counter-K).
  Acceptance cell: ((a)|b){0,4000}c compiles 293 lines / 0.12 s pcrec
  / 0.12 s gcc, size count-independent (was cap-refused; 113k lines
  uncapped) — D47.1's refuse-cap ENDGAME landed. Differential 205
  patterns / 395,757 cells / 0 divergences; corpus 5,984 → 7,655;
  -fno-revdet + VM_RUNG_REVDET stamp (D46/D47.3). FIVE existing
  checks went GREEN-BECAUSE-FAST (D46's motivating scenario, incl.
  the D45 compile-budget positive control and the exact-mask
  mixed-rung stamp D46's text nominated) — all re-pinned with
  -fno-revdet AND paired with the other side of the fact (no-ceiling
  gate, endgame-compiles rows); D45 control gained a SIZE FLOOR that
  counter-K will meet. Residuals (design file §5, nine): single-level
  scope, reverse/forward-ambiguous bodies, nullable, assertions,
  ranged nested, >64 groups, a Glushkov modelling decline, and the
  STEP-BUDGET BLIND SPOT now WIDENED (possessified loops, the revdet
  scan AND the walk all charge nothing — covered by the counter-K
  design note §7.4's forward-work meter under F-2 settlement 4, which
  REPLACED the refuted E-5 entry charge; D47 SECOND ADDENDUM). Follow-up recorded
  eng_brep_design.md §8.1: capture-walk sinking (eager/n-step/
  accept-time; bench eager-vs-sunk with counter-K's harness).
  NEXT LADDER STEP: counter-K (carries: the §7.4 forward-work meter
  under F-2 settlement 4 [replaces the refuted E-5 entry charge, R25
  §7.2], K=8 limits.h constant, size cap → backstop-only, -fno-counter,
  the gen_timeout size-floor tripwire; K22 CLOSED separately by F-1 —
  D47 ADDENDUM, compile half re-homed to [ENG-CLAMP]).
  **COUNTER-K DESIGN NOTE ACCEPTED 2026-08-17** (manager, after F-2 =
  settlement 4 applied on the lane branch and reviewed; note at
  docs/design/counterk_impl/counterk_design.md on lane/counterk, R25
  twice-verified, findings 1-29 dispositioned). **BUILD PHASE STARTED
  same day**, additionally carrying D49's conforming edits (uniform
  rx_matchfn negative-code contract: match_api_m4.md §1/§3.1,
  design_callout_abi.md F2's named-floor trap, the emitted give-up
  comment block emit_vm.c:3137-3147) and the ruled work-bound surface
  (work_budget default ~10⁹, RX_ERR_WORK, one existence gate in v1).
  R24-corrected census: 17%/82%; as-built verdict census 252/1,832
  source quantifiers (13%), archived docs/design/possessify_impl/) —
  BOUNDED-REPEAT EMISSION STRATEGY: the
  counter rung (Frank, 2026-08-15, twenty-first session — queue
  placement ruled alongside M4.6; "sort-of an optimization, but
  strictly the result was intractable, so not"). Today the VM emits
  {0,N} by FULL REPLICATION (N body copies), which is O(N·body)
  emitted C — ((a)|b){0,4000}c produced 113,545 lines / 3.5 MB and
  gcc goes superlinear on it (the D45 incident); the interim guard is
  the D45 compile timeouts + the refuse-above-cap backstop. The real
  fix is DESIGN-FIRST (short note against engine_m4.md §2.5, panel
  eyes, K17-lane validation methodology): ONE body copy + an
  iteration counter in the backtrack frame. The strategy space is one
  axis — unroll factor K: replication is K=N, the pure counter loop
  K=1, and Frank's partial-unroll suggestion K=8/16/... amortizes
  counter bookkeeping over straight-line copies; choice points (one
  per iteration, semantics-dictated) are IDENTICAL across all K, so K
  is purely a speed/size dial picked by BENCH MEASUREMENT (sweep
  N × K × body size, compile time AND throughput — BENCH-1's
  bounded-repeats family is the home). FOUR ruled requirements
  (Frank, same discussion): (1) ACCURACY HAS A TRUE VERSION —
  replication is the semantic ground truth (literally {0,N} unrolled)
  and is tractable below the knee, so the primary instrument is a
  pcrec-vs-pcrec differential: same pattern under forced-replication
  vs forced-counter(-K), subjects swept, spans + EVERY capture slot +
  the FAILURE SURFACE (RX_ERR_FRAMES at the same iteration count)
  byte-equal — any disagreement is a bug by construction; (2) every
  strategy stays FORCEABLE end-to-end via a generation flag,
  do-or-die (the R21 E-6 testability pattern); (3) the three-way
  python/pcre2 oracle sweep rides on top, dense at the K-threshold
  boundary, N=0/1, rmin>0, empty-capable bodies, captures in the
  loop; (4) E-2's ruling is load-bearing: bounded repeats take NO
  empty-iteration guard, and the counter's strict increase is what
  makes that safe — the design note must state the termination
  argument explicitly. AMENDED same day (Frank's [ab]{0,4000}
  observation, MEASURED): RUNG SELECTION COMES BEFORE STRATEGY K —
  the capture-ERASED artifact of ((a)|b){0,4000}c is 1,378 lines /
  0.078s to compile (the count lives in table-driven DFA states:
  DATA, which gcc swallows; determinization already collapses
  single-byte alternation into class transitions, no AST rewrite
  needed), vs the VM's 113,545-line replication — and PCRE2
  semantics report only the LAST iteration's capture, so the
  replicas' 3999 other capture writes are unobservable by
  definition. This class belongs to §2.5's REVERSE-DETERMINISTIC
  rung (Frank's play-the-regex-backwards rung, UNBUILT — [M4.5b]
  landed 2 of the 5 rungs): DFA pair delivers the exact span,
  last-iteration captures derived by walking backward from end
  (here: group1 = [end-2,end-1), group2 = same iff subject[end-2]
  == 'a'). The counter-K loop is the fallback ONLY for genuinely
  nondeterministic bodies where per-iteration backtracking is real.
  SECOND AMENDMENT same day (Frank: "going back through an a and b
  string isn't going to find c"): DISJOINT-FOLLOW POSSESSIFICATION is
  the analysis that PROVES backtracking dead for this class — body
  consumes only [ab], follow requires c, so giveback re-examines a
  byte that cannot be c (and a|b's branches are per-byte disjoint, so
  intra-body backtracking is dead too): the quantifier is
  possessive-equivalent, zero frames. This is already designed
  (engine_m4.md §6.4 "disjoint-follow possessification, built M4.6";
  PCRE2 precedent: pcre2_auto_possess.c) and its delivery seam is
  §5.2's verdict-discharging rewrite socket (the atomic-cut row). The
  design note's question ORDER is therefore: (1) possessify — which
  bounded repeats provably need NO backtracking machinery; (2) which
  residual bodies each ladder rung captures (erasure measurement
  above as the motivating cell); (3) the K-axis for what remains. Supersedes
  the "cap emitted size" half of the D45 follow-up as the ENDGAME
  (the cap stays as the backstop whose diagnostic can honestly
  point here). THIRD AMENDMENT (R23 panel, 2026-08-15 evening,
  semantics critic S14 — reviews/2026-08-15-r23-k18-memo.md):
  replication has a third victim beyond emitted size and gcc time —
  THE COMPILER'S OWN CLOSURE WALK. A_REP's nested copies multiply the
  loop-nesting depth the epsilon-closure's open-loop machinery
  actually sees: a 78-char pattern with source-visible nesting ~3
  measured at EFFECTIVE depth 11, and under the K18 path-sensitive
  memo the cost driver is the CONTEXT COUNT, which grows with the
  unrolled copy count while depth stays constant (k∈{2..5} sweep:
  depth pinned at 11, contexts 450→40k, compile 0.3s→52s on the
  unfixed prototype; 0.11-0.12s after the S16 stack fix, but the
  depth-multiplication mechanism is prototype-independent and
  MEASURED). **CORRECTED 2026-08-15 (k18-revision lane's re-measurement
  on the FIXED prototype): the depth-multiplication half is REFUTED
  and is NOT prototype-independent.** Same patterns, same binary but
  with the open-loop stack's ENTRIES restored per frame: max open
  depth is **1**, not 11, and contexts grow LINEARLY (13/19/25/31/37/
  43/49 for k=2..8) against the unfixed prototype's 450/2,834/11,770/
  40,422 — compile time 2.9ms → 8.7ms across k=2..8, linear, where
  unfixed was 0.22s → 50.7s over k=2..5 and did not finish beyond.
  The depth of 11 was the CORRUPTED stack failing to pop loops whose
  redirects were missed; A_REP's copies sit in SEQUENCE, so a walk is
  inside at most one at a time and the open-loop depth does not
  multiply. Consequences carried forward: (a) any depth- or
  context-shaped budget anywhere in the compiler must be posed on the
  UNROLLED quantity, never on nesting as a reader counts it in the
  pattern — the surviving evidence for this is the NFA itself (405
  states at k=2, 1,485 at k=8, from a pattern whose visible nesting
  never moves) plus the rule that the closure's cost driver is the
  CONTEXT COUNT, which the memo keys on, and not reader-visible
  nesting; (b) ~~ENG-BREP's replication reduction also shrinks pcrec's
  own DFA-construction work~~ **STRUCK-AND-REPLACED (Frank, 2026-08-16,
  R24 ruling 4; refutation measured in eng_brep_design.md §1.4):**
  possessify/rung-select/counter-K are EMITTER-side strategies, while
  the replication the compiler itself suffers happens upstream in
  src/ir/nfa.c's A_REP lowering — this row shrinks nothing there. The
  SURVIVING measured fact: the compiler's own cost on the
  capture-erased path is QUADRATIC in the unrolled count and lives
  almost entirely in the REVERSE DFA (4,002 states at N=4000 vs a
  2-state forward DFA at every N; 0.012 s → 2.689 s over N=64..4000).
  Shrinking THAT would be an IR-level lowering change — a different,
  currently unproposed row; (c) the
  bounded-repeat-times-nullable-loop family (S14's witnesses, ~0.1%
  of random patterns) joins the cost-gate families any strategy
  bench must sweep.

## 2026-08-17 (twenty-ninth session — M4.6 CLOSES: MRL lands, K23 closed, D46 prefilter pair, both ASK-6 items measured-no)

- [M4.6] STATE:completed 2026-08-17 (started twenty-eighth session, closed twenty-ninth) — CLOSE-OUT
  of the engine-selection milestone. **AUTHORIZED (Frank, 2026-08-17):
  "continue through M4.6".** ROW PROSE CORRECTED against the scoping
  sweep (2026-08-17, read-only lane): "per-pattern engine selection +
  DFA-prefilter hybrid" ALREADY SHIPPED in [M4.5b] (select_engine.c's
  full §5 pass, fit.prefilter at :259, --engine=dfa|vm|auto, RX_ENGINE/
  RX_ENGINE_WHY, D44.6 refusal); DFA ISLANDS DEFERRED OUT of this
  milestone (Frank, 2026-08-17, D50 — evidence-gated, new row
  [ENG-ISL]). What M4.6 actually delivers, as substeps:
  - [M4.6a] STATE:completed 2026-08-17 — BUDGET CALIBRATION done
    (lane m46a merged 0078ce1; docs/design/m46a_impl/ carries the
    instrument + archived sweep; §4.6 EXTENDED to all four bounds via
    one real-meter run, DEFAULT-engine numbers only — the forced
    --engine=vm split was the sweep's key methodological catch).
    LANDED: frame/trail 2x — BOTH knob pairs, VM_DEFAULT_* and
    VM_MAX_AUTO_* (902cb91+5c838fc; the second pair discovered
    half-landed when the endgame ceiling did not move; endgame 307→614
    verified; zero re-pins — the counterk/possessify cells read stamps
    dynamically). KEPT: work 10⁹ (empirically corroborated, 83x
    headroom on the worst ordinary shape). DEFERRED TO FRANK: step
    budget (1M → 20M rec / 500M parity option) — raising it flips the
    K23 known_fail resident (10.6M steps) to passing, so it lands WITH
    adopt-MRL/[M4.6d] where the interaction dissolves. Ratio re-anchor:
    the retracted 5.24 proxy has NO real-meter analog (work=0 on the
    exemplar); steps and work measured as genuinely disjoint cost
    classes. Doc note owed sometime: --engine=vm users should pass
    explicit --work-budget (diagnostic mode has no prefilter
    protection).
  - [M4.6b] STATE:completed 2026-08-17 — DD-9 capture-bearing bench
    sibling DONE (lane m46b merged; case (j) in tests/bench/compare's
    matrix, VM-hybrid confirmed, floor 150.369/0.900 from three
    quiet-box runs). PLUS two findings out of the substep: (1) cases
    (c)/(i) had silently measured the WRONG ENGINE since D42.1's
    captures-default (floors captured on the DFA, patterns routing to
    the hybrid) — RULED: pinned --no-captures per the run_bench case
    (d) precedent, and the durable fix landed: PER-CASE
    rx_info.engine ASSERTIONS in compare.sh (ENGINE MISMATCH
    hard-errors before any number is trusted); compare/ marked
    ages-freely rather than battery-wired. (2) K24 filed
    (known_issues.md): the residual case (c) DFA regression (~300 vs
    388 floor, engine-verified, gate deliberately RED) — bisect
    queued. **K24 IS NOW CLOSED (2026-08-17, k24bisect + k24fix
    lanes): not a DFA regression at all — gcc -O2's partial-inlining
    pass was splitting `<prefix>_search` into a trampoline plus a
    `.part.0` clone in every unanchored DFA artifact since [M4.4],
    identical instructions, a pure code-PLACEMENT cost. Fixed in the
    EMITTER (`noclone` on `<prefix>_search`; pcrec cannot dictate its
    users' CFLAGS). Floor NEVER touched — case (c) recovered to
    391.063 MB/s at its historical 1.02x spread and the full gate is
    10/10 green (results-ubuntubudu-20260817-2.md). The
    deliberately-RED floor is what carried the finding across three
    lanes; it is the posture that worked.** K-sweep archived INCONCLUSIVE
    (docs/design/counterk_impl/bench_k.txt): the pre-recalibration
    frame placeholder invalidated the high-N regime and the driver
    lacks median/spread; re-run only after a driver upgrade or when a
    K answer is actually needed.
  - [M4.6c] STATE:completed (2026-08-17, same session start-to-accept) —
    K23 DESIGN-FIRST note, **ACCEPTED**: docs/design/k23_impl/
    k23_design.md on lane/k23 (31 commits, docs-only). MRL PRUNING
    recommended and twice-panel-verified (R26 + same-day verification:
    the lattice-rounded clamp, stride/residue corpus, 1,059 cells /
    0 disagreements, sabotage arm 101-red-zero-at-stride-1 proving the
    old corpus incapable; preference-blindness PROVEN — the explosion
    needs a greedy INNER; closed-form step law exact out of sample;
    memoization and routing priced and refuted). Review:
    reviews/2026-08-17-r26-k23.md. TO FRANK: adopt-MRL, and ruling 6
    (prefilter-window ceiling — v1 with three build obligations vs
    subject-end fallback; a stale window errs UNSOUND, see the
    verification's direction-of-error note).
  - [M4.6d] STATE:completed (2026-08-17, twenty-ninth session; lanes: mrl
    opus build in worktrees/mrl, plus a cell-isolated test author this lane
    spawned in its own cell — see the finding below) — **K23 FIXED** by
    MINIMUM-REMAINING-LENGTH pruning per D51's three rulings, all in one
    change on lane/mrl. Exemplar `(a{10,20}){10,50}` at 100 bytes: 10.6 M steps
    (RX_ERR_STEPS) -> **<=1**, captures identical to python and to the
    unpruned build; the three-level shape 11,906,349,370 -> <=1. Validated
    as a pcrec-vs-pcrec differential against `-fno-length-prune`
    (tests/mrl/run_mrldiff.sh): **202,458 cells / 0 divergences**, strides
    1-3, lengths on and off the lattice, all four greedy/lazy combinations,
    BOTH ceiling forms. Ruling 2 taken with all three obligations as code:
    the ceiling is a match-function PARAMETER (so an entry that forgets it is
    a compile error, discharging (a)), the start++ retry RECOMPUTES the window
    ((b) — the structural no-fire argument is written down and deliberately
    NOT relied on, since it rests on the span-equality R21 split to
    BELIEVED-WITH-GATE), and `<PREFIX>_VM_PRUNE_CEILING` names the active form
    ((c)). Ruling 3's 500M step default lands WITH it, so the ratchet resident
    flips because the defect is fixed rather than outspent; the resident moved
    to tests/base/ and K23 is CLOSED. **PREDICTION 6 ANSWERED, in the negative
    direction**: the revdet rung needs NO lattice argument, because its
    forward scan IS the walk onto the boundary set — the bound stops the scan
    one boundary early and the E1 substitution has no spelling there. **AND
    THE E1 CLASS RECURRED ONE RUNG DOWN, found from OUTSIDE the
    implementation's own model** (a cell-isolated author this lane spawned
    before it knew the manager had one): on the counter rung one body copy serves every trip, so the
    compile-time follow-min tops out at `K + residue` (9 on `(a{1,3}){65}`
    where the truth is 65) and K23 stayed alive on it — the differential, the
    structural checks and the acceptance cell all agreed with the bug because
    all three were derived from the model the bug was in. Fixed by building
    §4.5's runtime term (`Vm.fdyn`, read from the trailed counter slot). PER
    THE MANAGER'S MID-FLIGHT CORRECTION the owed-region file is NOT delivered
    here — the D27 corpus of record is d27k23's
    tests/base/d27_k23_ambiguous_decomposition.rxt, and two corpora over one
    region collide at merge; this lane keeps the MECHANISM guard instead
    (tests/mrl/run_mrl_tests.sh §1b: (a{1,3}){65} answers inside eight steps
    and the emitted bound reads the counter). The remaining tests/mrl/ .rxt
    files are 191 ORDINARY implementation cases, labelled as such.
    CROSS-CHECK, run before the removal: d27k23's corpus (89 cases, a
    different author in a different cell, expectations from a separately
    proven law) passes 89/89 against this build, neither author having seen
    the other'"'"'s work, and it covers the same rung and the same runtime term. Battery: test
    10,168/0 (ratchet "nothing to ratchet"), strict, mrl 19/19 + 202,458
    differential cells (per-rung coverage complete), gate.sh 10/10 with case
    (c) at 392.445 above its 388.615 floor, ubsan/asan. THREE HARNESS FIXES the budget move forced, reported
    as such: counterkdiff and the vm §4.7 contrast now PIN the step budget
    (they were measuring a calibration default), and the possessify stamped-
    ceiling check becomes a floor-with-window because MRL legitimately makes
    that artifact 2 bytes more capable than it declares. Design note gains
    §14, its BUILD OUTCOME section.
  - [M4.6e] STATE:completed (2026-08-17, lane m46e) — RX_HYBRID_MIN
    (engine_m4.md §12 ASK-6) + the trie-factored VM alternation switch
    (§2.2 item 4/§6.4), both MEASURE-THEN-IMPLEMENT, both **MEASURED-NO,
    neither built** — a fully successful outcome under the brief's own
    bar. RX_HYBRID_MIN: a subject-length sweep at fixed match offset (three
    capture-bearing shapes, `-fno-prefilter`'s existing [M4.6f] force pair
    reused as the VM-only build, no new plumbing needed to measure) shows
    the crossover variable is OFFSET, not LENGTH — hybrid's ns/call is flat
    in `n`, VM-only's grows with the naive retry loop's candidate-position
    count. A `n < RX_HYBRID_MIN` branch as designed would misfire on the
    ASK's own named target: bench case (i)'s actual buffer sits at offset
    20, past the measured 8-12-byte crossover, where hybrid is already 65%
    FASTER than VM-only (three-run reproducible) — a length threshold
    generous enough to "catch" case (i)'s 60-byte length would regress the
    exact case it exists to protect, and case (j)'s own pattern never
    crosses at all (hybrid wins from offset 0). Trie switch: a corpus
    survey (the same eligibility rule `nfa.c`'s trie_key() checks,
    approximated on pattern text) finds 22/1146 (1.92%) of all corpus
    patterns and 22/347 (6.34%) of capture-bearing ones are candidates, and
    NEITHER shipped capture-bearing bench shape (case j; case c's own
    alternation is pinned `--no-captures` and never reaches `vm_alt`) hits
    it; a direct branch-position measurement on two real disjoint
    alternations finds the chain's own cost real (+18% worst-vs-best branch
    on a 5-way word alternation) but narrow, declined on D18 ("an axis must
    earn itself") against the new emitter analysis's own build cost (a D46
    stamp+force pair, a permanent sabotage row — `src/opt/CLAUDE.md`'s
    established price for a selection axis). Both items' seams are left
    exactly as engine_m4.md designed them, unimplemented; three independent
    pinned runs (taskset, best-of-9) archived per D35 in
    `docs/design/m46e_impl/out/`, probes in `docs/design/m46e_impl/probes/`,
    engine_m4.md's ASK-6/§2.2 item 4/§6.4 carry the findings in place. No
    runtime match code touched — see the lane's own CLAUDE.md for the full
    validation-scope reasoning.
  - [M4.6f] STATE:completed (2026-08-17, lane m46f) — D46 CLOSE-OUT for
    the PREFILTER axis DONE: `<PREFIX>_VM_PREFILTER` stamp (`"hybrid"`/
    `"none"`, a SCALAR string like `RX_ENGINE`/`RX_VM_PRUNE_CEILING` —
    `fit.prefilter` is one verdict per artifact, not per-quantifier, so
    there is no mixed case for a bitmask to disambiguate) plus the
    `-fprefilter`/`-fno-prefilter` FORCE pair (`PCREC_FORCE_PREFILTER`/
    `PCREC_NO_PREFILTER`, `1u<<9`/`1u<<8`) in src/opt/select_engine.c,
    applied AFTER the derived default and do-or-die on the impossible
    direction only: `-fprefilter` REFUSES when `fit.chosen != ENGM_VM`
    (verified against explicit `--engine=dfa` and auto-routed-to-DFA via
    `--no-captures`), `-fno-prefilter` never refuses (`--engine=vm`
    already ships that configuration). A FORCE pair rather than D47.3's
    DENY-only shape — reported deviation, reasoned in src/opt/CLAUDE.md
    and lib/CLAUDE.md: the axis is artifact-level, so there is no
    per-quantifier addressing problem FORCE would create. Both new bits
    masked out of `rx_info.flags` (emit_dfa.c) alongside the four D47.3
    siblings. tests/prefilter/run_prefilter_tests.sh: 18 structural
    checks, no differential sibling (the prefilter's correctness already
    rides tests/vm's S3.7 differential and tests/mrl's ceiling coverage —
    this substep is observability+controllability only). Islands' own
    pair stays deferred to [ENG-ISL],
    which already records the obligation ("carries its own D46
    stamp+force obligation when built"). Battery: `make strict` clean;
    full `make -j12 -Otarget test` CONFIRMED GREEN — 10,257/0 corpus
    cases (exactly the expected count, unchanged), ratchet "nothing to
    ratchet", zero FAIL lines across every section including the new
    `test-prefilter` (18/18). Also added S64/S65 to tests/mech/sabotages/
    (the R28-1 convention: dev-time failing-direction checks must be
    PERMANENT sabotage rows, not ad-hoc and reverted) — both validated
    DETECTED via `bash tests/mech/run_sabotage_matrix.sh`. No sanitizer
    run: no runtime match code path changed, only selection (compile-time)
    and emitted stamp text — judged unnecessary per
    docs/testing.md's SAN-1 scope (a stamp is emitted text; the force
    flag touches selection, not the matcher body).

## 2026-08-17 (thirtieth session — [M4.7] opens; BENCH-VM lands)

- [BENCH-VM] STATE:completed (2026-08-17, thirtieth session, lane/benchvm; floors from 3x quiet-window pinned runs, manager gate verification 13/13 on merged main) — VM-TIER MINI-BENCH CASES (manager
  proposal accepted into the queue 2026-08-17, twenty-ninth session;
  a deliberately thin EARLY SLICE of [BENCH-1], not a replacement):
  three new compare.sh cases with floors, closing the gap that the
  bench's only VM case is (j): (k) an MRL dense shape (the
  `(a{10,20}){10,50}` class — a throughput floor watching that the
  K23 fix STAYS cheap; today only correctness-tier step cells watch
  it); (l) the +8% site-dense shape `([a-z]{2,4}){2,8}b` — a floor
  watching the D51-addendum's ACCEPTED cost (the
  deliberately-floored-sentinel posture that caught K24; today a
  drift to +20% would be invisible); (m) an offset-deep capture case
  flooring the hybrid's measured win regime (D53's crossover
  evidence, unrepresented today because case (i) is pinned
  --no-captures). Discipline per (j)'s precedent: three quiet-box
  pinned runs each, floors.tsv rows with D17 margins, per-case engine
  assertions, journal entry. ALSO RIDES: the counter-K K-sweep
  driver's median/spread upgrade (the INCONCLUSIVE verdict's stated
  prerequisite, docs/design/counterk_impl/bench_k.txt). Sonnet-sized,
  one lane.

- [OPT-ALTCLS] STATE:completed (2026-08-18, thirtieth session, altcls lane; stages 1+2 merged 621ffce, stage 3 measured-no per D54, row close merged de7cfa1) — ALTERNATION→CLASS NORMALIZATION
  (Frank, 2026-08-17, twenty-ninth session, from reading --emit-ir on
  `a(b|c)+d` vs `a([bc])+d`): an IR/AST pass merging maximal runs of
  ADJACENT single-character branches (1-char literal or class atoms:
  `b|c`→`[bc]`, `[ab]|[cd]`→`[abcd]`, `b|[cd]`→`[bcd]`) into one class
  node. SOUNDNESS: each merged branch consumes exactly one byte at the
  same position, so leftmost-first preference among them is
  indistinguishable — same match set, same span, same capture spans;
  preference relative to UNMERGED (multi-char) branches is preserved by
  merging only ADJACENT runs in place. MEASURED MOTIVATION (2026-08-17,
  the two exemplars above): the VM tier is the payoff — rung selection
  sees the class body and downgrades revdet→cursor: 23 labels/66
  events/3 frames/2 resume points → 4/18/1/0, emitted C 445→380 lines,
  and the cursor form is possessified span-scan (a fraction of the
  steps); the DFA tier gains a small byte-equivalence-class merge (b,c
  currently stay distinct classes when spelled as alternation — wider
  rx_ftr table). INTERACTIONS: shrinks the [M4.6e]/D53 trie-switch
  candidate pool by deleting mergeable alternations outright (better
  than dispatching over them); post-merge shapes re-enter possessify/
  MRL/counter analyses with class bodies, so the pass runs BEFORE
  those. Obligations at build: D46 stamp+force for the pass (it is a
  selection point), a permanent sabotage row, differential validation
  alternation-spelling vs class-spelling on identical subjects
  (match + all capture slots), and the survey question "what do PCRE2/
  RE2 normalize here" answered by MEASUREMENT not docs. Sonnet-sized;
  Frank schedules. THE GENERALIZATION LADDER (Frank probing for the
  larger algo, 2026-08-17, measured same conversation): per-position
  class merging of MULTI-char branches is UNSOUND — classes are
  position-independent, branches carry cross-position correlation
  (`frank|fred` → `fr[ae][nd]k?` accepts the cross-products fran/
  fredk/frad/fren: 4/6 probe mismatches vs python, verified). The
  correlation-preserving forms, cheap→general: (1) this row's
  single-char merge (no correlation exists); (2) PREFIX/SUFFIX
  FACTORING at the AST level (`frank|fred`→`fr(?:ank|ed)` — sound,
  branch-order-preserving, and the automatic pass must emit
  NON-CAPTURING groups or it changes the group count; the DFA engine
  has it via M2.8's trie, VM emission does NOT factor today —
  MEASURED WORTH IT 2026-08-17 (manager probe, Frank's exemplar
  `frank|fred|brad|bobby|janet` vs `fr(?:ank|ed)|b(?:rad|obby)|janet`,
  pinned best-of-9 ×3 runs): single-shot marginal (first branch +1-2%,
  late branches -5..-8%, no-match ±0.5% — the prefilter owns those),
  but the QUANTIFIED form `(...)+` over 30 concatenated names is
  -15.0..-15.6% reproducible — per-attempt savings amplify under
  repetition, the keyword-tokenizer shape. Stage 2 is therefore
  chartered WITH stage 1; probe was session-scratch, re-run under the
  row's own D35-archived instrument at build); (2b, STAGE 3 — Frank,
  same conversation, from the `(?=[a-f])(?:a|...|f)` idea):
  FIRST-SET ENTRY GUARDS — for an alternation of multi-char branches,
  emit ONE derived first-byte-set bitmap test (`frank|...|janet` →
  `[fbj]`) before the branch cascade. Needs NO lookahead module — the
  FIRST set is a compile-time fact the emitter plants like MRL plants
  its bound; note the all-single-char case is stage 1's territory
  (the class IS the whole match, no guard needed). Economics: saves
  the REJECT path (1 test vs N first-byte compares, grows with N),
  costs +1 test on the accept path — earns where reject-traffic × N
  is large, which the hybrid's prefilter TEMPERS (VM reject traffic
  is mostly once-per-loop-exit in quantified alternations): strictly
  measure-at-build. Generalizes past alternations (any choice point
  can carry its FIRST-set guard); DUALITY worth keeping: MRL is
  length-viability, FIRST sets are byte-viability — cheap
  necessary-condition guards whose everywhere-limit IS the DFA.
  PCRE2/RE2 both compute start-byte sets — survey by measurement.
  Adjacent: the unfiled required-byte prescan/skip OPT idea is this
  family's scan-side sibling. (3) full fragment DETERMINIZATION with
  direct automaton emission = [ENG-ISL] exactly (states encode the
  correlations; the overlap/preference subtlety — leftmost-FIRST vs
  DFA-longest on `foo|foobar` shapes — is the exactness proof that
  row already owns; the ladder 1→2→2b→3 is a lattice of PARTIAL
  DETERMINIZATIONS, each trading compile-time analysis and code size
  for run-time checks removed). DFA→regex re-spelling is rejected as a route
  (state-elimination blowup, loses preference); the automaton is the
  final form, not a rewritten pattern. Frank's shape class is itself
  candidate D50-gate evidence for [ENG-ISL] if bench/PGO shows it
  hot.

  **ROW CLOSE (2026-08-17/18, altcls lane).** Stage 1 (single-char merge)
  and stage 2 (prefix factoring) LANDED and MERGED to main: D46 stamp+force
  (`RX_ALTCLS_MERGES`/`RX_ALTCLS_FACTORED`, `-fno-altcls-merge`/
  `-fno-altcls-factor`), differential validation (38 designed + 78
  corpus-derived patterns, ~82k cells, 0 divergences), oracle-verified
  `.rxt` corpus, two permanent mech sabotages (S66/S67, both DETECTED).
  Landing also found and fixed a real regression the pass caused in
  `tests/codegen/run_trie_identity.sh`'s M2.8 trie positive controls
  (altcls pre-empted the exact bare-literal-prefix shape those controls
  were built from, vacuously; fixed by widening the controls' bytes to
  two-member classes — see `tests/codegen/CLAUDE.md`).

  **Stage 2's -15.0..-15.6% figure is SUPERSEDED.** The row's own D35
  pinned re-measurement (`docs/design/altcls_pinned_impl/`,
  best-of-9 x 3 interleaved rounds, mpstat-verified quiet box) measures
  **-7.61%** (n=27, stdev 0.226us on a ~47.2us mean, clean non-overlapping
  distributions against the unfactored arm) on the identical
  quantified-30-name-keyword shape. Direction CONFIRMED; magnitude
  superseded — the design-evening figure was session-scratch with its
  exact pattern/subject never archived, and is not further chased per
  ruling (a capture-placement variant moved the number to -9.6% without
  fully closing the gap; two untried variables — a `--engine=vm`
  reproduction, matching the original subject shape exactly — are
  recorded in the archive as the next step if this cell reopens).

  **Stage 3 (FIRST-set entry guards): MEASURED-NO, per D53's own posture
  — a full success outcome for the row, not a failure.** Implemented as a
  working prototype (`src/opt/firstset.c`, `src/gen/emit_vm.c`'s
  `vm_alt_guard`), correctness-validated (0 divergences over ~48k
  differential cells), then measured under the manager's decision frame:
  no cell under DEFAULT (real-caller) routing showed a benefit
  distinguishable from noise, including a purpose-built arm testing an
  alternation NOT at the pattern's start (weak prefilter selectivity) —
  the one shape structurally capable of showing default-path benefit
  given `select_engine.c`'s `fit.prefilter` derivation is unconditionally
  true whenever the VM is auto-selected (no pattern-shape-dependent path
  to false exists today outside explicit flags). The real ~11x win Cell B
  measures is confined to `--engine=vm`, a comparability/debug facility
  (DD-8/R21 E-6), which does not on its own justify a new selection axis
  plus the full D46 stamp+force+sabotage apparatus on the default path —
  `[m46e_impl]`'s trie-switch decline is the exact precedent this ruling
  follows. **Disposition: does NOT merge, not even denied-by-default** —
  a denied-by-default facility with no default-path customer still buys a
  permanent maintenance surface for nothing. The implementation survives
  in git history (worktree `lane/altcls` commit `a07a87c`, reverted at
  `8b5acb4`) and is re-derivable from `docs/design/altcls_pinned_impl/`'s
  archived record rather than kept live in the tree.

  REVISIT-WHEN (stage 3, also recorded in
  `docs/design/altcls_pinned_impl/CLAUDE.md` beside the evidence): (1)
  M6's VM-mandatory constructs (backrefs, lookaround) land — the
  capture-erased prefilter becomes an over-approximation for those
  patterns, raising VM cascade reject-traffic for a reason this session's
  shapes could not exercise; (2) `--engine=vm` ever becomes a supported
  deployment path rather than a comparability facility; (3)
  `[ENG-PGO]`/bench evidence surfaces real guard-eligible cascade traffic
  under the default engine.

## 2026-08-18 (thirty-first session — M4.7 CLOSES: the spec survives its panel)

- [M4.7] STATE:completed (2026-08-18, thirty-first session; merge d523a88) — **AUTHORIZED (Frank, 2026-08-17,
  twenty-ninth session close): open at next session start, alongside
  the [OPT-ALTCLS] and [BENCH-VM] lanes (3 lanes; [DD-13b] stays
  paused). Sequencing constraint recorded: [OPT-ALTCLS] merges BEFORE
  the at-scale differential run so any divergence attributes cleanly.
  EXPANDED 2026-08-17 (thirtieth session) into the substeps below;
  K9's API half and K7 HOMED here (rationale in each substep).** DIFFERENTIAL + CLOSE: capture differential
  vs libpcre2 ovectors (gate-ON per docs/testing.md's differential-gate
  principle), fuzzer extended to compare capture spans, SR-8's
  diagnostic flip lands (the VM now exists), full close battery +
  ratchets. M4-CALLOUTS step 2 stays a boonies row, NOT an M4 substep —
  the VM design must merely not preclude its call sites (F-obligations
  already frozen). ALSO (Frank, 2026-08-14, with D40): the AS-BUILT
  match-API contract graduates to docs/spec/ at this close — the first
  spec document (design = what we want to build, spec = what we DID
  build and becomes our contract; changeable but a deliberate
  deliverable). Authored from the shipped surface, referencing
  match_api_m4.md for reasoning per the spec charter; it is the natural
  enumeration D40's future v1 declaration points at. OWED AT THIS STEP
  (R22, 2026-08-15, recorded here 2026-08-16 so it survives wake.md
  rotation): the CONTRACT-TEXT WORDING PASS over match_api_m4.md §2.2 —
  the two gaps the blinded capture author found (cross-iteration
  retention; empty-final-iteration overwrite), arbitrated three-way
  unanimous and recorded as the §2.2 as-built addendum, get folded into
  the graduated spec text properly rather than living as an addendum
  - [M4.7d] STATE:completed (2026-08-17, lane/fuzzcap, merge 58717d3;
    manager positive control: sabotaged group-1 span detected 252/252,
    clean control 0/860 pairs) — FUZZER CAPTURE-SPAN EXTENSION: fuzz.py's
    content-divergence comparison extended from whole-match spans to
    ALL capture-group spans vs the PCRE2 ovector (unset groups
    included — the -1/-1 convention vs pcrec's contract per
    match_api_m4.md), generator extended to emit capture-bearing
    shapes at meaningful density. Prerequisite of [M4.7e]; independent
    of [OPT-ALTCLS], so it runs first-wave. Sonnet lane
  - [M4.7a] STATE:completed (2026-08-18, thirtieth session, lane/m47a,
    merged post-battery; rulings placed as D55) — SR-8 FLIP. Lane
    lane/m47a delivered for review 2026-08-17: `\1` etc. are still refused by the PARSER, and
    correctly so — re-reading every src/parse/ module file at this lane
    confirmed the row's own premise does not hold in code (no VM_ONLY
    registry row has a producer, so the parser's "requires module 'X'"
    was always a module-ENABLEMENT refusal, never an engine-capability
    one; there was no parser-side engine check to relocate). The lane's
    first pass built SR-8's consuming socket ahead of a producer
    (src/opt/select_engine.c + Ctx.vmonly_*); a manager REDIRECT
    (2026-08-17) reverted it — zero producers means zero customers
    (D18/OS-0/D53's standing discipline against unpopulated machinery),
    and a hand-built Ctx proving the socket works is a control sharing
    a source with what it controls. What landed instead is a TRIPWIRE:
    tests/registry/registry_check.c's check_engine_capability_tripwire
    asserts, over the real 51-row population, that every RS_MODULE row
    whose `engines` mask excludes ENGM_DFA has no wired atom-position
    producer — the fact that makes SR-8's silence safe today. Its
    failure message names the exact next step (build the consultation
    in select_engine.c) so the day a module wires the first VM_ONLY
    producer, this fails loudly instead of silently. Sabotage-validated
    (dummy producer on the atomic-groups row fires it + check_class_
    ports independently). Zero accept/reject verdicts changed; zero
    diagnostic wording changed. Awaiting manager review/merge. See
    [SR-8]'s own row for the charter-level disposition this discharges
  - [M4.7b] STATE:delivered (2026-08-18, lane/m47b; awaiting manager
    review/merge) — K7 FIX (homed here: the at-scale
    differential/fuzzer run stresses exactly the compile-side
    resource boundary K7 breaks, and M4.7 is the last stop before
    M5/M6 widen the surface): a large bounded repeat must reach the
    "too complex" diagnostic under bounded memory instead of 2-5 GB
    RSS / SIGKILL / aborting a limited caller's process; reconcile
    the two wrong docs/pcre2_compliance.md claims K7's entry records.
    Engine-core resource accounting — opus-tier lane.
    DELIVERED: K7's own diagnosis was WRONG about where the memory
    went, and that is the finding. The bounded-optional blowup was
    one line in src/ir/nfa.c — the `X{m,n}` tail loop rebuilt its
    out-patch set every iteration, Theta(n^2) arena traffic behind a
    linear STATE count, so no cap had anything to object to;
    inheriting the array instead (frag_cat2's existing idiom) takes
    `a{0,20000}` from 4.68 GB to 13.2 MB and makes BOTH caps K7 called
    unreachable fire in 0.1 s. A SECOND, separate quadratic in the
    exact-count form (`a{20000}`: 200M interned state-set elements,
    845 MB, 63 s, COMPILING) is bounded by the new
    PCREC_MAX_SUBSET_ELEMS. The caller-abort is closed by routing all
    seven malloc-failure sites through ctx_nomem(). NARROWING to note
    at review: exact repeats above ~`a{9800}` now refuse. New suite
    tests/resource/ (19 checks, `make test-resource`), sabotage-
    validated three ways; 572/572 corpus artifacts byte-identical.
    SPUN OUT as K25: `a{0,25000}`'s remaining ~15 s is a MEASURED
    15.3 s inside pcrec_minimize_dfa (Moore refinement, O(n) rounds
    on a chain) against 0.03 s for everything K7 bounds — bounded
    memory, terminates, out of this lane's scope
  - [M4.7c] STATE:completed (2026-08-17, lane/m47c, commits 3900eac/bb21274/
    069f943; awaiting manager review/merge) — K9 API HALF. FOUND ALREADY
    LANDED: `rx_info.pattern_len` (D44.5) shipped at [M4.4]'s match-API
    freeze on 2026-08-14 (`src/gen/emit_dfa.c`'s `emit_info_def`, off
    `cx->patlen` — the same `strlen()` at `pcrec_compile()`'s entry that
    decides what actually gets compiled), well before this substep was
    scoped 2026-08-17. What this lane supplied was the TESTING the row's
    own K9 repro needed and never had: `tests/cli/run_cli_tests.sh` case16
    (a direct library-API C probe — argv cannot carry an embedded NUL to
    `pcrec_compile()` — pinning K9's "a\0b" compiles as "a", reports
    success" and asserting the new detectability: `rx_info.pattern_len`
    honestly reads 1) and two `tests/codegen/run_codegen_tests.sh`
    structural cells (ordinary byte count for `'abc'`; `'a\nb'` stamps 4,
    the SOURCE spelling, not 3, the matched-byte count — the cell that
    would catch a field reporting the wrong one). test-codegen 41/41,
    test-cli 260/260, test-registry (incl. PC-4 62,872 cells) clean.
    Contract text: docs/design/match_api_m4.md §5's `rx_info` layout table
    already carries `pattern_len` at D44.5's own ruling — no further
    contract-text change needed; [M4.7f]'s spec graduation inherits it
    as-is. docs/dev/known_issues.md K9 gets a dated landed-note; K9 STAYS
    OPEN (the compile-entry length-parameter half is still DD-3's).
  - [M4.7e] STATE:not-started — AT-SCALE CAPTURE DIFFERENTIAL vs
    libpcre2 ovectors, gate-ON per docs/testing.md's differential-gate
    principle. SEQUENCED: starts only after [OPT-ALTCLS] merges (so
    divergences attribute cleanly) and [M4.7d] lands. D44 three-way
    posture where python re can arbitrate
  - [M4.7f] STATE:completed (2026-08-18, lane/m47f, merged ccfa3a3
    after manager read + green suite) — SPEC GRADUATION. `docs/spec/match_api.md`
    authored: the entry-point set, the six fixed-literal ABI types,
    capture-slot semantics (C1-C11 restated as contract prose with the
    R22 §2.2 rules — cross-iteration retention, empty-final-iteration
    overwrite — folded in as first-class text, not an addendum), the
    D49 give-up code space, the rx_info reflection structure plus its
    D46 compile-time observability-macro mirror, the COMPILE-ENTRY
    NUL-termination contract, and pcrec_options/pcrec_error. Every
    claim checked against the shipped surface (lib/pcrec.h, artifacts
    actually emitted for --no-captures/captures-default/custom-prefix
    builds, cited tests) rather than copied from match_api_m4.md,
    which had DRIFTED in two places — both corrected in the spec, not
    silently reconciled: §3 there still shows D42.3's give-up-code
    `-1` collapse, superseded by D49 before this graduation (the
    shipped rx_match propagates give-up codes uniformly — verified in
    the emitted C, which even carries a comment explaining why); and
    §5's rx_info layout sketch shows a bare typedef where the shipped
    artifact emits a struct TAG ONLY (`struct rx_info` — forced by the
    default-prefix `<prefix>_info` name collision, recorded as an
    as-built deviation at [M4.4] and still an open Frank ruling,
    unchanged by this lane). The COMPILE-ENTRY contract (patterns are
    NUL-terminated; a raw 0x00 truncates the compile) is stated with
    an INDEPENDENTLY MEASURED comparison, not merely cited from this
    row's own text: dlopen'd libpcre2 10.46 via tests/fuzz/pcre2_abi.h,
    confirming PCRE2_ZERO_TERMINATED truncates the 3-byte {'a',0,'b'}
    buffer identically (matches only "a"), while explicit length=3
    compiles and matches the real 3-byte pattern — an API-surface gap
    relative to PCRE2's length-taking mode, not a semantics
    divergence; full length-taking support stays DD-3's (K9), trigger
    customer [V-A]'s (pattern,length) compat shim; rx_info.pattern_len
    is the named detectability instrument (K9 pins: tests/cli case16).
    docs/spec/CLAUDE.md gets its first real entry; docs/CLAUDE.md's
    spec/ line updated; match_api_m4.md gets a graduation pointer at
    the top naming both discrepancies. Commits: c24d699 (spec content),
    4adb10f (plan/journal), lane/m47f.
  - [M4.7g] STATE:completed (2026-08-18, thirty-first session; R29 panel + fix merge d523a88; post-merge suite 10,369/0 + strict; battery test/strict/ubsan/asan/lint all exit 0; gate 13/13) — CLOSE:
    D6 critic panel over docs/spec/match_api.md (rides this close per
    the 2026-08-18 journal entry; 3 read-only critics, findings to
    docs/dev/reviews/), full close battery + ratchets, bench gate on a
    quiet box after the battery; M5-vs-M6 order RULED BY FRANK at this
    close: **M6 FIRST** (assertions/lookaround/backrefs/named-groups
    surface before the UTF-8 encoding axis; [M6.0] expands on arrival
    next session, carrying its D47.5 possessification-gate
    obligation). rx_info struct-tag spelling BLESSED (D57) — spec note
    update rides the panel fix pass. Push to origin done at session
    start (Frank's call, 860dcb6..1a933a2).

## 2026-08-18 (thirty-second session — [M5-SEAM]: the encoding seam prelude lands)

- [M5-SEAM] STATE:completed — THE ENCODING SEAM PRELUDE (D58, Frank,
  2026-08-18, thirty-second session: built BEFORE M6 so M6's
  encoding-sensitive residue is born on the seam, not retrofitted).
  Scope: (a) encoding as a PER-PATTERN generation scalar —
  pcrec_options field + CLI `--encoding=byte|utf8`, byte the default,
  utf8 CLEANLY REFUSED until M5 proper (never process- or file-global;
  mixed encodings in one compilation unit are supported by
  construction); (b) the DD-12 residual-header embed mechanism, byte
  backend only — each artifact embeds exactly one encoding's residual
  block; (c) `<prefix>_next_pos` as the first pulled residual entry:
  spec §3.1's find-all loop moves onto it (resolving that section's
  recorded byte-vs-character caveat), §8.0's worked example updated
  compile-and-run, emitted ABI comment + lib/pcrec.h updated under the
  R29 verbatim-quote discipline; (d) codegen structural check that
  residual entries are never called from hot-loop labels (allowlist
  shape per DD-12 (7)), sabotage-validated; (e) riders: the K27 fix
  (this IS the emitter-touching wave known_issues.md scheduled it for)
  and the stale D56 "VM engine arrives in M4" diagnostic text. NOT in
  scope: UTF-8 lowering, \p{...}, DD-1 folding — those stay [M5.0].
  [M6.0] expands only after this row lands.
  COMPLETION NOTE (2026-08-18): landed as merge e70f71c (lane/m5seam,
  opus, 10 WIP commits, single session same day as ruled). As-built
  deltas from the row text: the options field and `-e` ALREADY EXISTED
  spelled PCREC_ENC_ASCII / `-e ascii` — RENAMED to PCREC_ENC_BYTE
  with NO alias (pre-v1 announced boundary, spec §9 posture; "ASCII"
  was false about 8-bit-clean byte semantics, and D58 names the
  encoding `byte`; manager-accepted, Frank-notified). Layout:
  src/gen/enc/ {enc.h seam interface, enc.c registry, enc_byte.c};
  backends are TEXT with `$`-prefix substitution; utf8 exists as a
  NULL-backend registry row so the refusal reads the row's own name
  (closes [SR-10]'s motivating instance — compile.c and cli both
  resolve names through the registry now). next_pos is EXTERN like the
  other four entry points; contract: smallest boundary strictly greater
  than pos, every position >= n counts as a boundary, reads s only in
  [pos, n). Spec gains §3.1.1; find-all re-verified 26 pairs x 2
  engines = 52 runs vs re.finditer, lossy class subset-checked BOTH
  directions, graduated from transcript to suite (tests/encseam/, in
  make test). New checks: S68 sabotage (hot-loop residual call — a
  sabotage that changes NO answer, only the structural check sees it;
  codegen 3fail/44pass red arm, corpus 0fail control) and ABI-block
  cross-prefix byte-identity (4 prefixes, whole-file control). K27
  CLOSED (guard `if (pos >= n) return 0;` on the non-EOL memchr arm
  only; UBSan-verified in both directions; regression rides the ubsan
  battery). Suite 10,369/0 (verified independently by the manager
  pre-merge), cli 260→269, codegen 41→44; post-merge battery all five
  stages green; bench gate 13/13, case (c) at historical spread
  (391.366 MB/s — the K27 guard cost nothing measurable). Check-design
  find for the ledger: TWO suites (trie-identity, thread) assembled
  reference builds from one-level source globs and broke loudly on
  src/gen/enc/ nesting — the failure shape is the silent one; both now
  `find` sources and hard-fail on an empty list.

## 2026-08-18 (thirty-third session — [M6.3]: module named-groups lands)

- [M6.3] STATE:completed — module `named-groups`: the three declaring spellings (?<n>...) (?'n'...) (?P<n>...) parse and capture as their group number (including the measured (?n) divergence — a named group captures even under no-auto-capture); name grammar [A-Za-z_][A-Za-z0-9_]{0,127}, case-sensitive, measured against libpcre2 10.46 (the 128-unit wall measured by TWO independent probes — manager ctypes sweep and the lane's tests/probes/probe_named_groups.c — refuting the stale documented 32); duplicates refused; `rx_info.groups` populated sorted-by-name (strcmp, matching PCRE2's own measured NAMETABLE order) with `nnames` counting it, NO ABI change (the slot was anticipated); the sort key FIXED scoped to ref-empty rows (D59; the compound (ref,name) ordering deliberately left to the first ref producer) and spec §6's long-open paragraph resolved with verbatim re-quotes in both engine directions (VM slot=live, DFA slot=-1). Three registry rows reclassified VM_ONLY→ANY_ENGINE instead of building SR-8 (D59 part 2 — the construct's AST is an ordinary A_CAP; the generic capture-forcing rule already routes it). Boundaries proven both ways: \k<n>/(?P=n) still refuse with `backrefs`, (?J) refuses with the ratified-D38-consistent known-but-unbuilt wording ("module 'named-groups' does not implement duplicate group names"). D27 blinded acceptance corpus (ngauthor cell, 41 blocks / 83 harness cases) ran 83/0 against the implementation at merge review — author and implementation converged on the measured oracle with neither seeing the other. Suite 10,418/0 pre-corpus-merge (+49 over baseline), cli 269/0, registry+PC-3 163/0, reject 532/0 (four new gated boundary pins), spec_mod0 14/14. Merges: implementation + corpus, 2026-08-18.

## 2026-08-18 (thirty-third session — [M6.1]: the assertions design survives R30)

- [M6.1] STATE:completed — module `assertions` DESIGN GATE (design before code — this is the engine-touching substep). Produce docs/design/assertions_design.md answering, per construct (\b \B \A \z \Z (?m)^$ \G \K): (i) ENGINE SPLIT — which are DFA-representable as state context (DD-6's territory: last-byte-class context states for \b/\B, multiline ^/$ variants; cost vs the state budget, measured not asserted), which force the VM, which both engines carry; (ii) DD-4 — \G vs startpos semantics (note engine_m4.md §7.3: `nfa_wrap_unanchored` bakes in the self-loop with no toggle, confirmed STRUCTURAL); (iii) DD-11 — which newline convention (?m) and \Z bind to, and where that axis is declared; (iv) \K vs the match-start reporting contract and the DFA reverse pass; (v) D58 RESIDUE ENUMERATION — name each construct's encoding-sensitive residue and the seam entry it routes through (word-char classification is a CHARACTER question; \G's advance; nothing lands as raw byte arithmetic); (vi) the D47.5 gate design for (?m); (vii) module gating — all constructs under module `assertions`, partial-enable behavior. D6 adversarial panel on the design BEFORE implementation starts. **DESIGN DELIVERED 2026-08-18 and REVISED after the R30 panel (docs/dev/reviews/2026-08-18-r30-assertions-design.md): docs/design/assertions_design.md + docs/design/assertions_measurements/ (9 probes + archiver, outputs archived with stamped provenance). A FOCUSED RE-CHECK of the revised sections gates [M6.2].** R30 verdict: the FOUNDATIONS survived adversarial re-derivation on the critics' own instruments — D47.5 confirmed twice independently and called the single best-supported claim in the document; \A/\Z alias 1,008 cells / 0 disagreements; \G's mechanism structurally verified; the \Z oracle divergence reproduced; the mods blast radius confirmed; all six probes reproducing — but the ENGINE-SPLIT half took TWO HIGH refutations and six mediums, all now fixed in lane. E1: the spine had NO MECHANISM AT ALL for assertion context at startpos>0 — \b/\B/(?m)^ read s[startpos-1] and a trailing \b reads s[end], bytes outside the search window, while both engines emit their start states as compile-time constants (emit_dfa.c:946/:1029); a FOURTH mechanism (runtime start-state seeding, forward and reverse) is now §3.8, measured at 5 of 10 differing cells with a LOST match through the find-all loop. E2: (?m)^ does not 'inherit D8's shape' — it can never take the start_max=0 fast path, so it is a permanent move into a MEASURED O(n^2) class (3.99x per doubling, 1996x slower than the anchored twin at n=64,000); the memchr('\n') candidate-start prefilter is adopted as a design element and Q3 is reframed, with the DD-7 unpark now a Frank ruling. Mediums: E3 \z's byte-identity canonicalized against the wrong reference (three-way rule now; Wave A's own check would have caught it); E4 §3.4 and §3.5 were never composed and composed they EXCEED the state cap (38,009 vs 32,000) plus §3.4's corpus silently excluded every ENG_ATTEMPT pattern; E5 the skip hazard was misattributed to \b (whose accept is CONSTANT across a skipped run by the doc's own state-identity argument), so Wave B's sabotage could not fire on any pattern Wave B lands — cure and sabotage move to Wave C, and all FIVE scan-avoidance mechanisms are now enumerated with individual fates (memchr is un-intersectable; start_acc must widen); E6 the zero-cost accept measurement is ENG_UNANCH-only and had no pos==n column (composition rule now written: at pos==n the accept is the view's SCALAR, never class-indexed); E7 \K 'structurally cannot' overstated — leftmost-first is a total order and tagged DFAs recover such positions, so the door is recorded as closed BY CHOICE (conclusion unchanged); E8 §9.3's match-here paragraph was FACTUALLY WRONG (the DFA's rx_match IS rx_search plus a start filter), which withdrew Wave D's owed differential and exposed a live \K hazard — the filter rejects genuine anchored matches and the returned length is the post-\K length a D38 callout would advance by. THREE PROVENANCE FINDINGS ARE THIS LANE'S OWN FAILURES: M7, a header HAND-WRITTEN to imitate the archiver ('worse than absent provenance' — a reader cannot tell stamped from asserted without git archaeology; the rule is now written down: archive.sh is the ONLY writer of out/); M6, the locale-collation sort -u undercount reproduced VERBATIM after reading the R24 M-F1 entry that named and fixed it (true population 1030, the defect reports 609, 421 patterns SILENTLY MERGED — now committed tooling with LC_ALL=C, and every headline number is IDENTICAL on the corrected 962/1030 corpus); M8, the -Wswitch experiment unverifiable by a read-only critic (now a self-restoring instrument, 15 warnings / 6 files). M2: the state prototype has a SECOND fidelity gap running opposite the first — it minimises a LANGUAGE where pcrec tracks thread PRIORITY — so \w{3,16}'s 4.50x was an artifact (real ratio ~1.06x) and the '>2x: 2 patterns' line drops to one, while the 4.75x HEADLINE SURVIVES on (?:ab){1,8}c, whose prototype baseline is verified against pcrec exactly. M5: Q1's D18 exemption argument is REFUTED (D23 ran earn-its-axis on case-folding, a SEMANTIC dimension, and it failed into the parser), so Q1 now asks for the fold-first test rather than an exemption. FOCUSED RE-CHECK (both critics resumed): 7 of 8 engine discharges and 5 of 6 measurement ones HELD; the final batch closed N1 plus seven smaller items. N1 IS A SECOND DEFECT AND THE SHARPEST RESULT OF THE ROUND: §3.8 filled mechanism 4 at three of the FOUR places it is needed, and the missing one is the REVERSE machine's TERMINATION boundary -- at pp == startpos the loop breaks (emit_dfa.c:1056) before s[startpos-1] is read, so a LEADING \B evaluates blind and, on the doc's own cell (\Bfoo/'xfoo'/startpos 1 -> (1,4)), the forward pass finds the match and the reverse pass THROWS IT AWAY. \b is safe BY ACCIDENT (its blind assumption coincides with its truth condition), so a \b-only or trailing-only sweep reports clean against a design that loses matches -- and the lane's own forward fix is what made the reverse defect reachable. Fixed as §3.8.3.1 with an INVARIANT covering every sfound writer (the reverse skip's own write included), a peeled epilogue so the cost is zero per byte, §12 item 6 naming both ends, and a Wave B landing condition that sweeps \B-LEADING patterns at startpos>0. Also closed: M5 propagation (§5.2 still carried the withdrawn declare-the-namespace recommendation verbatim -- a live contradiction with §11 Q1), N2 (§3.7.1's table came from a different run than the archive it cited -- re-pasted from a genuine archive.sh run), N3 (the memchr('\n') mitigation was justified on the QUADRATIC arm when its benefit is the LINEAR non-crossing case; a non-crossing arm added to the probe measures 85-185x and Q3(b) is re-grounded on it), and N4-N8 (a 'three mechanisms' line over a four-row table, Wave D's agreement test unscoped -- partial \G legitimately disagrees, §6.1's heading contradicting its own retracting body, two orphaned paragraphs, and mechanism-table cite drift plus the fbound row's absence now explained). N1 VERIFIED AND CLOSED by focused re-check, which found N9 IN THE FIX: the reverse loop has TWO exits and the first wording of §3.8.3.1's peeled epilogue would have run on the DEAD-STATE exit (emit_dfa.c:1059) -- writing sfound at a position the walk never reached AND indexing an accept table with a negative state, K27's out-of-bounds class in EMITTED code; the accept is now attached to the boundary break itself so both are unreachable by construction. Same pass: the :1044 rendering sharpened (the emitter's `if` is COMPILE-time, so the artifact carries a bare UNCONDITIONAL `sfound = pp;` inside the skip block), the reverse boundary table counted in the budget section (states x (ncls+1), the +1 being the RX_CLS_BOT sentinel), ENG_ATTEMPT's n+1 initializations cross-referenced to §3.7, the A/B ratio column marked noise-dominated with cross-run evidence (n=32,000 moved 1001x->409x on B's jitter alone, so GROWTH is the load-bearing column), and TWO INSTRUMENT NEAR-MISSES promoted into prose because each would have produced a quotable number -- an all-'a' subject that measures the (?m)^ curve as FLAT and would have confirmed the struck sentence, and gcc -O2 deleting a repeat loop so a memchr arm read 0.000000 over 200 searches (the more dangerous of the two: an infinite ratio reads as a STRONGER result for the mitigation it supports). Also flags that eng_brep_design.md §2.5's cited 0/720 and 180/720 are STALE: re-running that section's own probe gives 0 of 168 and 12 of 168 on the greedy population, same qualitative result, both oracles agreeing

## 2026-08-18 (thirty-third session — [ABI-NS]: the constant namespace unifies)

- [ABI-NS] STATE:completed — UNIFY the emitted universal-constant namespace (D60 + addendum, Frank 2026-08-18): every emitted macro whose value is artifact-independent (ERR_STEPS/FRAMES/WORK/FLOOR, UNSET, the D46 stamp BIT constants, and PCREC_ENGINE_DFA/PCREC_ENGINE_VM naming rx_info.engine's currently number-only contract — spec §6 says "no such constant is #defined anywhere", the addendum closes that) moves to one canonical PCREC_* spelling in the prefix-independent ABI block; the per-prefix spellings are DELETED, no aliases (house precedent: PCREC_ENC_BYTE, D44.2). Per-artifact-valued macros (NCAPS, budgets, stamp MASKS, prefilter/ceiling stamps) stay prefixed — the membership rule is intensional, the lane enumerates by grepping the emitter. Travels with: spec §4/§5 verbatim re-quotes, codegen/stamp pin updates, ABI-block identity re-baseline. SEQUENCING: small standalone lane BEFORE [M6.2]'s first implementation wave lands (wave authors write PCREC_* from birth); NOT part of [M6-READ] (its charter forbids ABI changes); [OS-0]'s future rx_searchfn typedef is a separate later addition to the same block COMPLETED 2026-08-18 (thirty-third session): 15-member set landed in the ABI block, old spellings deleted and pinned-absent; the lib/pcrec.h PCREC_ENGINE_* collision found and resolved as request/outcome vocabulary unification with a permanent both-orders check; 8 extraction sites moved to the .h and hard-fail on empty (silent-zero class closed); spec re-quoted; suite 10,501/0 bit-for-bit baseline, 4 differentials 0-diverged

## 2026-08-21

- [M6.2] STATE:completed (CLOSED 2026-08-21, thirty-fifth session: D27 blinded corpus merged 68998b9 — 145 blocks / 224 oracle-verified cells / 242 harness cases, ZERO divergences vs the shipped module, the acceptance result; close battery all-green on the final state, test 20,775/0, gate 13/13 archived a610967; the (?m) two-module gating shape, the flags-i/options=0 finding and the verify_pcre2.py flags-skip guard are the corpus's returned findings. POST-MODULE QUEUE re-homed to [M6.0] at close. Original row text preserved below.) (ALL FIVE WAVES + THE REPAIR SLICE MERGED AND
  CLOSE-VALIDATED as of 2026-08-19 ~17:15 EDT, thirty-fourth session —
  merges e609a8c/b8b14dd/2737c61/307fe6c/84f5b1e/6da4ba5, each wave's
  battery all-green + gate 13/13 archived; module `assertions` is
  CONSTRUCT-COMPLETE 8/8 and K28 is CLOSED. THE SOLE REMAINING CLOSE
  ITEM IS THE D27 BLINDED CORPUS, deferred to the next session on
  Frank's token-ceiling stop order — it is the FIRST work of that
  session, on this row's final bytes, then this row goes completed.
  POST-MODULE QUEUE recorded here from the waves' returned findings:
  DD-7's reverse BOT variant (D63); D63's SECOND instance
  (first-byte-at-offset-0, the measured 83x partial-anchor gap);
  SEVEN pre-existing drifted sabotage anchors
  (S08/S09/S21/S22/S26/S39/S65 — audit method in tests/mech/CLAUDE.md);
  a registry BUILT-STATUS field (the repair slice's item-3 refutation
  names it as the real fix); wordb.rxt shard-split + PROCS tiering;
  SR-8's second-construct trigger; heavy differentials on the sanitizer
  lists.) — module `assertions` IMPLEMENTATION, in the five-wave structure [M6.1]'s design fixed (RULINGS LANDED 2026-08-18: Q8→D62 flag+controls, Q3→D63 prefilter-as-tool then DD-7, Q1→D64 no axis/definition-shaped sites; blocked now ONLY on [ABI-NS] landing before wave A per D60, then waves A→E). D47.5's possessification-gate test lands WITH the multiline wave — a `(?m)` pattern whose `$`-follow bounded quantifier must NOT possessify, INCLUDING the SCOPED cells D47.5's own wording does not ask for (`(?m:a{0,4}$)`, `(?m)...(?-m)` — the R30-confirmed miscompile rows; the parse-time-resolution cure per the design §8; Q8 RULED (D62): a FLAG on the node, with the three controls — scoped cells, permanent sabotage row on the reader, Ast field-comment obligation). Re-measured figures (2026-08-18, both oracles, archived assertions_measurements/out/dollar_multiline_rerun.txt): 0/168 diverging multiline-off and 12/168 multiline-on on the greedy population the exemption is about — the 180/720 previously cited here came from a since-changed probe population; qualitative claim unchanged. Wave briefs must state the corpus is substantially libpcre2-dependent (python lacks \Z agreement, bare (?-m), trailing (?m), \K). D27 blinded corpus for the module rides the close.
  **WAVE A LANDED 2026-08-19 (lane/asrtwavea)**: `\A`->A_BOL and `\Z`->A_EOL
  as exact aliases (no engine work); `\z` as a new `A_END`/`N_END` kind with
  the third closure view and §3.3's CORRECTED three-way canonicalization
  (`endvar` against the EOL view, not the base — R30 E3), gated by
  tests/codegen/run_endvar_identity.sh at 1011/1011 `\z`-free corpus patterns
  byte-identical with sabotage S69 as its failing direction; the D47.5 cure
  per D62 (multiline resolved at parse onto `Ast.multiline`, possessify reads
  the NODE, `ParseMods` moved behind an incomplete type so a post-parse read
  is a COMPILE ERROR — §8.6 made structural); `--features assertions` with
  §9.2's enabled-but-unbuilt refusal naming the CONSTRUCT (sabotage S70); VM
  arms for all three. Tests: tests/assertions/ (948 cases, libpcre2-verified
  by its own verify_pcre2.py — python's `\Z` IS PCRE2's `\z`, U11).
  **STILL OWED, and deliberately NOT faked early: D62's controls 1 and 2**
  (the widened scoped `(?m:...)`/`(?m)...(?-m)` cells and the permanent
  flag-reader sabotage) land in WAVE C, where the flag can be true and those
  rows can go red; with `(?m)` still refused they would be checks with no
  failing direction
  **WAVE B LANDED 2026-08-19 (lane/asrtwaveb)**: `\b`/`\B` as `A_WORDB`/
  `A_NWORDB` + `N_WORDB`/`N_NWORDB`, the module's first CONTEXT assertions and
  its only real engine work. §3.4's alphabet refinement by
  `pcrec_cls_word_esc` (ONE spelling, shared with `\w`); §3.5's context bit in
  the state identity as a SECOND CLOSURE per state (`DState.wlist`) rather
  than an interned variant, so the transition row for a class is built from
  the closure that class's word-ness selects and the emitted hot path stays a
  single table read; §3.6's class-indexed accept emitted ONLY where a state's
  accept actually varies with the next byte; §3.6.2's composition rule (scalar
  accept at `pos == n`, class-indexed below it); **mechanism 4 at all FOUR
  boundaries** (§3.8) — forward init from `s[startpos-1]`, reverse init from
  `s[end]`, reverse TERMINATION from `s[startpos-1]` attached to the boundary
  break per R30 N9, and the forward terminal's scalar rule — via `Dfa.s1w` and
  emitted `fseed`/`rseed` class->start tables; §9.3's guarded VM arms on the
  shared class pool. Both engines: ENG_ATTEMPT gets the same accept split and
  a per-attempt `seed[]` label table.
  EVIDENCE: 30,386-cell libpcre2 differential at 0 divergences across FOUR
  arms kept apart because they fail on disjoint populations (general,
  reverse-INIT via trailing assertions, reverse-TERM via LEADING `\B` at
  `startpos > 0`, and the §3.1 find-all loop with mid-word resumes);
  tests/assertions/wordb.rxt 4,392 cases, every expectation libpcre2-produced
  (including a capture-bearing VM section whose ABSENCE was measured — see
  the deviations below);
  tests/codegen/run_wordctx_identity.sh 1039/1039 `\b`-free corpus patterns
  byte-identical against a `-DPCREC_NO_WORDCTX` reference with 47 controls
  differing; three [M6.2-WORDB] structural rules in
  tests/codegen/run_codegen_tests.sh; sabotages S71-S74.
  **THE COMPOSED BUDGET IS MEASURED AND §3.5.1's FORECAST IS REFUTED AS AN
  OBSERVATION** (it stands as a bound). Measured on the built compiler
  (docs/design/assertions_measurements/out/wordctx_budget.txt): state ratio
  min/median/max **0.67x / 1.10x / 4.75x** — the max reproduces §3.5's
  headline exactly against a pcrec-verified base, and the MIN goes BELOW 1
  (`[01]*1[01]{8}` is 768 states bare and 513 with the context, a shape the
  prototype could not express). Alphabet delta +0/+1/+1, inside §3.4's
  predicted 0/+1/+2, which `probe_ncls_refine.py` re-confirms on the grown
  corpus (965 patterns; word 0/1/2, largest `states x ncls` 48,012, unmoved).
  The refusal boundary is LOCATED, not predicted, and on §3.5.1's OWN worst
  family the word context RAISES the ceiling — `((a)|ab){N}c` refuses at
  N=5655 (subset-elems) while `\b((a)|ab){N}c\b` compiles to N=15998 (31,999
  states), because a leading `\b` prunes start positions and moves the binding
  constraint. ENG_ATTEMPT's boundary is IDENTICAL with and without the
  context (N=4999, 10,000 states). The genuine regression is ONE repeat count
  wide, on a linear chain: `[a-z]{1,31999}` compiles at exactly 32,000 states
  and `\b[a-z]{1,31999}\b` refuses — cleanly, with the states-cap diagnostic,
  which tests/assertions/run_assertions_tests.sh pins on both engines.
  **DEVIATIONS AND FINDINGS RETURNED**: (1) §3.6.1's argument that `\b` cannot
  suffer the D11 skip hazard does NOT hold — "a skip set is a union of classes
  so every byte in the run has the same next-is-word value" is false, since a
  union of classes may contain both word and non-word classes; wave B declines
  instead (a state whose accept varies by class is not skip-eligible), which
  costs nothing on any pre-wave pattern. (2) A PRE-EXISTING defect, reproduced
  on the merge base c23662e with the base-tier pattern `^a^b`: an anchored
  pattern whose DFA is one dead state emits C that fails `-Wall -Wextra
  -Werror` (gcc reports the `<prefix>_match` wrapper's `caps` array
  maybe-uninitialized after inlining the always-returns-0 search). `^\Bfoo`,
  `^\Bo` and `^a\bb` are three new spellings that reach it; they are named
  and excluded in wordb.rxt's own header with live equivalents in their place,
  NOT fixed here — the fix touches every artifact in the tree. (3) The
  enabled-but-unbuilt reject rows for `\b`/`\B` RETIRE (gated 66 -> 64) and
  their compile controls move to run_assertions_tests.sh in the same change.
  (4) TWO OF THE WAVE'S OWN CHECKS WERE MEASURED VACUOUS BY RUNNING THEIR
  SABOTAGES, and both are recorded rather than quietly repaired. S72 came back
  UNDETECTED because the blind `sfound` writer it restores is gated by a
  compile-time condition with TWO conjuncts and the fixture's reverse skip
  state did not accept — the fixture moved to `.*\b.*` and the rule now
  ASSERTS `rx_racc[K] == 1` off the artifact. S75 came back UNDETECTED for two
  independent reasons: the substituted set is a contiguous RANGE so it emits
  no table (the rule counted tables; it now counts distinct normalised
  MEMBERSHIP TESTS), and every block in wordb.rxt was capture-free so nothing
  in the corpus reached `emit_vm.c`'s arm at all (the file gained its VM
  section in the same change). Both now fire; S71/S73/S74 were DETECTED on
  their first run, S74 on BOTH its instruments — 215 corpus cases, every one
  a leading-`\B` at `startpos > 0` losing its match, and codegen rule 2b.
  Final matrix: S71 wordctxid 1fail/3pass + corpus 0fail/15202pass; S72
  codegen 1fail/51pass + corpus 0fail/4392pass; S73 codegen 1fail/51pass +
  corpus 0fail/3528pass; S74 corpus 215fail/4177pass + asrt 0fail/26pass;
  S75 codegen 1fail/51pass + corpus 131fail/4261pass. Three of the five are
  SEMANTICS-PRESERVING (0 corpus failures), which is the standing argument
  for landing construction checks the prose says cannot fail.
  SUITE (final, this lane): corpus 16,066/0, cli 269/0, reject 537/0,
  registry 169/0 + PC-3 163/0, codegen 52/0, trie 7/0, vm-identity 9/0,
  ir-listing 79/0, vm 35/0, possessify 18/0, rungselect 24/0, counterk
  23/0, mrl 22/0 + 18/0, altcls 15/0, assertions 26/0, endvar-identity
  3/0, wordctx-identity 3/0; `make strict` clean.
  **WAVE C LANDED 2026-08-19 (lane/asrtwavec)**: `(?m)`, the wave four
  separate rulings travel on. The `m` letter is ACCEPTED
  (src/parse/mod_modifiers.c; both its wave-A refusals retire with it) and
  `^`/`$` copy the SCOPED state onto the node at the assertion itself, which
  wave A had already built — so `(?m:...)`, `(?m)...(?-m)` and a mid-pattern
  `(?m)` are right BY CONSTRUCTION rather than by a downstream pass
  re-deriving scope.
  ENGINE: `(?m)` adds NO new mechanism — it adds a second PROPERTY to the two
  axes wave B built, so the class axis stops being a bool and becomes the
  three-valued `UPC_{PLAIN,WORD,NL}` partition of the alphabet (disjoint and
  exhaustive: a newline is not a word character). `DState.up[UPC_N]` replaces
  `list`/`accept` + `wlist`/`waccept`; `Dfa.s1u[UPC_N]` replaces `s1`/`s1w`;
  the alphabet refines by `pcrec_cls_newline` (D64's ONE definition, the table
  `\N` compiles from) when and only when the machine carries an
  N_BOT_M/N_EOL_M. `(?m)$` stays on ENG_UNANCH; `(?m)^` routes to ENG_ATTEMPT
  via an extended `nfa_has_bot` and the seeded start dispatch.
  **DIRECTION APPEARS IN EXACTLY ONE PLACE, and wave B genuinely did not need
  it**: `\b` is SYMMETRIC in its two operands so a machine reading them
  backwards gets the same answer, while `(?m)$` reads ONE side — forward the
  byte about to be consumed, reverse the one already consumed. The closure now
  names its operands by SIDE (`left_*`/`right_*`) and `make_state`'s
  `sides_of` is the only function that knows a machine has a direction;
  `pcrec_build_dfa` takes `reverse` explicitly rather than deriving it from
  `prune` (they coincide under D7, and a coincidence load-bearing for
  correctness is what this project keeps recording).
  D63's CANDIDATE-START PREFILTER lands as a TOOL per its charter: the
  DERIVATION (`CandSet`/`cand_derive`/`cand_emit_table`) is ONE site with two
  callers — ENG_UNANCH's `cand_from_escapes` and ENG_ATTEMPT's
  `cand_from_live_seeds` — and the `(?m)^` predecessor-byte twist is a FIELD
  (`offset`), not a fork. `pcrec_emit_prologue` calls the SAME predicate to
  decide about `#include <string.h>`.
  D62's controls 1-3 all land: the widened scoped cells, the PERMANENT
  flag-reader sabotage S77, and the field-comment obligation — the last
  discharged by INSPECTING all four `default:`-carrying `Ast.k` switches
  (§8.3's stated landing condition) and recording the rule that generalizes:
  an analysis is at risk exactly when it treats `$` as TRANSPARENT, and all
  four treat it as OPAQUE (decline, widen, unreachable). possessify was the
  tree's one transparent consumer.
  **THE DESIGN'S `(?m)^` RULE IS WRONG AND SHIPPED WRONG FIRST — this wave's
  sharpest finding.** §3.7 and §9.3 both give `(?m)^` as "`pos == 0` or
  `s[pos-1] == '\n'`"; PCRE2's multiline `^` "does not match after a newline
  that ENDS the string", so `(?m)^` is NOT the mirror of `(?m)$` (on `"a\n"`
  the first holds at 0 only, the second at 1 AND 2). pcrec implemented the
  design's rule and was WRONG for it. **python3 `re` implements the design's
  rule too**, which is why no oracle in the base tier could see it — filed as
  upstream_issues.md U11b, and every `(?m)`-with-`^` corpus block is now
  `# pcre2-only` on the same WHOLESALE rule `\Z` blocks follow. Found by
  tests/assertions/run_mline_diff.sh at `startpos > 0`, because from
  `startpos 0` an earlier match masks the trailing position on almost every
  subject; `(?m)^$` on `"a\n"` is the one shape that shows it from 0 and is
  now in the corpus by name. The corpus gained a full startpos sweep for the
  same reason.
  **THE FIVE SCAN-AVOIDANCE MECHANISMS (§3.6.1): NOT ONE SHIPS AN
  INTERSECTION, AND ONLY ONE IS A LIVE HAZARD.** The design proposes
  intersections for rows 2-5. The wave wrote a sabotage per mechanism and
  MEASURED each before committing it — sweeping every corpus pattern whose
  ARTIFACT the edit changes through 107 subjects under the §3.1 find-all loop
  — and SHIPPED FOUR ROWS OF SIX:
  - rows 3/5 (self-loop skips) DECLINE via `pick_skip_states`, and it is real:
    S78 turns `(?m)[^c]*$` on `"a
b
c"` from `(0,3)` into `(0,1)`, and
    `(?m)[^c]+$` on the same subject from `[(0,3)]` into `[(0,1),(1,3)]`. Both
    witness subjects were ADDED TO THE CORPUS when the row was validated; the
    first draft had neither and the row would have come back UNDETECTED.
  - rows 1/2 (the prefilters) share the widened `start_acc`, and **that
    widening is REDUNDANT** — D3's accept-pruning cuts the unanchored start
    self-loop out of every accepting closure, so a class the start state
    accepts on ESCAPES it and the prefilter's stay set never contains it.
    §3.6.1's `x*` prediction is FALSE: narrowing `start_acc` changes 21
    corpus artifacts and **0 answers over 2,247 cells**. Kept as
    belt-and-braces (free, and the honest reading of "accepts on any class"),
    NOT cited as load-bearing, and NO sabotage row — a row with no failing
    direction is the check-design failure this project records, and writing
    one here would have been the section's own mistake repeated. This is the
    same argument `emit_dfa.c` already makes for the neighbouring
    `last == (size_t)-1` gate, which two critics attacked without building a
    witness.
  - row 4's compensating accept can only UNDER-report (the EOL view's closure
    is a superset of the base's; a skip-eligible state's accept does not vary
    by class): 13 artifacts, **0 answers over 1,391 cells**, and 0 new answers
    even when combined with row 3's sabotage. NO row.
  The cost of DECLINING is measured too: exactly ZERO on the pre-wave corpus
  (the eligibility test is false at every state) and non-zero on the `(?m)$`
  family, accepted and recorded rather than priced away.
  **THE `(?m)^` COST, MEASURED ON THE BUILT COMPILER AND ARCHIVED**
  (`assertions_measurements/out/mline_caret_cost.txt`; the [M6.1] probe gained
  a wave-C arm that runs the REAL construct instead of the stand-ins it had to
  use when the letter was refused):
  - NON-CROSSING arm, the one D63's prefilter is for: `(?m)^ERROR` against
    its unprefiltered stand-in `^ERROR|\nERROR` reads **3x / 7x / 7x** at
    n = 8k/32k/128k. What is LEFT against a plain unanchored `ERROR` is
    **82x / 33x / 27x** — so the design's 85-185x target is closed to roughly
    27-33x at settled n, not to nothing, and that residual is the honest
    number rather than the headline.
  - CROSSING arm, D63's accepted residue: `(?m)^[^b]*b` still grows
    **3.98x / 3.99x / 3.98x / 4.01x per doubling** — the O(n^2) signature,
    unrescued exactly as D63 says. Its ratio against the stand-in is
    **1.00-1.01x** at settled n, which incidentally confirms the [M6.1]
    stand-in was faithful: the prefilter skips nothing there because every
    line start is already a candidate.
  EVIDENCE: tests/assertions/multiline.rxt, every expectation libpcre2-
  produced, re-verified by BOTH oracles on every run;
  tests/assertions/run_mline_diff.sh, a generated subject sweep over the
  `(?m)$` family on BOTH engines with the population claim CHECKED (it fails
  if too few patterns carry a live mechanism);
  tests/codegen/run_mlinectx_identity.sh against a `-DPCREC_NO_MLINECTX`
  reference; sabotages S76-S81 and the two new mech arms;
  tests/lib/mlscan.py, the `(?m)`-scope scanner all three checks share, with
  its own self-check.
  **DEVIATIONS AND FINDINGS RETURNED**: (1) the `(?m)^` rule above, which is a
  design refutation and an oracle divergence at once. (2) `(?m)$` reaches
  `emit_view_select`'s `has_end && !has_eol` arm — the branch wave A wrote for
  "`\z` with no `$` anywhere" — because `N_EOL_M` never consults `eol_ok`: a
  construct the design calls `$`'s sibling shares its emitted selector with
  `\z` and none with `$`. (3) Wave B's inline note at ENG_ATTEMPT's EOL arm
  ("the EOL position's next byte is `\n`, which is NOT a word character, so
  the scalar accept is already right") was right for its axis and its
  CONCLUSION IS NOW WRONG — `'\n'` IS the newline definition; the arm reads a
  compile-time constant indexed by `upc_of_newline`, and the `eolvar`-only arm
  SPLITS when its two positions disagree. (4) D63's candidate set is the
  LIVE-SEED set, strictly more general than §3.7.2's "offset 0 or immediately
  after a `'\n'`" — that sentence is true of a fully-anchored pattern and
  false of `(?m)^a|b`, and sabotage S81 is the sentence written as code.
  (5) K28 gains a FOURTH spelling, `a(?m)^b`, excluded by name with live
  equivalents; the list grows monotonically until the wrapper is fixed.
  SUITE (this lane, build/test_wavec_final.log, EXIT=0, zero FAIL lines):
  corpus **19,346/0** (16,066 at the merge base + 3,280 new `(?m)` cells),
  cli 269/0,
  reject 535/0 (gated 64 -> 62), registry 169/0 + PC-3 163/0, codegen 52/0,
  trie 7/0, vm-identity 9/0, ir-listing 79/0, vm 35/0, possessify 18/0,
  rungselect 24/0, counterk 23/0, mrl 22/0 + 18/0, altcls 15/0, assertions
  33/0, endvar-identity 3/0 (**1087** `pos == n`-view-free patterns identical,
  83 controls differing), wordctx-identity 3/0 (**1108** identical, 63
  controls), mlinectx-identity 4/0 (**1117** identical, 56 controls, plus the
  shared scanner's own 36-case self-check), mline-diff 3/0 (**5,038 DFA +
  5,038 VM cells** at 0 divergences, 20 of 22 patterns carrying a live
  scan-avoidance mechanism), encseam 2/0, resource 19/0, thread 8/0;
  `make strict` clean (build/wavec_strict.log).
  (6) The identity gate's first split was too coarse — ten patterns that SET
  `m` with no anchor to receive it read as a dead reference knob — and the
  `(?m)$` differential's first python arm excluded the D47.5 GUARD CELL over a
  `^` that is a class negation in `[^c]`. Both are why the scanner is one
  shared file with a self-check.
  (7) **WAVE A's ENDVAR-IDENTITY GATE WENT RED ON 51 PATTERNS, and it was
  right to.** `(?m)$`'s "or end of subject" half IS wave A's `pos == n` view
  (`N_EOL_M` reads `end_ok`), so a `(?m)$` pattern belongs to that gate's
  POSITIVE CONTROL and not to its identity population — but wave A split on
  `grep -F '\z'`, which was exact when it was written. The split now asks
  "does this pattern create a `pos == n` view" through the shared scanner.
  Worth naming: a wave-C construct silently joined a wave-A mechanism, no
  behaviour test could have seen it (`-DPCREC_NO_ENDVAR` is never defined in a
  shipped build), and the construction gate is the only instrument that did.
  That is the third time in this module a byte-identity gate has earned its
  keep.
  (8) **D62's control 2 NEEDS A CAPTURE-BEARING CELL, and §8.7's own spelling
  is capture-free.** Possessification is a VM optimization — it removes
  backtracking states, and A DFA HAS NO BACKTRACKING TO REMOVE — so
  `(?m)[^c]{1,3}$` routes to the DFA and answers correctly with the flag-read
  turned off (measured: 749 find-all cells, 0 divergences under S77). One
  parenthesis routes it to the VM and the same pattern loses its match
  entirely. multiline.rxt carries both forms in adjacent sections and says
  which is which. This is wave B's S75 lesson ("every block in wordb.rxt was
  capture-free so nothing in the corpus reached emit_vm.c's arm at all")
  arriving one wave later on a different arm — worth a process note, because
  the wave that recorded it is the wave before this one.
  **WAVE D LANDED 2026-08-19 (lane/asrtwaved)**: `\G` as `A_GSTART`/`N_GSTART`
  — the module's THIRD kind of question, after the absolute-position tests
  (`\A`/`\Z`/`\z`) and the two-byte context tests (`\b`/`\B`): it compares
  the position against a RUNTIME value the match call supplies rather than a
  compile-time constant, which is why it costs a closure bit
  (`Clo.gst_ok`) and a SECOND FAMILY of interior start states (`Dfa.s1g[]`,
  the same class-axis family as `s1u[]` closed with that bit set) and NOTHING
  in the alphabet. §4.1's answer to DD-4 lands as designed and needs no wrap
  toggle: `start_max` is a THIRD compile-time string (`0` fully-`^`-anchored /
  `startpos` fully-`\G`-anchored / `n`), because ENG_ATTEMPT already emitted
  the un-self-looped shape. §4.2's three reachable start states become a
  three-way dispatch with `start == 0` tested FIRST (it is the row where BOTH
  `\A` and `\G` hold). Mid-pattern `\G` (`a\Gb`) is unsatisfiable with no
  special case anywhere — the worklist closes every successor with the bit
  clear, because one transition means one byte consumed. §4.3's spec sentence
  landed in `docs/spec/match_api.md` §3.1.
  EVIDENCE: tests/assertions/run_gstart_diff.sh — **13,062 DFA + 13,062 VM
  cells** over 21 patterns x 111 subjects x EVERY startpos in `[0, n]` at 0
  divergences from libpcre2 (the startpos axis is swept exhaustively where
  wave C used two values, because `(?m)`'s truth is a fact about the SUBJECT
  and `\G`'s is a fact about the ARGUMENT); **888 find-all runs** agreeing
  span for span with libpcre2 driven through the SAME §3.1 loop, plus the
  named cell (`\G[ab]+` on `"ab ab ab"` reports only `0,2` where `[ab]+`
  reports all three — tokenizer vs scanner, which is the whole content of
  §4.3); R30 E8's replacement obligation SCOPED as §10 requires — **18,214
  agreeing cells for fully-`\G` patterns, 446 legitimate DISagreements for
  partial ones, 0 bad**, on both engines, since §9.3's own correction is that
  the two match-here entries do not share a shape; tests/assertions/gpos.rxt
  286 cases (280 libpcre2-verified); tests/codegen/run_gstart_identity.sh at
  **1175/1175** `\G`-free corpus patterns byte-identical with 21 controls
  differing; sabotages S82/S83/S84 and two new mech arms.
  **THE VM NEEDS A PARAMETER, which §4 and §9.3 are both silent on.** `\G` is
  the only assertion in the module whose truth is not a function of
  `(s, n, pos)`: `<prefix>_match_impl` has `ctx->pos` — the offset THIS
  ATTEMPT began at — and the search entry's retry loop moves it. So
  `<prefix>_startpos` is threaded in, emitted only where a `\G` exists, on the
  MRL ceiling's precedent; the three entries pass `startpos` / `ctx->pos` /
  `ctx->pos`, the last two being E8's answer reached from the artifact rather
  than from the withdrawn premise.
  **ORACLE: the module's THIRD exclusion and the first TOTAL one** —
  `re.compile(r'\G')` raises `bad escape \G`, so gpos.rxt is `# pcre2-only`
  in its entirety (U11c). The consequence is for the INSTRUMENTS rather than
  the corpus: wave C's python arm exists to catch the script driving the
  oracle wrongly, and it cannot run on `\G` at all, so run_gstart_diff.sh §0
  points it at the sweep's own `\G`-FREE control patterns — weaker than wave
  C's, and the strongest available.
  **D63's THIRD INSTANCE: MEASURED, AND THE ANSWER IS "THERE IS NO THIRD
  INSTANCE"** (`assertions_measurements/out/gstart_prefilter.txt`). The
  derivation is over PREDECESSOR-BYTE liveness of `s1u[]`, and a partial-`\G`
  pattern's `s1u[]` is exactly the closure of its `\G`-FREE branches — so
  instance one already serves the population with no new code (3 of 8 measured
  partial-`\G` shapes get a `memchr` today). The other 5 are unserved for a
  reason that is NOT `\G`'s: the `\G`-free control `(?m)^a|b` is unserved
  identically, and so is D8's `^a|b`. The gap is real — `\Gfoo|xbar` runs
  ~83x slower than plain `xbar` on a 1 MB no-match subject — and it belongs to
  D63's SECOND instance (the first-byte set at offset 0), which would serve
  all three shapes from one place. **RECOMMENDED to the manager: schedule
  instance 2 as one piece of work; this is a second population arguing for
  it.** What wave D DID add to the prefilter is a SOUNDNESS bound, not an
  instance: the guard's lower limit is `start > startpos` rather than wave C's
  `start > 0` whenever the machine has a `\G` family, because the derivation's
  domain is `start > startpos` and the attempt AT `startpos` enters a state it
  never looked at. `(?m)^a|\Gb` on `"xb"` at startpos 1 loses its match under
  the wave-C bound (S82) — a population existing only in the INTERSECTION of
  two waves.
  **DEVIATIONS AND FINDINGS RETURNED**:
  (1) **THE BYTE-IDENTITY GATES' REFERENCE KNOBS ARE MIS-PLACED, MEASURED.**
  This wave's first draft put `-DPCREC_NO_GSTART` in `src/ir/dfa.c` beside
  waves A/B/C's — and its own byte-identity sabotage then left the sweep at
  **1175/1175 IDENTICAL**, because the reference compiler is built from THE
  SAME (sabotaged) SOURCES and any edit outside the knob's own gated region
  applies to both builds and CANCELS. Re-measured on wave B's row:
  `run_wordctx_identity.sh` stays **1135/1135 identical under S71**, and that
  script fails only because the deleted gate orphans a parameter and the
  reference build warns — i.e. the row is scored DETECTED for a reason
  unrelated to its own `SAB_DOC_FIGURE`, and a same-shaped sabotage that did
  not orphan a parameter would read UNDETECTED against a clean gate. Wave D's
  knob moved to the EMITTER's three decision points, which makes the reference
  structurally the pre-wave EMITTER; S83 then goes red in the sweep (93 of
  1175) as it should. S71 and S76 are ANNOTATED with the measurement;
  **re-placing THEIR knobs is a manager decision and was not done here.**
  This is the project's control-shares-a-source-with-its-subject shape,
  found inside the directory built to prevent it.
  (2) **Moving the knob immediately exposed a real defect in this wave's own
  emitter** that the mis-placed knob had hidden: `gtbl` (does the `\G` start
  family vary by class) answers exactly what `dfa_needs_seed` answers on a
  `\G`-free machine, so without an `&& gseed` conjunct every `\b` and `(?m)`
  artifact emitted a `gseed[]` table no dispatch ever read. Nothing else in
  the tree could have seen it.
  (3) **A LIVE WAVE-B OVER-REJECTION, found while adding the sixth node
  kind.** The bare-anchor rule (quantifier-refuse bare, group-wrap inside
  parens) lived as FOUR hand copies — `try_quant`, `p_group_body`,
  mod_modifiers.c's `(?i:...)` port, mod_named_groups.c's declaring port — and
  wave B added `\b`/`\B` to two of them. Now ONE predicate
  (`pcrec_is_bare_anchor`) with four readers. **The two stale copies were NOT
  equally reachable and this lane's first write-up got that wrong before
  measuring it on a pre-fix build**: mod_modifiers.c's is LIVE on the default
  path (`(?i:\b)*`, `(?i:\B)*`, `(?i:\G)*` all REFUSED where libpcre2 gives
  `(0,0)` — a tier-2 over-rejection invisible to a corpus of ACCEPTED
  patterns), while mod_named_groups.c's is reachable ONLY under
  `--no-captures`, because a named group wraps its body in `A_CAP` and an
  `A_CAP` is not a bare anchor, so at default captures the quantifier lands on
  the wrapper. The two halves are pinned in different places for that reason —
  gpos.rxt section 8 and run_assertions_tests.sh §2b, since no `.rxt` block
  can pass a flag.
  (4) `\G` in a quantifier's FOLLOW must make possessification DECLINE and
  takes `\A`'s arm, NOT `\z`'s — a third reason for the same verdict, so it
  gets its own STRATS row. The attractive wrong generalisation is "singleton
  satisfying set, therefore exempt": `\z`'s singleton is `{n}`, ABOVE every
  retreat position, and `\G`'s is `{startpos}`, BELOW every one. Measured:
  `(x)?a{0,4}\G` on `"aaaa"` answers `(0,0)` shipped and NO MATCH under `\z`'s
  arm (S84) — D47.5's failure mode one construct over.
  (5) K28 gains a FIFTH and SIXTH spelling, `a\Gb` and `x\G`, excluded from
  gpos.rxt by name with live equivalents; run_gstart_diff.sh §4 asserts them
  at `-O2` instead. K28's own entry predicts this list growing once per wave
  that lands a start-state assertion, and this is the third wave to confirm it.
  (6) `run_mlinectx_identity.sh` and `run_mline_diff.sh` were absent from the
  `ubsan`/`asan` lists while their wave-A/B siblings were present; the two
  IDENTITY gates (wave C's and wave D's) are added, the two heavy
  DIFFERENTIALS deliberately not — putting a multi-minute sweep on the
  sanitizer battery is a scheduling decision for the manager.
  **WAVE E LANDED 2026-08-19 (lane/asrtwavee) — `\K`, AND THE MODULE'S
  CONSTRUCT LIST IS COMPLETE.** `A_KRESET` lowering to **N_EPS** (`\K` changes
  no language, only what is reported), the SECOND `forces_*` row in
  src/opt/select_engine.c, and the trailed `caps[0][0] = pos` write. All three
  of §6.3's rules are discharged; ONE OF THEM AS A CORRECTION, below.
  **THE SLOT IS THE MECHANISM, and §6.2 does not name it.** `\K` writes
  `stv[0]` — group 0's START slot, reserved by `nstate`'s `2 * ncaps` term
  since [M4.5b] and never written by anything, since capture writes use `2*k`
  with `k >= 1` and every other family bases at `2 * (ngroups + 1)`. So the
  slot that already MEANS "the reported start" is the one `\K` writes, and it
  inherits with no new machinery: the trail's exact old-value undo, the
  per-search `PCREC_UNSET` fill (which becomes the "no `\K` crossed on this
  path" signal — a value a position can never legitimately hold), the rewind
  on a failed attempt, and the listing event. No slot is allocated. The ONE
  cost §6.2's "one line" hides is a TRAIL ENTRY in `vm_cost`, multiplied by
  the enclosing quantifier exactly as A_CAP's two are — the only member of the
  assertion family that is not free there, and under-counting it returns
  `PCREC_ERR_FRAMES` on a pattern the artifact can match.
  EVIDENCE: tests/assertions/run_kreset_diff.sh — **13,398 default-engine
  (hybrid, prefilter LIVE) + 13,398 `--engine=vm` (prefilter OFF) cells** over
  33 patterns x 70 subjects x EVERY startpos in `[0, n]` at 0 divergences from
  libpcre2; **23,548 ENTRY cells** on both engines at 0 wrong, of which
  **2,462 have the consumed length differing from the reported span's width**
  and 0 returned the width; the find-all loop agreeing span for span with
  libpcre2 driven through the SAME §3.1 loop, including the empty-reported-span
  arm `\K` is what makes reachable; tests/assertions/kreset.rxt **596 cases,
  0 pending**, every expectation libpcre2-produced; four `[M6.2-KRESET]`
  structural checks; sabotages S85/S86 and one new mech arm.
  **§6.3 RULE 3's PROPOSED CURE WAS NOT NEEDED, and this is the wave's
  substantive correction to the design.** The rule ("filter on the pre-`\K`
  start, return the consumed length") is derived from the DFA artifact's
  `rx_match` — `rx_search` plus `caps[0][0] != ctx->pos`, returning
  `caps[0][1] - caps[0][0]` — and both lines really do break under `\K`. But
  R30 E8's OTHER correction is that the two engines' match-here entries do not
  share a shape, and a `\K` pattern is VM-FORCED, so it never HAS that entry.
  The VM's calls `<prefix>_match_impl` at `ctx->pos` directly: the anchoring is
  a property of the CALL rather than a test applied afterwards, and the return
  is `pos - ctx->pos`, computed from positions and never from `caps`. So the
  design's proposed slot ("the VM has to report both positions") describes a
  fix for an entry a `\K` pattern cannot reach — the VM already keeps the
  pre-`\K` start, in `ctx->pos`, where it always was. What the wave owed
  instead was EVIDENCE, since "the entries happen to be right" is exactly the
  claim that rots: kreset_entries.c drives all three entries, and
  run_kreset_diff.sh §2 checks both match-here ones against libpcre2's answer
  for **`\G(?:PAT)` at the same startpos** — wave D's construct used as the
  ANCHORED-MATCH ORACLE this tree has no flag for, which is the generalisable
  half: when an entry point has no oracle flag, find the PATTERN SPELLING that
  asks the oracle the same question.
  **ORACLE: the module's FOURTH exclusion, and it COMPLETES the list** —
  `re.compile(r"a\Kb")` raises `bad escape \K`, so kreset.rxt is
  `# pcre2-only` in its entirety (U11d). THREE of the module's eight constructs
  are excluded WHOLLY (`\Z` answered wrongly, `\G` and `\K` not expressible)
  and a fourth PARTLY (`(?m)`, its `^` half only); `\A`, `\z`, `\b`, `\B`
  and `(?m)$` are python-verified cell for cell at 0 divergences, which is
  what makes the rule a statement about particular CONSTRUCTS rather than
  about the module. A lookbehind is NOT an escape hatch here: `(?<=a)b` is a
  different assertion with different backtracking, cannot express the
  variable-width shapes `\K` is for, and needs a module that does not exist.
  **NO BYTE-IDENTITY GATE WAS BUILT, and that is a justified deviation from
  the four-wave precedent rather than an omission.** Waves A-D each changed a
  construction spanning several emitter decision points, so each needed a
  corpus-wide comparison against a `-D` knob build. `\K` is VM-forced and the
  emitter reads `v.nkreset` into a DEFAULT ARTIFACT at exactly ONE site
  (`<prefix>_caps_out`'s body; `--emit-ir`'s listing and `--trace`'s ACCEPT
  line read it too, and neither writes a default artifact),
  so the claim is about one predicate: pinned permanently as
  `[M6.2-KRESET rule 1b]`, which quotes the pre-wave body as a LITERAL so a
  rewrite into a third shape fails too. The corpus-wide half was MEASURED ONCE
  against the genuine PRE-WAVE COMPILER — **1,208/1,208 identical at the
  default engine, 1,209/1,209 under `--engine=vm`, 0 refusal mismatches** — a
  reference sharing NO SOURCES with the subject, which is strictly stronger
  than a knob build and is the direct answer to wave D's own knob-placement
  finding.
  **DEVIATIONS AND FINDINGS RETURNED**:
  (1) **THE SR-8 TRIPWIRE FIRED — the day it was written for — AND THE ANSWER
  WAS STILL NOT SR-8.** `tests/registry/registry_check.c`'s
  `check_engine_capability_tripwire` has asserted since [M4.7a] that no
  `VM_ONLY`-masked `RS_MODULE` row has a wired producer, naming
  select_engine.c as the thing to build first. [M6.3]'s trip was a
  reclassification (a named group's AST is an ordinary A_CAP, so the rows
  moved to ANY_ENGINE and LEFT the population); `\K` genuinely is VM-only and
  stays in it. Building SR-8's generic registry-column consultation at sample
  size ONE is what D18/OS-0/D53 forbid, and `\K`'s verdict is not "a column
  says VM" but "this AST carries a node whose write is path-dependent" — a
  fact about the tree. The tripwire keeps its demand for the other 47 rows and
  gains a NAMED exception that PAYS: it asserts LIVE that `--engine=dfa` on
  `a\Kb` refuses by the construct's own name AND that the same pattern
  compiles on the default engine. **A SECOND construct arriving there is when
  the generic consultation has earned its axis** — that is the recorded
  trigger, and it is a manager decision.
  (2) **WAVE D'S PREDICTION ABOUT THE ENABLED-BUT-UNBUILT MECHANISM IS
  MEASURED WRONG.** Its note said that when `\K` left tests/reject's
  `reject_gated assertions` paragraph, "the row that has to go WITH them is
  the epilogue's own pin in src/parse/ext.c (the `UNBUILT` arm). A refusal
  mechanism with no population is machinery nothing can test." The mechanism's
  population is not this module's rows — it is EVERY registry row whose module
  is enabled and whose port is unwired, and it is large and live: measured on
  the shipped compiler, `--features backrefs '\k'`, `--features lookaround
  '(?=a)'`, `--features atomic-groups '(?>a)'` and `--features quoting '[\Q]'`
  all produce it. Deleting the arm would have deleted a live diagnostic. What
  WAS true is narrower: `\K`'s row was the ONLY hand-written pin on that arm
  anywhere in the tree. Four rows now stand in its place across THREE modules
  and BOTH positions (the in-class wording is spliced at a different site in
  ext.c), gated count 61 -> 64. **Generalisation for the next module: when a
  module's last unbuilt construct lands, move the PIN, not the MECHANISM.**
  (3) **The three optimisation rungs had to be decided and §6.2 is silent on
  all of them.** `src/opt/revdet.c` DECLINES any body containing a `\K`, and
  that decline is a CORRECTNESS requirement rather than a missed rung: the
  reverse-deterministic rung suppresses per-iteration capture writes and
  recovers them by walking backwards over ITERATION BOUNDARIES, and a `\K`
  position is not on that lattice. The cursor rung declines on the kind
  (`vm_det_seq`'s `default`), also required — its span loop scans by stride and
  would skip the write. Possessification does NOT need to decline, and the
  argument is the one worth keeping: `\K` is transparent to `first_of` because
  it cannot FAIL, and possessifying a loop CONTAINING one is safe because the
  cut discards retreat frames only after the loop exits at its chosen count,
  while a trial iteration that failed has already had its write rewound by the
  fail label. MEASURED off the artifacts' own `RX_VM_STRATS` stamps rather than
  argued: `(?:a\K)*b` stamps `0x1` (POSSESSIVE) and answers `(3,4)` on
  `"aaab"`, `(?:a\Kb)*c` stamps `0x1` and answers `(3,5)` on `"ababc"`, and
  `(?:a\K)*ab` stamps `0x2` (BACKTRACKING — body and follow both start with
  `a`, so the analysis declines) and answers `(2,4)`, which is the retreat
  case. All three are corpus cells, all three libpcre2-verified, so the
  possessification argument has both a shape that takes the rung WITH a `\K`
  in the loop and the shape that would expose an error if the argument were
  wrong.
  (4) `run_kreset_diff.sh`'s §2 was BATCHED after measuring it: one driver
  process and one awk per artifact instead of ~six subprocesses per cell,
  9m18s -> 5m10s wall, with §2's own figures BYTE-IDENTICAL across the change
  (23,548 cells, 2,462 non-vacuous, 0 wrong). A speedup that moved a count
  would have meant the batching changed what was compared.
  (5) K28 gains NO new spelling — the first wave since B not to. No shape in
  this corpus compiles to a single dead state, and the reason CORRECTS wave
  C's stated prediction rather than merely not confirming it: the shape needs
  a pattern that CANNOT MATCH, every previous spelling got there by asserting
  something impossible after a byte was consumed, and `\K` asserts nothing —
  it cannot fail, so no placement of it makes a pattern unsatisfiable. The
  rule is "one per construct that can make a pattern IMPOSSIBLE", not "one per
  wave", and module `assertions` has now landed all of those. K28's entry
  carries the correction; the repair slice's scope is unchanged at six
  spellings.
  (7) **THE GENERATED COMPLIANCE INDEX IS STALE FOR THE WHOLE MODULE AND THIS
  WAVE DID NOT FIX IT — manager decision.** `docs/pcre2_compliance.md`'s
  hand-written prose rows are corrected here (including the `\b \B \G` row,
  which had read `REJECTED` for two waves after those waves landed), but the
  GENERATED index below them still reads `REJECTED | planned` for all eight
  constructs, because it is derived from each registry row's `status`/
  `roadmap` columns and every one of them is still `RS_MODULE`/
  `ROADMAP_PLANNED`. That is not `\K`'s situation, it is the module's: waves
  A-D left it too. Changing those columns is a cross-cutting edit — the same
  fields feed `registry_check`'s exact counts, `tests/reject`'s iterated rows,
  PC-3's row-claim polarity and `compliance_section.py --check` — so it wants
  its own slice rather than a rider on the closing wave, and it should be one
  edit for all eight rather than one per construct.
  (8) `run_kreset_diff.sh` is NOT on the `ubsan`/`asan` lists, inheriting wave
  D's finding (6) posture for heavy differentials verbatim (it is a ~5 minute
  sweep). Also a manager scheduling decision, unchanged by this wave.
  (6) `docs/spec/match_api.md` §3.1 gains the wave's spec sentence, and it is
  a bigger one than `\G`'s: `caps[0][0]` is where REPORTING begins, which is
  not always where matching began, so `caps[0][0] == caps[0][1]` no longer
  implies nothing was consumed and `caps[0][0]` is not a bound on where the
  engine looked. The find-all loop is unaffected (it advances off
  `caps[0][1]`) and the anchored entries return the CONSUMED length, which is
  what makes the D38 callout advance terminate.
  **REPAIR SLICE LANDED 2026-08-19 (lane/repair) — the module's last code
  lane, serialized after all five waves so the every-artifact byte churn
  lands once.** Three chartered items; two done as chartered, ONE REFUTED.
  (1) **K28 CLOSED.** The `<prefix>_match` wrapper's `caps` array is
  INITIALIZED in `src/gen/emit_dfa.c`. The entry's other suggestion —
  restructure so gcc sees the dominance — was tried FIRST and MEASURED not to
  work: splitting the `||` into two `if`s leaves the `-O1` report exactly
  where it was. **THE ENTRY NAMED ONE SITE AND THERE WERE THREE**:
  `<prefix>_match`, `<prefix>_match_caps` and the standalone `main()` all
  emit the same declaration and all three warn; the second and third were
  invisible because `-Werror` stops at the first report, and no corpus header
  or known-issue text had ever mentioned them. Clean at `-O0`/`-O1`/`-O2`/
  `-O3`/`-Os` (all five, so the report was not traded to another level) and
  under both sanitizer GENCFLAGS paths; `RX_NCAPS > 1` artifacts raise no
  `-Wmissing-braces`. THE SIX EXCLUDED CORPUS SPELLINGS ARE BACK, oracle-
  verified against libpcre2 (`^\Bfoo` `^\Bo` `^a\bb` +216 cells,
  `a(?m)^b` +45, `a\Gb` `x\G` +30); each was re-verified FAILING on the
  pre-slice compiler at the harness's exact GENCFLAGS and CLEAN on the fixed
  one, so the reinstatement is evidence rather than assertion. The live
  sibling-branch equivalents STAY.
  (2) **THE A/B/C REFERENCE KNOBS RE-PLACED — AND "MOVE THEM TO THE EMITTER"
  IS NOT WHAT WORKED.** Wave D's finding says a knob sharing a source with
  the sabotaged code cancels, and prescribes wave D's own emitter placement
  as the cure. MEASURED BY THIS SLICE BEFORE IT WROTE ANYTHING: an
  emitter-only knob leaves S71 at **1186/1186 `\b`-free artifacts
  byte-identical**, i.e. exactly as blind as the flag pin. The reason is
  which STAGE decides the emitted text — `\G` refines no alphabet and interns
  no state the emitter cannot neutralize, but `\b`/`(?m)` refine the ALPHABET
  and `\z` interns a STATE, and no emitter branch can un-refine a partition.
  Each knob now has TWO halves: a `#ifndef` around the ANALYSIS'S ACTION
  (`eqclasses`' refinement, `make_state`'s interning — uncancellable by an
  edit to the action's own gate, which is exactly what S71/S76 are) AND an
  emitter half at the decision points. After both, all three rows are red on
  their OWN gates through BYTES — not through the incidental
  `-Wunused-parameter`, which the knob's `(void)` cast removes — with every
  corpus arm green: **S71 `wordctxid:1fail/2pass, corpus:0fail/20533pass`,
  1178 of 1186 differing; S76 `mlinectxid:1fail/3pass, corpus:0fail/20533pass`,
  1117 of 1201; S69 `endvarid:1fail/2pass, corpus:0fail/32pass`.** `-DPCREC_NO_ENDVAR` was ALREADY at its action and did not move; S69
  is red on its gate for its documented reason. The emitter half is
  byte-neutral in a shipped build, measured at 1,261/1,261 corpus artifacts
  identical against the pre-slice compiler. The durable rule, recorded in
  tests/mech/CLAUDE.md: **wrap the ACTION, never the FLAG.**
  (3) **THE COMPLIANCE FLIP WAS NOT DONE, AND THE FINDING'S PREMISE IS THE
  REASON.** Wave E's finding (7) above reads the generated index's
  `REJECTED | planned` on the eight `assertions` rows as staleness specific
  to this module. MEASURED (`pcrec --list-syntax`, counted by module): **34
  rows of that index name a module that is SHIPPED — `classes` 12,
  `modifiers` 12, `assertions` 7, `named-groups` 3 — and every one reads
  `REJECTED | planned`.** `\d` and `(?i)` are marked exactly as `\b` is.
  The index's `status` is `RegStatus`, a fact about PCRE2 and pcrec's BASE
  grammar ("the base grammar does not implement this; `module` names what
  does"); there is no "the owning module is built" value to flip TO, and
  `RS_BASE` would be false (these need `--features assertions`), would break
  the `RS_BASE => ROADMAP_NONE` pairing `registry_check` enforces, and would
  delete the module name from the gate-CLOSED diagnostic `tests/reject`'s
  rows assert. Flipping only these eight would make the index INCONSISTENT
  rather than current. So none of the four named consumers moved and no count
  was re-baselined. What landed instead is a "How to read the generated index
  below" section in `docs/pcre2_compliance.md`, carrying the measurement and
  the note that the shipped status lives in the PROSE rows by design
  (`compliance_section.py`: "the inventory is generated and the analysis is
  not"). **RE-HOMED AS A DESIGN QUESTION FOR THE MANAGER**: giving the
  registry a built-status field so the index can answer "does this compile
  today" is a real, small, WHOLE-REGISTRY change — not a per-module repair —
  and it is now the only thing left of this item.

- [SPEC-M] STATE:completed (DONE same day, lane/specm merged post-union-battery: named (?m) exceptions in check01 (nm pair, allowed-count exactly 1) and check07 (structured-field selector + non-vacuity guard), sabotage-validated both directions; suite 12/2 -> 14/0; amendment in the D27 suite's acceptance record; expiry = DD-11) — formerly STATE:not-started (CHARTERED by Frank 2026-08-21, ruling 1a
  of the triage discussion: "agree but don't spend a lot of time as
  this is to be replaced") — tests/spec_mod0 check01_isolation and
  check07_gate_equivalence, red since [M6.2] wave C: their model
  assumes a module's behavior depends only on its OWN gate, and (?m)
  is a measured TWO-MODULE construct (mod_modifiers.c consults
  FEAT_ASSERTIONS for the multiline EFFECT — the same fact the D27
  corpus found from outside and gating.rxt pins on all four
  combinations). Fix: carry (?m) as a NAMED, evidence-cited exception
  in both checks (cite the D27 gating.rxt record and D65's memo),
  restore the suite green, and note the amendment in the suite's
  acceptance record since it is D27-authored. MINIMAL EFFORT by
  ruling — the real resolution is [DD-11]'s flags-as-binding-mutators
  redesign, which dissolves the cross-module shape; this row's fix is
  interim truth-restoration, not architecture

- [M6-READ] STATE:completed (CLOSED 2026-08-21, thirty-fifth session: sample stage APPROVED by Frank; the full emitter conversion merged c4bb613 — census 925 patterns / 0 uncompilable / 574-574 byte-identical / 570 renamed, suite + full mech green on the lane tip and again on merged main (85/0/0 at 115fbc6), union battery + gate 13/13 archived b8cb848; five pin classes + the rename-reaches-English inventory + the fixed-fixture-sampling lesson in docs/design/m6read_samples/CONVERSION_LOG.md; the ~64 doc-prose mentions and 47 emitter-comment stragglers cleaned by the tail lane; ORIGINALLY (2026-08-21 morning, on Frank's ruling — pulled ahead of [M6.4]/[M6.5]/[M6.6] together with the [M6.2] post-module queue's tranche A, D27 corpus merged and close battery in flight; SAMPLE STAGE first: lane/m6read delivers the naming scheme, hand-commented sample artifact(s), object-code-neutrality measurement and pin-update budget FOR FRANK'S APPROVAL before any emitter conversion) — EMITTED-CODE READABILITY PASS (Frank,
  2026-08-18, thirty-second session: ruled as the IMMEDIATE follow to
  M6, ahead of the rest of M5). The generated C becomes readable as
  first-class output. Frank's five requirements, near-verbatim:
  (1) DATA STRUCTURES: a 1–3-line comment each — what it is, where it
  is used, what it means. (2) CODE SECTIONS: 1–2 lines saying what the
  section is about to do ("prefilter section to find candidates...").
  (3) LINE COMMENTS — CODE ONLY, not data structures (Frank
  clarification, same day): 1 line, the INTENT of the next line, never
  an echo of the code ("advance to next character", NOT "increment
  source pointer"); structures/tables get item (1)'s block comment,
  never per-line/per-row commentary. (4) FULL NAMES — LOCALLY SCOPED
  IDENTIFIERS ONLY (Frank's second clarification, same day): variables,
  types, and structure names that are LOCAL to the artifact get full
  names — no "pos", the source_position/source_index class of names,
  ONE consistent scheme, the scheme delegated to the implementer. ABI
  NAMES ARE KEPT AS-IS: the public emitted surface (entry points,
  rx_matchfn, the emitted header's names) does not change — THIS ROW
  MAKES NO ABI CHANGE OF ANY KIND; it is purely an internal
  comment/clarity step. (5) STATE-NAME LEGENDS (upgraded from
  "consider" to a REQUIREMENT by the same clarification): numbers in
  data tables in structures/arrays get short text names WHERE THEY ARE
  STATES — not indexes or other numeric kinds — with a legend in the
  comment above the table.
  ENGINEERING NOTES recorded at ruling time: (i) the pass must be
  OBJECT-CODE-NEUTRAL — comments, renames, and state names cannot
  change the compiled artifact; the natural check is
  compile-before/after and compare object code, which the row gets for
  free (state names via macros/enums resolving to the same values);
  (ii) spec §2's verbatim quotes re-quote under the verification-ledger
  discipline in the same change — the ABI comment block and all ABI
  names are UNTOUCHED by ruling, so the re-quote is body-text only;
  (iii) codegen structural checks and stamp pins that grep emitted
  LOCAL identifiers need a coordinated pin update — budget for it;
  (iv) distinguishing state-valued table cells from index/other
  numerics is emitter knowledge — the emitter tags what it emits, no
  after-the-fact inference; (v) the code-vs-structure
  clarification resolved the worst of the comment-density question
  (tables never get per-line commentary); the design pass still brings
  Frank ONE sample commented artifact to approve the style against
  before the full emitter conversion — cheap, and it fixes the
  line-comment granularity on real code by example.
  INTENT CLARIFICATION (Frank, 2026-08-21, thirty-fifth session — recorded
  so the implementing lane's brief carries the GOAL, not just the letter):
  the five requirements are GUIDELINES, not a checklist, and following them
  blindly is the named failure mode (per-line quota comments that echo
  code, renames that add length without comprehension). The goal they
  serve: a READER can understand what the emitted code is doing — there is
  an EDUCATIONAL aspect. The acceptance question for every individual
  commenting/naming decision is "does this help a competent C programmer,
  new to regex engines, understand what is going on here" — density and
  altitude follow from that answer, in both directions: self-evident code
  correctly gets NO comment; a genuinely subtle mechanism may deserve a
  fuller explanatory block than any per-line rule would produce.
  Consequences: (a) the one-sample style approval judges EDUCATIONAL
  quality against this goal, not format compliance; (b) the implementing
  lane is judgment-heavy work, not mechanical transcription — model choice
  accordingly; (c) manager PROPOSAL for the sample stage (not ruled): a
  top-of-artifact "how this matcher works" overview block as the natural
  home for machine-shape orientation and the state legends; (d) the lane's
  brief must quote this clarification alongside the five requirements.
  SAMPLE STAGE APPROVED (Frank, 2026-08-21, on lane/m6read 61f0209's
  exemplars — "look fantastic"), with ONE COSMETIC RULING: section/block
  comments stay `/* */`, LINE comments switch to `//` (stands out
  better). Approval ratifies the samples' embodied judgment calls
  (README §2's five: local param renames with the frozen ABI block
  untouched; rx_L labels kept with legends; the five new emitted
  macros and no state enum; developer commentary kept under the reader
  layer; decimal byte literals with consume-comments) — none was
  separately overruled. Frank's VM-sample observation (a literal
  sequence matched byte-at-a-time rather than one strncmp) is the
  [OPT-A] literal-run-coalescing lead HE recorded 2026-08-18, re-surfaced
  by the readable artifact — see that row; no new work item here.
  NEXT: the emitter conversion per the sample README §5's plan, FIRST
  landing the non-vacuous replacement for run_ir_listing.sh's
  prose-grep (the vacuous-pass hazard the sample stage found), watched
  failing, before any renaming.
  SCOPE RULED (Frank, same day, answering the manager's calibration
  question): the artifact explains ITSELF — "it's not comp-sci 101", no
  general regex-engine pedagogy. Frank's frame, recorded as the working
  standard: readers coming from higher-level languages lose the LARGER
  PICTURE in C's nuts and bolts — the commentary's job is restoring the
  altitude C strips away, i.e. saying what a higher-level language would
  have let the code say itself ("this block is the candidate scan", "this
  table maps byte-class to next state"), never teaching engine theory.
  The (c) overview proposal is re-scoped accordingly: an orientation map
  of THIS artifact's sections and match-attempt flow, not a regex-engine
  primer; still brought to Frank at the sample stage.

- [TT-3] STATE:completed (CLOSED 2026-08-21/22, merge ee57668: verdict NO for make test — plain 7:16 / cold 32:01 / warm 29:48 at a real 64.6% hit rate, per-call overhead x ~20k tiny compiles beats 12-core parallelism (workload shape, not wiring); qualified YES for mech rows (25-29% warm on single-row samples, cross-sabotage unmeasured with reasoning documented); wiring merged as opt-in CCACHE=1 off-by-default, toggle-off byte-identity PROVEN, D45 controls verified cold+warm; two-blocker diagnosis (compile+link shape; -I temp paths + -g CWD hashing) in docs/testing.md "Compile caching"; predictions REFUTED for the suite, the honest-no outcome the charter allowed) — formerly STATE:not-started (CHARTERED by Frank 2026-08-21, thirty-fifth
  session, from the test-timings discussion; runs NEXT when a lane is
  available — prerequisite DISCHARGED same day: Frank installed ccache
  4.12.3) — COMPILE-CACHING THE SUITE. The suite's cost driver is
  gcc compiling generated C (full `make test` 7m16s at 20,775 cases;
  the five-stage battery ~65 min; full mech ~50 min at PROCS=4 —
  measured 2026-08-21), and that compilation is deterministic in its
  inputs, which the identity-gate discipline already proves stay
  byte-identical for most artifacts under most changes. Wire ccache
  onto BOTH compile paths (the tree build and the GENCFLAGS
  generated-artifact path in tests/lib/gen_timeout.sh's gen_cc), as an
  OPT-IN toggle in the house style (a plain `make test` without the
  toggle must behave exactly as today). CACHE COMPILATION, NEVER
  VERDICTS: every test still executes and every verdict is computed
  fresh; verdict/skip caching is explicitly out of scope (it caches
  conclusions). TWO RULED CAVEATS travel as design items, not
  footnotes: (1) D45's gen-timeout POSITIVE CONTROL (the compile that
  must actually time out) and anything that MEASURES compile time gets
  CCACHE_DISABLE or a content salt — a cache hit would make the
  wrapper's control vacuous, the checks-going-vacuous class; (2)
  nothing timing-flavored (bench, gate, M2.9-territory compile-time
  budgets) is ever cached. DELIVERABLE IS A MEASUREMENT, not a claim:
  cold/warm before-after table for `make test`, one full mech row,
  and the battery's ubsan stage, on a quiet box; land only with the
  table (predictions on record: test 7m -> 1-2m, mech 50m -> 5-10m —
  refute or confirm). Disk bound stated and checked (cache size cap;
  the box has ~46G free). Update docs/testing.md's tier table and the
  stale "make mech ~6-7 minutes" figure in the same change

- [SR-11] STATE:completed (CLOSED 2026-08-22, merge 70650b2: tests/lib/table.sh is the one implementation of docs/spec/table_contract.md; all four consumers converted with resolution-failure poisoning; HEADER TRUTHFULNESS and GENERATOR AGREEMENT checks landed and sabotage-validated end-to-end through the real consumers; section-scoped validation at pre-change figures; the lane self-caught a pipeline-status-swallowing bug in its own library — lesson 9 self-applied) — formerly STATE:not-started (CHARTERED by Frank 2026-08-21, thirty-fifth
  session, from the D65 format-consumer breakage: "if it was meant to be
  read, it might be prep'd for it — #comments are ignored and a
  #header:col1 col2... row". PART 1 DONE same day: the contract is
  WRITTEN and GENERALIZED to every tabular command — docs/spec/
  table_contract.md covers --list-syntax AND --list-verbs, rules
  producers (# comments, header-names-columns, append-only, no tabs in
  fields) and consumers (resolve by name; trailing-safe; count only as
  header-equality), and declares future table commands adopt it AT
  BIRTH; --emit-ir moved to TO-BE-CONSIDERED on [DD-8]; sections added
  same day. Remaining here: parts 2-3, consumer conversion + the two
  checks, per the doc. RULED ADDITIONS (Frank, 2026-08-21 evening):
  (i) the conversion lands as TEST LIBRARY FUNCTIONS — one
  implementation of the contract in tests/lib/ (comment-skip, header
  name->index resolution, section selection, header-truthfulness
  assertion; shell for the awk consumers, and compliance_section.py's
  parse routed through the same contract semantics) that every
  consumer CALLS instead of hand-rolling the format at each site —
  "the test code ties to the spec": the library cites and implements
  docs/spec/table_contract.md, so a future format feature (e.g.
  sections) is implemented ONCE, in gen_timeout.sh's one-rule pattern;
  (ii) VALIDATION SCOPE: not the full suite — the affected sections
  (test-reject, test-cli, test-registry) plus the contract's own
  checks are the merge bar) — THE DUMP'S SELF-DESCRIBING CONTRACT.
  `--list-syntax` ALREADY emits `#` comment lines and a `#kind<TAB>...`
  header row naming every column; what is missing is the ruled CONTRACT
  and conforming consumers. Three parts: (1) DOCUMENT the contract where
  the dump is specified (# lines are comments; the last # line before
  data is the header naming all columns in order; columns are APPENDED
  only, per SR-4; consumers MUST resolve columns by header NAME, never
  by hardcoded count or bare position); (2) CONVERT the in-tree
  positional/count consumers to header-name resolution — the
  tests/reject iterator and cli case10 (their NF != 16 fix was the
  minimal repair, this is the durable one: awk builds a name->index map
  from the header row; case10's integrity check becomes "every row's
  field count equals the HEADER's declared count", strictly stronger
  than any hardcoded number), plus check09's cut -f4 while there;
  (3) a CHECK that the header row itself stays truthful (column count
  in header == column count in every row — which case10's converted
  form IS; and compliance_section.py's COLS list cross-checked against
  the emitted header, so the generator and its checker cannot disagree
  silently). EVIDENCE FOR THE DESIGN: the complete format-consumer
  survey in registry_built_status_memo.md's Correction section —
  spec_mod0's header-deriving loader (written blind, years early) was
  the only shape-robust consumer and survived D65 unchanged; the two
  hardcoded-count consumers broke. Sonnet-sized; no dependency;
  schedule with the next test-infra window

- [DOC-DRV] STATE:completed (CLOSED 2026-08-22, merge fc36e5e: 90 keyed annotations (38 registry-keyed live-checked, 52 base-keyed vs an independent allowlist), per-section generated annotation blocks, --check-annotations (stale-key + render-drift) and --tension (checked-tension both directions) landed and red-cased, survey untouched per the ruled model, migration manifest complete with zero ASK rows, two pre-existing compliance_section.py bugs fixed; compliance-refresh skill flipped to LANDED with the key-based procedure) — formerly STATE:not-started — COMPLIANCE PAGE AS ANNOTATED DERIVATION
  (Frank, 2026-08-21, thirty-fifth session, from the "could the entire
  compliance page be derived from source?" discussion): restructure
  docs/pcre2_compliance.md so every derivable FACT is generated and the
  hand-written residue shrinks to the two things that genuinely require a
  human. THE THREE-COMPONENT MODEL, ruled: (1) GENERATED FACTS from
  `--list-syntax` (status/module/gating/diagnostic + the [built-status]
  column once the registry_built_status memo's implementation lands) —
  never hand-edited, SR-4's cannot-drift property; (2) the INDEPENDENT
  SURVEY derived from PCRE2's own documentation — NEVER generated from the
  registry, because its value is answering "what does PCRE2 have that the
  registry doesn't even list", and deriving it from the registry would
  certify completeness from the thing being audited (the
  controls-sharing-a-source class); (3) KEYED ANNOTATIONS — the
  hand-written measurements and judgment (OK-LIMITED qualifiers, U-list
  divergences, K-list caveats, D26 tiers, the deferral analysis), each
  keyed to the construct it describes so staleness is detectable rather
  than silent, rendered into the page by the generator. The page stays
  trustworthy through the CHECKED TENSION of independently-derived halves
  (compliance_section.py), not through full derivation. SCOPE: generator +
  checker changes, migration of ~600 lines of prose-row content into keyed
  annotations, prose shrunk to survey + judgment. THE PROCESS IS CARRIED BY
  A SKILL (Frank's ruling, same discussion): .claude/skills/
  compliance-refresh/SKILL.md defines the repeatable refresh procedure and
  its invariants, exists NOW (ahead of this row), and governs the interim
  discipline until this row lands; update its migration-status section when
  this row moves. Sequencing: after the built-status column (which lands
  first and independently); pairs naturally with it (same generator, same
  checker). The recurring failure this retires: prose rows going stale
  after waves land (three recorded instances in [M6.2] alone).
  SCHEDULING RULED (Frank, 2026-08-21, triage ruling 2): CLEARED for
  the test-infra window BEFORE [M6.4], sequenced AFTER [SR-11] (shared
  compliance_section.py); the window also absorbs the anchor-checker
  promotion into make test and the PROCS=4-5 tests/assertions
  recommendation
