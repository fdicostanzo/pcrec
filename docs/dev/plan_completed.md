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

- [SAFEKILL] STATE:completed (CLOSED 2026-08-19, thirty-fourth session, merge db8ddde: scripts/safekill — PID mode = pgid ∪ ppid-descendant tree, pattern mode narrow with pure-/proc discovery and zero subprocess spawns, unconditional self/ancestor exclusion, refuse-by-default on ambiguity, --list/--under/--cwd, audit line before the signal; phase 3 scripts/tests/safekill.test 13/13 per D48 under make testscripts, never part of make test; every brief since points at it, pkill/pgrep -f retired. ROW FLIPPED 2026-08-22 at the thirty-sixth session's wake-up — the flip was missed at merge time and sat STATE:started for three days while the tool was in daily use) — formerly STATE:started (chartered by Frank 2026-08-19, thirty-fourth
  session, on the recurring pkill-collateral class) — a SAFE PROCESS-KILL
  script in scripts/, wrapping/replacing pkill for this project's
  operational use. The incident record that charters it: the wave B lane's
  pkill -f killed a concurrent legitimate mech run (2026-08-19 journal,
  lane process note); the manager's pkill -f run_sabotage_matrix killed the
  wave C lane's live S76 matrix child HOURS after journaling that exact
  lesson (same entry, manager lessons); the standing no-pgrep-f polling
  rule shares the root ("a command line is not an identity" — two
  legitimate concurrent runs are indistinguishable under a pattern, and
  the pattern can match the caller's own wrapper shell). Three phases per
  Frank's charter: (1) problems + requirements from the record, (2) the
  script, (3) tests — per D48's shape (scripts/tests/<full-filename>.test,
  make testscripts, NEVER part of make test). Non-interactive by
  construction (agents cannot answer prompts).

## 2026-08-22 (thirty-sixth session — [M6.4.1]: the atomic-groups design survives R31)

  - [M6.4.1] STATE:completed (CLOSED 2026-08-22, thirty-sixth session: docs/design/atomic_groups_design.md APPROVED by the R31 panel at 21e173e after three rounds — panel, focused re-check, final re-check — nine HIGH refuted and closed, four new HIGH found against the revisions and closed; merged 497a28f, docs only; the design's §12 is [M6.4.2]'s brief) — formerly STATE:started — DESIGN GATE (design before code — the
    engine-touching substep). docs/design/atomic_groups_design.md answering
    PER CONSTRUCT ((?>...), *+, ++, ?+, {n,m}+ incl. {n}+ and the lazy-then-
    possessive error shape): (i) the VM lowering of the UNCONDITIONAL cut —
    what vm_cut may be reused for and what needs its own argument, in
    particular the no-trail-rewind invariant that possessify's proof licenses
    and an atomic group does NOT come with (captures written inside the body
    must still be undone on an OUTER failure; captures retained on success);
    (ii) THE HYBRID HAZARD — the default path runs the DFA prefilter on what
    is now the UNCUT language (a superset), so a DFA-reported span/start can
    be wrong under the cut while the true atomic match starts later: rule
    what the prefilter may still be used for (sound rejection; a start LOWER
    BOUND, since uncut matches ⊇ atomic matches) and what it may not (the
    span end; the start itself), and how the emitted search loop changes;
    the match-here entry's filter (assertions_design.md §6.3 / R30 E8) gets
    its own rule; (iii) engine split per the charter above — the VM-forcing
    EngineAnalysis (select_engine.c's table), the free discharge, and the
    deferred cut construction with a size estimate of what it would cost;
    (iv) interaction table: nesting, atomic inside quantifiers and
    quantified atomic groups, alternation inside, lazy quantifiers inside,
    empty body, captures inside (retained), \K \G and assertions inside,
    (?m), the existing possessify/ENG-BREP rungs meeting a user-written
    possessive (must not double-cut or mis-rung), --engine=dfa refusal
    wording per the \K precedent; (v) REGISTRY — (?> is row registry.c:623;
    the possessive suffix refusal is HAND-WRITTEN in parse.c:988 OUTSIDE the
    registry, so D65's built column cannot see it: rule how possessives
    become registry-visible (rows, a quant kind, or an explicit exemption
    with its reason); (vi) SR-8 — D59 names atomic-groups/backrefs as the
    trigger for the general engines-column consultation: decide whether
    this module builds it; (vii) D58 residue enumeration (expected: none —
    a cut is position-free — state it and say why); (viii) module gating
    and partial-enable; (ix) the identity gate (atomic-free patterns
    byte-identical with and without the module's analysis, tests/mech/
    CLAUDE.md placement rule) and the mech sabotage rows the implementation
    must add. D6 panel (R31) BEFORE implementation; revision; focused
    re-check.

## 2026-08-22 (thirty-sixth session — [M6.5.1]: the backrefs design survives R32)

  - [M6.5.1] STATE:completed (CLOSED 2026-08-22, thirty-sixth session: docs/design/backrefs_design.md APPROVED by the R32 panel at ca9beef after three rounds — eight HIGH refuted and closed, E12/E13/E15 found against the revisions and closed; merged docs-only; §11 is [M6.5.2]'s brief) — formerly STATE:started — DESIGN GATE. docs/design/backrefs_design.md answering PER CONSTRUCT (\1..\9, \10+ and the octal disambiguation rule, \g{n} \g{-n} \g{name} \g<...> where PCRE2 defines them, \k<n> \k'n' \k{n}, (?P=n), and (?J) duplicate names): (i) the VM lowering — the compare instruction, unset-group semantics (PCRE2: an unset group fails to match unless PCRE2_MATCH_UNSET_BACKREF; measure), empty-group match, backrefs inside their own group `(a\1)`, forward references `\2(a)(b)`, backrefs inside quantifiers and the trail/slot model they read; (ii) CASELESS COMPARE as D58-named residue — a new src/gen/enc/ residual entry from birth, never inline byte arithmetic in shared emitter code (today only <prefix>_next_pos exists; design the entry's signature for the UTF-8 backend too); (iii) the engine split per Frank's 2026-08-12 design note (plan.md M4 design notes): infinite-language group -> VM; finite-language group -> DFA via the expansion rewrite in the discharge socket, with the size estimate before committing that §5.2 makes the rewrite author's obligation — and whether the expansion ships in THIS module or is chartered as a follow-on with the VM-only semantics shipping first; (iv) the octal rule — PCRE2's actual context-sensitive disambiguation of \N (group count so far, \8 \9, \0dd, the 3-digit forms) measured against libpcre2 and compared with the registry's RD_MODULE_OCTAL rows (registry.c:190-215) and what the base tier already does for octal; (v) DUPNAMES, implemented here per the row: (?J) and duplicate names as multiple adjacent rows in rx_info.groups sorted (name asc, number asc), BOTH consumers on the same first-entry-of-the-name-run-whose-slot-participated algorithm, VERIFIED against libpcre2 at design time; the named-groups module's refusal (mod_modifiers.c 'J' case; mod_named_groups.c duplicate refusal) is what this replaces; (vi) the hybrid hazard — a backref pattern's DFA prefilter (if any) runs a language that is NOT a superset or subset in general: rule what the prefilter may do (likely nothing — VM-only search) per pattern class; (vii) the D27 goal-facts list (python re vs libpcre2 divergences on backrefs: unset-group behaviour, (?P=n) spelling, \g forms python lacks); (viii) registry visibility of every spelling for D65's built column; (ix) identity gate and sabotage rows. D6 panel (R32) BEFORE implementation.

## 2026-08-22 (thirty-sixth session — [M6.4]: module `atomic-groups` ships)

- [M6.4] STATE:completed (CLOSED 2026-08-22, thirty-sixth session, under Frank's autonomous-run grant: design R31-approved at 21e173e; implementation merged 69f3b93, its tier-1 miscompile found by the blinded corpus and fixed 8e4af41; D27 corpus merged c324091 at 134/134; battery all green on 8e4af41 (test 21,557/0, strict, ubsan, asan, lint); mech 99/0 undetected with S88-S101 DETECTED and the S48 anomaly resolved; gate 13/13 at load 0.39, weakest margin 1.43x (34ede2c); SR-8 built per D67; K29 fixed; U9 RULED D68 the same evening — pcrec keeps the derived semantics, deviation documented, suspected PCRE2 defect) — formerly STATE:started (STARTED 2026-08-22, thirty-sixth session, on Frank's
  standing ruling of 2026-08-21 — session reset, proceed into [M6.4] at the
  next session's start; AUTONOMOUS RUN THROUGH [M6.4] AND [M6.5] authorized
  by Frank 2026-08-22 with "journal defensively" — journal + commit at every
  stage boundary; module order 6.4 -> 6.5 -> 6.6 REAFFIRMED) — module
  `atomic-groups`: (?>...) and the possessive-quantifier spellings *+ ++ ?+
  {n,m}+ as SEMANTICS (unconditional cut, not a proof-gated optimization —
  the existing possessify pass, src/opt/possessify.c, is the mechanism
  library, not the feature); engine selection routes atomic-bearing patterns
  off the plain-DFA path (atomic changes the matched language: `(?>a*)a`
  matches nothing); the VM's RX_CUT machinery ([ENG-BREP], vm_cut in
  src/gen/emit_vm.c) is the substrate. Frank's 2026-08-12 companion note
  (above, under the M4 design notes) rules the engine answer PER-PATTERN:
  cut-constructible -> DFA (Berglund et al., cuts preserve regularity), else
  VM; the M6.4 row's VM-substrate wording is the newer ruling and the charter
  reconciles them as: the module SHIPS the VM cut as the semantics plus the
  FREE discharge (a possessive whose body already satisfies possessify's §2.2
  proof is a no-op and the pattern stays DFA-eligible — Frank's "disjoint-
  follow special case is free in both directions"), and the FULL cut
  construction is chartered as a follow-on engine row by the design gate
  with a measured motivation (engine_m4.md §5.2's discharge socket is the
  seam). Oracle: libpcre2 10.46 is the oracle of record; this box's python
  3.14 `re` supports both spellings (verified 2026-08-22: `(?>a*)a`, `a*+a`,
  `(?>a|ab)c` all decline as PCRE2 does) and is the base-tier second oracle.
  Substeps:
  - [M6.4.1] archived to plan_completed.md (completed 2026-08-22 — design APPROVED by the R31 panel at lane/agdesign 21e173e, merged 497a28f: docs/design/atomic_groups_design.md + atomic_groups_measurements/; D67 SR-8 built here; [ENG-CUT] chartered; K29 found)
  - [M6.4.2] STATE:completed (2026-08-22) (MERGED to main 69f3b93 2026-08-22 12:58 after review; THEN the D27 acceptance run found a TIER-1 MISCOMPILE — `(?:aa|a)++ab` on "aaab" answers the UNCUT language on the frames rungs (0x2/0x4) for two-exit bodies — FIX ROUND on lane/agfix (same lane): the fix + two-exit bodies under every rung in the differential with asserted floors + a sabotage row; the identity sweep OUT of make test (one-shot landing gate, its own opt-in target); S45/S63 anchors re-derived; union battery on the fixed state before `completed`. Lane `lane/agimpl` DELIVERED 2026-08-22; the row stays started until the manager reviews and merges — `completed` is a merge fact, not a lane one) — IMPLEMENTATION, one wave
    in four slices, awaiting manager review + merge. What landed: `A_ATOMIC`
    and both producers (`(?>` through a port, `X q+` through `p_rep`'s
    desugaring); the four RK_QUANTSUFFIX registry rows and THIRTEEN registry
    sites (the design enumerated eleven; a twelfth was a `const RegRow *all[4]`
    in registry_check.c whose own loop ran to RK_COUNT, found by a SEGFAULT,
    and a thirteenth was tests/cli's case10 routing sweep + case11); `vm_atomic`
    plus the four-condition LIFT with checked rung preconditions; K29 FIXED and
    ordered before the lift; SR-8 BUILT (D67) with `forces_kreset`, the [M4.7a]
    tripwire and its `\K` exception all RETIRED into it; the free discharge;
    RULE H3 at three sites; tests/atomic_groups/ (748 cases, 722 re-verified
    against libpcre2); run_atomic_diff.sh (39,326 cells x 3 arms + the discharge
    and entries sections); the byte-identity gate against a PINNED PRE-MODULE
    COMMIT; seven codegen rules; sabotage rows S88-S100; the `-fno-atomic-
    discharge` knob.
    STILL OWED AT CLOSE ([M6.4.4]'s): the canonical `run_sabotage_matrix.sh`
    figures for S88-S100 (each row carries a marked PREDICTION today — the
    lane never runs the matrix), and the compliance page refresh.
    TWO THINGS THE MANAGER MUST RULE, both raised with evidence in the lane's
    report: U9 (now REACHABLE for the first time, pcrec agreeing with python and
    a hand derivation against libpcre2 — held in tests/known_fail/u9_atomic.rxt
    rather than decided by the lane), and three places the approved design is
    WRONG where the lane deviated deliberately (possessify's `pss_walk` is NOT
    transparent to `A_ATOMIC`; the free discharge is UNSOUND for a lazy body;
    the STRATS stamp must read the emitted shape, not `Ast.possessive`).
    POST-MERGE FIX ROUND, lane `lane/agfix` from 69f3b93 (2026-08-22, delivered;
    the manager reviews and merges): [M6.4.3]'s BLINDED corpus, run against the
    merged module, found a TIER-1 MISCOMPILE this row's own 748 cases and
    39,326-cell differential were green over — `(?:aa|a)++ab` on "aaab" gave
    (0,4) against libpcre2's and python's NO MATCH, on every frames rung, in
    every mode. ROOT CAUSE: `vm_atomic` emitted the atomic body with the
    caller's follow-min still in force, and the possessive rungs turn that into
    a loop bound ("one more iteration plus the follow does not fit" -> exit),
    which is answer-preserving only while a retreat to that exit still exists.
    THE FOLLOW DOES NOT CROSS A CUT: `v->fmin`/`v->fdyn` are now scoped to zero
    for the whole atomic body, on both routes out of `vm_atomic`. The corpus
    gap was UNIFORM and nobody had noticed it — every `cut` pattern in the tree
    had a follow disjoint from its body's first set, so the early exit always
    landed where the follow failed anyway. Closed by class `cut2`: 30 patterns,
    two-exit bodies under overlapping follows, all five possessive rungs
    (0x1f ASSERTED from the artifacts), its own non-vacuity floor (30/30, kept
    SEPARATE because the old floor cleared 15 without them); possessive.rxt
    section 10; sabotage row S101 — the only row in the matrix whose defect
    SHIPPED. Also in that lane: the identity gate moved OUT of `make test` to
    the opt-in `make test-atomic-identity` (§11.2/§14 item 8's ruled one-shot
    landing gate), and THREE stale sabotage anchors re-derived from live source
    (S45, S63 and S90 — the tripwire's second and third live catches).
  - [M6.4.3] STATE:completed (2026-08-22) (AUTHORED 2026-08-22 11:4x on branch agd27 44ae045; CORRECTED 464ab1f after the first acceptance run — 15 corpus-side cells, the miscompile cell untouched; vs main 69f3b93 133/134 (the miscompile); vs the FIXED main 8e4af41 134/134 — merges into tests/atomic_groups/d27/ after the battery — 8 files / 113 patterns / 137 cells, oracle.py 137/137 reproduced by the manager, nothing in GOAL_FACTS found wrong; acceptance run against the merged module at [M6.4.2]'s merge review (69f3b93); cell agd27 created from main 59cbbda; allowlist docs/testing.md + docs/spec/match_api.md + the docs-side pcre2_ctypes.py + GOAL_FACTS.md = the approved design's Appendix B) — D27 BLINDED CORPUS (scripts/mk_d27_cell.sh;
    author denied src/ and tests/; written from the PCRE2 goal; may be
    AUTHORED IN PARALLEL with [M6.4.2] since the author never sees the
    implementation; run against the shipped module at merge review for a
    0-divergence acceptance record that stays as authored).
  - [M6.4.4] STATE:completed (2026-08-22: battery + mech + gate + tripwire + D27 run + archive, this entry) — CLOSE: union battery + quiet-box gate +
    full mech matrix + anchor tripwire, archive, row -> completed and
    archived to plan_completed.md, [M6.0] milestone updated, journal +
    wake.md rewritten.

## 2026-08-22 (thirty-sixth session — [M6.5]: module `backrefs` ships)

- [M6.5] STATE:completed (CLOSED 2026-08-22, thirty-sixth session, under Frank's autonomous-run grant: design R32-approved at ca9beef; implementation merged 3aa446f with three measured design corrections accepted; D27 corpus merged at 207/207 — zero implementation divergences; battery all green on 3aa446f; mech 118 rows / 0 anomalies / 2 undetected at 5edba64 → S107 corpus gap closed + DETECTED, S108 RETIRED as measured-unobservable → 117 scored rows, 0 outstanding; gate 13/13 at load 0.36, weakest margin 1.43x (41e541a); SR-8 consumed per D67; U9 ruled D68 the same evening) — formerly STATE:started (DESIGN GATE STARTED 2026-08-22, thirty-sixth session, under Frank's autonomous-run ruling of the same day; the design gate runs IN PARALLEL with [M6.4]'s — disjoint modules — but LANDING ORDER stays 6.4 -> 6.5: the first implementation of engine_m4.md §5.2's discharge socket belongs to [M6.4], and this module's finite-language expansion is the socket's SECOND customer, written against whatever shape [M6.4] lands) — module `backrefs`: VM-forcing (a backref is not DFA-representable); numeric \1..\99 with the octal disambiguation the parser's refusal already hints at, \k spellings, (?P=n) once named-groups is in; CASELESS BACKREF COMPARE is D58-named residue — routes through a seam entry from birth. DUPNAMES DECISION POINT LIVES HERE (Frank, 2026-08-18, thirty-third session): (?J)/duplicate names are IMPLEMENTED with this module's by-name resolution machinery, not merely re-decided — ruled semantics: duplicate names appear as MULTIPLE adjacent rows in rx_info.groups, sorted (name asc, number asc) — the within-run number tiebreak D59 left unpinned, pinned now — and BOTH consumers use the same algorithm, 'first entry of the name-run whose slot participated': the caller walking the reflection table, and the emitted \k<name> resolution (which is PCRE2's own documented first-set-by-number behavior — verify against libpcre2 at design time per house discipline). The reflection half is nearly free (bsearch = first-of-run); the match-time half is VM machinery designed WITH \k<name> anyway. (?J)'s refusal stays truthful until this lands; the 'J' revisit trigger in docs/pcre2_compliance.md's deferral analysis points here
  Substeps:
  - [M6.5.1] archived to plan_completed.md (completed 2026-08-22 — design APPROVED by the R32 panel at lane/brdesign ca9beef, merged; docs/design/backrefs_design.md + backrefs_measurements/; publish-at-close, the seam's second entry, transitive erasure gate, dupnames resolution measured)
  - [M6.5.2] STATE:completed (2026-08-22) (2026-08-22 16:4x, opus lane/brimpl from 5286265 — implements the approved design ca9beef per its §11; [M6.4] closed) — IMPLEMENTATION (after [M6.4.2] merges; implements the approved design ca9beef per its §11; S-BR12 unvalidatable until SR-8 lands; the --engine=dfa second-why fix and the built-tally assertion arrive with [M6.4.2]). AUTHOR NOTES AT SIGN-OFF (2026-08-22): §13 P-11's tally prediction (built 33→47, unbuilt 61→49, 102 rows) assumes §9's preferred `\g<`/`\g'` split lands — §9's fallback (b) changes the number for a reason that is NOT a defect, so a red tally is read against that first; S-BR12 (no detector until SR-8) and the --no-captures slot-retention ruling (§6.3/§10) are design ASSERTIONS with no measurement behind them — the implementation measures both.
  - [M6.5.3] STATE:completed (2026-08-22) (AUTHORED 2026-08-22 17:0x on branch brd27 9c3f9aa; ACCEPTANCE vs the merged main 3aa446f: first run 193/200 with ZERO implementation divergences (seven corpus-side cells — three stranded features lines, three vacuous enabled-direction perr, one dup); CORRECTED 672a2f4 → 207/207, pending-vm 0; merges into tests/backrefs/d27/ in the pre-mech window — 8 files / 94 patterns / 183 oracle checks (63 group lines written as `gp`: asserted when the artifact delivers the slot; the acceptance run's pending-vm count must be 0), oracle.py 183/183 reproduced by the manager, nothing in GOAL_FACTS found wrong; HELD for the acceptance run at [M6.5.2]'s merge review; cell brd27 created 2026-08-22 16:4x from main 5286265; allowlist docs/testing.md + docs/spec/match_api.md + the docs-side pcre2_ctypes.py and br_oracle.py + GOAL_FACTS.md = the approved design's §12; sonnet author in parallel) — D27 BLINDED CORPUS, authored in parallel with [M6.5.2].
  - [M6.5.4] STATE:completed (2026-08-22: battery + mech + gate + tripwire + D27 run + archive, this entry) — CLOSE (battery + gate + mech + archive; row archived; [M6.0] updated; journal + wake.md).

## 2026-08-24 (thirty-eighth session — [M6.6]: module `lookaround` ships; archived 2026-08-25)

- [M6.6] STATE:completed (MODULE `lookaround` SHIPS 2026-08-24 ~09:4x — 18 spellings built (6 primaries + 12 aliases), 3 refusals each a PCRE2 fact, lookbehind fixed-per-top-level-branch with variable refused, VM-only per the ruled design, the D70 union + the family field + the substitution driver + K30 landed en route; every wave byte-identity-gated, full matrix 137/0/0 at close, the blinded corpus 1,819/0. DESIGN GATE OPENED 2026-08-23 13:2x on Frank's "how about some design for the next lane" while the [TT-6] battery ran; implementation NOT cleared until the design is panel-approved and Frank says go) — module `lookaround`: last on purpose (hardest; likely its own design gate before code). Lookbehind's back-step is D58-named residue — a seam entry, never raw `pos - k` byte arithmetic in shared emitter code. Substeps:

  - [M6.6.1] STATE:completed (APPROVED 2026-08-23 at 46868d6, merged 9fced73: docs/design/lookaround_design.md 2,756 lines + lookaround_measurements/ (10 probes, archived outputs); R33 three rounds — 25 findings (5 HIGH, incl. the fmin/fdyn follow-scoping miscompile class and the accept-pruned Σ*·L sizing), 12 verifier findings against the revisions (3 blocking, all text), 0 outstanding; reviews/2026-08-23-r33-lookaround-design.md is the record; 18 spellings ship / 3 refuse; lookbehind fixed-per-branch ships, variable refuses; VM-only semantics, DFA deferred to [ENG-LOOK]; §14's five ASKs await Frank; [M6.6.2] NOT cleared unprompted) — formerly STATE:started — DESIGN GATE (lane/ladesign, opus). AMENDED 13:5x (Frank): charter item (iv)'s DFA-eligible subset is RE-SCOPED — NO one-character fold; engine selection is VM for semantics now, and the DFA answer is [ENG-LOOK]'s product construction (see that row); the design states the prefilter-soundness argument and the VM body as a self-contained sub-program (DD-14's call target), and hands [ENG-LOOK] the sizing inputs (component automata sizes for the expanded assertion corpus and the lookaround population). docs/design/lookaround_design.md answering PER CONSTRUCT, every claim marked MEASURED (a probe against libpcre2 10.46 via the house ctypes oracle, or a pcrec artifact on HEAD) or ASSERTED: (i) THE CONSTRUCT TABLE — (?=X) (?!X) (?<=X) (?<!X); PCRE2's alpha spellings (*pla:X) (*positive_lookahead:X) (*nla:) (*negative_lookahead:) (*plb:) (*positive_lookbehind:) (*nlb:) (*negative_lookbehind:) and the NON-ATOMIC forms (?*X) (?<*X) (*napla:) (*naplb:) — which ship, which refuse with "requires module" (D26 tier: a construct's EXISTENCE and owner are exact, its diagnostic wording is not); the LOOKBEHIND LENGTH RULE as PCRE2 10.46 actually implements it (fixed-length alternatives of DIFFERENT lengths are legal; variable-length lookbehind bounded by max_varlookbehind since 10.43 — measure what 10.46 accepts and rule the pcrec subset: fixed-per-alternative ships, variable-length refuses or ships, with the reason); quantified lookaround ((?=a)* and friends — PCRE2's special handling); nested lookaround; lookaround containing backrefs, atomic groups, \K (PCRE2 ≥10.38 REFUSES \K inside lookaround by default — measure, rule), captures inside POSITIVE lookaround (retained after success) vs NEGATIVE (discarded), captures inside lookbehind; the degenerate (?=) (?!) forms; lookaround at pattern start (prefilter interplay) and end; (ii) THE VM LOWERING — lookahead as an ATOMIC sub-match: save pos + frame depth + capture snapshot, run the body, on success CUT to the saved depth (RX_CUT substrate, vm_cut in src/gen/emit_vm.c) and restore pos (positive) / fail (negative); on failure fail (positive) / succeed with pos and captures restored (negative); lookbehind as BACK-STEP-then-forward-body-with-END-CHECK (PCRE2's shape: for each alternative of fixed length k, step back k CHARACTERS, run forward, require the body to end exactly at the original pos) — the emitted code with labels, the trail/slot interactions (the trail restores OLD slot values on backtrack, backrefs_design.md §3.7's model), the step/frame budgets (D42.6: a lookaround body's steps count; empty-iteration guard when a lookaround sits under a quantifier); (iii) THE BACK-STEP as the [M5-SEAM]'s THIRD residual entry (src/gen/enc/enc.h's PcrecEncEntry: id, engine_callable, decls/defs) — signature designed for the UTF-8 backend (k characters, not bytes; what happens at start-of-subject), the D58 record of the seam change, the [M5-SEAM] codegen check's population (backrefs_design.md §4.4's P14 precedent); (iv) ENGINE SELECTION — registry rows VM_ONLY by default (APPROACH §: lookaround is VM), EXCEPT the DFA-ELIGIBLE SUBSET that D66 needs: a ONE-CHARACTER fixed lookaround whose body is a single class (`(?<=\n)`, `(?<!\w)`, `(?=\w)`, `(?!\z)`-shaped end forms) IS the assertions module's alphabet-context assertion (waves B/C) — design the RECOGNIZER (which shapes, where in the pipeline, how the identity gate proves it is a no-op for today's population) and rule whether M6.6 SHIPS it or hands it to [DD-11] with the door built; the PREFILTER SOUNDNESS argument: dropping any lookaround from a pattern yields a SUPERSET language, so the hybrid's DFA prefilter may run the lookaround-erased pattern — state it, then MEASURE it on the candidate-start population (the hybrid's planted-window hazard from backrefs_design.md §11.2 is the precedent for how a "superset" can still change an answer: check the match-START semantics, not just membership); (v) THE D66 HAND-OFF — what the core lookbehind-anchor form needs from this module (the one-byte lookbehind lowering to the context mechanism; the (?m)^ ≡ `\A|(?<=\n)(?!\z)` self-oracle: expansion vs folded implementation as an in-tree differential — design the CHECK's shape even if DD-11 builds it); (vi) THE D27 GOAL-FACTS LIST — python 3.14 `re` vs libpcre2 divergences on lookaround (python REQUIRES every lookbehind alternative to have the SAME fixed width — `(?<=a|bc)` is a python error, legal in PCRE2; python lacks the alpha spellings and the non-atomic forms; python's treatment of captures in negative lookahead; quantified lookaround) so the blinded author knows which oracle rules each cell; (vii) registry visibility of every spelling for D65's built column (SR-8 generic capability check will CATCH rows lacking witnesses — the backrefs precedent); (viii) the identity gate (byte-identity of every pre-module artifact on three axes against a pinned pre-module SHA, the positive control refusing every lookaround pattern) and the sabotage rows (each claim one row; the two-site mechanism exists if a claim needs it); (ix) the size of the module's construct population for the blinded corpus and the acceptance run. Premises RE-VERIFIED on HEAD (the refusals, the assertions context machinery's actual shape in src/, the VM cut's actual interface). D6 panel (R33) BEFORE implementation; Frank says go after.

  - [M6.6.2] STATE:completed-pending-close (ALL BUILD WAVES MERGED 2026-08-24 ~07:2x — wave F at 7307741 (lane/waveF b68ca13): twelve alpha spellings as ALIAS ROWS (family = the primary's canonical syntax; la_kind resolves alias→primary so an alias has no flags of its own to be wrong about; the assignment MEASURED 84 templates × 19 subjects / 0 divergences; §8.2's VerbName-pair recommendation superseded by rows — one home, D24), D71.3's family field + --list-families (118 rows / 106 family lines; recursion joins by setting family="(?N)" on its rows + one 'at most one canonical' relaxation in check_families) + RF_INDEX (arbitrate skip placed BEFORE the REG_SEL_ANY arm — load-bearing) + S142 (registry:2fail DETECTED), D65 tally 106/58 → 118/70 with ZERO out-of-module movement (dump-diffed), K30 CLOSED (S18 1fail/454pass at BOTH widths), compliance refreshed all three components (the (?= annotation had analysed the WRONG ENGINE; [[:<:]] re-measured CORRECT; D71.4's DEFINE substitutes VERIFIED per-startpos), reject rows moved with the FORM-row claim REFUTED by a control build and replaced by four answer-level cli pins, registry_check's verb-arm segfault fixed as a named failure, mod_verbs.c's stale PURE-MIGRATION header corrected; corpus 23,049/0, gate 202 bearing / free unchanged, 29 D69 rows all DETECTED. Two waveF caveats on record: the generated index's engines column emits unescaped `dfa|vm` (pre-existing, one-line md_escape owed); --list-families has no --flavour axis (refused rather than invented — SR-7's shape stated). REMAINING FOR THE MODULE: [M6.6.3] D27 blinded corpus + acceptance, [M6.6.4] close (FULL matrix, battery, gate, archive). WAVE E2 MERGED 154141b at ~05:1x 2026-08-24: the §6.3 substitution driver — 887 patterns / 29,063 three-way comparisons / 0 disagreements (P1 263/8,260; P2 361/12,543 — the design's per-cell parenthetical understated P2 by 52%, amended; control 263/8,260 trivially equal), population EXACT vs the design's table (zero delta, asserted not floored), identity rows counted/asserted/excluded (84 = 37 \A + 47 \z), five anti-tautology controls (§0 table re-verified 2,646 cells + a 16-cell vacuity guard in the failing direction; §1b module guard; §1c cell-fidelity 8,260/0; B==C attribution 8,260/0), runtime 40 s warm — rides make test; the laexpand arm measured PER ROW (8 detected, 7 structurally blind — S131 among them: every §6.1 expansion is atomic, the design's wave-E2 bar corrected in the doc; the census in tests/mech/CLAUDE.md), the SKIP trailer renamed oracle-skipped with the failing direction demonstrated from a real log, and the lane's own witness printer found wrong TWICE (awk -v escape-processing; the fix on the wrong pipeline stage) — now a function under §1d's standing three-cell failing-direction control. Driver re-run GREEN on the MERGED tree (11/0, 16,635 lookaround-bearing comparisons) per the lane's recommendation since wave E touched emit_vm.c. WAVE F OPENED ~05:2x as lane/waveF (opus, brief scratchpad/brief_waveF.md). WAVE E MERGED 6cf861c at ~04:4x 2026-08-24: the §5.6 predicate — THE CEILING BUG WAS LIVE on pre-E main (the measured witness `((?:a(?!q)|aq)(?:xy){0,4}q)` answered NOMATCH on "aqq"; now (0,3), matching both oracles); codegen rule 1 = ceil_drop/ceil_keep over FOUR readers incl. --emit-ir's PRUNING line; prefilter.rxt (9 blocks, every clamping cell QUALIFIED against a pre-wave compiler — 5 of 10 candidates; incl. the non-atomic `(?*!` cell that separates this predicate from atomic's); S140/S141 DETECTED (S141 two-site: both builders sabotaged, stamp left reading the flag — only rule 1(a) catches it); the identity gate caught the lane's own 37-byte generated-comment regression on 54 lookaround-free artifacts (reverted; the wording wart recorded as [M4.6d] obligation (d) — a second why-flag beside mrl_win would be the two-sources defect); the `lookaround` mech arm measured BLIND to S140 (no `q` in its shared subjects — the .rxt is the detector, recorded); merge conflicts resolved by the manager, NPO guard re-derived on the merged tree = 45 (5/0 green); one unexplained one-off: run_vm_identity refusal mismatch under concurrent load, not reproducible. WAVES 0/A/A2/B+C/D/E ALL MERGED — remaining: E2 (in flight), F, then M6.6.3/M6.6.4. WAVE D MERGED e10bad4 at ~04:1x 2026-08-24: the seam's third residual entry $_back_step with ZERO interface change (P-1 held, recorded in enc/CLAUDE.md), the fixed-per-branch lookbehind (widths from the A_ALT spine filled from the END, count asserted vs AltInfo.nbr; unbounded tested before int-representability), end-check on BOTH arms (negative = hard RX_R_FRAMES by elimination — see the D71.1 wave-D note), corpus +175 blocks (22,936/0 total), [M5-SEAM] N=7 + the sentinel detector added, rows S133-S136 + S130/S125 re-homed, FULL mech 134/0/0, gate 168 bearing / 2,049 free control exact 168/168, run_lookaround_diff §1 44 blocks / 4,268 cells / 0; three lane findings: the design §3.4 sentinel-arm sketch was WRONG TWICE (amended in the doc at merge), the width-0 guard tripped -Wtype-limits (condition-gated), S134's first single-row run scored UNDETECTED because the row's detector was uncommitted while mech archives HEAD — a lesson for lanes writing a row and its detector in one wave. WAVE E2 OPENED ~04:2x as lane/waveE2 (opus, brief scratchpad/brief_waveE2.md — the §6.3 substitution driver, tests-only, launched off wave D's merge without waiting for E; disjoint from waveE except an append-shaped CLAUDE.md edit). WAVE B+C MERGED b6338f6 at 2026-08-24 ~00:3x: mod_lookaround.c's one port (three lookahead tails built, the `<` tails declined = the D65 split — --list-syntax 55 built / 45 unbuilt / 6 n/a), vm_look's three lookahead arms with §3.2.1 scoping (measured: `(?=(a+)b)a+b` prunes at 1), tests/lookaround (81 blocks / 118 cells, gen_corpus.py computes `# pcre2-only`; G8/G9 REFUTED — quantified lookaround and the capture axis are 100% python-verifiable; G5 holds), run_lookaround_diff.sh (1,022 pcre2-only cells vs libpcre2; the atomicity discriminator disagrees with itself on exactly 13 cells, asserted), rows S122-S132 incl. S128 (`\K`, in no wave's bar — the lane caught it) and S130 deferred to D, the `lookaround` mech arm, the gate's bucket split (85 bearing / 2,048 free, control 85/85, STRICT_ALL=1 demonstrated red 332 comparisons / 0 in the free bucket), corpus 22,651/0; four lane findings: S101's anchor collision (R33 V-7's prediction arriving at the EXISTING row), a D24 two-homes defect (UNBUILT marker) fixed, the SR-8 capability check re-keyed on D65's built column, a stale population guard that contaminated the first row batch (re-run clean). WAVE D OPENED ~00:4x as lane/waveD (opus, brief scratchpad/brief_waveD.md: the seam's third residual entry $_back_step + the fixed-per-branch lookbehind + end-check on both arms + S-LA6/7/8/11 + S130 re-homed). WAVE E OPENED ~00:5x CONCURRENTLY as lane/waveE (opus, brief scratchpad/brief_waveE.md: the §5.6 predicate at the v.mrl_win site, codegen rule 1 on both sources, --emit-ir's description, prefilter.rxt with the measured witness, S-LA12/13 taken from the end of the id range) — disjoint from D except emit_vm.c, second lander rebases; E2 (the substitution driver) waits for D's lookbehind. WAVES A+A2 MERGED 1187973 at ~22:4x: pcrec_maxw (PCREC_W_UNBOUNDED == PCREC_MINW_MAX, composes with the saturating arithmetic) + tests/mrl/maxw_check.c's two-sided sweep (12,637 nodes / 8,901 oracle spans / 0 violations, three sabotages caught), the A_LOOK enumerator + u.look payload, 24 walker arms (design's 23 confirmed file-for-file + maxw's; the critic's 27 = +4 default-carrying), four default: sites re-inspected SOUND, gate 2056×4 identical, full mech 119/0/0, S58 anchor re-homed; tooling defect FIXED at merge: tests/mech/rows_for.sh printed SAB_IDs the matrix FATALs on (66/67) — D69's targeted tier had never run; it now prints the file's S<id> selector. Cross-milestone obligation recorded: A_CLASS's maxw arm is exact only while UTF-8 refuses by name. WAVE B+C OPENED ~22:5x as lane/waveBC (opus, brief scratchpad/brief_waveBC.md — moves the gate's bucket-split classifier up from wave E and the `lookaround` mech arm up from F); WAVE 0 MERGED a9739e1 at ~21:2x: D70 union, gate 2056×4 identical vs pin eacac76, rd_node/mod_assertions kind-guarded, revdet_highbytes.rxt + S121, corpus 22,485/0, mech 118/0/0 + S121 DETECTED, sizeof(Ast) 104→72; WAVES A+A2 opened ~21:3x as lane/waveA (opus): pcrec_maxw + the A_LOOK enumerator/u.look payload + the budgeted walker arms + the four default: sites; 2026-08-23 ~17:1x, thirty-eighth session, on Frank's "proceed to scheduled build … proceed deliberately"; WAVE 0 = D70 union refactor lane/d70union (opus, worktree) opened first; waves A/A2 → B+C → D → E/E2 → F follow SEQUENTIALLY after D70 lands since all touch the renamed files; the identity gate is built at wave 0 as tests/codegen/run_lookaround_identity.sh in STRICT_ALL pure-refactor mode over the four ruled axes, pin eacac76; wave-0 finding at briefing: 14 mech sabotage rows anchor on the renamed field names — anchor re-homing + D69 targeted rows are on wave 0's landing bar) — IMPLEMENTATION per the approved design (VM lowering, seam entry, registry rows, engine selection, identity gate, sabotage rows, tests/lookaround/ corpus). ASK RULINGS (Frank, 2026-08-23 16:2x-16:4x): ASK 1 RULED — one A_LOOK kind AND the D70 tagged-union refactor lands FIRST as the module's opening wave (pure refactor, byte-identity gate over the full corpus; A_LOOK's payload joins the union; see D70). ASK 2 RULED (Frank, 16:5x): EMIT the end-check on BOTH arms — hard RX_R_* internal-error return on the NEGATIVE arm (a silent decline there is a false match), cheap branch decline on the positive; S-LA11 carries both a (?<= and a (?<! cell. ASK 3 RULED (Frank, 17:0x): YES — the twelve alpha spellings get their own registry/dump rows (spelling-aliases of their six primaries), full D65 built column + SR-8 witness obligations; wave F's module reattribution away from `verbs` stands regardless. ASK 3a RULED (Frank, 17:3x, after the sequencing discussion — 6.6 NOT parked for subroutines; DD-14's design gate runs alongside): the substitution driver BUILDS IN [M6.6.2] wave E2 as designed (263 patterns / 8,260 cells; test infrastructure, not a product mechanism). ASK 4 RULED (Frank, 17:4x): FOUR gate axes — default, the standard second, -fno-prefilter (isolates the §5.6 ceiling-drop conditional, the module's only touch on lookaround-free paths), --no-captures (the backrefs-precedent axis); positive control = every lookaround pattern refuses under the pinned pre-module binary. ALL FIVE §14 ASKS RULED + D70; [M6.6.2] is CLEARED TO START at the next session (Frank, this session: "we'll start implementing next session"). \K-in-lookaround: refusal PERMANENT (Frank: BSK is "bad mojo"; design §2.7 amendment carries the measured old semantics for the record). ASKs 2-5 pending Frank.

  - [M6.6.3] STATE:completed (MERGED 967d795 2026-08-24 ~09:3x: 7 files / 457 blocks / 2,408 oracle assertions authored blinded in the la27 cell; ACCEPTANCE per design §10.3 (cells/failures/triage): first run 1,849 cases / 310 failed / 71 distinct compile failures — ZERO answer mismatches, ZERO pcrec-wrong; triage classes all corpus-wrong: (1) features lines placed before their pattern (the harness attaches directives to the open block; docs/testing.md's after-pattern rule — the author's generator and checker SHARED the misreading, the check-design lesson), (2) missing module names rooted in the manager's brief naming only assertions/backrefs, (3) the §2.5 grouped-alternation boundary — `(?<=(a|ba))c` is ONE variable branch, refused, exactly the boundary the design predicted readers would get wrong, caught as a REFUSAL never a miscompile; final run 1,819/0/0/0. THE BLINDED CORPUS FOUND NO IMPLEMENTATION DIVERGENCE — the backrefs precedent repeated. Corpus lands as tests/lookaround/d27/ riding make test; the cell and la27 worktree removed. 2026-08-24 ~07:5x: cell la27 created via scripts/mk_d27_cell.sh — allowlist la_d27_extract.md (the §2+§7+§10.1 cut, committed 5ae833f) + la_oracle.py with its borrow chain (br_oracle.py, pcre2_ctypes.py) + docs/testing.md + lib/pcrec.h + prebuilt build/; author = sonnet per the brd27 precedent; brief scratchpad/brief_m663_d27.md; the acceptance run happens WITHOUT the author against the merge, every failure triaged corpus-wrong vs pcrec-wrong before any edit) — D27 BLINDED CORPUS (cell author from the goal-facts list; written from PCRE2 semantics and the design's construct table, never from src/) and the ACCEPTANCE RUN against the merge.

  - [M6.6.4] STATE:completed (2026-08-24 ~09:4x — the close ran DURING the corpus authoring, on the F-merged tree 1844a1c: FULL matrix 137 rows / undetected 0 / anomalies 0 / oracle-skipped 0; identity gate 6/0 on the four ruled axes; strict clean; make test rc=0; `make san` green both axes; compliance refreshed at wave F; the final landed-tree make test (corpus + d27 = ~24.9k cases) ran at the merge. Gate-bench re-baseline REMAINS QUEUED (archived COMPILE-SPEED/GCC-TIME numbers predate the timeout swap) — it was NOT cited by this close.) — CLOSE: battery, D69-tier mech (module close = FULL matrix), gate, compliance refresh, archive.

Note at archive time (2026-08-25): [M6.6.2]'s STATE reads `completed-pending-close`; its close was [M6.6.4] (ran during the corpus audit, completed 2026-08-24 ~09:4x), so the row is complete.

## 2026-08-25 (thirty-ninth session — [DD-14]: module `recursion` ships at D69 tier; archived 2026-08-25)

- [DD-14] STATE:completed (MODULE `recursion` SHIPS AT D69 TIER 2026-08-25 ~10:2x — design a59bbb5 (2026-08-23) → waves A 0c75c96, A2 ac4917d, B+C 67e40b9, D 3a08eae, LB 2a9dfeb, E+EMPTY 85361cd, F 514f154, D27 corpus 8da6120 (1,031 blinded cells), K34 measured 07e09aa (PCRE2's loop rule NOT adopted; 11 cells parked), G 08ddcbd (splice linkage + dead-capture elision + prefilter restored; the email specimen's factored form is ONE DFA artifact with the hand-inlined one; panel r35's E1 splice save-block sizing fixed 99eecd5), FB 17469b6 (the caller-provided frame buffer: three `_in` entries at 144 B vs 131 KB, sizing surface + _Static_asserts, abi 3; panel r36; the identity gate SPLIT: program region vs ac4917d, whole file vs 8fc1e51), mech triage ae9c98c (S155/S70 re-pointed, K37, S159), CLOSE 692c2e8. BATTERY on ae9c98c's compiler: full matrix 180 rows → headline 180 / unexpected 0 / undetected 6 (S150-S153, S160, S178) / anomalies 0 as the composite of the manager's run + three solo re-runs; make test 26,843/0 cases (the close tree: 26,560 corpus / 0; 1,536/0 checks; test-resource inline); strict; san clean both axes (manager 07:36; close lane 1h05m, 28 scripts, zero reports). Gates: three RETIRED refuse by name; recursion 15/0 at the pinned per-axis numbers. §3 1,836 cells vs libpcre2 10.46 = 0; A==B 279/322 patterns, 28,458 cells, 0. Open rows born here: [MECH-REACH], [TT-10] widened, [OS-4]'s customer, [DD-13]'s bench candidates; K36, K37. RULINGS OWED TO FRANK: K34's guard; the elision option (i); the gate exception + split; see wake.md.) — was: started

  Frank's GENERALIZED definition/insertion direction — the assertion

  family as scope-resolved definitions whose replacement values are

  inserted rx; this row's call primitive is that idea's substrate, so a

  DD-14 design must read DD-11's generalization block first) — RECURSIVE PATTERN CALLS, the design sketch

  (Frank question + manager sketch, 2026-08-18, thirty-third session;

  UNRULED territory parked at Frank's "save your notes" — module

  `recursion` keeps refusing by name until ruled in). The language is

  non-regular so this is VM-ONLY structurally (joins the forces_* rows;

  --engine=dfa refuses). THE MECHANISM: an explicit call stack of

  computed-goto LABEL ADDRESSES inside the single emitted VM function —

  push the return label, goto the subpattern's entry, pop-and-goto* on

  subpattern success. No C recursion, no interpreter, allocation-free

  with a bounded DEPTH capacity and a NEW typed give-up code (D49

  reserved below ERR_FLOOR for exactly this; the floor moves -4→-5 as a

  deliberate pre-v1 change). NOT inline expansion to depth K — that is

  bounded-repeat replication again, and K19/K22 already paid for that

  lesson; the call stack makes emitted size depth-independent (the

  revdet-rung reason). Four design questions at charter time: (i)

  per-level capture save/restore (PCRE2 semantics MEASURED, not

  recalled); (ii) call atomicity — changed across PCRE versions; if

  atomic, RX_CUT is the tool; measure 10.46, the answer picks the

  machinery; (iii) left-recursion refused at compile time (PCRE2's

  could-loop-indefinitely check equivalent); (iv) the capacity/budget

  accounting joins the D42.6 family. THE CONVERGENCE (ties D61/D64

  threads): a call to a NAMED pattern and a recursive self-call are the

  SAME primitive — once the label-call mechanism exists, match-time

  insertion is a non-recursive call to the inserted body's entry label,

  so the insertion machinery and recursion should be DESIGNED TOGETHER,

  with compile-time splicing remaining an optimization for the

  non-recursive case

  - [DD-14.A] STATE:completed (MERGED 0c75c96 2026-08-24 ~10:2x; lane/srA 3 commits 09b2769/3ca8588/9b8cfda; bars: strict clean, [ABI-NS] 18 constants, gu failing-direction demonstrated, lookaround corpus 2383/0, anchors 137/142, D69 rows 71/71 DETECTED (6 re-run on merged main after srA2's pkill), test-resource clean solo; the corpus's one red block was a load compile-timeout on the K32 cell — the merged-tree battery is the clean reading. SIDE EFFECT: the three pinned pre-module identity gates (lookaround/atomic/backref) RETIRE — their references cannot move past the ABI event; each now refuses with the reason. Was: lane/srA, sonnet) — WAVE A, the give-up code space alone: PCREC_ERR_RECURSE (-5), ERR_FLOOR −4→−5 at design §5.6 sites 1-8, the `_R_RECURSE` sentinel + search-entry propagation, the driver naming every code, the `gu <code>` harness directive (§10.3) exercised in the failing direction; PLUS (D72, CONFIRMED by Frank ~10:2x) PCREC_ERR_INTERNAL (-6) BELOW the floor and the lookbehind end-check's hard return re-pointed to it. No producer, no counter (D71.1), no frame fields (5a/5b are B+C's).

  - [DD-14.A2] STATE:completed (MERGED ac4917d 2026-08-24 ~10:4x; lane/srA2 4822297, 4 commits; strict clean, identity 2657/0, anchors resolve; D69 rows 88/88 DETECTED (single-row sweep, MECH_DONE 13:31); FOUND the u.call.body pass-ordering hazard + la_has_kreset blindness → B+C obligations. Was: lane/srA2, opus) — WAVE A2: `A_CALL` + the `u.call` D70 payload + `CallLink`; the 27 arms of §4.4a (GRAPH sites as loud placeholders until callgraph.c); `pcrec_has_call` external, unwired; the D70 survey's `u.call` answers; the eight switch-less walkers inspected; byte-identity of every corpus artifact vs main as a plain diff. Merges after A, rebased.

  - [DD-14.BC] STATE:completed (MERGED 67e40b9 2026-08-24 ~15:3x; MERGED-TREE BATTERY: make test corpus 25,217/0 every section (the one red was the D45 control catching the un-ruled GENCPU_SAN edit, fixed 06c7ee2, solo green), strict clean, san rc=0 58 min ZERO reports both axes (~16:35) — BATTERY GREEN; lane/srBC 19b3a4c, 18 WIP commits: bars — make test 25,216/0 every section, strict, san 55 min zero reports, tests/recursion 346/0 incl. --no-captures, run_recursion_diff.sh 1,632 oracle cells 0 disagreements, sibling corpora untouched, identity 2198/2198 ctl_bad 0, anchors 162/172, --list-syntax 24 (? rows built / 2 \g unbuilt, depth n=342 then frames, a×200 matches, mech 19 DETECTED / 7 expected-UNDETECTED with measurements (S150-153 S157 S160 S164) — the checked SAB_EXPECT field LANDED as the follow-on (lane/srBC-expect b6311f4, merged ~16:0x: 26 rows 'unexpected: 0' = 19 DETECTED / 7 UNDETECTED(expected), failing direction exercised on S146); refuted/amended: §5.3b axis-C premise, S-SR9a's arm, A2 obligation 1 → bind over the FINAL tree (S166 + codegen rule 3), A2 obligation 2 WITHDRAWN (\K is LEXICAL on 10.46, measured), three non-existent suite names in §9.3; cells 2-3 parked → [DD-14.LB]; cell 1 → corpus fix per P-12. Was: lane/srBC from 086624a, opus) — WAVE B+C: ports, resolver, callgraph.c (SCCs, W fixpoint, minw), RX_CALL/RX_RETURN, save/restore, the fourteen corpora, 23 sabotage rows (§11). Opens when A and A2 are merged and the battery is green.

  - [DD-14.LB] STATE:completed (MERGED 2a9dfeb 2026-08-24 ~17:4x; D+LB-TREE BATTERY GREEN: test 25,271/0, resource 19/19 solo, strict, san rc=0 45 min zero reports; lane/srLB 3b67bd3, 12 commits, +1867/−316: src/opt/postresolve.c = THE POST-RESOLUTION CHECKS pass (every rule that must refuse at an offset and needs the call graph; lookaround's fixed-width rule its first customer, the rule rendered from ONE home in the module), u.look.at, u.call.maxw/maxw_known + the maxw fixpoint; parked cell 1 compiles, cell 2 = the ruled §2.5 limit (its diagnostic corrected from a false 'unbounded' to the true '1..2' at the same offset — the fifth reject row pins that WORDING); known_fail EMPTY; inlookaround.rxt 3→21 blocks; S169-S172 DETECTED; lookaround corpus byte-identical 352/354; identity 2198/2198 + 96/96 call-bearing; make test-recursion-lbsweep 908 patterns × 22 subjects = 9,240/9,240, the over-rejection surface = exactly PCRE2 10.43+'s variable-length lookbehind; full matrix 159 DETECTED / 7 expected; five reject rows pin the refusal OFFSETS (all libpcre2's own); two reject-suite guard defects fixed in passing. Was: lane/srLB from 67e40b9, opus) — INTERIM (srLB 1d42123, ~15:5x): mechanism landed as `src/opt/postresolve.c` (`pcrec_postresolve` after `pcrec_callgraph_build`; the hook RECORDS a call-bearing lookbehind with its offset — `u.look.at`; the pass visits in ascending offset and calls module lookaround's own rule from one home, so the diagnostic bytes are identical at both timings; `u.call.maxw`/`maxw_known` + a maxw Kleene fixpoint in callgraph.c); control 354 blocks, 352 byte-identical incl. all 43 lookaround refusals; parked cell 1 now COMPILES and matches; parked cell 2 was NEVER in the shipped subset — a single variable-width branch (1..2) reached through a call, the twin of refused.rxt's `(?<=(a|bc))x` — so it lands as a RULED perr (tier 2), not a known_fail; the borrow-the-callee's-branches special case rejected (general-mechanism rule; would invert §2.4's longest-first order). known_fail returns to EMPTY. — DEFERRED LOOKBEHIND WIDTH RE-CHECK for call-bearing bodies (found by wave B+C, 2026-08-24): `la_widths` runs in the parse hook (the only place with an offset to refuse at) before `.body` exists, so `(?<=(?&g))` with a fixed-width callee is over-rejected as unbounded (tier-2, never a miscompile; two cells parked in tests/known_fail/dd14_bc_open.rxt, the ratchet fires when they pass). Charter: the hook RECORDS a call-bearing lookbehind (+ offset, a `u.look` field) instead of refusing; a pass after `pcrec_callgraph_build` recomputes widths through the graph (design §3.4(d): recursive callee = UNBOUNDED exact, acyclic = the callee's maxw) and refuses at the recorded offset. Same timing class as A2's `la_has_kreset` obligation — land together. Owner: wave D or E (manager's call at wave D's brief).

  - [DD-14.EMPTY] STATE:completed (MERGED with wave E at 85361cd: MEASURED that engine selection runs BEFORE pcrec_callgraph_build fills u.call.minw (compile.c :216 vs :235) so a root check there can never fire — the site is the EMITTER's search-entry prologue: `if (subject_length - search_from < RX_VM_ROOT_MINW) return 0;` with RX_VM_ROOT_MINW = PCREC_MINW_MAX = 2^40, a WIDTH COMPARISON not an unconditional return (saturation on a merely enormous minimum reaches the same ceiling), emitted only when the root reaches the ceiling (four corpus patterns, all call-bearing — no call-free byte moves); the two sibling cells RULED `n` via the generator's ruling form; S169 DETECTED with the predicted two-red/one-green signature) — UNIFORM ANSWER FOR AN EMPTY-LANGUAGE CALLEE (found by wave B+C): design §12 P-12 rules `minw = infinity` a legal compile meaning "no position can match"; today `^(a?(?1)b)$` answers NOMATCH in O(1) (the `a?` carries the MRL bound) while its siblings `^((?1)a)$` and the indirect cycle GIVE UP (`frames`) because no quantifier carries the bound — the answer depends on an accident of shape. Charter: the general mechanism (root-level minw = infinity → the search entry answers nomatch before any frame is pushed), the sibling cells' expectations flipped to `n` with P-12 cited, `gu frames` cells kept only for genuinely runaway shapes with a base case. Owner: wave E (engine selection is where the root predicate lives). B+C lane's refinement (2026-08-24 ~15:5x): all three siblings already have root minw = ∞ (reasoned from the `mrl_sat_add` chain + the fixpoint seed, corroborated by cell 1's emitted clamp line; NOT instrumented — instrument `pcrec_minw(root)` on the two give-up siblings FIRST, ten minutes); the mechanism is `pcrec_minw(root) >= PCREC_W_UNBOUNDED` → the search entry answers NOMATCH before any frame is pushed — one site, subsumes the quantifier case. Cell 1 now lives in leftrec.rxt as a RULED `n` cell (the generator's GU block generalised to `code=None` + a required `ruling=` citation). **[TOUR-1] ADDENDUM (2026-09-20), moved here from the 53-line essay that stood over `pcrec_minw(root)` in `src/gen/emit_vm.c`:** (a) THE PASS ORDER MOVED AND THE CONCLUSION DID NOT — since [DD-14 wave G] `pcrec_callgraph_build` runs BEFORE `pcrec_select_engine` (engine selection reads §6.3's LINKAGE), so `pcrec_minw(root)` asked there is no longer the arena's zero; the root check still belongs in the EMITTER for the reason that outlives the timing, namely that it is about what the ARTIFACT enforces at its search entry and only that emitter writes a search entry. The argument for the reorder being sound is an enumeration of who reads the two memos and when: `u.call.minw`/the character pair are read by `src/gen/emit_vm.c` (after the graph, in both orders) and by `mod_lookaround`'s parse hook (before the graph, in both orders), and by nobody in between; engine selection's only NEW read is `Ast.u.call.link`, a field the graph WRITES and selection did not previously consult at all. (b) A RETRACTED PREMISE, recorded so it is not re-derived: the emitter comment once defended that move by claiming `pcrec_possessify` calls `pcrec_minw` and so now sees a better bound — `src/opt/possessify.c` never calls `pcrec_minw` at all (grep is empty), a false premise defending a true conclusion.

  - [DD-14.D] STATE:completed (MERGED 3a08eae 2026-08-24 ~16:5x; lane/srD 85fddf6, 9 commits: the two `\g` rows carried NO_PORT — the design's 'decline branch' premise was stale — so the job was wiring aport + pcrec_brport_g's `<`/`'` arms via two mod_recursion.c exports; tests/recursion 371/0, run_recursion_diff 7/7, both `\g` rows built, S167 (S-SR15) DETECTED, backrefs corpus unchanged 662/0 + diffs green, strict, anchors 163/173, D69 27 rows all as expected, make test corpus 25,241/0 (the one red = my gentimeout control fix postdating its base), registry/reject populations ±2 as predicted, a reject pin re-pointed; tests/codegen/run_recursion_identity.sh = the wave-E SEED (default axis, pin ac4917d, 2568 patterns / 130 call-bearing / 2198 identical / 0 differing / ctl_bad 0 — its positive control caught a classifier draft that read every atomic group as a call). Was: lane/srD, sonnet) — WAVE D: the `\g` tails and the zero family (§11).

  - [DD-14.E] STATE:completed (MERGED 85361cd 2026-08-24 ~21:4x; E-MERGED-TREE BATTERY GREEN: test 25,463/0, resource 19/19 solo, strict, san rc=0 zero reports; lane/srE d69cfc2, 11 commits, +1196/−142, rebased onto post-F main with two conflicts resolved (gen_corpus.py file list; tests/recursion/CLAUDE.md where LB's closure of the parked cells superseded E's stale bullet): [DD-14.EMPTY] at the emitter's search-entry prologue (measured: engine selection precedes the call graph; a width comparison against RX_VM_ROOT_MINW = 2^40; conditional on the root reaching the ceiling — four corpus patterns; identity holds), the sibling cells ruled `n`, S169 DETECTED two-red/one-green; S157 CLOSED AS DETECTED (a deleted match via automatic possessification of the callee's `a?`, not the predicted hang; SAB_EXPECT 20/6); the prefilter predicate was B+C's (S165) — E fixed the listing's phantom flag and added prefilter.rxt (§8.2's counterexample, three doorways, unanchored); the FOUR-AXIS gate: 2610 patterns, 168 call-bearing / 2442 call-free, ctl 168/168 every axis, raw+stripped with stamp-moved a failure, failing direction demonstrated, classifier self-test 22/22 incl. F's DEFINE arm; make test 25,463/0; strict; anchors 168/178; 80 rows unexpected 0. Was: lane/srE, opus) — WAVE E: engine selection, prefilter predicate, the four-axis identity gate; D71.6 rung admission declines call-bearing bodies.

  - [DD-14.F] STATE:completed (MERGED 514f154 2026-08-24 ~19:4x; F-MERGED-TREE BATTERY GREEN: test 25,423/0, resource 19/19 solo, strict, san rc=0 zero reports; lane/srF 1ddb8a1, 11 commits: all four §8.1 families ALREADY compiled and agreed with 10.46 (18/18) — the inventory was missing, not the behaviour — landed as RF_INDEX rows (--list-syntax 118→128, families 106→90 lines, recursion rows 26→36 all built, SR-8 qualifying 66→75); the quant column wrong on THIRTEEN rows not nine (91/91 quantified spellings compile); `(?(DEFINE)` = a tailed row on `(?(` with the `)` in the tail (`(?(define)`/`(?(DEF)` are name conditions on 10.46), ANY_ENGINE (a definition is zero-width; `--engine=dfa` makes a pure DFA of a `{0}` body), lowered as A_REP{0,0} — callgraph.c/emit_vm.c gained no line; no 'non-definition body' refusal exists on 10.46 (measured); codegen rule 4: DEFINE and `{0}` spellings emit the same program byte for byte; check_index_shape_witnesses with the expected refusal DERIVED from pcrec_registry_arbitrate (the `(?01)`-vs-`(?1)` family/row distinction); RF_INDEX generalised past verbs across five surfaces; compliance refresh — the survey row had read REJECTED since B+C, now OK-LIMITED, LB's annotation re-measured (offset 9, err 125 both sides); define.rxt 12 blocks, realworld.rxt = [LIB] entry #1 (orig/factored/DEFINE agree on 85 subjects; 1 MB and deep-repetition subjects excluded pending G/FB), zerodef DEFINE twins; tests/recursion 553/0; make test 25,423/0; anchors 167/177; D69 rows unexpected 0; identity 2199/2199 default axis (the classifier learned DEFINE — the gate caught it). S-SR2a recorded as owed by [V-H]. Was: lane/srF, opus) — WAVE F: registry families (D71.3), the `(?(DEFINE)` row (D71.4), compliance refresh.

  - [DD-14.G] STATE:completed (MERGED 08ddcbd 2026-08-25 ~02:1x — lane/srG fbac26a, 49 files; panel r35: E1 splice save-block sizing fixed 99eecd5 and re-verified; bothlinkage.rxt 7 blocks/26 cells; make test on the lane 25,746/0 at d87afff, merge battery pending the sweep; 111-row D69 sweep in flight at merge time; STOPPED at 48/111 all clean after two harness reaps — NOT resumed by decision ~02:5x: one full matrix on the merged G+FB tree replaces it) — was: started (2026-08-24 ~21:5x, lane/srG from 85361cd, opus, brief scratchpad/brief_srG.md. RULING ~22:1x on the elision rule (manager, D26-derived; Frank may veto): OPTION (i) FIDELITY — dead call-only-reached groups are elided from ENGINE SELECTION only; the artifact declares them as PCRE2 reports them (MEASURED: `(?(DEFINE)(?<g>a))(x)(?&g)` CAPTURECOUNT 2, g1 UNSET, g2 (0,1)); the BAR becomes byte-identity modulo the pattern stamp AND a named ~10-line capture-declaration filter (RX_NCAPS, the unset-fill, rx_info.ngroups/nnames/groups, the name table) plus EXACT identity on the `--no-captures` axis; option (ii) (dead groups vanish) rejected as a visible tier-1 divergence. Also approved: a per-emitted-splice-site slot family for the saved W (nesting excluded by the cycle rule); no Σ* approximation arm (unreachable under 'prefilter off iff a LINKED call exists'; the spliced prefilter is EXACT). INTERIM 561adc2 ~22:2x: eligibility + composed size budget + `-fno-splice-calls` landed; discharge hoisted before the call graph (fixing a latent root-discharge drop); nfa.c inlines spliced callees exactly; dead-capture elision GENERAL (`pcrec_has_live_capture`) — four call-free `{0}` corpus patterns move VM→DFA, answers unchanged, the gate states them as an exact both-directions exception (approved); THE SPECIMEN BAR MET IN SUBSTANCE: orig/factored/factored_x all DFA + prefilter, residue = the capture declaration + RX_ALTCLS_FACTORED, every DFA-table and search-loop byte identical; the gate caught a 558-pattern unset-fill leak on its first run. INTERIM 2 ~23:1x: THE BAR IS MET — four spellings incl. a new factored_define.rx are ONE artifact past three named exclusions; 85 subjects four ways no give-up; throughput 0.88×/1.19×/0.88× of the original; A == B 15,912 cells 0; five-axis gate with the four elision patterns asserted as a pair; hazard INLINE zeros against an ERASE control that fires; §6.2 re-measured (SPLICE 855 B, HYBRID 171 B per site); S173-S177 DETECTED; S175 segfaulted the compiler → splice-depth counter in nfa.c; SR-8 witnesses asked under -fno-splice-calls (the `engines=vm` column = the linked form); S164 re-pointed at a cyclic callee (ruled) → 36e1e2e: all eight rulings discharged with numbers (filter 22/681 lines + exact --no-captures 11/11; A == B 1,836 §3 cells; elision semantic control 44/0; S178 expected-UNDETECTED; S164 DETECTED; compliance 91/91 + 128 rows); the fifth gate axis is the subject vs itself + A == B (a self-recording flag cannot be compared against a compiler lacking it — ruled); final make test + 111 rows pending) — WAVE G: the splice linkage, nfa.c's approximation, prefilter restored, `A == B` control. BAR RAISED by the email specimen (docs/design/subroutines_measurements/email_specimen/, 2026-08-24): factoring with calls is today strictly worse than the hand-inlined pattern — VM forced (the `{0}` definitions' groups are captures), no prefilter (~23× on a no-`@` MB), no rungs (a STEPS give-up on 1 MB of `a` where the DFA takes 4 ms), a frame per iteration (FRAMES give-ups ~2 K iterations in). All four have one cause (the callee is a CALL) and one cure for an ACYCLIC callee: SPLICE plus DEAD-CAPTURE ELISION — a group reached ONLY through calls (its `{0}` occurrence never matches lexically) can never leave a visible capture because the return restores every slot the callee wrote (§3.1), so engine selection may treat it as non-capturing. CHECKABLE BAR: `factored.rx`'s artifact BYTE-IDENTICAL (modulo the pattern stamp) to `orig.rx`'s — the DFA engine with its prefilter — and the 85-subject + throughput tables reproduced with the three columns equal. General mechanism (Frank's 2026-08-23 rule): 'a capture no caller can observe is not a capture' belongs in the marked-set analysis, not in a DEFINE special case.

  - [DD-14.FB] STATE:completed (CODE HALF MERGED 17469b6 2026-08-25 ~04:51 — lane/srFBc 88a22d1, 43 files; three `_in` entries at 144 B (-O2) vs 131,216 B default; sizing surface + _Static_asserts, abi 3; the identity gate SPLIT (region vs ac4917d unfiltered; whole file vs 8fc1e51) 15/0; S179-S184 detected; final make test 26,814/29 + 1,532/1 = the K31 pair, solo-green; battery on main pending) — was: started (CODE HALF: lane/srFBc from 08ddcbd, opus, brief scratchpad/brief_srFBcode.md, spawned 2026-08-25 ~02:2x under a BOX HOLD; DELIVERED 79873cb ~03:0x; panel r36 (docs/dev/reviews/2026-08-25-r36-frame-buffer-code-panel.md): no miscompile, one contract clause, the identity gate SPLIT per ruling B — program region vs ac4917d unfiltered, whole file re-pinned post-FB; batch 12c4a8c; merge pending its final make test) (SPEC HALF MERGED 0f62433 ~18:4x — lane/srFB cdea67c: frame_buffer_design.md 751 lines + match_api.md §10; the CODE half is queued after wave G, 11-item checklist + 3 cells + 6 rows + the `frames-buffer=N` harness directive. ASK-1 RULED by Frank ~18:3x = D73: KEEP 2048/3072; the buffer is the path around it; USER DOCS must carry the capacity, its implied subject size, the musl/small-stack caveat and the `_in` remedy — a [REL-META] obligation. SPEC HALF 2026-08-24 ~18:0x, lane/srFB from bf07d31, opus, docs-only, brief scratchpad/brief_srFB.md: the API shape at docs/spec/match_api.md + docs/design/frame_buffer_design.md with alternatives measured, ASK 2's stamped default calibrated by measurement, the implementation checklist; the CODE half follows wave G) — (specimen note 2026-08-24: a non-recursive `(?&x)*` costs one surviving frame PER ITERATION because a call frame is a resume frame that outlives its return (§5.1, S-SR3) — the 2048-frame default gives up ~2 K iterations in on the factored email pattern; the buffer is the remedy for genuinely recursive depth, SPLICE (wave G) for the acyclic case) D71.2 the CALLER-PROVIDED FRAME BUFFER: API shape at docs/spec/match_api.md under D40, versioning per [DD-3]; a spec lane first, then the emitter change (byte-identical default artifacts).

  - [DD-14.D27] STATE:completed (MERGED 8da6120 2026-08-24 ~22:5x: tests/recursion/d27/ rides make test — corpus 26,483/0 with it; 11 K34 cells parked under the ratchet; four empty-language-root cells RULED n; the author's tooling incl. the Perl arm lands with it; smoke/anchors/resource-solo/ratchet green on main. EXTRACT merged 461b361 ~20:2x after the manager scrubbed mechanism names from its withheld list; CELL `worktrees/sr27-cell` built ~20:3x (allowlist: the extract, the sr/la/br oracle chain + pcre2_ctypes, the two specimen .rx, testing.md, pcrec.h, prebuilt build/); BLINDED AUTHOR sr27 (opus) DELIVERED ~20:3x: 10 files, 200 blocks, 569 cases + 433 g = 1,002 expectations, a generator whose intent is oracle-checked, an independent checker, a two-arm features check (found `(?J)` needs `backrefs`), a PERL ARM (414 cells run, 403 exact, 71 spellings perl refuses, the predicted atomicity divergence MEASURED NEGATIVE, 6 divergence rows); copied to worktrees/sr27 b2a8bb3. PRE-E ACCEPTANCE 1,016/1,031: all 15 failures = K34 (pcrec `frames` where libpcre2 concludes nomatch on a runaway left recursion), 0 corpus-wrong. LANDING on branch sr27 (sr27land 1302570 + the manager's 11f5275): the 11 K34 cells parked in tests/known_fail/k34_leftrec_giveup.rxt through a generalised `parked=` in the author's generator (ratchet: still failing 1); the four empty-language-root `gu frames` cells became RULED `n` (P-12 / wave E) via guclass='ruled', the checker accepting a declining oracle only under the RULED comment; a path bug fixed in all four d27 tools; findings 1/2/4 → design/extract amendments; three CLAUDE.mds; d27 alone 1,020/0; the branch's final make test running ~23:0x, merge on green) — the blinded corpus with the PERL ARM (D71.5), M6.6.3's cell shape; the SPLICE-vs-LINKAGE self-oracle rides wave G.

  - [DD-14.K34] STATE:completed (MEASURED, lane/srK34 471f393 + the manager's R9 correction, merged ~22:4x: the rule pinned from pcre2_match.c — five conjuncts incl. the `last_used_ptr` lookahead high-water mark; 65/65 cells; the START-OPTIMIZE confound neutralised; pcrec's classes measured on the built module (the lane had run pcrec without --features all and misread the refusal as 'unbuilt' — corrected). RECOMMENDATION pending Frank's ruling: do not adopt the guard (a faithful copy threads a high-water mark through every fail site); the 11 D27 cells stay parked as OK-LIMITED's second limit kind) — PCRE2's RECURSION-LOOP RULE, MEASURED, and pcrec's answer (K34, found by the D27 author 2026-08-24): libpcre2 10.46 returns a clean NOMATCH on `(a|(?1)a)b`/"a" and `((?1)a)`/"b" (unanchored runaways), −52 on `^(a|(?1)a)$`/"aaaaab" and `^((?1)a)$`/"a" (anchored), a MATCH on `^(a|(?1)a)$`/"aaaaa" (199-deep same-position recursion with a base case), and −52 on `((?1)?a)`/"a" where pcrec matches (0,1). pcrec answers `frames` on every runaway. Charter: (1) a probe matrix over {anchored, unanchored} × {base case present/absent} × {subject matches/does not} × {recursion at the first item vs after a nullable prefix} reading pcre2_match's actual rule from its source (pcre2_match.c's recursion-loop check — cite the line) — a MEASUREMENT lane, docs only; (2) then a ruling: adopt the same rule as a GENERAL mechanism in the VM (it must preserve §3.3's 199-deep match and [DD-14.EMPTY]'s nomatch), or document the give-up as pcrec's answer (D26: a give-up is not a false answer) and keep the D27 cells parked. Blocks nothing; owed before the module's compliance page can say more than OK-LIMITED about left recursion.

  - [DD-14.CLOSE] STATE:completed (MERGED 692c2e8 2026-08-25 ~10:2x — lane/srClose 3c4b3e3, 8 commits, 41 files, NO src/ change: matrix 180 / unexpected 0 / undetected 6 / anomalies 0 as the composite of the manager's 17469b6 run + three solo re-runs (S155, S70, S159 all DETECTED); make test 26,560 corpus / 0, 1,833 checks; strict; san green both axes, 28 scripts, zero reports, 1h05m; recursion-identity 15/0 on the pinned per-axis numbers; test-recursion 10/0 (A==B 28,458 cells / 0); lbsweep 9,240/0; specimen 12/0; compliance 128 rows / 91 keys green, tension 79/177; K35 remedy in three layers (51 sites, two exports, structural sweep 62/53 with floors); doc sweep; four findings recorded (K35's follow-up wrong about the four suites — run_object_neutrality.sh:75 was the exposure; specimen 8/8→12/0 and 681→712 superseded; the `\g` doorway message has no executable pin; [TT-9] still open). Close summary: journal part 45) — was: started (2026-08-25 ~07:45 — lane/srClose from e7fa4d2 (= ae9c98c code), opus, brief scratchpad/brief_srClose.md; the battery on ae9c98c is GREEN (journal part 43); the lane owns: three solo row re-runs + the re-derived 180-row headline, gates, compliance refresh, doc sweep, K35 locale audit, residuals, the [DD-14.*] archive, the close summary) — D69-tier close: full sabotage matrix, battery, gate, compliance refresh, archive.

## 2026-08-25 (fortieth session — [M6.0] the module-milestone umbrella CLOSED; archived 2026-08-25)

- [M6.0] STATE:completed (CLOSED 2026-08-25 on Frank's ruling, fortieth session, D79: the five ruled modules all DONE and the M6 milestone is what completed the spine; post-module queue dispositions — (3)(4)(5)(7) DONE; (1)/(2) live on [DD-11] by D66; (6) is [SR-8]'s armed trigger; nothing on the row is executable from the row) — milestone (EXPANDED 2026-08-18, thirty-third session, on Frank's standing ruling). Scope per the ruled list: assertions (\b \B, \A \z, (?m) multiline, \G, \K — module `assertions`), lookaround, backrefs, atomic groups + possessive-quantifier SPELLINGS (module `atomic-groups`; the possessify OPTIMIZATION already exists internally — this is the surface syntax, which is SEMANTICS, not an optimization), named groups (module `named-groups`). PREMISES RE-VERIFIED AT EXPANSION (constraint (a); probe on HEAD b95fbe6, 2026-08-18): \b \B \A \z \Z (?m) \G \K all refuse with module `assertions`; (?= (?! (?<= (?<! with `lookaround`; \1 \k (?P= with `backrefs`; (?> and *+ ++ ?+ with `atomic-groups`; (?<n> (?'n' (?P<n> declarations with `named-groups`; (?( with `conditionals`, (?R with `recursion`, (?| with `branch-reset` — those three are NOT in Frank's ruled M6 list, their refusals stand; \d, [[:alpha:]], (?i), (?s), and mid-pattern $ all COMPILE (the 2026-08-16 row correction holds). ABI groundwork verified shipped: `rx_info.groups` (`const rx_group_entry *`, "NULL until named-groups"), `nnames`, and the `rx_group_entry` ABI type all exist in the frozen M4 ABI — named-groups POPULATES an anticipated slot, no ABI change; the groups SORT KEY is the one deliberately-unfixed spec point (match_api.md §6) and is fixed by [M6.3]. INHERITED OBLIGATIONS travelling on substeps: D47.5 possessification-gate test rides whichever wave lands (?m) — see [M6.2]; D58 seam routing — every encoding-sensitive residue (lookbehind back-step, \G advance, caseless backref compare, word-character classification for \b) routes through src/gen/enc/ residual entries FROM BIRTH, never raw byte arithmetic in shared emitter code. MODULE PROGRESS: named-groups DONE ([M6.3], 2026-08-18); assertions DONE ([M6.2], 2026-08-21, 8/8 constructs); atomic-groups DONE ([M6.4], 2026-08-22, (?>...) + *+ ++ ?+ {n,m}+; SR-8 built); lookaround DONE ([M6.6], 2026-08-24, 18 spellings + fixed-per-branch lookbehind); backrefs DONE ([M6.5], 2026-08-22, \1..\N + \g + \k + (?P=n) + DUPNAMES (?J); the seam's second entry); remaining: NONE of the five ruled modules (stale text corrected 2026-08-25 at the [DD-14] close: lookaround shipped 2026-08-24 as [M6.6]; `recursion` shipped 2026-08-25 as [DD-14] OUTSIDE the ruled M6 list). WHETHER [M6.0] ITSELF CLOSES is Frank's ruling at the going-forward conversation — its post-module queue and the D66 re-basing below are what remain on the row. POST-MODULE QUEUE (re-homed here from the [M6.2] row at its close; groupings and status as of 2026-08-21): TRANCHE A IN FLIGHT — (3) seven drifted sabotage anchors S08/S09/S21/S22/S26/S39/S65 (lane/sabanchors: re-anchored, mech validation pending), (5) wordb.rxt shard-split + PROCS note (lane/wordbshard: split done, suite validation pending), (7) heavy differentials on the sanitizer axes — DONE (kreset+gstart under BOTH axes, all four clean on first-ever sanitizer exposure, in the union chain b8cb848); the post-merge full-matrix mech on main also DONE (85/0/0 at 115fbc6), closing (3)+(5)'s verification of record. RE-BASED BY D66 (Frank, 2026-08-21) — (1) DD-7's reverse BOT variant (D63) and (2) D63's second instance (first-byte-at-offset-0, the 83x partial-anchor gap) now DEPEND ON the [DD-11] core-reduction work: optimize the CORE lookbehind-anchor form once (candidate-start derivation from a leading fixed lookbehind + generalized reverse boundary evaluation) so every desugared anchor benefits, rather than implementing against ^'s special case; sequenced behind [M6.6] lookaround + the DD-11 design — see D66 for the two answered questions and the accepted tradeoffs; (4) the registry BUILT-STATUS field — DONE (D65 ratified, implemented, merged 30f5e4b; the two missed FORMAT consumers fixed by the tail lane b7c230d with the complete format-consumer survey in the memo's Correction section; validated by the union battery b8cb848). ARMED, NO WORK — (6) SR-8's second-construct trigger
- [OPT-5] STATE:completed (CLOSED 2026-08-28 on the bench's [B11.1] loglines number, outbox O-7 item 4 — Frank: agree. THE MEASUREMENT SAID NOT TO BUILD IT AS ITS OWN MECHANISM: on mixed log text every required code unit is STRUCTURAL (`:` `.` `-` `5` present in 112/112 chunks; `"` absent in 35/112, `)` in 16/112; three patterns have none), so the precheck's value is a property of the SUBJECT BYTE DISTRIBUTION, not of the pattern (D83). Where the required byte is absent and NOT first, interp dismisses a syslog 1 MB in 18-19 µs vs pcrec's 3.2-3.6 ms scan (169-202×), but on the SEARCH BAND the precheck buys kv-quoted at most ~150 of its 501 µs (→ parity with the JIT's 335) and stack-frame 1/30th of its gap. THE CONTROL: http-5xx, whose required `"` IS the first byte, dismisses the same 1 MB in 17.6 µs = interp — the existing k=0 candidate-start skip already IS the dismissal when the byte is first. The general form that subsumes it — candidate-start derivation from ANY fixed offset k, of which "absent at every k" is the degenerate case — is [OPT-K]. Nothing under src/ was written for this row; its lasting yield is the loglines set and the D83 ruling) — formerly STATE:not-started — THE LOOP'S FOURTH OUTLIER, from the bench's
  reporter-v4 per-subject throughput rows (read 2026-08-26, inbox I-7):
  on the two FAILING 1 MB subjects (`t-b-no-at`; `t-c-long-atom-run` =
  1 MB of `a`, no `@`) pcre2-interp answers in 17.8 µs = 0.017 ns/byte
  (memchr speed: PCRE2's REQUIRED-CODE-UNIT check — `@` occurs in every
  match, absent → no match, no scan) while pcrec-auto's DFA scans them at
  3.26 ns/byte (3.42 ms, 192× slower) and pcre2-JIT at 2.45-2.70 ns/byte.
  pcrec's DFA has a candidate-START skip only (emit_dfa.c: memchr for a
  single first byte, a 256-bitmap walk for a class); both email patterns
  open with a ~70-byte class, so the start skip never skips. STEP 1,
  MEASUREMENT (sonnet, no code): the abi-6 stamps on `orig`/`factored`
  (`RX_DFA_PREFILTER` expected `byte-class`); the cost of one whole-
  subject memchr('@') over the 1 MB subjects vs the scan; how many of
  the bench's 85 compliance + 77 search subjects lack the byte (the
  precheck's hit rate on real sets). STEP 2, THE GENERAL MECHANISM (no
  special case for `@`): a REQUIRED-BYTE SET — bytes on EVERY path
  through the pattern, from the same IR walk that yields the first-byte
  set (a required byte is the dual: intersection over paths, not union);
  search entries only (match entries are bounded by the subject already
  — measure before deciding); one memchr over the remaining subject
  before the scan, and find-all re-uses the found position (PCRE2's
  `req_cu_ptr` memo) so the precheck is O(n) per subject, not per
  restart; a stamp names it (`RX_DFA_PREFILTER` gains a value or a
  sibling stamp — abi bump, four sites). Identity gate: every answer
  byte-identical (the precheck only refuses subjects the scan would
  refuse). BUILD WAITS on a number (D77): the bench's [B11] log-line
  sub-bench (mostly-failing lines) is the regime where this dominates;
  its first report, or Frank's word, opens STEP 2. Interacts with
  [OPT-3] (the transition loop's 11 cycles/byte is what the precheck
  skips) and [OPT-4] (a prefilter that scales with a count is the
  wrong prefilter — the required-byte set does not scale).
- [OPT-K] STATE:completed (CLOSED 2026-08-28 ~20:2x — BATTERY-PROVEN on the union (7603c4d code; test 1,644 checks / 0 failed under `make -k -j12`, solo clean, mech 184 rows / 0 unexpected / undetected S150-S153 S160 S178 / 0 anomalies, san green both axes rc 0 with 0 report lines, `make test-axes` 15/15 axes answer-identical incl. `-fno-offset-skip` 22,105/22,105, form census re-floored 2e97c65). abi 9 is the pin the bench gets as I-15. MERGED 7603c4d 2026-08-28 ~15:4x, abi 9 — BATTERY OWED on the union with [SEL-1]; closes on green. WHAT LANDED: src/opt/prefix_k.c (the NFA walk from `Nfa.anch_start`; offset 0 has TWO roles and two sets — the scan keeps the escape set, the verify takes frontier[0]; getting that wrong was MISCOMPILE-1, r39), emit_dfa.c's dfa_pfs gains `offset-set`/`offset-set-bounded` at the head (a selection; the k=0 forms byte-identical), `-fno-offset-skip` bit 16, stamps `RX_DFA_PREFILTER` values + `RX_DFA_PREFILTER_OFFSETS` (unconditional, D81), tuning.md §2.14, cli.md, match_api.md §6/§6.3, docs/design/offset_k_skip.md (§7.7/§7.8: the near miss — the correct set measured at 1.08-1.33× and DECLINED under the 2× bar; the model miss 192×/38×/23× predicted vs 4.5×/4.8×/7.2× measured, C_ENTER deliberately not retuned). NUMBERS (1 MB log text, 9 interleaved trials): stack-frame 10.18×/6.19×, uuid 4.45×/9.58×, iso-ts 6.13×/5.75×, needleXYZW 17.06×; controls ipv4 1.02× hex32-id 1.00× http-5xx 1.01×; ipv6/kv-quoted/bignum and BOTH email patterns declined and untouched; D82: 0 differing instructions on declined patterns, +40 B source; selected artifacts +1.4-1.9 KB, gcc +0.01 s. GATES: test-axes `-fno-offset-skip` 22,105/22,105 agree, 0 mismatches; tests/offsetskip 98/98 oracle-verified; run_offset_skip.sh 22/22 with a cross-build vacuity guard; S185-S188 (S188 = MISCOMPILE-1 restored → DETECTED 5/20 + 9/89). ALSO LANDED: run_axes.sh and axes_registry_check.sh derive the bit set with no upper bound (the hard-coded 4-15 had filtered bit 16 away before comparing), tuning.md §2's heading carries no count. OPEN (named by the lane, no row asks): the four offset-0 prefilter forms still have no deny flag of their own) — formerly (lane/optk opened 2026-08-28 ~13:2x, opus; design note first) — THE OFFSET-k CANDIDATE-START SKIP (Frank, 2026-08-28 ~13:0x, forty-third session: "agree" to the bench's O-7 ask ii; pair selection NOW, not later). THE FINDING (bench/loglines@0.1 at pin 35e1ab1, search band, set ns/call, pcrec-auto vs pcre2-jit): stack-frame 558,756 vs 17,574 (31.8× BEHIND), uuid 434,798 vs 35,766 (12.2×), iso-ts 213,267 vs 21,013 (10.1×); at 1 MB the same three 9× / 7× / 42× behind; kv-quoted 1.50× behind, bignum 1.07×; hex32-id 1.14× AHEAD, ipv4 3.56×, ipv6 4.39×, http-5xx 15.0× ahead. The JIT runs 0.08-0.15 ns/byte on the three: a SIMD scan of the FIXED-LENGTH PREFIX for its most selective byte-position PAIR (`-` at offsets 4,7 in `\d{4}-\d{2}-`; `-` at 8,13 in the uuid; `a`,`t`,` ` at 0,1,2 in `\bat `). pcrec's skip (emit_dfa.c: memchr for a single first byte, a 256-bitmap walk for a class) looks ONLY at offset 0, where all three start with a byte that is in every line (a digit, a hex digit, a letter), so the transition loop runs on every byte; the parity patterns (all-class prefixes) have no selective position and are unaffected either way. THE GENERAL MECHANISM, ONE ROW (memory `pcrec-general-mechanisms-not-special-cases`): derive, from the pattern's fixed-length prefix, the SET of (offset k, byte-set) tests every match must satisfy — the same walk that yields today's first-byte set, continued past offset 0 while the prefix width is fixed — and SELECT the k-set that minimizes the expected candidate rate under a byte-frequency prior: |set|=1 at k=0 is today's skip; [OPT-5]'s "the byte is absent" is the degenerate outcome at any k (memchr fails → no match, no scan); the JIT's pair scan is |set|=2. WHY THE PAIR FROM THE START (Frank's question, answered 2026-08-28): with a single (k, byte-set) the three outliers have NO selective position on log text — `-` at 4 or at 8 is structural (112/112 chunks), so a one-k skip fires on every hyphen and hands the loop nearly every byte; the selectivity is the CONJUNCTION. A single-k mechanism followed by a pair mechanism would be the parallel-mechanism shape the memory rule forbids. FIRST IMPLEMENTATION IS SCALAR: memchr for the rarest byte at its offset k*, verify the other offsets of the k-set at their relative positions before entering the transition loop, resume the memchr from the failed candidate; SIMD scanning of a pair is [OPT-SIMD]'s territory, measured only if the scalar form leaves a gap (D77). THE PRIOR: D83's file-general findings file when one is given (byte frequencies of the exemplar); a STATIC byte-frequency table (English text + log-line structural bytes, stated in the design note) as the fallback — the same selection code either way, the table is the only thing that changes. WHAT IS FIXED BY THE DESIGN NOTE BEFORE ANY CODE (docs/design/offset_k_skip.md, the premultiplied_dfa_table.md shape): the derivation's domain (which prefix shapes yield a fixed offset — literal bytes, classes, exact counts `{n}`; where it stops: any variable-width atom, a `\b` or lookaround at the position, alternation of unequal widths — with `\bat ` and `\d{4}-\d{2}-` and the uuid worked as examples); the cost model (candidate rate × verify cost vs the loop's ~9.5 cycles/byte on real prose — I-10); the k-set cap; how a candidate at offset k* maps back to the scan start (start = hit − k*, clamped at the subject start, and the reverse machine unaffected — the skip only chooses where the FORWARD scan begins, exactly as today's k=0 skip does); the [ENG-FORM] shape — a SELECTION over the candidate lists in emit_dfa.c (a new representation object for the skip, one accessor block), NOT a second skip mechanism beside the k=0 one (the k=0 skip BECOMES the |set|=1, k=0 case); the stamps (`RX_DFA_PREFILTER` gains a value or a sibling stamp naming the chosen k-set — abi bump, FOUR sites, D76) and the deny flag (`-fno-offset-skip`, next free bit, registered per [CHK-2]'s convention: stamp, deny flag, identity gate, structural check, sabotage row); the identity gate (every answer byte-identical; the skip only refuses starts the scan would refuse — `make test-axes` under the deny flag is the control). MEASUREMENT PLAN: before/after on bench/loglines (uuid, iso-ts, stack-frame are the exercising rows; ipv4/hex32-id/http-5xx the controls that must not move; the 1 MB fail/hit/syslog sweep) and on email-specimen@0.2 (the two email patterns open with a ~70-byte class at k=0 and have `@` at a VARIABLE offset — they must be untouched, which is the derivation-domain control); objdump of the hot loop (D82: zero cost where the skip is not selected); the new pin to the bench as an I-item. Lane: opus (engine code + design). Interacts with [OPT-3] (the loop this skips), [OPT-SIMD] (the vectorized form), [ENG-PGO]/D83 (the prior), [DD-11]/D66 (candidate-start derivation from a leading fixed lookbehind is the same derivation from the other side — the design note says whether one walk serves both).
- [SEL-1] STATE:completed (BENCH O-8 2026-08-29, the number for "predict": level-context under auto costs 510.7 ms emit-c vs 1.63 ms under `--engine=vm` on the byte-identical artifact — the 32,000-state DFA attempt is paid in full before the fallback (313×). [OPT-4]'s [SEL-1] rung (lane opt4b) reports whether the ENGINE-role exact attempt survives; if so, a knee on the exact NFA count for the engine-role attempt — the quantity [OPT-4]'s gate already reads — is [SEL-1.2], chartered on that number, not built ahead of it. Also O-8 6(d): `RX_ENGINE_WHY` is prose — a structured `RX_ENGINE_SEL` stamp rides opt4b's rung commit.) (CLOSED 2026-08-28 ~20:2x — BATTERY-PROVEN on the same union battery as [OPT-K] (above); its landing debt is the record of the row. MERGED f75a33f + landing db05020/d087733/48b6e30/029a697, 2026-08-28 — BATTERY OWED on the union with [OPT-K]; closes on green. THE LANDING DEBT, for the record — every item a test that asserted the DFA-cap REFUSAL under auto, or a control keyed on that refusal text: mech S102/S165 anchors; run_trie_identity.sh's three controls (vacuous — re-keyed on --no-captures --engine=dfa); resource ×3, [M4.5b] --no-captures, [budget] ×2 (auto twins added, WHY value discriminated, fallback population pinned at 1); K37 on --list-axes; run_axes.sh's -fprefilter documented-refusal table; and the FUZZ GATE, where the fallback shipped what the refusal used to suppress: K41, two oversize VM artifacts (2,004,449 B and 1,250,766 B) classified by SIZE and pinned at exactly 2 → [ART-SIZE]. Merge-review fix: err cleared on the retry (a successful fallback returned 0 beside the stale "too complex" text)) — formerly (lane/sel1 opened 2026-08-28 ~13:2x, sonnet) — `auto`'S CONTRACT WHEN THE DFA BUILD OVERFLOWS (Frank, 2026-08-28: agree; bench O-7 item 6, ask iii). REPRODUCED 2026-08-28 on main c60679b: `level-context` = `\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b` with `--features all` — `--engine=auto` REFUSES "pattern too complex for the DFA engine (>32000 states; try --engine=vm)" in 0.52 s; `--engine=vm` compiles in 0.00 s (runs at 1.55 ms/set on the bench vs the JIT's 115 µs — a working artifact where auto has none); `--engine=vm -fprefilter` refuses the same way (a prefilter-DFA overflow kills a VM compile too). CAUSE, STRUCTURAL: src/opt/select_engine.c chooses the DFA by feature-fit (nothing in the pattern is VM-only), src/core/compile.c:284-296 then builds it under PCREC_MAX_DFA_STATES_TABLE and src/ir/dfa.c:886 `ctx_fail`s — there is no path from a build-time cap back into selection; tuning.md §2.11 rules do-or-die for `--engine=dfa` and says nothing about `auto`. THE RULING: under `auto` a DFA cap overflow (states, table entries, the K7 element budget — every cap the DFA build can hit) is a SELECTION OUTCOME, not a refusal: the compile falls back to the VM, and a prefilter-DFA overflow under an auto-selected prefilter DROPS the prefilter; both stamped in `RX_ENGINE_WHY` / the prefilter stamp with the cap named (the bench's reporter already reads `selection changed`). `--engine=dfa` and `-fprefilter` (the FORCE forms) stay DO-OR-DIE with today's diagnostic — the user asked for that machine. GENERAL MECHANISM, not a special case: the fit feeds back — the DFA build reports "over budget" as a result the selector consumes (the selector's rung already models "cannot honour → next rung"); NO `try/catch`-shaped clause at the ctx_fail site, no second selector. The cost bound holds: the failed build is charged (0.52 s here; the K7 budget bounds the worst case at ~1 s / ~216 MB per limits.h), so the fallback compile is at most one refused build dearer than `--engine=vm` — state that number in the spec. SPEC HUNKS IN THE SAME CHANGE (D80): tuning.md §2.11 (auto's overflow clause; the two force forms unchanged) and §2.5 (prefilter drop), cli.md's `--engine` entry, match_api.md's stamp table if a stamp value is added; a known_issues.md row closes with it (K-number next free); a test in tests/cli or the tuning identity suite with `level-context` AS the witness (auto compiles, `RX_ENGINE "vm"`, WHY names the cap; `--engine=dfa` still refuses; identity of answers between the auto artifact and the `--engine=vm` artifact on a few subjects). The SECOND question in item 6 — why a bounded lazy repeat before a `\b` alternation reaches 32000 states — is a MEASUREMENT row in the K23/K32 band, filed on [DD-14]/[B11.4]'s territory, not chased here. Lane: sonnet. No abi bump unless a stamp VALUE-set changes (a new WHY string is not a layout change; the design says which).

- [CHK-2] STATE:completed (CLOSED 2026-08-28 ~20:2x — all three pieces built and battery-proven on the union (the axis registry check at 59, the sweep 15/15, the census with every value floored); (b)/(c)/(d) derivations remain filler rows when a consumer asks. PIECE 1 MERGED 17064f1, 2026-08-28 ~13:5x, lane chk2p1 — ALL THREE PIECES BUILT; the row closes on the battery: `pcrec --list-axes` (src/parse/axes_dump.c beside registry.c/syntax_dump.c; cli/main.c like --list-verbs) prints the FOURTH registry surface — 40 rows / 17 axes / 12 columns (axis order candidate kind stamp_macro stamp_value deny_macro deny_bit force_macro force_bit cli_flag applies); the six DFA axes (table, prefilter, view, seed, accept, direction) read LIVE off emit_dfa.c's DfaCand-headed arrays through six read-only accessors appended after dfa_dir_reverse (no emitted-text change, test-codegen 3/3), the eleven VM-side axes are `kind=predicate` rows stated from lib/pcrec.h's enum symbols via a stringifying macro (a rename breaks the build) — NO candidate-list-as-data exists for them yet, which is the honest census of where [ENG-FORM] has and has not reached. THE REGISTRY CHECK tests/registry/axes_registry_check.sh (PC-3's shape, wired into make test-registry → make test; 53 named checks): dump vs tuning.md §2.N headings + cli/main.c flag pairing + lib/pcrec.h bits, BOTH directions (bits 4-15), and the stamp-VALUE direction against match_api.md §6.3's tables and, for the nine D46 bit constants that live only as emitted text, against emit_dfa.c's emit_rx_abi_types literal block (two cited exceptions: RX_DFA_TABLE's mixed/none are artifact-level compositions; three rung constants have no flag of their own). Three sabotage transcripts, one named failure each, 52/53 otherwise (docs/testing.md). TWO BUGS THE WRITING FOUND: bash `IFS=$'\t' read` collapses runs of EMPTY tab fields (tab is IFS whitespace) — the tests/lib/table.sh header's own warning, reproduced live, fixed with \001 separators; and a `^\|` row test silently read the WRONG macro's value table (the tables sit indented under bullets) — output plausible, wrong, caught only by eye; fixed `^[ \t]*\|`. (b) census-from-dump, (c) test-axes-from-dump, (d) chosen-vs-possible coverage: NOT built, reported as mechanical (run_axes.sh already derives its bit map with the same awk) — filler rows when a consumer asks (D77). Merge order vs [OPT-K]'s bit 16 proven safe either way: a new dfa_pfs entry appears in the dump automatically; a wholly new axis fails the check by NAME until the predicate table gains its row) — THE OPTIMIZATION-AXIS REGISTRY + AXIS SWEEPS + FORM CENSUS (Frank: "agree with the plan for testing", 2026-08-26 ~14:4x). Today every axis gets five things by CONVENTION — a stamp read off the emitter's own predicate, a deny flag (bits 4 and up — 13 today, `-fno-offset-skip` = bit 16 joining with [OPT-K]; the checks derive the set from lib/pcrec.h with no upper bound since 2e2914e/optk's fix — a hard-coded 4-15 in run_axes.sh and in axes_registry_check.sh:317 had FILTERED bit 16 away before comparing, so the registry check's own headline assertion would have passed with the new axis absent from the dump), an identity gate, a structural check that reads the artifact not the stamp, a sabotage row — and nothing asserts an axis has all five (the abi second-site misses of 2026-08-25 are the same class of omission). THREE PIECES, in order: (1) the REGISTRY CHECK (sonnet, small; PC-3's module-registry shape): for each `PCREC_NO_*` bit assert by name that cli/main.c accepts the flag, tuning.md has its §2.N, a stamp value names the mechanism, an identity script and a sabotage row reference it; after [ENG-FORM] the code-side registry IS the candidate lists (D82) and the check reads spec against code. (2) `make test-axes` (opt-in battery stage, ~13 × 10 min, overnight, no tokens): the corpus's answers under EACH deny flag equal to default — today only 4 of 13 axes get an answer sweep (run_recursion_identity.sh's default/vm/noprefilter/nocaptures; run_codegen_tests.sh's three over eight patterns); PAIRS (78) only if a measured interaction bug ever asks (D77; none yet — K39 was single-axis). (3) the FORM CENSUS with floors (K35 for forms): count corpus artifacts per stamp VALUE and per (scan, prefilter, table) triple; a floor for every value with corpus witnesses; a REQUIRED synthetic witness for any value with zero corpus population (`"mixed"` is the likely first). Populations printed beside the verdict ([OPT-4]/K39 style).
  **PIECES 2 AND 3 DONE (lane srAxes, sonnet, 2026-08-26, branch `lane/srAxes`).
  PIECE 1 (the registry check) STAYS not-started, owned by lane srForm —
  waits on [ENG-FORM] per this row's own dependency.**
  **Piece 2 — `tests/axes/run_axes.sh`.** `tests/harness/run.sh` gained
  `RXTDUMP` (documented, threaded through PROCS>1 like RXTFLAGS/RXTROUTE):
  one line per evaluated case, so two corpus runs under different compiler
  axes diff by exact ANSWER (`tests/axes/dump_diff.awk`, keyed by
  `<file>:<line>`) rather than by pass/fail COUNT, which can agree while the
  cases that passed disagree. The axis registry is DERIVED from
  `lib/pcrec.h`'s `1u << N` constants and `cli/main.c`'s flag-parsing loop
  (never hand-copied), cross-checked live against `tuning.md` §2's own
  `"(bit N)"` headings: 12 bit-flag axes, matching 12 documented bit
  mentions. Sweeps all 12 plus `--engine=vm`/`--engine=dfa` (§2.11); the one
  documented DO-OR-DIE member (`PCREC_FORCE_PREFILTER`, bit 9) and the
  engine axis have their refusal populations printed, not failed — every
  other axis fails on ANY refusal population change. Oracle cross-check:
  `-fno-premul-table` (DFA-side, answer-identity) run through PC-4 (the
  tree's only LIVE libpcre2 match-semantics differential) via a bounded
  one-line wrapper, both plain and denied 0-failure against PC-4's own
  pinned population (273/232/62,872). DETECT DEMONSTRATION (scratch copy,
  `premul_val` off by one on the indexed form): 22 of 26 cases in
  `tests/base/alternation.rxt` MISMATCH, named individually — full
  transcript in the script's header. Validated on subsets (registry
  derivation, agree/lost/gained classification, `--engine=dfa`'s 14-of-58
  refusal population on a two-file check). **The FULL corpus sweep (~13
  passes) is QUEUED, not yet run**: box rule (one heavy suite at a time) —
  a background launcher (`/tmp/.../scratchpad/srAxes/launch_full_test_axes.sh`,
  detached via setsid) polls the manager's battery log for `"== BATTERY
  DONE"` and then runs `make test-axes` unattended, logging to
  `.../scratchpad/srAxes/full_test_axes.log`. Whoever picks this row back
  up: read that log first.
  **Piece 3 — `tests/codegen/run_form_census.sh`.** Compiles every corpus
  pattern twice (default engine; `--engine=vm` forced for the wider
  VM-only-stamp population) and counts every `match_api.md` §6.3 stamp
  value plus its two joint distributions. **Measured, RUN TO COMPLETION,
  green: 2,772 corpus patterns, 135s at PROCS=4 uncontended (checks passed:
  1, checks failed: 0).** Default: 995 DFA / 1,488 VM (1,263 hybrid / 225
  plain) / 289 refused. DFA-containing (2,258): scan unanchored 1,882 /
  attempt 368 / empty 8; prefilter memchr 1,152 / none 644 / byte-class 313
  / memchr-bounded 81 / byte-class-bounded 68; table premultiplied 1,882 /
  none 376. Triples and (engine, vm-prefilter) pairs printed in
  docs/testing.md's own section. TWO zero-population values found — `"mixed"`
  (tuning.md's own documented likely gap) and `"indexed"` (UNDOCUMENTED
  anywhere, found live by the completeness loop rather than a hand-picked
  exclusion list) — both covered by BUILT, ASSERTED synthetic witnesses
  (`[01]*1[01]{13}` for mixed; `(?:[a-z]+)@(?:[a-z]+) -fno-premul-table`
  for indexed — the deny flag itself as the controllability lever). A THIRD
  `RX_VM_PRUNE_CEILING` value ("none", 1,047 of 1,488) turned up live, not
  enumerated as a value-set table in §6.3 the way `RX_DFA_PREFILTER`'s is —
  floored as an observed fact. DETECT DEMONSTRATION (scratch copy,
  `dfa_table_name` never returns "mixed"): the census fails TWICE — the
  witness's own check and the completeness loop independently — naming the
  exact value and witness pattern. Runs as part of `make test-axes`
  (alongside piece 2) rather than `make test-codegen`, despite fitting its
  2-minute budget solo, since the two share the opt-in/heavy-battery
  placement.
  **Landing bar closed for both pieces**: `tests/axes/CLAUDE.md` (new),
  `tests/codegen/CLAUDE.md` row, `docs/testing.md` "Answer-identity sweep +
  form census" section, root `CLAUDE.md` one-liner, `docs/spec/tuning.md`
  §2 pointer (D80), Makefile `test-axes` target. `make strict` clean;
  `make test-codegen` 3/3 (a K37 static-sweep finding on this lane's own PC-4
  wrapper — an unbounded `$PCREC` on the wrapper's OWN emitted line, safe in
  practice via the already-bounded caller but K37 reads text not the call
  graph — found and fixed in the same session: `$TIMEOUT_BIN`'s resolved
  path written into the wrapper alongside `$PCREC`). Commits on
  `lane/srAxes`: ed084d2 (piece 2 WIP), 772a55f (piece 3), 9903b3f (K37
  fix). Not yet merged to main.
  **THIRD ITEM, manager-added mid-session (journal part 7 on main): `make
  test`'s own COMPLETION TRAILER, in piece 3's "populations printed"
  spirit but scoped to SECTIONS rather than to the stamp vocabulary.**
  `test:`'s recipe now invokes `$(MAKE) -k TEST_TRAILER_DIR=<dir>
  $(TEST_SECTIONS)` instead of listing the 26 sections as plain
  prerequisites (a failing section no longer stops make from LAUNCHING the
  rest; `$(MAKE)` inherits the parent's jobserver, so `-j` parallelism is
  unaffected — empirically verified with a timing toy: 4 fake 2s-sleep
  targets complete in ~2s total under the wrapper, not ~8s). Every section
  target's recipe touches a marker file as its first line, BEFORE running
  its real script; `tests/lib/test_trailer.sh` counts markers against the
  caller's own section-name argv, prints `sections ran: N/M`, names every
  missing one, and hard-fails on a zero-argument call. Validated in a
  scratch toy Makefile (never committed): reproduced the exact bug (old
  shape, `-j2`, a later section silently never runs — the "Waiting for
  unfinished jobs" the manager saw, on demand), showed the fix recovers it
  (5/5 launched, trailer confirms, overall failure still surfaces), and
  showed the trailer's own independent detection when sections genuinely
  cannot run even under `-k` (a broken shared `all` prerequisite — 0/5,
  every section named). `make strict` clean; `make test-codegen` 3/3, K37
  sweep count moved 498/83 (unaffected in kind). docs/testing.md "`make
  test`'s completion trailer" carries the full transcripts;
  `tests/lib/CLAUDE.md` gained the `test_trailer.sh` entry. Commit
  6811006 on `lane/srAxes`. PIECE 1 RE-SHAPED (Frank, 2026-08-26 ~18:5x: "can it self-report axis options for test coverage?" — yes): once [ENG-FORM]'s candidate lists exist as data, the compiler PRINTS them — `pcrec --list-axes`, a TSV in the registry's house style (docs/spec/registry.md's fourth surface): one row per (axis, candidate) in preference order with stamp, stamp value, deny flag + bit, and an applies() summary. Then (a) the registry check reads CODE against SPEC — every dumped row has its tuning.md §2.N, its §6.3 value and its CLI flag, every spec value appears in the dump — two independent sources (learnings §3), not grep against grep; (b) the census takes its universe from the dump: every (axis, candidate) the compiler can select needs ≥ 1 corpus or synthetic witness, computed not maintained; (c) test-axes derives its flag list from the dump; (d) coverage = chosen (the stamps, per artifact, over the corpus) vs possible (the dump). BOUNDARIES: the dump shares a source with the emitter, so it proves what the compiler THINKS its options are — the checks that read emitted artifacts stay the independent side; a per-artifact WHY stamp (`RX_DFA_TABLE_WHY`, the RX_ENGINE_WHY shape) is an abi bump and waits for a consumer (D77). Depends on [ENG-FORM] landing.
- [ART-SIZE.1b] STATE:completed (CLOSED 2026-08-28 ~22:0x — the final `make -k -j12 test` on 4f0c634: sections ran 26/26, checks failed 0 everywhere, `check_size_tripwire.sh: OK` as test-corpus's recipe tail (rc 2 = the known counterk load cell, 29 cases, solo 1,634/0). TWO PROPERTIES THE PROOF RUN SHOWED, for the record: under -j12 load the corpus's largest pattern (counterk.rxt:1807) times out and DROPS OUT of the log (2,874 rows, worst 465,750 B vs the quiet baseline's 2,875 / 651,344 B) — a loaded run's log is a subset, the committed baseline is the quiet one; and `make test` now REGENERATES a tracked file (docs/dev/artifact_size_log.tsv), so the tree is dirty after every run — by design (Frank: examine post-test; D35's diffable-report shape), commit it deliberately after a quiet run or `git checkout` it. MERGED 2026-08-28 ~21:3x, lane sizeratchet + manager landing; closes on one `make test` (it adds the `test-size` section). WHAT LANDED: the log at tests/harness/run.sh's existing gen_cc compile (bash `time`, SIZELOG threaded per worker and merged) at 1.79 % overhead (76.75 → 78.13 s on 712 artifacts, PROCS=2; the naive first cut was 20.4 %); tests/lib/size_count.sh (comment-excluded .c+.h, byte-exact with the census's classifier); docs/dev/artifact_size_log.tsv (D35 shape, stable name; NOT under docs/measurements/ because a check reads it) — baseline 2,875 rows at f446f1c, worst size 651,344 B (counterk.rxt:1807), worst gcc CPU 5.462 s (k18_cost_gates.rxt:103); tests/size/check_size_tripwire.sh = the ONE red (`make test-size`, zero recompiles): MAX 1,400,000 B (RULED at landing from the lane's 700,000, which sat 7 % over the max — a tripwire is for blowups, drift is size_diff's) / 8.0 s CPU / 1,500-row floor + unpinned-max guard, positional args REFUSED (the manager's first doctored-log sabotage passed `$1`, the script silently checked the real log and said OK — fixed, transcript in testing.md); scripts/size_diff (size zero-tolerance, CPU 1.25×/0.05 s thresholds; self-diff empty); sabotage: a REAL --unroll=48 compile of the largest pattern (713,076 B) tripping the 700,000 pin by name, empty/truncated logs tripping the guard, the doctored-log arm at 1.071× the shipped pin; the first baseline's absolute-path ids caught and fixed by the lane. No per-pattern pins, per Frank) — formerly (lane sizeratchet opened 2026-08-28 ~17:5x, sonnet) — THE ZERO-COST SIZE RATCHET riding the existing corpus (Frank, 2026-08-28: "zero cost size test hang-on on existing testing corpus (plus gcc cpu time test (wall test if not practical)) to track sizing blowups on future changes / future patterns"). The harness already compiles every corpus artifact once with gcc (tests/harness via tests/lib/gen_timeout.sh's gen_run); this row records TWO numbers per artifact at that site for the cost of a `wc -c` and a `time`: SIZE = emitted source bytes EXCLUDING comments (the census measured r = 0.99 against `.o` at -O2, so no second gcc pass is needed; count the self-contained form, .c + .h, per the census's own correction) and GCC CPU seconds of the compile that already happens (wall only if CPU is impractical). Then: (1) a per-pattern EXACT PIN FILE for size under tests/size/ (sizes are deterministic — an emitter change moves pins and the movement is a REVIEWED DIFF in the same commit, the abi-bump ritual's shape; the check names every pattern whose size moved, with old/new/ratio, never a shortfall count); (2) a gcc-CPU RATCHET, floor-only because time is noisy: fail when a pattern exceeds 2× its pinned CPU or half of D45's budget, with the load recorded beside the failure so a loaded box is distinguishable from a blowup; (3) corpus-level tripwires: the max `.o`-proxy and max gcc CPU pinned (the census's numbers: corpus max 675,555 B source / 6.995 s CPU); (4) new patterns entering the corpus get a pin on first sight (the check fails on an unpinned pattern with the add-the-pin instruction). Wired into `make test` with its own section marker (the trailer counts it); ~zero added runtime — say the measured overhead. SABOTAGE: plant `--unroll=64` (or an equivalent forced replication) on one pattern in a scratch run → red BY NAME with the ratio; plant a load-induced slow compile → the CPU ratchet's message shows the load. CHECK-DESIGN LESSONS apply (memory `pcrec-check-design-lessons`): the pin file is the independent side (a stored measurement, not the emitter's opinion); a pin that must be updated on every emitter change is the FEATURE (visibility), not a nuisance — the update instruction travels in the failure message. Baseline pin is measured on a QUIET box after the current battery chain (the lane polls …/scratchpad/mgr/san_rerun.log for `SAN RE-RUN DONE`); development uses targeted harness runs. FRANK'S REFINEMENT (same conversation): "or log metrics and examine post-test" — RULED: the METRICS LOG is the deliverable (one TSV per `make test` run — pattern, size, gcc CPU, load, engine/rungs stamps — archived under a STABLE filename so a re-run is a `git diff` away, D35's shape, plus a `scripts/size_diff` that reports movements between two logs by name with ratios, for post-test examination); the only RED is the corpus-level tripwire (max size and max gcc CPU pinned with generous headroom over the census's 675,555 B / 6.995 s, and an UNPINNED-max guard so the tripwire cannot go vacuous); per-pattern exact pins are NOT a gate — a per-pattern movement is a line in the diff report a reviewer reads, never a failure that every emitter change must re-pin. Report: docs/testing.md section + tests/size/CLAUDE.md.

## 2026-08-30 (forty-fifth session — [OPT-4] ruling B, the exact prefilter as the default with the count-collapsed language a ladder rescue; battery-proven on pin 96e44c2; archived 2026-08-30)

- [OPT-4] STATE:completed (BATTERY-PROVEN 2026-08-30 on pin 96e44c2 — union battery 3: san 34 scripts/0 reports, mech 189/0/6/0/0, test green after three non-code check fixes; ROW CLOSES at the session close when it moves to plan_completed.md; I-18 sent) (RULING B MERGED 0b89b23 2026-08-29 ~23:0x, lane opt4b 021b8d1: the knee DELETED with nothing replacing it — two ladder rungs, one setjmp: CR_SEL1 (state cap) and the new CR_SIZECAP (an emitted-size cap refused the exact artifact; resets the K ladder); `_LANG_WHY` five witness-driven values (`denied` dropped — no artifact can carry it); the census check deleted, the corpus sweep asserts B itself (every collapsed-at-default artifact names a rung); three of the A-era check props REVERTED (hazards restored); `--warn-emit-bytes` default 250,000, 0 disables, advisory and deliberately NOT raise-only; K39 re-scoped (count-BOUNDED at the default via the TOTAL cap — `(a|b){0,30000}` refused at 1,333,367 → the rung ships 32,297 — count-INDEPENDENT under the flag), K41 closed via the cap retry (witness 2 rescued because its artifact was too big, from a gate RUN); the K23 cell 13.34 s/`r=-2` → 0.00 s; every section green solo; FILEPIN c275aef; abi 12. UNION BATTERY 3 with [DD-11] pending the bench's window. RE-RULED 21:4x → **B, fallback-only**: the battery on 7794de9 (make test 0 checks failed after the nine landings; san 0 reports) exposed a CORPUS REGRESSION under the A default — tests/base/d27_k23_ambiguous_decomposition.rxt `(a{1,3}){65}`, stamped `count-collapsed, exact nfa 392 > 128`, TIMES OUT (>10 s) on two 120-byte broken-run subjects that passed before (the step-budget-reachability finding, note §7.2b, on an ordinary corpus pattern); it had failed in the first battery too, misread by the manager as the known counterk load cell — read failures-by-file, never assume. Frank: "go with B" + two asks: the exemplar pass may answer differently per target (→ [ENG-PGO] cross-note: a per-target `-fprefilter-collapse` chosen from the subject profile) and an advisory SIZE WARNING on builds > N, N default 250,000 (`--warn-emit-bytes=N`, a warning never a refusal). Lane opt4b implements: the knee gate and its census retire; the default builds the EXACT prefilter; the collapsed language is a ladder ATTEMPT only when the exact build is impossible — state-cap overflow (the [SEL-1] rung) or size-cap refusal (new); `-fprefilter-collapse` = always; K39 re-scoped to count-BOUNDED at the default / count-independent under the flag; K41 stays closed via the cap retry; the K23 cell passes untouched. Earlier ruling for the record — FRANK RULED THE DEFAULT 19:4x: A, the knee-128 default as built — "go with A. it can be turned off"; and: "this sounds like the kind of thing that analyzing the exemplar file with a profiling version of the pattern would answer" → CROSS-NOTE on [ENG-PGO]: the collapse decision is a PGO-informed selection point — the static knee is the default, the D83 findings file (subject run lengths, candidate-start density) is the informed override, exactly [DD-13b]'s `analysis` block family. The alternative default (collapse only when the size caps refuse) was MEASURED INERT: `emit_code` excludes table initializers, so the row moves the capped quantity by ~3 bytes on the 23 — only K41 witness 2 (computed-goto form) reaches the cap. DELIVERED by lanes opt4 (STEP 0-2) + opt4b (STEP 3 + the [SEL-1] rung + RX_ENGINE_SEL), lane/opt4 b69a331: corpus −1,874,322 code bytes over exactly 23 artifacts (60 controls unchanged), K41 witness 2 671,039 REFUSED → 152,302 ACCEPTED (gcc 66.9 s → 2.0 s, PCRE2-identical on 15 subjects), `((a)|ab){4000}c` −95.4 %; level-context 2.4-3.4× faster via the rung (artifact 22.9 → 69.4 KB, its own trade); costs MEASURED into tuning.md §2.17 (worst case 9.24 s / 99,601 attempts vs 11 µs / 1 exact; 44× on `(ab){300}` find-all; 1.49× lost ceiling; 2.7× FASTER on rejected subjects); the bar pinned by a census (plateau 117..160, band 15..28 on the sweep's 20, zero factor<2 over any bar); `_LANG` / `_LANG_WHY` (5 values) / `RX_ENGINE_SEL` (5 values, each witness-driven) stamps; abi 11 → 12 at D76's four sites (FILEPIN moved four times, one bump); K39 CLOSED, K41 CLOSED; [SEL-1.2] measured — the 507 ms is the ENGINE-role exact attempt, the rung saves none, a predictor could only decline-to-try (not built, D77). 2026-08-29 ~14:4x, forty-fifth session, on Frank's "go on all three"; lane opt4, opus, worktree worktrees/opt4 — the D86 OPTIMIZATION lane; STEP 0 measure/locate → STEP 1 design note docs/design/prefilter_count_independence.md (manager reads before code) → STEP 2 build under the identity gate → STEP 3 before/after; K41 witness 2 is the pinned exemplar, K39 closes on the measurement) — formerly STATE:not-started — (D84 CROSS-NOTE 2026-08-28: K41's second fuzz-gate witness — 1.25 MB, 92 % hybrid-prefilter jump tables, gcc inside budget — is the PINNED exemplar of this row's K39 mechanism; [ART-SIZE] STEP 2 will refuse or price it under its byte cap, this row is what makes it small.) [OPT-3] STEP 2 NOTE (2026-08-26): the hybrid's inlined prefilter is `emit_unanchored`'s own output through `pcrec_emit_dfa_engine`, so it TOOK the pre-multiplied table with no clause of its own and stamps `RX_DFA_TABLE` like any DFA artifact — this row's scan is the same loop, and a fix here does not have to re-derive the table form. The VM hybrid's inlined DFA PREFILTER scales with a bounded-repeat count (K39, found 2026-08-26 when [ENG-BREP]'s size ceiling went red by 6 lines of slack): `((a)|b){0,4000}c` 1,994 lines vs 869 for {0,400} at the default, 573 at any count with the prefilter off. Candidate general fix: build the candidate-start DFA from a count-INDEPENDENT language (the first-byte class / a count-collapsed pattern); answers unchanged (D46: the prefilter axis is answer-identity-preserving), the identity gates the control. Build when a bench row shows the cost (D77); the size checks now print the auto sizes so the number stays visible.

## 2026-08-31
- [M4-QUOTING] STATE:completed (BATTERY-PROVEN 2026-08-31 20:05, battery 7 green-by-diagnosis — test 1,971 checks/0 failed (the 29 red cases = K32's load cell, cleared solo in-battery), san rc 0/0 reports, mech: all five quoting/scan-edge rows DETECTED in the full matrix with figures matching the author-cited ones. Was: impl (5 commits incl. the p_rep in_quote fix), the blinded D27 corpus as tests/quoting/d27/ (95/95 on the fixed tree), S210/S211/S212 all DETECTED solo, compliance refreshed, rxtsource census 188/3317/26786, registry+reject+strict green. THE HEADLINE: the blinded corpus caught a TIER-1 MISCOMPILE (quoted quantifier chars live — \Qa*b\E compiled as a*b) on its FIRST run, through four green check layers incl. the impl lane's own 164-probe differential (autopsy: the quantifier-metachar-as-quoted-content axis was never enumerated — coverage bias toward axes that had already produced findings); D27's second measured tier-1 catch. Formerly: lanes chartered, S210/S211 allocated) — formerly STATE:not-started (Frank, 2026-08-30 forty-sixth session: "lets put it in the plan. i am asking for compliance than need so schedule as appropriate" — a COMPLIANCE row, not a measured-need row; scheduled as the ADMIN column's row after [LIM-1], sonnet, one lane) — THE `quoting` MODULE: `\Q...\E` literal quoting (registry rows `\Q`/`\E`, feature bit 0x0010, kind lexical, engines dfa|vm, today `unbuilt`/`planned`; a bare `pcrec` refuses with "requires module 'quoting'" — measured 2026-08-30 on `a\Q.*\Eb`; compliance doc: "pure front-end lexing; PLANNED-easy whenever wanted"). PCRE2 semantics to match exactly (D26 tier 1): everything between `\Q` and `\E` is literal (no metacharacters, no escapes — `\Q\E` inside is not an escape, `\` is literal); an unterminated `\Q` quotes to the end of the pattern; a stray `\E` is ignored (PCRE2 err 106 is only the diagnostic the registry names for the refusal tier — verify against libpcre2 10.46 which spelling it ignores vs rejects); `\Q...\E` INSIDE a character class quotes class members (the second compliance row, currently REJECTED); quoting interacts with `(?x)` extended mode (quoted whitespace is literal). Shape: a lexer state in src/parse (module hook, D5 drop-in), lowering is nothing (literals), `tests/quoting/` corpus written D27-BLINDED from pcre2pattern's "quoting" section and oracle-verified against libpcre2 cell for cell (python `re` has no `\Q` — libpcre2 is the only oracle), the registry rows flipped to `built`, the compliance refresh (`/compliance-refresh`), `--list-syntax` row count pinned, docs/spec/ hunk (D80). Acceptance: every cell of the blinded corpus agrees with libpcre2; PC-3 green; the DFA and VM engines answer-identical (test-axes); the refusal disappears from the reject table's accept-controls (find the rows that pin today's refusal — they must FLIP, not vanish).


## Completed 2026-09-06

- [K50-BNDSTART] STATE:completed (MERGED 2026-09-06 8e0fe77f, lane k50bnd, 20 commits; abi 23->24; PCREC_ERR_STARTPOS=-7 Frank-ratified same day (D97); identity gate 16/16 differing=0 all four axes; S232-S235 + startbnd arm; K50 entry FIXED with its second face; Linux full battery owed at the next slot.) (CHARTERED by Frank 2026-09-05, fifty-fifth session, at the K49 lane's escalation; SEQUENCED next engine lane after the K49 merge, BEFORE M5.0 stages 3-5 — stage 3's \p corpus would pile population onto a known wrong-answer class) — CANDIDATE STARTS ARE CHARACTER BOUNDARIES, THE DFA HALF (K50, docs/dev/known_issues.md): under `-e utf8` the unanchored DFA's start-anywhere self-loop steps one BYTE and splits into the pattern at every byte offset, so a pattern nullable at a mid-character position reports a mid-character match from an ORDINARY startpos-0 search — witness `\B` over "a\xce\xb1" answering (2,2) where (3,3) is correct, both engines agreeing (the VM's route via the K49 retry, fixed by that lane; the DFA's via nfa_wrap_unanchored, src/ir/nfa.c:965). REFUTES utf8_design.md §5.5's "mid-character starts have no path so they cannot produce a wrong answer" (true only for POSITIVE patterns; §2.6.1 one section earlier records the inversion for negative assertions — annotation landed with the K49 lane) and the ASK 5 ruling's premise. THE FIX'S RULED CONSTRAINTS: (a) the general rule — positions the ENGINE generates (self-loop entry points, retries) are exactly the encoding's character boundaries; for the CALLER, per Frank's 2026-09-05 follow-up ruling ("prepend a call, perhaps optionally but by default, a fail-if-this-start-is-not-valid"): the emitted entry gains a DEFAULT-ON O(1) startpos-boundary guard under `-e utf8` (byte backend emits nothing — every position valid), refusing a mid-character caller startpos with a TYPED code in the negative-return family (manager-recommended over silent nomatch; PCRE2's own UTF mode refuses with BADUTFOFFSET — MEASURE 10.46's exact behavior over ssh, transcript not assertion, before pinning the compat claim); a D46 deny-flag arm retains §2.6.1.1's ruled permissive semantics verbatim (the existing oracle-validated mid-char cells move to that arm, never deleted) — never round caller startpos on either arm; match_api.md §3.1 hunk in the same change (D80), stamp + deny pair per D46. TESTING SHAPE (Frank, same day: "something of an axis... i don't want a full doubling but we should test with/without for full matches so this flag doesn't hide errors" — ruled as the house deny-axis pattern, corpus BLIND to the axis by construction since ~every corpus cell is startpos-0 where the guard passes trivially): (i) BOTH-ARM CELLS exactly where the arms legitimately differ — the §2.6.1.1 mid-char-startpos table + the K49/K50 witnesses carry a default-arm expectation (the new typed code, riding the `gu <code>` directive family) AND a deny-arm expectation (the ruled permissive answer) — both semantics permanently watched, a handful of cells not a doubling; (ii) THE DIFFERENTIAL is the primary instrument (possessify/altcls shape): one witness family, both arms in one TU, swept over EVERY startpos of every subject — identical at every valid boundary (guard transparent), divergent at EXACTLY the mid-char set with the typed code (non-vacuity: an empty divergence population is a dead guard and a red check), and the BYTE artifact guard-free under either flag; (iii) test-axes membership with the divergence class DOCUMENTED and FLOORED (its harness's refused-documented vocabulary), never breaking that sweep's identity claim; (iv) sabotage rows in all four failing directions (guard deleted / over-firing on valid boundaries / leaking into the deny arm / leaking into byte artifacts), SAB_REACH from birth. Error-code spelling proposed by the lane within the RX_ERR_* family (manager suggests RX_ERR_STARTPOS); (b) §2.6(c) stands — the self-loop still TRAVERSES ill-formed bytes (matches after an FF byte are found); the gate is on where attempts BEGIN (the split edge gated on "next byte is not a continuation byte" or equivalent), not on what the loop walks; (c) the hybrid prefilter's candidate handoff (emit_vm.c:11080-11089 re-windows through the same DFA) is part of the site list — see K50's entry for whether the K49 retry fix already bounds it; (d) an ABI EVENT: every unanchored utf8 DFA artifact moves — full D76/D94 ritual (bump, re-pin (B), grep every reader, [SABANCHOR] tripwire, manifests/size-log re-records), byte-encoding artifacts must NOT move (identity gate green). ACCEPTANCE: known_fail/k50_utf8_dfa_midchar_start.rxt fires and its cell moves live; a generated nullable-at-mid-char sweep (negative assertions x \B x empty-alternation shapes, utf8 subjects with 2/3/4-byte characters) against the ARGUED table + 10.46 where an oracle exists; both-engine agreement ON THE CORRECT answer (today they agree on the wrong one, which is why nothing caught it — the sweep must include a cross-engine arm); the wasted-attempt claim of §5.5 re-measured as the fix's own throughput side-note (skipping mid-char starts is also the OPTIMIZATION §5.5 called "not optimal"). Opus lane (engine + IR); design review of the split-gate shape before code per D6 if the lane finds more than one candidate placement.

## Completed 2026-09-11
- [CC-ORIGIN] STATE:completed (RULED Frank 2026-09-11, sixtieth session, option 1 on the clstudy escalation; ADMIN, short list, sonnet-sized) — RETIRE THE TREE-WIDE INERT `CC ?=` IDIOM: GNU make predefines CC (built-in `cc`), so `?=` never fires and the named fallback compiler has never once been used; the same defect class santriage recorded for battery.sh, found live twice more (tt4m2's smoke pool, clstudy's `make discover`). Fix at every live site — root Makefile:4 plus studies/{lim2_census,n1budget,simd1,lim2_m1} — with the pattern the two newest studies Makefiles already carry: `ifeq ($(origin CC),default)` / `CC := gcc` (gcc-16 where the file names it), + a comment naming the trap so it is not "simplified" back to `?=`. DELIBERATELY NO `export CC` — not needed (same-Makefile recursion re-evaluates the guard identically at every level; caller choices propagate by make's own MAKEOVERRIDES/environment rules; `$(MAKE) -C scripts` uses no CC) and exporting would change the environment of every recipe subprocess, a new observable. R5-Q1 angle ruled through: a stranger's plain `make` moves from silent `cc` to the gcc the Makefile always claimed; a box with no gcc fails loudly instead of silently building with an untested compiler — accepted. Runs after the abifix landing (done) in the next admin slot. **COMPLETED 2026-09-11 (lane ccorigin, merged c4be2c7f): six sites (a 6th, studies/alt_dispatch, found by the lane's own grep — extra whitespace had hidden it from the charter's list); n1budget's guard set to gcc-16 per its own CLAUDE.md's documented measurements (an effective-behavior change, flagged); lim2_census + simd1 dropped the inert line with rationale (no documented compiler pin; simd1 targets a foreign x86-64/AVX2 Linux box). Validated: build+strict rc=0, smoke green except the chartered darwin inline_capability; all three origin cases verified by the manager in the worktree (plain→gcc/origin=file; cmdline and env both win).**

## Completed 2026-09-12
- [M5.0] STATE:completed (STANDING GO Frank 2026-09-06, fifty-sixth session: "continue through to M5.0 completion" — stages 3, 4, 5 open sequentially, each after the prior stage's battery-green landing, no per-stage round-trip; [K50-BNDSTART] stays sequenced before stage 3 per the 2026-09-05 ruling.) (DESIGN GATE OPENED 2026-09-04 evening, fifty-third session, on Frank's word ("will be interesting to see utf") — lane utf8design, opus, worktrees/utf8design: docs/design/utf8_design.md answering the eight design-gate questions (lowering, \p tables, DD-1 fold subset, the seam's second instance incl. the maxw cross-note below, state-count blowup vs the caps, the oracle plan with 10.46-over-ssh as the reference per today's PC-3 version-drift finding, validation plan, module staging); D6 panel after delivery; implementation NOT cleared by the design's landing — Frank's word per milestone discipline. DESIGN DELIVERED same evening (16d5adc2, 1,496 lines + 7 probes/8 transcripts; the five headline results incl. the cross-note's cure REFUTED — PCRE2 measures lookbehind in CHARACTERS — and \p{L} at 283 minimized states, no blowup; six §14 ASKs for Frank). R54 PANEL RAN the same night (docs/dev/reviews/2026-09-04-r54-utf8-design.md, three critics): 5 BLOCKING / 10 MUST-FIX — the sharpest: the lowering as placed never reaches the VM emitter (compile.c:1228 hands the AST root to emit_vm, four u.cls.bits read sites — a miscompile class), and the code-point-space complement refuses every negated class under --encoding=byte; all five headline results SURVIVED adversarial verification. REVISION ROUND DONE the same night (23 commits; all seven §14 ASKs RULED by Frank mid-revision — invalid-UTF matches-nothing; UCD vendored reluctantly with the usage condition; the fold standing-check S-U11; no UCP axis AT M5 door open; ENG_ATTEMPT leave + oracle-validated mid-char cells; the rxt_format amendment route; ASK 7 = a D58 ADDENDUM carrying max_cp AND the rationale narrowing, ruled at merge — decisions.md), plus the data-generality and encoding-wide-door rulings (§3.3.2, §5.7). VERIFIER PASSED (14/15 fully discharged, one paragraph-sized partial fixed at merge; four-lens evaluation clean; docs/dev/reviews/2026-09-04-r54-utf8-design.md OUTCOME section). **DESIGN APPROVED AND MERGED c9fcfa01; IMPLEMENTATION OPEN per Frank ("proceed through utf dev once the design is approved") — stage 1 (the interval-payload refactor, §9.2's five-stage ladder) is the first wave; its brief carries the verifier's two wave-tasks (constraint 2 confirmed empirically; the render helper's per-site conversion cost measured)**) **STAGE 1 DONE AND MERGED 2026-09-05 (f22b65c4, lane utf8s1, opus): A_CLASS carries sorted code-point intervals; pcrec_lower_enc's byte instance at compile.c:1000 under the SPLICE-IN-PLACE invariant; pcrec_cls_bits the sole bitmap reader (assertion ships enabled + fires on a scratch build); PcrecEnc.max_cp; all nine consumer sites converted. IDENTITY GATE 14/14 four axes (2,557 artifacts byte-identical, 0 differing, exact refusal agreement over 2,845 patterns); no abi bump (.abi=22 both); check 1 demonstrated RED on the pin; interval algebra independently model-checked (400×60 ops, 0 disagreements); byte-identity confirmed THREE ways (gate + size-log 2,962 rows + no abi). WAVE-TASK (a) REFUTED THE DESIGN — constraint 2 was mis-stated (a rebuilding lowering differs on 45/179 recursion artifacts at :1000, no legal slot with constraint 3); RULED R2(a) splice-in-place, design corrected at merge (30de9e3a — constraint 2 is now a node-identity PROPERTY, P-12 discharged). Wave-task (b): render helper 0.024% of compile time. S121 re-aimed via SAB_REACH (dormant until stage 3). NEW STAGE-2 FINDING: u.rep.revbody's reversed copy (413 classes) is built before the lowering and unvisited by the splice — inert now, a miscompile if stage 2 ignores it (in §9.2 acceptance). NEXT: STAGE 2 (the utf8 backend — enc_utf8.c, the genuinely-rebuilding lowering, cwmin/cwmax + maxw retirement incl. the test-side census, the revbody resolution) on Frank's word.** **STAGE 2 DONE AND MERGED 2026-09-05 (05b2fe8a, lane utf8s2, opus, fifty-fourth/overnight session; Frank's word = "finish utf", the session directive; docs/dev/lanes/utf8s2_report.md): src/gen/enc/enc_utf8.c (four residual bodies, back_step per §5.2.1) with the third-encoding recipe validated — nothing outside src/gen/enc/ + one enc.c table row to make `-e utf8` exist; src/opt/lower_enc.c became a LowerOps instance table (no if(enc==UTF8)) doing §2.3's range→byte-seq decomposition (E0/ED rows, surrogate gap, overlong); splice-in-place with cap_sig as R2's group-root-ADDRESS check IN THE COMPILER; u.rep.revbody RESOLVED (byte-confined bodies ≤ identity_max keep the revdet rung by identity — 413/413 corpus classes; genuinely non-ASCII bodies drop the rung, throughput never correctness); the width chain re-aimed to CHARACTERS (pcrec_maxw RETIRED → cwmax + new cwmin, both timings §5.6.4, callgraph third fixpoint, maxw_check.c→cwmax_check.c, S136/S171 re-aimed, S-U10 new); \x{...} now BASE grammar range-checked per encoding (§2.7.3). ACCEPTANCE: byte identity gate 14/14 at .abi=22 unchanged (the byte-path proof); run_encoding_checks.sh 7/7 (§8.5 slice 0 divergences + exclusion control, CHK3 census, DD-12(7)(a) both checks, S-U8 probe); S-U4..S-U10 all demonstrated DETECTED; confirmatory run rungselect 24/0 (395,757 cells 0 diverged, 106 revdet-rung patterns intact) + possessify 16/0 + corpus 27,045/0 + size-log columns identical on 2,962 rows. OWED TO THE LINUX SLOT: full ENC_MAX_BLOCKS=0 §8.5 sweep (~6,600 compiles), run_expansion_diff three-way vs reference 10.46, compliance-refresh for the \x{} row. The D27 blinded corpus (524 blocks, lane utf8corpus, cell) delivered same night — promotion pass + tests/utf8/ wiring by lane utfprom; oracle provenance is LOCAL 10.37 (the find_library hazard, see journal) so 10.46 re-verification rides the slot. STAGES 3-5 (\p tables + UCD vendoring, DD-1 fold closure, scripts) NEXT, on Frank's word per milestone discipline.** **STAGE 3 DELIVERED 2026-09-06 (lane utf8s3, opus, worktrees/utf8s3, branch lane/utf8s3; docs/dev/lanes/utf8s3_report.md): module `unicode-props` PRODUCES.** third_party/ chartered with the general shape (README index, one directory per source with version in the name, PROVENANCE naming what DERIVES from it, generator beside its data) and `make gen-tables` iterating `third_party/*/generate.py` naming no source; UCD 16.0.0 vendored (UnicodeData.txt only — D77, stages 4/5 bring their own files) compiling to src/parse/uprops_tables.inc (45 properties, 8,437 intervals, 67 KB). 45 NAMES SHIP: 7 one-letter + 30 two-letter general categories, L&/Lc, Any, Xan/Xps/Xsp/Xuc/Xwd — both encodings, both polarities, in-class, `\P{^X}` == `\p{X}`. **ACCEPTANCE MET: (1) PC-3's name axis green AND gained the arm it needed** — the closed-gate uprops differential still read GREEN and stopped certifying what its name claims the day a producer landed (its own wall asserts "no producer this phase"), so `check_gated_uprops_space` was ADDED (T1: pcrec never accepts a name libpcre2 rejects; the unshipped-name WORDING clause; two vacuity floors) — 118 probes, libpcre2 accepted 28 / rejected 90, pcrec accepted exactly the same 28, +6 PASS lines (201 -> 207, A/B-measured against a scratch build of the branch point: 187 -> 193 with the SAME 119 pre-existing failures both sides); **(2) PC-4-class membership differential BUILT AS ITS OWN SUITE** (tests/uprops/, `make test-uprops`) over the WHOLE code-point space on both encodings — byte 14/0 with ZERO drift, utf8 14/0 with 62,121 code points attributed to Unicode-version drift and NONE unexplained; **(3) the D65 `built` column flips for \p and \P** (138 = 110 built + 12 unbuilt + 16 n/a; `\N{U+}` correctly stays unbuilt). **THE D27-BLINDED CORPUS IS THE SHARPEST RESULT**: tests/utf8/axis04_p_categories.rxt's 148 perr blocks promoted from the oracle answers their blinded author carried since stage 2 — **462/506 cases green on the first run with ZERO semantic divergences**, all 44 failures one compile-size refusal on six patterns. **SIX FINDINGS.** (a) **K53 FILED, an ENGINE issue found through \p**: the OPTIONAL anchored DFA machine's bytes count toward max_emit_bytes, so it refuses patterns that compile without it (`\p{L}` under -e utf8 is 1,076,640 bytes at default axes and 772,412 with -fno-anchored-dfa) — contradicting `anchored_match_unwrapped.md`'s own "an overflow is a selection outcome, never a diagnostic"; 5 of 45 names affected; the 12 corpus blocks are tests/known_fail/k53_uprops_oversize.rxt. It REFUTES utf8_design.md §3.3's sizing conclusion, which measured STATES where the emitted size is states x CLASSES x digits. (b) **A CURSOR BUG the differential could not see**: `esc_class_value` never advanced past a produced EXT_MEMBERS, so `[^\p{L}]` excluded `{` and `}` as well as the letters — found by tests/uprops/ §4's ORACLE-FREE invariant `[^\p{L}] == \P{L}`, since both sides of the membership differential compile `\p{L}` at an ATOM; esc_atom's [M6.5.2] lesson at the class position, which that entry predicted in advance. (c) **U15 FILED, two halves**: libpcre2 changed `\p{Xwd}` from Xan+underscore to Xan+Mn+Pc between 10.42 and 10.46 (light reference probe, transcript in the report), and — the half that is about the whole tree — **the dlopen shim resolves macOS's SYSTEM libpcre2 10.42 / Unicode 14.0.0 on this box, not the Homebrew 10.48 every note assumes**, because bare SONAMEs precede the Homebrew absolute paths in tests/fuzz/pcre2_abi.h; that RE-OPENS what U13's 119 PC-3 failures actually measured (10.42 predates 10.43, where U2's `{,n}` change landed). A RULING IS OWED — reordering the list re-baselines the whole suite's oracle. (d) **THE CASELESS RULE IS NOT A FOLD CLOSURE**: measured two ways (44 names x 12,290 code points, and a full-space interval comparison), under -i `\p{Lu}`/`\p{Ll}`/`\p{Lt}` are EXACTLY `\p{L&}` and every other property is caseless-INVARIANT — U+0345 (Mn, uppercases to U+0399) is the discriminating cell a general closure would get wrong. So each row carries its set twice and cls_casefold is never applied; stage 4's closure is not a precondition for stage 3 after all. (e) **S121 DID NOT WAKE UP and stage 1's reach probe would have said it had** — it asked only whether `\p{L}` COMPILES, and stage 3's own encoding CLAMP makes that eight Latin-1 runs under the default encoding; re-measured, the hazard is STRUCTURALLY unreachable (n>255 needs a code point above 0xFF, and such a class DECLINES the revdet rung via pcrec_cls_bits_widen — proven with a \p-free control), probe re-aimed, solo run UNREACHED/0 anomalies. (f) THREE design-§3.4 claims refuted: `Assigned` is error 147 on all three reachable libpcre2 versions (NOT shipped), `Lc` compiles on all three (SHIPPED, §3.1's survey never tried it), and Xps/Xsp are NOT a pure category union (U+0085 and U+180E). Also: uprops_tables.inc joined the Makefile prerequisites — THE SAME DEFECT A THIRD TIME after cls_bits.inc and limits.def, caught within minutes. **STAGE 4 (DD-1, the fold closure — CaseFolding.txt into the same third_party directory) NEXT.** **STAGE 4 MERGED 2026-09-08 evening (lane utf8s4, opus; the per-contribution fold rule its headline result — utf8s4_report.md; design hunks applied at merge by lane foldhunks) AND ITS VALIDATION CLOSED 2026-09-09 ~13:04 (the darwin battery: zero merge regressions, four infrastructure catches incl. K54 darwin-san; the I-61 Linux arm: san 35/35, lint's first real run (one CWE-457 finding chartered to triage), tests/utf8 1713/0, backref_diff 12/0 with §9b exact, THE PC4 SEMANTIC DIFFERENTIAL ON REAL 10.46: 62,872 match cells 0 disagreements + the 1:n fold arm PASS, S-U11 solo DETECTED 0-unexpected; C3 authoritative pins re-pinning via lane arm61fix). STAGE 5 OPENED same hour under the standing go — lane utf8s5 (opus): SCRIPT properties (\p{Greek} et al.) — Scripts.txt vendored beside the other two UCD files, generate.py's fourth product, the script-name axis joining module unicode-props' table on stage 3's machinery.** **STAGE-4 GATE GREEN 2026-09-08 evening (I-59 executor run at 9ddf634e, report acked under I-59 in the bench inbox, logs build/ntriage_reval_20260908/): the tier-1 uprops-utf8 differential on REAL 10.46 reads EXACT agreement — "compared 45 properties; 0 code points attributed to version drift", oracle Unicode 16.0.0 = pcrec's pinned 16.0.0 (the version-drift budget wasn't even needed); uprops byte 14/0, rxtsource 121/0, encchk full 11/0, S-U9 solo UNDETECTED(EXPECTED)/0 unexpected; strict clean. (The I-59 item's "25 expected" was the manager quoting the bare both-encodings script count for the single-encoding make target — criterion slip, not a regression; make -n confirms ENC=byte vs ENC=utf8 vs both.) STAGE 4 OPENED same evening under the standing go — lane utf8s4 (OPUS, engine tier), worktree worktrees/utf8s4: DD-1's fold closure, CaseFolding.txt vendored beside UnicodeData.txt in third_party/ucd-16.0.0/ (generate.py extended, gen-tables generic rule unchanged), the caseless constructor widening for ORDINARY classes/literals under -i -e utf8 (stage 3's §9 measured rule means \p rows are NOT customers — Lu/Ll/Lt=L& ships already; the customer is [a-z]/literals/ranges beyond ASCII), S-U11 the fold standing-check per the design ruling, fold_agreement_check.c's extraction-vs-source shape where the rule is spelled twice. Box note at launch: tt4m2's parallel sweep owns the box — construction first, suites coordinate through the manager.** — milestone (expand on arrival): byte-wise UTF-8 automata, \p{...} module. CROSS-NOTE 2026-08-23 ([M6.6.2] wave A): `pcrec_maxw`'s A_CLASS arm answers 1 BYTE and is EXACT only because src/core/compile.c refuses PCREC_ENC_UTF8 by name; the day a UTF-8 backend lands that arm must become the encoding's maximum code-unit length (minw's identical-looking arm stays sound as an under-estimate) or the lookbehind fixed-width rule silently accepts variable-width branches. Recorded at both functions and in src/opt/CLAUDE.md; this row owns the change. NOTE ([M5-SEAM], completed 2026-08-18, see plan_completed.md): the residual seam, per-pattern `--encoding` scalar, and `<prefix>_next_pos` already SHIPPED as the D58 prelude — what remains here is the UTF-8 lowering instance (CharSet → byte-sequence fragments), \p{...}, DD-1 folding, the UTF PC-4 oracle twin, and DD-12 (7)(a)'s two M5-time structural checks (hot-loop shape identity ASCII-vs-UTF-8; the second-backend validation of the seam D58's revisit-when names) **STAGE-5 VALIDATION DISCHARGED 2026-09-11 (I-65 re-run, pcrecdev2 self-launched 14:05 EDT under Frank's new executor permission, pin 616c2e49, logs build/s5_rerun_20260911 on ubuntubudu): ALL SIX red stages green — san 35/35 (69m11s), registry PC-3 209 + POSIX 34-real-names + PC-4 62,872 cells 0 disagreements + definitions-oracle 202,488 comparisons 0, uprops byte+utf8 47/0 and 26/0 with [STORE] 387/387 exact + [LIVE] 0 drift, atomic 8/0, known-fail ratchet K34 alone. The ns/char rider RAN on its single pre-declared retry (gate never loosened; load1 0.10 at start): studies/cls_tree_study/results/bench_ubuntubudu_20260911.tsv, 2,641 rows — the [CLS-TREE] design-note gate's last input. REMAINING for the milestone: the close-out ritual (compliance-refresh, plan completion, milestone entry) — HELD on Frank's no-new-lanes instruction of the same afternoon.** **[M5.0] CLOSE-OUT RITUAL COMPLETE (lane m5close, 2026-09-12):** stage-5 validation DISCHARGED 2026-09-11 via I-65 (all six S5-ARM stages green at pin 616c2e49 on ubuntubudu — san 35/35; uprops_utf8 [STORE] 387/387 exact; PC-4 62,872 cells 0 disagreements); this lane ran the compliance-refresh over the milestone's changes (docs/pcre2_compliance.md's unicode-properties section survey prose reconciled to K53-SELRETRY's 2026-09-10 fix — the generated construct index and the keyed annotation store already matched the current tree, so components 1 and 3 needed no edit; component 2's hand-written narrative was the stale half, corrected in place), moved this row to docs/dev/plan_completed.md verbatim, and appended the milestone-close journal entry. MILESTONE CLOSED.**

## Completed 2026-09-15
  - [DD-13b.W23] STATE:completed (COMPLETED 2026-09-15, sixty-fifth session: all six merges delivered and MERGED at cd371441, Linux battery validated — strict/axes/san/lint rc=0, mech 256 rows 0 anomalies, test reds dispositioned box-margin; the row moves to plan_completed.md verbatim next session) (CHARTERED 2026-09-12, sixty-first session, on Frank's session directive "focus on rxt file format development; bench has come up with additional requirements" + the bench's O-26/[B42] input — Frank's [B42] ruling makes the capability survey set THE CONSUMER that earns W2 and W3 at once, ending the no-production-ahead-of-its-consumer hold at wave granularity) — W2+W3 DESIGN REVISION + BUILD, against `docs/design/dd13_format/bench_rxt_needs_v1.md` (the received input: 50 needs, 6 roadblocks, 12 proposed productions, a 41-check acceptance checklist the bench runs at their restart). BINDING RULINGS (Frank, 2026-09-12, recorded in the input's header): F-Q1 the first delivery is Tier 1 AND Tier 2 together (tag + vocabulary, @file: + subject id + optional sha256, mc + its stated counting rule, oracle at a version, provenance, capable, variant + kind, under-convention expectations, the config scoping/permanence rule, --list-source emitting all of it) — no W2-only cut; F-Q2 multi-line patterns are a MUST (pattern-esc or equivalent; the set will never flatten a (?x) body) and land with the NUL refusal in first-delivery scope. STEP 0 (separate small lane, rxtnul): the two silent-loss defect fixes — a NUL anywhere in a .rxt refuses by name (M1: today a pattern line truncates at the first NUL, exit 0) and a second `description` in one block refuses by name (M5: today last-wins; corpus measured clean, 210 files / 0 double-description blocks, manager 2026-09-12) — independent of every wave, the bench ranks the NUL refusal above every feature. STEP 1 (lane w23design, opus): format_design.md REVISION 3 absorbing the input — the twelve productions worked into §1.3's grammar/§2's semantics, the nine P-Q dispositions recorded with rationale, §4.5 item 4's regime mechanism REPLACED (measured unusable: the widened -/. name grammar and the (?&name) call grammar are individually right and jointly unusable for every bench pattern id), §6.2's worked bench file repaired against the D93 hazard (roadblock #6), the spec-delta plan and the W23 sequencing; D6 panel after delivery; implementation NOT cleared by the design landing — the impl note (w1_impl.md's shape) and code lanes follow. Manager syntax pre-rulings and leanings in the lane brief (dd13b-syntax-is-managers); Frank ruling queue: P-Q4 (capable in the format vs bench-side), the D93 scoping mechanism ratification. **STEP 1 DESIGN PHASE COMPLETE AND MERGED 2026-09-12 evening (four lanes, two panel rounds, one night): rev 3 (lane w23design — the twelve productions absorbed; built WITHOUT Frank's two mid-flight rulings, which never reached the lane — the both-channels+ack rule is now in the manager's memory) → rev 3.1 (lane w23recon — the reconciliation: the TWO-LAYER grammar, S0-S2 + declared schema, the head/body asymmetry DELETED; the version break PRICED AND DECLINED with the keyword reserved; §2.25 the schema mechanism + --list-schema; the ownership audit's renames incl. capable→provides, licence→license) → r57 ROUND 1 (three opus critics: 3 blockers / 12 must-fix — the block scalar a second undeclared structural device, two lenses converged; the constraint kinds missing four W23 rules; B6's refusal an EMPTY population; the x_y-beside-x-y fifth narrowing) → rev 3.2 (lane w23fix — S3 OPAQUE REGIONS, eight constraint kinds, B6 dropped premise-dissolved, the narrowing census; three pushbacks accepted incl. K57 FILED) → r57 ROUND 2 (focused re-check: blockers b/c HOLD, blocker a's fix failed on its own axis — COMMENT and WHITESPACE-ONLY line classes had shipped structural effects the layers could not produce, the latter multi-paragraph prose's only spelling) → rev 3.3 (lane w23fix2 — all four line classes given effects; whitespace-only INERT, a deviation from the manager's leaning that a probe forced; the cardinality decision measured-first, catching budget as accumulate-over-fields where at-most-one would have refused a shipped corpus file; census FINAL: eleven candidates, seven taken, four avoided, STEP 0's two carried with attribution). MERGED to main with the review record docs/dev/reviews/2026-09-12-r57-w23-format.md. FRANK QUEUE OPEN: W23-F1 (configs describe, amends D93), W23-F2 (provides in-format), W23-F4 (the non-callable-definition loss, manager recommends ACCEPT). IMPLEMENTATION NOT CLEARED — the impl note (w1_impl.md's shape) and code lanes open on Frank's rulings; the bench outbox message (correction list incl. capable→provides, licence→license, B6 premise dissolved, D1 nine→eleven, the mc adapter edit, the --list-schema offer) goes at the implementation delivery per O-26 §7. STEP 0 (rxtnul: the NUL + duplicate-description refusals) delivered, merge pending its full-suite trailer.** **STEP 1.4 / REVISION 3.4 (lane w23aux, 2026-09-13, docs-only): FRANK'S D99 EXECUTED — the ruling that the .rxt file's purpose is DEFINING RX, primarily for pcrec. W23-F1 (`configs describe`) and W23-F2 (`provides`) are WITHDRAWN rather than ratified (marked in place with their reasoning, house style); `config … testee`/`option` (N-42, a bench SHOULD) leave the wave plan with them; the format gains §2.27's AUX production `ext <consumer>` — consumer-namespaced, structurally parsed, semantically uninterpreted, dumped in a new `#section aux`, with the GRADUATION RULE normative. §0.9's SECOND-ORDER IMPACT TABLE is the deliverable Frank asked to see (23 rows: 13 seeded, 10 found), headed by `cross-scope` losing its only customer (constraint kinds EIGHT -> SEVEN by §2.25.3's own membership rule), the `lib`-contributes-DEFINITIONS-ONLY clause re-homed from §2.20 rule 4 to §2.5 (independent of describe mode; deleting it with its section would have re-opened a closure question in another production), and a STALE ECHO found in §8 P-Q9 (the `pattern`/`pattern-esc` refusal dropped at 3.2, surviving into 3.3). Census re-derived: NO narrowing row moves. Appendix A drafts the bench outbox message, NOT sent and NOT written to the bench repo. **FRANK QUEUE IS NOW W23-F4 ALONE** (the non-callable-definition loss, manager recommends ACCEPT); D93 untouched and DECOUPLED (D99 item 5). STATE UNCHANGED at started — implementation is still gated, now on F4 alone plus a D6 panel on this revision.** **STEP 1.5 / REVISION 3.4.1 (lane w23fix3, 2026-09-13): the r58 FIX ROUND — two-opus-critic panel `docs/dev/reviews/2026-09-13-r58-w23-aux.md` (3 blockers / 7 must, all FIX-NOW; critic B's inverse method over 66 mechanisms found exactly ONE orphan, the one 3.4 had already caught) + manager rulings R1-R4: structure-layer PARAMETER 3 (open subtree, `children: tree` — S2 empty and S3 never opens inside), NO prose values in aux bodies (a bare `|` is the literal `|`), `tag-prose` REMOVED under the membership rule, the outbox gated-then-cleared. MERGED 278689d3 + the F2-echo fix aa983157, pushed. **IMPLEMENTATION IS CLEARED (2026-09-13): W23-F4 RULED ACCEPT (D100), the r58 panel is the ruled D6 gate, the Frank queue is EMPTY. I-67 sent to the bench (their A2 fixture drops two `config` lines; D1 unmoved; F2 premise dissolved). NEXT STEP = the W23 IMPL NOTE in w1_impl.md's shape (what lands where, checks/sabotage, merge points, H12-H16 staging; folds in legs B/C parity for STEP 0's refusals, the A3/A4 fixture plan incl. the r57 probe cells, the SW1-SW19 spec deltas incl. SW18/SW19's aux rows and the `#section aux` dump-shape reader survey), its own D6 panel, then code lanes.** **STEP 2 / THE IMPL NOTE — COMPLETE, PANELED (r59) AND MERGED 2026-09-13 (sixty-third session): `docs/design/dd13_format/w23_impl.md` REVISION 1.1 (lane w23impl rev 1, opus → r59 three-critic panel `docs/dev/reviews/2026-09-13-r59-w23-impl.md` (checks/fidelity/citations lenses; 4 blockers, 13 must-fix groups, ALL FIX-NOW) → lane w23implfix rev 1.1). THE DELIVERY IS SIX MERGES: W23.1 schema table (`src/parse/rxt_schema.def`) + `--list-schema` + leg A dispatch as a table walk; W23.2 attachment arm + diagnostic CLASS tag in legs B/C + the STEP 0 parity fix (headless fixtures only — r59-A2; NUL rule at ONE scope, whole-file pre-parse, all three legs); W23.3 the fourteen productions + §2.22's repair; W23.3a the include HARNESS half (r59-B2's blocker: entry-set subtraction, closure accounting, the fourth failure class, SW20 — the H5 work the staging had silently dropped, a Tier-1 cut under F-Q1); W23.4 `--list-source`'s four `#section` blocks + the R5 AND R6 reader repairs (r59-A1: R6 at `run_rxtsource_tests.sh:499` is an INEQUALITY reader the survey mis-marked safe — a green W23-S4 would have PROVED it broken) + S200-S203 re-verification; W23.5 population check, remaining hunks, the ~25/41 RUNNABLE bench-check dry run (r59-B-M6's split). Seven checks W23-S1..S7, sabotage S239-S247, SW1-SW21 per step (SW20: spec row S3 never landed despite its W1 label; SW21: the diagnostic-class cli.md hunk, ruling R1). Manager rulings r59-R1..R4 (all four §7.3 questions manager-ruleable per critic B; K57 stays unfixed, `prose_dedent.rxtin` asserts the CURRENT wrong value naming K57 and goes red at its fix). format_design.md at REVISION 3.4.2 (three point corrections at the merge, §0.11 — incl. the conditional A1 `include` block-scope correction joining the §9 outbox list). abi 24 UNCHANGED, confirmed from the file-by-file plan (§1.9). Frank queue EMPTY. NEXT: charter [DD-13b.W23.1] (code lane, the schema table), then the steps in order; the D78 outbox message goes at the implementation delivery per O-26 §7, carrying §9's full correction list BY REFERENCE (r59-B1's standing rule).** **[W23.1] DELIVERED AND PARKED 2026-09-13 (lane w231, opus, branch `lane/w231`, 9 commits from 3127cf62, worktree kept): the 66-row schema table, `--list-schema` (both #section blocks table_contract-truthful), leg A's dispatch as a table walk. MEASURED: `--list-source` byte-identical 210/210 vs a scratch branch-point build; census unmoved; rxtsource 145/1/1; strict clean; CENSUS_WORDS_32→_30 re-pinned. Two note contradictions lane-resolved + manager-RATIFIED (later-wave rows EXIST wave-marked, 2/6/2; `version` reserved-sentinel row — the note takes both as one-line corrections at merge). Full `make test` exit 2 at 38/38: inline_capability (chartered, not the lane's) + W23-S3 arm 4 — the lane's own check vs its own reserved row (class `[unknown-token-in-scope]` on a RESERVED keyword; wording right, class wrong half; class vocabulary is W23.2's). MERGE NEXT SESSION: fix arm 4 → re-run test-rxtsource → full battery → merge; then W23.2.** **[W23.1] MERGED 2026-09-14 (0b7f4d62, arm-4/4b split at merge review; the pin's full battery — test/strict/axes 2026-09-14 overnight + san/lint/mech green 2026-09-15 02:17, mech 248 rows 0 unexpected — also ROOT-CAUSED AND FIXED K54 en route, Frank ratified). [W23.2] DELIVERED AND MERGED 2026-09-15 (lane w232, sonnet, merge bb750dce+: legs B/C class comparison at 12 all3 sites, attachment arm, STEP 0 parity, S239, fixtures; rxtsource 160/0/1, census unmoved; reserved-`version` class RULED stay-[unknown-token-in-scope] per §2.25.5's own wave-above-build clause; §3.2's indent_under_m row corrected to structure-attachment at merge). Post-merge full battery launched 2026-09-15; W23.3 (the fourteen productions) chartered off the merged tree. NEXT after W23.3: W23.3a → W23.4 → W23.5, then the D78 outbox message.** **[K57 CODA, 2026-09-16: the r59-R4 waiting state discharged — lane k57fix merged; the block-scalar dedent now REFUSES a shallower content line by name (class `value-shape`) in all three legs, `prose_dedent.rxtin` inverted exactly as the ruling predicted, plus the new three-leg body-scope fixture `prose_dedent_body.rxtin` (rxtsource 208/0/1).]**

## 2026-09-18

- [REVW.FIX] STATE:completed — the FIX-NOW pile, synthesis §1 items 1-10 in
  its landing order (L8-F1 first; L1-X2 the pilot, last). D105/Q2 already
  landed at the ruling. Lane fixnow, merged 312c76ae (fast-forward): ten
  commits, one per item, comment-only or byte-preserving throughout; both
  X2 sabotage rows re-aimed + re-verified DETECTED at exact pre-merge
  figures; full make test 39/39 sections green (sole FAIL = pre-existing
  darwin inline_capability nm-probe, reproduced on main); recursion
  differential 10/0 incl. §5's 28,458 splice-vs-linkage cells. Report:
  docs/dev/lanes/fixnow_report.md.

- [REVW.U] STATE:completed — wave U (nets): L5-R0 unit tier (unit_cc.sh, 7
  sites, tests/core/), L5-R2 sat-arith agreement check (S254 core:1fail/
  6pass), the allocation-failure injector (make alloc; red-on-unrepaired-F1
  transcript both directions; FOUND K60 — retry ladder absorbs a genuine
  OOM on a non-final attempt, filed, three dispositions to Frank),
  L8-F6(a)/(b)/(c) (40-site census, darwin positive control, S255/S256/
  S257 all resource:1fail/26pass DETECTED). Lane waveu (sonnet), manager
  takeover at the landing (lane died post-S257-launch); merged 2026-09-18,
  make test 40/40 green (known darwin inline_capability red only).

- [REVW.1] STATE:completed 2026-09-18 — wave 1 (emission kit, outer). STAGE 0
  (lane w1stage0): the long-prefix full-corpus sweep repairing the
  [MECH-REACH] finding (1,499/1,500 clean at the 60-byte legal prefix, no live
  K38 recurrence), the --emit-ir byte-neutrality arm (S258 DETECTED both
  directions), the listing-reach census (27/41 role sites on the fixture set,
  31/41 corpus-wide; lookbehind + subroutine-call emission UNREACHED — the gap
  a stage-3 lane must widen). STAGES 1-2 (lane w1kit, opus): sb_text/sb_textn/
  sb_field/sb_join/sb_row in src/core/sb.c, adopted at ~36 sites; cli_err at
  71 of 79 stderr sites. **THE CHARTER'S CENTRAL STAGE-1 PROPOSAL WAS REFUTED
  BY THE TREE** — promoting put_escaped as the one field escape doubles a
  backslash and would break 150 data rows across five registry dumps (the
  `syntax` column literally IS `\d`, and tests/reject builds probe patterns
  from it); resolved as TWO VOCABULARIES over ONE implementation. Byte-neutral
  (3.6 MB dump corpus 0 differing, 79-message CLI set identical over a 1.68 MB
  sweep with two deliberately non-shared normalization rules, 1,500-cell
  emit-diff 0 movers) — not an abi event. S200/S241 re-aimed + re-verified
  DETECTED. Manager landing fixes: the K37 allowlist entry for the sweep's
  python continuation line, and FOUR stray generated artifacts (zzz, zzz.h,
  out.c, out.h) removed — scratch committed by accident in 3cc0d46d.
  Checkpoint battery battery_20260918_051433 @ 272bf970: mech 265 rows
  (unexpected 0, anomalies 0), strict/axes/lint rc=0; test + san reds both
  triaged (lanes btriage2, santriage3) and non-blocking — THE PIN HELD.

## Completed 2026-09-21 (seventy-fourth session: D114 rulings — [ADMIN-0921] the wave's four owed items, gated + re-pinned at 8607a83d; [LIM-2] closed in place, N2 vacuous by M1)

- [ADMIN-0921] STATE:completed (**GATED + RE-PINNED 2026-09-21: merged d697655e; darwin gate at 4c2b06d2 build/strict clean, 53 sections 0 failed, sole code-unrelated red the standing nm probe; the corpus-census pins moved by the new K62 file were re-pinned by lane k62pin (2dc8e021), rxtsource solo 212/0 on the merged main.** **DELIVERED 2026-09-21, seventy-fourth session, lane `adm0921`, branch `lane/adm0921` at `70a298f0`, five commits, one per item plus one fix-up caught by the item's own broader validation.** (1) DELETED the four dead exports (`pcrec_emit_abi_types`, `pcrec_nfa_has_asserts`, `pcrec_rxt_schema_opens_group`, `pcrec_rxt_source_ncols`) with their declarations and header comments; `nm -g build/libpcrec.a ' T '` 262 -> 258, exactly -4; `make strict` clean, no new unused-function warning (nothing else went dead). D104's cited export count (295) was found ALREADY stale for reasons unrelated to this lane (measured 262 at the branch point, before any of these four deletions) — flagged, not re-pinned, since re-pinning a pre-existing drift is outside this charter's four items. (2) REGENERATED all five tools/review censuses at HEAD (not just function_census, which CLAUDE.md's own practice always regenerates as a set): function_census 917->935 rows, clone_candidates 278->295 member rows, literal_census 12652->12712/5136->5157, include_graph 207->208 includes, 0 back-edges throughout, churn_hotspots unchanged row count — the drift was real and pre-dated this lane (emit_vm.c alone gained 18 functions since the 2026-09-20 snapshot). No "export" column exists in any of the five schemas; read as the same staleness the row counts already show. (3) FOUND S154's live witness, closing tour2_report.md's owed item: tour2's own attempt ('^(a(?1)?b)$' over a^n b^n) hits the fixed RX_TRAIL_FRAMES 3072 bring-up default at every n because that call is self-recursive (cost.unbounded stays true); a non-recursive single call, '(a)(?1)' over subject 'aa', gets a COMPUTED trail_frames instead (13 clean vs 10 sabotaged) and reproduces the row's documented failure mode exactly (clean matches [0,2), agreeing with libpcre2 10.48; sabotaged returns PCREC_ERR_FRAMES on the identical subject) — recorded in the row's own SAB_DOC_FIGURE. Re-ran the row solo through the real driver post-delivery: DETECTED, `corpus:522fail/1168pass,recdiff:98fail/6pass,codegen:1fail/108pass`, unexpected 0. (4) CLOSED K62: one shared helper, `cls_dissolve_len(cx, pos, in_quote)`, answers "how many bytes here are a dissolving quote marker" (2 for a bare `\E`, 4 for `\Q\E` only when NOT already inside a real quote) for both `cls_skip` and `cls_peek_past_dash`, which previously disagreed (the lookahead recognised only the four-byte spelling). Oracle-verified against local libpcre2 10.48-Homebrew and pinned in `tests/quoting/k62_class_range_e.rxt` (5 blocks/16 cases, outside the D27-blinded `d27/` corpus): `[0-\E]`={0,-}, `[a-\E]`={a,-}, `[0-\E9]`=0-9, `[0-\Q\E]`={0,-} (control), `[0-\E` (unterminated) still refuses. **A fix-up commit was needed**: the first cut of the shared helper dissolved a `\Q\E` sequence unconditionally, which broke nested `\Q` inside an already-open quote (`tests/quoting/d27/charclass.rxt`'s `[\Qa\Q\E]` cells, caught by running the FULL tests/quoting/+tests/classes/ harness rather than trusting the narrow new pin file alone) — fixed by gating the four-byte form on `!in_quote`; re-validated 186/186. VALIDATION (whole delivery, at `70a298f0`): `make -j4 CC=gcc-16` and `make strict CC=gcc-16` clean throughout; `scripts/m6read_check_sab_anchors.py` 286/286 resolve; `python3 scripts/emit_sweep.py --ref 476892de` — self-check PASSED at full reach (3520/3521/3521/33/7 population, 0 movers/0 asymmetric), real run **0 movers on all 5 streams**, the only asymmetry (2 rows, 3 streams) being the two K62 test patterns that used to refuse and now compile (the fix's own intended effect, not a corpus regression); `make test-codegen` 65/65 checks, 9/10 scripts, sole red `run_inline_capability.sh`'s standing pre-existing darwin `nm`/`arm_a.o` probe (confirmed pre-existing by tour2 and others, unrelated to this lane); `make test-registry` 620/620 checks (225+209+108+24+54 across its five sub-checks), 0 failures. Full `make test` launched in the background as the lane's last act; numbers OWED, log at `worktrees/adm0921/build/adm0921_test.log`, completion line `checks failed:`. Report: `docs/dev/lanes/adm0921_report.md`. Never merged to main by the lane; the manager's darwin gate + `make test` review is owed at merge.** re-pin landed by k62pin: `tests/rxtsource/run_rxtsource_tests.sh`'s census 212/3939/28955 -> 213/3944/28971 for the new `k62_class_range_e.rxt` (RUNSH_* moved by the identical +1/+5/+16; C3's Linux-reference breakdown moved PASS +1/SKIP +15, all fifteen under no-python-expression); rxtsource solo 212 passed/0 failed/1 recorded, `make test-codegen` 65/65 checks (9/10 scripts, sole red the standing pre-existing darwin nm/arm_a.o probe), `scripts/m6read_check_sab_anchors.py` 286/286. See `docs/dev/lanes/k62pin_report.md`.)
- [LIM-2] STATE:completed **(CLOSED IN PLACE 2026-09-21, seventy-fourth session, the manager's D77 reading reported to Frank: the practical problem CLOSED 2026-09-04 with N1 (d7c64fbb); the audit's owed N2 is measured out by M1's own bar — the closed fraction never exceeds 14.3% (dfamin_m1m2.md finding 2), nowhere near the study's 50%-before-half threshold that makes N2 live, so a closed-subgraph lower bound would bound nothing; nothing is built. Revisit trigger: a refusal whose cost N1's budget does not bound.)** — formerly STATE:started (LANE C `lim2` LAUNCHED 2026-09-04 08:2x EDT, fifty-first session: sonnet, worktree worktrees/lim2, branch lane/lim2 on main at abi 20, write-only under `.hold` until w13's chain and the battery free the box; the projection during subset construction, the refusal-identity check with a main-built BEFORE control, the altwide cost table) — formerly STATE:not-started (CHARTERED 2026-09-02, Frank's ruling, fiftieth session; ADMIN/LIMITS column). THE DFA ROUTE'S PROJECTED-SIZE BAIL: the source cap `PCREC_MAX_EMIT_BYTES` is checked on the EMITTED bytes after subset construction and table emission (src/core/compile.c:1203 reads emit_size_total), so an altwide refusal costs 8.7-36.0 s on the DFA route against 0.01-0.07 s on the VM route (O-14 §6, ledger §6.3; 26 auto refusals in the night). Charter: project the table part (states × classes × cell width is exact) DURING construction and refuse with the same stamped reason the late check gives, answer-identical on every artifact that compiles today (the refusal set moves NOT AT ALL — a check, not a hope: the corpus + the bench's altwide@0.1 refusal table are the before/after). QUEUED behind [OPT-5] STEP 2 (both touch the DFA build path). D77 trigger: measured. **SIZED BY THE BENCH 2026-09-02 ~16:1x (their docs/dev/measurements/2026-09-02-altwide-raised-cap-sizes.txt): at default caps 50 of altwide@0.1's 80 compiles refuse — 26 auto at the total cap costing 0.07-40.2 s each (checked AFTER emission), 24 VM at the code cap < 0.1 s; on the auto route the cost IS the subset construction (11-37 s; gcc < 1 s) — so the bail must project DURING construction, not before emission, to reach the VM route's cost class; a post-construction check saves only the emission.** **LIFTED 2026-09-04 13:41 (fresh sonnet agent on the committed lane/lim2 4e0055ea; post-lift list = the census check, then test → codegen → registry → axes; DELIVERED by .stage).** **STUDY-1 CHARTERED 2026-09-04 14:2x by Frank ("i would like a study done on this for a later step"), lane dfamin (opus, worktrees/dfamin, lane/dfamin; a READ-ONLY study, nothing under src/, no builds while the afternoon's timings own the box): CAN STATES BE COMPACTED AS THEY ARE GENERATED? Trigger = lim2's census (k18_cost_gates: raw subset construction 33× the minimized machine, so a raw-byte projection cannot bound the emitted table). Frank's three directives: (1) it is cutting-edge — a WEB SEARCH on the latest (incremental DFA minimization, NFA reduction by simulation/position-automaton reduction, anytime/partial minimization) is the first step; (2) consider whether an INCREMENTAL PARTIAL compaction followed by the existing THOROUGH pass at the end is SIMPLER than full online minimization — "simplicity is the key there"; (3) the study's question is whether it can be done WITHOUT GETTING BRITTLE — Frank's stated concern. Deliverable docs/dev/dfa_online_minimization_study.md: the survey with citations, the candidate mechanisms ranked by simplicity and by fit to src/ir/dfa.c's worklist/intern idiom, the brittleness analysis (what can go wrong, how it would be caught — the census check is the instrument), and a measurement plan for the later step; no code.** **Frank 14:3x, clarifying: the method is NOT dictated ("if it turns out the full compaction is the way to go then i'm all for it"); the two-pass shape is an OPPORTUNITY — cheap wins taken incrementally as states are generated, then a second pass for the complicated equivalences, and that second pass "might even be optional if expensive and the final state of the incremental was usable" — so the study asks whether the thorough pass is a correctness requirement or an optimization.** **STUDY-1 DELIVERED AND MERGED 2026-09-04 14:5x (1e5133d6; lane dfamin tip 3a0c6350; docs/dev/dfa_online_minimization_study.md, 876 lines, read-only — no compile, no make, no benchmark): five candidates ranked by simplicity — N1 a deterministic work budget (10-25 lines, no size claim), N2 minimize the CLOSED subgraph periodically and project from its block count (80-120 lines, an exact LOWER bound with no percentage, not an abi event: it retires lim2's unrepresentable-margin finding without any compaction), A Frank's shape (200-300 lines, sound with one branch in minimize.c's state_sig making an unfilled cell unique, but its sound merges are exactly the closed subgraph's and on a counted repetition the frontier stays reachable from nearly everything until the end — expected to do ~nothing on the K18 population; reasoned, not measured), B prune each subset as it is closed by an NFA dominance (simulation) preorder (170-270 lines; the only shape matching the 27×: unrolled counter copies are inclusion-ordered so {4..30} → {4}, reachable subsets quadratic → linear; also the only one reducing the K7 subset_elems charge; exact IF three pcrec-specific conditions hold — assertion-boundary domination, the K18 open-loop context, the reverse machine's no-prune rule), C the full online equivalence registry (500+ lines, a subsystem). BRITTLENESS: A checkable only with a forced-threshold mode; B brittle AS THE TREE STANDS — three of seven failure modes live in a counted-repeat × assertion cross-product cell no sweep generates (learnings §3) — fixable by a few hundred generated oracle-verified patterns written BEFORE the mechanism; BOTH move the refusal set and nothing today asserts the refusal set. Two unasked findings: emitted state numbering is minimize.c:161's first-occurrence order over raw creation order, so a merge-into-the-earlier-state compaction PLAUSIBLY preserves emitted bytes (three named holes; an abi event if it moves); and N2 is lim2's cheap sound fix. RECOMMENDATION: do not build A; do not build C yet; (1) N2 for lim2's margin as its own small row, conditional on M1; (2) M1 = instrument pcrec_build_dfa's worklist to report the closed-state fraction at each 5% of construction on the k18 witnesses + altwide w-2048/w-512/s-4096/s-2048/sh1-512 + the counterk tower + 20 ordinary controls (bar: >50% closed before half the raw states → A and N2 live; <10% until the last 5% → A dead, fall back to N1); (3) M2 = the dominance prize via a deliberately illegitimate copy-index stand-in, charter B only if 27× → under 3× and sum(nlist) halves on the altwide series; (4) M5 read Nicol & Frohme [NF25] (2025, TACAS 2026) and its library, no box time. UNRULED: which of M1/N2 to charter and when.** **REVISED AND RE-MERGED 2026-09-04 14:5x (ec78046e; lane tip 3fe408d8, 1,125 lines) after Frank's clarification reached the lane: §3.1 answers "is the thorough pass a correctness requirement or an optimization?" — it is architecturally optional ONLY in the one configuration where compaction proves equivalence exactly during construction (C); §3.2 a taxonomy of merges by what each must know (Tier 1 before intern / Tier 2 finished rows / Tier 3 closed subgraph / Tier 4 full registry); A′ (merge states with identical finished rows; exact, tiny, safe, Tier 2 — build only as C's confirmation step) added; C promoted to first-class. REVISED RECOMMENDATION: (1) fix lim2's margin on its own NOW with N2 (or N1 if M1 says the closed set is empty) — the bail needs provable INEQUIVALENCE while compaction proves EQUIVALENCE, opposite proofs, so the bail must not wait on the compaction question; (2) READ Nicol & Frohme (M5) FIRST, no box time — C is the only candidate with the optional-second-pass property and an exact projection, and it is ranked on an abstract; (3) M1 and M2; (4) choose B vs C on the numbers (C the more dangerous mechanism and the better-CHECKABLE one: diffable for isomorphism against the existing pipeline over the whole corpus, B is not). DO NOT BUILD A (no M1 outcome favours it). UNRULED: M5/N2/M1 chartering and timing.** **RULED 2026-09-04 15:1x (Frank): the afternoon runs PLAN A (everything today; quiet-box timings edge2 → ccd2 ladder → form0 until an 18:00 hard stop, then edge2+ccd2 merged back to back and ONE union chain, DONE to the bench ~19:30); the paper STUDY-1 ranks C on is https://arxiv.org/html/2505.10319v2 (Frank supplied the URL) — M5 CHARTERED as lane m5paper (opus, read-only, no box time): read it and its library, retire the study's `unverified` marks on §2.3/§3.8, and say whether C's optional-second-pass + exact-projection property holds as stated.** **STEP 1 CLOSED BY MEASUREMENT AND MERGED 2026-09-04 15:2x (86e66dcd; lane lim2 tip 64872e17; strict clean; src/ and tests/ byte-identical to main, abi 20 unmoved): the projected-size bail and the reverse-first reorder are WITHDRAWN (revert commits on the branch) — ruling 1's corpus-wide census (population 12 = the patterns that cross the premul threshold, out of 3,386 blocks: 1 corpus + 11 altwide) found tests/base/k18_cost_gates.rxt:66 shrinking 97.062% on minimization (27,575 raw states → 1,010), so the required margin (2× = 194.1 pts) is unrepresentable in a percent-of-raw-bytes bail; measured on a quiet box, w-2048 refusal: main 10.81 s / branch@85% 1.33 s / branch@census-margin 11.39 s (s-4096: 19.32 / 12.62 / 19.24) — the whole win depended on the disproved margin, and the reorder costs ~0.5 s when it buys nothing. Two side findings: the bail's refusal did not join intern()'s dfa_overflowed umbrella (an auto-fallback regression, the bail's own, reverted with it); under reverse-first, a{65535} hits the 32,000-state cap on the REVERSE machine before forward's subset-element bound fires (a fact for whoever builds N2). LANDED: docs/dev/lanes/lim2_report.md (S1-S14) and studies/lim2_census/ (the instrument + census_data.tsv + summary; `make` builds it against build/libpcrec.a; never run by make test). Frank: "that sounds like a success. we theorized and tested and made the best choice." STEP 2 = the study's successor design (N2: project a LOWER bound from the closed subgraph's minimized block count; N1 the work-budget fallback), gated on M1; the accept-table term is deferred behind it.** **M5 DONE AND MERGED 2026-09-04 15:3x (4355c90f; lane m5paper tip 42bfe82a; the paper [NF25] arXiv:2505.10319v2 and its OTF reference implementation github.com/jn1z/OTF read in full, no box time): CANDIDATE C's DEFINING PROPERTY IS FALSE — the paper's §3.1 says "a final minimization is necessary", and the reference driver runs Hopcroft unconditionally after the loop; so the second pass is NOT optional, raw ≠ emitted, lim2's projection does not become an identity, and no intermediate count is a lower bound. The algorithm = subset construction + an equivalence registry whose lookup can answer for a never-created metastate (the only work-saving part) + a threshold predicate that periodically runs Hopcroft on the partial DFA with unexplored states pinned in singleton blocks; the relation is language equivalence, simulation only a key-normalizing device. Cost: no complexity analysis in the paper; registry GET worst-case quadratic; evaluated on 52 Walnut systems + 300 random modular NFAs — NO regular expression and NO counted repeat anywhere. Two structural findings: the paper's Table 1 is a 2×2 of this study's own candidates (SC-S = B, OTF = A + a generalization layer), and C REQUIRES A (UNIFY is called only from the intermediate minimization) — so "do not build A" and "build C" were inconsistent. REVISED VERDICT: C stays Tier 4 and drops BELOW B; §5.1 step 4 is B-FIRST; M1 must measure the paper's partition rule (unexplored states pinned as singletons), not the closed fraction — §3.5's "precisely the closed subgraph" was too pessimistic and was the sole basis for ranking A down; M6's size bar is answered in advance, only its scan-edge minimality-vs-finality question survives. Library: OTF, MIT, Java on AutomataLib, plain NFAs only (no epsilon/priority/views) — not an isomorphism oracle for pcrec. OWED: the study cites no REFERENCES.md keys yet (lane refs2 retrofits). UNRULED: charter N2 (lim2's margin, now independent of compaction) and M1 (the partition-rule measurement, B-first).** **RULED 2026-09-04 15:5x (Frank): "we'll charter the remaining step for after we move machines" — N2/N1, M1 (the partition-rule measurement), M2 (the dominance prize), the headroom count (how many of the census's 389 cap-refusals are small minimal machines behind a wide route) and B are NOT chartered until pcrecdev1 runs on the new machine; the next session does not start them unprompted (memory pcrec-two-machine-split).** **M1 STARTED 2026-09-04 evening (fifty-third session, on Frank's "agree with your lane plan" — the post-move word the ruling required): lane m1part (sonnet, worktrees/m1part) builds the partition-rule instrument per the study's §6 re-scope — the [NF25] rule (unexplored states pinned as singletons) measured at checkpoints over the lim2 census population + the corpus's large-DFA tail, answering (1) the monotonicity/lower-bound property N2's margin needs and (2) the closed-fraction comparison that re-ranks candidate A. N2/N1, M2, the headroom count and candidate B stay unchartered pending M1's evidence.** **M1 DONE AND MERGED same evening (c88ada5d, lane m1part, ~40 min; docs/dev/lim2_m1_partition_measurement.md; instrument studies/lim2_m1/, self-checked against pcrec_minimize_dfa over all 119 measured patterns at zero mismatches, failing-direction control verified by the manager on the census witness at landing): (1) MONOTONICITY REFUTED — the partition-rule intermediate block count EXCEEDS the true minimized count on 30/119 patterns (25.2%; up to 3,001× on counterk.rxt:1845, 8,002 raw / 2 minimized; the census witness itself exceeds 10.5× at 75%) — so N2's naive lower-bound projection is dead as designed; (2) candidate A's death made QUANTITATIVE — the closed-subgraph fraction never exceeds 14.3% at any pre-100% checkpoint and sits under 0.04% on every substantial-shrink pattern, while the partition rule's own merged fraction reaches 33-49% on the census witness (the two-orders gap that is §6.6 item 4's "too pessimistic" in numbers). OPEN: M2 (the dominance prize, candidate B's gate) unmeasured; reverse/anchored machines unmeasured (forward-only, lim2_census's own scope). The B-vs-C ruling awaits M2 + Frank.** **N1 DONE AND MERGED 2026-09-04 late (d7c64fbb, lane n1budget, sonnet): PCREC_MAX_AUTO_DFA_ELEMS = 30,000,000 checked before the K7 hard cap, AUTO-only + mandatory-machine-only (an explicit --engine=dfa pays the full 48M cap), joining the SEL-1 fallback umbrella with a one-line stderr note (discard-safe placement, WARN_EMIT_BYTES shape). Default derived from a real sweep (studies/n1budget/, worst currently-compiling spend 24,050,003 elems) and PROVEN inert by a before/after engine-selection census vs a main-at-fork compiler: 0 differences either direction over 2,845 corpus + 33 altwide. The raise surface GENERALIZED cli/main.c's two --max-emit-* blocks into one offsetof-addressed raise_only_limits[] driving six flags (the general mechanism, not four one-offs); PCREC_MAX_DFA_STATES_TABLE surveyed non-raisable (emitted as a C short) and reported. Diagnostics name their raise flag; limits manifest 55->56; tests/codegen/run_n1_budget.sh 13/13 (failing-direction validated). make strict clean; manager re-verified at merge after a stale-binary false alarm. The [LIM-2] practical problem is CLOSED without B/C/projection; B/M2 stay dormant (D77).** **N1 CHARTERED 2026-09-04 late evening (Frank: "Charter N1 as stated", on the manager's validated package after M1's double refutation; B/M2 go DORMANT per D77 — "we may never need to measure it" accepted): THE WORK-BUDGET FALLBACK + THE RAISE-AND-RETRY SURFACE. (1) the AUTO route's DFA attempt gains a construction-spend budget in ALREADY-COUNTED units (the K7 subset-element counter — no new counter), a limits.def row with a DEFAULT sized ABOVE every currently-compiling corpus artifact's spend (from studies/lim2_census + lim2_m1 data + margin) so today's engine selections move NOT AT ALL (proven by a before/after stamp census; the identity gate is the backstop); over budget → fall back to VM exactly as a cap refusal does under SEL-1, with a one-line actionable note naming the limit; explicit --engine=dfa is UNAFFECTED (full caps, the user asked and pays). (2) the four construction caps (limits.def:136-140 — NFA states, both DFA state caps, subset elems, all override NONE today) gain the raise surface: survey how --max-emit-* is plumbed and generalize (the general mechanism, not four one-offs — memory pcrec-general-mechanisms); any cap whose consumers structurally need a compile-time constant is reported, not forced. (3) diagnostics: the --engine=dfa refusal names the limit AND its raise flag; the auto-fallback note per (1). (4) the raw-projection WARNING is OPTIONAL/stretch — a follow-up, never gold-plated into this lane. Spec hunks (docs/spec/limits.md, tuning.md) in the same change per D80. Sonnet lane; light local validation, the full battery rides the next ubuntubudu slot.** **[K53-SELRETRY] CROSS-CONSTRAINTS (2026-09-10, lane utf8k53 at its merge): the refusal set MOVED — eight altwide witnesses (tests/rxtsource/fixtures/bench_altwide_0_2.rxtin) now compile via the size-drop retry, so ANY future [LIM-2]-family before/after control (and the bench's altwide refusal table) re-bases onto this tip, never onto an older branch point; and ANY projected-size bail built later MUST route an OPTIONAL machine's projection to the optional arm (d->overflowed = true), never to ctx_fail — or it re-introduces K53 one pass earlier than the post-emission retry can see.** **M1+M2 DELIVERED AND MERGED 2026-09-17 early (lane dfam12, docs/dev/dfamin_m1m2.md; probe dropped at merge, preserved as dfam12_probe_m2.patch): A LEGITIMATE NO. M1 = ZERO merge yield on K25's chains (strict sequential chains have no redundancy for any candidate to find — K25's cost is pure Moore-refinement overhead); M2 = candidate B's dominance prize is narrow (4.6% aggregate K7 relief, 4.0% of rows with real raw relief) and MEASURABLY HARMFUL on the study's own chartering witness (k18_cost_gates.rxt:66 flips compile→refusal under the most permissive stand-in — §4.3 B2's predicted brittleness, now a number). Candidates A/B/C all stay UNBUILT; revisit trigger = the study §4.3's preconditions (the general context-aware simulation preorder + the counted-repeat×assertion cross-product corpus) if the question ever reopens. The dfamin STUDY THREAD CLOSES here; the original [LIM-2] projected-size-bail row's own remaining work is unaffected.**

## Completed 2026-09-21 ([TOUR-EXEC] wave: the guided-tour tidy-ups, merged and gated 2026-09-21)

  - [TOUR-2] STATE:completed (MERGED 78058db7; GATED 2026-09-21 01:5x, seventy-third session: darwin `make test` at 1691c590 40/40 sections, 0 checks failed, sole red the standing nm arm_a.o probe; size log 0 movers / byte-identical total; strict clean; anchors 286/286 after every merge — formerly STATE:started: MERGED 78058db7 2026-09-20 ~18:4x, gate owed with the wave: make test + make test-axes on the merged tree; lane delivered in full — cost_add/cost_max, the dispatcher, the shared vm_alt_flatten (the two walks were byte-identical), F6 at the three emit_vm.c callers (select_engine.c has no vm_counter_fits call site), emit_sweep 0/0 on five streams, size log 0 movers, anchors 285/285; OWED small: S154's live differential needs a better witness — lane `tour2` LAUNCHED 2026-09-20 ~17:3x, sonnet, worktree worktrees/tour2, branch lane/tour2, branch point 82dd396a; carries r61 F6) — emit_vm.c vm_cost: `cost_add` / `cost_max` helpers (CAT = SUM, ALT = ONE-PLUS-MAX visible at the call site), then the per-kind dispatcher (`vm_cost_cat/alt/call/cap/atomic/kreset/look`, the free kinds one shared `return c`), the shared alt-flatten helper iff the two walks prove identical (reported either way); F6: PCREC_NO_COUNTER read where the cursor/revdet deny flags are read, the three alike. Design record: docs/dev/reviews/2026-09-20-frank-tour.md [TOUR-2]. Proof: emit_sweep 0 movers on five streams AND the size log's stamped ceilings 0 movers by column; anchors 285/285; make strict; make test at merge. Sequenced BEFORE [TOUR-1] (same file).
  - [TOUR-4] STATE:completed (MERGED d29290ce; GATED 2026-09-21 01:5x, seventy-third session: darwin `make test` at 1691c590 40/40 sections, 0 checks failed, sole red the standing nm arm_a.o probe; size log 0 movers / byte-identical total; strict clean; anchors 286/286 after every merge — formerly STATE:started: LANE `tour4` LAUNCHED 2026-09-20 ~17:3x, sonnet, worktree worktrees/tour4, branch lane/tour4, branch point 82dd396a; carries [ORG-7]) — DFA_INVARIANT abort → pcrec_ctx_fail on the compile path (r61 F1; design record: docs/dev/reviews/2026-09-20-frank-tour.md [TOUR-4]). THREE sites at 82dd396a (dfa.c:590, 667, 857), each carrying its invariant's text; the stale "this file's idiom" comment rewritten; K61 in known_issues.md; a sabotage row forcing an invariant false and expecting the refusal (never a crash); match_api.md unchanged because the fix makes it true. Proof: make test + emit_sweep 0 movers on five streams + the new row detected under run_sabotage_matrix.sh.
  - [ORG-7] STATE:completed (MERGED d29290ce with [TOUR-4] — FIVE exports static (tune_row, bufsurface_inert, dfa_axis_cands, registry_verb_name_limit, rxt_constraint_name); FOUR have NO caller anywhere, not even in their own file (emit_abi_types, nfa_has_asserts, rxt_schema_opens_group, rxt_source_ncols) — dead code, deletion is a separate ruling (Frank); GATED 2026-09-21 01:5x, seventy-third session: darwin `make test` at 1691c590 40/40 sections, 0 checks failed, sole red the standing nm arm_a.o probe; size log 0 movers / byte-identical total; strict clean; anchors 286/286 after every merge — formerly STATE:started: folded into lane `tour4`, 2026-09-20) — nine `pcrec_` exports with no reader outside their definer → static, internal.h declarations deleted (design record: docs/dev/reviews/2026-09-20-code-org.md [ORG-7]; sites at 82dd396a: tune.c, emit_dfa.c ×3, nfa.c, mod_verbs.c, rxt_schema.c ×2, rxt_source.c). Gate: make strict + tests/spec_mod0/check01_isolation.sh + the function census's export column re-pinned.
  - [TOUR-1] STATE:completed (MERGED 672b4cdd; GATED 2026-09-21 01:5x, seventy-third session: darwin `make test` at 1691c590 40/40 sections, 0 checks failed, sole red the standing nm arm_a.o probe; size log 0 movers / byte-identical total; strict clean; anchors 286/286 after every merge — formerly STATE:started: LANE `tour1` LAUNCHED 2026-09-20 ~18:5x, opus, worktree worktrees/tour1, branch lane/tour1, branch point 78058db7 = main with [TOUR-2] merged) — pcrec_emit_vm at one altitude: `vm_init`, the plan tail finished, one function per artifact section in the artifact's order (prologue, vm_emit_stamps, vm_emit_storage, vm_emit_search_body, vm_emit_entries, epilogue), pcrec_emit_vm becomes eight or nine calls; the seam-crossing locals decided per local (Vm as PLANNED FACTS or a per-phase struct — the VmCaps precedent — never a bag); every setup essay pruned to its invariant + a pointer to the decision/plan row it narrates. Design record: docs/dev/reviews/2026-09-20-frank-tour.md [TOUR-1] (measured at 11ff5f51). Proof: emit_sweep byte-identical on five streams, anchors re-aimed 285/285, not an abi event.
  - [TOUR-3] STATE:completed (MERGED cf710c7d + landing 6ee551f2 (tour3rev: ordering PRESERVED, 40,740 cells identical; K62 found out of scope); GATED 2026-09-21 01:5x, seventy-third session: darwin `make test` at 1691c590 40/40 sections, 0 checks failed, sole red the standing nm arm_a.o probe; size log 0 movers / byte-identical total; strict clean; anchors 286/286 after every merge — formerly STATE:started: LANE `tour3` LAUNCHED 2026-09-20 ~18:5x, sonnet, worktree worktrees/tour3, branch lane/tour3, branch point 78058db7; the opus read-only review of the member reader's claim ordering follows delivery) — parse.c p_class: one `cls_read_member` at both endpoints (removes the quote-open mirror and the duplicate four-way decode), `p_class_range` extracted, wave narrative pruned with EVERY measured PCRE2 cell kept verbatim (D26). Design record: docs/dev/reviews/2026-09-20-frank-tour.md [TOUR-3]. Proof: tests/classes + reject table + registry checks, emit_sweep 0 movers; the review confirms the K12 endpoint rule's steps 1-4 and the deferred-refusal ordering survive.
  - [TOUR-5] STATE:completed (MERGED 3fe96ed1 + wording 1691c590; GATED 2026-09-21 01:5x, seventy-third session: darwin `make test` at 1691c590 40/40 sections, 0 checks failed, sole red the standing nm arm_a.o probe; size log 0 movers / byte-identical total; strict clean; anchors 286/286 after every merge — formerly STATE:started: LANE `tour5` LAUNCHED 2026-09-20 ~17:3x, opus, worktree worktrees/tour5, branch lane/tour5, branch point 82dd396a) — select_engine.c: `esel_of()` as the nine-arm ladder with the NON-OVERLAP argument stated ONCE as a table in its header (replacing the five stacked blocks), the unasserted premise (size-drop rung and overflow rung exclusive) made an internal-error check; `prefilter_decision()` extracted; the zero-hook `discharge` fixpoint DELETED (D77). Design record: docs/dev/reviews/2026-09-20-frank-tour.md [TOUR-5] (r61 F2). r61 F6 goes to [TOUR-2]'s lane (emit_vm.c has one writer at a time). Proof: registry stamp checks, tests/axes (the deny/force matrix), emit_sweep 0 movers on five streams, make test.
- [TOUR-EXEC] STATE:completed (CLOSED 2026-09-21 ~08:1x, seventy-third session: GATE COMPLETE at 1691c590 — darwin make test 40/40 sections / 0 checks failed (sole red the standing nm arm_a.o probe); make test-axes: all 32 axes answer-identical to default over the corpus, 21,572 s wall; form census floors OK + synthetic witnesses asserted (run alone after the chain's own 6 h timeout cut it off — a bound sized too small, not a red); size log 0 movers; abi 27 unchanged. Six item rows archived. — formerly STATE:started: ALL SIX ROWS MERGED AND GATED 2026-09-21 01:5x — rows archived in plan_completed.md; this row closes at the `make test-axes` trailer on 1691c590 (in flight, build/gate_1691c590/) + push; OWED after: the tools/review census regeneration, tour2's S154 witness, the four dead exports ruling, K62. ASSESSMENT WRITTEN 2026-09-20 ~17:3x, seventy-third session — the "Manager's assessment" section at the end of docs/dev/reviews/2026-09-20-frank-tour.md; all five TOUR items + ORG-7 = DO, r61 F3/F4/F5 forgone with a trigger; rows [TOUR-1..5] + [ORG-7] below track the lanes; wave 1 = TOUR-4+ORG-7 / TOUR-5 / TOUR-2, wave 2 = TOUR-1 / TOUR-3; branch point 82dd396a. RULED by Frank 2026-09-20 at session close: "on wake, tackle the findings from the tour report. assess the items and do those that you deem worth it. it is ok to forego unimportant ones. then we'll move on to another effort." The list: docs/dev/reviews/2026-09-20-frank-tour.md [TOUR-1..5] (readability tidy-ups, byte-neutral by construction, emit_sweep 0 movers the proof); the code-org list `2026-09-20-code-org.md` [ORG-1..8] is NOT in scope except ORG-7 (nine no-reader exports → static, small, worth it). Manager's assessment first (one paragraph per item: do / defer / forgo, with the reason); **every item the assessment says DO becomes its OWN plan row (`[TOUR-n]`, STATE:started when its lane launches) so the work is tracked here consistently — Frank's ruling at close, 2026-09-20: "migrate tour items you decide to tackle to plan items"; the tour file stays the design record the rows cite**; then lanes: TOUR-4 (sonnet, K61) and TOUR-5 (opus) first — they are r61's act-on-it findings; TOUR-2 (sonnet) + ORG-7 (sonnet) cheap; TOUR-1 (opus, the biggest, essay pruning included) and TOUR-3 (sonnet + opus review) by size. Each lane: worktree, incremental commits, emit_sweep against the branch point, anchors 285/285, make strict; merges serialized with make test between; NO merge while a battery is in flight.)

## Completed 2026-09-22 (lane closefold: Frank's ruling on [BACKLOG-TRIAGE]'s close/fold candidates, backlog_triage_2026-09-22.md §3 — "Agree with close items")

- [DD-1] STATE:completed (CLOSED 2026-09-22, lane closefold, Frank 2026-09-22, backlog_triage_2026-09-22.md §3: delivered under [M5.0] stage 4 (DD-1's fold closure, utf8s4_report.md)) — formerly STATE:not-started — case-insensitivity design: UNICODE folding vs byte-wise automata (before M5) (R1 A-7). The ASCII half is CLOSED by OS-1/D23 — it folded into class construction and is a parser change, not an engine question. What remains here is genuinely Unicode: multi-byte fold pairs, one-to-many foldings and the fold-before-negate rule over byte-range trees rather than a 256-bit bitmap

- [DD-12] STATE:completed (CLOSED 2026-09-22, lane closefold, Frank 2026-09-22, backlog_triage_2026-09-22.md §3: superseded by docs/design/utf8_design.md and [M5.0]) — formerly STATE:not-started — the UTF ARCHITECTURE sketch (Frank,
  2026-08-12 tenth-session close; elaborates APPROACH §4/§10, OS-2, DD-1,
  D33 §7 into one position). (1) ONE parser, no encoding parameter in the
  grammar: the parser's semantic output becomes a CharSet — sorted CODE
  POINT intervals (the D33 §7 widening and DD-1's "byte-range trees" are
  this) — and the encoding is a LOWERING instance, CharSet → byte-level
  NFA fragment: ASCII = identity byte map, UTF-8 = interval-to-byte-
  sequence expansion with suffix sharing (the RE2/Ragel construction, so
  \p{L}-sized sets stay near-linear). Downstream (subset construction,
  minimization, emitter, prefilters) stays encoding-blind and BYTE-WISE —
  OS-2's fold prediction, made concrete. Parser changes only where UTF
  changes the LANGUAGE: \x{>FF} becomes meaningful, a multi-byte atom
  quantifies as one unit (free once atoms are lowered fragments), pattern
  validity. (2) UTF-8 AT MATCH TIME, ALWAYS — never convert the subject:
  UTF-32 conversion costs a decode pass + 4x memory, kills the byte
  prefilters/skips, breaks the byte-offset API (PCRE2 reports byte offsets
  even under UTF) and M3 streaming. Code points exist ONLY at regex-compile
  time, inside the CharSet, between parse and lowering — that is the right
  home for the "convert to UTF-32" instinct. The backtracking worry is
  bounded: the DFA never backtracks; the M4 VM steps back a character by
  skipping ≤3 continuation bytes (self-synchronization), O(1). (3) Invalid
  UTF-8 is a DECISION: byte-wise automata naturally treat invalid
  sequences as nomatch; PCRE2_UTF errors, but PCRE2_MATCH_INVALID_UTF is
  essentially the byte-wise semantics — measure against THAT mode and pick
  deliberately. (4) The oracle pipeline extends with a UTF twin of PC-4
  (compiled PCRE2_UTF), carrying the R13/R14 warning verbatim: a UTF sweep
  needs generators that can PRODUCE multi-byte constructs, or it counts
  the generator. (5) Fold-before-negate and the one-constructor-owns-fold
  seam (OS-1) carry over at the CharSet level; DD-1's Unicode fold pairs
  land there. (6) Scope: ASCII + UTF-8 only (D18 earn-its-axis; UTF-16's
  surrogates make byte automata messy and no consumer asks); encoding is
  a generation-time scalar (D20, --encoding), named entry points via OS-0
  if anyone wants both from one binary. Owners: the CharSet widening is
  MOD-0.6's (D33 §7); the lowering instances and the UTF PC-4 twin are
  M5's; DD-1 folds in at the CharSet level. (7) FRANK'S CONSTRAINTS
  (2026-08-16, twenty-seventh session, ruled into this row as
  requirements): NO encoding conditionals anywhere — no "if utf do x
  else y" in the compiler, the emitter, or the emitted artifact;
  encodings are SEALED backends behind the one lowering interface, all
  specialized code within. The include-package question ANSWERED with
  the two-seam characterization: per-encoding inline-function headers
  are the WRONG seam for the hot path (gcc cannot invert decode+compare
  back into a byte automaton; malformed-input handling degrades from
  automaton structure to runtime branches; the reverse pass would need a
  second backward-decode shim) and the RIGHT seam for the enumerable
  runtime-identity RESIDUE (caseless backref comparison under M6xM5,
  optional subject validation, grapheme \X if ever, trace printing) —
  ONE per-encoding header embedded at generation, so the artifact
  contains exactly one encoding's code and the "switch" is which header
  text was emitted. ENFORCED BY CHECK, NOT CONVENTION, when M5 lands:
  (a) OS-2's hot-loop shape-identity check ASCII-vs-UTF-8 as a pinned
  structural test; (b) a codegen-structural check that no hot-loop label
  calls into the encoding header (allowlist of named residual sites).
  INVARIANTS: subject and all reported offsets are BYTES, permanently,
  third encoding included; fixed-vs-variable width is a PROPERTY the
  backend exploits (fixed-size lowers to fixed-length chains / direct
  indexing), never an interface axis. THIRD-ENCODING RECIPE (the
  planned-for threat): a new backend = one lowering module + one
  residual header, core and emitter untouched — if adding one ever
  requires touching a shared file outside the backend directory, that is
  the derailment signal and a design stop. (8) PER-PATTERN RULING
  (Frank, 2026-08-18, thirty-second session, D58): the generation-time
  scalar is per COMPILE CALL — a pcrec_options field + `--encoding` —
  never process- or file-global; mixed encodings in one compilation
  unit or binary are SUPPORTED BY CONSTRUCTION (self-contained
  artifacts, distinct prefixes, each embedding exactly one encoding's
  residual block). The residual-seam half of this row is built EARLY as
  [M5-SEAM] (D58 ordering: seam → M6 → the rest of M5); the lowering
  instances, oracle twin, and both M5-time structural checks named in
  (7)(a) remain M5's

- [DD-7] STATE:completed (CLOSED 2026-09-22, lane closefold, Frank 2026-09-22, backlog_triage_2026-09-22.md §3: both halves dispositioned — capture prefilter answered by engine_m4.md §7.1; `^`/`$` absorption re-homed to [ENG-ABS]; the M4.3 panel happened (plan_completed.md's own "Completed 2026-08-14" [M4.3] archive entry confirms the D6 panel ran)) — formerly STATE:not-started — engine unification ownership (R2-A6), SPLIT 2026-08-14 (D42.7): the WHICH-machine-is-the-capture-prefilter half is ANSWERED by engine_m4.md §7.1 (both existing machines, unchanged — the capture-erased forward+reverse pair is exact for the capture-only tier), pending the M4.3 panel; the `^`/`$` ABSORPTION half is RE-HOMED to [ENG-ABS] (with the OPT rows) gated on a measured loss existing first — GATE SATISFIED 2026-08-18 (D63): (?m)^'s quadratic crossing-body curve is measured (3.99x/doubling, 1996x at n=64k) and the D63-chartered ENG_ATTEMPT prefilter deliberately does not rescue it; the reverse BOT variant is UNPARKED as sequenced follow-on work queued behind the [M6.2] waves; DD-4 (\G) keeps its note — `nfa_wrap_unanchored` bakes in the self-loop with no toggle (confirmed STRUCTURAL, engine_m4.md §7.3)

- [BENCH-1] STATE:completed (CLOSED 2026-09-22, lane closefold, Frank 2026-09-22, backlog_triage_2026-09-22.md §3: FOLDED into D119's [OPTLOOP] (the bench repo D78 + the cause-ranked analysis are its two jobs)) — formerly STATE:started — FEATURE-SPANNING BENCHMARK EXPANSION + THE PRIORITIZER (Frank, 2026-08-13 sixteenth session): today's bench is 9 cases (a-i) of deliberately basic shapes — good regression gates, not a capability map (Frank: "whenever i see benchmarks, its usually a series of rather basic benchmarks that do not really exercise the capabilities"). Build a benchmark that SPANS the feature set and the complexity range: per-feature-family case GROUPS (literal/memchr shapes, classes, alternation/trie widths, bounded repeats, anchors/EOL, dense/counting — the case-f family, captures (M4), backrefs/lookaround/atomic (M6), UTF-8/\p (M5), plus real-world-shaped patterns), each family at graded complexities; pattern sources = hand-designed families + the PCRE2 testdata import (M7 — this row is deliberately scheduled around that import so the corpus arrives with it) + generated shapes where a family needs a sweep. STRUCTURED FOR SPOT-CHECKS exactly like TT-1's tiers: every case and group individually addressable (make bench CASE=... / GROUP=...), the full sweep at evaluation points only. TWO INSTRUMENTS, deliberately distinct — M2.11's ruling stands: the regression GATE stays absolute per-case floors (cross-engine ratios move for reasons that are not our regression); the new PRIORITIZER is a cross-engine RELATIVE ranking vs libpcre2 — informational, never a gate — whose output is a worst-first worklist. Frank's stated optimization workflow, recorded as the row's purpose: (1) OPT-A's survey incl. the pattern-generation study, then (2) work the prioritizer list from the relative worst downward. Every number under D12/D17/R3.10 discipline; MECH-3's provenance-refusing wrapper is the intended measurement vehicle and lands first. Sequencing: after the main feature set is built and proven (post-M6, with M7's testdata), BEFORE the OPT waves open — this row is the OPT waves' worklist generator. AMENDED 2026-08-13 (same session, positioning discussion): the case groups include a LATENCY / SHORT-SUBJECT group — time-to-first-match from process start (the AOT structural win: tables page in from .rodata vs pcre2_compile + JIT warmup per process) and per-call overhead on short subjects (log lines, field validation — the dimension real workloads are dominated by and typical benchmarks skip); and the prioritizer gets a second reading — the BEST relative cells feed the positioning note (Beyond M7), not just the worst cells feeding the fix list. AMENDED 2026-08-14 (D42.8): the prioritizer worklist has a KNOWN HEAD before it runs — case (f) at 0.151 relative, re-homed here from [DD-9] (archived) with engine_m4.md §8.4's three findings attached (wrong-lever computed goto; ~2x reverse-pass share; bit-parallel shift-and candidate); [OPT-SIMD] is the adjacent lever row. **CHARTERED 2026-09-03 ~16:5x (Frank: "Let's charter it") AS THE SYNTAX CENSUS — I-42 in the bench inbox: a wide-net sub-bench across every BUILT construct (`pcrec --list-syntax` is the seed; patterns written from the PCRE2 syntax reference, blind to the emitter — D27), one or two canonical patterns per construct plus one in context, standard subjects, the six pinned testees × three regimes on the existing instrument; first sample in ONE night (the third night from now at the earliest); an outlier rule stated before the run (ratio vs the JIT outside a band, refusals on built constructs, compile-time/size cliffs, engine-selection surprises from the stamps); OUTPUT = a ranked list of QUESTIONS that become depth probes before any pcrec row — the census widens the queue on purpose. Bench-owned; pcrec owes the registry seed and the answers.**

- [OPT-4.2] STATE:completed (CLOSED 2026-09-22, lane closefold, Frank 2026-09-22, backlog_triage_2026-09-22.md §3: Frank's ruling "WAIT FOR A WITNESS — no row, no hunt" stands as a closed disposition; the impact-bounded finding recorded; cross-referenced in known_issues.md K41) — formerly STATE:started (STARTED 2026-08-31 forty-eighth session, lane o42 / `lane/o42`, sonnet — Frank's close ruling "next session proceed with queued items" read as the charter per wake.md, to be confirmed in one line when he's present; manager's design pin: the rungless decline gets its OWN ESEL value, the internal.h invariant stays true with its comment extended; S216 assigned; the bench re-measure inbox item goes at merge) — **DELIVERED GREEN 2026-09-01 03:15, awaiting merge review**: branch `lane/o42` 15 commits, `ESEL_DECLINED_NULLABLE_DEFAULT` (no abi bump — gate (A) 0 differing, [OPT-4.1] precedent), prefilter 32/32, resource 30/30, registry 600/600, codegen 198/198, sweep 2,845/50 moved all-clean, S216 DETECTED; OPEN at merge: the rung-scoped value's WITNESS GAP (SEL-1 state-cap path live in principle, unexercised — build a witness vs accept, manager's call) and the bench cls-* re-measure inbox item (FILED 2026-08-31 by the manager from battery 7's diagnosis; NEEDS FRANK'S CHARTER — it changes a bench-bucketed stamp surface) — EXTEND THE NULLABILITY DECLINE TO EVERY PREFILTER RUNG (the general form of [OPT-4.1]'s gate, per the general-mechanisms rule): today `fit.prefilter_declined_nullable` requires `collapse_reason != CR_NONE`, so an ORDINARY hybrid whose EXACT language is nullable still builds — a scan that can never dismiss a position (bench O-10: 1.2-9.9x loss on that shape). The population GREW when [OPT-5] landed: `(a|b){0,30000}`-family patterns that used to be size-REFUSED now compile into exactly this config (MEASURED 2026-08-31: hybrid/exact/nullable, 34,522 B). Pinned loud and dated by tests/resource's [OPT-4.2 tripwire] cell until this row lands. DESIGN CARE OWED: `ESEL_DECLINED_NULLABLE` is currently rung-scoped with a documented invariant (`>= ESEL_OVERFLOWED_DFA` implies a state-cap overflow, internal.h) — the rungless decline needs either its own value (registry legs + spec + abi ritual) or a deliberate, documented invariant change; do NOT reuse the value silently. Also the pre-existing population (VM-chosen nullable patterns that have carried useless hybrids all along) changes stamps — the bench re-measures its cls-* hybrid cells after this lands (their 1.2-9.9x loss is the predicted WIN). **o42 witness-gap RULED (Frank, 2026-09-03): WAIT FOR A WITNESS — no row, no hunt; the trace in tests/resource/run_resource_tests.sh stays the record. Impact bounded: both errors on the unwitnessed retry path are performance-only (a prefilter is a filter, never the answer).**

- [TT-14] STATE:completed (CLOSED 2026-09-22, lane closefold, Frank 2026-09-22, backlog_triage_2026-09-22.md §3: FOLDED into [TT-4M]/[TT-4M-TIME] (the same charter, built there); [TT-15] stays distinct) — formerly STATE:not-started (CHARTERED 2026-09-04 evening, fifty-third session, by Frank on the Mac timing measurement: "from a practical perspective, we are going to need to figure something out because otherwise we will spend all our time in test. so lets look at batching. i fear a whole test run. i'd like the solution to be switchable so that the tests run on linux fine"; admin column) — EXEC-BATCHING FOR THE HARNESS: THE macOS SPAWN TAX. Facts at chartering (first timed serial `make test-corpus` on the M1 Max, 2026-09-04, scratchpad corpus_timing.log): 27,045/0 green but 1,717.5 s wall vs the old box's 64.1 s (TT-6's isolated figure) — ~63.5 ms/case vs ~2.9, with only 1,067 s of the 1,717 being CPU at all and a THIRD of that sys time (kernel process machinery): the workload spawns ~100k processes (per-case `$TIMEOUT_BIN` + matcher, per-pattern pcrec + gcc) and macOS's fork/exec is ~an order of magnitude costlier than Linux's; compute itself is FINE (worst gcc cell 1.416 s CPU against the 8.0 s Ryzen-sized pin; all 2,962 size-log rows byte-identical to the old box's log). THE LEVER IS ALREADY PRICED: [TT-4.1] Stage A2 measured `corpus` as the ONLY section with per-case matcher exec (19,185 spawns then) — every other section already sweeps subjects inside ONE C driver process, which is also the fix's proven in-tree shape (bref_batch.c, possdiff_driver.c) — and isolated the exec-batching lever at 5.57x on Linux, a measured NO there; at 22x the per-case cost the same lever re-prices to a YES here. STEP 0 (light, ~30 min): decompose the 63.5 ms/case on THIS box — timeout-spawn vs matcher-spawn vs run.sh's own per-case subshell forks — so STEP 1 aims at the measured majority, not the assumed one. STEP 1: DRIVER-SIDE CASE BATCHING — one driver invocation per PATTERN (or per pattern-group) consuming all its cases (subjects + expected kinds via file/stdin, one verdict line per case out), run.sh comparing per line; collapses the two per-case spawns to ~2 per pattern (~9x fewer execs on the corpus's ~9 cases/pattern). CONSTRAINTS, each load-bearing: (a) SWITCHABLE per Frank — an env toggle in the LINTGEN/CLANGGEN shape (say RXT_BATCH), darwin may default ON only after (c) is proven, Linux DEFAULT UNCHANGED (per-case, the calibrated shape), both directions forceable; (b) FAILURE ATTRIBUTION SURVIVES — a batch member's crash/timeout re-runs that pattern per-case so the failing CASE is named (the batch mode may never turn one case's crash into a whole-batch mystery), and the lost-worker-hard-fails discipline holds; (c) ANSWER IDENTITY BETWEEN MODES is the acceptance — one full corpus run per mode, identical summaries and identical per-case verdicts (the test-axes shape applied to the harness itself); (d) D45 budgets COMPOSE, not stretch — the batch's execution budget derives from gen_run's per-case number times its member count, a member timeout attributes per (b), and the budget arithmetic lives in gen_timeout.sh where D45's single implementation already is; (e) the driver template's RX_NCAPS/runtime-ncaps discipline (tests/fuzz's shared-driver lesson) applies to any driver reuse across patterns. NOT this row: TU-batching of gcc compiles ([TT-4.2]'s measured obstacles stand; gcc is the next-largest cost after execs and parallelism, revisit only if STEP 1 + PROCS leaves the wall unacceptable), pcrec-side multi-pattern compilation (product change), the other sections (already batched by construction). SEQUENCED BEHIND the [MACPORT] merge (same files: tests/harness/run.sh, driver.c). Sonnet-sized with the manager reviewing the budget/attribution design; the STEP 1 differential (both modes, full corpus) is the merge bar. **RE-SEQUENCED same evening (Frank: "one option i considered was setting up a test harness for a cloud machine. i'd rather do that then spend 20 hours on a simple pre-merge test suite"): a CLOUD LINUX RUNNER for make test + the battery is the preferred first move — it restores the calibrated environment (budgets, pins, sanitizers, battery shapes) wholesale and covers the tier no Mac-side batching reaches (san is gcc-sanitizer-dependent, mech's 222 tree-rebuilds under the spawn tax); this row DEMOTES to the local inner loop's quality-of-life, picked up only if targeted sections still chafe after the runner exists. The runner's harness-side work (workflow file or a run-remote + trailer-poll script) is its own charter when Frank picks the vehicle.**
## Completed 2026-09-22 (lane admin1: MACPORT-XARGS discovered already fixed)

- [MACPORT-XARGS] STATE:completed (DISCOVERED ALREADY FIXED 2026-09-22 by lane admin1, sonnet, in a session bundling this row with [LIM-OVR] per the manager's own admin-column pairing: Frank himself closed every remaining `xargs -a` call site in `tests/rxtsource/run_rxtsource_tests.sh` directly, commit fb1b9c5e ("tests/rxtsource/run_rxtsource_tests.sh: fix xargs -a and wc -l padding", 2026-09-10 12:55:40 -0400), four days AFTER this row was chartered and never re-flagged — that commit's own message records the population this row named: "xargs -a's failure cascaded into 11 of the 14 test-rxtsource FAILs" and fixed all six remaining sites via the portable `xargs CMD < "$FILES"` form, taking the suite from 106 passed/14 failed to 115 passed/3 failed (the residual 3 were an unrelated python3-oracle divergence and a TMPDIR-length message-truncation finding, both explicitly out of that commit's scope and unrelated to xargs). LIVE-VERIFIED by this lane on this box at branch point 69172a00: `bash tests/rxtsource/run_rxtsource_tests.sh` reads **212 passed / 0 failed / 1 recorded** — zero FAIL lines of any kind. The one RECORD line ("C3: population pins are python 3.14's numbers; this python (3.9)'s deltas...") is the pre-existing, already-documented darwin python-version note (btriage_20260917_report.md), not a failure and not xargs-related. A tree-wide grep for `xargs -a`, `-d`, `--arg-file`, `--max-lines` and other GNU-only xargs spellings found NONE outside historical prose comments explaining why those sites were avoided — every live xargs call in the tree (`tests/mrl/run_mrl_tests.sh`, all of `tests/codegen/run_*_identity.sh`, `tests/registry/limits_check.sh`, etc.) already uses the portable `xargs CMD < FILE` or `... | xargs -0 CMD` form. `docs/testing.md` carries no darwin-known-reds text citing a 14-failure xargs class either, so no re-pin was owed there. No code change was needed or made by this lane. Linux verification command for the executor (unchanged in shape by this row, since nothing here touched behavior): `bash tests/rxtsource/run_rxtsource_tests.sh` on ubuntubudu/pcrecdev2 — expect the identical PASS population to darwin's 212/0/1 (the RECORD line's exact wording may cite the Linux box's own python3 minor version instead of 3.9, which is expected version-sensitivity per the existing C3 note, not a divergence). **Process finding, not this lane's to fix**: `docs/dev/backlog_triage_2026-09-22.md`'s own MACPORT-XARGS row (delivered by lane backtri hours earlier the same session) cites the same now-stale "14 pre-existing failures, A/B'd" figure as evidence the row was ready to schedule, rather than as a citation of an already-fixed defect — flagged to the manager in this lane's handback rather than self-edited, since that inventory is another lane's delivered artifact.) (CHARTERED by the manager 2026-09-06 from stage 3's full-run A/B; admin column, sonnet, bundle with [LIM-OVR] in the next admin lane) — `tests/rxtsource/run_rxtsource_tests.sh` legs B/C use `xargs -a`, a GNU-only option BSD xargs refuses, so those legs and everything downstream have NEVER run on darwin (14 failures, identical at branch point and tip — pre-existing, A/B'd by lane utf8s3). Portable rewrite (pipe into xargs or a while-read loop), then re-run the full rxtsource suite on this box and re-pin the darwin expectation; the Linux arm must stay byte-identical in behaviour (verify at the next Linux slot).

- [LIM-OVR] STATE:completed (DELIVERED 2026-09-22 by lane admin1, sonnet, bundled with [MACPORT-XARGS] in the session's admin lane: audited all six BUILD_D-override rows in `src/core/limits.def` against `cli/main.c`'s `raise_only_limits[]` table and found FOUR, not one, carrying the false "-D, never a caller lever" claim -- `PCREC_MAX_AUTO_DFA_ELEMS`/`PCREC_MAX_VM_EMIT_CODE_BYTES`/`PCREC_MAX_EMIT_BYTES` (each has a real raise-only flag through the table) plus `PCREC_DEFAULT_WARN_EMIT_BYTES` (a real, non-raise-only `--warn-emit-bytes=` flag, wired through cli/main.c's own bespoke else-if chain rather than the table -- found only by reading the flag's actual wiring, not by trusting the charter's "audit the other five" framing, which undercounted by missing this one). Built the new token FLAG_D exactly as scoped: identical `-D`-movable-default generation machinery to BUILD_D in `src/core/limits.h`'s dispatch macros (`PCREC_LIMIT_LIMITS_H_FLAG_D`, same body, one more `#undef`), zero change to the `#ifndef`/`#define`/`#endif` wiring blocks (keyed on row NAME, never on override token), and an honest dump rendering in `src/dump/limits_dump.c`'s `override_name()` -- BUILD_D stays "-D" (still true for its two remaining rows, `PCREC_ANCHORED_MAX_STATES`/`PCREC_SIZE_TERM_THRESHOLD`, which really have no caller lever), FLAG_D renders "flag+-D". `docs/spec/limits.md` §3.4a's override vocabulary gained the fourth spelling (D80, caller-observable). THE OWED CHECK ALSO BUILT: `tests/registry/limits_check.sh` part 4 (was "three parts", now four) reads `cli/main.c`'s `raise_only_limits[]` table BY GREP (independent of limits.def, K35's own rule) plus the one bespoke `--warn-emit-bytes=` site, and cross-checks BOTH directions against every `-D`/`flag+-D` dump row -- a row with a real lever whose override does not say so (the exact [LIM-OVR] shape), or a row claiming one it lacks. SABOTAGE-VALIDATED LIVE (scratch: reverted `PCREC_MAX_EMIT_BYTES`'s token to BUILD_D, rebuilt, confirmed part 4 fails naming the row and the shape, reverted before commit) and S208 RE-AIMED (its `SAB_BEFORE`/`SAB_AFTER` anchors quote `PCREC_MAX_VM_EMIT_CODE_BYTES`'s full row text, which moved from BUILD_D to FLAG_D plus a derivation note -- verified byte-for-byte against the live limits.def line before committing the re-aim) and re-verified DETECTED at the same predicted cell. Also updated every LIVE reader found by grep across the whole tree (root CLAUDE.md's D94 discipline, applied to a registry-dump change rather than an abi bump -- this is NOT an abi event, `--list-limits` is compiler-side registry surface, not emitted-artifact scaffolding): `src/core/limits.def`'s own header vocabulary and mechanism comment (the worked example there was `PCREC_MAX_VM_EMIT_CODE_BYTES`, itself one of the four moving rows), `src/core/limits.h`'s dispatch-macro comment, `src/core/CLAUDE.md` and `src/ir/CLAUDE.md` (both cited BUILD_D by name for `PCREC_MAX_AUTO_DFA_ELEMS`), `tests/codegen/run_n1_budget.sh` and `tests/codegen/CLAUDE.md` (same row, same citation), `tests/registry/CLAUDE.md`'s limits_check.sh entry. `make -j4 CC=gcc-16` and `make strict CC=gcc-16` both clean; `tests/registry/limits_check.sh` 27/0 (was 21/21 at [LIM-1]'s own count, now three more PASS lines for part 4); `make test-codegen CC=gcc-16` run as validation (see this session's admin1 report for the result). No `docs/spec/` hunk beyond limits.md §3.4a was needed (no other spec section states an override-column value for any of the four moved rows). The D26-tier "elements"-vs-"state-set elements" unit-harmonization residual the charter's own last sentence named is DELIBERATELY UNTOUCHED here, per that sentence's own instruction ("harmonize opportunistically at a future abi event, never alone").) (CHARTERED 2026-09-06 by the manager at O-18 §3's finding; admin column, sonnet-sized, bundle into the next admin lane) — THE LIMITS DUMP'S `override` COLUMN CANNOT EXPRESS THE TWO-LEVER SHAPE: rows with BOTH a raise-only caller flag AND a -D-movable built-in default (PCREC_MAX_AUTO_DFA_ELEMS via --max-auto-dfa-elems; audit the other five BUILD_D rows against cli/main.c's raise_only_limits[] — the --max-emit-* family is the same shape) render `-D`, whose documented meaning in limits.def's header is "never a caller lever" — a false claim the bench read at face value (O-18 §3(a)). The token is SEMANTIC (BUILD_D drives limits.h's #ifndef/_DEFAULT machinery; a naive flip to FLAG breaks the build — measured 2026-09-06), so the fix is a new token (e.g. FLAG_D) carrying BUILD_D's generation machinery with an honest dump rendering, + limits.def header vocabulary, + docs/spec/limits.md §3 hunk if it restates override values (D80), + limits_check re-pin if content is pinned. Also owed here: a check that ties every row's override token to the CLI's actual flag table (the drift had no detector — learnings §3 shape), and D26-tier note: the N1 _WHY's "elements" vs K7's "state-set elements" is the same unit (Ctx.subset_elems); harmonize opportunistically at a future abi event, never alone.

## Completed 2026-09-22 (manager: cycle-1 analysis rows closed on Frank's ratification)

- [BENCH-REVIEW] STATE:completed (COMPLETED 2026-09-22: delivered as [OPTLOOP.1.analysis] (lane optrev) + the captures-vs-captures view (lane capsview) + the I-85 profile reading (lane profread); Frank ratified the six rows and batch 1 the same day) (DELIVERED 2026-09-22 as [OPTLOOP.1.analysis] — see that row; closes when Frank ratifies the mechanism list) (CHARTERED by Frank 2026-09-19, D113; RE-SCOPED 2026-09-21 by D119 as [OPTLOOP] cycle 1's analysis step, on the `capability` subbench first — Frank: "made for this purpose and has some examples already"; deliverable: n≈5 targets ranked by the D119 priority rule, bucketed by cause via the D81 stamps, each with a why-slower diagnosis and a plan or a fundamental/deferral disposition) — analysis of the bench's results as of that time: its reports (findings needing attention — e.g. the pcrec HANG on an evil adversarial pattern) and its SUMMARY MATRIX (every engine × every case) for optimization priority → proposed plan rows, ratified by Frank together with [BACKLOG-TRIAGE]. After [REL-1].

- [BACKLOG-TRIAGE] STATE:completed (COMPLETED 2026-09-22: delivered (lane backtri), Frank ruled the six closes/folds, applied (lane closefold); column proposals recorded; features HELD by Frank unless quick) (DELIVERED + MERGED 2026-09-22, lane backtri: docs/dev/backlog_triage_2026-09-22.md — 93 rows = 81 ANCHORED not-started + 12 dormant started; the "102 at open" figure was an unanchored grep counting "formerly STATE:not-started" prose; three column proposals M3.0 / ENG-DIRECT (pending optrev's cause ranking) / MACPORT-XARGS+LIM-OVR; 6 close/fold candidates; awaits Frank's ratification together with optrev's mechanisms; closes applied 2026-09-22 (lane closefold): DD-1/DD-12/DD-7/BENCH-1/OPT-4.2/TT-14 archived to plan_completed.md, [BENCH-1]'s dependency text re-pointed at [OPTLOOP] in 7 rows) (CHARTERED by Frank 2026-09-19, D113) — the not-started rows (97 today) triaged into the three-lane columns (D86) alongside [BENCH-REVIEW]'s rows → one ranked future-work list Frank ratifies. With [BENCH-REVIEW].

## Archived 2026-09-22 (lane admin2: the resident completed rows the header promised were archived — see docs/dev/plan.md's header for the STATE vocabulary)

### M5 — UTF-8

- [K50-NULLGATE] STATE:completed (CLOSED 2026-09-19, seventy-first session, per docs/dev/plan_audit_2026-09-19.md: delivered, tag stale — Frank\'s ruling on the audit) — formerly STATE:started (CHARTERED 2026-09-06 fifty-sixth session at the K50 merge's encoding-checks red; lane k50bnd continues — the manager's ruling on the lane's own disposition (B)) — NARROW THE [K50] BOUNDARY GATE TO MACHINES THAT CAN OBSERVE IT. The gate is a real automaton state on EVERY unanchored utf8 machine regardless of alphabet, which broke DD12a(i)'s strict-identity bucket (243/243 pairs differing at the merged tree — the rebuilt instrument meeting a deliberate machine change, K52's scope problem one row later). The consumption argument: a NON-NULLABLE pattern's match consumes a byte at its start, and no utf8-lowered path begins with a continuation byte, so a mid-character attempt dies on its first transition — the gate is unobservable and may be omitted as pure optimization (this is Frank's general rule holding OBSERVABLY; also deletes the measured 1.33x ENG_ATTEMPT guard cost for provably-safe patterns). THE PREDICATE IS THE MACHINE'S, NOT A PROBE'S: empty-subject nomatch is insufficient (context-dependent zero-width patterns — the (?<=x) family — can accept mid-character while failing the empty subject); the sound condition is whether any attempt-entry state accepts without consuming in any class context, read off the unanchored start closure's accept bits the DFA already computes. Bar: D6 design round if more than one predicate placement; the gate-omitted-on-nullable sabotage direction; its own validation pass; abi 24->25 with the full ritual; the DD12a(i) interim manifest (the K51-shape excusal landed to un-red main) SHRINKS to the genuinely-nullable set as this row's own expiry event — non-nullable machines return to the strict bucket.

- [ENCCHK-DD12A] STATE:completed (CLOSED 2026-09-19, seventy-first session, per docs/dev/plan_audit_2026-09-19.md: delivered, tag stale — Frank\'s ruling on the audit) — formerly STATE:started (GO Frank 2026-09-06 in the admin column beside [K50-BNDSTART]; lane launched same hour, sonnet, worktrees/encchk.) (CHARTERED 2026-09-05 by the manager at K52's filing; admin column, sonnet-sized) — REBUILD DD12a(i)'S INSTRUMENT (docs/dev/known_issues.md K52: vacuous on darwin — objdump -j .text is empty on Mach-O, every historical green was empty-vs-empty — and mis-scoped everywhere: the whole-object compare cannot admit the seam's own per-encoding residual bodies or K49's advance). The repaired check: extraction asserted NON-EMPTY per artifact; compare scoped to the engine MINUS the named encoding-owned regions (marker-delimited source normalization with the normalization count pinned, or per-symbol object compare with the exclusion list printed — the always_inline smear of the K49 advance across the entry chain is why naive symbol exclusion fails, see K52); a real darwin arm or a loud named SKIP; VALIDATED with a planted encoding conditional in the hot loop (the failing direction the current instrument was never shown). Also owed here per the k49fix landing: the cwmax floors' mech row (the matrix's `mrl` token reaches run_mrl_tests.sh §8) and run_encoding_checks.sh's missing mech suite token (S229 scores on the harness arm only until it exists).

- [K53-SELRETRY] STATE:completed (DELIVERED 2026-09-10 by lane utf8k53, branch lane/utf8k53, report docs/dev/lanes/utf8k53_report.md — the ladder built as `Ctx.size_drop_rung`/`SDR_*` with ONE rung, its own comment carrying what a second rung owes (a MEASURED run-time cost per contributor, to order them by); `build_anchored_dfa` reads the rung on the line it already reads `-fno-anchored-dfa`, so D82's single decision point is untouched; NO new stamp and NO abi bump — `ESEL_SIZE_CAP_RETRY` already MEANS "an emitted-size cap forced a retry and the retry shipped", its "reachable ONLY from CR_SIZECAP" clause was a description of the one rung that existed, and the two rungs are mutually exclusive BY ENGINE so `_DFA_MATCH`/`_DFA_PREFILTER` say which fired. ACCEPTANCE: all 14 spellings compile (`\p{L}` 772,418 raw where it refused at 1,076,638); the 16 parked blocks are back at their authored positions in axis04 (12, restoring that file's own stated 148-block count) and axis12 (4), running 590/0 with their carried oracles exercised for the FIRST time and all agreeing; byte-identity 3,348/3,348 over every distinct (pattern, encoding, features) triple against a branch-point compiler; `run_anchored_match.sh` 20/0. TWO FINDINGS THE ROW DID NOT PREDICT. (1) THE CORPUS POPULATION IS NOT THE `\p` FAMILY: 8 corpus patterns stop refusing and every one is a WIDE LITERAL ALTERNATION from `tests/rxtsource/fixtures/bench_altwide_0_2.rxtin` — pcrec-bench's own altwide witnesses — which is this row's "filed as an ENGINE issue, not a Unicode one" discharged rather than merely asserted. **Two cross-lane consequences the manager owns**: the bench's altwide refusal table MOVES, and [LIM-2]'s charter ("the refusal set moves NOT AT ALL", with that table as its before/after control) must be re-based onto this tip. (2) THE CHECK THAT WENT RED WAS THE FINDING: `run_anchored_match.sh` §5's fourth bucket ("the anchored machine overflowed a STATE cap") was defined BY ELIMINATION, so the 8 landed in it and the check reported "a corpus pattern has grown past the 4,096 ceiling" — the right alarm with the wrong cause, on a population that never went near it. A FIFTH bucket keyed on `RX_ENGINE_SEL` fixes it; K35's shape in a classification rather than in a count. New: §6 (the rung driven through two `-D`-capped reference compilers — positive, BOUNDED, and a no-contributor control), sabotage rows S237/S238. Design annotations landed: `anchored_match_unwrapped.md` §5.2a (the promise was enumerated over the budgets the BUILD can cross, and the emitted-bytes cap is charged three machines downstream — "optional" is a claim about every resource a component consumes) and `utf8_design.md` §3.3's refutation (size is states x CLASSES x digits; the section measured one factor of three). FULL BATTERY OWED to the manager. Formerly CHARTERED by the manager 2026-09-06 at stage 3's K53 filing; engine row, opus-small, schedule before M5.0's close — it is the difference between `\p{L}` working and not working under `-e utf8` at default axes) — DROP THE OPTIONAL ANCHORED MACHINE ON EMIT-BYTES OVERFLOW AND RE-EMIT. Five of 45 property names (`C Cn L Xan Xwd`, both polarities) refuse under `--encoding=utf8` at defaults because the OPTIONAL anchored DFA's bytes count toward `max_emit_bytes` (\p{L}: 1,076,640 vs cap 1,000,000; 772,412 WITH `-fno-anchored-dfa` — compiles), contradicting `anchored_match_unwrapped.md` §2/§5.2's "built OPTIONAL — an overflow is a selection outcome, never a diagnostic", a promise `src/core/compile.c` keeps for the SUBSET-ELEMS budget (save/restore `Ctx.dfa_overflowed`) and not for the emit-BYTES one (applied after all three machines emit). The cure is a [SEL-1]-shaped retry: on exceeding `max_emit_bytes` with an optional anchored machine present, drop it and re-emit — observable (`RX_DFA_MATCH` stamps `unwrapped` vs wrapped), strictly better than refusal, own stamp + spec hunk (D80); regression population = `tests/known_fail/k53_uprops_oversize.rxt`'s 12 blocks flip to passing (a NOW-PASSING ratchet event, re-pin known_fail). Also carries the refutation for the design record: `utf8_design.md` §3.3 measured STATES where emitted size is states × CLASSES × digits — one factor of a three-factor product; annotate that section at landing, not silently.

### Beyond M7 — long-term vision

- [TT-6] STATE:completed (MERGED 5935ea9, 2026-08-23 12:1x: tests/lib/timeout_bin.sh resolves TIMEOUT_BIN — GNU when the default is uutils, plain `timeout` elsewhere; every bare call swapped in 9 scripts + scripts/Makefile; MEASURED test-corpus isolated 6:44.24→1:04.08 (6.31x, identical 22,358/0), make -j12 test 10:32.82→10:15.96 (oversubscribed at load 33-41, sleep hidden — the saving shows where sections run serially: the sanitizer axes and mech rows; battery_tt6.log is that number); S43 anchor re-derived, tripwire 118/119; D69 rows S11+S43 DETECTED on the merge in 19 s total; bench COMPILE-SPEED/GCC-TIME budgets had the wrapper's launch cost inside their number — archived gate results predate the swap, flagged in tests/bench/CLAUDE.md) — formerly STATE:started (APPROVED by Frank 2026-08-23 11:1x as #1 of the set; lane/tt6timeout) — THE `timeout` BINARY TAX (found by [TT-4.1]
  2026-08-23, manager-verified: uutils coreutils 0.8.0 `timeout` sleeps
  ~108 ms per call at zero CPU; GNU `gnutimeout` 4 ms). ~10 test scripts
  call `timeout` bare (pcrec calls, every per-case matcher run in
  tests/harness/run.sh:356, gen_cc's wall wrapper). LANDING SHAPE: a
  tests/lib helper resolving TIMEOUT_BIN (prefer GNU when the default is
  uutils; plain `timeout` elsewhere so a stranger's box is unaffected) used
  by every script; before/after `make test` wall on this box (projected
  ≈ −200 s on corpus's 469 s section wall, also on each sanitizer axis
  and per mech row); the D45 timeout semantics (exit 124, SIGTERM→KILL)
  must be re-verified against the GNU binary in the failing direction.
  Measurement is DONE (tt4_measurement.md "The timeout binary itself");
  Frank decides the set with [TT-4.2]/[TT-5] stage 2.

- [TT-5] STATE:completed (CLOSED 2026-08-25 on Frank's ruling, fortieth session. WHOLE-CHAIN BEFORE/AFTER, owed to Frank: BEFORE (m65, 2026-08-22) test 10m14s + ubsan 32m35s + asan 42m25s + mech 60m08s @118 rows ≈ 2h26m; AFTER (the [DD-14] close tree, 2026-08-25) test ~25-37m under -j12 + san ~60m (one combined axis, [TT-7]) + mech ~80m @180 rows PROCS=6 ≈ 2h50m — per row and per case the chain is FASTER ([TT-6] −105 ms × ~23k calls, [TT-7] −18 min, [TT-8]'s PROCS); in wall time it is not, because [DD-14] grew the corpus ~40% and the matrix 52% faster than the moves shrank it. Residue: #5 CCACHE for mech → [CHK-1] item (d), measured in situ before adoption; the [TT-10] load sensitivity → [CHK-1]; D69's premise ("no row observed flipping DETECTED→UNDETECTED from a compiler change alone") has since FAILED — S70 — mitigated by [MECH-REACH], D69 addendum) — formerly STATE:started (2026-08-23, thirty-seventh session; chartered by
  Frank: "we are in the multiple hours for overall testing right now and
  it's slowing development … consider some other testing moves outside
  [TT-4] … perhaps some more profiling will spark ideas") — VALIDATION-
  CHAIN PROFILE AND CANDIDATE MOVES. The per-merge chain measured
  2026-08-22 on 3aa446f/5edba64 (build/battery_m65.log, build/mech_m65.log):
  test 10m14s, strict 6s, ubsan 32m35s, asan 42m25s, lint 33s, mech 60m08s
  (118 rows, PROCS=4) — ~2.5 h, of which the two sanitizer axes + mech are
  ~135 min; `make test` is the SMALLER part, so [TT-4]'s batching only
  reaches the hours if it rides the sanitizer and mech paths ([TT-4.3]).
  STAGE 1 (read-only, from the existing timestamped logs + the drivers'
  source; no runs while the [TT-4.1] census is timing): where the minutes
  go inside each stage (section-level for the sanitizer axes; row-level
  for mech as far as the log allows — it has no per-row timestamps, a
  blind spot to name), what each stage RE-does that another already did
  (the sanitizer axes recompile the whole suite twice; mech rebuilds pcrec
  per row), and a candidate list with the evidence each needs before
  it is a row: e.g. one combined `-fsanitize=address,undefined` axis
  instead of two (halves ~75 min IF the diagnoses stay distinct — docs/
  testing.md SAN-1's reasons for separate axes must be read first),
  mech per-row scoping (which sections a row really needs), CCACHE=1 for
  mech ([TT-3]'s qualified yes), PROCS for mech, pipelining stages on a
  quiet box. STAGE 1 DONE (6f1e941, docs/dev/chain_profile.md: chain
  2h26m on m65; three-log trend; ubsan/asan/mech +20% in one day with no
  growth alarm; SAN-1's separate-axes reason is TSan-specific; mech PROCS=4
  never re-validated at 118 rows and leaks into inner harness sharding;
  CCACHE=1 for mech). CANDIDATE (h), added 2026-08-23 from Frank's
  question "are the sabotage tests dependent on the tests themselves; do
  they need re-running if the tests don't change?": a row's verdict is a
  property of the PAIR (compiler, corpus) — it flips when (1) its
  SAB_HARNESS_TARGET changes (exact, grep-able), (2a) its anchor drifts
  (caught STATICALLY by the tripwire, seconds, already on the bar), or
  (2b) a compiler change elsewhere MASKS or unreaches the sabotaged path
  (S108's single-site shape; NOT derivable from the diff — only a run
  finds it). No row has yet been observed flipping DETECTED→UNDETECTED
  from a compiler change alone. Tiered policy proposed, NOT ruled: docs/
  infra-only → tripwire; tests-only → tripwire + rows targeting the
  changed files; src changed → tripwire + rows whose SAB_FILE or target
  changed, full matrix at module close. MEASUREMENT FIRST: diff the
  2026-08-18..22 mech matrices in build/ (different HEADs, known diffs)
  for any row that flipped without its SAB_FILE/target changing. Frank
  (08:5x): "wait for the census memo and decide as a set". STAGE 2 RULED
  by Frank (11:1x, 2026-08-23): "spend the effort where it has the
  greatest impact; if test is 10 minutes, spend the least time there —
  insofar as it's not called as part of the other tests. Approve 1-3 as
  per your recommendations. #4 I am ok with this risk. 6 and 7 probably
  not worth it. 5 as a follow-on if needed." → #1 [TT-6] timeout swap
  (STARTED); #2 [TT-7] one combined ASan+UBSan axis, measurement first
  (STARTED); #3 [TT-8] mech PROCS re-validation + the PROCS leak into
  inner sharding (STARTED); #4 the tiered mech re-run policy ADOPTED as
  D69 (risk accepted by Frank; the retro-diff of the m64/m65 matrices
  rides [TT-8] as evidence, not as a gate); #5 CCACHE=1 for mech — follow-
  on if the [TT-8] numbers leave mech long; #6/#7 gcc/exec batching —
  closed with [TT-4]. BOX RULE for the three lanes: every timed run is
  box-exclusive and serializes through the manager — [TT-6]'s
  before/after first, then the battery on the merged swap (= the axes'
  "after"), then [TT-7]'s combined-axis run, then [TT-8]'s matrices.
  Frank gets the whole-chain before/after at the end.

- [TT-7] STATE:completed (ADOPTED 2026-08-23 14:2x: `make san` MEASURED 45:50 vs ubsan 26:58 + asan 36:45 = 63:43 on the same tree — −17:54 per chain, identical 1569 PASS lines, zero reports; the battery's sanitizer stage is now `san`, ubsan/asan opt-in singles; docs/testing.md "[TT-7] combined axis — ADOPTED") — formerly STATE:started (2026-08-23, Frank's #2; PREP MERGED 9582091: `make san` target, build-san/, distinctness verified through the real generated-matcher path, D45 budgets byte-identical to either single axis, docs PENDING; LSan is a no-op on this box under ANY axis — K26, ptrace_scope=1; OWED: the manager's timing run `gnutimeout 5400 /usr/bin/time -v make -j12 san` vs the battery_tt6 ubsan+asan walls, then the adoption flip) — ONE
  COMBINED `-fsanitize=address,undefined` AXIS, measurement first: a
  `make san` target building a third separate tree (build-san/) with the
  combined flags on BOTH axes exactly as ubsan/asan do; measure its wall
  against ubsan+asan run back-to-back on the same HEAD (after [TT-6]
  lands, so the axes are measured without the sleep); verify the
  DIAGNOSES stay distinct (the sanitizer findings inventory in
  docs/testing.md lists the historical reports — replant one of each
  kind, or a known UB and a known leak, and show the combined build
  reports both with their own tool names); if the combined axis is
  faster AND as diagnostic, the battery adopts it and ubsan/asan stay as
  opt-in singles. SAN-1's separate-axes reason is TSan-specific
  (Makefile:577-580) — not a blocker.

- [CHK-1] STATE:completed (CLOSED 2026-08-25 18:2x — THE BATTERY IS GREEN on 1879bc2 (matrix tree 44c77fc, docs-only apart): `make test` 26,843 cases with the K32 corpus cell's 29 re-run solo 1,634/0, 1,539 checks / 0, 1 INCONCLUSIVE under -j12 (the load guard doing its job); solo resource 19/0, counterk 24/0; `make san` clean both axes, 33 scripts (1h41m — five previously-dropped diff scripts now run); full matrix 180 rows / unexpected 0 / undetected 6 (S150-S153, S160, S178, all expected) / UNREACHED 0 / anomalies 0 — the FIRST matrix measuring reach on every row, 42 reach lines. Three battery-found defects fixed on the way (c448437, 1879bc2): the sweep's pcrec_run-behind-an-exec-wrapper and unsourced-use shapes, and the 20 s wall on a hostile compile under load. Started 2026-08-25 12:3x; PROGRESS ~14:3x: [MECH-REACH] MERGED 3eb4cc8 (row stays started until the full 180-row matrix measures `unreached` across every row — owed at this batch's battery); K37 FIXED + [TT-9] MERGED ea4504b; CROSS-LANE CATCH at the merge: the K37 structural check went RED on main with 22 sites the srReach merge introduced — 21 `SAB_REACH` probe strings and one help line — because the mech script's witness-probe executor ran `bash -c "$SAB_REACH"` unbounded; fixed the general way (one `$TIMEOUT_BIN` bound at the executor, `SAB_REACH_TIMEOUT` override, two reasoned allowlist entries), verified [K37] PASS 459 sites/77 scripts + S27 solo DETECTED through the bounded executor; [TT-10]/[TT-11]/(d) delivered by srLoad, under review) — THE CHECK-INFRASTRUCTURE BATCH (Frank,
  2026-08-25, fortieth session, ruling 5 of the [DD-14] going-forward
  conversation): [MECH-REACH], K37, [TT-10], [TT-9], [TT-11] — five
  one-way improvements to checks, no `src/` change, disjoint files —
  run as up to three sonnet lanes BEFORE the bench loop starts (every
  battery until then pays K37's hang risk and [TT-10]'s solo re-runs).
  Order by what each protects: [MECH-REACH] (the matrix's meaning), K37
  (the battery hanging on a real bug), then [TT-10]/[TT-9]/[TT-11].
  BRIEF NOTES from the ruling: (a) K37's `pcrec_run` helper routes the
  compiler through `scripts/watchdog` (wall + tree-RSS + CPU + log line),
  not bare coreutils timeout — the same mechanism `gen_run` already uses
  for the other half of the harness's calls; a compiler that
  runaway-allocates instead of looping slips past a plain timeout. (b)
  [TT-10]'s "measure the child's CPU, not wall" is what watchdog's `-c`
  (cpukill, exit 123) already does — try wiring before building. (c)
  every brief: `gnutimeout`, never `timeout` (uutils; docs/testing.md
  "The `timeout` binary itself"); `scripts/safekill PID` to kill.
  (d) CCACHE=1 for mech (Frank, [TT-5]'s #5, 2026-08-25: "test ccache in
  situ because last time we tried it it made the tests take longer") —
  [TT-3] measured NO for `make test` (slower) and a QUALIFIED yes for
  mech; the wiring is already opt-in. Adopt as mech's default ONLY on a
  before/after WIN measured on a full matrix on the same tree,
  box-exclusive (mech rebuilds pcrec per row — that is the cache's
  case); a loss or a wash stays opt-in and the number is recorded.
  MEASURED 2026-08-25 (srLoad, 12 rows, 4-way pool, HEAD 3e771a3, CCACHE_DIR persisted outside the archive tree — the Makefile default resolves INSIDE each row's ephemeral tree and would never hit): 10 measurable rows 348.2 s → 306.8 s (−11.9%), NON-UNIFORM — build-dominated rows −21..−52% (S01 −52%, S11 −34%), suite-execution-dominated rows −3..−4% (S46, S56), the two hang rows S159/S90 unhelped in either condition; ccache 66% hit rate; the ccache pass ran on a QUIETER box (confound disclosed). NOT ADOPTED as default — stays opt-in; revisit only if a full-matrix wall number is ever needed and the build-dominated share justifies it.

- [K38-FIX] STATE:completed (lane srK38, sonnet, 2026-08-26, commit 06c08c9) — the VM emitter's fixed-size name buffers truncate at long prefixes (known_issues K38, FIXED) — was: started (STARTED 2026-08-26 ~12:0x): a 60-char prefix — the documented maximum — yields uncompilable C. General fix: one `PCREC_MAX_PREFIX_LEN`-derived buffer size for every emitted name; a tests/cli witness that emits and COMPILES a max-length-prefix artifact on both engines. Sonnet; the identity gates must stay byte-identical for `rx` (the buffers only grow). CLOSED: reproduced with a real 60-char prefix through gcc rather than trusting the original buffer list (nm[48]/entrypos[32] turned out clean; the real family was vm_slot_expr's sl[64], the span-cursor family, the revdet rung's rv/cur/byte[80]/ga/gs/val — ga/gs truncated to the IDENTICAL wrong string, collapsing the group-span write and group-seen flag onto one name); `src/core/limits.h`'s new `PCREC_MAX_EMIT_NAME_LEN` sizes the whole family plus emit_dfa.c's one prefix-carrying buffer; 1,784-pattern x 2-prefix x 2-engine identity sweep (7,136 compiles) 0 diffs against the pre-fix binary; tests/cli case17 verified DETECTING against that same pre-fix binary; make test-codegen + test-cli (287/287) green, make strict clean.

- [TT-12] STATE:completed (CLOSED 2026-09-19, seventy-first session, per docs/dev/plan_audit_2026-09-19.md: delivered, tag stale — Frank\'s ruling on the audit) — formerly STATE:started (CHARTERED AND SCHEDULED 2026-09-02 ~19:3x by Frank, fiftieth session: "Add your plan item and schedule it for the test axes optimization and addition to union tests. Observe its cpu usage (and tests usage in general) for unused cpu/optimization potential.") TEST-AXES WALL-CLOCK + THE BATTERY'S UNUSED CPU. Facts at filing: tests/axes/run_axes.sh walks 21 axes SEQUENTIALLY, each a full corpus run at PROCS=nproc (12), ~175 s each (one at 517 s), 4,205 s total (opt5i's run, 2026-09-02); the box sat at load 4.5-6 on 12 cores during it (9 live harness workers observed) — roughly half idle in each axis's serial phases. test-axes is OPT-IN and outside battery_v4, which is how K45's pre-existing red survived. STEP 0 (MEASUREMENT, running tonight for free): a CPU sampler (scratchpad cpu_sampler.sh: load1 + all-core busy% every 30 s, tagged with the battery's stage markers) rides the union battery on de32a4b — test/strict/san/lint/mech each get a utilisation profile; the analysis (a sonnet lane, tomorrow morning) archives the samples under docs/dev/ and names each stage's idle fraction and its cause (serial phases, PROCS caps, single-threaded oracles, the mech matrix's PROCS=4). STEP 1: run_axes.sh runs axes PAIRWISE (two concurrent axes at PROCS=nproc/2, or whatever STEP 0's profile says fills the box) — answer-identical by construction (the axes are independent corpus runs; the base dump is shared), target ≤ 40 min. STEP 2: test-axes JOINS THE UNION BATTERY (battery_v5 = test → strict → axes → san → lint → mech) once STEP 1's wall fits the day/night rule; K45's tower documented/excluded first so the stage is green on a clean tree. STEP 3 (if STEP 0 shows it): the same pairing idea applied to any other stage whose profile shows idle cores. **RULED 2026-09-03 ~08:1x (Frank: "2 yes"): test-axes JOINS THE UNION BATTERY (STEP 2 chartered) — sequence unchanged: STEP 0 analysis of the archived samples (lane tt12a, sonnet, launched now), STEP 1 pairwise axes, then battery_v5 = test → strict → axes → san → lint → mech; K45's tower documented first so the stage is green on a clean tree.** **STEP 0 MEASURED 2026-09-03 ~08:3x (lane tt12a, docs/dev/tt12_step0_profile.md, from the archived samples): idle core-hours per stage — test 0.62 (81% busy at -j12; the OPPOSITE problem: -j12 outer × PROCS=nproc inner stack to load 47, K44's cause), san 18.49 (110 min at 15.7% busy — only 4 of its 34 scripts read PROCS; the 5 whole-corpus identity scripts are single-process by construction), lint 0.15, mech 14.01 (132 min at 47% — run at PROCS=4 by the manager's battery.sh AGAINST [TT-8]'s measured setting PROCS=6: 28:43 vs 36:36 on the 118-row matrix, byte-identical rows). RANKED: (1) mech at PROCS=6 in the battery (one-line fix; confirm with one run diffed against battery_mech.log); (2) STEP 1's pairwise axes — each axis's ~175 s is bounded by ONE 3,065-case file (tests/assertions/multiline.rxt) under the harness's per-FILE dispatch, not by PROCS, so two axes at PROCS=6 each should be near-additive (≤ 40 min from 70); (3) a small -P (3-4) over san_scripts.txt's serial loop for the single-process identity scripts, after a concurrent-vs-sequential timing rules out shared-resource contention. Stage order for battery_v5 given day/night: keep the wall flat by landing (1)-(3) before adding axes.** **K44 direction (Frank, 2026-09-03 "4 agree"): the test stage's parallelism shape is decided by STEP 1's measured table (fix direction (b) of K44), not by hand; the K44 entry's disposition is updated when battery_v5 lands.** **STEP 1 ITEM 1+2 MEASURED 2026-09-03 09:4x (lane tt12b, 969b9ba, unmerged): the PAIRED 21-axis sweep is 2,868 s vs the sequential 4,205 s (−32%; target ≤ 2,400 not met — the 3,065-case file bounds each axis), ALL axes answer-identical, and with K45's tower documented the sweep reads 'all axes answer-identical (documented refusal populations excepted)' — GREEN on a clean tree for the first time since fa9b6d4. Measured beside ccdiff1's builds (load 12-16), so the quiet-box number may be lower.** **STEP 1 MEASURED AND MERGED 2026-09-03 11:1x (lane tt12b, 648970e; docs/dev/lanes/tt12b_report.md): (1) pairwise axes 2,868 s vs 4,205 sequential (1.47×), answer-identical on all 21 axes, measured under load 12-18 (a quiet-box re-run owed before the ≤40-min target is called unreachable); (2) K45 CLOSED — the tower's refusals documented, refused_undoc 2→0 on all five axes, the sweep GREEN on a clean tree; (3) san's 34 scripts run through tests/lib/run_san_group.sh's bounded pool (SAN_PROCS=4) — the D77 probe on the five identity scripts: 831 → 351 s (2.37×), zero contention, verdicts identical; the full 34-script san under the pool is unmeasured until the next battery; (4) THE K44 SHAPE TABLE (full `make test`, one shape at a time): -j12/PROCS=1 1,674 s rc=2; **-j4/PROCS=3 1,115 s rc=0 (both K44 cells GREEN)**; -j2/PROCS=6 1,792 s rc=0 — the winner is -j4/PROCS=3 (Frank's '4 agree': the measured shape decides; K44's disposition updated by the lane); shapes (a)/(b) saw ~6 min of a bench `make check`, the relative order holds; (5) scripts/battery.sh WRITTEN (battery_v5: test at -j4/PROCS=3 → strict → axes paired → san pooled → lint → mech PROCS=6; timestamped stage markers; detached with a PID file) — NOT yet run end to end; its first run is the next merge's battery ([CC-DIFF] STEP 1, abi 17). STEP 2 (test-axes in the battery) is thereby BUILT pending that first run.** **STEP 2 BATTERY-PROVEN 2026-09-04 13:28 (battery_v5's FIRST end-to-end run, on main 93381afb→0ef083e2 = code 8d68ddc2 + docs, abi 20; build/battery_20260904_092529): test 20 min rc=0 (-j4/PROCS=3) → strict 11 s → axes 50 min rc=0 (paired PROCS=12, 21 axes answer-identical, 0 mismatches) → san 55 min rc=0 (34 scripts -P4; battery_v4 was 110) → lint 77 s → mech 115 min rc=0 (PROCS=6; 222 rows, unexpected 0 / undetected 8 all expected / unreached 0 / anomalies 0); 4 h 03 min wall vs battery_v4's 4 h 20 min WITHOUT an axes stage — STEP 1's ~75 min saving bought the axes stage (+50) and mech's growth (118 rows/28 min on 08-23 → 222 rows/115 min: rows × corpus, both growing). OBSERVATION (Frank, 2026-09-04 13:3x: "as soon as we speed up testing battery we add something to it that brings it back to where it was"): the growth law is the population, not the constant — the manager's proposed answer (UNRULED): tier mech by cadence using [TT-8]'s tests/mech/rows_for.sh (per-merge battery runs the rows the merge touches; the full matrix on a schedule or when a check/site changes), then overlap san+mech (STEP 3, one measured run first), then an allowlist rule for what a lane may add to the per-merge set. OWED on the row: the quiet-box paired-axes re-run; STEP 3.** **UNION CHAIN 2026-09-04 16:58-18:17 on c7288a59 (build/chain_20260904_1700/; edge2 abi 21 + ccd2 abi 22 + form0): test 44 sections green / 2 red, codegen 1 red, registry 1 red — all three reds test INFRASTRUCTURE (the limits manifest lacked ccd2's VM_INLINE_CHAIN_MAX_BYTES row; one sort under the ambient locale in the newly-wired capability probe, K35; one unbounded compiler call in the entry-shape gate, K37), fixed 8fc1580c and re-proven solo (registry 55-row manifest green; codegen 6/6; the entry-shape gate 14×5; the recursion identity gate at FILEPIN 2706ba6c: (B) whole-file identity on 2,294 patterns per axis); axes rc=0, all 24 axes (21 + forward/inline rungs + oracle) answer-identical, 22,455/22,455 keys, 0 mismatches. Size log regenerated on the quiet box and committed alone as 334fd10e (every VM artifact +68.5 B mean from the two stamps + the entry chain; 15 DFA artifacts moved on the edge dispatch; 1,244 DFA rows byte-identical). DONE + the box to the bench at 334fd10e (I-44, durable only — no bench session was listed).**

- [TT-11] STATE:completed (MERGED 2026-08-25 ~14:5x, lane srLoad: run_recursion_identity.sh:311-343 reads `.abi = N` from an artifact of each compiler and refuses on mismatch with D76's message — demonstrated on ac4917d ('.abi = 2' vs 3); default pin 8fc1e51 15/0, (A)/(B) on all four axes at their pinned numbers; subroutines_design.md now says the dead-capture rule is a general src/opt change (D75 addendum)) — formerly STATE:not-started — THE IDENTITY GATE'S WHOLE-FILE PIN FOLLOWS THE
  `abi` NUMBER (Frank, 2026-08-25, fortieth session; D76). Today
  `tests/codegen/run_recursion_identity.sh` comparison (B) pins `8fc1e51`
  and guards the pin with an ad-hoc probe (`RESUME_FRAME_SIZE` present in
  the pin's emit_dfa.c — one wave's boundary, encoded by hand). Make it
  STRUCTURAL: the pin's emitted `rx_info.abi` must equal the compiler's
  (build the pin's compiler as the script already does; emit one
  artifact; read the stamp), refusing with a message that says "the
  scaffolding changed — bump `abi` and re-pin in the same change" when
  they differ. Comparison (A) (program region vs the pre-module
  `ac4917d`) is untouched — it is the module's promise, not the abi's.
  Same change: `docs/testing.md` + `tests/codegen/CLAUDE.md` state the
  two owners (D76), and the gate's comment + `docs/design/
  subroutines_design.md` describe the dead-capture rule as a GENERAL
  engine-selection change that landed with wave G (D75 addendum), not a
  recursion feature. Validation: the refusal must FIRE on a deliberately
  wrong pin (a pre-FB commit) and PASS on `8fc1e51`; the gate's 15/0
  unchanged. Sonnet-sized; no src change.

- [TT-10] STATE:completed (MERGED 2026-08-25 ~14:5x, lane srLoad: tests/lib/load_guard.sh — 1-min-load/nproc > 2.0 (between the 1.0 every budget already prices in and the K31 addendum's measured 2.58 failure point) turns a watchdog 123/124 on a CPU-capped cell into INCONCLUSIVE, a third counter, never PASS never FAIL; tests/resource's K7 cells and a NEW load-guarded K32 compile-cost pin in counterk (20 s CPU ≈ 5× the 4.0 s quiet cost); solo 19/0 and 24/0; forced breach at ratio 2.47 → INCONCLUSIVE, at 1.18 → FAIL (counterk directly; resource's heavy-load direction by the shared mechanism). RESIDUE 2 (found by the c448437 battery, 2026-08-25 14:4x): the four identity sweeps (endvar/wordctx/mlinectx/gstart, and codegen's M4.5b §5.4) score a compile that TIMED OUT (exit 124 under load) as "N patterns changed emitted bytes" — a failed compile is not a byte change; those scripts must distinguish exit 124 (→ INCONCLUSIVE via load_guard, or a named compile failure) from a diff. Mitigated for now by pcrec_run's 3× wall (1879bc2); the general fix is the next battery-touching lane's. RESIDUE, not built: a suite with inconclusive cells still EXITS 0 — the battery procedure must grep `checks inconclusive: [1-9]` after every run until a runner-level aggregate counter exists (next battery-touching lane; the general form)) — formerly STATE:not-started — tests/resource's 45 s COMPILE-CPU CAP CHECK IS LOAD-SENSITIVE BY CONSTRUCTION (2026-08-24: SIX identical failures across the day's merged-tree batteries on `[a-z]{0,30000}` / `(a|b){0,30000}`, every one green solo, every one under a concurrent lane build — the K31 addendum's shape). The check asserts the cap FIRES within 45 s of CPU, but CPU-time inflation under SMT contention (measured >2× in docs/testing.md) pushes a quiet-box ~25 s compile over 45. Charter: make the check measure what it means — either (a) a RATIO against a calibration compile taken in the same run (the cap fires within k× the calibrated cost), or (b) a load guard that reports INCONCLUSIVE (never PASS, never FAIL) when the 1-minute load average exceeds a threshold, with the D45 budgets themselves untouched. Same class as the k18 san budget: a CPU-bounded assertion is only exact on a quiet box, and a check that lies under load costs a solo re-run per battery. Sonnet lane, small; lands with the next battery-touching wave or at the [DD-14] close. **WIDENED 2026-08-25 ~04:37 (journal part 34):** a SINGLE `make -j12 -Otarget test` alone on a quiet box, twice (srFBc's runs 1 and 2), tripped the same two cells — the K32 compile-timeout cell `((a)|ab){4000}c` (exit 124 + 28 dependents) and tests/resource's 45 s CPU cap (`[a-z]{0,30000}`, `(a|b){0,30000}`) — both green solo every time (1634/0 ×3, 19/0 ×2). So the load sensitivity is to the suite's OWN parallelism, not only to three concurrent suites: the fix must make these cells load-aware (a CPU-time cap measured on the child, not wall; or a serialized section for the two cells; or a load-scaled budget with the reading printed), and the battery procedure meanwhile runs `test-resource` and counterk solo after every full run.

- [MECH-REACH] STATE:completed (CLOSED 2026-08-25 18:2x: the full 180-row matrix on 44c77fc scored `unreached: 0` with every retrofitted row's reach line green — the mechanism is measured across the whole population, not only the 22-row solo sweep) — formerly STATE:started — SABOTAGE WITNESSES MUST PROVE THEIR REACH (2026-08-25, from S70 on the merged [DD-14] tree, journal thirty-ninth session part 40 addendum): row S70 (the escape doorway's enabled-but-unbuilt epilogue, src/parse/ext.c:326) certified NOTHING from [M6.5.2] — when its last live witness `\k` gained a producer — until the full matrix on 17469b6 scored it UNDETECTED; its four named escape witnesses had all been implemented by later waves, and the matrix's "NOW DETECTED / expired claim" doctrine watches only the opposite direction. THE GENERAL MECHANISM (not a per-row fix): `tests/mech/run_sabotage_matrix.sh` gains an optional per-row `SAB_REACH` — a command run on the CLEAN tree whose output must contain a stated string (typically the exact diagnostic the witness produces at the sabotaged site) — asserted BEFORE the sabotage is applied; a row whose witness no longer reaches its site is then RED in the wave that implemented the construct, not two milestones later. Retrofit: every row whose SAB_DESC names a witness construct (the `reject_gated` family first, then any row whose detector is a diagnostic string). Ties to K35 (checks whose population silently shrank) and [TT-10] (checks that lie under load): three shapes of a check that goes green for the wrong reason. SECOND INSTANCE, same run: S155's SAB_HARNESS_TARGET (leftrec.rxt) had held ZERO give-up cells since [DD-14.EMPTY] — a witness FILE whose relevant population went to zero; and its sabotage changes a WRITE not an ANSWER (three byte-identical guards from one emitter function; the survivors answer identically one frame later), visible only to run_frame_buffer.sh §2's exact-fit ASan driver — so `SAB_REACH` must also be able to assert a population ('the target file has ≥N `gu` cells') and a row may declare an instrument requirement (`REQUIRE_ASAN`) whose absence is an ANOMALY, not UNDETECTED (ruled 2026-08-25 ~06:5x). Owner: the next mech-touching lane; the [DD-14] close lane RECORDS the row and re-runs S70/S155 solo, it does not build this. **BUILT BY LANE srReach, 2026-08-25 (fortieth session), branch `lane/srReach`.** `SAB_REACH` + `SAB_REACH_EXPECT` (one required literal per LINE, so a row's several witnesses at one site cannot expire one at a time), `SAB_REACH_POP` (`FILE|EREGEX|MIN`, count PRINTED every run), `SAB_REQUIRE` (closed vocabulary, `asan`) and the new verdict `UNREACHED` — counted in the trailer beside undetected/anomalies, RED unless the row declares `SAB_EXPECT=UNREACHED` with a mandatory `SAB_EXPECT_REASON`, scored in BOTH directions (`NOW REACHED`), and the sabotaged tree is not built when a row is UNREACHED. A CLEAN reference tree is `git archive HEAD`'d and built ONCE per run, lazily. 21 rows retrofitted (S15-S20, S27-S35, S70, S110, S111, S119, S155, S172), every witness verified live against the clean binary; NONE was found already unreached (S70's own expiry had been repaired by the close lane — this makes the repair CHECKED). VALIDATED three ways with plants made and removed: an expired `SAB_REACH_EXPECT` -> UNREACHED/exit 1; a population floor above the count -> UNREACHED printing `=29(want>=999)`; `SAB_REQUIRE=asan` under a cc wrapper refusing `-fsanitize=` -> ANOMALY. That third plant found a defect in the mechanism's own prose (the ANOMALY sentence contained the token `UNDETECTED`, which the headline's `grep -c UNDETECTED` counted — a control sharing a source with its own subject); reworded, re-measured `undetected: 0`. Also added `VALIDATE_ONLY=1` (180 definitions checked in seconds, four malformed-field plants each a named FATAL + exit 2, and deliberately NOT the pollable `mech run COMPLETE` trailer). Solo canonical runs: S70 `reach:ok(2/2), reject:2fail/587pass, asrt:0fail/52pass` DETECTED; S155 `require:asan-ok, pop:framebuffer.rxt:/^gu frames /=4(want>=4), reach:ok(1/1), corpus:0fail/16pass, recdiff:0fail/10pass, framebuf:1fail/5pass` DETECTED. `make strict` clean; tripwire 180 sabotages / 191 anchor sites all resolve. **REMAINING BEFORE STATE:completed — the manager's FULL-MATRIX composite at merge (D69's CLOSE tier), which is the first run in which `unreached:` is measured across all 180 rows.**

- [TT-9] STATE:completed (MERGED ea4504b, 2026-08-25 ~14:3x, lane srRun/srRun2: tests/lib/san_scripts.txt is the ONE list `ubsan`/`asan`/`san` read (Makefile SAN_SCRIPTS); FIVE diff scripts were in none of the three — lookaround's two AND assertions' gstart/kreset/mline — all added, exclusion list starts empty; structural check in run_codegen_tests.sh validated red→green; `make -n` shows the three targets expand to one identical 33-script set) — formerly STATE:not-started — THE THREE SANITIZER SUITE LISTS ARE HAND-MAINTAINED COPIES (found by [DD-14] wave B+C, 2026-08-24): `make ubsan`/`asan`/`san` each carry their own list of suite scripts and nothing enforces agreement — the lane's first patch added `run_recursion_diff.sh` to ubsan's list only, and the san run silently never executed it (only the `-- san:` stage banner revealed it). Also: `tests/lookaround/`'s diff script is absent from all three lists with no stated reason. Charter: ONE list (a Makefile variable or a manifest file) that the three targets read, plus a check in `tests/codegen`/`make testscripts` that every `tests/*/run_*_diff.sh` is either in the list or named in an exclusion list with a reason (the SKIP-is-not-a-pass shape); add the lookaround diff or record why not. Small; a sonnet lane; lands with the next battery-touching wave.

- [TT-8] STATE:completed (CLOSED 2026-08-23 15:3x: full 118-row matrices on 6b0ef30 — PROCS=4 36:36, PROCS=6 28:43, both undetected 0 / anomalies 0, rows byte-identical bar S18's reject figure which is shards+1 → K30 (run_reject_tests.sh's --list-syntax guard runs in every shard); PROCS=6 is the documented matrix setting; yesterday's 60:08 → 28:43 (−31 min) from the timeout swap + the leak fix; the lane's 20-row sample one-liner was INVALID — the script takes one id prefix — so the sweep was done as two full matrices; the first full pass through the two-site applier was the no-op expected) — formerly STATE:started (2026-08-23, Frank's #3 + #4; (a)(b)(c) MERGED bbf7847: the leak was LIVE — PROCS=4 on a single row spawned 4 REJECT_SHARD_TOTAL=4 workers; fixed with INNER_PROCS=ncpu/PROCS passed explicitly on the reject/harness arms, S15/S107 figures byte-identical across leaked/serial/fixed; D69 evidence: 99 common rows m64↔m65, ZERO flipped DETECTED→UNDETECTED without their own definition changing; tests/mech/rows_for.sh maps changed paths→rows, failing-direction tested; OWED: the PROCS sweep (~20 rows at 3/4/6) and the full after-matrix — docs/dev/tt8_mech.md has the one-liners) —
  MECH: (a) the PROCS LEAK: run_sabotage_matrix.sh's PROCS (row
  concurrency) reaches the inner tests/harness/run.sh and reject sharding
  through the environment — fix so inner scripts get an explicit per-row
  PROCS budget (JOBS already divides; do the same for the inner shard
  width) and measure the matrix at PROCS=4 before/after, then re-validate
  PROCS at 118 rows (sample of ~20 rows at PROCS=3/4/6, then ONE full
  matrix at the chosen setting = the chain's mech "after" figure); (b)
  D69's evidence: diff the m64 (99 rows) and m65 (118 rows) matrices and
  any earlier matrix in the journal for a row that flipped verdict
  without its SAB_FILE/target changing; (c) document D69's tiered policy
  in docs/testing.md's mech section and tests/mech/CLAUDE.md.

- [SPEC-1.1] STATE:completed (MERGED fab1b62 + landing items 3dff2a6, 2026-08-25 ~13:1x: docs/spec/limits.md 261 lines, every number cited and re-measured — 684 B matches / 686 B gives up; rx_search frame 131,216 B; the K33 figure drift 131,296→131,216 corrected in known_issues + a D73 correction note; --step-budget/--work-budget help and the two pcrec.h sentinel comments name the D49/D51 defaults; the K34 annotation ruled via the annotation store; strict / test-cli 283/0 / test-registry pc4 62,872 cells 0 / test-stackdepth green solo on main) — formerly STATE:started (lane srLimits, 2026-08-25 ~13:0x) — `docs/spec/limits.md`: the give-up/limit contract consolidated — D22's frame, the four codes (pointer to match_api §4), the numbers (step 500,000,000 D51; work ~10⁹ D49; frames/trail 2048/3072 D73 with the 684-byte `^(a(?1)?b)$` example RE-MEASURED; compile budgets D45), K33 + the `_in` remedy (pointer to §10), K34/D74 the documented divergence; plus the two stale fixes: `cli/main.c:58` wording and the K34 compliance annotation through the annotation store + refresh procedure. THE direct discharge of D73/D80.

- [SPEC-1.2] STATE:completed (MERGED 2026-08-25 ~14:5x, lane srCli: docs/spec/cli.md 386 lines; every flag verified on a live run + cli/main.c line; module table 8 built / 9 unbuilt measured from --list-syntax; exit codes 0/1/3 each with its producing command, 3 being --explain dissent only, currently unreproducible by design (case11 asserts zero); strict + test-cli 283/0) — formerly STATE:not-started — `docs/spec/cli.md`: the full flag reference (survey A1-A14; stubs into tuning/registry/diagnostics). P1; parallel with 1.1.

- [SPEC-1.3] STATE:completed (MERGED 2026-08-25 ~19:0x, lane srTuning: docs/spec/tuning.md 468 lines — every axis's stamp verified by an artifact diff, the masked/unmasked split confirmed against emit_dfa.c's strategy_denials, five differentials re-run with 0 diverged, prefilter named as the one axis without its own differential; FOUND: lib/pcrec.h named a stamp `<PREFIX>_VM_CALLS` that never shipped — fixed by the manager at merge to the two real counts) — formerly STATE:not-started — `docs/spec/tuning.md`: the `-f`/`-fno-` family, `--unroll=`, `--engine=` caller-side; byte-identity vs engine-selecting per flag (survey A7/F5). P1; parallel.

- [SPEC-1.4] STATE:completed (lane srK38, sonnet, 2026-08-26, commit 8d18b93) — match_api.md patches (survey: D3 pointer, C2, C4 D76 abi paragraph, F6 byte-only encoding lead, F9 whole-subject subsection) with a dated revision-log entry — was: started (STARTED 2026-08-26 ~12:0x, after K38-FIX). CLOSED: §4 gains a docs/spec/limits.md pointer for the give-up codes' numeric defaults (D3); §6.3's DFA-stamp-gap caveat re-verified against a fresh DFA/hybrid build — already discharged by [DD-13c], nothing changed in prose (C2, "verified, nothing to change" per the survey's own allowance); §6 gains a caller-facing abi paragraph restating D76 in contract terms, rx_info.abi confirmed 6 (C4); §8.2 now leads with "byte is the only encoding implemented today" (F6); new §3.6 states the (?:P)\z whole-subject idiom, the a|ab counter-example, D77/[OS-4]'s ruled-permanent status, and the idiom's own DFA stamps, every claim verified live against a fresh build rather than asserted (F9). docs/spec/CLAUDE.md's match_api.md entry updated to match; make test-cli (287/287) green after (doc-only change, no code touched).

- [SPEC-1.5] STATE:completed (MERGED cf551d4, 2026-08-25 ~19:4x, lane srReg: docs/spec/registry.md 228 lines — every column of the three TSV surfaces by header name with its value set measured live (128/50/90 rows), the append-only/resolve-by-name promise, built vs status/roadmap, the family rule, what registry_check vs PC-3 pin; drift: tests/registry/CLAUDE.md's '100 rows' → 128, fixed at merge) — formerly STATE:not-started — `docs/spec/registry.md`: the `--list-*` TSV column contract (A8). P2.

- [SPEC-1.6] STATE:completed (MERGED 962e2de, 2026-08-25 ~19:1x, lane srRxt: docs/spec/rxt_format.md 379 lines, the format/driver protocol/how-to-add moved out of testing.md with a line-range table; four prose-vs-parser drifts fixed — `perr` requires exit EXACTLY 1, the driver's exit-4 anchored-entry cross-check was undocumented anywhere, RXTFLAGS had no env row, the 'harness hardening' timeouts were pre-D45; anchors updated tree-wide incl. the manager skill; test-corpus 26,560/0 at PROCS=4) — formerly STATE:not-started — `docs/spec/rxt_format.md`: extraction of the .rxt format/driver protocol from docs/testing.md ~124-435 (F3); testing.md keeps the DEVDOC rest. P2, mechanical.

- [SPEC-1.7] STATE:completed (folded into cli.md §3 by srCli, 2026-08-25) — `diagnostics.md` or a cli.md section: D26 tiers caller-side, the offset-pinning convention (A13). Small.

- [SPEC-1.8] STATE:completed (folded into cli.md §1 `--features` table + §4 by srCli, 2026-08-25) — `modules.md` or cli.md's `--features` section: the 17-name map with status, pointing into pcre2_compliance.md (A10/E). Small.

- [REG-SV] STATE:completed (MERGED b819512 fast-forward 2026-08-30 06:2x, forty-sixth session: the owed verification FOUND A DEFECT — the new emitter-source leg's optional 5th arg `local src_label="$5"` died under `set -u` on every pre-existing 4-arg call (axes_registry_check.sh:500 "unbound variable"), 61 checks instead of the predicted 79; fixed as `"${5-}"` b819512; re-run PROCS=4 test-registry rc 0 — axes_registry_check 79/0 (the prediction held once the crash was gone), 225/201/54 in the other sections; test-codegen 198/0; make strict clean; registry 61 rows / 21 axes) — formerly STATE:started (BUILT on lane/admin1 33588a4 — one row per producible value, the `-fno-size-term` mis-attribution fixed, an emitter-source leg in the registry check; VERIFICATION + MERGE OWED next session: make -j4, PROCS=4 make test-registry (guard 79 PREDICTED), test-codegen; ADMIN column, D86; lane admin1, sonnet, chartered 2026-08-30 ~01:45 from the bench's O-8 6(b)) — `--list-axes` carries an EMPTY `stamp_value` on the `size-term` rows although `RX_UNROLL_K_WHY` is name-valued (seven values), and the `table` axis omits the outcome values `none`/`mixed` that attempt/empty artifacts stamp — so the registry check cannot cover those value sets and the bench's adapter cannot bucket them from the archived `list_axes.tsv`. The fix is the GENERAL form (one derivation, two readers — the emitter's value set IS the registry's population, as `engine-route` already does one row per value), never a hand-typed list beside the emitter; registry.md §6 hunk + the count re-pins in the same change (D80).

- [SPEC-1.10] STATE:completed (MERGED b819512 with [REG-SV], 2026-08-30 06:2x; verification as [REG-SV]'s row) — formerly STATE:started (DONE on lane/admin1 e7fb479 + 7987656 — F4 ruled process not spec; K2 FIXED with evidence; the "until module M lands" sweep clean; merges with [REG-SV]; lane admin1, sonnet, 2026-08-30 ~01:45) — survey debt: the sabotage-row format (F4, tests/mech/CLAUDE.md); K2's status (known_issues K2 says "fix with module backrefs" — backrefs shipped 08-22, no FIXED marker); table_contract.md's `--emit-ir` note vs [DD-8] — RESOLVED by srCli: [DD-8] still not-started, the note is CURRENT; README/APPROACH as the stranger's real first read (→ [GUIDE-1]/[REL-META]).

- [LIM-1] STATE:completed (BATTERY-PROVEN 2026-08-31 04:05:36, battery 6 on 99d4cbd — san ~110 min / 0 reports, mech 205 rows clean incl. S208/S209 DETECTED, test 1,963/0; the pin is the part-13 journal commit; LANDED BY TAKEOVER 2026-08-31 00:2x — lane lim1's 4 commits + the manager-committed final wave 71b8c59; 44-row limits.def, --list-limits live, limits_check 21/21, the size-cap rescue's RX_ENGINE_SEL value, S208/S209 DETECTED; BATTERY 6 pending — battery-proven flips this to completed and moves the pin; RULED 2026-08-30 by Frank, forty-sixth session — D90; ADMIN column, D86; chartered AFTER [DD-13b.W1.1]'s battery, sonnet) — THE LIMITS TABLE: `src/core/limits.def` (X-macro: name, value, unit, kind = compile budget | runtime capacity | size cap | selection knee, override = flag | -D | none, spec anchor, one-line what-it-bounds) as the SINGLE derivation of every numeric limit (measured 2026-08-30: 16 numbers in 8 files under 4 naming schemes; limits.md §3 hand-copied); limits.h and every runtime default derive from it; `pcrec --list-limits` dumps it as TSV per table_contract.md beside --list-axes/--list-definitions/--list-syntax; the registry check pins docs/spec/limits.md §3 against the dump; a sabotage row catches a bare numeric `#define` outside the table; D80 spec hunk. FOLDED IN (Frank): the size-cap RESCUE stamps `_ENGINE_SEL "selected"` (bench O-10 preview) — give it a distinct `_ENGINE_SEL` value so a fallback bucket sees it; spec hunk, no abi bump (a value, D76). Acceptance: every one of the 16 numbers has a row and no other definition; --list-limits row count pinned; limits.md §3 derived; registry green; `--list-axes` unchanged; battery.

- [PLAN-AUDIT] STATE:completed (DELIVERED + MERGED 2026-09-19 ~15:0x, lane planaudit; RULED by Frank 2026-09-19 ~16:2x: "focus on finishing the refactoring before chartering these partial items" — [REVW.5] + [REVW.A1] first; side-car only where it cannot collide (OPT-EDGE is measurement-only and may; LIM-2 touches src/opt and waits); then SMALLEST TO LARGEST: LIM-2 (S) → OPT-EDGE (S) → ENG-ISL (M) → DD-13b.W1.3 + DD-13 (M, behind [PFX-1]) → CLS-TREE (L; status DOUBLE-CHECKED by the manager: study + ns/char arm + the +2 placement direction all in; design note, panel, kit not started). The 7 complete-in-place rows CLOSED in this commit; the 9 parked rows stay parked; [BENCH-1] settles at [BENCH-REVIEW].) — every STATE:started row dispositioned with Frank (complete-in-place / finish / fold / park); the FINISH rows run to completion, sized, before [REL-1]. Runs after abi 27 lands.

- [REL-1] STATE:completed (**THE 0.1.0-beta IS TAGGED 2026-09-22**: REL-1.1..1.11 all completed — README, compliance page, guide, version, contribution posture, CI green, stranger's build both boxes, the gcc-shaped CLI, the library features lever; D113 step 2 done → step 3 [OPTLOOP] cycle 1 = [BENCH-REVIEW] + [BACKLOG-TRIAGE] on the capability subbench, D119) **PRE-FLIGHT DELIVERED + MERGED 2026-09-21 (lane rel1pre, docs/dev/lanes/rel1pre_facts.md, fdebdc4d): the milestone EXPANDS into the substeps below, sized from its §9; starts on Frank's word after [OPT-EDGE]'s I-81 tables (or earlier, if Frank lifts the sequencing while I-81 waits on the bench slot).** **NEXT (Frank 2026-09-21: "agree on sequencing, proceed"): starts when [OPT-EDGE]'s owed measurements land; a read-only PRE-FLIGHT survey lane `rel1pre` (sonnet) runs now — the row set from [REL-META]'s survey, docs/guide/ state, README staleness, version-constant plumbing, compliance-doc age, stranger's-build checklist — so the milestone expands into substeps from facts.** (CHARTERED by Frank 2026-09-19, D113) — THE 0.1 BETA RELEASE, the "open for business" sign on the already-public repo: [REL-META]'s survey → row set; [GUIDE-1]; README rewrite (status section stale: M3/M4/M5 are done); pcre2_compliance.md refreshed (compliance-refresh) as the public support page; a version constant + git tag `v0.1` + GitHub release; stranger's-build from a fresh clone on darwin + Linux; the contribution posture. Version is 0.1, NOT 1.0 — D81's abi reset does not fire. After [PLAN-AUDIT].
  - [REL-1.1] STATE:completed (RE-LANDED 2026-09-21 seventy-fifth session per D116: lane rel1c 5c3b8aff merged — README 125→65 lines, brief and friendly, digit audit clean (the example's output + the release string only), example verified live `match 2 7`; docs/dev/lanes/rel1c_report.md; first landing: MERGED 2026-09-21 seventy-fifth session, lane rel1a 9bf01318 → main; registry suite solo 225/0 + PC-3 209/0 + DD-11.3 101,244/0; compliance drift ZERO since 2026-09-12; docs/dev/lanes/rel1a_report.md) — README rewrite: the Status section (M4/M5 done, M3 the only open milestone; abi/--tune/--engine/--features/encodings/registry surfaces named), requirements caveats, links to docs/spec/ and the guide, how to run the tests. S. Facts: rel1pre_facts.md §2, §6.
  - [REL-1.2] STATE:completed (MERGED 2026-09-21 seventy-fifth session, lane rel1a 9bf01318 → main; registry suite solo 225/0 + PC-3 209/0 + DD-11.3 101,244/0; compliance drift ZERO since 2026-09-12; docs/dev/lanes/rel1a_report.md) — the compliance page as the public support page: bump the stale freshness header (touched 2026-09-12 and 2026-09-19, header still says 08-22), run compliance-refresh for real, a public-reader front matter. S. Facts: §5.
  - [REL-1.3] STATE:completed (MERGED 2026-09-21 ~23:0x after the 6a54b0ac gate, lane rel13 acd08a1e: docs/guide/ — index + CLAUDE.md + 8 chapters (getting-started, building-with-make, using-the-matcher-from-c, using-the-library, encodings-and-subjects, features-and-modules, tuning-and-limits, troubleshooting) + lang/ placeholder for [LANG-1]; every snippet built and run; the interface edges documented as-built; NULL features = empty default named as the one trap; README pointer + docs/CLAUDE.md row; the lane's finding — limits.md §4's worked-example command still positional — fixed at landing) (LIFTED 2026-09-21 evening, Frank "Proceed" after the interface discussion — the digest is docs/dev/lanes/iface_digest.md; the guide documents the interface AS IT IS with its edges named (return conventions, NUL-terminated pattern vs length-counted subject, three exit-code vocabularies, the inverted -fcomments pair) and the gcc-shaped CLI (D118); STARTS when [REL-1.11] lands so the library chapter documents the lever) — [GUIDE-1] the user guide, docs/guide/: use-case chapters pointing at the spec (D73's recursion-defaults paragraph with the 684-byte worked example — the one REL-META obligation still a GAP at the spec tier). M. Facts: §1, §3.
  - [REL-1.4] STATE:completed (MERGED 2026-09-21 seventy-fifth session, lane rel1b 2de4e318 → main; D115: `PCREC_VERSION` "0.1.0-beta" in lib/pcrec.h, `--version` prints `pcrec 0.1.0-beta`, the essential generated-by line stamps it beside the abi digit — abi 27→28 with the D94 grep re-pin (resource byte pin 762114→762125, codegen ABI_EXPECT, match_api.md §6; the (B) FILEPIN re-pinned to the merge by the manager); CHANGELOG.md seeded; riders: -e help text and limits.md's --source sentence de-staled; lane numbers codegen 9/10 (nm probe), resource/registry/rxtsource 0 failed, anchors 286/286, emit_sweep header-only movers; docs/dev/lanes/rel1b_report.md; DARWIN GATE on the merged main pending) — version plumbing: a version constant + `--version` (what it versions is a RULING — independent of `abi`, which keeps counting per D81/D113), a CHANGELOG seed. S. Facts: §4. Spec hunk in docs/spec/cli.md (D80).
  - [REL-1.5] STATE:completed (MERGED 2026-09-21 evening, lane rel15 4d51768b: CONTRIBUTING.md (77 lines: build/test, the PR checklist, where things are, D26 in two sentences, the internal-process note), README link, RUN-STAMP riding the existing completion trailer (Makefile `test:` sets SHA/dirty/duration env vars; the trailer prints `RUN-STAMP:` only when set — a paste-into-your-PR device, not a provenance control; the first LIVE stamp is owed from the next manager `make test`); PR checklist lives in CONTRIBUTING.md, .github/ left to rel16) (RULED 2026-09-21: no SECURITY.md / CODE_OF_CONDUCT.md — "leave extra docs") — contribution posture: CONTRIBUTING.md + PR template + RUN-STAMP (REL-META item a); the public-CLAUDE.md question (the internal lane/manager process is visible to every visitor — RULING: leave, preface, or move under docs/dev/). M. Facts: §7.
  - [REL-1.6] STATE:completed (GREEN 2026-09-22 ~00:5x: CI run 35684843294 on main 13f71687 — every section green on ubuntu-latest against the pinned pcre2 10.46 (make test step 2026-09-22T03:54:49Z -> 2026-09-22T04:31:25Z; pcre2 build step ran again — the cache had NOT been saved by the failed run 3 (its post-cache step was skipped); run 5, on the badge push, is the first that can hit); README badge added; the fit question answered: ~37-39 min for make test, ~41 min per job) (FIT MEASURED 2026-09-21: run 35675372280 on ubuntu-latest — `make test` real 39m17s, 41/41 sections, job ~41 min: IT FITS. Run 1 was CANCELLED by the manager's own push (concurrency supersede — no push to main while a CI measurement is in flight). Run 2 RED on environment only, lane cifix merged ~23:0x: pcre2 10.46 built from the release tarball + cached (apt ships 10.42; PC-3 60 reds on post-10.42 constructs), a version FLOOR in pcre2_check.c that SKIPs loudly below 10.46, fetch-depth 0 (a shallow clone lost a pinned commit), the C3 RECORD rule re-keyed on the resolved python version (was uname=Darwin), RUN-STAMP's dirty flag captured before the run; residual: the PC-3 probe count was pinned on ubuntubudu's gcc — a different count on the runner's 10.46 is a re-pin. RUN 3 on this push is the green candidate; badge after it) (WORKFLOW MERGED 2026-09-21 evening, lane rel16 31ca3633: .github/workflows/ci.yml — pull_request incl. forks + push:main, one ubuntu-latest job, libpcre2-dev so PC-3 runs, make -j / make strict / `time make test` under timeout-minutes 90 (job 120), logs uploaded on failure, concurrency-cancel; PR template (5 lines → CONTRIBUTING.md); testing.md CI subsection; no clang job (D2); the `test-ci` subset fallback DESIGNED not built (D77). THE FIT MEASUREMENT = the first run on this push; badge after the first green) (RULED 2026-09-21: go; the row's first measurement is whether the test+strict tier FITS an Actions runner — "curious to see if the test run fits in actions") — CI: GitHub Actions on the test+strict per-PR tier only (REL-META item b: the full gate never runs in CI). M. Facts: §7, §8.
  - [REL-1.7] STATE:completed (LINUX ARM DONE 2026-09-21 ~20:5x via executor I-84 at f12e123d: gcc 15.2.0, make + strict clean with no warnings, --version `pcrec 0.1.0-beta`, README example `match 2 7`, examples/makefile builds and its consumer prints the four expected lines, test-cli 284/0, test-examples 3/0, nothing undeclared) (DARWIN ARM DONE 2026-09-21 evening, lane rel15: scratch clone at f12e123d, plain `make` + `make strict` clean under Apple clang, `--version` → pcrec 0.1.0-beta, the README example verbatim, examples/makefile builds and runs (one harmless -Wcomment warning in main.c, noted), smoke tier cli 284/0 + examples 3/0, NO undocumented prerequisite found; the LINUX ARM posted to the executor as I-84 from the report's command block) — stranger's build from a fresh clone on darwin + Linux (the Linux arm via the executor), prerequisites stated where §6 found them unstated. S.
  - [REL-1.8] STATE:completed (TAGGED 2026-09-22 ~01:2x on Frank's word "go ahead and tag": annotated tag `v0.1.0-beta` at the CI-green main + GitHub pre-release via gh, notes from CHANGELOG's 0.1.0-beta section pointing at the guide and the compliance page) — LAST: `v0.1` tag + GitHub release via gh (2.100.0 present; remote = github.com/fdicostanzo/pcrec confirmed public), the release note carrying D73's obligations. S. Depends on 1.1-1.7.
  - [REL-1.9] STATE:completed (FOLDED 2026-09-22, Frank: "tag and meta" — [REL-META] closed into this expansion; its surviving obligations: the abi→1 reset at 1.0 (D81 addendum) stays on the 1.0 row) — [REL-META]'s row: dispose (fold into this expansion — the survey substituted for its "propose the rows" charter; Frank's word). S.
  - [REL-1.10] STATE:completed (GATED 2026-09-21 20:22 darwin at 735f199c: build/strict clean, 41/41 sections, red ONLY the standing nm probe + resource's documented skip; size log 0 movers; PUSHED) **MERGED 2026-09-21 evening (lane clishape f364d122..990f44d6 + clifix 28c7d9d0/7aaf7152, fast-forward to main 7aaf7152): parser (N file operands, --pattern, -I, --source retired, query-mode operands), cli.md/rxt_format.md/README/CHANGELOG/CLAUDE.md hunks, the reconciled migration (518 --pattern insertions/534 sites in .sh, 22 in 12 .py, 7 in .c, 4 Makefile; reference compilers from pinned commits keep the old grammar; emit_sweep probes each binary's dialect), examples/makefile (two sources, three targets, one pooled pcrec call, ar → libmatchers.a, a linked consumer) + tests/examples section (41 sections now); lane full make test 41/41 with the nm probe + a stale W1.2 counter (re-keyed on --target) + a wording regression ("builds nothing" restored) + the pre-merge manifest drift (expected); solo: cli 284/0, rxtsource 0, cpset-structure 28/0, examples 3/0, sweep 0 movers, anchors 286/286. DARWIN GATE on the merged main pending.** (CHARTERED 2026-09-21 seventy-fifth session, D118 — Frank: "proceed with the cli changes ... working with a makefile example as a test case ... rxt -> *.c -> gcc ... a single .a"; STEP A lane clicensus (sonnet, read-only): count every positional-pattern and --source call site outside the pcrec_run wrapper, the wrapper's own shape, the rxtsource suite's --source use, and every spec/README sentence that states the usage line — then STEP B implements: positional = input files, --pattern, -I, --source retired, cli.md hunk, README example, examples/makefile/ + its suite section) — THE gcc-SHAPED CLI, ahead of the guide. M. Facts: iface_digest.md §1(a), §2.
  - [REL-1.11] STATE:completed (GATED 2026-09-21 23:02 darwin at 6a54b0ac: 41/41, the nm probe only, size log 0 movers) (MERGED 2026-09-21 ~21:2x, lane libfeat, 6 commits on f12e123d: `pcrec_options.features` applied PER CALL through a PURE resolver `pcrec_enabled_resolve_spec` stored on the compile's own Ctx (no global write — the D19 race the brief flagged is avoided by construction); NULL = "no request" = today's EMPTY raw library default per D37's addendum (NOT std1 — the plan row's literal text was wrong; the CLI always assigns a concrete value, so bare invocations are unchanged); the old global installer STAYS for the query modes that never compile (--probe-ask/--count-groups/--list-source) — a parallel path, retirement shelved below; tests/core/features_opt_check.c (spec_mod0 was the wrong home — it is black-box); S111's sabotage anchor re-derived (pcrec_ext_gate gained a parameter); core 4/4, definitions 54/0, registry 0 FAIL + PC-3 209/0, sweep 0 movers all streams, codegen 9/10, cli 284/0; tests/thread SKIPs here — the D19 claim's TSan confirmation comes from CI on ubuntu (tests/thread runs there)) (CHARTERED + STARTED 2026-09-21 evening — the manager's recommendation from the interface discussion, taken under Frank's "Proceed"; lane libfeat, sonnet) — [LIB-FEATURES]: the library gets the `--features` lever. Today `pcrec_enabled_set_spec` (src/parse/enabled.c) is reached only from the CLI; a library caller gets `std1` unconditionally (iface_digest.md §1(b), "observed, not ruled"). The row: a `pcrec_options` field carrying the same spec string the CLI accepts (`std1` | comma list | `all` | `none`; NULL = the default resolution, D37), applied per `pcrec_compile` call exactly as the CLI applies it (one mechanism: the CLI sets the field, not a parallel path); the D19 thread-safety guard if the enabled set is process-global; spec hunk in docs/spec/match_api.md or wherever pcrec_options is specified (D80) + lib/CLAUDE.md; a tests/spec_mod0-style check that a library caller's `all` compiles a construct `std1` refuses. S. pcrec_options is the LIBRARY struct, not the artifact — no `abi` event unless the artifact changes.

- [REL-META] STATE:completed (FOLDED into [REL-1]'s expansion 2026-09-22 on Frank's word; the survey rel1pre_facts.md substituted for its charter and every item landed as REL-1.1..1.11; the 1.0 abi reset obligation stays recorded here and on D81's addendum) — (RULED 2026-08-28, Frank: the emitted `abi` number RESETS TO 1 at the 1.0 release — D81 addendum; a release-mechanics item on this row.) USER-DOCS OBLIGATION (Frank, 2026-08-24, D73; RE-HOMED 2026-08-25 by D80 — the numbers and mechanism go in [SPEC-1]'s limits section, the use-case paragraph in [GUIDE-1]; this row's README pass references the guide): the recursion frame/trail default (2048/3072), the subject size it implies for recursive patterns (`^(a(?1)?b)$` gives up at a 684-byte subject), the musl/small-thread-stack caveat (K33) and the caller-provided buffer (`_in` entries) as the remedy must be in the user docs and the release note — not a footnote. META-PLAN ROW for FIRST-RELEASE +
  CONTRIBUTION READINESS (Frank, 2026-08-21, thirty-fifth session:
  "we are within a few solid efforts of having a first release"; this
  row's deliverable is the ROW SET, not the work — [SIMD-META]'s
  pattern). Charter: survey what a first public release and an
  open-to-PRs posture actually require, and propose the concrete rows
  for Frank to ratify. KNOWN CANDIDATES from the chartering
  discussion, to be sized and split by this row: (a) CONTRIBUTING.md +
  PR template + the RUN-STAMP (`make test` emits tree-SHA/dirty-flag/
  counts/duration; the template asks for the paste — catches
  honest-mistake cases: wrong commit, subset, misread red; fraud is
  explicitly a non-goal, provenance-imitation lesson applies) — mostly
  distillation of existing house rules into contributor-sized form
  (oracle-verified expectations WITH the oracle named; module/refusal
  conventions; D26 tiering; CLAUDE.md maintenance travels with
  changes; exact-count checks self-enforce). (b) CI on GitHub Actions
  — FREE for public repos on standard runners (the minutes quota that
  burned Frank's other project is a private-repo constraint);
  fork-PR flow confirmed (fork -> PR, no access granted, first-time
  contributors' workflow runs gated on maintainer approval, no secrets
  exposed — none needed: gcc+make+libpcre2-8-0); TIERING per house
  discipline: per-PR = test+strict; sanitizers/mech = merge or
  nightly; the GATE NEVER runs in CI (shared runners are a loaded box
  — floor-gate-under-load is contamination by our own rule; the gate
  stays maintainer-side quiet-box); self-hosted runners explicitly
  REJECTED for fork PRs (strangers' code on the box). (c) README
  release-adequacy pass + user-facing quickstart. (d) versioning +
  changelog + release mechanics (tag discipline, what "release" means
  for an AOT compiler — source-only vs artifacts). (e) whatever the
  survey finds that this list missed — the survey asks "what does a
  stranger's first hour with this repo hit", which the chartering
  discussion did not walk. Sequencing: the meta-survey is a read-only
  sonnet lane, schedulable any time; the resulting rows land where
  Frank rules

### The 2026-09-17 code-review refactor

- [K60-FIX] STATE:completed (MERGED 2026-09-18 sixty-ninth session, lane k60fix delivered in full: W4 108/158 → 0/158 single-shot and sustained, control at the branch point reproduces 108/158, W1/W3 untouched as expected (legend class), test-codegen identity gates clean, D109 + K60 status + match_api.md §8.1 D80 hunk in the delivery; :1890 and the three syntax_dump.c setjmp sites read and confirmed not to need the test. Full `make test` + Linux san owed at the [D105-BUILD] merge.) — formerly STATE:started (LAUNCHED 2026-09-18, sixty-ninth session, lane k60fix, sonnet, worktree worktrees/k60fix — Frank's ruling 2026-09-18: K60's LADDER class TAKES THE FIX, carry the OOM out of compile_driver's single recovery point ahead of every rung's eligibility test and the [ART-SIZE] ladder's blanket catch, built with docs/dev/k60_measurement.md §4.4's standards-clean spelling (bare `if (setjmp(cx.jb))`, a Ctx field set by ctx_nomem and tested first; per-arrival by construction because Ctx is memset per attempt). Bar: `make alloc` W4 108 → 0 with W1/W3 untouched (legend class = [D105-BUILD]), reverted-fix control RED, test-codegen identity green, K60 entry + D80 spec hunk in the same delivery.)

- [D105-BUILD] STATE:completed (MERGED fast-forward f5427d53, 2026-09-18 sixty-ninth session, lane d105 delivered in full: all three rider points, full-corpus emit-diff ZERO differing on both arms (default 1,500 compared; --features all 3,517 compared, 3,024 carrying a legend: 3,014 full / 23 brief / 14 truncated), `make alloc` fully green after the lane merged main and re-pinned W4 (W1 57/0, W2 11/0, W3 303/0, W4 158/0 — populations pinned per K35), control at the branch point fails 8 checks. Found and fixed en route: run_alloc_tests.sh logged stdout only so every red run said "0 witness(es) misbehaved". K60 CLOSED in both classes (D109 + D105). S260 NOT built — ruling for Frank: population pins in `make test` tax every allocation-moving refactor vs an undetectable plant (d105_report.md §5.2). Full `make test` + Linux `make san` running/owed at the manager.) — formerly STATE:started (LAUNCHED 2026-09-18, sixty-ninth session, lane d105, opus, worktree worktrees/d105 — Frank's re-ruling 2026-09-18: BUILD D105 AS ORIGINALLY RULED via its rider's restructuring: `path` a fixed 40-int local and its unbounded allocation DELETED; the four BFS arrays into the Job's arena with the Ctx attached so refusal rides the existing general mechanism; brief mode allocates no from/via. NOT an abi event. Bar: full-corpus emit-diff byte identity vs main, `make alloc` W1 15 → 0 and W3 25 → 0, control RED, D105 status line BUILT + K60 legend class FIXED in the same delivery. Retires 40 of K60's 148 absorptions, the only ones reachable without an injector.)

- [ALLOC-PINS] STATE:completed (DELIVERED 2026-09-18 sixty-ninth session,
  lane allocpins, sonnet, worktree worktrees/allocpins, branch lane/allocpins
  off fa70bf84 — Frank's ruling 2026-09-18 on the tension D105/d105_report.md
  §5.2 and the [REVW.2] w2b merge's own W4 158→162 measurement left open,
  D110: (1) tests/core/alloc_check.c's per-witness population expectations
  become FLOORS (half the measured population: W1 57→28, W2 11→5,
  W3 303→151, W4 162→81), never equality pins — expect_absorbed_single/
  sustained stay exact at 0 in both directions, both K60 classes closed;
  (2) tests/resource/run_resource_tests.sh section 2b now asserts
  alloc_check's own rc + absence of any SUCCEEDED THROUGH line, not only the
  KILLED THE PROCESS BY SIGNAL grep, so a plant reopening either K60 class is
  detectable inside make test itself; (3) scripts/battery.sh gains an alloc
  stage (after san, before lint; make test untouched, per Frank's own scope
  concern). Two sabotage rows, S259 (compile.c's D109 cx.failed_nomem
  propagation neutered — the ladder class) and S260 (emit_dfa.c's
  emit_state_legend dist array reverts to a raw malloc with a silent NULL
  return — the legend class), both solo-run DETECTED at 066c73178254008e0eb7
  c0a150589a9deb7fa7ea: S259 resource:1fail/26pass, S260 resource:2fail/
  25pass (the second fail is Section 0's allocation-site census, since
  emit_dfa.c is outside its pinned nine-file set — two independent
  instruments catching one plant). D110 recorded in decisions.md, K60
  pointer in known_issues.md, tests/core/CLAUDE.md and tests/resource/
  CLAUDE.md rewritten, tests/mech/sabotages/CLAUDE.md entry added. VALIDATED:
  make alloc green (8/0, populations unmoved 57/11/303/162, all above their
  new floors), the floor control fires RED in the failing direction (a
  scratch W2 floor of 1000 against its population of 11 — reverted before
  commit), bash tests/resource/run_resource_tests.sh green (27/0/0, 1
  expected darwin skip), make strict clean, bash tests/core/run_core_tests.sh
  green (2/0). Report docs/dev/lanes/allocpins_report.md. Not merged.)

- [REVW.2] STATE:completed (WAVE 2 COMPLETE at EP2 step 15 — w2y merged 7f0f1e55 and gated 2026-09-19 early morning, seventieth session; tag flipped 2026-09-19 evening, seventy-first session) — formerly STATE:started (GO Frank 2026-09-18 "next session"; LAUNCHED 2026-09-18 sixty-ninth session after the K60/D105 pair merged and its Linux san came back green — SLICE A lane w2a, opus, worktree worktrees/w2a: EP2 steps 1-9 (E1 vm_slot_ref, E2, E3, P1, P2, E0, P4, P3, vm_plan_capacities), one commit per step, byte-neutral per step under the four .c identity gates + the irsb arm + a scratch subroutine-call witness for the paths the arm cannot reach, anchors re-aimed and re-verified DETECTED per row; SLICE B lane w2census, sonnet, worktree worktrees/w2census: the emit_dfa.c third-category census (tools/review/fragment_census script + docs/dev/w2census.md, the combined repaired-criterion floor over both emitters) + the listing-reach measurement (a minimal pattern set reaching the four families run_ir_listing.sh's fixture misses; the manager rules on widening). SLICE B DELIVERED AND MERGED 2026-09-18 (lane w2census): combined repaired-criterion floor **80 statements / 91 declarators** (emit_vm.c 58/67 — EP2's 66 missed `flr[32]` at vm_revdet_rep, a bare literal sharing a declaration with two NAME_LEN buffers; emit_dfa.c 23/25, category (c) six sites incl. PCREC_STARTPOS_GUARD_TEXT_MAX sizing three sites across both files); tools/review/fragment_census.py + docs/dev/w2census.md. Listing reach: 39/41 with FIVE existing corpus patterns (lookbehind_widths, bothlinkage, gated, counterk, possessive) — BUT three of the four missing families are module-gated and run_ir_listing.sh passes no --features, so the widening is a harness-invocation change, not an array edit; the last 2/41 (vm_counter_phase, zero literal prefix) are permanently instrument-blind. MANAGER RULING: the stage-3 lane WIDENS run_ir_listing.sh (the five patterns + per-pattern --features) as its FIRST commit, sabotage-verified, before touching any buffer on the counter-rung/lookbehind/subroutine paths. SLICE A DELIVERED AND MERGED 2026-09-18 (lane w2a, 0dd6d29c): all nine EP2 steps, one commit each, byte-neutral on THREE streams per step (corpus argv 3,938 lines × .c/.c-vm/--emit-ir; composition route 304 sources/74 artifacts; run_ir_listing 93/0 incl. 11 irsb rows) against a git-archive binary of the branch point; NOT an abi event; 7 anchors re-aimed (EP2 said 9 — vm_plan_capacities carries none) and re-driven solo, unexpected 0 across all; category-(a) literal buffers in emit_vm.c 35 → 24 declarators; pcrec_emit_vm 2,387 → 2,071 lines. FINDING FOR STAGE 3: vm_splice's DELIVER block is reachable ONLY through the composition route (.rxtin fixtures) — the pattern corpus cannot witness it; the composition sweep is mandatory. SLICE C lane w2b LAUNCHED 2026-09-18 evening (opus): step 11 stage 3 — widen run_ir_listing.sh first (ruling above), land sb_fragf, retire the fixed buffers in BOTH emitters under the repaired criterion (floor 80/91 → 0 or a named exclusion list), fragment_census.py as the acceptance instrument. SLICE C DELIVERED AND MERGED 2026-09-18 evening (lane w2b, c87c7919): sb_fragf/sb_fragfv landed (src/core/sb.c, unit check tests/core/sb_fragf_check.c); fragment census 81 → 6 declarators over both emitters, the 6 a NAMED exclusion list (Vm.up + the six-buffer encoding-seam family: enc.h's buf+cap+trunc outputs and pcrec_startpos_guard_text's three destinations — retiring the latter three would orphan PCREC_STARTPOS_GUARD_TEXT_MAX and its --list-limits note, a D80 follow-up); run_ir_listing.sh widened 11 → 16 patterns with per-row --features, reach 30 → 42 of 44 (vm_counter_phase's two sites instrument-blind by construction), sabotage-verified both ways, five irsb baselines added; the widening FOUND TWO DEFECTS in the pre-existing resume-point check (RX_CALL's return address counted as a resume point; equality asserted where the property is pre-pass ≥ emitted) — repaired; 6 anchors re-aimed (charter predicted 4 — the two missed quote a buffer's CONSUMER, general form in the report §4.3), all six re-driven solo DETECTED; byte-neutral on 3,938×3 + 304 composition + 128/0 listing; NOT an abi event. Landing item at merge: W4's alloc population re-pinned 158 → 162 (first measured pin brittleness — see the alloc_check.c note). Stage 3 did NOT produce sb_name/sb_upper (deliberately: their purpose is a Vm.up retirement); X8 lands them on its own terms. SLICE D DELIVERED AND MERGED 2026-09-18 night (lane w2x, bbded35f): X8 COMPLETE across BOTH emitters — four kit primitives (sb_stampf, sb_stampwf, sb_stamp_str, sb_upper over one file-static body; sb_vprintf split out), 57 value stamps moved (37 of 37 emit_vm.c, 20 of 21 emit_dfa.c; the one residue _DFA_PREFILTER_OFFSETS streams its value); EP2's "52 sites" was 52 LINES over 44 statements, only 37 value stamps — the other 15 are seven multi-line macro BODIES no stamp helper can take, and its "4 abutting" anchors were THREE rows stacked on one line; Vm.up RETIRED (the derivation builds once via sb_upper into the arena; census now reads exactly the 6 encoding-seam exclusions); NOT an abi event (zero bytes moved: 3,938×3 argv, 304 composition, listing 128/0); S224/S225/S226 re-aimed and DETECTED solo; instrument lesson: a mech re-aim cannot be driven before it is COMMITTED (matrix takes source from git archive HEAD, definition from the working tree). Flagged, not fixed: S224's SAB_DOC_FIGURE records an 11-check vmframeless suite that has 6 checks today (predates the lane). Slice C's merge gate: make test 40/40, size log 0 movers. NEXT: steps 12-15 (F7 vm_wordb/vm_cap/vm_cat/vm_bref; F7 vm_count_slots; F14 vm_look_behind_branch; F8 vm_render_listing's loops), then DD-8 + [EMIT-VERB] as render-path customers, steps 12-15, then DD-8 and [EMIT-VERB] as kit customers of the render path. SLICE E DELIVERED 2026-09-18 night (lane w2y, branch lane/w2y from ac21aaaf, commits e051baa8/dbcb8dc1/310eae96/c8771806): EP2 steps 13/12/14/15, one commit each, COMPLETING wave 2 — vm_count_slots_look + vm_count_slots_rep (the three vm_cursor_fits scratch locals move with the A_REP arm, their only reader); vm_wordb/vm_cap/vm_bref/vm_cat, so vm_emit's ten arms are ten delegations (515 -> 238 lines); vm_look_behind_branch (196 -> 68, and the caller's `b` and `neg` move down with the loop body — the extraction is not purely additive and -Wunused-variable is what says so); vm_listing_events + vm_listing_slot_row/vm_listing_slots for F8's two families. NOT an abi event: byte-identical on FOUR streams per step (3,938 corpus rows x .c/.c-vm/--emit-ir at reach 3,517/3,518/3,518, plus 304-file composition at 96 artifacts from 32 producing files), instrument validated against the branch point first. EP2's anchor table is EXACT for all four steps (8/2/4/0) — the report §0 says when it can be: a span-resolution count is exact for a RELOCATION and a floor for a data-flow change, which is why w2a's and w2b's differed. 14 records over 12 rows re-aimed, all by dedent except S98 (its dedented BEFORE would also have matched vm_cost_rep, so it re-aims onto the new signature) and S133, whose SECOND anchor is in the preamble and must NOT move. FINDING the next sweep-builder needs: the COMPOSITION arm does not reach vm_splice's DELIVER block without --features all (both deliver fixtures need module `recursion`; 29 files/84 artifacts at default vs 32/96 with it), contradicting w2x §5's recorded claim — the arm's population is pinned nowhere and three lanes' hand-rebuilt drivers disagree. Step 15's stream has no .c identity gate, so its green was checked for vacuity by a listing-family REACH census over the same 3,518 listings: 0 unreached arms. make strict clean, run_ir_listing 128/0 and anchor integrity 284/268/0 after every step; make test-codegen 8/9 (the standing darwin nm/arm_a.o red), tests/vm 48/0 (its D46 arm is a SECOND live comparator for step 15, A/B'd 48/0 at the branch point). ALL 13 re-aimed rows driven SOLO and DETECTED, unexpected/undetected/unreached/anomalies 0 on every trailer. Nothing owed. WAVE 2 IS COMPLETE at step 15 — EP2's sequence has no step 16; DD-8 and [EMIT-VERB] are the queued render-path customers and w2y_report.md §8 tells them what changed under them.) — formerly STATE:not-started — wave 2 (emit_vm.c interior): EP2's 16-step SLICE E MERGED 7f0f1e55 (--no-ff, 2026-09-19 00:2x, seventieth session): review accepted on the four-stream evidence + the listing-reach vacuity check + 13/13 solo DETECTED; post-merge build/strict/alloc green; merge-gate `make test` launched detached (3h bound). WAVE 2 IS COMPLETE AT STEP 15; the row stays started until its two render-path customers land ([DD-8] lane dd8, then [EMIT-VERB] after Frank rules its shape). w2y §3.2 chartered [BSWEEP].
  sequence authoritative (E1 `vm_slot_ref` first), fragment retirement under
  the REPAIRED floor (58/66, three sizing categories; emit_dfa.c
  third-category census first). X8 rides stage 3 (M1). DD-8's --emit-ir
  adoption rides this wave. Q3 folded (D106 add.3): slot[48] truncation free.

- [BSWEEP] STATE:completed (MERGED 02239219, 2026-09-19 ~04:4x, seventieth session — lane bsweep delivered in full; landing item by the manager: the -o basename-trap comment at the `-o -` site; the lane found and fixed two reach bugs in its OWN first cut — an rc==0 gate that skipped a fixture's partial success and a composition timeout under the argv streams' concurrency — which reconciles w2b/w2y/dd8/bsweep to 32/96 and leaves w2x's 30/72 as a probable instance of the same class) — formerly STATE:started (CHARTERED 2026-09-19 by the manager from w2y §3.2, admin column, sonnet lane bsweep launched after slice E's merge gate) — THE COMMITTED EMITTER BYTE-NEUTRALITY SWEEP: `scripts/emit_sweep.sh` (ref binary from `git archive REV` vs the tree; four streams, `--features all` everywhere — corpus argv × .c default / .c --engine=vm / --emit-ir --engine=vm, plus the composition arm over every .rxt/.rxtin; per-stream population, REACH, movers, asymmetric rows; reach FLOORS pinned per D110's shape plus the specific DELIVER-block witness; a --self-check ref-vs-ref run first). THE MEASURED NEED: five wave-2 lanes rebuilt it from prose and three recorded three different composition populations (30/72, 29/84, 32/96) because the arm's reach is a property of `--features all` that nobody wrote down — a mandatory arm that can be silently empty (K35's shape). Validation bar: self-check identical with full reach; ac21aaaf vs 7f0f1e55 identical (re-verifies w2y by a committed instrument); three scratch plants (a .c byte, a listing byte, a DELIVER-block byte) each reported by exactly the stream that should see it. docs/testing.md section + scripts/CLAUDE.md entry travel with it.

- [EMIT-VERB] STATE:completed (MERGED 6ff185cf + rider 74c2192c + triage 13382458/f4a64947/489a8503, GATED with wave 4 2026-09-19 21:08 — abi 27, comments OFF by default, -fcomments restores; source bytes −36.3%) — formerly STATE:started (DELIVERED 2026-09-19 on lane/emitverb from lane/w4's tip 4af16eb7, lane emitverb, opus; PARKED behind wave 4's own merge; report docs/dev/lanes/emitverb_report.md) — TWO EVENTS AS D112 ITEM 4 ORDERS. **EVENT 1, byte-neutral**: the axes.def row (the first reader of D111's `default_state` column, via the general `pcrec_axis_on(flags, deny, force)`), bits 26/27 as PCREC_NO_COMMENTS / **PCREC_FORCE_COMMENTS** (NOT `PCREC_EMIT_COMMENTS` as w4 §2 item 4 (c) predicted — `axes_registry_check.sh` derives the header's bit table with a `PCREC_(NO|FORCE)_` grep, so the naming convention is encoded in a check), both bits masked out of rx_info.flags, `--list-axes`' two rows with their DEFAULT sentence DERIVED from the table so the flip does not re-pin it, tuning.md §2.24; the gate is `sb_comments`/`sb_cmt_open`/`sb_cmt_close` in src/core/sb.c with the mute test at the three primitives (D108), 65 NON-ESSENTIAL regions + 2 ESSENTIAL, and the encoding seam's verbatim text blobs SPLIT into doc/code halves in PcrecEncEntry (a verbatim blob has no emission event to gate unless the split is in the DATA). emit_sweep 0 movers / 0 asymmetric on all FOUR artifact streams at full reach. **THE .o PROOF FOUND A REAL DEFECT AND IT IS NOT A LINE-NUMBER LEAK**: 5 of 3,517 artifacts' OBJECT FILES differed, because emit_vm.c's entry-shape AUTO rung compares `job->vmsb.len` — RAW bytes, comments INCLUDED — against the 4,096 knee, so a comment-free program crosses it and takes rung `forward` where the default takes `plain`. Fixed by making the GATE size-neutral (`sb_len_uncut` = len + the bytes a muted region discarded; every length-based decision reads it), NOT by re-basing the term — whether a size term should price comment bytes at all is left open with its measured population (D77). Re-run: **3,517 / 3,517 .o IDENTICAL**. Byte share 44.2% (DFA 45.6%, VM 43.1%). **EVENT 2, the flip (abi 26 -> 27)**: one token in axes.def; movers 3,517 / 3,518 / **0 (emit-ir, as predicted — the listing is not the artifact)** / 96 / 1; source bytes 146.6 MB -> 93.4 MB, **-36.3%**, the gap to 44.2% being the ESSENTIAL set's fixed ~3,272 B/artifact. New check tests/codegen/run_comments_axis.sh (65/0, in test-codegen) is the only script in the tree that compares a `-fno-comments` artifact against anything. Checks converted: the M5-SEAM residual extractor (now reads DECLARATIONS, a strengthening), D37 × 4 and cli case14 × 6 + case10 (read the STAMPS), run_comment_escape.sh (`-fcomments`, the one place the comment IS the thing under test), the cpset EMITTED_BYTES manifest re-recorded 12/12. **THE COMMENT-READER CENSUS WAS DONE BY MEASUREMENT, NOT GREP** — two grep passes were run and both were useless (needles built from shell variables; generic substrings matching emitted prose), so flipping the default and running the suites IS the census. Two D94-addendum readers found by the suites that COUNT: the registry's axes coverage pin 102 -> 108 (cites no axis, macro or abi digit) and the cpset manifest. FINDING, pre-existing and made live by the third force macro: run_axes.sh derived "the one DO-OR-DIE axis" by `PCREC_FORCE_*` NAME PREFIX keeping the last match — two candidates already, picked by bash hash order; named explicitly now with a FATAL. OWED: the (B) FILEPIN re-pin (must name a post-merge commit, opt5i/ccdiff1 precedent — that gate is red on the branch by construction), the full-corpus size-log regeneration (PREDICTION: `size_bytes` moves NOT AT ALL, since the log's column is the comment-EXCLUDED count; a mover there is a finding), `make test`, `make mech`, `make test-axes`. S07 and S257 re-aimed and re-driven SOLO, both DETECTED.) — formerly STATE:not-started (OPENED 2026-09-18, Frank: "these user
  comments should have an emit/no-emit option (some general option around
  code verbosity)") — A VERBOSITY AXIS OVER THE EMITTED ARTIFACT'S HUMAN
  COMMENTARY. **RIDES WAVE 2 AS AN EMISSION-KIT CUSTOMER, exactly like
  DD-8**, and the sequencing is the whole point of the row: there is NO
  chokepoint today (~1,247 comment-emission sites across emit_dfa.c and
  emit_vm.c; `emit_comment_safe_byte` is a byte-ESCAPING helper, not a
  gate), so building it now is ~1,247 hand-edits, and building it after the
  kit is ONE gate in the render path. D108 puts it in exactly the right
  place: verbosity is a RENDER-time property of a data-in/text-out layer —
  the walk emits comment EVENTS, the renderer decides whether their text
  reaches the artifact.
  TWO MEASURED FACTS THAT SHAPE IT, both already in the tree:
  (1) **the size cap CANNOT move** — `PCREC_MAX_EMIT_BYTES` is explicitly
  "the whole comment-EXCLUDED artifact" (limits.def:160; compile.c:179
  "TOTAL is the artifact minus its comments"), so no verbosity setting can
  rescue or refuse a pattern. The K59 refusal-set hazard is structurally
  absent here — state that in the design rather than re-deriving it.
  (2) **the win is SOURCE size and readability, not object size or speed** —
  [ART-SIZE] measured comments correlating with `.o` at r=0.43 against
  program+tables at r=0.99. A no-comments mode is for embedders shipping
  generated source, not a performance axis; do not let it be sold as one.
  OPEN AT OPENING: the axis's SHAPE (a boolean `-fno-comments`, or LEVELS —
  the tree already has a precedent in the legend's own brief mode at
  `n > LEGEND_MAX_STATES`, and in `--tune`'s ordinal); whether it is an
  `axes.def` row (wave 4's X9 design event is the venue, and this row is a
  second customer for it); what the identity gates and the `abi` ritual do
  with a mode whose whole purpose is to change emitted bytes (the DEFAULT
  stays byte-identical, so it is a new AXIS rather than an abi event — the
  `test-axes` answer-identity sweep is its natural home). D80: it is a
  caller-observable surface and needs its `docs/spec/` hunk in the same
  change.
  RULED 2026-09-19 (Frank, seventy-first session): BOOLEAN — one
  `-fno-comments` row in the deny family of `axes.def` (D111 makes it a
  row; run_axes.sh derives the bits from lib/pcrec.h, so the answer-identity
  sweep covers it with no new check); NOT an abi event (the default stays
  byte-identical; the identity gates never see the no-comments artifact);
  "a comment is text the C compiler discards — the stamps are defines and
  stay"; the two measured facts above are STATED in the design, not
  re-derived; sold to embedders shipping source, never as a performance
  axis. SEQUENCED after [REVW.4]'s X9 lands, as its own small lane — the
  first new row on the table. Levels wait for a measured need (D77).
  DEFAULT RULED OFF (Frank, same session, D112): the switch removes every
  NON-ESSENTIAL comment ("most all"); ESSENTIAL = provenance (generated-by
  line with the abi, the pattern echo) stays; the class is the seam a
  future levels change extends. Two events in one lane: the flag
  byte-neutral with default on (+ `.o` identity proof on/off over the
  corpus + the comment-reader census), then the flip as abi 26 → 27 with
  the full ritual. Measured: comments are 43-53% of a default artifact.

- [REVW.3] STATE:completed (GATED 2026-09-19 07:49, seventieth session: merge-gate make test 40/40, sole FAIL the standing darwin nm probe, size log 0 movers over 3,480 rows) — formerly STATE:started — wave 3 (layering): L6 L1+L3 LAND TOGETHER
  (enc/ -> src/enc/ + the layer model in tool and prose), the rxt minimal
  cut (2 files, 0 anchors), L4-dump relocation rider, internal.h
  declaration-grouping (split deferred). M4: no compile.c move.
  **DELIVERED on lane/w3 (2026-09-19, lane w3), five item commits +
  report `docs/dev/lanes/w3_report.md`, awaiting the manager's merge
  gate**: dump tier -> `src/dump/`, `src/gen/enc/` -> `src/enc/` (with
  `third_party/ucd-16.0.0/generate.py`'s three path sites and a
  `make gen-tables` proof), the layer order
  `lib -> core(base) -> enc -> parse -> ir -> opt -> gen -> driver ->
  dump -> cli` in `include_graph.py` (via a per-file tier override table)
  and in `src/CLAUDE.md` / `APPROACH.md` §8 / `coding_guide.md` §1.9, the
  rxt cut (`Ctx.compose` + `src/core/compile_defs.c`, `nm`-proven in both
  directions), and `internal.h`'s declaration tail grouped by defining
  layer. Every item byte-neutral on all four `scripts/emit_sweep.py`
  streams at full reach; NOT an abi event; no `docs/spec/` hunk owed.
  **Two findings for the record**: the call-level back-edge census is
  30, not lens 6's predicted 19 — the `driver` reclassification turns 20
  edges forward and creates 22 new ones, all `ctx_fail`/`ctx_nomem`, so
  `compile.c` is itself two layers; and item 1's dump move has TWO
  sabotage anchors (S18, S241) where lens 6 priced it at zero and left
  its own coupling grep unrun. **Wave 4's brief must cite
  `src/dump/axes_dump.c`, not `src/parse/axes_dump.c`.** MERGED 86e7c8da (--no-ff, 2026-09-19 06:1x, seventieth session; lane w3, opus, ~55 min): all five items, byte-identical on all four streams after each via the COMMITTED scripts/emit_sweep.py (its first lane customer), NOT an abi event, no docs/spec hunk owed; call-level back-edge census re-measured 39 → 30 (item 1 alone 39 → 28; the driver tier reclassifies 20 forward and exposes 22 ctx_fail/ctx_nomem edges INTO compile.c — the file is itself two layers; nothing proposed, D77: moving ctx_fail/ctx_nomem/pcrec_default_options to a base-tier file would take it to 8); include_backedges.tsv 6 → 0; lens 6's "0 anchors" for the dump move was 2 (S18, S241) + 62 citations; run_cpset_structure.sh CHECK 1R fixed to find the header by name (a relocation would have changed its red's CAUSE silently); APPROACH.md §8 rewritten (flagged for Frank, w3_report.md §5); coding_guide.md §1.9 added; clean rebuild + strict + alloc green on main; merge-gate make test launched 06:1x (3h bound). Wave 4's brief must cite src/dump/axes_dump.c.

- [REVW.4] STATE:completed (GATED 2026-09-19 21:08, seventy-first session: darwin make test on f3eb6f82 (abi 27, all eight branches) 40/40 sections in 48 min, FAILs = the standing nm probe + three readers evtriage3 fixed and merged 489a8503; size log 0 size_bytes movers over 3,480 rows, +1 row) — formerly STATE:started (MERGED f7a683d8 2026-09-19 15:4x after the I-75 Linux battery at 923a5a58 came back GREEN — all 7 stages rc=0, mech 268 rows unexpected 0 / anomalies 0 / undetected 10 documented-expected / unreached 1 (S121), san green, alloc rc=0; darwin merge gate pending behind [EMIT-VERB]'s rider; DELIVERED 2026-09-19 ~10:2x, seventy-first session — lane w4, opus, ~80 min, PARKED on lane/w4 (9 commits from 39860b66) until the I-75 Linux battery's trailer; report docs/dev/lanes/w4_report.md, read its §0 first. All five items + census regen; every item 0 movers on emit_sweep.py's four streams AND the new fifth `dumps` stream (7/7 dumps byte-identical across X9; positive control: 1 mover = item 1's new --list-limits row); lib/pcrec.h BYTE-IDENTICAL — D111's generated-block lean priced at 650-700 lines and declined per its stop condition, the row names the bit as a TOKEN (D111 addendum); both awk scrapers deleted, 22 reconciliation checks → 22 live acceptance probes; S261 new; S208/S209 canonical figures recorded; docs/spec/ carries ZERO cli/main.c line citations now (all 27 were rotten, re-aimed by spelling); L11-F6's "X9 is the whole remedy" for emit_predicate_axes is FALSE (178 code lines before and after — a table removes columns, never narrative rows); one re-pin missed and repaired (D94 addendum: run the suites that count). Manager review: strict clean on the branch, hunks as described. Merge gate: darwin make test after the trailer.) — wave 4 (CLI+config): the cli_parse table
  (L11+L2+L1-X10 one item, M3), mode mutual-exclusion written once, D107
  filter inversion, F2 bar->limits.def; X9/axes.def RULED BUILD (D111,
  Frank 2026-09-19 "Yes. I like single source" — one X-macro source, every
  reader derived, the two awk scrapers deleted; header enumeration
  generated at build time, manager's lean pending w4facts). Fact sheet
  lane w4facts (sonnet, read-only, docs/dev/lanes/w4_facts.md) launched
  2026-09-19 08:5x, seventy-first session; brief cites
  src/dump/axes_dump.c.

- [REVW.5] STATE:completed (GATED 2026-09-20 05:14, seventy-first session: darwin make test on e2368779 40/40 in 30 min, sole FAIL the standing nm probe, strict clean; size log 0 size_bytes movers; pushed) — formerly STATE:started (MERGED 55321f28 + axtriage e2368779, 2026-09-20 ~04:4x after the I-77 battery at 25b1984f came back green on every stage but the triaged axes pin (mech 269 rows, 0 unexpected, the same 10 documented undetected by name, S121 unreached); main rebuilt: ZERO non-pcrec_ exports; darwin gate (test+strict) launched 04:4x, log build/battery_gate_e2368779/; then push + the wave's Linux battery (I-78). DELIVERED 2026-09-19 ~23:5x, seventy-first session — lane w5, opus, 15 commits from 25b1984f, PARKED on lane/w5 until the I-77 battery's trailer; report docs/dev/lanes/w5_report.md. HEADLINE: libpcrec.a 295 exports, ZERO without pcrec_ (population was 34, not 29: EMIT-VERB's four sb_* gate primitives joined between the sheet and the lane; ten rename commits grouped by blast radius, nfa_* first, ctx_fail last; six full-corpus sweeps 0 movers on all five streams; anchors 285/285 after every commit via scripts/m6read_check_sab_anchors.py; 9 rows re-driven solo DETECTED, 24 more owed to the merge battery's full matrix). Spec sweep done (pcrec_options 9 → 19 quoted as shipped; tuning.md §4 mirror 14 → 28 and exhaustive); UNION MODE MEMBERSHIP MEASURED AND NOT BUILT — 4 acceptance flips, three of them --flavour's documented primary use; w4's asymmetry premise was false (--probe-ask --flavour already refuses) — proposal: --flavour gets its own applies-to relation (manager: a [REVW.5.1] rider); limits surface: pcrec_limits_tsv declared in lib/pcrec.h (one declaration, not eight #defines — D90), two of the eleven cited constants were NOT REAL (one deleted at [OPT-4], one with an invented prefix); PCREC_DEFAULT_FEATURES → pcrec_default_features (a name-keyed floor filter re-aimed); [REVW.A1] landed: match_api.md §6 is THE abi log (D76 addendum), emit_dfa.c's 449-line out-of-order log → 22 lines, the codegen check backfilled. FLAGGED FOR FRANK: lens 9 §5.1's K9/NUL-termination sentence (an open issue with two remedies). FLAGGED, not fixed: tests/spec_mod0/check01_isolation.sh's positive control is dead on darwin (nm's `_` prefix) since the two-machine split — the rider fixes it. OWED: its make test (running in worktrees/w5) + the 24 solo re-drives (the battery's matrix covers them).) — formerly STATE:not-started (FACT SHEET MERGED 8d961dc0, 2026-09-19 — docs/dev/lanes/w5_facts.md: P2/P7/P8 already done; P3/P6 one spec sweep; P4 needs its own re-read in-wave; the union mode membership rides the spec sweep with w4_modesweep.py as instrument; the rename population is 29 (D104 addendum: group by blast radius, per-commit witnesses, make test while iterating, one battery at close); [REVW.A1]'s home is RULED match_api.md §6 (gap-free 2 → 27, maintained by every bump) — the other three homes become pointers. Launches from the gated abi-27 main.) — wave 5 (public surface): L9 §8 order; D104
  renames name-by-name (nfa_* first, ctx_fail last); P3/P6 spec hunks may
  ride any earlier wave's D80 batch.

- [REVW.A1] STATE:completed (LANDED in wave 5, lane w5 commit 2c5c1948, merged 55321f28, gated 2026-09-20 05:14: docs/spec/match_api.md §6 is THE abi log (D76 addendum; gap-free 2 → 27, maintained by every bump's own spec hunk); emit_dfa.c's 449-line out-of-order comment log → 22 lines + pointer; src/gen/CLAUDE.md a pointer; the codegen transition check kept and backfilled (20→21, 21→22) with §6 named as its source. THE 2026-09-17 CODE-REVIEW REFACTOR IS COMPLETE — fix-now, waves 1/U/2/3/4/5, A1; Frank's guided tour is next.) — formerly STATE:not-started — LAST: L4-A1 abi-log reconciliation as its
  own change (three drifting homes, two transitions recorded nowhere).

### Design-debt ledger

- [HDR-1] STATE:completed (MERGED 2026-09-20 ~13:3x, seventy-second session: lane/hdrgen 4525e60d + lane/hdrrest 3ba8ed08 — 405 headers, comments only, both lanes emit_sweep 0 movers on five streams vs c007e9d2, strict clean, anchors 285/285; post-merge census `header=910 banner=6 none=2` — the residue is the printf-attribute forward-declaration pair vm_rolef/dfa_fragf, headed above the declaration, plus banner-only rows the census still scores; UNCLEAR list empty on both lanes) — formerly STATE:started (CHARTERED by Frank 2026-09-20, seventy-second session: "it would be helpful if the functions had a header comment that indicated their purpose. e.g. from the name, it isn't clear what 'vm_ev' is about" — extends L4-C1's >=50-line rule to EVERY function under src/, cli/, lib/. Population measured at 11ff5f51: 917 functions, 504 headed, 75 banner-only, 338 none = 413 owed (docs/dev/hdr1_census_2026-09-20.txt; emit_dfa.c 109, rxt_source.c 28, emit_vm.c 28, sb.c 23 lead). Two lanes: hdrgen (opus, src/gen only) + hdrrest (sonnet, everything else + the census tool's new `header` column + coding_guide.md §4.2's rule hunk). Byte-neutral by construction — emit_sweep.py against the branch point is the gate. Runs alongside nothing; before the guided tour.)

- [HDR-2] STATE:completed (MERGED 756e6f64, 2026-09-20 evening, lane hdr2, sonnet: coding_guide §4.2 first-sentence rule; 49 emit_vm.c + 44 emit_dfa.c headers rewritten; acceptance re-run functions 57% → 83% under condition B (bar 68 MET); fields 42 → 32 MISSED but inside the instrument's measured run-to-run spread (locals, untouched, went 56 → 4 — the noise floor; experiments file addendum); comments only, emit_sweep 0 movers on five streams, strict clean, anchors 285/285. Residue: the Vm fields with NO trailing comment at all (cx, enc_mask, rgn_emit and kin) — a field's comment is its header; rides the next src/gen lane.) — formerly STATE:started (CHARTERED by Frank 2026-09-20 evening, seventy-second session, from the readability experiments (docs/dev/reviews/2026-09-20-readability-experiments.md §1): a header TRIPLED field comprehension (15% → 42%) and HURT function comprehension (68% → 57%) because the HDR-1 headers lead with the invariant/cross-reference, not with what the function does. The pass: (1) coding_guide.md §4.2 gains the FIRST-SENTENCE rule — a header's first sentence says what the function does in plain words; the invariant and cross-references follow; (2) every HDR-1 header in src/gen/emit_vm.c and emit_dfa.c re-read against the rule, rewritten where the first sentence is a tag, a cross-reference or an invariant; (3) the 74-name failed list (grade_summary2.md §d, second list) fixed by name; (4) ACCEPTANCE IS THE EXPERIMENT RE-RUN: build_conditions.py on the new tree, a haiku guesser on cond_B, the same grader — functions under B must reach ≥ A's 68% (was 57%). Lane hdr2, sonnet, worktree worktrees/hdr2. Comments only; emit_sweep 0 movers; anchors 285/285.)

- [DD-13c] STATE:completed (CLOSED 2026-08-26 09:1x on the battery-proven tree 6e8edfb: matrix 180/0/6/0/0, full san 33/33 green, test 1,570; bench inbox I-6 sent; MERGED a895184 2026-08-26 ~04:5x — abi 6, (B) pin c940551; the FINAL battery on the combined tree is owed after srAnchor re-anchors S179/S183/S67; launched 2026-08-25 ~20:4x, lane srStamp2, opus) — THE STAMPS' SCOPE (r37 A5/A6) + the RUNTIME MIRRORS (Frank, D40 addendum): `RX_DFA_SCAN "empty"` for the four no-loop artifacts; VM HYBRIDS (1,263 of 1,488 VM artifacts) stamp their inlined DFA scan's `RX_DFA_SCAN`/`RX_DFA_PREFILTER` from the same derivation, the check's leak assertion becomes an iff; `struct rx_info` gains `scan` and `prefilter` string fields (appended; NULL where n/a; one derivation feeds macro and field); abi 5→6 (srTier's 4→5 merged first), (B) re-pinned, (A) unchanged. REBASED onto main 95320df (srR37's shipped run_dfa_stamps.sh, the A7/A8/A4 doc hunks and the atomic_groups §3 value-based discriminator all inherited; my redundant versions dropped). **MEASURED after the rx_info addition:** run_dfa_stamps.sh **29/0** over 2,772 patterns — 995 DFA (4 empty-engine) / 1,488 VM (1,263 HYBRID, 4 of those inlining an empty scan; 225 plain) / 289 refused; DFA prefilter none 380 / memchr 327 / byte-class 176 / memchr-bounded 61 / byte-class-bounded 51 — STILL IDENTICAL to [DD-13]'s recorded figures, the control that neither half of this change moved the DFA side — DFA scan unanchored 811 / attempt 180 / empty 4; hybrid prefilter memchr 825 / none 264 / byte-class 137 / memchr-bounded 20 / byte-class-bounded 17, hybrid scan unanchored 1,071 / attempt 188 / empty 4; the MIRROR assertion (rx_info.scan/.prefilter == the macros, NULL/"none" where absent) runs on all 2,483 compiled artifacts of BOTH engines, with the field LINE COUNT asserted so it cannot go vacuous. FIVE MEASURED validation reds against the 29/0 baseline: hybrid silent 21/5, gate dropped 24/2, empty arm removed 23/3, mirror written from a second spelling 28/1 (376 = 368 attempt + 8 empty exactly), mirror fields not emitted 27/2 (BOTH the line-count red and the counted-denominator red — without them the value comparison would have been vacuously true). TWO CHECK DEFECTS FOUND BY THIS LANE'S OWN VALIDATION and fixed: (i) the [agreement] denominators were arithmetic over bucket sizes, so a plant that routed 1,263 artifacts past a comparison still read "on all 2258" — they are COUNTED at the comparison sites now and the shortfall is asserted; (ii) run_codegen_tests.sh pins rx_info.abi by a hand-spelled literal and fired correctly (104/1) on the first `make test-codegen`, which is a second site every future abi bump must touch. SWEEP for the absence/presence-as-DFA hazard (manager's ask): 17 tests/*.sh read RX_ENGINE/RX_DFA_*; ALL are value-anchored or comment-only, NONE presence-based, and run_dfa_stamps.sh is the only reader of RX_DFA_* at all. abi 5→6 ([OPT-1]/srTier took 4→5 immediately before; LAYOUT event: fields appended at the END, no existing offset moves; the abi comment names BOTH artifact kinds per r37 A12 — the mirror image of [OPT-1]'s VM-only note), (B) re-pinned 469a432 → c940551. ALSO FIXED in passing: docs/spec/tuning.md §3 shipped on main with lane srStamp's editorial wrapper merged into the published spec (d8608ca).

### Parser structure — the syntax construct registry

- [TT-2] STATE:completed 2026-08-15 (lane tt2-parallel — relaunched after
  the first lane died mid-work, its sharding adopted with two defects
  fixed; merge ce2a080. Measured: reject 59.5s→5.8s at PROCS=12;
  test-vm 30.4→14.9s and test-codegen 10.1→8.7s via tests/lib/
  run_group.sh; `make -j$(nproc) -Otarget test` composes the full suite
  in ~44.6s vs ~8m49s serial; cli/registry measured and DECLINED with
  a re-measurement trigger (registry is correction-scarred, off the
  critical path); mech already had PROCS since 2026-08-12, verified.
  Sabotages both shapes per new path; serial PROCS=1 full suite green
  8m48.9s; populations conserved. docs/testing.md "Internal
  parallelism" section) — PARALLEL TEST INFRASTRUCTURE (Frank,
  2026-08-15, twenty-first session: "we have 6 cores. we should open it
  up"). Step 1 DONE same day (Makefile commit): make test/test-corpus
  set PROCS=nproc + TMPDIR=/var/tmp for the harness's existing worker
  mechanism — corpus 1449/0 in 56s at PROCS=12, was ~5min serial. The
  REMAINING work, one lane once the D45-stopgap branch merges (its
  timeout wrapper touches the same runner scripts — disjointness):
  internal parallelism for the other serial suites (reject 528, codegen,
  vm, cli, registry — xargs -P or run.sh's worker-reinvocation pattern,
  whichever fits each script), section-level composition (make -j over
  the TT-1 section targets, output legibility preserved), and a mech
  assessment (parallel sabotage rows need per-row build dirs — measure
  whether the win justifies it). DISCIPLINES that travel with it:
  run.sh's own aggregation rules are the house template — a lost worker
  HARD-FAILS (never reads as a pass), summary-line format stays
  grep-identical in both modes (mech reads it); population accounting
  exact at every PROCS; D45 timeouts must hold under full parallel load
  (sub-second compiles × 12 workers is fine at 5s — but MEASURE the
  tail, don't assume); wall-time before/after recorded per suite.

### Optimization waves (D21)

- [OPT-1] STATE:completed (CLOSED 2026-08-26 ~11:5x on Frank's ruling ("agree with recommendations"): the tiering bet HOLDS on the exemplar workload — 2/165 orig, 7/165 factored escalations, one of them a 25 B subject; STEP 4 (static length thresholds) stays a chartered-NOT-started candidate, reopened only by a population that asks — [B11]'s log-line set through the same counter (D77). The loop's first optimization: chartered from a bench row 2026-08-25 ~14:3x, shipped abi 5/6, measured closed the next morning. STEP 3 MEASURED 2026-08-26 ~13:3x, lane srEsc, sonnet, tests/bench/tier_escalation.sh + tier_escalation_driver.c (new; counts real -DRX_TEST_TIER_HOOK calls per subject, not run_tiered_entry.sh's synthetic depth ladder): the escalation RATE over pcrec-bench's bench/email exemplar (RFC 5322, READ-ONLY sibling repo) — orig.rx/factored.rx forced --engine=vm (confirmed: `auto` selects DFA for BOTH here, which has no tier — a DFA-forced run would measure nothing) in the whole-subject form (`(?:P)\z`, `rx_match_caps`, the 85 compliance subjects) and the search form (`rx_search`, the 77 search_short + 3 x 1MB throughput subjects), plus `floor.rx` (`@`) as a negative control ridden through the same pipeline (single-tier by construction, 0/165 escalations, as required). MEASURED, whole-subject: orig 2/85 (2.35%, s-058 4011B pathological 2000-deep dotted local part + s-061 2008B long many-label domain, BOTH still MATCH through the deep tier — the stamped 2048/3072 default suffices for the hand-inlined pattern) vs factored 6/85 (7.06%, the same two PLUS s-059/s-063/s-064 — and **s-058/s-059/s-061/s-063/s-064 all give up PCREC_ERR_FRAMES(-3) with escalated=1 on every one, exactly the bench inbox's P2**, confirming they do not fit even the stamped default, matching pcrec-bench's independently-measured 32768/131072 `_in` sizing — PLUS s-072 (25B, "quoted string missing closing quote", the exponential-backtracking hazard class NOTES.md names), which escalates and still answers nomatch, the SMALLEST escalating subject in the set (two_tier_entry.md section 7's "deep can be a very short subject" cliff warning confirmed on a REAL subject rather than the synthetic `((a)|(aa))+b` witness). search_short: orig 0/77, factored 1/77 (s-072 again, 25B, still MATCHES here). throughput: 0/3 both patterns — `t-c-long-atom-run` gives up on STEPS/WORK before ever reaching FRAMES (orig giveup:-4 WORK, factored giveup:-2 STEPS, both escalated=0), so it never triggers the mechanism this instrument counts. Boundary sizes (bytes): orig/factored whole-subject maxNoEsc=10252 (s-057, 10KB local part of plain atom chars — LARGE but cheap, not ambiguous); factored whole-subject minEsc=25 (s-072); orig whole-subject minEsc=2008 (s-061); factored search_short maxNoEsc=43 minEsc=25. TOTALS: floor 0/165, orig 2/165 (1.2%), factored 7/165 (4.2%) — **the bet holds on this workload**, so D77's own trigger for STEP 4's static fast/deep predictor is NOT met by this number alone; the five factored FRAMES give-ups are a separate, already-known problem (undersized stamped default for a call-bearing pattern, already fixed by the measured `_in` buffer) that STEP 4's guess-the-boundary heuristic would not change, since it only chooses fast-vs-deep and never grows the deep budget. NO pcrec-internal exemplar subject FILE exists (checked: tests/*/gen_corpus.py generate synthetic .rxt corpora procedurally, tests/bench/run_bench.sh's THROUGHPUT subjects are generated on the fly, neither is a stored real-world population) — bench/email is the only exemplar measured. Full per-cell/per-subject table: `bash tests/bench/tier_escalation.sh` (not archived verbatim here). STEP 2 CLOSED 2026-08-26 09:1x on the battery-proven tree 6e8edfb — the two-tier entries ship at abi 5 (then 6); NEXT = STEP 3, the escalation rate over exemplar subject files via the -DRX_TEST_TIER_HOOK counter, before any fast-size tuning or STEP 4's thresholds; STEP 2 MERGED 48e0c41 2026-08-26 00:02 — its battery on d0a9ab5 GREEN (test 1,558/0, san, matrix 180/0/6/0) with THREE anchor ANOMALIES (S179/S183/S67 drifted under the entry refactor; re-anchoring in lane srAnchor); two abi second sites and one K35 sort the lane missed were fixed on main (bf20427, 31926ca); a 64-byte sentinel buffer vs the 60-char prefix limit fixed (d0a9ab5) and exposed K38; lane srTier — the TWO-TIER DEFAULT ENTRY, design docs/design/two_tier_entry.md written before the code: one emitter for the three un-suffixed entries, fast capacities derived ONCE and read by both the stamps and the bind, `RX_FAST_FRAMES`/`_FAST_TRAIL` on every VM artifact, escalation to a noinline deep function on FRAMES only, `-fno-tiered-entry`; abi 5, (B) pin 469a432, (A) unchanged; run_tiered_entry.sh 17/0 incl. the effectiveness floor and the caps-array span comparison; K33 narrowed; rx_search 131,216 → 3,184 B; 213-268 → 45.6-48.8 ns/call; the numbers and the r38 dispositions are in the merge commit and the review. STEP 1 MEASURED 2026-08-25 ~19:3x, lane srOpt1, no code: REPRODUCED 2.2× on the bench's `quick` (pcrec-vm 29,737 vs vm-in 13,548 ns/call, 77 subjects) and 5.05× on a 16 B fast-matching subject (233.8 vs 46.3 ns/call, N=100k, median of 5, taskset). ATTRIBUTED: (a) gcc STACK-CLASH PROTECTION probing the 98,512 B `rx_run_buffers storage` local (24 pages; `-fstack-usage`: rx_search 98512, rx_search_in 208) — `-fno-stack-clash-protection` alone: 233.8 → 46.2 ns, i.e. ~99 % of the gap; (b) per-call init is 144 B on BOTH paths (excluded by code reading); (c) page faults O(1) per process, a pre-touch control changes nothing (excluded); (d) frame 24 B, SPLICED, no linked call (excluded). GENERALITY: the tax is proportional to the STAMPED default — `(\w+)\s+\1` (2/5 frames, 272 B) and `(?<=foo)bar` (3/3, 240 B) pay NOTHING (0.98×, 0.99×); it hits patterns whose default is large, i.e. the deep-sized ones. STEP 2 — THE FIX, RULED by Frank 2026-08-25 ~21:2x ("an elegant use of the frames error; I agree with the approach"): the TWO-TIER ENTRY — the un-suffixed entries carry a SMALL on-stack buffer (a page or less: e.g. 64 frames / 96 trail = 3,072 B) and, on PCREC_ERR_FRAMES only, call a separate `noinline` deep function that owns the full stamped storage and re-runs the match (the VM is deterministic: byte-identical answers; §5.3's no-allocation/no-thread-local contract kept; the depth ceiling D73 ruled is UNCHANGED; the probing cost moves to the slow path only). D6 CRITIC r38 (docs/dev/reviews/2026-08-25-r38-two-tier-entry.md): NO blockers — identity byte-for-byte across 377 escalations incl. captures, noinline survives LTO; five should-fixes to the lane (the spec blended two specimens' numbers; the ESCALATION CLIFF must be stated — ~1.6× SLOWER above the fast boundary, 2.8× discontinuity at it, on `((a)|(aa))+b` 'deep' is a 22-byte subject; the check needs a floor on the tier's effectiveness and a spans comparison). STEP 3 (next, before any fast-size tuning): the ESCALATION RATE over exemplar subject files via the `-DRX_TEST_TIER_HOOK` counter — the bet's number; capture-heavy patterns (>~145 slots) get no tier and the FAST=16 cutoff has no measured win (r38 note 6); a `--fast-tier=N` knob is the general lever if the number says the default is wrong. STEP 4 CANDIDATE (Frank's question, 2026-08-25 ~22:3x: "could the boundary be predicted?"): YES, statically — frames pushed ≤ subject length × the pattern's worst-case frames-per-byte, a coefficient the emitter can derive from the pattern's structure (the recursion specimen's ~2 frames + ~9 trail per nesting level is the measured instance). Two stamped per-artifact thresholds: `RX_FAST_SAFE_LEN = FAST / k_max` (a subject at or below it CANNOT overflow — the fast attempt is riskless) and `RX_FAST_HOPELESS_LEN = FAST / k_min` (above it the fast attempt is wasted — go straight to the deep path); the band between stays the bet; k_min = 0 degrades to today's behaviour. Zero runtime state (§5.3 forbids a dynamic guess inside the artifact; the caller can hold one and choose `_in`). RULED IN SPIRIT (Frank, ~22:4x): the guess "doesn't have to be 100 %" — a wrong guess never changes an answer, only its cost, and both wrong directions are bounded (deep-on-shallow: one probe loop, ~190 ns; fast-on-deep: the double run, ~1.5×), so the OBJECTIVE is the EXPECTED cost over the subject distribution: one per-pattern rule of thumb (a length threshold from the pattern's typical frames-per-byte, or tuned on the exemplar file) may beat both pure strategies; "if a user is really concerned, they should allocate themselves" (`_in`). BUILD ONLY IF STEP 3's escalation rate says the middle band matters (D77). Alternatives measured/considered: shrinking the stamped default (trades D73's depth ceiling for speed — not general); `no_stack_clash_protection` per entry (a hardening opt-out on emitted code — a posture decision, Frank's, and the attribute's existence in gcc is unverified). It is an emitter change (scaffolding: abi bump + re-pin per D76; the VM program region unchanged) — one opus lane with a design note and a D6 critic, AFTER srStamp lands (both touch entry emission). Original charter follows) — THE LOOP'S FIRST OUTLIER (pcrec-bench O-4,
  2026-08-25 ~14:3x, report reports/2026-08-25-email-specimen-0.1-budu-
  ryzen1600-repin-692c2e8.md, bench 0cf336c): at the SAME pin 692c2e8,
  `pcrec-vm-in` (the `_in` entry with a once-touched 2.75 MiB caller
  buffer) is FASTER than `pcrec-vm` (the un-suffixed entry, stamped
  default 2048/3072) on EVERY regime — orig/short-search 12,546 vs
  28,997 ns/call (2.3×), orig/compliance 62,732 vs 80,228,
  factored/short-search 54,118 vs 69,538. So the un-suffixed VM entries
  pay a PER-CALL cost the `_in` path does not, of the order of 16 µs on
  a ~256 B subject — larger than the whole match. General: every
  VM-selected pattern (backrefs, lookaround, linked recursion — sub-bench
  3's whole population) pays it on every call through the default entry.
  CANDIDATE CAUSES, each one measurement: (a) the 98-131 KB run struct on
  the C stack — gcc's stack-clash protection probes every page of a large
  frame (~24-32 page touches per call) — measure with
  `-fno-stack-clash-protection` and `-fstack-usage`; (b) zeroing or
  initialising the frames/trail arrays per call (`rx_run_state_bind`, any
  memset/`= {0}` on the run struct) — read the emitted entry, count bytes
  written before the first instruction of the match; (c) the first-touch
  page faults of a fresh 131 KB stack region on each call when the stack
  has been unwound past it (the `_in` buffer is touched once and stays
  resident) — `perf stat -e page-faults` on both entries; (d) the trail
  and frame layout (40 B vs 24 B frames — the bench's factored form is
  SPLICED, frame 24, so this is not the linked-call widening). STEP 1 is
  a MEASUREMENT lane (sonnet; no design): reproduce the 2.3× with the
  bench's `quick` or a driver in tests/bench/, then attribute it across
  (a)-(d) with one control each. STEP 2 is the general fix, chartered
  from the number — candidates already visible: lazy initialisation (no
  byte of a frame is written before it is used), a smaller stamped
  default with the `_in` path documented as the depth remedy (D73 kept
  the number; a per-call cost is a NEW input D73 did not have), or
  emitting the default entries as thin wrappers over `_in` with a
  static-thread-local... NO — allocation and thread-locals are forbidden
  by §5.3's contract; the fix must stay on the stack or in the caller's
  buffer. Identity gate: the `_in` entries and every answer byte-identical
  across the fix; the bench row (O-4) is the exercising case (D79 item 4).
  Queued behind [DD-13]'s stamps; the first optimization lane of the loop.

- [OPT-2] STATE:completed (CLOSED 2026-08-29 ~05:4x INTO [ENG-ABS]: the unwrapped-forward match-here it measured as the lever is BUILT and battery-proven on 808740c — matching subjects 1.031× the VM (target ≤ 1.046×, from 2.077×), the 35 short valid emails 0.482× (target ≤ 0.571×, from 1.207×), the failing 1 MB probe 363,305× cheaper; nothing else was owed on this row) — formerly STATE:started (STEP 2 MEASURED 2026-08-28 ~13:5x, lane opt2m, docs/dev/opt2_anchored_match_measurement.md, merged 5c2fdf4 — nothing under src/: THE STEP-1 LEAD IS REFUTED TOO — `rx_match` on the plain `orig` DFA vs the `(?:orig)\z` DFA over the bench's 85 compliance subjects differs by 3.7 % on the set, 3.3 % on the 40 matching subjects (one predictable `scan_position == subject_length` branch per byte + a restructured accept check), not 3.7×; on a `match`-regime subject the plain form scans to the end too, because the subject IS the match. WHAT THE 2× IS (the DFA-vs-VM gap reproduced in-tree at 2.133× set-grain, = the bench's 2.153× re-pin, so [OPT-3] STEP 2 already halved the 692c2e8-era 3.7×): THE REVERSE PASS — a cost-isolation patch (scratch, timing-only, answer-incorrect by construction) that deletes the reverse scan takes matching subjects from 2.077× behind the VM to 1.046× (parity) and the 35 ordinary short valid emails from 1.207× behind to 0.571× (43 % AHEAD); ~50 % of DFA cost on every matching split, 13.9 % on non-matching. MANAGER'S READING CORRECTION on the doc's "a value `rx_match` never needs": with the WRAPPED (self-looping) forward machine an accept can belong to a LATER start, and the reverse pass is what lets `rx_match` reject those — the start is unneeded only when the machine is UNWRAPPED and run from `ctx->pos`, which is exactly lever (a). THE LEVER, ranked by the lane: (a) [ENG-ABS]'s already-recorded second mechanism — anchored match-here via the unwrapped forward DFA from `ctx->pos`, no reverse pass, no candidate skip; NUMBER TO BEAT: the isolation understates it (it still pays the self-loop/skip machinery), so at/below VM on matching subjects, ~0.57× on short ones — this is [ENG-ABS]'s second forcing measurement and its gate is now MET by the numbers; (b) the `\z` view cost folds into [DD-13](b)'s general fold (3-5 %, not its own charter); (c) reverse dead-state exit — moot, the reverse loop already has it. NEXT: [OPT-2] closes into [ENG-ABS]'s unwrapped-forward mechanism when Frank opens it; nothing else is owed on this row. STEP 1 MEASURED 2026-08-25 ~19:3x, lane srOpt1: the dead-state-exit hypothesis is REFUTED for the fail path — anchored `\z` and plain DFA forms cost the same on failing subjects at every length (fail-first ≈0.35 ns/B, a table lookup per byte; fail-late ≈3.3 ns/B, a transition per byte; both ~linear, within 10 %). WHAT THE EMITTED C SAYS: a DFA artifact's `rx_match` (orig_anch_dfa.c:703-711) runs the UNANCHORED `rx_search` and filters `caps[0][0] != ctx->pos` afterwards — the [ENG-ABS] shape — so an anchored match scans for LATER starts it will then reject, and the `\z` end-view only changes acceptance at `scan_position == subject_length`. NEXT MEASUREMENT (the lane's lead, unmeasured): on MATCHING subjects the plain form exits at its last-accept while the `\z` form must scan to the end — likely the 3.7×; measure on the bench's 85 compliance subjects split matching/non-matching. THE GENERAL FIX is a TRUE ANCHORED DFA ENTRY — start at `pos`, stop at the dead state, never scan for later starts — which is [ENG-ABS]'s charter arriving through the loop (D79 item 4). Original charter follows) — THE LOOP'S SECOND OUTLIER (from the manager's
  O-5 reading of the same re-pin report, 2026-08-25 ~14:4x): on orig /
  match-compliance (85 whole-subject cells, 10-1000 B), the DFA
  `(?:P)\z` artifact costs 234,114 ns per set vs 62,732 for the VM form at
  the same pin — 3.7× SLOWER, ~2.7 µs vs ~0.7 µs per subject — far more
  than [DD-13](b)'s last-byte skip cost can explain. HYPOTHESIS to
  measure first: the anchored DFA match scans to the END of every
  non-matching subject instead of stopping at its dead state (a
  table-DFA in a dead state has no way out; the VM fails at the first
  mismatch). MEASUREMENT: emit the `\z` form of orig, run the anchored
  entry on a non-matching 1,000 B subject vs a 100 B one — if cost
  scales with length past the first mismatch, the dead-state exit is
  missing (or `\z`'s end-view state prevents it); read the emitted match
  loop for the dead-state test. If confirmed, the GENERAL fix (dead-state
  early exit in the anchored DFA loop, or the end-view fold [DD-13](b))
  benefits every anchored DFA match, not the bench. Needs the per-subject
  pass/fail split from the bench (requested via O-5 interpretation item)
  to model the cost. Queued with [OPT-1]; one measurement lane can take
  both (same driver, same box-quiet requirement).

- [ENG-FORM] STATE:completed (MERGED 2026-08-26 ~20:2x, lane srForm; abi 8; emit_unanchored 459/57/5 → 52/4/2, 14 form booleans → 0, a new representation = one object + one accessor block; objdump equality per loop, timing within spread; journal part 9; battery #3 owed on the combined tree) — THE EMITTER'S FORM AS A VALUE, DECISIONS AS SELECTION (Frank + manager, 2026-08-26 ~14:5x-15:0x, forty-first session; D82). Measured need: emit_dfa.c's two big functions carry the axes — emit_unanchored 459 lines / 57 ifs / nesting 7, emit_attempt 447 / 47 / 5 — with the form held as ~14 loose booleans, every one in a forward/reverse PAIR, and every new axis landing twice in the same function ([OPT-3] STEP 2 added ~20 branch sites). SHAPE, two layers: LAYER 1 (emitter) — `DfaForm` derived ONCE per machine by selecting, for each axis with ≥ 2 real forms (table representation: premultiplied-u16 / indexed-i16 / later u32, two-byte; prefilter kind; view handling; seed), the FIRST APPLICABLE object from an explicit preference list of representation objects `{name, applies(), emit_block()}` with an always-applicable fallback; the stamp = the chosen object's name (one derivation, two readers becomes structural); the deny flag = a filter on the candidate list; interactions (the un-multiply at emit_view_select) = a method on the object that owns the representation; the forward/reverse duplication collapses to one path called twice. LAYER 2 (emitted C) — an OPAQUE state token (`typedef` + `static inline` step / dead / accept / index accessors, one block per machine per form) so the loop SKELETON is emitted ONCE, form-independent, and the VM hybrid's inlined prefilter gets the same block by construction; a new representation is a new object + block, never a new if in the assembly. GUARDS: answer identity over the corpus + the bench's 91 subjects; the hot loop's objdump instruction sequence EQUAL to today's hand-written form (D82 bound 1 — always_inline first remedy); the timing driver (tests/bench/fdriver.c) within spread on t-a/t-b/t-c; the loop text moves ONCE (abi bump, four sites, gate re-pin); run_premul_table.sh §4 reads the typedef line instead of hunting the loop; sabotage anchors on loop lines re-anchored once and proved to detect solo. SCOPE: emit_dfa.c first; then MEASURE emit_vm.c (9,747 lines) the same way before deciding. SEQUENCE: after [OPT-3] STEP 2 merges, BEFORE [OPT-5] and STEP 3 (so those land as accessor-block entries). Opus (engine code); design note before code, D6 panel at close. No framework for its own sake (D75 addendum): a one-site boolean stays a boolean.

- [OPT-4.1] STATE:completed (BATTERY-PROVEN 2026-08-30 22:20, battery 5 on cdaae0b + the guard fix eefb228 — san re-run 36 scripts / 0 reports / 108 min; mech 203 rows clean; registry solo 83/rc 0; the pin is the part-11 journal commit; MERGED 2026-08-30 18:1x — every Phase 2 item green (corpus 26,680/0; scoped axes pair 22,114/22,114 ×2, 0 mismatches; S206/S207 DETECTED as a mutually-reading pair; the eleven bench points 11/11 as predicted; r47sel's must-fix fixed and pair-checked); BATTERY 5 pending — battery-proven flips this row to completed and the pin moves; CHARTERED 2026-08-30 14:3x, forty-sixth session, on Frank's "1-2 opt4/5 agree" — the OPTIMIZATION column's row AHEAD of [OPT-5]: a correction to a shipped default with a MEASURED loss beats a new row; lane opt41, opus, worktree worktrees/opt41, coding under a .lift hold while battery 4 + w11f's stage B own the box) — GATE THE COUNT-COLLAPSED PREFILTER RESCUE ON NON-NULLABILITY. Bench O-10 (abi-12 AFTER at 96e44c2, docs/dev/ledgers/2026-08-30-abi12-after-96e44c2.md there): ruling B's rescue is the largest gain the bench has measured where structure survives the collapse (ctx band 2.2-3.1×; loglines level-context ×4.60, 13.44× → 2.92× behind the JIT; the rescued fallback beats `--engine=vm` 2.2-4.6× because the forced VM has no prefilter) and a LOSS where the collapsed language is NULLABLE: `[a-z]{0,32768}` → `[a-z]*` admits a zero-length match at every position and can never dismiss — search ×3.57 slower, throughput 1.88 → 6.90 ns/B, t-digits-016k ×1.65 slower, the four letter runs ×3.9-6.0; three of the bench's patterns lose 1.2-9.9×, five win, and the rung cannot tell them apart. THE FIX IS ONE PREDICATE: do not build the collapsed prefilter when the collapsed language is nullable (equivalently, when nothing outside the collapsed repeat survives) — decline the rescue, stamp WHY (a new `_VM_PREFILTER_LANG_WHY` value naming nullability; a value, not scaffolding — no abi bump, D76; D80 spec hunk in tuning.md/limits.md §3.3). NOTE FOR THE LANE: the K39/[OPT-4] check witnesses (`[a-z]{0,4000}`-shaped pairs in tests/codegen/run_prefilter_collapse.sh and run_ir_listing.sh) are THEMSELVES the nullable shape — their expectation flips from `count-collapsed` to `declined`; the checks need a non-nullable twin (e.g. `a[a-z]{0,4000}b`) as the control that still collapses, so both directions are asserted. Acceptance: answer-identical over the corpus (test-axes); the ten labelled O-10 points predicted per pattern BEFORE the bench's AFTER (five keep their win, three lose their loss, two flat); codegen/cli/mech rows green; battery; then a NEW PIN to the bench. Also answers O-10 ask (iv) on the way (`RX_DFA_PREFILTER "none"` beside `vm_prefilter=hybrid` — intended or unpopulated; state it). CROSS-NOTE 2026-09-19 (lane dd8's listing-reach census, dd8_report.md §4.3): the `no-nullable-collapsed` decline (`prefilter_declined_nullable`, the RUNG-scoped decline) is reached by NO input over 10,640 listings across seven flag axes plus three hand-built witnesses — structurally, [OPT-4.2]'s `prefilter_declined_nullable_default` fires first at the ordinary hybrid on every nullable pattern, and count-collapse (`X{m,n}` → `X{min(m,1),}`) cannot make a non-nullable language nullable, so `collapse_reason != CR_NONE` and nullability never coincide. A live arm of a shipped diagnostic that cannot print; pre-existing, not dd8's. Disposition open (delete the arm, or find the input that reaches it); owner: this row.

- [OPT-EDGE] STATE:completed (CLOSED 2026-09-21 seventy-fifth session, D117: I-82/O-43 at 89d986c3 on the edgefix-fixed harness — 0 of 16 floor cells separate under D77, PCREC_MIN_SCAN_CHAIN stays 2, the m=2 bimodality named as box-side noise (the moving binary flips between runs, mode-match 50%), the ladder's before−after cost 1.00/0.57/0.22/0.24 ns/byte at k=1..4 recorded; logs studies/scan_edge_ladder/runs/2026-09-21-i82-89d986c3/, analysis docs/dev/lanes/edgefit_report.md; close-out LANDED by lane edgeclose 4e8e09e5: tuning.md §2.18 + limits.def:371 re-confirmation sentences (limits_check.sh's NAME list the only pin, unaffected; sweep stream 5 moves by that one row), the m5_stage1_stamps.tsv manifest re-recorded for abi 28 (12 EMITTED_BYTES rows +11, nothing else), study README Runs note, five lanes/CLAUDE.md lines; cpset-structure 28/28, registry 631/0, codegen 9/10, anchors 286/286) — formerly **RESUMED 2026-09-21 (Frank: "agree on sequencing, proceed"; the FIRST of D113 step 1's finish rows to run): **REROUTED ~10:0x: lane edge3 stopped before measuring — the box read load1 1.0-1.4 against the runbook's 0.5 refusal, and the harness is Linux-only (taskset, /proc idle); the measurement is EXECUTOR ITEM I-81 on ubuntubudu (pcrec-bench inbox, two floor runs + the ladder at main 476892de), slot asked; a fresh Mac lane applies the decision from the returned tables.** Originally: lane `edge3` (sonnet, worktrees/edge3) — the m=2 floor cell re-measured on a quiet box with its neighbours, the a+b·k entry-cost fit from the ladder by branch-vs-main isolation (studies/scan_edge_ladder/), PCREC_MIN_SCAN_CHAIN re-chosen ONLY inside a measured gap (D77) with its tuning.md hunk; else recorded as measured-no-gap and the row closes.** (LANE B `edge1` LAUNCHED 2026-09-03 ~17:05 EDT, fifty-first session: opus, worktree worktrees/edge1, branch lane/edge1, write-only under tonight's `.hold` — STEP 1 = the shared-sentinel dispatch + K43 direction (b); suites, LINTGEN and the measurement ladder after `.lift`) — formerly STATE:not-started (CHARTERED 2026-09-02, Frank's ruling, fiftieth session; OPTIMIZATION column, an [OPT-5] STEP 1 follow-up). THE SCAN EDGE'S ENTRY COST: O-14 measured the edge worth ≤ 0.2 ns at every k on the match axis while costing +2,037 B and ×1.03-1.09 on loglines' three edge-taking patterns (iso-ts/http-5xx/ipv6), with no cell where it PAYS in the window; the STEP 1 acceptance (letters ×2.71-3.03) is where it pays. MECHANISM (read 2026-09-02, emit_dfa.c emit_scan_loop/emit_scan_edge): every edge is its OWN `if (state == HEAD && more && class_test)` block on the loop's generic path, so the per-iteration cost is ONE COMPARE PER EDGE — iso-ts emits 8 edge blocks in rx_search and 4 in rx_match (measured from main), the worst regressor; and precondition (5) `m >= 2` (scanedge.c:330) admits chains of 2-4 that can never scan more than 2-4 bytes. Two levers, both general: (1) Frank's dispatch (2026-09-02): renumber edge heads to the TOP of the state id space and test `state >= FIRST_HEAD` ONCE (a sign test cannot serve — heads must stay valid table rows for the fall-through step; premultiplied cells are monotone so the range test holds on cells) — O(1) in the edge count; (2) a minimum-chain-length floor above 2, a limits.def row. MEASUREMENT FIRST (D77): the bench's `pcrec-auto-noedge` arm (-fno-scan-edge) on loglines is the population's BEFORE; the edge-count census over the corpus + sets says how many artifacts have ≥ 2 edges per loop. QUEUED behind [OPT-5] STEP 2 (same emit_scan_loop region). **SEQUENCING RULED (Frank, 2026-09-02 ~14:5x): the DISPATCH change comes FIRST and the minimum-chain floor is measured AFTER it, against the new loop — with one range compare per iteration the entry cost is no longer per-edge, so the length at which a chain pays changes; a floor measured on today's O(N) loop would be the wrong number. Order: (1) edge-count census + noedge BEFORE; (2) the single-dispatch renumbering, answer-identical, measured on iso-ts/http-5xx/ipv6 and the STEP 1 letters cells; (3) the floor ladder on the new loop.** **REFRAMING TRIGGER (Frank, 2026-09-02 ~15:2x): if the single-dispatch loop pays for some N edges, do NOT add edge KINDS one at a time — reframe as [ENG-ISL]'s 'islands of VM in DFA' (that row now carries the framing): the edge body becomes a VM-emitted island with the head/fall-through splice as the general protocol, one source for the loop shapes both engines use.** **BEFORE SIZED 2026-09-03 (bench O-15, ledger 2026-09-03-altwide-0.2-noedge-ccrerun-1989c62.md §5): the scan-edge counterfactual on iso-ts is ×1.089 at the PINNED tier (pcrec-auto vs pcrec-auto-noedge), replacing the scratch ×1.70 — the row's acceptance is read against 1.089, and the loglines family's total cost is that order, not larger.** **DESIGN REFINED (Frank, 2026-09-03 ~10:5x: "even a single if compare costs in the hot loop; negatives often don't pay because the sign bit is set by the previous instruction"): the hot loop ALREADY pays one sentinel test per iteration — emit_scan_loop's closing `if (<p>_is_dead(state)) break;` — so the general form is to make edge heads share THAT test: reserve the negative (or otherwise sentinel) state range for NON-STATES = dead ∪ edge-head, keep the table's fall-through/indexing valid by biasing the table base so negative offsets index (premultiplied cells stay monotone), and branch from the one existing test to a dispatcher that distinguishes dead from which-edge only when the sentinel fires. Zero compares added to the generic path (vs today's one `if` per edge, and vs the interim 'one range compare' idea, which still adds a cmp+jcc). x86 note: a table LOAD sets no flags, so a bare sign test still costs a `test`; but `test/js` and `cmp/jae` both macro-fuse to one µop, so the win is not the fused compare, it is folding the edge test into the dead test the loop already has. Consistent with the bench's SUBLINEAR edge cost (8 edges ≈ ×2.8 of one — the compares sit off the 7-cycle load-latency chain and mostly hide; the residual is fixed per edge-taking artifact: loop-body size/layout/µop-cache), which is what STEP 1's measurement must split before the floor is chosen: (1) fixed-per-artifact vs per-edge cost from the noedge pair + a 1-edge/2-edge/8-edge ladder; (2) the shared-sentinel dispatch; (3) the minimum-chain floor on the new loop.** **RULED (Frank, 2026-09-03 ~11:2x): the shared-sentinel form IS the mechanism — dead ∪ edge-head in one reserved range, tested by the loop's existing dead check, "to make the whole thing cost nothing"; the range-compare interim is dropped.** **STEP 1 VALIDATED 2026-09-03 23:3x EDT (lane edge1): test-axes 21/21 answer-identical (22,309 keys each, 0 mismatches; PC-4 live-libpcre2 cross-checks 0-failure; 3,267 s at PROCS=6 after a PROCS=3 launch tracking to ~94 min was killed by PID and relaunched — 31 min lost, a run saved); test-registry 101,244/0; test-codegen 4/5 with only [ART-SIZE]'s §9 bar (K43's +578 B; inherits isl1's pool at merge). K43 (b) DROPPED from the branch (refuted: see K43). CENSUS of precondition (8), by the emitted [OPT-5] SCAN EDGE markers, main vs branch over 2,539 artifacts compiled by both: 11 moved (0.43%), 10 to zero, ALL eleven \b/\B patterns, none without a seed table (the bound holds exactly), the loglines family untouched — and only 2 of the 11 carry the hazard (8) guards (offset-set prefilters with reseed sites); the other 9 have byte-class or memchr prefilters that advance the position but never WRITE the state variable. STEP 1.1 FILED: narrow (8) to "seed AND a reseeding prefilter" by giving src/opt/scanedge.c the start analysis (the pass runs before axis B is chosen and has already deleted the chain's interior states, so the emitter cannot filter later) — D77 trigger measured: 9 corpus artifacts, all \b-family, regain their edge. The draft SCC check stays a documented draft outside every make target (one bounded attempt: measures all four witnesses but reads an impossible 13-node SCC on iso-ts's control — a CFG/SCC bug, recorded in the file's §6).** **ACCEPTANCE MET 2026-09-03 23:5x EDT (edge1, quiet box load1 0.49-0.56, taskset-pinned, arms interleaved per round, 15 rounds × 10 sweeps, 256 KB of near-miss `NNNN-NN-NNX ` fields so the digit chain is entered and left without a match — on the bench's own syslog subject the loop reads 0.22 ns/byte because the prefilter dismisses nearly every position and an entry cost is invisible): main/noedge ×1.0937 (the bench's ×1.089 counterfactual REPRODUCED by this instrument — what licenses the next row), branch/noedge ×0.9995 (the edge now costs the loop nothing), branch/main ×0.9173. The citable number stays the bench's at the pinned tier. OWED: the 1/2/3/4 ladder — built and run but its DESIGN was wrong: subtracting the -fno-scan-edge arm does not isolate the entry cost because that arm is a DIFFERENT MACHINE (chain interiors not deleted), so the difference carries the scan collapse's own per-byte win (entry cost read negative at every rung); the isolation that works is branch vs main on the same machine (every rung faster: 0.711/0.811/0.693/0.876, not monotone in k, and the box had drifted to load 0.84-1.01) — re-run on a quiet box with subjects that engage each rung's pattern; the minimum-chain floor not reached; PCREC_MAX_SCAN_EDGES stays documented-not-rechosen until then. K43 (b) dropped (the third ruling reached the lane).** **STEP 1 MERGED 2026-09-04 06:1x as 386abf94 (abi 19; chain green first time). OWED: the 1/2/3/4 ladder by branch-vs-main isolation and the minimum-chain floor (PCREC_MAX_SCAN_EDGES documented-not-rechosen until then); STEP 1.1 (narrow precondition (8)); (A) of the identity gate untested (opt-in gate).** **NEXT WAVE (Frank, 2026-09-04 08:4x): lane B′ = STEP 1.1 (narrow (8)) + the owed 1/2/3/4 ladder by branch-vs-main isolation + the minimum-chain floor, quiet box.** **STEP 1.1 STARTED 2026-09-04 10:5x EDT — lane B′ `edge2` (opus, worktrees/edge2): narrow (8) to "seed AND a reseeding prefilter" by a general mechanism (the prefilter form decided before the pass, or the pass moved after axis B — measured), the census as an enumerated-manifest check, a hazard POSITIVE CONTROL (a scratch build with (8) removed must misbehave), then post-lift the ladder by branch-vs-main isolation and the minimum-chain floor as a limits.def knee.** **STEP 1.1 MERGED 2026-09-04 16:5x (81ef3044; abi 20→21 at 219875ee; FILEPIN 219875ee; lane edge2 + edge2b's §9 transcription): precondition (8) guards two hazards (seed AND the prefilter reseeds, read-back check); the entry-seed dispatch generalised to is_stop && !is_dead (lost-match witness foo\B on xfoofoox); the per-machine census check (11 named artifacts regain an edge); S227 mech row (its harness-arm figure owed to the next battery); studies/scan_edge_ladder/ measured — ladder step11/after ≈ 0.99-1.01 at all four rungs (IQR 0.01-0.04, 39 pooled rounds/rung); the floor PCREC_MIN_SCAN_CHAIN = 2 (limits.def row, tuning.md): m = 3/4/8 no gap, the m = 2 cell UNSTABLE (median 1.78, IQR 0.87, bimodal) — re-measurement OWED, the spec says so; the entry-cost a+b·k fit still owed. Suites on the lane tip: make test 44 sections 0 failed (codegen 6/6 embedded), registry 597/0; axes covered by the union chain. Process: the lane launched test-axes THREE times against ruling 7/8 (killed by PID each time, then TaskStop) — a busy lane reads neither messages nor its rulings file mid-run; the report was finished by a fresh sonnet agent from the artifacts.** **HARNESS TRIAGED 2026-09-21 (lane edgefix, sonnet, worktrees/edgefix): O-42's ubuntubudu run at eaab0d4a found the ladder producing NO FIT (every arm COMPILE FAILED, rc=0 anyway) and the floor stamping "forward edges = 0" on every cell (rc=0 anyway). Two root causes, both in the harness, nothing in src/: (1) `run_ladder.sh`'s ARM[before]/ARM[after] were built from a RELATIVE $OUT before its own `cd` into $OUT/work -- `make ladder` always passes the Makefile's own non-empty `OUT=out` default, so the script's `${OUT:-...}` fallback never fires, and after the cd the two reference-compiler paths resolve one level too deep; ARM[step11]=$PCREC alone escaped because it was already hardened absolute for the identical 2026-09-04 bug. (2) D112 (2026-09-19, abi 26->27) flipped emitted comments OFF by default, and the edge-count census reads the `[OPT-5] SCAN EDGE` comment marker -- the floor's census reads $PCREC's OWN artifact (no old-reference stand-in), so it now reads 0 unconditionally; the ladder's census reads the OLD `after` reference compiler's artifact (predates D112, always comments), unaffected. Fixed: $OUT absolute-ized in both run scripts; `-fcomments` added to floorcells'/run_floor.sh's `e_` build only (proven byte/behaviour-neutral, D108/emitverb_report.md); a rung/cell that measures nothing now fails the run (rc<>0) instead of exiting 0; run_floor.sh gained the median/IQR summary block the 2026-09-04 report cited (previously hand-computed, never saved). Mac verification (darwin, gcc-16, after the 4c2b06d2 gate cleared): compile+count paths only -- the timing stages need Linux `taskset` and are not portable here. See `docs/dev/lanes/edgefix_report.md` for the full diagnosis, evidence quotes and the exact re-run command block; the m=2 bimodal signature (~0.90-1.00 mixed with ~1.81-1.82 spikes) recorded, not analysed, per the brief.**

- [FORM-CHAR] STATE:completed (STEP 1 BUILT AND MERGED 2026-09-05 overnight session, lane formchar1, opus, merge on main before 05b2fe8a; docs/dev/lanes/formchar1_report.md; the manager's chosen lane under Frank's "one other chosen lane" delegation): object (2) `ascii-fold` shipped — vm_cls_shape, ONE classifier read by vm_cls_test, the bitmap-table emission loop (a latent inline re-spelling of the shape condition retired) and the stamp; a two-member class that is an ASCII fold pair ((lo^hi)==0x20, both letters) emits `(byte|0x20)==lower` and its 32-byte bitmap table is NOT emitted. D82 ritual complete: RX_VM_CLS_FOLDS (family (b) activity count, every VM artifact, 0 spelled), -fno-cls-fold / PCREC_NO_CLS_FOLD bit 24 (cli + --list-axes row altcls-style + strategy_denials mask; the axis joins test-axes with no list edit), tuning.md §2.22 + match_api.md §6.3, abi 22→23 (D94 grep, five readers), the recursion identity gate grew the fold as a SECOND deny-axis IFF with FOLD_PATTERNS manifest, form-census floors D>0:6 / V>0:12 (measured 16/28 at landing), sabotage S228 (recognizer widened — the unsound direction) DETECTED with reach 1/1. VERDICTS: whole-corpus answer identity default-vs-denied 22,488/22,488 agree 0 mismatches + PC-4 live-oracle 0-failure both arms; witness __TEXT 1,072 vs 1,552 denied (-31%), tables deleted; tests/base/cls_fold.rxt 58 python-verified cells incl. one-bit-off constant pins. Objects (4)/(5) utf8-fold stay M5.0 stage-4 territory (enum door left open); `atom`@N≥16 (family D) remains the next candidate contingent on timing; `table` rejected everywhere. Incidental finds: the grep -P mech row-filter macport residual (BSD grep assembled ZERO rows — fixed 8da8e685) and the five inherited darwin test-codegen reds (admin slice, journal).) — formerly STATE:not-started — (FILED 2026-09-03 ~17:0x by Frank: "another 'form' which is character matching — in pattern abc, the 'abc' part. It has two current forms, normal and case insensitive, but it will have utf stuff.") CHARACTER MATCHING AS A D82 AXIS. FACT AT FILING (D23; verified on an emitted `(?i)abc`): caselessness FOLDS AWAY AT PARSE TIME — a caseless literal becomes per-position two-member CLASSES (`'A','a'`), so every downstream literal mechanism ([OPT-VMLIT]'s literal chains, the memchr prefilter's single candidate byte, the M2.8 trie's factoring, [ENG-ISL]'s trie walk, the scan edge's `range` body) sees classes, not a literal — the bench's ci-256 fell to a `bitmap` edge for exactly this reason (two disjoint ranges). THE AXIS: a `char-match` object family with a stamp, deny/force flags and answer identity under D82: (1) `exact` — the byte compare (today's literal); (2) `ascii-fold` — a FOLDED COMPARE that keeps the literal shape (for a letter, `(b | 0x20) == c` is one op; non-letters compare exact), so caseless literals keep chains, memchr-on-either-case-first-byte, trie factoring and the island; (3) `utf8-exact` — a FACT worth stating on the row: identical to `exact` for literals (UTF-8 is self-synchronising; the bytes match iff the code points match — no decode needed); (4) `utf8-simple-fold` — 1:1 code-point folds of varying byte length (a folded compare per code point, decode on the subject side only where the pattern byte is non-ASCII); (5) `utf8-full-fold` — 1:n folds (ß ↔ SS): a small NFA step, the same shape rule 2 gives a class-leading branch. M5.0 (UTF-8, \p{}) then lands as OBJECTS (4)/(5) with stamps, not as special cases inside every consumer — one derivation, every consumer reads the object (the general-mechanisms rule). MEASUREMENT FIRST (D77): the syntax census's `(?i)` cells and the bench's ci-256 (today ×? vs the JIT under folding) are the BEFORE; the STEP 0 hand-twin is `(?i)abc...` as a folded-compare chain vs today's class chain on the ci-256 subjects. Sequencing: after [ENG-ISL] STEP 1 (its trie walk is a consumer) and before M5.0 opens. **NEXT WAVE (Frank, 2026-09-04 08:4x): lane C′ = [FORM-CHAR] STEP 0 with [OPT-CLSPACK] STEP 0 — the class-vs-compare and byte-table-vs-bit-array measurements, both engines; decides [ENG-ISL] STEP 2's class-member expansion.** **STEP 0 STARTED 2026-09-04 10:5x EDT — lane C′ `form0` (sonnet, worktrees/form0, measurement only): hand-twins per test form (two-member class bit array / folded compare / 256-byte table / shared atom table) on the VM chain and the DFA edge (ci-256), sizes now, timing post-lift; docs/dev/form_char_step0.md.** **COMPILER EVIDENCE 2026-09-04 11:1x (manager, on Frank's question "how would load latency affect fold? can it be one branch by or-ing?"): gcc -O2 emits the SAME code for `c=='a'||c=='A'`, `(c=='a')|(c=='A')` and `(c|0x20)=='a'` — `and $-33; cmp $65; sete`, one mask + one compare, no load, no branch (two constants one bit apart collapse to a mask test; every fold pair is such a pair); a non-pair two-member class (`a|z`) becomes cmp/sete/cmp/sete/or, still branchless. So load latency can only hurt the table and bit-array forms against the fold; the "one-load latency could win" question is table vs bit array on GENERAL classes (family B) and the atom table (D), not family A.** **STEP 0 MERGED 2026-09-04 16:58 (c7288a59; lane form0, sonnet; docs/dev/form_char_step0.md + studies/form_char_twins/; measurement only, nothing under src/): SIZE — the folded compare wins the VM caseless chain (family A closed by compiler evidence: gcc folds all three fold-pair spellings to and/cmp/sete, no load; asm committed), the 256-B table loses on size everywhere, the atom table wins at N=16; TIMING (quiet box, 11 rounds, load1 < 0.5 gated, 132 cells, 0 checksum mismatches) — B/general a wash (base 9.74 / table 9.38 / rangecmp 9.16 ns/call, within 6%); B/sparse rangecmp LOSES (36.2 vs table 31.5, +15%) despite the smallest .text — a size-only prediction overturned; C/small a wash (0.8%); D/n16 table 875 and atom 885 tie and both beat the bit array 1,147 by ~24% — atom graduates to supported on size AND time. OWED (§8.4): ci-256/nonpair timing for C, CPU pinning (taskset), a disassembly read of D's atom mechanism, the subject generator as a script. The recommendation STEP 0 can support: build `fold` (family A) on its own merits; `atom` at N≥16 (family D) second; `table` nowhere.**

- [OPT-DIAL] STATE:completed (CLOSED 2026-09-19, seventy-first session, per docs/dev/plan_audit_2026-09-19.md: delivered, tag stale — Frank\'s ruling on the audit) — formerly STATE:started (FILED 2026-09-03 21:2x EDT by Frank, fifty-first session, on the [CC-DIFF] STEP 2 inline ladder: "It can be switched. We should have a method of indicating the relative desire of speed vs size. Say there was a dial of N which indicated max speed vs min size then these switches could be set as a group depending on the dial setting." OPTIMIZATION column, a D82 META-axis.) THE SPEED-vs-SIZE DIAL: one option (spelling is the manager's; `--tune=N` or an `-O`-family letter, and a `tune` line in an .rxt config block per D93) whose value N on a small ordinal scale (min size … today's defaults … max speed) sets a GROUP of existing switches from a POLICY TABLE — one row per switch, one column per dial value — instead of each switch carrying a default chosen alone at its own landing. Explicit per-switch flags override the dial (explicit beats profile, as D93 file-wins beats the command line). The dial value is STAMPED (`RX_TUNE` or per D82's naming) so an artifact says which profile built it, and ANSWER IDENTITY across every dial value is the acceptance — the test-axes shape applies unchanged, so the dial is testable the day it exists. WHAT IS ON THE DIAL is only what has a MEASURED exchange rate (time × bytes × gcc time): today's first entry is [CC-DIFF] STEP 2's inline ladder (16-23% run time bought at ×2.6→×6.5 .text and ×2.9→×6.6 gcc from w-8 to w-256); candidates with ledgers to read: [ART-SIZE]'s materiality bar (75%) and its K choice, `--unroll=K`, the DFA cell/table representations (premultiplied; bitmap vs 256-byte table — [OPT-CLSPACK] STEP 0), prefilter collapse, the emitted-size caps themselves at the size end; NOT on the dial: switches that are pure wins on both axes (the alternation island: smaller AND faster) and switches with no measured trade. STEP 0 (D77): the INVENTORY — every switch's measured exchange rate from the ledgers we already have (the inline ladder, the K ladder, the bench's per-flag cells), the draft policy table with the numbers in it, and the explicit list of switches the dial may NOT touch until measured. STEP 1: the option, the policy table, the stamp, the spec (tuning.md §1 gains the profile concept; every §2 entry gains its policy row), the axes sweep over the dial. Sequenced with [CC-DIFF] STEP 2 (the size term is the first switch the dial sets). **STEP 0 STARTED 2026-09-04 10:5x EDT in lane ccd2: docs/design/opt_dial_inventory.md — every switch's measured exchange rate from existing ledgers, pure wins / measured trades / unmeasured, the draft policy table, the spelling alternatives for the manager.** **STEP 0 DELIVERED (ccd2, 11:2x): docs/design/opt_dial_inventory.md — 4 of 21 switches carry a two-axis measured rate, 2 are pure wins, 15 UNMEASURED (nearly always on size). RULED for STEP 1 (manager, on the lane's recommendation): spelling `--tune=size|balanced|speed`, a `tune <name>` config line (D93), a `<PREFIX>_TUNE` token stamp (a closed token set extends without renumbering); the POLICY TABLE IS AN ALLOWLIST — the dial can never set a switch without a measured rate; `--vm-entry-shape` is its first native rung and stays as the explicit override.** **STEP 0 MERGED 2026-09-04 17:0x with [CC-DIFF] STEP 2 (584b4db7): the dial inventory docs/design/opt_dial_inventory.md; STEP 1's spelling `--tune=size|balanced|speed` + the ALLOWLIST rule stand as ruled; the ladder's rate table (forward vs inline per program size) is STEP 1's first two-axis input.** **OPEN FOR FRANK (from ccd2's ladder, 2026-09-04): the cells just above the term (prog 5,183 / 5,985 / 6,954) are the cheapest speed wins in the table at 0.061-0.067 B per ns/call saved (5× better than the next cell up) — so `--tune=speed` should RAISE VM_INLINE_CHAIN_MAX_BYTES into 8-13 kB rather than remove it, and the question is whether the DEFAULT may rise too (a size-sensitive build with no flag would grow). Manager's recommendation: keep the default at 4,096 (the row's contract is "forward only where it costs nothing") and make the raise the speed profile's first measured setting in STEP 1.** **RULED (Frank, 2026-09-04 evening, fifty-third session): KEEP THE DEFAULTS — the entry-shape term's default stays 4,096 and the raise belongs to `--tune=speed`; his framing: "the dial is a theoretical at this point and will look better with more options" (STEP 1 gains value as more measured rates join the allowlist). The OPEN-FOR-FRANK above is discharged; STEP 1 remains chartered-not-started.** **DIRECTION (Frank, 2026-09-06 evening, fifty-sixth session, on the [FORM-CHAR2] cls-fold discussion — "we'll wait to decide" the fold itself, but the frame is set): THE DIAL HAS FIVE SETTINGS — default middle, TWO notches toward size, TWO toward speed (supersedes STEP 0's three-name spelling; the manager respells the option at STEP 1 — a 5-point ordinal, names TBD). AND THE POLICY TABLE'S ROWS ARE ASSIGNED BY A THRESHOLD RULE-SHAPE, not hand-placed: a switch whose measured trade is "performance penalty under x% AND size savings over y%" becomes a TIER-ONE size-notch option (the first notch toward size); the EXTREME size notch takes "savings above y% AND penalty under some LARGER bound". x/y and the speed-side mirror are unruled — the rule FORM is the direction. Worked example per Frank: cls-fold at its current numbers (−20% code/−32% .so vs ~3-10% match-tier penalty on one witness) would sit ONE notch toward size, i.e. default-middle would NOT apply it — which is why the fold-default ruling waits on [FORM-CHAR2]'s instruction counts: they decide which side of x% the penalty really sits. [SEL-SIZE]'s auto-decline question lands in the same table (a size-notch selection behaviour), not as its own special case.** **ADDENDUM (Frank, same evening): THE DEFAULT-MIDDLE PRINCIPLE — the middle setting applies only optimizations that are near-free on the axis they spend: a speed optimization that "does not cost much in size", or a size optimization inside an even TIGHTER performance window (the middle's windows are narrower than notch one's, and asymmetric — size pays a stricter performance bar at the middle than speed pays a size bar; numbers unruled). FIRST PROVISIONAL PLACEMENT: the always_inline entry-chain ladder ([CC-DIFF] STEP 2's `inline` rung, 16-23% run time at ×2.6→×6.5 .text) belongs ONE NOTCH TOWARD SPEED — it "increases size dramatically", so the middle doesn't take it. Consistent with the 2026-09-04 ruling as already landed: the default keeps the 4,096 entry-shape term (rung `forward`, measured near-free — inline's object-code properties at 0.50-0.61× its .text) and the raise into 8-13 kB belongs to the speed profile; that ruling is this principle's existing instance, now generalized.** **STEP 1 OPENED (Frank, 2026-09-16, sixty-sixth session: "Let's do #1, followed by #2" — OPT-DIAL design now, [CLS-TREE] design note after): the design lane charters off tonight's merged [OPT-DIAL] §7 size sweep (docs/dev/optdial_size_sweep.md, merge 876b1a89) — the inventory §3 revision (four newly defensible rows; -fno-anchored-dfa's 43%-reach reframing) plus the STEP 1 design note: the five-setting ordinal's spelling, the threshold rule-shape with PROPOSED x/y values derived from the measured rates (Frank rules the numbers), lambda's role as the dial's internal currency (cls_tree_study's own derived knob — the seam the [CLS-TREE] design note will consume), the allowlist policy table across all five settings, the stamp, the answer-identity acceptance, the spec plan. D6 panel after the note; implementation gated on the panel + Frank's x/y ratification.** **STEP 1 DESIGN DELIVERED, PANELED (r60), FIXED AND MERGED 2026-09-17 (lane dialdesign rev 1 -> three-critic panel docs/dev/reviews/2026-09-17-r60-opt-dial-design.md, 6 blockers/16 must-fix, the lambda apparatus and ~25 numbers verified exact -> lane dialfix rev 2, all findings worked + one measured pushback ADOPTED-ANYWAY on B2's unit-mismatched premise): docs/design/opt_dial_design.md + opt_dial_inventory.md rev 2.1. The design's shape after the panel: per-regime units with phi = (phi_scan, phi_entry, phi_cls) named; lambda per position = a SELECTION over the study's swept frontier (manager ruling, general-mechanisms); FOUR distinct first-build positions (+2 ships declared-vacuous, S219 precedent); anchored-dfa admitted at its WORST measured population (gate 6) and OUT of -2 at x2=2.00 (returns iff x2 >= 2.114). FRANK QUEUE OPEN, Q1-Q8 in the note's §9 — Q1 phi is THE BLOCKING MEASUREMENT (chartered before implementation); Q2 x2-as-a-number with its proxy rider; Q2b the middle's ratio + the t_mid-vs-cls-fold run (needed BEFORE [CLS-TREE] lands); Q7 the deny-only force-pair question. IMPLEMENTATION GATED on phi + the rulings.** **REV 3 (D103 governance) MERGED f7c985be; FIRST-BUILD TABLE RATIFIED (Frank, 2026-09-16 late evening, D103 addendum — with the art-over-science placement philosophy recorded verbatim); Q6/Q7/Q8 RULED (file-wins + D93 addendum; spec-narrowed override property; solo battery). NOTHING OPEN. IMPLEMENTATION CHARTERED same hour (lane dialimpl, opus): --tune + config line + pinned table + stamp + abi 25->26 ritual + spec hunks + the §6 check suite; solo battery on ubuntubudu after bench's box release.**

- [CC-DIFF] STATE:completed (CLOSED 2026-09-19, seventy-first session, per docs/dev/plan_audit_2026-09-19.md: delivered, tag stale — Frank\'s ruling on the audit) — formerly STATE:started (CHARTERED 2026-09-02 ~17:5x by Frank, fiftieth session; a BOUNDED investigation, admin/optimization: "I would be interested in some investigation of where clang is optimizing better for purposes of considering making the same move in emitted code to make it more general. I don't want to go too deep down the asm optimization path (there be dragons) but there might be some low hanging fruit." RULING WITH IT: the bench's timed clang arms leave the regular nightly — clang stays a COMPILE-ONLY GATE on every pin (the refusal set must stay empty) and timed clang re-runs periodically / on demand at emission-model changes ([ENG-DIRECT], the frameless stamp, K24). THE TARGETS (bench ledger §5.2-5.4, clang ÷ gcc): cls-upto-4 / throughput / auto **0.407**; floor / match / auto **0.432**; dig-upto-16 / throughput / vm **0.378**; stack-frame / search / vm 0.680; and the forced-VM large-subject-throughput MEDIAN 0.599 over 43 cells (a general effect, not one cell); CONTROLS where clang LOSES: floor / thr / vm 1.996 (the frameless scan), level-context 1.69, nest3-16 1.51. Lane ccdiff (opus): compile the same emitted C under both toolchains with the bench's own flags, diff ONLY the hot loop's object code, NAME the transformation clang applies (loop rotation / unswitching / hoisted table loads / branch layout / vectorised class test …), and test whether a C-LEVEL spelling of the emitted loop gets gcc there (hand-twin, timed on this box) — NO inline asm, NO intrinsics, NO per-arch work, ONE lane-day; deliverable docs/dev/ccdiff_step0.md with a ranked list of candidate emitter spellings, each with its measured hand-twin ratio, or the finding that the fruit hangs high. **STEP 0 MEASURED 2026-09-02 ~18:2x (lane ccdiff, docs/dev/ccdiff_step0.md + ccdiff_step0_evidence/, merged b295552, one lane-day as chartered).** THE VM SIGNAL IS ONE TRANSFORMATION: clang INLINES the emitted VM entry chain (rx_search → rx_search_run → on a frameless artifact rx_match_anchored) and proves the rx_run_state/rx_run_buffers storage dead; gcc stops at the first call boundary, so every rx_search builds a 152-byte frame, pays a -fstack-protector-strong canary (the arrays trip it; Ubuntu default) and calls out of line for storage a frameless artifact never touches — witnessed by nm. THE DFA SIGNAL: LLVM folds a variable-index load from an all-equal constant table, gcc 15 does not; on cls-upto-4 all six tables are uniform after the scan edge absorbed them. RANKED, measured as interleaved paired medians (box never below load 4.4; controls reproduce the ledger: floor/thr/vm 1.993 vs 1.996, stack-frame 0.718 vs 0.680): (1) **twin V — `always_inline` on the emitted VM helpers, GATED ON FRAMELESS** (gcc refuses always_inline on a function containing a computed goto; framed cells show no benefit, stack-frame 1.032): dig-upto-16 thr/vm **0.611** (beats clang's 0.817), floor/thr/vm control 0.994, level-context 0.954 (prefilter byte-identical); one emitter site (emit_vm.c function headers), rides RX_VM_FRAMELESS's own predicate; reach 36/90 forced-VM + 35% of the auto VM population. (2) **twin A — uniform-table constant folding in the emitted step/accept bodies**: cls-upto-4 thr/auto **0.589**; one emitter site (emit_dfa.c); reach 22/90 auto artifacts, the ledger's named win list. REJECTED on measurement: single-IV scan edge (0.849), eliding buffers without inlining (0.986 — rx_run_state's slot_values[] trips the canary too), pragma-unroll, any GENCFLAGS flag. Answer identity: 3,204 span comparisons over 178 bench subjects × 3 regimes, all identical; every twin compiles clean under clang too (the compile gate keeps its empty refusal set). BENCH CORRECTION: floor/match/auto's 0.432 DOES NOT REPRODUCE (~0.79 on byte-identical bytes; a code-layout artefact of that build) — I-37. STEP 1 (Frank's ruling owed): charter (1)+(2) as ONE implementation lane riding ONE abi event AFTER [OPT-5] STEP 2 merges (both touch the emitters STEP 2 is in; both change emitted scaffolding → D76/D94 ritual), with a quiet-box re-run of the two ratios as its acceptance. **STEP 1 CHARTERED 2026-09-03 ~09:0x (Frank: "1 agree"): ONE implementation lane (ccdiff1, opus), BOTH spellings on ONE abi event (16 → 17, D76/D94 ritual): (a) `always_inline` on the emitted VM helpers GATED ON the frameless predicate (the same has_push bool RX_VM_FRAMELESS reads; gcc refuses the attribute on a computed-goto function) — never on framed artifacts; (b) uniform-table constant folding in the emitted DFA step/accept bodies (an all-equal table becomes its constant; the table is not emitted). Answer identity over the corpus + test-axes; clang compile gate stays empty; the quiet-box re-run of the two ratios (dig-upto-16 thr/vm 0.611; cls-upto-4 thr/auto 0.589) is the acceptance, with the controls (floor/thr/vm 0.994, level-context 0.954) re-measured. Stamps: a (b)-family stamp per spelling if D82 requires a visible object (the lane reads §6.3 and says). Validation waits for lane tt12b's measurement runs to finish (one heavy thing at a time).** **STEP 1 MERGED 2026-09-03 15:4x — a3f40b1 (fast-forward; abi 17; gate (B) re-pinned to a3f40b1; the six new/changed checks and S-rows ride it): lanes ccdiff1 (opus, the two spellings; stood down after five API 529s) + ccdiff1b (sonnet, everything else). What landed: `always_inline` on the emitted VM helpers gated on the frameless predicate (one bool with RX_VM_FRAMELESS); the uniform-table fold on `<m>_next_state`/`<m>_is_accepting` with stamp `RX_DFA_UNIFORM_FOLDS` (the wide accept table is a named follow-up); `RX_VM_INLINE_CHAIN` rejected (≡ RX_VM_FRAMELESS); tests/codegen/run_dfa_uniform_fold.sh (370 of 3,507 DFA-bearing artifact/axis cells fold ≥ 1 table, 0 disagreements). VALIDATION: strict; test-codegen 5/5; make test at -j4/PROCS=3 32/32 rc=0 (the first fully green test stage on the fold); test-axes 21/21 answer-identical (paired, 72 s census); clang gate: compiled 2,556 / pcrec-refused 294 / clang-refused 0. FIVE CHECK FAMILIES re-derived with causes (report §5): table-presence detectors that read table TEXT the fold removes (search_pinned, anchored_match, premul_table — all verified as detector-not-defect by emit + -Werror + python re + grep for leftover references), the size-cap witnesses moved to a{5,25000}/(a|b){5,30000} and a lowered-cap reference compiler for the [OPT-4.1] nullable cell, and the new fold check's OWN phantom (its sharded worker mis-reconstructed a function; every shard silently produced nothing, '0 of 0' read green — fixed, plus two more detector bugs it had hidden). ACCEPTANCE (quiet box, load 0.09, 11 interleaved rounds; report §6): controls floor/thr/vm 0.995, nest3-16 1.008, stack-frame 0.986, level-context 0.996 (flat as predicted); the fold cells cls-upto-4/thr/auto 0.665 [0.33-1.65] and dig-upto-16/thr/vm 0.613 [0.24-1.53] — medians agree with STEP 0 (0.589 / 0.611) but the per-round ranges cross 1.0 on a quiet box, flagged honestly: the bench's instrument gives the citable number at the next pin. Structural evidence is exact: the frameless VM cell loses its 152-byte frame, canary and out-of-line call (.text 1561 → 1417 B); cls-upto-4 folds four tables (.rodata 627 → 47 B, rx_search 81 → 46 insns). BATTERY_v5's first end-to-end run = TOMORROW MORNING (I-40's rule: the merge landed after 15:00; the bench has tonight); a D6 panel (r52: fold soundness + read-site completeness; the inline gate) runs read-only beside it.** **STEP 2 FILED 2026-09-03 18:1x EDT (Frank: "agree", on isl1's finding): THE INLINE GATE WANTS A SIZE TERM. STEP 1(a) arms always_inline on frameless artifacts, measured only on small programs where inlining shrinks (.text 1,561 → 1,417); [ENG-ISL]'s island makes WIDE artifacts frameless and the same gate then replicates a ~70 KB matcher into all six entries — w-256 .text 71,293 → 270,544 (×3.8), gcc 1.38 → 5.91 s (×4.3), RSS 95 → 240 MB. RULED: the island LANDS as built; the size term is this row's own measured step — the knee ladder isl1 measures tomorrow (w-8/w-64/w-256, attribute present vs hand-removed: .text, gcc wall, RSS, one call's runtime) is STEP 2's STEP 0; the term is a limits.def row (emitted body bytes, or a derived proxy the emitter already has), the gate = frameless AND below it; answer-identical; a stamp change only if the IFF sentence moves. D77: built on that ladder, not before.** **STEP 2's STEP 0 MEASURED 2026-09-03 20:5x EDT (isl1, quiet box load1 < 0.31, answers checked per round): the inline ladder on island artifacts, attribute present vs hand-removed — w-8 .text 6,345 vs 2,457 (×2.58), gcc 0.29 vs 0.10 s, ns/call ratio 0.780; w-64 66,777 vs 17,081 (×3.91), 2.55 vs 0.49 s, 0.770; w-256 280,393 vs 43,049 (×6.51), 11.99 vs 1.82 s, 0.842. READ AS AN EXCHANGE RATE: always_inline buys a real 16-23% of run time at every rung (barely decaying) at a price that grows from ×2.6 code / ×2.9 gcc to ×6.5 / ×6.6 across two width decades — the point on that curve is FRANK'S to choose; a size term is the mechanism once chosen.** **STEP 2 SECOND ARM (Frank's question 2026-09-03 22:4x: "why can't rx_match call rx_match_in with the stack buffer?" — it effectively does: six thin binders → one shared static body; the six copies come only from STEP 1(a)'s always_inline honoured at six call sites): measure Frank's WRAPPER-FORWARD shape (22:5x): for a FRAMELESS artifact the non-`_in` entries have nothing to bind, so they are emitted as plain forwards to the `_in` entries (`return rx_match_in(ctx, &rx_no_buffers)`, a static descriptor — no local whose address escapes, so gcc emits a `jmp`, no frame, no canary), and the body lives once per `_in` entry (three copies) or once out-of-line behind them (one copy, one call each). STEP 1(a)'s measured win was the deleted frame + canary + call on frameless artifacts, which this keeps; what it re-pays is one call per entry, noise against a 40-70 KB island body and part of the win on the tiny bodies STEP 1 measured — so the size term still decides below some size. Ladder: w-8/w-64/w-256 × {six inlined copies (today), three `_in` copies, one out-of-line body}: .text, gcc, ns/call. Framed artifacts unchanged. The first arm changes the exchange rate; the size term then picks a point on the new curve.** **CAPABILITY PROBE (Frank 2026-09-03 23:0x: "do we have a guard or check to see if the compiler has that optimization?" — no: the attribute is unconditional on frameless VM artifacts, harmless under clang; the only guards are emit_dfa.c's `__has_attribute` on a gcc-only attribute and the compile-only CLANGGEN gate; STEP 0's nm witness — rx_search_run present under gcc, absent under clang — is the method but lives only in the report): STEP 2 adds a two-arm probe in test-codegen under the harness's CC — a frameless witness compiled as emitted and with the attribute hand-removed; the symbol table says whether the chain was inlined without help. Verdict logged with the compiler version: "workaround REDUNDANT under CC X.Y" or "NEEDED". A preprocessor guard cannot do this (`__has_attribute` says the attribute is understood, not that the inlining happens); the capability is observable only in object code.** **STEP 2 SCHEDULED 2026-09-04 08:4x (Frank: "schedule as you see fit"): the wave after [LIM-2] — lane A′ = [CC-DIFF] STEP 2 (the size term; the wrapper-forward arm; the capability probe) + [OPT-DIAL] STEP 0 (the inventory), one lane, same ledgers.** **STEP 2 STARTED 2026-09-04 10:5x EDT — lane A′ `ccd2` (opus, worktrees/ccd2, lane/ccd2 on main at abi 20; write-only under .hold while the battery runs): the four-arm ladder (six copies / wrapper-forward with the body in the three `_in` entries / one out-of-line body / no attribute), the size term as a limits.def knee, the capability probe; timing post-lift. Carries [OPT-DIAL] STEP 0.** **STEP 2 WRITE PHASE 2026-09-04 11:2x (ccd2): the entry chain has THREE call shapes, not six copies — a four-rung ordinal `--vm-entry-shape=0-4` (plain / shared / forward / inline; AUTO) with the FORWARD rung (three body copies behind forwarding entries) carrying inline's object properties (no frame, no canary, no out-of-line chain) at .text 0.50-0.61 of inline over twenty artifacts; AUTO = forward below VM_INLINE_CHAIN_MAX_BYTES (4,096, inside the measured gap 4,024→5,183 where forward stops being smaller than shared), shared above; stamps `<P>_VM_ENTRY_SHAPE` + `<P>_VM_PROGRAM_BYTES`; the capability probe (NEEDED gcc 15.2.0 / REDUNDANT clang 21.1.8). Brief corrections: a frameless artifact can still write the TRAIL (capture saves) so forwarding needs `Vm.emitted_set`; `shared` moves the canary, not deletes it. K46 fixed on the branch. OWED: every ns/call (the default forward is provisional on it); suites; the identity gate. An abi event, assigned at merge.** **STEP 2 MERGED 2026-09-04 17:0x (584b4db7; abi 21→22 at 2706ba6c; FILEPIN 2706ba6c at ae8cca33; lane ccd2, opus): `--vm-entry-shape=0-4` (plain/shared/forward/inline; AUTO); the FORWARD rung has inline's object properties at 0.50-0.61× its .text; AUTO = forward below VM_INLINE_CHAIN_MAX_BYTES 4,096 — CONFIRMED on the 20-cell ns/call ladder (studies/ccd2_entry_shape_ladder/, load1 < 0.5 gated per cell, answers checksummed): forward within noise of inline on 16 of 17 valid cells (0.979-1.016×), FASTER at 305,686 B (9,853 vs 10,069 ns/call) at half the .text; the one exception prog 645 where inline is 7% ahead for +632 B; shared at plain's run time (0.993-1.003×) — buys nothing; three vacuous cells named by the harness; 4,096 sits on the sign change of the trade (between 4,024 and 5,183). Stamps VM_ENTRY_SHAPE + VM_PROGRAM_BYTES (an abi event; _VM_PROGRAM_BYTES costs STEP 1's framed-artifact byte-identity by ruling); the capability probe; the entry-shape answer-identity gate (14 witnesses, four rungs, tests/codegen/run_entry_shape_identity.sh); test-axes tiered (forward+inline by default, all four under AXES_FULL=1 which battery.sh exports); K46 CLOSED (limits.def joins the object rule's prerequisites — the same defect found twice in one day, edge2 and ccd2); docs/design/opt_dial_inventory.md (4 of 21 switches have a two-axis rate, 2 pure wins, 15 unmeasured). Union chain on the merged tree owed (runs after form0's timing).**

- [ART-SIZE] STATE:completed (CLOSED 2026-09-19, seventy-first session, per docs/dev/plan_audit_2026-09-19.md: delivered, tag stale — Frank\'s ruling on the audit) — formerly STATE:started (STEP 2 BATTERY-PROVEN 2026-08-29 13:37 on 36d5963 (code) — strict clean, anchors 189/200 resolve, `make -k -j12 test` checks 0 failed / 27/27 sections (the counterk load cell red, solo 1,634/0; resource 26/0, counterk 24/0), `make san` rc 0 / 0 report lines both axes, mech 189 rows / unexpected 0 / undetected 6 (S150-S153 S160 S178, expected) / unreached 0 / anomalies 0; the battery script's verdict line reads RED only for the top-level `make test` exit line the load cell produces (a v4 excludes it when the solo stages clear) — verdict by hand GREEN. I-17 sent (pin 36d5963, the consolidated pcrecdev2 worklist). STEP 2 is DONE; the row stays STARTED as the record's home until [ART-SIZE] is archived with STEP 1. BATTERY on 6e37a4c RED 2026-08-29 ~09:4x — `make san`: LeakSanitizer 2 × 256 B on the R1 witness only (tests/size/size_term.rxt:34/35): r42's S3 fix armed vmsb's early abort, whose longjmp orphaned two function-local StrBufs live inside the VM emission; FIXED 36d5963 (Job-owned `scr_test`/`scr_desc`, freed by job_cleanup on every path; san axis on that file 21/0, strict clean, test-codegen 5/5); UNION BATTERY RELAUNCHED on 36d5963 at 10:02. STEP 2 MERGED 6e37a4c 2026-08-29 ~09:1x — lane/artsize3 cf13497, 58 commits; r42 close panel (docs/dev/reviews/2026-08-29-r42-artsize-close.md): identity and answers HOLD under measurement (shipped artifact byte-identical to the explicit-K artifact 7/7; 67,677 cells identical; capacity fields never lowered; 2,002-emit acceptance sweep — zero corpus changes); pre-merge round closed S1 (overflow) / S2 (rescue direction) / S3 (abort on the emission buffer) / S5 / S6 (the bar pinned to 0.73 % by two witnesses; the continuum real on the argmin-rung quantity) / S8, C1 (FILEPIN → b3cf716, 0 differing on four axes) / C2, M1 (quiet size log) / M2 / M5 / M6; the interior census is 159 (147 K=2, 11 K=3, 1 K=4), not the 150-pattern sample's 18; abi 11, bit 18, registry 67, `--list-axes` 47 rows / 19 axes; seven acceptance changes in the tree (three resource shapes, K41 witness 2, the K22 tower — all refused by the total cap, all pinned with `--max-emit-bytes` re-acceptance cells), bench survey 54/54 accept. UNION BATTERY PENDING on 6e37a4c; I-17 follows. STEP 2 DESIGN APPROVED FOR CODE 2026-08-29 ~00:1x at lane/artsize3 e72b57d after three revision passes — r40 close section; code phase opens, sequenced behind [ENG-ABS]'s merge for abi/bit/registry sites: abi 10→11, bit 18, registry 64→65. r40 PANELED 2026-08-28 ~23:0x — REVISION REQUIRED, docs/dev/reviews/2026-08-28-r40-artsize-term.md: the instrument was blind to the hybrid's jump tables (F1), no pre-emission node count exists (S1), K is caller-observable on the give-up surface (S2), the cap must re-run the ladder (S5); FRANK RULED Q2/Q4 = D84: cap overridable upward, and shipped BYTES are their own concern with a second, byte cap — unpredictability the worse half. STEP 2 OPENED 2026-08-28 ~22:3x, forty-fourth session, on Frank's "Go 1&2" — lane artsize3 (opus, worktree lane/artsize3): the [OPT-K] shape, design note `docs/design/artifact_size_term.md` FIRST (the counter rung choosing K from a size model, nesting depth the trigger, `--unroll=K` the override; a hard emitted-size cap with a refusal as the last resort; the three emitter levers PRICED against the corpus, not just the witness; stamps; identity gate as the control), then the D6 panel (r40), then code. STEP 1 CLOSED 2026-08-28 ~20:5x — census 50a3910 + the quiet-box throughput columns 98d0995 (lane artsize2; load1 0.13-1.2). CAVEAT THE RE-RUN TAUGHT: the tension curves' SPEED axis is micro-scale (2-13 µs subjects, 30 iters × 5 trials) and did not separate ±50 % effects between the loaded and the quiet pass — `-fno-premul-table` read 20-34 % slower loaded and direction-INCONSISTENT quiet (2 of 5 patterns "faster" without the table, which the mechanism cannot explain), and a stated size no-op cell swung from cheapest to dearest; the SIZE findings (load-independent) stand in full; the speed side of every lever is the bench's to measure on real 1 MB subjects ([OPT-3] STEP 2 already measured the premultiplied table at 1.79× there; I-15 ask (c)). What the quiet run DID settle: `--unroll=1` is a real WIN on the N=8 nested-repeat outlier (default 13.4 µs vs 5.9 µs), not merely free; `--engine=vm`'s failing-path cost 173,580× (was 359,000× loaded; the denominator is a 0.1-0.2 µs default); witness/-fno-counter has no throughput cell — its ~4.1 MB source cannot link within 180 s regardless of load. THE ANSWER: over 2,772 patterns (2,758 corpus + 14 bench) the shipped `.o` at -O2 is SMALL — median 6,760 B, p99 14,364 B; gcc max 6.995 s CPU (one pattern), everything else < 0.5 s; 0 timeouts, 0 budget kills. The 2 MB witness is NOT in the population: it is ~3× the corpus's own largest (`((a)|ab){4000}c`: 675,555 B source / 202,912 B .o vs the witness's 2,015,594 / 503,344 — self-contained form; the split .c alone undercounts by its .h sidecar, which is what both the plan row's old 2,004,778 and the manager's count were) and it is the SAME MECHANISM as every top-20 outlier: a bounded/exact repeat over a multi-branch alternation forcing the FRAMES-BOUNDED counter rung, body replicated per --unroll=K chunk. Source tracks .o at r = 0.99 once comments are excluded (.o/source ≈ 17 %, p10-p90 0.153-0.194); [M6-READ] prose is 42 % of aggregate SOURCE bytes but rides along, does not drive .o — a size term must price program+tables, not source. THREE LEVERS with different trades (§8): `--unroll=1` free on NESTED-repeat patterns (witness 17× smaller / 54× faster gcc / no speed loss on its subjects; corpus nested outliers 75-79 % smaller, 12× faster gcc) but ~1-3 % on single-level large counts; `-fno-premul-table` the known [OPT-3] trade (~22-25 % smaller, bounded speed cost); `--engine=vm` = the tension itself measured — dropping the hybrid prefilter shrinks .o to 4-9 % at up to a PROVISIONAL 359,000× failing-path cost, because the prefilter IS the size and the speed. Manager's line-kind attribution of the witness (span loops 40 %, label boilerplate 13.5 %, prune guards 8 %, class tests 6 %) is in §6/§7 as the three emitter levers to price in STEP 2. STEP 2 design input: the cap must bind on a measured tail nobody has written yet; the census script re-runs the census) — formerly (STEP 1 census, lane artsize opened 2026-08-28 ~14:4x, sonnet, measurement only) — ARTIFACT SIZE AS A FIRST-CLASS COST, AND THE SIZE-VS-PERFORMANCE TENSION (Frank, 2026-08-28: "I'm concerned about the 2 MB VM artifact. If our compiled artifacts are that big no one will want to use them. It deserves an investigation as well as a size vs performance tension that kicks in at some size"). THE WITNESS: the fuzz gate's seed-1 pattern `1{1,}b1{0}1{2,3}?|(c0{1}.)|((\n.*|.{2}|(?:a{2,3}|0{0,30}cc|c{0,3}bc{2,3}){1,}){5,10}.{2,}|[a-c-e]{1,}?|a$b){28,30}[a-z0-9]{28,30}(\n[^abc]{28,30}?){1,}` → a 2,004,778-byte VM artifact (RX_VM_RUNGS 0x17), gcc -O2 -c 52.9 s / 540 MB (over D45's budget), byte-identical under `--engine=vm`; hidden until [SEL-1] because its auto-prefilter DFA overflowed and refused the compile. STEP 1 — THE CENSUS (D77, before any design): over every corpus pattern (tests/**/*.rxt, --features all, default auto) and every pcrec-bench pattern (read-only), record per artifact: source bytes, `.o` bytes at -O2 (the number a user ships), gcc wall/CPU, engine + rungs + prefilter stamps, and a BYTE ATTRIBUTION by section — the emitted program proper vs tables (DFA transition/accept/class tables, premultiplied) vs the [M6-READ] prose (comments, listings) vs the accessor/scaffolding blocks vs `main`; derive the distribution (median, p90, p99, max), the outliers with their mechanism (counter-rung body replication under nested bounded repeats is the suspect: `{28,30}` × `{5,10}` × `{1,}`; `--unroll=K`'s contribution), and for each outlier the SAME pattern under `--unroll=1`, `-fno-counter`, `-fno-splice-calls` (size, gcc time, AND throughput on a representative subject — the tension has to be measured on both axes to be designed). Deliver docs/dev/artifact_size_census.md (opt3's report shape) + a one-line CLAUDE.md entry. STEP 2 (design, after the census, gated on its numbers): the tension as a GENERAL selection term, not a special case — a size cost in the emitter's candidate selection (the rung ladder's replication choices, unroll K, table forms) that binds past a threshold the census justifies; a hard emitted-size cap with a refusal ("pattern too large for the VM emitter", limits.h + limits.md) as the last resort so a fallback can never ship what gcc cannot compile in D45's budget; stamps for what the size term chose; identity gate as the control. Related: the `.o` size the bench already reports (+30 KB DFA at abi 7/8, O-7 item 2), [OPT-D] (no-impact dedupe — the census tells whether it matters), [OPT-C] (what gcc does with our output), the K-row sel1b files for the fuzz witness. Ask (1) of the same ruling rides the bench inbox I-15: for every bench pattern where auto's DFA fallback tripped, pcrec-VM vs pcre2-jit timing (level-context: 1.55 ms/set vs 115 µs at O-7).
