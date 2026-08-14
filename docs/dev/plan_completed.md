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
